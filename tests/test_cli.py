"""CLI integration checks for portable paths and protection of existing results."""
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CommandLineTests(unittest.TestCase):
    def test_run_from_another_directory_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'run'
            command = [sys.executable, str(ROOT / 'main.py'), '--policy', 'custom',
                       '--output-dir', str(output)]
            first = subprocess.run(command, cwd=directory, text=True, capture_output=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            summary_path = output / 'summary.json'
            content = summary_path.read_bytes()
            self.assertEqual(json.loads(content)['hits'], 7)
            with (output / 'requests.csv').open(newline='') as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 15)
            self.assertTrue(rows[0]['resource_id'].startswith('https://'))
            second = subprocess.run(command, cwd=directory, text=True, capture_output=True)
            self.assertEqual(second.returncode, 2)
            self.assertEqual(summary_path.read_bytes(), content)
            self.assertIn('not empty', second.stderr)

    def test_invalid_capacity_produces_no_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'invalid'
            completed = subprocess.run([sys.executable, str(ROOT / 'main.py'), '--capacity', '-1',
                                        '--output-dir', str(output)], text=True, capture_output=True)
            self.assertEqual(completed.returncode, 2)
            self.assertFalse(output.exists())

    def test_small_batch_writes_replayable_inputs_and_seed_metrics(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'matrix'
            completed = subprocess.run(
                [sys.executable, '-m', 'experiments.run', '--output-dir', str(output),
                 '--workloads', 'mixed', '--capacities', '102400',
                 '--policies', 'LRU', 'CUSTOM', '--seeds', '0', '1'],
                cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            config = json.loads((output / 'config.json').read_text())
            self.assertEqual(config['runs'], 4)
            self.assertEqual(len(config['traces']), 2)
            with (output / 'runs.csv').open(newline='') as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 4)
            self.assertTrue(all(int(row['request_count']) == 1200 for row in rows))
            replay = subprocess.run([sys.executable, str(ROOT / 'main.py'), '--policy', 'CUSTOM',
                                     '--requests', str(output / 'traces/mixed_seed0.csv'),
                                     '--output-dir', str(Path(directory) / 'replay')],
                                    cwd=directory, text=True, capture_output=True)
            self.assertEqual(replay.returncode, 0, replay.stderr)
            summary = json.loads((Path(directory) / 'replay/summary.json').read_text())
            row = next(r for r in rows if r['policy'] == 'CUSTOM' and r['seed'] == '0')
            self.assertEqual(summary['origin_traffic_bytes'], int(row['origin_traffic_bytes']))
            self.assertEqual(summary['average_response_time_ms'], float(row['average_response_time_ms']))


if __name__ == '__main__':
    unittest.main()
