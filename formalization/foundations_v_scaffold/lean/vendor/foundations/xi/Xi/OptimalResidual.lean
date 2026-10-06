import Main.LegalQuotient
import Xi.AdequacyResidual
import Main.XiInterface

open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Xi.AdequacyResidual
open SixBirdsMetaMath.Main.XiInterface

namespace SixBirdsMetaMath.Xi.OptimalResidual

/-!
Ξ companion paper §6 "Optimal residual and exact adequacy".

This module records the Package 5 partial mechanization of the
optimal residual identity and exact adequacy.  The full paper proofs
depend on Moore-Penrose support identities and quotient/projection
constructions that are still elevated as explicit hypotheses here.
-/

/--
Residual-squared-norm operator for an explanation map `A`:
`(D - A * L) * C^dagger * (D - A * L)^T`.
-/
def residualQuad {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (A : Mat z y) : Mat z z :=
  let residualMap := matSub D (matMul A L)
  matMul (matMul residualMap (diagonalPseudoInverse C)) (transpose residualMap)

/-- Penalty term `(A - A_*) * K_LL * (A - A_*)^T`. -/
def explanationPenalty {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y) (A : Mat z y) : Mat z z :=
  let dev := matSub A (optimalNativeExplanation C L D KLLdagger)
  matMul (matMul dev (blockCurrencyLL C L)) (transpose dev)

/--
Optimal residual identity, Loewner-minimal consequence branch: if the
paper's algebraic residual expansion holds and the native block
currency is positive semidefinite, then the adequacy residual is
Loewner-minimal below the residual currency for `A`.
-/
theorem optimalResidualIdentity {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y) (A : Mat z y)
    (hAlgebraicIdentity :
      residualQuad C L D A =
        matAdd
          (adequacyResidual C L D KLLdagger)
          (explanationPenalty C L D KLLdagger A))
    (hKLL_psd : PositiveSemidefinite (blockCurrencyLL C L)) :
    loewnerLE
      (adequacyResidual C L D KLLdagger)
      (residualQuad C L D A) := by
  have hPenaltyPSD :
      PositiveSemidefinite (explanationPenalty C L D KLLdagger A) := by
    unfold explanationPenalty
    exact posSemidef_conjugate
      (matSub A (optimalNativeExplanation C L D KLLdagger))
      (blockCurrencyLL C L)
      hKLL_psd
  rw [hAlgebraicIdentity]
  exact loewnerLE_self_matAdd
    (adequacyResidual C L D KLLdagger)
    (explanationPenalty C L D KLLdagger A)
    hPenaltyPSD

/--
Exact adequacy, partial four-condition chain.  The equivalence between
zero residual and optimal factorization, and the quotient-style
kernel-to-factorization implication, are exposed as hypotheses; the
factorization existence and kernel-inclusion directions are proved
directly.
-/
theorem exactAdequacy {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (KLLdagger : Mat y y)
    (h_i_implies_ii :
      adequacyResidual C L D KLLdagger = zeroMat z z →
        D = matMul (optimalNativeExplanation C L D KLLdagger) L)
    (h_ii_implies_i :
      D = matMul (optimalNativeExplanation C L D KLLdagger) L →
        adequacyResidual C L D KLLdagger = zeroMat z z)
    (h_iv_implies_ii :
      (∀ v, matVec L v = (fun _ => 0) → matVec D v = (fun _ => 0)) →
        D = matMul (optimalNativeExplanation C L D KLLdagger) L) :
    (adequacyResidual C L D KLLdagger = zeroMat z z ↔
       D = matMul (optimalNativeExplanation C L D KLLdagger) L) ∧
    (D = matMul (optimalNativeExplanation C L D KLLdagger) L →
       ∃ A : Mat z y, D = matMul A L) ∧
    ((∃ A : Mat z y, D = matMul A L) →
       ∀ v, matVec L v = (fun _ => 0) → matVec D v = (fun _ => 0)) ∧
    ((∀ v, matVec L v = (fun _ => 0) → matVec D v = (fun _ => 0)) →
       D = matMul (optimalNativeExplanation C L D KLLdagger) L) := by
  refine ⟨⟨h_i_implies_ii, h_ii_implies_i⟩, ?_, ?_, h_iv_implies_ii⟩
  · intro hD
    exact ⟨optimalNativeExplanation C L D KLLdagger, hD⟩
  · rintro ⟨A, hAL⟩ v hLv
    rw [hAL]
    rw [matVec_matMul, hLv]
    exact matVec_zero_input A

end SixBirdsMetaMath.Xi.OptimalResidual
