# Adversarial audit of the round-three structural lanes

Date: 2026-09-27. This note separates exact artifacts from numerical screens
and classifies whether each lane changes the mathematical representation or
only chooses another direction inside an existing family. The unpublished
comparison mentioned by the user remains unknown; the only public benchmark
used here is the rounded January 2026 statement.

## Canonical 384-class pair refinement

Run 003 passes the corrected implementation gates. The newly discovered
ordered fiber list equals the immutable quotient fiber list exactly. Each
four-vertex fiber is split by its unique degree-two mate into two pairs. For a
pair-cell block the seed density is the ordered edge count divided by four,
including the two self slots on a diagonal pair block. This is the correct
conditional-expectation step-graphon convention; it is not the
without-replacement edge density and it is not an exact finite-K4 quotient.
Edges in the resulting graphon are independent by definition.

The direction on every old block sums to zero, amplitude zero duplicates the
192-class parent exactly, all repeated 384-class indices remain in the ordered
count, and the feasible interval is checked entrywise. The selected amplitude
is `123/256`. The frozen candidate SHA-256 is
`08798b82fc1b22c0fdd0bab3294a000bd21a5103254baa7ae407d17708e0dacc`,
with exact internally recounted density

`515776638127812641542888831097 /
17113283103081096920205493272576`

or approximately `0.030138964862619`. It improves its `e26e...` parent but is
worse than the independently checked `d476...` incumbent.

The initial run failed because Python's `math.comb` does not implement the
generalized binomial coefficient at negative interpolation arguments. Run 002
fixed that arithmetic. Run 003 additionally replaced floating ceiling
division, bound the discovered fibers to the stored ordering, and checked the
pair relabeling exactly. The report SHA-256 is
`693918ace912098c40afd056217362ebefeb038e5d181e84f673f4c5b09dde8c`.

**Representation classification.** Every centered `2x2` child-block direction
has zero row and column sums and is therefore a scalar multiple of
`[[1,-1],[-1,1]]`. Consequently this is algebraically a binary rank-one latent
`+/-` perturbation `P_ij + epsilon s t C_ij`. Its contribution is a useful new
canonical, seed-derived heterogeneous `C`, but it is not a new latent-kernel
mechanism. A negative result rejects only this one common-amplitude direction.

## Witt-pair refinement of the quadratic basin

The 80-bin relation records the exact first hyperbolic-pair symbol, the
unordered multiset of the other two pair symbols, and the zero/nonzero
`Z3` orbit. This is a genuine refinement of the older `(weight,Q-)` bins. The
translated census retains repeated group elements and has mass `192^3`.
Sorting each six-relation signature is valid because the red and blue terms
are symmetric products of the six edge probabilities, with multiplicities
retained.

The objective, gradient, and Hessian formulas handle repeated relation IDs
correctly. The constrained basis spans directions whose bin-mass-weighted mean
vanishes inside every old fractional relation. Although this basis is not
orthonormal, a negative eigenvalue of `B^T H B` still proves a negative
quadratic-form direction if the numerical eigensolve is accurate. The reported
value `-2.18336e-5` and the observed finite decrease are strong numerical
evidence. The rounded search-model numerator is exact and improves the
quadratic parent, but the candidate remains substantially worse than the
campaign incumbent.

Two claims require narrower wording:

- the projected gradient and Hessian are computed in floating point. A
  residual near `5.56e-19` is numerical first-order stationarity, not an
  "exactly negative" first-order certificate;
- the 80 child probabilities are rounded independently. The source does not
  verify that the rounded integer probabilities retain each old relation's
  weighted mean exactly. Exact per-parent-bin residuals or balanced rounding
  are required before attributing the rational candidate wholly to the
  fixed-old-mean subspace.

The hand-written Jacobi eigensolver should also record its final off-diagonal
norm or an eigenpair residual. None of these issues invalidates the exact
objective value of the serialized 80-bin translation model; they limit the
mechanistic interpretation.

The subsequent exact residual audit found precisely one rounding violation:
old relation 5, of difference-element mass 11, has weighted numerator residual
`+1`, i.e. mean shift `1/(11*65536)`; every other old relation is exact. The
continuous direction remains mean-preserving. The rational artifact is thus a
valid near-constraint candidate but not an exactly fixed-old-mean witness.

## Recovery of group structure

The first exact recovery pass found an entrywise color-preserving automorphism
sending quotient vertex zero to every target, establishing transitivity of the
weighted 192-vertex quotient. The chosen one-per-target transversal is not
closed. That does **not** show that no regular subgroup exists: a different
choice of coset representatives may close.

The separately enumerated point stabilizer has exact order 240, with every
leaf permutation checked against all `192^2` relation entries. This is useful
group information but is not yet a Cayley certificate. A positive
`F2^6 semidirect C3` claim still requires an explicit regular subgroup, a
normal elementary-abelian subgroup of order 64, an order-three complement and
its displayed conjugation action, plus entrywise reconstruction as one
inverse-symmetric Cayley function. It would certify a Cayley labeling of the
archived quotient, not uniqueness or the historical PPSS labels.

## Nonabelian stochastic Cayley preflight

The proposed groups use
`(v,t)(w,s)=(v+A^t w,t+s)` with the three nontrivial conjugacy types
`A=C^r plus I^(6-2r)`, `r=1,2,3`. The multiplication, inverse, and action
classification are correct. One probability is assigned to each inverse
orbit, including the identity block. The translated objective over
`a,b,c` has normalization `192^3`, includes repeated cells, and is equivalent
to the full ordered four-class graphon sum by left translation. The exact
integer accumulator fits in 128 bits, and the embedded `A4` control checks
associativity, inversion, noncommutativity, and literal-versus-translated
counts.

This is genuinely distinct from the earlier `S3` class-function kernel lane:
it optimizes arbitrary inverse-orbit probabilities on three 192-element
semidirect groups. For a rational artifact, every optimized basin should be
rounded and recounted before selecting the best tested candidate, because
rounding can reverse close continuous scores. Any promoted report should also
freeze the candidate/source hashes and assert the serialized matrix's
symmetry and bounds. The bounded motivated-start screen is not a global search
over Cayley kernels.

The first 45-iteration result was not a completed negative: its best `r=1`
basin hit the iteration limit with gradient norm `1.39e-6`. A narrow
continuation correctly addressed that issue. It stopped after 79 further
iterations at gradient norm `9.96e-11`; the unrounded value was
`0.0301389772896462`, while the independently recounted rounded candidate is
`0.030138977289700743`. This is essentially the older precision-parent scale and
still about `7.37e-8` worse than the `d476...` incumbent. The optimized kernel
uses only five dyadic values, so the active follow-up question is whether the
semidirect search rediscovered a quotient or embedding of a known basin. This
is evidence about one supported basin, not exhaustion of all inverse-orbit
kernels.

## Homogeneous first-difference recursion

For a probability matrix `P`, the infinite-word construction is well-defined
almost everywhere: two independent words have a first differing coordinate,
and the exceptional diagonal has product measure zero. Conditional on the
outer labels of `t` samples, cross-fiber edge factors are fixed and the tail
integrals on disjoint equal-label fibers are independent. Therefore the
same-color clique densities `T_2,T_3,T_4` form a closed triangular recurrence.
The all-equal tuples contribute `B/B^t=B^(1-t)` times `T_t`.

The exact formulas and their coefficients pass review. At order four the
positional equality types have coefficients `1,6,3,4,1` for
`1111,211,22,31,4`, and the last type gives denominator `B^4-B`. Both red and
blue outer matrices have diagonal zero because equality triggers tail
recursion. Integer term sums are divided by the appropriate powers
`Q,Q^2,Q^3,Q^4,Q^5,Q^6` before the rational recurrence. The largest native
contraction is below `B^4 Q^6 < 2^127` at `B=192`, so unsigned 128-bit
accumulation is safe.

Tiny `B=2,3` controls compare native equality terms with literal enumeration
and compare depth-one through depth-three materializations with the generic
partition recurrence. The exact precision-parent result is
`0.030272980143043526`, substantially worse than its ordinary-step density
`0.03013897728988013`; the denominator-41 parent is likewise worse. Report
SHA-256 is
`dd82873f487f5a026644a80e80d29f827fbf77e6dbcdcb541070bb2bc91d1159`.

For an exact signed diagnosis against an ordinary step graphon with `P_ii=0`,
the equality-type contributions must be placed over `B^4`: ordinary red has
zero repeated-label contributions, while ordinary blue substitutes one for
each within-label clique factor and contributes one on the all-equal type.
Thus `1111` cancels; recursion adds the red `211,22,31,4` terms and changes the
blue factors by `T_2-1`, `T_2^2-1`, `T_3-1`, and `T_4-1`. This prevents
comparing the displayed recurrence numerator over `B^4-B` directly to
ordinary equality-type contributions.

The negative result rejects homogeneous first-difference recursion using the
same tested `P` at every scale. It does not reject alternating/complemented or
other typed child rules. Such a follow-up should be admitted only if the exact
signed type decomposition supplies a concrete rationale.

## Group-recovery update

The four-sheet lifting pass now exactly certifies vertex transitivity of the
full 768-vertex archived graph: 768 full-adjacency-verified movers send vertex
zero bijectively to all vertices. These movers are a transversal, not a closed
group, so this is not yet a Cayley certificate. A regular quotient-subgroup
search must still serialize and verify the six-dimensional conjugation action
of any order-three normalizer. Even a regular 192-quotient action would not by
itself establish a regular lift to all 768 vertices or identify the historical
PPSS coordinates.

The exact Schreier certificate goes further on the quotient. The exhaustively
enumerated order-240 point stabilizer together with verified root movers
generates a transitive subgroup. Since the stabilizer is already the full
automorphism stabilizer, orbit--stabilizer gives the full quotient
automorphism-group order `192*240=46080`. Its 24 directed orbitals reconstruct
all `192^2` parent probabilities exactly. Direct closure of the 1,248
fractional unordered pairs gives five orbits of sizes
`480,96,480,96,96`. These five orbit-constant directions are only the
invariant subspace of the collective Hessian; they are not a decomposition or
positivity certificate for the full 1,248-dimensional coordinate space.

## Shared relation engine and five-orbit preflight

The frozen engine source has SHA-256
`78c49a2587abfa28675242c275d6955080af8586151b1d7e877877adbaee3013`
and binary SHA-256
`e66388bbef9093035d469b7acb117ee9821ca6c935936d4af4566e65f3c86784`.
Its compressed census retains repeated class indices.  A separate literal
order-four fixture now checks the exact objective, gradient, and Hessian,
including repeated relation IDs and diagonal directions; this replaces the
invalid use of a central finite difference for a degree-six polynomial.  In
translated mode the engine checks an identity row, diagonal zero, bijective
difference rows, inverse-relation symmetry, and the torsor identity
`D(D(x,y),D(x,z))=D(y,z)`.  These gates are sufficient for fixing one vertex
and using the `N^3` normalization.

Exact range checks precede accumulation.  The objective and denominator are
bounded by `mass*Q^6` (the red and blue products sum to at most `Q^6`), the
signed gradient by `6*mass*Q^5`, and each Hessian entry by
`30*mass*Q^4`.  Overflow-safe multiplication checks these against the actual
integer types.  The source therefore passes adversarial preflight for
diagnostic use.  Candidate promotion still requires the separate immutable
candidate checker.

The first five-orbit run intentionally deferred its two supplied constraint
rows, so its zero-dimensional search output is only exact derivative data.
The exact gradient divided by oriented relation mass is
`-52946151201272210534400` for each of the four `p` orbitals 0, 1, 2, and 4.
The `h` orbital has the different quotient
`-7240758287166536220672` and must remain frozen.  Thus the mass-neutral row
on the four `p` orbitals passes the exact first-order gate and licenses a fresh
three-dimensional screen.  In the frozen constrained run the basis is exactly
`e0-5e4, e1-e4, e2-5e4` (an equivalent frozen certificate uses relation 1 as
reference).  All three exact gradient contractions vanish.  The
three leading principal minors of `B^T H B` are positive (respectively about
`1.109e26`, `3.263e50`, and `5.614e74`; the full integers are reproducible
from `reports/collective-mean-five-orbit-exact-audit-001/audit.json`, SHA-256
`e62cbdc59339a5b2f8497ccc7b2a9f512af1afcb758c47a73fd33feef8b5d1bc`).
Thus Sylvester's criterion gives an exact strict local minimum
in this three-dimensional subspace.  It does not reduce or certify the full
1,248-coordinate Hessian, nor does it prove a global minimum on these orbit
variables.  The unconstrained five-orbit run has nonzero first derivative;
its sub-grid continuous improvement rounds to `h-1`, whose exact objective is
worse than the parent, so it produces no rational child.  The quadratic
80-relation replay also reproduces
the known one-unit rounded constraint residual, while the 128-relation replay
has zero residual; this is a useful control that rounding errors are exposed.

A subsequent exact certificate adds the primitive compensated `p/h` column
forced by the two exact gradient values.  The resulting four columns span the
complete first-order-neutral tangent inside the five orbit constants.  All
four gradient contractions vanish, and all four leading principal minors of
`B^T H B` are positive by fraction-free Bareiss determinants.  Thus the full
four-dimensional orbit-constant neutral tangent is exactly positive definite
at the parent.  Artifact:
`reports/collective-mean-five-orbit-global-neutral-exact-001/audit.json`,
SHA-256 `088f8513a5be888ad508d6a7ce474d322f1d7803a387fcd4f21cdf5b5c6e19dd`.

The first three iterative full 1,248-edge proposals were **UNKNOWN**: their
Rayleigh/residual pairs were approximately `(386,134)`, `(42.6,41.7)`, and
`(475,589)`, so none excluded negative spectrum.  The final dense run fixes
that numerical defect.  Its exact census finds two gradient classes of sizes
1,152 and 96.  A production-style dense assembly now matches the independent
literal coefficient on nine small off-diagonal directions, while the earlier
formula controls cover diagonal directions and repeated tuple indices.  The
explicit `P C P` projection and full symmetric LAPACK eigensolve return two
class-constant numerical nulls, followed by eigenvalue
`41.16176167949` with residual `1.17e-11` and class-sum residual
`3.12e-13`.  This is strong numerical positive-curvature evidence in the
1,246-dimensional subspace whose `p` and `h` class sums vanish separately.

The final codimension-one run closes the remaining numerical tangent-space
gap.  It projects only the complete gradient vector, so it includes compensated
`p/h` motion and its cross-couplings with heterogeneous modes.  There is one
numerical gradient null at `2.16e-10`, followed by minimum eigenvalue
`41.16176167949` with residual `3.22e-11`.  The normalized gradient dot,
projector-annihilation, idempotence, and projected-symmetry residuals are all
about `2e-14` or smaller.  Thus this is strong numerical positive-curvature
evidence on the entire 1,247-dimensional first-order-neutral tangent at the
tested parent.  It remains floating spectral evidence, not an exact PSD
certificate, and says nothing global or about higher-order escape directions.

## Probability-adaptive polarization gate

`reports/nonlinear-polarization-b93-003/report.json` passes within its stated
one-step coefficient scope.  Sign averaging leaves exactly the four triangle
cubic terms and the three four-cycle quartic terms.  The stored edge ordering,
oriented typed kernels, coarse-tuple multiplicities, and repeated coarse
indices agree with literal order-2, order-4, and order-6 controls and with the
complement sign check.  Dividing the raw coefficients by `960^4 Q^9` and
`960^4 Q^10` is correct.  Separate positive and negative four-limb sums have
conservative 186-bit and 203-bit bounds.

The exact scalar minimum on `[-1,1]` occurs at the checked stationary point
and improves `b93...` by only about `1.85659e-11`, predicting
`0.030138903987771685`.  This is still about `4.22e-10` worse than the
`d476...` incumbent, while a materialized child would have a 1,061-bit
normalization.  Stopping without materialization is proportionate.  This is
exact candidate-bound coefficient evidence, not a recounted child, a Lean
proof, or evidence that repeated polarization is monotone.

The signed variant `C(p)=sgn(p-1/2)p(1-p)` passes the same narrow coefficient
gate.  The extra sign parity is handled edge-by-edge, the complement control
passes, and the exact cubic/quartic endpoint-and-stationary comparison gives a
slightly larger gain, about `2.63528e-11`, with predicted density
`0.030138903979984803`.  It is nevertheless about `4.15e-10` above the
incumbent and would require a 1,036-bit child normalization.  Report SHA-256 is
`8f4598be94feb27926aefa837b340b58651f446bedf99e1574f501640eecf4f0`.
It remains another adaptive rank-one scalar perturbation, not a materially
independent family or a recounted construction.

## Softened 24-orbital start

The structural construction passes: all 24 quotient orbitals are
self-transpose, their matrix exactly reconstructs the parent, relation zero is
the 192-cell diagonal orbital, and softening its graphon probability is a valid
within-class operation.  The original and softened frozen controls recount
correctly.  The free rounded point has density about `0.0307470269`, far worse
than the parent, and was correctly not promoted.

The first run is not reliable basin evidence because the original shared
optimizer lacks an active set.  It computes one global feasible step cap; a
boundary coordinate whose descent component points outward makes that cap zero
and stops all other coordinates.  The final rounded relation 14 is zero while
the other 23 relations are interior, and its positive start gradient drives it
toward that lower wall.  That report has no final continuous vector,
termination reason, or KKT residual.

Engine V2, source SHA-256
`161a5537ef694612d47376a5efa70753943df67ebc5b92ed545d9f28db51543c`,
correctly clips an outward descent component at a lower or upper wall before
normalizing the remaining free direction.  Its literal two-coordinate control
checks precisely this case.  The otherwise identical rerun has no cap stalls
and reaches rounded density `0.030139090196961885`, much closer to but still
worse than the incumbent.  This repairs the specific starvation bug, but the
run is still not a stationary-point certificate: it stops on
`line_search_stall` after 286 iterations with 17 active walls and reported
projected KKT infinity norm `2.57285e-5`, rather than on `projected_kkt`.
Moreover the report stores only the terminal scalar KKT norm, not the terminal
gradient vector needed to recompute complementarity independently.  V2 report
SHA-256 is
`a0fb3fd9aa62deef8de515586217c7dde6c79a036c963f78c7b1e5025d1a84aa`.
The supported conclusion remains that two specified optimizer paths failed;
neither excludes the 24-orbital family or establishes a local basin minimum.

## Heterogeneous XOR-partner gate

The core profile calculation in `reports/xor-partner-e26-gate-003` is sound.
The stored permutations are checked to preserve every parent entry and to act
transitively, so fixing one of four sampled classes changes the ordered
normalization from `192^4 Q^6` to `192^3 Q^6`.  The three remaining class
indices still range independently, retaining repeated indices and diagonal
probabilities.  The 64 labeled induced-pattern numerators normalize and are
constant on each of the 11 isomorphism orbits.  For independent product
coordinates, an XOR-monochromatic `K4` requires the partner pattern to equal
or complement the parent pattern, so
`sum_s g_s(h_s+h_(63 xor s))` is the correct exact objective.  In the
self-product, grouping the 64 patterns into 32 complement pairs and applying
Cauchy gives the stated `1/32` floor.

Three report-level claims need correction.  First, requiring the partner's
*standalone* monochromatic `K4` density to be at most the incumbent is not a
necessary condition for its XOR with the parent to improve.  It is a voluntary
restriction, so the LP containing that inequality is an outer relaxation only
of the restricted partner class, not of all feasible partners.  (Its displayed
optimizer, all mass on orbit representative 3, already satisfies the
inequality, so removing it appears not to change this particular numerical
minimum.)  Second, the fields named `competitive_partner_count` and
`partner_at_most_0.031` test standalone partner density, not XOR output.  The
minimum displayed XOR value is the unchanged `e26` value, worse than the
current incumbent but below `0.031`; therefore “no XOR meets 0.031” would be
false.  Third, finite profiles are dictionary-keyed by raw counts summing to
`n^4`, whereas recursive profiles are normalized fractions.  Proportional
profiles from different orders are consequently not deduplicated (the empty
profile appears at orders 2, 3, 4, and 5 and recursively), so 85 is a count of
evaluated representations, not distinct normalized profiles.

The LP value `0.029403603460895086` is exact for its stated linear polytope but
not realizable graphon evidence.  Its sole orbit, representative 3, is the
two-adjacent-edge wedge and has red edge density `1/3` while assigning zero
probability to two disjoint red edges.  In a graphon the two edges on four
disjoint sampled endpoints are independent, so their joint red probability
must be `(1/3)^2=1/9`, an immediate contradiction.  The corrected outcome is
therefore ambiguous: the archived bank supplies no incumbent improvement and
the weak LP only exposes how much realizability information is missing.  It
does not license a large partner optimizer without a stronger feasible
direction or profile-consistency relaxation.

The corrected gate `xor-partner-e26-gate-005` normalizes profile keys, so its
80 entries are genuinely distinct normalized profiles, and labels the
standalone-density restriction accurately.  The follow-up realizability gate
then removes that restriction and correctly adds the exact disjoint-edge
identity and degree/flag moment cuts.  Its two-flag indexing agrees with the
edge order `(01,02,03,12,13,23)`: bit 0 is the root edge, bits `(1,3)` and
`(2,4)` are the two adjacency words, and bit 5 is marginalized.  At fixed edge
density, a vertex with `k` active optional inequalities has support at most
`3+k`; the code enumerates these exact quadratic basis families, but locates
their interval roots and minima in floating arithmetic.  Accordingly the
displayed `0.0295865079478758` is numerical outer-relaxation evidence, not a
rigorous lower bound.

Its surviving uniform-even pseudoprofile is an exact diagnosis, not merely a
numerical coincidence: every marginal on at most five of the six edges is
uniform, so all tested flag cuts pass.  It cannot be a graphon profile.  Zero
odd-parity mass makes the expectation of
`prod_(i<j)(1-2W(X_i,X_j))` equal one.  Since every factor lies in `[-1,1]`,
this forces `W` to be zero-one almost everywhere.  Subtracting the parity
identities for `(x,y,z,w)` and `(x',y,z,w)` gives
`g(y)+g(z)+g(w)=0` in `F_2` almost everywhere, forcing `g=0`; all rows agree,
and symmetry makes the graphon constant zero or one.  Neither constant has the
uniform-even profile.  This supplies no quantitative separation from nearby
pseudoprofiles.  The separately stated equal-mass two-block rank-one control is
now reproducible: `rank_one_control.py` enumerates all 5,101 feasible
`0.01`-grid pairs `|a|<=min(p,1-p)`, averages the 16 latent-sign assignments,
and contracts the resulting full 64-pattern distribution with the frozen
parent profile.  It returns the unchanged parent at `(p,a)=(0,0)` and `1/32`
on the best balanced-grid point `(1/2,0)`.  Report SHA-256 is
`f10b65aa3256b1acf23005cb3a3672e8b5b3f86652d438aea34723a147fda7a5`.
This is correctly labeled a floating bounded-grid negative, not continuous
optimization or exact promotion evidence.
