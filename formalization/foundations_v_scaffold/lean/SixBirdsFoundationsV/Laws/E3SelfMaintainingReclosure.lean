import SixBirdsFoundationsV.Definitional.ESystem
import SixBirdsFoundationsV.Laws.E1Internalization
import SixBirdsFoundationsV.Laws.E2BoundedReflexivity

namespace SixBirdsFoundationsV

/-!
E3 self-maintaining reclosure: the closure apparatus, maintenance operator,
reinstatement, and status apparatus from the accepted E3 six-field normal
form (`formalization/notes/examples/E3.md`), together with E3's theorems.
This file is built up across several mechanization turns; consult E3.md's
own "Setup"/"Theorem" sections for the authoritative content, not any
in-progress/left-for-later note here.
-/

structure ClosureApparatusBoundary where
  boundaryId : Nat

structure ClosureApparatusAuditData where
  auditDataId : Nat

structure ClosureApparatusRecord where
  recordId : Nat

structure ClosureApparatus
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  time : Nat
  gateInstrument :
    ActiveCarriedInstrument S.T InstrumentRecord DefectRecord MovePayload
      LedgerEntry MoveRecord AuditRecord S.moveRecordPolicy
  thresholdRecords : List InstrumentRecord
  appBoundary : ClosureApparatusBoundary
  auditData : ClosureApparatusAuditData
  apparatusRecord : ClosureApparatusRecord
  usedLedgerEntries : List LedgerEntry
  usedAuditRecords : List AuditRecord

def ClosureApparatusOccurrenceFor
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (t : Nat) (app : ClosureApparatus S) : Prop :=
  app.time = t ∧
    (∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt appPolicy app.apparatusRecord n0 sourceTag
          generatedByS inScope) ∧
    CarriedInstrument app.gateInstrument.instrumentRecordCarried
      app.gateInstrument.instrument
      app.gateInstrument.recordsAreCompleteInventory
      app.gateInstrument.visibilityRecords
      app.gateInstrument.thresholdRecords
      app.gateInstrument.checkRuleRecords ∧
    (∀ record : InstrumentRecord, record ∈ app.thresholdRecords ->
      app.gateInstrument.instrumentRecordCarried record) ∧
    (∀ entry : LedgerEntry, entry ∈ app.usedLedgerEntries ->
      entry ∈ S.Lambda_S.ledgerEntries) ∧
    ∀ auditRecord : AuditRecord, auditRecord ∈ app.usedAuditRecords ->
      HasCarriedRecordEvidence S.auditRecordPolicy auditRecord

structure MaintenanceOperatorRecord where
  recordId : Nat

structure ClosureMaintenanceOperator
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  operatorRecord : MaintenanceOperatorRecord
  apply : S.T.Z -> ClosureApparatus S
  operatorLedgerEntries : List LedgerEntry
  operatorAuditRecords : List AuditRecord

def MaintenanceOperatorOccurrenceFor
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (_t : Nat) (m : ClosureMaintenanceOperator S) : Prop :=
  (∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
    ∃ generatedByS : Bool, ∃ inScope : Bool,
      CarriedRecordAt maintenancePolicy m.operatorRecord n0 sourceTag
        generatedByS inScope ∧
      (sourceTag = FineSourceTag.committed_state ∨
        sourceTag = FineSourceTag.audited_cell_records) ∧
      generatedByS = true ∧
      inScope = true) ∧
    (∀ entry : LedgerEntry, entry ∈ m.operatorLedgerEntries ->
      entry ∈ S.Lambda_S.ledgerEntries) ∧
    ∀ auditRecord : AuditRecord, auditRecord ∈ m.operatorAuditRecords ->
      HasCarriedRecordEvidence S.auditRecordPolicy auditRecord

structure MaintenanceReinstatementRecord
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  time : Nat
  sourceState : S.T.Z
  targetState : S.T.Z
  operatorRecord : MaintenanceOperatorRecord
  preAppRecord : ClosureApparatusRecord
  postAppRecord : ClosureApparatusRecord
  outputRecord : ClosureApparatusRecord
  reinstatementLedgerEntry : LedgerEntry

def MaintenanceReinstatementFor
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (_H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (t : Nat) (app_t app_tplus1 : ClosureApparatus S)
    (m : ClosureMaintenanceOperator S)
    (record : MaintenanceReinstatementRecord S) : Prop :=
  ClosureApparatusOccurrenceFor S appPolicy t app_t ∧
    ClosureApparatusOccurrenceFor S appPolicy (t + 1) app_tplus1 ∧
    MaintenanceOperatorOccurrenceFor S maintenancePolicy t m ∧
    (∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        CarriedRecordAt reinstatementPolicy record n0 sourceTag
          generatedByS inScope ∧
        (sourceTag = FineSourceTag.committed_state ∨
          sourceTag = FineSourceTag.audited_cell_records) ∧
        generatedByS = true ∧
        inScope = true ∧
        record.time = t ∧
        record.operatorRecord = m.operatorRecord ∧
        record.preAppRecord = app_t.apparatusRecord ∧
        record.postAppRecord = app_tplus1.apparatusRecord ∧
        record.outputRecord =
          (m.apply record.sourceState).apparatusRecord ∧
        app_tplus1 = m.apply record.sourceState ∧
        app_tplus1.apparatusRecord =
          (m.apply record.sourceState).apparatusRecord ∧
        record.reinstatementLedgerEntry ∈ S.Lambda_S.ledgerEntries ∧
        S.T.suppK record.sourceState record.targetState)

/--
Certified host predicate identifying the apparatus-level defect repaired by an
E1 occurrence.  It is a predicate interface, not an asserted placeholder; later
theorems must pass a concrete instance and use its `holds` field.
-/
structure ApparatusDefectForChallenge
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (ChallengeClass : Type z) (SourceQuotient : Type z')
    (DeclaredFamily : Type z'') (TargetReadout : Type z''')
    (ObstructionWitness : Type z'''') where
  holds :
    ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
      TargetReadout ObstructionWitness DefectRecord MoveRecord
      AuditRecord ->
    ChallengeClass -> Nat -> ClosureApparatus S -> DefectRecord -> Prop

/--
Certified bridge that a repair refinement targets the concrete closure
apparatus content, not merely a bookkeeping record.
-/
structure ApparatusRepairInstalls
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (RepairRefinement : Type z) where
  holds : RepairRefinement -> ClosureApparatus S -> ClosureApparatus S -> Prop

def EndogenousRepairOccurrenceWithWitnesses
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (C : ChallengeClass) (t : Nat)
    (rho_t : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord)
    (R_t : RepairRefinement) (z z' : S.T.Z)
    (defect : DefectRecord)
    (move : RepairMove S.T MovePayload LedgerEntry MoveRecord
      S.moveRecordPolicy)
    (auditRecord : AuditRecord) : Prop :=
  ∃ episode :
      ChallengeEpisode ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness,
    episode ∈ H.episodes ∧
      rho_t ∈ H.repairAuditEntries ∧
      H.entryEpisode rho_t episode ∧
      episode.challengeClass = C ∧
      episode.time = t ∧
      RepairTypedAuditEntryCarried S rho_t ∧
      rho_t.entryClass.sourceTag = FineSourceTag.committed_state ∧
      rho_t.entryClass.generatedByS = true ∧
      rho_t.entryClass.inScope = true ∧
      move = S.R_S defect ∧
      rho_t =
        RepairTypedAuditEntry.move move.moveRecord rho_t.entryClass ∧
      ESystem.RepairStep S z z' defect auditRecord ∧
      CorePromotionGatesPass S z z' defect move auditRecord ∧
      installs.holds move.payload R_t ∧
      postState.holds z' episode

def ApparatusLevelRepairOccurrenceWithWitnesses
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (C : ChallengeClass) (t : Nat)
    (app_t app_tplus1 : ClosureApparatus S)
    (m : ClosureMaintenanceOperator S)
    (record : MaintenanceReinstatementRecord S)
    (rho_t : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord)
    (R_t : RepairRefinement) (z z' : S.T.Z)
    (defect : DefectRecord)
    (move : RepairMove S.T MovePayload LedgerEntry MoveRecord
      S.moveRecordPolicy)
    (auditRecord : AuditRecord) : Prop :=
  MaintenanceReinstatementFor S H appPolicy maintenancePolicy
      reinstatementPolicy t app_t app_tplus1 m record ∧
    EndogenousRepairOccurrenceWithWitnesses S H installs postState C t
      rho_t R_t z z' defect move auditRecord ∧
    apparatusRepair.holds R_t app_t app_tplus1 ∧
    apparatusDefect.holds H C t app_t defect

def ApparatusLevelRepairOccurrence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (C : ChallengeClass) (t : Nat)
    (app_t app_tplus1 : ClosureApparatus S)
    (m : ClosureMaintenanceOperator S)
    (record : MaintenanceReinstatementRecord S) : Prop :=
  ∃ rho_t : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord,
    ∃ R_t : RepairRefinement, ∃ z : S.T.Z, ∃ z' : S.T.Z,
      ∃ defect : DefectRecord,
        ∃ move :
          RepairMove S.T MovePayload LedgerEntry MoveRecord
            S.moveRecordPolicy,
          ∃ auditRecord : AuditRecord,
            ApparatusLevelRepairOccurrenceWithWitnesses S H appPolicy
              maintenancePolicy reinstatementPolicy installs postState
              apparatusDefect apparatusRepair C t app_t app_tplus1 m record
              rho_t R_t z z' defect move auditRecord

/--
Certified apparatus-distance interface.  E3 does not derive a canonical metric
for closure apparatus records in this setup layer.
-/
structure ClosureApparatusDistance
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  distance : ClosureApparatus S -> ClosureApparatus S -> Rat
  nonnegative :
    ∀ app app', 0 <= distance app app'
  zeroOnSameRecord :
    ∀ app app',
      app.apparatusRecord = app'.apparatusRecord ->
        distance app app' = 0

def ApproxApparatusFixedPoint
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (app_t app_tplus1 : ClosureApparatus S) : Prop :=
  distance.distance app_tplus1 app_t <= epsilon

/--
Certified measured-run predicate: no declared apparatus-binding challenge is
active at the time.
-/
structure ChallengeFreeAt (History : Type u) where
  holds : History -> Nat -> Prop

/--
Certified measured-run predicate: an apparatus-level challenge of class `C`
is active at the time.
-/
structure ClosureApparatusChallengeAt (History : Type u)
    (ChallengeClass : Type v) where
  holds : History -> ChallengeClass -> Nat -> Prop

def ApparatusMaintainedStep
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (challengeFree :
      ChallengeFreeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (challengeAt :
      ClosureApparatusChallengeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        ChallengeClass)
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat)
    (app_t app_tplus1 : ClosureApparatus S)
    (m : ClosureMaintenanceOperator S)
    (record : MaintenanceReinstatementRecord S) : Prop :=
  MaintenanceReinstatementFor S H appPolicy maintenancePolicy
      reinstatementPolicy t app_t app_tplus1 m record ∧
    ((challengeFree.holds H t ∧
        ApproxApparatusFixedPoint distance epsilon app_t app_tplus1) ∨
      (challengeAt.holds H C t ∧
        ApparatusLevelRepairOccurrence S H appPolicy maintenancePolicy
          reinstatementPolicy installs postState apparatusDefect
          apparatusRepair C t app_t app_tplus1 m record))

/--
Certified F19/F20 input: the object-level closure is a fixed point up to the
declared defect.  E3 does not mechanize F19/F20 locally.
-/
structure ObjectLevelFixedPointCertified (System : Type u)
    (History : Type v) (Horizon : Type w) where
  holds : System -> History -> Nat -> Horizon -> Prop

/--
Certified F20-style input: the object-level record coherence side is already
discharged by the host theory.
-/
structure ObjectRecordCoherenceCertified (System : Type u)
    (History : Type v) (Horizon : Type w) where
  holds : System -> History -> Nat -> Horizon -> Prop

/--
Certified measured input for the ablation/status branch: object-level
persistence may remain transiently while the closure apparatus decays.
-/
structure ObjectLevelTransientPersistence (System : Type u)
    (History : Type v) (Horizon : Type w) where
  holds : System -> History -> Nat -> Horizon -> Prop

def ApparatusLevelFixedPointMaintained
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (challengeFree :
      ChallengeFreeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (challengeAt :
      ClosureApparatusChallengeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        ChallengeClass)
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat) (_horizon : Horizon) : Prop :=
  ∃ app_t : ClosureApparatus S, ∃ app_tplus1 : ClosureApparatus S,
    ∃ m : ClosureMaintenanceOperator S,
      ∃ record : MaintenanceReinstatementRecord S,
        ApparatusMaintainedStep S H appPolicy maintenancePolicy
          reinstatementPolicy installs postState apparatusDefect
          apparatusRepair challengeFree challengeAt distance epsilon C t
          app_t app_tplus1 m record

def TwoLevelFixedPoint
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (challengeFree :
      ChallengeFreeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (challengeAt :
      ClosureApparatusChallengeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        ChallengeClass)
    (objectFixed :
      ObjectLevelFixedPointCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (objectCoherent :
      ObjectRecordCoherenceCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon) : Prop :=
  objectFixed.holds S H t horizon ∧
    objectCoherent.holds S H t horizon ∧
    ApparatusLevelFixedPointMaintained S H appPolicy maintenancePolicy
      reinstatementPolicy installs postState apparatusDefect apparatusRepair
      challengeFree challengeAt distance epsilon C t horizon

def E2AuditedRepairTriggerWitnessFor
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (C : ChallengeClass) (_horizon : Horizon) (t : Nat)
    (rho_t : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord)
    (R_t : RepairRefinement) (z z' : S.T.Z)
    (defect : DefectRecord)
    (move : RepairMove S.T MovePayload LedgerEntry MoveRecord
      S.moveRecordPolicy)
    (auditRecord : AuditRecord) : Prop :=
  ChallengedEpisodeTime H C t ∧
    EndogenousRepairOccurrence S H installs postState C t rho_t R_t ∧
    rho_t ∈ H.repairAuditEntries ∧
    move = S.R_S defect ∧
    ESystem.RepairStep S z z' defect auditRecord ∧
    CorePromotionGatesPass S z z' defect move auditRecord

/--
Certified bridge for the prose clause that the E2 tower's lower-stack audit
records cite this E3 maintenance operator and reinstatement record.  E2 tower
levels expose ledger/audit record lists but no typed field for E3 operator
records, so the cross-record citation is host-certified here.
-/
structure MaintenanceTowerAuditCitation
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  holds :
    (Nat -> Option (CarriedInstrumentLevel S)) -> Nat ->
      ClosureMaintenanceOperator S -> MaintenanceReinstatementRecord S ->
        Prop

def MaintenanceOperatorAuditedByTower
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (towerCitation : MaintenanceTowerAuditCitation S)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon)
    (m : ClosureMaintenanceOperator S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat) :
    Prop :=
  MaintenanceOperatorOccurrenceFor S maintenancePolicy t m ∧
    ∃ app_t : ClosureApparatus S,
      ∃ app_tplus1 : ClosureApparatus S,
        ∃ record : MaintenanceReinstatementRecord S,
          ∃ rho_t : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord,
            ∃ R_t : RepairRefinement, ∃ z : S.T.Z, ∃ z' : S.T.Z,
              ∃ defect : DefectRecord,
                ∃ move :
                  RepairMove S.T MovePayload LedgerEntry MoveRecord
                    S.moveRecordPolicy,
                  ∃ auditRecord : AuditRecord,
                    ∃ stack : SixBirdsIII.InstrumentStack,
                      MaintenanceReinstatementFor S H appPolicy
                          maintenancePolicy reinstatementPolicy t app_t
                          app_tplus1 m record ∧
                        ApparatusLevelRepairOccurrenceWithWitnesses S H
                          appPolicy maintenancePolicy reinstatementPolicy
                          installs postState apparatusDefect apparatusRepair C
                          t app_t app_tplus1 m record rho_t R_t z z' defect
                          move auditRecord ∧
                        E2AuditedRepairTriggerWitnessFor S H installs
                          postState C horizon t rho_t R_t z z' defect move
                          auditRecord ∧
                        FIIIInstrumentStackBridge S tower n stack ∧
                        towerCitation.holds tower n m record

def E2StatusPartitionConclusion
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
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
    (measure : AuditTowerCapacityMeasure S)
    (C : ChallengeClass)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (z : S.T.Z) (horizon : Horizon) (targetLevel : Nat) : Prop :=
  (ActiveScopedHolds S H installs postState statusPolicy claimTarget measure C
      tower n z horizon targetLevel ∧
      ¬ RotatingHolds S H installs postState statusPolicy claimTarget measure C
        tower n z horizon targetLevel ∧
      ¬ SaturatedHolds S statusPolicy claimTarget measure tower n z
        targetLevel ∧
      ¬ CircularBlockedHolds S statusPolicy claimTarget tower n z
        targetLevel) ∨
    (RotatingHolds S H installs postState statusPolicy claimTarget measure C
      tower n z horizon targetLevel ∧
      ¬ ActiveScopedHolds S H installs postState statusPolicy claimTarget
        measure C tower n z horizon targetLevel ∧
      ¬ SaturatedHolds S statusPolicy claimTarget measure tower n z
        targetLevel ∧
      ¬ CircularBlockedHolds S statusPolicy claimTarget tower n z
        targetLevel) ∨
    (SaturatedHolds S statusPolicy claimTarget measure tower n z
      targetLevel ∧
      ¬ ActiveScopedHolds S H installs postState statusPolicy claimTarget
        measure C tower n z horizon targetLevel ∧
      ¬ RotatingHolds S H installs postState statusPolicy claimTarget measure C
        tower n z horizon targetLevel ∧
      ¬ CircularBlockedHolds S statusPolicy claimTarget tower n z
        targetLevel) ∨
    (CircularBlockedHolds S statusPolicy claimTarget tower n z targetLevel ∧
      ¬ ActiveScopedHolds S H installs postState statusPolicy claimTarget
        measure C tower n z horizon targetLevel ∧
      ¬ RotatingHolds S H installs postState statusPolicy claimTarget measure C
        tower n z horizon targetLevel ∧
      ¬ SaturatedHolds S statusPolicy claimTarget measure tower n z
        targetLevel)

noncomputable def MaintenanceAuditRegressStoppedByE2
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (towerCitation : MaintenanceTowerAuditCitation S)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (measure : AuditTowerCapacityMeasure S)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon)
    (m : ClosureMaintenanceOperator S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (z : S.T.Z) (targetLevel : Nat) : Prop :=
  MaintenanceOperatorAuditedByTower S H appPolicy maintenancePolicy
      reinstatementPolicy installs postState apparatusDefect apparatusRepair
      towerCitation C t horizon m tower n ∧
    CapacityRealizableTower S tower n ∧
    TowerFootprint S measure tower n <= measure.cap z ∧
    CompleteBoundedReflexivityStatus S H installs postState statusPolicy
      claimTarget measure C tower n z horizon targetLevel ∧
    E2StatusPartitionConclusion S H installs postState statusPolicy
      claimTarget measure C tower n z horizon targetLevel ∧
    ∀ level : CarriedInstrumentLevel S,
      ∀ claim : SixBirdsIII.SameLevelSelfAuditClaim,
        level.levelIndex = targetLevel ->
          CarriedInstrumentLevelOccurrence S level ->
            SameLevelSelfAuditClaimFor S claimTarget level claim ->
              claim.hasLevelShiftBridge = false ->
                SixBirdsIII.SameLevelSelfAuditClassify claim ≠
                  SixBirdsIII.ClaimStatus.accepted

inductive ClosureMaintenanceComponent (InstrumentRecord : Type u) where
  | gateInstrument
  | thresholdRecord (record : InstrumentRecord)
  | appBoundary
  | auditData

def ClosureMaintenanceComponentRequiredFor
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (app : ClosureApparatus S) :
    ClosureMaintenanceComponent InstrumentRecord -> Prop
  | ClosureMaintenanceComponent.gateInstrument => True
  | ClosureMaintenanceComponent.thresholdRecord record =>
      record ∈ app.thresholdRecords
  | ClosureMaintenanceComponent.appBoundary => True
  | ClosureMaintenanceComponent.auditData => True

structure MaintenanceReinstatementAccountsForComponent
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  holds :
    MaintenanceReinstatementRecord S ->
      ClosureMaintenanceComponent InstrumentRecord -> Prop

structure MaintenanceReinstatementAuditHistoryMembership
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord) where
  holds : MaintenanceReinstatementRecord S -> Prop

def DeltaMaintBadSourceTag : FineSourceTag -> Prop
  | FineSourceTag.fallback => True
  | FineSourceTag.unknown => True
  | FineSourceTag.contradictory => True
  | FineSourceTag.independent_pair_witness => True
  | FineSourceTag.simulation_trace => True
  | FineSourceTag.ablation_record => True
  | FineSourceTag.committed_state => False
  | FineSourceTag.audited_cell_records => False

def Delta_maint
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership :
      MaintenanceReinstatementAuditHistoryMembership S H)
    (t : Nat) (app_t app_tplus1 : ClosureApparatus S)
    (component : ClosureMaintenanceComponent InstrumentRecord) : Prop :=
  ClosureMaintenanceComponentRequiredFor app_tplus1 component ∧
    ((∀ record : MaintenanceReinstatementRecord S,
        accounts.holds record component ->
          ¬ ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
            ∃ generatedByS : Bool, ∃ inScope : Bool,
              CarriedRecordAt reinstatementPolicy record n0 sourceTag
                generatedByS inScope) ∨
      ∃ m : ClosureMaintenanceOperator S,
        ∃ record : MaintenanceReinstatementRecord S,
          accounts.holds record component ∧
            ((∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
              ∃ generatedByS : Bool, ∃ inScope : Bool,
                CarriedRecordAt reinstatementPolicy record n0 sourceTag
                  generatedByS inScope ∧
                  (DeltaMaintBadSourceTag sourceTag ∨
                    generatedByS = false ∨ inScope = false)) ∨
              ¬ MaintenanceOperatorOccurrenceFor S maintenancePolicy t m ∨
              ¬ MaintenanceReinstatementFor S H appPolicy
                maintenancePolicy reinstatementPolicy t app_t app_tplus1 m
                record ∨
              ¬ S.T.suppK record.sourceState record.targetState ∨
              ¬ historyMembership.holds record))

def DeltaMaintEmpty
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership :
      MaintenanceReinstatementAuditHistoryMembership S H)
    (t : Nat) (app_t app_tplus1 : ClosureApparatus S) : Prop :=
  ∀ component : ClosureMaintenanceComponent InstrumentRecord,
    ¬ Delta_maint S H appPolicy maintenancePolicy reinstatementPolicy
      accounts historyMembership t app_t app_tplus1 component

structure ObjectFixedPointStatusRecord where
  recordId : Nat

structure ApparatusDistanceRecord where
  recordId : Nat

inductive MaintenanceClosureStatus where
  | crystal_grade
  | maintained_closure
  | subsidized_closure
  | decaying_closure

structure MaintenanceStatusRecord
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (Horizon : Type u') where
  time : Nat
  horizon : Horizon
  status : MaintenanceClosureStatus
  objectFixedPointRecord : ObjectFixedPointStatusRecord
  apparatusRecord : ClosureApparatusRecord
  maintenanceOperatorRecord : Option MaintenanceOperatorRecord
  reinstatementRecord : Option (MaintenanceReinstatementRecord S)
  apparatusDistanceRecord : ApparatusDistanceRecord
  supportingLedgerEntries : List LedgerEntry
  supportingAuditRecords : List AuditRecord

def MaintenanceStatusRecordCarriedAt
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {Horizon : Type u'}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (maintenanceStatusPolicy :
      CarriedRecordPolicy S.T (MaintenanceStatusRecord S Horizon))
    (record : MaintenanceStatusRecord S Horizon)
    (n0 : Nat) (sourceTag : FineSourceTag)
    (generatedByS inScope : Bool) : Prop :=
  CarriedRecordAt maintenanceStatusPolicy record n0 sourceTag generatedByS
    inScope

def MaintenanceStatusOccurrenceFor
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (_H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (maintenanceStatusPolicy :
      CarriedRecordPolicy S.T (MaintenanceStatusRecord S Horizon))
    (t : Nat) (horizon : Horizon)
    (record : MaintenanceStatusRecord S Horizon) : Prop :=
  record.time = t ∧
    record.horizon = horizon ∧
    (∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
      ∃ generatedByS : Bool, ∃ inScope : Bool,
        MaintenanceStatusRecordCarriedAt maintenanceStatusPolicy record n0
          sourceTag generatedByS inScope) ∧
    (∀ entry : LedgerEntry, entry ∈ record.supportingLedgerEntries ->
      entry ∈ S.Lambda_S.ledgerEntries) ∧
    ∀ auditRecord : AuditRecord, auditRecord ∈ record.supportingAuditRecords ->
      HasCarriedRecordEvidence S.auditRecordPolicy auditRecord

/--
Certified host predicate: the apparatus remains stable without a valid
maintenance reinstatement under the declared perturbation experiment.
-/
structure ApparatusStableWithoutMaintenance
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (History : Type z) (Horizon : Type z') where
  holds :
    History -> ClosureApparatusDistance S -> Rat -> Nat -> Horizon -> Prop

/--
Certified host predicate: the apparatus decay exceeds the declared tolerance
under the perturbation experiment.
-/
structure ApparatusDecayExceedsTolerance
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (History : Type z) (Horizon : Type z') where
  holds :
    History -> ClosureApparatusDistance S -> Rat -> Nat -> Horizon -> Prop

/--
Certified status-classifier obligation: stability-without-maintenance and
decay-exceeds-tolerance are complementary for the declared experiment.
-/
structure ApparatusStabilityComplementarity
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {History : Type z} {Horizon : Type z'}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (stable : ApparatusStableWithoutMaintenance S History Horizon)
    (decay : ApparatusDecayExceedsTolerance S History Horizon) where
  complementary :
    ∀ H distance epsilon t horizon,
      stable.holds H distance epsilon t horizon ↔
        ¬ decay.holds H distance epsilon t horizon

/--
Certified host predicate: the apparatus is reinstated by an external or
fallback carrier rather than by the genuine maintenance operator.
-/
structure ApparatusReinstatedByExternalCarrier
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (History : Type z) where
  holds : History -> Nat -> ClosureApparatus S -> ClosureApparatus S -> Prop

/--
Certified host predicate: no valid maintenance reinstatement is available for
the apparatus transition under inspection.
-/
structure NoValidMaintenanceReinstatement
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (History : Type z) where
  holds : History -> Nat -> ClosureApparatus S -> ClosureApparatus S -> Prop

/--
Certified bridge for whether an otherwise carried maintenance operator is
claiming responsibility for the apparatus at time `t`.
-/
structure MaintenanceOperatorAccountsForApparatus
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  holds : Nat -> ClosureMaintenanceOperator S -> Prop

def SubsidizedReinstatementWitness
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (t : Nat) (app_t app_tplus1 : ClosureApparatus S)
    (maybeRR : Option (MaintenanceReinstatementRecord S))
    (component : ClosureMaintenanceComponent InstrumentRecord) : Prop :=
  Delta_maint S H appPolicy maintenancePolicy reinstatementPolicy accounts
      historyMembership t app_t app_tplus1 component ∧
    ((maybeRR = none ∧
        ∀ record : MaintenanceReinstatementRecord S,
          accounts.holds record component ->
            ¬ ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
              ∃ generatedByS : Bool, ∃ inScope : Bool,
                CarriedRecordAt reinstatementPolicy record n0 sourceTag
                  generatedByS inScope) ∨
      ∃ rr : MaintenanceReinstatementRecord S,
        ∃ m : ClosureMaintenanceOperator S,
          maybeRR = some rr ∧
            accounts.holds rr component ∧
            ((∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
              ∃ generatedByS : Bool, ∃ inScope : Bool,
                CarriedRecordAt reinstatementPolicy rr n0 sourceTag
                  generatedByS inScope ∧
                  (DeltaMaintBadSourceTag sourceTag ∨
                    generatedByS = false ∨ inScope = false)) ∨
              ¬ MaintenanceOperatorOccurrenceFor S maintenancePolicy t m ∨
              ¬ MaintenanceReinstatementFor S H appPolicy
                maintenancePolicy reinstatementPolicy t app_t app_tplus1 m
                rr ∨
              ¬ S.T.suppK rr.sourceState rr.targetState ∨
              ¬ historyMembership.holds rr))

def CrystalGradeEvidence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (operatorAccounts : MaintenanceOperatorAccountsForApparatus S)
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (objectFixed :
      ObjectLevelFixedPointCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (objectCoherent :
      ObjectRecordCoherenceCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (stable :
      ApparatusStableWithoutMaintenance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (decay :
      ApparatusDecayExceedsTolerance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (_stabilityComplement :
      ApparatusStabilityComplementarity stable decay)
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (_C : ChallengeClass) (t : Nat) (horizon : Horizon) : Prop :=
  objectFixed.holds S H t horizon ∧
    objectCoherent.holds S H t horizon ∧
    (¬ ∃ m : ClosureMaintenanceOperator S,
      MaintenanceOperatorOccurrenceFor S maintenancePolicy t m ∧
        operatorAccounts.holds t m) ∧
    (¬ ∃ app_t : ClosureApparatus S,
      ∃ app_tplus1 : ClosureApparatus S,
        ∃ m : ClosureMaintenanceOperator S,
          ∃ record : MaintenanceReinstatementRecord S,
            MaintenanceReinstatementFor S H appPolicy maintenancePolicy
              reinstatementPolicy t app_t app_tplus1 m record) ∧
    (¬ ∃ app_t : ClosureApparatus S,
      ∃ app_tplus1 : ClosureApparatus S,
        ∃ maybeRR : Option (MaintenanceReinstatementRecord S),
          ∃ component : ClosureMaintenanceComponent InstrumentRecord,
            SubsidizedReinstatementWitness S H appPolicy maintenancePolicy
              reinstatementPolicy accounts historyMembership t app_t
              app_tplus1 maybeRR component) ∧
    stable.holds H distance epsilon t horizon ∧
    ¬ decay.holds H distance epsilon t horizon

def MaintainedClosureEvidence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (boundedStatusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (challengeFree :
      ChallengeFreeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (challengeAt :
      ClosureApparatusChallengeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        ChallengeClass)
    (objectFixed :
      ObjectLevelFixedPointCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (objectCoherent :
      ObjectRecordCoherenceCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (towerCitation : MaintenanceTowerAuditCitation S)
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon)
    (app_t app_tplus1 : ClosureApparatus S)
    (m : ClosureMaintenanceOperator S)
    (record : MaintenanceReinstatementRecord S) : Prop :=
  TwoLevelFixedPoint S H appPolicy maintenancePolicy reinstatementPolicy
      installs postState apparatusDefect apparatusRepair challengeFree
      challengeAt objectFixed objectCoherent distance epsilon C t horizon ∧
    ApparatusMaintainedStep S H appPolicy maintenancePolicy
      reinstatementPolicy installs postState apparatusDefect apparatusRepair
      challengeFree challengeAt distance epsilon C t app_t app_tplus1 m
      record ∧
    DeltaMaintEmpty S H appPolicy maintenancePolicy reinstatementPolicy
      accounts historyMembership t app_t app_tplus1 ∧
    (¬ ∃ bad_app_t : ClosureApparatus S,
      ∃ bad_app_tplus1 : ClosureApparatus S,
        ∃ maybeRR : Option (MaintenanceReinstatementRecord S),
          ∃ component : ClosureMaintenanceComponent InstrumentRecord,
            SubsidizedReinstatementWitness S H appPolicy maintenancePolicy
              reinstatementPolicy accounts historyMembership t bad_app_t
              bad_app_tplus1 maybeRR component) ∧
    ∀ tower : Nat -> Option (CarriedInstrumentLevel S),
      ∀ n : Nat,
        ∀ measure :
          AuditTowerCapacityMeasure.{u, v, w, x, y, y', y'', y''', y'''',
            y''''', u', _} S,
        ∀ z : S.T.Z, ∀ targetLevel : Nat,
          MaintenanceOperatorAuditedByTower S H appPolicy maintenancePolicy
              reinstatementPolicy installs postState apparatusDefect
              apparatusRepair towerCitation C t horizon m tower n ->
            MaintenanceAuditRegressStoppedByE2 S H appPolicy
              maintenancePolicy reinstatementPolicy installs postState
              apparatusDefect apparatusRepair towerCitation
              boundedStatusPolicy claimTarget measure C t horizon m
              tower n z targetLevel

def SubsidizedClosureEvidence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (boundedStatusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (challengeFree :
      ChallengeFreeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (challengeAt :
      ClosureApparatusChallengeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        ChallengeClass)
    (objectFixed :
      ObjectLevelFixedPointCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (objectCoherent :
      ObjectRecordCoherenceCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (towerCitation : MaintenanceTowerAuditCitation S)
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon)
    (app_t app_tplus1 : ClosureApparatus S)
    (maybeRR : Option (MaintenanceReinstatementRecord S))
    (component : ClosureMaintenanceComponent InstrumentRecord) : Prop :=
  objectFixed.holds S H t horizon ∧
    SubsidizedReinstatementWitness S H appPolicy maintenancePolicy
      reinstatementPolicy accounts historyMembership t app_t app_tplus1
      maybeRR component ∧
    ¬ ∃ m : ClosureMaintenanceOperator S,
      ∃ record : MaintenanceReinstatementRecord S,
        MaintainedClosureEvidence S H appPolicy maintenancePolicy
          reinstatementPolicy boundedStatusPolicy installs postState
          apparatusDefect apparatusRepair challengeFree challengeAt
          objectFixed objectCoherent accounts historyMembership towerCitation
          claimTarget distance epsilon C t horizon app_t app_tplus1 m record

def DecayingClosureEvidence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (transient :
      ObjectLevelTransientPersistence
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (stable :
      ApparatusStableWithoutMaintenance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (decay :
      ApparatusDecayExceedsTolerance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (_stabilityComplement :
      ApparatusStabilityComplementarity stable decay)
    (external :
      ApparatusReinstatedByExternalCarrier S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (noValid :
      NoValidMaintenanceReinstatement S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (_C : ChallengeClass) (t : Nat) (horizon : Horizon) : Prop :=
  transient.holds S H t horizon ∧
    (¬ ∃ app_t : ClosureApparatus S,
      ∃ app_tplus1 : ClosureApparatus S,
        ∃ m : ClosureMaintenanceOperator S,
          ∃ record : MaintenanceReinstatementRecord S,
            MaintenanceReinstatementFor S H appPolicy maintenancePolicy
              reinstatementPolicy t app_t app_tplus1 m record) ∧
    (¬ ∃ app_t : ClosureApparatus S,
      ∃ app_tplus1 : ClosureApparatus S,
        ∃ maybeRR : Option (MaintenanceReinstatementRecord S),
          ∃ component : ClosureMaintenanceComponent InstrumentRecord,
            SubsidizedReinstatementWitness S H appPolicy maintenancePolicy
              reinstatementPolicy accounts historyMembership t app_t
              app_tplus1 maybeRR component) ∧
    ∃ app_t : ClosureApparatus S,
      ∃ app_tplus1 : ClosureApparatus S,
        noValid.holds H t app_t app_tplus1 ∧
          ¬ external.holds H t app_t app_tplus1 ∧
          decay.holds H distance epsilon t horizon ∧
          ¬ stable.holds H distance epsilon t horizon

def CrystalGradeCase
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (maintenanceStatusPolicy :
      CarriedRecordPolicy S.T (MaintenanceStatusRecord S Horizon))
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (operatorAccounts : MaintenanceOperatorAccountsForApparatus S)
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (objectFixed :
      ObjectLevelFixedPointCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (objectCoherent :
      ObjectRecordCoherenceCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (stable :
      ApparatusStableWithoutMaintenance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (decay :
      ApparatusDecayExceedsTolerance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (stabilityComplement :
      ApparatusStabilityComplementarity stable decay)
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon)
    (record : MaintenanceStatusRecord S Horizon) : Prop :=
  MaintenanceStatusOccurrenceFor S H maintenanceStatusPolicy t horizon
      record ∧
    record.status = MaintenanceClosureStatus.crystal_grade ∧
    record.reinstatementRecord = none ∧
    record.maintenanceOperatorRecord = none ∧
    CrystalGradeEvidence S H appPolicy maintenancePolicy reinstatementPolicy
      operatorAccounts accounts historyMembership objectFixed objectCoherent
      stable decay stabilityComplement distance epsilon C t horizon

def MaintainedClosureCase
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (maintenanceStatusPolicy :
      CarriedRecordPolicy S.T (MaintenanceStatusRecord S Horizon))
    (boundedStatusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (challengeFree :
      ChallengeFreeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (challengeAt :
      ClosureApparatusChallengeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        ChallengeClass)
    (objectFixed :
      ObjectLevelFixedPointCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (objectCoherent :
      ObjectRecordCoherenceCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (towerCitation : MaintenanceTowerAuditCitation S)
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon)
    (record : MaintenanceStatusRecord S Horizon) : Prop :=
  MaintenanceStatusOccurrenceFor S H maintenanceStatusPolicy t horizon
      record ∧
    record.status = MaintenanceClosureStatus.maintained_closure ∧
    ∃ app_t : ClosureApparatus S,
      ∃ app_tplus1 : ClosureApparatus S,
        ∃ m : ClosureMaintenanceOperator S,
          ∃ rr : MaintenanceReinstatementRecord S,
            record.reinstatementRecord = some rr ∧
              record.maintenanceOperatorRecord = some m.operatorRecord ∧
              MaintenanceReinstatementFor S H appPolicy maintenancePolicy
                reinstatementPolicy t app_t app_tplus1 m rr ∧
              MaintainedClosureEvidence S H appPolicy maintenancePolicy
                reinstatementPolicy boundedStatusPolicy installs
                postState apparatusDefect apparatusRepair challengeFree
                challengeAt objectFixed objectCoherent accounts
                historyMembership towerCitation claimTarget distance
                epsilon C t horizon app_t app_tplus1 m rr

def SubsidizedClosureCase
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (maintenanceStatusPolicy :
      CarriedRecordPolicy S.T (MaintenanceStatusRecord S Horizon))
    (boundedStatusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (challengeFree :
      ChallengeFreeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (challengeAt :
      ClosureApparatusChallengeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        ChallengeClass)
    (objectFixed :
      ObjectLevelFixedPointCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (objectCoherent :
      ObjectRecordCoherenceCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (towerCitation : MaintenanceTowerAuditCitation S)
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon)
    (record : MaintenanceStatusRecord S Horizon) : Prop :=
  MaintenanceStatusOccurrenceFor S H maintenanceStatusPolicy t horizon
      record ∧
    record.status = MaintenanceClosureStatus.subsidized_closure ∧
    record.maintenanceOperatorRecord = none ∧
    ∃ app_t : ClosureApparatus S,
      ∃ app_tplus1 : ClosureApparatus S,
        ∃ maybeRR : Option (MaintenanceReinstatementRecord S),
          ∃ component : ClosureMaintenanceComponent InstrumentRecord,
            record.reinstatementRecord = maybeRR ∧
              Delta_maint S H appPolicy maintenancePolicy
                reinstatementPolicy accounts historyMembership t app_t
                app_tplus1 component ∧
              SubsidizedClosureEvidence S H appPolicy maintenancePolicy
                reinstatementPolicy boundedStatusPolicy installs
                postState apparatusDefect apparatusRepair challengeFree
                challengeAt objectFixed objectCoherent accounts
                historyMembership towerCitation claimTarget distance
                epsilon C t horizon app_t app_tplus1 maybeRR component

def DecayingClosureCase
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (maintenanceStatusPolicy :
      CarriedRecordPolicy S.T (MaintenanceStatusRecord S Horizon))
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (transient :
      ObjectLevelTransientPersistence
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (stable :
      ApparatusStableWithoutMaintenance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (decay :
      ApparatusDecayExceedsTolerance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (stabilityComplement :
      ApparatusStabilityComplementarity stable decay)
    (external :
      ApparatusReinstatedByExternalCarrier S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (noValid :
      NoValidMaintenanceReinstatement S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon)
    (record : MaintenanceStatusRecord S Horizon) : Prop :=
  MaintenanceStatusOccurrenceFor S H maintenanceStatusPolicy t horizon
      record ∧
    record.status = MaintenanceClosureStatus.decaying_closure ∧
    record.reinstatementRecord = none ∧
    record.maintenanceOperatorRecord = none ∧
    DecayingClosureEvidence S H appPolicy maintenancePolicy
      reinstatementPolicy accounts historyMembership transient stable decay
      stabilityComplement external noValid distance epsilon C t horizon

def CrystalGradeHolds
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (maintenanceStatusPolicy :
      CarriedRecordPolicy S.T (MaintenanceStatusRecord S Horizon))
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (operatorAccounts : MaintenanceOperatorAccountsForApparatus S)
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (objectFixed :
      ObjectLevelFixedPointCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (objectCoherent :
      ObjectRecordCoherenceCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (stable :
      ApparatusStableWithoutMaintenance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (decay :
      ApparatusDecayExceedsTolerance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (stabilityComplement :
      ApparatusStabilityComplementarity stable decay)
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon) : Prop :=
  ∃ record : MaintenanceStatusRecord S Horizon,
    CrystalGradeCase S H maintenanceStatusPolicy appPolicy maintenancePolicy
      reinstatementPolicy operatorAccounts accounts historyMembership
      objectFixed objectCoherent stable decay stabilityComplement distance
      epsilon C t horizon record

def MaintainedClosureHolds
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (maintenanceStatusPolicy :
      CarriedRecordPolicy S.T (MaintenanceStatusRecord S Horizon))
    (boundedStatusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (challengeFree :
      ChallengeFreeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (challengeAt :
      ClosureApparatusChallengeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        ChallengeClass)
    (objectFixed :
      ObjectLevelFixedPointCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (objectCoherent :
      ObjectRecordCoherenceCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (towerCitation : MaintenanceTowerAuditCitation S)
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon) : Prop :=
  ∃ record : MaintenanceStatusRecord S Horizon,
    MaintainedClosureCase S H maintenanceStatusPolicy boundedStatusPolicy
      appPolicy
      maintenancePolicy reinstatementPolicy installs postState
      apparatusDefect apparatusRepair challengeFree challengeAt objectFixed
      objectCoherent accounts historyMembership towerCitation claimTarget
      distance epsilon C t horizon record

def SubsidizedClosureHolds
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (maintenanceStatusPolicy :
      CarriedRecordPolicy S.T (MaintenanceStatusRecord S Horizon))
    (boundedStatusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (challengeFree :
      ChallengeFreeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (challengeAt :
      ClosureApparatusChallengeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        ChallengeClass)
    (objectFixed :
      ObjectLevelFixedPointCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (objectCoherent :
      ObjectRecordCoherenceCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (towerCitation : MaintenanceTowerAuditCitation S)
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon) : Prop :=
  ∃ record : MaintenanceStatusRecord S Horizon,
    SubsidizedClosureCase S H maintenanceStatusPolicy boundedStatusPolicy
      appPolicy
      maintenancePolicy reinstatementPolicy installs postState
      apparatusDefect apparatusRepair challengeFree challengeAt objectFixed
      objectCoherent accounts historyMembership towerCitation claimTarget
      distance epsilon C t horizon record

def DecayingClosureHolds
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (maintenanceStatusPolicy :
      CarriedRecordPolicy S.T (MaintenanceStatusRecord S Horizon))
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (transient :
      ObjectLevelTransientPersistence
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (stable :
      ApparatusStableWithoutMaintenance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (decay :
      ApparatusDecayExceedsTolerance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (stabilityComplement :
      ApparatusStabilityComplementarity stable decay)
    (external :
      ApparatusReinstatedByExternalCarrier S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (noValid :
      NoValidMaintenanceReinstatement S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon) : Prop :=
  ∃ record : MaintenanceStatusRecord S Horizon,
    DecayingClosureCase S H maintenanceStatusPolicy appPolicy
      maintenancePolicy reinstatementPolicy accounts historyMembership
      transient stable decay stabilityComplement external noValid distance
      epsilon C t horizon record

def CompleteMaintenanceStatus
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (maintenanceStatusPolicy :
      CarriedRecordPolicy S.T (MaintenanceStatusRecord S Horizon))
    (boundedStatusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (challengeFree :
      ChallengeFreeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (challengeAt :
      ClosureApparatusChallengeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        ChallengeClass)
    (operatorAccounts : MaintenanceOperatorAccountsForApparatus S)
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (objectFixed :
      ObjectLevelFixedPointCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (objectCoherent :
      ObjectRecordCoherenceCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (transient :
      ObjectLevelTransientPersistence
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (stable :
      ApparatusStableWithoutMaintenance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (decay :
      ApparatusDecayExceedsTolerance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (stabilityComplement :
      ApparatusStabilityComplementarity stable decay)
    (external :
      ApparatusReinstatedByExternalCarrier S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (noValid :
      NoValidMaintenanceReinstatement S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (towerCitation : MaintenanceTowerAuditCitation S)
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon) : Prop :=
  (∃ record : MaintenanceStatusRecord S Horizon,
    MaintenanceStatusOccurrenceFor S H maintenanceStatusPolicy t horizon
      record ∧
      (CrystalGradeCase S H maintenanceStatusPolicy appPolicy
          maintenancePolicy reinstatementPolicy operatorAccounts accounts
          historyMembership objectFixed objectCoherent stable decay
          stabilityComplement distance epsilon C t horizon record ∨
        MaintainedClosureCase S H maintenanceStatusPolicy boundedStatusPolicy
          appPolicy
          maintenancePolicy reinstatementPolicy installs postState
          apparatusDefect apparatusRepair challengeFree challengeAt
          objectFixed objectCoherent accounts historyMembership
          towerCitation claimTarget distance epsilon C t horizon record ∨
        SubsidizedClosureCase S H maintenanceStatusPolicy boundedStatusPolicy
          appPolicy
          maintenancePolicy reinstatementPolicy installs postState
          apparatusDefect apparatusRepair challengeFree challengeAt
          objectFixed objectCoherent accounts historyMembership
          towerCitation claimTarget distance epsilon C t horizon record ∨
        DecayingClosureCase S H maintenanceStatusPolicy appPolicy
          maintenancePolicy reinstatementPolicy accounts historyMembership
          transient stable decay stabilityComplement external noValid
          distance epsilon C t horizon record)) ∧
    ∀ record1 record2 : MaintenanceStatusRecord S Horizon,
      MaintenanceStatusOccurrenceFor S H maintenanceStatusPolicy t horizon
        record1 ->
      MaintenanceStatusOccurrenceFor S H maintenanceStatusPolicy t horizon
        record2 ->
      record1.status = record2.status

theorem E3_TwoLevelFixedPoint
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (maintenanceStatusPolicy :
      CarriedRecordPolicy S.T (MaintenanceStatusRecord S Horizon))
    (boundedStatusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (challengeFree :
      ChallengeFreeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (challengeAt :
      ClosureApparatusChallengeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        ChallengeClass)
    (objectFixed :
      ObjectLevelFixedPointCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (objectCoherent :
      ObjectRecordCoherenceCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (towerCitation : MaintenanceTowerAuditCitation S)
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon)
    (app_t app_tplus1 : ClosureApparatus S)
    (m : ClosureMaintenanceOperator S)
    (record : MaintenanceReinstatementRecord S)
    (statusRecord : MaintenanceStatusRecord S Horizon)
    (hObjectFixed : objectFixed.holds S H t horizon)
    (hObjectCoherent : objectCoherent.holds S H t horizon)
    (_hAppOccurrence :
      ClosureApparatusOccurrenceFor S appPolicy t app_t)
    (_hOperator :
      MaintenanceOperatorOccurrenceFor S maintenancePolicy t m)
    (hReinstatement :
      MaintenanceReinstatementFor S H appPolicy maintenancePolicy
        reinstatementPolicy t app_t app_tplus1 m record)
    (hMaintainedStep :
      ApparatusMaintainedStep S H appPolicy maintenancePolicy
        reinstatementPolicy installs postState apparatusDefect apparatusRepair
        challengeFree challengeAt distance epsilon C t app_t app_tplus1 m
        record)
    (hDeltaEmpty :
      DeltaMaintEmpty S H appPolicy maintenancePolicy reinstatementPolicy
        accounts historyMembership t app_t app_tplus1)
    (hStatusOccurrence :
      MaintenanceStatusOccurrenceFor S H maintenanceStatusPolicy t horizon
        statusRecord)
    (hStatusTag :
      statusRecord.status = MaintenanceClosureStatus.maintained_closure)
    (hStatusReinstatement :
      statusRecord.reinstatementRecord = some record)
    (hStatusOperator :
      statusRecord.maintenanceOperatorRecord = some m.operatorRecord)
    (hNoSubsidized :
      ¬ ∃ bad_app_t : ClosureApparatus S,
        ∃ bad_app_tplus1 : ClosureApparatus S,
          ∃ maybeRR : Option (MaintenanceReinstatementRecord S),
            ∃ component : ClosureMaintenanceComponent InstrumentRecord,
              SubsidizedReinstatementWitness S H appPolicy maintenancePolicy
                reinstatementPolicy accounts historyMembership t bad_app_t
                bad_app_tplus1 maybeRR component)
    (hRegressStopIfAudited :
      ∀ tower : Nat -> Option (CarriedInstrumentLevel S),
        ∀ n : Nat,
          ∀ measure :
            AuditTowerCapacityMeasure.{u, v, w, x, y, y', y'', y''', y'''',
              y''''', u', _} S,
          ∀ z : S.T.Z, ∀ targetLevel : Nat,
            MaintenanceOperatorAuditedByTower S H appPolicy maintenancePolicy
                reinstatementPolicy installs postState apparatusDefect
                apparatusRepair towerCitation C t horizon m tower n ->
              MaintenanceAuditRegressStoppedByE2 S H appPolicy
                maintenancePolicy reinstatementPolicy installs postState
                apparatusDefect apparatusRepair towerCitation
                boundedStatusPolicy claimTarget measure C t horizon m tower n
                z targetLevel) :
    TwoLevelFixedPoint S H appPolicy maintenancePolicy reinstatementPolicy
        installs postState apparatusDefect apparatusRepair challengeFree
        challengeAt objectFixed objectCoherent distance epsilon C t horizon ∧
      MaintainedClosureHolds S H maintenanceStatusPolicy boundedStatusPolicy
        appPolicy maintenancePolicy reinstatementPolicy installs postState
        apparatusDefect apparatusRepair challengeFree challengeAt objectFixed
        objectCoherent accounts historyMembership towerCitation claimTarget
        distance epsilon C t horizon := by
  have hTwoLevel :
      TwoLevelFixedPoint S H appPolicy maintenancePolicy reinstatementPolicy
        installs postState apparatusDefect apparatusRepair challengeFree
        challengeAt objectFixed objectCoherent distance epsilon C t horizon :=
    ⟨hObjectFixed, hObjectCoherent,
      ⟨app_t, app_tplus1, m, record, hMaintainedStep⟩⟩
  refine ⟨hTwoLevel, ?_⟩
  refine ⟨statusRecord, ?_⟩
  refine ⟨hStatusOccurrence, hStatusTag, app_t, app_tplus1, m, record,
    hStatusReinstatement, hStatusOperator, hReinstatement, ?_⟩
  exact ⟨hTwoLevel, hMaintainedStep, hDeltaEmpty, hNoSubsidized,
    hRegressStopIfAudited⟩

theorem E3_StatusPartition
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (maintenanceStatusPolicy :
      CarriedRecordPolicy S.T (MaintenanceStatusRecord S Horizon))
    (boundedStatusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (challengeFree :
      ChallengeFreeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (challengeAt :
      ClosureApparatusChallengeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        ChallengeClass)
    (operatorAccounts : MaintenanceOperatorAccountsForApparatus S)
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (objectFixed :
      ObjectLevelFixedPointCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (objectCoherent :
      ObjectRecordCoherenceCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (transient :
      ObjectLevelTransientPersistence
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (stable :
      ApparatusStableWithoutMaintenance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (decay :
      ApparatusDecayExceedsTolerance S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (stabilityComplement :
      ApparatusStabilityComplementarity stable decay)
    (external :
      ApparatusReinstatedByExternalCarrier S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (noValid :
      NoValidMaintenanceReinstatement S
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (towerCitation : MaintenanceTowerAuditCitation S)
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (distance : ClosureApparatusDistance S) (epsilon : Rat)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon)
    (hComplete :
      CompleteMaintenanceStatus S H maintenanceStatusPolicy
        boundedStatusPolicy appPolicy maintenancePolicy reinstatementPolicy
        installs postState apparatusDefect apparatusRepair challengeFree
        challengeAt operatorAccounts accounts historyMembership objectFixed
        objectCoherent transient stable decay stabilityComplement external
        noValid towerCitation claimTarget distance epsilon C t horizon) :
    (CrystalGradeHolds S H maintenanceStatusPolicy appPolicy
        maintenancePolicy reinstatementPolicy operatorAccounts accounts
        historyMembership objectFixed objectCoherent stable decay
        stabilityComplement distance epsilon C t horizon ∧
        ¬ MaintainedClosureHolds S H maintenanceStatusPolicy
          boundedStatusPolicy appPolicy maintenancePolicy reinstatementPolicy
          installs postState apparatusDefect apparatusRepair challengeFree
          challengeAt objectFixed objectCoherent accounts historyMembership
          towerCitation claimTarget distance epsilon C t horizon ∧
        ¬ SubsidizedClosureHolds S H maintenanceStatusPolicy
          boundedStatusPolicy appPolicy maintenancePolicy reinstatementPolicy
          installs postState apparatusDefect apparatusRepair challengeFree
          challengeAt objectFixed objectCoherent accounts historyMembership
          towerCitation claimTarget distance epsilon C t horizon ∧
        ¬ DecayingClosureHolds S H maintenanceStatusPolicy appPolicy
          maintenancePolicy reinstatementPolicy accounts historyMembership
          transient stable decay stabilityComplement external noValid distance
          epsilon C t horizon) ∨
      (MaintainedClosureHolds S H maintenanceStatusPolicy boundedStatusPolicy
        appPolicy maintenancePolicy reinstatementPolicy installs postState
        apparatusDefect apparatusRepair challengeFree challengeAt objectFixed
        objectCoherent accounts historyMembership towerCitation claimTarget
        distance epsilon C t horizon ∧
        ¬ CrystalGradeHolds S H maintenanceStatusPolicy appPolicy
          maintenancePolicy reinstatementPolicy operatorAccounts accounts
          historyMembership objectFixed objectCoherent stable decay
          stabilityComplement distance epsilon C t horizon ∧
        ¬ SubsidizedClosureHolds S H maintenanceStatusPolicy
          boundedStatusPolicy appPolicy maintenancePolicy reinstatementPolicy
          installs postState apparatusDefect apparatusRepair challengeFree
          challengeAt objectFixed objectCoherent accounts historyMembership
          towerCitation claimTarget distance epsilon C t horizon ∧
        ¬ DecayingClosureHolds S H maintenanceStatusPolicy appPolicy
          maintenancePolicy reinstatementPolicy accounts historyMembership
          transient stable decay stabilityComplement external noValid distance
          epsilon C t horizon) ∨
      (SubsidizedClosureHolds S H maintenanceStatusPolicy boundedStatusPolicy
        appPolicy maintenancePolicy reinstatementPolicy installs postState
        apparatusDefect apparatusRepair challengeFree challengeAt objectFixed
        objectCoherent accounts historyMembership towerCitation claimTarget
        distance epsilon C t horizon ∧
        ¬ CrystalGradeHolds S H maintenanceStatusPolicy appPolicy
          maintenancePolicy reinstatementPolicy operatorAccounts accounts
          historyMembership objectFixed objectCoherent stable decay
          stabilityComplement distance epsilon C t horizon ∧
        ¬ MaintainedClosureHolds S H maintenanceStatusPolicy
          boundedStatusPolicy appPolicy maintenancePolicy reinstatementPolicy
          installs postState apparatusDefect apparatusRepair challengeFree
          challengeAt objectFixed objectCoherent accounts historyMembership
          towerCitation claimTarget distance epsilon C t horizon ∧
        ¬ DecayingClosureHolds S H maintenanceStatusPolicy appPolicy
          maintenancePolicy reinstatementPolicy accounts historyMembership
          transient stable decay stabilityComplement external noValid distance
          epsilon C t horizon) ∨
      (DecayingClosureHolds S H maintenanceStatusPolicy appPolicy
        maintenancePolicy reinstatementPolicy accounts historyMembership
        transient stable decay stabilityComplement external noValid distance
        epsilon C t horizon ∧
        ¬ CrystalGradeHolds S H maintenanceStatusPolicy appPolicy
          maintenancePolicy reinstatementPolicy operatorAccounts accounts
          historyMembership objectFixed objectCoherent stable decay
          stabilityComplement distance epsilon C t horizon ∧
        ¬ MaintainedClosureHolds S H maintenanceStatusPolicy
          boundedStatusPolicy appPolicy maintenancePolicy reinstatementPolicy
          installs postState apparatusDefect apparatusRepair challengeFree
          challengeAt objectFixed objectCoherent accounts historyMembership
          towerCitation claimTarget distance epsilon C t horizon ∧
        ¬ SubsidizedClosureHolds S H maintenanceStatusPolicy
          boundedStatusPolicy appPolicy maintenancePolicy reinstatementPolicy
          installs postState apparatusDefect apparatusRepair challengeFree
          challengeAt objectFixed objectCoherent accounts historyMembership
          towerCitation claimTarget distance epsilon C t horizon) := by
  let hUnique := hComplete.2
  rcases hComplete.1 with ⟨record, _hOccurrence, hBranch⟩
  rcases hBranch with hCrystalCase | hRest
  · have hCrystal :
        CrystalGradeHolds S H maintenanceStatusPolicy appPolicy
          maintenancePolicy reinstatementPolicy operatorAccounts accounts
          historyMembership objectFixed objectCoherent stable decay
          stabilityComplement distance epsilon C t horizon :=
      ⟨record, hCrystalCase⟩
    have hStatus :
        record.status = MaintenanceClosureStatus.crystal_grade :=
      hCrystalCase.2.1
    have hNotMaintained :
        ¬ MaintainedClosureHolds S H maintenanceStatusPolicy
          boundedStatusPolicy appPolicy maintenancePolicy reinstatementPolicy
          installs postState apparatusDefect apparatusRepair challengeFree
          challengeAt objectFixed objectCoherent accounts historyMembership
          towerCitation claimTarget distance epsilon C t horizon := by
      intro hOther
      rcases hOther with ⟨other, hOtherCase⟩
      have hsame := hUnique record other hCrystalCase.1 hOtherCase.1
      rw [hStatus, hOtherCase.2.1] at hsame
      cases hsame
    have hNotSubsidized :
        ¬ SubsidizedClosureHolds S H maintenanceStatusPolicy
          boundedStatusPolicy appPolicy maintenancePolicy reinstatementPolicy
          installs postState apparatusDefect apparatusRepair challengeFree
          challengeAt objectFixed objectCoherent accounts historyMembership
          towerCitation claimTarget distance epsilon C t horizon := by
      intro hOther
      rcases hOther with ⟨other, hOtherCase⟩
      have hsame := hUnique record other hCrystalCase.1 hOtherCase.1
      rw [hStatus, hOtherCase.2.1] at hsame
      cases hsame
    have hNotDecaying :
        ¬ DecayingClosureHolds S H maintenanceStatusPolicy appPolicy
          maintenancePolicy reinstatementPolicy accounts historyMembership
          transient stable decay stabilityComplement external noValid distance
          epsilon C t horizon := by
      intro hOther
      rcases hOther with ⟨other, hOtherCase⟩
      have hsame := hUnique record other hCrystalCase.1 hOtherCase.1
      rw [hStatus, hOtherCase.2.1] at hsame
      cases hsame
    exact Or.inl ⟨hCrystal, hNotMaintained, hNotSubsidized, hNotDecaying⟩
  · rcases hRest with hMaintainedCase | hRest
    · have hMaintained :
          MaintainedClosureHolds S H maintenanceStatusPolicy
            boundedStatusPolicy appPolicy maintenancePolicy reinstatementPolicy
            installs postState apparatusDefect apparatusRepair challengeFree
            challengeAt objectFixed objectCoherent accounts historyMembership
            towerCitation claimTarget distance epsilon C t horizon :=
        ⟨record, hMaintainedCase⟩
      have hStatus :
          record.status = MaintenanceClosureStatus.maintained_closure :=
        hMaintainedCase.2.1
      have hNotCrystal :
          ¬ CrystalGradeHolds S H maintenanceStatusPolicy appPolicy
            maintenancePolicy reinstatementPolicy operatorAccounts accounts
            historyMembership objectFixed objectCoherent stable decay
            stabilityComplement distance epsilon C t horizon := by
        intro hOther
        rcases hOther with ⟨other, hOtherCase⟩
        have hsame := hUnique record other hMaintainedCase.1 hOtherCase.1
        rw [hStatus, hOtherCase.2.1] at hsame
        cases hsame
      have hNotSubsidized :
          ¬ SubsidizedClosureHolds S H maintenanceStatusPolicy
            boundedStatusPolicy appPolicy maintenancePolicy
            reinstatementPolicy installs postState apparatusDefect
            apparatusRepair challengeFree challengeAt objectFixed
            objectCoherent accounts historyMembership towerCitation
            claimTarget distance epsilon C t horizon := by
        intro hOther
        rcases hOther with ⟨other, hOtherCase⟩
        have hsame := hUnique record other hMaintainedCase.1 hOtherCase.1
        rw [hStatus, hOtherCase.2.1] at hsame
        cases hsame
      have hNotDecaying :
          ¬ DecayingClosureHolds S H maintenanceStatusPolicy appPolicy
            maintenancePolicy reinstatementPolicy accounts historyMembership
            transient stable decay stabilityComplement external noValid
            distance epsilon C t horizon := by
        intro hOther
        rcases hOther with ⟨other, hOtherCase⟩
        have hsame := hUnique record other hMaintainedCase.1 hOtherCase.1
        rw [hStatus, hOtherCase.2.1] at hsame
        cases hsame
      exact
        Or.inr
          (Or.inl ⟨hMaintained, hNotCrystal, hNotSubsidized,
            hNotDecaying⟩)
    · rcases hRest with hSubsidizedCase | hDecayingCase
      · have hSubsidized :
            SubsidizedClosureHolds S H maintenanceStatusPolicy
              boundedStatusPolicy appPolicy maintenancePolicy
              reinstatementPolicy installs postState apparatusDefect
              apparatusRepair challengeFree challengeAt objectFixed
              objectCoherent accounts historyMembership towerCitation
              claimTarget distance epsilon C t horizon :=
          ⟨record, hSubsidizedCase⟩
        have hStatus :
            record.status = MaintenanceClosureStatus.subsidized_closure :=
          hSubsidizedCase.2.1
        have hNotCrystal :
            ¬ CrystalGradeHolds S H maintenanceStatusPolicy appPolicy
              maintenancePolicy reinstatementPolicy operatorAccounts accounts
              historyMembership objectFixed objectCoherent stable decay
              stabilityComplement distance epsilon C t horizon := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hSubsidizedCase.1
            hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        have hNotMaintained :
            ¬ MaintainedClosureHolds S H maintenanceStatusPolicy
              boundedStatusPolicy appPolicy maintenancePolicy
              reinstatementPolicy installs postState apparatusDefect
              apparatusRepair challengeFree challengeAt objectFixed
              objectCoherent accounts historyMembership towerCitation
              claimTarget distance epsilon C t horizon := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hSubsidizedCase.1
            hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        have hNotDecaying :
            ¬ DecayingClosureHolds S H maintenanceStatusPolicy appPolicy
              maintenancePolicy reinstatementPolicy accounts historyMembership
              transient stable decay stabilityComplement external noValid
              distance epsilon C t horizon := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hSubsidizedCase.1
            hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        exact
          Or.inr
            (Or.inr
              (Or.inl
                ⟨hSubsidized, hNotCrystal, hNotMaintained,
                  hNotDecaying⟩))
      · have hDecaying :
            DecayingClosureHolds S H maintenanceStatusPolicy appPolicy
              maintenancePolicy reinstatementPolicy accounts historyMembership
              transient stable decay stabilityComplement external noValid
              distance epsilon C t horizon :=
          ⟨record, hDecayingCase⟩
        have hStatus :
            record.status = MaintenanceClosureStatus.decaying_closure :=
          hDecayingCase.2.1
        have hNotCrystal :
            ¬ CrystalGradeHolds S H maintenanceStatusPolicy appPolicy
              maintenancePolicy reinstatementPolicy operatorAccounts accounts
              historyMembership objectFixed objectCoherent stable decay
              stabilityComplement distance epsilon C t horizon := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hDecayingCase.1 hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        have hNotMaintained :
            ¬ MaintainedClosureHolds S H maintenanceStatusPolicy
              boundedStatusPolicy appPolicy maintenancePolicy
              reinstatementPolicy installs postState apparatusDefect
              apparatusRepair challengeFree challengeAt objectFixed
              objectCoherent accounts historyMembership towerCitation
              claimTarget distance epsilon C t horizon := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hDecayingCase.1 hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        have hNotSubsidized :
            ¬ SubsidizedClosureHolds S H maintenanceStatusPolicy
              boundedStatusPolicy appPolicy maintenancePolicy
              reinstatementPolicy installs postState apparatusDefect
              apparatusRepair challengeFree challengeAt objectFixed
              objectCoherent accounts historyMembership towerCitation
              claimTarget distance epsilon C t horizon := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hDecayingCase.1 hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        exact
          Or.inr
            (Or.inr
              (Or.inr
                ⟨hDecaying, hNotCrystal, hNotMaintained,
                  hNotSubsidized⟩))

theorem E3_RegressStoppedByE2
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (towerCitation : MaintenanceTowerAuditCitation S)
    (boundedStatusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (measure : AuditTowerCapacityMeasure S)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon)
    (m : ClosureMaintenanceOperator S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (z : S.T.Z) (targetLevel : Nat)
    (_hOperator :
      MaintenanceOperatorOccurrenceFor S maintenancePolicy t m)
    (hAudited :
      MaintenanceOperatorAuditedByTower S H appPolicy maintenancePolicy
        reinstatementPolicy installs postState apparatusDefect apparatusRepair
        towerCitation C t horizon m tower n)
    (hRealizable : CapacityRealizableTower S tower n)
    (_hAdmissible : CapacityAdmissible S measure tower n z)
    (hComplete :
      CompleteBoundedReflexivityStatus S H installs postState
        boundedStatusPolicy claimTarget measure C tower n z horizon
        targetLevel) :
    MaintenanceAuditRegressStoppedByE2 S H appPolicy maintenancePolicy
        reinstatementPolicy installs postState apparatusDefect apparatusRepair
        towerCitation boundedStatusPolicy claimTarget measure C t horizon m
        tower n z targetLevel ∧
      TowerFootprint S measure tower n <= measure.cap z ∧
      E2StatusPartitionConclusion S H installs postState boundedStatusPolicy
        claimTarget measure C tower n z horizon targetLevel ∧
      (∀ level : CarriedInstrumentLevel S,
        ∀ claim : SixBirdsIII.SameLevelSelfAuditClaim,
          level.levelIndex = targetLevel ->
            CarriedInstrumentLevelOccurrence S level ->
              SameLevelSelfAuditClaimFor S claimTarget level claim ->
                claim.hasLevelShiftBridge = false ->
                  SixBirdsIII.SameLevelSelfAuditClassify claim ≠
                    SixBirdsIII.ClaimStatus.accepted) := by
  have hBound :
      TowerFootprint S measure tower n <= measure.cap z :=
    E2_CapacityBound S measure tower n z hRealizable
  have hStatus :
      E2StatusPartitionConclusion S H installs postState boundedStatusPolicy
        claimTarget measure C tower n z horizon targetLevel :=
    E2_StatusPartition S H installs postState boundedStatusPolicy claimTarget
      measure C tower n z horizon targetLevel hComplete
  have hNoSelfSoundness :
      ∀ level : CarriedInstrumentLevel S,
        ∀ claim : SixBirdsIII.SameLevelSelfAuditClaim,
          level.levelIndex = targetLevel ->
            CarriedInstrumentLevelOccurrence S level ->
              SameLevelSelfAuditClaimFor S claimTarget level claim ->
                claim.hasLevelShiftBridge = false ->
                  SixBirdsIII.SameLevelSelfAuditClassify claim ≠
                    SixBirdsIII.ClaimStatus.accepted := by
    intro level claim _hIndex hLevel hClaim hNoShift
    exact E2_SelfSoundnessObstruction S claimTarget level claim hLevel
      hClaim hNoShift
  have hRegress :
      MaintenanceAuditRegressStoppedByE2 S H appPolicy maintenancePolicy
        reinstatementPolicy installs postState apparatusDefect apparatusRepair
        towerCitation boundedStatusPolicy claimTarget measure C t horizon m
        tower n z targetLevel :=
    ⟨hAudited, hRealizable, hBound, hComplete, hStatus,
      hNoSelfSoundness⟩
  exact ⟨hRegress, hBound, hStatus, hNoSelfSoundness⟩

/--
A measured decay curve sampled over experiment time.  The toy-lab instantiates
this by exact `Fraction` sequences; Lean keeps only the mathematical readout.
-/
structure MeasuredCurve where
  value : Nat -> Rat

/--
Certified measured-run predicate: the maintenance channel is actually ablated
over the declared horizon.
-/
structure MaintenanceChannelAblated {System : Type u} {History : Type v}
    (S : System) (H : History) (Horizon : Type w) where
  holds : Nat -> Horizon -> Prop

/--
Certified measured-run predicate: the run genuinely exposes the closure
apparatus to sustained perturbation over the declared horizon.
-/
structure PersistentPerturbationExposure {System : Type u} {History : Type v}
    (S : System) (H : History) (Horizon : Type w) where
  holds : Nat -> Horizon -> Prop

/--
Certified measured-run extractor for the object-level decay curve.  E3 does
not mechanize a universal F19/F20 curve construction.
-/
structure ObjectDecayCurve {System : Type u} {History : Type v}
    (S : System) (H : History) (Horizon : Type w) where
  curve : Nat -> Horizon -> MeasuredCurve

/--
Certified measured-run extractor for the apparatus-level decay curve.  Concrete
instances are supplied by the toy-lab/host experiment.
-/
structure ApparatusDecayCurve {System : Type u} {History : Type v}
    (S : System) (H : History) (Horizon : Type w) where
  curve : Nat -> Horizon -> MeasuredCurve

/--
Concrete curve-separation criterion: at some experiment time the apparatus
curve exceeds its tolerance while the object curve remains within tolerance.
-/
def CurvesSeparate (apparatusCurve objectCurve : MeasuredCurve)
    (epsilonApp epsilonObj : Rat) : Prop :=
  ∃ time : Nat,
    apparatusCurve.value time > epsilonApp ∧
      objectCurve.value time <= epsilonObj

/--
Certified causal bridge for E3's ablation falsifier.  The implication from a
maintained-closure occurrence plus an actually ablated, persistently perturbed
run to separated measured curves is empirical/measured-run content.  The Round
B toy-lab supplies concrete grounding for specific instances; Lean records the
normal form under this certified bridge.
-/
structure AblationSeparationCertified {System : Type u} {History : Type v}
    (S : System) (H : History) (Horizon : Type w) where
  holds :
    (t : Nat) -> (horizon : Horizon) -> (maintainedClosure : Prop) ->
      (channel : MaintenanceChannelAblated S H Horizon) ->
        (exposure : PersistentPerturbationExposure S H Horizon) ->
          (apparatusCurve : ApparatusDecayCurve S H Horizon) ->
            (objectCurve : ObjectDecayCurve S H Horizon) ->
              (epsilonApp epsilonObj : Rat) ->
                maintainedClosure ->
                  channel.holds t horizon ->
                    exposure.holds t horizon ->
                      CurvesSeparate
                        (apparatusCurve.curve t horizon)
                        (objectCurve.curve t horizon)
                        epsilonApp epsilonObj

theorem E3_AblationSeparation
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u'}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (maintenanceStatusPolicy :
      CarriedRecordPolicy S.T (MaintenanceStatusRecord S Horizon))
    (boundedStatusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusDefect :
      ApparatusDefectForChallenge S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (apparatusRepair : ApparatusRepairInstalls S RepairRefinement)
    (challengeFree :
      ChallengeFreeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord))
    (challengeAt :
      ClosureApparatusChallengeAt
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        ChallengeClass)
    (objectFixed :
      ObjectLevelFixedPointCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (objectCoherent :
      ObjectRecordCoherenceCertified
        (ESystem FData RuleFamily ResidualFamily AuditAccessData
          InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
          AuditRecord)
        (ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
          TargetReadout ObstructionWitness DefectRecord MoveRecord
          AuditRecord)
        Horizon)
    (accounts : MaintenanceReinstatementAccountsForComponent S)
    (historyMembership : MaintenanceReinstatementAuditHistoryMembership S H)
    (towerCitation : MaintenanceTowerAuditCitation S)
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (distance : ClosureApparatusDistance S)
    (channel :
      MaintenanceChannelAblated S H Horizon)
    (exposure :
      PersistentPerturbationExposure S H Horizon)
    (objectCurve :
      ObjectDecayCurve S H Horizon)
    (apparatusCurve :
      ApparatusDecayCurve S H Horizon)
    (ablationCertified :
      AblationSeparationCertified S H Horizon)
    (C : ChallengeClass) (t : Nat) (horizon : Horizon)
    (epsilonApp epsilonObj : Rat) :
    MaintainedClosureHolds S H maintenanceStatusPolicy boundedStatusPolicy
        appPolicy maintenancePolicy reinstatementPolicy installs postState
        apparatusDefect apparatusRepair challengeFree challengeAt
        objectFixed objectCoherent accounts historyMembership towerCitation
        claimTarget distance epsilonApp C t horizon ∧
      channel.holds t horizon ∧
      exposure.holds t horizon ->
    CurvesSeparate (apparatusCurve.curve t horizon)
      (objectCurve.curve t horizon) epsilonApp epsilonObj := by
  intro h
  exact
    ablationCertified.holds t horizon
      (MaintainedClosureHolds S H maintenanceStatusPolicy
        boundedStatusPolicy appPolicy maintenancePolicy reinstatementPolicy
        installs postState apparatusDefect apparatusRepair challengeFree
        challengeAt objectFixed objectCoherent accounts historyMembership
        towerCitation claimTarget distance epsilonApp C t horizon)
      channel exposure apparatusCurve objectCurve epsilonApp epsilonObj
      h.1 h.2.1 h.2.2

end SixBirdsFoundationsV
