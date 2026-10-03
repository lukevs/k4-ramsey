import K4Ramsey.IO.TemplateInput

namespace K4Ramsey.Tests.TemplateInput

/-- The shared parser and named-count facade preserve a tiny exact count. -/
theorem parsed_count :
    (match K4Ramsey.TemplateInput.parseRows ["01", "10"] with
      | .ok g => g.countSubgraphs.numerator g.raw.order
      | .error _ => 0) = 2 := by native_decide

/-- Parsing cannot yield a graph that fails the representation checker. -/
theorem accepted_graph_valid (g : ValidTemplate) : g.raw.isValid = true := g.valid

/-- Shape, alphabet, diagonal, and symmetry failures all reject. -/
theorem malformed_rows_rejected :
    ([[], ["1"], ["01", "00"], ["00"], ["0x", "x0"]].all fun rows =>
      match K4Ramsey.TemplateInput.parseRows rows with
      | .ok _ => false
      | .error _ => true) = true := by native_decide

/-- A two-part all-blue weighted graph has numerator totalWeight^4. -/
theorem parsed_weighted_count :
    (match K4Ramsey.TemplateInput.parseWeightedRows ["2 3", "00", "00"] with
      | .ok g => g.numerator
      | .error _ => 0) = 625 := by native_decide

theorem malformed_weights_rejected :
    ([[], ["0 1", "00", "00"], ["65536 1", "00", "00"],
      ["1", "00", "00"], ["a 1", "00", "00"]].all fun rows =>
      match K4Ramsey.TemplateInput.parseWeightedRows rows with
      | .ok _ => false
      | .error _ => true) = true := by native_decide

end K4Ramsey.Tests.TemplateInput
