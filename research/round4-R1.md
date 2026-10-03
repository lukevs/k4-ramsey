# Round 4 lane R1: literature-driven direction scan

Date: 2026-09-27, 22:33–23:00 UTC. Reading and web only. No compute or commits.
Protocol: I brainstormed and searched before reading any campaign notes. Only then
did I read approach-registry, next-mechanism-queue, deeper-literature-root,
adjacent-methods, round4-contract, round4-P, round4-P-paper-draft §1, the headers of
fresh-hypotheses-round2, adjacent-algebraic-mechanisms-round3,
theory-directions-round3 and landscape-escape-literature, and the E4/E7/E9 lane
code headers. I used those files only to remove duplicates.

Evidence label for everything below: **proposal only**. Nothing here was run.

## Brainstorm list, and why most of it was dropped

I considered 25 mechanisms from 2015–2026 work. Most were dropped after the
duplicate check.

| Mechanism (source) | Status |
|---|---|
| Blow-ups of small graphs found by tabu or annealing (Parczyk–Pokutta–Spiegel–Szabó, [2206.04036](https://arxiv.org/abs/2206.04036)) | Baseline (PPSS). Already built on. |
| XOR and composition products (Even-Zohar–Linial, [1312.1205](https://arxiv.org/abs/1312.1205)) | E6 retired it. Also H4 in adjacent-methods. |
| Iterated or recursive blow-ups (Pikhurko; inducibility of blowups, [2606.06202](https://arxiv.org/abs/2606.06202); 6-vertex inducibility, [2606.00290](https://arxiv.org/pdf/2606.00290)) | Covered by typed recursive substitution (H-F2-02), recursive-quotient and TR3-1. Homogeneous recursion retired ("211 red cost"). |
| Flag-algebra SDP / complementary-slackness construction extraction | Covered by H-F2-04. Our lower/upper gap (about 0.0287 vs 0.0301) makes the certificate too loose to guide constructions. |
| Association schemes, Hamming/quadratic schemes, Paley difference sets as microstructure | Covered: quadratic-scheme*, hamming-scheme*, H-F2-01. |
| Cayley / orbital / Schreier / nonabelian kernels | Covered: E4, E7, H-F2-03, queue #2 and #4. |
| PatternBoost, FunSearch/AlphaEvolve ([2511.02864](https://arxiv.org/abs/2511.02864)), NRPA, RL ([2603.09172](https://arxiv.org/abs/2603.09172)) | Covered: E2, E3, landscape-escape §3. PPSS §5.3 already reports negative RL evidence. |
| Population annealing | Covered: E1. |
| Motif-to-graphon inversion (MomentNet) | Covered in the deeper-literature note. |
| Vertex-type insertion / column generation | Covered: E8. |
| Thomason-type centered perturbation around 1/2 (local commonness) | Covered by the "centered-family ceiling" work. |
| Block-mass and collective-curvature moves | Covered: F3 and queue #1. |
| Polar / BEC nonlinear recursion | Covered: E5 and queue #3/#5. |
| Cap-set "extendable" non-plain products | Its useful part is the symbol-dependent fibre lift, which is E9. Dropped. |
| Sphere packing and kissing (relax, then round; Klartag random-lattice growth) | No transferable mechanism beyond relax-and-round, which we already do. Dropped. |
| Fox–Wigderson / Moss–Noel Turán colourings | These are optimal only for pairs of graphs unlike (K4, K4). They are useful only as seeds; see R1-2. |

Eight directions survive, ranked below.

---

## R1-1. Lifts over non-cyclic fibre groups, seeded by Ramsey-critical Cayley colourings

**Observation (from the round4-P / E9 code, not the literature).** The Z5
"pentagon" fibre pattern used on active P and H edges (S = {±1} in Z5) is C5. C5
is the unique 2-colouring of K5 with no monochromatic triangle, i.e. the Paley(5)
Ramsey-critical colouring. The largest single gain in d4763 is therefore a lift
whose fibre kernel is a Ramsey-critical Cayley colouring.

**Literature mechanism.** Kiem–Pokutta–Spiegel, *The four-colour Ramsey
multiplicity of triangles* ([2312.08049](https://arxiv.org/abs/2312.08049),
JCTB 2026). Every large extremal construction is a blow-up of one of the two
R(3,3,3)-critical colourings of K16. Both are Cayley colourings of Z2^4 built
from the Clebsch graph. Parczyk et al.
([2206.04036](https://arxiv.org/abs/2206.04036)) settle the minimum density of
independent 4-sets with clique number at most 4 with a blow-up of a structured
Ramsey-type graph. In both cases, multiplicity extremals are built from
Ramsey-critical, spectrally flat Cayley colourings.

**Why it worked there.** A Ramsey-critical colouring puts zero monochromatic
copies inside the pattern. A spectrally flat pattern has
|κ̂(χ)| constant over non-trivial characters, so no single character dominates
the higher-order correction terms.

**Mismatch.**
1. There, the pattern is the whole construction. Here it is a fibre inside a
   192-class base, and the base's phases (voltages) matter as much as the fibre.
2. E9 already covers cyclic groups Z_m with arbitrary S, which includes
   Paley(13), Paley(17) and C8(1,4) as S-choices.
3. The genuinely new part is **non-cyclic fibre groups with group-valued
   voltages**: Z3^2 (Paley(9) = 3×3 rook graph), Z2^4 (Clebsch), Z5^2 (Paley(25)).
   E9's `(a-b-g) mod m` cannot represent these.

**Cheapest test (~30 min).**
1. Generalise E9's `build` from `(a-b-g) mod m ∈ S` to `a·b⁻¹·g⁻¹ ∈ S` over a
   group multiplication table.
2. At |Γ| = 9, compare Z3^2 with S = Paley(9) against the best Z9 with |S| = 4.
   At |Γ| = 16, compare Z2^4 with S = Clebsch (5-regular) against Z16 with
   |S| = 5 (or 6).
3. For each, take a random phase table plus E9's own voltage local search, with
   an equal evaluation budget.
4. Before any search, sanity check that Γ = Z5 reproduces C(9;7,4,8).

**Prediction.** If spectral flatness is the operative mechanism, the
non-cyclic, Ramsey-critical fibre gives a lower optimised (p0,x,y) value than
the best cyclic fibre of the same order. The first gain to look for is against
the plain Z5 lift C(Q;·) at the same stage, before per-edge polish.

**Disconfirmation.** At both orders, the non-cyclic group is no better than the
cyclic group at matched budget. That would say the base's phase structure, not
the fibre's spectrum, is what matters. Separately, if |Γ| ≥ 9 lifts lose to Z5,
the fibre-kernel direction as a whole is weakened.

**Distinct from lanes.** E9 is cyclic only. E7 and E4 put groups on the base,
not the fibre. The nonabelian voltage covers of H-F2-03 were not seeded by
Ramsey-critical patterns, and elementary-abelian fibres are abelian anyway.

---

## R1-2. Objective homotopy: continue along the off-diagonal weight λ

**Source.** Moss–Noel, *Off-diagonal Ramsey multiplicity*
([2306.17388](https://arxiv.org/abs/2306.17388)). This gives a dual formulation
for min t(H1,W) + λ·t(H2,1−W) and extremal constructions for several pairs. See
also *Turán colourings in off-diagonal Ramsey multiplicity*
([2309.06959](https://arxiv.org/abs/2309.06959)) and the off-diagonal
formulations in Kiem–Pokutta–Spiegel.

**Mechanism.** Minimise F_λ(W) = t(K4,W) + λ·t(K4,1−W). Near λ = 1 there is a
family of problems whose minimisers move continuously except where branches
cross. Start from minimisers at λ ≠ 1, which have different basins; at large λ
they are Turán-like colourings with few blue K4, and they are structurally
simple. Track each one back to λ = 1. Graduated non-convexity methods in vision
and robotics use the same idea: a deformed objective whose landscape is simpler
(e.g. GNC, [1909.08605](https://arxiv.org/abs/1909.08605)).

**Why it may apply.** The incumbent's colours are asymmetric (p = 32/41, not
1/2), so the λ = 1 minimiser is not forced to be complement-symmetric. There are
at least two mirrored basins, and branches that exist only for λ ≠ 1 may enter
at λ = 1 with lower value. None of E1–E9 changes the objective. Population
annealing changes the temperature, not the landscape.

**Mismatch.** Branch-following in a 10^3–10^5-dimensional non-convex space
often just lands back on a known basin. Also, the λ = 1 minimum might be an
isolated branch.

**Cheapest test (~30 min, all within existing search evaluators).**
1. **Family.** The 3-parameter pentagon family C(Q;p0,x,y) and the E9
   fractional-edge polish, with the objective multiplied by λ on the blue term.
   This is a one-line change to the evaluator.
2. **Path out and back.** Go outward λ = 1 → 1.5 → 2.5 and inward to 0.6. At
   each λ, re-optimise the phase table as well as the levels. Then return to
   λ = 1 in 10 steps.
3. **Extra seeds.** Also start at λ = 3 from two off-diagonal-style seeds: a
   Turán 3-colouring blow-up with fractional in-part density, and a B192 variant
   with p and h swapped.
4. **Control.** Plain descent at λ = 1 from the same seeds with the same
   evaluation budget.

**Prediction.** At least one returned path lands in a basin that is not
equivalent under colour swap or isomorphism to the incumbent, and is below the
control's result from the same seed. Beating d4763 would be a bonus, not the
gate.

**Disconfirmation.** Every path returns to the incumbent basin (the same phase
table up to automorphism) or to something worse than its control.

---

## R1-3. A second-level voltage tower: lift the 960-class lift again

**Source mechanism.** Iterated blow-up / recursive towers are optimal or
record-holding in hypergraph Turán problems: Pikhurko's recursive patterns
("Finite hypergraph families with rich extremal Turán constructions via mixing
patterns", [Forum Math Sigma](https://www.cambridge.org/core/journals/forum-of-mathematics-sigma/article/finite-hypergraph-families-with-rich-extremal-turan-constructions-via-mixing-patterns/510C784B7C84C92B16CF02DB282E1BBB)).
They also appear in inducibility ([2606.06202](https://arxiv.org/abs/2606.06202)).
Towers of covers (lifts of lifts) are the standard way to build graphs that are
locally like a base but globally twisted.

**Why distinct from the retired recursion.** The retired lane substituted a
homogeneous copy inside classes; the measured red cost was 211. A voltage tower
instead lifts d4763's 960-class base (or C(9;7,4,8)) by a *second* twisted
Z_m′, with voltages that must be consistent with the first-level voltages. This
is a cover of a cover, not a substitution. The measured fact that the first
cover gave the largest gain is the empirical reason to try a second.

**Mismatch.** Gains usually decay geometrically. The second level also has a
much larger voltage space (about 1000 active pairs) and N = 4800 fine classes.

**Cheapest test.** Do it perturbatively, so that N = 4800 is never evaluated.
1. At first order in amplitude, a centred second-level fibre term does not
   change the density.
2. The ε² coefficient is a quadratic form over the second-level voltage
   assignment. Its entries depend on the level-1 lift's 2-, 3- and 4-point
   statistics at fine-class pairs. E9 derived the analogous level-1 formula (or
   can compute it by finite differences on C(Q)).
3. Minimise that form over voltages by local search (Z3 and Z5 at level 2), and
   report its minimum.

**Prediction.** A strictly negative ε² minimum exists. Then a finite-amplitude
second lift is worth a full E9-style run.

**Disconfirmation.** The ε² minimum is ≥ 0 over all searched voltage
assignments. That would retire small-amplitude towers; a large-amplitude
"binary" second lift, like the level-1 x/Q pattern, would still be open but
lower priority.

**Coordination.** Ask E9 whether "beyond Z5" includes iterating on d4763. If it
does, merge this into E9 rather than running a separate lane.

---

## R1-4. Unstructured, full-kernel continuous descent: basin census at N ≈ 192–256

**Source.** Harchaoui–Oh–Pal–Somani–Tripathi, stochastic optimisation on
graphon limits ([2210.00422](https://arxiv.org/abs/2210.00422)). Parczyk et al.
search binary blow-ups by tabu search. Neither runs free continuous descent from
unstructured starts on the Ramsey objective.

**Mechanism.** Projected (or mirror/entropic) gradient descent on all N(N+1)/2
kernel entries. The exact gradient is G_ij ∝ (W A_i W)_jj with
A_i = diag(W_i) W diag(W_i). That costs O(N^4) per full gradient with BLAS,
i.e. seconds at N = 192.

Starts:
- random blow-ups of G(n, 1/2);
- 1/2 + noise (a saddle by symmetry, so it needs a noise kick);
- random 3- or 4-part Turán-type colourings.

Afterwards, cluster the converged kernels by twin classes, rank and profile.

**Why it may matter.** Every current lane lives on B192 or a chosen group. If
free descent from unstructured starts routinely finds values ≤ 0.03015 via
non-B192 structure, those are new bases for the P/E9 lift pipeline. If it always
recovers B192 or its sub-quotients, that is useful evidence that B192 is the
dominant basin at this scale.

**Mismatch.**
- N ≤ 256 cannot represent 960-class structure, so only compare against B192
  (0.03014178 at p = 4/5, h = 2/5).
- Non-convexity means many poor local minima.
- PPSS found RL uncompetitive, but plain gradient descent on fractional kernels
  is a different method.

**Cheapest test.** 24 starts at N = 192, 1500 mirror-descent steps each. Record
the final F; for any run below 0.03016, record twin-class count and whether it
is isomorphic to a B192 quotient.

**Prediction (skeptical).** The median lands at ≥ 0.0303. At most a few runs
fall below 0.03016, and those are B192-like.

**Disconfirmation / pivot.** A run below 0.03015 that is *not* B192-like would
promote it to a new lift base. If no run falls below 0.0302, the descent method
has too many poor minima to be useful for this problem; it is not evidence
that there are no other bases.

---

## R1-5. A Ramsey-critical pattern dictionary as the *base*, lifted like B192

**Source.** The same Kiem–Pokutta–Spiegel and PPSS precedents as R1-1.

**Mechanism.** Replace B192 with a structured Ramsey-type base. Candidates:
- the unique R(4,4)-critical colouring Paley(17);
- Paley(9), Paley(13), Clebsch, Schläfli and their complements;
- mixtures of these with diagonal densities.

Then run the same "fractional pairs + fibre lift" pipeline.

**Mismatch (strong).** Plain weighted blow-ups of these graphs are old
candidates, and PPSS certainly searched small blow-ups, so they are almost
surely above the McKay reference. The only new element is the
*lift-after-fractionalisation* pipeline that produced B192 → d4763.

**Cheapest test.**
1. For each of 6 bases (≤ 27 classes), optimise per-orbital probabilities and
   diagonals: seconds each.
2. Apply the E9 Z5 lift with voltage search: minutes each.
3. Compare the size of the lift gain with B192's lift gain (B192 → C(9;7,4,8),
   about 2.9e-6).

**Prediction.** The lift gain depends on the base. If some base gains more
relative to its pre-lift value, its larger blow-ups (tensor products with B192
classes) become candidates.

**Disconfirmation.** Every base's lifted value stays above 0.03015.

Rank 5 because the prior-art risk is high. It is kept because it directly asks
which property of B192 the lift exploits.

---

## R1-6. Sign test for colour asymmetry at the incumbent (diagnostic, minutes)

This comes out of R1-2's dual view (Moss–Noel).

**Diagnostic.** Compute dF_λ/dλ at λ = 1 for d4763, which equals t(K4, 1−W).
Also compute the split t_red vs t_blue.

**Why it matters.** If t_red ≠ t_blue by a large margin, the minimiser of F_1 is
sitting on a branch where one colour is "cheaper". That predicts a
complementary construction family, obtained by swapping which symbol sets carry
the fractional mass (P ↔ H roles), which no lane has tried as a seed.

**Cost and outcome.** Seconds from an existing receipt, since P's checker
already reports red and blue separately. It is a cheap gate for R1-2: if
t_red ≈ t_blue to about 1e-4 relative, drop R1-2's swapped-role seeds.

This is a diagnostic, not a construction lane. It is listed so that R1-2 is run
only if it is justified.

---

## Dropped after duplicate check (not listed as directions)

These overlap an existing lane or queue item:
- the flag-SDP dual-guided direction (H-F2-04);
- fibre-symmetry-breaking Hessian by Z5 isotypic components (queue #1 at the
  B192 level; at N = 960 it is too costly within 30 min);
- vertex-type gluing at finite mass (E8);
- program-evolved priority functions (E2/E3);
- Paley-difference-set microstructure (H-F2-01);
- Z_m with Paley S (E9).

## Top recommendations for the next batch

1. **R1-1**: non-cyclic Ramsey-critical fibre groups (Z3^2, Z2^4). New,
   mechanistically motivated, and needs only a small generalisation of E9 code.
2. **R1-3**: second-level voltage tower via an ε² quadratic-form screen. Cheap,
   and it has a clean go/no-go.
3. **R1-2 (gated by R1-6)**: λ-homotopy continuation. This is the only proposal
   that changes the objective landscape rather than the representation.
4. **R1-4**: unstructured full-kernel descent as a basin census. It tests the
   "B192 is the only good base" assumption behind every current lane.
