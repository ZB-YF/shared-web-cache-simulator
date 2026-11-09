"""Cache infrastructure placeholder. The cache manages storage; the policy selects victims."""
from models import Request, Resource
from policies.base import ReplacementPolicy


class Cache:
    def __init__(self, capacity_bytes: int, policy: ReplacementPolicy):
        if capacity_bytes < 0:
            raise ValueError("capacity_bytes must not be negative")
        self.capacity_bytes = capacity_bytes
        self.policy = policy
        self.used_bytes = 0
        self._items: dict[str, Resource] = {}  # dict preserves insertion order

    def contains(self, resource_id: str) -> bool:
        raise NotImplementedError("Implement resource lookup")

    def can_fit(self, size_bytes: int) -> bool:
        """Check total capacity, independently of currently available space."""
        raise NotImplementedError("Implement the individual resource capacity check")

    def record_hit(self, resource: Resource, request: Request, step: int) -> None:
        raise NotImplementedError("Notify the policy without changing storage insertion order")

    def admit(self, resource: Resource, request: Request, step: int) -> tuple[str, ...]:
        """Skip oversized resources; evict until enough space exists, then insert and return victims in order."""
        raise NotImplementedError("Implement capacity accounting, eviction, and policy callbacks")

    def remove(self, resource_id: str) -> None:
        raise NotImplementedError("Update capacity accounting and policy metadata")

    def snapshot(self) -> tuple[str, ...]:
        raise NotImplementedError("Return an immutable snapshot in insertion order")
