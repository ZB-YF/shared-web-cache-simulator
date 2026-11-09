# Validation evidence

This records the integrated implementation checkpoint on November 9, 2026. It does not establish final team approval or complete the report/video deliverables.

## Automated correctness checks

```bash
python3 -m unittest discover -s tests -v
python3 -m experiments.validate_reference
```

The full automated suite contains **25 passing tests**. A clean-directory copy, excluding Git state, existing results, and private material, also passed the test suite, reference comparison, and Custom CLI run.

The input tests cover supplied counts, stable timezone-aware sorting, unknown references, duplicate metadata, invalid numeric values, missing columns, non-GET methods, and naive timestamps.

Integration tests cover all instructor reference fields; D's custom reference result and frozen scenarios; shared-cache client behavior; independent metric formulas; zero/exact/oversized capacities; zero-byte resources; multiple eviction and duplicate admission; invalid victims and read-only previews; LFU reset and LRU tie-breaking; exact custom-score ties and equality admission; bypass state preservation; configured hit latency; single-use simulators; empty exports; deterministic workload generation and CSV roundtrips; and repeat-run independence.

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

The checked local output is under `results/d_reproduction/`. Generated results are ignored by Git and must be selected explicitly for a final release. All comparison results apply to the supplied metadata, reference trace, D's synthetic generators and tested boundaries; they do not imply performance guarantees on arbitrary workloads.
