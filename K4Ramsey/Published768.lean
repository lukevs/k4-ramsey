import K4Ramsey.Multiplicity
import K4Ramsey.Published768Data

namespace K4Ramsey.Published768

def certificate : Template where
  order := 768
  redRows := redRows

theorem row_count : redRows.size = 768 := by
  native_decide

theorem valid_certificate : certificate.isValid = true := by
  native_decide

theorem red_edge_count : certificate.redEdgeCount = 148608 := by
  native_decide

/-- Lean's native evaluator independently reproduces Theorem 1.1's exact
balanced-blow-up numerator from the published 768-vertex adjacency matrix. -/
theorem exact_numerator : certificate.monoK4Numerator = 10487165184 := by
  native_decide

/-- The exact density is `4551721 / 150994944`, written without rational
normalization so the theorem needs only natural-number arithmetic. -/
theorem exact_density_from_paper :
    10487165184 * 150994944 = 4551721 * denominator768 := by
  native_decide

/-- Reuse the expensive counting theorem; only small arithmetic remains. -/
theorem mckay_is_strict_improvement :
    mckayNumerator < certificate.monoK4Numerator := by
  rw [exact_numerator]
  decide

end K4Ramsey.Published768
