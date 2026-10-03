import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Logic.Equiv.Prod
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Push
import Mathlib.Tactic.Convert

/-! Finite probability by exact rational sums. No measure-theory or
probabilistic axioms are used. -/

namespace K4Ramsey.FiniteProbability

open scoped BigOperators
noncomputable section
open Classical

def mass {I A : Type*} [Fintype I] (w : I → A → ℚ) (x : I → A) : ℚ :=
  ∏ i, w i (x i)

def expectation {I A : Type*} [Fintype I] [Fintype A]
    (w : I → A → ℚ) (f : (I → A) → ℚ) : ℚ :=
  ∑ x, mass w x * f x

theorem mass_sum {I A : Type*} [Fintype I] [Fintype A]
    (w : I → A → ℚ) (hw : ∀ i, ∑ a, w i a = 1) :
    ∑ x, mass w x = 1 := by
  classical
  simp only [mass, ← Fintype.prod_sum, hw, Finset.prod_const_one]

theorem mass_nonneg {I A : Type*} [Fintype I]
    (w : I → A → ℚ) (hw : ∀ i a, 0 ≤ w i a) (x : I → A) :
    0 ≤ mass w x := Finset.prod_nonneg fun i _ => hw i (x i)

/-- Independence of observables on distinct coordinates. -/
theorem expectation_product {I A : Type*} [Fintype I] [Fintype A]
    (w f : I → A → ℚ) :
    expectation w (fun x => ∏ i, f i (x i)) =
      ∏ i, ∑ a, w i a * f i a := by
  classical
  simp only [expectation, mass, ← Finset.prod_mul_distrib, Fintype.prod_sum]

/-- Marginalizing independent coordinates leaves the same product law on
the retained coordinates. This includes arbitrary observables, not only
products. -/
theorem expectation_restrict {I A : Type*} [Fintype I] [Fintype A]
    (w : I → A → ℚ) (hw : ∀ i, ∑ a, w i a = 1)
    (p : I → Prop) (f : ({i // p i} → A) → ℚ) :
    expectation w (fun x => f (fun i => x i)) =
      expectation (fun (i : {i // p i}) a => w i a) f := by
  classical
  let e := Equiv.piEquivPiSubtypeProd p (fun _ : I => A)
  have split (x : I → A) : mass w x =
      mass (fun (i : {i // p i}) a => w i a) (e x).1 *
      mass (fun (i : {i // ¬p i}) a => w i a) (e x).2 := by
    exact (Fintype.prod_subtype_mul_prod_subtype p (fun i => w i (x i))).symm
  unfold expectation
  calc
    _ = ∑ y : ({i // p i} → A) × ({i // ¬p i} → A),
        mass (fun (i : {i // p i}) a => w i a) y.1 *
        mass (fun (i : {i // ¬p i}) a => w i a) y.2 * f y.1 := by
      apply Fintype.sum_equiv e
      intro x
      rw [split]
      rfl
    _ = _ := by
      rw [Fintype.sum_prod_type]
      simp only [mul_right_comm _ _ (f _), ← Finset.mul_sum]
      simp [mass, ← Fintype.prod_sum, hw]
      congr 1
      ext
      simp

/-- Changing the names of independent coordinates preserves expectation. -/
theorem expectation_equiv {I J A : Type*} [Fintype I] [Fintype J] [Fintype A]
    (e : J ≃ I) (w : I → A → ℚ) (f : (J → A) → ℚ) :
    expectation w (fun x => f (x ∘ e)) =
      expectation (fun j a => w (e j) a) f := by
  classical
  let E : (I → A) ≃ (J → A) := Equiv.arrowCongr e.symm (Equiv.refl A)
  unfold expectation
  apply Fintype.sum_equiv E
  intro x
  have h : mass w x = mass (fun j a => w (e j) a) (E x) := by
    exact (e.prod_comp (fun i => w i (x i))).symm
  rw [h]
  rfl

/-- Any distinct coordinates have the corresponding product distribution. -/
theorem expectation_embedding {I J A : Type*} [Fintype I] [Fintype J] [Fintype A]
    (e : J ↪ I) (w : I → A → ℚ) (hw : ∀ i, ∑ a, w i a = 1)
    (f : (J → A) → ℚ) :
    expectation w (fun x => f (x ∘ e)) =
      expectation (fun j a => w (e j) a) f := by
  classical
  let r : J ≃ Set.range e := Equiv.ofInjective e e.injective
  calc
    _ = expectation (fun (i : Set.range e) a => w i a)
        (fun y => f (y ∘ r)) := by
      have h := expectation_restrict w hw (· ∈ Set.range e) (fun y => f (y ∘ r))
      simp only [r, Equiv.ofInjective_apply, Function.comp_def] at h ⊢
      unfold expectation mass at h ⊢
      convert h using 1 <;> (congr 1 <;> ext <;> simp)
      left
      congr 1
      ext
      simp
    _ = _ := expectation_equiv r _ f

/-- The finite probabilistic method: some outcome is no larger than its
weighted average. Zero-probability outcomes cause no problem. -/
theorem exists_le_average {A : Type*} [Fintype A]
    (w f : A → ℚ) (hw : ∀ a, 0 ≤ w a) (hs : ∑ a, w a = 1) :
    ∃ a, f a ≤ ∑ b, w b * f b := by
  classical
  by_contra h
  push Not at h
  have pos : ∃ a, 0 < w a := by
    by_contra hn
    push Not at hn
    have : ∑ a, w a = 0 := Finset.sum_eq_zero fun a _ => le_antisymm (hn a) (hw a)
    linarith
  obtain ⟨a, ha⟩ := pos
  let m := ∑ b, w b * f b
  have strict : (∑ b, w b * m) < ∑ b, w b * f b := by
    apply Finset.sum_lt_sum
    · intro b _
      exact mul_le_mul_of_nonneg_left (le_of_lt (h b)) (hw b)
    · exact ⟨a, Finset.mem_univ a, mul_lt_mul_of_pos_left (h a) ha⟩
  rw [← Finset.sum_mul, hs, one_mul] at strict
  exact (lt_irrefl m) strict

/-- Exact Bernoulli mass, with `true` representing red. -/
def bernoulli (p : ℚ) (b : Bool) : ℚ := if b then p else 1 - p

theorem bernoulli_sum (p : ℚ) : ∑ b, bernoulli p b = 1 := by
  simp [bernoulli]

theorem bernoulli_nonneg (p : ℚ) (hp : 0 ≤ p) (hp' : p ≤ 1) (b : Bool) :
    0 ≤ bernoulli p b := by
  cases b <;> simp [bernoulli, hp, sub_nonneg.mpr hp']

end
end K4Ramsey.FiniteProbability
