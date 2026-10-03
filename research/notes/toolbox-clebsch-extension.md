# Toolbox Clebsch extension pilot

User authorized proceeding after installation and N6 reproduction. Focused
main-thread pilot, no distributed search, remote compute, paid work or outreach.
One local compute process at a time, BLAS/OpenMP single-thread, 180-second
per-run timeout, at most four initial solves plus one exact-rounding follow-up.
Stop for synthesis and verification after this bounded batch.

## H-TC1

Claim: adding the five-root pentagon flag Gram block to the existing N6
constraints, with shared nonnegative seven-vertex densities, improves the
universal K4 multiplicity relaxation. This is standard flag algebra machinery;
the literature-inspired choice of type is the hypothesis, not a new inequality
method. No triangle-free or Clebsch assumption is imposed on the target graph.

Controls: N6 constraints lifted to N7 without additional Gram blocks; same
plus C5 block; same plus all five-root blocks; full N7 together with old N6
blocks if timing permits. A gain >1e-6 is the numerical screening threshold.
Separate results for bare induced-density extension and added rooted squares.
All variants use exactly the same K4 + independent-four objective.

Scope: this small pilot does not test the six-root C5-plus-isolated block
at order ten, nor improve the published ~0.0296 lower bound by itself.
Keep any numerical result provisional. Export a certificate if a useful
gain appears; independently check before promoting a rigorous bound.

References: [FlagAlgebraToolbox](https://arxiv.org/html/2601.06590v1),
[Local flag algebras](https://arxiv.org/html/2607.12461v1), and our
[earlier coupling pilot](global-coupled-pilot.md).

Status: completed; no remaining jobs. Installed fork revision
6d8c7d2ecfa8b27d8373d1987678dc34c84ed45a, with documented ARM setup patch.

## Results and adaptation

| Variant | Numerical value | Outcome |
|---|---:|---|
| N6 constraints projected to N7, 13 types | 0.0287499650563 | Reduced accuracy; not evidence of a decrease |
| Plus C5 type, 14 types | 0.0287509246940 | No measurable improvement over N6 |
| Plus all five-root types | — | Timed out at 180 seconds during table generation; no solve |
| Plus C5, P5 and complement(P5), 16 types | 0.0287509244491 | No measurable improvement over N6 |

The broader table generation cost about 16 seconds per new five-root type.
Instead of extending that run, replaced the planned full-N7 solve by the
smaller pentagon-neighborhood family: deleting one pentagon edge gives P5;
adding an edge gives its complement up to isomorphism. These two types and
C5 form a colour-complement-closed selection. Runs took approximately
85, 28, 180 (timeout), and 46 seconds. No full N7 result was obtained.

## Independent exact certificates

The toolbox exported numerical dual matrices and graph/flag definitions.
Our new checker imports no Sage multiplication tables: it rounds duals to
integer matrices, adds a small diagonal correction, checks positive
definiteness by exact rational LDL, and enumerates all 5040 orderings of
each of the 1044 seven-vertex representatives. It checks that their disjoint
orbits cover all 2,097,152 labelled graphs. The objective is independently
counted from all 35 four-subsets. Five representative coefficient sums also
agree with a separate literal Python enumeration.

The pentagon run yields the independently checked certificate

    c4 >= 36226165105091 / 1260000000000000
       = 0.028750924686580158...

The three-type run gives 18113082423397/630000000000000,
approximately 0.02875092448158254. Their tiny difference is not evidence
that adding constraints weakens the optimum: these are two feasible dual
certificates with different numerical approximation/rounding losses.

An initial certificate import missed the toolbox's positive padding factors
for products using fewer than seven vertices: factors 3 for the old two-root
blocks and 2 for the old four-root blocks. That unscaled proposal produced
only a useless negative bound; preserved under `pentagon-independent/`.
Corrected proposals are in `pentagon-independent-v2/` and
`neighbors-independent/`. Scaling is only part of proposing a dual matrix:
the independent checker reconstructs the final bound itself, so correctness
does not rely on assuming that this import reproduces the solver's answer.

As in our earlier certificates, for every graph H the checker establishes
c(H) - sum_b <Q_b,C_b(H)> >= L. On averaging over graphon samples, every
C_b becomes a positive-semidefinite rooted Gram matrix, so c4 >= L.
This is exact native computation plus the usual flag-square argument, not
a proof-assistant certificate or a finite-n injective lower bound.

## Decision

H-TC1 is unsupported in the tested regime. The certified value reproduces
the existing small-level numerical result; its small increase over our older
0.028750881 certificate is improved rounding, not a demonstrated hierarchy
gain. It remains below the published ~0.0296 lower bound.

Do not simply add more starts or claim that pentagon structure has improved
the universal bound. A next experiment needs a materially stronger coupled
feature (such as the earlier six-root contrast and its shared higher moments)
or a planned larger hierarchy computation. The N9 baseline and tractable N10
closure remain unresolved. No local/global optimality conclusion follows.

Artifacts: `../reports/toolbox-extension-001/`; scripts
`toolbox_extension.sage`, `export_toolbox_certificate.py`, and
`check_toolbox_n7.{py,cpp}` in `../experiments/clebsch_bowl/`.
