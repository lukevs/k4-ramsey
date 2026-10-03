# Lane B handoff: two proved obstructions, no improved c4 bound

Final initial-window handoff, 2026-09-30 04:13 UTC. All compute finished; no live jobs.

**Strongest result:** an explicit rational seven-class graphon defeats EVERY convex combination of the rooted K4 objective and the same-/cross-colour conservative one-step neighbourhood transports at the existing certified N6 threshold 0.028750881. At a class of mass 1/10000 the three values are approximately 0.01978623, 0.02826053, and 0.02815040. Fraction enumeration and an independent integer checker agree exactly. This is a counterexample to that universal POINTWISE proof family, not to the global bound; this graphon's c4 is 0.03662471.

**Second result:** the common-prefix contraction matrix for suffix functions (1,d) has an explicit N5 flag-square representation. Its apparent coupled operator inequality is redundant already at N5. Exact checks on 25 graphons and the existing rational N5 witness agree.

Decision: retire these two precisely scoped low-order routes. More general higher-order coupled constraints, degree-dependent transports, and arguments conditional on near-optimality remain open. Primary artifacts: `reports/lower-frontier-B-006/exact-counterexample.json`, `reports/lower-frontier-B-006/independent-integer-audit.json`, and `reports/lower-frontier-B-001/contraction.json`. Detailed derivations, chronological hypotheses, failed tests, and sources follow.

## Initial contract and journal

Contract: initial handoff by 2026-09-30 04:16 UTC; local host only, one single-thread job at a time, each <=180 seconds. No Sage, remote compute, shared source edits, commits, outreach, or subagents. Only this note and lane-B experiment/report directories are writable task outputs.

Question: derive a universally valid constraint on arbitrary symmetric [0,1] graphons, correctly normalized, and distinguish a useful strengthening from standard-flag redundancy. Source: Local flag algebras https://arxiv.org/html/2607.12461v1, especially §5.1 and §7. Prior six-root free completion, C5/P5 failures, and edge-square containment have been read.

Registry:
- B1: common-prefix contraction for the universally double-centered kernel PWP; investigate degree-free operator bound 1/2 and compatible path moments. Proposed; exact small-example checks and vertex-order/redundancy audit next.
- B2: conservative neighborhood transport of rooted monochromatic K4 density, replacing the source's regularity-dependent averaging identity by a universally zero-integral divergence. Proposed; seek either a useful scalar inequality or explicit obstruction from exceptional neighborhoods.

No improved c4 lower bound is claimed. Process state: no compute launched yet.

04:06 UTC interim: B1 contraction matrix for features (1,d) passes 25 exact rational graphons and does NOT exclude the saved exact N5 witness. More decisively it has an explicit five-vertex flag-square representation: sample three roots x,y,z and their Bernoulli edge colours, and square `(e_xy-1/2) f(y)-(e_xz-1/2) f(z)` for f=alpha+beta*d. Half its expectation is the contraction slack. Therefore full N5 already implies it. This is a proved containment obstruction for common-prefix contraction, beyond an isolated diagonal test.

B2 refinement: use colour-specific conservative transport. Same-colour transport has infimum zero at an exceptional isolated root in an almost-red clique. Cross-colour transport instead gives the universal nonnegative local functional
`g(x)=d(x) fR(x)+(1-d(x)) fB(x)+integral[W(x,y) fB(y)+(1-W(x,y))fR(y)]dy`,
where fR,fB are rooted K4 probabilities. Its integral is exactly c4 by symmetry. Test whether an anomalous rooted neighborhood in a small step graphon can push g below the existing global lower bound, obstructing a uniformly positive pointwise improvement strategy.

## Proved result B1: a universal operator bound, but a containment obstruction

Let W be any symmetric measurable [0,1] kernel on a probability space. All integrals use that probability measure. Let d=W1, p=integral d, P=I-J, where J projects onto constants, and D=PWP. Then

    ||D||op <= 1/2.

Indeed D=P(W-1/2)P and the Hilbert–Schmidt norm of W-1/2 is at most 1/2. Balanced complete bipartite W attains equality. This requires no regularity; it repairs the failed global `min(p,1-p)` transfer only with a weaker constant. It is an elementary derivation, with no novelty claim.

For S=W-1/2 and any common family of functions f_i, the matrix

    A_ij = (1/4) integral f_i(y) f_j(y)dy
           - integral (S f_i)(x) (S f_j)(x)dx

is PSD. This couples all suffixes, not just their diagonal norms. For f=(1,d), write s2=t(P3,W), u=t(P4,W), v=t(P5,W), with Pk denoting a path on k vertices. Its explicit matrix is

    A00 = p-s2,
    A01 = (s2+p^2)/2-u,
    A11 = s2/4-v+p*s2-p^2/4.

For moment relaxations each product is a DISJOINT UNION graph density: p^2 means t(2K2), and p*s2 means t(K2 disjoint-union P3). Never substitute products of expected densities for these linear moment coordinates.

**Exact containment proof.** Sample three latent roots x,y,z and their random induced graph edges e_xy,e_xz,e_yz. For f=alpha+beta*d, define

    H = (e_xy-1/2) f(y) - (e_xz-1/2) f(z).

Since (e-1/2)^2=1/4 and the two different edges are conditionally independent,

    E[H^2]/2 = (alpha,beta) A (alpha,beta)^T.

Conditionally on the three roots and their induced type, H is the expectation of a linear combination of one-extra-vertex flags: replace d(y),d(z) by W(y,v),W(z,v) and average v. Its square uses two independent extra vertices, hence FIVE vertices total. Summing the eight labelled three-root types gives an ordinary full-N5 flag certificate. Thus this entire common-prefix degree-path family is already implied at N5, and a fortiori cannot strengthen full N9. The claim concerns this explicit specialization, not every higher-order operator inequality.

**Exact tests.** `reports/lower-frontier-B-001/contraction.json` records 24 binary weighted two-class kernels (including loops and unequal weights), one fractional irregular three-class kernel, and the saved exact N5 feasible witness. The literal homomorphism sums match the operator calculation exactly. All 25 matrices are PSD. On the old witness, A is approximately [[0.2462463,0.1231231],[0.1231231,0.0624055]], with strictly positive rational determinant

    29925206897786840226443 / 144000000000000000000000000.

It does NOT exclude that witness. The analytic containment proof, rather than this one successful test, establishes redundancy.

## B2: conservative transport and an exact obstruction

Define the rooted monochromatic clique densities

    fR(x)=integral W(x,y)W(x,z)W(x,t)W(y,z)W(y,t)W(z,t) dy dz dt,
    fB(x)=the same expression with W replaced by 1-W,
    F(x)=fR(x)+fB(x).

Then integral F=c4(W). Define L_W h(x)=integral W(x,y)(h(y)-h(x))dy. Symmetry gives integral L_W h=0 without any degree assumption. Two natural nonnegative one-step transfers are

    g_same = F + L_W fR + L_(1-W) fB
           = (1-d)fR+d fB + integral[W fR+(1-W)fB],
    g_cross = F + L_W fB + L_(1-W) fR
            = d fR+(1-d)fB + integral[W fB+(1-W)fR].

Both have integral exactly c4(W). Therefore a universal pointwise g>=L would imply a universal c4 lower bound. This is a legitimate transfer of overlapping-neighborhood compatibility, while retaining variable degrees. It imports NONE of the paper's triangle-free or maximum-degree conclusions.

**Same-colour obstruction, analytic.** Take a class A of measure epsilon with all incident red probabilities zero, and a red clique on the remaining class B. At x in A,

    g_same(x)=4 epsilon^3-3 epsilon^4 -> 0.

Thus no positive constant is a universal pointwise lower bound for g_same. This does not contradict the global objective, which tends to one.

**Cross-colour obstruction, exact positive-mass example.** A four-class base has weights (34,31,16,19)/100 and red matrix

    [54 68 16 24]
    [68 43  9 77] / 100.
    [16  9 100 100]
    [24 77 100 30]

Scale those masses by 999/1000 and append class E of mass 1/1000. Its red probabilities to the four classes are (1,0,1,0), and its internal red probability is 1/2. At every x in E, exact ordered-tuple enumeration gives

    g_cross(x) = 2916055474077888400572688602449 / 10^32
               = 0.029160554740778884...,
    g_same(x)  = 0.028884593580247024...,
    F(x)       = 0.022736327933675686... .

All three are below 0.0296. Consequently EVERY convex combination of F, g_same, and g_cross fails the universal pointwise 0.0296 bound on this one graphon. This includes all nonnegative mixing coefficients alpha,beta with alpha+beta<=1 in `F+alpha(L_W fR+L_blue fB)+beta(L_W fB+L_blue fR)`.

This is an obstruction to that precise pointwise proof route, NOT a counterexample to the global bound: this graphon's c4 is approximately 0.03530882038735022. The exceptional roots have positive mass; the argument does not rely on a measure-zero root.

`experiments/lower_frontier_B/check_transport.py` uses a separate exact implementation enumerating all ordered four-tuples with rational masses and six edge factors, including repeated class indices and nonzero diagonals. It verifies both transport averages equal the global objective exactly. `reports/lower-frontier-B-003/exact-counterexample.json` contains every matrix entry, rational density, source hash, and runtime.

## Normalization and scope

For a finite symmetric weighted matrix W with class weights w summing to one, all integrals above mean sums weighted by the corresponding w_i. Operators act as `W diag(w)` in coordinates (or its symmetric square-root-weight conjugate), never as unnormalized adjacency matrices. For n equal-mass classes this is W/n. Homomorphism densities sample indices independently with replacement. They are exact for these finite step graphons. These are not asserted as exact injective finite-n K4 inequalities; the usual collision difference is O(1/n) for a fixed motif.

## Sources and decision so far

Primary mechanism: [Local flag algebras, §5.1](https://arxiv.org/html/2607.12461v1#S5.SS1) couples counts at a vertex and its neighbours; its displayed averaging simplification uses regularity. Section 7 uses compatible overlapping neighbourhoods together with triangle-freeness and maximum degree. Our divergence identity replaces the regularity-dependent average, and the explicit counterexamples show why a bare one-step pointwise transplant is insufficient.

Prior local files read: global-anchor-pilot, global-coupled-pilot, global-overlap-pairs-pilot, toolbox-clebsch-extension, clebsch-bowl-path-contractions, clebsch-formations-literature-2026-09-29, and global-lower-bound-transfer-audit. The present operator result does not repeat the invalid mean-based norm bound or the isolated six-root completion.

Decision: retire B1 at these low orders by a proof of containment. Retire the B2 convex one-step pointwise family as a route to beating 0.0296, by an exact counterexample. Neither result retires higher-order shared moment constraints, multiple-step transport, nonlinear degree-dependent coefficients, or coupled inequalities that use average information rather than a uniform pointwise lower bound. No universal lower bound has improved and no new upper construction has been found.

## Stronger final counterexample: below the checked N6 bound

The nonsmooth minimax screen with eight bulk classes stalled at 0.0288723. Replacing that objective with an explicit SLSQP epigraph continued to about 0.0281638. It reached its iteration limit, so no optimizer/optimum claim is made. Its only role was to propose an object. Two almost-duplicate classes were then merged, a tiny redundant class removed, and all entries rounded to simple rational numbers. The resulting exact six-class bulk is:

    weights = (19,15,15,18,15,18)/100,
    W = [79  13 100  27  13  27]
        [13 100  13 100   7  18]
        [100 13  32  71  13  71] / 100.
        [27 100  71  40  18  73]
        [13   7  13  18 100 100]
        [27  18  71  73 100  40]

Scale those six masses by 9999/10000. Add E of mass 1/10000 with red probabilities (1,1,0,0,1,0) to the bulk classes and internal red probability 1/2. The resulting seven-class graphon has, at every x in E,

    F(x)       = 0.019786225004475393...,
    g_same(x)  = 0.028260533335198301...,
    g_cross(x) = 0.028150401872146666... .

The maximum is exactly

    28260533335198301186947426594972829 / 10^36,

strictly below 28750881/10^9, with exact margin

    490347664801698813052573405027171 / 10^36.

Thus the ENTIRE convex family cannot even certify the already checked N6 threshold by a universal pointwise bound. The global c4(W)=0.03662471020286957... is deliberately not competitive. This example does not refute a pointwise assertion restricted to near-optimal graphons; that would need a separately proved structural hypothesis. It also does not rule out using non-pointwise average constraints, signed/degree-dependent transport coefficients, longer paths, or additional local features.

Verification layers:
- Numerical search: `search_transport.py`, `refine_transport.py`, `epigraph_transport.py`; reports 002,004,005. L-BFGS and SLSQP termination limitations are preserved. No lower bound, optimum, or nonexistence follows from these numerical runs.
- Exact graphon evaluation: `check_transport_stronger.py` enumerates all ordered four-tuples with Fraction arithmetic; report 006. It verifies both transport averages equal global c4 exactly.
- Independent exact artifact check: `audit_integer.py` imports neither the search nor the Fraction checker. It builds an integer triangle tensor, then attaches each root. Every rooted density and both transported densities match the artifact exactly; both global averaging identities are checked as integer identities. Report `006/independent-integer-audit.json` records hashes and the exact separation margin.
- Mathematical conclusions: the flag containment proof and conservative-transport identities above are analytic proofs. The explicit rational counterexample is computer-assisted exact arithmetic with an independently implemented checker. Nothing here is a formal Lean/kernel proof or an improved universal multiplicity bound.

## Commands, resource receipts, and final process state

All Python subprocesses were bounded by an outer `subprocess.run(..., timeout=150 or 170, check=True)`, strictly below the 180-second ceiling. Exactly one compute subprocess ran at a time. Numerical commands used cached packages only:

    uv run --offline --with numpy --with scipy python experiments/lower_frontier_B/search_transport.py
    uv run --offline --with numpy --with scipy python experiments/lower_frontier_B/refine_transport.py
    uv run --offline --with numpy --with scipy python experiments/lower_frontier_B/epigraph_transport.py

OMP_NUM_THREADS, OPENBLAS_NUM_THREADS, MKL_NUM_THREADS and VECLIB_MAXIMUM_THREADS were all 1. Numerical jobs took about 1.3, 2.2 and 2.1 seconds, respectively. Standard-library exact jobs each took less than 0.1 seconds:

    python3 experiments/lower_frontier_B/check_contraction.py
    python3 experiments/lower_frontier_B/check_transport.py
    python3 experiments/lower_frontier_B/check_transport_stronger.py
    python3 experiments/lower_frontier_B/audit_integer.py

Source hashes, input hashes where applicable, Python/platform or package versions, deterministic seeds, actual timings, solver termination flags, full rational artifacts and objective values are in the JSON receipts. No N9 enumeration, SDP, Sage, package installation, paid/remote compute, outreach, commits, shared source edits, or subagents were used. All three returned shell sessions (60133,12035,85572) completed and were reaped. No process remains active; no continued campaign is implied. Initial handoff complete before 04:16 UTC.

Next discriminating direction, if later authorized: conditional-on-near-optimality transport constraints require a structural lemma excluding these anomalous rooted neighbourhoods, or a shared moment relaxation that pays for their frequency. Simply requiring a stronger universal pointwise bound on these three functionals is disproved.
