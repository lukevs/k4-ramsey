set shell := ["bash", "-eu", "-o", "pipefail", "-c"]
set positional-arguments

# Show the available project commands.
default:
    @just --list

# Download cached mathlib dependencies and build the proofs and runner.
setup:
    uv sync --locked
    bash scripts/lean.sh exe cache get
    just build

# Build the proof library and C++/Lean experiment runner.
build: lean-build runner-build

# Check the proof library (without importing test modules).
lean-build:
    bash scripts/lean.sh build K4Ramsey

# Build the C++ shared library and the Lean candidate checker.
runner-build: native-build checker-build
    uv run --locked k4-lab record-build

# Compile the C++ search engine as a shared library.
native-build:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p build
    suffix=so
    if [[ "$(uname -s)" == Darwin ]]; then suffix=dylib; fi
    c++ -std=c++17 -O3 -fPIC -shared native/search.cpp -o "build/libk4.$suffix"

# Build the independent Lean candidate checkers.
checker-build:
    bash scripts/lean.sh build check_candidate check_weighted_candidate

# Run both Lean and Python regression tests.
test: lean-test python-test

# Check the separate Lean regression-test library.
lean-test:
    bash scripts/lean.sh build Tests

# Build candidate checkers and run Python/native regression tests.
python-test: runner-build
    uv run --locked python -m unittest discover -s tests -v

# Build, test, and inspect theorem axioms.
check: lean-build test audit

# Print the published graph's exact count.
published:
    bash scripts/lean.sh exe check_published

# Print theorem axioms and native-evaluation dependencies.
audit: lean-build
    bash scripts/lean.sh env lean Audits/Published.lean
    bash scripts/lean.sh env lean Audits/Graphon.lean

# Run the long 3,840-part diagnostic recount (not its final certificate).
recount:
    bash scripts/lean.sh exe check_final3840

# Run a short C++-backed search; OUT must be a new directory.
search out seed="0" seconds="10" timeout="40":
    uv run --locked k4-lab run --out {{ quote(out) }} --seed {{ quote(seed) }} --seconds {{ quote(seconds) }} --timeout {{ quote(timeout) }} --hypothesis 'Sampled single-edge descent improves the published seed' --prediction 'Independent Lean recount confirms a smaller numerator'

# Run an experiment with custom runner flags; see just runner-help run.
experiment *args:
    uv run --locked k4-lab run "$@"

# Refresh the local journal.html snapshot (no background server).
dashboard:
    uv run --locked k4-lab dashboard

# Show the experiment runner's full CLI options.
runner-help *args:
    uv run --locked k4-lab "$@" --help
