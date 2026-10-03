---
name: hypothesis-research
description: Conduct iterative mathematical and computational research through diverse hypotheses, targeted literature review, rapid experiments, and adversarial verification. Use when asked to organize or run an open-ended research loop, seek better constructions, or develop and test proof strategies; not for ordinary coding or a one-off literature question.
---

# Hypothesis-driven research

Optimize the rate of reliable discoveries, not the number of runs or the appeal
of an argument. A research iteration ends with new evidence and a decision,
not merely an implementation or status update.

## Establish or resume the research contract

Read the project's research notes, current artifacts, and unfinished experiments
before proposing a new plan. Reuse established budgets and decisions. Record:

- The exact mathematical question and admissible constructions, including
  quantifiers, normalization, asymptotic versus finite claims, and edge cases.
- The user's actual objective, known milestones, and what would establish a
  stronger result. A published benchmark is not automatically a stopping target.
- What the checker certifies, what remains informal, and what changes require
  a new checker. Separate proof, counterexample, construction, and optimization.
- Authorized machine, wall-time/compute/spending limits, concurrency, external
  actions, and stopping criteria. Skill invocation does not authorize a campaign
  when the user only requested a plan, review, or skill creation.

Ask only for missing choices that change scope or risk. Do not silently convert
a finite construction search into a proof of global optimality, or the reverse.

Before running a campaign, read [the experiment protocol](references/protocol.md)
and establish its lightweight records. For the origin and adaptation of this
workflow, see [source principles](references/source-principles.md).

## Research loop

### Ground the baseline and generate hypotheses

Inspect direct and adjacent primary research before expensive rediscovery.
For each useful source, extract a transferable mechanism, its assumptions, a
specific mismatch with our problem, and the cheapest discriminating test.
Retrieve existing witnesses/code when useful and authorized; verify before reuse.
Distinguish published results, announcements, reproduced artifacts, our own
derivations, and unverified leads. Independent derivation is not novelty.

Maintain families of materially different ideas: objective/representation
changes, structural constructions, exact subproblems, search dynamics, and
proof or obstruction mechanisms as relevant. Parameter variants of one method
belong to one family. For each hypothesis state a prediction, a way to disconfirm
it, and why the outcome would change the next action.

### Build only the infrastructure that shortens a useful experiment

Start with a trusted baseline and a simple oracle on tiny instances. Isolate
the objective and checker from editable search code. Profile before optimizing;
move demonstrated hot loops to compiled code where useful. Expose reusable
primitives so a new hypothesis does not require a new framework.

Test incremental computations against full recounts, rollback and serialization,
exact arithmetic and boundaries. Account for setup and verification in performance
comparisons. A cheap surrogate may guide exploration, never certify the result.
Stop infrastructure work when it is sufficient for the next discriminating test.

### Run small tests, inspect, then adapt

Use the smallest case, screen, or restricted problem capable of falsifying the
mechanism. Make one causal change per comparison where practical; record
confounded exploratory runs as such. Use matched inputs, seeds and resource
budgets to compare algorithms. A verified witness establishes its value even
when algorithm reliability needs multiple runs.

After each short batch, inspect artifacts and mechanisms, not just the best
score: interaction patterns, where time went, accepted/rejected moves, structural
changes, sensitivity, and counterexamples to proposed explanations. Record a
decision: pursue, revise, combine, retire, or await a specific missing mechanism.
Let findings change the implementation and hypothesis queue, not just parameters.

Allocate effort dynamically by evidence gained and plausible progress per cost,
while retaining exploration of genuinely different families. Keep early proposals
from being steered by the current favorite. If delegation is separately authorized,
give independent workers the problem and constraints before sharing favored
arguments. Otherwise explore alternative formulations sequentially and do not
mislabel them independent-agent reviews.

Revisit literature when a result resembles known work, a structural barrier
appears, a representation changes, or a novelty claim is contemplated. Search
for counterexamples and negative results as well as supporting evidence.

### Audit proposed progress

Produce a concrete deliverable: a checked witness, explicit equation, proved
lemma, counterexample to a subclaim, measured failure, or validated implementation.
Challenge it in a separate review pass. Check hidden assumptions, circularity,
irreversible reductions, missing cases, numerical artifacts, and mismatch between
what was measured and what was claimed. Use a separate checker or independent
derivation where feasible; same-code agreement alone is not independence.

A reformulation that still requires a theorem-strength missing lemma is not
near-completion merely because it is elegant. Record the exact gap. Reopen that
route only with a new mechanism or relevant evidence, not cosmetic rewording.
An exhausted exact neighborhood establishes only a restricted result; a failed
heuristic establishes no nonexistence theorem.

If the evaluator is wrong, stop affected experiments, preserve their reports,
version the correction, and re-establish the baseline before comparing results.
Never promote a candidate whose independent check failed.

## Continue, stop, and hand off honestly

An unsuccessful batch triggers synthesis and a new experiment while authorized
budget and worthwhile hypotheses remain. Do not repeatedly ask permission for
already authorized steps. Do not substitute a fixed parameter sweep for research.

Stop at the agreed limit, user interruption, verified task completion, an
integrity failure, or a need for new authority. Reserve time to save and verify.
Checkpoint unproductive families without declaring the whole task impossible.
Do not claim a proof or optimum because time expired; do not continue indefinitely
because a source prompt demands success. Budget exhaustion is a valid outcome.

Leave a concise state: strongest verified result and artifact, exact remaining
gap, useful failures, unverified leads, next hypotheses with discriminating tests,
and whether any processes remain active. Report worker PIDs and deadlines if
leaving authorized jobs running; do not imply ongoing supervision after yielding.
