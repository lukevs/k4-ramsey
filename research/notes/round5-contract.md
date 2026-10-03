# Round 5 contract — 2026-09-27

Window: 23:15 UTC – 00:15 UTC (2026-09-28). Admit no new compute after 00:08; save and
reap by 00:15. Coordinator: Claude Code root.

Checked incumbent at start: E4-3840 (`reports/round4-E4-exact-3840-001/graphon-candidate.json`,
SHA 594aaefb...), 2112616269946473812116180096163290703/70096007590220172985161700444471296000
= 0.030138895816959867 (independent rooted CRT recount under verified transitivity).
Pending: E5 depth-1 (1920 classes) audit by lane P; E5 depth-2 (3840) needs a structured checker.

Read first: `research/round4-root-pattern.md` (the pattern: every post-B192 gain is a
latent-correlation lift of B192's fractional edges; quadratic term vanishes; gain is cubic
over fractional triangles, opposed by quartic; diminishing returns, extrapolated limit
~0.03013887–0.03013888; target 0.030138 needs ~9e-7 more).

## Lanes

- **C1 ceiling (single dedicated thread):** analytic/computational upper envelope on what any
  lift of B192 can gain, and characterisation of B192.
- **F1 open support:** open the cheapest 0/1 levels jointly with a lift (H-R5-a).
- **F2 Ramsey-critical latents:** Paley(9)/Paley(13)/Paley(17)/Clebsch latent kernels with
  holonomy-informed starts (H-R5-b).
- **F3 basin census:** structure-free starts; distribution of finals; B192-isomorphism test.
- **F4 proofs:** exact global optimum of the B192 (p,h) family; strict local minimum of
  E4-3840 in its invariant space.
- **F5 structured checker:** independent character-expansion checker for Z2^k fibre lifts
  (E5 depth-1 cross-check, depth-2 audit).
- **P:** promotion gate and paper draft (continuing).

## Rules (unchanged from round 4)

Local only; no paid/remote work, outreach, or git commits. One single-threaded compute
process per agent at a time; per-job timeout 10 min unless justified in the lane notes. Each
lane writes only under `experiments/round5_<lane>/`, `reports/round5-<lane>-*/` (fresh dir
per run), `research/round5-<lane>.md`. Root owns shared state files. Search code never
promotes its own result; flag "SUBMIT FOR PROMOTION" with a rational-step-graphon-v1 JSON,
SHA and predicted exact fraction. Evidence labels per the hypothesis-research protocol.
Each lane ends with a hypothesis record, results, a decision and a next test.

## Amendment 23:19 UTC

User: cancel new-idea search except analytic saddle understanding (C1). F1, F2, F3
stopped. F4 (proofs), F5 (checker), P (audit/paper) continue. Main thread: write-up
with visuals showing PPSS-768 = rounding of 12 coupled Clebsch copies (B192).
