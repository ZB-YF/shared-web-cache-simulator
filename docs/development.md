# Development and delivery status

**Reviewed on November 24, 2026. Target: all deliverables completed by November 25, 2026.** This status uses the merged GitHub main branch, its published results, and accessible local D handoff material. It does not establish that every private Google Drive file has been received or reviewed.

## Completed and verified

- The shared simulator, CSV validation, cache infrastructure, FIFO/LRU/LFU/LA-GDSF, metrics, CLI, exports, and batch tools are implemented.
- The current automated suite has 35 passing tests, including two added checks for the clarified Custom behavior. All three standard policies match all ten instructor fields for all 15 reference requests. Custom reproduces D's 7-hit reference result.
- The existing synthetic matrix has 1000 per-seed runs, 100 aggregate rows, and 40 saved traces. The baseline, its configuration, four PNG/SVG figure pairs, and draft findings are in the repository.
- B's [PR #1](https://github.com/ZB-YF/shared-web-cache-simulator/pull/1) is merged: [FIFO/LRU review](b_fifo_lru_review.md) plus five focused tests for access order, multiple eviction, reinsertion, oversized misses, and shared-client history.
- C's [PR #2](https://github.com/ZB-YF/shared-web-cache-simulator/pull/2) is merged: [LFU/metric/experiment review](c_lfu_reference_review.md) plus three focused tests. Its review reconstructs LFU decisions and per-client metrics and reports an independent full-matrix replay with CSV and trace checks.
- C's [PR #3](https://github.com/ZB-YF/shared-web-cache-simulator/pull/3) is now merged: original configs and an [evidence supplement](c_run_evidence_20261123.md). Maintainer checks matched all 27 batch and 25 reference source hashes, verified 40 trace hashes/counts, and reproduced metric CSVs/reference hashes from matching historical snapshots.
- D's updated English rules, pseudocode, test plan, and report draft were received on November 22. The revised H_cand/H_ins description matches existing code, resolving the earlier mismatch. The updated prototype and integrated simulator again match across 1000 runs and 900000 events; D's supplied CSV and published baseline are byte-identical. See [D revision review](d_custom_policy_review.md).
- Concise [A architecture](../reports/simulator_architecture.md) and [D policy-design](../reports/custom_policy_design.md) report sections are prepared. They still need assembly with E's results/analysis into the final report.

## Remaining work and completion criteria

| Owner | What is already complete | Next concrete delivery | Completion criterion |
|---|---|---|---|
| A | Core, integration, published baseline; B/C PRs merged | Update status; select final artifacts with the team; integrate report/video materials; verify release | Final report, working video link, reproducible ZIP, and clean-directory run checked |
| B | FIFO/LRU review and tests received via PR | Concise report explanation and approximately two-minute video segment | Explain a policy divergence with an actual example; final text/segment delivered |
| C | LFU/metric tests/review and original-config/replay evidence received via merged PRs #2/#3 | Concise LFU/metrics/experimental-methods report text and video segment | Text and demonstration agree with accepted code, configurations, and final data |
| D | Updated rules/pseudocode/test plan and report draft received and checked; timing mismatch resolved | Check the assembled report and prepare the two-minute video segment via Drive | Final report preserves the accepted rules and limitations; video contribution delivered |
| E | Baseline CSVs, generators, four figures, and draft findings available as inputs | Final matrix/snapshot and figure selection; CSV-backed interpretation; report body via Drive | At least three workloads, multiple capacities, metric trade-offs, and per-client effects explained with traceable numbers |

C's original configurations and comparison record are now in [the evidence supplement](c_run_evidence_20261123.md), closing the November 21 handoff gap. The three batch metric CSVs and all 40 generated traces reproduce the published values. The original batch config records Python 3.14.5; the maintainer replay used 3.14.2, with configuration matching after accounting for the actual Python version. The reference config and reported output hashes reproduce exactly. The raw Drive CSV package was not downloaded for these checks; the supplied checksums were independently reproduced, and duplicate baseline CSVs were not required for acceptance.

D's additional [LA-GDSF design package](d_la_gdsf_design.md) was received and published unchanged on November 24. Its embedded prototype code matches the earlier verified delivery and introduces no algorithm change. The [review notes](d_custom_policy_review.md) distinguish original contributor material from the maintained specification and edited report section.

No E-specific final selection/report was found in the reviewed materials; other work may exist on Drive. Existing figures and the A/D report sections do not constitute E's final selection or a completed technical report.

## D's confirmed algorithm description

D's revised delivery explicitly computes the candidate score using pre-eviction L and recomputes the insertion score after committed removals update L. Its prototype has unchanged executable logic and matches the integrated implementation. The previous description mismatch is closed; see [Custom policy](custom_policy.md) and [review evidence](d_custom_policy_review.md). The report section corrects scenario counts, units, and complexity wording from the supplied draft. No policy or simulator algorithm changed, and existing CSVs/configs/figures were preserved.

## Suggested final handoff schedule

These are proposed coordination dates, not claims of team acceptance. All times are Shanghai time.

| Date | Required checkpoint |
|---|---|
| November 22, 20:00 | Historical checkpoint: D rules/pseudocode received; C evidence has since merged in PR #3; E's final matrix/snapshot/figure list still required |
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
