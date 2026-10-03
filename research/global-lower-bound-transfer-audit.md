# Can the Clebsch insights strengthen the universal lower bound?

2026-09-29. Main-thread, bounded analytical audit. No distributed search, new
construction, full flag SDP, or improved universal lower bound.

## What was actually located

- [GLLV, On tripartite common graphs](https://arxiv.org/pdf/2012.02057),
  concluding remarks, reports a nine-vertex flag calculation giving
  C(K4) >= 1/33.77. This audit did not obtain its primal solution or certificate.
  The author's `/pub/common/` page was not retrievable through the web tool.
- [Kiem–Pokutta–Spiegel, section 7](https://arxiv.org/html/2312.08049v1#S7)
  reports numerical CSDP output near 0.02961 at N=9 and explicitly says it was
  not converted to an exact rational bound.
- Their [public certificate directory](https://github.com/FordUniver/kps_trianglemult/tree/main/certificates)
  contains certificates for Theorems 2.3/2.4, Goodman and Cummings et al., plus
  zero-eigenvector files. None is the two-colour K4 calculation. The verifier
  README confirms the different scope. A primal moment vector was not located.
- [Spiegel's 2022 Fields Institute slides](https://christophspiegel.berlin/assets/slides/Toronto_2022.pdf)
  give actual CSDP timings: reduced N=8 about 0.3 hours / 642 MB; N=9 weeks,
  with memory listed as less than 1.5 TB. This is one historical implementation,
  not a lower bound on the resources of every possible implementation.

Consequently we have **not inspected the global optimum's moments**. Finding
violations in our restricted Clebsch relaxation does not establish violations
in the published universal relaxation.

## Result 1: the simplest transferable inequalities are standard flags

Take two independent latent vertices x,y of an arbitrary graphon W. For a
fixed real p define the rooted path feature

    s(x,y) = integral_z (W(x,z)-p)(W(y,z)-p).

Both integral W(x,y) s(x,y)^2 and integral (1-W(x,y)) s(x,y)^2
are nonnegative. Expand s: it is a linear combination of the four possible
adjacency patterns of one extra vertex to the two roots. Squaring uses two
independent extra vertices. The weighting simply specifies whether the root
edge is red or blue. Thus each expression is exactly a quadratic form of
three-vertex flags over a two-vertex type, evaluated on four vertices.

More generally, if the rooted features use at most k vertices including r
roots, their flag product uses at most 2k-r vertices. All unspecified edges
can be summed over to obtain induced flags. A full standard hierarchy at
level nine already includes these quadratic forms whenever 2k-r <= 9
(padding smaller flags if necessary).

This is a mathematical containment statement, not a check of the unpublished
solver input. It rules out claiming this simple family as a new strengthening
of a full N=9 relaxation. It does not rule out additional constraints absent
from a deliberately reduced implementation.

Important qualification: W(x,y)^2 is a repeated-edge *probability* product,
not the indicator of one red edge. It cannot automatically be substituted
by W(x,y) when expanding a fractional graphon. Consequently this argument
does NOT prove that every localizer or centered-kernel constraint in our
Clebsch SDP is a low-order ordinary flag constraint.

## Result 2: the sharp bridge operator bound needs its hypotheses

For a constant-margin bridge U with row and column integrals p, D=U-p has
zero margins. On mean-zero functions its operator norm is at most
min(p,1-p): apply the Schur bound to U and to 1-U. This was useful in the
fixed-skeleton Clebsch calculation.

Replacing the constant margins by the overall edge density is invalid,
even after double-centering to remove all degree variation from the kernel.
Here is an exact counterexample. Let A have measure a and let

    U(x,y) = 1_A(x) 1_A(y),    p = a^2,
    d(x) = a 1_A(x),
    D(x,y) = U(x,y)-d(x)-d(y)+p
           = (1_A(x)-a)(1_A(y)-a).

D has zero row and column integrals. It is rank one, with operator norm
a(1-a). For a=1/4, this is 3/16 whereas min(p,1-p)=1/16. More generally
the ratio is (1-a)/a for small a, so there is no universal constant-factor
repair using only that mean. Double centering changed the pointwise bounds;
it did not manufacture a regular bridge.

This does not refute the original constant-margin theorem. It refutes a
tempting extension needed to use that theorem globally without first proving
regularity or retaining degree information.

For symmetric U, a valid but weaker degree-sensitive substitute is

    ||P U P|| <= min(ess sup d, 1 - ess inf d),

where P projects away constants. Indeed ||U|| <= ess sup d by the Schur
test, and P(1-U)P=-PUP gives the complementary bound. Constant degree
recovers the previous estimate. For bipartite unequal margins the two Schur
factors must be retained separately; this displayed formula is symmetric.

## Result 3: a universal replacement retains degrees, but is elementary

For each x, arbitrary real f, and d(x)=integral U(x,y)dy,

    d(x) integral U(x,y) f(y)^2 dy
      - (integral U(x,y) f(y)dy)^2
    = 1/2 integral U(x,y) U(x,z) (f(y)-f(z))^2 dy dz >= 0.

This exact weighted-variance identity does not assume regularity. Its
small rooted-flag specializations are again ordinary square constraints,
not a demonstrated new ingredient beyond level nine. Higher-order choices
of f could be useful, but must pass a vertex-count/containment audit first.

`experiments/clebsch_bowl/global_transfer_audit.py` checks the counterexample
eigenvector and zero margins in rational arithmetic for a=1/3,1/4,1/8,1/16.
It also checks the displayed variance identity in 420 rooted cases from
120 rational weighted symmetric matrices (sizes 1 through 6), allowing
nonzero diagonals and signed f. Run with Python 3; no dependencies.

## What remains worth pursuing

The most direct next experiment still needs the actual N=9 primal vector,
constraint conventions and numerical residuals. Then test *universal*
candidate inequalities on it, excluding those already in the level-nine
cone. A negative numerical value is a lead, not a new lower-bound proof;
the augmented optimization and a verified dual certificate are still needed.

Our construction can suggest a small set of higher-order rooted patterns.
For example, six-root/eight-vertex flag squares involve ten vertices and
are outside the immediate level-nine containment argument. This alone
does not establish independence or improvement. A sparse extension would
need new moment variables and all necessary consistency relations. It
must allow arbitrary graphs, not force a Clebsch decomposition. This is a
specific candidate design, not an experiment performed here.

Do not run a full N=9 rebuild on this laptop merely to retrieve a vector.
Do not use observed constant degrees of our constructions as a theorem
about every global optimizer. The fixed-Clebsch bowl remains a separate,
more tractable theorem target.

## Corrections to the older lane-L2 discussion

- Increasing bounds at earlier hierarchy levels does not prove that the
  current optimal moment vector is unrealizable. It might be realizable;
  then it would identify a better construction and a tight bound.
- Mixtures of graphon profiles need not themselves be single-graphon
  profiles, but cannot beat the minimum of a linear objective over their
  components. Mixture structure alone is not an explanation for a gap.
- The old assertions about inevitable flag size, universal hardware
  infeasibility and future linear extrapolation were not proved. Treat
  them as unsupported estimates, not impossibility results. Use the actual
  published implementation timings above when discussing practical scope.

Outcome: no new global lower bound. Two plausible transfers have been
classified—one is already standard at low order, one requires assumptions
we cannot impose globally—and the missing artifact is identified precisely.
