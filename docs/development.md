# Development and delivery status

**Reviewed on November 21, 2026. Target: all deliverables completed by November 25, 2026.** This status uses the merged GitHub main branch, its published results, and accessible local D handoff material. It does not establish that every private Google Drive file has been received or reviewed.

## Completed and verified

- The shared simulator, CSV validation, cache infrastructure, FIFO/LRU/LFU/LA-GDSF, metrics, CLI, exports, and batch tools are implemented.
- The current automated suite has 33 passing tests. All three standard policies match all ten instructor fields for all 15 reference requests. Custom reproduces D's 7-hit reference result.
- The existing synthetic matrix has 1000 per-seed runs, 100 aggregate rows, and 40 saved traces. The baseline, its configuration, four PNG/SVG figure pairs, and draft findings are in the repository.
- B's [PR #1](https://github.com/ZB-YF/shared-web-cache-simulator/pull/1) is merged: [FIFO/LRU review](b_fifo_lru_review.md) plus five focused tests for access order, multiple eviction, reinsertion, oversized misses, and shared-client history.
- C's [PR #2](https://github.com/ZB-YF/shared-web-cache-simulator/pull/2) is merged: [LFU/metric/experiment review](c_lfu_reference_review.md) plus three focused tests. Its review reconstructs LFU decisions and per-client metrics and reports an independent full-matrix replay with CSV and trace checks.
- D's original design/prototype and supplied experimental generators were integrated and compared with the shared simulator. B/C's PRs add validation evidence and do not change the algorithms or published result bytes.

## Remaining work and completion criteria

| Owner | What is already complete | Next concrete delivery | Completion criterion |
|---|---|---|---|
| A | Core, integration, published baseline; B/C PRs merged | Update status; select final artifacts with the team; integrate report/video materials; verify release | Final report, working video link, reproducible ZIP, and clean-directory run checked |
| B | FIFO/LRU review and tests received via PR | Concise report explanation and approximately two-minute video segment | Explain a policy divergence with an actual example; final text/segment delivered |
| C | LFU/metric tests and review received via PR | Original replay configuration plus verifiable result-comparison evidence in a follow-up PR; report methods/metrics and video segment | A can verify which code/inputs/seeds were run and how replay results reconcile with the published snapshot |
| D | Design/prototype integrated; Custom scenarios and baseline reproduced | Final confirmation/correction of implemented rules, consistent pseudocode, and Custom report section via Drive | Pre-eviction admission score and post-eviction insertion score are described consistently; limitations and checked scenarios are explicit |
| E | Baseline CSVs, generators, four figures, and draft findings available as inputs | Final matrix/snapshot and figure selection; CSV-backed interpretation; report body via Drive | At least three workloads, multiple capacities, metric trade-offs, and per-client effects explained with traceable numbers |

C's review names `results/c_lfu_reference_20261116/` and `results/c_matrix_20261116_final/`. Those directories are not tracked and were not present in the local handoff reviewed on November 21. This is a provenance/artifact handoff gap, not evidence that C failed to run the experiments. If their CSVs are identical to the published baseline, an original config and reproducible checksum/comparison record may establish the handoff without duplicating the entire matrix. If the original artifacts are unavailable, label any new run with its actual date and source version.

No newer D confirmation or E-specific final selection/report was found in the reviewed materials. D/E work may exist on Drive; A must receive it before recording completion. Existing figures and draft findings do not constitute E's sign-off or a final technical report.

## D's outstanding algorithm-description decision

The implementation follows D's executable prototype: compute the admission score before eviction, then recompute the inserted object's score after actual evictions update L. The delivered pseudocode instead retained the earlier insertion score. D must confirm the intended final rule and align the final pseudocode/report with the code. See [Custom policy](custom_policy.md). Keep the tested baseline stable unless an intentional rule change is justified; any such change requires the affected experiments and figures to be rerun.

## Suggested final handoff schedule

These are proposed coordination dates, not claims of team acceptance. All times are Shanghai time.

| Date | Required checkpoint |
|---|---|
| November 22, 20:00 | C's replay evidence, D's rule confirmation/pseudocode, E's final matrix/snapshot and figure list available; agree code/data freeze |
| November 23, 20:00 | Complete 3-4 page report draft; all five contributors check their text and numbers |
| November 24 | Finalize report; finish the five-person 10-minute video, upload, and verify its link |
| November 25 | Check the full ZIP and input/config/figure completeness; reproduce from a clean directory; finish all deliverables |

B/C submit follow-up work via PR. D/E submit via Google Drive. A alone handles final review/integration and merges to main. See [contribution workflow](contributing.md).

## Final package acceptance

- Source code, README and usage instructions, instructor inputs, required generated traces/configuration, experimental CSVs, and selected figures are included.
- The final report is 3-4 pages and answers which policy wins under which metric, when the ranking changes, and what the custom strategy costs.
- The five-person video is 10 minutes, includes all contributors and a real simulation demonstration, and has a usable YouTube link.
- Report numbers and figure labels refer to a named final result snapshot. Synthetic workloads are described as synthetic; prototype-derived Custom targets are not presented as instructor answers.
- Historical hashes and outputs remain intact. The final package runs without private local paths or missing ignored artifacts.
