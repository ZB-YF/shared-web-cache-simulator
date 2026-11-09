"""Global and per-client metrics derived from immutable request results."""
from models import RequestResult


class Statistics:
    def __init__(self):
        self._total = self._empty()
        self._clients = {}

    @staticmethod
    def _empty():
        return dict(request_count=0, hits=0, requested_bytes=0, hit_bytes=0,
                    total_response_time_ms=0.0, origin_traffic_bytes=0)

    def record(self, result: RequestResult) -> None:
        client = self._clients.setdefault(result.request.client_id, self._empty())
        for counters in (self._total, client):
            counters['request_count'] += 1
            counters['hits'] += int(result.hit)
            counters['requested_bytes'] += result.size_bytes
            counters['hit_bytes'] += result.size_bytes if result.hit else 0
            counters['total_response_time_ms'] += result.response_time_ms
            counters['origin_traffic_bytes'] += result.origin_traffic_bytes

    @staticmethod
    def _summary(counters):
        n = counters['request_count']
        size = counters['requested_bytes']
        return {**counters, 'misses': n - counters['hits'],
                'hit_ratio': counters['hits'] / n if n else 0.0,
                'byte_hit_ratio': counters['hit_bytes'] / size if size else 0.0,
                'average_response_time_ms': counters['total_response_time_ms'] / n if n else 0.0}

    def summary(self) -> dict:
        return self._summary(self._total)

    def per_client(self) -> list[dict]:
        return [dict(client_id=client, **self._summary(counters))
                for client, counters in sorted(self._clients.items())]
