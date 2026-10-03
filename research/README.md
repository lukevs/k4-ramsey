# Research archive

This directory preserves the route to the constructions, including unsuccessful
experiments. Start with the [introduction](../introduction.md),
[current verification status](../docs/verification.md), or [root commands](../README.md).

- `notes/`: dated literature reviews, search logs, checkpoints, and early drafts.
  “Current state” describes the time of writing, not today's proof status.
  The [construction draft](notes/round4-P-paper-draft.md) records the derivation;
  the maintained manuscript lives in `paper/`.
- `experiments/`: specialized Python, C++, Sage, shell, and Lean investigations.
  Some algorithms have regression tests, but these are not all supported CLIs.
  They may require extra dependencies, large local reports, or a specific working
  directory. Do not run the entire archive as a batch.
- Run outputs remain in the ignored root `reports/` directory, untouched.
  Fixed inputs needed by maintained generators are separately preserved in
  `data/constructions/` with source hashes.

## Path changes

Historical command text and frozen JSON evidence retain original paths and
hashes. Source imports and repository-root paths have been updated, along with
Markdown links. Translate old commands as follows:

| Former location | Current location |
|---|---|
| `experiments/strategies/` | `src/k4_ramsey/strategies/` |
| `experiments/configs/` | `data/search-configs/` |
| Other `experiments/` paths | `research/experiments/` |
| Notes directly under `research/` | `research/notes/` |
| `research/clebsch-explorer*` | `explainer/clebsch-explorer*` |
| `scripts/generate_*.py` | `src/k4_ramsey/generators/` (use `just generate-*`) |
| `scripts/probe_final_lean_structure.py` | `research/experiments/final_lean/probe_structure.py` |

The root justfile is the single public command surface. Algorithms stay in source
files, not shell recipes. Use `just experiment` for the supported runner and
`just runner-help run` for its options.
