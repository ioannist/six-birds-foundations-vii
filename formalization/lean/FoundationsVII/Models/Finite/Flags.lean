import FoundationsVII.Core.Protocols

/-!
# Finite reference-world data
-/

namespace FoundationsVII.Models.Finite

structure ScenarioFlags where
  antiProduct : Bool := false
  budgetOk : Bool := false
  closedFamily : Bool := false
  commonRefinement : Bool := false
  compatible : Bool := false
  composite : Bool := false
  contact : Bool := false
  detectorPower : Bool := false
  drive : Bool := false
  fired : Bool := false
  generatorReachable : Bool := false
  holonomy : Bool := false
  joinDestroyed : Bool := false
  neutralSeed : Bool := false
  newResidual : Bool := false
  observerPriced : Bool := false
  observerUsed : Bool := false
  orderResidue : Bool := false
  parentRefined : Bool := false
  partialDomain : Bool := false
  prospective : Bool := false
  reachable : Bool := false
  relabelOnly : Bool := false
  resemblanceOnly : Bool := false
  retention : Bool := false
  retrospective : Bool := false
  sameSource : Bool := false
  schedulingOnly : Bool := false
  seed : Bool := false
  sound : Bool := false
  sourceIndependent : Bool := false
  totalLensOnly : Bool := false
  deriving Repr, DecidableEq, BEq, Inhabited

inductive ScenarioStatus where
  | bootstrapBlocked
  | lawfulFirstExtension
  | prospectiveAdmission
  | retrospectiveSelfCertificationRejected
  | independenceGateFailed
  | contactWithoutJoin
  | commonRefinementNonstrict
  | strictJoin
  | retentionObstruction
  | budgetObstruction
  | sourceObstruction
  | noEvidencedContact
  | certifiedNoninteraction
  | fakeJoinScheduling
  | fakeJoinRelabeling
  | orderResidue
  | holonomyZeroArrow
  | drivenArrow
  | soundUnreachable
  | reachableNonoccurrent
  | occurrentEvent
  | unpricedObserver
  | unlicensedTotalityTransfer
  | refinementDestroysJoin
  | unclassified
  deriving Repr, DecidableEq, BEq, Inhabited

namespace ScenarioStatus

def all : List ScenarioStatus :=
  [.bootstrapBlocked, .lawfulFirstExtension, .prospectiveAdmission,
   .retrospectiveSelfCertificationRejected, .independenceGateFailed,
   .contactWithoutJoin, .commonRefinementNonstrict, .strictJoin,
   .retentionObstruction, .budgetObstruction, .sourceObstruction,
   .noEvidencedContact, .certifiedNoninteraction, .fakeJoinScheduling,
   .fakeJoinRelabeling, .orderResidue, .holonomyZeroArrow, .drivenArrow,
   .soundUnreachable, .reachableNonoccurrent, .occurrentEvent,
   .unpricedObserver, .unlicensedTotalityTransfer, .refinementDestroysJoin,
   .unclassified]

theorem mem_all (status : ScenarioStatus) : status ∈ all := by
  cases status <;> simp [all]

theorem all_pairwise_distinct : all.eraseDups.length = 25 := by decide

end ScenarioStatus

inductive DerivedKey where
  | bridgeValid
  | certifiedNoninteraction
  | contact
  | directionality
  | endogenous
  | firstExtension
  | holonomy
  | newResidual
  | occurred
  | prospectiveCredit
  | reachable
  | strictJoin
  deriving Repr, DecidableEq, BEq, Inhabited

namespace DerivedKey

def all : List DerivedKey :=
  [.bridgeValid, .certifiedNoninteraction, .contact, .directionality,
   .endogenous, .firstExtension, .holonomy, .newResidual, .occurred,
   .prospectiveCredit, .reachable, .strictJoin]

theorem mem_all (key : DerivedKey) : key ∈ all := by
  cases key <;> simp [all]

end DerivedKey

structure DerivedFacts where
  contact : Bool
  strictJoin : Bool
  directionality : Bool
  reachable : Bool
  occurred : Bool
  firstExtension : Bool
  prospectiveCredit : Bool
  certifiedNoninteraction : Bool
  bridgeValid : Bool
  endogenous : Bool
  newResidual : Bool
  holonomy : Bool
  deriving Repr, DecidableEq, BEq

structure ScenarioFixture where
  fixtureId : String
  name : String
  flags : ScenarioFlags
  expectedStatus : ScenarioStatus
  assertions : List (DerivedKey × Bool)
  candidateIds : List String
  deriving Repr, DecidableEq, BEq

structure CountermodelFixture where
  fixtureId : String
  name : String
  scenario : ScenarioFixture
  expectedStatus : ScenarioStatus
  shows : String
  candidateIds : List String
  deriving Repr, DecidableEq, BEq

end FoundationsVII.Models.Finite
