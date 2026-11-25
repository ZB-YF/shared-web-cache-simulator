"""Independently recompute the provided-trace matrix from request events.

The verifier constructs fresh simulators without using Statistics. It checks
matrix coverage, all exported global/client metrics, input and source hashes,
and per-request accounting. It does not change policies or published results.
"""
import argparse
from collections import defaultdict
import csv
from decimal import Decimal, InvalidOperation
from itertools import product
import json
import math
from pathlib import Path

from cache_simulator.cache import Cache
from cache_simulator.data_loader import load_requests, load_resources
from cache_simulator.models import SimulationConfig
from cache_simulator.output_writer import request_row, write_json
from cache_simulator.policies import create_policy
from cache_simulator.runner import sha256, source_hashes
from cache_simulator.simulator import Simulator


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ('sequential', 'repetitive', 'mixed')
POLICIES = ('FIFO', 'LRU', 'LFU', 'CUSTOM')
ADDITIVE_FIELDS = ('request_count', 'hits', 'misses', 'requested_bytes', 'hit_bytes',
                   'total_response_time_ms', 'origin_traffic_bytes', 'cache_evictions',
                   'oversized_resource_requests')
AVERAGE_FIELDS = ('hit_ratio', 'byte_hit_ratio', 'average_response_time_ms',
                  'average_cache_utilization')


def independent_metrics(results, capacity):
    """Calculate definitions directly, without calling Statistics methods."""
    count = len(results)
    requested = sum(result.size_bytes for result in results)
    hit_bytes = sum(result.size_bytes for result in results if result.hit)
    hits = sum(result.hit for result in results)
    latency = sum(result.response_time_ms for result in results)
    return dict(
        request_count=count, hits=hits, misses=count - hits,
        requested_bytes=requested, hit_bytes=hit_bytes,
        total_response_time_ms=latency,
        origin_traffic_bytes=sum(result.origin_traffic_bytes for result in results),
        cache_evictions=sum(len(result.evicted_resources) for result in results),
        oversized_resource_requests=sum(result.size_bytes > capacity for result in results),
        hit_ratio=hits / count if count else 0.0,
        byte_hit_ratio=hit_bytes / requested if requested else 0.0,
        average_response_time_ms=latency / count if count else 0.0,
        average_cache_utilization=(sum(result.cache_used_bytes for result in results)
                                   / (capacity * count) if capacity and count else 0.0))


def _read_csv(path):
    with Path(path).open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def _dimension(row):
    return row['workload'], int(row['capacity_bytes']), row['policy']


def _equal(actual, expected, context):
    if isinstance(expected, int):
        try:
            matches = Decimal(str(actual)) == expected
        except (InvalidOperation, ValueError, TypeError):
            matches = False
    else:
        try:
            matches = math.isclose(float(actual), expected, rel_tol=1e-12, abs_tol=1e-12)
        except (ValueError, TypeError):
            matches = False
    if not matches:
        raise ValueError(f'{context}: expected {expected!r}, found {actual!r}')


def _compare_metrics(row, expected, context):
    for key, value in expected.items():
        if key not in row:
            raise ValueError(f'{context}: missing metric {key}')
        _equal(row[key], value, f'{context}/{key}')


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(results_dir, resources_path=None, requests_dir=None, allow_source_drift=False):
    """Return portable evidence or raise ValueError on the first discrepancy."""
    results_dir = Path(results_dir)
    config = json.loads((results_dir / 'config.json').read_text(encoding='utf-8'))
    capacities = config['capacities_bytes']
    _require(set(config['workloads']) == set(WORKLOADS) and len(config['workloads']) == 3,
             'The official matrix must contain exactly the three provided workloads')
    _require(set(config['policies']) == set(POLICIES) and len(config['policies']) == 4,
             'The official matrix must contain exactly FIFO, LRU, LFU, CUSTOM')
    _require(len(capacities) == len(set(capacities)) == 6
             and all(isinstance(value, int) and value > 0 for value in capacities)
             and 5242880 in capacities,
             'The official matrix needs six distinct positive capacities including 5 MiB')
    _require(config['hit_latency_ms'] == 5, 'Official hit latency must be 5 ms')
    _require(config['runs'] == 72 and not config['characterize_only'],
             'The official matrix must have 72 completed replay cells')

    resources_path = Path(resources_path) if resources_path else ROOT / config['resources_file']
    _require(sha256(resources_path) == config['resources_sha256'], 'Resource input hash mismatch')
    resources = load_resources(resources_path)
    trace_config = {item['workload']: item for item in config['traces']}
    _require(set(trace_config) == set(WORKLOADS) and len(config['traces']) == 3,
             'Trace configuration must identify each provided workload once')
    traces = {}
    for workload in WORKLOADS:
        item = trace_config[workload]
        path = (Path(requests_dir) / f'requests_{workload}.csv' if requests_dir
                else ROOT / item['file'])
        _require(sha256(path) == item['sha256'], f'{workload}: request input hash mismatch')
        traces[workload] = load_requests(path, resources)
        _require(len(traces[workload]) == item['request_count'],
                 f'{workload}: configured request count differs from input')

    current_source = source_hashes()
    recorded_source = config['source_sha256']
    source_changes = {
        name: dict(recorded_sha256=recorded_source.get(name), current_sha256=current_source.get(name))
        for name in sorted(set(recorded_source) | set(current_source))
        if recorded_source.get(name) != current_source.get(name)}
    _require(allow_source_drift or not source_changes,
             'Source snapshot differs from config; rerun after code changes or explicitly allow source drift')

    rows = _read_csv(results_dir / 'runs.csv')
    clients = _read_csv(results_dir / 'per_client.csv')
    expected_cells = set(product(WORKLOADS, capacities, POLICIES))
    cells = {_dimension(row): row for row in rows}
    _require(len(cells) == len(rows) == 72 and set(cells) == expected_cells,
             'runs.csv contains missing, duplicate, or unexpected matrix cells')
    client_cells = {(*_dimension(row), row['client_id']): row for row in clients}
    expected_clients = {(*cell, client) for cell in expected_cells
                        for client in {request.client_id for request in traces[cell[0]]}}
    _require(len(client_cells) == len(clients) and set(client_cells) == expected_clients,
             'per_client.csv contains missing, duplicate, or unexpected clients')

    event_count = 0
    metrics_checked = 0
    request_logs_checked = 0
    observed_oversized = defaultdict(set)
    for workload, capacity, policy in sorted(expected_cells):
        cfg = SimulationConfig(capacity, config['hit_latency_ms'])
        simulator = Simulator(resources, Cache(capacity, create_policy(policy, cfg.hit_latency_ms)), cfg)
        results = simulator.run(traces[workload])
        context = f'{workload}/{capacity}/{policy}'
        expected = independent_metrics(results, capacity)
        _compare_metrics(cells[(workload, capacity, policy)], expected, context)
        metrics_checked += len(expected)
        per_client = defaultdict(list)
        for result in results:
            resource = resources[result.request.resource_id]
            _require(0 <= result.cache_used_bytes <= capacity,
                     f'{context}/{result.step}: cache occupancy outside capacity')
            _equal(result.cache_used_bytes,
                   sum(resources[key].size_bytes for key in result.cache_contents_oldest_first),
                   f'{context}/{result.step}/occupancy')
            _equal(result.origin_traffic_bytes, 0 if result.hit else result.size_bytes,
                   f'{context}/{result.step}/origin_traffic')
            _equal(result.response_time_ms, cfg.hit_latency_ms if result.hit else resource.origin_latency_ms,
                   f'{context}/{result.step}/response_time')
            if resource.size_bytes > capacity:
                _require(not result.hit and not result.evicted_resources,
                         f'{context}/{result.step}: oversized request hit or evicted cached resources')
            per_client[result.request.client_id].append(result)
        derived_clients = {}
        for client, events in per_client.items():
            derived = independent_metrics(events, capacity)
            derived_clients[client] = derived
            _compare_metrics(client_cells[(workload, capacity, policy, client)], derived,
                             f'{context}/{client}')
            metrics_checked += len(derived)
        for field in ADDITIVE_FIELDS:
            _equal(sum(row[field] for row in derived_clients.values()), expected[field],
                   f'{context}/global_client_sum/{field}')
        for field in AVERAGE_FIELDS:
            weight = 'requested_bytes' if field == 'byte_hit_ratio' else 'request_count'
            denominator = sum(row[weight] for row in derived_clients.values())
            weighted = (sum(row[field] * row[weight] for row in derived_clients.values())
                        / denominator if denominator else 0.0)
            _equal(weighted, expected[field], f'{context}/global_client_weighted/{field}')
        _equal(expected['origin_traffic_bytes'], expected['requested_bytes'] - expected['hit_bytes'],
               f'{context}/traffic_conservation')
        observed_oversized[(workload, capacity)].add(expected['oversized_resource_requests'])
        if config.get('request_logs'):
            path = results_dir / 'requests' / f'{workload}_{policy.lower()}_{capacity}.csv'
            logs = _read_csv(path)
            _require(len(logs) == len(results), f'{context}: request-log row count mismatch')
            for actual, result in zip(logs, results):
                for key, value in request_row(result).items():
                    if isinstance(value, (int, float)):
                        _equal(actual[key], value, f'{context}/{result.step}/log/{key}')
                    else:
                        _require(actual[key] == value, f'{context}/{result.step}/log/{key}: text mismatch')
            request_logs_checked += len(logs)
        event_count += len(results)
    _require(all(len(values) == 1 for values in observed_oversized.values()),
             'Oversized request count differs between policies with identical input and capacity')
    return dict(
        status='PASS', method='Fresh Simulator replays; metrics independently calculated from immutable RequestResult events without Statistics',
        matrix_cells=len(rows), per_client_rows=len(clients), request_events_checked=event_count,
        metric_values_checked=metrics_checked, request_log_rows_checked=request_logs_checked,
        resources_sha256=config['resources_sha256'],
        trace_sha256={name: trace_config[name]['sha256'] for name in WORKLOADS},
        result_sha256={name: sha256(results_dir / name) for name in ('runs.csv', 'per_client.csv', 'config.json')},
        source_snapshot_matches=not source_changes, source_changes=source_changes,
        checks=['72 unique workload/capacity/policy combinations',
                'Exact per-client coverage and independent metrics',
                'Per-request capacity, origin traffic, latency, and oversized handling',
                'Global/client additive counters and correctly weighted averages',
                'Origin traffic equals requested bytes minus hit bytes',
                'Policy-independent oversized counts for each input/capacity',
                'Resource, request, and source provenance hashes'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results-dir', type=Path, required=True)
    parser.add_argument('--resources', type=Path)
    parser.add_argument('--requests-dir', type=Path)
    parser.add_argument('--allow-source-drift', action='store_true',
                        help='Explicitly audit old results with current source; record differences')
    parser.add_argument('--output', type=Path, help='Optional new JSON evidence file')
    args = parser.parse_args()
    try:
        if args.output and args.output.exists():
            raise ValueError('Evidence output already exists; choose a new file')
        report = verify(args.results_dir, args.resources, args.requests_dir, args.allow_source_drift)
        if args.output:
            write_json(args.output, report)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    print(f"PASS: {report['matrix_cells']} cells, {report['per_client_rows']} client rows, "
          f"{report['request_events_checked']} request events; "
          f"source snapshot matches={report['source_snapshot_matches']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
