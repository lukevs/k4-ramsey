# Clebsch coarse-size pilot (lane B)

Contract: local sequential single-thread jobs <=180s; target total 6–8min including validation. Only this note, experiments/clebsch_size_coarse and reports/clebsch-size-coarse-* are writable. No subagents, promotion, novelty or global claims.

H-CS1: asymmetric deletion/altered duplication near twelve copies can improve the two-parameter parent, perhaps via nonuniform masses. Test k=10,11,12,13,14 using fixed within-copy 16-state Clebsch structure; simplex masses and shared p,h. Controls: exact duplication with split mass, baseline and literal tiny ordered quadruples with probability diagonals. Prior E11 regular product-design sweep is exhausted and not repeated. Prior collective graphon weights found stationary uniform masses and positive sampled curvature; this pilot tests coarse boundary changes and altered copy profiles instead.

Objective: sum over all ordered four independent class samples of products of six W entries plus six complementary entries, including all repeated labels. Evidence is numerical search plus separate direct checks, not an independent promotion audit.

Status: implementing compressed six-edge type polynomial; no campaign run yet.

## Completed results

Code: `experiments/clebsch_size_coarse/{pilot,followup,diagnostics,support}.py`.
Receipts: `reports/clebsch-size-coarse-001/` and `reports/clebsch-size-coarse-002/`.
Every job used `VECLIB_MAXIMUM_THREADS=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 uv run --offline --with numpy --with scipy python <script>`; all were sequential and completed well below 180s. The main and follow-up scripts report 0.454 and 0.538 seconds respectively (not whole-turn elapsed time); setup, reading, coding and reporting dominate this pilot. No process remains active. Source/rule hashes, versions, parameters, actual type matrices, masses and optimizer termination records are retained. `followup-launch.log` is in report001; other follow-up receipts are in report002.

46 optimization records: 21 initial and 25 follow-up, including matched equal/free masses, shared p,h optimization and two deterministic starts for k12 and deletions. No regular-product design sweep was repeated.

| construction | equal masses, optimized p,h | free masses and p,h |
|---|---:|---:|
| parent k12 | 0.03013897728966534 | 0.03013897728966538 |
| delete copy0, k11 | 0.03051882575288630 | 0.03037921462816712 |
| delete X-related pair, k10 | 0.03073962062370480 | 0.03046814612543448 |
| delete P-related pair, k10 | 0.03117834066393569 | 0.03099507580422385 |
| delete H-related pair, k10 | 0.03122698485625042 | 0.03103591970026096 |
| exact duplicate, k13 | 0.03038854281167045 | 0.03013897728966547 |
| best changed-row k13 under equal masses (P→H at link to copy6) | 0.03038697005826775 | 0.03013897728966538 |
| two altered duplicates, k14 | 0.03081799784555205 | 0.03013897728966806 |

All baseline-level differences at ~1e-12 or below are numerical, not improvements. No candidate beats B192, the d4763 parent 0.03013890356539909, or depth2 0.030138887566497220. No promotion proposed.

### Effective copies versus nominal copies

Full weights, exact-zero indices, near-zero indices and identical-profile groups are in `reports/clebsch-size-coarse-002/support.json`. Threshold below means 1e-7; actual near-zero residuals are around 1e-12, not deliberately positive new designs.

- Exact duplicate control: **both copies0 and12 remain positive**, new mass 0.0435434164. Their profiles are identical, so merging yields 12 effective copies. Equal 1/13 masses do NOT preserve the old graphon; splitting the old copy0 mass does, and was checked separately.
- Alter clone/original cross-link to X/P/H: **original copy0 vanishes**, while copy12 retains approximately 1/12. The clone replaces the original, leaving 12 effective profiles, rather than adding a new one.
- All ten changed-row variants: **new copy12 vanishes** (exactly zero for P→H, H→X and H→P; others at most 4.9e-12). The best changed-k13 witness is H→X at the new copy's link to copy3, with exactly zero new-copy weight. This is a degenerate k13 representation of the parent.
- k14 altered pair: **original copy0 and new copy13 vanish**; new copy12 survives at 0.0833333363. Again 12 active distinct profiles; no profile merge is needed.

Thus twelve is not a required representation size: neutral duplication gives arbitrarily many nominal copies. This pilot supplies numerical evidence for stability of twelve *effective* profiles in these limited deformations, not a theorem that every better coarse architecture must have twelve copies.

### Evaluator derivation and validation

Let a_s be coarse masses summing to one, with uniform internal mass a_s/16. For coarse labels (s,t,u,v), average the six-edge product over x1,x2,x3,x4 in F2^4. Simultaneous internal translation permits x1=0 for **each coarse tuple**, leaving 16^3=4096 internal triples; it does not permit fixing coarse s. Their six differences fall into 98 observed patterns over {0,S,outside C}. Enumerate all 4^6 six-edge type signatures and aggregate coefficients c^red_ab and c^blue_ab. The internal expectation is

    K(signature;p,h) = sum_ab c^red_ab p^a h^b
                            + c^blue_ab (1-p)^a (1-h)^b.

Sum K times a_s a_t a_u a_v over **all** coarse tuples; implementation uses sorted quadruples with their exact permutation multiplicities. This retains every repeated class occurrence and probability diagonal. The derivatives are analytic; no coarse transitivity assumption is used.

Checks (`report001/checks.json`): literal ordered products on random 2,3,5-state probability matrices with nonzero diagonals and unequal weights match full-root contraction to 1.12e-16. A two-copy, 32-state H-diagonal fixture matches compressed polynomial to 2.78e-17. B192 all-root recount agrees to 2.05e-16. Exact duplicate with old mass split agrees to 3.47e-18. Analytic gradient matches centered finite differences to 1.87e-11. Materialized witnesses are recounted by the separate full-root routine within this worker, but independent parent audit is still pending.

At optimized p,h, the k12 coarse-mass gradient range is 1.53e-16. The 11 eigenvalues of the mass Hessian on an orthonormal simplex tangent basis range from **0.0304848930 to 0.1732655324**; this is numerical fixed-p,h local stability, not an exact PSD certificate. The 13 tested altered-clone invasion slopes (moving mass from copy0 into an absent new copy) are all positive, ranging **1.642253659e-5 to 0.004151768485**. Smallest is H→X at link3. Actual slopes are in `diagnostics.json`.

### Audit handoff

`reports/clebsch-size-coarse-002/witnesses.json` contains SHA256, rationalized recount values and paths. Each witness uses `rational-step-graphon-v1`, integer edge denominator 10^12, and rational-string block weights, with all 16 states materialized per copy. Retained zero weights are intentional. Requested files:

- `best-deletion-k11.json`: 176 states, density 0.030379214628167138; genuinely unequal positive masses (range 0.0531502583–0.1104675513).
- `weighted-k12.json`: 192 states, density 0.030138977289665417; optimized masses converge to 1/12 within ~2.5e-8.
- `best-changed-k13.json`: 208 states, density 0.030138977289665275; exactly zero new-copy mass. The apparent ~1e-16 gain is roundoff.
- `positive-equal-k13.json`: 208 positive-weight states, density 0.030386970058267827; nondegenerate changed architecture.
- `best-deletion-k10.json`: 160 states, density 0.030468146125434543.

Parent indicated it will run `experiments/clebsch_bowl/audit_weighted.py`; that file was read but not changed or run here. No independently audited improvement is claimed.

Decision: retire these deletion and one-link altered-clone mechanisms as unsuccessful in this bounded pilot. Unequal masses materially repair damaged designs, but none approaches the stronger structured incumbent. A further run should require a new coordinated coarse-row mechanism, not more starts of these same neighborhoods. No general coarse-design impossibility or novelty claim follows.
