# Technical report and figures

Four figures have been generated from the integrated simulator's synthetic experiment reproduction, in PNG and SVG: latency_by_capacity, admission_ablation, mixed_tradeoffs, and mixed_client_latency. Regenerate them using the [usage guide](../docs/usage.md), preferably into a fresh output directory. PNGs are embedded in the [draft findings](experimental_findings.md).

The final 3-4 page technical report is still pending team review and authorship. It should cover architecture and data structures, the custom-policy rules and objective, experimental methodology, comparative figures, explanations, and limitations. Use actual exported numbers and align pseudocode with the [implemented Custom specification](../docs/custom_policy.md).

Explain which policy wins under which metric, when rankings change, and which client or traffic trade-offs arise. Complete the final report and figures by November 25, 2026. The draft findings and plots do not constitute a completed submission report.

## Sections available for final assembly

| Section | Status |
|---|---|
| [Simulator Architecture and Implementation](simulator_architecture.md) | A's code-based explanation is ready for report assembly |
| [Custom Policy Design and Justification](custom_policy_design.md) | Adapted from D's revised English draft; score timing, limitations, and complexity align with the integrated code |
| [Experimental findings and figures](experimental_findings.md) | Existing data-backed draft; E's final matrix/figure selection and narrative still pending |

D's original ten-file update is preserved in the private handoff archive; the additional [consolidated design document](../docs/d_la_gdsf_design.md) is published unchanged for reference; [review evidence](../docs/d_custom_policy_review.md) records what was received, checked, and edited. These sections and figures still need team assembly and review as one 3-4 page report. They are not a completed report submission.

## Final handoff still needed

E should identify the final result snapshot, workload/capacity/seed matrix, selected figures, and numeric evidence for the three central questions, then complete the result-analysis narrative. B/C's merged review notes support the standard-policy and metric sections. C's original configurations and replay comparisons are now received in merged [PR #3](https://github.com/ZB-YF/shared-web-cache-simulator/pull/3); see the [evidence supplement](../docs/c_run_evidence_20261123.md).

D's updated design and pseudocode no longer block report assembly. D should check the final combined wording and prepare the video contribution; no additional algorithm rewrite is requested. A integrates all sections, checks report length and numbers, and performs release packaging. Proposed dates and acceptance criteria are in [development status](../docs/development.md).
