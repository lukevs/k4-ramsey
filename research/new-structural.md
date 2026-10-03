# H-STRUCT-003: heterogeneous two-type recursive constructions

2026-09-27, bounded independent structural research round. This is not another
edge-search heuristic and does not modify diagonal probabilities in the current
768-vertex template. No source file belonging to earlier screens was edited.

## Hypothesis and prediction

Assign different recursive child types to different vertices of a small outer
graph. The resulting vertex-dependent recursive construction can escape the
restriction of repeating one identical core everywhere. Prediction: some mixed
construction has smaller exact density than **both** corresponding homogeneous
recursive constructions. A stronger success would improve the historical
`K4 XOR M4 XOR nested(Q9)` construction, then the current bound.

The general composition/profile method is established in
[Even-Zohar and Linial, sections 2–3](https://arxiv.org/html/1312.1205).
Our typed-recursion implementation is an adaptation of the same partition
argument; no claim of novelty or recovery of Feinstein's announced method.

## Exact equations

There are two types i=0,1. Rule i consists of a loopless graph G_i with m_i>=2
vertices and a child-type assignment c_i(v). Draw each vertex as an independent
infinite path; at each level choose uniformly among the current rule's vertices.
Different blocks get the outer edge color; paths in the same block recurse
using that block's child type. Coincidence for infinitely many levels has
probability zero. This defines a graph-limit construction with equal branching
masses, not fractional edge-color probabilities.

Let q_i,t(H) be its exact labeled t-vertex profile, for t=2,3,4. Partition a sampled
outer t-tuple by equal outer vertices. Cross-group edges are fixed. Within a
group S of size s, the internal pattern has distribution q_c,s; distinct groups
use independent tail samples, even when their child types coincide.

All partitions except the one-block partition use only profiles of orders <t.
Writing those known contributions as r_i,t(H) leaves

```
q_i,t(H) - sum_j M_t[i,j] * q_j,t(H) = r_i,t(H)
M_t[i,j] = #{v in G_i: c_i(v)=j} / m_i^t.
```

Solve one 2×2 rational system per pattern, bottom-up through t=2,3,4. Each row
sum of M_t is m_i^(1-t)<=1/2, so the linear system is invertible by contraction
and its physical fixed point is unique. The lower-order recursive equations
then establish the limiting interpretation. This argument is mathematical
reasoning and executable rational checks, not a Lean formalization.

## Implementation and independent review

- [new_profiles.py](../experiments/structural/new_profiles.py) compresses outer
  tuples into typed partition recipes, contracts lower-order profiles, and
  solves the exact limiting equations. It checks normalization, nonnegative
  coordinates, and every coordinate of the defining equation.
- [test_new_structural.py](../tests/test_new_structural.py) compares 12 randomly
  chosen heterogeneous rules against explicit depth-two adjacency expansion
  for both root types; checks reduction to the older independent 11-class
  homogeneous solver; and checks finite-depth convergence. Three tests pass
  in 0.37s.
- A separate worker reviewed the factorization, all-in-one-block coefficient,
  contraction proof, and unequal-rule-order interpretation. No blocking issue
  was found. Explicit unweighted materialization deliberately requires equal
  rule orders; unequal orders instead describe nested probability masses.

## Bounded screen and result

[new_screen.py](../experiments/structural/new_screen.py) evaluated the objective
after XOR with the fixed historical `K4 XOR M4` factor. It examined:

1. All 1,024 pairs of order-three typed rules: four unlabeled outer graphs and
   eight child assignments per rule. Both root types give 2,048 evaluations.
2. Q9 versus each of a single-edge addition and deletion, with 64 heterogeneous
   assignment pairs per perturbation, evaluating both roots: 256 evaluations.

Total: **2,304 exact values in 3.62 seconds**. **548** improve both homogeneous
controls, supporting the basic heterogeneity mechanism in weak constructions.
The largest such gain comes from alternating the empty and complete order-three
cores: density 171/4160 versus 27/512 for either homogeneous control. This is
far from competitive and resembles familiar alternating recursive composition,
not a novel-record claim.

The best value in the screen was

```
876512858070511 / 28942355436134400
```

from Q9 with one vertex recursing into a one-edge-perturbed Q9, whose vertices
all recurse back to Q9. It is **worse** than the historical 1411/46592 by
`123732397177/202596488052940800`, about 6.11e-7. It is also worse than our current
local incumbent. Thus there is no numerical bound improvement.

The immutable [screen report](../experiments/structural/new_screen_001.json)
contains exact values, both homogeneous controls, reconstructible rules, seed,
counts, elapsed time, and source hashes. Evidence level: exact rational screen
with independent tiny enumeration and cross-review; no independent Lean check.

## Decision and unresolved gap

The basic heterogeneity hypothesis is supported in weak small-core cases, but
unsupported as an improvement to the competitive Q9 family sampled here. Retire
this parameter bank during the pilot rather than enlarge the same sweep. A
useful continuation requires a different source of strong factors or a
mechanism predicting favorable heterogeneous assignments. No global statement
about all typed recursions follows from these finite screens.

No candidate can be promoted through the existing fixed-order checker merely
because its recursive profile is exact. A new construction needs either a
materialized admissible finite witness or an independent recurrence/limit
certificate; that remains a separate validation gap.
