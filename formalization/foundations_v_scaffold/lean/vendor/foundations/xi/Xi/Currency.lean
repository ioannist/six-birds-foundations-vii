import Main.LegalQuotient

open SixBirdsMetaMath.Main.LegalQuotient

namespace SixBirdsMetaMath.Xi.Currency

/-!
Ξ companion paper §3 "Currency and minimum spend".

The full paper theorem identifies the minimum spend with a
pseudoinverse quadratic form on range and with `+∞` off range.  This
module mechanizes the off-range branch in the same finite rational
matrix model used by the main-axis legal quotient module.
-/

/-- Bare Xi currency `K_F = F C^† F^T`. -/
def xiCurrency {e y : Nat} (C : Mat e e) (F : Mat y e) : Mat y y :=
  matMul (matMul F (diagonalPseudoInverse C)) (transpose F)

/--
Minimum-spend cost for a bare probe family `F`.  A finite value is a
lower bound for all feasible witnesses and is attained; `+∞` records
that `z` is outside the range of `F`.
-/
def xiMinimumSpendCost {e y : Nat}
    (C : Mat e e) (F : Mat y e) (z : Vec y) (value : ExtendedRat) : Prop :=
  match value with
  | ExtendedRat.finite m =>
      (∀ u, matVec F u = z → m ≤ quad C u) ∧
        ∃ u, matVec F u = z ∧ quad C u = m
  | ExtendedRat.posInfinity =>
      ¬ InRange F z

/--
Minimum-spend duality, off-range branch: if no audit vector maps to
`z`, the spend is `+∞`.
-/
theorem xiMinimumSpendDuality {e y : Nat}
    (C : Mat e e) (F : Mat y e) (z : Vec y) :
    ¬ InRange F z →
      xiMinimumSpendCost C F z ExtendedRat.posInfinity := by
  intro hz
  unfold xiMinimumSpendCost
  exact hz

end SixBirdsMetaMath.Xi.Currency
