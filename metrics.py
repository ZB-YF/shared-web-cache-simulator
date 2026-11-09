"""Statistics interface placeholder. Named metrics.py to avoid shadowing the standard library."""
from models import RequestResult


class Statistics:
    def record(self, result: RequestResult) -> None:
        raise NotImplementedError("Accumulate global and per-client metrics")

    def summary(self) -> dict:
        raise NotImplementedError("Implement global metrics; see docs/INTERFACES.md")

    def per_client(self) -> list[dict]:
        raise NotImplementedError("Return per-client metrics")
