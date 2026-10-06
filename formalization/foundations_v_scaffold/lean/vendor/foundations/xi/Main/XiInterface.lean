import Main.LegalQuotient
import Xi.AdequacyResidual

open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Xi.AdequacyResidual

namespace SixBirdsMetaMath.Main.XiInterface

/-!
Main paper §4 "The Ξ companion interface".

This module records the main-axis interface to the Ξ companion.  The
current mechanization proves the Schur-identity branch of the paper's
adequacy interface; the Loewner monotonicity and factorization
equivalence branches remain deferred in the manifest.
-/

/-- Optimal native explanation map `A_* = K_{DL} K_{LL}^†`. -/
def optimalNativeExplanation {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (KLLdagger : Mat y y) : Mat z y :=
  matMul (blockCurrencyDL C L D) KLLdagger

/--
Adequacy interface, Schur identity branch:
`K_DD = A_* K_LL A_*^T + Ξ_C(D|L)`.

The three algebraic hypotheses expose the paper's standing
Moore-Penrose/symmetry facts needed for the Schur calculation.
-/
theorem adequacyInterface {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (KLLdagger : Mat y y)
    (hKLDsym : transpose (blockCurrencyDL C L D) = blockCurrencyLD C L D)
    (hKLLdaggerSym : transpose KLLdagger = KLLdagger)
    (hMPLLD : matMul (matMul (blockCurrencyLL C L) KLLdagger)
          (blockCurrencyLD C L D) = blockCurrencyLD C L D) :
    blockCurrencyDD C D =
      matAdd
        (matMul
          (matMul (optimalNativeExplanation C L D KLLdagger) (blockCurrencyLL C L))
          (transpose (optimalNativeExplanation C L D KLLdagger)))
        (adequacyResidual C L D KLLdagger) := by
  let KLL := blockCurrencyLL C L
  let KDL := blockCurrencyDL C L D
  let KLD := blockCurrencyLD C L D
  let KDD := blockCurrencyDD C D
  let schurTerm := matMul (matMul KDL KLLdagger) KLD
  have hAstarSchur :
      matMul
          (matMul (optimalNativeExplanation C L D KLLdagger) KLL)
          (transpose (optimalNativeExplanation C L D KLLdagger)) =
        schurTerm := by
    calc
      matMul
          (matMul (optimalNativeExplanation C L D KLLdagger) KLL)
          (transpose (optimalNativeExplanation C L D KLLdagger))
          = matMul (matMul (matMul KDL KLLdagger) KLL)
              (transpose (matMul KDL KLLdagger)) := rfl
      _ = matMul (matMul (matMul KDL KLLdagger) KLL)
              (matMul (transpose KLLdagger) (transpose KDL)) := by
              rw [transpose_matMul]
      _ = matMul (matMul (matMul KDL KLLdagger) KLL)
              (matMul KLLdagger (transpose KDL)) := by
              rw [hKLLdaggerSym]
      _ = matMul (matMul (matMul KDL KLLdagger) KLL)
              (matMul KLLdagger KLD) := by
              rw [hKLDsym]
      _ = matMul (matMul KDL KLLdagger)
              (matMul KLL (matMul KLLdagger KLD)) := by
              rw [matMul_assoc (matMul KDL KLLdagger) KLL (matMul KLLdagger KLD)]
      _ = matMul (matMul KDL KLLdagger)
              (matMul (matMul KLL KLLdagger) KLD) := by
              rw [← matMul_assoc KLL KLLdagger KLD]
      _ = matMul (matMul KDL KLLdagger) KLD := by
              rw [show matMul (matMul KLL KLLdagger) KLD = KLD by
                unfold KLL KLD
                exact hMPLLD]
      _ = schurTerm := rfl
  symm
  calc
    matAdd
        (matMul
          (matMul (optimalNativeExplanation C L D KLLdagger) (blockCurrencyLL C L))
          (transpose (optimalNativeExplanation C L D KLLdagger)))
        (adequacyResidual C L D KLLdagger)
        = matAdd schurTerm (adequacyResidual C L D KLLdagger) := by
            rw [show blockCurrencyLL C L = KLL by rfl]
            rw [hAstarSchur]
    _ = matAdd schurTerm (matSub KDD schurTerm) := rfl
    _ = KDD := matAdd_sub_cancel KDD schurTerm
    _ = blockCurrencyDD C D := rfl

end SixBirdsMetaMath.Main.XiInterface
