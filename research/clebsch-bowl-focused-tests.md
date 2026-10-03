# Focused Clebsch bowl tests — 2026-09-29

Distributed work remains paused. User authorized the proposed focused tests.
One local single-threaded compute job at a time, no remote or paid compute.
Initial pilot: full-objective derivatives on a reproducible subset of the
checked depth-2 construction, with a ten-minute per-job ceiling; inspect results
before choosing any follow-up. No automatic incumbent promotion.

## CB-WALL-001

Question: do the cheap formerly solid coarse edge types already admit a
negative inward derivative in the finite depth-2 graphon?

Prediction: all screened inward derivatives are positive. Disconfirmation:
one negative full-objective derivative, then verified by exact arithmetic.

Test: independently enumerate the six-factor product-rule derivative on tiny
integer matrices, then evaluate the complete rooted-edge derivative on the
3840-class matrix. Cover every cheap coarse pair with a seeded sample, and
all latent endpoint pairs on the cheap coarse pairs incident with coarse class 0.
All ordered tuples, including repeated indices, are included. No T5/T6 omission.

Domain: finite equal-class perturbations of the stored candidate. Positive
samples do not certify a wall in graphon space, or signs on untested entries.
Also audit the coarse block means: a two-parameter equal-mean family must not
be claimed to contain a heterogeneous-mean candidate without verification.

Status: completed; positive in the tested finite directions.
Code: `experiments/clebsch_bowl/support_screen.py`.

Results:

- Initial screen: 7,425 fine pairs, all inward derivatives positive.
- Expanded screen: all 1,440 cheap coarse pairs, every fine endpoint pair.
  Verified the two global XOR generators entry by entry, reducing 576,000
  fine pairs to 144,000 representatives. All numerical derivatives positive.
- Minimum inward derivative: 4.574674855100866e-11 at fine pair (920,2608).
  Direct integer CRT gives exactly
  `3822641889643488999949/83560952651763168555690885120000`,
  or 4.574674855101511e-11. The CRT computes the complete rooted-edge sum,
  including all repeated class indices, with six primes and certified
  below-2^53 integer dot products. This confirms the numerically worst pair;
  the other signs remain a floating-point exhaustive screen.
- The derivative formula passed 60 literal integer brute-force checks with
  maximum absolute discrepancy 1.11e-16.
- Depth-2 coarse means are exactly uniform within each fractional type:
  P = 0.7791748046875, H = 0.5361785888671875. Every fine row in a coarse
  bridge has exactly this mean; all coarse hard blocks are unchanged.
- Main run: 30.62 seconds, one native thread.
- Receipts: `reports/clebsch-bowl-support-001/report.json` and
  `reports/clebsch-bowl-support-002/report.json`; code snapshots and raw
  derivative arrays are preserved beside them.

Decision: pursue fixed-support refinements first. No first-order leak was
found in either weakest solid type at the depth-2 point. This does not prove
stability under arbitrary graphon refinements, other hard types, coordinated
changes to fractional entries, or finite-size steps.

## Correction to the proposed wall test

The earlier C1 opening calculation is insufficient for a universal wall:
it counts a single new latent edge and omits changes to the coefficients of
old moments as coarse means move. For general rare-state changes, terms with
multiple newly opened edges also need bounds. A complete finite-candidate
gradient is a useful diagnostic, but does not fix that universal proof gap.

## CB-MOMENT-001

Claim: enforcing the true asymmetric probability box on the path Gram matrices
reduces the relaxation's unrealistically favorable diamond correlations.
Prediction: tenfold reduction of negative T5 credit, or a numerically useful
increase in the objective floor. Disconfirmation: no useful tightening.

For a spine edge of mean p, let D be its centered kernel and let s collect
two-edge path kernels between its endpoints. Define

`A = E[s s^T], B = E[D s s^T], C = E[D^2 s s^T]`.

The entries of B are diamond moments. Since -p <= D <= 1-p pointwise,

`p A + B >= 0`, `(1-p) A - B >= 0`,
`p(1-p) A + (1-2p) B - C >= 0`

in the positive-semidefinite order. Each follows by averaging `s s^T`
times a pointwise nonnegative scalar. Added these to the existing C1 Gram
relaxation behind `LOCALIZE=1`; default behavior is preserved.

Validation: 180 matrices from 60 weighted feature fixtures, including spine
values at both endpoints of the box, agree with direct nonnegative weighted
outer-product sums to 8.89e-16. This checks the added inequalities, not the
entire older SDP formulation. The unchanged control reproduces its old value.

| Quantity | Control | Added localizers, scale 1e6 |
|---|---:|---:|
| T3 | -3.74158e-7 | -3.58335e-7 |
| T4 | +1.91646e-7 | -4.61763e-7 |
| T5 | -1.15767e-6 | -2.13157e-7 |
| absolute T6 allowance | 2.04926e-7 | 2.04926e-7 |
| numerical allowed gain | 1.54510229e-6 | 1.23818041e-6 |
| numerical objective floor | 0.0301374321874 | 0.0301377391093 |

The initial scale-1e8 run returned `optimal_inaccurate` and is preserved.
Scales 1e6 and 1e7 both returned `optimal`; their objective floors differ by
2.81e-14. Maximum constraint violations were 1.70e-10 and 4.89e-10.
No rationalized dual certificate exists: these are numerical relaxation
results at fixed (p,h), not a proved universal bound for variable means.
Each SDP run took 5–7 seconds, one native thread.

Receipts: `reports/clebsch-bowl-localizer-{control,001,1e6,1e7}/`.
Source: `experiments/round5_C1/sdp2.py`; new-inequality validator:
`experiments/clebsch_bowl/validate_localizers.py`.

Decision: revise the tenfold prediction. T5 shrinks about 5.43-fold, but
T4 changes sign and accounts for much of the remaining unrealized gain.
The allowed total gain shrinks by about 20%. It was too strong to describe
diamonds as the only unresolved lever: correlations among overlapping
four-cycles and diamonds must be constrained together.

## Next focused step and stopping state

No new construction or improved upper bound was produced. Strongest existing
structured-exact result remains depth-2 at 0.030138887566497220.
There are no jobs from this focused run left running; distributed work stays
paused.

Next: inspect the most favorable four-cycle moment assignments in the new
relaxation and ask whether they can be realized jointly by finite zero-row-mean
bridge kernels. Derive overlapping-path consistency inequalities, and use a
joint Z5 x Z2^k finite kernel fit as the constructive counterpart. Failure to
round a moment assignment is not itself a proof that it is unrealizable.
Ultimately a bottom requires a checked upper construction and a certified
matching lower bound for the same domain; symmetry and decreasing increments
alone do not establish it.
