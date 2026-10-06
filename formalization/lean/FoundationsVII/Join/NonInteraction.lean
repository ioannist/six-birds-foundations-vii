import FoundationsVII.Residuals.All

/-!
# Coverage-qualified certified non-interaction

A point null is weaker than a certificate.  Certification records the covered
channel family, exact coverage, detector power, budget, horizon, closure, and
explicit escape routes.
-/

namespace FoundationsVII

structure ContactNullProfile where
  observedContact : Bool
  exactCoverage : Bool
  familyClosed : Bool
  detectorPower : Bool
  budgetSufficient : Bool
  horizonComplete : Bool
  deriving Repr, DecidableEq, BEq

namespace ContactNullProfile

def NoEvidencedContact (profile : ContactNullProfile) : Prop :=
  profile.observedContact = false

instance (profile : ContactNullProfile) : Decidable (NoEvidencedContact profile) := by
  unfold NoEvidencedContact
  infer_instance

def CertifiedNonInteraction (profile : ContactNullProfile) : Prop :=
  NoEvidencedContact profile ∧
  profile.exactCoverage = true ∧
  profile.familyClosed = true ∧
  profile.detectorPower = true ∧
  profile.budgetSufficient = true ∧
  profile.horizonComplete = true

instance (profile : ContactNullProfile) : Decidable (CertifiedNonInteraction profile) := by
  unfold CertifiedNonInteraction
  infer_instance

def openNull : ContactNullProfile :=
  { observedContact := false
    exactCoverage := false
    familyClosed := false
    detectorPower := false
    budgetSufficient := false
    horizonComplete := false }

def certifiedNull : ContactNullProfile :=
  { observedContact := false
    exactCoverage := true
    familyClosed := true
    detectorPower := true
    budgetSufficient := true
    horizonComplete := true }

theorem openNull_has_no_evidenced_contact : NoEvidencedContact openNull := rfl

theorem openNull_is_not_certified : ¬ CertifiedNonInteraction openNull := by decide

theorem certifiedNull_is_certified : CertifiedNonInteraction certifiedNull := by decide

theorem no_evidenced_contact_is_weaker_than_certified_noninteraction :
    ¬ (∀ profile : ContactNullProfile,
      NoEvidencedContact profile → CertifiedNonInteraction profile) := by
  intro h
  exact openNull_is_not_certified (h openNull openNull_has_no_evidenced_contact)

theorem certified_noninteraction_implies_no_evidenced_contact
    {profile : ContactNullProfile}
    (h : CertifiedNonInteraction profile) : NoEvidencedContact profile := h.1

end ContactNullProfile

structure ContactCoverageCertificate where
  certificateId : CertificateId
  coveredChannels : List InterfaceId
  exactCoverage : Bool
  familyClosed : Bool
  detectorPower : Bool
  budgetSufficient : Bool
  horizonComplete : Bool
  observedContact : Bool
  escapeRoutes : List String
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace ContactCoverageCertificate

def Certified (certificate : ContactCoverageCertificate) : Prop :=
  certificate.coveredChannels ≠ [] ∧
  certificate.exactCoverage = true ∧
  certificate.familyClosed = true ∧
  certificate.detectorPower = true ∧
  certificate.budgetSufficient = true ∧
  certificate.horizonComplete = true ∧
  certificate.observedContact = false ∧
  certificate.escapeRoutes ≠ [] ∧
  certificate.audit.entries ≠ []

instance (certificate : ContactCoverageCertificate) : Decidable (Certified certificate) := by
  unfold Certified
  infer_instance

theorem certified_has_no_observed_contact
    {certificate : ContactCoverageCertificate}
    (h : Certified certificate) : certificate.observedContact = false :=
  h.2.2.2.2.2.2.1

theorem certified_records_escape_routes
    {certificate : ContactCoverageCertificate}
    (h : Certified certificate) : certificate.escapeRoutes ≠ [] :=
  h.2.2.2.2.2.2.2.1

end ContactCoverageCertificate

structure DeclaredContactCase where
  channel : InterfaceId
  admissible : Bool
  observedContact : Bool
  deriving Repr, DecidableEq, BEq

namespace DeclaredContactCase

def ExhaustedNoContact (family : List DeclaredContactCase) : Prop :=
  ∀ case, case ∈ family → case.admissible = true → case.observedContact = false

def CoveredBy (family : List DeclaredContactCase) (case : DeclaredContactCase) : Prop :=
  case ∈ family

theorem exhaustive_declared_family_excludes_contact
    {family : List DeclaredContactCase}
    (hExhausted : ExhaustedNoContact family)
    {case : DeclaredContactCase}
    (hCovered : CoveredBy family case)
    (hAdmissible : case.admissible = true) :
    case.observedContact = false :=
  hExhausted case hCovered hAdmissible

theorem outside_family_is_an_explicit_escape
    {family : List DeclaredContactCase} {case : DeclaredContactCase}
    (hOutside : case ∉ family) : ¬ CoveredBy family case := hOutside

end DeclaredContactCase

end FoundationsVII
