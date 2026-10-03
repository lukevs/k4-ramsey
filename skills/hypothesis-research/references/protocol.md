# Lightweight experiment protocol

Read when establishing or resuming an actual campaign. Adapt to existing files;
do not build a database or controller merely to satisfy this document.

## Persistent state

Keep these concepts in the project's existing research/artifact directories:

1. **Contract:** objective, construction domain, evidence standards, budget,
   machine/concurrency limits, deadline, and allowed actions.
2. **Hypothesis registry:** stable IDs, approach family, mechanism, prediction,
   test, provenance, result, and next decision. Group by ideas, not filenames.
3. **Experiment records:** immutable evidence linked to input, code/config,
   command, output and checker identities. Preserve crashes and negative results.
4. **Current state / journal:** readable, regenerable summary of verified best,
   active work, discoveries, failures, and queued tests. Create before the first
   campaign experiment and keep current between batches.

A Markdown registry plus JSON reports and artifact folders is often sufficient.
Use SQLite only when useful for actual queries or concurrent writers. Updates
to summaries may replace old summaries; never rewrite evidence to improve a result.

## Hypothesis record

```yaml
id: H001
family: exact-coordinated-moves
claim: Coordinated restricted moves can escape single-move local minima.
mechanism: Interacting variables can have a favorable joint change.
provenance: Own derivation inspired by cited method; novelty unestablished.
prediction: At least one screened local minimum admits a verified joint decrease.
test: Verify the restricted objective on tiny cases, then solve bounded neighborhoods.
controls: Same parent artifacts and total compute; sequential moves and random subsets.
failure_interpretation: No gain in tested neighborhoods, not global local-search impossibility.
resource_limit: Use the active contract; record the concrete per-test allocation.
status: proposed
evidence: []
next_decision: Advance only after correctness checks and useful measured signal.
```

Status vocabulary may be simple: proposed, ready, running, supported,
unsupported-in-tested-regime, needs-new-mechanism, retired. A scheduler status
such as completed says nothing about whether the hypothesis was supported.

## Experiment record requirements

- Hypothesis ID; exact question; parent artifact and hash; seed/configuration;
  source revision plus hashes or a snapshot for dirty/untracked source.
- Actual command, environment/compiler/checker versions, machine, timing,
  concurrency, deadline, and termination reason.
- Exact result where applicable, work counts and useful structural diagnostics,
  checkpoint/witness paths and hashes, error logs, and independent check report.
- Interpretation with its domain of validity; what changed in the next hypothesis.

Use one artifact directory per experiment. Avoid overwriting previous runs.
Make checkpoint writes atomic. Test interruption and restart on a short fixture
before long work. The parent owns concurrency/deadlines and reaps subprocesses.

## Parallel experiments

Use a bounded process pool for CPU experiments, not one model agent per run.
Separate the coordinator's reasoning from computational workers. Honor the
active total CPU/memory budget, including compilers, native thread pools, and
verification jobs; four processes each using four threads are not four workers.

Queue many small experiments but run only the authorized number concurrently.
Initially spread short screens across distinct hypothesis families, then give
promising directions more resources while retaining exploration. Distinguish
quick screening from confirmatory matched-budget comparisons.

Each worker receives immutable code/config and a copied or read-only parent
artifact, writes only to its own run directory, and returns artifacts and
diagnostics. Build once before dispatch or use version-specific build outputs;
never replace a shared library underneath running workers. Include queue wait,
setup, compute, and verification separately in records.

Only the coordinator promotes independently checked candidates. Workers may
use new incumbents at explicit restart boundaries, not silently mid-comparison.
Record parent changes; retain diverse candidates instead of forcing all workers
onto a single basin. Read-only seed sharing is fine; concurrent edits to search
code, checkpoints, or shared reports are not.

The supervisor applies per-job timeouts plus the campaign deadline, records
crashes, and cancels/reaps children on interruption. Verify the supervisor with
short successful, failing, and intentionally timed-out jobs before a campaign.
External research and hypothesis revision occur between batches, not through
unbounded worker-spawning loops. Increase concurrency only with new authority
and evidence that hardware and memory permit it.

## Evidence labels

Use explicit labels rather than a single ambiguous 'verified' flag:

- Literature reported / announcement only.
- Search reported / numerical screen.
- Exact recount by the search implementation.
- Independently checked artifact, with checker identity and scope.
- Formal theorem checked, with statement and trust assumptions.
- Globally optimal, only with a matching universal bound or valid exhaustive proof.

Compiled Lean execution is useful evidence but is not interchangeable with a
kernel-only proof of counting correctness or an asymptotic lifting theorem.
A signed benchmark report likewise certifies only that benchmark's stated scope.
No held-out data is necessary for a deterministic witness count; stochastic
algorithm performance claims do require attention to repetitions and selection.

## Review prompts

For a construction: which exact object realizes the claim, and does the checker
read that object rather than a supplied score? Check repeated-index terms,
normalization, weight/diagonal semantics, and limits if relevant.

For a proof: list hypotheses of every imported result, the logical dependency
chain, unresolved lemmas, and small cases capable of refuting a step. Do not hide
an assumption in the checker that already implies the claimed conclusion.

For a heuristic: did it improve the actual objective under matched resources?
Does the proposed explanation predict a new observation? A useful witness does
not establish superiority of the algorithm, and multiple seeds are not multiple
independent mathematical constructions merely because their labels differ.

For novelty: identify the narrow proposed contribution, search alternate
terminology and closest predecessors, and separate 'not located' from 'new'.
Correspondence, publishing, paid services, and remote jobs need their own authority.
