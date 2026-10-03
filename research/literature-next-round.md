# Literature synthesis and a new stochastic construction screen

2026-09-27, literature_synthesis worker. Contract: local-only, one CPU after
19:44 UTC, no paid/remote computation or author contact, hard deadline
20:03:30 UTC. The question is asymptotic K4 Ramsey multiplicity, not R(4,t).
This worker uses the hypothesis-research protocol. The binary and weighted
Lean checkers were not modified.

## Concrete outcome

Final retained result of this worker (19:56 UTC): the two-parameter family
below gives

    515776850799050572477656236153 / 17113283103081096920205493272576
    = 0.03013897728988013...

Exact parameters: p=51064/65536, h=35015/65536.
`reports/literature-two-parameter-001/graphon-candidate.json`, SHA256
`e26e754168010c069da3e0b207a140f2c7cbbfc36cc0a6af06ef409db5024450`.
The independent full ordered-index audit passed. A more readable representative
p=32/41,h=22/41 gives
1013294255057839/33620705806123008 = .03013899413358829, also independently
audited, in `reports/literature-simple-graphon-001/graphon-candidate.json`.
Its SHA256 is `33e2e141890bd1982f4233139bfcc904dfea845a109249f97c0bc264f5806f59`.
No probability tuning continues after the parent's 19:56 reallocation.

The initial six-class breakthrough was:

A rational 192-block stochastic graphon, derived from the published seed's
four-vertex fibers, has exact density

    437229486076672219041203 / 14507109835375550096474112
    = 0.030138979509928936...

Artifact: `reports/literature-refined-graphon-001/graphon-candidate.json`.
SHA256: `d005fba8d1c4218cc52381eee8ef9d67b8a9068df8d56373de19843b2d341f9d`.
`independent-audit.json` records a separate full ordered-index C++ recount.
The search counter used equality partitions; the audit directly sums all
ordered quadruples and does not use class labels or partition coefficients.
Thirty tiny random matrices were also checked against Python literal ordered
tuples. These are exact executed counts, not Lean proofs. The asymptotic
realization argument below has received a conceptual peer review from the
progress_updates worker, not a formal verification.

This value is below McKay's supplied fraction and below the decimal threshold
0.030139 in the Feinstein–Even-Zohar announcement. It does **not** establish an
improvement over their actual result: their exact value/construction was not
retrieved. The overlap with their structured random constructions is unknown.
No novelty or global optimality is claimed.

## Sources and what transfers

1. [Parczyk–Pokutta–Spiegel–Szabó, v3](https://arxiv.org/html/2206.04036v3),
   §§3.3.1 and 6: the seed is a Cayley construction; the discussion asks for
   deeper understanding of its generating sets. I did not locate an explicit
   192-fiber/four-sheet voltage description in the inspected text. This is a
   search finding, not evidence that the representation is new. Their old
   product-family experiments argue against another blind small-factor sweep.
2. [Gross–Tucker 1977](https://doi.org/10.1016/0012-365X(77)90131-5) develops
   permutation voltage covers. [Gross–Tucker 1979](https://doi.org/10.1111/j.1749-6632.1979.tb32796.x)
   emphasizes cycle-basis voltage calculations. The transfer is gauge-invariant
   cycle constraints. Their covering framework applies to the missing matchings,
   not automatically to all the dense graph's monochromatic motifs.
3. [Diao–Guillot–Khare–Rajaratnam](https://arxiv.org/abs/1403.3736) develops
   derivatives of homomorphism-density graphon parameters. This supports using
   derivatives to expose a restricted family's missing directions. Our exact
   finite class-probability and vertex-mass formulas below are elementary
   derivations, not claims taken from that paper.
4. [Official Technion announcement](https://math.technion.ac.il/events/noam-feinstein/)
   states c4 < 0.030139 and structured randomized constructions. A further
   [RSA 2025 abstract](https://www.dmg.tuwien.ac.at/rsa2025/), August 7,
   already announces this work with Even-Zohar, without an exact bound or
   witness. Thus the public announcement predates January 2026. Searches by
   names, title and bound did not retrieve a usable preprint or thesis; that
   does not imply one does not exist.

## H-LIT-1: replace four-sheet constraints by a stochastic block model

Prediction: the empirical block densities can perform better when realized by
independent edges between much larger fibers. This changes the construction
family, not merely the seed or annealing parameters. An initial failure would
show that this particular independent-edge limit loses useful correlations;
it would not rule out correlated random constructions.

For n=192 equal-mass classes and a symmetric matrix P in [0,1], define

    F(P) = n^(-4) sum_(i,j,k,l)
             [Pij Pik Pil Pjk Pjl Pkl
              +(1-Pij)(1-Pik)(1-Pil)(1-Pjk)(1-Pjl)(1-Pkl)].

The observed four-sheet blocks give P values 0, 1/2, 3/4, 1, with Pii=0.
The initial exact density was 9103117/301989888 = .030143780840767756,
equivalent to N=10486790784 at denominator768^4. This improves the original
published seed by374400 numerator units but not McKay.

Mechanism tests and revisions:

| Test | Concrete result | Decision |
|---|---|---|
| Original block densities | .030143780840767756 | Optimize probabilities |
| One defect probability, one half-block probability, one diagonal probability | d=195/256,h=134/256,q=0; .030142509185743016 | Split mechanism-specific defect types |
| Distinguish defects in zero vs two D-D-H triangles | .03014241423856648 | Inspect unrestricted probability derivatives |
| Derivative diagnostic | 1056 complete blocks have improving inward directions | Free their two gradient classes; split defect gradients |
| Six-class rational optimization | .030138979509928936, independently recounted | Retain construction; audit and refine |

Artifacts, respectively: `reports/literature-soft-quotient-001`,
`literature-soft-family-001`, `literature-class-graphon-001`,
`literature-graphon-gradient-001`, `literature-refined-graphon-001`.
The first three search batches took approximately1.23s,3.77s,8.89s; the
six-class batch took13.40s. These are exploratory comparisons, not a matched
algorithm-performance study.

The six variable class probabilities in artifact order are

    [4096,3224,3162,3159,2187,3224] / 4096.

The 192×192 integer class matrix is the explicit specification; grouping was
discovered with floating derivatives but every candidate evaluation is integer
arithmetic. The decisive change softens 96 formerly complete blocks to
3224/4096. The other class of960 formerly complete blocks returns to1.
Empty blocks and diagonals stay0. At the retained candidate, the analytic
gradient has no improving boundary coordinate, but this is only a numerical
first-order diagnostic; it proves no local or global optimum.

The derivative used to propose classes is, for i≠j,

    ∂(n^4 F)/∂Pij = 12 sum_(k,l)
      [Pik Pjk Pil Pjl Pkl
       -(1-Pik)(1-Pjk)(1-Pil)(1-Pjl)(1-Pkl)].

For i=j the coefficient is6. This differentiates the full ordered expression,
so repeated class indices and repeated matrix variables receive all their
product-rule contributions. Derivatives are a search guide; the exact count
does not depend on their correctness.

### Why this graphon gives an asymptotic construction

For each m, create192 classes of m distinct vertices. For each unordered pair
of distinct vertices independently choose red with probability Pij, according
to its classes. Since Pii=0, all within-class edges are blue. Distinct vertex
edges remain independent even when some of their endpoint classes coincide.
Therefore the monochromatic probability for four distinct vertices is the
product of the six probabilities, or the corresponding blue product.

The class distribution of a uniformly sampled distinct four-tuple converges
to four independent uniform class indices as m→∞. Hence the expected
monochromatic K4 fraction converges to F(P). For every m at least one coloring
has fraction at most that expectation, so the Ramsey multiplicity limit is
at most F(P). This argument requires neither rational sampling nor a binary
finite template with the same count. Rational probabilities make the density
recount exact. It does not use the unit-weight numerator formula on P.

Important mismatch avoided: choosing each edge of a192-vertex template once
and reusing it across its blow-up would couple distinct vertex edges. That is
a different model and does not justify this formula.

## H-LIT-2: use voltage holonomy, with all competing motifs retained

Classical voltage theory suggests searching cycle invariants rather than
gauge-equivalent relabelings. Our inclusion–exclusion derivation: on four
distinct fibers with J−P along a defect C4 and complete blocks on both
diagonals, red transversal K4 count equals a voltage-independent constant
plus Fix(product of voltages around the cycle). Thus an odd/nonzero V4 flux
can help this particular motif. It does not imply that eliminating blue
partial triangles improves the full objective.

The algebraic worker found that anti-triangle assignments actually worsen
the total despite removing3840 blue triangles. This is a useful falsification
of the naive triangle-only surrogate. Aligned-bit controls improve the raw
seed. Its proposed exact second-bit XOR model passes the following conditional
reasoning check: if independent second-bit gauge changes at every fiber
preserve every half-block, Fourier support on defect variables must have even
degree at every base vertex. Since the defect quotient is triangle-free and
K4 terms involve at most four distinct fibers, the only nonconstant support
is a C4. Repeated-fiber terms have no such support. Fixed first-bit assignments
can alter coefficients; recompute them rather than assuming universal signs.
The algebraic worker owns implementation and exact full-count validation.

Cheapest discriminating test: explicitly verify every claimed gauge symmetry,
then compare XOR predictions against full counts for random bit assignments.
Failure identifies an omitted block constraint or repeated-index term. Do
not continue a long XOR search until those comparisons pass.

## H-LIT-3: collective block masses, beyond pairwise transfers

This is a separate representation family. Let H be the Hessian of the exact
weighted numerator at uniform masses. Existing pair-transfer coefficients
satisfy Buv = (Huu+Hvv−2Huv)/2. In the anchored zero-sum basis ei−e0,

    Kii = 2 Bi0,
    Kij = Bi0 + Bj0 − Bij.

Thus the pair screen already supplies the constrained Hessian on any selected
subset. Positive curvature on each pair-transfer direction does not imply K
is positive semidefinite. A collective negative-curvature direction may exist
even in a vertex-transitive seed with zero projected gradient. For asymmetric
incumbents, collective gradient/Newton directions are cheaper initial tests.
The progress_updates worker owns this track and has independently tiny-tested
the formulas. Candidate promotion uses the separate weighted Lean checker,
not this graphon counter.

Decision ranking: retain stochastic probability refinement because it produced
the largest new density change; continue the exact holonomy model because it
isolates a tested interaction; retain collective weights as an independent
family with its own verifier. None is evidence of global optimality, and
parameter sweeps within one are not counted as new hypothesis families.

## Final simplification: two probabilities and an explicit polynomial

All1152 pairs comprising the original1056 defect blocks and the96 newly
softened complete blocks can share probability p. The96 original half-block
pairs share probability h; all other pairs remain0 or1 and all diagonals0.
The final class matrix is `reports/literature-two-parameter-001/classes.json`,
where -1 means0, -2 means1, 0 meansp, and1 meansh. Every vertex has12 p-neighbors,
one h-neighbor,87 probability-one neighbors, and91 off-diagonal zero-neighbors.

An independently computed ordered pattern histogram gives the compact formula

    F(p,h) = [R(p,h) + B(1-p,1-h)] / 192^3,
    R(p,h) = 54360 +4560h +120h² +46080p +20160p²
             +2880p²h +960p³ +180p⁴ +360p⁴h +36p⁴h²,
    B(x,y) = 87200 +5808y +660y² +4y³ +3y⁴ +69696x
             +25920x² +3168x²y +3648x³ +144x³y²
             +576x⁴ +432x⁴y +36x⁴y².

The histogram was computed on sorted four-tuples with generic multiplicities,
and its evaluation agreed with the original equality-partition counter and
the separate direct ordered-index counter. This gives three differently
organized exact computations, but still not a formal counting theorem.

## Closest-prior comparison, timeboxed 19:56–19:59 UTC

Inspected the official author [homepage](https://chaime.net.technion.ac.il/)
and its linked [GitHub account](https://github.com/chaim-e). The public API
listed nine repositories, none describing Ramsey constructions. Direct
arXiv author-search requests failed to fetch; indexed searches by both names,
title, "graphon", "stochastic block", exact/rounded numerical bounds, thesis,
and an alternate spelling found no exact witness. This is not an exhaustive
literature clearance. The direct primary comparison remains the RSA2025 and
Technion2026 announcements cited above. Their description is compatible with
the family found here, so rediscovery is a serious unresolved possibility.
No external contact was made.

## One new mechanism after stopping precision sweeps: latent type splitting

H-LIT-4, delegated to algebraic_round for the deadline-bounded test. Split every
class into equal latent types s=±1 and set

    P'((i,s),(j,t)) = Pij + epsilon*s*t*Cij,

where C is symmetric, Cii=0, and its support lies on fractional-probability
pairs. This preserves each coarse block's mean probability but changes
correlations among edge probabilities after latent types are integrated out.
It is a structural refinement, not a different value of p or h.

For four independently sampled latent signs, a perturbation edge subset
survives averaging exactly when all four positional degrees are even. The
only nonempty such subgraphs of K4 are its four triangles and three C4s.
Consequently the density is exactly F0+A epsilon³+B epsilon⁴. This includes
repeated coarse-class indices: their sampled latent signs are still
independent. In particular, a C supported on a single coarse triangle can
still give nonzero quartic terms through backtracking coarse-index cycles.

For C=1 on all fractional pairs and the simple41-denominator candidate, a
short exact diagnostic found1152 supported coarse triangles, each with

    sum_l [Pil Pjl Pkl -(1-Pil)(1-Pjl)(1-Pkl)] = 59119/41³.

Thus A=24*1152*59119/(41³*192⁴)>0. For this nonnegative C, B>=0. Sufficiently
small negative epsilon gives a strict improvement if the expansion and
representation are implemented as stated. The exact minimum of this one-line
quartic is at epsilon=-3A/(4B) when B>0 and that point is admissible. Probability
constraints permit |epsilon|<=9/41 here. The algebraic worker owns the new
384-block materialization and independent count; no such candidate is claimed
by this note before its returned audit. A no-gain numerical test must challenge
the expansion or implementation, since the computed nonzero cubic predicts
an arbitrarily small feasible improvement.

At handoff this literature worker has no active computation or subprocess.
