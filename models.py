"""Draft shared data contracts; coordinate interface changes with contributors."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Resource:
    resource_id: str  # Full URL; reference aliases A-E are not primary keys
    size_bytes: int
    origin_latency_ms: float
    status_code: int
    content_type: str
    cache_control: str  # Preserved metadata; ignored during simulation


@dataclass(frozen=True)
class Request:
    source_row: int  # CSV line number for diagnostics, distinct from the sorted request step
    timestamp: datetime
    client_id: str
    resource_id: str


@dataclass(frozen=True)
class SimulationConfig:
    capacity_bytes: int = 102400
    hit_latency_ms: float = 5.0

    def __post_init__(self):
        from math import isfinite
        if self.capacity_bytes < 0:
            raise ValueError("capacity_bytes must not be negative")
        if not isfinite(self.hit_latency_ms) or self.hit_latency_ms < 0:
            raise ValueError("hit_latency_ms must be finite and nonnegative")


@dataclass(frozen=True)
class RequestResult:
    step: int
    request: Request
    size_bytes: int  # Required for byte-hit ratio calculations
    hit: bool
    response_time_ms: float
    origin_traffic_bytes: int
    evicted_resources: tuple[str, ...]
    cache_contents_oldest_first: tuple[str, ...]
    cache_used_bytes: int
    cumulative_origin_bytes: int
    cumulative_hits: int
