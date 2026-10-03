# H-SP-01 result

The candidate-bound exact coefficient gate completed in 1.27 seconds after
reusing the nonlinear-polarization histogram/counter infrastructure. Signed
accumulation was used for both coefficients; no sign was assumed for `A4`.

Exact results on `b93`:

- `A3 = 55050997213332184301980640016289209 /
  5575186299632655785383929568162090376495104`
  (`9.874288365387797e-9`), identical to the unsigned control;
- `A4 = 221200110045737849778693283319473137028507 /
  6576757367989063131916581747223273588451696443392`
  (`3.363361268615158e-8`), smaller than the unsigned control's
  `3.779871217348187e-8` but still positive;
- both endpoints increase the objective;
- the feasible stationary point `epsilon=-0.2201879513552852` gives
  `Delta=-2.635278185720771e-11`.

This improves the unsigned scalar line by about `7.787e-12`, supporting the
specific cancellation hypothesis weakly. Its predicted density is nevertheless
`0.030138903979984803`, still `4.145857e-10` above the independently checked
incumbent. Per the preregistered decision rule, the branch stops without child
materialization or repeated levels.

Evidence:

- report `reports/signed-polarization-b93-001/report.json`, SHA-256
  `8f4598be94feb27926aefa837b340b58651f446bedf99e1574f501640eecf4f0`;
- frozen coefficient source SHA-256
  `e1d26a5c27a2597d8cffbd63af4f96241d957b9ac951b66a60c1112a4b33b096`;
- parent and candidate-bound certificate hashes match the archived `b93`
  evidence.

All three literal tiny fixtures passed, including repeated indices. Under color
complementation both signed coefficients remained invariant, as derived. This
is exact coefficient evidence only, not a recounted child graphon or a claim
about deeper polarization.
