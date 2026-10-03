import K4Ramsey.Final3840Reduction
import K4Ramsey.Asymptotic
import Mathlib.Data.Fin.Embedding

/-! Symbolic upper bound for the actual final witness. No numerical density
is assumed here. The missing numerical contraction certificate is deliberately
not disguised as a hypothesis of an "exact density" theorem. -/

namespace K4Ramsey.Final3840

theorem exists_coloring (n : Nat) (hn : 4 ≤ n) :
    ∃ g : Sym2 (Fin n) → Bool,
      Realization.coloringDensity g ≤ Graphon.density table := by
  let : Nonempty (Fin 4 ↪ Fin n) := ⟨Fin.castLEEmb hn⟩
  exact finite_realization

theorem ramsey_upperLimit_bound :
    Asymptotic.ramseyUpperLimit ≤ (Graphon.density table : ℝ) :=
  Asymptotic.upperLimit_le_of_finite_bound _ exists_coloring

end K4Ramsey.Final3840
