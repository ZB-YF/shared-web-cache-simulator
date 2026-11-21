# Technical report and figures

Four figures have been generated from the integrated simulator's synthetic experiment reproduction, in PNG and SVG: latency_by_capacity, admission_ablation, mixed_tradeoffs, and mixed_client_latency. Regenerate them using the [usage guide](../docs/usage.md), preferably into a fresh output directory. PNGs are embedded in the [draft findings](experimental_findings.md).

The final 3-4 page technical report is still pending team review and authorship. It should cover architecture and data structures, the custom-policy rules and objective, experimental methodology, comparative figures, explanations, and limitations. Use actual exported numbers and align pseudocode with the [implemented Custom specification](../docs/custom_policy.md).

Explain which policy wins under which metric, when rankings change, and which client or traffic trade-offs arise. Complete the final report and figures by November 25, 2026. The draft findings and plots do not constitute a completed submission report.

## Final handoff still needed

E should identify the final result snapshot, workload/capacity/seed matrix, selected figures, and numeric evidence for the report's three central questions. D should deliver a confirmed, consistent Custom algorithm description and limitations. B/C's merged review notes are available for the standard-policy and metric sections. A integrates these contributions into the final 3-4 page report. D/E deliver via Drive; B/C follow-up text and checks use PRs.

The review notes do not include C's original independent-run artifact directories. Request original configuration/comparison evidence before describing that handoff as complete. The existing published baseline remains available, so final report drafting can proceed while evidence is collected. Proposed dates and acceptance criteria are in [development status](../docs/development.md).
