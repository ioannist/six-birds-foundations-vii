import SixBirdsMetaMath.Main.LegalQuotient
import SixBirdsMetaMath.Main.XiInterface
import SixBirdsMetaMath.Xi.AdequacyResidual

open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Main.XiInterface
open SixBirdsMetaMath.Xi.AdequacyResidual

namespace SixBirdsMetaMath.Main.LayerDissolving

/-!
Main paper §6 "Layer-dissolving membrane endpoint theorem".

This module mechanizes the transport-bound branch of the endpoint
theorem.  The capacity supremum consequence and the qualitative
no-needles assertion remain deferred in the manifest.
-/

/-- Layer-dissolving master theorem: transport-bound branch. -/
theorem layerDissolvingMaster {e y z d : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y)
    (ThetaY : Mat y y) (OmegaZ : Mat z z) (ThetaD : Mat d d)
    (S : Mat d z)
    (hKLDsym : transpose (blockCurrencyDL C L D) = blockCurrencyLD C L D)
    (hKLLdaggerSym : transpose KLLdagger = KLLdagger)
    (hMPLLD : matMul (matMul (blockCurrencyLL C L) KLLdagger)
      (blockCurrencyLD C L D) = blockCurrencyLD C L D)
    (hKLbound : loewnerLE (blockCurrencyLL C L) ThetaY)
    (hXibound : loewnerLE (adequacyResidual C L D KLLdagger) OmegaZ)
    (hTransport :
      loewnerLE
        (matMul
          (matMul S
            (matAdd
              (matMul
                (matMul (optimalNativeExplanation C L D KLLdagger) ThetaY)
                (transpose (optimalNativeExplanation C L D KLLdagger)))
              OmegaZ))
          (transpose S))
        ThetaD) :
    loewnerLE
      (matMul (matMul S (blockCurrencyDD C D)) (transpose S))
      ThetaD := by
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
  have hSchurBound :
      loewnerLE (blockCurrencyDD C D)
        (matAdd (matMul (matMul Astar ThetaY) (transpose Astar)) OmegaZ) := by
    rw [hSchur]
    exact loewnerLE_add_mono
      (matMul (matMul Astar (blockCurrencyLL C L)) (transpose Astar))
      (matMul (matMul Astar ThetaY) (transpose Astar))
      (adequacyResidual C L D KLLdagger)
      OmegaZ
      hNativeConjugated
      hXibound
  have hTransportSource :
      loewnerLE
        (matMul (matMul S (blockCurrencyDD C D)) (transpose S))
        (matMul
          (matMul S
          (matAdd
            (matMul (matMul Astar ThetaY) (transpose Astar))
            OmegaZ))
        (transpose S)) :=
    loewnerLE_conjugate S (blockCurrencyDD C D)
      (matAdd (matMul (matMul Astar ThetaY) (transpose Astar)) OmegaZ)
      hSchurBound
  exact loewnerLE_trans
    (matMul (matMul S (blockCurrencyDD C D)) (transpose S))
    (matMul
      (matMul S
        (matAdd
          (matMul (matMul Astar ThetaY) (transpose Astar))
          OmegaZ))
      (transpose S))
    ThetaD
    hTransportSource
    hTransport

end SixBirdsMetaMath.Main.LayerDissolving
