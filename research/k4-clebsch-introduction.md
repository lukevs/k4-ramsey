# Why twelve Clebsch graphs help us avoid monochromatic fours

An introduction to our K₄ Ramsey multiplicity project  
Research snapshot: September 29, 2026

This note assumes basic probability and college calculus, but no graph theory. Our goal is to arrange red and blue edges so that as few groups of four vertices as possible have all six edges the same color. We started from a published construction, found a simpler structure inside it, and used that structure to build slightly better constructions. We have not determined the best possible answer.

## 1. The question

A **graph** consists of vertices (dots) and edges (connections between pairs of dots). A **complete graph** has an edge between every pair. The complete graph on four vertices is called **K₄**. It has six edges: each of the four vertices connects to the other three, with each edge counted twice, giving 4 × 3 / 2 = 6.

Take a complete graph on a large number of vertices and color every edge either red or blue. Choose four vertices. If all six edges between them are red, or all six are blue, they form a **monochromatic K₄**.

Our question is:

> How small can we make the fraction of four-vertex groups that are monochromatic, when the graph becomes arbitrarily large?

This is the **Ramsey multiplicity problem for K₄**. The ordinary Ramsey question asks when even one monochromatic K₄ becomes unavoidable. The multiplicity question asks how many are unavoidable.

For a graph with n vertices, there are

\[
\binom n4=\frac{n(n-1)(n-2)(n-3)}{24}
\]

groups of four. For each n, minimize the number of monochromatic groups and divide by this total. The limiting minimum as n grows is called **c₄**.

The number 768 is not part of this definition. It is the size of one useful construction we started from.

## 2. A benchmark: color every edge by a fair coin

For any chosen four vertices, the probability that all six edges are red is (1/2)⁶ = 1/64. The all-blue probability is also 1/64. These events are disjoint, so the probability of either is

\[
\frac1{64}+\frac1{64}=\frac1{32}=0.03125.
\]

Thus independent random coloring gives an expected monochromatic fraction of **3.125%**. At least one coloring must do at least as well as that average.

Our constructions achieve about **3.014%**. The improvement comes from organizing which edges tend to be red together, rather than choosing every edge with the same probability.

## 3. Upper and lower bounds mean different things

An **upper bound** comes from a construction. If we can build arbitrarily large colorings with monochromatic fraction at most U, then c₄ ≤ U. Finding a smaller U improves this bound.

A **lower bound** is a statement about every coloring. If all sufficiently large colorings must have fraction at least L, up to a vanishing error, then c₄ ≥ L. Proving a larger L improves this bound.

The two sides surround an unknown answer:

\[
\text{unavoidable fraction}\ \leq\ c_4\ \leq\ \text{fraction achieved by a construction}.
\]

Most of our Clebsch work concerns the right-hand side. A good construction alone does not prove that a still better construction is impossible.

### What is known publicly?

These are the relevant public benchmarks verified for this note, rather than a claim that every unpublished result is known to us.

| Result | Upper bound on c₄ | Status |
|---|---:|---|
| Fair-coin coloring | 0.03125 | Elementary benchmark |
| Parczyk–Pokutta–Spiegel–Szabó (PPSS) | 0.0301448570… | Published construction; our starting point |
| McKay improvement reported by PPSS | 0.0301422734319… | Reported in the published paper, §5.3 |
| Feinstein, with advisor Even-Zohar | < 0.030139 | Public seminar announcement, January 2026 |

The PPSS bound is exactly 4551721/150994944. Their paper also reports McKay’s smaller value, 10486266368/768⁴. The published lower-bound benchmark is **c₄ > 0.0296**, credited to Grzesik, Lee, Lidický and Volec. See the [PPSS paper, Theorem 1.1 and §5.3](https://link.springer.com/article/10.1007/s10208-024-09675-6), first posted in 2022, published online in 2024 and assigned to a 2025 journal volume.

The [Feinstein seminar announcement](https://math.technion.ac.il/events/noam-feinstein/) describes structured randomized constructions below 0.030139, but does not give their exact value or construction. Our literature checks have not located enough detail to compare directly. A value below the rounded threshold 0.030139 therefore does **not** establish that we have beaten their result.

## 4. How a small recipe makes arbitrarily large graphs

Imagine dividing the vertices of a huge graph into a fixed number of groups. For every pair of groups, prescribe a probability of coloring an edge red. Color each edge independently using the probability assigned to its endpoints’ groups.

For example, a probability of 0 means always blue; 1 means always red; 3/4 means red with probability 75%.

The table of probabilities is a **template**. Mathematicians call this kind of template a **step graphon**. We only need the finite-table interpretation here.

A table also specifies what happens between two distinct vertices in the same group. Its diagonal entries describe those edges; they are not edges from a vertex to itself.

Suppose four distinct vertices land in groups i, j, k and l. The chance of all-red edges is

\[
W_{ij}W_{ik}W_{il}W_{jk}W_{jl}W_{kl},
\]

where Wᵢⱼ is the red probability between groups i and j. The all-blue probability is the same product with every W replaced by 1 − W.

Average their sum over the possible group assignments. Call the result **F(W)**. That is the expected monochromatic fraction of the large random coloring, so some coloring has fraction at most F(W). Consequently,

\[
c_4\leq F(W).
\]

This is why a finite probability table can improve a bound about arbitrarily large graphs. It is also why we can use 192, 960 or 3840 template groups without changing the underlying problem.

When counting F(W), group labels may repeat: four distinct vertices can belong to the same group. Our checkers include those cases. A derivation and the exact counting formula appear in our [construction draft](round4-P-paper-draft.md).

## 5. Meet the Clebsch graph

The **Clebsch graph** has 16 vertices. Here is a concrete way to construct it.

Label the vertices by all four-digit binary strings, from 0000 to 1111. Join two strings when they differ in exactly one digit, or in all four digits.

For example, the five neighbors of 0000 are

```text
1000   0100   0010   0001   1111
```

Every vertex has exactly five neighbors, so there are 16 × 5 / 2 = 40 edges.

The graph has two useful regularities:

- Adjacent vertices have no common neighbor. In particular, there are **no triangles**.
- Distinct nonadjacent vertices have exactly two common neighbors.

You can see the first property directly from the binary rule: taking two different allowed steps never produces a third allowed step. These rules give unusually uniform local neighborhoods. The term **strongly regular** describes this combination of fixed degree and fixed common-neighbor counts.

To use the graph in a red/blue coloring, color its edges blue and all other pairs red. Blue then has no triangles and therefore no blue K₄. But red still has plenty of K₄s. Preventing trouble in one color can create trouble in the other.

The useful construction is therefore not just one Clebsch graph. It is **a carefully connected collection of Clebsch-based pieces**.

## 6. Finding twelve pieces inside the published graph

[Explore the 12 × 64 structure interactively](clebsch-explorer.html): drill into a family, inspect actual edges, and compare the density summary with the adjustable template.

The PPSS construction has 768 vertices. Its adjacency matrix is a 768 × 768 grid: entry (u,v) records the color of the edge between u and v. In its original vertex order, the pattern is difficult to interpret.

Our structural analysis organized it as follows:

```text
768 original vertices
  = 12 families × 64 vertices per family
  = 12 families × 16 groups per family × 4 vertices per group.
```

There are three different operations to keep separate.

### First: reorder the vertices

We list the vertices family by family, then group by group. This only renames and reorders them. Every edge retains its color, and every clique count stays exactly the same.

With boundaries drawn between families, the matrix becomes a **12 × 12 grid of large squares**. Each large square is itself 64 × 64.

The twelve squares on the diagonal show the edges **within** the twelve families. The off-diagonal squares show the edges **between** families. Thus the picture has twelve families, not 144 copies of the graph.

Each family has the same internal Clebsch-based coloring. They are not alternately a red copy and a blue copy: every family contains both edge colors.

### Second: summarize groups of four

Take two different four-vertex groups. There are 4 × 4 = 16 edges between them. Count the red ones and divide by 16.

For example:

```text
12 red edges and 4 blue edges → one summary entry: 12/16 = 3/4.
```

Doing this throughout gives a **192 × 192 table**, because there are 12 × 16 = 192 groups. Its entries are 0, 1/2, 3/4 or 1. The groups themselves are internally blue, giving zero diagonal entries under our red-probability convention.

Each of the twelve diagonal 16 × 16 blocks shows the Clebsch coloring: blue on Clebsch edges and red on the other distinct pairs. At full resolution, a family is a fourfold expansion of that 16-vertex pattern.

**Averaging is a summary, not an exact replacement for every purpose.** It preserves each block’s red-edge density, but can discard information about how several edges fit together. K₄ counts involve products of six edges, so replacing a block by its average need not preserve the answer.

### Third: turn the pattern into a new adjustable construction

We use the revealed pattern to define a probability template and optimize it. This step deliberately changes the construction.

There is a further detail: our two-parameter template is not merely the raw averages with 3/4 and 1/2 renamed. It also makes **96 formerly all-red pairs of groups adjustable**, following a rule recovered from the structure. The exact extraction and modification are recorded in [the construction draft](round4-P-paper-draft.md) and [the origin-checking code](../experiments/round4_P/b192_origin.py).

This distinction matters: relabeling reveals the structure; averaging describes it; modifying and optimizing it produces the improved bound.

## 7. What we can adjust

Call the resulting 192-group template **B192**. Each group has an address consisting of a family number (one of twelve) and a Clebsch position (one of sixteen).

The connections between families use four patterns. The following table gives the probability of red. “Clebsch neighbors” refers to the two internal positions, even when those positions belong to different families.

| Connection pattern | Same internal position | Clebsch neighbors | Other distinct positions |
|---|---:|---:|---:|
| Z: the pattern used inside each family | 0 | 0 | 1 |
| X: the reversed pattern | 1 | 1 | 0 |
| P: an adjustable version of X | p | p | 0 |
| H: a second adjustable pattern | h | 1 | 0 |

A fixed symmetric rule assigns one of these patterns to each pair of families. The full rule is in [the construction draft, §3.1](round4-P-paper-draft.md). For understanding the optimization, the important point is that the large table has only **two adjustable probabilities**, p and h.

Changing p or h changes many related entries together. We retain the arrangement of the twelve families and tune the probabilities on their connections.

## 8. Where calculus enters

Because each K₄ probability is a product of six edge probabilities, the total F(p,h) is a polynomial. We can differentiate it, locate stationary points and check the boundary of the square 0 ≤ p,h ≤ 1.

Our algebraic calculation identifies a unique minimum in this two-parameter family at approximately

\[
p=0.7791808330,\qquad h=0.5342651880,
\]

with value

\[
F(p,h)=0.030138977289665338\ldots.
\]

The recorded calculation checks the stationary equations, curvature and boundary values using exact algebra and interval arithmetic; it is more than the output of a numerical optimizer. See [the polynomial and minimum analysis](round5-F4.md).

This solves a specific optimization problem: **the best p and h for this fixed table of connection patterns**. It does not prove that all Clebsch-based constructions, let alone all colorings, have their minimum here.

A calculus analogy helps. A bowl-shaped surface may have a minimum when we can move in two coordinates. Introduce another coordinate, and a direction downhill may appear. The old point was optimal on the original surface but not in the larger space.

## 9. How finer variations get below that minimum

The next step is to divide each template group into smaller groups and let the red probability vary between them. We can preserve the average probability across a connection while changing its internal pattern.

Why can that matter? Knowing the averages of several quantities does not determine the average of their product. K₄ counts depend on six probabilities together. Shared subgroup labels affect how those probabilities occur together, even though actual edges are still colored independently once the labels are fixed.

### Five-way refinements

One successful variation splits each of the 192 groups into five, producing **960 groups**. We arrange the five labels around a pentagon and assign different probabilities according to their relative positions. We also adjust how these pentagons align across different connections.

A relatively simple example uses only red probabilities

\[
0,\quad \frac49,\quad \frac79,\quad \frac89,\quad 1
\]

and has exactly

\[
F=\frac{4198776398959}{139314069504000}
 =0.0301389258\ldots.
\]

It already improves on the two-parameter minimum. Allowing individual connection strengths to vary gives **0.03013890356539909**. Both examples have independent exact recounts. Their definitions and receipts are linked in [the construction draft](round4-P-paper-draft.md).

### Repeated two-way refinements

Another variation splits every group into a “+” and a “−” subgroup of equal size. For a connection whose original probability is w, use

| | Destination + | Destination − |
|---|---:|---:|
| Source + | w + a | w − a |
| Source − | w − a | w + a |

Every row still averages to w. The parameter a must keep all probabilities between 0 and 1. We choose different amplitudes for different connections.

Applied to the 960-group construction, one split gives 1920 groups and a second gives 3840. Our strongest independently exact-checked construction in the current notes has value

\[
\boxed{0.030138887566497220\ldots}
\]

Its exact fraction is

```text
8450462766487926638466333426306607129
─────────────────────────────────────
280384030360880691940646801777885184000
```

The [independent verification](round5-F5.md) checks the candidate’s symmetry entry by entry and then uses that symmetry to perform an exact count. It has brute-force checks on small examples and cross-checks against a generic counter. The full 3840-group candidate has not had a generic count that ignores all symmetry, nor a complete formal proof in a proof assistant.

## 10. What the small gains are teaching us

The broad structure does most of the work. Optimizing the two probabilities already gets to roughly 0.0301389773. All the refinements above improve that by about **0.0000000897** in total.

Several search methods have returned to this same base structure. That makes it a compelling object to understand. But these methods often exploit the same underlying freedom: adding finer patterns to the connections whose probabilities lie between 0 and 1. Their agreement is not several independent proofs of optimality.

There is also a useful explanation for why some downhill directions are easy to miss. For the balanced two-way split above, averaging over the + and − labels cancels the linear and quadratic changes. The first possible contribution comes from three changed edges forming a triangle; four-edge cycles contribute at the next order. An ordinary second-derivative test can therefore miss an improvement that appears only after refining the groups. The expansion is documented in [the refinement analysis](round4-E5.md).

Our tests of nearby sizes reinforce this picture, within their limited scope. Deleting one or two families made things worse. Some added families ended up with zero weight; others merely divided an existing family into identical pieces. Tested three- and four-label replacements for a particular binary refinement collapsed back to two effective label groups. See the [family-size tests](clebsch-size-coarse.md) and [internal-refinement tests](clebsch-size-latent.md).

These are useful negative results about specific variations. They do not establish that twelve is the universally best number of families or that larger internal patterns cannot help.

## 11. Have we found the bottom?

We have found the bottom of the **fixed two-parameter family**. We have not found the bottom of **all refinements around the Clebsch base**.

Smaller gains after successive refinements suggest diminishing returns, but extrapolating those gains does not prove a limiting value. A different refinement could behave differently.

To establish the bottom of a specified family, we need two matching pieces:

1. A construction attaining a value U.
2. A proof that every allowed construction in that family has value at least U.

We are developing inequalities that constrain how the finer connection patterns can fit together. One important lesson is that apparently promising triangle and cycle statistics can be mutually incompatible: each can look reasonable separately while no single probability table realizes them all. Our [path-consistency analysis](clebsch-bowl-path-contractions.md) rules out some overly optimistic proposed statistics, but does not yet give a matching certified minimum.

Separately, our lower-bound work asks what is unavoidable in **every** coloring. Flag-algebra software combines identities and nonnegative expressions involving small graphs into universal inequalities. The Sage fork we are installing supports that work. Reproducing a small known calculation is the first check; installing the software itself produces no new bound.

The main structural insight is that a complicated 768-vertex construction can be understood through twelve coupled, sixteen-position Clebsch patterns. That makes the construction easier to explain and exposes useful variables to optimize. Determining whether this structure is ultimately optimal remains an open research question.
