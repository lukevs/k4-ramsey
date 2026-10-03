# Finite-group kernel spectrum screen

Date: 2026-09-27. This lane tests whether changing the centered latent relation
spectrum improves the exact triangle reward relative to C4, diamond, and K4
costs on the frozen two-parameter parent. It is a restricted construction
screen, not a novelty or optimality claim.

## Contract and representation

Every latent type set is a finite group with uniform mass. A primitive integer,
inverse-invariant class function `f` defines the oriented fine block

    K_h(a,b) = f(a^-1 h b).

The reverse coarse orientation uses `h^-1`, hence its block is exactly the
transpose. Uniform row and column sums vanish. The parent matrix and its 1,248
fractional-edge support stay fixed. Raw scaling is removed by requiring the gcd
of nonzero kernel values to be one; the scalar integer amplitude `q` remains
separate. For every kernel the degree-three through degree-six coefficients and
complete feasible integer interval are recomputed rather than transferred.

The preregistered library contained two Z4 spectra and three S3 class functions:
the standard character and its sum/difference with the sign character. It
quotients obvious global scaling and sign duplicates. These translation-
invariant kernels do not cover arbitrary centered symmetric matrices or
unequal type masses.

## Result

All five kernels passed literal ordered-tuple tests on base orders two and
three, including repeated coarse indices. The complete one-process screen and
one deterministic exploitation pass took 6.82 seconds.

The pure S3 standard character was best in the identity-phase screen. Its
values on identity, transpositions, and 3-cycles are respectively `2,0,-1`.
It selected `q=-9330`; one exact phase/support coordinate descent at that
amplitude made 340 edges inactive and retained 908 identity-phase edges. No
nonidentity phase was retained. Exact reoptimization then reached the
feasibility boundary
`q=-14472`, with polynomial coefficients

    C3 = 2982122860976145137664
    C4 = 140926564882921536
    C5 = -375468670080
    C6 = 0.

The resulting predicted density is

    66019395791930410328084302012171
    / 2190500237194380405786303138889728
    = 0.030138958522318564...

This is `1.0980217398595925e-9` below the independently recounted phased-Z5
control on the same parent. The explicit candidate has order 1,152, unit
masses, probability denominator 65,536, and base-major/type-minor indexing.

Candidate:
`reports/kernel-library-001/graphon-candidate.json`

SHA-256:
`14d9a93f56a4b8359211c210f534af4e1b2bc5c33dda0c2e514e78f0aec0b2fa`

Evidence at handoff is an exact sparse motif polynomial plus tiny literal
falsifiers and construction range/symmetry checks. It was not promoted or
independently recounted because the subsequently verified `0.030138904006...`
construction is materially stronger and verification budget was reserved for
potential promotions.  No process remains in this lane.  Selection was
deliberately heuristic: only the best identity-phase
kernel received phase/support optimization.  Therefore this run does not show
that the S3 standard character is best in the library after phase optimization;
a kernel with a worse identity-phase score could still optimize better.
