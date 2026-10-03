import K4Ramsey.Multiplicity

open K4Ramsey

/-- Read plain adjacency rows. The Python wrapper separately checks the JSON
schema and weights; this program independently checks the matrix and counts.
This is native execution, not a kernel-only counting-correctness theorem. -/
def main (args : List String) : IO Unit := do
  let some path := args[0]? | throw (IO.userError "usage: check_candidate rows.txt [expected_numerator]")
  let raw ← IO.FS.readFile (System.FilePath.mk path)
  let lines := (raw.splitOn "\n").filter (· != "")
  let n := lines.length
  unless n > 0 && n ≤ 1024 do throw (IO.userError "invalid order")
  let mut rows : Array BitRow := #[]
  for line in lines do
    unless line.length = n do throw (IO.userError "invalid row width")
    let mut row := Array.replicate (wordCount n) (0 : UInt64)
    let mut j := 0
    for c in line.toList do
      unless c = '0' || c = '1' do throw (IO.userError "non-binary row")
      if c = '1' then
        row := row.set! (j / 64) (row[j / 64]! ||| ((1 : UInt64) <<< (UInt64.ofNat (j % 64))))
      j := j + 1
    rows := rows.push row
  let cert : Template := ⟨n, rows⟩
  unless cert.isValid do throw (IO.userError "invalid symmetric blue-diagonal template")
  let edges := cert.redEdgeCount
  let blue := cert.blueRows
  let triangles := triangleCount n blue
  let redK4 := fourCliqueCount n rows
  let blueK4 := fourCliqueCount n blue
  let numerator := n + 14 * (n * (n-1) / 2 - edges) + 36 * triangles + 24 * (redK4 + blueK4)
  if let some expected := args[1]? then
    unless expected.toNat? = some numerator do throw (IO.userError "numerator mismatch")
  IO.println s!"{n} {numerator} {n^4} {edges} {triangles} {redK4} {blueK4}"
