# Broader mechanisms for the K4 problem — 2026-09-30

Literature-only lane; hypothesis-research skill applied. Scope: primary research
available by September 30, 2026, emphasizing 2024–2026. No experiments, installs,
Docker, agents, outreach, paid compute or commits. The main thread owns the N7
optimizer-only cut; this review neither ran nor assessed its pending solve.

**Recommendation:** the best ambitious transfer is **compressed, overlapping
marginal consistency**, from renormalization-based lower bounds. The most
surprising recent connection is **causal inflation**: graphon samples are a
network of independent latent sources with the same edge response everywhere.
Both are potentially useful representations of higher-order compatibility,
not new inequalities already proved for our problem. The cheapest upper-search
follow-up is a **new-class insertion oracle**, informed by recent phase studies.

## History and gates

Target: `inf_W F(W)`, where `F=t(K4,W)+t(K4,1-W)`, `0<=W<=1` and W is symmetric.
The reported upper incumbent is 0.030138887566497220. Published lower ~0.0296
and N9 numerical 0.02961 remain distinct from exact certificates. No fixed
768 size, equal degree, finite-step representation, or Clebsch assumption is
available for a universal lower bound.

Read RESUME, lower-frontier-literature-2026-09-30, lower-frontier-B,
global-anchor-pilot, clebsch-bowl-focused-tests, deeper-literature-root-2026-09-27,
landscape-escape-literature, and clebsch-formations-literature-2026-09-29.
RESUME's initial lane-status paragraphs are stale; the supplied handoffs govern.
In particular: isolated higher moments can be freely PSD-completed; simple
squares can be redundant; mean-degree regularity is unsound; one-step pointwise
transport fails exactly; reducing one certificate component worsens F;
an attractive motif profile need not be realizable. PatternBoost, annealing,
constructive Monte Carlo, voltage lifts, switching and concentration are prior
leads, not discoveries of this review.

The supplied main-thread baseline cut violation +0.00027923756 is NOT a gain.
This report supplies proposals and transfer audits, not a new bound or a claim
of novelty. A substantial outcome would be a certified improvement beyond the
existing frontier, a matching bound for an explicitly defined refinement family,
or a demonstrably cheaper way to retain higher-order compatibility. A small
hierarchy separation alone is a pilot success, not a frontier result.

## 1. Compress consistency across levels, rather than truncate the hierarchy

**Source and exact location.** Kull, Schuch, Dive and Navascués,
[*Lower bounds on ground-state energies of local Hamiltonians through the
renormalization group*](https://arxiv.org/html/2212.03014v3), PRX 14, 021008,
April 1, 2024; inspected revision April 10. Section III.1, equations (15)–(16),
sets up a general convex marginal hierarchy. Sections II.3–II.4 compress its
objects while retaining compatibility; IV.2 optimizes compression maps and
IV.3 handles finite-precision certification. Their numerical demonstration is
for spin chains; useful accuracy depends on the chosen compression. This is
not a dimension-independent guarantee for arbitrary dense interactions.

**Our mapping (proposal).** Let P_m be the distribution of the induced colored
graph on m iid sampled vertices. It is a nonnegative normalized classical
marginal, and deleting a vertex gives P_(m-1). The objective is linear in P_4.
Instead of storing full P_10, retain selected distributions of rooted summaries
of overlapping vertex sets. Candidate summaries include adjacency signatures
to an anchor, counts of extension types, and selected joint path statistics.
They must be defined for EVERY graph, including graphs without a Clebsch anchor.
For a zero-probability anchor use unnormalized joint probabilities, avoiding
division by its mass.

A sufficient bookkeeping pattern is a fixed positive map C_m with a smaller
map Ttilde_m satisfying `C_(m-1) T_m = Ttilde_m C_m`; then compressed marginals
inherit the exact equality. In general several deletion maps and summaries
will be necessary, not this single chain. Keep the existing full small-level
SDP and append these compressed constraints so the new relaxation cannot become
weaker merely through information loss. This is an adaptation to derive, not
an already implemented consequence of the paper.

**What is different?** The failed ten-vertex anchor block had three unconstrained
new entries. Here multiple overlapping summaries refer to the SAME underlying
events and share deletion identities, normalization and nonnegative atoms.
Unlike merely selecting more flag generators, the proposed compression also
acts on the high-level compatibility data. Whether that saves anything is open.

**Smallest falsifiable pilot.** On the already enumerated N5→N6 control, specify
one rooted summary and close it under all needed deletions. Count its states
before any solver work. If closure nearly recreates full N6, reject that summary.
Otherwise test extension of the saved old feasible witness while preserving
the full old constraints. Compare against the known full N6 improvement. A
successful pilot excludes the witness with substantially fewer stored states;
a certificate must expand back to checked graph identities and nonnegative
terms. Only then try a larger support.

**Risks/decision.** Dense K4 has no spatial boundary-to-volume advantage. A
Clebsch-trained compression is permitted as a choice of valid tests, never as
a restriction on all feasible graphons. Compression may erase precisely the
mixed four-vertex information needed, or deletion closure may explode. Lower
bounds primarily; upper candidates can suggest maps. **Pursue a paper-and-pencil
dimension/closure audit, not a new tensor-network software stack.**

## 2. Causal inflation: test whether overlapping observations have common causes

**Recent source.** William, Remy, Bancal, Cai, Brunner and Pozas-Kerstjens,
[*Symmetric observations without symmetric causal explanations*](https://arxiv.org/html/2502.14950v2),
February 20, 2025 preprint, published version March 27, 2026, PRA 113, 032219.
Section II equations (2)–(3) distinguishes identical-source/response models
from merely symmetric observed distributions. Section III uses seven copies
in a polygon; Appendix B equation (11) expands its outcome probabilities.
The paper exhibits symmetric classical observations without a symmetric causal
realization. Its [computational appendix](https://github.com/apozas/symmetric-causal/)
provides higher-level incompatibility tests and certificate export.

**Our mapping (exact model identification, not a new bound).** For a graphon,
take independent U_i uniform on [0,1] and independent edge coins Z_ij, and set
`A_ij=1{Z_ij<=W(U_i,U_j)}`. Thus the six observed edges of K4 have four shared
vertex sources, the SAME symmetric response W, and independent local coins.
Copying sources and retaining overlapping marginals is precisely the kind of
compatibility question inflation addresses. For a three-vertex sample the
three edges form a triangle causal network. This does NOT impose an additional
symmetry on W's latent classes: arbitrary irregular W still has this iid-source
representation. That distinction prevents misusing the paper's counterexample.

**Potential payoff.** Eliminate pseudo-profiles that satisfy separate PSD tests
but cannot arise from a single collection of independent vertex sources and
one common kernel. This directly targets the unrealizable-profile and free
completion failures. It might offer selective compatibility constraints without
all induced N9 graphs. It may also turn out to be only a repackaging of the
available flag hierarchy at the same support size.

**Smallest falsifiable pilot.** On a saved low-level primal witness, construct
the edge-outcome probabilities for a triangle and its first copied-source
network. Enumerate the marginal identities, disconnected-set factorization
requirements and shared-response symmetries, then compare their cone with the
existing graph identities/PSD constraints. A known low-order control is
`E[A12 A13] >= E[A12]^2` (degree variance); rediscovering it is not progress.
Use the present exact graphons as feasible controls, including irregular ones.
Only proceed to four-source/six-output K4 inflation after a genuinely new
separation or a demonstrated reduction in representation cost.

**Critical failure modes.** Unknown independent probabilities multiply:
`P(E and J)=P(E)P(J)` for source-disjoint events. When testing a fixed profile
the RHS is data; when optimizing profiles it is NOT a known linear constant.
An infeasibility certificate for one profile need not be a global linear cut.
Use disjoint-union moments or an explicitly justified polynomial relaxation;
do not silently cube a pseudo-moment. Unknown global mixtures need separate
treatment because dissociation holds for a fixed W, not arbitrary mixtures.
For a linear objective mixtures do not lower the true infimum, but nonlinear
compatibility tests can distinguish them. A triangle test may miss every K4
obstruction. **Pursue a small containment audit; transfer remains speculative.**

**Recent scaling companion.** Gitton–Renner,
[*The Elegant Joint Measurement is Non-Classical in the Triangle Network*](https://arxiv.org/abs/2510.15143),
October 16, 2025, reports symmetry reduction plus Frank–Wolfe and exact
computer-assisted certificates. The authors' [fast-inflation repository](https://github.com/vgitton/fast-inflation)
gives the classical triangle integral model and implementation. I inspected
the abstract and README, not the inaccessible HTML proof: this is a scaling
lead, not a verified K4-ready theorem or API. No installation was performed.

## 3. Phase nucleation: add a genuinely new vertex type before refining old ones

**Source.** DiCarlo–Sadun, [*Tripodal structure in undersaturated random graphs*](https://combinatorialpress.com/ojac-articles/issue-20-2025/tripodal-structure-in-undersaturated-random-graphs/),
preprint August 22, 2025; publication December 4, 2025. Equations (5)–(12)
analyze small-mass structured regions and their leading contributions;
Sections 4–5 numerically study discontinuous changes between competing phases.
The objective is entropy at fixed edge/triangle densities. The global phase
classification is not proved; the paper explicitly works with competing
ansatzes. It supplies a concrete warning that following a smooth symmetric
branch can miss another branch, not a K4 theorem.

**Our adaptation (elementary derivation).** For the present W, give a NEW class
mass epsilon, shrink old masses by 1-epsilon, and choose an arbitrary attachment
profile q(y) in [0,1]. Define

```
R_new(q) = integral [q(y)q(z)q(t) W(y,z)W(y,t)W(z,t)
                 +(1-q(y))(1-q(z))(1-q(t))
                    (1-W(y,z))(1-W(y,t))(1-W(z,t))] dy dz dt.
```

The full four-vertex density is an exact degree-four polynomial in epsilon
when W, q and the new diagonal probability are fixed. Its derivative at zero
is `4(R_new(q)-F(W))`. The new diagonal affects only terms of order epsilon²
and above. Therefore `R_new(q)<F(W)` is a checked improving direction, even
when every existing class has equal rooted participation. This is the stronger
question of whether an absent class could do better, not merely whether to
reweight existing classes. It is standard variational reasoning, not a novelty
claim. Failure of first-order insertion does not exclude finite-mass changes.

**Pilot.** Freeze B192 first. Optimize the cubic R_new over its 192 attachment
probabilities, allowing all old classes and both hard/fractional edge types.
Existing rows are mandatory controls. Rationalize any winning profile and
independently count the epsilon polynomial including repeats and diagonals.
If no first-order gain, report only a heuristic failure unless the cubic has
a certified lower bound. A later two-new-class finite-mass pilot can test a
barrier that first-order insertion misses; retain every term with 2,3,4 new
vertices. Do not assume constant degree.

**Difference and limit.** Prior concentration scales a chosen centered kernel;
this optimizes a new attachment profile outside the existing row list. Prior
growth/repair is related: novelty here would be an exact insertion oracle or
certificate, not renaming growth as physics. Compare code coverage before
implementing. It may simply return a known Clebsch row. Helps upper bounds and
restricted structural understanding, not a universal lower bound by itself.
**Reserve as a focused, falsifiable upper-search test.**

## 4. Exact optimal-face recovery from spherical-code proofs

**Source.** Cohn–de Laat–Leijenhorst,
[*Optimality of spherical codes via exact semidefinite programming bounds*](https://arxiv.org/html/2403.16874v1),
March 25, 2024. Theorem 1.1 gives exact code results. Section 2.1 recovers
rational kernels using row reduction, Hermite normal form and lattice reduction;
Section 2.2 changes coordinates to a smaller positive-definite block; Section
2.3 performs exact rounding. The method assumes a recoverable small-bit rational
description of the relevant optimal face. The triangle-free strongly regular
graph connection motivates attention, but their objective is spherical packing
or pair-potential energy, not monochromatic K4 density.

**Transfer.** If a promising lower-bound SDP becomes nearly singular, recovering
its actual face may preserve much more of the numerical bound than padding
every tiny eigenvalue with a diagonal shift. This could matter for the new
optimizer-conditioned programs or a recovered N9 certificate. It is a
certification improvement, not a fresh search inequality.

**Pilot.** Take one saved small SDP dual block whose diagonal correction costs
noticeable objective value. Try rational kernel recovery and reduced-coordinate
rounding; compare the final rigorously checked lower value with the current
checker at the same numerical input. Verify all original coefficient identities
and PSD conditions after expansion. Reject the proposal if kernel recognition
is unstable or the certificate is strictly interior already. A tiny recovery
of rounding loss is useful validation, not a stronger mathematical hierarchy.

**Important boundary.** Do not impose the incumbent Clebsch kernel on every
graphon. A guessed face used to search for a dual certificate is acceptable
only when the resulting certificate independently passes the original global
constraints. Primal face restrictions require a proof that they retain an
optimum. Symmetric spherical optimality does not imply our solution is optimal,
and K4 includes mixed four-point products absent from a pair-energy objective.
Lower certificates primarily. **Pursue only when an actual rounding bottleneck
appears; no replacement of the working checker now.**

## 5. Entropy constraints: a recent attractive transfer that fails its first test

**Source.** H. Fawzi, O. Fawzi and Scalet,
[*Entropy Constraints for Ground Energy Optimization*](https://arxiv.org/html/2305.06855v2),
January 9, 2024 revision, Journal of Mathematical Physics 65, 032201 (2024).
Sections 2–3 add weak-monotonicity and Markov-entropy-decomposition constraints
to local quantum marginals. Equation (12) bounds their hierarchy advantage
using larger consistency regions; Theorem 2.4 supplies a quantitative example.
The paper's useful violations exploit negative quantum conditional entropy.

**Our no-go check (analytical, no experiment).** For a valid classical joint
probability table, H(A|B)>=0. Thus a proposed cut
`H(A|B)+H(A|C)>=0` is already automatic separately on AB and AC marginals.
Likewise a MED sum of classical conditional entropies is automatically
nonnegative. Diagonal classical versions of these particular quantum cuts
cannot remove any of our nonnegative probability marginals, even if those
marginals have no global extension. This rules out the most direct transplant.

More sophisticated information inequalities could still help a causal model
with independence constraints, but they require a new derivation and must be
compared with the inflation route. Entropy of a PSD flag Gram matrix is not
the Shannon entropy of a graph distribution: do not substitute it. Strong
subadditivity on a fully represented joint table is also automatic. **Retire
these two direct entropy families; do not install a relative-entropy solver.**

## Additional rejected analogies and priority order

* **Hamiltonian Bootstrap**, [October 1, 2024](https://arxiv.org/html/2410.00810v2),
  equations (2)–(6): selected operator products generate an SDP moment matrix.
  In our commuting classical setting this alone rephrases selected flag/SOS
  generators, already covered by Wegener. No independent new mechanism found.
* Pairwise spin-glass cluster moves and lattice boundary-error estimates do
  not transfer to the dense six-edge K4 interaction without new proofs.
  Population annealing is already covered. Random-disorder landscape theorems
  do not describe this deterministic objective just because both are frustrated.
* Quantum hardware, quantum graphon learning, and generic neural surrogate
  methods supply no identified route beyond our existing learned-seed leads.
* Universal optimality of a spherical code and geometric resemblance to a
  Hadamard construction do not transfer an objective or an optimality proof.
* A new language for the same Gram cone is not a new constraint. For both
  renormalization and inflation the first deliverable must be a closure census
  or an explicit separation from the existing small relaxation.

Order of future work: (1) compressed overlap/deletion census; (2) causal
inflation containment audit; (3) exact new-class insertion oracle, after checking
overlap with earlier growth code; (4) optimal-face rounding when needed.
No experiments were launched and no processes remain from this lane.

Search log and source-access notes: [report directory](../../reports/broad-methods-literature-2026-09-30/search-log.md).
