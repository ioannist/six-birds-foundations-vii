import FoundationsVII.Contact.All

/-!
# Join-entry normal form

The entry record is sufficient for retrospective verification of a declared
join attempt, but record completeness does not prove that a join exists.
-/

namespace FoundationsVII

inductive JoinContactState where
  | pending
  | witnessed
  | failed
  deriving Repr, DecidableEq, BEq, Inhabited

inductive JoinEntryStatus where
  | pending
  | failed
  | obstructed
  | completed
  deriving Repr, DecidableEq, BEq, Inhabited

structure JoinEntryRecord where
  entryId : RecordId
  parents : List TheoryId
  surface : ContactSurface
  contactState : JoinContactState
  contact : Option ContactWitness
  sources : SourceLedger
  budgets : BudgetLedger
  observers : List ObserverOccupancyRecord
  obstructions : List JoinObstructionKind
  status : JoinEntryStatus
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace JoinEntryRecord

def ParentComplete (record : JoinEntryRecord) : Prop :=
  2 ≤ record.parents.length

instance (record : JoinEntryRecord) : Decidable (ParentComplete record) := by
  unfold ParentComplete
  infer_instance

def SourceComplete (record : JoinEntryRecord) : Prop :=
  SourceLedger.WellFormed record.sources

instance (record : JoinEntryRecord) : Decidable (SourceComplete record) := by
  unfold SourceComplete
  infer_instance

def BudgetComplete (record : JoinEntryRecord) : Prop :=
  BudgetLedger.WellFormed record.budgets

instance (record : JoinEntryRecord) : Decidable (BudgetComplete record) := by
  unfold BudgetComplete
  infer_instance

def ContactConsistent (record : JoinEntryRecord) : Prop :=
  (record.contactState = JoinContactState.witnessed →
    record.contact.isSome = true) ∧
  (record.status = JoinEntryStatus.completed →
    record.contactState = JoinContactState.witnessed ∧
    record.obstructions = []) ∧
  (record.status = JoinEntryStatus.obstructed →
    record.obstructions ≠ [])

instance (record : JoinEntryRecord) : Decidable (ContactConsistent record) := by
  unfold ContactConsistent
  infer_instance

def WellFormed (record : JoinEntryRecord) : Prop :=
  ParentComplete record ∧
  ContactSurface.WellFormed record.surface ∧
  SourceComplete record ∧
  BudgetComplete record ∧
  ContactConsistent record ∧
  record.audit.entries ≠ []

instance (record : JoinEntryRecord) : Decidable (WellFormed record) := by
  unfold WellFormed
  infer_instance

def RetrospectivelyVerifiable (record : JoinEntryRecord) : Prop :=
  WellFormed record

theorem wellFormed_has_two_parents {record : JoinEntryRecord}
    (h : WellFormed record) : 2 ≤ record.parents.length := by
  rcases h with ⟨hParents, _, _, _, _, _⟩
  exact hParents

theorem wellFormed_has_typed_contact_surface {record : JoinEntryRecord}
    (h : WellFormed record) : ContactSurface.WellFormed record.surface := by
  rcases h with ⟨_, hSurface, _, _, _, _⟩
  exact hSurface

theorem wellFormed_has_source_ledger {record : JoinEntryRecord}
    (h : WellFormed record) : SourceLedger.WellFormed record.sources := by
  rcases h with ⟨_, _, hSource, _, _, _⟩
  exact hSource

theorem wellFormed_has_budget_ledger {record : JoinEntryRecord}
    (h : WellFormed record) : BudgetLedger.WellFormed record.budgets := by
  rcases h with ⟨_, _, _, hBudget, _, _⟩
  exact hBudget

theorem wellFormed_has_append_only_audit_surface {record : JoinEntryRecord}
    (h : WellFormed record) : record.audit.entries ≠ [] := by
  rcases h with ⟨_, _, _, _, _, hAudit⟩
  exact hAudit

theorem completed_has_witnessed_contact {record : JoinEntryRecord}
    (h : WellFormed record) (hStatus : record.status = JoinEntryStatus.completed) :
    record.contactState = JoinContactState.witnessed := by
  rcases h with ⟨_, _, _, _, hConsistent, _⟩
  exact (hConsistent.2.1 hStatus).1

theorem completed_has_no_recorded_obstruction {record : JoinEntryRecord}
    (h : WellFormed record) (hStatus : record.status = JoinEntryStatus.completed) :
    record.obstructions = [] := by
  rcases h with ⟨_, _, _, _, hConsistent, _⟩
  exact (hConsistent.2.1 hStatus).2

theorem obstructed_has_obstruction {record : JoinEntryRecord}
    (h : WellFormed record) (hStatus : record.status = JoinEntryStatus.obstructed) :
    record.obstructions ≠ [] := by
  rcases h with ⟨_, _, _, _, hConsistent, _⟩
  exact hConsistent.2.2 hStatus

theorem witnessed_state_has_contact {record : JoinEntryRecord}
    (h : WellFormed record)
    (hState : record.contactState = JoinContactState.witnessed) :
    record.contact.isSome = true := by
  rcases h with ⟨_, _, _, _, hConsistent, _⟩
  exact hConsistent.1 hState

theorem pending_ne_completed :
    JoinEntryStatus.pending ≠ JoinEntryStatus.completed := by decide

theorem failed_ne_completed :
    JoinEntryStatus.failed ≠ JoinEntryStatus.completed := by decide

theorem obstructed_ne_completed :
    JoinEntryStatus.obstructed ≠ JoinEntryStatus.completed := by decide

end JoinEntryRecord

/-- A compact omission-attack profile for retrospective join-entry checking.
The strong checker names every mandatory evidence class; the weak checker
looks only at the terminal status and therefore admits false positives. -/
structure JoinEntryFieldProfile where
  parents : Bool
  surface : Bool
  contact : Bool
  source : Bool
  license : Bool
  budget : Bool
  retention : Bool
  baseline : Bool
  temporalScope : Bool
  audit : Bool
  obstructionAbsent : Bool
  completedStatus : Bool
  deriving Repr, DecidableEq, BEq

namespace JoinEntryFieldProfile

def StronglyComplete (profile : JoinEntryFieldProfile) : Prop :=
  profile.parents = true ∧ profile.surface = true ∧
  profile.contact = true ∧ profile.source = true ∧
  profile.license = true ∧ profile.budget = true ∧
  profile.retention = true ∧ profile.baseline = true ∧
  profile.temporalScope = true ∧ profile.audit = true ∧
  profile.obstructionAbsent = true ∧ profile.completedStatus = true

instance (profile : JoinEntryFieldProfile) : Decidable (StronglyComplete profile) := by
  unfold StronglyComplete
  infer_instance

def WeaklyAccepted (profile : JoinEntryFieldProfile) : Prop :=
  profile.completedStatus = true

instance (profile : JoinEntryFieldProfile) : Decidable (WeaklyAccepted profile) := by
  unfold WeaklyAccepted
  infer_instance

private def sourceOmissionAttack : JoinEntryFieldProfile :=
  { parents := true, surface := true, contact := true, source := false,
    license := true, budget := true, retention := true, baseline := true,
    temporalScope := true, audit := true, obstructionAbsent := true,
    completedStatus := true }

private def contactOmissionAttack : JoinEntryFieldProfile :=
  { sourceOmissionAttack with source := true, contact := false }

private def budgetOmissionAttack : JoinEntryFieldProfile :=
  { sourceOmissionAttack with source := true, budget := false }

theorem weak_status_checker_has_source_false_positive :
    WeaklyAccepted sourceOmissionAttack ∧
    ¬ StronglyComplete sourceOmissionAttack := by decide

theorem weak_status_checker_has_contact_false_positive :
    WeaklyAccepted contactOmissionAttack ∧
    ¬ StronglyComplete contactOmissionAttack := by decide

theorem weak_status_checker_has_budget_false_positive :
    WeaklyAccepted budgetOmissionAttack ∧
    ¬ StronglyComplete budgetOmissionAttack := by decide

end JoinEntryFieldProfile

end FoundationsVII
