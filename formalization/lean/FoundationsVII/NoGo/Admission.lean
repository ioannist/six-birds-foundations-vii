import FoundationsVII.Access.All

/-!
# Foundations VII admission/access no-go front

Each no-go has exact hypotheses and a separately named positive escape theorem.
The statements are structural; finite fixtures are controls, not premises.
-/

namespace FoundationsVII.NoGo

open FoundationsVII

theorem NGVII_01_no_first_extension_without_seed_or_generator
    {regime : AdmissionRegime}
    (hClosed : regime.closedFamily = true)
    (hNoSeed : ¬ AdmissionRegime.HasAdmittedSeed regime)
    (hNoGenerator : ¬ AdmissionRegime.HasReachableGenerator regime)
    (transitionId : TransitionId) :
    ¬ AdmissionRegime.LawfulFirstExtension regime transitionId :=
  AdmissionRegime.no_first_extension_without_seed_or_reachable_generator
    hClosed hNoSeed hNoGenerator transitionId

theorem NGVII_01_escape_admitted_seed
    {regime : AdmissionRegime} {transitionId : TransitionId}
    (hPermitted : transitionId ∈ regime.permittedFirstExtensions)
    (hSeed : AdmissionRegime.HasAdmittedSeed regime) :
    AdmissionRegime.LawfulFirstExtension regime transitionId :=
  AdmissionRegime.admitted_seed_authorizes_first_extension hPermitted hSeed

theorem NGVII_01_escape_reachable_generator
    {regime : AdmissionRegime} {transitionId : TransitionId}
    (hPermitted : transitionId ∈ regime.permittedFirstExtensions)
    (hGenerator : AdmissionRegime.HasReachableGenerator regime) :
    AdmissionRegime.LawfulFirstExtension regime transitionId :=
  AdmissionRegime.reachable_generator_authorizes_first_extension
    hPermitted hGenerator

theorem NGVII_01_escape_open_external_provision
    {regime : AdmissionRegime} {transitionId : TransitionId}
    (hPermitted : transitionId ∈ regime.permittedFirstExtensions)
    (hOpen : regime.closedFamily = false)
    (hProvisioned : transitionId ∈ regime.externallyProvisionedExtensions) :
    AdmissionRegime.LawfulFirstExtension regime transitionId :=
  AdmissionRegime.open_external_provision_authorizes_first_extension
    hPermitted hOpen hProvisioned

theorem NGVII_03_no_retrospective_self_certification
    {α : Type} {before : α → α → Prop} {registered evidence : α}
    {use : CommitmentUse}
    (hRetrospective : ¬ before registered evidence) :
    ¬ CommitmentUse.ProspectivelyCertified before registered evidence use :=
  CommitmentUse.retrospective_predicate_cannot_discharge_prospective_certificate
    hRetrospective

theorem NGVII_03_escape_prospective_certificate
    {α : Type} {before : α → α → Prop} {registered evidence : α}
    {use : CommitmentUse}
    (hCertified :
      CommitmentUse.ProspectivelyCertified before registered evidence use) :
    before registered evidence :=
  CommitmentUse.prospectively_certified_has_temporal_precedence hCertified

theorem NGVII_04_no_automatic_total_lens_transfer
    {transfer : LensTransferCase}
    (hTotal : transfer.sourceLensTotal = true)
    (hSelfOwned : transfer.targetSelfOwned = true)
    (hPartial : transfer.targetPartial = true)
    (hNoAdapter : transfer.adapterCertified = false) :
    ¬ LensTransferCase.Licensed transfer :=
  LensTransferCase.no_automatic_total_lens_transfer
    hTotal hSelfOwned hPartial hNoAdapter

theorem NGVII_04_escape_certified_adapter
    {transfer : LensTransferCase}
    (hTotal : transfer.sourceLensTotal = true)
    (hSelfOwned : transfer.targetSelfOwned = true)
    (hAdapter : transfer.adapterCertified = true)
    (hAudit : transfer.audit.entries ≠ []) :
    LensTransferCase.Licensed transfer :=
  LensTransferCase.certified_adapter_licenses_totality_transfer
    hTotal hSelfOwned hAdapter hAudit

theorem NGVII_05_no_unpriced_observer_native_credit
    {record : ObserverOccupancyRecord}
    (hHidden : record.charged < record.occupied) :
    ¬ ObserverOccupancyRecord.NativeFormationCredit record :=
  ObserverOccupancyRecord.unpriced_observer_invalidates_native_formation_credit
    hHidden

theorem NGVII_05_escape_external_observer
    {record : ObserverOccupancyRecord}
    (hWellFormed : ObserverOccupancyRecord.WellFormed record)
    (hExternal : record.sourceKind = SourceKind.observer ∨
      record.sourceKind = SourceKind.externalProvision)
    (hPriced : record.charged = record.occupied) :
    ObserverOccupancyRecord.ExternalObserverCredit record :=
  ObserverOccupancyRecord.certified_external_observer_is_a_lawful_escape
    hWellFormed hExternal hPriced

theorem NGVII_05_escape_zero_occupancy
    {record : ObserverOccupancyRecord}
    (hWellFormed : ObserverOccupancyRecord.WellFormed record)
    (hNative : ObserverOccupancyRecord.NativeOrEndogenous record)
    (hOccupied : record.occupied = 0)
    (hCharged : record.charged = 0) :
    ObserverOccupancyRecord.NativeFormationCredit record :=
  ObserverOccupancyRecord.zero_occupancy_native_credit
    hWellFormed hNative hOccupied hCharged

theorem NGVII_11_no_occurrence_from_reachability_alone :
    ¬ (∀ profile : OperationalProfile,
      OperationalProfile.Coherent profile →
      profile.reachable = true → profile.occurrent = true) :=
  OperationalProfile.no_occurrence_from_reachability_alone

theorem NGVII_11_escape_fired_occurrence :
    OperationalProfile.Coherent OperationalProfile.occurrentProfile ∧
      OperationalProfile.occurrentProfile.reachable = true ∧
      OperationalProfile.occurrentProfile.fired = true ∧
      OperationalProfile.occurrentProfile.occurrent = true := by
  decide

end FoundationsVII.NoGo
