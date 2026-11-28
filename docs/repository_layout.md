# Repository layout and preserved provenance

The revised-assignment evaluation is the main experiment, so its results and figures are grouped in the root-level [evaluation/](../evaluation/) directory. Additional seeded experiments are grouped under [supplementary/synthetic/](../supplementary/synthetic/). Names describe purpose rather than an execution date.

| Previous path | Current path |
|---|---|
| `results/experiments/provided_20261125/` | `evaluation/` |
| `reports/figures/provided_20261125/` | `evaluation/figures/` |
| `reports/provided_experimental_findings.md` | `evaluation/findings.md` |
| `reports/test_report_20261125.md` | `evaluation/test_report.md` |
| `results/experiments/README.md` | `evaluation/README.md` |
| `results/experiments/d_reproduction/` | `supplementary/synthetic/` |
| Four synthetic PNG/SVG pairs under `reports/figures/` | `supplementary/synthetic/figures/` |
| `reports/experimental_findings.md` | `supplementary/synthetic/findings.md` |

The [migration manifest](layout_migration.json) records each moved file, its previous and current path, and its original SHA256. Markdown navigation and explanatory text were updated; result CSVs, original configurations, generated traces and images retain their original bytes. Input datasets and simulation algorithms were not changed. No original contribution was discarded.

`results/` remains the home for local reruns and preserved reference-validation outputs. New experiment commands use fresh directories there so the published evidence is not overwritten. `reports/` contains reusable architecture and Custom design explanations; final integrated report and video drafts remain in the maintainer's private folder. E provides data analysis; A writes the integrated report.

## Historical paths are intentional in evidence

Saved `config.json` files, original contributor configurations, old audit JSONs, captured command logs and the [earlier reorganization manifest](reorganization_manifest.json) describe actual past executions. They retain historical paths, hashes and dates. Their old paths are not instructions for the current layout. Current instructions and Markdown navigation use the new locations.

Only C's documentation comparison helper needed a Python path edit: its baseline now points at `evaluation/`. All 33 Python sources recorded by the formal experiment retain their hashes. Because the source scanner also includes the later-added helper, audits of the published matrix explicitly record that extra file using `--allow-source-drift`; they do not falsely claim an identical source-file set. A new [reorganization audit](../evaluation/validation/reorganization_review.json) checks all 72 cells, 432 client rows and exported metrics after the move.

The [November 13 review](repository_review.md) remains a historical account of the first reorganization; its before/after table describes that checkpoint. This document and its manifest describe the current layout.
