# Simulation requirements

This document records the technical simulation rules and validation targets. Module names, Python APIs, directory structure, and implementation-specific edge-case conventions are project design choices rather than assignment requirements.

## Simulation rules

1. Replay local HTTP request traces without implementing a real proxy or establishing network connections.
2. Use one shared cache for all clients. Start each run empty and process requests sequentially in chronological order.
3. Resources remain unchanged. All requests are cacheable GET requests. Ignore expiration and Cache-Control directives, including `private` and `no-store`.
4. Cache capacity is configurable. The reference trace uses **100 KiB = 102400 bytes** and a **5 ms** cache-hit latency.
5. A hit generates no origin traffic. A miss uses the resource's supplied origin latency, without adding the hit latency, and generates traffic equal to its size in bytes.
6. A resource larger than total capacity is never stored. Its request still completes as a miss, without evicting cached resources.
7. On an admissible miss, evict as many resources as necessary before insertion. Admission is mandatory for individually fitting resources in the reference exercise.
8. Use the same input, capacity, hit latency, and initial state for fair policy comparisons.

## Replacement policies

- **FIFO:** Evict the oldest insertion. Hits do not change insertion order.
- **LRU:** Evict the resource whose last access is oldest.
- **LFU:** Count accesses since insertion. Evict the lowest frequency, breaking ties by LRU. Reset frequency after eviction and reinsertion.
- **Custom:** Define, implement, justify, and evaluate an additional strategy. Document its objective, tie-breaking, limitations, and trade-offs. It need not outperform every baseline under every workload. The integrated LA-GDSF design includes a documented admission filter; standard policies retain mandatory admission for fitting misses. Team review of the Custom interpretation remains outstanding.

## Performance metrics

| Metric | Definition |
|---|---|
| Cache-hit ratio | Hit requests divided by all requests |
| Byte-hit ratio | Bytes requested on hits divided by bytes requested on all requests |
| Average response time | Sum of request response times divided by request count |
| Origin traffic | Sum of resource sizes for miss requests |
| Per-client performance | At least hit ratio and average response time for each client |

The implemented internal ratio representation is 0-1, converted to percentages for display. For empty request sets or zero-byte denominators, the implemented convention is 0 with request counts retained. These boundary conventions require contributor agreement.

## Reference targets

Use the [answer key](../data/reference/reference_trace_answer_key.md) and the three expected CSV files for per-request validation.

| Policy | Hits | Misses | Hit ratio | Origin bytes | Origin KiB | Average response ms |
|---|---:|---:|---:|---:|---:|---:|
| FIFO | 3 | 12 | 20% | 421888 | 412 | 95.333333... |
| LRU | 3 | 12 | 20% | 403456 | 394 | 92.333333... |
| LFU | 4 | 11 | 26.666667% | 370688 | 362 | 84.333333... |

These supplied standard-policy reference targets have been reproduced by the integrated implementation. Compare individual requests, including eviction order and cache insertion order, before relying on summary totals. Validate byte-hit ratio and per-client metrics independently because they are not separate columns in the expected files.

## Evaluation scope

Compare all four policies using at least repetitive, sequential, and mixed workloads across multiple capacities. Analyze workload sensitivity, capacity effects, client fairness, and custom-policy trade-offs. Present comparative figures and explain observed behavior.

Project deliverables include reproducible source code and run instructions, experimental data and graphs, a 3-4 page technical report, and a demonstration video. For the current five-person team, the video is 10 minutes with participation from every member. The completion milestone for all deliverables is **November 25, 2026**.
