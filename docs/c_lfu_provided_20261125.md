# C handoff: LFU analysis and provided-trace replay

This note supplements C's merged [LFU reference review](c_lfu_reference_review.md)
and [original-run evidence](c_run_evidence_20261123.md). It analyzes the
November 25 [formal result matrix](../results/experiments/provided_20261125/runs.csv)
using the three instructor-provided fixed traces. It does not change LFU or
claim authorship of the team's new experiment pipeline.

## LFU's 18 results

Filtering the formal 72-row `runs.csv` to `policy=LFU` gives 3 workloads x 6
capacities = **18 rows**. Each row replays 3,000 requests with an initially
empty shared cache and 5 ms hit latency. The inputs are fixed; no random seed
or repeated-run averaging applies. Ratios in the CSV are fractions from 0 to
1; the percentages below are displayed values.

| Trace | Capacity | Hits / 3,000 | Hit ratio | Mean response (ms) | Evictions | Oversized requests | Mean utilization |
|---|---:|---:|---:|---:|---:|---:|---:|
| Sequential | 100 KiB | 634 | 21.13% | 327.513 | 932 | 1431 | 75.63% |
| Sequential | 500 KiB | 1281 | 42.70% | 289.545 | 995 | 716 | 82.68% |
| Sequential | 1 MiB | 1332 | 44.40% | 282.703 | 1093 | 570 | 84.26% |
| Sequential | 2 MiB | 1503 | 50.10% | 273.587 | 1065 | 424 | 65.78% |
| Sequential | 5 MiB | 1971 | 65.70% | 223.162 | 724 | 288 | 69.87% |
| Sequential | 10 MiB | 2693 | 89.77% | 166.330 | 0 | 288 | 60.62% |
| Repetitive | 100 KiB | 1252 | 41.73% | 205.400 | 252 | 1492 | 69.80% |
| Repetitive | 500 KiB | 1946 | 64.87% | 181.112 | 264 | 784 | 74.93% |
| Repetitive | 1 MiB | 2050 | 68.33% | 176.085 | 190 | 750 | 70.11% |
| Repetitive | 2 MiB | 2067 | 68.90% | 173.092 | 194 | 730 | 66.18% |
| Repetitive | 5 MiB | 2820 | 94.00% | 43.353 | 117 | 50 | 77.59% |
| Repetitive | 10 MiB | 2931 | 97.70% | 34.177 | 0 | 50 | 60.50% |
| Mixed | 100 KiB | 592 | 19.73% | 306.887 | 1034 | 1370 | 73.42% |
| Mixed | 500 KiB | 928 | 30.93% | 291.435 | 1338 | 730 | 78.96% |
| Mixed | 1 MiB | 1537 | 51.23% | 260.267 | 895 | 560 | 72.98% |
| Mixed | 2 MiB | 1504 | 50.13% | 250.727 | 1099 | 393 | 60.45% |
| Mixed | 5 MiB | 2362 | 78.73% | 184.695 | 389 | 234 | 83.96% |
| Mixed | 10 MiB | 2747 | 91.57% | 141.270 | 0 | 234 | 60.48% |

The [workload characterization](../results/experiments/provided_20261125/characterization/summary.csv)
shows that the top five resources account for 87.97% of Repetitive requests,
versus 24.60% of Sequential and 30.10% of Mixed requests. This concentration
is consistent with LFU's strongest 5 MiB result on Repetitive: 94.00% hits
and 43.353 ms mean response. Increasing its capacity from 2 to 5 MiB adds
753 hits and cuts mean response from 173.092 to 43.353 ms. One important
threshold is `lecture08.pdf`: it is 2,263,040 bytes and has 680 Repetitive
requests, so it cannot fit at 2 MiB but can fit at 5 MiB.

Capacity does not improve every LFU metric monotonically. On Mixed, 1 to
2 MiB reduces hits from 1,537 to 1,504 while mean response improves from
260.267 to 250.727 ms. At 10 MiB all three LFU traces have zero evictions,
but oversized requests remain because the two video resources still exceed
that capacity. Utilization alone is not a performance ranking.

At 5 MiB, LFU has more request hits and lower mean response time than FIFO
and LRU on all three traces; Custom does better on those two measures.
However, on Mixed, LFU has 277 more hits than FIFO while sending 22,790,144
more bytes to the origin server. Request-hit ratio and byte savings therefore
support different comparisons. These statements describe only the supplied
fixed traces and selected capacities.

## Reproduction and comparison record

At local commit `6e079a7b99e2822d64f8bcf58ff42b4a261e7b6c`, the LFU-only
replay was run from the repository root with Python 3.14.5:

```bash
python3 -m experiments.provided --output-dir results/c_lfu_provided_replay_20261125 --policies LFU
```

Use a new empty output directory when repeating this command. The complete
original generated [replay config](c_lfu_provided_20261125/replay_config_original.json)
is included verbatim (SHA-256
`79a359da7cc3f14b16b4b27522f60a20214d7bbc975fc47284526a9e43416f39`).
It records the three trace files, all six capacities, LFU, the 5 ms hit
latency, input hashes, and 33 source-file hashes. The published config records
Python 3.14.2; the fresh config records 3.14.5. Resource, all three trace,
and all 33 source hashes match the published config. The published config
does not record a Git commit, so matching hashes do not establish its unique
historical HEAD.

The [comparison script](c_lfu_provided_20261125/compare_replay.py) joins rows
by `(workload, capacity_bytes, policy)` and client rows additionally by
`client_id`, then compares every CSV field as exported. It also verifies the
input, source, capacity, and latency fields in both configs. Run it after a
fresh LFU-only replay:

```bash
python3 docs/c_lfu_provided_20261125/compare_replay.py results/c_lfu_provided_replay_20261125
```

Observed result: **18/18** LFU `runs.csv` rows match all 16 fields, and
**108/108** LFU `per_client.csv` rows match all 17 fields. The fresh CSV
SHA-256 values are:

| Fresh output | SHA-256 |
|---|---|
| `runs.csv` | `46d1846ec6baad7eb1bdf3fe43c174308bb626c61ee544bea5402e45ec9621dd` |
| `per_client.csv` | `c3ba039eceb3978affcd0f25d306cced75920c472193d7f076c9b81ce038ce93` |

For the Mixed, 5 MiB cell, a separate local request-log check counted
389 resources removed between successive cache states, 234 requests for
resources larger than 5,242,880 bytes, and mean post-request occupancy
`13,204,989,952 / (3,000 x 5,242,880) = 0.839550651... = 83.955065...%`, displayed as
83.96%. The 234 requests comprise 173 requests for one video and 61 for
the other. This checks the exported metrics for that cell; the 18-cell
replay verifies reproducibility with the same LFU implementation rather
than supplying an independent implementation of LFU.

The current suite passed **48/48** tests with
`python3 -m unittest discover -s tests -v`. The reference validator
`python3 -m experiments.validate_reference` matched every supplied field
for all 15 reference requests under FIFO, LRU, and LFU.

No discrepancy was found. This note and the original replay config provide
the C handoff without duplicating the team's published 72-row CSVs or the
three input traces.
