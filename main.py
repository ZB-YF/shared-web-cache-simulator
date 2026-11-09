"""Validate input or run a reproducible shared-cache simulation."""
import argparse
from pathlib import Path

from data_loader import load_requests, load_resources
from models import SimulationConfig
from output_writer import write_request_results, write_summary
from policies import POLICIES
from runner import input_config, run_simulation

ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description='Shared Web Cache Simulator')
    parser.add_argument('--resources', type=Path, default=ROOT / 'data/resources.csv')
    parser.add_argument('--requests', type=Path, default=ROOT / 'data/requests_reference.csv')
    parser.add_argument('--policy', type=str.upper, choices=POLICIES, default='FIFO')
    parser.add_argument('--capacity', type=int, default=102400, help='Cache capacity in bytes')
    parser.add_argument('--hit-latency-ms', type=float, default=5)
    parser.add_argument('--output-dir', type=Path, help='A new or empty output directory')
    parser.add_argument('--validate-only', action='store_true', help='Validate inputs without simulation')
    args = parser.parse_args()
    try:
        config = SimulationConfig(args.capacity, args.hit_latency_ms)
        resources = load_resources(args.resources)
        requests = load_requests(args.requests, resources)
        if args.validate_only:
            print(f'Input validation passed: {len(resources)} resources, {len(requests)} requests, '
                  f'{len({r.client_id for r in requests})} clients')
            print(f'The trace references {len({r.resource_id for r in requests})} distinct resources.')
            return 0
        output = args.output_dir or ROOT / 'results' / f'{args.requests.stem}_{args.policy}_{args.capacity}'
        if output.exists() and any(output.iterdir()):
            raise ValueError(f'Output directory is not empty: {output}; choose a new directory')
        results, statistics = run_simulation(resources, requests, args.policy, config)
        metadata = input_config(args.resources, args.requests, args.policy, config, len(requests))
        write_request_results(output / 'requests.csv', results)
        summary = statistics.summary()
        write_summary(output, summary, statistics.per_client(), metadata)
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    print(f"{args.policy}: {summary['hits']}/{summary['request_count']} hits "
          f"({summary['hit_ratio']:.2%}), average response {summary['average_response_time_ms']:.2f} ms, "
          f"origin traffic {summary['origin_traffic_bytes']} bytes")
    print(f'Results: {output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
