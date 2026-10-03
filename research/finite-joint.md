# Finite joint-voltage lane

## H-FJ-001: exact two-bit quotient-block moves

Family: F4/F1, a correlated structural neighborhood on the finite binary
four-sheet lift.  The parent is the checked cycle-optimized raw construction
in `reports/pilot-algebraic-cycle-opt-001/candidate.json`.

Mechanism: treat each of the 1056 defect blocks as one V4 voltage with two
bits.  A coordinate move replaces its missing perfect matching by another,
toggling eight ordinary graph edges while preserving every fiber-to-fiber
degree.  Both voltage bits are selected jointly with the exact finite
objective.  This strictly contains the fixed-first-bit move family used by
the C4 parity model and differs from another random voltage seed.

Prediction: starting from the fixed-first-bit cycle local minimum, at least
one joint voltage move using the first bit has negative exact delta; repeated
joint coordinate moves give a lower raw numerator than the `second_only`
control.  A full sweep with no joint move, or no advantage over that control,
disconfirms the mechanism at this parent and coordinate neighborhood.

Control: same input, randomized coordinate order, sweep cap, exact grouped
delta implementation, and seed.  The control permits only `old XOR 1`, the
second-bit move already represented by the C4 model.  Joint mode inspects all
three alternate V4 translations.  This is a neighborhood-existence test, not
an equal-evaluation claim of optimizer efficiency.

Validation: a tiny eight-vertex oracle checks all 16 old/new translation
pairs in four random surrounding graphs.  For each pair, sequential cached
deltas equal a full recount and rollback restores both graph and objective.
Production candidates receive a final native recount; only a subsequent
frozen compiled-Lean runner report can promote a finite witness.

`finite-joint-control-001` is a preserved infrastructure failure: the copied
strategy ran from its report snapshot, so a relative model path was unresolved.
The search did not start.  Both configs now name the immutable model by its
absolute path; this does not alter the hypothesis or candidate input.

Integrity note: the completed control found a net negative path even though
the earlier C4 optimizer reported a strict local minimum.  Inspection of the
new coordinate code shows it admits deterministic zero-delta tie moves when
`new_shift < old_shift`; its first accepted changes can therefore traverse a
plateau before a negative move appears.  A direct scan of the untouched parent
(`finite-joint-first-move-audit-002`) found no negative low-bit coordinate,
consistent with strict local optimality.  Audit003 now reproduces the plateau
prefix and compares every stored C4 coefficient delta to the exact grouped
delta before materializing the first subsequent negative move.  The broader
model-completeness interpretation remains withheld until that audit passes.

Resource: one CPU job at a time; source and reports confined to
`experiments/finite_joint` and `reports/finite-joint-*`.  Stop compute by
21:00 UTC and finish handoff by 21:04:08 UTC.

## H-FJ-002: matching-cycle escape after unrestricted polish

Mechanism: after ordinary single/star polish destroys exact J-minus-matching
blocks, retain the discovered quotient only as a move scaffold.  For each of
the1056 defect-block locations, toggle the symmetric difference of any two of
the four V4 matchings.  This is an exact eight-edge correlated move and does
not assume the current block still has lift form or preserves degrees.

Prediction: the new H-FJ-001 polished incumbent, despite being a restricted
single/star local minimum, admits a negative exact matching-cycle move.
Disconfirm at this parent if a complete sweep of all6336 moves finds none.
Every trial is rolled back; checkpoints and the retained candidate receive
full recounts, and promotion still requires the frozen Lean checker.

## H-ROOT-005: exact neutral-component exploration

Mechanism: the strict C4 coordinate minimum has eight zero-gain coordinates.
Breadth-first search the exact zero-gain component, stopping at the first state
that exposes a negative coordinate; take that coordinate, strictly descend to
the next local minimum, and repeat.  This tests plateau connectivity rather
than another random voltage seed.  Each state and move uses the stored exact
C4 coefficients; the final materialized graph must match a native full recount
and then the frozen Lean checker.

Prediction: systematic neutral traversal reaches at least one lower strict
minimum than10486901088.  The matched strict control is the untouched parent:
minimum one-coordinate gain0 with no negative coordinate.  A bounded run may
hit its state/time cap and does not prove the full neutral component exhausted.

## H-FJ-003: exact degree-two block escape after polish

Mechanism: use each of the96 original degree-two quotient blocks as a move
scaffold on the current polished graph.  Compare its archived regular4x4
pattern with every other regular degree-two pattern, toggling their symmetric
difference and evaluating the true finite objective.  This is distinct from
the earlier random pre-polish half-block assignment bank: it exhausts all89
alternatives per visited block, selects only exact negative moves, and makes no
claim that the polished block itself still has lift form.

Prediction: at least one of the8544 first-sweep alternatives escapes the
single/star/matching-cycle local incumbent.  A complete sweep with no accepted
move disconfirms this scaffold neighborhood at that parent only.

## H-FJ-004: guided exact degree-preserving 2-switches

Mechanism: choose two disjoint red edges and a blue cross matching on their
four endpoints, then toggle all four edges.  Every accepted move preserves the
full red degree sequence and is evaluated by exact sequential deltas with
rollback.  Candidate generation uses the192 cheapest red single-flip deltas
only as a surrogate shortlist; it is not part of certification.

Prediction: despite the incumbent's single/star local minimum, at least one
shortlisted degree-preserving 2-switch has negative exact delta.  Failure
establishes only a negative for the dynamically rebuilt shortlist, not all
2-switches.  Tiny arbitrary-graph rollback and degree-sequence checks precede
the bounded production run; final native and Lean recounts remain mandatory.

`finite-joint-two-switch-001` is a preserved pre-search failure: proposal keys
used increasing endpoint order while the cached-delta dictionary used the
native lower-triangle order.  The resulting `KeyError` occurred before any
trial or candidate write.  `edge_key` now follows the dictionary convention;
the move semantics and preregistered bank are unchanged for run002.

## Checkpoint at 20:28 UTC

- H-FJ-001 joint two-bit voltage descent improved the raw cycle parent by
  24,288 versus1,920 for the low-bit plateau control.  The matched polished
  result was10486204490 versus10486240028.  The apparent conflict with the
  older strict C4 local minimum was resolved: deterministic zero-delta moves
  traverse a plateau before negative moves appear.  Audit003 matched stored
  coefficients, sequential cached deltas, native recount, and Lean; an
  independent reviewer found no remaining integrity blocker.
- H-ROOT-005 systematically explored exact low-bit neutral components and
  made nine escapes for raw delta-4512.  Its matched polish ended at
  10486223544, worse than the strict-control polish10486219192.  Retire this
  as an incumbent route while retaining the exact plateau mechanism.
- H-FJ-002 matching-cycle moves plus local repolish improved the joint result
  through three alternating rounds.  Returns diminished from4932+3866 to
  504+216 and then240+0.
- H-FJ-003 exhausted all8544 regular degree-two alternatives in its first
  sweep, accepted three for delta-204, and found no local repolish move.  A
  partial second sweep accepted none.
- H-FJ-004 run002 screened a192-red-edge surrogate shortlist.  Sweep1 tried
  9,743 exact switches and accepted four for delta-1044; the rebuilt sweep2
  tried all10,596 proposals and accepted none.  The degree sequence and full
  native count were checked, followed by the frozen compiled-Lean recount.

Strongest finite artifact from this lane is currently
`reports/finite-joint-two-switch-002/candidate.json`, numerator
**10486193484 / 768^4**, exactly72,884 below McKay, SHA-256
`6b7c1fb28bc3b2c12cf47f5fc910047579af21afd8180bda2f0c73d212390e8a`.
The adjacent report SHA-256 is
`5162343d12d751fe4e7a8fdf1d2e58b273b1b63f0a63ddd3d2ca9a6821f9c0a4`.
Counts are red edges148710, blue triangles9130452, red K4s217033296,
blue K4s206110662.  This last candidate has not yet received the identical
single/star repolish because the coordinator reassigned the CPU slot to
infrastructure benchmarking.  No process owned by this lane remains active.
