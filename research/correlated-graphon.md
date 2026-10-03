# Correlated graphon lane

## H-CG-1: centered three-state latent types

Status: supported in the tested regime. This is a mechanism test, not a record
or novelty claim.

Split each coarse class `i` into three equally weighted fine classes `(i,a)`,
where `a` is in `{0,1,2}`. On every fractional coarse block set

    W((i,a),(j,b)) = P(i,j) + epsilon K(a,b),
    K(a,b) = 2 when a=b, and -1 otherwise.

On non-fractional blocks leave `P` unchanged. The matrix `K` is symmetric,
has zero row sums, and rank two. Thus averaging either fine endpoint exactly
recovers every parent block probability. Unlike the earlier two-state
rank-one split, products of five and six perturbation edges can survive
latent averaging, so this tests genuinely different motif correlations.

Validity/realization: this is an ordinary deterministic step graphon, not an
edge-marginal specification with possibly inconsistent correlations. In a
finite blow-up, use equal fine classes and independently color every distinct
vertex edge according to its fine-block probability. Conditional independence
therefore defines an actual random red/blue coloring. If several of four
sampled vertices have the same coarse class, their fine types are nevertheless
sampled independently in the graphon integral; direct summation over all 576
fine indices retains those repeated-coarse-class terms.

Prediction: a feasible nonzero perturbation improves the simple denominator-41
parent. Cheapest falsifier: enumerate the full integer interval allowed by
`0 <= P+epsilon*K <= 1`, exactly recounting the ordered K4 objective. This uses
the readable parent to avoid duplicating the separate high-precision checking
lane. A failure retires this uniform Potts support, not all multi-type graphons.

Artifacts after execution will be under
`reports/correlated-graphon-potts-001/`. The screen's own exact C++ counter is
not an independent audit and cannot promote a candidate by itself.

## Result

The one authorized CPU job exhausted every feasible integer coordinate
`q=-9,...,4` on the denominator-41 parent. It completed in 251.1 seconds and
was reaped. The exact minimum is `q=-3`, with

    1013294138177269 / 33620705806123008
    = 0.030138990657142234...

This improves the parent by
`2164455/622605663076352 = 3.476446053...e-9`. It is also
`2116503/1245211326152704 = 1.699713900...e-9` below the earlier two-state
split on this same parent. It remains worse than the high-precision unsplit
graphon's `0.03013897728988013...`, and it has not received an independent
recount or Lean check.

The complete exact sweep interpolates to the causal polynomial

    F(q) = F(0)
         + (59119/116738561826816) q^3
         + (700081/5603450967687168) q^4
         - (37/116738561826816) q^5.

The coefficients of degrees one, two, and six vanish. At `q=-3`, the cubic
gain is `-1.367339956...e-8`; the quartic and quintic costs are respectively
`1.011993526...e-8` and `7.701825223...e-11`. The new rank-two kernel is
therefore supported because it preserves and roughly doubles the favorable
triangle response while introducing a small adverse five-edge interaction.

Candidate SHA-256:
`406164ecb9705883f3b6b8974b715f06525ea2b21695f7723515b01e71c0db83`.
The report and all feasible points are in
`reports/correlated-graphon-potts-001/report.json`.

## Recursive implication

For several independent additive latent levels, expansion terms mixing two
levels would require two edge-disjoint nonempty perturbation subgraphs of K4,
each having no degree-one latent vertex. None exists: a surviving subgraph has
at least three edges, and the complement of a triangle is a star. Thus, while
the same support mask remains fractional, the K4 density response is the sum
of the per-level cubic/quartic/quintic polynomials. This agrees with the binary
latent lane's analogous Eulerian-support observation.

This is not yet an indefinitely iterable construction. Constant `q=-3`
exhausts probability slack after finitely many levels. A convergent hierarchy
would need shrinking coordinates, or a true typed substitution/composition.
For the latter, the ordinary 11-component unlabeled four-profile is not by
itself sufficient: the transition depends on which of the six edges carry the
fractional-support mask and on their probability class. A correct finite
transfer state must refine each four-vertex colored type by these edge labels;
then averaging over the 3^4 child labels defines its linear local-profile
operator. Deriving and reducing that marked operator is the next discriminating
step before any second-level compute.

## H-CG-2: transfer to the strongest precision parent

After the centered three-state mechanism beat the binary split on the readable
parent, the coordinator authorized one bounded transfer job on the strongest
`Q=65536` parent. Two preserved attempts (`-001`, `-002`) failed during
compilation and evaluated no experiment points. The dependency-free `-003`
job completed both phases and was reaped.

Seven calibration coordinates determined the exact response polynomial. Before
any candidate recount, `preregistration.json` recorded every exact derivative
sign-change bracket and its integer neighbors, the discrete polynomial minimum
and its neighbors, zero, and the feasibility boundaries. All eleven subsequent
candidate recounts agreed with the polynomial. The minimum is

    q = -4708, epsilon = -1177/16384,
    F = 4126214370894080731270691413993
        / 136906264824648775361643946180608
      = 0.030138974108883818...

This is lower than its parent by

    145166107949516852825077
    / 45635421608216258453881315393536
    = 3.1809963145685272e-9.

Candidate SHA-256:
`bc6ff4995ea00723ec6df51d056362ddcab47c041635e612a8cf4b21fd6e8d05`.
Artifact: `reports/correlated-graphon-potts-precision-003/`.

The exact contributions at `q=-4708` are cubic
`-1.2656156476337239e-8`, quartic `+9.4045198004446903e-9`, and quintic
`+7.0640361324020963e-11`. Degrees one, two, and six again vanish. This is
exact search-counter evidence with an embedded tiny literal oracle and a
separate candidate recount phase, but both phases use the same counter. It is
not promoted pending an independent recount.

The counter's inner contraction has explicit bound
`401092572728463209067316248576 < 2^128`; its outer total has explicit bound
`17442129760689666084243756244998681526272 < 2^134` and is accumulated in a
checked 192-bit three-limb integer.

### Held recursive consequence

The edge-disjoint-support argument above applies to the Potts kernel too. It
predicts that several independent latent levels add their one-level response
polynomials exactly as long as every refined probability remains in `[0,1]`.
In particular, three levels at `q=-4708` use total negative-coordinate budget
`14124`, below the governing slack `14472`. This is a concrete unverified next
lead, not a claimed construction: per coordinator instruction, no recursive
candidate was materialized or counted before independent audit of the one-level
result. A proof/audit must also confirm that the support mask remains unchanged
at every fine level.
