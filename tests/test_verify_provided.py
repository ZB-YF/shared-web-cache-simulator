"""Checks that the independent audit detects corrupted experiment results."""
from contextlib import redirect_stdout
import csv
from datetime import datetime, timedelta, timezone
import io
from pathlib import Path
import tempfile
import unittest

from cache_simulator.models import Request, RequestResult
from experiments.provided import run_experiments
from experiments.verify_provided import independent_metrics, verify


class ProvidedVerificationTests(unittest.TestCase):
    def test_independent_formulas_count_resources_and_every_occupancy_sample(self):
        start = datetime(2026, 11, 25, tzinfo=timezone.utc)
        events = [
            RequestResult(1, Request(2, start, 'a', 'small'), 4, False, 20, 4,
                          (), ('small',), 4, 4, 0),
            RequestResult(2, Request(3, start + timedelta(seconds=1), 'a', 'large'),
                          11, False, 40, 11, (), ('small',), 4, 15, 0),
            RequestResult(3, Request(4, start + timedelta(seconds=2), 'b', 'new'),
                          8, False, 60, 8, ('small', 'other'), ('new',), 8, 23, 0),
            RequestResult(4, Request(5, start + timedelta(seconds=3), 'b', 'new'),
                          8, True, 5, 0, (), ('new',), 8, 23, 1),
        ]
        metrics = independent_metrics(events, 10)
        self.assertEqual(metrics['cache_evictions'], 2)
        self.assertEqual(metrics['oversized_resource_requests'], 1)
        self.assertEqual(metrics['average_cache_utilization'], 0.6)
        self.assertEqual(metrics['hit_ratio'], 0.25)
        self.assertEqual(metrics['byte_hit_ratio'], 8 / 31)
        self.assertEqual(metrics['origin_traffic_bytes'], 23)
        self.assertEqual(metrics['average_response_time_ms'], 31.25)
        self.assertEqual(independent_metrics([], 0)['average_cache_utilization'], 0)

    def test_complete_audit_and_detection_of_corrupted_metric(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            resources_path = root / 'resources.csv'
            resources_path.write_text(
                'scheme,host,path,status_code,content_type,size_bytes,origin_latency_ms,cache_control\n'
                'https,example.test,/a,200,text/plain,4,20,no-store\n', encoding='utf-8')
            for workload in ('sequential', 'repetitive', 'mixed'):
                (root / f'requests_{workload}.csv').write_text(
                    'timestamp,client_id,method,scheme,host,path\n'
                    '2026-11-25T00:00:00Z,x,GET,https,example.test,/a\n'
                    '2026-11-25T00:00:01Z,y,GET,https,example.test,/a\n', encoding='utf-8')
            output = root / 'results'
            with redirect_stdout(io.StringIO()):
                run_experiments(resources_path, root, output)
            report = verify(output, resources_path, root, allow_source_drift=True)
            self.assertEqual(report['matrix_cells'], 72)
            self.assertEqual(report['per_client_rows'], 144)
            self.assertEqual(report['request_events_checked'], 144)
            path = output / 'runs.csv'
            with path.open(newline='') as stream:
                reader = csv.DictReader(stream)
                fields, rows = reader.fieldnames, list(reader)
            rows[0]['cache_evictions'] = '1'
            with path.open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)
            with self.assertRaisesRegex(ValueError, 'cache_evictions'):
                verify(output, resources_path, root, allow_source_drift=True)


if __name__ == '__main__':
    unittest.main()
