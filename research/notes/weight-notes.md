# H11: fractional pair mass transfers

2026-09-27. F3 representation/weights family, distinct from the failed unit-step
clone screen. A positive t=1 clone cost does not rule out a negative small-t
direction. No weighted result is promoted through the unit-weight checker.

For a blue-diagonal graph, let d_i and T_i count blue neighbors and blue
triangle incidences, and let K_i count both-color K4 incidences. Transfer mass
from u to v: w_u=1-t, w_v=1+t, other weights1; total mass remains n.
Let e indicate that uv is blue, h be the number of blue triangles containing
uv (zero if uv is red), and q be the number of monochromatic K4s containing uv.
The exact numerator difference is A*t+B*t²+C*t³+D*t⁴, with

    A = 28*(d_v-d_u)+48*(T_v-T_u)+24*(K_v-K_u)
    B = 12+18*(d_u+d_v)-48*e+12*(T_u+T_v-5*h)-24*q
    C = 4*(d_v-d_u)
    D = 2-2*e.

Derivation: partition repeated-index types. Vertex loops contribute
12*t²+2*t⁴. A blue edge incident to one changing vertex has polynomial
4*w³+6*w²+4*w, while the uv edge contributes -12*t²-2*t⁴ if blue.
A blue triangle with one changing vertex contributes12*(w²+2*w);
with both changing vertices it contributes36*(1-t²). Distinct K4 terms are
multilinear:24*t*(K_v-K_u)-24*t²*q. Collecting gives the formula above.

Per-vertex K_i is extracted by temporarily isolating vertex i in red,
summing exact current-state native edge deltas, and restoring it. This is
checked by ΣK_i=4*(K4_red+K4_blue), unchanged adjacency, and tiny literal
weighted tuple tests. Pair q uses induced-edge counts on the common
neighborhood in the color of uv.

The cheap screen ranks the first-order gradient g_i=28*d_i+48*T_i+24*K_i,
selects high-gradient donors and low-gradient recipients, and exhaustively
tests rational t on a fixed grid in[0,1) for those pairs, excluding the zero
donor weight at t=1. This is exact on
the selected finite grid, not a complete optimization of all weights.

Validation: every four-vertex graph, every unordered vertex pair, and
t∈{-1,-1/2,0,1/2,1}, compared with literal weighted ordered quadruples.
The grid optimizer is separately checked by direct rational polynomial sums.

Prediction: the symmetric published seed has zero first-order differences,
but an edge-refined asymmetric incumbent may admit a strict fractional gain.
If detected, stop promotion and implement a separate versioned independent
weighted checker; leave the frozen unit-weight/blue-diagonal checker untouched.

## Initial positive screen — development evidence only

`reports/pilot-h11-weights-001`: on the retained768-vertex incumbent,576
high-gradient/low-gradient pairs were screened on a1/1024 grid. Best transfer:
t=1/16 from vertex392 to221; derived numerator decrease2575385/1024,
approximately2515.0244 fixed-768 numerator units. Its exact derived density is
10738054212583/356241767399424. The positive integer weights are equivalent to
15 at392,17 at221, and16 elsewhere. No zero or negative weight is present.

This is **not independently checked weighted progress yet**. Only the
unit-weight parent received the existing Lean recount. The emitted weighted
candidate must pass a separately versioned general-weight checker before
promotion. The screen found a strict gain invisible to the failed integer
clone experiment, supporting the distinction between coarse unit transfers
and continuous mass perturbations.

The initial screen's source snapshot also tested t=1 endpoints; its winning
candidate has strictly positive weights. Subsequent source excludes t=1
from admissible candidate selection. Literal polynomial tests retain endpoint
cases as algebraic checks, not positive-weight witness claims.

## Independent weighted verification

The initial candidate has now passed a **separate full weighted recount**:
`reports/pilot-h11-weights-001/weighted-verification-v1.json`. The versioned
`WeightedV1` Lean module counts repeated-index partition contributions and
weighted four-cliques directly using byte-mask weight-sum tables. It does
not evaluate the pair-transfer quartic, and the original unit-weight checker
was not changed. Its actual serialized total mass is786432, numerator
11529897916429754171392, denominator382511685112441262309376, yielding exactly
the predicted reduced density. Recount took2.07seconds.

The new Lean tests compare all64 four-vertex graphs with all16 binary positive
weight patterns against literal ordered tuples, plus varied weights and
word-boundary all-blue templates. Python wrapper tests cover independent
literal counts, big integers, normalization and invalid weights. Evidence is
compiled Lean execution with fixture tests, not a kernel-only proof of the
general counting identity or asymptotic lifting theorem.

Separately, a later unit-weight tabu incumbent improved by6210 from the old
parent, exceeding this weighted gain of2515.0244. Therefore this first
weighted candidate establishes the mechanism but is **not** the global best
retained construction. Candidate verification and incumbent promotion are
different decisions.
