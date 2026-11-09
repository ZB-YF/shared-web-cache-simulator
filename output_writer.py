"""Deterministic UTF-8 result export, without rounding intermediate metrics."""
import csv
import json
from pathlib import Path

from models import RequestResult

REQUEST_FIELDS = ('step', 'resource_id', 'client_id', 'result', 'evicted',
                  'cache_contents_oldest_first', 'cache_used_KiB', 'response_ms',
                  'cumulative_origin_bytes', 'cumulative_hits', 'timestamp',
                  'size_bytes', 'origin_traffic_bytes', 'cache_used_bytes')


def request_row(result: RequestResult, aliases=None) -> dict:
    aliases = aliases or {}
    def label(key):
        return aliases.get(key, key)
    return dict(step=result.step, resource_id=label(result.request.resource_id),
                client_id=result.request.client_id, result='HIT' if result.hit else 'MISS',
                evicted=','.join(map(label, result.evicted_resources)) or '-',
                cache_contents_oldest_first=','.join(map(label, result.cache_contents_oldest_first)),
                cache_used_KiB=result.cache_used_bytes / 1024,
                response_ms=result.response_time_ms,
                cumulative_origin_bytes=result.cumulative_origin_bytes,
                cumulative_hits=result.cumulative_hits,
                timestamp=result.request.timestamp.isoformat(), size_bytes=result.size_bytes,
                origin_traffic_bytes=result.origin_traffic_bytes, cache_used_bytes=result.cache_used_bytes)


def write_csv(path: Path, rows: list[dict], fields=None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8')


def write_request_results(path: Path, results: list[RequestResult]) -> None:
    write_csv(path, [request_row(result) for result in results], REQUEST_FIELDS)


def write_summary(path: Path, summary: dict, per_client: list[dict], config: dict) -> None:
    """Write all metrics and configuration into the supplied run directory."""
    write_json(path / 'summary.json', summary)
    fields = ['client_id', *summary.keys()]
    write_csv(path / 'per_client.csv', per_client, fields)
    write_json(path / 'config.json', config)
