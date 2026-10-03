# Lower-bound methods beyond problem-specific literature

User direction: search for transferable mathematics, not primarily K4 papers.
This is a research shortlist, not a new bound. No new distributed work or solver
installation was launched for this review.

## 1. Alternative nonnegativity certificates

Moustrou, Riener, Theobald and Verdure, [Symmetric SAGE and SONC forms,
exactness and quantitative gaps](https://arxiv.org/abs/2312.10500), preprint
December 2023, online August 2024, journal issue 2025. These certificates use
the arithmetic–geometric mean inequality; the paper identifies symmetric
cases where they characterize nonnegativity and others with gaps.

[Duality of sum of nonnegative circuit polynomials and optimal SONC
bounds](https://www.sciencedirect.com/science/article/pii/S0747717122000359)
explains that SONC and SOS cones do not contain one another. This makes SONC
a complementary proof system, not a uniformly stronger replacement.

Averkov, Peters and Sager, [Unifying view on sparse convex relaxations in
polynomial optimization](https://ojmo.centre-mersenne.org/articles/10.5802/ojmo.50/),
published June 4, 2026, provides a common framework using monomial patterns
for polyhedral, SDP, SAGE, SONC and term-sparse SOS relaxations.

Proposed transfer: build a small hybrid certificate using polynomial relations
among universal motif statistics. First test separation of a saved low-valued
pseudo-moment witness. Failure to separate means no reason to scale that version.
The formulation and separation remain unimplemented. Certifying only the B192
parameter polynomial would prove a restricted-family floor, not a universal bound.

## 2. Causal compatibility and inflation

Gitton and Renner, [The Elegant Joint Measurement is Non-Classical in the
Triangle Network](https://arxiv.org/abs/2510.15143), October 2025, is a recent
computer-assisted application of inflation to rule out latent-source models.
[Symmetric observations without symmetric causal explanations](https://arxiv.org/html/2502.14950v2)
also distinguishes identical-source/response assumptions from observed symmetry.

Our proposed mapping: graphon samples have independent vertex sources U_i,
independent edge coins Z_ij, and a common symmetric response
A_ij = 1{Z_ij <= W(U_i,U_j)}. Copying sources and enforcing agreement of
overlapping observations might expose impossible local statistics.

First gate: derive an explicit source-copy constraint and show that it is not
already implied by the current finite flag relaxation. Independence introduces
products of probabilities: do not substitute products of pseudo-expectations
without justification. Fixed-profile infeasibility alone is not a universal
lower bound. This was identified in the earlier broad review and remains untested.

## 3. Ground-state bootstrap and bounds on observables

Paul and Refael, [Bootstrapping ground state properties of classical frustrated
magnets](https://arxiv.org/html/2605.06784v1), May 7, 2026, uses finite moment
constraints to bound energy and correlations. Its section II.4 conditions on
a known feasible energy upper bound to constrain ground-state observables.
This is still moment/SOS mathematics, not a replacement for it.

Proposed transfer: impose F <= our checked upper bound, then bound auxiliary
statistics of every potentially optimal graphon. Use those ranges to select
additional moments or divide the feasible region into rigorously bounded cases.
Adding F <= U alone cannot lift an existing lower optimizer with F < U.
The benefit must come from additional constraints or certified case analysis.
Lattice locality and translation invariance must not be imported into our
unrestricted graph problem; use only valid vertex-exchangeable constraints.

This is the most direct practical next pilot. Alternative proof cones are the
more distinct mathematical direction; causal inflation is the higher-risk
compatibility direction. None currently implies a better Ramsey bound.

## Cheap screen performed during this review

`experiments/lower_bound_refresh/screen.py` screened four saved N6 moment vectors;
`reports/lower-bound-refresh-001/screen.json` records coefficients and results.
The odd-path inequality used three disjoint edges on its right side, avoiding
an unjustified cube of pseudo-edge density. Its slacks were about 1.6e-9 to
1.6e-8, with no observed violation beyond numerical uncertainty.
An averaged complement-row insertion condition had slack about 0.01010.
It is a minimizer-only proposed constraint, not an inequality for every graphon.
No solve or independent coefficient audit was performed. Neither screen supplies
a separating witness, a redundancy theorem, or a lower-bound improvement.

Earlier low-order stationarity and particular compressed-marginal tests failed;
they should not be advertised as fresh untested directions. Any next experiment
must first exhibit additional constraint strength, then produce a checked dual
certificate before being described as a rigorous bound.
