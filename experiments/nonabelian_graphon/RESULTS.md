# H-NAB-01 results

## Contract and exact reduction

The screened family is the full 128-parameter undirected stochastic Cayley
kernel on each of the three nontrivial groups `F2^6 semidirect C3`, one action
type for each `r=1,2,3` acted two-bit blocks. The exact ordered graphon objective
was evaluated by the left-translated `192^3` formula in `derivation.md`.

The tiny `A4 = F2^2 semidirect C3` oracle checked associativity, inverses,
noncommutativity, inverse symmetry, repeated indices, and equality of literal
`|G|^4` and translated `|G|^3` counts. Every optimized basin was rounded to
`Q=65536` and exactly recounted before selection.

## First screen

The deterministic screen completed in 16.0 seconds. Constant and character
starts returned to the weak-local-common `1/32` basin. The invariant-quadratic
start found:

| acted blocks | best exact rounded density |
|---:|---:|
| 1 | 0.03014021334622540 |
| 2 | 0.03014062101885995 |
| 3 | 0.03116140389229423 |

The `r=1` result beat its same-group structured binary control
`0.03064416956018519`, showing a genuinely fractional basin, but it remained
above the campaign incumbent. Its gradient was still `1.39e-6`, so it was not
treated as a converged negative.

## Causal continuation

One continuation from the frozen, exact-rounded `r=1` probabilities converged
after 79 further L-BFGS iterations to gradient norm `9.96e-11`. The explicit
192-step candidate is

`reports/nonabelian-cayley-r1-continuation-001/graphon-candidate.json`

with SHA-256
`0fb88f4a60b1459a5c7f9a3a3b0707237c1a743aa0ead49ec1f95f0214209895`.
Its translated exact density is

`8252429612735690156467948788193 /
273812529649297550723287892361216 = 0.030138977289700743`.

The unrounded continuous objective was `0.030138977289646214`; it must not be
reported as the explicit rational candidate's density.

This is about `1.79e-13` below the older literature precision parent but
`7.37243e-8` above the independently checked incumbent. The affine-subspace
diagnostic attributes `0.00077300388` to rank-at-most-two tuples within a
single `V` coset and `0.00139597755` to rank-three tuples, only about 7.2% of
the total. The normal elementary-abelian subgroup is not dominating this
density in the crude sense tested.

## Structural falsifier: the twist cancels

The final rounded kernel is exactly invariant under the order-three action:
`p(A v,t)=p(v,t)` for all 192 group elements. Consequently

`p((v,t)^-1(w,s)) = p(A^-t(v+w),s-t) = p(v+w,s-t)`.

Therefore its explicit matrix is also an abelian Cayley graphon on the direct
product `F2^6 x C3`. It does **not** factor through the order-48 abelianization:
all 192 tests of invariance under adding the acted two-bit commutator subspace
fail. Rather, the nonabelian semidirect twist is invisible because the kernel
itself is action-invariant.

The orbit numerators take only five values: 64 at `65536`, 51 at `0`, six at
`14471`, six at `14472`, and one at `30522`. This recovers the known
quadratic/two-parameter shape with a small orbitwise integer split. The tested
basin therefore does not support a nonabelian-specific mechanism.

Latent-group recovery independently shows that the archived 192-class row order
has 24 directed orbitals and is presently known as a Schreier action, not a
regular Cayley coordinate system. Accordingly, “recovers” here means only the
probability pattern/near-identical objective; no row-wise identification with
the archived construction is claimed.

## Corrected action-breaking screen

The first four starts were all action-invariant, so deterministic optimization
could not leave the abelian direct-product subspace. `H-NAB-01C` corrected this
formal mismatch with one preregistered finite-amplitude non-class matrix-
coefficient perturbation for each exhaustive action type. Its joint success
criterion required both an exact gain over the matched invariant control and a
nonzero rounded action-invariance residual.

| acted blocks | exact density | rounded action violations | interpretation |
|---:|---:|---:|---|
| 1 | 0.030140174736420576 | 10 | nonabelian residue survives, but loses to stationary invariant control |
| 2 | 0.030140174736792362 | 0 | improves an underoptimized control, but collapses to the abelian subspace |
| 3 | 0.030310686879586646 | 84 | strongly nonabelian and substantially worse |

The joint criterion failed in every action type. This is a causal negative for
the tested induced-matrix-coefficient branch, not for all action-breaking starts.

## Shared-engine local curvature test

As a distinct local question, the stationary `r=1` candidate was sent through
the reusable relation engine with all 13 strictly fractional inverse relations
free and all 115 deterministic boundary relations frozen. The exact parent gate
matched the independent candidate recount. On this 13-dimensional face the
minimum Hessian eigenvalue was

`+5.817020891888041e-6`

with eigenpair residual `2.24e-19`. Thus there is no negative-curvature escape,
including an action-breaking one, in this specific fixed-boundary local face.
The continuous Newton value was about `3.41e-14` below the rational parent, but
rounding at `Q=65536` returned exactly the original probabilities and exact
objective. The rounded kernel retained zero action-invariance violations.

Evidence: `reports/relation-engine-nonabelian-r1-fractional-free-001/report.json`
(SHA-256 `7b1da7eb3e2f4f54de4f330d370fdb0f9f95d2ef1e6e59cf21f9528583bede6a`).
This is only second-order locality with deterministic boundaries fixed; it does
not exclude boundary release, a different basin, or the full Cayley family.

## Decision

Status: **unsupported in the tested motivated basins**, not retired and not a
global lower bound for the 128-dimensional family. The three action types are
exhaustive, but the tested deterministic starts are not exhaustive optimization.
Reopen only with a new coupling mechanism (or a Schreier/orbital graphon), not
another unrestricted binary or amplitude sweep.

No novelty or record claim is made. A fresh generic candidate-only U256 recount
passed the exact fraction above in
`reports/graphon-nonabelian-cayley-r1-continuation-direct-u256-001` (report
SHA-256 `a5d72cbf873361879f74ca8c25807f31bd7eae0d7184e0190387ac4553c19b82`).
The explicit-matrix raw counts are red
`1624865133768359556289729165221101568`, blue
`1620122228833117584275971785476997120`, total
`3244987362601477140565700950698098688`, with denominator
`107667467658578185705208371882707910656`. The smaller search-report counts are
the left-translated census and differ by the expected factor 192.
