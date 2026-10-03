# Lane C: global necessary structure, 2026-09-30

## Contract and state

Deadline 04:16 UTC. One host-Python single-thread job at a time, each <=180 s;
no Sage, remote compute, shared edits, outreach, commits, or subagents.
Domain: arbitrary symmetric measurable W in [0,1], arbitrary vertex masses,
all repeated latent indices included. F=t(K4,W)+t(K4,1-W), c4=inf F.
Baseline checked lower bound L=36226165105091/1260000000000000;
checked incumbent about 0.030138887566497220. No matching certificate.

Read required prior notes and PPSS Section 4. Prior retired transfers include
assuming global regularity, imposing non-tight certificate kernels, and
claiming elementary overlap squares are beyond the standard hierarchy.

## Hypotheses

- C1 (variational/global): rooted monochromatic K4 density R(x) must have
  variance O(F-c4). Test through exact vertex-mass perturbations on arbitrary
  rational graphons, including nonzero diagonals and unequal masses.
  Own elementary derivation; no novelty claim. Status: proved and tested.
- C2 (obstruction): constant R alone need not imply balanced degrees or a
  particular template. Test explicit transitive and two-block controls.
  Status: exact counterexample, including below the random bound.

## Main result: quantitative rooted stationarity without a template

**Mathematical theorem (informal proof, not proof-assistant checked).** Let
W be any graphon and set

    H(x1,x2,x3,x4) = product_{i<j} W(xi,xj)
                     + product_{i<j} (1-W(xi,xj)),
    F = E H,  R(x) = E[H | x1=x],  V = E(R-F)^2.

Then

    F - c4 >= (4 - sqrt(6 F(1-F))) V.                 (C1)

In particular a graphon with F <= c4+epsilon satisfies
V <= epsilon/(4-sqrt(3/2)). Every global minimizer has R=F almost everywhere.
If F <= 1/32 the coefficient is at least

    4 - sqrt(186)/32 = 3.573806821969192... > 7/2.

These statements assume neither regular degrees nor Clebsch structure,
triangle-freeness, deterministic edges, finite support, or a tight certificate.
They also hold for any bounded symmetric four-variable objective kernel
H in [0,1] on a domain closed under changes of vertex measure, with its own
infimum in place of c4. No sharpness claim for the constant.

### Proof

Work on the original probability space and put h(x)=R(x)-F. Thus E h=0,
E h^2=V and -F <= h <= 1-F. The density q=1-h=1+F-R is nonnegative and
has integral one. Reweight the underlying vertex measure by q, retaining W;
this gives an admissible graphon (for a step graphon, simply change masses).
Write its objective as Fq=E[H product_i(1-h(xi))]. Therefore Fq>=c4.

In L2 of four independent vertices, the four functions h(xi) are orthogonal.
The function

    Z = H-F-sum_i h(xi)

is orthogonal to constants and to every function of any one vertex:
conditioning on xi gives E[Z|xi]=0. Hence

    ||Z||_2^2 = E H^2 - F^2 - 4V <= F(1-F)-4V,

where 0<=H<=1. In particular 0<=V<=F(1-F)/4.
Expand product_i(1-hi)=1-sum_i hi+S, where S is the sum of all terms of
degrees 2,3,4. Products indexed by distinct vertex subsets are orthogonal,
because E h=0. Consequently

    ||S||_2^2 = 6V^2+4V^3+V^4,
    Fq = F-4V+E[Z S].

Cauchy--Schwarz yields

    Fq <= F-4V+V sqrt((F(1-F)-4V)(6+4V+V^2)).       (C2)

Set s=F(1-F)<=1/4. Expanding the product in the square root gives

    (s-4V)(6+4V+V^2)
      = 6s+(4s-24)V+(s-16)V^2-4V^3 <= 6s.

Combine this with Fq>=c4 to obtain (C1). Reweighting a Lebesgue graphon by
the bounded density q is admissible; the resulting atomless probability
space can be represented on [0,1]. Zero-density regions can be discarded.
The proof covers F=0 or 1 as well: then V=0. QED.

The earlier elementary expansion produced weaker constants 143/128
(universal) and 3442751/2654208 (F<=1/32). Its frozen reports remain as
development evidence; (C1) supersedes it.

### Numerical consequence of the checked gap

For any available verified L<=c4, (C1) implies

    V <= (F-L)/(4-sqrt(6F(1-F))).

Using the displayed incumbent F=0.030138887566497220 and checked
L=36226165105091/1260000000000000 gives approximately V<=0.000387568.
This is a numerical illustration using the displayed decimal, not a new
exact evaluation of that incumbent. The simpler rational coefficient 7/2
gives a fully rational bound when an exact rational upper threshold is used.
The bound is useful as a necessary condition, but does not identify a graphon.

## Concrete lower-bound input: an optimizer-only seven-vertex constraint

Put B(W)=E R(x)^2. If W_n is any minimizing sequence, (C1) gives

    F(W_n) -> c4,  V(W_n) -> 0,  B(W_n) -> c4^2.

For any verified upper bound U>=c4, every limit of its seven-vertex moment
vectors therefore obeys

    B <= U F.                                        (C3)

Such a limit exists by compactness of the finite probability simplex.
Thus adding (C3) to a valid finite moment relaxation still gives a lower
bound on c4: the relaxation contains a moment vector of objective c4.
**This is an optimizer-only constraint, not a universal graphon inequality.**
No assumption about uniqueness, existence of a finite extremizer, or Clebsch
is involved. Fair-coin W=1/2 violates it when U<1/32, which is expected.

For an induced seven-vertex graph G, the coefficient B(G) is the fraction
of 140 choices (a root and a three-subset of its other six vertices) such
that both four-sets formed with the root are monochromatic. Their colors
may differ. The denominator is 7*C(6,3)=140, and the two unordered wings
are counted twice consistently. F(G) is its monochromatic four-subset
fraction, denominator C(7,4)=35. The two wings are disjoint apart from the
root, so conditional independence proves E B(G)=E R^2, also for fractional
graphons and repeated latent class samples. No repeated edge is squared.

`reports/lower-frontier-C-cut-001/cut.json` exports exact rational
coefficients B(G)-U F(G) for all 1044 stored seven-vertex representatives,
with U=0.030138888 (rounded upward from the checked incumbent). The row
order and input hash match `toolbox-extension-001/pentagon-portable.json`.
Twenty-two selected representatives were separately checked by all 5040
vertex permutations, and checked under relabeling and complementation.

**Missing experiment:** test this cut against an actual N7/N9 primal vector,
then solve the restricted relaxation and independently certify its dual.
No N7 primal vector was located in the portable certificate, and no solve
was run. No claim that the cut escapes the N9 cone or improves a bound.
At most seven vertices appear in B; this is a global stationarity restriction,
not a claim of new high-order local flag machinery. Root may pass the cut to
lane B after checking this distinction.

A threshold-valid, weaker inequality for all graphons with F<=U<=1/32 is

    (1 + (7/2)U) F - (7/2) B >= L,

obtained from (C1), F^2<=UF, and L<=c4. Unlike (C3), this version applies to
the entire indicated sublevel set, not only minimizing limits.

## Exact obstruction: rooted stationarity does not imply regular degrees

Take any vertex-transitive regular graphon A with red degree p, objective
F0, and total monochromatic triangle density T. On two equal halves put A
on the first, 1-A on the second, and 1/2 on cross pairs. Call the result W.
Translations make rooted K4 densities constant within each half. Swapping
halves complements W, leaving H unchanged, so R is constant everywhere.
Nevertheless the two degrees are 1/4+p/2 and 3/4-p/2. Thus

    Var(R)=0,  Var(d)=(p-1/2)^2/4,
    F(W)=F0/8+T/16+3p(1-p)/64.                      (C4)

Proof of (C4): four vertices split between halves as 4+0 with probability
1/8, 3+1 with probability 1/2, and 2+2 with probability 3/8. Conditional
monochromatic probabilities are respectively F0, T/8, and p(1-p)/8.
For regular A, Goodman's identity gives T=1/4+3(p-1/2)^2; this identity was
independently tested by direct rational triangle counts below.

For the explicitly defined B192 companion at (p_parameter,h)=(32/41,22/41),
whose exact value was already independently recounted in the required notes,

    F0 = 1013294255057839/33620705806123008,
    p  = 3973/7872,
    F(W) = 8368659238977991/268965646448984064
         = 0.031114230941628126... < 1/32,
    Var(d) = 1369/247873536 > 0,  Var(R)=0.

This is an explicit 384-class fractional graphon. It disproves any finite-C
claim Var(d)<=C Var(R), even among graphons beating random. It does **not**
disprove a degree-stability theorem confined to a much tighter neighborhood
of the unknown c4. The B192 base value is reused from prior exact recounts;
this lane did not perform a fresh 384-class full recount. Its partition
formula was checked independently on 15 small transitive rational bases.

Even regular rooted stationarity cannot establish optimality: B192 itself
has V=0 throughout its Cayley family, while the checked incumbent is strictly
better than the rational companion above. A new global relation connecting
rooted K4 stationarity to useful degree/overlap restrictions remains missing.

## Tests and evidence boundaries

- `exact_tests.py`: 433 exact rational graphons, including all 125 symmetric
  two-class matrices over {0,1/4,1/2,3/4,1} at three mass ratios, 48 seeded
  random weighted matrices of sizes 1--6 with arbitrary diagonals, complete
  and cycle controls, and balanced/unequal Clebsch graphons. Ordered tuple
  recount and separate multiset/multinomial recount agree. Both early tilts
  satisfy their exact decrease bounds. Seed 9302026.
- `structural_checks.py`: 128 arbitrary symmetric binary four-variable kernels
  (a test broader than graphons), 15 literal color-swap graphons, and five
  nonstationary sub-random fixtures built by adding a fair-coin class to B192.
  At mass 1/1000000, F=0.030138998610742852 and V~1.2528e-12.
  These fixtures use the established exact base value and exact partition
  formulas. They are not new upper-bound candidates.
- `orthogonal_check.py`: checks the stronger (C2) by exact squared rational
  comparisons, including 433 graphons, 128 arbitrary kernels, and those five
  nonstationary fixtures. No floating-point tolerance is used for acceptance.
  Floating values appear only in display fields. All pass.
- `export_stationarity_cut.py`: exports and crosschecks (C3), as above.
- `final_audit.py`: separately differentiates the unordered-multiset K4
  polynomial in each mass and verifies all 986 saved root-density values
  across all 433 graphons. All agree exactly. Receipt and input/source hashes
  are in `reports/lower-frontier-C-audit-001/audit.json`.

All five jobs were host Python 3.14.6, standard library only, single-threaded,
with a 170-second alarm. Each completed in under one reported second.
Commands, timings, interpreter/source/input hashes, and exact fractions are
in `reports/lower-frontier-C-{exact,structural,orthogonal,cut}-001/`.
No optimizer, Sage, native threaded library, or remote compute was launched.
The proof is mathematical prose plus exact tests, not formal verification;
two enumeration orders are a crosscheck, not an independent human review.

## Sources and transfer audit

- [PPSS, Section 4.2](https://link.springer.com/article/10.1007/s10208-024-09675-6):
  Theorem 4.9 and Lemma 4.10 assume matching extremal certificates; their
  reconstruction and kernel conclusions cannot be imposed from our N6 gap.
  The present result instead varies vertex measure directly and retains the
  gap. Section 4 supplied context, not a premise in proof (C1).
- [Diao--Guillot--Khare--Rajaratnam, Differential Calculus on Graphon Space](https://arxiv.org/abs/1403.3736):
  adjacent primary work on derivatives/Taylor expansions of graphon densities.
  Only abstract inspected; no attribution of (C1) to it and no novelty claim.
- Required local inputs: `round4-P-paper-draft.md` (B192 exact companion and
  Cayley rule); `round5-F4.md` (restricted-family optimality boundaries);
  `global-lower-bound-transfer-audit.md` (retired global regularity transfer);
  `certificate-guided-upper-search.md` (non-tight certificate gap);
  `global-coupled-pilot.md` (normalization and existing moment hierarchy).

## Decision and process state

**Pursue** the exact optimizer-only stationarity cut as one bounded diagnostic
against saved primal moments; **retire** inference from rooted stationarity
alone to degree regularity, a Clebsch template, or optimality.
The concrete deliverables are theorem (C1), counterexample (C4), and the exact
1044-row cut artifact. No improved numerical or certified lower bound claimed.
All launched jobs completed. No worker process remains active. Initial handoff
is ready before 04:16 UTC; no further computation is needed for these claims.
