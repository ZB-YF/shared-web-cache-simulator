"""Compare all ten instructor reference fields at every request, not just hit totals."""
import csv
from pathlib import Path

from data_loader import load_requests, load_resources
from experiments.workloads import find_resource
from output_writer import request_row
from runner import run_simulation

ROOT = Path(__file__).resolve().parents[1]


def reference_aliases(resources):
    fragments = [('learn', 'index.html'), ('learn', 'main.css'), ('learn', 'logo.svg'),
                 ('cdn', 'avatar'), ('pypi', 'warehouse')]
    return {find_resource(resources, host, path): alias
            for alias, (host, path) in zip('ABCDE', fragments)}


def validate():
    resources = load_resources(ROOT / 'data/resources.csv')
    requests = load_requests(ROOT / 'data/requests_reference.csv', resources)
    aliases = reference_aliases(resources)
    reports = []
    for policy in ('FIFO', 'LRU', 'LFU'):
        results, statistics = run_simulation(resources, requests, policy)
        with (ROOT / f'data/reference/expected_{policy.lower()}.csv').open(newline='') as stream:
            expected = list(csv.DictReader(stream))
        if len(results) != len(expected):
            raise AssertionError(f'{policy}: request count mismatch')
        for result, reference in zip(results, expected):
            actual = request_row(result, aliases)
            for field, value in reference.items():
                numeric = field in {'step', 'cache_used_KiB', 'response_ms', 'cumulative_origin_bytes', 'cumulative_hits'}
                equal = float(actual[field]) == float(value) if numeric else actual[field] == value
                if not equal:
                    raise AssertionError(f'{policy} step {result.step}, {field}: {actual[field]!r} != {value!r}')
        reports.append(dict(policy=policy, compared_requests=len(results), **statistics.summary()))
    return reports


def main():
    for report in validate():
        print(f"PASS {report['policy']}: {report['compared_requests']} requests, all 10 reference fields; "
              f"hits={report['hits']}, origin={report['origin_traffic_bytes']} bytes")


if __name__ == '__main__':
    main()
