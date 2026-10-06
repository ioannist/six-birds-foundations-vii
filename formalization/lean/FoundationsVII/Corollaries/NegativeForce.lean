import FoundationsVII.Access.Reachability
import FoundationsVII.Join.NonInteraction

/-!
# Coverage, horizon, and detector-qualified negative force
-/

namespace FoundationsVII

structure ScopedNegativePackage where
  contact : ContactCoverageCertificate
  occurrence : HorizonObservation

namespace ScopedNegativePackage

structure Certified (profile : ScopedNegativePackage) : Prop where
  contactClosed : ContactCoverageCertificate.Certified profile.contact
  occurrenceClosed : HorizonObservation.ClosedFamilyNegativeCertificate
    profile.occurrence

/-- Closed contact coverage and a complete occurrence horizon jointly license
only the scoped negative conclusions recorded by their two certificates. -/
theorem certified_excludes_contact_and_occurrence_at_declared_scope
    {profile : ScopedNegativePackage}
    (h : Certified profile) :
    profile.contact.observedContact = false ∧
      profile.occurrence.occurrenceWithinHorizon = false ∧
      profile.occurrence.occurrenceAfterHorizon = false := by
  exact ⟨ContactCoverageCertificate.certified_has_no_observed_contact
      h.contactClosed,
    h.occurrenceClosed.1.2.1,
    h.occurrenceClosed.2.2.2⟩

/-- A bounded null without closed-family force cannot be upgraded merely by a
separate point null on contact. -/
theorem point_null_plus_bounded_horizon_is_not_automatically_global
    {contact : ContactNullProfile} {occurrence : HorizonObservation}
    (hContact : ContactNullProfile.NoEvidencedContact contact)
    (hBounded : HorizonObservation.BoundedNull occurrence)
    (hOpen : occurrence.familyClosed = false) :
    ContactNullProfile.NoEvidencedContact contact ∧
      HorizonObservation.BoundedNull occurrence ∧
      ¬ HorizonObservation.ClosedFamilyNegativeCertificate occurrence := by
  exact ⟨hContact, hBounded,
    HorizonObservation.open_family_cannot_receive_closed_family_negative_certificate
      hOpen⟩

end ScopedNegativePackage

end FoundationsVII
