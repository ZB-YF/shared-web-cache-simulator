# Shared Web Cache Simulator

A trace-driven simulator for evaluating a shared HTTP cache across multiple clients. The project will compare FIFO, LRU, LFU, and a custom replacement policy using the same workloads and cache capacities. It reads local CSV files and does not make network requests.

## Status

This repository currently contains the initial scaffold, shared data models, a draft policy interface, an input loader, and a validation CLI. Cache operations, the simulation loop, replacement policies, statistics, and result export are **not implemented yet**. Interface proposals still require contributor review.

The team plans to complete all implementation, experiments, figures, documentation, report, video, packaging, and reproducibility checks by **November 25, 2026**.

## Quick start

Python 3.10 or newer is required. The current scaffold uses only the standard library.

```bash
python3 main.py --validate-only
python3 -m unittest discover -s tests -v
```

The supplied inputs contain 21 resources and 15 requests from 3 clients, referencing 5 distinct resources. Running without `--validate-only` reports the unimplemented simulation and exits with status 2; it does not generate experiment results.

## Repository structure

```text
main.py                  CLI and input validation
models.py                Resource, Request, SimulationConfig, RequestResult
data_loader.py           CSV loading, validation, and stable timestamp sorting
cache.py                 Cache storage and capacity management placeholder
simulator.py             Shared request processing placeholder
output_writer.py         Result export placeholders
metrics.py               Statistics interface placeholder
policies/
  base.py                Draft replacement-policy interface
  fifo.py / lru.py        FIFO and LRU placeholders
  lfu.py                 LFU placeholder
  custom.py              Custom policy placeholder
data/
  resources.csv          Supplied resource metadata
  requests_reference.csv Supplied reference requests
  reference/             Expected outputs and answer key
  workloads/             Reserved for experimental traces
docs/                    Technical specifications and development guidance
tests/                   Tests for the implemented input layer
experiments/             Experimental evaluation guidance
results/                 Reserved for generated results
report/figures/          Reserved for report figures
video/                   Reserved for demonstration materials
```

## Documentation

- [Usage](HOWTO.md)
- [Simulation requirements](docs/REQUIREMENTS.md)
- [Input data dictionary](docs/DATA_DICTIONARY.md)
- [Draft interfaces](docs/INTERFACES.md)
- [Development roadmap](docs/DEVELOPMENT.md)
- [Testing and integration plan](docs/TEST_PLAN.md)
- [Experimental evaluation](experiments/README.md)

Resources are identified by their full URL. Cache storage and replacement decisions are separated so every policy uses the same simulation workflow. The statistics module is named `metrics.py` to avoid shadowing Python's standard-library `statistics` module. Reference outputs are validation fixtures, not results produced by this scaffold.

All repository documentation, comments, diagnostics, and contributor-facing text are maintained in English.
