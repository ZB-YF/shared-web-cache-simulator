"""Independent reference, infrastructure, lifecycle, and metrics checks."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from cache import Cache
from data_loader import load_requests, load_resources
from experiments.scenarios import EXPECTED, scenarios
from experiments.validate_reference import validate
from experiments.workloads import generate, write_trace
from metrics import Statistics
from models import Request, Resource, SimulationConfig
from output_writer import write_request_results, write_summary
from policies import create_policy
from runner import run_simulation
from simulator import Simulator

ROOT = Path(__file__).resolve().parents[1]
START = datetime(2026, 10, 26, tzinfo=timezone.utc)


def resource(key, size=1, latency=15):
    return Resource(key, size, latency, 200, 'text/plain', 'no-store')


def trace(*keys):
    return [Request(i + 2, START + timedelta(seconds=i), 'client', key) for i, key in enumerate(keys)]


class SimulationTests(unittest.TestCase):
    def test_all_reference_fields(self):
        self.assertEqual([r['hits'] for r in validate()], [3, 3, 4])

    def test_custom_reference(self):
        resources = load_resources(ROOT / 'data/resources.csv')
        requests = load_requests(ROOT / 'data/requests_reference.csv', resources)
        results, stats = run_simulation(resources, requests, 'CUSTOM')
        self.assertEqual(''.join('H' if r.hit else 'M' for r in results), 'MMMHHMHHMHMHMHM')
        self.assertEqual(stats.summary()['origin_traffic_bytes'], 299008)
        self.assertAlmostEqual(stats.summary()['average_response_time_ms'], 68 + 2 / 3)
        self.assertFalse(results[5].evicted_resources)
        self.assertFalse(results[8].evicted_resources)

    def test_d_frozen_scenarios_and_capacity(self):
        resources = load_resources(ROOT / 'data/resources.csv')
        for name, requests in scenarios(resources).items():
            with self.subTest(scenario=name):
                results, _ = run_simulation(resources, requests, 'CUSTOM')
                if name in EXPECTED:
                    self.assertEqual(''.join('H' if r.hit else 'M' for r in results), EXPECTED[name])
                for result in results:
                    self.assertGreaterEqual(result.cache_used_bytes, 0)
                    self.assertLessEqual(result.cache_used_bytes, 102400)
                    self.assertEqual(result.cache_used_bytes,
                                     sum(resources[key].size_bytes for key in result.cache_contents_oldest_first))

    def test_shared_cache_and_independent_metrics(self):
        requests = trace('a', 'b', 'a')
        requests[2] = Request(4, requests[2].timestamp, 'other-client', 'a')
        results, stats = run_simulation({'a': resource('a', 10, 20), 'b': resource('b', 20, 40)},
                                        requests, 'FIFO', SimulationConfig(30))
        total = stats.summary()
        self.assertEqual([r.response_time_ms for r in results], [20, 40, 5])
        self.assertEqual([r.origin_traffic_bytes for r in results], [10, 20, 0])
        self.assertAlmostEqual(total['hit_ratio'], 1 / 3)
        self.assertEqual(total['byte_hit_ratio'], 0.25)
        self.assertAlmostEqual(total['average_response_time_ms'], 65 / 3)
        self.assertEqual(total['origin_traffic_bytes'], 30)
        clients = {r['client_id']: r for r in stats.per_client()}
        self.assertEqual(clients['other-client']['hit_ratio'], 1)
        self.assertEqual(clients['other-client']['average_response_time_ms'], 5)

    def test_oversized_does_not_evict_or_change_inflation(self):
        policy = create_policy('CUSTOM')
        cache = Cache(10, policy)
        sim = Simulator({'a': resource('a', 10), 'b': resource('b', 11)}, cache, SimulationConfig(10))
        results = sim.run(trace('a', 'b', 'b', 'a'))
        self.assertEqual([r.hit for r in results], [False, False, False, True])
        self.assertTrue(all(r.cache_contents_oldest_first == ('a',) for r in results))
        self.assertEqual(policy.frequency['b'], 2)
        self.assertEqual(policy.inflation, 0)

    def test_capacity_edges_and_zero_size(self):
        for policy in ('FIFO', 'LRU', 'LFU', 'CUSTOM'):
            for capacity in (0, 9, 10, 11):
                with self.subTest(policy=policy, capacity=capacity):
                    results, _ = run_simulation({'a': resource('a', 10)}, trace('a', 'a'),
                                                policy, SimulationConfig(capacity))
                    self.assertEqual(results[1].hit, capacity >= 10)
            results, stats = run_simulation({'z': resource('z', 0, 0)}, trace('z', 'z'),
                                            policy, SimulationConfig(0))
            self.assertTrue(results[1].hit)
            self.assertEqual(stats.summary()['byte_hit_ratio'], 0)

    def test_multiple_evictions_and_duplicate_admission(self):
        resources = {key: resource(key, size) for key, size in [('a', 4), ('b', 4), ('c', 8)]}
        cache = Cache(10, create_policy('FIFO'))
        sim = Simulator(resources, cache, SimulationConfig(10))
        results = sim.run(trace('a', 'b', 'c'))
        self.assertEqual(results[-1].evicted_resources, ('a', 'b'))
        self.assertEqual(cache.used_bytes, 8)
        with self.assertRaises(ValueError):
            cache.admit(resources['c'], trace('c')[0], 4)
        cache.remove('c')
        self.assertEqual(cache.used_bytes, 0)

    def test_invalid_victim_and_read_only_preview(self):
        policy = create_policy('FIFO')
        cache = Cache(1, policy)
        cache.admit(resource('a'), trace('a')[0], 1)
        policy.choose_victim = lambda items: 'missing'
        with self.assertRaises(ValueError):
            cache.admit(resource('b'), trace('b')[0], 2)
        self.assertEqual(cache.snapshot(), ('a',))
        def mutate(items):
            items.pop('a')
        policy.choose_victim = mutate
        with self.assertRaises(AttributeError):
            cache.admit(resource('b'), trace('b')[0], 2)
        self.assertEqual(cache.used_bytes, 1)

    def test_lfu_tie_break_and_reset(self):
        policy = create_policy('LFU')
        cache = Cache(2, policy)
        resources = {key: resource(key) for key in 'abc'}
        results = Simulator(resources, cache, SimulationConfig(2)).run(trace('a', 'b', 'a', 'b', 'c', 'a'))
        self.assertEqual(results[4].evicted_resources, ('a',))
        self.assertEqual(results[5].evicted_resources, ('c',))
        self.assertEqual(policy.frequency['a'], 1)

    def test_custom_tie_and_admission_equality(self):
        policy = create_policy('CUSTOM')
        resources = {key: resource(key, 1024, 15) for key in 'abc'}
        results = Simulator(resources, Cache(2048, policy), SimulationConfig(2048)).run(trace('a', 'b', 'c'))
        self.assertEqual(results[-1].evicted_resources, ('a',))
        self.assertEqual(results[-1].cache_contents_oldest_first, ('b', 'c'))
        # Insertion uses inflation after eviction: 10 + 10, not pre-eviction 0 + 10.
        self.assertEqual(policy.priority['c'], 20)
        self.assertEqual(policy.inflation, 10)

    def test_custom_bypass_keeps_state_and_counts_misses(self):
        policy = create_policy('CUSTOM')
        resources = {'a': resource('a', 1, 105), 'b': resource('b', 1, 6)}
        results = Simulator(resources, Cache(1, policy), SimulationConfig(1)).run(trace('a', 'b', 'b', 'a'))
        self.assertEqual(results[1].cache_contents_oldest_first, ('a',))
        self.assertEqual(results[2].cache_contents_oldest_first, ('a',))
        self.assertEqual(policy.frequency['b'], 2)
        self.assertEqual(policy.inflation, 0)

    def test_nondefault_hit_latency_used_by_custom_score(self):
        policy = create_policy('CUSTOM', 20)
        r = resource('a', 1024, 30)
        Simulator({'a': r}, Cache(1024, policy), SimulationConfig(1024, 20)).run(trace('a'))
        self.assertEqual(policy.priority['a'], 10)

    def test_single_use_sort_and_config_guard(self):
        sim = Simulator({'a': resource('a')}, Cache(1, create_policy('FIFO')), SimulationConfig(1))
        requests = trace('a', 'a')
        results = sim.run(requests[::-1])
        self.assertEqual([r.request for r in results], requests)
        with self.assertRaises(ValueError):
            sim.run(requests)
        with self.assertRaises(ValueError):
            Simulator({}, Cache(1, create_policy('FIFO')), SimulationConfig(2))

    def test_empty_run_and_exports(self):
        results, stats = run_simulation({}, [], 'CUSTOM', SimulationConfig(0))
        self.assertEqual(stats.summary()['request_count'], 0)
        self.assertEqual(stats.summary()['average_response_time_ms'], 0)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            write_request_results(path / 'requests.csv', results)
            write_summary(path, stats.summary(), stats.per_client(), {'policy': 'CUSTOM'})
            self.assertEqual(len((path / 'requests.csv').read_text().splitlines()), 1)
            self.assertEqual(len((path / 'per_client.csv').read_text().splitlines()), 1)

    def test_reproducible_workloads_and_csv_roundtrip(self):
        resources = load_resources(ROOT / 'data/resources.csv')
        first = generate(resources, 'mixed', 7)
        self.assertEqual(first, generate(resources, 'mixed', 7))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'trace.csv'
            write_trace(path, first)
            self.assertEqual(load_requests(path, resources), first)
        for policy in ('FIFO', 'LRU', 'LFU', 'CUSTOM', 'CUSTOM_NOADM'):
            a, stats_a = run_simulation(resources, first, policy)
            b, stats_b = run_simulation(resources, first, policy)
            self.assertEqual(a, b)
            self.assertEqual(stats_a.summary(), stats_b.summary())
            self.assertEqual(stats_a.summary()['origin_traffic_bytes'],
                             stats_a.summary()['requested_bytes'] - stats_a.summary()['hit_bytes'])


if __name__ == '__main__':
    unittest.main()
