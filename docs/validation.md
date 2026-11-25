# Validation evidence

The [program test report](../reports/test_report_20261125.md) summarizes the checks below. The latest [captured output](run_evidence_20261125/checks.txt) and [execution metadata](run_evidence_20261125/checks.json) record actual commands and exit codes. These reports and [run notes](../reports/provided_experimental_findings.md) are public supporting evidence; the final four-page report and presentation drafts remain private.

## November 25 revised-requirements checkpoint

The update retains policy algorithms, reference fixtures, historical results/configs, and original contributions. It adds capacity-aware statistics, the three original evaluation traces, fixed-input characterization and matrix execution, and formal visualizations/report materials.

```bash
python3 -m unittest discover -s tests -v
python3 -m experiments.validate_reference
python3 -m experiments.provided --output-dir results/my_provided_matrix
python3 -m experiments.verify_provided --results-dir results/my_provided_matrix --output results/my_provided_review.json
```

At the initial November 25 integration checkpoint, **46 tests passed**: 35 historical checks, six added metric checks, and five provided-trace experiment checks. The reference validator again matched all 15 rows and all ten supplied fields for FIFO, LRU, and LFU. Later release checks may extend this checkpoint; the command above runs the current full suite.

The three received CSVs were validated against the existing resource metadata, which matches the received resource file byte for byte. Each supplied workload has 3000 requests, six clients, and 21 distinct requested resources. Original trace bytes and SHA256 values are recorded in [the dataset guide](../data/workloads/provided/README.md) and formal configuration.

The [formal snapshot](../results/experiments/provided_20261125/) contains 72 default combinations: three provided traces, six capacities, and four primary policies. Global results include resource evictions, oversized request counts, and mean post-request utilization. Characterization and preliminary hypotheses are written before policy execution. Single-run CLI support for custom input/capacity/policy was already present; no replacement-policy rewrite is part of this update.

The reproducibility verifier checks the selected result snapshot without changing it. The published [review record](provided_run_review.json) records the maintainer's final verification when available.

Final November 25 source freeze: **48 tests pass** (35 historical + six metric + five experiment + two audit checks). The strict formal audit passes all 72 cells, 432 client rows, 216000 request events and 6552 exported metric values; its source snapshot matches exactly. A separate comparison with D's original prototype also matches the 72 runs and all events for hit/miss, ordered evictions and cache occupancy. The prototype remains an independently received contribution rather than a rewritten expected output.

The historical 1000-run synthetic matrix was rerun after the metric additions. All old `runs.csv` fields and all 40 generated traces match; `summary.csv` and `d_compatible.csv` remain byte-identical. Fresh run CSVs additionally expose the new metric columns. Published historical artifacts were preserved.

[Generated figures](../reports/figures/provided_20261125/) use the new snapshot. Do not infer policy guarantees from these finite traces. In particular, the earlier synthetic mixed-client trade-off is not automatically a finding for the new mixed input. Contributor report analysis, final assembly and video recording/upload remain outstanding.

## Historical evidence through November 24

The following retained record describes earlier code snapshots and the synthetic reproduction. References to “current” or “remaining” work below are historical as of their stated dates; the November 25 checkpoint and [development status](development.md) take precedence.

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
