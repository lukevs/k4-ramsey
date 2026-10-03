# Round 4 lane E5 — probability-adaptive sign refinement (graphon tensoring)

Window 22:12–23:12 UTC 2026-09-27. Code: `experiments/round4_E5/`. Runs:
`reports/round4-E5-opt-00{1,2,3}/`, `reports/round4-E5-depth1-001/`,
`reports/round4-E5-depth2-001/`.

## Hypothesis record (H-R4-E5)

**Claim.** The rank-one sign split
`W'((u,s),(v,t)) = W(u,v) + s t A(u,v)`, `s,t in {+1,-1}` uniform, with a
*free signed amplitude* `A` supported on the fractional entries of the
incumbent d4763fef and boxed by `|A| <= min(p,1-p)`, lowers `F` by a
material amount (> 1e-9), unlike the fixed amplitude `A = eps p(1-p)`
tested earlier (gain ~2e-11 on b93).

**Prediction.** Optimised `A` gives `Delta F <= -1e-9` at depth 1, and depth
2 (the same move applied to the 1920-class child) does not reverse.

**Disconfirmation.** `T3 = 0` identically on the support, optimised gain
below 1e-9, or a non-negative optimum at depth 2.

## Exact identity (verified)

Sign-averaging kills every edge subset of `K4` with an odd-degree vertex, so
for rank-one sign kernels exactly

    F(W') - F(W) = T3(A) + T4(A),
    T3 = 4/n^4 sum_{u,v,w} A_uv A_vw A_wu sum_z (p_uz p_vz p_wz - q_uz q_vz q_wz)
    T4 = 3/n^4 sum_{u,v,w,z} A_uv A_vw A_wz A_zu (p_uw p_vz + q_uw q_vz)

(`q = 1-p`, uniform class weights, all repeated class indices included:
`A_uu = 0` but `u = w` or `v = z` terms in `T4` survive via `q_uu = 1`).
The quadratic term vanishes identically, so this is a genuinely third-order
move that no second-order (Hessian) test of the fixed class space can see.
With signed `A`, `T4` can be negative (it is at the optimum).

Validation (`validate.py`, `exact_validate.py`):
- float `T3+T4` vs direct recount of the materialised 2n-class graphon on
  random 9-class graphons with 0/1 entries: agreement to 1e-17; gradient vs
  finite difference to 1e-10 relative;
- exact rational `Delta` (`exact.py`: python-int `S3`, CRT `S4`) equals the
  literal ordered-4-tuple Fraction recount on a 6-class Q=64 case exactly.

Scale-invariance note: the one-line gain `-27 T3^4 / (256 T4^3)` is
invariant under rescaling `A`, so only the *shape* of `A` matters until the
box binds; at the optimum ~52% of the support is at the box.
Multi-channel variants (independent characters of `F_2^k`, `k` channels,
budget `sum_r |A^r| <= min(p,1-p)`) give `sum_r Phi(A^r)`; since the optimum
is box-limited this cannot beat one channel (splitting the budget scales the
cubic term down). Not run.

## Results

All numbers exact rationals unless marked float. Incumbent parent d4763fef:
`F0 = 16900934504649027287619486865996291/560768060721761383881293603555770368`
= 0.03013890356539909.

| step | amplitude A | classes | Delta F | F |
|---|---|---|---|---|
| audit baseline (b93-style) | `eps p(1-p)`, eps opt | 1920 | -2.02e-11 (float) | — |
| random-sign `c`, random-sign `m` starts | — | — | ~0 / stalled | — |
| depth 1, start `-m sign(grad T3)`, 250 s + 480 s projected gradient (opt-002, opt-003) | free signed, 52% at box | 1920 | **-775895085614712958567643070937/93461343453626897313548933925961728000** = -8.3018e-9 | **0.03013889526362365** |
| depth 2 (same move on the 1920 child, 470 s, 63 iters) | free signed | 3840 | **-53953783254030113357594058139/7009600759022017298516170044447129600** = -7.6971e-9 | **0.03013888756649722** |
| depth 3 (float only, 9 iters, not materialised) | free signed | 7680 | -3.93e-9 (float, still descending) | ~0.0301388836 (float) |

Depth-1 checks: float `T3+T4` of the rounded integer amplitude
(-8.301775439379308e-9) agrees with the exact rational to 1e-23; an
**independent direct float recount** of the materialised 1920-class JSON
(`direct_float.py`, plain ordered K4 contraction, no use of the T3/T4 identity)
gives 0.030138895263623688 vs predicted 0.03013889526362365 (diff 4e-17).
Depth-2 checks: float vs exact rational agree to 1e-24 (the S4 CRT path here
is float-BLAS mod 16-bit primes, a different code path from depth 1's int64
path; depth-1 S4 was computed with the int64 path). No direct recount at 3840
classes (cost ~16x depth 1; out of window).

Amplitudes are rounded to integer numerators over the parent's Q = 65536
with `|a| <= min(N, Q-N)`, so the child keeps denominator 65536 and uniform
weights; no denominator growth at any depth. Construction: child class
`2u + (s == -1)`, numerator `N(u,v) + s t a(u,v)`.

## SUBMIT FOR PROMOTION

Both are `rational-step-graphon-v1`, uniform weights, Q = 65536.

1. **Depth 1 (primary, cheaper to audit):**
   `reports/round4-E5-depth1-001/graphon-candidate.json`
   SHA256 `a0524bbaa7d4313a561bdbcd06d1022710c9405014b45ad6e429bac520e02cf7`,
   1920 classes, predicted exact
   `8450464924639256799670867730068932689/280384030360880691940646801777885184000`
   = 0.03013889526362365 (improvement 8.30e-9 over d4763fef).
2. **Depth 2 (best):**
   `reports/round4-E5-depth2-001/graphon-candidate.json`
   SHA256 `05302cbc635e939cc41f4ba019cdcba80199b0b83563100bac0b1a0d9fff1a29`,
   3840 classes (163 MB JSON), predicted exact
   `8450462766487926638466333426306607129/280384030360880691940646801777885184000`
   = 0.03013888756649722 (improvement 1.600e-8 over d4763fef).

Evidence level: depth 1 is exact-predicted plus an independent float direct
recount; depth 2 is exact-predicted only (search-side code). Neither has been
through lane P's independent U256 audit. Both remain far above the 0.030138
target (need ~9e-7 more).

## Decision

**Pursue (revise).** The free-amplitude sign split is a real third-order
descent direction that the fixed-support/Hessian tests cannot see, it does
not reverse at depth 2 or 3, and each depth costs no denominator growth. But
the per-depth gain is ~8e-9, ~4e-9 at depth 3 with truncated optimisation,
roughly two orders of magnitude short of the 0.030138 target unless it keeps
up over ~50-100 depths, which class-count doubling (3840 -> 7680 -> ...)
rules out by direct materialisation. The mechanism does not deliver a
robust margin; it does produce a verifiable incremental record.

## Next test

1. Lane P: audit depth 1 (1920 classes) directly; depth 2 needs a
   structured checker (e.g. the T3/T4 identity checked by an independent
   implementation, or a histogram audit over the two-level sign structure).
2. Combine instead of stacking: optimise depth-1 and depth-2 amplitudes
   jointly on `F_2^2` (two characters plus their product), which adds the
   degree-3 (K4-e, K4) terms absent for rank one, before paying the class
   doubling. Also re-polish the parent's own fractional entries after the
   split (the split changes the first-order landscape).
3. Stop rule: if joint depth-2 on `F_2^2` gives < 2x the stacked gain, retire
   the tensoring route as a record-polishing tool, not a margin mechanism.


## Process notes

One single-threaded job at a time (VECLIB/OMP threads = 1, `timeout 600`),
with one exception: the 6-class exact-vs-literal validation (<5 s) ran while
opt-002 was active. Compute ended 22:59 UTC. Depth-3 amplitude (float) is
kept at `reports/round4-E5-depth3-001/A.npy` for a later materialisation.
