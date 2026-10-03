# Round 4 lane E6: XOR / Boolean products of fractional step graphons

Window: 22:12 to 22:25 UTC, 2026-09-27. Local, single-threaded jobs (VECLIB/torch threads = 1), every job under 10 min. No candidate was produced, so nothing goes to lane P.

## Hypothesis record (H-R4-E6)

- **Claim.** Take the XOR product of the competitive fractional step graphon (d4763fef, 960 classes, 0.03013890356539909; or e26e7541, 192 classes, 0.03013897729) with a small fractional factor that has 2 to 16 classes and is optimised. The colours are independent, so the product has sigma = sigma1 (x) sigma2 with sigma = 1 - 2W. The claim is that this product, or a more general Boolean combination, gets below the big factor.
- **Prediction.** Optimising the small factor against the fixed profile of the big factor finds a value below 0.030138.
- **Disconfirmation.** Every optimised partner collapses to the trivial factor, which is isomorphic to W1. A local certificate would show that moving away from trivial raises the monochromatic density to first order.

## Method (exact bilinear reduction)

The indicator that all six edges are monochromatic equals (1/32) times the sum, over even edge subsets S of E(K4), of the product of chi_e for e in S. So

    mono(W) = (1/32) [1 + 3 e^2 + 12 t(P3) + 3 t(C4) + 12 t(paw) + t(K4)]   (signed densities of sigma)

and, for independent XOR, t_S(sigma1 (x) sigma2) = t_S(sigma1) t_S(sigma2). The product objective is therefore bilinear in two 6-vectors. This is equivalent to the 64-pattern formula in `experiments/xor_partner_gate`, but it is cheaper: e, P3, C4 and paw cost O(n^3) and K4 costs O(n^4). It takes 4.4 s at n = 960.

**Generalisation (affine lift).** sigma((x,a),(y,b)) = g_ab + d_ab sigma1(x,y), with |g| + |d| <= 1. This covers every Boolean combination of W1 with an independent small factor: XOR, AND, OR, and constant patches. The objective is linear in the 11 signed subgraph densities of sigma1, with the closed-form coefficient c_T = prod_T d * (prod_{E\T}(1+g) +/- prod_{E\T}(1-g))/2.

Code is in `experiments/round4_E6/`:

- `sprofile.py`: the profile.
- `partner.py`: XOR partner optimisation and enumeration of +-1 partners.
- `affine_lift.py`: Boolean and affine lifts.
- `diag_derivative.py`: first-order certificates.
- `k4_vs_c4.py` and `ratio_probe.py`: global heuristic probes.
- `alternate.py`: step 4.

## Checks

- **Profile reproduces the incumbent.** mono computed from the profile of d4763fef is 0.030138903565399076, against the recorded value 0.03013890356539909. The first draft had a paw bug (an extra w_a factor); it was found through this mismatch and fixed.
- **XOR formula.** The bilinear XOR formula matches a direct recount of the explicit Kronecker product graphon (3x2 random case): 0.032547275992982794 on both sides.
- **Affine lift.** The affine-lift formula matches a direct recount (random 3-class W1 x 2-class lift): 0.0448265053251617 on both sides.

## Results

### Incumbent profile

Signed densities of d4763fef:

| e | P3 | C4 | paw | K4 |
|---|---|---|---|---|
| -0.0092320 (e^2 = 8.523e-5) | 8.523e-5 (= e^2, regular) | 0.0057690 | -7.5834e-5 | -0.0532306 |

The other signed densities: K3 = 0.0082142, P4 = K13 = -7.87e-7, diamond = 0.0040310.

### Search outcomes

| Search | Big factor | Best found | Outcome |
|---|---|---|---|
| +-1 uniform partners, all colourings for k <= 5 | d4763fef | = incumbent | trivial only |
| Fractional XOR partner, k = 2, 3, 4, 6, 8, 15 starts | d4763fef | 0.030138903567 at best | collapses to trivial (one class takes weight 1) |
| Same two searches | e26e7541 | 0.030138977290 | collapses to trivial |
| Affine / Boolean lift, k = 2, 3, 4 | d4763fef | 0.0301389037 | collapses to trivial |
| Affine / Boolean lift, k = 2, 3, 4 | e26e7541 | 0.0301389832 | no gain |

### First-order certificates at the trivial partner (restricted-local, exact formulas, float evaluation)

- **XOR shrink.** Change sigma2 to 1 - eps*h with h >= 0. Then d mono / d eps = h-bar * (-sum n_S a_S |S|)/32 = **+0.00785 h-bar** > 0. The trivial partner is a strict corner minimum, and the loss is first order, not a second-order saddle.
  - By the envelope theorem, re-optimising the big factor (step 4, alternating) cannot recover this first-order loss near trivial.
- **Vertex insertion.** Insert a partner class of small weight whose sign to all other classes is r. The rate is g(r)/32, which is >= 0 on [-1, 1] and equals 0 only at r = 1. It is dominated by 4|a_K|(1 - r^3) >= 12 a_C (1 - r^2).
- **Composition / substitution (EZL Lemma-6 nesting into diagonal blocks).** All diagonal sigma_ii equal 1. The derivative of mono with respect to decreasing all |sigma_ii| is **+1.48e-5**, which is +0.0142 per unit of diagonal mass. Any internal graphon placed in a block must lower its mean, so it loses at first order. Its structural gain enters only at relative order w_i = 1/960.

### Global heuristic

Suppose the small terms (e^2, P3, paw, each below 1e-3 in weight) are ignored. An XOR partner b then gains only if (1 - b_K)/(1 - b_C) < 3 a_C / |a_K| = 0.325.

Numerical minimisation of this ratio over k <= 12 class partners gives infimum **2/3**. It is attained by a 4-class +-1 colouring with K4 = 1/2 and C4 = 1/4. So the margin is about a factor of 2.

The plain inequality t(K4) <= t(C4) is false: t(K4) - t(C4) reaches 0.25. This is heuristic support only and does not prove anything.

### Step 4 (fix b, optimise the big factor from scratch)

This was not informative. With n <= 32, Adam and L-BFGS on free step graphons fall into the quasi-random attractor 1/32, even for b = trivial. The attempt is recorded in `reports/round4-E6-alternate-001/log-adam-invalid.txt`, which is not evidence either way.

## Decision: retire (restricted negative)

No candidate beat the incumbent, and there is nothing to submit for promotion.

Evidence label: **restricted negative** plus a **local first-order certificate**. This is not an impossibility result, because partners far from trivial were covered only by multistart search for k <= 8 (XOR) and k <= 4 (affine).

The mechanism cannot improve a near-optimal factor locally. XOR with any partner near trivial costs 0.00785 per unit of shrink. Two competitive factors give roughly 1/32 (e.g. the e26 self-product is 0.03134). A win would need a partner with b_K close to 1 but b_C well below 1, and that combination appears not to exist (ratio >= 2/3 found, versus 0.325 needed).

## Next test (if anyone continues)

Prove, or refute with a flag-SDP, the bound (1 - t(K4,s)) >= 0.33 (1 - t(C4,s)) together with the small-term corrections for |s| <= 1. That would turn this into a global XOR-partner negative for any incumbent whose ratio 3a_C/|a_K| stays near 0.33.

Reports: `reports/round4-E6-partner-001/`, `reports/round4-E6-partner-192-001/`, `reports/round4-E6-lift-001/`, `reports/round4-E6-alternate-001/`.
