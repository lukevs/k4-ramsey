# Prepared per-edge amplitude coordinate screen

Status: derivation and test plan only; no CPU screen launched.  Parent is the
immutable H-F2-01D candidate
`reports/association-scheme-phase-two-amplitude-001`, candidate SHA-256
`33df1d72c6e50a2ea0dc205f771ab8d3372b621b273cc53237072017ad4dda4d`.

This lane is distinct from the latent worker's active-block mean/amplitude face
move.  Here every coarse mean, phase, support bit, kernel, and all other edge
amplitudes stay fixed.  Only one active edge amplitude varies at a time.

## Exact coordinate polynomial

Give every active fractional coarse edge `e` its own integer amplitude `q_e`.
For an exact cached motif factor `f`, let

```
b_f = coarse_weight(f) * cyclic_intersection_moment(f, phases).
```

The factor contribution is

```
b_f * product over selected position-edges r in f of q_{edge(r)}.
```

The product is over occurrences, not distinct coarse edges.  If equality among
the four sampled coarse indices makes the same coarse edge occupy several
selected position-edges, its amplitude is repeated with that multiplicity.

Fix an active edge `e` and hold every other amplitude at the H-F2-01D values
`q_p=-7236`, `q_h=-11671`.  Group its incident factors by the number `m` of
times `e` occurs in their signatures:

```
A_e,m = sum_{f incident to e, multiplicity_e(f)=m}
          b_f * product_{r in f: edge(r) != e} q_{edge(r)}.

g_e(x) = sum_{m=1}^4 A_e,m x^m.
```

The maximum multiplicity is four, attained by a `2+2` coarse equality pattern
whose four cross position-edges all use the same coarse edge.  Multiplicity
five or six would force a selected loop, but fractional support has no loops.
Therefore every exact coordinate objective has degree at most four, even
though the full amplitude objective has total degree at most six.

The current feasible coordinate intervals remain

```
p edge: x in [-7236, 4824]
h edge: x in [-11671, 10173].
```

For an inactive edge the factor objective is discontinuous in the separate
support bit: activating it introduces factors that are currently zero.  This
first screen covers the 976 active parent edges only.  It must not silently
describe inactive edges as amplitude zero coordinates unless their phase and
activation semantics are also restored.

## Preregistered cheapest falsifier

For all 976 active edges, derive `(A_1,A_2,A_3,A_4)` from the cached factor
signatures and exhaustively minimize `g_e(x)` over that edge's complete integer
interval.  All edges are screened against the same immutable parent; do not
apply earlier improving coordinates while measuring later ones.

Record for every edge:

- coarse endpoints, p/h kind, current amplitude, and interval;
- exact four coefficients, current local value, exact minimizing coordinate,
  and exact local delta;
- inward one-step delta `g(q+1)-g(q)` at the current lower boundary;
- incident-factor counts by motif degree and repeated-edge multiplicity.

Prediction: at least one active edge has a strict exact coordinate improvement
away from its shared lower boundary.  The decisive restricted negative is that
every edge's exact interval minimum includes its current coordinate.  That
would establish coordinatewise amplitude stability only for this fixed
phase/support/mean/kernel parent, not joint-amplitude or graphon optimality.

If the screen is positive, preregister one deterministic sequential coordinate
sweep using the same lexicographic edge order and exact minima, recomputing
affected factor products after each accepted change.  Do not materialize 976
independent candidates or select among seed restarts.

## Tiny exact oracle plan

Run before the production screen:

1. **Two coarse classes, one active edge.**  Use a rational `T=5` refinement
   and enumerate all refined ordered quadruples literally.  The `2+2` terms
   force four occurrences of the sole coarse edge.  Compare the derived
   quartic with literal raw numerators at every feasible amplitude in a small
   denominator.
2. **Three/four coarse classes with two probability kinds.**  Include active
   p/h edges, one inactive edge, repeated coarse indices, and nonuniform phases.
   Compare the complete factor sum with the literal refined count.  For one
   active edge of each kind, hold the other per-edge amplitudes fixed and check
   the coordinate polynomial at both boundaries, the parent coordinate, and
   two interior values.
3. Assert on the full factor bank that every occurrence multiplicity is at most
   four and that evaluating all coordinate polynomials at their parent
   amplitudes reproduces each factor's current local contribution.

These tests distinguish repeated-variable powers from mistakenly treating a
factor signature as a set of coarse edges.

## Prospective cost and evidence boundary

The current model has 160,320 aggregated factors.  Building all coordinate
coefficients touches each factor signature occurrence once, roughly under one
million exact integer products.  Exhaustive interval minimization needs

```
880 * 12061 + 96 * 21845 = 12,710,800 integer quartic evaluations
```

(the precise active p/h counts are 880 and 96).  Horner evaluation should make
this a seconds-scale single-process screen; tiny oracles are subsecond.  Record
actual factor-build, coefficient-build, and interval-scan times separately.

The output is diagnostic search evidence.  Coordinate polynomials are exact if
the oracle passes, but an improving edge is not a recounted graphon candidate.
Only a subsequently preregistered sequential sweep, explicit materialization,
and fresh candidate-bound compressed recount can promote a construction.

## Results

The matched `33df` screen found 374 improving coordinates among all 976 active
variables. Its single preregistered sweep changed 338 amplitudes and predicted
`0.030138904016391212`; this improves `33df` but is weaker than the subsequently
verified `b93` boundary-face candidate.

The causal combination was then tested once on immutable `b93`, after rebuilding
the factor weights with active-h mean 35139 and amplitude -11713. Reconstruction
of the parent was required to equal the `b93` 960-step matrix before descent.
Three bounded exact coordinate sweeps changed 314, 329, and 267 amplitudes and
predicted

`16900934506883319165303058334011571 /
560768060721761383881293603555770368 = 0.03013890356938343`.

This is an exact predicted improvement of
`245029933804809651175341901 /
560768060721761383881293603555770368` over `b93`. The third sweep was still
active, so this is a bounded witness rather than a coordinate fixed point.
The candidate is `reports/association-scheme-per-edge-boundary-001` (SHA-256
`3f657ae09b736b09dc7ebed7404da5ba9b396ef96fe88978a74d9056d7eea106`), with
288 distinct oriented 5x5 kernels. Independent recount is pending.

The three-sweep candidate subsequently passed a fresh full generic U256 recount
exactly (`reports/graphon-association-per-edge-boundary-direct-u256-001`). A
separate deterministic continuation ran ten more sweeps; changes fell from 241
to 25 and the per-sweep marginal gain became negligible. Its final prediction is

`16900934504649027287619486865996291 /
560768060721761383881293603555770368 = 0.03013890356539909`.

That continuation candidate is
`reports/association-scheme-per-edge-boundary-continuation-001` (SHA-256
`d4763fefc34a3966bfbe811d279b522c067f193e436bb522d357dd423c0c58c3`), with
276 distinct oriented kernels. It improves the directly verified three-sweep
candidate by about `3.98e-12`; independent recount is pending. All 976 active
amplitudes remained nonzero. Residual changes mean this is still not a claimed
coordinate fixed point.
