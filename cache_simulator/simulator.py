"""Chronological request processing over a single shared cache."""
from cache_simulator.cache import Cache
from cache_simulator.models import Request, RequestResult, Resource, SimulationConfig


class Simulator:
    def __init__(self, resources: dict[str, Resource], cache: Cache, config: SimulationConfig):
        self.resources = resources
        self.cache = cache
        self.config = config
        if config.capacity_bytes != cache.capacity_bytes:
            raise ValueError("Cache and configuration capacities must match")
        if cache.snapshot():
            raise ValueError("Simulator requires an initially empty cache")
        self._started = False
        self._step = 0
        self._last_timestamp = None
        self._origin_bytes = 0
        self._hits = 0

    def process_request(self, request: Request, step: int) -> RequestResult:
        if step != self._step + 1:
            raise ValueError("Request steps must be consecutive, starting at 1")
        if request.timestamp.tzinfo is None:
            raise ValueError("Request timestamps must include a timezone")
        if self._last_timestamp is not None and request.timestamp < self._last_timestamp:
            raise ValueError("Requests must be processed chronologically")
        resource = self.resources[request.resource_id]
        self.cache.policy.on_request(resource, request, step)
        hit = self.cache.contains(resource.resource_id)
        if hit:
            self.cache.record_hit(resource, request, step)
            response, traffic, evicted = self.config.hit_latency_ms, 0, ()
            self._hits += 1
        else:
            response, traffic = resource.origin_latency_ms, resource.size_bytes
            evicted = self.cache.admit(resource, request, step)
            self._origin_bytes += traffic
        self._step = step
        self._last_timestamp = request.timestamp
        return RequestResult(step, request, resource.size_bytes, hit, response, traffic,
                             evicted, self.cache.snapshot(), self.cache.used_bytes,
                             self._origin_bytes, self._hits)

    def run(self, requests: list[Request]) -> list[RequestResult]:
        if self._started or self._step:
            raise ValueError("Simulator instances are single-use; create a fresh run")
        self._started = True
        # Sort by instant, retaining original order for equal timestamps.
        ordered = sorted(requests, key=lambda request: request.timestamp)
        return [self.process_request(request, step) for step, request in enumerate(ordered, 1)]
