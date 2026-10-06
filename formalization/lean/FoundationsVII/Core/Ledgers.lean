import FoundationsVII.Core.Audit

/-!
# Source and budget ledgers

The authoritative data are append-only entry lists.  Every projection is a
definition over that list, so no duplicated counter can silently drift.
-/

namespace FoundationsVII

structure SourceEntry where
  sourceId : SourceId
  kind : SourceKind
  parentSources : List SourceId
  generatedBySystem : Bool
  inScope : Bool
  disposition : AuditDisposition
  deriving Repr, DecidableEq, BEq

namespace SourceEntry

def WellFormed (entry : SourceEntry) : Prop :=
  entry.sourceId ∉ entry.parentSources

instance (entry : SourceEntry) : Decidable (WellFormed entry) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (entry : SourceEntry)
    (hNoSelfParent : entry.sourceId ∉ entry.parentSources) : WellFormed entry :=
  hNoSelfParent

end SourceEntry


structure SourceLedger where
  entries : List SourceEntry
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace SourceLedger

/-- Phase-1 structural validity; ancestry closure and acyclicity are later laws. -/
def WellFormed (ledger : SourceLedger) : Prop :=
  ledger.entries ≠ [] ∧
  (ledger.entries.map SourceEntry.sourceId).Nodup ∧
  (∀ entry, entry ∈ ledger.entries → SourceEntry.WellFormed entry) ∧
  ledger.audit.entries ≠ []

instance (ledger : SourceLedger) : Decidable (WellFormed ledger) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (ledger : SourceLedger)
    (hEntries : ledger.entries ≠ [])
    (hUnique : (ledger.entries.map SourceEntry.sourceId).Nodup)
    (hEntry : ∀ entry, entry ∈ ledger.entries → SourceEntry.WellFormed entry)
    (hAudit : ledger.audit.entries ≠ []) : WellFormed ledger := by
  exact ⟨hEntries, hUnique, hEntry, hAudit⟩

theorem entry_wellFormed {ledger : SourceLedger}
    (hLedger : WellFormed ledger) {entry : SourceEntry}
    (hMem : entry ∈ ledger.entries) : SourceEntry.WellFormed entry :=
  hLedger.2.2.1 entry hMem

def sourceIds (ledger : SourceLedger) : List SourceId :=
  ledger.entries.map SourceEntry.sourceId

def sourceKinds (ledger : SourceLedger) : List SourceKind :=
  ledger.entries.map SourceEntry.kind

def append (ledger : SourceLedger) (entry : SourceEntry)
    (auditEntry : AuditEntry) : SourceLedger :=
  { entries := ledger.entries ++ [entry]
    audit := ledger.audit.append auditEntry }

def EntryExtends (old newer : SourceLedger) : Prop :=
  ∃ suffix : List SourceEntry, newer.entries = old.entries ++ suffix

def Extends (old newer : SourceLedger) : Prop :=
  EntryExtends old newer ∧ AuditRecord.Extends old.audit newer.audit

theorem sourceIds_projection_consistent (ledger : SourceLedger) :
    sourceIds ledger = ledger.entries.map SourceEntry.sourceId := rfl

theorem sourceKinds_projection_consistent (ledger : SourceLedger) :
    sourceKinds ledger = ledger.entries.map SourceEntry.kind := rfl

theorem append_sourceIds (ledger : SourceLedger) (entry : SourceEntry)
    (auditEntry : AuditEntry) :
    sourceIds (append ledger entry auditEntry) =
      sourceIds ledger ++ [entry.sourceId] := by
  simp [sourceIds, append]

theorem append_sourceKinds (ledger : SourceLedger) (entry : SourceEntry)
    (auditEntry : AuditEntry) :
    sourceKinds (append ledger entry auditEntry) =
      sourceKinds ledger ++ [entry.kind] := by
  simp [sourceKinds, append]

theorem append_extends (ledger : SourceLedger) (entry : SourceEntry)
    (auditEntry : AuditEntry) : Extends ledger (append ledger entry auditEntry) := by
  exact ⟨⟨[entry], rfl⟩, AuditRecord.append_extends ledger.audit auditEntry⟩

theorem mem_of_extends {old newer : SourceLedger}
    (h : Extends old newer) {entry : SourceEntry}
    (hmem : entry ∈ old.entries) : entry ∈ newer.entries := by
  rcases h.1 with ⟨suffix, hsuffix⟩
  rw [hsuffix]
  simp only [List.mem_append]
  exact Or.inl hmem

theorem audit_mem_of_extends {old newer : SourceLedger}
    (h : Extends old newer) {entry : AuditEntry}
    (hmem : entry ∈ old.audit.entries) : entry ∈ newer.audit.entries :=
  AuditRecord.mem_of_extends h.2 hmem

theorem failed_source_not_silently_deleted {old newer : SourceLedger}
    (h : Extends old newer) {entry : SourceEntry}
    (hmem : entry ∈ old.entries)
    (_ : entry.disposition = AuditDisposition.failed) :
    entry ∈ newer.entries := mem_of_extends h hmem

theorem revoked_source_not_silently_deleted {old newer : SourceLedger}
    (h : Extends old newer) {entry : SourceEntry}
    (hmem : entry ∈ old.entries)
    (_ : entry.disposition = AuditDisposition.revoked) :
    entry ∈ newer.entries := mem_of_extends h hmem

theorem refunded_source_not_silently_deleted {old newer : SourceLedger}
    (h : Extends old newer) {entry : SourceEntry}
    (hmem : entry ∈ old.entries)
    (_ : entry.disposition = AuditDisposition.refunded) :
    entry ∈ newer.entries := mem_of_extends h hmem

theorem withdrawn_source_not_silently_deleted {old newer : SourceLedger}
    (h : Extends old newer) {entry : SourceEntry}
    (hmem : entry ∈ old.entries)
    (_ : entry.disposition = AuditDisposition.withdrawn) :
    entry ∈ newer.entries := mem_of_extends h hmem

theorem audit_extends_of_ledger_extends {old newer : SourceLedger}
    (h : Extends old newer) : AuditRecord.Extends old.audit newer.audit := h.2

end SourceLedger

inductive BudgetEntryKind where
  | credit
  | debit
  | occupancy
  | crossCost
  | residual
  | refund
  deriving Repr, DecidableEq, BEq, Inhabited

structure BudgetEntry where
  resourceId : ResourceId
  kind : BudgetEntryKind
  allocated : Cost
  spent : Cost
  refunded : Cost
  occupied : Cost
  disposition : AuditDisposition
  deriving Repr, DecidableEq, BEq

namespace BudgetEntry

def EntryFeasible (entry : BudgetEntry) : Prop :=
  entry.spent + entry.occupied ≤ entry.allocated + entry.refunded

instance (entry : BudgetEntry) : Decidable (EntryFeasible entry) := by
  unfold EntryFeasible
  infer_instance


def WellFormed (entry : BudgetEntry) : Prop :=
  entry.spent ≤ entry.allocated ∧
  entry.refunded ≤ entry.allocated ∧
  entry.occupied ≤ entry.allocated ∧
  EntryFeasible entry

instance (entry : BudgetEntry) : Decidable (WellFormed entry) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (entry : BudgetEntry)
    (hSpent : entry.spent ≤ entry.allocated)
    (hRefunded : entry.refunded ≤ entry.allocated)
    (hOccupied : entry.occupied ≤ entry.allocated)
    (hFeasible : EntryFeasible entry) : WellFormed entry := by
  exact ⟨hSpent, hRefunded, hOccupied, hFeasible⟩

theorem entryFeasible_of_wellFormed {entry : BudgetEntry}
    (h : WellFormed entry) : EntryFeasible entry := h.2.2.2

end BudgetEntry

structure BudgetLedger where
  entries : List BudgetEntry
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace BudgetLedger

/-- Phase-1 structural validity; conservation laws are deliberately later. -/
def WellFormed (ledger : BudgetLedger) : Prop :=
  ledger.entries ≠ [] ∧
  (∀ entry, entry ∈ ledger.entries → BudgetEntry.WellFormed entry) ∧
  ledger.audit.entries ≠ []

instance (ledger : BudgetLedger) : Decidable (WellFormed ledger) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (ledger : BudgetLedger)
    (hEntries : ledger.entries ≠ [])
    (hEntry : ∀ entry, entry ∈ ledger.entries → BudgetEntry.WellFormed entry)
    (hAudit : ledger.audit.entries ≠ []) : WellFormed ledger := by
  exact ⟨hEntries, hEntry, hAudit⟩

theorem entry_wellFormed {ledger : BudgetLedger}
    (hLedger : WellFormed ledger) {entry : BudgetEntry}
    (hMem : entry ∈ ledger.entries) : BudgetEntry.WellFormed entry :=
  hLedger.2.1 entry hMem

def resourceIds (ledger : BudgetLedger) : List ResourceId :=
  ledger.entries.map BudgetEntry.resourceId

def allocations (ledger : BudgetLedger) : List Cost :=
  ledger.entries.map BudgetEntry.allocated

def spends (ledger : BudgetLedger) : List Cost :=
  ledger.entries.map BudgetEntry.spent

def refunds (ledger : BudgetLedger) : List Cost :=
  ledger.entries.map BudgetEntry.refunded

def occupancies (ledger : BudgetLedger) : List Cost :=
  ledger.entries.map BudgetEntry.occupied

def append (ledger : BudgetLedger) (entry : BudgetEntry)
    (auditEntry : AuditEntry) : BudgetLedger :=
  { entries := ledger.entries ++ [entry]
    audit := ledger.audit.append auditEntry }

def EntryExtends (old newer : BudgetLedger) : Prop :=
  ∃ suffix : List BudgetEntry, newer.entries = old.entries ++ suffix

def Extends (old newer : BudgetLedger) : Prop :=
  EntryExtends old newer ∧ AuditRecord.Extends old.audit newer.audit

theorem resourceIds_projection_consistent (ledger : BudgetLedger) :
    resourceIds ledger = ledger.entries.map BudgetEntry.resourceId := rfl

theorem allocations_projection_consistent (ledger : BudgetLedger) :
    allocations ledger = ledger.entries.map BudgetEntry.allocated := rfl

theorem spends_projection_consistent (ledger : BudgetLedger) :
    spends ledger = ledger.entries.map BudgetEntry.spent := rfl

theorem refunds_projection_consistent (ledger : BudgetLedger) :
    refunds ledger = ledger.entries.map BudgetEntry.refunded := rfl

theorem occupancies_projection_consistent (ledger : BudgetLedger) :
    occupancies ledger = ledger.entries.map BudgetEntry.occupied := rfl

theorem append_resourceIds (ledger : BudgetLedger) (entry : BudgetEntry)
    (auditEntry : AuditEntry) :
    resourceIds (append ledger entry auditEntry) =
      resourceIds ledger ++ [entry.resourceId] := by
  simp [resourceIds, append]

theorem append_allocations (ledger : BudgetLedger) (entry : BudgetEntry)
    (auditEntry : AuditEntry) :
    allocations (append ledger entry auditEntry) =
      allocations ledger ++ [entry.allocated] := by
  simp [allocations, append]

theorem append_extends (ledger : BudgetLedger) (entry : BudgetEntry)
    (auditEntry : AuditEntry) : Extends ledger (append ledger entry auditEntry) := by
  exact ⟨⟨[entry], rfl⟩, AuditRecord.append_extends ledger.audit auditEntry⟩

theorem mem_of_extends {old newer : BudgetLedger}
    (h : Extends old newer) {entry : BudgetEntry}
    (hmem : entry ∈ old.entries) : entry ∈ newer.entries := by
  rcases h.1 with ⟨suffix, hsuffix⟩
  rw [hsuffix]
  simp only [List.mem_append]
  exact Or.inl hmem

theorem audit_mem_of_extends {old newer : BudgetLedger}
    (h : Extends old newer) {entry : AuditEntry}
    (hmem : entry ∈ old.audit.entries) : entry ∈ newer.audit.entries :=
  AuditRecord.mem_of_extends h.2 hmem

theorem failed_budget_not_silently_deleted {old newer : BudgetLedger}
    (h : Extends old newer) {entry : BudgetEntry}
    (hmem : entry ∈ old.entries)
    (_ : entry.disposition = AuditDisposition.failed) :
    entry ∈ newer.entries := mem_of_extends h hmem

theorem revoked_budget_not_silently_deleted {old newer : BudgetLedger}
    (h : Extends old newer) {entry : BudgetEntry}
    (hmem : entry ∈ old.entries)
    (_ : entry.disposition = AuditDisposition.revoked) :
    entry ∈ newer.entries := mem_of_extends h hmem

theorem refunded_budget_not_silently_deleted {old newer : BudgetLedger}
    (h : Extends old newer) {entry : BudgetEntry}
    (hmem : entry ∈ old.entries)
    (_ : entry.disposition = AuditDisposition.refunded) :
    entry ∈ newer.entries := mem_of_extends h hmem

theorem withdrawn_budget_not_silently_deleted {old newer : BudgetLedger}
    (h : Extends old newer) {entry : BudgetEntry}
    (hmem : entry ∈ old.entries)
    (_ : entry.disposition = AuditDisposition.withdrawn) :
    entry ∈ newer.entries := mem_of_extends h hmem

theorem audit_extends_of_ledger_extends {old newer : BudgetLedger}
    (h : Extends old newer) : AuditRecord.Extends old.audit newer.audit := h.2

end BudgetLedger

end FoundationsVII
