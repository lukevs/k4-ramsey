# Selective N8 extension: independence of two four-vertex patterns

Authorized by user's 'ok try it' on 2026-09-30. Local 15-minute pilot window
06:24–06:39 UTC. No agents, dependency installs, outreach, remote or paid work.
Existing Sage container may enumerate graphs; numerical solves remain sequential
with the active automatic N7 worker. Individual jobs <=175 seconds, one BLAS thread.

Preserve the full N7 constraints via one shared deletion marginal of a nonnegative
N8 induced distribution. Add the 11x11 matrix of disjoint four-vertex pattern
probabilities, and test exact factorization at fixed-profile diagnostics before
attempting a larger globally partitioned certificate. This is a selective N8
extension, not the full N8 flag hierarchy or the published N9 baseline.

Cheap gates: can the low-valued N7 diagnostic extend to N8 at all? Can a low-valued
N8 point satisfy J44=p4*p4? A fixed-profile solve or failed extension is not a
universal bound. Compare matched controls, inspect residuals, and retain exact
certificate requirements before any global promotion.

## Status after interrupted turn

N8 representatives and coefficients generated. The N7 fixed-profile diagnostic
has a nonnegative N8 extension (HiGHS residual 1.12e-15); bare extension
positivity does not exclude that point. This is a numerical check only.

The N8 matched control completed in 54.71 seconds, status optimal, objective
0.0292566682836: it merely recovers the imposed known lower endpoint. Its
objective variance z-F^2 is 0.0001883397023, much larger than the proposed
secant allows in the narrow interval. The control therefore exposes a useful
constraint violation, but excluding a point does not prove the optimum improves.

The interrupted turn had not launched the cut solve. It was launched on resume
at approximately 06:36:30 UTC, same matrices and settings, one extra scalar cut.

The particularly direct new scalar uses the probability z that TWO disjoint
four-vertex sets are each monochromatic (either colour). True graphons have
z=F^2, so on L<=F<=U the inequality (L+U)F-z-LU>=0 holds.
L=57520950383/1966080000000 is a previously checked lower bound, and
U=30139/1000000 is a convenient threshold. A bound B<=U proved on this band
extends globally: F>U already implies F>=B. This argument does not need to
assume an optimizing graphon has a prescribed profile.

## Completed result

The objective-independence cut gave numerical value 0.0292566682668, versus
control 0.0292566682836. The difference -1.68e-11 is solver error, not a gain
or a worsening of the exact relaxation. Status optimal in both cases; solve
times 54.71 and 93.29 seconds. The cut reduced z-F^2 from 0.00018834 to
3.73e-12, yet another low-valued point remained feasible numerically. This is
a measured failure of this particular added inequality, not a redundancy theorem.

The stronger all-pairs extension test is inconclusive. At default tolerances
HiGHS reported success, but explicit checking found residual 4.34e-6 and a
negative probability -4.94e-7. These invalidate interpreting that output as a
feasible witness. At 1e-9 feasibility tolerances, the solver reported infeasible.
The supplied N7 point itself has small PSD/equality errors, so this does not
establish a robust new obstruction. A future test needs distance-to-feasibility
or a jointly reoptimized profile and an independent separation certificate.
Neither LP result is an exact lower bound or an exact ceiling certificate.

The late tolerance check finished just after the nominal window; no further
compute was launched. All jobs are reaped. The strongest checked local result
remains the automatic N7 bound 0.029260494838693384, below the published
frontier near 0.0296. No N8 bound was promoted.

Decision: do not keep refining this scalar F-squared inequality alone. The
next meaningful work is either a robust joint four-pattern test or selected
rooted N8 constraints, alongside recovery of the stronger published baseline.
A point-specific tolerance-dependent rejection is not evidence that the new
program will improve its optimum.
