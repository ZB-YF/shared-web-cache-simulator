"""Reproduce D's matrix with the integrated simulator and explicit seeded inputs."""
import argparse
from collections import defaultdict
from pathlib import Path
import platform
from statistics import mean, stdev

from cache_simulator.data_loader import load_resources
from experiments.workloads import CAPACITIES, NAMES, generate, write_trace
from cache_simulator.models import SimulationConfig
from cache_simulator.output_writer import write_csv, write_json
from cache_simulator.policies import POLICIES
from cache_simulator.runner import run_simulation, sha256, source_hashes

ROOT = Path(__file__).resolve().parents[1]


def aggregate(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[(row['workload'], row['capacity_bytes'], row['policy'])].append(row)
    summaries, compatible = [], []
    for (workload, capacity, policy), runs in groups.items():
        metrics = ('hit_ratio', 'byte_hit_ratio', 'average_response_time_ms', 'origin_traffic_bytes')
        summary = dict(workload=workload, capacity_bytes=capacity, policy=policy, seed_count=len(runs))
        for field in metrics:
            values = [run[field] for run in runs]
            summary[field + '_mean'] = mean(values)
            summary[field + '_sample_stddev'] = stdev(values) if len(values) > 1 else 0.0
        summaries.append(summary)
        # D first rounds mean origin bytes to four decimals, then converts to MiB.
        legacy = dict(workload=workload, cap_KiB=capacity // 1024,
                      policy='CUSTOM_noadm' if policy == 'CUSTOM_NOADM' else policy,
                      hit_ratio=round(mean(run['hit_ratio'] for run in runs), 4),
                      byte_hit_ratio=round(mean(run['byte_hit_ratio'] for run in runs), 4),
                      avg_rt=round(mean(run['average_response_time_ms'] for run in runs), 4),
                      origin_MiB=round(round(mean(run['origin_traffic_bytes'] for run in runs), 4) / 1048576, 3))
        client_fields = sorted({key for run in runs for key in run
                                if key.startswith(('hit_ratio_', 'avg_rt_'))})
        for field in client_fields:
            digits = 4 if field.startswith('hit_ratio_') else 2
            legacy[field] = round(mean(run[field] for run in runs if field in run), digits)
        compatible.append(legacy)
    return summaries, compatible


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resources', type=Path, default=ROOT / 'data/reference/resources.csv')
    parser.add_argument('--output-dir', type=Path, required=True, help='A new or empty directory')
    parser.add_argument('--seeds', type=int, nargs='+', default=list(range(10)))
    parser.add_argument('--capacities', type=int, nargs='+', default=list(CAPACITIES))
    parser.add_argument('--workloads', nargs='+', choices=NAMES, default=list(NAMES))
    parser.add_argument('--policies', type=str.upper, nargs='+', choices=POLICIES, default=list(POLICIES))
    args = parser.parse_args()
    try:
        if any(capacity < 0 for capacity in args.capacities):
            raise ValueError('Capacities must not be negative')
        for values in (args.seeds, args.capacities, args.workloads, args.policies):
            if len(values) != len(set(values)):
                raise ValueError('Experiment parameters must not contain duplicates')
        if args.output_dir.exists() and any(args.output_dir.iterdir()):
            raise ValueError('Output directory must be new or empty')
        resources = load_resources(args.resources)
        rows, inputs = [], []
        for workload in args.workloads:
            traces = {}
            for seed in args.seeds:
                requests = generate(resources, workload, seed)
                path = args.output_dir / 'traces' / f'{workload}_seed{seed}.csv'
                write_trace(path, requests)
                inputs.append(dict(workload=workload, seed=seed, path=path.relative_to(args.output_dir).as_posix(),
                                   sha256=sha256(path), request_count=len(requests)))
                traces[seed] = requests
            for capacity in args.capacities:
                for policy in args.policies:
                    for seed, requests in traces.items():
                        _, statistics = run_simulation(resources, requests, policy, SimulationConfig(capacity))
                        row = dict(workload=workload, capacity_bytes=capacity, policy=policy,
                                   seed=seed, **statistics.summary())
                        for client in statistics.per_client():
                            row['hit_ratio_' + client['client_id']] = client['hit_ratio']
                            row['avg_rt_' + client['client_id']] = client['average_response_time_ms']
                        rows.append(row)
            print(f'Completed {workload}; {len(rows)} runs total', flush=True)
        summaries, compatible = aggregate(rows)
        run_fields = list(dict.fromkeys(key for row in rows for key in row))
        legacy_fields = ['workload', 'cap_KiB', 'policy', 'hit_ratio', 'byte_hit_ratio', 'avg_rt', 'origin_MiB']
        legacy_fields += sorted({key for row in compatible for key in row} - set(legacy_fields))
        write_csv(args.output_dir / 'runs.csv', rows, run_fields)
        write_csv(args.output_dir / 'summary.csv', summaries)
        write_csv(args.output_dir / 'd_compatible.csv', compatible, legacy_fields)
        write_json(args.output_dir / 'config.json', dict(
            provenance='Synthetic workloads adapted from contributor D; integrated simulator rerun',
            seeds=args.seeds, capacities_bytes=args.capacities, policies=args.policies,
            workloads=args.workloads, hit_latency_ms=5, resources_file=args.resources.name,
            resources_sha256=sha256(args.resources), source_sha256=source_hashes(),
            python_version=platform.python_version(), traces=inputs,
            aggregation='Arithmetic mean across seeds; sample standard deviation in summary.csv',
            runs=len(rows)))
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    print(f'Wrote {len(rows)} runs and {len(summaries)} aggregate rows to {args.output_dir}')


if __name__ == '__main__':
    main()
