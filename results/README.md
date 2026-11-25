# Published simulation outputs

The selected snapshots are included so teammates can inspect CSVs, provenance, and figures without installing Python.

| Directory | Contents |
|---|---|
| [reference/](reference/) | Preserved 100 KiB reference runs for FIFO, LRU, LFU, and Custom |
| [experiments/provided_20261125/](experiments/provided_20261125/) | Required 72-run evaluation of the three instructor-provided traces at six capacities |
| [experiments/d_reproduction/](experiments/d_reproduction/) | Preserved supplementary synthetic matrix: 1000 seeded runs, 100 aggregate rows, 40 generated traces |

## Which file should I open?

- Formal `runs.csv`: one global result per workload, capacity, and policy. Includes evictions, oversized request counts, and mean utilization as well as hit ratios, latency, and traffic.
- Formal `per_client.csv`: client metrics identified by workload, capacity, and policy; select mixed and 5242880 bytes for the required fairness comparison.
- Formal `characterization/*.csv`: workload counts, popularity distribution/top five, requested bytes, and capacity-dependent oversized request counts.
- `characterization/hypotheses.md`: preliminary expectations derived from workload characterization before policy execution.
- `config.json`: identify input/source hashes, parameters, and provenance.
- Single-run `requests.csv`: inspect hit/miss, ordered victims, insertion-order cache contents, response, and cumulative counters.
- Single-run `summary.json` and `per_client.csv`: global and client summaries.
- Historical synthetic `summary.csv` and `d_compatible.csv`: seeded means/deviations and D's original rounded comparison schema.

Use [generated figures](../reports/figures/provided_20261125/) to inspect the results; the team will supply report interpretation and final figure selection. See [report handoff status](../reports/README.md). Instructor expected answers remain unchanged under [data/reference/](../data/reference/).

Historical reference and synthetic output bytes, including old config source paths/hashes, remain as generated. Those source hashes describe historical snapshots, not the current tree. New runs record current sources. See the [repository review](../docs/repository_review.md) and [migration map](../docs/reorganization_manifest.json).

Ad hoc result directories remain ignored by Git. Tools refuse nonempty output directories; choose a fresh name instead of overwriting evidence. Only the maintainer selects additional snapshots for tracking, following the [contribution workflow](../docs/contributing.md).
