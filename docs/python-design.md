# Python design

The maintained Python code follows the data-first design recipe from
[How to Design Programs](https://htdp.org/2024-8-20/Book/part_one.html): define the
information and its representation, state each function's purpose and signature,
write examples (including boundaries), implement according to that data, then test.
Pydantic implements the data contracts; it is not a substitute for the recipe.

## Read the data definitions first

All Pydantic definitions live in `src/k4_ramsey/schemas/`:

| Module | Meaning |
|---|---|
| `certificates.py` | Symmetric binary graphs, blue diagonals, bounded integer weights; unit-weight search subset. |
| `verification.py` | Exact counts and separately scoped unit/weighted Lean recount results. |
| `experiments.py` | Run requests, subprocess outcomes, untrusted metrics, and lifecycle reports. |
| `strategies.py` | Shared script options and each maintained strategy's configuration. |
| `dashboard.py` | Read-only projections of older reports, not new verification evidence. |
| `types.py` | Shared scalar constraints, such as nonnegative counts and finite positive budgets. |
| `native.py` | Fixed-width ctypes layouts matching the C header; these are ABI structures, not Pydantic JSON models. |

Models use Pydantic's `BaseModel` and declare their own configuration. There is no
custom root model. Strict validation rejects booleans, floats, or strings in integer
fields. Unknown contract/configuration keys are errors. Strategy diagnostics are
an explicitly open JSON extension; their count claim is still strictly validated.
Historical dashboard projections deliberately ignore fields they do not consume.

JSON field names and schema versions remain unchanged. Python's `schema_version`
field has the JSON alias `schema`. Exact fractions are never replaced by floats.
JSON reading rejects duplicate keys and nonfinite values.

## Read the program from callers to helpers

`lab.py` starts with its Typer commands and the experiment orchestration, followed
by recount/promotion, snapshotting, and subprocess helpers. `verify.py` and
`weighted_verify.py` separate checker execution from parsing its exact output.
`artifacts.py` contains file/hash operations. Strategy modules start with their
entry point and search procedure, then the algorithmic helpers.

Functions are named for actions (`freeze_sources`, `hash_file`, `read_certificate`,
`calculate_delta`, `render_timeline`); data types are nouns. Purpose docstrings
describe the result or invariant, not a narration of individual statements.
Older dictionary APIs and a few historical names remain as compatibility adapters;
new runner code uses typed requests and results.

Failure, interruption, and timeout preserve an unverified report. A completed run
must have candidate recount evidence; it cannot promote a strategy's own claim.
Process cleanup, source hashes, and exact verifier agreement remain independent
of Pydantic's shape checks. These mechanisms are not a hostile-code sandbox.

## Development workflow

Use `just format`, `just python-lint`, and `just python-test`; `just check` includes
lint, the Python/native tests, Lean tests, and theorem audits. Schema examples and
counterexamples live in `tests/test_schemas.py`; CLI examples are in
`tests/test_cli.py`. Existing literal-count, timeout, tamper, and snapshot tests
remain regression checks.

The CLI migration covers the installed package, all nine maintained strategy
scripts, and the binary-certificate generator. Historical one-off research
programs and specialized fixed-witness generators have not been rewritten.

## Native boundary

`native/search.h` is the C contract: ownership, buffer sizes, cache prerequisites,
error codes, and named count/move results. `native/search.cpp` keeps graph storage
private and puts exported operations before their computational implementation.
The order limit determines scratch-buffer sizes; it is not an unrelated magic
array length. Cached flips allocate no memory. Cache creation builds a temporary
table and publishes it only after success.

Every exported operation contains C++ exceptions and reports an error through
thread-local state. Python checks that state immediately and raises `ValueError`,
`MemoryError`, or `RuntimeError`. Named ctypes structures replace positional
result buffers in the maintained Python wrapper; the old C exports remain as
compatibility adapters. Native validation checks nulls, indices, matrix symmetry,
binary values, blue diagonals, and cache state independently of Python.

As with ordinary pointer-based C APIs, callers must still supply live handles and
buffers of the documented sizes. Dangling pointers and undersized nonnull buffers
cannot be diagnosed reliably by this interface. A handle must not be mutated by
concurrent calls.

`just native-test` runs standalone C++ tests under AddressSanitizer and
UndefinedBehaviorSanitizer, including allocation-failure injection, invalid
arguments, thread-local errors, literal counts, deltas, and word boundaries.
It is included in `just test` and `just check`. Native builds enable compiler
warnings and treat them as errors.
