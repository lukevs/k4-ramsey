# Compressed graphon evaluation: implementation acceptance

User approved implementation on 2026-09-27. Root coordinates; agents own
experimental code and tests. Existing campaign deadline and four-process cap apply.

## Deliverables

1. Reusable exact degree-at-most-six polynomial evaluation and integer amplitude
   minimization, with explicit normalization and exact probability feasibility.
2. A candidate-bound compressed recount. A supplied histogram and its total mass
   cannot certify correspondence to a candidate; reconstruct or verify the partition.
3. Tiny independent ordered-tuple oracles, including repeated coarse indices,
   nonzero diagonal cells, negative amplitudes and multiple latent levels.
4. Integration on the precision Potts candidate; retain the phase-optimized Z5
   candidate as a second fixture and document any unsupported kernel orientation.
5. Separate timings for setup, coefficient/certificate construction, optimization,
   and independent verification. Do not claim end-to-end speedup from fast
   polynomial evaluation alone.

## Ownership

- precision_lean_audit: compressed recount, candidate binding and benchmark.
- correlated_graphon: polynomial/feasibility utilities.
- latent_precision: independent tiny tests for those utilities.
- adversarial_review: certificate and implementation soundness.
- formal_realization: precise mathematical certificate contract.
- fresh_hypotheses: integration documentation and existing factor interface.
- root: review, coordination, evidence promotion and UI.

## Compression idea to evaluate

Aggregate coarse quadruples by their six base probabilities and six typed kernel
identifiers, retaining orientation. Compute a microtype sum once per signature,
instead of once per coarse tuple. Correct multiplicities must include repeated
coarse indices. A direct scan binding the serialized candidate to its typed
decomposition is mandatory. This is a proposed optimization until tested.

## Evidence boundaries

Independent native recount, compiled Lean recount, arithmetic-only Lean checking,
and a kernel-checked counting theorem are different evidence levels. Report the
one actually achieved. Restricted kernel support is acceptable for a first usable
implementation if its interface rejects unsupported inputs clearly.
