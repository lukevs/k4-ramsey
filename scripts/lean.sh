#!/usr/bin/env bash
# Run Lake in the Lean package, supporting the optional local elan install.
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo_root/lean"
if [[ -x "$repo_root/.elan/bin/lake" ]]; then
  exec env ELAN_HOME="$repo_root/.elan" PATH="$repo_root/.elan/bin:$PATH" lake "$@"
fi
exec lake "$@"
