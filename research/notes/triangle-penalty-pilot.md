# Triangle-penalty proof pilot

User authorized trying to derive a triangle-avoidance structural theorem.
First bounded scope: shared-kernel row-zero lifts of B192, before claiming
anything about arbitrary graphons. Hypothesis-research protocol; local only,
one single-thread process at a time<=180s, initial15min proof/test window.
No new agents, paid work, outreach. Fix rational coarse levels p=32/41,h=22/41
and exact known baseF=1013294255057839/33620705806123008.

Test T1: for fixed latent degree rho, triangles impose a positive cubic
penalty when P amplitude a and H amplitude b have b>0. Derive exact
coefficients and a uniform bound on all higher-degree terms. Need distinguish
asymptotically small amplitude from finite-amplitude/global necessity.
Test T2: can a triangle-containing regular latent beat a triangle-free one
at the same degree after higher terms are included? Small graph census as
adversarial evidence, not an exhaustive theorem for all graphs.

## Outcome: a small-amplitude principle, not a triangle-free necessity theorem

At fixed latent degree, triangles have a positive cubic cost in the shared
kernel model below. At finite amplitude, reduced four-cycle cost can outweigh
it. An exact rational comparison demonstrates this in two ten-vertex graphs.
Neither result improves our incumbent or proves a statement for all graphons.

### Model and exact expansion

Fix the B192 coarse kernel with P=32/41 and H=22/41. Let A be any symmetric
[0,1]-valued latent kernel of constant row integral rho. Set S=A-rho, so S has
zero row integral. Replace each P block by p+aS and each H block by h+bS;
retain hard blocks. All motif densities below are homomorphism densities,
including repeated indices for finite equal-weight kernels.

Writing D for the diamond (K4 minus an edge), the exact change is

    F(lift)-F(base) = C3 t(K3,S) + C4 t(C4,S)
                     + C5 t(D,S) + C6 t(K4,S),

where

    C3 = (59119/3387604992) a²b
    C4 = (27257/165249024) a⁴ + (1843/165249024) a²b²
         + (1/2359296) b⁴
    C5 = -(19/2015232) a⁴b - (3/335872) a³b²
    C6 = (1/98304) a⁴b².

To obtain this identity, expand the six edge factors of each coloured K4.
Any selected perturbation-edge pattern with a degree-one vertex vanishes
when integrating that latent variable, by the zero-row condition. The only
nonempty surviving patterns are a triangle, a four-cycle, a diamond and K4.
Their multiplicities among subsets of the six edges are 4, 3, 6 and 1.
Summing the remaining coarse factors gives the rational coefficients above.
`coefficients.py` performs these finite sums in integer arithmetic before
forming fractions. This is a computer-assisted identity for the specified
coarse base, not a classification of arbitrary candidates.

### Restricted proposition

Take a=epsilon*alpha and b=epsilon*beta, with |alpha|<=1 and 0<beta<=1.
Let tau=t(K3,A). Regularity gives t(K3,S)=tau-rho³. Hence

    F(lift)-F(base) = c alpha² beta epsilon³ (tau-rho³) + R,
    c = 59119/3387604992,
    |R| <= K epsilon⁴,
    K = 813241/3965976576,

for 0<=epsilon<=1 whenever the lift is feasible. For example,
epsilon<=9/41 guarantees feasibility for this entire class.

Proof of the remainder bound: |S|<=1 makes each signed motif density at most
one in absolute value. Bound each monomial in C4,C5,C6 by its absolute
coefficient times epsilon⁴; their sum is K.

If A0 is triangle-free and regular with the same rho, then at the same
amplitudes

    F(lift(A))-F(lift(A0))
      >= c alpha² beta epsilon³ tau - 2K epsilon⁴.

For alpha nonzero, any fixed positive triangle density therefore loses to
A0 at sufficiently small epsilon. Any minimizer in this restricted family,
if a triangle-free comparator exists, satisfies

    tau <= 2K epsilon / (c alpha² beta).

This bound can be weak or vacuous. It shows triangle density tends to zero
in the small-amplitude limit with fixed nonzero alpha and positive beta;
it does NOT force exact triangle-freeness at any fixed positive amplitude.
An additive optimization error eta adds eta/(c alpha² beta epsilon³) to the
bound. The sign restriction on beta matters. The proposition says nothing
about freely optimizing arbitrary coarse structures or independent P/H kernels.

### Exact finite-amplitude reversal

Compare two regular ten-vertex latent graphs, both degree four (rho=2/5),
with a=-3/10 and b=3/10. All probabilities remain in [0,1].
The first is the equal twofold blowup of C5. The second, saved as
`random_10_4_34` in screen.json, has four triangles.

| Latent graph | t(K3,S) | t(C4,S) | Change from coarse base |
|---|---:|---:|---:|
| C5 twofold blowup | -8/125 | 14/625 | +1.8588666253470912e-9 |
| Four-triangle graph | -1/25 | 3/250 | -1.6899693327054822e-9 |

The exact difference (second minus first) is

    -500918933637 / 141150208000000000000 < 0.

The triangle-containing graph sacrifices some cubic benefit but approximately
halves the four-cycle penalty; that tradeoff wins at these fixed amplitudes.
It does not establish superiority over EVERY triangle-free latent graph,
or over triangle-free graphs after separately optimizing their amplitudes.

### Checks, scope, and next useful target

The exploratory census covered 268 regular graphs (not exhaustive).
`exact_check.py` independently enumerates all ordered triples and quadruples
of the two selected latent graphs using Python integers, checks regularity
and feasibility, and substitutes exact rational motif densities into the
coarse expansion. It agrees with the floating-point matrix screen. Receipts
are in `reports/triangle-penalty-001/`. This is not a separate full recount of
the resulting 1920-class matrices; no candidate is promoted.

The useful next theorem would bound the JOINT triangle/four-cycle tradeoff,
including control of diamond and K4 terms, at fixed latent degree. A theorem
that only says fewer triangles is better is too strong at finite amplitude.
All pilot jobs finished. No agents were launched for this pilot.
