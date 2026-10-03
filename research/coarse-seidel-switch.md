# Deterministic coarse Seidel-switch screen

Date: 2026-09-27.  This tests deterministic switching of the exact 192-class
coarse marginal under

    P'_ij = 1-P_ij  if exactly one of i,j lies in the cut,
            P_ij    otherwise.

It is distinct from the earlier random finite lift experiment: it complements
whole probability blocks and is evaluated as a rational graphon.  The parent
is the exact coarse marginal of the verified boundary-face candidate, before
its five-type phase kernel is added.

A four-class rational literal oracle agreed with the generic ordered-index C++
counter before and after switching.  The production screen tested the three
intrinsic 64-class defect components and one side of the exact degree-two
perfect matching.  All endpoints were substantially worse:

| cut | size | density increase |
|---|---:|---:|
| each defect component | 64 | `+0.008966381477549338` |
| lower-index side of half matching | 96 | `+0.004042640197318052` |

An exact best-improvement pass evaluated all 192 single coarse-vertex switches
from the unchanged parent.  Even the best, vertex 0, increased density by
`0.00010760948226945262`.  Consequently there was no negative endpoint signal
and the preregistered convex-line optimization was not opened.

Machine-readable evidence is
`reports/latent-precision-seidel-switch-001/report.json`, SHA-256
`2f723c3fa9f50f50117751d073d4b35f473bbbf007d81309ce8901503cc0d878`.
The run made 199 exact generic recounts in 45.47 seconds and left no process.

Decision: retire these structural cuts and the entire one-vertex neighborhood
of the empty cut.  This is not a search over all `2^191` Seidel cuts, does not
exclude coordinated multi-vertex descent without an improving singleton, and
does not evaluate switching jointly with the inherited five-type phase kernel.
