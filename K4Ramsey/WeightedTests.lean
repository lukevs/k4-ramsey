import K4Ramsey.WeightedMultiplicity
import K4Ramsey.Tests

namespace K4Ramsey.WeightedTests

def tupleOracle (weights : Array Nat) (edge : Nat → Nat → Bool) : Nat := Id.run do
  let mut total := 0
  for a in [0:weights.size] do
    for b in [0:weights.size] do
      for c in [0:weights.size] do
        for d in [0:weights.size] do
          let color := edge a b
          if edge a c == color && edge a d == color && edge b c == color &&
              edge b d == color && edge c d == color then
            total := total + weights[a]! * weights[b]! * weights[c]! * weights[d]!
  return total

theorem all_four_vertex_graphs_binary_weights :
    ((List.range 64).all fun mask => (List.range 16).all fun code =>
      let weights := (List.range 4).toArray.map (fun i => if code.testBit i then 2 else 1)
      let edge := Tests.graphEdge mask
      let g := Tests.fromAdj 4 edge
      WeightedV1.numerator g weights == tupleOracle weights edge) = true := by
  native_decide

theorem varied_weights :
    ((List.range 64).all fun mask =>
      let weights := #[1, 3, 7, 11]
      let edge := Tests.graphEdge mask
      let g := Tests.fromAdj 4 edge
      WeightedV1.numerator g weights == tupleOracle weights edge) = true := by
  native_decide

theorem weighted_blue_boundaries :
    ([1, 2, 4, 63, 64, 65, 127, 128, 129].all fun n =>
      let weights := (List.range n).toArray.map (fun i => 1 + i % 7)
      let g := Tests.fromAdj n (fun _ _ => false)
      WeightedV1.numerator g weights == WeightedV1.denominator weights) = true := by
  native_decide

theorem reject_invalid_weights :
    (WeightedV1.validWeights 2 #[1] = false) ∧
    (WeightedV1.validWeights 2 #[1, 0] = false) ∧
    (WeightedV1.validWeights 2 #[1, 65536] = false) ∧
    (WeightedV1.validWeights 2 #[1, 65535] = true) := by
  native_decide

end K4Ramsey.WeightedTests
