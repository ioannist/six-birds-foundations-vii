import Main.LegalQuotient

open SixBirdsMetaMath.Main.LegalQuotient

namespace SixBirdsMetaMath.Xi.AdequacyResidual

/-!
Ξ companion paper §4 "Definition of the adequacy residual".

This module defines the block currencies and the residual
`Ξ_C(D | L) = K_DD - K_DL K_LL^† K_LD` in the finite rational matrix
model used by the main-axis legal quotient module.
-/

/-- Block currency `K_{LL}`. -/
def blockCurrencyLL {e y : Nat} (C : Mat e e) (L : Mat y e) : Mat y y :=
  matMul (matMul L (diagonalPseudoInverse C)) (transpose L)

/-- Block currency `K_{DL}`. -/
def blockCurrencyDL {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) : Mat z y :=
  matMul (matMul D (diagonalPseudoInverse C)) (transpose L)

/-- Block currency `K_{LD}`. -/
def blockCurrencyLD {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e) : Mat y z :=
  matMul (matMul L (diagonalPseudoInverse C)) (transpose D)

/-- Block currency `K_{DD}`. -/
def blockCurrencyDD {e z : Nat} (C : Mat e e) (D : Mat z e) : Mat z z :=
  matMul (matMul D (diagonalPseudoInverse C)) (transpose D)

/--
Adequacy residual `Ξ_C(D | L) = K_DD - K_DL K_LL^† K_LD`.  The
Moore-Penrose inverse `K_LL^†` is exposed as an explicit parameter
`KLLdagger` because no constructive Moore-Penrose pseudoinverse for
non-diagonal matrices is yet available in this project.
-/
def adequacyResidual {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y) : Mat z z :=
  matSub (blockCurrencyDD C D)
    (matMul (matMul (blockCurrencyDL C L D) KLLdagger)
      (blockCurrencyLD C L D))

end SixBirdsMetaMath.Xi.AdequacyResidual
