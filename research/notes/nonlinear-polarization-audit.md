# Audit of nonlinear probability-adaptive sign refinement

Date: 2026-09-27. Proposed transformation:

    W'((x,s),(y,t))
      = W(x,y) + epsilon W(x,y)(1-W(x,y)) s t,
    s,t in {+1,-1}, |epsilon| <= 1.

This note separates the sound one-step mechanism from the substantially harder
claim that repeated application is beneficial.

## Validity and exact one-step gate

Put `p=W(x,y)` and `c=p(1-p)`. Since

    p-c = p^2 >= 0,
    p+c = 1-(1-p)^2 <= 1,

every `|epsilon|<=1` is pointwise feasible. The kernel is symmetric when `W`
is symmetric, and averaging either fresh sign preserves `p` exactly.

For four positional vertices, sign averaging kills every selected perturbation
edge set with an odd-degree positional vertex. The only nonempty survivors are
the four triangles and three four-cycles. Consequently

    F(W') = F(W) + A3 epsilon^3 + A4 epsilon^4,              (1)

where, writing `p_e=W(x_u,x_v)` and `c_e=p_e(1-p_e)`, the exact graphon
coefficients are

    A3 = E_x sum_{H triangle in K4}
           product_{e in H} c_e
           [product_{e notin H} p_e
            - product_{e notin H} (1-p_e)],                 (2)

    A4 = E_x sum_{H C4 in K4}
           product_{e in H} c_e
           [product_{e notin H} p_e
            + product_{e notin H} (1-p_e)].                 (3)

Repeated coarse/fine class labels remain in the expectation. Formula (3)
shows `A4>=0`.

This gives a decisive gate before materialization:

- if `A3=0`, this line cannot improve `W`; its minimum is `epsilon=0`;
- if `A3!=0`, taking a sufficiently small `epsilon` of the opposite sign gives
  strict improvement;
- when `A4>0`, the unconstrained nonzero stationary point is
  `epsilon_*=-3 A3/(4 A4)`, clipped to `[-1,1]`, and exact endpoint/stationary
  comparison solves the complete one-step line.

Thus no generic symmetry argument presently kills the proposal, but a zero or
tiny `A3` on candidate `b93b...` would kill it cheaply. Red/blue balance of the
total objective does not by itself imply `A3=0`; the weighted star difference
in (2) must be computed.

## Relationship to work already done

One level is not a wholly new perturbation principle. It is the previous
rank-one centered sign split with a block-adaptive amplitude
`C(x,y)=W(x,y)(1-W(x,y))`. What is new relative to the fixed-support additive
analysis is that the amplitude changes after every descendant probability
changes. Hence the fixed coefficients, additive-level recurrence, and
`sum |q_a|` feasibility ceiling in `recursive-latent.md` do not apply.

It also differs from the five-state per-edge boundary search: the latter uses
one translated cyclic kernel on selected coarse fractional blocks. Here every
fractional **fine** block receives a binary rank-one split whose magnitude is
determined nonlinearly by its current probability. At `epsilon=1` this is not
merely analogous to probability polarization: the two scalar descendants are
exactly the binary-erasure-channel polar transform `p^- = 2p-p^2` and
`p^+ = p^2` (Arikan, arXiv:0807.3917). Thus the marginal recursion and its
endpoint-polarization proof are prior art, not a novel mechanism.

What remains candidate-specific is the six-edge `K4` objective. For four
vertices the six branch signs are not independent: a vertex-sign assignment
induces one of the eight cut-space sign vectors `(s_i s_j)_{i<j}`. Therefore
scalar BEC polarization does not determine the joint `K4` transfer or its
monotonicity; that is the actual research question.

## Infinite iteration is valid, but not closed or monotone

At `epsilon=1`, a fresh sign product sends

    p -> p^2             with probability 1/2,
    p -> 2p-p^2          with probability 1/2.              (4)

For a fixed pair of infinite sign sequences, the successive probabilities
form a bounded martingale. More generally, for any fixed nonzero
`|epsilon|<=1`,

    E[p_{d+1} | p_d] = p_d,
    E[(p_{d+1}-p_d)^2 | p_d]
      = epsilon^2 p_d^2(1-p_d)^2.                            (5)

Bounded-martingale convergence and the finite total quadratic variation imply
`p_d -> p_infinity` in `L2`, with
`p_infinity in {0,1}` almost surely. The graphons therefore converge in `L1`
to a symmetric random-free graphon, and the red and blue `K4` densities
converge by the six-factor telescoping bound.

There is also a quantitative proof which avoids hiding the endpoint step in a
quadratic-variation citation. With `V_d=p_d(1-p_d)`, direct expansion gives

    E[V_{d+1} | p_d] = V_d - epsilon^2 V_d^2.

Thus `a_d=E[V_d]` obeys
`a_{d+1} <= a_d-epsilon^2 a_d^2`, and hence
`a_d <= 1/(epsilon^2 d+1/a_0)`. Under the natural terminal-indicator coupling,
`||W_d-W_infinity||_1=2a_d`; the six-factor telescoping bound for both colors
then gives `|F(W_d)-F(W_infinity)| <= 24a_d`.

The BEC identification gives a more explicit version of the same limit. There
is a uniform threshold variable `Theta` on an infinite bit stream satisfying

    Theta(0z) = 1-sqrt(1-Theta(z)),
    Theta(1z) = sqrt(Theta(z)),

such that, up to null sets,

    W_infinity((x,u),(y,v))
      = 1{Theta(u xor v) < W_0(x,y)}.                       (6)

This is useful for representing or sampling the limit, but it does not close
the `K4` objective: the four vertex streams generate only eight correlated
cut vectors per level, and those correlations persist through the cascade.

This proves existence of a legitimate limiting construction. It does **not**
prove it is better. At level `d`, equations (2)--(3) must be recomputed from
`W_d`; `A3` can change sign or vanish, and (1) supplies no monotonicity for a
fixed `epsilon`. Cross-level terms are absorbed into the changed amplitudes,
so the earlier no-mixing/additive recurrence is inapplicable.

There is also no evident small finite profile closure. A generic starting
probability has up to `2^d` descendants under (4), and a rational denominator
roughly squares at each level. Materialized type count and numerator bit length
therefore grow exponentially unless extra algebraic coincidences are proved.
An assertion of an infinite fixed-profile operator would presently hide the
main hard lemma.

## Recommendation and cheapest test

The proposal earns one coefficient computation, not an immediate recursive
campaign:

1. From the explicit `b93b...` matrix, recompute (2)--(3) exactly, including
   repeated fine indices.
2. Compare `epsilon=0`, the clipped rational stationary point, its neighboring
   grid points if quantized, and both endpoints.
3. If the predicted gain is material, construct only the one-level split and
   recount it with the generic typed-kernel histogram evaluator. Existing five
   fine types plus the new sign give ten types over each of 192 bases.
4. Only after an admitted one-level gain, compute fresh `A3,A4` at level two.
   Continue while gains remain material; do not extrapolate a fixed recurrence.

Denominators must be represented explicitly. If the current entries are
`a/Q` and `epsilon=r/s`, a direct child denominator is `s Q^2`; repeated depth
squares denominator sizes. Arbitrary-precision arithmetic and recorded
normalization bounds are mandatory.

Decision rule: `A3=0`, or a rigorously optimized one-step gain below the cost
threshold chosen by the coordinator, retires this candidate-specific direction.
A nonzero `A3` proves only a local one-step improvement, while a recounted
one-level candidate is already a valid construction without any infinite-limit
claim.

## Candidate-specific gate result

`reports/nonlinear-polarization-b93-003/report.json` evaluated (2)--(3) exactly
from the candidate-bound six-kernel-signature histogram. An independent source
audit checked all four triangle/complement triples, all three
cycle/complementary-matching pairs, the `N^4` normalization including repeated
coarse labels, the `Q^9,Q^10` denominator powers, and the exact stationary
point. It found

    A3 ~= 9.8742883654e-9,
    A4 ~= 3.7798712173e-8,
    epsilon_* ~= -0.1959250950,
    Delta F ~= -1.8565900255e-11.

This is a real but structurally tiny one-step improvement. The exact stationary
rational has an enormous denominator and cannot be recounted by the current
U256 materialization. That is not a fundamental obstruction: `epsilon=-1/5`
retains `99.7332%` of the gain (`Delta F ~= -1.8516367446e-11`), has child
denominator `5Q^2`, and gives a 250-bit normalization denominator (251-bit
two-color raw upper bound), so the total is mathematically representable in 256
bits. This does **not** mean the existing generic U256 counter accepts it: that
implementation stores pair products in `uint64` and the inner contraction in
`uint128`, assumptions violated by denominator `5Q^2`. A widened-intermediate
or compressed recount would be required. The experiment remains Level A: the
native histogram is candidate-bound, but no materialized child recount was
performed. On scale, this gate does not justify that checker adaptation or a
deep cascade before stronger mechanisms are exhausted.

### Bias-signed amplitude variant

The follow-up amplitude

    C(p) = sign(2p-1) p(1-p),    sign(0)=0,

is equally feasible and mean-preserving: the sign only swaps the two children.
The same cubic-plus-quartic expansion applies, but the four signed amplitudes
around a cycle can have negative product, so `A4>=0` cannot be assumed. The
complete line minimum is nevertheless elementary: compare `0`, both endpoints,
and `-3A3/(4A4)` when it exists inside `[-1,1]`. Under color complement the
signed amplitude and triangle red-minus-blue bracket both reverse, so both
`A3` and `A4` are invariant.

`reports/signed-polarization-b93-001/report.json` passes an independent source
audit of those sign rules, signed accumulators, motif indices, and candidate
comparison. It found

    A3 ~= 9.8742883654e-9,
    A4 ~= 3.3633612686e-8,
    epsilon_* ~= -0.2201879514,
    Delta F ~= -2.6352781857e-11.

This modestly improves the unsigned line but remains about `4.15e-10` above
the incumbent. A low-denominator point `epsilon=-2/9` retains about `99.9482%`
of the line gain, so denominator approximation is not the scientific blocker.
The scale is; stopping before child materialization is justified.
