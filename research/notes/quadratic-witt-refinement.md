# Second-order Witt-pair refinement of the quadratic basin

Date: 2026-09-27.  This experiment starts from the exact rational nonsplit
quadratic/Hamming baseline `a26ecda...` and refines its relations according to
the Witt decomposition.  A binary difference is classified by its exact first
two-bit symbol and the unordered multiset of its other two two-bit symbols;
together with the Z3 zero/nonzero orbit this gives 80 relations.  It strictly
refines the old `(Z3 orbit, Hamming weight, Q-)` family while retaining the
swap symmetry of the last two hyperbolic pairs.

The translated-triple census has 7,077,888 states compressed to 81,840
repeated six-relation signatures.  The lifted parent matched its exact known
density, componentwise complementation left the objective unchanged, and an
independent literal translated enumeration matched the compressed objective.

The first-order gate was exactly negative: among the 16 refined children of
realized fractional old relations, the largest mass-normalized gradient after
subtracting the old-orbit mean was only `5.56e-19`.  Thus the refinement does
not reveal a linear symmetry-breaking direction.

The collective second-order gate was positive.  The subspace preserving every
old relation's mass-weighted mean has dimension ten.  Its restricted Hessian
has minimum eigenvalue `-2.1833638816511427e-5` in the recorded basis.  A
deterministic step along that eigenvector lowered the objective by
`1.6242560716e-7`; subsequent constrained descent reached
`0.030140295692077351` numerically.  This separates the mechanism from the
previous dyadic-rounding residual: it is a genuine collective second-order
split with every old relation mean fixed.

The continuous Hessian step and descent preserve every old relation mean.
Independent rounding of the 80 children to denominator 65,536 does not quite
preserve that constraint: old relation 5 has weighted numerator residual `+1`
across 11 difference-elements, a mean shift of `1/(11*65536)`; every other old
relation has zero residual.  With that explicitly weakened rational scope, the
rounded point has exact search-model density

    16901715161505423885044215944464856
    / 560768060721761383881293603555770368
    = 0.030140295686154409...

This improves the quadratic parent by `3.25370e-7`, but remains approximately
`1.39212e-6` above the campaign best `0.03013890356539909`, so it is retained
as a mechanistic baseline rather than promoted.  The explicit 192-class
candidate is `reports/quadratic-next-002/graphon-candidate.json`, SHA-256
`87da15c83bc3477da3c467610a26dd93c92e6fe663a7480adce58ccfd2a8744a`.

Scope: the continuous optimization preserves all old relation means and the
chosen pair symmetries; the serialized dyadic point has the single rounding
residual above.  It does not test simultaneous old-mean motion, ordering the
last two hyperbolic pairs, larger Witt dimension, or unrestricted blocks.  The
candidate remains unpromoted and has not received a fresh candidate-only
independent recount.

## Maximal fixed-group Cayley refinement

A follow-up removes the final pair-order symmetry and assigns a probability to
every exact binary difference, retaining only the necessary Z3 zero/nonzero
orbit.  These 128 relations are the maximal symmetric translation-invariant
family on the fixed group `Z3 x F2^6`.  The 7,077,888 translated states compress
to 162,208 signatures; matched-parent, literal-translation, and complement
controls pass.

The first-order split is again flat (`3.59e-19` maximum centered residual), but
the 12-dimensional old-mean-preserving Hessian again has negative curvature:

    minimum basis-coordinate eigenvalue  -2.2002025815159347e-5
    Jacobi terminal off-diagonal          5.3823145738553898e-19
    eigenpair residual infinity norm      3.3447261357124577e-19

The retained dyadic point has exact search-model density

    16901604713711361968764487837017176
    / 560768060721761383881293603555770368
    = 0.030140098728086213...

This gains another `1.96958e-7` over the 80-bin point and `5.22328e-7` over the
original quadratic parent, but remains `1.19516e-6` above the campaign best.
The explicit candidate is
`reports/quadratic-full-cayley-001/graphon-candidate.json`, SHA-256
`d5b957fca6aa1335375f944c4bc64c30ea7f88d02dd5e4adee58cb03746fcf44`.

This exhausts relation refinement only for the fixed group under translation
and the undirected Z3 orbit.  The negative result relative to the incumbent is
not a ceiling for larger groups, non-Cayley step graphons, unequal masses, or
iterated constructions.
