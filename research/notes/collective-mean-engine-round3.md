# H-TR3-2: five-orbit collective-mean screen

Date: 2026-09-27. Status: completed negative result in the stated restricted
subspaces; the separate 1248-coordinate nonconstant screen remains open.

## Question and scope

Starting from the immutable order-192 rational parent with denominator 65536,
test the five certified fractional pair-orbit constants. The orbit sizes are
480, 96, 480, 96, 96. Relations 0, 1, 2, and 4 have parent numerator 51064;
relation 3 has numerator 35015. This is an invariant five-dimensional slice,
not the full 1248-dimensional fractional-edge space.

The exact engine run first established

```
G0/960 = G1/192 = G2/960 = G4/192
       = -52946151201272210534400,
G3/192 = -7240758287166536220672.
```

Therefore `5*d0+d1+5*d2+d4=0`, with `d3=0`, is exactly first-order neutral.
This gate justifies the native weighted group `[0,0,0,-1,0,-1,-1]`; equality
was not inferred merely from the common parent probability.

## Results

The weighted-neutral run has dimension 3, numerical minimum restricted
Hessian eigenvalue `+2.2381023451584748e-5`, exact rounded group residual zero,
and returns the parent unchanged. More strongly, an exact integer nullspace
basis has zero exact linear coefficients, and the three leading principal
minors of its exact restricted second-derivative matrix are all positive.
Sylvester's criterion therefore proves positive definiteness on this precise
3D subspace.

The all-five-free configuration has dimension 5 and numerical minimum Hessian
eigenvalue `+1.6991235982069643e-5`. Its continuous optimizer reports a very
small improvement, but independent dyadic rounding changes only `h` from
35015 to 35014 and is exactly worse than the parent. It produced no candidate.
This is recorded as a continuous improvement not retained at denominator
65536, not as an independently exact improvement or a numerical artifact.

This result closes neither compensated p/h directions nor nonconstant modes
within the 1248 fractional coordinates.

## Evidence

- Unconstrained exact baseline:
  `reports/collective-mean-five-orbit-engine-002/report.json`.
- Weighted-neutral run:
  `reports/collective-mean-five-orbit-weighted-neutral-001/report.json`, SHA256
  `8e8ca59cef21560ecd7271f87c8278d86d7daea7d1adba415ecbd3fa3a7e66b3`.
- Free-five run:
  `reports/collective-mean-five-orbit-free-001/report.json`, SHA256
  `a54235935e9fd37b442eda2cd2be530a36135ec4160bbfb7fd2cf4ff09780b3a`.
- Exact restricted certificate:
  `reports/collective-mean-five-orbit-exact-audit-001/audit.json`, SHA256
  `e62cbdc59339a5b2f8497ccc7b2a9f512af1afcb758c47a73fd33feef8b5d1bc`.
- Shared engine binary SHA256
  `e66388bbef9093035d469b7acb117ee9821ca6c935936d4af4566e65f3c86784`;
  source SHA256
  `78c49a2587abfa28675242c275d6955080af8586151b1d7e877877adbaee3013`.

## Throughput observation

After the frozen engine became available at 17:24:18 local time, the exact
unconstrained result was written 38 seconds later. The two new configs were
prepared and both exact runs completed by 17:26:57. Native compute was 0.831
seconds and 0.828 seconds respectively; their sequential wrapper call took
2.2 seconds. The exact Sylvester certificate was complete by 17:28:21. Thus
the remaining latency was consumer configuration, interpreting the constraint,
and documentation rather than objective computation.

Minimal reuse commands:

```
python3 experiments/collective_mean_engine/make_variants.py \
  --input reports/collective-mean-engine-input-001/input.json \
  --out NEW_CONFIG_DIR

PYTHONPATH=src:. python3 experiments/relation_engine/run.py \
  --config NEW_CONFIG_DIR/weighted-neutral.json --out NEW_REPORT_DIR
```

The main API pain point is that the engine reports the optimized and rounded
probability vectors but not the continuous optimized vector. For this negative
screen that did not block the conclusion; promotion would still require an
independent exact candidate checker.
