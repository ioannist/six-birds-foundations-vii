import SixBirdsFoundationsV.Definitional.ESystem
import SixBirdsFoundationsV.Definitional.ProbeEconomy
import SixBirdsFoundationsV.Laws.E1Internalization
import SixBirdsFoundationsV.Laws.E3SelfMaintainingReclosure
import SixBirdsFoundationsV.Laws.E6E9PricedAccess

namespace SixBirdsFoundationsV

/-!
E5 reclosure collapse setup.

This setup layer mechanizes the repair-economy rescue candidates, collapse
falsifier, certified reachability/kernel inputs, subsidy/suspension/revival
vocabulary, and exact-rational budget/residual surfaces from the accepted E5
six-field normal form (`formalization/notes/examples/E5.md`).  The seven-way
status apparatus and E5 theorems are intentionally left to later
mechanization subsections.
-/

section Setup

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
variable {ChallengeClass : Type z} {SourceQuotient : Type z'}
variable {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
variable {ObstructionWitness : Type z''''}
variable {Horizon : Type z'''''}
variable {RepairRefinement : Type u'} {Probe : Type v'}
variable {XiFamily : Type w'} {ExternalCarrier : Type x'}
variable {ViabilityProbeFamilyRecord : Type y''''''}
variable {ViabilityDescentReadoutRecord : Type y'''''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
  AuditRecord)
variable (H :
  ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
    TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)

inductive CollapseMoveKind where
  | repair
  | boundary_update
  | apparatus_reclosure
  | acquisition
  deriving DecidableEq, Repr

structure CollapseMoveRecord where
  moveId : Nat
  kind : CollapseMoveKind
  deriving DecidableEq, Repr

structure CollapseScopeRecord where
  challengeClass : ChallengeClass
  horizon : Horizon

structure CollapseBoundaryRecord
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  boundaryId : Nat
  sourceState : S.T.Z
  targetState : S.T.Z

structure BoundaryUpdateRecord
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  updateId : Nat
  preBoundary : CollapseBoundaryRecord S
  postBoundary : CollapseBoundaryRecord S
  moveRecord : CollapseMoveRecord

structure ReclosureCollapseStatusRecordRef where
  statusRecordId : Nat
  deriving DecidableEq, Repr

/-- Certified carried-status lookup used by revival witnesses. -/
structure PriorStatusIsSubsidizedOrCollapsed where
  holds : ReclosureCollapseStatusRecordRef -> Prop

structure ResidualStatusRecord where
  residualId : Nat
  deriving DecidableEq, Repr

structure SubsidyRecord where
  subsidyId : Nat
  deriving DecidableEq, Repr

structure SubsidyWithdrawalRecord where
  withdrawalId : Nat
  priorSubsidyRecord : SubsidyRecord

structure SuspensionRecord where
  suspensionId : Nat
  deriving DecidableEq, Repr

structure RepairGeneratorReachabilityRecord where
  reachabilityId : Nat
  scope : CollapseScopeRecord (ChallengeClass := ChallengeClass) (Horizon := Horizon)

structure ApparatusViabilityKernelRecord where
  kernelId : Nat
  scope : CollapseScopeRecord (ChallengeClass := ChallengeClass) (Horizon := Horizon)

/-- Certified operational-state input: the apparatus remains intact. -/
structure ApparatusIntactCertified (System : Type u) (History : Type v)
    (ChallengeClass : Type w) (Horizon : Type x) where
  holds : System -> History -> ChallengeClass -> Horizon -> Prop

/-- Certified operational-state input: operations are gated off. -/
structure OperationsGatedOffCertified (System : Type u) (History : Type v)
    (ChallengeClass : Type w) (Horizon : Type x) where
  holds : System -> History -> ChallengeClass -> Horizon -> Prop

/-- Certified operational-state input: a binding operational challenge is active. -/
structure BindingOperationalChallengeActive (System : Type u) (History : Type v)
    (ChallengeClass : Type w) (Horizon : Type x) where
  holds : System -> History -> ChallengeClass -> Horizon -> Prop

structure DeclaredViabilityProbeFamily
    (probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord) where
  probeFamilyRecord : ViabilityProbeFamilyRecord
  carried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt probeFamilyPolicy probeFamilyRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

/-- Certified bridge tying a descent readout to the declared probe family. -/
structure DescentReadoutForProbeFamily
    (ViabilityDescentReadoutRecord : Type u)
    (ViabilityProbeFamilyRecord : Type v) where
  holds : ViabilityDescentReadoutRecord -> ViabilityProbeFamilyRecord -> Prop

/--
Certified attribution that credits a concrete rescue move record for the
descent readout, closing the proof-irrelevance gap for scope-level descent.
-/
structure RescueMoveCreditedForDescent
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
    (C : ChallengeClass) (horizon : Horizon)
    (ViabilityDescentReadoutRecord : Type y''''''') where
  holds : CollapseMoveRecord -> ViabilityDescentReadoutRecord -> Prop

structure RescueDescentCertificate
    (descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon)
    (probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord)
    (descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord)
    (readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord)
    (C : ChallengeClass) (horizon : Horizon)
    (descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord)
    (moveRecord : CollapseMoveRecord) where
  probeFamily : DeclaredViabilityProbeFamily S probeFamilyPolicy
  descentForMove : CollapseMoveRecord
  moveRecordLinked : descentForMove = moveRecord
  descendsForScope : descends.holds S H C horizon
  descentReadoutRecord : ViabilityDescentReadoutRecord
  readoutForDeclaredFamily :
    readoutForProbeFamily.holds descentReadoutRecord
      probeFamily.probeFamilyRecord
  moveCreditedForDescent :
    descentAttribution.holds moveRecord descentReadoutRecord
  readoutCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt descentReadoutPolicy descentReadoutRecord n0
          sourceTag generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope

structure CollapseBudgetWitness (moveRecord : CollapseMoveRecord) where
  spend : Rat
  budget : Rat
  budgetEntry : LedgerEntry
  spendEntry : LedgerEntry
  budgetEntryInLedger : budgetEntry ∈ S.Lambda_S.ledgerEntries
  spendEntryInLedger : spendEntry ∈ S.Lambda_S.ledgerEntries
  budgetedMoveRecord : CollapseMoveRecord
  moveRecordLinked : budgetedMoveRecord = moveRecord

def CollapseBudgetFeasible
    {moveRecord : CollapseMoveRecord}
    (w : CollapseBudgetWitness S moveRecord) : Prop :=
  w.spend <= w.budget

structure RepairRescueCandidate
    (descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon)
    (probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord)
    (descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord)
    (readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord)
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (repairMoveRef :
      RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
        CollapseMoveRecord)
    (C : ChallengeClass) (horizon : Horizon)
    (descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord) where
  moveRecord : CollapseMoveRecord
  kindOk : moveRecord.kind = CollapseMoveKind.repair
  t : Nat
  rho_t : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord
  R_t : RepairRefinement
  occurrence :
    EndogenousRepairOccurrence S H installs postState C t rho_t R_t
  moveRecordLinked : repairMoveRef rho_t = moveRecord
  budget : CollapseBudgetWitness S moveRecord
  descent :
    RescueDescentCertificate S H descends probeFamilyPolicy
      descentReadoutPolicy readoutForProbeFamily C horizon
      descentAttribution moveRecord

def RepairRescueAdmissibleInBudget
    {descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon}
    {probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord}
    {descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord}
    {readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {repairMoveRef :
      RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
        CollapseMoveRecord}
    {C : ChallengeClass} {horizon : Horizon}
    {descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord}
    (r :
      RepairRescueCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef C horizon descentAttribution) : Prop :=
  CollapseBudgetFeasible (S := S) r.budget

structure BoundaryUpdateCandidate
    (descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon)
    (probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord)
    (descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord)
    (readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord)
    (boundaryUpdatePolicy :
      CarriedRecordPolicy S.T (BoundaryUpdateRecord S))
    (C : ChallengeClass) (horizon : Horizon)
    (descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord) where
  moveRecord : CollapseMoveRecord
  kindOk : moveRecord.kind = CollapseMoveKind.boundary_update
  preBoundary : CollapseBoundaryRecord S
  postBoundary : CollapseBoundaryRecord S
  updateRecord : BoundaryUpdateRecord S
  carried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt boundaryUpdatePolicy updateRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  linksPrePost :
    updateRecord.preBoundary = preBoundary ∧
      updateRecord.postBoundary = postBoundary ∧
      updateRecord.moveRecord = moveRecord
  kernelRealized :
    S.T.suppK preBoundary.sourceState postBoundary.targetState
  budget : CollapseBudgetWitness S moveRecord
  descent :
    RescueDescentCertificate S H descends probeFamilyPolicy
      descentReadoutPolicy readoutForProbeFamily C horizon
      descentAttribution moveRecord

def BoundaryUpdateAdmissibleInBudget
    {descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon}
    {probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord}
    {descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord}
    {readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord}
    {boundaryUpdatePolicy :
      CarriedRecordPolicy S.T (BoundaryUpdateRecord S)}
    {C : ChallengeClass} {horizon : Horizon}
    {descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord}
    (b :
      BoundaryUpdateCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily boundaryUpdatePolicy C
        horizon descentAttribution) : Prop :=
  CollapseBudgetFeasible (S := S) b.budget

structure ApparatusReclosureCandidate
    (descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon)
    (probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord)
    (descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord)
    (readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (reclosureMoveRef :
      MaintenanceReinstatementRecord S -> CollapseMoveRecord)
    (C : ChallengeClass) (horizon : Horizon)
    (descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord) where
  moveRecord : CollapseMoveRecord
  kindOk : moveRecord.kind = CollapseMoveKind.apparatus_reclosure
  t : Nat
  app_t : ClosureApparatus S
  app_tplus1 : ClosureApparatus S
  m : ClosureMaintenanceOperator S
  record : MaintenanceReinstatementRecord S
  reinstatement :
    MaintenanceReinstatementFor S H appPolicy maintenancePolicy
      reinstatementPolicy t app_t app_tplus1 m record
  moveRecordLinked : reclosureMoveRef record = moveRecord
  budget : CollapseBudgetWitness S moveRecord
  descent :
    RescueDescentCertificate S H descends probeFamilyPolicy
      descentReadoutPolicy readoutForProbeFamily C horizon
      descentAttribution moveRecord

def ApparatusReclosureAdmissibleInBudget
    {descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon}
    {probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord}
    {descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord}
    {readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord}
    {appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord}
    {maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord}
    {reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S)}
    {reclosureMoveRef :
      MaintenanceReinstatementRecord S -> CollapseMoveRecord}
    {C : ChallengeClass} {horizon : Horizon}
    {descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord}
    (e :
      ApparatusReclosureCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily appPolicy
        maintenancePolicy reinstatementPolicy reclosureMoveRef C horizon
        descentAttribution) : Prop :=
  CollapseBudgetFeasible (S := S) e.budget

structure AcquisitionRescueCandidate
    (descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon)
    (probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord)
    (descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord)
    (readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord)
    (economy : ProbeEconomy S Probe XiFamily)
    (riskAdmissible : ViabilityRiskAdmissible Probe XiFamily)
    (acquisitionMoveRef :
      ProbeMove Probe XiFamily -> CollapseMoveRecord)
    (C : ChallengeClass) (horizon : Horizon)
    (descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord) where
  moveRecord : CollapseMoveRecord
  kindOk : moveRecord.kind = CollapseMoveKind.acquisition
  L_t : ActiveFamily Probe XiFamily
  L_tplus1 : ActiveFamily Probe XiFamily
  M : Probe
  budgetData :
    ExposureBudgetWitness economy (ProbeMove.acquisition L_t M L_tplus1)
  preN0 : Nat
  preSourceTag : FineSourceTag
  preGeneratedByS : Bool
  preInScope : Bool
  postN0 : Nat
  postSourceTag : FineSourceTag
  postGeneratedByS : Bool
  postInScope : Bool
  lawful :
    LawfulAcquisition economy L_t M L_tplus1 preN0 preSourceTag
      preGeneratedByS preInScope postN0 postSourceTag postGeneratedByS
      postInScope
  candidate :
    CandidateAcquisition economy L_t M L_tplus1 budgetData riskAdmissible
  moveRecordLinked :
    acquisitionMoveRef (ProbeMove.acquisition L_t M L_tplus1) =
      moveRecord
  descent :
    RescueDescentCertificate S H descends probeFamilyPolicy
      descentReadoutPolicy readoutForProbeFamily C horizon
      descentAttribution moveRecord

def AcquisitionRescueAdmissibleInBudget
    {descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon}
    {probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord}
    {descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord}
    {readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord}
    {economy : ProbeEconomy S Probe XiFamily}
    {riskAdmissible : ViabilityRiskAdmissible Probe XiFamily}
    {acquisitionMoveRef : ProbeMove Probe XiFamily -> CollapseMoveRecord}
    {C : ChallengeClass} {horizon : Horizon}
    {descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord}
    (a :
      AcquisitionRescueCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution) : Prop :=
  BudgetFeasible a.budgetData

inductive CollapseRescueCandidate
    (descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon)
    (probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord)
    (descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord)
    (readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord)
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (repairMoveRef :
      RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
        CollapseMoveRecord)
    (boundaryUpdatePolicy :
      CarriedRecordPolicy S.T (BoundaryUpdateRecord S))
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (reclosureMoveRef :
      MaintenanceReinstatementRecord S -> CollapseMoveRecord)
    (economy : ProbeEconomy S Probe XiFamily)
    (riskAdmissible : ViabilityRiskAdmissible Probe XiFamily)
    (acquisitionMoveRef : ProbeMove Probe XiFamily -> CollapseMoveRecord)
    (C : ChallengeClass) (horizon : Horizon)
    (descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord) where
  | repair :
      RepairRescueCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef C horizon descentAttribution ->
        CollapseRescueCandidate descends
          probeFamilyPolicy descentReadoutPolicy readoutForProbeFamily
          installs postState repairMoveRef boundaryUpdatePolicy appPolicy
          maintenancePolicy reinstatementPolicy reclosureMoveRef economy
          riskAdmissible acquisitionMoveRef C horizon descentAttribution
  | boundary :
      BoundaryUpdateCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily boundaryUpdatePolicy C
        horizon descentAttribution ->
        CollapseRescueCandidate descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution
  | reclosure :
      ApparatusReclosureCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily appPolicy
        maintenancePolicy reinstatementPolicy reclosureMoveRef C horizon
        descentAttribution ->
        CollapseRescueCandidate descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution
  | acquisition :
      AcquisitionRescueCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution ->
        CollapseRescueCandidate descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution

def CollapseRescueAdmissibleInBudget
    {descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon}
    {probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord}
    {descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord}
    {readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {repairMoveRef :
      RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
        CollapseMoveRecord}
    {boundaryUpdatePolicy :
      CarriedRecordPolicy S.T (BoundaryUpdateRecord S)}
    {appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord}
    {maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord}
    {reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S)}
    {reclosureMoveRef :
      MaintenanceReinstatementRecord S -> CollapseMoveRecord}
    {economy : ProbeEconomy S Probe XiFamily}
    {riskAdmissible : ViabilityRiskAdmissible Probe XiFamily}
    {acquisitionMoveRef : ProbeMove Probe XiFamily -> CollapseMoveRecord}
    {C : ChallengeClass} {horizon : Horizon}
    {descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord}
    (move :
      CollapseRescueCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution) : Prop :=
  match move with
  | CollapseRescueCandidate.repair r =>
      RepairRescueAdmissibleInBudget (S := S) (H := H)
        (C := C) (horizon := horizon)
        (descentAttribution := descentAttribution) r
  | CollapseRescueCandidate.boundary b =>
      BoundaryUpdateAdmissibleInBudget (S := S) (H := H)
        (C := C) (horizon := horizon)
        (descentAttribution := descentAttribution) b
  | CollapseRescueCandidate.reclosure e =>
      ApparatusReclosureAdmissibleInBudget (S := S) (H := H)
        (C := C) (horizon := horizon)
        (descentAttribution := descentAttribution) e
  | CollapseRescueCandidate.acquisition a =>
      AcquisitionRescueAdmissibleInBudget (S := S) (H := H)
        (C := C) (horizon := horizon)
        (descentAttribution := descentAttribution) a

def CollapseRescueDescends
    {descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon}
    {probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord}
    {descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord}
    {readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {repairMoveRef :
      RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
        CollapseMoveRecord}
    {boundaryUpdatePolicy :
      CarriedRecordPolicy S.T (BoundaryUpdateRecord S)}
    {appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord}
    {maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord}
    {reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S)}
    {reclosureMoveRef :
      MaintenanceReinstatementRecord S -> CollapseMoveRecord}
    {economy : ProbeEconomy S Probe XiFamily}
    {riskAdmissible : ViabilityRiskAdmissible Probe XiFamily}
    {acquisitionMoveRef : ProbeMove Probe XiFamily -> CollapseMoveRecord}
    {C : ChallengeClass} {horizon : Horizon}
    {descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord}
    (move :
      CollapseRescueCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution) : Prop :=
  match move with
  | CollapseRescueCandidate.repair r =>
      descentAttribution.holds r.moveRecord r.descent.descentReadoutRecord
  | CollapseRescueCandidate.boundary b =>
      descentAttribution.holds b.moveRecord b.descent.descentReadoutRecord
  | CollapseRescueCandidate.reclosure e =>
      descentAttribution.holds e.moveRecord e.descent.descentReadoutRecord
  | CollapseRescueCandidate.acquisition a =>
      descentAttribution.holds a.moveRecord a.descent.descentReadoutRecord

def CollapseRescueMoveRecord
    {descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon}
    {probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord}
    {descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord}
    {readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {repairMoveRef :
      RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
        CollapseMoveRecord}
    {boundaryUpdatePolicy :
      CarriedRecordPolicy S.T (BoundaryUpdateRecord S)}
    {appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord}
    {maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord}
    {reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S)}
    {reclosureMoveRef :
      MaintenanceReinstatementRecord S -> CollapseMoveRecord}
    {economy : ProbeEconomy S Probe XiFamily}
    {riskAdmissible : ViabilityRiskAdmissible Probe XiFamily}
    {acquisitionMoveRef : ProbeMove Probe XiFamily -> CollapseMoveRecord}
    {C : ChallengeClass} {horizon : Horizon}
    {descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord}
    (move :
      CollapseRescueCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution) :
    CollapseMoveRecord :=
  match move with
  | CollapseRescueCandidate.repair r => r.moveRecord
  | CollapseRescueCandidate.boundary b => b.moveRecord
  | CollapseRescueCandidate.reclosure e => e.moveRecord
  | CollapseRescueCandidate.acquisition a => a.moveRecord

structure CompleteCollapseRescueInventory
    (descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon)
    (probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord)
    (descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord)
    (readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord)
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (repairMoveRef :
      RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
        CollapseMoveRecord)
    (boundaryUpdatePolicy :
      CarriedRecordPolicy S.T (BoundaryUpdateRecord S))
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (reclosureMoveRef :
      MaintenanceReinstatementRecord S -> CollapseMoveRecord)
    (economy : ProbeEconomy S Probe XiFamily)
    (riskAdmissible : ViabilityRiskAdmissible Probe XiFamily)
    (acquisitionMoveRef : ProbeMove Probe XiFamily -> CollapseMoveRecord)
    (C : ChallengeClass) (horizon : Horizon)
    (descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord) where
  declaredCandidates :
    List (CollapseRescueCandidate S H descends probeFamilyPolicy
      descentReadoutPolicy readoutForProbeFamily installs postState
      repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
      reinstatementPolicy reclosureMoveRef economy riskAdmissible
      acquisitionMoveRef C horizon descentAttribution)
  complete :
    ∀ move :
      CollapseRescueCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution,
      move ∈ declaredCandidates

def CollapseFalsifier
    {descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon}
    {probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord}
    {descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord}
    {readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {repairMoveRef :
      RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
        CollapseMoveRecord}
    {boundaryUpdatePolicy :
      CarriedRecordPolicy S.T (BoundaryUpdateRecord S)}
    {appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord}
    {maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord}
    {reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S)}
    {reclosureMoveRef :
      MaintenanceReinstatementRecord S -> CollapseMoveRecord}
    {economy : ProbeEconomy S Probe XiFamily}
    {riskAdmissible : ViabilityRiskAdmissible Probe XiFamily}
    {acquisitionMoveRef : ProbeMove Probe XiFamily -> CollapseMoveRecord}
    {C : ChallengeClass} {horizon : Horizon}
    {descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord}
    (inventory :
      CompleteCollapseRescueInventory S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution) : Prop :=
  ∃ move, move ∈ inventory.declaredCandidates ∧
    CollapseRescueAdmissibleInBudget (S := S) (H := H) move ∧
    CollapseRescueDescends (S := S) (H := H) move

def NoCollapseFalsifier
    {descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon}
    {probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord}
    {descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord}
    {readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {repairMoveRef :
      RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
        CollapseMoveRecord}
    {boundaryUpdatePolicy :
      CarriedRecordPolicy S.T (BoundaryUpdateRecord S)}
    {appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord}
    {maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord}
    {reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S)}
    {reclosureMoveRef :
      MaintenanceReinstatementRecord S -> CollapseMoveRecord}
    {economy : ProbeEconomy S Probe XiFamily}
    {riskAdmissible : ViabilityRiskAdmissible Probe XiFamily}
    {acquisitionMoveRef : ProbeMove Probe XiFamily -> CollapseMoveRecord}
    {C : ChallengeClass} {horizon : Horizon}
    {descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord}
    (inventory :
      CompleteCollapseRescueInventory S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution) : Prop :=
  ¬ CollapseFalsifier (S := S) (H := H) inventory

structure StatusedResidualAccrual
    (residualPolicy : CarriedRecordPolicy S.T ResidualStatusRecord)
    (C : ChallengeClass) (horizon : Horizon) where
  challengeClass : ChallengeClass
  residualHorizon : Horizon
  scopeLinked : challengeClass = C ∧ residualHorizon = horizon
  residualRecord : ResidualStatusRecord
  residualSpend : Rat
  residualBudget : Rat
  residualCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt residualPolicy residualRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  accrualWithinBudget : residualSpend <= residualBudget

def CollapsedCore
    {descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon}
    {probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord}
    {descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord}
    {readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {repairMoveRef :
      RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
        CollapseMoveRecord}
    {boundaryUpdatePolicy :
      CarriedRecordPolicy S.T (BoundaryUpdateRecord S)}
    {appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord}
    {maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord}
    {reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S)}
    {reclosureMoveRef :
      MaintenanceReinstatementRecord S -> CollapseMoveRecord}
    {economy : ProbeEconomy S Probe XiFamily}
    {riskAdmissible : ViabilityRiskAdmissible Probe XiFamily}
    {acquisitionMoveRef : ProbeMove Probe XiFamily -> CollapseMoveRecord}
    {C : ChallengeClass} {horizon : Horizon}
    {descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord}
    (inventory :
      CompleteCollapseRescueInventory S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution) : Prop :=
  NoCollapseFalsifier (S := S) (H := H) inventory

structure RepairGeneratorReachabilityCertified where
  reachabilityRecord :
    RepairGeneratorReachabilityRecord
      (ChallengeClass := ChallengeClass) (Horizon := Horizon)
  selfReachable : Prop
  externallyReachableOnly : Prop
  unreachable : Prop
  exclusive :
    (selfReachable ∧ ¬ externallyReachableOnly ∧ ¬ unreachable) ∨
      (externallyReachableOnly ∧ ¬ selfReachable ∧ ¬ unreachable) ∨
        (unreachable ∧ ¬ selfReachable ∧ ¬ externallyReachableOnly)

structure ApparatusViabilityKernelCertified where
  kernelRecord :
    ApparatusViabilityKernelRecord
      (ChallengeClass := ChallengeClass) (Horizon := Horizon)
  kernelNonempty : Prop
  kernelEmpty : Prop
  complement : kernelNonempty ↔ ¬ kernelEmpty

structure IrreversibilityCoherence
    (C : ChallengeClass) (horizon : Horizon)
    (reach :
      RepairGeneratorReachabilityCertified
        (ChallengeClass := ChallengeClass) (Horizon := Horizon))
    (kernel :
      ApparatusViabilityKernelCertified
        (ChallengeClass := ChallengeClass) (Horizon := Horizon)) where
  currentScopeLinked :
    reach.reachabilityRecord.scope.challengeClass = C ∧
      reach.reachabilityRecord.scope.horizon = horizon ∧
      kernel.kernelRecord.scope.challengeClass = C ∧
      kernel.kernelRecord.scope.horizon = horizon
  sameDeclaredScope : reach.reachabilityRecord.scope = kernel.kernelRecord.scope
  unreachableIffKernelEmpty : reach.unreachable ↔ kernel.kernelEmpty

def IrreversibleCollapseInput
    (C : ChallengeClass) (horizon : Horizon)
    (reach :
      RepairGeneratorReachabilityCertified
        (ChallengeClass := ChallengeClass) (Horizon := Horizon))
    (kernel :
      ApparatusViabilityKernelCertified
        (ChallengeClass := ChallengeClass) (Horizon := Horizon)) : Prop :=
  ∃ _coherence : IrreversibilityCoherence C horizon reach kernel,
    reach.unreachable ∧ kernel.kernelEmpty

def RecoverableCollapseInput
    (C : ChallengeClass) (horizon : Horizon)
    (reach :
      RepairGeneratorReachabilityCertified
        (ChallengeClass := ChallengeClass) (Horizon := Horizon))
    (kernel :
      ApparatusViabilityKernelCertified
        (ChallengeClass := ChallengeClass) (Horizon := Horizon)) : Prop :=
  ∃ _coherence : IrreversibilityCoherence C horizon reach kernel,
    (reach.selfReachable ∨ reach.externallyReachableOnly ∨
      kernel.kernelNonempty) ∧
      ¬ IrreversibleCollapseInput C horizon reach kernel

/-- Certified ownership of a subsidizer-scope move record. -/
structure SubsidizerScopeOwns (ExternalCarrier : Type u) where
  holds : ExternalCarrier -> CollapseMoveRecord -> Prop

/-- Certified budget feasibility in the subsidizer scope. -/
structure SubsidizerBudgetFeasible (ExternalCarrier : Type u) where
  holds : ExternalCarrier -> CollapseMoveRecord -> Prop

/-- Certified descent of the declared probes in the subsidizer scope. -/
structure SubsidizerMoveDescends (ExternalCarrier : Type u)
    (History : Type v) (ChallengeClass : Type w) (Horizon : Type x) where
  holds : ExternalCarrier -> CollapseMoveRecord -> History ->
    ChallengeClass -> Horizon -> Prop

structure SubsidizerRescueCandidate
    (scopeOwns : SubsidizerScopeOwns ExternalCarrier)
    (budgetFeasible : SubsidizerBudgetFeasible ExternalCarrier)
    (moveDescends :
      SubsidizerMoveDescends ExternalCarrier
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon)
    (C : ChallengeClass) (horizon : Horizon) where
  subsidizer : ExternalCarrier
  moveRecord : CollapseMoveRecord
  carriedInSubsidizerScope : scopeOwns.holds subsidizer moveRecord
  budgetFeasibleInSubsidizerScope :
    budgetFeasible.holds subsidizer moveRecord
  descends : moveDescends.holds subsidizer moveRecord H C horizon

structure ExternalSubsidyWitness
    (subsidyPolicy : CarriedRecordPolicy S.T SubsidyRecord)
    (scopeOwns : SubsidizerScopeOwns ExternalCarrier)
    (budgetFeasible : SubsidizerBudgetFeasible ExternalCarrier)
    (moveDescends :
      SubsidizerMoveDescends ExternalCarrier
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon)
    (C : ChallengeClass) (horizon : Horizon)
    (SelfMove : Type u'') (selfMoveRecord : SelfMove -> CollapseMoveRecord) where
  subsidyRecord : SubsidyRecord
  subsidyRecordCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt subsidyPolicy subsidyRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  subsidizer : ExternalCarrier
  suppliedMove :
    SubsidizerRescueCandidate H scopeOwns budgetFeasible moveDescends C
      horizon
  suppliedMoveOwnedBySubsidizer : suppliedMove.subsidizer = subsidizer
  suppliedMoveDescends :
    moveDescends.holds suppliedMove.subsidizer suppliedMove.moveRecord H C
      horizon
  suppliedMoveInSubsidizerScope :
    scopeOwns.holds subsidizer suppliedMove.moveRecord
  notSelfCarried :
    ¬ ∃ selfMove : SelfMove, selfMoveRecord selfMove = suppliedMove.moveRecord

def ActiveExternalSubsidyAt
    {subsidyPolicy : CarriedRecordPolicy S.T SubsidyRecord}
    {scopeOwns : SubsidizerScopeOwns ExternalCarrier}
    {budgetFeasible : SubsidizerBudgetFeasible ExternalCarrier}
    {moveDescends :
      SubsidizerMoveDescends ExternalCarrier
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon}
    {C : ChallengeClass} {horizon : Horizon}
    {SelfMove : Type u''} {selfMoveRecord : SelfMove -> CollapseMoveRecord}
    (H0 :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord) : Prop :=
  ∃ _subsidy :
    ExternalSubsidyWitness S H0 subsidyPolicy scopeOwns budgetFeasible
      moveDescends C horizon SelfMove selfMoveRecord,
    True

def NoActiveExternalSubsidyAt
    {subsidyPolicy : CarriedRecordPolicy S.T SubsidyRecord}
    {scopeOwns : SubsidizerScopeOwns ExternalCarrier}
    {budgetFeasible : SubsidizerBudgetFeasible ExternalCarrier}
    {moveDescends :
      SubsidizerMoveDescends ExternalCarrier
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon}
    {C : ChallengeClass} {horizon : Horizon}
    {SelfMove : Type u''} {selfMoveRecord : SelfMove -> CollapseMoveRecord}
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord) : Prop :=
  ¬ (ActiveExternalSubsidyAt (S := S) (subsidyPolicy := subsidyPolicy)
    (scopeOwns := scopeOwns) (budgetFeasible := budgetFeasible)
    (moveDescends := moveDescends) (C := C) (horizon := horizon)
    (SelfMove := SelfMove) (selfMoveRecord := selfMoveRecord) H)

structure SubsidyWithdrawalEvent
    (subsidyWithdrawalPolicy :
      CarriedRecordPolicy S.T SubsidyWithdrawalRecord) where
  priorSubsidyRecord : SubsidyRecord
  withdrawalRecord : SubsidyWithdrawalRecord
  carried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt subsidyWithdrawalPolicy withdrawalRecord n0
          sourceTag generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  recordLinks : withdrawalRecord.priorSubsidyRecord = priorSubsidyRecord

structure SuspensionWitness
    (suspensionPolicy : CarriedRecordPolicy S.T SuspensionRecord)
    (apparatusIntact :
      ApparatusIntactCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon)
    (operationsGatedOff :
      OperationsGatedOffCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon)
    (bindingOperationalChallenge :
      BindingOperationalChallengeActive
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon)
    (C : ChallengeClass) (horizon : Horizon) where
  suspensionRecord : SuspensionRecord
  suspensionRecordCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt suspensionPolicy suspensionRecord n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  apparatusIntactForScope : apparatusIntact.holds S H C horizon
  operationsGatedOffForScope : operationsGatedOff.holds S H C horizon
  noCurrentBindingOperation :
    ¬ bindingOperationalChallenge.holds S H C horizon

structure ApparatusLineageRecord where
  lineageId : Nat
  deriving DecidableEq, Repr

structure RevivalWitness
    (priorStatusPredicate : PriorStatusIsSubsidizedOrCollapsed)
    (apparatusLineagePolicy :
      CarriedRecordPolicy S.T ApparatusLineageRecord)
    (C : ChallengeClass) (horizon : Horizon)
    {descends :
      ViabilityProbesDescendAtH
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
        ChallengeClass Horizon}
    {probeFamilyPolicy :
      CarriedRecordPolicy S.T ViabilityProbeFamilyRecord}
    {descentReadoutPolicy :
      CarriedRecordPolicy S.T ViabilityDescentReadoutRecord}
    {readoutForProbeFamily :
      DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
        ViabilityProbeFamilyRecord}
    (descentAttribution :
      RescueMoveCreditedForDescent S H C horizon
        ViabilityDescentReadoutRecord)
    {appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord}
    {maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord}
    {reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S)}
    {reclosureMoveRef :
      MaintenanceReinstatementRecord S -> CollapseMoveRecord} where
  priorStatusRef : ReclosureCollapseStatusRecordRef
  priorWasSubsidizedOrCollapsed :
    priorStatusPredicate.holds priorStatusRef
  newLineage : ApparatusLineageRecord
  oldLineage : ApparatusLineageRecord
  newLineageCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt apparatusLineagePolicy newLineage n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  oldLineageCarried :
    ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt apparatusLineagePolicy oldLineage n0 sourceTag
          generatedByS inScope ∧
        CarriedSource sourceTag generatedByS inScope
  lineageChanged : newLineage ≠ oldLineage
  reclosure :
    ApparatusReclosureCandidate S H descends probeFamilyPolicy
      descentReadoutPolicy readoutForProbeFamily appPolicy
      maintenancePolicy reinstatementPolicy reclosureMoveRef C horizon
      descentAttribution
  selfCarriedNow :
    ApparatusReclosureAdmissibleInBudget (S := S) (H := H)
      (C := C) (horizon := horizon)
      (descentAttribution := descentAttribution) reclosure

end Setup

section StatusApparatus

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
variable {ChallengeClass : Type z} {SourceQuotient : Type z'}
variable {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
variable {ObstructionWitness : Type z''''}
variable {Horizon : Type z'''''}
variable {RepairRefinement : Type u'} {Probe : Type v'}
variable {XiFamily : Type w'} {ExternalCarrier : Type x'}
variable {ViabilityProbeFamilyRecord : Type y''''''}
variable {ViabilityDescentReadoutRecord : Type y'''''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
  AuditRecord)
variable (H :
  ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
    TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)

inductive ReclosureCollapseStatus where
  | revived
  | subsidized
  | suspended
  | viable
  | stressed
  | collapsed_recoverable
  | collapsed_irreversible
  deriving DecidableEq, Repr

structure ReclosureCollapseStatusRecord
    (ChallengeClass : Type z) (Horizon : Type z''''')
    (LedgerEntry : Type y') (AuditRecord : Type y''''') where
  challengeClass : ChallengeClass
  horizon : Horizon
  status : ReclosureCollapseStatus
  residualRecord : Option ResidualStatusRecord
  rescueMoveRecord : Option CollapseMoveRecord
  subsidyRecord : Option SubsidyRecord
  suspensionRecord : Option SuspensionRecord
  priorStatusRecord : Option ReclosureCollapseStatusRecordRef
  lineageRecord : Option ApparatusLineageRecord
  reachabilityRecord :
    Option
      (RepairGeneratorReachabilityRecord
        (ChallengeClass := ChallengeClass) (Horizon := Horizon))
  kernelRecord :
    Option
      (ApparatusViabilityKernelRecord
        (ChallengeClass := ChallengeClass) (Horizon := Horizon))
  supportingLedgerEntries : List LedgerEntry
  supportingAuditRecords : List AuditRecord

def ReclosureCollapseStatusOccurrenceFor
    (statusPolicy : CarriedRecordPolicy S.T (ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord))
    (C : ChallengeClass) (horizon : Horizon)
    (record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord) : Prop :=
  record.challengeClass = C ∧
    record.horizon = horizon ∧
    (∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt statusPolicy record n0 sourceTag generatedByS
          inScope ∧
        CarriedSource sourceTag generatedByS inScope) ∧
    (∀ entry : LedgerEntry, entry ∈ record.supportingLedgerEntries ->
      entry ∈ S.Lambda_S.ledgerEntries) ∧
    ∀ auditRecord : AuditRecord, auditRecord ∈ record.supportingAuditRecords ->
      HasCarriedRecordEvidence S.auditRecordPolicy auditRecord

variable (descends :
  ViabilityProbesDescendAtH
    (ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
      TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
    ChallengeClass Horizon)
variable (probeFamilyPolicy :
  CarriedRecordPolicy S.T ViabilityProbeFamilyRecord)
variable (descentReadoutPolicy :
  CarriedRecordPolicy S.T ViabilityDescentReadoutRecord)
variable (readoutForProbeFamily :
  DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
    ViabilityProbeFamilyRecord)
variable (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
variable (postState :
  PostRepairStateForEpisode S ChallengeClass SourceQuotient
    DeclaredFamily TargetReadout ObstructionWitness)
variable (repairMoveRef :
  RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
    CollapseMoveRecord)
variable (boundaryUpdatePolicy :
  CarriedRecordPolicy S.T (BoundaryUpdateRecord S))
variable (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
variable (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
variable (reinstatementPolicy :
  CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
variable (reclosureMoveRef :
  MaintenanceReinstatementRecord S -> CollapseMoveRecord)
variable (economy : ProbeEconomy S Probe XiFamily)
variable (riskAdmissible : ViabilityRiskAdmissible Probe XiFamily)
variable (acquisitionMoveRef : ProbeMove Probe XiFamily -> CollapseMoveRecord)
variable (C : ChallengeClass) (horizon : Horizon)
variable (descentAttribution :
  RescueMoveCreditedForDescent S H C horizon ViabilityDescentReadoutRecord)
variable (inventory :
  CompleteCollapseRescueInventory S H descends probeFamilyPolicy
    descentReadoutPolicy readoutForProbeFamily installs postState
    repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
    reinstatementPolicy reclosureMoveRef economy riskAdmissible
    acquisitionMoveRef C horizon descentAttribution)
variable (statusPolicy :
  CarriedRecordPolicy S.T (ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord))
variable (residualPolicy : CarriedRecordPolicy S.T ResidualStatusRecord)
variable (priorStatusPredicate : PriorStatusIsSubsidizedOrCollapsed)
variable (apparatusLineagePolicy :
  CarriedRecordPolicy S.T ApparatusLineageRecord)
variable (subsidyPolicy : CarriedRecordPolicy S.T SubsidyRecord)
variable (scopeOwns : SubsidizerScopeOwns ExternalCarrier)
variable (subsidizerBudgetFeasible : SubsidizerBudgetFeasible ExternalCarrier)
variable (subsidizerMoveDescends :
  SubsidizerMoveDescends ExternalCarrier
    (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
      TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
    ChallengeClass Horizon)
variable (suspensionPolicy : CarriedRecordPolicy S.T SuspensionRecord)
variable (apparatusIntact :
  ApparatusIntactCertified
    (ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
      TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
    ChallengeClass Horizon)
variable (operationsGatedOff :
  OperationsGatedOffCertified
    (ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
      TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
    ChallengeClass Horizon)
variable (bindingOperationalChallenge :
  BindingOperationalChallengeActive
    (ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
      TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
    ChallengeClass Horizon)

def RevivedEvidenceFor : Prop :=
  Nonempty
    (RevivalWitness (S := S) (H := H) (descends := descends)
      (probeFamilyPolicy := probeFamilyPolicy)
      (descentReadoutPolicy := descentReadoutPolicy)
      (readoutForProbeFamily := readoutForProbeFamily)
      (appPolicy := appPolicy) (maintenancePolicy := maintenancePolicy)
      (reinstatementPolicy := reinstatementPolicy)
      (reclosureMoveRef := reclosureMoveRef)
      priorStatusPredicate apparatusLineagePolicy C horizon
      descentAttribution)

def SubsidizedEvidenceFor : Prop :=
  ∃ _subsidy :
      ExternalSubsidyWitness (S := S) (H := H)
        (subsidyPolicy := subsidyPolicy) (scopeOwns := scopeOwns)
        (budgetFeasible := subsidizerBudgetFeasible)
        (moveDescends := subsidizerMoveDescends)
        (C := C) (horizon := horizon)
        (SelfMove :=
          CollapseRescueCandidate S H descends probeFamilyPolicy
            descentReadoutPolicy readoutForProbeFamily installs postState
            repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
            reinstatementPolicy reclosureMoveRef economy riskAdmissible
            acquisitionMoveRef C horizon descentAttribution)
        (selfMoveRecord := fun move =>
          CollapseRescueMoveRecord (S := S) (H := H) move),
    ¬ ∃ selfMove, selfMove ∈ inventory.declaredCandidates ∧
      CollapseRescueAdmissibleInBudget (S := S) (H := H) selfMove ∧
      CollapseRescueDescends (S := S) (H := H) selfMove

def SuspendedEvidenceFor : Prop :=
  Nonempty
    (SuspensionWitness (S := S) (H := H) suspensionPolicy apparatusIntact
      operationsGatedOff bindingOperationalChallenge C horizon)

def ViableEvidenceFor : Prop :=
  ∃ move :
      CollapseRescueCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution,
    move ∈ inventory.declaredCandidates ∧
      CollapseRescueAdmissibleInBudget (S := S) (H := H) move ∧
      CollapseRescueDescends (S := S) (H := H) move ∧
      ¬ ∃ _residual : StatusedResidualAccrual S residualPolicy C horizon,
        True

def ReclosureStressedEvidenceFor : Prop :=
  ∃ _residual : StatusedResidualAccrual S residualPolicy C horizon,
    ∃ move :
        CollapseRescueCandidate S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution,
      move ∈ inventory.declaredCandidates ∧
        CollapseRescueAdmissibleInBudget (S := S) (H := H) move ∧
        CollapseRescueDescends (S := S) (H := H) move

def CollapsedIrreversibleEvidenceFor : Prop :=
  ∃ reach : RepairGeneratorReachabilityCertified
      (ChallengeClass := ChallengeClass) (Horizon := Horizon),
    ∃ kernel : ApparatusViabilityKernelCertified
        (ChallengeClass := ChallengeClass) (Horizon := Horizon),
      CollapsedCore (S := S) (H := H) inventory ∧
        IrreversibleCollapseInput C horizon reach kernel

def RevivedEvidence
    (record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord)
    (revival :
      RevivalWitness (S := S) (H := H) (descends := descends)
        (probeFamilyPolicy := probeFamilyPolicy)
        (descentReadoutPolicy := descentReadoutPolicy)
        (readoutForProbeFamily := readoutForProbeFamily)
        (appPolicy := appPolicy) (maintenancePolicy := maintenancePolicy)
        (reinstatementPolicy := reinstatementPolicy)
        (reclosureMoveRef := reclosureMoveRef)
        priorStatusPredicate apparatusLineagePolicy C horizon
        descentAttribution) : Prop :=
  record.status = ReclosureCollapseStatus.revived ∧
    record.priorStatusRecord = some revival.priorStatusRef ∧
    record.lineageRecord = some revival.newLineage ∧
    record.rescueMoveRecord = some revival.reclosure.moveRecord

def RevivedCase (record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord) : Prop :=
  ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon record ∧
    ∃ revival :
      RevivalWitness (S := S) (H := H) (descends := descends)
        (probeFamilyPolicy := probeFamilyPolicy)
        (descentReadoutPolicy := descentReadoutPolicy)
        (readoutForProbeFamily := readoutForProbeFamily)
        (appPolicy := appPolicy) (maintenancePolicy := maintenancePolicy)
        (reinstatementPolicy := reinstatementPolicy)
        (reclosureMoveRef := reclosureMoveRef)
        priorStatusPredicate apparatusLineagePolicy C horizon
        descentAttribution,
      RevivedEvidence S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily appPolicy maintenancePolicy reinstatementPolicy
        reclosureMoveRef C horizon descentAttribution priorStatusPredicate
        apparatusLineagePolicy record revival

def SubsidizedEvidence
    (record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord)
    (subsidy :
      ExternalSubsidyWitness (S := S) (H := H)
        (subsidyPolicy := subsidyPolicy) (scopeOwns := scopeOwns)
        (budgetFeasible := subsidizerBudgetFeasible)
        (moveDescends := subsidizerMoveDescends)
        (C := C) (horizon := horizon)
        (SelfMove :=
          CollapseRescueCandidate S H descends probeFamilyPolicy
            descentReadoutPolicy readoutForProbeFamily installs postState
            repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
            reinstatementPolicy reclosureMoveRef economy riskAdmissible
            acquisitionMoveRef C horizon descentAttribution)
        (selfMoveRecord := fun move =>
          CollapseRescueMoveRecord (S := S) (H := H) move)) : Prop :=
  (¬ ∃ selfMove, selfMove ∈ inventory.declaredCandidates ∧
    CollapseRescueAdmissibleInBudget (S := S) (H := H) selfMove ∧
    CollapseRescueDescends (S := S) (H := H) selfMove) ∧
    record.status = ReclosureCollapseStatus.subsidized ∧
    record.subsidyRecord = some subsidy.subsidyRecord

def SubsidizedCase (record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord) : Prop :=
  ¬ RevivedEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
      readoutForProbeFamily appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef C horizon descentAttribution
      priorStatusPredicate apparatusLineagePolicy ∧
    ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon record ∧
    ∃ subsidy :
      ExternalSubsidyWitness (S := S) (H := H)
        (subsidyPolicy := subsidyPolicy) (scopeOwns := scopeOwns)
        (budgetFeasible := subsidizerBudgetFeasible)
        (moveDescends := subsidizerMoveDescends)
        (C := C) (horizon := horizon)
        (SelfMove :=
          CollapseRescueCandidate S H descends probeFamilyPolicy
            descentReadoutPolicy readoutForProbeFamily installs postState
            repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
            reinstatementPolicy reclosureMoveRef economy riskAdmissible
            acquisitionMoveRef C horizon descentAttribution)
        (selfMoveRecord := fun move =>
          CollapseRescueMoveRecord (S := S) (H := H) move),
      SubsidizedEvidence S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends record subsidy

def SuspendedEvidence
    (record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord)
    (suspension :
      SuspensionWitness (S := S) (H := H) suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge C horizon) : Prop :=
  record.status = ReclosureCollapseStatus.suspended ∧
    record.suspensionRecord = some suspension.suspensionRecord

def SuspendedCase (record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord) : Prop :=
  ¬ RevivedEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
      readoutForProbeFamily appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef C horizon descentAttribution
      priorStatusPredicate apparatusLineagePolicy ∧
    ¬ SubsidizedEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
      readoutForProbeFamily installs postState repairMoveRef
      boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
      descentAttribution inventory subsidyPolicy scopeOwns
      subsidizerBudgetFeasible subsidizerMoveDescends ∧
    ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon record ∧
    ∃ suspension :
      SuspensionWitness (S := S) (H := H) suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge C horizon,
      SuspendedEvidence S H C horizon suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge record suspension

def ViableEvidence
    (record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord)
    (move :
      CollapseRescueCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution) : Prop :=
  move ∈ inventory.declaredCandidates ∧
    CollapseRescueAdmissibleInBudget (S := S) (H := H) move ∧
    CollapseRescueDescends (S := S) (H := H) move ∧
    (¬ ∃ _residual : StatusedResidualAccrual S residualPolicy C horizon,
      True) ∧
    record.status = ReclosureCollapseStatus.viable ∧
    record.rescueMoveRecord =
      some (CollapseRescueMoveRecord (S := S) (H := H) move)

def ViableCase (record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord) : Prop :=
  ¬ RevivedEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
      readoutForProbeFamily appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef C horizon descentAttribution
      priorStatusPredicate apparatusLineagePolicy ∧
    ¬ SubsidizedEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
      readoutForProbeFamily installs postState repairMoveRef
      boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
      descentAttribution inventory subsidyPolicy scopeOwns
      subsidizerBudgetFeasible subsidizerMoveDescends ∧
    ¬ SuspendedEvidenceFor S H C horizon suspensionPolicy apparatusIntact
      operationsGatedOff bindingOperationalChallenge ∧
    ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon record ∧
    ∃ move :
      CollapseRescueCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution,
      ViableEvidence S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily installs postState repairMoveRef
        boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
        reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
        descentAttribution inventory residualPolicy record move

def ReclosureStressedEvidence
    (record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord)
    (residual : StatusedResidualAccrual S residualPolicy C horizon)
    (move :
      CollapseRescueCandidate S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution) : Prop :=
  move ∈ inventory.declaredCandidates ∧
    CollapseRescueAdmissibleInBudget (S := S) (H := H) move ∧
    CollapseRescueDescends (S := S) (H := H) move ∧
    record.status = ReclosureCollapseStatus.stressed ∧
    record.residualRecord = some residual.residualRecord ∧
    record.rescueMoveRecord =
      some (CollapseRescueMoveRecord (S := S) (H := H) move)

def ReclosureStressedCase (record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord) : Prop :=
  ¬ RevivedEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
      readoutForProbeFamily appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef C horizon descentAttribution
      priorStatusPredicate apparatusLineagePolicy ∧
    ¬ SubsidizedEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
      readoutForProbeFamily installs postState repairMoveRef
      boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
      descentAttribution inventory subsidyPolicy scopeOwns
      subsidizerBudgetFeasible subsidizerMoveDescends ∧
    ¬ SuspendedEvidenceFor S H C horizon suspensionPolicy apparatusIntact
      operationsGatedOff bindingOperationalChallenge ∧
    ¬ ViableEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
      readoutForProbeFamily installs postState repairMoveRef
      boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
      descentAttribution inventory residualPolicy ∧
    ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon record ∧
    ∃ residual : StatusedResidualAccrual S residualPolicy C horizon,
      ∃ move :
        CollapseRescueCandidate S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution,
        ReclosureStressedEvidence S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          residualPolicy record residual move

def CollapsedIrreversibleEvidence
    (record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord)
    (reach : RepairGeneratorReachabilityCertified
      (ChallengeClass := ChallengeClass) (Horizon := Horizon))
    (kernel : ApparatusViabilityKernelCertified
      (ChallengeClass := ChallengeClass) (Horizon := Horizon)) : Prop :=
  CollapsedCore (S := S) (H := H) inventory ∧
    IrreversibleCollapseInput C horizon reach kernel ∧
    record.status = ReclosureCollapseStatus.collapsed_irreversible ∧
    record.reachabilityRecord = some reach.reachabilityRecord ∧
    record.kernelRecord = some kernel.kernelRecord ∧
    record.rescueMoveRecord = none

def CollapsedIrreversibleCase
    (record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord) : Prop :=
  ¬ RevivedEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
      readoutForProbeFamily appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef C horizon descentAttribution
      priorStatusPredicate apparatusLineagePolicy ∧
    ¬ SubsidizedEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
      readoutForProbeFamily installs postState repairMoveRef
      boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
      descentAttribution inventory subsidyPolicy scopeOwns
      subsidizerBudgetFeasible subsidizerMoveDescends ∧
    ¬ SuspendedEvidenceFor S H C horizon suspensionPolicy apparatusIntact
      operationsGatedOff bindingOperationalChallenge ∧
    ¬ ViableEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
      readoutForProbeFamily installs postState repairMoveRef
      boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
      descentAttribution inventory residualPolicy ∧
    ¬ ReclosureStressedEvidenceFor S H descends probeFamilyPolicy
      descentReadoutPolicy
      readoutForProbeFamily installs postState repairMoveRef
      boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
      descentAttribution inventory residualPolicy ∧
    ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon record ∧
    ∃ reach : RepairGeneratorReachabilityCertified
        (ChallengeClass := ChallengeClass) (Horizon := Horizon),
      ∃ kernel : ApparatusViabilityKernelCertified
          (ChallengeClass := ChallengeClass) (Horizon := Horizon),
        CollapsedIrreversibleEvidence S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory record
          reach kernel

def CollapsedRecoverableEvidence
    (record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord)
    (reach : RepairGeneratorReachabilityCertified
      (ChallengeClass := ChallengeClass) (Horizon := Horizon))
    (kernel : ApparatusViabilityKernelCertified
      (ChallengeClass := ChallengeClass) (Horizon := Horizon)) : Prop :=
  CollapsedCore (S := S) (H := H) inventory ∧
    RecoverableCollapseInput C horizon reach kernel ∧
    record.status = ReclosureCollapseStatus.collapsed_recoverable ∧
    record.reachabilityRecord = some reach.reachabilityRecord ∧
    record.kernelRecord = some kernel.kernelRecord ∧
    record.rescueMoveRecord = none

def CollapsedRecoverableCase
    (record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord) : Prop :=
  ¬ RevivedEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
      readoutForProbeFamily appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef C horizon descentAttribution
      priorStatusPredicate apparatusLineagePolicy ∧
    ¬ SubsidizedEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
      readoutForProbeFamily installs postState repairMoveRef
      boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
      descentAttribution inventory subsidyPolicy scopeOwns
      subsidizerBudgetFeasible subsidizerMoveDescends ∧
    ¬ SuspendedEvidenceFor S H C horizon suspensionPolicy apparatusIntact
      operationsGatedOff bindingOperationalChallenge ∧
    ¬ ViableEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
      readoutForProbeFamily installs postState repairMoveRef
      boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
      descentAttribution inventory residualPolicy ∧
    ¬ ReclosureStressedEvidenceFor S H descends probeFamilyPolicy
      descentReadoutPolicy
      readoutForProbeFamily installs postState repairMoveRef
      boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
      reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
      descentAttribution inventory residualPolicy ∧
    ¬ CollapsedIrreversibleEvidenceFor S H descends probeFamilyPolicy
      descentReadoutPolicy readoutForProbeFamily installs postState
      repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
      reinstatementPolicy reclosureMoveRef economy riskAdmissible
      acquisitionMoveRef C horizon descentAttribution inventory ∧
    ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon record ∧
    ∃ reach : RepairGeneratorReachabilityCertified
        (ChallengeClass := ChallengeClass) (Horizon := Horizon),
      ∃ kernel : ApparatusViabilityKernelCertified
          (ChallengeClass := ChallengeClass) (Horizon := Horizon),
        CollapsedRecoverableEvidence S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory record
          reach kernel

def RevivedHolds : Prop :=
  ∃ record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord,
    ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon record ∧
      record.status = ReclosureCollapseStatus.revived ∧
      RevivedCase S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef C horizon descentAttribution
        statusPolicy priorStatusPredicate apparatusLineagePolicy record

def SubsidizedHolds : Prop :=
  ∃ record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord,
    ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon record ∧
      record.status = ReclosureCollapseStatus.subsidized ∧
      SubsidizedCase S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily installs postState repairMoveRef
        boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
        reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
        descentAttribution inventory statusPolicy priorStatusPredicate
        apparatusLineagePolicy subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends record

def SuspendedHolds : Prop :=
  ∃ record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord,
    ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon record ∧
      record.status = ReclosureCollapseStatus.suspended ∧
      SuspendedCase S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily installs postState repairMoveRef
        boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
        reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
        descentAttribution inventory statusPolicy priorStatusPredicate
        apparatusLineagePolicy subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
        apparatusIntact operationsGatedOff bindingOperationalChallenge record

def ViableHolds : Prop :=
  ∃ record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord,
    ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon record ∧
      record.status = ReclosureCollapseStatus.viable ∧
      ViableCase S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily installs postState repairMoveRef
        boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
        reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
        descentAttribution inventory statusPolicy residualPolicy
        priorStatusPredicate apparatusLineagePolicy subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
        apparatusIntact operationsGatedOff bindingOperationalChallenge record

def ReclosureStressedHolds : Prop :=
  ∃ record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord,
    ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon record ∧
      record.status = ReclosureCollapseStatus.stressed ∧
      ReclosureStressedCase S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily installs postState repairMoveRef
        boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
        reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
        descentAttribution inventory statusPolicy residualPolicy
        priorStatusPredicate apparatusLineagePolicy subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
        apparatusIntact operationsGatedOff bindingOperationalChallenge record

def CollapsedIrreversibleHolds : Prop :=
  ∃ record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord,
    ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon record ∧
      record.status = ReclosureCollapseStatus.collapsed_irreversible ∧
      CollapsedIrreversibleCase S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        statusPolicy residualPolicy priorStatusPredicate apparatusLineagePolicy
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge record

def CollapsedRecoverableHolds : Prop :=
  ∃ record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord,
    ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon record ∧
      record.status = ReclosureCollapseStatus.collapsed_recoverable ∧
      CollapsedRecoverableCase S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        statusPolicy residualPolicy priorStatusPredicate apparatusLineagePolicy
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge record

def CompleteReclosureCollapseStatus : Prop :=
  (∃ record : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord,
    ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon record ∧
      (RevivedCase S H descends probeFamilyPolicy descentReadoutPolicy
          readoutForProbeFamily appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef C horizon descentAttribution
          statusPolicy priorStatusPredicate apparatusLineagePolicy record ∨
        SubsidizedCase S H descends probeFamilyPolicy descentReadoutPolicy
          readoutForProbeFamily installs postState repairMoveRef
          boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
          reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
          descentAttribution inventory statusPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends record ∨
        SuspendedCase S H descends probeFamilyPolicy descentReadoutPolicy
          readoutForProbeFamily installs postState repairMoveRef
          boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
          reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
          descentAttribution inventory statusPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge
          record ∨
        ViableCase S H descends probeFamilyPolicy descentReadoutPolicy
          readoutForProbeFamily installs postState repairMoveRef
          boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
          reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
          descentAttribution inventory statusPolicy residualPolicy
          priorStatusPredicate apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge
          record ∨
        ReclosureStressedCase S H descends probeFamilyPolicy descentReadoutPolicy
          readoutForProbeFamily installs postState repairMoveRef
          boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
          reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
          descentAttribution inventory statusPolicy residualPolicy
          priorStatusPredicate apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge
          record ∨
        CollapsedIrreversibleCase S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate apparatusLineagePolicy
          subsidyPolicy scopeOwns subsidizerBudgetFeasible
          subsidizerMoveDescends suspensionPolicy apparatusIntact
          operationsGatedOff bindingOperationalChallenge record ∨
        CollapsedRecoverableCase S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate apparatusLineagePolicy
          subsidyPolicy scopeOwns subsidizerBudgetFeasible
          subsidizerMoveDescends suspensionPolicy apparatusIntact
          operationsGatedOff bindingOperationalChallenge record)) ∧
    ∀ record1 record2 : ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord,
      ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon
        record1 ->
      ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon
        record2 ->
      record1.status = record2.status

end StatusApparatus

section Theorems

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
variable {ChallengeClass : Type z} {SourceQuotient : Type z'}
variable {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
variable {ObstructionWitness : Type z''''}
variable {Horizon : Type z'''''}
variable {RepairRefinement : Type u'} {Probe : Type v'}
variable {XiFamily : Type w'} {ExternalCarrier : Type x'}
variable {ViabilityProbeFamilyRecord : Type y''''''}
variable {ViabilityDescentReadoutRecord : Type y'''''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
  AuditRecord)
variable (H :
  ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
    TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)

variable (descends :
  ViabilityProbesDescendAtH
    (ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
      TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
    ChallengeClass Horizon)
variable (probeFamilyPolicy :
  CarriedRecordPolicy S.T ViabilityProbeFamilyRecord)
variable (descentReadoutPolicy :
  CarriedRecordPolicy S.T ViabilityDescentReadoutRecord)
variable (readoutForProbeFamily :
  DescentReadoutForProbeFamily ViabilityDescentReadoutRecord
    ViabilityProbeFamilyRecord)
variable (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
variable (postState :
  PostRepairStateForEpisode S ChallengeClass SourceQuotient
    DeclaredFamily TargetReadout ObstructionWitness)
variable (repairMoveRef :
  RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord ->
    CollapseMoveRecord)
variable (boundaryUpdatePolicy :
  CarriedRecordPolicy S.T (BoundaryUpdateRecord S))
variable (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
variable (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
variable (reinstatementPolicy :
  CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
variable (reclosureMoveRef :
  MaintenanceReinstatementRecord S -> CollapseMoveRecord)
variable (economy : ProbeEconomy S Probe XiFamily)
variable (riskAdmissible : ViabilityRiskAdmissible Probe XiFamily)
variable (acquisitionMoveRef : ProbeMove Probe XiFamily -> CollapseMoveRecord)
variable (C : ChallengeClass) (horizon : Horizon)
variable (descentAttribution :
  RescueMoveCreditedForDescent S H C horizon ViabilityDescentReadoutRecord)
variable (inventory :
  CompleteCollapseRescueInventory S H descends probeFamilyPolicy
    descentReadoutPolicy readoutForProbeFamily installs postState
    repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
    reinstatementPolicy reclosureMoveRef economy riskAdmissible
    acquisitionMoveRef C horizon descentAttribution)
variable (statusPolicy :
  CarriedRecordPolicy S.T (ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry AuditRecord))
variable (residualPolicy : CarriedRecordPolicy S.T ResidualStatusRecord)
variable (priorStatusPredicate : PriorStatusIsSubsidizedOrCollapsed)
variable (apparatusLineagePolicy :
  CarriedRecordPolicy S.T ApparatusLineageRecord)
variable (subsidyPolicy : CarriedRecordPolicy S.T SubsidyRecord)
variable (scopeOwns : SubsidizerScopeOwns ExternalCarrier)
variable (subsidizerBudgetFeasible : SubsidizerBudgetFeasible ExternalCarrier)
variable (subsidizerMoveDescends :
  SubsidizerMoveDescends ExternalCarrier
    (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
      TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
    ChallengeClass Horizon)
variable (suspensionPolicy : CarriedRecordPolicy S.T SuspensionRecord)
variable (apparatusIntact :
  ApparatusIntactCertified
    (ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
      TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
    ChallengeClass Horizon)
variable (operationsGatedOff :
  OperationsGatedOffCertified
    (ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
      TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
    ChallengeClass Horizon)
variable (bindingOperationalChallenge :
  BindingOperationalChallengeActive
    (ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
      TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
    ChallengeClass Horizon)

theorem E5_CollapseFalsifier
    (hFalsifier :
      CollapseFalsifier (S := S) (H := H) inventory) :
    ¬ CollapsedCore (S := S) (H := H) inventory := by
  intro hCollapsed
  exact hCollapsed hFalsifier

theorem E5_ReclosureCollapse
    (hComplete :
      CompleteReclosureCollapseStatus S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        statusPolicy residualPolicy priorStatusPredicate apparatusLineagePolicy
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge) :
    (RevivedHolds S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef C horizon descentAttribution
        statusPolicy priorStatusPredicate apparatusLineagePolicy ∧
        ¬ SubsidizedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy priorStatusPredicate apparatusLineagePolicy
          subsidyPolicy scopeOwns subsidizerBudgetFeasible
          subsidizerMoveDescends ∧
        ¬ SuspendedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy priorStatusPredicate apparatusLineagePolicy
          subsidyPolicy scopeOwns subsidizerBudgetFeasible
          subsidizerMoveDescends suspensionPolicy apparatusIntact
          operationsGatedOff bindingOperationalChallenge ∧
        ¬ ViableHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ ReclosureStressedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ CollapsedIrreversibleHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ CollapsedRecoverableHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge) ∨
      (SubsidizedHolds S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        statusPolicy priorStatusPredicate apparatusLineagePolicy
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends ∧
        ¬ RevivedHolds S H descends probeFamilyPolicy descentReadoutPolicy
          readoutForProbeFamily appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef C horizon descentAttribution
          statusPolicy priorStatusPredicate apparatusLineagePolicy ∧
        ¬ SuspendedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy priorStatusPredicate apparatusLineagePolicy
          subsidyPolicy scopeOwns subsidizerBudgetFeasible
          subsidizerMoveDescends suspensionPolicy apparatusIntact
          operationsGatedOff bindingOperationalChallenge ∧
        ¬ ViableHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ ReclosureStressedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ CollapsedIrreversibleHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ CollapsedRecoverableHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge) ∨
      (SuspendedHolds S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        statusPolicy priorStatusPredicate apparatusLineagePolicy
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge ∧
        ¬ RevivedHolds S H descends probeFamilyPolicy descentReadoutPolicy
          readoutForProbeFamily appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef C horizon descentAttribution
          statusPolicy priorStatusPredicate apparatusLineagePolicy ∧
        ¬ SubsidizedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy priorStatusPredicate apparatusLineagePolicy
          subsidyPolicy scopeOwns subsidizerBudgetFeasible
          subsidizerMoveDescends ∧
        ¬ ViableHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ ReclosureStressedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ CollapsedIrreversibleHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ CollapsedRecoverableHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge) ∨
      (ViableHolds S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily installs postState repairMoveRef
        boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
        reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
        descentAttribution inventory statusPolicy residualPolicy
        priorStatusPredicate apparatusLineagePolicy subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
        apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ RevivedHolds S H descends probeFamilyPolicy descentReadoutPolicy
          readoutForProbeFamily appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef C horizon descentAttribution
          statusPolicy priorStatusPredicate apparatusLineagePolicy ∧
        ¬ SubsidizedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy priorStatusPredicate apparatusLineagePolicy
          subsidyPolicy scopeOwns subsidizerBudgetFeasible
          subsidizerMoveDescends ∧
        ¬ SuspendedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy priorStatusPredicate apparatusLineagePolicy
          subsidyPolicy scopeOwns subsidizerBudgetFeasible
          subsidizerMoveDescends suspensionPolicy apparatusIntact
          operationsGatedOff bindingOperationalChallenge ∧
        ¬ ReclosureStressedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ CollapsedIrreversibleHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ CollapsedRecoverableHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge) ∨
      (ReclosureStressedHolds S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        statusPolicy residualPolicy priorStatusPredicate apparatusLineagePolicy
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge ∧
        ¬ RevivedHolds S H descends probeFamilyPolicy descentReadoutPolicy
          readoutForProbeFamily appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef C horizon descentAttribution
          statusPolicy priorStatusPredicate apparatusLineagePolicy ∧
        ¬ SubsidizedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy priorStatusPredicate apparatusLineagePolicy
          subsidyPolicy scopeOwns subsidizerBudgetFeasible
          subsidizerMoveDescends ∧
        ¬ SuspendedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy priorStatusPredicate apparatusLineagePolicy
          subsidyPolicy scopeOwns subsidizerBudgetFeasible
          subsidizerMoveDescends suspensionPolicy apparatusIntact
          operationsGatedOff bindingOperationalChallenge ∧
        ¬ ViableHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ CollapsedIrreversibleHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ CollapsedRecoverableHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge) ∨
      (CollapsedIrreversibleHolds S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        statusPolicy residualPolicy priorStatusPredicate apparatusLineagePolicy
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge ∧
        ¬ RevivedHolds S H descends probeFamilyPolicy descentReadoutPolicy
          readoutForProbeFamily appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef C horizon descentAttribution
          statusPolicy priorStatusPredicate apparatusLineagePolicy ∧
        ¬ SubsidizedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy priorStatusPredicate apparatusLineagePolicy
          subsidyPolicy scopeOwns subsidizerBudgetFeasible
          subsidizerMoveDescends ∧
        ¬ SuspendedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy priorStatusPredicate apparatusLineagePolicy
          subsidyPolicy scopeOwns subsidizerBudgetFeasible
          subsidizerMoveDescends suspensionPolicy apparatusIntact
          operationsGatedOff bindingOperationalChallenge ∧
        ¬ ViableHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ ReclosureStressedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ CollapsedRecoverableHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge) ∨
      (CollapsedRecoverableHolds S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        statusPolicy residualPolicy priorStatusPredicate apparatusLineagePolicy
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge ∧
        ¬ RevivedHolds S H descends probeFamilyPolicy descentReadoutPolicy
          readoutForProbeFamily appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef C horizon descentAttribution
          statusPolicy priorStatusPredicate apparatusLineagePolicy ∧
        ¬ SubsidizedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy priorStatusPredicate apparatusLineagePolicy
          subsidyPolicy scopeOwns subsidizerBudgetFeasible
          subsidizerMoveDescends ∧
        ¬ SuspendedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy priorStatusPredicate apparatusLineagePolicy
          subsidyPolicy scopeOwns subsidizerBudgetFeasible
          subsidizerMoveDescends suspensionPolicy apparatusIntact
          operationsGatedOff bindingOperationalChallenge ∧
        ¬ ViableHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ ReclosureStressedHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
        ¬ CollapsedIrreversibleHolds S H descends probeFamilyPolicy
          descentReadoutPolicy readoutForProbeFamily installs postState
          repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef economy riskAdmissible
          acquisitionMoveRef C horizon descentAttribution inventory
          statusPolicy residualPolicy priorStatusPredicate
          apparatusLineagePolicy subsidyPolicy scopeOwns
          subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
          apparatusIntact operationsGatedOff bindingOperationalChallenge) := by
  rcases hComplete.1 with ⟨record, hOccurrence, hBranch⟩
  rcases hBranch with hRevived | hRest
  · have hStatus :
        record.status = ReclosureCollapseStatus.revived := by
      rcases hRevived with ⟨_, revival, hEvidence⟩
      exact hEvidence.1
    have hHolds :
        RevivedHolds S H descends probeFamilyPolicy descentReadoutPolicy
          readoutForProbeFamily appPolicy maintenancePolicy
          reinstatementPolicy reclosureMoveRef C horizon descentAttribution
          statusPolicy priorStatusPredicate apparatusLineagePolicy :=
      ⟨record, hOccurrence, hStatus, hRevived⟩
    refine Or.inl ?_
    refine ⟨hHolds, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
      intro hOther <;>
      rcases hOther with ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩ <;>
      have hSame := hComplete.2 record other hOccurrence hOtherOccurrence <;>
      rw [hStatus, hOtherStatus] at hSame <;>
      cases hSame
  · rcases hRest with hSubsidized | hRest
    · have hStatus :
          record.status = ReclosureCollapseStatus.subsidized := by
        rcases hSubsidized with ⟨_, _, subsidy, hEvidence⟩
        exact hEvidence.2.1
      have hHolds :
          SubsidizedHolds S H descends probeFamilyPolicy
            descentReadoutPolicy readoutForProbeFamily installs postState
            repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
            reinstatementPolicy reclosureMoveRef economy riskAdmissible
            acquisitionMoveRef C horizon descentAttribution inventory
            statusPolicy priorStatusPredicate apparatusLineagePolicy
            subsidyPolicy scopeOwns subsidizerBudgetFeasible
            subsidizerMoveDescends :=
        ⟨record, hOccurrence, hStatus, hSubsidized⟩
      refine Or.inr (Or.inl ?_)
      refine ⟨hHolds, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
        intro hOther <;>
        rcases hOther with ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩ <;>
        have hSame := hComplete.2 record other hOccurrence hOtherOccurrence <;>
        rw [hStatus, hOtherStatus] at hSame <;>
        cases hSame
    · rcases hRest with hSuspended | hRest
      · have hStatus :
            record.status = ReclosureCollapseStatus.suspended := by
          rcases hSuspended with ⟨_, _, _, suspension, hEvidence⟩
          exact hEvidence.1
        have hHolds :
            SuspendedHolds S H descends probeFamilyPolicy
              descentReadoutPolicy readoutForProbeFamily installs postState
              repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
              reinstatementPolicy reclosureMoveRef economy riskAdmissible
              acquisitionMoveRef C horizon descentAttribution inventory
              statusPolicy priorStatusPredicate apparatusLineagePolicy
              subsidyPolicy scopeOwns subsidizerBudgetFeasible
              subsidizerMoveDescends suspensionPolicy apparatusIntact
              operationsGatedOff bindingOperationalChallenge :=
          ⟨record, hOccurrence, hStatus, hSuspended⟩
        refine Or.inr (Or.inr (Or.inl ?_))
        refine ⟨hHolds, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
          intro hOther <;>
          rcases hOther with ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩ <;>
          have hSame := hComplete.2 record other hOccurrence hOtherOccurrence <;>
          rw [hStatus, hOtherStatus] at hSame <;>
          cases hSame
      · rcases hRest with hViable | hRest
        · have hStatus :
              record.status = ReclosureCollapseStatus.viable := by
            rcases hViable with ⟨_, _, _, _, move, hEvidence⟩
            rcases hEvidence with ⟨_, _, _, _, hStatus, _⟩
            exact hStatus
          have hHolds :
              ViableHolds S H descends probeFamilyPolicy
                descentReadoutPolicy readoutForProbeFamily installs postState
                repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
                reinstatementPolicy reclosureMoveRef economy riskAdmissible
                acquisitionMoveRef C horizon descentAttribution inventory
                statusPolicy residualPolicy priorStatusPredicate
                apparatusLineagePolicy subsidyPolicy scopeOwns
                subsidizerBudgetFeasible subsidizerMoveDescends
                suspensionPolicy apparatusIntact operationsGatedOff
                bindingOperationalChallenge :=
            ⟨record, hOccurrence, hStatus, hViable⟩
          refine Or.inr (Or.inr (Or.inr (Or.inl ?_)))
          refine ⟨hHolds, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
            intro hOther <;>
            rcases hOther with ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩ <;>
            have hSame := hComplete.2 record other hOccurrence hOtherOccurrence <;>
            rw [hStatus, hOtherStatus] at hSame <;>
            cases hSame
        · rcases hRest with hStressed | hRest
          · have hStatus :
                record.status = ReclosureCollapseStatus.stressed := by
              rcases hStressed with ⟨_, _, _, _, _, residual, move, hEvidence⟩
              rcases hEvidence with ⟨_, _, _, hStatus, _, _⟩
              exact hStatus
            have hHolds :
                ReclosureStressedHolds S H descends probeFamilyPolicy
                  descentReadoutPolicy readoutForProbeFamily installs postState
                  repairMoveRef boundaryUpdatePolicy appPolicy
                  maintenancePolicy reinstatementPolicy reclosureMoveRef
                  economy riskAdmissible acquisitionMoveRef C horizon
                  descentAttribution inventory statusPolicy residualPolicy
                  priorStatusPredicate apparatusLineagePolicy subsidyPolicy
                  scopeOwns subsidizerBudgetFeasible subsidizerMoveDescends
                  suspensionPolicy apparatusIntact operationsGatedOff
                  bindingOperationalChallenge :=
              ⟨record, hOccurrence, hStatus, hStressed⟩
            refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ?_))))
            refine ⟨hHolds, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
              intro hOther <;>
              rcases hOther with ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩ <;>
              have hSame := hComplete.2 record other hOccurrence hOtherOccurrence <;>
              rw [hStatus, hOtherStatus] at hSame <;>
              cases hSame
          · rcases hRest with hIrreversible | hRecoverable
            · have hStatus :
                  record.status =
                    ReclosureCollapseStatus.collapsed_irreversible := by
                rcases hIrreversible with
                  ⟨_, _, _, _, _, _, reach, kernel, hEvidence⟩
                rcases hEvidence with ⟨_, _, hStatus, _, _, _⟩
                exact hStatus
              have hHolds :
                  CollapsedIrreversibleHolds S H descends probeFamilyPolicy
                    descentReadoutPolicy readoutForProbeFamily installs
                    postState repairMoveRef boundaryUpdatePolicy appPolicy
                    maintenancePolicy reinstatementPolicy reclosureMoveRef
                    economy riskAdmissible acquisitionMoveRef C horizon
                    descentAttribution inventory statusPolicy residualPolicy
                    priorStatusPredicate apparatusLineagePolicy subsidyPolicy
                    scopeOwns subsidizerBudgetFeasible subsidizerMoveDescends
                    suspensionPolicy apparatusIntact operationsGatedOff
                    bindingOperationalChallenge :=
                ⟨record, hOccurrence, hStatus, hIrreversible⟩
              refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ?_)))))
              refine ⟨hHolds, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
                intro hOther <;>
                rcases hOther with ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩ <;>
                have hSame := hComplete.2 record other hOccurrence hOtherOccurrence <;>
                rw [hStatus, hOtherStatus] at hSame <;>
                cases hSame
            · have hStatus :
                  record.status =
                    ReclosureCollapseStatus.collapsed_recoverable := by
                rcases hRecoverable with
                  ⟨_, _, _, _, _, _, _, reach, kernel, hEvidence⟩
                rcases hEvidence with ⟨_, _, hStatus, _, _, _⟩
                exact hStatus
              have hHolds :
                  CollapsedRecoverableHolds S H descends probeFamilyPolicy
                    descentReadoutPolicy readoutForProbeFamily installs
                    postState repairMoveRef boundaryUpdatePolicy appPolicy
                    maintenancePolicy reinstatementPolicy reclosureMoveRef
                    economy riskAdmissible acquisitionMoveRef C horizon
                    descentAttribution inventory statusPolicy residualPolicy
                    priorStatusPredicate apparatusLineagePolicy subsidyPolicy
                    scopeOwns subsidizerBudgetFeasible subsidizerMoveDescends
                    suspensionPolicy apparatusIntact operationsGatedOff
                    bindingOperationalChallenge :=
                ⟨record, hOccurrence, hStatus, hRecoverable⟩
              refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr ?_)))))
              refine ⟨hHolds, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;>
                intro hOther <;>
                rcases hOther with ⟨other, hOtherOccurrence, hOtherStatus, _hOtherCase⟩ <;>
                have hSame := hComplete.2 record other hOccurrence hOtherOccurrence <;>
                rw [hStatus, hOtherStatus] at hSame <;>
                cases hSame

theorem E5_RevivedExcludesLowerPriority
    (hRevivedEvidence :
      RevivedEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef C horizon descentAttribution
        priorStatusPredicate apparatusLineagePolicy)
    (hComplete :
      CompleteReclosureCollapseStatus S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        statusPolicy residualPolicy priorStatusPredicate apparatusLineagePolicy
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge) :
    ¬ SubsidizedHolds S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily installs postState repairMoveRef
        boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
        reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
        descentAttribution inventory statusPolicy priorStatusPredicate
        apparatusLineagePolicy subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends ∧
      ¬ SuspendedHolds S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily installs postState repairMoveRef
        boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
        reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
        descentAttribution inventory statusPolicy priorStatusPredicate
        apparatusLineagePolicy subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
        apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
      ¬ ViableHolds S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily installs postState repairMoveRef
        boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
        reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
        descentAttribution inventory statusPolicy residualPolicy
        priorStatusPredicate apparatusLineagePolicy subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
        apparatusIntact operationsGatedOff bindingOperationalChallenge ∧
      ¬ ReclosureStressedHolds S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        statusPolicy residualPolicy priorStatusPredicate apparatusLineagePolicy
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge ∧
      ¬ CollapsedIrreversibleHolds S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        statusPolicy residualPolicy priorStatusPredicate apparatusLineagePolicy
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge ∧
      ¬ CollapsedRecoverableHolds S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        statusPolicy residualPolicy priorStatusPredicate apparatusLineagePolicy
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge := by
  have hPartition :=
    E5_ReclosureCollapse S H descends probeFamilyPolicy
      descentReadoutPolicy readoutForProbeFamily installs postState
      repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
      reinstatementPolicy reclosureMoveRef economy riskAdmissible
      acquisitionMoveRef C horizon descentAttribution inventory statusPolicy
      residualPolicy priorStatusPredicate apparatusLineagePolicy subsidyPolicy
      scopeOwns subsidizerBudgetFeasible subsidizerMoveDescends
      suspensionPolicy apparatusIntact operationsGatedOff
      bindingOperationalChallenge hComplete
  rcases hPartition with hRevived | hRest
  · exact hRevived.2
  · rcases hRest with hSubsidized | hRest
    · rcases hSubsidized.1 with
        ⟨_record, _hOccurrence, _hStatus, hCase⟩
      exact (hCase.1 hRevivedEvidence).elim
    · rcases hRest with hSuspended | hRest
      · rcases hSuspended.1 with
          ⟨_record, _hOccurrence, _hStatus, hCase⟩
        exact (hCase.1 hRevivedEvidence).elim
      · rcases hRest with hViable | hRest
        · rcases hViable.1 with
            ⟨_record, _hOccurrence, _hStatus, hCase⟩
          exact (hCase.1 hRevivedEvidence).elim
        · rcases hRest with hStressed | hRest
          · rcases hStressed.1 with
              ⟨_record, _hOccurrence, _hStatus, hCase⟩
            exact (hCase.1 hRevivedEvidence).elim
          · rcases hRest with hIrreversible | hRecoverable
            · rcases hIrreversible.1 with
                ⟨_record, _hOccurrence, _hStatus, hCase⟩
              exact (hCase.1 hRevivedEvidence).elim
            · rcases hRecoverable.1 with
                ⟨_record, _hOccurrence, _hStatus, hCase⟩
              exact (hCase.1 hRevivedEvidence).elim

theorem E5_IrreversibleCollapse
    (statusRecord :
      ReclosureCollapseStatusRecord ChallengeClass Horizon LedgerEntry
        AuditRecord)
    (hOccurrence :
      ReclosureCollapseStatusOccurrenceFor S statusPolicy C horizon
        statusRecord)
    (reach : RepairGeneratorReachabilityCertified
      (ChallengeClass := ChallengeClass) (Horizon := Horizon))
    (kernel : ApparatusViabilityKernelCertified
      (ChallengeClass := ChallengeClass) (Horizon := Horizon))
    (hCollapsed : CollapsedCore (S := S) (H := H) inventory)
    (hIrreversible : IrreversibleCollapseInput C horizon reach kernel)
    (hStatus :
      statusRecord.status =
        ReclosureCollapseStatus.collapsed_irreversible)
    (hReach :
      statusRecord.reachabilityRecord = some reach.reachabilityRecord)
    (hKernel :
      statusRecord.kernelRecord = some kernel.kernelRecord)
    (hNoRescue : statusRecord.rescueMoveRecord = none)
    (hNotRevived :
      ¬ RevivedEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef C horizon descentAttribution
        priorStatusPredicate apparatusLineagePolicy)
    (hNotSubsidized :
      ¬ SubsidizedEvidenceFor S H descends probeFamilyPolicy
        descentReadoutPolicy
        readoutForProbeFamily installs postState repairMoveRef
        boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
        reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
        descentAttribution inventory subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends)
    (hNotSuspended :
      ¬ SuspendedEvidenceFor S H C horizon suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge)
    (hNotViable :
      ¬ ViableEvidenceFor S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily installs postState repairMoveRef
        boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
        reclosureMoveRef economy riskAdmissible acquisitionMoveRef C horizon
        descentAttribution inventory residualPolicy)
    (hNotStressed :
      ¬ ReclosureStressedEvidenceFor S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        residualPolicy) :
    CollapsedIrreversibleHolds S H descends probeFamilyPolicy
      descentReadoutPolicy readoutForProbeFamily installs postState
      repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
      reinstatementPolicy reclosureMoveRef economy riskAdmissible
      acquisitionMoveRef C horizon descentAttribution inventory
      statusPolicy residualPolicy priorStatusPredicate apparatusLineagePolicy
      subsidyPolicy scopeOwns subsidizerBudgetFeasible
      subsidizerMoveDescends suspensionPolicy apparatusIntact
      operationsGatedOff bindingOperationalChallenge := by
  have hCase :
      CollapsedIrreversibleCase S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        statusPolicy residualPolicy priorStatusPredicate apparatusLineagePolicy
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge statusRecord :=
    ⟨hNotRevived, hNotSubsidized, hNotSuspended, hNotViable,
      hNotStressed, hOccurrence, reach, kernel, hCollapsed,
      hIrreversible, hStatus, hReach, hKernel, hNoRescue⟩
  exact ⟨statusRecord, hOccurrence, hStatus, hCase⟩

theorem E5_SubsidyWithdrawalReclassification
    (horizonAfter : Horizon)
    (descentAttributionAfter :
      RescueMoveCreditedForDescent S H C horizonAfter
        ViabilityDescentReadoutRecord)
    (inventoryAfter :
      CompleteCollapseRescueInventory S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizonAfter descentAttributionAfter)
    (_hSubsidizedBefore :
      SubsidizedHolds S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizon descentAttribution inventory
        statusPolicy priorStatusPredicate apparatusLineagePolicy
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends)
    (subsidyWithdrawalPolicy :
      CarriedRecordPolicy S.T SubsidyWithdrawalRecord)
    (_withdrawal : SubsidyWithdrawalEvent S subsidyWithdrawalPolicy)
    (hNoActiveAfter :
      NoActiveExternalSubsidyAt (S := S) (subsidyPolicy := subsidyPolicy)
        (scopeOwns := scopeOwns) (budgetFeasible := subsidizerBudgetFeasible)
        (moveDescends := subsidizerMoveDescends) (C := C)
        (horizon := horizonAfter)
        (SelfMove :=
          CollapseRescueCandidate S H descends probeFamilyPolicy
            descentReadoutPolicy readoutForProbeFamily installs postState
            repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
            reinstatementPolicy reclosureMoveRef economy riskAdmissible
            acquisitionMoveRef C horizonAfter descentAttributionAfter)
        (selfMoveRecord := fun move =>
          CollapseRescueMoveRecord (S := S) (H := H) move) H)
    (hCompleteAfter :
      CompleteReclosureCollapseStatus S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizonAfter descentAttributionAfter
        inventoryAfter statusPolicy residualPolicy priorStatusPredicate
        apparatusLineagePolicy subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
        apparatusIntact operationsGatedOff bindingOperationalChallenge) :
    let RevivedAfter :=
      RevivedHolds S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef C horizonAfter
        descentAttributionAfter statusPolicy priorStatusPredicate
        apparatusLineagePolicy
    let SubsidizedAfter :=
      SubsidizedHolds S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily installs postState repairMoveRef
        boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
        reclosureMoveRef economy riskAdmissible acquisitionMoveRef C
        horizonAfter descentAttributionAfter inventoryAfter statusPolicy
        priorStatusPredicate apparatusLineagePolicy subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends
    let SuspendedAfter :=
      SuspendedHolds S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily installs postState repairMoveRef
        boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
        reclosureMoveRef economy riskAdmissible acquisitionMoveRef C
        horizonAfter descentAttributionAfter inventoryAfter statusPolicy
        priorStatusPredicate apparatusLineagePolicy subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
        apparatusIntact operationsGatedOff bindingOperationalChallenge
    let ViableAfter :=
      ViableHolds S H descends probeFamilyPolicy descentReadoutPolicy
        readoutForProbeFamily installs postState repairMoveRef
        boundaryUpdatePolicy appPolicy maintenancePolicy reinstatementPolicy
        reclosureMoveRef economy riskAdmissible acquisitionMoveRef C
        horizonAfter descentAttributionAfter inventoryAfter statusPolicy
        residualPolicy priorStatusPredicate apparatusLineagePolicy
        subsidyPolicy scopeOwns subsidizerBudgetFeasible
        subsidizerMoveDescends suspensionPolicy apparatusIntact
        operationsGatedOff bindingOperationalChallenge
    let StressedAfter :=
      ReclosureStressedHolds S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizonAfter descentAttributionAfter
        inventoryAfter statusPolicy residualPolicy priorStatusPredicate
        apparatusLineagePolicy subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
        apparatusIntact operationsGatedOff bindingOperationalChallenge
    let IrreversibleAfter :=
      CollapsedIrreversibleHolds S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizonAfter descentAttributionAfter
        inventoryAfter statusPolicy residualPolicy priorStatusPredicate
        apparatusLineagePolicy subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
        apparatusIntact operationsGatedOff bindingOperationalChallenge
    let RecoverableAfter :=
      CollapsedRecoverableHolds S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizonAfter descentAttributionAfter
        inventoryAfter statusPolicy residualPolicy priorStatusPredicate
        apparatusLineagePolicy subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
        apparatusIntact operationsGatedOff bindingOperationalChallenge
    ¬ SubsidizedAfter ∧
      ((RevivedAfter ∧ ¬ SuspendedAfter ∧ ¬ ViableAfter ∧
          ¬ StressedAfter ∧ ¬ IrreversibleAfter ∧
          ¬ RecoverableAfter) ∨
        (SuspendedAfter ∧ ¬ RevivedAfter ∧ ¬ ViableAfter ∧
          ¬ StressedAfter ∧ ¬ IrreversibleAfter ∧
          ¬ RecoverableAfter) ∨
        (ViableAfter ∧ ¬ RevivedAfter ∧ ¬ SuspendedAfter ∧
          ¬ StressedAfter ∧ ¬ IrreversibleAfter ∧
          ¬ RecoverableAfter) ∨
        (StressedAfter ∧ ¬ RevivedAfter ∧ ¬ SuspendedAfter ∧
          ¬ ViableAfter ∧ ¬ IrreversibleAfter ∧
          ¬ RecoverableAfter) ∨
        (IrreversibleAfter ∧ ¬ RevivedAfter ∧ ¬ SuspendedAfter ∧
          ¬ ViableAfter ∧ ¬ StressedAfter ∧ ¬ RecoverableAfter) ∨
        (RecoverableAfter ∧ ¬ RevivedAfter ∧ ¬ SuspendedAfter ∧
          ¬ ViableAfter ∧ ¬ StressedAfter ∧ ¬ IrreversibleAfter)) := by
  dsimp
  have hNotSubsidizedAfter :
      ¬ SubsidizedHolds S H descends probeFamilyPolicy
        descentReadoutPolicy readoutForProbeFamily installs postState
        repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
        reinstatementPolicy reclosureMoveRef economy riskAdmissible
        acquisitionMoveRef C horizonAfter descentAttributionAfter
        inventoryAfter statusPolicy priorStatusPredicate
        apparatusLineagePolicy subsidyPolicy scopeOwns
        subsidizerBudgetFeasible subsidizerMoveDescends := by
    intro hSubsidizedAfter
    rcases hSubsidizedAfter with
      ⟨_record, _hOccurrence, _hStatus, hCase⟩
    rcases hCase with ⟨_hNotRevived, _hOccurrenceCase, subsidy, _hEvidence⟩
    exact hNoActiveAfter ⟨subsidy, trivial⟩
  have hPartitionAfter :=
    E5_ReclosureCollapse S H descends probeFamilyPolicy
      descentReadoutPolicy readoutForProbeFamily installs postState
      repairMoveRef boundaryUpdatePolicy appPolicy maintenancePolicy
      reinstatementPolicy reclosureMoveRef economy riskAdmissible
      acquisitionMoveRef C horizonAfter descentAttributionAfter
      inventoryAfter statusPolicy residualPolicy priorStatusPredicate
      apparatusLineagePolicy subsidyPolicy scopeOwns
      subsidizerBudgetFeasible subsidizerMoveDescends suspensionPolicy
      apparatusIntact operationsGatedOff bindingOperationalChallenge
      hCompleteAfter
  constructor
  · exact hNotSubsidizedAfter
  · rcases hPartitionAfter with hRevived | hRest
    · rcases hRevived with
        ⟨hRevivedHolds, _hNotSubsidized, hNotSuspended, hNotViable,
          hNotStressed, hNotIrreversible, hNotRecoverable⟩
      exact Or.inl
        ⟨hRevivedHolds, hNotSuspended, hNotViable, hNotStressed,
          hNotIrreversible, hNotRecoverable⟩
    · rcases hRest with hSubsidized | hRest
      · exact False.elim (hNotSubsidizedAfter hSubsidized.1)
      · rcases hRest with hSuspended | hRest
        · rcases hSuspended with
            ⟨hSuspendedHolds, hNotRevived, _hNotSubsidized,
              hNotViable, hNotStressed, hNotIrreversible,
              hNotRecoverable⟩
          exact Or.inr (Or.inl
            ⟨hSuspendedHolds, hNotRevived, hNotViable,
              hNotStressed, hNotIrreversible, hNotRecoverable⟩)
        · rcases hRest with hViable | hRest
          · rcases hViable with
              ⟨hViableHolds, hNotRevived, _hNotSubsidized,
                hNotSuspended, hNotStressed, hNotIrreversible,
                hNotRecoverable⟩
            exact Or.inr (Or.inr (Or.inl
              ⟨hViableHolds, hNotRevived, hNotSuspended,
                hNotStressed, hNotIrreversible, hNotRecoverable⟩))
          · rcases hRest with hStressed | hRest
            · rcases hStressed with
                ⟨hStressedHolds, hNotRevived, _hNotSubsidized,
                  hNotSuspended, hNotViable, hNotIrreversible,
                  hNotRecoverable⟩
              exact Or.inr (Or.inr (Or.inr (Or.inl
                ⟨hStressedHolds, hNotRevived, hNotSuspended,
                  hNotViable, hNotIrreversible, hNotRecoverable⟩)))
            · rcases hRest with hIrreversible | hRecoverable
              · rcases hIrreversible with
                  ⟨hIrreversibleHolds, hNotRevived, _hNotSubsidized,
                    hNotSuspended, hNotViable, hNotStressed,
                    hNotRecoverable⟩
                exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inl
                  ⟨hIrreversibleHolds, hNotRevived, hNotSuspended,
                    hNotViable, hNotStressed, hNotRecoverable⟩))))
              · rcases hRecoverable with
                  ⟨hRecoverableHolds, hNotRevived, _hNotSubsidized,
                    hNotSuspended, hNotViable, hNotStressed,
                    hNotIrreversible⟩
                exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr
                  ⟨hRecoverableHolds, hNotRevived, hNotSuspended,
                    hNotViable, hNotStressed, hNotIrreversible⟩))))

end Theorems

end SixBirdsFoundationsV
