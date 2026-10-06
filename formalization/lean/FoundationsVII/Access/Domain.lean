import FoundationsVII.Core.Domain

/-!
# Accessible-domain normal form and access-coordinate separation

This module closes the structural part of VII-C001 and VII-C022.  The seven
operational coordinates are represented exactly and their admitted implication
spine is not strengthened by converse assumptions.
-/

namespace FoundationsVII

structure AccessStatusVector where
  expressible : Bool
  present : Bool
  exposed : Bool
  recoverable : Bool
  admissible : Bool
  reachable : Bool
  occurrent : Bool
  deriving Repr, DecidableEq, BEq

namespace DomainState

def statusVector (state : DomainState) : AccessStatusVector :=
  { expressible := state.expressible
    present := state.present
    exposed := state.exposed
    recoverable := state.recoverable
    admissible := state.admissible
    reachable := state.reachable
    occurrent := state.occurrent }

def withStatusVector (frame : DomainState)
    (status : AccessStatusVector) : DomainState :=
  { theoryId := frame.theoryId
    interfaceId := frame.interfaceId
    scopeId := frame.scopeId
    timestamp := frame.timestamp
    expressible := status.expressible
    present := status.present
    exposed := status.exposed
    recoverable := status.recoverable
    admissible := status.admissible
    reachable := status.reachable
    occurrent := status.occurrent
    audit := frame.audit }

def normalForm (state : DomainState) : DomainState :=
  withStatusVector state (statusVector state)

theorem statusVector_withStatusVector (frame : DomainState)
    (status : AccessStatusVector) :
    statusVector (withStatusVector frame status) = status := by
  cases status
  rfl

theorem withStatusVector_statusVector (state : DomainState) :
    withStatusVector state (statusVector state) = state := by
  cases state
  rfl

theorem normalForm_eq (state : DomainState) : normalForm state = state :=
  withStatusVector_statusVector state

theorem normalForm_idempotent (state : DomainState) :
    normalForm (normalForm state) = normalForm state := by
  rw [normalForm_eq]

/-- Equality of the seven operational coordinates, separated from carrier identity. -/
def SameOperationalStatus (left right : DomainState) : Prop :=
  statusVector left = statusVector right

/-- A scope change keeps the theory/interface fixed, changes scope, and retains audit. -/
structure ScopeChange (before after : DomainState) : Prop where
  sameTheory : before.theoryId = after.theoryId
  sameInterface : before.interfaceId = after.interfaceId
  changedScope : before.scopeId ≠ after.scopeId
  beforeAudit : before.audit.entries ≠ []
  afterAudit : after.audit.entries ≠ []

namespace ScopeChange

theorem preserves_theory_and_interface {before after : DomainState}
    (h : ScopeChange before after) :
    before.theoryId = after.theoryId ∧
      before.interfaceId = after.interfaceId :=
  ⟨h.sameTheory, h.sameInterface⟩

end ScopeChange

/-- Same expressibility/presence data, without identifying exposure. -/
def DeterminationEquivalent (left right : DomainState) : Prop :=
  left.expressible = right.expressible ∧ left.present = right.present

instance (left right : DomainState) :
    Decidable (DeterminationEquivalent left right) := by
  unfold DeterminationEquivalent
  infer_instance


def phase2AuditEntry : AuditEntry :=
  { auditId := 2001
    disposition := .accepted
    subject := "FVII-SCI-02 access witness"
    message := "closed finite witness"
    sourceLocation := "FoundationsVII.Access.Domain" }

def phase2Audit : AuditRecord := { entries := [phase2AuditEntry] }

def mkAccessState
    (expressible present exposed recoverable admissible reachable occurrent : Bool) :
    DomainState :=
  { theoryId := 7
    interfaceId := 2
    scopeId := 1
    timestamp := 0
    expressible := expressible
    present := present
    exposed := exposed
    recoverable := recoverable
    admissible := admissible
    reachable := reachable
    occurrent := occurrent
    audit := phase2Audit }

def expressibleOnlyWitness : DomainState :=
  mkAccessState true false false false false false false

def presentWithoutExposureWitness : DomainState :=
  mkAccessState true true false false false false false

def presentWithExposureWitness : DomainState :=
  mkAccessState true true true false false false false

def exposedWithoutRecoverabilityWitness : DomainState :=
  mkAccessState true true true false false false false

def recoverableWithoutAdmissibilityWitness : DomainState :=
  mkAccessState true true true true false false false

def admissibleWithoutRecoverabilityWitness : DomainState :=
  mkAccessState true true false false true false false

def admissibleWithoutReachabilityWitness : DomainState :=
  mkAccessState true true false false true false false

def reachableWithoutOccurrenceWitness : DomainState :=
  mkAccessState true true false false true true false

theorem expressibility_does_not_imply_presence :
    DomainState.Coherent expressibleOnlyWitness ∧
      expressibleOnlyWitness.expressible = true ∧
      expressibleOnlyWitness.present = false := by
  decide

theorem presence_does_not_imply_exposure :
    DomainState.Coherent presentWithoutExposureWitness ∧
      presentWithoutExposureWitness.present = true ∧
      presentWithoutExposureWitness.exposed = false := by
  decide

theorem same_determination_can_have_different_exposure :
    DeterminationEquivalent presentWithoutExposureWitness
      presentWithExposureWitness ∧
    presentWithoutExposureWitness.exposed ≠
      presentWithExposureWitness.exposed := by
  decide

theorem exposure_does_not_imply_recoverability :
    DomainState.Coherent exposedWithoutRecoverabilityWitness ∧
      exposedWithoutRecoverabilityWitness.exposed = true ∧
      exposedWithoutRecoverabilityWitness.recoverable = false := by
  decide

theorem recoverability_does_not_imply_admissibility :
    DomainState.Coherent recoverableWithoutAdmissibilityWitness ∧
      recoverableWithoutAdmissibilityWitness.recoverable = true ∧
      recoverableWithoutAdmissibilityWitness.admissible = false := by
  decide

theorem admissibility_does_not_imply_recoverability :
    DomainState.Coherent admissibleWithoutRecoverabilityWitness ∧
      admissibleWithoutRecoverabilityWitness.admissible = true ∧
      admissibleWithoutRecoverabilityWitness.recoverable = false := by
  decide

theorem admissibility_does_not_imply_reachability :
    DomainState.Coherent admissibleWithoutReachabilityWitness ∧
      admissibleWithoutReachabilityWitness.admissible = true ∧
      admissibleWithoutReachabilityWitness.reachable = false := by
  decide

theorem reachability_does_not_imply_occurrence :
    DomainState.Coherent reachableWithoutOccurrenceWitness ∧
      reachableWithoutOccurrenceWitness.reachable = true ∧
      reachableWithoutOccurrenceWitness.occurrent = false := by
  decide

theorem recoverability_and_admissibility_are_incomparable :
    (∃ state : DomainState,
      DomainState.Coherent state ∧ state.recoverable = true ∧
        state.admissible = false) ∧
    (∃ state : DomainState,
      DomainState.Coherent state ∧ state.admissible = true ∧
        state.recoverable = false) := by
  exact ⟨
    ⟨recoverableWithoutAdmissibilityWitness,
      recoverability_does_not_imply_admissibility⟩,
    ⟨admissibleWithoutRecoverabilityWitness,
      admissibility_does_not_imply_recoverability⟩⟩

structure AuxiliaryRecoveryCertificate where
  source : DomainState
  target : DomainState
  operationPresent : Bool
  adapterCertified : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace AuxiliaryRecoveryCertificate

def Valid (certificate : AuxiliaryRecoveryCertificate) : Prop :=
  certificate.source.theoryId = certificate.target.theoryId ∧
  certificate.source.scopeId = certificate.target.scopeId ∧
  certificate.source.exposed = true ∧
  certificate.target.recoverable = true ∧
  certificate.operationPresent = true ∧
  certificate.adapterCertified = true ∧
  certificate.audit.entries ≠ []

instance (certificate : AuxiliaryRecoveryCertificate) : Decidable (Valid certificate) := by
  unfold Valid
  infer_instance

def SpuriousRigidity (certificate : AuxiliaryRecoveryCertificate) : Prop :=
  certificate.target.recoverable = true ∧
  certificate.operationPresent = false

theorem valid_recovery_has_present_operation_and_adapter
    {certificate : AuxiliaryRecoveryCertificate}
    (h : Valid certificate) :
    certificate.operationPresent = true ∧
      certificate.adapterCertified = true :=
  ⟨h.2.2.2.2.1, h.2.2.2.2.2.1⟩

theorem absent_operation_blocks_valid_recovery
    {certificate : AuxiliaryRecoveryCertificate}
    (hAbsent : certificate.operationPresent = false) :
    ¬ Valid certificate := by
  intro hValid
  rw [hValid.2.2.2.2.1] at hAbsent
  exact Bool.noConfusion hAbsent

theorem spurious_rigidity_is_not_a_recovery_certificate
    {certificate : AuxiliaryRecoveryCertificate}
    (h : SpuriousRigidity certificate) :
    ¬ Valid certificate :=
  absent_operation_blocks_valid_recovery h.2

end AuxiliaryRecoveryCertificate

structure AccessRigid (left right : DomainState) : Prop where
  theory : left.theoryId = right.theoryId
  interface : left.interfaceId = right.interfaceId
  scope : left.scopeId = right.scopeId
  exposed : left.exposed = right.exposed
  recoverable : left.recoverable = right.recoverable
  admissible : left.admissible = right.admissible

namespace AccessRigid

theorem refl (state : DomainState) : AccessRigid state state := by
  exact ⟨rfl, rfl, rfl, rfl, rfl, rfl⟩

theorem symm {left right : DomainState}
    (h : AccessRigid left right) : AccessRigid right left := by
  exact ⟨h.theory.symm, h.interface.symm, h.scope.symm,
    h.exposed.symm, h.recoverable.symm, h.admissible.symm⟩

theorem trans {left middle right : DomainState}
    (h₁ : AccessRigid left middle) (h₂ : AccessRigid middle right) :
    AccessRigid left right := by
  exact ⟨h₁.theory.trans h₂.theory,
    h₁.interface.trans h₂.interface,
    h₁.scope.trans h₂.scope,
    h₁.exposed.trans h₂.exposed,
    h₁.recoverable.trans h₂.recoverable,
    h₁.admissible.trans h₂.admissible⟩

end AccessRigid
end DomainState
end FoundationsVII
