# Twelve-block arrangement lane

Initial checkpoint: launched 2026-09-30; precise launch UTC in reports/assumption-block_arrangement-001/launch.txt. Reading required protocol, inherited family and negative evidence. No tests completed; no compute job running. Scope: own lane paths only; 15-minute wall budget with final two minutes for independent checking and handoff; one single-thread compute job, timeout 175 seconds. No promotions or shared evaluator modifications.

Checkpoint 05:25:38 UTC: read required negative evidence. H-BA1 tests random joint destruction of assignments incident to 3–5 coarse rows followed by full single-entry repair, against local-only repair with equal 45-second budgets, seed120012. Includes diagonal type assignments. Baseline and two asymmetric-template polynomial/direct checks precede search. Running tool session12666 (actual Python PID recorded in search.log). Hard process alarm175s; single-thread env set. All-coarse-tuple polynomial uses only proven simultaneous F2^4 translation, never coarse vertex transitivity. No candidate or promotion yet.

Checkpoint 05:26 UTC: Python PID78076 running, session12666. Baseline recovered .030138977289665386 versus full-root .030138977289665258; two asymmetric checks agree within4e-17. Local-only repeated scans find zero improving entries. Correct comparison parent is coarse B192 (.0301389772896653), not incumbent .030138887566497220. Local repeats are a wall-time control, not independent basin samples. Hypothesis registry: H-BA1 multi-row type destroy/rebuild predicts escape after coordinated damage; disconfirmed if all repaired endpoints are worse or equivalent. If unsuccessful, H-BA2 changes pairwise internal XOR alignment (frustrated cycle shifts), distinct from type-label reconstruction; gauge shifts are mandatory no-change controls.

Checkpoint 05:27 UTC: H-BA1 completed/reaped PID78076. 2529 structural repairs,48206 accepted repair moves,1132 distinct labelled endpoints,1091 exact parent returns; no improvement. Strongest changed endpoint ties baseline and is not yet claimed nonisomorphic. Matched local control45s found no move; repeats not independent evidence. Saved local.json,destroy_rebuild.json,basins.json,receipt.json and initial-checks.json. H-BA2 ready: pairwise XOR shifts with nonzero triangle holonomy,55s local-only vs55s cycle destruction/repair, seed121212. All12 coarse representatives retained, full-root asymmetric check and gauge relabelling control required.

Checkpoint 05:29 UTC: H-BA2 running Python PID78482, session44959. Base .03013897728966534, gauge control .030138977289665334; asymmetric representative count .0303021938429922 agrees all-root .030302193842992212. No coarse-transitivity assumption. H-BA1 no improvement; next artifact-only diagnostics will replay fixed-seed early trajectories to retain best nonisomorphic damaged basin (initial search retained only the best changed endpoint, which may be a relabelling). Independent six-edge recount and rationalized witnesses planned for final handoff.

Checkpoint 05:30 UTC: H-BA2 PID78482 completed/reaped. Structural cycle-shift lane32732 proposals,2728 cycle rebuilds, no improvement. Strongest nongauge shift found in local lane; after p/h polish .030207886614223547, worse. Diagnostic replay PID78729 completed/reaped: first700 fixed-seed repairs classified, explicit isomorphism proves tied strongest changed endpoint is parent relabelling. Best nonisomorphic saved basin .030147191848580585 at fixed p/h, polished .030146862072186763 (trial130). Not a new optimum/record. Search stopped; independent serialized-witness count and handoff only next. All prior jobs exited0; no active job at this checkpoint.


## Completed handoff

No candidate improves coarse B192 or the incumbent. All jobs completed and were reaped; no running lane process. Finished within the initial15-minute authorization, ending search early to preserve verification/handoff time.

| Test | Matched local control | Structural test | Best relative to coarse parent |
|---|---|---|---|
| H-BA1 type assignments |45s; zero accepted changes |45s;2529 multirow repairs,48206 repair moves |No gain |
| H-BA2 internal XOR alignment |55s;32771 proposals,zero accepted |55s;32732 proposals,2728 cycle rebuilds |No gain |

H-BA1 destroys assignments incident to3–5 rows, including diagonals, then repairs over all78 unordered coarse entries with4 possible types. This is not the old15bit internal defect or a regular product sweep. H-BA2 changes cycle holonomy of pairwise XOR shifts; gauge shifts are explicit no-change controls. Both retain every coarse root. Equal weights1/192, diagonal probabilities and all repeated indices enter every count.

The1132 distinct labelled H-BA1 endpoints are NOT1132 claimed graph isomorphism classes.1091 runs return exactly to the labelled parent. The best changed endpoint ties baseline and has an explicit parent isomorphism in isomorphism-diagnostics.json. First700 trajectories were replayed only to recover missing nonisomorphic artifacts:380 endpoints are nonisomorphic to parent; the best saved one came from trial130. This is not a claim to the best nonisomorphic endpoint among all2529 runs. It differs by an exact objective value, so cannot secretly be a graphon relabelling of the parent.

Strongest checked witness remains the recovered parent. Exact integer checker values:
- Baseline rationalized at denominator10^12: .030138977289665338.
- Best saved nonisomorphic type witness after shared p/h polish: .03014686207218672 (loss~7.885e-6).
- Strongest saved nongauge shift after polish: .030207886614223547 search value; independently float-recounted .03020788661422339.

Exact fractions, serialized witness hashes and checker hashes are in exact-types-check.json. The independently written checker enumerates98 internal triple categories, retains exact coarse permutation multiplicities, evaluates integer six-edge products, and binds every serialized192x192 entry. It imports no search evaluator or coefficient cache. A separately organized pair-root float recount reads rational artifacts directly; three tiny exact Fraction fixtures validate it. All floating discrepancies are <=2.31e-15. Parent audit is still separate; no promotion requested.

Sources: experiments/round4_E11/family.py and rule.json; the all-coarse-tuple polynomial and cached coefficients from experiments/clebsch_size_coarse/pilot.py and reports/clebsch-size-coarse-001/coefficients.npy; prior negatives research/coarse-alignment.md, coarse-seidel-switch.md, coordinated-reconstruction-round3.md and clebsch-size-coarse.md. Full source/input/checker hashes and actual commands/timings are in receipts and manifest.json. Search uses seed120012; shifts121212; tiny independent checks74102. No shared evaluator or parent-owned file edited.

Decision: retire these two bounded mechanisms; no global optimality, impossibility, novelty or record inference. Remaining gap: fixed shared probabilities and fixed Clebsch internal relations may block changes requiring jointly altered type assignments and heterogeneous probabilities. A future discriminating test should continuously reconstruct per-pair relation probabilities jointly with coarse types, compared to the current discrete barriers; more random starts alone are not justified.

Final checkpoint UTC: 2026-09-30T05:32:36.127600+00:00
