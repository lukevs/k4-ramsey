# Experiment runner and dashboard

From the repository root, use `just runner-build`, `just search OUT`, and
`just dashboard`. The Lean
package and compiled checkers live under `lean/`; Python tests stay in `tests/`.

The coordinating session dispatches individual experiments; there is no queue
service. Build once before dispatch, and do not rebuild during active runs:

```sh
just runner-build
just python-test
just experiment \
  --out reports/descent-001 --seconds 10 --timeout 40 --seed 0 \
  --hypothesis 'Sampled single-edge descent improves the published seed' \
  --prediction 'Independent Lean recount confirms a smaller numerator'
just dashboard
```

Open [the HTML experiment dashboard](../journal.html) for statuses, exact checked
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

## Division of responsibilities

The justfile owns compiler invocations: `native-build` compiles the C++ shared
library, and `checker-build` builds the Lean checkers. `runner-build` runs both,
then calls Python's `record-build` command to hash the resulting artifacts and
build configuration. Python does not compile missing binaries implicitly.

During an experiment, Python still supervises the strategy subprocess, applies
deadlines, captures logs, invokes the frozen Lean checker, validates its counts,
and writes JSON reports. The search accesses the C++ library through `ctypes`.
These runtime subprocesses are separate from build orchestration.

The justfile invokes Python commands through `uv run --locked`. A strategy uses
that same interpreter, but runs from `snapshot/src/strategy.py`, alongside its
frozen `k4_ramsey` package. This preserves source isolation without `PYTHONPATH`
overrides or creating an additional environment for every run.
