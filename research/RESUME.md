# Completed: full two-root N8 pilot

Full 120x120 blocks exactly reduced to 74+46 and independently recounted.
Solve timed out with invalid primal; no bound improvement. Explicit colour
quotient halves variables to 6178; solver prepared, NOT run. All jobs reaped.
Next: experiments/rooted_frontier/solve_quotient.py control then cut.
See research/rooted-full-pilot.md and reports/rooted-full-001/summary.json.

# Historical: complete two-root N8 pilot

Through 13:29 UTC, parent only, one numerical job at a time.
See research/rooted-full-pilot.md. No new bound yet.

# Completed: rooted frontier pilot

No improvement. 96 rooted square cuts and two projected 16x16 matrices
independently recounted; all three solves stayed near the imposed lower endpoint.
Fixed-profile factorization obstruction is only ~9e-9. N9 not reproduced.
Checked reference 0.029260494838693384 unchanged; all jobs reaped.
See research/rooted-frontier-pilot.md. Historical checkpoints follow.

# Historical: rooted frontier pilot

Local pilot through 13:00 UTC, parent only. See research/rooted-frontier-pilot.md.
No new bound. Previous completed checkpoints follow.

# Completed: automatic N7 and selective N8 pilots

Checked bound 0.029260494838693384 remains strongest here, below published
frontier. N8 objective-independence cut gave no improvement. All-four-pattern
point extension is tolerance-sensitive and inconclusive. See
research/energy-bootstrap-n8-pilot.md and reports/energy-bootstrap-n8-001/summary.json.
All jobs reaped; no current numerical work. Prior active checkpoints below are historical.

# Active: automatic weakest-case refinement

Local campaign through 06:29 UTC, one persistent numerical worker and sequential
exact checks. See research/energy-bootstrap-auto-pilot.md and
reports/energy-bootstrap-auto-001/queue.json. Existing checked bound
0.029256668285624187. No upper-bound promotion.

# Completed: joint independence and adaptive refinement

Exact checked universal bound 0.02925666828562419, below published frontier.
See research/energy-bootstrap-joint-pilot.md and
reports/energy-bootstrap-joint-001/combined-11-check.json.
All jobs finished; no upper-bound promotion. No next experiment running.

# Completed: full N7 independence pilot

Exact checked universal bound 0.029206667764322916, improving matched full-N7
control 0.029184646404761906, still below published frontier. See
research/energy-bootstrap-n7-pilot.md and reports/energy-bootstrap-n7-001/combined-check.json.
All jobs finished. No upper-bound promotion. Next experiment is not running.

# Completed: energy-bootstrap pilot

Exact checked universal reference bound 0.02879100332515625, below published
frontier. See research/energy-bootstrap-pilot.md and independent-check receipt
in reports/energy-bootstrap-001. Six exhaustive intervals enforce disjoint
triple independence. All jobs and prior five agents finished; incumbent unchanged.
Next: test at a higher hierarchy level. Historical checkpoints follow.

# Historical: five assumption-challenge agents

See assumption-challenge-campaign.json for IDs and assignments; initial15-minute
pilots, original four deadline~05:39UTC, Planck~05:42UTC. Parent updates portfolio-status.json and
journal.html. Four single-thread jobs maximum, <=175seconds each. No new result
or promotion yet. Prior campaigns below are historical.

# Completed: two parallel follow-up pilots

See research/family-vs-basin-parallel.md for agent IDs, deadlines, ownership and
review gate. Euler explores current-family joint parent/amplitude directions;
Lorentz challenges inherited structure using unrestricted weighted matrices.
Both completed: first-layer joint patch gain4.60e-13 verified relatively; unrestricted92-candidate pilot near1/32. No incumbent improvement.

# Latest checkpoint: flexible mechanisms pilot completed

See research/flexible-mechanisms-pilot.md. Matched nested Clebsch controls
show independent amplitudes and diagonal relations help. A spectral-projector
recipe retains99.998% of the four-variable model's gain; random relative
relabellings lose. Actual incumbent layer1 has negative cubic AND quartic;
sign/magnitude ablations lose98%+ of its gain. Both recursive layers are
box-limited along their current scale directions. Next: joint parent/amplitude
updates to move those boxes, with matched controls and independent checking.
No new bound; no full-incumbent Hessian; all jobs finished, no agents launched.

# Latest checkpoint: spectral floor pilot completed

See research/spectral-bowl-pilot.md and reports/spectral-bowl-001/.
Spectral Cauchy-Schwarz plus rigorous diamond/K4 remainder bounds give a
closed-form floor for B192 shared regular latent kernels, a=-e,b=e.
At fixed p=32/41,h=22/41,rho=5/16 and 0<=e<=304/451, floor
0.030138931158062644 exceeds incumbent; arbitrary latent size cannot improve
incumbent within this ray. rho=2/5 analogous floor0.03013895716716552.
Not a universal lower bound or incumbent optimality result. Independent
amplitudes/kernels and coarse changes not covered. All jobs finished.

# Latest checkpoint: triangle-penalty proof pilot completed

See research/triangle-penalty-pilot.md. Exact B192 shared-kernel expansion
proves a positive cubic triangle penalty at fixed latent degree with positive
H amplitude; bounded remainder gives asymptotic triangle avoidance only.
An exact rational ten-vertex comparison reverses triangle-free superiority
at finite amplitude because four-cycle cost falls. No global theorem or new
bound; no full lifted recount or candidate promotion. All jobs finished.

# Latest checkpoint: other SRG arrangements tested

See research/graph-arrangements-pilot.md. Gewirtz/M22/Higman–Sims generated
and checked. Direct plain/ambient/anchor kernels did not beat random. As
row-zero latent refinements of B192 they give small gains, best HS mixed
P/H prediction0.03013895500468096, worse than incumbent0.030138887566497220.
No new upper bound or exact promoted witness. Mixed expansion validated by
separate576-class recount. All jobs finished; no active agents.

# Latest checkpoint: compressed consistency pilot completed

See research/compressed-consistency-pilot.md. Three compressed6->5 systems
(152,154,104 upper states) tested; no resolved improvement over N5. Exact
rational extensions show the old feasible witness survives all three.
All compression tensors/deletion maps independently checked. Full deletion
fidelity requires156 deterministic states in this small census. No bound
changed; no jobs or agents remain running. Historical checkpoints below.

# Latest checkpoint: edge/vertex/curvature pilots complete

See research/edge-optimality-pilot.md. Edge and vertex-feature localizers, alone
and together, left the small N6/N5 bound near0.028750924. First7-vertex mass
curvature condition has strict slack on both savedN7 solutions. No stronger
bound claimed. All experiments and literature agents have finished. Broader
literature report: research/broad-methods-literature-2026-09-30.md.

# Latest checkpoint: stationarity-cut test completed

See research/stationarity-cut-pilot.md. Matched N7 control/cut both ~0.028750924;
no resolved gain, no new exact bound. All pilot compute exited. Broader recent
cross-field literature agent Kierkegaard (01a0f088-f305-7fb3-add3-db2218ca2b54)
is separately active for up to25min from launch, no experiments. Direct
literature lane and lower-frontier A/B/C finished. Historical context below.

# Restart handoff — 2026-09-27 22:12 UTC

## Active three-agent lower-bound pilot — 2026-09-30 04:01 UTC

User explicitly authorized three parallel lanes. Contract and agent IDs:
`lower-frontier-parallel-2026-09-30.md`. A/Ampere: recover N9 KPS calculation;
B/Aristotle: local-to-global inequalities; C/Bohr: necessary near-optimal
structure. First handoff deadline 04:16 UTC, one single-thread <=180s job
per worker, local only. Only A owns Sage container work. Root reviews and
integrates. All three launched; no results yet. Prior pause on distributed
work is superseded only for this explicitly requested bounded pilot.

## Latest focused audit — 2026-09-29

Certificate-guided upper-search pilot complete: `certificate-guided-upper-search.md`.
P4-rooted term is ~35% of the chosen certificate gap on depth2. Coarse changes
that reduce it worsen true density; two actual-objective repair runs return
to B192. No new incumbent. All jobs finished. User asks relevance of the PPSS
paper; it is our starting source, with relevant tight-certificate/kernel and
stability methods in Section 4, not a proof of symmetric K4 optimality.

Sage fork installed and exact Mantel smoke test passed; N6 K4 reproduced.
New bounded N6->N7 pilot: `toolbox-clebsch-extension.md`. C5 alone and C5
plus P5/complement(P5) show no measurable gain; all-five-root run timed out
during generation. Independent exact coefficient/PSD checker certifies
0.028750924686580158, a tighter rounding of the existing low-level result,
NOT a new hierarchy gain or published record. All jobs complete.
User now asks about optimality within the Clebsch family versus all
768-vertex colorings; keep those distinct from graphon-template optimization.

Overlap follow-up: `global-overlap-pairs-pilot.md`. All 15 pairs of four-root
colour groups tested. Best (3,15)+(7,11) gives exact certificate
851700121/30000000000 = 0.0283900040333, independently recounted, using four
new blocks. Direct literature example reproduced: Clebsch 192 pentagons,
prism-derived alternative 117 despite one root attaining 60 in both.
Toolbox reproduction script prepared but UNEXECUTED: no Sage/CSDP installed;
documented fork build is Linux-tested and >=10GB. No jobs remain running.

Recent literature refreshed in `recent-literature-update-2026-09-29.md`.
Newly located July 2026 papers: Local flag algebras (Clebsch pentagon equality
and overlapping-neighborhood arguments) and Formalizing Flag Algebras in Lean
(public Flagmatic certificate compiler). Also reviewed January 2026
FlagAlgebraToolbox and sparse-plus-low-rank SDP work. No new verified K4 bound
or Feinstein exact construction located. No installations or new jobs launched.

Coupled extension pilot now complete: `global-coupled-pilot.md`. N5→N6
controls show individual type groups give no measurable gain but eleven
four-root blocks collectively nearly recover the full N6 bound. Independent
stdlib checker enumerates all 32768 labelled six-vertex graphs, recounts 19
coefficient blocks and checks rational LDL/slacks. Exact bound 0.028750881;
old-level rational feasible moment vector has objective 0.0282000000077,
proving strict strengthening of the small relaxation. NOT a new record;
N9→N10 experiment and sparse closure still outstanding. All jobs finished.

Follow-up completed: `global-anchor-pilot.md`. A C5-plus-isolated six-root
Gram constraint is universally valid and its expansion has a ten-vertex,
21-edge graph term with coefficient 630. Exact tiny ten-vertex recounts pass.
An isolated block with three free new moments always has a rank-one PSD
completion when anchor mass is positive, so that shortcut cannot improve the
bound. Need coupled shared moment variables and marginal consistency, then
an extension-feasibility test; N=9 solution remains unavailable. No new bound.

User authorized investigating whether the Clebsch insights strengthen the
universal lower bound. See `global-lower-bound-transfer-audit.md` and exact
checks in `experiments/clebsch_bowl/global_transfer_audit.py`. No global N=9
primal/certificate located; KPS public certificates address other problems.
Simple edge-weighted path squares are already standard low-order flags.
Exact counterexample prevents extending the constant-margin Schur bound
using only global edge density. Degree-sensitive replacement proved; 420
exact rooted variance checks pass. No new lower bound and no jobs running.
Old lane-L2 feasibility/realizability claims are qualified in the new note.

## Focused pause — 2026-09-29

User paused distributed work. Do not start new search lanes. The active research
question is the bottom of the fixed-support Clebsch refinement bowl, with a
separate test of whether currently hard 0/1 orbitals form a positive wall.
Strategy and the Hadamard-order-668 comparison:
`clebsch-bowl-strategy-and-hadamard-668.md`.

Focused tests now complete: `clebsch-bowl-focused-tests.md`. Depth-2 full-objective
gradient screen covers all 576,000 fine edges of the two weakest solid types
via verified XOR symmetry, no negative inward derivatives; worst sign also
checked by exact CRT. Probability-box localizers reduce numerical allowed gain
from 1.5451e-6 to 1.2382e-6 at the fixed B192 means, with no rational dual
certificate. Diamond credit drops 5.43x but four-cycle credit becomes favorable.
Next: joint overlapping-path consistency / finite latent realizability test.
No new incumbent; all jobs from this focused run finished, no workers launched.

Subsequent authorized main-thread continuation: `clebsch-bowl-path-contractions.md`.
Sharp mean-zero operator bound ||D|| <= min(p,1-p) exposes 1020 impossible
path-moment inequalities in the former relaxation. Constant-feature and
centered K4 constraints bring the estimated fixed-mean floor to ~0.03013850455
(optimal_inaccurate, no certified dual). Exact box screen rejects all 3072
one-class subset reflections of the Z5 parent. One separately user-authorized
literature subagent completed `clebsch-formations-literature-2026-09-29.md`.
No new upper construction. All jobs and the literature review are finished.

## Round 5 (Claude Code root) — 23:15–00:15 UTC

23:33: NEW INCUMBENT E5 depth-1 reports/round4-E5-depth1-001/graphon-candidate.json (SHA a0524bba...),
8450464924639256799670867730068932689/280384030360880691940646801777885184000 = 0.03013889526362365,
full direct U256 recount reports/round4-P-audit-E5-depth1-001. Write-up page:
reports/round5-writeup-clebsch-001 (artifact A2FZUXkmetc8TCGZm1adhb). F4 theorems in round5-F4.md.

Contract `round5-contract.md`; lanes C1 ceiling, F1 open support, F2 Ramsey-critical
latents, F3 basin census, F4 proofs, F5 structured checker, P gate. Pattern note:
`round4-root-pattern.md`.

## Round 4 (Claude Code root) — 22:12–23:12 UTC

Contract: `round4-contract.md`. Eight fresh subagents, one single-threaded job each.
P: publishability of d476 (description, simplification, second independent
checker, lifting theorem, paper draft, data package) + promotion gate.
E1 population annealing; E2 NRPA/NMCS constructive rollouts; E3 PatternBoost-lite
learned seeds; E4 Schreier/orbital coset-action kernels; E5 adaptive nonlinear
polarization; E6 XOR/Boolean products of fractional graphons via 4-vertex
colour profiles; E7 new-group Cayley solver LNS + fractional polish.
Lane notes: `research/round4-<lane>.md`. Status vs literature: below every
published bound (PPSS 2022, McKay); vs unpublished Feinstein–Even-Zohar
c4<0.030139 announcement only ~1e-7 margin, record status UNKNOWN.

22:48: NEW INCUMBENT E4-3840 reports/round4-E4-exact-3840-001/graphon-candidate.json
(SHA 594aaefb...), 2112616269946473812116180096163290703/70096007590220172985161700444471296000
=0.030138895816959867, audited reports/round4-P-audit-E4-3840-001 (independent rooted
CRT recount under verified transitivity; full O(N^4) recount not yet run).

22:27: E6 RETIRED (restricted negative, first-order loss for XOR/affine
small partners near trivial; see round4-E6.md). Slot reassigned to E8:
new-vertex-type pricing / column generation on d476.


## Active renewed window — 21:04:41–22:04:41 UTC

Latest allocation (21:48 UTC), superseding earlier allocations: user approved
diversity pivot. CPU1 finite_joint_search: bounded exact coordinated reconstruction;
CPU2 correlated_graphon: growth/repair or destroy/rebuild search procedures on
independent seeds; CPU3 fresh_hypotheses: realizability-constrained induced-profile
XOR gate. CPU4 precision_lean_audit reserved for independent checking.
latent_precision supports kernel/seed reuse without compute; formal_realization
supplies profile constraints; prior_art_exact supports method transfer;
adversarial_review challenges claims. Root coordinates/UI only.
First pilots requested within about seven minutes; deadlines unchanged.
No new incumbent. Full 1247D neutral Hessian now converged numerically positive
(minimum41.16176167949, residual3.22e-11), not exact PSD or global optimality.
First XOR LP optimum is unrealizable: its disjoint-edge probabilities contradict
independence. Do not confuse partner density with XOR output density.

User authorized continuation and clarified eight subagent slots. All eight
existing agents are reused; root coordinates, reviews evidence and maintains UI.
Local only, at most four single-process compute jobs total. Stop admitting new
compute at22:00 and save/reap by22:04:41. No paid or remote work authorized.

Incumbent remains independently direct-U256 checked d4763fef at
0.03013890356539909, with exact fraction and report below. No record or global
optimality claim. New directions and decisions: `root-synthesis-round3.md`.

At21:12, CPU1 finite_joint_search moves from completed canonical pair refinement
to exact first-difference recursive quotient; CPU2 correlated_graphon tests full
128-relation Cayley refinement after a successful but non-record quadratic
symmetry break; CPU3 fresh_hypotheses tests nonabelian stochastic Cayley groups;
CPU4 latent_precision recovers exact quotient automorphisms/group structure,
yielding the slot to precision_lean_audit for candidate checks. The remaining
three lanes are adversarial_review, prior_art_exact and formal_realization.

At21:23 this allocation is superseded: CPU1 finite is the collective-mean
consumer; CPU2 correlated builds the minimal shared relation engine; CPU3 fresh
validates its nonabelian cross-family adapter; CPU4 latent tests nonlinear
polarization coefficients, yielding to independent verification when needed.
User clarified copying code is fine: optimize hypothesis-to-result time, not
architectural cleanliness. Early sharedengine selftests are being debugged;
no engine result is accepted until controls and matched-parent checks pass.

Canonical pair candidate08798 passed independent direct recount at
0.030138964862619. It improves its parent but not the incumbent. Its mechanism
is a heterogeneous binary latent-sign direction, not a separate graphon family.
Quadratic Witt refinement has search-exact density0.030140295686154409; numerical
negative curvature is new evidence, but exact old-mean preservation needs audit.
Quotient transitivity and stabilizer order240 were recovered; a regular group
or particular abstract group identification is not yet certified.

All checkpoints below describe earlier windows, not current process state.

## Final research-window checkpoint — 21:03 UTC

All experimental lanes confirm their processes completed and were reaped. No
new experiment was admitted after21:00. The one-hour window ends21:04:08.
The final source/provenance bundle is being saved without running experiments.

**Read `campaign-2026-09-27-round2.md` and `current-state.md` first.**
Final independent direct-U256 incumbent: candidate
`reports/association-scheme-per-edge-boundary-continuation-001/graphon-candidate.json`,
SHA `d4763fefc34a3966bfbe811d279b522c067f193e436bb522d357dd423c0c58c3`.
Exact density16900934504649027287619486865996291/560768060721761383881293603555770368
=0.03013890356539909. Direct report SHA
`634a92d73e6c6e15e10e72a7d4da6462894862f73c528e798241eebca94d7b01`.
Adversarial checks pass; no kernel theorem, global optimum or record claim.

Later structural tests did not beat it. The exact quadratic k6 baseline is
0.030140621056356332; its fractional gradients are constant within relation
orbits, so their small residual is rounding, not symmetry-breaking descent.
Alternative quotient partitions and tested deterministic Seidel switches lost.
The visible3×64 factor is not a valid ordinary recursive composition factor.

Best next distinct test:384-class quotient from canonical pairs within original
four-vertex fibers, retaining a matched lifted-parent control. No further
experiment is currently running. The dashboard headline and cumulative graph
both include all supported independent evidence methods and the d476 incumbent.

Earlier checkpoints below are historical.

## Latest portfolio checkpoint — 20:54 UTC

User explicitly requested stronger parallel representation changes, not only
small refinements. Active CPU allocation now: correlated_graphon quadratic-form
relation family (CPU1); latent_precision exact factor/composition detection
(CPU2); finite_joint_search alternative intrinsic quotient partitions (CPU3);
precision_lean_audit final direct recount (CPU4). Stop new compute21:00, save
and reap by21:04:08. Adversarial reviewer audits latest family and numerical claims.

Current verified per-edge boundary candidate3f657ae0... has direct exact density
16900934506883319165303058334011571/560768060721761383881293603555770368
=0.03013890356938343; report graphon-association-per-edge-boundary-direct-u256-001.
Continuation d4763fef... predicts0.03013890356539909 and is in direct recount.
No more amplitude-polish jobs: last marginal gain was~7.7e-17 per sweep.

Dedicated adversarial33df and successor b93 audits live in
research/current-best-adversarial-audit.md. Both exact counting organizations
matched on33df. Every successor must retain its own evidence label.

Negative screens: original192 parent has no numerically detected inward boundary
gradient; fractional gradients are not exactly stationary. Exact sampled
diagonal-inclusive orbit lines did not improve it. Common nonuniform5-type
mass numerical screen did not improve b93. Hamming shell model failed tested
basins, BUT historical k10 control required red-clique diagonal; corrected
control32765943/1073741824 reproduces Franek–Rödl. Do not call the whole Hamming
family impossible; PPSS shell projection was not tested.

## Latest steering and infrastructure checkpoint — 20:35 UTC

User asked to continue seeking a substantially lower bound. Current deadline
remains21:04:08 UTC; stop new compute21:00. Root has reassigned existing agents:
fresh_hypotheses phase/amplitude alternation (CPU1), correlated_graphon changed
kernel library (CPU2), latent_precision joint coarse probability optimization
(CPU3), precision_lean_audit independent compressed checking (CPU4). Formal,
finite structural exploration, literature and adversarial lanes reason without
CPU initially. No new authority for paid/remote work.

Strongest exact native-recounted graphon is association-scheme-phase-001:
4126212387321705745944256745965/136906264824648775361643946180608
=0.030138959620340307. It ALSO passed the independent compressed recount in
graphon-association-phase-compressed-001. Full checking3.102s vs111.658s direct;
end-to-end5.248s including compile/tiny fixtures. Native code binds candidate
to histogram; Lean checks exact arithmetic. This is NOT full Lean candidate
reconstruction. Binary latent full independent Lean count remains available.

Reusable implementation in experiments/compressed_graphon/README.md and
experiments/verification_precision/run_typed_kernel_audit.py. Polynomial suite
13/13 passes; evaluator supports exact coefficient adapters/minimization with
normalization/provenance and proof gates. General typed histogram supports
oriented absolute kernels; polynomial feasibility utility restricts to symmetric
centered kernels. Do not conflate those interface scopes.

Dashboard headline and timeline NOW include all hash-valid independently checked
binary, weighted and graphon candidates. Legacy graphon reports lacking timestamps
use explicitly labeled report file timestamps. Timeline is cumulative minimum.
Latest finite result10486193484/768^4; finite-joint-two-switch-002, Lean checked.

Earlier sections below are historical, except authority/deadline constraints.

## Resumed campaign — 2026-09-27 20:04:08 UTC

User resumed and said to continue. Root explicitly announced and adopted a fresh
one-hour local research window, ending **21:04:08 UTC**, under the unchanged
four-total-CPU-job limit. The new runtime exposes nine total model-agent slots
(root plus eight subagents). Root owns coordination, evidence promotion,
dashboard and reporting; all experimental derivation/implementation/execution
is delegated. No paid APIs, remote compute, author contact, or official AutoLab
score claims. Stop admitting compute at21:00 and reserve the final minutes for
independent verification, persistent handoffs and process reaping.

Eight parallel lanes were started: full-precision Lean graphon recount;
latent-split transfer to the precision graphon; a new finite joint-quotient
mechanism; a distinct correlated-graphon mechanism; exact prior-art search;
asymptotic realization proof audit; adversarial artifact review; and fresh
independent hypothesis generation. Only the first four may own one CPU job
each. Later allocation changes must keep the same aggregate cap and be recorded.

User is restarting Codex with resume to apply eight-subagent configuration.
Read this first, then `current-state.md`, `approach-registry.md`, and worker
notes below. Read the installed hypothesis-research skill and its protocol.
Do not assume old agents or subprocesses survive; inspect before launching.

## Authority and coordination

- Root coordinates, reviews evidence, maintains dashboard and reporting.
  User explicitly requires all experimentation/derivation to be subagents.
- Project `.codex/config.toml` sets
  `agents.max_concurrent_threads_per_session = 8` (excludes root). The old
  session actually enforced four agents including root. Inspect the new
  session's supplied runtime limit; do not assume resume applies the setting.
- Eight agents does NOT authorize eight CPU jobs. Existing limit: four total
  CPU jobs including compilers/checkers, local only, no paid APIs/remote jobs
  or author contact. Research objective: strongest K4 multiplicity construction,
  not merely beating McKay; no global-optimum or novelty claims without evidence.
- Original one-hour pilot ran19:03:30–20:03:30 UTC on2026-09-27. Restart requested
  at~19:59:30 with roughly four minutes left. Do not silently reset the budget
  or extend past20:03:30. If resuming later, ask for a renewed research budget.
- Workers were told to stop admitting jobs, save artifacts and safely reap
  processes for this restart. Final confirmations are appended below.

## Checked results and evidence boundaries

1. Best finite/unit template:10486219192/768^4 (47,176 below McKay numerator).
   `reports/pilot-algebraic-cycle-polish-001/candidate.json`, SHA256
   `7dd4461967810f5780878b24ac64bd76858850fa0300a6a0aaa9f9170c926ee5`.
   Independent compiled Lean count in adjacent `report.json`.
2. Best weighted binary template:
   23059300053734294930609/765023370224882524618752≈.03014195507119723.
   `reports/weights-collective-curvature-002/candidate-weighted.json`, SHA256
   `45e79a75ab55c298d6c25cd3d5e3f93d6ff3305842091a203aafd66a1af42ee4`.
   Separate weighted Lean checker: adjacent `weighted-verification-v1.json`.
3. Strongest stochastic graphon:
   515776850799050572477656236153/17113283103081096920205493272576
   ≈.03013897728988013. `reports/literature-two-parameter-001/graphon-candidate.json`,
   SHA256 `e26e754168010c069da3e0b207a140f2c7cbbfc36cc0a6af06ef409db5024450`.
   Two different exact C++ counters and independent artifact/overflow audit;
   NOT yet full-precision Lean recount.
4. Simpler graphon, p=32/41,h=22/41:
   1013294255057839/33620705806123008≈.03013899413358829.
   `reports/literature-simple-graphon-001/graphon-candidate.json`, SHA256
   `33e2e141890bd1982f4233139bfcc904dfea845a109249f97c0bc264f5806f59`.
   NEW standalone compiled Lean recount PASSED in
   `reports/weights-collective-graphon-audit-002/report.json`;20 tiny arbitrary
   rational-matrix fixtures checked against Python big-integer ordered tuples.
   Existing frozen binary/weighted checkers and lakefile unchanged.

None of these is a kernel-only proof of counting correctness or asymptotic
realization. Graphon realization has an explicit first-moment prose argument:
independent edges among distinct expanded vertices, even when class indices
coincide. Do not reuse a randomly chosen finite template edge across a blow-up.
Density below announced .030139 does NOT establish improvement over the actual
Feinstein–Even-Zohar result; exact previous construction/value not obtained.

## Re-spawn assignments (three concrete lanes, then expand if useful/authorized)

### Algebraic / distinct structural exploration

Read `research/algebraic-round.md`, `reports/pilot-algebraic-summary.json`.
192×4 fibers → aligned first-bit voltages → exact3372-term C4 parity objective
→ cached local polish yielded three finite witnesses below McKay. Triangle-only
surrogate failed; finite four-sheet rounding of stochastic probabilities also
failed to beat best finite graph. Do not repeat seed/precision sweeps.
Latest assignment: independently challenge and tiny-test latent±type split of
each graphon class, P_(i,s),(j,t)=Pij+epsilon*s*t*Cij on fractional blocks.
Coordinate with literature notes; claimed cubic triangle mechanism is a
hypothesis, not established progress. Any384-block exact test requires fresh
overflow checks. Save this screen's status before restarting it.

### Literature / construction mechanisms

Read `research/literature-next-round.md`, `experiments/literature/` and named
graphon reports. Closest-prior search checked PPSS, voltage-cover literature,
graphon derivatives, Technion2026/RSA2025 announcements, author homepage and
linked public GitHub; no exact Feinstein–Even-Zohar witness retrieved.
Novelty remains unknown. Stop fine probability tuning; prioritize precise
prior-art comparison or a genuinely different representation. Latest idea is
the latent±type split described above; worker deriving explicit coefficients.

### Independent audit / collective weights

Former agent name `progress_updates` is historical: it is now a hypothesis
and verification worker, NOT dashboard owner. Read `research/collective-weights.md`
and `experiments/weights/collective_*`.
Collective gradient/Newton directions produced verified weighted gains.
Graphon mass gradient flat; sampled curvatures positive; exact PSD attempt
timed out at152/191 positive pivots—NO PSD/local-optimum claim.
Current priority is adversarial graphon audit, not more mass tuning.
Standalone `collective_graphon_audit.lean` and driver passed simpleQ41 audit;
audit001 preserves a failed initial compile, audit002 succeeded. Potential
next step: separately bounded Nat-based full-precision Lean checker, but user
restart interrupted admission of that task. Do not rerun completed simple audit.

## Dashboard, code, and handoff hygiene

`journal.html` refreshed19:58UTC with hash-gated binary/weighted Lean rankings.
Stochastic graphon reports currently intentionally excluded from those rankings;
add a distinct evidence section rather than silently treating them as same checker.
Refresh: `PYTHONPATH=src python3 -m k4_ramsey.dashboard --reports reports --out journal.html`.
Root may edit/test dashboard; all research experiments remain delegated.
Reports are immutable evidence. Use new run directories. Preserve dirty/untracked
worktree; no commits or destructive cleanup requested. Many files are untracked
but saved on disk. Do not rebuild shared native libraries beneath running jobs.

## Final worker/process checkpoint

All three workers confirmed their owned processes completed/reaped, none active,
at~20:01UTC. No high-precision Nat checker implementation/job was started.
Literature checkpoint is complete in `research/literature-next-round.md`;
audit checkpoint is complete in `research/collective-weights.md`.

Late completed latent-split result (do NOT rerun):
`reports/pilot-algebraic-latent-split-001/{graphon-candidate.json,expansion.json,report.json}`;
code `experiments/algebraic/latent_split.py`. Splitting to384 classes with
epsilon=-3/41 gives12357246284425/410008607391744≈.030138992356856135.
It improves its SIMPLEQ41 parent, but is weaker than the best high-precision
graphon. Independent ordered C++ recount passed in3.90s; six tiny expansion
tests include repeated base indices. Exact cubic/quartic expansion validated,
signed128 overflow bound checked. NOT yet Lean recounted.
Next discriminating experiment: apply this mechanism to the strongest graphon,
recompute coefficients and admissible support/epsilon/overflow rather than
assuming coefficients transfer. Resume only with valid time budget.
