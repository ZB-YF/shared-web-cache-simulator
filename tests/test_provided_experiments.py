"""Coverage and independent arithmetic checks for fixed instructor-trace runs."""
from contextlib import redirect_stdout
import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from cache_simulator.data_loader import load_requests, load_resources
from cache_simulator.models import Request
from experiments.provided import CAPACITIES, POLICIES, ROOT, WORKLOADS, characterize, run_experiments


def write_csv(path, fields, rows):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def fixture(directory):
    root = Path(directory)
    resource_path = root / 'resources.csv'
    fields = ('scheme', 'host', 'path', 'status_code', 'content_type',
              'size_bytes', 'origin_latency_ms', 'cache_control')
    write_csv(resource_path, fields, [
        dict(scheme='https', host='example.test', path='/' + key, status_code=200,
             content_type='text/plain', size_bytes=size, origin_latency_ms=20,
             cache_control='no-store')
        for key, size in [('a', 2), ('b', 3), ('c', 10), ('d', 0), ('e', 1), ('f', 4)]])
    trace_fields = ('timestamp', 'client_id', 'method', 'scheme', 'host', 'path')
    events = dict(sequential=[('x', 'a'), ('y', 'b'), ('y', 'a'), ('x', 'c')],
                  repetitive=[('x', 'a'), ('x', 'a'), ('x', 'b')],
                  mixed=[('y', 'b'), ('x', 'c'), ('x', 'a')])
    for workload, requests in events.items():
        write_csv(root / f'requests_{workload}.csv', trace_fields, [
            dict(timestamp=f'2026-11-25T00:00:{index:02d}Z', client_id=client,
                 method='GET', scheme='https', host='example.test', path='/' + key)
            for index, (client, key) in enumerate(requests)])
    return resource_path, root


def rows(path):
    with path.open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))


class ProvidedExperimentTests(unittest.TestCase):
    def test_full_matrix_has_exactly_72_distinct_cells(self):
        with tempfile.TemporaryDirectory() as directory:
            resources, inputs = fixture(directory)
            output = inputs / 'matrix'
            with redirect_stdout(io.StringIO()):
                config = run_experiments(resources, inputs, output)
            actual = rows(output / 'runs.csv')
            expected = {(workload, capacity, policy) for workload in WORKLOADS
                        for capacity in CAPACITIES for policy in POLICIES}
            self.assertEqual(len(actual), 72)
            self.assertEqual({(row['workload'], int(row['capacity_bytes']), row['policy'])
                              for row in actual}, expected)
            self.assertEqual(config['runs'], 72)
            self.assertEqual(config['hit_latency_ms'], 5)
            self.assertIn('no seed averaging', config['aggregation'])
            self.assertEqual(config['resources_file'], 'resources.csv')
            self.assertNotIn(directory, json.dumps(config))
            self.assertFalse((output / 'requests').exists())
            clients = rows(output / 'per_client.csv')
            self.assertEqual(len(clients), 120)  # (2 + 1 + 2) clients * 6 capacities * 4 policies

    def test_characterization_and_new_metrics_match_hand_calculation(self):
        with tempfile.TemporaryDirectory() as directory:
            resources, inputs = fixture(directory)
            output = inputs / 'small'
            with redirect_stdout(io.StringIO()):
                run_experiments(resources, inputs, output, capacities=(5,), policies=('FIFO',))
            summaries = {row['workload']: row for row in rows(output / 'characterization/summary.csv')}
            sequential = summaries['sequential']
            self.assertEqual(int(sequential['request_count']), 4)
            self.assertEqual(int(sequential['distinct_resources']), 3)
            self.assertEqual(int(sequential['distinct_clients']), 2)
            self.assertEqual(int(sequential['requested_bytes']), 17)
            self.assertEqual(int(sequential['requested_working_set_bytes']), 15)
            popularity = [row for row in rows(output / 'characterization/resource_popularity.csv')
                          if row['workload'] == 'sequential']
            self.assertEqual([row['resource_id'] for row in popularity],
                             ['https://example.test/a', 'https://example.test/b', 'https://example.test/c'])
            self.assertEqual(float(popularity[0]['request_share']), 0.5)
            self.assertEqual(int(popularity[0]['requested_bytes']), 4)
            self.assertEqual(int(rows(output / 'characterization/oversized_requests.csv')[0]
                                 ['oversized_resource_requests']), 1)
            result = next(row for row in rows(output / 'runs.csv') if row['workload'] == 'sequential')
            self.assertEqual(int(result['cache_evictions']), 0)
            self.assertEqual(int(result['oversized_resource_requests']), 1)
            self.assertAlmostEqual(float(result['average_cache_utilization']), 17 / 20)
            self.assertEqual(float(result['hit_ratio']), 1 / 4)
            self.assertEqual(int(result['origin_traffic_bytes']), 15)

    def test_characterize_only_never_runs_policies_and_limits_top_five(self):
        with tempfile.TemporaryDirectory() as directory:
            resources_path, inputs = fixture(directory)
            output = inputs / 'analysis'
            config = run_experiments(resources_path, inputs, output, characterize_only=True)
            self.assertEqual(config['runs'], 0)
            self.assertTrue(config['characterize_only'])
            self.assertFalse((output / 'runs.csv').exists())
            hypotheses = (output / 'characterization/hypotheses.md').read_text()
            self.assertIn('before this invocation executes any policy simulation', hypotheses)
            self.assertIn('not a preregistered study', hypotheses)
            self.assertIn(config['started_at_utc'], hypotheses)
            resources = load_resources(resources_path)
            trace = load_requests(inputs / 'requests_sequential.csv', resources)
            # Six different resources with equal popularity: the URL is the tie breaker.
            six = [Request(i + 2, trace[0].timestamp, 'x', key)
                   for i, key in enumerate(reversed(list(resources)))]
            analysis = characterize(resources, {'six': six}, (2, 3, 10))
            self.assertEqual(len(analysis['resource_popularity']), 6)
            self.assertEqual([row['resource_id'] for row in analysis['top_five']], sorted(resources)[:5])
            self.assertEqual([row['oversized_resource_requests']
                              for row in analysis['oversized_requests']], [3, 2, 0])

    def test_invalid_or_missing_inputs_do_not_create_output(self):
        with tempfile.TemporaryDirectory() as directory:
            resources, inputs = fixture(directory)
            for capacities, policies in [((0,), ('FIFO',)), ((-1,), ('FIFO',)),
                                         ((5, 5), ('FIFO',)), ((5,), ('FIFO', 'fifo')),
                                         ((5,), ('UNKNOWN',))]:
                with self.subTest(capacities=capacities, policies=policies):
                    output = inputs / 'invalid'
                    with self.assertRaises(ValueError):
                        run_experiments(resources, inputs, output, capacities, policies)
                    self.assertFalse(output.exists())
            missing = inputs / 'requests_mixed.csv'
            missing.rename(inputs / 'mixed_saved.csv')
            with self.assertRaises(FileNotFoundError):
                run_experiments(resources, inputs, inputs / 'missing')
            self.assertFalse((inputs / 'missing').exists())
            missing.write_text('timestamp,client_id,method,scheme,host,path\n'
                               '2026-11-25T00:00:00Z,x,GET,https,example.test,/unknown\n')
            with self.assertRaisesRegex(ValueError, 'Resource not found'):
                run_experiments(resources, inputs, inputs / 'unknown')
            self.assertFalse((inputs / 'unknown').exists())

    def test_cli_is_portable_exports_optional_logs_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            resources, inputs = fixture(directory)
            output = inputs / 'cli'
            # Running as a module from repo is documented; supplying the repository
            # through PYTHONPATH also permits module invocation from any directory.
            env = dict(os.environ, PYTHONPATH=str(ROOT))
            command = [sys.executable, '-m', 'experiments.provided', '--resources', str(resources),
                       '--requests-dir', str(inputs), '--output-dir', str(output),
                       '--capacities', '5', '--policies', 'FIFO', '--request-logs']
            first = subprocess.run(command, cwd=directory, env=env, text=True, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(len(rows(output / 'requests/sequential_fifo_5.csv')), 4)
            before = (output / 'runs.csv').read_bytes()
            second = subprocess.run(command, cwd=directory, env=env, text=True, capture_output=True)
            self.assertEqual(second.returncode, 2)
            self.assertIn('not empty', second.stderr)
            self.assertEqual((output / 'runs.csv').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
