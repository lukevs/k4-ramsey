# Homogeneous first-difference recursion on the 192 quotient

## H-TR3-1

For infinite uniform words over the 192 quotient labels, color an edge using
the retained quotient probability at the first coordinate where its endpoints
differ.  Equal outer labels recurse; the displayed diagonal of the ordinary
step graphon is never used.  This is a graphon construction, not a finite
quotient approximation.

For each color, set the off-diagonal probability matrix to `A` and its
diagonal to zero.  Exact ordered distinct-label sums give

    T2 = S1 / (B^2-B),
    T3 = (S111 + 3 T2 S2) / (B^3-B),
    T4 = (S1111 + 6 T2 S211 + 3 T2^2 S4 + 4 T3 S3)
         / (B^4-B).

Here `Sk=sum_(a!=b) A_ab^k`, `S111` is the ordered distinct-label triangle
sum, and

    S211 = sum_(distinct a,b,c) A_ab^2 A_ac^2 A_bc.

The factors `6,3,4` are the equality partitions `211,22,31`; the denominator
removes the all-equal contraction term.  Red and blue recurrences are solved
independently and added only at the end.

### Controls

Before production evaluation:

- a native exact term counter was checked against literal ordered sums on
  arbitrary `B=2,3` rational matrices;
- the closed formulas were checked against a generic tuple/partition
  implementation of the recurrence;
- for both terminal colors, depth-one through depth-three recurrences were
  checked against literal finite-word materializations;
- both production ordinary-step densities were independently reconstructed
  from the emitted equality terms;
- `B^4 Q^6` is below signed 128-bit capacity in the largest case, while the
  implementation uses nonnegative unsigned 128-bit accumulators.

The finite-depth error is controlled by the event that at least one sampled
pair has not differed by depth `d`, bounded by `choose(t,2) B^-d`; the
one-level all-equal self-coefficient remains exactly `B^(1-t)`.

## Exact result

The prediction was `F_nested < F_step(P)`.  It failed for both requested
parents:

| Parent | Ordinary step | First-difference recursion | Delta |
|---|---:|---:|---:|
| denominator 41 | 0.03013899413358829 | 0.03027519757186159 | +0.0001362034383 |
| denominator 65536 | 0.03013897728988013 | 0.030272980143043526 | +0.0001340028532 |

For the competitive precision quotient, the red `K4` density rises from
`0.01504738834263002` to `0.016989596485075368`, a penalty
`+0.00194220814245`.  The blue density falls from `0.015091588947250111` to
`0.013283383657968157`, a gain `-0.00180820528928`.  Recursive red cliques
inside equal-label fibers therefore overwhelm the blue improvement.  The
failure is stable across the simple and precision parameterizations and is
far above numerical ambiguity because the comparison is an exact rational
inequality.

Decision: retire homogeneous self-substitution of these two 192 quotients.
The signed diagnosis gives a rationale only for a genuinely typed or
color-alternating child rule that suppresses the red same-label contribution;
it does not justify a broad typed search without a separately preregistered
closed recurrence.

Immutable report SHA-256:
`dd82873f487f5a026644a80e80d29f827fbf77e6dbcdcb541070bb2bc91d1159`.
