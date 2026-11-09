# Testing and integration plan

The integrated suite now tests the input layer, cache infrastructure, simulation, policy behavior, metric formulas, and output boundaries. See [validation evidence](VALIDATION.md) for the completed checkpoint. The checks below remain the regression and final release checklist.

## Input layer

Run `python3 -m unittest discover -s tests -v`. Existing tests cover supplied data counts and URL identity, timestamp sorting and equal-time stability, unknown references, duplicate metadata, invalid numeric values, missing columns, non-GET requests, and timestamps without timezones. Extend coverage for empty fields, malformed row lengths, BOM handling, and header-only files when changing the loader.

## Cache and simulator acceptance cases

| Scenario | Expected behavior |
|---|---|
| First request into an empty cache | Miss; origin latency; resource-size traffic; insert if it fits |
| Repeated resource | Hit; configured hit latency; zero traffic; no reinsertion |
| Same URL requested by another client | Shared-cache hit is possible; metrics belong to the requesting client |
| Size equals capacity | Resource can be stored without exceeding capacity |
| Size is capacity minus/plus one byte | Smaller fits; oversized request causes no insertion or eviction |
| Repeated oversized resource | Miss and full origin traffic each time; existing cache remains unchanged |
| Multiple evictions needed | Query the policy repeatedly and record actual removal order |
| Duplicate admission | Explicit failure without double-counting bytes |
| Invalid victim identifier | Explicit failure without an infinite loop |
| Removal | Byte accounting and policy metadata remain synchronized |
| Equal request timestamps | Preserve source order; use step for deterministic recency |
| Zero capacity | Every positive-size resource is oversized |
| Empty trace or zero-byte denominator | No division by zero; Zero metric with counts retained |
| Miss with a different origin latency | Do not add hit latency to miss latency |
| Repeat run with the same configuration | Fresh objects and identical numerical results |

Check `used_bytes == sum(item.size_bytes)` and capacity bounds throughout operations. Use a small fake policy inside cache tests to verify infrastructure without presenting it as a completed production policy.

## Standard policies and reference comparison

Compare every row of `data/reference/expected_fifo.csv`, `expected_lru.csv`, and `expected_lfu.csv`. Map full URLs to A-E only in reference comparison. Check step, resource, client, hit/miss, eviction order, insertion-order contents, used capacity, response time, cumulative bytes, and cumulative hits.

Useful divergence points: at step 6 FIFO evicts A while LRU/LFU evict C; at step 8 LRU evicts B while LFU evicts D; step 9 requires multiple evictions. LRU access order must remain separate from insertion-order display. LFU must use LRU tie-breaking and reset counts on reinsertion.

Compare integer bytes and counts exactly; use appropriate tolerance for floating-point averages without rounding intermediate values. Independently calculate byte-hit ratio and per-client metrics. Investigate the first differing request instead of changing fixtures to match an implementation.

## Experiments and release

- Compare all four policies with identical input, capacity, hit latency, and initial state.
- Evaluate at least three workloads and multiple capacities; record exact bytes and generation seeds.
- Validate the custom policy against at least five design scenarios and its documented tie-breaking rules.
- Use unique output directories and input hashes. Per-client request counts must sum to the global count.
- Check that origin bytes equal total requested bytes minus hit bytes.
- Run the documented commands from a clean directory without relying on private notes or files outside this repository.
- Complete code, data, figures, report, video link, packaging, and reproducibility checks by November 25, 2026.
