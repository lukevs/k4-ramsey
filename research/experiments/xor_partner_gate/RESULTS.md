# H-XOR-PARTNER-001 result

The archived XOR screens did not optimize a heterogeneous partner against the
competitive 192-class `e26` graphon. They used small finite factors, or a fixed
`K4 XOR M4` factor with heterogeneous recursive rules. The requested objective
change was therefore not previously covered.

The final development report is
`reports/xor-partner-e26-gate-003/report.json`. It verifies that the eight
stored action generators preserve every rational probability entry and act
transitively, then fixes one sampled class and histograms `192^3` triples. This
gives the exact 64 labeled coordinates and their 11 unlabeled orbit sums while
retaining repeated-class and diagonal graphon semantics.

For independent XOR factors,

```text
c4(G XOR H) = sum_s p_G(s) (p_H(s) + p_H(complement(s))).
```

The exact `e26` self-product is about `0.03134167519`, consistent with the
complement-pair Cauchy floor `1/32`; it is a control, not a candidate. None of
the normalized archived order-at-most-five or nested partner profiles has
standalone monochromatic density at most `0.031`, so this bank supplies no test
in which both factors are competitive. This restriction is the stated scope of
the gate, not a necessary condition for an arbitrary XOR partner to improve.

An exact linear outer relaxation of that two-competitive-factor subclass uses
nonnegativity, normalization, Goodman's monochromatic-triangle inequality, and
the incumbent upper bound on the partner. It has lower value about
`0.02940360346`. Its optimizer puts all mass on the two-adjacent-edge type; this
is unrealizable because its edge density is `1/3` but it gives probability zero
to two disjoint red edges, whose graphon probability must be `(1/3)^2`. Thus it
exposes weak realizability constraints, not a candidate or a predicted gain.

Decision: do not launch a large continuous profile optimizer from this gate.
The cheapest discriminating continuation is either a small flag-PSD
realizability relaxation or an exact profile extraction for one already
competitive, structurally distinct archived graphon followed by a single XOR
evaluation. No novelty or family-exhaustion claim is made.
