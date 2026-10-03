# A ten-vertex constraint and its free-completion obstruction

2026-09-29. Continuation of `global-lower-bound-transfer-audit.md` under
`global-anchor-pilot-contract.md`. Own derivation; no novelty claim.

## Explicit universal constraint

Let W be any symmetric measurable [0,1] graphon. Draw six independent roots
r0,...,r5. Let tau(r) be the probability their induced graph is the labelled
five-cycle 01,12,23,34,40 with vertex 5 isolated: multiply W on those five
edges and 1-W on the other ten pairs. It is nonnegative. No assumption is
made that W contains such a pattern with positive probability.

Define, with all integrations against the graphon's probability measure,

    psi_r(z) = W(r0,z)+...+W(r4,z)-5 W(r5,z),
    L(r) = (integral psi_r(z) dz)^2,
    R(r) = integral W(z,w) psi_r(z) psi_r(w) dz dw.

The 3 by 3 matrix

    M = integral tau(r) (1,L(r),R(r))(1,L(r),R(r))^T dr

is positive semidefinite. For any real coefficients b, its quadratic form
is the integral of tau times (b0+b1 L+b2 R)^2. This proves the assertion
without regularity, Clebsch structure, or assumptions about optimal graphs.

The blue analogue of R is L-R, so adding it as a fourth feature alone
does not add another direction. The Clebsch connection is the choice of
the six-root identifying pattern; the contrast psi is a simple heuristic
choice, not a proved optimal feature or a reconstruction of all 16 vertices.

These are ordinary rooted flag squares. The point of the pilot is selecting
and checking one concrete higher-order block, not inventing a new method.

## The ten-vertex dependence does not cancel

M00 uses six vertices, M01 and M02 at most eight, and the lower 2 by 2 block
at most ten. Consider M22. Expanding its graphon products into ordinary
homomorphism densities, its maximum edge degree is 21: the complete graph
on the six roots (15 edges), two disjoint outside edges, and four attachments
of the outside endpoints to roots.

One surviving graph H is K6 with two triangles attached at the same core
vertex, adding four outside vertices. It has ten vertices, 21 edges and
degree sequence (9,5,5,5,5,5,2,2,2,2). The leading term of tau has sign
(-1)^10=+1. Writing a=(1,1,1,1,1,-5), the coefficient of t(H,W) is

    sum_i a_i^4 = 5+625 = 630.

To obtain this graph all four attachments must use the same root. All
6^4=1296 attachment choices were checked; exactly six contribute. Terms
using fewer edges from tau cannot cancel a 21-edge graph.

This is genuine dependence beyond a linear combination of densities of
graphs on at most nine vertices. One elementary justification: evaluate
on step graphons with ten variable class masses and variable edge entries,
and homogenize smaller vertex counts by multiplying by total mass to reach
degree ten. A monomial with ten distinct class masses and H's edges cannot
come from an at-most-nine-vertex graph padded with isolated vertices: every
vertex of H touches an edge. Its coefficient is nonzero. This argument
does NOT establish nonredundancy after projection of a larger moment SDP.

## The important obstruction: an isolated block does nothing

Suppose an order-nine solution supplies the first row (a,b,c) of M, with
a>0, and we introduce its three lower-block entries as otherwise free new
moments. Then

    M = (a,b,c)^T (a,b,c) / a

is always a positive-semidefinite completion with the required first row.
Thus the additional block, by itself, excludes no such solution. If a=0,
PSD requires b=c=0; the statement above deliberately excludes that boundary.
In an actual graphon zero anchor density indeed makes the entire block zero.

The completion can violate bounds or identities that real graph moments
must satisfy. That is exactly why those additional conditions are necessary.
Real higher-order moments must share variables across all isomorphic graph
expansions, obey nonnegative induced-density constraints, and have marginal
densities compatible with the order-nine data. Other overlapping Gram blocks
then act on the same variables. A collection of separate blocks with separate
free moments would repeat the same problem.

Consequently a ten-vertex square cannot simply be evaluated on a nine-vertex
moment vector: some of its inputs are absent. The correct experiment is an
extension-feasibility problem, holding the old moments fixed and asking whether
consistent higher moments exist. This sharpens the earlier next-step plan.

## Validation and artifacts

`experiments/clebsch_bowl/global_anchor_pilot.py` uses only Python's standard
library and exact fractions. Four weighted graphons include a constant kernel,
a fractional irregular two-class kernel, a clique-plus-isolates kernel and
a complete bipartite kernel. Repeated class indices and nonzero diagonals are
allowed, as required for graphon integration.

For each, grouped integration of the rooted features agrees exactly with a
literal sum over all ten latent vertices for M22. All seven principal minors
of the 3 by 3 matrix are nonnegative. The fractional example has a strictly
positive M22; these are not exclusively zero checks. Two exact examples also
check the rank-one free-completion construction. The general claims above
are supported by their analytical proofs, not inferred from finitely many tests.

Receipts:
- `reports/global-anchor-pilot-001/check.json`: initial constraint checks,
  including the source hash at that point.
- `reports/global-anchor-pilot-001/check-with-completion.json`: final checks,
  including the completion obstruction and updated source hash.

Both runs finished in under one second. No compute remains running.

## Decision

H-GA1 is supported: an explicit universally valid block contains a nonzero
ten-vertex term. The proposed isolated-block shortcut is retired: it has a
universal free completion for positive anchor mass.

No higher-order extension SDP was built or solved, no N=9 artifact was
obtained, and neither nonredundancy of a coupled SDP nor an improved lower
bound has been established. Further search of indexed author pages did not
retrieve the missing solution. The previously inspected KPS certificate
directory remains about other multiplicity objectives.

The next meaningful computational target is a *coupled* sparse extension
with shared graph-density variables and checked marginal constraints, first
validated at a small hierarchy level where the full extension can serve as
a control. The real N=9 test additionally needs the saved moments or a
reproduced baseline. This is more substantial than appending a few inequalities;
the obstruction above explains why the simpler experiment would be misleading.
