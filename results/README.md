# Local outputs and reference validation

Open [evaluation/](../evaluation/) for the required experiments. This directory retains reference-validation outputs and is the ignored workspace for fresh local runs.

| Directory | Contents |
|---|---|
| [Required evaluation](../evaluation/) | Primary 72-run evaluation, characterization, figures and verification |
| [reference/](reference/) | Preserved 100 KiB reference runs for FIFO, LRU, LFU, and Custom |
| [Additional synthetic study](../supplementary/synthetic/) | Ten-seed supplementary matrix: 1000 runs, 100 aggregate rows, 40 generated traces |

## Which file should I open?

- Formal `runs.csv`: one global result per workload, capacity, and policy. Includes evictions, oversized request counts, and mean utilization as well as hit ratios, latency, and traffic.
- Formal `per_client.csv`: client metrics identified by workload, capacity, and policy; select mixed and 5242880 bytes for the required fairness comparison.
- Formal `characterization/*.csv`: workload counts, popularity distribution/top five, requested bytes, and capacity-dependent oversized request counts.
- `characterization/hypotheses.md`: preliminary expectations derived from workload characterization before policy execution.
- `config.json`: identify input/source hashes, parameters, and provenance.
- Single-run `requests.csv`: inspect hit/miss, ordered victims, insertion-order cache contents, response, and cumulative counters.
- Single-run `summary.json` and `per_client.csv`: global and client summaries.
- Historical synthetic `summary.csv` and `d_compatible.csv`: seeded means/deviations and D's original rounded comparison schema.

Use [generated figures](../evaluation/figures/) to inspect the formal results. E supplies data analysis and A writes the final report; see [report materials](../reports/README.md). Instructor expected answers remain unchanged under [data/reference/](../data/reference/).

Historical output bytes, including old config source paths/hashes, remain as generated. Those source hashes describe historical snapshots. New runs record current sources. See the [current layout](../docs/repository_layout.md) and [migration map](../docs/layout_migration.json).

Ad hoc result directories remain ignored by Git. Tools refuse nonempty output directories; choose a fresh name instead of overwriting evidence. Only the maintainer selects additional snapshots for tracking, following the [contribution workflow](../docs/contributing.md).
