"""Characterize and compare the three instructor-provided fixed request traces.

This entry point does not generate or resample workloads. Each matrix cell is
one deterministic replay, with an empty shared cache and 5 ms hit latency.
The older ``experiments.run`` command remains the synthetic reproduction.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import platform

from cache_simulator.data_loader import load_requests, load_resources
from cache_simulator.models import SimulationConfig
from cache_simulator.output_writer import write_csv, write_json, write_request_results
from cache_simulator.runner import run_simulation, sha256, source_hashes


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ('sequential', 'repetitive', 'mixed')
CAPACITIES = (102400, 512000, 1048576, 2097152, 5242880, 10485760)
POLICIES = ('FIFO', 'LRU', 'LFU', 'CUSTOM')
HIT_LATENCY_MS = 5.0

SUMMARY_FIELDS = ('workload', 'request_count', 'distinct_resources',
                  'distinct_clients', 'requested_bytes',
                  'requested_working_set_bytes', 'top_five_request_share')
POPULARITY_FIELDS = ('workload', 'resource_id', 'request_count', 'request_share',
                     'size_bytes', 'requested_bytes', 'rank')
OVERSIZED_FIELDS = ('workload', 'capacity_bytes', 'oversized_resource_requests')


def characterize(resources, traces, capacities):
    """Describe input requests only; no cache-policy outcome enters this step."""
    summaries, popularity, top_five, oversized = [], [], [], []
    for workload, requests in traces.items():
        counts = Counter(request.resource_id for request in requests)
        ordered = sorted(counts, key=lambda key: (-counts[key], key))
        n = len(requests)
        for rank, key in enumerate(ordered, 1):
            row = dict(workload=workload, resource_id=key,
                       request_count=counts[key], request_share=counts[key] / n,
                       size_bytes=resources[key].size_bytes,
                       requested_bytes=counts[key] * resources[key].size_bytes,
                       rank=rank)
            popularity.append(row)
            if rank <= 5:
                top_five.append(dict(row))
        summaries.append(dict(
            workload=workload, request_count=n, distinct_resources=len(counts),
            distinct_clients=len({request.client_id for request in requests}),
            requested_bytes=sum(count * resources[key].size_bytes
                                for key, count in counts.items()),
            requested_working_set_bytes=sum(resources[key].size_bytes for key in counts),
            top_five_request_share=sum(counts[key] for key in ordered[:5]) / n if n else 0.0))
        for capacity in capacities:
            oversized.append(dict(
                workload=workload, capacity_bytes=capacity,
                oversized_resource_requests=sum(
                    count for key, count in counts.items()
                    if resources[key].size_bytes > capacity)))
    return dict(summary=summaries, resource_popularity=popularity,
                top_five=top_five, oversized_requests=oversized)


def preliminary_hypotheses(characterization, capacities, created_at):
    """Write testable expectations from input characteristics, before replay."""
    lines = [
        '# Preliminary hypotheses from workload characterization', '',
        f'Generated at {created_at} from the supplied input files, before this '
        'invocation executes any policy simulation. This is an input-analysis '
        'record, not a preregistered study or evidence that earlier results were unseen.', '',
        'These expectations must be checked against the exported results. '
        'Popularity alone does not describe temporal locality or guarantee a policy ranking.', '',
    ]
    for row in characterization['summary']:
        workload = row['workload']
        lines += [f'## {workload.title()}', '',
                  f"The trace contains {row['request_count']} requests from "
                  f"{row['distinct_clients']} clients for {row['distinct_resources']} "
                  f"resources. The five most requested resources account for "
                  f"{row['top_five_request_share']:.2%} of requests. Distinct "
                  f"requested resources total {row['requested_working_set_bytes']} bytes; "
                  f"repeated requests total {row['requested_bytes']} bytes.", '']
        if workload == 'sequential':
            expectation = (
                'If requests are spread across resources with limited short-term reuse, '
                'all policies should have fewer opportunities to exploit a stable hot set. '
                'FIFO and LRU may perform similarly; LFU needs repeat accesses before '
                'its frequency information can help.')
        elif workload == 'repetitive':
            expectation = (
                'If the popular working set fits in the cache, repeated requests should '
                'produce more hits. LFU may protect frequently accessed resources, while '
                'LRU benefits when repetition is recent. LA-GDSF may reduce latency by '
                'retaining resources with high saved retrieval cost per byte.')
        else:
            expectation = (
                'Heterogeneous resource sizes and client requests may separate request-hit '
                'ratio, byte-hit ratio, response time, and client experience. LA-GDSF may '
                'improve latency through small costly resources while sacrificing hits '
                'or bytes for a client requesting larger resources.')
        lines += [expectation, '',
                  'For every workload, increasing capacity may change both the fitting '
                  'working set and which requests are oversized. This can change policy '
                  'rankings; monotonic improvement for every policy is not assumed.', '']
        relevant = [item for item in characterization['oversized_requests']
                    if item['workload'] == workload]
        lines += ['| Capacity bytes | Oversized requests |', '|---:|---:|']
        lines += [f"| {item['capacity_bytes']} | {item['oversized_resource_requests']} |"
                  for item in relevant]
        lines += ['', 'Oversized requests cannot become hits under any policy at that '
                  'capacity. Compare their request share and byte volume when interpreting '
                  'the gap between request-hit and byte-hit ratios.', '']
    lines += ['## Evaluation plan', '',
              'Compare FIFO, LRU, LFU, and CUSTOM on the same fixed traces, metadata, '
              'capacities, and 5 ms hit latency. Evaluate policy differences at 5242880 '
              'bytes (5 MiB), compare capacity curves, and inspect individual clients '
              'on the mixed trace at 5 MiB. Use all required metrics, including '
              'individual resource evictions, oversized requests, and mean post-request '
              'cache utilization.', '',
              'Selected capacities in bytes: ' + ', '.join(map(str, capacities)) + '.', '']
    return '\n'.join(lines)


def _input_name(path):
    """Keep configuration portable without exposing private absolute paths."""
    try:
        return Path(path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return Path(path).name


def run_experiments(resources_path, requests_dir, output_dir, capacities=CAPACITIES,
                    policies=POLICIES, characterize_only=False, request_logs=False):
    """Validate all inputs, characterize them, then run one replay per cell."""
    resources_path, requests_dir, output_dir = map(Path, (resources_path, requests_dir, output_dir))
    capacities = tuple(capacities)
    policies = tuple(policy.upper() for policy in policies)
    if not capacities or any(not isinstance(value, int) or value <= 0 for value in capacities):
        raise ValueError('Capacities must be positive integers in bytes')
    if len(set(capacities)) != len(capacities):
        raise ValueError('Capacities must not contain duplicates')
    if not policies or any(policy not in POLICIES for policy in policies):
        raise ValueError('Policies must be selected from FIFO, LRU, LFU, CUSTOM')
    if len(set(policies)) != len(policies):
        raise ValueError('Policies must not contain duplicates')
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError('Output directory is not empty; choose a new directory')

    # Load every trace before creating output, so malformed/missing inputs do not
    # leave an apparently successful partial experiment directory.
    resources = load_resources(resources_path)
    paths = {name: requests_dir / f'requests_{name}.csv' for name in WORKLOADS}
    traces = {name: load_requests(path, resources) for name, path in paths.items()}
    created_at = datetime.now(timezone.utc).isoformat()
    characterization = characterize(resources, traces, capacities)
    for name, fields in [('summary', SUMMARY_FIELDS),
                         ('resource_popularity', POPULARITY_FIELDS),
                         ('top_five', POPULARITY_FIELDS),
                         ('oversized_requests', OVERSIZED_FIELDS)]:
        write_csv(output_dir / 'characterization' / f'{name}.csv',
                  characterization[name], fields)
    (output_dir / 'characterization' / 'hypotheses.md').write_text(
        preliminary_hypotheses(characterization, capacities, created_at), encoding='utf-8')

    config = dict(
        provenance='Instructor-provided fixed request traces; no synthetic generation or resampling',
        started_at_utc=created_at, python_version=platform.python_version(),
        workloads=list(WORKLOADS), capacities_bytes=list(capacities), policies=list(policies),
        hit_latency_ms=HIT_LATENCY_MS,
        resources_file=_input_name(resources_path), resources_sha256=sha256(resources_path),
        traces=[dict(workload=name, file=_input_name(paths[name]), sha256=sha256(paths[name]),
                     request_count=len(traces[name])) for name in WORKLOADS],
        source_sha256=source_hashes(),
        characterize_only=characterize_only, request_logs=request_logs,
        runs=0, aggregation='One deterministic replay per workload/capacity/policy cell; no seed averaging',
        execution_order='All inputs loaded, characterization and hypotheses written, then policy replays',
        ratio_units='hit_ratio, byte_hit_ratio, and average_cache_utilization are fractions from 0 to 1')
    write_json(output_dir / 'config.json', config)
    if characterize_only:
        return config

    rows, client_rows = [], []
    for workload in WORKLOADS:
        for capacity in capacities:
            for policy in policies:
                results, statistics = run_simulation(
                    resources, traces[workload], policy,
                    SimulationConfig(capacity, HIT_LATENCY_MS))
                dimensions = dict(workload=workload, capacity_bytes=capacity, policy=policy)
                rows.append(dict(**dimensions, **statistics.summary()))
                client_rows.extend(dict(**dimensions, **client) for client in statistics.per_client())
                if request_logs:
                    write_request_results(
                        output_dir / 'requests' / f'{workload}_{policy.lower()}_{capacity}.csv', results)
        print(f'Completed {workload}; {len(rows)} fixed-trace runs total', flush=True)
    write_csv(output_dir / 'runs.csv', rows)
    # Preserve a usable header even if all supplied traces have no requests.
    client_fields = ['workload', 'capacity_bytes', 'policy', 'client_id',
                     *(key for key in rows[0] if key not in ('workload', 'capacity_bytes', 'policy'))]
    write_csv(output_dir / 'per_client.csv', client_rows, client_fields)
    config.update(runs=len(rows), completed_at_utc=datetime.now(timezone.utc).isoformat())
    write_json(output_dir / 'config.json', config)
    return config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resources', type=Path, default=ROOT / 'data/reference/resources.csv')
    parser.add_argument('--requests-dir', type=Path, default=ROOT / 'data/workloads/provided')
    parser.add_argument('--output-dir', type=Path, required=True, help='A new or empty directory')
    parser.add_argument('--capacities', type=int, nargs='+', default=list(CAPACITIES),
                        help='Positive cache capacities in bytes')
    parser.add_argument('--policies', type=str.upper, nargs='+', choices=POLICIES, default=list(POLICIES))
    parser.add_argument('--characterize-only', action='store_true',
                        help='Write input analysis and hypotheses without running policies')
    parser.add_argument('--request-logs', action='store_true',
                        help='Also export every request from each matrix cell (larger output)')
    args = parser.parse_args()
    try:
        config = run_experiments(args.resources, args.requests_dir, args.output_dir,
                                 args.capacities, args.policies, args.characterize_only,
                                 args.request_logs)
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    print(f"Wrote characterization and {config['runs']} fixed-trace runs to {args.output_dir}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
