import SixBirdsFoundationsV.Laws.E14Reconsolidation
import SixBirdsFoundationsV.Laws.E7Alarm
import SixBirdsFoundationsV.Laws.E5ReclosureCollapse
import SixBirdsFoundationsV.Laws.E6E9PricedAccess
import SixBirdsIII.Basic
import Xi.AdequacyResidual

namespace SixBirdsFoundationsV

open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Xi.AdequacyResidual

/-!
E15 offline reclosure setup.

This setup layer mechanizes the carried closure-debt sources, exact debt-flow
inventories, derived online/offline budget geometry, lawful P2 exchange gate,
finite alternation schedule, and obstruction evidence from the accepted E15
six-field normal form (`formalization/notes/examples/E15.md`).  The status
apparatus and theorem statements are intentionally left to later subsections.
-/

section Setup

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)

variable {X : Type z} {RecordValue : Type z'} {Q : Type z''}
variable {TransportedValue : Type z'''} {FOut : Type z''''}
variable {Readout : Type z'''''}
variable {RouteResiduePayload : Type z''''''}
variable {Probe : Type z'''''''} {XiFamily : Type z''''''''}
variable {ChallengeClass : Type z'''''''''} {Horizon : Type z''''''''''}
variable {e yDim xiDim : Nat}

structure ClosureDebtHorizonRecord where
  horizonId : Nat
  startTime : Rat
  endTime : Rat
  positiveDuration : startTime < endTime
  deriving Repr

structure ClosureDebtScopeRecord (ChallengeClass : Type u) where
  debtClaimId : Nat
  challengeClass : ChallengeClass
  horizon : ClosureDebtHorizonRecord

inductive ClosureDebtComponentKind where
  | e14_reconsolidation
  | f3_route_residue
  | xi_adequacy_residual
  deriving DecidableEq, Repr

structure RouteResidueDebtRecord (RouteResiduePayload : Type u) where
  residueId : Nat
  routeResidue : RouteResiduePayload
  reconciliationClaimId : Nat
  recordedAt : Rat
  residualAmount : Rat

structure XiResidualValuationPolicyRecord where
  valuationPolicyId : Nat
  declaredAt : Rat
  deriving DecidableEq, Repr

structure XiAdequacyResidualDebtRecord (e yDim xiDim : Nat) where
  residualId : Nat
  C : Mat e e
  L : Mat yDim e
  D : Mat xiDim e
  KLLdagger : Mat yDim yDim
  residualMatrix : Mat xiDim xiDim
  residualComputed : residualMatrix = adequacyResidual C L D KLLdagger
  valuationPolicy : XiResidualValuationPolicyRecord
  reconciliationClaimId : Nat
  recordedAt : Rat
  residualAmount : Rat

structure E14ResidualRegistrationRecord
    (X : Type u) (RecordValue : Type v) (Q : Type w)
    (TransportedValue : Type x) (FOut : Type y) (Readout : Type z) where
  registrationId : Nat
  residualRecord :
    ReconsolidationResidualRecord X RecordValue Q TransportedValue FOut Readout
  registeredAt : Rat

structure SharedBudgetAllocationRecord (ChallengeClass : Type u) where
  allocationId : Nat
  scope : ClosureDebtScopeRecord ChallengeClass
  declaredAt : Rat
  onlineExternalAllocation : Rat
  onlineInternalDischargeAllocation : Rat
  offlineExternalAllocation : Rat
  offlineInternalDischargeAllocation : Rat

inductive OperatingMode where
  | online
  | offline
  deriving DecidableEq, Repr

structure OperatingPhaseRecord (ChallengeClass : Type u) where
  phaseId : Nat
  scope : ClosureDebtScopeRecord ChallengeClass
  allocationRecord : SharedBudgetAllocationRecord ChallengeClass
  mode : OperatingMode
  startTime : Rat
  endTime : Rat
  positiveDuration : startTime < endTime

structure ExchangeGateRecord
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    (ChallengeClass : Type z) where
  gateRecordId : Nat
  phaseRecord : OperatingPhaseRecord ChallengeClass
  z : S.T.Z
  z' : S.T.Z
  defect : DefectRecord
  move : RepairMove S.T MovePayload LedgerEntry MoveRecord S.moveRecordPolicy
  auditRecord : AuditRecord

structure ExternalExchangeRecord (ChallengeClass : Type u) where
  exchangeRecordId : Nat
  phaseRecord : OperatingPhaseRecord ChallengeClass
  exchangedAmount : Rat
  recordedAt : Rat

structure DutyCycleToleranceRecord (ChallengeClass : Type u) where
  toleranceId : Nat
  scope : ClosureDebtScopeRecord ChallengeClass
  declaredAt : Rat
  tolerance : Rat
  nonnegative : 0 <= tolerance

structure OfflineRecurrenceBoundRecord (ChallengeClass : Type u) where
  recurrenceBoundId : Nat
  scope : ClosureDebtScopeRecord ChallengeClass
  declaredAt : Rat
  maximumOnlineRun : Rat
  positiveBound : 0 < maximumOnlineRun

structure DebtBoundRecord (ChallengeClass : Type u) where
  boundId : Nat
  scope : ClosureDebtScopeRecord ChallengeClass
  declaredAt : Rat
  upperBound : Rat

structure E7AlarmCascadeObservation (ChallengeClass : Type u) where
  observationId : Nat
  scope : ClosureDebtScopeRecord ChallengeClass
  phaseRecord : OperatingPhaseRecord ChallengeClass
  observedAt : Rat
  dispositionKind : AlarmDispositionKind
  discountReason : Option AlarmDiscountReason

structure E5StressCascadeObservation (ChallengeClass : Type u) where
  observationId : Nat
  scope : ClosureDebtScopeRecord ChallengeClass
  phaseRecord : OperatingPhaseRecord ChallengeClass
  observedAt : Rat
  status : ReclosureCollapseStatus

def ConsecutiveIn {ChallengeClass : Type u}
    (phases : List (OperatingPhaseRecord ChallengeClass))
    (phase1 phase2 : OperatingPhaseRecord ChallengeClass) : Prop :=
  ∃ pre post, phases = pre ++ phase1 :: phase2 :: post

structure DeclaredOperatingSchedule (ChallengeClass : Type u) where
  scheduleId : Nat
  scope : ClosureDebtScopeRecord ChallengeClass
  phases : List (OperatingPhaseRecord ChallengeClass)
  phasesNodup : phases.Nodup
  nonempty : phases ≠ []
  everyPhaseScoped : ∀ phase, phase ∈ phases -> phase.scope = scope
  coversHorizon :
    phases.head?.map OperatingPhaseRecord.startTime = some scope.horizon.startTime ∧
      phases.getLast?.map OperatingPhaseRecord.endTime = some scope.horizon.endTime
  orderedAndContiguous :
    ∀ phase1 phase2,
      ConsecutiveIn phases phase1 phase2 -> phase1.endTime = phase2.startTime

inductive ClosureDebtEntryRecord
    (X : Type u) (RecordValue : Type v) (Q : Type w)
    (TransportedValue : Type x) (FOut : Type y) (Readout : Type z)
    (RouteResiduePayload : Type u') (LedgerEntry : Type v')
    (e yDim xiDim : Nat) where
  | e14
      (residualRecord :
        ReconsolidationResidualRecord X RecordValue Q TransportedValue FOut Readout)
      (ledgerEntry : LedgerEntry)
  | f3
      (residueRecord : RouteResidueDebtRecord RouteResiduePayload)
      (ledgerEntry : LedgerEntry)
  | xi
      (residualRecord : XiAdequacyResidualDebtRecord e yDim xiDim)
      (ledgerEntry : LedgerEntry)

structure ClosureDebtSnapshotRecord
    (ChallengeClass : Type u) (X : Type v) (RecordValue : Type w)
    (Q : Type x) (TransportedValue : Type y) (FOut : Type z)
    (Readout : Type u') (RouteResiduePayload : Type v')
    (LedgerEntry : Type w') (e yDim xiDim : Nat) where
  snapshotId : Nat
  scope : ClosureDebtScopeRecord ChallengeClass
  observedAt : Rat
  entries : List
    (ClosureDebtEntryRecord X RecordValue Q TransportedValue FOut Readout
      RouteResiduePayload LedgerEntry e yDim xiDim)
  totalDebt : Rat

structure DebtDischargeRecord
    (ChallengeClass : Type u) (X : Type v) (RecordValue : Type w)
    (Q : Type x) (TransportedValue : Type y) (FOut : Type z)
    (Readout : Type u') (RouteResiduePayload : Type v')
    (LedgerEntry : Type w') (e yDim xiDim : Nat) where
  dischargeId : Nat
  phaseRecord : OperatingPhaseRecord ChallengeClass
  debtEntry :
    ClosureDebtEntryRecord X RecordValue Q TransportedValue FOut Readout
      RouteResiduePayload LedgerEntry e yDim xiDim
  amount : Rat
  dischargedAt : Rat

structure ClosureDebtFlowRecord
    (ChallengeClass : Type u) (X : Type v) (RecordValue : Type w)
    (Q : Type x) (TransportedValue : Type y) (FOut : Type z)
    (Readout : Type u') (RouteResiduePayload : Type v')
    (LedgerEntry : Type w') (e yDim xiDim : Nat) where
  flowId : Nat
  phaseRecord : OperatingPhaseRecord ChallengeClass
  beforeSnapshot :
    ClosureDebtSnapshotRecord ChallengeClass X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload LedgerEntry e yDim xiDim
  afterSnapshot :
    ClosureDebtSnapshotRecord ChallengeClass X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload LedgerEntry e yDim xiDim
  accruedEntries : List
    (ClosureDebtEntryRecord X RecordValue Q TransportedValue FOut Readout
      RouteResiduePayload LedgerEntry e yDim xiDim)
  dischargeRecords : List
    (DebtDischargeRecord ChallengeClass X RecordValue Q TransportedValue FOut
      Readout RouteResiduePayload LedgerEntry e yDim xiDim)

structure OfflineReclosureClassifierContext
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    (X : Type z) (RecordValue : Type z') (Q : Type z'')
    (TransportedValue : Type z''') (FOut : Type z'''')
    (Readout : Type z''''') (RouteResiduePayload : Type z'''''')
    (ChallengeClass : Type z''''''') (e yDim xiDim : Nat) where
  e14ResidualOutstanding :
    E14ResidualRegistrationRecord X RecordValue Q TransportedValue FOut Readout ->
      Rat -> Prop
  f3RouteResidueAwaitingReconciliation :
    RouteResidueDebtRecord RouteResiduePayload -> Rat -> Prop
  xiValuationPolicyAccepted : XiResidualValuationPolicyRecord -> Prop
  xiResidualAmount :
    XiResidualValuationPolicyRecord -> Mat xiDim xiDim -> Rat
  xiResidualAwaitingDischarge :
    XiAdequacyResidualDebtRecord e yDim xiDim -> Rat -> Prop
  ledgerEntryChargesRouteResidue :
    LedgerEntry -> RouteResidueDebtRecord RouteResiduePayload -> Rat -> Prop
  ledgerEntryChargesXiResidual :
    LedgerEntry -> XiAdequacyResidualDebtRecord e yDim xiDim -> Rat -> Prop
  gateClosesExternalExchange : ExchangeGateRecord S ChallengeClass -> Prop
  e7AlarmObservationAccepted : E7AlarmCascadeObservation ChallengeClass -> Prop
  e5StressObservationAccepted : E5StressCascadeObservation ChallengeClass -> Prop

structure OfflineReclosureEvidencePolicies
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    (X : Type z) (RecordValue : Type z') (Q : Type z'')
    (TransportedValue : Type z''') (FOut : Type z'''')
    (Readout : Type z''''') (RouteResiduePayload : Type z'''''')
    (ChallengeClass : Type z''''''') (e yDim xiDim : Nat) where
  scopePolicy : CarriedRecordPolicy S.T (ClosureDebtScopeRecord ChallengeClass)
  routeResiduePolicy :
    CarriedRecordPolicy S.T (RouteResidueDebtRecord RouteResiduePayload)
  xiValuationPolicy : CarriedRecordPolicy S.T XiResidualValuationPolicyRecord
  xiResidualPolicy :
    CarriedRecordPolicy S.T (XiAdequacyResidualDebtRecord e yDim xiDim)
  e14RegistrationPolicy :
    CarriedRecordPolicy S.T
      (E14ResidualRegistrationRecord X RecordValue Q TransportedValue FOut Readout)
  budgetAllocationPolicy :
    CarriedRecordPolicy S.T (SharedBudgetAllocationRecord ChallengeClass)
  phasePolicy : CarriedRecordPolicy S.T (OperatingPhaseRecord ChallengeClass)
  exchangeGatePolicy :
    CarriedRecordPolicy S.T (ExchangeGateRecord S ChallengeClass)
  exchangePolicy : CarriedRecordPolicy S.T (ExternalExchangeRecord ChallengeClass)
  tolerancePolicy :
    CarriedRecordPolicy S.T (DutyCycleToleranceRecord ChallengeClass)
  recurrenceBoundPolicy :
    CarriedRecordPolicy S.T (OfflineRecurrenceBoundRecord ChallengeClass)
  debtBoundPolicy : CarriedRecordPolicy S.T (DebtBoundRecord ChallengeClass)
  alarmObservationPolicy :
    CarriedRecordPolicy S.T (E7AlarmCascadeObservation ChallengeClass)
  stressObservationPolicy :
    CarriedRecordPolicy S.T (E5StressCascadeObservation ChallengeClass)
  schedulePolicy :
    CarriedRecordPolicy S.T (DeclaredOperatingSchedule ChallengeClass)
  debtSnapshotPolicy :
    CarriedRecordPolicy S.T
      (ClosureDebtSnapshotRecord ChallengeClass X RecordValue Q TransportedValue
        FOut Readout RouteResiduePayload LedgerEntry e yDim xiDim)
  dischargePolicy :
    CarriedRecordPolicy S.T
      (DebtDischargeRecord ChallengeClass X RecordValue Q TransportedValue FOut
        Readout RouteResiduePayload LedgerEntry e yDim xiDim)
  debtFlowPolicy :
    CarriedRecordPolicy S.T
      (ClosureDebtFlowRecord ChallengeClass X RecordValue Q TransportedValue
        FOut Readout RouteResiduePayload LedgerEntry e yDim xiDim)

def E15Carried
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord}
    {Record : Type z} (policy : CarriedRecordPolicy S.T Record)
    (record : Record) : Prop :=
  ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
    ∃ generatedByS : Bool, ∃ inScope : Bool,
      CarriedRecordAt policy record n0 sourceTag generatedByS inScope ∧
      CarriedSource sourceTag generatedByS inScope

structure P2ExternalExchangeGateEvidence
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (phaseRecord : OperatingPhaseRecord ChallengeClass) where
  gateRecord : ExchangeGateRecord S ChallengeClass
  gateCarried : E15Carried policies.exchangeGatePolicy gateRecord
  phaseLinked : gateRecord.phaseRecord = phaseRecord
  generatedByRepairGenerator : gateRecord.move = S.R_S gateRecord.defect
  sortIsP2 : gateRecord.move.sort.val = SixBirdsIII.Primitive.P2
  lawfulStep :
    LawfulRepairStep S.Lambda_S S.defectRecordPolicy S.moveRecordPolicy
      S.auditRecordPolicy S.I_S S.AdmissibleMove gateRecord.z gateRecord.z'
      gateRecord.defect gateRecord.move gateRecord.auditRecord
  closesDeclaredChannel : ctx.gateClosesExternalExchange gateRecord

structure E14ResidualDebtItem
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass) (asOf : Rat) where
  sourceRecord : CarriedMemoryRecord X RecordValue FOut Readout
  family : DeclaredRetrievalContextFamily
  trigger : ReconsolidationTrigger S e14ctx e14policies sourceRecord family
  unresolved :
    StatusedUnresolvedEvidence S e14ctx e14policies sourceRecord family trigger
  claimRef :
    ReconsolidationClaimRef X RecordValue Q TransportedValue FOut Readout
  claimSourceLinked : claimRef.sourceRecord = sourceRecord
  claimFamilyLinked : claimRef.family = family
  claimTransportLinked :
    claimRef.transportRecord = trigger.conflict.transport.transportRecord
  claimContextLinked :
    claimRef.contextRecord =
      trigger.conflict.transport.transportRecord.contextRecord
  claimRecordLinked : claimRef.claimRecord = sourceRecord.claimRecord
  statusPolicy :
    CarriedRecordPolicy S.T
      (ReconsolidationStatusRecord X RecordValue Q TransportedValue FOut Readout)
  statusRecord :
    ReconsolidationStatusRecord X RecordValue Q TransportedValue FOut Readout
  statusOccurrence :
    ReconsolidationStatusOccurrenceFor S statusPolicy claimRef statusRecord
  canonicalStatus :
    statusRecord.status = ReconsolidationStatus.statused_unresolved
  statusCase :
    StatusedUnresolvedCase S e14ctx e14policies statusPolicy claimRef statusRecord
  classifiedResidualLinked :
    statusRecord.residualRecord = some unresolved.residualRecord
  registrationRecord :
    E14ResidualRegistrationRecord X RecordValue Q TransportedValue FOut Readout
  registrationCarried :
    E15Carried policies.e14RegistrationPolicy registrationRecord
  registrationLinked :
    registrationRecord.residualRecord = unresolved.residualRecord
  recordedByAsOf : registrationRecord.registeredAt <= asOf
  outstandingAtAsOf : ctx.e14ResidualOutstanding registrationRecord asOf
  asOfInHorizon :
    scope.horizon.startTime <= asOf ∧ asOf <= scope.horizon.endTime
  claimLinked :
    unresolved.residualRecord.conflictRecord = trigger.conflict.conflictRecord
  scopeClaimLinked :
    unresolved.residualRecord.conflictRecord.claimRecord.claimId =
      scope.debtClaimId

namespace E14ResidualDebtItem

def amount
    {e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout}
    {e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout}
    {ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim}
    {policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim}
    {scope : ClosureDebtScopeRecord ChallengeClass} {asOf : Rat}
    (item : E14ResidualDebtItem S e14ctx e14policies ctx policies scope asOf) :
    Rat :=
  item.unresolved.residualRecord.residualAmount

def ledgerEntry
    {e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout}
    {e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout}
    {ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim}
    {policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim}
    {scope : ClosureDebtScopeRecord ChallengeClass} {asOf : Rat}
    (item : E14ResidualDebtItem S e14ctx e14policies ctx policies scope asOf) :
    LedgerEntry :=
  item.unresolved.ledgerEntry

end E14ResidualDebtItem

structure F3RouteResidueDebtItem
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass) (asOf : Rat) where
  residueRecord : RouteResidueDebtRecord RouteResiduePayload
  ledgerEntry : LedgerEntry
  residueCarried : E15Carried policies.routeResiduePolicy residueRecord
  positiveAmount : 0 < residueRecord.residualAmount
  claimLinked : residueRecord.reconciliationClaimId = scope.debtClaimId
  recordedByAsOf : residueRecord.recordedAt <= asOf
  asOfInHorizon :
    scope.horizon.startTime <= asOf ∧ asOf <= scope.horizon.endTime
  f3Certified : ctx.f3RouteResidueAwaitingReconciliation residueRecord asOf
  ledgerEntryPresent : ledgerEntry ∈ S.Lambda_S.ledgerEntries
  ledgerEntryCarried : E15Carried S.Lambda_S.ledgerPolicy ledgerEntry
  chargedToExistingLedger :
    ctx.ledgerEntryChargesRouteResidue ledgerEntry residueRecord
      residueRecord.residualAmount

structure XiAdequacyResidualDebtItem
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass) (asOf : Rat) where
  residualRecord : XiAdequacyResidualDebtRecord e yDim xiDim
  ledgerEntry : LedgerEntry
  valuationPolicyCarried :
    E15Carried policies.xiValuationPolicy residualRecord.valuationPolicy
  valuationDeclaredInAdvance :
    residualRecord.valuationPolicy.declaredAt <= scope.horizon.startTime
  valuationAccepted :
    ctx.xiValuationPolicyAccepted residualRecord.valuationPolicy
  residualCarried : E15Carried policies.xiResidualPolicy residualRecord
  matrixAmountLinked :
    residualRecord.residualAmount =
      ctx.xiResidualAmount residualRecord.valuationPolicy
        residualRecord.residualMatrix
  positiveAmount : 0 < residualRecord.residualAmount
  claimLinked : residualRecord.reconciliationClaimId = scope.debtClaimId
  recordedByAsOf : residualRecord.recordedAt <= asOf
  asOfInHorizon :
    scope.horizon.startTime <= asOf ∧ asOf <= scope.horizon.endTime
  awaitingDischarge : ctx.xiResidualAwaitingDischarge residualRecord asOf
  ledgerEntryPresent : ledgerEntry ∈ S.Lambda_S.ledgerEntries
  ledgerEntryCarried : E15Carried S.Lambda_S.ledgerPolicy ledgerEntry
  chargedToExistingLedger :
    ctx.ledgerEntryChargesXiResidual ledgerEntry residualRecord
      residualRecord.residualAmount

namespace ClosureDebtEntryRecord

def amount :
    ClosureDebtEntryRecord X RecordValue Q TransportedValue FOut Readout
      RouteResiduePayload LedgerEntry e yDim xiDim -> Rat
  | .e14 residualRecord _ => residualRecord.residualAmount
  | .f3 residueRecord _ => residueRecord.residualAmount
  | .xi residualRecord _ => residualRecord.residualAmount

def key :
    ClosureDebtEntryRecord X RecordValue Q TransportedValue FOut Readout
      RouteResiduePayload LedgerEntry e yDim xiDim ->
      ClosureDebtComponentKind × Nat
  | .e14 residualRecord _ =>
      (.e14_reconsolidation, residualRecord.residualId)
  | .f3 residueRecord _ => (.f3_route_residue, residueRecord.residueId)
  | .xi residualRecord _ => (.xi_adequacy_residual, residualRecord.residualId)

def ledgerEntry :
    ClosureDebtEntryRecord X RecordValue Q TransportedValue FOut Readout
      RouteResiduePayload LedgerEntry e yDim xiDim -> LedgerEntry
  | .e14 _ ledgerEntry => ledgerEntry
  | .f3 _ ledgerEntry => ledgerEntry
  | .xi _ ledgerEntry => ledgerEntry

end ClosureDebtEntryRecord

structure CompleteClosureDebtInventory
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass) (asOf : Rat)
    (entries : List
      (ClosureDebtEntryRecord X RecordValue Q TransportedValue FOut Readout
        RouteResiduePayload LedgerEntry e yDim xiDim)) where
  keysNodup : (entries.map ClosureDebtEntryRecord.key).Nodup
  ledgerChargesNodup :
    (entries.map ClosureDebtEntryRecord.ledgerEntry).Nodup
  everyE14Sound :
    ∀ residualRecord ledgerEntry,
      ClosureDebtEntryRecord.e14 residualRecord ledgerEntry ∈ entries ->
      ∃ item : E14ResidualDebtItem S e14ctx e14policies ctx policies scope asOf,
        item.unresolved.residualRecord = residualRecord ∧
          item.ledgerEntry = ledgerEntry
  everyF3Sound :
    ∀ residueRecord ledgerEntry,
      ClosureDebtEntryRecord.f3 residueRecord ledgerEntry ∈ entries ->
      ∃ item : F3RouteResidueDebtItem S ctx policies scope asOf,
        item.residueRecord = residueRecord ∧ item.ledgerEntry = ledgerEntry
  everyXiSound :
    ∀ residualRecord ledgerEntry,
      ClosureDebtEntryRecord.xi residualRecord ledgerEntry ∈ entries ->
      ∃ item : XiAdequacyResidualDebtItem S ctx policies scope asOf,
        item.residualRecord = residualRecord ∧ item.ledgerEntry = ledgerEntry
  everyE14Covered :
    ∀ item : E14ResidualDebtItem S e14ctx e14policies ctx policies scope asOf,
      ClosureDebtEntryRecord.e14 item.unresolved.residualRecord
        item.ledgerEntry ∈ entries
  everyF3Covered :
    ∀ item : F3RouteResidueDebtItem S ctx policies scope asOf,
      ClosureDebtEntryRecord.f3 item.residueRecord item.ledgerEntry ∈ entries
  everyXiCovered :
    ∀ item : XiAdequacyResidualDebtItem S ctx policies scope asOf,
      ClosureDebtEntryRecord.xi item.residualRecord item.ledgerEntry ∈ entries

def ClosureDebt
    (entries : List
      (ClosureDebtEntryRecord X RecordValue Q TransportedValue FOut Readout
        RouteResiduePayload LedgerEntry e yDim xiDim)) : Rat :=
  (entries.map ClosureDebtEntryRecord.amount).sum

structure CompleteClosureDebtSnapshot
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass)
    (snapshot : ClosureDebtSnapshotRecord ChallengeClass X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload LedgerEntry e yDim
      xiDim) where
  snapshotCarried : E15Carried policies.debtSnapshotPolicy snapshot
  scopeLinked : snapshot.scope = scope
  timeInHorizon :
    scope.horizon.startTime <= snapshot.observedAt ∧
      snapshot.observedAt <= scope.horizon.endTime
  inventory :
    CompleteClosureDebtInventory S e14ctx e14policies ctx policies scope
      snapshot.observedAt snapshot.entries
  totalComputed : snapshot.totalDebt = ClosureDebt snapshot.entries

def AccruedDebt
    (flow : ClosureDebtFlowRecord ChallengeClass X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload LedgerEntry e yDim
      xiDim) : Rat :=
  (flow.accruedEntries.map ClosureDebtEntryRecord.amount).sum

def DischargedDebt
    (flow : ClosureDebtFlowRecord ChallengeClass X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload LedgerEntry e yDim
      xiDim) : Rat :=
  (flow.dischargeRecords.map fun discharge => discharge.amount).sum

def PhaseDuration (phase : OperatingPhaseRecord ChallengeClass) : Rat :=
  phase.endTime - phase.startTime

def ClosureDebtAccrualRate
    (flow : ClosureDebtFlowRecord ChallengeClass X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload LedgerEntry e yDim
      xiDim) : Rat :=
  AccruedDebt flow / PhaseDuration flow.phaseRecord

def ClosureDebtDischargeRate
    (flow : ClosureDebtFlowRecord ChallengeClass X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload LedgerEntry e yDim
      xiDim) : Rat :=
  DischargedDebt flow / PhaseDuration flow.phaseRecord

structure CompleteClosureDebtFlow
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (flow : ClosureDebtFlowRecord ChallengeClass X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload LedgerEntry e yDim
      xiDim) where
  flowCarried : E15Carried policies.debtFlowPolicy flow
  beforeComplete : Nonempty
    (CompleteClosureDebtSnapshot S e14ctx e14policies ctx policies
      flow.phaseRecord.scope flow.beforeSnapshot)
  afterComplete : Nonempty
    (CompleteClosureDebtSnapshot S e14ctx e14policies ctx policies
      flow.phaseRecord.scope flow.afterSnapshot)
  phaseLinked :
    flow.beforeSnapshot.observedAt = flow.phaseRecord.startTime ∧
      flow.afterSnapshot.observedAt = flow.phaseRecord.endTime
  accruedEntriesNodup :
    (flow.accruedEntries.map ClosureDebtEntryRecord.key).Nodup
  dischargesNodup :
    (flow.dischargeRecords.map fun discharge => discharge.dischargeId).Nodup
  dischargedEntriesNodup :
    (flow.dischargeRecords.map fun discharge => discharge.debtEntry).Nodup
  everyAccrualNew :
    ∀ entry, entry ∈ flow.accruedEntries ->
      entry ∉ flow.beforeSnapshot.entries ∧ entry ∈ flow.afterSnapshot.entries
  everyNewEntryCovered :
    ∀ entry, entry ∈ flow.afterSnapshot.entries ->
      entry ∉ flow.beforeSnapshot.entries -> entry ∈ flow.accruedEntries
  everyDischargeCarried :
    ∀ discharge, discharge ∈ flow.dischargeRecords ->
      E15Carried policies.dischargePolicy discharge
  everyDischargeLinked :
    ∀ discharge, discharge ∈ flow.dischargeRecords ->
      discharge.phaseRecord = flow.phaseRecord ∧
      discharge.phaseRecord.startTime <= discharge.dischargedAt ∧
      discharge.dischargedAt <= discharge.phaseRecord.endTime ∧
      discharge.debtEntry ∈ flow.beforeSnapshot.entries ∧
      0 < discharge.amount ∧
      discharge.amount = ClosureDebtEntryRecord.amount discharge.debtEntry ∧
      discharge.debtEntry ∉ flow.afterSnapshot.entries
  balanceEquation :
    flow.afterSnapshot.totalDebt =
      flow.beforeSnapshot.totalDebt + AccruedDebt flow - DischargedDebt flow

structure DerivedOfflineBudgetGeometry
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass)
    (economy : ProbeEconomy S Probe XiFamily)
    (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (allocation : SharedBudgetAllocationRecord ChallengeClass) where
  allocationCarried : E15Carried policies.budgetAllocationPolicy allocation
  scopeLinked : allocation.scope = scope
  declaredInAdvance : allocation.declaredAt <= scope.horizon.startTime
  budgetBinding : BindingExposureBudget budgetData
  budgetEntryCarried :
    E15Carried S.Lambda_S.ledgerPolicy budgetData.budgetEntry
  spendEntryCarried :
    E15Carried S.Lambda_S.ledgerPolicy budgetData.spendEntry
  onlineExternalPositive : 0 < allocation.onlineExternalAllocation
  onlineInternalNonnegative : 0 <= allocation.onlineInternalDischargeAllocation
  onlineExhaustsSharedBudget :
    allocation.onlineExternalAllocation +
      allocation.onlineInternalDischargeAllocation = budgetData.budget
  offlineExchangeGated : allocation.offlineExternalAllocation = 0
  offlineInternalIsReallocation :
    allocation.offlineInternalDischargeAllocation =
      allocation.onlineInternalDischargeAllocation +
        allocation.onlineExternalAllocation
  offlineExhaustsSharedBudget :
    allocation.offlineExternalAllocation +
      allocation.offlineInternalDischargeAllocation = budgetData.budget

def kappaOn
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation) : Rat :=
  allocation.onlineInternalDischargeAllocation

def freedAllocation
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation) : Rat :=
  allocation.onlineExternalAllocation

def kappaOff
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation) : Rat :=
  allocation.offlineInternalDischargeAllocation

structure CompletePhaseFlowInventory
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (schedule : DeclaredOperatingSchedule ChallengeClass) where
  flows : List
    (ClosureDebtFlowRecord ChallengeClass X RecordValue Q TransportedValue FOut
      Readout RouteResiduePayload LedgerEntry e yDim xiDim)
  everyPhaseCarried :
    ∀ phase, phase ∈ schedule.phases -> E15Carried policies.phasePolicy phase
  everyPhaseCovered :
    ∀ phase, phase ∈ schedule.phases ->
      ∃ flow, flow ∈ flows ∧ flow.phaseRecord = phase ∧
        Nonempty
          (CompleteClosureDebtFlow S e14ctx e14policies ctx policies flow)
  flowSingleValuedPerPhase :
    ∀ flow1 flow2, flow1 ∈ flows -> flow2 ∈ flows ->
      flow1.phaseRecord = flow2.phaseRecord -> flow1 = flow2
  noForeignFlows :
    ∀ flow, flow ∈ flows -> flow.phaseRecord ∈ schedule.phases

structure EligibleExternalExchange
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (schedule : DeclaredOperatingSchedule ChallengeClass) where
  exchangeRecord : ExternalExchangeRecord ChallengeClass
  recordCarried : E15Carried policies.exchangePolicy exchangeRecord
  phaseMember : exchangeRecord.phaseRecord ∈ schedule.phases
  nonnegative : 0 <= exchangeRecord.exchangedAmount
  timedInPhase :
    exchangeRecord.phaseRecord.startTime <= exchangeRecord.recordedAt ∧
      exchangeRecord.recordedAt <= exchangeRecord.phaseRecord.endTime

structure CompleteExternalExchangeInventory
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (schedule : DeclaredOperatingSchedule ChallengeClass) where
  records : List (ExternalExchangeRecord ChallengeClass)
  recordsNodup : records.Nodup
  recordIdsNodup : (records.map fun record => record.exchangeRecordId).Nodup
  completeForSchedule :
    ∀ eligible : EligibleExternalExchange S policies schedule,
      eligible.exchangeRecord ∈ records
  soundForSchedule :
    ∀ record, record ∈ records ->
      ∃ eligible : EligibleExternalExchange S policies schedule,
        eligible.exchangeRecord = record
  everyPhaseCovered :
    ∀ phase, phase ∈ schedule.phases ->
      ∃ record, record ∈ records ∧ record.phaseRecord = phase

noncomputable def ExchangeInPhase
    {policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim}
    {schedule : DeclaredOperatingSchedule ChallengeClass}
    (inventory : CompleteExternalExchangeInventory S policies schedule)
    (phase : OperatingPhaseRecord ChallengeClass) : Rat := by
  classical
  exact
    ((inventory.records.filter fun record => record.phaseRecord = phase).map
      fun record => record.exchangedAmount).sum

def TotalDuration (schedule : DeclaredOperatingSchedule ChallengeClass) : Rat :=
  (schedule.phases.map PhaseDuration).sum

def OfflineDuration
    (schedule : DeclaredOperatingSchedule ChallengeClass) : Rat :=
  ((schedule.phases.filter fun phase => phase.mode = .offline).map
    PhaseDuration).sum

def ObservedOfflineDuty
    (schedule : DeclaredOperatingSchedule ChallengeClass) : Rat :=
  OfflineDuration schedule / TotalDuration schedule

def PredictedOfflineDuty (accrualRate : Rat)
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation) : Rat :=
  (accrualRate - kappaOn S geometry) /
    ((accrualRate - kappaOn S geometry) + kappaOff S geometry)

def RatAbs (value : Rat) : Rat :=
  if value < 0 then -value else value

structure PersistentDeficitEvidence
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (allocation : SharedBudgetAllocationRecord ChallengeClass)
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation) where
  schedule : DeclaredOperatingSchedule ChallengeClass
  scheduleCarried : E15Carried policies.schedulePolicy schedule
  flowInventory :
    CompletePhaseFlowInventory S e14ctx e14policies ctx policies schedule
  everyPhaseUsesClaimAllocation :
    ∀ phase, phase ∈ schedule.phases -> phase.allocationRecord = allocation
  onlinePhaseExists :
    ∃ phase, phase ∈ schedule.phases ∧ phase.mode = .online
  accrualRate : Rat
  everyOnlineRateLinked :
    ∀ phase, phase ∈ schedule.phases -> phase.mode = .online ->
      ∃ flow, flow ∈ flowInventory.flows ∧ flow.phaseRecord = phase ∧
        ClosureDebtAccrualRate flow = accrualRate
  everyOnlineDischargeWithinCapacity :
    ∀ phase, phase ∈ schedule.phases -> phase.mode = .online ->
      ∃ flow, flow ∈ flowInventory.flows ∧ flow.phaseRecord = phase ∧
        ClosureDebtDischargeRate flow <= kappaOn S geometry
  persistentDeficit : kappaOn S geometry < accrualRate

structure GenuineOfflinePhaseEvidence
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (allocation : SharedBudgetAllocationRecord ChallengeClass)
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation)
    (schedule : DeclaredOperatingSchedule ChallengeClass)
    (flowInventory :
      CompletePhaseFlowInventory S e14ctx e14policies ctx policies schedule)
    (exchangeInventory :
      CompleteExternalExchangeInventory S policies schedule) where
  phaseRecord : OperatingPhaseRecord ChallengeClass
  flowRecord : ClosureDebtFlowRecord ChallengeClass X RecordValue Q
    TransportedValue FOut Readout RouteResiduePayload LedgerEntry e yDim xiDim
  phaseMember : phaseRecord ∈ schedule.phases
  phaseOffline : phaseRecord.mode = .offline
  phaseCarried : E15Carried policies.phasePolicy phaseRecord
  flowCarried : E15Carried policies.debtFlowPolicy flowRecord
  flowLinked : flowRecord.phaseRecord = phaseRecord
  flowMember : flowRecord ∈ flowInventory.flows
  flowComplete : Nonempty
    (CompleteClosureDebtFlow S e14ctx e14policies ctx policies flowRecord)
  usesClaimAllocation : phaseRecord.allocationRecord = allocation
  p2ExchangeGate :
    P2ExternalExchangeGateEvidence S ctx policies phaseRecord
  exchangeGated : ExchangeInPhase S exchangeInventory phaseRecord = 0
  positiveMeasuredDischarge : 0 < DischargedDebt flowRecord
  debtStrictlyReduced :
    flowRecord.afterSnapshot.totalDebt < flowRecord.beforeSnapshot.totalDebt
  dischargeWithinDerivedCapacity :
    ClosureDebtDischargeRate flowRecord <= kappaOff S geometry
  usesOfflineAllocation :
    phaseRecord.allocationRecord.offlineInternalDischargeAllocation =
      kappaOff S geometry

structure AlternatingOfflineSubstrate
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (allocation : SharedBudgetAllocationRecord ChallengeClass)
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation) where
  deficit : PersistentDeficitEvidence S e14ctx e14policies ctx policies scope
    economy move budgetData allocation geometry
  exchangeInventory :
    CompleteExternalExchangeInventory S policies deficit.schedule
  recurrenceBound : OfflineRecurrenceBoundRecord ChallengeClass
  recurrenceBoundCarried :
    E15Carried policies.recurrenceBoundPolicy recurrenceBound
  recurrenceBoundScoped : recurrenceBound.scope = scope
  recurrenceBoundDeclaredInAdvance :
    recurrenceBound.declaredAt <= scope.horizon.startTime
  atLeastTwoOfflinePhases :
    2 <= (deficit.schedule.phases.filter fun phase =>
      phase.mode = .offline).length
  startsOnline :
    deficit.schedule.phases.head?.map OperatingPhaseRecord.mode = some .online
  alternates :
    ∀ phase1 phase2,
      ConsecutiveIn deficit.schedule.phases phase1 phase2 ->
        phase1.mode ≠ phase2.mode
  everyOnlineExchanges :
    ∀ phase, phase ∈ deficit.schedule.phases -> phase.mode = .online ->
      0 < ExchangeInPhase S exchangeInventory phase
  everyOnlineUsesDerivedCapacity :
    ∀ phase, phase ∈ deficit.schedule.phases -> phase.mode = .online ->
      ∃ flow, flow ∈ deficit.flowInventory.flows ∧ flow.phaseRecord = phase ∧
        ClosureDebtDischargeRate flow = kappaOn S geometry
  everyOfflineGenuine :
    ∀ phase, phase ∈ deficit.schedule.phases -> phase.mode = .offline ->
      ∃ offline : GenuineOfflinePhaseEvidence S e14ctx e14policies ctx policies
          scope economy move budgetData allocation geometry deficit.schedule
          deficit.flowInventory exchangeInventory,
        offline.phaseRecord = phase ∧
          ClosureDebtDischargeRate offline.flowRecord = kappaOff S geometry
          ∧ AccruedDebt offline.flowRecord = 0
  recurring :
    ∀ phase, phase ∈ deficit.schedule.phases -> phase.mode = .online ->
      PhaseDuration phase <= recurrenceBound.maximumOnlineRun ∧
        ∃ laterOffline, laterOffline ∈ deficit.schedule.phases ∧
          laterOffline.mode = .offline ∧ phase.endTime <= laterOffline.startTime

structure DutyCyclePredictionEvidence
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (allocation : SharedBudgetAllocationRecord ChallengeClass)
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation) where
  substrate : AlternatingOfflineSubstrate S e14ctx e14policies ctx policies
    scope economy move budgetData allocation geometry
  toleranceRecord : DutyCycleToleranceRecord ChallengeClass
  toleranceCarried : E15Carried policies.tolerancePolicy toleranceRecord
  toleranceScoped : toleranceRecord.scope = scope
  toleranceDeclaredInAdvance :
    toleranceRecord.declaredAt <= scope.horizon.startTime
  predictionWithinTolerance :
    RatAbs (ObservedOfflineDuty substrate.deficit.schedule -
      PredictedOfflineDuty S substrate.deficit.accrualRate geometry) <=
        toleranceRecord.tolerance

structure OnlineSufficientEvidence
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (allocation : SharedBudgetAllocationRecord ChallengeClass)
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation) where
  schedule : DeclaredOperatingSchedule ChallengeClass
  scheduleCarried : E15Carried policies.schedulePolicy schedule
  flowInventory :
    CompletePhaseFlowInventory S e14ctx e14policies ctx policies schedule
  exchangeInventory :
    CompleteExternalExchangeInventory S policies schedule
  everyPhaseUsesClaimAllocation :
    ∀ phase, phase ∈ schedule.phases -> phase.allocationRecord = allocation
  everyPhaseOnline :
    ∀ phase, phase ∈ schedule.phases -> phase.mode = .online
  everyOnlineActuallyOffsetsAccrualWithinCapacity :
    ∀ flow, flow ∈ flowInventory.flows ->
      ClosureDebtAccrualRate flow <= ClosureDebtDischargeRate flow ∧
        ClosureDebtDischargeRate flow <= kappaOn S geometry
  debtNonincreasing :
    ∀ flow, flow ∈ flowInventory.flows ->
      flow.afterSnapshot.totalDebt <= flow.beforeSnapshot.totalDebt
  everyPhaseExchanges :
    ∀ phase, phase ∈ schedule.phases ->
      0 < ExchangeInPhase S exchangeInventory phase

structure OptionalOfflineOutsideDeficitEvidence
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (allocation : SharedBudgetAllocationRecord ChallengeClass)
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation) where
  schedule : DeclaredOperatingSchedule ChallengeClass
  scheduleCarried : E15Carried policies.schedulePolicy schedule
  flowInventory :
    CompletePhaseFlowInventory S e14ctx e14policies ctx policies schedule
  exchangeInventory :
    CompleteExternalExchangeInventory S policies schedule
  everyPhaseUsesClaimAllocation :
    ∀ phase, phase ∈ schedule.phases -> phase.allocationRecord = allocation
  onlineAccrualRate : Rat
  onlinePhaseExists :
    ∃ phase, phase ∈ schedule.phases ∧ phase.mode = .online
  everyOnlineRateLinked :
    ∀ phase, phase ∈ schedule.phases -> phase.mode = .online ->
      ∃ flow, flow ∈ flowInventory.flows ∧ flow.phaseRecord = phase ∧
        ClosureDebtAccrualRate flow = onlineAccrualRate
  everyOnlineDischargeWithinCapacity :
    ∀ phase, phase ∈ schedule.phases -> phase.mode = .online ->
      ∃ flow, flow ∈ flowInventory.flows ∧ flow.phaseRecord = phase ∧
        ClosureDebtDischargeRate flow <= kappaOn S geometry
  onlineCapacitySufficient : onlineAccrualRate <= kappaOn S geometry
  offlinePhaseExists :
    ∃ phase, phase ∈ schedule.phases ∧ phase.mode = .offline
  everyOfflineGenuine :
    ∀ phase, phase ∈ schedule.phases -> phase.mode = .offline ->
      ∃ offline : GenuineOfflinePhaseEvidence S e14ctx e14policies ctx policies
          scope economy move budgetData allocation geometry schedule
          flowInventory exchangeInventory,
        offline.phaseRecord = phase

structure DeficitOnlineBoundedCounterexample
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (allocation : SharedBudgetAllocationRecord ChallengeClass)
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation) where
  deficit : PersistentDeficitEvidence S e14ctx e14policies ctx policies scope
    economy move budgetData allocation geometry
  exchangeInventory :
    CompleteExternalExchangeInventory S policies deficit.schedule
  debtBound : DebtBoundRecord ChallengeClass
  boundCarried : E15Carried policies.debtBoundPolicy debtBound
  boundScoped : debtBound.scope = scope
  boundDeclaredInAdvance : debtBound.declaredAt <= scope.horizon.startTime
  recurrenceBound : OfflineRecurrenceBoundRecord ChallengeClass
  recurrenceBoundCarried :
    E15Carried policies.recurrenceBoundPolicy recurrenceBound
  recurrenceBoundScoped : recurrenceBound.scope = scope
  recurrenceBoundDeclaredInAdvance :
    recurrenceBound.declaredAt <= scope.horizon.startTime
  horizonExceedsRecurrenceBound :
    recurrenceBound.maximumOnlineRun <
      scope.horizon.endTime - scope.horizon.startTime
  allPhasesOnline :
    ∀ phase, phase ∈ deficit.schedule.phases -> phase.mode = .online
  everyOnlineDischargeWithinCapacity :
    ∀ flow, flow ∈ deficit.flowInventory.flows ->
      ClosureDebtDischargeRate flow <= kappaOn S geometry
  everySnapshotBounded :
    ∀ flow, flow ∈ deficit.flowInventory.flows ->
      flow.beforeSnapshot.totalDebt <= debtBound.upperBound ∧
        flow.afterSnapshot.totalDebt <= debtBound.upperBound
  exchangePersists :
    ∀ phase, phase ∈ deficit.schedule.phases ->
      0 < ExchangeInPhase S exchangeInventory phase

structure DecorativeOfflineEvidence
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (allocation : SharedBudgetAllocationRecord ChallengeClass)
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation)
    (schedule : DeclaredOperatingSchedule ChallengeClass)
    (flowInventory :
      CompletePhaseFlowInventory S e14ctx e14policies ctx policies schedule)
    (exchangeInventory :
      CompleteExternalExchangeInventory S policies schedule) where
  phaseRecord : OperatingPhaseRecord ChallengeClass
  flowRecord : ClosureDebtFlowRecord ChallengeClass X RecordValue Q
    TransportedValue FOut Readout RouteResiduePayload LedgerEntry e yDim xiDim
  phaseMember : phaseRecord ∈ schedule.phases
  labelledOffline : phaseRecord.mode = .offline
  phaseCarried : E15Carried policies.phasePolicy phaseRecord
  flowCarried : E15Carried policies.debtFlowPolicy flowRecord
  flowLinked : flowRecord.phaseRecord = phaseRecord
  flowMember : flowRecord ∈ flowInventory.flows
  flowComplete : Nonempty
    (CompleteClosureDebtFlow S e14ctx e14policies ctx policies flowRecord)
  concreteFailure :
    0 < ExchangeInPhase S exchangeInventory phaseRecord ∨
      phaseRecord.allocationRecord ≠ allocation ∨
      phaseRecord.allocationRecord.offlineExternalAllocation ≠ 0 ∨
      phaseRecord.allocationRecord.offlineInternalDischargeAllocation ≠
        allocation.onlineInternalDischargeAllocation +
          allocation.onlineExternalAllocation ∨
      DischargedDebt flowRecord <= 0 ∨
      flowRecord.beforeSnapshot.totalDebt <= flowRecord.afterSnapshot.totalDebt ∨
      kappaOff S geometry < ClosureDebtDischargeRate flowRecord

structure DutyCycleMismatchEvidence
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (allocation : SharedBudgetAllocationRecord ChallengeClass)
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation) where
  substrate : AlternatingOfflineSubstrate S e14ctx e14policies ctx policies
    scope economy move budgetData allocation geometry
  toleranceRecord : DutyCycleToleranceRecord ChallengeClass
  toleranceCarried : E15Carried policies.tolerancePolicy toleranceRecord
  toleranceScoped : toleranceRecord.scope = scope
  toleranceDeclaredInAdvance :
    toleranceRecord.declaredAt <= scope.horizon.startTime
  exceedsTolerance :
    toleranceRecord.tolerance <
      RatAbs (ObservedOfflineDuty substrate.deficit.schedule -
        PredictedOfflineDuty S substrate.deficit.accrualRate geometry)

structure SkippedOfflineCascadeEvidence
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (allocation : SharedBudgetAllocationRecord ChallengeClass)
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation) where
  deficit : PersistentDeficitEvidence S e14ctx e14policies ctx policies scope
    economy move budgetData allocation geometry
  exchangeInventory :
    CompleteExternalExchangeInventory S policies deficit.schedule
  allPhasesOnline :
    ∀ phase, phase ∈ deficit.schedule.phases -> phase.mode = .online
  debtGrows :
    ∀ flow, flow ∈ deficit.flowInventory.flows ->
      flow.beforeSnapshot.totalDebt < flow.afterSnapshot.totalDebt
  alarmObservation : E7AlarmCascadeObservation ChallengeClass
  stressObservation : E5StressCascadeObservation ChallengeClass
  alarmCarried :
    E15Carried policies.alarmObservationPolicy alarmObservation
  stressCarried :
    E15Carried policies.stressObservationPolicy stressObservation
  alarmScoped : alarmObservation.scope = scope
  stressScoped : stressObservation.scope = scope
  alarmTimedInNamedPhase :
    alarmObservation.phaseRecord.startTime <= alarmObservation.observedAt ∧
      alarmObservation.observedAt <= alarmObservation.phaseRecord.endTime
  stressTimedInNamedPhase :
    stressObservation.phaseRecord.startTime <= stressObservation.observedAt ∧
      stressObservation.observedAt <= stressObservation.phaseRecord.endTime
  alarmAccepted : ctx.e7AlarmObservationAccepted alarmObservation
  stressAccepted : ctx.e5StressObservationAccepted stressObservation
  stressTag : stressObservation.status = ReclosureCollapseStatus.stressed
  chronological : alarmObservation.observedAt < stressObservation.observedAt
  sameDebtLineage :
    alarmObservation.phaseRecord ∈ deficit.schedule.phases ∧
      stressObservation.phaseRecord ∈ deficit.schedule.phases

end Setup

section StatusApparatus

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)

variable {X : Type z} {RecordValue : Type z'} {Q : Type z''}
variable {TransportedValue : Type z'''} {FOut : Type z''''}
variable {Readout : Type z'''''}
variable {RouteResiduePayload : Type z''''''}
variable {Probe : Type z'''''''} {XiFamily : Type z''''''''}
variable {ChallengeClass : Type z'''''''''}
variable {e yDim xiDim : Nat}

inductive OfflineReclosureStatus where
  | deficit_online_counterexample
  | decorative_offline
  | duty_cycle_mismatch
  | skipped_offline_cascade
  | alternation_required
  | online_sufficient
  | offline_optional
  | offline_reclosure_rejected
  deriving DecidableEq, Repr

structure OfflineReclosureClaimRef
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim) where
  scope : ClosureDebtScopeRecord ChallengeClass
  allocationRecord : SharedBudgetAllocationRecord ChallengeClass
  schedule : DeclaredOperatingSchedule ChallengeClass
  toleranceRecord : DutyCycleToleranceRecord ChallengeClass
  recurrenceBound : OfflineRecurrenceBoundRecord ChallengeClass
  scopeCarried : E15Carried policies.scopePolicy scope
  allocationCarried :
    E15Carried policies.budgetAllocationPolicy allocationRecord
  scheduleCarried : E15Carried policies.schedulePolicy schedule
  toleranceCarried : E15Carried policies.tolerancePolicy toleranceRecord
  recurrenceBoundCarried :
    E15Carried policies.recurrenceBoundPolicy recurrenceBound
  allocationScoped : allocationRecord.scope = scope
  scheduleScoped : schedule.scope = scope
  toleranceScoped : toleranceRecord.scope = scope
  recurrenceBoundScoped : recurrenceBound.scope = scope
  allocationDeclaredInAdvance :
    allocationRecord.declaredAt <= scope.horizon.startTime
  toleranceDeclaredInAdvance :
    toleranceRecord.declaredAt <= scope.horizon.startTime
  recurrenceBoundDeclaredInAdvance :
    recurrenceBound.declaredAt <= scope.horizon.startTime

structure OfflineReclosureStatusRecord (ChallengeClass : Type u) where
  statusRecordId : Nat
  status : OfflineReclosureStatus
  scope : ClosureDebtScopeRecord ChallengeClass
  allocationRecord : SharedBudgetAllocationRecord ChallengeClass
  schedule : DeclaredOperatingSchedule ChallengeClass
  toleranceRecord : DutyCycleToleranceRecord ChallengeClass
  recurrenceBound : OfflineRecurrenceBoundRecord ChallengeClass
  phaseRecord : Option (OperatingPhaseRecord ChallengeClass)
  alarmObservation : Option (E7AlarmCascadeObservation ChallengeClass)
  stressObservation : Option (E5StressCascadeObservation ChallengeClass)

def OfflineReclosureStatusRecordMatchesClaim
    {policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim}
    (claimRef : OfflineReclosureClaimRef S policies)
    (record : OfflineReclosureStatusRecord ChallengeClass) : Prop :=
  record.scope = claimRef.scope ∧
  record.allocationRecord = claimRef.allocationRecord ∧
  record.schedule = claimRef.schedule ∧
  record.toleranceRecord = claimRef.toleranceRecord ∧
  record.recurrenceBound = claimRef.recurrenceBound

def OfflineReclosureStatusOccurrenceFor
    {policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim}
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (record : OfflineReclosureStatusRecord ChallengeClass) : Prop :=
  OfflineReclosureStatusRecordMatchesClaim S claimRef record ∧
  ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
    ∃ generatedByS : Bool, ∃ inScope : Bool,
      CarriedRecordAt statusPolicy record n0 sourceTag generatedByS inScope ∧
      CarriedSource sourceTag generatedByS inScope

def DeficitOnlineCounterexampleEvidenceFor
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (claimRef : OfflineReclosureClaimRef S policies) : Prop :=
  ∃ geometry : DerivedOfflineBudgetGeometry S policies claimRef.scope economy
      move budgetData claimRef.allocationRecord,
    ∃ witness : DeficitOnlineBoundedCounterexample S e14ctx e14policies ctx
        policies claimRef.scope economy move budgetData claimRef.allocationRecord
        geometry,
      witness.deficit.schedule = claimRef.schedule ∧
      witness.recurrenceBound = claimRef.recurrenceBound

def DecorativeOfflineEvidenceFor
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (claimRef : OfflineReclosureClaimRef S policies) : Prop :=
  ∃ geometry : DerivedOfflineBudgetGeometry S policies claimRef.scope economy
      move budgetData claimRef.allocationRecord,
    ∃ flowInventory : CompletePhaseFlowInventory S e14ctx e14policies ctx
        policies claimRef.schedule,
      ∃ exchangeInventory : CompleteExternalExchangeInventory S policies
          claimRef.schedule,
        ∃ witness : DecorativeOfflineEvidence S e14ctx e14policies ctx policies
            claimRef.scope economy move budgetData claimRef.allocationRecord
            geometry claimRef.schedule flowInventory exchangeInventory,
          witness.phaseRecord ∈ claimRef.schedule.phases

def DutyCycleMismatchEvidenceFor
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (claimRef : OfflineReclosureClaimRef S policies) : Prop :=
  ∃ geometry : DerivedOfflineBudgetGeometry S policies claimRef.scope economy
      move budgetData claimRef.allocationRecord,
    ∃ witness : DutyCycleMismatchEvidence S e14ctx e14policies ctx policies
        claimRef.scope economy move budgetData claimRef.allocationRecord geometry,
      witness.substrate.deficit.schedule = claimRef.schedule ∧
      witness.toleranceRecord = claimRef.toleranceRecord ∧
      witness.substrate.recurrenceBound = claimRef.recurrenceBound

def SkippedOfflineCascadeEvidenceFor
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (claimRef : OfflineReclosureClaimRef S policies) : Prop :=
  ∃ geometry : DerivedOfflineBudgetGeometry S policies claimRef.scope economy
      move budgetData claimRef.allocationRecord,
    ∃ witness : SkippedOfflineCascadeEvidence S e14ctx e14policies ctx policies
        claimRef.scope economy move budgetData claimRef.allocationRecord geometry,
      witness.deficit.schedule = claimRef.schedule

def AlternationRequiredEvidenceFor
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (claimRef : OfflineReclosureClaimRef S policies) : Prop :=
  ∃ geometry : DerivedOfflineBudgetGeometry S policies claimRef.scope economy
      move budgetData claimRef.allocationRecord,
    ∃ witness : DutyCyclePredictionEvidence S e14ctx e14policies ctx policies
        claimRef.scope economy move budgetData claimRef.allocationRecord geometry,
      witness.substrate.deficit.schedule = claimRef.schedule ∧
      witness.toleranceRecord = claimRef.toleranceRecord ∧
      witness.substrate.recurrenceBound = claimRef.recurrenceBound

def OnlineSufficientEvidenceFor
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (claimRef : OfflineReclosureClaimRef S policies) : Prop :=
  ∃ geometry : DerivedOfflineBudgetGeometry S policies claimRef.scope economy
      move budgetData claimRef.allocationRecord,
    ∃ witness : OnlineSufficientEvidence S e14ctx e14policies ctx policies
        claimRef.scope economy move budgetData claimRef.allocationRecord geometry,
      witness.schedule = claimRef.schedule

def OfflineOptionalEvidenceFor
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (claimRef : OfflineReclosureClaimRef S policies) : Prop :=
  ∃ geometry : DerivedOfflineBudgetGeometry S policies claimRef.scope economy
      move budgetData claimRef.allocationRecord,
    ∃ witness : OptionalOfflineOutsideDeficitEvidence S e14ctx e14policies ctx
        policies claimRef.scope economy move budgetData claimRef.allocationRecord
        geometry,
      witness.schedule = claimRef.schedule

def DeficitOnlineCounterexampleCase
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (record : OfflineReclosureStatusRecord ChallengeClass) : Prop :=
  OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
  record.status = OfflineReclosureStatus.deficit_online_counterexample ∧
  ∃ geometry : DerivedOfflineBudgetGeometry S policies claimRef.scope economy
      move budgetData claimRef.allocationRecord,
    ∃ witness : DeficitOnlineBoundedCounterexample S e14ctx e14policies ctx
        policies claimRef.scope economy move budgetData claimRef.allocationRecord
        geometry,
      witness.deficit.schedule = claimRef.schedule ∧
      witness.recurrenceBound = claimRef.recurrenceBound

def DecorativeOfflineCase
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (record : OfflineReclosureStatusRecord ChallengeClass) : Prop :=
  OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
  ¬ DeficitOnlineCounterexampleEvidenceFor S e14ctx e14policies ctx policies
      economy move budgetData claimRef ∧
  record.status = OfflineReclosureStatus.decorative_offline ∧
  ∃ geometry : DerivedOfflineBudgetGeometry S policies claimRef.scope economy
      move budgetData claimRef.allocationRecord,
    ∃ flowInventory : CompletePhaseFlowInventory S e14ctx e14policies ctx
        policies claimRef.schedule,
      ∃ exchangeInventory : CompleteExternalExchangeInventory S policies
          claimRef.schedule,
        ∃ witness : DecorativeOfflineEvidence S e14ctx e14policies ctx policies
            claimRef.scope economy move budgetData claimRef.allocationRecord
            geometry claimRef.schedule flowInventory exchangeInventory,
          witness.phaseRecord ∈ claimRef.schedule.phases ∧
          record.phaseRecord = some witness.phaseRecord

def DutyCycleMismatchCase
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (record : OfflineReclosureStatusRecord ChallengeClass) : Prop :=
  OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
  ¬ DeficitOnlineCounterexampleEvidenceFor S e14ctx e14policies ctx policies
      economy move budgetData claimRef ∧
  ¬ DecorativeOfflineEvidenceFor S e14ctx e14policies ctx policies economy move
      budgetData claimRef ∧
  record.status = OfflineReclosureStatus.duty_cycle_mismatch ∧
  ∃ geometry : DerivedOfflineBudgetGeometry S policies claimRef.scope economy
      move budgetData claimRef.allocationRecord,
    ∃ witness : DutyCycleMismatchEvidence S e14ctx e14policies ctx policies
        claimRef.scope economy move budgetData claimRef.allocationRecord geometry,
      witness.substrate.deficit.schedule = claimRef.schedule ∧
      witness.toleranceRecord = claimRef.toleranceRecord ∧
      witness.substrate.recurrenceBound = claimRef.recurrenceBound

def SkippedOfflineCascadeCase
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (record : OfflineReclosureStatusRecord ChallengeClass) : Prop :=
  OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
  ¬ DeficitOnlineCounterexampleEvidenceFor S e14ctx e14policies ctx policies
      economy move budgetData claimRef ∧
  ¬ DecorativeOfflineEvidenceFor S e14ctx e14policies ctx policies economy move
      budgetData claimRef ∧
  ¬ DutyCycleMismatchEvidenceFor S e14ctx e14policies ctx policies economy move
      budgetData claimRef ∧
  record.status = OfflineReclosureStatus.skipped_offline_cascade ∧
  ∃ geometry : DerivedOfflineBudgetGeometry S policies claimRef.scope economy
      move budgetData claimRef.allocationRecord,
    ∃ witness : SkippedOfflineCascadeEvidence S e14ctx e14policies ctx policies
        claimRef.scope economy move budgetData claimRef.allocationRecord geometry,
      witness.deficit.schedule = claimRef.schedule ∧
      record.alarmObservation = some witness.alarmObservation ∧
      record.stressObservation = some witness.stressObservation

def AlternationRequiredCase
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (record : OfflineReclosureStatusRecord ChallengeClass) : Prop :=
  OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
  ¬ DeficitOnlineCounterexampleEvidenceFor S e14ctx e14policies ctx policies
      economy move budgetData claimRef ∧
  ¬ DecorativeOfflineEvidenceFor S e14ctx e14policies ctx policies economy move
      budgetData claimRef ∧
  ¬ DutyCycleMismatchEvidenceFor S e14ctx e14policies ctx policies economy move
      budgetData claimRef ∧
  ¬ SkippedOfflineCascadeEvidenceFor S e14ctx e14policies ctx policies economy
      move budgetData claimRef ∧
  record.status = OfflineReclosureStatus.alternation_required ∧
  ∃ geometry : DerivedOfflineBudgetGeometry S policies claimRef.scope economy
      move budgetData claimRef.allocationRecord,
    ∃ witness : DutyCyclePredictionEvidence S e14ctx e14policies ctx policies
        claimRef.scope economy move budgetData claimRef.allocationRecord geometry,
      witness.substrate.deficit.schedule = claimRef.schedule ∧
      witness.toleranceRecord = claimRef.toleranceRecord ∧
      witness.substrate.recurrenceBound = claimRef.recurrenceBound

def OnlineSufficientCase
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (record : OfflineReclosureStatusRecord ChallengeClass) : Prop :=
  OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
  ¬ DeficitOnlineCounterexampleEvidenceFor S e14ctx e14policies ctx policies
      economy move budgetData claimRef ∧
  ¬ DecorativeOfflineEvidenceFor S e14ctx e14policies ctx policies economy move
      budgetData claimRef ∧
  ¬ DutyCycleMismatchEvidenceFor S e14ctx e14policies ctx policies economy move
      budgetData claimRef ∧
  ¬ SkippedOfflineCascadeEvidenceFor S e14ctx e14policies ctx policies economy
      move budgetData claimRef ∧
  ¬ AlternationRequiredEvidenceFor S e14ctx e14policies ctx policies economy
      move budgetData claimRef ∧
  record.status = OfflineReclosureStatus.online_sufficient ∧
  ∃ geometry : DerivedOfflineBudgetGeometry S policies claimRef.scope economy
      move budgetData claimRef.allocationRecord,
    ∃ witness : OnlineSufficientEvidence S e14ctx e14policies ctx policies
        claimRef.scope economy move budgetData claimRef.allocationRecord geometry,
      witness.schedule = claimRef.schedule

def OfflineOptionalCase
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (record : OfflineReclosureStatusRecord ChallengeClass) : Prop :=
  OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
  ¬ DeficitOnlineCounterexampleEvidenceFor S e14ctx e14policies ctx policies
      economy move budgetData claimRef ∧
  ¬ DecorativeOfflineEvidenceFor S e14ctx e14policies ctx policies economy move
      budgetData claimRef ∧
  ¬ DutyCycleMismatchEvidenceFor S e14ctx e14policies ctx policies economy move
      budgetData claimRef ∧
  ¬ SkippedOfflineCascadeEvidenceFor S e14ctx e14policies ctx policies economy
      move budgetData claimRef ∧
  ¬ AlternationRequiredEvidenceFor S e14ctx e14policies ctx policies economy
      move budgetData claimRef ∧
  ¬ OnlineSufficientEvidenceFor S e14ctx e14policies ctx policies economy move
      budgetData claimRef ∧
  record.status = OfflineReclosureStatus.offline_optional ∧
  ∃ geometry : DerivedOfflineBudgetGeometry S policies claimRef.scope economy
      move budgetData claimRef.allocationRecord,
    ∃ witness : OptionalOfflineOutsideDeficitEvidence S e14ctx e14policies ctx
        policies claimRef.scope economy move budgetData claimRef.allocationRecord
        geometry,
      witness.schedule = claimRef.schedule

def OfflineReclosureRejectedCase
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (record : OfflineReclosureStatusRecord ChallengeClass) : Prop :=
  OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
  ¬ DeficitOnlineCounterexampleEvidenceFor S e14ctx e14policies ctx policies
      economy move budgetData claimRef ∧
  ¬ DecorativeOfflineEvidenceFor S e14ctx e14policies ctx policies economy move
      budgetData claimRef ∧
  ¬ DutyCycleMismatchEvidenceFor S e14ctx e14policies ctx policies economy move
      budgetData claimRef ∧
  ¬ SkippedOfflineCascadeEvidenceFor S e14ctx e14policies ctx policies economy
      move budgetData claimRef ∧
  ¬ AlternationRequiredEvidenceFor S e14ctx e14policies ctx policies economy
      move budgetData claimRef ∧
  ¬ OnlineSufficientEvidenceFor S e14ctx e14policies ctx policies economy move
      budgetData claimRef ∧
  ¬ OfflineOptionalEvidenceFor S e14ctx e14policies ctx policies economy move
      budgetData claimRef ∧
  record.status = OfflineReclosureStatus.offline_reclosure_rejected

def DeficitOnlineCounterexampleHolds
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies) : Prop :=
  ∃ record : OfflineReclosureStatusRecord ChallengeClass,
    OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = OfflineReclosureStatus.deficit_online_counterexample ∧
    DeficitOnlineCounterexampleCase S e14ctx e14policies ctx policies economy
      move budgetData statusPolicy claimRef record

def DecorativeOfflineHolds
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies) : Prop :=
  ∃ record : OfflineReclosureStatusRecord ChallengeClass,
    OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = OfflineReclosureStatus.decorative_offline ∧
    DecorativeOfflineCase S e14ctx e14policies ctx policies economy move
      budgetData statusPolicy claimRef record

def DutyCycleMismatchHolds
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies) : Prop :=
  ∃ record : OfflineReclosureStatusRecord ChallengeClass,
    OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = OfflineReclosureStatus.duty_cycle_mismatch ∧
    DutyCycleMismatchCase S e14ctx e14policies ctx policies economy move
      budgetData statusPolicy claimRef record

def SkippedOfflineCascadeHolds
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies) : Prop :=
  ∃ record : OfflineReclosureStatusRecord ChallengeClass,
    OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = OfflineReclosureStatus.skipped_offline_cascade ∧
    SkippedOfflineCascadeCase S e14ctx e14policies ctx policies economy move
      budgetData statusPolicy claimRef record

def AlternationRequiredHolds
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies) : Prop :=
  ∃ record : OfflineReclosureStatusRecord ChallengeClass,
    OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = OfflineReclosureStatus.alternation_required ∧
    AlternationRequiredCase S e14ctx e14policies ctx policies economy move
      budgetData statusPolicy claimRef record

def OnlineSufficientHolds
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies) : Prop :=
  ∃ record : OfflineReclosureStatusRecord ChallengeClass,
    OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = OfflineReclosureStatus.online_sufficient ∧
    OnlineSufficientCase S e14ctx e14policies ctx policies economy move budgetData
      statusPolicy claimRef record

def OfflineOptionalHolds
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies) : Prop :=
  ∃ record : OfflineReclosureStatusRecord ChallengeClass,
    OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = OfflineReclosureStatus.offline_optional ∧
    OfflineOptionalCase S e14ctx e14policies ctx policies economy move budgetData
      statusPolicy claimRef record

def OfflineReclosureRejectedHolds
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies) : Prop :=
  ∃ record : OfflineReclosureStatusRecord ChallengeClass,
    OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = OfflineReclosureStatus.offline_reclosure_rejected ∧
    OfflineReclosureRejectedCase S e14ctx e14policies ctx policies economy move
      budgetData statusPolicy claimRef record

structure CompleteOfflineReclosureStatus
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies) where
  branchValid :
    DeficitOnlineCounterexampleHolds S e14ctx e14policies ctx policies economy
        move budgetData statusPolicy claimRef ∨
      DecorativeOfflineHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef ∨
      DutyCycleMismatchHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef ∨
      SkippedOfflineCascadeHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef ∨
      AlternationRequiredHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef ∨
      OnlineSufficientHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef ∨
      OfflineOptionalHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef ∨
      OfflineReclosureRejectedHolds S e14ctx e14policies ctx policies economy
        move budgetData statusPolicy claimRef
  statusUnique :
    ∀ record1 record2 : OfflineReclosureStatusRecord ChallengeClass,
      OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record1 ->
      OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record2 ->
      record1.status = record2.status

structure DeficitNecessityFalsifier
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass)) where
  claimRef : OfflineReclosureClaimRef S policies
  counterexample :
    DeficitOnlineCounterexampleEvidenceFor S e14ctx e14policies ctx policies
      economy move budgetData claimRef
  complete : CompleteOfflineReclosureStatus S e14ctx e14policies ctx policies
    economy move budgetData statusPolicy claimRef

structure DecorativeOfflineFalsifier
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass)) where
  claimRef : OfflineReclosureClaimRef S policies
  decorative : DecorativeOfflineEvidenceFor S e14ctx e14policies ctx policies
    economy move budgetData claimRef
  complete : CompleteOfflineReclosureStatus S e14ctx e14policies ctx policies
    economy move budgetData statusPolicy claimRef

structure DutyCycleFalsifier
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass)) where
  claimRef : OfflineReclosureClaimRef S policies
  mismatch : DutyCycleMismatchEvidenceFor S e14ctx e14policies ctx policies
    economy move budgetData claimRef
  complete : CompleteOfflineReclosureStatus S e14ctx e14policies ctx policies
    economy move budgetData statusPolicy claimRef

end StatusApparatus

namespace E15

def ExactlyOne : List Prop -> Prop
  | p1 :: p2 :: p3 :: p4 :: p5 :: p6 :: p7 :: p8 :: [] =>
      (p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p7 ∧ ¬ p8) ∨
      (p2 ∧ ¬ p1 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p7 ∧ ¬ p8) ∨
      (p3 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p7 ∧ ¬ p8) ∨
      (p4 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p7 ∧ ¬ p8) ∨
      (p5 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p6 ∧ ¬ p7 ∧ ¬ p8) ∨
      (p6 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p7 ∧ ¬ p8) ∨
      (p7 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p8) ∨
      (p8 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p7)
  | _ => False

end E15

section Theorems

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)

variable {X : Type z} {RecordValue : Type z'} {Q : Type z''}
variable {TransportedValue : Type z'''} {FOut : Type z''''}
variable {Readout : Type z'''''}
variable {RouteResiduePayload : Type z''''''}
variable {Probe : Type z'''''''} {XiFamily : Type z''''''''}
variable {ChallengeClass : Type z'''''''''}
variable {e yDim xiDim : Nat}

theorem E15_OfflineReclosureStatus
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (complete : CompleteOfflineReclosureStatus S e14ctx e14policies ctx policies
      economy move budgetData statusPolicy claimRef) :
    E15.ExactlyOne
      [DeficitOnlineCounterexampleHolds S e14ctx e14policies ctx policies economy
          move budgetData statusPolicy claimRef,
       DecorativeOfflineHolds S e14ctx e14policies ctx policies economy move
          budgetData statusPolicy claimRef,
       DutyCycleMismatchHolds S e14ctx e14policies ctx policies economy move
          budgetData statusPolicy claimRef,
       SkippedOfflineCascadeHolds S e14ctx e14policies ctx policies economy move
          budgetData statusPolicy claimRef,
       AlternationRequiredHolds S e14ctx e14policies ctx policies economy move
          budgetData statusPolicy claimRef,
       OnlineSufficientHolds S e14ctx e14policies ctx policies economy move
          budgetData statusPolicy claimRef,
       OfflineOptionalHolds S e14ctx e14policies ctx policies economy move
          budgetData statusPolicy claimRef,
       OfflineReclosureRejectedHolds S e14ctx e14policies ctx policies economy
          move budgetData statusPolicy claimRef] := by
  have hConflict :
      ∀ {record1 record2 : OfflineReclosureStatusRecord ChallengeClass}
        {status1 status2 : OfflineReclosureStatus},
        OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record1 ->
        OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record2 ->
        record1.status = status1 ->
        record2.status = status2 ->
        status1 ≠ status2 -> False := by
    intro record1 record2 status1 status2 hOcc1 hOcc2 hStatus1 hStatus2 hNe
    have hEq := complete.statusUnique record1 record2 hOcc1 hOcc2
    rw [hStatus1, hStatus2] at hEq
    exact hNe hEq
  simp only [E15.ExactlyOne]
  rcases complete.branchValid with
    hCounterexample | hDecorative | hMismatch | hCascade | hAlternation |
      hOnline | hOptional | hRejected
  · rcases hCounterexample with ⟨record, hOccurrence, hStatus, hCase⟩
    refine Or.inl ⟨⟨record, hOccurrence, hStatus, hCase⟩, ?_, ?_, ?_, ?_, ?_,
      ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩ <;>
      exact hConflict hOccurrence hOtherOccurrence hStatus hOtherStatus (by decide)
  · rcases hDecorative with ⟨record, hOccurrence, hStatus, hCase⟩
    refine Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hStatus, hCase⟩, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩ <;>
      exact hConflict hOccurrence hOtherOccurrence hStatus hOtherStatus (by decide)
  · rcases hMismatch with ⟨record, hOccurrence, hStatus, hCase⟩
    refine Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hStatus, hCase⟩, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩ <;>
      exact hConflict hOccurrence hOtherOccurrence hStatus hOtherStatus (by decide)
  · rcases hCascade with ⟨record, hOccurrence, hStatus, hCase⟩
    refine Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hStatus, hCase⟩, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩ <;>
      exact hConflict hOccurrence hOtherOccurrence hStatus hOtherStatus (by decide)
  · rcases hAlternation with ⟨record, hOccurrence, hStatus, hCase⟩
    refine Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hStatus, hCase⟩, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩ <;>
      exact hConflict hOccurrence hOtherOccurrence hStatus hOtherStatus (by decide)
  · rcases hOnline with ⟨record, hOccurrence, hStatus, hCase⟩
    refine Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hStatus, hCase⟩, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩ <;>
      exact hConflict hOccurrence hOtherOccurrence hStatus hOtherStatus (by decide)
  · rcases hOptional with ⟨record, hOccurrence, hStatus, hCase⟩
    refine Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hStatus, hCase⟩, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩ <;>
      exact hConflict hOccurrence hOtherOccurrence hStatus hOtherStatus (by decide)
  · rcases hRejected with ⟨record, hOccurrence, hStatus, hCase⟩
    refine Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <|
      Or.inr
      ⟨⟨record, hOccurrence, hStatus, hCase⟩, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩ <;>
      exact hConflict hOccurrence hOtherOccurrence hStatus hOtherStatus (by decide)

theorem E15_DeficitAlternation
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (record : OfflineReclosureStatusRecord ChallengeClass)
    (hOccurrence :
      OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record)
    (hStatus : record.status = OfflineReclosureStatus.alternation_required)
    (hCase : AlternationRequiredCase S e14ctx e14policies ctx policies economy
      move budgetData statusPolicy claimRef record) :
    AlternationRequiredHolds S e14ctx e14policies ctx policies economy move
      budgetData statusPolicy claimRef := by
  exact ⟨record, hOccurrence, hStatus, hCase⟩

theorem E15_OfflineCapacityExactlyFreed
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (allocation : SharedBudgetAllocationRecord ChallengeClass)
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation) :
    kappaOff S geometry = kappaOn S geometry + freedAllocation S geometry ∧
      kappaOn S geometry < kappaOff S geometry := by
  constructor
  · exact geometry.offlineInternalIsReallocation
  · change allocation.onlineInternalDischargeAllocation <
      allocation.offlineInternalDischargeAllocation
    rw [geometry.offlineInternalIsReallocation]
    rw [Rat.lt_iff_sub_pos]
    simpa [Rat.sub_eq_add_neg, Rat.add_assoc, Rat.add_comm, Rat.add_left_comm,
      Rat.add_neg_cancel, Rat.add_zero]
      using geometry.onlineExternalPositive

theorem E15_OnlineSufficientNoOfflineRequired
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (complete : CompleteOfflineReclosureStatus S e14ctx e14policies ctx policies
      economy move budgetData statusPolicy claimRef)
    (record : OfflineReclosureStatusRecord ChallengeClass)
    (hOccurrence :
      OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record)
    (hStatus : record.status = OfflineReclosureStatus.online_sufficient)
    (hCase : OnlineSufficientCase S e14ctx e14policies ctx policies economy move
      budgetData statusPolicy claimRef record) :
    OnlineSufficientHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef ∧
      ¬ AlternationRequiredHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef := by
  refine ⟨⟨record, hOccurrence, hStatus, hCase⟩, ?_⟩
  rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩
  have hSameStatus :=
    complete.statusUnique record other hOccurrence hOtherOccurrence
  rw [hStatus, hOtherStatus] at hSameStatus
  cases hSameStatus

theorem E15_OfflinePermittedOutsideDeficit
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (record : OfflineReclosureStatusRecord ChallengeClass)
    (hOccurrence :
      OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record)
    (hStatus : record.status = OfflineReclosureStatus.offline_optional)
    (hCase : OfflineOptionalCase S e14ctx e14policies ctx policies economy move
      budgetData statusPolicy claimRef record) :
    OfflineOptionalHolds S e14ctx e14policies ctx policies economy move
      budgetData statusPolicy claimRef := by
  exact ⟨record, hOccurrence, hStatus, hCase⟩

theorem E15_SkippedOfflineCascade
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (record : OfflineReclosureStatusRecord ChallengeClass)
    (hOccurrence :
      OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record)
    (hStatus : record.status = OfflineReclosureStatus.skipped_offline_cascade)
    (hCase : SkippedOfflineCascadeCase S e14ctx e14policies ctx policies economy
      move budgetData statusPolicy claimRef record) :
    SkippedOfflineCascadeHolds S e14ctx e14policies ctx policies economy move
      budgetData statusPolicy claimRef := by
  exact ⟨record, hOccurrence, hStatus, hCase⟩

theorem E15_DecorativeOfflineFalsifier
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (complete : CompleteOfflineReclosureStatus S e14ctx e14policies ctx policies
      economy move budgetData statusPolicy claimRef)
    (record : OfflineReclosureStatusRecord ChallengeClass)
    (hOccurrence :
      OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record)
    (hStatus : record.status = OfflineReclosureStatus.decorative_offline)
    (hCase : DecorativeOfflineCase S e14ctx e14policies ctx policies economy move
      budgetData statusPolicy claimRef record) :
    DecorativeOfflineHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef ∧
      ¬ AlternationRequiredHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef := by
  refine ⟨⟨record, hOccurrence, hStatus, hCase⟩, ?_⟩
  rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩
  have hSameStatus :=
    complete.statusUnique record other hOccurrence hOtherOccurrence
  rw [hStatus, hOtherStatus] at hSameStatus
  cases hSameStatus

theorem E15_DutyCycleMismatchFalsifier
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (complete : CompleteOfflineReclosureStatus S e14ctx e14policies ctx policies
      economy move budgetData statusPolicy claimRef)
    (record : OfflineReclosureStatusRecord ChallengeClass)
    (hOccurrence :
      OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record)
    (hStatus : record.status = OfflineReclosureStatus.duty_cycle_mismatch)
    (hCase : DutyCycleMismatchCase S e14ctx e14policies ctx policies economy move
      budgetData statusPolicy claimRef record) :
    DutyCycleMismatchHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef ∧
      ¬ AlternationRequiredHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef := by
  refine ⟨⟨record, hOccurrence, hStatus, hCase⟩, ?_⟩
  rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩
  have hSameStatus :=
    complete.statusUnique record other hOccurrence hOtherOccurrence
  rw [hStatus, hOtherStatus] at hSameStatus
  cases hSameStatus

theorem E15_DeficitOnlineFalsifiesNecessity
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (complete : CompleteOfflineReclosureStatus S e14ctx e14policies ctx policies
      economy move budgetData statusPolicy claimRef)
    (record : OfflineReclosureStatusRecord ChallengeClass)
    (hOccurrence :
      OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef record)
    (hStatus :
      record.status = OfflineReclosureStatus.deficit_online_counterexample)
    (hCase : DeficitOnlineCounterexampleCase S e14ctx e14policies ctx policies
      economy move budgetData statusPolicy claimRef record) :
    DeficitOnlineCounterexampleHolds S e14ctx e14policies ctx policies economy
        move budgetData statusPolicy claimRef ∧
      ¬ AlternationRequiredHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef := by
  refine ⟨⟨record, hOccurrence, hStatus, hCase⟩, ?_⟩
  rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩
  have hSameStatus :=
    complete.statusUnique record other hOccurrence hOtherOccurrence
  rw [hStatus, hOtherStatus] at hSameStatus
  cases hSameStatus

theorem E15_DeficitCounterexampleExcludesLowerPriority
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (statusPolicy :
      CarriedRecordPolicy S.T (OfflineReclosureStatusRecord ChallengeClass))
    (claimRef : OfflineReclosureClaimRef S policies)
    (counterexample : DeficitOnlineCounterexampleEvidenceFor S e14ctx
      e14policies ctx policies economy move budgetData claimRef)
    (complete : CompleteOfflineReclosureStatus S e14ctx e14policies ctx policies
      economy move budgetData statusPolicy claimRef) :
    ¬ DecorativeOfflineHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef ∧
      ¬ DutyCycleMismatchHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef ∧
      ¬ SkippedOfflineCascadeHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef ∧
      ¬ AlternationRequiredHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef ∧
      ¬ OnlineSufficientHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef ∧
      ¬ OfflineOptionalHolds S e14ctx e14policies ctx policies economy move
        budgetData statusPolicy claimRef ∧
      ¬ OfflineReclosureRejectedHolds S e14ctx e14policies ctx policies economy
        move budgetData statusPolicy claimRef := by
  have hTop : DeficitOnlineCounterexampleHolds S e14ctx e14policies ctx policies
      economy move budgetData statusPolicy claimRef := by
    rcases complete.branchValid with
      hCounterexample | hDecorative | hMismatch | hCascade | hAlternation |
        hOnline | hOptional | hRejected
    · exact hCounterexample
    · rcases hDecorative with ⟨_record, _hOccurrence, _hStatus, hCase⟩
      exact (hCase.2.1 counterexample).elim
    · rcases hMismatch with ⟨_record, _hOccurrence, _hStatus, hCase⟩
      exact (hCase.2.1 counterexample).elim
    · rcases hCascade with ⟨_record, _hOccurrence, _hStatus, hCase⟩
      exact (hCase.2.1 counterexample).elim
    · rcases hAlternation with ⟨_record, _hOccurrence, _hStatus, hCase⟩
      exact (hCase.2.1 counterexample).elim
    · rcases hOnline with ⟨_record, _hOccurrence, _hStatus, hCase⟩
      exact (hCase.2.1 counterexample).elim
    · rcases hOptional with ⟨_record, _hOccurrence, _hStatus, hCase⟩
      exact (hCase.2.1 counterexample).elim
    · rcases hRejected with ⟨_record, _hOccurrence, _hStatus, hCase⟩
      exact (hCase.2.1 counterexample).elim
  rcases hTop with ⟨topRecord, hTopOccurrence, hTopStatus, _hTopCase⟩
  have hExclude :
      ∀ {other : OfflineReclosureStatusRecord ChallengeClass}
        {otherStatus : OfflineReclosureStatus},
        OfflineReclosureStatusOccurrenceFor S statusPolicy claimRef other ->
        other.status = otherStatus ->
        OfflineReclosureStatus.deficit_online_counterexample ≠ otherStatus ->
        False := by
    intro other otherStatus hOtherOccurrence hOtherStatus hDifferent
    have hSameStatus :=
      complete.statusUnique topRecord other hTopOccurrence hOtherOccurrence
    rw [hTopStatus, hOtherStatus] at hSameStatus
    exact hDifferent hSameStatus
  constructor
  · rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩
    exact hExclude hOtherOccurrence hOtherStatus (by decide)
  constructor
  · rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩
    exact hExclude hOtherOccurrence hOtherStatus (by decide)
  constructor
  · rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩
    exact hExclude hOtherOccurrence hOtherStatus (by decide)
  constructor
  · rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩
    exact hExclude hOtherOccurrence hOtherStatus (by decide)
  constructor
  · rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩
    exact hExclude hOtherOccurrence hOtherStatus (by decide)
  constructor
  · rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩
    exact hExclude hOtherOccurrence hOtherStatus (by decide)
  · rintro ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩
    exact hExclude hOtherOccurrence hOtherStatus (by decide)

theorem E15_OffInventoryFlowCannotCertifyOffline
    (e14ctx : ReconsolidationClassifierContext S X RecordValue Q
      TransportedValue FOut Readout)
    (e14policies : ReconsolidationEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout)
    (ctx : OfflineReclosureClassifierContext S X RecordValue Q TransportedValue
      FOut Readout RouteResiduePayload ChallengeClass e yDim xiDim)
    (policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass e yDim
      xiDim)
    (scope : ClosureDebtScopeRecord ChallengeClass)
    (economy : ProbeEconomy S Probe XiFamily) (move : ProbeMove Probe XiFamily)
    (budgetData : ExposureBudgetWitness economy move)
    (allocation : SharedBudgetAllocationRecord ChallengeClass)
    (geometry : DerivedOfflineBudgetGeometry S policies scope economy move
      budgetData allocation)
    (schedule : DeclaredOperatingSchedule ChallengeClass)
    (flowInventory :
      CompletePhaseFlowInventory S e14ctx e14policies ctx policies schedule)
    (exchangeInventory :
      CompleteExternalExchangeInventory S policies schedule)
    (flowRecord : ClosureDebtFlowRecord ChallengeClass X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload LedgerEntry e yDim xiDim)
    (offInventory : flowRecord ∉ flowInventory.flows) :
    (¬ ∃ witness : GenuineOfflinePhaseEvidence S e14ctx e14policies ctx policies
        scope economy move budgetData allocation geometry schedule flowInventory
        exchangeInventory,
      witness.flowRecord = flowRecord) ∧
    (¬ ∃ witness : DecorativeOfflineEvidence S e14ctx e14policies ctx policies
        scope economy move budgetData allocation geometry schedule flowInventory
        exchangeInventory,
      witness.flowRecord = flowRecord) := by
  constructor
  · rintro ⟨witness, hLinked⟩
    apply offInventory
    simpa [hLinked] using witness.flowMember
  · rintro ⟨witness, hLinked⟩
    apply offInventory
    simpa [hLinked] using witness.flowMember

end Theorems

end SixBirdsFoundationsV
