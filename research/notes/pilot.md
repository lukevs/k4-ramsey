# Local hypothesis-driven pilot · 2026-09-27

## Contract

Started 19:03:30 UTC. Hard stop 20:03:30 UTC; admit no new experiment unless
its total timeout fits before that stop. Local machine only, at most four CPU
jobs including tests/builds/verification. No paid services or author contact.
The coordinating session dispatches jobs directly; no queue daemon.

Goal: improve the K4 Ramsey multiplicity construction, beyond McKay and other
known constructions where possible. A reference crossing is not a stopping rule.
Initial domain: 768 unit-weight blocks, blue diagonal. Objective N / 768^4,
N = n + 14 E_blue + 36 T_blue + 24(K4_red + K4_blue). No global optimality claim.
The generic compiled Lean checker is frozen for this pilot; search primitives
and strategies may change with tests and versioned snapshots. Different
weights/diagonals require a separate, explicit verification extension.

Initial independently recounted incumbent: 10486706554 / 347892350976,
`reports/current-best-replay-001/candidate.json`. McKay reference numerator
10486266368. Newer 0.030139 announcement is a lead, not a reproduced witness.
Evidence means independent compiled Lean execution, not a kernel-only proof
of counting correctness or the asymptotic lifting theorem. No AutoLab score.

## Hypotheses and decisions

| ID | Family / prediction | Cheapest test | Status / decision |
|---|---|---|---|
| H0 | Single-edge descent: smoke candidate still has improving edges | Full edge scan; descent with fresh deltas; final exhaustive scan | Supported; local minimum reached |
| H1 | Exact matching subproblems: coordinated flips escape a single-edge minimum | Exhaustive tiny polynomial checks, then bounded matching search | Supported on H0 parent: four-flip escape |
| H3 | Interaction-guided neighborhoods outperform random neighborhoods | Matched-parent short screens after H1 validation | Suggestive only; random hit neighborhood cap early |
| H4 | Structural constructions/profiles open alternatives to edge edits | Primary-source review and tiny exact construction screen | Tested small-factor families uncompetitive; retire those families |
| H7 | Basin escape: temporary uphill edits find better descent basins | Controlled annealing versus continued descent, same parent/budget | Supported in two one-minute trials; continue best |
| H2 | Shared-center swaps have stronger interactions than disjoint matchings | Tiny exact interaction tests, then bounded incident-edge pairs | Implementation delegated |
| H5/H6 | Clone replacement tests integer block-mass redistribution at fixed order | Tiny replacement/rollback tests, then short candidate screen | Implementation delegated |

## Batch log

- Preparation: existing 16 tests and Lean build passed in previous turn.
  Current-best replay was byte-identical and independently recounted.
- Batch 1: establish a genuine single-edge local minimum rather than interpret
  sampled-descent stagnation as one. Matching/structural work proceeds separately.
- H0 result (`pilot-h0-scan-001`): Lean checked N=10486474490; 558 accepted
  flips across 24 scans; final exhaustive native minimum delta +2, no improving
  edge. Total 20.26 s. Remaining McKay numerator gap 208122. Next: use this
  explicit parent for coordinated edits and uphill search, not longer strict
  descent. Local-optimality scan is native diagnostic, not a formal theorem.
- H7 low (T=12) and medium (T=96) screens from H0, seed 1, 60 seconds each:
  Lean-checked gains 13512 and 53646 respectively. Medium best N=10486420844,
  gap 154476. Both accepted uphill moves; temporary regressions therefore
  succeeded where strict descent cannot. One seed is insufficient for a
  general temperature comparison. Continue medium incumbent for 300 seconds;
  retain other parents rather than silently change inputs mid-comparison.
- H1 pair screen exhausted the necessary eligible disjoint pairs (566 examined)
  with no gain in 1.46 search seconds. Guided 20-edge matching then found a
  four-flip gain of 24 in its first exact neighborhood, followed by 284 more.
  Final Lean-checked N=10486474182. Random 20-edge control found no gain in
  100000 neighborhoods, hitting the cap after 25.78 s rather than the 60 s
  budget; this is NOT a matched-duration superiority claim. Guided ran 60 s,
  1621 neighborhoods, 1620 solved exactly and one interrupted by its deadline.
- H4 structural profiles independently reproduce historical rational bounds.
  55444 finite n768 XOR/composition candidates and 2244 recursive candidates
  are uncompetitive; see structural-pilot.md. These are exact rational
  development screens, not Lean-promoted witnesses or a whole-family impossibility
  result. Retire these particular factor sets rather than lengthen the sweep.
- H2 shared-center swaps from H0 gained 47676 in 60 seconds (52 accepted).
  The first swap has interaction -2328 and joint gain 1464, while H0 had no
  improving single edge or disjoint pair. This distinguishes the mechanism,
  not just its parameters. All 15974400 screened pair evaluations are exact
  on the chosen endpoint sets, not an exhaustive all-pair optimality claim.
  A second screen starts from the stronger annealed parent to test combination.
- H5/H6 random clone screen: 22277 attempted replacements, none improving;
  best tested delta +42228, worst +825446. Retire unselected whole-clone moves
  in this regime; this does not rule out fractional weights or block refinement.
- Instrumentation: full single-delta rescans dominate each accepted star move.
  Derive and independently audit an incremental all-edge delta landscape using
  exact mixed interactions before optimizing this bottleneck. The objective
  and Lean checker stay unchanged; rebuild search backend between batches only.
- H2 combination screen gained another 19812 from the annealed parent,
  reaching 10486401032. The 300-second T=96 annealing continuation then reached
  10486397004 (130636 above McKay), versus only 92 gain for the exploratory
  T=384 / longer-cycle alternative. Retain the stronger parent and move to
  systematic neighborhood search rather than spending the budget on hotter
  random walks. This is not a general proof that high temperatures are worse.
- Display correction: reduced-fraction gap numerators confused comparisons
  (4291 and 5611 had different denominators). Dashboard headline and per-run
  gaps now use fixed 768^4-denominator units; ranking always used exact fractions
  and did not regress. Immutable experiment reports are unchanged.

## Coordination

Updated by explicit user direction: parent coordinates only; all experimentation
belongs to subagents. Each research worker owns its short round end to end,
including tests, runner dispatch and analysis, with at most two CPU jobs each.
They coordinate builds and honor the overall four-job cap. Parent reviews
evidence and promotes checked incumbents. Reporter owns dashboard regeneration
and three-minute updates. See [approach registry](approach-registry.md) for
independent families and dynamic reassignment, rather than fixed strategy teams.
Retain all failures and reports; promote only independently checked artifacts.
