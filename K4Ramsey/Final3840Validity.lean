import K4Ramsey.Final3840Model
import K4Ramsey.Realization
import Mathlib.Tactic.NormNum

namespace K4Ramsey.Final3840

theorem data_shape : Final3840Data.blockIndex.size = 192 * 192 ∧
    Final3840Data.blocks.size = 1248 ∧
    (∀ b ∈ Final3840Data.blocks, b.size = 400) := by native_decide

theorem numerator_symmetry : ∀ u v : Coarse, ∀ x y : Fiber,
    numerator u v x y = numerator v u y x := by native_decide

theorem numerator_bounds : ∀ u v : Coarse, ∀ x y : Fiber,
    numerator u v x y ≤ denominator := by native_decide

theorem base_symmetry : ∀ u v : Coarse,
    baseNumerator u v = baseNumerator v u := by native_decide

theorem centered_rows : ∀ u v : Coarse, ∀ x : Fiber,
    (∑ y : Fiber, centeredNumerator u v x y) = 0 := by native_decide

theorem hard_blocks : ∀ u v : Coarse,
    baseNumerator u v = 0 ∨ baseNumerator u v = denominator →
    ∀ x y : Fiber, centeredNumerator u v x y = 0 := by native_decide

theorem table_symmetric (u v : Vertex) : table u v = table v u := by
  simp only [table, numerator_symmetry u.1 v.1 u.2 v.2]

theorem table_nonnegative (u v : Vertex) : 0 ≤ table u v := by
  exact div_nonneg (Nat.cast_nonneg _) (Nat.cast_nonneg _)

theorem table_le_one (u v : Vertex) : table u v ≤ 1 := by
  apply (div_le_one₀ (by norm_num [denominator] : (0 : ℚ) < denominator)).2
  exact_mod_cast numerator_bounds u.1 v.1 u.2 v.2

theorem perturbation_symmetric (u v : Coarse) (x y : Fiber) :
    perturbation u v x y = perturbation v u y x := by
  simp only [perturbation, centeredNumerator, numerator_symmetry u v x y,
    base_symmetry u v]

theorem perturbation_rows (u v : Coarse) (x : Fiber) :
    (∑ y : Fiber, perturbation u v x y) = 0 := by
  simp only [perturbation, div_eq_mul_inv, ← Finset.sum_mul, ← Int.cast_sum,
    centered_rows, Int.cast_zero, zero_mul]

theorem perturbation_columns (u v : Coarse) (y : Fiber) :
    (∑ x : Fiber, perturbation u v x y) = 0 := by
  simp only [perturbation_symmetric u v]
  exact perturbation_rows v u y

/-- A genuine 3840-part template is now embedded in Lean. This statement
deliberately leaves its density symbolic until the recount is certified. -/
theorem finite_realization {V : Type*} [Fintype V] [Nonempty (Fin 4 ↪ V)] :
    ∃ g : Sym2 V → Bool, Realization.coloringDensity g ≤ Graphon.density table :=
  Realization.exists_coloring_le table table_symmetric table_nonnegative table_le_one

end K4Ramsey.Final3840
