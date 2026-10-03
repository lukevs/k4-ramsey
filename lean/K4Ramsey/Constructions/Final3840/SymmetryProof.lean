import K4Ramsey.Constructions.Final3840.Symmetry
import K4Ramsey.Constructions.Final3840.CountCorrect

namespace K4Ramsey.Final3840

theorem shift_bijective : ∀ i, Function.Bijective (shift i) := by native_decide
theorem shift_zero : ∀ i, shift i 0 = i := by native_decide
theorem shift_preserves_base : ∀ i j k,
    baseNumerator (shift i j) (shift i k) = baseNumerator j k := by native_decide

noncomputable def shiftEquiv (i : Coarse) : Coarse ≃ Coarse := Equiv.ofBijective (shift i) (shift_bijective i)

theorem baseRoot_eq (i : Coarse) : Count.baseRoot i = Count.baseRoot 0 := by
  symm
  unfold Count.baseRoot
  apply Fintype.sum_equiv (shiftEquiv i)
  intro j
  apply Fintype.sum_equiv (shiftEquiv i)
  intro k
  apply Fintype.sum_equiv (shiftEquiv i)
  intro l
  simp only [Count.b_eq, shiftEquiv, Equiv.ofBijective_apply]
  have h (j : Coarse) : baseNumerator i (shift i j) = baseNumerator 0 j := by
    simpa only [shift_zero] using shift_preserves_base i 0 j
  simp only [h, shift_preserves_base]

end K4Ramsey.Final3840
