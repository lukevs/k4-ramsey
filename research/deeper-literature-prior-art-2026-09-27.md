# Structural and search mechanisms from the 2024--2026 literature

Date of check: 2026-09-27. This is a mechanism-transfer note, not a claim that
any cited work improves the symmetric `K4` Ramsey multiplicity bound. No
experiments were run in this lane.

## Ranked shortlist

### 1. Direct implicit-neural graphon optimisation

Primary source: [*Implicit Neural Representation of Graphons for Asymptotic
Extremal Problems in Graph Theory*](https://openreview.net/pdf?id=ejqxghoKNO),
anonymous ICLR 2026 submission, still labelled **under double-blind review** in
the public PDF at the time checked. This is not an accepted-paper claim. The
[NeurIPS 2026 downloads index](https://neurips.cc/Downloads/2026) now lists an
accepted poster titled *Implicit Neural Representations for Variational
Problems on Graphons*. The poster metadata was not publicly accessible in this
check, so I could not verify whether it is a renamed/final version of the
OpenReview work; the two records should not yet be conflated.

The method directly represents a symmetric graphon by a neural network and
differentiates Monte-Carlo estimates of homomorphism-density objectives. A
plain MLP is reported to miss the discontinuous step boundaries typical of
extremisers, so the proposed network uses multiple, varying-scale sinusoidal
input encodings. For constrained problems it solves an empirical density
constraint inside the forward pass and differentiates through that solver.
Fresh latent samples are used at each update. Cosine learning-rate cycles are
used to alternate broad structural search with boundary fitting. The paper
rediscovers several known extremal graphons and reports candidate
counterexamples for open homomorphism-density inequalities; those numerical
candidates are not proofs.

**Transfer.** Our objective needs no edge-density constraint:
`t(K4,W) + t(K4,1-W)` can be estimated and differentiated directly. This is a
resolution-free family, rather than another fixed orbital/step template, and
therefore tests whether the current search is losing primarily through its
chosen partition.

**Cheapest discriminating test.** Use one small, symmetric multiscale-Fourier
network and fixed-budget restarts. First require it to recover (a) the constant
`1/2` value `1/32` and (b) the score and visible block structure of one known
step graphon. Only then optimise the target. Recount every output on independent
samples, rasterise it, and exact-score/refine the raster with the existing
evaluator. Failure of a plain MLP is not a useful control: the paper itself
identifies that architecture as biased toward smooth solutions.

**Mismatch/risk.** Monte-Carlo error is dangerous at the fourth decimal place;
the representation may yield an opaque, non-exact witness; and the source is an
unreviewed anonymous submission. The independent recount and finite-step
projection are mandatory. This overlaps our continuous graphon optimisation in
objective only, not in representation.

### 2. PatternBoost's local/global population loop

Primary source: Charton--Ellenberg--Wagner--Williamson,
[*PatternBoost: Constructions in Mathematics with a Little Help from
AI*](https://arxiv.org/html/2411.00566), arXiv:2411.00566v1, 1 November 2024.
The paper links [public experiment
code](https://github.com/zawagner22/transformers_math_experiments).

The exact useful mechanism is not merely "use a transformer." It repeatedly
(1) creates many locally optimised constructions, (2) retains an elite subset,
(3) learns the joint distribution of their serialized structure, (4) samples
new structures, and (5) locally repairs those samples. In the 20-vertex
triangle-free example, the initial 40,000 local searches found score 99 only
twice; 37,000 valid learned samples followed by the same local search produced
score 99 forty-seven times and the optimum 100 forty-six times. The paper also
shows that its global-only control is poor, and its `C4`-free study exposes very
large sample costs and tokenisation sensitivity.

**Transfer.** Serialize a canonical relation vector (not a labelled adjacency
matrix), train/sample only from a structurally diverse elite archive, then pass
samples through exactly the same local optimiser used for controls. This
targets cross-variable correlations between good basins rather than one-more
restart near the incumbent.

**Cheapest discriminating test.** Before installing or training a transformer,
fit an elite empirical generator: marginal logits plus pairwise conditionals,
or a shallow autoregressive table in canonical variable order. Under a matched
number of objective evaluations, compare the post-local-search improvement and
distinct-basin yield with (i) independent random starts and (ii) elite
resampling plus matched perturbations. Reject the idea if it only reproduces
one isomorphism class or if generation/training cost erases the gain.

**Mismatch/risk.** Published examples are finite discrete constructions, not a
continuous graphon objective. Representation choice is a major confounder, and
the impressive examples consume millions of local searches. This overlaps the
existing portfolio loop but adds learned joint seeding, which that loop does
not currently have.

### 3. Heterogeneous recursive mixing of several templates

Primary source: Xizhi Liu and Oleg Pikhurko, [*Finite Hypergraph Families with
Rich Extremal Turan Constructions via Mixing
Patterns*](https://arxiv.org/abs/2212.08636), initial preprint 16 December 2022,
revised 2024/2026; [published online 6 March 2025 in *Forum of Mathematics,
Sigma*](https://www.cambridge.org/core/journals/forum-of-mathematics-sigma/article/finite-hypergraph-families-with-rich-extremal-turan-constructions-via-mixing-patterns/510C784B7C84C92B16CF02DB282E1BBB),
DOI 10.1017/fms.2025.12.

A pattern is a triple `P=(m,E,R)`: a finite part count, allowed edge profiles,
and the subset of parts in which construction recurses. The new structural
point is a finite *set* of patterns. At every recursive node one may choose a
different member of that set. For the forbidden hypergraph families constructed
in the paper, all maximum objects are exactly maximum mixed-pattern blowups,
and near-extremisers are close to such mixtures. Thus heterogeneous recursion
can be structurally essential; repeating one globally chosen kernel can miss an
entire extremal set.

**Transfer.** Our homogeneous recursive and scalar-polarisation tests do not
cover a branch-dependent `A/B` construction. Select two already-strong but
structurally different kernels, use `A` at the root and `B` inside one or two
positive-mass cells, then reverse the roles. Allow the recursive choice to
depend on the parent cell rather than forcing the same child kernel everywhere.

**Cheapest discriminating test.** Exact-score all depth-two `A->B`, `B->A`,
`A->A`, and `B->B` compositions for a tiny list of symmetry-inequivalent cells
and fixed inherited cell masses. Do not optimise a large recursive family until
a heterogeneous composition beats both homogeneous controls.

**Mismatch/risk.** The theorem is for specially engineered forbidden
`r`-uniform hypergraph Turan problems with `r >= 3`; it gives no inequality for
`t(K4,W)+t(K4,1-W)`. It is a structural precedent and a search-space correction,
not evidence that mixing will improve our bound.

### 4. Inverting or interpolating motif profiles (MomentNet)

Primary source: Marques--Sabharwal--Ramezanpour--Segarra--Tenorio,
[*A Few Moments Please: Scalable Graphon Learning via Moment
Matching*](https://arxiv.org/html/2506.04206), arXiv:2506.04206v1, 4 June
2025 (revised 17 June 2025).

MomentNet discards vertex identities after extracting induced motif densities
(ORCA is used for graphlets through five vertices), represents the unknown
graphon by an implicit neural function, estimates its induced motif densities
by differentiable Monte Carlo, and fits the target moment vector. MomentMixup
forms a convex combination in *moment space* and then solves the inverse
problem; the paper explicitly proves that this differs from pointwise graphon
mixing except for the edge-density coordinate.

**Transfer.** Record full induced four-vertex profiles, and optionally selected
five-vertex profiles, for diverse elite witnesses. Invert an interpolated or
slightly perturbed target profile into a small symmetric step graphon. This can
propose a construction between elite basins without presupposing a shared
labelling or common partition.

**Cheapest discriminating test.** First recover one known small step graphon
from its exact induced four-profile, up to relabelling, using the existing
step-graphon variables rather than a new INR stack. Then interpolate two elite
profiles and require a low moment residual *and* an independently exact-scored
realisation. A target with low requested `K4/co-K4` coordinates but a large
overall residual is simply infeasible evidence, not a candidate.

**Mismatch/risk.** This is graphon estimation and data augmentation, not
extremal optimisation. Finitely many moments do not identify a graphon, and an
arbitrary interpolated profile need not be realisable. If the `K4` and co-`K4`
coordinates themselves are fixed by interpolation, their sum cannot improve
on the endpoints; improvement requires a search/perturbation in feasible
profile space, not literal convex interpolation alone.

## Two lower-priority structural observations

- Liu--Pikhurko, [*A Note on Extremal Constructions for the
  Erdos--Rademacher Problem*](https://www.cambridge.org/core/journals/combinatorics-probability-and-computing/article/note-on-extremal-constructions-for-the-erdosrademacher-problem/861F9C17713FD1055F58598E6A4F058E),
  published online 10 October 2024, gives strong adjacent precedent for
  **localized substitution**: a complete multipartite coarse construction with
  a triangle-free graph inserted into one part. For our objective the cheap
  analogue is to split exactly one coarse cell, keep all of its cross-cell rows
  fixed, and test a few tiny inner kernels. The fixed-edge-density clique
  objective is different, so this is a move generator rather than a prediction.

- Jae-baek Lee's 2025 University of Victoria dissertation, [*The Ramsey
  Multiplicity
  Problem*](https://dspace.library.uvic.ca/bitstreams/449f12fd-fe7a-46f3-844b-6885d689a304/download),
  does not contain a new direct `c4` construction. Its Chapter 4 perturbation
  argument starts with a complement-of-Turan colouring and independently
  deletes each present edge with probability `epsilon`; it compares the
  first-order destruction of one monochromatic target with the first-order
  creation of the other through critical-edge colourings. The transferable
  item is an exact **directional-derivative census** for deciding which relation
  class to soften. It is already conceptually close to our soft-block
  perturbations, so it should not outrank the four mechanisms above.

## Recommended order

1. Run the depth-two heterogeneous `A/B` composition census: it is exact,
   structural, and cheapest.
2. Run PatternBoost-lite on the archive with matched-budget controls.
3. If neither changes the basin, pilot the direct multiscale-INR graphon on
   known controls before target optimisation.
4. Treat motif-profile inversion as a candidate generator only after the
   realizability/recovery control passes.
