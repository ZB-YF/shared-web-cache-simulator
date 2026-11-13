# Experimental evaluation

The integrated batch runner reproduces contributor D's synthetic workload matrix with no dependencies beyond Python's standard library.

```bash
python3 -m experiments.run --output-dir results/my_matrix
```

## Default matrix

| Capacity | Bytes |
|---|---:|
| 100 KiB | 102400 |
| 500 KiB | 512000 |
| 1 MiB | 1048576 |
| 5 MiB | 5242880 |
| 10 MiB | 10485760 |

Workloads: repetitive and sequential (600 requests each), mixed and scan_pollution (1200 each). Policies: FIFO, LRU, LFU, CUSTOM, CUSTOM_NOADM. Seeds: 0-9. This gives 1,000 runs and 100 mean rows. Scan pollution and the no-admission policy are additional diagnostic cases beyond the minimum required comparison.

`workloads.py` preserves D's selection ordering and random calls while removing private absolute paths and import-time file loading. Each generated trace uses full URLs and deterministic chronological timestamps. Inputs are synthetic, not instructor-provided user traces. Every policy shares the exact same workload/seed trace, regardless of capacity.

## Outputs

- `runs.csv`: unrounded per-seed global and client metrics.
- `summary.csv`: metric means and sample standard deviations across seeds.
- `d_compatible.csv`: D-compatible rounded means, including per-client columns.
- `traces/`: all 40 generated request files for replay through the single-run CLI.
- `config.json`: parameters, Python version, resource/source/trace hashes, and provenance.

The batch runner refuses nonempty output directories. It records summary metrics rather than every request log; reproduce an individual run using `main.py --requests <saved-trace>` if detailed logs are needed. D's 100 supplied aggregate rows have been matched independently; see [validation evidence](../docs/validation.md).

Optional plotting uses `python3 -m experiments.plot --results-dir results/my_matrix --output-dir reports/figures` after installing `requirements-plots.txt`. Mean and standard-deviation figures support review; they are not the final report. Complete team review and all deliverables by November 25, 2026.

The reviewed baseline is tracked at `results/experiments/d_reproduction/`. Historical configs retain the original source layout and hashes; new runs use the current package layout. Additional team inputs belong in `data/workloads/`; generated traces for a particular experiment stay inside that result snapshot.
