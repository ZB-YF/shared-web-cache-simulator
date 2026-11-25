# Team delivery and maintainer workflow

A is the **sole maintainer of main and the final integrator**. B and C submit code, tests, review notes, and experiment evidence through **GitHub pull requests**. D and E submit design, analysis, and report material through **Google Drive**. A reviews and merges B/C PRs and manually integrates D/E deliveries. Everyone can contribute without directly pushing to main.

## B and C: submit a pull request

1. Update from the latest main before starting. Work on a feature branch or fork; do not push directly to main.
2. Keep the PR focused. Describe the change, affected files, commands run, expected/observed results, and unresolved questions.
3. Run relevant tests and the reference validator before requesting review:

   ```bash
   python3 -m unittest discover -s tests -v
   python3 -m experiments.validate_reference
   ```

4. Attach review evidence as repository files, with clear provenance. B's [PR #1](https://github.com/ZB-YF/shared-web-cache-simulator/pull/1) and C's [PR #2](https://github.com/ZB-YF/shared-web-cache-simulator/pull/2) and [evidence PR #3](https://github.com/ZB-YF/shared-web-cache-simulator/pull/3) are already merged; further work should use a new PR based on current main.
5. For experimental claims, include the original run configuration, source commit or hashes, parameters/seeds, and a reproducible comparison record or checking script. A local path mentioned in prose is not itself a delivered artifact.
6. Generated result directories are ignored unless explicitly allowlisted. If a new result snapshot is needed, add the narrow .gitignore exception and the intended files in the same PR. Check the PR's file list before submission.

If a replay is byte-identical to the published baseline, do not duplicate all trace and CSV bytes merely to prove completion. Supply the original run config and a verifiable comparison record with metric-file checksums, trace checks, and the exact published snapshot referenced. If results differ, preserve the new files and explain the first difference. Do not fabricate missing historical run artifacts or relabel a maintainer's replay as C's independent run.

## D and E: submit through Google Drive

Provide a dated folder such as `d_custom_review_2026-11-22` or `e_report_analysis_2026-11-22` with:

1. The actual design document, corrected pseudocode, analysis, figure source, or report section intended for integration. Keep the original delivered files intact in Drive.
2. A short handoff note listing what changed, which repository documents it affects, and whether it replaces an earlier version.
3. For D, an explicit statement about the implemented rules checked and any disagreement with the code. For E, the selected experiment snapshot/matrix and the exact CSV rows or fields supporting conclusions.
4. Any remaining issue, missing input, and expected next delivery time.

Use English for material intended for the public repository. Private discussion may be in Chinese. A final file/link must be made available to A; a verbal update alone does not establish receipt. The maintainer records delivery status only from accessible materials and does not assume every Drive file has been reviewed.

## Contribution areas and current evidence

| Area | Integration destination | Available evidence and next handoff |
|---|---|---|
| A: core and final integration | cache_simulator/, main.py, documentation | Working implementation; final package and clean-run verification remain |
| B: FIFO/LRU | cache_simulator/policies/; tests/; docs/b_fifo_lru_review.md | PR #1 merged, five focused tests; report explanation and video segment next |
| C: LFU/metrics/experiments | tests/; experiments/; docs/c_lfu_reference_review.md | PR #2 tests/review and PR #3 original configs/replay evidence merged; report methods and video next |
| D: Custom design | docs/custom_policy.md; scenario tests; report | Accepted design and report section retained; video recorded per maintainer's November 25 update; use existing materials for assembly without a new revision or recording request |
| E: methodology and interpretation | reports/; reviewed result snapshot | Final matrix/snapshot choice, CSV-backed conclusions, report draft and selected figures via Drive |

## Maintainer integration checklist

1. Review each PR or preserve and inspect each original Drive delivery. Credit the actual author and distinguish independent review from existing integration work.
2. Compare the change with current interfaces. Merge intentional changes without replacing the whole project with someone else's copy.
3. Keep code in cache_simulator/, inputs in data/, tests in tests/, result snapshots in results/, and report material in reports/.
4. Run relevant checks, preserve historical results, and review Git's file list and diff. An algorithm change requires its affected experiment results to be checked again.
5. For B/C, resolve review issues and merge the tested PR into main. For D/E, integrate the received English material, commit with appropriate attribution, and push as maintainer.
6. Update status documents only for evidence actually received. Keep private planning and unreviewed raw deliveries outside the public repository.

Do not delete original deliveries, edit reported numbers by hand, or claim team sign-off that has not happened. See [development status](development.md) for outstanding work and completion criteria.
