import FoundationsVII.Access.Commitment

/-!
# Origin, shared access, source independence, and totality transfer

Common provenance, shared carrier, and shared instrument are weaker than lawful
peer access.  Total-lens conclusions require a target adapter when transported
to a partial self-owned domain.
-/

namespace FoundationsVII

structure PackageAccess where
  packageId : TheoryId
  sourceId : SourceId
  carrierId : Nat
  interfaceId : InterfaceId
  instrumentId : Nat
  accessible : Bool
  peerTransportCertified : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace PackageAccess

def CommonOrigin (left right : PackageAccess) : Prop :=
  left.sourceId = right.sourceId

instance (left right : PackageAccess) : Decidable (CommonOrigin left right) := by
  unfold CommonOrigin
  infer_instance

def CommonCarrier (left right : PackageAccess) : Prop :=
  left.carrierId = right.carrierId

instance (left right : PackageAccess) : Decidable (CommonCarrier left right) := by
  unfold CommonCarrier
  infer_instance

def CommonInstrument (left right : PackageAccess) : Prop :=
  left.instrumentId = right.instrumentId

instance (left right : PackageAccess) : Decidable (CommonInstrument left right) := by
  unfold CommonInstrument
  infer_instance

def SharedAccess (left right : PackageAccess) : Prop :=
  left.accessible = true ∧
  right.accessible = true ∧
  left.interfaceId = right.interfaceId ∧
  left.peerTransportCertified = true ∧
  right.peerTransportCertified = true

instance (left right : PackageAccess) : Decidable (SharedAccess left right) := by
  unfold SharedAccess
  infer_instance

def SourceIndependent (left right : PackageAccess) : Prop :=
  left.sourceId ≠ right.sourceId

instance (left right : PackageAccess) : Decidable (SourceIndependent left right) := by
  unfold SourceIndependent
  infer_instance

def accessAudit : AuditRecord := DomainState.phase2Audit

def commonOriginLeft : PackageAccess :=
  { packageId := 1
    sourceId := 9
    carrierId := 4
    interfaceId := 2
    instrumentId := 3
    accessible := true
    peerTransportCertified := true
    audit := accessAudit }

def commonOriginRightNoAccess : PackageAccess :=
  { packageId := 2
    sourceId := 9
    carrierId := 4
    interfaceId := 2
    instrumentId := 3
    accessible := false
    peerTransportCertified := false
    audit := accessAudit }

def commonOriginRightWithAccess : PackageAccess :=
  { packageId := 2
    sourceId := 9
    carrierId := 4
    interfaceId := 2
    instrumentId := 3
    accessible := true
    peerTransportCertified := true
    audit := accessAudit }

theorem common_origin_countermodel :
    CommonOrigin commonOriginLeft commonOriginRightNoAccess ∧
    CommonCarrier commonOriginLeft commonOriginRightNoAccess ∧
    CommonInstrument commonOriginLeft commonOriginRightNoAccess ∧
    ¬ SharedAccess commonOriginLeft commonOriginRightNoAccess := by
  decide

theorem common_origin_does_not_imply_shared_access :
    ¬ (∀ left right : PackageAccess,
      CommonOrigin left right → SharedAccess left right) := by
  intro hUniversal
  have hShared := hUniversal commonOriginLeft commonOriginRightNoAccess rfl
  exact common_origin_countermodel.2.2.2 hShared

theorem shared_access_does_not_imply_source_independence :
    SharedAccess commonOriginLeft commonOriginRightWithAccess ∧
    ¬ SourceIndependent commonOriginLeft commonOriginRightWithAccess := by
  decide

theorem certified_peer_transport_is_sufficient_for_shared_access
    {left right : PackageAccess}
    (hLeft : left.accessible = true)
    (hRight : right.accessible = true)
    (hInterface : left.interfaceId = right.interfaceId)
    (hLeftTransport : left.peerTransportCertified = true)
    (hRightTransport : right.peerTransportCertified = true) :
    SharedAccess left right :=
  ⟨hLeft, hRight, hInterface, hLeftTransport, hRightTransport⟩

end PackageAccess

structure LensTransferCase where
  sourceLensTotal : Bool
  targetPartial : Bool
  targetSelfOwned : Bool
  adapterCertified : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace LensTransferCase

def Licensed (transfer : LensTransferCase) : Prop :=
  transfer.sourceLensTotal = true ∧
  transfer.targetSelfOwned = true ∧
  (transfer.targetPartial = false ∨ transfer.adapterCertified = true) ∧
  transfer.audit.entries ≠ []

theorem no_automatic_total_lens_transfer
    {transfer : LensTransferCase}
    (hTotal : transfer.sourceLensTotal = true)
    (hSelfOwned : transfer.targetSelfOwned = true)
    (hPartial : transfer.targetPartial = true)
    (hNoAdapter : transfer.adapterCertified = false) :
    ¬ Licensed transfer := by
  intro hLicensed
  rcases hLicensed.2.2.1 with hNotPartial | hAdapter
  · rw [hPartial] at hNotPartial
    exact Bool.noConfusion hNotPartial
  · rw [hNoAdapter] at hAdapter
    exact Bool.noConfusion hAdapter

theorem certified_adapter_licenses_totality_transfer
    {transfer : LensTransferCase}
    (hTotal : transfer.sourceLensTotal = true)
    (hSelfOwned : transfer.targetSelfOwned = true)
    (hAdapter : transfer.adapterCertified = true)
    (hAudit : transfer.audit.entries ≠ []) :
    Licensed transfer :=
  ⟨hTotal, hSelfOwned, Or.inr hAdapter, hAudit⟩

theorem nonpartial_target_licenses_totality_transfer
    {transfer : LensTransferCase}
    (hTotal : transfer.sourceLensTotal = true)
    (hSelfOwned : transfer.targetSelfOwned = true)
    (hNotPartial : transfer.targetPartial = false)
    (hAudit : transfer.audit.entries ≠ []) :
    Licensed transfer :=
  ⟨hTotal, hSelfOwned, Or.inl hNotPartial, hAudit⟩

end LensTransferCase

end FoundationsVII
