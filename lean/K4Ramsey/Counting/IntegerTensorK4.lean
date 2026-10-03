import K4Ramsey.Counting.TensorK4

namespace K4Ramsey.IntegerTensorK4

open scoped BigOperators

abbrev Kernel (V : Type*) := V → V → ℤ

/-- Six possibly different kernels, in edge order 01,02,03,12,13,23. -/
def sum {V : Type*} [Fintype V] (a b c d e f : Kernel V) : ℤ :=
  ∑ i, ∑ j, ∑ k, ∑ l, a i j * b i k * c i l * d j k * e j l * f k l

def colorSum {V : Type*} [Fintype V] (w : Kernel V) : ℤ := sum w w w w w w

def transpose {V : Type*} (a : Kernel V) : Kernel V := fun i j => a j i

theorem swap01 {V : Type*} [Fintype V] (a b c d e f : Kernel V) :
    sum a b c d e f = sum (transpose a) d e b c f := by
  unfold sum
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro j _
  apply Finset.sum_congr rfl
  intro i _
  apply Finset.sum_congr rfl
  intro k _
  apply Finset.sum_congr rfl
  intro l _
  simp only [transpose]
  ring

theorem swap12 {V : Type*} [Fintype V] (a b c d e f : Kernel V) :
    sum a b c d e f = sum b a c (transpose d) f e := by
  unfold sum
  apply Finset.sum_congr rfl
  intro i _
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro k _
  apply Finset.sum_congr rfl
  intro j _
  apply Finset.sum_congr rfl
  intro l _
  simp only [transpose]
  ring

theorem swap23 {V : Type*} [Fintype V] (a b c d e f : Kernel V) :
    sum a b c d e f = sum a c b e d (transpose f) := by
  unfold sum
  apply Finset.sum_congr rfl
  intro i _
  apply Finset.sum_congr rfl
  intro j _
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro l _
  apply Finset.sum_congr rfl
  intro k _
  simp only [transpose]
  ring

theorem symmetric_transpose {V : Type*} {a : Kernel V}
    (ha : ∀ i j, a i j = a j i) : transpose a = a := by
  funext i j
  exact (ha i j).symm

theorem add01 {V : Type*} [Fintype V] (a a' b c d e f : Kernel V) :
    sum (fun i j => a i j + a' i j) b c d e f = sum a b c d e f + sum a' b c d e f := by
  simp [sum, add_mul, Finset.sum_add_distrib]

theorem add02 {V : Type*} [Fintype V] (a b b' c d e f : Kernel V) :
    sum a (fun i j => b i j + b' i j) c d e f = sum a b c d e f + sum a b' c d e f := by
  simp [sum, mul_add, add_mul, Finset.sum_add_distrib]

theorem add03 {V : Type*} [Fintype V] (a b c c' d e f : Kernel V) :
    sum a b (fun i j => c i j + c' i j) d e f = sum a b c d e f + sum a b c' d e f := by
  simp [sum, mul_add, add_mul, Finset.sum_add_distrib]

theorem add12 {V : Type*} [Fintype V] (a b c d d' e f : Kernel V) :
    sum a b c (fun i j => d i j + d' i j) e f = sum a b c d e f + sum a b c d' e f := by
  simp [sum, mul_add, add_mul, Finset.sum_add_distrib]

theorem add13 {V : Type*} [Fintype V] (a b c d e e' f : Kernel V) :
    sum a b c d (fun i j => e i j + e' i j) f = sum a b c d e f + sum a b c d e' f := by
  simp [sum, mul_add, add_mul, Finset.sum_add_distrib]

theorem add23 {V : Type*} [Fintype V] (a b c d e f f' : Kernel V) :
    sum a b c d e (fun i j => f i j + f' i j) = sum a b c d e f + sum a b c d e f' := by
  simp [sum, mul_add, add_mul, Finset.sum_add_distrib]

theorem split_prod4 {B L : Type*} [Fintype B] [Fintype L]
    (f : (B × L) → (B × L) → (B × L) → (B × L) → ℤ) :
    (∑ u, ∑ v, ∑ w, ∑ z, f u v w z) =
    ∑ i, ∑ j, ∑ k, ∑ l, ∑ x, ∑ y, ∑ z, ∑ t,
      f (i,x) (j,y) (k,z) (l,t) := by
  simp only [Fintype.sum_prod_type]
  apply Finset.sum_congr rfl
  intro i _
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro j _
  conv_lhs => arg 2; ext x; rw [Finset.sum_comm]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro k _
  conv_lhs => arg 2; ext x; arg 2; ext y; rw [Finset.sum_comm]
  conv_lhs => arg 2; ext x; rw [Finset.sum_comm]
  rw [Finset.sum_comm]

theorem leaf_zero {L : Type*} [Fintype L] (a d e f : Kernel L)
    (ha : ∀ j, ∑ i, a i j = 0) (b c : ℤ) :
    sum a (fun _ _ => b) (fun _ _ => c) d e f = 0 := by
  unfold sum
  rw [Finset.sum_comm]
  apply Finset.sum_eq_zero
  intro j _
  rw [Finset.sum_comm]
  apply Finset.sum_eq_zero
  intro k _
  rw [Finset.sum_comm]
  apply Finset.sum_eq_zero
  intro l _
  simp only [← Finset.sum_mul, ha, zero_mul]

def liftBase {B L : Type*} (w : Kernel B) : Kernel (B × L) :=
  fun u v => w u.1 v.1

/-- A perturbation leaf vanishes after averaging its fine label, even when
all other vertices and kernels are arbitrary. -/
theorem centered_leaf_zero {B L : Type*} [Fintype B] [Fintype L]
    (a d e f : Kernel (B × L))
    (ha : ∀ i j y, ∑ x : L, a (i,x) (j,y) = 0) (b c : Kernel B) :
    sum a (liftBase b) (liftBase c) d e f = 0 := by
  unfold sum
  rw [split_prod4]
  apply Finset.sum_eq_zero
  intro i _
  apply Finset.sum_eq_zero
  intro j _
  apply Finset.sum_eq_zero
  intro k _
  apply Finset.sum_eq_zero
  intro l _
  exact leaf_zero (fun x y => a (i,x) (j,y))
    (fun y z => d (j,y) (k,z)) (fun y t => e (j,y) (l,t))
    (fun z t => f (k,z) (l,t)) (ha i j) (b i k) (c i l)

/-- A two-edge contraction; its value can be cached independently of the
other two vertices. -/
def path {L : Type*} [Fintype L] (b d : Kernel L) (i j : L) : ℤ :=
  ∑ k, b i k * d j k

/-- Exact factorization of the diamond term. The cycle is the special case
where `a` is constant. This reduces four fine-label sums to two cached paths. -/
theorem diamond_contraction {L : Type*} [Fintype L]
    (a b c d e : Kernel L) (f : ℤ) :
    sum a b c d e (fun _ _ => f) =
      f * ∑ i, ∑ j, a i j * path b d i j * path c e i j := by
  simp only [sum, path, Finset.mul_sum, Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro i _
  apply Finset.sum_congr rfl
  intro j _
  conv_lhs => rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro k _
  apply Finset.sum_congr rfl
  intro l _
  ring

end K4Ramsey.IntegerTensorK4
