# Report source materials

**A writes and integrates the final 3–4 page technical report. E provides data analysis as an input to that report.** The integrated draft and video/presentation drafts remain in the maintainer's private project folder; they are not published here.

## Main evaluation

The required three-workload, six-capacity, four-policy study is collected in [evaluation/](../evaluation/):

| Material | Purpose |
|---|---|
| [Global results](../evaluation/runs.csv) | All 72 experiment combinations |
| [Client results](../evaluation/per_client.csv) | 432 client rows, including mixed at 5 MiB |
| [Workload characterization](../evaluation/characterization/) | Input counts, distributions, top five, byte volumes, and oversized counts |
| [Formal figures](../evaluation/figures/) | Six PNG/SVG figure pairs |
| [Findings](../evaluation/findings.md) | Supporting numerical observations and limitations |
| [Program test report](../evaluation/test_report.md) | Executed checks and reproducibility scope |

The report must explain the observed behavior and cover all five assignment questions: the best policy under each metric, workload effects, capacity effects, unequal client benefits, and Custom trade-offs. Use the same inputs and assumptions for fair comparisons, and explain LA-GDSF's lifetime frequency and additional admission rule. Complete results remain in CSV; selected comparisons belong in the short report.

## Design and contributor evidence

| Source | Scope |
|---|---|
| [Simulator architecture](simulator_architecture.md) | A's architecture and data-structure explanation |
| [Custom policy design](custom_policy_design.md) | Edited report section based on D's accepted design |
| [Original LA-GDSF delivery](../docs/d_la_gdsf_design.md) | Preserved D document, with a separate [review](../docs/d_custom_policy_review.md) |
| [B's FIFO/LRU review](../docs/b_fifo_lru_review.md) | Accepted baseline-policy validation |
| [C's LFU review](../docs/c_lfu_reference_review.md) and [provided-trace evidence](../docs/c_lfu_provided_20261125.md) | Accepted tests, metric checks, and independent replay evidence |

E's delivered analysis informs A's interpretation and figure selection. It does not transfer final report authorship to E. D's accepted explanation and existing recording are retained.

## Supplementary material

The earlier ten-seed synthetic study, its original four figure pairs, and its findings are under [supplementary/synthetic/](../supplementary/synthetic/). They can support clearly labeled additional analysis; they are not outcomes of the three instructor-provided traces. Original numerical outputs and configurations are preserved.

See [HOWTO](../HOWTO.md) for reproduction and [requirements](../docs/requirements.md) for report, video, and submission criteria.
