# Development status

The team target is **November 25, 2026 for all deliverables**.

## Completed integration milestone

- CSV loading and stable chronological request ordering using full URLs.
- Shared cache storage, capacity accounting, oversized handling, eviction previews, and admission commits.
- Unified request processing and deterministic FIFO, LRU, LFU, LA-GDSF, and no-admission ablation implementations.
- Global and per-client metrics, request CSV export, configuration/input/source hashes, and protected output directories.
- All instructor reference fields, D's frozen custom scenarios, dedicated tie-breaking tests, and core boundary tests.
- Four portable seeded synthetic workloads, a batch runner, and a 1,000-run reproduction of D's results.
- Standalone comparative figures and evidence-backed draft findings.

This integration advances the initial scaffold using D's supplied prototype and the assignment rules. It does not imply that separate B/C modules have been received or approved. Existing adapters provide a common working baseline for contributor review.

## Remaining team work

1. B reviews FIFO/LRU and their per-step evidence; C reviews LFU, statistics, batch execution, and Custom integration.
2. D reviews the documented executable-prototype interpretation, especially post-eviction score calculation, admission filtering, and tie-breaking.
3. E reviews whether D's synthetic workloads and capacities are the final experimental matrix, and checks the figures, statistical summaries, and client trade-offs. These workloads are generated data, not real browsing measurements.
4. Agree the final public interface. The extended hooks are implemented, but there is no recorded team-wide sign-off.
5. Turn verified findings into the final 3-4 page report, with consistent algorithm pseudocode and claims supported by exported data.
6. Record and upload the five-person 10-minute video with individual contributions.
7. Select final experiment artifacts, create the complete submission ZIP, and perform final clean-directory reproduction by November 25.

## Intended contribution areas

A: core/cache/CLI/export/integration. B: FIFO/LRU/reference validation. C: LFU/statistics/experiment execution and Custom implementation review. D: Custom design, pseudocode, scenario expectations, and limitations. E: experimental design, metric review, figures, and report analysis.

The current code can support independent review and report work without waiting for the initial scaffold to become runnable. Private planning and personal notes remain outside this public repository.

## Repository and handoff workflow

The source now lives in cache_simulator/, reference inputs and expected answers in data/reference/, reviewed CSV outputs in results/, and report findings/figures in reports/. The root main.py and experiment module commands remain the supported entry points. The sole maintainer integrates team deliveries from Google Drive and handles all GitHub commits and pushes; see [contribution workflow](contributing.md). Existing reviewed outputs are included in GitHub, so analysis can proceed without rerunning them.
