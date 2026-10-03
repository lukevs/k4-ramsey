# Complete two-root N8 pilot

User authorized continuation on 2026-09-30. Local parent-only window
13:14–13:29 UTC, one single-thread numerical job at a time, <=175 seconds
per job. No installs, outreach, remote or paid work. Reserve time for audit.
Goal remains reaching and exceeding the published universal lower bound;
this pilot tests one missing portion of the hierarchy, not full N8 or N9.

H1: the entire two-root N8 flag matrices give a gain where selected scalar
and low-dimensional matrix constraints did not. Use root-exchange symmetry
for an exact block diagonalization, not a projection or graphon symmetry
assumption. Preserve N7 and unrooted N8 blocks and the objective band/cut.

H2: a memory-aware sparse formulation makes these full blocks tractable.
Measure coefficients before solving; no conventional dense N9 launch.

Checked reference 0.029260494838693384 remains unchanged until an exact
certificate passes an independent checker. Numerical improvements stay
labelled numerical. Source files: experiments/rooted_frontier/; immutable
outputs reports/rooted-full-001/. All predecessor artifacts remain intact.

## Completed results

Both complete 120x120 two-root matrices reduce exactly to 74+46 blocks.
Four sparse blocks occupy 34,963,208 bytes in memory. Independent C++
adjacency enumeration checked every integer coefficient on every N8 graph,
plus the zero cross-parity blocks. The basis is invertible. No full N8
hierarchy claim: four-root and six-root families remain absent.

The full solve hit its time limit (145.03 seconds overall). Its numerical
objective 0.02929400399 is NOT a bound: negative probabilities reach
-1.65e-5, scalar violation 1.42e-5, rooted eigenvalue -1.33e-6. Exact dual
rounding produced -0.082374, which is useless and not promoted or independently
certified. Do not report the unfinished primal value as an improvement.

Explicit complement isomorphisms reduce 12,346 graphs to 6,178 orbits,
including 10 self-complementary representatives. Every mapping was checked
on all 28 pairs. A quotient solver is prepared but NOT executed.
The linear current problem is invariant under complement; averaging preserves
PSD and the F-based scalar cut because F is complement invariant. This is
not an assumption that the optimizing graphon is colour balanced. It must
not be blindly applied to earlier nonlinear triple-factorization branches.

Next: solve_quotient.py control, then cut, with matched resources; quantify
convergence and attempt exact certification only on useful duals.
No new bound; checked reference 0.029260494838693384. All jobs finished.
