
/-!
Vendor note: the meta-math original imports `SixBirdsMetaMath.Terminology`.
That import is intentionally dropped here rather than rewritten because
`Terminology.lean` pulls in the unvendored `ImportedFoundations` and
`FoundationsICompat` dependency chain, which is outside this vendoring unit.
The import is unused in this file: there is no `Terminology`-qualified
reference in the body, and `Terminology.lean` declares no notation or instances
that could apply implicitly.
-/

namespace SixBirdsMetaMath.Main.LegalQuotient

/-!
Main paper §2 "Legal quotient and native currency".

This module uses a concrete finite-dimensional rational model.  Vectors
are functions on `Fin n`, matrices are rational-valued rectangular
arrays, adjoints are transposes, and the local Moore-Penrose operation is
the diagonal-support inverse.  The labeled declarations below therefore
compute the paper's packaged currency from `C`, `Γ`, and `L`; the
capacity and minimum-spend statements no longer receive their
conclusions as hypotheses.
-/

/-- Rational finite-dimensional column vectors. -/
def Vec (n : Nat) : Type :=
  Fin n → Rat

/-- Rational finite-dimensional matrices, with row count first. -/
def Mat (m n : Nat) : Type :=
  Fin m → Fin n → Rat

/-- A finite sum over `Fin n`, implemented by direct recursion on `Fin`. -/
def sumFin : (n : Nat) → (Fin n → Rat) → Rat
  | 0, _ => 0
  | n + 1, f => sumFin n (fun i => f i.castSucc) + f (Fin.last n)

/-- `sumFin` sends the zero function to zero. -/
theorem sumFin_zero (n : Nat) : sumFin n (fun _ => (0 : Rat)) = 0 := by
  induction n with
  | zero => rfl
  | succ n ih =>
      rw [sumFin, ih]
      exact Rat.add_zero 0

/-- Sum distributes over pointwise addition. -/
theorem sumFin_add (n : Nat) (f g : Fin n → Rat) :
    sumFin n (fun i => f i + g i) = sumFin n f + sumFin n g := by
  induction n with
  | zero =>
      rw [sumFin, sumFin, sumFin]
      exact (Rat.add_zero 0).symm
  | succ n ih =>
      rw [sumFin, sumFin, sumFin, ih]
      grind [Rat.add_assoc, Rat.add_comm, Rat.add_left_comm]

/-- A scalar may be factored out on the left of a finite sum. -/
theorem sumFin_mul_left (n : Nat) (c : Rat) (f : Fin n → Rat) :
    sumFin n (fun i => c * f i) = c * sumFin n f := by
  induction n with
  | zero =>
      rw [sumFin, sumFin, Rat.mul_zero]
  | succ n ih =>
      rw [sumFin, sumFin, ih, Rat.mul_add]

/-- A scalar may be factored out on the right of a finite sum. -/
theorem sumFin_mul_right (n : Nat) (c : Rat) (f : Fin n → Rat) :
    sumFin n (fun i => f i * c) = sumFin n f * c := by
  induction n with
  | zero =>
      rw [sumFin, sumFin, Rat.zero_mul]
  | succ n ih =>
      rw [sumFin, sumFin, ih, Rat.add_mul]

/-- Finite double sums may be interchanged. -/
theorem sumFin_comm (m n : Nat) (f : Fin m → Fin n → Rat) :
    sumFin m (fun i => sumFin n (fun j => f i j)) =
      sumFin n (fun j => sumFin m (fun i => f i j)) := by
  induction m with
  | zero =>
      rw [sumFin]
      symm
      exact sumFin_zero n
  | succ m ih =>
      rw [sumFin]
      rw [ih]
      rw [
        show
          (sumFin n fun j => sumFin (m + 1) fun i => f i j) =
            sumFin n
              (fun j => sumFin m (fun i => f i.castSucc j) + f (Fin.last m) j) by
            rfl]
      rw [sumFin_add]

/-- A `sumFin` with one possible nonzero term equals that term. -/
theorem sumFin_eq_single {n : Nat} (t : Fin n) (f : Fin n → Rat)
    (hzero : ∀ k, k ≠ t → f k = 0) : sumFin n f = f t := by
  induction n with
  | zero => exact Fin.elim0 t
  | succ n ih =>
      rw [sumFin]
      by_cases htlast : t = Fin.last n
      · rw [htlast]
        have hfun : (fun i : Fin n => f i.castSucc) = (fun _ => (0 : Rat)) := by
          funext i
          exact hzero i.castSucc
            (by
              intro h
              have hv : i.val = n := by
                have hv0 := congrArg Fin.val (h.trans htlast)
                simpa using hv0
              omega)
        have hleft : sumFin n (fun i => f i.castSucc) = 0 := by
          rw [hfun]
          exact sumFin_zero n
        rw [hleft]
        exact Rat.zero_add (f (Fin.last n))
      · have hval : t.val < n := by
          have htlt := t.isLt
          have hne : t.val ≠ n := by
            intro hv
            apply htlast
            exact Fin.ext hv
          omega
        let t' : Fin n := ⟨t.val, hval⟩
        have htcast : t'.castSucc = t := by
          apply Fin.ext
          rfl
        have hleft : sumFin n (fun i => f i.castSucc) = f t := by
          calc
            sumFin n (fun i => f i.castSucc) = f t'.castSucc := by
              exact ih t' (fun i => f i.castSucc)
                (fun i hi =>
                  hzero i.castSucc
                    (by
                      intro h
                      apply hi
                      exact Fin.ext (by simpa [t'] using congrArg Fin.val h)))
            _ = f t := by rw [htcast]
        rw [hleft]
        rw [hzero (Fin.last n) (by intro h; exact htlast h.symm)]
        exact Rat.add_zero (f t)

/-- Double negation for rational numbers. -/
theorem rat_neg_neg (x : Rat) : - - x = x := by
  apply Rat.ext
  · simp [Rat.neg_num, Int.neg_neg]
  · simp [Rat.neg_den]

/-- A rational square is nonnegative. -/
theorem rat_mul_self_nonneg (x : Rat) : 0 ≤ x * x := by
  cases Rat.nonneg_total x with
  | inl hx =>
      exact Rat.mul_nonneg hx hx
  | inr hnx =>
      have hsq : 0 ≤ (-x) * (-x) := Rat.mul_nonneg hnx hnx
      have hsq' : 0 ≤ - (-(x * x)) := by
        rw [← Rat.neg_mul]
        rw [← Rat.mul_neg]
        exact hsq
      rw [rat_neg_neg] at hsq'
      exact hsq'

/-- Nonnegative scaling preserves rational order. -/
theorem rat_mul_mono_nonneg (a b c : Rat) : 0 ≤ a → b ≤ c → a * b ≤ a * c := by
  intro ha hbc
  exact Rat.mul_le_mul_of_nonneg_left hbc ha

/-- Addition preserves rational order in both inputs. -/
theorem rat_add_le_add (a b c d : Rat) (hab : a ≤ b) (hcd : c ≤ d) :
    a + c ≤ b + d := by
  rw [Rat.le_iff_sub_nonneg] at hab hcd ⊢
  have hsum : 0 ≤ (b - a) + (d - c) := Rat.add_nonneg hab hcd
  have heq : b + d - (a + c) = (b - a) + (d - c) := by
    grind [Rat.sub_eq_add_neg, Rat.add_assoc, Rat.add_comm, Rat.add_left_comm]
  rw [heq]
  exact hsum

/-- A nonnegative rational sum equal to zero has zero left summand. -/
theorem rat_add_eq_zero_left_of_nonneg (a b : Rat) (ha : 0 ≤ a) (hb : 0 ≤ b)
    (h : a + b = 0) : a = 0 := by
  apply Rat.nonneg_antisymm ha
  have hb_eq : b = -a := by
    calc
      b = 0 + b := by rw [Rat.zero_add]
      _ = (-a + a) + b := by rw [Rat.neg_add_cancel]
      _ = -a + (a + b) := by rw [Rat.add_assoc]
      _ = -a + 0 := by rw [h]
      _ = -a := by rw [Rat.add_zero]
  rw [← hb_eq]
  exact hb

/-- A nonnegative rational sum equal to zero has zero right summand. -/
theorem rat_add_eq_zero_right_of_nonneg (a b : Rat) (ha : 0 ≤ a) (hb : 0 ≤ b)
    (h : a + b = 0) : b = 0 := by
  apply rat_add_eq_zero_left_of_nonneg b a hb ha
  rw [Rat.add_comm]
  exact h

/-- A nonpositive rational becomes nonnegative after negation. -/
theorem rat_neg_nonneg_of_nonpos (x : Rat) (hx : x ≤ 0) : 0 ≤ -x := by
  rw [Rat.le_iff_sub_nonneg] at hx
  have heq : 0 - x = -x := by
    grind [Rat.sub_eq_add_neg, Rat.zero_add]
  rw [heq] at hx
  exact hx

/-- A nonnegative rational becomes nonpositive after negation. -/
theorem rat_neg_nonpos_of_nonneg (x : Rat) (hx : 0 ≤ x) : -x ≤ 0 := by
  rw [Rat.le_iff_sub_nonneg]
  have heq : 0 - (-x) = x := by
    grind [Rat.sub_eq_add_neg, Rat.zero_add, Rat.neg_add_cancel, Rat.add_neg_cancel]
  rw [heq]
  exact hx

/-- A finite sum of nonnegative terms is nonnegative. -/
theorem sumFin_nonneg {n : Nat} (f : Fin n → Rat) (hf : ∀ i, 0 ≤ f i) :
    0 ≤ sumFin n f := by
  induction n with
  | zero =>
      rw [sumFin]
      exact (Rat.le_refl : (0 : Rat) ≤ 0)
  | succ n ih =>
      rw [sumFin]
      exact Rat.add_nonneg
        (ih (fun i => f i.castSucc) (fun i => hf i.castSucc))
        (hf (Fin.last n))

/-- Pointwise rational order lifts to finite sums. -/
theorem sumFin_mono {n : Nat} (f g : Fin n → Rat) (hfg : ∀ i, f i ≤ g i) :
    sumFin n f ≤ sumFin n g := by
  induction n with
  | zero =>
      rw [sumFin, sumFin]
      exact (Rat.le_refl : (0 : Rat) ≤ 0)
  | succ n ih =>
      rw [sumFin, sumFin]
      exact rat_add_le_add
        (sumFin n (fun i => f i.castSucc))
        (sumFin n (fun i => g i.castSucc))
        (f (Fin.last n))
        (g (Fin.last n))
        (ih (fun i => f i.castSucc) (fun i => g i.castSucc) (fun i => hfg i.castSucc))
        (hfg (Fin.last n))

/-- A finite sum of nonnegative terms equals zero iff every term equals zero. -/
theorem sumFin_eq_zero_of_nonneg {n : Nat} (f : Fin n → Rat) (hf : ∀ i, 0 ≤ f i) :
    sumFin n f = 0 ↔ ∀ i, f i = 0 := by
  induction n with
  | zero =>
      constructor
      · intro _ i
        exact Fin.elim0 i
      · intro _
        rfl
  | succ n ih =>
      constructor
      · intro h i
        rw [sumFin] at h
        have hleft_nonneg : 0 ≤ sumFin n (fun i => f i.castSucc) :=
          sumFin_nonneg (fun i => f i.castSucc) (fun i => hf i.castSucc)
        have hleft_zero : sumFin n (fun i => f i.castSucc) = 0 :=
          rat_add_eq_zero_left_of_nonneg _ _ hleft_nonneg (hf (Fin.last n)) h
        have hlast_zero : f (Fin.last n) = 0 :=
          rat_add_eq_zero_right_of_nonneg _ _ hleft_nonneg (hf (Fin.last n)) h
        by_cases hi : i = Fin.last n
        · rw [hi]
          exact hlast_zero
        · have hival : i.val < n := by
            have hlt := i.isLt
            have hne : i.val ≠ n := by
              intro hv
              apply hi
              exact Fin.ext hv
            omega
          let i' : Fin n := ⟨i.val, hival⟩
          have hcast : i'.castSucc = i := by
            apply Fin.ext
            rfl
          have hall := (ih (fun i => f i.castSucc) (fun i => hf i.castSucc)).mp hleft_zero
          rw [← hcast]
          exact hall i'
      · intro h
        rw [sumFin]
        have hleft : sumFin n (fun i => f i.castSucc) = 0 :=
          (ih (fun i => f i.castSucc) (fun i => hf i.castSucc)).mpr (fun i => h i.castSucc)
        rw [hleft, h (Fin.last n)]
        exact Rat.add_zero 0

/-- Matrix-vector product. -/
def matVec {m n : Nat} (M : Mat m n) (v : Vec n) : Vec m :=
  fun i => sumFin n (fun j => M i j * v j)

/-- Trace of a square matrix, as the finite sum of diagonal entries. -/
def traceMat {n : Nat} (M : Mat n n) : Rat :=
  sumFin n (fun i => M i i)

/-- Matrix-matrix product. -/
def matMul {m n p : Nat} (A : Mat m n) (B : Mat n p) : Mat m p :=
  fun i k => sumFin n (fun j => A i j * B j k)

/-- Matrix-vector multiplication composes with matrix multiplication. -/
theorem matVec_matMul {m n p : Nat} (A : Mat m n) (B : Mat n p) (v : Vec p) :
    matVec (matMul A B) v = matVec A (matVec B v) := by
  funext i
  unfold matVec matMul
  rw [
    show
      sumFin p (fun k => sumFin n (fun j => A i j * B j k) * v k) =
        sumFin p (fun k => sumFin n (fun j => (A i j * B j k) * v k)) by
        apply congrArg
        funext k
        rw [sumFin_mul_right]]
  rw [
    show
      sumFin p (fun k => sumFin n (fun j => (A i j * B j k) * v k)) =
        sumFin p (fun k => sumFin n (fun j => A i j * (B j k * v k))) by
        apply congrArg
        funext k
        apply congrArg
        funext j
        rw [Rat.mul_assoc]]
  rw [sumFin_comm]
  apply congrArg
  funext j
  rw [← sumFin_mul_left]

/-- Matrix transpose, the finite-dimensional adjoint used here. -/
def transpose {m n : Nat} (M : Mat m n) : Mat n m :=
  fun i j => M j i

/-- Matrix subtraction. -/
def matSub {m n : Nat} (A B : Mat m n) : Mat m n :=
  fun i j => A i j - B i j

/-- Matrix addition. -/
def matAdd {m n : Nat} (A B : Mat m n) : Mat m n :=
  fun i j => A i j + B i j

/-- Zero matrix. -/
def zeroMat (m n : Nat) : Mat m n :=
  fun _ _ => 0

/-- Trace of the zero matrix is zero. -/
theorem traceMat_zeroMat {n : Nat} : traceMat (zeroMat n n) = 0 := by
  unfold traceMat zeroMat
  exact sumFin_zero n

/-- Scalar multiplication of a matrix. -/
def matScale {m n : Nat} (r : Rat) (M : Mat m n) : Mat m n :=
  fun i j => r * M i j

/-- Identity matrix. -/
def identityMat (n : Nat) : Mat n n :=
  fun i j => if i = j then 1 else 0

/-- Standard basis vector at coordinate `i`. -/
def standardBasis {n : Nat} (i : Fin n) : Vec n :=
  fun j => if j = i then 1 else 0

/-- Zero is neutral for matrix addition on the right. -/
theorem matAdd_zero_right {m n : Nat} (A : Mat m n) :
    matAdd A (zeroMat m n) = A := by
  funext i j
  unfold matAdd zeroMat
  exact Rat.add_zero (A i j)

/-- Scaling a matrix by one is neutral. -/
theorem matScale_one {m n : Nat} (A : Mat m n) :
    matScale 1 A = A := by
  funext i j
  unfold matScale
  exact Rat.one_mul (A i j)

/-- Matrix-vector product by the zero matrix is the zero vector. -/
theorem matVec_zeroMat {m n : Nat} (v : Vec n) :
    matVec (zeroMat m n) v = (fun _ => (0 : Rat)) := by
  funext i
  unfold matVec zeroMat
  rw [show sumFin n (fun j => (0 : Rat) * v j) = sumFin n (fun _ => (0 : Rat)) by
    apply congrArg
    funext j
    exact Rat.zero_mul (v j)]
  exact sumFin_zero n

/-- `matVec` applied to the constant-zero vector is the constant-zero vector. -/
theorem matVec_zero_input {m n : Nat} (A : Mat m n) :
    matVec A (fun _ => (0 : Rat)) = (fun _ => 0) := by
  funext i
  unfold matVec
  rw [show sumFin n (fun j => A i j * (0 : Rat)) = sumFin n (fun _ => (0 : Rat)) by
    apply congrArg
    funext j
    exact Rat.mul_zero (A i j)]
  exact sumFin_zero n

/-- Matrix-vector product distributes over matrix addition. -/
theorem matVec_add {m n : Nat} (A B : Mat m n) (v : Vec n) :
    matVec (matAdd A B) v = fun i => matVec A v i + matVec B v i := by
  funext i
  unfold matVec matAdd
  rw [
    show sumFin n (fun j => (A i j + B i j) * v j) =
        sumFin n (fun j => A i j * v j + B i j * v j) by
      apply congrArg
      funext j
      rw [Rat.add_mul]]
  rw [sumFin_add]

/-- Matrix-vector product respects matrix scaling. -/
theorem matVec_scale {m n : Nat} (r : Rat) (A : Mat m n) (v : Vec n) :
    matVec (matScale r A) v = fun i => r * matVec A v i := by
  funext i
  unfold matVec matScale
  rw [
    show sumFin n (fun j => r * A i j * v j) =
        sumFin n (fun j => r * (A i j * v j)) by
      apply congrArg
      funext j
      rw [Rat.mul_assoc]]
  rw [sumFin_mul_left]

/-- Finite sums distribute over subtraction. -/
theorem sumFin_sub (n : Nat) (f g : Fin n → Rat) :
    sumFin n (fun i => f i - g i) = sumFin n f - sumFin n g := by
  induction n with
  | zero =>
      rw [sumFin, sumFin, sumFin]
      grind
  | succ n ih =>
      rw [sumFin, sumFin, sumFin, ih]
      grind

/-- Trace is additive over matrix subtraction. -/
theorem traceMat_sub {n : Nat} (A B : Mat n n) :
    traceMat (matSub A B) = traceMat A - traceMat B := by
  unfold traceMat matSub
  exact sumFin_sub n (fun i => A i i) (fun i => B i i)

/-- Trace is additive over matrix addition. -/
theorem traceMat_add {n : Nat} (A B : Mat n n) :
    traceMat (matAdd A B) = traceMat A + traceMat B := by
  unfold traceMat matAdd
  exact sumFin_add n (fun i => A i i) (fun i => B i i)

/-- Trace pulls scalars out of matrix scaling. -/
theorem traceMat_scale {n : Nat} (r : Rat) (M : Mat n n) :
    traceMat (matScale r M) = r * traceMat M := by
  unfold traceMat matScale
  rw [← sumFin_mul_left]

/-- Matrix-vector product distributes over matrix subtraction. -/
theorem matVec_sub {m n : Nat} (A B : Mat m n) (v : Vec n) :
    matVec (matSub A B) v = fun i => matVec A v i - matVec B v i := by
  funext i
  unfold matVec matSub
  rw [
    show sumFin n (fun j => (A i j - B i j) * v j) =
        sumFin n (fun j => A i j * v j - B i j * v j) by
      apply congrArg
      funext j
      grind]
  rw [sumFin_sub]

/-- Matrix multiplication is associative for the local finite matrix model. -/
theorem matMul_assoc {l m n p : Nat}
    (A : Mat l m) (B : Mat m n) (C : Mat n p) :
    matMul (matMul A B) C = matMul A (matMul B C) := by
  funext i k
  unfold matMul
  rw [
    show
      sumFin n (fun j => sumFin m (fun h => A i h * B h j) * C j k) =
        sumFin n (fun j => sumFin m (fun h => (A i h * B h j) * C j k)) by
        apply congrArg
        funext j
        rw [sumFin_mul_right]]
  rw [
    show
      sumFin n (fun j => sumFin m (fun h => (A i h * B h j) * C j k)) =
        sumFin n (fun j => sumFin m (fun h => A i h * (B h j * C j k))) by
        apply congrArg
        funext j
        apply congrArg
        funext h
        rw [Rat.mul_assoc]]
  rw [sumFin_comm]
  apply congrArg
  funext h
  rw [← sumFin_mul_left]

/-- Right multiplication by the identity matrix is neutral. -/
theorem matMul_identity_right {m n : Nat} (A : Mat m n) :
    matMul A (identityMat n) = A := by
  funext i k
  unfold matMul identityMat
  rw [sumFin_eq_single k]
  · simp
  · intro j hjk
    simp [hjk, Rat.mul_zero]

/-- Matrix multiplication distributes over subtraction in the right input. -/
theorem matMul_sub_right {m n p : Nat}
    (A : Mat m n) (B C : Mat n p) :
    matMul A (matSub B C) = matSub (matMul A B) (matMul A C) := by
  funext i k
  unfold matMul matSub
  rw [
    show sumFin n (fun j => A i j * (B j k - C j k)) =
        sumFin n (fun j => A i j * B j k - A i j * C j k) by
      apply congrArg
      funext j
      grind]
  rw [sumFin_sub]

/-- Matrix multiplication distributes over subtraction in the left input. -/
theorem matMul_sub_left {m n p : Nat}
    (A B : Mat m n) (C : Mat n p) :
    matMul (matSub A B) C = matSub (matMul A C) (matMul B C) := by
  funext i k
  unfold matMul matSub
  rw [
    show sumFin n (fun j => (A i j - B i j) * C j k) =
        sumFin n (fun j => A i j * C j k - B i j * C j k) by
      apply congrArg
      funext j
      grind]
  rw [sumFin_sub]

/-- Left multiplication by a zero matrix gives a zero matrix. -/
theorem matMul_zero_left {m n k : Nat} (A : Mat n k) :
    matMul (zeroMat m n) A = zeroMat m k := by
  funext i j
  unfold matMul zeroMat
  rw [show sumFin n (fun h => (0 : Rat) * A h j) = sumFin n (fun _ => (0 : Rat)) by
    apply congrArg
    funext h
    exact Rat.zero_mul (A h j)]
  exact sumFin_zero n

/-- Right multiplication by a zero matrix gives a zero matrix. -/
theorem matMul_zero_right {m n k : Nat} (A : Mat m n) :
    matMul A (zeroMat n k) = zeroMat m k := by
  funext i j
  unfold matMul zeroMat
  rw [show sumFin n (fun h => A i h * (0 : Rat)) = sumFin n (fun _ => (0 : Rat)) by
    apply congrArg
    funext h
    exact Rat.mul_zero (A i h)]
  exact sumFin_zero n

/-- Transpose reverses matrix multiplication. -/
theorem transpose_matMul {m n p : Nat} (A : Mat m n) (B : Mat n p) :
    transpose (matMul A B) = matMul (transpose B) (transpose A) := by
  funext i k
  unfold transpose matMul
  apply congrArg
  funext j
  rw [Rat.mul_comm]

/-- Transposing twice returns the original matrix. -/
theorem transpose_transpose {m n : Nat} (A : Mat m n) :
    transpose (transpose A) = A := by
  funext i j
  rfl

/-- Addition cancels a matching subtraction on the right. -/
theorem matAdd_sub_cancel {m n : Nat} (A B : Mat m n) :
    matAdd B (matSub A B) = A := by
  funext i j
  unfold matAdd matSub
  grind

/-- Identity matrix acts as identity on vectors. -/
theorem matVec_identity {n : Nat} (v : Vec n) :
    matVec (identityMat n) v = v := by
  funext i
  unfold matVec identityMat
  rw [sumFin_eq_single i]
  · simp
  · intro j hji
    have hij : i ≠ j := fun h => hji h.symm
    simp [hij, Rat.zero_mul]

/-- Dot product of rational vectors. -/
def dot {n : Nat} (u v : Vec n) : Rat :=
  sumFin n (fun i => u i * v i)

/-- Dot product distributes over addition in the right input. -/
theorem dot_add_right {n : Nat} (u v w : Vec n) :
    dot u (fun i => v i + w i) = dot u v + dot u w := by
  unfold dot
  rw [
    show sumFin n (fun i => u i * (v i + w i)) =
        sumFin n (fun i => u i * v i + u i * w i) by
      apply congrArg
      funext i
      rw [Rat.mul_add]]
  rw [sumFin_add]

/-- Dot product distributes over subtraction in the right input. -/
theorem dot_sub_right {n : Nat} (u v w : Vec n) :
    dot u (fun i => v i - w i) = dot u v - dot u w := by
  unfold dot
  rw [
    show sumFin n (fun i => u i * (v i - w i)) =
        sumFin n (fun i => u i * v i - u i * w i) by
      apply congrArg
      funext i
      grind]
  rw [sumFin_sub]

/-- Dot product respects scaling in the right input. -/
theorem dot_scale_right {n : Nat} (r : Rat) (u v : Vec n) :
    dot u (fun i => r * v i) = r * dot u v := by
  unfold dot
  rw [
    show sumFin n (fun i => u i * (r * v i)) =
        sumFin n (fun i => r * (u i * v i)) by
      apply congrArg
      funext i
      grind [Rat.mul_assoc, Rat.mul_comm]]
  rw [sumFin_mul_left]

/-- Squared norm via dot is nonnegative. -/
theorem dot_self_nonneg {n : Nat} (v : Vec n) : 0 ≤ dot v v := by
  unfold dot
  exact sumFin_nonneg (fun i => v i * v i) (fun i => rat_mul_self_nonneg (v i))

/-- Squared norm via dot vanishes iff the vector is zero. -/
theorem dot_self_eq_zero {n : Nat} (v : Vec n) :
    dot v v = 0 ↔ v = (fun _ => 0) := by
  constructor
  · intro h
    funext i
    have hall :
        ∀ i, v i * v i = 0 :=
      (sumFin_eq_zero_of_nonneg (fun i => v i * v i)
        (fun i => rat_mul_self_nonneg (v i))).mp h
    have hz := (Rat.mul_eq_zero).mp (hall i)
    cases hz with
    | inl hleft => exact hleft
    | inr hright => exact hright
  · intro h
    rw [h]
    unfold dot
    rw [
      show sumFin n (fun i => (fun _ => (0 : Rat)) i * (fun _ => (0 : Rat)) i) =
          sumFin n (fun _ => (0 : Rat)) by
        apply congrArg
        funext i
        exact Rat.zero_mul 0]
    exact sumFin_zero n

/-- Transpose is adjoint for the finite rational dot product. -/
theorem dot_matVec_transpose {m n : Nat} (A : Mat m n) (u : Vec m) (v : Vec n) :
    dot (matVec (transpose A) u) v = dot u (matVec A v) := by
  unfold dot matVec transpose
  rw [
    show
      sumFin n (fun j => sumFin m (fun i => A i j * u i) * v j) =
        sumFin n (fun j => sumFin m (fun i => (A i j * u i) * v j)) by
        apply congrArg
        funext j
        rw [sumFin_mul_right]]
  rw [
    show
      sumFin n (fun j => sumFin m (fun i => (A i j * u i) * v j)) =
        sumFin n (fun j => sumFin m (fun i => u i * (A i j * v j))) by
        apply congrArg
        funext j
        apply congrArg
        funext i
        grind [Rat.mul_assoc, Rat.mul_comm]]
  rw [sumFin_comm]
  apply congrArg
  funext i
  rw [← sumFin_mul_left]

/-- Quadratic form `v^T M v`. -/
def quad {n : Nat} (M : Mat n n) (v : Vec n) : Rat :=
  dot v (matVec M v)

/-- Matrix-vector product on a standard basis vector selects a column. -/
theorem matVec_standardBasis {n : Nat} (A : Mat n n) (i : Fin n) :
    matVec A (standardBasis i) = fun k => A k i := by
  funext k
  unfold matVec standardBasis
  rw [sumFin_eq_single i]
  · rw [if_pos rfl]
    exact Rat.mul_one (A k i)
  · intro j hji
    rw [if_neg hji]
    exact Rat.mul_zero (A k j)

/-- Quadratic form on a standard basis vector selects the diagonal entry. -/
theorem quad_standardBasis {n : Nat} (A : Mat n n) (i : Fin n) :
    quad A (standardBasis i) = A i i := by
  unfold quad
  rw [matVec_standardBasis]
  unfold dot standardBasis
  rw [sumFin_eq_single i]
  · rw [if_pos rfl]
    exact Rat.one_mul (A i i)
  · intro j hji
    rw [if_neg hji]
    exact Rat.zero_mul (A j i)

/-- Quadratic forms distribute over matrix addition. -/
theorem quad_add {n : Nat} (A B : Mat n n) (v : Vec n) :
    quad (matAdd A B) v = quad A v + quad B v := by
  unfold quad
  rw [matVec_add]
  rw [dot_add_right]

/-- Quadratic forms respect matrix scaling. -/
theorem quad_scale {n : Nat} (r : Rat) (A : Mat n n) (v : Vec n) :
    quad (matScale r A) v = r * quad A v := by
  unfold quad
  rw [matVec_scale]
  rw [dot_scale_right]

/-- Quadratic form of a congruent matrix. -/
theorem quad_conjugate {m n : Nat} (M : Mat m n) (A : Mat n n) (v : Vec m) :
    quad (matMul (matMul M A) (transpose M)) v = quad A (matVec (transpose M) v) := by
  unfold quad
  calc
    dot v (matVec (matMul (matMul M A) (transpose M)) v) =
        dot v (matVec (matMul M A) (matVec (transpose M) v)) := by
          rw [matVec_matMul]
    _ = dot v (matVec M (matVec A (matVec (transpose M) v))) := by
          rw [matVec_matMul]
    _ = dot (matVec (transpose M) v) (matVec A (matVec (transpose M) v)) := by
          rw [dot_matVec_transpose]

/-- Reversing a matrix subtraction negates the quadratic form. -/
theorem quad_sub_neg {n : Nat} (A B : Mat n n) (v : Vec n) :
    quad (matSub A B) v = - quad (matSub B A) v := by
  unfold quad
  rw [matVec_sub, matVec_sub, dot_sub_right, dot_sub_right]
  grind [Rat.sub_eq_add_neg, Rat.add_assoc, Rat.add_comm, Rat.add_left_comm]

/-- Symmetry predicate for finite matrices. -/
def Symmetric {n : Nat} (M : Mat n n) : Prop :=
  ∀ i j, M i j = M j i

/-- Positive-semidefinite predicate by rational quadratic forms. -/
def PositiveSemidefinite {n : Nat} (M : Mat n n) : Prop :=
  ∀ v, 0 ≤ quad M v

/-- The zero matrix is positive semidefinite. -/
theorem posSemidef_zero {n : Nat} : PositiveSemidefinite (zeroMat n n) := by
  intro v
  unfold quad
  rw [matVec_zeroMat]
  unfold dot
  rw [show sumFin n (fun i => v i * (0 : Rat)) = sumFin n (fun _ => (0 : Rat)) by
    apply congrArg
    funext i
    exact Rat.mul_zero (v i)]
  rw [sumFin_zero]
  exact (Rat.le_refl : (0 : Rat) ≤ 0)

/-- Sum of positive-semidefinite matrices is positive semidefinite. -/
theorem posSemidef_add {n : Nat} (A B : Mat n n) :
    PositiveSemidefinite A → PositiveSemidefinite B →
    PositiveSemidefinite (matAdd A B) := by
  intro hA hB v
  rw [quad_add]
  exact Rat.add_nonneg (hA v) (hB v)

/-- Nonnegative scaling preserves positive semidefiniteness. -/
theorem posSemidef_scale_nonneg {n : Nat} (r : Rat) (A : Mat n n) :
    0 ≤ r → PositiveSemidefinite A → PositiveSemidefinite (matScale r A) := by
  intro hr hA v
  rw [quad_scale]
  exact Rat.mul_nonneg hr (hA v)

/-- Congruence by a matrix preserves positive semidefiniteness. -/
theorem posSemidef_conjugate {m n : Nat} (M : Mat m n) (A : Mat n n) :
    PositiveSemidefinite A →
    PositiveSemidefinite (matMul (matMul M A) (transpose M)) := by
  intro hA v
  rw [quad_conjugate]
  exact hA (matVec (transpose M) v)

/-- A positive-semidefinite matrix has nonnegative trace. -/
theorem psd_trace_nonneg {n : Nat} (A : Mat n n) :
    PositiveSemidefinite A → 0 ≤ traceMat A := by
  intro hA
  unfold traceMat
  exact sumFin_nonneg (fun i => A i i)
    (fun i => by
      have hq : 0 ≤ quad A (standardBasis i) := hA (standardBasis i)
      rw [quad_standardBasis] at hq
      exact hq)

/-- Strict-positive diagonal matrices: positive diagonal and zero off-diagonal. -/
def StrictPositiveDiagonal {n : Nat} (M : Mat n n) : Prop :=
  (∀ i, 0 < M i i) ∧ (∀ i j, i ≠ j → M i j = 0)

/--
Diagonal-support Moore-Penrose inverse.  On the finite-dimensional
diagonal-positive support used by this subsection, nonzero diagonal
entries are inverted and zero modes remain zero.
-/
def diagonalPseudoInverse {n : Nat} (M : Mat n n) : Mat n n :=
  fun i j => if i = j then if M i i = 0 then 0 else (M i i)⁻¹ else 0

/-- The diagonal pseudoinverse is symmetric. -/
theorem transpose_diagonalPseudoInverse {n : Nat} (M : Mat n n) :
    transpose (diagonalPseudoInverse M) = diagonalPseudoInverse M := by
  funext i j
  unfold transpose diagonalPseudoInverse
  by_cases hij : i = j
  · subst hij
    rfl
  · have hji : j ≠ i := fun h => hij h.symm
    simp [hij, hji]

/-- Strict positivity implies nonzero rational diagonal entry. -/
theorem rat_pos_ne_zero (x : Rat) (hx : 0 < x) : x ≠ 0 := by
  exact Rat.ne_of_gt hx

/-- For strict-positive diagonal matrices, the diagonal pseudoinverse is a right inverse. -/
theorem diagonalPseudoInverse_strictPositiveDiagonal_inverse {n : Nat} (M : Mat n n)
    (hM : StrictPositiveDiagonal M) :
    matMul M (diagonalPseudoInverse M) = identityMat n := by
  funext i k
  unfold matMul identityMat
  rw [sumFin_eq_single i]
  · unfold diagonalPseudoInverse
    by_cases hik : i = k
    · subst k
      rw [if_pos rfl]
      rw [if_pos rfl]
      rw [if_neg (rat_pos_ne_zero (M i i) (hM.left i))]
      exact Rat.mul_inv_cancel (M i i) (rat_pos_ne_zero (M i i) (hM.left i))
    · rw [if_neg hik]
      rw [if_neg hik]
      exact Rat.mul_zero (M i i)
  · intro j hji
    rw [hM.right i j (fun h => hji h.symm)]
    exact Rat.zero_mul (diagonalPseudoInverse M j k)

/-- Moore-Penrose equations for the local matrix calculus. -/
def MoorePenroseInverse {n : Nat} (M Mdagger : Mat n n) : Prop :=
  matMul (matMul M Mdagger) M = M ∧
    matMul (matMul Mdagger M) Mdagger = Mdagger ∧
    transpose (matMul M Mdagger) = matMul M Mdagger ∧
    transpose (matMul Mdagger M) = matMul Mdagger M

/-- Null-mode legality: package vectors with zero audit image have zero native image. -/
def NullLegal {a y : Nat} (C_Gamma : Mat a a) (L_Gamma : Mat y a) : Prop :=
  ∀ v, matVec C_Gamma v = (fun _ => 0) → matVec L_Gamma v = (fun _ => 0)

/-- The packaged audit `C_Γ = Γ^T C Γ`. -/
def packagedAudit {e a : Nat} (C : Mat e e) (Gamma : Mat e a) : Mat a a :=
  matMul (matMul (transpose Gamma) C) Gamma

/-- The packaged native probe family `L_Γ = L Γ`. -/
def packagedNative {e a y : Nat} (L : Mat y e) (Gamma : Mat e a) : Mat y a :=
  matMul L Gamma

/--
Packaged native currency
`K_{C,Γ}(L) = L_Γ C_Γ^† L_Γ^T`.

The adjoint `L_Γ^T` and diagonal-support pseudoinverse `C_Γ^†` are
constructed from `L_Γ` and `C_Γ`; they are not parameters.
-/
def packagedCurrency {e a y : Nat}
    (C : Mat e e) (Gamma : Mat e a) (L : Mat y e) : Mat y y :=
  let C_Gamma := packagedAudit C Gamma
  let L_Gamma := packagedNative L Gamma
  matMul (matMul L_Gamma (diagonalPseudoInverse C_Gamma)) (transpose L_Gamma)

/-- The Moore-Penrose optimal direction for the variational capacity problem. -/
def capacityOptimizer {e a y : Nat}
    (C : Mat e e) (Gamma : Mat e a) (L : Mat y e)
    (nativeRecombination : Vec y) : Vec a :=
  let C_Gamma := packagedAudit C Gamma
  let L_Gamma := packagedNative L Gamma
  matVec (diagonalPseudoInverse C_Gamma) (matVec (transpose L_Gamma) nativeRecombination)

/--
Audit energy of the Moore-Penrose optimal direction equals the
packaged-currency quadratic form in the strict-positive diagonal audit
case.
-/
theorem auditOptimalEnergy_eq_currencyQuad {a y : Nat}
    (C_Gamma : Mat a a) (L_Gamma : Mat y a)
    (hDiag : StrictPositiveDiagonal C_Gamma) (nativeRecombination : Vec y) :
    quad C_Gamma
        (matVec (diagonalPseudoInverse C_Gamma)
          (matVec (transpose L_Gamma) nativeRecombination)) =
      quad (matMul (matMul L_Gamma (diagonalPseudoInverse C_Gamma))
        (transpose L_Gamma)) nativeRecombination := by
  let Ddagger := diagonalPseudoInverse C_Gamma
  let w := matVec (transpose L_Gamma) nativeRecombination
  let u := matVec Ddagger w
  have hAuditInverse : matMul C_Gamma Ddagger = identityMat a := by
    unfold Ddagger
    exact diagonalPseudoInverse_strictPositiveDiagonal_inverse C_Gamma hDiag
  have hTransposeDagger : transpose Ddagger = Ddagger := by
    unfold Ddagger
    exact transpose_diagonalPseudoInverse C_Gamma
  have hAuditVec : matVec C_Gamma u = w := by
    calc
      matVec C_Gamma u = matVec C_Gamma (matVec Ddagger w) := rfl
      _ = matVec (matMul C_Gamma Ddagger) w := by
          rw [matVec_matMul]
      _ = matVec (identityMat a) w := by
          rw [hAuditInverse]
      _ = w := matVec_identity w
  calc
    quad C_Gamma
        (matVec (diagonalPseudoInverse C_Gamma)
          (matVec (transpose L_Gamma) nativeRecombination)) =
        dot u (matVec C_Gamma u) := rfl
    _ = dot u w := by
        rw [hAuditVec]
    _ = dot (matVec Ddagger w) w := rfl
    _ = dot (matVec (transpose Ddagger) w) w := by
        rw [hTransposeDagger]
    _ = dot w (matVec Ddagger w) := by
        rw [dot_matVec_transpose]
    _ = dot w (matVec Ddagger (matVec (transpose L_Gamma) nativeRecombination)) := rfl
    _ = dot w (matVec (matMul Ddagger (transpose L_Gamma)) nativeRecombination) := by
        rw [matVec_matMul]
    _ = dot (matVec (transpose L_Gamma) nativeRecombination)
          (matVec (matMul Ddagger (transpose L_Gamma)) nativeRecombination) := rfl
    _ = dot nativeRecombination
          (matVec L_Gamma
            (matVec (matMul Ddagger (transpose L_Gamma)) nativeRecombination)) := by
        rw [dot_matVec_transpose]
    _ = dot nativeRecombination
          (matVec L_Gamma
            (matVec Ddagger (matVec (transpose L_Gamma) nativeRecombination))) := by
        rw [matVec_matMul]
    _ = dot nativeRecombination
          (matVec (matMul L_Gamma Ddagger)
            (matVec (transpose L_Gamma) nativeRecombination)) := by
        rw [← matVec_matMul]
    _ = dot nativeRecombination
          (matVec (matMul (matMul L_Gamma Ddagger) (transpose L_Gamma))
            nativeRecombination) := by
        rw [← matVec_matMul]
    _ = quad (matMul (matMul L_Gamma Ddagger) (transpose L_Gamma))
          nativeRecombination := rfl
    _ = quad (matMul (matMul L_Gamma (diagonalPseudoInverse C_Gamma))
          (transpose L_Gamma)) nativeRecombination := rfl

/--
The finite-dimensional variational capacity evaluated at the
Moore-Penrose optimal direction.  This is not definitionally the
packaged-currency quadratic form; the theorem below identifies them on
the projection support.
-/
def capacity {e a y : Nat}
    (C : Mat e e) (Gamma : Mat e a) (L : Mat y e) (nativeRecombination : Vec y) : Rat :=
  quad (packagedAudit C Gamma)
    (capacityOptimizer C Gamma L nativeRecombination)

/-- Loewner order represented by nonpositivity of all difference quadratic forms. -/
def loewnerLE {y : Nat} (K Theta : Mat y y) : Prop :=
  ∀ nativeRecombination, ¬ 0 < quad (matSub K Theta) nativeRecombination

/-- Subtracting a matrix from itself gives the zero matrix. -/
theorem matSub_self_eq_zero {m n : Nat} (A : Mat m n) :
    matSub A A = zeroMat m n := by
  funext i j
  unfold matSub zeroMat
  grind [Rat.sub_eq_add_neg, Rat.add_neg_cancel]

/-- Subtracting the zero matrix on the right is neutral. -/
theorem matSub_zero_right {m n : Nat} (X : Mat m n) :
    matSub X (zeroMat m n) = X := by
  funext i j
  unfold matSub zeroMat
  grind

/-- Subtracting a difference from its left endpoint returns the right endpoint. -/
theorem matSub_self_matSub {m n : Nat} (X Y : Mat m n) :
    matSub X (matSub X Y) = Y := by
  funext i j
  unfold matSub
  grind [Rat.sub_eq_add_neg, Rat.add_assoc, Rat.add_comm, Rat.add_left_comm]

/-- Consecutive matrix differences telescope under addition. -/
theorem matSub_add_matSub {n : Nat} (A B C : Mat n n) :
    matAdd (matSub B A) (matSub C B) = matSub C A := by
  funext i j
  unfold matAdd matSub
  grind [Rat.sub_eq_add_neg, Rat.add_assoc, Rat.add_comm, Rat.add_left_comm]

/-- Matrix subtraction distributes over paired additions. -/
theorem matSub_matAdd_matAdd {n : Nat} (A B C D : Mat n n) :
    matSub (matAdd B D) (matAdd A C) = matAdd (matSub B A) (matSub D C) := by
  funext i j
  unfold matSub matAdd
  grind [Rat.sub_eq_add_neg, Rat.add_assoc, Rat.add_comm, Rat.add_left_comm]

/-- Matrix subtraction commutes with scalar multiplication. -/
theorem matSub_scale {m n : Nat} (r : Rat) (A B : Mat m n) :
    matSub (matScale r B) (matScale r A) = matScale r (matSub B A) := by
  funext i j
  unfold matSub matScale
  grind [Rat.sub_eq_add_neg, Rat.mul_add, Rat.mul_neg]

/-- Matrix conjugation distributes over subtraction. -/
theorem matSub_matMul_conjugate {m n : Nat} (M : Mat m n) (A B : Mat n n) :
    matMul (matMul M (matSub B A)) (transpose M) =
      matSub (matMul (matMul M B) (transpose M)) (matMul (matMul M A) (transpose M)) := by
  calc
    matMul (matMul M (matSub B A)) (transpose M) =
        matMul (matSub (matMul M B) (matMul M A)) (transpose M) := by
          rw [matMul_sub_right]
    _ = matSub (matMul (matMul M B) (transpose M)) (matMul (matMul M A) (transpose M)) := by
          rw [matMul_sub_left]

/-- Loewner order is equivalent to positive semidefiniteness of the reversed difference. -/
theorem loewnerLE_iff_psd_sub {n : Nat} (K Theta : Mat n n) :
    loewnerLE K Theta ↔ PositiveSemidefinite (matSub Theta K) := by
  constructor
  · intro h v
    have hnonpos : quad (matSub K Theta) v ≤ 0 := (Rat.not_lt).mp (h v)
    have hneg : 0 ≤ -quad (matSub K Theta) v :=
      rat_neg_nonneg_of_nonpos (quad (matSub K Theta) v) hnonpos
    have hquad : quad (matSub Theta K) v = -quad (matSub K Theta) v := by
      exact quad_sub_neg Theta K v
    rw [hquad]
    exact hneg
  · intro h v
    have htheta : 0 ≤ quad (matSub Theta K) v := h v
    have hnonpos : quad (matSub K Theta) v ≤ 0 := by
      have hneg : -quad (matSub Theta K) v ≤ 0 :=
        rat_neg_nonpos_of_nonneg (quad (matSub Theta K) v) htheta
      have hquad : quad (matSub K Theta) v = -quad (matSub Theta K) v := by
        exact quad_sub_neg K Theta v
      rw [hquad]
      exact hneg
    exact (Rat.not_lt).mpr hnonpos

/-- Loewner order is reflexive. -/
theorem loewnerLE_refl {n : Nat} (M : Mat n n) : loewnerLE M M := by
  rw [loewnerLE_iff_psd_sub]
  rw [matSub_self_eq_zero]
  exact posSemidef_zero

/-- Loewner order is transitive. -/
theorem loewnerLE_trans {n : Nat} (A B C : Mat n n) :
    loewnerLE A B → loewnerLE B C → loewnerLE A C := by
  intro hAB hBC
  rw [loewnerLE_iff_psd_sub] at hAB hBC ⊢
  have hsum := posSemidef_add (matSub B A) (matSub C B) hAB hBC
  rw [matSub_add_matSub] at hsum
  exact hsum

/-- Loewner order is monotone under matrix addition. -/
theorem loewnerLE_add_mono {n : Nat} (A B C D : Mat n n) :
    loewnerLE A B → loewnerLE C D →
    loewnerLE (matAdd A C) (matAdd B D) := by
  intro hAB hCD
  rw [loewnerLE_iff_psd_sub] at hAB hCD ⊢
  have hsum := posSemidef_add (matSub B A) (matSub D C) hAB hCD
  rw [matSub_matAdd_matAdd]
  exact hsum

/-- Loewner order is monotone under nonnegative scaling. -/
theorem loewnerLE_scale_nonneg {n : Nat} (r : Rat) (A B : Mat n n) :
    0 ≤ r → loewnerLE A B → loewnerLE (matScale r A) (matScale r B) := by
  intro hr hAB
  rw [loewnerLE_iff_psd_sub] at hAB ⊢
  rw [matSub_scale]
  exact posSemidef_scale_nonneg r (matSub B A) hr hAB

/-- Loewner order is preserved by matrix conjugation. -/
theorem loewnerLE_conjugate {m n : Nat} (M : Mat m n) (A B : Mat n n) :
    loewnerLE A B →
    loewnerLE (matMul (matMul M A) (transpose M)) (matMul (matMul M B) (transpose M)) := by
  intro hAB
  rw [loewnerLE_iff_psd_sub] at hAB ⊢
  rw [← matSub_matMul_conjugate]
  exact posSemidef_conjugate M (matSub B A) hAB

/-- Subtracting a PSD matrix gives a Loewner-smaller matrix. -/
theorem loewnerLE_matSub_self {n : Nat} (X Y : Mat n n) :
    PositiveSemidefinite Y → loewnerLE (matSub X Y) X := by
  intro hY
  rw [loewnerLE_iff_psd_sub]
  rw [matSub_self_matSub]
  exact hY

/-- `loewnerLE X (matAdd X Y)` whenever `Y` is positive semidefinite. -/
theorem loewnerLE_self_matAdd {n : Nat} (X Y : Mat n n)
    (hY : PositiveSemidefinite Y) : loewnerLE X (matAdd X Y) := by
  rw [loewnerLE_iff_psd_sub]
  have hdiff : matSub (matAdd X Y) X = Y := by
    funext i j
    unfold matSub matAdd
    grind [Rat.sub_eq_add_neg, Rat.add_assoc, Rat.add_comm, Rat.add_left_comm]
  rw [hdiff]
  exact hY

/-- Difference of the scaled AM-GM envelope and the unscaled sum. -/
theorem matSub_scaled_add {n : Nat} (A B : Mat n n) (t : Rat) :
    matSub (matAdd (matScale (1 + t) A) (matScale (1 + t⁻¹) B)) (matAdd A B) =
      matAdd (matScale t A) (matScale t⁻¹ B) := by
  funext i j
  unfold matSub matAdd matScale
  grind [Rat.sub_eq_add_neg, Rat.add_assoc, Rat.add_comm, Rat.add_left_comm,
    Rat.mul_add, Rat.add_mul]

/--
For PSD `A`, PSD `B`, and `t > 0`, `A + B` is Loewner-dominated by
`(1 + t) A + (1 + t⁻¹) B`.  The difference is
`t A + t⁻¹ B`, a nonnegative linear combination of PSD matrices.
-/
theorem loewnerLE_scaled_add {n : Nat} (A B : Mat n n) (t : Rat)
    (ht : 0 < t) (hA : PositiveSemidefinite A) (hB : PositiveSemidefinite B) :
    loewnerLE
      (matAdd A B)
      (matAdd (matScale (1 + t) A) (matScale (1 + t⁻¹) B)) := by
  rw [loewnerLE_iff_psd_sub]
  rw [matSub_scaled_add]
  have ht_nonneg : 0 ≤ t := Rat.le_of_lt ht
  have ht_inv_nonneg : 0 ≤ t⁻¹ := by
    exact Rat.le_of_lt (Rat.inv_pos.mpr ht)
  exact posSemidef_add (matScale t A) (matScale t⁻¹ B)
    (posSemidef_scale_nonneg t A ht_nonneg hA)
    (posSemidef_scale_nonneg t⁻¹ B ht_inv_nonneg hB)

/-- Trace is monotone for Loewner order. -/
theorem loewnerLE_traceMat_mono {n : Nat} (A B : Mat n n) :
    loewnerLE A B → traceMat A ≤ traceMat B := by
  intro hAB
  rw [Rat.le_iff_sub_nonneg]
  rw [← traceMat_sub]
  exact psd_trace_nonneg (matSub B A) ((loewnerLE_iff_psd_sub A B).mp hAB)

/-- Native membrane budget `K_{C,Γ}(L) ⪯ Θ`. -/
def nativeMembraneBudget {y : Nat} (K Theta : Mat y y) : Prop :=
  loewnerLE K Theta

/-- A critical-pair witness `y` with `y^T (K - Θ) y > 0`. -/
def criticalPairWitness {y : Nat} (K Theta : Mat y y) (nativeRecombination : Vec y) : Prop :=
  0 < quad (matSub K Theta) nativeRecombination

/--
Probe-family currency: every native recombination has capacity
`y^T K_{C,Γ}(L)y`; the membrane budget is the Loewner inequality, and
failure is equivalent to a critical-pair witness.
-/
theorem probeFamilyCurrency {e a y : Nat}
    (C : Mat e e) (Gamma : Mat e a) (L : Mat y e)
    (Theta : Mat y y)
    (hDiag : StrictPositiveDiagonal (packagedAudit C Gamma)) :
    (∀ nativeRecombination,
      capacity C Gamma L nativeRecombination =
        quad (packagedCurrency C Gamma L) nativeRecombination) ∧
      (nativeMembraneBudget (packagedCurrency C Gamma L) Theta ↔
        loewnerLE (packagedCurrency C Gamma L) Theta) ∧
      (¬ nativeMembraneBudget (packagedCurrency C Gamma L) Theta ↔
        ∃ nativeRecombination,
          criticalPairWitness (packagedCurrency C Gamma L) Theta nativeRecombination) := by
  constructor
  · intro nativeRecombination
    unfold capacity capacityOptimizer packagedCurrency
    exact auditOptimalEnergy_eq_currencyQuad
      (packagedAudit C Gamma) (packagedNative L Gamma) hDiag nativeRecombination
  constructor
  · rfl
  · classical
    change
      ¬ (∀ nativeRecombination,
          ¬ criticalPairWitness
              (packagedCurrency C Gamma L) Theta nativeRecombination) ↔
        ∃ nativeRecombination,
          criticalPairWitness
            (packagedCurrency C Gamma L) Theta nativeRecombination
    constructor
    · intro hNoBudget
      exact Classical.byContradiction
        (fun hNoWitness =>
          hNoBudget
            (fun nativeRecombination hWitness =>
              hNoWitness ⟨nativeRecombination, hWitness⟩))
    · intro hWitness hBudget
      cases hWitness with
      | intro nativeRecombination hCritical =>
          exact hBudget nativeRecombination hCritical

/-- Range predicate for a finite matrix. -/
def InRange {m n : Nat} (M : Mat m n) (z : Vec m) : Prop :=
  ∃ a, matVec M a = z

/-- Extended rational values for finite costs and `+∞`. -/
inductive ExtendedRat where
  | finite : Rat → ExtendedRat
  | posInfinity : ExtendedRat
deriving Repr, DecidableEq

/--
Minimum-spend cost as an infimum certificate.  A finite value is a lower
bound for every feasible package vector and is attained by one feasible
package vector.  The `+∞` value records infeasibility of the affine
constraint `L_Γ a = z`.
-/
def minimumSpendCost {e a y : Nat}
    (C : Mat e e) (Gamma : Mat e a) (L : Mat y e) (z : Vec y)
    (value : ExtendedRat) : Prop :=
  let C_Gamma := packagedAudit C Gamma
  let L_Gamma := packagedNative L Gamma
  match value with
  | ExtendedRat.finite m =>
      (∀ packageVector, matVec L_Gamma packageVector = z →
        m ≤ quad C_Gamma packageVector) ∧
        ∃ packageVector,
          matVec L_Gamma packageVector = z ∧
          quad C_Gamma packageVector = m
  | ExtendedRat.posInfinity =>
      ¬ InRange L_Gamma z

/--
Minimum-spend duality: for a desired response `z`, the finite
closed-form infimum is `z^T K_{C,Γ}(L)^† z` on the native range and
`+∞` off that range.
-/
theorem minimumSpendDuality {e a y : Nat}
    (C : Mat e e) (Gamma : Mat e a) (L : Mat y e) (z : Vec y) :
    ¬ InRange (packagedNative L Gamma) z →
      minimumSpendCost C Gamma L z ExtendedRat.posInfinity := by
  intro hz
  unfold minimumSpendCost
  simp only
  exact hz

end SixBirdsMetaMath.Main.LegalQuotient
