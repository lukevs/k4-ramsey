# Signed probability-conditioned polarization

Set `C(p)=sign(2p-1)p(1-p)`, with `sign(0)=0`, and refine by

`W'((x,s),(y,t))=W(x,y)+epsilon C(W(x,y)) s t`.

The magnitude of `C` is at most `p(1-p)`, so the usual endpoint calculation
proves feasibility for every `|epsilon|<=1`. Averaging a fresh vertex sign gives
the parent probability exactly. Sign averaging again kills every nonempty edge
subset of `K4` with an odd-degree positional vertex, leaving only four triangles
and three four-cycles. Hence the objective is exactly

`F(epsilon)=F(0)+A3 epsilon^3+A4 epsilon^4`.

Unlike the unsigned control, products of four signed amplitudes can be negative,
so `A4>=0` is unavailable. The complete scalar gate therefore compares
`epsilon=0,-1,1` and the nonzero stationary point
`-3A3/(4A4)` whenever `A4!=0` and that point lies in `[-1,1]`. No clipping is
used as a substitute for explicit endpoint comparison.

Under color complementation, both the signed amplitude and the triangle
red-minus-blue bracket reverse sign. Therefore `A3` is complement invariant;
`A4` is also invariant. This replaces the unsigned control `(A3,A4)->(-A3,A4)`.
