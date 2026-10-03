# Rooted frontier pilot

User authorized on 2026-09-30. Local parent-only pilot 12:45–13:00 UTC,
one single-thread numerical job at a time, each <=175 seconds. No installs,
outreach, paid or remote computation. Existing checked lower reference
0.029260494838693384; no new bound until independently certified.

Goal: strengthen the hierarchy toward the published N9 baseline and test
whether independence adds strength there. N9 recovery previously found no
solver bundle; dense N9 is outside local memory. Do not repeat that search.

H1: quantify the distance of the previous fixed N7 profile to an N8 extension
satisfying all four-pattern products. A robust positive residual would guide
further work, not prove a universal lower bound or a genuine obstruction for
the slightly inaccurate source profile.

H2: missing two-root N8 flag squares exclude surviving low-valued N8 points.
Generate all five-vertex flags with two fixed roots, screen their matrices,
then add violated square inequalities and reoptimize. Positive cuts are
universally valid, but numerical solver output alone is not a certificate.
Verify coefficients with a separate direct enumeration before interpreting.

Decision gates: distinguish single-point rejection from objective gain;
retain old constraints and matched controls; report numerical residuals;
do not label selective N8 as full N8 or as published N9 reproduction.

## Results before final projected-matrix solve

The fixed-profile all-four-product extension distance is 8.34e-9 (measured
maximum residual 8.69e-9). This is a numerical near-extension, not a robust
obstruction; the input itself is approximate. Retire the old tolerance-dependent
infeasibility as a lead unless a well-conditioned separation can be found.

Generated all 120 five-vertex flags for each of the two labelled two-root
types. The original N8 point has minimum matrix eigenvalue -9.58e-5 in each
type. Two rounds of 48 quantized square cuts were independently recounted
on all 12,346 graphs, including every integer coefficient. The directions
are rational; their validity follows from averaged flag squares. This is
not the full N8 hierarchy.

Matched solves: prior control 0.0292566682668; first rooted round
0.0292566682763 (optimal), second 0.0292566682200 (optimal_inaccurate).
These differences are numerical noise, not improvement. Worst remaining
rooted eigenvalue after round one -3.10e-5: the solver moved to another
unrealizable point. Both retain the previous band and independence cut.

Final test combines eight directions from each round into a 16-dimensional
subspace for each root type, imposing the complete projected PSD matrices.
This tests cross-relations between directions, not only individual squares.

## N9 recovery decision

Reviewed the existing recovery record (research/lower-frontier-A.md), including
all prior repository/history inspections. No new N9 solver bundle was located
in this pilot; no fresh web search or correspondence was performed. A conventional
dense colour-quotient Schur matrix alone costs 140.56 GiB. This is a limitation
of that implementation, not a mathematical barrier or a universal memory lower
bound. We have NOT reproduced the published N9 baseline or tested independence
on it. Selective N8 experiments cannot substitute for that milestone.

Next priority: complete more rooted N8 blocks or implement a memory-aware N9
formulation. Finite scalar-cut sampling has not raised the present objective.
No restriction to Clebsch, regularity, or balanced colours has been imposed.

## Completed

Projected solve: 0.0292566665415, optimal_inaccurate, 132.96 seconds.
Minimum projected eigenvalue 1.25e-6; worst scalar violation 1.74e-9 and
unrooted eigenvalue -3.44e-10. No measured gain; no exact feasibility or
relaxation ceiling claimed. All coefficients of both 16x16 blocks were
independently recounted via 272 polarization squares on all 12,346 graphs.

Strongest checked reference remains 0.029260494838693384. No promotion.
All jobs completed and reaped. Reports: reports/rooted-frontier-001/summary.json,
all-cuts-check.json, projection-check.json.
