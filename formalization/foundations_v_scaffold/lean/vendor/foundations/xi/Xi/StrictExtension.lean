import Main.LegalQuotient
import Xi.AdequacyResidual
import Main.CriticalPair
import Main.XiInterface

open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Xi.AdequacyResidual
open SixBirdsMetaMath.Main.CriticalPair
open SixBirdsMetaMath.Main.XiInterface

namespace SixBirdsMetaMath.Xi.StrictExtension

/-!
Ξ companion paper §8 "Strict native extension".

This module reuses the main-axis conditional currencies for the Xi
strict-extension chain rule and same-family saturation corollary.
-/

/--
Chain rule for adequacy residuals, Loewner clause: the algebraic
Schur chain rule and PSD of the conditional Schur term imply that the
extended residual is Loewner dominated by the original residual.
-/
theorem chainRule {e y z m : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (M : Mat m e)
    (KLLdagger : Mat y y) (KMMLdagger : Mat m m)
    (extendedResidual : Mat z z)
    (hChainRule :
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
    loewnerLE extendedResidual (adequacyResidual C L D KLLdagger) :=
  strictExtensionContraction C L D M KLLdagger KMMLdagger extendedResidual
    hChainRule hConditionalSchurPSD

/--
Same-family saturation: if the chain-rule update term has zero
`K_{DM|L}` factor, the extended residual equals the original residual.
The factorization hypothesis `M = B * L` is included as the paper
condition that supplies the elevated zero conditional-currency fact.
-/
theorem sameFamilySaturation {e y z m : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (M : Mat m e)
    (KLLdagger : Mat y y) (KMMLdagger : Mat m m)
    (B : Mat m y)
    (extendedResidual : Mat z z)
    (hChainRule :
      extendedResidual =
        matSub
          (adequacyResidual C L D KLLdagger)
          (matMul
            (matMul (conditionalCurrencyDM_L C L D M KLLdagger) KMMLdagger)
            (conditionalCurrencyMD_L C L D M KLLdagger)))
    (hM_factors : M = matMul B L)
    (hDML_zero :
      conditionalCurrencyDM_L C L D M KLLdagger = zeroMat z m) :
    extendedResidual = adequacyResidual C L D KLLdagger := by
  have _ : M = matMul B L := hM_factors
  rw [hChainRule, hDML_zero]
  rw [matMul_zero_left]
  rw [matMul_zero_left]
  rw [matSub_zero_right]

end SixBirdsMetaMath.Xi.StrictExtension
