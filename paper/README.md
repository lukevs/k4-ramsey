# Paper

`main.tex` is the manuscript source. `main.pdf` is the compiled version.
`references.bib` contains the bibliography.

Authors: Luke Van Seters and Madhan Jothimani.

The paper states the exact 3840-class construction bound and the 192-class
bound. Both have numerical Lean proofs; the 3840-class value is also confirmed
by an independent exact computation.

## Build

From the repository root, use the existing UV environment and `just`:

```sh
uv sync --locked
just paper
```

This uses `latexmk`, pdfLaTeX, and BibTeX. Tectonic is an alternative:

```sh
just paper-tectonic
```

Both commands produce `main.pdf` here. The PDF remains part of the paper
directory. Intermediate LaTeX files are ignored by Git. There is no separate
Python project or environment under `paper/`.

The Typer entry point is `uv run --locked k4-paper --help`. Its maintained code
lives in `src/k4_ramsey/paper/`, with strict Pydantic definitions in
`src/k4_ramsey/schemas/paper.py`. The project lockfile includes Matplotlib in
the development dependencies. `just` owns the LaTeX compiler step.

## Figures

`just paper-figures` regenerates six figures under `figures/`, as PDF for the
manuscript and PNG for the Markdown documents:

| File | Content |
|---|---|
| `bounds` | History of upper bounds on c₄, and a zoom on recent constructions |
| `clebsch-graph` | The Clebsch graph, drawn and as a 16 × 16 coloring |
| `ppss-reordered` | The PPSS graph in published order, in Clebsch order, and one family |
| `family-rule` | The twelve-family type rule, the family graph, and the four patterns |
| `refinements` | The pentagon refinement and the balanced sign split |
| `hero` | README banner: the PPSS graph as published, relabeled, and the Clebsch graph |

The generator reads the published PPSS matrix and the explainer's vertex order.
It checks that they agree, that every family is a fourfold Clebsch blow-up, and
that the fiber red counts follow the type rule (Proposition 3.1 of the paper).
`figures/manifest.json` records source and output hashes.

## Research-method provenance

Section 9 describes the hypothesis-driven workflow and the primary configuration:
OpenAI's Codex harness, with a GPT-6 Astra parent agent directing eight GPT-6
Astra subagents through Codex's native subagents, all following the research skill in
`data/research-workflow.md`. The configuration is supplied by the authors. Historical records use multiple coordinator labels and later
rounds changed the active lanes; the manuscript does not claim a complete model
audit of all historical runs.

The methods section and bibliography explicitly cite both instruction sources:

- [Jacobian Conjecture Prompt, hosted by Aaron Lou](https://aaronlou.com/jacobian_counterexample_prompt.pdf).
- [OpenAI Cycle Double Cover prompt](https://cdn.openai.com/pdf/04d1d1e4-bc75-476a-97cf-49055cd98d31/cdc_prompt.pdf).

The supplement retains the local research skill and its source-principles note.
These explain how the workflow adapted the source prompts. Mathematical prior
work appears separately in the introduction and bibliography.

The bibliography cites external research and the two source prompts, not this
repository or its local instruction files. The repository link belongs in the
data-availability section. Prior-work coverage includes the original Ramsey
multiplicity problem, Cayley and product constructions, Fourier counts,
flag-algebra lower bounds, signed graphons and local commonness, related
Clebsch/pentagon extremal results, and recent formal-verification work.

## Supplement checks

The supplement includes the explicit final witness, a simpler pentagon witness,
the base polynomial, optimization certificates, class maps, and count records.
The construction file contains no score. `data/manifest.json` gives file hashes.

```sh
just paper-check
```

This checks supplement hashes, exact block means, probability bounds, sign
symmetry, and arithmetic in the recorded character-count receipt. It is not a
new density recount. The export additionally checks all 14745600 original
matrix entries under the recorded class permutation.

To create a full candidate file for a new independent count:

```sh
just paper-check --matrix /tmp/k4-paper-final3840.json --original-order
```

The output file must not exist. Its byte hash differs from the original audit
input because the JSON format differs. Its ordered integer matrix is the same.
The output is large; the compact supplement is sufficient to define the witness.

The independent counter needs NumPy, a C++17 compiler, and Apple Accelerate.
From the repository root, compile the contraction engine:

```sh
c++ -O3 -std=c++17 research/experiments/round5_F5/k4mix.cpp \
  -framework Accelerate -o research/experiments/round5_F5/k4mix
```

Then run the checker on the reconstructed candidate with a fresh output directory:

```sh
VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
  uv run --locked python research/experiments/round5_F5/zk_checker.py \
  --candidate /tmp/k4-paper-final3840.json --out /tmp/k4-paper-recount
```

The checker performs its small-instance oracle before the full count. The
recount takes several minutes on the research machine. This native route is
specific to macOS; the mathematical identity is platform-independent.

For the formal proofs, use `just lean-build` and `just audit` from the repository
root. `just certify-final3840` checks the numerical 3840-class certificate (about
12 minutes when not cached). See [verification details](../docs/verification.md)
for the trust boundary.

`just paper-export` regenerates the frozen data from the repository's Lean
tables and local reports. A normal paper build does not need those reports.
The optional `--workflow` argument includes a supplied research skill snapshot.

## Before submission

The authors must review the mathematics, affiliations, and AI-use statement.
The data and paper need a fixed repository release or archival deposit.
The Feinstein comparison needs an exact value or construction before any
priority claim.
