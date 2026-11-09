# Input data dictionary

## Resource metadata

`data/resources.csv` contains 21 resources.

| Field | Parsed type | Purpose |
|---|---|---|
| scheme | str | HTTP scheme; part of the resource identifier |
| host | str | Hostname; part of the resource identifier |
| path | str | Preserved path; part of the resource identifier |
| status_code | int | Metadata; status 404 does not change the simplified cacheability rules |
| content_type | str | Metadata for optional analysis |
| size_bytes | Nonnegative int | Cache capacity, traffic, and byte-hit ratio calculations |
| origin_latency_ms | Finite nonnegative float | Response time on a miss, in milliseconds |
| cache_control | str | Preserved but ignored by the simulation |

The internal identifier is `f"{scheme}://{host}{path}"`. The initial implementation uses exact string matching without URL normalization. It does not fetch these URLs.

## Request trace

`data/requests_reference.csv` contains 15 requests from 3 clients, with 5 requests per client and 5 distinct requested resources. The supplied trace is chronological, from `2026-10-26T09:00:00Z` to `09:03:30Z`, at 15-second intervals.

| Field | Parsed type | Purpose |
|---|---|---|
| timestamp | Timezone-aware datetime converted to UTC | Chronological processing by instant |
| client_id | str | Per-client metrics within one shared cache |
| method | str | Must be GET |
| scheme, host, path | str | Construct the identifier, which must exist in the metadata |

`Request.source_row` retains the CSV line number for diagnostics. The simulation `step` is the processing index after sorting, starting at 1. Equal timestamps retain source order as a deterministic implementation convention.

## Reference display aliases

The expected outputs use aliases for five full URLs:

| Alias | URL | Bytes | KiB | Origin latency ms |
|---|---|---:|---:|---:|
| A | https://learn.university.edu/courses/ics/index.html | 32768 | 32 | 125 |
| B | https://learn.university.edu/static/main.css | 43008 | 42 | 90 |
| C | https://learn.university.edu/static/logo.svg | 14336 | 14 | 80 |
| D | https://cdn.university.edu/images/avatar-default.png | 24576 | 24 | 95 |
| E | https://pypi.org/static/css/warehouse.css | 58368 | 57 | 210 |

Aliases are only for reference comparison and display. General simulation code must support all resource URLs. In expected CSV files, `cache_contents_oldest_first` records insertion age, not replacement priority. LRU hits must not reorder that output column.

## Loader validation scope

The loader checks required columns and nonempty fields, row lengths, numeric values, basic identifier structure, duplicate resources, unknown references, GET methods, and timezone-aware timestamps. Input is UTF-8 with optional BOM. Empty datasets are accepted when the required header is present. This is a loader for the project's supplied schema, not a general HTTP or URL normalization library.
