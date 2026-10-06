import SixBirdsFoundationsV.Definitional.ESystem
import SixBirdsFoundationsV.Laws.E1Internalization
import SixBirdsIII.TopDownChannel

namespace SixBirdsFoundationsV

/-!
E10 cognitive-demarcation setup.

This setup layer mechanizes the carried package, repair-descent,
top-down-kernel-gate, intention, and goal vocabulary from the accepted E10
six-field normal form (`formalization/notes/examples/E10.md`).  The status
apparatus and E10 theorem statements are intentionally left to later
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

structure CognitiveChallengeClass where
  classId : Nat
  deriving DecidableEq, Repr

inductive AccessActionKind where
  | access
  | action
  deriving DecidableEq, Repr

structure CognitivePackageRecord where
  recordId : Nat
  packageValueId : Nat
  declaredClass : CognitiveChallengeClass
  deriving DecidableEq, Repr

structure PackageFormationRecord where
  recordId : Nat
  packageRecord : CognitivePackageRecord
  formedAt : Nat
  deriving DecidableEq, Repr

structure PackageInvocationRecord where
  recordId : Nat
  packageRecord : CognitivePackageRecord
  invokedAt : Nat
  challengeClass : CognitiveChallengeClass
  deriving DecidableEq, Repr

structure PackageQuotientRecord where
  recordId : Nat
  challengeClass : CognitiveChallengeClass
  deriving DecidableEq, Repr

structure DescentWitnessRecord where
  recordId : Nat
  beforeQuotient : PackageQuotientRecord
  afterQuotient : PackageQuotientRecord
  challengeClass : CognitiveChallengeClass
  deriving DecidableEq, Repr

structure KernelSupportRecord where
  recordId : Nat
  kind : AccessActionKind
  packageRecord : CognitivePackageRecord
  challengeClass : CognitiveChallengeClass
  supportId : Nat
  deriving DecidableEq, Repr

structure PackageInterventionRecord where
  recordId : Nat
  packageRecord : CognitivePackageRecord
  packageValueId : Nat
  interventionIndex : Nat
  deriving DecidableEq, Repr

structure MatchedControlRecord where
  recordId : Nat
  interventionA : PackageInterventionRecord
  interventionB : PackageInterventionRecord
  challengeClass : CognitiveChallengeClass
  deriving DecidableEq, Repr

structure DecodabilityReadoutRecord where
  recordId : Nat
  packageRecord : CognitivePackageRecord
  decodedClass : CognitiveChallengeClass
  deriving DecidableEq, Repr

structure ExogenousScheduleRecord where
  recordId : Nat
  challengeClass : CognitiveChallengeClass
  scheduleId : Nat
  deriving DecidableEq, Repr

structure StructuralPathRecord where
  recordId : Nat
  packageRecord : CognitivePackageRecord
  challengeClass : CognitiveChallengeClass
  channelRecord : SixBirdsIII.TopDownChannelRecord
  deriving Repr

structure TargetClassRecord where
  recordId : Nat
  challengeClass : CognitiveChallengeClass
  deriving DecidableEq, Repr

structure ActionSupportRestrictionRecord where
  recordId : Nat
  theta : CognitivePackageRecord
  targetClass : TargetClassRecord
  unrestrictedSupport : KernelSupportRecord
  restrictedSupport : KernelSupportRecord
  restrictionTime : Nat
  outcomeTime : Nat
  deriving DecidableEq, Repr

structure FutureProbeRecord where
  recordId : Nat
  targetClass : TargetClassRecord
  probeIndex : Nat
  deriving DecidableEq, Repr

structure TargetQuotientRecord where
  recordId : Nat
  theta : CognitivePackageRecord
  targetClass : TargetClassRecord
  quotientId : Nat
  deriving DecidableEq, Repr

structure RouteSubstitutionRecord where
  recordId : Nat
  routeIndex : Nat
  targetClass : TargetClassRecord
  deriving DecidableEq, Repr

structure RouteEvaluationRecord where
  recordId : Nat
  route : RouteSubstitutionRecord
  targetQuotient : TargetQuotientRecord
  beforeQuotient : PackageQuotientRecord
  afterQuotient : PackageQuotientRecord
  deriving DecidableEq, Repr

structure RewardProxyRecord where
  recordId : Nat
  theta : CognitivePackageRecord
  proxyValue : Rat
  deriving DecidableEq, Repr

structure CognitiveDemarcationClassifierContext where
  packageInstallsQuotient :
    CognitivePackageRecord -> PackageQuotientRecord ->
      PackageQuotientRecord -> Prop
  deltaNonempty :
    PackageQuotientRecord -> CognitiveChallengeClass -> Prop
  deltaStrictlyReducedBy :
    PackageQuotientRecord -> PackageQuotientRecord ->
      CognitiveChallengeClass -> Prop
  kernelSupportDiffers :
    KernelSupportRecord -> KernelSupportRecord -> Prop
  supportForIntervention :
    KernelSupportRecord -> PackageInterventionRecord -> Prop
  channelCertifiesKernelComparison :
    SixBirdsIII.TopDownChannelRecord -> MatchedControlRecord ->
      KernelSupportRecord -> KernelSupportRecord -> Prop
  decodesPackage :
    DecodabilityReadoutRecord -> CognitivePackageRecord ->
      CognitiveChallengeClass -> Prop
  scheduleExplainsKernelChange :
    ExogenousScheduleRecord -> KernelSupportRecord ->
      KernelSupportRecord -> Prop
  supportStrictSubset :
    KernelSupportRecord -> KernelSupportRecord -> Prop
  targetCoherentUnderProbe :
    TargetClassRecord -> FutureProbeRecord ->
      ActionSupportRestrictionRecord -> Prop
  approximateSupportRestriction :
    ActionSupportRestrictionRecord -> Prop
  routeEvaluationTargets :
    RouteEvaluationRecord -> RouteSubstitutionRecord ->
      TargetQuotientRecord -> Prop
  routeSelectionPersists :
    TargetQuotientRecord -> List RouteEvaluationRecord -> Prop
  rewardProxyExplainsSelection :
    RewardProxyRecord -> TargetQuotientRecord -> Prop

structure PackageCarriedProvenance
    (packagePolicy : CarriedRecordPolicy S.T CognitivePackageRecord)
    (formationPolicy : CarriedRecordPolicy S.T PackageFormationRecord)
    (invocationPolicy : CarriedRecordPolicy S.T PackageInvocationRecord)
    (package : CognitivePackageRecord) where
  formationRecord : PackageFormationRecord
  invocationRecord : PackageInvocationRecord
  formationLinked : formationRecord.packageRecord = package
  invocationLinked : invocationRecord.packageRecord = package
  packageCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt packagePolicy package n0 sourceTag generatedByS
          inScope ∧
        CarriedSource sourceTag generatedByS inScope
  formationCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt formationPolicy formationRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  invocationCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt invocationPolicy invocationRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  sameDeclaredClass : invocationRecord.challengeClass = package.declaredClass

structure CompletePackageProvenanceInventory
    (packagePolicy : CarriedRecordPolicy S.T CognitivePackageRecord)
    (formationPolicy : CarriedRecordPolicy S.T PackageFormationRecord)
    (invocationPolicy : CarriedRecordPolicy S.T PackageInvocationRecord)
    (package : CognitivePackageRecord) where
  declaredProvenancePairs :
    List (PackageFormationRecord × PackageInvocationRecord)
  completeForPackage :
    ∀ provenance :
      PackageCarriedProvenance S packagePolicy formationPolicy
        invocationPolicy package,
      (provenance.formationRecord, provenance.invocationRecord) ∈
        declaredProvenancePairs

def NoCarriedPackageProvenanceFor
    {packagePolicy : CarriedRecordPolicy S.T CognitivePackageRecord}
    {formationPolicy : CarriedRecordPolicy S.T PackageFormationRecord}
    {invocationPolicy : CarriedRecordPolicy S.T PackageInvocationRecord}
    {package : CognitivePackageRecord}
    (inventory :
      CompletePackageProvenanceInventory S packagePolicy formationPolicy
        invocationPolicy package) : Prop :=
  inventory.declaredProvenancePairs = []

structure PackageRepairDescent
    (ctx : CognitiveDemarcationClassifierContext)
    (package : CognitivePackageRecord)
    (challengeClass : CognitiveChallengeClass) where
  witnessRecord : DescentWitnessRecord
  qBefore : PackageQuotientRecord
  qAfter : PackageQuotientRecord
  witnessLinked :
    witnessRecord.beforeQuotient = qBefore ∧
    witnessRecord.afterQuotient = qAfter ∧
    witnessRecord.challengeClass = challengeClass
  packageClassLinked : package.declaredClass = challengeClass
  beforeFailureNonempty : ctx.deltaNonempty qBefore challengeClass
  afterQuotientInstalledByPackage :
    ctx.packageInstallsQuotient package qBefore qAfter
  strictReduction : ctx.deltaStrictlyReducedBy qBefore qAfter challengeClass

structure CompletePackageRepairInventory
    (ctx : CognitiveDemarcationClassifierContext)
    (package : CognitivePackageRecord)
    (challengeClass : CognitiveChallengeClass) where
  declaredDescentRecords : List DescentWitnessRecord
  completeForPackage :
    ∀ descent : PackageRepairDescent ctx package challengeClass,
      descent.witnessRecord ∈ declaredDescentRecords

def NoPackageRepairDescentFor
    {ctx : CognitiveDemarcationClassifierContext}
    {package : CognitivePackageRecord}
    {challengeClass : CognitiveChallengeClass}
    (inventory :
      CompletePackageRepairInventory ctx package challengeClass) : Prop :=
  inventory.declaredDescentRecords = []

structure TopDownKernelGateCertified
    (ctx : CognitiveDemarcationClassifierContext)
    (interventionPolicy :
      CarriedRecordPolicy S.T PackageInterventionRecord)
    (matchedControlPolicy :
      CarriedRecordPolicy S.T MatchedControlRecord)
    (supportPolicy : CarriedRecordPolicy S.T KernelSupportRecord)
    (channelPolicy :
      CarriedRecordPolicy S.T SixBirdsIII.TopDownChannelRecord)
    (package : CognitivePackageRecord)
    (challengeClass : CognitiveChallengeClass) where
  channelRecord : SixBirdsIII.TopDownChannelRecord
  intervention1 : PackageInterventionRecord
  intervention2 : PackageInterventionRecord
  matchedControls : MatchedControlRecord
  support1 : KernelSupportRecord
  support2 : KernelSupportRecord
  interventionsLinked :
    intervention1.packageRecord = package ∧
    intervention2.packageRecord = package ∧
    matchedControls.interventionA = intervention1 ∧
    matchedControls.interventionB = intervention2
  intervention1Carried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt interventionPolicy intervention1 n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  intervention2Carried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt interventionPolicy intervention2 n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  matchedControlsCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt matchedControlPolicy matchedControls n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  support1Carried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt supportPolicy support1 n0 sourceTag generatedByS
          inScope ∧
        CarriedSource sourceTag generatedByS inScope
  support2Carried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt supportPolicy support2 n0 sourceTag generatedByS
          inScope ∧
        CarriedSource sourceTag generatedByS inScope
  channelCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt channelPolicy channelRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  distinctCarriedValues :
    intervention1.packageValueId ≠ intervention2.packageValueId
  sameChallengeClass :
    support1.challengeClass = challengeClass ∧
    support2.challengeClass = challengeClass ∧
    matchedControls.challengeClass = challengeClass
  supportsLinkedToValues :
    support1.packageRecord = package ∧ support2.packageRecord = package
  support1ForIntervention1 :
    ctx.supportForIntervention support1 intervention1
  support2ForIntervention2 :
    ctx.supportForIntervention support2 intervention2
  channelCertifiesThisComparison :
    ctx.channelCertifiesKernelComparison channelRecord matchedControls
      support1 support2
  atLeastTwoInterventions :
    intervention1.interventionIndex ≠ intervention2.interventionIndex
  acceptedTopDownChannel :
    SixBirdsIII.TopDownChannelAcceptedBool channelRecord = true
  notMerelyStructural :
    SixBirdsIII.TopDownChannelClaimStatus channelRecord =
      SixBirdsIII.ClaimStatus.accepted
  supportDifference : ctx.kernelSupportDiffers support1 support2

structure CompleteKernelGateInventory
    (ctx : CognitiveDemarcationClassifierContext)
    (interventionPolicy :
      CarriedRecordPolicy S.T PackageInterventionRecord)
    (matchedControlPolicy :
      CarriedRecordPolicy S.T MatchedControlRecord)
    (supportPolicy : CarriedRecordPolicy S.T KernelSupportRecord)
    (channelPolicy :
      CarriedRecordPolicy S.T SixBirdsIII.TopDownChannelRecord)
    (package : CognitivePackageRecord)
    (challengeClass : CognitiveChallengeClass) where
  declaredAcceptedChannels : List SixBirdsIII.TopDownChannelRecord
  completeForClaim :
    ∀ gate :
      TopDownKernelGateCertified S ctx interventionPolicy
        matchedControlPolicy supportPolicy channelPolicy
        package challengeClass,
      gate.channelRecord ∈ declaredAcceptedChannels

def NoAcceptedTopDownGateFor
    {ctx : CognitiveDemarcationClassifierContext}
    {interventionPolicy :
      CarriedRecordPolicy S.T PackageInterventionRecord}
    {matchedControlPolicy :
      CarriedRecordPolicy S.T MatchedControlRecord}
    {supportPolicy : CarriedRecordPolicy S.T KernelSupportRecord}
    {channelPolicy :
      CarriedRecordPolicy S.T SixBirdsIII.TopDownChannelRecord}
    {package : CognitivePackageRecord}
    {challengeClass : CognitiveChallengeClass}
    (inventory :
      CompleteKernelGateInventory S ctx interventionPolicy
        matchedControlPolicy supportPolicy channelPolicy package
        challengeClass) : Prop :=
  inventory.declaredAcceptedChannels = []

structure StructuralPathOnlyWitness
    (ctx : CognitiveDemarcationClassifierContext)
    (package : CognitivePackageRecord)
    (challengeClass : CognitiveChallengeClass) where
  pathRecord : StructuralPathRecord
  support1 : KernelSupportRecord
  support2 : KernelSupportRecord
  linked :
    pathRecord.packageRecord = package ∧
    pathRecord.challengeClass = challengeClass ∧
    support1.packageRecord = package ∧
    support2.packageRecord = package ∧
    support1.challengeClass = challengeClass ∧
    support2.challengeClass = challengeClass
  structuralDown : SixBirdsIII.StructDown pathRecord.channelRecord
  channelBlocked :
    SixBirdsIII.TopDownChannelClaimStatus pathRecord.channelRecord =
      SixBirdsIII.ClaimStatus.blocked
  supportDifference : ctx.kernelSupportDiffers support1 support2

structure ScheduleTrapWitness
    (ctx : CognitiveDemarcationClassifierContext)
    (package : CognitivePackageRecord)
    (challengeClass : CognitiveChallengeClass)
    (gateInventory :
      CompleteKernelGateInventory S ctx interventionPolicy
        matchedControlPolicy supportPolicy channelPolicy package
        challengeClass) where
  scheduleRecord : ExogenousScheduleRecord
  supportBefore : KernelSupportRecord
  supportAfter : KernelSupportRecord
  scheduleClassLinked : scheduleRecord.challengeClass = challengeClass
  supportsLinked :
    supportBefore.packageRecord = package ∧
    supportAfter.packageRecord = package ∧
    supportBefore.challengeClass = challengeClass ∧
    supportAfter.challengeClass = challengeClass
  exogenousScheduleExplains :
    ctx.scheduleExplainsKernelChange scheduleRecord supportBefore supportAfter
  noAcceptedTopDownGate : NoAcceptedTopDownGateFor S gateInventory

structure DecodableCorrelateEvidence
    (ctx : CognitiveDemarcationClassifierContext)
    (package : CognitivePackageRecord)
    (challengeClass : CognitiveChallengeClass)
    (gateInventory :
      CompleteKernelGateInventory S ctx interventionPolicy
        matchedControlPolicy supportPolicy channelPolicy package
        challengeClass) where
  readout : DecodabilityReadoutRecord
  readoutLinked :
    readout.packageRecord = package ∧ readout.decodedClass = challengeClass
  decodedByTheorist : ctx.decodesPackage readout package challengeClass
  gatingAblated : NoAcceptedTopDownGateFor S gateInventory

structure ScaffoldingEvidence
    (ctx : CognitiveDemarcationClassifierContext)
    (packagePolicy : CarriedRecordPolicy S.T CognitivePackageRecord)
    (formationPolicy : CarriedRecordPolicy S.T PackageFormationRecord)
    (invocationPolicy : CarriedRecordPolicy S.T PackageInvocationRecord)
    (package : CognitivePackageRecord)
    (provenanceInventory :
      CompletePackageProvenanceInventory S packagePolicy formationPolicy
        invocationPolicy package)
    (challengeClass : CognitiveChallengeClass) where
  scheduleRecord : Option ExogenousScheduleRecord
  packageClassLinked : package.declaredClass = challengeClass
  missingProvenance : NoCarriedPackageProvenanceFor S provenanceInventory

structure CognitivePackageEvidence
    (ctx : CognitiveDemarcationClassifierContext)
    (interventionPolicy :
      CarriedRecordPolicy S.T PackageInterventionRecord)
    (matchedControlPolicy :
      CarriedRecordPolicy S.T MatchedControlRecord)
    (supportPolicy : CarriedRecordPolicy S.T KernelSupportRecord)
    (channelPolicy :
      CarriedRecordPolicy S.T SixBirdsIII.TopDownChannelRecord)
    (packagePolicy : CarriedRecordPolicy S.T CognitivePackageRecord)
    (formationPolicy : CarriedRecordPolicy S.T PackageFormationRecord)
    (invocationPolicy : CarriedRecordPolicy S.T PackageInvocationRecord)
    (package : CognitivePackageRecord)
    (challengeClass : CognitiveChallengeClass) where
  repair : PackageRepairDescent ctx package challengeClass
  differenceMaking :
    TopDownKernelGateCertified S ctx interventionPolicy
      matchedControlPolicy supportPolicy channelPolicy package challengeClass
  provenance :
    PackageCarriedProvenance S packagePolicy formationPolicy
      invocationPolicy package

structure RepairWithoutGateDefect
    (ctx : CognitiveDemarcationClassifierContext)
    (package : CognitivePackageRecord)
    (challengeClass : CognitiveChallengeClass)
    (gateInventory :
      CompleteKernelGateInventory S ctx interventionPolicy
        matchedControlPolicy supportPolicy channelPolicy package
        challengeClass) where
  repair : PackageRepairDescent ctx package challengeClass
  noAcceptedGate : NoAcceptedTopDownGateFor S gateInventory

structure GateWithoutRepairDefect
    (ctx : CognitiveDemarcationClassifierContext)
    (package : CognitivePackageRecord)
    (challengeClass : CognitiveChallengeClass)
    (repairInventory :
      CompletePackageRepairInventory ctx package challengeClass) where
  gate :
    TopDownKernelGateCertified S ctx interventionPolicy
      matchedControlPolicy supportPolicy channelPolicy package challengeClass
  noRepairDescent : NoPackageRepairDescentFor repairInventory

structure SupportRestrictionInAdvance
    (ctx : CognitiveDemarcationClassifierContext)
    (restrictionPolicy :
      CarriedRecordPolicy S.T ActionSupportRestrictionRecord)
    (supportPolicy : CarriedRecordPolicy S.T KernelSupportRecord)
    (theta : CognitivePackageRecord)
    (targetClass : TargetClassRecord) where
  restrictionRecord : ActionSupportRestrictionRecord
  linked :
    restrictionRecord.theta = theta ∧
    restrictionRecord.targetClass = targetClass
  actionKind :
    restrictionRecord.unrestrictedSupport.kind = AccessActionKind.action ∧
    restrictionRecord.restrictedSupport.kind = AccessActionKind.action
  beforeOutcome : restrictionRecord.restrictionTime < restrictionRecord.outcomeTime
  restrictionCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt restrictionPolicy restrictionRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  unrestrictedSupportCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt supportPolicy restrictionRecord.unrestrictedSupport
          n0 sourceTag generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  restrictedSupportCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt supportPolicy restrictionRecord.restrictedSupport n0
          sourceTag generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  strictSupportRestriction :
    ctx.supportStrictSubset restrictionRecord.restrictedSupport
      restrictionRecord.unrestrictedSupport

structure TargetCoherenceUnderFutureProbes
    (ctx : CognitiveDemarcationClassifierContext)
    (futureProbePolicy : CarriedRecordPolicy S.T FutureProbeRecord)
    (theta : CognitivePackageRecord)
    (targetClass : TargetClassRecord)
    (restriction : ActionSupportRestrictionRecord) where
  declaredFutureProbes : List FutureProbeRecord
  nonemptyProbes : declaredFutureProbes.length > 0
  probesLinked :
    ∀ probe : FutureProbeRecord, probe ∈ declaredFutureProbes ->
      probe.targetClass = targetClass
  probesCarried :
    ∀ probe : FutureProbeRecord, probe ∈ declaredFutureProbes ->
      ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
        ∃ generatedByS : Bool, ∃ inScope : Bool,
          CarriedRecordAt futureProbePolicy probe n0 sourceTag
            generatedByS inScope ∧
          CarriedSource sourceTag generatedByS inScope
  coherent :
    ∀ probe : FutureProbeRecord, probe ∈ declaredFutureProbes ->
      ctx.targetCoherentUnderProbe targetClass probe restriction

structure IntentionEvidence
    (ctx : CognitiveDemarcationClassifierContext)
    (interventionPolicy :
      CarriedRecordPolicy S.T PackageInterventionRecord)
    (matchedControlPolicy :
      CarriedRecordPolicy S.T MatchedControlRecord)
    (supportPolicy : CarriedRecordPolicy S.T KernelSupportRecord)
    (channelPolicy :
      CarriedRecordPolicy S.T SixBirdsIII.TopDownChannelRecord)
    (packagePolicy : CarriedRecordPolicy S.T CognitivePackageRecord)
    (formationPolicy : CarriedRecordPolicy S.T PackageFormationRecord)
    (invocationPolicy : CarriedRecordPolicy S.T PackageInvocationRecord)
    (restrictionPolicy :
      CarriedRecordPolicy S.T ActionSupportRestrictionRecord)
    (futureProbePolicy : CarriedRecordPolicy S.T FutureProbeRecord)
    (theta : CognitivePackageRecord)
    (targetClass : TargetClassRecord) where
  provenance :
    PackageCarriedProvenance S packagePolicy formationPolicy
      invocationPolicy theta
  topDownRestriction :
    TopDownKernelGateCertified S ctx interventionPolicy
      matchedControlPolicy supportPolicy channelPolicy
      theta targetClass.challengeClass
  restriction :
    SupportRestrictionInAdvance S ctx restrictionPolicy supportPolicy
      theta targetClass
  certifiedRestrictionLinked :
    topDownRestriction.support1 =
      restriction.restrictionRecord.unrestrictedSupport ∧
    topDownRestriction.support2 =
      restriction.restrictionRecord.restrictedSupport
  targetCoherence :
    TargetCoherenceUnderFutureProbes S ctx futureProbePolicy theta
      targetClass restriction.restrictionRecord

structure PostHocIntentionWitness
    (ctx : CognitiveDemarcationClassifierContext)
    (restrictionPolicy :
      CarriedRecordPolicy S.T ActionSupportRestrictionRecord)
    (theta : CognitivePackageRecord)
    (targetClass : TargetClassRecord) where
  restrictionRecord : ActionSupportRestrictionRecord
  linked :
    restrictionRecord.theta = theta ∧
    restrictionRecord.targetClass = targetClass
  restrictionCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt restrictionPolicy restrictionRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  notBeforeOutcome :
    ¬ restrictionRecord.restrictionTime < restrictionRecord.outcomeTime

structure ApproximateSupportRestrictionDefect
    (ctx : CognitiveDemarcationClassifierContext)
    (restrictionPolicy :
      CarriedRecordPolicy S.T ActionSupportRestrictionRecord)
    (theta : CognitivePackageRecord)
    (targetClass : TargetClassRecord) where
  restrictionRecord : ActionSupportRestrictionRecord
  linked :
    restrictionRecord.theta = theta ∧
    restrictionRecord.targetClass = targetClass
  restrictionCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt restrictionPolicy restrictionRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  approximateOnly : ctx.approximateSupportRestriction restrictionRecord
  exactStrictSubsetMissing :
    ¬ ctx.supportStrictSubset restrictionRecord.restrictedSupport
      restrictionRecord.unrestrictedSupport

structure TargetIncoherentRestrictionDefect
    (ctx : CognitiveDemarcationClassifierContext)
    (restrictionPolicy :
      CarriedRecordPolicy S.T ActionSupportRestrictionRecord)
    (futureProbePolicy : CarriedRecordPolicy S.T FutureProbeRecord)
    (theta : CognitivePackageRecord)
    (targetClass : TargetClassRecord) where
  restrictionRecord : ActionSupportRestrictionRecord
  failedProbe : FutureProbeRecord
  linked :
    restrictionRecord.theta = theta ∧
    restrictionRecord.targetClass = targetClass ∧
    failedProbe.targetClass = targetClass
  restrictionCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt restrictionPolicy restrictionRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  failedProbeCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt futureProbePolicy failedProbe n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  incoherent :
    ¬ ctx.targetCoherentUnderProbe targetClass failedProbe restrictionRecord

structure GoalTargetSelection
    (targetQuotientPolicy :
      CarriedRecordPolicy S.T TargetQuotientRecord)
    (theta : CognitivePackageRecord)
    (targetClass : TargetClassRecord) where
  targetQuotient : TargetQuotientRecord
  selectedByTheta :
    targetQuotient.theta = theta ∧ targetQuotient.targetClass = targetClass
  targetQuotientCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt targetQuotientPolicy targetQuotient n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

structure RouteSubstitutionEvaluation
    (ctx : CognitiveDemarcationClassifierContext)
    (targetQuotientPolicy :
      CarriedRecordPolicy S.T TargetQuotientRecord)
    (routePolicy : CarriedRecordPolicy S.T RouteSubstitutionRecord)
    (evaluationPolicy : CarriedRecordPolicy S.T RouteEvaluationRecord)
    (selection : GoalTargetSelection S targetQuotientPolicy theta targetClass)
    (route : RouteSubstitutionRecord) where
  evaluation : RouteEvaluationRecord
  routeLinked :
    evaluation.route = route ∧
    ctx.routeEvaluationTargets evaluation route selection.targetQuotient
  routeTargetLinked : route.targetClass = targetClass
  routeCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt routePolicy route n0 sourceTag generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  evaluationCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt evaluationPolicy evaluation n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  deltaEvaluatedAgainstTarget :
    ctx.deltaNonempty evaluation.beforeQuotient
      route.targetClass.challengeClass ∨
    ctx.deltaStrictlyReducedBy evaluation.beforeQuotient
      evaluation.afterQuotient route.targetClass.challengeClass

structure RouteSubstitutionPersistenceCertified
    (ctx : CognitiveDemarcationClassifierContext)
    (targetQuotientPolicy :
      CarriedRecordPolicy S.T TargetQuotientRecord)
    (routePolicy : CarriedRecordPolicy S.T RouteSubstitutionRecord)
    (evaluationPolicy : CarriedRecordPolicy S.T RouteEvaluationRecord)
    (theta : CognitivePackageRecord)
    (targetClass : TargetClassRecord)
    (selection : GoalTargetSelection S targetQuotientPolicy theta targetClass) where
  routes : List RouteSubstitutionRecord
  routeEvaluations : List RouteEvaluationRecord
  atLeastTwoDistinctRoutes :
    ∃ route1 route2 : RouteSubstitutionRecord,
      route1 ∈ routes ∧ route2 ∈ routes ∧ route1 ≠ route2
  routesCarried :
    ∀ route : RouteSubstitutionRecord, route ∈ routes ->
      ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
        ∃ generatedByS : Bool, ∃ inScope : Bool,
          CarriedRecordAt routePolicy route n0 sourceTag generatedByS
            inScope ∧
          CarriedSource sourceTag generatedByS inScope
  everyRouteEvaluated :
    ∀ route : RouteSubstitutionRecord, route ∈ routes ->
      ∃ evaluationWitness :
        RouteSubstitutionEvaluation S ctx targetQuotientPolicy routePolicy
          evaluationPolicy selection route,
        evaluationWitness.evaluation ∈ routeEvaluations
  evaluationsCarried :
    ∀ eval : RouteEvaluationRecord, eval ∈ routeEvaluations ->
      ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
        ∃ generatedByS : Bool, ∃ inScope : Bool,
          CarriedRecordAt evaluationPolicy eval n0 sourceTag generatedByS
            inScope ∧
          CarriedSource sourceTag generatedByS inScope
  persists : ctx.routeSelectionPersists selection.targetQuotient routeEvaluations

structure CompleteRoutePersistenceInventory
    (ctx : CognitiveDemarcationClassifierContext)
    (targetQuotientPolicy :
      CarriedRecordPolicy S.T TargetQuotientRecord)
    (routePolicy : CarriedRecordPolicy S.T RouteSubstitutionRecord)
    (evaluationPolicy : CarriedRecordPolicy S.T RouteEvaluationRecord)
    (theta : CognitivePackageRecord)
    (targetClass : TargetClassRecord)
    (selection : GoalTargetSelection S targetQuotientPolicy theta targetClass) where
  declaredPersistenceEvaluations : List RouteEvaluationRecord
  completeForSelection :
    ∀ persistence :
      RouteSubstitutionPersistenceCertified S ctx targetQuotientPolicy
        routePolicy evaluationPolicy theta targetClass selection,
      persistence.routeEvaluations = declaredPersistenceEvaluations

def NoRoutePersistenceFor
    {ctx : CognitiveDemarcationClassifierContext}
    {targetQuotientPolicy :
      CarriedRecordPolicy S.T TargetQuotientRecord}
    {routePolicy : CarriedRecordPolicy S.T RouteSubstitutionRecord}
    {evaluationPolicy : CarriedRecordPolicy S.T RouteEvaluationRecord}
    {theta : CognitivePackageRecord}
    {targetClass : TargetClassRecord}
    {selection : GoalTargetSelection S targetQuotientPolicy theta targetClass}
    (inventory :
      CompleteRoutePersistenceInventory S ctx targetQuotientPolicy
        routePolicy evaluationPolicy theta targetClass selection) : Prop :=
  inventory.declaredPersistenceEvaluations = []

structure GoalEvidence
    (ctx : CognitiveDemarcationClassifierContext)
    (interventionPolicy :
      CarriedRecordPolicy S.T PackageInterventionRecord)
    (matchedControlPolicy :
      CarriedRecordPolicy S.T MatchedControlRecord)
    (supportPolicy : CarriedRecordPolicy S.T KernelSupportRecord)
    (channelPolicy :
      CarriedRecordPolicy S.T SixBirdsIII.TopDownChannelRecord)
    (packagePolicy : CarriedRecordPolicy S.T CognitivePackageRecord)
    (formationPolicy : CarriedRecordPolicy S.T PackageFormationRecord)
    (invocationPolicy : CarriedRecordPolicy S.T PackageInvocationRecord)
    (targetQuotientPolicy :
      CarriedRecordPolicy S.T TargetQuotientRecord)
    (routePolicy : CarriedRecordPolicy S.T RouteSubstitutionRecord)
    (evaluationPolicy : CarriedRecordPolicy S.T RouteEvaluationRecord)
    (theta : CognitivePackageRecord)
    (targetClass : TargetClassRecord) where
  provenance :
    PackageCarriedProvenance S packagePolicy formationPolicy
      invocationPolicy theta
  topDownOrientation :
    TopDownKernelGateCertified S ctx interventionPolicy
      matchedControlPolicy supportPolicy channelPolicy
      theta targetClass.challengeClass
  selection : GoalTargetSelection S targetQuotientPolicy theta targetClass
  routePersistence :
    RouteSubstitutionPersistenceCertified S ctx targetQuotientPolicy
      routePolicy evaluationPolicy theta targetClass selection

structure RewardProxyOnlyWitness
    (ctx : CognitiveDemarcationClassifierContext)
    (rewardProxyPolicy : CarriedRecordPolicy S.T RewardProxyRecord)
    (targetQuotientPolicy :
      CarriedRecordPolicy S.T TargetQuotientRecord)
    (routePolicy : CarriedRecordPolicy S.T RouteSubstitutionRecord)
    (evaluationPolicy : CarriedRecordPolicy S.T RouteEvaluationRecord)
    (theta : CognitivePackageRecord)
    (targetClass : TargetClassRecord)
    (selection : GoalTargetSelection S targetQuotientPolicy theta targetClass)
    (routePersistenceInventory :
      CompleteRoutePersistenceInventory S ctx targetQuotientPolicy
        routePolicy evaluationPolicy theta targetClass selection) where
  rewardProxy : RewardProxyRecord
  proxyLinked : rewardProxy.theta = theta
  rewardProxyCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt rewardProxyPolicy rewardProxy n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  proxyExplains :
    ctx.rewardProxyExplainsSelection rewardProxy selection.targetQuotient
  noRoutePersistence :
    NoRoutePersistenceFor S routePersistenceInventory

structure RouteUnstableWitness
    (ctx : CognitiveDemarcationClassifierContext)
    (routePolicy : CarriedRecordPolicy S.T RouteSubstitutionRecord)
    (evaluationPolicy : CarriedRecordPolicy S.T RouteEvaluationRecord)
    (targetQuotientPolicy :
      CarriedRecordPolicy S.T TargetQuotientRecord)
    (theta : CognitivePackageRecord)
    (targetClass : TargetClassRecord) where
  selection : GoalTargetSelection S targetQuotientPolicy theta targetClass
  routes : List RouteSubstitutionRecord
  routeEvaluations : List RouteEvaluationRecord
  atLeastTwoDistinctRoutes :
    ∃ route1 route2 : RouteSubstitutionRecord,
      route1 ∈ routes ∧ route2 ∈ routes ∧ route1 ≠ route2
  everyRouteEvaluated :
    ∀ route : RouteSubstitutionRecord, route ∈ routes ->
      ∃ evaluationWitness :
        RouteSubstitutionEvaluation S ctx targetQuotientPolicy routePolicy
          evaluationPolicy selection route,
        evaluationWitness.evaluation ∈ routeEvaluations
  routesCarried :
    ∀ route : RouteSubstitutionRecord, route ∈ routes ->
      ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
        ∃ generatedByS : Bool, ∃ inScope : Bool,
          CarriedRecordAt routePolicy route n0 sourceTag generatedByS
            inScope ∧
          CarriedSource sourceTag generatedByS inScope
  evaluationsCarried :
    ∀ eval : RouteEvaluationRecord, eval ∈ routeEvaluations ->
      ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
        ∃ generatedByS : Bool, ∃ inScope : Bool,
          CarriedRecordAt evaluationPolicy eval n0 sourceTag generatedByS
            inScope ∧
          CarriedSource sourceTag generatedByS inScope
  persistenceFails :
    ¬ ctx.routeSelectionPersists selection.targetQuotient routeEvaluations

end Setup

section StatusApparatus

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)

inductive CognitiveStatus where
  | schedule_trap
  | scaffolding
  | structural_path_only
  | decodable_correlate
  | repair_without_gate
  | gate_without_repair
  | cognitive
  | non_cognitive
  deriving DecidableEq, Repr

structure CognitiveStatusRecord where
  recordId : Nat
  status : CognitiveStatus
  packageRecord : Option CognitivePackageRecord
  challengeClass : Option CognitiveChallengeClass
  formationRecord : Option PackageFormationRecord
  invocationRecord : Option PackageInvocationRecord
  descentRecord : Option DescentWitnessRecord
  channelRecord : Option SixBirdsIII.TopDownChannelRecord
  decodabilityRecord : Option DecodabilityReadoutRecord
  scheduleRecord : Option ExogenousScheduleRecord
  structuralPathRecord : Option StructuralPathRecord
  deriving Repr

inductive CognitiveClaimRef where
  | package (package : CognitivePackageRecord)
      (challengeClass : CognitiveChallengeClass)
  deriving DecidableEq, Repr

inductive IntentionStatus where
  | post_hoc_intention
  | approximate_support_defect
  | target_incoherent_restriction
  | intention
  | not_intention
  deriving DecidableEq, Repr

structure IntentionStatusRecord where
  recordId : Nat
  status : IntentionStatus
  theta : Option CognitivePackageRecord
  targetClass : Option TargetClassRecord
  restrictionRecord : Option ActionSupportRestrictionRecord
  channelRecord : Option SixBirdsIII.TopDownChannelRecord
  deriving Repr

inductive IntentionClaimRef where
  | theta (theta : CognitivePackageRecord) (targetClass : TargetClassRecord)
  deriving DecidableEq, Repr

inductive GoalStatus where
  | reward_proxy_only
  | route_unstable
  | goal
  | not_goal
  deriving DecidableEq, Repr

structure GoalStatusRecord where
  recordId : Nat
  status : GoalStatus
  theta : Option CognitivePackageRecord
  targetClass : Option TargetClassRecord
  targetQuotient : Option TargetQuotientRecord
  rewardProxy : Option RewardProxyRecord
  routeEvaluations : List RouteEvaluationRecord
  deriving DecidableEq, Repr

inductive GoalClaimRef where
  | theta (theta : CognitivePackageRecord) (targetClass : TargetClassRecord)
  deriving DecidableEq, Repr

structure CognitiveEvidencePolicies where
  packagePolicy : CarriedRecordPolicy S.T CognitivePackageRecord
  formationPolicy : CarriedRecordPolicy S.T PackageFormationRecord
  invocationPolicy : CarriedRecordPolicy S.T PackageInvocationRecord
  interventionPolicy : CarriedRecordPolicy S.T PackageInterventionRecord
  matchedControlPolicy : CarriedRecordPolicy S.T MatchedControlRecord
  supportPolicy : CarriedRecordPolicy S.T KernelSupportRecord
  channelPolicy :
    CarriedRecordPolicy S.T SixBirdsIII.TopDownChannelRecord
  restrictionPolicy :
    CarriedRecordPolicy S.T ActionSupportRestrictionRecord
  futureProbePolicy : CarriedRecordPolicy S.T FutureProbeRecord
  targetQuotientPolicy : CarriedRecordPolicy S.T TargetQuotientRecord
  routePolicy : CarriedRecordPolicy S.T RouteSubstitutionRecord
  evaluationPolicy : CarriedRecordPolicy S.T RouteEvaluationRecord
  rewardProxyPolicy : CarriedRecordPolicy S.T RewardProxyRecord
  cognitiveStatusPolicy : CarriedRecordPolicy S.T CognitiveStatusRecord
  intentionStatusPolicy : CarriedRecordPolicy S.T IntentionStatusRecord
  goalStatusPolicy : CarriedRecordPolicy S.T GoalStatusRecord

def CognitiveStatusRecordMatchesClaim
    (claimRef : CognitiveClaimRef)
    (record : CognitiveStatusRecord) : Prop :=
  match claimRef with
  | CognitiveClaimRef.package package challengeClass =>
      record.packageRecord = some package ∧
        record.challengeClass = some challengeClass

def CognitiveStatusOccurrenceFor
    (policies : CognitiveEvidencePolicies S)
    (claimRef : CognitiveClaimRef)
    (record : CognitiveStatusRecord) : Prop :=
  CognitiveStatusRecordMatchesClaim claimRef record ∧
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.cognitiveStatusPolicy record n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

def IntentionStatusRecordMatchesClaim
    (claimRef : IntentionClaimRef)
    (record : IntentionStatusRecord) : Prop :=
  match claimRef with
  | IntentionClaimRef.theta theta targetClass =>
      record.theta = some theta ∧ record.targetClass = some targetClass

def IntentionStatusOccurrenceFor
    (policies : CognitiveEvidencePolicies S)
    (claimRef : IntentionClaimRef)
    (record : IntentionStatusRecord) : Prop :=
  IntentionStatusRecordMatchesClaim claimRef record ∧
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.intentionStatusPolicy record n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

def GoalStatusRecordMatchesClaim
    (claimRef : GoalClaimRef)
    (record : GoalStatusRecord) : Prop :=
  match claimRef with
  | GoalClaimRef.theta theta targetClass =>
      record.theta = some theta ∧ record.targetClass = some targetClass

def GoalStatusOccurrenceFor
    (policies : CognitiveEvidencePolicies S)
    (claimRef : GoalClaimRef)
    (record : GoalStatusRecord) : Prop :=
  GoalStatusRecordMatchesClaim claimRef record ∧
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.goalStatusPolicy record n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

def ScheduleTrapEvidenceFor
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) : Prop :=
  ∃ package challengeClass,
    claimRef = CognitiveClaimRef.package package challengeClass ∧
      ∃ gateInventory :
        CompleteKernelGateInventory S ctx policies.interventionPolicy
          policies.matchedControlPolicy policies.supportPolicy
          policies.channelPolicy package challengeClass,
        Nonempty
          (ScheduleTrapWitness S ctx package challengeClass gateInventory)

def ScaffoldingEvidenceFor
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) : Prop :=
  ∃ package challengeClass,
    claimRef = CognitiveClaimRef.package package challengeClass ∧
      ∃ provenanceInventory :
        CompletePackageProvenanceInventory S policies.packagePolicy
          policies.formationPolicy policies.invocationPolicy package,
        Nonempty
          (ScaffoldingEvidence S ctx policies.packagePolicy
            policies.formationPolicy policies.invocationPolicy package
            provenanceInventory challengeClass)

def StructuralPathOnlyEvidenceFor
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) : Prop :=
  ∃ package challengeClass,
    claimRef = CognitiveClaimRef.package package challengeClass ∧
      Nonempty (StructuralPathOnlyWitness ctx package challengeClass)

def DecodableCorrelateEvidenceFor
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) : Prop :=
  ∃ package challengeClass,
    claimRef = CognitiveClaimRef.package package challengeClass ∧
      ∃ gateInventory :
        CompleteKernelGateInventory S ctx policies.interventionPolicy
          policies.matchedControlPolicy policies.supportPolicy
          policies.channelPolicy package challengeClass,
        Nonempty
          (DecodableCorrelateEvidence S ctx package challengeClass
            gateInventory)

def RepairWithoutGateEvidenceFor
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) : Prop :=
  ∃ package challengeClass,
    claimRef = CognitiveClaimRef.package package challengeClass ∧
      ∃ gateInventory :
        CompleteKernelGateInventory S ctx policies.interventionPolicy
          policies.matchedControlPolicy policies.supportPolicy
          policies.channelPolicy package challengeClass,
        Nonempty
          (RepairWithoutGateDefect S ctx package challengeClass
            gateInventory)

def GateWithoutRepairEvidenceFor
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) : Prop :=
  ∃ package challengeClass,
    claimRef = CognitiveClaimRef.package package challengeClass ∧
      ∃ repairInventory :
        CompletePackageRepairInventory ctx package challengeClass,
        Nonempty
          (GateWithoutRepairDefect S ctx package challengeClass
            repairInventory)

def CognitiveEvidenceFor
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) : Prop :=
  ∃ package challengeClass,
    claimRef = CognitiveClaimRef.package package challengeClass ∧
      Nonempty
        (CognitivePackageEvidence S ctx policies.interventionPolicy
          policies.matchedControlPolicy policies.supportPolicy
          policies.channelPolicy policies.packagePolicy
          policies.formationPolicy policies.invocationPolicy package
          challengeClass)

def PostHocIntentionEvidenceFor
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef) : Prop :=
  ∃ theta targetClass,
    claimRef = IntentionClaimRef.theta theta targetClass ∧
      Nonempty
        (PostHocIntentionWitness S ctx policies.restrictionPolicy theta
          targetClass)

def ApproximateSupportDefectEvidenceFor
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef) : Prop :=
  ∃ theta targetClass,
    claimRef = IntentionClaimRef.theta theta targetClass ∧
      Nonempty
        (ApproximateSupportRestrictionDefect S ctx
          policies.restrictionPolicy theta targetClass)

def TargetIncoherentRestrictionEvidenceFor
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef) : Prop :=
  ∃ theta targetClass,
    claimRef = IntentionClaimRef.theta theta targetClass ∧
      Nonempty
        (TargetIncoherentRestrictionDefect S ctx policies.restrictionPolicy
          policies.futureProbePolicy theta targetClass)

def IntentionEvidenceFor
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef) : Prop :=
  ∃ theta targetClass,
    claimRef = IntentionClaimRef.theta theta targetClass ∧
      Nonempty
        (IntentionEvidence S ctx policies.interventionPolicy
          policies.matchedControlPolicy policies.supportPolicy
          policies.channelPolicy policies.packagePolicy
          policies.formationPolicy policies.invocationPolicy
          policies.restrictionPolicy policies.futureProbePolicy theta
          targetClass)

def RewardProxyOnlyEvidenceFor
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : GoalClaimRef) : Prop :=
  ∃ theta targetClass,
    claimRef = GoalClaimRef.theta theta targetClass ∧
      ∃ selection :
        GoalTargetSelection S policies.targetQuotientPolicy theta
          targetClass,
        ∃ routePersistenceInventory :
          CompleteRoutePersistenceInventory S ctx
            policies.targetQuotientPolicy policies.routePolicy
            policies.evaluationPolicy theta targetClass selection,
          Nonempty
            (RewardProxyOnlyWitness S ctx policies.rewardProxyPolicy
              policies.targetQuotientPolicy policies.routePolicy
              policies.evaluationPolicy theta targetClass selection
              routePersistenceInventory)

def RouteUnstableEvidenceFor
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : GoalClaimRef) : Prop :=
  ∃ theta targetClass,
    claimRef = GoalClaimRef.theta theta targetClass ∧
      Nonempty
        (RouteUnstableWitness S ctx policies.routePolicy
          policies.evaluationPolicy policies.targetQuotientPolicy theta
          targetClass)

def GoalEvidenceFor
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : GoalClaimRef) : Prop :=
  ∃ theta targetClass,
    claimRef = GoalClaimRef.theta theta targetClass ∧
      Nonempty
        (GoalEvidence S ctx policies.interventionPolicy
          policies.matchedControlPolicy policies.supportPolicy
          policies.channelPolicy policies.packagePolicy
          policies.formationPolicy policies.invocationPolicy
          policies.targetQuotientPolicy policies.routePolicy
          policies.evaluationPolicy theta targetClass)

def ScheduleTrapCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef)
    (record : CognitiveStatusRecord) : Prop :=
  CognitiveStatusOccurrenceFor S policies claimRef record ∧
    record.status = CognitiveStatus.schedule_trap ∧
    ∃ package challengeClass,
      claimRef = CognitiveClaimRef.package package challengeClass ∧
        ∃ gateInventory :
          CompleteKernelGateInventory S ctx policies.interventionPolicy
            policies.matchedControlPolicy policies.supportPolicy
            policies.channelPolicy package challengeClass,
          ∃ trap : ScheduleTrapWitness S ctx package challengeClass
            gateInventory,
            record.packageRecord = some package ∧
              record.challengeClass = some challengeClass ∧
              record.scheduleRecord = some trap.scheduleRecord

def ScaffoldingCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef)
    (record : CognitiveStatusRecord) : Prop :=
  CognitiveStatusOccurrenceFor S policies claimRef record ∧
    record.status = CognitiveStatus.scaffolding ∧
    ¬ ScheduleTrapEvidenceFor S policies ctx claimRef ∧
    ∃ package challengeClass,
      claimRef = CognitiveClaimRef.package package challengeClass ∧
        ∃ provenanceInventory :
          CompletePackageProvenanceInventory S policies.packagePolicy
            policies.formationPolicy policies.invocationPolicy package,
          ∃ scaffold :
            ScaffoldingEvidence S ctx policies.packagePolicy
              policies.formationPolicy policies.invocationPolicy package
              provenanceInventory challengeClass,
            record.packageRecord = some package ∧
              record.challengeClass = some challengeClass ∧
              record.scheduleRecord = scaffold.scheduleRecord

def StructuralPathOnlyCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef)
    (record : CognitiveStatusRecord) : Prop :=
  CognitiveStatusOccurrenceFor S policies claimRef record ∧
    record.status = CognitiveStatus.structural_path_only ∧
    ¬ ScheduleTrapEvidenceFor S policies ctx claimRef ∧
    ¬ ScaffoldingEvidenceFor S policies ctx claimRef ∧
    ∃ package challengeClass,
      claimRef = CognitiveClaimRef.package package challengeClass ∧
        ∃ structural : StructuralPathOnlyWitness ctx package challengeClass,
          record.structuralPathRecord = some structural.pathRecord

def DecodableCorrelateCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef)
    (record : CognitiveStatusRecord) : Prop :=
  CognitiveStatusOccurrenceFor S policies claimRef record ∧
    record.status = CognitiveStatus.decodable_correlate ∧
    ¬ ScheduleTrapEvidenceFor S policies ctx claimRef ∧
    ¬ ScaffoldingEvidenceFor S policies ctx claimRef ∧
    ¬ StructuralPathOnlyEvidenceFor ctx claimRef ∧
    ∃ package challengeClass,
      claimRef = CognitiveClaimRef.package package challengeClass ∧
        ∃ gateInventory :
          CompleteKernelGateInventory S ctx policies.interventionPolicy
            policies.matchedControlPolicy policies.supportPolicy
            policies.channelPolicy package challengeClass,
          ∃ correlate : DecodableCorrelateEvidence S ctx package
            challengeClass gateInventory,
            record.decodabilityRecord = some correlate.readout

def RepairWithoutGateCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef)
    (record : CognitiveStatusRecord) : Prop :=
  CognitiveStatusOccurrenceFor S policies claimRef record ∧
    record.status = CognitiveStatus.repair_without_gate ∧
    ¬ ScheduleTrapEvidenceFor S policies ctx claimRef ∧
    ¬ ScaffoldingEvidenceFor S policies ctx claimRef ∧
    ¬ StructuralPathOnlyEvidenceFor ctx claimRef ∧
    ¬ DecodableCorrelateEvidenceFor S policies ctx claimRef ∧
    ∃ package challengeClass,
      claimRef = CognitiveClaimRef.package package challengeClass ∧
        ∃ gateInventory :
          CompleteKernelGateInventory S ctx policies.interventionPolicy
            policies.matchedControlPolicy policies.supportPolicy
            policies.channelPolicy package challengeClass,
          ∃ defect : RepairWithoutGateDefect S ctx package challengeClass
            gateInventory,
            record.descentRecord = some defect.repair.witnessRecord

def GateWithoutRepairCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef)
    (record : CognitiveStatusRecord) : Prop :=
  CognitiveStatusOccurrenceFor S policies claimRef record ∧
    record.status = CognitiveStatus.gate_without_repair ∧
    ¬ ScheduleTrapEvidenceFor S policies ctx claimRef ∧
    ¬ ScaffoldingEvidenceFor S policies ctx claimRef ∧
    ¬ StructuralPathOnlyEvidenceFor ctx claimRef ∧
    ¬ DecodableCorrelateEvidenceFor S policies ctx claimRef ∧
    ¬ RepairWithoutGateEvidenceFor S policies ctx claimRef ∧
    ∃ package challengeClass,
      claimRef = CognitiveClaimRef.package package challengeClass ∧
        ∃ repairInventory :
          CompletePackageRepairInventory ctx package challengeClass,
          ∃ defect : GateWithoutRepairDefect S ctx package challengeClass
            repairInventory,
            record.channelRecord =
              some ((defect.gate
                (interventionPolicy := policies.interventionPolicy)
                (matchedControlPolicy := policies.matchedControlPolicy)
                (supportPolicy := policies.supportPolicy)
                (channelPolicy := policies.channelPolicy)).channelRecord)

def CognitiveCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef)
    (record : CognitiveStatusRecord) : Prop :=
  CognitiveStatusOccurrenceFor S policies claimRef record ∧
    record.status = CognitiveStatus.cognitive ∧
    ¬ ScheduleTrapEvidenceFor S policies ctx claimRef ∧
    ¬ ScaffoldingEvidenceFor S policies ctx claimRef ∧
    ¬ StructuralPathOnlyEvidenceFor ctx claimRef ∧
    ¬ DecodableCorrelateEvidenceFor S policies ctx claimRef ∧
    ¬ RepairWithoutGateEvidenceFor S policies ctx claimRef ∧
    ¬ GateWithoutRepairEvidenceFor S ctx claimRef ∧
    ∃ package challengeClass,
      claimRef = CognitiveClaimRef.package package challengeClass ∧
        ∃ evidence :
          CognitivePackageEvidence S ctx policies.interventionPolicy
            policies.matchedControlPolicy policies.supportPolicy
            policies.channelPolicy policies.packagePolicy
            policies.formationPolicy policies.invocationPolicy package
            challengeClass,
          record.descentRecord = some evidence.repair.witnessRecord ∧
            record.channelRecord =
              some evidence.differenceMaking.channelRecord

def NonCognitiveCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef)
    (record : CognitiveStatusRecord) : Prop :=
  CognitiveStatusOccurrenceFor S policies claimRef record ∧
    record.status = CognitiveStatus.non_cognitive ∧
    ¬ ScheduleTrapEvidenceFor S policies ctx claimRef ∧
    ¬ ScaffoldingEvidenceFor S policies ctx claimRef ∧
    ¬ StructuralPathOnlyEvidenceFor ctx claimRef ∧
    ¬ DecodableCorrelateEvidenceFor S policies ctx claimRef ∧
    ¬ RepairWithoutGateEvidenceFor S policies ctx claimRef ∧
    ¬ GateWithoutRepairEvidenceFor S ctx claimRef ∧
    ¬ CognitiveEvidenceFor S policies ctx claimRef

def ScheduleTrapHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) : Prop :=
  ∃ record : CognitiveStatusRecord,
    CognitiveStatusOccurrenceFor S policies claimRef record ∧
      record.status = CognitiveStatus.schedule_trap ∧
      ScheduleTrapCase S policies ctx claimRef record

def ScaffoldingHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) : Prop :=
  ∃ record : CognitiveStatusRecord,
    CognitiveStatusOccurrenceFor S policies claimRef record ∧
      record.status = CognitiveStatus.scaffolding ∧
      ScaffoldingCase S policies ctx claimRef record

def StructuralPathOnlyHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) : Prop :=
  ∃ record : CognitiveStatusRecord,
    CognitiveStatusOccurrenceFor S policies claimRef record ∧
      record.status = CognitiveStatus.structural_path_only ∧
      StructuralPathOnlyCase S policies ctx claimRef record

def DecodableCorrelateHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) : Prop :=
  ∃ record : CognitiveStatusRecord,
    CognitiveStatusOccurrenceFor S policies claimRef record ∧
      record.status = CognitiveStatus.decodable_correlate ∧
      DecodableCorrelateCase S policies ctx claimRef record

def RepairWithoutGateHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) : Prop :=
  ∃ record : CognitiveStatusRecord,
    CognitiveStatusOccurrenceFor S policies claimRef record ∧
      record.status = CognitiveStatus.repair_without_gate ∧
      RepairWithoutGateCase S policies ctx claimRef record

def GateWithoutRepairHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) : Prop :=
  ∃ record : CognitiveStatusRecord,
    CognitiveStatusOccurrenceFor S policies claimRef record ∧
      record.status = CognitiveStatus.gate_without_repair ∧
      GateWithoutRepairCase S policies ctx claimRef record

def CognitiveHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) : Prop :=
  ∃ record : CognitiveStatusRecord,
    CognitiveStatusOccurrenceFor S policies claimRef record ∧
      record.status = CognitiveStatus.cognitive ∧
      CognitiveCase S policies ctx claimRef record

def NonCognitiveHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) : Prop :=
  ∃ record : CognitiveStatusRecord,
    CognitiveStatusOccurrenceFor S policies claimRef record ∧
      record.status = CognitiveStatus.non_cognitive ∧
      NonCognitiveCase S policies ctx claimRef record

structure CompleteCognitiveStatus
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef) where
  branchValid :
    ∃ record : CognitiveStatusRecord,
      ScheduleTrapCase S policies ctx claimRef record ∨
      ScaffoldingCase S policies ctx claimRef record ∨
      StructuralPathOnlyCase S policies ctx claimRef record ∨
      DecodableCorrelateCase S policies ctx claimRef record ∨
      RepairWithoutGateCase S policies ctx claimRef record ∨
      GateWithoutRepairCase S policies ctx claimRef record ∨
      CognitiveCase S policies ctx claimRef record ∨
      NonCognitiveCase S policies ctx claimRef record
  statusUnique :
    ∀ record1 record2 : CognitiveStatusRecord,
      CognitiveStatusOccurrenceFor S policies claimRef record1 ->
      CognitiveStatusOccurrenceFor S policies claimRef record2 ->
      record1.status = record2.status

def PostHocIntentionCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef)
    (record : IntentionStatusRecord) : Prop :=
  IntentionStatusOccurrenceFor S policies claimRef record ∧
    record.status = IntentionStatus.post_hoc_intention ∧
    ∃ theta targetClass,
      claimRef = IntentionClaimRef.theta theta targetClass ∧
        ∃ witness : PostHocIntentionWitness S ctx policies.restrictionPolicy
          theta targetClass,
          record.restrictionRecord = some witness.restrictionRecord

def ApproximateSupportDefectCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef)
    (record : IntentionStatusRecord) : Prop :=
  IntentionStatusOccurrenceFor S policies claimRef record ∧
    record.status = IntentionStatus.approximate_support_defect ∧
    ¬ PostHocIntentionEvidenceFor S policies ctx claimRef ∧
    ∃ theta targetClass,
      claimRef = IntentionClaimRef.theta theta targetClass ∧
        ∃ defect : ApproximateSupportRestrictionDefect S ctx
          policies.restrictionPolicy theta targetClass,
          record.restrictionRecord = some defect.restrictionRecord

def TargetIncoherentRestrictionCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef)
    (record : IntentionStatusRecord) : Prop :=
  IntentionStatusOccurrenceFor S policies claimRef record ∧
    record.status = IntentionStatus.target_incoherent_restriction ∧
    ¬ PostHocIntentionEvidenceFor S policies ctx claimRef ∧
    ¬ ApproximateSupportDefectEvidenceFor S policies ctx claimRef ∧
    ∃ theta targetClass,
      claimRef = IntentionClaimRef.theta theta targetClass ∧
        ∃ defect : TargetIncoherentRestrictionDefect S ctx
          policies.restrictionPolicy policies.futureProbePolicy theta
          targetClass,
          record.restrictionRecord = some defect.restrictionRecord

def IntentionCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef)
    (record : IntentionStatusRecord) : Prop :=
  IntentionStatusOccurrenceFor S policies claimRef record ∧
    record.status = IntentionStatus.intention ∧
    ¬ PostHocIntentionEvidenceFor S policies ctx claimRef ∧
    ¬ ApproximateSupportDefectEvidenceFor S policies ctx claimRef ∧
    ¬ TargetIncoherentRestrictionEvidenceFor S policies ctx claimRef ∧
    ∃ theta targetClass,
      claimRef = IntentionClaimRef.theta theta targetClass ∧
        ∃ evidence :
          IntentionEvidence S ctx policies.interventionPolicy
            policies.matchedControlPolicy policies.supportPolicy
            policies.channelPolicy policies.packagePolicy
            policies.formationPolicy policies.invocationPolicy
            policies.restrictionPolicy policies.futureProbePolicy theta
            targetClass,
          record.restrictionRecord =
            some evidence.restriction.restrictionRecord ∧
            record.channelRecord =
              some evidence.topDownRestriction.channelRecord

def NotIntentionCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef)
    (record : IntentionStatusRecord) : Prop :=
  IntentionStatusOccurrenceFor S policies claimRef record ∧
    record.status = IntentionStatus.not_intention ∧
    ¬ PostHocIntentionEvidenceFor S policies ctx claimRef ∧
    ¬ ApproximateSupportDefectEvidenceFor S policies ctx claimRef ∧
    ¬ TargetIncoherentRestrictionEvidenceFor S policies ctx claimRef ∧
    ¬ IntentionEvidenceFor S policies ctx claimRef

def PostHocIntentionHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef) : Prop :=
  ∃ record : IntentionStatusRecord,
    IntentionStatusOccurrenceFor S policies claimRef record ∧
      record.status = IntentionStatus.post_hoc_intention ∧
      PostHocIntentionCase S policies ctx claimRef record

def ApproximateSupportDefectHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef) : Prop :=
  ∃ record : IntentionStatusRecord,
    IntentionStatusOccurrenceFor S policies claimRef record ∧
      record.status = IntentionStatus.approximate_support_defect ∧
      ApproximateSupportDefectCase S policies ctx claimRef record

def TargetIncoherentRestrictionHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef) : Prop :=
  ∃ record : IntentionStatusRecord,
    IntentionStatusOccurrenceFor S policies claimRef record ∧
      record.status = IntentionStatus.target_incoherent_restriction ∧
      TargetIncoherentRestrictionCase S policies ctx claimRef record

def IntentionHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef) : Prop :=
  ∃ record : IntentionStatusRecord,
    IntentionStatusOccurrenceFor S policies claimRef record ∧
      record.status = IntentionStatus.intention ∧
      IntentionCase S policies ctx claimRef record

def NotIntentionHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef) : Prop :=
  ∃ record : IntentionStatusRecord,
    IntentionStatusOccurrenceFor S policies claimRef record ∧
      record.status = IntentionStatus.not_intention ∧
      NotIntentionCase S policies ctx claimRef record

structure CompleteIntentionStatus
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef) where
  branchValid :
    ∃ record : IntentionStatusRecord,
      PostHocIntentionCase S policies ctx claimRef record ∨
      ApproximateSupportDefectCase S policies ctx claimRef record ∨
      TargetIncoherentRestrictionCase S policies ctx claimRef record ∨
      IntentionCase S policies ctx claimRef record ∨
      NotIntentionCase S policies ctx claimRef record
  statusUnique :
    ∀ record1 record2 : IntentionStatusRecord,
      IntentionStatusOccurrenceFor S policies claimRef record1 ->
      IntentionStatusOccurrenceFor S policies claimRef record2 ->
      record1.status = record2.status

def RewardProxyOnlyCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : GoalClaimRef)
    (record : GoalStatusRecord) : Prop :=
  GoalStatusOccurrenceFor S policies claimRef record ∧
    record.status = GoalStatus.reward_proxy_only ∧
    ∃ theta targetClass,
      claimRef = GoalClaimRef.theta theta targetClass ∧
        ∃ selection :
          GoalTargetSelection S policies.targetQuotientPolicy theta
            targetClass,
          ∃ routePersistenceInventory :
            CompleteRoutePersistenceInventory S ctx
              policies.targetQuotientPolicy policies.routePolicy
              policies.evaluationPolicy theta targetClass selection,
            ∃ witness :
              RewardProxyOnlyWitness S ctx policies.rewardProxyPolicy
                policies.targetQuotientPolicy policies.routePolicy
                policies.evaluationPolicy theta targetClass selection
                routePersistenceInventory,
              record.rewardProxy = some witness.rewardProxy

def RouteUnstableCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : GoalClaimRef)
    (record : GoalStatusRecord) : Prop :=
  GoalStatusOccurrenceFor S policies claimRef record ∧
    record.status = GoalStatus.route_unstable ∧
    ¬ RewardProxyOnlyEvidenceFor S policies ctx claimRef ∧
    ∃ theta targetClass,
      claimRef = GoalClaimRef.theta theta targetClass ∧
        ∃ witness :
          RouteUnstableWitness S ctx policies.routePolicy
            policies.evaluationPolicy policies.targetQuotientPolicy theta
            targetClass,
          record.targetQuotient = some witness.selection.targetQuotient ∧
            record.routeEvaluations = witness.routeEvaluations

def GoalCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : GoalClaimRef)
    (record : GoalStatusRecord) : Prop :=
  GoalStatusOccurrenceFor S policies claimRef record ∧
    record.status = GoalStatus.goal ∧
    ¬ RewardProxyOnlyEvidenceFor S policies ctx claimRef ∧
    ¬ RouteUnstableEvidenceFor S policies ctx claimRef ∧
    ∃ theta targetClass,
      claimRef = GoalClaimRef.theta theta targetClass ∧
        ∃ evidence :
          GoalEvidence S ctx policies.interventionPolicy
            policies.matchedControlPolicy policies.supportPolicy
            policies.channelPolicy policies.packagePolicy
            policies.formationPolicy policies.invocationPolicy
            policies.targetQuotientPolicy policies.routePolicy
            policies.evaluationPolicy theta targetClass,
          record.targetQuotient = some evidence.selection.targetQuotient ∧
            record.routeEvaluations =
              evidence.routePersistence.routeEvaluations

def NotGoalCase
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : GoalClaimRef)
    (record : GoalStatusRecord) : Prop :=
  GoalStatusOccurrenceFor S policies claimRef record ∧
    record.status = GoalStatus.not_goal ∧
    ¬ RewardProxyOnlyEvidenceFor S policies ctx claimRef ∧
    ¬ RouteUnstableEvidenceFor S policies ctx claimRef ∧
    ¬ GoalEvidenceFor S policies ctx claimRef

def RewardProxyOnlyHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : GoalClaimRef) : Prop :=
  ∃ record : GoalStatusRecord,
    GoalStatusOccurrenceFor S policies claimRef record ∧
      record.status = GoalStatus.reward_proxy_only ∧
      RewardProxyOnlyCase S policies ctx claimRef record

def RouteUnstableHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : GoalClaimRef) : Prop :=
  ∃ record : GoalStatusRecord,
    GoalStatusOccurrenceFor S policies claimRef record ∧
      record.status = GoalStatus.route_unstable ∧
      RouteUnstableCase S policies ctx claimRef record

def GoalHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : GoalClaimRef) : Prop :=
  ∃ record : GoalStatusRecord,
    GoalStatusOccurrenceFor S policies claimRef record ∧
      record.status = GoalStatus.goal ∧
      GoalCase S policies ctx claimRef record

def NotGoalHolds
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : GoalClaimRef) : Prop :=
  ∃ record : GoalStatusRecord,
    GoalStatusOccurrenceFor S policies claimRef record ∧
      record.status = GoalStatus.not_goal ∧
      NotGoalCase S policies ctx claimRef record

structure CompleteGoalStatus
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : GoalClaimRef) where
  branchValid :
    ∃ record : GoalStatusRecord,
      RewardProxyOnlyCase S policies ctx claimRef record ∨
      RouteUnstableCase S policies ctx claimRef record ∨
      GoalCase S policies ctx claimRef record ∨
      NotGoalCase S policies ctx claimRef record
  statusUnique :
    ∀ record1 record2 : GoalStatusRecord,
      GoalStatusOccurrenceFor S policies claimRef record1 ->
      GoalStatusOccurrenceFor S policies claimRef record2 ->
      record1.status = record2.status

end StatusApparatus

section Theorems

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord AuditRecord)

namespace E10

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
  | p1 :: p2 :: p3 :: p4 :: p5 :: [] =>
      (p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5) ∨
      (p2 ∧ ¬ p1 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5) ∨
      (p3 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p4 ∧ ¬ p5) ∨
      (p4 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p5) ∨
      (p5 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4)
  | p1 :: p2 :: p3 :: p4 :: [] =>
      (p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4) ∨
      (p2 ∧ ¬ p1 ∧ ¬ p3 ∧ ¬ p4) ∨
      (p3 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p4) ∨
      (p4 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3)
  | _ => False

end E10

theorem E10_CognitiveDemarcation
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef)
    (hComplete : CompleteCognitiveStatus S policies ctx claimRef) :
    E10.ExactlyOne
      [ScheduleTrapHolds S policies ctx claimRef,
       ScaffoldingHolds S policies ctx claimRef,
       StructuralPathOnlyHolds S policies ctx claimRef,
       DecodableCorrelateHolds S policies ctx claimRef,
       RepairWithoutGateHolds S policies ctx claimRef,
       GateWithoutRepairHolds S policies ctx claimRef,
       CognitiveHolds S policies ctx claimRef,
       NonCognitiveHolds S policies ctx claimRef] := by
  rcases hComplete.branchValid with ⟨record, hBranch⟩
  have hConflict :
      ∀ {record1 record2 : CognitiveStatusRecord}
        {status1 status2 : CognitiveStatus},
        CognitiveStatusOccurrenceFor S policies claimRef record1 ->
        CognitiveStatusOccurrenceFor S policies claimRef record2 ->
        record1.status = status1 ->
        record2.status = status2 ->
        status1 ≠ status2 ->
        False := by
    intro record1 record2 status1 status2 hOcc1 hOcc2 hStatus1 hStatus2 hNe
    have hEq := hComplete.statusUnique record1 record2 hOcc1 hOcc2
    rw [hStatus1, hStatus2] at hEq
    exact hNe hEq
  have hNotSchedule :
      ∀ {record : CognitiveStatusRecord} {status : CognitiveStatus},
        CognitiveStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ CognitiveStatus.schedule_trap ->
        ¬ ScheduleTrapHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotScaffolding :
      ∀ {record : CognitiveStatusRecord} {status : CognitiveStatus},
        CognitiveStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ CognitiveStatus.scaffolding ->
        ¬ ScaffoldingHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotStructural :
      ∀ {record : CognitiveStatusRecord} {status : CognitiveStatus},
        CognitiveStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ CognitiveStatus.structural_path_only ->
        ¬ StructuralPathOnlyHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotDecodable :
      ∀ {record : CognitiveStatusRecord} {status : CognitiveStatus},
        CognitiveStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ CognitiveStatus.decodable_correlate ->
        ¬ DecodableCorrelateHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotRepairWithoutGate :
      ∀ {record : CognitiveStatusRecord} {status : CognitiveStatus},
        CognitiveStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ CognitiveStatus.repair_without_gate ->
        ¬ RepairWithoutGateHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotGateWithoutRepair :
      ∀ {record : CognitiveStatusRecord} {status : CognitiveStatus},
        CognitiveStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ CognitiveStatus.gate_without_repair ->
        ¬ GateWithoutRepairHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotCognitive :
      ∀ {record : CognitiveStatusRecord} {status : CognitiveStatus},
        CognitiveStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ CognitiveStatus.cognitive ->
        ¬ CognitiveHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotNonCognitive :
      ∀ {record : CognitiveStatusRecord} {status : CognitiveStatus},
        CognitiveStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ CognitiveStatus.non_cognitive ->
        ¬ NonCognitiveHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  rcases hBranch with
    hSchedule | hScaffolding | hStructural | hDecodable |
      hRepairWithoutGate | hGateWithoutRepair | hCognitive | hNonCognitive
  · have hCase := hSchedule
    rcases hSchedule with ⟨hOcc, hStatus, _hEvidence⟩
    exact Or.inl
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotScaffolding hOcc hStatus (by decide),
        hNotStructural hOcc hStatus (by decide),
        hNotDecodable hOcc hStatus (by decide),
        hNotRepairWithoutGate hOcc hStatus (by decide),
        hNotGateWithoutRepair hOcc hStatus (by decide),
        hNotCognitive hOcc hStatus (by decide),
        hNotNonCognitive hOcc hStatus (by decide)⟩
  · have hCase := hScaffolding
    rcases hScaffolding with ⟨hOcc, hStatus, _hRest⟩
    exact Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotSchedule hOcc hStatus (by decide),
        hNotStructural hOcc hStatus (by decide),
        hNotDecodable hOcc hStatus (by decide),
        hNotRepairWithoutGate hOcc hStatus (by decide),
        hNotGateWithoutRepair hOcc hStatus (by decide),
        hNotCognitive hOcc hStatus (by decide),
        hNotNonCognitive hOcc hStatus (by decide)⟩
  · have hCase := hStructural
    rcases hStructural with ⟨hOcc, hStatus, _hRest⟩
    exact Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotSchedule hOcc hStatus (by decide),
        hNotScaffolding hOcc hStatus (by decide),
        hNotDecodable hOcc hStatus (by decide),
        hNotRepairWithoutGate hOcc hStatus (by decide),
        hNotGateWithoutRepair hOcc hStatus (by decide),
        hNotCognitive hOcc hStatus (by decide),
        hNotNonCognitive hOcc hStatus (by decide)⟩
  · have hCase := hDecodable
    rcases hDecodable with ⟨hOcc, hStatus, _hRest⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotSchedule hOcc hStatus (by decide),
        hNotScaffolding hOcc hStatus (by decide),
        hNotStructural hOcc hStatus (by decide),
        hNotRepairWithoutGate hOcc hStatus (by decide),
        hNotGateWithoutRepair hOcc hStatus (by decide),
        hNotCognitive hOcc hStatus (by decide),
        hNotNonCognitive hOcc hStatus (by decide)⟩
  · have hCase := hRepairWithoutGate
    rcases hRepairWithoutGate with ⟨hOcc, hStatus, _hRest⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotSchedule hOcc hStatus (by decide),
        hNotScaffolding hOcc hStatus (by decide),
        hNotStructural hOcc hStatus (by decide),
        hNotDecodable hOcc hStatus (by decide),
        hNotGateWithoutRepair hOcc hStatus (by decide),
        hNotCognitive hOcc hStatus (by decide),
        hNotNonCognitive hOcc hStatus (by decide)⟩
  · have hCase := hGateWithoutRepair
    rcases hGateWithoutRepair with ⟨hOcc, hStatus, _hRest⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotSchedule hOcc hStatus (by decide),
        hNotScaffolding hOcc hStatus (by decide),
        hNotStructural hOcc hStatus (by decide),
        hNotDecodable hOcc hStatus (by decide),
        hNotRepairWithoutGate hOcc hStatus (by decide),
        hNotCognitive hOcc hStatus (by decide),
        hNotNonCognitive hOcc hStatus (by decide)⟩
  · have hCase := hCognitive
    rcases hCognitive with ⟨hOcc, hStatus, _hRest⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotSchedule hOcc hStatus (by decide),
        hNotScaffolding hOcc hStatus (by decide),
        hNotStructural hOcc hStatus (by decide),
        hNotDecodable hOcc hStatus (by decide),
        hNotRepairWithoutGate hOcc hStatus (by decide),
        hNotGateWithoutRepair hOcc hStatus (by decide),
        hNotNonCognitive hOcc hStatus (by decide)⟩
  · have hCase := hNonCognitive
    rcases hNonCognitive with ⟨hOcc, hStatus, _hRest⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotSchedule hOcc hStatus (by decide),
        hNotScaffolding hOcc hStatus (by decide),
        hNotStructural hOcc hStatus (by decide),
        hNotDecodable hOcc hStatus (by decide),
        hNotRepairWithoutGate hOcc hStatus (by decide),
        hNotGateWithoutRepair hOcc hStatus (by decide),
        hNotCognitive hOcc hStatus (by decide)⟩

theorem E10_ScheduleTrapExcludesLowerPriority
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef)
    (hScheduleEvidence : ScheduleTrapEvidenceFor S policies ctx claimRef)
    (hComplete : CompleteCognitiveStatus S policies ctx claimRef) :
    ¬ ScaffoldingHolds S policies ctx claimRef ∧
      ¬ StructuralPathOnlyHolds S policies ctx claimRef ∧
      ¬ DecodableCorrelateHolds S policies ctx claimRef ∧
      ¬ RepairWithoutGateHolds S policies ctx claimRef ∧
      ¬ GateWithoutRepairHolds S policies ctx claimRef ∧
      ¬ CognitiveHolds S policies ctx claimRef ∧
      ¬ NonCognitiveHolds S policies ctx claimRef := by
  have hPartition :=
    E10_CognitiveDemarcation S policies ctx claimRef hComplete
  simp only [E10.ExactlyOne] at hPartition
  rcases hPartition with
    hSchedule | hScaffolding | hStructural | hDecodable |
      hRepairWithoutGate | hGateWithoutRepair | hCognitive | hNonCognitive
  · exact hSchedule.2
  · rcases hScaffolding.1 with
      ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, _hCaseStatus, hNoSchedule, _rest⟩
    exact (hNoSchedule hScheduleEvidence).elim
  · rcases hStructural.1 with
      ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, _hCaseStatus, hNoSchedule, _rest⟩
    exact (hNoSchedule hScheduleEvidence).elim
  · rcases hDecodable.1 with
      ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, _hCaseStatus, hNoSchedule, _rest⟩
    exact (hNoSchedule hScheduleEvidence).elim
  · rcases hRepairWithoutGate.1 with
      ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, _hCaseStatus, hNoSchedule, _rest⟩
    exact (hNoSchedule hScheduleEvidence).elim
  · rcases hGateWithoutRepair.1 with
      ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, _hCaseStatus, hNoSchedule, _rest⟩
    exact (hNoSchedule hScheduleEvidence).elim
  · rcases hCognitive.1 with
      ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, _hCaseStatus, hNoSchedule, _rest⟩
    exact (hNoSchedule hScheduleEvidence).elim
  · rcases hNonCognitive.1 with
      ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, _hCaseStatus, hNoSchedule, _rest⟩
    exact (hNoSchedule hScheduleEvidence).elim

theorem E10_DecodableCorrelate
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef)
    (hComplete : CompleteCognitiveStatus S policies ctx claimRef)
    (correlate : DecodableCorrelateHolds S policies ctx claimRef) :
    ¬ CognitiveHolds S policies ctx claimRef := by
  intro hCognitive
  rcases correlate with ⟨record1, hOcc1, hStatus1, _hCase1⟩
  rcases hCognitive with ⟨record2, hOcc2, hStatus2, _hCase2⟩
  have hEq := hComplete.statusUnique record1 record2 hOcc1 hOcc2
  rw [hStatus1, hStatus2] at hEq
  exact (by decide :
    CognitiveStatus.decodable_correlate ≠ CognitiveStatus.cognitive) hEq

theorem E10_ScheduleTrapNull
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : CognitiveClaimRef)
    (hComplete : CompleteCognitiveStatus S policies ctx claimRef)
    (trap : ScheduleTrapHolds S policies ctx claimRef) :
    ¬ CognitiveHolds S policies ctx claimRef := by
  intro hCognitive
  rcases trap with ⟨record1, hOcc1, hStatus1, _hCase1⟩
  rcases hCognitive with ⟨record2, hOcc2, hStatus2, _hCase2⟩
  have hEq := hComplete.statusUnique record1 record2 hOcc1 hOcc2
  rw [hStatus1, hStatus2] at hEq
  exact (by decide :
    CognitiveStatus.schedule_trap ≠ CognitiveStatus.cognitive) hEq

theorem E10_1_Intention
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef)
    (hComplete : CompleteIntentionStatus S policies ctx claimRef) :
    E10.ExactlyOne
      [PostHocIntentionHolds S policies ctx claimRef,
       ApproximateSupportDefectHolds S policies ctx claimRef,
       TargetIncoherentRestrictionHolds S policies ctx claimRef,
       IntentionHolds S policies ctx claimRef,
       NotIntentionHolds S policies ctx claimRef] := by
  rcases hComplete.branchValid with ⟨record, hBranch⟩
  have hConflict :
      ∀ {record1 record2 : IntentionStatusRecord}
        {status1 status2 : IntentionStatus},
        IntentionStatusOccurrenceFor S policies claimRef record1 ->
        IntentionStatusOccurrenceFor S policies claimRef record2 ->
        record1.status = status1 ->
        record2.status = status2 ->
        status1 ≠ status2 ->
        False := by
    intro record1 record2 status1 status2 hOcc1 hOcc2 hStatus1 hStatus2 hNe
    have hEq := hComplete.statusUnique record1 record2 hOcc1 hOcc2
    rw [hStatus1, hStatus2] at hEq
    exact hNe hEq
  have hNotPostHoc :
      ∀ {record : IntentionStatusRecord} {status : IntentionStatus},
        IntentionStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ IntentionStatus.post_hoc_intention ->
        ¬ PostHocIntentionHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotApprox :
      ∀ {record : IntentionStatusRecord} {status : IntentionStatus},
        IntentionStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ IntentionStatus.approximate_support_defect ->
        ¬ ApproximateSupportDefectHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotTargetIncoherent :
      ∀ {record : IntentionStatusRecord} {status : IntentionStatus},
        IntentionStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ IntentionStatus.target_incoherent_restriction ->
        ¬ TargetIncoherentRestrictionHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotIntention :
      ∀ {record : IntentionStatusRecord} {status : IntentionStatus},
        IntentionStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ IntentionStatus.intention ->
        ¬ IntentionHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotNotIntention :
      ∀ {record : IntentionStatusRecord} {status : IntentionStatus},
        IntentionStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ IntentionStatus.not_intention ->
        ¬ NotIntentionHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  rcases hBranch with
    hPostHoc | hApprox | hTargetIncoherent | hIntention | hNotIntentionCase
  · have hCase := hPostHoc
    rcases hPostHoc with ⟨hOcc, hStatus, _hEvidence⟩
    exact Or.inl
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotApprox hOcc hStatus (by decide),
        hNotTargetIncoherent hOcc hStatus (by decide),
        hNotIntention hOcc hStatus (by decide),
        hNotNotIntention hOcc hStatus (by decide)⟩
  · have hCase := hApprox
    rcases hApprox with ⟨hOcc, hStatus, _hRest⟩
    exact Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotPostHoc hOcc hStatus (by decide),
        hNotTargetIncoherent hOcc hStatus (by decide),
        hNotIntention hOcc hStatus (by decide),
        hNotNotIntention hOcc hStatus (by decide)⟩
  · have hCase := hTargetIncoherent
    rcases hTargetIncoherent with ⟨hOcc, hStatus, _hRest⟩
    exact Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotPostHoc hOcc hStatus (by decide),
        hNotApprox hOcc hStatus (by decide),
        hNotIntention hOcc hStatus (by decide),
        hNotNotIntention hOcc hStatus (by decide)⟩
  · have hCase := hIntention
    rcases hIntention with ⟨hOcc, hStatus, _hRest⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotPostHoc hOcc hStatus (by decide),
        hNotApprox hOcc hStatus (by decide),
        hNotTargetIncoherent hOcc hStatus (by decide),
        hNotNotIntention hOcc hStatus (by decide)⟩
  · have hCase := hNotIntentionCase
    rcases hNotIntentionCase with ⟨hOcc, hStatus, _hRest⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inr
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotPostHoc hOcc hStatus (by decide),
        hNotApprox hOcc hStatus (by decide),
        hNotTargetIncoherent hOcc hStatus (by decide),
        hNotIntention hOcc hStatus (by decide)⟩

theorem E10_1_PostHocIntentionExcludesLowerPriority
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef)
    (hPostHocEvidence :
      PostHocIntentionEvidenceFor S policies ctx claimRef)
    (hComplete : CompleteIntentionStatus S policies ctx claimRef) :
    ¬ ApproximateSupportDefectHolds S policies ctx claimRef ∧
      ¬ TargetIncoherentRestrictionHolds S policies ctx claimRef ∧
      ¬ IntentionHolds S policies ctx claimRef ∧
      ¬ NotIntentionHolds S policies ctx claimRef := by
  have hPartition := E10_1_Intention S policies ctx claimRef hComplete
  simp only [E10.ExactlyOne] at hPartition
  rcases hPartition with
    hPostHoc | hApprox | hTargetIncoherent | hIntention | hNotIntention
  · exact hPostHoc.2
  · rcases hApprox.1 with ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, _hCaseStatus, hNoPostHoc, _rest⟩
    exact (hNoPostHoc hPostHocEvidence).elim
  · rcases hTargetIncoherent.1 with
      ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, _hCaseStatus, hNoPostHoc, _rest⟩
    exact (hNoPostHoc hPostHocEvidence).elim
  · rcases hIntention.1 with ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, _hCaseStatus, hNoPostHoc, _rest⟩
    exact (hNoPostHoc hPostHocEvidence).elim
  · rcases hNotIntention.1 with
      ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, _hCaseStatus, hNoPostHoc, _rest⟩
    exact (hNoPostHoc hPostHocEvidence).elim

theorem E10_1_PostHocIntentionFalsifier
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : IntentionClaimRef)
    (hComplete : CompleteIntentionStatus S policies ctx claimRef)
    (postHoc : PostHocIntentionHolds S policies ctx claimRef) :
    ¬ IntentionHolds S policies ctx claimRef := by
  intro hIntention
  rcases postHoc with ⟨record1, hOcc1, hStatus1, _hCase1⟩
  rcases hIntention with ⟨record2, hOcc2, hStatus2, _hCase2⟩
  have hEq := hComplete.statusUnique record1 record2 hOcc1 hOcc2
  rw [hStatus1, hStatus2] at hEq
  exact (by decide :
    IntentionStatus.post_hoc_intention ≠ IntentionStatus.intention) hEq

theorem E10_2_Goal
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : GoalClaimRef)
    (hComplete : CompleteGoalStatus S policies ctx claimRef) :
    E10.ExactlyOne
      [RewardProxyOnlyHolds S policies ctx claimRef,
       RouteUnstableHolds S policies ctx claimRef,
       GoalHolds S policies ctx claimRef,
       NotGoalHolds S policies ctx claimRef] := by
  rcases hComplete.branchValid with ⟨record, hBranch⟩
  have hConflict :
      ∀ {record1 record2 : GoalStatusRecord}
        {status1 status2 : GoalStatus},
        GoalStatusOccurrenceFor S policies claimRef record1 ->
        GoalStatusOccurrenceFor S policies claimRef record2 ->
        record1.status = status1 ->
        record2.status = status2 ->
        status1 ≠ status2 ->
        False := by
    intro record1 record2 status1 status2 hOcc1 hOcc2 hStatus1 hStatus2 hNe
    have hEq := hComplete.statusUnique record1 record2 hOcc1 hOcc2
    rw [hStatus1, hStatus2] at hEq
    exact hNe hEq
  have hNotReward :
      ∀ {record : GoalStatusRecord} {status : GoalStatus},
        GoalStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ GoalStatus.reward_proxy_only ->
        ¬ RewardProxyOnlyHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotRoute :
      ∀ {record : GoalStatusRecord} {status : GoalStatus},
        GoalStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ GoalStatus.route_unstable ->
        ¬ RouteUnstableHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotGoal :
      ∀ {record : GoalStatusRecord} {status : GoalStatus},
        GoalStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ GoalStatus.goal ->
        ¬ GoalHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotNotGoal :
      ∀ {record : GoalStatusRecord} {status : GoalStatus},
        GoalStatusOccurrenceFor S policies claimRef record ->
        record.status = status ->
        status ≠ GoalStatus.not_goal ->
        ¬ NotGoalHolds S policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  rcases hBranch with hReward | hRoute | hGoal | hNotGoalCase
  · have hCase := hReward
    rcases hReward with ⟨hOcc, hStatus, _hEvidence⟩
    exact Or.inl
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotRoute hOcc hStatus (by decide),
        hNotGoal hOcc hStatus (by decide),
        hNotNotGoal hOcc hStatus (by decide)⟩
  · have hCase := hRoute
    rcases hRoute with ⟨hOcc, hStatus, _hRest⟩
    exact Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotReward hOcc hStatus (by decide),
        hNotGoal hOcc hStatus (by decide),
        hNotNotGoal hOcc hStatus (by decide)⟩
  · have hCase := hGoal
    rcases hGoal with ⟨hOcc, hStatus, _hRest⟩
    exact Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotReward hOcc hStatus (by decide),
        hNotRoute hOcc hStatus (by decide),
        hNotNotGoal hOcc hStatus (by decide)⟩
  · have hCase := hNotGoalCase
    rcases hNotGoalCase with ⟨hOcc, hStatus, _hRest⟩
    exact Or.inr <| Or.inr <| Or.inr
      ⟨⟨record, hOcc, hStatus, hCase⟩,
        hNotReward hOcc hStatus (by decide),
        hNotRoute hOcc hStatus (by decide),
        hNotGoal hOcc hStatus (by decide)⟩

theorem E10_2_RewardProxyOnlyExcludesLowerPriority
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : GoalClaimRef)
    (hRewardEvidence : RewardProxyOnlyEvidenceFor S policies ctx claimRef)
    (hComplete : CompleteGoalStatus S policies ctx claimRef) :
    ¬ RouteUnstableHolds S policies ctx claimRef ∧
      ¬ GoalHolds S policies ctx claimRef ∧
      ¬ NotGoalHolds S policies ctx claimRef := by
  have hPartition := E10_2_Goal S policies ctx claimRef hComplete
  simp only [E10.ExactlyOne] at hPartition
  rcases hPartition with hReward | hRoute | hGoal | hNotGoal
  · exact hReward.2
  · rcases hRoute.1 with ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, _hCaseStatus, hNoReward, _rest⟩
    exact (hNoReward hRewardEvidence).elim
  · rcases hGoal.1 with ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, _hCaseStatus, hNoReward, _rest⟩
    exact (hNoReward hRewardEvidence).elim
  · rcases hNotGoal.1 with ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, _hCaseStatus, hNoReward, _rest⟩
    exact (hNoReward hRewardEvidence).elim

theorem E10_2_RewardProxyNotGoal
    (policies : CognitiveEvidencePolicies S)
    (ctx : CognitiveDemarcationClassifierContext)
    (claimRef : GoalClaimRef)
    (hComplete : CompleteGoalStatus S policies ctx claimRef)
    (proxy : RewardProxyOnlyHolds S policies ctx claimRef) :
    ¬ GoalHolds S policies ctx claimRef := by
  intro hGoal
  rcases proxy with ⟨record1, hOcc1, hStatus1, _hCase1⟩
  rcases hGoal with ⟨record2, hOcc2, hStatus2, _hCase2⟩
  have hEq := hComplete.statusUnique record1 record2 hOcc1 hOcc2
  rw [hStatus1, hStatus2] at hEq
  exact (by decide :
    GoalStatus.reward_proxy_only ≠ GoalStatus.goal) hEq

end Theorems

end SixBirdsFoundationsV
