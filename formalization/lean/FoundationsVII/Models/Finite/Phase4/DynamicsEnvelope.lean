import FoundationsVII.NoGo.Dynamics

/-!
# Bounded enablement/descent/dynamics envelopes for FVII-SCI-04

Each list exhausts one declared finite carrier and mirrors the independent
Python implementation. These computations support but do not replace the
structural theorem modules.
-/

set_option maxHeartbeats 0
set_option maxRecDepth 4000000

namespace FoundationsVII.Models.Finite.Phase4

private def bools : List Bool := [false, true]
private def small : List Nat := [0, 1, 2]

/-! ## P4-E01: enablement attribution -/

inductive FiniteEnablementSource where
  | theorist | carrier | peer | observer | environment | endogenousSystem | mixed
  deriving Repr, DecidableEq, BEq, Inhabited

private def finiteEnablementSources : List FiniteEnablementSource :=
  [.theorist, .carrier, .peer, .observer, .environment, .endogenousSystem, .mixed]

structure AttributionCase where
  sourceKind : FiniteEnablementSource
  executed : Bool
  audited : Bool
  budgeted : Bool
  sourceTyped : Bool
  bridgeRefined : Bool
  rootPreserved : Bool
  hiddenExecutor : Bool
  attributionCredit : Bool
  deriving Repr, DecidableEq, BEq

def attributionLaw (c : AttributionCase) : Bool :=
  (!c.attributionCredit ||
    (c.executed && c.audited && c.budgeted && c.sourceTyped && !c.hiddenExecutor)) &&
  (!(c.bridgeRefined && c.attributionCredit) || c.rootPreserved)

def allAttributionCases : List AttributionCase :=
  finiteEnablementSources.flatMap fun sourceKind =>
  bools.flatMap fun executed =>
  bools.flatMap fun audited =>
  bools.flatMap fun budgeted =>
  bools.flatMap fun sourceTyped =>
  bools.flatMap fun bridgeRefined =>
  bools.flatMap fun rootPreserved =>
  bools.flatMap fun hiddenExecutor =>
  bools.map fun attributionCredit =>
    { sourceKind, executed, audited, budgeted, sourceTyped, bridgeRefined,
      rootPreserved, hiddenExecutor, attributionCredit }

theorem attribution_raw_cardinality : allAttributionCases.length = 1792 := by decide

theorem attribution_accepted_cardinality :
    (allAttributionCases.filter attributionLaw).length = 917 := by decide

theorem attribution_exhaustive :
    (allAttributionCases.filter attributionLaw).all attributionLaw = true := by decide

/-! ## P4-E02: endogenous criterion -/

structure EndogenousCase where
  carried : Bool
  reachable : Bool
  executed : Bool
  audited : Bool
  budgeted : Bool
  boundaryClosed : Bool
  theoristHidden : Bool
  observerHidden : Bool
  environmentalInput : Bool
  environmentAccounted : Bool
  endogenousCredit : Bool
  deriving Repr, DecidableEq, BEq

def endogenousExact (c : EndogenousCase) : Bool :=
  c.carried && c.reachable && c.executed && c.audited && c.budgeted &&
  c.boundaryClosed && !c.theoristHidden && !c.observerHidden &&
  (!c.environmentalInput || c.environmentAccounted)

def endogenousLaw (c : EndogenousCase) : Bool :=
  c.endogenousCredit == endogenousExact c

def allEndogenousCases : List EndogenousCase :=
  bools.flatMap fun carried =>
  bools.flatMap fun reachable =>
  bools.flatMap fun executed =>
  bools.flatMap fun audited =>
  bools.flatMap fun budgeted =>
  bools.flatMap fun boundaryClosed =>
  bools.flatMap fun theoristHidden =>
  bools.flatMap fun observerHidden =>
  bools.flatMap fun environmentalInput =>
  bools.flatMap fun environmentAccounted =>
  bools.map fun endogenousCredit =>
    { carried, reachable, executed, audited, budgeted, boundaryClosed,
      theoristHidden, observerHidden, environmentalInput,
      environmentAccounted, endogenousCredit }

theorem endogenous_raw_cardinality : allEndogenousCases.length = 2048 := by decide

theorem endogenous_accepted_cardinality :
    (allEndogenousCases.filter endogenousLaw).length = 1024 := by decide

theorem endogenous_exhaustive :
    (allEndogenousCases.filter endogenousLaw).all endogenousLaw = true := by decide

/-! ## P4-E03: birth and participant creation -/

inductive FiniteClosureAgency where
  | systemPerforms | systemUndergoes | peer | environment | mixed
  deriving Repr, DecidableEq, BEq, Inhabited

inductive FiniteBirthOutcome where
  | relationOnly | newLayer | newParticipant | refinementOnly
  deriving Repr, DecidableEq, BEq, Inhabited

private def finiteAgencies : List FiniteClosureAgency :=
  [.systemPerforms, .systemUndergoes, .peer, .environment, .mixed]
private def finiteBirthOutcomes : List FiniteBirthOutcome :=
  [.relationOnly, .newLayer, .newParticipant, .refinementOnly]

structure BirthCase where
  agency : FiniteClosureAgency
  outcome : FiniteBirthOutcome
  contactPresent : Bool
  survivesClosure : Bool
  objecthood : Bool
  performedBySystem : Bool
  participantCredit : Bool
  birthCredit : Bool
  deriving Repr, DecidableEq, BEq

def birthLaw (c : BirthCase) : Bool :=
  (c.performedBySystem == (c.agency == .systemPerforms)) &&
  (c.participantCredit ==
    (c.outcome == .newParticipant && c.contactPresent &&
      c.survivesClosure && c.objecthood)) &&
  (c.birthCredit ==
    ((c.outcome == .newLayer || c.outcome == .newParticipant) &&
      c.survivesClosure && c.objecthood)) &&
  (!(c.outcome == .relationOnly) || !c.participantCredit)

def allBirthCases : List BirthCase :=
  finiteAgencies.flatMap fun agency =>
  finiteBirthOutcomes.flatMap fun outcome =>
  bools.flatMap fun contactPresent =>
  bools.flatMap fun survivesClosure =>
  bools.flatMap fun objecthood =>
  bools.flatMap fun performedBySystem =>
  bools.flatMap fun participantCredit =>
  bools.map fun birthCredit =>
    { agency, outcome, contactPresent, survivesClosure, objecthood,
      performedBySystem, participantCredit, birthCredit }

theorem birth_raw_cardinality : allBirthCases.length = 1280 := by decide

theorem birth_accepted_cardinality :
    (allBirthCases.filter birthLaw).length = 160 := by decide

theorem birth_exhaustive :
    (allBirthCases.filter birthLaw).all birthLaw = true := by decide

/-! ## P4-E04: transmission/descent -/

inductive FiniteTransmissionDirection where
  | upward | downward | peer
  deriving Repr, DecidableEq, BEq, Inhabited

private def finiteDirections : List FiniteTransmissionDirection :=
  [.upward, .downward, .peer]

structure TransmissionCase where
  direction : FiniteTransmissionDirection
  payloadPresent : Bool
  sourceTyped : Bool
  budgeted : Bool
  lossRecorded : Bool
  ambiguityRecorded : Bool
  lowerFactBefore : Bool
  lowerFactAfter : Bool
  externalInsertion : Bool
  fidelityCredit : Bool
  causalCertificate : Bool
  causalCredit : Bool
  deriving Repr, DecidableEq, BEq

def transmissionLaw (c : TransmissionCase) : Bool :=
  (!c.fidelityCredit ||
    (c.payloadPresent && c.sourceTyped && c.budgeted &&
      c.lossRecorded && c.ambiguityRecorded)) &&
  (!(c.direction == .downward && c.fidelityCredit && c.lowerFactAfter &&
      !c.externalInsertion) || c.lowerFactBefore) &&
  (!c.causalCredit || (c.fidelityCredit && c.causalCertificate))

def allTransmissionCases : List TransmissionCase :=
  finiteDirections.flatMap fun direction =>
  bools.flatMap fun payloadPresent =>
  bools.flatMap fun sourceTyped =>
  bools.flatMap fun budgeted =>
  bools.flatMap fun lossRecorded =>
  bools.flatMap fun ambiguityRecorded =>
  bools.flatMap fun lowerFactBefore =>
  bools.flatMap fun lowerFactAfter =>
  bools.flatMap fun externalInsertion =>
  bools.flatMap fun fidelityCredit =>
  bools.flatMap fun causalCertificate =>
  bools.map fun causalCredit =>
    { direction, payloadPresent, sourceTyped, budgeted, lossRecorded,
      ambiguityRecorded, lowerFactBefore, lowerFactAfter, externalInsertion,
      fidelityCredit, causalCertificate, causalCredit }

theorem transmission_raw_cardinality : allTransmissionCases.length = 6144 := by decide

theorem transmission_accepted_cardinality :
    (allTransmissionCases.filter transmissionLaw).length = 1605 := by decide

theorem transmission_exhaustive :
    (allTransmissionCases.filter transmissionLaw).all transmissionLaw = true := by decide

/-! ## P4-E05: enablement separations -/

structure SeparationCase where
  enabled : Bool
  loadBearing : Bool
  descentFactorization : Bool
  necessary : Bool
  sufficient : Bool
  alternativeDeterminants : Bool
  causalChannel : Bool
  withoutDescentCredit : Bool
  necessaryInsufficientCredit : Bool
  deriving Repr, DecidableEq, BEq

def separationLaw (c : SeparationCase) : Bool :=
  (c.withoutDescentCredit == (c.enabled && c.loadBearing && !c.descentFactorization)) &&
  (c.necessaryInsufficientCredit ==
    (c.enabled && c.necessary && !c.sufficient && c.alternativeDeterminants))

def allSeparationCases : List SeparationCase :=
  bools.flatMap fun enabled =>
  bools.flatMap fun loadBearing =>
  bools.flatMap fun descentFactorization =>
  bools.flatMap fun necessary =>
  bools.flatMap fun sufficient =>
  bools.flatMap fun alternativeDeterminants =>
  bools.flatMap fun causalChannel =>
  bools.flatMap fun withoutDescentCredit =>
  bools.map fun necessaryInsufficientCredit =>
    { enabled, loadBearing, descentFactorization, necessary, sufficient,
      alternativeDeterminants, causalChannel, withoutDescentCredit,
      necessaryInsufficientCredit }

theorem separation_raw_cardinality : allSeparationCases.length = 512 := by decide

theorem separation_accepted_cardinality :
    (allSeparationCases.filter separationLaw).length = 128 := by decide

theorem separation_exhaustive :
    (allSeparationCases.filter separationLaw).all separationLaw = true := by decide

/-! ## P4-E06: enablement composition -/

structure CompositionCase where
  firstExecuted : Bool
  secondExecuted : Bool
  sourceCompatible : Bool
  budgetCompatible : Bool
  residualCompatible : Bool
  auditCompatible : Bool
  causalChainCertified : Bool
  composedCredit : Bool
  transitiveCausalCredit : Bool
  costA : Nat
  costB : Nat
  debtA : Nat
  debtB : Nat
  deriving Repr, DecidableEq, BEq

def compositionLaw (c : CompositionCase) : Bool :=
  let composable := c.firstExecuted && c.secondExecuted && c.sourceCompatible &&
    c.budgetCompatible && c.residualCompatible && c.auditCompatible
  (c.composedCredit == composable) &&
  (!c.transitiveCausalCredit || (composable && c.causalChainCertified))

def allCompositionCases : List CompositionCase :=
  bools.flatMap fun firstExecuted =>
  bools.flatMap fun secondExecuted =>
  bools.flatMap fun sourceCompatible =>
  bools.flatMap fun budgetCompatible =>
  bools.flatMap fun residualCompatible =>
  bools.flatMap fun auditCompatible =>
  bools.flatMap fun causalChainCertified =>
  bools.flatMap fun composedCredit =>
  bools.flatMap fun transitiveCausalCredit =>
  small.flatMap fun costA =>
  small.flatMap fun costB =>
  small.flatMap fun debtA =>
  small.map fun debtB =>
    { firstExecuted, secondExecuted, sourceCompatible, budgetCompatible,
      residualCompatible, auditCompatible, causalChainCertified,
      composedCredit, transitiveCausalCredit, costA, costB, debtA, debtB }

theorem composition_raw_cardinality : allCompositionCases.length = 41472 := by decide

theorem composition_accepted_cardinality :
    (allCompositionCases.filter compositionLaw).length = 10449 := by decide

theorem composition_exhaustive :
    (allCompositionCases.filter compositionLaw).all compositionLaw = true := by decide

/-! ## P4-E07: critical-pair confluence -/

structure ConfluenceCase where
  bothLegal : Bool
  joinable : Bool
  auditEquivalent : Bool
  terminalEqual : Bool
  predictiveEquivalent : Bool
  confluenceCredit : Bool
  deriving Repr, DecidableEq, BEq

def confluenceLaw (c : ConfluenceCase) : Bool :=
  c.confluenceCredit == (!c.bothLegal || (c.joinable && c.auditEquivalent))

def allConfluenceCases : List ConfluenceCase :=
  bools.flatMap fun bothLegal =>
  bools.flatMap fun joinable =>
  bools.flatMap fun auditEquivalent =>
  bools.flatMap fun terminalEqual =>
  bools.flatMap fun predictiveEquivalent =>
  bools.map fun confluenceCredit =>
    { bothLegal, joinable, auditEquivalent, terminalEqual,
      predictiveEquivalent, confluenceCredit }

theorem confluence_raw_cardinality : allConfluenceCases.length = 64 := by decide

theorem confluence_accepted_cardinality :
    (allConfluenceCases.filter confluenceLaw).length = 32 := by decide

theorem confluence_exhaustive :
    (allConfluenceCases.filter confluenceLaw).all confluenceLaw = true := by decide

/-! ## P4-E08: seed dependence -/

structure SeedCase where
  sameRules : Bool
  sameSeedPartition : Bool
  terminalEqual : Bool
  predictiveEquivalent : Bool
  presentationOnly : Bool
  seedDependenceCredit : Bool
  deriving Repr, DecidableEq, BEq

def seedLaw (c : SeedCase) : Bool :=
  (!(c.sameRules && c.sameSeedPartition) || c.terminalEqual) &&
  (!c.presentationOnly || c.predictiveEquivalent) &&
  (c.seedDependenceCredit ==
    (c.sameRules && !c.sameSeedPartition && !c.terminalEqual))

def allSeedCases : List SeedCase :=
  bools.flatMap fun sameRules =>
  bools.flatMap fun sameSeedPartition =>
  bools.flatMap fun terminalEqual =>
  bools.flatMap fun predictiveEquivalent =>
  bools.flatMap fun presentationOnly =>
  bools.map fun seedDependenceCredit =>
    { sameRules, sameSeedPartition, terminalEqual, predictiveEquivalent,
      presentationOnly, seedDependenceCredit }

theorem seed_raw_cardinality : allSeedCases.length = 64 := by decide

theorem seed_accepted_cardinality :
    (allSeedCases.filter seedLaw).length = 21 := by decide

theorem seed_exhaustive :
    (allSeedCases.filter seedLaw).all seedLaw = true := by decide

/-! ## P4-E09: route residue and holonomy -/

structure HolonomyCase where
  legalA : Bool
  legalB : Bool
  sameTarget : Bool
  sameMembers : Bool
  sameOrder : Bool
  sameBracketing : Bool
  samePredictive : Bool
  auditEquivalent : Bool
  routeResidue : Bool
  holonomyCredit : Bool
  deriving Repr, DecidableEq, BEq

def holonomyLaw (c : HolonomyCase) : Bool :=
  let changedRoute := !c.sameOrder || !c.sameBracketing
  let residue := c.legalA && c.legalB && c.sameTarget && c.sameMembers &&
    changedRoute && (!c.samePredictive || !c.auditEquivalent)
  let holonomy := residue && !c.samePredictive
  (c.routeResidue == residue) && (c.holonomyCredit == holonomy)

def allHolonomyCases : List HolonomyCase :=
  bools.flatMap fun legalA =>
  bools.flatMap fun legalB =>
  bools.flatMap fun sameTarget =>
  bools.flatMap fun sameMembers =>
  bools.flatMap fun sameOrder =>
  bools.flatMap fun sameBracketing =>
  bools.flatMap fun samePredictive =>
  bools.flatMap fun auditEquivalent =>
  bools.flatMap fun routeResidue =>
  bools.map fun holonomyCredit =>
    { legalA, legalB, sameTarget, sameMembers, sameOrder, sameBracketing,
      samePredictive, auditEquivalent, routeResidue, holonomyCredit }

theorem holonomy_raw_cardinality : allHolonomyCases.length = 1024 := by decide

theorem holonomy_accepted_cardinality :
    (allHolonomyCases.filter holonomyLaw).length = 256 := by decide

theorem holonomy_exhaustive :
    (allHolonomyCases.filter holonomyLaw).all holonomyLaw = true := by decide

/-! ## P4-E10: arrow certificate -/

structure ArrowCase where
  holonomy : Bool
  drive : Bool
  pathAsymmetry : Bool
  reversalFails : Bool
  budgeted : Bool
  audited : Bool
  arrowCredit : Bool
  deriving Repr, DecidableEq

def arrowLaw (c : ArrowCase) : Bool :=
  c.arrowCredit ==
    (c.drive && c.pathAsymmetry && c.reversalFails && c.budgeted && c.audited)

def allArrowCases : List ArrowCase :=
  bools.flatMap fun holonomy =>
  bools.flatMap fun drive =>
  bools.flatMap fun pathAsymmetry =>
  bools.flatMap fun reversalFails =>
  bools.flatMap fun budgeted =>
  bools.flatMap fun audited =>
  bools.map fun arrowCredit =>
    { holonomy, drive, pathAsymmetry, reversalFails, budgeted, audited,
      arrowCredit }

theorem arrow_raw_cardinality : allArrowCases.length = 128 := by decide

theorem arrow_accepted_cardinality :
    (allArrowCases.filter arrowLaw).length = 64 := by decide

theorem arrow_exhaustive :
    (allArrowCases.filter arrowLaw).all arrowLaw = true := by decide

private def finiteHolonomyZeroArrow : ArrowCase :=
  { holonomy := true, drive := false, pathAsymmetry := false,
    reversalFails := false, budgeted := true, audited := true,
    arrowCredit := false }

private def finiteDrivenArrow : ArrowCase :=
  { holonomy := true, drive := true, pathAsymmetry := true,
    reversalFails := true, budgeted := true, audited := true,
    arrowCredit := true }

theorem finite_holonomy_zero_arrow_exists :
    finiteHolonomyZeroArrow ∈ allArrowCases ∧
    arrowLaw finiteHolonomyZeroArrow = true ∧
    finiteHolonomyZeroArrow.holonomy = true ∧
    finiteHolonomyZeroArrow.arrowCredit = false := by decide

theorem finite_driven_arrow_exists :
    finiteDrivenArrow ∈ allArrowCases ∧
    arrowLaw finiteDrivenArrow = true ∧
    finiteDrivenArrow.arrowCredit = true := by decide

/-! ## P4-E11: cross-time contact -/

inductive FiniteTimeWitness where
  | synchronization | partialOrder | none
  deriving Repr, DecidableEq, BEq, Inhabited

private def finiteTimeWitnesses : List FiniteTimeWitness :=
  [.synchronization, .partialOrder, .none]

structure CrossTimeCase where
  witnessKind : FiniteTimeWitness
  commonOrder : Bool
  orderComparable : Bool
  payloadCrossed : Bool
  assumedSimultaneity : Bool
  admissibleReparameterization : Bool
  contactCredit : Bool
  invarianceCredit : Bool
  deriving Repr, DecidableEq, BEq

def crossTimeLaw (c : CrossTimeCase) : Bool :=
  let witnessed :=
    (c.witnessKind == .synchronization && c.commonOrder) ||
    (c.witnessKind == .partialOrder && c.orderComparable)
  let contact := witnessed && c.payloadCrossed && !c.assumedSimultaneity
  let invariant := contact && c.admissibleReparameterization
  (c.contactCredit == contact) && (c.invarianceCredit == invariant)

def allCrossTimeCases : List CrossTimeCase :=
  finiteTimeWitnesses.flatMap fun witnessKind =>
  bools.flatMap fun commonOrder =>
  bools.flatMap fun orderComparable =>
  bools.flatMap fun payloadCrossed =>
  bools.flatMap fun assumedSimultaneity =>
  bools.flatMap fun admissibleReparameterization =>
  bools.flatMap fun contactCredit =>
  bools.map fun invarianceCredit =>
    { witnessKind, commonOrder, orderComparable, payloadCrossed,
      assumedSimultaneity, admissibleReparameterization, contactCredit,
      invarianceCredit }

theorem cross_time_raw_cardinality : allCrossTimeCases.length = 384 := by decide

theorem cross_time_accepted_cardinality :
    (allCrossTimeCases.filter crossTimeLaw).length = 96 := by decide

theorem cross_time_exhaustive :
    (allCrossTimeCases.filter crossTimeLaw).all crossTimeLaw = true := by decide

/-! ## P4-E12: algebra readiness -/

structure AlgebraCase where
  generatorsDeclared : Bool
  equivalenceDeclared : Bool
  domainsDeclared : Bool
  nonredundancyProved : Bool
  semanticsDeclared : Bool
  lawsProved : Bool
  fullAlgebraCredit : Bool
  resourceFragmentCredit : Bool
  deriving Repr, DecidableEq, BEq

def algebraLaw (c : AlgebraCase) : Bool :=
  let full := c.generatorsDeclared && c.equivalenceDeclared &&
    c.domainsDeclared && c.nonredundancyProved && c.semanticsDeclared && c.lawsProved
  let fragment := c.domainsDeclared && c.lawsProved
  (c.fullAlgebraCredit == full) && (!c.resourceFragmentCredit || fragment)

def allAlgebraCases : List AlgebraCase :=
  bools.flatMap fun generatorsDeclared =>
  bools.flatMap fun equivalenceDeclared =>
  bools.flatMap fun domainsDeclared =>
  bools.flatMap fun nonredundancyProved =>
  bools.flatMap fun semanticsDeclared =>
  bools.flatMap fun lawsProved =>
  bools.flatMap fun fullAlgebraCredit =>
  bools.map fun resourceFragmentCredit =>
    { generatorsDeclared, equivalenceDeclared, domainsDeclared,
      nonredundancyProved, semanticsDeclared, lawsProved,
      fullAlgebraCredit, resourceFragmentCredit }

theorem algebra_raw_cardinality : allAlgebraCases.length = 256 := by decide

theorem algebra_accepted_cardinality :
    (allAlgebraCases.filter algebraLaw).length = 80 := by decide

theorem algebra_exhaustive :
    (allAlgebraCases.filter algebraLaw).all algebraLaw = true := by decide

end FoundationsVII.Models.Finite.Phase4
