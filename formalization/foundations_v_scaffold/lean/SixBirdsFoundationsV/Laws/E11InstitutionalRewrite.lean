import SixBirdsFoundationsV.Definitional.ESystem
import SixBirdsIII.TopDownChannel

namespace SixBirdsFoundationsV

/-!
E11 institutional rewrite setup.

This setup layer introduces the Foundations-V institutional comparison and
support/closure comparator surface while directly reusing the vendored FIII
`SixBirdsIII.TopDownChannel` declarations.  The four-way rewrite status
apparatus and E11 theorem statements are intentionally left to later
mechanization subsections.
-/

structure InstitutionLabelRecord where
  recordId : Nat
  deriving DecidableEq, Repr

structure InstitutionInterventionRecord where
  recordId : Nat
  deriving DecidableEq, Repr

structure MatchedComparisonRecord where
  recordId : Nat
  deriving DecidableEq, Repr

structure InstitutionalEffectRecord where
  recordId : Nat
  deriving DecidableEq, Repr

structure ParameterEffectRecord where
  recordId : Nat
  deriving DecidableEq, Repr

structure CompiledRewriteRecord where
  recordId : Nat
  deriving DecidableEq, Repr

structure InstitutionalLabel where
  labelId : Nat
  deriving DecidableEq, Repr

structure LowerContextRecord where
  recordId : Nat
  deriving DecidableEq, Repr

structure UncontrolledDifferenceRecord where
  recordId : Nat
  deriving DecidableEq, Repr

structure LowerClosureSignature where
  signatureId : Nat
  deriving DecidableEq, Repr

structure LowerClosureDifferenceRecord where
  recordId : Nat
  deriving DecidableEq, Repr

structure InstitutionalOutcomeReadout where
  readoutId : Nat
  deriving DecidableEq, Repr

structure InstitutionalIntervention
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  labelRecord : InstitutionLabelRecord
  interventionRecord : InstitutionInterventionRecord
  labelValue : InstitutionalLabel
  lowerState : S.T.Z
  sourceTag : FineSourceTag
  generatedByS : Bool
  inScope : Bool
  usedLedgerEntries : List LedgerEntry
  usedAuditRecords : List AuditRecord

def InstitutionalInterventionOccurrenceFor
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (labelPolicy : CarriedRecordPolicy S.T InstitutionLabelRecord)
    (interventionPolicy :
      CarriedRecordPolicy S.T InstitutionInterventionRecord)
    (theta : InstitutionalIntervention S) : Prop :=
  (∃ nLabel nIntervention : Nat,
    CarriedRecordAt labelPolicy theta.labelRecord nLabel
      theta.sourceTag theta.generatedByS theta.inScope ∧
    CarriedRecordAt interventionPolicy theta.interventionRecord
      nIntervention theta.sourceTag theta.generatedByS theta.inScope) ∧
    (theta.sourceTag = FineSourceTag.committed_state ∨
      theta.sourceTag = FineSourceTag.audited_cell_records) ∧
    theta.generatedByS = true ∧
    theta.inScope = true ∧
    (∀ entry : LedgerEntry, entry ∈ theta.usedLedgerEntries ->
      entry ∈ S.Lambda_S.ledgerEntries) ∧
    ∀ auditRecord : AuditRecord, auditRecord ∈ theta.usedAuditRecords ->
      HasCarriedRecordEvidence S.auditRecordPolicy auditRecord

def DistinctInstitutionalInterventions
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (theta_i theta_j : InstitutionalIntervention S) : Prop :=
  theta_i.labelValue ≠ theta_j.labelValue ∧
    theta_i.interventionRecord ≠ theta_j.interventionRecord

structure MatchedInstitutionalComparison
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  comparisonRecord : MatchedComparisonRecord
  theta_i : InstitutionalIntervention S
  theta_j : InstitutionalIntervention S
  channelRecord : SixBirdsIII.TopDownChannelRecord
  matchedControlsRecord : AuditRecord
  controlledLowerContext : LowerContextRecord
  uncontrolledDifferenceWitness : Option UncontrolledDifferenceRecord

def MatchedControlsComparison
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (labelPolicy : CarriedRecordPolicy S.T InstitutionLabelRecord)
    (interventionPolicy :
      CarriedRecordPolicy S.T InstitutionInterventionRecord)
    (comparisonPolicy : CarriedRecordPolicy S.T MatchedComparisonRecord)
    (comparison : MatchedInstitutionalComparison S) : Prop :=
  InstitutionalInterventionOccurrenceFor S labelPolicy interventionPolicy
    comparison.theta_i ∧
    InstitutionalInterventionOccurrenceFor S labelPolicy interventionPolicy
      comparison.theta_j ∧
    DistinctInstitutionalInterventions comparison.theta_i
      comparison.theta_j ∧
    (∃ n0 : Nat,
      CarriedRecordAt comparisonPolicy comparison.comparisonRecord n0
        FineSourceTag.committed_state true true) ∧
    HasCarriedRecordEvidence S.auditRecordPolicy
      comparison.matchedControlsRecord ∧
    comparison.uncontrolledDifferenceWitness = none ∧
    comparison.channelRecord.matchedControlsGate = true

/--
Certified host fact that institutional labels are static/per-path for a
comparison.  Used later by the washout branch; E11 does not derive it locally.
-/
structure StaticInstitutionalLabels
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  holds : MatchedInstitutionalComparison S -> Prop

/--
Certified host fact that behavior is base-independent for a comparison.
-/
structure BaseIndependentBehavior
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  holds : MatchedInstitutionalComparison S -> Prop

/--
Certified host fact for strict lower predictive refinement under live labels.
-/
structure StrictInstitutionalRefinement
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  holds : MatchedInstitutionalComparison S -> Prop

structure LowerKernelSupportComparator
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  supportUnder : InstitutionalIntervention S -> S.T.Z -> S.T.Z -> Prop
  agreesWithCarrier :
    ∀ theta z z', supportUnder theta z z' -> S.T.suppK z z'
  finiteComparator : Prop
  finiteComparatorCertified : finiteComparator

def KernelSupportDiffers
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (comparator : LowerKernelSupportComparator S)
    (theta_i theta_j : InstitutionalIntervention S) : Prop :=
  ∃ z z' : S.T.Z,
    comparator.supportUnder theta_i z z' ≠
      comparator.supportUnder theta_j z z'

structure LowerClosureComparator
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  closureUnder : InstitutionalIntervention S -> LowerClosureSignature
  finiteComparator : Prop
  finiteComparatorCertified : finiteComparator

def ClosureDiffers
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (closureComparator : LowerClosureComparator S)
    (theta_i theta_j : InstitutionalIntervention S) : Prop :=
  closureComparator.closureUnder theta_i ≠
    closureComparator.closureUnder theta_j

structure LowerParameterComparator
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  parametersDiffer :
    InstitutionalIntervention S -> InstitutionalIntervention S -> Prop
  supportUnchanged :
    LowerKernelSupportComparator S ->
      InstitutionalIntervention S -> InstitutionalIntervention S -> Prop
  closureUnchanged :
    LowerClosureComparator S ->
      InstitutionalIntervention S -> InstitutionalIntervention S -> Prop

def ParameterConditioningOnly
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (parameterComparator : LowerParameterComparator S)
    (supportComparator : LowerKernelSupportComparator S)
    (closureComparator : LowerClosureComparator S)
    (theta_i theta_j : InstitutionalIntervention S) : Prop :=
  parameterComparator.parametersDiffer theta_i theta_j ∧
    parameterComparator.supportUnchanged supportComparator theta_i theta_j ∧
    parameterComparator.closureUnchanged closureComparator theta_i theta_j ∧
    ¬ KernelSupportDiffers supportComparator theta_i theta_j ∧
    ¬ ClosureDiffers closureComparator theta_i theta_j

def TopDownChannelRecordCarriedAt
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (channelPolicy :
      CarriedRecordPolicy S.T SixBirdsIII.TopDownChannelRecord)
    (channelRecord : SixBirdsIII.TopDownChannelRecord)
    (n0 : Nat) (sourceTag : FineSourceTag)
    (generatedByS inScope : Bool) : Prop :=
  CarriedRecordAt channelPolicy channelRecord n0 sourceTag generatedByS
    inScope

structure InstitutionalStructuralEffect
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  effectRecord : InstitutionalEffectRecord
  comparisonRecord : MatchedComparisonRecord
  channelRecord : SixBirdsIII.TopDownChannelRecord
  observedOutcome : InstitutionalOutcomeReadout
  supportWitness : Option (S.T.Z × S.T.Z)
  closureWitness : Option LowerClosureDifferenceRecord

structure InstitutionalParameterEffect where
  parameterRecord : ParameterEffectRecord
  comparisonRecord : MatchedComparisonRecord
  observedOutcome : InstitutionalOutcomeReadout

def ReproducesClaimedEffect
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord}
    (parameterEffect : InstitutionalParameterEffect)
    (structuralEffect : InstitutionalStructuralEffect S) : Prop :=
  parameterEffect.observedOutcome = structuralEffect.observedOutcome

def StructuralEffectFor
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (labelPolicy : CarriedRecordPolicy S.T InstitutionLabelRecord)
    (interventionPolicy :
      CarriedRecordPolicy S.T InstitutionInterventionRecord)
    (comparisonPolicy : CarriedRecordPolicy S.T MatchedComparisonRecord)
    (effectPolicy : CarriedRecordPolicy S.T InstitutionalEffectRecord)
    (channelPolicy :
      CarriedRecordPolicy S.T SixBirdsIII.TopDownChannelRecord)
    (supportComparator : LowerKernelSupportComparator S)
    (closureComparator : LowerClosureComparator S)
    (comparison : MatchedInstitutionalComparison S)
    (channelRecord : SixBirdsIII.TopDownChannelRecord)
    (effect : InstitutionalStructuralEffect S) : Prop :=
  MatchedControlsComparison S labelPolicy interventionPolicy
    comparisonPolicy comparison ∧
    comparison.channelRecord = channelRecord ∧
    effect.comparisonRecord = comparison.comparisonRecord ∧
    effect.channelRecord = channelRecord ∧
    (∃ nEffect : Nat,
      CarriedRecordAt effectPolicy effect.effectRecord nEffect
        FineSourceTag.committed_state true true) ∧
    (∃ nChannel : Nat,
      TopDownChannelRecordCarriedAt channelPolicy channelRecord nChannel
        FineSourceTag.committed_state true true) ∧
    SixBirdsIII.TopDownChannelAcceptedBool channelRecord = true ∧
    channelRecord.effectGate = true ∧
    ((∃ z z' : S.T.Z,
      effect.supportWitness = some (z, z') ∧
      supportComparator.supportUnder comparison.theta_i z z' ≠
        supportComparator.supportUnder comparison.theta_j z z') ∨
    (∃ closureDiff : LowerClosureDifferenceRecord,
      effect.closureWitness = some closureDiff ∧
      ClosureDiffers closureComparator comparison.theta_i
        comparison.theta_j))

def Delta_stack
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (labelPolicy : CarriedRecordPolicy S.T InstitutionLabelRecord)
    (interventionPolicy :
      CarriedRecordPolicy S.T InstitutionInterventionRecord)
    (comparisonPolicy : CarriedRecordPolicy S.T MatchedComparisonRecord)
    (parameterPolicy : CarriedRecordPolicy S.T ParameterEffectRecord)
    (parameterComparator : LowerParameterComparator S)
    (supportComparator : LowerKernelSupportComparator S)
    (closureComparator : LowerClosureComparator S)
    (comparison : MatchedInstitutionalComparison S)
    (effect : InstitutionalStructuralEffect S)
    (parameterComparison : MatchedInstitutionalComparison S)
    (parameterEffect : InstitutionalParameterEffect) : Prop :=
  MatchedControlsComparison S labelPolicy interventionPolicy
    comparisonPolicy comparison ∧
    effect.comparisonRecord = comparison.comparisonRecord ∧
    MatchedControlsComparison S labelPolicy interventionPolicy
      comparisonPolicy parameterComparison ∧
    parameterEffect.comparisonRecord =
      parameterComparison.comparisonRecord ∧
    (∃ nParameter : Nat,
      CarriedRecordAt parameterPolicy parameterEffect.parameterRecord
        nParameter FineSourceTag.committed_state true true) ∧
    ParameterConditioningOnly parameterComparator supportComparator
      closureComparator parameterComparison.theta_i
      parameterComparison.theta_j ∧
    ReproducesClaimedEffect parameterEffect effect

def DeltaStackEmptyFor
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (labelPolicy : CarriedRecordPolicy S.T InstitutionLabelRecord)
    (interventionPolicy :
      CarriedRecordPolicy S.T InstitutionInterventionRecord)
    (comparisonPolicy : CarriedRecordPolicy S.T MatchedComparisonRecord)
    (parameterPolicy : CarriedRecordPolicy S.T ParameterEffectRecord)
    (parameterComparator : LowerParameterComparator S)
    (supportComparator : LowerKernelSupportComparator S)
    (closureComparator : LowerClosureComparator S)
    (comparison : MatchedInstitutionalComparison S)
    (effect : InstitutionalStructuralEffect S) : Prop :=
  ¬ ∃ parameterComparison : MatchedInstitutionalComparison S,
      ∃ parameterEffect : InstitutionalParameterEffect,
        Delta_stack S labelPolicy interventionPolicy comparisonPolicy
          parameterPolicy parameterComparator supportComparator
          closureComparator comparison effect parameterComparison
          parameterEffect

/--
Certified forward interface for E4's not-yet-landed compilation refinement.
ForwardObligation(E4_constitutive_compilation_correspondence).
-/
structure E4CompiledInstitutionalRewrite
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  compiledRecordFor :
    MatchedInstitutionalComparison S ->
    SixBirdsIII.TopDownChannelRecord ->
    InstitutionalStructuralEffect S -> CompiledRewriteRecord
  holds :
    MatchedInstitutionalComparison S ->
    SixBirdsIII.TopDownChannelRecord ->
    InstitutionalStructuralEffect S -> Prop

inductive InstitutionalRewriteStatus where
  | inert
  | conditioning
  | stack_active
  | constitutive
  deriving DecidableEq, Repr

structure InstitutionalRewriteStatusRecord
    (LedgerEntry : Type u) (AuditRecord : Type v) where
  comparisonRecord : MatchedComparisonRecord
  status : InstitutionalRewriteStatus
  channelRecord : Option SixBirdsIII.TopDownChannelRecord
  effectRecord : Option InstitutionalEffectRecord
  parameterRecord : Option ParameterEffectRecord
  compiledRecord : Option CompiledRewriteRecord
  supportingLedgerEntries : List LedgerEntry
  supportingAuditRecords : List AuditRecord

section StatusApparatus

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
  AuditRecord)
variable (labelPolicy : CarriedRecordPolicy S.T InstitutionLabelRecord)
variable (interventionPolicy :
  CarriedRecordPolicy S.T InstitutionInterventionRecord)
variable (comparisonPolicy : CarriedRecordPolicy S.T MatchedComparisonRecord)
variable (effectPolicy : CarriedRecordPolicy S.T InstitutionalEffectRecord)
variable (parameterPolicy : CarriedRecordPolicy S.T ParameterEffectRecord)
variable (compiledPolicy : CarriedRecordPolicy S.T CompiledRewriteRecord)
variable (channelPolicy :
  CarriedRecordPolicy S.T SixBirdsIII.TopDownChannelRecord)
variable (statusPolicy :
  CarriedRecordPolicy S.T
    (InstitutionalRewriteStatusRecord LedgerEntry AuditRecord))
variable (staticLabels : StaticInstitutionalLabels S)
variable (baseIndependent : BaseIndependentBehavior S)
variable (strictRefinement : StrictInstitutionalRefinement S)
variable (parameterComparator : LowerParameterComparator S)
variable (supportComparator : LowerKernelSupportComparator S)
variable (closureComparator : LowerClosureComparator S)
variable (e4Compiled : E4CompiledInstitutionalRewrite S)

def InstitutionalRewriteStatusOccurrenceFor
    (comparison : MatchedInstitutionalComparison S)
    (record :
      InstitutionalRewriteStatusRecord LedgerEntry AuditRecord) : Prop :=
  MatchedControlsComparison S labelPolicy interventionPolicy
    comparisonPolicy comparison ∧
    record.comparisonRecord = comparison.comparisonRecord ∧
    (∃ n0 : Nat,
      CarriedRecordAt statusPolicy record n0 FineSourceTag.committed_state
        true true) ∧
    (∀ entry : LedgerEntry, entry ∈ record.supportingLedgerEntries ->
      entry ∈ S.Lambda_S.ledgerEntries) ∧
    ∀ auditRecord : AuditRecord, auditRecord ∈ record.supportingAuditRecords ->
      HasCarriedRecordEvidence S.auditRecordPolicy auditRecord

def WashoutNull
    (comparison : MatchedInstitutionalComparison S) : Prop :=
  staticLabels.holds comparison ∧
    baseIndependent.holds comparison ∧
    ¬ strictRefinement.holds comparison ∧
    ¬ ParameterConditioningOnly parameterComparator supportComparator
      closureComparator comparison.theta_i comparison.theta_j ∧
    ¬ ∃ channelRecord : SixBirdsIII.TopDownChannelRecord,
      ∃ effect : InstitutionalStructuralEffect S,
        StructuralEffectFor S labelPolicy interventionPolicy
          comparisonPolicy effectPolicy channelPolicy supportComparator
          closureComparator comparison channelRecord effect

def NCTDControl
    (channelRecord : SixBirdsIII.TopDownChannelRecord) : Prop :=
  SixBirdsIII.StructDown channelRecord ∧
    SixBirdsIII.TopDownChannelClaimStatus channelRecord =
      SixBirdsIII.ClaimStatus.blocked

def InertEvidence
    (comparison : MatchedInstitutionalComparison S) : Prop :=
  MatchedControlsComparison S labelPolicy interventionPolicy
    comparisonPolicy comparison ∧
    (WashoutNull S labelPolicy interventionPolicy comparisonPolicy
        effectPolicy channelPolicy staticLabels baseIndependent
        strictRefinement parameterComparator supportComparator
        closureComparator comparison ∨
      (¬ ParameterConditioningOnly parameterComparator supportComparator
          closureComparator comparison.theta_i comparison.theta_j ∧
        ¬ ∃ channelRecord : SixBirdsIII.TopDownChannelRecord,
          ∃ effect : InstitutionalStructuralEffect S,
            StructuralEffectFor S labelPolicy interventionPolicy
              comparisonPolicy effectPolicy channelPolicy supportComparator
              closureComparator comparison channelRecord effect))

def ConditioningEvidence
    (comparison : MatchedInstitutionalComparison S)
    (parameterEffect : InstitutionalParameterEffect) : Prop :=
  MatchedControlsComparison S labelPolicy interventionPolicy
    comparisonPolicy comparison ∧
    parameterEffect.comparisonRecord = comparison.comparisonRecord ∧
    (∃ nParameter : Nat,
      CarriedRecordAt parameterPolicy parameterEffect.parameterRecord
        nParameter FineSourceTag.committed_state true true) ∧
    ParameterConditioningOnly parameterComparator supportComparator
      closureComparator comparison.theta_i comparison.theta_j ∧
    ¬ ∃ channelRecord : SixBirdsIII.TopDownChannelRecord,
      ∃ effect : InstitutionalStructuralEffect S,
        StructuralEffectFor S labelPolicy interventionPolicy
          comparisonPolicy effectPolicy channelPolicy supportComparator
          closureComparator comparison channelRecord effect

def ConstitutiveEvidence
    (comparison : MatchedInstitutionalComparison S)
    (channelRecord : SixBirdsIII.TopDownChannelRecord)
    (effect : InstitutionalStructuralEffect S)
    (compiledRecord : CompiledRewriteRecord) : Prop :=
  StructuralEffectFor S labelPolicy interventionPolicy comparisonPolicy
    effectPolicy channelPolicy supportComparator closureComparator
    comparison channelRecord effect ∧
    DeltaStackEmptyFor S labelPolicy interventionPolicy comparisonPolicy
      parameterPolicy parameterComparator supportComparator closureComparator
      comparison effect ∧
    e4Compiled.holds comparison channelRecord effect ∧
    (∃ nCompiled : Nat,
      CarriedRecordAt compiledPolicy compiledRecord nCompiled
        FineSourceTag.committed_state true true) ∧
    compiledRecord =
      e4Compiled.compiledRecordFor comparison channelRecord effect

def ConstitutiveEvidenceExistsFor
    (comparison : MatchedInstitutionalComparison S) : Prop :=
  ∃ channelRecord : SixBirdsIII.TopDownChannelRecord,
    ∃ effect : InstitutionalStructuralEffect S,
      ∃ compiledRecord : CompiledRewriteRecord,
        ConstitutiveEvidence S labelPolicy interventionPolicy
          comparisonPolicy effectPolicy parameterPolicy compiledPolicy
          channelPolicy parameterComparator supportComparator
          closureComparator e4Compiled comparison channelRecord effect
          compiledRecord

def StackActiveEvidence
    (comparison : MatchedInstitutionalComparison S)
    (channelRecord : SixBirdsIII.TopDownChannelRecord)
    (effect : InstitutionalStructuralEffect S) : Prop :=
  StructuralEffectFor S labelPolicy interventionPolicy comparisonPolicy
    effectPolicy channelPolicy supportComparator closureComparator
    comparison channelRecord effect ∧
    DeltaStackEmptyFor S labelPolicy interventionPolicy comparisonPolicy
      parameterPolicy parameterComparator supportComparator closureComparator
      comparison effect ∧
    ¬ ConstitutiveEvidenceExistsFor S labelPolicy interventionPolicy
      comparisonPolicy effectPolicy parameterPolicy compiledPolicy
      channelPolicy parameterComparator supportComparator closureComparator
      e4Compiled comparison

def InertCase
    (comparison : MatchedInstitutionalComparison S)
    (record :
      InstitutionalRewriteStatusRecord LedgerEntry AuditRecord) : Prop :=
  InstitutionalRewriteStatusOccurrenceFor S labelPolicy interventionPolicy
    comparisonPolicy statusPolicy comparison record ∧
    record.status = InstitutionalRewriteStatus.inert ∧
    record.channelRecord = none ∧
    record.effectRecord = none ∧
    record.parameterRecord = none ∧
    record.compiledRecord = none ∧
    InertEvidence S labelPolicy interventionPolicy comparisonPolicy
      effectPolicy channelPolicy staticLabels baseIndependent
      strictRefinement parameterComparator supportComparator
      closureComparator comparison

def ConditioningCase
    (comparison : MatchedInstitutionalComparison S)
    (record :
      InstitutionalRewriteStatusRecord LedgerEntry AuditRecord) : Prop :=
  ∃ parameterEffect : InstitutionalParameterEffect,
    InstitutionalRewriteStatusOccurrenceFor S labelPolicy interventionPolicy
      comparisonPolicy statusPolicy comparison record ∧
      record.status = InstitutionalRewriteStatus.conditioning ∧
      record.channelRecord = none ∧
      record.parameterRecord = some parameterEffect.parameterRecord ∧
      record.effectRecord = none ∧
      record.compiledRecord = none ∧
      ConditioningEvidence S labelPolicy interventionPolicy
        comparisonPolicy effectPolicy parameterPolicy channelPolicy
        parameterComparator supportComparator closureComparator comparison
        parameterEffect

def StackActiveCase
    (comparison : MatchedInstitutionalComparison S)
    (record :
      InstitutionalRewriteStatusRecord LedgerEntry AuditRecord) : Prop :=
  ∃ channelRecord : SixBirdsIII.TopDownChannelRecord,
    ∃ effect : InstitutionalStructuralEffect S,
      InstitutionalRewriteStatusOccurrenceFor S labelPolicy
        interventionPolicy comparisonPolicy statusPolicy comparison record ∧
      record.status = InstitutionalRewriteStatus.stack_active ∧
      record.channelRecord = some channelRecord ∧
      record.effectRecord = some effect.effectRecord ∧
      record.parameterRecord = none ∧
      record.compiledRecord = none ∧
      StackActiveEvidence S labelPolicy interventionPolicy
        comparisonPolicy effectPolicy parameterPolicy compiledPolicy
        channelPolicy parameterComparator supportComparator closureComparator
        e4Compiled comparison channelRecord effect

def ConstitutiveCase
    (comparison : MatchedInstitutionalComparison S)
    (record :
      InstitutionalRewriteStatusRecord LedgerEntry AuditRecord) : Prop :=
  ∃ channelRecord : SixBirdsIII.TopDownChannelRecord,
    ∃ effect : InstitutionalStructuralEffect S,
      ∃ compiledRecord : CompiledRewriteRecord,
        InstitutionalRewriteStatusOccurrenceFor S labelPolicy
          interventionPolicy comparisonPolicy statusPolicy comparison
          record ∧
        record.status = InstitutionalRewriteStatus.constitutive ∧
        record.channelRecord = some channelRecord ∧
        record.effectRecord = some effect.effectRecord ∧
        record.parameterRecord = none ∧
        record.compiledRecord = some compiledRecord ∧
        ConstitutiveEvidence S labelPolicy interventionPolicy
          comparisonPolicy effectPolicy parameterPolicy compiledPolicy
          channelPolicy parameterComparator supportComparator
          closureComparator e4Compiled comparison channelRecord effect
          compiledRecord

def InertHolds
    (comparison : MatchedInstitutionalComparison S) : Prop :=
  ∃ record : InstitutionalRewriteStatusRecord LedgerEntry AuditRecord,
    InertCase S labelPolicy interventionPolicy comparisonPolicy
      effectPolicy channelPolicy statusPolicy staticLabels baseIndependent
      strictRefinement parameterComparator supportComparator
      closureComparator comparison record

def ConditioningHolds
    (comparison : MatchedInstitutionalComparison S) : Prop :=
  ∃ record : InstitutionalRewriteStatusRecord LedgerEntry AuditRecord,
    ConditioningCase S labelPolicy interventionPolicy comparisonPolicy
      effectPolicy parameterPolicy channelPolicy statusPolicy
      parameterComparator supportComparator closureComparator comparison
      record

def StackActiveHolds
    (comparison : MatchedInstitutionalComparison S) : Prop :=
  ∃ record : InstitutionalRewriteStatusRecord LedgerEntry AuditRecord,
    StackActiveCase S labelPolicy interventionPolicy comparisonPolicy
      effectPolicy parameterPolicy compiledPolicy channelPolicy
      statusPolicy parameterComparator supportComparator closureComparator
      e4Compiled comparison record

def ConstitutiveHolds
    (comparison : MatchedInstitutionalComparison S) : Prop :=
  ∃ record : InstitutionalRewriteStatusRecord LedgerEntry AuditRecord,
    ConstitutiveCase S labelPolicy interventionPolicy comparisonPolicy
      effectPolicy parameterPolicy compiledPolicy channelPolicy
      statusPolicy parameterComparator supportComparator closureComparator
      e4Compiled comparison record

def CompleteInstitutionalRewriteStatus
    (comparison : MatchedInstitutionalComparison S) : Prop :=
  (∃ record : InstitutionalRewriteStatusRecord LedgerEntry AuditRecord,
    InstitutionalRewriteStatusOccurrenceFor S labelPolicy interventionPolicy
      comparisonPolicy statusPolicy comparison record ∧
      (InertCase S labelPolicy interventionPolicy comparisonPolicy
          effectPolicy channelPolicy statusPolicy staticLabels
          baseIndependent strictRefinement parameterComparator
          supportComparator closureComparator comparison record ∨
        ConditioningCase S labelPolicy interventionPolicy
          comparisonPolicy effectPolicy parameterPolicy channelPolicy
          statusPolicy parameterComparator supportComparator
          closureComparator comparison record ∨
        StackActiveCase S labelPolicy interventionPolicy
          comparisonPolicy effectPolicy parameterPolicy compiledPolicy
          channelPolicy statusPolicy parameterComparator supportComparator
          closureComparator e4Compiled comparison record ∨
        ConstitutiveCase S labelPolicy interventionPolicy
          comparisonPolicy effectPolicy parameterPolicy compiledPolicy
          channelPolicy statusPolicy parameterComparator supportComparator
          closureComparator e4Compiled comparison record)) ∧
    ∀ record1 record2 :
      InstitutionalRewriteStatusRecord LedgerEntry AuditRecord,
      InstitutionalRewriteStatusOccurrenceFor S labelPolicy
        interventionPolicy comparisonPolicy statusPolicy comparison
        record1 ->
      InstitutionalRewriteStatusOccurrenceFor S labelPolicy
        interventionPolicy comparisonPolicy statusPolicy comparison
        record2 ->
      record1.status = record2.status

end StatusApparatus

section Theorems

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
  AuditRecord)
variable (labelPolicy : CarriedRecordPolicy S.T InstitutionLabelRecord)
variable (interventionPolicy :
  CarriedRecordPolicy S.T InstitutionInterventionRecord)
variable (comparisonPolicy : CarriedRecordPolicy S.T MatchedComparisonRecord)
variable (effectPolicy : CarriedRecordPolicy S.T InstitutionalEffectRecord)
variable (parameterPolicy : CarriedRecordPolicy S.T ParameterEffectRecord)
variable (compiledPolicy : CarriedRecordPolicy S.T CompiledRewriteRecord)
variable (channelPolicy :
  CarriedRecordPolicy S.T SixBirdsIII.TopDownChannelRecord)
variable (statusPolicy :
  CarriedRecordPolicy S.T
    (InstitutionalRewriteStatusRecord LedgerEntry AuditRecord))
variable (staticLabels : StaticInstitutionalLabels S)
variable (baseIndependent : BaseIndependentBehavior S)
variable (strictRefinement : StrictInstitutionalRefinement S)
variable (parameterComparator : LowerParameterComparator S)
variable (supportComparator : LowerKernelSupportComparator S)
variable (closureComparator : LowerClosureComparator S)
variable (e4Compiled : E4CompiledInstitutionalRewrite S)

theorem E11_StackActivity
    (comparison : MatchedInstitutionalComparison S)
    (channelRecord : SixBirdsIII.TopDownChannelRecord)
    (effect : InstitutionalStructuralEffect S)
    (statusRecord :
      InstitutionalRewriteStatusRecord LedgerEntry AuditRecord)
    (_hMatched :
      MatchedControlsComparison S labelPolicy interventionPolicy
        comparisonPolicy comparison)
    (hStructural :
      StructuralEffectFor S labelPolicy interventionPolicy comparisonPolicy
        effectPolicy channelPolicy supportComparator closureComparator
        comparison channelRecord effect)
    (hDelta :
      DeltaStackEmptyFor S labelPolicy interventionPolicy comparisonPolicy
        parameterPolicy parameterComparator supportComparator
        closureComparator comparison effect)
    (hNoConstitutive :
      ¬ ConstitutiveEvidenceExistsFor S labelPolicy interventionPolicy
        comparisonPolicy effectPolicy parameterPolicy compiledPolicy
        channelPolicy parameterComparator supportComparator closureComparator
        e4Compiled comparison)
    (hStatusOccurrence :
      InstitutionalRewriteStatusOccurrenceFor S labelPolicy interventionPolicy
        comparisonPolicy statusPolicy comparison statusRecord)
    (hStatus :
      statusRecord.status = InstitutionalRewriteStatus.stack_active)
    (hChannel :
      statusRecord.channelRecord = some channelRecord)
    (hEffect :
      statusRecord.effectRecord = some effect.effectRecord)
    (hParameter : statusRecord.parameterRecord = none)
    (hCompiled : statusRecord.compiledRecord = none) :
    StackActiveHolds S labelPolicy interventionPolicy comparisonPolicy
      effectPolicy parameterPolicy compiledPolicy channelPolicy statusPolicy
      parameterComparator supportComparator closureComparator e4Compiled
      comparison := by
  refine ⟨statusRecord, ?_⟩
  refine ⟨channelRecord, effect, ?_⟩
  exact ⟨hStatusOccurrence, hStatus, hChannel, hEffect, hParameter,
    hCompiled, hStructural, hDelta, hNoConstitutive⟩

theorem E11_Constitutive
    (comparison : MatchedInstitutionalComparison S)
    (channelRecord : SixBirdsIII.TopDownChannelRecord)
    (effect : InstitutionalStructuralEffect S)
    (compiledRecord : CompiledRewriteRecord)
    (nCompiled : Nat)
    (statusRecord :
      InstitutionalRewriteStatusRecord LedgerEntry AuditRecord)
    (_hMatched :
      MatchedControlsComparison S labelPolicy interventionPolicy
        comparisonPolicy comparison)
    (hStructural :
      StructuralEffectFor S labelPolicy interventionPolicy comparisonPolicy
        effectPolicy channelPolicy supportComparator closureComparator
        comparison channelRecord effect)
    (hDelta :
      DeltaStackEmptyFor S labelPolicy interventionPolicy comparisonPolicy
        parameterPolicy parameterComparator supportComparator
        closureComparator comparison effect)
    (hE4 : e4Compiled.holds comparison channelRecord effect)
    (hStatusOccurrence :
      InstitutionalRewriteStatusOccurrenceFor S labelPolicy interventionPolicy
        comparisonPolicy statusPolicy comparison statusRecord)
    (hStatus :
      statusRecord.status = InstitutionalRewriteStatus.constitutive)
    (hChannel :
      statusRecord.channelRecord = some channelRecord)
    (hEffect :
      statusRecord.effectRecord = some effect.effectRecord)
    (hParameter : statusRecord.parameterRecord = none)
    (hCompiledField : statusRecord.compiledRecord = some compiledRecord)
    (hCompiledCarried :
      CarriedRecordAt compiledPolicy compiledRecord nCompiled
        FineSourceTag.committed_state true true)
    (hCompiledEq :
      compiledRecord =
        e4Compiled.compiledRecordFor comparison channelRecord effect) :
    ConstitutiveHolds S labelPolicy interventionPolicy comparisonPolicy
      effectPolicy parameterPolicy compiledPolicy channelPolicy statusPolicy
      parameterComparator supportComparator closureComparator e4Compiled
      comparison := by
  refine ⟨statusRecord, ?_⟩
  refine ⟨channelRecord, effect, compiledRecord, ?_⟩
  exact ⟨hStatusOccurrence, hStatus, hChannel, hEffect, hParameter,
    hCompiledField, hStructural, hDelta, hE4,
    ⟨nCompiled, hCompiledCarried⟩, hCompiledEq⟩

theorem E11_ConditioningOnly
    (comparison : MatchedInstitutionalComparison S)
    (parameterEffect : InstitutionalParameterEffect)
    (nParameter : Nat)
    (statusRecord :
      InstitutionalRewriteStatusRecord LedgerEntry AuditRecord)
    (_hMatched :
      MatchedControlsComparison S labelPolicy interventionPolicy
        comparisonPolicy comparison)
    (hParameterOnly :
      ParameterConditioningOnly parameterComparator supportComparator
        closureComparator comparison.theta_i comparison.theta_j)
    (hNoStructural :
      ¬ ∃ channelRecord : SixBirdsIII.TopDownChannelRecord,
        ∃ effect : InstitutionalStructuralEffect S,
          StructuralEffectFor S labelPolicy interventionPolicy
            comparisonPolicy effectPolicy channelPolicy supportComparator
            closureComparator comparison channelRecord effect)
    (hStatusOccurrence :
      InstitutionalRewriteStatusOccurrenceFor S labelPolicy interventionPolicy
        comparisonPolicy statusPolicy comparison statusRecord)
    (hStatus :
      statusRecord.status = InstitutionalRewriteStatus.conditioning)
    (hChannel : statusRecord.channelRecord = none)
    (hParameterField :
      statusRecord.parameterRecord = some parameterEffect.parameterRecord)
    (hEffect : statusRecord.effectRecord = none)
    (hCompiled : statusRecord.compiledRecord = none)
    (hParameterComparison :
      parameterEffect.comparisonRecord = comparison.comparisonRecord)
    (hParameterCarried :
      CarriedRecordAt parameterPolicy parameterEffect.parameterRecord
        nParameter FineSourceTag.committed_state true true) :
    ConditioningHolds S labelPolicy interventionPolicy comparisonPolicy
      effectPolicy parameterPolicy channelPolicy statusPolicy
      parameterComparator supportComparator closureComparator comparison := by
  refine ⟨statusRecord, parameterEffect, ?_⟩
  exact ⟨hStatusOccurrence, hStatus, hChannel, hParameterField, hEffect,
    hCompiled, hStatusOccurrence.1, hParameterComparison,
    ⟨nParameter, hParameterCarried⟩, hParameterOnly, hNoStructural⟩

theorem E11_WashoutInert
    (comparison : MatchedInstitutionalComparison S)
    (statusRecord :
      InstitutionalRewriteStatusRecord LedgerEntry AuditRecord)
    (hWashout :
      WashoutNull S labelPolicy interventionPolicy comparisonPolicy
        effectPolicy channelPolicy staticLabels baseIndependent
        strictRefinement parameterComparator supportComparator
        closureComparator comparison)
    (hStatusOccurrence :
      InstitutionalRewriteStatusOccurrenceFor S labelPolicy interventionPolicy
        comparisonPolicy statusPolicy comparison statusRecord)
    (hStatus : statusRecord.status = InstitutionalRewriteStatus.inert)
    (hChannel : statusRecord.channelRecord = none)
    (hEffect : statusRecord.effectRecord = none)
    (hParameter : statusRecord.parameterRecord = none)
    (hCompiled : statusRecord.compiledRecord = none) :
    InertHolds S labelPolicy interventionPolicy comparisonPolicy
      effectPolicy channelPolicy statusPolicy staticLabels baseIndependent
      strictRefinement parameterComparator supportComparator
      closureComparator comparison := by
  refine ⟨statusRecord, ?_⟩
  exact ⟨hStatusOccurrence, hStatus, hChannel, hEffect, hParameter,
    hCompiled, hStatusOccurrence.1, Or.inl hWashout⟩

theorem E11_NCTDObstruction :
    exists R : SixBirdsIII.TopDownChannelRecord,
      SixBirdsIII.StructDown R ∧
      SixBirdsIII.TopDownChannelClaimStatus R =
        SixBirdsIII.ClaimStatus.blocked := by
  exact SixBirdsIII.structural_downward_influence_not_top_down_channel

theorem E11_StatusPartition
    (comparison : MatchedInstitutionalComparison S)
    (hComplete :
      CompleteInstitutionalRewriteStatus S labelPolicy interventionPolicy
        comparisonPolicy effectPolicy parameterPolicy compiledPolicy
        channelPolicy statusPolicy staticLabels baseIndependent
        strictRefinement parameterComparator supportComparator
        closureComparator e4Compiled comparison) :
    (InertHolds S labelPolicy interventionPolicy comparisonPolicy
        effectPolicy channelPolicy statusPolicy staticLabels baseIndependent
        strictRefinement parameterComparator supportComparator
        closureComparator comparison ∧
        ¬ ConditioningHolds S labelPolicy interventionPolicy
          comparisonPolicy effectPolicy parameterPolicy channelPolicy
          statusPolicy parameterComparator supportComparator
          closureComparator comparison ∧
        ¬ StackActiveHolds S labelPolicy interventionPolicy comparisonPolicy
          effectPolicy parameterPolicy compiledPolicy channelPolicy
          statusPolicy parameterComparator supportComparator
          closureComparator e4Compiled comparison ∧
        ¬ ConstitutiveHolds S labelPolicy interventionPolicy
          comparisonPolicy effectPolicy parameterPolicy compiledPolicy
          channelPolicy statusPolicy parameterComparator supportComparator
          closureComparator e4Compiled comparison) ∨
      (ConditioningHolds S labelPolicy interventionPolicy comparisonPolicy
        effectPolicy parameterPolicy channelPolicy statusPolicy
        parameterComparator supportComparator closureComparator comparison ∧
        ¬ InertHolds S labelPolicy interventionPolicy comparisonPolicy
          effectPolicy channelPolicy statusPolicy staticLabels
          baseIndependent strictRefinement parameterComparator
          supportComparator closureComparator comparison ∧
        ¬ StackActiveHolds S labelPolicy interventionPolicy comparisonPolicy
          effectPolicy parameterPolicy compiledPolicy channelPolicy
          statusPolicy parameterComparator supportComparator
          closureComparator e4Compiled comparison ∧
        ¬ ConstitutiveHolds S labelPolicy interventionPolicy
          comparisonPolicy effectPolicy parameterPolicy compiledPolicy
          channelPolicy statusPolicy parameterComparator supportComparator
          closureComparator e4Compiled comparison) ∨
      (StackActiveHolds S labelPolicy interventionPolicy comparisonPolicy
        effectPolicy parameterPolicy compiledPolicy channelPolicy
        statusPolicy parameterComparator supportComparator closureComparator
        e4Compiled comparison ∧
        ¬ InertHolds S labelPolicy interventionPolicy comparisonPolicy
          effectPolicy channelPolicy statusPolicy staticLabels
          baseIndependent strictRefinement parameterComparator
          supportComparator closureComparator comparison ∧
        ¬ ConditioningHolds S labelPolicy interventionPolicy
          comparisonPolicy effectPolicy parameterPolicy channelPolicy
          statusPolicy parameterComparator supportComparator
          closureComparator comparison ∧
        ¬ ConstitutiveHolds S labelPolicy interventionPolicy
          comparisonPolicy effectPolicy parameterPolicy compiledPolicy
          channelPolicy statusPolicy parameterComparator supportComparator
          closureComparator e4Compiled comparison) ∨
      (ConstitutiveHolds S labelPolicy interventionPolicy comparisonPolicy
        effectPolicy parameterPolicy compiledPolicy channelPolicy
        statusPolicy parameterComparator supportComparator closureComparator
        e4Compiled comparison ∧
        ¬ InertHolds S labelPolicy interventionPolicy comparisonPolicy
          effectPolicy channelPolicy statusPolicy staticLabels
          baseIndependent strictRefinement parameterComparator
          supportComparator closureComparator comparison ∧
        ¬ ConditioningHolds S labelPolicy interventionPolicy
          comparisonPolicy effectPolicy parameterPolicy channelPolicy
          statusPolicy parameterComparator supportComparator
          closureComparator comparison ∧
        ¬ StackActiveHolds S labelPolicy interventionPolicy comparisonPolicy
          effectPolicy parameterPolicy compiledPolicy channelPolicy
          statusPolicy parameterComparator supportComparator
          closureComparator e4Compiled comparison) := by
  let hUnique := hComplete.2
  rcases hComplete.1 with ⟨record, _hOccurrence, hBranch⟩
  rcases hBranch with hInertCase | hRest
  · have hInert :
        InertHolds S labelPolicy interventionPolicy comparisonPolicy
          effectPolicy channelPolicy statusPolicy staticLabels
          baseIndependent strictRefinement parameterComparator
          supportComparator closureComparator comparison :=
      ⟨record, hInertCase⟩
    have hStatus :
        record.status = InstitutionalRewriteStatus.inert := hInertCase.2.1
    have hNotConditioning :
        ¬ ConditioningHolds S labelPolicy interventionPolicy
          comparisonPolicy effectPolicy parameterPolicy channelPolicy
          statusPolicy parameterComparator supportComparator
          closureComparator comparison := by
      intro hOther
      rcases hOther with ⟨other, hOtherCase⟩
      rcases hOtherCase with ⟨parameterEffect, hOtherBody⟩
      have hsame := hUnique record other hInertCase.1 hOtherBody.1
      rw [hStatus, hOtherBody.2.1] at hsame
      cases hsame
    have hNotStack :
        ¬ StackActiveHolds S labelPolicy interventionPolicy comparisonPolicy
          effectPolicy parameterPolicy compiledPolicy channelPolicy
          statusPolicy parameterComparator supportComparator
          closureComparator e4Compiled comparison := by
      intro hOther
      rcases hOther with ⟨other, hOtherCase⟩
      rcases hOtherCase with ⟨channelRecord, effect, hOtherBody⟩
      have hsame := hUnique record other hInertCase.1 hOtherBody.1
      rw [hStatus, hOtherBody.2.1] at hsame
      cases hsame
    have hNotConstitutive :
        ¬ ConstitutiveHolds S labelPolicy interventionPolicy
          comparisonPolicy effectPolicy parameterPolicy compiledPolicy
          channelPolicy statusPolicy parameterComparator supportComparator
          closureComparator e4Compiled comparison := by
      intro hOther
      rcases hOther with ⟨other, hOtherCase⟩
      rcases hOtherCase with
        ⟨channelRecord, effect, compiledRecord, hOtherBody⟩
      have hsame := hUnique record other hInertCase.1 hOtherBody.1
      rw [hStatus, hOtherBody.2.1] at hsame
      cases hsame
    exact Or.inl
      ⟨hInert, hNotConditioning, hNotStack, hNotConstitutive⟩
  · rcases hRest with hConditioningCase | hRest
    · rcases hConditioningCase with
        ⟨parameterEffect, hConditioningBody⟩
      have hConditioning :
          ConditioningHolds S labelPolicy interventionPolicy
            comparisonPolicy effectPolicy parameterPolicy channelPolicy
            statusPolicy parameterComparator supportComparator
            closureComparator comparison :=
        ⟨record, parameterEffect, hConditioningBody⟩
      have hStatus :
          record.status = InstitutionalRewriteStatus.conditioning :=
        hConditioningBody.2.1
      have hNotInert :
          ¬ InertHolds S labelPolicy interventionPolicy comparisonPolicy
            effectPolicy channelPolicy statusPolicy staticLabels
            baseIndependent strictRefinement parameterComparator
            supportComparator closureComparator comparison := by
        intro hOther
        rcases hOther with ⟨other, hOtherCase⟩
        have hsame := hUnique record other hConditioningBody.1
          hOtherCase.1
        rw [hStatus, hOtherCase.2.1] at hsame
        cases hsame
      have hNotStack :
          ¬ StackActiveHolds S labelPolicy interventionPolicy
            comparisonPolicy effectPolicy parameterPolicy compiledPolicy
            channelPolicy statusPolicy parameterComparator supportComparator
            closureComparator e4Compiled comparison := by
        intro hOther
        rcases hOther with ⟨other, hOtherCase⟩
        rcases hOtherCase with ⟨channelRecord, effect, hOtherBody⟩
        have hsame := hUnique record other hConditioningBody.1
          hOtherBody.1
        rw [hStatus, hOtherBody.2.1] at hsame
        cases hsame
      have hNotConstitutive :
          ¬ ConstitutiveHolds S labelPolicy interventionPolicy
            comparisonPolicy effectPolicy parameterPolicy compiledPolicy
            channelPolicy statusPolicy parameterComparator supportComparator
            closureComparator e4Compiled comparison := by
        intro hOther
        rcases hOther with ⟨other, hOtherCase⟩
        rcases hOtherCase with
          ⟨channelRecord, effect, compiledRecord, hOtherBody⟩
        have hsame := hUnique record other hConditioningBody.1
          hOtherBody.1
        rw [hStatus, hOtherBody.2.1] at hsame
        cases hsame
      exact Or.inr (Or.inl
        ⟨hConditioning, hNotInert, hNotStack, hNotConstitutive⟩)
    · rcases hRest with hStackCase | hConstitutiveCase
      · rcases hStackCase with ⟨channelRecord, effect, hStackBody⟩
        have hStack :
            StackActiveHolds S labelPolicy interventionPolicy
              comparisonPolicy effectPolicy parameterPolicy compiledPolicy
              channelPolicy statusPolicy parameterComparator
              supportComparator closureComparator e4Compiled comparison :=
          ⟨record, channelRecord, effect, hStackBody⟩
        have hStatus :
            record.status = InstitutionalRewriteStatus.stack_active :=
          hStackBody.2.1
        have hNotInert :
            ¬ InertHolds S labelPolicy interventionPolicy comparisonPolicy
              effectPolicy channelPolicy statusPolicy staticLabels
              baseIndependent strictRefinement parameterComparator
              supportComparator closureComparator comparison := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hStackBody.1 hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        have hNotConditioning :
            ¬ ConditioningHolds S labelPolicy interventionPolicy
              comparisonPolicy effectPolicy parameterPolicy channelPolicy
              statusPolicy parameterComparator supportComparator
              closureComparator comparison := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          rcases hOtherCase with ⟨parameterEffect, hOtherBody⟩
          have hsame := hUnique record other hStackBody.1
            hOtherBody.1
          rw [hStatus, hOtherBody.2.1] at hsame
          cases hsame
        have hNotConstitutive :
            ¬ ConstitutiveHolds S labelPolicy interventionPolicy
              comparisonPolicy effectPolicy parameterPolicy compiledPolicy
              channelPolicy statusPolicy parameterComparator supportComparator
              closureComparator e4Compiled comparison := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          rcases hOtherCase with
            ⟨otherChannel, otherEffect, otherCompiled, hOtherBody⟩
          have hsame := hUnique record other hStackBody.1 hOtherBody.1
          rw [hStatus, hOtherBody.2.1] at hsame
          cases hsame
        exact Or.inr (Or.inr (Or.inl
          ⟨hStack, hNotInert, hNotConditioning, hNotConstitutive⟩))
      · rcases hConstitutiveCase with
          ⟨channelRecord, effect, compiledRecord, hConstitutiveBody⟩
        have hConstitutive :
            ConstitutiveHolds S labelPolicy interventionPolicy
              comparisonPolicy effectPolicy parameterPolicy compiledPolicy
              channelPolicy statusPolicy parameterComparator
              supportComparator closureComparator e4Compiled comparison :=
          ⟨record, channelRecord, effect, compiledRecord,
            hConstitutiveBody⟩
        have hStatus :
            record.status = InstitutionalRewriteStatus.constitutive :=
          hConstitutiveBody.2.1
        have hNotInert :
            ¬ InertHolds S labelPolicy interventionPolicy comparisonPolicy
              effectPolicy channelPolicy statusPolicy staticLabels
              baseIndependent strictRefinement parameterComparator
              supportComparator closureComparator comparison := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          have hsame := hUnique record other hConstitutiveBody.1
            hOtherCase.1
          rw [hStatus, hOtherCase.2.1] at hsame
          cases hsame
        have hNotConditioning :
            ¬ ConditioningHolds S labelPolicy interventionPolicy
              comparisonPolicy effectPolicy parameterPolicy channelPolicy
              statusPolicy parameterComparator supportComparator
              closureComparator comparison := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          rcases hOtherCase with ⟨parameterEffect, hOtherBody⟩
          have hsame := hUnique record other hConstitutiveBody.1
            hOtherBody.1
          rw [hStatus, hOtherBody.2.1] at hsame
          cases hsame
        have hNotStack :
            ¬ StackActiveHolds S labelPolicy interventionPolicy
              comparisonPolicy effectPolicy parameterPolicy compiledPolicy
              channelPolicy statusPolicy parameterComparator supportComparator
              closureComparator e4Compiled comparison := by
          intro hOther
          rcases hOther with ⟨other, hOtherCase⟩
          rcases hOtherCase with ⟨otherChannel, otherEffect, hOtherBody⟩
          have hsame := hUnique record other hConstitutiveBody.1
            hOtherBody.1
          rw [hStatus, hOtherBody.2.1] at hsame
          cases hsame
        exact Or.inr (Or.inr (Or.inr
          ⟨hConstitutive, hNotInert, hNotConditioning, hNotStack⟩))

end Theorems

end SixBirdsFoundationsV
