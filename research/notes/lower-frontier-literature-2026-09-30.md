# Deep literature lane L — 2026-09-30

## Contract and interim checkpoint (04:11 UTC)

One additional literature agent, alongside A/B/C. Read-only research with writes
only to this note and its report directory. Up to 25 minutes from launch; no
experiments, Docker, installations, outreach, paid work, commits or subagents.
Read the supplied history and recent experiment notes; treat worker results as
reported evidence, not independently reviewed proofs. Full report follows.

**Strongest newly located mechanism:** optimality-conditioned flag certificates.
Daniel Brosch's [2024 conference text, Section 2](https://eventos.ull.es/_files/_event/_111018/_editorFiles/file/ConferenceProgram/paper-086.pdf)
and [March 2025 Graz slides, “Using the derivatives in optimization”](https://slides.danielbrosch.com/CombDerivatives_Graz/)
describe adding vertex/edge-deletion necessary conditions at a global minimizer,
then finding SOS certificates in the resulting quadratic module. The slides
also treat hinge/edge swaps and report a certificate for the three-edge path
inequality. They label the broader paper work in progress. No K4 bound follows
without a new derivation, coefficient construction and certificate.

This is a meaningful distinction from our failed universal-square transfers:
the added conditions need hold at a minimizer, not at every graphon, provided
the reduction to minimizers is proved. It connects directly to C's root-mass
variation. It does not justify assuming Clebsch structure, balanced degrees,
or any currently non-tight certificate kernel. Implementation and the exact
smallest K4 test remain under review.

Other grounded leads being assessed: non-SOS density inequalities and their
precise scope; edge-count rather than vertex-count symmetry-reduced flag
hierarchies; June 2026 exact blowup stability; scalable SDP methods with
independent exact certification. No newer verified K4 frontier located so far;
the Feinstein announcement still gives only <0.030139 in the inspected source.

## Completed review and recommendation

**Pursue minimizer-conditioned flag constraints first.** This is the clearest
mechanism newly located in this review. It supports lane C's direction and
provides additional edge-rooted conditions with a small initial coefficient
budget. Next, inspect a selective edge-count hierarchy before committing to
the full N9/N10 induced-density expansion. Neither is a new mathematical
invention here, nor an established improvement to our bound.

The review looked through September 30, 2026. Primary texts, author slides,
conference abstracts and software documentation are distinguished below.
No experiments or installations were performed. The formulas suggested for
our objective are adaptations for a future checked pilot, not certificates.

### Scope and history used

The target remains the universal graphon minimum
`c4 = min_W F(W)`, where `F(W)=t(K4,W)+t(K4,1-W)` and `0<=W<=1`.
There is no fixed size, regular-degree, triangle-free, or Clebsch assumption.
Our reported upper incumbent is approximately 0.030138887566497220, with
structured independent checking; this review did not recount it. Its local
refinements do not identify the global minimizer.

The prior failures determine the selection below: elementary contractions can
already be low-order flags; isolated higher moments admit free PSD completion;
one-step neighborhood transfer has exceptional-root obstructions; adding
C5/P5 blocks did not improve the small hierarchy; reducing the largest term
of one non-tight certificate worsened the actual upper objective. A's N9
census exposes a solver-layout bottleneck, not a theorem of infeasibility.
C now supplies a quantitative rooted-variance estimate and an optimizer-only
seven-vertex cut; those results require root review and are not being
re-derived or independently certified by this literature lane.

### 1. Conditions at minimizers can strengthen the proof system

**Primary source and precise location.** Razborov, *Flag algebras* (2007),
[Section 4, Theorems 4.3 and 4.5, Corollary 4.6](https://www.ias.edu/sites/default/files/math/csdm/05-06/arazborov_flag_algebras.pdf).
The vertex derivative vanishes almost surely at an extremal homomorphism;
the edge-deletion derivative is nonnegative. Corollary 4.6 permits multiplying
these by arbitrary rooted expressions for equalities and nonnegative rooted
expressions for inequalities before averaging. This is established prior art.

Brosch's [2024 ISCO conference text, Sections 2–3](https://eventos.ull.es/_files/_event/_111018/_editorFiles/file/ConferenceProgram/paper-086.pdf)
and [March 2025 Graz slides, “Using the derivatives in optimization” and
“SOS based proofs”](https://slides.danielbrosch.com/CombDerivatives_Graz/)
extend the approach to more operations and illustrate derivative-conditioned
certificates for Sidorenko examples. The slides identify the general paper as
work in progress. The basic test below needs only the older established
vertex/edge principles, not the unlocated full extension.

**Our K4 adaptation.** Let `A(x,y)` be the integral over `z,t` of
`W(x,z)W(y,z)W(x,t)W(y,t)W(z,t)`, and let `B` replace each factor by `1-W`.
Put `D=A-B`. Direct differentiation gives `delta F=6 integral D delta W`.
At a global minimizer, the feasible edge directions imply

```
W D <= 0,                 (1-W) D >= 0   almost everywhere.
```

Thus `D=0` wherever `0<W<1`; at hard 0/1 entries the conditions are one-sided.
For any two-rooted feature vector `f`, the matrices
`E[-W D f f^T]` and `E[(1-W)D f f^T]` are PSD at a minimizer.
They are NOT universal graphon inequalities. Rooted stationarity also gives
`E[(R-F)g]=0` for one-rooted features `g`.

**Why this could matter.** Compactness ensures that the global minimum is
attained, so a relaxation retaining every minimizer still bounds `c4` from
below. This avoids importing unjustified properties of our construction.
Unlike lane B's universal squares, these are objective-dependent restrictions
on possible optimizers. C's cut is an inexpensive compressed version of the
vertex-stationarity idea, not the whole set of derivative restrictions.

**Cheapest discriminating test.** Independently derive red and blue localizer
coefficients with two-root flags having one free vertex. The product uses
at most six vertices: two roots, two vertices for `D`, two for `f f^T`.
Add the two localizers to the existing N6 control, preserving shared moments;
compare with the unchanged control and C's N7 cut separately. A dual needs an
exact coefficient/PSD check PLUS the minimizer-reduction argument. Testing an
inequality on arbitrary nonoptimal graphons is not its soundness criterion.
Do not assume our incumbent is exactly stationary or feasible for these cuts.

**Decision: pursue.** No gain is predicted; this is a distinct small test.
Do not advertise minimizer-only constraints as a novel method.

#### Focused comparison with C3: what is actually additional?

Read the completed `lower-frontier-C.md`, including its exported
`B_root-U F<=0` row (`B_root=E R^2`, `U=0.030138888`). At an exact minimizer,
the classical vertex-variation identity already yields `R=F` almost
everywhere. Consequently `B_root=F^2=c4^2<=U c4`. Thus the soundness of C3
does not need the new quantitative coefficient in C1; C1 additionally controls
near-minimizers and provides a minimizing-sequence route. The constant in C1
was not located in the inspected sources, and novelty remains unestablished.
C3 is a practical application of established optimality conditioning.

The edge conditions concern different variations: change edge probabilities
while holding vertex measure fixed. They are not consequences of constant
root participation alone. For example, `W=p` has `R=F` for every p, whereas
`D=p^5-(1-p)^5` violates the two-sided interior edge condition unless p=1/2.
This example proves logical independence from rooted stationarity, NOT a
separation of C's actual constrained relaxation: these constant graphons have
`F>=1/32>U` and so fail C3's upper-threshold restriction. Whether the edge
localizers cut the surviving N7/N9 pseudo-moments is an unperformed test.

**Swaps should not be our first added family.** For the ordinary leading-order
swap of a present red edge `e` with an absent red edge `f`, the change is
proportional to `D(f)-D(e)`. The pointwise red-deletion and blue-deletion
conditions already make both contributions nonnegative. For a fixed finite
hinge/swap, copies of K4 containing both changed edges are lower order in n,
so do not create a new first-order term. This is our applicability inference,
not a general theorem about every operation in Brosch's program. Swaps can
matter when edge density is constrained, or when a truncated implementation
lacks the multipliers needed to derive their rows. Our unconstrained c4
problem has no edge-density constraint. Require an explicit truncated-cone
separation before paying for a separate swap family; do not count it as an
independent mathematical strengthening merely because the move is different.

For review, the elementary graphon edge argument is self-contained: if D>0
on a positive-measure part of W>0, decrease W there by a sufficiently small
feasible amount; the first variation is negative. If D<0 on a part of W<1,
increase W there. Bounded polynomial remainder and a positive-margin subset
justify the contradiction. This argument needs no prescribed c4 value,
regularity, finite support or Clebsch hypothesis. The proposed localizer
coefficients and certificate implications still need independent checking.

### 2. Select flags by edge support, not just by all graphs on N vertices

**Source.** Brosch's 2022 thesis is documented by its
[university publication record](https://research.tilburguniversity.edu/en/publications/symmetry-reduction-in-convex-optimization-with-applications-in-co).
The directly inspected [FlagSOS documentation](https://www.danielbrosch.com/FlagSOS.jl/stable/)
specifies `LasserreModel`, `addLasserreBlock!`, `QuadraticModule`,
`EqualityModule` and `HarmonicFlag`. It allows an empty block populated with
selected generators, or edge/predicate and vertex limits. The documentation
explicitly distinguishes a fully reduced Lasserre model from its partially
reduced Razborov model; a non-induced basis change alone returns the same
hierarchy bound. The [Mantel example](https://www.danielbrosch.com/FlagSOS.jl/stable/examples/TriangleFreeGraphs/)
is dated May 14, 2024. Current repository:
[FlagSOS.jl](https://github.com/DanielBrosch/FlagSOS.jl).

**Our application and assumptions.** We need a sparse collection of coupled
motifs, not merely fewer PSD blocks over all 137,352 N9 quotient variables.
Partially specified graphs can retain a few useful high-vertex products
without naming every induced graph. Shared products still must identify the
same moment, and positivity/probability constraints must be preserved.
Color-complement expansion can destroy apparent sparsity.

**Cheapest test.** On paper first, enumerate the product support of the proposed
edge localizers and six-root anchor features, including all required equalities
and complement partners. Compare that support with the existing formulation.
If materially smaller, reproduce a checked small bound through the new basis
before enlargement. Documentation supports quadratic modules, but no automatic
derivative generator or K4-ready sparse closure was verified.

**Decision: pursue a dimension census, then revise or retire.** This is a
representation option, not evidence that selective flags beat full N9 or that
changing software alone yields stronger mathematics. No new installation now.

### 3. Analytic inequalities beyond pure flag SOS deserve a targeted screen

**Source.** Blekherman–Raymond–Singh–Thomas,
[*Tropicalization of Graph Profiles*, v2 February 3, 2022](https://arxiv.org/html/2004.05207v2),
Theorem 5.1, Corollaries 5.2 and 5.12. They establish exact SOS obstructions,
including the odd-length Blakley–Roy path inequality, and specify the
translation between gluing and induced-flag languages. The obstruction is
about the stated proof cones and binomial forms; it does not prove that
additive-error lower bounds for our K4 objective cannot converge.

**Our application.** For ordinary nonnegative `W`, the three-edge path obeys
`t(P4,W)>=t(K2,W)^3`. Add the color-complement counterpart. In a linear moment
program the cubic term must be represented by the density of three disjoint
edges, not by cubing a pseudo-moment. In a fixed-edge-density subproblem the
right side instead becomes a scalar. The theorem does not justify applying
this to signed centered bridge kernels or mixed decorated paths.

**Cheapest test.** Evaluate the exact six-vertex linear rows
`P4-3K2` and their complements on saved primal witnesses; audit whether the
actual relaxation (including induced nonnegativity) already implies them.
If no separation, stop rather than adding them ceremonially. Non-SOS results
do not guarantee a violation by our witness.

**Decision: pursue only the inexpensive separation/containment test.** Older
math, newly relevant to the redundancy obstacle; no new inequality claimed.

### 4. Rooted stationarity has substantial prior art; structural stability needs more

**Established source.** Kim–Liu–Pikhurko–Sharifzadeh,
[*Asymptotic Structure for the Clique Density Theorem*](https://arxiv.org/html/1906.05942v2),
published December 30, 2020: Section 3.1, Claim 1 and equations (3.2)–(3.6)
explicitly change the vertex measure to force a rooted contribution identity.
Section 3.2, Claim 3 uses edge perturbations. The problem fixes a one-color
edge density and has a known sharp clique-density function, so its structural
conclusions cannot be copied to two-color K4.

**Recent source.** Chen–Liu,
[*Exact extremal constructions for the inducibility of blowup graphs*](https://arxiv.org/html/2606.06202v1),
June 4, 2026: Lemma 2.5 uses vertex cloning for finite local optimality;
Proposition 3.1 and Section 3.2 then use pre-existing weighted/rooted stability
and a cleaning argument. The objective is induced copies of a sufficiently
large blowup of a fixed graph, not our four-vertex objective. Theorem 1.3
therefore does not force a Clebsch blowup in our problem.

**Our application.** Cite the measure-variation lineage when writing C's result.
The particular quantitative constant in C's variance bound was not found in
these sources; that is not evidence of novelty. The useful structural lesson
is that equal rooted participation is a first stage. It needs an independent
local row-classification/stability lemma before it identifies a template.

**Cheapest test.** Review C's proof against the established perturbation
argument and retain its exact irregular-degree counterexample as a required
control for every proposed structural consequence. Identify a precise
additional condition that excludes that control before seeking Clebsch
rigidity. No new numerical search is needed for this review.

**Decision: use for attribution and revise the structural claim.** Do not
equate stationarity with regularity, a finite blowup, uniqueness or optimality.

### 5. A recent solver avoids the dense Schur layout, with a relevant failure mode

**Source.** Brosch–Schwiddessen–Wiegele,
[*The Augmented Mixing Method*, July 27, 2025](https://arxiv.org/html/2507.20386v1),
Sections 3.1–3.5 and 4.3–4.7; [public implementation](https://github.com/jschwiddessen/AugmentedMixing.jl).
It uses factored PSD matrices and column updates, supports general affine
equalities/inequalities, multiple blocks and higher precision. Its setup
assumes independent constraints and primal/dual Slater conditions.
Section 4.5 explicitly gives failures despite Slater, including stagnation
when the objective depends on a scalar block, a pattern in moment/SOS models.
There is no convergence guarantee.

**Our application/test.** A's 140.56-GiB dense Schur estimate is not an inherent
memory lower bound. Benchmark a exported small SDP against CSDP, measuring
residuals, memory and exact-certification loss. Check rank choices and data
storage before N9: many constraints may eliminate the rank savings. Factor
the certificate matrices directly if useful, then verify all inequalities
independently. Numerical precision is not exact certification.

**Decision: conditional benchmark candidate.** Stronger relevance than generic
solver publicity, but not a reason to replace working infrastructure now.

### 6. Higher cycle profiles: an actual 2026 theorem, but lower immediate priority

**Source.** Blekherman–Raymond,
[*Ubiquity of Power Sums in Graph Profiles*](https://www.combinatorics.org/ojs/index.php/eljc/article/download/v33i1p24/pdf/),
February 13, 2026: Section 3.1, Theorem 4, and Section 3.3, Corollary 14.
Ratios of 4k-cycle/necklace densities form power-sum profiles. The introduction
and Remark 15 explicitly leave absolute scale information unresolved.

**Our application.** A common self-adjoint operator links all its even-cycle
moments through one spectrum. This offers stronger joint consistency than
checking each trace separately. It does not make an arbitrary mixed bridge
cycle a power sum, or realize the full motif profile.

**Cheapest test.** Inventory whether an existing relaxed path system actually
contains repeated powers of one common operator. If it does, check its
normalized cycle moments against the power-sum constraints; handle zero
denominators separately. If it contains only unrelated mixed traces, retire
the direct transfer. Going to C8/C12 or necklace moments could cost more than
the current N9 problem, so do not generate them merely to use this theorem.

**Decision: reserve.** Useful profile geometry, no current separation or K4 gain.

## Frontier check and excluded leads

The original GLLV text, [*On tripartite common graphs*, Section 5](https://arxiv.org/html/2012.02057),
states the N9 lower bound `1/33.77`, approximately 0.0296. Its version history
is older than the dynamically rendered date in the HTML; do not call this a
new 2026 theorem. [KPS v1, Section 7](https://arxiv.org/html/2312.08049v1#S7)
explicitly labels 0.02961 floating-point output without exact rationalization.
The July 2026 [journal record](https://www.sciencedirect.com/science/article/pii/S0095895626000080)
was located, but full journal text was not retrieved reliably. An alternate
[DMD 2024 proceedings source](https://publicaciones.uah.es/export/sites/publicaciones/.galleries/Galeria-Servicio-de-Publicaciones/primeras-paginas/9788418979385p.pdf)
mentions the same number, not a newly located certificate. A owns repository
recovery, so this lane did not duplicate its archaeology.

The [January 21, 2026 Feinstein seminar](https://math.technion.ac.il/events/noam-feinstein/)
still supplies only `c4<0.030139`, describing structured randomized
constructions. No newer exact value, preprint or full construction was located
in this search. This is a statement about search results, not proof none exists.
Our record/overlap status remains unknown.

The July 2026 local-flag and Lean papers, January 2026 toolbox, Clebsch
reconstruction gadget, Godsil–McKay switching and sparse-plus-low-rank SDP
paper are already in our notes. They are not counted as new discoveries.
The local triangle-free/degree-five hypotheses still cannot be imposed here.
Current B's exact pointwise-transport counterexample strengthens that warning.

Other hits excluded: threshold Ramsey multiplicity (different finite problem),
canonical/ordered Ramsey numbers, additive Rado multiplicity, unrelated
“FlagSparse” software, and K4-minor spectral results. A September 2026 AI
research page reports a c4,5 construction, but this is a different objective
and its artifact was not audited; it is not evidence of a symmetric c4 record.
General undecidability/non-SOS results are barriers to particular proof
systems, not evidence that this specific extremal value is inaccessible.

## Search log and evidence hygiene

Primary-source sweep, 2026-09-30 approximately 04:07–04:16 UTC:

| Search family | Follow-up inspected | Outcome |
|---|---|---|
| K4/Ramsey multiplicity 2025–2026; exact decimals; Feinstein/Even-Zohar | Technion, GLLV, KPS arXiv/journal record, DMD | No new verified symmetric frontier found |
| Graphon reweighting/variational stability | Kim et al. §3; Chen–Liu §2–3; Diao et al. §4.3 | Prior art and transfer boundaries for C |
| Non-SOS graph-density inequalities | Tropicalization §5 and corollaries | Concrete analytic-cut screen; no K4 impossibility claim |
| Symmetry-reduced flag hierarchies | FlagSOS official API/examples, Brosch thesis record/talks | Selected-generator and quadratic-module options |
| Derivatives/optimality conditions in flags | Razborov §4; ISCO 2024 text; Graz 2025 slides; EUCCO 2025 listing | Strongest actionable mechanism |
| Large-scale SDP 2024–2026 | Augmented Mixing full relevant sections and repository | Possible memory alternative, material convergence caveat |
| Recent graph profiles | Power-sum paper §3, Remark 15 | Secondary joint-moment consistency lead |

Search snippets and review aggregators were used only to locate primary
sources. Claims above are grounded in the linked author/publisher texts.
Thesis PDF endpoints and some journal pages failed through the browser; no
unread theorem number from them is asserted. The 2025 EUCCO slides require
client rendering, so the directly readable Graz slides and conference text
are the evidence for the newer derivative extension. Dates come from source
metadata/events rather than search-engine crawl ages. No authors contacted.

## Handoff

Recommend one bounded future N6 red/blue optimality-localizer pilot, with C's
seven-vertex stationarity cut as a separately measured control. This is a
proposal only: no experiment launched. Keep A's recovery results and B's
negative evidence; do not rerun their failed universal transfers. All work
in this literature lane is complete, with no background process left running.
