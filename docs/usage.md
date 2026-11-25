# Usage and output conventions

Start with the complete [HOWTO](../HOWTO.md) for setup, input selection, required experiments, optional plotting, and troubleshooting. Python 3.10+ and the standard library suffice for simulations, analysis, tests, and batch runs.

## Main entry point

```bash
python3 main.py --validate-only
python3 -m experiments.validate_reference
python3 -m unittest discover -s tests -v
python3 main.py --requests data/workloads/provided/requests_mixed.csv --policy CUSTOM --capacity 5242880 --output-dir results/my_mixed_custom
```

`main.py` delegates to `cache_simulator.cli`. It already accepts `--resources`, `--requests`, `--policy`, `--capacity` in bytes, `--hit-latency-ms` (default 5), `--output-dir`, and `--validate-only`. Selecting the new data does not require a separate simulator or changed policy algorithms. Input defaults resolve from the project location; explicit relative paths resolve from the current working directory.

Policies are FIFO, LRU, LFU, CUSTOM, and CUSTOM_NOADM (supplementary admission ablation), case-insensitively. Without `--output-dir`, results go to `results/<request-file-stem>_<lowercase-policy>_<capacity>`. A nonempty destination is rejected. Success exits 0; invalid input, configuration, or output exits 2.

Resources use full URLs as identifiers. Inputs are UTF-8 CSV with timezone-aware timestamps; equal timestamps retain source order. See the [data dictionary](data_dictionary.md). Cache-Control and status 404 do not change the assignment's simplified cacheability rules. No network requests occur.

## Single-run outputs

| File | Contents |
|---|---|
| `requests.csv` | Every hit/miss, ordered eviction list, insertion-order contents, post-request used bytes, response, and cumulative counters |
| `summary.json` | Global counts, hit ratios, response/traffic metrics, evictions, oversized requests, and average utilization |
| `per_client.csv` | Metrics grouped by requesting client |
| `config.json` | Policy, capacity, hit latency, input filenames/hashes, request count, and source hashes |

Ratios are unrounded 0-1 values, traffic is bytes, and latency is milliseconds. `cache_evictions` counts resources removed, not requests that cause a removal. `oversized_resource_requests` compares resource size with total capacity, not free space. `average_cache_utilization` averages post-request occupied/capacity ratios across **all** requests. Empty denominators and zero-capacity utilization use 0.

Per-client response/hit metrics concern that client's requests. Additional per-client utilization means shared occupancy observed after those requests; it is not a dedicated client cache. The shared cache allows one client's insertion to benefit another client's later request.

## Required fixed-input evaluation

```bash
python3 -m experiments.provided --output-dir results/my_provided_matrix
python3 -m experiments.provided --output-dir results/my_characterization --characterize-only
```

Use three instructor workloads, six capacities, four primary policies, and 5 ms hit latency: **72 deterministic runs**. Workload analysis and `characterization/hypotheses.md` precede policy execution. Global results and client results are separate CSVs. Add `--request-logs` for every run's detailed events, or replay one combination through `main.py`. See the [experiment guide](../experiments/README.md) for schemas, parameters, and the three required comparisons.

```bash
python3 -m pip install -r requirements-plots.txt
python3 -m experiments.plot_provided --results-dir results/my_provided_matrix --output-dir results/my_provided_figures
```

## Supplementary generated experiments

```bash
python3 -m experiments.run --output-dir results/my_synthetic_matrix
python3 -m experiments.plot --results-dir results/my_synthetic_matrix --output-dir results/my_synthetic_figures
```

The synthetic pipeline remains 4 workloads × 5 capacities × 5 policy/ablation variants × 10 seeds = 1000 runs. It retains per-seed values, means/sample deviations, D-compatible summaries, and exact generated traces. It does not substitute for the required fixed-input matrix.

## Included evidence and provenance

The repository includes [reference runs](../results/reference/), the [formal 72-run snapshot](../results/experiments/provided_20261125/), and the preserved [synthetic snapshot](../results/experiments/d_reproduction/). Formal figures are under `reports/figures/provided_20261125/`; older synthetic figures remain in their original locations.

Historical configs retain the source paths/hashes of their original code snapshots. They are not relabeled as current runs. The [repository review](repository_review.md) and [migration map](reorganization_manifest.json) explain the earlier reorganization. New runs hash current sources. The maintainer explicitly selects published snapshots; ad hoc result directories remain ignored. B/C submit via PR and D/E via Google Drive, following the [contribution workflow](contributing.md).
