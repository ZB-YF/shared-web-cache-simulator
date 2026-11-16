"""Focused LFU lifecycle and shared-cache metric checks for C's review."""
from datetime import datetime, timedelta, timezone
import unittest

from cache_simulator.models import Request, Resource, SimulationConfig
from cache_simulator.runner import run_simulation


START = datetime(2026, 10, 26, tzinfo=timezone.utc)


def resources(**sizes):
    return {
        key: Resource(key, size, 20 if key == 'a' else 40,
                      200, 'text/plain', 'no-store')
        for key, size in sizes.items()
    }


def requests(*events):
    return [
        Request(index + 2, START + timedelta(seconds=index), client, key)
        for index, (client, key) in enumerate(events)
    ]


class LfuMetricsTests(unittest.TestCase):
    def test_multiple_evictions_recheck_frequency_then_lru_tie(self):
        trace = requests(('x', 'a'), ('x', 'b'), ('x', 'c'),
                         ('x', 'c'), ('x', 'a'), ('x', 'd'))
        results, _ = run_simulation(resources(a=1, b=1, c=1, d=2),
                                    trace, 'LFU', SimulationConfig(3))
        # b has frequency 1. Then a and c tie at 2; c was accessed earlier.
        self.assertEqual(results[-1].evicted_resources, ('b', 'c'))
        self.assertEqual(results[-1].cache_contents_oldest_first, ('a', 'd'))
        self.assertEqual(results[-1].cache_used_bytes, 3)

    def test_reinsertion_resets_old_frequency(self):
        trace = requests(('x', 'a'), ('x', 'b'), ('x', 'a'),
                         ('x', 'b'), ('x', 'a'), ('x', 'c'),
                         ('x', 'b'), ('x', 'd'))
        results, _ = run_simulation(resources(a=1, b=1, c=1, d=1),
                                    trace, 'LFU', SimulationConfig(2))
        self.assertEqual(results[5].evicted_resources, ('b',))
        self.assertEqual(results[6].evicted_resources, ('c',))
        # Reinserted b has frequency 1, so d evicts b rather than a (frequency 3).
        self.assertEqual(results[7].evicted_resources, ('b',))
        self.assertEqual(results[7].cache_contents_oldest_first, ('a', 'd'))

    def test_shared_hit_and_per_client_denominators(self):
        trace = requests(('client-1', 'a'), ('client-2', 'a'),
                         ('client-2', 'b'))
        results, stats = run_simulation(resources(a=2, b=4), trace,
                                        'LFU', SimulationConfig(6))
        self.assertEqual([r.hit for r in results], [False, True, False])
        total = stats.summary()
        self.assertEqual((total['request_count'], total['hits'], total['misses']),
                         (3, 1, 2))
        self.assertEqual((total['requested_bytes'], total['hit_bytes'],
                          total['origin_traffic_bytes']), (8, 2, 6))
        self.assertEqual(total['total_response_time_ms'], 65)
        self.assertAlmostEqual(total['hit_ratio'], 1 / 3)
        self.assertAlmostEqual(total['byte_hit_ratio'], 1 / 4)
        self.assertAlmostEqual(total['average_response_time_ms'], 65 / 3)
        clients = {row['client_id']: row for row in stats.per_client()}
        self.assertEqual((clients['client-1']['request_count'],
                          clients['client-1']['hits']), (1, 0))
        self.assertEqual((clients['client-2']['request_count'],
                          clients['client-2']['hits']), (2, 1))
        self.assertAlmostEqual(clients['client-2']['hit_ratio'], 1 / 2)
        self.assertAlmostEqual(clients['client-2']['byte_hit_ratio'], 1 / 3)
        self.assertAlmostEqual(clients['client-2']['average_response_time_ms'], 45 / 2)
        self.assertEqual(clients['client-2']['origin_traffic_bytes'], 4)


if __name__ == '__main__':
    unittest.main()
