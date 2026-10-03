import K4Ramsey.Final3840Data
import K4Ramsey.Graphon

/-! The final witness, defined independently of every external count.
Coarse coordinates are `(a,e,s,x)` in `3 × 2 × 2 × 16`, in that order.
The twenty fine labels retain the original five-way and two sign refinements.
-/

namespace K4Ramsey.Final3840

open scoped BigOperators

abbrev Coarse := Fin 192
abbrev Fiber := Fin 20
abbrev Vertex := Coarse × Fiber

def denominator : Nat := 65536

def baseNumerator (u v : Coarse) : Nat :=
  let a := u.val / 64 == v.val / 64
  let e := u.val / 32 % 2 == v.val / 32 % 2
  let s := u.val / 16 % 2 == v.val / 16 % 2
  let z := (u.val % 16) ^^^ (v.val % 16)
  let inside := z == 0 || z == 1 || z == 2 || z == 4 || z == 8 || z == 15
  let zeroType := if inside then 0 else denominator
  if !s then
    if a then (if inside then 51064 else 0) else zeroType
  else if a then
    if e then zeroType else if z == 0 then 35139 else if inside then denominator else 0
  else if e then (if inside then denominator else 0) else zeroType

def numerator (u v : Coarse) (x y : Fiber) : Nat :=
  let i := min u.val v.val
  let j := max u.val v.val
  let block := Final3840Data.blockIndex[i * 192 + j]?.getD 0
  if block = 0 then baseNumerator u v
  else
    let entry := if u.val ≤ v.val then x.val * 20 + y.val else y.val * 20 + x.val
    ((Final3840Data.blocks[block - 1]?.getD #[])[entry]?).getD 0

def centeredNumerator (u v : Coarse) (x y : Fiber) : Int :=
  (numerator u v x y : Int) - (baseNumerator u v : Int)

def baseTable (u v : Coarse) : ℚ := (baseNumerator u v : ℚ) / denominator

def perturbation (u v : Coarse) (x y : Fiber) : ℚ :=
  (centeredNumerator u v x y : ℚ) / denominator

def table (u v : Vertex) : ℚ := (numerator u.1 v.1 u.2 v.2 : ℚ) / denominator

theorem table_decomposition (u v : Vertex) :
    table u v = baseTable u.1 v.1 + perturbation u.1 v.1 u.2 v.2 := by
  simp only [table, baseTable, perturbation, centeredNumerator, Int.cast_sub, Int.cast_natCast]
  ring

end K4Ramsey.Final3840
