# Common nonuniform latent weights on the b93 candidate

Date: 2026-09-27.  This screen freezes every probability in the independently
recounted 960-class b93 candidate and changes only the common mass vector of
its five microtypes inside each of the 192 equal coarse groups.

The candidate-bound typed certificate has 10 distinct 5-by-5 kernels and
28,272 coarse six-kernel signatures.  For each signature, enumerating all
`5^4` ordered microtype assignments and grouping by the five type
multiplicities produces the complete 70-monomial homogeneous quartic in the
mass vector.  Each term uses the full product of the six red probabilities
plus the full product of the six complementary probabilities.  Thus this is a
recomputation of the whole objective, not a reuse of the centered-kernel delta
polynomial.  Repeated coarse indices retain their original histogram weights.

A separate tiny base-order-two, type-order-three fixture with unequal integer
masses, arbitrary diagonal kernels, and repeated base indices matched literal
enumeration of the replicated equal-mass classes exactly.

At uniform masses the numerical quartic evaluation is
`0.030138904006339624`, within `2.1e-15` accumulated floating error of the
independently verified exact `0.030138904006337588`.  All five gradient
coordinates equal `0.12055561602535848`; the simplex-projected gradient norm is
`1.39e-17`.  A deterministic numerical tangent-space Hessian search found a
smallest observed Rayleigh quotient `4.0217006923e-5`.  The implementation
uses 200 pseudorandom tangent starts followed by normalized descent; it is not
a complete eigensolve and carries no interval or exact-arithmetic error bound.
It is therefore evidence for positive local curvature, not a proof that the
Hessian is positive definite in every mass-preserving direction.

Twelve 4,000-step softmax-Adam trajectories returned uniform weights to about
`2e-13`.  Their apparent `5e-17` objective change is below floating precision
and accompanies no displacement.  Every nonnegative integer mass vector with
total at most 16 was enumerated, including boundary vectors that delete
microtypes, and the `long double` evaluation selected
`[1,1,1,1,1]/5`.  This is exhaustive coverage of that rational grid but not an
exact-arithmetic comparison; the report gives no separation margin with which
to turn it into a certificate.  The separate tiny replicated-class oracle is
exact for its fixture, but it does not make the 960-class grid comparison
exact.

Decision: stop this common-mass lane as a well-covered numerical negative.  No
first-order direction, negative local curvature, or small rational/boundary
improvement was found.  This is not a convexity proof or a certified global
minimum.  It also does not test base-dependent microtype masses, simultaneous
probability/mass motion, or a different latent kernel.

Evidence: `reports/latent-weights-001/report.json`.  Input certificate SHA-256
`730606d4c91ea92cbdb58f4d157797fa923af20cceb847800cd006d4b583b434`.
Screen source SHA-256
`1a5725e31cc8abc6f14f1fc6cceb9b674f4a22a1e02735055e1842bb863bad19`.
