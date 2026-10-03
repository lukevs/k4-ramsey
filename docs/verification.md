# Verification details

See the [project README](../README.md) for setup and run commands. Paths and
commands below are relative to the repository root.

## Formal Clebsch construction

`lean/K4Ramsey/Constructions/Clebsch192/Bound.lean` is an end-to-end finite upper-bound theorem
for the compact **192-part** Clebsch construction at `p = 32/41`, `h = 22/41`:

```text
For every n >= 4, there exists a red/blue coloring on n vertices with
monochromatic K4 density <= 1013294255057839 / 33620705806123008
                        < 0.030139.
```

The construction is defined directly in group coordinates in
`lean/K4Ramsey/Constructions/Clebsch192/Model.lean`; it needs no files from `reports/`. The proof chain is:

1. `Graphon.lean` defines the literal six-edge sum, including repeated template
   labels, proves the pair factorization, and proves the Cayley rooting identity.
2. `Clebsch192Certificate.lean` checks symmetry and probability bounds and
   evaluates the literal rooted sum using Lean's `native_decide`.
3. `FiniteProbability.lean` proves finite independence and averaging.
4. `Realization.lean` proves that every symmetric rational probability table
   gives an actual coloring no worse than its density at **every** order >= 4.
   It uses independent random labels and edge colors; no asymptotic
   approximation or assumed realization theorem is needed.
5. `Clebsch192Bound.exists_coloring` combines those results. Density uses
   uniformly sampled ordered distinct vertices: every four-set has the same
   24 orderings.
6. `Asymptotic.lean` defines the actual finite minimum over all colorings and
   bounds its upper limit, without assuming convergence. It also proves that
   a uniform finite bound passes to any limit of those minima.
   `Clebsch192Bound.ramsey_upperLimit_bound` and `ramsey_limit_bound`
   specialize these results to the construction.
   Convergence of the minimum-density sequence itself is not proved here;
   neither the upper-limit bound nor finite-order existence requires it.

Build and inspect the trust boundary:

```sh
just lean-build
just audit
```

Lean and mathlib are both pinned to `v4.34.1`. The first build downloads
mathlib and its cache. The just recipes use `scripts/lean.sh`, which selects
the `lean/` package and supports the repository-local elan installation.
Use `just lean-build`, rather than invoking the numerical certificate directly
before its imported computational modules have been compiled.

The general counting and realization proofs use standard Lean axioms only;
the concrete arithmetic additionally trusts native compilation/evaluation.
There are no `sorry` placeholders or assumed numerical certificates in this
proof chain. A finite-order bound valid for every n >= 4 also bounds any
asymptotic limit of the minimum densities.

**Scope:** this is not yet a numerical formal certificate for the stronger
**3,840-part** refinement with reported value approximately
`0.030138887566497220`. The following parts of that refinement now compile:

- `Final3840Data/` embeds the witness itself, not a supplied count. Its ten
  small source chunks store the 1,248 fractional 20-by-20 blocks; the hard
  blocks follow the canonical Clebsch rule in `Final3840Model.lean`.
- `Final3840Validity.lean` checks symmetry, probability bounds, data dimensions,
  and exact zero row means of the centered perturbations with `native_decide`.
  It proves the existence of actual finite colorings bounded by the literal
  density of this table.
- `TensorK4.lean` and `CenteredExpansion.lean` prove the general counting
  reduction: of the 64 expanded terms, only the base, four triangles, three
  four-cycles, six diamonds, and the all-perturbation K4 remain. The proofs
  include repeated labels and use no native evaluation. The generated proof
  script only selects reindexings; Lean checks each reindexing and cancellation.
- `Final3840Reduction.lean` applies that identity to both colors of this
  actual witness. `Final3840Bound.lean` proves the upper-limit bound by its
  **symbolic** density.
- `Final3840Count.lean` implements sparse integer sums with stored two-edge
  contraction arrays. `Final3840CountCorrect.lean` proves cache lookup,
  factorization, and the correctness of every support guard.
- `Final3840Arithmetic.density_eq_count` proves that these executable integer
  sums, with the exact denominator `65536^6 * 3840^4`, equal the literal density.
  `Final3840SymmetryProof.baseRoot_eq` reduces the base contribution to one
  rooted count. These close the optimized-counter correctness gap.

**Remaining gap:** finish the full numerical run and use `native_decide` to
certify that the proved integer expression equals the reported exact rational
`8450462766487926638466333426306607129 / 280384030360880691940646801777885184000`.
The external numerical report is not used as a Lean premise. Thus the symbolic
upper-limit theorem must not be presented as a certificate of that number.

The compiled single-slice smoke test completed. The full run was interrupted
at the user's request to ship this checkpoint; no complete total was obtained.
Resume the diagnostic run with `just recount`. This runner prints
progress every 16 coarse vertices and uses roughly 700 MB in the observed run.
Its output alone is not a theorem: the next step is a numerical Lean certificate
and substitution into `density_eq_count` and the existing upper-bound theorem.

`SignRefinement.lean` also proves the local six-edge identity for balanced
two-way splits. The centered-block route above handles the complete 20-way
refinement directly. Structural checks are separate from the still-unverified numerical contraction
certificate.

The embedded witness comes from SHA-256
`05302cbc635e939cc41f4ba019cdcba80199b0b83563100bac0b1a0d9fff1a29`.
`scripts/generate_final3840_data.py` checks this hash and every block mean when
regenerating the data; normal Lean builds do not need Python, NumPy, or the
large original JSON. `scripts/generate_tensor_expansion.py` regenerates the
64-term algebraic proof without reading any numerical report.

The older published-graph bitset checker
also still lacks a proof connecting its implementation to that objective.
The result above improves the 2022 benchmark; it makes no claim of priority
over newer announced bounds.

## Published 768-vertex graph

The Lean project checks the published 768-vertex Cayley template from Parczyk,
Pokutta, Spiegel, and Szabó. It computes the exact balanced-blow-up numerator
`10487165184`, with denominator `768^4`, equivalent to
`4551721 / 150994944 ≈ 0.0301448570` (about 3.0145%).

McKay's later reference numerator is `10486266368`. Its adjacency matrix is
not included here, so **this project does not reproduce that improved bound**.

## Performance and verification scope

`precompileModules = true` is essential: Lean loads compiled machine code for
the imported counter. The data uses twelve `UInt64` words per adjacency row;
all accumulated counts use arbitrary-precision `Nat`. The comparison theorem
rewrites with `exact_numerator`, reusing its result instead of counting again.
The 64-bit shift boundary is handled explicitly because UInt64 shifts wrap
their shift count modulo 64.

Historical timings for the published-only project, before the new mathlib
formalization: a clean build of the library, tests, and executable
took 9.15 seconds; the certificate proof module took 1.1 seconds, and the
standalone executable took about 0.7 seconds wall time. These are observed
timings, not a guarantee of optimality or identical speed on other machines.

Lean verifies the matrix shape, symmetry, clear diagonal, padding bits, edge
count, and the computed numerator. Tests exhaust all 1,024 simple graphs on
five vertices against an independent ordered-quadruple oracle. Complete and
empty graphs exercise word boundaries at 63/64/65 and 127/128/129 vertices.

This is a verified execution of a counting program via `native_decide`.
Lean 4.34.1 records native-evaluation axioms, visible in `lean/Audits/Published.lean`; compilation
and runtime are part of the trust boundary. The general theorem connecting
this optimized bitset program to the literal tuple sum has **not** been
formalized. The new general realization theorem above supplies the
finite-to-asymptotic mathematical bridge, but the published certificate has
not yet been connected to it. Regression tests do not replace the missing
counting proof.

## Data provenance

Source: [New Ramsey Multiplicity Bounds and Search Heuristics,
Theorem 1.1](https://arxiv.org/html/2206.04036v3), and the authors'
[Zenodo archive](https://zenodo.org/records/6602512) (CC BY 4.0),
`graphs.zip`, member `graphs/c4.graph6.txt`.
Archive SHA256: `6ff8a2496c545e86def3a12bd69ef557c50a890c732a8506d30b1bbe8467ec89`.

`lean/K4Ramsey/Constructions/Published768/Data.lean` embeds the graph supplied by the local hill's
published example. To regenerate this representation:

```sh
just generate-certificate \
  .autolab/hills/clique-cluster-ramsey-multiplicity/examples/published_cayley_768/solution.json \
  lean/K4Ramsey/Constructions/Published768/Data.lean --namespace Published768
```

The checker currently supports unit weights and blue diagonals, precisely the
published scenario. The generator rejects inputs outside that scope.
