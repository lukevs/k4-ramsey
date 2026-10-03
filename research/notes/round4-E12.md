# Round 4 — lane E12: λ-homotopy (graduated objective), R1-2 gated by R1-6

Window used: 22:41–22:56 UTC. One single-threaded numpy process at a time, each job < 70 s.
All numbers are float64 search-side values (evidence: numerical, not audited). No exact recount was
needed: nothing went below 0.0301389258, let alone the incumbent.

## Hypothesis record
- **H-R4-E12.** Minimising F_λ(W) = t(K4,W) + λ·t(K4,1−W), moving λ from 1 to 2.5 or 0.6 and back
  (10 + 10 steps, re-optimising at each step), carries the construction into a different basin at λ=1.
- **Prediction.** At least one path ends at λ=1 in a distinct basin (a different 0/1/fractional
  pattern, not just a colour swap). After polishing, that basin is within 1e-8 of the incumbent or better.
- **Disconfirmation.** Every path returns to the incumbent basin or ends worse than plain descent
  with a matched budget.

## Step 0: R1-6 gate (red/blue split)
| construction | total | red | blue | (red−blue)/total |
|---|---|---|---|---|
| d4763 (exact, from `reports/graphon-association-per-edge-boundary-continuation-direct-u256-001/report.json`) | 0.0301389036 | 1.01233e39 | 1.01578e39 (/N^4Q^6) | −3.4e-3 |
| C(9;7,4,8) Z5 lift (float, E9 builder) | 0.030138925766 | 0.015024690 | 0.015114235 | −3.0e-3 |
| B192 (32/41, 22/41) (float) | 0.030138994134 | 0.015064815 | 0.015074179 | −3.1e-4 |
| E4 3840 (P audit numbers) | 0.0301388958 | — | — | −3.3e-3 |

Blue is heavier in every case, and the asymmetry is above R1-6's 1e-4 threshold. For the lifts it is
about 10× larger than for B192, so the gate passes and R1-2 was run. The Z5 lift increases the
red/blue imbalance.

## Step 1: runs
Code: `experiments/round4_E12/homotopy.py` (N=192 K4 evaluator plus analytic gradient, adapted from
E9's `lift.py`), `run_levels.py`, `run_full.py`, `run_polish.py`, `gate.py`.

**(a) B192 symbol-level family** (z,f,p,h for the 0/F/P/H symbols, diagonal 0), projected gradient.
`reports/round4-E12-levels-001/results.jsonl`.
Seeds: b192 (32/41,22/41), p/h swapped (22/41,32/41), (½,½), and an interior point (.2,.8,.6,.4).
- Control (plain descent at λ=1, matched or larger budget): every seed reaches the same point,
  (z,f,p,h) = (0, 1, 0.779181, 0.534269), F = 0.0301389772897. This is the continuous (p,h) optimum
  of B192. It is a known-family point (B192 ladder), 7.4e-8 above C(9;7,4,8).
- λ paths: every "down" (0.6) path ends at the same point, ±7e-14 relative (unconverged tails).
  The "up" (2.5) paths end worse (0.03013900–0.03013904). The interior-seed up path is stuck at
  0.0312069 with z,f interior.
  **No path beats control.**

**(b) Full 192×192 kernel** (every off-diagonal entry free, diagonal 0), projected gradient,
4 iterations per λ step plus 20 polish iterations. `reports/round4-E12-full-001/`.
Seeds: b192, swapped, and a noisy Turán-3 blow-up.
- Control: b192 and swapped both give 0.030138977290, pattern (n0,n1,frac) = (17664,16704,2496).
  This is the same point as (a). Gradient flow preserves the B192 symmetry.
- Down paths: b192 gives 0.03013917. Swapped gives 0.03013904, and after polishing it is back at
  0.030138977290 with the same pattern.
- Up paths (b192, swapped, and a b192 seed with σ=0.01 symmetric noise) all end at **one other
  stationary point**: F = 0.03014062106, pattern (17664, 13824, 5376). At this point all P and H
  entries, plus 15 F entries per row, merge into a single level 0.890244 (≈73/82).
  Polishing does not move it (`reports/round4-E12-polish-001/`).
  It is a distinct basin, but it is **1.64e-6 worse** than control.
- Turán-3 seed: every path stalls near 0.03125 (the Turán/random-like regime), far from the others.
- Noisy b192 control (σ=0.01, 304 evals) returns to 0.030138977290 with the B192 pattern.
  At this budget, noise does not escape the symmetric basin.

## Step 2: inspection / results
- λ<1 (down) paths: return to the B192 basin.
- λ>1 (up) paths: move to a different active pattern (the P/H/partial-F levels merge at ≈0.8902),
  which is a worse stationary point, +1.6e-6.
- Nothing below 0.0301389258. **No candidate. Nothing to submit.**

## Decision
**Retire at this scale (restricted negative).** On the B192-symmetric manifold (4 levels) and on the
full N=192 kernel with gradient descent, the λ-homotopy either returns to the incumbent B192 basin or
lands in a worse merged-level basin. This follows the disconfirmation branch. It does **not** test
homotopy on the Z5 lift (N=960, about 8 s per evaluation here, too slow for this window) or on the
d4763/E4 3840-part constructions. That is where the red/blue asymmetry is 10× larger and the
hypothesis would matter most.

## Next test (if anyone reopens)
Run the homotopy on the Z5 lift C(9;7,4,8), with the 3 levels plus phase flips (E9's `opt.py` loop
with an objective of red + λ·blue), using the strided evaluator in C++. Also try λ ∈ [0.8,1.25] with
finer steps, because the 2.5 excursion is clearly too violent (it collapses the level structure).
Compare with matched-budget E9 control. Cost: about 1 CPU-hour. Priority is below E9/E4 refinements.
