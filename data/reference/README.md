# Instructor reference dataset

| File | Purpose |
|---|---|
| resources.csv | 21 resource URLs with sizes, latencies, and preserved HTTP metadata |
| requests_reference.csv | 15 requests from 3 clients, referring to 5 resources |
| expected_fifo.csv | Per-request expected FIFO behavior |
| expected_lru.csv | Per-request expected LRU behavior |
| expected_lfu.csv | Per-request expected LFU behavior |
| reference_trace_answer_key.md | Assumptions, URL aliases A-E, expected steps, summary targets |

The original input and answer contents have not been changed. Reference runs use 102400 bytes of cache and a 5 ms hit latency. Full URLs are internal identifiers; A-E are display aliases for comparison.

Run `python3 -m experiments.validate_reference` from the repository root to compare all three standard policies against all ten expected columns. Actual simulator outputs are kept separately in [results/reference/](../../results/reference/).
