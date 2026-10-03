import K4Ramsey.Final3840CountCorrect
import K4Ramsey.IntegerRefinement

namespace K4Ramsey.Final3840.Count
open scoped BigOperators
open IntegerTensorK4

def w : Kernel Vertex := liftBase b
def e : Kernel Vertex := fun u v => d u.1 v.1 u.2 v.2
def bw : Kernel Coarse := fun i j => 65536 - b i j
def be : Kernel Vertex := fun u v => -e u v

theorem b_sym (i j : Coarse) : b i j = b j i := by
  simp only [b_eq, base_symmetry i j]
theorem e_sym (u v : Vertex) : e u v = e v u := by
  simp only [e, d_eq, centeredNumerator, numerator_symmetry u.1 v.1 u.2 v.2,
    base_symmetry u.1 v.1]
theorem e_columns (i j : Coarse) (y : Fiber) : (∑ x : Fiber, e (i,x) (j,y)) = 0 := by
  calc
    _ = ∑ x : Fiber, e (j,y) (i,x) := Finset.sum_congr rfl (fun x _ => e_sym _ _)
    _ = 0 := by simp only [e, d_eq]; exact centered_rows j i y

theorem raw_red_expansion : colorSum (fun u v => w u v + e u v) =
    colorSum w + 4 * sum e e w e w w + 3 * sum w e e e e w +
    6 * sum e e e e e w + sum e e e e e e := by
  exact centered_expansion b e
    (symmetric_transpose (fun u v => b_sym u.1 v.1))
    (symmetric_transpose e_sym) e_columns

theorem raw_blue_expansion : colorSum (fun u v => liftBase bw u v + be u v) =
    colorSum (liftBase (L := Fiber) bw) + 4 * sum be be (liftBase bw) be (liftBase bw) (liftBase bw) +
    3 * sum (liftBase bw) be be be be (liftBase bw) +
    6 * sum be be be be be (liftBase bw) + sum be be be be be be := by
  apply centered_expansion bw be
  · apply symmetric_transpose
    intro u v
    simp only [liftBase, bw, b_sym u.1 v.1]
  · apply symmetric_transpose
    intro u v
    simp only [be, e_sym u v]
  · intro i j y
    simp only [be, Finset.sum_neg_distrib, e_columns, neg_zero]

theorem red_triangle : sum e e w e w w =
    20 * ∑ i : Coarse, ∑ j : Coarse, ∑ k : Coarse, ∑ l : Coarse,
      b i l * b j l * b k l * triangle i j k := by
  rw [sum_split]
  simp only [e, w, liftBase, triangle_contraction, Fintype.card_fin,
    ← triangle_eq, Finset.mul_sum]
  apply Finset.sum_congr rfl; intro i _
  apply Finset.sum_congr rfl; intro j _
  apply Finset.sum_congr rfl; intro k _
  apply Finset.sum_congr rfl; intro l _
  ring

theorem red_cycle : sum w e e e e w =
    ∑ i : Coarse, ∑ j : Coarse, ∑ k : Coarse, ∑ l : Coarse,
      b i j * b k l * cycle i j k l := by
  rw [sum_split]
  simp only [w, e, liftBase, cycle_contraction, cycle, paths_eq, path]

theorem red_diamond : sum e e e e e w =
    ∑ i : Coarse, ∑ j : Coarse, ∑ k : Coarse, ∑ l : Coarse,
      b k l * diamond i j k l := by
  rw [sum_split]
  simp only [w, e, liftBase, diamond_contraction, diamond, paths_eq, path]

theorem red_tetrahedron : sum e e e e e e =
    ∑ i : Coarse, ∑ j : Coarse, ∑ k : Coarse, ∑ l : Coarse,
      tetrahedron i j k l := by
  rw [sum_split]
  rfl

theorem blue_triangle : sum be be (liftBase bw) be (liftBase bw) (liftBase bw) =
    -(20 * ∑ i : Coarse, ∑ j : Coarse, ∑ k : Coarse, ∑ l : Coarse,
      bw i l * bw j l * bw k l * triangle i j k) := by
  rw [sum_split]
  simp only [be, e, liftBase, triangle_contraction, Fintype.card_fin,
    neg_mul, mul_neg, neg_neg, Finset.sum_neg_distrib, ← triangle_eq]
  simp only [Finset.mul_sum, ← Finset.sum_neg_distrib]
  apply Finset.sum_congr rfl; intro i _
  apply Finset.sum_congr rfl; intro j _
  apply Finset.sum_congr rfl; intro k _
  apply Finset.sum_congr rfl; intro l _
  ring

theorem blue_cycle : sum (liftBase bw) be be be be (liftBase bw) =
    ∑ i : Coarse, ∑ j : Coarse, ∑ k : Coarse, ∑ l : Coarse,
      bw i j * bw k l * cycle i j k l := by
  rw [sum_split]
  simp only [be, e, liftBase, cycle_contraction, cycle, paths_eq, path, neg_mul_neg]

theorem blue_diamond : sum be be be be be (liftBase bw) =
    -(∑ i : Coarse, ∑ j : Coarse, ∑ k : Coarse, ∑ l : Coarse,
      bw k l * diamond i j k l) := by
  rw [sum_split]
  simp only [be, e, liftBase, diamond_contraction, diamond, paths_eq, path,
    neg_mul_neg, neg_mul, Finset.sum_neg_distrib, mul_neg, neg_neg]

theorem blue_tetrahedron : sum be be be be be be = sum e e e e e e := by
  simp only [sum, be, neg_mul_neg, mul_neg, neg_mul, neg_neg]

theorem raw_total :
    colorSum (fun u v => w u v + e u v) +
      colorSum (fun u v => liftBase bw u v + be u v) =
    160000 * (∑ i : Coarse, baseRoot i) +
      4 * (∑ i : Coarse, triangleAt i) + 3 * (∑ i : Coarse, cycleAt i) +
      6 * (∑ i : Coarse, diamondAt i) + (∑ i : Coarse, tetrahedronAt i) := by
  rw [raw_red_expansion, raw_blue_expansion, red_triangle, red_cycle, red_diamond,
    blue_triangle, blue_cycle, blue_diamond, blue_tetrahedron, red_tetrahedron]
  change colorSum (liftBase (L := Fiber) b) + _ + _ + _ + _ + _ = _
  rw [base_lift_sum, base_lift_sum]
  simp only [Fintype.card_fin]
  norm_num only [Nat.cast_ofNat, Int.reducePow]
  simp only [triangleAt_eq, cycleAt_eq, diamondAt_eq, tetrahedronAt_eq,
    triangleCoefficient, baseRoot, colorSum, sum, bw, Finset.mul_sum, Finset.sum_mul,
    ← Finset.sum_neg_distrib, ← Finset.sum_add_distrib, ← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl; intro i _
  apply Finset.sum_congr rfl; intro j _
  apply Finset.sum_congr rfl; intro k _
  apply Finset.sum_congr rfl; intro l _
  ring

theorem density_eq_count : Graphon.density table =
    ((160000 * (∑ i : Coarse, baseRoot i) +
      4 * (∑ i : Coarse, triangleAt i) + 3 * (∑ i : Coarse, cycleAt i) +
      6 * (∑ i : Coarse, diamondAt i) + (∑ i : Coarse, tetrahedronAt i) : Int) : ℚ) /
      (65536^6 * 3840^4) := by
  have hr : table = fun u v => ((w u v + e u v : Int) : ℚ) / 65536 := by
    funext u v
    simp only [table, w, liftBase, e, b_eq, d_eq, centeredNumerator, Int.cast_add,
      Int.cast_sub, Int.cast_natCast, denominator]
    ring
  have hb : (fun u v => 1 - table u v) =
      fun u v => ((liftBase bw u v + be u v : Int) : ℚ) / 65536 := by
    funext u v
    simp only [table, liftBase, bw, be, e, b_eq, d_eq, centeredNumerator,
      Int.cast_add, Int.cast_sub, Int.cast_natCast, Int.cast_neg, Int.cast_ofNat, denominator]
    ring
  unfold Graphon.density
  rw [hb, hr, scaled_colorSum, scaled_colorSum, ← add_div, ← Int.cast_add, raw_total]
  norm_num [Vertex, Coarse, Fiber, div_div]

end K4Ramsey.Final3840.Count
