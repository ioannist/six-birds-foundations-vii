import FoundationsVII.Models.Finite.Countermodels

/-!
# Finite fixture serialization kernels

The Python side owns canonical JSON bytes.  Lean proves round trips for the
finite semantic payloads that are serialized into those fixtures.
-/

namespace FoundationsVII.Models.Finite

def statusCode : ScenarioStatus → Nat
  | .bootstrapBlocked => 0
  | .lawfulFirstExtension => 1
  | .prospectiveAdmission => 2
  | .retrospectiveSelfCertificationRejected => 3
  | .independenceGateFailed => 4
  | .contactWithoutJoin => 5
  | .commonRefinementNonstrict => 6
  | .strictJoin => 7
  | .retentionObstruction => 8
  | .budgetObstruction => 9
  | .sourceObstruction => 10
  | .noEvidencedContact => 11
  | .certifiedNoninteraction => 12
  | .fakeJoinScheduling => 13
  | .fakeJoinRelabeling => 14
  | .orderResidue => 15
  | .holonomyZeroArrow => 16
  | .drivenArrow => 17
  | .soundUnreachable => 18
  | .reachableNonoccurrent => 19
  | .occurrentEvent => 20
  | .unpricedObserver => 21
  | .unlicensedTotalityTransfer => 22
  | .refinementDestroysJoin => 23
  | .unclassified => 24

def decodeStatus : Nat → Option ScenarioStatus
  | 0 => some .bootstrapBlocked
  | 1 => some .lawfulFirstExtension
  | 2 => some .prospectiveAdmission
  | 3 => some .retrospectiveSelfCertificationRejected
  | 4 => some .independenceGateFailed
  | 5 => some .contactWithoutJoin
  | 6 => some .commonRefinementNonstrict
  | 7 => some .strictJoin
  | 8 => some .retentionObstruction
  | 9 => some .budgetObstruction
  | 10 => some .sourceObstruction
  | 11 => some .noEvidencedContact
  | 12 => some .certifiedNoninteraction
  | 13 => some .fakeJoinScheduling
  | 14 => some .fakeJoinRelabeling
  | 15 => some .orderResidue
  | 16 => some .holonomyZeroArrow
  | 17 => some .drivenArrow
  | 18 => some .soundUnreachable
  | 19 => some .reachableNonoccurrent
  | 20 => some .occurrentEvent
  | 21 => some .unpricedObserver
  | 22 => some .unlicensedTotalityTransfer
  | 23 => some .refinementDestroysJoin
  | 24 => some .unclassified
  | _ => none

theorem decodeStatus_statusCode (status : ScenarioStatus) :
    decodeStatus (statusCode status) = some status := by
  cases status <;> rfl

def statusName : ScenarioStatus → String
  | .bootstrapBlocked => "BOOTSTRAP_BLOCKED"
  | .lawfulFirstExtension => "LAWFUL_FIRST_EXTENSION"
  | .prospectiveAdmission => "PROSPECTIVE_ADMISSION"
  | .retrospectiveSelfCertificationRejected => "RETROSPECTIVE_SELF_CERTIFICATION_REJECTED"
  | .independenceGateFailed => "INDEPENDENCE_GATE_FAILED"
  | .contactWithoutJoin => "CONTACT_WITHOUT_JOIN"
  | .commonRefinementNonstrict => "COMMON_REFINEMENT_NONSTRICT"
  | .strictJoin => "STRICT_JOIN"
  | .retentionObstruction => "RETENTION_OBSTRUCTION"
  | .budgetObstruction => "BUDGET_OBSTRUCTION"
  | .sourceObstruction => "SOURCE_OBSTRUCTION"
  | .noEvidencedContact => "NO_EVIDENCED_CONTACT"
  | .certifiedNoninteraction => "CERTIFIED_NONINTERACTION"
  | .fakeJoinScheduling => "FAKE_JOIN_SCHEDULING"
  | .fakeJoinRelabeling => "FAKE_JOIN_RELABELING"
  | .orderResidue => "ORDER_RESIDUE"
  | .holonomyZeroArrow => "HOLONOMY_ZERO_ARROW"
  | .drivenArrow => "DRIVEN_ARROW"
  | .soundUnreachable => "SOUND_UNREACHABLE"
  | .reachableNonoccurrent => "REACHABLE_NONOCCURRENT"
  | .occurrentEvent => "OCCURRENT_EVENT"
  | .unpricedObserver => "UNPRICED_OBSERVER"
  | .unlicensedTotalityTransfer => "UNLICENSED_TOTALITY_TRANSFER"
  | .refinementDestroysJoin => "REFINEMENT_DESTROYS_JOIN"
  | .unclassified => "UNCLASSIFIED"

def encodeFlags (f : ScenarioFlags) : List Bool :=
  [ f.antiProduct, f.budgetOk, f.closedFamily, f.commonRefinement
  , f.compatible, f.composite, f.contact, f.detectorPower, f.drive, f.fired
  , f.generatorReachable, f.holonomy, f.joinDestroyed, f.neutralSeed
  , f.newResidual, f.observerPriced, f.observerUsed, f.orderResidue
  , f.parentRefined, f.partialDomain, f.prospective, f.reachable, f.relabelOnly
  , f.resemblanceOnly, f.retention, f.retrospective, f.sameSource
  , f.schedulingOnly, f.seed, f.sound, f.sourceIndependent, f.totalLensOnly ]

def decodeFlags : List Bool → Option ScenarioFlags
  | [ antiProduct, budgetOk, closedFamily, commonRefinement
    , compatible, composite, contact, detectorPower, drive, fired
    , generatorReachable, holonomy, joinDestroyed, neutralSeed
    , newResidual, observerPriced, observerUsed, orderResidue
    , parentRefined, partialDomain, prospective, reachable, relabelOnly
    , resemblanceOnly, retention, retrospective, sameSource
    , schedulingOnly, seed, sound, sourceIndependent, totalLensOnly ] =>
      some
        { antiProduct := antiProduct
          budgetOk := budgetOk
          closedFamily := closedFamily
          commonRefinement := commonRefinement
          compatible := compatible
          composite := composite
          contact := contact
          detectorPower := detectorPower
          drive := drive
          fired := fired
          generatorReachable := generatorReachable
          holonomy := holonomy
          joinDestroyed := joinDestroyed
          neutralSeed := neutralSeed
          newResidual := newResidual
          observerPriced := observerPriced
          observerUsed := observerUsed
          orderResidue := orderResidue
          parentRefined := parentRefined
          partialDomain := partialDomain
          prospective := prospective
          reachable := reachable
          relabelOnly := relabelOnly
          resemblanceOnly := resemblanceOnly
          retention := retention
          retrospective := retrospective
          sameSource := sameSource
          schedulingOnly := schedulingOnly
          seed := seed
          sound := sound
          sourceIndependent := sourceIndependent
          totalLensOnly := totalLensOnly }
  | _ => none

theorem decodeFlags_encodeFlags (flags : ScenarioFlags) :
    decodeFlags (encodeFlags flags) = some flags := by
  cases flags <;> rfl

end FoundationsVII.Models.Finite
