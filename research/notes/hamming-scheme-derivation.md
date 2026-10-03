# Exact census contract for `Z_3 x F_2^k` Hamming kernels

Date: 2026-09-27. This is an implementation note for M-ADJ-1. It derives
the exact objective and checks; it reports no experiment. In particular, this
restricted association-scheme family should not be assumed to contain the
best PPSS Cayley graph.

## Kernel and diagonal semantics

Let

```text
G_k = Z_3 x F_2^k,             |G_k| = 3*2^k.
```

For a difference `(a,z)`, the red-edge probability is `q[a,wt(z)]`.
Because an undirected kernel must agree on a difference and its inverse,

```text
q[1,d] = q[2,d].
```

It is therefore convenient to store two rows, `q[0,d]` and `q[1,d]`, where
the second row means a nonzero `Z_3` difference.

The entry `q[0,0]` is important. It is the independent red probability for
an edge between two **distinct fine vertices in the same coarse class**. It
is not a self-loop probability. The diagonal of a graphon has measure zero,
but four independently sampled coarse labels can coincide, so every edge
whose endpoints have the same coarse label must use `q[0,0]`. In a finite
blow-up, sample every unordered pair of distinct fine vertices independently
with the parameter determined by its two coarse classes; add no loops.

## Translation-reduced objective

Write the four sampled coarse labels as

```text
x0 = (0,0),  x1 = (a,u),  x2 = (b,v),  x3 = (c,w).
```

Translation invariance fixes `x0` without loss. Define `o(0)=0` and
`o(1)=o(2)=1`. The six relation bins, in edge order
`01,02,03,12,13,23`, have `Z_3` rows

```text
o(a), o(b), o(c), o(b-a), o(c-a), o(c-b)
```

and binary distances

```text
wt(u), wt(v), wt(w), wt(u xor v), wt(u xor w), wt(v xor w).
```

Consequently

```text
F_k(q) = 1/(27*2^(3k)) * sum_{a,b,c in Z_3} sum_{u,v,w in F_2^k}
           [ product_{six edges e} q[type(e)]
             + product_{six edges e} (1-q[type(e)]) ].
```

This is an ordered four-sample graphon density. There is no extra `4!`
division. If several of the six edges have the same relation bin, that factor
must occur repeatedly in the product; relation variables are not deduplicated.

## Eight-type coordinate census

For every binary coordinate `r`, record the column

```text
t = (u_r,v_r,w_r) in {0,1}^3.
```

Let `n_t` count columns of type `t`. Enumerate every weak composition

```text
n_t >= 0,                    sum_t n_t = k,
```

of `k` into eight labeled parts. Its multiplicity is

```text
M(n) = k! / product_t n_t!.
```

Writing `t=(t1,t2,t3)`, recover the distances as

```text
d01 = sum_{t:t1=1}      n_t
d02 = sum_{t:t2=1}      n_t
d03 = sum_{t:t3=1}      n_t
d12 = sum_{t:t1!=t2}    n_t
d13 = sum_{t:t1!=t3}    n_t
d23 = sum_{t:t2!=t3}    n_t.
```

For each composition and each of the 27 triples `(a,b,c)`, add `M(n)`
times the two six-factor products above. The number of compressed states is

```text
27 * binom(k+7,7).
```

The normalization identity that the implementation should assert is

```text
sum_n M(n) = 8^k = 2^(3k),
```

so the total weighted state mass is `27*8^k`, exactly `|G_k|^3`.

## Exact gradient, if used

For a state of multiplicity `M` with six red probabilities `p_e`, the
contribution is

```text
M * [ product_e p_e + product_e (1-p_e) ].
```

For relation variable `q_t`, differentiate once for **every occurrence** of
that relation among the six edges:

```text
M * sum_{e:type(e)=t}
      [ product_{f!=e} p_f - product_{f!=e} (1-p_f) ].
```

This occurrence sum is necessary when two or more sample edges use the same
relation. At the constant kernel `q=1/2`, every gradient coordinate is zero.

## Tiny controls

These checks distinguish normalization, repeated-class, and diagonal bugs
before any optimization.

1. `k=0`: there is one empty count vector and 27 `Z_3` triples. Let
   `r=q[0,0]`, `s=q[1,0]`. Literal translated enumeration has 27 terms. For
   `(r,s)=(0,1)` or `(1,0)`, `F=1/27`: one color is complete tripartite and
   cannot contain a `K4`, while a four-sample clique of the other color occurs
   precisely when all four labels agree.
2. `k=1`: the eight compositions each put one count in one coordinate type,
   all with multiplicity one. Thus `27*8=216=6^3` compressed/translated
   states, matching literal enumeration.
3. `k=2`: there are `27*binom(9,7)=972` compressed states. Their weighted
   mass is `27*64=1728=12^3`, matching literal translated enumeration.
4. For every `k`, constant `q=p` gives exactly
   `F=p^6+(1-p)^6`. Thus `q=1/2` gives `1/32`; all-zero and all-one kernels
   give `1`.
5. For every `k` and every parameter vector, componentwise complementation
   satisfies `F(q)=F(1-q)`.
6. For `k>=1`, ignore the `Z_3` row and set `q=1` exactly at odd Hamming
   distances (so `q[0,0]=0`). This is complete bipartite in red according to
   binary parity and two disjoint cliques in blue. Hence `F=1/8`. Its color
   complement also gives `1/8`.

A robust test compares the compressed census with literal translated triples
for `k<=2` using random rational parameters, not just the special constants.

### Franek--Rodl primary-paper control

The published `k=10` rule is

```text
F = {1,3,4,7,8,10}.
```

There is a diagonal subtlety: Definition 2 of Franek--Rodl replaces every
core vertex by a **red clique**. Therefore its limiting graphon has
`q[d=0]=1`, not zero, and `q[d]=1[d in F]` for `d>=1`. When this control is
embedded in `Z_3 x F_2^10` while ignoring `Z_3`, both stored rows must be
identical, including

```text
q[0,0] = q[1,0] = 1.
```

This makes the three `Z_3` copies of each binary label parts of one red
macroclass. The paper reports the rounded Erdos number `32*F=0.976501`, or
`F approximately 0.03051565625`. Its Lemma 2 gives the exact density as

```text
[24*(k4(G)+k4(complement G)) + 36*k3(G) + 14*k2(G) + 1024] / 1024^4.
```

The paper does not print the exact numerator, so an exact numerator produced
by our census is a reproduction result rather than a sourced value. The
corrected control in `reports/hamming-scheme-k10-002/report.json` reproduced

```text
F = 32765943 / 1073741824
  = 33552325632 / 2^40
  = 0.030515662394464016...,

32*F = 32765943 / 33554432
     = 0.9765011966...,
```

which is consistent with the primary paper's rounded `0.976501`. The earlier
`k10-001` run used `q[d=0]=0` and is a convention-failure control, not a
reproduction of the historical blow-up.

## Scope relative to PPSS

An arbitrary Cayley generator indicator on `Z_3 x F_2^k` need not depend only
on the Hamming weight of its binary component. Binary points of this model
therefore contain only the **shell-invariant** Cayley graphs, not all PPSS
graphs. Averaging a PPSS adjacency indicator over each `(Z_3` orbit, Hamming
weight`)` relation gives a valid stochastic starting point, but it changes the
graph and need not preserve its monochromatic density. It should be called a
shell projection, not a representation of the PPSS construction.

For reference, the red edge density of a kernel in this family is

```text
1/(3*2^k) * [ sum_d binom(k,d) q[0,d]
              + 2 sum_d binom(k,d) q[1,d] ].
```

The monochromatic objective is color-complement symmetric, but the optimizer
need not constrain this edge density to `1/2`.
