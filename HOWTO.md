# Usage

## Setup and input validation

Use Python 3.10+ from the repository root. No dependencies are needed for simulation, testing, or batch execution.

```bash
python3 main.py --validate-only
python3 -m experiments.validate_reference
python3 -m unittest discover -s tests -v
```

Default input paths are relative to `main.py`, so invoking it from another working directory also works. Resources use full URLs as identifiers. Inputs are UTF-8 CSV; timestamps must include a timezone. Equal timestamps retain source order. See the [data dictionary](docs/DATA_DICTIONARY.md) for the exact schema.

## Run a policy

```bash
python3 main.py --policy FIFO --capacity 102400 --output-dir results/my_fifo_run
python3 main.py --policy LRU --capacity 102400 --output-dir results/my_lru_run
python3 main.py --policy LFU --capacity 102400 --output-dir results/my_lfu_run
python3 main.py --policy CUSTOM --capacity 102400 --output-dir results/my_custom_run
```

Policy names are case-insensitive. `CUSTOM_NOADM` disables only Custom's admission filter as an ablation. `--capacity` is in bytes: 100 KiB = 102400. `--hit-latency-ms` defaults to 5 and is also used by Custom's saved-latency score. Misses use the resource's origin latency without adding hit latency.

Use `--resources PATH` and `--requests PATH` to select inputs. If `--output-dir` is omitted, the default is `results/<request-file-stem>_<POLICY>_<capacity>`. An existing nonempty directory is rejected; choose a new output directory for another run. Success returns exit code 0; invalid input, configuration, or output location returns 2.

Each run writes:

| File | Contents |
|---|---|
| requests.csv | Every hit/miss, eviction sequence, cache insertion-order contents, capacity usage, response, and cumulative counters |
| summary.json | Global counts, byte totals, hit ratios, response times, and origin traffic |
| per_client.csv | The same metrics grouped by client |
| config.json | Policy, capacity, hit latency, input filenames and SHA256 hashes, request count, and source hashes |

Output uses full URLs. Reference validation maps those URLs to A-E without changing the general simulator. Ratios are 0-1; CSV and JSON preserve unrounded metrics. Empty traces and zero-byte denominators yield zero ratios, with counts retained.

## Batch experiments

```bash
python3 -m experiments.run --output-dir results/my_matrix
```

The default matrix has 4 workloads × 5 capacities × 5 policies/variants × 10 seeds = 1,000 runs. To run a smaller matrix:

```bash
python3 -m experiments.run --output-dir results/my_small_matrix --workloads mixed --capacities 102400 1048576 --policies LRU CUSTOM --seeds 0 1
```

Every policy receives the same trace for each workload and seed. All runs start with fresh objects. Batch output consists of `runs.csv` with per-seed and per-client metrics; `summary.csv` with arithmetic means and sample standard deviations; `d_compatible.csv` with D's rounded aggregate schema; `traces/` with exact generated inputs; and `config.json` with parameters, trace hashes, resource hash, source hashes, and Python version. Batch mode avoids exporting every request log; replay a saved trace through `main.py` when debugging one run.

## Optional figures

```bash
python3 -m pip install -r requirements-plots.txt
python3 -m experiments.plot --results-dir results/my_matrix --output-dir report/figures
```

The plotting command expects the full default matrix and creates four figures in PNG and SVG: capacity/latency, admission ablation, mixed-workload traffic trade-offs, and mixed-workload per-client latency. It reads actual aggregate and per-seed files. These figures are report inputs rather than a completed report.

## Troubleshooting

Unknown resources, duplicate metadata, invalid numeric values, non-GET methods, and timestamps without timezones are rejected with file and row diagnostics where applicable. Cache-Control and status 404 do not alter the simplified cacheability rules. URLs are never fetched.

A nonempty output directory error means the existing files have been preserved. A missing Matplotlib import affects only optional plotting. Input files and source code needed to rerun experiments are in this repository; private planning material is not required.
