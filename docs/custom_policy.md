# LA-GDSF custom policy

## Objective and provenance

D's [original consolidated design package](d_la_gdsf_design.md) is available for attribution and reference. This maintained specification and the [revision review](d_custom_policy_review.md) record the integrated rules and editorial corrections.

Contributor D supplied a latency-aware size/frequency policy, executable prototype, scenario oracles, workload generators, and preliminary aggregate results. The updated English handoff received November 22, 2026 resolves the earlier pseudocode mismatch and was checked against the integrated implementation; see [D revision review](d_custom_policy_review.md). This repository adapts that work to the shared simulator. The primary objective is lower average response time, with hit ratio secondary. Byte traffic and large-resource client performance are explicit trade-offs, not fairness guarantees.

## Score and retained state

For resource r:

```text
H(r) = L + F(r) * (origin_latency_ms(r) - hit_latency_ms) / (size_bytes(r) / 1024)
```

`F` counts every request, including misses, admission bypasses, and oversized requests. It persists after eviction. `L` starts at zero and is updated to `max(L, H(victim))` for each actual eviction. Each cached resource has a stored score and last-access step. A hit recomputes its score with the current L; unrelated cached scores remain unchanged.

For zero-byte resources, the implementation uses a one-byte effective denominator to define the score without division by zero. Storage and traffic still use the true size of zero. This is an integration boundary convention, outside D's nonzero-size data. Origin latency below hit latency is allowed and produces a negative savings term; the term is not silently clamped.

## Access and admission

1. Count the request before branching on hit or miss.
2. On a hit, update the stored score and last-access step. Cache insertion order remains unchanged.
3. On an oversized miss, skip insertion and eviction. The request still counts toward persistent F and origin traffic.
4. On a fitting miss with sufficient free space, insert directly.
5. Otherwise, preview victims in increasing `(stored H, last-access step)` order until enough space would be freed.
6. Compute the candidate score using L **before** eviction. Bypass if it is strictly below the largest stored score among planned victims. Equality admits. A bypass leaves cache contents, used bytes, L, and cached priorities unchanged.
7. If admitted, commit the planned removals and inflation updates, then compute the insertion score using L **after** those removals.

The main `CUSTOM` version enables admission filtering. `CUSTOM_NOADM` follows the same logic but always admits a fitting miss, providing the same ablation as D's `CUSTOM_noadm`.

## Canonical pseudocode

The insertion helper records the current processing step and adds the true resource size to used bytes. PRIORITY uses the configured hit latency and the one-byte denominator convention for zero-sized objects described above.

```text
ACCESS(r):
    step += 1
    F[r] += 1
    if r is cached:
        H[r] = PRIORITY(r, L)
        last[r] = step
        return HIT
    record origin latency and size as miss response and traffic
    if size[r] > capacity:
        return MISS
    select victims by (stored H, last), until enough space would be free
    if victims exist and admission filtering is enabled:
        H_cand = PRIORITY(r, L)
        if H_cand < max(stored H[v] for v in victims):
            return MISS
    save all victim priorities before removal
    remove victims and their resident metadata; subtract their sizes
    L = max(L, saved victim priorities) if any victims were removed
    insert r with H_ins = PRIORITY(r, L) and last[r] = step
    add size[r] to used bytes
    return MISS
```

This is explanatory pseudocode; the implementation separates request observation, victim preview, admission, removal, and insertion callbacks. Resident metadata is removed while lifetime F remains available.

## Integration decisions

The initial pseudocode retained a pre-eviction candidate score at insertion. D's November 22 revision explicitly separates H_cand (old L, admission comparison only) from H_ins (updated L, stored at insertion), matching the executable prototype and existing integrated code. The description mismatch is resolved. The original files are preserved; the [receipt and checks](d_custom_policy_review.json) identify the reviewed update.

D's prototype hardcodes a 5 ms hit cost. Here the configured hit latency is passed to Custom, preserving the reference behavior at 5 ms and keeping nondefault configurations consistent. Full URLs replace the prototype's `(host, path)` keys. Workload selection order and random-number calls preserve D's supplied experiments.

The original four-method policy draft could not count bypassed misses or preview a rejection without mutating cache storage. Two default hooks, `on_request` and `should_admit`, were added. Standard policies need no admission-specific behavior. See the [lifecycle contract](interfaces.md).

## Complexity and limits

The current implementation scans candidate items for each planned victim. With n cached objects and k victims, preview is O(k*n) in the worst case and O(n) temporary storage. It is deliberately simple for the supplied 21-resource dataset. Persistent request counters use O(u) memory for u distinct requested resources. This is not a bounded-memory production proxy implementation.

The score favors small resources with frequent requests and large latency savings. It does not directly optimize byte-hit ratio, total traffic, or per-client fairness. Retained lifetime frequencies can also preserve historical popularity; the finite aging scenario demonstrates behavior on that trace rather than proving every stale object will eventually leave under all future traces. The policy uses supplied origin latencies as known metadata.

## Regression targets

The integrated tests retain D's T1-T4 and T6 frozen hit/miss sequences and reference sequence `MMMHHMHHMHMHMHM`. The earlier T5 sequence remains exercised for capacity invariants for continuity, but D did not provide a frozen oracle and removed that label from the revised delivery. A separate equal-size/equal-cost test explicitly verifies LRU tie-breaking and equality admission.

On the 15-request reference trace, Custom has 7 hits, average response 68.666666... ms, and origin traffic 299008 bytes (292 KiB). These are D-derived regression targets verified by the integrated implementation, not instructor-provided Custom answers.
