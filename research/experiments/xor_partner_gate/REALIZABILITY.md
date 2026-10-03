# H-XOR-PARTNER-002 realizability gate

The final profile source is
`reports/xor-partner-e26-gate-005/report.json`. It corrects the earlier bank
deduplication and scope wording. The actual XOR objective is optimized without
requiring the partner's standalone monochromatic density to be small.

For an unlabeled induced-four profile `h`, let `mu` be its red-edge density,
`D` the probability that a uniformly selected disjoint edge pair is red-red,
and `A` the probability that a uniformly selected adjacent edge pair is
red-red. Every graphon profile satisfies the exact identity `D=mu^2`, because
the two edges use disjoint latent vertices, and the one-flag PSD inequality
`A>=mu^2`. The gate also imposes Goodman and exact rational-vector cuts from
the red and blue one-flag and full two-flag moment matrices.

The successive numerical outer minima are:

- weak linear gate: `0.02940360346`, an impossible all-wedge profile;
- disjoint identity plus degree variance: `0.02958650795`;
- the same constraints plus rational one-flag and full two-flag cuts:
  `0.02958650795`.

The last minimizer has orbit masses

```text
0:1/32, 3:12/32, 12:3/32, 15:12/32, 30:3/32, 63:1/32.
```

These are exactly orbit-size over 32 for the even-edge patterns and zero for
all odd-edge patterns: the uniform distribution on the 32 labeled even-parity
colorings of `K4`. It is still not a graphon profile. If a graphon has zero
odd-parity probability, then

```text
E product_(i<j) (1-2 W(X_i,X_j)) = 1.
```

Every factor lies in `[-1,1]`, so equality forces `W` to be zero-one almost
everywhere and every sampled `K4` to have even red-edge parity. For two fixed
rows `x,x'`, subtracting the parity equations on `(x,y,z,w)` and
`(x',y,z,w)` shows that their row difference `g` obeys
`g(y)+g(z)+g(w)=0` almost everywhere. This forces `g=0`; all rows agree and
symmetry makes `W` constant. A constant graphon cannot have the uniform-even
profile. This is a mechanism diagnosis, not a quantitative separation from
near-parity profiles.

As a realizable control, the full feasible triangle of equal-mass two-block
rank-one partners `W_H=p+a s_x s_y`, `|a|<=min(p,1-p)`, was screened on the
`0.01` grid. The best point was `p=a=0`, which simply returns `e26` with density
about `0.03013897729`; the balanced `p=1/2` line is minimized at `a=0` with
density `1/32`. The frozen calculation is
`reports/xor-partner-e26-rank-one-control-001/report.json`. This is a floating
bounded-grid negative, not continuous optimization or exact promotion evidence.

Decision: stop. The tested realizability constraints identify a parity
pseudodistribution but do not give a useful rigorous lower bound near it, and
the motivated realizable rank-one family gives no improvement. A general
profile optimizer would be a much larger project and is not supported by this
gate.
