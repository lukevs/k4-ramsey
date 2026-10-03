import K4Ramsey.Core.Graphon
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.BigOperators.Fin

/-! The compact, two-parameter Clebsch construction, in canonical group
coordinates. This is B192 at p = 32/41 and h = 22/41, not the later
3,840-part refinement. No historical experiment artifact is imported. -/

namespace K4Ramsey.Clebsch192

open scoped BigOperators

abbrev Position := Fin 4 → ZMod 2
abbrev Vertex := ZMod 3 × ZMod 2 × ZMod 2 × Position

/-- Closed Clebsch neighborhood of zero: weights zero, one, or four. -/
def closedNeighborhood (x : Position) : Bool :=
  let weight := ∑ i, (x i).val
  weight == 0 || weight == 1 || weight == 4

/-- Integer numerator of the difference kernel, with denominator 41. -/
def numerator (v : Vertex) : Nat :=
  let a := v.1
  let e := v.2.1
  let s := v.2.2.1
  let x := v.2.2.2
  let inside := closedNeighborhood x
  let z := if inside then 0 else 41
  if s ≠ 0 then
    if a = 0 then (if inside then 32 else 0) else z
  else if a = 0 then
    if e = 0 then z
    else if x = 0 then 22 else if inside then 41 else 0
  else if e = 0 then (if inside then 41 else 0) else z

def kernel (v : Vertex) : ℚ := (numerator v : ℚ) / 41

def table : Vertex → Vertex → ℚ := Graphon.cayley kernel

def rootedSum (f : Vertex → ℚ) : ℚ :=
  ∑ j, ∑ k, ∑ l, Graphon.cliqueWeight (Graphon.cayley f) 0 j k l

end K4Ramsey.Clebsch192
