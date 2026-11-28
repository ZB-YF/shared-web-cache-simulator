# Testing and release acceptance

The suite covers input validation, shared-cache behavior, policy rules, metric formulas, CLI behavior, and the required fixed-input experiment pipeline. See [validation evidence](validation.md) for recorded checks. Run:

```bash
python3 -m unittest discover -s tests -v
python3 -m experiments.validate_reference
```

## Input and cache correctness

Input tests cover known counts/URL identity, timezone-aware sorting and equal-time stability, unknown resources, duplicate metadata, invalid numeric fields, missing columns, non-GET requests, and naive timestamps. Supplied evaluation files must validate against the same metadata without editing their bytes.

| Scenario | Acceptance criterion |
|---|---|
| First request | Miss, origin latency, full resource-size traffic, insert if admitted and fitting |
| Repeated/cross-client request | Shared-cache hit possible; configured hit latency, zero origin bytes |
| Size equals capacity | Fits without exceeding capacity |
| Size exceeds total capacity | Never stored and does not evict existing objects |
| Repeated oversized request | Miss every time; count every request and its full origin traffic |
| Several victims required | Choose and record every actual victim in order |
| LFU tie/reinsertion | LRU tie-breaking; frequency resets to 1 after reinsertion |
| FIFO/LRU hit | FIFO insertion order unchanged; LRU recency updated |
| Custom rejected admission | No actual evictions; occupancy retained; request still counts |
| Zero capacity/empty trace | Valid single-run boundary behavior with zero utilization, no division by zero |
| Repeat run | Fresh state and identical numerical outcomes for identical inputs/configuration |

Check `used_bytes == sum(cached resource sizes)` and `0 <= used_bytes <= capacity_bytes`. Infrastructure tests use small fake policies where appropriate. No algorithm or instructor answer is modified to make a comparison pass.

## Reference and metric checks

Compare all 15 rows and all ten columns of `expected_fifo.csv`, `expected_lru.csv`, and `expected_lfu.csv`. URL aliases A-E are validation labels only. Check hit/miss, victim order, insertion-order display, used capacity, response, and cumulative counters. Investigate the first differing request. Compare integer counters exactly and floating averages with appropriate tolerance, without rounding intermediate results.

Independently verify global and client denominators, byte-hit ratio, and `origin_traffic_bytes == requested_bytes - hit_bytes`. Added metric checks must distinguish victim count from requests causing eviction, count repeated oversized requests relative to total capacity, and average occupancy after **every** request including hits/bypasses. The zero/empty conventions and capacity passed from the actual simulation configuration must be checked. Per-client utilization is observed shared occupancy, not allocated storage.

## Provided-trace evaluation acceptance

- Characterize all three supplied traces before executing policy runs; retain popularity, top five, requested volume, distinct counts, and oversized counts for all six capacities.
- Record preliminary hypotheses honestly as input-derived expectations, without claiming preregistration or a guaranteed winner.
- Cover exactly the requested unique cells: 3 workloads × 6 capacities × 4 primary policies = 72 default runs, including 5 MiB.
- Reuse identical resource metadata and fixed trace bytes for every relevant policy/capacity. Use empty initial state and 5 ms hit latency.
- Save all global metrics and client rows with workload/capacity/policy identifiers. Client request counts must sum to global counts.
- Check input/source/configuration hashes and matrix coverage. Fixed traces have no random seed dimension or artificial standard-deviation bars.
- Reject missing/invalid traces, duplicate parameters, nonpositive experiment capacities, and nonempty output locations. Invalid inputs must not create a partial policy result set.
- Compare the published matrix with a clean reproduction from the included source/data, separating runtime metadata from deterministic numerical evidence.

## Report and final submission acceptance

The required views are all workloads at 5 MiB, six-capacity curves, and mixed-client comparisons at 5 MiB. Figure labels and report numbers must trace to the published snapshot. Old synthetic findings remain explicitly supplementary; do not transfer a client-harm conclusion to new data without checking it.

The report must be 3-4 pages and cover all five revised questions. The ZIP must contain source, HOWTO/README, inputs, experiment scripts, CSVs/configs, figures, and report. Verify the extracted package without private paths or missing ignored files. Review contribution claims with all members. The five-person video must include all five participants, a real demonstration, a verified YouTube link, and the same result interpretation.

The official deadline is December 4, 2026 at 17:59 Shanghai time. A reviewed script and generated package do not establish completed recording, upload, team sign-off, or Brightspace submission. E provides data analysis; A authors the final integrated report.

## Preserved contributor checks

B's five FIFO/LRU tests, C's three LFU/metrics tests and merged original-run evidence, and the two D-related integration tests remain accepted. The pre-update suite had 35 passing checks. The new requirements add statistics and fixed-input experiment checks without reopening the completed historical handoffs. See [B review](b_fifo_lru_review.md), [C review](c_lfu_reference_review.md), [C run evidence](c_run_evidence_20261123.md), and [D review](d_custom_policy_review.md).
