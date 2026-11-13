"""LFU counts accesses since insertion and breaks ties using LRU."""
from cache_simulator.policies.base import ReplacementPolicy


class LFUPolicy(ReplacementPolicy):
    def __init__(self):
        self.frequency = {}
        self.last_access = {}

    def on_hit(self, resource, request, step):
        self.frequency[resource.resource_id] += 1
        self.last_access[resource.resource_id] = step

    def on_insert(self, resource, request, step):
        self.frequency[resource.resource_id] = 1
        self.last_access[resource.resource_id] = step

    def choose_victim(self, items):
        return min(items, key=lambda key: (self.frequency[key], self.last_access[key]))

    def on_remove(self, resource_id):
        del self.frequency[resource_id]
        del self.last_access[resource_id]
