import Mathlib.Data.Fintype.BigOperators
import Mathlib.Data.Rat.Cast.Order
import Mathlib.Tactic.Ring

/-! The exact local identity behind balanced two-way refinements.

The final 3,840-part construction uses this operation twice. This module
proves its six-edge algebra, independently of the external Fourier checker.
It does not certify the final matrices or their numerical contraction sums.
-/

namespace K4Ramsey.SignRefinement

open scoped BigOperators

def sign (b : Bool) : ℚ := if b then 1 else -1

/-- Average the six-edge product over four independently chosen signs.
Edge order: 01, 02, 03, 12, 13, 23. -/
def fiberAverage (w a : Fin 6 → ℚ) : ℚ :=
  (∑ b₀ : Bool, ∑ b₁ : Bool, ∑ b₂ : Bool, ∑ b₃ : Bool,
    (w 0 + sign b₀ * sign b₁ * a 0) *
    (w 1 + sign b₀ * sign b₂ * a 1) *
    (w 2 + sign b₀ * sign b₃ * a 2) *
    (w 3 + sign b₁ * sign b₂ * a 3) *
    (w 4 + sign b₁ * sign b₃ * a 4) *
    (w 5 + sign b₂ * sign b₃ * a 5)) / 16

def base (w : Fin 6 → ℚ) : ℚ := w 0 * w 1 * w 2 * w 3 * w 4 * w 5

/-- Four triangles, each multiplied by the three unchanged edges. -/
def triangles (w a : Fin 6 → ℚ) : ℚ :=
  a 0 * a 1 * a 3 * w 2 * w 4 * w 5 +
  a 0 * a 2 * a 4 * w 1 * w 3 * w 5 +
  a 1 * a 2 * a 5 * w 0 * w 3 * w 4 +
  a 3 * a 4 * a 5 * w 0 * w 1 * w 2

/-- Three four-cycles, each multiplied by the two unchanged diagonals. -/
def cycles (w a : Fin 6 → ℚ) : ℚ :=
  a 0 * a 2 * a 3 * a 5 * w 1 * w 4 +
  a 0 * a 1 * a 4 * a 5 * w 2 * w 3 +
  a 1 * a 2 * a 3 * a 4 * w 0 * w 5

/-- Only even-degree edge subsets survive sign averaging: the empty set,
four triangles, and three four-cycles. All other terms cancel exactly. -/
theorem fiberAverage_eq (w a : Fin 6 → ℚ) :
    fiberAverage w a = base w + triangles w a + cycles w a := by
  simp only [fiberAverage, Fintype.sum_bool, sign, Bool.false_eq_true, ite_false, ite_true]
  unfold base triangles cycles
  ring

/-- Both colors use opposite amplitudes; the blue triangle terms change
sign while the four-cycle terms do not. -/
theorem monochromatic_fiberAverage (w a : Fin 6 → ℚ) :
    fiberAverage w a + fiberAverage (fun e => 1 - w e) (fun e => -a e) =
      base w + base (fun e => 1 - w e) +
      triangles w a - triangles (fun e => 1 - w e) a +
      cycles w a + cycles (fun e => 1 - w e) a := by
  rw [fiberAverage_eq, fiberAverage_eq]
  unfold triangles cycles
  ring

end K4Ramsey.SignRefinement
