# Development roadmap

The target for completing all project deliverables is **November 25, 2026**. Implementation should proceed through independently reviewable modules.

## Current implementation

Implemented: shared models, CSV loading and validation, stable request sorting, and the `--validate-only` CLI. The input-layer tests run against both supplied fixtures and malformed input cases.

Pending: contributor approval of interfaces, cache operations, simulation logic, policy implementations, statistics, export, reference comparison tooling, workload generation, batch experiments, figures, report, and demonstration video.

## Implementation sequence

1. Review `models.py`, the data dictionary, and the draft policy interface. Confirm URL identity, timestamp ordering, callbacks, and result fields before separate implementations diverge.
2. Implement cache lookup, total-capacity checks, removal, snapshots, hit notification, and admission. Reject oversized resources before any eviction. Maintain `used_bytes == sum(item.size_bytes)` and `0 <= used_bytes <= capacity_bytes`.
3. Implement single-request hit/miss handling, then the chronological loop. Hits use configured hit latency and zero traffic; misses use origin latency and resource-size traffic. Clients share one cache.
4. Integrate FIFO, LRU, LFU, and statistics through the same simulator. Compare every reference row before checking aggregate metrics. Independently validate byte-hit ratio and per-client statistics.
5. Connect real simulation to the CLI and implement exports. Save independent output directories and reproducible configurations. Build the batch runner on the single-run interface.
6. Document and implement the custom policy, including deterministic tie-breaking and boundary cases. Evaluate all policies on the same workloads and capacities.
7. Finish figures, usage documentation, the report, video, and the complete package. Reproduce the documented workflow from a clean directory by November 25.

## Integration ownership

| Contribution | Owner |
|---|---|
| Core simulator, cache infrastructure, CLI, export, integration | A |
| FIFO, LRU, and reference validation | B |
| LFU, statistics, experiment execution, and custom-policy implementation | C |
| Custom-policy design, pseudocode, test scenarios, and trade-off analysis | D |
| Experimental design, metric review, figures, and report analysis | E |

Interface changes must be coordinated across consumers. The custom algorithm is still unspecified; its design and implementation handoff must be agreed before coding. A working validation CLI does not establish simulator correctness or completion.
