# Relation signature engine

This is a small exact/numerical screening engine for step graphons whose block
probabilities are constant on a modest number of symmetric relations.  It is a
search tool, not an independent promotion checker.

## Run

Compile once:

```sh
/usr/bin/clang++ -O3 -std=c++17 research/experiments/relation_engine/engine.cpp \
  -o research/experiments/relation_engine/engine
```

Run a JSON configuration through the immutable adapter/native snapshots:

```sh
python3 research/experiments/relation_engine/run.py \
  --config research/experiments/relation_engine/configs/quadratic80.json \
  --out reports/my-relation-run
```

Regression suite:

```sh
python3 research/experiments/relation_engine/test_engine.py
```

`engine.cpp` and `run.py` are the frozen v1 artifacts.  The separate
`engine_v2.cpp` / `run_v2.py` pair fixes boxed free-variable boundary
projection without changing v1 or the weighted-group path, and reports its
continuous terminal point, projected KKT norm, active walls, iteration count,
termination reason, and cap stalls.  Its regression command is:

```sh
python3 research/experiments/relation_engine/test_engine_v2.py
```

The 80- and 128-relation accepted replays are respectively
`reports/relation-engine-quadratic80-replay-001` and
`reports/relation-engine-quadratic128-replay-001`.

## JSON schema

Generic configurations use `schema: relation-engine-config-v1` and contain:

- `mode`: `matrix` or `translated`;
- `n`, `q`, and `relation_count`;
- matrix mode: an explicit symmetric `n` by `n` `relation_ids` matrix;
- translated mode: an `n` by `n` `difference_table` plus an `n`-entry
  `relation_of_difference`; the native engine verifies the full torsor identity
  before using the reduced `n^3` normalization;
- `probability_numerators`, one exact integer in `[0,q]` per relation;
- `constraint_group_ids`: `-1` freezes a relation, `-2` makes an interior
  relation free, and each nonnegative ID preserves the mass-weighted mean of
  that disjoint relation group;
- optional `integer_direction`, used for exact objective values at integer
  steps zero through six;
- `expected_parent_fraction`, required when `materialize_candidate` is true;
- `materialize_candidate`, normally false for screening.

The five-orbit input schema `relation-engine-input-v1` is also accepted.  Its
neutral rows are checked for disjoint support and proportionality to native
relation masses, but deliberately deferred.  The first pass freezes every
relation and emits exact gradients/Hessian; a consumer must certify the true
gradient-neutral subspace before activating constraints or submitting a
direction.

## Semantics and output

Matrix mode enumerates all ordered `n^4` vertex tuples, including repeated
indices, by unordered-index compression.  Translated mode uses the verified
group-difference witness and equivalent `n^3` census.  Six positional edge
occurrences are never deduplicated.

The report includes the exact parent numerator, exact relation gradient, exact
Hessian second derivative, relation masses, constrained numerical minimum
eigenpair with Jacobi residual, deterministic feasible descent, exact rounded
recount, rounding-constraint residuals, optional seven directional values, and
separate timings.  For an integer direction `d`, the degree-two directional
polynomial coefficient is `C2 = (d^T H d)/2`; the stored Hessian is the second
derivative, not `C2` itself.

Every run snapshots and hashes the input, fixture, source, binary, and adapter
before execution and verifies those bytes are unchanged afterward.  Built-in
controls cover a literal arbitrary `n=4` matrix, repeated relation occurrences,
diagonal blocks, exact gradient/Hessian, complement invariance, production
mass, and constant probabilities.  Arithmetic bounds are checked before exact
`UInt128`/`Int128` evaluation.

## Known limits

- Constraints are only disjoint mass-weighted groups.  General overlapping
  linear constraints must be projected by the consumer into an explicit
  direction.
- Dense relation Hessians are intended for hundreds of relations, not all
  1,248 individual fractional edges of the 192-class parent.  That problem
  needs the separate direct matrix HVP/dense formula.
- Numerical eigenvectors are proposals.  Promotion requires seven exact line
  recounts, a separately materialized candidate, and the independent
  candidate-bound verifier.
- A five-orbit invariant-subspace result is not exhaustive for the full graphon.
- No global optimality or novelty claim follows from absence of local descent.
