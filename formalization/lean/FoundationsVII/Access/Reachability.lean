import FoundationsVII.Access.Origin
import FoundationsVII.Core.Protocols

/-!
# Operational reachability, firing, occurrence, and negative force

This module closes VII-C021.  Reachability is an executable-path property;
occurrence additionally requires firing.  Finite-horizon nulls retain their
horizon and family qualifiers.
-/

namespace FoundationsVII

structure OperationalProfile where
  sound : Bool
  executable : Bool
  guardActive : Bool
  reachable : Bool
  fired : Bool
  occurrent : Bool
  deriving Repr, DecidableEq, BEq

namespace OperationalProfile

def Coherent (profile : OperationalProfile) : Prop :=
  (profile.executable = true → profile.sound = true) ∧
  (profile.reachable = true →
    profile.guardActive = true ∧ profile.executable = true) ∧
  (profile.fired = true → profile.reachable = true) ∧
  (profile.occurrent = true → profile.fired = true)

instance (profile : OperationalProfile) : Decidable (Coherent profile) := by
  unfold Coherent
  infer_instance

def soundUnreachable : OperationalProfile :=
  { sound := true
    executable := false
    guardActive := false
    reachable := false
    fired := false
    occurrent := false }

def reachableNonoccurring : OperationalProfile :=
  { sound := true
    executable := true
    guardActive := true
    reachable := true
    fired := false
    occurrent := false }

def occurrentProfile : OperationalProfile :=
  { sound := true
    executable := true
    guardActive := true
    reachable := true
    fired := true
    occurrent := true }

theorem soundness_does_not_imply_reachability :
    Coherent soundUnreachable ∧
      soundUnreachable.sound = true ∧
      soundUnreachable.reachable = false := by
  decide

theorem reachability_does_not_imply_firing_or_occurrence :
    Coherent reachableNonoccurring ∧
      reachableNonoccurring.reachable = true ∧
      reachableNonoccurring.fired = false ∧
      reachableNonoccurring.occurrent = false := by
  decide

theorem no_occurrence_from_reachability_alone :
    ¬ (∀ profile : OperationalProfile,
      Coherent profile → profile.reachable = true →
        profile.occurrent = true) := by
  intro hUniversal
  have hOccurrence := hUniversal reachableNonoccurring (by decide) rfl
  exact absurd hOccurrence (by decide)

theorem occurrence_requires_firing {profile : OperationalProfile}
    (hCoherent : Coherent profile)
    (hOccurrence : profile.occurrent = true) :
    profile.fired = true :=
  hCoherent.2.2.2 hOccurrence

theorem firing_requires_reachability {profile : OperationalProfile}
    (hCoherent : Coherent profile)
    (hFired : profile.fired = true) :
    profile.reachable = true :=
  hCoherent.2.2.1 hFired

theorem reachability_requires_active_guard_and_execution
    {profile : OperationalProfile}
    (hCoherent : Coherent profile)
    (hReachable : profile.reachable = true) :
    profile.guardActive = true ∧ profile.executable = true :=
  hCoherent.2.1 hReachable

end OperationalProfile

structure HorizonObservation where
  horizon : Nat
  completeThroughHorizon : Bool
  familyClosed : Bool
  detectorPower : Bool
  occurrenceWithinHorizon : Bool
  occurrenceAfterHorizon : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace HorizonObservation

def BoundedNull (observation : HorizonObservation) : Prop :=
  observation.completeThroughHorizon = true ∧
  observation.occurrenceWithinHorizon = false ∧
  observation.audit.entries ≠ []

instance (observation : HorizonObservation) : Decidable (BoundedNull observation) := by
  unfold BoundedNull
  infer_instance

def ClosedFamilyNegativeCertificate
    (observation : HorizonObservation) : Prop :=
  BoundedNull observation ∧
  observation.familyClosed = true ∧
  observation.detectorPower = true ∧
  observation.occurrenceAfterHorizon = false

instance (observation : HorizonObservation) :
    Decidable (ClosedFamilyNegativeCertificate observation) := by
  unfold ClosedFamilyNegativeCertificate
  infer_instance

def finiteOpenNull : HorizonObservation :=
  { horizon := 4
    completeThroughHorizon := true
    familyClosed := false
    detectorPower := true
    occurrenceWithinHorizon := false
    occurrenceAfterHorizon := true
    audit := DomainState.phase2Audit }

theorem finite_horizon_null_is_only_horizon_qualified :
    BoundedNull finiteOpenNull ∧
      ¬ ClosedFamilyNegativeCertificate finiteOpenNull := by
  decide

theorem bounded_null_does_not_imply_unrestricted_nonoccurrence :
    ¬ (∀ observation : HorizonObservation,
      BoundedNull observation →
        ClosedFamilyNegativeCertificate observation) := by
  intro hUniversal
  exact finite_horizon_null_is_only_horizon_qualified.2
    (hUniversal finiteOpenNull finite_horizon_null_is_only_horizon_qualified.1)

theorem closed_family_detector_power_and_complete_null_are_sufficient
    {observation : HorizonObservation}
    (hNull : BoundedNull observation)
    (hClosed : observation.familyClosed = true)
    (hPower : observation.detectorPower = true)
    (hNoLaterOccurrence : observation.occurrenceAfterHorizon = false) :
    ClosedFamilyNegativeCertificate observation :=
  ⟨hNull, hClosed, hPower, hNoLaterOccurrence⟩

theorem open_family_cannot_receive_closed_family_negative_certificate
    {observation : HorizonObservation}
    (hOpen : observation.familyClosed = false) :
    ¬ ClosedFamilyNegativeCertificate observation := by
  intro hCertificate
  rw [hCertificate.2.1] at hOpen
  exact Bool.noConfusion hOpen

theorem detector_weakness_blocks_closed_family_negative_certificate
    {observation : HorizonObservation}
    (hWeak : observation.detectorPower = false) :
    ¬ ClosedFamilyNegativeCertificate observation := by
  intro hCertificate
  rw [hCertificate.2.2.1] at hWeak
  exact Bool.noConfusion hWeak

end HorizonObservation

end FoundationsVII
