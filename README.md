# Shared Web Cache Simulator

A university course project that replays local HTTP request traces through one shared cache. It compares FIFO, LRU, LFU, and a custom latency-aware policy (LA-GDSF), measuring response time, hit ratios, origin traffic, and per-client performance. The simulator does not access resource URLs over the network.

## Start here

| What you need | Where to look |
|---|---|
| Run the program or tests | [Usage guide](docs/usage.md) |
| Read the code | [Core package](cache_simulator/) and [policy implementations](cache_simulator/policies/) |
| Inspect instructor inputs and expected answers | [Reference dataset](data/reference/) |
| See the four policies on the reference trace | [Reference run outputs](results/reference/) |
| Open the existing experiment CSVs | [Reproduced experiment baseline](results/experiments/d_reproduction/) |
| See the graphs and their interpretation | [Experimental findings](reports/experimental_findings.md) and [figures](reports/figures/) |
| Submit or integrate a team contribution | [Google Drive handoff and maintainer workflow](docs/contributing.md) |

The baseline CSVs, configuration files, generated traces, and PNG/SVG figures are included in GitHub. You can read them without installing Python or rerunning experiments.

## Setup and quick start

Use **Python 3.10 or newer**. Simulation, experiments, and tests use only the standard library. From the repository root:

```bash
python3 main.py --validate-only
python3 -m experiments.validate_reference
python3 -m unittest discover -s tests -v
python3 main.py --policy CUSTOM --capacity 102400 --output-dir results/my_custom_run
```

Use `python` instead of `python3` if that is your Python 3 command. No package installation or build step is needed. The supplied data contains 21 resources and 15 requests from 3 clients. The reference cache capacity is 100 KiB (102400 bytes) and hit latency is 5 ms. Output directories must be new or empty; choose another name when repeating a run.

Each simulation writes `requests.csv`, `summary.json`, `per_client.csv`, and `config.json`. Policy names are FIFO, LRU, LFU, CUSTOM, and CUSTOM_NOADM (the custom admission-filter ablation). See the [usage guide](docs/usage.md) for inputs, parameters, output fields, and troubleshooting.

## Repository structure

```text
main.py                         Small CLI entry point; existing run commands still work
cache_simulator/                All simulator source code
  cli.py                        Argument parsing and single-run execution
  cache.py, simulator.py        Shared storage and request processing
  data_loader.py, models.py     Input validation and shared data types
  metrics.py, output_writer.py  Statistics and CSV/JSON export
  runner.py                     Fresh run construction and provenance hashes
  policies/                     FIFO, LRU, LFU, and LA-GDSF implementations
experiments/                    Workload generation, batch runs, validation, plotting
  README.md                     Experimental matrix and output meanings
data/
  reference/                    Original resource/request CSVs, expected CSVs, answer key
  workloads/                    Reserved for additional team-authored input traces
tests/                          Automated input, CLI, cache, policy, and integration tests
results/
  reference/                    Reviewed 100 KiB runs for the four primary policies
  experiments/d_reproduction/   Existing 1000-run baseline, summary CSVs, config, 40 traces
reports/
  experimental_findings.md      Draft analysis based on the reproduced data
  figures/                      Four comparative figures, each in PNG and SVG
  README.md                     Report status and figure index
docs/                           Usage, design, validation, collaboration, repository review
video/                          Demonstration planning and eventual video-link information
requirements-plots.txt          Optional plotting dependencies
```

Python modules and ordinary documentation filenames use lowercase snake_case. Standard landing files retain `README.md`; instructor CSV names are preserved. New default single-run directory names use lowercase policy names. Policy identifiers inside CSV data retain their existing uppercase spelling.

## Reproduce experiments and figures

The default matrix replays four synthetic workloads across five capacities, four primary policies plus one ablation, and seeds 0-9: **1000 runs and 100 aggregate rows**.

```bash
python3 -m experiments.run --output-dir results/my_matrix
```

The existing [baseline](results/experiments/d_reproduction/) is already available. A new batch creates per-seed metrics, means and sample standard deviations, D-compatible rounded summaries, exact request traces, and configuration hashes. These are synthetic workloads derived from contributor D's delivery, not real browsing measurements.

Matplotlib is needed only to regenerate figures:

```bash
python3 -m pip install -r requirements-plots.txt
python3 -m experiments.plot --results-dir results/experiments/d_reproduction --output-dir results/my_figures
```

This example uses a fresh output location to leave the reviewed [published figures](reports/figures/) intact. The plotting tool expects the complete default matrix. Ad hoc runs under `results/` are ignored by Git; the maintainer explicitly selects reviewed artifacts for publication.

## Status and collaboration

All 25 existing tests pass, the standard policies match every supplied reference field, and the custom policy reproduces D's reference result. The repository reorganization preserves algorithms, datasets, existing numerical outputs, and figures. See [validation evidence](docs/validation.md) and the [repository review and migration notes](docs/repository_review.md).

**There is one GitHub maintainer.** Other team members submit source, documents, checks, and findings through Google Drive. The maintainer reviews, integrates, tests, commits, and pushes those files. Team members are not required to push branches or open pull requests. Public project content is in English; private planning remains outside the repository.

The final team-reviewed report, video, and submission package are still pending. The target for completing all deliverables is **November 25, 2026**. Current ownership and next steps are in [development status](docs/development.md).

## Design documentation

- [Simulation requirements](docs/requirements.md)
- [Input data dictionary](docs/data_dictionary.md)
- [Module and policy interfaces](docs/interfaces.md)
- [Custom-policy rules and documented integration decisions](docs/custom_policy.md)
- [Testing and integration checklist](docs/test_plan.md)
