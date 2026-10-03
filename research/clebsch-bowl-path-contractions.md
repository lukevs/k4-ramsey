# Clebsch bowl: path contractions and a literature-guided switching pilot

2026-09-29. Main-thread continuation authorized by “Let's do it”. One local
single-threaded compute job at a time, ten-minute subprocess ceilings. User
separately authorized one literature subagent; its completed review is in
`clebsch-formations-literature-2026-09-29.md`. No broader distributed search.

## CB-PATH-002: why the earlier relaxed moments are unrealizable

Let U(x,y) in [0,1] have every row and column integral equal to p, and put
D=U-p. Operators use probability measures, so a finite m-state matrix acts
as D/m, not as the unnormalized matrix D.

**Lemma.** `||D||op <= min(p,1-p)`.

Proof: D kills constants and maps into the mean-zero subspace. On that
subspace it agrees with U and with -(1-U). The nonnegative kernels U and
1-U have constant row and column sums p and 1-p, respectively. The Schur
test bounds their operator norms by those numbers. Decomposing any input
into its constant and mean-zero parts proves the assertion.

This does not bound the entries of D by min(p,1-p): the pointwise box remains
asymmetric. It therefore applies to the true-box family and the Z5 lifts.

Consequently every two-edge path obeys

`||D_ac D_cb||HS^2 <= min(p_ac,1-p_ac)^2 ||D_cb||HS^2`.

The older SDP used the valid but weaker factor p_ac(1-p_ac). Its saved solution
violates the stronger condition in 1,020 of 2,028 inspected inequalities.
A concrete witness, with x=b=48 and c=96:

- edge mean p = 0.7791808266653855;
- requested edge Hilbert–Schmidt norm squared = 0.1720580660683476;
- requested path norm squared = 0.029603978120912377;
- the valid path upper bound is only 0.00838974182348529.

The ratio is 3.52859. The lemma is analytic; the decimal witness identifies a
large violation in the numerical moment vector. This definitively rules out
realizing that saved vector by constant-margin probability kernels. It does
not rule out realizing the newer tightened vector.

Validation: 52 explicit regular and mixed constant-margin kernels of orders
4,5,8,13, including 15 examples attaining the operator bound. Maximum numerical
excess 9.72e-17. Repeated-class C4 nonnegativity was also inspected as a possible
missing restriction, but all 1,014 such moments were already positive: that
would not tighten this solution.

Artifacts: `reports/clebsch-bowl-schur-{1e6,1e7}/`,
`reports/clebsch-bowl-localizer-1e6/schur-obstruction.json`.

## CB-PATH-003: force a common probability space

For a fixed spine xy, write s_z(x,y)=E_z[D_xz D_zy], and collect these paths
into s. Every s_z has mean zero. Also E[D_xy s_z] is exactly its triangle
moment. The previous localizers used s but omitted the constant feature.

Replace s by (1,s), link its moments to the existing triangle variables, and
require the full Gram matrix of (1,D_xy,s,D_xy s). This is a necessary joint
condition, not a realizability theorem. It ties the triangle moments to the
same diamond and path moments rather than allowing their means to drift.

Implemented behind CENTER=1. First numerical run modestly tightens the
allowed gain from 6.4600e-7 to 6.2397e-7, still with the old constant K4
allowance. The solver reported optimal_inaccurate; no certified bound claimed.

## CB-PATH-004: control K4 using the same path moments

For four coarse classes x,y,z,w, let K be the six-edge latent K4 moment.
Let v_ab=p_ab(1-p_ab), M_ab=max(p_ab,1-p_ab), and
q_z=||D_xz D_zy||HS^2. Then

`|K| <= M_xy min(p_zw,1-p_zw)`
`       * sqrt((v_xz v_yz-q_z)(v_xw v_yw-q_w))`.

Proof: for fixed latent x,y, apply D_zw to the functions
a(z)=D_xz D_yz and b(w)=D_xw D_yw. D_zw kills constants, so first subtract
their respective means. Apply its operator norm and then Cauchy–Schwarz
over x,y; bound |D_xy| by M_xy. The average squared norm of a is at most
v_xz v_yz: conditional on z, x and y are independent and both conditional
second moments are bounded by their constant-margin Bernoulli variances.
Subtracting the mean contributes exactly -q_z, with the analogous formula
for w. This includes all centered path variance terms.

Impose this for all six spine choices on every K4 moment class. The square-root
bounds have 2x2 PSD representations. They replace the former independent
absolute K4 allowance with a bound linked to the C4 variables. There are 18
translation classes in this template.

Validation: 288 actual finite-kernel/spine cases, all six spine choices,
including binary and mixed regular kernels. Full six-edge contractions obey
the inequality; the centered localizers agree with PSD weighted feature
matrices up to 1.12e-16. These tests support the implementation of the new
inequalities; they are not an audit of every older SDP modeling choice.

## Numerical results and their limits

At the fixed near-optimal two-parameter B192 means:

| Relaxation | Allowed gain | Objective floor estimate |
|---|---:|---:|
| Original C1 true-box SDP | 1.5451023e-6 | 0.0301374321874 |
| Probability-box localizers | 1.2381804e-6 | 0.0301377391093 |
| Plus sharp operator contraction | 6.4599943e-7 | 0.0301383312902 |
| Plus constant feature and centered K4 path bound | 4.72738e-7 | 0.030138504551 |

The last run decomposes approximately as T3=-3.032e-7, T4=-5.379e-8,
T5=-6.209e-8, T6 allowance=-5.370e-8. The old K4 allowance was -2.049e-7.
The total allowed gain is about 69% smaller than in the original relaxation.

The strongest runs return **optimal_inaccurate**. At scales 1e6 and 1e7 their
objective estimates differ by 5.92e-13, with maximum constraint violations
3.06e-9 and 6.95e-9. This is evidence of numerical stability, not a rational
dual certificate. Do not report these floors as proved bounds.

At the exact coarse means of the checked depth-2 construction, P=0.7791748046875
and H=0.5361785888671875, the strongest estimated floor is 0.0301385043566402.
The existing checked upper construction is 0.030138887566497220. This gives a
numerical, uncertified gap of about 3.83e-7 **for that fixed-mean family**.
It does not give a uniform bound after reoptimizing the means.

Receipts: `reports/clebsch-bowl-centered-1e7/`,
`reports/clebsch-bowl-joint-paths-{1e6,1e7,matched}/`.
Controls and validation scripts: `experiments/clebsch_bowl/`.
The pre-existing `experiments/round5_C1/sdp2.py` gained opt-in LOCALIZE,
SCHUR, CENTER and K4PATH flags; legacy defaults are retained.

## CB-SWITCH-001: a concrete test from the literature review

The Godsil–McKay reflection suggests transformations
`D_uv -> Q_u D_uv Q_v^T`, with Q_u orthogonal and fixing constants.
All individual closed-walk traces telescope, preserving T3 and T4 exactly.
Diamond and K4 terms can change because pointwise multiplication is not
orthogonally invariant. Probability-box feasibility is a separate requirement.

Pilot: on the exact d4763 five-state parent, reflect a subset of size 3,4,5
at exactly one coarse class. Exhaust all 192 coarse classes and all such
subsets: 1,920 size-3 cases, 960 size-4 cases, 192 size-5 cases. All 3,072
fail the [0,1] probability box, checked by integer arithmetic. No candidate
was produced. A subset of size 2 is only a permutation, so was omitted.

Decision: retire this one-class reflection move at this parent. This does
not exclude coordinated reflections at multiple classes, rotations, or
switches in a different latent dimension. Do not infer a general rigidity
theorem from this finite failure.

Artifact: `reports/clebsch-bowl-reflections-001/report.json`.

## Next step

The literature-guided improvement with the clearest connection is to apply
the operator contraction to **whole families of compatible suffix words**:

`[q_ac^2 <X_i,X_j>HS - <D_ac X_i,D_ac X_j>HS]_(i,j) >= 0`.

This is stronger than separate norm inequalities when cross-word moments
are shared. Nontrivial suffix families may require sixth-order moments;
check actual novelty versus existing Gram blocks before enlarging the SDP.
In parallel in the mathematical argument, seek a dual certificate for a
fixed rational pair of means. No matching bottom, improved construction,
global optimum, or novelty claim has been established.

All computation from this continuation finished. The single literature
subagent completed. Distributed search remains paused.
