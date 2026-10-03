# H10: eliminate all diagonal-color variables exactly

2026-09-27. Representation/internal-cluster-color family, distinct from
edge-edit search. Own elementary derivation, novelty not established.

Fix any symmetric binary off-diagonal matrix with **unit weights**. Let d_i
indicate changing diagonal i from blue to red. Partition an ordered quadruple
by repeated template indices:

- 4: contributes1 per vertex, independent of its diagonal color.
- 3+1: contributes4 for each ordered pair(i,j) when d_i matches edge ij.
- 2+2: contributes6 for each unordered pair(i,j) when both diagonals match ij.
- 2+1+1: contributes12 per repeated vertex i and unordered singleton pair
  {j,k} when the triangle ijk matches diagonal i.
- 1+1+1+1: independent of all diagonal choices.

Writing degrees and triangle incidences by color, the resulting numerator
relative to all-blue diagonals is exactly

    ΔN(d) = Σ_i L_i*d_i + 6*Σ_{i<j} d_i*d_j
    L_i = 4*deg_red(i) - 10*deg_blue(i)
          + 12*(tri_red_at(i) - tri_blue_at(i)).

Both red and blue off-diagonal pairs give the **same positive quadratic
coefficient6**. Thus at exactly k red diagonals the quadratic term is
3*k*(k-1), independent of which vertices are chosen. Sort the L_i values,
take prefix sums, and minimize prefix(k)+3*k*(k-1) over k=0..n. After counting
triangle incidences, optimization of all2^n choices costs O(n log n).

This proves a restricted exact optimization rule at the mathematical level;
it is not a formal Lean theorem or a global graph optimum. Unequal weights
do not preserve this fixed-cardinality reduction and need a separate analysis.

Validation before screening: every graph on1–4 vertices, every diagonal
assignment, compared with a literal ordered-four-tuple oracle; twelve random
five-vertex graphs, every assignment, likewise. Every fixed-k optimum and the
returned assignment are checked, not just the best scalar value.

The existing blue-diagonal checker is intentionally untouched. If screening
finds a strict gain, a separate versioned mixed-diagonal checker is required
before promoting it as independently checked research progress. No unchanged
blue-checker result will be attached to a changed-diagonal certificate.

## Bounded screen result

`reports/pilot-h10-diagonal-001/report.json` screened the published768 seed,
the H0 single-flip local minimum, and the retained cached-star incumbent
N=10486383582. **All-blue diagonals attained the exact restricted minimum in
all three cases.** Their blue baselines were independently recounted in Lean.
No changed-diagonal candidate was promoted, and no verifier was modified.

The three screens took approximately0.83,0.82,0.80seconds including baseline
Lean verification. Reports include all768 linear coefficients and every
fixed-red-count optimum, rather than just the best scalar. This eliminates
all2^768 diagonal choices for each of these fixed off-diagonal graphs under
the derived objective, contingent on the implementation/algebra rather than
a formal Lean optimization proof. It says nothing about simultaneous changes
of off-diagonal edges or unequal weights.

Decision: no further repetitions on unchanged parents; this exact optimizer
is reusable if a materially different off-diagonal construction appears.
