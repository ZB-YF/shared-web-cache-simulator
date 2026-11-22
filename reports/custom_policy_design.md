# Custom Policy Design and Justification

Our custom strategy, Latency-Aware Greedy-Dual-Size-Frequency (LA-GDSF), aims to reduce average response time. Cache-hit ratio is a secondary measure; origin traffic and per-client effects are evaluated separately. Unlike FIFO, LRU, and LFU, its priority combines request frequency, resource size, and the latency saved by a cache hit:

```text
H(r) = L + F(r) * (origin_latency_ms(r) - hit_latency_ms) / size_KiB(r)
```

F(r) counts all requests for a resource, including misses and bypasses, and persists after eviction. L is a global inflation value, initially zero. Cached priorities are updated on insertion or hit. Victims are selected by the lowest stored H, breaking ties by least recent access.

On a fitting miss that needs space, the cache first previews sufficient victims. It computes a candidate score using the current L and bypasses insertion if that score is strictly below the largest victim score. Bypass remains a miss and generates full origin traffic, while preserving existing cache contents and L. Otherwise, removals update L to the maximum of its previous value and the removed priorities; the insertion score is then recomputed with this updated L. Oversized resources are never stored.

The size-normalized savings heuristic can protect frequently requested small objects against one-off large requests. Inflation helps age cached priorities; the T4 scenario demonstrates removal of a formerly hot object. These benefits do not guarantee lower traffic or client fairness. Persistent counters add metadata, and the current victim preview costs O(k*n) for k removals among n residents. Evaluation therefore includes byte-hit ratio, origin traffic, per-client latency, and a no-admission-filter ablation, rather than assuming a higher request hit ratio is sufficient evidence of improvement.
