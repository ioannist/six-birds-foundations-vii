import FoundationsVII.Dynamics.All

/-!
# FVII-SCI-04 no-go: no arrow from holonomy alone
-/

namespace FoundationsVII.NoGo

structure HolonomyArrowProfile where
  holonomy : Bool
  drive : Bool
  pathAsymmetry : Bool
  reversalFails : Bool
  budgeted : Bool
  audited : Bool
  arrowCredit : Bool
  deriving Repr, DecidableEq, BEq

namespace HolonomyArrowProfile

def Eligible (profile : HolonomyArrowProfile) : Prop :=
  profile.arrowCredit = true ∧
  profile.drive = true ∧
  profile.pathAsymmetry = true ∧
  profile.reversalFails = true ∧
  profile.budgeted = true ∧
  profile.audited = true

instance (profile : HolonomyArrowProfile) : Decidable (Eligible profile) := by
  unfold Eligible
  infer_instance

def HolonomyOnly (profile : HolonomyArrowProfile) : Prop :=
  profile.holonomy = true ∧
  profile.drive = false ∧
  profile.pathAsymmetry = false ∧
  profile.reversalFails = false

instance (profile : HolonomyArrowProfile) : Decidable (HolonomyOnly profile) := by
  unfold HolonomyOnly
  infer_instance

end HolonomyArrowProfile

/-- NGVII-10 structural no-go. -/
theorem NGVII_10_no_arrow_from_holonomy_alone
    (profile : HolonomyArrowProfile)
    (hOnly : HolonomyArrowProfile.HolonomyOnly profile) :
    ¬ HolonomyArrowProfile.Eligible profile := by
  intro hEligible
  have hDrive : profile.drive = true := hEligible.2.1
  rw [hOnly.2.1] at hDrive
  exact Bool.noConfusion hDrive

private def holonomyOnlyControl : HolonomyArrowProfile :=
  { holonomy := true, drive := false, pathAsymmetry := false,
    reversalFails := false, budgeted := true, audited := true,
    arrowCredit := false }

private def drivenEscapeControl : HolonomyArrowProfile :=
  { holonomy := true, drive := true, pathAsymmetry := true,
    reversalFails := true, budgeted := true, audited := true,
    arrowCredit := true }

theorem NGVII_10_holonomy_zero_arrow_control :
    HolonomyArrowProfile.HolonomyOnly holonomyOnlyControl ∧
    holonomyOnlyControl.arrowCredit = false := by decide

theorem NGVII_10_escape_independent_driven_arrow :
    HolonomyArrowProfile.Eligible drivenEscapeControl := by decide

end FoundationsVII.NoGo
