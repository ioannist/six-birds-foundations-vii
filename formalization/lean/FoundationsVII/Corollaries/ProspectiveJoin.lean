import FoundationsVII.Access.Commitment
import FoundationsVII.Access.Transitions
import FoundationsVII.Join.Strictness
import FoundationsVII.Join.Budget

/-!
# Prospective admission and strict-join integration

A strict join may receive prospective admission credit only when the temporal
commitment, admission step, join certificate, payment ledger, and source link
are all independently present.  This module composes those certificates; it
does not collapse them into one primitive assertion.
-/

namespace FoundationsVII

universe u

structure ProspectiveJoinAdmission {α : Type u}
    (before : α → α → Prop) (registered evidence : α) where
  commitmentUse : CommitmentUse
  admission : TypedAdmissionStep
  joinEvidence : StrictJoinEvidence
  payment : JoinPaymentLedger
  sourceAligned : admission.transition.sourceId = commitmentUse.commitment.sourceId

namespace ProspectiveJoinAdmission

structure Certified {α : Type u}
    {before : α → α → Prop} {registered evidence : α}
    (profile : ProspectiveJoinAdmission before registered evidence) : Prop where
  prospective : CommitmentUse.ProspectivelyCertified before registered evidence
    profile.commitmentUse
  lawfulAdmission : TypedAdmissionStep.Lawful profile.admission
  strictJoin : StrictJoinEvidence.Certified profile.joinEvidence
  paymentSettled : JoinPaymentLedger.FullyPaid profile.payment

/-- A prospective strict-join admission exposes the temporal, source, join,
and payment certificates separately. -/
theorem certified_has_temporal_source_join_and_payment
    {α : Type u} {before : α → α → Prop} {registered evidence : α}
    {profile : ProspectiveJoinAdmission before registered evidence}
    (h : Certified profile) :
    before registered evidence ∧
      TypedAdmissionStep.SourceAuthorized profile.admission ∧
      profile.joinEvidence.sourceIndependent = true ∧
      profile.joinEvidence.budgetSettled = true ∧
      profile.payment.audit.entries ≠ [] ∧
      profile.admission.transition.sourceId =
        profile.commitmentUse.commitment.sourceId := by
  have hJoin := StrictJoinEvidence.certified_has_source_and_budget_gates h.strictJoin
  exact ⟨CommitmentUse.prospectively_certified_has_temporal_precedence h.prospective,
    h.lawfulAdmission.sourceAuthorized, hJoin.1, hJoin.2,
    JoinPaymentLedger.fullyPaid_has_audit h.paymentSettled,
    profile.sourceAligned⟩

/-- Retrospective registration cannot be repaired by later admission, join, or
payment evidence. -/
theorem retrospective_registration_blocks_prospective_join_credit
    {α : Type u} {before : α → α → Prop} {registered evidence : α}
    {profile : ProspectiveJoinAdmission before registered evidence}
    (hNotBefore : ¬ before registered evidence) :
    ¬ Certified profile := by
  intro h
  exact hNotBefore
    (CommitmentUse.prospectively_certified_has_temporal_precedence h.prospective)

/-- Source alignment is part of the integrated certificate and is not inferred
from similarity of the joined packages. -/
theorem certified_preserves_declared_source_alignment
    {α : Type u} {before : α → α → Prop} {registered evidence : α}
    {profile : ProspectiveJoinAdmission before registered evidence}
    (_h : Certified profile) :
    profile.admission.transition.sourceId =
      profile.commitmentUse.commitment.sourceId :=
  profile.sourceAligned

end ProspectiveJoinAdmission

end FoundationsVII
