# Restart checkpoint — latent sign splitting

User requested a stop/restart at approximately20:00UTC on2026-09-27. No new
research should start until renewed session coordination. All algebraic jobs,
including the latent checker, have finished and been reaped. No active PID.

## Completed bounded H-ALG-008

Start with the simple192-block rational graphon in
`reports/literature-simple-graphon-001/graphon-candidate.json`, denominator41.
Split every block into two equal ± types and set

    P'[(i,s),(j,t)] = P[i,j] + epsilon*s*t*C[i,j],

where C is1 on fractional off-diagonal blocks and0 elsewhere. Independent
type signs annihilate all perturbation edge subsets except Eulerian subsets
of K4: the four triangles and three four-cycles. Thus exactly

    F(epsilon) = F(0) + A*epsilon^3 + B*epsilon^4.

Let d be the probability denominator and n the original block count. The
implementation returns Aint=A*n^4*d^3 and Bint=B*n^4*d^2, so at epsilon=q/d,

    F(q/d)-F(0) = (Aint*q^3+Bint*q^4)/(n^4*d^6).

The quartic sum explicitly retains repeated base indices. Discarding them
would give an incorrect coefficient; independently sampled latent types remain
independent even when their base labels agree. Cubic coefficient sums1152
fractional base triangles. Aint=1634522112; Bint=403246656. Analytic stationary
grid coordinate is -2128284/700081, so q=-3 is the selected original-grid value.

Result: epsilon=-3/41 yields384 blocks and exact density

    12357246284425/410008607391744
    = approximately0.030138992356856135.

This improves the simple parent0.03013899413358829, but **does not beat** the
separate refined/precision graphon incumbent. It supports latent correlation as
a new mechanism; it is not the strongest current bound or a novelty claim.

Six tiny literal tuple tests (n2 or3, both signs, including a triangle-free
support with nonzero quartic contribution) agree with the expansion. The full
384-block candidate receives an independent exact ordered-index C++ recount.
The prior checker has no192-block hard limit. Before using it, the total bound
2*384^4*41^6=206565616472819761152 is checked below2^127, and its long-long pair
products41² below2^63. All probability entries stay in[0,41]. Full count agrees
with expansion. Whole experiment took3.90s, including verification.

Artifacts: `reports/pilot-algebraic-latent-split-001/graphon-candidate.json`,
`expansion.json`, `report.json`, source snapshot, copied checker binary/source.
Candidate SHA256:
`089d704a76f3ea6b89c9186e290497a084d405b7221201da968c488821dbb494`.
Implementation: `experiments/algebraic/latent_split.py`.

Evidence: independent exact C++128 recount and tiny ordered-tuple tests; no Lean
certificate or formal general graphon realization theorem. The standard
independent-edge graphon realization argument still applies to this rational
step matrix, but must remain distinguished from the computational count.

## Concrete continuation, only after restart authorization

Read `research/RESUME.md` first for coordinator state and current strongest
graphon. Reuse this exact expansion implementation; generalize its hardcoded
parent/output paths using a fresh immutable run directory. Recompute A and B
for the strongest graphon and chosen symmetric support; do not reuse the simple
parent coefficients. Inspect whether the analytic admissible split improves
that parent. Recheck denominator growth and128-bit/long-long bounds before any
full checker call; larger denominators may require arbitrary-precision counting.
Do not blindly sweep epsilons: the exact cubic-plus-quartic polynomial gives
stationary points and probability-boundary endpoints directly.

Earlier finite construction work and its handoff are in
`research/algebraic-round.md` and `reports/pilot-algebraic-summary.json`.
