import K4Ramsey.Realization
import Mathlib.Data.Finset.Lattice.Fold
import Mathlib.Topology.Instances.Real.Lemmas
import Mathlib.Topology.Order.OrderClosed
import Mathlib.Order.Filter.AtTopBot.Basic
import Mathlib.Order.LiminfLimsup

/-! The finite-to-limit implication for the actual minimum over colorings.
The finite realization theorem is stronger than this implication. We do not
assume the desired upper bound as a hypothesis or define the Ramsey constant
to be the density of our template. -/

namespace K4Ramsey.Asymptotic

open Classical Filter
open scoped Topology
noncomputable section

/-- The genuine finite minimum over all red/blue colorings. -/
def minimumDensity (n : Nat) : ℚ :=
  (Finset.univ : Finset (Sym2 (Fin n) → Bool)).inf'
    Finset.univ_nonempty Realization.coloringDensity

theorem minimumDensity_le (n : Nat) (g : Sym2 (Fin n) → Bool) :
    minimumDensity n ≤ Realization.coloringDensity g := by
  exact Finset.inf'_le _ (Finset.mem_univ g)

theorem minimumDensity_nonnegative (n : Nat) : 0 ≤ minimumDensity n := by
  apply Finset.le_inf'
  intro g _
  apply div_nonneg _ (Nat.cast_nonneg _)
  apply Finset.sum_nonneg
  intro x _
  unfold Realization.copyScore
  rw [Realization.monochromatic_indicator]
  split <;> norm_num

/-- The upper limiting finite minimum. Bounding this needs no separate
assumption that the minimum-density sequence converges. -/
def ramseyUpperLimit : ℝ := limsup (fun n => (minimumDensity n : ℝ)) atTop

theorem upperLimit_le_of_finite_bound (U : ℚ)
    (hU : ∀ n, 4 ≤ n → ∃ g : Sym2 (Fin n) → Bool,
      Realization.coloringDensity g ≤ U) :
    ramseyUpperLimit ≤ (U : ℝ) := by
  apply limsup_le_of_le
  · exact isCoboundedUnder_le_of_le atTop
      (fun n => (show (0 : ℝ) ≤ (minimumDensity n : ℝ) by
        exact_mod_cast minimumDensity_nonnegative n))
  · apply eventually_atTop.2
    refine ⟨4, fun n hn => ?_⟩
    obtain ⟨g, hg⟩ := hU n hn
    exact_mod_cast (minimumDensity_le n g).trans hg

/-- A uniform construction bound passes to any asymptotic Ramsey limit.
The only limit hypothesis is convergence of the actual finite minima. -/
theorem limit_le_of_finite_bound (U : ℚ)
    (hU : ∀ n, 4 ≤ n → ∃ g : Sym2 (Fin n) → Bool,
      Realization.coloringDensity g ≤ U)
    (L : ℝ) (hL : Tendsto (fun n => (minimumDensity n : ℝ)) atTop (𝓝 L)) :
    L ≤ (U : ℝ) := by
  apply le_of_tendsto hL
  apply eventually_atTop.2
  refine ⟨4, fun n hn => ?_⟩
  obtain ⟨g, hg⟩ := hU n hn
  exact_mod_cast (minimumDensity_le n g).trans hg

end
end K4Ramsey.Asymptotic
