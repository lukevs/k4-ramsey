import K4Ramsey.Counting.Multiplicity

namespace K4Ramsey.Tests

/-- Construct packed rows independently from a Boolean adjacency function. -/
def fromAdj (n : Nat) (edge : Nat → Nat → Bool) : Template := Id.run do
  let mut rows := #[]
  for i in [0:n] do
    let mut row := Array.replicate (wordCount n) (0 : UInt64)
    for j in [0:n] do
      if edge i j then
        row := row.set! (j / 64) (row[j / 64]! ||| ((1 : UInt64) <<< UInt64.ofNat (j % 64)))
    rows := rows.push row
  return ⟨n, rows⟩

/-- Independent definition: directly enumerate all ordered block quadruples,
including repeated indices. No clique decomposition or population counts. -/
def tupleOracle (n : Nat) (edge : Nat → Nat → Bool) : Nat := Id.run do
  let mut total := 0
  for a in [0:n] do
    for b in [0:n] do
      for c in [0:n] do
        for d in [0:n] do
          let color := edge a b
          if edge a c == color && edge a d == color && edge b c == color &&
              edge b d == color && edge c d == color then
            total := total + 1
  return total

def graphEdge (mask i j : Nat) : Bool :=
  i != j && mask.testBit (max i j * (max i j - 1) / 2 + min i j)

/-- Exhaust all 1,024 simple graphs on five vertices. -/
theorem all_five_vertex_graphs :
    ((List.range 1024).all fun mask =>
      let edge := graphEdge mask
      let g := fromAdj 5 edge
      g.isValid && g.monoK4Numerator == tupleOracle 5 edge) = true := by
  native_decide

/-- Complete graphs straddling 64-bit boundaries, including partial last words.
The blue-diagonal template contributes `n` in addition to distinct red tuples. -/
theorem word_boundaries :
    ([1, 2, 4, 63, 64, 65, 127, 128, 129].all fun n =>
      let g := fromAdj n (fun i j => i != j)
      g.isValid && g.monoK4Numerator == n + n * (n-1) * (n-2) * (n-3)) = true := by
  native_decide

/-- All-blue templates include every repeated-index pattern. -/
theorem blue_templates :
    ([1, 2, 4, 63, 64, 65, 129].all fun n =>
      let g := fromAdj n (fun _ _ => false)
      g.isValid && g.monoK4Numerator == n ^ 4) = true := by
  native_decide

theorem malformed_rejected :
    (Template.isValid ⟨1, #[#[(1 : UInt64)]]⟩ = false) ∧
    (Template.isValid ⟨1, #[#[(2 : UInt64)]]⟩ = false) ∧
    (Template.isValid ⟨2, #[#[(2 : UInt64)], #[(0 : UInt64)]]⟩ = false) ∧
    (Template.isValid ⟨1, #[]⟩ = false) ∧
    (Template.isValid ⟨1, #[#[]]⟩ = false) := by
  native_decide

end K4Ramsey.Tests
