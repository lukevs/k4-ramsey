# Exact automorphism and orbital recovery

Date: 2026-09-27.  This lane addresses the missing vertex-label obstruction
without treating archived row numbers as group coordinates.  All proposed
permutations are derived from adjacency/fiber relations and then verified
entrywise.

## Quotient automorphisms

The 768-vertex published core has an exact four-sheet decomposition into 192
fibers.  Color each quotient pair by its inter-fiber degree in `{0,2,3,4}`.
Individualization/refinement with base `[0,18,4,3,7]` makes this colored
quotient discrete.  Exhaustive compatible-base branching gives:

- an automorphism sending fiber 0 to every one of the 192 fibers;
- an exact point stabilizer of order 240;
- five compact stabilizer generators and three further movers, targeting
  fibers 1, 3, and 18, which make the action transitive.

Every permutation is checked on all `192^2` colored entries.  Since the
generated action contains the complete 240-element point stabilizer and is
transitive, orbit-stabilizer certifies the full colored automorphism-group
order as `192*240 = 46080`.  The stabilizer element-order distribution is

    1:1, 2:51, 3:20, 4:60, 5:24, 6:60, 10:24,

consistent with `S5 x C2`; this resemblance and the corresponding `W(B6)`
order are structural clues, not the group-identification certificate used
here.

## Schreier orbitals and the graphon basis

The point-stabilizer orbits give 24 directed orbitals.  The exact two-parameter
192-class graphon is invariant under all eight compact generators, and its
entire `192 x 192` probability matrix is reconstructed from the stored orbital
IDs and 24 orbital values.

More importantly for collective optimization, its 1,248 fractional unordered
edges split into only five exact automorphism orbits:

| orbit | numerator / 65536 | size | representative |
|---:|---:|---:|---:|
| 0 | 51064 | 480 | `(18,2)` |
| 1 | 51064 | 96 | `(28,2)` |
| 2 | 51064 | 480 | `(30,7)` |
| 3 | 35015 | 96 | `(40,18)` |
| 4 | 51064 | 96 | `(50,2)` |

This is the exact low-dimensional orbit basis requested for a collective
gradient/Hessian screen.  It is materially finer than the old common `p,h`
parameterization while retaining a certified symmetry.

## Lift to all 768 vertices

Each quotient map was lifted through the degree-three permutation voltages.
Candidate sheet maps are propagated exactly along the three connected
64-fiber defect components and filtered by every degree-two block.  For each
target fiber, a lift exists.  The identity quotient has four sheet movers at
fiber 0.  Composing them produces 768 permutations whose images of vertex 0
are all distinct.  Every retained permutation is checked on all `768^2`
adjacency entries.  Thus the archived core itself is exactly vertex-transitive,
with a certified Schreier/voltage description.

These 768 movers are a transversal, not a subgroup.  A greedy attempt to find
a regular elementary-abelian 64-subgroup stalled, and no negative Cayley claim
is inferred: choosing the first automorphism per target need not close.  The
current positive result is the exact transitive action and orbital factor.

## Evidence

- quotient/transversal report:
  `reports/group-recovery-quotient-001/report.json`, SHA-256
  `5aa5d3452273376a486fae38e5c403aea6ec0f43d206ffa0040765378e5311bc`;
- stabilizer report:
  `reports/group-recovery-stabilizer-001/report.json`, SHA-256
  `8f9826e103b15adcee43074ff00bfcbd990613596bf2f269704619c05b375881`;
- full 768 lift report:
  `reports/group-recovery-lifted-action-001/report.json`, SHA-256
  `ea0ee703b1d81bd09d78bd47469b79e85ae40947dba4988a9695bb7982bd5bb3`;
- orbital/fractional-basis report:
  `reports/group-recovery-orbitals-001/report.json`, SHA-256
  `7a8d162778041e36635357ac52bc497e86d095f9a55dab4fc00f94ceea3a8035`.

The five modes span the automorphism-invariant fractional-edge subspace; they
do not diagonalize or certify positive semidefiniteness of the full
1,248-variable Hessian.

Next discriminating use: compute the exact five-variable coarse Hessian and
complete degree-six line polynomial for any negative eigendirection.  A more
general 24-orbital probability kernel is justified only after that compact
screen; recursive substitution should use the certified multi-type orbital
operator rather than assuming a scalar 11-profile composition.
