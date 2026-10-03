import K4Ramsey.Constructions.Final3840.Reduction
import K4Ramsey.Core.Asymptotic
import Mathlib.Data.Fin.Embedding

/-! Symbolic upper bound for the actual final witness. No numerical density
is assumed here. `NumericalBound` specializes this result using the
native-evaluated arithmetic certificate in `Certificate`. -/

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
