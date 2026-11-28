# Verification after relocation

The required CSVs and figures were moved without rerunning or editing the published results.

| Evidence | Scope |
|---|---|
| [reorganization_review.json](reorganization_review.json) | Fresh independent accounting: 72 cells, 432 client rows, 216000 request events and 6552 matching metrics |
| [layout_checks.json](layout_checks.json) | Migration SHA256 preservation, unchanged original Python sources and current Markdown links |

The post-move automated suite passed **48/48** tests, and FIFO/LRU/LFU each matched all ten reference fields for 15 requests. C's relocated-baseline checker also passed a fresh LFU-only replay: **18 global rows and 108 client rows**, with all fields matching the published CSVs.

All 33 source files recorded by the original formal matrix retain their hashes. The audit explicitly records the additional `docs/c_lfu_provided_20261125/compare_replay.py`; only that helper's baseline path changed. Historical configurations and older audits remain unchanged under their original evidence names. See the [migration guide](../../docs/repository_layout.md) and [test report](../test_report.md).
