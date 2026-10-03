# H-LAT-R: recursive latent-sign refinement

Date: 2026-09-27. This is a derivation-only follow-up to the exact run in
`reports/latent-precision-002`; no CPU experiment was launched. The objective
is to decide whether its binary latent split can be coherently iterated and
whether the iteration has an analogue of a nested-profile fixed point.

## Construction and exact recurrence

Let `P` be the retained 192-class probability matrix and let `C` be one on all
1248 fractional unordered blocks and zero elsewhere. For independent latent
sign coordinates, define

    W_r((i,s),(j,t)) = P_ij + C_ij sum_{a=1}^r epsilon_a s_a t_a,

where `s,t` lie in `{+1,-1}^r`. All `2^r` latent types inside a base class have
equal mass. This is the coherent iteration of the successful one-level split;
it is additive across latent coordinates, rather than a fresh use of the
simple-case coefficients.

Consider any labeled induced four-vertex graph. After choosing whether each
of its six factors is `W_r` or `1-W_r`, expand the product. Averaging a latent
coordinate kills a selected edge set unless every one of the four positional
vertices has even selected degree. The only nonempty Eulerian subgraphs of
`K4` are its four triangles and three four-cycles. Moreover, two nonempty such
subgraphs cannot be edge-disjoint: two triangles share an edge, two four-cycles
share two edges, and a triangle cannot fit in the two-edge complement of a
four-cycle. Since each product edge can be assigned to only one latent level,
at most one level can occur nontrivially in any surviving monomial.

It follows for the complete labeled profile, and hence for its 11-dimensional
unlabeled orbit sum, that

    v_r = v_0 + U sum_a epsilon_a^3 + V sum_a epsilon_a^4.        (1)

The vectors `U,V` depend on the typed pair `(P,C)`, but do not change with `r`.
Repeated base-class indices cause no exception: the four sampled latent type
vectors are independent positional samples even when their base labels agree.

For the monochromatic `K4` functional, let `Q=65536`, `n=192`, and write
`epsilon_a=q_a/Q`. The completed high-precision run recomputed

    Aint = 6529004621732118528
    Bint = 1030493629601280.

Therefore the exact scalar recurrence is

    F_r = F_0
          + [Aint sum_a q_a^3 + Bint sum_a q_a^4] / (n^4 Q^6).   (2)

In normalized epsilon coordinates, the invariant coefficients are
`alpha=Aint/(n^4 Q^3)` and `beta=Bint/(n^4 Q^2)`. If they are recomputed as raw
integer coefficients on the `2^r n`-class matrix, both multiply by `16^r`;
the larger class normalization cancels the same factor. Combinatorially, each
base triangle has `8^r` latent lifts and the fourth-index sum contributes
another `2^r`, while the four-cycle sum directly has `16^r` lifts.

This establishes coefficient rescaling only for the lifted support `C`. It is
not a license to reuse the coefficients after changing the support rule.

## Probability bounds and support changes

For a fixed active base block, all sign products can align. Thus admissibility
is exactly

    sum_a |q_a| <= min_{C_ij=1} min(P_ij, Q-P_ij) = 14472.       (3)

The successful one-level optimum `q=-4752` may consequently be repeated only
three times (`14256 <= 14472`); a fourth equal copy is invalid. Constant
nonzero amplitude therefore does not define an infinite recursion or fixed
point.

As long as inequality (3) is strict, all descendants of an active block stay
fractional, so "all fractional blocks" is exactly the complete latent lift of
the original support. At equality, some descendants of a `P_ij=51064` block
hit probability one. A subsequent rule that automatically selects all and
only fractional entries would then drop those branches, creating new support
types and invalidating recurrence (1). No coefficient-invariance claim crosses
that boundary.

An exact infinite hierarchy is possible with shrinking amplitudes. If

    epsilon_a = eta rho^(a-1),  |rho|<1,
    |eta|/(1-|rho|) < 14472/65536,

then the probability series converges uniformly and (1) gives

    F_infinity = F_0
       + alpha eta^3/(1-rho^3)
       + beta  eta^4/(1-rho^4).                                 (4)

The full 11-profile has the identical vector formula with `U,V`. Its tail has
two contraction modes, `rho^3` and `rho^4`; this is a genuine exact limiting
density, though not a Perron--Frobenius stationary profile of a constant split.

## Relation to the 11-profile composition operator

Even-Zohar and Linial define graph composition `G odot H`, derive a bilinear
profile operator by conditioning on partitions of the sampled vertices, and,
with `G` fixed, obtain a stochastic linear operator whose stationary vector is
the nested four-profile. Their unlabeled order-four reduction is an `11 x 11`
Perron--Frobenius calculation. See Sections 2--3, especially equations (7)--(8),
of [A Note on the Inducibility of 4-vertex Graphs](https://arxiv.org/abs/1312.1205).

Our latent refinement is not that composition. Every latent coordinate changes
all active cross-block probabilities additively; adjacency is not decided by
the first coordinate at which two vertices differ. More importantly, the next
the derivation of the next update uses the support mask `C` and its alignment
with the probability types in `P`. That information is absent from an ordinary
untyped 11-profile when comparing arbitrary typed constructions. Thus the
standard universal stochastic `11 x 11` composition operator does not apply.
`typed-profile-operator.md` now supplies an explicit same-untyped-profile,
different-support-alignment counterexample. On our fixed `(P,C)` orbit,
however, equation (1) itself gives the closed affine controlled update
`v' = v + U epsilon^3 + V epsilon^4`; if `U,V` are independent, `v_r` also
encodes `(S3,S4)`. This is closure, but not a stochastic PF iteration.

A generic transfer description would have to retain a typed profile, at least
the simultaneous isomorphism type of the realized six-edge graph and the
six-edge support/type pattern. A labeled version is finite but much larger
than 11 states. For this particular additive binary kernel, the Eulerian
argument collapses that generic state space much further: after `U,V` have been
computed from `(P,C)`, the exact sufficient state is only

    (1, S3, S4),  where S3=sum epsilon_a^3 and S4=sum epsilon_a^4.

Adding a prescribed amplitude is an affine translation of `(S3,S4)`. Its
homogeneous matrix has every eigenvalue equal to one, can contain signed profile
increments, and is neither a stochastic 11-state operator nor an attracting PF
map. For geometric amplitudes the tail instead evolves under the diagonal
contraction `diag(rho^3,rho^4)` and converges to (4).

This distinction is the main transfer from the adjacent literature: profile
operators remain the right language, but the state must include construction
types before any stationary-vector claim is sound.

## Exact global allocation of latent amplitudes

Equation (2) turns recursive amplitude choice into the bounded separable problem

    minimize sum_a [Bint x_a^4 - Aint x_a^3]
    subject to x_a >= 0 and sum_a x_a <= 14472,

with `q_a=-x_a`. This problem has an exact global solution, including unequal
and countably infinite collections of levels:

    x_1=x_2=x_3=x_4=3618, and all other x_a=0.                (5)

Equivalently, the four amplitudes are the rational number
`epsilon_a=-3618/65536=-1809/32768`. They exactly exhaust the slack because
`4*3618=14472`.

Here is a proof that does not assume equal amplitudes. Scale `x=Rt`, where
`R=Aint/Bint`, and put

    h(t)=t^4-t^3,
    T=14472/R,
    m=T/4=14472*Bint/(4*Aint).

Direct integer cross-multiplication using the displayed `Aint,Bint` gives

    57/100 < m < 3/5.                                      (6)

The constraint is active at an optimum: if slack remains, adding a sufficiently
small positive component strictly decreases the objective. No component with
`t>=1` is useful because `h(t)>=0`. An infinite positive sequence cannot beat a
finite one. Indeed, choose a tail with total below `3/4`; merging any two pieces
of that tail strictly decreases the cost, since

    h(x)+h(y)-h(x+y)
      = xy [3(x+y)-4x^2-6xy-4y^2] > 0

whenever `x+y<3/4`. Iterating and taking the tail limit replaces it by one
component without increasing the objective.

At a finite interior optimum, all positive components satisfy

    h'(t)=t^2(4t-3)=lambda.

For `lambda<0` this equation has at most two positive roots: a small root
`a<1/2` and a large root `b>1/2`. There can be at most one small component,
because two small roots give a negative second variation. All large components
are equal. Regardless of the multiplier, any allocation with at most three
positive components has total cost at least `3h(3/4)=-81/256`, because
`h(t)>=h(3/4)` for every `t>=0` and fewer negative summands only raise that
bound. The four-equal value is strictly smaller: by (6), monotonicity of `h`
below `3/4`, and exact rational comparison,

    4h(m) < 4h(57/100) = -31853196/100000000 < -81/256.

It remains to exclude finite mixed stationary points. Five components would
have one small and four large roots. For two distinct roots of `h'(t)=lambda`,

    4(a^2+ab+b^2)=3(a+b).

Writing `s=a+b` gives

    b = [s+sqrt(3s(1-s))]/2,
    T = a+4b = [5s+3sqrt(3s(1-s))]/2 >= 5/2,

for `3/4<=s<=1`, contradicting `T=4m<12/5` from (6). Six or more components
are also impossible at a local minimum: after the at-most-one small root, five
large roots already sum to more than `5/2>T`. Equal five-or-more configurations
lie in the concave region and have a negative second variation.

For four components, the only remaining alternative is one `a` and three equal
`b`. Set `a=m+3d`, `b=m-d`. A direct expansion gives

    h(a)+3h(b)-4h(m)
      = 12 d^2 [7d^2+(8m-2)d+6m^2-3m].                    (7)

The quadratic in brackets is strictly positive: its discriminant is
`4(-26m^2+13m+1)`, which is negative when
`m>(13+sqrt(273))/52`; inequality (6) implies this threshold because
`57/100>(13+sqrt(273))/52`. Hence (7) is positive for every unequal allocation.
This proves (5) globally, including arbitrary finite and infinite level counts.

The resulting exact best density within the coherent additive latent family is

    F_best = F_0
      + 4 [Aint*(-3618)^3 + Bint*3618^4] / (192^4 * 65536^6). (8)

Equation (8) is an exact rational specification; it is not yet an independently
recounted 3072-class artifact. At equality in the slack constraint, some leaf
probabilities reach one, so this is the terminal point for the fixed lifted
support recurrence.

## Concrete next discriminating check

Before spending CPU on a `192*2^4=3072`-class materialization, an independent
checker should evaluate the typed 4-profile recurrence or enumerate the
triangle/four-cycle contributions by latent level. The discriminating checks
are:

1. verify the complete 11-vector recurrence, not only the monochromatic scalar;
2. confirm raw `Aint,Bint` scaling by 16 for one lifted level;
3. independently verify the global allocation proof above with an exact
   rational stationary/boundary enumerator;
4. recount the selected hierarchy without using equation (2) as its checker.

No CPU allocation is requested by this note. The global optimum claim is only
for the coherent additive latent family under fixed lifted support and constraint
(3), not for arbitrary graphons. No Lean certificate, novelty claim, or
comparison with an unpublished exact bound is made.
