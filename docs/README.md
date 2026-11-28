# Documentation guide

Terminal examples assume the project root unless an absolute path is shown. Public project documentation is in English; private planning and original handoff archives are outside this repository.

| Topic | Document |
|---|---|
| Setup and exact reproduction commands | [HOWTO](../HOWTO.md) |
| CLI parameters, output conventions, troubleshooting | [Usage](usage.md) |
| Revised requirements, six capacities, metric definitions | [Requirements](requirements.md) |
| Required fixed-input matrix and supplementary experiments | [Experiment guide](../experiments/README.md) |
| Input schemas, URL identity, reference aliases | [Data dictionary](data_dictionary.md) |
| Module ownership and policy callbacks | [Interfaces](interfaces.md) |
| LA-GDSF rules, scoring, and admission decisions | [Custom policy](custom_policy.md) |
| B's FIFO/LRU review, merged PR #1 | [B review](b_fifo_lru_review.md) |
| C's LFU/metric review, merged PR #2 | [C review](c_lfu_reference_review.md) |
| C's original configs and replay record, merged PR #3 | [C run evidence](c_run_evidence_20261123.md) |
| C's 18 LFU provided-trace runs, merged PR #4 | [LFU analysis and reproducible comparison](c_lfu_provided_20261125.md) |
| D's original consolidated source and its interpretation | [Original design](d_la_gdsf_design.md), [review](d_custom_policy_review.md) |
| Test coverage and release acceptance | [Test plan](test_plan.md), [validation evidence](validation.md) |
| Program test report and supporting result observations | [Test report](../evaluation/test_report.md), [run notes](../evaluation/findings.md) |
| Technical status and contribution areas | [Development status](development.md) |
| B/C PRs, D/E Drive handoff, sole-maintainer workflow | [Contributing](contributing.md) |
| Historical file inventory and path mapping | [Repository review](repository_review.md), [manifest](reorganization_manifest.json) |
| Current directory layout and result relocations | [Layout guide](repository_layout.md), [migration manifest](layout_migration.json) |

Start with the [required evaluation](../evaluation/), [generated figures](../evaluation/figures/) and [report materials](../reports/README.md). E supplies data analysis and A writes the integrated report. The older [synthetic findings](../supplementary/synthetic/findings.md) remain supplementary. [Video requirements](../video/README.md) are separate from the report.
