# Round 4 lane E3 — PatternBoost-style learned seeding (H-R4-E3)

Window 22:12–23:12 UTC 2026-09-27. Local, one single-threaded process, jobs <= 10 min.

## Hypothesis record

- **Claim (H-R4-E3):** alternating local search -> bank of good, diverse local
  minima -> learned generative model -> sample -> local repair -> retrain yields
  better post-repair results than (b) random seeds or (c) perturbed bank members
  at a matched number of repair calls (training cost included).
- **Prediction:** the model arm's post-repair distribution (median, q10, min, count
  beating the bank median/best) is better than both controls, and improves over rounds.
- **Disconfirmation:** model arm not better than the best control at matched calls
  across rounds/seeds; or the model does not capture structure (samples no closer
  to good minima than matched perturbations; post-repair outputs not distinct).

## Representation and evaluator

- 0/1 Cayley graphs Cay(G,S), S=S^{-1}, identity blue (blue diagonal blow-up).
  Bitstring = one bit per inverse-pair orbit. Value
  `(c_R + c_B)/n^3`, `c_X = #{(a,b,c) in X^3 : a^-1 b, a^-1 c, b^-1 c in X}`
  (X = S, or T = G\S including e), i.e. `t(K4,W)+t(K4,1-W)` of the n-step graphon.
- Code: `experiments/round4_E3/cay.c` (bitset exact integer count, first-improvement
  descent, tabu), `groups.py` (groups F2^k, F2^k x| C3, abelian products; ctypes wrapper;
  brute-force n^4 homomorphism oracle), `pboost.py` (alternation + controls).
- **Validation:** `validate.py`: exact agreement (to 1e-15, both integer-derived) with
  literal n^4 hom counts on Z12, F2^4, F2^2 x| C3 (= A4, nonabelian), Z2xZ4xZ3,
  4 random S each. All 16 PASS.
- Group screen (`timing.py`, `t2.py`): tabu(100 steps) from random seeds gives
  F2^8: best 0.03033686, 300 steps 0.03030795; F2^6 x| C3: ~0.0312–0.0316;
  F2^7 x| C3 (n=384) descent 0.03157. F2^8 (255 bits, ~24 us exact eval) chosen.

## Design of the controlled comparison (`pboost.py`)

Round 0: 96 random seeds (density U(0.3,0.7)) -> repair -> bank. Each round r>=1:
bank top-K=48 (deduped by exact value, a crude isomorphism dedupe) ->
four arms, **32 seeds each, identical repair (tabu, fixed steps, tenure m/12)**:
- `model`: fully-visible sigmoid belief net (autoregressive logistic, 255x255 lower-
  triangular weights, L2 1e-2, Adam 400 full-batch steps) trained on the bank; sample T=1.
- `indep`: product-Bernoulli fitted to bank marginals (model ablation).
- `random`: iid bits at density drawn from the bank's density range.
- `perturb`: random bank member + k random orbit flips, **k = median Hamming distance of
  model samples to their nearest bank member** (matched perturbation).
All repaired outputs join the shared bank. Training (and alignment) seconds are
logged against the model arm; it is <= 1% of the arm's repair time (0.13–0.85 s/round vs ~21 s).

## Runs and exact results

Values are exact rationals `tot/256^3`; decimals below are those ratios.

### run 001 — `reports/round4-E3-pb-001/` (F2^8, tabu 100 steps, no alignment, seed 0)
6 rounds (perturb: 5 — last arm killed by the 600 s timeout). Averages over rounds:

| arm | avg median | avg q10 | best | # beat bank median | # beat bank best |
|---|---|---|---|---|---|
| model | 0.030647467 | 0.030350782 | 0.030307233 | 58/192 | 3 |
| indep | 0.030739749 | 0.030404650 | 0.030307233 | 53/192 | 1 |
| random | 0.030742392 | 0.030412966 | 0.030307949 | 49/192 | 0 |
| perturb | 0.030762876 | 0.030419292 | 0.030307949 | 49/160 | 2 |

Per-round median ranking is inconsistent (model best in 3/6 rounds). Bank pairwise
Hamming stays 126–127 of 255 (= random-looking) because F2^8 Cayley sets are only defined
up to GL(8,2); model samples sit at Hamming ~86 from the nearest bank member (partial
memorization), and repair moves them to ~104 — i.e. repair washes the seed out.

### run 002 — `reports/round4-E3-pb-002-align/` (as 001 + GL(8,2) alignment, seed 1)
Bank members aligned to the bank best by greedy transvection hill-climb (3x3000 moves,
value-preserving, verified by exact re-evaluation). Alignment reduced pairwise Hamming
only 127 -> 117 (to-reference 94): distinct minima are genuinely non-isomorphic, not
just mis-oriented. 5 rounds:

| arm | avg median | avg q10 | best | # beat bank median |
|---|---|---|---|---|
| model | 0.030671352 | 0.030318359 | 0.030307949 | 60/160 |
| indep | 0.030657732 | 0.030364252 | 0.030307949 | 59/160 |
| random | 0.030747664 | 0.030433331 | 0.030307233 | 36/160 |
| perturb | 0.030800450 | 0.030391811 | 0.030307949 | 40/160 |

### run 003 — `reports/round4-E3-pb-003-weak/` (weak repair: tabu 30 steps, alignment, 40 seeds/arm, seed 2)
12 rounds, 480 repairs per arm (per-sample exact values logged):

| arm | pooled median | pooled q10 | best | P(model < arm), pairwise | round-median wins |
|---|---|---|---|---|---|
| model | 0.031739950 | 0.031696260 | 0.031538904 | — | 8/12 |
| indep | 0.031750619 | 0.031701267 | 0.031596839 | 0.582 | 2/12 |
| random | 0.031747758 | 0.031706989 | 0.031619728 | 0.573 | 2/12 |
| perturb | 0.031747043 | 0.031700552 | 0.031614780 | 0.570 | 0/12 |

AUC 0.57–0.58 with 480 vs 480 (SE ~0.019): a real but small seed effect (~1e-5 in
median). Model training+alignment cost 11.3 s vs ~108 s repair per arm (~10% overhead,
i.e. the model arm had the equivalent of ~528 calls vs 480 — the AUC edge is larger than
what 10% more calls buys at these spreads, but this was not separately measured).
Independent-marginal ablation = random: the gain needs the pairwise (autoregressive) terms.

### run 004 — `reports/round4-E3-pb-004-rep/` (replicate of 002: tabu 100, alignment, seed 3, per-sample values)
4 rounds, 128 repairs per arm:

| arm | pooled median | pooled q10 | best | # at <= 0.0303080 | P(model < arm) |
|---|---|---|---|---|---|
| model | 0.030684173 | 0.030310094 | 0.030307233 | 8 | — |
| indep | 0.030782223 | 0.030422390 | 0.030307949 | 6 | 0.518 |
| random | 0.030780017 | 0.030428886 | 0.030307949 | 3 | 0.555 |
| perturb | 0.030735016 | 0.030339003 | 0.030307949 | 5 | 0.521 |

Round-median wins: model 2/4, perturb 2/4. Model training+alignment 3.6 s vs ~92 s repair.

Across runs 001/002/004 (strong repair) every arm terminates in the same attractor set;
the best exact value found anywhere is `508471/16777216 = 0.030307233333587646`
reached by model, indep and random arms alike.
This is ~1.69e-4 above the incumbent 0.03013890356539909: no candidate, nothing to promote.

### run 005 — `reports/round4-E3-lift9-005/` (side probe, not part of the H-R4-E3 test)
F2^9 (n=512, 511 bits), tabu 60 steps, alternating exact 2-blow-ups of banked F2^8
minima (twins blue; lift value equals the parent value exactly) vs random seeds, 360 s:
lift arm 16/16 -> `4052780/134217728 = 0.030195564031600952`; random arm best
`4226271/134217728 = 0.031488172709941864`. Growth-by-lift beats fresh search at n=512
by 1.3e-3, but remains 5.67e-5 above the incumbent.

### run 006 — `reports/round4-E3-lift10-006/` (side probe)
F2^10 (n=1024): exact 2-blow-up of the run-005 best, first-improvement descent (8 s):
`32400975/1073741824 = 0.030175759457051754`; then repeated tabu(20) from the best:
`32400219/1073741824 = 0.030175055377185345` (12 tabu rounds, stalled after the 6th).
Still 3.62e-5 above the incumbent. Saved `best10.npy` / `best10.json` (not a candidate).

### Structure of the attractor (`analyze.py`, run-004 bank)
Best F2^8 set: |S|=129, algebraic degree 8, only **7 distinct Cayley eigenvalues**
(-11..13; multiplicities incl. -7x84, 9x56, 5x48, -11x36) — a spectrally rigid object,
not a random-looking set. Bank entries 1–7 share one 11-eigenvalue spectrum, i.e. the raw
bank is dominated by isomorphic copies (value-dedupe used for training avoids exact copies,
but raw-bit models still see GL-scrambled versions of a few graphs).

## Interpretation (evidence labels)

- [measured] Under **strong** repair (tabu 100 on 255 bits), seed source barely matters:
  all arms converge into the same small attractor set (0.0303072–0.0303080); the learned
  model gives a better pooled median/q10 in runs 001 and 004 (P(model<control) 0.52–0.56),
  but it is not consistent round-to-round and never finds a better minimum than controls.
- [measured] Under **weak** repair (tabu 30), the autoregressive model gives a small,
  statistically clear edge (AUC 0.57–0.58, 8/12 round-median wins, best 0.031538904 vs
  0.03161 controls) at ~10% compute overhead; the independent-marginal ablation does not.
  So the model does capture *some* pairwise structure, but the gain is on the order of 1e-5
  in an objective where the gap to the target is 1.7e-4 at this size.
- [measured] Representation obstacle: bank bitstrings are mutually at Hamming ~127/255
  (random-looking) because of the GL(8,2) symmetry; greedy alignment removes only ~10 of it.
  The model therefore partly memorises (samples at Hamming ~76–88 from nearest bank member)
  instead of learning transferable structure.
- [measured, side probe] Order-growth by exact blow-up + repair (F2^8 -> F2^9 -> F2^10:
  0.0303072 -> 0.0301956 -> 0.03017506) is far more effective than any seed-source effect,
  but elementary-abelian 0/1 Cayley graphs at n <= 1024 remain above the incumbent.
- [restricted negative] This does not refute PatternBoost for K4: only a small FVSBN, one
  group family, 0/1 sets, and ~2500 repairs per run were tested.

## Decision

**Revise** (not pursue as-is, not retire). No candidate beats 0.03014; nothing submitted
for promotion. H-R4-E3 as stated (learned seeds beat matched controls post-repair) is
*weakly supported only under weak repair* and *not supported* under strong repair, where it
matters for records.

## Next test

1. Symmetry-reduced representation: learn over GL-invariant/canonical coordinates (e.g.
   Walsh-spectrum / ANF low-degree coefficients, or a group with small Aut such as
   F2^k x| C3 with fixed complement) so bank members become comparable; gate = bank
   pairwise distance well below m/2 before training.
2. Put the learned model inside the growth loop (seed F2^{k+1} repairs from model samples
   conditioned on lifts) at n = 512–1024 — where repair is expensive and seed quality
   should matter more — against lift + matched perturbation controls, equal repair calls.
3. Fractional (stochastic Cayley) targets rather than 0/1, since the 192-element fractional
   kernels already reach 0.0301390 while 0/1 sets at 256 sit at 0.03031.
