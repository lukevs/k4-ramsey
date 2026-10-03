# Deeper literature pass — 2026-09-27

User requested broader research; this note proposes tests, not new results.
Research skill applied: mechanisms, mismatches, cheap controls; no framework
installation or training campaign authorized by this literature request.

## Priority: learn new starting basins

[PatternBoost](https://arxiv.org/html/2411.00566), November 2024, alternates
classical local optimization with transformer training on good constructions,
then feeds generated seeds back into optimization. Public code is linked in
the paper. This differs from both evolving search programs and repairing one
incumbent. Its examples also expose significant compute costs and sensitivity
to representation; it is not evidence of success for K4 multiplicity.

Proposed gate: first build a diverse, deduplicated bank of local minima and
test whether a compact learned seed distribution produces better *post-repair*
results than empirical resampling plus matched perturbations. Include training
cost. A simpler statistical distribution would be an adaptation, not a literal
PatternBoost reproduction. Do not silently train on only one incumbent basin.

## Priority: evaluate move sequences by completed rollouts

[Taieb et al., Automated Refutation with Monte Carlo Search](https://www.lamsade.dauphine.fr/~cazenave/papers/ArticleLioraLNCS.pdf),
LION 2025 work with 2026 proceedings, compares constructive NMCS, NRPA and GRAVE
on spectral graph conjectures. Its tree restrictions are important to the
reported successes and do not transfer to our dense two-color problem.

Proposed gate: a bounded reconstruction sequence over a compact quotient,
ranked by completed asymptotic K4 score; compare rollout-policy adaptation with
random rollouts and greedy reconstruction under matched evaluation budgets.
Unlike immediate repair, intermediate moves may look bad but have good completions.

## Profile-to-construction bridge

[MomentNet](https://arxiv.org/html/2506.04206), June 2025, fits a graphon
representation to motif densities. Our transfer would be an inverse-construction
search from promising profiles, not statistical recovery from observed graphs.
Start with a small explicit symmetric step graphon and motif-fitting loss;
round and independently recount any promising witness. A few matching moments
neither identify a unique graphon nor certify a target profile is realizable.

## Useful implementation reference, not a new construction theorem

[RLGT](https://arxiv.org/html/2602.17276), February 2026 / April revision,
provides modular graph environments and multiple RL algorithms. Inspect reusable
interfaces if learning becomes worthwhile; do not replace our fast checker or
spend the remaining research window building a general RL stack.

## Negative evidence to retain

## Additional distinct leads from the parallel review

[Population annealing](https://arxiv.org/abs/1412.2104), 2014/2015, and its
[higher-order implementation study](https://arxiv.org/abs/1710.09025), 2017/2018,
suggest maintaining and resampling a population across a cooling schedule.
Cheap test: 16–32 replicas, equal total objective-delta budget against independent
annealing, with lineage diversity and distinct final basins recorded. This is
older useful research, not a recent Ramsey breakthrough. Dense high-order
interactions invalidate blindly importing rejection-free pairwise cluster moves.

[Coniglio et al.](https://arxiv.org/html/2608.18769v1), August 19, 2026, presents
symmetry-projected integer programming and strengthened branch-and-cut for
circulant Ramsey avoidance, with explicit independently checkable certificates.
For us this supports a solver-guided coordinated move design, not importing
zero-clique constraints into multiplicity minimization. The completed 15-bit
enumeration pilot is not a reproduction of this method. Inspect code/solver
requirements and derive a count-budget model before a new pilot.

## Direct negative evidence

[Parczyk et al., section 5.3](https://link.springer.com/article/10.1007/s10208-024-09675-6)
reports inferior quality/runtime of tested neural reinforcement approaches versus
simulated annealing and tabu search on medium/large instances. This is directly
relevant but does not rule out later population/representation approaches.

These are new leads for our recorded queue, not claims of mathematical novelty,
new bounds, or reasons to extend the existing compute deadline.
