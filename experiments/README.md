# Experimental evaluation

The repository has two experiment pipelines. Use the provided-trace pipeline for the revised assignment. D's original synthetic reproduction remains available as supplementary evidence, with its historical files preserved.

## Required provided-trace experiments

```bash
python3 -m experiments.provided --output-dir results/my_provided_matrix
```

Defaults use [the three supplied workloads](../data/workloads/provided/) and `data/reference/resources.csv`, with hit latency 5 ms. The complete matrix contains **72 runs**: sequential, repetitive, and mixed × six capacities × FIFO, LRU, LFU, and CUSTOM. Capacities in bytes are `102400 512000 1048576 2097152 5242880 10485760`. The added 2 MiB capacity is a documented team choice; the assignment specifies six capacities but lists only five examples.

Each trace has 3000 requests, six clients, and 21 requested resources. Fixed input files are reused for every policy/capacity. Every run starts with a fresh empty cache. No seeds or synthetic traces are introduced into this evaluation.

| Output | Meaning |
|---|---|
| `characterization/summary.csv` | Request, resource and client counts, requested bytes, and concentration/working-set statistics |
| `characterization/resource_popularity.csv` | Requested-resource counts and shares, sizes, byte volume, and popularity ranks |
| `characterization/top_five.csv` | The five most requested resources per workload |
| `characterization/oversized_requests.csv` | Oversized request counts at each selected capacity |
| `characterization/hypotheses.md` | Preliminary expectations derived before executing policy runs |
| `runs.csv` | One row per workload/capacity/policy with all global metrics |
| `per_client.csv` | Client metrics with workload/capacity/policy identifiers |
| `config.json` | Fixed-input provenance, parameters, hashes, source snapshot, and actual runtime information |

The three required comparisons are selections from this matrix: all workloads and four policies at 5 MiB; capacity curves across six capacities; and per-client comparisons for mixed at 5 MiB. The published November 25 snapshot is [provided_20261125](../results/experiments/provided_20261125/).

Use `--characterize-only` to inspect workloads before policy execution. `--requests-dir`, `--resources`, `--capacities`, and `--policies` select other inputs or smaller diagnostic matrices. `--request-logs` additionally writes detailed event logs; default aggregate output avoids storing 216000 verbose event rows. The existing [single-run CLI](../HOWTO.md) also exports exact request logs for any selected combination.

```bash
python3 -m experiments.provided --output-dir results/my_characterization --characterize-only
python3 -m experiments.provided --output-dir results/my_provided_check --capacities 5242880 --policies FIFO CUSTOM
python3 -m pip install -r requirements-plots.txt
python3 -m experiments.plot_provided --results-dir results/my_provided_matrix --output-dir results/my_provided_figures
```

Output directories must be new or empty. Invalid inputs are rejected before policy output is created. Ratios and average utilization are 0-1 in CSV; charts show percentages. Origin traffic is bytes in CSV. Do not calculate standard deviations across unrelated fixed workloads or capacities.

## Supplementary synthetic reproduction

```bash
python3 -m experiments.run --output-dir results/my_synthetic_matrix
python3 -m experiments.plot --results-dir results/my_synthetic_matrix --output-dir results/my_synthetic_figures
```

This unchanged generator reproduces D's four synthetic workloads, five capacities, five policy/ablation variants, and seeds 0-9: **1000 runs, 100 aggregate rows, and 40 saved traces**. Repetitive and sequential have 600 requests per seed; mixed and scan pollution have 1200. Policy variants include CUSTOM_NOADM to isolate the admission filter. The fifth capacity list is 100 KiB, 500 KiB, 1 MiB, 5 MiB, and 10 MiB; it does not supply the new sixth-capacity requirement.

`workloads.py` preserves D's random-call and selection ordering while removing private paths. `runs.csv` contains per-seed metrics; `summary.csv` reports arithmetic means and sample standard deviations; `d_compatible.csv` preserves D's rounded schema; `traces/` contains exact generated requests; `config.json` records parameters and hashes. Every policy shares the same trace for each workload/seed.

The reviewed historical snapshot is [d_reproduction](../results/experiments/d_reproduction/). Its original CSVs, configs, traces, and figures remain intact. Its 1000 runs do not replace the 72 required combinations using the instructor-provided traces. See [validation evidence](../docs/validation.md) for the independent prototype comparison.
