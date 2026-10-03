import K4Ramsey.IO.TemplateInput

open K4Ramsey

/-- Read plain adjacency rows. The Python wrapper separately checks the JSON
schema and weights; this program independently checks the matrix and counts.
This is native execution, not a kernel-only counting-correctness theorem. -/
def main (args : List String) : IO Unit := do
  let some path := args[0]? | throw (IO.userError "usage: check_candidate rows.txt [expected_numerator]")
  let raw ← IO.FS.readFile (System.FilePath.mk path)
  let cert ← match TemplateInput.parseRows (TemplateInput.splitRows raw) with
    | .ok cert => pure cert
    | .error message => throw (IO.userError message)
  let n := cert.raw.order
  let counts := cert.countSubgraphs
  let numerator := counts.numerator n
  if let some expected := args[1]? then
    unless expected.toNat? = some numerator do throw (IO.userError "numerator mismatch")
  IO.println s!"{n} {numerator} {n^4} {counts.redEdges} {counts.blueTriangles} {counts.redK4} {counts.blueK4}"
