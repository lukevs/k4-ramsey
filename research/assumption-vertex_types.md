# Vertex types lane checkpoint

Launched 2026-09-30; initial checkpoint written before research reads/compute.
Scope: new attachment profiles and positive class masses; assigned paths only.
Budget: 15 minutes from launch, last 2 minutes independent checks/handoff; one single-thread compute job at a time, hard job timeout 175 seconds. No descendants, installs, remote compute, commits, promotions, or shared evaluator edits.
Completed tests: none.
Running job/PID: none.
Result/blocker: reading protocol, pilot, resume and prior negative evidence; numerical work will use offline uv with numpy/scipy and BLAS thread limits.

## Checkpoint 2026-09-30 05:26 UTC
Completed HVT1: 12 unrestricted 192-attachment L-BFGS-B starts (seed930192), full all-root B192 baseline, exact duplicate/split graphon control, attachment finite differences, and finite-mass polynomial checks. Job PID and times in receipt-hvt1.json; completed/reaped, no job running.
B192 input is the saved rational weighted-k12 witness: F=0.030138977289665417. Existing rooted contributions vary by7.7e-10 because saved coarse masses are only numerically optimized; apparent negative slopes around1e-10 reproduce existing rows and are NOT a new-profile improvement. Random starts found distinct profiles at R≈0.030193817 or near homogeneous R≈0.031249034, both worse than base. Perturbed-row starts returned existing rows (weighted RMS≤4.2e-7). Finite positive-mass search for best returned the lower mass bound1e-8; no resolved gain. Split control error0; polynomial all-root errors≤5.3e-17; gradient error2.5e-13.
Decision: HVT1 unsupported in tested starts. Next materially different hypothesis HVT2: coordinated finite-mass two-profile insertion, retaining all mixed new-new interactions; optimize profiles jointly so a finite cooperative barrier is allowed. No promotion or global claim.

## Checkpoint 2026-09-30 05:28 UTC
Completed HVT2: 9 finite-mass two-profile insertions (three starts at each total mass .01,.05,.15, then jointly optimize mass), plus 3 coherent replacements splitting class0 into two unrestricted profiles with its original total mass. Job completed and reaped; no running PID. Pair search includes all mixed repeated new-class assignments, both new diagonals and their mutual probability. Tiny full-root/gradient checks passed (pair-checks.json). Pair witnesses and start vectors saved for all12 trials. New symmetry/representation agent Planck owns that separate comparison; this lane will not duplicate it. Shared read-only rooted and finite polynomial interfaces noted in commentary.

## Checkpoint 2026-09-30 05:30 UTC
HVT2 equal-mass results: all9 insertions chose total mass1e-8; fixed masses were worse. All3 replacement splits returned baseline within6.5e-16 with pair-profile RMS≤5.8e-6. The large nearest-OLD-row RMS in replacement records excludes the deleted source row and must not be interpreted as genuine novelty.
Completed HVT2b (9 trials): unequal new masses at fixed total .025, one-to-two replacement, and two-to-two coherent rebuilding. No resolved improvement. Some one-to-two trials suppressed one new mass to the lower alpha bound1e-5. Two-to-two returned approximately balanced masses and baseline. Job completed/reaped; no PID running. Beginning independent full-root recounts, exact tiny fixtures, positive-mass witness replay, and profile-collapse diagnostics. New searches stop here; remaining work is verification/handoff.

## Final handoff — 2026-09-30 05:33 UTC

**No resolved improvement and no promotion.** Finished within the15-minute authorization, with search stopped after about6minutes and the final review devoted to independent checks and handoff. All four numerical jobs completed and their tool sessions were reaped. Parent-owned RESUME, portfolio status, journal, and shared evaluators were not modified. No descendant agents, installs, remote/paid compute, outreach, or commits.

### Results and correct comparator

The fixed parent is `reports/clebsch-size-coarse-002/weighted-k12.json`,192 classes, rational probabilities and normalized positive saved weights. Independently recounted F=**0.030138977289665417**. This is weaker than incumbent0.030138887566497220 by approximately8.9723e-8. No tests here operate on the full incumbent.

| Hypothesis / test | Trials | Outcome |
|---|---:|---|
| HVT1 unrestricted single-class attachment,192 free probabilities |12|5 existing-row/perturbed-row trials return known rows;4 random trials find distinct worse profiles at R≈.030193817;3 near-homogeneous profiles have R≈.031249034 |
| HVT2 equal-mass cooperative pair, total mass .01,.05,.15 |9|Every fixed positive mass is worse; subsequent joint mass optimization reaches lower bound1e-8 |
| HVT2 coherent one-to-two replacement, total original-class mass |3|Returns original profile twice; F within6.5e-16 of parent |
| HVT2b unequal pair masses, total mass .025 |3|Worse F≈.030242838; one profile mass fraction hits1e-5 or1-1e-5 |
| HVT2b unequal one-to-two replacement |3|No gain; one new profile is suppressed;2 trials hit250-iteration cap |
| HVT2b unequal two-to-two rebuilding of classes0,37 |3|Recovers both original rows and approximately balanced masses; differences from parent are rounding noise |

These are33 search trials, plus3 single-profile finite-mass scalar fits and9 deterministic fixed-positive-mass replays for witness retention. Fixed-e pair minimum across starts: e=.01 gives .030163736235357803; e=.05 gives .030336268687445003; e=.15 gives .0306617941430936. The two insertion profiles have fully free attachments and all three new-new entries; no inherited relation categories are enforced. Replacement neighborhoods fix all remaining old-old entries. The unequal-pair total mass is fixed; it does not jointly free the old mass vector. Equal pair insertions do jointly vary total new mass after the fixed-e stage.

### Mechanism and confound checks

For one new class, exact conditioning on the number k of new sampled vertices gives
`F(e)=sum_{k=0}^4 binom(4,k)e^k(1-e)^(4-k)c_k`.
Here c0=F, c1=R(q), c2=d*(m*q²)^T W(m*q²)+(1-d)*(m*(1-q)²)^T(1-W)(m*(1-q)²), c3=d³ sum(m*q³)+(1-d)³ sum(m*(1-q)³), and c4=d⁶+(1-d)⁶. Thus F'(0)=4(R-F), and the new diagonal matters from order e² onward. Pair code averages every ordered new-class assignment within each k, retaining repeats, both diagonals, and mutual probability.

Existing root participation lies in [.030138977097967635,.03013897786709617]. This7.69e-10 spread is a saved-parent mass residual, so slight negative R-F at known rows is not evidence for an absent type. The returned existing profiles are within4.2e-7 weighted RMS of saved rows. The distinct random-root basin is approximately.45472 RMS from its closest row and.65877 RMS from its closest complemented row; it is genuinely distinct in this metric but worse by≈5.484e-5 in R. No symmetry-guided comparison was performed; Planck owns that lane.

For replacement splits, initial diagnostics compared only surviving old rows, producing misleading distances≈.675 because the original source row had been removed. The independent audit compares against **all original192 profiles on retained coordinates**. Equal split profiles return to removed row0 within4.1e-6 RMS. Two-to-two profiles return to rows0 and37 within1.6e-6. This correction is documented without rewriting original numerical receipts.

### Independent verification

`reports/assumption-vertex_types-001/audit.json` and the three audit detail files bind witness paths/hashes to checks:

- All21 final full graphons plus9 fixed-positive-mass replay graphons separately recounted by read-only `experiments/clebsch_bowl/audit_weighted.py`, using full weighted all-root contractions. Maximum search/recount difference1.076e-16. No class indices or diagonals omitted.
- All12 rooted profiles checked with a separately constructed explicit192³ triangle tensor; maximum discrepancy4.511e-17.
- Exact rational four-class fixture, nonzero diagonals and unequal old weights: F=512605790921940643/14303228060030765625. Repeated-index contribution and all five new-vertex multiplicity terms separately saved; pair evaluator error6.94e-18.
- Read-only checker self-test passed24 tiny rational fixtures, duplicate subdivisions and zero-mass deletions. Original B192 duplicate/split control error0. Single finite polynomial checks≤5.3e-17. All analytic attachment/new-new gradients and mass derivative checks passed finite differences.

These are independent numerical recounts and an exact tiny fixture, **not full-sized exact rational audits or formal certificates**. Rooted local optimizers cannot certify the cubic minimum. No theorem about the necessity of inherited classes, global stationarity, optimum or record follows.

### Read-only interfaces and reproducibility

`experiments/assumption_vertex_types/insertion.py`: `rooted(q,W,m)` returns value and attachment gradient; `coefficients`/`polynomial` implement one-class insertion. `pair.py`: `PairModel(W,m).evaluate(x,e)` gives objective, attachment/new-new gradient, total mass derivative and conditional coefficients. `materialize` returns a full weighted graphon. **These research scripts arm SIGALRM and load the baseline on import; import only inside a separately time-bounded job.** Unequal specialization is saved verbatim in the report directory. It is a search evaluator, not the independent checker.

Seeds930192/930193/930194; every numerical command used OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 and `uv run --offline --with numpy --with scipy python SCRIPT`. Hard SIGALRM175s installed before NumPy imports and reclamped after imports where needed. Actual job PIDs78113,78514,78696,78868; measured script times approximately.75s,2.04s,4.01s,2.84s, excluding earlier file writing and interpreter launch overhead. Python/numpy/scipy/platform and input/checker hashes in receipts; authoritative final manifest contains commands, source revision, source and artifact hashes. BLAS hardware thread counts were not independently sampled.

Decision: retire these bounded local insertion/replacement neighborhoods pending a different mechanism. Most useful next discriminating test is a certified lower bound for the rooted cubic on this exact parent, or a coordinated multi-old-class replacement that preserves a competing nonconstant structure. Do not merely repeat random starts. Planck's separate representation-guided lane may supply such profiles. Parent remains sole promotion authority.
