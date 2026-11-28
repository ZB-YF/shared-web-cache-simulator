# Required experimental evaluation

**This is the primary result set for the revised assignment:** three instructor-provided workloads × six capacities × four policies = **72 deterministic runs**. Results, characterization, figures and verification are together here. No random seeds are used in this evaluation.

## Open the results

| Material | Contents |
|---|---|
| [runs.csv](runs.csv) | All 72 global results: hits, byte hits, latency, traffic, evictions, oversized requests and utilization |
| [per_client.csv](per_client.csv) | 432 client rows, with workload, capacity and policy identifiers |
| [figures/](figures/) | Six PNG/SVG figure pairs covering workloads, policies, capacities, storage and clients |
| [findings.md](findings.md) | CSV-backed observations, explanations and limits |
| [characterization/](characterization/) | Workload summaries, popularity distributions, top five resources, oversized counts and preliminary hypotheses |
| [config.json](config.json) | Original execution metadata, exact parameters and input/source hashes |
| [test_report.md](test_report.md) | Reference comparison, automated tests and independent metric checks |
| [validation/](validation/) | Verification of the relocated snapshot against the current checkout |

CSV ratios are fractions from 0 to 1; charts show percentages. Traffic is bytes, capacity is bytes, and latency is milliseconds.

## Three required comparisons

1. **Policy effects:** in `runs.csv`, select `capacity_bytes=5242880` for all three workloads and FIFO, LRU, LFU and CUSTOM.
2. **Capacity effects:** use all six capacities: 102400, 512000, 1048576, 2097152, 5242880 and 10485760 bytes.
3. **Client effects:** in `per_client.csv`, select `workload=mixed` and `capacity_bytes=5242880` for the four policies.

Useful figures: [policy comparison at 5 MiB](figures/policy_comparison_5mib.png), [capacity effects](figures/capacity_effects.png), [mixed clients at 5 MiB](figures/mixed_clients_5mib.png), and [workload characterization](figures/workload_characteristics.png).

All runs use the same [resource metadata](../data/reference/resources.csv), the [three original supplied traces](../data/workloads/provided/), a fresh empty shared cache, 5 ms hit latency and the supplied origin latency on a miss. The selected 2 MiB configuration is the team's additional capacity; six configurations and the 5 MiB comparison are required by the assignment.

## Reproduce without overwriting evidence

From the repository root:

```bash
python3 -m experiments.provided --output-dir results/my_provided_matrix
python3 -m experiments.verify_provided --results-dir results/my_provided_matrix
python3 -m experiments.verify_provided --results-dir evaluation --allow-source-drift
```

See [HOWTO](../HOWTO.md) for setup, figures and detailed options. The final command audits this historical result set using current sources and reports source differences explicitly. The original 33 Python source hashes still match; the only additional source is C's comparison helper, whose baseline path was updated for this layout. Original CSVs, figures, traces and configurations were not regenerated or edited. Dates inside `config.json` describe the actual execution, not result priority. See the [layout migration](../docs/repository_layout.md) for old-to-new paths and preserved provenance.

The [ten-seed synthetic experiments](../supplementary/synthetic/) are **additional evidence**, separate from this required matrix. E supplies data analysis; A authors and integrates the final 3–4 page report. Final report and presentation drafts remain private.
