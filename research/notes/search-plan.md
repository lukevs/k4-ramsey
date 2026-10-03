# Computational search plan

Updated 2026-09-27. Status: native primitives, a generic unit-weight Lean
checker, and the isolated single-experiment runner are implemented and tested.
A one-second infrastructure smoke search and a no-search reproducibility test
exercise the pipeline; the one-hour research campaign has not been launched.
Supersedes the earlier proposal for a pydantic-ai research controller.

The [adjacent-methods review](adjacent-methods.md) supersedes the fixed
algorithm-portfolio priority below: run short hypothesis-driven experiments,
including exact matching/star neighborhoods and recursive/profile constructions.
McKay is a milestone, not a stopping target. A stronger construction, rather
than compliance with AutoLab's construction limits, is the research goal.
Any enlarged mathematical objective/domain needs a corresponding exact checker.

## Decision and responsibilities

Use a compiled computational search engine, a small Python experiment runner,
and an independent exact verifier. The assistant coordinates implementation,
experiment selection, diagnosis, and research notes. No pydantic-ai dependency,
paid model loop, or per-edge model calls are needed.

The coordinating Codex session and its authorized subagents dispatch bounded
experiments directly; no standalone queue service is needed. A strategy runs
computationally within its explicit deadline. Do not imply that a detached
worker guarantees ongoing assistant supervision. Regenerate the HTML journal
after dispatch and completion to expose the latest recorded state.

The evidence motivating this choice is summarized in
[current-state.md](current-state.md). It supports testing local-search methods;
it does not establish which will perform best in our implementation.

## Exact single-edge changes

Initial domain: n=768, unit weights, blue diagonal. Optimize the integer
numerator N, not a floating-point approximation or a distinct-vertex-only
clique objective.

For endpoints u,v, let C_b be their common blue neighbors and C_r their common
red neighbors, excluding u and v. Write e_b(C_b) and e_r(C_r) for unordered
induced edges of the specified color. A blue-to-red flip has exact change

    delta_N = -14 - 36*|C_b| - 24*e_b(C_b) + 24*e_r(C_r).

A red-to-blue flip has the negative of this expression. The sets are formed
from the current graph; changing uv leaves these endpoint-excluded sets
unchanged. For a multi-edge move, apply/recompute changes sequentially or
derive interaction corrections. Summing independently evaluated stale deltas
is not valid in general.

Use packed adjacency bitsets, popcount intersections, and signed 64-bit
deltas/counts in this fixed-size backend. The maximum N is 768^4, within
signed 64-bit range. General weighted evaluation requires a separate integer
overflow analysis, preferably arbitrary-precision arithmetic.

## Validation before the timed pilot

1. Reproduce the published numerator and all component counts.
2. Compare a separate full counter with literal ordered-quadruple enumeration
   on tiny graphs, including complete and empty cases.
3. Check every edge delta against a full before/after recount on small random
   graphs and exhaustive small instances.
4. Test long flip sequences, undo operations, and checkpoint reloads; confirm
   no incremental-count drift.
5. Exercise bitset boundaries, invalid inputs, deterministic seeds, deadlines,
   and worker cleanup. Measure moves/second and full-scan cost.
6. Save a deterministic greedy baseline, including tie-breaking rules.

Keep verifier implementation separate from search code. Verification failure
quarantines the candidate and stops the affected search rather than promoting
an apparent improvement.

## One-hour local pilot

User selected a one-hour local pilot with at most four CPU workers. No paid
API calls are planned; the former $20 ceiling is not a spending target.
Start the timed campaign after implementation and correctness checks.

Begin with a small portfolio sharing the same published seed:

- Greedy descent as the baseline and a source of restart checkpoints.
- Tabu search permitting bounded uphill moves, with aspiration for a new best.
- Simulated annealing with recorded temperature and cooling schedules.
- Iterated local search with variable-size kicks and diverse retained seeds.

Use at most four concurrent compute workers in total, including expensive
verification tasks. All workers share a campaign deadline. Checkpoint on new
bests and periodically; stop on deadline, explicit user request, or integrity
failure. A target-beating candidate triggers independent verification before
any success claim. Do not launch an unbounded continuation automatically.

Measure full-neighborhood scans before making them the default at every move.
Candidate sampling may improve throughput; record it as part of the algorithm.
Compare methods on matched seeds and compute budgets. A single pilot is not
enough to conclude one heuristic is generally superior.

Do not defer all structural experiments until edge search is exhausted:
allocate short screens to the adjacent-methods hypotheses as well. Weighted,
diagonal, and recursive extensions require extending the checker first.

## Persistent outputs and acceptance

Create an experiment journal before the campaign. Preserve:

- Exact input/output matrices in the hill-compatible certificate schema.
- Graph and code hashes, RNG seeds, configurations, command lines, versions,
  wall time, evaluated moves, and accepted moves.
- Best-so-far history, full recount reports, failures, and restart provenance.
- Separate search-reported, independently integer-checked, and Lean-native-
  checked result statuses.

Full-recount every candidate promoted to the shared incumbent. Recheck the
final best and every target-reaching candidate with Lean, extending the current
seed-only certificate workflow as necessary. Verification time belongs in
campaign resource accounting; stop admitting work early enough to save and
verify the final artifact.

Report the exact fraction and gap to 10486266368/768^4. At fixed n=768:

- N > 10486266368: target not reached, even if the seed was improved.
- N = 10486266368: matched the reference density, not necessarily McKay's graph.
- N < 10486266368: beat the frozen reference, subject to verification and
  novelty review; not a proof of the exact value of c4.

Do not call a run successful merely because it stopped, because a floating-
point display rounded to the reference, or because a search-maintained count
crossed the threshold without a checked witness.
