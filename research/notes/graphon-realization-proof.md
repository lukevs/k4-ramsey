# Rational stochastic-block realization: adversarial proof blueprint

Date: 2026-09-27.  This note audits the passage from the rational
192-class probability matrix to an asymptotic upper bound for the `K4`
Ramsey multiplicity constant.  It does not recount the matrix, establish
novelty, or prove a matching lower bound.

## Statement to prove

For a red/blue coloring `C` of `K_N`, let `M4(C)` be the number of unordered
four-vertex sets whose six edges are all red or all blue, and put

    a_N = min_C M4(C) / binom(N,4),                  N >= 4.

The sequence `a_N` is nondecreasing and bounded, so

    c4 = lim_(N -> infinity) a_N

exists.  Fix `r >= 1`, `q >= 1`, and a symmetric integer matrix
`A : {0,...,r-1}^2 -> {0,...,q}`.  Write `P_ij = A_ij/q` and

    T_A(i0,i1,i2,i3)
      = product_(0 <= s < t < 4) A_(i_s,i_t)
        + product_(0 <= s < t < 4) (q - A_(i_s,i_t)),

    S(A) = sum_(i0,i1,i2,i3 in {0,...,r-1}) T_A(i0,i1,i2,i3),

    F(A) = S(A) / (r^4 q^6).

The target general theorem is

    rational_step_upper_bound:
      symmetric(A) -> entries(A) <= q -> c4 <= F(A).

The diagonal is meaningful: `A_ii/q` is the red probability for an edge
between two **distinct** vertices in the same class.  It is not a loop
probability.  The present candidate has `A_ii = 0`, but the theorem should
not require that specialization.

For `reports/literature-two-parameter-001/graphon-candidate.json`, the audited
parameters are

    r = 192,
    q = 65536,
    entries(A) in {0, 35015, 51064, 65536},
    S(A) = 3244987362620791518517985192882208768,
    r^4 q^6 = 107667467658578185705208371882707910656.

After reduction this is

    F(A)
      = 515776850799050572477656236153
        / 17113283103081096920205493272576
      ~= 0.03013897728988013.

The exact sum is an executed-count claim reproduced by two C++ organizations
and by the standalone unbounded-`Nat` compiled Lean recount in
`reports/graphon-precision-lean-001/report.json` (candidate hash
`e26e754168010c069da3e0b207a140f2c7cbbfc36cc0a6af06ef409db5024450`).
That is strong independent execution evidence, but still not a theorem
supplied by the realization argument below or a kernel reduction of the sum.

## Finite random construction

For each integer `m >= 1`, use the vertex set

    V_m = {0,...,r-1} x {0,...,m-1},       N = r m.

For every unordered pair of **distinct vertices** `e = {u,v}`, independently
choose its color.  If the class labels of `u,v` are `i,j`, make the edge red
with probability `A_ij/q` and blue with probability `(q-A_ij)/q`.

No measure theory is needed for rational `A`.  Give each edge an independent
uniform label in `{0,...,q-1}` and declare it red exactly when its label is
less than `A_ij`.  Thus the sample space is the finite set

    Omega_m = ({0,...,q-1})^(E(K_N)).

This distinction is essential.  Randomizing one edge for each pair of
classes and reusing it across a blow-up would couple many vertex edges and
would not have the density `F(A)`.

For four distinct vertices `v0,v1,v2,v3`, all six unordered vertex edges are
distinct random coordinates, even if two, three, or four class labels agree.
Consequently, conditional on class labels `i0,i1,i2,i3`, the probability that
the four-set is monochromatic is exactly

    T_A(i0,i1,i2,i3) / q^6.

This establishes the product formula for repeated **class indices**.  It
does not apply to repeated vertices, which are treated only as an auxiliary
comparison below.

## Exact normalization and collision error

Let `X0,...,X3` be independent uniform vertices of `V_m`, sampled with
replacement, and let `I_s` be their class labels.  Define the auxiliary
bounded function

    f(I0,I1,I2,I3) = T_A(I0,I1,I2,I3) / q^6 in [0,1].

Because the four class labels are independent uniform elements of `Fin r`,

    E[f(I0,I1,I2,I3)] = S(A)/(r^4 q^6) = F(A).

On the collision event this is only an auxiliary value; it is not claimed to
be the monochromatic probability of a tuple with loops or repeated edges.
Let `D` be the event that the four sampled vertices are distinct.  On `D`,
independence of the six vertex edges gives

    E[f | D]
      = E_C[M4(C)/binom(N,4)],

where the outer expectation is over the random coloring.  The normalization
is exact: ordered distinct four-tuples have denominator

    (N)_4 = N(N-1)(N-2)(N-3) = 24 binom(N,4),

and every unordered four-set has exactly 24 orderings.  In contrast, `r^4`
in `F(A)` is correct because class labels are ordered, sampled with
replacement, and may repeat.

Put

    epsilon_N = Pr(not D) = 1 - (N)_4/N^4.

Writing `F(A) = (1-epsilon_N) E[f|D] + epsilon_N E[f|not D]` and using
`0 <= f <= 1` gives the explicit bound

    |E_C[M4(C)/binom(N,4)] - F(A)| <= epsilon_N <= 6/N.

The last inequality is the union bound over the six pairs of sampled
positions.  For this candidate, `N = 192m`, so the displayed error is at most

    1/(32m).

This is the complete `O(1/m)` term; it is not necessary to enumerate the
patterns of repeated class labels.  Those patterns are already part of
`S(A)`.  Only repeated **vertices** enter `epsilon_N`.

## Deterministic realization

The random variable `M4(C)/binom(N,4)` lives on the finite nonempty space
`Omega_m`.  At least one outcome is no larger than its average.  Hence, for
every `m` (here automatically `N >= 4`), there is a deterministic coloring
`C_m` of `K_(rm)` such that

    M4(C_m)/binom(rm,4)
      <= F(A) + epsilon_(rm)
      <= F(A) + 6/(rm).

No concentration theorem is needed.  The proof does not produce a compact
serialized coloring, and it does not claim that any finite `C_m` has density
exactly `F(A)`.  It proves the existence of a sequence whose limiting upper
density is at most `F(A)`.

## Existence of `c4` and passage to the limit

For `4 <= n <= N`, take any coloring `C` of `K_N` and average over all induced
`n`-vertex subgraphs.  Each monochromatic four-set is contained in exactly
`binom(N-4,n-4)` such subgraphs.  The binomial identity

    binom(N-4,n-4) / (binom(N,n) binom(n,4)) = 1/binom(N,4)

shows that their average monochromatic density is exactly the density of
`C`.  Some induced subgraph has density at most this average.  Applying this
to a minimizing `N`-vertex coloring yields

    a_n <= a_N.

Thus `(a_N)_(N>=4)` is nondecreasing.  It is bounded in `[0,1]`, so its real
limit `c4` exists.  The indices `rm` are cofinal, hence `a_(rm)` has the same
limit.  Since

    a_(rm) <= density(C_m) <= F(A) + 6/(rm),

taking `m -> infinity` proves `c4 <= F(A)`.

The monotonicity direction above is worth preserving in tests: the minimum
density is nondecreasing with the number of vertices, not nonincreasing.

## Smallest useful Lean theorem stack

The implementation should separate the general lifting theorem from the
candidate-specific matrix recount.  A minimal dependency chain is:

1. `StepData` validation: `q > 0`, square symmetric `A`, and `A_ij <= q`.
   Define `stepTerm`, `stepNumerator`, and `stepDensity` with the ordered
   `Fin r` four-sum and denominator `r^4*q^6`.
2. `six_edges_distinct`: the six unordered pairs determined by four distinct
   vertices are pairwise distinct.  This is the bridge that remains valid
   when class labels repeat.
3. `pi_assignment_restriction_count`: for a finite coordinate type `E`, a
   six-element subset `S : Finset E`, and allowed-set sizes `b_e <= q`, count
   assignments `omega : E -> Fin q` satisfying the six coordinate
   restrictions.  The result is

       q^(card E - 6) * product_(e in S) b_e.

   Apply it once with `b_e=A_ij` and once with `b_e=q-A_ij`.
4. `finite_first_moment`: interchange the finite sum over outcomes with the
   sum over four-sets, use (3), and apply the elementary finite-average lemma
   to obtain a deterministic coloring whose density is at most the expected
   density.
5. `distinct_conditioning_error`: express the expected density as the
   ordered-distinct class sum, compare it with the ordered-with-replacement
   sum, and prove the exact `epsilon_N` bound and `epsilon_N <= 6/N`.
6. `minimum_density_mono`: formalize the induced-subgraph double count and
   prove `a_n <= a_N` for `4 <= n <= N`.
7. `minimum_density_tendsto` plus `rational_step_upper_bound`: invoke monotone
   convergence and the cofinal multiples `r*m` to conclude `c4 <= F(A)`.
8. Candidate theorems: check the matrix schema, symmetry, range, exact
   `stepNumerator`, reduction to the displayed fraction, and the desired
   strict comparison by integer cross-multiplication.

The smallest clean formal environment is Mathlib, using `Finset`, `Fintype`,
`SimpleGraph` (or a local unordered-edge type), finite cardinality lemmas, and
the monotone convergence theorem for real sequences.  The current repository
imports only `Std`; staying `Std`-only is possible but would require recreating
substantial finite-set/cardinality and real-limit infrastructure.  It is not
the smaller proof project.

The recommended top-level statements should be inequalities over naturals or
rationals until step 7.  This avoids fragile division side conditions.  A
convenient finite theorem is the cross-multiplied form of

    exists C_m,
      density(C_m) <= stepDensity(A,q) + (1 - (N)_4/N^4).

Only the final limit theorem needs coercions to `Real`.

### Hidden hard lemma

The main hidden lemma is step 3, not the collision estimate.  Informally it is
called “independence of the six edges”; in a kernel proof it must count
functions on the full edge set after restricting six distinct coordinates.
If it is imported as an unproved probability-independence assertion, the
formalization merely relocates the essential argument.  Proving the general
restriction-count lemma once makes the first-moment calculation short and
auditable.

The induced-subgraph double count in step 6 is the second nontrivial lemma,
but it is standard and considerably smaller.  Exact evaluation of the
192^4 candidate sum is computationally expensive rather than conceptually
hard.  `native_decide` or a compiled Lean recount has a different trust
boundary from kernel reduction; a fully kernel-checked headline theorem must
state which mechanism establishes the large numeral equality.

## Adversarial claim ledger

- **Accepted:** repeated class indices are included correctly by the ordered
  sum.  Four distinct vertices still expose six independent edge coordinates.
- **Accepted:** the finite-vs-limit discrepancy is at most
  `1-(N)_4/N^4 <= 6/N`, hence at most `1/(32m)` for 192 equal classes.
- **Accepted:** an at-most-average deterministic coloring exists for every
  `m`; concentration and a consistent infinite random coloring are unnecessary.
- **Accepted:** the minimum densities are nondecreasing, bounded, and their
  cofinal 192-multiple subsequence has the same limit.
- **Not established by this proof itself:** that the JSON matrix sum equals
  the reported numerator.  This equality now has two C++ recounts and a
  standalone exact-`Nat` compiled Lean recount; their trust boundary remains
  candidate-specific execution rather than the general realization theorem.
- **Not established:** a finite binary graph with density `F(A)`, a novel or
  world-record construction, or the exact value of `c4`.
- **Required wording:** once the exact matrix sum is accepted, the candidate
  proves the upper bound `c4 <= F(A)`.  It is a limiting probabilistic
  construction, not merely a heuristic graphon score.

## Cheap falsification tests for the formalization

Before the 192-class theorem is attempted, instantiate the general lemmas on:

1. one class with `A_00=0`, where every finite graph is all blue and both
   `F(A)` and the realized density are 1;
2. one class with `0<A_00<q`, which forces the proof to handle six distinct
   within-class edges rather than accidentally reuse one block-level coin;
3. two classes with repeated label patterns such as `(0,0,1,1)` and
   `(0,0,0,1)`;
4. `N=4`, where there is exactly one four-set and six edge coordinates;
5. a deliberately asymmetric matrix, which validation must reject rather
   than silently orienting undirected edges.

These tests directly target the plausible proof failures; reproducing more
decimal digits of the candidate does not.
