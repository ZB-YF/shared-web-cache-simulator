"""Hand-calculated checks for the additional course performance metrics."""
from datetime import datetime, timedelta, timezone
import csv
import json
from pathlib import Path
import tempfile
import unittest

from cache_simulator.metrics import Statistics
from cache_simulator.models import Request, Resource, SimulationConfig
from cache_simulator.output_writer import write_summary
from cache_simulator.runner import run_simulation


START = datetime(2026, 11, 25, tzinfo=timezone.utc)


def resources(**sizes):
    return {key: Resource(key, size, 20, 200, 'text/plain', 'no-store')
            for key, size in sizes.items()}


def requests(*events):
    return [Request(index + 2, START + timedelta(seconds=index), client, key)
            for index, (client, key) in enumerate(events)]


class RequiredMetricsTests(unittest.TestCase):
    def test_individual_evictions_and_repeated_oversized_requests(self):
        trace = requests(*(('x', key) for key in ('a', 'b', 'c', 'large', 'large', 'c')))
        results, stats = run_simulation(resources(a=4, b=4, c=8, large=11),
                                        trace, 'FIFO', SimulationConfig(10))
        self.assertEqual(results[2].evicted_resources, ('a', 'b'))
        total = stats.summary()
        self.assertEqual(total['cache_evictions'], 2)
        self.assertEqual(total['oversized_resource_requests'], 2)
        # Post-request occupied bytes are 4, 8, 8, 8, 8, 8, including misses
        # for the two oversized requests. Average occupancy is 44 / 60.
        self.assertAlmostEqual(total['average_cache_utilization'], 11 / 15)
        self.assertEqual(total['hits'], 1)
        self.assertEqual(total['requested_bytes'], 46)
        self.assertEqual(total['origin_traffic_bytes'], 38)
        self.assertEqual(total['average_response_time_ms'], 17.5)

    def test_utilization_samples_hits_and_per_client_shared_occupancy(self):
        trace = requests(('x', 'a'), ('y', 'a'), ('y', 'b'), ('y', 'a'))
        _, stats = run_simulation(resources(a=4, b=6), trace, 'LRU', SimulationConfig(10))
        # Shared occupied bytes after each request: 4, 4, 10, 10.
        self.assertAlmostEqual(stats.summary()['average_cache_utilization'], 0.7)
        clients = {row['client_id']: row for row in stats.per_client()}
        self.assertAlmostEqual(clients['x']['average_cache_utilization'], 0.4)
        self.assertAlmostEqual(clients['y']['average_cache_utilization'], 0.8)
        self.assertEqual(clients['y']['hits'], 2)
        self.assertEqual(stats.summary()['cache_evictions'], 0)

    def test_resource_equal_to_total_capacity_is_not_oversized(self):
        _, stats = run_simulation(resources(exact=10), requests(('x', 'exact'), ('x', 'exact')),
                                  'LFU', SimulationConfig(10))
        total = stats.summary()
        self.assertEqual(total['oversized_resource_requests'], 0)
        self.assertEqual(total['cache_evictions'], 0)
        self.assertEqual(total['average_cache_utilization'], 1.0)
        self.assertEqual(total['hits'], 1)

    def test_custom_admission_bypass_is_neither_eviction_nor_oversized(self):
        items = {'hot': Resource('hot', 1, 105, 200, 'text/plain', ''),
                 'cold': Resource('cold', 1, 6, 200, 'text/plain', '')}
        trace = requests(('x', 'hot'), ('y', 'cold'), ('y', 'cold'), ('x', 'hot'))
        results, stats = run_simulation(items, trace, 'CUSTOM', SimulationConfig(1))
        self.assertTrue(all(row.cache_contents_oldest_first == ('hot',) for row in results))
        self.assertEqual(stats.summary()['cache_evictions'], 0)
        self.assertEqual(stats.summary()['oversized_resource_requests'], 0)
        self.assertEqual(stats.summary()['average_cache_utilization'], 1.0)
        self.assertEqual(stats.summary()['hits'], 1)

    def test_empty_and_zero_capacity_conventions(self):
        empty = Statistics().summary()
        self.assertEqual(empty['cache_evictions'], 0)
        self.assertEqual(empty['oversized_resource_requests'], 0)
        self.assertEqual(empty['average_cache_utilization'], 0.0)
        trace = requests(('x', 'a'), ('x', 'zero'), ('x', 'zero'))
        _, stats = run_simulation(resources(a=1, zero=0), trace, 'FIFO', SimulationConfig(0))
        self.assertEqual(stats.summary()['average_cache_utilization'], 0.0)
        self.assertEqual(stats.summary()['oversized_resource_requests'], 1)
        self.assertEqual(stats.summary()['cache_evictions'], 0)
        self.assertEqual(stats.summary()['hits'], 1)
        with self.assertRaises(ValueError):
            Statistics(-1)

    def test_summary_and_client_exports_include_new_fields(self):
        _, stats = run_simulation(resources(a=4), requests(('x', 'a')), 'FIFO', SimulationConfig(10))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            write_summary(output, stats.summary(), stats.per_client(), {'capacity_bytes': 10})
            summary = json.loads((output / 'summary.json').read_text())
            with (output / 'per_client.csv').open(newline='') as stream:
                clients = list(csv.DictReader(stream))
            self.assertEqual(summary['average_cache_utilization'], 0.4)
            self.assertEqual(clients[0]['average_cache_utilization'], '0.4')
            self.assertEqual(clients[0]['cache_evictions'], '0')
            self.assertEqual(clients[0]['oversized_resource_requests'], '0')
            self.assertTrue(all(not key.startswith('_') for key in summary))


if __name__ == '__main__':
    unittest.main()
