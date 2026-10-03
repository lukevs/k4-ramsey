# Matching neighborhoods: prototype and derivation

2026-09-27. H1/H3, own derivation prompted by the adjacent pseudo-Boolean
optimization review. Novelty is not established. Scope: unit weights, blue
diagonal, fixed template order. This is not a global-optimality method.

For disjoint free edges uv and xy, only the four-distinct-endpoint K4 term
can depend on both flips. The repeated-index terms involve at most three
distinct vertices, so they contribute no interaction. If the four cross edges
ux, uy, vx, vy are not all the same color, the interaction coefficient is zero.
Otherwise it is +24 when uv and xy currently have the same color, and -24 when
their colors differ. This follows by taking the mixed finite difference of
24 times the product of their two color-match indicators.

Consequences: all coefficients belong to {-24,0,24}; favorable interactions
require opposite-colored free edges. A matching of m edges satisfies
Q(z) >= sum_i (a_i - 12*d_i)*z_i, where d_i is the number of negative
interactions incident to i. Thus a_i >= 12*d_i for every i rules out any strict
improvement in that particular matching. This is a sufficient, not necessary,
obstruction. Uniform a_i >= 12*(m-1) is an even cheaper sufficient test.

`experiments/strategies/matching_search.py` builds the exact quadratic using
native single-flip deltas and the four-endpoint shortcut. Its branch-and-bound
uses a conservative lower bound from negative residual linear terms and all
negative remaining pair terms. A fully exhausted search certifies only its
chosen matching neighborhood; timeout returns a feasible best assignment and
explicitly marks that neighborhood incomplete. Every accepted graph change is
fully recounted natively, and the runner independently checks the final graph
with Lean. Random, low-delta, and interaction-guided selection are configurable.
A fourth `mode: pair` directly screens every disjoint pair whose single-flip
costs sum to less than 24. At a single-flip local minimum these are the only
pairs that can strictly improve, since b >= -24. An exhausted screen therefore
certifies no improving disjoint pair at that graph, but says nothing about
overlapping pairs or larger coordinated changes. If singles remain negative,
this mode first descends those rather than claiming pair exhaustion.

Tiny correctness tests enumerate every assignment of two matching edges in
all 64 four-vertex graphs against a literal ordered-four-tuple oracle, plus
three free edges in eight random six-vertex graphs. Separate random quadratic
objectives test branch-and-bound against exhaustive enumeration. These tests
are validation evidence, not formal proofs.

Cheap proposed screen: at a independently checked single-flip local minimum,
run size16 matching neighborhoods for a bounded 30–60 seconds per selection
method, using the same parent. Record number of distinct neighborhoods,
negative interactions, minimum single deltas, solver nodes, and exact joint
gains. A failed screen only rejects the selected-neighborhood regime. If
linear costs swamp interactions, move to overlapping-edge neighborhoods or
uphill escape mechanisms instead of increasing repetitions blindly.
