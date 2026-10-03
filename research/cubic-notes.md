# H9: exact cubic star subcubes

2026-09-27. Motivation: cached16-per-color pair descent reached a restricted
plateau at numerator10486383582 after25 single flips and82 pair moves. A
selected incident-edge set permits at most three free edges in any K4;
the exact restricted objective is cubic rather than general degree six.

For three free edges from center u to leaves v,w,x, the cubic coefficient
vanishes unless triangle vwx is monochromatic, of color c. Otherwise it is
24 times the product over the three free edges of (1-2*r_i), where r_i is1
when that edge currently matches c. The coefficient is therefore ±24.
The lower-order coefficients are the previously validated cached single
deltas and exact shared-center mixed differences. This is our direct finite
difference derivation, with no novelty claim.

Prototype: choose12 incident edges, balanced between current colors, with
low-cost and randomized leaf choices. Enumerate all4096 assignments using
Gray codes. Maintain first and second discrete derivatives, updating those
affected by the toggled variable; cubic coefficients remain constant.
An exhausted solve certifies exactly its selected subcube, not all stars.
Deadline interruption returns the best feasible assignment explicitly marked
incomplete. Every accepted prediction is checked against sequential current
cached deltas and then full native recount; the runner checks the final
artifact independently with compiled Lean.

Prediction: some selected cubic subcube improves the star-pair plateau, via
a coordinated move unavailable to the tested single/pair neighborhoods.
A gain must be inspected for number of actual flipped edges: a one/two-edge
gain only shows that previous candidate restrictions missed it, not evidence
of genuinely three-or-more-edge coordination.

Validation: all64 four-vertex graphs, all8 assignments of a3-edge star,
against a literal ordered-four-tuple oracle. Generic random8-variable cubic
objectives check Gray-code minima against exhaustive direct polynomial sums.
These tests validate code on finite fixtures; they are not a formal theorem
or proof of global optimality.

## First bounded screen

`reports/pilot-h9-cubic-001`: size12, one random leaf per color, seed9,
90-second search from the independently checked selected-pair plateau
N=10486383582. The final artifact was independently recounted by Lean and
unchanged (gap117214 numerator units above McKay). No improving selected
star subcube was found. The method and Gray-update implementation received
a separate read-only mathematical/code review from the structural worker.

Decision: unsupported in this tested selection regime; retain the exact
compiler/solver, but rotate to a genuinely different family (diagonal/internal
cluster colors) rather than spend this round on more edge-neighborhood tuning.
This does not establish exhaustion of all star subcubes or any global optimum.
