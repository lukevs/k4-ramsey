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
`lean/K4Ramsey/Constructions/Clebsch192/Model.lean`; it needs no files from `reports/`.
Paths below are relative to `lean/K4Ramsey/`. The proof chain is:

1. `Core/Graphon.lean` defines the literal six-edge sum, including repeated template
   labels, proves the pair factorization, and proves the Cayley rooting identity.
2. `Constructions/Clebsch192/Certificate.lean` checks symmetry and probability bounds and
   evaluates the literal rooted sum using Lean's `native_decide`.
3. `Core/FiniteProbability.lean` proves finite independence and averaging.
4. `Core/Realization.lean` proves that every symmetric rational probability table
   gives an actual coloring no worse than its density at **every** order >= 4.
   It uses independent random labels and edge colors; no asymptotic
   approximation or assumed realization theorem is needed.
5. `Clebsch192.exists_coloring` combines those results. Density uses
   uniformly sampled ordered distinct vertices: every four-set has the same
   24 orderings.
6. `Core/Asymptotic.lean` defines the actual finite minimum over all colorings and
   bounds its upper limit, without assuming convergence. It also proves that
   a uniform finite bound passes to any limit of those minima.
   `Clebsch192.ramsey_upperLimit_bound` and `ramsey_limit_bound`
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

## Formal 3,840-class bound

The **3,840-part** refinement has the same kind of end-to-end proof:

```text
For every n >= 4, there exists a red/blue coloring on n vertices with
monochromatic K4 density
  <= 8450462766487926638466333426306607129 / 280384030360880691940646801777885184000
   = 0.030138887566497220...
```

Paths below are relative to `lean/K4Ramsey/`. The proof chain is:

1. `Constructions/Final3840/Data/` embeds the witness itself, not a count: ten
   source chunks store the 1,248 fractional 20-by-20 blocks, and
   `Constructions/Final3840/Model.lean` gives the remaining blocks by the
   Clebsch rule.
2. `Constructions/Final3840/Validity.lean` checks symmetry, probability bounds,
   dimensions, and zero row means of the centered blocks with `native_decide`.
3. `Counting/TensorK4.lean` and `Counting/CenteredExpansion.lean` prove the
   general counting reduction: of the 64 expanded terms, only the base, four
   triangles, three four-cycles, six diamonds, and the all-perturbation K4
   remain. These proofs include repeated labels and use no native evaluation.
4. `Constructions/Final3840/Reduction.lean` applies that identity to both
   colors of the witness, and `Constructions/Final3840/Bound.lean` proves the
   finite and asymptotic bounds in terms of its density.
5. `Constructions/Final3840/Count.lean` implements sparse integer sums, and
   `CountCorrect.lean` proves them correct. `Arithmetic.lean` proves
   `Count.density_eq_count`: these sums, over the denominator
   `65536^6 * 3840^4`, equal the density. `SymmetryProof.lean` proves
   `baseRoot_eq`, which reduces the base term to a single rooted count.
6. `Constructions/Final3840/Certificate.lean` evaluates that integer
   expression with `native_decide`, obtaining
   `519196432373018212667371525712277942005760`, and `exact_density` turns it
   into the exact fraction above by kernel-checked rational arithmetic. No
   external report is a Lean premise.
7. `Constructions/Final3840/NumericalBound.lean` proves `exists_coloring_exact`
   (the statement above for every n >= 4), `ramsey_upperLimit_exact_bound`
   (without assuming convergence), and `ramsey_limit_exact_bound` (for any
   limit of the finite minima).

Run `just certify-final3840` to check this certificate, or `just lean-build`
for the whole library. A fresh check takes several minutes. Cached builds reuse the checked result.
`just audit` lists the axioms of each final theorem: Lean's standard axioms plus
the native-evaluation steps. As for the 192-part bound, the general counting
and realization arguments are kernel-checked, and native compilation and
evaluation are part of the trust boundary for the arithmetic.

`just recount` runs the same counting code as a standalone program, outside the
proof, as a diagnostic. On the research machine it took about nine minutes, and its totals give
exactly the numerator above. It prints progress every 16 coarse vertices. The paper
also confirms the value with a separate character-identity computation in
Python and C++.

`Counting/SignRefinement.lean` also proves the six-edge identity for a single
balanced two-way split. The centered-block route above handles the full 20-way
refinement directly.

The embedded witness comes from SHA-256
`05302cbc635e939cc41f4ba019cdcba80199b0b83563100bac0b1a0d9fff1a29`.
`just generate-final3840` checks this hash and every block mean when regenerating
the data from `data/constructions/final3840.json.gz`. The compressed input
preserves the original JSON bytes; its provenance is recorded alongside it.
Regeneration expands roughly 163 MB of JSON and needs substantially more RAM
while validating the matrix. Normal Lean builds do not need Python, NumPy, or
the expanded JSON. `just generate-expansion` regenerates the 64-term algebraic
proof without reading any numerical report.

The result above improves the published 2022 benchmark; it makes no claim of
priority over newer announced bounds.

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

## Validated executable inputs

`lean/K4Ramsey/Counting/ValidatedTemplate.lean` provides `ValidTemplate` and
`ValidWeightedTemplate`: raw packed data accompanied by proofs that the Lean
representation and weight checks returned true. The candidate executables share
the pure parser in `lean/K4Ramsey/IO/TemplateInput.lean`, and count through these
validated inputs. The published checker uses the same named `SubgraphCounts`
record and numerator assembly, removing duplicated counting formulas.

`ValidTemplate.countSubgraphs_numerator` proves that this facade computes the
existing packed formula exactly; its axiom audit is empty. It does **not** prove
the missing general equivalence between that formula and the literal tuple sum.
Parser regression examples cover malformed matrices/weights and small exact
counts. The remaining mathematical correctness gaps described above are unchanged.

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
