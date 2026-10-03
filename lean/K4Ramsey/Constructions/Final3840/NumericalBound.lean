import K4Ramsey.Constructions.Final3840.Certificate
import K4Ramsey.Constructions.Final3840.Bound

/-! Numerical finite-order and asymptotic bounds for the fixed witness. -/

namespace K4Ramsey.Final3840

theorem exists_coloring_exact (n : Nat) (hn : 4 ≤ n) :
    ∃ g : Sym2 (Fin n) → Bool,
      Realization.coloringDensity g ≤
        (8450462766487926638466333426306607129 : ℚ) /
          280384030360880691940646801777885184000 := by
  simpa only [exact_density] using exists_coloring n hn

theorem ramsey_upperLimit_exact_bound :
    Asymptotic.ramseyUpperLimit ≤
      (8450462766487926638466333426306607129 : ℝ) /
        280384030360880691940646801777885184000 := by
  simpa only [Rat.cast_div, Rat.cast_ofNat] using
    Asymptotic.upperLimit_le_of_finite_bound _ exists_coloring_exact

theorem ramsey_limit_exact_bound (L : ℝ)
    (hL : Filter.Tendsto (fun n => (Asymptotic.minimumDensity n : ℝ))
      Filter.atTop (nhds L)) :
    L ≤ (8450462766487926638466333426306607129 : ℝ) /
      280384030360880691940646801777885184000 := by
  simpa only [Rat.cast_div, Rat.cast_ofNat] using
    Asymptotic.limit_le_of_finite_bound _ exists_coloring_exact L hL

theorem exists_coloring_below_decimal (n : Nat) (hn : 4 ≤ n) :
    ∃ g : Sym2 (Fin n) → Bool,
      Realization.coloringDensity g < (30139 : ℚ) / 1000000 := by
  obtain ⟨g, hg⟩ := exists_coloring_exact n hn
  refine ⟨g, lt_of_le_of_lt hg ?_⟩
  norm_num

end K4Ramsey.Final3840
