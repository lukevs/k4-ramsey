# Edge-optimality pilot

User authorized next lower-bound tests. First E1: two objective-dependent
edge localizer PSD constraints at six vertices. One local single-thread job
at a time, each<=180s; initial15-minute pilot/check window. No new agents,
remote/paid compute or outreach. Baseline fullN6 plusN5 from prior independently
checked coefficients. Read hypothesis-research protocol and prior reports.

For D(x,y)=red K4 edge derivative minus blue, minimizers obey -WD>=0 and
(1-W)D>=0. For the four possible adjacency patterns of an extra vertex to
roots x,y, let f be their conditional probability vector. Then averages of
-WD ff^T and (1-W)D ff^T are PSD at every global minimizer. Products use
separate derivative vertices and two separate feature vertices (six total);
no duplicated Bernoulli edge factors. Symmetric edge variations justify the
signs, including hard0/1 boundaries. Conditions restrict minimizers, not all
 graphons. Global minimum existence or limiting-variation argument is part of
certificate soundness; exact coefficient checks required before promotion.
Screen both savedN7 moment vectors then solve matchedN6 control/edge pair.

## Results: no resolved improvement in three small tests

Matched N6+N5 control:0.028750924878818446; with edge localizers:
0.02875092476340374. Solver labels both optimal_inaccurate; residuals roughly
1e-11, differences below meaningful precision. Saved N7 solutions already
satisfy edge matrices up to ~5e-11 eigenvalue residual. No separation.

V1: E[(U-R) ff^T]>=0 at minimizers, f=(1-d,d), U=0.030138888.
The independent six-vertex product uses root+3 clique extensions+2 feature
extensions. Control has minimum eigenvalue +5.65e-7. Vertex-only solve:
0.028750925089837558; combined with edges:0.028750924913794114. No resolved
increase. All 156 integer coefficient tensors for both families independently
recounted by subset enumeration; constant graphon controls p=0,1/4,1/2,3/4,1
agree with direct conditional expectations. Existing19 baseline tensors came
from the previously audited N6/N5 experiment. Search-side rational duals are
saved but weaker than prior certificate; not promoted or separately certified.

H1: second variation of vertex measure. For a fixed anchor a, take
h_a(x)=W(x,a)-d(a), which is bounded and mean zero. Both signs of sufficiently
small q=1+t*h_a are admissible. At a global minimum the second derivative is
12 E[H(x,y,z,t) h_a(x) h_a(y)]>=0. Average over a. Expand the centering with
two independent extra vertices b,c. This gives a seven-vertex coefficient
for E[H (W(x,a)-W(b,a))(W(y,a)-W(c,a))]. No repeated edge occurs. Coefficients
computed for1044 graphs; 22 independently checked by all5040 permutations.
Saved control expectation+0.0010739939393321525; stationarity-cut solution
+0.000832202510967769. Both have strict positive slack. No further solve was
justified by this screen. This does not test every possible Hessian direction.

Decision: these low-order edge/vertex restrictions and one averaged curvature
condition do not separate the saved pseudo-moments beyond solver noise.
Retain exact formulas and data; don't repeat these same tests. Broader report
suggests compressed compatible marginals or causal inflation; transfer and
nonredundancy remain untested. No published frontier or upper witness changed.
All experiment processes finished; all literature agents have finished too.

Artifacts: reports/edge-optimality-001/{run.log,vertex.log,screen.json,
independent-coefficients.json,curvature.json,*-result.json}. Source scripts
in experiments/edge_optimality/. Commands used cached uv numpy/scipy/cvxpy/
networkx, OPENBLAS/OMP single-thread, Python175s alarms for both solver jobs.
