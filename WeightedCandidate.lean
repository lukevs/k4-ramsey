import K4Ramsey.WeightedMultiplicity

open K4Ramsey

/-- Versioned weighted checker: first line weights, then plain adjacency rows.
Original CheckCandidate and its unit-weight contract remain unchanged. -/
def main (args : List String) : IO Unit := do
  let some path := args[0]? | throw (IO.userError "usage: check_weighted_candidate input.txt")
  let raw ← IO.FS.readFile (System.FilePath.mk path)
  let lines := (raw.splitOn "\n").filter (· != "")
  let some weightLine := lines.head? | throw (IO.userError "missing weights")
  let mut weights : Array Nat := #[]
  for token in weightLine.splitOn " " do
    let some w := token.toNat? | throw (IO.userError "invalid integer weight")
    weights := weights.push w
  let matrix := lines.drop 1
  let n := matrix.length
  unless n > 0 && n ≤ 1024 && WeightedV1.validWeights n weights do
    throw (IO.userError "invalid order or positive integer weights")
  let mut rows : Array BitRow := #[]
  for line in matrix do
    unless line.length = n do throw (IO.userError "invalid row width")
    let mut row := Array.replicate (wordCount n) (0 : UInt64)
    let mut j := 0
    for c in line.toList do
      unless c = '0' || c = '1' do throw (IO.userError "non-binary row")
      if c = '1' then
        row := row.set! (j / 64) (row[j / 64]! ||| ((1 : UInt64) <<< UInt64.ofNat (j % 64)))
      j := j + 1
    rows := rows.push row
  let g : Template := ⟨n, rows⟩
  unless g.isValid do throw (IO.userError "invalid symmetric blue-diagonal graph")
  let value := WeightedV1.numerator g weights
  let denominator := WeightedV1.denominator weights
  IO.println s!"{n} {weights.foldl (· + ·) 0} {value} {denominator}"
