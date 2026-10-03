import K4Ramsey.Final3840Count
import K4Ramsey.Final3840Validity

namespace K4Ramsey.Final3840.Count
open scoped BigOperators
set_option maxRecDepth 4096

@[simp] theorem b_eq (i j : Coarse) : b i j = (baseNumerator i j : Int) := by
  simp [b, bCache]

@[simp] theorem d_eq (i j : Coarse) (x y : Fiber) :
    d i j x y = centeredNumerator i j x y := by simp [d, dCache]

theorem d_zero (i j : Coarse) (h : support i j ≠ true) (x y : Fiber) :
    d i j x y = 0 := by
  have hb : baseNumerator i j = 0 ∨ baseNumerator i j = denominator := by
    by_cases h0 : baseNumerator i j = 0
    · exact Or.inl h0
    · exact Or.inr (by simpa [support, h0] using h)
  simpa using hard_blocks i j hb x y

theorem paths_eq (i j k : Coarse) (x y : Fiber) :
    paths i j k x y = ∑ z : Fiber, d i k x z * d j k y z := by
  have hc : lookup (lookup (lookup pathsCache i) j) k =
      if support i k && support j k then
        some (tabulate (fun x => tabulate (fun y => ∑ z : Fiber, d i k x z * d j k y z)))
      else none := by simp only [pathsCache, lookup_tabulate]
  unfold paths
  rw [hc]
  by_cases h : (support i k && support j k) = true
  · rw [if_pos h]
    simp only [lookup_tabulate]
  · rw [if_neg h]
    have hz : support i k ≠ true ∨ support j k ≠ true := by
      simpa only [Bool.and_eq_true, not_and_or] using h
    rcases hz with hi | hj
    · simp only [d_zero i k hi, zero_mul, Finset.sum_const_zero]
    · simp only [d_zero j k hj, mul_zero, Finset.sum_const_zero]

theorem cycle_eq (i j k l : Coarse) :
    cycle i j k l = IntegerTensorK4.sum
      (fun _ _ => 1) (d i k) (d i l) (d j k) (d j l) (fun _ _ => 1) := by
  rw [IntegerTensorK4.diamond_contraction]
  simp only [cycle, paths_eq, IntegerTensorK4.path, one_mul]

theorem diamond_eq (i j k l : Coarse) :
    diamond i j k l = IntegerTensorK4.sum
      (d i j) (d i k) (d i l) (d j k) (d j l) (fun _ _ => 1) := by
  rw [IntegerTensorK4.diamond_contraction]
  simp only [diamond, paths_eq, IntegerTensorK4.path, one_mul]

theorem triangle_eq (i j k : Coarse) :
    triangle i j k = ∑ x : Fiber, ∑ y : Fiber, ∑ z : Fiber,
      d i j x y * d i k x z * d j k y z := by
  simp only [triangle, paths_eq, Finset.mul_sum, mul_assoc]

theorem paths_zero (i j k : Coarse) (h : (support i k && support j k) ≠ true)
    (x y : Fiber) : paths i j k x y = 0 := by
  rw [paths_eq]
  have hz : support i k ≠ true ∨ support j k ≠ true := by
    simpa only [ne_eq, Bool.and_eq_true, not_and_or] using h
  rcases hz with hi | hj
  · simp only [d_zero i k hi, zero_mul, Finset.sum_const_zero]
  · simp only [d_zero j k hj, mul_zero, Finset.sum_const_zero]

theorem triangleAt_eq (i : Coarse) : triangleAt i =
    20 * ∑ j : Coarse, ∑ k : Coarse, triangleCoefficient i j k * triangle i j k := by
  unfold triangleAt
  congr 1
  apply Finset.sum_congr rfl; intro j _
  by_cases hj : support i j = true
  · rw [if_pos hj]
    apply Finset.sum_congr rfl; intro k _
    by_cases hk : (support i k && support j k) = true
    · rw [if_pos hk]
    · simp only [if_neg hk, triangle, paths_zero i j k hk, mul_zero, Finset.sum_const_zero]
  · simp only [if_neg hj, triangle, d_zero i j hj, zero_mul, Finset.sum_const_zero, mul_zero]

theorem cycleAt_eq (i : Coarse) : cycleAt i =
    ∑ j : Coarse, ∑ k : Coarse, ∑ l : Coarse,
      (b i j * b k l + (65536 - b i j) * (65536 - b k l)) * cycle i j k l := by
  unfold cycleAt
  apply Finset.sum_congr rfl; intro j _
  apply Finset.sum_congr rfl; intro k _
  by_cases hk : (support i k && support j k) = true
  · rw [if_pos hk]
    apply Finset.sum_congr rfl; intro l _
    by_cases hl : (support i l && support j l) = true
    · rw [if_pos hl]
    · simp only [if_neg hl, cycle, paths_zero i j l hl, mul_zero, Finset.sum_const_zero]
  · simp only [if_neg hk, cycle, paths_zero i j k hk, zero_mul, Finset.sum_const_zero, mul_zero]

theorem diamondAt_eq (i : Coarse) : diamondAt i =
    ∑ j : Coarse, ∑ k : Coarse, ∑ l : Coarse,
      (2 * b k l - 65536) * diamond i j k l := by
  unfold diamondAt
  apply Finset.sum_congr rfl; intro j _
  by_cases hj : support i j = true
  · rw [if_pos hj]
    apply Finset.sum_congr rfl; intro k _
    by_cases hk : (support i k && support j k) = true
    · rw [if_pos hk]
      apply Finset.sum_congr rfl; intro l _
      by_cases hl : (support i l && support j l) = true
      · rw [if_pos hl]
      · simp only [if_neg hl, diamond, paths_zero i j l hl, mul_zero, Finset.sum_const_zero]
    · simp only [if_neg hk, diamond, paths_zero i j k hk, mul_zero, zero_mul,
        Finset.sum_const_zero]
  · simp only [if_neg hj, diamond, d_zero i j hj, zero_mul, Finset.sum_const_zero, mul_zero]

theorem tetrahedronAt_eq (i : Coarse) : tetrahedronAt i =
    2 * ∑ j : Coarse, ∑ k : Coarse, ∑ l : Coarse, tetrahedron i j k l := by
  unfold tetrahedronAt
  congr 1
  apply Finset.sum_congr rfl; intro j _
  by_cases hj : support i j = true
  · rw [if_pos hj]
    apply Finset.sum_congr rfl; intro k _
    by_cases hk : (support i k && support j k) = true
    · rw [if_pos hk]
      apply Finset.sum_congr rfl; intro l _
      by_cases hl : (support i l && support j l && support k l) = true
      · rw [if_pos hl]
      · rw [if_neg hl]
        have hz : (support i l ≠ true ∨ support j l ≠ true) ∨ support k l ≠ true := by
          simpa only [Bool.and_eq_true, not_and_or] using hl
        rcases hz with (hi | hj) | hk <;>
          simp only [tetrahedron, d_zero _ _ (by assumption), mul_zero, zero_mul, Finset.sum_const_zero]
    · rw [if_neg hk]
      have hz : support i k ≠ true ∨ support j k ≠ true := by
        simpa only [Bool.and_eq_true, not_and_or] using hk
      rcases hz with hi | hj <;>
        simp only [tetrahedron, d_zero _ _ (by assumption), mul_zero, zero_mul, Finset.sum_const_zero]
  · simp only [if_neg hj, tetrahedron, d_zero i j hj, zero_mul, Finset.sum_const_zero]

end K4Ramsey.Final3840.Count
