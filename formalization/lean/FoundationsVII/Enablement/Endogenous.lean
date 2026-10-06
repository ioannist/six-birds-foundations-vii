import FoundationsVII.Enablement.Attribution
import FoundationsVII.Prior.FT12
import FoundationsVII.Prior.FT16

/-!
# Endogenous enablement criterion

Endogenous credit is exact at the declared boundary: the generator is carried,
reachable, executed, audited, budgeted, and free of hidden theorist/observer
execution. Accounted environmental input is compatible with endogeny.
-/

namespace FoundationsVII

structure EndogenousEnablementProfile where
  carried : Bool
  reachable : Bool
  executed : Bool
  audited : Bool
  budgeted : Bool
  boundaryClosed : Bool
  hiddenTheorist : Bool
  hiddenObserver : Bool
  environmentalInput : Bool
  environmentAccounted : Bool
  deriving Repr, DecidableEq, BEq

namespace EndogenousEnablementProfile

def Eligible (profile : EndogenousEnablementProfile) : Prop :=
  profile.carried = true ∧
  profile.reachable = true ∧
  profile.executed = true ∧
  profile.audited = true ∧
  profile.budgeted = true ∧
  profile.boundaryClosed = true ∧
  profile.hiddenTheorist = false ∧
  profile.hiddenObserver = false ∧
  (profile.environmentalInput = false ∨ profile.environmentAccounted = true)

instance (profile : EndogenousEnablementProfile) : Decidable (Eligible profile) := by
  unfold Eligible
  infer_instance


theorem eligible_iff_exact_criterion (profile : EndogenousEnablementProfile) :
    Eligible profile ↔
      profile.carried = true ∧ profile.reachable = true ∧
      profile.executed = true ∧ profile.audited = true ∧
      profile.budgeted = true ∧ profile.boundaryClosed = true ∧
      profile.hiddenTheorist = false ∧ profile.hiddenObserver = false ∧
      (profile.environmentalInput = false ∨ profile.environmentAccounted = true) :=
  Iff.rfl

theorem eligible_requires_carried_generator {profile : EndogenousEnablementProfile}
    (h : Eligible profile) : profile.carried = true := h.1

theorem eligible_requires_reachable_generator {profile : EndogenousEnablementProfile}
    (h : Eligible profile) : profile.reachable = true := h.2.1

theorem eligible_requires_execution {profile : EndogenousEnablementProfile}
    (h : Eligible profile) : profile.executed = true := h.2.2.1

theorem eligible_requires_audit {profile : EndogenousEnablementProfile}
    (h : Eligible profile) : profile.audited = true := h.2.2.2.1

theorem eligible_requires_budget {profile : EndogenousEnablementProfile}
    (h : Eligible profile) : profile.budgeted = true := h.2.2.2.2.1

theorem hidden_theorist_execution_defeats_endogenous_credit
    (profile : EndogenousEnablementProfile)
    (hHidden : profile.hiddenTheorist = true) : ¬ Eligible profile := by
  intro h
  have hNoHidden : profile.hiddenTheorist = false := h.2.2.2.2.2.2.1
  rw [hHidden] at hNoHidden
  exact Bool.noConfusion hNoHidden

theorem hidden_observer_execution_defeats_endogenous_credit
    (profile : EndogenousEnablementProfile)
    (hHidden : profile.hiddenObserver = true) : ¬ Eligible profile := by
  intro h
  have hNoHidden : profile.hiddenObserver = false := h.2.2.2.2.2.2.2.1
  rw [hHidden] at hNoHidden
  exact Bool.noConfusion hNoHidden

end EndogenousEnablementProfile

private def endogenousPositive : EndogenousEnablementProfile :=
  { carried := true, reachable := true, executed := true, audited := true,
    budgeted := true, boundaryClosed := true, hiddenTheorist := false,
    hiddenObserver := false, environmentalInput := false,
    environmentAccounted := false }

private def accountedEnvironmentPositive : EndogenousEnablementProfile :=
  { endogenousPositive with
      environmentalInput := true,
      environmentAccounted := true }

private def theoristTriggered : EndogenousEnablementProfile :=
  { endogenousPositive with hiddenTheorist := true }

private def observerTriggered : EndogenousEnablementProfile :=
  { endogenousPositive with hiddenObserver := true }

theorem constructive_endogenous_enablement_exists :
    EndogenousEnablementProfile.Eligible endogenousPositive := by decide

theorem accounted_environmental_input_is_compatible_with_endogeny :
    EndogenousEnablementProfile.Eligible accountedEnvironmentPositive := by decide

theorem theorist_triggered_enablement_is_not_endogenous :
    ¬ EndogenousEnablementProfile.Eligible theoristTriggered := by decide

theorem hidden_observer_enablement_is_not_endogenous :
    ¬ EndogenousEnablementProfile.Eligible observerTriggered := by decide

/-- Endogenous does not mean uncaused or environmentally isolated. -/
structure EndogenyBoundaryProfile where
  endogenous : Bool
  environmentallyCoupled : Bool
  caused : Bool
  deriving Repr, DecidableEq, BEq

private def coupledEndogenous : EndogenyBoundaryProfile :=
  { endogenous := true, environmentallyCoupled := true, caused := true }

theorem endogenous_does_not_mean_environmentally_isolated_or_uncaused :
    ∃ profile : EndogenyBoundaryProfile,
      profile.endogenous = true ∧
      profile.environmentallyCoupled = true ∧
      profile.caused = true :=
  ⟨coupledEndogenous, rfl, rfl, rfl⟩

end FoundationsVII
