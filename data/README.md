# Input datasets

- [reference/](reference/): the original instructor resource metadata, 15-request reference trace, three expected policy outputs, and answer key. The CSV contents are preserved unchanged.
- [workloads/](workloads/): reserved for additional team-authored experimental input traces. It currently contains only its original placeholder.

The 40 seeded traces generated for D's reproduced matrix stay with that specific [result snapshot](../results/experiments/d_reproduction/traces/). Keeping them there preserves the association with the seed list and hashes in its config.json. They are synthetic data, not additional instructor inputs.

[Input schemas](../docs/data_dictionary.md) explain fields and resource identity. Outputs belong under results/, not beside the instructor expectations.
