import FoundationsVII.NoGo.All

/-!
# Bounded admission/access envelopes for FVII-SCI-02

These exhaustive finite lists support the structural proofs and preserve exact
carrier bounds.  They are not universal substitutes for the theorem modules.
-/

-- The bounded carriers below are enumerated exhaustively.  These options affect
-- elaboration resources only; they do not add assumptions or alter any theorem
-- statement.
set_option maxHeartbeats 0
set_option maxRecDepth 4000000

namespace FoundationsVII.Models.Finite.Phase2

private def bools : List Bool := [false, true]
private def smallCosts : List Nat := [0, 1, 2]

structure AccessCase where
  expressible : Bool
  present : Bool
  exposed : Bool
  recoverable : Bool
  admissible : Bool
  reachable : Bool
  occurrent : Bool
  deriving Repr, DecidableEq, BEq

def accessCoherent (c : AccessCase) : Bool :=
  (!c.occurrent || c.reachable) &&
  (!c.reachable || c.admissible) &&
  (!c.admissible || c.present) &&
  (!c.recoverable || c.exposed) &&
  (!c.exposed || c.present) &&
  (!c.present || c.expressible)

def allAccessCases : List AccessCase :=
  bools.flatMap fun expressible =>
  bools.flatMap fun present =>
  bools.flatMap fun exposed =>
  bools.flatMap fun recoverable =>
  bools.flatMap fun admissible =>
  bools.flatMap fun reachable =>
  bools.map fun occurrent =>
    { expressible, present, exposed, recoverable, admissible, reachable, occurrent }

theorem access_raw_cardinality : allAccessCases.length = 128 := by decide

theorem coherent_access_cardinality :
    (allAccessCases.filter accessCoherent).length = 14 := by decide

theorem coherent_access_cases_respect_implication_spine :
    (allAccessCases.filter accessCoherent).all accessCoherent = true := by decide

structure TransitionCase where
  sound : Bool
  executable : Bool
  guardActive : Bool
  resourcesAvailable : Bool
  reachable : Bool
  fired : Bool
  occurrent : Bool
  deriving Repr, DecidableEq, BEq

def transitionCoherent (c : TransitionCase) : Bool :=
  (!c.executable || (c.sound && c.guardActive && c.resourcesAvailable)) &&
  (!c.reachable || (c.executable && c.guardActive && c.resourcesAvailable)) &&
  (!c.fired || c.reachable) &&
  (!c.occurrent || c.fired)

def allTransitionCases : List TransitionCase :=
  bools.flatMap fun sound =>
  bools.flatMap fun executable =>
  bools.flatMap fun guardActive =>
  bools.flatMap fun resourcesAvailable =>
  bools.flatMap fun reachable =>
  bools.flatMap fun fired =>
  bools.map fun occurrent =>
    { sound, executable, guardActive, resourcesAvailable, reachable, fired, occurrent }

theorem transition_raw_cardinality : allTransitionCases.length = 128 := by decide

theorem coherent_transition_cardinality :
    (allTransitionCases.filter transitionCoherent).length = 12 := by decide

theorem coherent_transitions_respect_operational_spine :
    (allTransitionCases.filter transitionCoherent).all transitionCoherent = true := by decide

structure BootstrapCase where
  closedFamily : Bool
  seed : Bool
  generatorReachable : Bool
  externalProvision : Bool
  firstExtension : Bool
  deriving Repr, DecidableEq, BEq

def bootstrapLaw (c : BootstrapCase) : Bool :=
  !c.firstExtension || c.seed || c.generatorReachable ||
    (!c.closedFamily && c.externalProvision)

def allBootstrapCases : List BootstrapCase :=
  bools.flatMap fun closedFamily =>
  bools.flatMap fun seed =>
  bools.flatMap fun generatorReachable =>
  bools.flatMap fun externalProvision =>
  bools.map fun firstExtension =>
    { closedFamily, seed, generatorReachable, externalProvision, firstExtension }

theorem bootstrap_raw_cardinality : allBootstrapCases.length = 32 := by decide

theorem bootstrap_admissible_cardinality :
    (allBootstrapCases.filter bootstrapLaw).length = 29 := by decide

theorem bootstrap_law_exhaustive :
    (allBootstrapCases.filter bootstrapLaw).all bootstrapLaw = true := by decide

structure CommitmentCase where
  preregistered : Bool
  precedesEvidence : Bool
  retrospective : Bool
  taskBlind : Bool
  outcomeIndependent : Bool
  symmetryCertified : Bool
  controlMatched : Bool
  prospectiveCredit : Bool
  deriving Repr, DecidableEq, BEq

def commitmentLaw (c : CommitmentCase) : Bool :=
  !c.prospectiveCredit ||
    (c.preregistered && c.precedesEvidence && !c.retrospective &&
      c.taskBlind && c.outcomeIndependent && c.symmetryCertified &&
      c.controlMatched)

def allCommitmentCases : List CommitmentCase :=
  bools.flatMap fun preregistered =>
  bools.flatMap fun precedesEvidence =>
  bools.flatMap fun retrospective =>
  bools.flatMap fun taskBlind =>
  bools.flatMap fun outcomeIndependent =>
  bools.flatMap fun symmetryCertified =>
  bools.flatMap fun controlMatched =>
  bools.map fun prospectiveCredit =>
    { preregistered, precedesEvidence, retrospective, taskBlind,
      outcomeIndependent, symmetryCertified, controlMatched,
      prospectiveCredit }

theorem commitment_raw_cardinality : allCommitmentCases.length = 256 := by decide

theorem commitment_admissible_cardinality :
    (allCommitmentCases.filter commitmentLaw).length = 129 := by decide

theorem no_retrospective_self_certification_exhaustive :
    (allCommitmentCases.filter commitmentLaw).all commitmentLaw = true := by decide

structure OriginCase where
  sameOrigin : Bool
  commonCarrier : Bool
  commonInstrument : Bool
  leftAccess : Bool
  rightAccess : Bool
  leftPeer : Bool
  rightPeer : Bool
  sourceIndependent : Bool
  deriving Repr, DecidableEq, BEq

def originLaw (c : OriginCase) : Bool :=
  c.sourceIndependent != c.sameOrigin

def allOriginCases : List OriginCase :=
  bools.flatMap fun sameOrigin =>
  bools.flatMap fun commonCarrier =>
  bools.flatMap fun commonInstrument =>
  bools.flatMap fun leftAccess =>
  bools.flatMap fun rightAccess =>
  bools.flatMap fun leftPeer =>
  bools.flatMap fun rightPeer =>
  bools.map fun sourceIndependent =>
    { sameOrigin, commonCarrier, commonInstrument, leftAccess, rightAccess,
      leftPeer, rightPeer, sourceIndependent }

theorem origin_canonical_cardinality : allOriginCases.length = 256 := by decide

theorem origin_raw_labelled_cardinality :
    allOriginCases.length * 2 = 512 := by decide

theorem origin_admissible_cardinality :
    (allOriginCases.filter originLaw).length = 128 := by decide

theorem source_independence_is_complementary_to_same_origin_in_canonical_family :
    (allOriginCases.filter originLaw).all originLaw = true := by decide

structure TotalityCase where
  sourceTotal : Bool
  targetPartial : Bool
  targetSelfOwned : Bool
  adapterCertified : Bool
  transferLicensed : Bool
  deriving Repr, DecidableEq, BEq

def totalityLaw (c : TotalityCase) : Bool :=
  !c.transferLicensed ||
    (c.sourceTotal && c.targetSelfOwned &&
      (!c.targetPartial || c.adapterCertified))

def allTotalityCases : List TotalityCase :=
  bools.flatMap fun sourceTotal =>
  bools.flatMap fun targetPartial =>
  bools.flatMap fun targetSelfOwned =>
  bools.flatMap fun adapterCertified =>
  bools.map fun transferLicensed =>
    { sourceTotal, targetPartial, targetSelfOwned,
      adapterCertified, transferLicensed }

theorem totality_raw_cardinality : allTotalityCases.length = 32 := by decide

theorem totality_admissible_cardinality :
    (allTotalityCases.filter totalityLaw).length = 19 := by decide

theorem totality_transfer_requires_adapter_on_partial_targets :
    (allTotalityCases.filter totalityLaw).all totalityLaw = true := by decide

structure HorizonCase where
  complete : Bool
  familyClosed : Bool
  detectorPower : Bool
  occurrenceWithin : Bool
  occurrenceAfter : Bool
  universalNegativeCredit : Bool
  deriving Repr, DecidableEq, BEq

def horizonLaw (c : HorizonCase) : Bool :=
  !c.universalNegativeCredit ||
    (c.complete && c.familyClosed && c.detectorPower &&
      !c.occurrenceWithin && !c.occurrenceAfter)

def allHorizonCases : List HorizonCase :=
  bools.flatMap fun complete =>
  bools.flatMap fun familyClosed =>
  bools.flatMap fun detectorPower =>
  bools.flatMap fun occurrenceWithin =>
  bools.flatMap fun occurrenceAfter =>
  bools.map fun universalNegativeCredit =>
    { complete, familyClosed, detectorPower, occurrenceWithin,
      occurrenceAfter, universalNegativeCredit }

theorem horizon_raw_cardinality : allHorizonCases.length = 64 := by decide

theorem horizon_admissible_cardinality :
    (allHorizonCases.filter horizonLaw).length = 33 := by decide

theorem negative_force_requires_closed_powerful_complete_null :
    (allHorizonCases.filter horizonLaw).all horizonLaw = true := by decide

structure ObserverCase where
  occupied : Nat
  charged : Nat
  nativeCredit : Bool
  deriving Repr, DecidableEq, BEq

def observerLaw (c : ObserverCase) : Bool :=
  !c.nativeCredit || decide (c.occupied ≤ c.charged)

def allObserverCases : List ObserverCase :=
  smallCosts.flatMap fun occupied =>
  smallCosts.flatMap fun charged =>
  bools.map fun nativeCredit => { occupied, charged, nativeCredit }

theorem observer_raw_cardinality : allObserverCases.length = 18 := by decide

theorem observer_admissible_cardinality :
    (allObserverCases.filter observerLaw).length = 15 := by decide

theorem native_credit_requires_priced_occupancy :
    (allObserverCases.filter observerLaw).all observerLaw = true := by decide

structure SettlementCase where
  allocated : Nat
  spent : Nat
  occupied : Nat
  refunded : Nat
  settled : Bool
  deriving Repr, DecidableEq, BEq

def settlementLaw (c : SettlementCase) : Bool :=
  !c.settled || decide (c.spent + c.occupied + c.refunded = c.allocated)

def allSettlementCases : List SettlementCase :=
  smallCosts.flatMap fun allocated =>
  smallCosts.flatMap fun spent =>
  smallCosts.flatMap fun occupied =>
  smallCosts.flatMap fun refunded =>
  bools.map fun settled => { allocated, spent, occupied, refunded, settled }

theorem settlement_raw_cardinality : allSettlementCases.length = 162 := by decide

theorem settlement_admissible_cardinality :
    (allSettlementCases.filter settlementLaw).length = 91 := by decide

theorem settled_failures_conserve_declared_budget :
    (allSettlementCases.filter settlementLaw).all settlementLaw = true := by decide

end FoundationsVII.Models.Finite.Phase2
