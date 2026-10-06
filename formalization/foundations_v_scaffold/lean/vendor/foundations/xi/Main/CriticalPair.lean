import Main.LegalQuotient
import Xi.AdequacyResidual

open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Xi.AdequacyResidual

namespace SixBirdsMetaMath.Main.CriticalPair

/-!
Main paper §8 "Critical-pair completion and strict extension".

This module records the finite-matrix Schur-complement currencies used
by the strict-extension theorem.  The full block-stacked residual
identity for `L^+ = [L; M]` is not constructed here; it is exposed as a
paper algebra hypothesis in the labeled theorem below.
-/

/-- Conditional currency `K_{DM|L} = K_DM - K_DL · K_LL^† · K_LM`. -/
def conditionalCurrencyDM_L {e y z m : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (M : Mat m e)
    (KLLdagger : Mat y y) : Mat z m :=
  matSub
    (blockCurrencyDL C M D)
    (matMul
      (matMul (blockCurrencyDL C L D) KLLdagger)
      (blockCurrencyLD C L M))

/-- Conditional currency `K_{MM|L} = K_MM - K_ML · K_LL^† · K_LM`. -/
def conditionalCurrencyMM_L {e y m : Nat}
    (C : Mat e e) (L : Mat y e) (M : Mat m e)
    (KLLdagger : Mat y y) : Mat m m :=
  matSub
    (blockCurrencyLL C M)
    (matMul
      (matMul (blockCurrencyDL C L M) KLLdagger)
      (blockCurrencyLD C L M))

/-- Conditional currency `K_{MD|L} = K_MD - K_ML · K_LL^† · K_LD`. -/
def conditionalCurrencyMD_L {e y z m : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (M : Mat m e)
    (KLLdagger : Mat y y) : Mat m z :=
  matSub
    (blockCurrencyLD C M D)
    (matMul
      (matMul (blockCurrencyDL C L M) KLLdagger)
      (blockCurrencyLD C L D))

/--
Strict extension contraction, Loewner clause.  If the extended residual
is related to the old residual by the Schur-update identity and the
conditional Schur term is PSD, then the extended residual is Loewner
dominated by the old one.
-/
theorem strictExtensionContraction {e y z m : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (M : Mat m e)
    (KLLdagger : Mat y y) (KMMLdagger : Mat m m)
    (extendedResidual : Mat z z)
    (hExtendedResidual :
      extendedResidual =
        matSub
          (adequacyResidual C L D KLLdagger)
          (matMul
            (matMul (conditionalCurrencyDM_L C L D M KLLdagger) KMMLdagger)
            (conditionalCurrencyMD_L C L D M KLLdagger)))
    (hConditionalSchurPSD :
      PositiveSemidefinite
        (matMul
          (matMul (conditionalCurrencyDM_L C L D M KLLdagger) KMMLdagger)
          (conditionalCurrencyMD_L C L D M KLLdagger))) :
    loewnerLE extendedResidual (adequacyResidual C L D KLLdagger) := by
  rw [hExtendedResidual]
  exact loewnerLE_matSub_self
    (adequacyResidual C L D KLLdagger)
    (matMul
      (matMul (conditionalCurrencyDM_L C L D M KLLdagger) KMMLdagger)
      (conditionalCurrencyMD_L C L D M KLLdagger))
    hConditionalSchurPSD

end SixBirdsMetaMath.Main.CriticalPair
