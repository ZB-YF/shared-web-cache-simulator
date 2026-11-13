# Repository review and reorganization

The repository was reviewed and reorganized on November 13, 2026. Its purpose remains a small university course project. The changes group files by function and make existing results visible to teammates; they do not change simulation algorithms or introduce packaging/build infrastructure.

## Inventory and migration

The initial inventory covered **117 project files and 26 local cache/system files** outside Git internals. Every Python/Markdown/text file was read, every CSV was parsed for schema and row count, every JSON config/summary was parsed, and all figure pairs were identified by format, dimensions, and purpose. Local Python bytecode and Finder metadata were classified as generated housekeeping files.

The project files comprised 23 Python files, 15 Markdown files, 56 CSV files, 9 JSON files, 4 PNGs, 4 SVGs, one optional dependency list, .gitignore, and four empty .gitkeep placeholders. New navigation, collaboration, and review documents were added separately.

| Before | After | Reason |
|---|---|---|
| Root-level core Python modules | cache_simulator/ | Group implementation in one importable package |
| Root main.py implementation | cache_simulator/cli.py plus a small root main.py wrapper | Preserve the familiar CLI while keeping implementation together |
| policies/ | cache_simulator/policies/ | Keep policies with the simulator that consumes them |
| data/resources.csv, data/requests_reference.csv | data/reference/ | Put instructor inputs beside their expected outputs |
| Uppercase docs filenames | Lowercase snake_case under docs/ | Consistent names and simpler links |
| HOWTO.md | docs/usage.md | One documentation home |
| docs/EXPERIMENTAL_FINDINGS.md | reports/experimental_findings.md | Keep result interpretation with figures |
| report/ | reports/ | Consistent output-material category |
| results/reference/FIFO_102400 and peer directories | Lowercase policy directory names | Consistent naming; contents unchanged |
| results/d_reproduction/ | results/experiments/d_reproduction/ | Separate reference checks from multi-workload experiments |
| Ignored experiment snapshots | Explicitly allowlisted in .gitignore | Include reviewed CSVs, configs, and traces on GitHub |

[reorganization_manifest.json](reorganization_manifest.json) maps every pre-existing file to its retained location and original SHA256 where applicable. `baseline_commit` is the last commit before this change: `cf9b7026b1e254a54a0429c5bcee0b19b724fce8`. New files have no entry in that historical inventory. The manifest also identifies retained, ignored local caches.

## Duplicated, outdated, or unnecessary candidates

Nothing was deleted. The review found:

| Candidate | Assessment and action |
|---|---|
| Four byte-identical empty .gitkeep files | Intentional placeholders; retained in their directories |
| __pycache__ trees and .DS_Store files | Generated/local housekeeping, unnecessary for GitHub; retained locally and ignored |
| data/workloads/ placeholder | Currently unused but a reasonable home for future team input traces; retained |
| PNG and SVG versions of each figure | Two useful export formats, not accidental duplicates; both retained |
| d_compatible.csv versus summary.csv | Different schemas, rounding, and review purposes; both retained |
| Experimental findings versus report README | Findings contain analysis; README is the index/status; both retained |
| Old code paths in historical config.json files | Historical generation metadata, not current import instructions; preserved with migration context |
| CSV CRLF line endings | Original data bytes are intentional; .gitattributes preserves them and recognizes CRLF in whitespace checks |
| Prior statements that all results were Git-ignored | Outdated documentation; updated to distinguish reviewed baselines from ad hoc runs |

No exact-content duplicate project files were found apart from the four empty placeholders. No archive or deletion was needed. Any future cleanup that removes files requires maintainer approval.

## Historical provenance

All 73 existing dataset/result/figure files (including original JSON configs) remain byte for byte identical. All 115 historical source-hash entries in the five saved configurations resolve exactly to the baseline commit. In particular, source_sha256 entries inside old configs are not replaced with hashes from the new layout. To inspect their source snapshot, use the recorded hashes and the pre-reorganization baseline commit; the path manifest explains relocations.

Moving source modules requires changes to imports, repository-root resolution, input paths, output-path naming, and documentation. The root CLI and experiment module commands remain available. Python source was compared against the original with only these permitted structural substitutions; policy and simulation logic were not changed.

## Verification

- All 25 existing tests pass before and after reorganization.
- FIFO/LRU/LFU still match all ten instructor reference fields for all 15 requests.
- A fresh full 1000-run matrix is compared byte for byte with the preserved baseline's runs.csv, summary.csv, d_compatible.csv, and 40 trace CSVs.
- Existing single-run outputs, input data, original configs, and figure files are checked against their original SHA256 values.
- Documentation links, package imports, source syntax, and Git inclusion of reviewed data are checked.
- The staged repository is tested from a separate clean directory before push.

Detailed correctness context is in [validation evidence](validation.md). Review and integration ownership follows the [Google Drive / sole-maintainer workflow](contributing.md).

## Unresolved project work

The final report, video, and team sign-off remain pending. The documented Custom pseudocode/prototype discrepancy still requires D's review; no algorithm rule was changed to resolve it during this reorganization. B/C review of their implementation areas and E's final experiment selection remain as described in [development status](development.md). No raw private planning documents or Drive-original files were added to this public repository.
