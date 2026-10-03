# Overlapping rooted constraints: a smaller useful family

2026-09-29. Main-thread follow-up under `global-overlap-pilot-contract.md`.
All local jobs finished. No new global record, N9/N10 run, package installation,
or remote computation.

## A small coupled family succeeds

The earlier pilot found no measurable improvement from any one of the six
colour-complement groups of four-root types. We tested all 15 pairs with the
same N5 constraints, the same 156 nonnegative N6 density variables, and the
same marginal identities. Four-root types were the only new blocks.

The best pair consists of:

- Type 3: two adjacent edges plus an isolated vertex, and its complement,
  type 15: a triangle with a pendant edge.
- Type 7: the three-leaf star, and its complement, type 11: a triangle plus
  an isolated vertex.

These four Gram blocks plus the five old blocks give numerical value
0.028390031457. Exact dual rounding gives

    c4 >= 851700121 / 30000000000 = 0.0283900040333333...

The independent checker recounted all coefficients over all 32768 labelled
six-vertex graphs, checked rational positive definiteness and coefficient
slacks, and rechecked the old-level rational moment vector with objective
0.0282000000077. This proves strict strengthening over that old relaxation.
The individual-group no-gain statements remain numerical, not exact redundancy
theorems. Most solver outputs carry optimal_inaccurate; certification bypasses
that uncertainty for the displayed rational bound.

For comparison, all eleven four-root types give about 0.028748632; the entire
N6 extension gives about 0.028750925. The pair recovers roughly half the
four-root improvement over the approximately 0.028046406 baseline, using four
new blocks instead of eleven. This establishes a smaller useful selection,
not a minimum-cardinality selection among arbitrary flags or block bases.

Other pair results worth retaining: groups (1,31)+(3,15) give approximately
0.028197753; (3,15)+(13) approximately 0.028145935. All pairs with a clearly
visible gain contain (3,15). A tiny 1.3e-7 numerical increase for
(3,15)+(12,30) is not independently certified and should not drive conclusions.

## Direct reproduction of the literature example

Section 7 of [Local flag algebras](https://arxiv.org/html/2607.12461v1#S7)
constructs a triangle-free degree-five graph from a pentagonal prism whose
selected root saturates the same pentagon bound as Clebsch. We rebuilt that
example and the Clebsch graph, then enumerated every five-subset independently
of the attachment-count formula. The two counting routes agree exactly.

| Graph | Pentagons overall | Pentagons through individual vertices |
|---|---:|---|
| Clebsch | 192 | 60 at each of 16 vertices |
| Prism-derived counterexample | 117 | 60 once, 41 five times, 32 ten times |

Thus the selected root alone hides a deficit visible from its neighbours.
This is a reproduction of their mechanism, not a new extremal theorem. The
maximum-degree-five and triangle-free hypotheses do not hold for arbitrary
colour classes in our K4 problem; we transfer the idea of testing compatible
neighborhoods, not their numerical inequality.

## Independent software reproduction status

Neither `sage` nor `csdp` was found on PATH. The
[FlagAlgebraToolbox installation instructions](https://arxiv.org/html/2601.06590v1#S1.SS2)
describe a SageMath fork tested on Linux and a source build requiring at least
10 GB. The current machine is macOS. A large build was not launched as part
of this small pilot.

`experiments/clebsch_bowl/reproduce_toolbox.sage` is prepared from the documented
API. It minimizes the induced K4 plus empty-four objective at level six,
first numerically and then with exact rounding. It is explicitly UNEXECUTED;
this is not a completed second-software reproduction. Expected comparison
is the full N6 value around 0.0287509, allowing for rounding and any hierarchy
convention differences. The documented upstream revision is 9a9f84d.

## Artifacts and next decision

All receipts are in `reports/global-overlap-pairs-001/`: the 15 primals and
selected certificate in `result.json` / `full-certificate.json`, metadata,
the old feasible point, `independent-check-with-baseline.json`, and the
exact local comparison `local-example.json`.

Scripts:
- `experiments/clebsch_bowl/overlap_pair_pilot.py`
- `experiments/clebsch_bowl/check_local_overlap_example.py`
- `experiments/clebsch_bowl/check_coupled_certificate.py` now accepts an
  optional report-directory argument; its default behavior is unchanged.

H-GO1 is supported. A small family can be selected for collective usefulness
instead of ranking types only by their individual effect. Before extrapolating
to N9/N10, the outstanding obstacle is still a tractable shared-variable
closure: these small tests retain ALL 156 six-vertex density variables.
No scaling claim follows from merely reducing the number of PSD blocks.
