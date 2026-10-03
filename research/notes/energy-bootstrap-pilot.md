# Energy-conditioned observable pilot

Active main-thread pilot, 2026-09-30. Hypothesis-research protocol applies.
Budget: local single-thread computation, each job <=175 seconds, initial
15-minute ceiling including audit; no agents, installs, remote work or commits.

Question: can conditioning a universal N6 moment relaxation on the checked
upper bound constrain optimizer observables, and can case analysis of their
independence relations strengthen the small reference lower bound?
All graphons are admissible; no Clebsch, regularity or finite-step restriction.

Source: Paul–Refael, https://arxiv.org/html/2605.06784v1, section II.4.
Branching on disjoint-motif factorization is our proposed adaptation.
For an induced motif probability x=t_ind(H,W), disjoint independent samples
have joint probability z=x^2. On x in [a,b], z <= (a+b)x-ab.
The finite moment relaxation need not satisfy this equality. All branches
must cover the allowed interval; selecting only a promising branch is unsound.
F<=U alone cannot raise an old feasible minimum already below U.

Controls: existing independently audited N5/N6 Gram tensors, unconditioned
versus conditioned objective, independent motif-coefficient enumeration,
constant graphon and two-class examples. Initial evidence is numerical only.
Success gate: a separation above numerical uncertainty, followed by rational
dual checking before claiming any bound. A small N6 improvement would still
be below the published frontier (~0.0296).

## Completed result

The pilot produces an independently checked rational certificate

    c4 >= 184262421281 / 6400000000000
       = 0.02879100332515625.

The prior independently checked reference was 0.028750881. The increase is
0.00004012232515625. Both remain below the published bound near 0.0296;
this is method validation at N6, not a new frontier or novelty claim.
All jobs finished. No upper-bound incumbent changed.

## What caused the improvement

Conditioning on F <= 0.030138887566497220 alone changed the numerical objective
only from 0.028750924879 to 0.028750924945 (solver noise).
It bounded red-edge probability numerically to [0.45018,0.54982], triangle
probability to [0.10521,0.14975], and the probability x of exactly one red edge
on a sampled triple to [0.26523,0.47646]. These endpoints are NOT certified.

The unconditioned optimizer had x approximately 0.37453136 and
z-x^2 approximately 0.00190049, where z is the probability that each of two
disjoint triples has exactly one red edge. For a fixed graphon, these events
are independent, so z=x^2 exactly. The moment relaxation permits a discrepancy.
This numerical witness motivated the branch selection; it is not a realizable
construction. Mixtures of different graphons can also produce such a discrepancy,
so this diagnostic alone does not classify a point as an impossible mixture.

The first 16-cell numerical branch test improved the objective to approximately
0.0287910279. The exact follow-up removed the upper-bound constraint completely
and used six intervals covering all of [0,1]. Thus the new bound does not rely
on the numerical observable ranges or the construction's quoted decimal.

## Proof and exact checking scope

For a fixed graphon W, sample six independent latent vertices and independent
edge coins. Let x be the probability that the first three induce exactly one
red edge, and z the probability that BOTH disjoint triples do so. Independence
gives z=x^2. For any interval [a,b] containing x,

    g = (a+b)x - z - ab = (x-a)(b-x) >= 0.

For each of the six intervals the certificate gives rational positive-definite
matrices Q_j and a rational lambda>=0 such that, for every six-vertex graph H,

    c(H) - sum_j <Q_j,C_j(H)>
         - lambda*((a+b)x(H)-z(H)) >= r.

Average over the graphon sample. The existing flag-square construction gives
E C_j positive semidefinite. Therefore F(W)>=r+lambda*ab, since E g>=0.
Use the interval containing x and take the minimum of all six resulting bounds.
No finite-size, regularity, Clebsch, or symmetry assumption on W enters.
These are asymptotic graphon bounds, not lower bounds on the injective density
of every individual small finite graph.

| Interval for x | Checked lower bound |
|---|---:|
| [0,1/4] | 0.0307456909 |
| [1/4,5/16] | 0.029392499190625 |
| [5/16,3/8] | 0.02879100332515625 |
| [3/8,7/16] | 0.02879229712796875 |
| [7/16,1/2] | 0.02942066108125 |
| [1/2,1] | 0.0310201623 |

The independent checker uses only standard-library rational arithmetic. It
rebuilds new motif coefficients from all 720 vertex orders, verifies coverage
of all 32768 labelled graphs, checks nine analytic graphon controls (including
unequal class masses and repeated latent classes), verifies 114 positive-definite
matrices by exact LDL, and checks every graph coefficient and interval endpoint.
The inherited 19 Gram tensors were separately re-enumerated by the existing
independent checker in this session. Their SHA256 binding matches the new receipt.
This is an exact computer-assisted argument with an informal flag-square proof,
not a Lean/kernel proof. The numerical solvers often reported optimal_inaccurate;
the rational certificate does not rely on that status or their residuals.

## Artifacts, reproduction, and decision

- `experiments/energy_bootstrap/pilot.py`: observable bounds and first branch test.
- `experiments/energy_bootstrap/certify.py`: six branches and rational rounding.
- `experiments/energy_bootstrap/check.py`: independent new-certificate verification.
- `reports/energy-bootstrap-001/`: numerical runs, logs, coefficients, certificate,
  source hashes, and `independent-check.json`.

Numerical commands use the cached offline uv environment with numpy, scipy,
cvxpy and networkx, with OPENBLAS/OMP/VECLIB thread counts set to one.
Both scripts enforce a 175-second alarm; reported computation times were
17.36 seconds and 4.94 seconds. Checks took approximately 0.51 and 0.88 seconds.

Recheck without numerical dependencies:

    python3 experiments/clebsch_bowl/check_coupled_certificate.py
    python3 experiments/energy_bootstrap/check.py

Decision: pursue disjoint-motif factorization with certified case analysis.
The next discriminating test is whether it strengthens a higher-level baseline,
not merely whether a finer N6 partition improves the last few digits. The known
upper bound was useful for exploration but was not the cause of the certified
improvement. No N9 test or published-bound improvement has been performed.
