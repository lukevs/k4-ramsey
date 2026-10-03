# Clebsch formations: targeted primary-literature review

Date: 2026-09-29 (New York). Literature-only review; no experiments, additional agents, remote compute, or changes to experiment/state files. Read `clebsch-bowl-focused-tests.md`, `round5-C1.md`, the prior September 27 literature notes, and the Clebsch/Hadamard comparison. The focused-tests correction supersedes C1's claim that diamonds alone are the remaining lever. The operator bound `||D_uv||op <= min(p_uv,1-p_uv)` is supplied by the main thread, not a result discovered in this review.

**Most useful next directions:** (1) apply contraction bounds to whole families of overlapping words, not only individual path norms; (2) try admissible orthogonal switches that preserve every triangle/C4 trace and isolate changes in T5/T6; (3) use the six-vertex Clebsch reconstruction pattern to organize rooted constraints. No inspected theorem supplies a lower bound matching the B192 refinement family.

## 1. Lovász: signed-kernel inequalities, with a precise transfer boundary

Primary source: László Lovász, [*Subgraph densities in signed graphons and the local Sidorenko conjecture*](https://arxiv.org/pdf/1004.3026). Inspected §§2.2–2.4, especially Lemma 2.3, equation (4), Lemma 2.6, and Lemma 2.12.

**Verified result.** Partially labelled graphs multiply by gluing their labelled vertices. Equation (4) is Cauchy–Schwarz for the resulting rooted functions. Lemma 2.3 gives a product-integral bound when each variable occurs in at most two factors. Lemma 2.12 makes even-cycle densities nonnegative, decreasing and log-convex for a single bounded signed kernel.

**Direct transfer.** Rooted-function Cauchy–Schwarz works for our different bridge kernels on different edges: it is an integral inequality, independent of their names. It supports joint moment matrices with shared entries across different decompositions of the same decorated motif.

**Obstruction.** The single-kernel even-cycle statement does NOT make `tr(D_ab D_bc D_cd D_da)` nonnegative. A mixed cycle is not a Schatten fourth power. Likewise, a bipartite density-domination theorem cannot simply be applied to a diamond or K4, or to differently decorated edges. Keep the actual repeated coarse classes and independent latent variables.

**Next test — analytic, then an SDP redundancy check.** For any common prefix `L=D_ac` and compatible suffix words `X_i : H_b -> H_c`, impose the entire matrix inequality

```
[q_ac^2 <X_i,X_j>HS - <L X_i,L X_j>HS]_(i,j) >= 0,
q_ac = min(p_ac,1-p_ac).
```

This is our direct derivation: evaluate its quadratic form on `X=sum_i alpha_i X_i` and use `||LX||HS <= q_ac ||X||HS`. It strengthens separate diagonal estimates only if the cross-word entries are present and shared consistently. Start with one favorable overlap from the current solution; if the needed suffixes require higher-degree moments, record that cost explicitly. Do not add a nominally new constraint already implied by existing Gram/localizer blocks.

## 2. Godsil–McKay: switching that can isolate the non-cycle moments

Primary source: C. D. Godsil and B. D. McKay, [*Constructing cospectral graphs*, Aequationes Mathematicae 25, 257–268](https://users.cecs.anu.edu.au/~bdm/papers/GodsilMcKayCospectral.pdf). Inspected Construction 2.1 and Theorem 2.2, pp. 258–259. The scan labels the volume 1982; McKay's publication list dates publication 1983.

**Verified result.** An equitable switched part, with external vertices having zero, half, or all its vertices as neighbors, permits complementing the half-neighborhoods. The original and switched graphs, and their complements, are cospectral. The proof uses the orthogonal reflection `Q=2J/m-I`, fixing the constant vector.

**Concrete adaptation, derived here.** In an equal-mass finite latent model, choose orthogonal `Q_u` with `Q_u 1=1`, and replace

```
D_uv by Q_u D_uv Q_v^T.
```

Margins and transpose consistency survive. Adjacent factors telescope around every closed walk, so **each individual triangle and C4 trace is unchanged**, including backtracking walks. Consequently T3 and T4 are exactly fixed at unchanged coarse means. Hadamard multiplication is not orthogonally equivariant, so T5 and T6 need not be fixed. This is stronger and more relevant than preserving only the spectrum of one assembled graph.

**Obstruction.** Orthogonal conjugation does not preserve entrywise probability boxes. The GM half-neighborhood hypotheses do not automatically hold for P/H bridges. Permutation matrices only relabel latents and preserve everything. Applying `2J/m-I` to every whole latent space also gives a trivial transformation of row/column-zero kernels: both sides act as minus identity. Use a proper subset or a genuinely different constant-fixing orthogonal transformation, and reject any box violation. Weighted latent spaces require weighted orthogonality.

**Next test.** On an existing finite refinement, examine one proper latent subset at one coarse vertex and its reflection, updating all incident bridges together. First check all asymmetric boxes; only if admissible, compare the exact T5+T6 change. Cycle terms must agree identically. This tests a non-cycle mechanism without sacrificing the attained triangle/C4 tradeoff; no gain is predicted by the switching theorem.

## 3. Pikhurko–Vaughan: an actual Clebsch stability proof and its reconstruction gadget

Primary source: Oleg Pikhurko and Emil R. Vaughan, [*Minimum Number of k-Cliques in Graphs with Bounded Independence Number*](https://arxiv.org/pdf/1203.4393), published 2013. Inspected Theorems 1–2, §4.2, equation (21), Claim 15, and the concluding discussion.

**Verified result.** Their problems for `(k,l)=(6,3),(7,3)` have extremal limits given by uniform expansions of the complement of the triangle-free Clebsch graph. Equivalently, in the complementary convention these minimize independent 6/7-sets in triangle-free graphs. Claim 15 uses an induced `C5` plus an isolated vertex. Its embedding into Clebsch is unique up to automorphism, and its six vertices distinguish all sixteen vertices by their neighborhoods. A further deletion property permits reconstructing pairs from five of the anchors.

**Transfer.** This supplies an explicit rooted type, not just a visually suggestive SRG. In the paper's even-weight five-bit coordinates the anchor is

```
{00000, 00011, 01100, 10001, 00110, 11000}.
```

**Obstruction.** Their sharp induced-subgraph lists and forbidden-triangle condition drive the stability proof. B192's objective has neither that forbidden condition nor their known sharp certificate. The lemma identifies coarse Clebsch positions, not arbitrary hidden latent states; it cannot itself tighten moments once all coarse positions are already recorded.

**Next test.** Use this anchor to classify one H-spine's P-path attachments under its stabilizer, retaining which anchors distinguish the two wings. Check whether the current symmetry reduction has lost a joint rooted relation between overlapping paths. Add only a demonstrably missing shared identity/PSD block. If no information was lost, use the gadget only for certificate organization.

## 4. Csóka–Hubai–Lovász: concentration and tensor powers, and the quantifier trap

Primary source: Endre Csóka, Tamás Hubai and László Lovász, [*Locally common graphs*](https://arxiv.org/pdf/1912.02926). Inspected Proposition 2.3 and the proof of Theorem 3.1, especially equation (10).

**Verified result.** Proposition 2.3 distinguishes a uniform perturbation radius over all kernels from a radius depending on each fixed direction. Theorem 3.1 states that no graph containing K4 is locally common. Its proof preserves balanced kernels under tensor powers and under concentration into a square of measure `delta^2`. Motif densities then become respectively `t(F,U)^m` and `delta^v(F)t(F,U)`.

**Direct transfer, derived for this family.** Concentrate every bridge's kernel on the same measure-delta latent subset at every coarse class. Row and column means remain zero, and the boxes remain valid. Our expansion becomes

```
Delta F(delta) = delta^3 T3 + delta^4 (T4+T5+T6).
```

This remains true with repeated coarse indices because positional latents are independently sampled. Concentration separates triangle contributions from four-vertex contributions, but cannot separate C4, diamond and K4 contributions from each other.

**Obstruction.** Their base is the constant half graphon, whereas ours is B192. Their local-commonness conclusion says nothing about this bowl. Tensoring raw asymmetric-box D kernels can violate a bridge's upper bound; amplitude feasibility must be rederived. No uniform stability statement follows from checking finitely many fixed directions.

**Next test.** Before materializing any new graphon, minimize the displayed one-variable polynomial on `[0,1]` using an already verified T3/T4/T5/T6 decomposition. It can reject concentration of that particular refinement analytically. Keep this distinct from tensor powers and from changing coarse means.

## 5. Kiem–Pokutta–Spiegel: two different joint arrangements of Clebsch relations

Primary source: Aldo Kiem, Sebastian Pokutta and Christoph Spiegel, [*The Four-Color Ramsey Multiplicity of Triangles*](https://arxiv.org/pdf/2312.08049), 2023 preprint. Inspected Theorems 1.1 and 2.3 and §2.1. The Clebsch identification is independently stated in Pikhurko–Vaughan's concluding discussion, not explicitly named in this PDF.

**Verified result.** Four-color triangle multiplicity is asymptotically `1/256`. Near-extremal colorings are close to the described family based on the two triangle-free three-colorings of K16, with a fourth color inside parts and specified triangle-preserving recolorings. Pikhurko–Vaughan notes that each color class in either K16 coloring is Clebsch.

**Transfer.** Two joint placements of three isomorphic regular relations can differ even though each relation separately looks identical. This is a concrete reason to test mixed-relation motif counts rather than relying on the SRG parameters or individual spectra. Do not assume either coloring automatically gives the same association scheme or the same mixed intersection numbers.

**Obstruction.** Four-color triangles are a different objective. Merging colors creates monochromatic triangles, so the theorem yields no two-color K4 bound. Nor does a scalar multiple of one regular relation exhaust its joint structure.

**Next test.** If an additional latent-family test is wanted, compare the two K16 relation triples in exactly the same ansatz: `D_e=sum_r a_(e,r)(A_r-5J/16)`, with symmetric relation matrices and coefficients satisfying each bridge's box. First compare the exact mixed triangle/C4/diamond signatures at matched coefficients. Stop if this restricted ansatz cannot distinguish the two arrangements; individual Clebsch spectra cannot select between them.

## 6. PPSS and the foundational Thomason/Jagger lineage: what is actually verified

Primary source: Parczyk–Pokutta–Spiegel–Szabó, [*New Ramsey Multiplicity Bounds and Search Heuristics*, v3](https://arxiv.org/html/2206.04036v3). Inspected §§3.3.1, 4.2, 5.1 and 5.3.

**Verified result.** §3.3.1 gives the historical XOR-product construction `K4 XOR M4 XOR G18` and explains multiplicative signed-density coordinates. §5.1 asks for structural understanding of the new Cayley generating sets. §5.3 reports inferior quality/time for their tested neural cross-entropy approaches versus annealing/tabu; it is a limited empirical comparison, not a universal impossibility result.

Foundational primary landing pages inspected: Jagger–Šťovíček–Thomason, [*Multiplicities of subgraphs* (1996)](https://link.springer.com/article/10.1007/BF01300130), whose abstract states uncommonness of every graph containing K4; Thomason, [*Graph products and monochromatic multiplicities* (1997)](https://link.springer.com/article/10.1007/BF01196136), whose abstract explains the product family containing the earlier constructions. Their full texts were not accessible in this review, so no original section/page claim about Clebsch is asserted.

**The Clebsch connection is algebraic, not pictorial (derivation here).** Take `K4` as the Cayley graph on `F2^2` with all nonzero generators, and `M4` on another `F2^2` with generator `b1`. The complement of their XOR product has five generators

```
(0,b2), (0,b1+b2), (a1,b1), (a2,b1), (a1+a2,b1).
```

Their only nonempty linear dependence is the sum of all five. A change of basis therefore identifies them with the five weight-four generators in the even-weight five-bit Clebsch model of source 3. Thus `K4 XOR M4` is the **complement** of the degree-five Clebsch graph. This verifies the structural appearance in the product lineage without pretending the paywalled papers were read. It does not show that their complete construction equals B192.

**Obstruction.** XOR products act on whole signed kernels; our additive, support-restricted, unequal-mean bridges are not automatically closed under them. Spectral/factor descriptions alone miss mixed Hadamard moments. The old literature notes already cover voltage holonomy and iterative products; another blind small-factor sweep would repeat those directions.

**Next test.** Use the explicit five-generator correspondence as a normalization audit for any claimed product decomposition of the twelve-copy quotient. Require entrywise agreement of the hard relations and both fractional types before importing a product density formula. This is a representation check, not a new optimization campaign.

## Handoff priorities and limits

1. **Main-thread inequality work:** source 1's common-prefix contraction matrix, with a check for redundancy and for the extra moments it needs. The new operator bound is especially valuable here because it controls all linear combinations simultaneously.
2. **Most discriminating later construction test:** source 2's admissible proper-subset switch. It preserves T3/T4 exactly and asks whether T5/T6 can move usefully. This connects spectral switching to the actual unresolved motifs rather than to their appearance.
3. **Cheap analytic check:** source 4's concentration polynomial. No new graph construction is needed to decide whether concentrating an existing refinement helps.
4. **Secondary:** source 3's anchored consistency organization; source 5's two joint Clebsch arrangements if current scalar/abelian families appear restrictive.

All tests above are proposals, not runs. No novelty, universal stability, matching lower bound, or global optimality is claimed. In particular, the presence of Clebsch blocks does not transfer a stability theorem from another objective, and preserving spectra does not preserve the full K4 density.
