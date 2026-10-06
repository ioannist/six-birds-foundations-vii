import SixBirdsIII.Basic

namespace SixBirdsIII

inductive RoleStatus where
  | activeProjection
  | belowThreshold
  | collapsedBoundaryCase
  | absentWithRecord
  | inapplicableOutsideScope
  deriving DecidableEq, Repr

inductive CellStatus where
  | action
  | implicit
  | trivial
  | blocked
  | undefinedCircular
  | belowThreshold
  | collapsed
  | absent
  | outsideScope
  deriving DecidableEq, Repr

inductive PairStatus where
  | real
  | realProvisional
  | realDuplicated
  | blocked
  deriving DecidableEq, Repr

inductive PromotionStatus where
  | candidate
  | accepted
  | strict
  | nonStrict
  | failedDescent
  | failedStability
  | failedAudit
  | failedNoSmuggling
  | localOnly
  | globallyObstructed
  | outsideScope
  deriving DecidableEq, Repr

inductive ClaimStatus where
  | accepted
  | rejected
  | provisional
  | blocked
  | outsideScope
  | absentWithRecord
  | belowThreshold
  | failedAudit
  | undefinedCircular
  deriving DecidableEq, Repr

inductive GateStatus where
  | pass
  | fail
  | notRequired
  | notChecked
  | outsideScope
  deriving DecidableEq, Repr

inductive StrictGateStatus where
  | strictPass
  | nonStrictPass
  | notRequired
  | notChecked
  | badAudit
  | outsideScope
  deriving DecidableEq, Repr

inductive SqStatus where
  | exact
  | lax
  | obstructed
  | blocked
  | outsideScope
  | failedAudit
  | undefinedCircular
  | provisional
  deriving DecidableEq, Repr

end SixBirdsIII
