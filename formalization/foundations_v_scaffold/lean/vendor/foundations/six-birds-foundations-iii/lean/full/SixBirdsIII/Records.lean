import SixBirdsIII.Domain

namespace SixBirdsIII

inductive DefectPolarity where
  | obstruction
  | certificate
  | gap
  | residual
  | capacityLoss
  deriving DecidableEq, Repr

structure DefectRecord where
  host : Host
  threshold : ThresholdTag
  polarity : DefectPolarity
  audit : AuditTag
  visible : VisibilityTag
  deriving Repr

structure DirectedCellRecord where
  actor : Primitive
  informant : Primitive
  status : CellStatus
  profile : Profile
  finiteFields : Bool
  auditPresent : Bool
  witnessPresent : Bool
  updatePresent : Bool
  profileAdmissible : Bool
  hostAdmitsCell : Bool
  inInstrumentScope : Bool
  outsideScope : Bool
  blocked : Bool
  circular : Bool
  collapsed : Bool
  belowThreshold : Bool
  trivialCell : Bool
  implicitCell : Bool
  deriving Repr

def WellFormedDirectedCell (cell : DirectedCellRecord) : Prop :=
  cell.finiteFields = true ∧
  cell.auditPresent = true ∧
  cell.witnessPresent = true ∧
  cell.updatePresent = true ∧
  cell.profileAdmissible = true ∧
  cell.hostAdmitsCell = true ∧
  cell.inInstrumentScope = true

structure PairObservableRecord where
  left : Primitive
  right : Primitive
  status : PairStatus
  source : SourceTag
  profile : Profile
  auditPresent : Bool
  deriving Repr

structure PromotionBridgeRecord where
  sourceHost : Host
  targetHost : Host
  status : PromotionStatus
  gate : GateStatus
  strictGate : StrictGateStatus
  auditPresent : Bool
  deriving Repr

structure ClaimRecord where
  host : Host
  status : ClaimStatus
  visible : VisibilityTag
  audit : AuditTag
  nonclaimRecorded : Bool
  deriving Repr

structure BirdIntDomain where
  primitiveCount : Nat
  levelCount : Nat
  hostCount : Nat
  statusFamilies : Nat
  auditCarried : Bool
  nonclaimsCarried : Bool
  deriving Repr

def standardBirdIntDomain : BirdIntDomain :=
  { primitiveCount := primitiveLabels.length
    levelCount := levels.length
    hostCount := hosts.length
    statusFamilies := 7
    auditCarried := true
    nonclaimsCarried := true }

def malformedDirectedCell : DirectedCellRecord :=
  { actor := Primitive.P1
    informant := Primitive.P2
    status := CellStatus.action
    profile := baseProfile
    finiteFields := false
    auditPresent := true
    witnessPresent := true
    updatePresent := true
    profileAdmissible := true
    hostAdmitsCell := true
    inInstrumentScope := true
    outsideScope := false
    blocked := false
    circular := false
    collapsed := false
    belowThreshold := false
    trivialCell := false
    implicitCell := false }

def auditedDirectedCell : DirectedCellRecord :=
  { actor := Primitive.P1
    informant := Primitive.P2
    status := CellStatus.action
    profile := baseProfile
    finiteFields := true
    auditPresent := true
    witnessPresent := true
    updatePresent := true
    profileAdmissible := true
    hostAdmitsCell := true
    inInstrumentScope := true
    outsideScope := false
    blocked := false
    circular := false
    collapsed := false
    belowThreshold := false
    trivialCell := false
    implicitCell := false }

end SixBirdsIII
