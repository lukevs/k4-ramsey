# Coupled global flag pilot: strict improvement at a small hierarchy level

2026-09-29. Main-thread local experiment, following `global-anchor-pilot.md`.
Contract: `global-coupled-pilot-contract.md`. No subagents, outreach, paid work
or remote computation. All launched jobs finished.

## Result

Coupling succeeds in the N=5 to N=6 control. An exact rational vector is
feasible for all tested N=5 constraints plus nonnegative consistent N=6
extensions, with objective

    84600000023 / 3000000000000 = 0.0282000000076666...

The full coupled N=6 relaxation has the independently checked exact bound

    c4 >= 28750881 / 1000000000 = 0.028750881.

Thus the stronger constraints strictly exclude a feasible point of the
smaller relaxation. This conclusion does not depend on solver tolerances.
The moment vector is NOT a graphon construction or an upper bound for c4.

This reproduces a low-level universal lower bound, well below the previously
located published bound near 0.0296. It is not a new record, a claim of novelty,
or a test of the particular six-root Clebsch contrast at N=10.

## What is coupled

There are 34 unlabelled graphs on five vertices and 156 on six. A single
nonnegative vector y assigns probabilities to the six-vertex graphs, with
sum y=1. The five-vertex vector is x=P y, where P averages vertex deletion.
Every Gram entry uses that same y. There are no independent free moments for
individual blocks.

The objective is the expected proportion of monochromatic four-subsets.
It obeys c5^T P = c6^T, verified during generation. All constraints apply to
arbitrary graphons; no regularity, Clebsch skeleton, or symmetry of an optimizer
is assumed. Enumerating unlabelled graphs removes duplicate isomorphism
classes and does not restrict admissible graphons.

N=5 uses all canonical labelled types with one or three roots, and flags with
two or one extra vertices respectively (five PSD blocks). N=6 uses zero,
two, or four roots, with three, two, or one extra vertices (14 additional
blocks). In a product, the two sets of extra vertices are disjoint. The full
control retains the old constraints too, giving 19 blocks.

## Numerical comparisons

| Constraints | Minimum, numerical |
|---|---:|
| Full N=5 | 0.0280464060 |
| N=5 plus nonnegative consistent N=6 extension | 0.0280464054 |
| Also the two-root N=6 blocks | 0.0280464057 |
| Also all eleven four-root blocks, without other new blocks | 0.0287486320 |
| Also two-root and four-root blocks | 0.0287509249 |
| Full N=6 plus N=5 | 0.0287509251 |

Most Clarabel runs reported optimal_inaccurate; the four-root-only grouped
run reported optimal. The small differences around 0.028046406 are not
evidence of improvement. The numerical optimum is not certified to all
displayed digits. Exact rounding deliberately sacrifices about 4.4e-8 from
the full numerical objective.

Six additional ablations added each four-root type together with its colour
complement (one group is self-complementary). None individually gave a
measurable gain. All eleven together produced almost the full gain. The
empty-type block alone, or combined with the two-root blocks, also gave no
measurable gain. These are numerical statements about the tested programs,
not exact proofs that each individual addition is redundant.

The `002` run selected a nominal best group whose advantage was solver noise;
its sparse certificate is not evidence of improvement. The scientifically
relevant certificate and exact baseline separation are in `003`.

## Exact certificate and its proof interpretation

For each six-vertex graph H the checker verifies the rational inequality

    c(H) - sum_b <Q_b, C_b(H)> >= L,
    L = 28750881/1000000000,

and verifies every Q_b positive definite by rational LDL decomposition.
C_b(H) is the matrix of disjoint rooted flag-pair probabilities; for an old
block it additionally averages over the five-vertex marginal.

For a graphon W, average this identity over an induced random six-vertex
graph. The average C_b is a Gram matrix: condition on the latent roots and
their induced type, then integrate the two independent extension sets.
It is therefore PSD. Since Q_b is PSD, its inner product with that average
is nonnegative. Averaging c(H) gives exactly t(K4,W)+t(K4,1-W), proving the
displayed universal graphon bound. This implies the asymptotic multiplicity
bound. It is not an assertion that every small finite graph's injective K4
proportion exceeds L.

The implementation is an exact computer-assisted check plus this mathematical
flag-square argument; it is not a Lean/kernel-checked proof.

## Independent verification

The optimizer constructs coefficients using ordered roots and unordered
extension sets. The separate standard-library-only checker imports neither
the optimizer nor its coefficient generation. It instead averages all 720
vertex orderings and reconstructs every coefficient as an integer over 720.

It also verifies:

- Relabellings of the 156 supplied representatives cover all 32768 labelled
  six-vertex graphs exactly by disjoint isomorphism classes.
- All 19 coefficient tensors agree exactly with that independent enumeration.
- Every rounded dual matrix is symmetric and exactly positive definite.
- Every graph coefficient has nonnegative slack above the claimed bound.
- The old-level rational probability vector is nonnegative, normalized, has
  positive-definite old Gram matrices, and objective strictly below L.

The old-level witness even has a nonnegative six-vertex extension already,
so bare extension positivity alone cannot account for the separation.

Additional development controls verified G(n,1/2) Gram matrices against
independent single-flag Bernoulli-edge enumeration, yielding zero discrepancy,
and checked the random-colouring objective 1/32 and marginal identities.

## Files and reproduction

- `experiments/clebsch_bowl/coupled_flag_pilot.py`: base four-way comparison.
- `experiments/clebsch_bowl/coupled_flag_followup.py`: individual type-group
  ablations and exact dual rounding utilities.
- `experiments/clebsch_bowl/coupled_flag_interactions.py`: collective ablations
  and full rational certificate.
- `experiments/clebsch_bowl/coupled_baseline_witness.py`: old-level feasible
  rational moment vector.
- `experiments/clebsch_bowl/check_coupled_certificate.py`: independent checker.

Reports `global-coupled-pilot-001`, `-002`, and `-003` preserve primal vectors,
timings and results. `-003/full-certificate.json` contains rational dual and
coefficient data; `baseline-feasible-witness.json` contains the old-level point;
`independent-check-with-baseline.json` contains the final exact check receipt.
The coefficient tensor archive is also saved in `-001/coefficients.npz`.

Optimization commands used single-thread limits for VECLIB, OPENBLAS and OMP,
and `uv run --offline --with numpy --with scipy --with cvxpy --with networkx
python <script>`. Each solve had a 120-second limit; actual solves were under
one second. Run the final exact verification without dependencies:

    python3 experiments/clebsch_bowl/check_coupled_certificate.py

## Decision and remaining gap

The narrow hypothesis that the two-root blocks alone would help was not
supported. The broader coupling mechanism is supported, with an exact strict
separation. The useful experimental lesson is that groups of overlapping
constraints can help collectively when none of the tested groups helps alone.

This validates a small reference implementation and the rational-verification
pipeline. It does not make a nine-to-ten-vertex extension cheap: this pilot
uses all six-vertex density variables, not a scalable sparse moment closure.
The higher-order task still needs a tractable shared-variable closure and the
N=9 baseline data (or a reproduced baseline). No N=9 solution has been obtained
and no ten-vertex extension has been solved. Further work should select a
coupled family, not infer global improvement from isolated anchored squares.
