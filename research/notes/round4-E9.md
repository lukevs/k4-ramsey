# Round 4 lane E9: other lift groups and voltage assignments for B192

Window 22:29–23:00 UTC, 2026-09-27. Code: `experiments/round4_E9/` (lift.py, opt.py,
tower*.py). Runs: `reports/round4-E9-*/`. All values are float64 search-side
numbers. Nothing here is certified and nothing is submitted for promotion.

## Hypothesis record (H-R4-E9)

- **Claim.** The gain of (C) over (B) comes from a twisted (voltage) cyclic lift.
  Other groups Z_m, or other voltage assignments, give more.
- **Prediction.** Some m != 5 (or a second lift stacked on (C)) beats (C) with the
  same number of parameters.
- **Disconfirmation.** No m beats Z5 under the same search, and the Z5 phase table
  is locally optimal.

## What ran and results

1. **Control, passed.** My own builder plus a numpy strided evaluator reproduce
   C(9;7,4,8) = 0.030138925766133334 (exact 4198776398959/139314069504000 =
   0.030138925766133366; the difference is float round-off). Time 7.5 s.
2. **Voltage choice (Z5 table), locally optimal.** `round4-E9-z5ctrl-001`: the
   phase table was the start point, and I searched over single and batched
   phase or inactive moves (linear-gradient proposals plus an exact re-evaluation).
   No phase move was accepted, even the single best proposed flip. Only moving
   the levels helped: 0.0301389047 at (p0,x,y) ≈ (.7803,.4482,.8895), which is
   (D)-like and not new. **Restricted negative:** lane P's table is 1-flip
   locally optimal.
3. **Trend in m, same search, random start phases, about 160–200 s each.**
   | m | S (on-pattern) | best F | vs (B)=0.0301389941 |
   |---|---|---|---|
   | 3 | {±1} | 0.0301419908 | worse |
   | 4 | {±1} | 0.0301397307 | worse |
   | 5 | {±1} (random start) | 0.0301393777 | worse |
   | 5 | lane P table (control) | 0.0301389258 → 0.0301389047 | better |
   | 6 | {±1} | 0.0301398300 | worse |
   | 7 | {±1} | 0.0301414802 (only 4 iterations, N=1344) | worse |
   The random-start greedy search cannot even rediscover the Z5 mechanism: with
   random phases, Z5 ends above the unlifted base. So this table is
   **uninformative about m.** It measures the search method, not the groups.
   Label: search failure, not evidence against other m.
4. **Structure check (pure Python).** After gauge-fixing on a spanning forest, the
   Z5 phases leave a large residual (residual classes 0..4 = 304/232/97/100/243
   over 976 active pairs). So the phase table is a genuine twist, not a coboundary.
5. **Stationarity argument for Z_{5k} (answers R2-4, analytic).** The exact
   embedding of (C) into Z_{5k} uses the pull-back S' = {d : d mod 5 = ±1} and a
   phase g' ≡ g (mod 5). The coordinator's suggested form, 4g with S={±3,±4,±5},
   is an arc family and not an exact blow-up. At the blow-up, the gradient G is
   constant on cosets of the kernel. So every refinement direction inside Z_{5k}
   (phase shifts by the kernel, adding or removing single pattern elements) has
   first-order change equal to an average of Z5 moves, and those are already
   non-improving (item 2). **Z5 is first-order stationary for every Z_{5k}
   refinement.** Any gain from larger m must come at higher order.
6. **Z2 voltage tower on (C) (answers R1-3; this is where the signal is).** Take
   W'_{(u,s),(v,t)} = W_uv + ε·D_uv·(-1)^{s+t} on 1920 classes. Averaging over
   characters removes the ε¹ and ε² terms exactly. The leading term is cubic:
   T(D) = (4/N⁴) Σ_{ijk} D_ij D_ik D_jk Σ_l (W_il W_jl W_kl − (1−W)_il(1−W)_jl(1−W)_kl).
   - With D equal to the mask of all fractional entries: T = 2.877e-6, which is
     nonzero. So the tower gives strict descent: sign(ε) = −sign(T).
   - Exact float evaluation of the materialised 1920-class tower at ε=−0.1:
     **F = 0.030138925091 (Δ = −6.75e-10 vs (C))**. The prediction from the cubic
     term alone is −2.88e-9, so the quartic term is about +2.2e-5·ε⁴, and the best
     ε is about 0.1 along this direction. (`round4-E9-tower-002`)
   - Other directions: the power-iterated grad-T direction gave −2.2e-10
     (`-003`). Per-type amplitudes (p0,x,y)=(.15,.2,.1) were worse (+1.1e-8,
     the quartic term dominates) (`-005`). (0,.1,.1) gave −1.1e-10 (`-006`).
   - The sign scan of T over per-type ±1 patterns (`-004`) gives T=0 for any
     single type alone, and ±2.877e-6 for every three-type pattern. With (0,.1,.1), T = 5.1e-10, against 2.9e-9 at (.1,.1,.1). So the
     cubic term needs mixed-type triangles (consistent with R2's PPH structure),
     and it is largest when all three types are perturbed.
   **Positive mechanism result, but tiny.** A second lift improves (C) by about
   7e-10, about 1% of the Z5 gain. It does not approach the incumbent (E).

## Not done (time)

- Noncyclic groups: Z3² with Paley(9), Z2⁴ with Clebsch, Z2×Z4, S3, D5
  (lane E10 is covering dihedral).
- Larger m with an informed start.
- A tower on (E), and re-optimising levels jointly with the tower.

## Decision

- **Revise.** The "other m" half of the hypothesis is untested in any meaningful
  way: random-start search fails even for Z5. For m = 5k it is first-order
  stationary.
- **Pursue** the tower as a real but small mechanism, since it strictly
  descends at order ε³.
- No candidate beats 0.03013890356539909. None beats (C) at ≤ 960 classes, so
  there is **no SUBMIT FOR PROMOTION**.

## Next test

1. Z2 tower on (E) d4763 with D = fractional mask, jointly with re-optimising
   (p0,x,y) and per-type amplitudes. Also a Z3 tower, whose complex characters
   give a cubic term on all triangles.
2. An informed start for Z_m: transport the Z5 triangle holonomy pattern (the ±1
   sign field on PPH triangles, R2) into Z_m by solving for phases whose triangle
   sums hit ±(nearest pattern offset). Then run the same opt.py polish at equal
   budget.
3. Z3² with Paley(9) against Z9 at |S|=4, starting from the same kind of
   holonomy transport.
