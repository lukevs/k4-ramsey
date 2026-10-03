# H-CR-001: solver-guided coordinated reconstruction

Date: 2026-09-27. Status: first bounded gate completed; no candidate.

## Test

No SAT, MaxSAT, or integer-programming package was installed locally, so this
pilot used exact exhaustive enumeration rather than adding a dependency. On the
frozen order-192, denominator-65536 rational graphon, it selected the six-class
structured core

```
[0, 62, 67, 69, 73, 104].
```

These are root class 0 and the first representatives of its five fractional
automorphism orbitals 10, 11, 12, 13, and 16. All 15 internal off-diagonal
positive-mass block probabilities were jointly replaced by either 0 or 1.
Every one of the `2^15 = 32768` assignments was evaluated exactly.

For each nondecreasing class quadruple touched by one of the 15 variables, the
native evaluator retains its permutation multiplicity, all repeated indices,
and fixed diagonal probabilities. Red terms are aggregated by the set of
variables required to be 1 and blue terms by those required to be 0; subset
zeta transforms then give every binary assignment. A separate order-6 tiny
fixture literally enumerates every ordered quadruple for all 32768 assignments
and agrees on the exact optimum and witness.

Controls were exact sequential one-bit descent from threshold rounding on the
same core and the identical global/sequential computation on a seeded random
six-class set `[18,19,30,61,80,124]`.

## Result

The structured global optimum and sequential control are the same witness.
They increase the full raw numerator by

```
54715471171528470976482329427968
```

and have density approximately `0.030139485479330125`, worse than the fractional
parent `0.03013897728988013`. The random control already has deterministic
internal edges; its global and sequential optima reproduce the parent exactly.

Thus this precise binary six-class defect supplies neither an improvement nor
a coordination advantage over sequential descent. It says nothing about
larger defects, changes to external block edges, unequal masses, nonbinary
reconstruction, or the broader group-difference defect encoding.

## Throughput and evidence

Setup-to-first-result was about 150 seconds. The native process took 0.743
seconds including its exhaustive tiny oracle; each production neighborhood took
0.231 seconds. The immutable report is
`reports/coordinated-reconstruction-001/report.json`, SHA256
`1eb1a51be61d83d88f58854834ed977b0b7f760c61134d8ac20fcbb577ec3ac2`.
The source snapshot SHA256 is
`148ce43e51d052ffb3e4c2bd68674c7340d5683485215a571fe0279c82b01e44`.
