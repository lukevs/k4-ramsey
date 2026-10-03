# Relation-engine fixtures

`adapter.py` converts an explicit semidirect Cayley candidate into the generic
`relation-engine-config-v1` matrix format. It reconstructs the group law and all
128 inverse-paired relations, then refuses the conversion unless every explicit
candidate entry is constant on its claimed relation.

Frozen fixtures:

- `r1_stationary_frozen.json` (SHA-256 `3a280b44feebd4f9ab3cde31dacdc8bfab16a66b81b556f3c874afefbe2ad959`):
  independently recounted stationary abelian-collapse candidate `0fb88f4a...`.
- `r1_action_breaking_frozen.json` (SHA-256 `0948cadc8f982d4745b094b0cab52bc61182175c4e69baf60afefa76908ef1ac`):
  matched r=1 action-breaking control `f86d4a79...`.
- `r1_stationary_fractional_free.json` (SHA-256 `4e53fd4f6b2121b54b7a00e3a22cc21a51378cadb2d9741a38e9d459a2006379`):
  the stationary fixture with its 13 strictly fractional inverse relations free
  and 115 deterministic boundary relations frozen, for a local Hessian test.

The adapter itself has SHA-256
`66a9bc180190d1c0b17aa445e2d0f152b1f3761f415e79145b051c7c78d03a1a`.
Regenerate a config on stdout with, for example:

```sh
python3 research/experiments/nonabelian_graphon/adapter.py \
  --candidate reports/nonabelian-cayley-r1-continuation-001/graphon-candidate.json \
  --acted-blocks 1 \
  --expected-fraction 8252429612735690156467948788193/273812529649297550723287892361216
```

Once the shared engine is present, the frozen roundtrip command is:

```sh
python3 research/experiments/relation_engine/run.py \
  --config research/experiments/nonabelian_graphon/configs/r1_stationary_frozen.json \
  --out reports/relation-engine-nonabelian-r1-stationary-001
```

The engine owns objective evaluation, exact recount, and candidate emission;
this directory contains no duplicate optimizer/evaluator.

## Acceptance result

The first acceptance run is preserved at
`reports/relation-engine-nonabelian-r1-stationary-001`: the initial engine
binary aborted its internal gradient self-test in 0.27 seconds, before fixture
evaluation. After the engine owner corrected and independently smoke-tested the
self-test, the unchanged config passed at
`reports/relation-engine-nonabelian-r1-stationary-002`.

The shared engine reproduced the independent exact fraction
`8252429612735690156467948788193/273812529649297550723287892361216`
with zero optimization dimensions. Census time was 3.114 seconds and native
total time 3.157 seconds. The rematerialized candidate is JSON-semantically
identical to the archived candidate. Raw file hashes differ only because of
serialization formatting; both have canonical sorted/compact JSON SHA-256
`18341f6955ae415f8b6ca1bbe212072e2b2bc781f5dae270ebaafdff55ccf418`.

Accepted engine identities: source
`78c49a2587abfa28675242c275d6955080af8586151b1d7e877877adbaee3013`,
binary `e66388bbef9093035d469b7acb117ee9821ca6c935936d4af4566e65f3c86784`,
and driver `1008b55d52f00661ed04e81d07e453b1ea959a9fcf178f788387a68fd8fa4eab`.
