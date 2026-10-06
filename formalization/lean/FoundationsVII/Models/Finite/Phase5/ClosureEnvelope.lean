import FoundationsVII.Corollaries.All

/-!
# Final bounded cross-family closure envelopes

These eleven finite carriers independently mirror the Python Phase-5 model.
They test the conjunctions and separations used by the final corollaries.  The
results are exhaustive only over the declared finite universes below and do not
replace the structural theorem modules.
-/

set_option maxHeartbeats 0
set_option maxRecDepth 4000000

namespace FoundationsVII.Models.Finite.Phase5

private def bools : List Bool := [false, true]
private def small : List Nat := [0, 1, 2]
private def domainCounts : List Nat := [2, 3]

/-! ## P5-E01: prospective admission plus strict join -/

structure ProspectiveJoinCase where
  preregistered : Bool
  precedes : Bool
  retrospective : Bool
  lawfulAdmission : Bool
  sourceAligned : Bool
  contact : Bool
  composite : Bool
  retention : Bool
  antiProduct : Bool
  sourceIndependent : Bool
  budgetSettled : Bool
  paymentFullyCredited : Bool
  integratedCredit : Bool
  deriving Repr, DecidableEq, BEq

def prospectiveJoinExact (c : ProspectiveJoinCase) : Bool :=
  c.preregistered && c.precedes && !c.retrospective && c.lawfulAdmission &&
  c.sourceAligned && c.contact && c.composite && c.retention && c.antiProduct &&
  c.sourceIndependent && c.budgetSettled && c.paymentFullyCredited

def prospectiveJoinLaw (c : ProspectiveJoinCase) : Bool :=
  c.integratedCredit == prospectiveJoinExact c

def allProspectiveJoinCases : List ProspectiveJoinCase :=
  bools.flatMap fun preregistered =>
  bools.flatMap fun precedes =>
  bools.flatMap fun retrospective =>
  bools.flatMap fun lawfulAdmission =>
  bools.flatMap fun sourceAligned =>
  bools.flatMap fun contact =>
  bools.flatMap fun composite =>
  bools.flatMap fun retention =>
  bools.flatMap fun antiProduct =>
  bools.flatMap fun sourceIndependent =>
  bools.flatMap fun budgetSettled =>
  bools.flatMap fun paymentFullyCredited =>
  bools.map fun integratedCredit =>
    { preregistered, precedes, retrospective, lawfulAdmission, sourceAligned,
      contact, composite, retention, antiProduct, sourceIndependent,
      budgetSettled, paymentFullyCredited, integratedCredit }

theorem prospectiveJoin_raw_cardinality : allProspectiveJoinCases.length = 8192 := by decide

theorem prospectiveJoin_accepted_cardinality :
    (allProspectiveJoinCases.filter prospectiveJoinLaw).length = 4096 := by decide

theorem prospectiveJoin_exhaustive :
    (allProspectiveJoinCases.filter prospectiveJoinLaw).all prospectiveJoinLaw = true := by decide

/-! ## P5-E02: source, budget, observer pricing, and finite capacity -/

structure SourceBudgetCapacityCase where
  sourceIndependent : Bool
  budgetSettled : Bool
  ledgerNonempty : Bool
  allEntriesCredited : Bool
  observerPriced : Bool
  strictJoinCredit : Bool
  capacityCredit : Bool
  capacity : Nat
  liveJoinCount : Nat
  minimumPositiveCost : Nat
  deriving Repr, DecidableEq, BEq

def sourceBudgetStrictExact (c : SourceBudgetCapacityCase) : Bool :=
  c.sourceIndependent && c.budgetSettled && c.ledgerNonempty &&
  c.allEntriesCredited && c.observerPriced

def capacityExact (c : SourceBudgetCapacityCase) : Bool :=
  decide (0 < c.minimumPositiveCost) &&
  decide (c.liveJoinCount * c.minimumPositiveCost ≤ c.capacity)

def sourceBudgetCapacityLaw (c : SourceBudgetCapacityCase) : Bool :=
  (c.strictJoinCredit == sourceBudgetStrictExact c) &&
  (c.capacityCredit == capacityExact c)

def allSourceBudgetCapacityCases : List SourceBudgetCapacityCase :=
  bools.flatMap fun sourceIndependent =>
  bools.flatMap fun budgetSettled =>
  bools.flatMap fun ledgerNonempty =>
  bools.flatMap fun allEntriesCredited =>
  bools.flatMap fun observerPriced =>
  bools.flatMap fun strictJoinCredit =>
  bools.flatMap fun capacityCredit =>
  small.flatMap fun capacity =>
  small.flatMap fun liveJoinCount =>
  small.map fun minimumPositiveCost =>
    { sourceIndependent, budgetSettled, ledgerNonempty, allEntriesCredited,
      observerPriced, strictJoinCredit, capacityCredit, capacity,
      liveJoinCount, minimumPositiveCost }

theorem sourceBudgetCapacity_raw_cardinality : allSourceBudgetCapacityCases.length = 3456 := by decide

theorem sourceBudgetCapacity_accepted_cardinality :
    (allSourceBudgetCapacityCases.filter sourceBudgetCapacityLaw).length = 864 := by decide

theorem sourceBudgetCapacity_exhaustive :
    (allSourceBudgetCapacityCases.filter sourceBudgetCapacityLaw).all sourceBudgetCapacityLaw = true := by decide

/-! ## P5-E03: certified non-interaction -/

structure CertifiedNoninteractionCase where
  noContact : Bool
  exactCoverage : Bool
  familyClosed : Bool
  detectorPower : Bool
  budgetSufficient : Bool
  horizonComplete : Bool
  escapeRoutesRecorded : Bool
  certifiedNoninteraction : Bool
  strictJoinCredit : Bool
  deriving Repr, DecidableEq, BEq

def certifiedNoninteractionExact (c : CertifiedNoninteractionCase) : Bool :=
  c.noContact && c.exactCoverage && c.familyClosed && c.detectorPower &&
  c.budgetSufficient && c.horizonComplete && c.escapeRoutesRecorded

def certifiedNoninteractionLaw (c : CertifiedNoninteractionCase) : Bool :=
  (c.certifiedNoninteraction == certifiedNoninteractionExact c) &&
  (!(certifiedNoninteractionExact c) || !c.strictJoinCredit)

def allCertifiedNoninteractionCases : List CertifiedNoninteractionCase :=
  bools.flatMap fun noContact =>
  bools.flatMap fun exactCoverage =>
  bools.flatMap fun familyClosed =>
  bools.flatMap fun detectorPower =>
  bools.flatMap fun budgetSufficient =>
  bools.flatMap fun horizonComplete =>
  bools.flatMap fun escapeRoutesRecorded =>
  bools.flatMap fun certifiedNoninteraction =>
  bools.map fun strictJoinCredit =>
    { noContact, exactCoverage, familyClosed, detectorPower, budgetSufficient,
      horizonComplete, escapeRoutesRecorded, certifiedNoninteraction,
      strictJoinCredit }

theorem certifiedNoninteraction_raw_cardinality : allCertifiedNoninteractionCases.length = 512 := by decide

theorem certifiedNoninteraction_accepted_cardinality :
    (allCertifiedNoninteractionCases.filter certifiedNoninteractionLaw).length = 255 := by decide

theorem certifiedNoninteraction_exhaustive :
    (allCertifiedNoninteractionCases.filter certifiedNoninteractionLaw).all certifiedNoninteractionLaw = true := by decide

/-! ## P5-E04: residual-aware enablement composition -/

structure ResidualEnablementCase where
  firstExecuted : Bool
  secondExecuted : Bool
  sourceCompatible : Bool
  budgetCompatible : Bool
  residualCompatible : Bool
  auditCompatible : Bool
  oldResidualRetained : Bool
  crossTermCreated : Bool
  relabelOnly : Bool
  composedCredit : Bool
  zeroResidualClaim : Bool
  debtA : Nat
  debtB : Nat
  deriving Repr, DecidableEq, BEq

def residualEnablementComposable (c : ResidualEnablementCase) : Bool :=
  c.firstExecuted && c.secondExecuted && c.sourceCompatible &&
  c.budgetCompatible && c.residualCompatible && c.auditCompatible

def residualEnablementLaw (c : ResidualEnablementCase) : Bool :=
  let debt := c.debtA + c.debtB
  (c.composedCredit == residualEnablementComposable c) &&
  (!residualEnablementComposable c || c.oldResidualRetained) &&
  (!(c.crossTermCreated && !c.relabelOnly) ||
    (decide (0 < debt) && !c.zeroResidualClaim)) &&
  (!c.zeroResidualClaim || decide (debt = 0))

def allResidualEnablementCases : List ResidualEnablementCase :=
  bools.flatMap fun firstExecuted =>
  bools.flatMap fun secondExecuted =>
  bools.flatMap fun sourceCompatible =>
  bools.flatMap fun budgetCompatible =>
  bools.flatMap fun residualCompatible =>
  bools.flatMap fun auditCompatible =>
  bools.flatMap fun oldResidualRetained =>
  bools.flatMap fun crossTermCreated =>
  bools.flatMap fun relabelOnly =>
  bools.flatMap fun composedCredit =>
  bools.flatMap fun zeroResidualClaim =>
  small.flatMap fun debtA =>
  small.map fun debtB =>
    { firstExecuted, secondExecuted, sourceCompatible, budgetCompatible,
      residualCompatible, auditCompatible, oldResidualRetained,
      crossTermCreated, relabelOnly, composedCredit, zeroResidualClaim,
      debtA, debtB }

theorem residualEnablement_raw_cardinality : allResidualEnablementCases.length = 18432 := by decide

theorem residualEnablement_accepted_cardinality :
    (allResidualEnablementCases.filter residualEnablementLaw).length = 4826 := by decide

theorem residualEnablement_exhaustive :
    (allResidualEnablementCases.filter residualEnablementLaw).all residualEnablementLaw = true := by decide

/-! ## P5-E05: parent refinement and descent -/

inductive FiniteRefinementEffect where
  | preserves | strengthens | weakens | destroys
  deriving Repr, DecidableEq, BEq, Inhabited

private def finiteRefinementEffects : List FiniteRefinementEffect :=
  [.preserves, .strengthens, .weakens, .destroys]

structure RefinementDescentCase where
  effect : FiniteRefinementEffect
  refinementWellFormed : Bool
  transmissionValid : Bool
  compatibilityPreserved : Bool
  strictnessPreserved : Bool
  sourcePreserved : Bool
  budgetPreserved : Bool
  squareCommutes : Bool
  preservationCredit : Bool
  unconditionalMonotonicityClaim : Bool
  deriving Repr, DecidableEq, BEq

def finiteRefinementPreserving (effect : FiniteRefinementEffect) : Bool :=
  effect == .preserves || effect == .strengthens

def refinementDescentExact (c : RefinementDescentCase) : Bool :=
  finiteRefinementPreserving c.effect && c.refinementWellFormed &&
  c.transmissionValid && c.compatibilityPreserved && c.strictnessPreserved &&
  c.sourcePreserved && c.budgetPreserved && c.squareCommutes

def refinementDescentLaw (c : RefinementDescentCase) : Bool :=
  (c.preservationCredit == refinementDescentExact c) &&
  !c.unconditionalMonotonicityClaim &&
  (!(c.effect == .destroys && c.refinementWellFormed) ||
    (!c.compatibilityPreserved || !c.strictnessPreserved))

def allRefinementDescentCases : List RefinementDescentCase :=
  finiteRefinementEffects.flatMap fun effect =>
  bools.flatMap fun refinementWellFormed =>
  bools.flatMap fun transmissionValid =>
  bools.flatMap fun compatibilityPreserved =>
  bools.flatMap fun strictnessPreserved =>
  bools.flatMap fun sourcePreserved =>
  bools.flatMap fun budgetPreserved =>
  bools.flatMap fun squareCommutes =>
  bools.flatMap fun preservationCredit =>
  bools.map fun unconditionalMonotonicityClaim =>
    { effect, refinementWellFormed, transmissionValid, compatibilityPreserved,
      strictnessPreserved, sourcePreserved, budgetPreserved, squareCommutes,
      preservationCredit, unconditionalMonotonicityClaim }

theorem refinementDescent_raw_cardinality : allRefinementDescentCases.length = 2048 := by decide

theorem refinementDescent_accepted_cardinality :
    (allRefinementDescentCases.filter refinementDescentLaw).length = 496 := by decide

theorem refinementDescent_exhaustive :
    (allRefinementDescentCases.filter refinementDescentLaw).all refinementDescentLaw = true := by decide

/-! ## P5-E06: no-free-join -/

structure NoFreeJoinCase where
  closedFamily : Bool
  seed : Bool
  generator : Bool
  externalProvision : Bool
  permitted : Bool
  positiveCost : Bool
  paid : Bool
  zeroCostCertified : Bool
  firstExtension : Bool
  paymentCredit : Bool
  joinCredit : Bool
  freeJoinCredit : Bool
  deriving Repr, DecidableEq, BEq

def noFreeJoinExtensionExact (c : NoFreeJoinCase) : Bool :=
  c.permitted &&
    (c.seed || c.generator || (!c.closedFamily && c.externalProvision))

def noFreeJoinPaymentExact (c : NoFreeJoinCase) : Bool :=
  (c.positiveCost && c.paid) || (!c.positiveCost && c.zeroCostCertified)

def noFreeJoinExact (c : NoFreeJoinCase) : Bool :=
  noFreeJoinExtensionExact c && noFreeJoinPaymentExact c

def noFreeJoinIllicitCredit (c : NoFreeJoinCase) : Bool :=
  noFreeJoinExact c && !c.seed && !c.generator && !c.externalProvision &&
  !c.paid && !c.zeroCostCertified

def noFreeJoinLaw (c : NoFreeJoinCase) : Bool :=
  (c.firstExtension == noFreeJoinExtensionExact c) &&
  (c.paymentCredit == noFreeJoinPaymentExact c) &&
  (c.joinCredit == noFreeJoinExact c) &&
  (c.freeJoinCredit == noFreeJoinIllicitCredit c) &&
  !c.freeJoinCredit

def allNoFreeJoinCases : List NoFreeJoinCase :=
  bools.flatMap fun closedFamily =>
  bools.flatMap fun seed =>
  bools.flatMap fun generator =>
  bools.flatMap fun externalProvision =>
  bools.flatMap fun permitted =>
  bools.flatMap fun positiveCost =>
  bools.flatMap fun paid =>
  bools.flatMap fun zeroCostCertified =>
  bools.flatMap fun firstExtension =>
  bools.flatMap fun paymentCredit =>
  bools.flatMap fun joinCredit =>
  bools.map fun freeJoinCredit =>
    { closedFamily, seed, generator, externalProvision, permitted, positiveCost,
      paid, zeroCostCertified, firstExtension, paymentCredit, joinCredit,
      freeJoinCredit }

theorem noFreeJoin_raw_cardinality : allNoFreeJoinCases.length = 4096 := by decide

theorem noFreeJoin_accepted_cardinality :
    (allNoFreeJoinCases.filter noFreeJoinLaw).length = 256 := by decide

theorem noFreeJoin_exhaustive :
    (allNoFreeJoinCases.filter noFreeJoinLaw).all noFreeJoinLaw = true := by decide

/-! ## P5-E07: strict join, holonomy, and arrows -/

structure HolonomyArrowCase where
  strictJoin : Bool
  holonomy : Bool
  drive : Bool
  pathAsymmetry : Bool
  reversalFails : Bool
  budgeted : Bool
  audited : Bool
  arrowCredit : Bool
  joinOnlyArrowClaim : Bool
  holonomyOnlyArrowClaim : Bool
  deriving Repr, DecidableEq, BEq

def holonomyArrowExact (c : HolonomyArrowCase) : Bool :=
  c.drive && c.pathAsymmetry && c.reversalFails && c.budgeted && c.audited

def holonomyArrowLaw (c : HolonomyArrowCase) : Bool :=
  (c.arrowCredit == holonomyArrowExact c) &&
  !(c.strictJoin && !c.drive && c.joinOnlyArrowClaim) &&
  !(c.holonomy && !c.drive && c.holonomyOnlyArrowClaim)

def allHolonomyArrowCases : List HolonomyArrowCase :=
  bools.flatMap fun strictJoin =>
  bools.flatMap fun holonomy =>
  bools.flatMap fun drive =>
  bools.flatMap fun pathAsymmetry =>
  bools.flatMap fun reversalFails =>
  bools.flatMap fun budgeted =>
  bools.flatMap fun audited =>
  bools.flatMap fun arrowCredit =>
  bools.flatMap fun joinOnlyArrowClaim =>
  bools.map fun holonomyOnlyArrowClaim =>
    { strictJoin, holonomy, drive, pathAsymmetry, reversalFails, budgeted,
      audited, arrowCredit, joinOnlyArrowClaim, holonomyOnlyArrowClaim }

theorem holonomyArrow_raw_cardinality : allHolonomyArrowCases.length = 1024 := by decide

theorem holonomyArrow_accepted_cardinality :
    (allHolonomyArrowCases.filter holonomyArrowLaw).length = 400 := by decide

theorem holonomyArrow_exhaustive :
    (allHolonomyArrowCases.filter holonomyArrowLaw).all holonomyArrowLaw = true := by decide

/-! ## P5-E08: reachability and scoped negative force -/

structure NegativeForceCase where
  sound : Bool
  executable : Bool
  guardActive : Bool
  reachable : Bool
  fired : Bool
  occurrent : Bool
  completeHorizon : Bool
  familyClosed : Bool
  detectorPower : Bool
  noOccurrenceWithin : Bool
  noOccurrenceAfter : Bool
  globalNegativeCredit : Bool
  deriving Repr, DecidableEq, BEq

def negativeOperationalCoherent (c : NegativeForceCase) : Bool :=
  (!c.executable || c.sound) &&
  (!c.reachable || (c.executable && c.guardActive)) &&
  (!c.fired || c.reachable) &&
  (!c.occurrent || c.fired)

def negativeForceExact (c : NegativeForceCase) : Bool :=
  c.completeHorizon && c.familyClosed && c.detectorPower &&
  c.noOccurrenceWithin && c.noOccurrenceAfter

def negativeForceLaw (c : NegativeForceCase) : Bool :=
  negativeOperationalCoherent c &&
  (c.globalNegativeCredit == negativeForceExact c)

def allNegativeForceCases : List NegativeForceCase :=
  bools.flatMap fun sound =>
  bools.flatMap fun executable =>
  bools.flatMap fun guardActive =>
  bools.flatMap fun reachable =>
  bools.flatMap fun fired =>
  bools.flatMap fun occurrent =>
  bools.flatMap fun completeHorizon =>
  bools.flatMap fun familyClosed =>
  bools.flatMap fun detectorPower =>
  bools.flatMap fun noOccurrenceWithin =>
  bools.flatMap fun noOccurrenceAfter =>
  bools.map fun globalNegativeCredit =>
    { sound, executable, guardActive, reachable, fired, occurrent,
      completeHorizon, familyClosed, detectorPower, noOccurrenceWithin,
      noOccurrenceAfter, globalNegativeCredit }

theorem negativeForce_raw_cardinality : allNegativeForceCases.length = 4096 := by decide

theorem negativeForce_accepted_cardinality :
    (allNegativeForceCases.filter negativeForceLaw).length = 288 := by decide

theorem negativeForce_exhaustive :
    (allNegativeForceCases.filter negativeForceLaw).all negativeForceLaw = true := by decide

/-! ## P5-E09: observer pricing and endogeny -/

structure ObserverEndogenyCase where
  nativeSource : Bool
  carried : Bool
  reachable : Bool
  executed : Bool
  audited : Bool
  budgeted : Bool
  boundaryClosed : Bool
  hiddenObserver : Bool
  nativeCredit : Bool
  endogenousCredit : Bool
  jointCredit : Bool
  occupied : Nat
  charged : Nat
  deriving Repr, DecidableEq, BEq

def observerNativeExact (c : ObserverEndogenyCase) : Bool :=
  c.nativeSource && decide (c.charged = c.occupied)

def observerEndogenyExact (c : ObserverEndogenyCase) : Bool :=
  c.carried && c.reachable && c.executed && c.audited && c.budgeted &&
  c.boundaryClosed && !c.hiddenObserver

def observerEndogenyLaw (c : ObserverEndogenyCase) : Bool :=
  (c.nativeCredit == observerNativeExact c) &&
  (c.endogenousCredit == observerEndogenyExact c) &&
  (c.jointCredit == (observerNativeExact c && observerEndogenyExact c))

def allObserverEndogenyCases : List ObserverEndogenyCase :=
  bools.flatMap fun nativeSource =>
  bools.flatMap fun carried =>
  bools.flatMap fun reachable =>
  bools.flatMap fun executed =>
  bools.flatMap fun audited =>
  bools.flatMap fun budgeted =>
  bools.flatMap fun boundaryClosed =>
  bools.flatMap fun hiddenObserver =>
  bools.flatMap fun nativeCredit =>
  bools.flatMap fun endogenousCredit =>
  bools.flatMap fun jointCredit =>
  small.flatMap fun occupied =>
  small.map fun charged =>
    { nativeSource, carried, reachable, executed, audited, budgeted,
      boundaryClosed, hiddenObserver, nativeCredit, endogenousCredit,
      jointCredit, occupied, charged }

theorem observerEndogeny_raw_cardinality : allObserverEndogenyCases.length = 18432 := by decide

theorem observerEndogeny_accepted_cardinality :
    (allObserverEndogenyCases.filter observerEndogenyLaw).length = 2304 := by decide

theorem observerEndogeny_exhaustive :
    (allObserverEndogenyCases.filter observerEndogenyLaw).all observerEndogenyLaw = true := by decide

/-! ## P5-E10: three-domain order and confluence -/

structure ThreeDomainConfluenceCase where
  sameRules : Bool
  sameSeedPartition : Bool
  pairABResolved : Bool
  pairBCResolved : Bool
  pairACResolved : Bool
  allPairsChecked : Bool
  familyClosed : Bool
  auditEquivalent : Bool
  terminalEqual : Bool
  orderResidue : Bool
  holonomy : Bool
  globalConfluenceCredit : Bool
  seedDependenceCredit : Bool
  deriving Repr, DecidableEq, BEq

private def rawPairAssignments : List (Bool × Bool) :=
  [(false, false), (false, true), (true, false), (true, true)]

private def canonicalPairAssignments : List (Bool × Bool) :=
  [(false, false), (false, true), (true, true)]

def threeDomainConfluenceExact (c : ThreeDomainConfluenceCase) : Bool :=
  c.allPairsChecked && c.familyClosed && c.auditEquivalent &&
  c.pairABResolved && c.pairBCResolved && c.pairACResolved

def threeDomainSeedDependenceExact (c : ThreeDomainConfluenceCase) : Bool :=
  c.sameRules && !c.sameSeedPartition && !c.terminalEqual

def threeDomainConfluenceLaw (c : ThreeDomainConfluenceCase) : Bool :=
  (c.globalConfluenceCredit == threeDomainConfluenceExact c) &&
  (c.seedDependenceCredit == threeDomainSeedDependenceExact c) &&
  (!c.holonomy || c.orderResidue)

private def buildThreeDomainCases (pairs : List (Bool × Bool)) : List ThreeDomainConfluenceCase :=
  bools.flatMap fun sameRules =>
  bools.flatMap fun sameSeedPartition =>
  pairs.flatMap fun pair =>
  bools.flatMap fun pairACResolved =>
  bools.flatMap fun allPairsChecked =>
  bools.flatMap fun familyClosed =>
  bools.flatMap fun auditEquivalent =>
  bools.flatMap fun terminalEqual =>
  bools.flatMap fun orderResidue =>
  bools.flatMap fun holonomy =>
  bools.flatMap fun globalConfluenceCredit =>
  bools.map fun seedDependenceCredit =>
    { sameRules, sameSeedPartition, pairABResolved := pair.1,
      pairBCResolved := pair.2, pairACResolved, allPairsChecked,
      familyClosed, auditEquivalent, terminalEqual, orderResidue, holonomy,
      globalConfluenceCredit, seedDependenceCredit }

def allRawThreeDomainConfluenceCases : List ThreeDomainConfluenceCase :=
  buildThreeDomainCases rawPairAssignments

def allThreeDomainConfluenceCases : List ThreeDomainConfluenceCase :=
  buildThreeDomainCases canonicalPairAssignments

theorem threeDomainConfluence_raw_cardinality : allRawThreeDomainConfluenceCases.length = 8192 := by decide

theorem threeDomainConfluence_canonical_cardinality : allThreeDomainConfluenceCases.length = 6144 := by decide

theorem threeDomainConfluence_accepted_cardinality :
    (allThreeDomainConfluenceCases.filter threeDomainConfluenceLaw).length = 1152 := by decide

theorem threeDomainConfluence_exhaustive :
    (allThreeDomainConfluenceCases.filter threeDomainConfluenceLaw).all threeDomainConfluenceLaw = true := by decide

/-! ## P5-E11: integrated release profiles -/

structure IntegratedDomainCase where
  domainCount : Nat
  allDomainsAdmissible : Bool
  contactGraphClosed : Bool
  witnessesComplete : Bool
  sourcesTyped : Bool
  budgeted : Bool
  observerPriced : Bool
  residualsAccounted : Bool
  allJoinsCertified : Bool
  allNegativesScoped : Bool
  systemCredit : Bool
  joinCount : Nat
  residualCount : Nat
  deriving Repr, DecidableEq, BEq

def integratedDomainExact (c : IntegratedDomainCase) : Bool :=
  c.allDomainsAdmissible && c.contactGraphClosed && c.witnessesComplete &&
  c.sourcesTyped && c.budgeted && c.observerPriced &&
  (decide (c.residualCount = 0) || c.residualsAccounted) &&
  (decide (c.joinCount = 0) || c.allJoinsCertified) &&
  c.allNegativesScoped

def integratedDomainLaw (c : IntegratedDomainCase) : Bool :=
  (c.systemCredit == integratedDomainExact c) &&
  (decide (c.residualCount = 0) || c.residualsAccounted)

def allIntegratedDomainCases : List IntegratedDomainCase :=
  domainCounts.flatMap fun domainCount =>
  bools.flatMap fun allDomainsAdmissible =>
  bools.flatMap fun contactGraphClosed =>
  bools.flatMap fun witnessesComplete =>
  bools.flatMap fun sourcesTyped =>
  bools.flatMap fun budgeted =>
  bools.flatMap fun observerPriced =>
  bools.flatMap fun residualsAccounted =>
  bools.flatMap fun allJoinsCertified =>
  bools.flatMap fun allNegativesScoped =>
  bools.flatMap fun systemCredit =>
  small.flatMap fun joinCount =>
  small.map fun residualCount =>
    { domainCount, allDomainsAdmissible, contactGraphClosed,
      witnessesComplete, sourcesTyped, budgeted, observerPriced,
      residualsAccounted, allJoinsCertified, allNegativesScoped,
      systemCredit, joinCount, residualCount }

theorem integratedDomain_raw_cardinality : allIntegratedDomainCases.length = 18432 := by decide

theorem integratedDomain_accepted_cardinality :
    (allIntegratedDomainCases.filter integratedDomainLaw).length = 6144 := by decide

theorem integratedDomain_exhaustive :
    (allIntegratedDomainCases.filter integratedDomainLaw).all integratedDomainLaw = true := by decide

/-! ## Final finite closure summaries -/

def finalRawCardinality : Nat :=
  allProspectiveJoinCases.length + allSourceBudgetCapacityCases.length +
  allCertifiedNoninteractionCases.length + allResidualEnablementCases.length +
  allRefinementDescentCases.length + allNoFreeJoinCases.length +
  allHolonomyArrowCases.length + allNegativeForceCases.length +
  allObserverEndogenyCases.length + allRawThreeDomainConfluenceCases.length +
  allIntegratedDomainCases.length

def finalCanonicalCardinality : Nat :=
  allProspectiveJoinCases.length + allSourceBudgetCapacityCases.length +
  allCertifiedNoninteractionCases.length + allResidualEnablementCases.length +
  allRefinementDescentCases.length + allNoFreeJoinCases.length +
  allHolonomyArrowCases.length + allNegativeForceCases.length +
  allObserverEndogenyCases.length + allThreeDomainConfluenceCases.length +
  allIntegratedDomainCases.length

def finalAcceptedCardinality : Nat :=
  (allProspectiveJoinCases.filter prospectiveJoinLaw).length +
  (allSourceBudgetCapacityCases.filter sourceBudgetCapacityLaw).length +
  (allCertifiedNoninteractionCases.filter certifiedNoninteractionLaw).length +
  (allResidualEnablementCases.filter residualEnablementLaw).length +
  (allRefinementDescentCases.filter refinementDescentLaw).length +
  (allNoFreeJoinCases.filter noFreeJoinLaw).length +
  (allHolonomyArrowCases.filter holonomyArrowLaw).length +
  (allNegativeForceCases.filter negativeForceLaw).length +
  (allObserverEndogenyCases.filter observerEndogenyLaw).length +
  (allThreeDomainConfluenceCases.filter threeDomainConfluenceLaw).length +
  (allIntegratedDomainCases.filter integratedDomainLaw).length

theorem final_raw_cardinality : finalRawCardinality = 86912 := by decide

theorem final_canonical_cardinality : finalCanonicalCardinality = 84864 := by decide

theorem final_accepted_cardinality : finalAcceptedCardinality = 21081 := by decide

theorem final_rejected_cardinality :
    finalCanonicalCardinality - finalAcceptedCardinality = 63783 := by decide

end FoundationsVII.Models.Finite.Phase5
