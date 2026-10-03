# H-F2-01 boundary-face follow-up

Checkpoint: 2026-09-27 20:42 UTC.  No experiment in this note has run.

## Audited parent

The immutable two-amplitude candidate is
`reports/association-scheme-phase-two-amplitude-001/graphon-candidate.json`,
SHA-256
`33df1d72c6e50a2ea0dc205f771ab8d3372b621b273cc53237072017ad4dda4d`.
Its Level-A compressed recount passed in
`reports/graphon-association-phase-two-amplitude-compressed-001/report.json`:

```
66019277286046017264653194279027 /
2190500237194380405786303138889728
  = 0.030138904422400026...
```

The fixed-point amplitudes both hit lower feasibility boundaries:

```
q_p = -7236 for coarse p=51064, feasible [-7236,4824]
q_h = -11671 for coarse h=35015, feasible [-11671,10173].
```

Thus another phase restart at the same representation is not the next causal
test.  The active constraint itself should be relaxed.

## Preferred hypothesis: an affine boundary-face ray

Keep the retained phase/support assignment and the same cyclic kernel
`kappa=[-2,3,-2,-2,3]`.  Change only active fractional blocks.  For integer
`t>=0`, define

```
q_p(t) = -7236 - t,    p(t) = 51064 - 2t,
q_h(t) = -11671 - t,  h(t) = 35015 + 3t.
```

On an active p-block, cells with `kappa=-2` stay exactly at `65536`, while
cells with `kappa=3` decrease by `5t` from 29356.  Hence p-block feasibility
allows `t<=5871`.  On an active h-block, cells with `kappa=3` stay exactly at
2, while cells with `kappa=-2` increase by `5t` from 58357.  Hence h-block
feasibility allows `t<=1435`.  The combined preregistered ray therefore has

```
0 <= t <= 1435.
```

Inactive coarse blocks remain unchanged.  This deliberately stops preserving
the old coarse p/h marginals; it remains an explicit symmetric rational
960-step graphon with unit fine masses.

### Exact prediction and cheapest falsifier

Every affected fine-block numerator is affine in t, so the ordered
monochromatic K4 numerator has degree at most six.  Reuse the fixed compressed
typed-kernel histogram/signature of the audited parent and obtain seven exact
raw numerators at distinct feasible t values.  The six-edge product proves the
degree bound; pass `degree_bound_proven=True`, interpolate the exact polynomial,
and check at least one additional coordinate.  Exhaustively minimize its 1,436
integer values.

Prediction: the exact minimum occurs at nonzero t and improves the audited
parent.  Falsifier: the exact polynomial is minimized at t=0.  Only after a
strict prediction should one explicit candidate be materialized and sent to
the compressed candidate-bound Lean audit.

This is one boundary-face direction, not a kernel/seed sweep.  If supported,
the next refinement is separate `t_p,t_h`; if unsupported, do not enlarge it
without inspecting the exact derivative and degree contributions.

Coordination update: the latent-precision lane independently confirmed these
bounds and ranks separate `t_p,t_h` coordinates above the tied ray.  That lane
owns the approved independent face screen after its CPU slot releases; do not
duplicate it here.  The tied ray remains the smallest one-dimensional
falsifier if a separate control is later useful.

## Alternative: per-edge amplitude KKT screen

For every active coarse edge, hold all other amplitudes and phases fixed and
exactly minimize its own amplitude over the appropriate p/h interval.  Factor
signatures already retain repeated occurrences of the same coarse edge, so an
edge coordinate may enter a motif with powers greater than one.  A full exact
coordinate sweep would determine whether any active edge prefers moving off
its class boundary.  No improving coordinate is only a restricted KKT-style
negative, not joint amplitude optimality.

This is ranked second because the class amplitudes' boundary collision already
suggests a coherent mean/amplitude trade rather than isolated edge exceptions.

## Other freedoms and why they are later

- **Unequal latent weights:** changes the centering equations, normalization,
  and coarse sampling masses simultaneously.  It is genuine but requires a new
  weighted typed evaluator and is not the cheapest discriminator.
- **A different/noncentered kernel:** unrestricted kernel search conflates
  several mechanisms.  The boundary ray above is the minimal noncentered
  deformation predicted by the two active constraints.
- **More phase sweeps at fixed representation:** retired at this checkpoint;
  H-F2-01D reached a zero-move exact phase and coordinate-amplitude fixed point.

## Evidence and realization boundary

The polynomial or histogram screen is search evidence.  Promotion still needs
an explicit candidate hash and fresh native candidate-to-histogram binding plus
Lean exact-`Nat` arithmetic.  Standard conditionally independent-edge blow-up
realization applies verbatim to any resulting symmetric step matrix whose
entries stay in `[0,Q]`; shifting coarse means is irrelevant to validity.  The
formal lane confirmed the remaining caveats: diagonal matrix entries describe
edges between distinct vertices within one fine class, actual vertex collisions
are lower order, equal-mass normalization remains `960^4 Q^6`, and the old
centered sparse coefficients cannot be reused for this noncentered line.
