import K4Ramsey.Constructions.Clebsch192.Model
import Mathlib.Tactic.NormNum

namespace K4Ramsey.Clebsch192

theorem vertex_count : Fintype.card Vertex = 192 := by
  norm_num [Vertex, Position]

theorem table_symmetric : ∀ i j, table i j = table j i := by native_decide

theorem table_nonnegative : ∀ i j, 0 ≤ table i j := by native_decide

theorem table_le_one : ∀ i j, table i j ≤ 1 := by native_decide

/-- Literal rooted six-edge sum, evaluated by Lean, not an imported receipt. -/
theorem exact_rooted_sum :
    rootedSum kernel + rootedSum (fun v => 1 - kernel v) =
      (1013294255057839 : ℚ) / 4750104241 := by
  native_decide

theorem exact_density : Graphon.density table =
    (1013294255057839 : ℚ) / 33620705806123008 := by
  have hblue : (fun i j => 1 - table i j) = Graphon.cayley (fun v => 1 - kernel v) := rfl
  unfold Graphon.density
  rw [hblue]
  unfold table
  rw [Graphon.cayley_colorSum, Graphon.cayley_colorSum, vertex_count]
  change (192 * rootedSum kernel + 192 * rootedSum (fun v => 1 - kernel v)) /
    (192 : ℚ)^4 = _
  rw [← mul_add, exact_rooted_sum]
  norm_num

theorem below_decimal_threshold : Graphon.density table < (30139 : ℚ) / 1000000 := by
  rw [exact_density]
  norm_num

end K4Ramsey.Clebsch192
