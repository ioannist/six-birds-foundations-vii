import SixBirdsMetaMath.Main.LayerDissolving

/-!
F6 No-Needles Stability.

This Foundations IV stability law is anchored to the inherited Paper 4
layer-dissolving endpoint theorem. The F-IV statement keeps the structural
spine: native budget plus residual budget plus transported endpoint budget
implies the dissolving endpoint budget, hence no unpriced layer-dissolving
critical pair at the formed stability package.
-/

namespace SixBirdsMetaMath.FoundationsIV.Stability.NoNeedles

open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Main.XiInterface
open SixBirdsMetaMath.Xi.AdequacyResidual

/--
No-Needles Stability, anchored to
`SixBirdsMetaMath.Main.LayerDissolving.layerDissolvingMaster`.

The conclusion is the endpoint Loewner budget
`S K^D S^* <= ThetaD`; because `loewnerLE` is defined as absence of a
positive critical-pair witness, this is the formal no-needles endpoint.
-/
theorem no_needles_stability {e y z d : Nat}
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
      ThetaD :=
  SixBirdsMetaMath.Main.LayerDissolving.layerDissolvingMaster
    C L D KLLdagger ThetaY OmegaZ ThetaD S
    hKLDsym hKLLdaggerSym hMPLLD hKLbound hXibound hTransport

end SixBirdsMetaMath.FoundationsIV.Stability.NoNeedles
