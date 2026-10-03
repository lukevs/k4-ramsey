# Theory-led directions after the centered-family ceiling

Date: 2026-09-27. No search or sustained CPU computation was used for these
hypotheses. They respond to three concrete negatives: all 18,528 coarse
box-KKT signs pass, the tested 34 one/two-orbit lines do not improve the parent,
and the fixed cyclic two-amplitude centered family has a relaxed gain envelope
below `7.68e-7`.

The earlier structural screens do not justify abandoning recursion altogether.
They tested XOR banks of small deterministic factors, homogeneous nested cores
of order at most five, and a bounded heterogeneous Q9 bank. Their best values
were around `0.0306` or slightly worse than the historical `1411/46592`. They
did **not** use the competitive 192-class rational probability quotient as a
recursive outer rule. The two proposals below also differ from each other:
the first changes the construction at every scale, while the second seeks a
finite-dimensional collective escape in the current quotient.

## Rank 1 — H-TR3-1: first-difference recursion of the 192-class quotient

### Construction

Let `P` be a symmetric rational `B x B` matrix with entries in `[0,1]`, here
the strongest `B=192` quotient. Give each graphon point an infinite word

    x=(x_1,x_2,...) in [B]^N

with product-uniform measure. For distinct words `x,y`, let `k` be their first
differing coordinate and set

    W(x,y) = P[x_k,y_k].

The first differing coordinate exists almost surely. This is the probabilistic
analogue of nested lexicographic composition: if two samples choose different
outer classes, their edge uses the outer quotient; if they choose the same
class, the pair recurses instead of using the old diagonal block `P_ii=0`.
It is not an XOR with a small factor and was not included in the retired
small-core screens.

### Exact scalar recurrence

For color `c`, put `A^R_ab=P_ab` and `A^B_ab=1-P_ab` for `a!=b`. Let `T^c_t`
be the monochromatic color-`c` clique density on `t` sampled words, with
`T^c_1=1`. For an outer label tuple `a=(a_1,...,a_t)`, let `pi(a)` be its
partition into equal-label fibers. Conditional independence between distinct
tail samples gives

    T^c_t = B^(-t) sum_a
      product_{i<j: a_i != a_j} A^c[a_i,a_j]
      product_{S in pi(a), |S|>=2} T^c_|S|.                 (1)

The `B` all-equal tuples contribute exactly `B^(1-t) T^c_t`. Hence, after
orders below `t` have been solved,

    T^c_t = R^c_t(T^c_2,...,T^c_{t-1}) / (1-B^(1-t)),      (2)

where `R` is the sum in (1) with the all-equal tuples omitted. Equations (1)--
(2) sequentially and exactly determine `T_2,T_3,T_4`; the target is

    F_nested = T^R_4 + T^B_4.

No 11-state profile is required for this first discriminator. For a clique,
every equal-label fiber must itself be a clique of the same color, so the
lower-order same-color clique densities are a closed state. Explicitly, the
order-four terms have equality types `1111`, `211`, `22`, `31`, and `4`; the
last is the isolated contraction term `B^-3 T_4`.

### Validity and transfer assumptions

- `P` need only be symmetric and `[0,1]`-valued; its displayed diagonal is
  unused by the first-difference rule.
- The infinite-word kernel is measurable as the pointwise limit of its finite
  depth truncations. The unresolved-tail set at depth `d` has pair measure
  `B^-d`, so convergence is also immediate in `L1`.
- Equation (2) is contractive because `B^(1-t)<1`. There is no stationary-
  vector or Perron--Frobenius assumption hidden in the calculation.
- If `P` is rational, every `T^c_t` from (2) is rational. Standard graphon
  sampling/first-moment realization then gives deterministic finite colorings.
- A direct finite-depth control is available: truncate at depth `d`, use any
  fixed color on unresolved equal words, and verify convergence to (2) at the
  predicted geometric rate.

### Prediction and scale

The ordinary 192-step graphon makes every within-class block blue. Recursion
replaces those positive-measure blocks by a scaled copy of the full competitive
quotient. Equality patterns occur with probabilities of order `1/B`, `1/B^2`,
and `1/B^3`, so this mechanism is not constrained by the `7.68e-7` centered-
kernel envelope. The falsifiable prediction is simply

    F_nested < F_step(P).

Even failure is informative: the exact partition decomposition reports which
of `31`, `22`, and `211` overwhelms any gain and therefore whether a two-type
child rule (for example alternating with the complemented quotient) has a
sign-based rationale. Do not launch a broad typed-rule screen without that
coefficient evidence.

### Cheapest decisive test

1. Implement (1)--(2) with exact integers/rationals for red and blue at orders
   2, 3, and 4.
2. Validate it on `B=2,3` against explicit depth `d=1,2,3` materializations.
3. Evaluate the simple denominator-41 quotient and the precision quotient.
4. If and only if either improves, independently recompute the five equality-
   partition contributions and serialize a depth-convergence certificate.

This is `O(B^4)` naively and can reuse the coarse-signature histogram. A value
at or above the parent falsifies homogeneous first-difference recursion for
that `P`, not typed recursion generally.

## Rank 2 — H-TR3-2: a collective quadratic mode of fractional coarse means

### Why existing tests do not cover it

The 192-class parent has 1,248 fractional unordered off-diagonal blocks: 1,152
of type `p` and 96 of type `h`. Its exact gradient is constant on each of these
two orbits. Therefore every direction `D` supported on fractional blocks with

    sum_{e of type p} D_e = 0,
    sum_{e of type h} D_e = 0                              (3)

has exactly zero first variation. The box-KKT audit only tests first-order
coordinate signs. The 34-line bank tests regular one-orbit and selected
two-orbit moves. Neither establishes the sign of the Hessian on the roughly
1,246-dimensional neutral space (3). Centered microtype refinements are also
different: they keep **each** coarse mean fixed, whereas (3) redistributes
means collectively among fractional blocks.

### Exact quadratic form

For an ordered coarse quadruple `x=(x_0,...,x_3)` and its six positional edges
`E(K4)`, differentiation of

    product_e P[x_e] + product_e (1-P[x_e])

gives, for a symmetric direction `D`,

    D^2 F_P[D,D] = (2/B^4) sum_x sum_{e<f}
      D[x_e] D[x_f]
      [product_{g != e,f} P[x_g]
       + product_{g != e,f} (1-P[x_g])].                   (4)

All coefficients in brackets are nonnegative, but the quadratic form need not
be positive semidefinite because products `D[x_e]D[x_f]` have both signs. If
(3) holds and (4) is strictly negative, then `P+tD` is a rigorous descent for
all sufficiently small nonzero rational `t`; no unproved global optimizer is
needed. Moreover `F(P+tD)` is an exact polynomial of degree at most six, so the
best feasible point on that line can be selected and recounted exactly.

### Symmetry reduction

The quotient was built from a Cayley/product/voltage description. If a group
action is available on the 1,248 fractional edge coordinates, the Hessian
commutes with that action. Representation decomposition can then reduce the
1,248-square matrix to smaller invariant blocks. The two constant orbit modes
are removed by (3). An exact negative eigenvalue can be certified by an integer
vector `D` with `D^T H D<0`; a full spectral theorem is unnecessary for a
construction.

The subsequent exact recovery audit found a transitive quotient action with
point stabilizer of order 240, but the 192 chosen transporters are neither
closed nor regular. Therefore an abelian 192-point Fourier transform is **not**
currently justified. A symmetry implementation must use the actual full group/
orbital algebra (or its permutation representation on fractional edges), not
treat the transporter list as a group. The bounded Lanczos-plus-exact-vector
fallback below remains valid without resolving that representation theory.

This symmetry is a performance assumption, not a validity assumption. If the
stored quotient coordinates do not expose the required group action, (4)
still defines exact Hessian-vector products, and a floating Lanczos vector may
be rounded to an integer proposal before exact evaluation.

### Prediction and falsifier

Prediction: at least one nonconstant representation block of the fractional-
mean Hessian is indefinite, yielding a collective rational direction with a
larger gain than scalar `p,h` retuning. This is plausible precisely because
the parent was optimized only in the two constant modes.

The decisive local falsifier is an exact `LDL^T`/character-block certificate
that every Hessian block on (3) is positive semidefinite. That rejects the
quadratic escape mechanism at this parent. It does not exclude a finite-amplitude
higher-order escape or a new quotient, and that distinction must be reported.

### Cheapest decisive test

1. Derive exact Hessian-vector products from (4) and check them against exact
   second differences on tiny matrices and on several sparse directions.
2. Confirm the orbit-constant gradient identity, then project out the two
   constant modes in (3).
3. Diagonalize the smallest symmetry blocks first, or run a bounded Lanczos
   proposal followed by exact `D^T H D` evaluation.
4. On the first exact negative vector, determine the entrywise feasible
   interval for `t`, evaluate the full exact degree-six line, materialize the
   best rational point, and use the generic compressed recount.

No candidate should be promoted from a floating eigenvalue alone. Conversely,
one exact negative quadratic form plus the zero-linear identity is already a
mathematical proof of local improvement and a strong reason to allocate a CPU
lane.

## Allocation recommendation

Run H-TR3-1 first: its recurrence is tiny, exact, and either yields a new
infinite construction or a useful signed equality-partition diagnosis. In
parallel only after implementation ownership is assigned, derive H-TR3-2's
Hessian reduction. Do not spend another lane on fixed-kernel phase restarts;
their best possible scale is already bounded. Do not reuse the old small-core
recursive screen as a control for H-TR3-1—the correct control is the same
192-class quotient used once as an ordinary step graphon.
