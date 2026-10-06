import SixBirdsFoundationsV.Definitional.ESystem
import SixBirdsFoundationsV.Definitional.ProbeEconomy
import SixBirdsFoundationsV.Laws.E1Internalization
import SixBirdsIII.TopDownChannel
import SixBirdsIII.Promotion

namespace SixBirdsFoundationsV

/-!
E4 repair compilation setup.

This setup layer mechanizes the repeated-repair window, compiled-operator
record, lawfulness gates, descent/silence predicates, and certified F2
interface from the accepted E4 six-field normal form
(`formalization/notes/examples/E4.md`).  The five-way compilation status
apparatus and E4 theorems are intentionally left to later mechanization
subsections.
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
variable {RepairRefinement : Type z'''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
  AuditRecord)
variable (H :
  ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
    TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)

/--
A finite window in which the same E1 repair refinement is invoked repeatedly.
The `installs`, `postState`, and `R` witnesses are fixed once for the whole
window, closing the dangling-witness gap noted in the E4 normal form.
-/
structure CompilationCandidateWindow
    (C : ChallengeClass)
    (installs : MovePayloadInstallsRefinement MovePayload RepairRefinement)
    (postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness)
    (R : RepairRefinement) where
  episodeTimes : List Nat
  atLeastTwoInvocations : episodeTimes.length ≥ 2
  invocations :
    ∀ t : Nat, t ∈ episodeTimes ->
      RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord
  occursAtEach :
    ∀ t : Nat, ∀ ht : t ∈ episodeTimes,
      EndogenousRepairOccurrence S H installs postState C t
        (invocations t ht) R

/--
Strict obstruction reduction across every invocation in the window.  This is
the Delta-emptiness-wrapper style used by E1: no post-invocation obstruction is
new, and at least one pre-invocation obstruction is genuinely removed.
-/
def ObstructionReducingAcrossWindow
    {C : ChallengeClass}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {R : RepairRefinement}
    (window : CompilationCandidateWindow S H C installs postState R)
    {X : Type u'} {QPre : Type v'} {QPost : Type w'}
    {FOut : Type x'} {Readout : Type y''''' }
    (preQuotient : Nat -> X -> QPre)
    (postQuotient : Nat -> X -> QPost)
    (F_C : X -> FOut) (r : FOut -> Readout) : Prop :=
  ∀ t : Nat, ∀ _ht : t ∈ window.episodeTimes,
    (∀ x x' : X,
      Delta (postQuotient t) F_C r x x' ->
        Delta (preQuotient t) F_C r x x') ∧
      ∃ x x' : X,
        Delta (preQuotient t) F_C r x x' ∧
          ¬ Delta (postQuotient t) F_C r x x'

/--
Certified exact-rational defect measure for comparing repeated repair
payloads.  D5 audit entries expose carried move records, not payloads directly,
so the payload readout is part of this certified measuring interface while the
actual defect still has the E4-specified `MovePayload -> MovePayload -> Rat`
shape.
-/
structure IdempotenceDefectMeasure
    (_S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  payloadOfInvocation :
    RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord -> MovePayload
  defect : MovePayload -> MovePayload -> Rat
  defectNonneg : ∀ p p' : MovePayload, 0 ≤ defect p p'

def IdempotenceStableAcrossWindow
    {C : ChallengeClass}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {R : RepairRefinement}
    (measure : IdempotenceDefectMeasure S)
    (window : CompilationCandidateWindow S H C installs postState R)
    (threshold : Rat) : Prop :=
  ∀ t : Nat, ∀ ht : t ∈ window.episodeTimes,
    ∀ t' : Nat, ∀ ht' : t' ∈ window.episodeTimes,
      measure.defect
        (measure.payloadOfInvocation (window.invocations t ht))
        (measure.payloadOfInvocation (window.invocations t' ht')) ≤
          threshold

/--
Certified host input for the Strict-Tests memory-only comparator.  E4 checks
that a compiled candidate survives this control; the comparator itself is not
derived in Foundations V.
-/
structure MemoryOnlyComparatorCertified
    (_S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (_C : ChallengeClass) where
  survivesControl : Prop

/--
Compiled lower-layer operator candidate.  It owns the concrete D4 lawful repair
step and all lawfulness-certifying witnesses used by `CompilationLawful`, so
those witnesses cannot be supplied independently from an unrelated claim.
-/
structure CompiledOperatorRecord
    (decompilationPolicy : CarriedRecordPolicy S.T DefectRecord)
    (C : ChallengeClass) (R : RepairRefinement)
    (PromotionCarrier : Type) (PromotionO0 : Type)
    (PromotionO1 : Type) (Family : Type x') (Probe : Type y''''')
    (X : Type u'') (Q : Type v'') where
  z : S.T.Z
  z' : S.T.Z
  defect : DefectRecord
  move : RepairMove S.T MovePayload LedgerEntry MoveRecord S.moveRecordPolicy
  auditRecord : AuditRecord
  sortIsRewriteOrGate :
    move.sort.val = SixBirdsIII.Primitive.P1 ∨
      move.sort.val = SixBirdsIII.Primitive.P2
  lawfulStep :
    LawfulRepairStep S.Lambda_S S.defectRecordPolicy S.moveRecordPolicy
      S.auditRecordPolicy S.I_S S.AdmissibleMove z z' defect move
      auditRecord
  /-- Owning the quotient here prevents descent evidence from being supplied for an unrelated candidate. -/
  inducedQuotient : X -> Q
  decompilationRecord : DefectRecord
  annotationCarried :
    ∃ n : Nat,
      CarriedRecordAt decompilationPolicy decompilationRecord n
        FineSourceTag.committed_state true true
  channelRecord : SixBirdsIII.TopDownChannelRecord
  promotionData :
    SixBirdsIII.PromotionBridgeData PromotionCarrier PromotionO0
      PromotionO1
  memoryOnly : MemoryOnlyComparatorCertified S C
  saturated : Family -> Probe -> Prop
  L : Family
  Mprobe : Probe

def CompilationLawful
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    {C : ChallengeClass} {R : RepairRefinement}
    {PromotionCarrier : Type} {PromotionO0 : Type}
    {PromotionO1 : Type} {Family : Type x'} {Probe : Type y'''''}
    {X : Type u''} {Q : Type v''}
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q) : Prop :=
  SixBirdsIII.TopDownChannelAcceptedBool candidate.channelRecord = true ∧
    candidate.channelRecord.effectGate = true ∧
    SixBirdsIII.AcceptedPromotionFamily
      (SixBirdsIII.Promote candidate.promotionData) ∧
    candidate.memoryOnly.survivesControl ∧
    ¬ (SameFamilySaturated candidate.saturated candidate.L candidate.Mprobe) ∧
    ∃ n : Nat,
      CarriedRecordAt decompilationPolicy candidate.decompilationRecord n
        FineSourceTag.committed_state true true

theorem compilationLawful_requiredCoreGatesPass
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    {C : ChallengeClass} {R : RepairRefinement}
    {PromotionCarrier : Type} {PromotionO0 : Type}
    {PromotionO1 : Type} {Family : Type x'} {Probe : Type y'''''}
    {X : Type u''} {Q : Type v''}
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q)
    (h : CompilationLawful S candidate) :
    SixBirdsIII.RequiredCoreGatesPass candidate.promotionData.gates :=
  SixBirdsIII.promotion_gate_soundness candidate.promotionData h.2.2.1

/--
Independently verified compiled descent for the candidate's induced quotient,
represented in Lean as E1's `Delta` emptiness wrapper over the supplied
family/readout surface.
-/
def CompiledDescent
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    {C : ChallengeClass} {R : RepairRefinement}
    {PromotionCarrier : Type} {PromotionO0 : Type}
    {PromotionO1 : Type} {Family : Type x'} {Probe : Type y'''''}
    {X : Type u''} {Q : Type v''} {FOut : Type w''}
    {Readout : Type x''}
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q)
    (F_C : X -> FOut) (r : FOut -> Readout) : Prop :=
  ∀ x x' : X, ¬ Delta candidate.inducedQuotient F_C r x x'

def HigherPackageGoesSilent
    {C : ChallengeClass}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {R : RepairRefinement}
    (window : CompilationCandidateWindow S H C installs postState R)
    (afterTime : Nat) : Prop :=
  ∀ t : Nat, t > afterTime -> t ∉ window.episodeTimes ->
    ¬ ∃ rho_t : RepairTypedAuditEntry DefectRecord MoveRecord AuditRecord,
      EndogenousRepairOccurrence S H installs postState C t rho_t R

/--
Certified F2 interface used later by the brittleness theorem.  FIV's F2
machinery is not vendored here; the host supplies the split-obstruction
predicate, descent predicate, certified equivalence, and generated quotient.
-/
structure F2Certified
    {X : Type u'} {Q : Type v'} {FOut : Type w'}
    {Readout : Type x'} where
  splitObs :
    (X -> Q) -> (X -> FOut) -> (FOut -> Readout) -> X -> X -> Prop
  descends : (X -> Q) -> (X -> FOut) -> (FOut -> Readout) -> Prop
  descentIffSplitObsEmpty :
    ∀ (q : X -> Q) (F : X -> FOut) (r : FOut -> Readout),
      (∀ x x' : X, ¬ splitObs q F r x x') ↔ descends q F r
  minimalGeneratedQuotient :
    (X -> Q) -> (X -> FOut) -> (FOut -> Readout) -> X -> Q

end Setup

section StatusApparatus

universe u1 v1 w1 x1 y1 z1

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
variable {ChallengeClass : Type z} {SourceQuotient : Type z'}
variable {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
variable {ObstructionWitness : Type z''''}
variable {RepairRefinement : Type z'''''}
variable {PromotionCarrier PromotionO0 PromotionO1 : Type}
variable {Family : Type x'} {Probe : Type y'''''}
variable {X : Type w1} {Q : Type x1}
variable {FOut : Type y1} {Readout : Type z1}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
  AuditRecord)
variable (H :
  ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
    TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)

inductive ObstructionClassification where
  | accepted_brittleness
  | repaired

structure ObstructionStatusRecord
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    {C : ChallengeClass} {R : RepairRefinement}
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q) where
  forClass : ChallengeClass
  x : X
  x' : X
  assignedStatus : ObstructionClassification

def CarriedObstructionStatusFor
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    {C : ChallengeClass} {R : RepairRefinement}
    {candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q}
    (obstructionStatusPolicy :
      CarriedRecordPolicy S.T (ObstructionStatusRecord (X := X) S candidate))
    (otherClass : ChallengeClass) (x x' : X)
    (record : ObstructionStatusRecord (X := X) S candidate) : Prop :=
  record.forClass = otherClass ∧
    record.x = x ∧
    record.x' = x' ∧
    ∃ n : Nat,
      CarriedRecordAt obstructionStatusPolicy record n
        FineSourceTag.committed_state true true

structure OutOfClassObstructionWitness
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    {C : ChallengeClass} {R : RepairRefinement}
    (obstructionStatusPolicy :
      {candidate :
        CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
          PromotionO0 PromotionO1 Family Probe X Q} ->
        CarriedRecordPolicy S.T (ObstructionStatusRecord (X := X) S candidate))
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q)
    (F : ChallengeClass -> X -> FOut) (r : FOut -> Readout) where
  otherClass : ChallengeClass
  otherClassDistinct : otherClass ≠ C
  x : X
  x' : X
  obstructs : Delta candidate.inducedQuotient (F otherClass) r x x'
  unstatused :
    ¬ ∃ record : ObstructionStatusRecord (X := X) S candidate,
      CarriedObstructionStatusFor S (obstructionStatusPolicy) otherClass
        x x' record

structure DecompilationEventRecord
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    {C : ChallengeClass} {R : RepairRefinement}
    (decompilationEventPolicy : CarriedRecordPolicy S.T DefectRecord)
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q) where
  eventTime : Nat
  revertsRecord : DefectRecord
  revertsMatchesCandidate : revertsRecord = candidate.decompilationRecord
  carried :
    ∃ n : Nat,
      CarriedRecordAt decompilationEventPolicy revertsRecord n
        FineSourceTag.committed_state true true

def CompiledOperatorRecordAttributedTo
    {C : ChallengeClass} {R : RepairRefinement}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (compiledPolicy : CarriedRecordPolicy S.T MoveRecord)
    (_window : CompilationCandidateWindow S H C installs postState R)
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q) : Prop :=
  ∃ n : Nat,
    CarriedRecordAt compiledPolicy candidate.move.moveRecord n
      FineSourceTag.committed_state true true

def ExposedCase
    {C : ChallengeClass} {R : RepairRefinement}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (compiledPolicy : CarriedRecordPolicy S.T MoveRecord)
    (window : CompilationCandidateWindow S H C installs postState R) :
    Prop :=
  ¬ ∃ candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q,
    CompiledOperatorRecordAttributedTo S H compiledPolicy window candidate

def DecompiledCase
    {C : ChallengeClass} {R : RepairRefinement}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (compiledPolicy : CarriedRecordPolicy S.T MoveRecord)
    (decompilationEventPolicy : CarriedRecordPolicy S.T DefectRecord)
    (window : CompilationCandidateWindow S H C installs postState R)
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q) : Prop :=
  ¬ ExposedCase (X := X) (Q := Q)
      (decompilationPolicy := decompilationPolicy)
      (PromotionCarrier := PromotionCarrier) (PromotionO0 := PromotionO0)
      (PromotionO1 := PromotionO1) (Family := Family) (Probe := Probe)
      S H compiledPolicy window ∧
    CompiledOperatorRecordAttributedTo S H compiledPolicy window candidate ∧
    ∃ _event : DecompilationEventRecord S decompilationEventPolicy candidate,
      True

def CompiledCase
    {C : ChallengeClass} {R : RepairRefinement}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (compiledPolicy : CarriedRecordPolicy S.T MoveRecord)
    (decompilationEventPolicy : CarriedRecordPolicy S.T DefectRecord)
    (obstructionStatusPolicy :
      {candidate :
        CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
          PromotionO0 PromotionO1 Family Probe X Q} ->
        CarriedRecordPolicy S.T (ObstructionStatusRecord (X := X) S candidate))
    (window : CompilationCandidateWindow S H C installs postState R)
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q)
    (F : ChallengeClass -> X -> FOut) (r : FOut -> Readout)
    (afterTime : Nat) : Prop :=
  ¬ ExposedCase (X := X) (Q := Q)
      (decompilationPolicy := decompilationPolicy)
      (PromotionCarrier := PromotionCarrier) (PromotionO0 := PromotionO0)
      (PromotionO1 := PromotionO1) (Family := Family) (Probe := Probe)
      S H compiledPolicy window ∧
    ¬ DecompiledCase S H compiledPolicy decompilationEventPolicy window
      candidate ∧
    CompiledOperatorRecordAttributedTo S H compiledPolicy window candidate ∧
    CompilationLawful S candidate ∧
    CompiledDescent S candidate (F C) r ∧
    HigherPackageGoesSilent S H window afterTime ∧
    ¬ ∃ _witness :
      OutOfClassObstructionWitness S obstructionStatusPolicy candidate F r,
      True

def MisCompiledCase
    {C : ChallengeClass} {R : RepairRefinement}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (compiledPolicy : CarriedRecordPolicy S.T MoveRecord)
    (decompilationEventPolicy : CarriedRecordPolicy S.T DefectRecord)
    (obstructionStatusPolicy :
      {candidate :
        CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
          PromotionO0 PromotionO1 Family Probe X Q} ->
        CarriedRecordPolicy S.T (ObstructionStatusRecord (X := X) S candidate))
    (window : CompilationCandidateWindow S H C installs postState R)
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q)
    (F : ChallengeClass -> X -> FOut) (r : FOut -> Readout)
    (afterTime : Nat) : Prop :=
  ¬ ExposedCase (X := X) (Q := Q)
      (decompilationPolicy := decompilationPolicy)
      (PromotionCarrier := PromotionCarrier) (PromotionO0 := PromotionO0)
      (PromotionO1 := PromotionO1) (Family := Family) (Probe := Probe)
      S H compiledPolicy window ∧
    ¬ DecompiledCase S H compiledPolicy decompilationEventPolicy window
      candidate ∧
    CompiledOperatorRecordAttributedTo S H compiledPolicy window candidate ∧
    CompilationLawful S candidate ∧
    CompiledDescent S candidate (F C) r ∧
    HigherPackageGoesSilent S H window afterTime ∧
    ∃ _witness :
      OutOfClassObstructionWitness S obstructionStatusPolicy candidate F r,
      True

def CompilingCase
    {C : ChallengeClass} {R : RepairRefinement}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (compiledPolicy : CarriedRecordPolicy S.T MoveRecord)
    (decompilationEventPolicy : CarriedRecordPolicy S.T DefectRecord)
    (obstructionStatusPolicy :
      {candidate :
        CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
          PromotionO0 PromotionO1 Family Probe X Q} ->
        CarriedRecordPolicy S.T (ObstructionStatusRecord (X := X) S candidate))
    (window : CompilationCandidateWindow S H C installs postState R)
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q)
    (F : ChallengeClass -> X -> FOut) (r : FOut -> Readout)
    (afterTime : Nat) : Prop :=
  ¬ ExposedCase (X := X) (Q := Q)
      (decompilationPolicy := decompilationPolicy)
      (PromotionCarrier := PromotionCarrier) (PromotionO0 := PromotionO0)
      (PromotionO1 := PromotionO1) (Family := Family) (Probe := Probe)
      S H compiledPolicy window ∧
    ¬ DecompiledCase S H compiledPolicy decompilationEventPolicy window
      candidate ∧
    ¬ CompiledCase S H compiledPolicy decompilationEventPolicy
      obstructionStatusPolicy window candidate F r afterTime ∧
    ¬ MisCompiledCase S H compiledPolicy decompilationEventPolicy
      obstructionStatusPolicy window candidate F r afterTime ∧
    CompiledOperatorRecordAttributedTo S H compiledPolicy window candidate

inductive CompilationStatus where
  | exposed
  | decompiled
  | compiled
  | mis_compiled
  | compiling

structure CompilationStatusRecord
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (ChallengeClass : Type z) (RepairRefinement : Type z''''') where
  windowRef : ChallengeClass × RepairRefinement
  candidateRef : Option MoveRecord
  status : CompilationStatus
  supportingLedgerEntries : List LedgerEntry
  supportingAuditRecords : List AuditRecord

def CompilationStatusOccurrenceFor
    {C : ChallengeClass} {R : RepairRefinement}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (statusPolicy :
      CarriedRecordPolicy S.T
        (CompilationStatusRecord S ChallengeClass RepairRefinement))
    (_window : CompilationCandidateWindow S H C installs postState R)
    (candidateOpt :
      Option
        (CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
          PromotionO0 PromotionO1 Family Probe X Q))
    (record : CompilationStatusRecord S ChallengeClass RepairRefinement) :
    Prop :=
  record.windowRef = (C, R) ∧
    record.candidateRef = candidateOpt.map (fun c => c.move.moveRecord) ∧
    (∃ n : Nat,
      CarriedRecordAt statusPolicy record n FineSourceTag.committed_state
        true true) ∧
    (∀ entry : LedgerEntry, entry ∈ record.supportingLedgerEntries ->
      entry ∈ S.Lambda_S.ledgerEntries) ∧
    ∀ auditRecord : AuditRecord, auditRecord ∈ record.supportingAuditRecords ->
      HasCarriedRecordEvidence S.auditRecordPolicy auditRecord

def CompleteCompilationStatus
    {C : ChallengeClass} {R : RepairRefinement}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (compiledPolicy : CarriedRecordPolicy S.T MoveRecord)
    (decompilationEventPolicy : CarriedRecordPolicy S.T DefectRecord)
    (obstructionStatusPolicy :
      {candidate :
        CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
          PromotionO0 PromotionO1 Family Probe X Q} ->
        CarriedRecordPolicy S.T (ObstructionStatusRecord (X := X) S candidate))
    (statusPolicy :
      CarriedRecordPolicy S.T
        (CompilationStatusRecord S ChallengeClass RepairRefinement))
    (window : CompilationCandidateWindow S H C installs postState R)
    (candidateOpt :
      Option
        (CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
          PromotionO0 PromotionO1 Family Probe X Q))
    (F : ChallengeClass -> X -> FOut) (r : FOut -> Readout)
    (afterTime : Nat) : Prop :=
  (∃ record : CompilationStatusRecord S ChallengeClass RepairRefinement,
    CompilationStatusOccurrenceFor S H statusPolicy window candidateOpt record ∧
      match candidateOpt with
      | none =>
          record.status = CompilationStatus.exposed ∧
            ExposedCase (X := X) (Q := Q)
              (decompilationPolicy := decompilationPolicy)
              (PromotionCarrier := PromotionCarrier)
              (PromotionO0 := PromotionO0) (PromotionO1 := PromotionO1)
              (Family := Family) (Probe := Probe) S H compiledPolicy window
      | some candidate =>
          (record.status = CompilationStatus.decompiled ∧
            DecompiledCase S H compiledPolicy decompilationEventPolicy window
              candidate) ∨
          (record.status = CompilationStatus.compiled ∧
            CompiledCase S H compiledPolicy decompilationEventPolicy
              obstructionStatusPolicy window candidate F r afterTime) ∨
          (record.status = CompilationStatus.mis_compiled ∧
            MisCompiledCase S H compiledPolicy decompilationEventPolicy
              obstructionStatusPolicy window candidate F r afterTime) ∨
          (record.status = CompilationStatus.compiling ∧
            CompilingCase S H compiledPolicy decompilationEventPolicy
              obstructionStatusPolicy window candidate F r afterTime)) ∧
    ∀ record1 record2 :
      CompilationStatusRecord S ChallengeClass RepairRefinement,
      CompilationStatusOccurrenceFor S H statusPolicy window candidateOpt
        record1 ->
      CompilationStatusOccurrenceFor S H statusPolicy window candidateOpt
        record2 ->
      record1.status = record2.status

def ExposedHolds
    {C : ChallengeClass} {R : RepairRefinement}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (compiledPolicy : CarriedRecordPolicy S.T MoveRecord)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (CompilationStatusRecord S ChallengeClass RepairRefinement))
    (window : CompilationCandidateWindow S H C installs postState R) :
    Prop :=
  ∃ record : CompilationStatusRecord S ChallengeClass RepairRefinement,
    CompilationStatusOccurrenceFor S H statusPolicy window
      (none :
        Option
          (CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
            PromotionO0 PromotionO1 Family Probe X Q)) record ∧
    record.status = CompilationStatus.exposed ∧
    ExposedCase (X := X) (Q := Q)
      (decompilationPolicy := decompilationPolicy)
      (PromotionCarrier := PromotionCarrier) (PromotionO0 := PromotionO0)
      (PromotionO1 := PromotionO1) (Family := Family) (Probe := Probe)
      S H compiledPolicy window

def DecompiledHolds
    {C : ChallengeClass} {R : RepairRefinement}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (compiledPolicy : CarriedRecordPolicy S.T MoveRecord)
    (decompilationEventPolicy : CarriedRecordPolicy S.T DefectRecord)
    (statusPolicy :
      CarriedRecordPolicy S.T
        (CompilationStatusRecord S ChallengeClass RepairRefinement))
    (window : CompilationCandidateWindow S H C installs postState R)
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q) : Prop :=
  ∃ record : CompilationStatusRecord S ChallengeClass RepairRefinement,
    CompilationStatusOccurrenceFor S H statusPolicy window (some candidate)
      record ∧
    record.status = CompilationStatus.decompiled ∧
    DecompiledCase S H compiledPolicy decompilationEventPolicy window candidate

def CompiledHolds
    {C : ChallengeClass} {R : RepairRefinement}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (compiledPolicy : CarriedRecordPolicy S.T MoveRecord)
    (decompilationEventPolicy : CarriedRecordPolicy S.T DefectRecord)
    (obstructionStatusPolicy :
      {candidate :
        CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
          PromotionO0 PromotionO1 Family Probe X Q} ->
        CarriedRecordPolicy S.T (ObstructionStatusRecord (X := X) S candidate))
    (statusPolicy :
      CarriedRecordPolicy S.T
        (CompilationStatusRecord S ChallengeClass RepairRefinement))
    (window : CompilationCandidateWindow S H C installs postState R)
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q)
    (F : ChallengeClass -> X -> FOut) (r : FOut -> Readout)
    (afterTime : Nat) : Prop :=
  ∃ record : CompilationStatusRecord S ChallengeClass RepairRefinement,
    CompilationStatusOccurrenceFor S H statusPolicy window (some candidate)
      record ∧
    record.status = CompilationStatus.compiled ∧
    CompiledCase S H compiledPolicy decompilationEventPolicy
      obstructionStatusPolicy window candidate F r afterTime

def MisCompiledHolds
    {C : ChallengeClass} {R : RepairRefinement}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (compiledPolicy : CarriedRecordPolicy S.T MoveRecord)
    (decompilationEventPolicy : CarriedRecordPolicy S.T DefectRecord)
    (obstructionStatusPolicy :
      {candidate :
        CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
          PromotionO0 PromotionO1 Family Probe X Q} ->
        CarriedRecordPolicy S.T (ObstructionStatusRecord (X := X) S candidate))
    (statusPolicy :
      CarriedRecordPolicy S.T
        (CompilationStatusRecord S ChallengeClass RepairRefinement))
    (window : CompilationCandidateWindow S H C installs postState R)
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q)
    (F : ChallengeClass -> X -> FOut) (r : FOut -> Readout)
    (afterTime : Nat) : Prop :=
  ∃ record : CompilationStatusRecord S ChallengeClass RepairRefinement,
    CompilationStatusOccurrenceFor S H statusPolicy window (some candidate)
      record ∧
    record.status = CompilationStatus.mis_compiled ∧
    MisCompiledCase S H compiledPolicy decompilationEventPolicy
      obstructionStatusPolicy window candidate F r afterTime

def CompilingHolds
    {C : ChallengeClass} {R : RepairRefinement}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (compiledPolicy : CarriedRecordPolicy S.T MoveRecord)
    (decompilationEventPolicy : CarriedRecordPolicy S.T DefectRecord)
    (obstructionStatusPolicy :
      {candidate :
        CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
          PromotionO0 PromotionO1 Family Probe X Q} ->
        CarriedRecordPolicy S.T (ObstructionStatusRecord (X := X) S candidate))
    (statusPolicy :
      CarriedRecordPolicy S.T
        (CompilationStatusRecord S ChallengeClass RepairRefinement))
    (window : CompilationCandidateWindow S H C installs postState R)
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q)
    (F : ChallengeClass -> X -> FOut) (r : FOut -> Readout)
    (afterTime : Nat) : Prop :=
  ∃ record : CompilationStatusRecord S ChallengeClass RepairRefinement,
    CompilationStatusOccurrenceFor S H statusPolicy window (some candidate)
      record ∧
    record.status = CompilationStatus.compiling ∧
    CompilingCase S H compiledPolicy decompilationEventPolicy
      obstructionStatusPolicy window candidate F r afterTime

end StatusApparatus

section Theorems

universe u1 v1 w1 x1 y1 z1

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
variable {ChallengeClass : Type z} {SourceQuotient : Type z'}
variable {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
variable {ObstructionWitness : Type z''''}
variable {RepairRefinement : Type z'''''}
variable {PromotionCarrier PromotionO0 PromotionO1 : Type}
variable {Family : Type x'} {Probe : Type y'''''}
variable {X : Type w1} {Q : Type x1}
variable {FOut : Type y1} {Readout : Type y'''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
  AuditRecord)
variable (H :
  ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
    TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)

/--
E4's stable-audit scope condition is carried structurally by
`CompilationCandidateWindow.occursAtEach`: every listed invocation is an E1
`EndogenousRepairOccurrence`, whose definition already checks committed source
tag, `generatedByS = true`, and `inScope = true` for the repair audit entry.
-/
theorem E4_Compilation
    {C : ChallengeClass} {R : RepairRefinement}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (compiledPolicy : CarriedRecordPolicy S.T MoveRecord)
    (decompilationEventPolicy : CarriedRecordPolicy S.T DefectRecord)
    (obstructionStatusPolicy :
      {candidate :
        CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
          PromotionO0 PromotionO1 Family Probe X Q} ->
        CarriedRecordPolicy S.T (ObstructionStatusRecord (X := X) S candidate))
    (statusPolicy :
      CarriedRecordPolicy S.T
        (CompilationStatusRecord S ChallengeClass RepairRefinement))
    (window : CompilationCandidateWindow S H C installs postState R)
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q)
    (F : ChallengeClass -> X -> FOut) (r : FOut -> Readout)
    (preQuotient postQuotient : Nat -> X -> Q)
    (_hObstructionReducing :
      ObstructionReducingAcrossWindow S H window preQuotient postQuotient
        (F C) r)
    (measure : IdempotenceDefectMeasure S) (threshold : Rat)
    (_hIdempotenceStable :
      IdempotenceStableAcrossWindow S H measure window threshold)
    (afterTime : Nat)
    (statusRecord : CompilationStatusRecord S ChallengeClass RepairRefinement)
    (hOccurrence :
      CompilationStatusOccurrenceFor S H statusPolicy window
        (some candidate) statusRecord)
    (hStatus : statusRecord.status = CompilationStatus.compiled)
    (hCompiledCase :
      CompiledCase S H compiledPolicy decompilationEventPolicy
        obstructionStatusPolicy window candidate F r afterTime) :
    CompiledHolds S H compiledPolicy decompilationEventPolicy
      obstructionStatusPolicy statusPolicy window candidate F r afterTime := by
  exact ⟨statusRecord, hOccurrence, hStatus, hCompiledCase⟩

theorem E4_Brittleness
    {C : ChallengeClass} {R : RepairRefinement}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (f2 : F2Certified (X := X) (Q := Q) (FOut := FOut)
      (Readout := Readout))
    (candidate :
      CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
        PromotionO0 PromotionO1 Family Probe X Q)
    (F : ChallengeClass -> X -> FOut)
    (r : FOut -> Readout)
    (otherClass : ChallengeClass)
    (_hOutOfClass : otherClass ≠ C)
    (x x' : X)
    (hSplit :
      f2.splitObs
        (f2.minimalGeneratedQuotient candidate.inducedQuotient (F C) r)
        (F otherClass) r x x') :
    ¬ f2.descends
      (f2.minimalGeneratedQuotient candidate.inducedQuotient (F C) r)
      (F otherClass) r := by
  intro hDescends
  have hNoSplit :=
    (f2.descentIffSplitObsEmpty
      (f2.minimalGeneratedQuotient candidate.inducedQuotient (F C) r)
      (F otherClass) r).mpr hDescends
  exact hNoSplit x x' hSplit

theorem E4_StatusPartition
    {C : ChallengeClass} {R : RepairRefinement}
    {installs : MovePayloadInstallsRefinement MovePayload RepairRefinement}
    {postState :
      PostRepairStateForEpisode S ChallengeClass SourceQuotient
        DeclaredFamily TargetReadout ObstructionWitness}
    {decompilationPolicy : CarriedRecordPolicy S.T DefectRecord}
    (compiledPolicy : CarriedRecordPolicy S.T MoveRecord)
    (decompilationEventPolicy : CarriedRecordPolicy S.T DefectRecord)
    (obstructionStatusPolicy :
      {candidate :
        CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
          PromotionO0 PromotionO1 Family Probe X Q} ->
        CarriedRecordPolicy S.T (ObstructionStatusRecord (X := X) S candidate))
    (statusPolicy :
      CarriedRecordPolicy S.T
        (CompilationStatusRecord S ChallengeClass RepairRefinement))
    (window : CompilationCandidateWindow S H C installs postState R)
    (candidateOpt :
      Option
        (CompiledOperatorRecord S decompilationPolicy C R PromotionCarrier
          PromotionO0 PromotionO1 Family Probe X Q))
    (F : ChallengeClass -> X -> FOut) (r : FOut -> Readout)
    (afterTime : Nat)
    (hComplete :
      CompleteCompilationStatus S H compiledPolicy decompilationEventPolicy
        obstructionStatusPolicy statusPolicy window candidateOpt F r afterTime) :
    match candidateOpt with
    | none =>
        ExposedHolds (X := X) (Q := Q)
          (decompilationPolicy := decompilationPolicy)
          (PromotionCarrier := PromotionCarrier)
          (PromotionO0 := PromotionO0) (PromotionO1 := PromotionO1)
          (Family := Family) (Probe := Probe) S H compiledPolicy
          statusPolicy window
    | some candidate =>
        (DecompiledHolds S H compiledPolicy decompilationEventPolicy
          statusPolicy window candidate ∧
          ¬ CompiledHolds S H compiledPolicy decompilationEventPolicy
            obstructionStatusPolicy statusPolicy window candidate F r
            afterTime ∧
          ¬ MisCompiledHolds S H compiledPolicy decompilationEventPolicy
            obstructionStatusPolicy statusPolicy window candidate F r
            afterTime ∧
          ¬ CompilingHolds S H compiledPolicy decompilationEventPolicy
            obstructionStatusPolicy statusPolicy window candidate F r
            afterTime) ∨
        (CompiledHolds S H compiledPolicy decompilationEventPolicy
          obstructionStatusPolicy statusPolicy window candidate F r
          afterTime ∧
          ¬ DecompiledHolds S H compiledPolicy decompilationEventPolicy
            statusPolicy window candidate ∧
          ¬ MisCompiledHolds S H compiledPolicy decompilationEventPolicy
            obstructionStatusPolicy statusPolicy window candidate F r
            afterTime ∧
          ¬ CompilingHolds S H compiledPolicy decompilationEventPolicy
            obstructionStatusPolicy statusPolicy window candidate F r
            afterTime) ∨
        (MisCompiledHolds S H compiledPolicy decompilationEventPolicy
          obstructionStatusPolicy statusPolicy window candidate F r
          afterTime ∧
          ¬ DecompiledHolds S H compiledPolicy decompilationEventPolicy
            statusPolicy window candidate ∧
          ¬ CompiledHolds S H compiledPolicy decompilationEventPolicy
            obstructionStatusPolicy statusPolicy window candidate F r
            afterTime ∧
          ¬ CompilingHolds S H compiledPolicy decompilationEventPolicy
            obstructionStatusPolicy statusPolicy window candidate F r
            afterTime) ∨
        (CompilingHolds S H compiledPolicy decompilationEventPolicy
          obstructionStatusPolicy statusPolicy window candidate F r
          afterTime ∧
          ¬ DecompiledHolds S H compiledPolicy decompilationEventPolicy
            statusPolicy window candidate ∧
          ¬ CompiledHolds S H compiledPolicy decompilationEventPolicy
            obstructionStatusPolicy statusPolicy window candidate F r
            afterTime ∧
          ¬ MisCompiledHolds S H compiledPolicy decompilationEventPolicy
            obstructionStatusPolicy statusPolicy window candidate F r
            afterTime) := by
  cases candidateOpt with
  | none =>
      rcases hComplete.1 with ⟨record, hOccurrence, hBranch⟩
      exact ⟨record, hOccurrence, hBranch.1, hBranch.2⟩
  | some candidate =>
      rcases hComplete.1 with ⟨record, hOccurrence, hBranch⟩
      rcases hBranch with hDecompiled | hRest
      · have hDecompiledHolds :
            DecompiledHolds S H compiledPolicy decompilationEventPolicy
              statusPolicy window candidate :=
          ⟨record, hOccurrence, hDecompiled.1, hDecompiled.2⟩
        have hNotCompiled :
            ¬ CompiledHolds S H compiledPolicy decompilationEventPolicy
              obstructionStatusPolicy statusPolicy window candidate F r
              afterTime := by
          intro hOther
          rcases hOther with
            ⟨_other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
          exact hOtherCase.2.1 hDecompiled.2
        have hNotMisCompiled :
            ¬ MisCompiledHolds S H compiledPolicy decompilationEventPolicy
              obstructionStatusPolicy statusPolicy window candidate F r
              afterTime := by
          intro hOther
          rcases hOther with
            ⟨_other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
          exact hOtherCase.2.1 hDecompiled.2
        have hNotCompiling :
            ¬ CompilingHolds S H compiledPolicy decompilationEventPolicy
              obstructionStatusPolicy statusPolicy window candidate F r
              afterTime := by
          intro hOther
          rcases hOther with
            ⟨_other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
          exact hOtherCase.2.1 hDecompiled.2
        exact Or.inl
          ⟨hDecompiledHolds, hNotCompiled, hNotMisCompiled,
            hNotCompiling⟩
      · rcases hRest with hCompiled | hRest
        · have hCompiledHolds :
              CompiledHolds S H compiledPolicy decompilationEventPolicy
                obstructionStatusPolicy statusPolicy window candidate F r
                afterTime :=
            ⟨record, hOccurrence, hCompiled.1, hCompiled.2⟩
          have hNotDecompiled :
              ¬ DecompiledHolds S H compiledPolicy decompilationEventPolicy
                statusPolicy window candidate := by
            intro hOther
            rcases hOther with
              ⟨_other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
            exact hCompiled.2.2.1 hOtherCase
          have hNotMisCompiled :
              ¬ MisCompiledHolds S H compiledPolicy decompilationEventPolicy
                obstructionStatusPolicy statusPolicy window candidate F r
                afterTime := by
            intro hOther
            rcases hCompiled.2 with
              ⟨_hNotExposed, _hNotDecompiled, _hAttributed, _hLawful,
                _hDescent, _hSilent, hNoOutOfClass⟩
            rcases hOther with
              ⟨_other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
            rcases hOtherCase with
              ⟨_hOtherNotExposed, _hOtherNotDecompiled,
                _hOtherAttributed, _hOtherLawful, _hOtherDescent,
                _hOtherSilent, hOutOfClass⟩
            exact hNoOutOfClass hOutOfClass
          have hNotCompiling :
              ¬ CompilingHolds S H compiledPolicy decompilationEventPolicy
                obstructionStatusPolicy statusPolicy window candidate F r
                afterTime := by
            intro hOther
            rcases hOther with
              ⟨_other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
            exact hOtherCase.2.2.1 hCompiled.2
          exact Or.inr (Or.inl
            ⟨hCompiledHolds, hNotDecompiled, hNotMisCompiled,
              hNotCompiling⟩)
        · rcases hRest with hMisCompiled | hCompiling
          · have hMisCompiledHolds :
                MisCompiledHolds S H compiledPolicy decompilationEventPolicy
                  obstructionStatusPolicy statusPolicy window candidate F r
                  afterTime :=
              ⟨record, hOccurrence, hMisCompiled.1, hMisCompiled.2⟩
            have hNotDecompiled :
                ¬ DecompiledHolds S H compiledPolicy decompilationEventPolicy
                  statusPolicy window candidate := by
              intro hOther
              rcases hOther with
                ⟨_other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              exact hMisCompiled.2.2.1 hOtherCase
            have hNotCompiled :
                ¬ CompiledHolds S H compiledPolicy decompilationEventPolicy
                  obstructionStatusPolicy statusPolicy window candidate F r
                  afterTime := by
              intro hOther
              rcases hMisCompiled.2 with
                ⟨_hNotExposed, _hNotDecompiled, _hAttributed, _hLawful,
                  _hDescent, _hSilent, hOutOfClass⟩
              rcases hOther with
                ⟨_other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              rcases hOtherCase with
                ⟨_hOtherNotExposed, _hOtherNotDecompiled,
                  _hOtherAttributed, _hOtherLawful, _hOtherDescent,
                  _hOtherSilent, hNoOutOfClass⟩
              exact hNoOutOfClass hOutOfClass
            have hNotCompiling :
                ¬ CompilingHolds S H compiledPolicy decompilationEventPolicy
                  obstructionStatusPolicy statusPolicy window candidate F r
                  afterTime := by
              intro hOther
              rcases hOther with
                ⟨_other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              exact hOtherCase.2.2.2.1 hMisCompiled.2
            exact Or.inr (Or.inr (Or.inl
              ⟨hMisCompiledHolds, hNotDecompiled, hNotCompiled,
                hNotCompiling⟩))
          · have hCompilingHolds :
                CompilingHolds S H compiledPolicy decompilationEventPolicy
                  obstructionStatusPolicy statusPolicy window candidate F r
                  afterTime :=
              ⟨record, hOccurrence, hCompiling.1, hCompiling.2⟩
            have hNotDecompiled :
                ¬ DecompiledHolds S H compiledPolicy decompilationEventPolicy
                  statusPolicy window candidate := by
              intro hOther
              rcases hOther with
                ⟨_other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              exact hCompiling.2.2.1 hOtherCase
            have hNotCompiled :
                ¬ CompiledHolds S H compiledPolicy decompilationEventPolicy
                  obstructionStatusPolicy statusPolicy window candidate F r
                  afterTime := by
              intro hOther
              rcases hOther with
                ⟨_other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              exact hCompiling.2.2.2.1 hOtherCase
            have hNotMisCompiled :
                ¬ MisCompiledHolds S H compiledPolicy decompilationEventPolicy
                  obstructionStatusPolicy statusPolicy window candidate F r
                  afterTime := by
              intro hOther
              rcases hOther with
                ⟨_other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              exact hCompiling.2.2.2.2.1 hOtherCase
            exact Or.inr (Or.inr (Or.inr
              ⟨hCompilingHolds, hNotDecompiled, hNotCompiled,
                hNotMisCompiled⟩))

end Theorems

end SixBirdsFoundationsV
