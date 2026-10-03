# Independent discrete structure search — completed

No incumbent improvement or promotion. All owned processes exited and were
reaped; unrestricted process-table inspection confirmed none remain. Search
stopped at05:33:29 UTC, well before05:37:15 search cutoff; independent checks
and handoff completed within the15-minute window launched05:24:15 UTC.
Only the three assigned paths were written. Parent-owned files untouched.

## Result and decision

Two representation families were tested, both with1024 equal normalized classes,
binary diagonal probabilities, and ALL ordered quadruples including repeats.
H-D1 frees individual Cayley generators of F2^10 (translation restricted,
not shell restricted); H-D2 frees all symmetric binary matrix entries
(no translation or Clebsch/P-H/12-block template restriction). H-D2 was the
materially different hypothesis after H-D1 independent starts failed.

| Matched screen | Seeds / proposals per branch | Downhill densities | Annealing densities |
|---|---|---|---|
| F2^10 generators |1101,1102,1103 /8192 |.03138016537, .03138792049, .03141638543 |.03141695540, .03142252099, .03143044468 |
| Unrestricted matrices |1301,1302 /200000 |.03140490860, .03140505699 |.03140820389, .03140838867 |

Starts, proposed coordinates, proposal counts, and random uniform streams are
matched within pairs; CPU time is measured but not exactly equal. Annealing
uses an exponentially decreasing temperature with final/initial ratio1e-4.
It accepted1800–1837 uphill moves in Cayley trials and26568–26678 in the
long matrix trials. Downhill won all five principal comparisons. These are
bounded negatives for these schedules, not a claim that barrier crossing is
ineffective in general. No independent start beat1/32 or the incumbent.
The earlier short20000-proposal matrix pair is retained as a pilot, not a
third independent comparison.

## Recovery and strongest retained artifact

Historical Franek–Rödl control (red Hamming distances0,1,3,4,7,8,10, including
red diagonal) reproduced exactly32765943/1073741824=.030515662394464016.
It is a recovery/control input ONLY, not an independent start. Eight generator
flips raised its rooted count to32833335.1000 random proposals incompletely
recovered it;8192 downhill proposals reached32759495/1073741824=
.030509657226502895. Recovery therefore passed before interpreting independent
negative searches. The paired annealing run retained the damaged start;
its high-temperature exploration lost the useful basin within this schedule.

Unrestricted downhill edits starting from the historical control gave the
strongest retained artifact:
`reports/assumption-discrete_basins-001/matrix-control-s1401-k20000-downhill.json`
with exact33545236716/1099511627776=0.03050921506292070, independently
recounted by a sorted-clique/equality-partition checker. This improves its own
historical control, but is substantially worse than incumbent
.030138887566497220. Parent audit remains required for any use/promotion.
No record, novelty, optimum, or new bound is claimed.

After discrete search, scalar continuous polish W=.5+t(A-.5),0<=t<=1 on the
three best independent Cayley outputs returned1/32 within floating error;
the recovered control retained t=1. A reported t≈.00032 and apparent2.8e-16
gain for one random start is numerical roundoff, not improvement. This is a
one-dimensional diagnostic, not full continuous matrix optimization.

## Checks, receipts, limitations, next test

- 24 tiny Cayley fixtures versus literal ordered tuples;700 arbitrary-matrix
incremental move tests versus literal ordered tuples (including diagonal edits).
- 30 independent sorted-clique checker fixtures at n1–6 versus literal tuples.
- All10 saved Cayley artifacts and7 full matrix artifacts independently exactly
recounted; hashes bound in audit-final.json and audit-matrix.json. Scalar
polish independently agrees with a trace-of-cube contraction numerically.
- Contract/source hashes, per-search command/PID/start/end/code hashes, complete
matrices/generating sets, compiler identity, and final manifest are retained.
First manual controls have self-measured times and transcript commands but
lack external start/end timestamps; handoff.json explicitly records this gap.
- C++ jobs were single-threaded with175s hard alarms; subprocess drivers used
170s communicate deadlines. NumPy polish used the authorized offline cached
environment with BLAS/OpenMP/VECLIB thread counts1. No installs or descendants
were launched. Runs/checkers completed normally, with no timed-out searches.

Decision: retire these particular annealing schedules; preserve the validated
arbitrary-edge delta and independent checker for a future explicitly budgeted
search. A next discriminating test would be coordinated row/vertex rebuilds
from independently developed structured seeds, matched against edge descent;
current200000 proposals cover only a fraction of524800 coordinates and cannot
exclude deeper useful unrestricted basins. Do not repeat random continuous
descent or interpret this result as a symmetry necessity theorem.

## Checkpoint history (approximate labels; receipts are authoritative)

# Independent discrete structure search

Initial checkpoint: launched 2026-09-30; exact UTC launch recorded in tool receipt. Status: reading protocol and prior evidence; no compute job running. Scope: discrete binary block search, matched downhill/barrier crossing, literal oracle and nonconstant recovery control. Budget 15 minutes from launch; final 2 minutes reserved for independent validation and process cleanup. Own paths only; no promotions or shared evaluator edits.

05:26 UTC checkpoint: read required prior evidence and unrestricted checker/search.
H-D1: unrestricted generating sets on F2^10 and cyclic Z257, binary diagonals
included; matched downhill/annealing from identical starts and proposal stream.
This is translation symmetry restricted, not unrestricted matrix search. F2^10
can represent historical Franek–Rödl control (distance 0,1,3,4,7,8,10 red),
known exact 32765943/1073741824 <1/32. It does not impose Hamming shells on
search variables. No Clebsch/P-H/12-block template. Planned damaged-control
recovery precedes independent random starts. No active job after compilation.
Deadline 05:39:15 UTC; stop search by05:37:15 UTC. Frozen literal tiny oracle
compares ordered quadruples including repeats against rooted bitset count.

05:28 UTC checkpoint: literal F2^2 and Z5 counts passed (12 random fixtures
each, including diagonal bits). Historical F2^10 control exactly reproduced.
Eight-generator damage raised rooted count32765943 ->32833335. At1000 random
proposals recovery incomplete32785015, diagnosed insufficient coverage;8192
proposals reached32759495 (better than known control), so nonconstant recovery
passes. Recovery annealing currently running PID78328, bounded175s; exact
running command/PID saved in reports/assumption-discrete_basins-001/running.json.
No negative claim from the short incomplete-recovery run. Checkpoint clock is
approximate; immutable receipt timestamps will be authoritative.

05:30 UTC checkpoint: recovery annealing completed/reaped (3681 accepted,
1786 uphill), retained damaged start32833335; downhill best32759495. Independent
equality-partition/triangle checker agrees exactly on all four control artifacts.
Matched F2^10 independent starts running sequentially (seeds1101–1103,
8192 proposals per branch, identical proposal streams). Current PID/command
is updated per launch in running.json. Preparing materially different H-D2:
unrestricted1024x1024 binary matrices, including diagonal edits; no translation
symmetry or template restriction. Exact incremental deltas will be checked
against full ordered count before use. No shared files modified.

05:30:18 UTC actual checkpoint: all six F2 runs finished and reaped. Downhill
rooted counts33694196,33702523,33733087; paired annealing33733699,33739675,
33748183, all denominator1073741824, all above1/32. Annealing accepted
1800–1837 uphill moves per independent trial but lost all three comparisons.
This batch failed to locate a useful independent basin; H-D2 now running
PID78745: unrestricted1024 binary block matrix, seed1301,20000 proposals,
downhill; full symmetry release is materially different from temperatures
or move-arity variants. Tiny incremental tests passed600 moves across n5/n9,
including diagonal flips, against full ordered bitset recount. Independent
literal/sorted-partition checker still required before final claims.

05:32 UTC checkpoint: unrestricted seed1301 short paired20000-proposal screen
completed and reaped. Downhill34616062722 versus anneal34623622592, common
denominator1024^4, both above1/32. Longer matched200000-proposal comparison
underway, downhill PID78860. Candidate reports contain full binary matrices;
no weight/diagonal terms omitted. Sorted distinct-clique plus equality-partition
independent checker prepared, with literal tiny fixture driver. No promotion.

05:33:29 UTC checkpoint: all search jobs finished and reaped; no search PID.
Second unrestricted200000-proposal pair: downhill34530225336 versus anneal
34533888552 over1024^4; downhill again wins. Known historical matrix control
preserved/improved to33545236716/1024^4 by20000 downhill edits. Search stopped
early to reserve ample independent checking/handoff time. Sequential checks
now run: literal ordered-delta tests, Cayley independent triangle census,
unrestricted sorted-clique/equality-partition census, then scalar t-polish
W=.5+t(A-.5),0<=t<=1 on four retained Cayley witnesses. This polish is explicitly
one-dimensional, not full matrix continuous optimization. No active search;
verification command session27613, individual child PID not yet sampled.

Final clarification: the early recovery coverage diagnosis was a hypothesis,
not a logged coordinate-coverage measurement; the longer successful recovery
is the decisive control. Earlier commentary rounded one matrix comparison
inaccurately; the exact fractions and final table above are authoritative.
