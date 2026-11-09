"""Output writer placeholders. No simulated results are generated yet."""
from pathlib import Path
from models import RequestResult


def write_request_results(path: Path, results: list[RequestResult]) -> None:
    raise NotImplementedError("Implement request CSV output; see docs/INTERFACES.md for reference fields")


def write_summary(path: Path, summary: dict, per_client: list[dict], config: dict) -> None:
    raise NotImplementedError("Write global metrics, per-client metrics, and reproducible configuration")
