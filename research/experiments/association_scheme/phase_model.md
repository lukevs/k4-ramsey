# Exact phase/support objective for the cyclic r=5 refinement

Fix the precision parent `P`, denominator `Q`, cyclic kernel

```
kappa(d) = 3 if d is +1 or -1 mod 5, and -2 otherwise,
```

and scalar numerator `q`.  Every fractional coarse edge `e={i,j}`, `i<j`,
has state `inactive` or a phase `x_e in Z/5Z`.  If active, its fine block is

```
P_ij + q * kappa(a-b-g_ij),
g_ij = x_e for i<j, and -x_e for i>j.
```

Every kernel row and column sums to zero, so all coarse marginals are exactly
preserved.  Expand the red and blue six-edge products on an ordered coarse
quadruple.  A selected perturbation edge set containing a degree-one vertex
vanishes after averaging microtypes.  The only surviving nonempty subgraphs
of `K4` are:

- a triangle (degree 3), with red-minus-blue coarse weight;
- a four-cycle (degree 4), with red-plus-blue diagonal weight;
- a diamond/K4-minus-edge (degree 5), with red-minus-blue missing-edge weight;
- all of K4 (degree 6), with red-plus-blue weight 2.

For a selected motif `H` with oriented phases `g_e`, define its exact cyclic
intersection number

```
M_H(g) = sum_{a_0,...,a_3 in Z5} product_{uv in E(H)}
             kappa(a_u-a_v-g_uv).
```

The exact refined numerator change is

```
Delta(x,q) = sum_{d=3}^6 C_d(x) q^d,
```

where `C_d` is the sum of `M_H` times the corresponding exact coarse weight.
An inactive variable zeros every factor containing it.  This is a finite
group-valued weighted Max-CSP on the 1,248 fractional coarse edges.  Its
factors are supported on the fractional-support triangles, C4s, diamonds and
K4s.  It is not the r=3 Potts screen: block phases vary independently and the
triangle factor reads their non-gauge cycle holonomy.

The executable model validates this sparse objective against literal refined
ordered-quadruple counts, including repeated coarse indices, before the full
optimization.  A generic direct ordered-index counter, which knows none of
the factorization above, is the only candidate recount.
