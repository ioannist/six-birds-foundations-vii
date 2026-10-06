import FoundationsVII.Access.Transitions

/-!
# Bootstrap obstruction and neutral provisioning

The no-go is explicitly scoped to a declared closed transition family.  It
forbids a lawful first extension only when neither an admitted seed nor a
reachable generator is available.  External neutral provision and reachable
generation are positive escape theorems.
-/

namespace FoundationsVII

structure AdmissionRegime where
  closedFamily : Bool
  admittedSeeds : List SourceId
  reachableGenerators : List TransitionId
  externallyProvisionedExtensions : List TransitionId
  permittedFirstExtensions : List TransitionId
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace AdmissionRegime

def WellFormed (regime : AdmissionRegime) : Prop :=
  regime.permittedFirstExtensions.Nodup ∧
  regime.admittedSeeds.Nodup ∧
  regime.reachableGenerators.Nodup ∧
  regime.externallyProvisionedExtensions.Nodup ∧
  regime.audit.entries ≠ []

instance (regime : AdmissionRegime) : Decidable (WellFormed regime) := by
  unfold WellFormed
  infer_instance

def HasAdmittedSeed (regime : AdmissionRegime) : Prop :=
  regime.admittedSeeds ≠ []

def HasReachableGenerator (regime : AdmissionRegime) : Prop :=
  regime.reachableGenerators ≠ []

def HasOpenExternalProvision (regime : AdmissionRegime)
    (transitionId : TransitionId) : Prop :=
  regime.closedFamily = false ∧
  transitionId ∈ regime.externallyProvisionedExtensions

def FirstExtensionAuthorized (regime : AdmissionRegime)
    (transitionId : TransitionId) : Prop :=
  HasAdmittedSeed regime ∨
  HasReachableGenerator regime ∨
  HasOpenExternalProvision regime transitionId

def LawfulFirstExtension (regime : AdmissionRegime)
    (transitionId : TransitionId) : Prop :=
  transitionId ∈ regime.permittedFirstExtensions ∧
  FirstExtensionAuthorized regime transitionId

def BootstrapNoGoApplies (regime : AdmissionRegime) : Prop :=
  regime.closedFamily = true ∧
  ¬ HasAdmittedSeed regime ∧
  ¬ HasReachableGenerator regime

theorem no_first_extension_without_seed_or_reachable_generator
    {regime : AdmissionRegime}
    (hClosed : regime.closedFamily = true)
    (hNoSeed : ¬ HasAdmittedSeed regime)
    (hNoGenerator : ¬ HasReachableGenerator regime)
    (transitionId : TransitionId) :
    ¬ LawfulFirstExtension regime transitionId := by
  intro hLawful
  rcases hLawful.2 with hSeed | hGenerator | hExternal
  · exact hNoSeed hSeed
  · exact hNoGenerator hGenerator
  · have hImpossible : regime.closedFamily = false := hExternal.1
    rw [hClosed] at hImpossible
    exact Bool.noConfusion hImpossible

theorem bootstrap_no_go_applies_implies_no_first_extension
    {regime : AdmissionRegime}
    (h : BootstrapNoGoApplies regime)
    (transitionId : TransitionId) :
    ¬ LawfulFirstExtension regime transitionId :=
  no_first_extension_without_seed_or_reachable_generator
    h.1 h.2.1 h.2.2 transitionId

theorem admitted_seed_authorizes_first_extension
    {regime : AdmissionRegime} {transitionId : TransitionId}
    (hPermitted : transitionId ∈ regime.permittedFirstExtensions)
    (hSeed : HasAdmittedSeed regime) :
    LawfulFirstExtension regime transitionId :=
  ⟨hPermitted, Or.inl hSeed⟩

theorem reachable_generator_authorizes_first_extension
    {regime : AdmissionRegime} {transitionId : TransitionId}
    (hPermitted : transitionId ∈ regime.permittedFirstExtensions)
    (hGenerator : HasReachableGenerator regime) :
    LawfulFirstExtension regime transitionId :=
  ⟨hPermitted, Or.inr (Or.inl hGenerator)⟩

theorem open_external_provision_authorizes_first_extension
    {regime : AdmissionRegime} {transitionId : TransitionId}
    (hPermitted : transitionId ∈ regime.permittedFirstExtensions)
    (hOpen : regime.closedFamily = false)
    (hProvisioned : transitionId ∈ regime.externallyProvisionedExtensions) :
    LawfulFirstExtension regime transitionId :=
  ⟨hPermitted, Or.inr (Or.inr ⟨hOpen, hProvisioned⟩)⟩

theorem open_family_is_not_covered_by_closed_bootstrap_hypotheses
    {regime : AdmissionRegime}
    (hOpen : regime.closedFamily = false) :
    ¬ BootstrapNoGoApplies regime := by
  intro hApplies
  rw [hApplies.1] at hOpen
  exact Bool.noConfusion hOpen

end AdmissionRegime

structure NeutralProvisioningCertificate where
  certificateId : CertificateId
  source : SourceEntry
  commitment : ProspectiveCommitment
  taskBlind : Bool
  outcomeIndependent : Bool
  symmetryCertified : Bool
  controlMatched : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

structure NeutralProvisioningAt
    (certificate : NeutralProvisioningCertificate)
    (observedAt : Timestamp) : Prop where
  sourceExternal : certificate.source.kind = SourceKind.externalProvision
  sourceAccepted : certificate.source.disposition = AuditDisposition.accepted
  sourceNotSystemGenerated : certificate.source.generatedBySystem = false
  commitmentAccepted :
    certificate.commitment.disposition = AuditDisposition.accepted
  commitmentWellFormed :
    ProspectiveCommitment.WellFormed certificate.commitment
  registeredBeforeObservation :
    certificate.commitment.registeredAt < observedAt
  activeAtObservation :
    certificate.commitment.validFrom ≤ observedAt ∧
      observedAt ≤ certificate.commitment.expiresAt
  taskBlind : certificate.taskBlind = true
  outcomeIndependent : certificate.outcomeIndependent = true
  symmetryCertified : certificate.symmetryCertified = true
  controlMatched : certificate.controlMatched = true
  auditPresent : certificate.audit.entries ≠ []

namespace NeutralProvisioningCertificate

def ProvidesSeedFor (certificate : NeutralProvisioningCertificate)
    (regime : AdmissionRegime) : Prop :=
  certificate.source.sourceId ∈ regime.admittedSeeds

theorem neutral_provisioning_authorizes_first_extension
    {certificate : NeutralProvisioningCertificate}
    {regime : AdmissionRegime} {observedAt : Timestamp}
    {transitionId : TransitionId}
    (_hNeutral : NeutralProvisioningAt certificate observedAt)
    (hProvides : ProvidesSeedFor certificate regime)
    (hPermitted : transitionId ∈ regime.permittedFirstExtensions) :
    AdmissionRegime.LawfulFirstExtension regime transitionId := by
  apply AdmissionRegime.admitted_seed_authorizes_first_extension hPermitted
  exact List.ne_nil_of_mem hProvides

theorem retrospective_stocking_cannot_earn_neutral_credit
    {certificate : NeutralProvisioningCertificate}
    {observedAt : Timestamp}
    (hRetrospective : observedAt ≤ certificate.commitment.registeredAt) :
    ¬ NeutralProvisioningAt certificate observedAt := by
  intro hNeutral
  exact (Nat.not_lt_of_ge hRetrospective)
    hNeutral.registeredBeforeObservation

theorem system_generated_source_cannot_earn_neutral_credit
    {certificate : NeutralProvisioningCertificate}
    {observedAt : Timestamp}
    (hGenerated : certificate.source.generatedBySystem = true) :
    ¬ NeutralProvisioningAt certificate observedAt := by
  intro hNeutral
  have hFalse : true = false := by
    calc
      true = certificate.source.generatedBySystem := hGenerated.symm
      _ = false := hNeutral.sourceNotSystemGenerated
  exact Bool.noConfusion hFalse

theorem source_laundering_through_system_generation_fails
    {certificate : NeutralProvisioningCertificate}
    {observedAt : Timestamp}
    (hLaundered : certificate.source.generatedBySystem = true) :
    ¬ NeutralProvisioningAt certificate observedAt :=
  system_generated_source_cannot_earn_neutral_credit hLaundered

end NeutralProvisioningCertificate

end FoundationsVII
