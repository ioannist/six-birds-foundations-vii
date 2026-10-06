import FoundationsVII.Join.Strictness
import FoundationsVII.Dynamics.Holonomy

/-!
# Strict join, holonomy, and independently certified arrows
-/

namespace FoundationsVII

/-- Holonomy and strictness may coexist while arrow credit remains blocked by
an invalid drive certificate. -/
theorem strict_join_and_holonomy_do_not_replace_drive
    {join : StrictJoinEvidence} {claim : ArrowClaim}
    (hJoin : StrictJoinEvidence.Certified join)
    (hHolonomy : RouteComparison.Holonomy claim.comparison)
    (hDriveInvalid : ¬ DriveCertificate.Valid claim.drive) :
    StrictJoinEvidence.Certified join ∧
      RouteComparison.Holonomy claim.comparison ∧
      ¬ ArrowClaim.Eligible claim := by
  refine ⟨hJoin, hHolonomy, ?_⟩
  intro hArrow
  exact hDriveInvalid hArrow.2

/-- When holonomy is accompanied by an independently valid drive certificate
and explicit arrow credit, the arrow package is eligible. -/
theorem holonomy_with_independent_drive_supports_arrow
    {claim : ArrowClaim}
    (hHolonomy : RouteComparison.Holonomy claim.comparison)
    (hDrive : DriveCertificate.Valid claim.drive)
    (hCredit : claim.arrowCredit = true) :
    RouteComparison.Holonomy claim.comparison ∧ ArrowClaim.Eligible claim := by
  exact ⟨hHolonomy, hCredit, hDrive⟩

end FoundationsVII
