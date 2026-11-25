# Program test and run verification report

Checked on November 25, 2026. This report records maintainer verification of the simulator and its exported results. It is supporting evidence for the team; it does not replace contributor explanations, E's report analysis, the integrated four-page report, or presentation contributions.

## Recorded checks

| Check | Scope | Outcome |
|---|---|---|
| Automated tests | 35 existing checks, six required-metric checks, five fixed-input experiment checks and two independent-audit checks | 48 passed |
| Instructor reference comparison | FIFO, LRU and LFU; each compared on 15 requests and all ten expected fields | All match |
| Required experiment coverage | Three supplied traces, six capacities and four policies | 72 unique cells |
| Client coverage | Six clients per trace for every experiment cell | 432 rows checked |
| Independent event accounting | Cache occupancy, origin traffic, latency and oversized handling | 216000 request events checked |
| Independently calculated metrics | Global and client counts, ratios, latency, traffic, evictions and mean utilization | 6552 values match |
| Input and source provenance | Supplied resource/trace hashes and the exact public Python source snapshot | Match |
| D prototype comparison | Hit/miss, client/resource, ordered evictions and occupied bytes | 72 runs and 216000 events match |

The [captured command output](../docs/run_evidence_20261125/checks.txt) and [execution metadata](../docs/run_evidence_20261125/checks.json) record the actual test commands, return codes, Python version, UTC check time, source commit and log checksum. The source commit identifies the tested code; this publication adds documentation and evidence without changing Python sources.

The [strict matrix review](../docs/provided_run_review.json) includes exact input and result hashes. The separate [D prototype review](../docs/provided_proto_review.json) identifies the received prototype by SHA256. The prototype comparison and historical synthetic regression were performed during the earlier November 25 integration; the captured command log records the fresh public-source checks.

## Metric definitions verified

Evictions count individual resources removed, including all victims when one insertion needs several removals. Oversized requests compare resource size with total capacity using a strict greater-than test. Average utilization averages occupied bytes divided by capacity after every request, including hits and bypassed misses. CSV ratios use 0-1 values.

Global additive counters equal the sum of client counters. Global hit ratio, latency and observed utilization use request-weighted client averages; byte-hit ratio uses requested-byte weights. Per-client utilization observes the shared cache after that client's requests and does not imply private allocation.

The audit derives metrics directly from immutable request results without calling `Statistics`. It checks exported calculations and per-event invariants using the existing simulator. D's separately received prototype provides an additional comparison of cache behavior; these checks do not establish correctness for every possible future trace.

## Reproduction

Run from the project root:

```bash
python3 -m unittest discover -s tests -v
python3 -m experiments.validate_reference
python3 -m experiments.verify_provided --results-dir results/experiments/provided_20261125
```

To create a fresh result snapshot, choose a new output directory:

```bash
python3 -m experiments.provided --output-dir results/my_provided_matrix
python3 -m experiments.verify_provided --results-dir results/my_provided_matrix
```

The fixed traces are deterministic, so repeated-run seed averaging is unnecessary. Config timestamps can change on a fresh run; the metric CSVs are reproducible for the same code and inputs. Source changes intentionally cause strict historical-snapshot verification to fail unless drift is explicitly allowed and recorded.

The earlier 1000-run synthetic baseline was also checked during integration: all historical run fields, all 40 traces and both aggregate CSVs match. Original inputs, replacement algorithms and historical published outputs were preserved. See [validation history](../docs/validation.md) for the scope and historical checkpoints, [run notes](provided_experimental_findings.md) for numeric observations, and [HOWTO](../HOWTO.md) for setup.

## Publication and team handoff

Program outputs, test evidence, generated figures and supporting run notes are public. The integrated four-page report and video/presentation drafts remain in the maintainer's private project folder until contributor materials are collected. E still owns final result interpretation, figure selection and report analysis/conclusions; B/C supply their own explanations and checks. D's already recorded segment and accepted design are retained without a new recording request.
