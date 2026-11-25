# Preliminary hypotheses from workload characterization

Generated at 2026-11-25T07:00:54.256449+00:00 from the supplied input files, before this invocation executes any policy simulation. This is an input-analysis record, not a preregistered study or evidence that earlier results were unseen.

These expectations must be checked against the exported results. Popularity alone does not describe temporal locality or guarantee a policy ranking.

## Sequential

The trace contains 3000 requests from 6 clients for 21 resources. The five most requested resources account for 24.60% of requests. Distinct requested resources total 110490624 bytes; repeated requests total 15836925952 bytes.

If requests are spread across resources with limited short-term reuse, all policies should have fewer opportunities to exploit a stable hot set. FIFO and LRU may perform similarly; LFU needs repeat accesses before its frequency information can help.

For every workload, increasing capacity may change both the fitting working set and which requests are oversized. This can change policy rankings; monotonic improvement for every policy is not assumed.

| Capacity bytes | Oversized requests |
|---:|---:|
| 102400 | 1431 |
| 512000 | 716 |
| 1048576 | 570 |
| 2097152 | 424 |
| 5242880 | 288 |
| 10485760 | 288 |

Oversized requests cannot become hits under any policy at that capacity. Compare their request share and byte volume when interpreting the gap between request-hit and byte-hit ratios.

## Repetitive

The trace contains 3000 requests from 6 clients for 21 resources. The five most requested resources account for 87.97% of requests. Distinct requested resources total 110490624 bytes; repeated requests total 4380107776 bytes.

If the popular working set fits in the cache, repeated requests should produce more hits. LFU may protect frequently accessed resources, while LRU benefits when repetition is recent. LA-GDSF may reduce latency by retaining resources with high saved retrieval cost per byte.

For every workload, increasing capacity may change both the fitting working set and which requests are oversized. This can change policy rankings; monotonic improvement for every policy is not assumed.

| Capacity bytes | Oversized requests |
|---:|---:|
| 102400 | 1492 |
| 512000 | 784 |
| 1048576 | 750 |
| 2097152 | 730 |
| 5242880 | 50 |
| 10485760 | 50 |

Oversized requests cannot become hits under any policy at that capacity. Compare their request share and byte volume when interpreting the gap between request-hit and byte-hit ratios.

## Mixed

The trace contains 3000 requests from 6 clients for 21 resources. The five most requested resources account for 30.10% of requests. Distinct requested resources total 110490624 bytes; repeated requests total 14038665216 bytes.

Heterogeneous resource sizes and client requests may separate request-hit ratio, byte-hit ratio, response time, and client experience. LA-GDSF may improve latency through small costly resources while sacrificing hits or bytes for a client requesting larger resources.

For every workload, increasing capacity may change both the fitting working set and which requests are oversized. This can change policy rankings; monotonic improvement for every policy is not assumed.

| Capacity bytes | Oversized requests |
|---:|---:|
| 102400 | 1370 |
| 512000 | 730 |
| 1048576 | 560 |
| 2097152 | 393 |
| 5242880 | 234 |
| 10485760 | 234 |

Oversized requests cannot become hits under any policy at that capacity. Compare their request share and byte volume when interpreting the gap between request-hit and byte-hit ratios.

## Evaluation plan

Compare FIFO, LRU, LFU, and CUSTOM on the same fixed traces, metadata, capacities, and 5 ms hit latency. Evaluate policy differences at 5242880 bytes (5 MiB), compare capacity curves, and inspect individual clients on the mixed trace at 5 MiB. Use all required metrics, including individual resource evictions, oversized requests, and mean post-request cache utilization.

Selected capacities in bytes: 102400, 512000, 1048576, 2097152, 5242880, 10485760.
