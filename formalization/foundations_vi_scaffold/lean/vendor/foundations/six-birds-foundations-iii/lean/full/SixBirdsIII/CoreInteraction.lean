import SixBirdsIII.Records

namespace SixBirdsIII

structure RoleChannelRecord where
  role : Primitive
  status : RoleStatus
  deriving Repr

def HasActorInformantSlots (_cell : DirectedCellRecord) : Prop :=
  True

def CellHasSomeStatusCondition (cell : DirectedCellRecord) : Prop :=
  cell.outsideScope = true ∨
  cell.witnessPresent = false ∨
  cell.blocked = true ∨
  cell.circular = true ∨
  cell.collapsed = true ∨
  cell.belowThreshold = true ∨
  cell.trivialCell = true ∨
  cell.implicitCell = true ∨
  (cell.outsideScope = false ∧
    cell.witnessPresent = true ∧
    cell.blocked = false ∧
    cell.circular = false ∧
    cell.collapsed = false ∧
    cell.belowThreshold = false ∧
    cell.trivialCell = false ∧
    cell.implicitCell = false)

def CoveredDirectedCell (cell : DirectedCellRecord) : Prop :=
  WellFormedDirectedCell cell ∧ CellHasSomeStatusCondition cell

def CellClassify (cell : DirectedCellRecord) : CellStatus :=
  if cell.outsideScope then CellStatus.outsideScope
  else if cell.witnessPresent == false then CellStatus.absent
  else if cell.blocked then CellStatus.blocked
  else if cell.circular then CellStatus.undefinedCircular
  else if cell.collapsed then CellStatus.collapsed
  else if cell.belowThreshold then CellStatus.belowThreshold
  else if cell.trivialCell then CellStatus.trivial
  else if cell.implicitCell then CellStatus.implicit
  else CellStatus.action

def missingWitnessCell : DirectedCellRecord :=
  { auditedDirectedCell with
    witnessPresent := false
    status := CellStatus.absent }

def outsideAndActionCell : DirectedCellRecord :=
  { auditedDirectedCell with
    outsideScope := true
    status := CellStatus.outsideScope }

def blockedCell : DirectedCellRecord :=
  { auditedDirectedCell with
    blocked := true
    status := CellStatus.blocked }

def actionReadyCell : DirectedCellRecord :=
  auditedDirectedCell

def roleActiveCellAbsentWitness : DirectedCellRecord :=
  missingWitnessCell

def activeRoleChannel : RoleChannelRecord :=
  { role := Primitive.P1, status := RoleStatus.activeProjection }

def blockedPairObservable : PairObservableRecord :=
  { left := Primitive.P1
    right := Primitive.P2
    status := PairStatus.blocked
    source := SourceTag.missing
    profile := baseProfile
    auditPresent := true }

def strictPromotionBridge : PromotionBridgeRecord :=
  { sourceHost := Host.fin
    targetHost := Host.fin
    status := PromotionStatus.strict
    gate := GateStatus.pass
    strictGate := StrictGateStatus.strictPass
    auditPresent := true }

theorem typed_non_collapse :
    ∃ cell : DirectedCellRecord,
      WellFormedDirectedCell cell ∧
      cell.status = CellStatus.action ∧
      cell.actor ≠ cell.informant := by
  refine ⟨auditedDirectedCell, ?_, rfl, ?_⟩
  · exact ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
  · intro h
    cases h

theorem cell_well_formedness_decidable :
    ∀ cell : DirectedCellRecord,
      WellFormedDirectedCell cell ∨ ¬ WellFormedDirectedCell cell := by
  intro cell
  by_cases h : WellFormedDirectedCell cell
  · exact Or.inl h
  · exact Or.inr h

theorem covered_cell_unique_status :
    ∀ cell : DirectedCellRecord,
      CoveredDirectedCell cell ->
      ∃ status : CellStatus,
        CellClassify cell = status ∧
        ∀ status' : CellStatus, CellClassify cell = status' -> status' = status := by
  intro cell _hcovered
  refine ⟨CellClassify cell, rfl, ?_⟩
  intro status' hstatus
  exact hstatus.symm

theorem active_role_channel_not_cell_action :
    ∃ roleCell : RoleChannelRecord, ∃ cell : DirectedCellRecord,
      roleCell.status = RoleStatus.activeProjection ∧
      CellClassify cell ≠ CellStatus.action := by
  refine ⟨activeRoleChannel, roleActiveCellAbsentWitness, rfl, ?_⟩
  decide

theorem cell_action_not_pair_real :
    ∃ cell : DirectedCellRecord, ∃ pair : PairObservableRecord,
      CellClassify cell = CellStatus.action ∧
      pair.status = PairStatus.blocked := by
  refine ⟨actionReadyCell, blockedPairObservable, ?_, rfl⟩
  simp [actionReadyCell, CellClassify, auditedDirectedCell]

theorem strict_promotion_not_cell_action :
    ∃ bridge : PromotionBridgeRecord, ∃ cell : DirectedCellRecord,
      bridge.status = PromotionStatus.strict ∧
      CellClassify cell ≠ CellStatus.action := by
  refine ⟨strictPromotionBridge, blockedCell, rfl, ?_⟩
  decide

theorem status_family_separation :
    (∃ roleCell : RoleChannelRecord, ∃ cell : DirectedCellRecord,
      roleCell.status = RoleStatus.activeProjection ∧
      CellClassify cell ≠ CellStatus.action) ∧
    (∃ cell : DirectedCellRecord, ∃ pair : PairObservableRecord,
      CellClassify cell = CellStatus.action ∧
      pair.status = PairStatus.blocked) ∧
    (∃ bridge : PromotionBridgeRecord, ∃ cell : DirectedCellRecord,
      bridge.status = PromotionStatus.strict ∧
      CellClassify cell ≠ CellStatus.action) := by
  exact ⟨active_role_channel_not_cell_action,
    cell_action_not_pair_real,
    strict_promotion_not_cell_action⟩

end SixBirdsIII
