# Clebsch size pilots — 2026-09-29

User explicitly authorized two subagents after asking whether construction size
is intrinsic. Two focused lanes are active; the broader distributed campaign
is not restarted. Target 6–8 minutes per initial pilot, one single-threaded
local compute job per lane, 180-second per-job ceilings. Root prepares and
runs independent small-instance/recount checks. No remote or paid compute.

Objective: weighted graphon t(K4,W)+t(K4,1-W), all ordered tuples including
repeated classes, with class weights normalized to sum to one. Matrix diagonal
entries are within-class probabilities, not automatically ignorable loops.
Benchmark: structured-exact depth-2 value 0.030138887566497220; compare every
pilot with its own matched baseline as well. No automatic record/promotion.

## SIZE-A — refinement size and latent masses

Agent Hegel, 01a0eff0-7ca1-7811-b8d5-42b59196b03e.
Hold twelve coarse Clebsch copies and their weights fixed; vary latent sizes,
nonbinary refinements or unequal latent masses. Read earlier E9 and latent
weight tests first. A random-start method that cannot reproduce the known
Z5 solution cannot rank other group sizes fairly. Required control: changing
size by exact duplication leaves the objective unchanged.

Writes only `experiments/clebsch_size_latent/`, `reports/clebsch-size-latent-*/`,
and `research/clebsch-size-latent.md`.

## SIZE-B — number and masses of the Clebsch copies

Agent Lovelace, 01a0eff0-7d2a-7bd1-8a05-14a2bfe20864.
Keep the internal 16-state Clebsch pattern; test a few changed coarse copy
counts and unequal copy weights. New coarse couplings must distinguish adding
a new type from duplicating an existing one. Single-root evaluation is invalid
after unverified loss of transitivity. Require weighted full-objective checks.

Writes only `experiments/clebsch_size_coarse/`, `reports/clebsch-size-coarse-*/`,
and `research/clebsch-size-coarse.md`.

## Completion standard

Each lane runs a bounded experiment, validates its evaluator, reports tested
scope and measurements, preserves reconstructible improvements, and states
whether to pursue, revise or stop that restricted family. Root checks results
without reimplementing either lane's search. A failed pilot is not a proof of
optimality in class count, weights or graphon space.

User subsequently requested reasoning about effectiveness before continuing.
Further experiments paused. Latent pilot completed 24 starts: all reduced to
two effective half-mass groups, no gain in its fixed-amplitude common-kernel
family. Root independently rebuilt and recounted all 20 initial coarse runs;
maximum discrepancy 4.65e-14. Coarse agent was instructed to stop new work and
finalize completed evidence. No new upper bound has been established.
