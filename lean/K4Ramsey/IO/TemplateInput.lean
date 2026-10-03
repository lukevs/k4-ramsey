import K4Ramsey.Counting.ValidatedTemplate

/-! Shared input parsing for the independent unit and weighted executables.
Parsing returns checked data rather than a raw array plus an implicit promise.
-/
namespace K4Ramsey.TemplateInput

/-- Parse a bounded square binary matrix, then independently check its graph invariants. -/
def parseRows (lines : List String) : Except String ValidTemplate := do
  let n := lines.length
  unless n > 0 && n ≤ 1024 do throw "invalid order"
  let mut rows : Array BitRow := #[]
  for line in lines do
    unless line.length = n do throw "invalid row width"
    let mut row := Array.replicate (wordCount n) (0 : UInt64)
    let mut j := 0
    for c in line.toList do
      unless c = '0' || c = '1' do throw "non-binary row"
      if c = '1' then
        row := row.set! (j / 64) (row[j / 64]! ||| ((1 : UInt64) <<< UInt64.ofNat (j % 64)))
      j := j + 1
    rows := rows.push row
  (⟨n, rows⟩ : Template).validate

/-- The weighted text protocol places positive integer weights on its first line. -/
def parseWeightedRows (lines : List String) : Except String ValidWeightedTemplate := do
  let some weightLine := lines.head? | throw "missing weights"
  let mut weights : Array Nat := #[]
  for token in weightLine.splitOn " " do
    let some weight := token.toNat? | throw "invalid integer weight"
    weights := weights.push weight
  let graph ← parseRows (lines.drop 1)
  graph.withWeights weights

/-- Preserve the existing line-oriented protocol, including ignored blank lines. -/
def splitRows (text : String) : List String :=
  (text.splitOn "\n").filter (· != "")

end K4Ramsey.TemplateInput
