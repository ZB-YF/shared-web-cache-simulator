# Validation evidence

Updated November 21, 2026 after the merged B/C reviews. The earlier integration checkpoint and D-prototype comparison below remain historical evidence; this update does not establish final team approval or complete the report/video deliverables.

## Automated correctness checks

```bash
python3 -m unittest discover -s tests -v
python3 -m experiments.validate_reference
```

The current automated suite contains **33 passing tests**: the original 25 checks, five FIFO/LRU checks from B, and three LFU/metrics checks from C. On November 21 the merged implementation was rerun through the full suite, reference validator, and Custom CLI check. The original 25-test checkpoint also passed a clean-directory run without private files or existing results.

The input tests cover supplied counts, stable timezone-aware sorting, unknown references, duplicate metadata, invalid numeric values, missing columns, non-GET methods, and naive timestamps.

Integration tests cover all instructor reference fields; D's custom reference result and frozen scenarios; shared-cache client behavior; independent metric formulas; zero/exact/oversized capacities; zero-byte resources; multiple eviction and duplicate admission; invalid victims and read-only previews; LFU reset and LRU tie-breaking; exact custom-score ties and equality admission; bypass state preservation; configured hit latency; single-use simulators; empty exports; deterministic workload generation and CSV roundtrips; and repeat-run independence.

## Merged contributor reviews

- [B review](b_fifo_lru_review.md), merged in [PR #1](https://github.com/ZB-YF/shared-web-cache-simulator/pull/1): reconstructed FIFO/LRU trace, global/client metrics, and five focused tests. The review distinguishes its reconstruction from unaided handwritten work.
- [C review](c_lfu_reference_review.md), merged in [PR #2](https://github.com/ZB-YF/shared-web-cache-simulator/pull/2): LFU eviction decisions, independent client-metric reconstruction, three focused tests, and a reported seeded replay. The reviewed replay CSVs/configs were not delivered in the PR or found in the local handoff, so full independent-run artifact receipt remains pending.

The contributor PRs change tests and review documents only. Their review completion does not by itself establish D's final design confirmation, E's final matrix selection, or report completion. See [development status](development.md) for precise acceptance criteria.

## Reference checks

FIFO, LRU, and LFU each match **15 rows × all 10 instructor CSV columns**, including ordered evictions, insertion-order cache contents, used capacity, response times, cumulative origin bytes, and cumulative hits. Custom matches D's supplied 7-hit sequence and 299008-byte origin total. The tests do not replace instructor fixtures with generated outputs.

## Independent D-prototype comparison

A separate local verification used an archived copy of D's prototype with only its hardcoded input directory changed. The original delivered files remained unchanged. The prototype's original test script passed after path portability correction.

The integrated and original generators produced identical client/resource sequences for four workloads and seeds 0-9. Across five capacities and five policy/ablation choices, verification compared:

| Evidence | Count | Outcome |
|---|---:|---|
| Per-seed matrix runs | 1000 | Match |
| Request events: client, resource, hit/miss, ordered evictions, used bytes | 900000 | Match |
| Aggregate rows from D's results_D.csv | 100 | Match |
| Supplied aggregate CSV cells | 1700 | Match |

Global hits, origin bytes, average response, byte-hit ratio, and per-client hit ratios and average response were also compared to the independent prototype. The private verification script is review evidence; normal repository tests and experiment execution do not require access to private files.

## Reproduce the integrated matrix

```bash
python3 -m experiments.run --output-dir results/my_matrix
```

`runs.csv` retains unrounded per-seed values. `summary.csv` reports arithmetic means and sample standard deviations. `d_compatible.csv` reproduces D's rounding and column meanings, including the legacy `CUSTOM_noadm` spelling. Exact generated input traces and hashes accompany the outputs.

The checked local output is under `results/experiments/d_reproduction/`. This reviewed baseline and its traces are now included in Git. Ad hoc result directories remain ignored. See the [reorganization review](repository_review.md) for preserved historical provenance. All comparison results apply to the supplied metadata, reference trace, D's synthetic generators and tested boundaries; they do not imply performance guarantees on arbitrary workloads.
