import FoundationsVII.Core.Identifiers

/-!
# Append-only audit records

The authoritative audit is a list.  Extension is witnessed by a suffix, so
failed, revoked, refunded, and withdrawn entries remain first-class history.
-/

namespace FoundationsVII

structure AuditEntry where
  auditId : AuditId
  disposition : AuditDisposition
  subject : String
  message : String
  sourceLocation : String
  deriving Repr, DecidableEq, BEq

namespace AuditEntry

def WellFormed (entry : AuditEntry) : Prop :=
  entry.subject ≠ "" ∧
  entry.message ≠ "" ∧
  entry.sourceLocation ≠ ""

instance (entry : AuditEntry) : Decidable (WellFormed entry) := by
  unfold WellFormed
  infer_instance

end AuditEntry

structure AuditRecord where
  entries : List AuditEntry
  deriving Repr, DecidableEq, BEq

namespace AuditRecord

def WellFormed (record : AuditRecord) : Prop :=
  record.entries ≠ [] ∧
  ∀ entry, entry ∈ record.entries → AuditEntry.WellFormed entry

instance (record : AuditRecord) : Decidable (WellFormed record) := by
  unfold WellFormed
  infer_instance

def append (record : AuditRecord) (entry : AuditEntry) : AuditRecord :=
  { entries := record.entries ++ [entry] }

def extend (record : AuditRecord) (suffix : List AuditEntry) : AuditRecord :=
  { entries := record.entries ++ suffix }

def Extends (old newer : AuditRecord) : Prop :=
  ∃ suffix : List AuditEntry, newer.entries = old.entries ++ suffix

theorem append_extends (record : AuditRecord) (entry : AuditEntry) :
    Extends record (append record entry) := by
  exact ⟨[entry], rfl⟩

theorem extend_extends (record : AuditRecord) (suffix : List AuditEntry) :
    Extends record (extend record suffix) := by
  exact ⟨suffix, rfl⟩

theorem extends_refl (record : AuditRecord) : Extends record record := by
  exact ⟨[], by simp⟩

theorem extends_trans {a b c : AuditRecord}
    (hab : Extends a b) (hbc : Extends b c) : Extends a c := by
  rcases hab with ⟨ab, hab⟩
  rcases hbc with ⟨bc, hbc⟩
  refine ⟨ab ++ bc, ?_⟩
  calc
    c.entries = b.entries ++ bc := hbc
    _ = (a.entries ++ ab) ++ bc := by rw [hab]
    _ = a.entries ++ (ab ++ bc) := by simp [List.append_assoc]

theorem append_preserves_old {record : AuditRecord} {oldEntry : AuditEntry}
    (hmem : oldEntry ∈ record.entries) (newEntry : AuditEntry) :
    oldEntry ∈ (append record newEntry).entries := by
  simp only [append, List.mem_append]
  exact Or.inl hmem

theorem append_contains_new (record : AuditRecord) (entry : AuditEntry) :
    entry ∈ (append record entry).entries := by
  simp [append]

theorem mem_of_extends {old newer : AuditRecord}
    (h : Extends old newer) {entry : AuditEntry}
    (hmem : entry ∈ old.entries) : entry ∈ newer.entries := by
  rcases h with ⟨suffix, hsuffix⟩
  rw [hsuffix]
  simp only [List.mem_append]
  exact Or.inl hmem

theorem failed_entry_not_silently_deleted {old newer : AuditRecord}
    (h : Extends old newer) {entry : AuditEntry}
    (hmem : entry ∈ old.entries)
    (_ : entry.disposition = AuditDisposition.failed) :
    entry ∈ newer.entries := mem_of_extends h hmem

theorem revoked_entry_not_silently_deleted {old newer : AuditRecord}
    (h : Extends old newer) {entry : AuditEntry}
    (hmem : entry ∈ old.entries)
    (_ : entry.disposition = AuditDisposition.revoked) :
    entry ∈ newer.entries := mem_of_extends h hmem

theorem refunded_entry_not_silently_deleted {old newer : AuditRecord}
    (h : Extends old newer) {entry : AuditEntry}
    (hmem : entry ∈ old.entries)
    (_ : entry.disposition = AuditDisposition.refunded) :
    entry ∈ newer.entries := mem_of_extends h hmem

theorem withdrawn_entry_not_silently_deleted {old newer : AuditRecord}
    (h : Extends old newer) {entry : AuditEntry}
    (hmem : entry ∈ old.entries)
    (_ : entry.disposition = AuditDisposition.withdrawn) :
    entry ∈ newer.entries := mem_of_extends h hmem

end AuditRecord

end FoundationsVII
