# An explicit step graphon with K4 Ramsey multiplicity density below 0.030139

Draft, round 4 lane P, 2026-09-27.  Status: **internal draft, not submitted,
not reviewed by a human mathematician.**  Every number below is an exact
fraction regenerated from a stored `report.json`; decimals are for display.

## 1. Statement

For a 2-colouring of the edges of K_n let m(n) be the minimum, over all
colourings, of the number of monochromatic K4 divided by C(n,4), and let
c4 = lim m(n) (the limit exists; m(n) is non-decreasing by averaging over
(n-1)-subsets).

**Theorem (computational).** c4 <= F*, where

    F* = 16900934504649027287619486865996291 / 560768060721761383881293603555770368
       = 0.030138903565399090...

F* = t(K4, W) + t(K4, 1 - W) for the explicit 960-step graphon W of Section 3
(file `graphon-candidate.json`, SHA-256
`d4763fefc34a3966bfbe811d279b522c067f193e436bb522d357dd423c0c58c3`).

**Simpler companion statements** (each an explicit step graphon, each
independently recounted, Section 5):

| Construction | parameters | exact value | decimal |
|---|---|---|---|
| (A) B192, p=4/5, h=2/5 | 2 | 3333439223/110592000000 | 0.0301417754 |
| (B) B192, p=32/41, h=22/41 | 2 | 1013294255057839/33620705806123008 | 0.0301389941 |
| (F) B192 lifted by Z5 twisted pentagons, (p0,x,y)=(3,2,4)/4 | 3 + phase table | 2048009329/67947724800 | 0.0301409552 |
| (C) B192 lifted by Z5 twisted pentagons, (p0,x,y)=(7,4,8)/9 | 3 + phase table | 4198776398959/139314069504000 | 0.0301389258 |
| (D) as (C) with (51064,29356,58565)/65536 ("b93") | 3 + phase table | 1375401591138773841968807740019/45635421608216258453881315393536 | 0.0301389040 |
| (E) = W above ("d4763") | (D) + 234 per-edge amplitude exceptions | F* | 0.0301389036 |
| (G) E4-3840: orbital kernel on coset action G/K, \|G\|=46080, \|K\|=12, 3840 classes | 456 orbital parameters (23 fractional) | 2112616269946473812116180096163290703/70096007590220172985161700444471296000 | **0.0301388958** (sharpest) |

Trust boundary of (G): exact rooted multiprime-CRT count x N, valid under
vertex-transitivity that was independently verified (8 generators preserve
every entry; generated group transitive); cross-checked against the generic
direct U256 checker on the 768-class sibling.  It is not a full O(N^4)
generic recount (that would take hours).  (E) has two full generic recounts.

| (H) E5 depth1: d4763 x {±1}, W'((u,s),(v,t)) = W(u,v) + s t A(u,v), 1920 classes | (E) + signed amplitude table A | 8450464924639256799670867730068932689/280384030360880691940646801777885184000 | **0.0301388953** (sharpest audited, 5.5e-10 below (G)) |

(H) passed a full generic direct U256 recount (no symmetry assumption, 1645 s).

(A) and (F) already beat the McKay reference ((F) uses only the
probabilities 0, 1/2, 3/4, 1 — the same values as the PPSS block densities);
(B), (C), (D), (E) are below 0.030139.  In a restricted rounding scan of
C(Q; p0, x, y) for Q in {4,5,7,8,9,10,11,13,18} (search side,
`reports/round4-P-pentagon-001/evaluations.jsonl`), Q=9 was the smallest
denominator found below 0.030139; this is not an exhaustive search.
(C) is the recommended headline for exposition: every probability is in
{0, 4/9, 7/9, 8/9, 1}, it loses only 2.2e-8 relative to (E), and it is
7.4e-8 below the rounded 0.030139 threshold.  (E) is the sharpest value.

## 2. From a step graphon to colourings (lifting)

Let W be an N-step graphon with equal class masses 1/N and class-pair values
w_ij in [0,1] (w symmetric, diagonal w_ii allowed).  Define

    F(W) = N^-4 * sum_{(i1,i2,i3,i4) in [N]^4} ( prod_{s<t} w_{i_s i_t} + prod_{s<t} (1 - w_{i_s i_t}) ),

the sum running over **all ordered 4-tuples including repeated indices**, with
w_ii used for a repeated pair.  This equals t(K4,W) + t(K4,1-W).

**Lemma.** For every n >= 4, m(n) <= F(W).  Hence c4 <= F(W).

*Proof.*  Give each vertex v of K_n an independent uniform class c(v) in [N];
conditionally on the classes, colour each edge uv red independently with
probability w_{c(u)c(v)}, blue otherwise.  For four distinct vertices the six
edges are distinct, hence conditionally independent, and the class 4-tuple is
uniform on [N]^4 (repeats included; two distinct vertices in the same class i
are red with probability w_ii).  So P(the four vertices span a monochromatic
K4) = F(W) exactly, the expected number of monochromatic K4 is C(n,4) F(W),
and some colouring achieves at most the expectation.  QED.

This is the standard W-random graph / random blow-up argument (Lovász and
Szegedy, "Limits of dense graph sequences", J. Combin. Theory Ser. B 96
(2006); Lovász, *Large Networks and Graph Limits*, AMS 2012, section on
W-random graphs).  It needs no limit, no rationality of w, and no finite
template reuse.  Both independent checkers compute exactly the sum above:
integer numerators r_ij = Q w_ij, blue numerators Q - r_ij (diagonal
included), all N^4 ordered tuples, denominator N^4 Q^6
(`experiments/association_scheme/ordered_graphon_u256.cpp`, loop `i,j,k,l`
over `[0,n)` with no distinctness filter;
`experiments/round4_P/crt_pair_quadratic.cpp`, same range).

## 3. Construction

### 3.1 The 192-class base B192 (closed form)

Vertices: (x, u) with x in F2^4 and u = (a, e, σ) in Z3 x Z2 x Z2 (192 classes).
Let S = {e1, e2, e3, e4, 1111} (Cay(F2^4, S) is the Clebsch graph) and
C = {0} ∪ S.  Four type functions on F2^4:

| type | z = 0 | z in S | z not in C |
|---|---|---|---|
| Z | 0 | 0 | 1 |
| X | 1 | 1 | 0 |
| P | p | p | 0 |
| H | h | 1 | 0 |

The block type T(u, v) depends only on (da, de, dσ) = u - v:
dσ = 0: (da,de) = (0,0) -> Z, (0,1) -> H, da ≠ 0 & de = 0 -> X, da ≠ 0 & de = 1 -> Z;
dσ = 1: da = 0 -> P, da ≠ 0 -> Z.
Then W((x,u),(y,v)) = g_{T(u,v)}(x + y), with W = 0 on the diagonal
(the diagonal convention is immaterial for the Z-type rule, which gives 0 at z = 0).
So B192 is a Cayley graphon on F2^4 x Z3 x Z2 x Z2 with two free levels p, h;
each class has 87 neighbours at 1, 12 at p, 1 at h.

Verification (lane E11 found the rule; lane P re-verified with its own code,
`experiments/round4_P/verify_e11_rule.py`, `reports/round4-P-e11-rule-check-001/`):
(i) a bijection between E11's 12x12 type matrix and the difference design
above exists (backtracking search); (ii) under E11's vertex map (data,
checked bijective), all 36,672 off-diagonal entries of the stored B192 agree
with the rule, diagonal zero; (iii) the matrix built purely from the closed
form in canonical coordinates, at p = 51064/65536, h = 35015/65536, has exact
density 515776850799050572477656236153/17113283103081096920205493272576,
identical to the stored B192 (CRT checker).

*Remark (provenance).* B192 was found as a quotient of the Parczyk–Pokutta–
Spiegel–Szabó 768-vertex Cayley colouring (arXiv:2206.04036) by 192 fibres of
size 4 (`reports/pilot-algebraic-lift-001/quotient.json`): with D(i,j) the
number of red edges between fibres, D = 0/8/12 give 0/H/P, and a complete
block (D = 16) is P iff D(i, H(j)) = 12, else 1
(`experiments/round4_P/b192_origin.py`), followed by optimisation of p, h.

Constructions (A), (B): W_ij = 0, 1, p, h according to the symbol.

### 3.2 The Z5 twisted-pentagon lift

Refine each class i into five equal classes (i,a), a in Z5.  Let
kappa(d) = 3 if d = +-1 (mod 5) and -2 otherwise (so kappa/5 + 2/5 is the
indicator of the 5-cycle; sum_d kappa(d) = 0).  A phase table assigns to each
of the 1248 fractional pairs {i<j} (1152 P-pairs, 96 H-pairs) a state
g_ij in {inactive, 0,1,2,3,4}; g_ji = -g_ij.  Observed: 272 P-pairs inactive,
P phases 0/1/2/3/4 on 82/280/116/195/207 pairs, all 96 H-pairs phase 1.
("on-pattern" means a - b - g_ij = +-1 mod 5.)

Construction C(Q; p0, x, y):
- 0 and F blocks and the diagonal blocks (i,i) unchanged (0, 1, 0);
- inactive P-pair: constant p0/Q;
- active P-pair: x/Q on-pattern, 1 off-pattern;
- H-pair: 0 on-pattern, y/Q off-pattern.

The phase table is presented as an explicit table
(`structure/phase-assignment.json`, 1248 entries keyed by B192 class indices
of the stored matrix).  Lane E10 reports it has only a Z2 symmetry and no
closed-form cocycle description; we have not re-verified that claim.

(F) = C(4; 3, 2, 4), (C) = C(9; 7, 4, 8), (D) = C(65536; 51064, 29356, 58565).  In amplitude form,
(D) is entry = base + q*kappa(a-b-g) with base 51064, q = -7236 on P-pairs and
base 35139, q = -11713 on H-pairs, both at the boundary of [0, 1].

The whole graphon is invariant under the simultaneous shift (i,a) -> (i,a+1),
so Z5 acts freely; the base symmetry of B192 is inherited only where the phase
table is compatible (not analysed in this round).

### 3.3 The sharpest point (E)

(E) = (D) except that 234 of the 880 active P-pairs carry an amplitude
different from -7236 (135 other values in [-7236, -5685]; the per-edge table
is `per-edge-amplitudes.json`).  It came from exact deterministic per-edge
coordinate descent; it is not claimed to be a local or global optimum.
`experiments/round4_P/describe.py` reconstructs all 921,600 entries of (E)
from (B192, phase table, amplitude table) with zero mismatches.

## 4. Certificate data

A candidate is a `rational-step-graphon-v1` JSON: unit block weights, integer
denominator Q, symmetric integer matrix of red numerators in [0,Q].  No score is
stored in the candidate.  See `reports/round4-P-package/README.md`.

## 5. Verification and trust boundary

Two generic exact checkers read only the candidate matrix:

1. **Direct ordered U256** (`experiments/association_scheme/ordered_graphon_u256.cpp`,
   SHA a31c4052...): for each ordered pair (i,j), inner double loop over (k,l)
   with exact U128/U256 integers, explicit overflow bounds, 12 tiny literal
   cases.
2. **Pair-quadratic multiprime CRT** (new, `experiments/round4_P/`): for each a,
   X[b,c] = r_ac r_bc mod p, Y = X r via Accelerate dgemm (exact because every
   partial sum is an integer < 2^53), sum_{b} r_ab <X_b, Y_b> mod p; seven primes
   below 2^21 whose product (> 2^146) exceeds the count bound N^4 Q^6; CRT;
   red and blue separately.  Tiny oracle: 21 random symmetric matrices
   (n = 1..7, arbitrary diagonals, Q in {1,2,7,65536}) against a pure-Python
   brute force over [n]^4.  Independent of (1) in code, arithmetic
   (modular/CRT vs multiword), and summation library; it shares only the
   defining formula (a sum over [N]^4), so a misreading of the definition
   would be common-mode.  The tiny oracle and Lemma of Section 2 address that.

Results (all exact agreement, fraction and red/blue raw totals):

| Candidate | SHA-256 (prefix) | U256 direct | CRT (this round) |
|---|---|---|---|
| (E) d4763 | d4763fef | passed, 105.5 s (earlier round) | passed, 144.0 s |
| (C) Q=9 | 22df51a8 | passed, 115.9 s | passed, 73.7 s |
| (F) Q=4 | 52b6c692 | passed, 129.9 s | passed, 116.9 s |
| (B) d=41 | 33e2e141 | passed | passed |
| (A) d=5 | 45b13fd1 | passed | passed |
| (D) b93 | b93b3589 | passed, 112.7 s (this round) | search-side strided evaluation only; earlier compressed Level-A |

Trust boundary: native C++ / Accelerate / Python execution on one machine.
Not a Lean proof (the repository's Lean checker covers the 768-vertex PPSS
template only), not a formal proof of the Lemma, no optimality claim.

## 6. Comparison with prior bounds

| Source | value | status |
|---|---|---|
| Thomason 1989/1997; Even-Zohar–Linial (arXiv:1312.1205) | earlier, weaker upper bounds (values to be transcribed from primary sources) | published history |
| Parczyk–Pokutta–Spiegel–Szabó 2022 (arXiv:2206.04036), 768-vertex Cayley | 4551721/150994944 = 0.0301448570 | published; recounted in Lean here |
| McKay reference | 10486266368/768^4 = 0.0301422734 | numerator recorded in repo; adjacency not available here |
| Feinstein (with Even-Zohar), Technion seminar 2026-01-21 | "c4 < 0.030139" | announcement only; no exact value, construction, or preprint found |
| This draft (E) | 0.0301389036 | computational, two independent exact recounts |

Margins of (E): 5.95e-6 below PPSS, 3.37e-6 below McKay, 9.6e-8 below the
rounded 0.030139.

**Honest status.** We cannot compare with the Feinstein–Even-Zohar value: the
announcement states only an upper threshold, and their construction may be
lower than ours.  The announcement's description ("randomized, structured,
symmetric") is compatible with ours; we make **no claim of a record, of
novelty, or of independence from their work** until their construction is
public.  Softening a structured blow-up is itself prior art (Thomason's
random perturbation, as recounted by Even-Zohar–Linial).  The lower-bound side
(flag algebras) is not addressed here.

## 6a. Convergence evidence (independent starts)

| Run | classes | exact value | decimal | independent start | shares B192 structure | audit |
|---|---|---|---|---|---|---|
| E7 run010 (Cayley on F_64 x Z_12) | 768 | 67603793210844365850594037608134633/2243072242887045535525174414223081472 | 0.030138928171 | yes (random 0/1 seeds) | yes (earlier iterate of run012) | direct U256 |
| E7 run012 (converged, projected KKT 4.4e-15) | 768 | 33801895922290936849104250872162095/1121536121443522767762587207111540736 | 0.030138927562 | yes (random 0/1 seeds) | yes: a Z2^2 lift of B192 (lane E7's claim, not re-verified by P) | direct U256 |

An abelian Cayley search with no B192 input converged into the B192 basin,
which is evidence (not proof) that B192 is a natural attractor rather than an
artefact of the PPSS seed.

## 6b. Newer candidate (lane E4, audited 22:40 UTC)

A 3840-class vertex-transitive orbital kernel on a coset action G/K
(|G| = 46080, |K| = 12) of the group recovered from B192 has exact value
2112616269946473812116180096163290703/70096007590220172985161700444471296000
= 0.030138895816959867 (7.7e-9 below (E)), verified by group-invariance +
transitivity checks and a rooted exact CRT count (`research/round4-P.md`).
It is symmetry-certified with 456 orbital parameters (23 fractional) and may
be a better headline than (E) once described; the rooted audit is conditional
on the verified transitivity, not a full O(N^4) recount.

## 7. Gaps before submission

1. Literature: obtain the Feinstein–Even-Zohar value/preprint; check Thomason
   1997 primary text; confirm the McKay reference source.
2. B192 now has a closed form (section 3.1); the Z5 phase table remains an
   explicit 1248-entry table (only a Z2 symmetry per lane E10).  The table
   should be re-keyed to the closed-form coordinates (x, a, e, σ) via
   E11's vertex map before publication.
3. Optional formal certificate (compact Lean proof of the motif expansion on
   the 192-class quotient), or a third recount on a different machine.
4. Precise citations with theorem numbers for the lifting lemma (the proof
   above is self-contained, so this is presentational).
5. Explain why the Z5 pentagon twist helps (derivative/phase heuristics are in
   research notes, not a theorem).
