import Main.LegalQuotient
import Xi.AdequacyResidual

open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Xi.AdequacyResidual

namespace SixBirdsMetaMath.Xi.Obstruction

/-!
Ξ companion paper §10 "Obstruction and repair calculus".

This module proves the Loewner violation / positive quadratic witness
duality for the adequacy defect.
-/

/-- Adequacy defect `Delta_Xi = Xi_C(D | L) - Omega`. -/
def adequacyDefect {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y) (Omega : Mat z z) : Mat z z :=
  matSub (adequacyResidual C L D KLLdagger) Omega

/--
Blind-spot witness: failure of the adequacy-residual budget is
equivalent to a recombination vector with positive quadratic form on
the adequacy defect.
-/
theorem blindSpotWitness {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y) (Omega : Mat z z) :
    ¬ loewnerLE (adequacyResidual C L D KLLdagger) Omega ↔
      ∃ z_witness : Vec z,
        0 < quad (adequacyDefect C L D KLLdagger Omega) z_witness := by
  unfold loewnerLE adequacyDefect
  constructor
  · intro h
    exact Classical.byContradiction
      (fun hNoWitness =>
        h
          (fun z_witness hPositive =>
            hNoWitness ⟨z_witness, hPositive⟩))
  · intro h hAll
    cases h with
    | intro z_witness hPositive => exact hAll z_witness hPositive

end SixBirdsMetaMath.Xi.Obstruction
