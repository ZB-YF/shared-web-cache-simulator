# Usage

## Validate the supplied input

From the repository root:

```bash
python3 main.py --validate-only
python3 -m unittest discover -s tests -v
```

Default input paths are resolved relative to `main.py`, so they also work when the script is invoked from another working directory. No package installation is currently required.

To validate specific inputs and configuration:

```bash
python3 main.py --validate-only --resources data/resources.csv --requests data/requests_reference.csv --policy LFU --capacity 102400 --hit-latency-ms 5
```

`--capacity` is measured in bytes: 100 KiB = 102400 bytes. Policy names are case-insensitive and must be FIFO, LRU, LFU, or CUSTOM. The current CLI validates and displays these parameters but does not instantiate a policy. `--output-dir` is reserved for future result export and currently creates no output.

Successful validation exits with status 0. Invalid input or configuration exits with status 2. Requesting simulation without `--validate-only` also exits with status 2 and explicitly reports that simulation is not implemented.

## Planned simulation commands

The following commands describe the intended interface. They **do not run a simulation in the current scaffold**:

```bash
python3 main.py --policy FIFO --capacity 102400 --output-dir results/reference/FIFO_102400
python3 main.py --policy LRU --capacity 102400 --output-dir results/reference/LRU_102400
python3 main.py --policy LFU --capacity 102400 --output-dir results/reference/LFU_102400
```

Each completed run is intended to produce `requests.csv`, `summary.json`, `per_client.csv`, and `config.json`. A batch runner remains to be implemented. Every run must create fresh cache, policy, and statistics objects.

## Input format and troubleshooting

Use the original CSV schemas described in the [data dictionary](docs/DATA_DICTIONARY.md). Resources are identified by `scheme + "://" + host + path`; reference aliases A-E must not replace those fields. Timestamps must include a timezone, such as `2026-10-26T09:00:00Z`. Equal timestamps retain source-file order.

The loader rejects missing columns or fields, malformed row lengths, invalid numeric values, duplicate resources, unknown resource references, non-GET requests, and timestamps without timezones. Diagnostics identify the file and source line where applicable.

The simulation specification treats all resources as cacheable, including metadata containing `private, no-store` or status 404. Cache-Control and expiration are ignored. Resource URLs are never fetched.

If a file cannot be found, check the input path. A `NotImplementedError` or abstract-class instantiation error indicates an unfinished component. See the [development roadmap](docs/DEVELOPMENT.md) for implementation order.
