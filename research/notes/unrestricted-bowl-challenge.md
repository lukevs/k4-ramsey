# Unrestricted bowl CHALLENGE — completed bounded pilot

Shared workspace, no fork. Deadline 2026-09-30 05:20 UTC, unchanged. All compute
completed before deadline; every launched job has exited and been reaped. No
incumbent/shared RESUME changes, commits, remote work, outreach or descendants.
Only assigned experiment/report/note paths written. Initial setup was delayed
because system Python and .venv lacked numpy/scipy; reused an existing cached
environment without installing anything. This was a CHALLENGE lane, not a new
agent launch. Used hypothesis-research skill and its experiment protocol.

## Question and scope

Does removing Clebsch, P/H relation categories, fixed entries, and the 12-block
template expose competitive small constructions? Optimize full symmetric
probability matrices at n=6,10,16, including diagonal probabilities. Objective
is the weighted sum over ALL ordered quadruples of red and blue six-edge
products, including repeated indices. Masses are nonnegative and sum to one.
SLSQP permits zero masses; L-BFGS-B uses positive softmax masses with bounded
logits. Incumbent 0.030138887566497220 is preserved.

H1: variable masses improve matched unrestricted starts. Unsupported in this
screen: all runs returned near 1/32. H2: coherent pair rebuilds escape the
observed near-homogeneous basin. Unsupported for the tested moves. Neither
result establishes nonexistence, optimality, or dependence on Clebsch.

## Completed evidence

- 32 matched equal/variable pairs: 20 SLSQP pairs and 12 L-BFGS-B pairs.
  Starts include independent uniform probabilities, sharply heterogeneous beta
  probabilities, binary matrices, and random three-block models with noise.
  Within each pair the full initial matrix and equal initial masses coincide.
- 24 additional coherent rebuild trials: copy a donor row into two classes
  with opposite 0.45 perturbations, reset their mutual/diagonal interactions,
  preserve masses, and reoptimize the whole matrix. The perturbations were not
  matched between equal/variable branches; these are exploratory escape tests.
- Four separate known-base relaxation controls: cycle5 and Clebsch16, equal
  and variable masses, freeing every formerly binary entry including diagonal.
  These are NOT independent-start evidence and did not improve the incumbent.
- 92 full candidate matrices and mass vectors saved and independently recounted.
  The best independent-start candidate is n6-s503-equal.json at
  0.031250000000223245. The smallest number across all candidates is the
  Clebsch control at 0.03125000000007711. Neither numerically improves exact
  constant-half graphon 1/32, let alone the incumbent. Gap to incumbent is
  approximately 0.001111112434.
- Variable-minus-equal objective differences across the 32 pairs range from
  -2.30e-11 to +5.39e-11: no meaningful mass advantage at these tolerances.
- 91/92 optimizer calls report success. lb-n16-s703-variable-rebuild reached
  its 500-iteration cap; its valid saved candidate still passed recount.

## Diversity and collapse

All final kernels have mass-weighted RMS distance from constant 1/2 between
0.000673 and 0.003935. Thus initial structural diversity largely disappeared
in the objective-relevant kernel. This is approximate homogenization, not
literal identical-row collapse: pairwise row distances are saved and exact
near-duplicate rows need not occur at the 1e-5 threshold.

| n | saved independent/rebuild candidates | variable effective class count range | mass entries <1e-6 summed over these candidates |
|---|---:|---:|---:|
| 6 | 30 | 3.700–5.957 | 6 |
| 10 | 30 | 5.132–9.717 | 14 |
| 16 | 28 | 5.211–15.536 | 42 |

Effective count is 1/sum(m_i^2). Counts above include correlated descendants;
they are diagnostics, not independent trials. Nonuniform surviving masses
and occasional vanished classes did not preserve a useful nonconstant kernel.

## Verification and reproducibility

Frozen evaluator.py uses a separate Python ordered-quadruple loop and math.fsum;
search.py uses NumPy contractions and analytic derivatives. The evaluator is
never called by search. n=1,2,3,4 objective checks differ by <=1.39e-17, matrix
and mass derivatives differ from central differences by <=1.97e-11. Complement
and permutation invariance pass, as does a duplicate-class split preserving
mass. Exact two-class rational fixture is 6367985293/89616844800. This checks
repeats/diagonals explicitly; candidate recounts also separately report repeated
and distinct contributions. Maximum independent candidate recount disagreement
is 1.39e-17. These are independent numerical checks plus an exact tiny fixture,
not formal certificates or exact rational certificates for searched candidates.

All jobs sequential, thread environment set to 1 before NumPy import, hard
SIGALRM <=170 seconds and clamped to deadline. Total measured optimizer wall
time was 4.516 seconds; independent final recount took 0.946 seconds. These
exclude interpreter imports, setup, code writing and tiny checks. Same starts
and iteration caps are matched, not CPU time or evaluation counts. Hardware
thread counts were not independently sampled. Source, per-run vectors, seed,
initialization, solver status, elapsed time and PID are saved. contract.json
records commands, environment and hypotheses; audit.json binds candidate hashes.
manifest-final.json is the authoritative final hash list. Earlier manifest.json
was created before audit stdout closed and can contain a stale stdout hash;
it is retained as an uncorrected historical receipt, not used for final checking.

## Decision and next discriminating test

The small unrestricted local searches tested here do not challenge the
incumbent; they mainly expose attraction to near-constant-half kernels. They
do not show Clebsch, P/H categories or 12 blocks are necessary. No novelty or
record claim, and nothing is promoted.

Next test: use a fixed budget of discrete multi-block rebuild/annealing moves
before unrestricted continuous relaxation, at n=16 and one moderately larger
size, with matched equal/variable matrix-entry evaluation budgets. Include a
held-known nonconstant witness as a recovery control to distinguish an
optimization failure from an insufficient representation. Compare retained
nonconstant weighted variance and checked objective, not just optimizer success.
