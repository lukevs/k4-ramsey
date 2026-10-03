# Adversarial audit of the frozen current-best construction

Date: 2026-09-27

## Verdict

The frozen two-amplitude five-state artifact passes every structural,
normalization, boundary, repeated-index, and exact-arithmetic check performed
so far. I found no counterexample to the claimed graphon value.

The validated claim is narrow:

> The serialized 960-step rational graphon has monochromatic `K4` density
> `66019277286046017264653194279027 /
> 2190500237194380405786303138889728`, approximately
> `0.030138904422400026`, and therefore gives an asymptotic existence upper
> bound of that value for ordinary two-colorings.

This is **not** a proof of global optimality, a kernel theorem, an explicit
finite simple-graph witness at exactly that density, or a comparison with the
unpublished lower value mentioned by the user. It is strictly below the
rounded January 2026 published benchmark `0.030139` under the user's benchmark
classification.

## Frozen identities

| Artifact | SHA-256 |
|---|---|
| Current candidate | `33df1d72c6e50a2ea0dc205f771ab8d3372b621b273cc53237072017ad4dda4d` |
| Phase assignment | `226ab819da150c12b8152e2ac6a10acaf7d5dcff716199c42d8d42c68790011e` |
| Two-amplitude preregistration | `f3fbbd553e8f3a3cac6228026fef3c7b0a5876646fe1f3543c1b8c001c820260` |
| Two-amplitude source snapshot | `333b9acf4f672bd5e0f50173ac796b1c1637c4c84dde491f9353207f59cf2409` |
| Two-amplitude report | `badc91111c2ab339912fadaa29c8c10e524e35b0450b0dd6b33b3ef2d2eaaf93` |
| Frozen 192-class base | `e26e754168010c069da3e0b207a140f2c7cbbfc36cc0a6af06ef409db5024450` |
| Compressed recount candidate snapshot | `33df1d72c6e50a2ea0dc205f771ab8d3372b621b273cc53237072017ad4dda4d` |
| Compressed recount certificate | `ae2473ab58c790ade0e879041ad5a19d04bae662aed47bf080e929b66cbdbba0` |
| Compressed recount report | `c622b7916c60aabe171c25925095361033bffa9b8897eefad1ffec247f0635d3` |
| Generic direct U256 recount report | `284db8b1c2efe530cabb986a61ad4b4a1ee14f9996a567614862dfbaf7b35766` |
| Generic direct counter source | `a31c4052c5e429f042e4f0ea20e92a0078fa354c767b33f7801d9b0060beca97` |
| Generic direct driver | `d8efb98fdb4b8158ec3e55ce4b531fe2db111af3208bca7dd9b4fee03a46f7a8` |
| Standalone structural-audit source | `cc2cbd9e34829de2d1e25526de72cfc4044b4078f96b4964c170153bedaa3264` |
| Standalone structural-audit report | `69d575a6dd153953f99b151c2f32abd1314f7b8482d827de1b93a9f2ee8e522e` |

The standalone structural audit is
`reports/current-best-structure-audit-001/report.json`. It reads the frozen
base, phase assignment, and candidate, but no optimization report or supplied
score.

## Construction reconstructed from bytes

The base has 192 equal-mass coarse classes and denominator `Q=65536`. Each
coarse class is split into five equal fine types. On an active fractional
coarse edge `{i,j}`, with stored phase `x_ij in Z/5Z`, the red numerator is

`P_ij + q(P_ij) kappa(a-b-x_ij)` for `i<j`,

with the phase negated on reversed orientation and

`kappa(d)=3` for `d=plus/minus 1 mod 5`, and `-2` otherwise.

The two amplitudes are

- `q(51064)=-7236`;
- `q(35015)=-11671`.

The standalone audit reconstructed all 921,600 candidate entries from this
definition with zero mismatches. It checked all 36,864 coarse blocks, every
matrix symmetry pair, every range constraint, and every diagonal entry.

| Structural claim | Verdict | Evidence |
|---|---|---|
| Candidate is square, equal-mass, and correctly indexed | **PASS** | Order 960, 960 unit weights, base-major/type-minor indexing, denominator 65,536. |
| Candidate equals the frozen base/phase/two-amplitude construction | **PASS** | All 921,600 entries independently reconstructed; no mismatch. |
| Undirected symmetry | **PASS** | All entries satisfy `W_xy=W_yx`. Structurally, reversing the coarse edge negates the phase and `kappa(-d)=kappa(d)`. |
| Bounds and diagonal | **PASS** | Every entry lies in `[0,Q]`; all 960 diagonal entries are zero. |
| Exact coarse marginals | **PASS** | Every one of the `192^2` fine-block sums is `25 P_ij`. This follows because the kernel vector `[-2,3,-2,-2,3]` sums to zero. |
| Support/phase coverage | **PASS** | All 1,248 fractional coarse edges occur exactly once in the phase file: 976 active and 272 inactive. Active edges split as 880 of parent value 51,064 and 96 of parent value 35,015. |

The only candidate numerators are `0,2,29356,51064,58357,65536`. Inactive
edges all belong to the `51064` class; every `35015` edge is active.

## Boundary attack

Both selected amplitudes are at the exact lower endpoint of their independent
integer feasibility interval:

| Parent value | Exact feasible `q` | Selected | Fine values at selected `q` | At `q-1` |
|---|---:|---:|---:|---:|
| 51,064 | `[-7236,4824]` | `-7236` | `65536,29356` | `65538,29353` |
| 35,015 | `[-11671,10173]` | `-11671` | `58357,2` | `58359,-1` |

Thus the serialized candidate is valid, while increasing either negative
amplitude by one unit in magnitude immediately leaves `[0,Q]`. The boundary
does not cause an ambiguity in the count: probabilities zero and one are
ordinary exact factors. It does create an important future-model constraint.
Any later rule that defines support as “all fractional fine blocks” changes
support when a descendant reaches zero or one and must rebuild every motif
coefficient. No fixed-support recurrence may silently cross this face.

## Multivariate motif polynomial

The exact change from the coarse parent has the form

`Delta(q_p,q_h) = sum_(a,b) C_(a,b) q_p^a q_h^b`.

This follows by expanding the six edge factors. Kernel row-centering kills any
selected perturbation subset with a positional degree-one vertex, leaving only
triangles, four-cycles, diamonds, and `K4`, of total degrees 3 through 6.
Giving the two parent probability classes different amplitudes simply labels
each selected positional edge by `p` or `h`.

The repeated-index case is handled correctly. When two or more selected
positional edges map to the same coarse edge, the factor signature contains
that variable repeatedly. `TwoAmplitudeObjective` counts occurrences in the
signature, not distinct variables, so the monomial receives the required
repeated power of `q_p` or `q_h`. The incident list uses a set only to avoid
re-evaluating the same factor twice during a coordinate move; the factor value
itself retains all repeated occurrences. Literal small examples with repeated
coarse indices agree for mixed-sign and zero amplitudes.

At the selected amplitudes, the seven recorded monomial contributions sum
independently to

`Delta = -4903410661048703594617299671040000`.

Adding this to the five-fold lift of the frozen base gives raw total

`2028112198227333650370146128251709440000`.

The arithmetic agrees exactly with the candidate-bound recount described
below. This validates the reported polynomial evaluation but, by itself, would
not be an implementation-independent recount because the coefficients come
from the search model.

## Exact recount and normalization

For equal fine-class mass, the ordered graphon numerator is the sum over all
`960^4` ordered class quadruples of the red six-edge product plus the blue
six-edge product. Every probability is stored over `Q`, so the unreduced
normalization is

`960^4 * 65536^6 = 67292167286611366065755232426692444160000`.

The frozen compressed audit reports

- red: `1012200962346867798814543106142827520000`;
- blue: `1015911235880465851555603022108881920000`;
- total: `2028112198227333650370146128251709440000`.

Red plus blue equals total, and reducing total by the normalization gives

`66019277286046017264653194279027 /
2190500237194380405786303138889728`.

| Recount claim | Verdict | Boundary |
|---|---|---|
| Candidate-bound structural histogram | **PASS, trusted-native scope** | Fresh native code reads every candidate entry, extracts all oriented `5x5` kernels, and builds the exact coarse-signature histogram. This is independent of the phase optimizer. |
| Coarse-index multiplicities | **PASS** | It enumerates sorted coarse quadruples and weights each by `4! / product multiplicity!`. The histogram mass is exactly `192^4`. |
| Fine-type and repeated-index enumeration | **PASS** | For every signature, compiled Lean sums all `5^4` ordered fine-type assignments and multiplies all six edge factors. Repeated coarse and fine indices remain present. |
| Tiny literal controls | **PASS** | Eight arbitrary oriented-block fixtures at base orders 1--4 cover coarse multiplicity partitions `4`, `31`, `22`, `211`, and `1111` and agree with literal ordered quadruples. |
| Lean candidate binding | **UNKNOWN / not claimed** | Lean checks certificate structure, mass, and exact `Nat` arithmetic but trusts the native candidate-to-histogram stage. A forged mass-correct histogram could pass Lean alone. This is Level-A combined evidence, not a full Lean candidate recount or kernel theorem. |
| Fresh generic direct recount | **PASS** | `graphon-association-phase-two-amplitude-direct-u256-001` reads only the candidate matrix, not a score, phase decomposition, histogram, or search report. It loops over all ordered fine indices and agrees exactly on red, blue, total, denominator, and reduced fraction. Twelve arbitrary symmetric matrices of orders 1--4, including arbitrary diagonals, agree with a literal Python big-integer oracle. |
| Direct-counter overflow safety | **PASS** | Pair products are at most `Q^2=2^32` in 64 bits. The complete inner contraction is below `960^2 Q^5 <2^128`, one outer addend below `960^2 Q^6 <2^128`, and the global nonnegative total below `960^4 Q^6 <2^256`. The four-limb addition and decimal conversion were separately source-audited. |

## Asymptotic realization

The artifact is a rational step graphon, not a finite 960-vertex simple graph
with this ordinary finite density. To realize it, take `t` vertices in each of
the 960 fine classes and independently color each distinct vertex edge red
with its class-pair probability.

For four distinct sampled vertices the six graph edges are distinct and their
colors are independent, even if two or more vertices have the same class
label. Therefore their expected monochromatic indicator is exactly the
six-factor expression used by the graphon count. Repeated class indices are
required here; they do not mean reusing one random edge color.

Sampling four vertices with replacement differs from conditioning on four
distinct vertices by at most the collision probability, bounded by
`6/(960t)`. Hence the expected finite monochromatic density converges to the
reported graphon value. Some deterministic coloring is no worse than the
expectation. The finite minimum densities are nondecreasing by averaging over
induced subgraphs, so their limit is at most this cofinal subsequence limit.

Verdict: **PASS as ordinary mathematics; not kernel-formalized**.

## Benchmark comparison and optimization scope

Exact subtraction from the rounded published benchmark gives

`0.030139 - F =
3271293053340395940562874539253 /
34226566206162193840410986545152000000 > 0`,

about `9.56e-8`. The artifact improves its immediate common-amplitude parent by
about `4.15e-8`.

The optimizer reaches a **block-coordinate fixed point**:

- the final phase sweep has zero strict one-edge moves;
- each amplitude is an exact integer coordinate minimum with the other fixed;
- both amplitudes remain unchanged in the final alternation round.

This does not imply a global bivariate amplitude minimum, a multiedge phase
minimum, or a plateau-component minimum. Ties are retained. The family also
fixes the 192-class coarse matrix, five equal fine types, one cyclic kernel,
two global amplitudes, and an active/off phase state per fractional coarse
edge. Edge-specific amplitudes, different kernels, unequal type weights, and
coarse-probability motion remain outside the claim.

## Final claim table

| Claim | Verdict |
|---|---|
| Frozen bytes encode the stated two-amplitude construction | **PASS** |
| Symmetry, bounds, diagonal, equal masses, and coarse marginals | **PASS** |
| Per-type boundary feasibility | **PASS** |
| Multivariate repeated-factor powers | **PASS** |
| Exact reduced density under Level-A recount | **PASS** |
| Independent generic direct full recount | **PASS** |
| Asymptotic finite-coloring existence | **PASS, prose proof** |
| Below rounded January 2026 published benchmark | **PASS numerically** |
| Below the separate unpublished value | **UNKNOWN and not claimed** |
| Phase/amplitude local optimum beyond strict coordinates | **UNKNOWN** |
| Global optimum, novelty, or world record | **UNKNOWN and not claimed** |

No falsifying discrepancy was found. The remaining evidence upgrade, if formal
assurance is desired, is a candidate-bound Lean reconstruction or a
kernel-checked motif identity; the present compiled Lean stage verifies exact
certificate arithmetic rather than reconstructing the candidate histogram.

## Incumbent update: clipped boundary-face candidate

After the complete audit above froze, a slightly stronger candidate was
materialized at
`reports/joint-coarse-boundary-face-001/graphon-candidate.json`, SHA-256
`b93b3589a5be4846436f1f721df5efaf06a6bc852c008e00cf74cdce0d87e838`.
This section is a narrower audit of that update; it does not retroactively
attribute the `33df...` generic direct recount to the new bytes.

The new candidate retains the `33df...` phase/support assignment and the
`p=51064` face with `q_p=-7236`. It moves the mean of every active `h` block to
`35139` and sets `q_h=-11713`. Consequently its two active `h` fine values are
exactly

`35139 + 3*(-11713) = 0` and
`35139 - 2*(-11713) = 58565`.

Inactive fractional blocks retain their original means byte-for-byte.

| Updated claim | Verdict | Evidence and boundary |
|---|---|---|
| Residual-face parameterization | **PASS** | On the `p` face, `active_p=51064-2t` and `q_p=-7236-t` keep the clipped `kappa=-2` cell at `Q`, while the other cell is `29356-5t`; hence `0<=t<=5871`. On the `h` face, `active_h=35013+r+3t` and `q_h=-11671-t` keep the `kappa=3` cell at residue `r`, while the other is `58355+r+5t`, giving the reported bounds. The winner is residue zero and `t_h=42`. |
| Active/inactive semantics | **PASS** | The changed coarse matrix modifies active edges only. Inactive means remain in the direct coarse count and in every unselected-edge motif weight. `PhaseModel` and all typed coefficients are rebuilt for every sampled coarse matrix; no stale coefficient is transferred. Original `p/h` kinds remain well-defined because every changed coarse mean stays strictly between zero and `Q`. |
| Direct-coarse plus typed-delta normalization | **PASS** | A 192-class direct ordered recount gives the changed coarse raw total. Multiplying by `5^4` accounts for all fine-type lifts of the baseline. The recomputed typed delta is already summed over fine microtypes, so their sum has denominator `(5*192)^4 Q^6`, with no missing or duplicate factor. A literal small affine example agrees exactly. |
| Coordinate interpolation | **PASS, restricted scope** | Along either face coordinate every fine edge probability is affine, so the six-edge objective has degree at most six. Seven exact samples determine the complete line, and the integer line minimizer is exact. Alternating these line minima for at most three sweeps is not a global two-variable proof. The tested residuals `r=0,1,2` are all integer lower-boundary faces: `r=h+3q=h mod 3` when `q=-floor(h/3)`. There are no missing boundary residues 3 or 4; the step size 5 belongs to the opposite cell's motion along a fixed-residue ray. |
| Serialized bounds/symmetry/marginals | **PASS at candidate-bound native scope** | The materializer checks all entries and symmetry and verifies every active/inactive coarse block sum against its intended mean. The selected active `h` cell at zero is valid. It also means any later “all fractional descendants” support rule must rebuild its support and coefficients. |
| Exact recount | **PASS at Level A only** | `graphon-joint-coarse-boundary-face-compressed-001` reads the exact `b93b...` candidate, builds the structural histogram, and evaluates it with compiled Lean exact arithmetic. Red is `1012318055788828548031119660375982080000`; blue is `1015794114440761808382405480746434560000`; total is `2028112170229590356413525141122416640000`. The reduced density is `1375401591138773841968807740019/45635421608216258453881315393536`, approximately `0.030138904006337588`. Lean still trusts the native histogram binding, and no candidate-only generic direct recount is yet attached to `b93b...`. |
| Asymptotic realization | **PASS** | The equal-mass 960-step graphon has the same independent-edge first-moment realization as `33df...`; zero/one cells require no new argument. |

The boundary-face source and report hash to
`36a025bb1c91b2573bf50959b0a65dfc381c8a5debe450d71b9802ba9423dfd9`
and `525ea232d1769806ab44e529d3d8242496844cc05dfc6f31c308d7e20b8c336d`
respectively. Its compressed-audit report and certificate hash to
`7faaf29b1b505874898c4944d7259ef98292cd03100f8f8a428ef7829214797b`
and `730606d4c91ea92cbdb58f4d157797fa923af20cceb847800cd006d4b583b434`.
The new exact improvement over `33df...` is only about
`4.16e-10`; it is real under the Level-A recount but should remain labeled
with that evidence tier until a second direct candidate-only recount finishes.

## Incumbent update: per-edge amplitudes and continuation

The current frozen incumbent is
`reports/association-scheme-per-edge-boundary-continuation-001/graphon-candidate.json`,
SHA-256
`d4763fefc34a3966bfbe811d279b522c067f193e436bb522d357dd423c0c58c3`.
It continues the three-sweep per-edge artifact `3f657ae09b736b09...` for ten
more lexicographic sweeps while freezing the coarse means, cyclic kernel,
phase assignment, and support inherited from `b93b...`.

| Per-edge claim | Verdict | Evidence and boundary |
|---|---|---|
| Repeated amplitude multiplicities | **PASS** | A factor signature retains every positional occurrence of an unordered coarse-edge variable. When the coordinate variable occurs `m` times, `coordinate_coefficients` removes all `m` copies from the other-amplitude product and places their common factor in the coefficient of `x^m`. The incident list deduplicates only factor indices, not signature entries. Multiplicities through four occur. The exact sole-edge `2+2` fixture produces a nonzero fourth-power term and literal recounts agree at every feasible amplitude. |
| Sequential coordinate updates | **PASS** | Coefficients are rebuilt from the current amplitude vector immediately before every move. Thus later moves include earlier moves in the same sweep; no matched-screen coefficient is reused. `full_objective` is recomputed after every sweep. |
| Candidate materialization | **PASS** | Each active unordered coarse edge reads its own serialized amplitude, uses the fixed phase with the reverse orientation negated, and adds `q_e*kappa(a-b-phase)`. Inactive edges receive amplitude zero. The first run reconstructs the `b93b...` parent exactly before descent, and the continuation reconstructs the complete `3f657...` candidate exactly from its amplitude file before proceeding. |
| Feasible integer intervals | **PASS** | For `p=51064`, requiring both `p-2q` and `p+3q` in `[0,65536]` gives `[-7236,4824]`. For active `h=35139` it gives `[-11713,10132]`. The minimizer enumerates every integer in the relevant per-edge interval, and materialization checks all final entries. |
| Density and normalization | **PASS, independent direct recount** | A generic direct ordered-index U256 program read only the frozen `d4763...` matrix and obtained red `1012334007820347997697733495484569780000`, blue `1015778132737535276816604928434985140000`, and total `2028112140557883274514338423919554920000` over `960^4*65536^6`. The reduced density is `16900934504649027287619486865996291 / 560768060721761383881293603555770368`, about `0.03013890356539909`. Its report SHA-256 is `634a92d73e6c6e15e10e72a7d4da6462894862f73c528e798241eebca94d7b01`; twelve arbitrary order-1--4 literal controls and conservative overflow bounds pass. |
| Search-code reproducibility | **PASS with packaging caveat** | The continuation source snapshot hashes to `5da3f47602b682494c163576008eee67228c1020a7b15ad4a381abe86ac3b3dd`. The first three-sweep snapshot differs from the working source only in output formatting. However, both snapshots import the common per-edge/phase modules rather than vendoring their exact versions, so the candidate and direct recount are immutable but the search derivation is not fully self-contained in its report directory. |
| Optimization claim | **NOT ESTABLISHED beyond completed sweeps** | Sweep 13 still made 25 strict moves and termination is `sweep_limit`, not a coordinate fixed point. The count is valid, but even coordinatewise local optimality has not yet been reached, and no global claim follows. |

The predecessor `3f657...` also has an independent candidate-only direct
recount matching its predicted density, but it is superseded by `d4763...`.
The direct recount validates the incumbent value independently of the motif
model; the model audit above additionally supports the interpretation as a
member of the claimed per-edge amplitude family.
