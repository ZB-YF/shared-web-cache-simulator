# Simulation and evaluation requirements

Updated November 25, 2026 against the revised assignment. This page distinguishes assignment requirements from project choices. The old synthetic experiment snapshot remains supplementary evidence; the required evaluation uses the three provided workloads.

## Simulation rules

1. Replay local HTTP request traces through one shared cache, without network requests or a real proxy.
2. Start every run empty. Process requests sequentially in chronological order; preserve source order for equal timestamps.
3. Resources remain unchanged. All requests are cacheable GET requests. Ignore expiration and Cache-Control, including `private` and `no-store`.
4. Use **100 KiB = 102400 bytes** for reference validation and **5 MiB = 5242880 bytes** for the fixed-capacity policy and client comparisons. Hit latency is **5 ms**.
5. A hit generates no origin traffic. A miss uses the supplied origin latency, without adding hit latency, and generates traffic equal to the requested resource size.
6. Resources larger than total cache capacity are never stored and do not trigger evictions. Resources exactly equal to capacity fit.
7. On an admitted miss, evict as many resources as necessary before insertion. Standard policies admit every resource that individually fits; Custom's additional admission rule is documented explicitly.
8. Allow resource metadata, request trace, policy, and capacity to be specified as inputs. Use the same `resources.csv`, fixed trace, capacity, hit latency, and empty initial state for fair comparisons.

## Replacement policies

- **FIFO:** Evict the oldest insertion. Hits do not change insertion order.
- **LRU:** Evict the resource whose most recent access is oldest.
- **LFU:** Initialize frequency to 1 on insertion and increment on cache hits. Evict minimum frequency, breaking ties by LRU. Reset to 1 after eviction and reinsertion. The existing implementation already follows the clarified rule.
- **Custom:** Define and evaluate another strategy, with its objective, parameters, tie-breaking, admission rules, limitations, and trade-offs. It need not beat every baseline. The integrated LA-GDSF policy uses lifetime request frequency, retrieval cost, size, aging, and an admission filter; see the maintained [specification](custom_policy.md). The November 25 requirements update does not change its algorithm.

## Required measurements

| Metric | Definition |
|---|---|
| Cache-hit ratio | Hit requests divided by all requests |
| Byte-hit ratio | Bytes requested on hits divided by all requested bytes |
| Average response time | Sum of response times divided by request count |
| Origin-server traffic | Sum of resource sizes on cache misses |
| Per-client performance | At least hit ratio and average response time for each client |
| Cache evictions | Total number of resources removed to admit new resources, including every victim in a multiple-eviction request |
| Oversized resource requests | Count of requests whose resource is larger than total cache capacity, including repeated requests |
| Average cache utilization | Mean of `cache_used_bytes / capacity_bytes` after each request, including hits and bypasses |

Ratios, including `average_cache_utilization`, are exported as 0-1 and displayed as percentages. Empty request sets, zero-byte denominators, and zero-capacity utilization use 0 with request counts retained. These are project boundary conventions. Client utilization, where exported, describes shared-cache occupancy observed after that client's requests; it is not a private allocation to that client.

## Workload characterization before performance experiments

Analyze `requests_sequential.csv`, `requests_repetitive.csv`, and `requests_mixed.csv` with the same [resource metadata](../data/reference/resources.csv). For each trace report total requests, distinct requested resources, distinct clients, the request distribution across resources, the five most requested resources, total requested bytes, and requests for resources larger than the selected capacity. Oversized counts must identify their capacity; the official pipeline records all six capacities.

Plot the differences and formulate performance hypotheses from these observations before running policy comparisons. Additional synthetic workloads are allowed as supplements. The generated `hypotheses.md` records preliminary expectations, not a claim of independent preregistration or evidence that a policy must win.

## Required experiment matrix

Run **3 provided workloads × 6 capacities × 4 primary policies = 72 deterministic combinations**. The chosen capacities are:

| Capacity | Bytes |
|---|---:|
| 100 KiB | 102400 |
| 500 KiB | 512000 |
| 1 MiB | 1048576 |
| 2 MiB | 2097152 |
| 5 MiB | 5242880 |
| 10 MiB | 10485760 |

The assignment gives five example capacities but explicitly requires six in its deliverables. The team adds 2 MiB and records all values in bytes; 2 MiB is a project choice. Each fixed trace is reused unchanged across policies and capacities. These deterministic runs need no random seeds or artificial repeated-run error bars.

The matrix supports the three required experiments: compare policies on all workloads at **5 MiB**; investigate capacity effects across all six capacities; and compare individual clients on **mixed at 5 MiB**. Those are views of the same matrix, not three unrelated datasets. Structured CSV results and the experiment scripts must be included.

## Reference validation

Use the [answer key](../data/reference/reference_trace_answer_key.md) and original expected CSVs to compare every request, including victim order and insertion-order display.

| Policy | Hits | Misses | Origin bytes | Average response ms |
|---|---:|---:|---:|---:|
| FIFO | 3 | 12 | 421888 | 95.333333... |
| LRU | 3 | 12 | 403456 | 92.333333... |
| LFU | 4 | 11 | 370688 | 84.333333... |

All 15 requests and all ten supplied columns match the integrated standard policies. Custom's reference result comes from D's design, not an instructor Custom answer. The revised assignment keeps this reference configuration unchanged.

## Report, video, and submission

Submit one reproducible ZIP through Brightspace containing source, run/build instructions, README/HOWTO, input data, experiment scripts, structured results, graphs, and a **3-4 page technical report**. The five-person team must provide a **10-minute video**, approximately two minutes per member, with every member presenting their contribution. Upload it to YouTube (Unlisted is allowed) and submit its link on Brightspace.

Although the revised text still says “three central questions,” it lists five. Cover all five in the report and video:

1. Which policy performs best, according to which metric?
2. How do workload characteristics influence policy performance?
3. How does increasing capacity affect the relative performance of policies?
4. Do global improvements benefit all clients equally?
5. What trade-offs does the custom policy introduce?

Grading remains correctness 30%, performance/experiments 20%, Custom design 20%, analysis/visualization 20%, and code/documentation 10%. The official deadline is **December 4, 2026 at 17:59 Shanghai time**. See [implementation and contribution status](development.md) for the published evidence. E supplies data analysis, and A authors and integrates the final report.
