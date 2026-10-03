# Independent audit: exact single-flip delta-landscape updates

2026-09-27. Scope: unit weights, blue diagonals, objective
`N = n + 14*E_blue + 36*T_blue + 24*(K4_blue + K4_red)`.

## Verdict

The proposed mixed-interaction formulas are correct. An independent literal
ordered-quadruple oracle checked **all 1,024 labeled five-vertex graphs**, every
one of their 10 possible first flips, and every resulting edge-delta coordinate:
**102,400 exact checks**, completed in 0.71 seconds without calling native code.
The sign reversal of each interaction after flipping its first edge was also
checked exhaustively. This validates the mathematical update on small instances,
not a future optimized implementation or its 64-bit boundary handling.

## Derivation and signs

For distinct edges e and f, let

```
D_e(G) = N(G xor e) - N(G)
B_ef(G) = N(G xor e xor f) - N(G xor e) - N(G xor f) + N(G).
```

Direct substitution gives

```
D_f(G xor e) = D_f(G) + B_ef(G),  f != e
D_e(G xor e) = -D_e(G).
```

Let s be +1 if the current colors of e and f agree, and -1 otherwise.
The 14*E_blue term is linear and contributes no mixed interaction.

For shared-endpoint edges e=uv and f=uw, put c=color(vw). Only the triangle
uvw and four-vertex sets uvwz can contain both free edges. A blue triangle
contributes `36*s` exactly when c is blue. A four-set contributes `24*s`
exactly when uz, vz, wz, and vw all have color c. Therefore

```
B_uv,uw = s * (36*I(vw blue) + 24*|N_c(u) intersect N_c(v) intersect N_c(w)|).
```

Neighborhood masks must exclude their own vertex and any unused high bits.
With proper simple-graph neighborhoods, the triple intersection automatically
excludes u, v, and w. Treating blue diagonal entries as blue self-neighbors here
would introduce spurious contributions; diagonal repetition effects are already
accounted for by the 36 term.

For disjoint edges e=uv and f=wx, only their four endpoints can contribute.
Consequently

```
B_uv,wx = 24*s*I(uw, ux, vw, vx all have one common color).
```

These expressions are symmetric under exchanging e and f or reversing either
edge's endpoint ordering. The sign depends on the two *free-edge colors*, not
on the common color of the fixed cross edges.

## Update-order hazards

1. Compute all B values on the **pre-flip graph**, add them to the cached deltas,
   negate the flipped edge's delta, then flip its adjacency bits. It is valid to
   stream the cache updates because B depends only on adjacency, not on cached
   delta values, provided adjacency stays unchanged until the pass ends.
2. Alternatively, flip adjacency first and **subtract** the B values evaluated
   afterward: `B_ef(G xor e) = -B_ef(G)`. Do not add post-flip interactions.
3. For an accepted multi-edge move, repeat the whole single-flip procedure
   sequentially on intermediate states. Summing two interaction updates computed
   on the original graph is generally wrong because third-order terms exist.
4. Handle the flipped edge separately. The mixed-difference formula for distinct
   edges is not intended for e=f. Store only one orientation or keep both cache
   orientations synchronized; do not apply a mixed update twice.
5. After first flipping one edge of an accepted pair, the second edge's cached
   delta already includes their mixed interaction. Summing those two sequential
   deltas yields the joint objective change exactly, without another B term.

## Implementation checks still required

Before promotion, compare the optimized implementation's complete cache against
fresh native deltas after random and adversarial flip sequences, including
undo and n=63,64,65,127,128,129 boundary cases. Check both red and blue free-edge
colors and both shared/disjoint configurations. A fresh whole-graph count should
agree with accumulated gains. The runner's independent compiled Lean check
remains necessary for emitted full-order candidates.

No claim of a new theorem or novelty: these are finite-difference identities
and direct motif enumeration. No full-order experiment was run by this auditor.
