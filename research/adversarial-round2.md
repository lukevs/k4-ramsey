# Adversarial review, resumed round R1

Date: 2026-09-27. This review used the hypothesis-research audit protocol and
performed no search or sustained CPU experiment. It inspected the serialized
artifacts, recorded hashes, checker sources, counting formulas, normalization,
overflow arguments, and comparison claims. A **pass** is scoped to the stated
claim; it is not a novelty or optimality ruling.

## Bottom line

I did not falsify the strongest finite, weighted, or stochastic-graphon value.
The exact artifact hashes in `research/RESUME.md` match the files on disk. The
finite and weighted partition formulas survive an independent hand derivation,
and the high-precision graphon's direct ordered counter handles repeated class
indices with six separate probability factors. Its signed-128 arithmetic is
safe under the recorded bound.

The principal correction is semantic. The reported finite values are densities
of **finite block templates and their infinite blow-ups**. In particular,
`10486219192/768^4` is not the ordinary `M4(G)/binom(768,4)` ratio of the base
768-vertex graph. Likewise, the weighted value is a rational block-mass graphon
density, not exactly the finite density of one graph on 3,145,728 vertices.
Both are valid asymptotic constructions under the hill's intended semantics.

The stochastic result gives a mathematically adequate asymptotic existence
argument but not an explicit deterministic finite witness, a kernel proof, a
novelty finding, or an established improvement over the unavailable exact
Feinstein--Even-Zohar construction.

## Claim audit

| Claim | Verdict | Evidence and boundary |
|---|---|---|
| Unit candidate identity | **PASS** | `pilot-algebraic-cycle-polish-001/candidate.json` hashes to `7dd4461967810f5780878b24ac64bd76858850fa0300a6a0aaa9f9170c926ee5`, matching its report and handoff. The checker reads the rows, rejects malformed/asymmetric/red-diagonal inputs, and does not read a supplied score from the candidate. |
| Unit count `10486219192/768^4` | **PASS, compiled-computation scope** | The report's components independently recombine as `n + 14 E_blue + 36 T_blue + 24(K4_red+K4_blue) = 10486219192`. Coefficients follow from ordered class-index patterns: `4`; `3+1` and `2+2` contribute `8+6=14`; `2+1+1` contributes `36`; four distinct indices contribute `24`. The compiled Lean binary and current sources match their recorded hashes. `K4Ramsey/Tests.lean` compares the optimized counter to a literal ordered-tuple oracle on all 1,024 five-vertex graphs and checks word boundaries. This is not a kernel theorem of the general identity. |
| Unit candidate beats the frozen McKay reference | **PASS** | At the shared denominator, `10486266368-10486219192=47176`. This proves a strict improvement over the exact frozen numeric reference. McKay's adjacency matrix is absent, so it does not reproduce or structurally compare against McKay's graph. The reference provenance is PPSS v3's final note/personal communication, as documented by the hill. |
| “Explicit 768-vertex graph has this density” | **FAIL if read literally** | The artifact is an explicit 768-vertex adjacency matrix, but the reported objective includes repeated template indices and denominator `768^4`; it is the limiting density of balanced blow-ups with blue diagonal blocks. Use “768-block binary template” or “768-vertex template graph,” not the ordinary finite `K4` density of the base graph. |
| Weighted candidate identity and input semantics | **PASS** | Candidate hash `45e79a75ab55c298d6c25cd3d5e3f93d6ff3305842091a203aafd66a1af42ee4` matches the sidecar. It has 768 positive integer weights in `[3712,4408]`, total `3145728`, and exactly the same adjacency rows as the strongest unit template. The wrapper and compiled checker validate weight bounds, dimensions, symmetry, binary rows, and blue diagonals. |
| Weighted count `23059300053734294930609/765023370224882524618752` | **PASS, one-implementation caveat** | The full compiled Lean recount reports numerator `2951590406877989751117952` over `(3145728)^4`, reducing to the claimed fraction. A hand partition check agrees: same-class terms are `sum w_i^4`; a blue pair contributes `4(w_i^3w_j+w_iw_j^3)+6w_i^2w_j^2`; each blue triangle contributes `12w_iw_jw_k(w_i+w_j+w_k)`; four distinct monochromatic classes contribute `24w_iw_jw_kw_l`. `WeightedTests.lean` checks every four-vertex graph under all binary `{1,2}` weight assignments, varied weights, and size boundaries. However, the search's line interpolation and final recount both use the same weighted Lean objective implementation. The final invocation is separate, but it is not an implementation-independent recount. |
| Weighted result beats McKay | **PASS** | Exact cross multiplication of the verified weighted fraction against `10486266368/768^4` is negative. Selection of the direction and step on this same deterministic objective does not invalidate the witness. It does not establish that curvature search is generally superior. |
| Weighted value is an exact finite 3,145,728-vertex density | **FAIL if claimed** | The denominator `Q^4` and repeated block indices define the limit under further common scaling. The hill lifting lemma shows convergence with `O(1/tQ)` collision error. Call it a weighted block-template/asymptotic density. |
| Precision graphon artifact identity and validity | **PASS** | Hash `e26e754168010c069da3e0b207a140f2c7cbbfc36cc0a6af06ef409db5024450` matches both audit and handoff. The artifact has 192 equal-weight classes, a symmetric `192x192` integer matrix, denominator `65536`, entries in `[0,65536]`, and zero red diagonal. No claimed score is stored in the candidate. |
| Precision graphon repeated-index semantics | **PASS** | `ordered_graphon_check.cpp` loops over all ordered `i,j,k,l` and evaluates `Pij*Pik*Pil*Pjk*Pjl*Pkl`, then the blue complement. When class indices repeat, the same probability value can occur several times but is multiplied once for each of the six distinct graph edges. This is correct for independently colored edges among four distinct expanded vertices. It does not reuse one sampled template edge. |
| Precision graphon exact count and normalization | **PASS, exact C++ scope** | The partition counter and the direct ordered-index counter use different enumerations and agree on total `3244987362620791518517985192882208768` over `192^4*65536^6 = 107667467658578185705208371882707910656`, reducing to `515776850799050572477656236153/17113283103081096920205493272576`. The ordered-counter source snapshot hash matches the current source (`76eb...4293`). The simpler `Q=41` member was also recounted by a standalone compiled Lean implementation and checked on 20 tiny arbitrary rational matrices, which supports the convention but is not a recount of the precision artifact. |
| Precision graphon has no signed-128 overflow | **PASS** | `192^4*65536^6 < 2^127`. All accumulated terms are nonnegative, and for any six probabilities in `[0,Q]`, `prod p_e + prod(Q-p_e) <= Q^6`; hence every partial total is below the final global bound. In the direct counter, each `long long` product is at most `Q^2=2^32`; conversion to `__int128` occurs before larger products. The partition counter stores probability arithmetic in `__int128`. |
| Precision graphon is below `0.030139` | **PASS** | Exact cross multiplication against `30139/10^6` is negative by `388644710607600417125589168064` in the unreduced cross-product orientation. It is also strictly better than the Lean-recounted simple graphon. This only beats the rounded public threshold, not necessarily the actual unpublished construction. |
| Stochastic graphon implies `c4 <= F(P)` | **PASS as ordinary mathematics; not formalized** | For `192` classes of size `m`, color every distinct vertex edge independently with its class-pair probability. For any fixed four-set, its six edges are distinct and therefore independent even when class labels repeat. The expected monochromatic density converges to the ordered equal-class sum because sampling four distinct vertices converges to four IID uniform class labels. Some outcome is no worse than the expectation. Since the finite minima are nondecreasing and bounded, their limit along this subsequence is at most `F(P)`. No rational-probability sampling or random-template-edge reuse is needed. A formal Lean theorem is absent but there is no theorem-strength missing lemma in the prose argument. |
| High-precision Lean recount | **PASS, compiled-computation scope** | `reports/graphon-precision-lean-001/report.json` now records a standalone exact-`Nat` ordered-index recount. Its candidate snapshot is byte-identical to the original and has hash `e26e...4450`; red `1620114197726184155591033697069957120` plus blue `1624873164894607362926951495812251648` equals the two C++ totals. The source imports only `Std`, uses unbounded `Nat`, validates dimensions/range/symmetry, and passed 20 tiny matrices against a direct Python six-edge oracle. Source and snapshot share hash `c2d5...aa23`. This is independent compiled Lean execution, not a kernel proof. |
| Search-method reliability / robustness | **UNKNOWN** | Three finite successes are matched comparisons inside one algebraic-plus-polish pipeline, not three independent construction families. The weighted result is one selected exact line. The graphon parameters were optimized on the same deterministic objective they are reported on. This creates no held-out-data issue for witness validity, but it supports no general solver-superiority, basin-frequency, or local/global-optimum claim. |
| Novelty or world-record status | **UNKNOWN** | Passing McKay and a rounded announcement threshold does not settle comparison with Feinstein--Even-Zohar. Their exact value and construction remain unavailable, and the announced “structured randomized constructions” could overlap substantially with this stochastic block mechanism. No novelty claim is currently justified. |

## Checker-independence assessment

1. **Unit template:** good separation. Search scores come from native C++
   incremental machinery; the final artifact is fully reread and counted by a
   compiled Lean program using clique decomposition, with a literal tuple oracle
   on exhaustive tiny cases.
2. **Weighted template:** adequate correctness evidence, weaker independence.
   The checker fully rereads the artifact and uses arbitrary-precision `Nat`, but
   the search interpolation also queries this same objective implementation.
   The exhaustive four-vertex literal tests and the hand partition derivation
   are the independent checks.
3. **Precision stochastic graphon:** good enumeration diversity but currently
   supported at full precision by a partition-by-equality C++ counter, a direct
   ordered-index C++ counter, and a standalone exact-`Nat` compiled Lean ordered
   counter. All three implement the same mathematical graphon convention, so
   their agreement is execution evidence rather than a kernel theorem of that
   convention.

## Priority integrity incident: cycle-model local minimum

The initial report that `finite-joint-control-002` found improving second-bit
coordinates directly at the H-ALG-006 local minimum was **not** a contradiction.
The exact cause is a zero-delta tie rule in the new strategy:

```python
if delta < best_delta or (delta == best_delta and target < best):
    best_delta, best = delta, target
```

Thus it accepts a zero move when the target voltage has the smaller integer
label. On the exact parent (hash `2e32...73a8`), inferred shifts match all 1,056
stored `best_bits`, the fixed first bits also match, and the stored model has
minimum one-coordinate delta zero: eight ties and no negative coordinate. I
directly applied and rolled back all eight tied coordinates; every exact native
delta was zero. A representative positive coordinate, 833, was `+96` in both
the model and a full recount.

`finite-joint-first-move-audit-003` reproduces the deterministic path. It takes
three exact plateau moves (coordinates 466, 692, 966), each model/native delta
zero; this changes the parities seen by later variables. Coordinate 688 then
has model and exact delta `-480`. The four-move child has native and compiled
Lean numerator `10486900608` and candidate hash `3ec2...ba5`. A fresh model
rebuild from the exact parent reproduces 8,400 cycles and 3,372 active
coefficient terms, all `-96`, with identical fiber/block/term structure.

Verdict:

- **PASS:** H-ALG-006 is a strict-decrease one-coordinate local minimum
  (minimum delta is zero, so no strictly improving coordinate exists).
- **PASS:** the second-only control supplies exact evidence that a directed
  walk across its zero plateau can expose a later strict improvement.
- **PASS, distinct scope:** the joint run changes either voltage bit and is
  outside the fixed-first-bit C4 model; its final candidate is Lean recounted.
- **Do not claim:** the original point is plateau-component optimal, the
  control exhausts every zero path, or the time-limited joint run is a
  restricted local minimum. The tie rule is label-orientation dependent.

## R2 audit: precision latent-sign split

Artifact: `reports/latent-precision-002/graphon-candidate.json`, SHA-256
`25caaa51c76f1c07e61656a93be5165093f080d43d083219a659ffac077775df`.
Parent: precision graphon hash `e26e...4450`.

| Claim | Verdict | Evidence and boundary |
|---|---|---|
| Candidate is the claimed latent split | **PASS** | I independently reconstructed all `384^2` entries from the hashed 192-class parent. On exactly the 1,248 fractional parent pairs, `P'_(i,s),(j,t)=P_ij+q*s*t` with integer `q=-4752`; all other entries are unchanged. There were zero mismatches. The candidate has 384 unit-mass classes, denominator 65,536, is square and symmetric, has zero diagonal, and has values `{0,30263,39767,46312,55816,65536}` all in range. |
| Support and admissibility | **PASS** | The support is exactly the union of the 96 `35015` pairs and 1,152 `51064` pairs. Every support vertex has degree 13. The tight probability margin is `min(51064,65536-51064)=14472`, so `|q|=4752` is admissible. Separate supports are triangle-free; their union has the reported 1,152 support triangles, explaining why only the union can have a cubic term. |
| Expansion contains only cubic and quartic terms | **PASS** | Averaging over four independent latent signs kills every perturbation-edge subset with an odd positional degree. The nonempty even-degree simple subgraphs of positional `K4` are exactly its four triangles and three 4-cycles. Hence `F(q/Q)=F0+(A q^3+B q^4)/(n^4 Q^6)` with no linear, quadratic, fifth, or sixth term. This logic remains valid when base-class indices repeat because the four positional latent signs are independently summed; `C_ii=0` prevents loop-support terms. |
| Cubic coefficient formula | **PASS by derivation and fixtures** | For each undirected support triangle `{i,j,k}`, the isolated fourth base label `l` contributes `24[P_il P_jl P_kl-(Q-P_il)(Q-P_jl)(Q-P_kl)]`. The factor 24 is four isolated-position choices times six triangle-label permutations. The implementation sums `l` over all base labels, including `l=i,j,k`, so repeated base indices are retained. Its 12 literal tiny comparisons cover both signs and supported triangles. |
| Quartic coefficient formula | **PASS by derivation and fixtures** | Fix one positional 4-cycle and opposite labels `i,k`; its other two labels `j,l` must lie in `N(i) intersect N(k)`. The two unperturbed diagonals contribute `P_ik P_jl+(Q-P_ik)(Q-P_jl)`. Summing ordered `j,l`, including `j=l`, gives `(Q-P_ik)Q c^2+(2P_ik-Q) sum_(j,l)P_jl`; multiplying by three covers the three positional 4-cycles. This is the implemented formula and explicitly includes repeated base labels. Triangle-free tiny supports with nonzero quartic terms agree with literal ordered counts. |
| Integer minimization on the chosen line | **PASS, restricted scope** | For `Aq^3+Bq^4`, all possible bounded integer minima lie at endpoints, zero, or integers neighboring `-3A/(4B)`. The screen checks these candidates and selects `q=-4752` (`epsilon=-297/4096`). This is the exact grid minimum for each of three preregistered supports, not an optimum over arbitrary supports or refinements. |
| U256 ordered recount arithmetic | **PASS** | Pair products are at most `Q^2=2^32` in `uint64`. Each inner `k,l` sum is bounded by `384^2 Q^5 <2^128`; multiplying by the outer edge remains below `384^2 Q^6 <2^128`. The complete nonnegative sum can exceed 128 bits but is below `384^4 Q^6`, far below 256 bits. The four-limb addition propagates carries correctly, and decimal conversion divides a four-limb copy using a 128-bit `(remainder<<64)|limb`, with remainder below 10. The checker validates all entries are at most `Q`; artifact symmetry is separately established. |
| C++ exact count and normalization | **PASS** | The direct ordered-index recount gives red `25921517909898492898077455905292550144`, blue `25998277089855978252837899376776970240`, and total `51919794999754471150915355282069520384`; red plus blue equals total. The normalization equals `384^4*65536^6`. The reduced density exactly matches the expansion: `515776822961911272515012376329/17113283103081096920205493272576`. The checker source snapshot and live source both hash to `a0c7...0c34`; construction source and snapshot both hash to `7f79...ddc3`. |
| Improvement over precision parent | **PASS** | The reduced denominators are identical. The numerator decreases by `27837139299962643859824`, a density improvement of about `1.62663932643e-9`. It is also strictly better than the simple-Q41 latent split and remains exactly below `30139/10^6`. This is small but far above any floating-only distinction because comparison is integer exact. |
| Independent exact-`Nat` Lean recount | **PASS, compiled-computation scope** | `graphon-latent-precision-lean-001` hash-checks the candidate, passed 12 small arbitrary-matrix fixtures against a direct Python ordered oracle, and completed the full 384-class recount in 602 seconds. Its exact red `25921517909898492898077455905292550144`, blue `25998277089855978252837899376776970240`, total, denominator, and reduced fraction all agree with the C++ artifact. It reads only the candidate matrix, not expansion metadata or a supplied score. This is compiled Lean exact-`Nat` execution, not a kernel theorem. |
| Novelty / record | **UNKNOWN** | This strengthens our reproduced stochastic graphon, but the exact Feinstein--Even-Zohar value and construction are still unavailable. No record or novelty language follows from the numerical improvement alone. |

The simple-Q41 and precision mechanisms agree qualitatively: neither
triangle-free probability class improves alone, while their union creates a
nonzero cubic interaction and favors a negative perturbation of about `-0.073`.
The precision run recomputes all coefficients and admissibility from its own
parent; it does not transfer the simple-case numerics.

## R2 derivation audit: recursive latent coordinates

This audits `research/recursive-latent.md`; no recursive experiment has been
run.

| Claim | Verdict | Reason |
|---|---|---|
| Different latent levels cannot coexist in a surviving monomial | **PASS** | Expanding each positional edge assigns it to at most one latent level. Sign averaging requires the edge subset assigned to each level to be Eulerian on positional `K4`. Its only nonempty Eulerian simple subgraphs are triangles and 4-cycles. Every pair of such subgraphs intersects in an edge, so two levels cannot both receive disjoint nonempty subsets. This remains positional and is unaffected by repeated base labels. |
| `v_r=v_0+U sum epsilon_a^3+V sum epsilon_a^4` | **PASS for a fixed typed `(P,C)`** | The preceding no-mixing fact leaves one triangle or one 4-cycle from a single level. Old latent coordinates cannot modify a new level's coefficient without producing a forbidden mixed term. Changing the support/type rule invalidates the fixed `U,V`. |
| Raw coefficient scaling by `16^r` | **PASS** | Each ordered base quadruple has `2^(4r)=16^r` old-latent lifts. Equivalently a base triangle's three vertices have `8^r` lifts and its isolated fourth vertex `2^r`; a 4-cycle uses all four. The refined order-to-the-fourth normalization also gains `16^r`, leaving normalized coefficients invariant. |
| Exact feasibility `sum_a |q_a| <= 14472` | **PASS** | For a fixed active block, every vector of coordinatewise products `s_a t_a` is attainable (take one latent vector all `+1`). Hence the maximum positive and negative perturbations are exactly `plus/minus sum|q_a|`. The tight parent-block margin is 14,472, making the condition both necessary and sufficient. Three copies of `-4752` are valid; four are not. |
| Infinite shrinking hierarchy formula | **PASS conditionally** | Under strict feasibility and fixed lifted support, uniform convergence follows from absolute geometric summability, and the no-mixing recurrence sums the cubic and quartic geometric series. At a boundary where descendants become 0 or 1, an “all fractional” support rule changes type and the recurrence must be recomputed, as the note says. |
| A generic untyped 11-profile cannot close | **UNKNOWN / currently overstated** | The note correctly shows that the standard stochastic 11-state composition operator does not automatically apply and that `(P,C)` type alignment is absent from its derivation. That information argument alone does not prove nonexistence of every operator on untyped profiles. A categorical nonclosure claim needs two typed kernels with the same current 11-profile and different next profiles. On this particular two-dimensional affine orbit, the 11-vector may itself encode `(S3,S4)` if `U,V` are independent, and a prescribed next amplitude is an affine translation. Use “no universal untyped closure has been established / the composition operator does not apply” until a counterexample is supplied. |
| `(1,S3,S4)` is sufficient state | **PASS for the fixed additive kernel** | Once `U,V` are computed from the typed base, every profile in this family is affine in `S3,S4`; adding a prescribed amplitude translates those two sums. This is not a Perron--Frobenius stochastic operator and does not imply an attracting fixed point. |

## Prioritized gaps and focus recommendation

1. **P0 -- settle closest-prior overlap before any “new best” language.** The
   public `c4<0.030139` announcement is too coarse to compare. Continue the
   exact thesis/preprint/code search; absent an exact artifact, use “our strongest
   reproduced construction” and “below the announced rounded threshold.”
2. **P1 -- correct dashboard/user-facing semantics.** Label the first two rows
   “binary block template” and “weighted block template.” Label the probability
   result “stochastic graphon / asymptotic existence” and keep it in a distinct
   evidence class even after the high-precision compiled Lean recount.
3. **P1 -- if formal verification is the next goal, formalize the general
   ordered-tuple identity and lifting argument.** Current compiled Lean execution
   is strong certificate evidence, but neither the unit/weighted identity nor
   the stochastic realization is a kernel theorem.
4. **P2 -- do not allocate further effort to seed repeats or tiny precision
   tuning.** Selection uncertainty affects method claims, not these exact
   witnesses. New compute should target a materially different construction or
   the latent-split transfer after the prior-art comparison.

No sustained CPU job was started by this review. Two short read-only native
grouped-delta checks completed during the integrity incident; no process remains.

## R3 audit: cyclic five-state association-scheme refinement

Artifact: `reports/association-scheme-r5-001/graphon-candidate.json`, SHA-256
`b44a3a40b13b9bd41790132802816af9cf94b51f5ea759153360db41c8c07857`.
Parent: precision graphon hash `e26e...4450`. The reported exact density is

`2816829130796602774891955949737353 / 93461343453626897313548933925961728`

or approximately `0.030138975395685816`.

| Claim | Verdict | Evidence and boundary |
|---|---|---|
| Candidate bytes and construction | **PASS** | The file hash is exactly `b44a...857`. I independently reconstructed every entry of the `960 x 960` matrix from the hashed 192-class parent using `P'_(i,a),(j,b)=P_ij+q*kappa(a-b-g(i,j))` on fractional coarse pairs, with `q=-2611`, `kappa=3` on differences `plus/minus 1` and `-2` otherwise, and `g(i,j)=1` for `i<j` and `-1` for `i>j`. There were zero entry mismatches. The source snapshots and live construction/checker sources also exactly match their recorded hashes (`df79...38b0` and `a31c...a97`). |
| Fine matrix symmetry, range, and diagonals | **PASS** | All 921,600 entries are in `[0,65536]`; the matrix is symmetric and has zero diagonal. Symmetry follows structurally because `g(j,i)=-g(i,j)` and `kappa(-x)=kappa(x)`. The artifact has 960 unit block weights, so its normalization is `960^4*65536^6`. |
| Exact preservation of coarse marginals | **PASS** | `sum_x kappa(x)=0`, and for every fixed phase shift each difference occurs five times among the 25 fine pairs. Hence each coarse block has exact sum `25 P_ij`. I independently checked all `192^2` block sums, including diagonal blocks, with zero failures. This preserves the parent after forgetting the fine coordinate; it does not mean the nonlinear `K4` objective is preserved. |
| Sparse polynomial has degrees only 3 through 6 | **PASS** | In the six-edge expansion, summing a selected perturbation edge set over a positional microtype of degree one gives zero by the kernel row sum. Every surviving nonempty simple edge subset of positional `K4` therefore has minimum degree at least two: a triangle, 4-cycle, diamond, or all of `K4`, of degrees 3, 4, 5, and 6. The complementary-color sign is `(-1)^d`, giving the implemented triangle difference, C4 sum, diamond difference, and doubled K4 term. |
| Triangle/C4/diamond/K4 multiplicities | **PASS by derivation** | The factors are respectively 24 (four isolated-position choices times six triangle orderings), 3 (the three positional 4-cycles after summing all ordered base quadruples), 6 (choice of the missing positional edge), and 2 (red plus blue for the even six-edge term). The support loops enumerate precisely the required selected fractional edges. The recorded embedding totals are consistent with this organization: `5308416`, `484416`, `221184`, and `6912`. |
| Repeated coarse indices in the coefficient derivation | **PASS** | Repetition is excluded only where a selected perturbation edge would become a coarse loop, correctly making that factor zero. The free triangle vertex ranges over all 192 labels, including triangle labels; opposite C4 vertices may coincide; and the missing-edge endpoints of a diamond may coincide. Positional microtypes remain independently summed even when coarse labels coincide, so the moment cache correctly depends only on the selected positional edge set and its phase tuple. Tiny literal tests include repeated coarse labels, although their coverage alone would be weak; the exact generic full recount below is the decisive cross-check. |
| Phase/orientation semantics | **PASS** | The phase is an antisymmetric orientation of each coarse support edge, while the even kernel makes the resulting undirected fine probability symmetric. It need not be a gradient/gauge: nonzero cycle phase is the intended coherent perturbation. `micro_sum` sums all `5^4` positional microtype assignments, so cycle frustration is retained rather than averaged away accidentally. |
| Feasible interval and scalar selection | **PASS, restricted scope** | Because the kernel takes only `-2` and `3`, intersecting `0 <= P_ij-2q <= Q` and `0 <= P_ij+3q <= Q` over every fractional block gives the complete integer interval `[-7236,4824]`. The code exhausts that interval exactly and selects `q=-2611`. This is an exact optimum only on the one preregistered scalar direction, not over other phases, kernels, supports, or association schemes. The on-disk preregistration fixes those choices, but the filesystem alone is not external proof of its creation time. |
| Sparse coefficients and selected delta | **PASS with independent full-recount backstop** | Re-evaluating the recorded degree-3--6 integers at `q=-2611` gives exactly `-127464440701151532461740486320000`. Adding this over the recorded normalization to the parent fraction produces the reported child fraction exactly. More importantly, the separately organized checker consumes the fully materialized matrix and directly sums all ordered fine-class quadruples; it knows nothing about phases or polynomial coefficients and agrees exactly. This agreement would be exceptionally unlikely if a repeated-index multiplicity or phase-moment case were missing. |
| Generic U256 recount formula | **PASS** | For each color it computes `sum_(i,j) P_ij sum_(k,l)(P_ik P_jk)(P_il P_jl)P_kl`, exactly the product of the six positional edges over every ordered quadruple. Repetitions of fine or coarse class indices are included. It reports red `1012557335545927819569543152487647400000`, blue `1015559638627626178352665131323246760000`, and their exact sum `2028116974173553997922208283810894160000`. Reduction by the stated normalization reproduces the candidate fraction. An arbitrary 4-class fixture and a structured 15-class five-state fixture both agree with a literal six-edge oracle. |
| U256 arithmetic and overflow bounds | **PASS** | A pair product is at most `Q^2=2^32` in `uint64`. The `k,l` inner sum is below `960^2 Q^5 <2^128`; multiplying by the outer edge remains below `960^2 Q^6 <2^128`. The total is below `960^4 Q^6 <2^256`. Both U256 addition overloads correctly propagate carries, and decimal conversion is safe because its running remainder is below 10 before the 64-bit shift. The bounds cover each nonnegative partial sum, not only the final value. |
| Improvement over the parent | **PASS** | Exact subtraction gives `531101836254798051923918693 / 280384030360880691940646801777885184 > 0`. This makes the artifact the strongest exactly recounted construction presently in this repository. It remains an asymptotic stochastic graphon value, and it does not establish novelty or improvement over an unavailable exact Feinstein--Even-Zohar value. |
| Fully independent formal certificate | **UNKNOWN / not yet present** | The direct full recount is implementation-independent from the sparse polynomial but is another native C++ computation, not a Lean kernel theorem. A full 960-class exact-`Nat` Lean `O(n^4)` recount is possible but poor value per CPU. The cheapest strong independent certificate is a direct modular recount written independently of the U256 code: use three fixed approximately 61-bit primes whose product exceeds the proven `<2^136` total bound, compute the same ordered count modulo each with a different loop/block organization, and reconstruct the unique nonnegative integer by CRT. For formal assurance, a compact Lean certificate should instead prove the four surviving motif cases once, then verify the 192-class sparse coefficient vector and final integer evaluation; that avoids materializing an `O(960^4)` proof computation. |

No falsifying inconsistency was found. This review added only sub-second hash,
matrix-reconstruction, marginal, and exact-fraction checks; it did not start a
sustained recount or search job.

## R3 addendum: global latent-amplitude allocation

The new claim in `research/recursive-latent.md` that the fixed additive latent
family is globally minimized by four amplitudes `q_a=-3618` also survives a
derivation audit. After scaling, the tail-merging identity is positive whenever
the merged mass is below `3/4`, so countably many positive components reduce to
a finite case. The KKT equation has at most one small root at a local minimum.
For a five-component mixed point, the two-root relation gives
`s in [3/4,1]` and
`T=(5s+3 sqrt(3s(1-s)))/2 >= 5/2`, contradicting `T<12/5`.
For four components the displayed expansion is exact, and its quadratic has
discriminant `4(-26m^2+13m+1)<0` under the proved `m>57/100` bound.

Verdict: **PASS for the fixed-support separable family**, not for arbitrary
graphons or support-changing descendants. One expository sentence should be
widened: the lower bound for solutions with at most three positive components
is stated in the `lambda>=0` paragraph, but it is also needed when `lambda<0`.
It remains valid without that qualifier because `h(t)>=h(3/4)` for every
`t>=0`, so any at-most-three-component value is at least `3h(3/4)`.

## R3 addendum: precision three-state Potts candidate

Artifact: `reports/correlated-graphon-potts-precision-003/graphon-candidate.json`,
SHA-256 `bc6ff4995ea00723ec6df51d056362ddcab47c041635e612a8cf4b21fd6e8d05`.

| Claim | Verdict | Evidence and boundary |
|---|---|---|
| Serialized construction | **PASS** | I independently reconstructed all `576^2` entries from the hashed precision parent with `q=-4708` and kernel `2` for equal fine types, `-1` otherwise. There were zero mismatches. Every `3 x 3` block has perturbation sum zero, and all `192^2` coarse block sums equal `9 P_ij`. The reported exact fraction recomputes from numerator and normalization. |
| Degree-six interpolation/search | **PASS** | Each of six edge factors is affine in `q`, so the objective is a polynomial of degree at most six. Seven distinct exact calibration values determine it globally. Exhaustive evaluation on every feasible integer `q` then proves the line optimum at `-4708`; there is no statistical fitting assumption. This is only an optimum on the selected Potts line. |
| Counter arithmetic | **PASS** | The contraction is the exact ordered six-edge product. Pair products fit 64 bits, the complete inner contraction is below 128 bits, and the three-limb multiplication/addition correctly accumulates a total below the reported `2^134` bound. Its embedded arbitrary tiny matrices compare against literal ordered quadruples. |
| Candidate-input independence | **PASS at Level A; not candidate-bound Lean** | `graphon-potts-precision-compressed-001` hash-checks and parses the exact `bc6f...8d05` JSON, validates every matrix entry, and passes the complete matrix to a fresh native structural counter. That counter is independent of the search/U256 implementation. The compiled Lean stage evaluates the resulting exact-`Nat` certificate but does not independently reconstruct its histogram from the candidate. Thus the combined evidence is accurately “candidate-bound native structural recount plus Lean certificate arithmetic,” not a full Lean candidate recount or kernel proof. |
| Compressed histogram organization and controls | **PASS under the explicit native-binding trust boundary** | The native generator extracts every oriented `3 x 3` block, enumerates sorted coarse quadruples with weight `4!/product multiplicity!`, and the Lean evaluator sums all `3^4` ordered fine-type assignments per six-block signature. This covers repeated fine and coarse indices. Eight arbitrary oriented-block fixtures at base orders 1--4 and type counts 2 and 3 agree with literal ordered quadruples and exercise partitions `4`, `31`, `22`, `211`, and `1111`. The production certificate has 4 kernels, 1,002 signatures, mass `192^4`, and yields exactly the generic recount's red, blue, total, denominator, and reduced density. Generation took 0.238 seconds, Lean evaluation 0.024 seconds, and the full compile-plus-fixtures audit 3.35 seconds. A forged mass-correct histogram could still pass Lean alone; the trusted native candidate-to-histogram stage is essential to this verdict. |

## R4 audit: phase/support optimization of the five-state lift

Artifact: `reports/association-scheme-phase-001/graphon-candidate.json`, SHA-256
`31b6d0941b4d36e6e8ce61689321df1d1f914223ab21d261a60c1809c963d9b0`.
Its exact density is
`4126212387321705745944256745965 / 136906264824648775361643946180608`,
approximately `0.030138959620340307`.

| Claim | Verdict | Evidence and boundary |
|---|---|---|
| Phase/support factor model | **PASS** | The model is rebuilt from the fixed hashed 192-class parent. A state is inactive or one of five oriented phases on each of the 1,248 fractional coarse edges. Row-centering leaves only triangle, C4, diamond, and K4 perturbation subsets. Aggregation by signed edge-variable signature is exact because each microtype moment depends only on that signature; repeated occurrences of one coarse edge remain repeated factors inside the moment. |
| Orientation and control reproduction | **PASS** | Reversing a coarse edge negates its phase, and the even cyclic kernel makes the materialized fine matrix symmetric. Setting every state to phase 1 exactly reproduces all four stored coefficients and the selected delta of `association-scheme-r5-001`, providing a full-size control on indexing and normalization. |
| Coefficient reuse across amplitude change | **PASS** | Coordinate descent holds the parent and kernel fixed at `q=-2611`. After the phase/support state changes, the code recomputes all degree-3--6 coefficients for that exact state, derives the active-edge feasibility interval, and exhaustively minimizes its exact polynomial over every integer `q`. Moving to `q=-5496` therefore does not use stale coefficients. Any future change to the coarse parent probabilities must rebuild the factor weights; the joint coarse-probability lane has explicitly committed to doing so. |
| Serialized candidate | **PASS** | I independently reconstructed all `960^2` entries from the parent, selected phase assignment, eight inactive edges, and `q=-5496`; there were zero mismatches. The exact numerator/normalization reduces to the reported fraction. Every coarse block marginal is preserved because the five-state kernel sums to zero. |
| Independent recounts | **PASS at Level A plus generic C++** | The generic U256 ordered counter reports red `1012440513965551325127207325779148800000` and blue `1015675398650813483119313749997568000000`. The separate compressed structural audit reads the exact candidate and produces identical values using 10 block kernels and 22,257 signatures; native generation took 0.493 seconds and Lean exact-`Nat` evaluation 2.609 seconds. As before, the Lean stage trusts the native candidate-to-histogram binding. |
| Optimization status | **PASS witness; not locally optimized** | The exact witness is valid, but the phase run stops at the preregistered eight-sweep cap while its final sweep still accepts 51 strict moves. The phases were optimized at `q=-2611` and were not repolished after selecting `q=-5496`. It is therefore neither a phase-coordinate local optimum at the old amplitude nor a phase/amplitude fixed point at the reported amplitude. This is opportunity, not a validity defect. |

### Present mathematical ceilings

The current phase family preserves the entire coarse probability matrix and
can improve only through higher-order fine-type correlations. It has one
common scalar amplitude, one fixed circulant five-state kernel, and only an
on/off plus phase choice per fractional coarse edge. It cannot express
edge-specific amplitudes, non-circulant centered kernels, unequal fine-type
weights, or movement of the coarse probabilities.

There is also a large gauge redundancy. Relabeling the five microtypes inside
coarse class `i` by a shift `y_i` sends edge phases to
`x_ij + y_i - y_j` without changing the graphon. Only cycle holonomies are
intrinsic. A spanning-tree gauge fix would remove 191 redundant phase degrees
of freedom, make phase summaries meaningful, and let optimization focus on the
support cycle space. The reported phase histogram is representation-dependent.

For any kernel-library or joint-coarse extension, coefficient reuse is valid
only while `(P, support/type alignment, kernel, type weights)` remains fixed.
Changing `P` changes every unselected-edge motif weight; changing support at a
0/1 boundary changes the factor hypergraph; changing kernel scale changes both
moments and feasible amplitudes. Kernel comparisons therefore need a fixed
normalization (for example a primitive integer representative or a weighted
norm) with amplitude separated from shape, and row-centering must use the
actual type weights rather than an unweighted row sum.

## R5 audit: alternating phase and amplitude

Artifact: `reports/association-scheme-phase-alternating-001/graphon-candidate.json`,
SHA-256 `d93abf5aa5f8b90a98cba93f52ee154a355ae217dc5934ef88954ab6e2b80bcd`.

| Claim | Verdict | Evidence and boundary |
|---|---|---|
| Alternating update semantics | **PASS** | Each round performs one strict phase/support coordinate sweep at the current `q`, recomputes the complete coefficient vector, exhaustively minimizes the resulting exact scalar polynomial over its freshly computed feasible integer interval, then repeats. No coefficient is reused after a state change without recomputation. The fixed coarse parent and kernel justify reuse of the factor hypergraph across rounds. |
| Termination | **PASS as a block-coordinate fixed point** | Round 14 has zero strict phase moves and leaves `q` unchanged at `-7236`; the preceding round had only two moves. Thus it is a strict one-coordinate phase fixed point plus an exact global amplitude minimum for that state. Ties are retained, so this does not exhaust a zero plateau or prove a multicoordinate/global optimum. |
| Boundary semantics | **PASS candidate; future support caveat** | `q=-7236` is the lower feasible boundary, so some active descendants of a `P=51064` block reach probability one. This is valid for the serialized candidate. Any subsequent rule that redefines support as “all fractional fine blocks” changes the support/type state and must rebuild its coefficients; fixed-support recurrence cannot cross that boundary silently. |
| Exact value and independent evidence | **PASS at Level A** | The compressed candidate-bound native structural recount plus Lean exact arithmetic reports red `1012341444814995204119793470917816320000`, blue `1015773545766374662456842546957496320000`, and density `16504842045746825086072884260053/547625059298595101446575784722432`, approximately `0.030138945918374207`. It uses 10 kernels and 28,148 signatures; the trusted native binding and non-kernel-proof caveats remain. |

The main remaining ceiling is now active: the common amplitude is pinned by a
single tight probability class. Further progress inside the same representation
is more likely to require edge/type-specific amplitudes, a different centered
kernel, or movement of the two coarse probabilities than additional scalar
`q` tuning.
