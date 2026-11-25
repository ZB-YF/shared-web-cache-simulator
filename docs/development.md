# Development and delivery status

## November 25 revised-assignment update

The revised assignment keeps the simulator/policy/reference rules and adds a specific provided-trace evaluation. The three new teacher CSVs are now included unchanged. The existing `main.py` entry point already supports selecting them. Statistics and the experiment pipeline have been extended; no replacement algorithm or historical output was changed.

| Work | Current status | Evidence |
|---|---|---|
| Core and policy correctness | Accepted historical functionality retained | Reference validator and existing tests |
| Added metrics | Implemented with capacity-aware counting and mean post-request occupancy | Metric tests and formal `runs.csv` |
| Required data | All three original 3000-request traces present; common resource file verified | [Provided inputs](../data/workloads/provided/README.md) |
| Characterization and hypotheses | Included before policy execution | Formal `characterization/` outputs |
| Required experiments | 72 cells: 3 workloads × 6 capacities × 4 policies, including 5 MiB | [Formal result snapshot](../results/experiments/provided_20261125/) |
| Generated charts | Available from fixed-input results; team selection and interpretation pending | [Figures](../reports/figures/provided_20261125/) |
| Test reports and run notes | Published as evidence and supporting material, separate from the integrated report | [Test report](../reports/test_report_20261125.md), [run notes](../reports/provided_experimental_findings.md) |
| Integrated report | Withheld until contributor materials are collected and integrated | [Report index](../reports/README.md) |
| Video | Individual contributions, recording/upload/link outstanding | [Video plan](../video/README.md) |
| Submission | Program and results are reproducible; final package awaits report and video | [HOWTO](../HOWTO.md), final acceptance below |

This update was prepared during maintainer integration. It does not imply that C submitted the new metrics/pipeline, or that E has independently reviewed or authored the new narrative. Previously accepted B/C PR work and D's design remain credited. Complete private Drive contents have not been inspected.

## Concrete remaining team actions

| Owner | Existing contribution retained | Next action and acceptance |
|---|---|---|
| A | Core, integration, accepted PRs, dataset/result publication | Coordinate review; check final numbers/report length; assemble members' recordings, verify YouTube link, inspect final extracted ZIP, and submit |
| B | FIFO/LRU review, reference comparison, five merged tests | Check formal FIFO/LRU workload/capacity explanations; provide corrections if needed and record own two-minute segment |
| C | LFU/metric tests, review, original configs, independent historical replay evidence | Review the new statistics and fixed-trace methods; reproduce/check a selected result; record own two-minute segment. The earlier evidence handoff is complete |
| D | LA-GDSF design/prototype, clarified score timing, accepted scenarios/report text; video recorded per maintainer update | Retain existing materials and recording for assembly; no new rewrite or recording requested |
| E | Existing report-analysis role; generated CSVs and charts available as inputs | Deliver workload and results interpretation, choose report figures, write analysis/conclusions and record own segment |

B/C deliver changes through PRs. D/E use Google Drive. A alone reviews, integrates, merges, and publishes to main. Ask for concrete files, a PR, or a Drive link and the unresolved issue; do not request completed reference tests or historical evidence again without a new discrepancy.

## Final acceptance still required

1. Collect B/C/E's remaining explanations and analysis, then integrate them with accepted A/D materials. Confirm the report's 3-4 page length, exact snapshot, units, metric definitions and interpretations. Keep the final report and presentation drafts private until integration; D's existing design and recording do not need another revision cycle.
2. Verify the package contains every source/input/script/result/figure/report needed for reproduction, and rerun the HOWTO from its extracted directory without private paths.
3. Record the real simulator demonstration and collect the remaining individual segments, retaining D's completed recording. Assemble the five-member 10-minute video, check playback/audio/legibility, upload to YouTube, and verify its link without the owner's login.
4. Submit the complete ZIP and video link on Brightspace. Generated files and a script are preparation, not evidence of upload or submission.

Use the 72-run provided-trace matrix as the primary evaluation. The historical 1000-run synthetic matrix remains supplementary; its input seeds, old configs, CSVs, traces, and graphs are preserved. At mixed/5 MiB the new results show all clients improve in mean latency under Custom relative to the standard policies; do not reuse the old synthetic client-harm conclusion as if it described this trace. Lower response time can still accompany higher origin traffic.

The team target remains **November 25, 2026**. The official deadline remains **December 4, 2026 at 17:59 Shanghai time**. The historical suggested dates below are retained records and are not new promises or confirmations.

## Historical status reviewed November 24

The following record is retained for handoff/provenance context. Its pending lists and suggested dates describe the state before the revised requirements were integrated; the current sections above take precedence.

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
