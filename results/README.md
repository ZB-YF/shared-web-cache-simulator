# Published simulation outputs

These reviewed baseline files are included in Git so teammates can inspect the same CSVs and configuration snapshots without running the simulator.

| Directory | Contents |
|---|---|
| [reference/](reference/) | Single runs of FIFO, LRU, LFU, and Custom on the instructor trace at 100 KiB |
| [experiments/d_reproduction/](experiments/d_reproduction/) | 1000 seeded synthetic runs, aggregate summaries, configuration, and 40 exact request traces |

## Which file should I open?

- `requests.csv`: inspect the exact hit/miss, evictions, insertion-order cache state, response time, and cumulative counters of a single run.
- `summary.json`: read that run's global metrics.
- `per_client.csv`: compare its client-specific metrics.
- `runs.csv`: inspect each seed's results in a batch.
- `summary.csv`: compare batch means and sample standard deviations.
- `d_compatible.csv`: compare the batch with D's rounded pre-experiment schema.
- `config.json`: identify policy, parameters, input/source hashes, and provenance.

[Report figures](../reports/figures/) and [draft findings](../reports/experimental_findings.md) are derived from these results. Instructor expected outputs remain separate in [data/reference/](../data/reference/).

The existing numerical files, generated traces, and original configs were preserved byte for byte during reorganization. Old source paths in historical configs refer to the code layout at generation time, not today's imports. The [migration map](../docs/reorganization_manifest.json) and baseline commit documented in the [repository review](../docs/repository_review.md) provide that context.

Ad hoc new directories such as `results/my_custom_run` remain ignored by Git. New runs must use new or empty output directories. Only the maintainer selects additional reviewed snapshots for tracking; see [contribution workflow](../docs/contributing.md).
