# Lane A: KPS N9 recovery (2026-09-30)

Contract: recover actual two-colour K4 N9 input/output or perform a bounded,
symmetry-aware cost/reproduction pilot. Deadline 04:16 UTC. One local
single-thread compute job at a time, each <=180 seconds; no remote compute,
outreach, source installation changes, commits or subagents.

H-A1 (artifact recovery): the published repository/release history contains
the K4 N9 instance. Initial inspection: current main tree has only certificates
for Theorems 2.3/2.4, Goodman, Cummings; three releases have no extra assets.
Continue historical tree inspection. Not locating an artifact does not prove
it was never made public elsewhere.

H-A2 (bounded reconstruction): the authors' public symmetry-aware verifier
utilities can generate real N9 coefficient rows for a selected type without
enumerating N9. Test one-root/five-vertex flags, complement symmetry, and
selected nine-vertex graphs. This is a coefficient pilot, not an N9 solve.

H-A3 (resource census): Burnside counting gives exact dimensions of the
colour-quotiented moment set without enumerating all N9 graphs. Compare
small counts to actual generators, then quantify dense Schur storage.

## Interim concrete result (04:06 UTC)

Recovered and ran the authors' **unmodified** `utilities.py` and importable
`verify.py` from commit `f9c3b95cede94bbb9736fe1d71a2a7b2d2390e8a`.
For the actual N9 one-root block: 90 order-five flags, 46 flag orbits,
2,071 symmetric pair orbits. Generated 12 nine-vertex rows in 2.84 seconds
after imports, peak RSS 324,776 KiB; single rows 0.056–0.256 s. All rows
have correct all-ones normalization and agree with complement rows.

**Independent exact check:** `check_pilot.py` imports no upstream code or Sage.
It enumerates all 630 ordered root/split choices per nine-vertex graph,
canonicalizes the four free vertices by all 24 permutations, and agrees with
every exported nonzero coefficient in rational arithmetic. Objective counts
were independently recounted over all 126 four-subsets. This certifies these
selected coefficient rows, not a lower bound or PSD solver result.

**Exact resource census:** Burnside's lemma, summed over permutation cycle
types, gives 274,668 unlabeled N9 graphs, 36 self-complementary classes and
137,352 classes modulo global colour exchange. No N9 graph enumeration.
A dense float64 Schur matrix with one equality per class requires
150,924,575,232 bytes (about 140.56 GiB) alone; packed symmetric storage
75,462,837,024 bytes. This is conditional on the usual dense Schur solver
layout, not a universal lower bound for every algorithm.

Artifact search now includes all 21 public commits' changed-file inventories,
the sole public branch, and all three releases (no attached release assets).
Historical extra files were LDL decompositions for the same other problems.
No K4 N9 input, numerical solution, primal moments or solver log was found.

## Completed additional tests

The two three-root types each have 816 order-six flags. Their root symmetry
groups have orders 2 and 6; the public code yields respectively 172,648 and
61,636 symmetric pair orbits. Four actual N9 sample rows took 0.191–0.257 s
each, with 511–802 nonzero orbit coefficients across both types. Complement
rows agreed. Total run 15.946 s after imports, peak RSS 576,444 KiB. These
three-root rows have **same-code checks only**, unlike the independently
checked one-root rows.

An independent character calculation (`symmetry_sizes.py`) confirms PSD
multiplicity-space sizes 484+332 for the path type, and 220+68+264 for the
triangle type (the last representation has degree two). Their symmetric
parameter totals equal the measured pair-orbit counts exactly. The one-root
block splits into 46+44. No change-of-basis matrices or solver input were
constructed, so these dimensions are not a block-diagonalized solve.

An independent nauty/Sage enumeration confirms both ordinary and
colour-quotiented counts at N=5,6,7,8. N8: 12,346 ordinary / 6,178 quotient,
1.264 s. Only the **0–8 edge sector** was enumerated at N9: 601 ordinary
graphs in 0.0653 s. This sector is deliberately biased and is not an N9
enumeration or representative timing benchmark. Peak RSS 236,208 KiB.
The exact N9 count comes from Burnside, not this sector.

First enumeration run crashed (exit 139) inside the installed Bliss module;
the traceback and original script are retained. Selecting
`canonical_label(algorithm='sage')` fixed the pilot. No installation was
changed. The authors' coefficient utilities explicitly use the Sage backend
and succeeded unchanged. The failed homepage `master` tree lookup was a 404;
the actual `gh-pages` tree was subsequently retrieved.

## N9 size and what was actually measured

| Type order | Number of types modulo colour | Flag order | Flags per fixed labelled type |
|---|---:|---:|---:|
| 1 | 1 | 5 | 90 |
| 3 | 2 | 6 | 816 |
| 5 | 18 | 7 | 1,056 |
| 7 | 522 | 8 | 128 |

These are exact counts before each type's automorphism block reduction.
They describe the standard odd-parity full level-nine hierarchy, not a
recovered manifest proving which blocks KPS actually selected.

Burnside calculation: for each permutation cycle type on vertices, count
edge orbits. Ordinary fixed colourings contribute 2^(number of edge orbits).
For permutation composed with colour exchange, the contribution is zero
unless every edge orbit has even length, and otherwise the same power of
two. Weight by the conjugacy-class sizes, divide by n!, and average the
ordinary and colour-twisted counts. The twisted average is the number of
self-complementary isomorphism classes. Fixed-root flag counts use only
permutations of unlabelled vertices and exclude edges internal to the type.
All arithmetic in the census is integer arithmetic.

For a dense Schur formulation, colour symmetry reduces N9 storage by nearly
fourfold versus 274,668 rows, but leaves 140.56 GiB for one square float64
matrix, or 70.28 GiB packed. Factorizations, coefficients, and PSD blocks are
additional. This is a design-specific memory calculation, not a measured
CSDP peak and not an impossibility theorem for sparse or matrix-free methods.
The corresponding N8 dense matrix is 291.20 MiB. No full SDP was launched.

For orientation only, multiplying the measured per-row medians by 137,352
gives roughly 2.3 CPU-hours for the one-root coefficient rows and 7.8 for
both three-root blocks, with this Python implementation. The small chosen
sample does not justify extrapolating the remaining types or full solve time.
Enumeration itself was cheap in the tested sectors; it is not the measured
reason to reject a naive dense CSDP run.

## Missing artifacts and next decision

**H-A1: unsupported in the inspected public sources.** The current tree,
all 21 visible commits' changed-file inventories, sole branch, three releases,
author public repository list, personal-site tree, and empty Playground
repository did not supply K4 N9 input/output. Historical removed files were
decompositions for the other certificate families. This does not establish
global non-publication. No outreach occurred.

**H-A2/H-A3: supported within their stated scope.** Real N9 coefficient rows
are reproducible from public KPS utilities; exact counts and small symmetry
dimensions are obtainable cheaply. We did not reproduce 0.02961, obtain an
N9 feasible solution, or improve a universal lower bound.

The **smallest missing artifact for the root's inequality-diagnosis task** is
the numerical optimal N9 moment vector, keyed by canonical graph6 (or the
authors' colouring strings), with normalization and the solver residuals.
There are only 137,352 entries in the natural colour quotient: 1,098,816
bytes for raw float64 values, plus the ordering/keys. Its interpretation as
orbit probability mass versus density per representative must be specified.
With that vector, universal candidate inequalities can be screened without
rebuilding the full SDP. A negative value would remain numerical evidence.

For **reproducing the reported optimization**, also missing is the exact
block/flag/basis manifest and the CSDP input plus numerical solution (or an
equivalent generator and its configuration). For **proving a bound**, one
needs rational PSD matrices and exact verification of every coefficient
inequality; the pilot does not supply those. The standard asymptotic flag
square implication must also be stated, with no regularity or Clebsch
assumptions. There is no claimed new mathematical lemma beyond the standard
Burnside and representation calculations used for resource counting.

Decision: **pursue recovery of the keyed N9 vector/solver bundle; revise any
local rebuild toward streamed sparse coefficients and a memory-aware solver.
Do not launch conventional full dense N9 CSDP on this machine.** Before
larger reconstruction, the smallest useful computational follow-up is a
bounded five-root coefficient and sparsity profile, with an exact independent
normalization check. It would measure the currently unprofiled block family;
it would not by itself reproduce N9.

## Sources and artifacts

- [KPS section 7](https://arxiv.org/html/2312.08049v1#S7): reports CSDP's
  approximate 0.02961 and explicitly states that it was not rationalized.
- [Pinned public repository](https://github.com/FordUniver/kps_trianglemult/tree/f9c3b95cede94bbb9736fe1d71a2a7b2d2390e8a):
  actual source used, certificate scope, and numerical/exact verification code.
- [Release history](https://github.com/FordUniver/kps_trianglemult/releases):
  inspected through the GitHub API, no extra assets.
- Prior context: `sage-fork-installation.md`,
  `global-lower-bound-transfer-audit.md`, `toolbox-clebsch-extension.md`, and
  `recent-literature-update-2026-09-29.md`; retired low-order additions were
  not rerun.
- `../experiments/lower_frontier_A/`: all pilot/checker/census source.
- `../reports/lower-frontier-A-recovery/`: pinned upstream files, API source
  inventories, row artifacts, exact checker output, timing logs and crash log.
  `manifest.json` records SHA256 for artifacts and scripts.

Environment: local container `flag-sage`, Linux aarch64, SageMath 10.9
(2026-05-04); installed fork revision from installation record
`6d8c7d2ecfa8b27d8373d1987678dc34c84ed45a`. Workspace HEAD
`66b6eadbc3d67a025fce49c41e46f9f2c29127f9`. Container work only in
`/home/researcher/lower-frontier-A`, with BLAS/OpenMP threads fixed to one,
`mp.cpu_count=lambda:2`, actual public utility calls using `mp=None`.
Each Sage launch had GNU `timeout -k 5 170` (175 s maximum including grace).
All jobs ran sequentially and exited normally except the preserved crash.

**Final process state:** all lane-A compute jobs exited and were reaped;
container process inspection at 04:09 UTC found no active lane-A worker or
solver. The container has historical defunct children and one defunct shell
from the crash, but no running computation. No paid/remote computation,
outreach, commits, subagents, shared source or dashboard edits. Initial
handoff saved before 04:16 UTC. No automatically continuing work.
