import K4Ramsey.Constructions.Final3840.Model
import K4Ramsey.Counting.IntegerTensorK4

namespace K4Ramsey.Final3840.Count
open scoped BigOperators

/-- Pure Lean tabulation, with its lookup correctness proved below. -/
def memo {n : Nat} {α : Type} (f : Fin n → α) : Fin n → α :=
  let a := Array.ofFn f
  fun i => a[i.val]'(by simpa [a] using i.isLt)

@[simp] theorem memo_apply {n : Nat} {α : Type} (f : Fin n → α) (i : Fin n) :
    memo f i = f i := by simp [memo]

abbrev Tab (n : Nat) (α : Type) := {a : Array α // a.size = n}

/-- A 20-by-20 integer block between two coarse vertices. -/
abbrev FiberMatrix := Tab 20 (Tab 20 Int)
/-- A value indexed by an ordered pair of the 192 coarse vertices. -/
abbrev CoarsePairTable (α : Type) := Tab 192 (Tab 192 α)
/-- Sparse path contractions, indexed by two endpoints and one middle block. -/
abbrev PathCache := CoarsePairTable (Tab 192 (Option FiberMatrix))

def tabulate {n : Nat} {α : Type} (f : Fin n → α) : Tab n α :=
  ⟨Array.ofFn f, by simp⟩
def lookup {n : Nat} {α : Type} (a : Tab n α) (i : Fin n) : α :=
  a.val[i.val]'(by rw [a.property]; exact i.isLt)
@[simp] theorem lookup_tabulate {n : Nat} {α : Type} (f : Fin n → α) (i : Fin n) :
    lookup (tabulate f) i = f i := by simp [lookup, tabulate]

def bCache : CoarsePairTable Int := tabulate (fun i => tabulate (fun j => baseNumerator i j))
/-- The mathematical base matrix `b`, read from its tabulation. -/
def b (i j : Coarse) : Int := lookup (lookup bCache i) j
def dCache : CoarsePairTable FiberMatrix :=
  tabulate (fun i => tabulate (fun j => tabulate (fun x => tabulate (fun y => centeredNumerator i j x y))))
/-- The centered perturbation matrix `d`, read from its tabulation. -/
def d (i j : Coarse) (x y : Fiber) : Int :=
  lookup (lookup (lookup (lookup dCache i) j) x) y

def support (i j : Coarse) : Bool := baseNumerator i j != 0 && baseNumerator i j != denominator

def baseRoot (i : Coarse) : Int :=
  ∑ j : Coarse, ∑ k : Coarse, ∑ l : Coarse,
    (b i j * b i k * b i l * b j k * b j l * b k l +
    (65536 - b i j) * (65536 - b i k) * (65536 - b i l) *
    (65536 - b j k) * (65536 - b j l) * (65536 - b k l))

def pathsCache : PathCache :=
  tabulate (fun i => tabulate (fun j => tabulate (fun k =>
    if support i k && support j k then
      some (tabulate (fun x => tabulate (fun y => ∑ z : Fiber, d i k x z * d j k y z)))
    else none)))

def paths (i j k : Coarse) (x y : Fiber) : Int :=
  match lookup (lookup (lookup pathsCache i) j) k with
  | some a => lookup (lookup a x) y
  | none => 0

def triangle (i j k : Coarse) : Int :=
  ∑ x : Fiber, ∑ y : Fiber, d i j x y * paths i j k x y

def cycle (i j k l : Coarse) : Int :=
  ∑ x : Fiber, ∑ y : Fiber, paths i j k x y * paths i j l x y

def diamond (i j k l : Coarse) : Int :=
  ∑ x : Fiber, ∑ y : Fiber, d i j x y * paths i j k x y * paths i j l x y

def tetrahedron (i j k l : Coarse) : Int :=
  ∑ x : Fiber, ∑ y : Fiber, ∑ z : Fiber, ∑ t : Fiber,
    d i j x y * d i k x z * d i l x t * d j k y z * d j l y t * d k l z t

/-- Combined red-plus-blue coefficient of the triangle contribution. -/
def triangleCoefficient (i j k : Coarse) : Int :=
  ∑ l : Coarse, (b i l * b j l * b k l -
    (65536 - b i l) * (65536 - b j l) * (65536 - b k l))

def triangleAt (i : Coarse) : Int :=
  20 * ∑ j : Coarse, if support i j then
    ∑ k : Coarse, if support i k && support j k then
      triangleCoefficient i j k * triangle i j k else 0 else 0

def cycleAt (i : Coarse) : Int :=
  ∑ j : Coarse, ∑ k : Coarse,
    if support i k && support j k then
      ∑ l : Coarse, if support i l && support j l then
        (b i j * b k l + (65536 - b i j) * (65536 - b k l)) * cycle i j k l
      else 0
    else 0

def diamondAt (i : Coarse) : Int :=
  ∑ j : Coarse, if support i j then
    ∑ k : Coarse, if support i k && support j k then
      ∑ l : Coarse, if support i l && support j l then
        (2 * b k l - 65536) * diamond i j k l else 0 else 0 else 0

def tetrahedronAt (i : Coarse) : Int :=
  2 * ∑ j : Coarse, if support i j then
    ∑ k : Coarse, if support i k && support j k then
      ∑ l : Coarse, if support i l && support j l && support k l then
        tetrahedron i j k l else 0 else 0 else 0

end K4Ramsey.Final3840.Count
