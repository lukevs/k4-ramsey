# Round 5 lane F5 — independent structured Z2^k fibre checker

Window 23:15–00:15 UTC. Code: `experiments/round5_F5/` (`zk_checker.py`, `k4mix.cpp`,
`submatrix_crosscheck.py`). Compute used 23:17–23:35, one single-threaded job at a time
(VECLIB/OMP threads = 1, `timeout 600` per job). No commits. No E5 evaluator or formula code
was read. No search-side value was used as an expected value; comparisons came after the
recount.

## Hypothesis record (H-R5-F5)

**Claim.** A checker that reads only the candidate matrix, finds a Z2^k fibre structure in it,
and counts via the character expansion reproduces the exact generic-recount fraction. That
makes an exact audit of E5 depth-2 (3840 classes) possible within the window.
**Disconfirmation.** A mismatch against brute force on tiny cases, against P's direct U256
recount of E5 depth-1, or between the character route and the plain route on submatrices.
**Result: confirmed** (no mismatches anywhere).

## Method (derived independently)

1. **Fibre discovery.** Exhaustive search over XOR masks g in [1,N): keep g if i -> i^g
   permutes [N] and W[i^g][j^g] = W[i][j] for every entry (exact). The kept masks plus 0
   form G = Z2^k acting freely, and its orbits are the fibres. This gives
   W((u,x),(v,y)) = f_uv(x+y).
2. **Integer Fourier transform.** F_c = sum_z f(z)(-1)^{c.z}. The check
   2^k W[i][j] = sum_c F_c(u,v) chi_c(x) chi_c(y) passes on every entry (red and 1-W) with
   zero mismatches.
3. **Character identity.** D (the sum over all N^4 ordered tuples, repeats included, with
   denominator N^4 Q^6) equals 2^{-2k} sum over c in cyc(K4) (x) F2^k (2^{3k} assignments,
   c12=a+b, c13=a+d, c14=b+d, c23=a, c24=b, c34=d) of S(c) = sum_{u in [n]^4} prod_e
   F_{c_e}. Assignments are reduced to their S4 orbits: k=1 gives 3 orbits (K4, triangle,
   C4) and k=2 gives 11 orbits. The members are chosen so that 2 (k=1) or 5 (k=2) dgemm keys
   (c13,c23,c34) cover every orbit.
4. **Exact S(c).** A pair-quadratic count in C++ with Accelerate dgemm, run mod primes
   below 2^21 (asserted n(p-1)^2 < 2^53). The code picks the fewest primes whose product
   exceeds 2|S|max + 1, where |S| <= n^4 prod max|F_{c_e}|. That is 7 primes (2^147 vs
   2^141.6) for k=1 and 8 primes (2^168 vs 2^147.6) for k=2, followed by a signed CRT
   lift. 4^k | S is asserted.

## Validation

- **Tiny oracle (in every report):** 27 cases, all passed, checked against a literal
  Python-int brute force over all N^4 tuples with arbitrary diagonals:
  - k = 0..3, including Q = 1 and Q = 7, for both W and Q-W;
  - relabelled cases (random base permutation, random linear map on fibre bits, per-fibre
    XOR offsets), up to N = 48 with multi-batch paths;
  - unstructured symmetric matrices;
  - a perturbed matrix, where the discovered k drops from 2 to 0 as it should.
- **Scale cross-check** (`reports/round5-F5-submatrix-crosscheck-001/result.json`): on
  principal submatrices of E5 depth-1 (480) and depth-2 (960), the character route
  (k=1, 2; n=240) equals the plain k=0 route exactly, for both red and blue.
- **Engine vs P's U256:** E7 run012 (768; no XOR structure found, so k=0) gives
  33801895922290936849104250872162095/1121536121443522767762587207111540736. This equals
  P's direct U256 receipt exactly (`reports/round5-F5-audit-E7-run012-001`).

## Results (exact; schema `zk-fibre-character-audit-v1`)

| Candidate | SHA-256 | k / n | Exact density | Receipt (report.json SHA) | Time |
|---|---|---|---|---|---|
| E5 depth-1 (1920) | a0524bba... | 1 / 960 | 8450464924639256799670867730068932689/280384030360880691940646801777885184000 = 0.030138895263623650 | `reports/round5-F5-audit-E5-depth1-001` (170130ae...) | 204 s |
| E5 depth-2 (3840) | 05302cbc... | 2 / 960 | **8450462766487926638466333426306607129/280384030360880691940646801777885184000 = 0.030138887566497220** | `reports/round5-F5-audit-E5-depth2-001` (8c983a4d...) | 345 s red + 273 s blue (two jobs) |

- **Depth-1 cross-check.** P's generic direct U256 (`reports/round4-P-audit-E5-depth1-001`,
  report SHA 914066a7...) agrees exactly on red, blue, total, denominator and density.
- **Depth-2.** red 259147196226119060009588075500947710392320, blue
  260049236146899152657783450211330231613440, denominator N^4 Q^6. This is the first
  independent exact count of depth-2. It agrees with E5's prediction (compared after the
  recount). It is 8.25e-9 below the E4-3840 incumbent (exact comparison) and 8.9e-7 above
  0.030138. Depth-1 is 5.5e-10 below E4-3840.
- **Structure found in depth-2.** Characters 1, 2 and 3 have 41090, 40390 and 40980
  nonzero base entries respectively. The product character is genuinely present, as
  expected from iterating the sign split.

## Trust boundary

This is exact native computation: Python ints, numpy, and C++ with Accelerate float64 dgemm
mod p, with bounds asserted. It reads only the candidate matrix, and the fibre group is
discovered and verified entry by entry.

The reduction D = 2^{-2k} sum_cycle S(c) and the S4 orbit reduction are derived identities.
They are backed by brute-force and scale cross-checks, not by a formal proof. Depth-2 has no
full O(N^4) generic recount.

Discovery covers only fibre structures that act by XOR masks on the given indices (E7 run012
showed none). This limits what gets exploited, not correctness.

The depth-1 report's `zk_checker_snapshot.py` predates the addition of the `--part` flag
(count logic unchanged). Depth-2 red and blue ran as two jobs, and blue merged `part-red.json`
after checking the SHA. This is not Lean and makes no optimality or novelty claim. Promotion
is the coordinator's decision.

## Decision / next test

**Pursue.** E5 depth-2 now has an independent exact receipt that beats the incumbent;
coordinator to decide promotion. Next tests:
- a generic direct U256 on depth-2 overnight;
- generalise discovery to non-XOR labellings (automorphism search by row fingerprints), so
  that lifts like E7 can be structurally audited;
- the checker is ready for depth-3 (7680 classes, k=3, estimated ~64 orbits and more keys)
  if it is materialised.
