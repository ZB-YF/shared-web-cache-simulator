"""Shared cache storage, capacity accounting, and transactional admission planning."""
from types import MappingProxyType
from cache_simulator.models import Request, Resource
from cache_simulator.policies.base import ReplacementPolicy


class Cache:
    def __init__(self, capacity_bytes: int, policy: ReplacementPolicy):
        if capacity_bytes < 0:
            raise ValueError("capacity_bytes must not be negative")
        self.capacity_bytes = capacity_bytes
        self.policy = policy
        self.used_bytes = 0
        self._items: dict[str, Resource] = {}  # dict preserves insertion order

    def contains(self, resource_id: str) -> bool:
        return resource_id in self._items

    def can_fit(self, size_bytes: int) -> bool:
        """Check total capacity, independently of currently available space."""
        if size_bytes < 0:
            raise ValueError("size_bytes must not be negative")
        return size_bytes <= self.capacity_bytes

    def record_hit(self, resource: Resource, request: Request, step: int) -> None:
        if resource.resource_id not in self._items:
            raise KeyError(resource.resource_id)
        self.policy.on_hit(resource, request, step)

    def admit(self, resource: Resource, request: Request, step: int) -> tuple[str, ...]:
        """Skip oversized resources; evict until enough space exists, then insert and return victims in order."""
        if self.contains(resource.resource_id):
            raise ValueError("Cannot admit an already cached resource")
        if not self.can_fit(resource.size_bytes):
            return ()
        # Preview all victims without deleting anything. Admission may reject the batch.
        remaining = dict(self._items)
        available = self.capacity_bytes - self.used_bytes
        victims = []
        while available < resource.size_bytes:
            victim = self.policy.choose_victim(MappingProxyType(remaining))
            if victim not in remaining:
                raise ValueError(f"Policy selected an invalid victim: {victim}")
            available += remaining.pop(victim).size_bytes
            victims.append(victim)
        planned = tuple(victims)
        if not self.policy.should_admit(resource, MappingProxyType(self._items), planned):
            return ()
        for victim in planned:
            self.remove(victim)
        self._items[resource.resource_id] = resource
        self.used_bytes += resource.size_bytes
        self.policy.on_insert(resource, request, step)
        return planned

    def remove(self, resource_id: str) -> None:
        resource = self._items.pop(resource_id)
        self.used_bytes -= resource.size_bytes
        self.policy.on_remove(resource_id)

    def snapshot(self) -> tuple[str, ...]:
        return tuple(self._items)
