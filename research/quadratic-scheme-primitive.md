# Exact quadratic-form primitive and provenance boundary

Date: 2026-09-27. This note records the seed supplied to the quadratic-scheme
screen. It reports no experiment.

## What the primary literature supports

Thomason's 1989 construction is described as an `m`-fold cover of an
orthogonal tower over `F_2`, and later accounts say it has maximal Witt index.
The accessible source material in this pass did not yield a sufficiently clear
complete definition of the cover/tower to implement it without guesswork.
Accordingly, the primitive below must **not** be called a reproduction of
Thomason's `<1/33` construction. It is the nearest exact orthogonal
association-scheme ingredient.

## Split and nonsplit forms

On `F_2^(2m)`, define the split (Arf-zero) form

```text
Q+(z) = sum_{i=0}^{m-1} z[2i] z[2i+1]  (mod 2).
```

Its signed character and Cayley adjacency are

```text
s(z) = (-1)^Q+(z),
A(x,y) = Q+(x xor y) = (1-s(x xor y))/2.
```

This is symmetric because subtraction and addition agree over `F_2`. Also
`Q+(0)=0`, so the corresponding simple graph has no loop. A regular blow-up
uses an anticlique inside a core class (`q00=0`); complementing every graphon
probability gives `q00=1` and leaves the monochromatic objective unchanged.

The nonsplit (Arf-one) alternative can be represented as

```text
Q-(z) = z[0] + z[1] + z[0]z[1]
        + sum_{i=1}^{m-1} z[2i]z[2i+1]  (mod 2).
```

Exact census controls are

```text
#{z:Q+(z)=0} = 2^(2m-1) + 2^(m-1)
#{z:Q+(z)=1} = 2^(2m-1) - 2^(m-1),
```

with the two counts exchanged for `Q-`. The polar form is

```text
B(x,y) = Q(x+y)+Q(x)+Q(y)
       = sum_i [x[2i]y[2i+1] + x[2i+1]y[2i]]  (mod 2).
```

## Proposed screen and controls

Refining the Hamming model by relation bins

```text
(Z_3 difference zero/nonzero, wt(z), Q+(z))
```

or its `Q-` analogue is a legitimate undirected association-scheme
refinement. It changes the structure rather than merely retuning whole Hamming
shells. The weight-zero, quadratic-zero bin contains the diagonal relation, so
its within-class parameter must be handled explicitly.

Literal translated-triple enumeration is already cheap for the intended
controls:

```text
k=4: (3*2^4)^3 = 110592 states
k=6: (3*2^6)^3 = 7077888 states.
```

At `k=4`, any compressed evaluator should match the literal evaluator exactly.
Additional controls are the quadratic value counts above, `q=1/2` giving
`1/32`, and componentwise color complementation preserving the objective.
