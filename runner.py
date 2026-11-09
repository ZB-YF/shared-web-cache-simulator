"""Single-run orchestration shared by the CLI, validation, and batch experiments."""
import hashlib
from pathlib import Path

from cache import Cache
from metrics import Statistics
from models import SimulationConfig
from policies import create_policy
from simulator import Simulator


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_simulation(resources, requests, policy='FIFO', config=None):
    config = config or SimulationConfig()
    replacement = create_policy(policy, config.hit_latency_ms)
    simulator = Simulator(resources, Cache(config.capacity_bytes, replacement), config)
    results = simulator.run(requests)
    statistics = Statistics()
    for result in results:
        statistics.record(result)
    return results, statistics


def source_hashes():
    root = Path(__file__).resolve().parent
    return {path.relative_to(root).as_posix(): sha256(path)
            for path in sorted(root.rglob('*.py'))
            if not any(part.startswith('.') or part == '__pycache__' for part in path.relative_to(root).parts)}


def input_config(resources_path, requests_path, policy, config, request_count):
    return dict(policy=policy.upper(), capacity_bytes=config.capacity_bytes,
                hit_latency_ms=config.hit_latency_ms, request_count=request_count,
                resources_file=Path(resources_path).name, resources_sha256=sha256(resources_path),
                requests_file=Path(requests_path).name, requests_sha256=sha256(requests_path),
                source_sha256=source_hashes())
