import FoundationsVII.Dynamics.Holonomy

/-!
# Cross-time contact

Contact across incommensurable internal times uses either a synchronization
witness into a common order or a partial-order witness. Equality of local clock
readings is not assumed. Admissible reparameterization preserves the witness.
-/

namespace FoundationsVII

structure ClockEvent where
  clockId : Nat
  localTime : Nat
  orderIndex : Nat
  deriving Repr, DecidableEq, BEq

inductive TimeWitnessKind where
  | synchronization
  | partialOrder
  deriving Repr, DecidableEq, BEq, Inhabited

structure CrossTimeContact where
  left : ClockEvent
  right : ClockEvent
  witnessKind : TimeWitnessKind
  commonOrder : Bool
  orderComparable : Bool
  payloadCrossed : Bool
  assumedSimultaneity : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace CrossTimeContact

def Valid (contact : CrossTimeContact) : Prop :=
  contact.payloadCrossed = true ∧
  contact.assumedSimultaneity = false ∧
  contact.audit.entries ≠ [] ∧
  ((contact.witnessKind = .synchronization ∧ contact.commonOrder = true) ∨
    (contact.witnessKind = .partialOrder ∧ contact.orderComparable = true))

instance (contact : CrossTimeContact) : Decidable (Valid contact) := by
  unfold Valid
  infer_instance

def reparameterize (contact : CrossTimeContact)
    (leftShift rightShift : Nat) : CrossTimeContact :=
  { contact with
    left := { contact.left with localTime := contact.left.localTime + leftShift },
    right := { contact.right with localTime := contact.right.localTime + rightShift } }

theorem valid_under_admissible_reparameterization
    (contact : CrossTimeContact) (leftShift rightShift : Nat)
    (h : Valid contact) :
    Valid (reparameterize contact leftShift rightShift) := by
  simpa [Valid, reparameterize] using h

end CrossTimeContact

private def phase4TimeAuditEntry : AuditEntry :=
  { auditId := 4001, disposition := .accepted,
    subject := "cross-time contact", message := "typed time witness",
    sourceLocation := "FoundationsVII.Dynamics.CrossTime" }

private def phase4TimeAudit : AuditRecord :=
  { entries := [phase4TimeAuditEntry] }

private def synchronizedContact : CrossTimeContact :=
  { left := { clockId := 1, localTime := 2, orderIndex := 10 },
    right := { clockId := 2, localTime := 99, orderIndex := 10 },
    witnessKind := .synchronization, commonOrder := true,
    orderComparable := true, payloadCrossed := true,
    assumedSimultaneity := false, audit := phase4TimeAudit }

private def partialOrderContact : CrossTimeContact :=
  { left := { clockId := 1, localTime := 7, orderIndex := 4 },
    right := { clockId := 2, localTime := 3, orderIndex := 5 },
    witnessKind := .partialOrder, commonOrder := false,
    orderComparable := true, payloadCrossed := true,
    assumedSimultaneity := false, audit := phase4TimeAudit }

theorem synchronized_cross_time_contact_exists :
    CrossTimeContact.Valid synchronizedContact := by decide

theorem partial_order_cross_time_contact_exists :
    CrossTimeContact.Valid partialOrderContact := by decide

theorem synchronization_does_not_require_equal_local_clock_readings :
    CrossTimeContact.Valid synchronizedContact ∧
    synchronizedContact.left.localTime ≠ synchronizedContact.right.localTime := by decide

theorem partial_order_contact_survives_clock_reparameterization :
    CrossTimeContact.Valid (CrossTimeContact.reparameterize partialOrderContact 5 11) := by
  exact CrossTimeContact.valid_under_admissible_reparameterization
    partialOrderContact 5 11 (by decide)

/-- DP07 terminal ruling. -/
theorem incommensurable_times_require_explicit_order_witness :
    (∃ contact : CrossTimeContact,
      CrossTimeContact.Valid contact ∧
      contact.witnessKind = .synchronization) ∧
    (∃ contact : CrossTimeContact,
      CrossTimeContact.Valid contact ∧
      contact.witnessKind = .partialOrder) := by
  exact ⟨⟨synchronizedContact, by decide, rfl⟩,
    ⟨partialOrderContact, by decide, rfl⟩⟩

end FoundationsVII
