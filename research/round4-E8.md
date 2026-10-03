# Round 4 lane E8: new-vertex-type pricing (column generation)

## Hypothesis record (H-R4-E8)
- **Claim.** Add a class x of mass eps whose row r ranges over [0,1]^960. Then dF/deps at 0 equals 4(R(r) - F), where
  R(r) = sum_{j,k,l} m_j m_k m_l [r_j r_k r_l W_jk W_jl W_kl + (1-r_j)(1-r_k)(1-r_l)(1-W_jk)(1-W_jl)(1-W_kl)].
  Repeated indices are included and use the diagonal W_jj. If min_r R < F by a useful margin, inserting that type and re-optimising the masses lowers F.
- **Prediction if the hypothesis is useful.** min R - F <= about -1e-4. A gain of order 1e-6 needs a gap of that size, because the gain is roughly (gap)^2 / O(1).
- **Disconfirmation.** min R - F is only about -1e-7 over a thorough search. Then the realisable gain is about 1e-12 or less.

## Method (`experiments/round4_E8/pricing.py`, `massopt.py`)
- R is computed as u^T (A o (A U A)) u + (blue analogue), with u = m o r and U = diag(u). The gradient is 3 m o (g_red - g_blue), where g = (A o (A U A)) u.
- Validation on a random 4-class graphon with a literal 5th class of mass eps = 1e-5, counted by brute force over 4-tuples:
  - Numeric dF/deps = 0.0224045; the formula 4(R - F) gives 0.0224039. They agree to O(eps).
  - sum_i m_i R(W_i) = F exactly, as a check.
- Control on the incumbent: F from the rows is 0.030138903565399063, which matches the exact value. R(W_i) - F lies in [-1.47e-7, +7.0e-8]. So the equal-mass incumbent is **not** exactly mass-stationary; the residual spread is about 2e-7.
- Minimisation used L-BFGS-B on the box [0,1]^960 with an analytic gradient. There were 36 starts (seed 1):
  - 12 existing rows;
  - 4 rows with N(0, 0.2) perturbation;
  - 4 rounded rows;
  - 4 colour-flipped rows (1 - W_i);
  - 6 uniform random rows;
  - 2 near-1/2 starts. The mix-of-two-rows starts did not run because the 480 s budget ran out.

## Results (`reports/round4-E8-pricing-001/log.txt`, `reports/round4-E8-massopt-001/log.txt`)
- **Starts from rows, perturbed rows or rounded rows.** Converged minima give R - F in [-1.9e-7, -1.2e-8]. The best is **-1.911e-7**, from row 87, whose own value is -1.40e-7. The minimisers keep only about 3% of their coordinates interior.
- **Starts from flipped, random or 1/2 rows.** Every one converged to a local minimum **above** F, at +5.2e-5 or +7.4e-5. None found a new basin below F.
- **Insertion with mass re-optimisation.** The best type was added as class 961, followed by 4 rounds of projected steepest descent on all 961 masses with an exact quartic line search.
  - F went from 0.030138903565399063 to 0.030138903562742660, a **gain of 2.66e-12**.
  - Almost all of this comes from reweighting existing classes. The new type took mass only 2e-7.
  - Unequal masses would also need class replication to pass the equal-weight audit (`run_direct_u256_audit` requires block_weights == [1]*n).
- **Two types priced jointly at second order.** Not run. With first-order gaps of about 2e-7, the eps^2 interaction terms cannot produce a 1e-6 gain at any small eps.

## Decision: retire (restricted negative plus a numerical first-order certificate)
- Nothing to submit for promotion.
- Within the searched starts, min_r R(r) >= F - 1.9e-7. The incumbent is therefore first-order optimal against adding one new vertex type, up to the same about 2e-7 non-stationarity that the existing classes already have. The best local improvement found from pricing plus mass re-optimisation is about 3e-12, six orders of magnitude short of the 1e-6 target.
- Evidence label: numerical, multistart, local. It is not a global certificate, because R is a nonconvex cubic on the box. Random starts consistently land at local minima of +5e-5.

## Next test (if continued)
Certify min_r R >= F - delta globally. Two options:
- a branch-and-bound or SDP relaxation of the cubic R over the box, using the orbit structure of the 960 classes to reduce dimension;
- many more random starts in C++, run as a single process.
A global certificate would turn this into "no one-type extension helps at first order". Separately, equalising R_i through unequal masses is worth at most about 1e-11 and is not worth pursuing.
