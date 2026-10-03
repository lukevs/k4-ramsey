import K4Ramsey.Constructions.Clebsch192.Bound
import K4Ramsey.Counting.SignRefinement
import K4Ramsey.Constructions.Final3840.Bound
import K4Ramsey.Constructions.Final3840.Arithmetic
import K4Ramsey.Constructions.Final3840.SymmetryProof

-- These general theorems must not depend on sorryAx or native evaluation.
#print axioms K4Ramsey.Graphon.pairSum_eq_colorSum
#print axioms K4Ramsey.Graphon.cayley_colorSum
#print axioms K4Ramsey.FiniteProbability.expectation_embedding
#print axioms K4Ramsey.Realization.monochromatic_indicator
#print axioms K4Ramsey.Realization.exists_coloring_le
#print axioms K4Ramsey.Asymptotic.limit_le_of_finite_bound
#print axioms K4Ramsey.Asymptotic.upperLimit_le_of_finite_bound
#print axioms K4Ramsey.SignRefinement.monochromatic_fiberAverage
#print axioms K4Ramsey.TensorK4.centered_leaf_zero
#print axioms K4Ramsey.TensorK4.centered_expansion
#print axioms K4Ramsey.TensorK4.diamond_contraction

-- These additionally trust native evaluation of the explicit finite table.
#print axioms K4Ramsey.Clebsch192.exact_rooted_sum
#print axioms K4Ramsey.Clebsch192.exact_density
#print axioms K4Ramsey.Clebsch192.exists_coloring
#print axioms K4Ramsey.Clebsch192.ramsey_upperLimit_bound
#print axioms K4Ramsey.Clebsch192.ramsey_limit_bound
#print axioms K4Ramsey.Final3840.data_shape
#print axioms K4Ramsey.Final3840.centered_rows
#print axioms K4Ramsey.Final3840.red_count_reduction
#print axioms K4Ramsey.Final3840.blue_count_reduction
#print axioms K4Ramsey.Final3840.finite_realization
#print axioms K4Ramsey.Final3840.ramsey_upperLimit_bound
#print axioms K4Ramsey.Final3840.Count.paths_eq
#print axioms K4Ramsey.Final3840.Count.raw_total
#print axioms K4Ramsey.Final3840.Count.density_eq_count
#print axioms K4Ramsey.Final3840.baseRoot_eq
