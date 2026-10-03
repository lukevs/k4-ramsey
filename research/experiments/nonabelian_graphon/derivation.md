# H-NAB-01 derivation

Let `G = F2^6 semidirect C3`, with

`(v,t)(w,s) = (v + A^t w, t+s)` and
`(v,t)^-1 = (A^-t v, -t)`.

For a stochastic Cayley graphon set `W(x,y)=p(x^-1 y)`. It is symmetric exactly
when `p(g)=p(g^-1)`. The value `p(e)` is a within-cell edge probability between
distinct blow-up vertices, not a loop value, and is therefore optimized.

For ordered `x1,x2,x3,x4`, left translation by `x1^-1` fixes the first group
coordinate to the identity. Writing `a=x1^-1 x2`, `b=x1^-1 x3`, and
`c=x1^-1 x4`, the six edge labels are

`a, b, c, a^-1 b, a^-1 c, b^-1 c`.

Thus the exact density is

`|G|^-3 sum_(a,b,c) [prod_e p(e) + prod_e (1-p(e))]`.

This is a `192^3` census rather than a `192^4` census. The reduction uses only
left invariance, not commutativity. Repeated group cells remain in the sum.

Over `F2`, `x^3-1=(x+1)(x^2+x+1)` is square-free. Hence every order-three
linear map on `F2^6` is semisimple and every nontrivial action is conjugate to
`C^r plus I^(6-2r)` for `r=1,2,3`, where `C=[[0,1],[1,1]]`. These three cases
therefore exhaust action types up to conjugacy. Fourier/character features
motivate deterministic starts, but do not turn the K4 objective into a spectral
quadratic form.

