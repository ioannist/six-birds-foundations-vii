import SixBirdsFoundationsV.Definitional.ESystem
import SixBirdsFoundationsV.Definitional.ProbeEconomy
import SixBirdsFoundationsV.Laws.E6E9PricedAccess
import SixBirdsFoundationsV.Laws.E15OfflineReclosure
import HolonomyMemory.Asymmetry
import HolonomyMemory.Witnesses

open HolonomyMemory

universe u v w x y y' y'' y''' y'''' y'''''
universe z z' z'' z''' z'''' z''''' z'''''' z''''''' z'''''''' z'''''''''

namespace SixBirdsFoundationsV

section

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}

variable
  (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
    InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)

variable {Support : Type z} {ChallengeClass : Type z'}
variable {Probe : Type z''} {XiFamily : Type z'''}
variable {RouteResiduePayload : Type z''''}
variable {X : Type z'''''} {RecordValue : Type z''''''}
variable {Q : Type z'''''''} {TransportedValue : Type z''''''''}
variable {FOut : Type z'''''''''} {Readout : Type z''''''''''}
variable {e yDim xiDim : Nat}

/-! D3 carriedness used by every E16 record family. -/

def E16Carried
    {Record : Type z} (policy : CarriedRecordPolicy S.T Record)
    (record : Record) : Prop :=
  ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
    ∃ generatedByS : Bool, ∃ inScope : Bool,
      CarriedRecordAt policy record n0 sourceTag generatedByS inScope ∧
      CarriedSource sourceTag generatedByS inScope

/-! Fixed-support route package over the vendored Holonomy core. -/

structure DeclaredComparisonBaseRecord (Support : Type u) where
  baseId : Nat
  support : Support
  declaredAt : Rat
  deriving Repr

structure DeclaredRouteTransportPackage (Support : Type u) where
  packageId : Nat
  comparisonBase : DeclaredComparisonBaseRecord Support
  core : RouteTransportCore

structure RoutePairRecord
    {Support : Type u}
    (package : DeclaredRouteTransportPackage Support) where
  routePairId : Nat
  sourceInterface : package.core.Interface
  targetInterface : package.core.Interface
  sourceHistory : package.core.History sourceInterface
  gamma : package.core.Continuation sourceInterface targetInterface
  eta : package.core.Continuation sourceInterface targetInterface
  gammaEndpoint : package.core.History targetInterface
  etaEndpoint : package.core.History targetInterface
  gammaEndpointLinked :
    gammaEndpoint = package.core.push sourceHistory gamma
  etaEndpointLinked :
    etaEndpoint = package.core.push sourceHistory eta

structure CarriedRoutePair
    {Support : Type z}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    (packagePolicy :
      CarriedRecordPolicy S.T (DeclaredRouteTransportPackage Support))
    (basePolicy :
      CarriedRecordPolicy S.T (DeclaredComparisonBaseRecord Support)) where
  package : DeclaredRouteTransportPackage Support
  pair : RoutePairRecord package
  pairPolicy : CarriedRecordPolicy S.T (RoutePairRecord package)
  packageCarried : E16Carried S packagePolicy package
  baseCarried : E16Carried S basePolicy package.comparisonBase
  pairCarried : E16Carried S pairPolicy pair

structure SameCurrentRouteEndpoints
    {Support : Type u}
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package) where
  currentEquivalent :
    CurrentEventEquiv package.core pair.gammaEndpoint pair.etaEndpoint
  quotientEqual :
    (Quotient.mk (CurrentSetoid package.core pair.targetInterface)
      pair.gammaEndpoint : CurrentQuotient package.core pair.targetInterface) =
    Quotient.mk (CurrentSetoid package.core pair.targetInterface)
      pair.etaEndpoint

structure RoutePredictiveWitness
    {Support : Type u}
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package) where
  witness : PredictiveWitness package.core pair.targetInterface
  leftLinked : witness.h = pair.gammaEndpoint
  rightLinked : witness.h' = pair.etaEndpoint

structure LoopAnchoredRouteAsymmetry
    {Support : Type u}
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package) where
  loop : Loop package.core pair.sourceInterface
  gammaIsLoop : pair.targetInterface = pair.sourceInterface
  gammaLinked : HEq pair.gamma loop
  etaIsIdentity :
    HEq pair.eta (package.core.idCont (i := pair.sourceInterface))
  asymmetry : LoopAsymmetry package.core pair.sourceInterface loop

/-! Declared held-out challenges and ledger-backed repair trials. -/

structure HeldOutChallengeFamily (ChallengeClass : Type u) where
  familyId : Nat
  classes : List ChallengeClass
  classesNodup : classes.Nodup
  nonempty : classes ≠ []
  declaredAt : Rat

structure RepairCapacityProtocolRecord (ChallengeClass : Type u) where
  protocolId : Nat
  challengeFamily : HeldOutChallengeFamily ChallengeClass
  measuredAt : Rat

structure RepairDischargeProbabilityRecord
    (LedgerEntry : Type u) (ChallengeClass : Type v) where
  probabilityRecordId : Nat
  challengeClass : ChallengeClass
  probability : Rat
  probabilityNonnegative : 0 ≤ probability
  probabilityAtMostOne : probability ≤ 1
  supportingLedgerEntries : List LedgerEntry
  supportingLedgerEntriesNodup : supportingLedgerEntries.Nodup
  measuredAt : Rat

structure RepairDischargeTrialRecord
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    (ChallengeClass : Type z) where
  trialId : Nat
  challengeClass : ChallengeClass
  startState : S.T.Z
  endState : S.T.Z
  defectRecord : DefectRecord
  auditRecord : AuditRecord
  dischargeEntry : LedgerEntry
  ledgerBefore : List LedgerEntry
  ledgerAfter : List LedgerEntry
  dischargeEntryAbsentBefore : dischargeEntry ∉ ledgerBefore
  dischargeEntryPresentAfter : dischargeEntry ∈ ledgerAfter
  observedAt : Rat
  lawfulRepair : S.RepairStep startState endState defectRecord auditRecord

abbrev TrialEligibleForRouteEndpoint
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    (ChallengeClass : Type z) :=
  ∀ {core : RouteTransportCore} {interface : core.Interface},
    RepairDischargeTrialRecord S ChallengeClass → core.History interface → Prop

structure CompleteRepairDischargeTrialInventory
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    (ChallengeClass : Type z)
    (trialPolicy :
      CarriedRecordPolicy S.T (RepairDischargeTrialRecord S ChallengeClass))
    (EligibleTrial : RepairDischargeTrialRecord S ChallengeClass → Prop) where
  trials : List (RepairDischargeTrialRecord S ChallengeClass)
  trialsNodup : trials.Nodup
  trialIdsNodup : (trials.map (fun trial => trial.trialId)).Nodup
  everyEligibleTrialCovered :
    ∀ trial, EligibleTrial trial → trial ∈ trials
  everyTrialEligible :
    ∀ trial, trial ∈ trials → EligibleTrial trial
  everyTrialCarried :
    ∀ trial, trial ∈ trials → E16Carried S trialPolicy trial
  singleValuedPerTrialId :
    ∀ trial1 trial2, trial1 ∈ trials → trial2 ∈ trials →
      trial1.trialId = trial2.trialId → trial1 = trial2

structure RouteRepairCapacityDistribution
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    {Support : Type z} (ChallengeClass : Type z')
    (trialEligibleForRouteEndpoint : TrialEligibleForRouteEndpoint S ChallengeClass)
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package) where
  distributionId : Nat
  routeEndpoint : package.core.History pair.targetInterface
  protocol : RepairCapacityProtocolRecord ChallengeClass
  trialPolicy :
    CarriedRecordPolicy S.T (RepairDischargeTrialRecord S ChallengeClass)
  records : List (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass)
  trialInventory :
    CompleteRepairDischargeTrialInventory S ChallengeClass trialPolicy
      (fun trial => trialEligibleForRouteEndpoint trial routeEndpoint)
  recordsNodup : records.Nodup
  recordIdsNodup : (records.map (fun record => record.probabilityRecordId)).Nodup
  everyClassCovered :
    ∀ C, C ∈ protocol.challengeFamily.classes →
      ∃ record, record ∈ records ∧ record.challengeClass = C
  everyRecordDeclared :
    ∀ record, record ∈ records →
      record.challengeClass ∈ protocol.challengeFamily.classes
  singleValuedPerClass :
    ∀ record1 record2, record1 ∈ records → record2 ∈ records →
      record1.challengeClass = record2.challengeClass → record1 = record2

/-!
Continuation endpoints no longer share the route pair's source history.  This
parallel distribution is therefore indexed directly by one history endpoint.
-/

structure EndpointRepairCapacityDistribution
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    (ChallengeClass : Type z)
    (trialEligibleForRouteEndpoint : TrialEligibleForRouteEndpoint S ChallengeClass)
    (core : RouteTransportCore)
    (interface : core.Interface) where
  distributionId : Nat
  routeEndpoint : core.History interface
  protocol : RepairCapacityProtocolRecord ChallengeClass
  trialPolicy :
    CarriedRecordPolicy S.T (RepairDischargeTrialRecord S ChallengeClass)
  records : List (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass)
  trialInventory :
    CompleteRepairDischargeTrialInventory S ChallengeClass trialPolicy
      (fun trial => trialEligibleForRouteEndpoint trial routeEndpoint)
  recordsNodup : records.Nodup
  recordIdsNodup : (records.map (fun record => record.probabilityRecordId)).Nodup
  everyClassCovered :
    ∀ C, C ∈ protocol.challengeFamily.classes →
      ∃ record, record ∈ records ∧ record.challengeClass = C
  everyRecordDeclared :
    ∀ record, record ∈ records →
      record.challengeClass ∈ protocol.challengeFamily.classes
  singleValuedPerClass :
    ∀ record1 record2, record1 ∈ records → record2 ∈ records →
      record1.challengeClass = record2.challengeClass → record1 = record2

/-!
The accepted pseudocode gives one shared context, but that context mentions
counterparts which themselves contain context-indexed distributions.  This
core breaks that declaration cycle without changing any documented check.
-/

structure AdaptabilityCoreContext
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    (Support : Type z) (ChallengeClass : Type z')
    (Probe : Type z'') (XiFamily : Type z''') where
  routePackageDeclared : DeclaredRouteTransportPackage Support → Prop
  routePairAdmissible :
    (package : DeclaredRouteTransportPackage Support) →
      RoutePairRecord package → Prop
  trialEligibleForRouteEndpoint : TrialEligibleForRouteEndpoint S ChallengeClass
  trialLedgerEffectRecordsDischarge :
    RepairDischargeTrialRecord S ChallengeClass → Prop
  probabilityComputedFromRepairLedger :
    (package : DeclaredRouteTransportPackage Support) →
      (pair : RoutePairRecord package) →
      (distribution :
        RouteRepairCapacityDistribution S ChallengeClass
          trialEligibleForRouteEndpoint package pair) →
      (protocol : RepairCapacityProtocolRecord ChallengeClass) →
      (routeEndpoint : package.core.History pair.targetInterface) →
      CompleteRepairDischargeTrialInventory S ChallengeClass
        distribution.trialPolicy
          (fun trial => trialEligibleForRouteEndpoint trial distribution.routeEndpoint) →
      RepairDischargeProbabilityRecord LedgerEntry ChallengeClass → Prop
  endpointProbabilityComputedFromRepairLedger :
    ∀ {core : RouteTransportCore} {interface : core.Interface},
      (distribution :
        EndpointRepairCapacityDistribution S ChallengeClass
          trialEligibleForRouteEndpoint core interface) →
      (protocol : RepairCapacityProtocolRecord ChallengeClass) →
      (routeEndpoint : core.History interface) →
      CompleteRepairDischargeTrialInventory S ChallengeClass
        distribution.trialPolicy
          (fun trial => trialEligibleForRouteEndpoint trial distribution.routeEndpoint) →
      RepairDischargeProbabilityRecord LedgerEntry ChallengeClass → Prop
  supportingLedgerEntryRelevant :
    RepairDischargeProbabilityRecord LedgerEntry ChallengeClass →
      LedgerEntry → Prop
  protocolUsesBindingBudget :
    RepairCapacityProtocolRecord ChallengeClass →
      (economy : ProbeEconomy S Probe XiFamily) →
      (move : ProbeMove Probe XiFamily) →
      ExposureBudgetWitness economy move → Prop

noncomputable def eligibleTrials
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (distribution : RouteRepairCapacityDistribution S ChallengeClass
      ctx.trialEligibleForRouteEndpoint package pair)
    (challengeClass : ChallengeClass) :
    List (RepairDischargeTrialRecord S ChallengeClass) := by
  classical
  exact distribution.trialInventory.trials.filter
    (fun trial => trial.challengeClass = challengeClass)

noncomputable def successfulEligibleTrials
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (distribution : RouteRepairCapacityDistribution S ChallengeClass
      ctx.trialEligibleForRouteEndpoint package pair)
    (challengeClass : ChallengeClass) :
    List (RepairDischargeTrialRecord S ChallengeClass) := by
  classical
  exact (eligibleTrials S ctx distribution challengeClass).filter
    ctx.trialLedgerEffectRecordsDischarge

noncomputable def eligibleTrialCount
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (distribution : RouteRepairCapacityDistribution S ChallengeClass
      ctx.trialEligibleForRouteEndpoint package pair)
    (challengeClass : ChallengeClass) : Nat :=
  (eligibleTrials S ctx distribution challengeClass).length

noncomputable def successfulEligibleCount
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (distribution : RouteRepairCapacityDistribution S ChallengeClass
      ctx.trialEligibleForRouteEndpoint package pair)
    (challengeClass : ChallengeClass) : Nat :=
  (successfulEligibleTrials S ctx distribution challengeClass).length

noncomputable def endpointEligibleTrials
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (distribution : EndpointRepairCapacityDistribution S ChallengeClass
      ctx.trialEligibleForRouteEndpoint core interface)
    (challengeClass : ChallengeClass) :
    List (RepairDischargeTrialRecord S ChallengeClass) := by
  classical
  exact distribution.trialInventory.trials.filter
    (fun trial => trial.challengeClass = challengeClass)

noncomputable def endpointSuccessfulEligibleTrials
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (distribution : EndpointRepairCapacityDistribution S ChallengeClass
      ctx.trialEligibleForRouteEndpoint core interface)
    (challengeClass : ChallengeClass) :
    List (RepairDischargeTrialRecord S ChallengeClass) := by
  classical
  exact (endpointEligibleTrials S ctx distribution challengeClass).filter
    ctx.trialLedgerEffectRecordsDischarge

noncomputable def endpointEligibleTrialCount
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (distribution : EndpointRepairCapacityDistribution S ChallengeClass
      ctx.trialEligibleForRouteEndpoint core interface)
    (challengeClass : ChallengeClass) : Nat :=
  (endpointEligibleTrials S ctx distribution challengeClass).length

noncomputable def endpointSuccessfulEligibleCount
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (distribution : EndpointRepairCapacityDistribution S ChallengeClass
      ctx.trialEligibleForRouteEndpoint core interface)
    (challengeClass : ChallengeClass) : Nat :=
  (endpointSuccessfulEligibleTrials S ctx distribution challengeClass).length

structure CompleteRouteRepairCapacityDistribution
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package)
    (distribution :
      RouteRepairCapacityDistribution S ChallengeClass
        ctx.trialEligibleForRouteEndpoint package pair)
    (distributionPolicy : CarriedRecordPolicy S.T
      (RouteRepairCapacityDistribution S ChallengeClass
        ctx.trialEligibleForRouteEndpoint package pair))
    (probabilityPolicy : CarriedRecordPolicy S.T
      (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass)) where
  distributionCarried : E16Carried S distributionPolicy distribution
  everyRecordCarried :
    ∀ record, record ∈ distribution.records →
      E16Carried S probabilityPolicy record
  everyTrialCarried :
    ∀ trial, trial ∈ distribution.trialInventory.trials →
      E16Carried S distribution.trialPolicy trial
  everyLedgerEntryCarried :
    ∀ record, record ∈ distribution.records → ∀ entry,
      entry ∈ record.supportingLedgerEntries →
        entry ∈ S.Lambda_S.ledgerEntries ∧
        HasCarriedRecordEvidence S.Lambda_S.ledgerPolicy entry
  everyProbabilityComputed :
    ∀ record, record ∈ distribution.records →
      ctx.probabilityComputedFromRepairLedger package pair distribution
        distribution.protocol distribution.routeEndpoint
        distribution.trialInventory record
  everyProbabilityAtProtocolTime :
    ∀ record, record ∈ distribution.records →
      record.measuredAt = distribution.protocol.measuredAt
  everyTrialAtProtocolTime :
    ∀ trial, trial ∈ distribution.trialInventory.trials →
      trial.observedAt = distribution.protocol.measuredAt
  everyProbabilityUsesExactEligibleDenominator :
    ∀ record, record ∈ distribution.records →
      record.probability =
        (successfulEligibleCount S ctx distribution record.challengeClass : Rat) /
          eligibleTrialCount S ctx distribution record.challengeClass
  everyDenominatorPositive :
    ∀ C, C ∈ distribution.protocol.challengeFamily.classes →
      0 < eligibleTrialCount S ctx distribution C

structure CompleteEndpointRepairCapacityDistribution
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (core : RouteTransportCore) (interface : core.Interface)
    (distribution :
      EndpointRepairCapacityDistribution S ChallengeClass
        ctx.trialEligibleForRouteEndpoint core interface)
    (distributionPolicy : CarriedRecordPolicy S.T
      (EndpointRepairCapacityDistribution S ChallengeClass
        ctx.trialEligibleForRouteEndpoint core interface))
    (probabilityPolicy : CarriedRecordPolicy S.T
      (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass)) where
  distributionCarried : E16Carried S distributionPolicy distribution
  everyRecordCarried :
    ∀ record, record ∈ distribution.records →
      E16Carried S probabilityPolicy record
  everyTrialCarried :
    ∀ trial, trial ∈ distribution.trialInventory.trials →
      E16Carried S distribution.trialPolicy trial
  everyLedgerEntryCarried :
    ∀ record, record ∈ distribution.records → ∀ entry,
      entry ∈ record.supportingLedgerEntries →
        entry ∈ S.Lambda_S.ledgerEntries ∧
        HasCarriedRecordEvidence S.Lambda_S.ledgerPolicy entry
  everyProbabilityComputed :
    ∀ record, record ∈ distribution.records →
      ctx.endpointProbabilityComputedFromRepairLedger distribution
        distribution.protocol distribution.routeEndpoint
        distribution.trialInventory record
  everyProbabilityAtProtocolTime :
    ∀ record, record ∈ distribution.records →
      record.measuredAt = distribution.protocol.measuredAt
  everyTrialAtProtocolTime :
    ∀ trial, trial ∈ distribution.trialInventory.trials →
      trial.observedAt = distribution.protocol.measuredAt
  everyProbabilityUsesExactEligibleDenominator :
    ∀ record, record ∈ distribution.records →
      record.probability =
        (endpointSuccessfulEligibleCount S ctx distribution
          record.challengeClass : Rat) /
          endpointEligibleTrialCount S ctx distribution record.challengeClass
  everyDenominatorPositive :
    ∀ C, C ∈ distribution.protocol.challengeFamily.classes →
      0 < endpointEligibleTrialCount S ctx distribution C

theorem E16_SwappedRouteTrialPopulationRejected
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package)
    (left right : RouteRepairCapacityDistribution S ChallengeClass
      ctx.trialEligibleForRouteEndpoint package pair)
    (trial : RepairDischargeTrialRecord S ChallengeClass)
    (hLeft : trial ∈ left.trialInventory.trials)
    (hNotRight : ¬ ctx.trialEligibleForRouteEndpoint trial right.routeEndpoint) :
    ctx.trialEligibleForRouteEndpoint trial left.routeEndpoint ∧
      trial ∉ right.trialInventory.trials := by
  refine ⟨left.trialInventory.everyTrialEligible trial hLeft, ?_⟩
  intro hRight
  exact hNotRight (right.trialInventory.everyTrialEligible trial hRight)

structure RepairCapacityDistributionPair
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package)
    (probabilityPolicy : CarriedRecordPolicy S.T
      (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass)) where
  left : RouteRepairCapacityDistribution S ChallengeClass
    ctx.trialEligibleForRouteEndpoint package pair
  right : RouteRepairCapacityDistribution S ChallengeClass
    ctx.trialEligibleForRouteEndpoint package pair
  distributionPolicy : CarriedRecordPolicy S.T
    (RouteRepairCapacityDistribution S ChallengeClass
      ctx.trialEligibleForRouteEndpoint package pair)
  leftComplete :
    CompleteRouteRepairCapacityDistribution S ctx package pair left
      distributionPolicy probabilityPolicy
  rightComplete :
    CompleteRouteRepairCapacityDistribution S ctx package pair right
      distributionPolicy probabilityPolicy
  sameProtocol : left.protocol = right.protocol
  leftEndpoint : left.routeEndpoint = pair.gammaEndpoint
  rightEndpoint : right.routeEndpoint = pair.etaEndpoint

structure DeclaredRepairCapacityDifference
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package)
    (probabilityPolicy : CarriedRecordPolicy S.T
      (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass)) where
  distributions :
    RepairCapacityDistributionPair S ctx package pair probabilityPolicy
  challengeClass : ChallengeClass
  challengeDeclared :
    challengeClass ∈ distributions.left.protocol.challengeFamily.classes
  leftRecord : RepairDischargeProbabilityRecord LedgerEntry ChallengeClass
  rightRecord : RepairDischargeProbabilityRecord LedgerEntry ChallengeClass
  leftMember : leftRecord ∈ distributions.left.records
  rightMember : rightRecord ∈ distributions.right.records
  leftClassLinked : leftRecord.challengeClass = challengeClass
  rightClassLinked : rightRecord.challengeClass = challengeClass
  probabilitiesDiffer : leftRecord.probability ≠ rightRecord.probability
  leftCarried : E16Carried S probabilityPolicy leftRecord
  rightCarried : E16Carried S probabilityPolicy rightRecord
  leftLedgerComputed :
    ctx.probabilityComputedFromRepairLedger package pair distributions.left
      distributions.left.protocol distributions.left.routeEndpoint
      distributions.left.trialInventory leftRecord
  rightLedgerComputed :
    ctx.probabilityComputedFromRepairLedger package pair distributions.right
      distributions.right.protocol distributions.right.routeEndpoint
      distributions.right.trialInventory rightRecord
  everyLeftEntryCarried :
    ∀ entry, entry ∈ leftRecord.supportingLedgerEntries →
      entry ∈ S.Lambda_S.ledgerEntries ∧
      HasCarriedRecordEvidence S.Lambda_S.ledgerPolicy entry
  everyRightEntryCarried :
    ∀ entry, entry ∈ rightRecord.supportingLedgerEntries →
      entry ∈ S.Lambda_S.ledgerEntries ∧
      HasCarriedRecordEvidence S.Lambda_S.ledgerPolicy entry
  everyLeftEntryRelevant :
    ∀ entry, entry ∈ leftRecord.supportingLedgerEntries →
      ctx.supportingLedgerEntryRelevant leftRecord entry
  everyRightEntryRelevant :
    ∀ entry, entry ∈ rightRecord.supportingLedgerEntries →
      ctx.supportingLedgerEntryRelevant rightRecord entry

structure NoDeclaredRepairCapacityDifference
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package)
    (probabilityPolicy : CarriedRecordPolicy S.T
      (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass))
    (distributions :
      RepairCapacityDistributionPair S ctx package pair probabilityPolicy) where
  everyDeclaredClassEqual :
    ∀ C, C ∈ distributions.left.protocol.challengeFamily.classes →
      ∃ left right,
        left ∈ distributions.left.records ∧
        right ∈ distributions.right.records ∧
        left.challengeClass = C ∧ right.challengeClass = C ∧
        left.probability = right.probability ∧
        E16Carried S probabilityPolicy left ∧
        E16Carried S probabilityPolicy right ∧
        ctx.probabilityComputedFromRepairLedger package pair distributions.left
          distributions.left.protocol distributions.left.routeEndpoint
          distributions.left.trialInventory left ∧
        ctx.probabilityComputedFromRepairLedger package pair distributions.right
          distributions.right.protocol distributions.right.routeEndpoint
          distributions.right.trialInventory right

/-! E15 full-record reconciliation bridge. -/

structure RouteResidueReconciliationBridgeRecord
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (RouteResiduePayload : Type z'''')
    (probabilityPolicy : CarriedRecordPolicy S.T
      (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass)) where
  bridgeId : Nat
  e15Residue : RouteResidueDebtRecord RouteResiduePayload
  e16CandidateId : Nat
  candidatePackage : DeclaredRouteTransportPackage Support
  candidateRoutePair : RoutePairRecord candidatePackage
  candidateCapacityDifference :
    DeclaredRepairCapacityDifference S ctx candidatePackage candidateRoutePair
      probabilityPolicy
  reconciledAt : Rat
  observedAt : Rat
  reconciledBeforeObservation : reconciledAt ≤ observedAt

/-! Claim and raw control-counterpart records. -/

structure AdaptabilityClaimRef
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    (Support : Type z) (ChallengeClass : Type z')
    (Probe : Type z'') (XiFamily : Type z''') where
  candidateId : Nat
  package : DeclaredRouteTransportPackage Support
  routePair : RoutePairRecord package
  protocol : RepairCapacityProtocolRecord ChallengeClass
  economy : ProbeEconomy S Probe XiFamily
  probeMove : ProbeMove Probe XiFamily
  budgetData : ExposureBudgetWitness economy probeMove
  challengeClass : ChallengeClass
  observedAt : Rat

structure ProtocolCounterpartRecord
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (probabilityPolicy : CarriedRecordPolicy S.T
      (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass)) where
  counterpartId : Nat
  candidateId : Nat
  observedAt : Rat
  comparisonBase : DeclaredComparisonBaseRecord Support
  honestPackage : DeclaredRouteTransportPackage Support
  packageBaseLinked : comparisonBase = honestPackage.comparisonBase
  honestPair : RoutePairRecord honestPackage
  honestDifference : Option
    (DeclaredRepairCapacityDifference S ctx honestPackage honestPair
      probabilityPolicy)
  honestDifferenceAtObservation :
    ∀ difference, honestDifference = some difference →
      difference.distributions.left.protocol.measuredAt = observedAt

structure CompletionCounterpartRecord
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (probabilityPolicy : CarriedRecordPolicy S.T
      (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass)) where
  counterpartId : Nat
  candidateId : Nat
  observedAt : Rat
  comparisonBase : DeclaredComparisonBaseRecord Support
  completedPackage : DeclaredRouteTransportPackage Support
  packageBaseLinked : comparisonBase = completedPackage.comparisonBase
  completedPair : RoutePairRecord completedPackage
  completedWitnessCount : Nat
  completedDiscrepancy : Rat

structure RefinementCounterpartRecord
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (probabilityPolicy : CarriedRecordPolicy S.T
      (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass)) where
  counterpartId : Nat
  candidateId : Nat
  observedAt : Rat
  comparisonBase : DeclaredComparisonBaseRecord Support
  refinedPackage : DeclaredRouteTransportPackage Support
  packageBaseLinked : comparisonBase = refinedPackage.comparisonBase
  refinedPair : RoutePairRecord refinedPackage
  refinedWitnessCount : Nat
  refinedDiscrepancy : Rat
  refinedMaxFiber : Nat

structure ContinuedRepairCapacityDifference
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (core : RouteTransportCore) (interface : core.Interface)
    (leftAfter rightAfter : core.History interface)
    (probabilityPolicy : CarriedRecordPolicy S.T
      (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass)) where
  left : EndpointRepairCapacityDistribution S ChallengeClass
    ctx.trialEligibleForRouteEndpoint core interface
  right : EndpointRepairCapacityDistribution S ChallengeClass
    ctx.trialEligibleForRouteEndpoint core interface
  distributionPolicy : CarriedRecordPolicy S.T
    (EndpointRepairCapacityDistribution S ChallengeClass
      ctx.trialEligibleForRouteEndpoint core interface)
  leftComplete : CompleteEndpointRepairCapacityDistribution S ctx core interface
    left distributionPolicy probabilityPolicy
  rightComplete : CompleteEndpointRepairCapacityDistribution S ctx core interface
    right distributionPolicy probabilityPolicy
  sameProtocol : left.protocol = right.protocol
  leftEndpointLinked : left.routeEndpoint = leftAfter
  rightEndpointLinked : right.routeEndpoint = rightAfter
  challengeClass : ChallengeClass
  challengeDeclared : challengeClass ∈ left.protocol.challengeFamily.classes
  leftRecord : RepairDischargeProbabilityRecord LedgerEntry ChallengeClass
  rightRecord : RepairDischargeProbabilityRecord LedgerEntry ChallengeClass
  leftRecordMember : leftRecord ∈ left.records
  rightRecordMember : rightRecord ∈ right.records
  leftClassLinked : leftRecord.challengeClass = challengeClass
  rightClassLinked : rightRecord.challengeClass = challengeClass
  probabilitiesDiffer : leftRecord.probability ≠ rightRecord.probability
  leftCarried : E16Carried S probabilityPolicy leftRecord
  rightCarried : E16Carried S probabilityPolicy rightRecord
  leftLedgerComputed :
    ctx.endpointProbabilityComputedFromRepairLedger left left.protocol
      left.routeEndpoint left.trialInventory leftRecord
  rightLedgerComputed :
    ctx.endpointProbabilityComputedFromRepairLedger right right.protocol
      right.routeEndpoint right.trialInventory rightRecord
  everyLeftEntryCarried :
    ∀ entry, entry ∈ leftRecord.supportingLedgerEntries →
      entry ∈ S.Lambda_S.ledgerEntries ∧
      HasCarriedRecordEvidence S.Lambda_S.ledgerPolicy entry
  everyRightEntryCarried :
    ∀ entry, entry ∈ rightRecord.supportingLedgerEntries →
      entry ∈ S.Lambda_S.ledgerEntries ∧
      HasCarriedRecordEvidence S.Lambda_S.ledgerPolicy entry
  everyLeftEntryRelevant :
    ∀ entry, entry ∈ leftRecord.supportingLedgerEntries →
      ctx.supportingLedgerEntryRelevant leftRecord entry
  everyRightEntryRelevant :
    ∀ entry, entry ∈ rightRecord.supportingLedgerEntries →
      ctx.supportingLedgerEntryRelevant rightRecord entry

structure ContinuationControlRecord
    (ctx : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily)
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package)
    (probabilityPolicy : CarriedRecordPolicy S.T
      (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass)) where
  continuationId : Nat
  candidateId : Nat
  observedAt : Rat
  comparisonBase : DeclaredComparisonBaseRecord Support
  packageBaseLinked : comparisonBase = package.comparisonBase
  target : package.core.Interface
  continuation : package.core.Continuation pair.targetInterface target
  leftAfter : package.core.History target
  rightAfter : package.core.History target
  leftLinked : leftAfter = package.core.push pair.gammaEndpoint continuation
  rightLinked : rightAfter = package.core.push pair.etaEndpoint continuation
  laterDifference : Option
    (ContinuedRepairCapacityDifference S ctx package.core target leftAfter rightAfter
      probabilityPolicy)
  laterDifferenceAtObservation :
    ∀ difference, laterDifference = some difference →
      difference.left.protocol.measuredAt = observedAt ∧
      difference.right.protocol.measuredAt = observedAt

structure DeclaredPerturbationBoundRecord where
  boundId : Nat
  candidateId : Nat
  maximumMagnitude : Rat
  nonnegative : 0 ≤ maximumMagnitude
  declaredAt : Rat

structure PerturbationTrialRecord
    (package : DeclaredRouteTransportPackage Support) where
  trialId : Nat
  candidateId : Nat
  observedAt : Rat
  comparisonBase : DeclaredComparisonBaseRecord Support
  packageBaseLinked : comparisonBase = package.comparisonBase
  perturbedPair : RoutePairRecord package
  perturbationMagnitude : Rat
  magnitudeNonnegative : 0 ≤ perturbationMagnitude

/-! Full shared classifier context after all raw counterpart types exist. -/

structure AdaptabilityClassifierContext
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)
    (Support : Type z) (ChallengeClass : Type z')
    (Probe : Type z'') (XiFamily : Type z''')
    (RouteResiduePayload : Type z'''')
    (probabilityPolicy : CarriedRecordPolicy S.T
      (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass)) where
  core : AdaptabilityCoreContext S Support ChallengeClass Probe XiFamily
  protocolCounterpartAdmissible :
    ProtocolCounterpartRecord S core probabilityPolicy → Prop
  completionCounterpartAdmissible :
    CompletionCounterpartRecord S core probabilityPolicy → Prop
  refinementCounterpartAdmissible :
    RefinementCounterpartRecord S core probabilityPolicy → Prop
  continuationAdmissibleForControl :
    ∀ {package pair},
      ContinuationControlRecord S core package pair probabilityPolicy → Prop
  honestProtocolInternalizationClears :
    ProtocolCounterpartRecord S core probabilityPolicy → Prop
  completionClearsResidue :
    CompletionCounterpartRecord S core probabilityPolicy → Prop
  refinementMakesResidueCurrentVisible :
    RefinementCounterpartRecord S core probabilityPolicy → Prop
  continuationDissipatesResidue :
    ∀ {package pair},
      ContinuationControlRecord S core package pair probabilityPolicy → Prop
  perturbationTrialEligible :
    ∀ {package : DeclaredRouteTransportPackage Support},
      PerturbationTrialRecord package → Prop
  boundedPerturbationPreservesResidue :
    (package : DeclaredRouteTransportPackage Support) →
      PerturbationTrialRecord package → Prop
  e15ResidueReconciledForAdaptability :
    (bridge : RouteResidueReconciliationBridgeRecord S core
      RouteResiduePayload probabilityPolicy) →
    (package : DeclaredRouteTransportPackage Support) →
    (pair : RoutePairRecord package) →
    DeclaredRepairCapacityDifference S core package pair probabilityPolicy → Prop

/-! Claim-indexed control eligibility. -/

def EligibleProtocolCounterpart
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (record : ProtocolCounterpartRecord S ctx.core probabilityPolicy) : Prop :=
  ctx.protocolCounterpartAdmissible record ∧
  record.candidateId = claimRef.candidateId ∧
  record.observedAt = claimRef.observedAt

def EligibleCompletionCounterpart
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (record : CompletionCounterpartRecord S ctx.core probabilityPolicy) : Prop :=
  ctx.completionCounterpartAdmissible record ∧
  record.candidateId = claimRef.candidateId ∧
  record.observedAt = claimRef.observedAt

def EligibleRefinementCounterpart
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (record : RefinementCounterpartRecord S ctx.core probabilityPolicy) : Prop :=
  ctx.refinementCounterpartAdmissible record ∧
  record.candidateId = claimRef.candidateId ∧
  record.observedAt = claimRef.observedAt

def EligibleContinuationControl
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    {package : DeclaredRouteTransportPackage Support}
    {pair : RoutePairRecord package}
    (record : ContinuationControlRecord S ctx.core package pair probabilityPolicy) : Prop :=
  ctx.continuationAdmissibleForControl record ∧
  record.candidateId = claimRef.candidateId ∧
  record.observedAt = claimRef.observedAt

/-! Duplicate-safe complete control inventories. -/

structure CompleteProtocolCounterpartInventory
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (counterpartPolicy : CarriedRecordPolicy S.T
      (ProtocolCounterpartRecord S ctx.core probabilityPolicy)) where
  records : List (ProtocolCounterpartRecord S ctx.core probabilityPolicy)
  recordsNodup : records.Nodup
  recordIdsNodup : (records.map (fun record => record.counterpartId)).Nodup
  everyEligibleCovered :
    ∀ record, EligibleProtocolCounterpart S ctx claimRef record → record ∈ records
  everyRecordEligible :
    ∀ record, record ∈ records → EligibleProtocolCounterpart S ctx claimRef record
  everyRecordCarried :
    ∀ record, record ∈ records → E16Carried S counterpartPolicy record
  singleValuedPerDeclaredKey :
    ∀ record1 record2, record1 ∈ records → record2 ∈ records →
      record1.candidateId = record2.candidateId →
      record1.observedAt = record2.observedAt →
      record1.comparisonBase = record2.comparisonBase → record1 = record2

structure CompleteCompletionCounterpartInventory
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (counterpartPolicy : CarriedRecordPolicy S.T
      (CompletionCounterpartRecord S ctx.core probabilityPolicy)) where
  records : List (CompletionCounterpartRecord S ctx.core probabilityPolicy)
  recordsNodup : records.Nodup
  recordIdsNodup : (records.map (fun record => record.counterpartId)).Nodup
  everyEligibleCovered :
    ∀ record, EligibleCompletionCounterpart S ctx claimRef record → record ∈ records
  everyRecordEligible :
    ∀ record, record ∈ records → EligibleCompletionCounterpart S ctx claimRef record
  everyRecordCarried :
    ∀ record, record ∈ records → E16Carried S counterpartPolicy record
  singleValuedPerDeclaredKey :
    ∀ record1 record2, record1 ∈ records → record2 ∈ records →
      record1.candidateId = record2.candidateId →
      record1.observedAt = record2.observedAt →
      record1.comparisonBase = record2.comparisonBase → record1 = record2

structure CompleteRefinementCounterpartInventory
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (counterpartPolicy : CarriedRecordPolicy S.T
      (RefinementCounterpartRecord S ctx.core probabilityPolicy)) where
  records : List (RefinementCounterpartRecord S ctx.core probabilityPolicy)
  recordsNodup : records.Nodup
  recordIdsNodup : (records.map (fun record => record.counterpartId)).Nodup
  everyEligibleCovered :
    ∀ record, EligibleRefinementCounterpart S ctx claimRef record → record ∈ records
  everyRecordEligible :
    ∀ record, record ∈ records → EligibleRefinementCounterpart S ctx claimRef record
  everyRecordCarried :
    ∀ record, record ∈ records → E16Carried S counterpartPolicy record
  singleValuedPerDeclaredKey :
    ∀ record1 record2, record1 ∈ records → record2 ∈ records →
      record1.candidateId = record2.candidateId →
      record1.observedAt = record2.observedAt →
      record1.comparisonBase = record2.comparisonBase → record1 = record2

structure CompleteContinuationControlInventory
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package)
    (continuationPolicy : CarriedRecordPolicy S.T
      (ContinuationControlRecord S ctx.core package pair probabilityPolicy)) where
  records : List (ContinuationControlRecord S ctx.core package pair probabilityPolicy)
  recordsNodup : records.Nodup
  recordIdsNodup : (records.map (fun record => record.continuationId)).Nodup
  everyEligibleCovered :
    ∀ record, EligibleContinuationControl S ctx claimRef record → record ∈ records
  everyRecordEligible :
    ∀ record, record ∈ records → EligibleContinuationControl S ctx claimRef record
  everyRecordCarried :
    ∀ record, record ∈ records → E16Carried S continuationPolicy record
  singleValuedPerDeclaredKey :
    ∀ record1 record2, record1 ∈ records → record2 ∈ records →
      record1.candidateId = record2.candidateId →
      record1.observedAt = record2.observedAt →
      record1.continuationId = record2.continuationId → record1 = record2

structure CompletePerturbationTrialInventory
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (package : DeclaredRouteTransportPackage Support)
    (boundPolicy : CarriedRecordPolicy S.T DeclaredPerturbationBoundRecord)
    (trialPolicy : CarriedRecordPolicy S.T (PerturbationTrialRecord package)) where
  bound : DeclaredPerturbationBoundRecord
  boundCarried : E16Carried S boundPolicy bound
  boundCandidateLinked : bound.candidateId = claimRef.candidateId
  boundPredatesClaim : bound.declaredAt ≤ claimRef.observedAt
  records : List (PerturbationTrialRecord package)
  recordsNodup : records.Nodup
  recordIdsNodup : (records.map (fun trial => trial.trialId)).Nodup
  everyEligibleCovered :
    ∀ trial, ctx.perturbationTrialEligible trial →
      trial.candidateId = claimRef.candidateId →
      trial.observedAt = claimRef.observedAt →
      trial.perturbationMagnitude ≤ bound.maximumMagnitude → trial ∈ records
  everyRecordEligible :
    ∀ trial, trial ∈ records →
      ctx.perturbationTrialEligible trial ∧
      trial.candidateId = claimRef.candidateId ∧
      trial.observedAt = claimRef.observedAt ∧
      trial.perturbationMagnitude ≤ bound.maximumMagnitude
  everyRecordCarried :
    ∀ trial, trial ∈ records → E16Carried S trialPolicy trial
  singleValuedPerDeclaredKey :
    ∀ trial1 trial2, trial1 ∈ records → trial2 ∈ records →
      trial1.candidateId = trial2.candidateId →
      trial1.observedAt = trial2.observedAt →
      trial1.trialId = trial2.trialId → trial1 = trial2

def EligiblePerturbationTrial
    {package : DeclaredRouteTransportPackage Support}
    {boundPolicy : CarriedRecordPolicy S.T DeclaredPerturbationBoundRecord}
    {trialPolicy : CarriedRecordPolicy S.T (PerturbationTrialRecord package)}
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (inventory : CompletePerturbationTrialInventory S ctx claimRef package
      boundPolicy trialPolicy)
    (record : PerturbationTrialRecord package) : Prop :=
  ctx.perturbationTrialEligible record ∧
  record.candidateId = claimRef.candidateId ∧
  record.observedAt = claimRef.observedAt ∧
  record.perturbationMagnitude ≤ inventory.bound.maximumMagnitude

def emptyCompletePerturbationTrialInventory
    {package : DeclaredRouteTransportPackage Support}
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (boundPolicy : CarriedRecordPolicy S.T DeclaredPerturbationBoundRecord)
    (trialPolicy : CarriedRecordPolicy S.T (PerturbationTrialRecord package))
    (bound : DeclaredPerturbationBoundRecord)
    (boundCarried : E16Carried S boundPolicy bound)
    (boundCandidateLinked : bound.candidateId = claimRef.candidateId)
    (boundPredatesClaim : bound.declaredAt ≤ claimRef.observedAt)
    (noEligible : ∀ trial : PerturbationTrialRecord package,
      ¬ ctx.perturbationTrialEligible trial) :
    CompletePerturbationTrialInventory S ctx claimRef package boundPolicy trialPolicy where
  bound := bound
  boundCarried := boundCarried
  boundCandidateLinked := boundCandidateLinked
  boundPredatesClaim := boundPredatesClaim
  records := []
  recordsNodup := by simp
  recordIdsNodup := by simp
  everyEligibleCovered := by
    intro trial hEligible
    exact (noEligible trial hEligible).elim
  everyRecordEligible := by simp
  everyRecordCarried := by simp
  singleValuedPerDeclaredKey := by simp

/-! E15 status bridge eligibility using E15's literal comparator. -/

structure RouteResidueEligibleForAdaptability
    (e15ctx : OfflineReclosureClassifierContext S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass
      e yDim xiDim)
    (e15policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass
      e yDim xiDim)
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (candidateId : Nat) (observedAt : Rat)
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package)
    (capacityDifference : DeclaredRepairCapacityDifference S ctx.core package pair
      probabilityPolicy)
    (bridgePolicy : CarriedRecordPolicy S.T
      (RouteResidueReconciliationBridgeRecord S ctx.core RouteResiduePayload
        probabilityPolicy)) where
  sourceResidue : RouteResidueDebtRecord RouteResiduePayload
  bridge : RouteResidueReconciliationBridgeRecord S ctx.core
    RouteResiduePayload probabilityPolicy
  sourceResidueCarried :
    E15Carried e15policies.routeResiduePolicy sourceResidue
  sourceClaimLinked : sourceResidue.reconciliationClaimId = candidateId
  residueLinked : bridge.e15Residue = sourceResidue
  candidateLinked : bridge.e16CandidateId = candidateId
  packageLinked : bridge.candidatePackage = package
  routePairLinked : HEq bridge.candidateRoutePair pair
  capacityDifferenceLinked :
    HEq bridge.candidateCapacityDifference capacityDifference
  observationLinked : bridge.observedAt = observedAt
  bridgeCarried : E16Carried S bridgePolicy bridge
  bridgeAccepted :
    ctx.e15ResidueReconciledForAdaptability bridge package pair capacityDifference
  notOutstandingAtObservation :
    ¬ e15ctx.f3RouteResidueAwaitingReconciliation sourceResidue observedAt

/-! Raw candidate and full claim linkage. -/

structure RepairLedgerHolonomyCandidate
    (e15ctx : OfflineReclosureClassifierContext S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass
      e yDim xiDim)
    (e15policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass
      e yDim xiDim)
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (packagePolicy : CarriedRecordPolicy S.T
      (DeclaredRouteTransportPackage Support))
    (basePolicy : CarriedRecordPolicy S.T
      (DeclaredComparisonBaseRecord Support))
    (protocolPolicy : CarriedRecordPolicy S.T
      (RepairCapacityProtocolRecord ChallengeClass))
    (familyPolicy : CarriedRecordPolicy S.T
      (HeldOutChallengeFamily ChallengeClass))
    (bridgePolicy : CarriedRecordPolicy S.T
      (RouteResidueReconciliationBridgeRecord S ctx.core RouteResiduePayload
        probabilityPolicy)) where
  candidateId : Nat
  observedAt : Rat
  carriedPair : CarriedRoutePair S packagePolicy basePolicy
  packageDeclared : ctx.core.routePackageDeclared carriedPair.package
  pairAdmissible :
    ctx.core.routePairAdmissible carriedPair.package carriedPair.pair
  sameCurrent : SameCurrentRouteEndpoints carriedPair.package carriedPair.pair
  predictiveWitness :
    RoutePredictiveWitness carriedPair.package carriedPair.pair
  capacityDifference : DeclaredRepairCapacityDifference S ctx.core
    carriedPair.package carriedPair.pair probabilityPolicy
  protocolCarried :
    E16Carried S protocolPolicy capacityDifference.distributions.left.protocol
  protocolMeasuredAtObservation :
    capacityDifference.distributions.left.protocol.measuredAt = observedAt
  challengeFamilyCarried : E16Carried S familyPolicy
    capacityDifference.distributions.left.protocol.challengeFamily
  challengeFamilyDeclaredBeforeObservation :
    capacityDifference.distributions.left.protocol.challengeFamily.declaredAt ≤
      observedAt
  economy : ProbeEconomy S Probe XiFamily
  probeMove : ProbeMove Probe XiFamily
  budgetData : ExposureBudgetWitness economy probeMove
  bindingBudget : BindingExposureBudget budgetData
  protocolUsesExactBudget :
    ctx.core.protocolUsesBindingBudget capacityDifference.distributions.left.protocol
      economy probeMove budgetData
  routeResidueEligibility :
    RouteResidueEligibleForAdaptability S e15ctx e15policies ctx
      candidateId observedAt carriedPair.package carriedPair.pair
      capacityDifference bridgePolicy

def RoutePairMatchesClaim
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  claimRef.package = package ∧ HEq claimRef.routePair pair

def DistributionsMatchClaim
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    {package : DeclaredRouteTransportPackage Support}
    {pair : RoutePairRecord package}
    (distributions : RepairCapacityDistributionPair S ctx.core package pair
      probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  RoutePairMatchesClaim S package pair claimRef ∧
  distributions.left.protocol = claimRef.protocol ∧
  distributions.right.protocol = claimRef.protocol ∧
  claimRef.challengeClass ∈ claimRef.protocol.challengeFamily.classes

def CandidateMatchesClaim
    {e15ctx : OfflineReclosureClassifierContext S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass
      e yDim xiDim}
    {e15policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass
      e yDim xiDim}
    {probabilityPolicy : CarriedRecordPolicy S.T
      (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass)}
    {ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy}
    {packagePolicy : CarriedRecordPolicy S.T
      (DeclaredRouteTransportPackage Support)}
    {basePolicy : CarriedRecordPolicy S.T
      (DeclaredComparisonBaseRecord Support)}
    {protocolPolicy : CarriedRecordPolicy S.T
      (RepairCapacityProtocolRecord ChallengeClass)}
    {familyPolicy : CarriedRecordPolicy S.T
      (HeldOutChallengeFamily ChallengeClass)}
    {bridgePolicy : CarriedRecordPolicy S.T
      (RouteResidueReconciliationBridgeRecord S ctx.core RouteResiduePayload
        probabilityPolicy)}
    (candidate : RepairLedgerHolonomyCandidate S e15ctx e15policies ctx
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  candidate.candidateId = claimRef.candidateId ∧
  RoutePairMatchesClaim S candidate.carriedPair.package
    candidate.carriedPair.pair claimRef ∧
  candidate.capacityDifference.distributions.left.protocol = claimRef.protocol ∧
  HEq candidate.economy claimRef.economy ∧
  HEq candidate.probeMove claimRef.probeMove ∧
  HEq candidate.budgetData claimRef.budgetData ∧
  candidate.capacityDifference.challengeClass = claimRef.challengeClass ∧
  candidate.observedAt = claimRef.observedAt ∧
  candidate.routeResidueEligibility.bridge.observedAt = claimRef.observedAt

/-! Four control-freedom structures and positive obstructions. -/

structure SupportFixationFreedomEvidence
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (counterpartPolicy : CarriedRecordPolicy S.T
      (ProtocolCounterpartRecord S ctx.core probabilityPolicy))
    (inventory : CompleteProtocolCounterpartInventory S ctx claimRef
      counterpartPolicy) where
  candidateBase : DeclaredComparisonBaseRecord Support
  candidateBaseLinked : candidateBase = claimRef.package.comparisonBase
  everyCounterpartSameBase :
    ∀ counterpart, counterpart ∈ inventory.records →
      counterpart.comparisonBase = candidateBase
  noHonestProtocolClears :
    ∀ counterpart, counterpart ∈ inventory.records →
      ¬ ctx.honestProtocolInternalizationClears counterpart

structure FlatteningFreedomEvidence
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (counterpartPolicy : CarriedRecordPolicy S.T
      (CompletionCounterpartRecord S ctx.core probabilityPolicy))
    (inventory : CompleteCompletionCounterpartInventory S ctx claimRef
      counterpartPolicy) where
  everyCompletionSameBase :
    ∀ completion, completion ∈ inventory.records →
      completion.comparisonBase = claimRef.package.comparisonBase
  noAdmissibleCompletionClears :
    ∀ completion, completion ∈ inventory.records →
      ¬ ctx.completionClearsResidue completion

structure CurrentizationFreedomEvidence
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (counterpartPolicy : CarriedRecordPolicy S.T
      (RefinementCounterpartRecord S ctx.core probabilityPolicy))
    (inventory : CompleteRefinementCounterpartInventory S ctx claimRef
      counterpartPolicy) where
  everyRefinementSameBase :
    ∀ refinement, refinement ∈ inventory.records →
      refinement.comparisonBase = claimRef.package.comparisonBase
  noAdmissibleRefinementCurrentizes :
    ∀ refinement, refinement ∈ inventory.records →
      ¬ ctx.refinementMakesResidueCurrentVisible refinement

structure DissipationFreedomEvidence
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package)
    (continuationPolicy : CarriedRecordPolicy S.T
      (ContinuationControlRecord S ctx.core package pair probabilityPolicy))
    (boundPolicy : CarriedRecordPolicy S.T DeclaredPerturbationBoundRecord)
    (perturbationPolicy : CarriedRecordPolicy S.T
      (PerturbationTrialRecord package))
    (continuationInventory : CompleteContinuationControlInventory S ctx claimRef
      package pair continuationPolicy)
    (perturbationInventory : CompletePerturbationTrialInventory S ctx claimRef
      package boundPolicy perturbationPolicy) where
  everyOwnContinuationSurvives :
    ∀ continuation, continuation ∈ continuationInventory.records →
      ¬ ctx.continuationDissipatesResidue continuation
  everyDeclaredPerturbationSurvives :
    ∀ trial, trial ∈ perturbationInventory.records →
      trial.perturbationMagnitude ≤
        perturbationInventory.bound.maximumMagnitude →
      ctx.boundedPerturbationPreservesResidue package trial

structure SupportConfoundEvidence
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (counterpartPolicy : CarriedRecordPolicy S.T
      (ProtocolCounterpartRecord S ctx.core probabilityPolicy))
    (inventory : CompleteProtocolCounterpartInventory S ctx claimRef
      counterpartPolicy) where
  counterpart : ProtocolCounterpartRecord S ctx.core probabilityPolicy
  member : counterpart ∈ inventory.records
  counterpartCarried : E16Carried S counterpartPolicy counterpart
  counterpartEligible : EligibleProtocolCounterpart S ctx claimRef counterpart
  candidateLinked : counterpart.candidateId = claimRef.candidateId
  observationLinked : counterpart.observedAt = claimRef.observedAt
  baseMismatch :
    counterpart.honestPackage.comparisonBase ≠ claimRef.package.comparisonBase

structure ProtocolArtifactEvidence
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (counterpartPolicy : CarriedRecordPolicy S.T
      (ProtocolCounterpartRecord S ctx.core probabilityPolicy))
    (inventory : CompleteProtocolCounterpartInventory S ctx claimRef
      counterpartPolicy) where
  counterpart : ProtocolCounterpartRecord S ctx.core probabilityPolicy
  member : counterpart ∈ inventory.records
  sameBase : counterpart.comparisonBase = claimRef.package.comparisonBase
  clears : ctx.honestProtocolInternalizationClears counterpart

structure FlattenableResidueEvidence
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (counterpartPolicy : CarriedRecordPolicy S.T
      (CompletionCounterpartRecord S ctx.core probabilityPolicy))
    (inventory : CompleteCompletionCounterpartInventory S ctx claimRef
      counterpartPolicy) where
  completion : CompletionCounterpartRecord S ctx.core probabilityPolicy
  member : completion ∈ inventory.records
  sameBase : completion.comparisonBase = claimRef.package.comparisonBase
  clears : ctx.completionClearsResidue completion

structure CurrentizableResidueEvidence
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (counterpartPolicy : CarriedRecordPolicy S.T
      (RefinementCounterpartRecord S ctx.core probabilityPolicy))
    (inventory : CompleteRefinementCounterpartInventory S ctx claimRef
      counterpartPolicy) where
  refinement : RefinementCounterpartRecord S ctx.core probabilityPolicy
  member : refinement ∈ inventory.records
  sameBase : refinement.comparisonBase = claimRef.package.comparisonBase
  currentizes : ctx.refinementMakesResidueCurrentVisible refinement
  zeroWitnesses : refinement.refinedWitnessCount = 0
  zeroDiscrepancy : refinement.refinedDiscrepancy = 0
  singletonFibers : refinement.refinedMaxFiber = 1

structure DissipativeResidueEvidence
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package)
    (continuationPolicy : CarriedRecordPolicy S.T
      (ContinuationControlRecord S ctx.core package pair probabilityPolicy))
    (inventory : CompleteContinuationControlInventory S ctx claimRef package pair
      continuationPolicy) where
  continuation : ContinuationControlRecord S ctx.core package pair probabilityPolicy
  member : continuation ∈ inventory.records
  dissipates : ctx.continuationDissipatesResidue continuation

/-! Positive administrative rejection evidence remains status-record independent. -/

structure BoundedPerturbationFailureEvidence
    (candidate : RepairLedgerHolonomyCandidate S e15ctx e15policies ctx
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (candidateMatches : CandidateMatchesClaim S candidate claimRef)
    (boundPolicy : CarriedRecordPolicy S.T DeclaredPerturbationBoundRecord)
    (perturbationPolicy : CarriedRecordPolicy S.T
      (PerturbationTrialRecord candidate.carriedPair.package))
    (inventory : CompletePerturbationTrialInventory S ctx claimRef
      candidate.carriedPair.package boundPolicy perturbationPolicy) where
  trial : PerturbationTrialRecord candidate.carriedPair.package
  member : trial ∈ inventory.records
  trialCandidateLinked : trial.candidateId = candidate.candidateId
  trialObservationLinked : trial.observedAt = claimRef.observedAt
  inBound : trial.perturbationMagnitude ≤ inventory.bound.maximumMagnitude
  failed :
    ¬ ctx.boundedPerturbationPreservesResidue candidate.carriedPair.package trial

inductive AdministrativeRejectionKind where
  | package_undeclared
  | pair_inadmissible
  | budget_not_binding
  | protocol_budget_unlinked
  deriving DecidableEq, Repr

structure AdministrativeRejectionEvidence
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (packagePolicy : CarriedRecordPolicy S.T
      (DeclaredRouteTransportPackage Support))
    (basePolicy : CarriedRecordPolicy S.T
      (DeclaredComparisonBaseRecord Support))
    (protocolPolicy : CarriedRecordPolicy S.T
      (RepairCapacityProtocolRecord ChallengeClass))
    (familyPolicy : CarriedRecordPolicy S.T
      (HeldOutChallengeFamily ChallengeClass)) where
  carriedPair : CarriedRoutePair S packagePolicy basePolicy
  pairMatches :
    RoutePairMatchesClaim S carriedPair.package carriedPair.pair claimRef
  protocolCarried : E16Carried S protocolPolicy claimRef.protocol
  challengeFamilyCarried :
    E16Carried S familyPolicy claimRef.protocol.challengeFamily
  protocolMeasuredAtObservation :
    claimRef.protocol.measuredAt = claimRef.observedAt
  reason : AdministrativeRejectionKind
  reasonVerified :
    match reason with
    | .package_undeclared =>
        ¬ ctx.core.routePackageDeclared claimRef.package
    | .pair_inadmissible =>
        ¬ ctx.core.routePairAdmissible claimRef.package claimRef.routePair
    | .budget_not_binding =>
        ¬ BindingExposureBudget claimRef.budgetData
    | .protocol_budget_unlinked =>
        ¬ ctx.core.protocolUsesBindingBudget claimRef.protocol claimRef.economy
          claimRef.probeMove claimRef.budgetData

structure GatedFlatControlEvidence
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (packagePolicy : CarriedRecordPolicy S.T
      (DeclaredRouteTransportPackage Support))
    (basePolicy : CarriedRecordPolicy S.T
      (DeclaredComparisonBaseRecord Support))
    (protocolPolicy : CarriedRecordPolicy S.T
      (RepairCapacityProtocolRecord ChallengeClass))
    (familyPolicy : CarriedRecordPolicy S.T
      (HeldOutChallengeFamily ChallengeClass)) where
  carriedPair : CarriedRoutePair S packagePolicy basePolicy
  pairMatches :
    RoutePairMatchesClaim S carriedPair.package carriedPair.pair claimRef
  packageDeclared : ctx.core.routePackageDeclared carriedPair.package
  pairAdmissible : ctx.core.routePairAdmissible carriedPair.package carriedPair.pair
  sameCurrent : SameCurrentRouteEndpoints carriedPair.package carriedPair.pair
  protocolCarried : E16Carried S protocolPolicy claimRef.protocol
  challengeFamilyCarried :
    E16Carried S familyPolicy claimRef.protocol.challengeFamily
  challengeFamilyDeclaredBeforeObservation :
    claimRef.protocol.challengeFamily.declaredAt ≤ claimRef.observedAt
  protocolMeasuredAtObservation :
    claimRef.protocol.measuredAt = claimRef.observedAt
  bindingBudget : BindingExposureBudget claimRef.budgetData
  protocolUsesExactBudget :
    ctx.core.protocolUsesBindingBudget claimRef.protocol claimRef.economy
      claimRef.probeMove claimRef.budgetData
  flatReason :
    FuturePredictiveEquiv carriedPair.package.core
      carriedPair.pair.gammaEndpoint carriedPair.pair.etaEndpoint ∨
    ∃ distributions : RepairCapacityDistributionPair S ctx.core
        carriedPair.package carriedPair.pair probabilityPolicy,
      DistributionsMatchClaim S ctx distributions claimRef ∧
      Nonempty (NoDeclaredRepairCapacityDifference S ctx.core
        carriedPair.package carriedPair.pair probabilityPolicy distributions)

theorem E16_FlatSecondArmUsesClaimLinkedPair
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (packagePolicy : CarriedRecordPolicy S.T
      (DeclaredRouteTransportPackage Support))
    (basePolicy : CarriedRecordPolicy S.T
      (DeclaredComparisonBaseRecord Support))
    (protocolPolicy : CarriedRecordPolicy S.T
      (RepairCapacityProtocolRecord ChallengeClass))
    (familyPolicy : CarriedRecordPolicy S.T
      (HeldOutChallengeFamily ChallengeClass))
    (evidence : GatedFlatControlEvidence S ctx claimRef packagePolicy basePolicy
      protocolPolicy familyPolicy)
    (notFuture : ¬ FuturePredictiveEquiv evidence.carriedPair.package.core
      evidence.carriedPair.pair.gammaEndpoint
      evidence.carriedPair.pair.etaEndpoint) :
    ∃ distributions : RepairCapacityDistributionPair S ctx.core
        evidence.carriedPair.package evidence.carriedPair.pair probabilityPolicy,
      DistributionsMatchClaim S ctx distributions claimRef ∧
      Nonempty (NoDeclaredRepairCapacityDifference S ctx.core
        evidence.carriedPair.package evidence.carriedPair.pair probabilityPolicy
        distributions) := by
  rcases evidence.flatReason with future | equalPair
  · exact (notFuture future).elim
  · exact equalPair

theorem E16_UnrelatedEqualPairCannotReplaceClaimDifference
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (package : DeclaredRouteTransportPackage Support)
    (pair : RoutePairRecord package)
    (claimDifference : DeclaredRepairCapacityDifference S ctx.core package pair
      probabilityPolicy)
    (claimDifferenceMatches :
      DistributionsMatchClaim S ctx claimDifference.distributions claimRef)
    (unrelated : RepairCapacityDistributionPair S ctx.core package pair
      probabilityPolicy)
    (unrelatedDoesNotMatch : ¬ DistributionsMatchClaim S ctx unrelated claimRef) :
    DistributionsMatchClaim S ctx claimDifference.distributions claimRef ∧
      ¬ (DistributionsMatchClaim S ctx unrelated claimRef ∧
        Nonempty (NoDeclaredRepairCapacityDifference S ctx.core package pair
          probabilityPolicy unrelated)) := by
  refine ⟨claimDifferenceMatches, ?_⟩
  rintro ⟨unrelatedMatches, _⟩
  exact unrelatedDoesNotMatch unrelatedMatches

structure CoherentAdaptabilityEvidence
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (e15ctx : OfflineReclosureClassifierContext S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass
      e yDim xiDim)
    (e15policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass
      e yDim xiDim)
    (packagePolicy : CarriedRecordPolicy S.T
      (DeclaredRouteTransportPackage Support))
    (basePolicy : CarriedRecordPolicy S.T
      (DeclaredComparisonBaseRecord Support))
    (protocolPolicy : CarriedRecordPolicy S.T
      (RepairCapacityProtocolRecord ChallengeClass))
    (familyPolicy : CarriedRecordPolicy S.T
      (HeldOutChallengeFamily ChallengeClass))
    (bridgePolicy : CarriedRecordPolicy S.T
      (RouteResidueReconciliationBridgeRecord S ctx.core RouteResiduePayload
        probabilityPolicy))
    (candidate : RepairLedgerHolonomyCandidate S e15ctx e15policies ctx
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy)
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (candidateMatches : CandidateMatchesClaim S candidate claimRef)
    (protocolCounterpartPolicy : CarriedRecordPolicy S.T
      (ProtocolCounterpartRecord S ctx.core probabilityPolicy))
    (completionCounterpartPolicy : CarriedRecordPolicy S.T
      (CompletionCounterpartRecord S ctx.core probabilityPolicy))
    (refinementCounterpartPolicy : CarriedRecordPolicy S.T
      (RefinementCounterpartRecord S ctx.core probabilityPolicy))
    (protocolInventory : CompleteProtocolCounterpartInventory S ctx claimRef
      protocolCounterpartPolicy)
    (completionInventory : CompleteCompletionCounterpartInventory S ctx claimRef
      completionCounterpartPolicy)
    (refinementInventory : CompleteRefinementCounterpartInventory S ctx claimRef
      refinementCounterpartPolicy)
    (continuationPolicy : CarriedRecordPolicy S.T
      (ContinuationControlRecord S ctx.core candidate.carriedPair.package
        candidate.carriedPair.pair probabilityPolicy))
    (continuationInventory : CompleteContinuationControlInventory
      (S := S) (Support := Support) (ChallengeClass := ChallengeClass)
      (Probe := Probe) (XiFamily := XiFamily)
      (RouteResiduePayload := RouteResiduePayload)
      (probabilityPolicy := probabilityPolicy)
      (ctx := ctx) (claimRef := claimRef)
      (package := candidate.carriedPair.package)
      (pair := candidate.carriedPair.pair)
      (continuationPolicy := continuationPolicy))
    (boundPolicy : CarriedRecordPolicy S.T DeclaredPerturbationBoundRecord)
    (perturbationPolicy : CarriedRecordPolicy S.T
      (PerturbationTrialRecord candidate.carriedPair.package))
    (perturbationInventory : CompletePerturbationTrialInventory S ctx claimRef
      candidate.carriedPair.package boundPolicy perturbationPolicy) where
  supportFreedom :
    SupportFixationFreedomEvidence S ctx claimRef protocolCounterpartPolicy
      protocolInventory
  flatteningFreedom :
    FlatteningFreedomEvidence S ctx claimRef completionCounterpartPolicy
      completionInventory
  currentizationFreedom :
    CurrentizationFreedomEvidence S ctx claimRef refinementCounterpartPolicy
      refinementInventory
  dissipationFreedom : DissipationFreedomEvidence S ctx claimRef
    candidate.carriedPair.package candidate.carriedPair.pair
    continuationPolicy boundPolicy perturbationPolicy continuationInventory
    perturbationInventory

/-! ## Status apparatus -/

section StatusApparatus

variable
  (probabilityPolicy : CarriedRecordPolicy S.T
    (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass))
variable
  (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
    RouteResiduePayload probabilityPolicy)
variable
  (e15ctx : OfflineReclosureClassifierContext S X RecordValue Q
    TransportedValue FOut Readout RouteResiduePayload ChallengeClass
    e yDim xiDim)
variable
  (e15policies : OfflineReclosureEvidencePolicies S X RecordValue Q
    TransportedValue FOut Readout RouteResiduePayload ChallengeClass
    e yDim xiDim)
variable
  (packagePolicy : CarriedRecordPolicy S.T
    (DeclaredRouteTransportPackage Support))
variable
  (basePolicy : CarriedRecordPolicy S.T
    (DeclaredComparisonBaseRecord Support))
variable
  (protocolPolicy : CarriedRecordPolicy S.T
    (RepairCapacityProtocolRecord ChallengeClass))
variable
  (familyPolicy : CarriedRecordPolicy S.T
    (HeldOutChallengeFamily ChallengeClass))
variable
  (bridgePolicy : CarriedRecordPolicy S.T
    (RouteResidueReconciliationBridgeRecord S ctx.core RouteResiduePayload
      probabilityPolicy))

inductive AdaptabilityStatus where
  | support_confound
  | artifact
  | flat
  | flattenable
  | currentizable_slack
  | dissipative
  | coherent_adaptability
  | adaptability_rejected
  deriving DecidableEq, Repr

structure AdaptabilityStatusRecord
    {probabilityPolicy : CarriedRecordPolicy S.T
      (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass)}
    (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
      RouteResiduePayload probabilityPolicy)
    (e15ctx : OfflineReclosureClassifierContext S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass
      e yDim xiDim)
    (e15policies : OfflineReclosureEvidencePolicies S X RecordValue Q
      TransportedValue FOut Readout RouteResiduePayload ChallengeClass
      e yDim xiDim)
    (packagePolicy : CarriedRecordPolicy S.T
      (DeclaredRouteTransportPackage Support))
    (basePolicy : CarriedRecordPolicy S.T
      (DeclaredComparisonBaseRecord Support))
    (protocolPolicy : CarriedRecordPolicy S.T
      (RepairCapacityProtocolRecord ChallengeClass))
    (familyPolicy : CarriedRecordPolicy S.T
      (HeldOutChallengeFamily ChallengeClass))
    (bridgePolicy : CarriedRecordPolicy S.T
      (RouteResidueReconciliationBridgeRecord S ctx.core RouteResiduePayload
        probabilityPolicy)) where
  statusRecordId : Nat
  claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily
  status : AdaptabilityStatus
  candidate : Option (RepairLedgerHolonomyCandidate S e15ctx e15policies ctx
    packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy)
  obstructionRecordId : Option Nat
  recordedAt : Rat

def AdaptabilityStatusRecordMatchesClaim
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy) : Prop :=
  record.claimRef = claimRef

def AdaptabilityStatusOccurrenceFor
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy) : Prop :=
  AdaptabilityStatusRecordMatchesClaim (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef record ∧
    E16Carried S statusPolicy record

/-! Claim-scoped raw evidence, independent of status records. -/

def SupportConfoundEvidenceFor
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  ∃ counterpartPolicy : CarriedRecordPolicy S.T
      (ProtocolCounterpartRecord S ctx.core probabilityPolicy),
    ∃ inventory : CompleteProtocolCounterpartInventory S ctx claimRef
        counterpartPolicy,
      Nonempty (SupportConfoundEvidence S ctx claimRef counterpartPolicy inventory)

def ArtifactEvidenceFor
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  ∃ candidate : RepairLedgerHolonomyCandidate S e15ctx e15policies ctx
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy,
    CandidateMatchesClaim S candidate claimRef ∧
      ∃ counterpartPolicy : CarriedRecordPolicy S.T
          (ProtocolCounterpartRecord S ctx.core probabilityPolicy),
        ∃ inventory : CompleteProtocolCounterpartInventory S ctx claimRef
            counterpartPolicy,
          Nonempty (ProtocolArtifactEvidence S ctx claimRef counterpartPolicy inventory)

def FlatEvidenceFor
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  Nonempty (GatedFlatControlEvidence S ctx claimRef packagePolicy basePolicy
    protocolPolicy familyPolicy)

def FlattenableEvidenceFor
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  ∃ candidate : RepairLedgerHolonomyCandidate S e15ctx e15policies ctx
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy,
    CandidateMatchesClaim S candidate claimRef ∧
      ∃ counterpartPolicy : CarriedRecordPolicy S.T
          (CompletionCounterpartRecord S ctx.core probabilityPolicy),
        ∃ inventory : CompleteCompletionCounterpartInventory S ctx claimRef
            counterpartPolicy,
          Nonempty (FlattenableResidueEvidence S ctx claimRef counterpartPolicy
            inventory)

def CurrentizableEvidenceFor
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  ∃ candidate : RepairLedgerHolonomyCandidate S e15ctx e15policies ctx
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy,
    CandidateMatchesClaim S candidate claimRef ∧
      ∃ counterpartPolicy : CarriedRecordPolicy S.T
          (RefinementCounterpartRecord S ctx.core probabilityPolicy),
        ∃ inventory : CompleteRefinementCounterpartInventory S ctx claimRef
            counterpartPolicy,
          Nonempty (CurrentizableResidueEvidence S ctx claimRef counterpartPolicy
            inventory)

def DissipativeEvidenceFor
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  ∃ candidate : RepairLedgerHolonomyCandidate S e15ctx e15policies ctx
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy,
    CandidateMatchesClaim S candidate claimRef ∧
      ∃ continuationPolicy : CarriedRecordPolicy S.T
          (ContinuationControlRecord S ctx.core candidate.carriedPair.package
            candidate.carriedPair.pair probabilityPolicy),
        ∃ inventory : CompleteContinuationControlInventory S ctx claimRef
            candidate.carriedPair.package candidate.carriedPair.pair
            continuationPolicy,
          Nonempty (DissipativeResidueEvidence S ctx claimRef
            candidate.carriedPair.package candidate.carriedPair.pair
            continuationPolicy inventory)

def CoherentAdaptabilityEvidenceFor
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  ∃ candidate : RepairLedgerHolonomyCandidate S e15ctx e15policies ctx
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy,
    ∃ candidateMatches : CandidateMatchesClaim S candidate claimRef,
      ∃ protocolCounterpartPolicy : CarriedRecordPolicy S.T
          (ProtocolCounterpartRecord S ctx.core probabilityPolicy),
        ∃ completionCounterpartPolicy : CarriedRecordPolicy S.T
            (CompletionCounterpartRecord S ctx.core probabilityPolicy),
          ∃ refinementCounterpartPolicy : CarriedRecordPolicy S.T
              (RefinementCounterpartRecord S ctx.core probabilityPolicy),
            ∃ protocolInventory : CompleteProtocolCounterpartInventory S ctx
                claimRef protocolCounterpartPolicy,
              ∃ completionInventory : CompleteCompletionCounterpartInventory S ctx
                  claimRef completionCounterpartPolicy,
                ∃ refinementInventory : CompleteRefinementCounterpartInventory S ctx
                    claimRef refinementCounterpartPolicy,
                  ∃ continuationPolicy : CarriedRecordPolicy S.T
                      (ContinuationControlRecord S ctx.core
                        candidate.carriedPair.package candidate.carriedPair.pair
                        probabilityPolicy),
                    ∃ continuationInventory : CompleteContinuationControlInventory S
                        ctx claimRef candidate.carriedPair.package
                        candidate.carriedPair.pair continuationPolicy,
                      ∃ boundPolicy : CarriedRecordPolicy S.T
                          DeclaredPerturbationBoundRecord,
                        ∃ perturbationPolicy : CarriedRecordPolicy S.T
                            (PerturbationTrialRecord candidate.carriedPair.package),
                          ∃ perturbationInventory :
                              CompletePerturbationTrialInventory S ctx claimRef
                                candidate.carriedPair.package boundPolicy
                                perturbationPolicy,
                            Nonempty (CoherentAdaptabilityEvidence S ctx e15ctx
                              e15policies packagePolicy basePolicy protocolPolicy
                              familyPolicy bridgePolicy candidate claimRef
                              candidateMatches protocolCounterpartPolicy
                              completionCounterpartPolicy
                              refinementCounterpartPolicy protocolInventory
                              completionInventory refinementInventory
                              continuationPolicy continuationInventory boundPolicy
                              perturbationPolicy perturbationInventory)

def AdaptabilityRejectedEvidenceFor
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  (∃ candidate : RepairLedgerHolonomyCandidate S e15ctx e15policies ctx
        packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy,
      ∃ candidateMatches : CandidateMatchesClaim S candidate claimRef,
        ∃ boundPolicy : CarriedRecordPolicy S.T DeclaredPerturbationBoundRecord,
          ∃ perturbationPolicy : CarriedRecordPolicy S.T
              (PerturbationTrialRecord candidate.carriedPair.package),
            ∃ inventory : CompletePerturbationTrialInventory S ctx claimRef
                candidate.carriedPair.package boundPolicy perturbationPolicy,
              Nonempty (BoundedPerturbationFailureEvidence S candidate claimRef
                candidateMatches boundPolicy perturbationPolicy inventory)) ∨
    Nonempty (AdministrativeRejectionEvidence S ctx claimRef packagePolicy
      basePolicy protocolPolicy familyPolicy)

/-! Priority-normalized cases exclude higher raw evidence only. -/

def SupportConfoundCase
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy) : Prop :=
  AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record ∧
    record.status = .support_confound ∧
    SupportConfoundEvidenceFor S probabilityPolicy ctx claimRef

def ArtifactCase
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy) : Prop :=
  AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record ∧
    ¬ SupportConfoundEvidenceFor S probabilityPolicy ctx claimRef ∧
    record.status = .artifact ∧
    ArtifactEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef

def FlatCase
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy) : Prop :=
  AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record ∧
    ¬ SupportConfoundEvidenceFor S probabilityPolicy ctx claimRef ∧
    ¬ ArtifactEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    record.status = .flat ∧
    FlatEvidenceFor S probabilityPolicy ctx packagePolicy basePolicy protocolPolicy
      familyPolicy claimRef

def FlattenableCase
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy) : Prop :=
  AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record ∧
    ¬ SupportConfoundEvidenceFor S probabilityPolicy ctx claimRef ∧
    ¬ ArtifactEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    ¬ FlatEvidenceFor S probabilityPolicy ctx packagePolicy basePolicy protocolPolicy
      familyPolicy claimRef ∧
    record.status = .flattenable ∧
    FlattenableEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef

def CurrentizableSlackCase
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy) : Prop :=
  AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record ∧
    ¬ SupportConfoundEvidenceFor S probabilityPolicy ctx claimRef ∧
    ¬ ArtifactEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    ¬ FlatEvidenceFor S probabilityPolicy ctx packagePolicy basePolicy protocolPolicy
      familyPolicy claimRef ∧
    ¬ FlattenableEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    record.status = .currentizable_slack ∧
    CurrentizableEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef

def DissipativeCase
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy) : Prop :=
  AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record ∧
    ¬ SupportConfoundEvidenceFor S probabilityPolicy ctx claimRef ∧
    ¬ ArtifactEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    ¬ FlatEvidenceFor S probabilityPolicy ctx packagePolicy basePolicy protocolPolicy
      familyPolicy claimRef ∧
    ¬ FlattenableEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    ¬ CurrentizableEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    record.status = .dissipative ∧
    DissipativeEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef

def CoherentAdaptabilityCase
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy) : Prop :=
  AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record ∧
    ¬ SupportConfoundEvidenceFor S probabilityPolicy ctx claimRef ∧
    ¬ ArtifactEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    ¬ FlatEvidenceFor S probabilityPolicy ctx packagePolicy basePolicy protocolPolicy
      familyPolicy claimRef ∧
    ¬ FlattenableEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    ¬ CurrentizableEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    ¬ DissipativeEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    record.status = .coherent_adaptability ∧
    CoherentAdaptabilityEvidenceFor S probabilityPolicy ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy claimRef

def AdaptabilityRejectedCase
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)
    (record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy) : Prop :=
  AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record ∧
    ¬ SupportConfoundEvidenceFor S probabilityPolicy ctx claimRef ∧
    ¬ ArtifactEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    ¬ FlatEvidenceFor S probabilityPolicy ctx packagePolicy basePolicy protocolPolicy
      familyPolicy claimRef ∧
    ¬ FlattenableEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    ¬ CurrentizableEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    ¬ DissipativeEvidenceFor S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    ¬ CoherentAdaptabilityEvidenceFor S probabilityPolicy ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy claimRef ∧
    record.status = .adaptability_rejected ∧
    AdaptabilityRejectedEvidenceFor S probabilityPolicy ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy claimRef

/-! Carried occurrence wrappers. -/

def SupportConfoundHolds
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  ∃ record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy,
    AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy basePolicy protocolPolicy familyPolicy
      bridgePolicy statusPolicy claimRef record ∧
    SupportConfoundCase S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record

def ArtifactHolds
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  ∃ record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy,
    AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy basePolicy protocolPolicy familyPolicy
      bridgePolicy statusPolicy claimRef record ∧
    ArtifactCase S probabilityPolicy ctx e15ctx e15policies packagePolicy basePolicy
      protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record

def FlatHolds
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  ∃ record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy,
    AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy basePolicy protocolPolicy familyPolicy
      bridgePolicy statusPolicy claimRef record ∧
    FlatCase S probabilityPolicy ctx e15ctx e15policies packagePolicy basePolicy
      protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record

def FlattenableHolds
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  ∃ record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy,
    AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy basePolicy protocolPolicy familyPolicy
      bridgePolicy statusPolicy claimRef record ∧
    FlattenableCase S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record

def CurrentizableSlackHolds
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  ∃ record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy,
    AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy basePolicy protocolPolicy familyPolicy
      bridgePolicy statusPolicy claimRef record ∧
    CurrentizableSlackCase S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record

def DissipativeHolds
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  ∃ record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy,
    AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy basePolicy protocolPolicy familyPolicy
      bridgePolicy statusPolicy claimRef record ∧
    DissipativeCase S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record

def CoherentAdaptabilityHolds
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  ∃ record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy,
    AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy basePolicy protocolPolicy familyPolicy
      bridgePolicy statusPolicy claimRef record ∧
    CoherentAdaptabilityCase S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record

def AdaptabilityRejectedHolds
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) : Prop :=
  ∃ record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy,
    AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
      S ctx e15ctx e15policies packagePolicy basePolicy protocolPolicy familyPolicy
      bridgePolicy statusPolicy claimRef record ∧
    AdaptabilityRejectedCase S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef record

structure CompleteAdaptabilityStatus
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy))
    (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily) where
  branchValid :
    SupportConfoundHolds S probabilityPolicy ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef ∨
      ArtifactHolds S probabilityPolicy ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef ∨
      FlatHolds S probabilityPolicy ctx e15ctx e15policies packagePolicy basePolicy
        protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef ∨
      FlattenableHolds S probabilityPolicy ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef ∨
      CurrentizableSlackHolds S probabilityPolicy ctx e15ctx e15policies
        packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
        claimRef ∨
      DissipativeHolds S probabilityPolicy ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef ∨
      CoherentAdaptabilityHolds S probabilityPolicy ctx e15ctx e15policies
        packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
        claimRef ∨
      AdaptabilityRejectedHolds S probabilityPolicy ctx e15ctx e15policies
        packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
        claimRef
  statusUnique :
    ∀ record1 record2,
      AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
        S ctx e15ctx e15policies packagePolicy basePolicy protocolPolicy familyPolicy
          bridgePolicy statusPolicy claimRef record1 →
      AdaptabilityStatusOccurrenceFor (probabilityPolicy := probabilityPolicy)
        S ctx e15ctx e15policies packagePolicy basePolicy protocolPolicy familyPolicy
          bridgePolicy statusPolicy claimRef record2 →
      record1.status = record2.status

/-! Named obstruction packages. -/

structure SupportConfoundFalsifier
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy)) where
  claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily
  evidence : SupportConfoundEvidenceFor S probabilityPolicy ctx claimRef
  complete : CompleteAdaptabilityStatus S probabilityPolicy ctx e15ctx e15policies
    packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
    claimRef

structure ArtifactFalsifier
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy)) where
  claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily
  evidence : ArtifactEvidenceFor S probabilityPolicy ctx e15ctx e15policies
    packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy claimRef
  complete : CompleteAdaptabilityStatus S probabilityPolicy ctx e15ctx e15policies
    packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
    claimRef

structure FlatteningFalsifier
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy)) where
  claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily
  evidence : FlattenableEvidenceFor S probabilityPolicy ctx e15ctx e15policies
    packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy claimRef
  complete : CompleteAdaptabilityStatus S probabilityPolicy ctx e15ctx e15policies
    packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
    claimRef

structure CurrentizationFalsifier
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy)) where
  claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily
  evidence : CurrentizableEvidenceFor S probabilityPolicy ctx e15ctx e15policies
    packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy claimRef
  complete : CompleteAdaptabilityStatus S probabilityPolicy ctx e15ctx e15policies
    packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
    claimRef

structure DissipationFalsifier
    (statusPolicy : CarriedRecordPolicy S.T
      (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy)) where
  claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily
  evidence : DissipativeEvidenceFor S probabilityPolicy ctx e15ctx e15policies
    packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy claimRef
  complete : CompleteAdaptabilityStatus S probabilityPolicy ctx e15ctx e15policies
    packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
    claimRef

end StatusApparatus

namespace E16

def ExactlyOne : List Prop → Prop
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

end E16

section Theorems

variable
  (probabilityPolicy : CarriedRecordPolicy S.T
    (RepairDischargeProbabilityRecord LedgerEntry ChallengeClass))
variable
  (ctx : AdaptabilityClassifierContext S Support ChallengeClass Probe XiFamily
    RouteResiduePayload probabilityPolicy)
variable
  (e15ctx : OfflineReclosureClassifierContext S X RecordValue Q
    TransportedValue FOut Readout RouteResiduePayload ChallengeClass
    e yDim xiDim)
variable
  (e15policies : OfflineReclosureEvidencePolicies S X RecordValue Q
    TransportedValue FOut Readout RouteResiduePayload ChallengeClass
    e yDim xiDim)
variable
  (packagePolicy : CarriedRecordPolicy S.T
    (DeclaredRouteTransportPackage Support))
variable
  (basePolicy : CarriedRecordPolicy S.T
    (DeclaredComparisonBaseRecord Support))
variable
  (protocolPolicy : CarriedRecordPolicy S.T
    (RepairCapacityProtocolRecord ChallengeClass))
variable
  (familyPolicy : CarriedRecordPolicy S.T
    (HeldOutChallengeFamily ChallengeClass))
variable
  (bridgePolicy : CarriedRecordPolicy S.T
    (RouteResidueReconciliationBridgeRecord S ctx.core RouteResiduePayload
      probabilityPolicy))
variable
  (statusPolicy : CarriedRecordPolicy S.T
    (AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy))
variable
  (claimRef : AdaptabilityClaimRef S Support ChallengeClass Probe XiFamily)

theorem E16_AdaptabilityStatus
    (complete : CompleteAdaptabilityStatus S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      statusPolicy claimRef) :
    E16.ExactlyOne
      [SupportConfoundHolds S probabilityPolicy ctx e15ctx e15policies packagePolicy
          basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef,
       ArtifactHolds S probabilityPolicy ctx e15ctx e15policies packagePolicy
          basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef,
       FlatHolds S probabilityPolicy ctx e15ctx e15policies packagePolicy basePolicy
          protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef,
       FlattenableHolds S probabilityPolicy ctx e15ctx e15policies packagePolicy
          basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef,
       CurrentizableSlackHolds S probabilityPolicy ctx e15ctx e15policies
          packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
          statusPolicy claimRef,
       DissipativeHolds S probabilityPolicy ctx e15ctx e15policies packagePolicy
          basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef,
       CoherentAdaptabilityHolds S probabilityPolicy ctx e15ctx e15policies
          packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
          statusPolicy claimRef,
       AdaptabilityRejectedHolds S probabilityPolicy ctx e15ctx e15policies
          packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
          statusPolicy claimRef] := by
  simp only [E16.ExactlyOne]
  rcases complete.branchValid with
    hSupport | hArtifact | hFlat | hFlattenable | hCurrentizable | hDissipative |
      hCoherent | hRejected
  · rcases hSupport with ⟨record, hOccurrence, hCase⟩
    have hStatus : record.status = AdaptabilityStatus.support_confound := hCase.2.1
    refine Or.inl ⟨⟨record, hOccurrence, hCase⟩, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherCase⟩ <;>
      simp only [ArtifactCase, FlatCase, FlattenableCase, CurrentizableSlackCase,
        DissipativeCase, CoherentAdaptabilityCase, AdaptabilityRejectedCase] at hOtherCase <;>
      have hEq := complete.statusUnique record other hOccurrence hOtherOccurrence <;>
      rw [hStatus] at hEq <;> simp_all
  · rcases hArtifact with ⟨record, hOccurrence, hCase⟩
    have hStatus : record.status = AdaptabilityStatus.artifact := hCase.2.2.1
    refine Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hCase⟩, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherCase⟩ <;>
      simp only [SupportConfoundCase, FlatCase, FlattenableCase,
        CurrentizableSlackCase, DissipativeCase, CoherentAdaptabilityCase,
        AdaptabilityRejectedCase] at hOtherCase <;>
      have hEq := complete.statusUnique record other hOccurrence hOtherOccurrence <;>
      rw [hStatus] at hEq <;> simp_all
  · rcases hFlat with ⟨record, hOccurrence, hCase⟩
    have hStatus : record.status = AdaptabilityStatus.flat := hCase.2.2.2.1
    refine Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hCase⟩, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherCase⟩ <;>
      simp only [SupportConfoundCase, ArtifactCase, FlattenableCase,
        CurrentizableSlackCase, DissipativeCase, CoherentAdaptabilityCase,
        AdaptabilityRejectedCase] at hOtherCase <;>
      have hEq := complete.statusUnique record other hOccurrence hOtherOccurrence <;>
      rw [hStatus] at hEq <;> simp_all
  · rcases hFlattenable with ⟨record, hOccurrence, hCase⟩
    have hStatus : record.status = AdaptabilityStatus.flattenable :=
      hCase.2.2.2.2.1
    refine Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hCase⟩, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherCase⟩ <;>
      simp only [SupportConfoundCase, ArtifactCase, FlatCase,
        CurrentizableSlackCase, DissipativeCase, CoherentAdaptabilityCase,
        AdaptabilityRejectedCase] at hOtherCase <;>
      have hEq := complete.statusUnique record other hOccurrence hOtherOccurrence <;>
      rw [hStatus] at hEq <;> simp_all
  · rcases hCurrentizable with ⟨record, hOccurrence, hCase⟩
    have hStatus : record.status = AdaptabilityStatus.currentizable_slack :=
      hCase.2.2.2.2.2.1
    refine Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hCase⟩, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherCase⟩ <;>
      simp only [SupportConfoundCase, ArtifactCase, FlatCase, FlattenableCase,
        DissipativeCase, CoherentAdaptabilityCase, AdaptabilityRejectedCase] at hOtherCase <;>
      have hEq := complete.statusUnique record other hOccurrence hOtherOccurrence <;>
      rw [hStatus] at hEq <;> simp_all
  · rcases hDissipative with ⟨record, hOccurrence, hCase⟩
    have hStatus : record.status = AdaptabilityStatus.dissipative :=
      hCase.2.2.2.2.2.2.1
    refine Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hCase⟩, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherCase⟩ <;>
      simp only [SupportConfoundCase, ArtifactCase, FlatCase, FlattenableCase,
        CurrentizableSlackCase, CoherentAdaptabilityCase,
        AdaptabilityRejectedCase] at hOtherCase <;>
      have hEq := complete.statusUnique record other hOccurrence hOtherOccurrence <;>
      rw [hStatus] at hEq <;> simp_all
  · rcases hCoherent with ⟨record, hOccurrence, hCase⟩
    have hStatus : record.status = AdaptabilityStatus.coherent_adaptability :=
      hCase.2.2.2.2.2.2.2.1
    refine Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOccurrence, hCase⟩, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherCase⟩ <;>
      simp only [SupportConfoundCase, ArtifactCase, FlatCase, FlattenableCase,
        CurrentizableSlackCase, DissipativeCase, AdaptabilityRejectedCase] at hOtherCase <;>
      have hEq := complete.statusUnique record other hOccurrence hOtherOccurrence <;>
      rw [hStatus] at hEq <;> simp_all
  · rcases hRejected with ⟨record, hOccurrence, hCase⟩
    have hStatus : record.status = AdaptabilityStatus.adaptability_rejected :=
      hCase.2.2.2.2.2.2.2.2.1
    refine Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <|
      Or.inr ⟨⟨record, hOccurrence, hCase⟩, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      rintro ⟨other, hOtherOccurrence, hOtherCase⟩ <;>
      simp only [SupportConfoundCase, ArtifactCase, FlatCase, FlattenableCase,
        CurrentizableSlackCase, DissipativeCase, CoherentAdaptabilityCase] at hOtherCase <;>
      have hEq := complete.statusUnique record other hOccurrence hOtherOccurrence <;>
      rw [hStatus] at hEq <;> simp_all

theorem E16_CoherentAdaptability
    (record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy)
    (hOccurrence : AdaptabilityStatusOccurrenceFor
      (probabilityPolicy := probabilityPolicy) S ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
      claimRef record)
    (hStatus : record.status = AdaptabilityStatus.coherent_adaptability)
    (hCase : CoherentAdaptabilityCase S probabilityPolicy ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
      claimRef record) :
    CoherentAdaptabilityHolds S probabilityPolicy ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
      claimRef := by
  exact ⟨record, hOccurrence, hCase⟩

theorem E16_CurrentAuditBlindness
    (evidence : CoherentAdaptabilityEvidenceFor S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      claimRef) :
    CurrentEventEquiv claimRef.package.core claimRef.routePair.gammaEndpoint
      claimRef.routePair.etaEndpoint := by
  rcases evidence with ⟨candidate, hMatches, _⟩
  rcases hMatches.2.1 with ⟨hPackage, hPair⟩
  have hSigma :
      (⟨claimRef.package, claimRef.routePair⟩ :
        Σ package : DeclaredRouteTransportPackage Support, RoutePairRecord package) =
      ⟨candidate.carriedPair.package, candidate.carriedPair.pair⟩ :=
    Sigma.ext hPackage hPair
  let currentEquivalent :
      (Σ package : DeclaredRouteTransportPackage Support, RoutePairRecord package) →
        Prop := fun route =>
      CurrentEventEquiv route.1.core route.2.gammaEndpoint route.2.etaEndpoint
  change currentEquivalent ⟨claimRef.package, claimRef.routePair⟩
  rw [hSigma]
  exact candidate.sameCurrent.currentEquivalent

theorem E16_RouteManufacturesRepairCapacity
    (evidence : CoherentAdaptabilityEvidenceFor S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      claimRef) :
    ∃ left right : RepairDischargeProbabilityRecord LedgerEntry ChallengeClass,
      left.challengeClass = claimRef.challengeClass ∧
      right.challengeClass = claimRef.challengeClass ∧
      left.probability ≠ right.probability := by
  rcases evidence with ⟨candidate, hMatches, _⟩
  rcases hMatches with ⟨_, _, _, _, _, _, hChallenge, _, _⟩
  exact ⟨candidate.capacityDifference.leftRecord,
    candidate.capacityDifference.rightRecord,
    candidate.capacityDifference.leftClassLinked.trans hChallenge,
    candidate.capacityDifference.rightClassLinked.trans hChallenge,
    candidate.capacityDifference.probabilitiesDiffer⟩

theorem E16_ArtifactNotAdaptability
    (complete : CompleteAdaptabilityStatus S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      statusPolicy claimRef)
    (artifact : ArtifactEvidenceFor S probabilityPolicy ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy claimRef) :
    ¬ CoherentAdaptabilityHolds S probabilityPolicy ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
      claimRef := by
  rintro ⟨_, _, hCase⟩
  rcases hCase with ⟨_, _, hNoArtifact, _⟩
  rcases complete.branchValid with _ | _ | _ | _ | _ | _ | _ | _ <;>
    exact hNoArtifact artifact

theorem E16_FlatNoAdaptability
    (complete : CompleteAdaptabilityStatus S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      statusPolicy claimRef)
    (flat : FlatEvidenceFor S probabilityPolicy ctx packagePolicy basePolicy
      protocolPolicy familyPolicy claimRef) :
    ¬ CoherentAdaptabilityHolds S probabilityPolicy ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
      claimRef := by
  rintro ⟨_, _, hCase⟩
  rcases hCase with ⟨_, _, _, hNoFlat, _⟩
  rcases complete.branchValid with _ | _ | _ | _ | _ | _ | _ | _ <;>
    exact hNoFlat flat

theorem E16_FlattenableNotAdaptability
    (complete : CompleteAdaptabilityStatus S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      statusPolicy claimRef)
    (flattenable : FlattenableEvidenceFor S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      claimRef) :
    ¬ CoherentAdaptabilityHolds S probabilityPolicy ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
      claimRef := by
  rintro ⟨_, _, hCase⟩
  rcases hCase with ⟨_, _, _, _, hNoFlattenable, _⟩
  rcases complete.branchValid with _ | _ | _ | _ | _ | _ | _ | _ <;>
    exact hNoFlattenable flattenable

theorem E16_CurrentizableIsLegibleSlack
    (record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy)
    (hOccurrence : AdaptabilityStatusOccurrenceFor
      (probabilityPolicy := probabilityPolicy) S ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
      claimRef record)
    (hStatus : record.status = AdaptabilityStatus.currentizable_slack)
    (hCase : CurrentizableSlackCase S probabilityPolicy ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
      claimRef record)
    (complete : CompleteAdaptabilityStatus S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      statusPolicy claimRef) :
    CurrentizableSlackHolds S probabilityPolicy ctx e15ctx e15policies
        packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
        claimRef ∧
      ¬ CoherentAdaptabilityHolds S probabilityPolicy ctx e15ctx e15policies
        packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
        claimRef := by
  refine ⟨⟨record, hOccurrence, hCase⟩, ?_⟩
  rintro ⟨other, hOtherOccurrence, hOtherCase⟩
  have hOtherStatus : other.status = AdaptabilityStatus.coherent_adaptability :=
    hOtherCase.2.2.2.2.2.2.2.1
  have hSame := complete.statusUnique record other hOccurrence hOtherOccurrence
  rw [hStatus, hOtherStatus] at hSame
  cases hSame

theorem E16_DissipativeNotAdaptability
    (complete : CompleteAdaptabilityStatus S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      statusPolicy claimRef)
    (dissipative : DissipativeEvidenceFor S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      claimRef) :
    ¬ CoherentAdaptabilityHolds S probabilityPolicy ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
      claimRef := by
  rintro ⟨_, _, hCase⟩
  rcases hCase with ⟨_, _, _, _, _, _, hNoDissipative, _⟩
  rcases complete.branchValid with _ | _ | _ | _ | _ | _ | _ | _ <;>
    exact hNoDissipative dissipative

theorem E16_BoundedPerturbationFailureRejected
    (candidate : RepairLedgerHolonomyCandidate S e15ctx e15policies ctx
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy)
    (candidateMatches : CandidateMatchesClaim S candidate claimRef)
    (boundPolicy : CarriedRecordPolicy S.T DeclaredPerturbationBoundRecord)
    (perturbationPolicy : CarriedRecordPolicy S.T
      (PerturbationTrialRecord candidate.carriedPair.package))
    (inventory : CompletePerturbationTrialInventory S ctx claimRef
      candidate.carriedPair.package boundPolicy perturbationPolicy)
    (failure : BoundedPerturbationFailureEvidence S candidate claimRef
      candidateMatches boundPolicy perturbationPolicy inventory)
    (record : AdaptabilityStatusRecord S ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy)
    (hOccurrence : AdaptabilityStatusOccurrenceFor
      (probabilityPolicy := probabilityPolicy) S ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
      claimRef record)
    (hStatus : record.status = AdaptabilityStatus.adaptability_rejected)
    (hNoSupport : ¬ SupportConfoundEvidenceFor S probabilityPolicy ctx claimRef)
    (hNoArtifact : ¬ ArtifactEvidenceFor S probabilityPolicy ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy claimRef)
    (hNoFlat : ¬ FlatEvidenceFor S probabilityPolicy ctx packagePolicy basePolicy
      protocolPolicy familyPolicy claimRef)
    (hNoFlattening : ¬ FlattenableEvidenceFor S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      claimRef)
    (hNoCurrentization : ¬ CurrentizableEvidenceFor S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      claimRef)
    (hNoDissipation : ¬ DissipativeEvidenceFor S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      claimRef)
    (hNoCoherent : ¬ CoherentAdaptabilityEvidenceFor S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      claimRef) :
    AdaptabilityRejectedHolds S probabilityPolicy ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
      claimRef := by
  have hRejectedEvidence : AdaptabilityRejectedEvidenceFor S probabilityPolicy ctx
      e15ctx e15policies packagePolicy basePolicy protocolPolicy familyPolicy
      bridgePolicy claimRef :=
    Or.inl ⟨candidate, candidateMatches, boundPolicy, perturbationPolicy,
      inventory, ⟨failure⟩⟩
  refine ⟨record, hOccurrence, ?_⟩
  exact ⟨hOccurrence, hNoSupport, hNoArtifact, hNoFlat, hNoFlattening,
    hNoCurrentization, hNoDissipation, hNoCoherent, hStatus, hRejectedEvidence⟩

theorem E16_SupportConfoundExcludesLowerPriority
    (confound : SupportConfoundEvidenceFor S probabilityPolicy ctx claimRef)
    (complete : CompleteAdaptabilityStatus S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      statusPolicy claimRef) :
    ¬ ArtifactHolds S probabilityPolicy ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef ∧
      ¬ FlatHolds S probabilityPolicy ctx e15ctx e15policies packagePolicy basePolicy
        protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef ∧
      ¬ FlattenableHolds S probabilityPolicy ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef ∧
      ¬ CurrentizableSlackHolds S probabilityPolicy ctx e15ctx e15policies
        packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
        claimRef ∧
      ¬ DissipativeHolds S probabilityPolicy ctx e15ctx e15policies packagePolicy
        basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef ∧
      ¬ CoherentAdaptabilityHolds S probabilityPolicy ctx e15ctx e15policies
        packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
        claimRef ∧
      ¬ AdaptabilityRejectedHolds S probabilityPolicy ctx e15ctx e15policies
        packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
        claimRef := by
  have hArtifact : ¬ ArtifactHolds S probabilityPolicy ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
      claimRef := by
    rintro ⟨_, _, hCase⟩
    exact hCase.2.1 confound
  have hFlat : ¬ FlatHolds S probabilityPolicy ctx e15ctx e15policies packagePolicy
      basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy claimRef := by
    rintro ⟨_, _, hCase⟩
    exact hCase.2.1 confound
  have hFlattenable : ¬ FlattenableHolds S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      statusPolicy claimRef := by
    rintro ⟨_, _, hCase⟩
    exact hCase.2.1 confound
  have hCurrentizable : ¬ CurrentizableSlackHolds S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      statusPolicy claimRef := by
    rintro ⟨_, _, hCase⟩
    exact hCase.2.1 confound
  have hDissipative : ¬ DissipativeHolds S probabilityPolicy ctx e15ctx e15policies
      packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy statusPolicy
      claimRef := by
    rintro ⟨_, _, hCase⟩
    exact hCase.2.1 confound
  have hCoherent : ¬ CoherentAdaptabilityHolds S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      statusPolicy claimRef := by
    rintro ⟨_, _, hCase⟩
    exact hCase.2.1 confound
  have hRejected : ¬ AdaptabilityRejectedHolds S probabilityPolicy ctx e15ctx
      e15policies packagePolicy basePolicy protocolPolicy familyPolicy bridgePolicy
      statusPolicy claimRef := by
    rintro ⟨_, _, hCase⟩
    exact hCase.2.1 confound
  rcases complete.branchValid with _ | _ | _ | _ | _ | _ | _ | _ <;>
    exact ⟨hArtifact, hFlat, hFlattenable, hCurrentizable, hDissipative,
      hCoherent, hRejected⟩

theorem E16_LoopAsymmetryAnchor
    {package : DeclaredRouteTransportPackage Support}
    {pair : RoutePairRecord package}
    (loopEvidence : LoopAnchoredRouteAsymmetry package pair) :
    ∃ q : PredictiveQuotient package.core pair.sourceInterface,
      predictiveLoopAction package.core loopEvidence.loop q ≠ q ∧
      predictiveToCurrent package.core
          (predictiveLoopAction package.core loopEvidence.loop q) =
        predictiveToCurrent package.core q := by
  exact loopAsymmetry_exhibits_movedPredictive_fixedCurrent package.core
    loopEvidence.loop loopEvidence.asymmetry

end Theorems

end

end SixBirdsFoundationsV
