# Experimental evaluation

The batch runner and experimental traces have not been implemented. Experimental design should be agreed before execution; reference validation must pass before large runs.

## Proposed capacity matrix

| Capacity | Bytes |
|---|---:|
| 100 KiB | 102400 |
| 500 KiB | 512000 |
| 1 MiB | 1048576 |
| 5 MiB | 5242880 |
| 10 MiB | 10485760 |

These are suggested capacities, not a mandatory assignment list. Evaluate repetitive, sequential, and mixed workloads with FIFO, LRU, LFU, and CUSTOM. Using all five capacities produces 60 configurations. Inspect the 21 resource sizes to avoid an uninformative matrix in which every resource is oversized or every requested resource fits.

Store traces under `data/workloads/` with generation rules and seeds. Intended output directories are `results/<workload>/<policy>_<capacity_bytes>/`. Save input paths and hashes, policy, capacity, hit latency, request count, workload, and seed in `config.json`.

Compare hit ratio, byte-hit ratio, average response time, origin traffic, and per-client performance. Explain how policy rankings change with workload, capacity, and objective. Identify where the custom policy helps and what it costs. Finish all experiments and figures by the November 25, 2026 completion milestone.
