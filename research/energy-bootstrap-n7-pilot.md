# Seven-vertex independence-branch pilot

Active main-thread pilot, 2026-09-30. Follow-up authorized after the exact N6
result. Local work only, no subagents, installs, remote work or commits.
Initial 15-minute ceiling; single-thread numerical jobs <=175 seconds each.

Hypothesis: disjoint-triple factorization strengthens a genuinely larger
seven-vertex moment relaxation. Compare the same N7 blocks with and without
six exhaustive interval secants. Target all ordinary N7 rooted-square blocks,
retaining existing N6 constraints where tractable. There are 1044 unlabelled
seven-vertex graphs. The earlier selective C5-root N7 test did not strengthen
N6; merely re-running that is not a higher-baseline result.

Re-use the elementary proof and six intervals from energy-bootstrap-pilot.md.
First establish the larger baseline; then run branch solves and independently
check any rational dual. If resource limits prevent full N7, label any reduced
block-family experiment explicitly. No finite-step/Clebsch/regularity restriction.
Published frontier remains stronger than the earlier N6 certificate.

## Completed: gain survives full N7

The independently checked global bound from this pilot is

    c4 >= 22430720843 / 768000000000
       = 0.029206667764322916...

The matched full N7 control has the exact certificate

    c4 >= 1225755149 / 42000000000
       = 0.029184646404761906...

Thus the new checked certificate raises our N7 reference by approximately
0.00002202136. This is below the published frontier near 0.0296, and is not
an assertion of a new record, a new method, or novelty. The upper incumbent
is unchanged. All jobs finished; no subagents were launched.

## Comparison and interpretation

The new program uses all 39 ordinary seven-vertex blocks (one 1-root block,
four 3-root blocks, 34 5-root blocks), plus the 19 previously audited N5/N6
blocks lifted through vertex deletion. It has 1044 induced graph probabilities.
The numerical control objective was 0.029184709736 (solver status optimal).
For the one-red-edge triple event it had x=0.374705217 and z-x^2=0.001157712.
This is smaller than the N6 discrepancy, but still positive.

| Case | Numerical value | Independently checked value |
|---|---:|---:|
| Full N7 control | 0.029184709736 | 0.029184646405 |
| x in [5/16,3/8] | 0.029207246673 | 0.029206667764 |
| x in [3/8,7/16] | 0.029207733502 | 0.029207135027 |

Both branch solvers reported optimal_inaccurate; the exact result uses rounded
rational matrices and checked coefficient inequalities, not their numerical
optimality claims. The two expensive branches took about 48 and 47 seconds,
and the control took 45 seconds, with single-thread settings.

The four outer intervals retain their already checked N6 bounds: 0.0307456909,
0.029392499190625, 0.02942066108125 and 0.0310201623. Each exceeds both new
central bounds. Reusing these saves four larger solves without weakening the
combined minimum. The combination checker verifies exact coverage of [0,1]
and binds every reused or new certificate by SHA256.

The elementary proof remains: for a fixed graphon, independently sampled
triples give z=x^2. Within [a,b], (a+b)x-z-ab>=0. Add a nonnegative multiple
of that constraint to the ordinary flag-square certificate and take the
minimum over an exhaustive partition. No upper-bound condition, estimated
observable endpoint, Clebsch assumption, regularity restriction, or fixed
vertex count of the underlying graphon is used.

The result supports the transfer: explicit disjoint-motif factorization remains
useful even after strengthening the ordinary moment relaxation. It does not
show that the gain will persist at N9, nor certify the numerical relaxation's
exact optimum. Correlation in a pseudo-moment vector by itself also does not
rule out a mixture of graphons; the branch certificate is what proves the bound.

## Independent verification and artifacts

- `prepare.py` defines complete rooted flag lists.
- `generate.cpp` accumulates product coefficients over labelled-graph orbits.
- `check_tables.cpp` separately enumerates all 5040 vertex orders of each
  representative. It compares all 58,413,888 new matrix entries exactly,
  checks objective and triple coefficients, and verifies coverage of all
  2,097,152 labelled graphs by the 1044 distinct orbits.
- `solve.py` solves the control/branch SDP; `certify.py` proposes rational duals.
- `check.py` does not import the solver or certificate generator. It verifies
  flag lookup semantics, coverage of all root types, independently reconstructs
  deletion marginals, checks 58 rational matrices per certificate by exact LDL,
  and accumulates graph coefficient identities with Python integers.
- `combine.py` verifies the exhaustive partition and reused-certificate hashes.

Scripts are in `experiments/energy_bootstrap_n7/`; reports are in
`reports/energy-bootstrap-n7-001/`. Read `combined-check.json` for the final
result and `table-check-receipt.json` for coefficient-enumerator bindings.
Three new exact certificates cover the control and two branches; 174 new
positive-definite matrices passed rational checking. The inherited N6 Gram
identity was previously independently enumerated and is hash-bound in receipts.
This is an exact computer-assisted argument with the informal flag-square and
independence proof, not a Lean/kernel theorem.

An initial certificate-generation attempt deliberately stopped at an aggregate
int64-overflow guard. The corrected version uses arbitrary-precision integers
for aggregate penalties (and for individual products if required); all proposed
certificates were then independently checked. The failed log is preserved.

## Reproduction

Use the existing offline uv environment with numpy, scipy, cvxpy and networkx,
and OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=VECLIB_MAXIMUM_THREADS=1. Every Python
numerical/check job and C++ enumeration enforces a 175-second alarm.

    uv run --offline --with numpy --with scipy --with cvxpy --with networkx python experiments/energy_bootstrap_n7/prepare.py
    clang++ -O3 -std=c++17 experiments/energy_bootstrap_n7/generate.cpp -o /private/tmp/energy-n7-generate
    /private/tmp/energy-n7-generate reports/energy-bootstrap-n7-001/coefficients.bin reports/energy-bootstrap-n7-001/six.txt < reports/energy-bootstrap-n7-001/input.txt
    clang++ -O3 -std=c++17 experiments/energy_bootstrap_n7/check_tables.cpp -o /private/tmp/energy-n7-check
    /private/tmp/energy-n7-check reports/energy-bootstrap-n7-001/coefficients.bin < reports/energy-bootstrap-n7-001/input.txt

Run `solve.py`, `certify.py`, and `check.py` in that order for each argument
`control`, `0.3125,0.375`, and `0.375,0.4375`, under the same uv environment.
Then `python3 experiments/energy_bootstrap_n7/combine.py` verifies combination
with the preserved N6 certificates. Exact receipts are portable; cached
numerical dependencies are not needed for the C++ table check or combination.

Decision: pursue richer disjoint-motif constraints or apply this approach to a
recovered higher-order baseline. N9 is not available as a reproduced solve in
this workspace, so frontier improvement remains a separate substantial task.
No next experiment is running automatically.
