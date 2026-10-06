import FoundationsVII.Access.Bootstrap

/-!
# Prospective commitment without a compulsory global clock

Temporal precedence is carried by an explicit relation and certificate.  The
numeric commitment timestamps remain local validity and budget fields; they do
not supply an unstated global event order.
-/

namespace FoundationsVII

universe u

structure PrecedenceCertificate {α : Type u}
    (before : α → α → Prop) (registered evidence : α) : Prop where
  precedes : before registered evidence

namespace PrecedenceCertificate

theorem impossible_when_not_precedent {α : Type u}
    {before : α → α → Prop} {registered evidence : α}
    (hNotBefore : ¬ before registered evidence) :
    ¬ Nonempty (PrecedenceCertificate before registered evidence) := by
  intro hCertificate
  rcases hCertificate with ⟨certificate⟩
  exact hNotBefore certificate.precedes

end PrecedenceCertificate

structure CommitmentUse where
  commitment : ProspectiveCommitment
  usedAt : Timestamp
  taskBlind : Bool
  outcomeIndependent : Bool
  symmetryCertified : Bool
  controlMatched : Bool
  spent : Cost
  refunded : Cost
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace CommitmentUse

def Active (use : CommitmentUse) : Prop :=
  use.commitment.validFrom ≤ use.usedAt ∧
  use.usedAt ≤ use.commitment.expiresAt

def BudgetSettled (use : CommitmentUse) : Prop :=
  use.spent + use.refunded = use.commitment.reservedBudget

def NeutralSeedEquivalent (use : CommitmentUse) : Prop :=
  use.commitment.preregistered = true ∧
  use.taskBlind = true ∧
  use.outcomeIndependent = true ∧
  use.symmetryCertified = true ∧
  use.controlMatched = true

structure NeutralSeedClassKey where
  sourceId : SourceId
  permittedSourceKinds : List SourceKind
  taskBlind : Bool
  outcomeIndependent : Bool
  symmetryCertified : Bool
  controlMatched : Bool
  deriving Repr, DecidableEq, BEq

def neutralSeedClassKey (use : CommitmentUse) : NeutralSeedClassKey :=
  { sourceId := use.commitment.sourceId
    permittedSourceKinds := use.commitment.permittedSourceKinds
    taskBlind := use.taskBlind
    outcomeIndependent := use.outcomeIndependent
    symmetryCertified := use.symmetryCertified
    controlMatched := use.controlMatched }

def SameNeutralSeedClass (left right : CommitmentUse) : Prop :=
  neutralSeedClassKey left = neutralSeedClassKey right

namespace SameNeutralSeedClass

theorem refl (use : CommitmentUse) : SameNeutralSeedClass use use := rfl

theorem symm {left right : CommitmentUse}
    (h : SameNeutralSeedClass left right) : SameNeutralSeedClass right left :=
  Eq.symm h

theorem trans {left middle right : CommitmentUse}
    (h₁ : SameNeutralSeedClass left middle)
    (h₂ : SameNeutralSeedClass middle right) :
    SameNeutralSeedClass left right :=
  Eq.trans h₁ h₂

end SameNeutralSeedClass

structure ProspectivelyCertified {α : Type u}
    (before : α → α → Prop) (registered evidence : α)
    (use : CommitmentUse) : Prop where
  precedence : PrecedenceCertificate before registered evidence
  commitmentWellFormed : ProspectiveCommitment.WellFormed use.commitment
  active : Active use
  preregistered : use.commitment.preregistered = true
  taskBlind : use.taskBlind = true
  outcomeIndependent : use.outcomeIndependent = true
  symmetryCertified : use.symmetryCertified = true
  controlMatched : use.controlMatched = true
  budgetSettled : BudgetSettled use
  auditPresent : use.audit.entries ≠ []

theorem prospectively_certified_has_temporal_precedence
    {α : Type u} {before : α → α → Prop} {registered evidence : α}
    {use : CommitmentUse}
    (h : ProspectivelyCertified before registered evidence use) :
    before registered evidence :=
  h.precedence.precedes

theorem prospectively_certified_is_neutral_seed_equivalent
    {α : Type u} {before : α → α → Prop} {registered evidence : α}
    {use : CommitmentUse}
    (h : ProspectivelyCertified before registered evidence use) :
    NeutralSeedEquivalent use :=
  ⟨h.preregistered, h.taskBlind, h.outcomeIndependent,
    h.symmetryCertified, h.controlMatched⟩

theorem retrospective_predicate_cannot_discharge_prospective_certificate
    {α : Type u} {before : α → α → Prop} {registered evidence : α}
    {use : CommitmentUse}
    (hNotBefore : ¬ before registered evidence) :
    ¬ ProspectivelyCertified before registered evidence use := by
  intro hCertified
  exact hNotBefore hCertified.precedence.precedes

theorem expired_commitment_is_not_active {use : CommitmentUse}
    (hExpired : use.commitment.expiresAt < use.usedAt) :
    ¬ Active use := by
  intro hActive
  exact (Nat.not_lt_of_ge hActive.2) hExpired

theorem unused_reserved_budget_is_refunded
    {use : CommitmentUse}
    (hSettled : BudgetSettled use)
    (hUnused : use.spent = 0) :
    use.refunded = use.commitment.reservedBudget := by
  change use.spent + use.refunded = use.commitment.reservedBudget at hSettled
  rw [hUnused, Nat.zero_add] at hSettled
  exact hSettled

end CommitmentUse

end FoundationsVII
