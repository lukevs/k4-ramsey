# Round 4 lane P — publishability and independent promotion gate

Window 22:12–23:12 UTC, 2026-09-27.  Writes only under `experiments/round4_P/`,
`reports/round4-P-*/`, `research/round4-P*.md`.  One single-threaded job at a
time; local only; no commits.

## Hypothesis records

**H-P1 (second checker).** Claim: an exact recount by a different code path
(pair-quadratic grouping, modular arithmetic mod seven primes < 2^21, Accelerate
dgemm, CRT) reproduces d4763's fraction.  Disconfirmation: any mismatch in red,
blue, or total.  **Result: confirmed** (exact agreement on red, blue, total,
denominator; 144.0 s single-threaded; 21 tiny brute-force cases passed).
Also reproduces the 192-class two-parameter base exactly (0.58 s).
Evidence label: independent native exact recount (not Lean).

**H-P2 (simpler description).** Claim: most of d4763's gain over PPSS lives in
a few-parameter description.  Prediction: B192 with small-denominator (p,h)
beats McKay; the Z5 pentagon lift with three small-denominator probabilities
stays below 0.030139.  Disconfirmation: no small-denominator point below the
relevant threshold.  **Result: confirmed for both** (table below).  Decision:
pursue (C) = C(9;7,4,8) as the expository headline.

## Exact results (all fractions from independent checker receipts)

| Candidate | SHA-256 | exact value | decimal | receipts |
|---|---|---|---|---|
| (A) B192 p=4/5 h=2/5 | 45b13fd1... | 3333439223/110592000000 | 0.030141775382 | `reports/round4-P-u256-b192-d5-p4-h2`, `reports/round4-P-crt-b192-d5-p4-h2` |
| (B) B192 p=32/41 h=22/41 | 33e2e141... | 1013294255057839/33620705806123008 | 0.030138994134 | `reports/round4-P-u256-b192-d41-p32-h22`, `reports/round4-P-crt-b192-d41-p32-h22` |
| (C) Z5 lift C(9;7,4,8) | 22df51a8e7e24030c246fe266a1077dc363eda23c4fe299798cfbb3ec400f511 | 4198776398959/139314069504000 | 0.030138925766 | `reports/round4-P-u256-pent-Q9-7-4-8` (passed, 115.9 s), `reports/round4-P-crt-pent-Q9-7-4-8` |
| (F) Z5 lift C(4;3,2,4) | 52b6c692dd5f04aae4d8bc43ae64220a5d2191d619f6ef0638ffeb8932689945 | 2048009329/67947724800 | 0.030140955198 | `reports/round4-P-u256-pent-Q4-3-2-4` (129.9 s), `reports/round4-P-crt-pent-Q4-3-2-4` (116.9 s) |
| (D) b93 = C(65536;51064,29356,58565) | b93b3589... | 1375401591138773841968807740019/45635421608216258453881315393536 | 0.030138904006 | `reports/round4-P-u256-b93-001` |
| (E) d4763 incumbent | d4763fef... | 16900934504649027287619486865996291/560768060721761383881293603555770368 | 0.030138903565 | earlier U256 + `reports/round4-P-crt-d4763-001` |

References: PPSS 4551721/150994944 = 0.0301448570; McKay 10486266368/768^4 =
0.0301422734; announcement threshold 0.030139 (rounded, unpublished).
(A) beats McKay by 5.0e-7 and (F) (probabilities only 0,1/2,3/4,1) by 1.3e-6,
both above 0.030139.  (B) is 5.9e-9 below
0.030139 (fragile).  (C) is 7.4e-8 below; (E) 9.6e-8 below.

Small-denominator scan of B192 (profile polynomial, search side; retained
points recounted): `reports/round4-P-b192-small-denominator-001/table.json`.
d=5 is the smallest denominator beating McKay; d=41 is the smallest below
0.030139 (d<=64 scanned exhaustively over 0<=p,h<=d).

Restricted rounding scan of C(Q;p0,x,y) (search side, strided evaluator,
`reports/round4-P-pentagon-001/evaluations.jsonl`): Q=4 (3,2,4) 0.0301409552;
Q=5 (4,2,4) 0.0301408061; Q=7 (5,3,6) 0.0301434930; Q=8 (6,4,7) 0.0301398645;
Q=9 (7,4,8) **0.0301389258**, (7,4,9) 0.0301392986, (7,5,8) 0.0301474286,
(7,3,8) 0.0301492315; Q=10 (8,4,9) 0.0301398981; Q=11 (9,5,10) 0.0301402051;
Q=13 (10,6,12) 0.0301390316; Q=18 (14,8,17) 0.0301389863, (14,9,16)
0.0301408330.  Q=9 is the smallest denominator found below 0.030139 in this
non-exhaustive scan.  At Q=9, y=1 (H blocks purely 0/1) is worse by 3.7e-7.

B192 origin rule (`experiments/round4_P/b192_origin.py`,
`reports/round4-P-describe-001/b192-origin.txt`): with D(i,j) = red edges
between PPSS fibres, B192 = 0/H/P for D = 0/8/12, and a complete block
(D=16) is P iff D(i,H(j)) = 12 (else F); 96 complete blocks promoted.  The
fibres are those of `reports/pilot-algebraic-lift-001/quotient.json`, not
consecutive quadruples.

Construction C(Q;p0,x,y) and its exact reconstruction of b93 (zero entry
mismatches): `experiments/round4_P/pentagon_family.py`.  The search-side
evaluator exploits the free Z5 shift (strided rows x5) after asserting shift
invariance; promotion values come only from the generic checkers.

Structural decomposition of d4763 (`reports/round4-P-describe-001/description.json`):
B192 (symbols 0/F/P/H with row degrees 91+diag/87/12/1) x Z5, kappa(d)=3 on
d=+-1 else -2; 1248 fractional pairs: 272 P inactive, 880 P active (phases
0..4 = 82/280/116/195/207), 96 H active (all phase 1); amplitudes: all H
-11713 (base raised 35015->35139), P modal -7236 on 646 pairs, 234 exceptions
over 135 other values.  Zero reconstruction mismatches over 921,600 entries.

## Lifting statement

See `research/round4-P-paper-draft.md` section 2.  Exact for every n (iid
uniform class labels, independent edges); repeated class indices use the
diagonal block value.  Both checkers sum all N^4 ordered tuples including
repeats with the stored diagonal, denominator N^4 Q^6 — matching the lemma.

## Promotion gate log

**E4-3840 — PASSED independent audit (22:40 UTC).**
Candidate `reports/round4-E4-exact-3840-001/graphon-candidate.json`, SHA-256
`594aaefbf74f72c4465fa898ecc11ffbbb1fbfb98dee7c84b3e69550b1ac2f34`, N=3840,
Q=65536.  Receipt `reports/round4-P-audit-E4-3840-001/report.json`.
Exact value (computed from the matrix; E4's score not used as input):

    2112616269946473812116180096163290703 / 70096007590220172985161700444471296000
    = 0.030138895816959867

red 259164139458368121908292741333386630799360, blue
260032435043677282157379679099703692369920, denominator N^4 Q^6.
It agrees with E4's predicted fraction (compared only after the recount).
7.75e-9 below d4763; 1.03e-7 below 0.030139; not below 0.030138.

Route (`experiments/round4_P/run_rooted_audit.py`, `crt_rooted.cpp`):
(1) 8 generator permutations of [3840] were emitted as plain data by E4's
`coset_action.py` (`experiments/round4_P/e4_generator_images.py`); P then
checked, with its own code, that each is a permutation, that
M[s(i)][s(j)] = M[i][j] for every one of the 14.7M entries and every
generator, and that the orbit of 0 under the generated group is all of [3840]
(transitive).  (2) Hence total = N * rooted(0); rooted(r) computed exactly by
the pair-quadratic multiprime CRT method (seven primes < 2^21, product
2^147 > bound 2^144); roots 0, 1, 1919, 3839 all agree.  (3) Tiny oracle:
14 cases (circulants vs brute force; sum over all roots vs brute force on
arbitrary symmetric matrices).  (4) Route cross-check on E4's 768 candidate
(SHA ecc539ef...): rooted route red/blue/total equal the generic direct U256
recount exactly (`reports/round4-P-audit-E4-768-001`,
`reports/round4-P-u256-E4-768-001`, U256 60.4 s): 0.030138935296941588.
Timing: 65.2 s total at N=3840 (rooted count 60.6 s, single thread).

Trust boundary: exact native computation (C++/Accelerate/Python), conditional
on the verified transitivity (a checked mathematical reduction, not a full
O(N^4) sum; a full direct recount would take hours).  Shares the
vertex-transitive reduction with E4's own recount but no code; the group
generators are data verified here, not trusted.  Not Lean; no optimality,
record, or novelty claim.

Other lanes checked at 22:41 UTC (E1, E3, E6, L1, R1, R2): no
"SUBMIT FOR PROMOTION" candidates.

## Decision and next tests

- Decision: **pursue** publication with (C) C(9;7,4,8) as the expository
  construction and the sharpest audited value as the headline — now E4-3840
  (0.030138895816959867, transitivity-conditional audit) or d4763 (two full
  generic recounts).  No record, novelty, or optimality claim; the
  Feinstein–Even-Zohar value is unknown.
- Next: (1) group-theoretic description of the 192 fibres and of the phase
  table (is the (C) phase table a G/K orbital structure?); (2) a full generic
  recount of E4-3840 overnight (the direct U256 run takes hours) or a
  different-machine rerun; (3) exhaustive small-Q scan of C(Q;p0,x,y) for
  Q <= 12; (4) literature items listed in the paper draft section 7.
- Process note: the E4 audit directories were created by P immediately
  before the run to hold the generator-image data; they held no prior report.

**E11 closed form for B192 — independently re-verified (22:53 UTC).**
`experiments/round4_P/verify_e11_rule.py` (own code): design isomorphism
found; 0 mismatches over 36,672 off-diagonal entries under E11's vertex map;
the canonical closed-form matrix recounts (CRT) to exactly the stored B192
fraction.  Paper draft section 3.1 now uses the closed form, with PPSS
provenance as a remark.  E10's "phase table has only Z2 symmetry" is
recorded but not re-verified.

**E7 run010 (secondary/structural) — PASSED direct U256 audit (22:55 UTC).**
`reports/round4-E7-run010/graphon-candidate.json`, SHA-256
625f03b81753737d75733b94b64539e579feb11d9e8970641f9acd38a81553dd, 768 classes
(Cayley kernel on F_64 x Z_12).  Receipt `reports/round4-P-audit-E7-001`
(generic direct ordered U256, tiny oracle passed, total = red + blue, 53.4 s).
Exact 67603793210844365850594037608134633/2243072242887045535525174414223081472
= 0.030138928171048074; agrees with E7's prediction (compared after).
Above the incumbent (not a promotion to best); below 0.030139 and PPSS.

**E7 run012 (secondary; converged) — PASSED direct U256 audit (22:59 UTC).**
`reports/round4-E7-run012/graphon-candidate.json`, SHA-256
4861081909351e67543a5b993e22efdbcf81e948a4c724991d007a21be44e94b, 768 classes.
Receipt `reports/round4-P-audit-E7-768-001` (tiny oracle passed, total =
red + blue, 46.4 s).  Exact
33801895922290936849104250872162095/1121536121443522767762587207111540736
= 0.03013892756194487; agrees with E7's prediction (compared after).
Not an incumbent (2.4e-8 above E4-3840's predecessor d4763).  Per the
coordinator, it is a Z2^2 lift of B192 reached from random 0/1 seeds on
F_64 x Z_12 (independent start: yes; shares B192 structure: yes) — the
lift/quotient relation is E7's claim, not re-verified by P.  Run010 (above)
is its earlier, less converged iterate.

E9 checked 22:58: explicitly "no SUBMIT FOR PROMOTION".  E8, E10, E11, E12:
no flags as of 22:59.

**E5 depth1 — audit STARTED 23:05 UTC (coordinator-authorised extension, one
single-threaded job, 60-min cap).**  Candidate
`reports/round4-E5-depth1-001/graphon-candidate.json`, SHA-256
a0524bbaa7d4313a561bdbcd06d1022710c9405014b45ad6e429bac520e02cf7, 1920 classes,
Q=65536.  Route: generic direct ordered U256 (full O(N^4), no symmetry
assumption), expected ~28 min.  Output `reports/round4-P-audit-E5-depth1-001`.
Result appended below when finished.  The 3840-class depth-2 candidate was not
attempted (per coordinator).

Window-end poll 23:05 UTC: no further SUBMIT flags in E1–E12.

**E5 depth1 — PASSED full generic direct U256 audit (finished 23:33 UTC).**
Receipt `reports/round4-P-audit-E5-depth1-001/report.json`: status completed,
evidence independent_generic_direct_ordered_index_u256_recount, SHA matches,
tiny oracle passed, all overflow bounds recorded, total = red + blue,
denominator = 1920^4 * 65536^6, 1644.7 s single-threaded.  Exact

    8450464924639256799670867730068932689 / 280384030360880691940646801777885184000
    = 0.03013889526362365

5.53e-10 below E4-3840 (0.030138895816959867); 1.05e-7 below 0.030139; not
below 0.030138.  Agrees with E5's predicted fraction (compared after).
Trust boundary: full O(N^4) generic recount with no symmetry assumption
(stronger scope than the E4-3840 rooted audit); native C++, not Lean.
