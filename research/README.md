# K4 Ramsey multiplicity research

Updated: 2026-09-27. Scope: AutoLab's
`clique-cluster-ramsey-multiplicity` problem, not classical Ramsey numbers R(4,t).

- [Current state](current-state.md): precise problem, reference bounds,
  relevant prior work, seed provenance, and current verification status.
- [Computational search plan](search-plan.md): exact move objective, testing,
  bounded local pilot, and evidence required for a result.
- [Bounds](bounds.csv): machine-readable seed and target fractions, with
  distinct evidence statuses.
- [Experiment dashboard](../journal.html): recorded statuses, independently
  checked values, and links to individual run artifacts.
- [Adjacent methods and hypotheses](adjacent-methods.md): targeted literature
  review, exact-neighborhood reductions, recursive constructions, weight
  optimization, and an ordered list of falsifiable experiments.

The aim is to go beyond published constructions, not merely meet AutoLab's
reference. A January 2026 seminar announces c4 < 0.030139; its construction has
not been obtained. See the adjacent-methods review for evidence and limitations.

The earlier off-diagonal Ramsey-number review and table were removed because
they addressed a different problem. The working direction is computational
search coordinated by the assistant, without pydantic-ai or a paid model loop.
Only short runner-validation results are recorded so far; the one-hour pilot
has not started.
