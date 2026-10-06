import SixBirdsFoundationsV.Laws.E6E9PricedAccess

namespace SixBirdsFoundationsV

open SixBirdsMetaMath.Main.LegalQuotient
open SixBirdsMetaMath.Xi.AdequacyResidual

/-!
E7 alarm setup.

This module is the setup layer only.  It introduces the Xi excess witness,
abstract F19 viability-coupling predicates, carried attention-constraint
rewrites, and carried alarm-disposition records.  The trichotomy and
preemption theorems are intentionally left to later subsections.

As in E6/E9, all host-governance facts that are not already mechanized in
Foundations V are verification-shaped certified inputs, not derived solvers or
new hidden axioms.
-/

def ResidualMatrix {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y) : Mat z z :=
  adequacyResidual C L D KLLdagger

def DeltaXi {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y) (Omega : Mat z z) : Mat z z :=
  matSub (ResidualMatrix C L D KLLdagger) Omega

def BlindSpotWitness {e y z : Nat}
    (C : Mat e e) (L : Mat y e) (D : Mat z e)
    (KLLdagger : Mat y y) (Omega : Mat z z) (witness : Vec z) : Prop :=
  quad (DeltaXi C L D KLLdagger Omega) witness > 0

/--
Certified host input standing for F19's dissolution obstruction along a
witness direction.  E7 does not derive this from a viability kernel in this
module.
-/
structure DissolutionObstructionNonempty
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (Probe : Type z) (XiFamily : Type z') (Horizon : Type z'')
    (xiDim : Nat) where
  holds : ActiveFamily Probe XiFamily -> Vec xiDim -> Horizon -> Prop

/--
Certified host input standing for whether the F19-style viability probe
descends within the declared horizon.  No F19 greatest-fixed-point machinery
is constructed here.
-/
structure ViabilityProbeDescends
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (Probe : Type z) (XiFamily : Type z') (Horizon : Type z'')
    (xiDim : Nat) where
  holds : ActiveFamily Probe XiFamily -> Vec xiDim -> Horizon -> Prop

def ViabilityCoupled
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    {Probe : Type z} {XiFamily : Type z'} {Horizon : Type z''}
    {xiDim : Nat}
    (dissolution :
      DissolutionObstructionNonempty S Probe XiFamily Horizon xiDim)
    (L_t : ActiveFamily Probe XiFamily) (witness : Vec xiDim)
    (horizon : Horizon) : Prop :=
  dissolution.holds L_t witness horizon

structure AttentionConstraintSet
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (Probe : Type z) (XiFamily : Type z') (WitnessVector : Type z'')
    (PriorityRecord : Type z''') where
  governs : AccessPolicy Probe XiFamily
  admittedMove : AccessMove Probe XiFamily -> Prop
  witnessExposureAdmissible : WitnessVector -> Prop
  exposureBudgetEntry : LedgerEntry
  priorityThresholdRecord : PriorityRecord
  preemptedWitness : Option WitnessVector

/--
Carried rewrite of the standing access-policy constraint set.  The carriedness
check is genuine D3/D4 `CarriedRecordAt` evidence for the post-rewrite
constraint record, plus a concrete budget-entry membership check in
`S.Lambda_S`.
-/
def AlarmConstraintRewrite
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    {Probe : Type z} {XiFamily : Type z'} {WitnessVector : Type z''}
    {PriorityRecord : Type z'''}
    (constraintPolicy :
      CarriedRecordPolicy S.T
        (AttentionConstraintSet S Probe XiFamily WitnessVector PriorityRecord))
    (policy : AccessPolicy Probe XiFamily)
    (before after :
      AttentionConstraintSet S Probe XiFamily WitnessVector PriorityRecord)
    (witness : WitnessVector) (n0 : Nat)
    (sourceTag : FineSourceTag) (generatedByS inScope : Bool) : Prop :=
  before.governs = policy ∧
    after.governs = policy ∧
    CarriedRecordAt constraintPolicy after n0 sourceTag generatedByS inScope ∧
    after.exposureBudgetEntry ∈ S.Lambda_S.ledgerEntries ∧
    before ≠ after ∧
    after.witnessExposureAdmissible witness ∧
    after.preemptedWitness = some witness

inductive AlarmDispositionKind where
  | currentize
  | boundary_nonclosure
  | lawful_discount

inductive AlarmDiscountReason where
  | protocol_artifact
  | currentizable_residue
  | out_of_horizon
  | coupling_dissolved

structure AlarmStatusRecord (StatusPayload : Type u) where
  discountReason : AlarmDiscountReason
  payload : StatusPayload

def DiscountReason {StatusPayload : Type u}
    (statusRecord : AlarmStatusRecord StatusPayload) : AlarmDiscountReason :=
  statusRecord.discountReason

/--
Certified host input for F9-style statused discounting.  Foundations V has not
yet mechanized F9 status records as a reusable Lean structure, so E7 treats the
status predicate as supplied governance data over `AlarmStatusRecord`.
-/
abbrev F9StatusedDiscount (StatusPayload : Type u) : Type u :=
  AlarmStatusRecord StatusPayload -> Prop

structure AlarmDispositionRecord
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (Probe : Type z) (XiFamily : Type z') (WitnessVector : Type z'')
    (Horizon : Type z''') (PriorityRecord : Type z'''')
    (StatusPayload : Type z''''') where
  witnessVector : WitnessVector
  horizon : Horizon
  kind : AlarmDispositionKind
  sourcePolicy : AccessPolicy Probe XiFamily
  preConstraintSet :
    AttentionConstraintSet S Probe XiFamily WitnessVector PriorityRecord
  postConstraintSet :
    AttentionConstraintSet S Probe XiFamily WitnessVector PriorityRecord
  statusRecord : AlarmStatusRecord StatusPayload

def AlarmDispositionCarriedAt
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    {Probe : Type z} {XiFamily : Type z'} {WitnessVector : Type z''}
    {Horizon : Type z'''} {PriorityRecord : Type z''''}
    {StatusPayload : Type z'''''}
    (alarmDispositionPolicy :
      CarriedRecordPolicy S.T
        (AlarmDispositionRecord S Probe XiFamily WitnessVector Horizon
          PriorityRecord StatusPayload))
    (record :
      AlarmDispositionRecord S Probe XiFamily WitnessVector Horizon
        PriorityRecord StatusPayload)
    (n0 : Nat) (sourceTag : FineSourceTag)
    (generatedByS inScope : Bool) : Prop :=
  CarriedRecordAt alarmDispositionPolicy record n0 sourceTag generatedByS
    inScope

structure AlarmDispositionInventory
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (Probe : Type z) (XiFamily : Type z') (WitnessVector : Type z'')
    (Horizon : Type z''') (PriorityRecord : Type z'''')
    (StatusPayload : Type z''''') where
  alarmDispositionPolicy :
    CarriedRecordPolicy S.T
      (AlarmDispositionRecord S Probe XiFamily WitnessVector Horizon
        PriorityRecord StatusPayload)
  /--
  Optional finite bookkeeping inventory for hosts that want to enumerate alarm
  records.  It is not the scope of E7's uniqueness theorem: `AlarmDispositionFor`
  ranges over every genuinely carried occurrence for the witness/horizon rather
  than only records listed here.
  -/
  records :
    List
      (AlarmDispositionRecord S Probe XiFamily WitnessVector Horizon
        PriorityRecord StatusPayload)
  responseForActiveFamily :
    ActiveFamily Probe XiFamily ->
      AlarmDispositionRecord S Probe XiFamily WitnessVector Horizon
        PriorityRecord StatusPayload -> Prop

def AlarmDispositionFor
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    {Probe : Type z} {XiFamily : Type z'} {WitnessVector : Type z''}
    {Horizon : Type z'''} {PriorityRecord : Type z''''}
    {StatusPayload : Type z'''''}
    (inventory :
      AlarmDispositionInventory S Probe XiFamily WitnessVector Horizon
        PriorityRecord StatusPayload)
    (L_t : ActiveFamily Probe XiFamily) (witness : WitnessVector)
    (horizon : Horizon)
    (record :
      AlarmDispositionRecord S Probe XiFamily WitnessVector Horizon
        PriorityRecord StatusPayload)
    (n0 : Nat) (sourceTag : FineSourceTag)
    (generatedByS inScope : Bool) : Prop :=
  record.witnessVector = witness ∧
    record.horizon = horizon ∧
    inventory.responseForActiveFamily L_t record ∧
    AlarmDispositionCarriedAt inventory.alarmDispositionPolicy record n0
      sourceTag generatedByS inScope

/--
Certified host input classifying which carried ledger entries record a forced
exposure/currentization move for a witness.  E7 checks actual membership in
`S.Lambda_S`; this predicate only classifies the entry's alarm meaning.
-/
structure ForcedExposureLedgerEntry
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (xiDim : Nat) where
  holds : LedgerEntry -> Vec xiDim -> Prop

def ForcedExposureMoveRecorded
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    {xiDim : Nat}
    (forcedExposure : ForcedExposureLedgerEntry S xiDim)
    (entry : LedgerEntry)
    (witness : Vec xiDim) : Prop :=
  entry ∈ S.Lambda_S.ledgerEntries ∧ forcedExposure.holds entry witness

def PreemptionOverrides
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    {Probe : Type z} {XiFamily : Type z'} {PriorityRecord : Type z''}
    {xiDim : Nat}
    (policy : AccessPolicy Probe XiFamily)
    (constraintSet :
      AttentionConstraintSet S Probe XiFamily (Vec xiDim) PriorityRecord)
    (witness : Vec xiDim) : Prop :=
  constraintSet.governs = policy ∧
    constraintSet.preemptedWitness = some witness

/--
Certified host input for F11 no-overread discipline on the post-alarm
constraint set.  Foundations V has not yet mechanized F11 as a reusable Lean
checker, so E7 treats this as an audited host predicate.
-/
structure NoOverreadDiscipline
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (Probe : Type z) (XiFamily : Type z') (PriorityRecord : Type z'')
    (xiDim : Nat) where
  holds :
    AttentionConstraintSet S Probe XiFamily (Vec xiDim) PriorityRecord ->
      Prop

/--
Certified host input for F12/null-mode legality on the post-alarm constraint
set and witness direction.  It prevents preemption from crediting zero-cost or
null-residual directions by declaration alone.
-/
structure NullModeLegality
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (economy : ProbeEconomy S Probe XiFamily)
    (PriorityRecord : Type z) (xiDim : Nat) where
  holds :
    AttentionConstraintSet S Probe XiFamily (Vec xiDim) PriorityRecord ->
      Vec xiDim -> Prop

/--
Certified host input that a status record is a boundary-nonclosure record.
This is a real predicate on `AlarmStatusRecord`, not an unconstrained branch
`Prop`.
-/
structure BoundaryNonclosureStatusPredicate (StatusPayload : Type u) where
  holds : AlarmStatusRecord StatusPayload -> Prop

def BoundaryNonclosureStatusRecorded
    {StatusPayload : Type u}
    (boundaryStatus : BoundaryNonclosureStatusPredicate StatusPayload)
    (statusRecord : AlarmStatusRecord StatusPayload) : Prop :=
  boundaryStatus.holds statusRecord

def AllowedDiscountReason : AlarmDiscountReason -> Prop
  | AlarmDiscountReason.protocol_artifact => True
  | AlarmDiscountReason.currentizable_residue => True
  | AlarmDiscountReason.out_of_horizon => True
  | AlarmDiscountReason.coupling_dissolved => True

def CurrentizationCase
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    {Probe : Type z} {XiFamily : Type z'} {Horizon : Type z''}
    {PriorityRecord : Type z'''} {StatusPayload : Type z''''}
    {xiDim : Nat}
    (inventory :
      AlarmDispositionInventory S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload)
    (constraintPolicy :
      CarriedRecordPolicy S.T
        (AttentionConstraintSet S Probe XiFamily (Vec xiDim) PriorityRecord))
    (forcedExposure : ForcedExposureLedgerEntry S xiDim)
    (noOverread :
      NoOverreadDiscipline S Probe XiFamily PriorityRecord xiDim)
    (economy : ProbeEconomy S Probe XiFamily)
    (nullMode :
      NullModeLegality (S := S) (economy := economy) PriorityRecord xiDim)
    (L_t : ActiveFamily Probe XiFamily)
    (policy : AccessPolicy Probe XiFamily)
    (record :
      AlarmDispositionRecord S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload)
    (recordN0 : Nat) (recordSourceTag : FineSourceTag)
    (recordGeneratedByS recordInScope : Bool)
    (rewriteN0 : Nat) (rewriteSourceTag : FineSourceTag)
    (rewriteGeneratedByS rewriteInScope : Bool) : Prop :=
  record.kind = AlarmDispositionKind.currentize ∧
    AlarmDispositionFor inventory L_t record.witnessVector record.horizon
      record recordN0 recordSourceTag recordGeneratedByS recordInScope ∧
    AlarmConstraintRewrite constraintPolicy policy record.preConstraintSet
      record.postConstraintSet record.witnessVector rewriteN0
      rewriteSourceTag rewriteGeneratedByS rewriteInScope ∧
    ForcedExposureMoveRecorded forcedExposure
      record.postConstraintSet.exposureBudgetEntry record.witnessVector ∧
    PreemptionOverrides policy record.postConstraintSet record.witnessVector ∧
    noOverread.holds record.postConstraintSet ∧
    nullMode.holds record.postConstraintSet record.witnessVector

def BoundaryNonclosureCase
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    {Probe : Type z} {XiFamily : Type z'} {Horizon : Type z''}
    {PriorityRecord : Type z'''} {StatusPayload : Type z''''}
    {xiDim : Nat}
    (inventory :
      AlarmDispositionInventory S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload)
    (descends : ViabilityProbeDescends S Probe XiFamily Horizon xiDim)
    (boundaryStatus : BoundaryNonclosureStatusPredicate StatusPayload)
    (L_t : ActiveFamily Probe XiFamily)
    (record :
      AlarmDispositionRecord S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload)
    (recordN0 : Nat) (recordSourceTag : FineSourceTag)
    (recordGeneratedByS recordInScope : Bool) : Prop :=
  record.kind = AlarmDispositionKind.boundary_nonclosure ∧
    AlarmDispositionFor inventory L_t record.witnessVector record.horizon
      record recordN0 recordSourceTag recordGeneratedByS recordInScope ∧
    ¬ descends.holds L_t record.witnessVector record.horizon ∧
    BoundaryNonclosureStatusRecorded boundaryStatus record.statusRecord

def LawfulDiscountCase
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    {Probe : Type z} {XiFamily : Type z'} {Horizon : Type z''}
    {PriorityRecord : Type z'''} {StatusPayload : Type z''''}
    {xiDim : Nat}
    (inventory :
      AlarmDispositionInventory S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload)
    (statusedDiscount : F9StatusedDiscount StatusPayload)
    (L_t : ActiveFamily Probe XiFamily)
    (record :
      AlarmDispositionRecord S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload)
    (recordN0 : Nat) (recordSourceTag : FineSourceTag)
    (recordGeneratedByS recordInScope : Bool) : Prop :=
  record.kind = AlarmDispositionKind.lawful_discount ∧
    AlarmDispositionFor inventory L_t record.witnessVector record.horizon
      record recordN0 recordSourceTag recordGeneratedByS recordInScope ∧
    statusedDiscount record.statusRecord ∧
    AllowedDiscountReason (DiscountReason record.statusRecord)

def CurrentizationHolds
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    {Probe : Type z} {XiFamily : Type z'} {Horizon : Type z''}
    {PriorityRecord : Type z'''} {StatusPayload : Type z''''}
    {xiDim : Nat}
    (inventory :
      AlarmDispositionInventory S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload)
    (constraintPolicy :
      CarriedRecordPolicy S.T
        (AttentionConstraintSet S Probe XiFamily (Vec xiDim) PriorityRecord))
    (forcedExposure : ForcedExposureLedgerEntry S xiDim)
    (noOverread :
      NoOverreadDiscipline S Probe XiFamily PriorityRecord xiDim)
    (economy : ProbeEconomy S Probe XiFamily)
    (nullMode : NullModeLegality (S := S) (economy := economy)
      PriorityRecord xiDim)
    (L_t : ActiveFamily Probe XiFamily)
    (policy : AccessPolicy Probe XiFamily) (witness : Vec xiDim)
    (horizon : Horizon) : Prop :=
  ∃ record :
      AlarmDispositionRecord S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload,
    ∃ recordN0 : Nat,
      ∃ recordSourceTag : FineSourceTag,
        ∃ recordGeneratedByS : Bool,
          ∃ recordInScope : Bool,
            ∃ rewriteN0 : Nat,
              ∃ rewriteSourceTag : FineSourceTag,
                ∃ rewriteGeneratedByS : Bool,
                  ∃ rewriteInScope : Bool,
                    AlarmDispositionFor inventory L_t witness horizon record
                      recordN0 recordSourceTag recordGeneratedByS
                      recordInScope ∧
                    CurrentizationCase inventory constraintPolicy
                      forcedExposure noOverread economy nullMode L_t policy
                      record recordN0 recordSourceTag recordGeneratedByS
                      recordInScope rewriteN0 rewriteSourceTag
                      rewriteGeneratedByS rewriteInScope

def BoundaryNonclosureHolds
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    {Probe : Type z} {XiFamily : Type z'} {Horizon : Type z''}
    {PriorityRecord : Type z'''} {StatusPayload : Type z''''}
    {xiDim : Nat}
    (inventory :
      AlarmDispositionInventory S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload)
    (descends : ViabilityProbeDescends S Probe XiFamily Horizon xiDim)
    (boundaryStatus : BoundaryNonclosureStatusPredicate StatusPayload)
    (L_t : ActiveFamily Probe XiFamily) (witness : Vec xiDim)
    (horizon : Horizon) : Prop :=
  ∃ record :
      AlarmDispositionRecord S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload,
    ∃ recordN0 : Nat,
      ∃ recordSourceTag : FineSourceTag,
        ∃ recordGeneratedByS : Bool,
          ∃ recordInScope : Bool,
            AlarmDispositionFor inventory L_t witness horizon record
              recordN0 recordSourceTag recordGeneratedByS recordInScope ∧
            BoundaryNonclosureCase inventory descends boundaryStatus L_t
              record recordN0 recordSourceTag recordGeneratedByS recordInScope

def LawfulDiscountHolds
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    {Probe : Type z} {XiFamily : Type z'} {Horizon : Type z''}
    {PriorityRecord : Type z'''} {StatusPayload : Type z''''}
    {xiDim : Nat}
    (inventory :
      AlarmDispositionInventory S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload)
    (statusedDiscount : F9StatusedDiscount StatusPayload)
    (L_t : ActiveFamily Probe XiFamily) (witness : Vec xiDim)
    (horizon : Horizon) : Prop :=
  ∃ record :
      AlarmDispositionRecord S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload,
    ∃ recordN0 : Nat,
      ∃ recordSourceTag : FineSourceTag,
        ∃ recordGeneratedByS : Bool,
          ∃ recordInScope : Bool,
            AlarmDispositionFor inventory L_t witness horizon record
              recordN0 recordSourceTag recordGeneratedByS recordInScope ∧
            LawfulDiscountCase inventory statusedDiscount L_t record
              recordN0 recordSourceTag recordGeneratedByS recordInScope

def LawfulAlarmDispositionUniqueTotality
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    {Probe : Type z} {XiFamily : Type z'} {Horizon : Type z''}
    {PriorityRecord : Type z'''} {StatusPayload : Type z''''}
    {xiDim : Nat}
    (inventory :
      AlarmDispositionInventory S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload)
    (constraintPolicy :
      CarriedRecordPolicy S.T
        (AttentionConstraintSet S Probe XiFamily (Vec xiDim) PriorityRecord))
    (forcedExposure : ForcedExposureLedgerEntry S xiDim)
    (noOverread :
      NoOverreadDiscipline S Probe XiFamily PriorityRecord xiDim)
    (economy : ProbeEconomy S Probe XiFamily)
    (nullMode : NullModeLegality (S := S) (economy := economy)
      PriorityRecord xiDim)
    (descends : ViabilityProbeDescends S Probe XiFamily Horizon xiDim)
    (boundaryStatus : BoundaryNonclosureStatusPredicate StatusPayload)
    (statusedDiscount : F9StatusedDiscount StatusPayload)
    (L_t : ActiveFamily Probe XiFamily)
    (policy : AccessPolicy Probe XiFamily) (witness : Vec xiDim)
    (horizon : Horizon) : Prop :=
  (CurrentizationHolds inventory constraintPolicy forcedExposure noOverread
      economy nullMode L_t policy witness horizon ∨
    BoundaryNonclosureHolds inventory descends boundaryStatus L_t witness
      horizon ∨
    LawfulDiscountHolds inventory statusedDiscount L_t witness horizon) ∧
    ∀ record1 record2 :
      AlarmDispositionRecord S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload,
      (∃ n01 : Nat,
        ∃ sourceTag1 : FineSourceTag,
          ∃ generatedByS1 : Bool,
            ∃ inScope1 : Bool,
              AlarmDispositionFor inventory L_t witness horizon record1 n01
                sourceTag1 generatedByS1 inScope1) ->
      (∃ n02 : Nat,
        ∃ sourceTag2 : FineSourceTag,
          ∃ generatedByS2 : Bool,
            ∃ inScope2 : Bool,
              AlarmDispositionFor inventory L_t witness horizon record2 n02
                sourceTag2 generatedByS2 inScope2) ->
      record1.kind = record2.kind

/--
`BlindSpotWitness`, `ViabilityCoupled`, `PolicyCarriedAt`, and
`LawfulActiveFamilyAt` are retained in the theorem statement for fidelity to
E7's source law.  The formal trichotomy proof below uses the already-certified
`LawfulAlarmDispositionUniqueTotality` package, which is the governance
hypothesis saying that such a positive, viability-coupled witness over a
carried policy and lawful active family has been given a branch-valid unique
disposition.
-/
theorem E7_AlarmTrichotomy
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    {Probe : Type z} {XiFamily : Type z'} {Horizon : Type z''}
    {PriorityRecord : Type z'''} {StatusPayload : Type z''''}
    {e yDim xiDim : Nat}
    (C : Mat e e) (Lxi : Mat yDim e) (D : Mat xiDim e)
    (KLLdagger : Mat yDim yDim) (Omega : Mat xiDim xiDim)
    (policyRecord :
      CarriedRecordPolicy S.T (AccessPolicy Probe XiFamily))
    (inventory :
      AlarmDispositionInventory S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload)
    (constraintPolicy :
      CarriedRecordPolicy S.T
        (AttentionConstraintSet S Probe XiFamily (Vec xiDim) PriorityRecord))
    (forcedExposure : ForcedExposureLedgerEntry S xiDim)
    (noOverread :
      NoOverreadDiscipline S Probe XiFamily PriorityRecord xiDim)
    (economy : ProbeEconomy S Probe XiFamily)
    (nullMode : NullModeLegality (S := S) (economy := economy)
      PriorityRecord xiDim)
    (dissolution :
      DissolutionObstructionNonempty S Probe XiFamily Horizon xiDim)
    (descends : ViabilityProbeDescends S Probe XiFamily Horizon xiDim)
    (boundaryStatus : BoundaryNonclosureStatusPredicate StatusPayload)
    (statusedDiscount : F9StatusedDiscount StatusPayload)
    (L_t : ActiveFamily Probe XiFamily)
    (policy : AccessPolicy Probe XiFamily) (witness : Vec xiDim)
    (horizon : Horizon)
    (policyN0 : Nat) (policySourceTag : FineSourceTag)
    (policyGeneratedByS policyInScope : Bool)
    (activeFamilyN0 : Nat) (activeFamilySourceTag : FineSourceTag)
    (activeFamilyGeneratedByS activeFamilyInScope : Bool)
    (_hBlindSpot :
      BlindSpotWitness C Lxi D KLLdagger Omega witness)
    (_hViabilityCoupled :
      ViabilityCoupled dissolution L_t witness horizon)
    (_hPolicyCarried :
      PolicyCarriedAt policyRecord policy policyN0 policySourceTag
        policyGeneratedByS policyInScope)
    (_hLawfulActiveFamily :
      LawfulActiveFamilyAt economy L_t activeFamilyN0 activeFamilySourceTag
        activeFamilyGeneratedByS activeFamilyInScope)
    (hTotal :
      LawfulAlarmDispositionUniqueTotality inventory constraintPolicy
        forcedExposure noOverread economy nullMode descends boundaryStatus
        statusedDiscount L_t policy witness horizon) :
    ∃ k : AlarmDispositionKind,
      (∀ record :
        AlarmDispositionRecord S Probe XiFamily (Vec xiDim) Horizon
          PriorityRecord StatusPayload,
        (∃ n0 : Nat,
          ∃ sourceTag : FineSourceTag,
            ∃ generatedByS : Bool,
              ∃ inScope : Bool,
                AlarmDispositionFor inventory L_t witness horizon record n0
                  sourceTag generatedByS inScope) ->
        record.kind = k) ∧
      ((CurrentizationHolds inventory constraintPolicy forcedExposure
          noOverread economy nullMode L_t policy witness horizon ∧
          ¬ BoundaryNonclosureHolds inventory descends boundaryStatus L_t
            witness horizon ∧
          ¬ LawfulDiscountHolds inventory statusedDiscount L_t witness
            horizon) ∨
        (BoundaryNonclosureHolds inventory descends boundaryStatus L_t
            witness horizon ∧
          ¬ CurrentizationHolds inventory constraintPolicy forcedExposure
            noOverread economy nullMode L_t policy witness horizon ∧
          ¬ LawfulDiscountHolds inventory statusedDiscount L_t witness
            horizon) ∨
        (LawfulDiscountHolds inventory statusedDiscount L_t witness
            horizon ∧
          ¬ CurrentizationHolds inventory constraintPolicy forcedExposure
            noOverread economy nullMode L_t policy witness horizon ∧
          ¬ BoundaryNonclosureHolds inventory descends boundaryStatus L_t
            witness horizon)) := by
  let hUnique := hTotal.2
  rcases hTotal.1 with hCurrent | hBoundary | hDiscount
  · rcases hCurrent with
      ⟨record, recordN0, recordSourceTag, recordGeneratedByS,
        recordInScope, rewriteN0, rewriteSourceTag, rewriteGeneratedByS,
        rewriteInScope, hFor, hCase⟩
    have hCurrentWitness :
        CurrentizationHolds inventory constraintPolicy forcedExposure
          noOverread economy nullMode L_t policy witness horizon :=
      ⟨record, recordN0, recordSourceTag, recordGeneratedByS,
        recordInScope, rewriteN0, rewriteSourceTag, rewriteGeneratedByS,
        rewriteInScope, hFor, hCase⟩
    have hRecordFor :
        ∃ n0 : Nat,
          ∃ sourceTag : FineSourceTag,
            ∃ generatedByS : Bool,
              ∃ inScope : Bool,
                AlarmDispositionFor inventory L_t witness horizon record n0
                  sourceTag generatedByS inScope :=
      ⟨recordN0, recordSourceTag, recordGeneratedByS, recordInScope, hFor⟩
    have allSame :
        ∀ other :
          AlarmDispositionRecord S Probe XiFamily (Vec xiDim) Horizon
            PriorityRecord StatusPayload,
          (∃ n0 : Nat,
            ∃ sourceTag : FineSourceTag,
              ∃ generatedByS : Bool,
                ∃ inScope : Bool,
                  AlarmDispositionFor inventory L_t witness horizon other n0
                    sourceTag generatedByS inScope) ->
          other.kind = AlarmDispositionKind.currentize := by
      intro other hOtherFor
      have hsame := hUnique other record hOtherFor hRecordFor
      rw [hsame, hCase.1]
    have hnotBoundary :
        ¬ BoundaryNonclosureHolds inventory descends boundaryStatus L_t
          witness horizon := by
      intro hBoundary'
      rcases hBoundary' with
        ⟨recordB, n0B, sourceTagB, generatedBySB, inScopeB, hForB,
          hCaseB⟩
      have hRecordBFor :
          ∃ n0 : Nat,
            ∃ sourceTag : FineSourceTag,
              ∃ generatedByS : Bool,
                ∃ inScope : Bool,
                  AlarmDispositionFor inventory L_t witness horizon recordB n0
                    sourceTag generatedByS inScope :=
        ⟨n0B, sourceTagB, generatedBySB, inScopeB, hForB⟩
      have hsame := hUnique record recordB hRecordFor hRecordBFor
      rw [hCase.1, hCaseB.1] at hsame
      cases hsame
    have hnotDiscount :
        ¬ LawfulDiscountHolds inventory statusedDiscount L_t witness
          horizon := by
      intro hDiscount'
      rcases hDiscount' with
        ⟨recordD, n0D, sourceTagD, generatedBySD, inScopeD, hForD,
          hCaseD⟩
      have hRecordDFor :
          ∃ n0 : Nat,
            ∃ sourceTag : FineSourceTag,
              ∃ generatedByS : Bool,
                ∃ inScope : Bool,
                  AlarmDispositionFor inventory L_t witness horizon recordD n0
                    sourceTag generatedByS inScope :=
        ⟨n0D, sourceTagD, generatedBySD, inScopeD, hForD⟩
      have hsame := hUnique record recordD hRecordFor hRecordDFor
      rw [hCase.1, hCaseD.1] at hsame
      cases hsame
    exact
      ⟨AlarmDispositionKind.currentize, allSame,
        Or.inl ⟨hCurrentWitness, hnotBoundary, hnotDiscount⟩⟩
  · rcases hBoundary with
      ⟨record, recordN0, recordSourceTag, recordGeneratedByS,
        recordInScope, hFor, hCase⟩
    have hBoundaryWitness :
        BoundaryNonclosureHolds inventory descends boundaryStatus L_t
          witness horizon :=
      ⟨record, recordN0, recordSourceTag, recordGeneratedByS,
        recordInScope, hFor, hCase⟩
    have hRecordFor :
        ∃ n0 : Nat,
          ∃ sourceTag : FineSourceTag,
            ∃ generatedByS : Bool,
              ∃ inScope : Bool,
                AlarmDispositionFor inventory L_t witness horizon record n0
                  sourceTag generatedByS inScope :=
      ⟨recordN0, recordSourceTag, recordGeneratedByS, recordInScope, hFor⟩
    have allSame :
        ∀ other :
          AlarmDispositionRecord S Probe XiFamily (Vec xiDim) Horizon
            PriorityRecord StatusPayload,
          (∃ n0 : Nat,
            ∃ sourceTag : FineSourceTag,
              ∃ generatedByS : Bool,
                ∃ inScope : Bool,
                  AlarmDispositionFor inventory L_t witness horizon other n0
                    sourceTag generatedByS inScope) ->
          other.kind = AlarmDispositionKind.boundary_nonclosure := by
      intro other hOtherFor
      have hsame := hUnique other record hOtherFor hRecordFor
      rw [hsame, hCase.1]
    have hnotCurrent :
        ¬ CurrentizationHolds inventory constraintPolicy forcedExposure
          noOverread economy nullMode L_t policy witness horizon := by
      intro hCurrent'
      rcases hCurrent' with
        ⟨recordC, n0C, sourceTagC, generatedBySC, inScopeC, rewriteN0C,
          rewriteSourceTagC, rewriteGeneratedBySC, rewriteInScopeC, hForC,
          hCaseC⟩
      have hRecordCFor :
          ∃ n0 : Nat,
            ∃ sourceTag : FineSourceTag,
              ∃ generatedByS : Bool,
                ∃ inScope : Bool,
                  AlarmDispositionFor inventory L_t witness horizon recordC n0
                    sourceTag generatedByS inScope :=
        ⟨n0C, sourceTagC, generatedBySC, inScopeC, hForC⟩
      have hsame := hUnique record recordC hRecordFor hRecordCFor
      rw [hCase.1, hCaseC.1] at hsame
      cases hsame
    have hnotDiscount :
        ¬ LawfulDiscountHolds inventory statusedDiscount L_t witness
          horizon := by
      intro hDiscount'
      rcases hDiscount' with
        ⟨recordD, n0D, sourceTagD, generatedBySD, inScopeD, hForD,
          hCaseD⟩
      have hRecordDFor :
          ∃ n0 : Nat,
            ∃ sourceTag : FineSourceTag,
              ∃ generatedByS : Bool,
                ∃ inScope : Bool,
                  AlarmDispositionFor inventory L_t witness horizon recordD n0
                    sourceTag generatedByS inScope :=
        ⟨n0D, sourceTagD, generatedBySD, inScopeD, hForD⟩
      have hsame := hUnique record recordD hRecordFor hRecordDFor
      rw [hCase.1, hCaseD.1] at hsame
      cases hsame
    exact
      ⟨AlarmDispositionKind.boundary_nonclosure, allSame,
        Or.inr (Or.inl ⟨hBoundaryWitness, hnotCurrent, hnotDiscount⟩)⟩
  · rcases hDiscount with
      ⟨record, recordN0, recordSourceTag, recordGeneratedByS,
        recordInScope, hFor, hCase⟩
    have hDiscountWitness :
        LawfulDiscountHolds inventory statusedDiscount L_t witness horizon :=
      ⟨record, recordN0, recordSourceTag, recordGeneratedByS,
        recordInScope, hFor, hCase⟩
    have hRecordFor :
        ∃ n0 : Nat,
          ∃ sourceTag : FineSourceTag,
            ∃ generatedByS : Bool,
              ∃ inScope : Bool,
                AlarmDispositionFor inventory L_t witness horizon record n0
                  sourceTag generatedByS inScope :=
      ⟨recordN0, recordSourceTag, recordGeneratedByS, recordInScope, hFor⟩
    have allSame :
        ∀ other :
          AlarmDispositionRecord S Probe XiFamily (Vec xiDim) Horizon
            PriorityRecord StatusPayload,
          (∃ n0 : Nat,
            ∃ sourceTag : FineSourceTag,
              ∃ generatedByS : Bool,
                ∃ inScope : Bool,
                  AlarmDispositionFor inventory L_t witness horizon other n0
                    sourceTag generatedByS inScope) ->
          other.kind = AlarmDispositionKind.lawful_discount := by
      intro other hOtherFor
      have hsame := hUnique other record hOtherFor hRecordFor
      rw [hsame, hCase.1]
    have hnotCurrent :
        ¬ CurrentizationHolds inventory constraintPolicy forcedExposure
          noOverread economy nullMode L_t policy witness horizon := by
      intro hCurrent'
      rcases hCurrent' with
        ⟨recordC, n0C, sourceTagC, generatedBySC, inScopeC, rewriteN0C,
          rewriteSourceTagC, rewriteGeneratedBySC, rewriteInScopeC, hForC,
          hCaseC⟩
      have hRecordCFor :
          ∃ n0 : Nat,
            ∃ sourceTag : FineSourceTag,
              ∃ generatedByS : Bool,
                ∃ inScope : Bool,
                  AlarmDispositionFor inventory L_t witness horizon recordC n0
                    sourceTag generatedByS inScope :=
        ⟨n0C, sourceTagC, generatedBySC, inScopeC, hForC⟩
      have hsame := hUnique record recordC hRecordFor hRecordCFor
      rw [hCase.1, hCaseC.1] at hsame
      cases hsame
    have hnotBoundary :
        ¬ BoundaryNonclosureHolds inventory descends boundaryStatus L_t
          witness horizon := by
      intro hBoundary'
      rcases hBoundary' with
        ⟨recordB, n0B, sourceTagB, generatedBySB, inScopeB, hForB,
          hCaseB⟩
      have hRecordBFor :
          ∃ n0 : Nat,
            ∃ sourceTag : FineSourceTag,
              ∃ generatedByS : Bool,
                ∃ inScope : Bool,
                  AlarmDispositionFor inventory L_t witness horizon recordB n0
                    sourceTag generatedByS inScope :=
        ⟨n0B, sourceTagB, generatedBySB, inScopeB, hForB⟩
      have hsame := hUnique record recordB hRecordFor hRecordBFor
      rw [hCase.1, hCaseB.1] at hsame
      cases hsame
    exact
      ⟨AlarmDispositionKind.lawful_discount, allSame,
        Or.inr (Or.inr ⟨hDiscountWitness, hnotCurrent, hnotBoundary⟩)⟩

theorem E7_PreemptionSignature
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    {Probe : Type z} {XiFamily : Type z'} {Horizon : Type z''}
    {PriorityRecord : Type z'''} {StatusPayload : Type z''''}
    {xiDim : Nat}
    {inventory :
      AlarmDispositionInventory S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload}
    {constraintPolicy :
      CarriedRecordPolicy S.T
        (AttentionConstraintSet S Probe XiFamily (Vec xiDim) PriorityRecord)}
    {forcedExposure : ForcedExposureLedgerEntry S xiDim}
    {noOverread :
      NoOverreadDiscipline S Probe XiFamily PriorityRecord xiDim}
    {economy : ProbeEconomy S Probe XiFamily}
    {nullMode : NullModeLegality (S := S) (economy := economy)
      PriorityRecord xiDim}
    {L_t : ActiveFamily Probe XiFamily}
    {policy : AccessPolicy Probe XiFamily}
    {record :
      AlarmDispositionRecord S Probe XiFamily (Vec xiDim) Horizon
        PriorityRecord StatusPayload}
    {recordN0 : Nat} {recordSourceTag : FineSourceTag}
    {recordGeneratedByS recordInScope : Bool}
    {rewriteN0 : Nat} {rewriteSourceTag : FineSourceTag}
    {rewriteGeneratedByS rewriteInScope : Bool}
    (hCase :
      CurrentizationCase inventory constraintPolicy forcedExposure noOverread
        economy nullMode L_t policy record recordN0 recordSourceTag
        recordGeneratedByS recordInScope rewriteN0 rewriteSourceTag
        rewriteGeneratedByS rewriteInScope) :
    AlarmConstraintRewrite constraintPolicy policy record.preConstraintSet
        record.postConstraintSet record.witnessVector rewriteN0
        rewriteSourceTag rewriteGeneratedByS rewriteInScope ∧
      record.preConstraintSet ≠ record.postConstraintSet ∧
      record.postConstraintSet.witnessExposureAdmissible
        record.witnessVector ∧
      PreemptionOverrides policy record.postConstraintSet
        record.witnessVector ∧
      noOverread.holds record.postConstraintSet ∧
      nullMode.holds record.postConstraintSet record.witnessVector := by
  unfold CurrentizationCase at hCase
  rcases hCase with
    ⟨_hKind, _hFor, hRewrite, _hForced, hPreemption, hNoOverread,
      hNullMode⟩
  have hRewriteFull := hRewrite
  unfold AlarmConstraintRewrite at hRewrite
  rcases hRewrite with
    ⟨_hBeforePolicy, _hAfterPolicy, _hCarried, _hBudgetEntry, hChanged,
      hWitnessAdmissible, _hPreempted⟩
  exact
    ⟨hRewriteFull, hChanged, hWitnessAdmissible, hPreemption, hNoOverread,
      hNullMode⟩

end SixBirdsFoundationsV
