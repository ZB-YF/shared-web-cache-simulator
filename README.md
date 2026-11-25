# Shared Web Cache Simulator

A university course project that replays local HTTP request traces through one shared cache. It compares FIFO, LRU, LFU, and LA-GDSF, a custom latency-aware policy. It measures hit ratios, response time, origin traffic, client performance, evictions, oversized requests, and cache utilization. Resource URLs are never fetched over the network.

## Start here

| What you need | Where to look |
|---|---|
| Install, run, test, or reproduce results | [HOWTO](HOWTO.md) and [usage conventions](docs/usage.md) |
| Open the required experiment results | [72-run provided-trace evaluation](results/experiments/provided_20261125/) |
| Read test evidence and numeric run notes | [Test report](reports/test_report_20261125.md) and [run notes](reports/provided_experimental_findings.md) |
| Inspect generated experiment figures | [Formal figure outputs](reports/figures/provided_20261125/) |
| Check report handoff status | [Report materials and remaining work](reports/README.md) |
| Inspect input traces and reference answers | [Input datasets](data/README.md) |
| Read the code | [Core](cache_simulator/) and [policies](cache_simulator/policies/) |
| Submit or integrate a contribution | [B/C PRs, D/E Google Drive](docs/contributing.md) |
| See remaining team tasks | [Development status](docs/development.md) and [video plan](video/README.md) |

CSV results, input/source configurations, generated graphs, test reports and supporting run notes are included so they can be inspected without rerunning the simulator. The integrated four-page report and video/presentation drafts remain private until contributor materials have been collected and combined. Report interpretation, figure selection, individual explanations, and outstanding video contributions remain team responsibilities.

## Quick start

Use **Python 3.10 or newer**. Simulation, analysis, experiments, and tests require only the standard library. From the project root:

```bash
python3 main.py --validate-only
python3 -m experiments.validate_reference
python3 -m unittest discover -s tests -v
python3 main.py --requests data/workloads/provided/requests_mixed.csv --policy CUSTOM --capacity 5242880 --output-dir results/my_mixed_custom
python3 -m experiments.provided --output-dir results/my_provided_matrix
```

No compilation or real HTTP proxy is required. Output directories must be new or empty; choose a fresh name for repeat runs. `--capacity` is bytes. The reference validation uses 100 KiB (102400 bytes), and the required policy/client comparison uses 5 MiB (5242880 bytes). Hit latency is 5 ms. Every run starts empty and processes requests sequentially.

The root `main.py` is a thin entry point into `cache_simulator.cli`; it already supports selecting a resource file, request file, policy, and capacity. The November 25 update extends statistics and adds a fixed-input experiment pipeline while preserving cache-replacement algorithms. Each single run exports detailed requests, global/client summaries, and input/source provenance.

## Required evaluation

The revised assignment uses **three instructor-provided traces × six capacities × four primary policies = 72 deterministic runs**. Each trace contains 3000 requests from six clients for 21 resources. All runs use the same `data/reference/resources.csv` and unchanged workload CSVs.

The six capacities are **100 KiB, 500 KiB, 1 MiB, 2 MiB, 5 MiB, and 10 MiB**. The assignment explicitly requires six but gives only five examples; the additional 2 MiB is a documented project choice. The fixed traces need no random seeds or repeated-run averaging.

The pipeline first characterizes workloads and records preliminary hypotheses, then runs all policies. It supports the three required comparisons: policy effects at 5 MiB, six-capacity effects, and individual clients on mixed at 5 MiB. Added metrics count individual evicted resources, requests exceeding total capacity, and mean post-request occupancy. Ratios are exported as 0-1 values.

To regenerate formal graphs:

```bash
python3 -m pip install -r requirements-plots.txt
python3 -m experiments.plot_provided --results-dir results/my_provided_matrix --output-dir results/my_provided_figures
```

The six PNG/SVG figure pairs cover workload characteristics, policy metrics at 5 MiB, capacity effects, storage metrics, and mixed clients at 5 MiB. See [experiment instructions](experiments/README.md) for output schemas and characterization-only or request-log options.

## Repository structure

```text
main.py                              Single-run CLI entry point
HOWTO.md                             Setup, parameters, reproduction, troubleshooting
cache_simulator/                     Shared cache, loader, simulator, metrics, exports
  policies/                          FIFO, LRU, LFU, and LA-GDSF
experiments/
  provided.py                        Required fixed-trace characterization and matrix
  plot_provided.py                   Required workload/policy/capacity/client figures
  validate_reference.py              Original expected-output comparison
  run.py, workloads.py, plot.py       Supplementary seeded synthetic reproduction
data/
  reference/                         Metadata, reference trace, expected CSVs, answer key
  workloads/provided/                Three original instructor evaluation traces
tests/                               Input, CLI, policy, metric, and experiment checks
results/
  reference/                         Preserved historical 100 KiB runs
  experiments/provided_20261125/      Required 72-run results and characterization
  experiments/d_reproduction/        Preserved 1000-run synthetic snapshot and traces
reports/
  test_report_20261125.md             Program checks and recorded run evidence
  provided_experimental_findings.md   Supporting notes on the provided-trace outputs
  figures/provided_20261125/          Six formal PNG/SVG figure pairs
  experimental_findings.md           Preserved supplementary synthetic findings
docs/                                Requirements, design, validation, collaboration
video/                               Presentation requirements and recording/upload status
requirements-plots.txt               Optional Matplotlib dependency
```

Ordinary module/document names use lowercase snake_case. Conventional landing files retain `README.md`/`HOWTO.md`, and instructor filenames and original contribution contents are preserved. Historical configs retain the actual old source paths and hashes that produced them.

## Preserved supplementary experiments

D's synthetic matrix remains available at [d_reproduction](results/experiments/d_reproduction/): four generated workloads, five capacities, five policy/ablation variants, and ten seeds produce 1000 runs and 100 aggregate rows. It includes scan pollution and Custom's no-admission ablation. Its [original findings](reports/experimental_findings.md), 40 traces, and four original PNG/SVG figure pairs are retained.

```bash
python3 -m experiments.run --output-dir results/my_synthetic_matrix
python3 -m experiments.plot --results-dir results/my_synthetic_matrix --output-dir results/my_synthetic_figures
```

These experiments are supplementary. They do not replace the required provided-trace evaluation, and their conclusions must not be attributed to the instructor's new CSVs.

## Validation and collaboration

FIFO/LRU/LFU reproduce all ten supplied fields for all 15 reference requests. Custom reproduces D's 7-hit reference result: 68.666666... ms average response and 299008 origin bytes. The November 25 suite has **48 passing tests**: the 35 historical checks, six required-metric checks, five fixed-input experiment checks, and two independent-verifier checks. The formal audit checks 72 cells, 432 client rows and 216000 events with matching source hashes. See [validation](docs/validation.md) for evidence and [test plan](docs/test_plan.md) for release acceptance.

| Contribution | Accepted material | Follow-up |
|---|---|---|
| B: FIFO/LRU | [PR #1](https://github.com/ZB-YF/shared-web-cache-simulator/pull/1), [review](docs/b_fifo_lru_review.md), five tests | Review formal policy analysis and record own video segment |
| C: LFU/metrics/reproduction | [PR #2](https://github.com/ZB-YF/shared-web-cache-simulator/pull/2), [PR #3](https://github.com/ZB-YF/shared-web-cache-simulator/pull/3), and [PR #4](https://github.com/ZB-YF/shared-web-cache-simulator/pull/4) merged; [18-run LFU analysis and replay evidence](docs/c_lfu_provided_20261125.md) checked | Use accepted LFU/metric explanations for assembly and prepare own video; no duplicate replay delivery requested |
| D: LA-GDSF | [Original design](docs/d_la_gdsf_design.md), [revision review](docs/d_custom_policy_review.md), [report section](reports/custom_policy_design.md); video recorded per maintainer update | Retain existing design and recording for assembly; no further rewrite or recording requested |
| E: results/report | Formal CSVs and generated figures are available as analysis inputs | Deliver workload/capacity/client interpretation, select figures, write report analysis/conclusions, and record own segment |
| A: maintainer | Core, integration, new-requirements update, and reproducible result publication | Collect contributor materials, integrate the report afterward, coordinate recording/upload and final checks |

**A is the sole main-branch maintainer. B and C submit via pull requests; D and E submit via Google Drive.** A reviews, integrates, runs checks, merges, and publishes. The new statistics and provided-trace integration were prepared during maintainer integration; they are not presented as a new C submission. Public content stays in English, and private plans remain outside the repository. Complete Drive contents have not been inspected, so absence here is not a claim that no private draft exists.

The team target is **November 25, 2026**. The official Brightspace deadline is **December 4, 2026 at 17:59 Shanghai time**. Final team review, all five members' participation in the **10-minute video**, the YouTube link, and submission remain outstanding until checked. See [report status](reports/README.md), [video checklist](video/README.md), and [development status](docs/development.md).
