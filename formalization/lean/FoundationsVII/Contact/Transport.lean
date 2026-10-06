import FoundationsVII.Core.All

/-!
# Typed contact and peer transport

Compatibility, witnessed contact, transport, composite formation, and strict
join are distinct. A transport record preserves destination ownership and
source provenance without manufacturing a joint object.
-/

namespace FoundationsVII

/-- Shared accepted audit witness for concrete FVII-SCI-03 finite controls. -/
def phase3AuditEntry : AuditEntry :=
  { auditId := 3001
    disposition := .accepted
    subject := "FVII-SCI-03 contact/join witness"
    message := "typed finite science witness"
    sourceLocation := "FoundationsVII.Contact.Transport" }

def phase3Audit : AuditRecord := { entries := [phase3AuditEntry] }

inductive ContactMode where
  | rendezvous
  | mediation
  | sequential
  | sharedCarrier
  | sharedBudget
  deriving Repr, DecidableEq, BEq, Inhabited

def allContactModes : List ContactMode :=
  [.rendezvous, .mediation, .sequential, .sharedCarrier, .sharedBudget]

theorem contactMode_mem_all (mode : ContactMode) : mode ∈ allContactModes := by
  cases mode <;> simp [allContactModes]

structure ContactChannelEvidence where
  directEndpointMatch : Bool
  mediatorCertified : Bool
  sequenceRecorded : Bool
  sharedCarrierCertified : Bool
  sharedBudgetCertified : Bool
  deriving Repr, DecidableEq, BEq

namespace ContactChannelEvidence

def Licenses (evidence : ContactChannelEvidence) (mode : ContactMode) : Prop :=
  match mode with
  | .rendezvous => evidence.directEndpointMatch = true
  | .mediation => evidence.mediatorCertified = true
  | .sequential => evidence.sequenceRecorded = true
  | .sharedCarrier => evidence.sharedCarrierCertified = true
  | .sharedBudget => evidence.sharedBudgetCertified = true

instance (evidence : ContactChannelEvidence) (mode : ContactMode) :
    Decidable (Licenses evidence mode) := by
  unfold Licenses
  cases mode <;> infer_instance

theorem rendezvous_licensed {evidence : ContactChannelEvidence}
    (h : evidence.directEndpointMatch = true) :
    Licenses evidence .rendezvous := h

theorem mediation_licensed {evidence : ContactChannelEvidence}
    (h : evidence.mediatorCertified = true) :
    Licenses evidence .mediation := h

theorem sequential_licensed {evidence : ContactChannelEvidence}
    (h : evidence.sequenceRecorded = true) :
    Licenses evidence .sequential := h

theorem shared_carrier_licensed {evidence : ContactChannelEvidence}
    (h : evidence.sharedCarrierCertified = true) :
    Licenses evidence .sharedCarrier := h

theorem shared_budget_licensed {evidence : ContactChannelEvidence}
    (h : evidence.sharedBudgetCertified = true) :
    Licenses evidence .sharedBudget := h

end ContactChannelEvidence

structure ContactProfile where
  compatible : Bool
  witnessed : Bool
  transported : Bool
  composite : Bool
  strictJoin : Bool
  deriving Repr, DecidableEq, BEq

namespace ContactProfile

def OperationallyCoherent (profile : ContactProfile) : Prop :=
  (profile.transported = true → profile.witnessed = true) ∧
  (profile.composite = true → profile.witnessed = true) ∧
  (profile.strictJoin = true → profile.composite = true)

instance (profile : ContactProfile) : Decidable (OperationallyCoherent profile) := by
  unfold OperationallyCoherent
  infer_instance

def compatibleWithoutContact : ContactProfile :=
  { compatible := true, witnessed := false, transported := false,
    composite := false, strictJoin := false }

def contactWithoutComposite : ContactProfile :=
  { compatible := true, witnessed := true, transported := true,
    composite := false, strictJoin := false }

theorem compatibleWithoutContact_coherent :
    OperationallyCoherent compatibleWithoutContact := by decide

theorem contactWithoutComposite_coherent :
    OperationallyCoherent contactWithoutComposite := by decide

theorem compatibility_does_not_imply_evidenced_contact :
    ¬ (∀ profile : ContactProfile,
      OperationallyCoherent profile →
      profile.compatible = true → profile.witnessed = true) := by
  intro h
  have hw := h compatibleWithoutContact compatibleWithoutContact_coherent rfl
  simp [compatibleWithoutContact] at hw

theorem evidenced_contact_does_not_imply_composite :
    ¬ (∀ profile : ContactProfile,
      OperationallyCoherent profile →
      profile.witnessed = true → profile.composite = true) := by
  intro h
  have hw := h contactWithoutComposite contactWithoutComposite_coherent rfl
  simp [contactWithoutComposite] at hw

end ContactProfile

structure PeerTransport where
  transportId : RecordId
  mode : ContactMode
  channel : ContactChannelEvidence
  contact : ContactWitness
  payloadSource : SourceId
  destinationTheory : TheoryId
  payloadCertified : Bool
  destinationOwned : Bool
  provenancePreserved : Bool
  formsComposite : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace PeerTransport

def WellFormed (transport : PeerTransport) : Prop :=
  ContactWitness.WellFormed transport.contact ∧
  ContactChannelEvidence.Licenses transport.channel transport.mode ∧
  transport.payloadCertified = true ∧
  transport.destinationOwned = true ∧
  transport.provenancePreserved = true ∧
  transport.contact.sourceId = transport.payloadSource ∧
  transport.contact.surface.rightTheory = transport.destinationTheory ∧
  transport.audit.entries ≠ []

instance (transport : PeerTransport) : Decidable (WellFormed transport) := by
  unfold WellFormed
  infer_instance

def WithoutJoin (transport : PeerTransport) : Prop :=
  WellFormed transport ∧ transport.formsComposite = false

instance (transport : PeerTransport) : Decidable (WithoutJoin transport) := by
  unfold WithoutJoin
  infer_instance

def CertifiedContentAvailable (transport : PeerTransport) : Prop :=
  WellFormed transport ∧ transport.payloadCertified = true

theorem wellFormed_preserves_destination_ownership
    {transport : PeerTransport} (h : WellFormed transport) :
    transport.destinationOwned = true := h.2.2.2.1

theorem wellFormed_preserves_provenance
    {transport : PeerTransport} (h : WellFormed transport) :
    transport.provenancePreserved = true := h.2.2.2.2.1

theorem wellFormed_preserves_payload_source
    {transport : PeerTransport} (h : WellFormed transport) :
    transport.contact.sourceId = transport.payloadSource := h.2.2.2.2.2.1

theorem wellFormed_targets_declared_destination
    {transport : PeerTransport} (h : WellFormed transport) :
    transport.contact.surface.rightTheory = transport.destinationTheory :=
  h.2.2.2.2.2.2.1

theorem withoutJoin_is_certified_transport
    {transport : PeerTransport} (h : WithoutJoin transport) :
    CertifiedContentAvailable transport := ⟨h.1, h.1.2.2.1⟩

theorem withoutJoin_does_not_form_composite
    {transport : PeerTransport} (h : WithoutJoin transport) :
    transport.formsComposite = false := h.2

end PeerTransport

private def phase3Surface : ContactSurface :=
  { leftTheory := 1, rightTheory := 2, leftInterface := 11,
    rightInterface := 22, crossingRelation := "typed payload crossing",
    admissible := true }

private def phase3Contact : ContactWitness :=
  { surface := phase3Surface, eventId := 3002, sourceId := 700,
    crossed := true, payloadDescription := "certified peer payload",
    audit := phase3Audit }

private def allModeEvidence : ContactChannelEvidence :=
  { directEndpointMatch := true, mediatorCertified := true,
    sequenceRecorded := true, sharedCarrierCertified := true,
    sharedBudgetCertified := true }

private def transportFor (mode : ContactMode) : PeerTransport :=
  { transportId := 3003, mode := mode, channel := allModeEvidence,
    contact := phase3Contact, payloadSource := 700, destinationTheory := 2,
    payloadCertified := true, destinationOwned := true,
    provenancePreserved := true, formsComposite := false,
    audit := phase3Audit }

private theorem transportFor_wellFormed (mode : ContactMode) :
    PeerTransport.WellFormed (transportFor mode) := by
  cases mode <;> decide

theorem peer_contact_can_transport_without_join :
    ∀ mode : ContactMode, PeerTransport.WithoutJoin (transportFor mode) := by
  intro mode
  exact ⟨transportFor_wellFormed mode, rfl⟩

theorem rendezvous_special_case_exists :
    ∃ transport : PeerTransport,
      PeerTransport.WithoutJoin transport ∧ transport.mode = .rendezvous :=
  ⟨transportFor .rendezvous, peer_contact_can_transport_without_join .rendezvous, rfl⟩

theorem mediation_special_case_exists :
    ∃ transport : PeerTransport,
      PeerTransport.WithoutJoin transport ∧ transport.mode = .mediation :=
  ⟨transportFor .mediation, peer_contact_can_transport_without_join .mediation, rfl⟩

theorem sequential_special_case_exists :
    ∃ transport : PeerTransport,
      PeerTransport.WithoutJoin transport ∧ transport.mode = .sequential :=
  ⟨transportFor .sequential, peer_contact_can_transport_without_join .sequential, rfl⟩

theorem shared_carrier_special_case_exists :
    ∃ transport : PeerTransport,
      PeerTransport.WithoutJoin transport ∧ transport.mode = .sharedCarrier :=
  ⟨transportFor .sharedCarrier, peer_contact_can_transport_without_join .sharedCarrier, rfl⟩

theorem shared_budget_special_case_exists :
    ∃ transport : PeerTransport,
      PeerTransport.WithoutJoin transport ∧ transport.mode = .sharedBudget :=
  ⟨transportFor .sharedBudget, peer_contact_can_transport_without_join .sharedBudget, rfl⟩

/-- DP01: contact is primitive evidence; mediation is one typed constructor. -/
theorem contact_surface_primitive_scoped_ruling :
    ContactSurface.WellFormed phase3Surface ∧
    ContactWitness.WellFormed phase3Contact := by decide

end FoundationsVII
