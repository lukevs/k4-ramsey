# Spectral bowl pilot

Authorized bounded local follow-up: derive a lower floor for shared-kernel
B192 refinements, not universal c4. Reuse exact p=32/41,h=22/41 expansion.
One single-thread job at a time, <=180 seconds each; initial 15-minute pilot.
No agents, external compute, commits or publishing.

S1: spectral Cauchy-Schwarz t3²<=t2*t4 forces a quantitative cost for cubic
improvement. Test against the 268 saved regular latent graphs and exact pair.
S2: bound the diamond and K4 remainders rigorously so this is a bound on the
whole restricted objective, not its truncation. Compare floor to constructions.
S3: test whether spectral moments alone distinguish strongly regular graphs;
identify equality obstructions rather than claiming a sharp optimum.

## Result: analytic floor and exclusion for a restricted ray

Let A be a symmetric [0,1] kernel of constant degree rho; S=A-rho.
Use probability-measure normalization throughout. Let v=t(K2,S²) mean
integral S(x,y)² dxdy (NOT the usual graph homomorphism notation for K2).
Write x=t(K3,S), y=t(C4,S), d=t(diamond,S), z=t(K4,S).
For clarity, v is simply the squared Hilbert–Schmidt norm of S.
Put V=rho(1-rho), m=max(rho,1-rho). Then

    0<=v<=V,  x²<=v*y<=V*y,  0<=y<=v²<=V²,
    |d|<=m*y,  |z|<=m²*v²<=m²*V².

Proof: the eigenvalues of the integral operator S satisfy
x=sum lambda³, y=sum lambda⁴, v=sum lambda². Cauchy–Schwarz gives
x²<=v*y. The variance bound follows from A²<=A and integral A=rho.
The diamond density is integral S(x,y)*(S²_operator(x,y))², giving its bound.
For K4, take absolute values and bound a pair of opposite edges by m².
The remaining four edges form a C4 in the entrywise-absolute kernel |S|.
Its fourth spectral moment is at most its squared second moment, namely v².
These arguments also work for arbitrary latent size and for measurable kernels.

For coefficients Cj in the exact coarse expansion, C3>=0 and C6>=0, define
B=C4-|C5|m. Whenever B>0,

    F-Fbase >= C3*x + B*x²/V - C6*m²*V².

Regularity also gives x>=-rho³. Minimizing the quadratic over that half-line
provides the fixed-amplitude floor. Endpoints rho=0,1 have S=0 and are handled
separately. No division by zero is used.

At a=-0.3,b=0.3 and rho=5/16:

    floor = 0.030138985786690442 (exact rational in check.json)
    Clebsch latent value = 0.030138988800000786 (numerical)

The gap is approximately 3.01e-9. This is not a proof of Clebsch optimality.

## Covering the whole equal-and-opposite amplitude ray

Write a=-e,b=e with 0<=e<=U. Let Cj=kj*e^j, using the signed k5 and
positive k3,k4,k6 from the coarse expansion. Explicitly:

    k3 = 59119/3387604992
    k4 = 27257/165249024 + 1843/165249024 + 1/2359296
    k5 = -19/2015232 + 3/335872
    k6 = 1/98304.

Choose the range that guarantees feasibility for EVERY A in [0,1]:

    U=min(p/(1-rho), (1-p)/rho, h/rho, (1-h)/(1-rho)),
    p=32/41, h=22/41.

Completing the square, and dropping the extra x>=-rho³ restriction, gives

    F >= Fbase - k3²*V*U²/[4*(k4-|k5|*m*U)]
               - k6*U^6*m²*V²,

provided k4-|k5|mU>0. To see why this covers every e, apply the same bound
with e in place of U. Both subtracted expressions are increasing on [0,U].
At e=0 the objective is exactly Fbase, so no limiting division issue arises.
This closed form is stronger than the separately computed rational interval
certificate in ray.json and requires no numerical optimization.

| rho | U | Analytic floor for all latent kernels on this ray |
|---|---|---|
| 5/16 (Clebsch degree density) | 304/451 | 0.030138931158062644 |
| 2/5 | 45/82 | 0.03013895716716552 |

Exact fractions are in closed-form.json. Both floors exceed our incumbent
0.030138887566497220. Thus neither specified family can improve the incumbent,
regardless of latent size. This is a restricted impossibility result, NOT a
universal c4 lower bound, nor an optimality proof for our incumbent.

The restriction matters: fixed coarse p,h; one shared centered regular kernel;
a=-e,b=e; fixed rho; e in the uniform feasible range above. Some kernels whose
entries avoid 0 and 1 admit larger e; those extensions are not covered. Unequal
P/H amplitudes, different kernels, coarse level changes and recursive lifts
are also outside this exclusion.

## Checks and interpretation

S1 supported: the triangle/four-cycle tradeoff follows directly from spectral
Cauchy–Schwarz. S2 supported: diamond and K4 were bounded, not omitted.
S3 unresolved: these moment inequalities do not characterize the best graph.
Equality in spectral Cauchy–Schwarz would require all nonzero eigenvalues to
have the same value; the relaxed floor need not be realizable.

Checked inequalities against all 268 saved regular-graph records; two selected
graphs also pass exact rational motif checks from independent ordered-tuple
enumeration. A 4000-interval rational certificate covers each amplitude range;
a separate analytic completing-square calculation gives the stronger closed
form. Computation took under one second. These are ordinary mathematical
proofs conditional on the existing computer-assisted coarse expansion, not
Lean proofs or independent full lifted-matrix recounts. No bound promotion.

Next useful extension: allow independent amplitudes a,b and investigate the
remaining moment slack. Do not spend a new size search on the excluded ray.
All jobs finished; no agents launched. Novelty is unestablished: the spectral
and norm inequalities used here are standard.
