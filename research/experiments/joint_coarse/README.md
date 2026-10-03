# Joint coarse-probability reoptimization

This lane freezes the exact phase/support assignment and amplitude `q=-5496`
from `reports/association-scheme-phase-001`, then reoptimizes the two original
coarse fractional probabilities `p,h`. Every evaluation rebuilds the phase
motif coefficients from the changed coarse matrix; no latent coefficient or
feasibility margin is reused from another `P`.

The exact unit-neighbor gate was negative in both increasing directions. Three
alternating exact degree-at-most-six coordinate-line sweeps converged from

    (p,h) = (51064,35015)

to

    (p,h) = (51068,35027).

The candidate in `reports/joint-coarse-001` has predicted exact density

    8252424762894922831636689905795
    ---------------------------------
    273812529649297550723287892361216

or approximately `0.030138959577433254`. This is a strict improvement over its
matched frozen parent but is weaker than later phase/amplitude candidates. It
therefore supports the mechanism—optimized phases shift the best coarse
probabilities—without becoming the campaign incumbent.

The serialized 960-class matrix is range-, symmetry-, and coarse-marginal
checked. Its SHA-256 is
`49dac8676830d66a17ba917610fea532c05d7866f6630142a2aab1864718dc3a`.
An independent audit was delegated to the precision checker lane. The local
`audit.py` is a fallback generic ordered-index recount driver and was not run,
to avoid duplicating that allocated checker process.

Scope: exact alternating coordinate minima for two probabilities with the
phase assignment and amplitude fixed. This is not a global two-variable
optimality proof, a nonuniform edge-type search, or a graphon record claim.

## Active clipped-face follow-up

`boundary_face.py` instead starts from the later two-amplitude candidate and
co-adjusts each active coarse mean with its amplitude while keeping the
already-clipped latent cell on its boundary.  Inactive coarse blocks remain at
the original `p,h`.  Every sample directly recounts the changed 192-class
coarse graphon and rebuilds the typed phase polynomial, so coefficients from
the fixed-base search are not reused.

The exact coordinate screen checked all three possible integer residues of the
active `h` boundary.  Here `r=active_h+3*q_h=active_h mod 3` on the tight
integer boundary `q_h=-floor(active_h/3)`, so the complete boundary residue
set is `r in {0,1,2}`.  (Slack 3 or 4 is interior, since decreasing `q_h` by
one remains feasible.)  Each face selected `t_p=0,t_h=42`; residue zero was
best:

    active_p = 51064, q_p = -7236
    active_h = 35139, q_h = -11713

The candidate in `reports/joint-coarse-boundary-face-001` has predicted exact
density

    1375401591138773841968807740019
    --------------------------------
    45635421608216258453881315393536

or approximately `0.030138904006337588`, about `4.16e-10` below its matched
two-amplitude control.  A 4-coarse-class literal expansion falsifier passed,
as did range, symmetry, inactive-block, and active-block mean checks.  The
serialized 960-class candidate SHA-256 is
`b93b3589a5be4846436f1f721df5efaf06a6bc852c008e00cf74cdce0d87e838`.
The independent compressed recount in
`reports/graphon-joint-coarse-boundary-face-compressed-001` exactly agrees
(report SHA-256
`7faaf29b1b505874898c4944d7259ef98292cd03100f8f8a428ef7829214797b`).
This promotes the exact count evidence, but no global-optimality or literature
record claim is made.
