"""Policy construction; every call creates fresh per-run state."""
from policies.fifo import FIFOPolicy
from policies.lru import LRUPolicy
from policies.lfu import LFUPolicy
from policies.custom import CustomPolicy

POLICIES = ("FIFO", "LRU", "LFU", "CUSTOM", "CUSTOM_NOADM")


def create_policy(name, hit_latency_ms=5.0):
    name = name.upper()
    standard = {"FIFO": FIFOPolicy, "LRU": LRUPolicy, "LFU": LFUPolicy}
    if name in standard:
        return standard[name]()
    if name in {"CUSTOM", "CUSTOM_NOADM"}:
        return CustomPolicy(hit_latency_ms, admission=name == "CUSTOM")
    raise ValueError(f"Unknown policy: {name}")
