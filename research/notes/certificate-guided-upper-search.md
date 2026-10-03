# Certificate-guided upper-bound pilot

User authorized evaluating lower-certificate slack on the Clebsch construction
and testing whether reducing dominant terms reduces the actual K4 objective.
Local main-thread work only, sequential single-process jobs, <=180 seconds
per compute job, bounded initial diagnostic and direction-test batch. No
distributed campaign, remote compute, paid services, outreach or publication.

H-CU1: the largest nonnegative contributions in our checked N7 lower certificate
suggest useful upper-construction changes. First measure all Gram contributions
AND the residual induced-density slack on the best depth-2 construction. Use
Monte Carlo only for diagnostics, with uncertainty and common random samples.
No sampled value can promote an upper bound. Test suggested coarse changes
on the fully countable B192 control and compare against the unchanged parent.
Any apparent candidate improvement needs a separate full-objective recount.

The decomposition is F(W)-L = sum_b E<C_b(H),Q_b> + E slack(H).
Each expectation is nonnegative; individual sampled Gram contributions need
not be nonnegative. A certificate term is not itself the optimization target.
The sum is exactly the same objective up to a constant, so this provides
diagnostics and alternative search directions, not extra mathematical freedom.

Baseline certificate: toolbox-extension-001/pentagon-independent-v2,
L=36226165105091/1260000000000000. Construction:
round4-E5-depth2-001/graphon-candidate.json, independently structured-exact value
0.030138887566497220. Coarse B192 minimum ~0.030138977289665338.

Status: completed. No processes remain. No improved construction or optimality claim.

## Diagnostic results

Ten million independent seven-vertex samples of the depth-2 construction,
with repeated latent classes allowed and edges conditionally independent,
estimate the four-root P4 block at 0.0004898433 (standard error 0.0000032142).
This is about 35% of F-L = 0.00138796288. The paw and complementary
two-edge-wedge-plus-isolated blocks together contribute about 0.00036870.
The C5-root block is about 2.35e-13; induced-density remainder about 2.21e-10.
These contributions depend on the chosen certificate; they are not raw motif
frequencies or certificate-independent measures of difficulty.

The exporter independently reconstructs every orbit-averaged component from
the integer certificate; its summed numerators match the earlier exact check.
Fair-coin expectations computed over all labelled graphs, an all-blue control,
known full-objective values and the decomposition identity pass. Monte Carlo
is diagnostic, not a construction recount. Forty batches provide standard
errors. The sampling does not resolve the ~1e-8 gains of fine refinements.

## Guided variation and objective control

Sampled conditional edge-flip differences give an unbiased gradient estimate
for the P4 term in a 12-probability coarse Cayley family (four connection types,
each split into same-position, Clebsch-neighbor and other-position cases).
After projecting onto feasible directions and retaining signals >3 SE,
the direction only increases P probabilities and the H diagonal probability.
It leaves all hard 0/1 entries unchanged. It splits the formerly shared P
probability into two separately variable levels.

Six matched/common-random-number tests use steps 0,.001,.005,.02,.05,.1.
At step .02 the P4 term falls by about 4.92e-6 (SE 0.43e-6), while the actual
K4 objective rises by 2.40113163e-6 to 0.030141378421292876. A separate full-root
weighted evaluator agrees at 0.03014137842129305. The smaller nonzero steps
also worsen the actual objective. Other certificate terms compensate for
the targeted reduction; their individual sampled changes have uncertainty.

Actual-objective L-BFGS-B over all 12 probabilities, started at steps .02 and
.1, returns to 0.030138977289665348 in both cases, matching the B192 minimum.
No new basin was found in these two repair runs. They do not rule out larger,
less symmetric changes or guided optimization directly on the depth-2 object.

## Decision and evidence

H-CU1 supplies useful diagnostics but no successful upper-bound move in this
tested family. Do not pursue the largest certificate term as a standalone
objective: here its reduction conflicts with other nonnegative terms.
Next meaningful tests need jointly compatible rooted features or larger
refinements, rather than further movement along this same coarse direction.

Artifacts: `../reports/certificate-guided-001/`, including `best.json`,
`base-P4-gradient.json`, `direction-test.json`, `repair-test.json`, input hashes,
component coefficients, batch estimates and validation. Scripts:
`certificate_guided.py`, `certificate_sample.cpp`; optional component export
added to `check_toolbox_n7.cpp`, preserving the original exact check.

## Connection to the PPSS paper

The user pointed again to [PPSS](https://link.springer.com/article/10.1007/s10208-024-09675-6).
This is our starting construction's paper. Section 4, especially Lemma 4.10
and Proposition 4.11, explains how a tight certificate forces rooted density
vectors into certificate-matrix kernels and can determine optimal weights.
Its matching-bound hypothesis is essential; our current nonzero gap prevents
using those equality conditions to claim optimality of our K4 construction.
