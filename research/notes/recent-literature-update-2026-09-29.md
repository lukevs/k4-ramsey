# Recent research update — 2026-09-29

Targeted primary-source review for the active K4 multiplicity, Clebsch and
coupled flag-relaxation questions. Papers and repository documentation were
read; no third-party package was installed, no proof library was built, and
no author was contacted. A search without a hit is not proof of absence.

## 1. Clebsch and overlapping local constraints

[Davey–Hurley–de Joannis de Verclos–Kang–Volec, Local flag algebras](https://arxiv.org/html/2607.12461v1),
14 July 2026, is the strongest newly located structural connection.
It studies pentagons in triangle-free graphs with maximum-degree normalization.
The general sharp Clebsch conjecture remains open; the maximum-degree-five
equality case is proved. Section 7 supplies non-Clebsch examples saturating
one rooted bound: equality at all vertices is needed to force Clebsch.
Its size-eight plateau discussion is explicitly heuristic.

Our proposed transfer: extract the overlapping-neighborhood equalities from
Section 7 and test whether they suggest a useful *universal* collection of
rooted features. The target objective and degree normalization differ from
ours, so its inequalities cannot simply be inserted into our K4 program.

[Accompanying code](https://github.com/rossjkang/localflagalgebras) includes
Rust generators and Lean files. Its README explicitly lists remaining domain
axioms for some headline results. Check `AxiomCheck.lean` and `RESULTS.md`
before describing any imported theorem as fully verified from standard axioms.

## 2. A general certificate-to-Lean pipeline

[Jeong–Park–Hyun–Oum–Yang, Formalizing Flag Algebras in Lean](https://arxiv.org/abs/2607.23500),
26 July 2026, provides a general flag-algebra formalization and a compiler
for externally generated certificates.
[Repository](https://github.com/taeyool/lean-flag-algebras-release):
`flag_certificate` consumes Flagmatic certificate JSON. Five examples use
kernel evaluation; two larger examples additionally trust compiled evaluation.

Our proposed test: adapt the checked six-vertex certificate to the expected
format and express the correct K4-plus-complement objective. This could close
the current gap between exact arithmetic checking and a formal proof of the
flag-algebra implication. Compatibility with our mixed-size blocks and linear
objective needs inspection; no successful import is claimed.

## 3. Modern flag-algebra software

[Bodnár, FlagAlgebraToolbox](https://arxiv.org/html/2601.06590v1), January 2026,
documents a SageMath fork with CSDP and Bliss. It supports typed positivity
assumptions, rational rounding, and weighted probabilistic blow-up constructions.
The documented revision is `9a9f84d`; source is
[bodnalev/sage](https://github.com/bodnalev/sage).
Construction-assisted rounding assumes the construction nearly matches the
numerical optimum; it does not establish optimality of an arbitrary candidate.

Our proposed test: independently reproduce our N6 numerical and exact bounds
before considering N7/N8. This is a stronger use of effort than extending our
prototype without comparison. Do not impose constant bridge degrees in a
universal problem merely because this API permits typed assumptions.

## 4. Sparse-plus-low-rank SDP conversion

[Tang–Toh, Exploring chordal sparsity in semidefinite programming with sparse
plus low-rank data matrices](https://arxiv.org/abs/2410.23849), October 2024
preprint, develops conversions to sparse SDPs with bounded tree-width for
structured data. A [2026 SIAM journal version](https://epubs.siam.org/doi/10.1137/24M1694112)
was also located.

Our proposed test: inspect the aggregate support and low-rank components of
the actual coefficient matrices before selecting a solver architecture.
Sparsity of the graph construction does not imply sparsity of the SDP.
Such conversion could reduce solver cost; it does not by itself avoid
enumerating the higher-order density variables or their consistency relations.

## 5. Recent small-pattern extremality and stability examples

[Bodnár–Pikhurko, Some exact inducibility-type results for graphs via flag
algebras](https://arxiv.org/abs/2507.01596v4), revised 11 February 2026,
provides new exact cases, structural results, notebooks and certificates.
This is a useful reproducibility/stability reference, not a K4 multiplicity
improvement. The linked ancillary files make it a candidate source of small
cross-check problems for a new toolchain.

[Their Semi-inducibility of 4-vertex graphs](https://arxiv.org/abs/2510.24336)
studies partly specified red/blue patterns, a close language match to our
rooted features. The [Warwick publication record](https://wrap.warwick.ac.uk/id/eprint/201806/)
reports availability in June 2026 and an October 2026 issue date; do not
mistake the future issue date for an unavailable result. No direct
improvement to our objective was found in this review.

## 6. Direct K4 status and publication caution

No newer verified universal K4 lower bound was located beyond the previously
identified GLLV result around 0.0296. The original paper is
[On tripartite common graphs](https://arxiv.org/abs/2012.02057).
KPS's approximately 0.02961 remains explicitly numerical in its
[discussion](https://arxiv.org/html/2312.08049v1#S7).

The [Feinstein January 2026 announcement](https://math.technion.ac.il/events/noam-feinstein/)
still states c4 < 0.030139 and describes structured randomized constructions.
The [RSA 2025 abstract](https://www.dmg.tuwien.ac.at/rsa2025/) identifies the
joint work with Even-Zohar. This search did not locate their full construction,
exact value or new preprint. Our record and overlap questions remain unresolved.

Excluded from the actionable list: ordered Ramsey multiplicity, Ramsey-number
search records, and FlagSparse GPU software. Their terminology matches but
their mathematical tasks do not supply the missing global K4 constraint.
The [FlagScale project](https://iol.zib.de/project/flagscale.html) is relevant
background, but its listed funding window ended September 2025; this review
did not locate a new public K4 certificate or turnkey sparse closure there.

## What changes in our plan

1. Prioritize the local Clebsch equality argument as a source of *coupled*
   features; compare whole overlapping families, given our ablation results.
2. Benchmark established flag software on the checked N6 instance before
   enlarging our own implementation.
3. Treat formal certification as a separate, concrete route to improving
   the write-up. A solver improvement and a proof-verification improvement
   are distinct results.
4. Profile matrix structure before adopting sparse SDP machinery.

These are proposed tests, not launched experiments. The literature reinforces
that flag squares, shared density variables and rational rounding are existing
methods. Our pilot establishes correct reproduction and coupling behavior;
it is not presently a novel lower-bound technique.
