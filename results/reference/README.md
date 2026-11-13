# Reference trace runs

All four snapshots use the instructor input trace, cache capacity 102400 bytes, and hit latency 5 ms. Each directory contains requests.csv, summary.json, per_client.csv, and the original config.json.

| Policy | Snapshot | Hits | Average response ms | Origin bytes |
|---|---|---:|---:|---:|
| FIFO | [fifo_102400/](fifo_102400/) | 3 | 95.333333... | 421888 |
| LRU | [lru_102400/](lru_102400/) | 3 | 92.333333... | 403456 |
| LFU | [lfu_102400/](lfu_102400/) | 4 | 84.333333... | 370688 |
| Custom | [custom_102400/](custom_102400/) | 7 | 68.666666... | 299008 |

The standard policies match the instructor's expected CSVs. The Custom result is a regression target from D's delivered prototype, not an instructor-provided Custom answer. Directory names were normalized to lowercase; output contents and historical source hashes were not rewritten.
