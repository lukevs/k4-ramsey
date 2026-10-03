# Round 4 lane R2: first-principles structural direction review

Window 22:32 to 23:05 UTC, 2026-09-27. I only read files and ran sanity computations of a few seconds each. I made no candidates, promotions or commits. Scripts are in `experiments/round4_R2/`.

## New structural facts (exact, computed this lane)

The scripts are `group_id.py`, `holonomy.py` and `blocks.py`. They use sympy on the certified generators in `reports/group-recovery-orbitals-001/generators.json` and the E9 loader of B192 plus the Z5 phase table.

1. **G is not W(B6).**
   - G has order 46080. Its centre has order 4. Its derived series has orders 46080 > 2880 > 960, and the last group is perfect.
   - W(B6) has centre of order 2.
   - I also enumerated five natural order-240 subgroups of W(B6) of the form S5 x C2 (`wb6_subdegrees.py`). Their 192-point actions have 10, 11 or 16 suborbits. None has the observed 24, which include four suborbits of size 1.
   - The order match with W(B6) is a coincidence. Drop that lead.
2. **B192 is 12 copies of the Clebsch graph.**
   - The perfect core has order 960, which is consistent with 2^4:A5 = W(D5)'. It has 12 orbits of 16 points. Its point stabiliser has order 60 and suborbits 1, 5, 10.
   - The kernel of the action on the 12 blocks has order 1920, which matches |W(D5)| = |2^4:S5|. The block action has order 24.
   - Inside each 16-block only the symbols 0 and F occur. The 0-graph is srg(16,5,0,2), which is the **Clebsch graph** (spectrum 5, 1^10, (-3)^5). So each block is coloured blue on the Clebsch graph and red on its complement.
   - **Every fractional pair (P or H) lies between blocks.**
   - Each block meets the other 11 blocks as follows:

   | Number of blocks | 0 per vertex | F per vertex | Fractional per vertex |
   |---|---|---|---|
   | 6 | 6 | 10 | none |
   | 2 | 10 | 6 | none |
   | 2 | 10 | none | 6 P |
   | 1 | 10 | 5 | 1 H |

   - So the fractional structure is a 2-regular "P-graph" on the 12 blocks plus an "H-matching" of the blocks.
3. **Gauge-invariant content of the Z5 lift.**
   - The lift is gauge invariant under g_ij -> g_ij + h_i - h_j, so only holonomies matter.
   - Every triangle of *active* fractional pairs has type (P,P,H). There are no active PPP or PHH triangles.
   - Every such triangle has holonomy **+1 or -1 (mod 5), never 0 or ±2**: 410 have +1 and 470 have -1.
   - So the phase table has much less freedom than 5^1248. On triangles it is a ±1 sign field, with the remaining freedom on longer cycles.

These facts change how the incumbent should be described. It is a coupled system of Clebsch graphs (W(D5) geometry, blow-ups of the folded 5-cube Cay(F2^4, {e1..e4, 1111})). Fractional "bridges" join the Clebsch copies, and a Z5 voltage lives on the bridges. Clebsch-type Cayley graphs on F2^n are exactly the Franek–Rödl / Thomason family. That is consistent with where the published record came from, and it suggests the 12-copy coupling is the new ingredient.

## Directions that are not already covered, ranked

The lanes already covered are:

- E1, E2, E3 and E7: abelian or small-group Cayley search.
- E4: G/K coset kernels of the same G.
- E5: rank-one perturbations.
- E6: XOR and affine products (retired).
- E8: mass and type pricing.
- E9: cyclic Z_m lifts with subset S.
- Round 3: recursive quotients, quadratic, Hamming and association-scheme kernels.

### R2-1. Dihedral (reflection) voltages: a D5 lift, a strict superset of the Z5 lift

- **Mechanism.** The kernel kappa(d) = 3·1[d = ±1] - 2 is reflection-symmetric, and every active triangle holonomy lies in the reflection-closed set {±1}. So the natural voltage group is D5 = Z5 ⋊ Z2, not Z5.
  - A reflection voltage r_g makes a pair on-pattern when a + b - g = ±1 (mod 5), instead of a - b - g = ±1.
  - This is still a 960-class step graphon with the same symbol and level structure.
  - Holonomies now take values in D5. A triangle carrying an odd number of reflections is a new type that Z5 cannot express, and E9's cyclic Z_m search cannot reach it for any S.
- **Cheapest test (at most 20 minutes).** Add a per-pair reflection bit to `experiments/round4_E9/lift.py` `build()`: when the bit is set, use `d = (a+b)` in place of `(a-b)`. Then:
  1. Start from the Z5 table with all bits zero and check that it reproduces C(9;7,4,8) exactly.
  2. Take single-pair bit-flip deltas with E9's gradient. This is exact first order, because the bit changes a whole block.
  3. Run a short local search over bits and phases at the (7,4,8)/9 levels.
- **Prediction.** Some reflection bits lower the value, and the gain is of the same order as a phase change (about 1e-9 to 1e-8).
- **Disconfirmation.** No bit flip improves, and local search over bits plus phases returns an all-rotation table up to gauge. That would be a restricted negative, and it would show the Z5 (cyclic) holonomy is locally forced.
- **Why distinct.** E9 varies m and S within cyclic groups. This is the first nonabelian voltage group. It is also the smallest one consistent with the observed ±1 holonomy symmetry.

### R2-2. Canonical geometric cocycle: is the holonomy sign a function of the triangle's G-orbit?

- **Mechanism.** The Z5 phase table was found by search and has no written meaning. Suppose the ±1 holonomy sign on the 880 PPH triangles is constant on G-orbits of triangles, or on orbits of a large subgroup. Then the lift is a canonical G-equivariant twisted cover of the Clebsch-copy system.
  - It can then be written down in closed form, which is valuable for the paper.
  - More importantly, it can be *re-instantiated* on other bases and other voltage groups (see R2-3). It also yields an exactly symmetric 960-class candidate that a Cayley or coset checker can handle.
- **Cheapest test (at most 10 minutes).**
  1. Enumerate the orbits of G (order 46080, generators on disk) on the 880 active PPH triangles.
  2. Tabulate the holonomy sign by orbit, and do the same for the 272 inactive P-pairs by orbit.
  3. Also compute holonomies of the fractional 4-cycles.
- **Prediction.** The sign is orbit-determined for a subgroup of index at most 5. The active and inactive split (880 versus 272) is a union of pair orbits for that subgroup.
- **Disconfirmation.** Both signs appear inside most orbits, and no index-at-most-5 subgroup separates them. Then the table is a "frustrated" search artefact, and a canonical family should not be expected.
- **Why distinct.** E4 imposes *full* G-invariance on a coset space, which gave only 7.7e-9 at 3840 classes. This asks which *subgroup* the incumbent's lift respects, and it uses holonomy, not raw phases.

### R2-3. The coupled-Clebsch family: vary the block graph and the bridge graph

- **Mechanism.** The base can be read as a three-part pattern:
  - k copies of a strongly regular graph Γ. In the incumbent this is Clebsch, with Γ blue and its complement red.
  - A block-level design on the k blocks with four relation types: "6/10 mixed 0-F" (6 blocks), "10/6" (2), "P-bridge" (2), "H-matching + F" (1).
  - Bijections or incidences between copies that come from Aut(Γ).
- **Natural generalisations.** Each has a canonical construction:
  - **Γ.** Use a folded n-cube or Clebsch-like Cayley graph on F2^{n-1}: the folded 4-cube (8 points, K_{4,4}), the folded 6-cube (32 points, W(D6)), the halved 5-cube, and triangle-free srgs (Petersen, Hoffman–Singleton, Gewirtz).
  - **k and the block design.** Use k = 6, 12, 24, with P-graph cycles of other lengths.
- **Cheapest test (at most 30 minutes).**
  1. Write the B192 rule in coordinates: x in F2^4 in each block, plus block index b in [12]. Recover each inter-block relation as an explicit affine or Hamming-weight rule on x - φ_ab(y). Verify it entrywise against `sym`.
  2. If the rule is affine, instantiate the same rule with F2^5 (folded 6-cube, 32 points, 384 classes) and F2^3. Optimise only the two levels (p, h) with the existing B192 evaluator, which takes seconds.
- **Prediction.** If the Clebsch/W(D5) geometry is essential, the F2^5 analogue has a two-parameter optimum within about 1e-5 of B192 (0.0301390).
- **Disconfirmation.** Either the inter-block rule is not affine or low-complexity in F2^4 coordinates, or every analogue at other n sits at 0.0302 or above. In the second case B192 is a sporadic coincidence at n = 5, and "family" directions should be retired.
- **Why distinct.** No lane changes the *underlying geometry* while keeping the construction rule. E1, E3 and E7 search Cayley sets from scratch, and the round-3 Hamming scheme used single-copy weight classes without inter-copy bridges.

### R2-4. Circle-latent continuum limit: a first-order stationarity test in the continuum

- **Mechanism.** Replace Z5 by the circle. An active pair becomes on-pattern when θ - φ - g_ij lies in an arc set A. For Z5, A is the arc ±[1/5 ± 1/10] and the phases g_ij are real.
  - Any finite m gives a valid step graphon.
  - The continuum gives two continuous controls: arc endpoints (arc width and offset) and continuous phases. Z_m only discretises these.
  - The question is whether the Z5 incumbent is a KKT point of this continuum family.
- **Cheapest test (at most 15 minutes).**
  1. At m = 20, embed the Z5 phases as 4g and the arcs as S = {±3, ±4, ±5}, which is isomorphic to the Z5 lift up to twins. Check that the value is equal.
  2. Take E9's gradient on the fine blocks. Sum it over (a) the boundary diagonals of the arcs, which gives the arc-endpoint derivative, and (b) the shift-by-one differences per pair, which gives the phase derivative.
- **Prediction.** A nonzero arc-width derivative of order 1e-7 per unit width. That would tell E9 which (m, S) to run: arcs slightly narrower or wider than 2/5.
- **Disconfirmation.** All boundary and phase derivatives vanish up to twin symmetry, or have the wrong sign at the level boundaries. Then the incumbent is continuum-stationary, and larger m will not help.
- **Why distinct.** E9 searches discrete (m, S) blindly. This is a single-derivative diagnostic that settles whether any m > 5 can gain at first order.

### R2-5. Active-set change: KKT slack of the 0/1 orbitals as a "second basin" predictor

- **Mechanism.** A basin with a different structure must change the support pattern: which pairs are 0, 1 or fractional.
  - At the incumbent, each 0 or 1 entry has an edge-rooted slack: blue minus red K4-minus-edge completion densities.
  - For B192 the 24 orbitals have 24 slacks; the 19 orbitals at 0 or 1 have signs forced by KKT.
  - The orbital with the smallest slack is the cheapest one to make fractional. Look especially at relations *inside* a Clebsch block, which are currently all 0/1.
  - Opening it gives a new active set, and the lift structure (R2-1 and R2-4) can be re-derived on the new set.
- **Cheapest test (seconds).** Compute the 24 orbital slacks from the B192 matrix. The gradient of F with respect to W on each orbital is already available via E9 `evalgrad` with m = 1.
- **Prediction.** An intra-Clebsch orbital (a 5-, 10- or 1-suborbit) has slack within a factor of about 3 of the fractional orbitals' curvature scale, making it a candidate to open.
- **Disconfirmation.** Every 0/1 slack is large, above about 1e-3 relative to the gradient scale. Then the active set is locally rigid, and a second basin needs a non-local move.
- **Why distinct.** E8 prices new vertex *types*, the mass direction. This prices new fractional *relations* on the existing classes. I could not confirm that the earlier derivative-guided split did this orbital by orbital, so check before running it.

## Directions I considered and ranked low

- **Flag-algebra complementary slackness (angle d).** The SDP lower bound (about 0.029) is 3.8% below the upper bounds. Slackness from a non-tight SDP does not identify zero-density subgraphs of the true extremal. Not worth a slot now.
- **Spectral design of σ (angle b).** The facts below make eigenvalue-only design uninformative.
  - With |σ| ≤ 1 there is a simple bound t(K4, σ) ≥ λ_min(σ).
  - The incumbent has t(K4) = -0.0532 against sqrt(t(C4)) = 0.076, so the spectrum is far from saturating any simple bound.
  - K4 is not spectral. Within a fixed scheme, E4 and the round-3 scheme lanes already cover orbital-kernel optimisation.
- **Other Weyl groups (angle a).** The W(B6) premise is false (fact 1). The meaningful version is R2-3: vary n in the folded-cube or Clebsch base.

## Recommended next batch

Run the top three in this order:

1. **R2-2**, the orbit-holonomy table. It takes about 10 minutes and decides whether R2-3 is canonical.
2. **R2-1**, D5 reflection voltages. It is a small patch to E9 and has the cleanest chance of a strictly new gain.
3. **R2-4**, the continuum derivative. It gates E9's large-m effort.

R2-3 and R2-5 follow if R2-2 comes back structured. The labels are: facts 1 to 3 are exact computations on certified artefacts, and all ranks are predictions only.
