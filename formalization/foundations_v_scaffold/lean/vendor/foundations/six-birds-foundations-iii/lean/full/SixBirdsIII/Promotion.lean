import SixBirdsIII.Defects
import SixBirdsIII.Status

namespace SixBirdsIII

structure PromotionGateResults where
  suff : GateStatus
  desc : GateStatus
  stab : GateStatus
  ctrl : GateStatus
  nosmuggle : GateStatus
  vis : GateStatus
  audit : GateStatus
  strict : StrictGateStatus
  locglob : GateStatus
deriving Repr

def CoreGateAcceptable (g : GateStatus) : Prop :=
  g = GateStatus.pass ∨ g = GateStatus.notRequired

def CoreGateAcceptableBool : GateStatus -> Bool
  | GateStatus.pass => true
  | GateStatus.notRequired => true
  | _ => false

def RequiredCoreGatesPassBool (g : PromotionGateResults) : Bool :=
  match g.suff, g.ctrl, g.nosmuggle, g.vis, g.audit with
  | GateStatus.pass, GateStatus.pass, GateStatus.pass, GateStatus.pass, GateStatus.pass =>
      CoreGateAcceptableBool g.desc && CoreGateAcceptableBool g.stab
  | _, _, _, _, _ => false

def RequiredCoreGatesPass (g : PromotionGateResults) : Prop :=
  RequiredCoreGatesPassBool g = true

structure PromotionBridgeData (S O0 O1 : Type) where
  pi0 : S -> O0
  pi1 : S -> O1
  admissible : Bool
  gates : PromotionGateResults
  strictGateSound :
    gates.strict = StrictGateStatus.strictPass ->
      HasFactorizationDefect pi0 pi1
  nonStrictGateSound :
    gates.strict = StrictGateStatus.nonStrictPass ->
      FactorsThroughImage pi0 pi1

def PromotionAcceptedCoreBool {S O0 O1 : Type} (B : PromotionBridgeData S O0 O1) : Bool :=
  B.admissible && RequiredCoreGatesPassBool B.gates

def PromotionAcceptedCore {S O0 O1 : Type} (B : PromotionBridgeData S O0 O1) : Prop :=
  PromotionAcceptedCoreBool B = true

def Promote {S O0 O1 : Type} (B : PromotionBridgeData S O0 O1) : PromotionStatus :=
  if PromotionAcceptedCoreBool B then
    if B.gates.strict = StrictGateStatus.strictPass then PromotionStatus.strict
    else if B.gates.strict = StrictGateStatus.nonStrictPass then PromotionStatus.nonStrict
    else PromotionStatus.accepted
  else PromotionStatus.candidate

def AcceptedPromotionFamily (status : PromotionStatus) : Prop :=
  status = PromotionStatus.accepted ∨
    status = PromotionStatus.strict ∨
    status = PromotionStatus.nonStrict

theorem promotion_gate_soundness {S O0 O1 : Type}
    (B : PromotionBridgeData S O0 O1) :
    AcceptedPromotionFamily (Promote B) ->
      RequiredCoreGatesPass B.gates := by
  intro haccepted
  unfold Promote at haccepted
  unfold RequiredCoreGatesPass
  cases hadm : B.admissible <;>
    cases hgates : RequiredCoreGatesPassBool B.gates <;>
    simp [PromotionAcceptedCoreBool, hadm, hgates] at haccepted ⊢
  all_goals
    try (rcases haccepted with h | h | h <;> cases h)

theorem strict_promotion_nonfactorization {S O0 O1 : Type}
    (B : PromotionBridgeData S O0 O1) :
    Promote B = PromotionStatus.strict ->
      HasFactorizationDefect B.pi0 B.pi1 ∧
      ¬ FactorsThroughImage B.pi0 B.pi1 := by
  intro hstrict
  unfold Promote at hstrict
  cases hadm : B.admissible <;>
    cases hgates : RequiredCoreGatesPassBool B.gates <;>
    simp [PromotionAcceptedCoreBool, hadm, hgates] at hstrict
  by_cases hs : B.gates.strict = StrictGateStatus.strictPass
  · have hdefect := B.strictGateSound hs
    exact ⟨hdefect, (factorization_defect_equivalence B.pi0 B.pi1).mp hdefect⟩
  · simp [hs] at hstrict
    by_cases hn : B.gates.strict = StrictGateStatus.nonStrictPass
    · simp [hn] at hstrict
    · simp [hn] at hstrict

theorem nonstrict_promotion_factorization {S O0 O1 : Type}
    (B : PromotionBridgeData S O0 O1) :
    Promote B = PromotionStatus.nonStrict ->
      FactorsThroughImage B.pi0 B.pi1 := by
  intro hnonstrict
  unfold Promote at hnonstrict
  cases hadm : B.admissible <;>
    cases hgates : RequiredCoreGatesPassBool B.gates <;>
    simp [PromotionAcceptedCoreBool, hadm, hgates] at hnonstrict
  by_cases hs : B.gates.strict = StrictGateStatus.strictPass
  · simp [hs] at hnonstrict
  · simp [hs] at hnonstrict
    by_cases hn : B.gates.strict = StrictGateStatus.nonStrictPass
    · exact B.nonStrictGateSound hn
    · simp [hn] at hnonstrict

inductive Toy22Carrier where
  | a
  | b
deriving DecidableEq, Repr

inductive Toy22O0 where
  | star
deriving DecidableEq, Repr

inductive Toy22O1 where
  | u
  | v
deriving DecidableEq, Repr

def toy22Pi0 : Toy22Carrier -> Toy22O0
  | _ => Toy22O0.star

def toy22Pi1 : Toy22Carrier -> Toy22O1
  | Toy22Carrier.a => Toy22O1.u
  | Toy22Carrier.b => Toy22O1.v

def toy22Gates : PromotionGateResults :=
  { suff := GateStatus.pass
    desc := GateStatus.notRequired
    stab := GateStatus.notRequired
    ctrl := GateStatus.pass
    nosmuggle := GateStatus.pass
    vis := GateStatus.pass
    audit := GateStatus.pass
    strict := StrictGateStatus.strictPass
    locglob := GateStatus.notRequired }

theorem toy22_factorization_defect :
    HasFactorizationDefect toy22Pi0 toy22Pi1 := by
  exact ⟨Toy22Carrier.a, Toy22Carrier.b, rfl, by
    intro h
    cases h⟩

def toy22Bridge : PromotionBridgeData Toy22Carrier Toy22O0 Toy22O1 :=
  { pi0 := toy22Pi0
    pi1 := toy22Pi1
    admissible := true
    gates := toy22Gates
    strictGateSound := by
      intro _h
      exact toy22_factorization_defect
    nonStrictGateSound := by
      intro h
      cases h }

theorem toy22_bridge_strict :
    Promote toy22Bridge = PromotionStatus.strict := by
  simp [Promote, PromotionAcceptedCoreBool, RequiredCoreGatesPassBool,
    CoreGateAcceptableBool, toy22Bridge, toy22Gates]

theorem toy22_strict_bridge :
    exists B : PromotionBridgeData Toy22Carrier Toy22O0 Toy22O1,
      Promote B = PromotionStatus.strict /\
      HasFactorizationDefect B.pi0 B.pi1 := by
  exact ⟨toy22Bridge, toy22_bridge_strict, toy22_factorization_defect⟩

end SixBirdsIII
