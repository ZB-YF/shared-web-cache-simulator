"""Compare a fresh LFU-only replay with the published provided-trace matrix."""

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "results/experiments/provided_20261125"


def require(condition, message):
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def csv_rows(path):
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        return reader.fieldnames, list(reader)


def compare_csv(name, keys, expected_count, replay_dir):
    original_fields, original_rows = csv_rows(BASELINE / name)
    replay_fields, replay_rows = csv_rows(replay_dir / name)
    original_lfu = [row for row in original_rows if row["policy"] == "LFU"]
    require(original_fields == replay_fields, f"{name}: columns differ")
    require(len(original_lfu) == len(replay_rows) == expected_count,
            f"{name}: LFU row count differs")
    require(all(row["policy"] == "LFU" for row in replay_rows),
            f"{name}: replay includes another policy")

    def index(rows):
        indexed = {tuple(row[field] for field in keys): row for row in rows}
        require(len(indexed) == len(rows), f"{name}: duplicate keys")
        return indexed

    expected = index(original_lfu)
    observed = index(replay_rows)
    require(expected.keys() == observed.keys(), f"{name}: row keys differ")
    for key, row in expected.items():
        require(row == observed[key], f"{name}: fields differ at {key}")
    digest = hashlib.sha256((replay_dir / name).read_bytes()).hexdigest()
    print(f"PASS {name}: {expected_count}/{expected_count} LFU rows, "
          f"all {len(original_fields)} fields match; replay SHA-256 {digest}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("replay_dir", type=Path, help="LFU-only output directory")
    args = parser.parse_args()
    replay_dir = args.replay_dir

    with (BASELINE / "config.json").open(encoding="utf-8") as stream:
        baseline_config = json.load(stream)
    with (replay_dir / "config.json").open(encoding="utf-8") as stream:
        replay_config = json.load(stream)
    for field in ("resources_sha256", "traces", "capacities_bytes",
                  "workloads", "hit_latency_ms"):
        require(baseline_config[field] == replay_config[field],
                f"config.json: {field} differs")
    # source_hashes() scans every .py file, including this checker once added.
    # Only its new path may be absent from the published experiment snapshot.
    checker_path = "docs/c_lfu_provided_20261125/compare_replay.py"
    baseline_sources = baseline_config["source_sha256"]
    replay_sources = dict(replay_config["source_sha256"])
    added_checker = replay_sources.pop(checker_path, None) is not None
    missing = sorted(baseline_sources.keys() - replay_sources.keys())
    added = sorted(replay_sources.keys() - baseline_sources.keys())
    changed = sorted(path for path in baseline_sources.keys() & replay_sources.keys()
                     if baseline_sources[path] != replay_sources[path])
    require(not (missing or added or changed),
            f"config.json: source_sha256 differs (missing={missing}, "
            f"added={added}, changed={changed})")
    require(replay_config["policies"] == ["LFU"] and replay_config["runs"] == 18,
            "config.json: expected 18 LFU runs")
    print("PASS config.json: resource, three traces, "
          f"all {len(baseline_sources)} original Python source hashes, "
          "capacities, workloads, and hit latency match"
          + (f"; allowed extra checker: {checker_path}" if added_checker else ""))
    print("Python versions: published " + baseline_config["python_version"]
          + "; replay " + replay_config["python_version"])
    compare_csv("runs.csv", ("workload", "capacity_bytes", "policy"), 18,
                replay_dir)
    compare_csv("per_client.csv", ("workload", "capacity_bytes", "policy",
                                   "client_id"), 108, replay_dir)


if __name__ == "__main__":
    main()
