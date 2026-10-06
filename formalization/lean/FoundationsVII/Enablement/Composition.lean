import FoundationsVII.Enablement.Separation
import FoundationsVII.Residuals.Ledger

/-!
# Enablement-chain composition

Composition requires source, budget, residual, and audit compatibility. Costs
and residual debts accumulate. Composed enablement is not transitive causation
without a separate causal-chain certificate.
-/

namespace FoundationsVII

structure ResourceDelta where
  cost : Nat
  residualDebt : Nat
  deriving Repr, DecidableEq, BEq

namespace ResourceDelta

def zero : ResourceDelta := { cost := 0, residualDebt := 0 }

def combine (left right : ResourceDelta) : ResourceDelta :=
  { cost := left.cost + right.cost,
    residualDebt := left.residualDebt + right.residualDebt }

theorem combine_cost (left right : ResourceDelta) :
    (combine left right).cost = left.cost + right.cost := rfl

theorem combine_residualDebt (left right : ResourceDelta) :
    (combine left right).residualDebt = left.residualDebt + right.residualDebt := rfl

theorem combine_assoc (a b c : ResourceDelta) :
    combine (combine a b) c = combine a (combine b c) := by
  cases a
  cases b
  cases c
  simp [combine, Nat.add_assoc]

theorem zero_left (a : ResourceDelta) : combine zero a = a := by
  cases a
  simp [combine, zero]

theorem zero_right (a : ResourceDelta) : combine a zero = a := by
  cases a
  simp [combine, zero]

end ResourceDelta

structure EnablementLink where
  sourceOperation : String
  targetOperation : String
  sourceRoot : SourceId
  targetRoot : SourceId
  executed : Bool
  audited : Bool
  delta : ResourceDelta
  causalChannel : Bool
  deriving Repr, DecidableEq, BEq

namespace EnablementLink

def Nonempty (link : EnablementLink) : Prop :=
  link.sourceOperation ≠ "" ∧ link.targetOperation ≠ ""

def Composable (first second : EnablementLink) : Prop :=
  Nonempty first ∧ Nonempty second ∧
  first.targetOperation = second.sourceOperation ∧
  first.targetRoot = second.sourceRoot ∧
  first.executed = true ∧ second.executed = true ∧
  first.audited = true ∧ second.audited = true

def compose (first second : EnablementLink) : EnablementLink :=
  { sourceOperation := first.sourceOperation,
    targetOperation := second.targetOperation,
    sourceRoot := first.sourceRoot,
    targetRoot := second.targetRoot,
    executed := first.executed && second.executed,
    audited := first.audited && second.audited,
    delta := ResourceDelta.combine first.delta second.delta,
    causalChannel := first.causalChannel && second.causalChannel }

theorem compose_accumulates_cost (first second : EnablementLink) :
    (compose first second).delta.cost = first.delta.cost + second.delta.cost := rfl

theorem compose_accumulates_residual_debt (first second : EnablementLink) :
    (compose first second).delta.residualDebt =
      first.delta.residualDebt + second.delta.residualDebt := rfl

theorem compose_associative_data (a b c : EnablementLink) :
    compose (compose a b) c = compose a (compose b c) := by
  cases a
  cases b
  cases c
  simp [compose, ResourceDelta.combine, Nat.add_assoc, Bool.and_assoc]

theorem composable_chain_associates
    (a b c : EnablementLink)
    (_hab : Composable a b)
    (_hbc : Composable b c) :
    compose (compose a b) c = compose a (compose b c) :=
  compose_associative_data a b c

end EnablementLink

structure CompositionCredit where
  firstExecuted : Bool
  secondExecuted : Bool
  sourceCompatible : Bool
  budgetCompatible : Bool
  residualCompatible : Bool
  auditCompatible : Bool
  causalChainCertified : Bool
  composedEnablementCredit : Bool
  transitiveCausationCredit : Bool
  deriving Repr, DecidableEq, BEq

namespace CompositionCredit

def Valid (credit : CompositionCredit) : Prop :=
  (credit.composedEnablementCredit = true ↔
    credit.firstExecuted = true ∧ credit.secondExecuted = true ∧
    credit.sourceCompatible = true ∧ credit.budgetCompatible = true ∧
    credit.residualCompatible = true ∧ credit.auditCompatible = true) ∧
  (credit.transitiveCausationCredit = true →
    credit.composedEnablementCredit = true ∧ credit.causalChainCertified = true)

instance (credit : CompositionCredit) : Decidable (Valid credit) := by
  unfold Valid
  infer_instance

end CompositionCredit

private def composedWithoutCausation : CompositionCredit :=
  { firstExecuted := true, secondExecuted := true, sourceCompatible := true,
    budgetCompatible := true, residualCompatible := true, auditCompatible := true,
    causalChainCertified := false, composedEnablementCredit := true,
    transitiveCausationCredit := false }

private def incompatibleOrderControl : CompositionCredit :=
  { firstExecuted := true, secondExecuted := true, sourceCompatible := false,
    budgetCompatible := true, residualCompatible := true, auditCompatible := true,
    causalChainCertified := false, composedEnablementCredit := false,
    transitiveCausationCredit := false }

theorem composed_enablement_without_transitive_causation_exists :
    CompositionCredit.Valid composedWithoutCausation ∧
    composedWithoutCausation.composedEnablementCredit = true ∧
    composedWithoutCausation.transitiveCausationCredit = false := by decide

theorem incompatible_order_blocks_composition_credit :
    CompositionCredit.Valid incompatibleOrderControl ∧
    incompatibleOrderControl.composedEnablementCredit = false := by decide

structure OrderedEnablementControl where
  leftFirstResult : Nat
  rightFirstResult : Nat
  sameMembers : Bool
  deriving Repr, DecidableEq, BEq

private def orderSensitiveEnablement : OrderedEnablementControl :=
  { leftFirstResult := 1, rightFirstResult := 2, sameMembers := true }

theorem enablement_chain_can_be_order_sensitive :
    orderSensitiveEnablement.sameMembers = true ∧
    orderSensitiveEnablement.leftFirstResult ≠ orderSensitiveEnablement.rightFirstResult := by decide

end FoundationsVII
