# Team delivery and maintainer workflow

A is the **sole maintainer of main, final integrator, and author of the final 3–4 page report**. B and C submit code, tests, review notes, and experiment evidence through **GitHub pull requests**. D and E submit design and data-analysis material through **Google Drive**. E's analysis is source material for A's report. A reviews and merges B/C PRs and manually integrates D/E deliveries.

## B and C: submit a pull request

1. Update from the latest main before starting. Work on a feature branch or fork; do not push directly to main.
2. Keep the PR focused. Describe the change, affected files, commands run, expected/observed results, and unresolved questions.
3. Run relevant tests and the reference validator before requesting review:

   ```bash
   python3 -m unittest discover -s tests -v
   python3 -m experiments.validate_reference
   ```

4. Attach review evidence as repository files, with clear provenance. B's [PR #1](https://github.com/ZB-YF/shared-web-cache-simulator/pull/1) and C's [PR #2](https://github.com/ZB-YF/shared-web-cache-simulator/pull/2), [#3](https://github.com/ZB-YF/shared-web-cache-simulator/pull/3), and [#4](https://github.com/ZB-YF/shared-web-cache-simulator/pull/4) are merged; further work should use a new PR based on current main.
5. For experimental claims, include the original run configuration, source commit or hashes, parameters/seeds, and a reproducible comparison record or checking script. A local path mentioned in prose is not itself a delivered artifact.
6. Ad hoc runs under `results/` are ignored. Published required results are selected under `evaluation/`; extra synthetic evidence is under `supplementary/synthetic/`. Check the PR's file list and include only intended, reviewed artifacts.

If a replay is byte-identical to the published baseline, do not duplicate all trace and CSV bytes merely to prove completion. Supply the original run config and a verifiable comparison record with metric-file checksums, trace checks, and the exact published snapshot referenced. If results differ, preserve the new files and explain the first difference. Do not fabricate missing historical run artifacts or relabel a maintainer's replay as C's independent run.

## D and E: submit through Google Drive

Provide a clearly versioned handoff with:

1. The actual design document, corrected pseudocode, analysis, figure source, or report section intended for integration. Keep the original delivered files intact in Drive.
2. A short handoff note listing what changed, which repository documents it affects, and whether it replaces an earlier version.
3. For D, an explicit statement about the implemented rules checked and any disagreement with the code. For E, the selected experiment snapshot/matrix and the exact CSV rows or fields supporting conclusions.
4. Any unresolved issue or missing input.

Use English for material intended for the public repository. Private discussion may be in Chinese. A final file/link must be made available to A; a verbal update alone does not establish receipt. The maintainer records delivery status only from accessible materials and does not assume every Drive file has been reviewed.

## Contribution areas and current evidence

| Area | Integration destination | Accepted contribution |
|---|---|---|
| A: core and final integration | cache_simulator/, main.py, evaluation/, documentation | Simulator, integration, reproducible evaluation, and final report authorship |
| B: FIFO/LRU | tests/; docs/b_fifo_lru_review.md | PR #1 review, reference comparison, and five tests |
| C: LFU/metrics/experiments | tests/; docs/c_lfu_reference_review.md | PR #2 tests/review, PR #3 historical configs, and PR #4 provided-trace LFU analysis/replay evidence |
| D: Custom design | docs/custom_policy.md; scenario tests; report source material | Accepted design/prototype and existing recorded presentation segment |
| E: data analysis | Private analysis used with evaluation/ CSVs and figures | Delivered workload/capacity/client interpretation via Drive; A incorporates it into the final report |

## Maintainer integration checklist

1. Review each PR or preserve and inspect each original Drive delivery. Credit the actual author and distinguish independent review from existing integration work.
2. Compare the change with current interfaces. Merge intentional changes without replacing the whole project with someone else's copy.
3. Keep code in `cache_simulator/`, inputs in `data/`, tests in `tests/`, required published results in `evaluation/`, extra synthetic evidence in `supplementary/synthetic/`, and design material in `reports/`. Use ignored `results/` directories for new local runs.
4. Run relevant checks, preserve historical results, and review Git's file list and diff. An algorithm change requires its affected experiment results to be checked again.
5. For B/C, resolve review issues and merge the tested PR into main. For D/E, integrate the received English material, commit with appropriate attribution, and push as maintainer.
6. Update status documents only for evidence actually received. Keep private planning and unreviewed raw deliveries outside the public repository.

Do not delete original deliveries, edit reported numbers by hand, or claim team sign-off that has not happened. The integrated report and presentation drafts remain private. See [implementation and contribution status](development.md).
