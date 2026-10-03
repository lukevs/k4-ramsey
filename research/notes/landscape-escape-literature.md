# Escaping deceptive combinatorial landscapes: targeted literature note

Date: 2026-09-27. Scope: read-only primary-source review. The goal is to
identify mechanisms that are materially different from the current exact
single-coordinate support-growth/repair sweep. No experiment was run.

## 1. Population annealing / replica exchange — recommended first pilot

Wang, Machta, and Katzgraber, *Comparing Monte Carlo methods for finding
ground states of Ising spin glasses: population annealing, simulated annealing
and parallel tempering*, first submitted 2014-12-05
([arXiv:1412.2104](https://arxiv.org/abs/1412.2104)), directly compare the
three methods on frustrated spin-glass ground-state search. Population
annealing was substantially more efficient than simulated annealing and
comparable to parallel tempering. Its relevant mechanism is not merely many
restarts: a population is cooled and **resampled at every temperature**, so
low-energy families replicate while diversity can persist across barriers.

Barzegar, Pattison, Wang, and Katzgraber, *Optimization of population
annealing Monte Carlo for large-scale spin-glass simulations*, submitted
2017-10-25 ([arXiv:1710.09025](https://arxiv.org/abs/1710.09025)), explicitly
describes population annealing as an inherently parallel algorithm for
`k`-local Boolean Hamiltonians and notes applicability to higher-order
Hamiltonians. This is the closest abstraction to the degree-at-most-six
Ramsey objective. It also gives useful diagnostics: population/family entropy,
adaptive schedules, and dynamic population sizes.

Cheap matched test on the 768-vertex finite witness:

1. Use 16 or 32 replicas and the existing exact cached single-edge deltas.
2. At each inverse-temperature step, perform a fixed number of Metropolis
   proposals per replica, then systematic-resample with weights
   `exp(-delta_beta*(E-E_min))`, using log-sum-exp arithmetic.
3. Adapt `delta_beta` so the resampling effective sample size is near half the
   population; finish with the same deterministic local quench for every
   surviving family.
4. Compare against independent simulated-annealing/tabu runs with exactly the
   same number of native delta evaluations. Record best exact numerator,
   number of distinct quenched basins, family entropy, and time to first
   improvement.

This differs from growth-repair because it searches the unrestricted finite
binary graph with an interacting population and deliberately transports
states across energy barriers. Growth-repair deterministically activates one
coarse graphon support coordinate at a time.

Assumptions and cautions: the finite objective is dense and sixth order but
the method only requires exact local energy differences, which we already
have. Temperature must be calibrated to the observed delta scale. Do **not**
import isoenergetic cluster moves without a new derivation. Zhu, Ochoa, and
Katzgraber's 2015 method ([arXiv:1501.05630](https://arxiv.org/abs/1501.05630))
gets rejection-free conservation from a pairwise Ising Hamiltonian and
nonpercolating overlap clusters; neither property follows for our dense
higher-order interaction hypergraph. Plain population annealing or replica
exchange is the sound pilot.

## 2. Exact large-neighborhood repair — promising, but a larger implementation

Huang, Ferber, Tian, Dilkina, and Steiner, *Local Branching Relaxation
Heuristics for Integer Linear Programs*, submitted 2022-12-15
([arXiv:2212.08183](https://arxiv.org/abs/2212.08183)), formulate large
neighborhood search as choosing a subset of variables, fixing the rest, and
optimizing the induced subproblem. Their LP-guided variants trade some
neighborhood quality for large speedups and use randomized/adaptive variants
to escape later local minima.

There is direct Ramsey precedent for exact optimization hybrids: Coniglio et
al., *An Integer Programming Approach to Compute Lower Bounds for Ramsey
Numbers Using Circulant Graphs*, submitted 2026-08-19
([arXiv:2608.18769](https://arxiv.org/abs/2608.18769)), use a symmetry-reduced
integer program plus branch-and-cut and common-neighborhood separation to
improve many circulant Ramsey lower bounds. It is a different Ramsey objective
and restricted family, so it supports the mechanism rather than our result.

Cheap matched discriminator: select 18–24 binary edges whose cached deltas and
mixed interactions are strongest, freeze every other edge, and exactly search
the resulting restricted degree-six pseudo-Boolean objective. Compare the best
joint move with the same number of single-edge evaluations. A first pilot can
enumerate Gray-code assignments with exact sequential cached updates and full
rollback/recount gates; only a positive signal justifies branch-and-bound or an
ILP linearization.

This differs from growth-repair by optimizing a coupled Hamming block exactly,
so it can cross a barrier requiring several individually bad flips. It also
differs from the already tested two-switch/short plateau moves by allowing a
larger unrestricted joint neighborhood. Its main risk is variable selection:
the useful barrier may not be contained in a 24-edge block.

## 3. Learned/program-evolved policies — evidence supports a narrow pilot only

Mehrabian et al., *Finding Increasingly Large Extremal Graphs with AlphaZero
and Tabu Search*, submitted 2023-11-06
([arXiv:2311.03583](https://arxiv.org/abs/2311.03583)), improved extremal
graph bounds with both AlphaZero and tabu search, but the clearest transferable
gain was a **curriculum**: initialize larger graphs from good smaller graphs.
Their incremental tabu search performed similarly to incremental AlphaZero and
substantially outperformed the cross-entropy method as size grew.

The negative evidence is unusually relevant. Parczyk, Pokutta, Spiegel, and
Szabó's Ramsey-multiplicity study
([arXiv:2206.04036v3](https://arxiv.org/html/2206.04036v3), originally 2022)
reports that cross-entropy / neural construction was much slower and weaker
than tabu or simulated annealing on their Ramsey and extremal-graph instances.
Thus a large learned policy is not the next experiment.

A bounded alternative inspired by program-search work is to evolve only a
small, interpretable move-ranking expression over already exact features
(delta, motif incidence, recency, elite disagreement), while the immutable
native evaluator grades complete trajectories. FunSearch demonstrated this
"evolve the critical heuristic inside a fixed program skeleton" pattern on
extremal combinatorics in Romera-Paredes et al., *Mathematical discoveries from
program search with large language models*, published 2023-12-13
([Nature 625, 468–475](https://doi.org/10.1038/s41586-023-06924-6)).

Matched gate: preregister a tiny grammar with at most 10 coefficients/operators,
train on several frozen lesser seeds, and evaluate once on a held-out strongest
seed under the same native-delta budget as tabu. Stop unless the held-out
result beats tabu repeatedly. This is different from growth-repair because it
searches over trajectory policies rather than graphon coordinates. It is lower
priority than population annealing: direct Ramsey evidence warns that learned
construction policies can spend far more compute than they save.

## Priority

1. Population annealing (or a small replica-exchange variant): lowest setup,
   directly matched to rough higher-order Boolean landscapes, easy parallelism.
2. Exact 18–24-edge large-neighborhood repair: strongest barrier-crossing move,
   but more implementation and variable-selection risk.
3. Tiny program-evolved ranking policy only after the first two; do not build a
   neural graph generator.

