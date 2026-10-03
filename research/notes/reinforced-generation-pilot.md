# Reinforced-generation procedure pilot

## What was transferred

This lane pursues the procedure-level direction in Nagda et al., *Reinforced
Generation of Combinatorial Structures* (arXiv:2603.09172), rather than another
small parameter family.  The first implementation transfers four concrete
ideas from their Ramsey search:

1. grow a retained construction by cloning one positive-mass type;
2. deliberately destroy part of the new/interacting region to leave the old
   local basin;
3. make a 75% attempt to draw a repair proposal from a current monochromatic
   `K4` witness, falling back to random when witness sampling fails;
4. use reheated perturbation chains and retain the best checkpoint before a
   final strict repair.

This is not a literal implementation of their reinforcement/meta-program
evolution.  It is the first hand-built operator portfolio that produces the
feedback such a controller would consume.  A later controller could learn the
donor, destroy radius, operator, and reheating schedule from exact gains.

Their zero-violation objective was not reused.  Every accepted/rejected move
uses the native exact blow-up numerator

`n + 14 E_blue + 36 T_blue + 24(K4_red + K4_blue)`,

whose denominator is `n^4`.  This is exactly the asymptotic density of the
equal-mass deterministic step graphon with blue diagonal.  Thus repeated type
indices and diagonal semantics are included.  A five-type literal ordered
tuple oracle, including repeats, agrees with the native evaluator; sequential
delta/apply/rollback drift controls also pass.

## Matched protocol

Each procedure arm and baseline uses the same source, donor, RNG seed, and wall
cap (not necessarily the same consumed compute, because a certified local
baseline terminates early).  The baseline clones the donor (or retains the fixed-order parent) and
runs exhaustive cached best-single-edge repair.  The procedure arm retains
that undamaged point as a portfolio checkpoint, flips 32 incident edges,
runs witness-guided/reheated Metropolis using exact sequential deltas, then
strictly repairs its best checkpoint.  The baseline often terminates early
because it has an exact single-edge local certificate; the procedure may use
the remainder to seek another basin.

Two genuinely different `n=192` sources were used:

- one representative from each certified four-vertex fiber of the strongest
  finite `n=768` construction;
- an independently seeded random symmetric coloring.

The strongest binary finite-derived `n=768` construction was then tested
directly, both by growth to `n=769` and by fixed-order destroy/rebuild.  It is
not the overall graphon incumbent: the independently verified `d476`
probabilistic graphon is stronger, at `0.03013890356539909`.

## Results

| source | seed | baseline | grow/rebuild | result |
|---|---:|---:|---:|---|
| algebraic quotient 192→193 | 17 | 0.0302261230149550 | 0.0302261230149550 | tie; retained clone |
| algebraic quotient 192→193 | 43 | 0.0302246988584949 | 0.0302246988584949 | tie; retained clone |
| random 192→193 | 17 | 0.0317323645092914 | 0.0317511495366078 | rebuilt basin worse |
| random 192→193 | 43 | 0.0317323933383695 | 0.0317382441997781 | rebuilt basin worse |
| best binary finite 768→769 | 17 | 0.0301424047755507 | 0.0301424047755507 | tie; worse than 768 parent |
| best binary finite, fixed 768 | 17 | 0.0301420639303547 | 0.0301420639303547 | tie; retained parent |

The full fixed-order campaign is the strongest diagnostic.  It evaluated
40,800 exact proposals, of which 30,433 came from current monochromatic
ordered-`K4` witnesses.  It accepted 5,877 moves, including 3,508 uphill moves,
and performed five reheats.  Nevertheless, no intermediate state beat the
retained binary parent `10486193484 / 768^4`.  The matched baseline
independently confirmed that parent is single-edge local.  This density is
still worse than the overall `d476` graphon incumbent.

For growth to 769, the best reached numerator was
`10541035035 / 769^4 = 0.03014240477555072`, which is worse than the 768 parent
by about `3.41e-7`.  Changing order therefore did not hide an improvement in
the raw numerator comparison.

## Interpretation and next procedural update

The experiment falsifies this particular single-focus, radius-32,
edge-proposal schedule as a useful basin escape on the tested sources.  It does
not falsify reinforced generation generally.  The telemetry suggests the next
controller/operator change should be structural: destroy and rebuild a
multi-type interacting region or propose coherent matching/quotient moves,
rather than performing more individual edge proposals inside one damaged row.
The existing exact two-switch and matching-cycle operators are natural actions
for such a portfolio.  Reward should be exact density improvement per wall
second, with the undamaged checkpoint always retained.

Plain relabeling was intentionally omitted from reheating: this evaluator and
deterministic cached search state are permutation-equivariant, so relabeling
alone cannot change the basin.  Each reheat instead uses exactly three exact
random perturbations, which is the nontrivial part of the paper's prescription here.

## Artifacts

- implementation: `experiments/growth_repair/run.py`
- small matched gate: `reports/growth-repair-pilot-001/report.json`
- full growth gate: `reports/growth-repair-full-incumbent-001/report.json`
- full fixed-order gate: `reports/destroy-rebuild-full-incumbent-001/report.json`

Final implementation SHA-256:
`901e7aa39fb471f7229616275f1aba46322868e875b816a7f22db11805a5c253`.
