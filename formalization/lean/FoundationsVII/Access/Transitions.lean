import FoundationsVII.Access.Domain
import FoundationsVII.Core.Reachability
import FoundationsVII.Core.Ledgers

/-!
# Lawful admission transitions and replayable paths

This module closes the structural transition obligations of VII-C002.  Rule
text, soundness, executability, firing, and occurrence remain separate fields.
Rollback and revocation change current status without deleting source, budget,
or audit history.
-/

namespace FoundationsVII

inductive AdmissionOperation where
  | admit
  | expire
  | revoke
  | retract
  | rollback
  deriving Repr, DecidableEq, BEq, Inhabited

namespace BudgetEntry

def remaining (entry : BudgetEntry) : Cost :=
  entry.allocated + entry.refunded - entry.spent - entry.occupied

end BudgetEntry

namespace BudgetLedger

def remaining (ledger : BudgetLedger) : Cost :=
  (ledger.entries.map BudgetEntry.remaining).foldl Nat.add 0

end BudgetLedger

structure TypedAdmissionStep where
  operation : AdmissionOperation
  transition : AdmissionTransition
  sourceBefore : SourceLedger
  sourceAfter : SourceLedger
  budgetBefore : BudgetLedger
  budgetAfter : BudgetLedger
  historyBefore : AuditRecord
  historyAfter : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace TypedAdmissionStep

def SourceAuthorized (step : TypedAdmissionStep) : Prop :=
  ∃ entry : SourceEntry,
    entry ∈ step.sourceBefore.entries ∧
    entry.sourceId = step.transition.sourceId ∧
    entry.inScope = true ∧
    entry.disposition = AuditDisposition.accepted

def EffectTyped (step : TypedAdmissionStep) : Prop :=
  match step.operation with
  | .admit => step.transition.target.admissible = true
  | .expire => step.transition.target.admissible = false
  | .revoke => step.transition.target.admissible = false
  | .retract => step.transition.target.admissible = false
  | .rollback => step.transition.target.admissible = false

structure Lawful (step : TypedAdmissionStep) : Prop where
  transitionWellFormed : AdmissionTransition.WellFormed step.transition
  guardSatisfied : step.transition.guardSatisfied = true
  sourceBeforeWellFormed : SourceLedger.WellFormed step.sourceBefore
  sourceAuthorized : SourceAuthorized step
  budgetBeforeWellFormed : BudgetLedger.WellFormed step.budgetBefore
  sourceExtends : SourceLedger.Extends step.sourceBefore step.sourceAfter
  budgetExtends : BudgetLedger.Extends step.budgetBefore step.budgetAfter
  historyExtends : AuditRecord.Extends step.historyBefore step.historyAfter
  costCovered : step.transition.cost ≤ BudgetLedger.remaining step.budgetBefore
  effectTyped : EffectTyped step

namespace Lawful

theorem executable_is_sound {step : TypedAdmissionStep}
    (h : Lawful step) (hExecutable : step.transition.executable = true) :
    step.transition.sound = true :=
  h.transitionWellFormed.2.2.2.2.2.2.1 hExecutable

theorem fired_is_executable {step : TypedAdmissionStep}
    (h : Lawful step) (hFired : step.transition.fired = true) :
    step.transition.executable = true :=
  AdmissionTransition.fired_implies_executable h.transitionWellFormed hFired

theorem occurrence_is_fired {step : TypedAdmissionStep}
    (h : Lawful step) (hOccurrence : step.transition.target.occurrent = true) :
    step.transition.fired = true :=
  h.transitionWellFormed.2.2.2.2.2.2.2.2.1 hOccurrence

theorem old_audit_entry_survives {step : TypedAdmissionStep}
    (h : Lawful step) {entry : AuditEntry}
    (hEntry : entry ∈ step.historyBefore.entries) :
    entry ∈ step.historyAfter.entries :=
  AuditRecord.mem_of_extends h.historyExtends hEntry

theorem old_source_entry_survives {step : TypedAdmissionStep}
    (h : Lawful step) {entry : SourceEntry}
    (hEntry : entry ∈ step.sourceBefore.entries) :
    entry ∈ step.sourceAfter.entries :=
  SourceLedger.mem_of_extends h.sourceExtends hEntry

theorem old_budget_entry_survives {step : TypedAdmissionStep}
    (h : Lawful step) {entry : BudgetEntry}
    (hEntry : entry ∈ step.budgetBefore.entries) :
    entry ∈ step.budgetAfter.entries :=
  BudgetLedger.mem_of_extends h.budgetExtends hEntry

theorem authorized_source_entry_exists {step : TypedAdmissionStep}
    (h : Lawful step) :
    ∃ entry : SourceEntry,
      entry ∈ step.sourceBefore.entries ∧
      entry.sourceId = step.transition.sourceId ∧
      entry.inScope = true ∧
      entry.disposition = AuditDisposition.accepted :=
  h.sourceAuthorized

theorem sourced_financed_and_audited {step : TypedAdmissionStep}
    (h : Lawful step) :
    SourceAuthorized step ∧
      SourceLedger.Extends step.sourceBefore step.sourceAfter ∧
      step.transition.cost ≤ BudgetLedger.remaining step.budgetBefore ∧
      BudgetLedger.Extends step.budgetBefore step.budgetAfter ∧
      AuditRecord.Extends step.historyBefore step.historyAfter :=
  ⟨h.sourceAuthorized, h.sourceExtends, h.costCovered,
    h.budgetExtends, h.historyExtends⟩

end Lawful

theorem admit_sets_admissible {step : TypedAdmissionStep}
    (hOperation : step.operation = AdmissionOperation.admit)
    (hLawful : Lawful step) :
    step.transition.target.admissible = true := by
  have hEffect := hLawful.effectTyped
  unfold EffectTyped at hEffect
  rw [hOperation] at hEffect
  exact hEffect

theorem expiry_clears_admissible {step : TypedAdmissionStep}
    (hOperation : step.operation = AdmissionOperation.expire)
    (hLawful : Lawful step) :
    step.transition.target.admissible = false := by
  have hEffect := hLawful.effectTyped
  unfold EffectTyped at hEffect
  rw [hOperation] at hEffect
  exact hEffect

theorem revocation_clears_admissible {step : TypedAdmissionStep}
    (hOperation : step.operation = AdmissionOperation.revoke)
    (hLawful : Lawful step) :
    step.transition.target.admissible = false := by
  have hEffect := hLawful.effectTyped
  unfold EffectTyped at hEffect
  rw [hOperation] at hEffect
  exact hEffect

theorem revocation_clears_current_admissibility_but_preserves_history
    {step : TypedAdmissionStep}
    (hOperation : step.operation = AdmissionOperation.revoke)
    (hLawful : Lawful step) {entry : AuditEntry}
    (hEntry : entry ∈ step.historyBefore.entries) :
    step.transition.target.admissible = false ∧
      entry ∈ step.historyAfter.entries := by
  constructor
  · exact revocation_clears_admissible hOperation hLawful
  · exact Lawful.old_audit_entry_survives hLawful hEntry

theorem retraction_clears_admissible {step : TypedAdmissionStep}
    (hOperation : step.operation = AdmissionOperation.retract)
    (hLawful : Lawful step) :
    step.transition.target.admissible = false := by
  have hEffect := hLawful.effectTyped
  unfold EffectTyped at hEffect
  rw [hOperation] at hEffect
  exact hEffect

theorem rollback_clears_current_admissibility_but_preserves_history
    {step : TypedAdmissionStep}
    (hOperation : step.operation = AdmissionOperation.rollback)
    (hLawful : Lawful step) {entry : AuditEntry}
    (hEntry : entry ∈ step.historyBefore.entries) :
    step.transition.target.admissible = false ∧
      entry ∈ step.historyAfter.entries := by
  constructor
  · have hEffect := hLawful.effectTyped
    unfold EffectTyped at hEffect
    rw [hOperation] at hEffect
    exact hEffect
  · exact Lawful.old_audit_entry_survives hLawful hEntry

end TypedAdmissionStep

inductive AdmissionReplay : DomainState → List TypedAdmissionStep → DomainState → Prop
  | nil (state : DomainState) : AdmissionReplay state [] state
  | cons {start middle finish : DomainState}
      {step : TypedAdmissionStep} {tail : List TypedAdmissionStep}
      (hSource : step.transition.source = start)
      (hTarget : step.transition.target = middle)
      (hLawful : TypedAdmissionStep.Lawful step)
      (hTail : AdmissionReplay middle tail finish) :
      AdmissionReplay start (step :: tail) finish

namespace AdmissionReplay

theorem append {start middle finish : DomainState}
    {first second : List TypedAdmissionStep}
    (hFirst : AdmissionReplay start first middle)
    (hSecond : AdmissionReplay middle second finish) :
    AdmissionReplay start (first ++ second) finish := by
  induction hFirst generalizing finish second with
  | nil =>
      simpa using hSecond
  | @cons start₁ middle₁ finish₁ step tail hSource hTarget hLawful hTail ih =>
      simp only [List.cons_append]
      exact AdmissionReplay.cons hSource hTarget hLawful (ih hSecond)

theorem two_step {start middle finish : DomainState}
    {first second : TypedAdmissionStep}
    (hFirstSource : first.transition.source = start)
    (hFirstTarget : first.transition.target = middle)
    (hFirstLawful : TypedAdmissionStep.Lawful first)
    (hSecondSource : second.transition.source = middle)
    (hSecondTarget : second.transition.target = finish)
    (hSecondLawful : TypedAdmissionStep.Lawful second) :
    AdmissionReplay start [first, second] finish := by
  exact AdmissionReplay.cons hFirstSource hFirstTarget hFirstLawful
    (AdmissionReplay.cons hSecondSource hSecondTarget hSecondLawful
      (AdmissionReplay.nil finish))

end AdmissionReplay

end FoundationsVII
