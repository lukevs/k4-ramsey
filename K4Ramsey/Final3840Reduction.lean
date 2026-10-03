import K4Ramsey.Final3840Validity
import K4Ramsey.CenteredExpansion

namespace K4Ramsey.Final3840

open TensorK4

def baseLift : Kernel Vertex := liftBase baseTable
def delta : Kernel Vertex := fun u v => perturbation u.1 v.1 u.2 v.2

/-- The complete literal red count reduced to five contractions. This is a
counting-correctness theorem, not yet a numerical evaluation of those terms. -/
theorem red_count_reduction : Graphon.colorSum table =
    sum baseLift baseLift baseLift baseLift baseLift baseLift
    + 4 * sum delta delta baseLift delta baseLift baseLift
    + 3 * sum baseLift delta delta delta delta baseLift
    + 6 * sum delta delta delta delta delta baseLift
    + sum delta delta delta delta delta delta := by
  have ht : table = fun u v => liftBase baseTable u v + delta u v := by
    funext u v
    exact table_decomposition u v
  rw [ht]
  apply centered_expansion
  · apply symmetric_transpose
    intro u v
    simp only [liftBase, baseTable, base_symmetry u.1 v.1]
  · apply symmetric_transpose
    intro u v
    exact perturbation_symmetric u.1 v.1 u.2 v.2
  · exact perturbation_columns

def blueBase : Kernel Coarse := fun u v => 1 - baseTable u v
def blueLift : Kernel Vertex := liftBase blueBase
def blueDelta : Kernel Vertex := fun u v => -delta u v

theorem blue_count_reduction : Graphon.colorSum (fun u v => 1 - table u v) =
    sum blueLift blueLift blueLift blueLift blueLift blueLift
    + 4 * sum blueDelta blueDelta blueLift blueDelta blueLift blueLift
    + 3 * sum blueLift blueDelta blueDelta blueDelta blueDelta blueLift
    + 6 * sum blueDelta blueDelta blueDelta blueDelta blueDelta blueLift
    + sum blueDelta blueDelta blueDelta blueDelta blueDelta blueDelta := by
  have ht : (fun u v => 1 - table u v) =
      fun u v => liftBase blueBase u v + blueDelta u v := by
    funext u v
    rw [table_decomposition]
    simp only [liftBase, blueBase, blueDelta, delta]
    ring
  rw [ht]
  apply centered_expansion
  · apply symmetric_transpose
    intro u v
    simp only [liftBase, blueBase, baseTable, base_symmetry u.1 v.1]
  · apply symmetric_transpose
    intro u v
    simp only [blueDelta, delta, perturbation_symmetric u.1 v.1 u.2 v.2]
  · intro i j y
    simp only [blueDelta, delta, Finset.sum_neg_distrib, perturbation_columns, neg_zero]

end K4Ramsey.Final3840
