# Exact-factor audit of the PPSS 768/192 construction

Date: 2026-09-27.  This is the fast discriminating test for M-ADJ-2 in
`adjacent-structural-mechanisms.md`.  It does not search small product graphs
and it does not infer group coordinates from the archived row order.

## Metadata boundary

The stored published core `data/published_cayley_768.json` contains only the
schema, 768 adjacency rows, and unit weights.  It has neither a map from row
indices to `Z_3 x F_2^8` nor the generator set.  The earlier algebraic audit
already found that simple mixed-radix interpretations of the row number do not
reproduce adjacency.  The primary-source worker independently confirmed that
the PPSS paper supports the abstract group family and generator-search method,
but our source set has no downloadable labeled generator artifact.  Therefore
enumerating purported low-index subgroups from row bits would be invalid.

## Actual intrinsic factors tested

The exact four-sheet decomposition is available and was used without changing
labels.  Its 192 fibers have inter-fiber degrees `0,2,3,4`.  The graph of
degree-three relations has exactly three connected components of size 64.
This is the sole obvious intrinsic `3 x 64` partition and is therefore the
right cheap composition/product falsifier.

Exact ordered relation histograms for its cells are:

| outer cell pair | degree-relation counts |
|---|---|
| same 64-cell | `0:2240, 2:64, 3:704, 4:1024` |
| distinct 64-cells | `0:1792, 4:2304` |

The three within-cell histograms agree, as do the three cross-cell histograms.
The 96 degree-two blocks form 32 matching edges wholly inside each 64-cell.

This is not an ordinary composition factor: every cross-cell `64 x 64` block
contains both zero and complete relations, rather than one constant outer
relation.  It is also not an obvious one-kernel XOR or tensor factor.  After
arbitrary relabeling inside outer cells, a one-kernel XOR factor must repeat a
block-value multiset or its complement, while a one-kernel tensor factor must
use zero blocks or repeat one block-value multiset.  Here the internal cells
contain the fractional degree-two and degree-three relations, whereas cross
cells are entirely deterministic.  Relabeling cannot alter that mismatch.

The real four-sheet structure likewise is a permutation-voltage cover: its
inter-fiber blocks use four relation types and edge-dependent voltages.  It is
not a repeated terminal composition kernel.  Consequently the universal
11-profile stationary operator from ordinary composition has no established
factor to act on, and building it would be an unsupported abstraction rather
than the requested factor-first test.

## Decision and scope

Do not advance a stationary internal-profile replacement from this audit.
The exact machine-readable evidence is
`reports/latent-precision-factor-audit-001/report.json`, SHA-256
`ceb60b91ee89e2276176d67857e5d80483f170843e8b7e4e9d7b78898cb8081d`.

This retires only the visible three-cell composition and one-kernel
XOR/tensor interpretations.  It does not rule out a relabeled group factor,
because the required group labeling is absent; nor does it rule out a richer
multi-type graph-directed substitution.  Either direction needs new exact
metadata or an independently certified equitable partition before a profile
operator is justified.
