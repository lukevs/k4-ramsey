# Adjacent structural mechanisms beyond centered perturbations

Search date: 2026-09-27.  This pass used no CPU experiments.  Its purpose is
to identify construction families capable of changing the coarse template or
its recursive organization, not to tune another small perturbation of the
current 192-block graphon.  Sources are primary where available; formulas and
tests labeled as ours are derivations, not claims found in the cited papers.

## Evidence boundary on the January announcement

The [Technion announcement](https://math.technion.ac.il/events/noam-feinstein/)
states only

```text
c(4) < 0.030139
```

and describes the constructions as randomized, structured, symmetric, and
human-friendly.  The [RSA 2025 program](https://www.dmg.tuwien.ac.at/rsa2025/)
confirms the earlier talk but supplies no more numerical precision.  No public
exact value or construction was located in the prior-art pass. The user clarified
that the much lower result they heard about is unpublished and distinct from
the January benchmark; no value or source is available. That report is motivation,
not verified evidence. The qualitative announcement is compatible with several mechanisms
below but does not identify any of them.

## M-ADJ-1: a randomized Hamming-scheme kernel on the PPSS groups

### Primary precedent

[Franek--Rödl (1993), author-hosted paper](https://www.cas.mcmaster.ca/~franek/journals/erdos-2569.pdf)
put the vertices at the subsets of an `m`-element set, equivalently
`F_2^m`, and join `x,y` according to whether the Hamming weight
`|x xor y|` lies in a selected set `F`.  Their best reported binary rule at
`m=10` is

```text
F = {1,3,4,7,8,10}.
```

They count cliques by classifying the seven membership regions of three
subsets.  Thus their construction already contains the exact joint-distance
census needed below; it was not a generic graph search.

[Parczyk--Pokutta--Spiegel--Szabó (2024/25)](https://link.springer.com/article/10.1007/s10208-024-09675-6)
search binary Cayley generator sets and find their strongest `K4` cores in
groups of order `3*2^k`, including `Z_3 x F_2^k`.  They report that their
binary searches pushed the Franek--Rödl approach to what they found feasible,
but also explicitly ask for a structural generalization of their generating
sets to arbitrary larger `k`.  I did **not** locate a source optimizing the
continuous randomized distance-shell family below.  That is a not-found
result, not a novelty claim.

### Transferable construction

Let the equal-mass coarse classes be

```text
V_k = Z_3 x F_2^k.
```

For two classes whose difference is `(a,z)`, put an independent red edge
between each pair of blown-up vertices with probability

```text
q[a, wt(z)].
```

Undirectedness imposes `q[1,d]=q[2,d]`, so there are only `2(k+1)` parameters:
one row for zero `Z_3` difference and one for nonzero difference.  The entry
`q[0,0]` is the within-class probability.  Restricting every parameter to
`{0,1}` recovers only the shell-invariant subfamily of Cayley cores; it does
**not** recover an arbitrary PPSS generator set and should not be assumed to
contain their best graph. Ignoring the `Z_3` coordinate recovers the
Franek--Rödl Hamming-shell family, provided its published red-clique blow-up
convention is retained: the distance-zero parameter is `q[0]=1`, even though
zero is not listed in its generator set. Allowing probabilities changes
the construction domain to a structured stochastic block graphon rather than
rounding a deterministic generator set.

The exact monochromatic density is

```text
F_k(q) = |V_k|^(-3) * sum_{u,v,w in V_k}
           [ product over ij of q[type(x_i-x_j)]
             + product over ij of (1-q[type(x_i-x_j)]) ],

where (x_0,x_1,x_2,x_3)=(0,u,v,w).
```

This is an exact graphon density, including repeated coarse indices.  Its
finite-graph realization uses fresh independent edges between distinct
blow-up vertices; it does not reuse one sampled edge per coarse pair.

### Why the exact evaluator is cheap

For each binary coordinate, record the three-bit column
`(u_r,v_r,w_r) in {0,1}^3`.  Let `n_b` be the count of each of the eight
column types.  The six binary Hamming distances in the displayed objective
are linear forms in the eight counts, and a count vector has multiplicity

```text
k! / product_b n_b!.
```

There are only `binom(k+7,7)` such count vectors and 27 assignments of the
three `Z_3` coordinates.  Consequently an exact objective/gradient evaluator
needs

```text
27 * binom(k+7,7)
```

states: `173745` at `k=8`, the dimension of the published 768-vertex core.
This is the direct probabilistic analogue of Franek--Rödl's seven-region
count, derived here for the six distances of a four-vertex sample.

### Cheapest discriminating test

1. Validate the joint-distance histogram against literal enumeration only at
   `k<=4`.
2. At `k=6,7,8`, evaluate the exact gradient at (a) the best available binary
   shell rule and (b) the best shell projection of the PPSS generator set.
   Here projection means averaging the PPSS indicator inside each
   `(Z_3`-difference orbit, Hamming-weight`)` class; it changes the graph and
   is only a stochastic initialization, not an equivalent representation.
3. If no coordinate or small joint direction is improving, retire this
   distance-shell library.  If there is a direction, optimize the
   `2(k+1)`-variable exact polynomial and independently recount the retained
   rational point.
4. Only after a gain, refine the relation classes by one quadratic-form or
   code-syndrome invariant.  Do not start with arbitrary block probabilities.

**Prediction.** Moving an entire relation class changes exponentially many
coarse pairs coherently and can produce a density change much larger than a
single latent-mode correction.  At least one `k` in `{6,7,8}` has a negative
feasible shell direction after continuous probabilities are admitted.

**Falsifier.** No negative feasible gradient/joint direction at all tested
binary shell rules, followed by exact failure of the small continuous
optimizer to beat the current 192-block value.  This rejects the stated
association scheme, not general structured random graphons.

**Important mismatch.** PPSS's statement that earlier approaches appeared
exhausted concerns their implemented binary searches and available resources.
It is evidence against another unrestricted binary generator sweep, but not a
published impossibility result for fractional relation probabilities.

## M-ADJ-2: detect a factor, then optimize its stationary profile

### Primary precedent

[Even-Zohar--Linial, arXiv:1312.1205v2](https://arxiv.org/html/1312.1205)
obtained the historical improvement by recognizing

```text
G18 = (K3 tensor K3) composition K2
```

inside Thomason's product and replacing the terminal factor by an iterated
composition.  Their Lemma 6 makes the four-vertex profile of
`G composition H` a bilinear function of the small outer profile and the
repetitive profile of `H`.  With the outer graph fixed, this is a finite linear
operator; its stationary vector is the exact limiting profile of the nested
construction.  Their concrete calculation reduces from 64 labeled graphs to
the 11 unlabeled four-vertex types.

PPSS explicitly says that this remains the only known `c4` construction in
their survey that is not a standard finite-core blow-up.  Their paper also
observes that the roles of the outer `K4 tensor M4` factors remain unclear and
that identifying suitable decompositions inside larger XOR products is
computationally challenging.  Thus the transferable lesson is not "try the
same Q9 nesting again"; it is **factor a strong modern core first, and only
then form the exact profile operator**.

### Transferable construction

Let a good Cayley or step template admit an exact equitable factorization into
outer cells, with one of a small set of internal kernels used in each cell.
Replace those internal kernels recursively.  In the one-type case the labeled
four-profile satisfies

```text
r_(n+1) = L_G r_n,
```

where `L_G` is the composition operator determined by the outer graph `G`;
the limit is a stationary vector of `L_G`.  For several cell/orbit types, stack
their profiles and use a graph-directed block operator.  An outer XOR factor,
when present, acts diagonally on the signed profile and can be applied after
the stationary solve.

This can alter every depth of the construction and therefore is not limited to
the cubic/quartic scale of one centered latent split.  It also avoids
materializing exponentially many refined classes.

### Cheapest discriminating test

1. On the stored 192- and 768-class Cayley templates, enumerate only low-index
   subgroups and their cosets.  For each, record whether every coset-pair block
   is constant, belongs to a small repeated relation library, or is genuinely
   irregular.
2. For each exact factor, construct its 11-state four-profile transfer matrix
   and compare the one-level profile with the stationary profile.  For a
   near-factor, replace each repeated block orbit by its exact probability and
   run the same test as a stochastic graphon operator.
3. Advance only factors whose stationary `K4 + A4` coordinate is lower.  A
   generic recursive microkernel search should not precede this factor audit.

**Prediction.** At least one low-index factor of a modern `3*2^k` template has
a repeated internal profile whose stationary substitution improves its
one-level realization.  A gain need not use the historical Q9 kernel.

**Falsifier.** No low-index subgroup produces a small exact/near relation
library, or every resulting stationary profile is no better than one level.
This retires recursion through the tested factors, not arbitrary graph-directed
substitution.

### Relation to current hypotheses

The existing `H-ROOT-004` already proposes a general local-profile operator.
The literature changes its first action: search for an **actual factorization
of the successful modern template** before optimizing abstract microkernels.
That mirrors the step that made the Even-Zohar--Linial improvement work and
provides a much cheaper falsifier.

## Reserve mechanism: learn a dimension-stable generator rule

This is a reserve if M-ADJ-1's coarse relation classes are too restrictive.
Even-Zohar--Linial explain that Thomason's original `F_2^{2t}` generators arise
from quadratic forms equivalent to Hamming-weight classes modulo four.  PPSS
asks whether its good `Z_3` by `2`-group generators can be generalized to
arbitrary dimension.  The direct test is to compute the Walsh spectrum of each
`Z_3` section of the known generator indicator and ask whether most energy is
carried by low-degree characters or a few quadratic/code-syndrome orbits.  If
so, enumerate the resulting small truth table at the known dimension before
extrapolating it.  A flat spectrum or a rule that loses the known density at
`k=8` immediately falsifies this route.  This is preferable to another blind
generator-bit search, but it is lower priority than the exact shell test.

## Recommended order

1. Run M-ADJ-1's exact gradient screen first.  It is a genuinely new coarse
   stochastic family relative to the current `p/h` quotient and has the
   smallest implementation burden.
2. In parallel with no numerical optimization, perform M-ADJ-2's subgroup
   factor audit.  Build a transfer operator only for a factor that actually
   appears.
3. Use the generator-rule reserve only if the shell screen fails but the known
   PPSS generators show concentrated Walsh structure.

None of these mechanisms implies a record, novelty, or the unpublished January
construction.  Each has an explicit restricted falsifier and an independent
exact recount path.

## Source ledger

| Source | Exact support used |
|---|---|
| [Franek--Rödl 1993 author-hosted PDF](https://www.cas.mcmaster.ca/~franek/journals/erdos-2569.pdf) | Power-set/Hamming-distance Cayley family, best binary configurations, seven-region clique census, and exhaustive shell search through dimensions 10--14. |
| [Even-Zohar--Linial 2014 arXiv](https://arxiv.org/html/1312.1205) | Tensor/XOR spectral multiplication, graph composition, finite local-profile transfer operator, and stationary-profile evaluation of iterated composition. |
| [PPSS official article](https://link.springer.com/article/10.1007/s10208-024-09675-6) | Strong `3*2^k` Cayley cores, limitations of earlier binary/product searches, and the explicit open direction of finding dimension-stable generator structure. |
| [Technion January 2026 announcement](https://math.technion.ac.il/events/noam-feinstein/) | Rounded inequality and qualitative randomized/structured/symmetric description only. |
| [RSA 2025 program/abstract](https://www.dmg.tuwien.ac.at/rsa2025/) | Earlier public announcement; no exact bound or construction. |
