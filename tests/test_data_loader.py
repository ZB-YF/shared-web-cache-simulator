"""Input-layer tests, independent of policy behavior."""
import csv
from pathlib import Path
import tempfile
import unittest

from cache_simulator.data_loader import load_requests, load_resources

DATA = Path(__file__).resolve().parents[1] / "data/reference"


class LoaderTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.resources = load_resources(DATA / "resources.csv")

    def copy_csv(self, name, change):
        with (DATA / name).open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        rows = change(rows)
        path = Path(self.directory.name) / name
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_supplied_data_and_url_identity(self):
        requests = load_requests(DATA / "requests_reference.csv", self.resources)
        self.assertEqual(len(self.resources), 21)
        self.assertEqual(len(requests), 15)
        self.assertEqual(len({r.client_id for r in requests}), 3)
        self.assertEqual(len({r.resource_id for r in requests}), 5)
        self.assertEqual(self.resources[requests[0].resource_id].size_bytes, 32768)
        # The assignment treats private/no-store and 404 resources as cacheable.
        self.assertTrue(any(r.status_code == 404 for r in self.resources.values()))
        self.assertTrue(any("no-store" in r.cache_control for r in self.resources.values()))

    def test_sort_by_instant_and_preserve_equal_time_order(self):
        def change(rows):
            rows = rows[:3]
            rows[0]["timestamp"] = "2026-10-26T09:01:00Z"
            rows[1]["timestamp"] = "2026-10-26T17:00:00+08:00"
            rows[2]["timestamp"] = "2026-10-26T09:00:00Z"
            return rows
        path = self.copy_csv("requests_reference.csv", change)
        requests = load_requests(path, self.resources)
        self.assertEqual([r.source_row for r in requests], [3, 4, 2])

    def test_unknown_resource_reports_source_row(self):
        def change(rows):
            rows[0]["path"] = "/unknown-resource"
            return rows
        path = self.copy_csv("requests_reference.csv", change)
        with self.assertRaisesRegex(ValueError, r":2:.*Resource not found in metadata"):
            load_requests(path, self.resources)

    def test_duplicate_resources_rejected(self):
        path = self.copy_csv("resources.csv", lambda rows: rows + [rows[0]])
        with self.assertRaisesRegex(ValueError, "Duplicate resource"):
            load_resources(path)

    def test_invalid_resource_numbers(self):
        for field, value in [("size_bytes", "-1"), ("origin_latency_ms", "NaN"),
                             ("origin_latency_ms", "inf"), ("size_bytes", "1.5")]:
            with self.subTest(field=field, value=value):
                def change(rows):
                    rows[0][field] = value
                    return rows
                path = self.copy_csv("resources.csv", change)
                with self.assertRaises(ValueError):
                    load_resources(path)

    def test_non_get_and_naive_timestamp_rejected(self):
        for field, value in [("method", "POST"), ("timestamp", "2026-10-26T09:00:00")]:
            with self.subTest(field=field):
                def change(rows):
                    rows[0][field] = value
                    return rows
                path = self.copy_csv("requests_reference.csv", change)
                with self.assertRaises(ValueError):
                    load_requests(path, self.resources)

    def test_missing_columns(self):
        path = Path(self.directory.name) / "missing.csv"
        path.write_text("timestamp,client_id\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Missing columns"):
            load_requests(path, self.resources)


if __name__ == "__main__":
    unittest.main()
