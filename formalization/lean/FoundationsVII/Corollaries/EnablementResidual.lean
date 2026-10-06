import FoundationsVII.Enablement.Composition
import FoundationsVII.Residuals.Ledger

/-!
# Residual-aware enablement composition
-/

namespace FoundationsVII

structure ResidualAwareEnablementChain where
  first : EnablementLink
  second : EnablementLink
  before : ResidualLedger
  after : ResidualLedger
  retainedEntry : ResidualEntry

namespace ResidualAwareEnablementChain

structure Certified (profile : ResidualAwareEnablementChain) : Prop where
  composable : EnablementLink.Composable profile.first profile.second
  residualExtends : ResidualLedger.Extends profile.before profile.after
  retainedBefore : profile.retainedEntry ∈ profile.before.entries
  positiveResidualDebt :
    0 < (EnablementLink.compose profile.first profile.second).delta.residualDebt

/-- Composition accumulates cost and residual debt while append-only residual
history preserves every previously recorded entry. -/
theorem certified_accumulates_resources_and_preserves_residuals
    {profile : ResidualAwareEnablementChain}
    (h : Certified profile) :
    (EnablementLink.compose profile.first profile.second).delta.cost =
        profile.first.delta.cost + profile.second.delta.cost ∧
      (EnablementLink.compose profile.first profile.second).delta.residualDebt =
        profile.first.delta.residualDebt + profile.second.delta.residualDebt ∧
      profile.retainedEntry ∈ profile.after.entries ∧
      0 < (EnablementLink.compose profile.first profile.second).delta.residualDebt := by
  exact ⟨EnablementLink.compose_accumulates_cost _ _,
    EnablementLink.compose_accumulates_residual_debt _ _,
    ResidualLedger.mem_of_extends h.residualExtends h.retainedBefore,
    h.positiveResidualDebt⟩

/-- A source-typed cross-term needle plus positive composed debt blocks a
zero-residual reading of the chain. -/
theorem join_created_needle_blocks_zero_residual_reading
    {profile : ResidualAwareEnablementChain}
    {needle : CrossTermNeedle}
    (h : Certified profile)
    (hNeedle : CrossTermNeedle.Valid needle) :
    needle.entry.kind = ResidualKind.crossTerm ∧
      (EnablementLink.compose profile.first profile.second).delta.residualDebt ≠ 0 := by
  exact ⟨hNeedle.2.1, Nat.ne_of_gt h.positiveResidualDebt⟩

end ResidualAwareEnablementChain

end FoundationsVII
