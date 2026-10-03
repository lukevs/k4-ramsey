# Exact cached delta landscape

2026-09-27. Infrastructure measurement, not a new bound or an algorithmic
superiority experiment. Unit-weight, blue-diagonal templates only.

## Mechanism and evidence

An optional native n×n int64 cache holds every single-edge numerator delta.
After flipping uv, its own delta changes sign; every other delta receives
the exact mixed finite difference evaluated on the **pre-flip** graph.
Disjoint edges use the ±24/common-color shortcut; incident edges use triangle
and triple-common-neighbor counts. Updating each edge once takes O(n²) cheap
operations instead of recomputing every motif contribution independently.
Sequential multi-edge moves update the cache after every component flip.

The existing `Graph.delta` remains an uncached oracle. `Graph.flip` maintains
the cache only after `enable_cache` is called. New APIs provide cached scalar
and batch queries, native minimum-single scans, a tabu-expiry/aspiration scan,
and a native low-cost-shortlist shared-center-pair scan. These are search
primitives, not extensions to the independent Lean verifier.

Validation before dispatch: five `test_landscape.py` test groups passed,
including all64 four-vertex graphs and every flip/undo; 120-move random
sequences at n=2,7,63,64,65,129 with full cache comparisons at intervals;
full recount and rollback; tabu expiry/strict aspiration; and native star
selection compared with sequential exact deltas. Three pre-existing engine
test groups also passed. An independent formula audit is recorded in
[landscape-audit.md](landscape-audit.md).

## Microbenchmark identity and measurements

One local warm-process measurement on the published768 seed, with optimized
native flags `-std=c++17 -O3 -fPIC -shared`:

| Operation | Measured wall seconds |
|---|---:|
| Initialize every cached delta | 0.651453 |
| 100 native minimum-edge scans plus selected flips | 0.033006 |
| Native shared-center screen, 16 candidates per color per center | 0.004332 |

After the100 flips, a fresh full native count equaled the accumulated deltas.
The star scan returned `(159,424,230,-3864)` on that intermediate graph.
Input loading and the final recount are excluded from the100-move timing;
checkpoint serialization and independent Lean verification are also excluded.
These are wall timings, not CPU utilization measurements, and not a matched
statistical speed comparison. The100-step measurement averaged0.330ms/step.

Artifact SHA-256 identities at measurement:

- `native/search.cpp`: `a72d2b77b5e24314177621a9d9559e9dcc20be8a6fb74a98b965c0cda349f71f`
- `build/libk4.dylib`: `ba54b9dd7e780b824a936061c5e6a568501bc53e1b2231a919d4edf11a32bae0`
- `data/published_cayley_768.json`: `4c372995b69be5e30713965670d525f75876a5e0a434f576491522cc0920fc54`

The measurement repeatedly called `best_cached_flip`, added its returned
delta, and called `flip` for100 steps; then called `best_cached_star(16)`.
It was a disposable in-memory benchmark, not a retained graph experiment.
Campaign comparisons must use immutable runner reports and independently
checked candidates.

## Interpretation and remaining risks

- A minimum cached single delta >=0 establishes only a single-flip local
  minimum, contingent on cache correctness. The final Lean recount checks
  the candidate value, not the entire cache or local-optimality assertion.
- A failed native star shortlist scan is **not** exhaustion of all incident
  pairs. `per_color` limits candidates; mixed-pair or global optimality is not
  certified.
- Tabu walks intentionally accept uphill changes. Report the retained best
  graph separately from the final walk state; equality or improvement of the
  retained best does not prove convergence or algorithm superiority.
- Cache-enabled graphs are mutable and not thread-safe. Parallel workers
  must use separate processes/objects, as the runner does.
- Source changes require a fresh build manifest before new dispatch. Never
  replace a binary used by an unsnapshotted live worker.
