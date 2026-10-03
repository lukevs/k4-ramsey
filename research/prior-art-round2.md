# Prior-art round 2: structured randomized constructions

Search date: 2026-09-27.  This is a literature audit, not a novelty
opinion.  It follows the hypothesis-research source protocol: primary sources
are preferred, search failures are recorded as **not found**, and “not found”
is never promoted to “novel.”  No author or library contact was made.

## Bottom line

1. I did **not** locate a public Feinstein–Even-Zohar preprint, thesis,
   slide deck, exact value, witness matrix, or code.  The two public primary
   announcements say only that the construction is randomized, structured,
   symmetric, and gives `c(4) < 0.030139`.  Those descriptions are compatible
   with our construction and are too coarse to distinguish rediscovery from an
   independent construction.
2. Structured random perturbation is not new to this problem.  Even-Zohar and
   Linial's 2014 arXiv paper gives a more precise account of Thomason's 1997
   last remark: in the product construction
   `M4 tensor K4 tensor ((K3 tensor K3) composition K2)`, replace the `K2`
   factor by a randomly perturbed blow-up of `K2`; they report an improvement
   of less than `10^-7`.  Sperfeld (2011) and Wolf (2010) independently point
   to the same final paragraph as a random perturbation.
3. The exact mechanism and parameter in Thomason's final paragraph remain
   **not found** because the primary 1997 full text was not publicly
   retrievable in this search.  Thus it is not established that his random
   edges were independent, that the perturbation used a single flip
   probability, or that its resulting graphon is literally a special case of
   our matrix.  The overlap at the design-principle level is nevertheless
   strong enough that we should not claim novelty for “softening a structured
   blow-up.”
4. I found no source specifying our exact equal-mass 192-class matrix with
   probabilities `p=51064/65536` and `h=35015/65536`, nor the exact latent
   `+/-` split.  That is a **not-found result**, not evidence of novelty.
5. Our value `0.03013897728988013...` cannot be compared to the unpublished
   Feinstein–Even-Zohar value.  It is only about `2.27e-8` below the rounded
   threshold `0.030139`; a strict announcement below that threshold may be
   arbitrarily lower.

## The construction being compared

The retained local artifact is
[`reports/literature-two-parameter-001/graphon-candidate.json`](../reports/literature-two-parameter-001/graphon-candidate.json).
It specifies an equal-mass 192-step graphon with

```text
p = 51064/65536
h = 35015/65536
F = 515776850799050572477656236153
    / 17113283103081096920205493272576
  = 0.03013897728988013...
```

The symmetric block matrix has values `{0,1,p,h}`, diagonal zero.  Every
class has 12 `p` neighbors, one `h` neighbor, 87 probability-one neighbors,
and 91 off-diagonal probability-zero neighbors.  The 1152 `p` blocks combine
1056 degree-three defect blocks from the 768-vertex Parczyk–Pokutta–Spiegel–
Szabó seed with 96 formerly complete blocks; the 96 `h` blocks are its
degree-two four-by-four half blocks.

Its realization is important for the comparison.  Each unordered pair of
vertices in the corresponding large class blow-up is sampled independently
with the probability of its class pair.  It is not a random choice of a
single finite 192-vertex template subsequently reused by deterministic
blow-up.

The related latent split doubles each coarse class by a sign `s in {+1,-1}`
and replaces

```text
P[i,j] by P[i,j] + epsilon*s*t*C[i,j].
```

Averaging over the independent latent signs removes perturbation-edge sets
having an odd degree at any sampled position.  For `K4`, the nonempty
survivors are its four triangles and three four-cycles, so the objective is
exactly `F0 + A*epsilon^3 + B*epsilon^4`.

## Feinstein–Even-Zohar: exact artifact search

### Located primary announcements

| Date | Source | Exact support | Limitation |
|---|---|---|---|
| 2025-08-07 | [RSA 2025 official program page](https://www.dmg.tuwien.ac.at/rsa2025/) | Talk titled *Improved Constructions for Ramsey Multiplicities*, joint with Chaim Even-Zohar.  The abstract says “random constructions” and describes them as more symmetric and structured than the Parczyk et al. constructions. | No number, formula, slides, witness, or code. |
| 2026-01-21 | [Technion official seminar page](https://math.technion.ac.il/events/noam-feinstein/) | Graduation seminar; MSc advisor Chaim Even-Zohar.  It states `c(4) < 0.030139` and `c(5) < 0.001652`, using randomized, structured, symmetric constructions. | Rounded inequalities only; no exact bound or construction. |

### Searches whose target was not found

The following were checked on 2026-09-27.  A zero result means only that the
named public index did not expose the item.

| Index or location | Query / result |
|---|---|
| [arXiv author search](https://arxiv.org/search/?query=Noam+Feinstein&searchtype=author) and the [official arXiv API](https://export.arxiv.org/api/query?search_query=au:%22Noam_Feinstein%22) | No Noam Feinstein entry, including the alternate spelling `Feinstien`.  Chaim Even-Zohar's public arXiv feed contained no Ramsey-multiplicity preprint. |
| [Crossref REST search](https://api.crossref.org/works?query.author=Noam%20Feinstein&query.title=Ramsey%20multiplicity&rows=20) | No matching publication or DOI. |
| [OpenAlex author search](https://api.openalex.org/authors?search=Noam%20Feinstein&per-page=25) | No exact author record exposing this work. |
| [DataCite search](https://api.datacite.org/dois?query=creators.name:%22Noam%20Feinstein%22%20Ramsey&size=100) | Fuzzy unrelated records only; no exact work. |
| [Chaim Even-Zohar's official site](https://chaime.net.technion.ac.il/) and its linked [public GitHub account](https://github.com/chaim-e) | Nine public repositories were listed; none described this work.  No public code was found. |
| [Technion Library thesis entry point](https://library.technion.ac.il/he/chb/theses/) | The legacy Graduate School abstracts endpoint timed out and the page's “new theses” document link was stale.  Exact-name/title searches did not return a thesis.  The thesis is therefore not retrieved, not shown absent. |
| General exact-title/name/value searches | No public slides, proceedings paper, personal manuscript, data deposit, or code repository was located. |

The exact Feinstein–Even-Zohar construction, value, and relationship to the
192-block artifact therefore remain **unresolved**.

## Closest direct precedent: Thomason's randomized perturbation

### What is supported

The primary publisher record is Andrew Thomason, *Graph products and
monochromatic multiplicities*, Combinatorica 17 (1997), 125–134,
[DOI 10.1007/BF01196136](https://link.springer.com/article/10.1007/BF01196136),
published March 1997.  The public page gives bibliographic data and abstract,
but not the final paragraph.  The
[OpenAlex record](https://api.openalex.org/works/https://doi.org/10.1007/BF01196136)
marks the work closed, reports no open-access URL, and reports no repository
full text.  Thomason's Cambridge publication list links only to the DOI; his
publicly posted 2002 survey describes the graph-product method but the indexed
text did not expose the 1997 referee calculation.

Three scholarly sources identify the final remark:

- [Even-Zohar–Linial, arXiv:1312.1205v2](https://arxiv.org/html/1312.1205),
  submitted 2013-12-04 and revised 2014-10-21, gives the most specific open
  account.  It states that Thomason's core is
  `M4 tensor K4 tensor G18`, with
  `G18=(K3 tensor K3) composition K2`, and that the referee's final remark
  replaces `K2` by a randomly perturbed blow-up of `K2`, gaining less than
  `10^-7`.
- [K. Sperfeld, *On the minimal monochromatic K4-density*,
  arXiv:1106.1030v4](https://arxiv.org/abs/1106.1030), revised 2011-11-18,
  says the final paragraph improves the construction by a tiny random
  perturbation.
- [J. Wolf, *The minimum number of monochromatic 4-term progressions in
  Z_p*](https://intlpress.com/site/pub/files/_fulltext/journals/joc/2010/0001/0001/JOC-2010-0001-0001-a004.pdf),
  Journal of Combinatorics 1 (2010), 53–68, likewise attributes an extremely
  small random-perturbation improvement to the final paragraph.  Her
  [Cambridge thesis](https://api.repository.cam.ac.uk/server/api/core/bitstreams/e551cdb9-d243-40c0-b303-656fe1527492/content)
  repeats the account.

The Even-Zohar–Linial paper also gives the unperturbed repetitive density

```text
R(K4 + A4, M4 tensor K4 tensor G18) = 3769/124416
                                      = 0.0302935313786008...
```

and then distinguishes the referee's randomized improvement.  Its precise
perturbation probability and resulting exact value are not stated.

There is a numerical reporting discrepancy worth preserving rather than
silently resolving: the 2024 Parczyk et al. paper summarizes Thomason's 1997
bound as `c4 < 0.030291`, while the open Even-Zohar–Linial account gives the
unperturbed fraction above and says the randomized gain is below `10^-7`.
Those statements do not transparently yield the same decimal.  The inaccessible
1997 last paragraph is needed to settle whether this reflects different
constructions, rounding, or a secondary-source error.

### Comparison to our 192-block form

| Feature | Thomason 1997, as recoverable | Current 192-block graphon |
|---|---|---|
| Deterministic skeleton | XOR/tensor product of small graphs, including a composed `K2` factor | Four-sheet quotient of the PPSS 768-vertex Cayley seed |
| Random location | A randomly perturbed blow-up replacing the `K2` factor | 1248 fractional inter-class blocks: 1152 at `p`, 96 at `h` |
| Number of exposed probability parameters | Not stated; the description suggests a localized perturbation but does not justify assuming one independent flip rate | Exactly two (`p`,`h`); all other blocks are 0 or 1 |
| Edge dependence | Not stated in the open sources | Independent for every distinct vertex pair conditional on its two classes |
| Exact value / witness | Not publicly recovered | Exact rational value and complete 192-by-192 class matrix retained locally |

The conservative conclusion is:

- **Known overlap:** both place a random perturbation on a highly structured
  deterministic product/blow-up construction.  Thomason predates the current
  work by almost thirty years.
- **Unknown overlap:** without the 1997 paragraph or the unpublished 2025–26
  construction, we cannot say whether either uses our independent-edge
  block model, our exact two probabilities, our 192-class quotient, or the
  same softened block orbit.
- **Novelty consequence:** the broad stochastic-softening idea is prior art;
  the exact two-orbit reduction is merely not located.

## Reconstructing the old perturbation from the open profile algebra

### What can and cannot be classified

Even-Zohar--Linial's account fixes the architecture more tightly than the
phrase "random perturbation" alone.  Write

```text
Q = K3 tensor K3,
A(B) = M4 tensor K4 tensor (Q composition B).
```

Thomason's unperturbed factor is `B=K2`; the referee's suggestion replaces it
by a randomly perturbed large blow-up of `K2`.  Consequently the mechanism is
best classified, on the evidence currently available, as:

1. a two-part latent refinement at the `B` level;
2. embedded inside a composition with `Q`; and then
3. propagated through the two outer XOR/tensor factors.

The source explicitly distinguishes this perturbation from the later
deterministic iterated composition construction.  It is therefore **not**
Even-Zohar--Linial's nested construction.  It is also not merely one scalar
edge probability on the final graph: the product architecture correlates the
role of the perturbed factor with three other small-graph coordinates.

For a literal finite product, the same sampled graph `B` is reused for the
outer coordinates, so identical `B` edges are not resampled independently in
each copy.  If the random perturbation inside the two cells of `B` is i.i.d.
or quasirandom and the blow-up tends to infinity, collisions of sampled `B`
vertices vanish.  Under that additional assumption, its limiting subgraph
densities are equivalently represented by the corresponding two-step
graphon.  The open sources do not state enough to verify that assumption.

In particular, none of the accessible accounts determines whether the
referee proposed:

- symmetric independent flips of all blow-up edges and nonedges;
- adding random edges only within the two independent parts;
- deleting random edges only between the two parts; or
- a degree-constrained or otherwise correlated perturbation.

The classification below is therefore conditional, not an identification of
the inaccessible 1997 mechanism.

### An exact density functional for any replacement factor

Use the sign kernel `S_B(x,y)=(-1)^[xy is an edge of B]`, and for every
subgraph `J` define

```text
tau_J(B) = E[ product over uv in E(J) of S_B(z_u,z_v) ].
```

This is the signed profile `r-hat(J,B)` in Even-Zohar--Linial's notation.  For
one of their five even-edge four-vertex types `H`, let

```text
T_H(B) = r-hat(H, Q composition B).
```

Their composition definition gives the following finite expression, where
`gamma` ranges over all maps from the four labeled vertices of `H` to the
nine vertices of `Q`:

```text
T_H(B) = 9^(-4) * sum_gamma
           product_{uv in E(H), gamma(u) != gamma(v)} S_Q(gamma(u),gamma(v))
           * product_{C in ker(gamma)} tau_{H[C]}(B).
```

Here `ker(gamma)` is the partition into equal-label fibers; a fiber contributes
the signed moment of the subgraph of `H` induced inside that fiber.  Combining
this with the published signed profiles of `M4` and `K4` yields the exact
parameterized repetitive density

```text
Phi(B) = 1/32 * (
             1
             - 1/4  * T_K4(B)
             + 3/16 * T_M4(B)
             + 3/16 * T_C4(B)
             - 3/16 * T_Q4(B)
             + 3/4  * T_V4(B)
         ).
```

For example, the `K4` coefficient is
`r-hat(K4,M4)*r-hat(K4,K4)=(1/2)*(-1/2)=-1/4`; the other four
coefficients follow in the same way from the paper's table.  This formula is
an exact reconstruction of how *any specified* `B` perturbation affects the
bound.  It cannot be reduced to Thomason's numerical polynomial without the
missing perturbation law.

### Diagnostic: symmetric flips are unusually simple

A balanced blow-up of `K2` has a latent sign `s in {+1,-1}` and sign kernel
`s*t`.  In the large-blow-up graphon limit, if every edge and nonedge is
flipped independently with the same probability `delta`, its expected sign
kernel is

```text
S_B(s,t) = theta*s*t,        theta = 1-2*delta.
```

Then `tau_J(B)` is zero unless every vertex of `J` has even degree, and is
`theta^|E(J)|` otherwise.  Applying the finite formula above and using that
the rook graph `Q=K3 tensor K3` has four positive and four negative
off-diagonal signs in each row leaves only one varying contribution: the
all-equal `C4` fiber.  Hence this interpretation predicts

```text
Phi_sym(theta)
  = 3769/124416 + (theta^4-1)/124416
  = (3768 + theta^4)/124416.
```

At `theta=0` the gain from the published unperturbed fraction is
`1/124416`, about `8.04e-6`.  This is much larger than the open account's
phrase "less than `10^-7`."  That does **not** by itself disprove symmetric
flipping: the old remark may merely give a very small, nonoptimized witness.
But if the phrase is meant to describe the optimized gain within the
referee's family, this calculation rules out fully symmetric independent
flips of a balanced `K2` blow-up.  It is therefore a useful test once the
primary paragraph becomes accessible.

### The natural one-sided families

Two other simple meanings of "perturbed blow-up" have sign kernels of the
form

```text
S_B(s,t) = alpha + beta*s*t.
```

Adding within-part edges independently with probability `delta`, leaving all
cross edges present, gives `(alpha,beta)=(-delta,1-delta)`.  Deleting cross
edges independently with probability `delta`, leaving the parts independent,
gives `(alpha,beta)=(delta,1-delta)`.  For either family the exact signed
moments are

```text
tau_J(B) = sum over F subset E(J), all degrees in F even
             alpha^(|E(J)|-|F|) * beta^|F|.
```

Thus the displayed `Phi(B)` becomes an exact polynomial of degree at most six
in `delta`.  Some diagnostic moments are

```text
tau_edge = alpha
tau_two-edge-path = tau_matching = alpha^2
tau_triangle = alpha^3 + beta^3
tau_C4 = alpha^4 + beta^4
tau_K4 = alpha^6 + 4*alpha^3*beta^3 + 3*alpha^2*beta^4.
```

Unlike symmetric flipping, a one-sided perturbation adds a constant component
to the rank-one `s*t` kernel.  That produces lower-degree terms and makes a
tiny interior optimum structurally plausible.  This observation narrows the
most useful next check, but it is not documentary evidence that Thomason used
one of these families.

### Structural comparison with the current refinements

| Construction | Local kernel/refinement | Where it acts | Dependence / propagation |
|---|---|---|---|
| Thomason perturbation, recoverable architecture | Two latent `K2` parts; exact noise law not found.  The simplest candidates are `theta*s*t` or `alpha+beta*s*t`. | One `B` factor inside `(K3 tensor K3) composition B`. | The finite `B` factor is reused across the outer XOR/product coordinates; an i.i.d.-cell large-blow-up limit can be represented by a two-step graphon. |
| Current 192-block `p/h` graphon | Scalar independent-edge softening with values `0,1,p,h`; no extra latent subtype. | 1248 selected class pairs in a 192-class quotient. | Distinct vertex-pair edges are independent conditional on coarse classes; no finite random factor is reused. |
| Binary latent split | Zero-mean rank-one direction `epsilon*s*t*C[i,j]`, preserving every coarse block mean. | A selected support `C` on the nonconstant 192-class parent. | Parity kills all terms except Eulerian perturbation-edge sets; for `K4` this gives only degrees three and four. |
| Retained `r=5` association-scheme refinement | Five microtypes with zero-row-sum cyclic kernel `[-2,3,-2,-2,3]` and an oriented coarse-pair phase. | All 1248 fractional coarse pairs; 960 deterministic fine classes. | A coherent higher-rank refinement; exact density has degrees three through six while every coarse marginal is preserved. |

In kernel language, the simplest Thomason candidates and our binary latent
split both use the rank-one two-point association scheme.  Their placement is
different: Thomason perturbs a `K2` factor and lets composition/XOR products
propagate it, whereas our split perturbs around a nonconstant 192-class parent
while preserving each parent block's mean.  The `r=5` construction is a
higher-rank coherent microtype refinement rather than a two-part edge-noise
model.  These are structural comparisons only; they do not establish novelty
for any of the present constructions.  The exact retained local certificate is
[`reports/association-scheme-r5-001/report.json`](../reports/association-scheme-r5-001/report.json):
five equal microtypes per coarse class, `epsilon=-2611/65536`, exact density
`2816829130796602774891955949737353 /
93461343453626897313548933925961728`, and an independent generic recount.

## Other structured constructions and how they differ

### Even-Zohar–Linial nested composition

[Even-Zohar–Linial](https://arxiv.org/html/1312.1205) define graph composition
`G composition H` and use the deterministic nested sequence

```text
M4 tensor K4 tensor (K3 tensor K3)^(composition n),
```

whose density tends to `1411/46592 = 0.030284168956...`.  This is a
hierarchical 0/1, or random-free, graphon construction.  It is not the same
as assigning independent fractional edge probabilities to a fixed 192-class
partition.  It is nevertheless close prior art for recursively refining a
coarse class by latent substructure.

### Parczyk–Pokutta–Spiegel–Szabó

[The official 2024 article](https://link.springer.com/article/10.1007/s10208-024-09675-6)
records the older product sequence, the Even-Zohar–Linial composition, and
its own deterministic Cayley cores.  Its `K4` theorem is obtained by ordinary
blow-ups of a 768-vertex Cayley graph; it also reports 192- and 384-vertex
cores and asks whether the `K4` optimum might be a finite blow-up.  The paper
does not present the present fractional 192-block stochastic quotient.  Our
matrix is derived from its 768 seed, however, so the combinatorial skeleton is
not independently new.

### General graphon perturbation theory

[Csóka–Hubai–Lovász, *Locally common graphs*,
arXiv:1912.02926](https://arxiv.org/html/1912.02926), submitted 2019-12-06,
uses graphons to study perturbations of the common-graph objective.  It writes
homomorphism densities in a perturbed graphon as a finite polynomial over
subgraphs and recalls that every graphon is the limit of finite graphs.  This
supports two routine parts of our reasoning:

- treating a finite probability matrix as a step graphon whose density is an
  exact polynomial; and
- realizing its value asymptotically by finite simple graphs.

That paper studies perturbations near the constant half graphon and does not
identify our perturbation of a nonconstant PPSS-derived step graphon.

## Latent split: prior-art status

The exact doubled-class rule

```text
P'((i,s),(j,t)) = P[i,j] + epsilon*s*t*C[i,j]
```

was not located in the inspected Ramsey-multiplicity sources.  Its underlying
ingredients are standard:

- splitting a step-graphon class into latent subtypes is an ordinary step
  refinement;
- `s*t` is a rank-one sign kernel;
- averaging independent Rademacher signs kills monomials with odd degree at
  any sign variable, a standard Fourier/parity argument; and
- graphon homomorphism densities have standard subgraph-polynomial
  perturbation expansions.

The particular observation that only triangles and four-cycles survive for
the `K4` edge set, and the use of that identity on this specific 192-class
base, were **not found**.  This is not enough to call them novel.  Moreover,
Even-Zohar–Linial's deterministic nested composition already demonstrates
that refining a coarse class by hidden internal structure can improve this
same objective, even though its mechanism differs from the balanced sign
split.

## Decision for the research loop

1. Freeze all claims that the stochastic 192-block idea or latent split is
   novel.  Use “our current construction” or “not located in the inspected
   sources.”
2. Treat Thomason's randomized blow-up as required prior art in every future
   explanation of probability softening.
3. Keep the 192-block candidate as a valid exact bound independent of novelty;
   its mathematical certificate does not depend on whether it was rediscovered.
4. Do not claim a record relative to Feinstein–Even-Zohar until their exact
   value is public.  The rounded `0.030139` comparison is insufficient.
5. The highest-value future literature check is the public release of the
   Feinstein MSc thesis or joint preprint.  A lawful public copy of Thomason's
   1997 final page would also settle the old perturbation's precise probability
   model.  No author contact is authorized for this lane.

## Source ledger

| Source | Type | What was actually used |
|---|---|---|
| [RSA 2025 official site](https://www.dmg.tuwien.ac.at/rsa2025/) | Primary announcement | Title, date, authorship, random/structured description. |
| [Technion seminar announcement](https://math.technion.ac.il/events/noam-feinstein/) | Primary announcement | Rounded `c4` and `c5` bounds, randomized/structured description, thesis context. |
| [Thomason 1997 publisher record](https://link.springer.com/article/10.1007/BF01196136) | Primary bibliographic record; full text unavailable | Publication identity and abstract only. |
| [OpenAlex record for Thomason 1997](https://api.openalex.org/works/https://doi.org/10.1007/BF01196136) | Scholarly index | Closed-access status, no OA URL, no repository full text as of the search date. |
| [Thomason's public paper list](https://www.dpmms.cam.ac.uk/~agt2/) and [2002 survey](https://www.dpmms.cam.ac.uk/~agt2/simple.pdf) | Author-hosted primary index/survey | Confirms the product-method exposition is author-hosted; no open copy or indexed reproduction of the 1997 final calculation was located. |
| [Even-Zohar–Linial 2014 arXiv](https://arxiv.org/html/1312.1205) | Primary research paper | Exact product/composition definitions, unperturbed fraction, and specific report of the perturbed `K2` blow-up. |
| [Sperfeld 2011 arXiv](https://arxiv.org/abs/1106.1030) | Primary research paper | Independent attribution of random perturbation to Thomason's final paragraph. |
| [Wolf 2010 paper](https://intlpress.com/site/pub/files/_fulltext/journals/joc/2010/0001/0001/JOC-2010-0001-0001-a004.pdf) | Primary research paper | Independent attribution and surrounding product construction. |
| [Parczyk et al. 2024/2025](https://link.springer.com/article/10.1007/s10208-024-09675-6) | Primary research paper | Historical construction taxonomy, deterministic Cayley/blow-up method, numerical summary, open questions. |
| [Csóka–Hubai–Lovász 2019](https://arxiv.org/html/1912.02926) | Primary research paper | Standard graphon realization and perturbation-polynomial framework. |
