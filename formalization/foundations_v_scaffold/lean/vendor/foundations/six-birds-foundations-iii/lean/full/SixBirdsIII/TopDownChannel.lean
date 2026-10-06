import SixBirdsIII.Records

namespace SixBirdsIII

inductive TopDownGate where
  | macroRecord
  | intervention
  | matchedControls
  | feasibility
  | source
  | visibility
  | audit
  | noSmuggling
  | effect
  deriving DecidableEq, Repr

structure TopDownChannelRecord where
  host : Host
  profile : Profile
  macroRecordPresent : Bool
  substrateRecordPresent : Bool
  structuralPathPresent : Bool
  interventionGate : Bool
  matchedControlsGate : Bool
  feasibilityGate : Bool
  sourceGate : Bool
  visibilityGate : Bool
  auditGate : Bool
  noSmugglingGate : Bool
  effectGate : Bool
  comparatorFinite : Bool
  thresholdFinite : Bool
  nonclaimRecorded : Bool
  deriving Repr

def StructDown (R : TopDownChannelRecord) : Prop :=
  R.structuralPathPresent = true

def WFTopDownChannelRecordBool (R : TopDownChannelRecord) : Bool :=
  R.macroRecordPresent &&
  R.substrateRecordPresent &&
  R.comparatorFinite &&
  R.thresholdFinite &&
  R.nonclaimRecorded

def TDGatePassBool (R : TopDownChannelRecord) : TopDownGate -> Bool
  | TopDownGate.macroRecord => R.macroRecordPresent
  | TopDownGate.intervention => R.interventionGate
  | TopDownGate.matchedControls => R.matchedControlsGate
  | TopDownGate.feasibility => R.feasibilityGate
  | TopDownGate.source => R.sourceGate
  | TopDownGate.visibility => R.visibilityGate
  | TopDownGate.audit => R.auditGate
  | TopDownGate.noSmuggling => R.noSmugglingGate
  | TopDownGate.effect => R.effectGate

def TDGatesPassBool (R : TopDownChannelRecord) : Bool :=
  R.macroRecordPresent &&
  R.interventionGate &&
  R.matchedControlsGate &&
  R.feasibilityGate &&
  R.sourceGate &&
  R.visibilityGate &&
  R.auditGate &&
  R.noSmugglingGate &&
  R.effectGate

def TopDownChannelAcceptedBool (R : TopDownChannelRecord) : Bool :=
  R.structuralPathPresent &&
  WFTopDownChannelRecordBool R &&
  TDGatesPassBool R

def TopDownChannelClaimStatus (R : TopDownChannelRecord) : ClaimStatus :=
  if TopDownChannelAcceptedBool R then ClaimStatus.accepted else ClaimStatus.blocked

def acceptedTopDownRecord : TopDownChannelRecord :=
  { host := Host.fin
    profile := baseProfile
    macroRecordPresent := true
    substrateRecordPresent := true
    structuralPathPresent := true
    interventionGate := true
    matchedControlsGate := true
    feasibilityGate := true
    sourceGate := true
    visibilityGate := true
    auditGate := true
    noSmugglingGate := true
    effectGate := true
    comparatorFinite := true
    thresholdFinite := true
    nonclaimRecorded := true }

def structuralOnlyTopDownRecord : TopDownChannelRecord :=
  { acceptedTopDownRecord with
    interventionGate := false
    effectGate := false }

theorem top_down_channel_implies_struct_down
    (R : TopDownChannelRecord)
    (h : TopDownChannelAcceptedBool R = true) :
    StructDown R := by
  simp [TopDownChannelAcceptedBool] at h
  exact h.1.1

theorem top_down_channel_gate_soundness
    (R : TopDownChannelRecord)
    (h : TopDownChannelAcceptedBool R = true) :
    forall gate : TopDownGate, TDGatePassBool R gate = true := by
  intro gate
  simp [TopDownChannelAcceptedBool, WFTopDownChannelRecordBool,
    TDGatesPassBool] at h
  cases gate <;> simp [TDGatePassBool, h]

theorem structural_downward_influence_not_top_down_channel :
    exists R : TopDownChannelRecord,
      StructDown R /\
      TopDownChannelClaimStatus R = ClaimStatus.blocked := by
  refine ⟨structuralOnlyTopDownRecord, ?_, ?_⟩
  · simp [StructDown, structuralOnlyTopDownRecord, acceptedTopDownRecord]
  · simp [TopDownChannelClaimStatus, TopDownChannelAcceptedBool,
      WFTopDownChannelRecordBool, TDGatesPassBool,
      structuralOnlyTopDownRecord, acceptedTopDownRecord]

end SixBirdsIII
