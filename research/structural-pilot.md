# Structural pilot — 2026-09-27

## Question and decision

Can cheap exact profiles uncover competitive constructions in a family quite
different from editing the published 768-vertex seed? The initial answer is
**no for the two bounded families below**. Retire these small-factor families
for now; do not spend the pilot budget on a larger undirected parameter sweep.
The reusable arithmetic succeeded and reproduces published historical results.

This work does not improve the current incumbent, prove global optimality, or
rule out more sophisticated XOR, recursive, or randomized constructions.

## Targeted literature follow-up

The [Technion seminar announcement](https://math.technion.ac.il/events/noam-feinstein/)
still provides only a rounded bound, c4 < 0.030139, and describes structured
random constructions. Additional author/title/arXiv/thesis searches found an
earlier [RSA 2025 conference abstract](https://dmg.tuwien.ac.at/rsa2025/)
for joint work of Noam Feinstein and Chaim Even-Zohar, but no explicit graph,
preprint, algorithm, or usable construction description. This is a failed
retrieval, not evidence that no public witness exists. No authors were contacted.

[Even-Zohar and Linial, sections 2–3](https://arxiv.org/html/1312.1205)
supply the actionable mechanism: repetitive labeled profiles convolve under
XOR, their Fourier transforms multiply, and composition acts linearly on the
inner profile. Nested limits are stationary profiles. Our implementation uses
64 exact labeled pattern coordinates and reduces the stationary equation to
11 isomorphism classes. Repetitions are retained throughout. This is an
implementation of known methods, not a novelty claim.

## Implementation and independent small tests

- [profiles.py](../experiments/structural/profiles.py): integer repetitive profiles,
  exact Walsh-Hadamard transform, XOR products, explicit graph materialization,
  composition transition, and rational nested-profile stationary solution.
- [test_structural.py](../tests/test_structural.py): 12 random tiny XOR checks,
  all 64 pairs of labeled three-vertex graph composition checks, repetitions and
  invalid-input checks. Explicit product adjacency enumeration is compared with
  profile arithmetic, rather than comparing two invocations of the same formula.
- Historical regression fractions reproduced exactly: 11411/373248,
  3769/124416, and the infinite nested limit 1411/46592. Four tests pass in 0.14s.

The composition calculation groups outer sampled tuples by which positions
share an outer vertex. Edges within those groups are inherited from the inner
profile; all other edges are fixed by the outer tuple. Solving the induced
11-class stationary linear system uses rational Gaussian elimination and checks
nonnegativity, normalization, and the full 64-coordinate fixed-point equation.
Its mathematical interpretation uses the probability that four independent
infinite words share increasingly long prefixes tending to zero.

These are exact Python calculations and tiny independent-enumeration tests,
**not** independent Lean certificates or a formal proof of the general operator.

## H-STRUCT-001: small fixed-order expression family

Prediction: at least one exact construction improves the initial 768-vertex
seed; otherwise this factor bank is too weak for further pilot effort.

Take the XOR product A × B × C, with orders 3, 16, 16. A ranges over all
four order-three graph profile types. Each order-sixteen factor is an XOR or
composition of two arbitrary four-vertex graphs. Exhaustively enumerating the
64 labeled order-four graphs yields 11 profiles; the derived bank has 166
distinct order-sixteen profiles. Exchange symmetry of B and C leaves
**55,444** exact profile evaluations. All diagonals remain blue, with 768 unit
weights, so this finite family is in our current construction domain.

Best: **10660872192 / 768^4 = 3389/110592**, approximately 0.03064.
This is worse than the seed and incumbent. The screen completed in 1.79s,
including factor construction. It did not materialize or independently certify
a full 768-vertex candidate because none was competitive.

Decision: unsupported in this precisely enumerated family; retire pending a
better structural factor source. Different expression shapes were not exhausted.

## H-STRUCT-002: small recursive cores

Prediction: combining a nested small core with two arbitrary order-four XOR
factors produces a value below the published historical 1411/46592.

All 1,024 labeled five-vertex graphs yield 34 different profiles; evaluate each
nested limit combined with an unordered pair of order-four graph profiles.
**2,244** exact constructions were evaluated. Best: **487/15872**, approximately
0.03068, worse than the historical construction. This second screen concerns
infinite recursive constructions and is explicitly outside the fixed-order
Lean checker's current domain. No candidate promotion is implied.

Decision: unsupported for these cores and factors; a larger random sweep of
the same family is not justified. This screen plus the finite screen took 4.15s.

## Reproduction and next mechanism

```
PYTHONPATH=src:. python3 -m unittest tests.test_structural -v
PYTHONPATH=src:. python3 -m experiments.structural.screen --out experiments/structural/new-screen.json
```

The original immutable [screen result](../experiments/structural/pilot-screen-001.json)
records exact values, factor descriptors, counts, timing, and source hashes.
No subprocess remains running.

The worthwhile structural follow-up is **randomized or heterogeneous internal
blocks**, not merely more small XOR factors: a fractional block construction
can alter the full six-edge profile while retaining a compact description.
That is a mechanism-level hypothesis inspired by the announced random
constructions, not an assertion about Feinstein's actual construction. A cheap
next test would derive a rational profile for one explicitly parameterized
block-random model and compare its homogeneous endpoints and first derivatives;
independent checking must be extended before promoting such a bound.
