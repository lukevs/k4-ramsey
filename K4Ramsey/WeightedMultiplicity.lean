import K4Ramsey.Multiplicity

namespace K4Ramsey.WeightedV1

abbrev WeightTables := Array (Array Nat)

/-- Byte-mask tables independently aggregate arbitrary positive block weights.
There is no pair-perturbation formula or assumed near-uniformity here. -/
def makeTables (weights : Array Nat) (power : Nat) : WeightTables := Id.run do
  let mut tables := #[]
  for byte in [0:8 * wordCount weights.size] do
    let mut table := #[]
    for mask in [0:256] do
      let mut total := 0
      for bit in [0:8] do
        let index := 8 * byte + bit
        if mask.testBit bit && index < weights.size then
          total := total + weights[index]! ^ power
      table := table.push total
    tables := tables.push table
  return tables

def weightedWord (tables : WeightTables) (word : Nat) (bits : UInt64) : Nat := Id.run do
  let mut total := 0
  for byte in [0:8] do
    let mask := ((bits >>> UInt64.ofNat (8 * byte)) &&& (255 : UInt64)).toNat
    total := total + tables[8 * word + byte]![mask]!
  return total

def weightedRow (tables : WeightTables) (row : BitRow) : Nat := Id.run do
  let mut total := 0
  for word in [0:row.size] do
    total := total + weightedWord tables word row[word]!
  return total

/-- Sum w_i*w_j over unordered induced edges, using only actual weights. -/
def inducedWeightedEdges (weights : Array Nat) (tables : WeightTables)
    (adj : Array BitRow) (vertices : BitRow) : Nat := Id.run do
  let mut total := 0
  for wi in [0:vertices.size] do
    let mut remaining := vertices[wi]!
    while remaining != 0 do
      let k := 64 * wi + trailingZeros64 remaining
      remaining := remaining &&& (remaining - 1)
      let mut neighbors := weightedWord tables wi (remaining &&& adj[k]![wi]!)
      for wj in [wi + 1:vertices.size] do
        neighbors := neighbors + weightedWord tables wj (vertices[wj]! &&& adj[k]![wj]!)
      total := total + weights[k]! * neighbors
  return total

def fourCliqueWeight (weights : Array Nat) (tables : WeightTables)
    (adj : Array BitRow) : Nat := Id.run do
  let mut total := 0
  let n := weights.size
  for i in [0:n] do
    for j in [i + 1:n] do
      if hasEdge adj i j then
        let common := commonAbove adj i j (wordCount n)
        total := total + weights[i]! * weights[j]! * inducedWeightedEdges weights tables adj common
  return total

def validWeights (n : Nat) (weights : Array Nat) : Bool :=
  weights.size == n && weights.all (fun w => 0 < w && w <= 65535)

/-- General positive-integer weights, blue diagonals. Partition types are
4; 3+1 and 2+2; 2+1+1; and four distinct indices. No identity with the literal
tuple oracle is yet proved for arbitrary inputs: native tests check fixtures. -/
def numerator (g : Template) (weights : Array Nat) : Nat := Id.run do
  let tables := makeTables weights 1
  let squared := makeTables weights 2
  let blue := g.blueRows
  let mut total := weights.foldl (fun sum w => sum + w^4) 0
  for i in [0:g.order] do
    for j in [i + 1:g.order] do
      if hasEdge blue i j then
        let wi := weights[i]!
        let wj := weights[j]!
        total := total + 4 * (wi^3 * wj + wi * wj^3) + 6 * wi^2 * wj^2
        let common := commonAbove blue i j (wordCount g.order)
        total := total + 12 * wi * wj *
          ((wi + wj) * weightedRow tables common + weightedRow squared common)
  return total + 24 * (fourCliqueWeight weights tables g.redRows + fourCliqueWeight weights tables blue)

def denominator (weights : Array Nat) : Nat :=
  (weights.foldl (· + ·) 0)^4

end K4Ramsey.WeightedV1
