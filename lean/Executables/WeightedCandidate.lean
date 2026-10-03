import K4Ramsey.IO.TemplateInput

open K4Ramsey

/-- Versioned weighted checker: first line weights, then plain adjacency rows.
Original CheckCandidate and its unit-weight contract remain unchanged. -/
def main (args : List String) : IO Unit := do
  let some path := args[0]? | throw (IO.userError "usage: check_weighted_candidate input.txt")
  let raw ← IO.FS.readFile (System.FilePath.mk path)
  let cert ← match TemplateInput.parseWeightedRows (TemplateInput.splitRows raw) with
    | .ok cert => pure cert
    | .error message => throw (IO.userError message)
  let value := cert.numerator
  let denominator := WeightedV1.denominator cert.weights
  IO.println s!"{cert.graph.raw.order} {cert.weights.foldl (· + ·) 0} {value} {denominator}"
