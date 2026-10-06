import SixBirdsFoundationsV.Definitional.ESystem
import SixBirdsFoundationsV.Laws.E1Internalization
import SixBirdsIII.InstrumentClaims
import SixBirdsIII.RotatingAudit

namespace SixBirdsFoundationsV

/-!
E2 bounded reflexivity setup.

This setup layer bridges D4 carried instruments and E1 audited repair
occurrences to the vendored FIII self-audit and rotating-audit vocabulary.  It
also introduces the Foundations-V-local carried-record capacity interface used
by E2's later counting theorem.

The four-way per-level status apparatus and E2 theorem statements are
intentionally left to later mechanization subsections.
-/

structure CarriedInstrumentLevel
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  levelIndex : Nat
  levelTag : Nat
  instrument :
    ActiveCarriedInstrument S.T InstrumentRecord DefectRecord MovePayload
      LedgerEntry MoveRecord AuditRecord S.moveRecordPolicy
  levelRecord : InstrumentRecord
  auditsLowerStack : List Nat -> Prop
  lowerStackTarget : List Nat
  usedLedgerEntries : List LedgerEntry
  usedAuditRecords : List AuditRecord

def CarriedInstrumentLevelOccurrence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (level : CarriedInstrumentLevel S) : Prop :=
  level.instrument.instrumentRecordCarried level.levelRecord ∧
    CarriedInstrument level.instrument.instrumentRecordCarried
      level.instrument.instrument
      level.instrument.recordsAreCompleteInventory
      level.instrument.visibilityRecords
      level.instrument.thresholdRecords
      level.instrument.checkRuleRecords ∧
    S.I_S.instrumentRecordCarried level.levelRecord ∧
    (∀ entry : LedgerEntry, entry ∈ level.usedLedgerEntries ->
      entry ∈ S.Lambda_S.ledgerEntries) ∧
    (∀ auditRecord : AuditRecord, auditRecord ∈ level.usedAuditRecords ->
      HasCarriedRecordEvidence S.auditRecordPolicy auditRecord) ∧
    ∀ lower : Nat, lower ∈ level.lowerStackTarget ->
      lower < level.levelIndex

/--
Certified bridge tying a carried instrument level to the FIII boolean
self-audit claim being classified.  FIII supplies the classifier theorem; E2
only records that this carried claim targets same-level `Sound(I)`.
-/
structure SameLevelSelfAuditClaimTarget
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  targetsSound :
    CarriedInstrumentLevel S ->
      SixBirdsIII.SameLevelSelfAuditClaim -> Prop

def SameLevelSelfAuditClaimFor
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (target : SameLevelSelfAuditClaimTarget S)
    (level : CarriedInstrumentLevel S)
    (claim : SixBirdsIII.SameLevelSelfAuditClaim) : Prop :=
  CarriedInstrumentLevelOccurrence S level ∧
    target.targetsSound level claim

def AuditedRepairTrigger
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
    (C : ChallengeClass) (_horizon : Horizon) : Prop :=
  ∃ t : Nat, ∃ rho_t :
    RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord,
      ∃ R_t : RepairRefinement,
        ChallengedEpisodeTime H C t ∧
          EndogenousRepairOccurrence S H installs postState C t rho_t R_t ∧
          rho_t ∈ H.repairAuditEntries ∧
          ∃ z : S.T.Z, ∃ z' : S.T.Z,
            ∃ defect : DefectRecord,
              ∃ move :
                RepairMove S.T MovePayload LedgerEntry MoveRecord
                  S.moveRecordPolicy,
                ∃ auditRecord : AuditRecord,
                  move = S.R_S defect ∧
                    ESystem.RepairStep S z z' defect auditRecord ∧
                    CorePromotionGatesPass S z z' defect move auditRecord

def TowerLevel
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (tower : Nat -> Option (CarriedInstrumentLevel S))
    (n k : Nat) (level : CarriedInstrumentLevel S) : Prop :=
  k < n ∧ tower k = some level ∧
    CarriedInstrumentLevelOccurrence S level ∧
    level.levelIndex = k

def StrictlyIncreasingLevelTags
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat) :
    Prop :=
  ∀ i j : Nat, ∀ level_i level_j : CarriedInstrumentLevel S,
    TowerLevel S tower n i level_i ->
      TowerLevel S tower n j level_j ->
        i < j -> level_i.levelTag < level_j.levelTag

def EachLevelAuditsLowerStack
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat) :
    Prop :=
  ∀ k : Nat, ∀ level : CarriedInstrumentLevel S,
    TowerLevel S tower n k level ->
      0 < k ->
        level.auditsLowerStack (List.range k) ∧
          level.lowerStackTarget = List.range k

def CompleteCarriedInstrumentTower
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat) :
    Prop :=
  ∀ level : CarriedInstrumentLevel S,
    CarriedInstrumentLevelOccurrence S level ->
      level.levelIndex < n ->
        ∃ k : Nat, TowerLevel S tower n k level

def FIIIInstrumentStackBridge
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (stack : SixBirdsIII.InstrumentStack) : Prop :=
  CompleteCarriedInstrumentTower S tower n ∧
    stack.length = n ∧
    stack.finiteRecords = true ∧
    stack.admissibleLowerStack = true ∧
    stack.strictlyIncreasingLevels = true

def CarriedRotatingExtensionRealized
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (stack : SixBirdsIII.InstrumentStack)
    (ext : SixBirdsIII.RotatingAuditExtension)
    (nextLevel : CarriedInstrumentLevel S) : Prop :=
  FIIIInstrumentStackBridge S tower n stack ∧
    ext.lower = stack ∧
    ext.extensionInstrumentPresent = true ∧
    ext.extensionLevelHigher = true ∧
    ext.bridgeAdmissible = true ∧
    ext.reportAccepted = true ∧
    ext.selfSoundnessAccepted = false ∧
    CarriedInstrumentLevelOccurrence S nextLevel ∧
    nextLevel.levelIndex = n ∧
    (∀ k : Nat, ∀ level : CarriedInstrumentLevel S,
      TowerLevel S tower n k level ->
        level.levelTag < nextLevel.levelTag) ∧
    nextLevel.auditsLowerStack (List.range n) ∧
    nextLevel.lowerStackTarget = List.range n

structure FiniteRecordSet (RecordId : Type u) where
  records : List RecordId
  nodup : records.Nodup

def FiniteRecordSet.card {RecordId : Type u}
    (set : FiniteRecordSet RecordId) : Nat :=
  set.records.length

def FiniteRecordSet.Subset {RecordId : Type u}
    (left right : FiniteRecordSet RecordId) : Prop :=
  ∀ record : RecordId, record ∈ left.records -> record ∈ right.records

def FiniteRecordSet.Disjoint {RecordId : Type u}
    (left right : FiniteRecordSet RecordId) : Prop :=
  ∀ record : RecordId, record ∈ left.records -> record ∈ right.records ->
    False

/--
Certified carried-capacity interface for E2.  The fields expose finite record
sets and the structural subset/disjointness facts used by the later counting
theorem; they do not assume the theorem's capacity inequality.
-/
structure AuditTowerCapacityMeasure
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  RecordId : Type u'
  instrumentRecordId : InstrumentRecord -> RecordId
  ledgerEntryId : LedgerEntry -> RecordId
  auditRecordId : AuditRecord -> RecordId
  instrumentRecordId_injective :
    ∀ left right : InstrumentRecord,
      instrumentRecordId left = instrumentRecordId right -> left = right
  ledgerEntryId_injective :
    ∀ left right : LedgerEntry,
      ledgerEntryId left = ledgerEntryId right -> left = right
  auditRecordId_injective :
    ∀ left right : AuditRecord,
      auditRecordId left = auditRecordId right -> left = right
  instrumentLedgerIds_disjoint :
    ∀ instrumentRecord : InstrumentRecord, ∀ ledgerEntry : LedgerEntry,
      instrumentRecordId instrumentRecord ≠ ledgerEntryId ledgerEntry
  instrumentAuditIds_disjoint :
    ∀ instrumentRecord : InstrumentRecord, ∀ auditRecord : AuditRecord,
      instrumentRecordId instrumentRecord ≠ auditRecordId auditRecord
  ledgerAuditIds_disjoint :
    ∀ ledgerEntry : LedgerEntry, ∀ auditRecord : AuditRecord,
      ledgerEntryId ledgerEntry ≠ auditRecordId auditRecord
  carrierRecordUniverse : S.T.Z -> FiniteRecordSet RecordId
  cap : S.T.Z -> Nat
  capIsUniverseCard :
    ∀ z : S.T.Z, (carrierRecordUniverse z).card = cap z
  levelRecordSet : CarriedInstrumentLevel S -> FiniteRecordSet RecordId
  footprint : CarriedInstrumentLevel S -> Nat
  footprintIsCard :
    ∀ level : CarriedInstrumentLevel S,
      CarriedInstrumentLevelOccurrence S level ->
        footprint level = (levelRecordSet level).card
  countsOnlyCarriedRecords :
    ∀ level : CarriedInstrumentLevel S,
      CarriedInstrumentLevelOccurrence S level ->
        ∀ recordId : RecordId,
          recordId ∈ (levelRecordSet level).records ↔
            recordId = instrumentRecordId level.levelRecord ∨
              (∃ record : InstrumentRecord,
                record ∈ level.instrument.visibilityRecords ∧
                  recordId = instrumentRecordId record) ∨
              (∃ record : InstrumentRecord,
                record ∈ level.instrument.thresholdRecords ∧
                  recordId = instrumentRecordId record) ∨
              (∃ checkRule : CheckRuleRecord InstrumentRecord,
                checkRule ∈ level.instrument.checkRuleRecords ∧
                  recordId = instrumentRecordId checkRule.record) ∨
              (∃ entry : LedgerEntry,
                entry ∈ level.usedLedgerEntries ∧
                  recordId = ledgerEntryId entry) ∨
              (∃ auditRecord : AuditRecord,
                auditRecord ∈ level.usedAuditRecords ∧
                  recordId = auditRecordId auditRecord)
  levelRecordsWithinCarrier :
    ∀ z : S.T.Z, ∀ level : CarriedInstrumentLevel S,
      CarriedInstrumentLevelOccurrence S level ->
        FiniteRecordSet.Subset (levelRecordSet level)
          (carrierRecordUniverse z)
  disjointAcrossLevels :
    ∀ level1 level2 : CarriedInstrumentLevel S,
      CarriedInstrumentLevelOccurrence S level1 ->
        CarriedInstrumentLevelOccurrence S level2 ->
          level1.levelIndex ≠ level2.levelIndex ->
            FiniteRecordSet.Disjoint (levelRecordSet level1)
              (levelRecordSet level2)
  positiveFootprint :
    ∀ level : CarriedInstrumentLevel S,
      CarriedInstrumentLevelOccurrence S level -> footprint level > 0

def TowerExtend
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (nextLevel : CarriedInstrumentLevel S) :
    Nat -> Option (CarriedInstrumentLevel S) :=
  fun k => if k = n then some nextLevel else tower k

noncomputable def TowerFootprint
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat) : Nat :=
  by
    classical
    exact
      (List.range n).foldl
        (fun total k =>
          match tower k with
          | none => total
          | some level =>
              if TowerLevel S tower n k level then
                total + measure.footprint level
              else
                total)
        0

def CapacityAdmissible
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (z : S.T.Z) : Prop :=
  TowerFootprint S measure tower n <= measure.cap z

def CapacityRealizableTower
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat) :
    Prop :=
  CompleteCarriedInstrumentTower S tower n ∧
    StrictlyIncreasingLevelTags S tower n ∧
    EachLevelAuditsLowerStack S tower n

def CapacitySaturated
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (z : S.T.Z) : Prop :=
  CapacityRealizableTower S tower n ∧
    CapacityAdmissible S measure tower n z ∧
    ∀ nextLevel : CarriedInstrumentLevel S,
      CarriedInstrumentLevelOccurrence S nextLevel ->
        nextLevel.levelIndex = n ->
          measure.footprint nextLevel > 0 ->
            ¬ CapacityAdmissible S measure
              (TowerExtend tower n nextLevel) (n + 1) z

inductive BoundedReflexivityStatus where
  | active_scoped
  | rotating
  | saturated
  | circular_blocked

structure BoundedReflexivityStatusRecord
    (InstrumentRecord : Type u) (LedgerEntry : Type v) where
  levelIndex : Nat
  levelTag : Nat
  status : BoundedReflexivityStatus
  claim : Option SixBirdsIII.SameLevelSelfAuditClaim
  stack : Option SixBirdsIII.InstrumentStack
  capacityFootprint : Nat
  supportingLevelRecords : List InstrumentRecord
  supportingLedgerEntries : List LedgerEntry

def BoundedReflexivityStatusRecordCarriedAt
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (record : BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry)
    (n0 : Nat) (sourceTag : FineSourceTag)
    (generatedByS inScope : Bool) : Prop :=
  CarriedRecordAt statusPolicy record n0 sourceTag generatedByS inScope

def BoundedReflexivityStatusOccurrenceFor
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (_z : S.T.Z) (targetLevel : Nat)
    (record : BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry) :
    Prop :=
  (∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
    ∃ generatedByS : Bool, ∃ inScope : Bool,
      BoundedReflexivityStatusRecordCarriedAt statusPolicy record n0
        sourceTag generatedByS inScope) ∧
    targetLevel < n ∧
    record.levelIndex = targetLevel ∧
    record.levelIndex < n ∧
    ∃ level : CarriedInstrumentLevel S,
      TowerLevel S tower n record.levelIndex level ∧
        record.levelTag = level.levelTag ∧
        (∀ support : InstrumentRecord,
          support ∈ record.supportingLevelRecords ->
            level.instrument.instrumentRecordCarried support) ∧
        ∀ entry : LedgerEntry,
          entry ∈ record.supportingLedgerEntries ->
            entry ∈ S.Lambda_S.ledgerEntries

def CircularBlockAtLevel
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (record : BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry) :
    Prop :=
  ∃ level : CarriedInstrumentLevel S,
    ∃ claim : SixBirdsIII.SameLevelSelfAuditClaim,
      TowerLevel S tower n record.levelIndex level ∧
        record.claim = some claim ∧
        SameLevelSelfAuditClaimFor S claimTarget level claim ∧
        claim.hasLevelShiftBridge = false ∧
        SixBirdsIII.SameLevelSelfAuditClassify claim ≠
          SixBirdsIII.ClaimStatus.accepted

def NoCircularBlockAtLevel
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (record : BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry) :
    Prop :=
  ¬ CircularBlockAtLevel S claimTarget tower n record

def ActiveScopedEvidence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u1}
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
    (z : S.T.Z) (horizon : Horizon) (targetLevel : Nat)
    (record : BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry) :
    Prop :=
  BoundedReflexivityStatusOccurrenceFor S statusPolicy tower n z
      targetLevel record ∧
    record.status = BoundedReflexivityStatus.active_scoped ∧
    NoCircularBlockAtLevel S claimTarget tower n record ∧
    (∃ claim : SixBirdsIII.SameLevelSelfAuditClaim,
      record.claim = some claim ∧
        claim.inClaimTypes = true ∧
        claim.selfDependent = false) ∧
    record.capacityFootprint = TowerFootprint S measure tower n ∧
    CapacityAdmissible S measure tower n z ∧
    ¬ CapacitySaturated S measure tower n z ∧
    ¬ AuditedRepairTrigger S H installs postState C horizon

def RotatingEvidence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u1}
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
    (z : S.T.Z) (horizon : Horizon) (targetLevel : Nat)
    (record : BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry) :
    Prop :=
  BoundedReflexivityStatusOccurrenceFor S statusPolicy tower n z
      targetLevel record ∧
    record.status = BoundedReflexivityStatus.rotating ∧
    NoCircularBlockAtLevel S claimTarget tower n record ∧
    AuditedRepairTrigger S H installs postState C horizon ∧
    ¬ CapacitySaturated S measure tower n z ∧
    ∃ stack : SixBirdsIII.InstrumentStack,
      ∃ ext : SixBirdsIII.RotatingAuditExtension,
        ∃ nextLevel : CarriedInstrumentLevel S,
          record.stack = some stack ∧
            record.capacityFootprint = TowerFootprint S measure tower n ∧
            FIIIInstrumentStackBridge S tower n stack ∧
            stack.finiteRecords = true ∧
            stack.admissibleLowerStack = true ∧
            stack.strictlyIncreasingLevels = true ∧
            CarriedRotatingExtensionRealized S tower n stack ext
              nextLevel

def SaturatedEvidence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (z : S.T.Z) (targetLevel : Nat)
    (record : BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry) :
    Prop :=
  BoundedReflexivityStatusOccurrenceFor S statusPolicy tower n z
      targetLevel record ∧
    record.status = BoundedReflexivityStatus.saturated ∧
    NoCircularBlockAtLevel S claimTarget tower n record ∧
    record.capacityFootprint = TowerFootprint S measure tower n ∧
    CapacitySaturated S measure tower n z

def CircularBlockedEvidence
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (z : S.T.Z) (targetLevel : Nat)
    (record : BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry) :
    Prop :=
  BoundedReflexivityStatusOccurrenceFor S statusPolicy tower n z
      targetLevel record ∧
    record.status = BoundedReflexivityStatus.circular_blocked ∧
    CircularBlockAtLevel S claimTarget tower n record

def ActiveScopedHolds
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u1}
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
  ∃ record : BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry,
    ActiveScopedEvidence S H installs postState statusPolicy claimTarget
      measure C tower n z horizon targetLevel record

def RotatingHolds
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u1}
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
  ∃ record : BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry,
    RotatingEvidence S H installs postState statusPolicy claimTarget
      measure C tower n z horizon targetLevel record

def SaturatedHolds
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (z : S.T.Z) (targetLevel : Nat) : Prop :=
  ∃ record : BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry,
    SaturatedEvidence S statusPolicy claimTarget measure tower n z
      targetLevel record

def CircularBlockedHolds
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry))
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (z : S.T.Z) (targetLevel : Nat) : Prop :=
  ∃ record : BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry,
    CircularBlockedEvidence S statusPolicy claimTarget tower n z
      targetLevel record

def CompleteBoundedReflexivityStatus
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u1}
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
  (∃ record : BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry,
    BoundedReflexivityStatusOccurrenceFor S statusPolicy tower n z
      targetLevel record ∧
      (ActiveScopedEvidence S H installs postState statusPolicy claimTarget
          measure C tower n z horizon targetLevel record ∨
        RotatingEvidence S H installs postState statusPolicy claimTarget
          measure C tower n z horizon targetLevel record ∨
        SaturatedEvidence S statusPolicy claimTarget measure tower n z
          targetLevel record ∨
        CircularBlockedEvidence S statusPolicy claimTarget tower n z
          targetLevel record)) ∧
    ∀ record1 record2 :
      BoundedReflexivityStatusRecord InstrumentRecord LedgerEntry,
      BoundedReflexivityStatusOccurrenceFor S statusPolicy tower n z
        targetLevel record1 ->
      BoundedReflexivityStatusOccurrenceFor S statusPolicy tower n z
        targetLevel record2 ->
      record1.status = record2.status

theorem E2_SelfSoundnessObstruction
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (claimTarget : SameLevelSelfAuditClaimTarget S)
    (level : CarriedInstrumentLevel S)
    (claim : SixBirdsIII.SameLevelSelfAuditClaim)
    (_hLevel : CarriedInstrumentLevelOccurrence S level)
    (_hClaim : SameLevelSelfAuditClaimFor S claimTarget level claim)
    (hNoShift : claim.hasLevelShiftBridge = false) :
    SixBirdsIII.SameLevelSelfAuditClassify claim ≠
      SixBirdsIII.ClaimStatus.accepted :=
  SixBirdsIII.same_level_self_audit_failure claim hNoShift

/--
Certified host bridge for the residual carried-level fields that are not
entailed by capacity openness alone.  Once non-saturation yields a carried
positive-footprint candidate at index `n`, this predicate supplies the fresh
level's tag ordering and lower-stack audit fields.
-/
def FreshRotatingLevelBridge
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat) :
    Prop :=
  ∀ nextLevel : CarriedInstrumentLevel S,
    CarriedInstrumentLevelOccurrence S nextLevel ->
      nextLevel.levelIndex = n ->
        (∀ k : Nat, ∀ level : CarriedInstrumentLevel S,
          TowerLevel S tower n k level ->
            level.levelTag < nextLevel.levelTag) ∧
          nextLevel.auditsLowerStack (List.range n) ∧
          nextLevel.lowerStackTarget = List.range n

theorem E2_ForcedStratification
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u1}
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
    (measure : AuditTowerCapacityMeasure S)
    (C : ChallengeClass)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (z : S.T.Z) (horizon : Horizon)
    (stack : SixBirdsIII.InstrumentStack)
    (_hTrigger : AuditedRepairTrigger S H installs postState C horizon)
    (hBridge : FIIIInstrumentStackBridge S tower n stack)
    (hFinite : stack.finiteRecords = true)
    (hAdmissible : stack.admissibleLowerStack = true)
    (hLevels : stack.strictlyIncreasingLevels = true)
    (hRealizable : CapacityRealizableTower S tower n)
    (hCurrentAdmissible : CapacityAdmissible S measure tower n z)
    (hNotSaturated : ¬ CapacitySaturated S measure tower n z)
    (hFreshBridge : FreshRotatingLevelBridge S tower n) :
    ∃ ext : SixBirdsIII.RotatingAuditExtension,
      ∃ nextLevel : CarriedInstrumentLevel S,
        CarriedRotatingExtensionRealized S tower n stack ext nextLevel ∧
          ext.extensionLevelHigher = true ∧
          ext.bridgeAdmissible = true ∧
          ext.reportAccepted = true ∧
          (ext.complianceAccepted = true ↔
            ext.stackDefectEmpty = true) ∧
          ext.selfSoundnessAccepted = false := by
  rcases SixBirdsIII.finite_rotating_audit stack hFinite hAdmissible
      hLevels with
    ⟨ext, hLower, hExtensionPresent, hHigher, hBridgeAdmissible,
      hReport, hCompliance, hSelfSoundness⟩
  have hCandidate :
      ∃ nextLevel : CarriedInstrumentLevel S,
        CarriedInstrumentLevelOccurrence S nextLevel ∧
          nextLevel.levelIndex = n ∧
          measure.footprint nextLevel > 0 ∧
          CapacityAdmissible S measure
            (TowerExtend tower n nextLevel) (n + 1) z := by
    exact Classical.byContradiction (fun hNoCandidate =>
      hNotSaturated
        ⟨hRealizable, hCurrentAdmissible, by
          intro nextLevel hNextOccurrence hNextIndex hNextPositive
          intro hExtendedAdmissible
          exact hNoCandidate
            ⟨nextLevel, hNextOccurrence, hNextIndex, hNextPositive,
              hExtendedAdmissible⟩⟩)
  rcases hCandidate with
    ⟨nextLevel, hNextOccurrence, hNextIndex, _hNextPositive,
      _hExtendedAdmissible⟩
  rcases hFreshBridge nextLevel hNextOccurrence hNextIndex with
    ⟨hNextTags, hNextAudits, hNextTarget⟩
  refine ⟨ext, nextLevel, ?_, hHigher, hBridgeAdmissible, hReport,
    hCompliance, hSelfSoundness⟩
  exact
    ⟨hBridge, hLower, hExtensionPresent, hHigher, hBridgeAdmissible,
      hReport, hSelfSoundness, hNextOccurrence, hNextIndex, hNextTags,
      hNextAudits, hNextTarget⟩

theorem list_length_le_of_nodup_subset {α : Type u}
    (xs ys : List α) (hxs : xs.Nodup) (hys : ys.Nodup)
    (hsub : ∀ a : α, a ∈ xs -> a ∈ ys) : xs.length <= ys.length := by
  classical
  induction xs generalizing ys with
  | nil => simp
  | cons a xs ih =>
      have hxsParts := List.nodup_cons.mp hxs
      have hnotMem : a ∉ xs := hxsParts.1
      have hxsNodup : xs.Nodup := hxsParts.2
      have hay : a ∈ ys := hsub a (by simp)
      let p : α -> Bool := fun b => decide (b = a)
      let ys' := ys.eraseP p
      have hysNodup' : ys'.Nodup := List.Nodup.eraseP p hys
      have hsub' : ∀ b : α, b ∈ xs -> b ∈ ys' := by
        intro b hb
        have hby : b ∈ ys := hsub b (by simp [hb])
        have hbne : b ≠ a := by
          intro heq
          apply hnotMem
          simpa [heq] using hb
        have hpneg : ¬ p b := by
          simp [p, hbne]
        exact (List.mem_eraseP_of_neg (l := ys) hpneg).2 hby
      have ihle : xs.length <= ys'.length :=
        ih ys' hxsNodup hysNodup' hsub'
      have hlenErase : ys'.length = ys.length - 1 := by
        exact List.length_eraseP_of_mem (p := p) hay (by simp [p])
      have hysPos : 0 < ys.length := List.length_pos_of_mem hay
      simp only [List.length_cons]
      omega

noncomputable def TowerSlotRecords
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n k : Nat) :
    List measure.RecordId :=
  by
    classical
    exact
      match tower k with
      | none => []
      | some level =>
          if TowerLevel S tower n k level then
            (measure.levelRecordSet level).records
          else
            []

noncomputable def TowerSlotFootprint
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n k : Nat) :
    Nat :=
  by
    classical
    exact
      match tower k with
      | none => 0
      | some level =>
          if TowerLevel S tower n k level then
            measure.footprint level
          else
            0

noncomputable def TowerRecordListForSlots
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    : List Nat -> List measure.RecordId
  | [] => []
  | k :: rest =>
      TowerSlotRecords S measure tower n k ++
        TowerRecordListForSlots S measure tower n rest

theorem TowerSlotFootprint_eq_records_length
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n k : Nat) :
    TowerSlotFootprint S measure tower n k =
      (TowerSlotRecords S measure tower n k).length := by
  classical
  unfold TowerSlotFootprint TowerSlotRecords
  cases hslot : tower k with
  | none => simp
  | some level =>
      by_cases hlevel : TowerLevel S tower n k level
      · have hOcc : CarriedInstrumentLevelOccurrence S level :=
          hlevel.2.2.1
        simp [hlevel, measure.footprintIsCard level hOcc,
          FiniteRecordSet.card]
      · simp [hlevel]

theorem mem_TowerRecordListForSlots
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (slots : List Nat) (record : measure.RecordId) :
    record ∈ TowerRecordListForSlots S measure tower n slots ↔
      ∃ k : Nat, k ∈ slots ∧
        ∃ level : CarriedInstrumentLevel S,
          tower k = some level ∧
            TowerLevel S tower n k level ∧
            record ∈ (measure.levelRecordSet level).records := by
  classical
  induction slots with
  | nil =>
      simp [TowerRecordListForSlots]
  | cons k rest ih =>
      simp only [TowerRecordListForSlots, List.mem_append, ih,
        List.mem_cons]
      unfold TowerSlotRecords
      cases hslot : tower k with
      | none =>
          simp [hslot]
      | some level =>
          by_cases hlevel : TowerLevel S tower n k level
          · simp [hslot, hlevel]
          · simp [hslot, hlevel]

theorem TowerRecordListForSlots_subset_carrier
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (z : S.T.Z) (slots : List Nat) :
    ∀ record : measure.RecordId,
      record ∈ TowerRecordListForSlots S measure tower n slots ->
        record ∈ (measure.carrierRecordUniverse z).records := by
  intro record hmem
  have hmem' :=
    (mem_TowerRecordListForSlots S measure tower n slots record).1 hmem
  rcases hmem' with
    ⟨_k, _hk, level, _hslot, hlevel, hrecord⟩
  exact measure.levelRecordsWithinCarrier z level hlevel.2.2.1 record
    hrecord

theorem TowerRecordListForSlots_nodup
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (slots : List Nat) (hslots : slots.Nodup) :
    (TowerRecordListForSlots S measure tower n slots).Nodup := by
  classical
  induction slots with
  | nil =>
      simp [TowerRecordListForSlots]
  | cons k rest ih =>
      have hparts := List.nodup_cons.mp hslots
      have hnotRest : k ∉ rest := hparts.1
      have hrestNodup : rest.Nodup := hparts.2
      cases hslot : tower k with
      | none =>
          simp [TowerRecordListForSlots, TowerSlotRecords, hslot,
            ih hrestNodup]
      | some level =>
          by_cases hlevel : TowerLevel S tower n k level
          · rw [TowerRecordListForSlots]
            unfold TowerSlotRecords
            simp [hslot, hlevel]
            apply List.nodup_append.mpr
            refine ⟨(measure.levelRecordSet level).nodup,
              ih hrestNodup, ?_⟩
            intro left hleft right hright heq
            have hright' :=
              (mem_TowerRecordListForSlots S measure tower n rest right).1
                hright
            rcases hright' with
              ⟨j, hj, level_j, _hslot_j, hlevel_j, hrightSet⟩
            have hIndexNe :
                level.levelIndex ≠ level_j.levelIndex := by
              intro hsame
              have hkj : k = j := by
                calc
                  k = level.levelIndex := hlevel.2.2.2.symm
                  _ = level_j.levelIndex := hsame
                  _ = j := hlevel_j.2.2.2
              exact hnotRest (by simpa [hkj] using hj)
            exact measure.disjointAcrossLevels level level_j hlevel.2.2.1
              hlevel_j.2.2.1 hIndexNe left hleft
              (by simpa [heq] using hrightSet)
          · simp [TowerRecordListForSlots, TowerSlotRecords, hslot,
              hlevel, ih hrestNodup]

def ListNatSumBy (f : Nat -> Nat) : List Nat -> Nat
  | [] => 0
  | k :: rest => f k + ListNatSumBy f rest

theorem foldl_add_eq_init_add_ListNatSumBy (f : Nat -> Nat) :
    ∀ slots : List Nat, ∀ init : Nat,
      slots.foldl (fun total k => total + f k) init =
        init + ListNatSumBy f slots := by
  intro slots
  induction slots with
  | nil =>
      intro init
      simp [ListNatSumBy]
  | cons k rest ih =>
      intro init
      rw [List.foldl_cons, ih]
      simp [ListNatSumBy]
      omega

theorem foldl_add_zero_eq_ListNatSumBy (f : Nat -> Nat)
    (slots : List Nat) :
    slots.foldl (fun total k => total + f k) 0 =
      ListNatSumBy f slots := by
  have h := foldl_add_eq_init_add_ListNatSumBy f slots 0
  simpa using h

noncomputable def TowerFootprintForSlots
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (slots : List Nat) : Nat :=
  ListNatSumBy (TowerSlotFootprint S measure tower n) slots

theorem TowerRecordListForSlots_length_eq_footprint
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (slots : List Nat) :
    (TowerRecordListForSlots S measure tower n slots).length =
      TowerFootprintForSlots S measure tower n slots := by
  induction slots with
  | nil =>
      simp [TowerRecordListForSlots, TowerFootprintForSlots, ListNatSumBy]
  | cons k rest ih =>
      simp [TowerRecordListForSlots, TowerFootprintForSlots, ListNatSumBy,
        List.length_append, TowerSlotFootprint_eq_records_length S measure
          tower n k, ih]

theorem TowerFootprint_eq_slotFootprint_foldl
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat) :
    TowerFootprint S measure tower n =
      (List.range n).foldl
        (fun total k =>
          total + TowerSlotFootprint S measure tower n k)
        0 := by
  classical
  unfold TowerFootprint
  have h :
      ∀ slots : List Nat, ∀ init : Nat,
        slots.foldl
          (fun total k =>
            match tower k with
            | none => total
            | some level =>
                if TowerLevel S tower n k level then
                  total + measure.footprint level
                else
                  total)
          init =
        slots.foldl
          (fun total k =>
            total + TowerSlotFootprint S measure tower n k)
          init := by
    intro slots
    induction slots with
    | nil =>
        intro init
        simp
    | cons k rest ih =>
        intro init
        rw [List.foldl_cons, List.foldl_cons]
        have hstep :
            (match tower k with
            | none => init
            | some level =>
                if TowerLevel S tower n k level then
                  init + measure.footprint level
                else
                  init) =
            init + TowerSlotFootprint S measure tower n k := by
          unfold TowerSlotFootprint
          cases hslot : tower k with
          | none => simp
          | some level =>
              by_cases hlevel : TowerLevel S tower n k level
              · simp [hlevel]
              · simp [hlevel]
        rw [hstep]
        exact ih (init + TowerSlotFootprint S measure tower n k)
  exact h (List.range n) 0

theorem TowerFootprint_eq_TowerFootprintForSlots_range
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat) :
    TowerFootprint S measure tower n =
      TowerFootprintForSlots S measure tower n (List.range n) := by
  classical
  unfold TowerFootprintForSlots
  rw [TowerFootprint_eq_slotFootprint_foldl S measure tower n]
  exact foldl_add_zero_eq_ListNatSumBy
    (TowerSlotFootprint S measure tower n) (List.range n)

theorem E2_CapacityBound
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (measure : AuditTowerCapacityMeasure S)
    (tower : Nat -> Option (CarriedInstrumentLevel S)) (n : Nat)
    (z : S.T.Z)
    (_hRealizable : CapacityRealizableTower S tower n) :
    TowerFootprint S measure tower n <= measure.cap z := by
  have hFootprintRange :
      TowerFootprint S measure tower n =
        TowerFootprintForSlots S measure tower n (List.range n) :=
    TowerFootprint_eq_TowerFootprintForSlots_range S measure tower n
  have hRecordLength :
      (TowerRecordListForSlots S measure tower n (List.range n)).length =
        TowerFootprintForSlots S measure tower n (List.range n) :=
    TowerRecordListForSlots_length_eq_footprint S measure tower n
      (List.range n)
  have hTowerRecordsNodup :
      (TowerRecordListForSlots S measure tower n (List.range n)).Nodup :=
    TowerRecordListForSlots_nodup S measure tower n (List.range n)
      List.nodup_range
  have hTowerRecordsSubset :
      ∀ record : measure.RecordId,
        record ∈ TowerRecordListForSlots S measure tower n (List.range n) ->
          record ∈ (measure.carrierRecordUniverse z).records :=
    TowerRecordListForSlots_subset_carrier S measure tower n z
      (List.range n)
  have hLengthBound :
      (TowerRecordListForSlots S measure tower n (List.range n)).length <=
        (measure.carrierRecordUniverse z).records.length :=
    list_length_le_of_nodup_subset
      (TowerRecordListForSlots S measure tower n (List.range n))
      (measure.carrierRecordUniverse z).records
      hTowerRecordsNodup
      (measure.carrierRecordUniverse z).nodup
      hTowerRecordsSubset
  have hCap :
      (measure.carrierRecordUniverse z).records.length = measure.cap z := by
    simpa [FiniteRecordSet.card] using measure.capIsUniverseCard z
  rw [hFootprintRange, ← hRecordLength]
  exact hCap ▸ hLengthBound

theorem E2_StatusPartition
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''} {RepairRefinement : Type z'''''}
    {Horizon : Type u1}
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
    (z : S.T.Z) (horizon : Horizon) (targetLevel : Nat)
    (hComplete :
      CompleteBoundedReflexivityStatus S H installs postState statusPolicy
        claimTarget measure C tower n z horizon targetLevel) :
    (ActiveScopedHolds S H installs postState statusPolicy claimTarget
        measure C tower n z horizon targetLevel ∧
        ¬ RotatingHolds S H installs postState statusPolicy claimTarget
          measure C tower n z horizon targetLevel ∧
        ¬ SaturatedHolds S statusPolicy claimTarget measure tower n z
          targetLevel ∧
        ¬ CircularBlockedHolds S statusPolicy claimTarget tower n z
          targetLevel) ∨
      (RotatingHolds S H installs postState statusPolicy claimTarget
        measure C tower n z horizon targetLevel ∧
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
        ¬ RotatingHolds S H installs postState statusPolicy claimTarget
          measure C tower n z horizon targetLevel ∧
        ¬ CircularBlockedHolds S statusPolicy claimTarget tower n z
          targetLevel) ∨
      (CircularBlockedHolds S statusPolicy claimTarget tower n z
        targetLevel ∧
        ¬ ActiveScopedHolds S H installs postState statusPolicy claimTarget
          measure C tower n z horizon targetLevel ∧
        ¬ RotatingHolds S H installs postState statusPolicy claimTarget
          measure C tower n z horizon targetLevel ∧
        ¬ SaturatedHolds S statusPolicy claimTarget measure tower n z
          targetLevel) := by
  let hUnique := hComplete.2
  rcases hComplete.1 with ⟨record, _hOccurrence, hBranch⟩
  rcases hBranch with hActiveCase | hRest
  · have hActive :
        ActiveScopedHolds S H installs postState statusPolicy claimTarget
          measure C tower n z horizon targetLevel :=
      ⟨record, hActiveCase⟩
    have hStatus :
        record.status = BoundedReflexivityStatus.active_scoped :=
      hActiveCase.2.1
    have hNotRotating :
        ¬ RotatingHolds S H installs postState statusPolicy claimTarget
          measure C tower n z horizon targetLevel := by
      intro hOther
      rcases hOther with ⟨other, hOtherCase⟩
      have hsame := hUnique record other hActiveCase.1 hOtherCase.1
      rw [hStatus, hOtherCase.2.1] at hsame
      cases hsame
    have hNotSaturated :
        ¬ SaturatedHolds S statusPolicy claimTarget measure tower n z
          targetLevel := by
      intro hOther
      rcases hOther with ⟨other, hOtherCase⟩
      have hsame := hUnique record other hActiveCase.1 hOtherCase.1
      rw [hStatus, hOtherCase.2.1] at hsame
      cases hsame
    have hNotCircular :
        ¬ CircularBlockedHolds S statusPolicy claimTarget tower n z
          targetLevel := by
      intro hOther
      rcases hOther with ⟨other, hOtherCase⟩
      have hsame := hUnique record other hActiveCase.1 hOtherCase.1
      rw [hStatus, hOtherCase.2.1] at hsame
      cases hsame
    exact Or.inl ⟨hActive, hNotRotating, hNotSaturated, hNotCircular⟩
  · rcases hRest with hRotatingCase | hRest
    · have hRotating :
          RotatingHolds S H installs postState statusPolicy claimTarget
            measure C tower n z horizon targetLevel :=
        ⟨record, hRotatingCase⟩
      have hStatus :
          record.status = BoundedReflexivityStatus.rotating :=
        hRotatingCase.2.1
      have hNotActive :
          ¬ ActiveScopedHolds S H installs postState statusPolicy claimTarget
            measure C tower n z horizon targetLevel := by
        intro hOther
        rcases hOther with ⟨other, hOtherCase⟩
        have hsame := hUnique record other hRotatingCase.1 hOtherCase.1
        rw [hStatus, hOtherCase.2.1] at hsame
        cases hsame
      have hNotSaturated :
          ¬ SaturatedHolds S statusPolicy claimTarget measure tower n z
            targetLevel := by
        intro hOther
        rcases hOther with ⟨other, hOtherCase⟩
        have hsame := hUnique record other hRotatingCase.1 hOtherCase.1
        rw [hStatus, hOtherCase.2.1] at hsame
        cases hsame
      have hNotCircular :
          ¬ CircularBlockedHolds S statusPolicy claimTarget tower n z
            targetLevel := by
        intro hOther
        rcases hOther with ⟨other, hOtherCase⟩
        have hsame := hUnique record other hRotatingCase.1 hOtherCase.1
        rw [hStatus, hOtherCase.2.1] at hsame
        cases hsame
      exact
        Or.inr
          (Or.inl ⟨hRotating, hNotActive, hNotSaturated, hNotCircular⟩)
    · rcases hRest with hSaturatedCase | hCircularCase
      · have hSaturated :
            SaturatedHolds S statusPolicy claimTarget measure tower n z
              targetLevel :=
          ⟨record, hSaturatedCase⟩
        have hStatus :
            record.status = BoundedReflexivityStatus.saturated :=
          hSaturatedCase.2.1
        have hNotActive :
            ¬ ActiveScopedHolds S H installs postState statusPolicy
              claimTarget measure C tower n z horizon targetLevel := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hSaturatedCase.1 hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        have hNotRotating :
            ¬ RotatingHolds S H installs postState statusPolicy claimTarget
              measure C tower n z horizon targetLevel := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hSaturatedCase.1 hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        have hNotCircular :
            ¬ CircularBlockedHolds S statusPolicy claimTarget tower n z
              targetLevel := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hSaturatedCase.1 hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        exact
          Or.inr
            (Or.inr
              (Or.inl
                ⟨hSaturated, hNotActive, hNotRotating, hNotCircular⟩))
      · have hCircular :
            CircularBlockedHolds S statusPolicy claimTarget tower n z
              targetLevel :=
          ⟨record, hCircularCase⟩
        have hStatus :
            record.status = BoundedReflexivityStatus.circular_blocked :=
          hCircularCase.2.1
        have hNotActive :
            ¬ ActiveScopedHolds S H installs postState statusPolicy
              claimTarget measure C tower n z horizon targetLevel := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hCircularCase.1 hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        have hNotRotating :
            ¬ RotatingHolds S H installs postState statusPolicy claimTarget
              measure C tower n z horizon targetLevel := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hCircularCase.1 hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        have hNotSaturated :
            ¬ SaturatedHolds S statusPolicy claimTarget measure tower n z
              targetLevel := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hCircularCase.1 hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        exact
          Or.inr
            (Or.inr
              (Or.inr
                ⟨hCircular, hNotActive, hNotRotating, hNotSaturated⟩))

end SixBirdsFoundationsV
