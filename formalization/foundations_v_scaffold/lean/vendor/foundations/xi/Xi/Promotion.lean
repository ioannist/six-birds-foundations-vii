import Main.LegalQuotient
import Main.XiInterface
import Xi.AdequacyResidual

open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Main.XiInterface
open SixBirdsMetaMath.Xi.AdequacyResidual

namespace SixBirdsMetaMath.Xi.Promotion

/-!
Ξ companion paper §7 "Promotion from native membrane to dissolving
membrane".

This module proves the Loewner promotion branch from a native budget
and a residual budget to the dissolving-family budget.
-/

/--
Adequacy promotion: under native budget `K_LL ⪯ Θ_Y` and residual
budget `Ξ_C(D | L) ⪯ Ξ_Z`, the dissolving currency is bounded by
`A_* Θ_Y A_*^T + Ξ_Z`.
-/
theorem adequacyPromotion {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) (KLLdagger : Mat y y)
    (ThetaY : Mat y y) (XiZ : Mat z z)
    (hKLDsym : transpose (blockCurrencyDL C L D) = blockCurrencyLD C L D)
    (hKLLdaggerSym : transpose KLLdagger = KLLdagger)
    (hMPLLD : matMul (matMul (blockCurrencyLL C L) KLLdagger)
        (blockCurrencyLD C L D) = blockCurrencyLD C L D)
    (hKLbound : loewnerLE (blockCurrencyLL C L) ThetaY)
    (hXibound : loewnerLE (adequacyResidual C L D KLLdagger) XiZ) :
    loewnerLE
      (blockCurrencyDD C D)
      (matAdd
        (matMul
          (matMul (optimalNativeExplanation C L D KLLdagger) ThetaY)
          (transpose (optimalNativeExplanation C L D KLLdagger)))
        XiZ) := by
  let Astar := optimalNativeExplanation C L D KLLdagger
  have hSchur : blockCurrencyDD C D =
      matAdd
        (matMul
          (matMul (optimalNativeExplanation C L D KLLdagger) (blockCurrencyLL C L))
          (transpose (optimalNativeExplanation C L D KLLdagger)))
        (adequacyResidual C L D KLLdagger) :=
    adequacyInterface C L D KLLdagger hKLDsym hKLLdaggerSym hMPLLD
  have hNativeConjugated :
      loewnerLE
        (matMul (matMul Astar (blockCurrencyLL C L)) (transpose Astar))
        (matMul (matMul Astar ThetaY) (transpose Astar)) :=
    loewnerLE_conjugate Astar (blockCurrencyLL C L) ThetaY hKLbound
  rw [hSchur]
  exact loewnerLE_add_mono
    (matMul (matMul Astar (blockCurrencyLL C L)) (transpose Astar))
    (matMul (matMul Astar ThetaY) (transpose Astar))
    (adequacyResidual C L D KLLdagger)
    XiZ
    hNativeConjugated
    hXibound

end SixBirdsMetaMath.Xi.Promotion
