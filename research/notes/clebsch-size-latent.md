# Lane A: finite centered latent kernels

Contract: local only, one single-threaded job at a time, each <=180 seconds;
6–8 minute target including setup and validation. Writes isolated to this note,
experiments/clebsch_size_latent and reports/clebsch-size-latent-*.
Objective: ordered K4 red+blue graphon density, including repeated indices and
probability diagonals. Twelve equal Clebsch copies remain fixed.

H-A1: Replace the shared binary sign kernel in the E5 depth-1 construction by
a centered symmetric 3-type kernel with unequal latent masses, retaining its
optimized edge-specific amplitudes. Prediction: mixed diamond/K4 moments give
a decrease relative to the exact same-amplitude binary baseline. Disconfirmation:
bounded multistart search finds no decrease. This is not a global obstruction.

Provenance: round4-E5 sign identity; extension by expanding all 64 edge subsets.
Unlike latent_weights (five fixed Z5 kernels), this changes an additional latent
kernel jointly with its masses. Unlike E9, no voltage assignments or random
cyclic initialization. The amplitude shape is fixed, a limitation of this pilot.
Controls: literal tiny weighted ordered tuple recount, duplicate-label invariance,
binary baseline compared with exact published E5 depth-1 delta. Evidence is
numerical search only unless independently audited. No promotion authorized.

## Completed results (2026-09-29)

Code: `experiments/clebsch_size_latent/run.py`, `validate_exact.py`.
Evidence: `reports/clebsch-size-latent-001/{report.json,coefficients.json,run.log,exact-validation.json}`.
Source revision: 66b6eadbc3d67a025fce49c41e46f9f2c29127f9.
Input and search source SHA256 values are recorded in report.json.

The centered-kernel expansion is
`Delta = C3 t(triangle,K) + C4 t(C4,K) + C5 t(K4-e,K) + C6 t(K4,K)`.
Centering kills every edge subset with a degree-one vertex. Each vertex is sampled
independently, including when base class indices repeat; all diagonal values are
retained. C3 and C4 reuse the E5 contraction; C5 and C6 use a new common-neighbor
contraction. In particular C5 has the factor 6 and complementary-edge coefficient
`2P-1`, and C6 has factor 2. Weights of refined classes are `w[a]/960`.

The rounded E5 amplitude over denominator 65536 gives:

- C3 = -7.1782104552186336e-9
- C4 = -1.1235649841606751e-9
- C5 = +7.952345516763437e-11
- C6 = +3.311535718465165e-12

Binary control reproduces the exact E5 delta -8.301775439379298e-9 to <1e-20.
Best density retained: **0.03013889526362365**, zero improvement versus the
same-family exact binary control, **+7.697126429284662e-9** versus the structured
exact depth-2 incumbent 0.030138887566497220. It improves d4763 by 8.3018e-9
only because the existing E5 amplitude already does so; this is no new result.

Ran 12 starts each for k=3 and k=4, seed 2917, including an exactly duplicated
binary start for each size. SLSQP optimizes a symmetric unconstrained matrix R
and k-1 weights; K=(I-1w^T)R(I-w1^T) centers it exactly. Bounds enforce |K|<=1
and each mass >=.02. Maximum 180 iterations/start. All 24 final points feasible
at the stated 1e-8 tolerance. The apparent best numerical decreases were around
1e-21, treated as roundoff; no candidate saved or proposed for promotion.

Float tiny weighted literal recount: error 2.95e-16; duplicate-label error
7.08e-16. Separate exact rational edge-subset expansion equals integer direct
ordered count exactly, with nonzero probability diagonals and unequal masses;
unequal duplicate splitting also gives exact equality. Exact fixture's delta is
150475/231928233984. This is implementation validation, not independent audit
of a new full-size witness. Root independently auditing candidates is separate.

Commands (sequential, no additional agents, no remote/paid work):
```
VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 uv run --offline --with numpy --with scipy python experiments/clebsch_size_latent/run.py
VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 uv run --offline --with numpy --with scipy python experiments/clebsch_size_latent/validate_exact.py
```
Actual search including float validation/coefficient setup: 0.989 s; exact
validation: 0.019 s. Each process has a 175-second alarm. Setup/read/analysis
were the bulk of this bounded pilot. No processes remain active.

Decision: **unsupported in this tested regime**. Retire this common centered
kernel replacement with fixed E5 amplitudes. No inference against other cyclic
sizes, varying amplitude shapes jointly with latent kernels, masses below .02,
or genuinely edge-dependent finite kernels. No novelty or optimality claim.

### Central structural observation and counting scope

All 24 optimized kernels collapse numerically to two sign groups: with
`s[a]=sign(K[0,a])`, maximum entrywise `|K-aa' - s[a]s[a']|` across all runs
is **7.366e-12**. Each group's total mass is **1/2 within 7.117e-14**.
Three-label solutions split as 1+2 or 2+1; four-label solutions as 1+3,
2+2, or 3+1. Thus added labels provide subdivisions of the existing binary
kernel in these runs. Per-run data: `effective-groups.json`.

Full-family counting assumptions: base masses uniform 1/960; same symmetric
latent K and same mass vector w in every base class; w sums to one and Kw=0;
P symmetric; A symmetric with zero diagonal and supported on P's fractional
entries. A is exactly the rounded E5 depth-1 shape and is held fixed. Each of
the four sampled latent variables is independent, even when base indices
coincide. The contraction includes all ordered base tuples, normalized by
960^4; latent moments include their own product weights and probability
diagonals. Only six-edge-subsets' graph isomorphism types and exchangeability
are used for multiplicities (4 triangles, 3 four-cycles, 6 diamonds, 1 K4).
No Z5 representative-row symmetry is assumed. Tiny exact validation has three
base classes, so its six-edge coefficient vanishes; it does not independently
validate a nonzero full-size six-edge coefficient. The float tiny fixture has
the same limitation. The full-size coefficient calculations remain search-side.

This supports only a restricted fixed-common-kernel/fixed-amplitude-shape
negative result, not a conclusion about all latent refinements.
