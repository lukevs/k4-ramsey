# Coarse deterministic-support alignment

## H-FJ-005

Hold the two optimized fractional probabilities and their support fixed.  The
fractional support has three64-class components.  For one component at a time,
permute only its deterministic cross-component incidence by one of the two
intrinsic perfect-matching involutions (`H`, the half-block matching, and `M`,
the96 softened-complete blocks) or their two compositions.  This changes many
deterministic0/1 blocks while leaving the internal fractional component fixed.
It therefore changes relative motif alignment rather than tuning p/h or adding
a centered latent kernel.

Prediction: at least one structural relative alignment reduces the exact
ordered graphon objective.  One random fixed-point-free involution per
component controls for moved-vertex count, while a full relabeling of one
component is an exact no-change control.  Failure is limited to this15-member
bank and does not establish support local optimality.

For `U=2P-1`, expansion of the two monochromatic products gives

    32 F = 1 + 12 t(P3,U) + 3 t(K2,U)^2
             + 12 t(paw,U) + 3 t(C4,U) + t(K4,U).

In integer numerator form with probability denominator `Q`, the bracket is

    n^4 Q^6 + 12 Q^4 T_P3 + 3 Q^4 E^2
      + 12 Q^2 T_paw + 3 Q^2 T_C4 + T_K4.

Thus row-sum-preserving macro moves fix the first two nonconstant terms and
trade signed paw/C4/K4 densities.  Tiny arbitrary rational matrices compare
this even-subset expansion with direct six-edge products.  Candidate counts
use the already audited direct ordered-index C++ counter, not the identity.

## Result

`finite-joint-coarse-alignment-001` finished in4.62 seconds.  Every H, M,
H-after-M, and M-after-H relative alignment changed4096 unordered deterministic
blocks, preserved every row sum, and had **exactly zero objective delta** in
all three components.  These structural involutions are therefore objective
symmetries in this test, not new template directions.  The three matched
random involutions also preserved row sums but all worsened the objective by
roughly3.76e34 raw denominator units.  Decision: retire this permutation bank;
the contrast says preserving degrees alone is far too weak, while the named
matchings only move inside an isomorphic/gauge orbit.

The immutable report's `isomorphism_control` descriptor incorrectly names the
last loop proposal (`component2/random_involution`) because Python loop
variables overwrote the saved labels before serialization.  The matrix
actually counted for that control was the preregistered first proposal,
`component0/H`, with the internal component relabeled as well.  Its exact
count equals the parent.  Candidate records and numerical results are
unaffected; the adjacent metadata audit records this correction.
