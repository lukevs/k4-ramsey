# Focused Clebsch-bowl program and Hadamard-668 comparison

Date: 2026-09-29. Distributed search is paused. This note narrows the research
question to the local family organised by the twelve-copy Clebsch template.

Update: the first focused tests are complete; see
`clebsch-bowl-focused-tests.md`. Both weakest solid types resist opening at
the depth-2 point in an exhaustive finite numerical gradient screen. New
probability-box localizers tighten the numerical relaxation, but expose
four-cycle correlations as a second major source of looseness.

## The three nested questions

These should not be called the same "local bowl."

1. **Two-level Clebsch family.** Vary only the coarse bridge probabilities
   `(p,h)`. This problem is solved exactly: the polynomial `F(p,h)` has one
   critical point and a unique global minimum
   `0.030138977289665338...` in `[0,1]^2`.
2. **Fixed-support refinement bowl.** Keep every 0/1 block fixed and keep the
   Clebsch quotient, but allow the two coarse bridge means `(p,h)` to move and
   replace each fractional bridge by an arbitrary finer kernel with that mean.
   This contains the Z5 lift and its E5 `Z2^k` sign refinements. Its infimum is
   unknown. This is the main target.
3. **Support-opening bowl.** Also allow currently solid red/blue orbitals to
   move into `(0,1)`. C1 found two nearly competitive one-sided directions,
   but omitted diamond and K4 rates, so it is not yet known whether the fixed
   support is protected by a positive wall.

The next claim should concern (2) only unless (3) is first settled.

## Exact local model

Write a refinement as

`W'((u,x),(v,y)) = W_uv + D_uv(x,y)`

on the 1,248 fractional unordered pairs of `W = W_(p,h)`, with zero row and
column means for `D`, symmetry under reversal, and pointwise bounds
`-W_uv <= D <= 1-W_uv`.
The exact objective change is

`Delta F = T3 + T4 + T5 + T6`,

where the terms are supported respectively on fractional triangles, closed
4-walks, diamonds, and fractional K4s. There is no linear or quadratic term.

The fractional support is three identical 64-vertex components. It has 1,152
triangles, all of type HPP, and every triangle has the same positive cubic
coefficient `c3 = 0.83901547...`. A gain therefore requires negative latent
holonomy around these triangles. The opposing cost is mostly the 4-cycle term.
Previously measured refinements have small diamond terms, while the original
lower relaxation assigned a very negative diamond term. The focused localizer
test reduces that term but shifts the relaxed improvement to four-cycles.
Their joint realizability is the unresolved mechanism; diamonds alone are
not sufficient to settle it.

## Strategy to locate the bottom

The program should produce monotone upper and lower bounds on one precisely
defined infimum rather than continue greedy class doubling.

### A. Upper bounds: optimise compact latent seeds

1. Use the character representation already validated by the F5 checker.
   Start from the existing Z5 phase kernel and optimise all characters of
   `Z5 x Z2^k` jointly for `k=1,2,3`, rather than stack one rank-one split at
   a time. Keep the families nested, so every new value is a valid upper bound
   on the same infimum. The current checked depth-2 object is in the
   `Z5 x Z2^2` member of this ladder.
2. Evaluate candidates directly through `(T3,T4,T5,T6)` without materialising
   `192*5*2^k` classes. Re-optimising `(p,h)` should remain available; C1's
   estimate of a small extra benefit is numerical, not a uniform certificate.
3. Add a deliberately diamond-sensitive ansatz. Rank-one sign kernels and
   balanced Paley/Clebsch signs have essentially zero odd diamond moment. Use
   general zero-row transition tables or coupled characters so that the spine
   variable `D_xy` can correlate with the product of the two triangle paths
   across a diamond. Reject it quickly if `T5` remains below `1e-8` or if the
   4-cycle cost erases the gain.
4. Extract compact seeds from the lower-bound SDP Gram matrix and round them
   into finite latent kernels. This is preferable to blind depth extension.

### B. Lower bounds: strengthen the moment/SOS relaxation

1. Strengthen C1's true-box moment SDP with pointwise localising constraints
   from `(D+W)(1-W-D) >= 0`.
2. Include all words needed to couple a diamond and its surrounding 4-cycles,
   then all words through degree six. Average the relaxation under the full
   automorphism group before solving.
3. Inspect the dual. A useful run ends with either a rationalised dual
   certificate or a concrete moment pattern that can be rounded into an upper
   construction. A solver decimal alone is not a bottom.
4. Increase the level until the certified lower bound and best construction
   differ by at most `1e-9`. If the same finite latent seed is extracted at
   successive levels, attempt an exact algebraic description of the limit.
   This is a target, not an established convergence theorem for the current
   relaxation. Full consistency and independence of latent samples must be
   respected before claiming convergence over arbitrary graphons.

### C. Certify the wall before widening the bowl

For the two cheapest hard orbitals (H-on-S and intra-copy off-C), compute the
full one-sided directional optimum including triangle, 4-cycle, diamond, and
K4 rates, coefficient changes as the coarse means move, and terms containing
multiple newly opened edges where rare latent states can contribute at first
order. Positive gradients at one finite point do not give a uniform moat
around the whole bowl. A verified negative derivative would identify a reason
to widen the upper-bound model.

### Stop conditions

- **Bottom located:** certified lower bound and checked upper construction
  differ by at most `1e-9`.
- **Diamond route retired:** the strengthened SDP reduces its diamond credit
  by at least tenfold and raises the lower bound to the achieved range.
- **Bowl must widen:** a hard orbital has a certified negative one-sided rate.

## Hadamard order 668: what actually matches

The order-668 result announced in August 2026 is exactly reconstructible from
four sign sequences of length 166. Their negative supports form a cyclic
`H_4^*` difference family `(166;82,83,83,83;164)`. Four circulant/anti-circulant
blocks plus four border rows and columns produce the 668 by 668 Hadamard matrix.
The combined periodic autocorrelation of the four sequences is `-4` at every
nonzero shift, and this compact identity implies exact row orthogonality.

The meaningful resemblance to our result is:

| Order 668 | Clebsch K4 construction |
|---|---|
| a visually complicated 668 by 668 matrix | a visually complicated 768-vertex colouring |
| four cyclic seeds on `Z_166` | twelve Clebsch copies with group coordinates |
| block-circulant/anti-circulant array | Cayley/quotient block structure |
| orthogonality collapses to autocorrelation identities | the local objective collapses to `T3`-`T6` moments |
| Hall switching changes entries while preserving exact feasibility | latent splitting preserves coarse means while changing higher moments |
| exact reconstruction plus independent matrix verification | compact rule plus independent exact K4 recount |

This is a real methodological rhyme: find the compact group-indexed seed,
optimise correlation data there, and verify the expanded object independently.

It is not evidence that the two objects share a construction theorem. Hadamard
668 is a finite exact-feasibility problem: once the autocorrelations match,
the residual is zero. The Clebsch problem is a continuous optimisation over
arbitrarily fine kernels, and breaking symmetry improves the value. The order-
668 search provenance is also still unknown, so there is no documented search
algorithm to import. The useful import is the correlation-first representation
and switching viewpoint, not the picture itself.

## Sources for the Hadamard comparison

- Primary announcement and decoder are linked from the exact reconstruction
  record: https://github.com/nreff/hadamard-search/blob/main/fixtures/known/hm-668/README.md
- Structural reconstruction and proof:
  https://github.com/nreff/hadamard-search/blob/main/docs/research/hm-668-construction.md
- Public structural discussion of the four-block core:
  https://mathoverflow.net/questions/85201/status-of-hadamard-matrix-conjecture
- A later switching analysis reports a Hall switch producing a second
  inequivalent matrix; this is a recent preprint-level source:
  https://hadamard-668.vercel.app/
