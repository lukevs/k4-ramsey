# Recent pivot references and minimal pilots

Date checked: 2026-09-27. These are mechanism transfers, not claims that the
source problems or objectives are equivalent to Ramsey multiplicity.

## 1. Positive-mass block-Cayley defects

Primary source: William J. Wesley, *New bounds for some small multicolor Ramsey
numbers*, arXiv:2509.03784v1 (submitted 2025-09-04), especially Sections 2.1
and 2.2:

- https://arxiv.org/abs/2509.03784
- https://arxiv.org/html/2509.03784v1

Wesley's finite encoding divides vertices into blocks indexed by `a` and uses a
common group `Gamma` inside every block. An edge between `(a,g)` and `(b,h)` is
determined by the block pair and `d = g h^{-1}`. Thus one orbit variable
`x[a,b,d]` replaces all edges with the same `(a,b,d)`. Undirected symmetry is

`x[b,a,d^{-1}] = x[a,b,d]`.

Off-diagonal kernels need not be inverse-closed individually; diagonal kernels
are. This is more expressive than one globally Cayley kernel.

Minimal graphon pilot: use atoms `(a,g)` and continuous probabilities
`q[a,b,d]`. Give one coarse class positive mass and free all kernels incident
to it, while tying the remaining core classes by a block permutation. Compare
against the fully tied model and a generic block model with matched parameter
count. Start with `b=3,4` and `Gamma=Z3,Z4,Z5`. Unlike the finite simple-graph
encoding, retain `q[a,a,e]` as the within-atom edge probability. A literal
constant number of exceptional finite vertices has zero graphon mass and is
not a relevant asymptotic defect; it must be promoted to a positive-mass type.

The paper's SAT clauses forbid target subgraphs and do not transfer to the
smooth `K4 + co-K4` objective. Only its orbit-variable/block mechanism is being
transferred. No public companion code was located in the paper.

## 2. Growth, witness-guided repair, and plateau escape

Primary source: Ansh Nagda, Prabhakar Raghavan, and Abhradeep Thakurta,
*Reinforced Generation of Combinatorial Structures: Ramsey Numbers*,
arXiv:2603.09172v5 (2026-04-21):

- https://arxiv.org/abs/2603.09172
- https://arxiv.org/html/2603.09172v5
- public search programs:
  https://github.com/google-research/google-research/tree/master/ramsey_number_bounds/code
- most directly relevant implementation:
  https://github.com/google-research/google-research/blob/master/ramsey_number_bounds/code/ramsey_4_16_170.py

The reusable small design, independent of AlphaEvolve, is:

1. Search a smaller structure, then carry a *valid* relation set into the next
   size or complexity rung. The cited script does not carry an arbitrary
   near-miss best state.
2. On 75% of moves, attempt to choose a relation occurring in a current bad
   witness; fall back to a random move when no suitable witness is available.
3. After 8,000 non-improving iterations, apply a structure-preserving
   unit-multiplier automorphism or relabeling, with probability 0.3 add one to
   three random relation perturbations, and reheat annealing by a factor 1.5.
4. Keep multiple seed families and retain a near-miss prospect as well as the
   current valid winner.

For multiplicity, replace a forbidden-clique witness by a sampled
high-contribution monochromatic `K4` in either color, choose one of its six
relation bins, and evaluate the exact objective delta. Replace the paper's
lexicographic zero-violation score with
`t(K4,W) + t(K4,1-W)`. There is no validity threshold or independent-set phase.

The source explicitly reports weak transfer between different Ramsey cells.
Its public scripts are therefore useful as compact pseudocode, not as directly
reusable optimizers for this objective. No AlphaEvolve dependency is needed for
the pilot.

## 3. Feinstein status boundary

The Technion seminar abstract dated 2026-01-21 is still the only located direct
public statement:

- https://math.technion.ac.il/events/noam-feinstein/

It states randomized, structured, symmetric constructions with
`c(4) < 0.030139`, but gives no exact value, witness, code, block count, group,
or probability law. No public full paper, arXiv preprint, exact witness, or
thesis PDF was located as of the date above. We should not identify any pilot
with Feinstein's mechanism absent a public artifact.
