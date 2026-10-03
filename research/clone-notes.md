# H-CLONE: integer mass transfers through vertex clones

Prepared 2026-09-27. The coordinator dispatches full-order trials and promotes
independently checked artifacts; this worker implemented and tested the method.

## Pilot result and decision

The coordinator's [random clone screen](../reports/pilot-h5-clone-001/report.json)
ran 22,277 exact trials in approximately 30 seconds from the checked medium
annealing incumbent. No clone was accepted. The best trial delta was **+42,228**
and the worst **+825,446** numerator units. The unchanged candidate was recounted
through the runner's independent compiled Lean checker.

Decision: retire unselected integer-unit clone transfer for this basin during
the current pilot. Strongly positive sampled deltas do not rule out every clone
pair, fractional weight perturbations, or a different parent. The proposed
faster formula below is therefore deferred rather than implemented: throughput
was already sufficient to obtain a useful negative result.

## Mechanism and exact domain

Replace vertex u's adjacency to each w != u by the old adjacency of v to w,
where v != u. Leave all other pairs unchanged and keep every diagonal blue.
The edge uv becomes blue, so u and v become blue twins. Order n and all unit
weights are unchanged: this is directly admissible to the existing Lean checker.

Equivalently, consider the original weighted template and transfer one unit of
mass from u to v: w_u = 0, w_v = 2, all others 1. Mapping both new twin indices
to original index v preserves every edge color, including repeated indices.
The resulting ordered-quadruple sum is exactly the cloned template numerator.
Although zero weight is not an allowed serialized hill certificate, this is
only an algebraic interpretation; the emitted certificate retains n unit
weights and has no zero-weight entries.

Thus this implements a discrete block-weight change without modifying the
checker. It is a large coordinated star edit, not a first-order gradient step.
The exact weighted objective along e_v-e_u is quartic. A small or negative
first derivative would not by itself certify the unit-step decrease. Symmetry
can make first derivatives vanish; curvature and higher terms still matter.
These are elementary derivations here; no novelty claim is made.

## Implementation

[clone_search.py](../experiments/strategies/clone_search.py) follows the existing
standalone runner protocol. Trial evaluation walks the changed incident edges,
computing the exact native delta on the **current updated graph before each
flip**. Summing these sequential deltas telescopes to the exact clone delta.
Every trial is rolled back; negative trials are reapplied and checkpointed.
A final full native recount checks incremental drift. The runner must still
perform independent compiled Lean verification.

Computational cost is at most n-1 edge-delta evaluations per trial plus rollback;
there is no full recount per trial. This avoids introducing a new native API.
Its actual full-order throughput should be measured before optimizing further.

Three pair-selection options support causal short comparisons:

- `random`: uniform ordered pair. This is the simplest structural screen.
- `closest`: choose the smallest Hamming-distance clone among a random pool,
  testing whether smaller profile changes make the discrete mass transfer viable.
- `linear`: choose the smallest sum of single-edge deltas on the unchanged
  parent among a random pool. This is explicitly a **surrogate**, not the exact
  clone objective; star interaction terms can invalidate its prediction.

Configuration keys: `selection` (default `random`), `pool_size` (default 8),
`max_moves` (default effectively unlimited within the runner time cap).
Search diagnostics retain the first 100 exact trial deltas and edit counts,
the best/worst trial delta, accepted moves, and RNG state. Strictly negative
moves only; zero-change clones are recorded but not accepted.

## Tests and next decision

[test_clone.py](../tests/test_clone.py) checks all 64 labeled four-vertex graphs
and all 12 ordered clone pairs: 768 exact trials. For each, it compares the
native sequential delta with an independent literal ordered-quadruple count,
checks the weighted (0,2) interpretation, verifies emitted adjacency and full
counts after acceptance, and restores the parent. Additional tests check pair
selection, invalid endpoints, and rollback after an injected evaluation failure.
All three tests pass in 0.22 seconds.

Prediction: a symmetry-broken single-edge plateau may admit a negative clone
delta. Cheapest useful test: equal-time random versus closest pair screens on
the same checked parent, with exact delta/edit-count distributions retained.
If all tested clone deltas are strongly positive, retire this integer-unit mass
transfer for that basin rather than infer that all weight directions fail.
Fractional weight steps and refined clones are a distinct follow-up requiring
more representation/checker work, unless realized by a larger unit-weight graph.

## Potential faster exact formula — derived, not yet tested

Let a be the red indicator of uv. For vertex x, let d_b(x), t_b(x), k_b(x),
k_r(x) count blue neighbors, blue triangles containing x, and blue/red K4s
containing x. Let c_b count common blue neighbors of u and v; q_b and q_r count
blue and red edges within the common blue and common red neighborhoods,
respectively. Define

```
F(x) = 14*d_b(x) + 36*t_b(x) + 24*(k_b(x) + k_r(x)).
```

Counting configurations containing the replaced vertex gives these differences:

```
delta E_b  = d_b(v) - d_b(u) + a
delta T_b  = t_b(v) - t_b(u) + d_b(v) - (1-a)*(c_b+1)
delta K4_b = k_b(v) - k_b(u) + t_b(v) - (1-a)*(q_b+c_b)
delta K4_r = k_r(v) - k_r(u) - a*q_r

delta N = F(v)-F(u) + 36*d_b(v) + 24*t_b(v) + 14*a
          - 36*(1-a) - 60*(1-a)*c_b - 24*((1-a)*q_b + a*q_r).
```

Reason: the new blue neighborhood is B_v minus u, plus v itself; the new red
neighborhood is R_v minus u. Remove configurations using u from those original
neighborhoods and add those containing the new blue twin v. With cached per-vertex
contributions, pair evaluation needs only common-neighborhood subgraph counts.
Cache construction/invalidation could dominate short searches, so do not
implement this before observing a promising clone signal. This formula is an
untested derivation, distinct from the already-tested sequential-delta code.

## Existing structural-screen provenance

The previously recorded [structural screen](../experiments/structural/pilot-screen-001.json)
is unchanged. Its source identities remain:

- `screen.py`: `9cfe0036392f7f8dfa77983ee6c495b4f8b82509c9c1716c420cab72fc6e547e`
- `profiles.py`: `f2c20249325ed952fcf5830bacc191838d8bc024d821a2332c1935f3b7115bf1`

Those files were not edited while implementing clones. Its evidence level
remains exact Python profile arithmetic with independent tiny enumeration and
historical regression tests; it has no Lean checker certificate. Future edits
must retain the original source versions if those experiment hashes are needed.
