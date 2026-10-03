# Adjacent algebraic mechanisms: recovery, four-type counts, and nonabelian kernels

Search date: 2026-09-27. This pass used no experiment CPU. It targeted the
active canonical-quotient, quadratic-relation, nonabelian-Cayley, and group
recovery lanes. Statements labeled as transfers or derivations below are ours;
they are not attributed to the cited papers.

## 1. Exact Cayley recovery is a regular-subgroup problem

[Sabidussi's theorem, restated as Theorem 2.3 in this primary research
article](https://link.springer.com/article/10.1007/s10801-018-0860-0), says
that a graph is Cayley if and only if its automorphism group contains a subgroup
acting regularly on the vertices. The same proof applies to an edge-colored or
weighted complete graph when `Aut` is restricted to permutations preserving
every color/weight.

For a weighted matrix `P`, an exact certificate therefore consists of:

1. a set `R` of `n` entrywise-verified automorphisms of `P`;
2. identity, closure, and distinct images of a chosen base vertex (equivalently,
   a free transitive action);
3. the induced bijection between vertices and elements of `R`; and
4. an inverse-symmetric connection function `f` satisfying
   `P[r(v0),s(v0)] = f(r^-1 s)` for every pair.

This certifies *a* Cayley labeling of the archived weighted graph. It does not
prove uniqueness or recover the historical authors' labeling.

For the proposed `F_2^6 semidirect C_3` identification, the certificate must
add an elementary-abelian normal subgroup `N` of order 64, an element `c` of
order 3 normalizing `N`, and the explicit conjugation matrix `T` on `N` with
`T^3=I`. An order distribution or spectrum is not enough.

There is also an important negative-claim boundary. Selecting one arbitrary
automorphism carrying a base vertex to each target and finding that these 192
choices are not closed does **not** prove that no regular subgroup exists; a
different transversal can close.

### Cheapest test

Compute the color-preserving automorphism group of the exact quotient. A
positive regular subgroup gives the certificate above. Divisibility, degree,
spectrum, and transitivity are filters only. Explicitly verify the proposed
generators and all matrix entries after labeling.

### Concrete recovery target from the completed quotient reports

The exact runs found a transitive action of degree 192 and a point stabilizer
of order 240, so the full color-preserving group has order `192*240=46080`.
This is the order of the hyperoctahedral group

```text
W(B6) = C_2^6 semidirect S_6.
```

Moreover, the measured point-stabilizer order distribution

```text
1:1, 2:51, 3:20, 4:60, 5:24, 6:60, 10:24
```

is exactly the distribution in `C_2 x S_5`. This is a strong recovery target,
not an isomorphism proof. An exact next test is to generate the full
permutation group, recover its largest normal elementary-abelian 2-subgroup
and test that it has order 64, then certify the quotient as `S_6`. If this
normal subgroup has three orbits of size 64, search an order-three element
cycling them; together they may form the desired regular
`C_2^6 semidirect C_3`. Every regularity and matrix-entry gate above still
applies.

There is a concrete reason not to expect this optimistic orbit pattern. In the
natural degree-192 coset action of `W(B6)` with stabilizer
`<e_i> x S_5`, points can be represented as

```text
(i, v modulo <e_i>),  i in {1,...,6},
```

giving six fibers of size 32. The standard normal `C_2^6` has point stabilizer
`<e_i>` on the `i`th fiber and is therefore not semiregular. An order-three
coordinate permutation has cycle type `3+1+1+1` or `3+3`, producing orbit
unions `96+32+32+32` or `96+96`, not one orbit of size 192. If the recovered
group and stabilizer embedding are this natural action, the obvious normal
`C_2^6 semidirect C_3` is obstructed and the Schreier family below is a more
faithful description. This does not exclude a different, nonnormal
elementary-abelian subgroup; it makes its explicit recovery essential.

## 2. Reserve family: stochastic Schreier/orbital kernels

The same [Sabidussi/Lovasz discussion](https://link.springer.com/article/10.1007/s10801-018-0860-0)
describes how a vertex-transitive graph with automorphism group `G` and point
stabilizer `H` is related to a Cayley cover. This suggests a family that remains
available when the action is transitive but not regular.

Let the coarse space be `X=G/H`. Pair orbitals are indexed by double cosets
`H\G/H`. Assign a probability `p_D` to each orbital, with
`p_D=p_(D^-1)` for undirectedness and a separate diagonal-orbital probability.
This is a stochastic Schreier/orbital graphon. It strictly generalizes Cayley
kernels, which are the case `H=1`.

The exact objective still fixes `x0=H` and sums over the other three cosets,
with denominator `|X|^3`. The cheapest pilot is to take a transitive subgroup
already found in the 192-quotient automorphism group, construct its
point-stabilizer orbitals, verify that the archived relation matrix is constant
on them, and optimize one probability per inverse-paired orbital. When
`H` is nontrivial the result must be called Schreier/coset, not Cayley.

## 3. Only three `F_2^6 semidirect C_3` action types

This is an elementary rational-canonical-form reduction. Over `F_2`,

```text
x^3 - 1 = (x+1)(x^2+x+1)
```

is square-free. Hence an order-three matrix in `GL(6,2)` is semisimple. Up to
`GL(6,2)` conjugacy every nonidentity action is

```text
T = C^(direct sum r) direct sum I_(6-2r),  r in {1,2,3},
C = [[0,1],[1,1]].
```

The actions `T` and `T^-1` are conjugate, so there are only three nontrivial
semidirect-product action types to screen. Using coordinates `(v,a)`,

```text
(v,a)(w,b) = (v + T^a w, a+b),
(v,a)^-1   = (T^(-a)v, -a).
```

Every `(v,0)` is self-inverse, while `(v,1)^-1=(T^2v,2)`. Thus a full
inverse-symmetric stochastic Cayley kernel has

```text
1 identity parameter + 63 involution parameters + 64 coset-pair parameters
= 128 parameters
```

for each action type.

There is a smaller characteristic-orbit pilot. The module decomposes as
`F_4^r direct sum F_2^f`, `f=6-2r`, and the centralizer is
`GL(r,4) x GL(f,2)`. For `r=3`, this yields one nonzero normal-subgroup orbit
and one inverse-paired outer-coset orbit: two off-identity parameters. For
`r=1,2`, zero/nonzero status in the two isotypic components gives three normal
orbits, and the fixed-component status gives two outer types: five
off-identity parameters. These are strict invariant subfamilies; their failure
does not reject the 128-parameter kernel.

## 4. Subgroup clustering is a concrete nonabelian warning

[Conlon--Fox--Pham--Yepremyan, *On the clique number of random Cayley graphs
and related topics*](https://arxiv.org/abs/2412.21194), defines the random
Cayley model by independently selecting inverse pairs. It proves a general
`O(log N log log N)` clique bound, but also explains that for `F_2^n` the extra
`log log N` is genuine: the many subgroups are the dominant clique source.
If all nonidentity elements of a subgroup are selected, that subgroup is a
clique.

The proposed semidirect group remains nonabelian but still contains the normal
elementary-abelian subgroup `V=F_2^6`, so this obstruction does not disappear.
The paper concerns clique number, not monochromatic `K_4` density, and supplies
no bound on our objective. Its transferable diagnostic is nonetheless exact:
partition the objective contribution from samples lying in a common affine
`V`-coset by the binary rank of their three translated differences. Rank at
most two identifies four-samples contained in an affine 2-flat; rank three
identifies an affine 3-flat. If these strata dominate, fractional softening of
the 63 involution relations is more motivated than merely changing the
order-three action.

## 5. Why small-noise optimization at one half is not a falsifier

[Csoka--Hubai--Lovasz, *Locally common graphs*](https://pmc.ncbi.nlm.nih.gov/articles/PMC10087361/),
formalizes two different local notions. `K_4` is weakly locally common but not
locally common. Concretely, for every fixed bounded kernel direction `U` there
is a direction-dependent `epsilon_U>0` on which perturbing the constant kernel
along `U` cannot improve the monochromatic objective. But there is no one
uniform radius valid for every direction.

Consequently, gradient or Hessian search initialized only at
`1/2 + tiny noise` can legitimately return to `1/32` even in a family that has
finite-amplitude or multiscale improvements. A meaningful screen must include
boundary-biased/binary algebraic seeds or explicitly multiscale directions.
Failure near one half retires only that local basin.

## 6. Four-type compression: exact benefit and exact limitation

[Terwilliger, *Counting 4-vertex configurations in P- and Q-polynomial
association schemes* (1985)](https://people.math.wisc.edu/~pmterwil/Htmlfiles/counting4vertex.pdf)
shows that in a `d`-class P- and Q-polynomial association scheme, all
four-tuple relation-type counts can be computed from the intersection numbers
and the counts of at most `floor(d/2)` exceptional four-types.

The implementation gate is strict:

1. relation matrices partition `X x X` and are closed under transpose;
2. exact products satisfy `A_i A_j = sum_k p^k_ij A_k` with constants
   independent of the selected vertex pair; and
3. a P- and Q-polynomial ordering is verified.

If these hold for the quadratic or canonical quotient relations, only the
exceptional four-types require literal enumeration, after which any weighted
kernel objective is a polynomial evaluated from the retained histogram. If
closure or the P/Q ordering fails, the theorem cannot be invoked.

This source also gives the relevant obstruction: intersection numbers and the
ordinary spectrum do not generally determine every four-vertex count. The
exceptional four-type data cannot be silently omitted. For the present orders,
literal translated enumeration remains an appropriate fallback.

## 7. The nonlinear recursion is exactly BEC channel polarization marginally

The endpoint recursion in `nonlinear-polarization-audit.md` is not merely
analogous to a known cascade. It is exactly the binary-erasure-channel part of
Arikan's polar transform. [Arikan's original paper (submitted 2008, published
2009)](https://arxiv.org/abs/0807.3917) gives, for a BEC of erasure probability
`p`, the two descendant erasure probabilities

```text
f_0(p) = 2p-p^2,          f_1(p) = p^2.
```

Here the index is chosen to match a vertex-bit difference: equal fresh bits
(`0`) give the plus/OR branch and unequal bits (`1`) give the minus/AND branch.
The two descendants are usually denoted minus and plus channels in the coding
literature, so their order is conventional.

It also proves polarization to the two endpoints. [Arikan--Telatar,
*On the Rate of Channel Polarization* (2008/2009)](https://arxiv.org/abs/0807.3806)
quantifies the marginal rate. Thus, for one fixed graphon pair, our fresh sign
products give precisely the BEC polarization martingale. Coding-theory rate
theorems can justify that most **individual pair probabilities** rapidly become
near-binary. They do not control a `K_4` density, because the six pair paths in
one four-vertex sample are not independent.

There is also an elementary quantitative identity valid for the audit's fixed
nonzero `epsilon`. Put `V_d=p_d(1-p_d)`. Direct expansion gives

```text
E[V_(d+1) | p_d] = V_d - epsilon^2 V_d^2.
```

This both repairs the endpoint argument without appealing only to finite
quadratic variation and yields, with `a_d=E[V_d]`,
`a_d <= 1/(epsilon^2 d + 1/a_0)`. In the random-free threshold coupling below,
`||W_d-W_infinity||_1=2a_d`; the six-factor telescoping inequality therefore
gives the rigorous but coarse truncation bound

```text
|F(W_d)-F(W_infinity)| <= 24 a_d.
```

This controls convergence, not its direction or whether the limit improves
the starting construction.

This also identifies the more precise analogy. The maps are the probabilities
of an AND and an OR of two independent Bernoulli variables. A depth-`d`
composition is a complete, level-homogeneous AND/OR formula. It is not a
standard Mandelbrot multiplicative cascade: only one branch is a square, the
other is its complement-dual, and the conserved quantity is the conditional
mean rather than a product mass.

### Exact four-vertex branch law

At one refinement level choose four independent signs `s_1,...,s_4`. The six
edge branches are

```text
b_ij = s_i s_j.
```

Modulo simultaneous sign reversal there are exactly `2^3=8` equiprobable
branch vectors, not `2^6=64`. Equivalently, every triangle satisfies
`b_ij b_jk b_ki=+1`; the support is the cut space of `K_4`. This explains the
triangle and four-cycle survivor terms in the one-step audit. Independent BEC
branches would erase precisely the correlations that can change the Ramsey
objective.

For a function `Phi` of the six current edge probabilities, the exact joint
transfer operator is therefore

```text
(L Phi)(p) = (1/8) sum_{s in {+-1}^4 / global sign}
             Phi((p_ij + s_i s_j p_ij(1-p_ij))_{ij}).
```

The depth-`d` objective is `L^d Phi`, where
`Phi(p)=prod_ij p_ij + prod_ij(1-p_ij)`, averaged over the initial coarse
four-tuples. This is an exact shallow-depth evaluator, but not a fixed small
profile. Substitution doubles the degree in every affected coordinate; the
degree bound grows from 1 per coordinate to `2^d`. Sign averaging removes
non-Eulerian selected-edge sets but does not stop this degree growth. Hence the
one-edge BEC state, or any profile containing only edge marginals, cannot close
the `K_4` recursion.

[Abbe--Telatar's multi-user polarization paper
(2010/2012)](https://arxiv.org/abs/1002.0777) is the closest primary adjacent
work found for joint linear constraints: its extremal multi-user states are
matroidal. Our cut-space support is likewise binary linear. However, that paper
tracks mutual-information polymatroids, not products of six nonidentical edge
probabilities, so it supplies no `K_4` closure or monotonicity theorem.

### Random-free limit as a thresholded Cantor-group Cayley lift

There is a useful exact representation of the limit. For almost every infinite
branch sequence `z`, monotonicity in the initial `p` and polarization define a
threshold `Theta(z)` such that the limit is

```text
lim_d f_{z_d} o ... o f_{z_1}(p) = 1{Theta(z) < p}
```

away from the null equality case. Mean preservation gives
`Pr(Theta < p)=p`, so `Theta` is uniform on `[0,1]`. Its inverse recursion is

```text
Theta(0 z) = 1-sqrt(1-Theta(z)),
Theta(1 z) = sqrt(Theta(z)).
```

If the new vertex coordinate is an infinite binary string `u`, the limiting
refinement can consequently be written

```text
W_infinity((x,u),(y,v)) = 1{Theta(u xor v) < W_0(x,y)}.
```

Thus the construction is a random-free, thresholded Cayley lift over the
Cantor group `F_2^N`. This is a derivation from the BEC recursion, not a claim
located in the cited papers. It makes the surviving dependence explicit:
within a four-tuple the six arguments are `x`, `y`, `z`, `x xor y`,
`x xor z`, and `y xor z` after fixing the first vertex coordinate to zero.

For finite depth let `G=F_2^d`, `N=2^d`, and let `q_p(g)` be the polar
composition selected by `g`. For one coarse six-edge probability signature,
the red `K_4` term is exactly

```text
N^-3 sum_{x,y,z in G}
  q_12(x) q_13(y) q_14(z)
  q_23(x xor y) q_24(x xor z) q_34(y xor z),
```

with the blue term obtained by replacing every `q` by `1-q`. This gives a
better-than-tree implementation route if recursion ever passes the one-step
gate. The inner three-factor correlation for all `(x,y)` has two-dimensional
Walsh transform

```text
hat(q_24)(alpha) hat(q_34)(beta) hat(q_14)(alpha xor beta),
```

so a two-dimensional FWHT evaluates a signature in
`O(N^2 log N)` time and `O(N^2)` memory, versus `O(N^3)=O(8^d)` direct
enumeration. This displayed identity uses the unnormalized forward Walsh
transform; the inverse contributes the usual powers of `N`. Coarse six-edge
signatures must still be histogrammed; the transform does not remove that
outer cost.

### Literature boundary and decision rule

A targeted search for channel polarization combined with graphon Ramsey
multiplicity found no primary source transferring the BEC recursion to the
monochromatic `K_4` objective. This is a not-found statement, not a novelty
claim. Standard graphon random-free results establish terminology and limit
behavior, but do not supply objective improvement.

The practical conclusion remains conservative:

1. use the already derived exact `A3,A4` one-step gate first;
2. if it improves materially, evaluate depths two or three with the eight-cut
   transfer, recomputing the objective after every level;
3. only then build the Cantor/FWHT evaluator for deeper levels; and
4. do not import marginal BEC polarization rates as evidence that the
   monochromatic `K_4` value decreases.

### Transferable extension: non-Kronecker polar-kernel lifts

The exact BEC identification exposes one genuinely broader family if the
binary recursion is promising. [Korada--Sasoglu--Urbanke (2009/2010)](https://arxiv.org/abs/0901.0536)
develop polarization from general binary `ell x ell` invertible kernels, and
[Fazeli--Hassani--Mondelli--Vardy (2017)](https://arxiv.org/abs/1711.01339)
shows that large kernels can improve BEC scaling. For a BEC, the `ell`
synthetic channels again have erasure probabilities `E_i(p) in [0,1]` and the
chain rule gives

```text
sum_i E_i(p) = ell p.
```

When `ell=2^m`, label the refined child vertices by `a in F_2^m` and define

```text
W'((x,a),(y,b)) = E_(a xor b)(W(x,y)).
```

This is automatically symmetric, stays in `[0,1]`, and averages back to `W`.
The bijection between the synthetic-channel indices and `F_2^m` is an
additional discrete design choice; assignments related by a group
automorphism are equivalent, but arbitrary permutations need not be.
For the Kronecker power of Arikan's `2 x 2` kernel it only bundles `m` levels
of the existing recursion. A non-Kronecker kernel gives a different valid
probability-polynomial refinement. The `E_i` can be generated exactly for a
small kernel by enumerating its `2^ell` erasure patterns and testing the
corresponding binary linear-system recoverability condition.

The one-level `K_4` branch census has only `ell^3` states after fixing one
vertex label, because the six indices remain the pairwise differences of four
labels. Thus `ell=16` has 4096 joint branch states per coarse signature and is
a feasible later screen. Better coding-theory polarization exponents do not
predict a lower Ramsey objective; this family is justified by structural
diversity, not by the rate theorem. It should be tested only after the current
binary one-step gate, or as a separately budgeted nonlinear family.

## Recommended decision order

1. Complete the positive regular-subgroup certificate if one appears; do not
   turn an arbitrary nonclosing transversal into a negative claim.
2. Screen the three, and only three, semidirect action types from finite-amplitude
   seeds. Keep the characteristic-orbit pilot and full 128-parameter kernel
   conclusions separate.
3. Report affine-subspace contribution strata for the nonabelian candidates.
4. Apply Terwilliger compression only after exact scheme and P/Q verification.
5. If the quotient is transitive but no regular group is certified, move to
   the Schreier/orbital family rather than forcing a false Cayley labeling.
6. Treat nonlinear probability polarization as exact BEC polarization only at
   the one-edge level; its `K_4` state is the eight-branch cut-space process.
7. If a nonlinear family is reopened, compare at least one non-Kronecker
   `ell=16` polar-kernel lift rather than assuming the binary recursion is
   representative of all mean-preserving polynomial refinements.

None of these sources supplies the unpublished target construction or implies
a record. Each mechanism narrows a concrete computation or a claim boundary.
