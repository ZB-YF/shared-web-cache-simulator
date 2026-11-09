# Shared Web Cache Simulator

A trace-driven simulator for evaluating a shared HTTP cache across multiple clients. It implements FIFO, LRU, LFU, and a latency-aware custom policy through one request-processing pipeline. Inputs are local CSV files; no network requests are made.

## Status

The runnable implementation includes input validation, cache capacity management, all four policies, per-request export, global and per-client metrics, reference validation, and seeded batch experiments. The custom policy and synthetic workloads were integrated from contributor D's delivered design and executable prototype.

The three standard policies match all ten supplied reference fields on all 15 requests. Custom reproduces D's 7-hit reference result. A 1,000-run synthetic matrix has been rerun through the integrated simulator and compared with D's prototype and aggregate CSV. See [validation evidence](docs/VALIDATION.md) and [experimental findings](docs/EXPERIMENTAL_FINDINGS.md).

The current milestone is **runnable implementation and reproduced experimental baseline, ready for contributor review**. The final team-reviewed report, video, final experiment selection, and submission package remain unfinished. The team completion target for all deliverables is **November 25, 2026**.

## Quick start

Python 3.10 or newer is required. Simulation, experiments, and tests use only the standard library.

```bash
python3 main.py --validate-only
python3 main.py --policy CUSTOM --capacity 102400 --output-dir results/my_custom_run
python3 -m experiments.validate_reference
python3 -m unittest discover -s tests -v
```

The supplied inputs contain 21 resources and 15 requests from 3 clients, referencing 5 distinct URLs. Output directories must be new or empty to prevent accidental result replacement.

## Reproduce the experimental matrix

```bash
python3 -m experiments.run --output-dir results/my_matrix
```

Defaults: four synthetic workloads, five capacities, FIFO/LRU/LFU/CUSTOM plus CUSTOM_NOADM as an admission-filter ablation, and seeds 0-9. The command writes 1,000 per-seed rows, 100 aggregate rows, exact generated traces, and configuration hashes. These workloads are synthetic, not instructor-provided browsing traces.

Plotting is optional and requires Matplotlib:

```bash
python3 -m pip install -r requirements-plots.txt
python3 -m experiments.plot --results-dir results/my_matrix --output-dir report/figures
```

## Repository structure

```text
main.py                  Validation and simulation CLI
models.py                Shared immutable input and result models
data_loader.py           CSV loading, validation, and stable timestamp sorting
cache.py                 Shared storage, capacity, and admission planning
simulator.py             Sequential hit/miss processing
metrics.py               Global and per-client statistics
output_writer.py         Deterministic CSV and JSON output
runner.py                Fresh per-run construction and provenance hashes
policies/                FIFO, LRU, LFU, LA-GDSF, and policy factory
experiments/             Seeded workloads, reference checks, batch runner, plotting
data/reference/          Instructor validation fixtures
tests/                   Input, reference, custom-policy, and integration checks
results/                 Generated runs and matrix outputs (ignored by Git)
report/figures/          Generated PNG and SVG figures
video/                   Demonstration planning
```

## Documentation

- [Usage and output files](HOWTO.md)
- [Simulation requirements](docs/REQUIREMENTS.md)
- [Input data dictionary](docs/DATA_DICTIONARY.md)
- [Interfaces and lifecycle](docs/INTERFACES.md)
- [Custom-policy specification and integration decisions](docs/CUSTOM_POLICY.md)
- [Validation evidence](docs/VALIDATION.md)
- [Experimental findings](docs/EXPERIMENTAL_FINDINGS.md)
- [Development status and remaining work](docs/DEVELOPMENT.md)
- [Testing plan](docs/TEST_PLAN.md)

Full URLs identify resources; reference aliases A-E are only for comparison. Cache insertion order remains separate from policy eviction priority. All public documentation, comments, and diagnostics are maintained in English. Generated outputs are local artifacts until deliberately included in a release; no remote publication has been performed.
