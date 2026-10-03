# Algebraic / spectral switching round

Contract: K4 Ramsey multiplicity, unit-weight blue-diagonal finite templates;
objective includes repeated indices. Deadline 2026-09-27 20:03:30 UTC, at most
two CPU jobs owned by this round (four total). No paid/remote jobs or contacts.

H-ALG-001, proposed independently before reading favored local approaches:
Seidel switching by algebraic/spectral cuts changes a macroscopic correlated
set of edges while preserving the Seidel spectrum. Prediction: at least one
structured cut of the published seed improves its exact numerator. Disconfirm
for the tested cut bank if all exact recounts increase the numerator. This is
not a prediction that the entire switching orbit or all graphs are exhausted.

For bits c_i, use A'_ij = A_ij XOR c_i XOR c_j. The diagonal remains blue,
the operation is an involution, complementary cuts agree, and off-diagonal
Seidel matrices satisfy S'=DSD with D_ii=(-1)^c_i. Spectral information only
proposes cuts; the native exact objective recount certifies search values.

The primary paper https://arxiv.org/html/2206.04036v3 describes the published
construction over Z3 x Z2^8. Simple mixed-radix vertex-index interpretations
do not match the archived adjacency labeling, so this first screen uses
label-independent spectral and neighborhood cuts rather than falsely claiming
the index bits are group characters. Deflated power iteration generates large
absolute-eigenvalue directions; seven quantile cuts per direction and pairwise
XORs of median cuts are screened against random-cut controls. Novelty is
unestablished; the elementary switching identity is standard.

Validation: random tiny symmetric graphs, repeated-index ordered-quadruple
oracle, switching involution, complementary-cut equivalence, and entrywise
Seidel conjugation. The existing snapshot runner independently recounts any
retained output using compiled Lean; this is not a kernel-only theorem.

## H-ALG-001 result: retire the coarse Seidel cut bank

`reports/pilot-algebraic-switch-001`: 96 unique cuts, 22.14 seconds. All worsen
the seed; best nontrivial delta +722737216. Neighborhood cuts give +1345719562,
random controls +726186448 through +778465872. Output remains the published
seed, independently compiled-Lean checked. This is a negative for the selected
cut bank, not the complete switching orbit. Peer review found no mathematical
issue; range validation and conservative timeout labels were tightened after
the immutable run. No timeout occurred in that run.

## H-ALG-002 result: no size-four Godsil–McKay cells in the seed

Use [Godsil and McKay's construction 2.1 and theorem 2.2](https://users.cecs.anu.edu.au/~bdm/papers/GodsilMcKayCospectral.pdf).
A four-vertex cell C must induce a regular graph of degree d, and every outside
vertex has 0,2,4 neighbors in C. Set B=A+(d mod 2)I over F2. Then B1_C=0.
By symmetry the four corresponding rows XOR to zero, so two disjoint pairs
have equal row XOR. Searching both diagonal parities covers all d=0,1,2,3;
explicit regularity checks remove any spurious parity solutions.

`reports/pilot-algebraic-gm4-001`: all 294528 pair XORs are distinct for each
parity. Consequently there are no such four-vertex cells in the published seed.
Runtime 0.20s. Explicit subset enumeration on every graph of order <=5 validates
the implementation; independent review agreed the completeness argument.
This is an exact Python combinatorial audit, not a Lean theorem. Enumeration
can grow very large on unrelated row-twin inputs. Degree preservation follows
for this regular seed; it is not automatic for arbitrary nonregular inputs.
Decision: retire GM4 on this fixed graph, not an unsupported larger-cell sweep.

## H-ALG-003: global four-sheet lift assignments

Structural observation: adjacency-row Hamming distance <=26 partitions all
768 vertices into 192 independent four-vertex fibers. Every inter-fiber block
is biregular. There are 8736 zero blocks, 8448 complete blocks, 1056 blocks of
the form J minus a permutation matrix, and 96 degree-two blocks consisting of
two K2,2 components. Every vertex has red degree387. Arbitrary reassignment
of each missing matching therefore preserves all degrees and the quotient.

The missing-matching quotient is three triangle-free 11-regular components of
order64. A spanning-tree gauge changes all voltages to Klein-four permutations;
the exact archived decomposition is in `reports/pilot-algebraic-lift-001/quotient.json`.
This is a discovered representation of the existing published construction,
not a novelty claim about graph lifts or the seed itself.

Prediction: global voltage changes improve the seed without the large degree
disturbance seen in Seidel switching. The first fixed bank includes every
nonidentity global left twist, every constant voltage, and matched-probability
random S4/V4 assignments. Two arbitrary fiber-gauge relabelings serve as exact
no-change controls. Tiny materialization, inverse gauge, degrees, and ordered
quadruple tests pass. The first test fixture incorrectly expected degree8
instead of6 in a three-fiber J−P graph; that expectation was corrected before
running experiments.

`reports/pilot-algebraic-lift-001`: 71 unique assignments in12.38s. Every one
of23 nonidentity global twists improves the seed (delta -69600..-30240), and
all24 randomized assignments improve it. The best random S4 lift changes1023
matching blocks and has exact numerator **10487028480**, a decrease136704.
The snapshot runner independently checks that witness with compiled Lean.
It is still worse than the edge-refined incumbent, so this is a distinct seed
basin and structural mechanism, not the best current bound.

Next discriminating test: expand the degree-two fiber blocks from the original
two-K2,2 pattern to all90 regular4×4 binary matrices (18 two-K2,2;72 C8). Use a
matched factorial design: change matching voltages only, half blocks only,
or both, with common random draws. This tests a genuinely additional set of
constraints while preserving every degree and the fixed quotient. Coordinate
with the reviewer on a matched local-polish test of the new structural basin.

## H-ALG-004: matched polish and block-constraint interactions

Phase2 (`reports/pilot-algebraic-lift-002`) evaluates54 assignments in9.77s.
Half-block randomization alone worsens the raw numerator by63648..78912.
With independently randomized matching voltages, C8 and unrestricted regular
half-blocks improve the raw score somewhat; best raw N=10487021880.

The first polish orchestrator attempt (`pilot-algebraic-polish-bank-001`) fails
before dispatch because JSON converts tuple patterns to lists. The failure,
partial inputs, and source snapshot remain; tuple normalization and a regression
test fix the interface. `pilot-algebraic-polish-bank-002` then compares twelve
predeclared group representatives with identical cached-star parameters:
mode=star, per_color=16, max_moves=100000, checkpoint_moves=100, seed21,
30s search/45s timeout. Each child has its own source snapshot, independent
baseline recount, candidate and Lean recount. At most two jobs run concurrently.

Best polished N=10486305592, a gap39224 above McKay, comes from a voltage-only
seed, not the lowest raw numerator. All half-only cases remain much weaker.
Thus the quotient's degree-three permutation freedom predicts a better basin;
the added degree-two shape freedom alone does not. These selected representatives
are an exploratory comparison, not a broad stochastic superiority estimate.

## H-ALG-005: an exact triangle constraint, and a falsified optimization intuition

The96 degree-two blocks form a perfect matching H on the192 fibers. Gauge each
two-K2,2 blue block to equality of the first sheet-bit. The degree-three defect
graph D is triangle-free. Every one of960 triangles of D union H has two D
edges and one H edge. Restrict missing-matchings to permutations preserving or
flipping the first sheet-bit. A triangle's blue transversal count is4 if the
first-bit flips of its two D edges agree, and0 if they differ.

The resulting binary constraints between1056 D-edge variables decompose into
240 four-cycles and96 isolated variables. Every inequality constraint can be
satisfied simultaneously. `pilot-algebraic-lift-003/constraints.json` and
`quotient.json` record the components, bipartite coloring, fibers and gauges.
The16 predefined cases compare aligned versus opposite bits, with common random
choices for V4 translations and the larger D8 partition-preserving group.

The prediction that eliminating blue triangles improves the full objective is
**false in this tested family**: all anti-triangle cases remove exactly3840
blue triangles but worsen N by52944..64416 because of the K4 term. All aligned
controls retain those triangles yet improve N by168816..173376. The paired
design thus discovers a stronger control rather than confirming its hypothesis.

All16 cases receive identical polish, without raw-score selection, in
`pilot-algebraic-polish-bank-003`. Every aligned case finishes substantially
better than its opposite-bit partner. Best N=10486269604, just3236 above McKay,
comes from V4 aligned repetition1. A raw-score ranking would not select it.

## H-ALG-006: exact C4 parity objective, then unrestricted polish

Fix aligned first bits and vary only the second-bit V4 voltage b_e on each
edge of D. Independently flipping the second bit in any whole fiber is a vertex
relabeling that preserves every fixed H/complete/empty block. The model builder
checks that invariance entry by entry, rather than assuming it from a name.

Write signs s_e=(-1)^b_e. Any K4-indicator contribution is multilinear in these
signs after reducing s_e²=1. Invariance under every fiber gauge forces its
Fourier support to have even degree at each quotient vertex. On at most four
fibers, triangle-free D leaves only empty support or a D4cycle. Repeated-fiber
quadruples involve at most three quotient vertices, so contribute only to the
constant. Consequently, at fixed first bits,

    N(b) = N(b0) + sum_C delta_C * (parity_C(b) - parity_C(b0)).

Each delta_C is24 times the difference of explicit monochromatic sheet-tuple
counts on those four fibers with odd versus even cycle parity. Gauge invariance
allows three cycle voltages to be normalized, so this difference is independent
of the representative. A triangle-free graph has at most one C4 on a four-set,
preventing duplicate support. Coefficients must be recomputed for different
first-bit choices; they are not universal constants across the architecture.

For the V4 aligned repetition1 parent, `pilot-algebraic-cycle-model-001` finds
8400 D4cycles, of which3372 are active, each with delta=-96. A literal16-vertex
tuple oracle checks all16 bit assignments in a small cycle fixture. Three
independently sampled full768 constructions exactly agree with native recounts
(predicted/actual10486994592,10486990656,10486994496). The literature worker
independently checked the gauge/Fourier/completeness argument.

Sixteen strict variable-descent restarts optimize this exact weighted XOR
objective in2.84s. `pilot-algebraic-cycle-opt-001` gives N=10486901088, lower
by92544 than its random aligned parent. It receives both a final native full
recount and the runner's independent compiled-Lean recount. No claim of global
optimality of the XOR problem follows from these restarts.

Identical unrestricted cached-star polish then produces

    N = 10486219192 over 768^4 = 1310777399/43486543872,

**47176 below the McKay numerator**. The finite witness is
`reports/pilot-algebraic-cycle-polish-001/candidate.json`, SHA256
`7dd4461967810f5780878b24ac64bd76858850fa0300a6a0aaa9f9170c926ee5`.
Independent Lean counts: red edges148720, blue triangles9128664, red K4
217117969, blue K4 206029748. This is a reproduced exact finite improvement,
not a world-record claim, kernel-only theorem, or stopping target. The newer
announced bound and the separate graphon investigation may be stronger.

Decision: pursue the explanatory exact cycle formulation and test a few distinct
first-bit parents with the same optimize/polish pipeline. Broader novelty and
general optimality remain unresolved. All retained finite candidates remain
inside the unchanged unit-weight/blue-diagonal checker domain.

That prescribed replication is complete. Two additional first-bit parents have
3412 and3346 active C4 terms, all delta=-96. With identical16-restart cycle
optimization and identical cached-star polish they give N=10486223872 and
N=10486241244, respectively (`cycle-polish-002` and `cycle-polish-003`). All
three cases beat McKay, whereas their matched random aligned parents do not.
The strongest finite unit-weight witness remains `cycle-polish-001` above.
This is three concrete matched comparisons, not proof of solver reliability
over arbitrary first-bit choices or global optimality.

## H-ALG-007: bounded finite rounding of a separate graphon improvement

The literature worker's independent probability-class investigation identifies
96 formerly complete quotient blocks worth softening in a192-block graphon.
Its later rational parameters use denominator65536, with class5 probability
51081/65536. The finite transfer test replaces J by J−P in each such4×4 block
with probability4*(1-p5). A paired condition also adjusts the degree-three
and degree-two classes by stochastic mixtures of regular blocks matching their
new mean probabilities. This is a correlated finite construction, not the
independent-edge graphon itself and not a purported graphon certificate.

Parent: the checked cycle-optimized raw graph N=10486901088. Four common-random
paired trials appear in `pilot-algebraic-quotient-round-001`. Class5-only changes
worsen raw N by831000..995304, and all mean shifts worsen it by435044..777284.
All eight outputs, without score filtering, undergo the same polish in
`pilot-algebraic-polish-bank-004`, with each child independently Lean checked.

Best rounded-and-polished N=10486249378, still16890 below McKay but worse than
the unchanged parent's matched polished N=10486219192. The all-class mean shift
is worse than class5-only after polish in three of four pairs. Thus this small
four-sheet correlated rounding fails to transfer the stronger graphon result.
Retire this particular finite rounding bank; no conclusion about the valid
independent-edge graphon limit, larger fibers, or all possible couplings follows.

## End-of-round handoff

All jobs owned by this round are finished and reaped. No further seed replication
was started after the coordinator's portfolio review. The final six algebraic
tests pass (0.61s): Seidel involution/repeated-index count, exhaustive GM4
feasibility on tiny graphs, lift/gauge/serialization, all90 degree-two patterns,
triangle constraints, and exact C4 model against literal tuples.

Strongest unit-weight artifact: `pilot-algebraic-cycle-polish-001`, as detailed
above. Other workers may have stronger weighted or graphon constructions; this
round's claim is limited to its retained finite artifacts. Valuable negative
results are the coarse Seidel bank, exhaustive GM4 obstruction on the seed,
blue-triangle minimization failure, and failed four-sheet graphon rounding.

The unresolved structural opportunity is to understand or optimize the complete
first-bit/second-bit quotient objective jointly, or transfer the independently
improved graphon using a construction with sufficiently large fibers and a
validated limit argument. Neither is solved here. Preserve the exact C4 model
and paired experiments; do not replace these gaps with more arbitrary random
seed repetitions or an unsupported novelty/world-record claim.
