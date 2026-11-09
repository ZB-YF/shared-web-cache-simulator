"""Read and validate local CSV files without fetching resource URLs."""
import csv
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path

from models import Request, Resource


def _rows(path: str | Path, required: set[str]):
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: Missing columns: {', '.join(sorted(missing))}")
        for row in reader:
            line = reader.line_num
            if None in row or any(row.get(key) is None for key in required):
                raise ValueError(f"{path}:{line}: Incorrect CSV column count")
            for key in required:
                if not row[key].strip():
                    raise ValueError(f"{path}:{line}: {key} must not be empty")
            yield line, row


def _resource_id(row: dict[str, str]) -> str:
    # Match identifiers exactly; preserve case, ports, query strings, and slashes.
    scheme, host, path = (row[key].strip() for key in ("scheme", "host", "path"))
    if scheme not in {"http", "https"} or not path.startswith("/"):
        raise ValueError("scheme must be http/https and path must start with /")
    return f"{scheme}://{host}{path}"


def load_resources(path: str | Path) -> dict[str, Resource]:
    required = {"scheme", "host", "path", "status_code", "content_type",
                "size_bytes", "origin_latency_ms", "cache_control"}
    resources = {}
    for line, row in _rows(path, required):
        try:
            key = _resource_id(row)
            size, latency = int(row["size_bytes"]), float(row["origin_latency_ms"])
            status = int(row["status_code"])
            if size < 0 or latency < 0 or not isfinite(latency):
                raise ValueError("Size and latency must be finite and nonnegative; size must be an integer")
            if key in resources:
                raise ValueError(f"Duplicate resource: {key}")
            resources[key] = Resource(key, size, latency, status,
                                      row["content_type"], row["cache_control"])
        except ValueError as exc:
            raise ValueError(f"{path}:{line}: {exc}") from exc
    return resources


def load_requests(path: str | Path, resources: dict[str, Resource]) -> list[Request]:
    requests = []
    required = {"timestamp", "client_id", "method", "scheme", "host", "path"}
    for line, row in _rows(path, required):
        try:
            if row["method"].strip() != "GET":
                raise ValueError("Only GET requests are supported")
            key = _resource_id(row)
            if key not in resources:
                raise ValueError(f"Resource not found in metadata: {key}")
            timestamp = datetime.fromisoformat(row["timestamp"].strip().replace("Z", "+00:00"))
            if timestamp.tzinfo is None:
                raise ValueError("timestamp must include a timezone, such as Z or +08:00")
            requests.append(Request(line, timestamp.astimezone(timezone.utc),
                                    row["client_id"].strip(), key))
        except ValueError as exc:
            raise ValueError(f"{path}:{line}: {exc}") from exc
    # Stable sorting preserves source order for requests with equal timestamps.
    return sorted(requests, key=lambda request: request.timestamp)
