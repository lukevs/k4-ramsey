# K4 Ramsey multiplicity

Construct, explore, and verify red/blue graph colorings with few monochromatic
copies of K₄. The project combines Clebsch-based constructions, a C++ search
engine, Python experiments, and Lean proofs.

Start with [the introduction](introduction.md) for the problem and results.
Open the [interactive explainer](research/clebsch-explorer.html) in a browser
to explore the graph visually.
The [paper directory](paper/README.md) contains the LaTeX manuscript, compiled
PDF, bibliography, and construction supplement.

## Layout

```text
lean/                     Self-contained Lean package
  K4Ramsey.lean           Public library entry point
  K4Ramsey/
    Core/                 Objective, probability, realization, and limits
    Counting/             Counters and general correctness proofs
    Constructions/        Published768, Clebsch192, and Final3840
  Executables/            Command-line counters
  Audits/                 Theorem-axiom inspection
  Tests/                  Lean regression tests
  lakefile.toml           Lean build targets and dependencies
src/k4_ramsey/            Python engine interface and experiment runner
  schemas/               Pydantic data definitions and validation contracts
native/                   C++17 search primitives
tests/                    Python/native regression tests
experiments/              Strategies, configurations, and specialized tools
data/                     Published seed and source attribution
scripts/                  Generators and the Lean command wrapper
docs/                     Verification and runner documentation
research/                 Research notes, paper draft, and visual explainer
paper/                    LaTeX manuscript, PDF, and checked construction data
justfile                  Common project commands
```

Generated `reports/`, `build/`, `lean/.lake/`, and `journal.html` stay out of Git.
Historical research logs retain their original paths; use the layout above for
current source locations.

## Setup

Use macOS or Linux with **Git**, **just**, **uv**, Lean's **elan** toolchain
manager, and a **C++17 compiler** available as `c++`. Python 3.12+ is required;
uv manages the project environment.

```sh
git clone https://github.com/lukevs/k4-ramsey.git
cd k4-ramsey
just setup
```

This syncs the locked Python environment, downloads cached mathlib dependencies,
checks the proof library, and builds
the C++ shared library and Lean candidate checker. Lean and mathlib are pinned
to `v4.34.1`; allow several GB for dependencies and build products.

The Python recipes use `uv run --locked` with the installed project package;
no `PYTHONPATH` setup is needed. Pydantic validates data contracts and Typer handles
the Python CLIs. Specialized research experiments may need additional dependencies.
The Lean proofs use embedded data, not the large local experiment artifacts.

## Common commands

Run `just` to list the available commands.

| Command | Action |
|---|---|
| `just build` | Build the proofs and C++/Lean experiment runner. |
| `just test` | Run Lean and Python/native regression tests. |
| `just audit` | List theorem axioms and native-evaluation dependencies. |
| `just check` | Build, test, and audit. |
| `just published` | Print the published 768-vertex graph's exact count. |
| `just recount` | Run the long 3,840-part diagnostic count. |
| `just search reports/descent-001` | Run a short search from the bundled seed. |
| `just dashboard` | Refresh the local `journal.html` snapshot. |
| `just runner-help run` | Show advanced experiment options. |
| `just format` | Format the maintained Python code. |
| `just python-lint` | Check Python formatting and basic correctness. |

Build before running searches, use a new output directory each time, and do not
rebuild during an active experiment. Search parameters are positional:
`just search OUT SEED SECONDS TIMEOUT`. The defaults are `0 10 40`; timeout
includes setup and verification. The dashboard is a snapshot, not a server.

Build commands live in the justfile. Python handles experiment supervision,
checker-output validation, and artifact formatting—not compiler invocations.
The C++ engine is loaded through `ctypes`.

The full recount is a multi-minute task, not part of `just check`. An observed
run used roughly 700 MB. Its printed totals do not replace the final numerical
Lean certificate.

## Further details

All normal workflows run through `just` from the repository root. The recipes
manage Python's uv environment, the Lean working directory, compiled counters,
and the optional repository-local `.elan/` installation. There is no need to set
`PYTHONPATH`, activate an environment, or invoke Python or Lake directly.

For custom strategies or replay, use `just experiment` with the options listed
by `just runner-help run`.

**Verification status:** the 192-part construction has an end-to-end numerical
upper-bound proof. The 3,840-part optimized counter is proved equal to the
literal density, but its final numerical certificate remains unfinished.
The published bitset checker also has a separate correctness gap.

See [verification details](docs/verification.md), [runner details](docs/experiments.md),
[Python design](docs/python-design.md), and [seed attribution](data/SOURCE.md).
