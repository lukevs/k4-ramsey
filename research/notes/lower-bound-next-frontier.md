# What could reach the published frontier after the N7 pilot?

Parent synthesis, 2026-09-30. Current work is universal lower-bound research,
not upper construction search. No new frontier improvement is claimed.

## Evidence against expecting interval refinement alone to reach 0.0296

The automated pilot's fixed triple profile (1/8,3/8,3/8,1/8), with all disjoint
triple products imposed, has a near-feasible numerical moment point of objective
0.0292853415. Residuals are around 1e-9, but no exact primal certificate exists.
This suggests limited headroom for that relaxation; it is not a rigorous ceiling.

A cheap screen of all eleven four-vertex types against all four disjoint triple
types (44 products, still on seven vertices) found maximum discrepancy only
1.19e-7 at that point; red/blue K4 discrepancies are about 3e-8 or less. In the
old N7 control the largest discrepancy was 5.48e-4. Thus the stronger diagnostic
already nearly satisfies these cheap additional equations. These coefficients
have not been independently audited, and no constrained solve was done: this
is evidence for deprioritizing the route, not a redundancy theorem.
See reports/mixed-motif-screen-001/result.json and its coefficient data.

## Priorities

1. Use relations between TWO four-vertex patterns. These directly involve
   the optimized motifs and require eight vertices for disjoint products.
   Start with a selective shared-variable N8 extension that preserves the
   current N7 blocks and includes the chosen mixed moments. Benchmark a
   matched control before proposing a larger campaign.
2. Recover and reproduce the calculation behind the stronger published lower
   frontier. A small-baseline gain cannot be added numerically to someone
   else's bound. The new constraints must strengthen the stronger relaxation
   itself, and the combined dual must pass exact checking.
3. Address scalability explicitly: sparse coefficient storage, selected blocks,
   symmetry that preserves the case being proved, and reusable solves. Earlier
   N9 recovery did not obtain a reproducible frontier certificate locally;
   naive dense formulations were beyond the established memory plan.

Do not assume a colour-averaged baseline can simply be reused unchanged with
nonlinear independence cuts. Averaging a graphon's moments with its complement
preserves a convex flag relaxation and the objective, but can destroy product
factorization. Our current method only reorients a graphon by colour complement;
it does NOT assume p1=p2. A higher-order implementation must preserve that
quantifier distinction, even if it costs more variables.

Optimizer-only conditions are another possible source of constraints, but the
specific low-order stationarity and edge-optimality tests already failed to
improve earlier baselines. Revisit them with a new coupled mechanism, not as
an untested generic suggestion. No branch or mathematical technique guarantees
an improvement past the published bound.
