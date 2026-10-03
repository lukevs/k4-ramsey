# K4 Ramsey multiplicity in Lean

The Lean project checks the published 768-vertex Cayley template from Parczyk,
Pokutta, Spiegel, and Szabó. It computes the exact balanced-blow-up numerator
`10487165184`, with denominator `768^4`, equivalent to
`4551721 / 150994944 ≈ 0.0301448570` (about 3.0145%).

McKay's later reference numerator is `10486266368`. Its adjacency matrix is
not included here, so **this project does not reproduce that improved bound**.

## Run

With Lean installed through elan, run `lake build`. In this workspace, the
local installation can be selected with:

```sh
env ELAN_HOME="$PWD/.elan" PATH="$PWD/.elan/bin:$PATH" lake build
env ELAN_HOME="$PWD/.elan" PATH="$PWD/.elan/bin:$PATH" lake exe check_published
env ELAN_HOME="$PWD/.elan" PATH="$PWD/.elan/bin:$PATH" lake env lean Audit.lean
```

The first command verifies the certificate and regression tests. The second
reports individual counts and computation time. The third prints the theorem
axioms. The bundled data makes all three independent of AutoLab and Python.
Use the executable target for timing; bare `lean --run` does not load Lake's
precompiled imports automatically and can fall back to slow interpretation.

## Performance and verification scope

`precompileModules = true` is essential: Lean loads compiled machine code for
the imported counter. The data uses twelve `UInt64` words per adjacency row;
all accumulated counts use arbitrary-precision `Nat`. The comparison theorem
rewrites with `exact_numerator`, reusing its result instead of counting again.
The 64-bit shift boundary is handled explicitly because UInt64 shifts wrap
their shift count modulo 64.

Measured on this workspace: a clean build of the library, tests, and executable
took 9.15 seconds; the certificate proof module took 1.1 seconds, and the
standalone executable took about 0.7 seconds wall time. These are observed
timings, not a guarantee of optimality or identical speed on other machines.

Lean verifies the matrix shape, symmetry, clear diagonal, padding bits, edge
count, and the computed numerator. Tests exhaust all 1,024 simple graphs on
five vertices against an independent ordered-quadruple oracle. Complete and
empty graphs exercise word boundaries at 63/64/65 and 127/128/129 vertices.

This is a verified execution of a counting program via `native_decide`.
Lean 4.34.1 records native-evaluation axioms, visible in `Audit.lean`; compilation
and runtime are part of the trust boundary. The general theorem connecting the
optimized program to the literal tuple sum, and the asymptotic blow-up theorem
proving a bound on `c₄`, have **not** been formalized. Regression tests do not
replace those proofs.

## Data provenance

Source: [New Ramsey Multiplicity Bounds and Search Heuristics,
Theorem 1.1](https://arxiv.org/html/2206.04036v3), and the authors'
[Zenodo archive](https://zenodo.org/records/6602512) (CC BY 4.0),
`graphs.zip`, member `graphs/c4.graph6.txt`.
Archive SHA256: `6ff8a2496c545e86def3a12bd69ef557c50a890c732a8506d30b1bbe8467ec89`.

`K4Ramsey/Published768Data.lean` embeds the graph supplied by the local hill's
published example. To regenerate this representation:

```sh
python3 scripts/generate_lean_certificate.py \
  .autolab/hills/clique-cluster-ramsey-multiplicity/examples/published_cayley_768/solution.json \
  K4Ramsey/Published768Data.lean --namespace Published768
```

The checker currently supports unit weights and blue diagonals, precisely the
published scenario. The generator rejects inputs outside that scope.

## Experiment runner and dashboard

The coordinating session dispatches individual experiments; there is no queue
service. Build once before dispatch, and do not rebuild during active runs:

```sh
PYTHONPATH=src python3 -m k4_ramsey.lab build
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m k4_ramsey.lab run \
  --out reports/descent-001 --seconds 10 --timeout 40 --seed 0 \
  --hypothesis 'Sampled single-edge descent improves the published seed' \
  --prediction 'Independent Lean recount confirms a smaller numerator'
PYTHONPATH=src python3 -m k4_ramsey.lab dashboard
```

Open [the HTML experiment dashboard](journal.html) for statuses, exact checked
values, reference gaps, and artifact links. It is a self-contained snapshot;
rerun the dashboard command after dispatch/completion to refresh it. It does
not start a server or supervise experiments after the session ends.

Each new output directory contains input/config, a private source and binary
snapshot, logs, mutable `status.json`, candidate/checkpoint, and final
`report.json`. Existing run directories are never reused. Completed candidates
are independently recounted by the compiled Lean executable; a failed/timed-out
search's checkpoint is not promoted. These checks certify the artifact count,
not the truth of its research hypothesis or a global optimum.

For a no-search reproducibility test, supply `--input PATH` and
`--config experiments/configs/replay.json`. For a new method, pass a standalone
Python script with `--strategy PATH`. It receives `--input`, `--output`,
`--seed`, `--seconds`, and `--config`; it must save a certificate at `--output`
and may write `search.json` alongside it. A reported `numerator` must match
Lean. The snapshot exposes the `k4_ramsey` package, but does not automatically
package arbitrary sibling files or third-party dependencies.

`--seconds` is the cooperative strategy duration; `--timeout` is the larger
total run budget including setup and verification. The parent bounds and reaps
the strategy process group, with a small startup/serialization grace period.
The implementation targets POSIX (including macOS). Source hashes detect
accidental mutation; this is not a security sandbox for hostile scripts.
The coordinator caps concurrent CPU jobs, including verification, at four.
Use fresh output paths and frozen builds for parallel experiments.
