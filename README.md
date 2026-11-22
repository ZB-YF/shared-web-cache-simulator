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
| Submit or integrate a team contribution | [B/C pull requests, D/E Google Drive handoff](docs/contributing.md) |

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

**Status checked November 22, 2026:** the current suite has **35 passing tests** (the earlier 33 plus two checks for D's clarified behavior). FIFO/LRU/LFU match all ten supplied reference fields on all 15 requests, and Custom reproduces D's reference result: 7 hits, 68.666666... ms average response, and 299008 origin bytes. The existing 1000-run synthetic baseline and figures remain available. D's revised score-timing pseudocode matches the implemented algorithm; the updated prototype was compared again across 1000 runs and 900000 request events, with unchanged results.

| Contribution | Evidence available | Status |
|---|---|---|
| B: FIFO/LRU | [Merged PR #1](https://github.com/ZB-YF/shared-web-cache-simulator/pull/1), [review](docs/b_fifo_lru_review.md), five focused tests | Review and tests integrated |
| C: LFU, metrics, experiments | [Merged PR #2](https://github.com/ZB-YF/shared-web-cache-simulator/pull/2), [review](docs/c_lfu_reference_review.md), three focused tests | Review and tests integrated; original independent-run configuration/comparison evidence still to be handed off |
| D: Custom policy | Updated English rules/pseudocode and report draft received; [revision review](docs/d_custom_policy_review.md), [report section](reports/custom_policy_design.md) | Score-timing mismatch resolved; implementation and published results unchanged; final assembled-report check and video pending |
| E: experiment/report analysis | Existing [baseline CSVs](results/experiments/d_reproduction/) and [draft findings/figures](reports/experimental_findings.md) are available to review | E's final experiment selection, interpretation, and report contribution are not yet present in the reviewed materials |

**A is the sole maintainer of the main branch. B and C submit changes through pull requests; D and E submit materials through Google Drive.** The maintainer reviews B/C PRs, manually integrates D/E deliveries, runs checks, and handles final merges and publication. B/C should not push directly to main. Public project content stays in English; private planning remains outside this repository. See the [contribution workflow](docs/contributing.md) for artifact requirements.

C's review records a separate replay, but its named output directories are not tracked or available in the local handoff reviewed for this update. This is an evidence-handoff gap, not a failed test. D's updated local handoff has been inspected; complete Drive contents have not been inspected, and other unreceived final materials may exist there. Progress is marked complete only when its evidence is available.

Report-ready [A architecture](reports/simulator_architecture.md) and [D policy-design](reports/custom_policy_design.md) sections are available for assembly. The final team-reviewed 3-4 page report, five-person 10-minute video/link, and submission package remain pending. The target is **November 25, 2026 for all deliverables**. Detailed remaining work and proposed handoff dates are in [development status](docs/development.md). See [validation evidence](docs/validation.md) for commands and historical checkpoints.

## Design documentation

- [Simulation requirements](docs/requirements.md)
- [Input data dictionary](docs/data_dictionary.md)
- [Module and policy interfaces](docs/interfaces.md)
- [Custom-policy rules and documented integration decisions](docs/custom_policy.md)
- [Testing and integration checklist](docs/test_plan.md)
