# Graph arrangement pilot

User authorized investigating Gewirtz, M22 and Higman–Sims structures, using
mixed relations rather than repeating the old fixed12-block substitution.
Apply hypothesis-research protocol. Initial15-minute local pilot, one
single-thread job at a time, each<=180s. No agents, paid/remote work/outreach.

H-GA1: probabilities on adjacency/nonadjacency/diagonal relations combined
with natural partitions may yield useful asymmetric relation kernels.
Generate Higman–Sims with Sage's documented four25-vertex pentagon/pentagram
groups. Extract M22 as nonneighbors of a vertex and Gewirtz as vertices
nonadjacent to both endpoints of an edge. Verify SRG parameters directly.
Compare plain3-relation controls with mixed relations from ambient group
partitions and an anchor's distance partition. Equal-mass graphons, including
all repeated indices and diagonal probabilities. This changes bridge rules
rather than substituting a graph into the fixed12-block B192 recipe.

Use existing frozen relation_engine_v2's exact ordered-tuple signature census
and bounded projected descent. Multiple starts, tiny controls, independent
recount of the best candidate. Numerical minima do not prove optimality;
negative screens only describe these finite parameterizations. These first
kernels have56/77/100 classes, not the3840-class incumbent. A poor direct
kernel does not rule out using its relations inside a larger construction.

## Completed results

All three graphs generated locally and directly checked: SRG(100,22,0,6),
SRG(77,16,0,4), SRG(56,10,0,2). No symmetry shortcut was assumed in the
latent census; every ordered4-tuple including repeats was counted. Higman–
Sims ambient labels document its four25-vertex pentagon/pentagram groups;
induced M22/Gewirtz retain their intersections with those groups.

### Direct small graphons

18 native projected-gradient runs: three graphs, three relation partitions
(plain3 relations; ambient23/24; anchor10), two starts. Then45 L-BFGS-B runs
(5 starts per graph/partition) using exported exact signature polynomials.
None beat1/32; best converged plain values were within~1e-14 above1/32.
Some richer runs hit450 iterations, so no claim of family minima. These are
negative screens, not proofs. An initial summary-key error occurred AFTER
a successful native run; preserved error log, reused its completed report.

### Latent use inside B192 fractional bridges

Retained B192 coarse mean levels p=.779180833031354, h=.5342651880306992;
base F=.030138977289665334 (floating). No hard0/1 coarse entry changed.
For each regular graph A on m vertices, S=A-(k/m)J has zero row means.
First tested D_P=a*S and D_H=b*S with exact box-derived amplitude ranges,
nine starts each. All three yield small numerical improvements of the base.

Then allowed distinct latent diagonal/edge/nonedge probabilities on P andH.
These have four free parameters; each nonedge probability is fixed by the
original coarse mean. Seven SLSQP starts per graph, objective rescaled1e8;
all reported best points feasible to floating tolerance. Latent types retain
all mixed triangle/C4/diamond/K4 contributions, not merely individual spectra.

| Latent | Classes of resulting graphon | Shared-kernel F | Mixed P/H F |
|---|---:|---:|---:|
| Higman–Sims |19200|.03013895898422188|.03013895500468096|
| M22 |14784|.03013896293718077|.03013895764899261|
| Gewirtz |10752|.03013896992392562|.03013896265320394|
| Clebsch control |3072|.03013895327334504|.03013893735333446|

None beats incumbent .030138887566497220. This does NOT improve our upper
bound. All table entries are numerical expansion predictions, not promoted
exact witnesses. These are graphon class counts, not finite injective counts.

Best Higman–Sims mixed probabilities (nonedge,edge,diagonal):
P=(.911882597889,.304687421166,1); H=(.408136607832,1,0).
Optimum lies on probability walls; the SLSQP numbers are not a global proof.
Its terms: T3=-4.59483712e-8, T4=+2.35786000e-8, T5=+1.50639504e-10,
T6=-6.58526979e-11. M22 and Gewirtz show the same triangle-gain/C4-cost
competition. These are SIGNED perturbation moments, not a claim of globally
eliminating monochromatic triangles. For the common centered triangle-free
regular kernel S, t(K3,S)=-(k/m)^3 follows from tr(A^3)=0 and regularity.
Triangle-freeness therefore has a precise role here, but says nothing alone
about the necessary fourth and higher moments or global optimality.

## Validation and limits

Frozen relation-engine regression passed (tiny exact objective/gradient/
Hessian, repeats, complement, boundaries). SRG parameters checked independently
of Sage metadata. Common and mixed lift expansions validated against separate
materialized576-class floating recounts; mixed error2.43e-17. Best standalone
rounded100-class matrix recounted using all roots; difference<1e-16. Every
latent ordered tuple mass and all six one-edge marginal counts checked exactly.
Large10752–19200-class candidate matrices were not materialized or directly
exact-recounted; no promotion attempted because predictions are worse than
incumbent. Exported6-edge histograms have98 nonempty positional patterns in
each of the three graphs. The floating expansion uses the previously tested
row-zero leaf-cancellation identity. No claim of novelty or optimality.

Decision: these SRGs are useful controls and viable small-gain latent kernels,
but do not justify replacing Clebsch. Stronger future test would vary HOW
multiple relations align between coarse bridges, rather than only three
scalar probabilities per graph. Do not repeat plain rank3 substitution or
these same centered-kernel families as new directions.

All processes finished. Local single-threaded host calculations; Sage only
for graph data. Native child limit170s, scipy jobs175s alarms, fixed seeds930;
all runs completed within limits. Sources/scripts and immutable result hashes
in reports/graph-arrangements-001/manifest.json; logs and summaries alongside.
