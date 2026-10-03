import K4Ramsey.Constructions.Clebsch192.Certificate
import K4Ramsey.Core.Realization
import K4Ramsey.Core.Asymptotic
import Mathlib.Data.Fin.Embedding

/-! End-to-end finite upper bound for the compact Clebsch construction.

The statement is stronger than an asymptotic assertion: at every order
`n ≥ 4` some actual coloring has monochromatic density at most the stated
rational number. The arithmetic certificate uses native evaluation; the
counting reduction and realization argument are kernel-checked proofs.

This is intentionally named `Clebsch192`, not `FinalClebsch`: the stronger
3,840-part refinement has not yet been connected to this proof pipeline.
-/

namespace K4Ramsey.Clebsch192

theorem exists_coloring (n : Nat) (hn : 4 ≤ n) :
    ∃ g : Sym2 (Fin n) → Bool,
      Realization.coloringDensity g ≤ (1013294255057839 : ℚ) / 33620705806123008 := by
  let : Nonempty (Fin 4 ↪ Fin n) := ⟨Fin.castLEEmb hn⟩
  simpa only [exact_density] using
    Realization.exists_coloring_le (V := Fin n) table
      table_symmetric table_nonnegative table_le_one

theorem exists_coloring_below_decimal (n : Nat) (hn : 4 ≤ n) :
    ∃ g : Sym2 (Fin n) → Bool,
      Realization.coloringDensity g < (30139 : ℚ) / 1000000 := by
  obtain ⟨g, hg⟩ := exists_coloring n hn
  refine ⟨g, lt_of_le_of_lt hg ?_⟩
  norm_num

/-- The upper bound for any limit of the genuine finite Ramsey minima. -/
theorem ramsey_upperLimit_bound :
    Asymptotic.ramseyUpperLimit ≤ (1013294255057839 : ℝ) / 33620705806123008 := by
  simpa only [Rat.cast_div, Rat.cast_ofNat] using
    Asymptotic.upperLimit_le_of_finite_bound _ exists_coloring

/-- Specialization when the minimum-density sequence is known to converge. -/
theorem ramsey_limit_bound (L : ℝ)
    (hL : Filter.Tendsto (fun n => (Asymptotic.minimumDensity n : ℝ))
      Filter.atTop (nhds L)) :
    L ≤ (1013294255057839 : ℝ) / 33620705806123008 := by
  simpa only [Rat.cast_div, Rat.cast_ofNat] using
    Asymptotic.limit_le_of_finite_bound _ exists_coloring L hL

end K4Ramsey.Clebsch192
