import K4Ramsey.Graphon
import K4Ramsey.FiniteProbability
import Mathlib.Data.Sym.Sym2
import Mathlib.Data.Finset.Sym
import Mathlib.Data.Fintype.Pi
import Mathlib.Algebra.BigOperators.Fin

/-! The finite random-coloring construction. Colors are functions on unordered
pairs, so edge reversal cannot change a color. Diagonal pairs are immaterial:
every tested copy of K4 has four distinct vertices. -/

namespace K4Ramsey.Realization

open scoped BigOperators
open FiniteProbability
open Classical
noncomputable section

def edges : Fin 6 ↪ Sym2 (Fin 4) where
  toFun := ![s(0, 1), s(0, 2), s(0, 3), s(1, 2), s(1, 3), s(2, 3)]
  inj' := by decide

def monochromatic (b : Fin 6 → Bool) : ℚ :=
  (∏ e, if b e then 1 else 0) + (∏ e, if b e then 0 else 1)

/-- The score is exactly the indicator of six edges of one color. -/
theorem monochromatic_indicator : ∀ b : Fin 6 → Bool,
    monochromatic b =
      if (∀ e, b e = true) ∨ (∀ e, b e = false) then 1 else 0 := by
  intro b
  simp only [monochromatic, Fin.prod_univ_six, Fin.forall_fin_succ]
  cases h0 : b 0 <;> cases h1 : b 1 <;> cases h2 : b 2 <;>
    cases h3 : b 3 <;> cases h4 : b 4 <;> cases h5 : b 5 <;>
    simp_all

def copyScore {V : Type*} (g : Sym2 V → Bool) (x : Fin 4 ↪ V) : ℚ :=
  monochromatic (g ∘ (edges.trans x.sym2Map))

/-- Ordered injective-copy density. Each unordered four-set has 24 orderings. -/
def coloringDensity {V : Type*} [Fintype V] (g : Sym2 V → Bool) : ℚ :=
  (∑ x : Fin 4 ↪ V, copyScore g x) / (Fintype.card (Fin 4 ↪ V) : ℚ)

def edgeProbability {V T : Type*} (W : T → T → ℚ)
    (hW : ∀ i j, W i j = W j i) (c : V → T) : Sym2 V → ℚ :=
  Sym2.lift ⟨fun u v => W (c u) (c v), fun u v => hW (c u) (c v)⟩

def colorLaw {V T : Type*} (W : T → T → ℚ)
    (hW : ∀ i j, W i j = W j i) (c : V → T) (e : Sym2 V) : Bool → ℚ :=
  bernoulli (edgeProbability W hW c e)

theorem expectation_add {I A : Type*} [Fintype I] [Fintype A]
    (w : I → A → ℚ) (f g : (I → A) → ℚ) :
    expectation w (fun x => f x + g x) = expectation w f + expectation w g := by
  simp [expectation, mul_add, Finset.sum_add_distrib]

theorem expected_monochromatic (p : Fin 6 → ℚ) :
    expectation (fun e => bernoulli (p e)) monochromatic =
      (∏ e, p e) + ∏ e, (1 - p e) := by
  unfold monochromatic
  rw [expectation_add,
    expectation_product _ (fun _ (b : Bool) => if b then (1 : ℚ) else 0),
    expectation_product _ (fun _ (b : Bool) => if b then (0 : ℚ) else 1)]
  simp [bernoulli]

/-- Exact probability for any four distinct vertices, conditional on their
template labels. The labels themselves are allowed to repeat. -/
theorem expected_copy {V T : Type*} [Fintype V]
    (W : T → T → ℚ) (hW : ∀ i j, W i j = W j i)
    (c : V → T) (x : Fin 4 ↪ V) :
    expectation (colorLaw W hW c) (fun g => copyScore g x) =
      Graphon.cliqueWeight W (c (x 0)) (c (x 1)) (c (x 2)) (c (x 3)) +
      Graphon.cliqueWeight (fun i j => 1 - W i j)
        (c (x 0)) (c (x 1)) (c (x 2)) (c (x 3)) := by
  unfold copyScore
  rw [expectation_embedding (edges.trans x.sym2Map) (colorLaw W hW c)
    (fun e => bernoulli_sum (edgeProbability W hW c e)) monochromatic]
  change expectation (fun e => bernoulli (edgeProbability W hW c
    ((edges.trans x.sym2Map) e))) monochromatic = _
  rw [expected_monochromatic]
  simp [Fin.prod_univ_six, edges, edgeProbability, Graphon.cliqueWeight]

def uniformLaw {I T : Type*} [Fintype T] (_ : I) (_ : T) : ℚ :=
  1 / (Fintype.card T : ℚ)

theorem uniformLaw_sum {I T : Type*} [Fintype T] [Nonempty T] (i : I) :
    ∑ a : T, uniformLaw i a = 1 := by
  simp [uniformLaw, Fintype.card_ne_zero]

theorem expectation_sum {I A B : Type*} [Fintype I] [Fintype A] [Fintype B]
    (w : I → A → ℚ) (f : B → (I → A) → ℚ) :
    expectation w (fun x => ∑ b, f b x) = ∑ b, expectation w (f b) := by
  simp only [expectation, Finset.mul_sum]
  rw [Finset.sum_comm]

theorem expectation_div {I A : Type*} [Fintype I] [Fintype A]
    (w : I → A → ℚ) (f : (I → A) → ℚ) (d : ℚ) :
    expectation w (fun x => f x / d) = expectation w f / d := by
  simp [expectation, div_eq_mul_inv, mul_assoc, Finset.sum_mul]

/-- Uniform independent labels give the literal template density for each
injective copy, with no asymptotic approximation. -/
theorem expected_labeled_copy {V T : Type*} [Fintype V] [Fintype T] [Nonempty T]
    (W : T → T → ℚ) (hW : ∀ i j, W i j = W j i) (x : Fin 4 ↪ V) :
    expectation (uniformLaw (T := T))
      (fun c => expectation (colorLaw W hW c) (fun g => copyScore g x)) =
        Graphon.density W := by
  simp_rw [expected_copy]
  change expectation uniformLaw (fun c =>
    (fun y : Fin 4 → T => Graphon.cliqueWeight W (y 0) (y 1) (y 2) (y 3) +
      Graphon.cliqueWeight (fun i j => 1 - W i j) (y 0) (y 1) (y 2) (y 3))
        (c ∘ x)) = _
  rw [expectation_embedding x uniformLaw uniformLaw_sum (fun y : Fin 4 → T =>
    Graphon.cliqueWeight W (y 0) (y 1) (y 2) (y 3) +
      Graphon.cliqueWeight (fun i j => 1 - W i j) (y 0) (y 1) (y 2) (y 3))]
  simp only [expectation, mass, uniformLaw, Finset.prod_const, Finset.card_univ,
    Fintype.card_fin, one_div, mul_add, Finset.sum_add_distrib, ← Finset.mul_sum]
  simp only [Graphon.density, Graphon.colorSum_eq_tupleSum]
  ring_nf
  congr 2 <;> (congr 1 <;> ext <;> simp)

/-- Expected density of the actual finite random coloring is exactly the
template density, for every vertex set with at least four vertices. -/
theorem expected_density {V T : Type*} [Fintype V] [Fintype T] [Nonempty T]
    [Nonempty (Fin 4 ↪ V)] (W : T → T → ℚ) (hW : ∀ i j, W i j = W j i) :
    expectation (uniformLaw (I := V) (T := T))
      (fun c => expectation (colorLaw W hW c) coloringDensity) = Graphon.density W := by
  change expectation uniformLaw (fun c => expectation (colorLaw W hW c)
    (fun g => (∑ x, copyScore g x) / (Fintype.card (Fin 4 ↪ V) : ℚ))) = _
  simp_rw [expectation_div, expectation_sum, expected_labeled_copy]
  simp [Fintype.card_ne_zero]

/-- Finite realization theorem: a symmetric probability table supplies a
genuine two-coloring no worse than its density, at every finite order ≥ 4.
This is stronger than merely obtaining a limit of balanced blow-ups. -/
theorem exists_coloring_le {V T : Type*} [Fintype V] [Fintype T] [Nonempty T]
    [Nonempty (Fin 4 ↪ V)] (W : T → T → ℚ)
    (hW : ∀ i j, W i j = W j i) (h0 : ∀ i j, 0 ≤ W i j)
    (h1 : ∀ i j, W i j ≤ 1) :
    ∃ g : Sym2 V → Bool, coloringDensity g ≤ Graphon.density W := by
  letI : DecidableEq (Sym2 V) := Classical.typeDecidableEq _
  have hu : ∀ (i : V) (a : T), 0 ≤ uniformLaw i a := by
    intro i a
    exact div_nonneg (by norm_num) (Nat.cast_nonneg _)
  obtain ⟨c, hc⟩ := exists_le_average (mass (uniformLaw (I := V) (T := T)))
    (fun c => expectation (colorLaw W hW c) coloringDensity)
    (mass_nonneg _ hu) (mass_sum _ uniformLaw_sum)
  change expectation (colorLaw W hW c) coloringDensity ≤
    expectation uniformLaw (fun c => expectation (colorLaw W hW c) coloringDensity) at hc
  rw [expected_density W hW] at hc
  have he : ∀ e b, 0 ≤ colorLaw W hW c e b := by
    intro e b
    induction e using Sym2.inductionOn with
    | hf u v => exact bernoulli_nonneg _ (h0 _ _) (h1 _ _) b
  obtain ⟨g, hg⟩ := exists_le_average (mass (colorLaw W hW c)) coloringDensity
    (mass_nonneg _ he) (mass_sum _ (fun e => bernoulli_sum _))
  exact ⟨g, hg.trans hc⟩

end
end K4Ramsey.Realization
