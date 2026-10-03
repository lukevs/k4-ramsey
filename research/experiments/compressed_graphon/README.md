# Compressed typed-graphon workflow

This directory supplies exact polynomial evaluation and feasibility utilities.
The candidate-bound compressed recount lives in
`research/experiments/verification_precision/`.  Together they support this workflow:

1. derive or interpolate an exact degree-at-most-six raw-numerator polynomial;
2. minimize it once on its proven feasible integer interval;
3. materialize the selected typed graphon with the producer that defined the
   family;
4. bind the explicit candidate to a compressed block histogram and recount it
   with the independent Lean `Nat` evaluator.

The utilities do **not** infer coefficients from a graphon family and do not
turn a numerical score into construction evidence.  Coefficient provenance,
feasibility, materialization, and candidate binding remain explicit steps.

## Exact convention and normalization

`ExactPolynomial` uses the canonical record schema
`compressed-graphon-polynomial-v1`:

```text
N(q) = base_numerator + sum_k c[k] q^k, with c[0] = 0.
density(q) = N(q) / normalization_denominator.
```

The fields are:

- `base_numerator`;
- `numerator_coefficients_low_to_high`;
- `normalization_denominator`;
- `amplitude_parameter` (normally `q`);
- `feasible_integer_interval`;
- optional `base_order`, `latent_order`, and `probability_denominator`;
- the exact `coefficient_convention` string above.

For a base order `B`, latent order `T`, refined order `N=B*T`, and probability
denominator `Q`, the normalization is

```text
N^4 * Q^6.
```

Thus a base graphon numerator must be rescaled by `T^4` before it is used as
the constant term of a refined polynomial.  The association-phase fixture, for
example, uses `B=192`, `T=5`, `N=960`, and
`normalization_denominator = 960^4 * 65536^6`.

Extra JSON fields are permitted and should retain provenance: parent and phase
assignment hashes, producer/checker hashes, the exact recount coordinates used
for interpolation, and the derivation report.  The evaluator ignores those
extra fields but the research record should not omit them.

## Why seven exact points are enough—and when they are not

If every perturbed fine-block numerator is affine in the single amplitude
`q`, each red or blue `K4` term is a product of six affine factors.  Its raw
ordered count is therefore a polynomial of degree at most six.  Seven distinct
integer coordinates determine it exactly.  This is the required degree proof
for using `interpolate_integer_polynomial(..., degree_bound_proven=True)`;
merely observing a good fit at seven points is not sufficient.  The explicit
flag guards against treating interpolation agreement as the proof.

Each interpolation ordinate must be an exact raw numerator with the same
candidate family, support semantics, ordering, and normalization.  The helper
rejects duplicate coordinates, nonintegral power-basis coefficients, or more
than seven points.  After interpolation, check additional coordinates not used
in the fit whenever they already exist.  If support, phases, block masses, or
another parameter changes with `q`, the affine-family proof must be redone.

There is currently no generic coefficient builder.  Existing producer adapters
are:

- `research/experiments/association_scheme/coefficient_falsifier.py` and
  `phase_optimize.py`, which derive exact triangle, `C4`, diamond, and `K4`
  intersection factors;
- the exact ordinate rows in the Potts reports, adapted with
  `interpolate_integer_polynomial`;
- producer-specific binary latent expansion coefficients in their reports.

This is an intentional limitation: a canonical polynomial certifies exact
evaluation of supplied coefficients, not their derivation.

## Kernel and support representations

`CenteredKernel` is a symmetric integer `T x T` matrix with zero uniform row
sums.  `KernelLevel(kernel, q)` and `probability_ranges` compute exact extrema
for additive latent levels.  The feasibility caller must pass **exactly** the
base probability entries being perturbed.  Include diagonal entries if and
only if diagonal blocks are in the support.

`ExactPolynomial.additive_raw` and `additive_density` require
`mixed_terms_absent=True`.  Centering alone does not eliminate mixed motif
terms between latent levels; callers must establish their absence separately.

The phase fixture is more general than one shared `CenteredKernel`.  For each
fractional coarse edge `e={i,j}`, it stores `inactive` or `x_e in Z/5Z` in
`reports/association-scheme-phase-001/phase-assignment.json`, and uses

```text
kappa(d) = 3 for d=+1,-1 mod 5, and -2 otherwise,
P[(i,a),(j,b)] = P[i,j] + q*kappa(a-b-g_ij),
g_ij = x_e for i<j and -x_e for i>j.
```

Its exact factor objective is documented in
`research/experiments/association_scheme/phase_model.md`.  The phase search polynomial
uses coefficients `C_3,...,C_6` such that
`Delta(q)=sum_d C_d q^d` under the refined normalization above.

## Candidate-bound compressed recount

The recount accepts `rational-step-graphon-v1` candidates with unit masses,
symmetric integer probabilities in `[0,Q]`, order `N` divisible by `T`, and
**base-major, type-minor** indexing `index = base*T + type`.

The native generator
`research/experiments/verification_precision/typed_kernel_histogram.cpp` reads every
candidate entry and deduplicates the full oriented `T x T` red-probability
blocks.  These certificate kernels contain absolute numerators in `[0,Q]`, not
centered perturbations and not hidden base/`q` metadata.  It then compresses
ordered coarse quadruples by their six kernel IDs in edge order
`01,02,03,12,13,23`.

Certificate V1 has header `N Q B T K H`, followed by `K` flattened absolute
kernel matrices and `H` records of six kernel IDs plus their ordered coarse
multiplicity.  Histogram mass must equal `B^4`.  The standalone Lean evaluator
checks structure, bounds, IDs, mass, and exact red/blue arithmetic by summing
all `T^4` latent assignments.  Its denominator is `N^4*Q^6` and it uses `Nat`,
so there is no machine-integer overflow boundary.

The current native signature encoding requires `K^6` to fit `UInt64` and
rejects candidates that exceed this bound.  This is an implementation limit on
the number of distinct oriented fine-block kernels, not a mathematical limit
of the histogram representation.

Evidence label: **Level A**, native candidate-to-histogram binding plus Lean
exact arithmetic.  The native generator binds the histogram to the explicit full
candidate.  Lean independently verifies the certificate arithmetic but does
not reconstruct that binding.  This is stronger and much cheaper than trusting
only a search polynomial, but it is not a kernel-only proof that the histogram
came from the candidate.

Production commands for the two current precision fixtures are:

```sh
python3 -m experiments.verification_precision.run_typed_kernel_audit \
  --candidate reports/correlated-graphon-potts-precision-003/graphon-candidate.json \
  --types 3 \
  --expected-sha256 bc6ff4995ea00723ec6df51d056362ddcab47c041635e612a8cf4b21fd6e8d05 \
  --out reports/graphon-potts-precision-compressed-001

python3 -m experiments.verification_precision.run_typed_kernel_audit \
  --candidate reports/association-scheme-phase-001/graphon-candidate.json \
  --types 5 \
  --expected-sha256 31b6d0941b4d36e6e8ce61689321df1d1f914223ab21d261a60c1809c963d9b0 \
  --out reports/graphon-association-phase-compressed-001
```

Use a fresh report directory for every run.  The driver runs literal tiny
oracles for `B=1..4`, `T=2,3`, covering coarse equality partitions
`4,31,22,211,1111`, before it processes the supplied candidate.

## Runnable phase-fixture pipeline

The report adapter converts the existing exact phase-factor report into the
canonical polynomial record while retaining source paths, hashes, coefficient
convention, normalization, and adapter timing:

```sh
PYTHONPATH=. python3 -m experiments.compressed_graphon.adapt \
  --kind degree-map \
  --report reports/association-scheme-phase-001/report.json \
  --parent-report reports/literature-two-parameter-001/report.json \
  --base-order 192 --latent-order 5 --probability-denominator 65536 \
  > /tmp/association-phase-polynomial.json

PYTHONPATH=. python3 -m experiments.compressed_graphon.evaluate \
  /tmp/association-phase-polynomial.json --q -5496 --minimize
```

For reports that already contain the complete low-to-high polynomial, such as
the precision Potts report, use `--kind total-coefficients` and omit
`--parent-report`:

```sh
PYTHONPATH=. python3 -m experiments.compressed_graphon.adapt \
  --kind total-coefficients \
  --report reports/correlated-graphon-potts-precision-003/report.json \
  --base-order 192 --latent-order 3 --probability-denominator 65536 \
  > /tmp/potts-precision-polynomial.json
```

The minimum must select `q=-5496`, and its raw numerator must equal the explicit
candidate report.  The producer-specific materialization has already written
`reports/association-scheme-phase-001/graphon-candidate.json`; the second audit
command in the preceding section then closes the selected-candidate recount.

For a new family, add a provenance-preserving report adapter and use its
originating materializer; do not replace the exact polynomial or histogram
evaluators.  Feed the selected `q` back to that producer/verifier.  No generic
materializer currently exists: the canonical polynomial alone does not encode
support, phases, or fine-block matrices and therefore cannot bind a graphon
candidate safely.

## Tiny validation and benchmark recipe

Run the reusable exact unit tests:

```sh
PYTHONPATH=. python3 -m unittest discover \
  -s research/experiments/compressed_graphon -p 'test_*.py'
```

Check the recount CLI without launching a candidate audit:

```sh
python3 -m experiments.verification_precision.run_typed_kernel_audit --help
```

For a small end-to-end timing, create the phase record with the adapter above
and time exact evaluation/minimization:

```sh
/usr/bin/time -p env PYTHONPATH=. python3 -m experiments.compressed_graphon.evaluate \
  /tmp/association-phase-polynomial.json --q -5496 --minimize
```

For candidate-scale benchmarking, use a fresh output directory and the audit
driver.  Record its separate setup, compile, native histogram-generation, and
Lean-evaluation times; do not compare only wall time or overwrite prior reports.

Historical measured costs on this machine provide the baseline:

- initial `r=5` motif generation, tiny checks, and scalar minimization:
  `4.668 s` (`association-scheme-coefficients-001`);
- phase Max-CSP coordinate search: `13.168 s` over 160,320 aggregated factors;
- generic direct ordered recount of the selected 960-step phase candidate:
  `111.658 s`;
- total phase run including setup and serialization: `126.300 s`.
- compressed Potts precision recount (`K=4`, `H=1002`): native certificate
  generation `0.238 s`, Lean exact-`Nat` evaluation `0.024 s`, and complete
  driver wall time `3.347 s` including compilation and eight tiny fixtures.
- compressed association-phase recount (`K=10`, `H=22257`): native certificate
  generation `0.493 s`, Lean exact-`Nat` evaluation `2.609 s`, and complete
  driver wall time `5.248 s`, versus `111.658 s` for the generic direct recount.

These measurements describe different scopes.  In particular, the first time
is not a standalone benchmark of the later phase-factor generator.  A useful
compressed pipeline benchmark reports coefficient production, minimization,
materialization, native certificate generation, and Lean evaluation separately.
