# Hamming plus orthogonal quadratic relations

Date: 2026-09-27.  This screen changes the coarse representation to the group
`Z3 x F2^k`.  A relation probability depends jointly on the Z3 zero/nonzero
orbit, Hamming weight, and a nondegenerate quadratic-form value.  Both the
split form

    Q+(z) = z0*z1 + z2*z3 + ...

and the nonsplit Arf-one form

    Q-(z) = z0 + z1 + z0*z1 + z2*z3 + ...

were tested.  These are genuine orthogonal association-scheme primitives, but
the bare Cayley kernels are not claimed to reproduce Thomason's more elaborate
orthogonal tower/cover.

Translation fixes the first of four samples.  At `k=6`, exact enumeration of
`27*64^3 = 7,077,888` translated triples aggregated to at most 9,766 repeated
six-relation signatures.  A separate `k=4` literal translated enumeration
matched the compressed evaluator for arbitrary probabilities for both forms;
constant-probability and componentwise-complement controls also passed.

The best `k=6` trajectory came from the nonsplit form and a nonrandom syndrome-
alternating seed.  Projected Adam reduced the objective as follows (the stored
prefix milestones are iterations 1, 100, and 400):

    0.031511475736186317
    0.030140621203525585
    0.030140621056356114

The final projected box-KKT residual in the 28 tied relation parameters is
`3.97e-14`.  Rounding all parameters to denominator 65,536 gives exact
translated-census numerator

    16901897618722474829755212952533952

over denominator

    560768060721761383881293603555770368

or approximately `0.030140621056356332`.  This is only `1.72e-6` above the
campaign incumbent, a much stronger adjacent baseline than the Hamming-only
screen, but it is not a promotion.  The materialized 192-class candidate is
`reports/quadratic-scheme-001/graphon-candidate.json`, SHA-256
`a26ecdaaf9522989c6affccb45ec6c29533c55a1501bd99526a3a3e148f9e440`.

The analogous `k=8` screen was worse at `0.03016895435431359`, so dimension
growth alone did not help this selected family.

An unrestricted analytic block-gradient diagnostic on the rational `k=6`
candidate found no improving inward direction among deterministic zero/one
blocks, including diagonal coordinates.  It reports 2,688 nonstationary
fractional symmetric coordinates, with maximum derivative magnitude
`0.00381704`, but a relation-by-relation audit shows that gradients within each
quadratic/Hamming orbit are constant to at worst `6.4e-10`.  Thus this is the
expected denominator-65,536 rounding residual in the tied orbit probability,
not evidence for a symmetry-breaking block direction.  Recovering the
continuous orbit optimum would only return the already reported numerical
value.  The diagnostic is double precision and proposal-grade, not an exact
KKT certificate.

Evidence:

- `reports/quadratic-scheme-001/report.json`
- `reports/quadratic-scheme-001/gradient-report.json`
- `reports/quadratic-scheme-k8-001/report.json`
