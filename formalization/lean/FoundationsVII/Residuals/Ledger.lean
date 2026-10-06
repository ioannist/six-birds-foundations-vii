import FoundationsVII.Join.Retention

/-!
# Access and join residual ledgers

Inherited, dissolved, and newly generated residuals have separate typed
entries.  Append-only extension prevents silent deletion under scope changes.
-/

namespace FoundationsVII

inductive ResidualKind where
  | inaccessible
  | unadmitted
  | expired
  | failed
  | inherited
  | dissolved
  | crossTerm
  | newlyGenerated
  deriving Repr, DecidableEq, BEq, Inhabited

def allResidualKinds : List ResidualKind :=
  [.inaccessible, .unadmitted, .expired, .failed, .inherited, .dissolved,
   .crossTerm, .newlyGenerated]

theorem residualKind_mem_all (value : ResidualKind) : value ∈ allResidualKinds := by
  cases value <;> simp [allResidualKinds]

structure ResidualEntry where
  residualId : ObstructionId
  kind : ResidualKind
  sourceParents : List TheoryId
  sourceDescription : String
  active : Bool
  dischargeRoute : Option String
  crossTerm : Bool
  relabelOnly : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace ResidualEntry

def WellFormed (entry : ResidualEntry) : Prop :=
  entry.sourceParents ≠ [] ∧
  entry.sourceDescription ≠ "" ∧
  entry.audit.entries ≠ [] ∧
  (entry.kind = .crossTerm →
    entry.sourceParents.length ≥ 2 ∧
    entry.crossTerm = true ∧
    entry.relabelOnly = false) ∧
  (entry.kind = .dissolved → entry.active = false)

instance (entry : ResidualEntry) : Decidable (WellFormed entry) := by
  unfold WellFormed
  infer_instance

end ResidualEntry

structure ResidualLedger where
  entries : List ResidualEntry
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace ResidualLedger

def WellFormed (ledger : ResidualLedger) : Prop :=
  ledger.entries ≠ [] ∧
  (∀ entry, entry ∈ ledger.entries → ResidualEntry.WellFormed entry) ∧
  ledger.audit.entries ≠ []

instance (ledger : ResidualLedger) : Decidable (WellFormed ledger) := by
  unfold WellFormed
  infer_instance

def append (ledger : ResidualLedger) (entry : ResidualEntry)
    (auditEntry : AuditEntry) : ResidualLedger :=
  { entries := ledger.entries ++ [entry]
    audit := ledger.audit.append auditEntry }

def Extends (old newer : ResidualLedger) : Prop :=
  (∃ suffix : List ResidualEntry, newer.entries = old.entries ++ suffix) ∧
  AuditRecord.Extends old.audit newer.audit

theorem append_extends (ledger : ResidualLedger) (entry : ResidualEntry)
    (auditEntry : AuditEntry) : Extends ledger (append ledger entry auditEntry) := by
  exact ⟨⟨[entry], rfl⟩, AuditRecord.append_extends ledger.audit auditEntry⟩

theorem mem_of_extends {old newer : ResidualLedger}
    (h : Extends old newer) {entry : ResidualEntry}
    (hMem : entry ∈ old.entries) : entry ∈ newer.entries := by
  rcases h.1 with ⟨suffix, hSuffix⟩
  rw [hSuffix]
  simp only [List.mem_append]
  exact Or.inl hMem

theorem no_silent_residual_deletion_under_scope_change
    {old newer : ResidualLedger} (h : Extends old newer)
    {entry : ResidualEntry} (hMem : entry ∈ old.entries) :
    entry ∈ newer.entries := mem_of_extends h hMem

end ResidualLedger

structure CrossTermNeedle where
  entry : ResidualEntry
  absentFromLeftParent : Bool
  absentFromRightParent : Bool
  generatedByJoin : Bool
  jointlyDetectable : Bool
  deriving Repr, DecidableEq, BEq

namespace CrossTermNeedle

def Valid (needle : CrossTermNeedle) : Prop :=
  ResidualEntry.WellFormed needle.entry ∧
  needle.entry.kind = .crossTerm ∧
  needle.absentFromLeftParent = true ∧
  needle.absentFromRightParent = true ∧
  needle.generatedByJoin = true ∧
  needle.jointlyDetectable = true

instance (needle : CrossTermNeedle) : Decidable (Valid needle) := by
  unfold Valid
  infer_instance

end CrossTermNeedle

structure ResidualTransition where
  before : ResidualLedger
  after : ResidualLedger
  inheritedIds : List ObstructionId
  dissolvedIds : List ObstructionId
  createdIds : List ObstructionId
  sourceAccounted : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace ResidualTransition

def WellFormed (transition : ResidualTransition) : Prop :=
  ResidualLedger.WellFormed transition.before ∧
  ResidualLedger.WellFormed transition.after ∧
  transition.sourceAccounted = true ∧
  transition.audit.entries ≠ []

instance (transition : ResidualTransition) : Decidable (WellFormed transition) := by
  unfold WellFormed
  infer_instance

end ResidualTransition

private def inheritedResidual : ResidualEntry :=
  { residualId := 1
    kind := .inherited
    sourceParents := [1]
    sourceDescription := "parent access residual"
    active := true
    dischargeRoute := none
    crossTerm := false
    relabelOnly := false
    audit := phase3Audit }

private def dissolvedResidual : ResidualEntry :=
  { residualId := 2
    kind := .dissolved
    sourceParents := [2]
    sourceDescription := "parent obstruction discharged by peer access"
    active := false
    dischargeRoute := some "peer join"
    crossTerm := false
    relabelOnly := false
    audit := phase3Audit }

private def crossTermResidual : ResidualEntry :=
  { residualId := 3
    kind := .crossTerm
    sourceParents := [1, 2]
    sourceDescription := "composite-only cross-parent needle"
    active := true
    dischargeRoute := none
    crossTerm := true
    relabelOnly := false
    audit := phase3Audit }

private def relabelResidual : ResidualEntry :=
  { crossTermResidual with
    residualId := 4
    sourceDescription := "presentation-only relabel"
    relabelOnly := true }

private def joinCreatedNeedle : CrossTermNeedle :=
  { entry := crossTermResidual
    absentFromLeftParent := true
    absentFromRightParent := true
    generatedByJoin := true
    jointlyDetectable := true }

private def beforeResidualLedger : ResidualLedger :=
  { entries := [inheritedResidual, dissolvedResidual]
    audit := phase3Audit }

private def afterResidualLedger : ResidualLedger :=
  { entries := [inheritedResidual, dissolvedResidual, crossTermResidual]
    audit := phase3Audit }

private def residualTransitionWitness : ResidualTransition :=
  { before := beforeResidualLedger
    after := afterResidualLedger
    inheritedIds := [1]
    dissolvedIds := [2]
    createdIds := [3]
    sourceAccounted := true
    audit := phase3Audit }

theorem constructive_join_created_cross_term_needle :
    CrossTermNeedle.Valid joinCreatedNeedle := by decide

theorem relabeling_does_not_count_as_new_cross_term :
    ¬ ResidualEntry.WellFormed relabelResidual := by decide

theorem join_can_dissolve_and_create_residuals_simultaneously :
    ResidualTransition.WellFormed residualTransitionWitness ∧
    residualTransitionWitness.dissolvedIds = [2] ∧
    residualTransitionWitness.createdIds = [3] := by
  simp [ResidualTransition.WellFormed, residualTransitionWitness,
    ResidualLedger.WellFormed, beforeResidualLedger, afterResidualLedger,
    ResidualEntry.WellFormed, inheritedResidual, dissolvedResidual,
    crossTermResidual, phase3Audit, phase3AuditEntry]

theorem joining_is_not_monotonically_obstruction_reducing :
    ResidualLedger.WellFormed beforeResidualLedger ∧
    ResidualLedger.WellFormed afterResidualLedger ∧
    crossTermResidual ∈ afterResidualLedger.entries ∧
    crossTermResidual ∉ beforeResidualLedger.entries := by
  simp [ResidualLedger.WellFormed, beforeResidualLedger,
    afterResidualLedger, ResidualEntry.WellFormed, inheritedResidual,
    dissolvedResidual, crossTermResidual, phase3Audit, phase3AuditEntry]

end FoundationsVII
