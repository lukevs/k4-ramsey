import Std

namespace K4Ramsey

abbrev BitRow := Array UInt64

/-- A finite, unweighted two-color template, packed into 64-bit words. A set
bit means red; the (unset) diagonal is treated as blue. -/
structure Template where
  order : Nat
  redRows : Array BitRow

def wordCount (n : Nat) : Nat := (n + 63) / 64

/-- Population count of one machine word, using the standard SWAR identity. -/
def popcount64 (input : UInt64) : Nat :=
  let x := input - ((input >>> 1) &&& (0x5555555555555555 : UInt64))
  let x := (x &&& (0x3333333333333333 : UInt64)) +
    ((x >>> 2) &&& (0x3333333333333333 : UInt64))
  let x := (x + (x >>> 4)) &&& (0x0f0f0f0f0f0f0f0f : UInt64)
  ((x * (0x0101010101010101 : UInt64)) >>> 56).toNat

/-- Index of the least significant bit in a nonzero machine word. -/
def trailingZeros64 (input : UInt64) : Nat := Id.run do
  let mut x := input
  let mut count := 0
  if x &&& (0xffffffff : UInt64) = 0 then count := count + 32; x := x >>> 32
  if x &&& (0xffff : UInt64) = 0 then count := count + 16; x := x >>> 16
  if x &&& (0xff : UInt64) = 0 then count := count + 8; x := x >>> 8
  if x &&& (0xf : UInt64) = 0 then count := count + 4; x := x >>> 4
  if x &&& (0x3 : UInt64) = 0 then count := count + 2; x := x >>> 2
  if x &&& (0x1 : UInt64) = 0 then count := count + 1
  return count

def rowPopcount (row : BitRow) : Nat :=
  row.foldl (fun total word => total + popcount64 word) 0

def hasEdge (adj : Array BitRow) (i j : Nat) : Bool :=
  (adj[i]![j / 64]! &&& ((1 : UInt64) <<< UInt64.ofNat (j % 64))) != 0

def validWordMask (n word : Nat) : UInt64 :=
  let bits := n - 64 * word
  if 64 <= bits then (0xffffffffffffffff : UInt64)
  else if bits = 0 then 0
  else ((1 : UInt64) <<< UInt64.ofNat bits) - 1

/-- Check representation invariants in Lean, independently of the generator. -/
def Template.isValid (g : Template) : Bool := Id.run do
  if g.order = 0 || g.redRows.size != g.order then return false
  for i in [0:g.order] do
    let row := g.redRows[i]!
    if row.size != wordCount g.order then return false
    for w in [0:row.size] do
      if row[w]! &&& ~~~validWordMask g.order w != 0 then return false
    if hasEdge g.redRows i i then return false
    for j in [0:i] do
      if hasEdge g.redRows i j != hasEdge g.redRows j i then return false
  return true

/-- The blue adjacency rows derived from red rows by complementing valid bits
and clearing the diagonal. -/
def Template.blueRows (g : Template) : Array BitRow := Id.run do
  let mut result := #[]
  for i in [0:g.order] do
    let mut row := #[]
    for w in [0:wordCount g.order] do
      let diagonal := if w = i / 64 then (1 : UInt64) <<< UInt64.ofNat (i % 64) else 0
      row := row.push ((~~~g.redRows[i]![w]!) &&& validWordMask g.order w &&& ~~~diagonal)
    result := result.push row
  return result

/-- Number of unordered edges induced by `vertices`. Each edge is charged to
its lower endpoint, so it is counted exactly once. -/
def inducedEdges (adj : Array BitRow) (vertices : BitRow) : Nat := Id.run do
  let mut total := 0
  for wi in [0:vertices.size] do
    let mut remaining := vertices[wi]!
    while remaining != 0 do
      let k := 64 * wi + trailingZeros64 remaining
      remaining := remaining &&& (remaining - 1)
      total := total + popcount64 (remaining &&& adj[k]![wi]!)
      for wj in [wi + 1:vertices.size] do
        total := total + popcount64 (vertices[wj]! &&& adj[k]![wj]!)
  return total

/-- Common neighbors of `i,j` whose index is greater than `j`. -/
def commonAbove (adj : Array BitRow) (i j words : Nat) : BitRow := Id.run do
  let mut result := #[]
  for w in [0:words] do
    let above :=
      if w < j / 64 then 0
      else if w = j / 64 then
        -- UInt64 shifts reduce their count modulo 64: handle 64 explicitly.
        if j % 64 = 63 then 0
        else (0xffffffffffffffff : UInt64) <<< UInt64.ofNat ((j % 64) + 1)
      else (0xffffffffffffffff : UInt64)
    result := result.push (adj[i]![w]! &&& adj[j]![w]! &&& above)
  return result

/-- Count unordered triangles. -/
def triangleCount (n : Nat) (adj : Array BitRow) : Nat := Id.run do
  let mut total := 0
  let words := wordCount n
  for i in [0:n] do
    for j in [i + 1:n] do
      if hasEdge adj i j then
        total := total + rowPopcount (commonAbove adj i j words)
  return total

/-- Count unordered four-cliques. -/
def fourCliqueCount (n : Nat) (adj : Array BitRow) : Nat := Id.run do
  let mut total := 0
  let words := wordCount n
  for i in [0:n] do
    for j in [i + 1:n] do
      if hasEdge adj i j then
        let common := commonAbove adj i j words
        total := total + inducedEdges adj common
  return total

/-- Number of red edges. -/
def Template.redEdgeCount (g : Template) : Nat :=
  g.redRows.foldl (fun total row => total + rowPopcount row) 0 / 2

/-- Computational counting formula for the balanced blow-up, with blue diagonal
blocks. Equality patterns 4, 3+1/2+2, 2+1+1, and 1+1+1+1 contribute respectively
`n`, `14 * blueEdges`, `36 * blueTriangles`, and `24 * monoFourCliques`.
The general equivalence to a literal tuple sum is not yet formally proved. -/
def Template.monoK4Numerator (g : Template) : Nat :=
  let blue := g.blueRows
  let totalEdges := g.order * (g.order - 1) / 2
  let blueEdges := totalEdges - g.redEdgeCount
  g.order + 14 * blueEdges + 36 * triangleCount g.order blue +
    24 * (fourCliqueCount g.order g.redRows + fourCliqueCount g.order blue)

/-- Cross-multiplied comparison of exact densities, avoiding floating point. -/
def densityLE (numerator₁ denominator₁ numerator₂ denominator₂ : Nat) : Bool :=
  numerator₁ * denominator₂ <= numerator₂ * denominator₁

def mckayNumerator : Nat := 10486266368
def denominator768 : Nat := 768 ^ 4

/-- McKay's value is below 0.0302 (3.02%). -/
theorem mckay_bound_below_three_point_zero_two_percent :
    densityLE mckayNumerator denominator768 302 10000 = true := by
  native_decide

end K4Ramsey
