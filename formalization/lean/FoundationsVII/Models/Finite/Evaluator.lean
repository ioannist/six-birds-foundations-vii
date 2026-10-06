import FoundationsVII.Models.Finite.Flags

/-!
# Independent Lean finite evaluator

This implementation is handwritten independently from the Python evaluator.
The two share only the frozen fixture specification.
-/

namespace FoundationsVII.Models.Finite

def derive (f : ScenarioFlags) : DerivedFacts :=
  let strictJoin :=
    f.contact && f.sourceIndependent && f.composite && f.retention &&
    f.antiProduct && f.budgetOk && !f.schedulingOnly && !f.relabelOnly
  { contact := f.contact
    strictJoin := strictJoin
    directionality := f.drive
    reachable := f.reachable
    occurred := f.fired
    firstExtension := f.seed && f.generatorReachable && f.fired
    prospectiveCredit := f.prospective && !f.retrospective
    certifiedNoninteraction := !f.contact && f.closedFamily && f.detectorPower
    bridgeValid := !(f.totalLensOnly && f.partialDomain)
    endogenous := f.generatorReachable && f.fired && !f.observerUsed && !f.seed
    newResidual := f.newResidual
    holonomy := f.holonomy }

def classify (f : ScenarioFlags) (facts : DerivedFacts) : ScenarioStatus :=
  if !f.seed && !f.generatorReachable &&
      !(facts.contact || f.compatible || f.closedFamily || f.sound ||
        f.prospective || f.retrospective || f.observerUsed ||
        f.totalLensOnly || f.parentRefined) then
    .bootstrapBlocked
  else if f.retrospective then
    .retrospectiveSelfCertificationRejected
  else if f.observerUsed && !f.observerPriced then
    .unpricedObserver
  else if f.totalLensOnly && f.partialDomain then
    .unlicensedTotalityTransfer
  else if f.holonomy && !f.drive && !f.orderResidue then
    .holonomyZeroArrow
  else if f.drive then
    .drivenArrow
  else if f.orderResidue then
    .orderResidue
  else if f.sound && !f.reachable then
    .soundUnreachable
  else if f.reachable && !f.fired then
    .reachableNonoccurrent
  else if f.sound && f.reachable && f.fired then
    .occurrentEvent
  else if f.parentRefined && f.joinDestroyed then
    .refinementDestroysJoin
  else if facts.certifiedNoninteraction then
    .certifiedNoninteraction
  else if !facts.contact && f.compatible then
    .noEvidencedContact
  else if f.schedulingOnly then
    .fakeJoinScheduling
  else if f.relabelOnly then
    .fakeJoinRelabeling
  else if facts.contact && f.sameSource && f.resemblanceOnly then
    .independenceGateFailed
  else if facts.contact && !f.composite then
    .contactWithoutJoin
  else if facts.contact && f.commonRefinement && !f.antiProduct then
    .commonRefinementNonstrict
  else if facts.contact && f.composite && !f.retention then
    .retentionObstruction
  else if facts.contact && f.composite && f.antiProduct && !f.budgetOk then
    .budgetObstruction
  else if facts.contact && f.composite && f.antiProduct && !f.sourceIndependent then
    .sourceObstruction
  else if facts.strictJoin then
    .strictJoin
  else if facts.prospectiveCredit then
    .prospectiveAdmission
  else if facts.firstExtension then
    .lawfulFirstExtension
  else
    .unclassified

def evaluate (f : ScenarioFlags) : ScenarioStatus × DerivedFacts :=
  let facts := derive f
  (classify f facts, facts)

def derivedValue (facts : DerivedFacts) : DerivedKey → Bool
  | .bridgeValid => facts.bridgeValid
  | .certifiedNoninteraction => facts.certifiedNoninteraction
  | .contact => facts.contact
  | .directionality => facts.directionality
  | .endogenous => facts.endogenous
  | .firstExtension => facts.firstExtension
  | .holonomy => facts.holonomy
  | .newResidual => facts.newResidual
  | .occurred => facts.occurred
  | .prospectiveCredit => facts.prospectiveCredit
  | .reachable => facts.reachable
  | .strictJoin => facts.strictJoin

def assertionsPass (fixture : ScenarioFixture) : Bool :=
  let facts := (evaluate fixture.flags).2
  fixture.assertions.all (fun assertion =>
    derivedValue facts assertion.1 == assertion.2)

def scenarioPass (fixture : ScenarioFixture) : Bool :=
  (evaluate fixture.flags).1 == fixture.expectedStatus && assertionsPass fixture

end FoundationsVII.Models.Finite
