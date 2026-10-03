# Induced-four profile constraints for the XOR gate

Date: 2026-09-27. This note records only the finite equations needed for the
profile-guided screen. All vertex samples are iid, so repeated step-class
indices are included automatically.

## Labeled convolution and unlabeled compression

For a graphon `W`, let `p_W(s)` be the probability that its induced red graph
on four ordered sampled vertices has labeled edge set `s subset E(K4)`. If
`G` and `H` are sampled independently on a product vertex space, their XOR
graphon satisfies

    p_XOR(r) = sum_s p_G(s) p_H(r xor s),

and therefore

    c4(G XOR H)
      = sum_s p_G(s) [p_H(s) + p_H(complement(s))].          (1)

Let `q_i` be total probability of unlabeled four-graph class `i`, and let
`n_i` be its number of labeled realizations. Vertex exchangeability makes
every labeled realization in a class equiprobable, so (1) becomes

    c4(G XOR H)
      = sum_i qG_i [qH_i + qH_complement(i)] / n_i.          (2)

In the class order

    empty, K2, 2K2, P3+I, K3+I, K1,3, P4,
    C4, paw, K4-e, K4,

the labeled multiplicities are

    n = [1, 6, 3, 12, 4, 4, 12, 3, 12, 6, 1].

For a self-product, group the 64 labeled patterns into 32 complementary pairs:

    c4(G XOR G)
      = sum_{pairs {s,~s}} [p_G(s)+p_G(~s)]^2 >= 1/32.      (3)

Equality requires every complementary pair to have mass `1/32`. Thus the
self-XOR family cannot reach the current density below `1/32`; only a
heterogeneous product merits screening.

## Linear statistics of the eleven classes

For an unlabeled graph `F`, write:

- `e(F)` for its edge count;
- `d(F)` for its number of two-edge matchings;
- `w(F)=sum_v binom(deg_F(v),2)` for adjacent red-edge pairs;
- `r3(F)` for its number of degree-three vertices.

In the class order above:

| statistic | empty | K2 | 2K2 | P3+I | K3+I | K1,3 | P4 | C4 | paw | K4-e | K4 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `e` | 0 | 1 | 2 | 2 | 3 | 3 | 3 | 4 | 4 | 5 | 6 |
| `d` | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 2 | 1 | 2 | 3 |
| `w` | 0 | 0 | 0 | 1 | 3 | 3 | 2 | 4 | 5 | 8 | 12 |
| `r3` | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 2 | 4 |

Define the three degree moments

    mu = sum_F q_F e(F)/6,
    A  = sum_F q_F w(F)/12,
    S  = sum_F q_F r3(F)/4.

If `d_W(x)=integral W(x,y)dy`, then these are exactly

    mu = E[d_W(X)],   A = E[d_W(X)^2],   S = E[d_W(X)^3].

## Necessary realizability constraints

The minimal probability constraints are

    q_F >= 0,                    sum_F q_F = 1.              (4)

Because the edges `12` and `34` use disjoint latent variables, they are
independent even when `W` is a nonconstant graphon. Hence

    sum_F q_F d(F)/3 = mu^2.                                  (5)

The analogous blue identity is redundant: it follows from (5) and the edge
marginal. On a fixed-`mu` slice, (5) is a linear equality.

Degree variance gives the stronger immediate fixed-slice inequality

    A >= mu^2.                                                  (6)

It implies Goodman because the monochromatic triangle density is

    t(K3,W)+t(K3,1-W) = 1 - 3mu + 3A >= 1/4.                  (7)

Thus (6) should replace, or at least accompany, a standalone Goodman cut.

The first nontrivial flag-moment constraints using only four vertices are

    [ mu       A ]             [ 1-mu   mu-A ]
    [ A        S ] >= 0,       [ mu-A   A-S  ] >= 0.          (8)

They are the Gram matrices
`E[d(X) (1,d(X))^T(1,d(X))]` and
`E[(1-d(X)) (1,d(X))^T(1,d(X))]`. Equivalently,

    mu*S >= A^2,
    (1-mu)*(A-S) >= (mu-A)^2,                                  (9)

with the nonnegative diagonal conditions. For a pure LP, every fixed rational
vector `(a,b)` supplies the valid linear cuts

    a^2 mu + 2ab A + b^2 S >= 0,
    a^2(1-mu) + 2ab(mu-A) + b^2(A-S) >= 0.                    (10)

A small preregistered bank of rational vectors gives a cheap polyhedral outer
approximation; retaining (8) directly gives the exact two-by-two SDP/SOCP
condition.

A stronger still-cheap two-flag constraint is available. For root-edge color
`c in {0,1}` and adjacency words `alpha,beta in {00,01,10,11}`, set

    M_c[alpha,beta]
      = P(A12=c,
          (A13,A23)=alpha,
          (A14,A24)=beta),                                    (11)

leaving `A34` unspecified. Conditional on the two root latents, vertices 3
and 4 are independent, so

    M_0 >= 0,       M_1 >= 0.                                  (12)

Every entry is linear in the eleven `q_F`. It can be generated without a
symbolic derivation: for each fixed representative `F`, enumerate all 24
vertex permutations, count those satisfying the five statuses in (11), and
use that count divided by 24 as the coefficient of `q_F`. These two four-by-four
PSD matrices are necessary, not sufficient, for graphon realizability.

## What an LP conclusion means

With an actual partner profile fixed, (2) is linear in the candidate profile.
Minimizing it over (4)--(7), or over any collection of valid linear flag cuts,
is a rigorous **lower bound** because the relaxation is an outer approximation
to realizable graphon profiles. A lower bound above a target rigorously rejects
that target for the slice. A low relaxed optimum does not construct a graphon;
it is only a screen.

For a global claim, fixed-`mu` slices must cover the continuum of `mu`
rigorously. Sampling a grid of `mu` values is only heuristic. Likewise, if both
factor profiles vary, (2) is bilinear: only a globally certified optimization
over the two outer relaxations is a rigorous lower bound. Alternation or local
bilinear optimization remains proposal evidence.
