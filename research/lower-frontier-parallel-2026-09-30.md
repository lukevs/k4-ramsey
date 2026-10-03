# Three lower-bound research lanes — 2026-09-30

User explicitly requested three agents, one for each proposed direction.
Initial scope: 15 minutes per agent for a concrete first result and handoff;
individual compute jobs <=180 seconds, one single-thread compute job per agent,
at most three concurrently. Root reserves the fourth historical CPU slot for
independent review. Local only; no paid/remote compute, outreach, commits,
publication or new agents. No automatically renewed research window.

Objective: strengthen the universal asymptotic c4 lower bound or establish a
specific tested obstruction/new usable inequality. c4 is inf_W of red plus
blue K4 homomorphism densities, including repeated latent class samples.
Never assume Clebsch structure, regularity, or triangle-freeness globally.

| Lane | Task | Required first deliverable |
|---|---|---|
| A | Recover strongest existing N9 computation | Located reproducible data/code or bounded reconstruction test and measured resource plan |
| B | Local-to-global inequalities | Explicit universal inequality with checked normalization and nonredundancy test, or counterexample/obstruction |
| C | Necessary near-optimal structure | Quantitative candidate structural lemma, tested on diverse constructions, with proof or precise remaining gap |

Each agent owns only `research/lower-frontier-{A,B,C}.md`, respectively,
`experiments/lower_frontier_{A,B,C}/`, and `reports/lower-frontier-{A,B,C}-*/`.
Only A may launch Sage in the flag-sage container, using a dedicated working
directory to avoid param.csdp collisions. No shared source/checker edits.

Numerical screen, exact search-side output, independently checked certificate,
and formal proof must be distinguished. Root alone promotes results after
review. All agents must save commands, timeouts, hashes, sources, results,
failures and process state, and return a pursue/revise/retire decision.

Starting evidence: N6/N7 checked bound 0.028750924686580158; no improvement
from C5/P5/complement-P5 additions. KPS report N9 numerical 0.02961 without
exact rounding. Published ~0.0296 benchmark is stronger than our small pilot.
Recent upper-search certificate diagnostics found a P4 term ~35% of the gap,
but targeting it in a 12-parameter coarse family worsened true density.

Status: all three agents launched at about 04:01 UTC. First handoff deadline
04:16 UTC. No research result yet.

- A / Ampere: `01a0f079-81ad-79e3-9e44-a4777265db2a`.
- B / Aristotle: `01a0f079-8240-7f92-907a-f86483cbfdb7`.
- C / Bohr: `01a0f079-82d2-7240-80c2-991f65896231`.

Root review gates: A must distinguish K4-specific N9 data from unrelated
certificates and numerical output from rational certification; B must prove
validity for arbitrary graphons and check whether proposed new moments can
be completed freely; C must avoid inferring universal structure from a
favored candidate or imposing equality at a non-tight certificate. Every
claimed strengthening must be compared to the same baseline/domain and
checked separately before promotion. Root handles integration, not duplicate
experiments while these lanes run.

## Added literature lane

User subsequently authorized one additional deep literature agent, with the
full research history. L / Wegener: `01a0f080-6cff-75e0-9674-73e820f8001b`.
Its separate scope is up to 25 minutes of primary-source literature review,
with an interim checkpoint around 10 minutes. No experiment compute, Docker,
outreach, paid work, commits or further agents. A/B/C deadlines are unchanged.
Agent inherited conversation context and an explicit briefing covering the
incumbent, published versus announced bounds, failed transfer arguments,
free-moment obstruction, N7 negative tests, certificate-guided search failure,
and provisional A/B/C findings. It must read the corresponding research notes.
Deliverable: `research/lower-frontier-literature-2026-09-30.md`, ranked sources
with precise mechanisms, assumptions, differences from tested ideas, and cheap
discriminating tests. Root retains mathematical review and integration.
