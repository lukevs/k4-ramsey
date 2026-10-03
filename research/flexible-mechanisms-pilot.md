# Flexible construction mechanisms

Authorized follow-up: controlled ablations and two-pattern spectral analysis.
Local single-thread jobs <=175 seconds; initial 15-minute pilot, no new agents,
paid compute or external actions. Preserve incumbent. Numerical predictions
are not promoted without independent recount. Use existing coarse expansion
and test its new polynomial encoding against direct latent contractions.

F1: unequal amplitudes vs a=-b; F2: independent diagonal relation on P or H;
F3: relative relabelling of H with individual spectra preserved; F4: compare
these restricted mechanisms with the actual incumbent's sign-split layers.
Run nested comparisons from identical coarse p,h and fixed 16-vertex Clebsch.
Test multiple starts; no claim of global optimization. Check boundary gradients
and Hessian on the active face only. Keep major open extensions explicit.

## Completed: two distinct mechanisms identified

No incumbent improvement or promotion. All jobs finished. Numerical screens
use the previously verified B192 expansion, with all repeated latent indices.
Coarse means fixed at p=.779180833031354,h=.5342651880306992 throughout the
Clebsch comparison. These differ from the earlier rational spectral-floor
pilot; do not attribute the difference between those pilots to flexibility.

### 1. Matched Clebsch ablations

Seven SLSQP starts per family; objective and analytic gradient rescaled.
Nonedge probabilities enforce exact row means; edge/diagonal probabilities
and nonedge probabilities constrained to [0,1], numerical tolerance1e-8.
These are best found points, not certified family minima.

| Freedom | Objective |
|---|---:|
| No refinement | .030138977289665334 |
| Shared pattern, opposite equal strengths | .030138971711946145 |
| Shared pattern, independently chosen strengths | .030138953273345044 |
| Plus separate P diagonal | .030138947822378852 |
| Plus separate H diagonal instead | .030138944682505355 |
| Both diagonals independently adjustable | .030138937353334457 |

Here a latent diagonal is the interaction between vertices assigned the same
latent class, not an ignored self-loop. It affects the graphon objective.
The two diagonal freedoms access more than scalar multiples of A-rho J.
The final four-variable point reproduces the previously saved mixed optimum.

### 2. Spectral explanation and a much simpler recipe

The cubic mixed term is proportional to tr(P²H)/16³ for centered kernels.
Clebsch adjacency has eigenvalues5 (constant vector),1 (multiplicity10),
and -3 (multiplicity5). The centered P/H kernels have these normalized modes:

| Adjacency eigenspace | P | H |
|---|---:|---:|
| 1, dimension10 | -.0697663790704 | -.1068530376061 |
| -3, dimension5 | -.0002861728441 | +.1068530376061 |

99.9991587% of P's squared spectral mass lies in the negative-H eigenspace.
Both matrices commute; their individual spectra AND their alignment matter.
The useful mechanism is suppressing P on the positive-H space, rather than
making all changes stronger. This explains the cubic contribution, while
fourth/fifth/sixth terms remain in every objective calculation.

An enforced exact projector recipe sets H(edge)=H(diagonal)=0 and

    P(nonedge)=2p-e, P(edge)=e, P(diagonal)=5e-4p,
    H(nonedge)=16h/10.

It preserves row means and makes P's adjacency -3 eigenvalue exactly zero.
One-variable optimization gives e=.6396482750821149 and
F=.030138937354123534. It loses only7.89075e-13 against the four-variable
point, retaining99.998024% of that point's gain from the common coarse base.
This is a numerical simplification, not a novelty claim or a global optimum.
It is not a simplification of the full incumbent.

### 3. Alignment tests preserve individual spectra

Compared aligned kernels, a single vertex transposition of H, and six seeded
random permutations of H (identity kept for P). Reoptimized all four scalar
parameters, seven starts each. Relabelling preserves the spectrum at fixed
parameters; optimization subsequently changes the parameters.

Aligned: .030138937353334457.
Single transposition: .030138952810422732.
Random permutations: best .030138967971169342.
All tested misalignments were worse. This supports the alignment explanation;
it does not rule out a specially designed different alignment or graph.
At the aligned optimum the two H variables lie at zero with strictly positive
inward derivatives. The free P face has positive Hessian eigenvalues
3.4510e-7 and2.3235e-6. The unconstrained Hessian has a negative eigenvalue,
but that alone is NOT a feasible descent certificate at this boundary.
No general Hessian of the full incumbent was computed.

### 4. Actual incumbent: signed amplitudes change the quartic story

Read the saved rational sign-split amplitudes from the960-class parent and
its exact first/second-layer receipts. This is a different, more flexible
model: W'((u,s),(v,t))=W(u,v)+st*A(u,v), with free signed A on fractional edges.
It has the exact delta=T3(A)+T4(A). Recomputed first-layer terms match the
saved exact receipt to <1e-20. Second-layer terms are extracted from that
layer's exact receipt, not newly independently recounted.

| Layer | Cubic | Quartic | Net |
|---|---:|---:|---:|
| 1 | -7.1782104552e-9 | -1.1235649842e-9 | -8.3017754394e-9 |
| 2 | -1.3863972726e-8 | +6.1668462981e-9 | -7.6971264283e-9 |

Unlike a single shared kernel's nonnegative tr(S^4), this quartic term is a
weighted sum of products along cycles, with weights depending on the coarse
chords. Signed cycle products can make it negative. Layer1 exploits this;
layer2 does not. Therefore the shared-kernel spectral floor must not be
extended to the incumbent by assuming its quartic contribution is nonnegative.

Ablations of the first layer, optimizing one scalar in [-1,1] after each
change (NOT fully reoptimizing every remaining free edge):

| Amplitude replacement | Gain retained |
|---|---:|
| Original signed magnitudes | 100% |
| Keep signs; use one fraction of each edge's box limit | 1.7936% |
| Keep magnitudes; remove sign pattern, allow global sign reversal | .1696% |
| Depend only on parent edge probability (conditional average) | 14.0354% |
| Common signed fraction of box limit | .0261% |

Original first layer has51.776% of fractional entries on their amplitude box.
Both layers have negative scale derivative at scale1. This is evidence that
box constraints limit their existing directions; it does not prove no other
shape can improve. A larger uniform scale would violate feasibility.
The conditional-average ablation shows that which edges receive amplitudes
matters beyond their parent probabilities; it does not prove that14% is the
maximum obtainable by a fully reoptimized probability-only function.

### Validation and decision

The new monomial evaluator was checked against direct products over all16^4
ordered latent tuples for13 selected candidates, max error2.65e-23.
Analytic gradients agree with central differences; all means/boxes checked.
The Clebsch eigenspaces were checked by direct matrix diagonalization. The
incumbent original delta agrees with existing exact receipt and reproduces
its known value. No full3072-class recount or fresh exact incumbent audit.
Source/input/output hashes in reports/flexible-mechanisms-001/manifest.json.

F1/F2 supported in these matched tests. F3: tested arbitrary misalignment is
harmful; pursue structured spectral filtering instead. F4: actual recursive
gains depend strongly on matching signed magnitudes to individual bridges;
shared-spectrum-only explanations are incomplete.

Next targeted experiment: jointly adjust parent probabilities and signed
refinement amplitudes on edges pinned to their boxes, preserving 0<=W±A<=1.
This tests whether moving the boxes unlocks the negative scale derivative.
Compare to amplitude-only refinement and parent-only adjustment under the
same budget. A second useful extension is a weighted quartic analysis that
keeps chord correlations, rather than replacing it by tr(S^4).
Do not call either route a new bound until an independent checker passes.
