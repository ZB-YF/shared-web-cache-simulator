# Shared Web Cache Simulator

A university course project that replays local HTTP request traces through one shared cache. It compares FIFO, LRU, LFU, and LA-GDSF, a custom latency-aware policy, without making network requests.

## Main evaluation — 72 experiments

**[Open the required evaluation](evaluation/)**: three instructor-provided workloads × six cache capacities × four policies. Results, workload characterization, figures, and test evidence are together in this top-level directory.

| Open | Contents |
|---|---|
| [Global results](evaluation/runs.csv) | All 72 workload/capacity/policy combinations and performance metrics |
| [Client results](evaluation/per_client.csv) | 432 client rows; use mixed and 5242880 bytes for the required client comparison |
| [Figures](evaluation/figures/) | Workload characteristics, policy comparisons, capacity effects, and mixed-client performance |
| [Workload analysis](evaluation/characterization/) | Counts, popularity, top five resources, requested bytes, and oversized requests |
| [Findings](evaluation/findings.md) | CSV-backed observations and limits |
| [Test report](evaluation/test_report.md) | Correctness checks and independent result verification |
| [Run configuration](evaluation/config.json) | Exact parameters, input hashes, and original source provenance |

Each provided trace contains 3000 requests, 21 resources, and six clients. All policies use the same [resource metadata](data/reference/resources.csv) and unchanged [workload files](data/workloads/provided/). The capacities are **100 KiB, 500 KiB, 1 MiB, 2 MiB, 5 MiB, and 10 MiB**. The additional 2 MiB is the team's selection to meet the six-capacity requirement.

The three required comparisons are policy effects at **5 MiB**, effects across **six capacities**, and individual clients on **mixed at 5 MiB**. These are deterministic replays, with no random seeds or repeated-run averaging. CSV ratios are 0–1, traffic is bytes, and response time is milliseconds.

## Run the simulator

Use **Python 3.10 or newer**. Simulation, workload analysis, experiments, and tests use only the standard library. From the repository root:

```bash
python3 main.py --validate-only
python3 -m experiments.validate_reference
python3 -m unittest discover -s tests -v
python3 main.py --requests data/workloads/provided/requests_mixed.csv --policy CUSTOM --capacity 5242880 --output-dir results/my_mixed_custom
```

`--capacity` is bytes. Every run starts with an empty shared cache and processes requests sequentially. Hits take 5 ms; misses use the supplied origin latency. Oversized resources bypass storage without evicting residents. Each single run exports request logs, global/client summaries, and provenance.

See [HOWTO](HOWTO.md) for setup, parameters, verification, and troubleshooting. Reproduce the main matrix and its figures into fresh directories:

```bash
python3 -m experiments.provided --output-dir results/my_provided_matrix
python3 -m pip install -r requirements-plots.txt
python3 -m experiments.plot_provided --results-dir results/my_provided_matrix --output-dir results/my_provided_figures
```

Matplotlib is needed only to regenerate plots. Existing CSVs and PNG/SVG figures can be inspected without installing it. Output directories must be new or empty; published evidence is preserved.

## Repository structure

```text
evaluation/                   Main required evaluation and its published evidence
  runs.csv                    72 global results
  per_client.csv              432 client results
  characterization/           Input statistics and preliminary hypotheses
  figures/                    Six required-evaluation PNG/SVG figure pairs
  findings.md                 Supporting analysis
  test_report.md              Correctness and verification evidence
  config.json                 Original run parameters and hashes
cache_simulator/              Cache, policies, input validation, metrics, exports
experiments/                  Required evaluation and supplementary experiment scripts
data/reference/               Resources, reference trace, and expected CSVs
data/workloads/provided/       Three instructor evaluation traces
tests/                        CLI, policy, metric, input, and experiment checks
reports/                      Architecture and Custom design source material
docs/                         Requirements, interfaces, validation, and contributions
results/reference/            Preserved 100 KiB reference outputs
supplementary/synthetic/      Extra ten-seed experiments, figures, and findings
video/                        Presentation requirements and publication status
main.py                       Single-run CLI entry point
HOWTO.md                      Setup and reproducible run instructions
```

The layout promotes the required evaluation without changing simulation algorithms or numerical outputs. Historical configs and audit logs keep their original paths and hashes; [the migration map](docs/layout_migration.json) records where files moved.

## Validation and contributions

Published checks record **48 passing tests**. FIFO/LRU/LFU match all ten supplied fields for all 15 reference requests. Independent accounting verifies 72 experiment cells, 432 client rows, and 216000 request events. See the [test report](evaluation/test_report.md) and [validation details](docs/validation.md) for the scope of each check.

| Member | Contribution |
|---|---|
| A | Shared simulator, integration, revised metrics and experiment pipeline; authors and assembles the final 3–4 page report |
| B | FIFO/LRU review, reference comparison, and five focused tests in merged [PR #1](https://github.com/ZB-YF/shared-web-cache-simulator/pull/1) |
| C | LFU/metrics tests, reviews, and reproducible experiment evidence in merged [PR #2](https://github.com/ZB-YF/shared-web-cache-simulator/pull/2), [#3](https://github.com/ZB-YF/shared-web-cache-simulator/pull/3), and [#4](https://github.com/ZB-YF/shared-web-cache-simulator/pull/4) |
| D | LA-GDSF design, prototype, scenarios, and preliminary experiments; existing recorded presentation segment retained |
| E | Delivered workload, capacity, and client data analysis as source material for A's final report |

**A is the sole GitHub maintainer. B/C submit through pull requests; D/E submit through Google Drive.** A reviews, integrates, tests, merges, and publishes. See [contributing](docs/contributing.md). The integrated report and video/presentation drafts remain private; public test reports and run notes are supporting evidence. [Report materials](reports/README.md) distinguish source contributions from the final report.

## Additional experiments

The **[supplementary synthetic study](supplementary/synthetic/)** preserves D's earlier generated workloads and admission ablation. Four workloads × five capacities × five policy/ablation variants × **ten seeds** produce 1000 runs, 100 aggregate rows, and 40 saved traces.

Its [figures](supplementary/synthetic/figures/) and [findings](supplementary/synthetic/findings.md) are **extra evidence**, separate from the 72 required experiments. They do not represent the instructor-provided workloads or satisfy the six-capacity requirement.

```bash
python3 -m experiments.run --output-dir results/my_synthetic_matrix
python3 -m experiments.plot --results-dir results/my_synthetic_matrix --output-dir results/my_synthetic_figures
```
