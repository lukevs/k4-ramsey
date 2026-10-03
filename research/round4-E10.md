# Round 4 lane E10: holonomy symmetry (R2-2) and D5 reflection voltages (R2-1)

Window 22:41 to 23:12 UTC, 2026-09-27. Code: `experiments/round4_E10/`. One single-threaded job at a time, local only, no commits.
All values are float64 search-side numbers; no candidate was produced (see decisions).

## H-R4-E10a (R2-2): is the Z5 holonomy table determined by symmetry?

- **Claim / prediction.** The ±1 triangle holonomy sign (and the active/inactive P split) is constant on orbits of a subgroup of G of index at most 5, giving a closed-form lift.
- **Disconfirmation.** Mixed signs inside most orbits; no small-index subgroup preserves the table.
- **Ran.** `orbit_holonomy.py` (orbit tables under G, the perfect core N (960) and the block kernel K (1920)), `table_stabilizer.py` (all 46080 elements of G enumerated; exact).
- **Results (exact).**
  - The symbol structure has 1152 fractional triangles, all PPH; 880 are active. G has 2 orbits on them (sizes 960 and 192); N and K each have 24 orbits.
  - Holonomy signs (i<j<k orientation) are mixed inside **every** orbit of G, N and K, roughly 50/50 (e.g. N-orbit tallies 27/32, 30/29, 7/8, 8/8).
  - The active/inactive split is not orbit-determined either: G's 5 P/H pair orbits split as (92 active, 4 inactive) x2, (348, 132) x2, H (96, 0); N/K pair orbits split (15,1), (56,24), (59,21) and (16,0).
  - Orientation-corrected test (does s act on holonomies by a global character ±1?): enumerating all 46080 elements, only **4** elements preserve the active set, and only **2** (identity plus one involution) preserve every holonomy; the other 2 map holonomy to ±holonomy non-uniformly. So the stabiliser of the Z5 table in G has order 2 (index 23040).
  - Fractional 4-cycles of active pairs (chordless PPPP): holonomies 0:3, ±1: 1334/1416, ±2: 111/112. Chorded PPPP: 0/±2 only (1591/938/915, as forced by two ±1 triangles). PPHH (chorded): 0:349, 2:54, 3:37.
- **Decision.** Disconfirmed (strongly). The Z5 table is a frustrated search artefact with only a Z2 symmetry, not a G-equivariant cocycle. Retire "closed-form canonical lift" for the paper; lane P should describe the lift as an explicit table (1248-entry phase file) plus the invariant facts (all active triangles PPH with holonomy ±1; 880/1152 active). Restricted negative: this does not exclude a *different* equivariant table with a nearby value (that is E4's territory).

## H-R4-E10b (R2-1): dihedral D5 (reflection) voltages

- **Claim / prediction.** Adding a per-pair reflection bit (on-pattern when a+b-g = ±1 mod 5 instead of a-b-g = ±1) lowers C(9;7,4,8) by about 1e-9 to 1e-8.
- **Disconfirmation.** No single or small multi-bit reflection move improves, so the cyclic Z5 holonomy is locally forced.
- **Validity.** Block (j,i) is the transpose of block (i,j). Under the reflection rule, W((i,a),(j,b)) depends on a+b, which is symmetric, so the reflection phase satisfies g_ji = g_ij. W is a symmetric 960-class step graphon with the same symbols and levels.
- **Ran.**
  - `dlift.py`: D5 build plus a full O(N^4) evaluator (46 s).
  - `flips.py`: exact local recount c_A. It counts the change in homomorphism counts over tuples meeting fiber A, using inclusion by the number of A-vertices. It was self-tested against brute force (573.75281169313 on both).
  - `flips2.py`: all single flips.
  - `flips3.py`: two-bit flips that share a fiber.
- **Results (float64, exact-formula recounts, not rational).**
  - **Control.** With all bits off, dlift gives F = 0.0301389257661334, which differs from 4198776398959/139314069504000 by 3.5e-17 (reproduced).
  - **Gauge control.** Reflecting every active pair at fiber 0 with phase -g is fiber negation. The delta is exactly 0.0, which confirms that the bits are gauge-dependent and only their Z2 cycle parity matters.
  - **First-order screen (misleading).** 2875 of the 4880 (pair, phase) moves have a negative gradient term, the best being -1.28e-10. The exact deltas of those same moves are +2.63e-10: the second-order term dominates, because a bit flip changes a whole block by O(1).
  - **All 976 active pairs, single reflection bit, exact.** 0 of 976 improve. The minimum is +2.6275e-10 and the median is +4.0e-10. On the top pairs the delta does not depend on the reflection phase h (differences of order 1e-18).
  - **865 two-bit moves (sharing a fiber, all 5 phases of the second bit), exact.** 0 improve. The best is +4.09e-10. Interaction terms range from -3.99e-10 to +8.7e-11, so there is partial cancellation but never a net gain.
  - Re-optimising the three levels was **not run**, because a full evaluation takes 46 s and the deadline did not allow it.
- **Decision.** Disconfirmed at the (7,4,8)/9 levels for all single flips and the sampled fiber-sharing pairs. This is a restricted negative: the Z5 (all-rotation) table is a strict local minimum against D5 reflection moves of weight 1 and 2, by at least about 2.6e-10. Retire R2-1 unless a larger-scale move is tried (see next tests). No candidate was produced, so nothing is submitted for promotion.

## Next tests (not run)

1. **Coordinated reflection patterns.** Flip bits on a whole non-coboundary Z2 cocycle class, for example one bit per PPH triangle chosen so that the Z2 parity is odd on a prescribed set of triangles, and re-optimise the phases. The two-bit interactions (about -4e-10) suggest large cooperative moves are the only hope.
2. **Levels re-optimisation with a few reflection bits,** using a symmetric fast evaluator. Full evaluation should use a C++ or cyclic-reduced path; about 46 s in numpy is too slow for search.
3. **E10a follow-up for P.** Describe the lift by its explicit table. Its only symmetry in G is one involution; the Z5 table is not G-equivariant.
