# Odd-characteristic quadratic-form screen

## Question and representation

This is one bounded screen of a genuinely different algebraic family, not a
record or novelty claim.  On the additive group `F3^d`, use four relations:
the identity difference, and the three values `0,1,2` of

`Q_a(z) = a z_0^2 + z_1^2 + ... + z_(d-1)^2 (mod 3)`

on nonzero differences.  The identity relation represents the probability
inside a coarse atom; it is not a graph loop.  Both `a=1` and the nonsquare
twist `a=2` were tested for `d=4,5`.  Color complements and equivalent forms
were not used as extra starts.  In odd dimension the two forms exchange the
nonzero quadratic values under the usual scalar equivalence; their identical
`d=5` start value is an explicit check of that equivalence.

The preregistered dyadic start (denominator 65536) was

`p(identity,Q=0,Q=1,Q=2) = (32768,32768,6554,58982)/65536`.

There was one deterministic four-free-variable run from this start for each
listed representation, with no random restarts.

## Exact controls

For each of the four cases, the frozen start was counted twice: once by the
engine's checked translated `N^3` census and once by its generic full-matrix
ordered-tuple census.  The reduced exact fractions agree in every case.

| d | twist | relation masses | exact start | decimal |
|---|---:|---|---|---:|
| 4 | 1 | 1,32,24,24 | 5468204710270535331561437 / 174085318024506601157689344 | 0.031411061956992586 |
| 4 | 2 | 1,20,30,30 | 11106914428182518352953519 / 348170636049013202315378688 | 0.031900778750965544 |
| 5 | 1 | 1,80,90,72 | 1036040721916334689 / 31128880624384868352 | 0.033282299303263420 |
| 5 | 2 | 1,80,72,90 | 1036040721916334689 / 31128880624384868352 | 0.033282299303263420 |

The relation masses sum to `3^d`.  The matched full-matrix controls are in the
corresponding `*-matrix-frozen-001` report directories; translated controls
are in `*-translated-frozen-001`.

## Screen results

The following are exact recounts of the rounded points reached by the frozen
v1 optimizer.  All are far above the incumbent `0.03013890356539909`, so none
was submitted for independent promotion.

| d | twist | rounded numerators | exact density | decimal |
|---|---:|---|---|---:|
| 4 | 1 | 32768,32785,23557,42004 | 1713488996603501831176661926879 / 54824341034821814889388789727232 | 0.031254164924940459 |
| 4 | 2 | 37981,31264,24173,42259 | 73112624195981657673555335924597 / 2339171884152397435280588361695232 | 0.031255772477136338 |
| 5 | 1 | 33395,50525,0,54311 | 218859494560308913775129607553313 / 7017515652457192305841765085085696 | 0.031187603334190638 |
| 5 | 2 | 32748,32939,14446,47140 | 4338937294353566263383488627677 / 138774113244392718938765373997056 | 0.031266186415562516 |

These are reached candidates, not family optima.  In particular, the v1
optimizer has a confirmed boundary-starvation defect: it includes an outward
component at a bound when computing one global feasible step cap.  At the
`d=5, twist=1` terminal point, relation 2 is at zero and the exact raw
gradient is positive, so the descent component is outward and forces the
global cap to zero even though the other three coordinates remain
nonstationary.  The terminal exact gradients are

`(143062728263197262318905956,
 -7562736065531405494751307840,
 26559327964722455166544860480,
 5653156288066420126917091680)`.

Therefore the numerical screen supports only the narrow conclusion that this
single motivated basin produced no competitive point before the defect was
encountered.  It does not rule out the four-relation family.

The separate v2 evaluator fixes only the boxed free-variable projection and
leaves the v1 exact census and weighted-constraint branch unchanged.  From the
identical `d=5, twist=1` start it reached

`p = (33263,53973,0,49986)/65536`

with exact density

`5901018021651408307897675321569659 /
 189472922616344192257727657297313792
 = 0.031144386966575340`.

There was one active wall and no cap stall.  The run exhausted its 300-step
budget with free projected-KKT infinity norm `0.0016725157`, so this is again a
reached exact point rather than a local optimum.  It is nevertheless already
more than `0.001` above the incumbent, which is decisive for this bounded
single-basin admission screen.

## Reproduction

Generate the configurations:

```sh
python3 experiments/relation_engine/make_f3_configs.py
```

Then run a configuration with the frozen shared evaluator, for example:

```sh
python3 experiments/relation_engine/run.py \
  --config experiments/relation_engine/configs/f3_quadratic/f3d4_twist1_translated_free.json \
  --out reports/relation-engine-f3d4-twist1-translated-free-001
```

`make_f3_final_diagnostic.py` freezes reached points for terminal exact-gradient
audits.  The frozen relation-engine source and binary hashes used throughout
are respectively `78c49a2587abfa28675242c275d6955080af8586151b1d7e877877adbaee3013`
and `e66388bbef9093035d469b7acb117ee9821ca6c935936d4af4566e65f3c86784`.
The boxed-free v2 source, binary, and adapter hashes are respectively
`161a5537ef694612d47376a5efa70753943df67ebc5b92ed545d9f28db51543c`,
`c5310f4ac47487630fbd8d462d146ec506ff336a20f2105dddd83a3008ce65cd`,
and `6cc0119aef045f72acc810553f985ebb5aa9136ec7df9ffb9ba3280ce1b1cb43`.
