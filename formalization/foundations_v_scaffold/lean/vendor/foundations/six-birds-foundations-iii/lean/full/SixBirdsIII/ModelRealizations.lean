import SixBirdsIII.Promotion

namespace SixBirdsIII

inductive ModelVerdict where
  | modelRealization
  | notRealized
deriving DecidableEq, Repr

structure FragmentRealization where
  finiteHost : Bool
  audited : Bool
  visibilityPasses : Bool
  sourcePolicyPasses : Bool
  nonclaimsRecorded : Bool
  verdict : ModelVerdict
deriving Repr

def successfulFragmentRealization : FragmentRealization :=
  { finiteHost := true
    audited := true
    visibilityPasses := true
    sourcePolicyPasses := true
    nonclaimsRecorded := true
    verdict := ModelVerdict.modelRealization }

structure PICARealization where
  finiteStateSpace : Bool
  finiteStores : Bool
  directedCellsRecovered : Bool
  pairObservablesRecovered : Bool
  provenanceAudited : Bool
  rawStatusDoesNotOverrideClassifier : Bool
  nonclaimsRecorded : Bool
deriving Repr

def PICARealizesCellPairProvenance (P : PICARealization) : Prop :=
  P.finiteStateSpace = true /\
    P.finiteStores = true /\
    P.directedCellsRecovered = true /\
    P.pairObservablesRecovered = true /\
    P.provenanceAudited = true /\
    P.rawStatusDoesNotOverrideClassifier = true /\
    P.nonclaimsRecorded = true

theorem pica_model_realization
    (P : PICARealization) :
    PICARealizesCellPairProvenance P ->
      exists R : FragmentRealization,
        R.verdict = ModelVerdict.modelRealization /\
        R.finiteHost = true /\
        R.audited = true /\
        R.nonclaimsRecorded = true := by
  intro hP
  exact ⟨successfulFragmentRealization, rfl, rfl, rfl, rfl⟩

structure CantorStrictBridgeRealization (S O0 O1 : Type) where
  finiteAuditedShell : Bool
  bridge : PromotionBridgeData S O0 O1
  gatesPassOrNotRequired : Bool
  strictnessWitnessAudited : Bool
  pressureGapRecordedAsConsequence : Bool
  scopedToAuditedShell : Bool
  nonclaimsRecorded : Bool

theorem cantor_strict_bridge_realization {S O0 O1 : Type}
    (C : CantorStrictBridgeRealization S O0 O1)
    (hfinite : C.finiteAuditedShell = true)
    (_hgates : C.gatesPassOrNotRequired = true)
    (_hstrict : C.strictnessWitnessAudited = true)
    (_hscope : C.scopedToAuditedShell = true)
    (hnonclaims : C.nonclaimsRecorded = true)
    (_hpromote : Promote C.bridge = PromotionStatus.strict) :
      exists R : FragmentRealization,
        R.verdict = ModelVerdict.modelRealization /\
        R.finiteHost = true /\
        R.audited = true /\
        R.nonclaimsRecorded = true := by
  refine ⟨{ successfulFragmentRealization with
      finiteHost := C.finiteAuditedShell
      nonclaimsRecorded := C.nonclaimsRecorded }, ?_, ?_, ?_, ?_⟩
  · rfl
  · exact hfinite
  · rfl
  · exact hnonclaims

def toyPICARealization : PICARealization :=
  { finiteStateSpace := true
    finiteStores := true
    directedCellsRecovered := true
    pairObservablesRecovered := true
    provenanceAudited := true
    rawStatusDoesNotOverrideClassifier := true
    nonclaimsRecorded := true }

def toyBadPICARealization : PICARealization :=
  { toyPICARealization with
    rawStatusDoesNotOverrideClassifier := false }

def toyCantorStrictBridgeRealization :
    CantorStrictBridgeRealization Toy22Carrier Toy22O0 Toy22O1 :=
  { finiteAuditedShell := true
    bridge := toy22Bridge
    gatesPassOrNotRequired := true
    strictnessWitnessAudited := true
    pressureGapRecordedAsConsequence := true
    scopedToAuditedShell := true
    nonclaimsRecorded := true }

end SixBirdsIII
