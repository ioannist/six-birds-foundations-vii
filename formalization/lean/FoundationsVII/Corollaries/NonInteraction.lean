import FoundationsVII.Join.NonInteraction

/-!
# Closed-family non-interaction and join exclusion
-/

namespace FoundationsVII

structure JoinClaimUnderCoverage where
  coverage : ContactCoverageCertificate
  strictJoinCredit : Bool
  strictJoinRequiresObservedContact :
    strictJoinCredit = true → coverage.observedContact = true

namespace JoinClaimUnderCoverage

/-- Inside the exact covered family, a certified absence of contact excludes
strict-join credit whose own admission rule requires observed contact. -/
theorem certified_noninteraction_excludes_strict_join
    {profile : JoinClaimUnderCoverage}
    (hCoverage : ContactCoverageCertificate.Certified profile.coverage) :
    profile.strictJoinCredit = false := by
  cases hCredit : profile.strictJoinCredit with
  | false => rfl
  | true =>
      have hObserved : profile.coverage.observedContact = true :=
        profile.strictJoinRequiresObservedContact hCredit
      have hNull : profile.coverage.observedContact = false :=
        ContactCoverageCertificate.certified_has_no_observed_contact hCoverage
      rw [hNull] at hObserved
      exact Bool.noConfusion hObserved

/-- A valid non-interaction certificate still records explicit outside-family
escape routes. -/
theorem certified_noninteraction_retains_escape_routes
    {profile : JoinClaimUnderCoverage}
    (hCoverage : ContactCoverageCertificate.Certified profile.coverage) :
    profile.coverage.escapeRoutes ≠ [] :=
  ContactCoverageCertificate.certified_records_escape_routes hCoverage

end JoinClaimUnderCoverage

end FoundationsVII
