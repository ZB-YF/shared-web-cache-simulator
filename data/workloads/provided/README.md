# Instructor-provided evaluation workloads

These original CSV files were received and copied without changing their bytes on November 25, 2026. Each trace has **3000 requests, six clients, and 21 requested resources**. Their resource popularity, ordering, and requested data volumes differ.

| File | Intended browsing pattern | SHA256 |
|---|---|---|
| `requests_sequential.csv` | Broad requests with relatively uniform popularity | `7486650b74bc47d98dee38226d464c670181806c8b35e98abcc940cf3d18915c` |
| `requests_repetitive.csv` | Repeated access to popular resources | `6f091f07b83781afdf8fb908c65437c522cd9be96ab414a827f51f55429b0dca` |
| `requests_mixed.csv` | Heterogeneous browsing patterns | `8f8a34f1129cd147cd6467ec5467bb626d9e82d76d8803d97b9707ba0c7a41f8` |

All experiments use [`data/reference/resources.csv`](../../reference/resources.csv), SHA256 `b2117bca54a566a999cd21333bb34a3dc25e0d0f371cf9aad8bfb7c63d1869e7`. The received resource file matches this repository copy byte for byte.

Run the formal matrix from the repository root:

```bash
python3 -m experiments.provided --output-dir results/my_provided_matrix
```

For one trace with detailed request records:

```bash
python3 main.py --requests data/workloads/provided/requests_mixed.csv --policy CUSTOM --capacity 5242880 --output-dir results/my_mixed_custom
```

The [experiment guide](../../../experiments/README.md) explains the six capacities, workload characterization, and output files. Instructor-provided workloads and D's supplementary synthetic generators remain separate.
