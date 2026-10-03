# Collective positive block weights

H-CW1 (2026-09-27): collective mass redistribution, not the previous pair-grid
screen. At unit weights the exact gradient is
`g_i = 4 + 28 d_blue(i) + 48 T_blue(i) + 24 K4_both(i)`; the constant4 cancels
under fixed-total-mass directions. Center and negate this gradient, quantize
to bounded integers, and rebalance exactly to obtain sum(d)=0. Search
`w_i(s)=1024+s*d_i` over nonnegative integer s with every weight in[1,65535].
The denominator remains `(768*1024)^4`; compare densities as exact fractions.

For a fixed graph the ordered weighted monochromatic count is homogeneous
quartic in weights. Five complete weighted Lean evaluations at s=0..4 determine
the exact line polynomial by Newton forward differences. Screen every allowed
integer step without more full counts, then separately recount the chosen point
and extrapolation holdout s=5. The old unit checker is unchanged. Lean serves as
the objective oracle here; this is not an independent second implementation of
Lean itself. Tiny literal ordered-tuple tests check interpolation on all64
four-vertex graphs and two collective directions, including extrapolation.

Prediction: asymmetric local edge minima admit a positive collective weight
gain larger than isolated pair movement. A negative result only rejects this
quantized direction/grid on that graph, not weighted optimization generally.
One CPU job at a time, including verification; hard pilot stop20:03:30UTC.

Next distinct mechanism if needed: projected Hessian reconstruction using the
old exact pair t² coefficient B_uv. With anchor0 and basis e_i-e_0,
K_ii=2B_i0 and K_ij=B_i0+B_j0-B_ij. This enables a restricted Newton or
negative-curvature direction. The literature agent pointed to Diao et al.'s
graphon differential calculus (arXiv1403.3736) as related calculus, not as a
source for this vertex-mass formula. Novelty is not claimed.

## First exact weighted result

`reports/weights-collective-gradient-001` starts explicitly from
`pilot-algebraic-polish-bank-002/polish-07` (unit N10486305592). The collective
direction changes724 weights and the chosen step is1. The separately recounted
density is `1921626605346585336283/63751947518740210384896`. This removes
`27649368489652847/549755813888` fixed-768 numerator units (about50293.9083),
placing it about11069.9083 such units **below McKay**. The exact fixed-unit gap is
`-6085746445709935/549755813888`; divide again by768^4 for density difference.
Full weighted Lean recount and extrapolated s=5 agree with the interpolation.
Total16seconds. The parent coordinator reviews promotion. This is not a claim
to beat the stronger2026 announced threshold or a proof of global optimality.

Decision: supported. Restart explicitly from the improved unit construction
`pilot-algebraic-polish-bank-003/polish-02`, not silently within the same trial.

## Curvature-informed follow-up

H-CW2 reconstructs the full exact Hessian at unit weights:
`H_ii=12+36*d_i+24*T_i`, and for i!=j,
`H_ij=48*blue_ij+60*blue_triangle_edge_incidence+24*K4_edge_incidence`.
Project matrix-vector products to the zero-sum subspace and use floating CG to
propose a Newton direction, then quantize and use the same exact quartic line
test and independent full weighted recount. Floating arithmetic proposes only;
there is no PSD or convergence claim. Hessian directional second derivatives
match literal quadruple polynomials on all64 four-vertex graphs; CG is separately
checked on a known positive projected quadratic. Full768 Hessian build is7.7s.

`weights-collective-curvature-001` reaches
`184475309486561516286529/6120186961799060196950016`, about59081.3782 fixed
units below McKay, improving the simple gradient's48305.8859 below.
An explicit restart on the later `pilot-algebraic-cycle-polish-001` unit graph
(N10486219192) gives `weights-collective-curvature-002`, density
`23059300053734294930609/765023370224882524618752`. Its gain from that unit parent
is `139812289408023375/2199023255552` fixed units, added to the parent's47176
units below McKay. Both have separate weighted-v1 Lean sidecars with matching
candidate hashes and exact polynomial/holdout agreement. Runtimes25seconds each.

## Graphon mass screen and independent audit — restart checkpoint19:59UTC

All jobs owned by this worker have completed. No process remains active.
Do not resume research without new-session coordination. The parent owns
`research/RESUME.md` and dashboard updates.

The separate probability-graphon track is **not** accepted by the binary weighted
checker. On `literature-refined-graphon-001`, all192 exact block-mass gradients
are identical, so there is no fixed-mass first-order direction. Four numerical
small-curvature proposals all have exact positive quadratic forms. An exact
fraction-free Sylvester test reached152/191 positive leading pivots before its
45-second timeout (`weights-collective-graphon-002`); this is NOT a PSD certificate.
Tiny literal probability-tuple tests validate the derivative counter. Retire
this mass direction provisionally, not all finite weight changes.

### Stronger graphon audit

`reports/weights-collective-graphon-audit-002/report.json` records a successful
**standalone compiled Lean recount** of the simple192-block probability graphon,
with probabilities0,22/41,32/41,1 and blue block diagonals. It imports only Std,
does not change or import either existing checker, and directly sums ordered
class indices. Red numerator97246023634579968 plus blue97306473336525120 equals
194552496971105088, denominator6455175514775617536, reduced density
`1013294255057839/33620705806123008` (approximately0.03013899413358829).
Twenty tiny random cases, including nonzero block-diagonal probabilities,
matched Python arbitrary-integer literal six-edge tuple products. Full setup,
compilation, fixtures and recount took3.63seconds. Source/binary SHA are recorded.
The earlier audit001 is a preserved compile failure caused by FilePath inference.

The simple and strongest `literature-two-parameter-001` candidate JSONs were
directly checked for square/symmetric matrices, integer probabilities in[0,Q],
zero diagonal, equal unit class masses, recorded candidate hashes, and exact
normalization. Strongest candidate density:
`515776850799050572477656236153/17113283103081096920205493272576`.
For Q65536,n192, `n^4 Q^6 = 107667467658578185705208371882707910656 < 2^127`,
so the original signed128 C++ counters cannot overflow their nonnegative total
or partial accumulations. The ordered counter's long-long pair products are
at mostQ²=2^32; promotion to128 occurs before larger multiplication. For the
simple Q41 case, the same bound is below2^64, explicitly checked by the new
Lean program before UInt64 counting. The sum of red and blue products is at
mostQ^6 for each ordered class quadruple, so the total bound also covers their sum.

The partition-based C++ search and direct ordered-index C++ audit are different
enumerations. They share the mathematical graphon convention and therefore do
not independently prove it. The new Lean counter provides independent language/
arithmetic execution for the simple case, but also uses that convention.
None is a kernel-only theorem proving the formula or its asymptotic realization.

### Realization argument and scope

For m distinct vertices in each of192 equal classes, independently color every
distinct vertex-pair red with probability P_ij. Distinct edges remain independent
even when their endpoints occupy repeated classes. Thus the probability that a
four-set is monochromatic is the product of its six P factors plus the product
of its six(1-P) factors. Repeated **class** indices do not mean reused random
edges; randomizing each finite-template edge once would be a different model.
The expected monochromatic four-set fraction tends to the ordered class sum
divided by192^4; finite vertex collisions contribute vanishing O(1/m) corrections.
For each m there is a deterministic realization at most its expectation.
Minimum finite monochromatic fractions are nondecreasing with vertex count by
averaging induced subgraphs, so their limit exists and is bounded by this F.
This is an elementary prose existence argument, not a serialized finite witness
achieving F exactly, and not a formalized Lean lifting theorem.

Both simple and strongest candidates lie below0.030139, but that is only the
rounded threshold of a2026 announcement. The announced unpublished exact value
might be smaller; **no world-record or novelty claim is established**.

### Resume instructions

Audit source: `experiments/weights/collective_graphon_audit.lean` and companion
Python driver. Repeat with a fresh output directory:

```
PYTHONPATH=src:. python3 -m experiments.weights.collective_graphon_audit \
  --simple reports/literature-simple-graphon-001/graphon-candidate.json \
  --precision reports/literature-two-parameter-001/graphon-candidate.json \
  --out reports/weights-collective-graphon-audit-003
```

The existing driver Lean-checks only the simple candidate. A future bounded
Nat-arithmetic version could independently recount the high-precision candidate;
that extension was considered but **not started** before the user restart.
Do not feed Q65536 into the UInt64 Lean checker: its explicit bound correctly
rejects that input. Other worthwhile work: formalize the graphon realization,
seek the exact2026 witness, and test genuinely different construction families.
