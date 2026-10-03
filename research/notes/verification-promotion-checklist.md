# Independent graphon promotion gate

This is the compact handoff contract between search lanes, the independent
verification lane, and any shared experiment engine.  It wraps the existing
checker; it does not change the mathematical evaluator.

## Search-lane request (never sufficient for promotion)

A search lane may submit only:

- `candidate_path` to an immutable `rational-step-graphon-v1` JSON artifact;
- the candidate's SHA-256;
- order, probability denominator, block-weight semantics, and any natural
  base/type indexing;
- its claimed **exact fraction** and comparison parent, labeled as a prediction;
- the candidate domain and anticipated kernel diversity, so verification can
  choose direct versus compressed counting.

Search-generated counts, decimals, certificates, or a `status: completed` field
cannot promote their own candidate.  In particular, do not copy the search
score into an independent report as an expected value.

## Independent invocation

The generic promotion path for an explicit equal-mass matrix is:

```sh
PYTHONPATH=src:. python3 -m experiments.verification_precision.run_direct_u256_audit \
  --candidate CANDIDATE.json \
  --expected-sha256 CANDIDATE_SHA256 \
  --out reports/UNIQUE-INDEPENDENT-AUDIT \
  --timeout 300
```

The output directory must not already exist.  The checker reads the candidate,
not a supplied score.  For low-diversity, base-major typed kernels, the faster
Level-A screen is:

```sh
PYTHONPATH=src:. python3 -m experiments.verification_precision.run_typed_kernel_audit \
  --candidate CANDIDATE.json --types T \
  --expected-sha256 CANDIDATE_SHA256 \
  --out reports/UNIQUE-COMPRESSED-AUDIT
```

That second path is native candidate-to-histogram binding plus compiled Lean
exact arithmetic.  It is not a full Lean candidate recount.  Use the direct
path for promotion-critical candidates when kernel diversity makes compression
large or when a materially independent full recount is warranted.

## `report.json` is the invocation receipt

The shared engine may accept a direct report only after checking all of these:

1. `schema == "direct-ordered-u256-audit-v1"`, `status == "completed"`, and
   `evidence == "independent_generic_direct_ordered_index_u256_recount"`.
2. `candidate.sha256` equals both the submitted SHA and the hash of the copied
   `candidate_snapshot.json`.  Candidate path alone is not identity.
3. Candidate validation flags assert unit masses, symmetry, and probabilities
   in `[0,Q]`.  Weighted candidates require a different checker or an exact
   unit-class expansion and must not be silently accepted here.
4. `tiny_literal_oracle.status == "passed"`; the current receipt contains 12
   arbitrary symmetric matrices with arbitrary diagonals and repeated indices.
5. Every recorded U64/U128/U256 inequality is strict and passed before the full
   count.  The engine must not infer safety merely from successful termination.
6. `direct_recount.total == red + blue` and
   `direct_recount.denominator == N^4 * Q^6`.
7. Parse `direct_recount.density` as an exact `Fraction(total, denominator)` and
   regenerate any decimal for display from that fraction.  Never promote or
   compare a manually transcribed decimal.
8. Hash and retain `report.json`, the source snapshot, driver snapshot, compiled
   binary, and candidate snapshot.  Record wall time and termination normally.
9. Preserve evidence scope: native exact execution is not compiled Lean, a
   kernel proof, a formal graphon-realization theorem, an optimum, or a novelty
   claim.

For a compressed report, require its corresponding schema/evidence labels,
candidate and certificate hashes, tiny fixtures, `coarse_histogram_mass=B^4`,
and exact normalization.  Display it as **native candidate binding + Lean exact
arithmetic (Level A)**.  Do not relabel it as a full Lean candidate recount.

## Promotion decision

The coordinator, not the search worker or checker, compares exact fractions.
Promote only if the independent receipt's fraction is strictly below the frozen
incumbent and the candidate domain is admissible.  A mismatch quarantines the
candidate and its reports; it never falls back to the predicted search score.

Current direct-receipt example:
`reports/graphon-association-per-edge-boundary-continuation-direct-u256-001/report.json`
with report SHA-256
`634a92d73e6c6e15e10e72a7d4da6462894862f73c528e798241eebca94d7b01`.
