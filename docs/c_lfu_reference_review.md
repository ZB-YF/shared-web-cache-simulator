# C review: LFU reference trace and client metrics

This is a focused review of the integrated LFU implementation against the
instructor's 15-request reference trace. It covers eviction decisions at steps
6, 9, and 13, independently reconstructs the exported per-client metrics,
and records C's separate seeded batch-experiment replay.
The A–E names below are the shorthand in the instructor answer key; the
simulator output uses full resource URLs.

## Inputs and reproduction

- Metadata: `data/reference/resources.csv`
- Requests: `data/reference/requests_reference.csv`
- Expected per-request results: `data/reference/expected_lfu.csv`
- Integrated output inspected: `results/reference/lfu_102400/requests.csv`
- Fresh C replay: `results/c_lfu_reference_20261116/requests.csv`, with
  `summary.json`, `per_client.csv`, and `config.json` in the same directory.
- Configuration: an initially empty shared cache of 100 KiB (102,400 bytes),
  5 ms hit latency, and LFU with LRU tie-breaking.
- Validation command from the repository root:
  `python3 -m experiments.validate_reference`
- Observed result on 2026-11-16: `PASS LFU: 15 requests, all 10 reference
  fields; hits=4, origin=370688 bytes`.

The fresh replay was run from the repository root with:

```bash
python3 main.py --policy LFU --capacity 102400 --hit-latency-ms 5 --output-dir results/c_lfu_reference_20261116
```

Its generated `requests.csv` was then compared field by field with
`expected_lfu.csv`, mapping full URLs to the instructor's A–E aliases and
comparing numeric fields numerically. All 15 rows and all 10 instructor
fields matched. The fresh `summary.json` also matches the reviewed LFU
summary: 4 hits, 11 misses, 26.6667% request hit ratio, 27.6% byte-hit
ratio, 84.3333 ms average response time, and 370,688 origin bytes.
The fresh CSV writes hit latency as `5.0`, while the existing snapshot writes
`5`; these represent the same 5 ms value. This replay uses the instructor
reference trace; the synthetic multi-workload experiment is reviewed below.

## Reconstructed eviction decisions

| Step | State immediately before the request | Space calculation and LFU decision | Expected and observed result |
|---|---|---|---|
| 6: request D (24 KiB) | A: 32 KiB, frequency 2, last access 4; B: 42 KiB, frequency 2, last access 5; C: 14 KiB, frequency 1, last access 3. Used: 88 KiB. | 88 + 24 = 112 KiB. C has the lowest frequency, so evict C (14 KiB). | MISS; evicted C; cache A,B,D; used 98 KiB; response 95 ms; cumulative origin 114,688 bytes; cumulative hits 2. |
| 9: request E (57 KiB) | A: 32 KiB, frequency 3, last access 7; B: 42 KiB, frequency 2, last access 5; reinserted C: 14 KiB, frequency 1, last access 8. Used: 88 KiB. | 88 + 57 = 145 KiB. Evict C first: combined use would still be 131 KiB. Evict B next: combined use becomes 89 KiB. | MISS; evicted C,B in that order; cache A,E; used 89 KiB; response 210 ms; cumulative origin 187,392 bytes; cumulative hits 3. |
| 13: request E (57 KiB) | A: 32 KiB, frequency 4, last access 12; reinserted B: 42 KiB, frequency 1, last access 10; D: 24 KiB, frequency 1, last access 11. Used: 98 KiB. | 98 + 57 = 155 KiB. B and D tie at frequency 1; B is least recently used (10 before 11), so evict B first. Combined use would still be 113 KiB, so evict D next. Final use is 89 KiB. | MISS; evicted B,D in that order; cache A,E; used 89 KiB; response 210 ms; cumulative origin 313,344 bytes; cumulative hits 4. |

The selected output rows agree with the instructor CSV for hit/miss,
eviction order, cache contents in insertion order, used capacity, response
time, cumulative origin traffic, and cumulative hits. No issue was found in
these three steps. The LFU source was not changed during this review.

## Per-client metrics reconstructed from the fresh request log

The fresh `requests.csv` was grouped by `client_id`. For each client, request
count, hits, requested bytes, hit bytes, response-time sum, and origin bytes
were added directly from the exported rows. Misses and ratios were then
calculated from those totals, without calling `cache_simulator.metrics`.
All 11 fields in each of the three `per_client.csv` rows matched.

| Client | Request steps | Hit steps | Hit ratio | Byte-hit ratio | Response-time sum | Average response | Origin traffic |
|---|---|---|---:|---:|---:|---:|---:|
| student-01 | 1, 4, 7, 10, 13 | 4, 7 | 2/5 = 40% | 64/195 = 32.82% | 435 ms | 435/5 = 87 ms | 131 KiB |
| student-02 | 2, 5, 8, 11, 14 | 5 | 1/5 = 20% | 42/136 = 30.88% | 350 ms | 350/5 = 70 ms | 94 KiB |
| student-03 | 3, 6, 9, 12, 15 | 12 | 1/5 = 20% | 32/169 = 18.93% | 480 ms | 480/5 = 96 ms | 137 KiB |

The client totals reconcile with `summary.json`: 15 requests, 4 hits,
500 KiB requested, 138 KiB served on hits, 1,265 ms total response time,
and 362 KiB (370,688 bytes) of origin traffic. Student-02 and student-03
have the same request hit ratio but different average response times, showing
why client response time must be reported alongside hit ratio. Step 12 also
shows the shared-cache behavior: student-03 hits A, which was first fetched
by student-01 at step 1.

## Independent seeded batch-experiment replay

From the repository root, after adding the focused tests in
`tests/test_lfu_metrics.py`, run:

```bash
python3 -m experiments.run --output-dir results/c_matrix_20261116_final
```

Use a new output directory on a repeat run; the runner refuses to overwrite
nonempty directories. This run used `data/reference/resources.csv` (SHA-256
`b2117bca54a566a999cd21333bb34a3dc25e0d0f371cf9aad8bfb7c63d1869e7`),
the workload generator in `experiments/workloads.py`, seeds 0–9, capacities
102400, 512000, 1048576, 5242880, and 10485760 bytes, and policies FIFO,
LRU, LFU, CUSTOM, and CUSTOM_NOADM. Hit latency was 5 ms. The four synthetic
workloads were `repetitive`, `sequential`, `mixed`, and `scan_pollution`.
`config.json` records Python 3.14.5, the exact source and input hashes, and
the 40 generated trace paths and hashes.

The result directory contains 1000 per-seed rows in `runs.csv`, 100 aggregate
rows in `summary.csv`, 100 D-compatible rows in `d_compatible.csv`, 40 replayable
trace CSVs, and `config.json`. All three output CSVs matched the repository's
`results/experiments/d_reproduction/` baseline byte for byte. This is a
reproducibility check, not an independent mathematical check by itself.

For the independent check, I read the exported CSVs and recomputed each run's
miss count, request hit ratio, byte-hit ratio, average response time, and
origin traffic (`requested_bytes - hit_bytes`). I grouped runs by workload,
capacity, and policy, verified seeds 0–9 in each group, and recomputed the
arithmetic means and sample standard deviations in `summary.csv`. I also
verified all 40 trace file SHA-256 hashes and request counts against
`config.json`, and checked that the same workload and seed has the same
request count and requested bytes across every policy and capacity. All
checks passed.

As two concrete LFU results at 100 KiB, the 10-seed mean request hit ratio
and response time were 68.63% and 53.58 ms for `repetitive`, versus 7.37%
and 346.41 ms for `sequential`. These are observations for the generated
traces, not general performance claims about LFU.

## Handoff and remaining questions

Run these regression commands from the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 -m experiments.validate_reference
```

On 2026-11-16, all 33 tests passed, and FIFO/LRU/LFU each matched all 10
instructor fields on all 15 reference requests. The three new C tests cover
LFU multi-eviction tie order, frequency reset after reinsertion, and global
versus per-client metrics from a shared-cache hit. The LFU and metrics source
files were not changed. No discrepancy remains in the checks recorded here.
The final choice of experiment snapshot and report interpretation belongs to
team integration. The generated C CSVs, traces, and configuration are ignored
by Git and must be delivered separately from a pull request.
