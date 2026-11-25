# Technical report and figures

The revised evaluation uses the three instructor-provided traces at six capacities. Its results and figures are separate from the preserved synthetic experiments.

## Required evaluation materials

| Material | Purpose |
|---|---|
| [Formal figures](figures/provided_20261125/) | Six figure pairs in PNG and SVG |
| [Formal result CSVs and provenance](../results/experiments/provided_20261125/) | All 72 combinations, client metrics, characterization, and configuration |

The formal figures are `workload_characteristics`, `policy_comparison_5mib`, `capacity_effects`, `capacity_storage`, `mixed_clients_5mib`, and the compact report plot `capacity_latency`. They cover input differences, policy comparisons at 5 MiB, six-capacity trends, the added storage metrics, and mixed-workload client comparisons at 5 MiB. See the [HOWTO](../HOWTO.md) to regenerate them into a fresh directory.

The report and video must address all five questions listed in the revised assignment: which policy wins under which metric; how workload characteristics affect results; how capacity affects policy rankings; whether all clients benefit equally; and the Custom policy's trade-offs. Use the same trace, resource metadata, capacity, and assumptions for fair comparisons. Explicitly state LA-GDSF's additional admission rule and lifetime frequency.

The generated outputs are available for team analysis. The integrated report is not published yet: contributor explanations, E's results analysis/conclusions and final figure selection must be collected before A assembles and uploads it. Individual presentation contributions and the actual video remain outstanding.


## Preserved contribution and supplementary sources

| Source | Scope |
|---|---|
| [Simulator architecture](simulator_architecture.md) | A's architecture/data-structure explanation |
| [Custom-policy design](custom_policy_design.md) | Edited report section based on D's accepted design |
| [Original consolidated LA-GDSF document](../docs/d_la_gdsf_design.md) | D's original delivery, unchanged; see [review](../docs/d_custom_policy_review.md) |
| [Earlier experimental findings](experimental_findings.md) | D-derived synthetic matrix and its four original PNG/SVG figure pairs |

The historical synthetic figures remain `latency_by_capacity`, `admission_ablation`, `mixed_tradeoffs`, and `mixed_client_latency` in `figures/`. They can support supplementary analysis, but cannot be presented as outcomes of the three provided CSVs. Original outputs and configurations are retained.

B/C's merged reviews and C's [original-config/replay supplement](../docs/c_run_evidence_20261123.md) remain accepted evidence. The maintainer's November 25 statistics and fixed-input pipeline update extends that work; it is not a new submission authored by C. E remains responsible for results interpretation, figure selection and report analysis/conclusions; D supplies the Custom explanation and limitations; B/C supply their policy and metric sections. Generated outputs do not mark those contributions complete. See [development status](../docs/development.md).
