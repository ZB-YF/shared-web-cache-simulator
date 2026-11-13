# Team delivery and maintainer workflow

This repository has **one GitHub maintainer**. Other team members submit their work through **Google Drive**. The maintainer manually reviews, integrates, verifies, commits, and pushes approved changes. Contributors do not need GitHub write access, branches, or pull requests.

## Submit through Google Drive

For each delivery, provide a clearly named folder such as `b_fifo_lru_2026-11-16` containing:

1. Your source files, documents, figures, or review notes. Keep the original delivered files intact in Drive.
2. A short handoff note explaining what changed, which repository files it affects, and whether it replaces an earlier delivery.
3. Reproduction commands and expected results for executable work, including input files, capacities, seeds, and dependencies when relevant.
4. Test or manual-check evidence and any unresolved questions.

Use English for material intended for the public repository. Personal notes may stay in private working material. Avoid including Python caches, editor settings, credentials, or unrelated downloads in a delivery.

## Where each contribution belongs

| Area | Integration destination | Review focus |
|---|---|---|
| A: simulator core and final integration | cache_simulator/, main.py, docs/usage.md | Input paths, shared cache, CLI, result export |
| B: FIFO/LRU and reference checks | cache_simulator/policies/fifo.py, lru.py; tests/ | Insertion vs access order; per-request expected fields |
| C: LFU, statistics, experiments, Custom integration | cache_simulator/policies/, metrics.py; experiments/ | LFU reset/ties, formulas, seed/config consistency |
| D: Custom design and test expectations | docs/custom_policy.md; experiments/scenarios.py; tests/ | Prototype/pseudocode consistency, admission, tie-breaking |
| E: methodology, interpretation, report figures | reports/; docs/development.md | Workload validity, CSV-backed claims, per-client trade-offs |

Paths in the table are repository-relative. The current implementation is a working integration baseline; its existence does not imply approval of each member's independently delivered work.

## Maintainer integration checklist

1. Preserve the original Google Drive delivery and record its contributor, date, and files in private integration notes. Public raw-delivery archives are not required.
2. Compare the delivery with the current module and documented interfaces. Integrate only intentional changes; do not replace the entire repository with a contributor's copy.
3. Keep source code in cache_simulator/, input datasets in data/, tests in tests/, result snapshots in results/, and report material in reports/.
4. Run the relevant checks, with the existing baseline commands:

   ```bash
   python3 -m unittest discover -s tests -v
   python3 -m experiments.validate_reference
   ```

5. For experiment changes, save the exact parameters, seeds, input traces, hashes, and both per-seed and aggregate metrics. Use a new output directory; do not overwrite a historical result snapshot.
6. Review `.gitignore` and `git status` so the intended CSVs, configs, and figures are actually included. The current baseline directories are allowlisted; new review-approved snapshots need an explicit allowlist entry.
7. Inspect `git diff`, update the affected documentation, then commit and push as the sole maintainer. Mention the contributor and integration scope in the commit message when appropriate.

Do not delete original deliveries, change reported numbers by hand, or claim independent review that has not occurred. Team algorithm and final-report decisions remain listed in [development status](development.md).
