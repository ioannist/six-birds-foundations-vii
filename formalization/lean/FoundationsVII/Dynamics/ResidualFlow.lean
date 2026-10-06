import FoundationsVII.Dynamics.PrimitiveAlgebra
import FoundationsVII.Prior.FT20

/-!
# Dynamic residual flow

Residual and debt bookkeeping is explicit across composed enablement and
transmission. The equality is a declared accounting law, not a claim that all
scientific obstructions are scalar or additive.
-/

namespace FoundationsVII

structure ResidualFlow where
  inherited : Nat
  created : Nat
  dissolved : Nat
  terminal : Nat
  debtCharged : Nat
  debtSettled : Nat
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace ResidualFlow

def WellAccounted (flow : ResidualFlow) : Prop :=
  flow.terminal + flow.dissolved = flow.inherited + flow.created ∧
  flow.debtSettled ≤ flow.debtCharged ∧
  flow.audit.entries ≠ []

theorem accounted_balance {flow : ResidualFlow} (h : WellAccounted flow) :
    flow.terminal + flow.dissolved = flow.inherited + flow.created := h.1

theorem settled_debt_bounded {flow : ResidualFlow} (h : WellAccounted flow) :
    flow.debtSettled ≤ flow.debtCharged := h.2.1

theorem composed_debt_accumulates (left right : ResidualFlow) :
    left.debtCharged + right.debtCharged =
      right.debtCharged + left.debtCharged := Nat.add_comm _ _

end ResidualFlow

end FoundationsVII
