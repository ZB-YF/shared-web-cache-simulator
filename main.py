"""Input validation entry point; simulation support is not implemented yet."""
import argparse
from pathlib import Path

from data_loader import load_requests, load_resources
from models import SimulationConfig

ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Shared Web Cache Simulator scaffold")
    parser.add_argument("--resources", type=Path, default=ROOT / "data/resources.csv")
    parser.add_argument("--requests", type=Path, default=ROOT / "data/requests_reference.csv")
    parser.add_argument("--policy", type=str.upper, choices=["FIFO", "LRU", "LFU", "CUSTOM"], default="FIFO")
    parser.add_argument("--capacity", type=int, default=102400, help="Cache capacity in bytes")
    parser.add_argument("--hit-latency-ms", type=float, default=5)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "results")
    parser.add_argument("--validate-only", action="store_true", help="Read, validate, and summarize the input files only")
    args = parser.parse_args()
    try:
        config = SimulationConfig(args.capacity, args.hit_latency_ms)
        resources = load_resources(args.resources)
        requests = load_requests(args.requests, resources)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(f"Input validation passed: {len(resources)} resources, {len(requests)} requests, "
          f"{len({request.client_id for request in requests})} clients")
    print(f"Configuration: policy={args.policy}, capacity={config.capacity_bytes} bytes, "
          f"hit_latency={config.hit_latency_ms:g} ms")
    print(f"The trace references {len({request.resource_id for request in requests})} distinct resources; requests are stably sorted by timestamp.")
    if not args.validate_only:
        print("Scaffold only: Cache, Simulator, and policies are not implemented. No simulation or experiment results were generated.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
