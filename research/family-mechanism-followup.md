# UNDERSTAND joint parent/amplitude pilot

Contract: launch 2026-09-30 05:05:04 UTC; stop by 05:20:04 UTC.
One local single-thread process at a time; each computational job has a hard
alarm of at most 175 seconds. No descendants, remote work, commits, promotion,
incumbent overwrite, or shared RESUME edits.

H001: moving parent probabilities on amplitude-bound edges can unlock useful
joint descent. Test independent two-variable parent-edge/amplitude-edge patches
of the saved first sign-split layer; compare parent-only and amplitude-only
controls on identical edges. These are restricted directions of the current
family, not optimization of the complete depth-two incumbent.

Implementation underway: compute the full lifted objective difference by
partitioning ordered tuples by how many indices lie in the four changed
classes. This includes repeated indices and diagonals. Validate against tiny
direct ordered counts and finite-difference gradients before real screens.
05:12 UTC checkpoint: local_patch.py and run.py now exist in the shared assigned
directory. First tiny job exited immediately: repository .venv lacks NumPy.
Checking the existing system Python; no dependency installation requested.
No successful numerical tests yet. No running process. Original deadline holds.
Incumbent remains .030138887566497220.

05:13 UTC: tiny direct ordered counts passed for 6- and 8-class lifts with
nonuniform weights and nonzero diagonals. Objective errors <=1.11e-16;
analytic gradient finite-difference error <=1.66e-12. Evidence: tiny.json.
Real matched edge screen launched under a 170-second hard alarm, single thread.

05:16 UTC: all 40 sampled edge screens completed in 4.80 seconds. Joint moves
improved all 40 numerically; parent-only improved 12; amplitude-only improved
none at threshold 1e-17. Best edge (653,927) passed an independent integer
relative recount on the full 1920-class lift. Joint delta -4.60466409479e-13
(see exact-check.json for exact value), parent-only -2.42449502742e-13,
amplitude-only zero. The candidate is worse than the depth-two incumbent.
No process running at this checkpoint; preparing decomposition and handoff.

## Completed result: a small checked joint gain

H001 is supported for a restricted direction, not for a substantial improvement.
Forty seeded single-edge patches were optimized independently from the SAME
saved first-layer matrix, with uniform class weights. Parent-only and
amplitude-only controls had identical edges and baseline; scalar minimization
is compared with a two-variable box optimizer. This is not a comparison of
algorithm efficiency or an exhaustive optimum. None of the 40 patches were
combined. Fifteen joint solutions increase amplitude magnitude; 25 shrink it.
Thus not every observed joint gain is explained by opening amplitude headroom.

Best edge: (653,927), denominator 65536. The initial parent numerator is 58565
and amplitude numerator -6971. The independently checked rational joint patch
sets these to 58008 and -7528. It preserves P-A=1 while reducing P+A from
51594/65536 to 50480/65536, so both lifted probabilities stay in [0,1].
All untouched probabilities and weights are inherited unchanged.

| Matched control | Exact-counted relative change |
|---|---:|
| Parent only (parent numerator 58160, amplitude -6971) | -2.4244950274220653e-13 |
| Amplitude only (unchanged) | 0 |
| Joint (parent 58008, amplitude -7528) | -4.604664094789801e-13 |

Joint exact delta:
`-7564888343878129399514999/16428751778957853043397273541672960000`.
Relative to the saved exact baseline, the conditional density is
0.030138895263163185, worse than incumbent 0.030138887566497220.
No candidate was promoted and no full incumbent recount was attempted.
The first-layer reference is 0.03013889526362365; comparing a first-layer gain
directly to the stronger second-layer incumbent would be misleading.

At this edge the initial numerical derivatives are dF/dP=7.8486398363e-11,
dF/dA=2.9781152529e-11. The feasible direction (dP,dA)=(-1,-1) has negative
derivative -1.08267550892e-10, and the rational patch above demonstrates a
finite checked gain. Amplitude-only motion in its descending direction is
blocked; the parent move creates space for the more negative amplitude.

Floating decomposition (the total alone has an independent exact recount):
the joint patch changes cubic by -3.4032259534e-13 and quartic by
+1.2526591092e-13. Its refinement gain is -2.1505668442e-13; the remaining
parent gain is -2.4540972506e-13, inferred by subtraction. Parent-only improves
the base more (-2.6948420312e-13) but worsens refinement (+2.7034700377e-14).
Thus the successful joint patch trades a little parent gain for a larger cubic
benefit; it does not strengthen the negative quartic at this edge.

## Why the quartic need not be nonnegative

For arbitrary class weights mu and symmetric signed A, the split quartic is

    3 sum_{i,j,k,l} mu_i mu_j mu_k mu_l A_ij A_jk A_kl A_li
      * (W_ik W_jl + (1-W_ik)(1-W_jl)).

All four indices range independently, including repetitions; graphon diagonals
are ordinary probabilities. Without the chord-dependent factor, this is
3 tr(S^4), S=diag(sqrt(mu)) A diag(sqrt(mu)), which is nonnegative because S
is real symmetric. Individual signed cycle products may still be negative.
The nonnegative chord factors depend on both opposite pairs and reweight those
signed cycle products; they cannot in general be removed or treated as a
constant. Therefore nonnegativity of tr(S^4) does not imply nonnegativity of
the weighted quartic. The saved first-layer negative quartic is reproduced.

## Validation, failures, and scope

The search partitions ordered tuples by the number of indices inside the four
changed classes. It includes all repetitions; its value and analytic gradient
passed independent tiny direct ordered counts with nonuniform weights and
nonzero diagonals (objective error <=1.11e-16; gradient error <=1.66e-12).
Only off-diagonal internal patch changes are supported by this implementation.

The separate checker telescopes the four changed lifted edges and groups tuples
by multiplicities of the TWO edge endpoints. It was checked against tiny
direct counts; its Python-integer variant passes exact 2-,3-,5-class fixtures
and recounts all three real rational controls exactly, with no integer overflow.
Its normalization is 1920^4 * 65536^6. This independently checks the relative
change, conditional on the saved baseline; it is not a fresh full absolute count
or a formal theorem. The floating real check agrees within 1.85e-23.

Failures are retained: missing NumPy in repo/system Python; floating checker
tiny tolerance 1e-17 was too strict (errors 2.58e-17); and the exact checker's
2-class fixture exposed an empty-index dtype bug, fixed by dtype=int. Apple
longdouble equals float64 here, as recorded in check.json, so no extra precision
is claimed. All corrected tests passed before the exact result was accepted.

All jobs used one numerical thread, self-enforced SIGALRM<=170s, no spawned
workers, and completed/reaped before the 05:20 UTC deadline. Real screen 4.80s,
floating check 0.35s, exact check 0.97s, decomposition 0.94s (script timings).
No descendants, network/paid compute, outreach, commits, or incumbent writes.
Artifacts are in the shared workspace, no fork. Source/input/output SHA256
manifest and source snapshots accompany the evidence.

Next discriminating test: apply sparse joint probability/amplitude blocks to
the full depth-two family, propagating the first-layer change through the second
layer and enforcing every resulting box. Compare matched parent-only and
amplitude-only controls, then independently recount the combined move. Do not
sum these independent single-edge gains as if they were additive. A fresh
authorized budget is required after this pilot; no work remains running.
