# D Custom Policy Revision Review

D's updated English package was received and checked on **November 22, 2026**. Its revised pseudocode explicitly distinguishes the candidate score before eviction from the insertion score after inflation updates. This resolves the previously recorded description mismatch and agrees with the existing integrated implementation. No simulator or policy algorithm was changed.

## Received material and provenance

The delivery contains D_Part.md, D_Requirements.md, D_Pseudocode.md, D_Test_Cases_and_Report.md, five Python scripts, and results_D.csv. All ten originals were preserved in the private integration archive. [The receipt and verification record](d_custom_policy_review.json) records their filenames, byte counts, SHA256 hashes, and comparison results. The combined English package's five embedded scripts match the separately delivered scripts.

D_Part.md repeats the split documents and code. At the November 22 checkpoint the public repository kept a canonical [policy specification](custom_policy.md), this review, and a concise [report section](../reports/custom_policy_design.md), rather than publishing several competing algorithm descriptions or a second simulator. D's original files remain intact in the handoff archive.

The prototype retains its fixed external input-directory assumption. A private portable copy changed only that path to the actual reference dataset; the original files were not edited. Normal repository tests and experiment execution remain independent of the private archive.

## Rules checked against the code

| Rule in the revised delivery | Integrated behavior | Result |
|---|---|---|
| Count every request, including misses; preserve frequency on eviction | on_request increments lifetime frequency | Matches |
| Order victims by stored priority, then least recent access | choose_victim uses priority and last-access step | Matches |
| Preview victims before making an admission decision | Cache.admit previews with read-only candidate mappings | Matches |
| Compute H_cand with the old L; bypass only when strictly lower than the largest victim score | should_admit accepts equality and rejects without deletion | Matches |
| Update L only on committed removals | on_remove updates inflation | Matches |
| Recompute H_ins using updated L | on_insert recalculates after all committed removals | Matches |
| Oversized resources cause misses without eviction or insertion | Cache rejects before admission planning | Matches |

D's supplied prototype has the same executable syntax tree as the earlier prototype; its changes explain the score timing in comments. Workload generation is unchanged. The scenario file drops the unasserted T5 label; the integrated exact-priority tie test is retained because it actually exercises equality and LRU tie-breaking.

## Verification results

- D's original five named scenario oracles and reference check pass in the portable prototype copy.
- All 35 integrated tests pass. Two additional integration checks assert eviction of the formerly hot A at step 20 of T4, and the final inflation/insertion score after multiple committed removals.
- The standard policies still match all ten instructor fields for all 15 reference requests.
- The Custom reference result remains 7 hits, 68.666666... ms average response, and 299008 origin bytes (292 KiB).
- The updated prototype and integrated simulator match across 1000 matrix runs and 900000 request events, including ordered evictions, used bytes, global metrics, and per-client metrics.
- All 100 supplied aggregate rows and 1700 cells match. The delivered results_D.csv is also byte-identical to the published d_compatible.csv baseline, so existing CSVs and figures were preserved.

This comparison validates the delivered behavior on the supplied metadata, scenarios, and synthetic generators. It does not turn the synthetic workloads into real browsing data or prove universal performance superiority.

## Editorial corrections applied during integration

The algorithm timing issue is resolved. The report-ready text also corrects these remaining wording details from the delivery without changing its rules:

| Delivery wording | Wording used in the repository |
|---|---|
| Six scenarios plus the reference trace | Five named scenarios T1-T4/T6 plus the reference trace; exact-tie tests are separate integrated checks |
| Largest resource is 59 MiB | The supplied maximum is 59637760 bytes, or 56.875 MiB; approximately 59.64 MB in decimal units |
| Prototype sorting complexity used as the integrated complexity | The prototype sorts O(n log n); the current cache preview repeatedly scans and is O(k*n) for k victims among n residents |
| Every formerly popular resource eventually leaves | T4 demonstrates eviction of A; no guarantee for every possible future trace |
| Read H of victims after deleting them in pseudocode | Save victim priorities before committing removals |
| References to D_Pseudocode_EN.md | The delivered file is D_Pseudocode.md; the maintained public description is custom_policy.md |

The report section is credited to D's revised design and edited for consistency with actual code and data. It is source material for A's final 3–4 page integrated report; E supplies data analysis.

## Updated handoff status

D's revised rules, corrected score-timing pseudocode, test plan, and draft report contribution have been received and checked. The earlier request to resolve that pseudocode discrepancy is closed. On November 25 the maintainer reported that D's video was also recorded. Retain her accepted design and existing recording for assembly; no additional rewrite, review cycle or recording is requested. C's original replay-evidence handoff is complete through PR #3. B/C/E's remaining explanations, checks and analysis are tracked separately in [development status](development.md).

## November 24 consolidated design supplement

D supplied an additional file named LA-GDSF Design.md, now published byte for byte as [d_la_gdsf_design.md](d_la_gdsf_design.md). It combines role definitions, policy rules, the corrected score-timing pseudocode, five embedded prototype scripts, scenario expectations, and pilot-result discussion. Its SHA256 and embedded-code comparison are recorded in the [receipt](d_custom_policy_review.json). This is a consolidated contributor reference document, not a replacement simulator or the final team report.

All five embedded Python scripts match the already checked delivery. The H_cand/H_ins distinction is unchanged, so no algorithm, production source, tests, or experiment output was replaced. The original formatting, filenames mentioned in examples, and section numbering are preserved as submitted.

The original supplement also preserves previously noted draft details: the 59 MiB size wording, prototype sorting complexity, scenario-count and aging claims, and some inherited section references. Its code examples use an external prototype input directory and are not the repository's run instructions. Use the [maintained specification](custom_policy.md), [edited report section](../reports/custom_policy_design.md), and [usage guide](usage.md) for corrected/current material.

C's original-config and replay-evidence follow-up has now merged in [PR #3](https://github.com/ZB-YF/shared-web-cache-simulator/pull/3); that earlier handoff gap is closed. The final team report, E's final experiment/figure selection, video, and package acceptance remain separate work.
