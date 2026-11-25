# Experimental snapshots

| Snapshot | Input provenance | Matrix | Role |
|---|---|---|---|
| [provided_20261125/](provided_20261125/) | Three fixed instructor-provided traces, 3000 requests each | 3 workloads × 6 capacities × 4 primary policies = 72 runs | Required revised-assignment evaluation |
| [d_reproduction/](d_reproduction/) | D's seeded synthetic generators | 4 workloads × 5 capacities × 5 policy/ablation variants × 10 seeds = 1000 runs | Preserved supplementary experiments and historical prototype comparison |

The provided snapshot includes workload characterization, preliminary hypotheses, global metrics, client metrics, and configuration/input/source provenance. It covers policy comparisons at 5 MiB, capacity effects, and mixed-workload client effects at 5 MiB. Its ratios are 0-1 and traffic counts are bytes. Generated outputs are inputs to the team's remaining report analysis and figure selection.

The older synthetic snapshot retains 100 aggregate rows and 40 exact generated traces. Its [earlier findings](../../reports/experimental_findings.md) and figure pairs remain available, but do not establish results for the new instructor files. Original numerical files and configurations are not rewritten.

For independent reproduction use a new directory:

```bash
python3 -m experiments.provided --output-dir results/my_provided_matrix
python3 -m experiments.run --output-dir results/my_synthetic_matrix
```

The maintainer explicitly selects reviewed snapshots for Git tracking. See [experiment instructions](../../experiments/README.md) for schemas and options.
