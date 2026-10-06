import FoundationsVII.Access.Observer
import FoundationsVII.Enablement.Endogenous

/-!
# Observer occupancy, endogeny, and zero-cost claims
-/

namespace FoundationsVII

structure ObserverEndogenyPackage where
  observer : ObserverOccupancyRecord
  endogeny : EndogenousEnablementProfile

namespace ObserverEndogenyPackage

structure Certified (profile : ObserverEndogenyPackage) : Prop where
  nativeFormation : ObserverOccupancyRecord.NativeFormationCredit profile.observer
  endogenous : EndogenousEnablementProfile.Eligible profile.endogeny

/-- Joint native/endogenous credit requires both full observer pricing and the
complete carried/reachable/executed/audited/budgeted endogeny criterion. -/
theorem certified_requires_pricing_and_internal_execution
    {profile : ObserverEndogenyPackage}
    (h : Certified profile) :
    profile.observer.charged = profile.observer.occupied ∧
      profile.endogeny.carried = true ∧
      profile.endogeny.reachable = true ∧
      profile.endogeny.executed = true ∧
      profile.endogeny.hiddenObserver = false := by
  exact ⟨h.nativeFormation.2.2,
    EndogenousEnablementProfile.eligible_requires_carried_generator h.endogenous,
    EndogenousEnablementProfile.eligible_requires_reachable_generator h.endogenous,
    EndogenousEnablementProfile.eligible_requires_execution h.endogenous,
    h.endogenous.2.2.2.2.2.2.2.1⟩

/-- Hidden positive observer occupancy blocks the joint native/endogenous
credit package regardless of the endogeny record. -/
theorem unpriced_observer_blocks_joint_native_endogenous_credit
    {profile : ObserverEndogenyPackage}
    (hHidden : profile.observer.charged < profile.observer.occupied) :
    ¬ Certified profile := by
  intro h
  exact ObserverOccupancyRecord.unpriced_observer_invalidates_native_formation_credit
    hHidden h.nativeFormation

/-- Genuine zero occupancy is a lawful native-credit escape when the remaining
well-formedness and endogeny certificates are independently present. -/
theorem zero_occupancy_escape_preserves_endogenous_credit
    {profile : ObserverEndogenyPackage}
    (hWellFormed : ObserverOccupancyRecord.WellFormed profile.observer)
    (hNative : ObserverOccupancyRecord.NativeOrEndogenous profile.observer)
    (hOccupied : profile.observer.occupied = 0)
    (hCharged : profile.observer.charged = 0)
    (hEndogenous : EndogenousEnablementProfile.Eligible profile.endogeny) :
    Certified profile := by
  exact ⟨ObserverOccupancyRecord.zero_occupancy_native_credit
      hWellFormed hNative hOccupied hCharged,
    hEndogenous⟩

end ObserverEndogenyPackage

end FoundationsVII
