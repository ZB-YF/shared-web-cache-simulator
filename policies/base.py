"""Draft policy interface. Policies manage metadata and must not mutate the cache."""
from abc import ABC, abstractmethod
from typing import Mapping

from models import Request, Resource


class ReplacementPolicy(ABC):
    @abstractmethod
    def on_hit(self, resource: Resource, request: Request, step: int) -> None:
        """Handle one hit; step is the monotonically increasing request sequence number."""

    @abstractmethod
    def on_insert(self, resource: Resource, request: Request, step: int) -> None:
        """Called once after insertion; the initial LFU frequency is 1."""

    @abstractmethod
    def choose_victim(self, items: Mapping[str, Resource]) -> str:
        """Return one resource_id from the nonempty cache without deleting any items."""

    @abstractmethod
    def on_remove(self, resource_id: str) -> None:
        """Clear metadata after removal; LFU frequency resets on reinsertion."""
