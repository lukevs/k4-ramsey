# Round 4 lane E11: the coupled-Clebsch family (R2-3)

Window 22:41 to 23:12 UTC, 2026-09-27. Local only, one single-threaded job at a time (each run took at most about 2 minutes), no commits.
- Code is in `experiments/round4_E11/`.
- Receipts are in `reports/round4-E11-{sweep,design,multilevel,abel16,srg,twist}-001/`.
- **No candidate was submitted for promotion.**

## Hypothesis record

- **H-R4-E11 (R2-3).** B192 is one member of a family: copies of a strongly regular or Cayley graph on F2^n, arranged by a block-level design, with fractional bridges. Other members could be competitive.
- **Prediction.** An F2^5 analogue (the folded 6-cube) comes within about 1e-5 of B192.
- **Disconfirmation.** Either the rule is not low-complexity, or every analogue scores 0.0302 or more. Then B192 is a one-off and the family directions retire.

**Outcome.** The rule is *extremely* low-complexity (Theorem-level description below), but every analogue that changes the graph (away from Clebsch) or the block design is worse by at least 1.1e-4 (best is Clebsch with the 16-block design (m,r)=(4,2) at 0.030254; best non-Clebsch graph is Petersen at 0.030511). Clebsch variants such as blow-ups, twists and pattern changes are worse by 2e-8 to 2.6e-5. **B192 is a sporadic, Clebsch-specific point. The family direction is retired (restricted negative).**

## 1. B192 in explicit coordinates (exact, verified entry by entry)

Vertex set: Q x [12] with Q = F2^4. The 12 blocks are the orbits of the perfect core of G.

Let
- S = {e1, e2, e3, e4, 1111}, and
- C = {0} ∪ S, a 6-set. Cay(F2^4, S) is the Clebsch graph.

Then there is a labelling of each block by F2^4, and a 12x12 symmetric "type matrix" T, such that

  W((x,s),(y,t)) = g_{T[s,t]}(x+y),

where the four type functions are:

| type | on 0 | on S | off C |
|---|---|---|---|
| Z (includes s=t) | 0 | 0 | 1 |
| X | 1 | 1 | 0 |
| P | p | p | 0 |
| H | h | 1 | 0 |

W is the red probability. For B192, p = 51064/65536 and h = 35015/65536.

Properties of the rule:
- **All inter-block identifications are the identity.** The raw shifts a_st satisfy a_st = b_s + b_t, so they are a pure gauge.
- **There is no linear twist.** Only the 16 translations of block t make M_0t translation-invariant.

**Block design.** The 12 blocks are Z3 x Z2 x Z2, written (a, e, σ). T depends only on the difference (da, de, dσ):
- dσ = 0:
  - (0,0) → Z
  - da = 0, de = 1 → H (the "dimer" matching)
  - da ≠ 0, de = 0 → X
  - da ≠ 0, de = 1 → Z
- dσ = 1:
  - da = 0 → P (a K_{2,2} between the two dimers {(a,·,0)} and {(a,·,1)})
  - da ≠ 0 → Z

In words:
- There are 6 H-dimers, forming two "sides" of 3.
- Within a side, same-end blocks are X and cross-end blocks are Z. So each side is a pair of X-triangles joined by an H-matching.
- Dimer a on side 0 is joined to dimer a on side 1 by a full P K_{2,2}.

This gives R2's per-vertex counts (6 Z, 2 X, 2 P, 1 H).

**Consequence.** B192 is a *Cayley graphon* on F2^4 x Z3 x F2^2 (order 192), with w(z, da, de, dσ) as above.

Verification:
- `verify_rule.py`: 0 mismatches over all 36672 off-diagonal entries of `reports/literature-two-parameter-001` under the stored permutation (`experiments/round4_E11/perm.json`).
- `iso.py`: block isomorphism T → the Z3xZ2xZ2 design is explicit.
- `family.py` / `design.py`: the rule gives F(32/41, 22/41) = 0.03013899413358829. That agrees in float with lane P's exact 1013294255057839/33620705806123008, and also at (4/5, 2/5).

The continuous two-parameter optimum is F = 0.0301389773 at p = 0.779181, h = 0.534265.

## 2. Analogues tried (search-side float64, (p,h) optimised by Nelder-Mead)

| variant | best F |
|---|---|
| B192 (Clebsch, Z3xZ2xZ2 design) | 0.0301389773 |
| F2^4, **all 2^15 connection sets C ∋ 0**, same design | best = the Clebsch sets (all 168 GL-images tie); next is worse |
| F2^5 folded 6-cube {e1..e5, 11111} | 0.033789 |
| F2^5 local search from folded 6-cube, and from Clebsch x F2 | both converge to the Clebsch x F2 blow-up: 0.0301389971 (the H centre is halved, so it is slightly worse) |
| F2^3, all 128 sets (includes the folded 4-cube K4,4) | 0.030428 |
| Z_m, m = 4..24, all symmetric C (12280 sets) | 0.030391 (Z12, Z24) |
| Z4xZ4, Z2^2xZ4 (all symmetric C) | Clebsch again (0.0301389773); Z2xZ8 0.030468; Z16 0.030580 |
| other srgs in place of Clebsch: Petersen, Paley 9/13/17, T6, T7, L2(4), L2(5), Hoffman–Singleton, K3,3, K4,4, 4K4, 3K3, and complements | best is Petersen at 0.030511; all others ≥ 0.03046 |
| design Z_m x Z2 x Z_r for (m,r) in {2..6} x {1..4} (6 to 48 blocks) | best non-B192 is (4,2) at 0.030254; (3,3) 0.030813; (3,1) 0.033637 |
| one type uses a different Clebsch set C' + a (3 x 168 x 16) | no improvement; next distinct value is 0.0301648 |
| discrete neighbourhood: one type's (0,S,off) pattern replaced by any of {0,1,p,h}^3 | best is 0.0301419 (P → "h p 0"); all worse |
| 15 free levels (type x {0, S, off}, with the diagonal block separate) | **KKT-rigid**: every 0/1 level has an outward-pointing derivative. Splitting P or H by class gains nothing |

Smallest slacks among the 0/1 levels (dF per unit move into the interior) are relevant to R2-5:
- H on S (at 1): +9.2e-6.
- Intra-block off-C (at 1): +1.8e-5.
- Z centre: +1.2e-3.
- All other 0/1 levels: at least 1.5e-4.

Evidence labels:
- Section 1 is an exact entrywise identity against the certified base.
- Section 2 is search-side float with restricted neighbourhoods. It is not an impossibility result.

## Decision

- **Retire** "vary the underlying srg, group or n" in the coupled-Clebsch family. No analogue with a different graph or design came within 1.1e-4.
- The prediction of an F2^5 analogue within 1e-5 **failed**.
- **Keep** the Section 1 description for lane P's paper. B192 = Cay(F2^4 x Z3 x F2^2, w) is a three-line construction: the Clebsch scheme ⊗ a 12-vertex Cayley design, with two levels.

## Next test

The only competitive directions left in this family are lifts and twists that break the translation or design symmetry (E9's Z5 and R2-1's D5 voltages). A natural next step is to phrase the Z5 phase table in these coordinates.

Phases live on (P-pair, x+y ∈ C) of the Cayley design. The test is whether the incumbent's phase field is an affine or character function of (x, y, a, e, σ), for example g = χ(x) - χ(y) + c(da, de). That would give a closed-form 960-class incumbent-grade construction for the paper.

Second: open the two cheapest 0/1 levels (H on S, and the intra-block off-C level) *together with* the Z5 lift. Their slacks (1e-5) are the same order as the lift's gain.
