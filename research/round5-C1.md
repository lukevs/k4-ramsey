# Round 5 lane C1: analytic ceiling on lifts of B192, and the character of B192

Window 23:15 to 00:15 UTC, 2026-09-27/28. Local only; one single-threaded job at a time (every job under 10 minutes, most under 10 s); no commits.
- Code: `experiments/round5_C1/`.
- Receipts: `reports/round5-C1-{char,walks,sdp,sdp2,sdp2-scale1e8,sdp2-scale1e10,sdp3-sym,sdp3-asym,sdp4-asym,sdp5-trunc-asym,scan-002,extras-002,z5decomp,open}-00*/`.
- Everything is float64 and search-side. The SDP bounds are numerical interior-point optima with no rounded dual certificate. **No candidate was produced, so nothing is submitted for promotion.**

## Hypothesis record (H-R5-c)

- **Claim.** An analytic upper envelope on the gain of any lift of B192 lies above 0.030138.
- **Prediction.** The envelope's floor, B192 minus the ceiling, is above 0.030138. If so, B192-lift routes should be retired for the record target.
- **Disconfirmation.** The floor is at or below 0.030138. The relaxation then names the latent moments a winning lift would need.

## 0. Framework (exact, validated)

**The lift.** A lift is W'((u,x),(v,y)) = W_uv + D_uv(x,y) on the fractional pairs of B192 (2496 entries, i.e. 1248 pairs). It satisfies:
- D_vu = D_uv^T;
- latents x, y live in a probability space;
- rows have mean zero: E_y D_uv(x,y) = 0 = E_x D_uv(x,y);
- 0/1 entries do not move.

**Exact expansion.** Averaging the latents kills every edge subset of K4 that has a degree-1 vertex. This leaves

ΔF = T3 + T4 + T5 + T6.

The four terms are:

| Term | Pattern | Coefficient | Moment |
|---|---|---|---|
| T3 | triangles | (4/n^4) Σ_{abc} c3(abc) | tr(D_ab D_bc D_ca), where c3 = Σ_d (W W W − Q Q Q) |
| T4 | closed 4-walks | (3/n^4) Σ_{abcd} (W_ac W_bd + Q_ac Q_bd) | tr(D_ab D_bc D_cd D_da) |
| T5 | diamonds | (6/n^4) Σ (W_zw − Q_zw) | E[D_xy · (D_xz D_zy) · (D_xw D_wy)] (pointwise product) |
| T6 | K4 | (2/n^4) Σ | the six-edge moment |

Repeated slot classes are included; they use independent latents and W_uu = 0.

**Validation.**
- A random 3-state latent lift of every fractional pair: the expansion (`expand.py`) matches a direct recount of the materialised 576-class graphon to 7.6e-18. Here ΔF = 1.16e-8, T5 = −1.5e-11 and T6 = −1.9e-13, so every term is exercised (`validate.py`).
- **The Z5 lift C(9;7,4,8) is exactly in this family** (`z5decomp.py`). It equals the B192 base at levels (7/9, 8/15) plus a pure latent lift. The row means are exactly zero (up to 2e-17). The expansion reproduces F(C) to 4e-18. The decomposition is:
  - base-level cost +1.67e-8;
  - T3 = −1.96e-7;
  - T4 = +1.23e-7;
  - T5 = +4.8e-9;
  - T6 = −1.5e-10.

  So the gain is a triangle gain opposed by 4-cycles. Diamonds and K4 are negligible and slightly unfavourable.

## 1. Character of B192 (p = 0.77918083, h = 0.53426505, F = 0.030138977289665)

**KKT data** (`reports/round5-C1-char-001/char.json`). The gradient is dF/dW per unordered pair, and the level derivative is summed over the orbital.
- **Fractional levels.** P on {0} and on S, and H on {0}, are stationary: the level derivatives are at most 2e-10, which is optimiser tolerance.
- **Every 0/1 level has a strictly outward gradient**, so strict complementary slackness holds.
- **Multipliers** (dF per unit level move into the interior):

  | Level | Multiplier |
  |---|---|
  | H on S | 9.16e-6 |
  | intra-block off-C | 1.83e-5 |
  | X on {0} | 2.7e-4 |
  | X on S | 4.0e-4 |
  | intra-block S | 5.2e-4 |
  | H off | 1.03e-3 |
  | Z on {0} | 1.18e-3 |
  | P off | 2.0e-3 |
  | Z off | 2.3e-3 |
  | X off | 2.8e-3 |
  | Z on S | 5.0e-3 |

  These agree with E11.
- **A coincidence worth noting.** The per-entry gradients of H-on-S and intra-off (−1.908e-8) are identical. So are those of intra-S and H-off (1.076e-6).

**Second-order refinement check (L2's necessary condition).** Use row-term moves D = r_uv(x) + r_vu(y). Their P3-rooted 13x13 matrix M_u is **positive definite**:
- eigenvalues 1.85e-7 (x5), 1.92e-7, 1.97e-7 (x5), 2.77e-7, 2.86e-6.

So B192 is second-order refinement-stable. No vertex-splitting move gains at second order, and every lift gain must start at cubic order. This explains "the quadratic term vanishes".

**Balance.**
- Red density 0.504606.
- t(K4, red) = 0.0150474 and t(K4, blue) = 0.0150915. Red and blue are nearly balanced; blue is 0.3% heavier.

**Spectrum of σ = 1 − 2W** (eigenvalue/n, multiplicity):
- −0.1061 (2), −0.0882 (24), −0.0693 (30), −0.0465 (20), −0.0460 (15), −0.0092 (1);
- 0.0189 (1), 0.0368 (12), 0.0557 (15), 0.0785 (40), 0.0790 (30), 0.1158 (2).

**The fractional pattern graph.**
- Spectrum: 13^3, 5^45, (−1)^96, (−3)^45, (−11)^3.
- It is **3 disjoint 64-vertex components**, one per Z3 coordinate a. Each component is 4 Clebsch blocks: an H perfect matching (x = y) plus a P "bipartite Clebsch" K_{2,2} of blocks.
- Per vertex: 12 P pairs and 1 H pair.

**Fractional subgraph census** (ordered counts; details in `reports/round5-C1-walks-001/walks.json`):
- **Triangles.** 6912 ordered, i.e. 1152 triangles, all HPP, each containing exactly one H edge. There are no PPP triangles, because the P graph is bipartite between the σ-sides.
- **Closed 4-walks.** 161472.
  - Non-degenerate: 94464 PPPP, 2304 HPHP, 2304 PHPH.
  - Degenerate: backtracking and doubled walks.
- **Diamonds.** 36864 ordered.
- **Fractional K4s.** 6912 ordered, i.e. 288 K4s. In each, the H edges form a perfect matching of the K4.

**The cubic tensor is a single number.**
- c3 = +0.83901547 on **every** fractional triangle. It is invariant under the full symmetry group, and so is T3 = (4 c3/n^4) Σ_triangles tr(D D D).
- Because c3 > 0, **a lift gains only if its latent triangle moments are negative**. Every PPH triangle must be "latently frustrated": in sign-kernel language, holonomy −1.
- **Quartic coefficients.** W_ac W_bd + Q_ac Q_bd lies in {0, 0.2208, 0.4657, 0.5023, 0.5343, 0.6559, 1}, and is always ≥ 0. The non-degenerate 4-cycle moments are indefinite, so T4 is not sign-definite.

## 2. Ceiling problem

**Relaxation.** A tracial Gram (moment) SDP (`sdp2.py`).
- For each endpoint pair (a,b), take the Gram matrix of the words D_ab, the length-2 paths D_ac D_cb, and the Hadamard words D_ab∘(D_ac D_cb). It must be PSD.
- Its entries are the triangle, 4-walk and diamond moments, shared across blocks.
- Further constraints:
  - ||D_e||_2^2 ≤ box;
  - ||D_ac D_cb||^2 ≤ ||D_ac||_op^2 ||D_cb||^2;
  - Hadamard diagonals ≤ sup|D|^2 · q and ≤ ||S||_∞^2 · ||D||^2.
- T6 is bounded in absolute value.

**Symmetry reduction.** The problem is reduced by F2^4 translations. This is valid because the relaxation is convex and invariant.

**Solver checks.** The solution is stable to 1e-15 under objective rescaling by 1e8 and by 1e10. Unscaled runs are ~0.3% low; I quote the scaled values.

**Two box models.** They must be kept apart.
- **Symmetric box, |D_e| ≤ min(W, 1−W).** This covers the E5-type sign splits and small-amplitude towers on B192 itself. It does *not* cover Z5, whose P kernel reaches −1/3 > 0.22.
- **True box, D_e ∈ [−W_e, 1−W_e].** With zero row means this gives E D^2 ≤ W(1−W) (Bhatia–Davis) and sup|D| ≤ max(W, 1−W). This covers every lift, including Z5, 0/1-valued latent patterns, and all depths and towers.

| bound (gain = B192 − F) | symmetric box | true box |
|---|---|---|
| crude box bound, fully rigorous (Σ \|coef\| × moment bounds; degenerate 4-walks dropped as ≥ 0) | **9.10e-7** (floor 0.0301380672) | not useful (T5 box 2.6e-5) |
| Gram SDP (T3 + T4 + T5, T6 box) | **2.28e-7** (floor **0.03013875**) | **1.55e-6** (floor 0.03013743) |
| relaxed optimum terms | T3 −2.18e-7, T4 +1.01e-7, T5 −1.06e-7, T6 box 5e-9 | T3 −3.74e-7, T4 +1.92e-7, T5 −1.16e-6, T6 box 2.0e-7 |
| truncated model T3 + T4 only (not a bound) | — | 8.2e-7 |

**Joint base-level moves.** The ceiling moves slowly with (p, h): the symmetric-box SDP over 7 level points gives 2.15e-7 to 2.49e-7. The base cost is quadratic with curvature about 1e-2. So re-optimising the levels jointly with a lift can add at most about 1e-10. The floor minimum stays at the B192 optimum (`scan-002`).

**Achieved gains, for comparison** (all versus B192 at 0.0301389773):

| construction | gain | relative to the bounds |
|---|---|---|
| rank-one sign split on B192 itself (this lane, symmetric box: ε_H = −1, λ_P = 0.567, λ_H = 0.893; T3 −1.11e-7, T4 +8.3e-8) | 2.8e-8 | 12% of the symmetric-box SDP ceiling |
| Z5 C | 5.2e-8 | |
| Z5 polished (d4763) | 7.4e-8 | |
| E4-3840 | 8.2e-8 | |
| E5 depth 2 | 9.0e-8 | |
| E5 depth 3 | ~9.4e-8 | 6% of the true-box SDP ceiling |

**Opening 0/1 support** (a mean shift d plus an arbitrary latent, first order in d; `open_asym.py`). The cubic plus quartic linear-rate bounds are:
- H-on-S: 8.6e-6, against a multiplier of 9.16e-6;
- intra-off: 1.72e-5, against 1.83e-5.

Both are *below* the multiplier, but by only about 6%. Diamond and K4 linear rates are not included. So opening support is **not excluded** at first order by this bound. With the symmetric box the rates are 7 times below the multiplier.

## 3. Verdict

1. **Symmetric-box lifts of B192 (E5 or E9 style on B192 itself): retired for the target.**
   - The ceiling is 2.28e-7 (Gram SDP, numerical) and 9.10e-7 (elementary, rigorous up to float summation).
   - The floor is at least 0.0301380672, which is above 0.030138. The SDP floor is 0.03013875.
2. **General lifts, including Z5 and every tower of it: not decided.**
   - The true-box relaxation ceiling is 1.55e-6, giving a floor of 0.03013743. That is below the target, so the relaxation *cannot* rule the target out.
   - The looseness is almost entirely diamonds. The relaxation credits T5 = −1.16e-6, while the real Z5 lift has T5 = +4.8e-9. Non-degenerate 4-cycles are the second source.
   - **Restricted conclusion.** To reach 0.030138 through a lift, a kernel would need one of two things:
     - **(a) triangle moments near their maximum on all 1152 PPH triangles** (T3 about −3.7e-7, roughly 1.9 times Z5's) while keeping the 4-cycle cost near zero; or
     - **(b) substantial negative diamond moments.** This needs E[D_xy S_z S_w] < 0 where σ_zw < 0 (wings red) and > 0 where the wings are blue. D_xy would have to correlate with the product of two triangle-paths across the spine.

     Every lift built so far has |T5| ≤ 5e-9. Route (b) is the only large unexplored lever the bound identifies.
   - **For F2.** A Ramsey-critical latent should be judged by its (T3, T4, T5) triple through `expand.py`, not by T3 alone. Paley/Clebsch kernels give zero odd diamond moments in sign form (E s^3 = 0). They will therefore sit in the triangle-only regime, whose realised efficiency so far is at most 6% of the ceiling.

## 4. Plain-language character (for the paper)

B192 is a strict, second-order-stable local optimum with a very small, rigid "soft part":
- Every red/blue-certain pair is held in place by a strictly positive price. The cheapest price is about 1e-5 per unit level.
- The uncertain pairs form three identical 64-vertex bridges between Clebsch copies. Their only triangles are 1152 copies of one triangle type (two P edges and one H edge), and every one of them has the same positive "triangle price" c3 = 0.839.

Any refinement that keeps the certain pairs fixed can gain only by making hidden correlations that are negative around these triangles. Such correlations necessarily create 4-cycle correlations, which cost. That is why every observed improvement is cubic, small, and saturating.

For the refinements people have actually built:
- If a hidden variable's amplitude stays within min(p, 1−p), the total possible gain is at most 2.3e-7 (and at most 9.1e-7 by an elementary argument). That is well short of the 9.8e-7 needed for 0.030138.
- The largest lifts built (Z5 and its E4/E5 descendants, about 1e-7) already reach about 40% of that symmetric-box ceiling. They use larger, 0/1-valued hidden patterns, which that bound does not cover.
- For fully general lifts, the analysis leaves one theoretical escape route: hidden correlations on "diamonds" (two uncertain triangles sharing an H edge). No construction to date uses it.

## Decision

- **Retire** symmetric-amplitude lifts of B192 for the target. The ceiling is below the target gap by at least a factor of 4 (SDP), and the elementary rigorous bound also excludes them.
- **Keep, but downgrade**, general B192 lifts. The only lever is the diamond moment. Achieved lifts are at 6% of a loose ceiling.

## Next test

1. Tighten the true-box relaxation. Add third-order Hadamard words S_z∘S_w and the moment inequalities that come from D ∈ [−W, 1−W] pointwise (localising constraints (D + W)(1 − W − D) ≥ 0 multiplied into the Gram). Prediction: the T5 credit drops by at least 10 times and the floor rises above 0.030138. That would retire all B192 lifts.
2. Lane F2 should screen candidate latents by their exact (T3, T4, T5) from `expand.py` before any polishing. Look specifically for kernels with E[D_xy (D_xz D_zy)(D_xw D_wy)] of sign −σ_zw.
3. Lane F1: the opening-support bound is not decisive (6% margin, diamond rates missing). Compute the diamond and K4 linear rates for H-on-S before spending search time.
