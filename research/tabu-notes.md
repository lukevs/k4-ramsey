# H8: exact-neighborhood tabu search

Prepared 2026-09-27. Implementation and tiny tests are ready; the coordinator
owns full-order dispatch, independent checking, and result promotion.

## Hypothesis and provenance

Prediction: selecting the best admissible edge across the entire graph while
forbidding recently flipped edges escapes basins that sampled strict descent
and short annealing walks cannot escape at comparable wall time.

This is a standard tabu mechanism, not a novelty claim.
[Parczyk et al., section 3.2](https://arxiv.org/html/2206.04036v3)
describe replacing a state-history exclusion rule with a history of modified
bits. We transfer that attribute-based rule from their construction search to
unrestricted individual edges of the existing 768-vertex graph. Our native
exact delta cache makes whole-neighborhood scans practical; it does not reduce
the underlying number of possible graphs or establish global optimality.

## Concrete algorithm

[tabu_search.py](../experiments/strategies/tabu_search.py) uses the existing
single-experiment runner protocol and the independently audited native cache.
At decision step s, choose the edge with smallest exact current delta among
edges whose expiry is <= s. A tabu edge is admissible by aspiration only if
its prospective value is **strictly below the best value found in this run**.
The move is accepted regardless of sign. Equal deltas use lexicographic edge
order; seed randomizes tenure, not ties. This deterministic tie policy is a
potential bias to consider in a subsequent hypothesis, not concealed randomness.

After choosing an edge at step s, set its expiry to `s + tenure + 1`, where
the actual tenure is the configured base plus a uniform integer from zero to
the configured jitter inclusive. It is therefore forbidden for the following
`tenure` decisions, unless aspiration applies. Store both symmetric expiry
entries in one persistent ctypes signed-int array, passed to the native scan
without rebuilding or copying it each iteration. The diagonal is never used.

The strategy retains the best construction, not the last walk state. A Python
bytearray adjacency mirror provides cheap best-state copies; it is checked
against exported native adjacency at termination. Each chosen cached delta is
checked against the independent native single-edge delta computation before
flipping. Final walk and retained-best numerators both receive full native
recounts; the parent runner must still independently check the retained graph
using compiled Lean.

The checker and mathematical objective are unchanged. No weights, diagonal
colors, or graph order are altered. The cache implementation is search code,
not a substitute for independent candidate verification.

## Configuration and evidence

```
{"max_moves": 1000000000, "tenure": 40, "tenure_jitter": 40,
 "checkpoint_seconds": 1}
```

The runner's wall-time budget is authoritative. Startup/cache construction is
included in the search clock. Checkpoints contain the best known construction
at least once per configured interval, subject to completion of the current
native call. Final recount/checkpoint overhead occurs after the timed loop and
must fit the runner's outer timeout. A no-allowed-edge condition terminates
cleanly; it does not mean a local optimum.

`search.json` records current and retained-best numerators, attempted moves,
uphill and zero moves, aspiration events, improvements, RNG state, setup time,
first 100 move diagnostics, and best-value history. The sample trace supports
auditing tenure boundaries and state transitions without storing every walk
state. Only the runner may promote independently checked results.

Four tests pass in 0.001 seconds: tenure off-by-one boundaries; native strict
aspiration and expiry; deterministic tiny walks with retained-best recount;
and all-edges-tabu termination. These strategy tests complement the native
cache worker's exhaustive and word-boundary tests, rather than replacing them.

## Pilot decision rule

Start with a short screen from a checked incumbent. Compare total wall time,
move count, best gain, uphill fraction, and whether aspiration is ever used
against current annealing evidence. If useful, perform matched-parent,
matched-budget comparisons with alternative tenure and tie policies. A single
better witness is valid progress; it does not establish method superiority.
If no gain and cycling or over-restriction is evident, modify that mechanism
rather than launching a wide tenure sweep by default.
