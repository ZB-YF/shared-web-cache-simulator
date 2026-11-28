# Implementation and contribution status

The simulator supports the revised assignment's three provided workloads, six capacities, and four primary policies. The required experiment evidence is published under the top-level [evaluation directory](../evaluation/); the older ten-seed study is [supplementary](../supplementary/synthetic/).

## Implementation evidence

| Component | Published evidence |
|---|---|
| Shared cache and FIFO/LRU/LFU/LA-GDSF | [Source code](../cache_simulator/) and [reference validation](validation.md) |
| Added eviction, oversized-request, and utilization metrics | [Metric definitions](data_dictionary.md), tests, and [global results](../evaluation/runs.csv) |
| Three unchanged instructor workloads | [Input files](../data/workloads/provided/) with common resource metadata |
| Workload characterization | [Counts, popularity, top five, oversized counts, and hypotheses](../evaluation/characterization/) |
| Required experiment matrix | [72 global rows](../evaluation/runs.csv) and [432 client rows](../evaluation/per_client.csv) |
| Comparative plots | [Six PNG/SVG figure pairs](../evaluation/figures/) |
| Tests and independent accounting | [Test report](../evaluation/test_report.md) and [validation history](validation.md) |
| Reproduction instructions | [HOWTO](../HOWTO.md) |

Current entry points accept input files, cache capacity, hit latency, and policy. Statistics and the provided-trace pipeline were prepared during maintainer integration; they are not attributed to a new C submission. The layout change preserves original inputs, replacement algorithms, and published numerical files.

## Contribution record

| Member | Accepted contribution and delivery route |
|---|---|
| A | Shared simulator, integration, revised metrics and evaluation publication; sole GitHub maintainer and final report author |
| B | Merged PR #1: FIFO/LRU review, reference comparison, and five tests |
| C | Merged PRs #2–#4: LFU/metric tests, historical configurations, and the provided-trace LFU replay/analysis evidence |
| D | Drive delivery: Custom design/prototype, clarified score timing, scenarios, and preliminary experiments; recorded segment retained |
| E | Drive delivery: data analysis covering workloads, capacity effects, policy trade-offs, and clients; source material for A's report |

B/C contribute through pull requests. D/E contribute through Google Drive, and A manually integrates their material. [Contribution instructions](contributing.md) describe the workflow.

## Report and presentation boundary

E supplies data analysis; **A writes and assembles the final 3–4 page technical report** using the accepted code, results, and contributor explanations. The current integrated draft remains in the maintainer's private project folder and is not a published repository deliverable. The public [report materials](../reports/README.md) and [evaluation findings](../evaluation/findings.md) support that work.

D's completed presentation segment is retained. Video scripts and presentation drafts remain private. The repository's [video page](../video/README.md) documents assignment requirements and verified publication status; it does not assert that a combined video or Brightspace submission has been completed.

Final submission must contain a reproducible ZIP with source, instructions, inputs, experiment scripts, CSVs/configs, figures, and the integrated report. A separately submitted YouTube link must point to the all-member presentation. See [requirements](requirements.md) for the official criteria.
