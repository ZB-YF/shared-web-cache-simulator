# Input datasets

| Directory | Purpose |
|---|---|
| [reference/](reference/) | Instructor resource metadata, 15-request validation trace, three expected outputs, and answer key |
| [workloads/provided/](workloads/provided/) | Three instructor-provided 3000-request workloads required for formal evaluation |

Use the **same `reference/resources.csv`** for all required experiments. The original CSV bytes and filenames are preserved. Input records use full URL identifiers; see the [data dictionary](../docs/data_dictionary.md).

D's 40 generated synthetic traces remain inside [their historical result snapshot](../supplementary/synthetic/traces/) alongside the matching seed/configuration hashes. Additional team-authored traces can be placed under `workloads/` with their provenance clearly stated. Generated traces are not instructor-provided inputs merely because their names describe similar browsing patterns.

Published required outputs are in [evaluation/](../evaluation/); additional seeded outputs are in [supplementary/](../supplementary/). Write fresh local runs under `results/`. Keep instructor expectations separate from generated simulator results.
