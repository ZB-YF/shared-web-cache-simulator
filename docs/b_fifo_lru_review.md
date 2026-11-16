# B delivery: FIFO and LRU, rounds 1–2

This note records B's review of the integrated baseline and its reference-trace
verification. The existing FIFO and LRU modules already implement the requested
rules; this delivery retains them and adds focused tests rather than replacing
another contributor's work. The trace below was reconstructed for this review
and checked against the instructor's answer key and expected CSVs; it should not
be represented as a student's unaided handwritten work.

## Rules and implementation

Both policies share a single byte-limited cache across clients. A hit returns the
cached resource without reinsertion. On a fitting miss, the cache plans and
commits as many evictions as needed before inserting. An oversized resource is
served from origin but neither inserted nor allowed to evict cached items. The
reference starts empty at 102,400 bytes, uses 5 ms per hit and the resource's
origin latency per miss, ignores expiration and Cache-Control, and admits every
fitting miss.

- **FIFO:** evict the item inserted earliest among current residents. Hits leave
  insertion order unchanged. `FIFOPolicy.choose_victim` selects the first key in
  the cache's insertion-ordered mapping; no policy metadata is needed. A resource
  inserted again after eviction is a new, newest insertion.
- **LRU:** evict the resident with the earliest last access. On both insertion
  and hit, `LRUPolicy` records the monotonically increasing request step; on
  removal it deletes that metadata. A hit changes eviction priority but does not
  change the cache's insertion-order snapshot.

Both operate through `ReplacementPolicy` and `Cache`; they inherit the default
admission decision of `True`. The cache previews victims using the supplied
candidate subset, then commits removals. Neither standard policy mutates the
cache during preview. This preserves the separate custom-policy admission flow.
See [interfaces.md](interfaces.md) for the full integration contract.

## Reference trace, request by request

Resource aliases follow the instructor key: A = index.html (32 KiB), B =
main.css (42 KiB), C = logo.svg (14 KiB), D = avatar (24 KiB), and E =
warehouse.css (57 KiB). `H` means hit, `M` means miss, `–` means no eviction.
Cache contents are listed oldest **insertion** first, as in the instructor CSV;
they are not necessarily the order in which LRU would evict items.

| Step | Client | Resource | FIFO H/M | FIFO evicted | FIFO cache | LRU H/M | LRU evicted | LRU cache |
|---:|---|---|---|---|---|---|---|---|
| 1 | 01 | A | M | – | A | M | – | A |
| 2 | 02 | B | M | – | A,B | M | – | A,B |
| 3 | 03 | C | M | – | A,B,C | M | – | A,B,C |
| 4 | 01 | A | H | – | A,B,C | H | – | A,B,C |
| 5 | 02 | B | H | – | A,B,C | H | – | A,B,C |
| 6 | 03 | D | M | A | B,C,D | M | C | A,B,D |
| 7 | 01 | A | M | B | C,D,A | H | – | A,B,D |
| 8 | 02 | C | H | – | C,D,A | M | B | A,D,C |
| 9 | 03 | E | M | C,D | A,E | M | D,A | C,E |
| 10 | 01 | B | M | A | E,B | M | C | E,B |
| 11 | 02 | D | M | E | B,D | M | E | B,D |
| 12 | 03 | A | M | – | B,D,A | M | – | B,D,A |
| 13 | 01 | E | M | B,D | A,E | M | B,D | A,E |
| 14 | 02 | C | M | A | E,C | M | A | E,C |
| 15 | 03 | B | M | E | C,B | M | E | C,B |

At step 6, A is the oldest insertion, so FIFO evicts A. LRU instead evicts C:
A and B were accessed at steps 4 and 5. At step 9, E needs more space than one
victim releases in each policy, so two evictions are required. These examples
show why a hit updates LRU priority but not FIFO insertion order.

## Results and verification

| Metric | FIFO | LRU |
|---|---:|---:|
| Requests / hits / misses | 15 / 3 / 12 | 15 / 3 / 12 |
| Hit ratio | 20.00% | 20.00% |
| Hit bytes / requested bytes | 90,112 / 512,000 | 108,544 / 512,000 |
| Byte-hit ratio | 17.60% | 21.20% |
| Origin traffic | 421,888 bytes (412 KiB) | 403,456 bytes (394 KiB) |
| Mean response | 95.33 ms | 92.33 ms |

Both have three hits here, but LRU's hits include more bytes and avoid more
origin latency. This is one short correctness fixture, not evidence that LRU
always outperforms FIFO. Per-client hit ratios / mean response are respectively
FIFO: student-01 20% / 111 ms, student-02 40% / 55 ms, student-03 0% / 120 ms;
LRU: student-01 40% / 87 ms, student-02 20% / 70 ms, student-03 0% / 120 ms.

Run from the repository root with Python 3.10+:

```sh
python3 -m experiments.validate_reference
python3 -m unittest discover -s tests -v
python3 main.py --policy FIFO --capacity 102400 --output-dir /tmp/cache-b-fifo
python3 main.py --policy LRU --capacity 102400 --output-dir /tmp/cache-b-lru
```

Use fresh output directories; the CLI deliberately refuses to overwrite a
nonempty directory. The reference validator reads the instructor inputs and
compares all 10 expected fields for all 15 requests, including ordered evictions,
insertion-order contents, occupancy, response time and cumulative counters.
The CLI runs also exercise input loading, policy selection, simulation and
`requests.csv`, `summary.json`, `per_client.csv` and `config.json` export.
`tests/test_fifo_lru.py` adds focused cases for behavior that is easy to regress.
The instructor data in `data/reference/` is left unchanged.
