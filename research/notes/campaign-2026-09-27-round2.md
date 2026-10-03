# Research window: 20:04–21:04 UTC, 2026-09-27

## Strongest checked artifact

The current 960-step rational graphon has exact monochromatic K4 density

`16900934504649027287619486865996291 / 560768060721761383881293603555770368`

or approximately **0.03013890356539909**. Candidate:
`reports/association-scheme-per-edge-boundary-continuation-001/graphon-candidate.json`.
SHA-256: `d4763fefc34a3966bfbe811d279b522c067f193e436bb522d357dd423c0c58c3`.

The independent direct ordered U256 counter reads only the candidate matrix,
retains repeated class indices, and matches the exact search prediction.
Report: `reports/graphon-association-per-edge-boundary-continuation-direct-u256-001/report.json`.
Report SHA-256: `634a92d73e6c6e15e10e72a7d4da6462894862f73c528e798241eebca94d7b01`.
Twelve tiny literal oracle cases and explicit arithmetic bounds pass. Full count:
104.744 seconds. The adversarial review is in `current-best-adversarial-audit.md`.
This is an exact independently checked computational construction with an audited
asymptotic existence argument, not a kernel proof or a global optimum.

## What produced progress

1. Latent centered kernels gave exact cubic-through-sixth-degree corrections.
2. Five-state cyclic phase optimization reduced the positive C4 penalty.
3. Alternating phases and amplitude reached a probability constraint.
4. Separate amplitudes for two coarse block types removed the shared constraint.
5. Moving the coarse mean and amplitude together along a boundary face improved it.
6. Individual edge amplitudes gave a final smaller gain; marginal gains became
   negligible, so further polishing was stopped without a local-optimum claim.

## Infrastructure completed

`experiments/compressed_graphon/README.md` documents exact polynomial adapters,
normalization, evaluation/minimization, feasibility and the verification workflow.
Thirteen utility/independent tests pass. The candidate-bound typed histogram
plus compiled Lean arithmetic checked a five-type phase artifact in3.102s versus
111.658s direct (5.248s including compilation and tiny fixtures). Native code
remains trusted for histogram binding; Lean alone does not certify that binding.
For the final diverse per-edge candidate compression is less useful, so the
independent direct checker is used instead.

The dashboard headline and timeline now include every supported independently
checked binary, weighted and graphon evidence type. Exact fractions determine
ranking. Legacy graphon file timestamps are explicitly labeled when completion
time was not recorded. Twelve dashboard regression tests pass.

## Structural exploration and useful negative evidence

- Nonabelian/spectral kernel library: a valid S3 search result was weaker than
  the incumbent; no best-in-library or independently checked value claimed.
- Hamming-distance probability models: tested basins were weaker. The corrected
  red-clique-diagonal Franek–Rödl control exactly reproduced the historical value.
  This does not exhaust the family; the PPSS shell projection was not tested.
- Quadratic-form relation models: a distinct k6 numerical construction reached
  approximately0.03014062105636, substantially better than the tested plain
  Hamming basins but still worse than the incumbent. The k8 test was worse.
  Exact materialization gives0.030140621056356332. The gradient diagnostic
  finds no improving deterministic boundary coordinate. All2688 fractional
  gradients agree within6.4e-10, consistent with uniform probability rounding;
  this is not evidence of a hidden first-order symmetry-breaking direction.
- Intrinsic composition-factor audit: the visible3×64 partition does not justify
  an ordinary composition or one-kernel product. Missing Cayley vertex labels
  prevent treating row bits as group coordinates.
- Coarse means: no numerical inward boundary-sign violations on the original
  parent; exact sampled orbit/paired lines did not improve it. Fractional
  stationarity and arbitrary collective directions were not certified.
- Alternative size-four partitions: none beat the matched original partition.
- Deterministic Seidel switching: the tested structural cuts and all singleton
  flips worsened the coarse marginal. Larger joint cuts remain untested.
- Common latent masses: numerical gradient/curvature and a numerically evaluated
  exhaustive small-denominator grid favored uniform weights. No exact PSD or
  global optimality certificate was established.

## Next research choices

Prioritize changed representations over further tiny amplitude polishing:

1. Split original four-vertex fibers into canonical size-two pairs instead of
   mixing fibers; test a384-class quotient with a matched lifted-parent control.
2. The exact quadratic k6 baseline is now available for collective second-order
   or relation-refinement tests; its first-order diagnostic did not reveal an
   improving new support direction.
3. Recover valid Cayley coordinates or a richer certified graph-directed factor
   before attempting a recursive stationary-profile construction.

The user clarified that the much lower result they heard about is unpublished
and supplied no number/source. January's public announcement remains only the
rounded inequality c4<0.030139 in our evidence. Neither hearsay nor crossing
that rounded threshold establishes a record comparison.

No new experiment admission after21:00; final process confirmations are recorded
in RESUME.md. Local-only, four concurrent CPU jobs maximum throughout.
