import SixBirdsFoundationsV.Definitional.ESystem
import SixBirdsFoundationsV.Definitional.RepairJoin
import SixBirdsFoundationsV.Laws.E1Internalization

namespace SixBirdsFoundationsV

/-!
E14 reconsolidation setup.

This setup layer mechanizes the carried memory-record, context-indexed
retrieval, direct `Delta` conflict, F9 disposition, lawful repair/coarsening,
statused residual, and provenance-defect vocabulary from the accepted E14
six-field normal form (`formalization/notes/examples/E14.md`).  The status
apparatus and E14 theorem statements are intentionally left to later
mechanization subsections.
-/

section Setup

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)

variable {X : Type z} {RecordValue : Type z'}
variable {Q : Type z''} {TransportedValue : Type z'''}
variable {FOut : Type z''''} {Readout : Type z'''''}

structure MemoryClaimRecord (X : Type u) (FOut : Type v)
    (Readout : Type w) where
  claimId : Nat
  demand : X -> FOut
  readout : FOut -> Readout

structure RetrievalContextRecord where
  contextId : Nat
  deriving DecidableEq, Repr

structure DeclaredRetrievalContextFamily where
  familyId : Nat
  contexts : List RetrievalContextRecord
  atLeastTwoContexts : contexts.length >= 2
  contextsPairwiseDistinct : contexts.Nodup

structure CarriedMemoryRecord (X : Type u) (RecordValue : Type v)
    (FOut : Type w) (Readout : Type x) where
  recordId : Nat
  version : Nat
  claimRecord : MemoryClaimRecord X FOut Readout
  recordValue : X -> RecordValue
  provenanceRootId : Nat

structure MemoryRecordFormationRecord (X : Type u) (RecordValue : Type v)
    (FOut : Type w) (Readout : Type x) where
  formationId : Nat
  memoryRecord : CarriedMemoryRecord X RecordValue FOut Readout
  formedAt : Nat

structure RetrievalTransportRecord (X : Type u) (RecordValue : Type v)
    (Q : Type w) (TransportedValue : Type x) (FOut : Type y)
    (Readout : Type z) where
  transportId : Nat
  sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout
  contextRecord : RetrievalContextRecord
  currentQuotient : X -> Q
  transportedRecord : X -> TransportedValue
  retrievedAt : Nat

structure RetrievalConflictRecord (X : Type u) (RecordValue : Type v)
    (Q : Type w) (TransportedValue : Type x) (FOut : Type y)
    (Readout : Type z) where
  conflictId : Nat
  sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout
  transportRecord :
    RetrievalTransportRecord X RecordValue Q TransportedValue FOut Readout
  claimRecord : MemoryClaimRecord X FOut Readout

inductive RecordMutationKind where
  | repair
  | coarsening
  deriving DecidableEq, Repr

structure RecordRepairPackage (X : Type u) (RecordValue : Type v) where
  repairId : Nat
  contextRecord : RetrievalContextRecord
  repairValue : X -> RecordValue

structure RecordMutationRecord (X : Type u) (RecordValue : Type v)
    (FOut : Type w) (Readout : Type x) where
  mutationId : Nat
  beforeRecord : CarriedMemoryRecord X RecordValue FOut Readout
  afterRecord : CarriedMemoryRecord X RecordValue FOut Readout
  retrievalTransportId : Nat
  contextRecord : RetrievalContextRecord
  mutationKind : RecordMutationKind

structure RecordQuotientRecord (X : Type u) (Q : Type v) where
  quotientId : Nat
  quotient : X -> Q

structure DistinctionSupportAuditRecord (X : Type u) (Q : Type v) where
  auditId : Nat
  beforeQuotient : RecordQuotientRecord X Q
  afterQuotient : RecordQuotientRecord X Q
  claimId : Nat
  mergedLeft : X
  mergedRight : X

structure MutationProvenanceRecord (X : Type u) (RecordValue : Type v)
    (FOut : Type w) (Readout : Type x) where
  provenanceId : Nat
  mutationRecord : RecordMutationRecord X RecordValue FOut Readout
  declaredParent : CarriedMemoryRecord X RecordValue FOut Readout
  declaredDerivedRecord : CarriedMemoryRecord X RecordValue FOut Readout

structure ProvenanceAuditRecord (X : Type u) (RecordValue : Type v)
    (FOut : Type w) (Readout : Type x) where
  auditId : Nat
  beforeRecord : CarriedMemoryRecord X RecordValue FOut Readout
  afterRecord : CarriedMemoryRecord X RecordValue FOut Readout
  retrievalTransportId : Nat

structure ReconsolidationResidualRecord (X : Type u)
    (RecordValue : Type v) (Q : Type w) (TransportedValue : Type x)
    (FOut : Type y) (Readout : Type z) where
  residualId : Nat
  conflictRecord :
    RetrievalConflictRecord X RecordValue Q TransportedValue FOut Readout
  residualAmount : Rat

inductive ReconsolidationDisposition where
  | record_repair
  | record_coarsening
  | statused_unresolved
  deriving DecidableEq, Repr

structure ReconsolidationDispositionRecord (X : Type u)
    (RecordValue : Type v) (Q : Type w) (TransportedValue : Type x)
    (FOut : Type y) (Readout : Type z) where
  dispositionId : Nat
  conflictRecord :
    RetrievalConflictRecord X RecordValue Q TransportedValue FOut Readout
  disposition : ReconsolidationDisposition
  supportingMutation :
    Option (RecordMutationRecord X RecordValue FOut Readout)
  supportingResidual :
    Option
      (ReconsolidationResidualRecord X RecordValue Q TransportedValue
        FOut Readout)

structure ReconsolidationClassifierContext
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (X : Type z) (RecordValue : Type z') (Q : Type z'')
    (TransportedValue : Type z''') (FOut : Type z'''')
    (Readout : Type z''''') where
  f20RecordFormed :
    MemoryRecordFormationRecord X RecordValue FOut Readout -> Prop
  retrievalDeclared :
    RetrievalTransportRecord X RecordValue Q TransportedValue FOut Readout ->
      Prop
  repairMoveInstallsJoin :
    RepairMove S.T MovePayload LedgerEntry MoveRecord S.moveRecordPolicy ->
      RecordRepairPackage X RecordValue ->
      CarriedMemoryRecord X RecordValue FOut Readout ->
      CarriedMemoryRecord X RecordValue FOut Readout -> Prop
  recordUsesQuotient :
    CarriedMemoryRecord X RecordValue FOut Readout ->
      RecordQuotientRecord X Q -> Prop
  coarseningMoveInstallsRecord :
    RepairMove S.T MovePayload LedgerEntry MoveRecord S.moveRecordPolicy ->
      CarriedMemoryRecord X RecordValue FOut Readout ->
      CarriedMemoryRecord X RecordValue FOut Readout ->
      RecordQuotientRecord X Q -> RecordQuotientRecord X Q -> Prop
  distinctionNoLongerSupportable :
    DistinctionSupportAuditRecord X Q ->
      MemoryClaimRecord X FOut Readout -> Prop
  f9ClassifiesNativeConflict :
    RetrievalConflictRecord X RecordValue Q TransportedValue FOut Readout ->
      ReconsolidationDispositionRecord X RecordValue Q TransportedValue
        FOut Readout -> Prop
  ledgerEntryChargesResidual :
    LedgerEntry ->
      ReconsolidationResidualRecord X RecordValue Q TransportedValue
        FOut Readout -> Rat -> Prop
  provenanceMatchesMutation :
    MutationProvenanceRecord X RecordValue FOut Readout -> Prop

structure ReconsolidationEvidencePolicies
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (X : Type z) (RecordValue : Type z') (Q : Type z'')
    (TransportedValue : Type z''') (FOut : Type z'''')
    (Readout : Type z''''') where
  memoryPolicy :
    CarriedRecordPolicy S.T (CarriedMemoryRecord X RecordValue FOut Readout)
  claimPolicy :
    CarriedRecordPolicy S.T (MemoryClaimRecord X FOut Readout)
  formationPolicy :
    CarriedRecordPolicy S.T
      (MemoryRecordFormationRecord X RecordValue FOut Readout)
  contextPolicy : CarriedRecordPolicy S.T RetrievalContextRecord
  contextFamilyPolicy :
    CarriedRecordPolicy S.T DeclaredRetrievalContextFamily
  transportPolicy :
    CarriedRecordPolicy S.T
      (RetrievalTransportRecord X RecordValue Q TransportedValue FOut Readout)
  conflictPolicy :
    CarriedRecordPolicy S.T
      (RetrievalConflictRecord X RecordValue Q TransportedValue FOut Readout)
  repairPackagePolicy :
    CarriedRecordPolicy S.T (RecordRepairPackage X RecordValue)
  mutationPolicy :
    CarriedRecordPolicy S.T
      (RecordMutationRecord X RecordValue FOut Readout)
  quotientPolicy :
    CarriedRecordPolicy S.T (RecordQuotientRecord X Q)
  distinctionAuditPolicy :
    CarriedRecordPolicy S.T (DistinctionSupportAuditRecord X Q)
  provenancePolicy :
    CarriedRecordPolicy S.T
      (MutationProvenanceRecord X RecordValue FOut Readout)
  provenanceAuditPolicy :
    CarriedRecordPolicy S.T
      (ProvenanceAuditRecord X RecordValue FOut Readout)
  residualPolicy :
    CarriedRecordPolicy S.T
      (ReconsolidationResidualRecord X RecordValue Q TransportedValue
        FOut Readout)
  dispositionPolicy :
    CarriedRecordPolicy S.T
      (ReconsolidationDispositionRecord X RecordValue Q TransportedValue
        FOut Readout)

structure F20CarriedMemoryRecord
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (memoryRecord : CarriedMemoryRecord X RecordValue FOut Readout) where
  formationRecord : MemoryRecordFormationRecord X RecordValue FOut Readout
  formationLinked : formationRecord.memoryRecord = memoryRecord
  memoryCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.memoryPolicy memoryRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  claimCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.claimPolicy memoryRecord.claimRecord n0
          sourceTag generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  formationCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.formationPolicy formationRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  formedByF20Contract : ctx.f20RecordFormed formationRecord

structure DeclaredRetrievalTransport
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout)
    (family : DeclaredRetrievalContextFamily) where
  transportRecord :
    RetrievalTransportRecord X RecordValue Q TransportedValue FOut Readout
  sourceLinked : transportRecord.sourceRecord = sourceRecord
  contextMember : transportRecord.contextRecord ∈ family.contexts
  sourceCarried : F20CarriedMemoryRecord S ctx policies sourceRecord
  contextCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.contextPolicy transportRecord.contextRecord n0
          sourceTag generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  contextFamilyCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.contextFamilyPolicy family n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  transportCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.transportPolicy transportRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  declaredByHost : ctx.retrievalDeclared transportRecord

structure CompleteRetrievalTransportInventory
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout)
    (family : DeclaredRetrievalContextFamily) where
  declaredTransports :
    List (RetrievalTransportRecord X RecordValue Q TransportedValue
      FOut Readout)
  completeForClaim :
    ∀ transport :
      DeclaredRetrievalTransport S ctx policies sourceRecord family,
      transport.transportRecord ∈ declaredTransports
  soundForClaim :
    ∀ transportRecord :
        RetrievalTransportRecord X RecordValue Q TransportedValue FOut Readout,
      transportRecord ∈ declaredTransports ->
      ∃ transport :
        DeclaredRetrievalTransport S ctx policies sourceRecord family,
        transport.transportRecord = transportRecord
  everyContextCovered :
    ∀ context : RetrievalContextRecord, context ∈ family.contexts ->
      ∃ transportRecord :
          RetrievalTransportRecord X RecordValue Q TransportedValue FOut Readout,
        transportRecord ∈ declaredTransports ∧
        transportRecord.contextRecord = context
  transportSingleValuedPerContext :
    ∀ transport1 :
        RetrievalTransportRecord X RecordValue Q TransportedValue FOut Readout,
      transport1 ∈ declaredTransports ->
      ∀ transport2 :
          RetrievalTransportRecord X RecordValue Q TransportedValue FOut Readout,
        transport2 ∈ declaredTransports ->
        transport1.contextRecord = transport2.contextRecord ->
        ∀ x : X,
          transport1.transportedRecord x = transport2.transportedRecord x

structure ContextDependentRetrieval
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout)
    (family : DeclaredRetrievalContextFamily)
    (inventory : CompleteRetrievalTransportInventory S ctx policies
      sourceRecord family) where
  transport1 :
    RetrievalTransportRecord X RecordValue Q TransportedValue FOut Readout
  transport2 :
    RetrievalTransportRecord X RecordValue Q TransportedValue FOut Readout
  transport1Declared : transport1 ∈ inventory.declaredTransports
  transport2Declared : transport2 ∈ inventory.declaredTransports
  distinctContexts : transport1.contextRecord ≠ transport2.contextRecord
  contextChangesTransport :
    ∃ x : X, transport1.transportedRecord x ≠ transport2.transportedRecord x

structure RetrievalWithoutTransportEvidence
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout)
    (family : DeclaredRetrievalContextFamily)
    (inventory : CompleteRetrievalTransportInventory S ctx policies
      sourceRecord family) where
  contextInvariant :
    ∀ transport1 :
        RetrievalTransportRecord X RecordValue Q TransportedValue FOut Readout,
      transport1 ∈ inventory.declaredTransports ->
      ∀ transport2 :
          RetrievalTransportRecord X RecordValue Q TransportedValue FOut Readout,
        transport2 ∈ inventory.declaredTransports ->
        ∀ x : X,
          transport1.transportedRecord x = transport2.transportedRecord x

structure RetrievalConflictEvidence
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout)
    (family : DeclaredRetrievalContextFamily) where
  transport : DeclaredRetrievalTransport S ctx policies sourceRecord family
  conflictRecord :
    RetrievalConflictRecord X RecordValue Q TransportedValue FOut Readout
  conflictLinked :
    conflictRecord.sourceRecord = sourceRecord ∧
    conflictRecord.transportRecord = transport.transportRecord ∧
    conflictRecord.claimRecord = sourceRecord.claimRecord
  conflictCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.conflictPolicy conflictRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  deltaConflict :
    ∃ x x' : X,
      Delta
        (repairJoin transport.transportRecord.currentQuotient
          transport.transportRecord.transportedRecord)
        sourceRecord.claimRecord.demand sourceRecord.claimRecord.readout x x'

structure ReconsolidationTrigger
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout)
    (family : DeclaredRetrievalContextFamily) where
  inventory :
    CompleteRetrievalTransportInventory S ctx policies sourceRecord family
  contextDependent :
    ContextDependentRetrieval S ctx policies sourceRecord family inventory
  conflict : RetrievalConflictEvidence S ctx policies sourceRecord family
  conflictTransportDeclared :
    conflict.transport.transportRecord ∈ inventory.declaredTransports

structure CompleteReconsolidationDispositionInventory
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (conflictRecord :
      RetrievalConflictRecord X RecordValue Q TransportedValue FOut Readout) where
  declaredDispositions :
    List (ReconsolidationDispositionRecord X RecordValue Q TransportedValue
      FOut Readout)
  completeForConflict :
    ∀ dispositionRecord,
      dispositionRecord.conflictRecord = conflictRecord ->
      ctx.f9ClassifiesNativeConflict conflictRecord dispositionRecord ->
      (∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
        ∃ generatedByS : Bool, ∃ inScope : Bool,
          CarriedRecordAt policies.dispositionPolicy dispositionRecord n0
            sourceTag generatedByS inScope ∧
          CarriedSource sourceTag generatedByS inScope) ->
      dispositionRecord ∈ declaredDispositions
  soundForConflict :
    ∀ dispositionRecord, dispositionRecord ∈ declaredDispositions ->
      dispositionRecord.conflictRecord = conflictRecord ∧
      ctx.f9ClassifiesNativeConflict conflictRecord dispositionRecord ∧
      ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
        ∃ generatedByS : Bool, ∃ inScope : Bool,
          CarriedRecordAt policies.dispositionPolicy dispositionRecord n0
            sourceTag generatedByS inScope ∧
          CarriedSource sourceTag generatedByS inScope
  statusSingleValued :
    ∀ disposition1, disposition1 ∈ declaredDispositions ->
      ∀ disposition2, disposition2 ∈ declaredDispositions ->
        disposition1.disposition = disposition2.disposition

structure F9ReconsolidationCoverageCertified
    {ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout}
    {policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout}
    {conflictRecord :
      RetrievalConflictRecord X RecordValue Q TransportedValue FOut Readout}
    (inventory : CompleteReconsolidationDispositionInventory S ctx policies
      conflictRecord) where
  dispositionRecord :
    ReconsolidationDispositionRecord X RecordValue Q TransportedValue
      FOut Readout
  dispositionDeclared : dispositionRecord ∈ inventory.declaredDispositions

def NoF9DispositionFor
    {ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout}
    {policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout}
    {conflictRecord :
      RetrievalConflictRecord X RecordValue Q TransportedValue FOut Readout}
    (inventory : CompleteReconsolidationDispositionInventory S ctx policies
      conflictRecord) : Prop :=
  inventory.declaredDispositions = []

structure RecordRepairEvidence
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout)
    (family : DeclaredRetrievalContextFamily)
    (trigger : ReconsolidationTrigger S ctx policies sourceRecord family) where
  repairPackage : RecordRepairPackage X RecordValue
  afterRecord : CarriedMemoryRecord X RecordValue FOut Readout
  mutationRecord : RecordMutationRecord X RecordValue FOut Readout
  provenanceRecord : MutationProvenanceRecord X RecordValue FOut Readout
  zBefore : S.T.Z
  zAfter : S.T.Z
  defect : DefectRecord
  auditRecord : AuditRecord
  repairPackageCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.repairPackagePolicy repairPackage n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  afterRecordCarried :
    F20CarriedMemoryRecord S ctx policies afterRecord
  mutationCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.mutationPolicy mutationRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  provenanceCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.provenancePolicy provenanceRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  mutationLinked :
    mutationRecord.beforeRecord = sourceRecord ∧
    mutationRecord.afterRecord = afterRecord ∧
    mutationRecord.retrievalTransportId =
      trigger.conflict.transport.transportRecord.transportId ∧
    mutationRecord.contextRecord =
      trigger.conflict.transport.transportRecord.contextRecord ∧
    mutationRecord.mutationKind = RecordMutationKind.repair
  provenanceLinked :
    provenanceRecord.mutationRecord = mutationRecord ∧
    provenanceRecord.declaredParent = sourceRecord ∧
    provenanceRecord.declaredDerivedRecord = afterRecord
  provenanceHonest : ctx.provenanceMatchesMutation provenanceRecord
  recordIdentityPreserved : afterRecord.recordId = sourceRecord.recordId
  claimPreserved : afterRecord.claimRecord = sourceRecord.claimRecord
  versionAdvances : afterRecord.version = sourceRecord.version + 1
  lawfulRepairStep : ESystem.RepairStep S zBefore zAfter defect auditRecord
  installsRecordJoin :
    ctx.repairMoveInstallsJoin (S.R_S defect) repairPackage sourceRecord
      afterRecord
  repairContextLinked :
    repairPackage.contextRecord =
      trigger.conflict.transport.transportRecord.contextRecord

structure RecordCoarseningEvidence
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout)
    (family : DeclaredRetrievalContextFamily)
    (trigger : ReconsolidationTrigger S ctx policies sourceRecord family) where
  afterRecord : CarriedMemoryRecord X RecordValue FOut Readout
  beforeQuotient : RecordQuotientRecord X Q
  afterQuotient : RecordQuotientRecord X Q
  supportAudit : DistinctionSupportAuditRecord X Q
  mutationRecord : RecordMutationRecord X RecordValue FOut Readout
  provenanceRecord : MutationProvenanceRecord X RecordValue FOut Readout
  zBefore : S.T.Z
  zAfter : S.T.Z
  defect : DefectRecord
  auditRecord : AuditRecord
  afterRecordCarried :
    F20CarriedMemoryRecord S ctx policies afterRecord
  beforeQuotientCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.quotientPolicy beforeQuotient n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  afterQuotientCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.quotientPolicy afterQuotient n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  supportAuditCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.distinctionAuditPolicy supportAudit n0
          sourceTag generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  mutationCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.mutationPolicy mutationRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  provenanceCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.provenancePolicy provenanceRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  quotientLinked :
    ctx.recordUsesQuotient sourceRecord beforeQuotient ∧
    ctx.recordUsesQuotient afterRecord afterQuotient ∧
    supportAudit.beforeQuotient = beforeQuotient ∧
    supportAudit.afterQuotient = afterQuotient ∧
    supportAudit.claimId = sourceRecord.claimRecord.claimId
  coarsens : Refines beforeQuotient.quotient afterQuotient.quotient
  strictMerge :
    afterQuotient.quotient supportAudit.mergedLeft =
      afterQuotient.quotient supportAudit.mergedRight ∧
    beforeQuotient.quotient supportAudit.mergedLeft ≠
      beforeQuotient.quotient supportAudit.mergedRight
  distinctionUnsupported :
    ctx.distinctionNoLongerSupportable supportAudit sourceRecord.claimRecord
  mutationLinked :
    mutationRecord.beforeRecord = sourceRecord ∧
    mutationRecord.afterRecord = afterRecord ∧
    mutationRecord.retrievalTransportId =
      trigger.conflict.transport.transportRecord.transportId ∧
    mutationRecord.contextRecord =
      trigger.conflict.transport.transportRecord.contextRecord ∧
    mutationRecord.mutationKind = RecordMutationKind.coarsening
  provenanceLinked :
    provenanceRecord.mutationRecord = mutationRecord ∧
    provenanceRecord.declaredParent = sourceRecord ∧
    provenanceRecord.declaredDerivedRecord = afterRecord
  provenanceHonest : ctx.provenanceMatchesMutation provenanceRecord
  recordIdentityPreserved : afterRecord.recordId = sourceRecord.recordId
  claimPreserved : afterRecord.claimRecord = sourceRecord.claimRecord
  versionAdvances : afterRecord.version = sourceRecord.version + 1
  lawfulCoarseningStep :
    ESystem.RepairStep S zBefore zAfter defect auditRecord
  moveInstallsCoarsening :
    ctx.coarseningMoveInstallsRecord (S.R_S defect) sourceRecord afterRecord
      beforeQuotient afterQuotient

structure StatusedUnresolvedEvidence
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout)
    (family : DeclaredRetrievalContextFamily)
    (trigger : ReconsolidationTrigger S ctx policies sourceRecord family) where
  currentRecordAtStatus : CarriedMemoryRecord X RecordValue FOut Readout
  residualRecord :
    ReconsolidationResidualRecord X RecordValue Q TransportedValue FOut Readout
  ledgerEntry : LedgerEntry
  currentRecordCarried :
    F20CarriedMemoryRecord S ctx policies currentRecordAtStatus
  recordIdentityPreserved :
    currentRecordAtStatus.recordId = sourceRecord.recordId
  claimPreserved :
    currentRecordAtStatus.claimRecord = sourceRecord.claimRecord
  versionUnchanged : currentRecordAtStatus.version = sourceRecord.version
  provenanceRootPreserved :
    currentRecordAtStatus.provenanceRootId = sourceRecord.provenanceRootId
  valueUnchanged :
    ∀ x : X,
      currentRecordAtStatus.recordValue x = sourceRecord.recordValue x
  residualCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.residualPolicy residualRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  residualLinked :
    residualRecord.conflictRecord = trigger.conflict.conflictRecord
  positiveCharge : 0 < residualRecord.residualAmount
  ledgerEntryPresent : ledgerEntry ∈ S.Lambda_S.ledgerEntries
  ledgerEntryCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt S.Lambda_S.ledgerPolicy ledgerEntry n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  chargedToExistingLedger :
    ctx.ledgerEntryChargesResidual ledgerEntry residualRecord
      residualRecord.residualAmount

structure CompleteReconsolidationOutcomeInventory
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout)
    (family : DeclaredRetrievalContextFamily)
    (trigger : ReconsolidationTrigger S ctx policies sourceRecord family) where
  repairMutationRecords :
    List (RecordMutationRecord X RecordValue FOut Readout)
  coarseningMutationRecords :
    List (RecordMutationRecord X RecordValue FOut Readout)
  unresolvedResidualRecords :
    List (ReconsolidationResidualRecord X RecordValue Q TransportedValue
      FOut Readout)
  completeRepairs :
    ∀ evidence :
      RecordRepairEvidence S ctx policies sourceRecord family trigger,
      evidence.mutationRecord ∈ repairMutationRecords
  completeCoarsenings :
    ∀ evidence :
      RecordCoarseningEvidence S ctx policies sourceRecord family trigger,
      evidence.mutationRecord ∈ coarseningMutationRecords
  completeUnresolved :
    ∀ evidence :
      StatusedUnresolvedEvidence S ctx policies sourceRecord family trigger,
      evidence.residualRecord ∈ unresolvedResidualRecords
  soundRepairs :
    ∀ mutationRecord : RecordMutationRecord X RecordValue FOut Readout,
      mutationRecord ∈ repairMutationRecords ->
      ∃ evidence :
        RecordRepairEvidence S ctx policies sourceRecord family trigger,
        evidence.mutationRecord = mutationRecord
  soundCoarsenings :
    ∀ mutationRecord : RecordMutationRecord X RecordValue FOut Readout,
      mutationRecord ∈ coarseningMutationRecords ->
      ∃ evidence :
        RecordCoarseningEvidence S ctx policies sourceRecord family trigger,
        evidence.mutationRecord = mutationRecord
  soundUnresolved :
    ∀ residualRecord :
        ReconsolidationResidualRecord X RecordValue Q TransportedValue
          FOut Readout,
      residualRecord ∈ unresolvedResidualRecords ->
      ∃ evidence :
        StatusedUnresolvedEvidence S ctx policies sourceRecord family trigger,
        evidence.residualRecord = residualRecord

def NoReconsolidationOutcomeFor
    {ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout}
    {policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout}
    {sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout}
    {family : DeclaredRetrievalContextFamily}
    {trigger : ReconsolidationTrigger S ctx policies sourceRecord family}
    (inventory : CompleteReconsolidationOutcomeInventory S ctx policies
      sourceRecord family trigger) : Prop :=
  inventory.repairMutationRecords = [] ∧
  inventory.coarseningMutationRecords = [] ∧
  inventory.unresolvedResidualRecords = []

def DispositionRealizedByInventory
    {ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout}
    {policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout}
    {sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout}
    {family : DeclaredRetrievalContextFamily}
    {trigger : ReconsolidationTrigger S ctx policies sourceRecord family}
    {dispositionInventory :
      CompleteReconsolidationDispositionInventory S ctx policies
        trigger.conflict.conflictRecord}
    (coverage : F9ReconsolidationCoverageCertified S dispositionInventory)
    (inventory : CompleteReconsolidationOutcomeInventory S ctx policies
      sourceRecord family trigger) : Prop :=
  (coverage.dispositionRecord.disposition =
      ReconsolidationDisposition.record_repair ∧
    coverage.dispositionRecord.supportingResidual = none ∧
    ∃ mutationRecord, mutationRecord ∈ inventory.repairMutationRecords ∧
      coverage.dispositionRecord.supportingMutation = some mutationRecord) ∨
  (coverage.dispositionRecord.disposition =
      ReconsolidationDisposition.record_coarsening ∧
    coverage.dispositionRecord.supportingResidual = none ∧
    ∃ mutationRecord,
      mutationRecord ∈ inventory.coarseningMutationRecords ∧
      coverage.dispositionRecord.supportingMutation = some mutationRecord) ∨
  (coverage.dispositionRecord.disposition =
      ReconsolidationDisposition.statused_unresolved ∧
    coverage.dispositionRecord.supportingMutation = none ∧
    ∃ residualRecord,
      residualRecord ∈ inventory.unresolvedResidualRecords ∧
      coverage.dispositionRecord.supportingResidual = some residualRecord)

structure UnrealizedDispositionEvidence
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout)
    (family : DeclaredRetrievalContextFamily)
    (trigger : ReconsolidationTrigger S ctx policies sourceRecord family)
    (dispositionInventory :
      CompleteReconsolidationDispositionInventory S ctx policies
        trigger.conflict.conflictRecord)
    (outcomeInventory :
      CompleteReconsolidationOutcomeInventory S ctx policies sourceRecord
        family trigger) where
  coverage : F9ReconsolidationCoverageCertified S dispositionInventory
  notRealized :
    ¬ DispositionRealizedByInventory S coverage outcomeInventory

structure ReconsolidationOutcomeCollision
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout)
    (family : DeclaredRetrievalContextFamily)
    (trigger : ReconsolidationTrigger S ctx policies sourceRecord family) where
  collision :
    (Nonempty
        (RecordRepairEvidence S ctx policies sourceRecord family trigger) ∧
      Nonempty
        (RecordCoarseningEvidence S ctx policies sourceRecord family trigger)) ∨
    (Nonempty
        (RecordRepairEvidence S ctx policies sourceRecord family trigger) ∧
      Nonempty
        (StatusedUnresolvedEvidence S ctx policies sourceRecord family trigger)) ∨
    (Nonempty
        (RecordCoarseningEvidence S ctx policies sourceRecord family trigger) ∧
      Nonempty
        (StatusedUnresolvedEvidence S ctx policies sourceRecord family trigger))

structure CompleteMutationProvenanceInventory
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (beforeRecord afterRecord :
      CarriedMemoryRecord X RecordValue FOut Readout)
    (retrievalTransportId : Nat) where
  declaredProvenanceRecords :
    List (MutationProvenanceRecord X RecordValue FOut Readout)
  completeForMutation :
    ∀ provenanceRecord : MutationProvenanceRecord X RecordValue FOut Readout,
      provenanceRecord.mutationRecord.beforeRecord = beforeRecord ->
      provenanceRecord.mutationRecord.afterRecord = afterRecord ->
      provenanceRecord.mutationRecord.retrievalTransportId =
        retrievalTransportId ->
      (∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
        ∃ generatedByS : Bool, ∃ inScope : Bool,
          CarriedRecordAt policies.provenancePolicy provenanceRecord n0
            sourceTag generatedByS inScope ∧
          CarriedSource sourceTag generatedByS inScope) ->
      provenanceRecord ∈ declaredProvenanceRecords

def NoMutationProvenanceFor
    {policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout}
    {beforeRecord afterRecord :
      CarriedMemoryRecord X RecordValue FOut Readout}
    {retrievalTransportId : Nat}
    (inventory : CompleteMutationProvenanceInventory S policies beforeRecord
      afterRecord retrievalTransportId) : Prop :=
  inventory.declaredProvenanceRecords = []

structure SilentRewriteEvidence
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout)
    (family : DeclaredRetrievalContextFamily)
    (trigger : ReconsolidationTrigger S ctx policies sourceRecord family)
    (dispositionInventory :
      CompleteReconsolidationDispositionInventory S ctx policies
        trigger.conflict.conflictRecord)
    (outcomeInventory :
      CompleteReconsolidationOutcomeInventory S ctx policies sourceRecord
        family trigger) where
  afterRecord : CarriedMemoryRecord X RecordValue FOut Readout
  auditRecord : ProvenanceAuditRecord X RecordValue FOut Readout
  afterRecordCarried :
    F20CarriedMemoryRecord S ctx policies afterRecord
  auditCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.provenanceAuditPolicy auditRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  auditLinked :
    auditRecord.beforeRecord = sourceRecord ∧
    auditRecord.afterRecord = afterRecord ∧
    auditRecord.retrievalTransportId =
      trigger.conflict.transport.transportRecord.transportId
  valueChanged :
    ∃ x : X, sourceRecord.recordValue x ≠ afterRecord.recordValue x
  sameRecordIdentity : afterRecord.recordId = sourceRecord.recordId
  sameClaim : afterRecord.claimRecord = sourceRecord.claimRecord
  noAuthorizedOutcome : NoReconsolidationOutcomeFor S outcomeInventory
  noTypedDisposition : NoF9DispositionFor S dispositionInventory
  provenanceInventory :
    CompleteMutationProvenanceInventory S policies sourceRecord afterRecord
      trigger.conflict.transport.transportRecord.transportId
  noProvenance : NoMutationProvenanceFor S provenanceInventory

structure LaunderedProvenanceDefect
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout)
    (family : DeclaredRetrievalContextFamily)
    (trigger : ReconsolidationTrigger S ctx policies sourceRecord family) where
  afterRecord : CarriedMemoryRecord X RecordValue FOut Readout
  mutationRecord : RecordMutationRecord X RecordValue FOut Readout
  provenanceRecord : MutationProvenanceRecord X RecordValue FOut Readout
  auditRecord : ProvenanceAuditRecord X RecordValue FOut Readout
  afterRecordCarried :
    F20CarriedMemoryRecord S ctx policies afterRecord
  mutationCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.mutationPolicy mutationRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  provenanceCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.provenancePolicy provenanceRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  auditCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.provenanceAuditPolicy auditRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  mutationLinked :
    mutationRecord.beforeRecord = sourceRecord ∧
    mutationRecord.afterRecord = afterRecord ∧
    mutationRecord.retrievalTransportId =
      trigger.conflict.transport.transportRecord.transportId
  auditLinked :
    auditRecord.beforeRecord = sourceRecord ∧
    auditRecord.afterRecord = afterRecord ∧
    auditRecord.retrievalTransportId = mutationRecord.retrievalTransportId
  valueChanged :
    ∃ x : X, sourceRecord.recordValue x ≠ afterRecord.recordValue x
  sameRecordIdentity : afterRecord.recordId = sourceRecord.recordId
  sameClaim : afterRecord.claimRecord = sourceRecord.claimRecord
  provenancePurportsToCoverMutation :
    provenanceRecord.mutationRecord = mutationRecord
  lineageLaundered : ¬ ctx.provenanceMatchesMutation provenanceRecord

structure UnstatusedConflictEvidence
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout)
    (family : DeclaredRetrievalContextFamily)
    (trigger : ReconsolidationTrigger S ctx policies sourceRecord family)
    (dispositionInventory :
      CompleteReconsolidationDispositionInventory S ctx policies
        trigger.conflict.conflictRecord) where
  noF9Disposition : NoF9DispositionFor S dispositionInventory

end Setup

section StatusApparatus

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)

variable {X : Type z} {RecordValue : Type z'}
variable {Q : Type z''} {TransportedValue : Type z'''}
variable {FOut : Type z''''} {Readout : Type z'''''}

inductive ReconsolidationStatus where
  | provenance_defect
  | silent_rewrite
  | ordinary_read
  | outcome_collision
  | unrealized_disposition
  | record_repaired
  | record_coarsened
  | statused_unresolved
  | unstatused_conflict
  deriving DecidableEq, Repr

structure ReconsolidationClaimRef
    (X : Type u) (RecordValue : Type v) (Q : Type w)
    (TransportedValue : Type x) (FOut : Type y) (Readout : Type z) where
  sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout
  family : DeclaredRetrievalContextFamily
  transportRecord :
    RetrievalTransportRecord X RecordValue Q TransportedValue FOut Readout
  contextRecord : RetrievalContextRecord
  claimRecord : MemoryClaimRecord X FOut Readout
  sourceLinked : transportRecord.sourceRecord = sourceRecord
  contextLinked : transportRecord.contextRecord = contextRecord
  contextMember : contextRecord ∈ family.contexts
  claimLinked : sourceRecord.claimRecord = claimRecord

structure ReconsolidationStatusRecord
    (X : Type u) (RecordValue : Type v) (Q : Type w)
    (TransportedValue : Type x) (FOut : Type y) (Readout : Type z) where
  statusRecordId : Nat
  status : ReconsolidationStatus
  sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout
  family : DeclaredRetrievalContextFamily
  transportRecord :
    RetrievalTransportRecord X RecordValue Q TransportedValue FOut Readout
  contextRecord : RetrievalContextRecord
  claimRecord : MemoryClaimRecord X FOut Readout
  conflictRecord :
    Option
      (RetrievalConflictRecord X RecordValue Q TransportedValue FOut Readout)
  mutationRecord :
    Option (RecordMutationRecord X RecordValue FOut Readout)
  residualRecord :
    Option
      (ReconsolidationResidualRecord X RecordValue Q TransportedValue
        FOut Readout)
  dispositionRecord :
    Option
      (ReconsolidationDispositionRecord X RecordValue Q TransportedValue
        FOut Readout)
  provenanceAuditRecord :
    Option (ProvenanceAuditRecord X RecordValue FOut Readout)

def ReconsolidationStatusRecordMatchesClaim
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  record.sourceRecord = claimRef.sourceRecord ∧
  record.family = claimRef.family ∧
  record.transportRecord = claimRef.transportRecord ∧
  record.contextRecord = claimRef.contextRecord ∧
  record.claimRecord = claimRef.claimRecord ∧
  claimRef.transportRecord.sourceRecord = claimRef.sourceRecord ∧
  claimRef.transportRecord.contextRecord = claimRef.contextRecord ∧
  claimRef.sourceRecord.claimRecord = claimRef.claimRecord

def ReconsolidationStatusOccurrenceFor
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ReconsolidationStatusRecordMatchesClaim claimRef record ∧
  ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
    ∃ generatedByS : Bool, ∃ inScope : Bool,
      CarriedRecordAt statusPolicy record n0 sourceTag generatedByS inScope ∧
      CarriedSource sourceTag generatedByS inScope

def ProvenanceDefectEvidenceFor
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    trigger.conflict.transport.transportRecord = claimRef.transportRecord ∧
    Nonempty (LaunderedProvenanceDefect S ctx policies claimRef.sourceRecord
      claimRef.family trigger)

def SilentRewriteEvidenceFor
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    trigger.conflict.transport.transportRecord = claimRef.transportRecord ∧
    ∃ dispositionInventory :
        CompleteReconsolidationDispositionInventory S ctx policies
          trigger.conflict.conflictRecord,
      ∃ outcomeInventory :
          CompleteReconsolidationOutcomeInventory S ctx policies
            claimRef.sourceRecord claimRef.family trigger,
        Nonempty (SilentRewriteEvidence S ctx policies claimRef.sourceRecord
          claimRef.family trigger dispositionInventory outcomeInventory)

def OrdinaryReadEvidenceFor
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ inventory : CompleteRetrievalTransportInventory S ctx policies
      claimRef.sourceRecord claimRef.family,
    claimRef.transportRecord ∈ inventory.declaredTransports ∧
    Nonempty (RetrievalWithoutTransportEvidence S ctx policies
      claimRef.sourceRecord claimRef.family inventory)

def OutcomeCollisionEvidenceFor
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    trigger.conflict.transport.transportRecord = claimRef.transportRecord ∧
    Nonempty (ReconsolidationOutcomeCollision S ctx policies
      claimRef.sourceRecord claimRef.family trigger)

def UnrealizedDispositionEvidenceFor
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    trigger.conflict.transport.transportRecord = claimRef.transportRecord ∧
    ∃ dispositionInventory :
        CompleteReconsolidationDispositionInventory S ctx policies
          trigger.conflict.conflictRecord,
      ∃ outcomeInventory :
          CompleteReconsolidationOutcomeInventory S ctx policies
            claimRef.sourceRecord claimRef.family trigger,
        Nonempty (UnrealizedDispositionEvidence S ctx policies
          claimRef.sourceRecord claimRef.family trigger dispositionInventory
          outcomeInventory)

def RecordRepairEvidenceFor
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    trigger.conflict.transport.transportRecord = claimRef.transportRecord ∧
    ∃ dispositionInventory :
        CompleteReconsolidationDispositionInventory S ctx policies
          trigger.conflict.conflictRecord,
      ∃ f9Coverage :
          F9ReconsolidationCoverageCertified S dispositionInventory,
        ∃ repair : RecordRepairEvidence S ctx policies claimRef.sourceRecord
            claimRef.family trigger,
          f9Coverage.dispositionRecord.disposition =
            ReconsolidationDisposition.record_repair ∧
          f9Coverage.dispositionRecord.supportingMutation =
            some repair.mutationRecord ∧
          f9Coverage.dispositionRecord.supportingResidual = none

def RecordCoarseningEvidenceFor
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    trigger.conflict.transport.transportRecord = claimRef.transportRecord ∧
    ∃ dispositionInventory :
        CompleteReconsolidationDispositionInventory S ctx policies
          trigger.conflict.conflictRecord,
      ∃ f9Coverage :
          F9ReconsolidationCoverageCertified S dispositionInventory,
        ∃ coarsening : RecordCoarseningEvidence S ctx policies
            claimRef.sourceRecord claimRef.family trigger,
          f9Coverage.dispositionRecord.disposition =
            ReconsolidationDisposition.record_coarsening ∧
          f9Coverage.dispositionRecord.supportingMutation =
            some coarsening.mutationRecord ∧
          f9Coverage.dispositionRecord.supportingResidual = none

def StatusedUnresolvedEvidenceFor
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    trigger.conflict.transport.transportRecord = claimRef.transportRecord ∧
    ∃ dispositionInventory :
        CompleteReconsolidationDispositionInventory S ctx policies
          trigger.conflict.conflictRecord,
      ∃ f9Coverage :
          F9ReconsolidationCoverageCertified S dispositionInventory,
        ∃ unresolved : StatusedUnresolvedEvidence S ctx policies
            claimRef.sourceRecord claimRef.family trigger,
          f9Coverage.dispositionRecord.disposition =
            ReconsolidationDisposition.statused_unresolved ∧
          f9Coverage.dispositionRecord.supportingMutation = none ∧
          f9Coverage.dispositionRecord.supportingResidual =
            some unresolved.residualRecord

def UnstatusedConflictEvidenceFor
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    trigger.conflict.transport.transportRecord = claimRef.transportRecord ∧
    ∃ dispositionInventory :
        CompleteReconsolidationDispositionInventory S ctx policies
          trigger.conflict.conflictRecord,
      Nonempty (UnstatusedConflictEvidence S ctx policies
        claimRef.sourceRecord claimRef.family trigger dispositionInventory)

def ProvenanceDefectCase
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    ∃ defect : LaunderedProvenanceDefect S ctx policies claimRef.sourceRecord
        claimRef.family trigger,
      trigger.conflict.transport.transportRecord = claimRef.transportRecord ∧
      record.conflictRecord = some trigger.conflict.conflictRecord ∧
      record.provenanceAuditRecord = some defect.auditRecord ∧
      record.status = ReconsolidationStatus.provenance_defect

def SilentRewriteCase
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
  ¬ ProvenanceDefectEvidenceFor S ctx policies claimRef ∧
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    ∃ dispositionInventory :
        CompleteReconsolidationDispositionInventory S ctx policies
          trigger.conflict.conflictRecord,
      ∃ outcomeInventory :
          CompleteReconsolidationOutcomeInventory S ctx policies
            claimRef.sourceRecord claimRef.family trigger,
        ∃ rewrite : SilentRewriteEvidence S ctx policies claimRef.sourceRecord
            claimRef.family trigger dispositionInventory outcomeInventory,
          trigger.conflict.transport.transportRecord =
              claimRef.transportRecord ∧
          record.conflictRecord = some trigger.conflict.conflictRecord ∧
          record.provenanceAuditRecord = some rewrite.auditRecord ∧
          record.status = ReconsolidationStatus.silent_rewrite

def OrdinaryReadCase
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
  ¬ ProvenanceDefectEvidenceFor S ctx policies claimRef ∧
  ¬ SilentRewriteEvidenceFor S ctx policies claimRef ∧
  ∃ inventory : CompleteRetrievalTransportInventory S ctx policies
      claimRef.sourceRecord claimRef.family,
    claimRef.transportRecord ∈ inventory.declaredTransports ∧
    Nonempty
      (RetrievalWithoutTransportEvidence S ctx policies claimRef.sourceRecord
        claimRef.family inventory) ∧
    record.status = ReconsolidationStatus.ordinary_read

def OutcomeCollisionCase
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
  ¬ ProvenanceDefectEvidenceFor S ctx policies claimRef ∧
  ¬ SilentRewriteEvidenceFor S ctx policies claimRef ∧
  ¬ OrdinaryReadEvidenceFor S ctx policies claimRef ∧
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    ∃ _collision : ReconsolidationOutcomeCollision S ctx policies
        claimRef.sourceRecord claimRef.family trigger,
      trigger.conflict.transport.transportRecord = claimRef.transportRecord ∧
      record.conflictRecord = some trigger.conflict.conflictRecord ∧
      record.status = ReconsolidationStatus.outcome_collision

def UnrealizedDispositionCase
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
  ¬ ProvenanceDefectEvidenceFor S ctx policies claimRef ∧
  ¬ SilentRewriteEvidenceFor S ctx policies claimRef ∧
  ¬ OrdinaryReadEvidenceFor S ctx policies claimRef ∧
  ¬ OutcomeCollisionEvidenceFor S ctx policies claimRef ∧
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    ∃ dispositionInventory :
        CompleteReconsolidationDispositionInventory S ctx policies
          trigger.conflict.conflictRecord,
      ∃ outcomeInventory :
          CompleteReconsolidationOutcomeInventory S ctx policies
            claimRef.sourceRecord claimRef.family trigger,
        ∃ unsupported : UnrealizedDispositionEvidence S ctx policies
            claimRef.sourceRecord claimRef.family trigger dispositionInventory
            outcomeInventory,
          trigger.conflict.transport.transportRecord =
              claimRef.transportRecord ∧
          record.conflictRecord = some trigger.conflict.conflictRecord ∧
          record.dispositionRecord =
            some unsupported.coverage.dispositionRecord ∧
          record.status = ReconsolidationStatus.unrealized_disposition

def RecordRepairedCase
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
  ¬ ProvenanceDefectEvidenceFor S ctx policies claimRef ∧
  ¬ SilentRewriteEvidenceFor S ctx policies claimRef ∧
  ¬ OrdinaryReadEvidenceFor S ctx policies claimRef ∧
  ¬ OutcomeCollisionEvidenceFor S ctx policies claimRef ∧
  ¬ UnrealizedDispositionEvidenceFor S ctx policies claimRef ∧
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    ∃ dispositionInventory :
        CompleteReconsolidationDispositionInventory S ctx policies
          trigger.conflict.conflictRecord,
      ∃ f9Coverage :
          F9ReconsolidationCoverageCertified S dispositionInventory,
        ∃ repair : RecordRepairEvidence S ctx policies claimRef.sourceRecord
            claimRef.family trigger,
          trigger.conflict.transport.transportRecord =
              claimRef.transportRecord ∧
          record.conflictRecord = some trigger.conflict.conflictRecord ∧
          record.mutationRecord = some repair.mutationRecord ∧
          f9Coverage.dispositionRecord.disposition =
            ReconsolidationDisposition.record_repair ∧
          f9Coverage.dispositionRecord.supportingMutation =
            some repair.mutationRecord ∧
          f9Coverage.dispositionRecord.supportingResidual = none ∧
          record.dispositionRecord = some f9Coverage.dispositionRecord ∧
          record.status = ReconsolidationStatus.record_repaired

def RecordCoarsenedCase
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
  ¬ ProvenanceDefectEvidenceFor S ctx policies claimRef ∧
  ¬ SilentRewriteEvidenceFor S ctx policies claimRef ∧
  ¬ OrdinaryReadEvidenceFor S ctx policies claimRef ∧
  ¬ OutcomeCollisionEvidenceFor S ctx policies claimRef ∧
  ¬ UnrealizedDispositionEvidenceFor S ctx policies claimRef ∧
  ¬ RecordRepairEvidenceFor S ctx policies claimRef ∧
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    ∃ dispositionInventory :
        CompleteReconsolidationDispositionInventory S ctx policies
          trigger.conflict.conflictRecord,
      ∃ f9Coverage :
          F9ReconsolidationCoverageCertified S dispositionInventory,
        ∃ coarsening : RecordCoarseningEvidence S ctx policies
            claimRef.sourceRecord claimRef.family trigger,
          trigger.conflict.transport.transportRecord =
              claimRef.transportRecord ∧
          record.conflictRecord = some trigger.conflict.conflictRecord ∧
          record.mutationRecord = some coarsening.mutationRecord ∧
          f9Coverage.dispositionRecord.disposition =
            ReconsolidationDisposition.record_coarsening ∧
          f9Coverage.dispositionRecord.supportingMutation =
            some coarsening.mutationRecord ∧
          f9Coverage.dispositionRecord.supportingResidual = none ∧
          record.dispositionRecord = some f9Coverage.dispositionRecord ∧
          record.status = ReconsolidationStatus.record_coarsened

def StatusedUnresolvedCase
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
  ¬ ProvenanceDefectEvidenceFor S ctx policies claimRef ∧
  ¬ SilentRewriteEvidenceFor S ctx policies claimRef ∧
  ¬ OrdinaryReadEvidenceFor S ctx policies claimRef ∧
  ¬ OutcomeCollisionEvidenceFor S ctx policies claimRef ∧
  ¬ UnrealizedDispositionEvidenceFor S ctx policies claimRef ∧
  ¬ RecordRepairEvidenceFor S ctx policies claimRef ∧
  ¬ RecordCoarseningEvidenceFor S ctx policies claimRef ∧
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    ∃ dispositionInventory :
        CompleteReconsolidationDispositionInventory S ctx policies
          trigger.conflict.conflictRecord,
      ∃ f9Coverage :
          F9ReconsolidationCoverageCertified S dispositionInventory,
        ∃ unresolved : StatusedUnresolvedEvidence S ctx policies
            claimRef.sourceRecord claimRef.family trigger,
          trigger.conflict.transport.transportRecord =
              claimRef.transportRecord ∧
          record.conflictRecord = some trigger.conflict.conflictRecord ∧
          record.residualRecord = some unresolved.residualRecord ∧
          f9Coverage.dispositionRecord.disposition =
            ReconsolidationDisposition.statused_unresolved ∧
          f9Coverage.dispositionRecord.supportingMutation = none ∧
          f9Coverage.dispositionRecord.supportingResidual =
            some unresolved.residualRecord ∧
          record.dispositionRecord = some f9Coverage.dispositionRecord ∧
          record.status = ReconsolidationStatus.statused_unresolved

def UnstatusedConflictCase
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
  ¬ ProvenanceDefectEvidenceFor S ctx policies claimRef ∧
  ¬ SilentRewriteEvidenceFor S ctx policies claimRef ∧
  ¬ OrdinaryReadEvidenceFor S ctx policies claimRef ∧
  ¬ OutcomeCollisionEvidenceFor S ctx policies claimRef ∧
  ¬ UnrealizedDispositionEvidenceFor S ctx policies claimRef ∧
  ¬ RecordRepairEvidenceFor S ctx policies claimRef ∧
  ¬ RecordCoarseningEvidenceFor S ctx policies claimRef ∧
  ¬ StatusedUnresolvedEvidenceFor S ctx policies claimRef ∧
  ∃ trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family,
    ∃ dispositionInventory :
        CompleteReconsolidationDispositionInventory S ctx policies
          trigger.conflict.conflictRecord,
      ∃ _unstatused : UnstatusedConflictEvidence S ctx policies
          claimRef.sourceRecord claimRef.family trigger dispositionInventory,
        trigger.conflict.transport.transportRecord =
            claimRef.transportRecord ∧
        record.conflictRecord = some trigger.conflict.conflictRecord ∧
        record.status = ReconsolidationStatus.unstatused_conflict

def ProvenanceDefectHolds
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout,
    ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = ReconsolidationStatus.provenance_defect ∧
    ProvenanceDefectCase S ctx policies statusPolicy claimRef record

def SilentRewriteHolds
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout,
    ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = ReconsolidationStatus.silent_rewrite ∧
    SilentRewriteCase S ctx policies statusPolicy claimRef record

def OrdinaryReadHolds
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout,
    ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = ReconsolidationStatus.ordinary_read ∧
    OrdinaryReadCase S ctx policies statusPolicy claimRef record

def OutcomeCollisionHolds
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout,
    ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = ReconsolidationStatus.outcome_collision ∧
    OutcomeCollisionCase S ctx policies statusPolicy claimRef record

def UnrealizedDispositionHolds
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout,
    ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = ReconsolidationStatus.unrealized_disposition ∧
    UnrealizedDispositionCase S ctx policies statusPolicy claimRef record

def RecordRepairedHolds
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout,
    ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = ReconsolidationStatus.record_repaired ∧
    RecordRepairedCase S ctx policies statusPolicy claimRef record

def RecordCoarsenedHolds
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout,
    ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = ReconsolidationStatus.record_coarsened ∧
    RecordCoarsenedCase S ctx policies statusPolicy claimRef record

def StatusedUnresolvedHolds
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout,
    ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = ReconsolidationStatus.statused_unresolved ∧
    StatusedUnresolvedCase S ctx policies statusPolicy claimRef record

def UnstatusedConflictHolds
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) : Prop :=
  ∃ record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout,
    ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = ReconsolidationStatus.unstatused_conflict ∧
    UnstatusedConflictCase S ctx policies statusPolicy claimRef record

structure CompleteReconsolidationStatus
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) where
  branchValid :
    ∃ record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
        FOut Readout,
      ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ∧
      (ProvenanceDefectCase S ctx policies statusPolicy claimRef record ∨
       SilentRewriteCase S ctx policies statusPolicy claimRef record ∨
       OrdinaryReadCase S ctx policies statusPolicy claimRef record ∨
       OutcomeCollisionCase S ctx policies statusPolicy claimRef record ∨
       UnrealizedDispositionCase S ctx policies statusPolicy claimRef record ∨
       RecordRepairedCase S ctx policies statusPolicy claimRef record ∨
       RecordCoarsenedCase S ctx policies statusPolicy claimRef record ∨
       StatusedUnresolvedCase S ctx policies statusPolicy claimRef record ∨
       UnstatusedConflictCase S ctx policies statusPolicy claimRef record)
  statusUnique :
    ∀ record1 record2 :
        ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout,
      ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record1 ->
      ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record2 ->
      record1.status = record2.status

structure SilentRewriteFalsifier
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family)
    (dispositionInventory :
      CompleteReconsolidationDispositionInventory S ctx policies
        trigger.conflict.conflictRecord)
    (outcomeInventory :
      CompleteReconsolidationOutcomeInventory S ctx policies
        claimRef.sourceRecord claimRef.family trigger) where
  rewrite : SilentRewriteEvidence S ctx policies claimRef.sourceRecord
    claimRef.family trigger dispositionInventory outcomeInventory
  claimLinked :
    trigger.conflict.transport.transportRecord = claimRef.transportRecord ∧
    trigger.conflict.transport.transportRecord.contextRecord =
      claimRef.contextRecord

structure RetrievalWithoutTransportFalsifier
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout) where
  inventory : CompleteRetrievalTransportInventory S ctx policies
    claimRef.sourceRecord claimRef.family
  ordinaryRead : RetrievalWithoutTransportEvidence S ctx policies
    claimRef.sourceRecord claimRef.family inventory
  transportDeclared : claimRef.transportRecord ∈ inventory.declaredTransports

structure LaunderedProvenanceFalsifier
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (trigger : ReconsolidationTrigger S ctx policies claimRef.sourceRecord
      claimRef.family) where
  defect : LaunderedProvenanceDefect S ctx policies claimRef.sourceRecord
    claimRef.family trigger
  claimLinked :
    trigger.conflict.transport.transportRecord = claimRef.transportRecord ∧
    trigger.conflict.transport.transportRecord.contextRecord =
      claimRef.contextRecord

end StatusApparatus

namespace E14

def ExactlyOne : List Prop -> Prop
  | p1 :: p2 :: p3 :: p4 :: p5 :: p6 :: p7 :: p8 :: p9 :: [] =>
      (p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p7 ∧ ¬ p8 ∧ ¬ p9) ∨
      (p2 ∧ ¬ p1 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p7 ∧ ¬ p8 ∧ ¬ p9) ∨
      (p3 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p7 ∧ ¬ p8 ∧ ¬ p9) ∨
      (p4 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p7 ∧ ¬ p8 ∧ ¬ p9) ∨
      (p5 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p6 ∧ ¬ p7 ∧ ¬ p8 ∧ ¬ p9) ∨
      (p6 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p7 ∧ ¬ p8 ∧ ¬ p9) ∨
      (p7 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p8 ∧ ¬ p9) ∨
      (p8 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p7 ∧ ¬ p9) ∨
      (p9 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p7 ∧ ¬ p8)
  | p1 :: p2 :: p3 :: [] =>
      (p1 ∧ ¬ p2 ∧ ¬ p3) ∨
      (p2 ∧ ¬ p1 ∧ ¬ p3) ∨
      (p3 ∧ ¬ p1 ∧ ¬ p2)
  | _ => False

end E14

section Theorems

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)

variable {X : Type z} {RecordValue : Type z'}
variable {Q : Type z''} {TransportedValue : Type z'''}
variable {FOut : Type z''''} {Readout : Type z'''''}

theorem E14_ReconsolidationStatus
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (complete : CompleteReconsolidationStatus S ctx policies statusPolicy
      claimRef) :
    E14.ExactlyOne
      [ProvenanceDefectHolds S ctx policies statusPolicy claimRef,
       SilentRewriteHolds S ctx policies statusPolicy claimRef,
       OrdinaryReadHolds S ctx policies statusPolicy claimRef,
       OutcomeCollisionHolds S ctx policies statusPolicy claimRef,
       UnrealizedDispositionHolds S ctx policies statusPolicy claimRef,
       RecordRepairedHolds S ctx policies statusPolicy claimRef,
       RecordCoarsenedHolds S ctx policies statusPolicy claimRef,
       StatusedUnresolvedHolds S ctx policies statusPolicy claimRef,
       UnstatusedConflictHolds S ctx policies statusPolicy claimRef] := by
  rcases complete.branchValid with ⟨record, hOccurrence, hBranch⟩
  have hConflict :
      ∀ {record1 record2 :
          ReconsolidationStatusRecord X RecordValue Q TransportedValue
            FOut Readout}
        {status1 status2 : ReconsolidationStatus},
        ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record1 ->
        ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record2 ->
        record1.status = status1 ->
        record2.status = status2 ->
        status1 ≠ status2 ->
        False := by
    intro record1 record2 status1 status2 hOcc1 hOcc2 hStatus1 hStatus2 hNe
    have hEq := complete.statusUnique record1 record2 hOcc1 hOcc2
    rw [hStatus1, hStatus2] at hEq
    exact hNe hEq
  have hNotProvenance :
      ∀ {record : ReconsolidationStatusRecord X RecordValue Q
          TransportedValue FOut Readout}
        {status : ReconsolidationStatus},
        ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ->
        record.status = status ->
        status ≠ ReconsolidationStatus.provenance_defect ->
        ¬ ProvenanceDefectHolds S ctx policies statusPolicy claimRef := by
    intro current status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotSilent :
      ∀ {record : ReconsolidationStatusRecord X RecordValue Q
          TransportedValue FOut Readout}
        {status : ReconsolidationStatus},
        ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ->
        record.status = status ->
        status ≠ ReconsolidationStatus.silent_rewrite ->
        ¬ SilentRewriteHolds S ctx policies statusPolicy claimRef := by
    intro current status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotOrdinary :
      ∀ {record : ReconsolidationStatusRecord X RecordValue Q
          TransportedValue FOut Readout}
        {status : ReconsolidationStatus},
        ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ->
        record.status = status ->
        status ≠ ReconsolidationStatus.ordinary_read ->
        ¬ OrdinaryReadHolds S ctx policies statusPolicy claimRef := by
    intro current status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotCollision :
      ∀ {record : ReconsolidationStatusRecord X RecordValue Q
          TransportedValue FOut Readout}
        {status : ReconsolidationStatus},
        ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ->
        record.status = status ->
        status ≠ ReconsolidationStatus.outcome_collision ->
        ¬ OutcomeCollisionHolds S ctx policies statusPolicy claimRef := by
    intro current status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotUnrealized :
      ∀ {record : ReconsolidationStatusRecord X RecordValue Q
          TransportedValue FOut Readout}
        {status : ReconsolidationStatus},
        ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ->
        record.status = status ->
        status ≠ ReconsolidationStatus.unrealized_disposition ->
        ¬ UnrealizedDispositionHolds S ctx policies statusPolicy claimRef := by
    intro current status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotRepaired :
      ∀ {record : ReconsolidationStatusRecord X RecordValue Q
          TransportedValue FOut Readout}
        {status : ReconsolidationStatus},
        ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ->
        record.status = status ->
        status ≠ ReconsolidationStatus.record_repaired ->
        ¬ RecordRepairedHolds S ctx policies statusPolicy claimRef := by
    intro current status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotCoarsened :
      ∀ {record : ReconsolidationStatusRecord X RecordValue Q
          TransportedValue FOut Readout}
        {status : ReconsolidationStatus},
        ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ->
        record.status = status ->
        status ≠ ReconsolidationStatus.record_coarsened ->
        ¬ RecordCoarsenedHolds S ctx policies statusPolicy claimRef := by
    intro current status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotUnresolved :
      ∀ {record : ReconsolidationStatusRecord X RecordValue Q
          TransportedValue FOut Readout}
        {status : ReconsolidationStatus},
        ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ->
        record.status = status ->
        status ≠ ReconsolidationStatus.statused_unresolved ->
        ¬ StatusedUnresolvedHolds S ctx policies statusPolicy claimRef := by
    intro current status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotUnstatused :
      ∀ {record : ReconsolidationStatusRecord X RecordValue Q
          TransportedValue FOut Readout}
        {status : ReconsolidationStatus},
        ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record ->
        record.status = status ->
        status ≠ ReconsolidationStatus.unstatused_conflict ->
        ¬ UnstatusedConflictHolds S ctx policies statusPolicy claimRef := by
    intro current status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  rcases hBranch with
    hProvenance | hSilent | hOrdinary | hCollision | hUnrealized |
      hRepaired | hCoarsened | hUnresolved | hUnstatused
  · have hCase := hProvenance
    rcases hProvenance with
      ⟨_hOcc, _trigger, _defect, _hTransport, _hConflictRecord,
        _hAuditRecord, hStatus⟩
    exact Or.inl
      ⟨⟨record, hOccurrence, hStatus, hCase⟩,
        hNotSilent hOccurrence hStatus (by decide),
        hNotOrdinary hOccurrence hStatus (by decide),
        hNotCollision hOccurrence hStatus (by decide),
        hNotUnrealized hOccurrence hStatus (by decide),
        hNotRepaired hOccurrence hStatus (by decide),
        hNotCoarsened hOccurrence hStatus (by decide),
        hNotUnresolved hOccurrence hStatus (by decide),
        hNotUnstatused hOccurrence hStatus (by decide)⟩
  · have hCase := hSilent
    rcases hSilent with
      ⟨_hOcc, _hNoProvenance, _trigger, _dispositionInventory,
        _outcomeInventory, _rewrite, _hTransport, _hConflictRecord,
        _hAuditRecord, hStatus⟩
    exact Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hStatus, hCase⟩,
        hNotProvenance hOccurrence hStatus (by decide),
        hNotOrdinary hOccurrence hStatus (by decide),
        hNotCollision hOccurrence hStatus (by decide),
        hNotUnrealized hOccurrence hStatus (by decide),
        hNotRepaired hOccurrence hStatus (by decide),
        hNotCoarsened hOccurrence hStatus (by decide),
        hNotUnresolved hOccurrence hStatus (by decide),
        hNotUnstatused hOccurrence hStatus (by decide)⟩
  · have hCase := hOrdinary
    rcases hOrdinary with
      ⟨_hOcc, _hNoProvenance, _hNoSilent, _inventory, _hTransport,
        _ordinaryRead, hStatus⟩
    exact Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hStatus, hCase⟩,
        hNotProvenance hOccurrence hStatus (by decide),
        hNotSilent hOccurrence hStatus (by decide),
        hNotCollision hOccurrence hStatus (by decide),
        hNotUnrealized hOccurrence hStatus (by decide),
        hNotRepaired hOccurrence hStatus (by decide),
        hNotCoarsened hOccurrence hStatus (by decide),
        hNotUnresolved hOccurrence hStatus (by decide),
        hNotUnstatused hOccurrence hStatus (by decide)⟩
  · have hCase := hCollision
    rcases hCollision with
      ⟨_hOcc, _hNoProvenance, _hNoSilent, _hNoOrdinary, _trigger,
        _collision, _hTransport, _hConflictRecord, hStatus⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hStatus, hCase⟩,
        hNotProvenance hOccurrence hStatus (by decide),
        hNotSilent hOccurrence hStatus (by decide),
        hNotOrdinary hOccurrence hStatus (by decide),
        hNotUnrealized hOccurrence hStatus (by decide),
        hNotRepaired hOccurrence hStatus (by decide),
        hNotCoarsened hOccurrence hStatus (by decide),
        hNotUnresolved hOccurrence hStatus (by decide),
        hNotUnstatused hOccurrence hStatus (by decide)⟩
  · have hCase := hUnrealized
    rcases hUnrealized with
      ⟨_hOcc, _hNoProvenance, _hNoSilent, _hNoOrdinary, _hNoCollision,
        _trigger, _dispositionInventory, _outcomeInventory, _unsupported,
        _hTransport, _hConflictRecord, _hDispositionRecord, hStatus⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hStatus, hCase⟩,
        hNotProvenance hOccurrence hStatus (by decide),
        hNotSilent hOccurrence hStatus (by decide),
        hNotOrdinary hOccurrence hStatus (by decide),
        hNotCollision hOccurrence hStatus (by decide),
        hNotRepaired hOccurrence hStatus (by decide),
        hNotCoarsened hOccurrence hStatus (by decide),
        hNotUnresolved hOccurrence hStatus (by decide),
        hNotUnstatused hOccurrence hStatus (by decide)⟩
  · have hCase := hRepaired
    rcases hRepaired with
      ⟨_hOcc, _hNoProvenance, _hNoSilent, _hNoOrdinary, _hNoCollision,
        _hNoUnrealized, _trigger, _dispositionInventory, _f9Coverage,
        _repair, _hTransport, _hConflictRecord, _hMutationRecord,
        _hDisposition, _hSupportingMutation, _hSupportingResidual,
        _hStatusDisposition, hStatus⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hStatus, hCase⟩,
        hNotProvenance hOccurrence hStatus (by decide),
        hNotSilent hOccurrence hStatus (by decide),
        hNotOrdinary hOccurrence hStatus (by decide),
        hNotCollision hOccurrence hStatus (by decide),
        hNotUnrealized hOccurrence hStatus (by decide),
        hNotCoarsened hOccurrence hStatus (by decide),
        hNotUnresolved hOccurrence hStatus (by decide),
        hNotUnstatused hOccurrence hStatus (by decide)⟩
  · have hCase := hCoarsened
    rcases hCoarsened with
      ⟨_hOcc, _hNoProvenance, _hNoSilent, _hNoOrdinary, _hNoCollision,
        _hNoUnrealized, _hNoRepaired, _trigger, _dispositionInventory,
        _f9Coverage, _coarsening, _hTransport, _hConflictRecord,
        _hMutationRecord, _hDisposition, _hSupportingMutation,
        _hSupportingResidual, _hStatusDisposition, hStatus⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hStatus, hCase⟩,
        hNotProvenance hOccurrence hStatus (by decide),
        hNotSilent hOccurrence hStatus (by decide),
        hNotOrdinary hOccurrence hStatus (by decide),
        hNotCollision hOccurrence hStatus (by decide),
        hNotUnrealized hOccurrence hStatus (by decide),
        hNotRepaired hOccurrence hStatus (by decide),
        hNotUnresolved hOccurrence hStatus (by decide),
        hNotUnstatused hOccurrence hStatus (by decide)⟩
  · have hCase := hUnresolved
    rcases hUnresolved with
      ⟨_hOcc, _hNoProvenance, _hNoSilent, _hNoOrdinary, _hNoCollision,
        _hNoUnrealized, _hNoRepaired, _hNoCoarsened, _trigger,
        _dispositionInventory, _f9Coverage, _unresolved, _hTransport,
        _hConflictRecord, _hResidualRecord, _hDisposition,
        _hSupportingMutation, _hSupportingResidual, _hStatusDisposition,
        hStatus⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <|
      Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hStatus, hCase⟩,
        hNotProvenance hOccurrence hStatus (by decide),
        hNotSilent hOccurrence hStatus (by decide),
        hNotOrdinary hOccurrence hStatus (by decide),
        hNotCollision hOccurrence hStatus (by decide),
        hNotUnrealized hOccurrence hStatus (by decide),
        hNotRepaired hOccurrence hStatus (by decide),
        hNotCoarsened hOccurrence hStatus (by decide),
        hNotUnstatused hOccurrence hStatus (by decide)⟩
  · have hCase := hUnstatused
    rcases hUnstatused with
      ⟨_hOcc, _hNoProvenance, _hNoSilent, _hNoOrdinary, _hNoCollision,
        _hNoUnrealized, _hNoRepaired, _hNoCoarsened, _hNoUnresolved,
        _trigger, _dispositionInventory, _unstatused, _hTransport,
        _hConflictRecord, hStatus⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <|
      Or.inr <| Or.inr
      ⟨⟨record, hOccurrence, hStatus, hCase⟩,
        hNotProvenance hOccurrence hStatus (by decide),
        hNotSilent hOccurrence hStatus (by decide),
        hNotOrdinary hOccurrence hStatus (by decide),
        hNotCollision hOccurrence hStatus (by decide),
        hNotUnrealized hOccurrence hStatus (by decide),
        hNotRepaired hOccurrence hStatus (by decide),
        hNotCoarsened hOccurrence hStatus (by decide),
        hNotUnresolved hOccurrence hStatus (by decide)⟩

theorem E14_LawfulConflictTrichotomy
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (complete : CompleteReconsolidationStatus S ctx policies statusPolicy
      claimRef)
    (hNoProvenanceDefect :
      ¬ ProvenanceDefectHolds S ctx policies statusPolicy claimRef)
    (hNoSilentRewrite :
      ¬ SilentRewriteHolds S ctx policies statusPolicy claimRef)
    (hGenuineTransport :
      ¬ OrdinaryReadHolds S ctx policies statusPolicy claimRef)
    (hNoCollision :
      ¬ OutcomeCollisionHolds S ctx policies statusPolicy claimRef)
    (hDispositionRealized :
      ¬ UnrealizedDispositionHolds S ctx policies statusPolicy claimRef)
    (hF9Statused :
      ¬ UnstatusedConflictHolds S ctx policies statusPolicy claimRef) :
    E14.ExactlyOne
      [RecordRepairedHolds S ctx policies statusPolicy claimRef,
       RecordCoarsenedHolds S ctx policies statusPolicy claimRef,
       StatusedUnresolvedHolds S ctx policies statusPolicy claimRef] := by
  have hPartition :=
    E14_ReconsolidationStatus S ctx policies statusPolicy claimRef complete
  simp only [E14.ExactlyOne] at hPartition ⊢
  rcases hPartition with
    hProvenance | hSilent | hOrdinary | hCollision | hUnrealized |
      hRepaired | hCoarsened | hUnresolved | hUnstatused
  · exact (hNoProvenanceDefect hProvenance.1).elim
  · exact (hNoSilentRewrite hSilent.1).elim
  · exact (hGenuineTransport hOrdinary.1).elim
  · exact (hNoCollision hCollision.1).elim
  · exact (hDispositionRealized hUnrealized.1).elim
  · rcases hRepaired with
      ⟨hRepaired, _hNoProvenance, _hNoSilent, _hNoOrdinary, _hNoCollision,
        _hNoUnrealized, hNoCoarsened, hNoUnresolved, _hNoUnstatused⟩
    exact Or.inl ⟨hRepaired, hNoCoarsened, hNoUnresolved⟩
  · rcases hCoarsened with
      ⟨hCoarsened, _hNoProvenance, _hNoSilent, _hNoOrdinary, _hNoCollision,
        _hNoUnrealized, hNoRepaired, hNoUnresolved, _hNoUnstatused⟩
    exact Or.inr <| Or.inl ⟨hCoarsened, hNoRepaired, hNoUnresolved⟩
  · rcases hUnresolved with
      ⟨hUnresolved, _hNoProvenance, _hNoSilent, _hNoOrdinary, _hNoCollision,
        _hNoUnrealized, hNoRepaired, hNoCoarsened, _hNoUnstatused⟩
    exact Or.inr <| Or.inr ⟨hUnresolved, hNoRepaired, hNoCoarsened⟩
  · exact (hF9Statused hUnstatused.1).elim

theorem E14_OutcomeCollisionExcludesLawful
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (collision : OutcomeCollisionEvidenceFor S ctx policies claimRef)
    (complete : CompleteReconsolidationStatus S ctx policies statusPolicy
      claimRef) :
    ¬ RecordRepairedHolds S ctx policies statusPolicy claimRef ∧
      ¬ RecordCoarsenedHolds S ctx policies statusPolicy claimRef ∧
      ¬ StatusedUnresolvedHolds S ctx policies statusPolicy claimRef := by
  rcases complete.branchValid with ⟨record, hOccurrence, hBranch⟩
  have hNotRepairedFromStatus
      (hDifferent : record.status ≠ ReconsolidationStatus.record_repaired) :
      ¬ RecordRepairedHolds S ctx policies statusPolicy claimRef := by
    rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩
    have hSameStatus :=
      complete.statusUnique record other hOccurrence hOtherOccurrence
    rw [hOtherStatus] at hSameStatus
    exact hDifferent hSameStatus
  have hNotCoarsenedFromStatus
      (hDifferent : record.status ≠ ReconsolidationStatus.record_coarsened) :
      ¬ RecordCoarsenedHolds S ctx policies statusPolicy claimRef := by
    rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩
    have hSameStatus :=
      complete.statusUnique record other hOccurrence hOtherOccurrence
    rw [hOtherStatus] at hSameStatus
    exact hDifferent hSameStatus
  have hNotUnresolvedFromStatus
      (hDifferent :
        record.status ≠ ReconsolidationStatus.statused_unresolved) :
      ¬ StatusedUnresolvedHolds S ctx policies statusPolicy claimRef := by
    rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩
    have hSameStatus :=
      complete.statusUnique record other hOccurrence hOtherOccurrence
    rw [hOtherStatus] at hSameStatus
    exact hDifferent hSameStatus
  rcases hBranch with
    hProvenance | hSilent | hOrdinary | hCollision | hUnrealized |
      hRepaired | hCoarsened | hUnresolved | hUnstatused
  · rcases hProvenance with
      ⟨_hOcc, _trigger, _defect, _hTransport, _hConflictRecord,
        _hAuditRecord, hStatus⟩
    exact
      ⟨hNotRepairedFromStatus (by rw [hStatus]; decide),
        hNotCoarsenedFromStatus (by rw [hStatus]; decide),
        hNotUnresolvedFromStatus (by rw [hStatus]; decide)⟩
  · rcases hSilent with
      ⟨_hOcc, _hNoProvenance, _trigger, _dispositionInventory,
        _outcomeInventory, _rewrite, _hTransport, _hConflictRecord,
        _hAuditRecord, hStatus⟩
    exact
      ⟨hNotRepairedFromStatus (by rw [hStatus]; decide),
        hNotCoarsenedFromStatus (by rw [hStatus]; decide),
        hNotUnresolvedFromStatus (by rw [hStatus]; decide)⟩
  · rcases hOrdinary with
      ⟨_hOcc, _hNoProvenance, _hNoSilent, _inventory, _hTransport,
        _ordinaryRead, hStatus⟩
    exact
      ⟨hNotRepairedFromStatus (by rw [hStatus]; decide),
        hNotCoarsenedFromStatus (by rw [hStatus]; decide),
        hNotUnresolvedFromStatus (by rw [hStatus]; decide)⟩
  · rcases hCollision with
      ⟨_hOcc, _hNoProvenance, _hNoSilent, _hNoOrdinary, _trigger,
        _collision, _hTransport, _hConflictRecord, hStatus⟩
    exact
      ⟨hNotRepairedFromStatus (by rw [hStatus]; decide),
        hNotCoarsenedFromStatus (by rw [hStatus]; decide),
        hNotUnresolvedFromStatus (by rw [hStatus]; decide)⟩
  · rcases hUnrealized with
      ⟨_hOcc, _hNoProvenance, _hNoSilent, _hNoOrdinary, _hNoCollision,
        _trigger, _dispositionInventory, _outcomeInventory, _unsupported,
        _hTransport, _hConflictRecord, _hDispositionRecord, hStatus⟩
    exact
      ⟨hNotRepairedFromStatus (by rw [hStatus]; decide),
        hNotCoarsenedFromStatus (by rw [hStatus]; decide),
        hNotUnresolvedFromStatus (by rw [hStatus]; decide)⟩
  · rcases hRepaired with
      ⟨_hOcc, _hNoProvenance, _hNoSilent, _hNoOrdinary, hNoCollision,
        _hNoUnrealized, _trigger, _dispositionInventory, _f9Coverage,
        _repair, _hTransport, _hConflictRecord, _hMutationRecord,
        _hDisposition, _hSupportingMutation, _hSupportingResidual,
        _hStatusDisposition, _hStatus⟩
    exact (hNoCollision collision).elim
  · rcases hCoarsened with
      ⟨_hOcc, _hNoProvenance, _hNoSilent, _hNoOrdinary, hNoCollision,
        _hNoUnrealized, _hNoRepaired, _trigger, _dispositionInventory,
        _f9Coverage, _coarsening, _hTransport, _hConflictRecord,
        _hMutationRecord, _hDisposition, _hSupportingMutation,
        _hSupportingResidual, _hStatusDisposition, _hStatus⟩
    exact (hNoCollision collision).elim
  · rcases hUnresolved with
      ⟨_hOcc, _hNoProvenance, _hNoSilent, _hNoOrdinary, hNoCollision,
        _hNoUnrealized, _hNoRepaired, _hNoCoarsened, _trigger,
        _dispositionInventory, _f9Coverage, _unresolved, _hTransport,
        _hConflictRecord, _hResidualRecord, _hDisposition,
        _hSupportingMutation, _hSupportingResidual, _hStatusDisposition,
        _hStatus⟩
    exact (hNoCollision collision).elim
  · rcases hUnstatused with
      ⟨_hOcc, _hNoProvenance, _hNoSilent, _hNoOrdinary, hNoCollision,
        _hNoUnrealized, _hNoRepaired, _hNoCoarsened, _hNoUnresolved,
        _trigger, _dispositionInventory, _unstatused, _hTransport,
        _hConflictRecord, _hStatus⟩
    exact (hNoCollision collision).elim

theorem E14_RecordRepair
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout)
    (hOccurrence :
      ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record)
    (hStatus : record.status = ReconsolidationStatus.record_repaired)
    (hCase :
      RecordRepairedCase S ctx policies statusPolicy claimRef record) :
    RecordRepairedHolds S ctx policies statusPolicy claimRef := by
  exact ⟨record, hOccurrence, hStatus, hCase⟩

theorem E14_RecordCoarsening
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout)
    (hOccurrence :
      ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record)
    (hStatus : record.status = ReconsolidationStatus.record_coarsened)
    (hCase :
      RecordCoarsenedCase S ctx policies statusPolicy claimRef record) :
    RecordCoarsenedHolds S ctx policies statusPolicy claimRef := by
  exact ⟨record, hOccurrence, hStatus, hCase⟩

theorem E14_StatusedUnresolvedChargedToLambda
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout)
    (hOccurrence :
      ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record)
    (hStatus : record.status = ReconsolidationStatus.statused_unresolved)
    (hCase :
      StatusedUnresolvedCase S ctx policies statusPolicy claimRef record) :
    StatusedUnresolvedHolds S ctx policies statusPolicy claimRef := by
  exact ⟨record, hOccurrence, hStatus, hCase⟩

theorem E14_SilentRewriteFalsifier
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (complete : CompleteReconsolidationStatus S ctx policies statusPolicy
      claimRef)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout)
    (hOccurrence :
      ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record)
    (hStatus : record.status = ReconsolidationStatus.silent_rewrite)
    (_hCase : SilentRewriteCase S ctx policies statusPolicy claimRef record) :
    ¬ RecordRepairedHolds S ctx policies statusPolicy claimRef ∧
    ¬ RecordCoarsenedHolds S ctx policies statusPolicy claimRef ∧
    ¬ StatusedUnresolvedHolds S ctx policies statusPolicy claimRef := by
  refine ⟨?_, ?_, ?_⟩
  · intro hRepaired
    rcases hRepaired with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    have hEq := complete.statusUnique record other hOccurrence hOtherOcc
    rw [hStatus, hOtherStatus] at hEq
    exact (by decide : ReconsolidationStatus.silent_rewrite ≠
      ReconsolidationStatus.record_repaired) hEq
  · intro hCoarsened
    rcases hCoarsened with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    have hEq := complete.statusUnique record other hOccurrence hOtherOcc
    rw [hStatus, hOtherStatus] at hEq
    exact (by decide : ReconsolidationStatus.silent_rewrite ≠
      ReconsolidationStatus.record_coarsened) hEq
  · intro hUnresolved
    rcases hUnresolved with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    have hEq := complete.statusUnique record other hOccurrence hOtherOcc
    rw [hStatus, hOtherStatus] at hEq
    exact (by decide : ReconsolidationStatus.silent_rewrite ≠
      ReconsolidationStatus.statused_unresolved) hEq

theorem E14_RetrievalWithoutTransportControl
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (complete : CompleteReconsolidationStatus S ctx policies statusPolicy
      claimRef)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout)
    (hOccurrence :
      ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record)
    (hStatus : record.status = ReconsolidationStatus.ordinary_read)
    (hCase : OrdinaryReadCase S ctx policies statusPolicy claimRef record) :
    OrdinaryReadHolds S ctx policies statusPolicy claimRef ∧
    ¬ RecordRepairedHolds S ctx policies statusPolicy claimRef ∧
    ¬ RecordCoarsenedHolds S ctx policies statusPolicy claimRef ∧
    ¬ StatusedUnresolvedHolds S ctx policies statusPolicy claimRef := by
  refine ⟨⟨record, hOccurrence, hStatus, hCase⟩, ?_, ?_, ?_⟩
  · intro hRepaired
    rcases hRepaired with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    have hEq := complete.statusUnique record other hOccurrence hOtherOcc
    rw [hStatus, hOtherStatus] at hEq
    exact (by decide : ReconsolidationStatus.ordinary_read ≠
      ReconsolidationStatus.record_repaired) hEq
  · intro hCoarsened
    rcases hCoarsened with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    have hEq := complete.statusUnique record other hOccurrence hOtherOcc
    rw [hStatus, hOtherStatus] at hEq
    exact (by decide : ReconsolidationStatus.ordinary_read ≠
      ReconsolidationStatus.record_coarsened) hEq
  · intro hUnresolved
    rcases hUnresolved with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    have hEq := complete.statusUnique record other hOccurrence hOtherOcc
    rw [hStatus, hOtherStatus] at hEq
    exact (by decide : ReconsolidationStatus.ordinary_read ≠
      ReconsolidationStatus.statused_unresolved) hEq

theorem E14_LaunderedProvenanceDefect
    (ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ReconsolidationStatusRecord X RecordValue Q TransportedValue
          FOut Readout))
    (claimRef : ReconsolidationClaimRef X RecordValue Q TransportedValue
      FOut Readout)
    (record : ReconsolidationStatusRecord X RecordValue Q TransportedValue
      FOut Readout)
    (hOccurrence :
      ReconsolidationStatusOccurrenceFor S statusPolicy claimRef record)
    (hStatus : record.status = ReconsolidationStatus.provenance_defect)
    (hCase :
      ProvenanceDefectCase S ctx policies statusPolicy claimRef record) :
    ProvenanceDefectHolds S ctx policies statusPolicy claimRef := by
  exact ⟨record, hOccurrence, hStatus, hCase⟩

end Theorems

end SixBirdsFoundationsV
