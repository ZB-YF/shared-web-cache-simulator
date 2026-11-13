# Reviewed experimental snapshots

[d_reproduction/](d_reproduction/) contains the existing integration rerun of contributor D's synthetic matrix:

- Workloads: repetitive, sequential, mixed, scan_pollution.
- Capacities: 100 KiB, 500 KiB, 1 MiB, 5 MiB, 10 MiB.
- Policies: FIFO, LRU, LFU, CUSTOM, CUSTOM_NOADM.
- Seeds: 0-9.
- Outputs: 1000 per-seed rows, 100 aggregate rows, 40 saved traces, and configuration hashes.

The matrix was compared with D's executable prototype and supplied results. Its contents are preserved rather than overwritten by reorganization checks. The [draft findings](../../reports/experimental_findings.md) explain performance and client trade-offs.

Generate a separate matrix from the repository root with `python3 -m experiments.run --output-dir results/my_matrix`. The maintainer must explicitly select any new reviewed snapshot for Git tracking.
