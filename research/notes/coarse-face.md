# Coarse mean boundary-face screen

## H-FJ-006

The 192-class two-parameter parent has no inward first-order violation on its
18,336 off-diagonal means.  Its fractional `p` and `h` gradients are small and
orbit-uniform, while each deterministic zero/one orbit points outward.  Since
the exact one-coordinate objective is convex, a boundary coordinate with an
outward derivative cannot hide a one-dimensional barrier-crossing gain.

The first exact screen therefore moved whole regular boundary orbits.  It
tested each deterministic orbit singly and every zero/one orbit pair in the
unique integer ratio that preserves every coarse row sum.  Each line received
a 17-point full-box grid and local integer refinement.  Prediction: at least
one coherent line improves the exact objective.  Failure only rejects this
29-line symmetry-orbit bank, not arbitrary collective mean directions.

`finite-joint-coarse-face-001` evaluated 1,089 exact points in 42.97 seconds.
The parent was best on every line (exact delta zero), and the retained matrix
matched an independent direct ordered-index C++128 recount.  This falsifies
the preregistered off-diagonal bank.

### Scope audit

The first KKT/reporting pass explicitly skipped the 192 diagonal block means.
Those are positive-measure graphon coordinates: the full symmetric box has
`192*193/2 = 18,528` means, not 18,336.  The immutable result is therefore
labelled **off-diagonal only**; its numerical conclusion remains valid for
that bank.  The diagonal-inclusive companion recomputes all KKT signs, treats
the diagonal orbit as a counter parameter, and adds its single and every
row-sum-preserving zero/one paired line.  Its falsifiable prediction and exact
recount gate are unchanged.

`finite-joint-coarse-face-diagonal-001` completed the corrected screen in
49.23 seconds.  None of the boundary means had a numerically detected inward
gradient; this is a floating-point sign diagnostic, not an exact KKT
certificate.  In particular, the fractional `p` and `h` gradients remain
small but nonzero at the retained dyadic values, so continuous stationarity
does not hold there.  The 192 diagonal means form one zero-valued orbit with outward gradient
`+1030.90808838`.  The exact bank comprised 34 lines and 1,262 evaluated
points.  The parent again remained best with exact delta zero, and the
partition count matched the independent direct ordered-index recount.  This
rejects the sampled points on the regular gradient-orbit singles and every
zero/one orbit pair in the bank, including the diagonal orbit.  It does not
prove line-global optimality between sampled dyadic points and does not reject
higher-dimensional collective directions, non-regular supports, or a changed
outer quotient.

The corrected report SHA-256 is
`7c07a1a96b04c0d625ce85c1d899ca3a9885c18ac56803fa22ed0beabd23750b`;
the retained (unchanged parent) candidate SHA-256 is
`db81e3ed2ad91da4c32181776bf7789abac33725149d107bd76a79a6f3903d68`.
