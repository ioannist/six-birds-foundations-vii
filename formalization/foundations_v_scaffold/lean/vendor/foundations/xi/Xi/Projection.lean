import Main.LegalQuotient
import Xi.AdequacyResidual

open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Xi.AdequacyResidual

namespace SixBirdsMetaMath.Xi.Projection

/-!
Ξ companion paper §5 "Projection theorem".

This module proves the algebraic Schur-complement equality in the
projection identity.  The paper's constructions of `T_L`, `T_D`, and
`P_L` are represented by explicit algebraic hypotheses; the Loewner
nonnegativity part is deferred until projection and PSD machinery is
available.
-/

/--
Projection identity, algebraic equality branch: under the block-currency
identifications supplied by `T_L`, `T_D`, and the algebraic projection
identity `T_L^T K_LL^† T_L = P_L`, the residual equals
`T_D (I - P_L) T_D^T`.
-/
theorem projectionIdentity {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y) (TL : Mat y e) (TD : Mat z e) (PL : Mat e e)
    (hKDD : matMul TD (transpose TD) = blockCurrencyDD C D)
    (hPLdef : matMul (matMul (transpose TL) KLLdagger) TL = PL)
    (hKDL : matMul TD (transpose TL) = blockCurrencyDL C L D)
    (hKLD : matMul TL (transpose TD) = blockCurrencyLD C L D) :
    adequacyResidual C L D KLLdagger =
      matMul (matMul TD (matSub (identityMat e) PL)) (transpose TD) := by
  have hSchur :
      matMul (matMul (blockCurrencyDL C L D) KLLdagger)
          (blockCurrencyLD C L D) =
        matMul (matMul TD PL) (transpose TD) := by
    calc
      matMul (matMul (blockCurrencyDL C L D) KLLdagger)
          (blockCurrencyLD C L D)
          = matMul (matMul (matMul TD (transpose TL)) KLLdagger)
              (matMul TL (transpose TD)) := by
              rw [← hKDL, ← hKLD]
      _ = matMul (matMul TD (matMul (transpose TL) KLLdagger))
              (matMul TL (transpose TD)) := by
              rw [matMul_assoc TD (transpose TL) KLLdagger]
      _ = matMul TD
              (matMul (matMul (transpose TL) KLLdagger)
                (matMul TL (transpose TD))) := by
              rw [matMul_assoc TD (matMul (transpose TL) KLLdagger)
                (matMul TL (transpose TD))]
      _ = matMul TD
              (matMul (matMul (matMul (transpose TL) KLLdagger) TL)
                (transpose TD)) := by
              rw [← matMul_assoc (matMul (transpose TL) KLLdagger) TL
                (transpose TD)]
      _ = matMul TD (matMul PL (transpose TD)) := by
              rw [hPLdef]
      _ = matMul (matMul TD PL) (transpose TD) := by
              rw [← matMul_assoc TD PL (transpose TD)]
  have hRhs :
      matMul (matMul TD (matSub (identityMat e) PL)) (transpose TD) =
        matSub (matMul TD (transpose TD))
          (matMul (matMul TD PL) (transpose TD)) := by
    calc
      matMul (matMul TD (matSub (identityMat e) PL)) (transpose TD)
          = matMul (matSub (matMul TD (identityMat e)) (matMul TD PL))
              (transpose TD) := by
              rw [matMul_sub_right]
      _ = matSub (matMul (matMul TD (identityMat e)) (transpose TD))
              (matMul (matMul TD PL) (transpose TD)) := by
              rw [matMul_sub_left]
      _ = matSub (matMul TD (transpose TD))
              (matMul (matMul TD PL) (transpose TD)) := by
              rw [matMul_identity_right]
  calc
    adequacyResidual C L D KLLdagger
        = matSub (blockCurrencyDD C D)
            (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
              (blockCurrencyLD C L D)) := rfl
    _ = matSub (matMul TD (transpose TD))
            (matMul (matMul TD PL) (transpose TD)) := by
            rw [← hKDD, hSchur]
    _ = matMul (matMul TD (matSub (identityMat e) PL)) (transpose TD) := hRhs.symm

end SixBirdsMetaMath.Xi.Projection
