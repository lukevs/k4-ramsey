import K4Ramsey.Counting.IntegerCenteredExpansion

namespace K4Ramsey.IntegerTensorK4
open scoped BigOperators

theorem sum_split {B L : Type*} [Fintype B] [Fintype L]
    (a b c d e f : Kernel (B × L)) : sum a b c d e f =
      ∑ i, ∑ j, ∑ k, ∑ l, sum
        (fun x y => a (i,x) (j,y)) (fun x z => b (i,x) (k,z))
        (fun x t => c (i,x) (l,t)) (fun y z => d (j,y) (k,z))
        (fun y t => e (j,y) (l,t)) (fun z t => f (k,z) (l,t)) := by
  exact split_prod4 _

theorem base_lift_sum {B L : Type*} [Fintype B] [Fintype L] (w : Kernel B) :
    colorSum (liftBase (L := L) w) = (Fintype.card L : Int)^4 * colorSum w := by
  unfold colorSum sum
  rw [split_prod4]
  simp only [liftBase, Finset.sum_const, Finset.card_univ, nsmul_eq_mul,
    Finset.mul_sum]
  apply Finset.sum_congr rfl; intro i _
  apply Finset.sum_congr rfl; intro j _
  apply Finset.sum_congr rfl; intro k _
  apply Finset.sum_congr rfl; intro l _
  ring

theorem triangle_contraction {L : Type*} [Fintype L]
    (a b d : Kernel L) (c e f : Int) :
    sum a b (fun _ _ => c) d (fun _ _ => e) (fun _ _ => f) =
      (Fintype.card L : Int) * c * e * f *
        (∑ x, ∑ y, ∑ z, a x y * b x z * d y z) := by
  simp only [sum, Finset.sum_const, Finset.card_univ, nsmul_eq_mul, Finset.mul_sum]
  apply Finset.sum_congr rfl; intro x _
  apply Finset.sum_congr rfl; intro y _
  apply Finset.sum_congr rfl; intro z _
  ring

theorem cycle_contraction {L : Type*} [Fintype L]
    (b c d e : Kernel L) (a f : Int) :
    sum (fun _ _ => a) b c d e (fun _ _ => f) =
      a * f * ∑ x, ∑ y, path b d x y * path c e x y := by
  rw [diamond_contraction]
  simp only [Finset.mul_sum]
  apply Finset.sum_congr rfl; intro x _
  apply Finset.sum_congr rfl; intro y _
  ring

theorem cast_colorSum {V : Type*} [Fintype V] (w : Kernel V) :
    (colorSum w : ℚ) = Graphon.colorSum (fun i j => (w i j : ℚ)) := by
  simp only [colorSum, sum, Int.cast_sum, Int.cast_mul, Graphon.colorSum,
    Graphon.cliqueWeight]

theorem scaled_colorSum {V : Type*} [Fintype V] (w : Kernel V) (q : ℚ) :
    Graphon.colorSum (fun i j => (w i j : ℚ) / q) = (colorSum w : ℚ) / q^6 := by
  rw [cast_colorSum]
  simp only [Graphon.colorSum, Graphon.cliqueWeight, div_eq_mul_inv, ← inv_pow,
    Finset.sum_mul]
  apply Finset.sum_congr rfl; intro i _
  apply Finset.sum_congr rfl; intro j _
  apply Finset.sum_congr rfl; intro k _
  apply Finset.sum_congr rfl; intro l _
  ring

end K4Ramsey.IntegerTensorK4
