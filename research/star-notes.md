# H2: shared-endpoint swaps after matching obstruction

2026-09-27, own derivation; no novelty claim. H0's single-flip local minimum
had no improving disjoint pair: exact necessary-cost screening exhausted 566
pairs (`reports/pilot-h1-pair-001`). This motivates changing interaction
geometry, not repeating the same matching screen.

For free edges uv and uw, let c be the fixed color of vw and let t be the
number of vertices x simultaneously joined to u,v,w by color c. The mixed
finite difference is

    b = sign * (36 * [c is blue] + 24 * t),

where sign is +1 if uv and uw have the same original color and -1 otherwise.
The triangle term supplies 36; every distinct fourth vertex supplies a K4
term of 24. Edge-count terms are linear. Thus overlapping opposite-color
pairs can have interactions much larger than the disjoint bound of 24.
Three bitset intersections compute t. The exact gain is a_uv+a_uw+b.

The prototype screens low-single-cost red and blue incident edges, together
with a random sample of higher-cost edges, at every center. Flipping one red
and one blue edge preserves the center's degree, but alters endpoint degrees.
This is a two-edge star neighborhood, NOT an exact multi-edge cubic solver.
Every accepted interaction is cross-checked using native finite differences;
the resulting numerator is fully recounted, then the final artifact is sent
to the runner's independent Lean check.

Prediction: some shared-center pair at the H0 local minimum admits a strict
decrease even though no disjoint pair does. Cheapest test: 30–60 seconds,
per_color16, random_per_color4, same H0 parent. Record the initial minimum
single cost to distinguish escape from ordinary uncompleted descent.
Failure only rules out the screened pairs, not all adjacent pairs or stars.

Validation: all 64 four-vertex graphs, all four assignments of a two-edge star,
compared with a literal ordered-four-tuple oracle; all ordered triples in
12 random six-vertex graphs compared with exact native finite differences.
