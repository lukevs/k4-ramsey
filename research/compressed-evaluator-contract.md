# Compressed step-graphon evaluator contract

Date: 2026-09-27. This contract reviews the proposed coarse-signature
histogram evaluator. It distinguishes an arithmetic certificate from a
candidate-bound compressed recount and specifies exactly what a verifier must
reconstruct before claiming the latter.

## Scope

The input is an exact symmetric rational step graphon with `N=B*T` equal-mass
classes, indexed base-major/type-minor:

    vertex class = (a,x),   0 <= a < B, 0 <= x < T,
    M[(a,x),(b,y)] / Q      is its red edge probability.

Version 1 assumes unit class masses, `Q>0`, and integer entries in `[0,Q]`.
It supports arbitrary finite `T x T` pair blocks; centering, Potts form, and
rank-one structure are not needed by the direct block evaluator. If a later
schema stores `base probability + centered kernel` instead of the absolute
block, it must additionally verify the reconstruction equation and every
weighted row sum exactly. Those are different schemas and must not be mixed.

The desired numerator is

    sum_(v0,v1,v2,v3 in [N])
      [product_(i<j) M[vi,vj]
       + product_(i<j) (Q-M[vi,vj])],

with denominator `N^4 Q^6`.

## Signature compression

For a sorted coarse multiset `a<=b<=c<=d`, form the six **oriented** pair
blocks in positional order

    01, 02, 03, 12, 13, 23.

An absolute-block schema needs only six exact block IDs. A centered-kernel
schema needs the six base numerators as well as the six kernel IDs and every
amplitude needed to reconstruct the absolute entries. Internal orientation
matters: global symmetry gives `block(b,a)=transpose(block(a,b))`, not
necessarily `block(a,b)=transpose(block(a,b))` when `a!=b`.

For one six-block signature `s`, define

    local(s) = sum_(x0,x1,x2,x3 in [T])
      [product_(i<j) block_s(ij)[xi,xj]
       + product_(i<j) (Q-block_s(ij)[xi,xj])].

The coarse multiset has multiplicity

    mult(a,b,c,d) = 4! / product_z count_z(a,b,c,d)!.

The complete numerator is the sum of `mult*local` over sorted coarse
multisets, or equivalently `sum_signature histogram[signature]*local(signature)`.

### Repeated indices

No separate equality-partition field is needed. If `a=b`, the corresponding
edge slot uses the diagonal coarse block `block(a,a)`. Repeated uses of a
coarse block remain separate edge slots. The inner variables
`x0,x1,x2,x3` are always summed independently over all `T^4` ordered choices,
even when coarse labels or microtype values coincide. They represent four
distinct vertices in the eventual finite realization; repeated step-class
labels are part of the graphon objective, not vertex collisions.

Multiplication by `mult` is sound because permuting the four positions merely
permutes the six blocks, transposes blocks whose endpoint order reverses, and
renames the four independently summed microtype variables. `local` is
invariant under this operation. A proof-producing version should establish
this finite permutation lemma once; a native executable should at least test
all five multiplicity patterns `4,31,22,211,1111` against ordered enumeration.

## Evidence level A: arithmetic-only histogram certificate

The currently proposed Lean checker receives `B,T,Q`, an exact block table,
and a sparse six-ID histogram. It validates:

1. block shapes and entries in `[0,Q]`;
2. signature IDs and nonnegative counts;
3. total histogram mass `sum counts = B^4`;
4. every `local(signature)` by an exact `T^4` `Nat` sum;
5. the final numerator, denominator, and reduced fraction.

This proves the arithmetic implication

    submitted histogram -> submitted exact density.

It does **not** prove that the histogram came from the candidate matrix. A
candidate hash, the mass check `B^4`, tiny fixtures, and agreement with totals
printed by the histogram generator do not supply that missing implication.
The admissible label is therefore:

> Exact compiled-Lean arithmetic evaluation of a native-generated compressed
> certificate, conditional on the candidate-to-histogram generator.

It is not an independently reconstructed candidate count or a kernel theorem.

## Evidence level B: candidate-bound compressed recount

To claim an independently reconstructed count, the verifier must also read the
original candidate matrix `M` (or a smaller construction description that it
evaluates itself) and perform all of the following:

1. Validate `N=B*T`, exact row lengths, `0<=M_uv<=Q`, and `M_uv=M_vu`.
2. Validate the block-ID table against **every one of the `N^2` entries**:

       M[(a,x),(b,y)] = blocks[id(a,b)][x,y].

   If only upper-oriented IDs are stored, explicitly check transpose lookup
   below the diagonal. Diagonal blocks must be symmetric.
3. Reconstruct the signature and multiplicity for every
   `a<=b<=c<=d`; either build a fresh histogram and compare it entry-for-entry
   with the certificate, or directly accumulate `mult*local(signature)` with
   memoized local values.
4. Recompute each distinct `local` by the exact `T^4` sum. Submitted local
   totals may be caches but not trusted facts.
5. Recompute `N^4 Q^6`, the total numerator, gcd reduction, and all reported
   comparisons by exact arithmetic.

After step 3 the histogram is bound to the matrix; step 4 then supplies a
compressed but exact reconstruction of the original ordered four-tuple count.
The certificate generator becomes a performance/provenance tool rather than
a soundness premise.

Canonical deduplication of equal blocks and signatures is useful for stable
artifacts but not logically necessary. If it is claimed, the verifier must
check the canonical ordering or perform its own deduplication.

## Complexity

Let `K` be the number of distinct oriented `T x T` blocks and `H` the number
of distinct six-block signatures.

Arithmetic-only verification costs

    O(K*T^2 + H*T^4)

exact operations and stores `O(K*T^2 + H)` data.

Candidate-bound verification additionally costs

    O(N^2) = O(B^2*T^2)

entry comparisons and

    binom(B+3,4)

coarse-multiset iterations, each doing six ID lookups plus a histogram or
memo-table operation. For the four-level candidate `B=192,T=16,N=3072`:

    N^2 = 9,437,184,
    binom(195,4) = 58,409,520,
    T^4 = 65,536.

Thus the exact work is approximately

    9.4 million entry checks
      + 58.4 million coarse-signature constructions
      + 65,536 * H local type tuples.

This replaces the infeasible `N^4` direct sum. Runtime is controlled primarily
by `H`; the implementation report must record observed `K,H`, histogram build
time, local-evaluation time, and peak memory. No generic efficiency claim is
valid for arbitrary matrices because `H` can approach the number of coarse
multisets.

### Observed version-1 run

The production audit at
`reports/graphon-potts-precision-compressed-001/report.json` used
`B=192,T=3,N=576,Q=65536`. It found `K=4` oriented absolute blocks and only
`H=1002` distinct six-ID signatures. Native candidate-to-certificate
generation took `0.238 s`; compiled Lean exact arithmetic took `0.024 s`.
The latter evaluated only

    H*T^4 = 1002*81 = 81,162

local microtype tuples. This is evidence that the compression is effective on
the present structured candidate, not an asymptotic guarantee.

If the same `H=1002` persisted at `T=16`, the local stage would instead visit

    1002*65,536 = 65,667,072

microtype tuples, in addition to the matrix scan and 58.4 million coarse
multisets. That is a planning estimate only: `K` and `H` must be measured on
the actual four-level candidate, and Lean runtime should not be extrapolated
linearly without a benchmark.

The observed run is level A with a native candidate-binding front end: C++
reconstructs the histogram from every matrix block, while Lean independently
recomputes the exact arithmetic from the resulting certificate. It is fair to
describe the two-stage pipeline that way, but not as a Lean reconstruction of
the histogram. The absolute-block scan also certifies the final matrix without
assuming the advertised Potts or centered-kernel provenance; it does not, by
itself, prove that the matrix was generated by that advertised mechanism.

## Narrower recurrence certificate

For the present fixed-support Rademacher construction, a second sound route is
much smaller but less general. A verifier can read the original `192 x 192`
parent `P`, support mask `C`, and amplitudes, then independently recompute:

- the parent numerator;
- the exact cubic triangle contraction `Aint`;
- the exact four-cycle/common-neighbor contraction `Bint`;
- `sum q_a^3`, `sum q_a^4`, feasibility `sum|q_a|<=14472`, and the final
  expansion.

That verifier must derive `Aint,Bint` from `P,C`; accepting them as certificate
fields would again be arithmetic-only. This narrower route handles repeated
base indices through its common-neighbor/C4 contraction and avoids all `3072`
classes, but it certifies only the fixed rank-one centered family. It cannot be
advertised as an arbitrary-kernel evaluator.

## Required report fields

Every run should record:

- evidence level `arithmetic_only` or `candidate_bound`;
- candidate path and SHA-256, `B,T,N,Q`, and indexing convention;
- schema choice: absolute blocks or base-plus-centered-kernel;
- observed `K,H`, histogram mass, all five equality-pattern fixture results;
- exact numerator/denominator/density and arithmetic type;
- source, binary, certificate, and report hashes;
- separate timings for candidate scan, histogram reconstruction, local sums,
  and final arithmetic;
- explicit trust statement naming any native preprocessing still assumed.

The strongest justified current claim is level A until the Lean side itself
performs steps 1--3 of level B. A separately written native direct control is
valuable evidence, but if it consumes the same generated histogram it is not
an independent reconstruction of the candidate count.
