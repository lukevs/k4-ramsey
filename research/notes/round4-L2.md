# Round 4, lane L2: can the Clebsch-based construction be proved optimal?

Window: 2026-09-27, 22:56–23:10 UTC. Web reading and one tiny sanity script only (Clebsch invariants and gap arithmetic, in seconds). No outreach, no commits.

Incumbent: 0.030138895816959867. This is the 3840-class G/K orbital kernel from E4, which descends from B192.

B192 itself is Cay(F2^4 x Z3 x F2^2, w), with Clebsch blocks and a two-level design (E11). Its value is 0.0301389773.

## TL;DR verdict

- **Global optimality cannot be proved now, and very likely not with any known method on any hardware.**
  - The best lower bound is 0.0296. That is GLLV's 9-vertex flag algebra; KPS independently reran N=9 with colour symmetry and got 0.02961 (float only).
  - The gap is 5.29e-4, which is 1.75% of our value.
  - No author has even *conjectured* a value for c4. GLLV say explicitly: "no conjectured value".
- **Our own data argues against a finite optimum near B192.**
  - B192 is a saddle in graphon space. Every symmetry-breaking lift improves it: 192 → 384 → 768 → 3840 gives −3.2e-8, −1.0e-8, −3.9e-8 (E4).
  - That pattern fits an optimum that is a large or infinite limit, not "blow-up of B192".
  - So "B192/Clebsch is optimal" is **false as stated**. The Z5/C5 lift already beats it.
- **The surrounding literature does support the *type* of structure.**
  - Blow-ups of Ramsey-critical colourings, specifically Paley(5)=C5 and the Clebsch/Greenwood–Gleason colourings, are *provably* the extremal constructions in the closest solved multiplicity problems.
  - This is a heuristic analogy, not evidence about c4 itself.
- **What is achievable and publishable:**
  - (a) a rigorous global optimum *within* the 2-parameter (and possibly the 15-level) Clebsch-design family;
  - (b) a rigorous *restricted* local-optimality certificate (a nondegenerate KKT point) for the 3840-class kernel in its own orbital space, via interval Newton;
  - (c) basin-convergence evidence.
  - No relative flag-algebra lower bound of the kind asked for in item (d) was found in the literature.

## Sources

| # | Source | URL | Verified claim | Relevance |
|---|---|---|---|---|
| S1 | Goodman 1959 | (classical) | c3 = 1/4. Random-like colourings are extremal, and many constructions attain it. | Baseline. For t=3 the optimum is not unique or rigid. |
| S2 | Thomason 1989/1997 | https://doi.org/10.1007/BF01196136 | c4 < 0.030304, then < 0.030291. Refutes Erdős's conjecture c4 = 2^−5. | Structured Cayley-type cores beat random. |
| S3 | Cummings–Král'–Pfender–Sperfeld–Treglown–Young, JCTB 103 (2013) | https://arxiv.org/abs/1206.1987 ; https://web.mat.bham.ac.uk/A.Treglown/MonoFINAL.pdf | 3-colour triangles: m3(3) = 1/25, **exact for large n**. The extremal colourings are exactly the balanced 5-part blow-ups of the unique triangle-free 2-colouring of K5 (both classes C5, i.e. **Paley(5)**), with each part in colour 3. Some between-part matchings may be recoloured with colour 3 if that creates no new monochromatic triangle. Flags on 4 vertices. | Paley(5)/C5 blow-up is **provably** extremal in a neighbouring problem, and our Z5 lift pattern is C5. Caveat: the extremal family is *not* rigid, because of the matching recolourings. |
| S4 | Kiem–Pokutta–Spiegel, JCTB 179 (2026) | https://arxiv.org/abs/2312.08049 ; https://github.com/FordUniver/kps_trianglemult | 4-colour triangles: m4(3) = 1/256. **Stability**: every near-extremal colouring is ε-close to a blow-up of one of the **two R(3,3,3) colourings of K16** (loops in colour 4). Certificate N=5, plus a stability theorem. Conjecture 7.1: m_c(3) = (R_{c−1}(3)−1)^−2, attained only by Ramsey colourings. | The strongest "Clebsch-provably-extremal" precedent. In both K16 colourings each colour class is the Clebsch graph (standard Kalbfleisch–Stanton fact, not re-verified here). |
| S4b | KPS §7 (same paper) | as above | Verbatim: "(marginally) improved lower bounds for the two-color K4 … Ramsey multiplicity using N = 9, with the floating-point output of csdp suggesting m2(4) ≥ 0.02961 … Since no matching or conjectured upper bound exists, we did not turn these results into exact rational values." Their colour-symmetry reductions give little "when there are no previously ignored symmetries". | **Direct evidence** that even state-of-the-art symmetry-reduced N=9 stalls at 0.02961. (The intro promises an "upper bound improvement in Section 7", but §7 of v1 contains only lower bounds. This looks like a typo.) |
| S5 | Parczyk–Pokutta–Spiegel–Szabó, FoCM 2024 | https://arxiv.org/abs/2206.04036 | c4 ≤ 0.030145 from a 768-vertex Cayley graph, with cores of 192/384/768 vertices. §5.1: "The crucial question regarding the Ramsey multiplicity of K4 is whether … there exists a graph whose blow-up sequence determines its value. Our answer to the c3,4 and c3,5 problem supports this possibility for c4. Our efforts for Theorem 1.1 however show that this construction could be unexpectedly complex." They ask for a generalisation to (semi)direct products Z3 ⋉ Z2^k. They prove perfect stability for **Schläfli** (c3,4 = 689·3^−8, 27 vertices) and for CR(3,5) (g4,5 = 29·13^−3). Their Lemma 3.3 says rooted K4 + anti-K4 densities are asymptotically equal at every vertex. | They do **not** conjecture a c4 value and do not conjecture that a finite core is optimal. They only call it a "possibility". Our Z3 × F2^k coordinates match their open question exactly. |
| S6 | Pikhurko–Vaughan, CPC 22 (2013) | https://arxiv.org/abs/1203.4393 | Minimum k-clique density with independence number < 3, equivalently the min independent-k-set density in triangle-free graphs (g_{k,3}). For k = 6, 7 the **Clebsch** blow-up is the unique extremal construction (with stability); for k = 5 it is C5-related. Proved by flag algebras (Flagmatic). | A **second provable Clebsch extremality**, in a related (but one-sided, forbidden-subgraph) problem. |
| S7 | Das–Huang–Ma–Naves–Sudakov, JCTB 2013 | (cited in S5) | g_{4,3}: the extremal construction is the C5 blow-up. | Another C5 result. |
| S8 | Pikhurko–Sliačan–Tyros, JCTB 2019 | https://www.sciencedirect.com/science/article/pii/S0095895618300728 | "Perfect stability" and reconstructors: a flag certificate of size ≥ \|V(C)\|+1, plus sharp-graph analysis, gives uniqueness of the blow-up of C. | The template any exact c4 proof would follow. Needs a flag size larger than the core: ≥ 193 here, hopeless. |
| S9 | Grzesik–Lee–Lidický–Volec, CPC 2022 | https://arxiv.org/abs/2012.02057 | "determining the value of C(K4) is a well-known open problem … **with no conjectured value**. A direct flag algebra calculation using … 9-vertex subgraph densities yields C(K4) ≥ 1/33.77 ≈ 0.0296, … slight improvement over … 1/33.9739 ≈ 0.0294343." | Lower-bound state and plateau. 8→9 vertices gained only about 1.8e-4. |
| S10 | Nieß 2012 | https://arxiv.org/abs/1207.4714 | c4 > 0.02876689 | Lower-bound history. |
| S11 | Even-Zohar–Linial 2015 | https://arxiv.org/abs/1312.1205 | c4 < 0.030285 from an **iterated** (nested) blow-up hidden in Thomason's construction. | Precedent: good c4 constructions can be *infinite-step* (iterated) rather than finite blow-ups. |
| S12 | Grzesik–Král'–Lovász, *Elusive extremal graphs*, PLMS 2020 | https://arxiv.org/abs/1807.01141 | Counterexample to Lovász's conjecture: some extremal problems have no finitely forcible optimum. | General warning: the minimiser need not be finite or step. Nothing specific to c4. |
| S13 | Csóka–Hubai–Lovász, *Locally common graphs*, JGT 2023 | https://arxiv.org/abs/1912.02926 | K4-containing graphs are not locally common at W ≡ 1/2 but are "weakly locally common". Sign determination uses up to 12 Taylor terms. | Methodology and precedent for *local* statements, and for how delicate higher-order terms are in the graphon topology. |
| S14 | Feinstein–Even-Zohar (talks, 2025/26) | https://math.technion.ac.il/events/noam-feinstein/ | c4 < 0.030139, "structured, symmetric" randomized constructions. | Possibly the same mechanism (see L1). No optimality claims. |
| S15 | FlagScale project (ZIB) | https://iol.zib.de/project/flagscale.html | Aims at scaling flag algebras. No K4 result listed. | No sign that a group is attempting N ≥ 10 for c4. |

I found no paper that conjectures the c4 optimum or proves it is not a finite blow-up. That is a search result, not proof of absence.

Sanity check (my script): Cay(F2^4, {e1..e4, 1111}) has 0 triangles, independence number 5, and 120 K4s in its complement. So within a single block, blue (the Clebsch graph) is K3-free and all monochromatic K4 inside a block are red.

## 1. How strong is the supporting evidence?

- **Pattern that holds in solved cases.** When the target clique is a triangle, or the problem is one-sided (forbidden K3), extremal constructions are blow-ups of Ramsey-critical colourings: C5/Paley(5) (S3, S7), Clebsch/Greenwood–Gleason (S4, S6), Schläfli (S5), CR(3,5) (S5).
  - The mechanism is clean. The critical colouring kills *all* monochromatic triangles between parts, so only intra-part triangles count, and the value is 1/(R−1)^2.
- **Why that mechanism does not transfer to c4.** For two-colour K4 no Ramsey colouring gives a competitive value.
  - The balanced blow-up of an R(4,4)-critical graph on 17 vertices has K4 density that is too large.
  - The best constructions (Thomason, PPSS, ours) are fractional, "soft" Cayley graphons, not critical colourings. B192 has two fractional levels.
  - In the solved cases the optimum is 0/1 between parts. That is exactly the structural feature that makes flag-algebra exact proofs possible: zero slack, simple sharp graphs.
- **Honest summary.** The literature supports "Clebsch/Paley-type algebraic cores are natural". It does *not* support "a finite Clebsch-based core is optimal for c4".
  - PPSS (S5) and GLLV (S9) both decline to conjecture.
  - Our own lift chain shows B192 is not even locally optimal in graphon space.

## 2. What proving global optimality would require

- **A matching lower bound c4 ≥ 0.0301388958…**, equal to our value. The only known route is flag algebras.
- **Current bound and gap.** 0.02961 (S4b, N=9, float) against 0.03013890, a gap of 5.29e-4 (1.75%).
- **Scaling of the flag bound.** The step from ~N=8 (0.029434) to N=9 (0.02961) gained 1.8e-4.
  - Even optimistic linear gains would need N ≥ 12. Diminishing returns would need far more.
  - A *tight* certificate for an optimum with 0/1 plus fractional structure on thousands of classes needs N > core size (S8 perfect stability), so N ≥ several hundred.
- **Problem size.** There are 12,005,168 graphs on 10 vertices, and roughly half as many up to complementation.
  - An N=10 SDP has millions of linear constraints and large type blocks. That is beyond csdp, and beyond a laptop by orders of magnitude.
  - KPS say their reductions are "largely not applicable" without extra symmetry. For c4 the only extra symmetry is complementation, a factor of 2.
- **Verdict on feasibility.** A laptop cannot do this. A cluster could not plausibly close 1.75% either. Nobody has attempted N=10 for c4.
- **Lagrangian or relative bounds.** Nothing in the literature (not located) proves a lower bound on c4 conditional on structure, e.g. "restricted to graphons containing the B192 pattern". Item 3(d) is therefore original work, not a citation.

## 3. Weaker but achievable, publishable statements

### (a) Global optimality inside finite-dimensional families

- **(a1) Two-level Clebsch-design family.** F(p, h) on [0,1]^2 is a polynomial of degree ≤ 6, since each W entry is affine in (p, h).
  - Method: exact rational coefficients (from `family.py`), then all critical points in the interior and on the four edges via resultants or Gröbner bases. Isolate real roots with rational intervals, and compare against corners and edge minima.
  - Result would be a theorem: the global minimum of the family is F* = 0.0301389773… at (p*, h*) ≈ (0.779181, 0.534265), p* and h* algebraic of known degree, and it is unique.
  - Cost: minutes (Sage/Singular or sympy). This is the cheapest rigorous statement and fully honest.
- **(a2) The 15-level family** (type × {0, S, off-C}, with a separate diagonal). F is a degree-6 polynomial in 15 box variables.
  - Method: Lasserre/SOS with the box constraints. A degree-6 relaxation uses a monomial basis C(15+3, 3) = 816, i.e. an 816×816 SDP, which is feasible on a laptop.
  - Rounding to an exact certificate is hard at an irrational optimum. The alternative is interval branch-and-bound using E11's KKT slacks (≥ 9.2e-6) to prune.
  - Cost: hours. It may fail to certify because of flatness: the fractional directions have near-zero curvature.
  - Result would be: "within all 15-level Clebsch-design graphons, B192 is globally optimal". This is publishable as a rigidity theorem for the base.
- **Beyond (a2).** "All Cayley graphons on F2^4 × Z3 × F2^2" has about 100 orbital variables in degree 6, so SOS basis ≈ C(103,3) ≈ 1.8e5. That is **infeasible**. Only local statements are available there.

### (b) Rigorous local optimality: which object, and in which space

- **B192 is not a local minimum in graphon space.** It is KKT in its 24-orbital kernel (E4: all 0-orbitals have gradient ≥ 1.5e-4, all 1-orbitals ≤ −9e-6, fractional ones ≈ 0). But it is a saddle once sub-orbitals are split. So the only true local statement about B192 is "strict local minimum in the G-invariant (24-parameter) or 15-level space".
- **The 3840-class kernel.** For the incumbent, the provable statement is: "a strict, nondegenerate local minimum in the space of all G/K-invariant step graphons on these 3840 classes, with 456 orbital parameters" (23 fractional, the rest at bounds).
  - Method, step 1. Confirm strict complementarity: every orbital at a bound has a nonzero gradient of the right sign. Bound that gradient below with rigorous interval arithmetic, since values are exact rationals.
  - Method, step 2. On the 23 fractional coordinates, run interval Newton/Krawczyk on ∇F = 0. This proves a unique true KKT point exists in a small box around the float optimum. The true optimum is irrational, so a rational KKT point does not exist. The exact rational value we publish is an *upper* bound at a nearby rational point, which is fine.
  - Method, step 3. Prove the 23×23 reduced Hessian is positive definite on the whole box. Use a rational LDL^T with interval error bounds, or check that the smallest-eigenvalue bound plus the Gershgorin error is > 0.
  - Cost: the Hessian by exact or interval rooted counts is 23² second derivatives. That is hours of single-thread time with existing CRT or rooted machinery. It is the cleanest rigorous "local" theorem.
- **Why a graphon-space (L∞ or cut-norm) local-optimality proof for any step graphon is hard.** This is my own analysis; S13 shows the same kind of delicacy.
  - The second variation vanishes on "pure fluctuation" perturbations U, i.e. those with zero mean over every class in each variable.
  - So local optimality in L∞ is decided by cubic and quartic terms. A cubic term that is nonzero on the null cone already *disproves* local minimality.
  - The one finite, checkable part is the "one-sided refinement" second-order condition. For each class i, the P3-rooted kernel matrix M_i (u(x) ∈ R^{#classes}) must be PSD, which is equivalent to "no vertex-splitting refinement helps at second order".
  - This is a finite eigenvalue check per class orbit (at most 3840/|orbit| matrices) and worth doing as a *necessary* condition. B192 should fail it (that is how the lifts win). The 3840 kernel either fails it, pointing to the next lift, or passes, giving evidence of refinement-stability.

### (c) Stability or rigidity evidence (non-rigorous)

- An abelian Cayley search from random seeds already converges into the B192 basin (E7).
- To make this quantitative, run a basin census: N random restarts per class count (192, 768, 3840). Report:
  - the fraction reaching the B192 lineage;
  - the value spread;
  - the orbit type of the result.
- Also report the lift chain 192 → 384 → 768 → 1920 → 3840 with gains, and fit the decay. If gains decay geometrically, give an extrapolated limit with an error bar. This quantifies "how far from optimal within the lineage".
- Cost: runs already exist, so a census adds hours. Label it evidence only.

### (d) Relative flag-algebra bound

- Nothing in the literature was located. A possible original formulation: a vertex-coloured flag algebra with 12 block colours, where cross-block pairs of 0/1 type are forced and fractional pairs are free bipartite graphons. Minimise the K4 + anti-K4 density.
  - This would give a lower bound for "all graphons with the B192 block skeleton", and so bound how much any refinement of B192 can gain.
  - Even N=5–6 with 12 colours is large, since the colour-pattern count explodes.
  - I rate it research-level. It could succeed only if a small N already nearly matches, which is unlikely since the lift gains are ~1e-7, far below flag-algebra resolution.
- **Not recommended** this round.

## 4. What the lower bound can teach the constructions (added on request, 23:02–23:12 UTC)

### (a) Certificate decomposition

For a flag certificate at order N the identity is exact:

  F(W) = LB + Σ_H s_H · p(H; W) + Σ_σ E_σ[ v_σ(W)^T Q_σ v_σ(W) ].

Here s_H ≥ 0 are the slacks on N-vertex graphs, Q_σ ⪰ 0, and v_σ are rooted flag densities.

Evaluating each term on our graphon splits our excess F(W) − LB exactly into per-H and per-type pieces.

**Precedent.** The complementary-slackness *use* of this identity is standard, but for tight problems only.
- Razborov's method and Flagmatic's "sharp graphs" check (Vaughan; Pikhurko–Vaughan S6): every H in the support of the extremal construction must have s_H = 0.
- Pikhurko–Sliačan–Tyros (S8) build perfect stability on exactly this.
- KPS (S4, §6) "factor out known zero eigenvectors based on the conjectured extremal constructions" to make the SDP well conditioned. That is the construction helping the certificate, which is the reverse direction.
- I found no published use of the decomposition as a diagnostic for a *non-tight* problem like c4 (not located).

**Caveat that limits its value.** The c4 bound still climbs with N:

| N | lower bound | source |
|---|---|---|
| 7 | 0.02877 | Nieß: "σ-flags with 5 vertices … represented as flags with 7 vertices" |
| 8 | ≈ 0.02943 (1/33.9739) | cited by GLLV; N not verified by me |
| 9 | 0.0296 / 0.02961 | GLLV; KPS |

So a large part of any term's value on our W reflects relaxation weakness, not "waste" in W. For a single W the two cannot be separated.

The informative version is **comparative**. Fix one certificate and decompose F(W_A) − F(W_B) for W_A, W_B among {Thomason, PPSS-768, B192, 3840}. Because the identity is exact, the difference is attributed exactly to specific H and σ. This shows which N-vertex statistics improved along the historical sequence. That is genuinely new information about *mechanism*, even though it says nothing about optimality.

**Cost.** Exact 7- or 8-vertex profiles of a 3840-class graphon are expensive (3840^7). Options:
- use B192's Cayley structure and fix one vertex;
- Monte Carlo: about 1e8 samples gives ±1e-4 per density. That is enough for attribution at the 1e-4 level, but not for 1e-8 lift gains.

### (b) Dual coefficients as a surrogate objective

**Not recommended.**
- The surrogate Σ s_H p(H;W) drops the SOS term, so it does not order constructions the way F does.
- The s_H come from a non-tight relaxation, so they penalise graphs the true optimum may need.
- F itself (4-vertex densities) is far cheaper to evaluate than any 7–9-vertex profile.
- I found no precedent (not located).
- At most, use it as a diagnostic *feature* in (a), not as a search objective.

### (c) Primal moment vector as a target profile

**Pitfall, decisive.** If the order-N primal optimum were realised by a graphon, that graphon would have value LB, and the bound would be tight: c4 = LB ≈ 0.0296. That contradicts the observed climb with N unless c4 ≈ 0.0296. So the moment vector is almost certainly **not realisable**. This is exactly our XOR-profile LP experience.

Further pitfalls:
- Interior-point solvers return a maximum-rank (analytic-centre) point of the optimal face. That is a mixture, and mixtures of graphon profiles are generally not graphon profiles.
- Realisability of density vectors is undecidable in general: Hatami–Norine, *Undecidability of linear inequalities in graph homomorphism densities*, JAMS 2011.
- Valid density inequalities need not have SOS proofs: Blekherman–Raymond–Singh–Thomas, *Simple graph density inequalities with no sum of squares proofs*, Combinatorica 2020.
- Projecting onto realisable profiles (MomentNet or similar) has no convergence guarantee.

**Verdict:** do not use it as a target.

### (d) Laptop feasibility

**Counts.**
- n=6: my exact orbit enumeration of all 2^15 graphs gives 156 graphs. There are 0 self-complementary graphs, since those need n ≡ 0 or 1 mod 4, so there are **78** colourings up to colour swap. Confirmed.
- n=7: 1044 graphs (OEIS A000088; not re-enumerated) and 0 self-complementary graphs (7 ≡ 3 mod 4), so **522** up to swap. "Roughly 1044" counts colour-labelled colourings, not colour-swap classes.
- n=8: 12346 graphs (OEIS A000088; not re-enumerated). n=9: 274668 (OEIS A000088; not re-enumerated).

**SDP size.** Types have size N−2, N−4, …; the largest blocks are flags on N−1 vertices over (N−2)-vertex types, so each block has at most 2^(N−2) rows.

| N | constraints | largest types | largest block | solve time (cvxpy + Clarabel/SCS) |
|---|---|---|---|---|
| 7 | ≤ 1044 | 34 types of size 5 | ≤ 32 | seconds |
| 8 | 12346 | 156 types of size 6 | ≤ 64 | minutes (Clarabel) |
| 9 | 274668 | 1044 types of size 7 | ≤ 128 | workstation-scale (GLLV, KPS used csdp). Flag-pair density generation is the bottleneck. Not a laptop task in Python. |

**Setup.** A from-scratch Python flag pipeline (canonical labelling by brute-force permutation or pynauty, then type/flag enumeration, pair densities and the SDP) takes about 3–5 hours of coding and debugging for N ≤ 8.

Existing tools:
- Flagmatic: old, Python 2/Sage-era.
- Bodnár's FlagAlgebraToolbox (SageMath, arXiv 2601.06590): needs Sage, which is heavy but uv-independent.
- KPS code (github.com/FordUniver/kps_trianglemult): specialised to multicolour triangles, with sage and csdp.

Reusing a toolbox would save hours only if Sage is already installed.

**Expected bounds.**
- N=6: not located in the literature. I expect it to be well below 0.0288. It is useless as a bound but fine as a pipeline test.
- N=7: about 0.0288 (Nieß).
- N=8: about 0.0294.

A crude geometric fit to the N=7,8,9 steps (+6.6e-4, then +1.8e-4, ratio about 0.27) extrapolates to only about 0.0297. That is 3 points and illustrative only. It suggests moderate-N flag algebras will not approach 0.0301.

### (e) Verdict on a flag-algebra diagnostic lane

- **Worth a small, bounded lane only in the comparative form (a).** Build an N=7 pipeline (half a day, including the certificate and exact rounding optional), then N=8 if the code is efficient (plus about 2–4 hours compute).
- Evaluate one fixed certificate on 3–4 historical constructions by Monte Carlo profiles. Report which H and σ terms separate them.
- Expected payoff: mechanistic insight and a nice figure for the paper. Low probability of directly guiding a better construction, because relaxation slack dominates at N ≤ 9.
- Do **not** build the surrogate objective (b) or the moment-target approach (c).
- Priority: below plan items 1–3.

## Ranked plan

1. **Exact global optimum of the 2-parameter family (a1).** Exact polynomial F(p, h), then resultants and real-root isolation, giving the algebraic (p*, h*, F*).
   - Cost: 30–60 minutes, laptop.
   - Payoff: a clean theorem for the paper, "B192 is the unique optimum of the Clebsch-design family", plus the algebraic degree of F*.
2. **Interval-Newton KKT and Hessian certificate for the 3840 kernel in its 456-parameter orbital space (b).** Prove strict complementarity at all 433 bound orbitals and a positive-definite 23×23 reduced Hessian.
   - Cost: 2–6 hours single-thread, plus coding.
   - Payoff: the rigorous statement "strict local minimum among G/K-invariant step graphons". The paper must state that this is *not* local in graphon space.
3. **Refinement-stability eigen-check (necessary second-order condition in graphon space) for B192 and the 3840 kernel.**
   - Cost: 1–3 hours.
   - Payoff: explains the saddle, predicts or rules out the next lift, and gives a checkable criterion for the paper.
4. **Lasserre degree-6 SDP on the 15-level family (a2).**
   - Cost: hours, with an uncertain rounding step.
   - Payoff: "global within the 15-level family", or a numerical lower bound for that family.
5. **Basin census and lift-decay fit (c).**
   - Cost: hours of existing runs.
   - Payoff: quantitative stability evidence and an extrapolated in-lineage limit.

Explicitly **not** feasible:
- a global proof (N ≥ 10 flag algebras, at least ~10^7 constraints, with no evidence it would close 1.75%);
- relative flag bounds (d).

## Wording for the paper

"We do not claim optimality. The best lower bound is 0.0296 (GLLV 2022; 0.02961 numerically in KPS 2023), and no value of c4 has been conjectured. Our base B192 is the global optimum of a two-parameter Clebsch-design family [if item 1 is done] and is a saddle in graphon space. The incumbent is a strict local minimum in its 456-parameter invariant space [if item 2 is done]. The structural analogy with provably extremal Ramsey-colouring blow-ups is: C5 in three-colour triangles (Cummings et al. 2013), Clebsch/Greenwood–Gleason in four-colour triangles (Kiem–Pokutta–Spiegel) and triangle-free independent sets (Pikhurko–Vaughan)."

Addendum to the plan:

6. **(optional) Comparative flag-certificate diagnostic, N=7 then N=8** (§4e).
   - Cost: half a day of coding plus hours of compute.
   - Payoff: exact per-subgraph attribution of the improvements Thomason → PPSS → B192 → 3840.
   - Low odds of finding a better construction.
