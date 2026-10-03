# Canonical pair refinement of the four-sheet quotient

## H-QR-001

This screen is a graphon refinement, not a claim about exact finite quotient
statistics.  The 384 fine blocks are independent step-graphon probabilities;
the full ordered count retains repeated fine indices and diagonal cells.  It
does not retain correlations between incident edges of the finite 768 graph.

Each discovered four-vertex fiber is incident to a unique degree-two block,
and that block is two disjoint `K2,2`s.  The twin classes at its two endpoints
canonically split both old fibers into two pairs.  This gives 384 cells of size
two without mixing different old fibers.  The production source asserts exact
ordered equality between the freshly discovered fibers and the stored
four-sheet quotient, so its seed-derived directions are aligned with the
retained 192 probability matrix.

For a fine pair of cells inside an old block `i,j`, define

    D = (exact red density of the seed's 2x2 subblock)
        - (exact red density of the seed's 4x4 old block).

The tested graphon is `P_ij + epsilon*D`.  The four directions within every
old block sum exactly to zero.  Thus `epsilon=0` duplicates each equal-mass old
class twice and is mathematically the same 192 graphon; the exact U256 recount
must reproduce the parent density.  This is the matched lifted-parent control,
not a reconstruction of the finite 768 graph.  Reversing both pair labels in
every old fiber is checked as a simultaneous fine-class relabeling.

The parent is `literature-two-parameter-001`, density
`0.03013897728988013`.  It is the strongest 192-class mean parent to which the
seed fibers align directly, but it is weaker than the current checked 960-class
construction `0.03013890356539909`.  Any result must be compared with both.

Prediction: a nonzero common amplitude on the actual pair-density direction
improves the duplicated 192 parent.  Seven exact values determine the
degree-at-most-six numerator polynomial; every feasible integer amplitude on
the `1/256` grid is then evaluated, and the selected point is directly
recounted.  Tiny arbitrary matrices test Newton interpolation, including held-
out negative coordinates.

## Result

Run001 is a preserved precompute failure: Python `math.comb` rejected the
negative held-out interpolation coordinates before production data or a CPU
recount was touched.  Run002 fixed this with generalized integer binomials.
An adversarial preflight then identified missing explicit fiber-order
alignment, floating interval ceilings, and a vacuous code check for degree
above six.  Run003 is the audit-clean result: it adds exact stored-fiber
alignment, integer ceiling division, and an exact relabeling construction
check.  The selected-point direct recount remains the interpolation gate.

The feasible grid was `[-226,226]`.  The exact optimum was
`epsilon=123/256`, with density

    515776638127812641542888831097
    --------------------------------
    17113283103081096920205493272576

or `0.030138964862619`.  This is an exact improvement of about `1.24e-8` over
the lifted 192 parent, so the preregistered mechanism prediction passes.  It is
still about `6.13e-8` worse than the checked global incumbent and is not a
promotion candidate.

There are 4,608 nonzero lower-triangle fine directions, with grid units
`{-128,-64,64,128}`.  Biregularity forces every centered two-by-two old block
to be a rank-one sign pattern; the exact polynomial in fact has degree four.
Consequently this experiment is algebraically a binary rank-one latent-sign
perturbation `c_ij [[1,-1],[-1,1]]`, with a new seed-derived heterogeneous
coefficient matrix `C`; it is not a fundamentally different graphon
mechanism.  It identifies the actual seed's canonical binary phase and fixed
`h:p` magnitude ratio `2:1`, differing from prior coefficient/support choices.
It supplies positive structural evidence inside the already explored
latent/phase representation.  Further scalar or typed
amplitude polishing is therefore not the high-level next step.

Run003 report SHA-256:
`693918ace912098c40afd056217362ebefeb038e5d181e84f673f4c5b09dde8c`.
Candidate SHA-256:
`08798b82fc1b22c0fdd0bab3294a000bd21a5103254baa7ae407d17708e0dacc`.

A separate precision lane then read only that serialized candidate and passed
12 tiny fixtures, conservative overflow bounds, and a fresh generic U256
ordered-index recount.  It obtained total
`51919776393744889768173715099811315712` over
`384^4*65536^6`, reducing to the same fraction above.  Independent audit
report SHA-256:
`14748355a58fbee29075ae65578f4bb2a16c7f286d68f2c76194f9af31d77bbe`.
