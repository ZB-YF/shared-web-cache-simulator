"""Behavioral tests for the shared-cache FIFO and LRU policies."""
from datetime import datetime, timedelta, timezone
import unittest

from cache_simulator.models import Request, Resource, SimulationConfig
from cache_simulator.runner import run_simulation


START = datetime(2026, 10, 26, tzinfo=timezone.utc)


def resources(**sizes):
    return {
        key: Resource(key, size, 100, 200, 'text/plain', 'no-store')
        for key, size in sizes.items()
    }


def requests(*events):
    """Events are (client, resource); timestamps preserve their given order."""
    return [
        Request(index + 2, START + timedelta(seconds=index), client, key)
        for index, (client, key) in enumerate(events)
    ]


class FifoLruTests(unittest.TestCase):
    def test_hit_changes_lru_victim_but_not_fifo_victim(self):
        trace = requests(('x', 'a'), ('x', 'b'), ('x', 'a'), ('x', 'c'))
        for policy, victim in [('FIFO', 'a'), ('LRU', 'b')]:
            with self.subTest(policy=policy):
                results, _ = run_simulation(resources(a=1, b=1, c=1), trace,
                                            policy, SimulationConfig(2))
                self.assertEqual([row.hit for row in results], [False, False, True, False])
                self.assertEqual(results[-1].evicted_resources, (victim,))
                self.assertEqual(results[-1].cache_used_bytes, 2)

    def test_multiple_evictions_follow_each_policy_order(self):
        trace = requests(('x', 'a'), ('x', 'b'), ('x', 'c'), ('x', 'a'), ('x', 'd'))
        for policy, victims in [('FIFO', ('a', 'b', 'c')), ('LRU', ('b', 'c', 'a'))]:
            with self.subTest(policy=policy):
                results, _ = run_simulation(resources(a=3, b=3, c=3, d=7), trace,
                                            policy, SimulationConfig(9))
                self.assertEqual(results[-1].evicted_resources, victims)
                self.assertEqual(results[-1].cache_contents_oldest_first, ('d',))
                self.assertEqual(results[-1].cache_used_bytes, 7)

    def test_eviction_and_reinsertion_create_new_policy_state(self):
        trace = requests(('x', 'a'), ('x', 'b'), ('x', 'c'),
                         ('x', 'a'), ('x', 'c'), ('x', 'd'))
        for policy, final_victim in [('FIFO', 'c'), ('LRU', 'a')]:
            with self.subTest(policy=policy):
                results, _ = run_simulation(resources(a=1, b=1, c=1, d=1), trace,
                                            policy, SimulationConfig(2))
                self.assertEqual(results[2].evicted_resources, ('a',))
                self.assertFalse(results[3].hit)
                self.assertEqual(results[3].evicted_resources, ('b',))
                self.assertTrue(results[4].hit)
                self.assertEqual(results[5].evicted_resources, (final_victim,))

    def test_oversized_misses_do_not_evict_existing_resources(self):
        trace = requests(('x', 'a'), ('x', 'b'), ('x', 'big'), ('x', 'big'), ('x', 'a'))
        for policy in ('FIFO', 'LRU'):
            with self.subTest(policy=policy):
                results, stats = run_simulation(resources(a=4, b=4, big=9), trace,
                                                policy, SimulationConfig(8))
                for result in results[2:4]:
                    self.assertFalse(result.hit)
                    self.assertEqual(result.evicted_resources, ())
                    self.assertEqual(result.cache_contents_oldest_first, ('a', 'b'))
                    self.assertEqual(result.cache_used_bytes, 8)
                    self.assertEqual(result.origin_traffic_bytes, 9)
                self.assertTrue(results[-1].hit)
                self.assertEqual(stats.summary()['origin_traffic_bytes'], 26)

    def test_clients_share_cache_and_lru_access_history(self):
        trace = requests(('client-1', 'a'), ('client-1', 'b'),
                         ('client-2', 'a'), ('client-1', 'c'))
        for policy, victim in [('FIFO', 'a'), ('LRU', 'b')]:
            with self.subTest(policy=policy):
                results, stats = run_simulation(resources(a=1, b=1, c=1), trace,
                                                policy, SimulationConfig(2))
                self.assertTrue(results[2].hit)
                self.assertEqual(results[-1].evicted_resources, (victim,))
                clients = {row['client_id']: row for row in stats.per_client()}
                self.assertEqual(clients['client-2']['hit_ratio'], 1)
                self.assertEqual(clients['client-2']['average_response_time_ms'], 5)


if __name__ == '__main__':
    unittest.main()
