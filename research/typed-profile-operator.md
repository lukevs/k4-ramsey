# Exact typed-profile operator for off-diagonal refinement

Date: 2026-09-27. This sharpens H-ROOT-004 and corrects the earlier suggestion
that recursive off-diagonal refinement necessarily needs a large unknown
profile state. A fixed centered typed kernel has a small exact controlled
transfer. The ordinary 11-profile is not sufficient to recover the typed
coefficients across arbitrary support alignments, but on one fixed reachable
orbit its update is closed and affine.

## 1. Fixed data and recursive family

Let `I={0,...,191}` be the equal-mass coarse labels, `P_ij in [0,1]` the fixed
symmetric parent probabilities, and `tau(i,j)` a symmetric edge-type/support
label. Type 0 may mean inactive. Let `X` be a finite microtype alphabet with
probability weights `mu`, and for each active edge type let

    K_t : X x X -> R

be symmetric and row-centered:

    sum_y mu_y K_t(x,y) = 0        for every x.

At latent level `a`, every graphon point gets an independent microtype
coordinate `z_a in X`. For amplitudes `epsilon_1,...,epsilon_d`, define

    W_d((i,z),(j,z'))
      = P_ij + sum_(a=1)^d epsilon_a
                   K_(tau(i,j))(z_a,z'_a),

with `K_0=0`. Feasibility requires `0 <= W_d <= 1` pointwise. This includes
the retained binary split with `X={+1,-1}`, uniform weights, one active type,
and `K(s,t)=st`.

The support labels and kernel library are immutable parameters of the
operator. If a later rule changes support based on which descendant cells
remain fractional, that is a different typed state and the formulas below do
not silently carry across the change. Likewise, this note treats additive
independent-coordinate refinement; a nonlinear replacement rule needs its own
closure derivation.

## 2. Exact closure on four sampled vertices

Fix one of the 64 labeled red/blue graphs `H` on four positions. Its induced
density in `W_d` is the expectation of six factors, using `W_d` on red edges
and `1-W_d` on blue edges. Expand those factors and group perturbation edges
by their latent level.

For one level, the microtype expectation of a selected edge set `S subseteq
E(K4)` vanishes whenever `S` has a degree-one vertex: integrate that vertex
first and use row-centering. The nonempty simple subgraphs of `K4` with no
degree-one vertex are exactly

- the four triangles, with 3 edges;
- the three four-cycles, with 4 edges;
- the six copies of `K4` minus one edge, with 5 edges;
- `K4`, with 6 edges.

Two nonempty members of this list cannot be edge-disjoint. Indeed, each has
at least three edges; two disjoint ones would both have to be 3-edge triangles,
but the complement of a triangle in `K4` is a star, not a triangle. Since an
edge factor can select only one latent level, at most one level can occur
nontrivially in a surviving monomial.

Consequently there are fixed 11-component vectors
`U_3,U_4,U_5,U_6`, determined by `(P,tau,K,mu)`, such that the complete
unlabeled induced four-profile satisfies the exact identity

    v_d = v_0 + U_3 S_3(d) + U_4 S_4(d)
                  + U_5 S_5(d) + U_6 S_6(d),                  (1)

where

    S_k(d) = sum_(a=1)^d epsilon_a^k.

The vectors are obtained by a finite sum over ordered coarse quadruples,
labeled target graphs `H`, and the leafless edge sets of size `k`:

    U_k[H] = sum_(i_1,...,i_4) sum_(S leafless, |S|=k)
               sigma_H(S)
               [product_(e notin S) baseFactor_H(P_e)]
               E_z product_(uv in S) K_(tau(i_u,i_v))(z_u,z_v),

with the common `192^-4` normalization. Here `sigma_H(S)` is `-1` to the
number of selected blue factors, and `baseFactor_H(p)` is `p` on a red edge
and `1-p` on a blue edge. This formula is the exact finite algorithm for the
operator; it includes repeated coarse indices.
The vectors are rational when the parent probabilities, type weights, and
kernel entries are rational.

For the rank-one Rademacher kernel `K(s,t)=st`, an edge-set moment vanishes if
any positional degree is odd. The 5- and 6-edge terms therefore vanish, and
(1) reduces to

    v_d = v_0 + U_3 S_3(d) + U_4 S_4(d).                       (2)

This recovers the cubic/quartic recurrence in `recursive-latent.md`.

## 3. Minimal dynamic state and transfer map

For a fixed `(P,tau,K,mu)`, a universal sufficient dynamic state for the full
four-profile is

    s_d = (S_3,S_4,S_5,S_6).

Adding a level of amplitude `epsilon` is the controlled affine update

    S_k' = S_k + epsilon^k,                k=3,4,5,6,           (3)
    v'   = v   + sum_(k=3)^6 U_k epsilon^k.                    (4)

The minimal linear state dimension needed to reconstruct every reachable
profile is

    rank{U_3,U_4,U_5,U_6} <= 4,

after quotienting moment directions with identical or zero profile effect.
This rank is also the affine-hull lower bound: four distinct sufficiently
small one-level amplitudes give a generalized Vandermonde span of the active
coefficient directions. Thus no smaller linear state reconstructs all profiles
on the generic fixed orbit.
For the retained binary split this rank is at most two; `(S_3,S_4)` is the
safe exact state until the two complete 11-vectors are computed and their
rank checked. For the scalar monochromatic objective, replace each `U_k` by
its scalar coefficient, though feasibility still needs separate state.

Thus the current 11-profile does close on a **fixed** reachable orbit:
equation (4) directly supplies its next value. It is an affine controlled
operator, not a homogeneous stochastic 11-by-11 matrix and not a
Perron--Frobenius iteration. The earlier categorical wording “no closed
operator on the untyped profile” was too strong.

For prescribed geometric amplitudes `epsilon_a=eta rho^(a-1)`, an autonomous
finite transfer uses

    (1,S_3,S_4,S_5,S_6,e_3,e_4,e_5,e_6),

where `e_k=epsilon_next^k`, with

    S_k' = S_k + e_k,
    e_k' = rho^k e_k.

The tail coordinates contract for `|rho|<1`, and

    S_k(infinity) = eta^k/(1-rho^k).

This is a closed convergence criterion usable for exact optimization. It is
not necessary, or correct, to search for a PF stationary vector of the
ordinary 11-profile for this additive family.

## 4. Exact feasibility state

Profile closure does not enforce `0 <= W_d <= 1`. For each coarse edge type
and base-probability class, track the attainable perturbation interval. If
level `a` uses kernel `K` and amplitude `epsilon_a`, its exact contribution to
the lower and upper endpoints is

    l_t(a) = min_(x,y) epsilon_a K_t(x,y),
    u_t(a) = max_(x,y) epsilon_a K_t(x,y).

Independence of the microtype coordinates makes all per-level choices
simultaneously attainable, so after `d` levels the exact interval is

    [L_t(d),R_t(d)]
      = [sum_a l_t(a), sum_a u_t(a)].

For every coarse pair of type `t`, require

    -P_ij <= L_t(d)       and       R_t(d) <= 1-P_ij.           (5)

These interval endpoints, grouped by identical `(P_ij,t)`, are the minimal
obvious exact feasibility state. A scalar norm budget is a safe relaxation.
For the common Rademacher support, (5) collapses exactly to

    sum_a |q_a| <= 14472,             epsilon_a=q_a/65536.

An infinite hierarchy is valid when the endpoint series converge and retain
the inequalities. Absolute summability of amplitudes is a simple sufficient
condition; it also gives uniform graphon convergence.

## 5. Why an untyped profile is not universally sufficient

Although a fixed orbit has the affine closure above, no update rule depending
only on the current untyped 11-profile can work uniformly across arbitrary
support alignments. Here is an explicit symbolic counterexample.

Take three equal coarse classes with zero diagonal and distinct fractional
off-diagonal probabilities

    P_12=a, P_23=b, P_13=c,

and let the fixed support mask `C` be the path with edges `12,23`. Apply one
rank-one Rademacher level `P+epsilon C st`. There is no cubic term because the
support has no triangle. A direct four-cycle enumeration gives raw ordered-sum
quartic coefficient

    B(P,C) = 24 - 12 c.                                      (6)

To see (6), each of the three positional `C4`s contributes the eight closed
four-walks in the support path. Their complementary matching factors sum to
`8-4c`, giving `3(8-4c)`. The graphon-density coefficient is
`(24-12c)/3^4`; the common normalization does not affect the comparison.

Now permute the labels of `P` while leaving the labeled mask `C` fixed so that
the probability on the missing support edge `13` becomes `b`. The old and
new probability graphons are isomorphic and therefore have identical complete
untyped profiles of every order, including the same 11-profile. Yet the next
quartic coefficient is

    B(P',C) = 24 - 12 b,

which differs when `b != c`. The missing information is the joint alignment
of `P` with `C`. If `C` is relabeled together with `P`, the update agrees, as
it should.

This counterexample supports the precise statement:

- untyped profile plus no construction metadata is not a universal state;
- fixed typed metadata plus the moment state (3) is closed;
- on that fixed orbit, the next untyped profile is given exactly by (4).

## 6. Optimization form for H-ROOT-004

For a fixed kernel library, H-ROOT-004 is a finite controlled moment problem,
not a stationary Markov-chain problem:

    minimize   L(v_0) + sum_(a,k) L(U_k^(theta_a)) epsilon_a^k
    subject to the exact interval constraints (5),

where `theta_a` selects a preregistered centered kernel type and `L` extracts
the `K4 + anti-K4` coordinate. If every level uses the same kernel, the
objective is separable in the amplitudes. For the retained binary kernel it
reduces to the already derived cubic/quartic resource-allocation problem.

The exact allocation proof now in `recursive-latent.md` solves that retained
fixed-support specialization: four equal integer amplitudes `q_a=-3618`
exhaust the exact budget `4*3618=14472` and globally minimize its separable
cubic/quartic objective, including against unequal finite and countably
infinite allocations. This is a terminal four-level, 3072-class specification,
not a PF fixed point. The allocation theorem is analytic; the resulting large
step graphon has not yet received its independent ordered recount.

The approach remains finite for a finite kernel library. Changing the support
as a function of descendant probabilities creates new edge types; closure then
requires adding those types and their feasibility intervals, rather than
pretending the old coefficients remain invariant.

## 7. Verification obligations

Before optimizing a new kernel:

1. validate row-centering with the actual microtype weights;
2. compute `U_3,...,U_6` by the typed formula and compare one- and two-level
   literal enumerations on tiny coarse matrices;
3. verify that the observed two-level profile equals the sum of independent
   level increments, directly testing the no-cross-level claim;
4. track exact interval feasibility, not only average preservation;
5. independently recount the selected finite refinement or limiting closed
   form without reusing the coefficient implementation as its checker.

This supplies the finite closure H-ROOT-004 needs while preserving the sharp
boundary between additive off-diagonal refinement and ordinary nested graph
composition.
