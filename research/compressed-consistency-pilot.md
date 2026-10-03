# Compressed consistency pilot

User authorized testing the broader literature's compressed overlapping
marginal proposal. Use hypothesis-research skill and existing protocol.
One local single-thread job at a time, each<=180s, initial15min pilot and audit.
No agents/paid work/outreach. Hypothesis CC1: a deterministic positive summary
of six-vertex induced graphs can retain coupled PSD/deletion constraints
with substantially fewer states and exclude a saved N5-feasible witness.
This is a small adaptation test, not reproduction of the physics results.

Keep full34-state N5 distribution and all existing N5 PSD blocks. New q is
nonnegative distribution over realizable signatures of six-vertex graphs.
Each signature stores selected compressed4-root Gram coefficient matrices
and specified deletion probabilities. All compatibility maps factor exactly
through the signatures, so any graphon defines feasible p,q. No assumption
of Clebsch structure, regularity, fixed order, or extremality is used.
The objective stays the ordinary sum of red/blue K4 densities.

Dimension audit: retaining all34 N5 deletion probabilities distinguishes
all156 N6 graphs: any deterministic summary that exactly determines this
whole deletion map needs at least156 states. This is not a no-go theorem
for linear/stochastic compression or multiple summaries.
Edge-count deletion alone:102states; edge+triangle150; edge+monoK4 120;
degree-sequence152. Compressed star/triangle-root extension-parity matrices
plus edge deletions use152; adding monoK4 gives154. Both permit an extension
of saved oldN5 witness; numerical minima~0.028046405, no gain over oldN5.

Next bounded adjustment: retain only shared root-type/extension deletion
identities, with degree rather than parity features, and measure the joint
state counts before interpreting any solver result.

## Completed adjustment and exact checks

The joint root-degree summary uses104 upper states (versus156 full graphs),
plus the retained34 lower variables. Each of two root types has5 degree
categories and a5x5 PSD matrix. Its six->five marginal rows are tied to the
same full p5. Objective0.028046405114974866, versus the archived N5 control
0.028046405991469712; no meaningful numerical difference. All optimization
runs reported optimal_inaccurate, so no solver difference is promoted.
The prior full N6+N5 control is0.028750925127350162. These compression tests
are below that existing level, not attempts claiming a new global record.

Independent checker recomputed every compressed matrix by unordered4-root
sets and invariant degree sequences: star(1,1,1,3) and triangle+isolated
(0,2,2,2), six root automorphisms each. It independently covered all1024
labelled5 graphs and recounted6->5 deletion. All integer tensors and map
factorizations matched exactly for all156 six-vertex graphs. This validates
shared overlaps/deletion identities, not just arbitrary free PSD matrices.

The old saved N5-feasible witness has exact rational extensions to ALL THREE
compressed systems. Numerical probabilities were rounded then adjusted by
an exact rational linear solve. Every normalization/deletion/row-sum equality
is exact, every atom strictly positive, and both compressed Gram matrices
passed exact rational LDL with positive pivots. Thus the old witness survives
these tests for mathematical reasons, not merely solver tolerance. This does
not prove equality of relaxation optima; it proves no separation of this
witness. Compressed variables are pseudo-moments, not a constructed graphon.

## Decision and limitations

Retire these three summaries as routes to strengthening the current bound.
They either retain nearly all states (152/154) or lose decisive information
(104). Do not infer that all compressed compatibility methods fail. The next
mechanism would need a summary preserving correlations among attachments to
individual anchor vertices, while sharing more deletion identities, or a
positive non-deterministic compression. Merely adding another isolated PSD
block would repeat the old free-completion failure.

No full renormalization algorithm from the source paper was implemented.
This is its proposed small graph-specific compatibility/closure audit. All
jobs have exited; no background experiments or agents remain active. No
upper witness, published frontier, or strongest local certificate changed.

Files: reports/compressed-consistency-001/{census,screen,result,degree-result,
independent-check,exact-extension-check}.json, exact extension witnesses,
coefficient NPZs and logs; experiments/compressed_consistency/*.py.
Commands: OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 uv run --offline with
numpy/cvxpy for solves, numpy/scipy/sympy for rational extension recovery.
Each solve script has a175s alarm and CLARABEL60s solve limit; all completed
in seconds. No remote compute or dependency network fetch occurred.
