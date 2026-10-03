# Fixed construction inputs

These immutable inputs are distinct from local experiment outputs.
`provenance.json` records original paths, byte lengths, and SHA-256 hashes.
Original paths are historical attribution, not build dependencies.

- `quotient.json`: the 192 fibers of the published 768-vertex graph.
- `base192.json`: the two-parameter table used by the visual explainer.
- `family-rule.json`, `vertex-map.json`: recovered family rule and coordinates.
- `final3840.json.gz`: the exact original final-witness JSON, losslessly compressed
  from 163 MB to 2.34 MB. This is mathematical construction data, not a model
  checkpoint. Decompression preserves the existing candidate SHA-256.

Run `just explainer` or `just generate-final3840` from the repository root.
Neither reads `reports/`. Witness regeneration checks the original hash,
dimensions, symmetry, and coarse block means before writing Lean data. These
checks do not certify its numerical K₄ density or close the remaining proof gap.

The explainer's diagonal parameter is 35015/65536; the final witness uses
35139/65536. They are different constructions, not interchangeable inputs.
