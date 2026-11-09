"""LRU metadata is separate from cache insertion order."""
from policies.base import ReplacementPolicy


class LRUPolicy(ReplacementPolicy):
    def __init__(self):
        self.last_access = {}

    def on_hit(self, resource, request, step):
        self.last_access[resource.resource_id] = step

    def on_insert(self, resource, request, step):
        self.on_hit(resource, request, step)

    def choose_victim(self, items):
        return min(items, key=lambda key: self.last_access[key])

    def on_remove(self, resource_id):
        del self.last_access[resource_id]
