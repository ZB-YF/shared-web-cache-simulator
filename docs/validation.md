# Validation evidence

Updated November 24, 2026 after C's evidence PR #3 and publication of D's additional consolidated design document. The earlier integration checkpoint and D-prototype comparison below remain historical evidence; this update does not establish final team approval or complete the report/video deliverables.

## Automated correctness checks

```bash
python3 -m unittest discover -s tests -v
python3 -m experiments.validate_reference
```

The current automated suite contains **35 passing tests**: the original 25 checks, five FIFO/LRU checks from B, three LFU/metrics checks from C, and two integration checks added for the clarified D behavior. The 33-test B/C checkpoint remains the November 21 record. On November 21 the merged implementation was rerun through the full suite, reference validator, and Custom CLI check. The original 25-test checkpoint also passed a clean-directory run without private files or existing results.

The input tests cover supplied counts, stable timezone-aware sorting, unknown references, duplicate metadata, invalid numeric values, missing columns, non-GET methods, and naive timestamps.

Integration tests cover all instructor reference fields; D's custom reference result and frozen scenarios; shared-cache client behavior; independent metric formulas; zero/exact/oversized capacities; zero-byte resources; multiple eviction and duplicate admission; invalid victims and read-only previews; LFU reset and LRU tie-breaking; exact custom-score ties and equality admission; bypass state preservation; configured hit latency; single-use simulators; empty exports; deterministic workload generation and CSV roundtrips; and repeat-run independence.

## Merged contributor reviews

- [B review](b_fifo_lru_review.md), merged in [PR #1](https://github.com/ZB-YF/shared-web-cache-simulator/pull/1): reconstructed FIFO/LRU trace, global/client metrics, and five focused tests. The review distinguishes its reconstruction from unaided handwritten work.
- [C review](c_lfu_reference_review.md), merged in [PR #2](https://github.com/ZB-YF/shared-web-cache-simulator/pull/2): LFU eviction decisions, independent client-metric reconstruction, three focused tests, and a reported seeded replay. That initial PR did not include original run artifacts; the original configs and comparison record have since been received in [PR #3](https://github.com/ZB-YF/shared-web-cache-simulator/pull/3), closing the follow-up evidence handoff.

The contributor PRs change tests and review documents only. D's revised score-timing rules have since been received and checked as described below; E's final matrix selection and the assembled report remain pending. See [development status](development.md) for precise acceptance criteria.

## November 24 follow-up evidence

C's [original configs and replay record](c_run_evidence_20261123.md) were checked before merging PR #3: all 27 batch and 25 reference source hashes match the named snapshots; all 40 trace hashes/counts match; three fresh batch metric CSVs match both the stated checksums and the published baseline; reference files match the stated hashes. Batch configuration matches apart from the reviewer's actual Python version (3.14.2 versus the recorded 3.14.5). The reference config reproduces byte for byte. The actual merged tree is identical to the tested prospective merge tree. Raw Drive originals were not downloaded; the submitted hash claims were independently reproduced.

D's additional [consolidated design source](d_la_gdsf_design.md) is published unchanged. All five embedded Python scripts match the earlier verified delivery. This is documentation/provenance publication, not a new algorithm or replacement result snapshot; the maintained [specification](custom_policy.md) and [review notes](d_custom_policy_review.md) remain the current interpretation.

## Reference checks

FIFO, LRU, and LFU each match **15 rows × all 10 instructor CSV columns**, including ordered evictions, insertion-order cache contents, used capacity, response times, cumulative origin bytes, and cumulative hits. Custom matches D's supplied 7-hit sequence and 299008-byte origin total. The tests do not replace instructor fixtures with generated outputs.

## November 22 D revision check

The updated English handoff resolves the old H_cand/H_ins pseudocode mismatch without changing prototype logic. D's portable original test script passes; the combined handoff's embedded scripts match its separate files. The updated prototype and integrated code match in 1000 runs and 900000 events, with all 100 aggregate rows / 1700 cells matching the delivered CSV. That CSV remains byte-identical to the published baseline.

The two new official integration checks cover the T4 aging eviction of A at step 20, and the final inflation/insertion score after multiple removals. All 35 tests and the standard reference validator pass. Original input data, result CSVs/configs, and figures have not been rewritten. Details and source hashes are in [D revision review](d_custom_policy_review.md) and its [JSON evidence](d_custom_policy_review.json).

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
