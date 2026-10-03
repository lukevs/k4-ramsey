# Round 4 lane E1 — population annealing on abelian Cayley graphs

Window 22:12–23:12 UTC 2026-09-27. Code: `experiments/round4_E1/pa.cpp`
(single-threaded C++, clang++ -O3). Reports: `reports/round4-E1-*/`.

## Hypothesis record (H-R4-E1)

- **Claim.** Population annealing (Hukushima–Iba / Machta: R replicas, Boltzmann
  resampling between temperature steps) finds better or more diverse basins than
  independent annealing (IA) with the same schedule and the same total number of
  energy evaluations.
- **Prediction.** At a matched budget, PA's best-of-run and median final value
  beat IA's; PA keeps more than one lineage to the end.
- **What would disconfirm it.** IA's best-of-32 matches or beats PA across seeds, or PA
  collapses to one lineage and gets stuck in one basin that IA gets past.

## Representation

Cay(G,S) with G a product of cyclic groups, S = −S, 0 ∉ S. The value is the blow-up
value with a blue diagonal, (F_R+F_B)/n^3. Here F counts ordered triples (a,b,c)
where a, b, c and every pairwise difference lie in S (red) or in G∖S (blue).
A move flips the inverse pair {t,−t}. The state keeps the translate bitsets
S+x. A flip updates them in O(n) and a full bitset recount costs about n^3/64
(29 µs per evaluation at n=256, about 100 µs at n=384, 420 µs at n=768).

**Correctness checks** (`./pa test <dims>`):
- The incremental translate update plus bitset recount matched a naive O(n^3)
  recount on 200 random states for each of Z_2^4, Z_3×Z_2^3, Z_4×Z_5 and Z_2^5.
  There were 0 mismatches.
- Separately, an explicit Python count over all 4-tuples of the 16-vertex adjacency
  matrix, t(K4,A)+t(K4,1−A), matched the C++ value exactly (0.039794921875).

PA: at each temperature, systematic resampling with weights exp(−Δβ·E) at fixed R,
then `sweeps × |reps|` Metropolis proposals per replica. The schedule is geometric,
β from 1e3 to 1e6. Every final replica is quenched by steepest 1-flip descent.
IA runs the same code without resampling. Evaluation counts are reported per run
and match to within 0.5% (the quench length varies).

## What ran (all single-process, sequential, each job < 10 min)

| batch | group (n) | arm | R | temps × sweeps | evals/run | seeds |
|---|---|---|---|---|---|---|
| 1,3 | Z_2^8 (256) | IA | 32 | 100 × 2 | 1.64M | 9 |
| 1 | Z_2^8 | PA fixed schedule | 32 | 100 × 2 | 1.64M | 3 |
| 2 | Z_2^8 | PA, adaptive ESS=0.9 | 32 | same budget | 1.64M | 3 |
| 3 | Z_2^8 | PA | 128 | 100 × 0.5 | 1.66M | 3 |
| 4,5,9 | Z_3×Z_2^7 (384) | PA | 32 | 60 × 1 | ~0.50M | 9 |
| 4,5,9 | Z_3×Z_2^7 | IA | 32 | 60 × 1 | ~0.50M | 5 |
| 6 | Z_3×Z_4×Z_2^5, Z_3×Z_4^2×Z_2^3 (384) | PA | 32 | 60 × 1 | ~0.42M | 2 each |
| 7,8 | Z_3×Z_2^8 (768), seeded by lifting the best 384 solution | PA (low T: β 1e5–1e7, then 2e5–1e7) | 16 | 20 and 60 × 1 | 0.17M, 0.50M | 1 each |

## Results (exact results; label: measured, search code only, not independently promoted)

**Z_3×Z_2^7, n=384, matched budget of about 0.5M evaluations**
- PA best per seed (9 seeds): 0.030148806 ×4, 0.030206539, 0.030207599, 0.030232235,
  0.030288184, 0.030504951.
- IA best-of-32 per seed (5 seeds): 0.030216500, 0.030682458, 0.031160884,
  0.031252737, 0.031275943.
- Median final replica value (median over seeds): PA 0.030211, IA 0.031469.
- Best value is 1707119/384^3 = 0.030148806395354. The same basin was found
  independently in 4/9 PA seeds and in 0/5 IA seeds.

**Z_2^8, n=256, matched budget of 1.64M evaluations**
- PA ended in the same basin in 9/9 runs (fixed schedule, ESS-adaptive and R=128):
  0.030307233333588.
- IA best-of-32 hit that basin in 7/9 seeds. Seed 3 found a **better** basin, 0.030291497707 (count 508207/256^3).
  PA never found it.
- Median final replica: PA 0.030308, IA 0.031650.

**Diversity**
- PA loses lineages to one surviving family in almost every run. On Z_2^8 this
  happens by temperature step 70–80 of 100. ESS-adaptive steps and R=128 did
  not prevent it.
- At the end PA has 1–10 distinct quenched basins among the 32 replicas; IA has 27–32.
- So PA's advantage is concentration (a much better typical replica), not
  diversity. Measured by distinct basins, PA is *less* diverse than IA.

**Other abelian groups of order 384:** the groups with a Z_4 factor are much worse
(0.03111–0.03146). This fits the good structure being elementary-abelian ×
Z_3.

**Lift to 768:**
- The 384 optimum pulled back along Z_3×Z_2^8 → Z_3×Z_2^7 reproduces 0.030148806395354
  exactly. This is a consistency check of the lift and the counter.
- Low-temperature PA on the lift reached 13655163/768^3 = **0.030144857035743**. A
  second, longer run from that state (β 2e5–1e7, 60 temps) did not improve it
  (4 families, 5 basins, all ≥ 0.030144857).
- This is worse than the published Cayley reference 10486266368/768^4 = 0.030142273,
  the best finite graph 0.030142064 and the incumbent 0.030138904.
- State file: `experiments/round4_E1/s768_b7.txt`, SHA-256
  b9e6016d86531d406f6ab059c493f3800578a246841e61a856db62fddd95a667.
  **Not submitted for promotion**: nothing beat 0.03014.

## Decision

**Revise, and don't use PA as a basin-diversity tool in this family.**
- The prediction "PA is better at matched budget" is **confirmed for typical-replica
  quality** on both groups. At n=384 it also holds for best-of-run: IA never got
  within 6.7e-5 of PA's basin.
- The prediction "PA is more diverse" is **disconfirmed**. Resampling collapses the
  population onto one lineage. On Z_2^8 this cost the rare better basin that one IA seed found.
- Evidence label: restricted negative for diversity, restricted positive for
  concentration. This covers abelian Cayley graphs with n ≤ 768, budgets ≤ 1.7M
  evaluations and 3–9 seeds per arm.
- Within this representation, and at these budgets, nothing gets close to the
  0.030138 target. The best Cayley structures found are at 0.03014+.

## Next test

1. PA with lineage-preserving resampling: cap the number of offspring per family, or run
   several independent PA sub-populations, each with its own collapse (an "island PA").
   Use the same budget and compare the number of distinct basins at n=384 and 768.
   It is disconfirmed if the island best-of-run is not better than plain PA across 9 seeds.
2. Use PA as the *global* stage for step-graphon engines: run it on the n=384/768
   Cayley quotient, then hand the 0.0301448 structure to a continuous per-edge
   relation engine. This tests whether the Cayley basin is a different basin from d476.
   The lane-P tooling can compare the block structure.
3. Nonabelian groups of order 384/768 (e.g. Z_3 ⋊ Z_2^k), which the published 768
   construction may use. The code only needs a multiplication table (left translates).
