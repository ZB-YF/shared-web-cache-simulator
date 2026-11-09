"""Simulation entry point placeholder. Create a fresh cache and policy for every run."""
from cache import Cache
from models import Request, RequestResult, Resource, SimulationConfig


class Simulator:
    def __init__(self, resources: dict[str, Resource], cache: Cache, config: SimulationConfig):
        self.resources = resources
        self.cache = cache
        self.config = config

    def process_request(self, request: Request, step: int) -> RequestResult:
        raise NotImplementedError("Implement hit/miss handling, latency, traffic, cache operations, and request records")

    def run(self, requests: list[Request]) -> list[RequestResult]:
        raise NotImplementedError("Process requests chronologically, starting each run with an empty state")
