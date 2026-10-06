import SixBirdsFoundationsV.Definitional.ESystem
import SixBirdsFoundationsV.Definitional.ProbeEconomy
import SixBirdsFoundationsV.Laws.E2BoundedReflexivity
import SixBirdsFoundationsV.Laws.E6E9PricedAccess
import Xi.Obstruction

open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Xi.Obstruction

universe uCap vCap

namespace SixBirdsFoundationsV

/-!
E8 control-price setup.

This setup layer mechanizes the carried control-price records, componentwise
E6/E9 multiplier surface, compressed-summary lawfulness vocabulary, and
E8.1 endogenous-budget audit/capture vocabulary from the accepted E8 six-field
normal form (`formalization/notes/examples/E8.md`).  The two status
apparatuses and E8 theorem statements are intentionally left to later
mechanization subsections.
-/

section Setup

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
variable {Probe : Type z} {XiFamily : Type z'}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
  AuditRecord)

structure ControlConstraintRecord where
  constraintId : Nat

structure ControlSignalRecord where
  signalId : Nat
  constraintRef : ControlConstraintRecord

structure PriceComponentRecord where
  componentId : Nat
  constraintRef : ControlConstraintRecord
  lambdaValue : Rat

structure ControlPriceFieldRecord where
  fieldId : Nat
  componentRefs : List PriceComponentRecord

structure CompressedSummaryRecord where
  summaryId : Nat
  fieldRef : ControlPriceFieldRecord
  value : Rat
  shadowComponent : Rat
  slackBaseline : Rat

structure ExternalObservationQuotientRecord where
  quotientId : Nat

structure PolicySupportReadoutRecord where
  readoutId : Nat

structure HeldOutPredictionRecord where
  predictionId : Nat

structure DualStabilityRecord where
  stabilityId : Nat

structure ProxyFailureRecord where
  proxyFailureId : Nat
  signalRef : ControlSignalRecord
  componentRef : PriceComponentRecord
  heldOutPredictionRef : HeldOutPredictionRecord
  stabilityRef : DualStabilityRecord

structure SlackViolationRecord where
  slackViolationId : Nat
  signalRef : ControlSignalRecord
  componentRef : PriceComponentRecord

structure SlackResidualExplanationRecord where
  explanationId : Nat
  signalRef : ControlSignalRecord
  componentRef : PriceComponentRecord

structure BudgetSettingMoveRecord where
  budgetMoveId : Nat

structure OmegaLineageRecord where
  lineageId : Nat
  budgetMoveRef : BudgetSettingMoveRecord
  originalOmegaRecord : AuditRecord
  currentReportedOmegaRecord : AuditRecord

structure BlindSpotAuditRecord where
  blindSpotAuditId : Nat
  lineageRef : OmegaLineageRecord (AuditRecord := AuditRecord)

structure ReportedLedgerHealthRecord where
  healthRecordId : Nat
  lineageRef : OmegaLineageRecord (AuditRecord := AuditRecord)
  reportsHealthy : Bool

structure MetaAuditRecord where
  metaAuditId : Nat
  budgetMoveRef : BudgetSettingMoveRecord
  lineageRef : Option (OmegaLineageRecord (AuditRecord := AuditRecord))

/-- Certified exact-rational readout for carried control signals. -/
structure ControlSignalReadoutCertified where
  value : ControlSignalRecord -> Rat
  active : ControlSignalRecord -> Prop

/-- Certified comparator tying a signal's price readout to the carried ledger. -/
structure LedgerAlignmentComparator where
  aligned :
    ControlSignalRecord -> ControlConstraintRecord -> Rat -> Rat -> Prop

/-- Certified held-out prediction comparator for proxy-failure checks. -/
structure HeldOutPredictionComparator where
  predicts : ControlSignalRecord -> HeldOutPredictionRecord -> Prop

/-- Certified perturbation-stability comparator for proxy-failure checks. -/
structure DualStabilityComparator where
  stable : ControlSignalRecord -> DualStabilityRecord -> Prop

/-- Certified comparator between reported ledger health and Omega lineage audit. -/
structure LedgerLineageAgreementComparator where
  agrees :
    ReportedLedgerHealthRecord (AuditRecord := AuditRecord) ->
      OmegaLineageRecord (AuditRecord := AuditRecord) -> Prop

/-- Shared certified comparator bundle for compressed-summary lawfulness. -/
structure SummaryLegitimacyComparators where
  sameExternalObservation :
    ExternalObservationQuotientRecord -> PolicySupportReadoutRecord ->
      PolicySupportReadoutRecord -> Prop
  summarySeparates :
    CompressedSummaryRecord -> PolicySupportReadoutRecord ->
      PolicySupportReadoutRecord -> Prop
  policySupportChanges :
    PolicySupportReadoutRecord -> PolicySupportReadoutRecord -> Prop
  heldOutPredicts :
    HeldOutPredictionRecord -> PolicySupportReadoutRecord ->
      PolicySupportReadoutRecord -> Prop
  dualStableHeldOut :
    DualStabilityRecord -> CompressedSummaryRecord -> List Rat -> Prop

structure ControlPriceComponent
    (economy : ProbeEconomy S Probe XiFamily)
    (signalPolicy : CarriedRecordPolicy S.T ControlSignalRecord)
    (componentPolicy : CarriedRecordPolicy S.T PriceComponentRecord) where
  constraintRecord : ControlConstraintRecord
  signalRecord : ControlSignalRecord
  componentRecord : PriceComponentRecord
  L_t : ActiveFamily Probe XiFamily
  move : ProbeMove Probe XiFamily
  budgetData : ExposureBudgetWitness economy move
  marginalDischarge : MarginalDischarge Probe XiFamily
  marginalCost : MarginalCost Probe XiFamily
  kkt : KKTWitness L_t budgetData marginalDischarge marginalCost
  positiveCosts : PositiveMarginalCosts marginalCost L_t
  signalCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt signalPolicy signalRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  componentCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt componentPolicy componentRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  linkedRecords :
    signalRecord.constraintRef = constraintRecord ∧
      componentRecord.constraintRef = constraintRecord ∧
      componentRecord.lambdaValue = kkt.lambda

def BindingControlComponent
    {economy : ProbeEconomy S Probe XiFamily}
    {signalPolicy : CarriedRecordPolicy S.T ControlSignalRecord}
    {componentPolicy : CarriedRecordPolicy S.T PriceComponentRecord}
    (component : ControlPriceComponent S economy signalPolicy componentPolicy) :
    Prop :=
  BindingExposureBudget component.budgetData ∧
    GenuineScarcity component.L_t component.marginalDischarge

def SlackControlComponent
    {economy : ProbeEconomy S Probe XiFamily}
    {signalPolicy : CarriedRecordPolicy S.T ControlSignalRecord}
    {componentPolicy : CarriedRecordPolicy S.T PriceComponentRecord}
    (component : ControlPriceComponent S economy signalPolicy componentPolicy) :
    Prop :=
  SlackExposureBudget component.budgetData

def ComponentSlackCollapse
    {economy : ProbeEconomy S Probe XiFamily}
    {signalPolicy : CarriedRecordPolicy S.T ControlSignalRecord}
    {componentPolicy : CarriedRecordPolicy S.T PriceComponentRecord}
    (component : ControlPriceComponent S economy signalPolicy componentPolicy) :
    Prop :=
  SlackControlComponent S component ->
    component.componentRecord.lambdaValue = 0

def ShadowPriceComponentIdentified
    {economy : ProbeEconomy S Probe XiFamily}
    {signalPolicy : CarriedRecordPolicy S.T ControlSignalRecord}
    {componentPolicy : CarriedRecordPolicy S.T PriceComponentRecord}
    (component : ControlPriceComponent S economy signalPolicy componentPolicy) :
    Prop :=
  component.componentRecord.lambdaValue = component.kkt.lambda ∧
    ComponentSlackCollapse S component

structure ControlPriceField
    (economy : ProbeEconomy S Probe XiFamily)
    (signalPolicy : CarriedRecordPolicy S.T ControlSignalRecord)
    (componentPolicy : CarriedRecordPolicy S.T PriceComponentRecord)
    (fieldPolicy : CarriedRecordPolicy S.T ControlPriceFieldRecord) where
  fieldRecord : ControlPriceFieldRecord
  declaredConstraints : List ControlConstraintRecord
  components : List (ControlPriceComponent S economy signalPolicy componentPolicy)
  nonempty : components.length > 0
  fieldCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt fieldPolicy fieldRecord n0 sourceTag generatedByS
          inScope ∧
        CarriedSource sourceTag generatedByS inScope
  completeForDeclaredConstraints :
    ∀ constraint : ControlConstraintRecord, constraint ∈ declaredConstraints ->
      ∃ component :
        ControlPriceComponent S economy signalPolicy componentPolicy,
        component ∈ components ∧ component.constraintRecord = constraint
  fieldLinksComponents :
    ∀ component :
      ControlPriceComponent S economy signalPolicy componentPolicy,
      component ∈ components ->
        component.componentRecord ∈ fieldRecord.componentRefs

structure SlackCollapseViolation
    {economy : ProbeEconomy S Probe XiFamily}
    {signalPolicy : CarriedRecordPolicy S.T ControlSignalRecord}
    {componentPolicy : CarriedRecordPolicy S.T PriceComponentRecord}
    (component : ControlPriceComponent S economy signalPolicy componentPolicy)
    (slackViolationPolicy : CarriedRecordPolicy S.T SlackViolationRecord)
    (slackResidualExplanationPolicy :
      CarriedRecordPolicy S.T SlackResidualExplanationRecord) where
  violationRecord : SlackViolationRecord
  signalReadout : ControlSignalReadoutCertified
  slack : SlackControlComponent S component
  persistentSignal :
    signalReadout.value component.signalRecord ≠ 0 ∨
      signalReadout.active component.signalRecord
  recordLinked :
    violationRecord.signalRef = component.signalRecord ∧
      violationRecord.componentRef = component.componentRecord
  unstatused :
    ¬ ∃ explanation : SlackResidualExplanationRecord,
      explanation.signalRef = component.signalRecord ∧
        explanation.componentRef = component.componentRecord ∧
        ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
          ∃ generatedByS : Bool, ∃ inScope : Bool,
            CarriedRecordAt slackResidualExplanationPolicy explanation n0
              sourceTag generatedByS inScope ∧
            CarriedSource sourceTag generatedByS inScope
  carried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt slackViolationPolicy violationRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

structure ProxyFailure
    {economy : ProbeEconomy S Probe XiFamily}
    {signalPolicy : CarriedRecordPolicy S.T ControlSignalRecord}
    {componentPolicy : CarriedRecordPolicy S.T PriceComponentRecord}
    (component : ControlPriceComponent S economy signalPolicy componentPolicy)
    (proxyFailurePolicy : CarriedRecordPolicy S.T ProxyFailureRecord) where
  failureRecord : ProxyFailureRecord
  ledgerComparator : LedgerAlignmentComparator
  predictionComparator : HeldOutPredictionComparator
  stabilityComparator : DualStabilityComparator
  heldOutPredictionRecord : HeldOutPredictionRecord
  stabilityRecord : DualStabilityRecord
  ledgerMisaligned :
    ¬ ledgerComparator.aligned component.signalRecord component.constraintRecord
      component.budgetData.spend component.budgetData.budget
  heldOutPredictionFails :
    ¬ predictionComparator.predicts component.signalRecord heldOutPredictionRecord
  dualStabilityFails :
    ¬ stabilityComparator.stable component.signalRecord stabilityRecord
  recordsLinked :
    failureRecord.signalRef = component.signalRecord ∧
      failureRecord.componentRef = component.componentRecord ∧
      failureRecord.heldOutPredictionRef = heldOutPredictionRecord ∧
      failureRecord.stabilityRef = stabilityRecord
  carried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt proxyFailurePolicy failureRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

def ComponentShadowPriceLawful
    {economy : ProbeEconomy S Probe XiFamily}
    {signalPolicy : CarriedRecordPolicy S.T ControlSignalRecord}
    {componentPolicy : CarriedRecordPolicy S.T PriceComponentRecord}
    (component : ControlPriceComponent S economy signalPolicy componentPolicy)
    (slackViolationPolicy : CarriedRecordPolicy S.T SlackViolationRecord)
    (slackResidualExplanationPolicy :
      CarriedRecordPolicy S.T SlackResidualExplanationRecord)
    (proxyFailurePolicy : CarriedRecordPolicy S.T ProxyFailureRecord) : Prop :=
  ShadowPriceComponentIdentified S component ∧
    ¬ Nonempty (
      SlackCollapseViolation S component slackViolationPolicy
        slackResidualExplanationPolicy) ∧
    ¬ Nonempty (ProxyFailure S component proxyFailurePolicy)

structure CompressedControlSummary
    (economy : ProbeEconomy S Probe XiFamily)
    (signalPolicy : CarriedRecordPolicy S.T ControlSignalRecord)
    (componentPolicy : CarriedRecordPolicy S.T PriceComponentRecord)
    (fieldPolicy : CarriedRecordPolicy S.T ControlPriceFieldRecord)
    (summaryPolicy : CarriedRecordPolicy S.T CompressedSummaryRecord) where
  summaryRecord : CompressedSummaryRecord
  field : ControlPriceField S economy signalPolicy componentPolicy fieldPolicy
  compression : List PriceComponentRecord -> Rat
  compressionLinked :
    summaryRecord.value = compression field.fieldRecord.componentRefs ∧
      summaryRecord.fieldRef = field.fieldRecord
  summaryCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt summaryPolicy summaryRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

structure SummaryPredictiveLegitimacy
    {economy : ProbeEconomy S Probe XiFamily}
    {signalPolicy : CarriedRecordPolicy S.T ControlSignalRecord}
    {componentPolicy : CarriedRecordPolicy S.T PriceComponentRecord}
    {fieldPolicy : CarriedRecordPolicy S.T ControlPriceFieldRecord}
    {summaryPolicy : CarriedRecordPolicy S.T CompressedSummaryRecord}
    (summary :
      CompressedControlSummary S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy)
    (quotientPolicy :
      CarriedRecordPolicy S.T ExternalObservationQuotientRecord)
    (readoutPolicy :
      CarriedRecordPolicy S.T PolicySupportReadoutRecord)
    (predictionPolicy :
      CarriedRecordPolicy S.T HeldOutPredictionRecord)
    (stabilityPolicy :
      CarriedRecordPolicy S.T DualStabilityRecord)
    (comparators : SummaryLegitimacyComparators) where
  quotientRecord : ExternalObservationQuotientRecord
  readoutBefore : PolicySupportReadoutRecord
  readoutAfter : PolicySupportReadoutRecord
  predictionRecord : HeldOutPredictionRecord
  stabilityRecord : DualStabilityRecord
  perturbationFamily : List Rat
  perturbationNonempty : perturbationFamily.length > 0
  sameExternalObservationCertified :
    comparators.sameExternalObservation quotientRecord readoutBefore
      readoutAfter
  summarySeparatesCertified :
    comparators.summarySeparates summary.summaryRecord readoutBefore
      readoutAfter
  policySupportChangesCertified :
    comparators.policySupportChanges readoutBefore readoutAfter
  heldOutPredictsCertified :
    comparators.heldOutPredicts predictionRecord readoutBefore
      readoutAfter
  dualStableHeldOutCertified :
    comparators.dualStableHeldOut stabilityRecord summary.summaryRecord
      perturbationFamily
  quotientCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt quotientPolicy quotientRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  predictionCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt predictionPolicy predictionRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  stabilityCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt stabilityPolicy stabilityRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  readoutBeforeCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt readoutPolicy readoutBefore n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  readoutAfterCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt readoutPolicy readoutAfter n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

def SummarySlackCollapse
    {economy : ProbeEconomy S Probe XiFamily}
    {signalPolicy : CarriedRecordPolicy S.T ControlSignalRecord}
    {componentPolicy : CarriedRecordPolicy S.T PriceComponentRecord}
    {fieldPolicy : CarriedRecordPolicy S.T ControlPriceFieldRecord}
    {summaryPolicy : CarriedRecordPolicy S.T CompressedSummaryRecord}
    (summary :
      CompressedControlSummary S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy) : Prop :=
  (∀ component :
    ControlPriceComponent S economy signalPolicy componentPolicy,
      component ∈ summary.field.components ->
        SlackControlComponent S component) ->
    summary.summaryRecord.shadowComponent =
      summary.summaryRecord.slackBaseline

def SummaryLawful
    {economy : ProbeEconomy S Probe XiFamily}
    {signalPolicy : CarriedRecordPolicy S.T ControlSignalRecord}
    {componentPolicy : CarriedRecordPolicy S.T PriceComponentRecord}
    {fieldPolicy : CarriedRecordPolicy S.T ControlPriceFieldRecord}
    {summaryPolicy : CarriedRecordPolicy S.T CompressedSummaryRecord}
    (summary :
      CompressedControlSummary S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy)
    (quotientPolicy :
      CarriedRecordPolicy S.T ExternalObservationQuotientRecord)
    (readoutPolicy :
      CarriedRecordPolicy S.T PolicySupportReadoutRecord)
    (predictionPolicy :
      CarriedRecordPolicy S.T HeldOutPredictionRecord)
    (stabilityPolicy :
      CarriedRecordPolicy S.T DualStabilityRecord)
    (comparators : SummaryLegitimacyComparators) : Prop :=
  (∃ _legitimacy :
    SummaryPredictiveLegitimacy S summary quotientPolicy readoutPolicy
      predictionPolicy stabilityPolicy comparators,
    True) ∧
    SummarySlackCollapse S summary

structure EndogenousBudgetSettingMove
    (budgetSettingMovePolicy :
      CarriedRecordPolicy S.T BudgetSettingMoveRecord) where
  moveRecord : BudgetSettingMoveRecord
  oldBudget : Rat
  newBudget : Rat
  budgetInflates : oldBudget < newBudget
  oldBudgetEntry : LedgerEntry
  newBudgetEntry : LedgerEntry
  moveCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt budgetSettingMovePolicy moveRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  oldBudgetEntryInLedger : oldBudgetEntry ∈ S.Lambda_S.ledgerEntries
  newBudgetEntryInLedger : newBudgetEntry ∈ S.Lambda_S.ledgerEntries

def OmegaLineageBlindSpot {e y z : Nat}
    (Cxi : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y) (originalOmega : Mat z z)
    (witness : Vec z) : Prop :=
  quad (adequacyDefect Cxi L D KLLdagger originalOmega) witness > 0

structure OmegaLineageAudit
    (budgetSettingMovePolicy :
      CarriedRecordPolicy S.T BudgetSettingMoveRecord)
    (lineagePolicy :
      CarriedRecordPolicy S.T
        (OmegaLineageRecord (AuditRecord := AuditRecord)))
    (blindSpotPolicy :
      CarriedRecordPolicy S.T
        (BlindSpotAuditRecord (AuditRecord := AuditRecord)))
    {e y z : Nat}
    (Cxi : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y) (originalOmega : Mat z z)
    (witness : Vec z) where
  lineageRecord : OmegaLineageRecord (AuditRecord := AuditRecord)
  blindSpotRecord : BlindSpotAuditRecord (AuditRecord := AuditRecord)
  budgetMove : EndogenousBudgetSettingMove S budgetSettingMovePolicy
  originalBlindSpotPersists :
    OmegaLineageBlindSpot Cxi L D KLLdagger originalOmega witness
  lineageLinked :
    lineageRecord.budgetMoveRef = budgetMove.moveRecord ∧
      blindSpotRecord.lineageRef = lineageRecord
  carried :
    (∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt lineagePolicy lineageRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope) ∧
      ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
        ∃ generatedByS : Bool, ∃ inScope : Bool,
          CarriedRecordAt blindSpotPolicy blindSpotRecord n0 sourceTag
            generatedByS inScope ∧
          CarriedSource sourceTag generatedByS inScope

structure NoCaptureLineageAudit
    (budgetSettingMovePolicy :
      CarriedRecordPolicy S.T BudgetSettingMoveRecord)
    (lineagePolicy :
      CarriedRecordPolicy S.T
        (OmegaLineageRecord (AuditRecord := AuditRecord)))
    (reportedHealthPolicy :
      CarriedRecordPolicy S.T
        (ReportedLedgerHealthRecord (AuditRecord := AuditRecord)))
    {e y z : Nat}
    (Cxi : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y) (originalOmega : Mat z z)
    (witness : Vec z) where
  lineageRecord : OmegaLineageRecord (AuditRecord := AuditRecord)
  budgetMove : EndogenousBudgetSettingMove S budgetSettingMovePolicy
  reportedHealth : ReportedLedgerHealthRecord (AuditRecord := AuditRecord)
  agreementComparator : LedgerLineageAgreementComparator (AuditRecord := AuditRecord)
  noOriginalBlindSpotPersists :
    ¬ OmegaLineageBlindSpot Cxi L D KLLdagger originalOmega witness
  agreesWithReportedLedger :
    agreementComparator.agrees reportedHealth lineageRecord
  lineageLinked :
    lineageRecord.budgetMoveRef = budgetMove.moveRecord ∧
      reportedHealth.lineageRef = lineageRecord
  carried :
    (∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt lineagePolicy lineageRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope) ∧
      ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
        ∃ generatedByS : Bool, ∃ inScope : Bool,
          CarriedRecordAt reportedHealthPolicy reportedHealth n0 sourceTag
            generatedByS inScope ∧
          CarriedSource sourceTag generatedByS inScope

structure ReportedLedgerHealth
    (reportedHealthPolicy :
      CarriedRecordPolicy S.T
        (ReportedLedgerHealthRecord (AuditRecord := AuditRecord))) where
  healthRecord : ReportedLedgerHealthRecord (AuditRecord := AuditRecord)
  lineageRecord : OmegaLineageRecord (AuditRecord := AuditRecord)
  healthLinked : healthRecord.lineageRef = lineageRecord
  reportedHealthy : healthRecord.reportsHealthy = true
  healthCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt reportedHealthPolicy healthRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

structure ResidualDischargeAudit
    (budgetSettingMovePolicy :
      CarriedRecordPolicy S.T BudgetSettingMoveRecord)
    (metaAuditPolicy :
      CarriedRecordPolicy S.T
        (MetaAuditRecord (AuditRecord := AuditRecord))) where
  metaAuditRecord : MetaAuditRecord (AuditRecord := AuditRecord)
  budgetMove : EndogenousBudgetSettingMove S budgetSettingMovePolicy
  lineageRecord : OmegaLineageRecord (AuditRecord := AuditRecord)
  residualBefore : Rat
  residualAfter : Rat
  dischargesResidual : residualAfter < residualBefore
  linkedToOriginalLineage :
    metaAuditRecord.budgetMoveRef = budgetMove.moveRecord ∧
      metaAuditRecord.lineageRef = some lineageRecord ∧
      lineageRecord.budgetMoveRef = budgetMove.moveRecord
  carried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt metaAuditPolicy metaAuditRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

structure BudgetInflationAudit
    (budgetSettingMovePolicy :
      CarriedRecordPolicy S.T BudgetSettingMoveRecord)
    (lineagePolicy :
      CarriedRecordPolicy S.T
        (OmegaLineageRecord (AuditRecord := AuditRecord)))
    (blindSpotPolicy :
      CarriedRecordPolicy S.T
        (BlindSpotAuditRecord (AuditRecord := AuditRecord)))
    (reportedHealthPolicy :
      CarriedRecordPolicy S.T
        (ReportedLedgerHealthRecord (AuditRecord := AuditRecord)))
    (metaAuditPolicy :
      CarriedRecordPolicy S.T
        (MetaAuditRecord (AuditRecord := AuditRecord)))
    {e y z : Nat}
    (Cxi : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y) (originalOmega : Mat z z)
    (witness : Vec z) where
  metaAuditRecord : MetaAuditRecord (AuditRecord := AuditRecord)
  budgetMove : EndogenousBudgetSettingMove S budgetSettingMovePolicy
  lineageAudit :
    OmegaLineageAudit S budgetSettingMovePolicy lineagePolicy blindSpotPolicy
      Cxi L D KLLdagger originalOmega witness
  reportedHealth : ReportedLedgerHealth S reportedHealthPolicy
  reportsHealth : reportedHealth.healthRecord.reportsHealthy = true
  budgetInflates : budgetMove.oldBudget < budgetMove.newBudget
  blindSpotPersists :
    OmegaLineageBlindSpot Cxi L D KLLdagger originalOmega witness
  /--
  Regression guard mirroring the toy-lab wrong-lineage capture control: the
  Omega-lineage audit whose blind spot is credited must be about the same
  budget-setting move whose inflation is being classified.
  -/
  lineageBudgetMoveLinked :
    lineageAudit.budgetMove.moveRecord = budgetMove.moveRecord
  reportedHealthLinked :
    reportedHealth.lineageRecord = lineageAudit.lineageRecord
  linkedToOriginalLineage :
    metaAuditRecord.budgetMoveRef = budgetMove.moveRecord ∧
      metaAuditRecord.lineageRef = some lineageAudit.lineageRecord
  carried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt metaAuditPolicy metaAuditRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

/--
Regression-style projection of `lineageBudgetMoveLinked`: if the nested
Omega-lineage audit is about a different move than `otherMove`, then the
classified budget-inflation move is also different from `otherMove`.
-/
theorem BudgetInflationAudit.lineageMustMatchClassifiedMove
    {budgetSettingMovePolicy :
      CarriedRecordPolicy S.T BudgetSettingMoveRecord}
    {lineagePolicy :
      CarriedRecordPolicy S.T
        (OmegaLineageRecord (AuditRecord := AuditRecord))}
    {blindSpotPolicy :
      CarriedRecordPolicy S.T
        (BlindSpotAuditRecord (AuditRecord := AuditRecord))}
    {reportedHealthPolicy :
      CarriedRecordPolicy S.T
        (ReportedLedgerHealthRecord (AuditRecord := AuditRecord))}
    {metaAuditPolicy :
      CarriedRecordPolicy S.T
        (MetaAuditRecord (AuditRecord := AuditRecord))}
    {e y z : Nat}
    {Cxi : Mat e e} {L : Mat y e} {D : Mat z e}
    {KLLdagger : Mat y y} {originalOmega : Mat z z}
    {witness : Vec z}
    (audit :
      BudgetInflationAudit S budgetSettingMovePolicy lineagePolicy
        blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi L D
        KLLdagger originalOmega witness)
    (otherMove : EndogenousBudgetSettingMove S budgetSettingMovePolicy)
    (hDifferent :
      audit.lineageAudit.budgetMove.moveRecord ≠ otherMove.moveRecord) :
    audit.budgetMove.moveRecord ≠ otherMove.moveRecord := by
  rw [← audit.lineageBudgetMoveLinked]
  exact hDifferent

structure MetaAuditBoundedByE2
    (budgetSettingMovePolicy :
      CarriedRecordPolicy S.T BudgetSettingMoveRecord) where
  budgetMove : EndogenousBudgetSettingMove S budgetSettingMovePolicy
  lineageRecord : Option (OmegaLineageRecord (AuditRecord := AuditRecord))
  healthRecord :
    Option (ReportedLedgerHealthRecord (AuditRecord := AuditRecord))
  tower : Nat -> Option (CarriedInstrumentLevel S)
  n : Nat
  z : S.T.Z
  measure : AuditTowerCapacityMeasure S
  realizable : CapacityRealizableTower S tower n
  admissible : CapacityAdmissible S measure tower n z

structure CaptureClaimFalsifier
    (budgetSettingMovePolicy :
      CarriedRecordPolicy S.T BudgetSettingMoveRecord)
    (lineagePolicy :
      CarriedRecordPolicy S.T
        (OmegaLineageRecord (AuditRecord := AuditRecord)))
    (reportedHealthPolicy :
      CarriedRecordPolicy S.T
        (ReportedLedgerHealthRecord (AuditRecord := AuditRecord)))
    (metaAuditPolicy :
      CarriedRecordPolicy S.T
        (MetaAuditRecord (AuditRecord := AuditRecord)))
    {e y z : Nat}
    (Cxi : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y) (originalOmega : Mat z z)
    (witness : Vec z) where
  noCaptureAudit :
    NoCaptureLineageAudit S budgetSettingMovePolicy lineagePolicy
      reportedHealthPolicy Cxi L D KLLdagger originalOmega
      witness
  agreesWithOriginalLineage :
    noCaptureAudit.agreementComparator.agrees noCaptureAudit.reportedHealth
      noCaptureAudit.lineageRecord
  claimedCaptureRecord : MetaAuditRecord (AuditRecord := AuditRecord)
  claimLinked :
    claimedCaptureRecord.budgetMoveRef =
        noCaptureAudit.budgetMove.moveRecord ∧
      claimedCaptureRecord.lineageRef =
        some noCaptureAudit.lineageRecord
  carriedClaim :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt metaAuditPolicy claimedCaptureRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

def CaptureClaimRejected
    {budgetSettingMovePolicy :
      CarriedRecordPolicy S.T BudgetSettingMoveRecord}
    {lineagePolicy :
      CarriedRecordPolicy S.T
        (OmegaLineageRecord (AuditRecord := AuditRecord))}
    {reportedHealthPolicy :
      CarriedRecordPolicy S.T
        (ReportedLedgerHealthRecord (AuditRecord := AuditRecord))}
    {metaAuditPolicy :
      CarriedRecordPolicy S.T
        (MetaAuditRecord (AuditRecord := AuditRecord))}
    {e y z : Nat}
    {Cxi : Mat e e} {L : Mat y e} {D : Mat z e}
    {KLLdagger : Mat y y} {originalOmega : Mat z z}
    {witness : Vec z}
    (falsifier :
      CaptureClaimFalsifier S budgetSettingMovePolicy lineagePolicy
        reportedHealthPolicy metaAuditPolicy Cxi L D KLLdagger
        originalOmega witness) : Prop :=
  falsifier.noCaptureAudit.agreementComparator.agrees
    falsifier.noCaptureAudit.reportedHealth
    falsifier.noCaptureAudit.lineageRecord

end Setup

section StatusApparatus

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
variable {Probe : Type z} {XiFamily : Type z'}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
  AuditRecord)

variable (economy : ProbeEconomy S Probe XiFamily)
variable (signalPolicy : CarriedRecordPolicy S.T ControlSignalRecord)
variable (componentPolicy : CarriedRecordPolicy S.T PriceComponentRecord)
variable (fieldPolicy : CarriedRecordPolicy S.T ControlPriceFieldRecord)
variable (summaryPolicy : CarriedRecordPolicy S.T CompressedSummaryRecord)
variable (slackViolationPolicy :
  CarriedRecordPolicy S.T SlackViolationRecord)
variable (slackResidualExplanationPolicy :
  CarriedRecordPolicy S.T SlackResidualExplanationRecord)
variable (proxyFailurePolicy :
  CarriedRecordPolicy S.T ProxyFailureRecord)
variable (quotientPolicy :
  CarriedRecordPolicy S.T ExternalObservationQuotientRecord)
variable (readoutPolicy :
  CarriedRecordPolicy S.T PolicySupportReadoutRecord)
variable (predictionPolicy :
  CarriedRecordPolicy S.T HeldOutPredictionRecord)
variable (stabilityPolicy :
  CarriedRecordPolicy S.T DualStabilityRecord)
variable (summaryComparators : SummaryLegitimacyComparators)

inductive ControlPriceClaimKind where
  | component
  | field
  | summary
  deriving DecidableEq, Repr

inductive ControlPriceStatus where
  | slack_obstructed
  | proxy_obstructed
  | summary_redescription
  | component_lawful
  | field_lawful
  | summary_lawful
  | incomplete_or_unpriced
  deriving DecidableEq, Repr

structure ControlPriceStatusRecord where
  claimKind : ControlPriceClaimKind
  componentRecord : Option PriceComponentRecord
  fieldRecord : Option ControlPriceFieldRecord
  summaryRecord : Option CompressedSummaryRecord
  status : ControlPriceStatus
  supportingLedgerEntries : List LedgerEntry
  supportingAuditRecords : List AuditRecord

inductive ControlPriceClaimRef where
  | component (componentRecord : PriceComponentRecord)
  | field (fieldRecord : ControlPriceFieldRecord)
  | summary (summaryRecord : CompressedSummaryRecord)

def ControlPriceStatusRecordMatchesClaim
    (claimRef : ControlPriceClaimRef)
    (record :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  match claimRef with
  | ControlPriceClaimRef.component componentRef =>
      record.claimKind = ControlPriceClaimKind.component ∧
        record.componentRecord = some componentRef ∧
        record.fieldRecord = none ∧
        record.summaryRecord = none
  | ControlPriceClaimRef.field fieldRef =>
      record.claimKind = ControlPriceClaimKind.field ∧
        record.componentRecord = none ∧
        record.fieldRecord = some fieldRef ∧
        record.summaryRecord = none
  | ControlPriceClaimRef.summary summaryRef =>
      record.claimKind = ControlPriceClaimKind.summary ∧
        record.componentRecord = none ∧
        record.fieldRecord = none ∧
        record.summaryRecord = some summaryRef

def ControlPriceStatusOccurrenceFor
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef)
    (record :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  ControlPriceStatusRecordMatchesClaim claimRef record ∧
    (∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt statusPolicy record n0 sourceTag generatedByS
          inScope ∧
        CarriedSource sourceTag generatedByS inScope) ∧
    (∀ entry : LedgerEntry, entry ∈ record.supportingLedgerEntries ->
      entry ∈ S.Lambda_S.ledgerEntries) ∧
    ∀ auditRecord : AuditRecord, auditRecord ∈ record.supportingAuditRecords ->
      HasCarriedRecordEvidence S.auditRecordPolicy auditRecord

def ControlClaimContainsComponent
    (claimRef : ControlPriceClaimRef)
    (component :
      ControlPriceComponent S economy signalPolicy componentPolicy) : Prop :=
  match claimRef with
  | ControlPriceClaimRef.component componentRef =>
      componentRef = component.componentRecord
  | ControlPriceClaimRef.field fieldRef =>
      ∃ field : ControlPriceField S economy signalPolicy componentPolicy
          fieldPolicy,
        field.fieldRecord = fieldRef ∧ component ∈ field.components
  | ControlPriceClaimRef.summary summaryRef =>
      ∃ summary :
        CompressedControlSummary S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy,
        summary.summaryRecord = summaryRef ∧
          component ∈ summary.field.components

def SlackObstructedCase
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef)
    (record :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  ControlPriceStatusOccurrenceFor S statusPolicy claimRef record ∧
    ((∃ component :
      ControlPriceComponent S economy signalPolicy componentPolicy,
      ∃ _violation :
        SlackCollapseViolation S component slackViolationPolicy
          slackResidualExplanationPolicy,
        ControlClaimContainsComponent S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy claimRef component) ∨
      ∃ summary :
        CompressedControlSummary S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy,
        claimRef = ControlPriceClaimRef.summary summary.summaryRecord ∧
          (∃ _legitimacy :
            SummaryPredictiveLegitimacy S summary quotientPolicy
              readoutPolicy predictionPolicy stabilityPolicy
              summaryComparators,
            True) ∧
          ¬ SummarySlackCollapse S summary) ∧
    record.status = ControlPriceStatus.slack_obstructed

def ProxyObstructedCase
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef)
    (record :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  (¬ ∃ higherRecord :
    ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
      SlackObstructedCase S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy quotientPolicy readoutPolicy
        predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    ControlPriceStatusOccurrenceFor S statusPolicy claimRef record ∧
    ∃ component :
      ControlPriceComponent S economy signalPolicy componentPolicy,
      ∃ _failure : ProxyFailure S component proxyFailurePolicy,
        ControlClaimContainsComponent S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy claimRef component ∧
          record.status = ControlPriceStatus.proxy_obstructed

def SummaryRedescriptionCase
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef)
    (record :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  (¬ ∃ higherRecord :
    ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
      SlackObstructedCase S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy quotientPolicy readoutPolicy
        predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      ProxyObstructedCase S economy signalPolicy componentPolicy fieldPolicy
        summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    ControlPriceStatusOccurrenceFor S statusPolicy claimRef record ∧
    ∃ summary :
      CompressedControlSummary S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy,
      claimRef = ControlPriceClaimRef.summary summary.summaryRecord ∧
        (¬ ∃ _legitimacy :
          SummaryPredictiveLegitimacy S summary quotientPolicy readoutPolicy
            predictionPolicy stabilityPolicy summaryComparators,
          True) ∧
        record.status = ControlPriceStatus.summary_redescription

def ComponentLawfulCase
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef)
    (record :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  (¬ ∃ higherRecord :
    ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
      SlackObstructedCase S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy quotientPolicy readoutPolicy
        predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      ProxyObstructedCase S economy signalPolicy componentPolicy fieldPolicy
        summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      SummaryRedescriptionCase S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    ControlPriceStatusOccurrenceFor S statusPolicy claimRef record ∧
    ∃ component :
      ControlPriceComponent S economy signalPolicy componentPolicy,
      claimRef = ControlPriceClaimRef.component component.componentRecord ∧
        ComponentShadowPriceLawful S component slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy ∧
        record.status = ControlPriceStatus.component_lawful

def FieldLawfulCase
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef)
    (record :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  (¬ ∃ higherRecord :
    ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
      SlackObstructedCase S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy quotientPolicy readoutPolicy
        predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      ProxyObstructedCase S economy signalPolicy componentPolicy fieldPolicy
        summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      SummaryRedescriptionCase S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      ComponentLawfulCase S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    ControlPriceStatusOccurrenceFor S statusPolicy claimRef record ∧
    ∃ field :
      ControlPriceField S economy signalPolicy componentPolicy fieldPolicy,
      claimRef = ControlPriceClaimRef.field field.fieldRecord ∧
        (∀ component :
          ControlPriceComponent S economy signalPolicy componentPolicy,
          component ∈ field.components ->
            ComponentShadowPriceLawful S component slackViolationPolicy
              slackResidualExplanationPolicy proxyFailurePolicy) ∧
        record.status = ControlPriceStatus.field_lawful

def SummaryLawfulCase
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef)
    (record :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  (¬ ∃ higherRecord :
    ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
      SlackObstructedCase S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy quotientPolicy readoutPolicy
        predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      ProxyObstructedCase S economy signalPolicy componentPolicy fieldPolicy
        summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      SummaryRedescriptionCase S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      ComponentLawfulCase S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      FieldLawfulCase S economy signalPolicy componentPolicy fieldPolicy
        summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef
        higherRecord) ∧
    ControlPriceStatusOccurrenceFor S statusPolicy claimRef record ∧
    ∃ summary :
      CompressedControlSummary S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy,
      claimRef = ControlPriceClaimRef.summary summary.summaryRecord ∧
        SummaryLawful S summary quotientPolicy readoutPolicy
          predictionPolicy stabilityPolicy summaryComparators ∧
        record.status = ControlPriceStatus.summary_lawful

def IncompleteOrUnpricedCase
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef)
    (record :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  (¬ ∃ higherRecord :
    ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
      SlackObstructedCase S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy quotientPolicy readoutPolicy
        predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      ProxyObstructedCase S economy signalPolicy componentPolicy fieldPolicy
        summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      SummaryRedescriptionCase S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      ComponentLawfulCase S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      FieldLawfulCase S economy signalPolicy componentPolicy fieldPolicy
        summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef
        higherRecord) ∧
    (¬ ∃ higherRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      SummaryLawfulCase S economy signalPolicy componentPolicy fieldPolicy
        summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef
        higherRecord) ∧
    ControlPriceStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = ControlPriceStatus.incomplete_or_unpriced

def SlackObstructedHolds
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef) : Prop :=
  ∃ record :
    ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
    SlackObstructedCase S economy signalPolicy componentPolicy fieldPolicy
      summaryPolicy slackViolationPolicy slackResidualExplanationPolicy
      quotientPolicy readoutPolicy predictionPolicy stabilityPolicy
      summaryComparators statusPolicy claimRef record

def ProxyObstructedHolds
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef) : Prop :=
  ∃ record :
    ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
    ProxyObstructedCase S economy signalPolicy componentPolicy fieldPolicy
      summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef record

def SummaryRedescriptionHolds
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef) : Prop :=
  ∃ record :
    ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
    SummaryRedescriptionCase S economy signalPolicy componentPolicy
      fieldPolicy summaryPolicy slackViolationPolicy
      slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef record

def ComponentLawfulHolds
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef) : Prop :=
  ∃ record :
    ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
    ComponentLawfulCase S economy signalPolicy componentPolicy fieldPolicy
      summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef record

def FieldLawfulHolds
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef) : Prop :=
  ∃ record :
    ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
    FieldLawfulCase S economy signalPolicy componentPolicy fieldPolicy
      summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef record

def SummaryLawfulHolds
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef) : Prop :=
  ∃ record :
    ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
    SummaryLawfulCase S economy signalPolicy componentPolicy fieldPolicy
      summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef record

def IncompleteOrUnpricedHolds
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef) : Prop :=
  ∃ record :
    ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
    IncompleteOrUnpricedCase S economy signalPolicy componentPolicy
      fieldPolicy summaryPolicy slackViolationPolicy
      slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef record

def CompleteControlPriceStatus
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef) : Prop :=
  (∃ record :
    ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
    ControlPriceStatusOccurrenceFor S statusPolicy claimRef record ∧
      (SlackObstructedCase S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy quotientPolicy readoutPolicy
          predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef record ∨
        ProxyObstructedCase S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy
          claimRef record ∨
        SummaryRedescriptionCase S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef record ∨
        ComponentLawfulCase S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef record ∨
        FieldLawfulCase S economy signalPolicy componentPolicy fieldPolicy
          summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef record ∨
        SummaryLawfulCase S economy signalPolicy componentPolicy fieldPolicy
          summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef record ∨
        IncompleteOrUnpricedCase S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef record)) ∧
    ∀ record1 record2 :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      ControlPriceStatusOccurrenceFor S statusPolicy claimRef record1 ->
      ControlPriceStatusOccurrenceFor S statusPolicy claimRef record2 ->
      record1.status = record2.status

variable (budgetSettingMovePolicy :
  CarriedRecordPolicy S.T BudgetSettingMoveRecord)
variable (lineagePolicy :
  CarriedRecordPolicy S.T
    (OmegaLineageRecord (AuditRecord := AuditRecord)))
variable (blindSpotPolicy :
  CarriedRecordPolicy S.T
    (BlindSpotAuditRecord (AuditRecord := AuditRecord)))
variable (reportedHealthPolicy :
  CarriedRecordPolicy S.T
    (ReportedLedgerHealthRecord (AuditRecord := AuditRecord)))
variable (metaAuditPolicy :
  CarriedRecordPolicy S.T
    (MetaAuditRecord (AuditRecord := AuditRecord)))
variable {eDim yDim zDim : Nat}
variable (Cxi : Mat eDim eDim) (Lxi : Mat yDim eDim)
variable (Dxi : Mat zDim eDim) (KLLdagger : Mat yDim yDim)
variable (originalOmega : Mat zDim zDim) (xiWitness : Vec zDim)

inductive BudgetAuditStatus where
  | residual_discharge_verified
  | capture_detected
  | capture_claim_rejected
  | meta_audit_capacity_blocked
  | meta_audit_missing
  deriving DecidableEq, Repr

structure BudgetAuditStatusRecord where
  budgetMoveRecord : Option BudgetSettingMoveRecord
  lineageRecord : Option (OmegaLineageRecord (AuditRecord := AuditRecord))
  healthRecord :
    Option (ReportedLedgerHealthRecord (AuditRecord := AuditRecord))
  metaAuditRecord : Option (MetaAuditRecord (AuditRecord := AuditRecord))
  status : BudgetAuditStatus
  supportingLedgerEntries : List LedgerEntry
  supportingAuditRecords : List AuditRecord

structure BudgetAuditClaimRef where
  budgetMoveRecord : BudgetSettingMoveRecord
  lineageRecord : Option (OmegaLineageRecord (AuditRecord := AuditRecord))
  healthRecord :
    Option (ReportedLedgerHealthRecord (AuditRecord := AuditRecord))

def BudgetAuditStatusRecordMatchesClaim
    (claimRef : BudgetAuditClaimRef (AuditRecord := AuditRecord))
    (record :
      BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  record.budgetMoveRecord = some claimRef.budgetMoveRecord ∧
    record.lineageRecord = claimRef.lineageRecord ∧
    record.healthRecord = claimRef.healthRecord

def BudgetAuditStatusOccurrenceFor
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : BudgetAuditClaimRef (AuditRecord := AuditRecord))
    (record :
      BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  BudgetAuditStatusRecordMatchesClaim claimRef record ∧
    (∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt statusPolicy record n0 sourceTag generatedByS
          inScope ∧
        CarriedSource sourceTag generatedByS inScope) ∧
    (∀ entry : LedgerEntry, entry ∈ record.supportingLedgerEntries ->
      entry ∈ S.Lambda_S.ledgerEntries) ∧
    ∀ auditRecord : AuditRecord, auditRecord ∈ record.supportingAuditRecords ->
      HasCarriedRecordEvidence S.auditRecordPolicy auditRecord

def CaptureClaimRejectedCase
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : BudgetAuditClaimRef (AuditRecord := AuditRecord))
    (record :
      BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  BudgetAuditStatusOccurrenceFor S statusPolicy claimRef record ∧
    ∃ falsifier :
      CaptureClaimFalsifier S budgetSettingMovePolicy lineagePolicy
        reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi KLLdagger
        originalOmega xiWitness,
      CaptureClaimRejected S falsifier ∧
        claimRef.budgetMoveRecord =
          falsifier.noCaptureAudit.budgetMove.moveRecord ∧
        claimRef.lineageRecord =
          some falsifier.noCaptureAudit.lineageRecord ∧
        claimRef.healthRecord =
          some falsifier.noCaptureAudit.reportedHealth ∧
        record.status = BudgetAuditStatus.capture_claim_rejected ∧
        record.budgetMoveRecord =
          some falsifier.noCaptureAudit.budgetMove.moveRecord ∧
        record.lineageRecord =
          some falsifier.noCaptureAudit.lineageRecord ∧
        record.healthRecord =
          some falsifier.noCaptureAudit.reportedHealth ∧
        record.metaAuditRecord = some falsifier.claimedCaptureRecord

def CaptureDetectedCase
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : BudgetAuditClaimRef (AuditRecord := AuditRecord))
    (record :
      BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  (¬ ∃ higherRecord :
    BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
      CaptureClaimRejectedCase S budgetSettingMovePolicy lineagePolicy
        reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi KLLdagger
        originalOmega xiWitness statusPolicy claimRef higherRecord) ∧
    BudgetAuditStatusOccurrenceFor S statusPolicy claimRef record ∧
    ∃ audit :
      BudgetInflationAudit S budgetSettingMovePolicy lineagePolicy
        blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
        KLLdagger originalOmega xiWitness,
      audit.reportedHealth.healthRecord.reportsHealthy = true ∧
        audit.budgetMove.oldBudget < audit.budgetMove.newBudget ∧
        OmegaLineageBlindSpot Cxi Lxi Dxi KLLdagger originalOmega
          xiWitness ∧
        claimRef.budgetMoveRecord = audit.budgetMove.moveRecord ∧
        claimRef.lineageRecord = some audit.lineageAudit.lineageRecord ∧
        claimRef.healthRecord = some audit.reportedHealth.healthRecord ∧
        record.status = BudgetAuditStatus.capture_detected ∧
        record.budgetMoveRecord = some audit.budgetMove.moveRecord ∧
        record.lineageRecord = some audit.lineageAudit.lineageRecord ∧
        record.healthRecord = some audit.reportedHealth.healthRecord ∧
        record.metaAuditRecord = some audit.metaAuditRecord

def ResidualDischargeVerifiedCase
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : BudgetAuditClaimRef (AuditRecord := AuditRecord))
    (record :
      BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  (¬ ∃ higherRecord :
    BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
      CaptureClaimRejectedCase S budgetSettingMovePolicy lineagePolicy
        reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi KLLdagger
        originalOmega xiWitness statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      CaptureDetectedCase S budgetSettingMovePolicy lineagePolicy
        blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
        KLLdagger originalOmega xiWitness statusPolicy claimRef
        higherRecord) ∧
    BudgetAuditStatusOccurrenceFor S statusPolicy claimRef record ∧
    ∃ audit : ResidualDischargeAudit S budgetSettingMovePolicy
        metaAuditPolicy,
      audit.residualAfter < audit.residualBefore ∧
        claimRef.budgetMoveRecord = audit.budgetMove.moveRecord ∧
        claimRef.lineageRecord = some audit.lineageRecord ∧
        claimRef.healthRecord = none ∧
        record.status = BudgetAuditStatus.residual_discharge_verified ∧
        record.budgetMoveRecord = some audit.budgetMove.moveRecord ∧
        record.lineageRecord = some audit.lineageRecord ∧
        record.healthRecord = none ∧
        record.metaAuditRecord = some audit.metaAuditRecord

def MetaAuditCapacityBlockedCase
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : BudgetAuditClaimRef (AuditRecord := AuditRecord))
    (record :
      BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  (¬ ∃ higherRecord :
    BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
      CaptureClaimRejectedCase S budgetSettingMovePolicy lineagePolicy
        reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi KLLdagger
        originalOmega xiWitness statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      CaptureDetectedCase S budgetSettingMovePolicy lineagePolicy
        blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
        KLLdagger originalOmega xiWitness statusPolicy claimRef
        higherRecord) ∧
    (¬ ∃ higherRecord :
      BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      ResidualDischargeVerifiedCase S budgetSettingMovePolicy
        lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
        Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
        claimRef higherRecord) ∧
    BudgetAuditStatusOccurrenceFor S statusPolicy claimRef record ∧
    ∃ bound :
      MetaAuditBoundedByE2.{u, v, w, x, y, y', y'', y''', y'''',
        y''''', uCap, vCap} S budgetSettingMovePolicy,
      claimRef.budgetMoveRecord = bound.budgetMove.moveRecord ∧
        claimRef.lineageRecord = bound.lineageRecord ∧
        claimRef.healthRecord = bound.healthRecord ∧
        CapacitySaturated S bound.measure bound.tower bound.n bound.z ∧
        record.status = BudgetAuditStatus.meta_audit_capacity_blocked

def MetaAuditMissingCase
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : BudgetAuditClaimRef (AuditRecord := AuditRecord))
    (record :
      BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord)) : Prop :=
  (¬ ∃ higherRecord :
    BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
      CaptureClaimRejectedCase S budgetSettingMovePolicy lineagePolicy
        reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi KLLdagger
        originalOmega xiWitness statusPolicy claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      CaptureDetectedCase S budgetSettingMovePolicy lineagePolicy
        blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
        KLLdagger originalOmega xiWitness statusPolicy claimRef
        higherRecord) ∧
    (¬ ∃ higherRecord :
      BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      ResidualDischargeVerifiedCase S budgetSettingMovePolicy
        lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
        Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
        claimRef higherRecord) ∧
    (¬ ∃ higherRecord :
      BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      MetaAuditCapacityBlockedCase.{uCap, vCap, u, v, w, x, y, y',
        y'', y''', y'''', y'''''} S budgetSettingMovePolicy lineagePolicy
        blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
        KLLdagger originalOmega xiWitness statusPolicy claimRef
        higherRecord) ∧
    BudgetAuditStatusOccurrenceFor S statusPolicy claimRef record ∧
    record.status = BudgetAuditStatus.meta_audit_missing

def CaptureClaimRejectedHolds
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : BudgetAuditClaimRef (AuditRecord := AuditRecord)) : Prop :=
  ∃ record :
    BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
    CaptureClaimRejectedCase S budgetSettingMovePolicy lineagePolicy
      reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi KLLdagger
      originalOmega xiWitness statusPolicy claimRef record

def CaptureDetectedHolds
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : BudgetAuditClaimRef (AuditRecord := AuditRecord)) : Prop :=
  ∃ record :
    BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
    CaptureDetectedCase S budgetSettingMovePolicy lineagePolicy
      blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
      KLLdagger originalOmega xiWitness statusPolicy claimRef record

def ResidualDischargeVerifiedHolds
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : BudgetAuditClaimRef (AuditRecord := AuditRecord)) : Prop :=
  ∃ record :
    BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
    ResidualDischargeVerifiedCase S budgetSettingMovePolicy lineagePolicy
      blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
      KLLdagger originalOmega xiWitness statusPolicy claimRef record

def MetaAuditCapacityBlockedHolds
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : BudgetAuditClaimRef (AuditRecord := AuditRecord)) : Prop :=
  ∃ record :
    BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
    MetaAuditCapacityBlockedCase.{uCap, vCap, u, v, w, x, y, y',
      y'', y''', y'''', y'''''} S budgetSettingMovePolicy lineagePolicy
      blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
      KLLdagger originalOmega xiWitness statusPolicy claimRef record

def MetaAuditMissingHolds
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : BudgetAuditClaimRef (AuditRecord := AuditRecord)) : Prop :=
  ∃ record :
    BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
    MetaAuditMissingCase.{uCap, vCap, u, v, w, x, y, y',
      y'', y''', y'''', y'''''} S budgetSettingMovePolicy lineagePolicy
      blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
      KLLdagger originalOmega xiWitness statusPolicy claimRef record

def CompleteBudgetAuditStatus
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : BudgetAuditClaimRef (AuditRecord := AuditRecord)) : Prop :=
  (∃ record :
    BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
      (AuditRecord := AuditRecord),
    BudgetAuditStatusOccurrenceFor S statusPolicy claimRef record ∧
      (CaptureClaimRejectedCase S budgetSettingMovePolicy lineagePolicy
          reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi KLLdagger
          originalOmega xiWitness statusPolicy claimRef record ∨
        CaptureDetectedCase S budgetSettingMovePolicy lineagePolicy
          blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
          KLLdagger originalOmega xiWitness statusPolicy claimRef record ∨
        ResidualDischargeVerifiedCase S budgetSettingMovePolicy
          lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
          Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
          claimRef record ∨
        MetaAuditCapacityBlockedCase.{uCap, vCap, u, v, w, x, y, y',
          y'', y''', y'''', y'''''} S budgetSettingMovePolicy
          lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
          Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
          claimRef record ∨
        MetaAuditMissingCase.{uCap, vCap, u, v, w, x, y, y',
          y'', y''', y'''', y'''''} S budgetSettingMovePolicy
          lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
          Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
          claimRef record)) ∧
    ∀ record1 record2 :
      BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord),
      BudgetAuditStatusOccurrenceFor S statusPolicy claimRef record1 ->
      BudgetAuditStatusOccurrenceFor S statusPolicy claimRef record2 ->
      record1.status = record2.status

section Theorems

theorem E8_ControlPrice
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : ControlPriceClaimRef)
    (hComplete :
      CompleteControlPriceStatus S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef) :
    (SlackObstructedHolds S economy signalPolicy componentPolicy fieldPolicy
        summaryPolicy slackViolationPolicy slackResidualExplanationPolicy
        quotientPolicy readoutPolicy predictionPolicy stabilityPolicy
        summaryComparators statusPolicy claimRef ∧
        ¬ ProxyObstructedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy
          claimRef ∧
        ¬ SummaryRedescriptionHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ ComponentLawfulHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ FieldLawfulHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ SummaryLawfulHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ IncompleteOrUnpricedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef) ∨
      (ProxyObstructedHolds S economy signalPolicy componentPolicy fieldPolicy
        summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ SlackObstructedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy quotientPolicy readoutPolicy
          predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ SummaryRedescriptionHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ ComponentLawfulHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ FieldLawfulHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ SummaryLawfulHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ IncompleteOrUnpricedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef) ∨
      (SummaryRedescriptionHolds S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ SlackObstructedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy quotientPolicy readoutPolicy
          predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ ProxyObstructedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy
          claimRef ∧
        ¬ ComponentLawfulHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ FieldLawfulHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ SummaryLawfulHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ IncompleteOrUnpricedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef) ∨
      (ComponentLawfulHolds S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ SlackObstructedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy quotientPolicy readoutPolicy
          predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ ProxyObstructedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy
          claimRef ∧
        ¬ SummaryRedescriptionHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ FieldLawfulHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ SummaryLawfulHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ IncompleteOrUnpricedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef) ∨
      (FieldLawfulHolds S economy signalPolicy componentPolicy fieldPolicy
        summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ SlackObstructedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy quotientPolicy readoutPolicy
          predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ ProxyObstructedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy
          claimRef ∧
        ¬ SummaryRedescriptionHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ ComponentLawfulHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ SummaryLawfulHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ IncompleteOrUnpricedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef) ∨
      (SummaryLawfulHolds S economy signalPolicy componentPolicy fieldPolicy
        summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ SlackObstructedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy quotientPolicy readoutPolicy
          predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ ProxyObstructedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy
          claimRef ∧
        ¬ SummaryRedescriptionHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ ComponentLawfulHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ FieldLawfulHolds S economy signalPolicy componentPolicy fieldPolicy
          summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ IncompleteOrUnpricedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef) ∨
      (IncompleteOrUnpricedHolds S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ SlackObstructedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy quotientPolicy readoutPolicy
          predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ ProxyObstructedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy
          claimRef ∧
        ¬ SummaryRedescriptionHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ ComponentLawfulHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ FieldLawfulHolds S economy signalPolicy componentPolicy fieldPolicy
          summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef ∧
        ¬ SummaryLawfulHolds S economy signalPolicy componentPolicy fieldPolicy
          summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef) := by
  rcases hComplete.1 with ⟨record, hOccurrence, hBranch⟩
  have hSlackFacts :
      ∀ {r :
        ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)},
        SlackObstructedCase S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy quotientPolicy readoutPolicy
          predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef r ->
        ControlPriceStatusOccurrenceFor S statusPolicy claimRef r ∧
          r.status = ControlPriceStatus.slack_obstructed := by
    intro r h
    rcases h with ⟨hOcc, _hObstruction, hStatus⟩
    exact ⟨hOcc, hStatus⟩
  have hProxyFacts :
      ∀ {r :
        ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)},
        ProxyObstructedCase S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy
          claimRef r ->
        ControlPriceStatusOccurrenceFor S statusPolicy claimRef r ∧
          r.status = ControlPriceStatus.proxy_obstructed := by
    intro r h
    rcases h with
      ⟨_hNoSlack, hOcc, _component, _failure, _hContains, hStatus⟩
    exact ⟨hOcc, hStatus⟩
  have hRedescriptionFacts :
      ∀ {r :
        ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)},
        SummaryRedescriptionCase S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef r ->
        ControlPriceStatusOccurrenceFor S statusPolicy claimRef r ∧
          r.status = ControlPriceStatus.summary_redescription := by
    intro r h
    rcases h with
      ⟨_hNoSlack, _hNoProxy, hOcc, _summary, _hClaim, _hNoLegit,
        hStatus⟩
    exact ⟨hOcc, hStatus⟩
  have hComponentFacts :
      ∀ {r :
        ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)},
        ComponentLawfulCase S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef r ->
        ControlPriceStatusOccurrenceFor S statusPolicy claimRef r ∧
          r.status = ControlPriceStatus.component_lawful := by
    intro r h
    rcases h with
      ⟨_hNoSlack, _hNoProxy, _hNoRedescription, hOcc, _component,
        _hClaim, _hLawful, hStatus⟩
    exact ⟨hOcc, hStatus⟩
  have hFieldFacts :
      ∀ {r :
        ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)},
        FieldLawfulCase S economy signalPolicy componentPolicy fieldPolicy
          summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef r ->
        ControlPriceStatusOccurrenceFor S statusPolicy claimRef r ∧
          r.status = ControlPriceStatus.field_lawful := by
    intro r h
    rcases h with
      ⟨_hNoSlack, _hNoProxy, _hNoRedescription, _hNoComponent, hOcc,
        _field, _hClaim, _hLawful, hStatus⟩
    exact ⟨hOcc, hStatus⟩
  have hSummaryFacts :
      ∀ {r :
        ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)},
        SummaryLawfulCase S economy signalPolicy componentPolicy fieldPolicy
          summaryPolicy slackViolationPolicy slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef r ->
        ControlPriceStatusOccurrenceFor S statusPolicy claimRef r ∧
          r.status = ControlPriceStatus.summary_lawful := by
    intro r h
    rcases h with
      ⟨_hNoSlack, _hNoProxy, _hNoRedescription, _hNoComponent, _hNoField,
        hOcc, _summary, _hClaim, _hLawful, hStatus⟩
    exact ⟨hOcc, hStatus⟩
  have hIncompleteFacts :
      ∀ {r :
        ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)},
        IncompleteOrUnpricedCase S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef r ->
        ControlPriceStatusOccurrenceFor S statusPolicy claimRef r ∧
          r.status = ControlPriceStatus.incomplete_or_unpriced := by
    intro r h
    rcases h with
      ⟨_hNoSlack, _hNoProxy, _hNoRedescription, _hNoComponent, _hNoField,
        _hNoSummary, hOcc, hStatus⟩
    exact ⟨hOcc, hStatus⟩
  have hNoOther :
      ∀ {current otherStatus : ControlPriceStatus}
        (hStatus : record.status = current)
        {OtherCase :
          ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
            (AuditRecord := AuditRecord) -> Prop}
        (hFacts : ∀ {r}, OtherCase r ->
          ControlPriceStatusOccurrenceFor S statusPolicy claimRef r ∧
            r.status = otherStatus)
        (hNe : current ≠ otherStatus),
        ¬ ∃ other :
          ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
            (AuditRecord := AuditRecord),
          OtherCase other := by
    intro current otherStatus hStatus OtherCase hFacts hNe hOther
    rcases hOther with ⟨other, hOtherCase⟩
    rcases hFacts hOtherCase with ⟨hOtherOccurrence, hOtherStatus⟩
    have hSame := hComplete.2 record other hOccurrence hOtherOccurrence
    rw [hStatus, hOtherStatus] at hSame
    exact hNe hSame
  rcases hBranch with hSlack | hRest
  · have hStatus := (hSlackFacts hSlack).2
    have hHolds :
        SlackObstructedHolds S economy signalPolicy componentPolicy
          fieldPolicy summaryPolicy slackViolationPolicy
          slackResidualExplanationPolicy quotientPolicy readoutPolicy
          predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef :=
      ⟨record, hSlack⟩
    refine Or.inl ?_
    exact
      ⟨hHolds,
        hNoOther hStatus hProxyFacts (by decide),
        hNoOther hStatus hRedescriptionFacts (by decide),
        hNoOther hStatus hComponentFacts (by decide),
        hNoOther hStatus hFieldFacts (by decide),
        hNoOther hStatus hSummaryFacts (by decide),
        hNoOther hStatus hIncompleteFacts (by decide)⟩
  · rcases hRest with hProxy | hRest
    · have hStatus := (hProxyFacts hProxy).2
      have hHolds :
          ProxyObstructedHolds S economy signalPolicy componentPolicy
            fieldPolicy summaryPolicy slackViolationPolicy
            slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy
            claimRef :=
        ⟨record, hProxy⟩
      refine Or.inr (Or.inl ?_)
      exact
        ⟨hHolds,
          hNoOther hStatus hSlackFacts (by decide),
          hNoOther hStatus hRedescriptionFacts (by decide),
          hNoOther hStatus hComponentFacts (by decide),
          hNoOther hStatus hFieldFacts (by decide),
          hNoOther hStatus hSummaryFacts (by decide),
          hNoOther hStatus hIncompleteFacts (by decide)⟩
    · rcases hRest with hRedescription | hRest
      · have hStatus := (hRedescriptionFacts hRedescription).2
        have hHolds :
              SummaryRedescriptionHolds S economy signalPolicy componentPolicy
                fieldPolicy summaryPolicy slackViolationPolicy
                slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef :=
          ⟨record, hRedescription⟩
        refine Or.inr (Or.inr (Or.inl ?_))
        exact
          ⟨hHolds,
            hNoOther hStatus hSlackFacts (by decide),
            hNoOther hStatus hProxyFacts (by decide),
            hNoOther hStatus hComponentFacts (by decide),
            hNoOther hStatus hFieldFacts (by decide),
            hNoOther hStatus hSummaryFacts (by decide),
            hNoOther hStatus hIncompleteFacts (by decide)⟩
      · rcases hRest with hComponent | hRest
        · have hStatus := (hComponentFacts hComponent).2
          have hHolds :
              ComponentLawfulHolds S economy signalPolicy componentPolicy
                fieldPolicy summaryPolicy slackViolationPolicy
                slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef :=
            ⟨record, hComponent⟩
          refine Or.inr (Or.inr (Or.inr (Or.inl ?_)))
          exact
            ⟨hHolds,
              hNoOther hStatus hSlackFacts (by decide),
              hNoOther hStatus hProxyFacts (by decide),
              hNoOther hStatus hRedescriptionFacts (by decide),
              hNoOther hStatus hFieldFacts (by decide),
              hNoOther hStatus hSummaryFacts (by decide),
              hNoOther hStatus hIncompleteFacts (by decide)⟩
        · rcases hRest with hField | hRest
          · have hStatus := (hFieldFacts hField).2
            have hHolds :
                FieldLawfulHolds S economy signalPolicy componentPolicy
                  fieldPolicy summaryPolicy slackViolationPolicy
                  slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef :=
              ⟨record, hField⟩
            refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ?_))))
            exact
              ⟨hHolds,
                hNoOther hStatus hSlackFacts (by decide),
                hNoOther hStatus hProxyFacts (by decide),
                hNoOther hStatus hRedescriptionFacts (by decide),
                hNoOther hStatus hComponentFacts (by decide),
                hNoOther hStatus hSummaryFacts (by decide),
                hNoOther hStatus hIncompleteFacts (by decide)⟩
          · rcases hRest with hSummary | hIncomplete
            · have hStatus := (hSummaryFacts hSummary).2
              have hHolds :
                  SummaryLawfulHolds S economy signalPolicy componentPolicy
                    fieldPolicy summaryPolicy slackViolationPolicy
                    slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy claimRef :=
                ⟨record, hSummary⟩
              refine Or.inr
                (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ?_)))))
              exact
                ⟨hHolds,
                  hNoOther hStatus hSlackFacts (by decide),
                  hNoOther hStatus hProxyFacts (by decide),
                  hNoOther hStatus hRedescriptionFacts (by decide),
                  hNoOther hStatus hComponentFacts (by decide),
                  hNoOther hStatus hFieldFacts (by decide),
                  hNoOther hStatus hIncompleteFacts (by decide)⟩
            · have hStatus := (hIncompleteFacts hIncomplete).2
              have hHolds :
                  IncompleteOrUnpricedHolds S economy signalPolicy
                    componentPolicy fieldPolicy summaryPolicy
                    slackViolationPolicy slackResidualExplanationPolicy
                    proxyFailurePolicy quotientPolicy readoutPolicy
                    predictionPolicy stabilityPolicy summaryComparators
                    statusPolicy claimRef :=
                ⟨record, hIncomplete⟩
              refine Or.inr
                (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr ?_)))))
              exact
                ⟨hHolds,
                  hNoOther hStatus hSlackFacts (by decide),
                  hNoOther hStatus hProxyFacts (by decide),
                  hNoOther hStatus hRedescriptionFacts (by decide),
                  hNoOther hStatus hComponentFacts (by decide),
                  hNoOther hStatus hFieldFacts (by decide),
                  hNoOther hStatus hSummaryFacts (by decide)⟩

theorem E8_ComponentShadowPrice
    (statusPolicy :
      CarriedRecordPolicy S.T
        (ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (component :
      ControlPriceComponent S economy signalPolicy componentPolicy)
    (statusRecord :
      ControlPriceStatusRecord (LedgerEntry := LedgerEntry)
        (AuditRecord := AuditRecord))
    (_hBinding : BindingControlComponent S component)
    (_hNoSlack :
      ¬ ∃ _violation :
        SlackCollapseViolation S component slackViolationPolicy
          slackResidualExplanationPolicy,
        True)
    (_hNoProxy :
      ¬ ∃ _failure : ProxyFailure S component proxyFailurePolicy, True)
    (hCase :
      ComponentLawfulCase S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy slackViolationPolicy
        slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy
        (ControlPriceClaimRef.component component.componentRecord)
        statusRecord) :
    ComponentLawfulHolds S economy signalPolicy componentPolicy
      fieldPolicy summaryPolicy slackViolationPolicy
      slackResidualExplanationPolicy proxyFailurePolicy quotientPolicy readoutPolicy predictionPolicy stabilityPolicy summaryComparators statusPolicy
      (ControlPriceClaimRef.component component.componentRecord) :=
  ⟨statusRecord, hCase⟩

theorem E8_CompressedSummaryLawfulness
    (summary :
      CompressedControlSummary S economy signalPolicy componentPolicy
        fieldPolicy summaryPolicy) :
    SummaryLawful S summary quotientPolicy readoutPolicy predictionPolicy
      stabilityPolicy summaryComparators ↔
      ((∃ _legitimacy :
        SummaryPredictiveLegitimacy S summary quotientPolicy readoutPolicy
          predictionPolicy stabilityPolicy summaryComparators,
        True) ∧
        SummarySlackCollapse S summary) := by
  rfl

theorem E8_1_AuditCapture
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (claimRef : BudgetAuditClaimRef (AuditRecord := AuditRecord))
    (hComplete :
      CompleteBudgetAuditStatus.{_, vCap, u, v, w, x, y, y', y'', y''',
        y'''', y'''''} S budgetSettingMovePolicy lineagePolicy
        blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
        KLLdagger originalOmega xiWitness statusPolicy claimRef) :
    (CaptureClaimRejectedHolds S budgetSettingMovePolicy lineagePolicy
        reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi KLLdagger
        originalOmega xiWitness statusPolicy claimRef ∧
        ¬ CaptureDetectedHolds S budgetSettingMovePolicy lineagePolicy
          blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
          KLLdagger originalOmega xiWitness statusPolicy claimRef ∧
        ¬ ResidualDischargeVerifiedHolds S budgetSettingMovePolicy
          lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
          Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
          claimRef ∧
        ¬ MetaAuditCapacityBlockedHolds.{_, vCap, u, v, w, x, y, y',
          y'', y''', y'''', y'''''} S budgetSettingMovePolicy
          lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
          Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
          claimRef ∧
        ¬ MetaAuditMissingHolds.{_, vCap, u, v, w, x, y, y', y'', y''',
          y'''', y'''''} S budgetSettingMovePolicy lineagePolicy
          blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
          KLLdagger originalOmega xiWitness statusPolicy claimRef) ∨
      (CaptureDetectedHolds S budgetSettingMovePolicy lineagePolicy
        blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
        KLLdagger originalOmega xiWitness statusPolicy claimRef ∧
        ¬ CaptureClaimRejectedHolds S budgetSettingMovePolicy lineagePolicy
          reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi KLLdagger
          originalOmega xiWitness statusPolicy claimRef ∧
        ¬ ResidualDischargeVerifiedHolds S budgetSettingMovePolicy
          lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
          Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
          claimRef ∧
        ¬ MetaAuditCapacityBlockedHolds.{_, vCap, u, v, w, x, y, y',
          y'', y''', y'''', y'''''} S budgetSettingMovePolicy
          lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
          Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
          claimRef ∧
        ¬ MetaAuditMissingHolds.{_, vCap, u, v, w, x, y, y', y'', y''',
          y'''', y'''''} S budgetSettingMovePolicy lineagePolicy
          blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
          KLLdagger originalOmega xiWitness statusPolicy claimRef) ∨
      (ResidualDischargeVerifiedHolds S budgetSettingMovePolicy
        lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
        Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
        claimRef ∧
        ¬ CaptureClaimRejectedHolds S budgetSettingMovePolicy lineagePolicy
          reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi KLLdagger
          originalOmega xiWitness statusPolicy claimRef ∧
        ¬ CaptureDetectedHolds S budgetSettingMovePolicy lineagePolicy
          blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
          KLLdagger originalOmega xiWitness statusPolicy claimRef ∧
        ¬ MetaAuditCapacityBlockedHolds.{_, vCap, u, v, w, x, y, y',
          y'', y''', y'''', y'''''} S budgetSettingMovePolicy
          lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
          Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
          claimRef ∧
        ¬ MetaAuditMissingHolds.{_, vCap, u, v, w, x, y, y', y'', y''',
          y'''', y'''''} S budgetSettingMovePolicy lineagePolicy
          blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
          KLLdagger originalOmega xiWitness statusPolicy claimRef) ∨
      (MetaAuditCapacityBlockedHolds.{_, vCap, u, v, w, x, y, y', y'',
        y''', y'''', y'''''} S budgetSettingMovePolicy
        lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
        Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
        claimRef ∧
        ¬ CaptureClaimRejectedHolds S budgetSettingMovePolicy lineagePolicy
          reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi KLLdagger
          originalOmega xiWitness statusPolicy claimRef ∧
        ¬ CaptureDetectedHolds S budgetSettingMovePolicy lineagePolicy
          blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
          KLLdagger originalOmega xiWitness statusPolicy claimRef ∧
        ¬ ResidualDischargeVerifiedHolds S budgetSettingMovePolicy
          lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
          Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
          claimRef ∧
        ¬ MetaAuditMissingHolds.{_, vCap, u, v, w, x, y, y', y'', y''',
          y'''', y'''''} S budgetSettingMovePolicy lineagePolicy
          blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
          KLLdagger originalOmega xiWitness statusPolicy claimRef) ∨
      (MetaAuditMissingHolds.{_, vCap, u, v, w, x, y, y', y'', y''',
        y'''', y'''''} S budgetSettingMovePolicy lineagePolicy
        blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
        KLLdagger originalOmega xiWitness statusPolicy claimRef ∧
        ¬ CaptureClaimRejectedHolds S budgetSettingMovePolicy lineagePolicy
          reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi KLLdagger
          originalOmega xiWitness statusPolicy claimRef ∧
        ¬ CaptureDetectedHolds S budgetSettingMovePolicy lineagePolicy
          blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
          KLLdagger originalOmega xiWitness statusPolicy claimRef ∧
        ¬ ResidualDischargeVerifiedHolds S budgetSettingMovePolicy
          lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
          Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
          claimRef ∧
        ¬ MetaAuditCapacityBlockedHolds.{_, vCap, u, v, w, x, y, y',
          y'', y''', y'''', y'''''} S budgetSettingMovePolicy
          lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
          Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
          claimRef) := by
  rcases hComplete.1 with ⟨record, hOccurrence, hBranch⟩
  have hRejectedFacts :
      ∀ {r :
        BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)},
        CaptureClaimRejectedCase S budgetSettingMovePolicy lineagePolicy
          reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi KLLdagger
          originalOmega xiWitness statusPolicy claimRef r ->
        BudgetAuditStatusOccurrenceFor S statusPolicy claimRef r ∧
          r.status = BudgetAuditStatus.capture_claim_rejected := by
    intro r h
    rcases h with
      ⟨hOcc, _falsifier, _hRejected, _hClaimBudget, _hClaimLineage,
        _hClaimHealth, hStatus, _hRecordBudget, _hRecordLineage,
        _hRecordHealth, _hMeta⟩
    exact ⟨hOcc, hStatus⟩
  have hDetectedFacts :
      ∀ {r :
        BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)},
        CaptureDetectedCase S budgetSettingMovePolicy lineagePolicy
          blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
          KLLdagger originalOmega xiWitness statusPolicy claimRef r ->
        BudgetAuditStatusOccurrenceFor S statusPolicy claimRef r ∧
          r.status = BudgetAuditStatus.capture_detected := by
    intro r h
    rcases h with
      ⟨_hNoRejected, hOcc, _audit, _hHealth, _hInflates, _hBlind,
        _hClaimBudget, _hClaimLineage, _hClaimHealth, hStatus,
        _hRecordBudget, _hRecordLineage, _hRecordHealth, _hMeta⟩
    exact ⟨hOcc, hStatus⟩
  have hDischargeFacts :
      ∀ {r :
        BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)},
        ResidualDischargeVerifiedCase S budgetSettingMovePolicy
          lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
          Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
          claimRef r ->
        BudgetAuditStatusOccurrenceFor S statusPolicy claimRef r ∧
          r.status = BudgetAuditStatus.residual_discharge_verified := by
    intro r h
    rcases h with
      ⟨_hNoRejected, _hNoDetected, hOcc, _audit, _hDischarge,
        _hClaimBudget, _hClaimLineage, _hClaimHealth, hStatus,
        _hRecordBudget, _hRecordLineage, _hRecordHealth, _hMeta⟩
    exact ⟨hOcc, hStatus⟩
  have hNoBudgetOther :
      ∀ {current otherStatus : BudgetAuditStatus}
        (hStatus : record.status = current)
        {OtherCase :
          BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
            (AuditRecord := AuditRecord) -> Prop}
        (hFacts : ∀ {r}, OtherCase r ->
          BudgetAuditStatusOccurrenceFor S statusPolicy claimRef r ∧
            r.status = otherStatus)
        (hNe : current ≠ otherStatus),
        ¬ ∃ other :
          BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
            (AuditRecord := AuditRecord),
          OtherCase other := by
    intro current otherStatus hStatus OtherCase hFacts hNe hOther
    rcases hOther with ⟨other, hOtherCase⟩
    rcases hFacts hOtherCase with ⟨hOtherOccurrence, hOtherStatus⟩
    have hSame := hComplete.2 record other hOccurrence hOtherOccurrence
    rw [hStatus, hOtherStatus] at hSame
    exact hNe hSame
  have hNoCapacity :
      ∀ {current : BudgetAuditStatus}
        (hStatus : record.status = current)
        (hNe :
          current ≠ BudgetAuditStatus.meta_audit_capacity_blocked),
        ¬ MetaAuditCapacityBlockedHolds.{_, vCap, u, v, w, x, y, y',
          y'', y''', y'''', y'''''} S budgetSettingMovePolicy
          lineagePolicy blindSpotPolicy reportedHealthPolicy metaAuditPolicy
          Cxi Lxi Dxi KLLdagger originalOmega xiWitness statusPolicy
          claimRef := by
    intro current hStatus hNe hOther
    rcases hOther with ⟨other, hOtherCase⟩
    rcases hOtherCase with
      ⟨_hNoRejected, _hNoDetected, _hNoDischarge, hOtherOccurrence,
        _bound, _hClaimBudget, _hClaimLineage, _hClaimHealth,
        _hSaturated, hOtherStatus⟩
    have hSame := hComplete.2 record other hOccurrence hOtherOccurrence
    rw [hStatus, hOtherStatus] at hSame
    exact hNe hSame
  have hNoMissing :
      ∀ {current : BudgetAuditStatus}
        (hStatus : record.status = current)
        (hNe : current ≠ BudgetAuditStatus.meta_audit_missing),
        ¬ MetaAuditMissingHolds.{_, vCap, u, v, w, x, y, y', y'', y''',
          y'''', y'''''} S budgetSettingMovePolicy lineagePolicy
          blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
          KLLdagger originalOmega xiWitness statusPolicy claimRef := by
    intro current hStatus hNe hOther
    rcases hOther with ⟨other, hOtherCase⟩
    rcases hOtherCase with
      ⟨_hNoRejected, _hNoDetected, _hNoDischarge, _hNoCapacity,
        hOtherOccurrence, hOtherStatus⟩
    have hSame := hComplete.2 record other hOccurrence hOtherOccurrence
    rw [hStatus, hOtherStatus] at hSame
    exact hNe hSame
  rcases hBranch with hRejected | hRest
  · have hStatus := (hRejectedFacts hRejected).2
    have hHolds :
        CaptureClaimRejectedHolds S budgetSettingMovePolicy lineagePolicy
          reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi KLLdagger
          originalOmega xiWitness statusPolicy claimRef :=
      ⟨record, hRejected⟩
    exact Or.inl
      ⟨hHolds,
        hNoBudgetOther hStatus hDetectedFacts (by decide),
        hNoBudgetOther hStatus hDischargeFacts (by decide),
        hNoCapacity hStatus (by decide),
        hNoMissing hStatus (by decide)⟩
  · rcases hRest with hDetected | hRest
    · have hStatus := (hDetectedFacts hDetected).2
      have hHolds :
          CaptureDetectedHolds S budgetSettingMovePolicy lineagePolicy
            blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
            KLLdagger originalOmega xiWitness statusPolicy claimRef :=
        ⟨record, hDetected⟩
      exact Or.inr (Or.inl
        ⟨hHolds,
          hNoBudgetOther hStatus hRejectedFacts (by decide),
          hNoBudgetOther hStatus hDischargeFacts (by decide),
          hNoCapacity hStatus (by decide),
          hNoMissing hStatus (by decide)⟩)
    · rcases hRest with hDischarge | hRest
      · have hStatus := (hDischargeFacts hDischarge).2
        have hHolds :
            ResidualDischargeVerifiedHolds S budgetSettingMovePolicy
              lineagePolicy blindSpotPolicy reportedHealthPolicy
              metaAuditPolicy Cxi Lxi Dxi KLLdagger originalOmega
              xiWitness statusPolicy claimRef :=
          ⟨record, hDischarge⟩
        exact Or.inr (Or.inr (Or.inl
          ⟨hHolds,
            hNoBudgetOther hStatus hRejectedFacts (by decide),
            hNoBudgetOther hStatus hDetectedFacts (by decide),
            hNoCapacity hStatus (by decide),
            hNoMissing hStatus (by decide)⟩))
      · rcases hRest with hCapacity | hMissing
        · have hStatus :
              record.status =
                BudgetAuditStatus.meta_audit_capacity_blocked := by
            rcases hCapacity with
              ⟨_hNoRejected, _hNoDetected, _hNoDischarge, _hOccurrence,
                _bound, _hClaimBudget, _hClaimLineage, _hClaimHealth,
                _hSaturated, hStatus⟩
            exact hStatus
          have hHolds :
              MetaAuditCapacityBlockedHolds.{_, vCap, u, v, w, x, y, y',
                y'', y''', y'''', y'''''} S budgetSettingMovePolicy
                lineagePolicy blindSpotPolicy reportedHealthPolicy
                metaAuditPolicy Cxi Lxi Dxi KLLdagger originalOmega
                xiWitness statusPolicy claimRef :=
            ⟨record, hCapacity⟩
          refine Or.inr (Or.inr (Or.inr (Or.inl ?_)))
          exact
            ⟨hHolds,
              hNoBudgetOther hStatus hRejectedFacts (by decide),
              hNoBudgetOther hStatus hDetectedFacts (by decide),
              hNoBudgetOther hStatus hDischargeFacts (by decide),
              hNoMissing hStatus (by decide)⟩
        · have hStatus :
              record.status = BudgetAuditStatus.meta_audit_missing := by
            rcases hMissing with
              ⟨_hNoRejected, _hNoDetected, _hNoDischarge, _hNoCapacity,
                _hOccurrence, hStatus⟩
            exact hStatus
          have hHolds :
              MetaAuditMissingHolds.{_, vCap, u, v, w, x, y, y', y'',
                y''', y'''', y'''''} S budgetSettingMovePolicy lineagePolicy
                blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi
                Dxi KLLdagger originalOmega xiWitness statusPolicy claimRef :=
            ⟨record, hMissing⟩
          refine Or.inr (Or.inr (Or.inr (Or.inr ?_)))
          exact
            ⟨hHolds,
              hNoBudgetOther hStatus hRejectedFacts (by decide),
              hNoBudgetOther hStatus hDetectedFacts (by decide),
              hNoBudgetOther hStatus hDischargeFacts (by decide),
              hNoCapacity hStatus (by decide)⟩

theorem E8_1_CaptureFalsifier
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BudgetAuditStatusRecord (LedgerEntry := LedgerEntry)
          (AuditRecord := AuditRecord)))
    (falsifier :
      CaptureClaimFalsifier S budgetSettingMovePolicy lineagePolicy
        reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi KLLdagger
        originalOmega xiWitness)
    (_hRejected : CaptureClaimRejected S falsifier) :
    ¬ CaptureDetectedHolds S budgetSettingMovePolicy lineagePolicy
      blindSpotPolicy reportedHealthPolicy metaAuditPolicy Cxi Lxi Dxi
      KLLdagger originalOmega xiWitness statusPolicy
      { budgetMoveRecord := falsifier.noCaptureAudit.budgetMove.moveRecord
        lineageRecord := some falsifier.noCaptureAudit.lineageRecord
        healthRecord := some falsifier.noCaptureAudit.reportedHealth } := by
  intro hDetected
  rcases hDetected with ⟨_record, hCase⟩
  rcases hCase with
    ⟨_hNoRejected, _hOccurrence, _audit, _hHealth, _hInflates, hBlind,
      _hClaimBudget, _hClaimLineage, _hClaimHealth, _hStatus,
      _hRecordBudget, _hRecordLineage, _hRecordHealth, _hMeta⟩
  exact falsifier.noCaptureAudit.noOriginalBlindSpotPersists hBlind

theorem E8_1_MetaAuditBoundedByE2
    {ChallengeClass : Type u1} {SourceQuotient : Type v1}
    {DeclaredFamily : Type w1} {TargetReadout : Type x1}
    {ObstructionWitness : Type y1} {RepairRefinement : Type z1}
    {Horizon : Type u2}
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (C : ChallengeClass) (horizon : Horizon) (targetLevel : Nat)
    (bound :
      MetaAuditBoundedByE2.{u, v, w, x, y, y', y'', y''', y'''',
        y''''', uCap, vCap} S budgetSettingMovePolicy)
    (hComplete :
      CompleteBoundedReflexivityStatus S H installs postState statusPolicy
        claimTarget bound.measure C bound.tower bound.n bound.z horizon
        targetLevel) :
    TowerFootprint S bound.measure bound.tower bound.n <=
        bound.measure.cap bound.z ∧
      ((ActiveScopedHolds S H installs postState statusPolicy claimTarget
          bound.measure C bound.tower bound.n bound.z horizon targetLevel ∧
          ¬ RotatingHolds S H installs postState statusPolicy claimTarget
            bound.measure C bound.tower bound.n bound.z horizon targetLevel ∧
          ¬ SaturatedHolds S statusPolicy claimTarget bound.measure
            bound.tower bound.n bound.z targetLevel ∧
          ¬ CircularBlockedHolds S statusPolicy claimTarget bound.tower
            bound.n bound.z targetLevel) ∨
        (RotatingHolds S H installs postState statusPolicy claimTarget
          bound.measure C bound.tower bound.n bound.z horizon targetLevel ∧
          ¬ ActiveScopedHolds S H installs postState statusPolicy claimTarget
            bound.measure C bound.tower bound.n bound.z horizon targetLevel ∧
          ¬ SaturatedHolds S statusPolicy claimTarget bound.measure
            bound.tower bound.n bound.z targetLevel ∧
          ¬ CircularBlockedHolds S statusPolicy claimTarget bound.tower
            bound.n bound.z targetLevel) ∨
        (SaturatedHolds S statusPolicy claimTarget bound.measure bound.tower
          bound.n bound.z targetLevel ∧
          ¬ ActiveScopedHolds S H installs postState statusPolicy claimTarget
            bound.measure C bound.tower bound.n bound.z horizon targetLevel ∧
          ¬ RotatingHolds S H installs postState statusPolicy claimTarget
            bound.measure C bound.tower bound.n bound.z horizon targetLevel ∧
          ¬ CircularBlockedHolds S statusPolicy claimTarget bound.tower
            bound.n bound.z targetLevel) ∨
        (CircularBlockedHolds S statusPolicy claimTarget bound.tower bound.n
          bound.z targetLevel ∧
          ¬ ActiveScopedHolds S H installs postState statusPolicy claimTarget
            bound.measure C bound.tower bound.n bound.z horizon targetLevel ∧
          ¬ RotatingHolds S H installs postState statusPolicy claimTarget
            bound.measure C bound.tower bound.n bound.z horizon targetLevel ∧
          ¬ SaturatedHolds S statusPolicy claimTarget bound.measure
            bound.tower bound.n bound.z targetLevel)) := by
  exact
    ⟨E2_CapacityBound S bound.measure bound.tower bound.n bound.z
        bound.realizable,
      E2_StatusPartition S H installs postState statusPolicy claimTarget
        bound.measure C bound.tower bound.n bound.z horizon targetLevel
        hComplete⟩

end Theorems

end StatusApparatus

end SixBirdsFoundationsV
