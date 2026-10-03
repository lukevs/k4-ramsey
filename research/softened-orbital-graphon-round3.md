# Full orbital graphon from a softened start

Date: 2026-09-27. Status: completed single-start structural gate; no candidate.

## Hypothesis

The five fractional-orbit test cannot cross deterministic boundary faces.
Release every symmetric orbital mean of the full color-preserving automorphism
action after moving the original order-192 graphon into the box interior via

```
P_delta = (3/4) P + 1/8,  delta = 1/8.
```

At denominator 65536, `(6*p+65536)/8` is integral for every original orbital
except the `p=35015` orbital. That value is rounded from 34453.25 to 34453;
all other rounding errors are zero. This lattice rounding is explicitly part
of the tested start.

## Structural controls

The recovered action has 24 directed orbitals. Every orbital is self-transpose,
so merging with reversal leaves 24 symmetric relation IDs. The relation matrix
exactly reconstructs all 192 squared entries of the frozen parent; relation 0
contains every diagonal cell and has original probability zero. The softened
probabilities are all strictly inside `(0,65536)`.

An exact frozen run of the original parent in these same 24 coordinates gives

```
515776850799050572477656236153 /
17113283103081096920205493272576
= 0.03013897728988013...
```

matching the established parent. The independently frozen softened start is

```
45472636391739650948276789297755 /
1460333491462920270524202092593152
= 0.031138528738518807...
```

## Result and optimizer audit

Releasing all 24 orbital means gives a negative local Hessian proposal
(`-0.003566462700569724`, residual `3.40e-17`). The v1 engine moved to a
continuous value about `0.0307470158623`; its exact denominator-65536 rounding
had density

```
1436829221010865790802818489686417 /
46730671726813448656774466962980864
= 0.030747026907949025...
```

Adversarial review found that v1's global box cap let one coordinate at a wall
starve all other free-coordinate updates. It is therefore retained only as a
failed engine path, not basin evidence.

The identical config was rerun after the shared engine owner froze the minimal
active-set v2 fix. V2 reached continuous `0.030139090151352438` and exact
rounded

```
0.030139090196961885...
```

This is materially better than v1, but remains worse than both the original
order-192 parent and the current incumbent `0.03013890356539909`. Moreover,
v2 terminated by `line_search_stall` after 286 iterations with 17 active walls
and projected KKT infinity norm `2.5728545e-5`; it is not a converged orbital
optimum. Per preregistration, the single start is stopped here: no seed sweep,
custom optimizer, materialization, or promotion is justified. This is evidence
only that the prescribed engine path did not produce a candidate, not a global
or basin-level negative result for the orbital family.

## Evidence

- Construction audit:
  `reports/softened-symmetric-orbitals-config-001/audit.json`, SHA256
  `67cbdf09f3951dd81ca849250b982a77d3be107ef692b760ce3fe2ac38824374`.
- Original frozen control:
  `reports/original-symmetric-orbitals-frozen-001/report.json`, SHA256
  `6295dc4ae705043cbb8c1f475731b68291fc630a809e65507a4d075bf970bd7d`.
- Softened frozen control:
  `reports/softened-symmetric-orbitals-frozen-001/report.json`, SHA256
  `6a0158586f26b3e67cb77160e5792c8e7beb4b9eac034cb88f9cd170ac1e99ad`.
- All-orbit free run:
  `reports/softened-symmetric-orbitals-free-001/report.json`, SHA256
  `fcf749552f40efedca518e74cf59c720dc76bd3bea4ad9690f206147fb83fe19`.
- Active-set v2 identical-config rerun:
  `reports/softened-symmetric-orbitals-free-v2-001/report.json`, SHA256
  `a0fb3fd9aa62deef8de515586217c7dde6c79a036c963f78c7b1e5025d1a84aa`.

The native exact engine took 1.18 seconds for each frozen control, 1.19 seconds
for the v1 free run, and 1.25 seconds for v2. Candidate promotion was not
attempted.
