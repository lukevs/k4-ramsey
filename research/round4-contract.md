# Round 4 contract — 2026-09-27

Window: 22:12–23:12 UTC. Admit no new compute after 23:05; save and reap by 23:12.
Coordinator: Claude Code root (coordination, review, state files only).

## Objective

1. **Publishability lane (P):** turn the incumbent d4763fef (0.03013890356539909,
   exact 16900934504649027287619486865996291/560768060721761383881293603555770368)
   into a publishable, reproducible result, and act as the independent
   promotion gate for any new candidate from exploration lanes.
2. **Seven exploration lanes (E1–E7):** materially different mechanisms
   aimed at a *robust* margin under the unpublished Feinstein–Even-Zohar
   announcement (c4 < 0.030139). Target of interest: below 0.030138.
   Refinement of d476 by more amplitude polishing is not an exploration lane.

## Rules

- Local only. No paid/remote jobs, no outreach, no git commits/pushes.
- Each agent owns at most ONE single-threaded compute process at a time
  (8 total; machine has 18 cores shared with other services). Per job timeout
  10 minutes unless the lane doc records a justification.
- Each lane writes only under `experiments/round4_<lane>/`,
  `reports/round4-<lane>-*/` (fresh directory per run) and
  `research/round4-<lane>.md`. Do not edit shared state files
  (RESUME.md, current-state.md, README, journal.html, approach-registry.md);
  root owns those.
- Search code never promotes its own result. Candidates go to lane P as a
  `rational-step-graphon-v1` JSON + SHA + predicted exact fraction; P runs
  `experiments.verification_precision.run_direct_u256_audit` (or another
  checker independent of the search code).
- Evidence labels per the hypothesis-research protocol. A failed heuristic is
  a restricted negative, not an impossibility result.
- Every lane ends with: hypothesis record (claim, prediction, disconfirmation),
  what ran, exact results, decision (pursue/revise/retire), next test.

## Amendment 22:30 UTC

User asked for more ideas. Added E9 (twisted voltage lifts of B192 beyond Z5,
building on lane P's finding that the Z5 pentagon lift is the largest single
gain) and L1 (record-status literature sweep, no compute, no outreach).
Total: 10 agents, at most 9 concurrent single-threaded jobs. E6 retired; E8 in its slot.

## Amendment 22:33 UTC

User asked for a parallel research review. Added R1 (literature-driven scan,
brainstorm before reading our notes) and R2 (first-principles structural review).
No compute beyond seconds-long sanity checks. Their proposals feed the next batch.

## Amendment 22:46 UTC

From R1/R2 reviews: added E10 (holonomy symmetry + D5 voltages), E11
(Clebsch-block base family), E12 (lambda-continuation). Up to 12 concurrent
single-threaded jobs. Deadline unchanged: no new compute after 23:05 UTC.

## Next-round priority (recorded 22:56 UTC, from user steer)

User: convergence of diverse approaches on the ~0.0301389 plateau would be
valuable for publication. Current routes (d4763, E4, E7) all plausibly pass
through the B192 Clebsch structure, so they are not yet independent evidence.
Lead lane next round: basin census — many structure-free starts (free kernels
or random Cayley kernels at sizes that can contain B192), report distribution
of final values and whether low finals are B192-isomorphic (quotient/automorphism
test). Keep an explicit independence column (shares B192? yes/no/unknown) for
every route in the paper's convergence table.

## Amendment 23:01 UTC

User asked about proving Clebsch-based optimality. Added L2 (literature/theory,
no compute, deadline 23:35). E1 note: its 768 lift equals the published PPSS
value exactly (13655163/768^3); isomorphism untested.

## Amendment 23:01 UTC

E5 submitted two candidates below the E4-3840 incumbent (search-side).
Coordinator authorises ONE extra single-threaded audit by lane P of the depth-1
(1920-class) candidate past 23:12, cap 60 min. Depth-2 (3840) audit deferred
to next round (needs structured checker).
