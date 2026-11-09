"""FIFO: hits do not change insertion order."""
from policies.base import ReplacementPolicy


class FIFOPolicy(ReplacementPolicy):
    def on_hit(self, resource, request, step):
        pass

    def on_insert(self, resource, request, step):
        pass

    def choose_victim(self, items):
        return next(iter(items))

    def on_remove(self, resource_id):
        pass
