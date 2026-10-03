# Twelve Clebsch graphs and the Ramsey multiplicity of K₄

How few monochromatic K₄s can a red/blue coloring of a large complete graph
have? The limiting fraction, c₄, is unknown. This repository contains a new
explicit upper bound,

```text
c₄ ≤ 8450462766487926638466333426306607129 / 280384030360880691940646801777885184000
   = 0.030138887566497220…
```

together with the code, data, and Lean proofs behind it.

![Upper bounds on c₄](paper/figures/bounds.png)

**Background.** The best construction with public data is the 768-vertex graph
of Parczyk, Pokutta, Spiegel and Szabó (2022), at 0.0301449. Their paper
reports an improvement by McKay to 0.0301423 whose graph has not been released.
A January 2026 seminar by Feinstein announced c₄ < 0.030139, without a value or
construction. Our bound is below that threshold. We can't compare the two
exactly, so we don't claim to beat it.

**What we found.**

1. **Structure.** The PPSS graph is twelve linked copies of the Clebsch graph.
   Its vertices split into 12 families × 16 Clebsch positions × 4. The colors
   between families follow one of four patterns, chosen by a rule on
   ℤ₃ × ℤ₂ × ℤ₂.
2. **Two parameters.** Making the two fractional patterns adjustable gives a
   192-class table with density given by an explicit polynomial in p and h. Its
   minimum, 0.0301389773, already beats McKay's value. A rational point,
   0.0301389941, is proved in Lean.
3. **Refinement.** Splitting each class with a pentagon pattern and then two
   balanced sign splits gives the 3840-class bound above. Its value comes from
   an independent exact computation.

![The PPSS graph before and after relabeling](paper/figures/ppss-reordered.png)

The results were found autonomously by an AI research system running in the
[Codex](https://github.com/openai/codex), OpenAI's agent harness: a GPT-6 Astra
parent agent directing eight GPT-6 Astra subagents through Codex's native
subagents. All agents
followed a research skill derived from OpenAI's
[Cycle Double Cover prompt](https://cdn.openai.com/pdf/04d1d1e4-bc75-476a-97cf-49055cd98d31/cdc_prompt.pdf)
and the [Jacobian Conjecture prompt](https://aaronlou.com/jacobian_counterexample_prompt.pdf)
([skill](paper/data/research-workflow.md), [adaptation notes](paper/data/workflow-source-principles.md)).
No candidate was accepted until a separate program had recounted it exactly.

**Where to read more.**

- [Introduction](introduction.md): the problem and the construction, with no
  graph theory assumed.
- [Paper](paper/main.pdf) ([source](paper/main.tex), [build notes](paper/README.md)):
  full statements, proofs, and the verification boundary.
- [Interactive explainer](explainer/clebsch-explorer.html): open it in a browser
  to explore the twelve families.

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
  strategies/            Maintained search implementations
  generators/            Reproducible Lean source generators
native/                   C++17 search primitives
tests/                    Python/native regression tests
data/                     Published seed, fixed construction inputs, provenance
  search-configs/         Example configurations for maintained strategies
explainer/                HTML template, builder, and standalone explainer
scripts/                  Lean environment wrapper only
docs/                     Verification and runner documentation
research/
  notes/                  Historical research notes and early paper drafts
  experiments/            Specialized research programs and configurations
paper/                    LaTeX manuscript, PDF, and checked construction data
justfile                  Common project commands
```

Generated `reports/`, `build/`, `lean/.lake/`, and `journal.html` stay out of Git.
Historical research logs retain their original command text; see the
[research index](research/README.md) for the old-to-new path mapping.
Fixed regeneration inputs are checked in under `data/constructions/`, not read
from local reports. No local reports are needed for Lean builds, Lean source
regeneration, or rebuilding the explainer. Historical evidence export for the
paper still uses archived reports.

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
| `just native-test` | Run standalone C++ boundary tests with address/undefined-behavior sanitizers. |
| `just audit` | List theorem axioms and native-evaluation dependencies. |
| `just check` | Build, test, and audit. |
| `just published` | Print the published 768-vertex graph's exact count. |
| `just recount` | Run the long 3,840-part diagnostic count. |
| `just search reports/descent-001` | Run a short search from the bundled seed. |
| `just dashboard` | Refresh the local `journal.html` snapshot. |
| `just runner-help run` | Show advanced experiment options. |
| `just format` | Format the maintained Python code. |
| `just python-lint` | Check Python formatting and basic correctness. |
| `just explainer` | Rebuild the standalone HTML explainer (requires Node.js). |
| `just generate-certificate --help` | Show binary-certificate embedding options. |
| `just generate-expansion` | Regenerate the six-edge Lean expansion proofs. |
| `just generate-final3840` | Regenerate the embedded Lean witness from bundled inputs. |
| `just paper-check` | Validate the paper's supplement data, without a new clique recount. |
| `just paper-figures` | Regenerate checked scientific figures. |
| `just paper` | Check, draw figures, and compile the paper with latexmk. |

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
