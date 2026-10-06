import FoundationsVII.NoGo.All

/-!
# Bounded contact/join envelopes for FVII-SCI-03

Each list exhausts one declared finite carrier and mirrors the independent
Python implementation. These finite computations support, but do not replace,
the structural theorem modules.
-/

-- The largest bounded carrier contains 65,536 canonical cases.  These

-- options affect elaboration resources only; they do not add assumptions

-- or alter any theorem statement.

set_option maxHeartbeats 0
set_option maxRecDepth 4000000

namespace FoundationsVII.Models.Finite.Phase3

private def bools : List Bool := [false, true]
private def small : List Nat := [0, 1, 2]
private def capacityValues : List Nat := [0, 1, 2, 3, 4]
private def minimumCosts : List Nat := [0, 1, 2, 3]

/-! ## P3-E01: contact and peer transport -/

structure ContactTransportCase where
  compatible : Bool
  contact : Bool
  payloadCertified : Bool
  destinationOwned : Bool
  provenancePreserved : Bool
  transportCredit : Bool
  composite : Bool
  strictJoin : Bool
  deriving Repr, DecidableEq, BEq

def contactTransportLaw (c : ContactTransportCase) : Bool :=
  (!c.transportCredit ||
    (c.contact && c.payloadCertified && c.destinationOwned &&
      c.provenancePreserved)) &&
  (!c.composite || c.contact) &&
  (!c.strictJoin || (c.transportCredit && c.composite))

def allContactTransportCases : List ContactTransportCase :=
  bools.flatMap fun compatible =>
  bools.flatMap fun contact =>
  bools.flatMap fun payloadCertified =>
  bools.flatMap fun destinationOwned =>
  bools.flatMap fun provenancePreserved =>
  bools.flatMap fun transportCredit =>
  bools.flatMap fun composite =>
  bools.map fun strictJoin =>
    { compatible, contact, payloadCertified, destinationOwned,
      provenancePreserved, transportCredit, composite, strictJoin }

theorem contact_transport_raw_cardinality :
    allContactTransportCases.length = 256 := by decide

theorem contact_transport_accepted_cardinality :
    (allContactTransportCases.filter contactTransportLaw).length = 54 := by decide

theorem contact_transport_exhaustive :
    (allContactTransportCases.filter contactTransportLaw).all
      contactTransportLaw = true := by decide

/-! ## P3-E02: declared-family join status -/

structure JoinStatusCase where
  contact : Bool
  commonRefinement : Bool
  composite : Bool
  objecthood : Bool
  retention : Bool
  novelty : Bool
  sourceGate : Bool
  budgetGate : Bool
  obstruction : Bool
  certifiedNoninteraction : Bool
  strictCredit : Bool
  deriving Repr, DecidableEq, BEq

def joinStatusLaw (c : JoinStatusCase) : Bool :=
  (!c.strictCredit ||
    (c.contact && c.composite && c.objecthood && c.retention && c.novelty &&
      c.sourceGate && c.budgetGate && !c.obstruction &&
      !c.certifiedNoninteraction)) &&
  (!c.composite || c.contact) &&
  (!c.objecthood || c.composite) &&
  (!c.retention || c.composite) &&
  (!c.novelty || c.composite) &&
  (!c.certifiedNoninteraction || !c.contact) &&
  !(c.obstruction && c.certifiedNoninteraction)

def allJoinStatusCases : List JoinStatusCase :=
  bools.flatMap fun contact =>
  bools.flatMap fun commonRefinement =>
  bools.flatMap fun composite =>
  bools.flatMap fun objecthood =>
  bools.flatMap fun retention =>
  bools.flatMap fun novelty =>
  bools.flatMap fun sourceGate =>
  bools.flatMap fun budgetGate =>
  bools.flatMap fun obstruction =>
  bools.flatMap fun certifiedNoninteraction =>
  bools.map fun strictCredit =>
    { contact, commonRefinement, composite, objecthood, retention, novelty,
      sourceGate, budgetGate, obstruction, certifiedNoninteraction,
      strictCredit }

theorem join_status_canonical_cardinality : allJoinStatusCases.length = 2048 := by decide

theorem join_status_raw_labelled_cardinality :
    allJoinStatusCases.length * 2 = 4096 := by decide

theorem join_status_accepted_cardinality :
    (allJoinStatusCases.filter joinStatusLaw).length = 170 := by decide

inductive FiniteJoinStatus where
  | noEvidencedContact
  | evidencedContact
  | commonRefinement
  | lawfulComposite
  | strictJoin
  | obstructed
  | certifiedNoninteraction
  deriving Repr, DecidableEq, BEq, Inhabited

def classifyJoinStatus (c : JoinStatusCase) : FiniteJoinStatus :=
  if c.certifiedNoninteraction then .certifiedNoninteraction
  else if c.obstruction then .obstructed
  else if c.strictCredit then .strictJoin
  else if c.composite then .lawfulComposite
  else if c.commonRefinement then .commonRefinement
  else if c.contact then .evidencedContact
  else .noEvidencedContact

def acceptedJoinStatusCases : List JoinStatusCase :=
  allJoinStatusCases.filter joinStatusLaw

def statusCount (status : FiniteJoinStatus) : Nat :=
  (acceptedJoinStatusCases.filter fun c => classifyJoinStatus c == status).length

theorem no_contact_status_count : statusCount .noEvidencedContact = 4 := by decide

theorem contact_status_count : statusCount .evidencedContact = 4 := by decide

theorem common_refinement_status_count : statusCount .commonRefinement = 8 := by decide

theorem lawful_composite_status_count : statusCount .lawfulComposite = 64 := by decide

theorem strict_join_status_count : statusCount .strictJoin = 2 := by decide

theorem obstructed_status_count : statusCount .obstructed = 80 := by decide

theorem certified_noninteraction_status_count :
    statusCount .certifiedNoninteraction = 8 := by decide

theorem status_partition_complete :
    statusCount .noEvidencedContact + statusCount .evidencedContact +
      statusCount .commonRefinement + statusCount .lawfulComposite +
      statusCount .strictJoin + statusCount .obstructed +
      statusCount .certifiedNoninteraction = acceptedJoinStatusCases.length := by decide

/-! ## P3-E03: strictness omission attacks -/

structure StrictnessCase where
  contact : Bool
  composite : Bool
  objecthood : Bool
  leftRetention : Bool
  rightRetention : Bool
  nonfactorLeft : Bool
  nonfactorRight : Bool
  nonfactorProduct : Bool
  sourceIndependent : Bool
  budgetPaid : Bool
  relabelOnly : Bool
  schedulingOnly : Bool
  coarseningOnly : Bool
  commonRefinementOnly : Bool
  directionCertified : Bool
  strictCredit : Bool
  deriving Repr, DecidableEq

def strictnessLaw (c : StrictnessCase) : Bool :=
  !c.strictCredit ||
    (c.contact && c.composite && c.objecthood && c.leftRetention &&
      c.rightRetention && c.nonfactorLeft && c.nonfactorRight &&
      c.nonfactorProduct && c.sourceIndependent && c.budgetPaid &&
      !c.relabelOnly && !c.schedulingOnly && !c.coarseningOnly &&
      !c.commonRefinementOnly)

def allStrictnessCases : List StrictnessCase :=
  bools.flatMap fun contact =>
  bools.flatMap fun composite =>
  bools.flatMap fun objecthood =>
  bools.flatMap fun leftRetention =>
  bools.flatMap fun rightRetention =>
  bools.flatMap fun nonfactorLeft =>
  bools.flatMap fun nonfactorRight =>
  bools.flatMap fun nonfactorProduct =>
  bools.flatMap fun sourceIndependent =>
  bools.flatMap fun budgetPaid =>
  bools.flatMap fun relabelOnly =>
  bools.flatMap fun schedulingOnly =>
  bools.flatMap fun coarseningOnly =>
  bools.flatMap fun commonRefinementOnly =>
  bools.flatMap fun directionCertified =>
  bools.map fun strictCredit =>
    { contact, composite, objecthood, leftRetention, rightRetention,
      nonfactorLeft, nonfactorRight, nonfactorProduct, sourceIndependent,
      budgetPaid, relabelOnly, schedulingOnly, coarseningOnly,
      commonRefinementOnly, directionCertified, strictCredit }

theorem strictness_canonical_cardinality : allStrictnessCases.length = 65536 := by decide

theorem strictness_raw_labelled_cardinality :
    allStrictnessCases.length * 2 = 131072 := by decide

theorem strictness_accepted_cardinality :
    (allStrictnessCases.filter strictnessLaw).length = 32770 := by decide

private def directionlessStrictFiniteWitness : StrictnessCase :=
  { contact := true, composite := true, objecthood := true,
    leftRetention := true, rightRetention := true,
    nonfactorLeft := true, nonfactorRight := true,
    nonfactorProduct := true, sourceIndependent := true,
    budgetPaid := true, relabelOnly := false, schedulingOnly := false,
    coarseningOnly := false, commonRefinementOnly := false,
    directionCertified := false, strictCredit := true }

private theorem mem_bools (x : Bool) : x ∈ bools := by cases x <;> decide

/--
Membership is proved structurally through the sixteen `flatMap` layers rather
than by scanning the 65,536-element carrier, which is not kernel-feasible.
-/
private theorem mem_allStrictnessCases (c : StrictnessCase) :
    c ∈ allStrictnessCases := by
  obtain ⟨f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11, f12, f13, f14, f15, f16⟩ := c
  refine List.mem_flatMap.mpr ⟨f1, mem_bools _, ?_⟩
  refine List.mem_flatMap.mpr ⟨f2, mem_bools _, ?_⟩
  refine List.mem_flatMap.mpr ⟨f3, mem_bools _, ?_⟩
  refine List.mem_flatMap.mpr ⟨f4, mem_bools _, ?_⟩
  refine List.mem_flatMap.mpr ⟨f5, mem_bools _, ?_⟩
  refine List.mem_flatMap.mpr ⟨f6, mem_bools _, ?_⟩
  refine List.mem_flatMap.mpr ⟨f7, mem_bools _, ?_⟩
  refine List.mem_flatMap.mpr ⟨f8, mem_bools _, ?_⟩
  refine List.mem_flatMap.mpr ⟨f9, mem_bools _, ?_⟩
  refine List.mem_flatMap.mpr ⟨f10, mem_bools _, ?_⟩
  refine List.mem_flatMap.mpr ⟨f11, mem_bools _, ?_⟩
  refine List.mem_flatMap.mpr ⟨f12, mem_bools _, ?_⟩
  refine List.mem_flatMap.mpr ⟨f13, mem_bools _, ?_⟩
  refine List.mem_flatMap.mpr ⟨f14, mem_bools _, ?_⟩
  refine List.mem_flatMap.mpr ⟨f15, mem_bools _, ?_⟩
  exact List.mem_map.mpr ⟨f16, mem_bools _, rfl⟩

theorem directionless_strict_case_exists :
    ∃ c ∈ allStrictnessCases,
      strictnessLaw c = true ∧ c.strictCredit = true ∧
      c.directionCertified = false :=
  ⟨directionlessStrictFiniteWitness, mem_allStrictnessCases _, by decide⟩

/-! ## P3-E04: source lineage -/

structure SourceLineageCase where
  sameLineage : Bool
  resemblance : Bool
  contact : Bool
  sourceWitness : Bool
  behavioralNovelty : Bool
  causalIndependence : Bool
  independenceCredit : Bool
  deriving Repr, DecidableEq, BEq

def sourceLineageLaw (c : SourceLineageCase) : Bool :=
  !c.independenceCredit ||
    (!c.sameLineage && c.contact && c.sourceWitness)

def allSourceLineageCases : List SourceLineageCase :=
  bools.flatMap fun sameLineage =>
  bools.flatMap fun resemblance =>
  bools.flatMap fun contact =>
  bools.flatMap fun sourceWitness =>
  bools.flatMap fun behavioralNovelty =>
  bools.flatMap fun causalIndependence =>
  bools.map fun independenceCredit =>
    { sameLineage, resemblance, contact, sourceWitness, behavioralNovelty,
      causalIndependence, independenceCredit }

theorem source_lineage_raw_cardinality : allSourceLineageCases.length = 128 := by decide

theorem source_lineage_accepted_cardinality :
    (allSourceLineageCases.filter sourceLineageLaw).length = 72 := by decide

/-! ## P3-E05: payment and observer accounting -/

structure PaymentCase where
  amount : Nat
  paid : Nat
  refunded : Nat
  zeroCostCertified : Bool
  observerUsed : Bool
  observerPriced : Bool
  credit : Bool
  deriving Repr, DecidableEq, BEq

def paymentLaw (c : PaymentCase) : Bool :=
  decide (c.refunded ≤ c.paid) &&
  (!c.credit ||
    ((!c.observerUsed || c.observerPriced) &&
      ((decide (c.amount = 0) && c.zeroCostCertified) ||
        (decide (0 < c.amount) && decide (c.amount ≤ c.paid)))))

def allPaymentCases : List PaymentCase :=
  small.flatMap fun amount =>
  small.flatMap fun paid =>
  small.flatMap fun refunded =>
  bools.flatMap fun zeroCostCertified =>
  bools.flatMap fun observerUsed =>
  bools.flatMap fun observerPriced =>
  bools.map fun credit =>
    { amount, paid, refunded, zeroCostCertified, observerUsed,
      observerPriced, credit }

theorem payment_raw_cardinality : allPaymentCases.length = 432 := by decide

theorem payment_accepted_cardinality :
    (allPaymentCases.filter paymentLaw).length = 210 := by decide

/-! ## P3-E06: finite live-join capacity -/

structure CapacityCase where
  capacity : Nat
  liveJoinCount : Nat
  minimumPositiveCost : Nat
  feasible : Bool
  deriving Repr, DecidableEq, BEq

def capacityActual (c : CapacityCase) : Bool :=
  decide (0 < c.minimumPositiveCost) &&
  decide (c.liveJoinCount * c.minimumPositiveCost ≤ c.capacity)

def capacityLaw (c : CapacityCase) : Bool :=
  c.feasible == capacityActual c

def allCapacityCases : List CapacityCase :=
  capacityValues.flatMap fun capacity =>
  capacityValues.flatMap fun liveJoinCount =>
  minimumCosts.flatMap fun minimumPositiveCost =>
  bools.map fun feasible =>
    { capacity, liveJoinCount, minimumPositiveCost, feasible }

theorem capacity_raw_cardinality : allCapacityCases.length = 200 := by decide

theorem capacity_accepted_cardinality :
    (allCapacityCases.filter capacityLaw).length = 100 := by decide

/-! ## P3-E07: retention and refinement -/

inductive FiniteRetentionStatus where
  | erased
  | «partial»
  | full
  deriving Repr, DecidableEq, BEq, Inhabited

inductive FiniteRefinementEffect where
  | preserves
  | strengthens
  | weakens
  | destroys
  deriving Repr, DecidableEq, BEq, Inhabited

private def retentionStatuses : List FiniteRetentionStatus :=
  [.erased, .«partial», .full]

private def refinementEffects : List FiniteRefinementEffect :=
  [.preserves, .strengthens, .weakens, .destroys]

def retentionRank : FiniteRetentionStatus → Nat
  | .erased => 0
  | .«partial» => 1
  | .full => 2

structure RefinementCase where
  joinBefore : Bool
  joinAfter : Bool
  noveltyBefore : Bool
  noveltyAfter : Bool
  retentionBefore : FiniteRetentionStatus
  retentionAfter : FiniteRetentionStatus
  effect : FiniteRefinementEffect
  deriving Repr, DecidableEq, BEq

def refinementLaw (c : RefinementCase) : Bool :=
  match c.effect with
  | .preserves =>
      (c.joinBefore == c.joinAfter) &&
      (c.noveltyBefore == c.noveltyAfter) &&
      (c.retentionBefore == c.retentionAfter)
  | .strengthens =>
      ((!c.joinBefore && c.joinAfter) ||
        ((c.joinBefore == c.joinAfter) &&
          ((!c.noveltyBefore && c.noveltyAfter) ||
            decide (retentionRank c.retentionBefore <
              retentionRank c.retentionAfter))))
  | .weakens =>
      c.joinBefore && c.joinAfter &&
        ((c.noveltyBefore && !c.noveltyAfter) ||
          decide (retentionRank c.retentionAfter <
            retentionRank c.retentionBefore))
  | .destroys => c.joinBefore && !c.joinAfter

def allRefinementCases : List RefinementCase :=
  bools.flatMap fun joinBefore =>
  bools.flatMap fun joinAfter =>
  bools.flatMap fun noveltyBefore =>
  bools.flatMap fun noveltyAfter =>
  retentionStatuses.flatMap fun retentionBefore =>
  retentionStatuses.flatMap fun retentionAfter =>
  refinementEffects.map fun effect =>
    { joinBefore, joinAfter, noveltyBefore, noveltyAfter,
      retentionBefore, retentionAfter, effect }

theorem refinement_raw_cardinality : allRefinementCases.length = 576 := by decide

theorem refinement_accepted_cardinality :
    (allRefinementCases.filter refinementLaw).length = 138 := by decide

/-! ## P3-E08: residuals and join-created cross terms -/

inductive FiniteResidualOrigin where
  | inheritedLeft
  | inheritedRight
  | dissolvedByJoin
  | createdCrossTerm
  deriving Repr, DecidableEq, BEq, Inhabited

private def residualOrigins : List FiniteResidualOrigin :=
  [.inheritedLeft, .inheritedRight, .dissolvedByJoin, .createdCrossTerm]

structure ResidualCase where
  origin : FiniteResidualOrigin
  active : Bool
  crossTerm : Bool
  relabelOnly : Bool
  sourceAccounted : Bool
  parentCount : Nat
  deriving Repr, DecidableEq, BEq

def residualLaw (c : ResidualCase) : Bool :=
  match c.origin with
  | .createdCrossTerm =>
      c.active && c.crossTerm && !c.relabelOnly && c.sourceAccounted &&
        decide (2 ≤ c.parentCount)
  | .dissolvedByJoin =>
      !c.active && !c.crossTerm && !c.relabelOnly && c.sourceAccounted &&
        decide (1 ≤ c.parentCount)
  | .inheritedLeft =>
      !c.crossTerm && !c.relabelOnly && c.sourceAccounted &&
        decide (1 ≤ c.parentCount)
  | .inheritedRight =>
      !c.crossTerm && !c.relabelOnly && c.sourceAccounted &&
        decide (1 ≤ c.parentCount)

def allResidualCases : List ResidualCase :=
  residualOrigins.flatMap fun origin =>
  bools.flatMap fun active =>
  bools.flatMap fun crossTerm =>
  bools.flatMap fun relabelOnly =>
  bools.flatMap fun sourceAccounted =>
  small.map fun parentCount =>
    { origin, active, crossTerm, relabelOnly, sourceAccounted, parentCount }

theorem residual_raw_cardinality : allResidualCases.length = 192 := by decide

theorem residual_accepted_cardinality :
    (allResidualCases.filter residualLaw).length = 11 := by decide

/-! ## P3-E09: certified non-interaction -/

structure NoninteractionCase where
  contact : Bool
  familyClosed : Bool
  detectorPower : Bool
  budgetSufficient : Bool
  horizonComplete : Bool
  allExamined : Bool
  outsideChannel : Bool
  certificateCredit : Bool
  deriving Repr, DecidableEq, BEq

def noninteractionActual (c : NoninteractionCase) : Bool :=
  !c.contact && c.familyClosed && c.detectorPower && c.budgetSufficient &&
    c.horizonComplete && c.allExamined && !c.outsideChannel

def noninteractionLaw (c : NoninteractionCase) : Bool :=
  c.certificateCredit == noninteractionActual c

def allNoninteractionCases : List NoninteractionCase :=
  bools.flatMap fun contact =>
  bools.flatMap fun familyClosed =>
  bools.flatMap fun detectorPower =>
  bools.flatMap fun budgetSufficient =>
  bools.flatMap fun horizonComplete =>
  bools.flatMap fun allExamined =>
  bools.flatMap fun outsideChannel =>
  bools.map fun certificateCredit =>
    { contact, familyClosed, detectorPower, budgetSufficient,
      horizonComplete, allExamined, outsideChannel, certificateCredit }

theorem noninteraction_raw_cardinality : allNoninteractionCases.length = 256 := by decide

theorem noninteraction_accepted_cardinality :
    (allNoninteractionCases.filter noninteractionLaw).length = 128 := by decide

theorem exactly_one_certified_noninteraction_profile :
    ((allNoninteractionCases.filter noninteractionLaw).filter
      fun c => c.certificateCredit).length = 1 := by decide

/-! ## P3-E10: conditional categorical representations -/

structure CategoricalCase where
  strictJoin : Bool
  categoryDeclared : Bool
  morphismsDeclared : Bool
  universalChecked : Bool
  parentsPreserved : Bool
  antiProduct : Bool
  productUniversal : Bool
  pullbackUniversal : Bool
  pushoutUniversal : Bool
  categoricalCredit : Bool
  deriving Repr, DecidableEq

def anyUniversal (c : CategoricalCase) : Bool :=
  c.productUniversal || c.pullbackUniversal || c.pushoutUniversal

def categoricalLaw (c : CategoricalCase) : Bool :=
  (!anyUniversal c ||
    (c.categoryDeclared && c.morphismsDeclared && c.universalChecked &&
      c.parentsPreserved)) &&
  (!c.categoricalCredit ||
    (c.strictJoin && anyUniversal c && c.categoryDeclared &&
      c.morphismsDeclared && c.universalChecked && c.parentsPreserved &&
      c.antiProduct))

def allCategoricalCases : List CategoricalCase :=
  bools.flatMap fun strictJoin =>
  bools.flatMap fun categoryDeclared =>
  bools.flatMap fun morphismsDeclared =>
  bools.flatMap fun universalChecked =>
  bools.flatMap fun parentsPreserved =>
  bools.flatMap fun antiProduct =>
  bools.flatMap fun productUniversal =>
  bools.flatMap fun pullbackUniversal =>
  bools.flatMap fun pushoutUniversal =>
  bools.map fun categoricalCredit =>
    { strictJoin, categoryDeclared, morphismsDeclared, universalChecked,
      parentsPreserved, antiProduct, productUniversal, pullbackUniversal,
      pushoutUniversal, categoricalCredit }

theorem categorical_raw_cardinality : allCategoricalCases.length = 1024 := by decide

theorem categorical_accepted_cardinality :
    (allCategoricalCases.filter categoricalLaw).length = 99 := by decide

private def noncategoricalStrictFiniteWitness : CategoricalCase :=
  { strictJoin := true, categoryDeclared := false,
    morphismsDeclared := false, universalChecked := false,
    parentsPreserved := false, antiProduct := true,
    productUniversal := false, pullbackUniversal := false,
    pushoutUniversal := false, categoricalCredit := false }

theorem strict_join_without_listed_universal_construction_exists :
    ∃ c ∈ allCategoricalCases,
      categoricalLaw c = true ∧ c.strictJoin = true ∧
      c.productUniversal = false ∧ c.pullbackUniversal = false ∧
      c.pushoutUniversal = false := by
  refine ⟨noncategoricalStrictFiniteWitness, ?_, ?_⟩
  · decide
  · decide

/-! ## P3-E11: candidate contact quantities -/

inductive FiniteMeasureKind where
  | contacts
  | liveJoins
  | paidCost
  | activeResiduals
  | retainedParents
  deriving Repr, DecidableEq, BEq, Inhabited

private def measureKinds : List FiniteMeasureKind :=
  [.contacts, .liveJoins, .paidCost, .activeResiduals, .retainedParents]

structure MeasureCase where
  measureKind : FiniteMeasureKind
  before : Nat
  after : Nat
  observerIncluded : Bool
  instrumentIncluded : Bool
  residualIncluded : Bool
  exactChecked : Bool
  lawful : Bool
  conservationCredit : Bool
  deriving Repr, DecidableEq, BEq

def measureComplete (c : MeasureCase) : Bool :=
  c.observerIncluded && c.instrumentIncluded && c.residualIncluded &&
    c.exactChecked

def measureLaw (c : MeasureCase) : Bool :=
  (!c.lawful || measureComplete c) &&
  (!c.conservationCredit ||
    (c.lawful && measureComplete c && decide (c.before = c.after)))

def allMeasureCases : List MeasureCase :=
  measureKinds.flatMap fun measureKind =>
  small.flatMap fun before =>
  small.flatMap fun after =>
  bools.flatMap fun observerIncluded =>
  bools.flatMap fun instrumentIncluded =>
  bools.flatMap fun residualIncluded =>
  bools.flatMap fun exactChecked =>
  bools.flatMap fun lawful =>
  bools.map fun conservationCredit =>
    { measureKind, before, after, observerIncluded, instrumentIncluded,
      residualIncluded, exactChecked, lawful, conservationCredit }

theorem measure_raw_cardinality : allMeasureCases.length = 2880 := by decide

theorem measure_accepted_cardinality :
    (allMeasureCases.filter measureLaw).length = 780 := by decide

def hasLawfulNonconservation (kind : FiniteMeasureKind) : Bool :=
  (allMeasureCases.filter measureLaw).any fun c =>
    c.measureKind == kind && c.lawful && decide (c.before ≠ c.after) &&
      !c.conservationCredit

theorem contacts_nonconservation_control :
    hasLawfulNonconservation .contacts = true := by decide

theorem live_joins_nonconservation_control :
    hasLawfulNonconservation .liveJoins = true := by decide

theorem paid_cost_nonconservation_control :
    hasLawfulNonconservation .paidCost = true := by decide

theorem active_residuals_nonconservation_control :
    hasLawfulNonconservation .activeResiduals = true := by decide

theorem retained_parents_nonconservation_control :
    hasLawfulNonconservation .retainedParents = true := by decide

end FoundationsVII.Models.Finite.Phase3
