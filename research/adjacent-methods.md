# Adjacent research → testable hypotheses

Reviewed 2026-09-27. This is a targeted review, not an exhaustive bibliography.
The goal is to improve the actual K4 multiplicity upper bound, not merely pass
AutoLab. McKay is a milestone, not a stopping condition. No method below is
known to find the global optimum of this problem.

## What the review changes

Pursue two complementary kinds of experiment: exact coordinated edits to
existing graphs, and compact descriptions of different infinite families.
Do not spend the whole budget on annealing parameters. First implement reusable
restricted objectives and graph-profile operations that make many hypotheses cheap.

The papers supply methods and precedents. The proposed applications and
predictions below are ours and remain untested unless explicitly stated.

## 1. Pseudo-Boolean optimization: exploit the shape of the free edges

**Research.** Boros and Gruber describe reductions of higher-degree binary
objectives to quadratic ones, and discuss auxiliary-variable and coefficient
costs. Quadratic does not mean easy in general; submodularity is an important
special case. [On Quadratization of Pseudo-Boolean Functions](https://arxiv.org/html/1404.6538)

**Our transfer.** With all but a selected edge set fixed, the numerator is a
multilinear polynomial in the remaining binary edge variables, of degree at
most six. Avoid constructing the enormous global polynomial. Compile only
the terms affected by the selected variables.

There are useful exact special cases (our elementary derivations):

- **Matching neighborhood:** if the free edges are pairwise vertex-disjoint,
  any four-vertex set contains at most two free edges. Edge terms are linear,
  triangle terms contain at most one free edge, and K4 terms at most two.
  Therefore the restricted numerator is exactly quadratic, without auxiliary
  variables. This does NOT assume the overall improvement consists of a matching.
- **Star neighborhood:** if all free edges meet one vertex, a K4 contains at
  most three of them. The restricted objective has degree at most three.
- **General neighborhood:** degree-six terms may be needed. Pairwise-only
  approximations are not exact here.

For matching flip indicators z, extract coefficients by finite differences:

    N(z) = N(0) + sum_i a_i*z_i + sum_{i<j} b_ij*z_i*z_j
    a_i = N(e_i) - N(0)
    b_ij = N(e_i+e_j) - N(e_i) - N(e_j) + N(0).

Here e_i means flipping only edge i from the current graph. For disjoint edges,
their interaction arises only from the four endpoints. Coefficients can be
computed without four whole-graph recounts per pair; derive and test that shortcut.

Development sanity check on 2026-09-27: with RNG seed 20260927, tested all 32
assignments of five disjoint free edges on each of 20 random ten-vertex graphs.
All 640 quadratic predictions agreed with the C++ full counter. This uses the
same native implementation for deltas and recounts, so it is not independent
verification or a formal proof. No search improvement is claimed.

**H1: coordinated matching moves escape single-flip local minima.**
First compare polynomial predictions with every assignment on tiny instances.
Then free 12–20 disjoint candidate edges at a verified local minimum and solve
exactly. Compare against sequential descent and random free-edge selection at
equal total time, including neighborhood construction. An improvement establishes
useful interaction; failure proves only that specific neighborhood exhausted.

**H2: star neighborhoods capture improvements matching neighborhoods miss.**
Compile 12–20 incident free edges, test cubic predictions exhaustively, and
compare improvements per second with H1. Do not quadratize by default: first
measure direct enumeration/branch-and-bound against solver overhead.

## 2. Local branching / large-neighborhood search

**Research.** Fischetti and Lodi's local branching uses a Hamming-distance
constraint around an incumbent within a mixed-integer solver. Later work by
Liu, Fischetti, and Lodi emphasizes the effect of neighborhood size. We need
the neighborhood concept, not their learned controller.
[Original publication record](https://publications.polymtl.ca/25914/);
[author-hosted follow-up](https://www.dei.unipd.it/~fisch/papers/2021_learning_to_search_in_local_branching.pdf).

**Our transfer.** Distinguish two restrictions:

- Free k selected edges: a subcube of 2^k assignments.
- Permit at most r flips among M candidates: a Hamming ball containing
  sum_{j=0}^r binom(M,j) assignments.

An exact solver may prune either, but neither is automatically cheap. Repeatedly
change the free subset; do not mistake its exact optimum for a global certificate.

**H3: interaction-guided neighborhoods outperform independent low-cost edges.**
Construct small sets using large favorable pair interactions, compare with
random sets and best-single-delta sets, then adapt size based on solve time.
Record optimal / feasible-but-time-limited / infeasible separately. Require
independent recount of all accepted graph changes. No whole-graph MILP first.

## 3. Inducibility, XOR products, and recursive constructions

**Research.** Even-Zohar and Linial give a historical K4 multiplicity
improvement using nested compositions and XOR products. Sections 2–3 derive
small-graph profile operations: XOR corresponds to convolution of labeled
profiles, or componentwise multiplication after Fourier transformation;
composition is handled by a partition-based operator.
[A Note on the Inducibility of 4-vertex Graphs](https://arxiv.org/html/1312.1205).

**Our transfer.** Represent a construction through the distribution of the
64 labeled four-vertex edge patterns, retaining repeated-index semantics for
finite templates. Cache profiles of small factors, then evaluate many products
without materializing their full adjacency matrices. Track all necessary
lower-order information for composition; a scalar K4 count is insufficient.

**H4: searching construction expressions finds useful families cheaply.**
Implement exact rational profile arithmetic. Test XOR and composition formulas
against explicit tiny products, then reproduce the paper's historical limit
1411/46592 as a regression test. Search small expression trees built from
cached factors and nested constructions. Reconstruct and independently verify
promising finite instances, or certify the recurrence and limit for an infinite
family. Report the construction family searched, not a global guarantee.

**Caution from direct prior work.** Parczyk et al. report trying extensions of
earlier product-based approaches without substantial improvements. Their work
also gives weighted small templates and discusses the unresolved role of finite
versus iterated blow-ups. This argues for a cheap, bounded screen, not blind
faith in old products. [Sections 1.3 and 3.3.1](https://arxiv.org/html/2206.04036v3).

## 4. Graphon and block-weight optimization

**Research.** Harchaoui, Oh, Pal, Somani, and Tripathi study stochastic
optimization on permutation-invariant symmetric matrices and graphon limits.
This provides a continuous-optimization framework, not a global convergence
guarantee for our nonconvex K4 objective.
[Stochastic optimization on matrices and a graphon McKean–Vlasov limit](https://arxiv.org/abs/2210.00422).

**Our transfer, cheapest version.** Keep the binary template fixed and vary
normalized block weights p_i >= 0, sum p_i = 1. Its exact density is a quartic
polynomial in p. Start with derivatives and line searches, not neural networks.
The current unit-weight Lean checker must be extended before weighted results
can receive the same verification status.

At equal weights in a vertex-transitive seed, symmetry makes all gradient
coordinates equal. The projected gradient on the simplex is therefore zero:
ordinary first-order descent from the perfectly symmetric point can stall even
when a symmetry-breaking improvement exists. This is our symmetry argument.

**H5: unequal weights improve a symmetry-broken incumbent.**
Check gradient identities on tiny exact fixtures, compute directional
derivatives after edge optimization, and test pairwise mass transfers.
For the symmetric seed, instead test curvature in sum-zero directions and
small asymmetric starts. Rationalize promising weights and recount exactly.
No negative curvature found in sampled directions is not a positivity proof.

**H6: refining blocks reveals structure excluded by the initial template.**
Split selected blocks, perturb their connections, and compare density before
and after joint weight/edge optimization. Initially duplicate a block exactly
as a zero-change sanity test. Mixed diagonals, non-unit weights, and recursive
internals require explicit evaluator extensions rather than use of the current
unit-weight formula.

**Two different continuous models must not be confused.** Randomly choosing
each finite template edge once gives the multilinear extension of the discrete
objective (after reducing x^r=x). A fractional graphon instead assigns
probabilities to edges between independently sampled vertices; repeated block
pairs can contribute powers of that probability. They are not interchangeable.
Fractional graphons require their own construction/limit certificate; rounding
is a new candidate that must be recounted.

## 5. Newer direct result: lead, not reproduced evidence

A Technion seminar on 2026-01-21 by Noam Feinstein announces randomized,
structured constructions with c4 < 0.030139 and c5 < 0.001652, supervised by
Chaim Even Zohar. This is stronger than McKay's reference. The inspected
announcement supplies neither an exact c4 fraction nor a usable construction.
Do not invent either or treat a decimal threshold as a supplied witness.
[Official seminar announcement](https://math.technion.ac.il/events/noam-feinstein/).

Searches by author, title, numerical bound, and arXiv did not locate a
reproducible preprint in this pass. That is a search limitation, not evidence
none exists. Continue checking public thesis/preprint material; contacting
authors would require user authorization. This result reinforces the priority
of structural experiments but does not tell us their successful mechanism.

## Experiment order and decision rules

| Priority | Experiment | Smallest useful test | Decision signal |
|---|---|---|---|
| 1 | H1 matching polynomial | Exhaustive tiny fixtures, then 12–20 free edges | Exact multi-flip gain after single-flip descent |
| 1 | H4 profile arithmetic | Tiny product agreement, historical recurrence | Many exact construction evaluations per second |
| 2 | H2/H3 stars and local branching | Matched-time neighborhood comparison | Better gain per total second than H1 |
| 2 | H5 weight perturbations | Derivative checks and rational mass transfers | Exact improvement unavailable to equal weights |
| 3 | H6 block refinement | Density-preserving clone, then perturbation | Improvement retained after exact verification |

These are priorities, not separate long runs or permission to exceed the local
compute budget. Use short screens before repetitions or larger neighborhoods.
Every experiment records a hypothesis, prediction, parent artifact, source,
code/evaluator identities, total time, verified outcome, and next decision.
Negative results stay in the registry. A literature review is not an experiment;
this document claims no new numerical improvement.

## What we should not do yet

- Build a huge global QUBO, MaxSAT, or MILP instance before measuring restricted
  objective sparsity and exact-neighborhood costs.
- Assume a matching, regular graph, Cayley graph, or 768 blocks contains the
  global optimum. These are temporary experimental subspaces.
- Introduce neural graphon machinery before testing explicit block models.
  An OpenReview lead was access-blocked and is not used as verified evidence here.
- Claim optimality from heuristic plateaus. Universal lower bounds, for example
  via rigorously certified flag-algebra inequalities, are a separate proof track.
- Claim novelty simply for passing McKay or the rounded 0.030139 threshold.
