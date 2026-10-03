# Root synthesis, round 2

Started2026-09-27 20:04 UTC. This is the coordinator's independent research
and redirection notebook. Experiments remain delegated to subagents.

## Target and evidence

The target is the smallest valid asymptotic monochromatic K4 density we can
establish, not merely McKay or the rounded January2026 announcement. The
Technion abstract states only `c(4) < 0.030139` and calls the construction
randomized, structured and symmetric; its exact value and construction are not
yet public in the sources located. Therefore `0.030139` is a coarse comparison
line, not the benchmark we must claim to have beaten.

Our strongest current object is the192-class rational independent-edge graphon
with density

    515776850799050572477656236153 /
    17113283103081096920205493272576

approximately `.03013897728988013`. It now has two exact C++ recounts and an
independent standalone compiled-Lean exact-`Nat` recount after20 tiny literal
oracle cases (`reports/graphon-precision-lean-001`). The first-moment lifting
argument has been independently audited in `graphon-realization-proof.md`.
This is strong construction evidence, not a kernel-only theorem or record claim.

Adjacent primary sources change the hypothesis portfolio:

- Sperfeld (2011, arXiv:1106.1030) reports that Thomason's1997 final paragraph
  already used a tiny random perturbation. Random softening is therefore not by
  itself a novelty claim.
- Parczyk–Pokutta–Spiegel–Szabó describe Even-Zohar–Linial's iterative
  composition as the only then-known nonstandard-blow-up construction and ask
  whether the K4 optimum is any finite blow-up.
- Diao–Guillot–Khare–Rajaratnam's graphon differential calculus supports
  organizing refinements by exact higher derivatives of homomorphism densities.

## H-ROOT-001: recursive typed refinement

**Mechanism.** Replace each scalar fractional coarse block not just by an iid
edge probability, but by a zero-mean finite-type kernel. The coarse gradient
cannot see such refinements. The exact K4 objective has degree six, so the
change is an exact sum of homogeneous forms of degree2 through6. The simple
two-type latent split already has a strict cubic improvement. If an improving
typed kernel can be substituted recursively, its accumulated density may have
a closed fixed-point expression, paralleling iterative composition but starting
from the new192-class quotient.

**Prediction.** A rank2 or higher refinement improves the precision graphon;
at least one improving mode remains improving, or leads to a better fixed point,
under a second self-similar substitution.

**Disconfirmation.** The exact precision-parent variation polynomial is
nonnegative throughout the admissible interval, or its one-level gain reverses
at the second substitution. That retires only the tested type kernel.

**Tests.** The latent-precision and three-state Potts lanes are the first
discriminators. If either is positive, derive the exact recursive density before
launching a generic parameter sweep. Preserve causal coefficients, not only the
winning value.

## H-ROOT-002: refinement tensor / association-scheme basis

**Mechanism.** For r microtypes, give each coarse pair a zero-row-sum symmetric
matrix C_ij, preserving its mean probability. Expand the exact objective and
diagonalize or otherwise optimize its degree2–6 forms in a small structured
basis: cyclic difference sets, characters of a finite abelian group, or a small
association scheme. Shared microtype coordinates create triangle and K4
correlations that independent scalar blocks cannot represent. This is not the
failed four-sheet rounding, which independently sampled a narrow regular-block
bank rather than optimizing coherent global intersection numbers.

**Prediction.** Some r<=5 structured basis direction beats the best rank-one
latent refinement on the same precision parent.

**Cheapest falsifier.** Exact motif/intersection coefficients for r=3 and r=5,
then an exact class-level recount of only the best preregistered direction.
Failure is restricted to those bases, not all graphon refinements.

## H-ROOT-003: exact joint quotient model, conditional on integrity audit

The finite lane has found19 improving single second-bit block toggles on the
stored cycle-opt parent where H-ALG-006 appeared to report single-variable
strict descent termination. This is an integrity trigger, not progress yet.
Possible explanations include parent mismatch, variable/gauge indexing,
coefficient construction, or an over-broad interpretation of the optimizer's
termination. Until an independent reviewer reconciles one move against the
stored parity coefficient and full recount, do not use the C4 model to guide a
joint first/second-bit hypothesis or promote descendants as model evidence.

## H-ROOT-004: optimize the recursive local-profile operator

Even-Zohar–Linial give a more precise route than literal repeated doubling:
composition acts linearly on the local4-profile once the outer construction's
without-replacement profile is fixed. Up to color-preserving isomorphism this is
a small finite state space (11 unlabeled four-vertex graph types in their
setting), and the infinitely nested construction is the stationary/Perron–
Frobenius profile of that transfer operator.

**Mechanism.** Parameterize a small typed probabilistic or deterministic
microkernel for the fractional block classes, derive its exact4-profile transfer
matrix, and optimize the stationary state's K4+anti-K4 coordinate. This evaluates
an infinite recursive family without materializing exponentially many classes.

**Prediction.** A kernel whose one-level variation has the observed negative
cubic interaction has a stationary profile below its single-level refinement;
alternatively, a different small kernel chosen directly by stationary-profile
gradient beats the rank-one split.

**Falsifier.** The exact transfer operator for the retained kernel has a unique
stationary profile no better than the one-level graphon. This rejects that
kernel, not recursive composition generally. The latent/Potts workers are
deriving the required state and must not approximate recursion by blindly
reusing a scalar coefficient.

## H-ROOT-005: neutral quotient plateaus as finite-basin portals

The apparent C4-model discrepancy resolved into a new mechanism. The stored
cycle optimum has no negative one-coordinate move, but it has exact zero moves.
After three zero toggles, a fourth coordinate has exact delta -480. Full native
and Lean recounts agree. Thus strict coordinate descent was correctly locally
minimal yet failed to explore its neutral component.

**Prediction.** Systematic traversal of the exact XOR objective's zero-gain
component exposes additional negative exits and distinct unrestricted-polish
basins more efficiently than arbitrary seed changes.

**Test.** Compare bounded neutral BFS/tabu against the original strict control
from identical parent/model; fully recount every retained exit, then apply the
same cached-star polish only to preregistered representatives. The first audited
plateau descendant already yields a new Lean-checked finite incumbent after
polish, N=10486204490/768^4. This supports the mechanism but does not establish
algorithmic superiority or plateau exhaustion.

## Management decisions

### Updated at 20:38 UTC

The finite-model integrity issue is resolved (neutral moves exposed negative
exits); matched neutral plateau polish did not improve the best unrestricted
basin. Finite search is checkpointed while larger graphon changes receive compute.

The independent compressed verifier is implemented and measured: current phase
candidate checking is3.102s vs111.658s direct. The combined checker trusts native
candidate-to-histogram binding and uses Lean for exact arithmetic; this is an
explicit evidence distinction, not a full Lean counting theorem.

Phase/amplitude alternation reached a coordinate fixed point at q=-7236, the
common amplitude's feasibility boundary. Candidate d93abf5... predicts
0.030138945918374207 and awaits independent check. Next mechanism H-ROOT-006:
separate amplitudes by coarse block type, because the p-block constraint clips
the h-block amplitude despite different probability slack. Use a multivariate
motif product, not a scalar coefficient fit with changing support.

Other active mechanisms: change kernel spectrum/group; reoptimize coarse
probabilities with frozen phases; derive coarse-support changes and bounds on
the improvement achievable within the existing centered family. Root's concern
is scale: simply improving this small correction may not reach a substantially
lower bound. Maintain structural exploration alongside exploitation.

The user has no numeric target/source beyond the belief that a much lower
value is possible. This informs ambition but is not prior-result evidence.

### Earlier decisions (superseded where noted above)

1. Prioritize exact January2026 construction recovery and record comparison.
2. Promote the precision graphon count only within its explicit evidence class.
3. Let the two refinement screens finish; use their exact variation terms to
   decide recursive versus association-scheme follow-up.
4. Pause further C4-model-guided finite work after the active exploratory run
   until the discrepancy is resolved.
5. Keep at least one independent construction family alive; do not turn eight
   workers into parameter variants of the current graphon.
