# Structural scale audit: centered refinements versus quotient changes

Date: 2026-09-27. This is a no-search analysis of the current 192-class
precision parent and its five-state cyclic refinement. It does not assert an
impossibility for arbitrary centered kernels. It gives a rigorous relaxed
envelope for the **fixed cyclic kernel, scalar amplitude, phase/support**
family used by `association-scheme-phase-001`, then identifies which modeling
restriction must change to seek a materially larger gain.

## Why the present corrections start at degree three

Write a refined block as

    W_ij(x,y) = P_ij + q K_ij(x,y) / Q,

with every row and column of `K_ij` summing to zero. In the six-edge expansion
of the monochromatic `K4` functional, summing a fine type at a positional
vertex kills every selected perturbation subgraph having a degree-one vertex.
The only surviving nonempty edge subsets of positional `K4` are therefore a
triangle, `C4`, diamond, and `K4`, of degrees 3, 4, 5, and 6. In particular,
the construction deliberately freezes all coarse block means and discards the
linear and quadratic response of the 192-class quotient.

For the current phase-optimized candidate, normalized contributions at
`q=-5496` are

    degree 3:  -6.99800478356379e-8
    degree 4:  +5.16016853102290e-8
    degree 5:  +7.22878742769311e-10
    degree 6:  -1.40560439874581e-11
    total:     -1.76695398266270e-8.

The phase/support search barely changed the favorable triangle coefficient:

    c3_phase / c3_control = 143/144 = 0.9930555555...,

but reduced the adverse four-cycle coefficient to

    c4_phase / c4_control = 0.4657811961....

That explains the gain: phase frustration mostly decoupled the `C4` cost from
the triangle response. It also shows the remaining scale. If every adverse
degree-4 and degree-5 term disappeared while the observed cubic coefficient
were kept, moving all the way to the feasibility boundary `q=-7236` would
gain only `1.5971e-7` (plus the negligible favorable degree-six term).

## Exact relaxed envelope for the common-amplitude phase/support family

The kernel is

    kappa(d) = 3 for d = +/-1 mod 5, and -2 otherwise.

For a connected selected motif, vertex-potential gauge transformations reduce
the phase dependence to its cycle holonomies. Fixing a spanning tree to phase
zero and exactly summing the `5^4` positional microtypes gives these complete
sets of raw moments:

    triangle: {-5000, -1875, 4375}
    C4:       {-6875,  2500, 8750}
    diamond:  {-6875, -3750, -625, 2500, 5625, 8750}
    K4:       {-15000, -2500, 625, 3750}.

This is a finite identity: only `5`, `5`, `25`, and `125` gauge-inequivalent
holonomy assignments respectively need checking. It can alternatively be
derived from the two nonzero Fourier eigenvalue pairs of the circulant kernel.

The immutable coarse factorization has the following sums of absolute factor
weights before inserting micro-moments:

    S3 = 6,529,004,621,732,118,528
    S4 = 1,030,493,629,601,280
    S5 = 12,851,426,304
    S6 = 13,824.

Every degree-3, degree-4, and degree-6 factor weight is nonnegative; degree 5
has signed sum `-1,644,088,320` but the displayed `S5` is its absolute sum.
Deactivating support edges only removes factors, so these remain coefficient
bounds for every support subset. The first envelope below retains the common
feasibility interval `[-7236,4824]` used by the full-support phase family. It
does not cover reoptimizing a larger amplitude after deleting every tight
`p=51064` block.

Let

    D = 960^4 * 65536^6
      = 67,292,167,286,611,366,065,755,232,426,692,444,160,000.

For negative `q`, favorable cubic response requires a positive triangle
moment, whose exact maximum is only `4375`; the other degrees are bounded by
absolute moments `6875,8750,15000`. Since `|q|<=7236`, every phase/support
assignment in this fixed family satisfies the relaxed bound

    F(P) - F(refinement)
      <= [4375 S3 x^3 + 6875 S4 x^4
          + 8750 S5 x^5 + 15000 S6 x^6] / D
      at x=7236
      = 4.830527863734297e-7.

The four terms are respectively

    1.608259746601731e-7,
    2.886341612912822e-7,
    3.315031489958042e-8,
    4.423355223939876e-10.

For positive `q<=4824`, use the negative triangle extreme `-5000`; the
corresponding envelope is smaller, `1.158780514836258e-7`.

These bounds relax all global phase-consistency constraints and let every
motif choose its best moment independently, so they are genuine upper bounds,
not predictions of attainable values. The negative-side bound is about 27.3
times the achieved `1.77e-8`, but only 4.83% of a `1e-5` improvement. Thus a
`1e-5`-scale target cannot be reached by more coordinate descent, restarts,
support toggles, or amplitude tuning inside this common-amplitude interval.

### Larger typed-feasibility envelope

If amplitudes are allowed to differ by fractional block type, exact entrywise
feasibility gives

    q_p in [-7236,4824]   for p=51064,
    q_h in [-11671,10173] for h=35015.

Thus a construction supported only on `h` blocks can leave the uniform
`|q|<=7236` box. A second, more conservative envelope assigns every occurrence
of a `p` edge magnitude `7236`, every `h` edge magnitude `11671`, takes the
largest absolute moment for each motif, and again lets every factor choose its
sign independently. Summing the immutable exact factors gives

    degree 3: 2.964542288966091e-7
    degree 4: 4.096410383935160e-7
    degree 5: 6.066867874053703e-8
    degree 6: 1.150723120684099e-9
    total:    7.679146691513463e-7.

This covers arbitrary signs, phases, support subsets, and two separate scalar
amplitudes within those typed boxes. It is still only 7.68% of a `1e-5` gain.
The conclusion still does **not** cover another kernel with larger normalized
moments, a separate amplitude for every block, noncentered blocks, or a changed
parent.

## Representation change with the best scale argument

The next primary hypothesis should be a **noncentered coarse-mean/support
move**, optionally followed by an internal kernel, rather than another phase
run. The parent has only 1,248 fractional unordered blocks out of 18,336; all
current centered perturbations are confined to that degree-13 support and
cannot touch the many probabilities at zero or one.

For every unordered coarse pair **including `i=j`**, compute the exact
derivative `g_e` of the 192-step objective with respect to its mean
probability. There are `192*193/2=18,528` symmetric block coordinates. A
step-graphon diagonal block `I_i x I_i` has positive measure and controls
edges between distinct vertices in the same class; it is not the measure-zero
pointwise graphon diagonal. The box tangent cone gives an immediate exact test:

- at `P_e=0`, only `d_e>=0` is allowed, and `g_e<0` is linear descent;
- at `P_e=1`, only `d_e<=0` is allowed, and `g_e>0` is linear descent;
- at a fractional block, both signs are allowed, so a true constrained local
  optimum requires `g_e=0` unless equality/orbit constraints are imposed.

The two-parameter optimization of common `p,h` checks only two aggregate
directions; it does not establish these 18,528 KKT conditions. A violating
bounded edge orbit changes the objective at degree one, which is qualitatively
larger than the present cubic response. If all first-order conditions pass,
construct exact zero-first-derivative paired directions (soften selected zero
blocks inward while softening selected one blocks inward) and test the
projected Hessian. A negative feasible quadratic direction is still a larger
mechanism than a degree-three centered split.

A compact representation is preferable to 18,528 free variables: partition
coarse pairs by the existing Cayley/product difference coordinates and assign
one mean `mu_r` per orbit. Then use

    W_ij(x,y) = mu_orbit(i,j) + q_orbit(i,j) K_phase(i,j)(x,y),

with exact entrywise box constraints. This simultaneously:

1. moves the deterministic `0/1` support inward where the tangent cone favors
   it;
2. changes which coarse triangles and four-cycles exist, instead of merely
   changing their micro-moments;
3. retains the successful internal phase mechanism after a better outer
   quotient has been found.

The compressed typed-block evaluator already handles this representation; no
new counting convention is required.

### Cheapest decisive falsifier

Before a large search, evaluate a preregistered orbit basis:

1. exact gradient and box-KKT signs for every orbit;
2. exact projected Hessian on the KKT-neutral subspace;
3. for the best one or two feasible directions, the complete exact degree-six
   line polynomial and its box-constrained minimum;
4. only if one line improves materially, add the centered five-state kernel
   and optimize means and internal moments jointly.

If all orbit KKT signs pass and the projected Hessian is positive semidefinite,
that falsifies this particular quotient-orbit basis, not all noncentered
graphons. The next escalation would be a new outer quotient or true nested
profile substitution, because the fixed 192-class quotient would then have
survived both its coarse mean directions and the bounded centered family above.

Post-audit update: `finite-joint-coarse-kkt-001` was superseded by the full
18,528-coordinate check, including all 192 diagonal-zero blocks. Every box-KKT
sign passes; the diagonal orbit gradient is positive, so moving those zeros
inward is not first-order descent. An exact 34-line orbit bank, including the
diagonal line and all tested zero/one row-sum pairs, also retained the parent as
its minimum over 1,262 exact points. This falsifies regular one-orbit and tested
two-orbit boundary-face moves, not collective high-dimensional escapes or a new
quotient.
