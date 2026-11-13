"""LA-GDSF adapted from contributor D's executable prototype.

Request counts persist after eviction and bypass. Candidate scores use the current
inflation for admission; committed insertions use inflation after actual evictions.
"""
from collections import defaultdict
from cache_simulator.policies.base import ReplacementPolicy


class CustomPolicy(ReplacementPolicy):
    def __init__(self, hit_latency_ms=5.0, admission=True):
        self.hit_latency_ms = hit_latency_ms
        self.admission = admission
        self.inflation = 0.0
        self.frequency = defaultdict(int)
        self.priority = {}
        self.last_access = {}

    def on_request(self, resource, request, step):
        self.frequency[resource.resource_id] += 1

    def score(self, resource):
        # A one-byte effective size defines the otherwise undefined zero-size case.
        size_kib = max(resource.size_bytes, 1) / 1024.0
        return (self.inflation + self.frequency[resource.resource_id]
                * (resource.origin_latency_ms - self.hit_latency_ms) / size_kib)

    def on_hit(self, resource, request, step):
        self.priority[resource.resource_id] = self.score(resource)
        self.last_access[resource.resource_id] = step

    def on_insert(self, resource, request, step):
        self.on_hit(resource, request, step)

    def choose_victim(self, items):
        return min(items, key=lambda key: (self.priority[key], self.last_access[key]))

    def should_admit(self, resource, items, victims):
        return (not self.admission or not victims
                or self.score(resource) >= max(self.priority[key] for key in victims))

    def on_remove(self, resource_id):
        self.inflation = max(self.inflation, self.priority.pop(resource_id))
        del self.last_access[resource_id]
