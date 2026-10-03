# H-LAT: high-precision latent sign split

This isolated experiment applies the previously validated latent `+/-` class
split to the strongest `Q=65536` 192-block graphon. It recomputes the exact
cubic and quartic terms; it does not transfer coefficients from the simpler
`Q=41` case.

Three automorphism-respecting supports are screened exactly: the 96 `h` edges,
the 1152 `p` edges, and their union. Each component support is triangle-free,
so its cubic coefficient is zero and its optimum is the unsplit point. Their
union has 1152 supported triangles and gives a nonzero cubic interaction.

The successful run is `reports/latent-precision-002`. Its exact integer optimum
on the original denominator grid is `q=-4752`, hence
`epsilon=-4752/65536=-297/4096`, within the exact probability constraint
`|q|<=14472`. The resulting exact density is

    515776822961911272515012376329
    --------------------------------
    17113283103081096920205493272576

or approximately `0.030138975663240804`. The expansion and an independently
organized ordered-index C++ recount agree. The checker uses bounded unsigned
128-bit inner sums and a self-contained four-limb unsigned 256-bit outer sum,
because the generic normalization exceeds signed 128-bit range.

Twelve tiny literal ordered-tuple tests cover both perturbation signs, repeated
base indices, and a triangle-free support with a nonzero quartic term. A raw
tiny red/blue test separately checks the C++ recount. The initial immutable
run `reports/latent-precision-001` records a pre-recount compile failure from
an unavailable Boost header; run 002 removes that dependency.

Evidence scope: exact computational expansion and exact C++ recount. This is
not a Lean certificate, a formal graphon realization theorem, a novelty result,
or a claim against an unpublished exact bound.
