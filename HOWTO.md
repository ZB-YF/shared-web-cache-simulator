# How to run and reproduce the project

The published **[72-run main evaluation](evaluation/)** contains the required result CSVs, workload characterization, figures, and test evidence. The older [ten-seed synthetic study](supplementary/synthetic/) is additional evidence.

## Requirements and setup

Use **Python 3.10 or newer**. Simulation, correctness tests, workload analysis, and experiment execution use only Python's standard library. No compilation, proxy server, web access, or private planning files are required.

Clone the repository, or extract the submission ZIP and open a terminal in its top-level project directory:

```bash
git clone https://github.com/ZB-YF/shared-web-cache-simulator.git
cd shared-web-cache-simulator
python3 --version
python3 main.py --validate-only
python3 -m experiments.validate_reference
python3 -m unittest discover -s tests -v
```

For an extracted ZIP, begin with `cd` into the extracted directory and omit `git clone`. Use `python` instead of `python3` where that is your Python 3 command. Existing output directories must be empty; choose another output name when repeating a command.

## Run one simulation with detailed request output

```bash
python3 main.py --resources data/reference/resources.csv --requests data/workloads/provided/requests_mixed.csv --policy CUSTOM --capacity 5242880 --hit-latency-ms 5 --output-dir results/my_mixed_custom
```

`--policy` accepts FIFO, LRU, LFU, CUSTOM, and the supplementary CUSTOM_NOADM ablation, case-insensitively. `--capacity` is **bytes**: 100 KiB = 102400; 5 MiB = 5242880. `--requests` selects a reference, instructor workload, or compatible additional trace. `--resources` selects its metadata. The default inputs are the reference resource/trace files; the default capacity is 100 KiB.

The command writes `requests.csv`, `summary.json`, `per_client.csv`, and `config.json`. Ratios, including average cache utilization, are 0-1; multiply by 100 for percentages. Traffic is bytes and response times are milliseconds. The result configuration records input and source hashes.

Default inputs are resolved from the program's location. From another working directory, an absolute script path works; explicit input paths must also be absolute or relative to that working directory. For example, replace the project path below with your actual extraction location:

```bash
cache_project='/absolute/path/to/shared-web-cache-simulator'
python3 "$cache_project/main.py" --requests "$cache_project/data/workloads/provided/requests_mixed.csv" --policy LRU --capacity 5242880 --output-dir /tmp/cache_mixed_lru_demo
```

## Reproduce the required 72-run evaluation

From the project root:

```bash
python3 -m experiments.provided --output-dir results/my_provided_matrix
```

Defaults are the three files under `data/workloads/provided/`, one common `data/reference/resources.csv`, four primary policies, hit latency 5 ms, and six capacities: **102400, 512000, 1048576, 2097152, 5242880, 10485760 bytes**. This is 3 × 6 × 4 = 72 deterministic runs. Every run starts empty. Fixed traces need no seeds or repeated-run averaging.

The runner analyzes all three workloads and writes preliminary hypotheses before executing policies. To inspect just that first step:

```bash
python3 -m experiments.provided --output-dir results/my_characterization --characterize-only
```

The full run produces:

| File | Contents |
|---|---|
| `characterization/summary.csv` | Requests, distinct resources/clients, requested volume, working-set size and concentration |
| `characterization/resource_popularity.csv` | Each requested resource's count, share, size, requested bytes, and rank |
| `characterization/top_five.csv` | Five most frequently requested resources per workload |
| `characterization/oversized_requests.csv` | Oversized request counts at each cache capacity |
| `characterization/hypotheses.md` | Preliminary performance expectations derived from input characteristics |
| `runs.csv` | All 72 global result rows, including the three added metrics |
| `per_client.csv` | Client results for every combination |
| `config.json` | Actual execution information, input/source hashes, and exact parameters |

The required policy comparison selects `capacity_bytes=5242880` in `runs.csv`. Capacity comparisons use all six capacities. The required fairness comparison selects `workload=mixed` and `capacity_bytes=5242880` in `per_client.csv`.

Add `--request-logs` when full event records for all runs are needed; the default avoids storing 216000 verbose request rows. For a smaller diagnostic matrix, use `--capacities 5242880 --policies FIFO CUSTOM`. Custom inputs can be supplied with `--resources PATH --requests-dir DIRECTORY`, retaining the three prescribed filenames.

Verify an existing snapshot without overwriting it:

```bash
python3 -m experiments.verify_provided --results-dir results/my_provided_matrix --output results/my_provided_review.json
```

The published [formal snapshot](evaluation/) is already included. Reproduction writes a separate directory; do not overwrite the published evidence. Source hashes describe the actual code used. They can differ from historical configs after a code change even if numerical results agree.

PR #4 added C's documentation-only `compare_replay.py` after the published snapshot was generated. Its baseline path now points to `evaluation/`. The snapshot's 33 original Python source hashes still match; the only added source is that reviewed helper. To audit the unchanged published matrix from the newer checkout, explicitly record the difference:

```bash
python3 -m experiments.verify_provided --results-dir evaluation --allow-source-drift --output results/my_published_review.json
```

Inspect `source_changes`; only the added comparison helper should appear, with no modified original source. The [historical post-merge review](docs/c_lfu_provided_20261125/maintainer_matrix_review.json) records the helper's earlier hash; keep that record intact rather than rewriting it after the path change. Fresh runs created from the current checkout can still be verified strictly. C's LFU-specific commands and preserved original config are documented in the [handoff](docs/c_lfu_provided_20261125.md). Historical paths in configs and logs describe their original execution; the [migration map](docs/layout_migration.json) identifies current locations.

## Reproduce figures

The supplied PNG/SVG graphs can be opened without installing plotting libraries. To regenerate formal graphs, install the optional plotting dependency:

```bash
python3 -m pip install -r requirements-plots.txt
python3 -m experiments.plot_provided --results-dir results/my_provided_matrix --output-dir results/my_provided_figures
```

This creates six PNG/SVG figure pairs: `workload_characteristics`, `policy_comparison_5mib`, `capacity_effects`, `capacity_storage`, `mixed_clients_5mib`, and the compact report plot `capacity_latency`. They cover input characteristics, policy metrics, capacity trends, storage behavior, and individual clients. Published figures are in [evaluation/figures/](evaluation/figures/); [report source materials](reports/README.md) explain how they relate to the final report.

## Supplementary synthetic experiments

The historical D reproduction remains separate from the required evaluation:

```bash
python3 -m experiments.run --output-dir results/my_synthetic_matrix
python3 -m experiments.plot --results-dir results/my_synthetic_matrix --output-dir results/my_synthetic_figures
```

This pipeline generates four synthetic workloads, five capacities, five policy/ablation variants, and ten seeds: 1000 runs. Its old means, standard deviations, traces, and graphs are preserved under [supplementary/synthetic/](supplementary/synthetic/). They do not replace the required three fixed instructor workloads and six capacities. Use the explicit `--output-dir` shown above to keep newly generated plots in a separate local directory.

## Troubleshooting and submission

A nonempty output error preserves existing files; choose a new directory. Invalid metadata, unknown requested resources, non-GET requests, and timezone-free timestamps are rejected. A missing Matplotlib import affects plotting only. No resource URL is fetched over the network.

The package must include code, this HOWTO, README, inputs, scripts, result CSVs/configs, figures, and the 3-4 page technical report. The five-person video must include all members, be uploaded to YouTube, and be linked on Brightspace separately. E supplies data analysis; A writes and integrates the final report. The integrated report and presentation drafts remain private until selected for final publication. See [implementation and contribution status](docs/development.md).
