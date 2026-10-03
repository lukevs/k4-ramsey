import K4Ramsey.Constructions.Final3840.Arithmetic
import K4Ramsey.Constructions.Final3840.SymmetryProof

/-! Numerical certificate for the embedded 3,840-class witness.

The integer is a proposed result, not an assumption: `native_decide` recomputes
the proved counter from the embedded block data. The subsequent rational
normalization is kernel checked. Native compilation remains in the trust base.
-/

namespace K4Ramsey.Final3840
open scoped BigOperators

/-- Exact ordered six-edge numerator, including repeated template labels. -/
theorem exact_count :
    160000 * (192 * Count.baseRoot 0) +
      4 * (∑ i : Coarse, Count.triangleAt i) +
      3 * (∑ i : Coarse, Count.cycleAt i) +
      6 * (∑ i : Coarse, Count.diamondAt i) +
      (∑ i : Coarse, Count.tetrahedronAt i) =
        (519196432373018212667371525712277942005760 : Int) := by
  native_decide

theorem exact_density : Graphon.density table =
    (8450462766487926638466333426306607129 : ℚ) /
      280384030360880691940646801777885184000 := by
  rw [Count.density_eq_count]
  simp_rw [baseRoot_eq]
  simp only [Finset.sum_const, Finset.card_univ, Fintype.card_fin, nsmul_eq_mul]
  norm_num only [Nat.cast_ofNat]
  rw [exact_count]
  norm_num

end K4Ramsey.Final3840
