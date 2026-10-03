import K4Ramsey.Counting.WeightedMultiplicity

/-!
# Validated computational inputs

Raw packed arrays remain available for generators and malformed-input tests.
The executable-facing API carries evidence that the representation checker
accepted them. This does not assert the still-unproved general equivalence of
the packed counter to a literal tuple sum.
-/

namespace K4Ramsey

/-- A packed template accompanied by evidence that its representation is valid. -/
structure ValidTemplate where
  raw : Template
  valid : raw.isValid = true

/-- A weighted input with both graph and weight-array invariants checked. -/
structure ValidWeightedTemplate where
  graph : ValidTemplate
  weights : Array Nat
  weights_valid : WeightedV1.validWeights graph.raw.order weights = true

/-- Named components of the blue-diagonal counting formula. -/
structure SubgraphCounts where
  redEdges : Nat
  blueTriangles : Nat
  redK4 : Nat
  blueK4 : Nat

/-- Accept raw storage only when the Lean representation checker succeeds. -/
def Template.validate (g : Template) : Except String ValidTemplate :=
  if h : g.isValid = true then .ok ⟨g, h⟩
  else .error "invalid symmetric blue-diagonal template"

/-- Validate weights before exposing a weighted counting input. -/
def ValidTemplate.withWeights (g : ValidTemplate) (weights : Array Nat) :
    Except String ValidWeightedTemplate :=
  if h : WeightedV1.validWeights g.raw.order weights = true then .ok ⟨g, weights, h⟩
  else .error "invalid positive integer weights"

/-- Count each component once; executable printers share this implementation. -/
def ValidTemplate.countSubgraphs (g : ValidTemplate) : SubgraphCounts :=
  let blue := g.raw.blueRows
  ⟨g.raw.redEdgeCount, triangleCount g.raw.order blue,
    fourCliqueCount g.raw.order g.raw.redRows, fourCliqueCount g.raw.order blue⟩

/-- Ordered numerator assembled from the four named subgraph counts. -/
def SubgraphCounts.numerator (counts : SubgraphCounts) (order : Nat) : Nat :=
  order + 14 * (order * (order - 1) / 2 - counts.redEdges) +
    36 * counts.blueTriangles + 24 * (counts.redK4 + counts.blueK4)

/-- The validated facade computes exactly the existing packed formula.
This is an API-refactoring theorem, not the missing literal-count theorem. -/
theorem ValidTemplate.countSubgraphs_numerator (g : ValidTemplate) :
    g.countSubgraphs.numerator g.raw.order = g.raw.monoK4Numerator := by
  rfl

/-- Weighted recount accepts evidence of both representation invariants. -/
def ValidWeightedTemplate.numerator (g : ValidWeightedTemplate) : Nat :=
  WeightedV1.numerator g.graph.raw g.weights

end K4Ramsey
