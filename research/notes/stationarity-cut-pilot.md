# Optimizer-only stationarity constraint pilot

User authorized testing lane C's exact seven-vertex constraint. One local
single-thread Sage job at a time, <=180 seconds per solve, initial 15-minute
implementation/solve/check window. No paid work, outreach or new agents.
Hypothesis S1: adding UF-B>=0 improves the existing N7 relaxation with the
same N6 blocks and C5-root block. Compare matched control and constrained
solves. U=3767361/125000000 is above the independently checked upper witness.
This is valid for limiting minimizers, not all graphons. Root reviewed C's
measure-tilt proof: orthogonal subset products and Cauchy--Schwarz establish
variance tending to zero along minimizing sequences, hence B<=UF in a limit.
Independent coefficient recount and exact dual verification required before
promoting any numerical improvement. No global record follows from improving
our weaker N7 baseline. Save primal vectors to measure constraint violations.
Status: preparing controlled solve; no bound improvement yet.

Control completed in 27.31s, numerical objective 0.028750924694048323.
Its returned moment objective is 0.028750924277178565; stationarity violation
B-UF=+0.0002792375613080375. This is a separated numerical point, not yet
proof that the optimum improves. All1044 cut coefficients independently
recounted with unordered intersecting four-set pairs; exact U checked above
incumbent fraction. Constrained solve launched next, identical blocks/settings.
A first launch failed on directory ownership before calculation; corrected.

User additionally authorized broader cross-field literature agent Kierkegaard,
01a0f088-f305-7fb3-add3-db2218ca2b54, separate up-to25min read-only research
window, no compute or further delegation. Owns broad-methods-literature note.

## Completed result

Constrained solve completed in11.06s: numerical bound0.028750924066431083,
versus control0.028750924694048323. Difference-6.28e-10 is numerical error,
not a worsening of the mathematical relaxation and not an improvement.
Returned constrained moment objective0.028750920305895256, cut
B-UF=-0.00003266038889200779 (strict slack); multiplier1.915e-8.
Solver reports success, relative primal infeasibility4.58e-11, dual3.82e-10.
The control point is excluded, but a different numerical near-optimal point
satisfies the cut. This is evidence of no gain here, not exact redundancy.
All1044 coefficients independently recounted, and the stored solver constraint
verified exactly to equal UF-B in matching graph order. No improved dual to
promote, hence no new exact bound claimed. All compute finished.

Decision: retain the valid cut as optional optimizer restriction, but do not
expect it alone to improve this N7 block family. Literature's edge-optimality
localizers are a distinct next candidate, not tested in this pilot. Existing
published lower frontier remains stronger than this small relaxation.
Artifacts and commands: reports/stationarity-cut-001/comparison.json.
