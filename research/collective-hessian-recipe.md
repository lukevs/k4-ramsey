# Implementation recipe: collective Hessian escape on 1,248 fractional means

Date: 2026-09-27. This is an implementation handoff for H-TR3-2. It uses the
192-class precision parent and changes its fractional **coarse probabilities**;
it does not split classes or preserve each coarse mean.

## Reusable components

- Parse and validate the parent exactly as in
  `experiments/latent_precision/latent_precision.py`.
- Reuse the objective/gradient contraction organization in
  `experiments/literature/graphon_gradient.cpp`; add an exact signed-128
  gradient mode before trusting equality classes.
- Reuse the Hessian accumulation pattern from
  `experiments/quadratic_next/screen.cpp`, but the new coordinate set is the
  1,248 unordered fractional pairs, not relation bins.
- Use `experiments/latent_precision/ordered_graphon_cppint.cpp` for exact
  recounts on seven line coordinates.
- Use `interpolate_integer_polynomial` from
  `experiments/compressed_graphon/polynomial.py` with the explicit external
  proof that six affine edge factors give degree at most six.

Do not modify the shared checker. A new driver and proposal binary should live
under a fresh experiment/report directory.

## Coordinate list and exact first-order gate

Let `E` contain every unordered off-diagonal pair `{i,j}` with
`0<P_ij<Q`; here `|E|=1248`. Store `id[min(i,j),max(i,j)]` and also the two
oriented incidences `(i,j,id)` and `(j,i,id)`.

Upgrade the existing gradient contraction to integer input. For an unordered
off-diagonal coordinate `{i,j}`, its raw gradient is

    g_ij = 12 sum_{k,l}
      [P_ik P_jk P_il P_jl P_kl
       - B_ik B_jk B_il B_jl B_kl],                         (1)

where `B_uv=Q-P_uv`. Five factors and `192^2` terms fit signed 128 bits at
`Q=65536`, but retain an explicit bound in the report.

Group coordinates by their **exact** integer gradient, optionally refined by
parent probability. Only after this check may the expected two constant `p/h`
gradient classes be used. A sufficient exact-neutral constraint is

    sum_{e in each exact gradient class} D_e = 0.            (2)

Then `sum_e g_e D_e=0` exactly. This avoids assuming that a visually regular
`p` or `h` set is a complete automorphism orbit.

## Inexpensive dense Hessian proposal

It is unnecessary to enumerate `192^4` tuples. By positional symmetry, the 15
pairs of `K4` edges split into 12 adjacent pairs and 3 disjoint pairs. For a
symmetric direction `D`, the raw coefficient of `t^2` in `F(P+tD)` is

    C2(D) = 12 Adj(D) + 3 Dis(D),                            (3)

with

    Adj(D) = sum_{i,j,k} D_ij D_ik Z(i,j,k),

    Z(i,j,k) = P_jk sum_l P_il P_jl P_kl
             + B_jk sum_l B_il B_jl B_kl,                   (4)

and

    Dis(D) = sum_{i,j,k,l} D_ij D_kl
      [P_ik P_il P_jk P_jl + B_ik B_il B_jk B_jl].          (5)

Set `D_uv=0` outside `E`. Equations (3)--(5) retain all repeated coarse indices;
there are no distinctness tests.

Build a dense double proposal matrix `C` of size `1248 x 1248`:

1. For each base vertex `i`, loop over its oriented fractional incidences
   `(i,j,e)` and `(i,k,f)`. Compute (4) by summing all 192 values of `l`, then
   add `12*Z` to `C[e,f]`. There are only about
   `192*13^2*192` scalar inner operations.
2. Loop over all pairs of the 2,496 oriented fractional incidences
   `(i,j,e),(k,l,f)` and add three times the bracket in (5) to `C[e,f]`.
3. Check `C` is symmetric within floating tolerance. For random small `D`,
   compare `D^T C D` with a direct implementation of (3)--(5).

`D^T C D` is the raw quadratic coefficient; the second derivative is twice
this value. Only its sign matters in the proposal stage.

## Projection and negative-mode proposal

Project vectors by subtracting their mean separately inside every exact
gradient class from (1). This enforces (2) in floating arithmetic. Because a
plain list of 192 transporters was shown not to be a group, do not use an
abelian Fourier transform.

The later orbital certificate
`reports/group-recovery-orbitals-001/report.json` supplies a genuine full
quotient automorphism group of order 46,080 with point stabilizer 240 and five
unordered fractional-edge orbits of sizes `480,96,480,96,96`. This can be used
only after checking its recorded hashes and exact reconstruction. It justifies
that the Hessian commutes with the certified permutation action; it does not
justify treating the five orbit-constant directions as the whole space. Those
constant directions largely overlap earlier orbit-line tests. The first
collective screen should therefore retain all 1,248 coordinates; a later exact
isotypic reduction may use the certified generators if needed.

A dependency-free minimum-mode proposal can use shifted power iteration:

1. Let `alpha` be the maximum absolute row sum of the projected symmetric
   matrix, an upper bound for its largest eigenvalue.
2. Iterate `v <- project(alpha*v-C*v)` from several deterministic hash-derived
   starts, normalizing after every step.
3. The largest eigenmode of `alpha I-C` corresponds to the smallest eigenmode
   of `C`. Record every Rayleigh quotient and retain only a clearly negative
   proposal.

Lanczos is also acceptable. Floating negativity is proposal evidence only.

Convert the best vector to a small integer direction:

- subtract each exact-gradient-class mean;
- scale maximum magnitude to 32 or 64 and round;
- within each class, correct the rounded sum to zero by distributing unit
  changes to entries with the appropriate largest rounding residual;
- divide the final direction by its gcd;
- verify (2) and `sum g_e D_e=0` with exact integers.

Try a small preregistered bank of scale/rounding choices; do not run an
unbounded direction search.

## Exact curvature and full-line certificate

For each integer direction, compute the complete feasible integer interval

    0 <= P_e + q D_e <= Q

over every `e`; unchanged entries impose no constraint. Require at least seven
distinct feasible `q` values. If necessary reduce the direction scale before
sampling—do not silently change the denominator merely to fit interpolation.

At seven distinct feasible coordinates, materialize the 192-square matrix and
run `ordered_graphon_cppint.cpp`. Interpolate the exact total numerator

    N(q)=c0+c1 q+...+c6 q^6.                                (6)

Required gates:

- `c0` equals the immutable parent numerator;
- `c1=0` exactly;
- `c2<0` exactly for a true negative-curvature certificate;
- at least one additional feasible holdout recount agrees with (6);
- the chosen minimum is obtained by exhaustive evaluation over the finite
  feasible integer interval, then separately recounted from the materialized
  matrix.

The exact polynomial, not the floating Hessian, is the evidence. If rounding
destroys negative curvature, try the remaining preregistered quantizations and
then report failure.

## Tiny controls and complexity

Before the production parent, compare (3)--(5) with literal ordered-quadruple
degree-two coefficients on symmetric matrices of orders 2--4. Use a tiny
dual-number/polynomial product or interpolate the entire degree-six literal
polynomial; a central second difference alone also contains the degree-four and
degree-six terms. Include repeated indices, a diagonal coordinate in the
literal control even though production `D` is off-diagonal, an order-three
adjacent `+1/-1` direction, an order-four disjoint-pair direction, and cases
where the same coordinate occurs in two positional slots. Also check complement
invariance under `(P,D) -> (Q-P,-D)`.

Expected proposal work is roughly 6.2 million disjoint-incidence pairs plus
6.2 million adjacent inner products, a 12 MB dense double matrix, and tens of
1.56-million-entry matrix-vector products. Seven exact 192-class recounts are
small compared with a 960-class recount. No recursive materialization or new
Lean program is needed for the discriminator.

## Decision rule

- `c1=0,c2<0` and an exact lower line point supports the collective escape and
  yields an immediately valid rational step graphon.
- No negative exact direction in the bounded proposal bank is weak negative
  evidence only.
- An exact PSD certificate for the entire projected 1,248-coordinate Hessian
  would retire the local quadratic mechanism, but the shifted-power screen is
  not such a certificate.

## First implementation audit and restricted results

The five certified fractional-edge orbits have sizes `480,96,480,96,96`.
Exact relation derivatives show that the four `p` orbits have the same
per-unordered-edge gradient:

    g0 = g2 = 5 g1 = 5 g4,
    |O0| = |O2| = 5|O1| = 5|O4|.

The `h` orbit has a different gradient. Thus the weighted-zero `p` row is
exactly first-order neutral, while freezing `h` is required for that
classwise-neutral restricted screen. The resulting three-dimensional
orbit-constant Hessian had floating minimum eigenvalue `+2.238102e-5`; the
unconstrained five-orbit block had floating minimum `+1.699124e-5`. Neither
produced a denominator-`Q` exact improvement. These are numerical restricted
results, not exact PSD certificates; the free run found a small continuous
improvement which was not retained after denominator-`Q` rounding.

The first full-coordinate implementation independently reconstructed exactly
two gradient classes, `1152` `p` edges and `96` `h` edges. Source inspection
confirmed the factor-`12` unordered gradient, oriented-incidence realization
of (3)--(5), repeated-index semantics, and the literal tiny controls. Its first
bounded Lanczos proposal returned positive Rayleigh quotient about `386.34`
with residual about `134.47`; this is only a failure to propose a negative
mode, not evidence of positive semidefiniteness.

That first report is not a promotion artifact: it records a source hash whose
file was subsequently changed and did not copy an immutable source snapshot
into its report directory. A rerun must snapshot and hash the exact source and
binary before execution. It should also state the decomposition scope. The
classwise-zero space has dimension `1246`; the compensated global `p/h`
first-order-neutral direction is excluded. The certified automorphism action
can separate the five-dimensional orbit-constant invariant block from its
orthogonal complement, but only after the report explicitly checks parent and
Hessian equivariance under the hashed generators. Without that check, the two
screens cannot be presented as an exhaustive block decomposition.

## Final full-coordinate spectral gate

The reproducible rerun is
`reports/collective-hessian-proposal-005/report.json` (SHA-256
`8a24a2cd4687dbe4bc8d09ceaeefd50576fd15b42ea85736c47a602a9784f2a9`).
It snapshots both the exact source and binary. Before the production run, the
production-style dense incidence assembly itself was compared with literal
ordered-quadruple coefficients on deterministic order-2, order-3, and order-4
directions; the earlier symbolic, repeated-index, and complement controls also
passed.

The run explicitly formed the projected matrix `P C P` and used Accelerate's
symmetric `DSYEVD` eigensolver. Its two class-constant null
eigenvalues were numerical zero (`-2.51e-12`, `1.02e-10`). The least
classwise-zero eigenvalue was `+41.16176167949167`, with eigenpair residual
`1.17e-11` and maximum class-sum residual `3.13e-13`; the next eigenvalue was
about `286.16`. Thus no negative integer direction or exact line recount was
attempted. This is strong numerical positive-semidefiniteness evidence on the
1,246-dimensional classwise-zero subspace, not an exact PSD certificate. It
does not cover the compensated direction that transfers total mass between the
`p` and `h` gradient classes. Production compute took 0.403 seconds and the
fresh compile/setup-to-gate path took 1.506 seconds; implementation and audit
setup took roughly eight minutes.

The stronger codimension-one rerun is
`reports/collective-hessian-proposal-006/report.json` (SHA-256
`31ee394d916b1d26be8e962fa56859521b40866f0d4ad31308bdedcca79fe201`).
It projects orthogonally to the complete exact gradient vector, rather than
separately zeroing its two constant-gradient classes. This includes the
previously omitted compensated `p/h` direction and covers the full
1,247-dimensional first-order-neutral tangent. The sole projected null
eigenvalue was `2.16e-10`; the least tangent eigenvalue was
`+41.16176167949171`, with eigenpair residual `3.22e-11` and normalized
gradient-dot residual `1.95e-14`. Projector annihilation, idempotence, and
projected symmetry residuals were respectively `1.80e-14`, `6.94e-18`, and
`5.68e-14`. Source, driver, and binary are snapshotted, and the recorded
Accelerate/OMP/OpenBLAS thread limits are all one. This is strong numerical
positive-semidefiniteness evidence for every first-order-neutral fractional
mean direction, but remains a numerical rather than exact PSD certificate.

The orbit-constant part also has an exact companion certificate:
`reports/collective-mean-five-orbit-global-neutral-exact-001/audit.json`
(SHA-256 `088f8513a5be888ad508d6a7ce474d322f1d7803a387fcd4f21cdf5b5c6e19dd`).
It appends the primitive compensated `p/h` vector, obtained by dividing the two
exact gradient values by their gcd `2,359,296`, to the three `p`-redistribution
vectors. All four exact gradient contractions vanish, and the four leading
principal minors of the exact restricted Hessian are positive (bit lengths
`86,169,249,455`). Sylvester's criterion therefore proves strict positive
definiteness on the complete four-dimensional gradient-neutral tangent inside
the five orbit constants. This exact statement does not extend to the
nonconstant part of the 1,248-coordinate space; that part still has only the
strong numerical spectral evidence above.
