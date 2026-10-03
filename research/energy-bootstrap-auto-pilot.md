# Automated weakest-case refinement and convergence diagnostic

Active 2026-09-30, renewed 15-minute local window (06:14–06:29 UTC).
Prior checked bound: 0.029256668285624187. Same universal graphon problem;
no restrictions to Clebsch, regular, or finite-step constructions.
One numerical worker, one sequential exact-check path, no agents, paid work,
remote compute or installs. Each solve/check <=175s; campaign deadline enforced.

H-A1: best-first case subdivision spends solves where they improve the global
certificate. Parent certificates remain valid until both children are checked.
Reuse one parameterized CVXPY problem and Clarabel workspace. Record solver
reuse and timings; warm_start=True alone is not evidence that previous numerical
iterates are used by this solver.
H-A2: a fixed consistent triple profile, with all J_ij=p_i*p_j imposed exactly
as linear data, supplies an exploratory estimate of the moment model's floor.
A numerically feasible moment vector is NOT a graph construction, not a rigorous
upper bound on c4, and not an exact convergence certificate.

Convergence check is advisory only. Every promoted bound still requires rational
PSD and coefficient checks plus exhaustive coverage modulo colour complement.

## Diagnostic result

The fixed profile (1/8,3/8,3/8,1/8), with every J_ij=p_i*p_j imposed as
linear equalities, gave numerical objective 0.029285341513274027. The minimum
Gram eigenvalue was -1.05e-9, maximum mean residual 3.16e-10 and maximum joint
residual 8.14e-10; status optimal_inaccurate. Thus this is a near-feasible
moment-model point, NOT an exact primal certificate, construction, or rigorous
ceiling. It suggests that refinement alone has limited headroom relative to
the published frontier. No stopping decision treats it as exact.

Local inspection of CVXPY's installed Clarabel adapter confirms warm_start=True
can reuse and update a cached solver object; it can fall back to reconstruction
if update fails. Our implementation reuses the same DPP problem and requests
that cache path. We do not claim reuse of previous numerical iterates or a
measured speedup without timings.

## Completed automatic run

Final checked bound: 50337414480901/1720320000000000 = 0.02926049483869338.
Six automatic splits and twelve branch solves completed, with previous parent
certificates retained when rounding lost a small numerical gain. Worker exited
and was reaped normally. See reports/energy-bootstrap-auto-001/combined-23-check.json and summary.json.
The fixed-profile diagnostic is still only numerical. A second prepared profile
diagnostic was not run because the user redirected the next experiment to N8.
No broad solver-speedup claim: branch runtimes remain roughly 36–51 seconds;
case differences confound direct timing comparisons.
