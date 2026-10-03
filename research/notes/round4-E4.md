# Round 4 lane E4 — stochastic Schreier/orbital kernels on coset actions G/K

Date: 2026-09-27, 22:12–23:12 UTC. Owner: lane E4. Search code; never self-promotes.

## SUBMIT FOR PROMOTION

- candidate: `reports/round4-E4-exact-3840-001/graphon-candidate.json`
  (`rational-step-graphon-v1`, 3840 equal-weight classes, q = 65536, 60 MB)
- SHA-256: `594aaefbf74f72c4465fa898ecc11ffbbb1fbfb98dee7c84b3e69550b1ac2f34`
- predicted exact value:
  `2112616269946473812116180096163290703/70096007590220172985161700444471296000`
  = 0.030138895816959867
- incumbent d476: 0.03013890356539909; predicted improvement 7.748e-9.
  **Not** below the 0.030138 target of interest.
- evidence label: search-code exact recount (u128 C++, vertex-transitive
  formula), float cross-check agrees to 1e-17. Lane-local cross-check
  (`experiments/round4_E4/crosscheck.py`, log
  `reports/round4-E4-exact-3840-001/crosscheck.log`): integer matrix read from the
  JSON is invariant under all 8 generator images, the action is transitive on
  3840 points, and the full uncompressed n^3 exact sum re-based at vertices 0 and
  513 both give the same fraction. Still search-side code; not independent.

Checker warning for lane P: n = 3840 and no twin classes (3840 distinct rows),
so a literal O(n^4) ordered audit is ~2e14 tuples. The graphon is exactly
invariant under a transitive group (the recovered G of order 46080 acting on
cosets of an order-12 subgroup K of the point stabilizer H), so an independent
checker may use t(K4,W) = n^-3 sum_{b,c,d} W_0b W_0c W_0d W_bc W_bd W_cd after
independently verifying (i) entrywise invariance of the integer matrix under
the 8 generator images on 3840 points and (ii) transitivity. Reproduce the
generator images with `experiments/round4_E4/coset_action.py`
(`CosetAction(Base(), K).act_G(g, arange(n))`, K listed in
`reports/round4-E4-exact-3840-001/exact-report.json`).

## Hypothesis record (H-R4-E4)

- Claim: the recovered transitive degree-192 action (|G| = 46080, |H| = 240) carries
  kernels constant on G-orbitals; lifting to coset actions G/K (K < H) gives
  symmetry-breaking directions unavailable in the 192-point quotient and in
  abelian Cayley families.
- Prediction: (a) the 192 orbital kernel is KKT at the archived parent (no gain);
  (b) G/K lifts strictly improve, with gain growing with [H:K].
- Disconfirmation: no G/K lift beating the 192 parent by >1e-9, or orbital
  constancy/reproduction failing.

## What ran

Code: `experiments/round4_E4/` (`coset_action.py` action/orbitals/objective,
`control.py`, `optimize.py`, `opt2.py` fast orbit-rep objective + warm start,
`exact.py` + `exact_count.cpp` exact recount). Objective: f = t(W)+t(1-W),
vertex-transitive O(r n^2) formula, analytic gradient (FD-checked), L-BFGS-B
with [0,1] boxes, single thread.

1. Control (K = H, n = 192): 24 directed orbitals, all self-paired (24 params);
   integer parent matrix reproduced exactly from orbital IDs; G-invariance on all
   8 generators; f = 0.03013897728988013 = archived value. Gradient signs: all
   0-orbitals have positive gradient (>=1.5e-4), all 1-orbitals negative
   (<= -9e-6), fractional orbitals ~ -3e-8. So the 192 kernel is KKT at the parent;
   perturbed restarts return to 0.030138977289665 (restricted negative, as predicted).
2. H-conjugacy classes of 1-/2-generated subgroups of H: 53 classes; orders
   240,120(x3),60,48,40,24(x3),20(x3),12(x8),...
3. Lifts (best L-BFGS-B, pullback start is always the parent value, perturbation
   of the fractional sub-orbitals is required to leave the saddle):

| K order | n | params | best f | report |
|---:|---:|---:|---:|---|
| 240 | 192 | 24 | 0.030138977289665 | round4-E4-screen-001 |
| 120 (3 classes) | 384 | 60/48/48 | 0.030138945327831 | round4-E4-screen-002 |
| 60 | 768 | 120 | 0.030138935296915 (exact 0.030138935296941588) | round4-E4-screen-002, round4-E4-exact-768-001 |
| 48 | 960 | 88 | 0.030138939272659 | round4-E4-screen-002 |
| 24 (class 8, inside order 48, chain from 960 basin 0.030138957199) | 1920 | 176 | 0.030138915884876 | round4-E4-chain-001 |
| 12 (class 20, inside the order-60 K), warm from 768 | 3840 | 456 | **0.030138895816960** (exact above) | round4-E4-k12-001, round4-E4-exact-3840-001 |
| 12 (class 20), warm from 1920 basin | 3840 | 456 | 0.030138915884326 (stays in 1920 basin) | round4-E4-k12-003 |
| 12 (class 20), second perturbation from 768 | 3840 | 456 | 0.030138896372825 (iter cap) | round4-E4-k12-004 |

(round4-E4-k12-002 was killed: warm start used the wrong conjugate of K,
start value 0.030146; fixed with `--from-within`.)

The 3840 optimum has only 23 fractional orbital parameters out of 456.

## Decision

PURSUE (revised). Prediction (a) and (b) both confirmed: the pullback is a
saddle, symmetry breaking via smaller K gives monotone-ish gains
(192 -> 384 -> 768 -> 3840: -3.2e-8, -1.0e-8, -3.9e-8). The result depends on
the basin: the lift path through the order-60 subgroup (A5-like) is
clearly better than the order-48 -> 24 path. The 3840 kernel beats the
incumbent by 7.7e-9 but is ~0.9e-6 above the 0.030138 target; the gains per
halving of |K| are shrinking (~1e-8 scale), so this mechanism alone is not on
track for a robust 1e-6 margin. It is a new, symmetry-certified family distinct
from d476 polishing.

## Next test

- K of order 6/4/2 (7680–23040 points) need a sparser objective (exploit the
  23 fractional params: 0/1 structure) or C++; predicted gains are small.
- Try other order-12 classes (13–19, not inside the order-60 K) and the
  order-24 chain (1920) for different basins; multiple restarts at 3840.
- Check whether d476 (960 classes) is itself a G/K kernel for |K| = 48; if not,
  combine its structure with the G/K orbitals.
