# Fresh hypotheses, round 2

Date: 2026-09-27.  This is an independent mechanism-generation pass for the
asymptotic two-colour `K4` multiplicity problem.  It proposes no new bound and
runs no experiment.  The benchmark to beat is the separately audited
stochastic step graphon of density

```
515776850799050572477656236153 / 17113283103081096920205493272576
  = 0.03013897728988013...
```

The proposals were selected for different mathematical mechanisms, not as
seed, precision, or search-parameter variants.  Overlap with the active lanes
was assessed only as a final triage step.  Every suggested numerical outcome
would remain a construction screen until independently recounted and supplied
with its own asymptotic-realization argument.

## Ranking

1. **H-F2-01: association-scheme microstructure in fractional blocks.**  This
   attacks the independence assumption responsible for the current graphon's
   six-edge products, while retaining its successful coarse quotient.
2. **H-F2-02: typed recursive substitution into the strong quotient.**  This
   changes the full internal two-, three-, and four-vertex profiles rather than
   optimizing a scalar diagonal probability.
3. **H-F2-03: nonabelian voltage covers.**  This is the most concrete route to
   correlations among several quotient blocks in a finite, exactly countable
   construction.
4. **H-F2-04: flag-moment SDP with flat extraction.**  This is a discovery
   instrument for latent types that do not fit a preselected rank-one split.
5. **H-F2-05: exact algebraic minimization of the two-parameter graphon.**  Its
   likely numerical gain is tiny, but it can close an active family exactly.

An initially attractive sixth idea, a random Seidel-switching lift, admits an
elementary `1/32` lower bound.  It is recorded last as a no-go result so it is
not rediscovered as an experimental lane.

## H-F2-01: association-scheme microstructure in fractional blocks

**Family.** Correlated random construction; finite fields, difference sets,
orthogonal arrays, and association schemes.

**Mechanism.** Retain the 192 coarse classes and the successful coarse
probabilities `p` and `h`, but give every expanded vertex a micro-coordinate
`x` in a growing finite group or vector space.  Between coarse classes `i,j`,
colour `(i,x)(j,y)` by a predicate such as

```
L_ij(x,y) in D_ij,
```

where `L_ij` is an affine or bilinear form and `D_ij` is a difference set or a
union of relations in a small association scheme.  Choose relation sizes so
that the coarse red densities remain `p` and `h`.  The zero Fourier character
then reproduces the independent-edge graphon term.  Nonzero characters obey
flow-conservation constraints at the four sampled vertices and add structured
triangle and cycle corrections.  Block-specific orientations or characters
can make these corrections cancel across the quotient instead of forcing the
positive correlations produced by using one common relation everywhere.

This is not finite rounding of each block independently.  The same
micro-coordinate participates in all incident edges, so the construction
retains vertex-mediated correlations as the micro-coordinate space grows.

**Falsifiable prediction.** A small relation library with at least two
nontrivial character classes admits an assignment to the `p` and `h` quotient
blocks whose exact nonzero-character correction to red-plus-blue `K4` density
is negative.  A strong success beats `0.03013897728988013`; a weaker but still
mechanistic success is a negative correction at exactly the incumbent coarse
marginals.

**Decisive falsifier.** If the character expansion reduces, for every allowed
block assignment in the first library, to a sum of nonnegative fourth powers
or Hilbert--Schmidt norms, then this family cannot beat its independent
coarse graphon.  A complete exact evaluation of Paley/difference-set and
two-class scheme representatives with no negative correction would retire
that library, not all coherent microstructures.

**Cheapest discriminating test.** Derive the six-edge character-flow formula
once, validate it by literal enumeration on groups of orders 3--7, and evaluate
one Paley-type and one Hadamard/difference-set relation using the already known
coarse block-type histogram.  Do not materialize a `192q` adjacency matrix
until a negative correction appears.

**Estimated compute.** Symbolic derivation plus seconds for tiny enumeration;
minutes for an exact block-orbit assignment screen.  A promising candidate
would need a separate exact counter and a finite-field limit proof.

**Overlap with existing lanes.** Medium with the latent-sign and failed
four-sheet rounding lanes, but materially different: those use one binary
latent mode or a fixed four-sheet coupling, whereas this hypothesis uses a
growing coherent configuration and its full character algebra.  Low overlap
with unit-edge local search.

## H-F2-02: typed recursive substitution into the strong quotient

**Family.** Graphon composition, recursive constructions, and rooted profile
operators.

**Mechanism.** Replace each of the 192 coarse classes by an internal graphon
type, possibly with complementary types paired according to its coarse
neighbourhood role.  Sampling two, three, or four vertices from the same
coarse class then invokes the internal edge, triangle, and four-vertex profile;
sampling from distinct classes still uses the strong coarse quotient.  The
stationary profiles satisfy a finite rational linear system indexed by equality
partitions and internal types, analogous to typed graph substitution.

A scalar within-class probability `q` throws away precisely these correlations:
it determines an internal edge density but forces the triangle and `K4`
moments to be powers of `q`.  Thus the earlier result `q=0` in a scalar family
does not settle this profile-valued substitution.  The contribution is small
because repeated coarse indices are infrequent, but the present lead over the
announced decimal threshold is also small.

**Falsifiable prediction.** There is a two-type internal rule, selected from
the coarse rooted-neighbourhood classes, whose stationary exact profile lowers
the objective relative to both (a) all-blue internals and (b) the independent
scalar-`q` profile with the same internal edge density.  The comparison must
keep the external `p,h` matrix fixed before any joint retuning.

**Decisive falsifier.** Derive the exact coefficient of every internal
two-, three-, and four-vertex profile coordinate.  The full objective is a
low-degree profile polynomial (for example, a `2+2` equality pattern multiplies
two edge-profile terms), while it is affine in the highest-order profile after
lower orders are fixed.  If this hierarchical polynomial is minimized over the
realizable two-type profile region at the all-blue extreme point, the proposed
recursive freedom cannot help for this quotient.
Failure of a few small cores is weaker evidence unless their convex/profile
region is proved complete.

**Cheapest discriminating test.** Reuse equality-partition bookkeeping to
write the hierarchical profile polynomial explicitly: solve order two first,
then order three, then the part affine in the order-four profile.  Before
searching rules, evaluate the order-four coefficients on all 11 unlabeled
directions and solve the two-type fixed-point equations for one alternating
complete/empty control and one historically strong recursive core.  This
determines whether any coordinate even has the right sign.

**Estimated compute.** Seconds for coefficient extraction and controls;
minutes for exact rational evaluation of a bounded rule bank.  Verification is
profile recurrence plus an independently materialized finite-depth sequence,
not the current fixed-template Lean checker.

**Overlap with existing lanes.** Medium with the retired small-core typed
recursion screen, but that screen used weak order-three/Q9 outer rules and fixed
historical XOR factors.  Here the outer object is the newly successful
192-class stochastic quotient, and the test begins from its exact rooted
profile functional rather than a larger blind core bank.  Low overlap with
mass optimization or latent `+/-` splitting.

## H-F2-03: nonabelian permutation-voltage covers

**Family.** Finite covers, permutation representations, and holonomy.

**Mechanism.** Lift the 192-vertex quotient by sheets carrying a transitive
permutation action of a small nonabelian group such as `S3`, `D8`, or `A4`.
Represent defect and half-density blocks by matchings or unions of orbital
relations whose voltages are group elements.  Counts of lifted triangles and
`K4`s become fixed-point counts of words around quotient cycles.  Abelian
voltage assignments only record additive cycle parities; noncommuting
holonomies can make two individually benign cycle constraints incompatible,
removing transversal monochromatic `K4`s that every `V4` assignment retains.

The right reduced objective is not “minimize identity holonomies” in isolation.
Repeated-fibre terms, complements of matchings, and both colours must appear
with their exact quotient multiplicities.  Character tables or explicit small
permutation matrices provide those terms without materializing the full lift.

**Falsifiable prediction.** For at least one quotient motif carrying two
interacting fundamental cycles, a nonabelian voltage assignment strictly
reduces the exact combined red/blue fixed-point contribution below every
assignment in the aligned-bit abelian control, and the reductions have net
negative weight in the full quotient census.

**Decisive falsifier.** If the exact motif census shows that all voltage words
enter only through independent single-cycle class functions, then
noncommutativity supplies no extra degree of freedom.  Alternatively, an exact
optimization over the full `S3` voltage state space that matches the best
abelian value would retire `S3`, though not larger representations.

**Cheapest discriminating test.** Select the smallest quotient subcomplex with
two shared cycles.  Tabulate its objective using the six permutations of `S3`,
including complementary blocks and repeated base indices, and compare with
all abelianized assignments.  Only if the local coefficient is favorable
should the state library be inserted into the full quotient factor graph.

**Estimated compute.** Seconds for the local table; minutes for a full exact
motif-census evaluation; potentially hours for global voltage assignment.
Any full candidate still needs an independent ordinary adjacency recount.

**Overlap with existing lanes.** High with the four-sheet voltage/cycle lane,
but it is a genuine representational extension rather than a new seed: the
test is specifically whether noncommuting holonomy creates joint constraints
unavailable to the existing first-/second-bit model.  It should be stopped
immediately if the motif objective factors through the abelianization.

## H-F2-04: flag-moment SDP with flat extraction

**Family.** Flag algebras, truncated moment problems, and stability-guided
construction discovery.

**Mechanism.** Introduce a small collection of rooted latent types for a
representative coarse vertex and variables for their two-, three-, and
four-vertex extension probabilities.  Impose normalization, complement
symmetry, coarse `p,h` marginals, and positive-semidefinite connection matrices.
Minimize the monochromatic `K4` functional over this truncated moment region.
Unlike a lower-bound-only flag calculation, the goal is a low-rank, flat
moment solution: if a moment matrix has stable rank and satisfies the extension
equalities, its atoms can be extracted as an explicit finite step graphon.

This permits several coupled latent modes without choosing in advance the
rank-one form `epsilon*s*t*C_ij`.  The dual residual also identifies which
rooted configurations make the current graphon expensive, providing a
principled refinement even if extraction fails.

**Falsifiable prediction.** The order-5 rooted relaxation has a feasible point
below the incumbent and an approximately flat moment matrix of modest rank
(say at most eight), from which rational latent types can be reconstructed and
exactly recounted.

**Decisive falsifier.** A relaxation value below the incumbent with no flat
extension is not evidence for a construction.  If successive order-4 and
order-5 relaxations either stay above the incumbent or produce only strongly
non-flat pseudo-moments whose rounded atoms fail exact recount, this route is
not earning its computational cost.

**Cheapest discriminating test.** Work on one orbit representative of each
fractional coarse-block type, not all 192 labels.  Build the order-4 connection
matrix, verify it on the independent graphon and binary latent split, then
inspect rank and dual residual.  Admit an order-5 solve only if the order-4
solution suggests extractable atoms.

**Estimated compute.** Tens of seconds to minutes for the first symmetry-reduced
SDP; potentially hours and numerical fragility at the next order.  Extracted
objects require rational reconstruction and exact counting; the SDP score
itself certifies no upper bound.

**Overlap with existing lanes.** Medium with graphon derivatives and latent
splitting, but different in both search object and output: it searches a
consistent local moment cone and must extract an explicit graphon.  It also
complements, rather than duplicates, flag-algebra lower-bound work.

## H-F2-05: exact algebraic minimization of the two-parameter graphon

**Family.** Exact polynomial optimization and family-level certification.

**Mechanism.** The current simple family has an explicit bivariate rational
polynomial `F(p,h)`.  Eliminate one derivative with a resultant, isolate every
real critical root by Sturm sequences or interval arithmetic, and compare
those algebraic values with all four boundary polynomials.  This replaces
dyadic coordinate tuning by a proof of the exact global minimum on
`[0,1]^2`.  The minimizing probabilities need not be rational: an algebraic
graphon still gives a valid upper bound, with certified rational intervals or
nearby rational witnesses available for the checker.

**Falsifiable prediction.** The reported dyadic pair is not an exact stationary
point, so the isolated interior minimizer has strictly smaller density.  The
more important predicted deliverable is a certificate that no other point in
this two-parameter rectangle does better.

**Decisive falsifier.** If the exact derivatives vanish at the current pair or
the certified gain is negligible compared with the next construction-level
uncertainty, no more search time should go to this family.  Failure to isolate
all roots is an implementation failure, not evidence of global optimality.

**Cheapest discriminating test.** Differentiate the published polynomial,
check the gradient sign at the current dyadic pair, and compute the univariate
resultant degree and coefficient sizes.  Proceed to exact root isolation only
if these are modest; verify the selected rational approximation through the
independent graphon counter.

**Estimated compute.** Seconds to minutes for a computer algebra system,
followed by one exact recount.  A human-checkable certificate can consist of
isolating intervals, derivative sign tables, and exact boundary comparisons.

**Overlap with existing lanes.** High with stopped probability tuning, so this
is deliberately low priority.  It is not another precision sweep: its value is
closing the whole two-parameter family and preventing further tuning from
consuming research budget.

## H-F2-06 (retired analytically): random Seidel-switching lift

**Family.** Two-graphs and Seidel switching.

**Proposed mechanism.** Start from a symmetric sign kernel `A(i,j)` and split
each base type into equal signs `s in {+1,-1}`.  Give the lifted edge the sign
`A(i,j) s t`.  Equivalently, independently switch every sampled vertex.  For a
fixed ordered base quadruple, the lift can be monochromatic exactly when its
four base triangle products are all equal; conditioned on that event, two of
the 16 sign assignments work, so the monochromatic probability is `1/8`.

This initially looked attractive because it converts the objective to the
density of homogeneous four-sets in a two-graph.  It is, however, obstructed.
Let `tau_1,...,tau_4` be the four triangle signs.  Their product is one, and

```
1{tau_1 = tau_2 = tau_3 = tau_4}
  = (tau_1 + tau_2 + tau_3 + tau_4)^2 / 16
  = 1/4 + (1/4) * sum_over_the_three_C4s chi(C4).
```

After averaging independent base indices, the three cycle terms are equal to
the signed `C4` homomorphism density.  For a symmetric kernel this is
nonnegative: it is the Hilbert--Schmidt square of the squared integral
operator.  Therefore every such switching lift has density

```
1/32 + (3/32) * t(C4,A) >= 1/32 = 0.03125,
```

well above the incumbent.  The calculation includes repeated base indices
because it is an ordered homomorphism-density identity.

**Prediction and falsifier.** The original prediction of a base two-graph with
homogeneous-four density below `8 * 0.03013898` is falsified by the positivity
identity.  A counterexample would have to invalidate the identity itself or
leave the vertex-switching form `A(i,j)st`; it would not be an instance of this
hypothesis.

**Cheapest test and compute.** No CPU test is warranted.  If formal assurance
is desired, check the identity on all tiny sign matrices and formalize the
operator-square proof.  Cost is seconds, but it cannot produce a competitive
construction.

**Overlap with existing lanes.** Superficially resembles the latent-sign split
and XOR products.  The obstruction applies only to the pure multiplicative
switching lift; it does **not** rule out the additive perturbation
`P_ij + epsilon*s*t*C_ij`, association-scheme microstructure, or general
multi-type refinements.  This distinction makes it a useful pre-screening
lemma rather than a negative verdict on latent variables.

## Recommended allocation

Spend the first short screen on H-F2-01's character correction.  In parallel
only at the reasoning level, derive H-F2-02's exact internal-profile
coefficients.  Advance H-F2-03 only if a shared-cycle motif demonstrably
depends on a noncommuting word.  H-F2-04 is a fallback when explicit latent
families stop producing mechanisms; H-F2-05 is closure work, not the main
improvement lane.  Retire H-F2-06 without experiment.
