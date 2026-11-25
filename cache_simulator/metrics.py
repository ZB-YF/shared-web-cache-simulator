"""Global and per-client metrics derived from immutable request results."""
from cache_simulator.models import RequestResult


class Statistics:
    """Accumulate metrics using the configured total cache capacity.

    Utilization is a ratio from 0 to 1, sampled after every request, including
    hits and bypassed misses. Per-client utilization is the shared cache's
    occupancy after that client's requests; it does not measure private storage.
    Empty runs and zero-capacity caches have utilization 0 by convention.
    """

    def __init__(self, capacity_bytes=102400):
        if capacity_bytes < 0:
            raise ValueError('capacity_bytes must not be negative')
        self.capacity_bytes = capacity_bytes
        self._total = self._empty()
        self._clients = {}

    @staticmethod
    def _empty():
        return dict(request_count=0, hits=0, requested_bytes=0, hit_bytes=0,
                    total_response_time_ms=0.0, origin_traffic_bytes=0,
                    cache_evictions=0, oversized_resource_requests=0,
                    _cache_used_bytes_sum=0)

    def record(self, result: RequestResult) -> None:
        client = self._clients.setdefault(result.request.client_id, self._empty())
        for counters in (self._total, client):
            counters['request_count'] += 1
            counters['hits'] += int(result.hit)
            counters['requested_bytes'] += result.size_bytes
            counters['hit_bytes'] += result.size_bytes if result.hit else 0
            counters['total_response_time_ms'] += result.response_time_ms
            counters['origin_traffic_bytes'] += result.origin_traffic_bytes
            counters['cache_evictions'] += len(result.evicted_resources)
            counters['oversized_resource_requests'] += int(result.size_bytes > self.capacity_bytes)
            counters['_cache_used_bytes_sum'] += result.cache_used_bytes

    def _summary(self, counters):
        n = counters['request_count']
        size = counters['requested_bytes']
        public = {key: value for key, value in counters.items() if not key.startswith('_')}
        return {**public, 'misses': n - counters['hits'],
                'hit_ratio': counters['hits'] / n if n else 0.0,
                'byte_hit_ratio': counters['hit_bytes'] / size if size else 0.0,
                'average_response_time_ms': counters['total_response_time_ms'] / n if n else 0.0,
                'average_cache_utilization': (counters['_cache_used_bytes_sum']
                                              / (n * self.capacity_bytes)
                                              if n and self.capacity_bytes else 0.0)}

    def summary(self) -> dict:
        return self._summary(self._total)

    def per_client(self) -> list[dict]:
        return [dict(client_id=client, **self._summary(counters))
                for client, counters in sorted(self._clients.items())]
