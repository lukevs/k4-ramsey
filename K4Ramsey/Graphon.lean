import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.Rat.Cast.Order
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.Fin.Tuple.Basic
import Mathlib.Tactic.Ring

/-!
# The literal K4 objective

These definitions use all ordered tuples, including repeated template labels.
They are independent of the bitset counter and of external audit receipts.
-/

namespace K4Ramsey.Graphon

open scoped BigOperators

/-- The six-edge product for four ordered labels. -/
def cliqueWeight {V : Type*} (W : V → V → ℚ) (i j k l : V) : ℚ :=
  W i j * W i k * W i l * W j k * W j l * W k l

/-- The literal ordered sum for one color. -/
def colorSum {V : Type*} [Fintype V] (W : V → V → ℚ) : ℚ :=
  ∑ i, ∑ j, ∑ k, ∑ l, cliqueWeight W i j k l

/-- Equal-mass step-template density. Repeated labels are intentional. -/
def density {V : Type*} [Fintype V] (W : V → V → ℚ) : ℚ :=
  (colorSum W + colorSum (fun i j => 1 - W i j)) / (Fintype.card V : ℚ) ^ 4

/-- Factorized pair counter, with exactly the same index ranges as the
literal sum. This is the mathematical specification for an optimized runner. -/
def pairSum {V : Type*} [Fintype V] (W : V → V → ℚ) : ℚ :=
  ∑ i, ∑ j, W i j *
    (∑ k, ∑ l, (W i k * W j k) * (W i l * W j l) * W k l)

/-- Counting correctness of the pair factorization, for every finite table.
No symmetry, diagonal convention, or probability bound is needed. -/
theorem pairSum_eq_colorSum {V : Type*} [Fintype V] (W : V → V → ℚ) :
    pairSum W = colorSum W := by
  unfold pairSum colorSum
  apply Finset.sum_congr rfl
  intro i _
  apply Finset.sum_congr rfl
  intro j _
  simp only [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro k _
  apply Finset.sum_congr rfl
  intro l _
  unfold cliqueWeight
  ring

/-- A Cayley probability table is specified by its difference kernel. -/
def cayley {G : Type*} [AddGroup G] (f : G → ℚ) (i j : G) : ℚ := f (j - i)

/-- Simultaneously translating all four labels preserves their contribution. -/
theorem cayley_translate {G : Type*} [AddCommGroup G] (f : G → ℚ)
    (a i j k l : G) :
    cliqueWeight (cayley f) (a + i) (a + j) (a + k) (a + l) =
      cliqueWeight (cayley f) i j k l := by
  simp [cliqueWeight, cayley]

/-- The four-label Cayley count reduces to a rooted three-label count.
This is a proved change of variables, not an assumed symmetry factor. -/
theorem cayley_colorSum {G : Type*} [Fintype G] [AddCommGroup G] (f : G → ℚ) :
    colorSum (cayley f) = (Fintype.card G : ℚ) *
      (∑ j, ∑ k, ∑ l, cliqueWeight (cayley f) 0 j k l) := by
  have rooted (i : G) :
      (∑ j, ∑ k, ∑ l, cliqueWeight (cayley f) i j k l) =
        ∑ j, ∑ k, ∑ l, cliqueWeight (cayley f) 0 j k l := by
    symm
    apply Fintype.sum_equiv (Equiv.addLeft i)
    intro j
    apply Fintype.sum_equiv (Equiv.addLeft i)
    intro k
    apply Fintype.sum_equiv (Equiv.addLeft i)
    intro l
    simpa using (cayley_translate f i 0 j k l).symm
  simp only [colorSum, rooted, Finset.sum_const, Finset.card_univ, nsmul_eq_mul]

theorem sum_tuple_succ {T : Type*} [Fintype T] {n : Nat}
    (f : (Fin (n + 1) → T) → ℚ) :
    (∑ x, f x) = ∑ a, ∑ y : Fin n → T, f (Fin.cons a y) := by
  rw [← (Fin.consEquiv (fun _ : Fin (n + 1) => T)).sum_comp f,
    Fintype.sum_prod_type]
  rfl

/-- Function-indexed four-tuples and four nested sums give the same count. -/
theorem colorSum_eq_tupleSum {T : Type*} [Fintype T] (W : T → T → ℚ) :
    colorSum W = ∑ x : Fin 4 → T, cliqueWeight W (x 0) (x 1) (x 2) (x 3) := by
  simp [sum_tuple_succ, colorSum]
  rfl

end K4Ramsey.Graphon
