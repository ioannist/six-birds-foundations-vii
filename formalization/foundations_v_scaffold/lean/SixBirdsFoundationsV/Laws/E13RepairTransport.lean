import SixBirdsFoundationsV.Definitional.ESystem
import SixBirdsFoundationsV.Laws.E1Internalization

namespace SixBirdsFoundationsV

/-!
E13 repair-transport setup.

This setup layer mechanizes the two-carrier record vocabulary, paid bridge
discipline, same-class transport taxonomy, receiver-side Delta reduction,
communication/teaching/coercion/scaffolding evidence, and symbol reactivation
surface from the accepted E13 six-field normal form
(`formalization/notes/examples/E13.md`).  The status apparatus and E13 theorem
statements are intentionally left to later mechanization subsections.
-/

section Setup

variable {FDataA : Type uA} {RuleFamilyA : Type vA}
variable {ResidualFamilyA : Type wA} {AuditAccessDataA : Type xA}
variable {InstrumentRecordA : Type yA} {LedgerEntryA : Type yA'}
variable {DefectRecordA : Type yA''} {MovePayloadA : Type yA'''}
variable {MoveRecordA : Type yA''''} {AuditRecordA : Type yA'''''}

variable {FDataB : Type uB} {RuleFamilyB : Type vB}
variable {ResidualFamilyB : Type wB} {AuditAccessDataB : Type xB}
variable {InstrumentRecordB : Type yB} {LedgerEntryB : Type yB'}
variable {DefectRecordB : Type yB''} {MovePayloadB : Type yB'''}
variable {MoveRecordB : Type yB''''} {AuditRecordB : Type yB'''''}

variable (S_A : ESystem FDataA RuleFamilyA ResidualFamilyA AuditAccessDataA
  InstrumentRecordA LedgerEntryA DefectRecordA MovePayloadA MoveRecordA
  AuditRecordA)
variable (S_B : ESystem FDataB RuleFamilyB ResidualFamilyB AuditAccessDataB
  InstrumentRecordB LedgerEntryB DefectRecordB MovePayloadB MoveRecordB
  AuditRecordB)

inductive TransportClaimKind where
  | communication
  | teaching
  | symbol
  deriving DecidableEq, Repr

structure CarrierName where
  carrierId : Nat
  deriving DecidableEq, Repr

structure ChallengeClassRecord where
  challengeId : Nat
  taxonomyId : Nat
  deriving DecidableEq, Repr

structure RepairRoleRecord where
  roleId : Nat
  challengeClass : ChallengeClassRecord
  packageKind : Nat
  deriving DecidableEq, Repr

structure TransportTokenRecord where
  tokenId : Nat
  sourceCarrier : CarrierName
  targetCarrier : CarrierName
  emittedFor : ChallengeClassRecord
  sourcePackageRef : Nat
  deriving DecidableEq, Repr

structure SourceRepairPackageRecord where
  packageId : Nat
  sourceChallenge : ChallengeClassRecord
  roleRecord : RepairRoleRecord
  emittedToken : TransportTokenRecord
  deriving DecidableEq, Repr

structure TargetRepairRecord where
  targetRepairId : Nat
  receiptToken : TransportTokenRecord
  targetChallenge : ChallengeClassRecord
  inducedMove :
    RepairMove S_B.T MovePayloadB LedgerEntryB MoveRecordB S_B.moveRecordPolicy
  roleRecord : RepairRoleRecord

structure BridgeChannelRecord where
  channelId : Nat
  deriving DecidableEq, Repr

structure BridgeDefectRecord where
  defectId : Nat
  bridgeRef : Nat
  sourceLedgerEntry : LedgerEntryA
  targetLedgerEntry : LedgerEntryB

structure InterCarrierBridgeRecord where
  bridgeId : Nat
  sourceCarrier : CarrierName
  targetCarrier : CarrierName
  channelRecord : BridgeChannelRecord
  deriving DecidableEq, Repr

structure TaxonomyRecord where
  taxonomyId : Nat
  deriving DecidableEq, Repr

structure InterfaceAccessRecordA where
  accessId : Nat
  bridgeRef : InterCarrierBridgeRecord
  taxonomyRef : TaxonomyRecord

structure InterfaceAccessRecordB where
  accessId : Nat
  bridgeRef : InterCarrierBridgeRecord
  taxonomyRef : TaxonomyRecord

structure ProbeScheduleRecord where
  scheduleId : Nat
  deriving DecidableEq, Repr

structure ForceScheduleRecord where
  scheduleId : Nat
  deriving DecidableEq, Repr

structure FreeResponseOpportunityRecord where
  opportunityId : Nat
  deriving DecidableEq, Repr

structure FreeResponseCensusRecord where
  censusId : Nat
  deriving DecidableEq, Repr

structure ContextReadoutRecord where
  readoutId : Nat
  deriving DecidableEq, Repr

structure TransportContextRecord where
  contextId : Nat
  challengeClass : ChallengeClassRecord
  contextReadout : ContextReadoutRecord
  deriving DecidableEq, Repr

structure ContextFamilyRecord where
  familyId : Nat
  deriving DecidableEq, Repr

structure BRoleStateRecord where
  stateId : Nat
  activeRoles : List RepairRoleRecord
  contextFamilyRef : ContextFamilyRecord

/-- Shared bridge-discharge comparator for a classifier context. -/
structure BridgeDischargeComparator where
  discharges :
    BridgeDefectRecord (LedgerEntryA := LedgerEntryA)
      (LedgerEntryB := LedgerEntryB) ->
    LedgerEntryA -> LedgerEntryB -> Prop

structure BridgeDischargeCertificate
    (comparator : BridgeDischargeComparator
      (LedgerEntryA := LedgerEntryA) (LedgerEntryB := LedgerEntryB))
    (defectRecord :
      BridgeDefectRecord (LedgerEntryA := LedgerEntryA)
        (LedgerEntryB := LedgerEntryB)) where
  sourceEntry : LedgerEntryA
  targetEntry : LedgerEntryB
  sourceEntryLinked : defectRecord.sourceLedgerEntry = sourceEntry
  targetEntryLinked : defectRecord.targetLedgerEntry = targetEntry
  paidByLedgerData :
    comparator.discharges defectRecord sourceEntry targetEntry

structure BridgeDefectsPaid
    (comparator : BridgeDischargeComparator
      (LedgerEntryA := LedgerEntryA) (LedgerEntryB := LedgerEntryB))
    (bridge : InterCarrierBridgeRecord) where
  defectRecord :
    BridgeDefectRecord (LedgerEntryA := LedgerEntryA)
      (LedgerEntryB := LedgerEntryB)
  defectLinked : defectRecord.bridgeRef = bridge.bridgeId
  sourceEntryInLedger :
    defectRecord.sourceLedgerEntry ∈ S_A.Lambda_S.ledgerEntries
  targetEntryInLedger :
    defectRecord.targetLedgerEntry ∈ S_B.Lambda_S.ledgerEntries
  sourceEntryCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt S_A.Lambda_S.ledgerPolicy
          defectRecord.sourceLedgerEntry n0 sourceTag generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  targetEntryCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt S_B.Lambda_S.ledgerPolicy
          defectRecord.targetLedgerEntry n0 sourceTag generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  dischargeCertificate :
    BridgeDischargeCertificate comparator defectRecord

structure InterCarrierBridge
    (dischargeComparator : BridgeDischargeComparator
      (LedgerEntryA := LedgerEntryA) (LedgerEntryB := LedgerEntryB))
    (bridgePolicyA : CarriedRecordPolicy S_A.T InterCarrierBridgeRecord)
    (bridgePolicyB : CarriedRecordPolicy S_B.T InterCarrierBridgeRecord) where
  bridgeRecord : InterCarrierBridgeRecord
  sourceCarrierName : CarrierName
  targetCarrierName : CarrierName
  sourceMatches : bridgeRecord.sourceCarrier = sourceCarrierName
  targetMatches : bridgeRecord.targetCarrier = targetCarrierName
  bridgeCarriedByA :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt bridgePolicyA bridgeRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  bridgeCarriedByB :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt bridgePolicyB bridgeRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  defectsPaid : BridgeDefectsPaid S_A S_B dischargeComparator bridgeRecord

structure DeclaredTransportTaxonomy
    (taxonomyPolicy : CarriedRecordPolicy S_B.T TaxonomyRecord) where
  taxonomyRecord : TaxonomyRecord
  classRecords : List ChallengeClassRecord
  nonempty : classRecords.length > 0
  carried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt taxonomyPolicy taxonomyRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

structure SameTransportChallengeClass
    {taxonomyPolicy : CarriedRecordPolicy S_B.T TaxonomyRecord}
    (taxonomy : DeclaredTransportTaxonomy S_B taxonomyPolicy)
    (sourceClass targetClass : ChallengeClassRecord) where
  sourceDeclared : sourceClass ∈ taxonomy.classRecords
  targetDeclared : targetClass ∈ taxonomy.classRecords
  sameTaxonomy : sourceClass.taxonomyId = targetClass.taxonomyId
  sameClassId : sourceClass.challengeId = targetClass.challengeId

structure InterfaceMediationCertified
    {bridgePolicyA : CarriedRecordPolicy S_A.T InterCarrierBridgeRecord}
    {bridgePolicyB : CarriedRecordPolicy S_B.T InterCarrierBridgeRecord}
    {taxonomyPolicy : CarriedRecordPolicy S_B.T TaxonomyRecord}
    (sourceAccessPolicy : CarriedRecordPolicy S_A.T InterfaceAccessRecordA)
    (targetAccessPolicy : CarriedRecordPolicy S_B.T InterfaceAccessRecordB)
    (dischargeComparator : BridgeDischargeComparator
      (LedgerEntryA := LedgerEntryA) (LedgerEntryB := LedgerEntryB))
    (bridge : InterCarrierBridge S_A S_B dischargeComparator
      bridgePolicyA bridgePolicyB)
    (taxonomy : DeclaredTransportTaxonomy S_B taxonomyPolicy) where
  sourceAccessRecord : InterfaceAccessRecordA
  targetAccessRecord : InterfaceAccessRecordB
  sourceAccessCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt sourceAccessPolicy sourceAccessRecord n0
          sourceTag generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  targetAccessCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt targetAccessPolicy targetAccessRecord n0
          sourceTag generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  bridgeLinked :
    sourceAccessRecord.bridgeRef = bridge.bridgeRecord ∧
      targetAccessRecord.bridgeRef = bridge.bridgeRecord
  taxonomyLinked :
    sourceAccessRecord.taxonomyRef = taxonomy.taxonomyRecord ∧
      targetAccessRecord.taxonomyRef = taxonomy.taxonomyRecord

structure ReceiverQuotientInstallCertified where
  installs :
    {X Q Q' : Type} ->
      RepairMove S_B.T MovePayloadB LedgerEntryB MoveRecordB
        S_B.moveRecordPolicy ->
      (X -> Q) -> (X -> Q') -> Prop

structure TransportDeltaReduction
    (targetRepair : TargetRepairRecord S_B)
    (install : ReceiverQuotientInstallCertified S_B)
    {X Q Q' FOut Readout : Type}
    (qBefore : X -> Q)
    (qAfter : X -> Q')
    (F_C : X -> FOut)
    (r_B : FOut -> Readout) where
  afterQuotientInstalledByMove :
    install.installs targetRepair.inducedMove qBefore qAfter
  subset :
    ∀ x x',
      Delta qAfter F_C r_B x x' -> Delta qBefore F_C r_B x x'
  strict :
    ∃ x x',
      Delta qBefore F_C r_B x x' ∧ ¬ Delta qAfter F_C r_B x x'

structure InducedBRepair
    {bridgePolicyA : CarriedRecordPolicy S_A.T InterCarrierBridgeRecord}
    {bridgePolicyB : CarriedRecordPolicy S_B.T InterCarrierBridgeRecord}
    {taxonomyPolicy : CarriedRecordPolicy S_B.T TaxonomyRecord}
    (targetRepairPolicy :
      CarriedRecordPolicy S_B.T (TargetRepairRecord S_B))
    (dischargeComparator : BridgeDischargeComparator
      (LedgerEntryA := LedgerEntryA) (LedgerEntryB := LedgerEntryB))
    (bridge : InterCarrierBridge S_A S_B dischargeComparator
      bridgePolicyA bridgePolicyB)
    (taxonomy : DeclaredTransportTaxonomy S_B taxonomyPolicy)
    (sourcePackage : SourceRepairPackageRecord)
    (token : TransportTokenRecord)
    (targetRepair : TargetRepairRecord S_B)
    (install : ReceiverQuotientInstallCertified S_B)
    {X Q Q' FOut Readout : Type}
    (qBefore : X -> Q)
    (qAfter : X -> Q')
    (F_C : X -> FOut)
    (r_B : FOut -> Readout) where
  tokenLinked : sourcePackage.emittedToken = token
  repairReceiptLinked : targetRepair.receiptToken = token
  bridgeLinked :
    bridge.bridgeRecord.sourceCarrier = token.sourceCarrier ∧
      bridge.bridgeRecord.targetCarrier = token.targetCarrier
  sameClass :
    SameTransportChallengeClass S_B taxonomy
      sourcePackage.sourceChallenge targetRepair.targetChallenge
  targetMoveCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt targetRepairPolicy targetRepair n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  targetMoveLawful :
    ∃ z z' : S_B.T.Z, ∃ defect : DefectRecordB,
      ∃ auditRecord : AuditRecordB,
        LawfulRepairStep S_B.Lambda_S S_B.defectRecordPolicy
          S_B.moveRecordPolicy S_B.auditRecordPolicy S_B.I_S
          S_B.AdmissibleMove z z' defect targetRepair.inducedMove
          auditRecord
  deltaReduction :
    TransportDeltaReduction S_B targetRepair install qBefore qAfter F_C r_B

structure RoleTransportComparator where
  preservesRole :
    SourceRepairPackageRecord -> TargetRepairRecord S_B -> RepairRoleRecord ->
      Prop

structure RolePreservingTransportCertified
    (comparator : RoleTransportComparator S_B)
    (sourcePackage : SourceRepairPackageRecord)
    (targetRepair : TargetRepairRecord S_B) where
  sourceRoleLinked :
    sourcePackage.roleRecord.challengeClass = sourcePackage.sourceChallenge
  targetRoleLinked :
    targetRepair.roleRecord.challengeClass = targetRepair.targetChallenge
  sameRoleRecord : sourcePackage.roleRecord.roleId = targetRepair.roleRecord.roleId
  certified :
    comparator.preservesRole sourcePackage targetRepair sourcePackage.roleRecord

structure RoleActivationComparator where
  roleActiveBefore :
    BRoleStateRecord -> RepairRoleRecord -> ContextFamilyRecord -> Prop
  roleActiveAfter :
    BRoleStateRecord -> RepairRoleRecord -> ContextFamilyRecord -> Prop

inductive ResponseMode where
  | observed_free_response
  | fully_forced_response
  | scaffolded_response
  | primed_response
  deriving DecidableEq, Repr

structure ForceOpportunityComparator where
  classifies :
    ForceScheduleRecord -> List FreeResponseOpportunityRecord ->
      ResponseMode -> Prop

structure RepairTransportClassifierContext
    (bridgePolicyA : CarriedRecordPolicy S_A.T InterCarrierBridgeRecord)
    (bridgePolicyB : CarriedRecordPolicy S_B.T InterCarrierBridgeRecord)
    (taxonomyPolicy : CarriedRecordPolicy S_B.T TaxonomyRecord) where
  taxonomy : DeclaredTransportTaxonomy S_B taxonomyPolicy
  roleComparator : RoleTransportComparator S_B
  activationComparator : RoleActivationComparator
  bridgeDischargeComparator :
    BridgeDischargeComparator (LedgerEntryA := LedgerEntryA)
      (LedgerEntryB := LedgerEntryB)
  quotientInstall : ReceiverQuotientInstallCertified S_B
  forceComparator : ForceOpportunityComparator

structure CommunicationTransportEvidence
    {bridgePolicyA : CarriedRecordPolicy S_A.T InterCarrierBridgeRecord}
    {bridgePolicyB : CarriedRecordPolicy S_B.T InterCarrierBridgeRecord}
    {taxonomyPolicy : CarriedRecordPolicy S_B.T TaxonomyRecord}
    (sourcePackagePolicy :
      CarriedRecordPolicy S_A.T SourceRepairPackageRecord)
    (tokenPolicyA : CarriedRecordPolicy S_A.T TransportTokenRecord)
    (tokenPolicyB : CarriedRecordPolicy S_B.T TransportTokenRecord)
    (targetRepairPolicy :
      CarriedRecordPolicy S_B.T (TargetRepairRecord S_B))
    (sourceAccessPolicy : CarriedRecordPolicy S_A.T InterfaceAccessRecordA)
    (targetAccessPolicy : CarriedRecordPolicy S_B.T InterfaceAccessRecordB)
    (ctx : RepairTransportClassifierContext S_A S_B
      bridgePolicyA bridgePolicyB taxonomyPolicy)
    (bridge : InterCarrierBridge S_A S_B ctx.bridgeDischargeComparator
      bridgePolicyA bridgePolicyB)
    (sourcePackage : SourceRepairPackageRecord)
    (token : TransportTokenRecord)
    (targetRepair : TargetRepairRecord S_B)
    {X Q Q' FOut Readout : Type}
    (qBefore : X -> Q)
    (qAfter : X -> Q')
    (F_C : X -> FOut)
    (r_B : FOut -> Readout) where
  inducedRepair :
    InducedBRepair S_A S_B targetRepairPolicy ctx.bridgeDischargeComparator
      bridge ctx.taxonomy sourcePackage token targetRepair
      ctx.quotientInstall qBefore qAfter F_C r_B
  interfaceMediation :
    InterfaceMediationCertified S_A S_B sourceAccessPolicy targetAccessPolicy
      ctx.bridgeDischargeComparator bridge ctx.taxonomy
  rolePreserving :
    RolePreservingTransportCertified S_B ctx.roleComparator sourcePackage
      targetRepair
  sourcePackageCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt sourcePackagePolicy sourcePackage n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  tokenCarriedByA :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt tokenPolicyA token n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  receiptCarriedByB :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt tokenPolicyB token n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

structure DifferentClassInfluenceEvidence
    {bridgePolicyA : CarriedRecordPolicy S_A.T InterCarrierBridgeRecord}
    {bridgePolicyB : CarriedRecordPolicy S_B.T InterCarrierBridgeRecord}
    {taxonomyPolicy : CarriedRecordPolicy S_B.T TaxonomyRecord}
    (sourcePackagePolicy :
      CarriedRecordPolicy S_A.T SourceRepairPackageRecord)
    (tokenPolicyA : CarriedRecordPolicy S_A.T TransportTokenRecord)
    (tokenPolicyB : CarriedRecordPolicy S_B.T TransportTokenRecord)
    (targetRepairPolicy :
      CarriedRecordPolicy S_B.T (TargetRepairRecord S_B))
    (ctx : RepairTransportClassifierContext S_A S_B
      bridgePolicyA bridgePolicyB taxonomyPolicy)
    (bridge : InterCarrierBridge S_A S_B ctx.bridgeDischargeComparator
      bridgePolicyA bridgePolicyB)
    (sourcePackage : SourceRepairPackageRecord)
    (token : TransportTokenRecord)
    (targetRepair : TargetRepairRecord S_B)
    {X Q Q' FOut Readout : Type}
    (qBefore : X -> Q)
    (qAfter : X -> Q')
    (F_other : X -> FOut)
    (r_B : FOut -> Readout) where
  tokenLinked : sourcePackage.emittedToken = token
  repairReceiptLinked : targetRepair.receiptToken = token
  bridgeLinked :
    bridge.bridgeRecord.sourceCarrier = token.sourceCarrier ∧
      bridge.bridgeRecord.targetCarrier = token.targetCarrier
  sourcePackageCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt sourcePackagePolicy sourcePackage n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  tokenCarriedByA :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt tokenPolicyA token n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  receiptCarriedByB :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt tokenPolicyB token n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  targetMoveCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt targetRepairPolicy targetRepair n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  targetMoveLawful :
    ∃ z z' : S_B.T.Z, ∃ defect : DefectRecordB,
      ∃ auditRecord : AuditRecordB,
        LawfulRepairStep S_B.Lambda_S S_B.defectRecordPolicy
          S_B.moveRecordPolicy S_B.auditRecordPolicy S_B.I_S
          S_B.AdmissibleMove z z' defect targetRepair.inducedMove
          auditRecord
  deltaReduction :
    TransportDeltaReduction S_B targetRepair ctx.quotientInstall qBefore qAfter
      F_other r_B
  differentClass :
    ¬ SameTransportChallengeClass S_B ctx.taxonomy sourcePackage.sourceChallenge
      targetRepair.targetChallenge

structure AAbsenceProbeSchedule
    (schedulePolicy : CarriedRecordPolicy S_B.T ProbeScheduleRecord) where
  scheduleRecord : ProbeScheduleRecord
  challengeClass : ChallengeClassRecord
  probeTimes : List Nat
  nonempty : probeTimes.length > 0
  aCarrierPresentAt : Nat -> Bool
  bridgeOpenAt : Nat -> Bool
  absenceAtEveryProbe :
    ∀ t, t ∈ probeTimes ->
      aCarrierPresentAt t = false ∧ bridgeOpenAt t = false
  carried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt schedulePolicy scheduleRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

structure BCommittedRepairInAAbsence
    {taxonomyPolicy : CarriedRecordPolicy S_B.T TaxonomyRecord}
    {schedulePolicy : CarriedRecordPolicy S_B.T ProbeScheduleRecord}
    (targetRepairPolicy :
      CarriedRecordPolicy S_B.T (TargetRepairRecord S_B))
    (taxonomy : DeclaredTransportTaxonomy S_B taxonomyPolicy)
    (schedule : AAbsenceProbeSchedule S_B schedulePolicy)
    (targetRepair : TargetRepairRecord S_B)
    (install : ReceiverQuotientInstallCertified S_B)
    {X Q Q' FOut Readout : Type}
    (qBefore : X -> Q)
    (qAfter : X -> Q')
    (F_C : X -> FOut)
    (r_B : FOut -> Readout) where
  repairInSameClass :
    SameTransportChallengeClass S_B taxonomy schedule.challengeClass
      targetRepair.targetChallenge
  repairTime : Nat
  repairTimeInSchedule : repairTime ∈ schedule.probeTimes
  sourceIsBCommitted :
    CarriedRecordAt targetRepairPolicy targetRepair repairTime
      FineSourceTag.committed_state true true
  lawfulRepair :
    ∃ z z' : S_B.T.Z, ∃ defect : DefectRecordB,
      ∃ auditRecord : AuditRecordB,
        LawfulRepairStep S_B.Lambda_S S_B.defectRecordPolicy
          S_B.moveRecordPolicy S_B.auditRecordPolicy S_B.I_S
          S_B.AdmissibleMove z z' defect targetRepair.inducedMove
          auditRecord
  descendsAgain :
    TransportDeltaReduction S_B targetRepair install qBefore qAfter F_C r_B

structure TeachingCapacityEvidence
    {bridgePolicyA : CarriedRecordPolicy S_A.T InterCarrierBridgeRecord}
    {bridgePolicyB : CarriedRecordPolicy S_B.T InterCarrierBridgeRecord}
    {taxonomyPolicy : CarriedRecordPolicy S_B.T TaxonomyRecord}
    {schedulePolicy : CarriedRecordPolicy S_B.T ProbeScheduleRecord}
    (sourcePackagePolicy :
      CarriedRecordPolicy S_A.T SourceRepairPackageRecord)
    (tokenPolicyA : CarriedRecordPolicy S_A.T TransportTokenRecord)
    (tokenPolicyB : CarriedRecordPolicy S_B.T TransportTokenRecord)
    (targetRepairPolicy :
      CarriedRecordPolicy S_B.T (TargetRepairRecord S_B))
    (sourceAccessPolicy : CarriedRecordPolicy S_A.T InterfaceAccessRecordA)
    (targetAccessPolicy : CarriedRecordPolicy S_B.T InterfaceAccessRecordB)
    (ctx : RepairTransportClassifierContext S_A S_B
      bridgePolicyA bridgePolicyB taxonomyPolicy)
    (bridge : InterCarrierBridge S_A S_B ctx.bridgeDischargeComparator
      bridgePolicyA bridgePolicyB)
    (sourcePackage : SourceRepairPackageRecord)
    (token : TransportTokenRecord)
    (initialRepair : TargetRepairRecord S_B)
    {X0 Q0 Q0' FOut0 Readout0 : Type}
    (qBeforeInitial : X0 -> Q0)
    (qAfterInitial : X0 -> Q0')
    (F_initial : X0 -> FOut0)
    (r_initial : FOut0 -> Readout0)
    (communication :
      CommunicationTransportEvidence S_A S_B sourcePackagePolicy tokenPolicyA
        tokenPolicyB targetRepairPolicy sourceAccessPolicy targetAccessPolicy
        ctx bridge sourcePackage token initialRepair qBeforeInitial
        qAfterInitial F_initial r_initial)
    (schedule : AAbsenceProbeSchedule S_B schedulePolicy)
    {X Q Q' FOut Readout : Type}
    (qBeforeAAbsent : X -> Q)
    (qAfterAAbsent : X -> Q')
    (F_C : X -> FOut)
    (r_B : FOut -> Readout) where
  subsequentRepair : TargetRepairRecord S_B
  tokenLinked : sourcePackage.emittedToken = token
  communicationSameClass :
    SameTransportChallengeClass S_B ctx.taxonomy
      sourcePackage.sourceChallenge initialRepair.targetChallenge
  communicationBridgeLinked :
    bridge.bridgeRecord.sourceCarrier = token.sourceCarrier ∧
      bridge.bridgeRecord.targetCarrier = token.targetCarrier
  bCommittedCapacity :
    BCommittedRepairInAAbsence S_B targetRepairPolicy ctx.taxonomy schedule
      subsequentRepair ctx.quotientInstall qBeforeAAbsent qAfterAAbsent F_C r_B
  sameChallengeAsSourcePackage :
    SameTransportChallengeClass S_B ctx.taxonomy sourcePackage.sourceChallenge
      subsequentRepair.targetChallenge
  capacityLinkedToPackage :
    subsequentRepair.roleRecord.roleId = sourcePackage.roleRecord.roleId

structure InteractionForcingRecord where
  interactionId : Nat
  token : TransportTokenRecord
  targetCarrier : CarrierName
  responseMode : ResponseMode
  forceSchedule : ForceScheduleRecord

structure FreeResponseOpportunityCensus
    (censusPolicy : CarriedRecordPolicy S_B.T FreeResponseCensusRecord) where
  censusRecord : FreeResponseCensusRecord
  interaction : InteractionForcingRecord
  forceSchedule : ForceScheduleRecord
  opportunities : List FreeResponseOpportunityRecord
  scheduleLinked : forceSchedule = interaction.forceSchedule
  carried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt censusPolicy censusRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

structure FullyForcedInteraction
    {censusPolicy : CarriedRecordPolicy S_B.T FreeResponseCensusRecord}
    (forcingPolicy : CarriedRecordPolicy S_B.T InteractionForcingRecord)
    (forceComparator : ForceOpportunityComparator)
    where
  forcingRecord : InteractionForcingRecord
  opportunityCensus : FreeResponseOpportunityCensus S_B censusPolicy
  censusLinked : opportunityCensus.interaction = forcingRecord
  forcingCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt forcingPolicy forcingRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  responseModeComputed :
    forceComparator.classifies forcingRecord.forceSchedule
      opportunityCensus.opportunities forcingRecord.responseMode
  responseModeLinked :
    forcingRecord.responseMode = ResponseMode.fully_forced_response
  noFreeOpportunity : opportunityCensus.opportunities = []

structure CoercionNullCertified
    {censusPolicy : CarriedRecordPolicy S_B.T FreeResponseCensusRecord}
    (targetRepairPolicy :
      CarriedRecordPolicy S_B.T (TargetRepairRecord S_B))
    (forcingPolicy : CarriedRecordPolicy S_B.T InteractionForcingRecord)
    (forceComparator : ForceOpportunityComparator)
    (forced : FullyForcedInteraction S_B forcingPolicy forceComparator
      (censusPolicy := censusPolicy))
    (token : TransportTokenRecord)
    {X Q Q' FOut Readout : Type}
    (qBeforeForce : X -> Q)
    (qAfterForce : X -> Q')
    (F_C : X -> FOut)
    (r_B : FOut -> Readout) where
  tokenLinked : forced.forcingRecord.token = token
  carriedCensusWitness :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt censusPolicy forced.opportunityCensus.censusRecord
          n0 sourceTag generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  forcedClassificationComputed :
    forceComparator.classifies forced.forcingRecord.forceSchedule
      forced.opportunityCensus.opportunities forced.forcingRecord.responseMode
  noBCommittedTransportedRepair :
    ¬ ∃ targetRepair : TargetRepairRecord S_B,
      targetRepair.receiptToken = token ∧
        ∃ t, CarriedRecordAt targetRepairPolicy targetRepair t
          FineSourceTag.committed_state true true
  targetQuotientUnrefined :
    ∀ x x',
      Delta qAfterForce F_C r_B x x' ↔ Delta qBeforeForce F_C r_B x x'

structure ScaffoldedOrPrimedInteraction
    {censusPolicy : CarriedRecordPolicy S_B.T FreeResponseCensusRecord}
    (forcingPolicy : CarriedRecordPolicy S_B.T InteractionForcingRecord)
    (forceComparator : ForceOpportunityComparator) where
  interaction : InteractionForcingRecord
  opportunityCensus : FreeResponseOpportunityCensus S_B censusPolicy
  censusLinked : opportunityCensus.interaction = interaction
  interactionCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt forcingPolicy interaction n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  responseModeComputed :
    forceComparator.classifies interaction.forceSchedule
      opportunityCensus.opportunities interaction.responseMode
  modeIsScaffoldOrPrime :
    interaction.responseMode = ResponseMode.scaffolded_response ∨
      interaction.responseMode = ResponseMode.primed_response

structure ScaffoldingOrPrimingWitness
    {taxonomyPolicy : CarriedRecordPolicy S_B.T TaxonomyRecord}
    {censusPolicy : CarriedRecordPolicy S_B.T FreeResponseCensusRecord}
    {schedulePolicy : CarriedRecordPolicy S_B.T ProbeScheduleRecord}
    (targetRepairPolicy :
      CarriedRecordPolicy S_B.T (TargetRepairRecord S_B))
    (forcingPolicy : CarriedRecordPolicy S_B.T InteractionForcingRecord)
    (forceComparator : ForceOpportunityComparator)
    (token : TransportTokenRecord)
    (sourcePackage : SourceRepairPackageRecord)
    (claimClass : ChallengeClassRecord)
    (taxonomy : DeclaredTransportTaxonomy S_B taxonomyPolicy)
    (install : ReceiverQuotientInstallCertified S_B)
    {X Q Q' FOut Readout : Type}
    (qBeforeWithAid : X -> Q)
    (qAfterWithAid : X -> Q')
    (F_C : X -> FOut)
    (r_B : FOut -> Readout) where
  scaffoldedOrPrimed :
    ScaffoldedOrPrimedInteraction S_B forcingPolicy forceComparator
      (censusPolicy := censusPolicy)
  tokenLinked : scaffoldedOrPrimed.interaction.token = token
  claimClassLinked :
    SameTransportChallengeClass S_B taxonomy sourcePackage.sourceChallenge
      claimClass
  responseModeComputed :
    forceComparator.classifies scaffoldedOrPrimed.interaction.forceSchedule
      scaffoldedOrPrimed.opportunityCensus.opportunities
      scaffoldedOrPrimed.interaction.responseMode
  behaviorImprovesWhilePresent :
    ∃ targetRepair : TargetRepairRecord S_B,
      targetRepair.receiptToken = token ∧
        SameTransportChallengeClass S_B taxonomy claimClass
          targetRepair.targetChallenge ∧
        TransportDeltaReduction S_B targetRepair install qBeforeWithAid
          qAfterWithAid F_C r_B
  noAAbsentBCommittedCapacity :
    ¬ ∃ schedule : AAbsenceProbeSchedule S_B schedulePolicy,
      ∃ targetRepair : TargetRepairRecord S_B,
        SameTransportChallengeClass S_B taxonomy sourcePackage.sourceChallenge
          targetRepair.targetChallenge ∧
        targetRepair.roleRecord.roleId = sourcePackage.roleRecord.roleId ∧
        Nonempty (BCommittedRepairInAAbsence S_B targetRepairPolicy taxonomy
          schedule targetRepair install qBeforeWithAid qAfterWithAid F_C r_B)

structure DeclaredTransportContextFamily
    (contextFamilyPolicy : CarriedRecordPolicy S_B.T ContextFamilyRecord) where
  familyRecord : ContextFamilyRecord
  contexts : List TransportContextRecord
  atLeastTwoContexts : contexts.length >= 2
  carried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt contextFamilyPolicy familyRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

structure ContextualRepairReactivation
    {bridgePolicyA : CarriedRecordPolicy S_A.T InterCarrierBridgeRecord}
    {bridgePolicyB : CarriedRecordPolicy S_B.T InterCarrierBridgeRecord}
    {taxonomyPolicy : CarriedRecordPolicy S_B.T TaxonomyRecord}
    (sourcePackagePolicy :
      CarriedRecordPolicy S_A.T SourceRepairPackageRecord)
    (tokenPolicyA : CarriedRecordPolicy S_A.T TransportTokenRecord)
    (tokenPolicyB : CarriedRecordPolicy S_B.T TransportTokenRecord)
    (targetRepairPolicy :
      CarriedRecordPolicy S_B.T (TargetRepairRecord S_B))
    (sourceAccessPolicy : CarriedRecordPolicy S_A.T InterfaceAccessRecordA)
    (targetAccessPolicy : CarriedRecordPolicy S_B.T InterfaceAccessRecordB)
    (bridgeDischargeComparator : BridgeDischargeComparator
      (LedgerEntryA := LedgerEntryA) (LedgerEntryB := LedgerEntryB))
    (bridge : InterCarrierBridge S_A S_B bridgeDischargeComparator
      bridgePolicyA bridgePolicyB)
    (token : TransportTokenRecord)
    (sourcePackage : SourceRepairPackageRecord)
    (context : TransportContextRecord)
    (taxonomy : DeclaredTransportTaxonomy S_B taxonomyPolicy)
    (roleComparator : RoleTransportComparator S_B)
    (install : ReceiverQuotientInstallCertified S_B)
    {X Q Q' FOut Readout : Type}
    (qBeforeContext : X -> Q)
    (qAfterContext : X -> Q')
    (F_context : X -> FOut)
    (r_B : FOut -> Readout) where
  targetRepair : TargetRepairRecord S_B
  bridgeLinked :
    bridge.bridgeRecord.sourceCarrier = token.sourceCarrier ∧
      bridge.bridgeRecord.targetCarrier = token.targetCarrier
  interfaceMediation :
    InterfaceMediationCertified S_A S_B sourceAccessPolicy targetAccessPolicy
      bridgeDischargeComparator bridge taxonomy
  contextLinked :
    SameTransportChallengeClass S_B taxonomy sourcePackage.sourceChallenge
      context.challengeClass
  tokenLinked : sourcePackage.emittedToken = token
  tokenReactivatesPackage : targetRepair.receiptToken = token
  sourcePackageCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt sourcePackagePolicy sourcePackage n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  tokenCarriedByA :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt tokenPolicyA token n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  receiptCarriedByB :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt tokenPolicyB token n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  targetRepairCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt targetRepairPolicy targetRepair n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  targetMoveLawful :
    ∃ z z' : S_B.T.Z, ∃ defect : DefectRecordB,
      ∃ auditRecord : AuditRecordB,
        LawfulRepairStep S_B.Lambda_S S_B.defectRecordPolicy
          S_B.moveRecordPolicy S_B.auditRecordPolicy S_B.I_S
          S_B.AdmissibleMove z z' defect targetRepair.inducedMove
          auditRecord
  rolePreserving :
    RolePreservingTransportCertified S_B roleComparator sourcePackage targetRepair
  descendsInContext :
    TransportDeltaReduction S_B targetRepair install qBeforeContext
      qAfterContext F_context r_B

structure CurrentStructureAlreadyCarriesRole
    (roleComparator : RoleActivationComparator)
    (sourcePackage : SourceRepairPackageRecord)
    {contextFamilyPolicy : CarriedRecordPolicy S_B.T ContextFamilyRecord}
    (family : DeclaredTransportContextFamily S_B contextFamilyPolicy)
    (roleStatePolicy : CarriedRecordPolicy S_B.T BRoleStateRecord) where
  preTokenState : BRoleStateRecord
  postTokenState : BRoleStateRecord
  preStateCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt roleStatePolicy preTokenState n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  postStateCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt roleStatePolicy postTokenState n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  familyLinked :
    preTokenState.contextFamilyRef = family.familyRecord ∧
      postTokenState.contextFamilyRef = family.familyRecord
  alreadyActiveBefore :
    roleComparator.roleActiveBefore preTokenState sourcePackage.roleRecord
      family.familyRecord
  activeAfter :
    roleComparator.roleActiveAfter postTokenState sourcePackage.roleRecord
      family.familyRecord

structure SymbolSaturationStrict
    {bridgePolicyA : CarriedRecordPolicy S_A.T InterCarrierBridgeRecord}
    {bridgePolicyB : CarriedRecordPolicy S_B.T InterCarrierBridgeRecord}
    {taxonomyPolicy : CarriedRecordPolicy S_B.T TaxonomyRecord}
    {contextFamilyPolicy : CarriedRecordPolicy S_B.T ContextFamilyRecord}
    (sourcePackagePolicy :
      CarriedRecordPolicy S_A.T SourceRepairPackageRecord)
    (tokenPolicyA : CarriedRecordPolicy S_A.T TransportTokenRecord)
    (tokenPolicyB : CarriedRecordPolicy S_B.T TransportTokenRecord)
    (targetRepairPolicy :
      CarriedRecordPolicy S_B.T (TargetRepairRecord S_B))
    (sourceAccessPolicy : CarriedRecordPolicy S_A.T InterfaceAccessRecordA)
    (targetAccessPolicy : CarriedRecordPolicy S_B.T InterfaceAccessRecordB)
    (roleStatePolicy : CarriedRecordPolicy S_B.T BRoleStateRecord)
    (bridgeDischargeComparator : BridgeDischargeComparator
      (LedgerEntryA := LedgerEntryA) (LedgerEntryB := LedgerEntryB))
    (bridge : InterCarrierBridge S_A S_B bridgeDischargeComparator
      bridgePolicyA bridgePolicyB)
    (token : TransportTokenRecord)
    (sourcePackage : SourceRepairPackageRecord)
    (family : DeclaredTransportContextFamily S_B contextFamilyPolicy)
    (taxonomy : DeclaredTransportTaxonomy S_B taxonomyPolicy)
    (roleComparator : RoleTransportComparator S_B)
    (activationComparator : RoleActivationComparator)
    (install : ReceiverQuotientInstallCertified S_B)
    {X Q Q' FOut Readout : Type}
    (qBeforeContext : X -> Q)
    (qAfterContext : X -> Q')
    (F_context : X -> FOut)
    (r_B : FOut -> Readout) where
  notCurrentRelabel :
    ¬ Nonempty (CurrentStructureAlreadyCarriesRole S_B activationComparator
      sourcePackage family roleStatePolicy)
  genuinePackageReactivated :
    ∃ context : TransportContextRecord, context ∈ family.contexts ∧
      ∃ _reactivation :
        ContextualRepairReactivation S_A S_B sourcePackagePolicy
          tokenPolicyA tokenPolicyB targetRepairPolicy sourceAccessPolicy
          targetAccessPolicy bridgeDischargeComparator bridge token
          sourcePackage context taxonomy roleComparator install qBeforeContext
          qAfterContext F_context r_B,
        True

structure SymbolicRepairEvidence
    {bridgePolicyA : CarriedRecordPolicy S_A.T InterCarrierBridgeRecord}
    {bridgePolicyB : CarriedRecordPolicy S_B.T InterCarrierBridgeRecord}
    {taxonomyPolicy : CarriedRecordPolicy S_B.T TaxonomyRecord}
    {contextFamilyPolicy : CarriedRecordPolicy S_B.T ContextFamilyRecord}
    (sourcePackagePolicy :
      CarriedRecordPolicy S_A.T SourceRepairPackageRecord)
    (tokenPolicyA : CarriedRecordPolicy S_A.T TransportTokenRecord)
    (tokenPolicyB : CarriedRecordPolicy S_B.T TransportTokenRecord)
    (targetRepairPolicy :
      CarriedRecordPolicy S_B.T (TargetRepairRecord S_B))
    (sourceAccessPolicy : CarriedRecordPolicy S_A.T InterfaceAccessRecordA)
    (targetAccessPolicy : CarriedRecordPolicy S_B.T InterfaceAccessRecordB)
    (roleStatePolicy : CarriedRecordPolicy S_B.T BRoleStateRecord)
    (bridgeDischargeComparator : BridgeDischargeComparator
      (LedgerEntryA := LedgerEntryA) (LedgerEntryB := LedgerEntryB))
    (bridge : InterCarrierBridge S_A S_B bridgeDischargeComparator
      bridgePolicyA bridgePolicyB)
    (token : TransportTokenRecord)
    (sourcePackage : SourceRepairPackageRecord)
    (family : DeclaredTransportContextFamily S_B contextFamilyPolicy)
    (taxonomy : DeclaredTransportTaxonomy S_B taxonomyPolicy)
    (roleComparator : RoleTransportComparator S_B)
    (activationComparator : RoleActivationComparator)
    (install : ReceiverQuotientInstallCertified S_B)
    {X Q Q' FOut Readout : Type}
    (qBeforeContext : X -> Q)
    (qAfterContext : X -> Q')
    (F_context : X -> FOut)
    (r_B : FOut -> Readout) where
  reactivatesEveryContext :
    ∀ context : TransportContextRecord, context ∈ family.contexts ->
      ∃ _reactivation :
        ContextualRepairReactivation S_A S_B sourcePackagePolicy tokenPolicyA
          tokenPolicyB targetRepairPolicy sourceAccessPolicy targetAccessPolicy
          bridgeDischargeComparator bridge token sourcePackage context taxonomy
          roleComparator install qBeforeContext qAfterContext F_context r_B,
        True
  roleStableAcrossContexts :
    ∀ {c1 c2 : TransportContextRecord}
      (r1 :
        ContextualRepairReactivation S_A S_B sourcePackagePolicy tokenPolicyA
          tokenPolicyB targetRepairPolicy sourceAccessPolicy targetAccessPolicy
          bridgeDischargeComparator bridge token sourcePackage c1 taxonomy
          roleComparator install qBeforeContext qAfterContext F_context r_B)
      (r2 :
        ContextualRepairReactivation S_A S_B sourcePackagePolicy tokenPolicyA
          tokenPolicyB targetRepairPolicy sourceAccessPolicy targetAccessPolicy
          bridgeDischargeComparator bridge token sourcePackage c2 taxonomy
          roleComparator install qBeforeContext qAfterContext F_context r_B),
      c1 ∈ family.contexts -> c2 ∈ family.contexts ->
        r1.targetRepair.roleRecord.roleId = r2.targetRepair.roleRecord.roleId
  saturationStrict :
    SymbolSaturationStrict S_A S_B sourcePackagePolicy tokenPolicyA tokenPolicyB
      targetRepairPolicy sourceAccessPolicy targetAccessPolicy roleStatePolicy
      bridgeDischargeComparator bridge token sourcePackage family taxonomy
      roleComparator activationComparator install qBeforeContext qAfterContext
      F_context r_B

end Setup

section StatusApparatus

variable {FDataA : Type uA} {RuleFamilyA : Type vA}
variable {ResidualFamilyA : Type wA} {AuditAccessDataA : Type xA}
variable {InstrumentRecordA : Type yA} {LedgerEntryA : Type yA'}
variable {DefectRecordA : Type yA''} {MovePayloadA : Type yA'''}
variable {MoveRecordA : Type yA''''} {AuditRecordA : Type yA'''''}

variable {FDataB : Type uB} {RuleFamilyB : Type vB}
variable {ResidualFamilyB : Type wB} {AuditAccessDataB : Type xB}
variable {InstrumentRecordB : Type yB} {LedgerEntryB : Type yB'}
variable {DefectRecordB : Type yB''} {MovePayloadB : Type yB'''}
variable {MoveRecordB : Type yB''''} {AuditRecordB : Type yB'''''}

variable (S_A : ESystem FDataA RuleFamilyA ResidualFamilyA AuditAccessDataA
  InstrumentRecordA LedgerEntryA DefectRecordA MovePayloadA MoveRecordA
  AuditRecordA)
variable (S_B : ESystem FDataB RuleFamilyB ResidualFamilyB AuditAccessDataB
  InstrumentRecordB LedgerEntryB DefectRecordB MovePayloadB MoveRecordB
  AuditRecordB)

inductive RepairTransportStatus where
  | coercion_null
  | symbolic
  | taught
  | communicated
  | scaffolded_or_primed
  | influence_only
  | transport_rejected
  deriving DecidableEq, Repr

inductive TransportClaimRef where
  | communication (token : TransportTokenRecord)
      (sourcePackage : SourceRepairPackageRecord)
      (bridge : InterCarrierBridgeRecord)
      (targetClass : ChallengeClassRecord)
  | teaching (token : TransportTokenRecord)
      (sourcePackage : SourceRepairPackageRecord)
      (bridge : InterCarrierBridgeRecord)
      (targetClass : ChallengeClassRecord)
  | symbol (token : TransportTokenRecord)
      (sourcePackage : SourceRepairPackageRecord)
      (bridge : InterCarrierBridgeRecord)
      (family : ContextFamilyRecord)

structure RepairTransportStatusRecord
    (S_A : ESystem FDataA RuleFamilyA ResidualFamilyA AuditAccessDataA
      InstrumentRecordA LedgerEntryA DefectRecordA MovePayloadA MoveRecordA
      AuditRecordA)
    (S_B : ESystem FDataB RuleFamilyB ResidualFamilyB AuditAccessDataB
      InstrumentRecordB LedgerEntryB DefectRecordB MovePayloadB MoveRecordB
      AuditRecordB) where
  claimKind : TransportClaimKind
  tokenRecord : TransportTokenRecord
  sourcePackageRecord : SourceRepairPackageRecord
  targetRepairRecord : Option (TargetRepairRecord S_B)
  contextFamilyRecord : Option ContextFamilyRecord
  forcingRecord : Option InteractionForcingRecord
  bridgeRecord : Option InterCarrierBridgeRecord
  status : RepairTransportStatus
  supportingLedgerEntriesA : List LedgerEntryA
  supportingLedgerEntriesB : List LedgerEntryB
  supportingAuditRecordsA : List AuditRecordA
  supportingAuditRecordsB : List AuditRecordB

def TransportStatusRecordMatchesClaim
    (claimRef : TransportClaimRef)
    (record : RepairTransportStatusRecord S_A S_B) : Prop :=
  match claimRef with
  | TransportClaimRef.communication token sourcePackage bridge targetClass =>
      record.claimKind = TransportClaimKind.communication ∧
        record.tokenRecord = token ∧
        record.sourcePackageRecord = sourcePackage ∧
        record.bridgeRecord = some bridge ∧
        record.contextFamilyRecord = none ∧
        ∃ targetRepair : TargetRepairRecord S_B,
          record.targetRepairRecord = some targetRepair ∧
            targetRepair.receiptToken = token ∧
            targetRepair.targetChallenge = targetClass
  | TransportClaimRef.teaching token sourcePackage bridge targetClass =>
      record.claimKind = TransportClaimKind.teaching ∧
        record.tokenRecord = token ∧
        record.sourcePackageRecord = sourcePackage ∧
        record.bridgeRecord = some bridge ∧
        record.contextFamilyRecord = none ∧
        ∃ targetRepair : TargetRepairRecord S_B,
          record.targetRepairRecord = some targetRepair ∧
            targetRepair.targetChallenge = targetClass
  | TransportClaimRef.symbol token sourcePackage bridge family =>
      record.claimKind = TransportClaimKind.symbol ∧
        record.tokenRecord = token ∧
        record.sourcePackageRecord = sourcePackage ∧
        record.bridgeRecord = some bridge ∧
        record.contextFamilyRecord = some family ∧
        record.targetRepairRecord = none

structure RepairTransportEvidencePolicies where
  bridgePolicyA : CarriedRecordPolicy S_A.T InterCarrierBridgeRecord
  bridgePolicyB : CarriedRecordPolicy S_B.T InterCarrierBridgeRecord
  taxonomyPolicy : CarriedRecordPolicy S_B.T TaxonomyRecord
  sourcePackagePolicy : CarriedRecordPolicy S_A.T SourceRepairPackageRecord
  tokenPolicyA : CarriedRecordPolicy S_A.T TransportTokenRecord
  tokenPolicyB : CarriedRecordPolicy S_B.T TransportTokenRecord
  targetRepairPolicy : CarriedRecordPolicy S_B.T (TargetRepairRecord S_B)
  sourceAccessPolicy : CarriedRecordPolicy S_A.T InterfaceAccessRecordA
  targetAccessPolicy : CarriedRecordPolicy S_B.T InterfaceAccessRecordB
  schedulePolicy : CarriedRecordPolicy S_B.T ProbeScheduleRecord
  censusPolicy : CarriedRecordPolicy S_B.T FreeResponseCensusRecord
  forcingPolicy : CarriedRecordPolicy S_B.T InteractionForcingRecord
  contextFamilyPolicy : CarriedRecordPolicy S_B.T ContextFamilyRecord
  roleStatePolicy : CarriedRecordPolicy S_B.T BRoleStateRecord
  statusPolicy : CarriedRecordPolicy S_B.T
    (RepairTransportStatusRecord S_A S_B)

def RepairTransportStatusOccurrenceFor
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (claimRef : TransportClaimRef)
    (record : RepairTransportStatusRecord S_A S_B) : Prop :=
  TransportStatusRecordMatchesClaim S_A S_B claimRef record ∧
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt policies.statusPolicy record n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

def TransportClaimAllowsScaffoldOrPrime (claimRef : TransportClaimRef) : Prop :=
  match claimRef with
  | TransportClaimRef.communication _ _ _ _ => True
  | TransportClaimRef.teaching _ _ _ _ => True
  | TransportClaimRef.symbol _ _ _ _ => False

def CoercionNullEvidenceFor
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef) : Prop :=
  ∃ token : TransportTokenRecord,
    ((∃ sourcePackage bridgeRecord targetClass,
        claimRef = TransportClaimRef.communication token sourcePackage
          bridgeRecord targetClass) ∨
      (∃ sourcePackage bridgeRecord targetClass,
        claimRef = TransportClaimRef.teaching token sourcePackage
          bridgeRecord targetClass) ∨
      (∃ sourcePackage bridgeRecord familyRecord,
        claimRef = TransportClaimRef.symbol token sourcePackage bridgeRecord
          familyRecord)) ∧
      ∃ forced : FullyForcedInteraction S_B policies.forcingPolicy
        ctx.forceComparator (censusPolicy := policies.censusPolicy),
        ∃ X Q Q' FOut Readout : Type,
          ∃ qBeforeForce : X -> Q,
            ∃ qAfterForce : X -> Q',
              ∃ F_C : X -> FOut,
                ∃ r_B : FOut -> Readout,
                  Nonempty (CoercionNullCertified S_B
                    policies.targetRepairPolicy policies.forcingPolicy
                    ctx.forceComparator forced token qBeforeForce
                    qAfterForce F_C r_B)

def SymbolicEvidenceFor
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef) : Prop :=
  ∃ token sourcePackage bridgeRecord,
    ∃ family : DeclaredTransportContextFamily S_B
      policies.contextFamilyPolicy,
      claimRef = TransportClaimRef.symbol token sourcePackage bridgeRecord
        family.familyRecord ∧
        ∃ bridge : InterCarrierBridge S_A S_B ctx.bridgeDischargeComparator
          policies.bridgePolicyA policies.bridgePolicyB,
          bridge.bridgeRecord = bridgeRecord ∧
            ∃ X Q Q' FOut Readout : Type,
              ∃ qBeforeContext : X -> Q,
                ∃ qAfterContext : X -> Q',
                  ∃ F_context : X -> FOut,
                    ∃ r_B : FOut -> Readout,
                      Nonempty (SymbolicRepairEvidence S_A S_B
                        policies.sourcePackagePolicy policies.tokenPolicyA
                        policies.tokenPolicyB policies.targetRepairPolicy
                        policies.sourceAccessPolicy policies.targetAccessPolicy
                        policies.roleStatePolicy ctx.bridgeDischargeComparator
                        bridge token sourcePackage family ctx.taxonomy
                        ctx.roleComparator ctx.activationComparator
                        ctx.quotientInstall qBeforeContext qAfterContext
                        F_context r_B)

def TaughtEvidenceFor
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef) : Prop :=
  ∃ token sourcePackage bridgeRecord targetRepair,
    claimRef = TransportClaimRef.teaching token sourcePackage bridgeRecord
      targetRepair.targetChallenge ∧
      ∃ bridge : InterCarrierBridge S_A S_B ctx.bridgeDischargeComparator
        policies.bridgePolicyA policies.bridgePolicyB,
        bridge.bridgeRecord = bridgeRecord ∧
          ∃ X0 Q0 Q0' FOut0 Readout0 : Type,
            ∃ qBefore : X0 -> Q0,
              ∃ qAfter : X0 -> Q0',
                ∃ F_C : X0 -> FOut0,
                  ∃ r_B : FOut0 -> Readout0,
                    ∃ communication :
                      CommunicationTransportEvidence S_A S_B
                        policies.sourcePackagePolicy policies.tokenPolicyA
                        policies.tokenPolicyB policies.targetRepairPolicy
                        policies.sourceAccessPolicy policies.targetAccessPolicy
                        ctx bridge sourcePackage token targetRepair qBefore
                        qAfter F_C r_B,
                      ∃ schedule :
                        AAbsenceProbeSchedule S_B policies.schedulePolicy,
                        ∃ X1 Q1 Q1' FOut1 Readout1 : Type,
                          ∃ qBeforeAbsent : X1 -> Q1,
                            ∃ qAfterAbsent : X1 -> Q1',
                              ∃ F_absent : X1 -> FOut1,
                                ∃ r_absent : FOut1 -> Readout1,
                                  Nonempty (TeachingCapacityEvidence S_A S_B
                                    policies.sourcePackagePolicy
                                    policies.tokenPolicyA
                                    policies.tokenPolicyB
                                    policies.targetRepairPolicy
                                    policies.sourceAccessPolicy
                                    policies.targetAccessPolicy ctx bridge
                                    sourcePackage token targetRepair qBefore
                                    qAfter F_C r_B communication schedule
                                    qBeforeAbsent qAfterAbsent F_absent
                                    r_absent)

def CommunicatedEvidenceFor
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef) : Prop :=
  ∃ token sourcePackage bridgeRecord targetRepair,
    (claimRef = TransportClaimRef.communication token sourcePackage
        bridgeRecord targetRepair.targetChallenge ∨
      claimRef = TransportClaimRef.teaching token sourcePackage bridgeRecord
        targetRepair.targetChallenge) ∧
      ∃ bridge : InterCarrierBridge S_A S_B ctx.bridgeDischargeComparator
        policies.bridgePolicyA policies.bridgePolicyB,
        bridge.bridgeRecord = bridgeRecord ∧
          ∃ X Q Q' FOut Readout : Type,
            ∃ qBefore : X -> Q,
              ∃ qAfter : X -> Q',
                ∃ F_C : X -> FOut,
                  ∃ r_B : FOut -> Readout,
                    Nonempty (CommunicationTransportEvidence S_A S_B
                      policies.sourcePackagePolicy policies.tokenPolicyA
                      policies.tokenPolicyB policies.targetRepairPolicy
                      policies.sourceAccessPolicy policies.targetAccessPolicy
                      ctx bridge sourcePackage token targetRepair qBefore
                      qAfter F_C r_B)

def ScaffoldedOrPrimedEvidenceFor
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef) : Prop :=
  TransportClaimAllowsScaffoldOrPrime claimRef ∧
    ∃ token sourcePackage bridgeRecord targetClass,
      (claimRef = TransportClaimRef.communication token sourcePackage
          bridgeRecord targetClass ∨
        claimRef = TransportClaimRef.teaching token sourcePackage
          bridgeRecord targetClass) ∧
        ∃ claimedClass : ChallengeClassRecord,
          ∃ X Q Q' FOut Readout : Type,
            ∃ qBeforeWithAid : X -> Q,
              ∃ qAfterWithAid : X -> Q',
                ∃ F_C : X -> FOut,
                  ∃ r_B : FOut -> Readout,
                    Nonempty (ScaffoldingOrPrimingWitness S_B
                      policies.targetRepairPolicy policies.forcingPolicy
                      ctx.forceComparator token sourcePackage claimedClass
                      ctx.taxonomy ctx.quotientInstall qBeforeWithAid
                      qAfterWithAid F_C r_B
                      (censusPolicy := policies.censusPolicy)
                      (schedulePolicy := policies.schedulePolicy))

def InfluenceOnlyEvidenceFor
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef) : Prop :=
  ∃ token sourcePackage bridgeRecord targetRepair,
    (claimRef = TransportClaimRef.communication token sourcePackage
        bridgeRecord targetRepair.targetChallenge ∨
      claimRef = TransportClaimRef.teaching token sourcePackage bridgeRecord
        targetRepair.targetChallenge) ∧
      ∃ bridge : InterCarrierBridge S_A S_B ctx.bridgeDischargeComparator
        policies.bridgePolicyA policies.bridgePolicyB,
        bridge.bridgeRecord = bridgeRecord ∧
          ∃ X Q Q' FOut Readout : Type,
            ∃ qBefore : X -> Q,
              ∃ qAfter : X -> Q',
                ∃ F_other : X -> FOut,
                  ∃ r_B : FOut -> Readout,
                    Nonempty (DifferentClassInfluenceEvidence S_A S_B
                      policies.sourcePackagePolicy policies.tokenPolicyA
                      policies.tokenPolicyB policies.targetRepairPolicy ctx
                      bridge sourcePackage token targetRepair qBefore qAfter
                      F_other r_B)

def CoercionNullCase
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (record : RepairTransportStatusRecord S_A S_B) : Prop :=
  RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ∧
    record.status = RepairTransportStatus.coercion_null ∧
    ∃ forced : FullyForcedInteraction S_B policies.forcingPolicy
      ctx.forceComparator (censusPolicy := policies.censusPolicy),
      record.forcingRecord = some forced.forcingRecord ∧
        ∃ X Q Q' FOut Readout : Type,
          ∃ qBeforeForce : X -> Q,
            ∃ qAfterForce : X -> Q',
              ∃ F_C : X -> FOut,
                ∃ r_B : FOut -> Readout,
                  Nonempty (CoercionNullCertified S_B
                    policies.targetRepairPolicy policies.forcingPolicy
                    ctx.forceComparator forced record.tokenRecord qBeforeForce
                    qAfterForce F_C r_B)

def SymbolicCase
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (record : RepairTransportStatusRecord S_A S_B) : Prop :=
  RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ∧
    ¬ CoercionNullEvidenceFor S_A S_B policies ctx claimRef ∧
    record.status = RepairTransportStatus.symbolic ∧
    ∃ token sourcePackage bridgeRecord,
      ∃ family : DeclaredTransportContextFamily S_B
        policies.contextFamilyPolicy,
      claimRef = TransportClaimRef.symbol token sourcePackage bridgeRecord
        family.familyRecord ∧
        record.contextFamilyRecord = some family.familyRecord ∧
        ∃ bridge : InterCarrierBridge S_A S_B ctx.bridgeDischargeComparator
          policies.bridgePolicyA policies.bridgePolicyB,
          bridge.bridgeRecord = bridgeRecord ∧
            ∃ X Q Q' FOut Readout : Type,
              ∃ qBeforeContext : X -> Q,
                ∃ qAfterContext : X -> Q',
                  ∃ F_context : X -> FOut,
                    ∃ r_B : FOut -> Readout,
                      Nonempty (SymbolicRepairEvidence S_A S_B
                        policies.sourcePackagePolicy policies.tokenPolicyA
                        policies.tokenPolicyB policies.targetRepairPolicy
                        policies.sourceAccessPolicy policies.targetAccessPolicy
                        policies.roleStatePolicy ctx.bridgeDischargeComparator
                        bridge token sourcePackage family ctx.taxonomy
                        ctx.roleComparator ctx.activationComparator
                        ctx.quotientInstall qBeforeContext qAfterContext
                        F_context r_B)

def TaughtCase
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (record : RepairTransportStatusRecord S_A S_B) : Prop :=
  RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ∧
    ¬ CoercionNullEvidenceFor S_A S_B policies ctx claimRef ∧
    ¬ SymbolicEvidenceFor S_A S_B policies ctx claimRef ∧
    record.status = RepairTransportStatus.taught ∧
    ∃ bridgeRecord targetRepair,
      record.targetRepairRecord = some targetRepair ∧
        record.bridgeRecord = some bridgeRecord ∧
        claimRef = TransportClaimRef.teaching record.tokenRecord
          record.sourcePackageRecord bridgeRecord targetRepair.targetChallenge ∧
        ∃ bridge : InterCarrierBridge S_A S_B ctx.bridgeDischargeComparator
          policies.bridgePolicyA policies.bridgePolicyB,
          bridge.bridgeRecord = bridgeRecord ∧
            ∃ X0 Q0 Q0' FOut0 Readout0 : Type,
              ∃ qBefore : X0 -> Q0,
                ∃ qAfter : X0 -> Q0',
                  ∃ F_C : X0 -> FOut0,
                    ∃ r_B : FOut0 -> Readout0,
                      ∃ communication :
                        CommunicationTransportEvidence S_A S_B
                          policies.sourcePackagePolicy policies.tokenPolicyA
                          policies.tokenPolicyB policies.targetRepairPolicy
                          policies.sourceAccessPolicy policies.targetAccessPolicy
                          ctx bridge record.sourcePackageRecord
                          record.tokenRecord targetRepair qBefore qAfter
                          F_C r_B,
                        ∃ schedule :
                          AAbsenceProbeSchedule S_B policies.schedulePolicy,
                          ∃ X1 Q1 Q1' FOut1 Readout1 : Type,
                            ∃ qBeforeAbsent : X1 -> Q1,
                              ∃ qAfterAbsent : X1 -> Q1',
                                ∃ F_absent : X1 -> FOut1,
                                  ∃ r_absent : FOut1 -> Readout1,
                                    Nonempty (TeachingCapacityEvidence S_A S_B
                                      policies.sourcePackagePolicy
                                      policies.tokenPolicyA policies.tokenPolicyB
                                      policies.targetRepairPolicy
                                      policies.sourceAccessPolicy
                                      policies.targetAccessPolicy ctx bridge
                                      record.sourcePackageRecord
                                      record.tokenRecord targetRepair qBefore
                                      qAfter F_C r_B communication schedule
                                      qBeforeAbsent qAfterAbsent F_absent
                                      r_absent)

def CommunicatedCase
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (record : RepairTransportStatusRecord S_A S_B) : Prop :=
  RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ∧
    ¬ CoercionNullEvidenceFor S_A S_B policies ctx claimRef ∧
    ¬ SymbolicEvidenceFor S_A S_B policies ctx claimRef ∧
    ¬ TaughtEvidenceFor S_A S_B policies ctx claimRef ∧
    record.status = RepairTransportStatus.communicated ∧
    ∃ bridge : InterCarrierBridge S_A S_B ctx.bridgeDischargeComparator
      policies.bridgePolicyA policies.bridgePolicyB,
      ∃ targetRepair : TargetRepairRecord S_B,
        record.targetRepairRecord = some targetRepair ∧
          record.bridgeRecord = some bridge.bridgeRecord ∧
          ∃ X Q Q' FOut Readout : Type,
            ∃ qBefore : X -> Q,
              ∃ qAfter : X -> Q',
                ∃ F_C : X -> FOut,
                  ∃ r_B : FOut -> Readout,
                    Nonempty (CommunicationTransportEvidence S_A S_B
                      policies.sourcePackagePolicy policies.tokenPolicyA
                      policies.tokenPolicyB policies.targetRepairPolicy
                      policies.sourceAccessPolicy policies.targetAccessPolicy
                      ctx bridge record.sourcePackageRecord record.tokenRecord
                      targetRepair qBefore qAfter F_C r_B)

def ScaffoldedOrPrimedCase
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (record : RepairTransportStatusRecord S_A S_B) : Prop :=
  RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ∧
    ¬ CoercionNullEvidenceFor S_A S_B policies ctx claimRef ∧
    ¬ SymbolicEvidenceFor S_A S_B policies ctx claimRef ∧
    ¬ TaughtEvidenceFor S_A S_B policies ctx claimRef ∧
    ¬ CommunicatedEvidenceFor S_A S_B policies ctx claimRef ∧
    record.status = RepairTransportStatus.scaffolded_or_primed ∧
    TransportClaimAllowsScaffoldOrPrime claimRef ∧
    ∃ claimedClass : ChallengeClassRecord,
      ∃ X Q Q' FOut Readout : Type,
        ∃ qBeforeWithAid : X -> Q,
          ∃ qAfterWithAid : X -> Q',
            ∃ F_C : X -> FOut,
              ∃ r_B : FOut -> Readout,
                ∃ witness : ScaffoldingOrPrimingWitness S_B
                  policies.targetRepairPolicy policies.forcingPolicy
                  ctx.forceComparator record.tokenRecord
                  record.sourcePackageRecord claimedClass ctx.taxonomy
                  ctx.quotientInstall qBeforeWithAid qAfterWithAid F_C r_B
                  (censusPolicy := policies.censusPolicy)
                  (schedulePolicy := policies.schedulePolicy),
                  record.forcingRecord =
                    some witness.scaffoldedOrPrimed.interaction

def InfluenceOnlyCase
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (record : RepairTransportStatusRecord S_A S_B) : Prop :=
  RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ∧
    ¬ CoercionNullEvidenceFor S_A S_B policies ctx claimRef ∧
    ¬ SymbolicEvidenceFor S_A S_B policies ctx claimRef ∧
    ¬ TaughtEvidenceFor S_A S_B policies ctx claimRef ∧
    ¬ CommunicatedEvidenceFor S_A S_B policies ctx claimRef ∧
    ¬ ScaffoldedOrPrimedEvidenceFor S_A S_B policies ctx claimRef ∧
    record.status = RepairTransportStatus.influence_only ∧
    ∃ bridge : InterCarrierBridge S_A S_B ctx.bridgeDischargeComparator
      policies.bridgePolicyA policies.bridgePolicyB,
      ∃ targetRepair : TargetRepairRecord S_B,
        record.targetRepairRecord = some targetRepair ∧
          record.bridgeRecord = some bridge.bridgeRecord ∧
          ∃ X Q Q' FOut Readout : Type,
            ∃ qBefore : X -> Q,
              ∃ qAfter : X -> Q',
                ∃ F_other : X -> FOut,
                  ∃ r_B : FOut -> Readout,
                    Nonempty (DifferentClassInfluenceEvidence S_A S_B
                      policies.sourcePackagePolicy policies.tokenPolicyA
                      policies.tokenPolicyB policies.targetRepairPolicy ctx
                      bridge record.sourcePackageRecord record.tokenRecord
                      targetRepair qBefore qAfter F_other r_B)

def TransportRejectedCase
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (record : RepairTransportStatusRecord S_A S_B) : Prop :=
  RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ∧
    ¬ CoercionNullEvidenceFor S_A S_B policies ctx claimRef ∧
    ¬ SymbolicEvidenceFor S_A S_B policies ctx claimRef ∧
    ¬ TaughtEvidenceFor S_A S_B policies ctx claimRef ∧
    ¬ CommunicatedEvidenceFor S_A S_B policies ctx claimRef ∧
    ¬ ScaffoldedOrPrimedEvidenceFor S_A S_B policies ctx claimRef ∧
    ¬ InfluenceOnlyEvidenceFor S_A S_B policies ctx claimRef ∧
    record.status = RepairTransportStatus.transport_rejected

def CoercionNullHolds
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef) : Prop :=
  ∃ record : RepairTransportStatusRecord S_A S_B,
    RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ∧
      record.status = RepairTransportStatus.coercion_null ∧
      CoercionNullCase S_A S_B policies ctx claimRef record

def SymbolicHolds
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef) : Prop :=
  ∃ record : RepairTransportStatusRecord S_A S_B,
    RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ∧
      record.status = RepairTransportStatus.symbolic ∧
      SymbolicCase S_A S_B policies ctx claimRef record

def TaughtHolds
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef) : Prop :=
  ∃ record : RepairTransportStatusRecord S_A S_B,
    RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ∧
      record.status = RepairTransportStatus.taught ∧
      TaughtCase S_A S_B policies ctx claimRef record

def CommunicatedHolds
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef) : Prop :=
  ∃ record : RepairTransportStatusRecord S_A S_B,
    RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ∧
      record.status = RepairTransportStatus.communicated ∧
      CommunicatedCase S_A S_B policies ctx claimRef record

def ScaffoldedOrPrimedHolds
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef) : Prop :=
  ∃ record : RepairTransportStatusRecord S_A S_B,
    RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ∧
      record.status = RepairTransportStatus.scaffolded_or_primed ∧
      ScaffoldedOrPrimedCase S_A S_B policies ctx claimRef record

def InfluenceOnlyHolds
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef) : Prop :=
  ∃ record : RepairTransportStatusRecord S_A S_B,
    RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ∧
      record.status = RepairTransportStatus.influence_only ∧
      InfluenceOnlyCase S_A S_B policies ctx claimRef record

def TransportRejectedHolds
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef) : Prop :=
  ∃ record : RepairTransportStatusRecord S_A S_B,
    RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ∧
      record.status = RepairTransportStatus.transport_rejected ∧
      TransportRejectedCase S_A S_B policies ctx claimRef record

structure CompleteRepairTransportStatus
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef) where
  branchValid :
    ∃ record : RepairTransportStatusRecord S_A S_B,
      CoercionNullCase S_A S_B policies ctx claimRef record ∨
      SymbolicCase S_A S_B policies ctx claimRef record ∨
      TaughtCase S_A S_B policies ctx claimRef record ∨
      CommunicatedCase S_A S_B policies ctx claimRef record ∨
      ScaffoldedOrPrimedCase S_A S_B policies ctx claimRef record ∨
      InfluenceOnlyCase S_A S_B policies ctx claimRef record ∨
      TransportRejectedCase S_A S_B policies ctx claimRef record
  statusUnique :
    ∀ record1 record2 : RepairTransportStatusRecord S_A S_B,
      RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record1 ->
      RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record2 ->
      record1.status = record2.status

structure SameClassFalsifier
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (bridge : InterCarrierBridge S_A S_B ctx.bridgeDischargeComparator
      policies.bridgePolicyA policies.bridgePolicyB)
    (sourcePackage : SourceRepairPackageRecord)
    (token : TransportTokenRecord)
    (targetRepair : TargetRepairRecord S_B)
    {X Q Q' FOut Readout : Type}
    (qBefore : X -> Q)
    (qAfter : X -> Q')
    (F_other : X -> FOut)
    (r_B : FOut -> Readout) where
  influenceEvidence :
    DifferentClassInfluenceEvidence S_A S_B policies.sourcePackagePolicy
      policies.tokenPolicyA policies.tokenPolicyB policies.targetRepairPolicy
      ctx bridge sourcePackage token targetRepair qBefore qAfter F_other r_B
  claimLinked :
    claimRef = TransportClaimRef.communication token sourcePackage
      bridge.bridgeRecord sourcePackage.sourceChallenge
  claimedCommunication :
    CommunicatedHolds S_A S_B policies ctx claimRef

structure CoercionNullFalsifier
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (token : TransportTokenRecord)
    {X Q Q' FOut Readout : Type}
    (qBeforeForce : X -> Q)
    (qAfterForce : X -> Q')
    (F_C : X -> FOut)
    (r_B : FOut -> Readout) where
  forced :
    FullyForcedInteraction S_B policies.forcingPolicy ctx.forceComparator
      (censusPolicy := policies.censusPolicy)
  null :
    CoercionNullCertified S_B policies.targetRepairPolicy policies.forcingPolicy
      ctx.forceComparator forced token qBeforeForce qAfterForce F_C r_B
  claimLinked :
    match claimRef with
    | TransportClaimRef.communication claimToken _ _ _ => claimToken = token
    | TransportClaimRef.teaching claimToken _ _ _ => claimToken = token
    | TransportClaimRef.symbol _ _ _ _ => False
  claimedTaughtOrCommunicated :
    TaughtHolds S_A S_B policies ctx claimRef ∨
      CommunicatedHolds S_A S_B policies ctx claimRef

structure ScaffoldingFalsifier
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (token : TransportTokenRecord)
    (sourcePackage : SourceRepairPackageRecord)
    (claimedClass : ChallengeClassRecord)
    {X Q Q' FOut Readout : Type}
    (qBeforeWithAid : X -> Q)
    (qAfterWithAid : X -> Q')
    (F_C : X -> FOut)
    (r_B : FOut -> Readout) where
  scaffold :
    ScaffoldingOrPrimingWitness S_B policies.targetRepairPolicy
      policies.forcingPolicy ctx.forceComparator token sourcePackage
      claimedClass ctx.taxonomy ctx.quotientInstall qBeforeWithAid
      qAfterWithAid F_C r_B (censusPolicy := policies.censusPolicy)
      (schedulePolicy := policies.schedulePolicy)
  bridgeRecord : InterCarrierBridgeRecord
  claimLinked :
    claimRef = TransportClaimRef.teaching token sourcePackage bridgeRecord
      claimedClass
  claimedTeaching : TaughtHolds S_A S_B policies ctx claimRef

structure SymbolInstabilityFalsifier
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (bridge : InterCarrierBridge S_A S_B ctx.bridgeDischargeComparator
      policies.bridgePolicyA policies.bridgePolicyB)
    (token : TransportTokenRecord)
    (sourcePackage : SourceRepairPackageRecord)
    {X Q Q' FOut Readout : Type}
    (qBeforeContext : X -> Q)
    (qAfterContext : X -> Q')
    (F_context : X -> FOut)
    (r_B : FOut -> Readout) where
  family : DeclaredTransportContextFamily S_B policies.contextFamilyPolicy
  claimLinked :
    claimRef = TransportClaimRef.symbol token sourcePackage bridge.bridgeRecord
      family.familyRecord
  failedContext : TransportContextRecord
  failedContextMember : failedContext ∈ family.contexts
  noReactivation :
    ¬ Nonempty (ContextualRepairReactivation S_A S_B
      policies.sourcePackagePolicy policies.tokenPolicyA policies.tokenPolicyB
      policies.targetRepairPolicy policies.sourceAccessPolicy
      policies.targetAccessPolicy ctx.bridgeDischargeComparator bridge token
      sourcePackage failedContext ctx.taxonomy ctx.roleComparator
      ctx.quotientInstall qBeforeContext qAfterContext F_context r_B)

structure RoleDriftFalsifier
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (bridge : InterCarrierBridge S_A S_B ctx.bridgeDischargeComparator
      policies.bridgePolicyA policies.bridgePolicyB)
    (token : TransportTokenRecord)
    (sourcePackage : SourceRepairPackageRecord)
    {X Q Q' FOut Readout : Type}
    (qBeforeContext : X -> Q)
    (qAfterContext : X -> Q')
    (F_context : X -> FOut)
    (r_B : FOut -> Readout) where
  family : DeclaredTransportContextFamily S_B policies.contextFamilyPolicy
  claimLinked :
    claimRef = TransportClaimRef.symbol token sourcePackage bridge.bridgeRecord
      family.familyRecord
  context1 : TransportContextRecord
  context2 : TransportContextRecord
  context1Member : context1 ∈ family.contexts
  context2Member : context2 ∈ family.contexts
  r1 :
    ContextualRepairReactivation S_A S_B policies.sourcePackagePolicy
      policies.tokenPolicyA policies.tokenPolicyB policies.targetRepairPolicy
      policies.sourceAccessPolicy policies.targetAccessPolicy
      ctx.bridgeDischargeComparator bridge token sourcePackage context1
      ctx.taxonomy ctx.roleComparator ctx.quotientInstall qBeforeContext
      qAfterContext F_context r_B
  r2 :
    ContextualRepairReactivation S_A S_B policies.sourcePackagePolicy
      policies.tokenPolicyA policies.tokenPolicyB policies.targetRepairPolicy
      policies.sourceAccessPolicy policies.targetAccessPolicy
      ctx.bridgeDischargeComparator bridge token sourcePackage context2
      ctx.taxonomy ctx.roleComparator ctx.quotientInstall qBeforeContext
      qAfterContext F_context r_B
  roleDrifts : r1.targetRepair.roleRecord.roleId ≠ r2.targetRepair.roleRecord.roleId

structure UnpaidBridgeFalsifier
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef) where
  bridgeRecord : InterCarrierBridgeRecord
  claimLinked :
    ∃ token sourcePackage targetClass,
      claimRef = TransportClaimRef.communication token sourcePackage
        bridgeRecord targetClass
  claimedCommunication : CommunicatedHolds S_A S_B policies ctx claimRef
  notPaid :
    ¬ ∃ bridge : InterCarrierBridge S_A S_B ctx.bridgeDischargeComparator
      policies.bridgePolicyA policies.bridgePolicyB,
      bridge.bridgeRecord = bridgeRecord

end StatusApparatus

section Theorems

variable {FDataA : Type uA} {RuleFamilyA : Type vA}
variable {ResidualFamilyA : Type wA} {AuditAccessDataA : Type xA}
variable {InstrumentRecordA : Type yA} {LedgerEntryA : Type yA'}
variable {DefectRecordA : Type yA''} {MovePayloadA : Type yA'''}
variable {MoveRecordA : Type yA''''} {AuditRecordA : Type yA'''''}

variable {FDataB : Type uB} {RuleFamilyB : Type vB}
variable {ResidualFamilyB : Type wB} {AuditAccessDataB : Type xB}
variable {InstrumentRecordB : Type yB} {LedgerEntryB : Type yB'}
variable {DefectRecordB : Type yB''} {MovePayloadB : Type yB'''}
variable {MoveRecordB : Type yB''''} {AuditRecordB : Type yB'''''}

variable (S_A : ESystem FDataA RuleFamilyA ResidualFamilyA AuditAccessDataA
  InstrumentRecordA LedgerEntryA DefectRecordA MovePayloadA MoveRecordA
  AuditRecordA)
variable (S_B : ESystem FDataB RuleFamilyB ResidualFamilyB AuditAccessDataB
  InstrumentRecordB LedgerEntryB DefectRecordB MovePayloadB MoveRecordB
  AuditRecordB)

def ExactlyOne : List Prop -> Prop
  | p1 :: p2 :: p3 :: p4 :: p5 :: p6 :: p7 :: [] =>
      (p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p7) ∨
      (p2 ∧ ¬ p1 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p7) ∨
      (p3 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p7) ∨
      (p4 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p5 ∧ ¬ p6 ∧ ¬ p7) ∨
      (p5 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p6 ∧ ¬ p7) ∨
      (p6 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p7) ∨
      (p7 ∧ ¬ p1 ∧ ¬ p2 ∧ ¬ p3 ∧ ¬ p4 ∧ ¬ p5 ∧ ¬ p6)
  | _ => False

theorem E13_Communication
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (record : RepairTransportStatusRecord S_A S_B)
    (hOccurrence :
      RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record)
    (hStatus : record.status = RepairTransportStatus.communicated)
    (hCase : CommunicatedCase S_A S_B policies ctx claimRef record) :
    CommunicatedHolds S_A S_B policies ctx claimRef := by
  exact ⟨record, hOccurrence, hStatus, hCase⟩

theorem E13_TeachingCapacity
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (record : RepairTransportStatusRecord S_A S_B)
    (hOccurrence :
      RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record)
    (hStatus : record.status = RepairTransportStatus.taught)
    (hCase : TaughtCase S_A S_B policies ctx claimRef record) :
    TaughtHolds S_A S_B policies ctx claimRef := by
  exact ⟨record, hOccurrence, hStatus, hCase⟩

theorem E13_CoercionNull
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (record : RepairTransportStatusRecord S_A S_B)
    (hOccurrence :
      RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record)
    (hStatus : record.status = RepairTransportStatus.coercion_null)
    (hCase : CoercionNullCase S_A S_B policies ctx claimRef record) :
    CoercionNullHolds S_A S_B policies ctx claimRef := by
  exact ⟨record, hOccurrence, hStatus, hCase⟩

theorem E13_SymbolicRepair
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (record : RepairTransportStatusRecord S_A S_B)
    (hOccurrence :
      RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record)
    (hStatus : record.status = RepairTransportStatus.symbolic)
    (hCase : SymbolicCase S_A S_B policies ctx claimRef record) :
    SymbolicHolds S_A S_B policies ctx claimRef := by
  exact ⟨record, hOccurrence, hStatus, hCase⟩

theorem E13_StatusPartition
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (hComplete : CompleteRepairTransportStatus S_A S_B policies ctx claimRef) :
    ExactlyOne
      [CoercionNullHolds S_A S_B policies ctx claimRef,
       SymbolicHolds S_A S_B policies ctx claimRef,
       TaughtHolds S_A S_B policies ctx claimRef,
       CommunicatedHolds S_A S_B policies ctx claimRef,
       ScaffoldedOrPrimedHolds S_A S_B policies ctx claimRef,
       InfluenceOnlyHolds S_A S_B policies ctx claimRef,
       TransportRejectedHolds S_A S_B policies ctx claimRef] := by
  rcases hComplete.branchValid with ⟨record, hBranch⟩
  have hConflict :
      ∀ {record1 record2 : RepairTransportStatusRecord S_A S_B}
        {status1 status2 : RepairTransportStatus},
        RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record1 ->
        RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record2 ->
        record1.status = status1 ->
        record2.status = status2 ->
        status1 ≠ status2 ->
        False := by
    intro record1 record2 status1 status2 hOcc1 hOcc2 hStatus1 hStatus2 hNe
    have hEq := hComplete.statusUnique record1 record2 hOcc1 hOcc2
    rw [hStatus1, hStatus2] at hEq
    exact hNe hEq
  have hNotCoercion :
      ∀ {record : RepairTransportStatusRecord S_A S_B}
        {status : RepairTransportStatus},
        RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ->
        record.status = status ->
        status ≠ RepairTransportStatus.coercion_null ->
        ¬ CoercionNullHolds S_A S_B policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotSymbolic :
      ∀ {record : RepairTransportStatusRecord S_A S_B}
        {status : RepairTransportStatus},
        RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ->
        record.status = status ->
        status ≠ RepairTransportStatus.symbolic ->
        ¬ SymbolicHolds S_A S_B policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotTaught :
      ∀ {record : RepairTransportStatusRecord S_A S_B}
        {status : RepairTransportStatus},
        RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ->
        record.status = status ->
        status ≠ RepairTransportStatus.taught ->
        ¬ TaughtHolds S_A S_B policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotCommunicated :
      ∀ {record : RepairTransportStatusRecord S_A S_B}
        {status : RepairTransportStatus},
        RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ->
        record.status = status ->
        status ≠ RepairTransportStatus.communicated ->
        ¬ CommunicatedHolds S_A S_B policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotScaffolded :
      ∀ {record : RepairTransportStatusRecord S_A S_B}
        {status : RepairTransportStatus},
        RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ->
        record.status = status ->
        status ≠ RepairTransportStatus.scaffolded_or_primed ->
        ¬ ScaffoldedOrPrimedHolds S_A S_B policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotInfluence :
      ∀ {record : RepairTransportStatusRecord S_A S_B}
        {status : RepairTransportStatus},
        RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ->
        record.status = status ->
        status ≠ RepairTransportStatus.influence_only ->
        ¬ InfluenceOnlyHolds S_A S_B policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  have hNotRejected :
      ∀ {record : RepairTransportStatusRecord S_A S_B}
        {status : RepairTransportStatus},
        RepairTransportStatusOccurrenceFor S_A S_B policies claimRef record ->
        record.status = status ->
        status ≠ RepairTransportStatus.transport_rejected ->
        ¬ TransportRejectedHolds S_A S_B policies ctx claimRef := by
    intro record status hOcc hStatus hNe hOther
    rcases hOther with ⟨other, hOtherOcc, hOtherStatus, _hOtherCase⟩
    exact hConflict hOcc hOtherOcc hStatus hOtherStatus hNe
  rcases hBranch with
    hCoercion | hSymbolic | hTaught | hCommunicated | hScaffolded |
      hInfluence | hRejected
  · have hCoercionCase := hCoercion
    rcases hCoercion with ⟨hOcc, hStatus, _hEvidence⟩
    exact Or.inl
      ⟨⟨record, hOcc, hStatus, hCoercionCase⟩,
        hNotSymbolic hOcc hStatus (by decide),
        hNotTaught hOcc hStatus (by decide),
        hNotCommunicated hOcc hStatus (by decide),
        hNotScaffolded hOcc hStatus (by decide),
        hNotInfluence hOcc hStatus (by decide),
        hNotRejected hOcc hStatus (by decide)⟩
  · have hSymbolicCase := hSymbolic
    rcases hSymbolic with ⟨hOcc, _hNoCoercion, hStatus, _hEvidence⟩
    exact Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hSymbolicCase⟩,
        hNotCoercion hOcc hStatus (by decide),
        hNotTaught hOcc hStatus (by decide),
        hNotCommunicated hOcc hStatus (by decide),
        hNotScaffolded hOcc hStatus (by decide),
        hNotInfluence hOcc hStatus (by decide),
        hNotRejected hOcc hStatus (by decide)⟩
  · have hTaughtCase := hTaught
    rcases hTaught with
      ⟨hOcc, _hNoCoercion, _hNoSymbolic, hStatus, _hEvidence⟩
    exact Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hTaughtCase⟩,
        hNotCoercion hOcc hStatus (by decide),
        hNotSymbolic hOcc hStatus (by decide),
        hNotCommunicated hOcc hStatus (by decide),
        hNotScaffolded hOcc hStatus (by decide),
        hNotInfluence hOcc hStatus (by decide),
        hNotRejected hOcc hStatus (by decide)⟩
  · have hCommunicatedCase := hCommunicated
    rcases hCommunicated with
      ⟨hOcc, _hNoCoercion, _hNoSymbolic, _hNoTaught, hStatus, _hEvidence⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hCommunicatedCase⟩,
        hNotCoercion hOcc hStatus (by decide),
        hNotSymbolic hOcc hStatus (by decide),
        hNotTaught hOcc hStatus (by decide),
        hNotScaffolded hOcc hStatus (by decide),
        hNotInfluence hOcc hStatus (by decide),
        hNotRejected hOcc hStatus (by decide)⟩
  · have hScaffoldedCase := hScaffolded
    rcases hScaffolded with
      ⟨hOcc, _hNoCoercion, _hNoSymbolic, _hNoTaught, _hNoCommunicated,
        hStatus, _hClaimKind, _hEvidence⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hScaffoldedCase⟩,
        hNotCoercion hOcc hStatus (by decide),
        hNotSymbolic hOcc hStatus (by decide),
        hNotTaught hOcc hStatus (by decide),
        hNotCommunicated hOcc hStatus (by decide),
        hNotInfluence hOcc hStatus (by decide),
        hNotRejected hOcc hStatus (by decide)⟩
  · have hInfluenceCase := hInfluence
    rcases hInfluence with
      ⟨hOcc, _hNoCoercion, _hNoSymbolic, _hNoTaught, _hNoCommunicated,
        _hNoScaffolded, hStatus, _hEvidence⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inl
      ⟨⟨record, hOcc, hStatus, hInfluenceCase⟩,
        hNotCoercion hOcc hStatus (by decide),
        hNotSymbolic hOcc hStatus (by decide),
        hNotTaught hOcc hStatus (by decide),
        hNotCommunicated hOcc hStatus (by decide),
        hNotScaffolded hOcc hStatus (by decide),
        hNotRejected hOcc hStatus (by decide)⟩
  · have hRejectedCase := hRejected
    rcases hRejected with
      ⟨hOcc, _hNoCoercion, _hNoSymbolic, _hNoTaught, _hNoCommunicated,
        _hNoScaffolded, _hNoInfluence, hStatus⟩
    exact Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr <| Or.inr
      ⟨⟨record, hOcc, hStatus, hRejectedCase⟩,
        hNotCoercion hOcc hStatus (by decide),
        hNotSymbolic hOcc hStatus (by decide),
        hNotTaught hOcc hStatus (by decide),
        hNotCommunicated hOcc hStatus (by decide),
        hNotScaffolded hOcc hStatus (by decide),
        hNotInfluence hOcc hStatus (by decide)⟩

theorem E13_CoercionNullExcludesLowerPriority
    (policies : RepairTransportEvidencePolicies S_A S_B)
    (ctx : RepairTransportClassifierContext S_A S_B
      policies.bridgePolicyA policies.bridgePolicyB policies.taxonomyPolicy)
    (claimRef : TransportClaimRef)
    (hCoercionEvidence :
      CoercionNullEvidenceFor S_A S_B policies ctx claimRef)
    (hComplete :
      CompleteRepairTransportStatus S_A S_B policies ctx claimRef) :
    ¬ SymbolicHolds S_A S_B policies ctx claimRef ∧
      ¬ TaughtHolds S_A S_B policies ctx claimRef ∧
      ¬ CommunicatedHolds S_A S_B policies ctx claimRef ∧
      ¬ ScaffoldedOrPrimedHolds S_A S_B policies ctx claimRef ∧
      ¬ InfluenceOnlyHolds S_A S_B policies ctx claimRef ∧
      ¬ TransportRejectedHolds S_A S_B policies ctx claimRef := by
  have hPartition :=
    E13_StatusPartition S_A S_B policies ctx claimRef hComplete
  simp only [ExactlyOne] at hPartition
  rcases hPartition with
    hCoercion | hSymbolic | hTaught | hCommunicated | hScaffolded |
      hInfluence | hRejected
  · exact hCoercion.2
  · rcases hSymbolic.1 with
      ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, hNoCoercion, _rest⟩
    exact (hNoCoercion hCoercionEvidence).elim
  · rcases hTaught.1 with ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, hNoCoercion, _rest⟩
    exact (hNoCoercion hCoercionEvidence).elim
  · rcases hCommunicated.1 with
      ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, hNoCoercion, _rest⟩
    exact (hNoCoercion hCoercionEvidence).elim
  · rcases hScaffolded.1 with
      ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, hNoCoercion, _rest⟩
    exact (hNoCoercion hCoercionEvidence).elim
  · rcases hInfluence.1 with
      ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, hNoCoercion, _rest⟩
    exact (hNoCoercion hCoercionEvidence).elim
  · rcases hRejected.1 with
      ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hCaseOccurrence, hNoCoercion, _rest⟩
    exact (hNoCoercion hCoercionEvidence).elim

end Theorems

end SixBirdsFoundationsV
