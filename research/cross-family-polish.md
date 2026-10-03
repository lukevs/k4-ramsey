# Algebraic basin plus unrestricted polishing

2026-09-27. Matched short comparison, not proof of general superiority.

The algebraic worker independently generated a degree-preserving permutation
lift seed. Both it and the original published seed were then run through the
same deterministic cached single-edge/star-pair descent, with30-second caps,
seed21 (unused by this deterministic strategy), per_color16 and checkpoints
every100moves. Both finished at their selected-neighborhood plateaus.

| Input | Input numerator | Checked polished numerator | Gap above McKay |
|---|---:|---:|---:|
| Published Cayley seed |10487165184|10486395412|129044|
| Independent lift seed |10487028480|10486318166|51798|

Denominator768^4 throughout. Reports:

- `reports/cross-family-original-star-001/report.json`
- `reports/cross-family-lift-star-001/report.json`

Both candidates received independent compiled Lean recounts. The latter was
submitted to the coordinator as a new retained-best candidate. This is a
positive instance of structural construction followed by releasing constraints,
not evidence that all lift seeds outperform all local-search starts. The
algebraic worker now owns a bounded independent-seed follow-up.

Reproduction uses `experiments/strategies/fast_neighborhood.py` with
`reports/config-cross-family-star-001.json`, `--seconds30 --timeout45` under
the single-experiment runner (spaces required between flags and values).

## Handoff

The unit build manifest was refreshed after adding the separate weighted
checker executable. Original unit verifier and native engine sources were
not modified during weighted-checker development. The full Python regression
was rerun after these integrations; see the worker's handoff for its result.
All processes launched by this worker have completed.

A potentially useful untested weight direction remains: the already-derived
unit-weight gradient is g_i=4+28*d_blue(i)+48*T_blue(i)+24*K4_incidence(i).
Rather than transfer mass between only two blocks, take a small rational,
sum-zero direction against the full projected gradient, keeping every weight
positive. This could aggregate many individually small pair improvements.
It needs a recorded prediction, exact candidate evaluation, and independent
verification; no such experiment was launched before this handoff.
