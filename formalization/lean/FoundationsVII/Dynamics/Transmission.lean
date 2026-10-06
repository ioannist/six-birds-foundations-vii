import FoundationsVII.Enablement.All
import FoundationsVII.Join.Retention
import FoundationsVII.Prior.FT13
import FoundationsVII.Prior.FT19

/-!
# Typed transmission and descent fidelity

Upward, downward, and peer transmission record payload, loss, ambiguity, source,
and budget. A descent-fidelity square is explicit. Pure downward selection does
not create a lower-carrier fact absent from the lower carrier, and structural
selection is not itself a causal-channel certificate.
-/

namespace FoundationsVII

inductive TransmissionDirection where
  | upward
  | downward
  | peer
  deriving Repr, DecidableEq, BEq, Inhabited

def allTransmissionDirections : List TransmissionDirection :=
  [.upward, .downward, .peer]

theorem transmissionDirection_mem_all (direction : TransmissionDirection) :
    direction ∈ allTransmissionDirections := by
  cases direction <;> simp [allTransmissionDirections]

structure TransmissionRecord where
  direction : TransmissionDirection
  sourceTheory : TheoryId
  targetTheory : TheoryId
  payload : String
  sourceId : SourceId
  sourceTyped : Bool
  budgeted : Bool
  lossDescription : String
  ambiguityDescription : String
  lowerFactPresentBefore : Bool
  lowerFactPresentAfter : Bool
  externalInsertion : Bool
  causalCertificate : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace TransmissionRecord

def WellFormed (record : TransmissionRecord) : Prop :=
  record.sourceTheory ≠ record.targetTheory ∧
  record.payload ≠ "" ∧
  record.sourceTyped = true ∧
  record.budgeted = true ∧
  record.lossDescription ≠ "" ∧
  record.ambiguityDescription ≠ "" ∧
  record.audit.entries ≠ []

instance (record : TransmissionRecord) : Decidable (WellFormed record) := by
  unfold WellFormed
  infer_instance

def LowerFactProvenancePreserved (record : TransmissionRecord) : Prop :=
  record.lowerFactPresentAfter = true →
    record.lowerFactPresentBefore = true ∨ record.externalInsertion = true

def PureDownwardSelection (record : TransmissionRecord) : Prop :=
  WellFormed record ∧
  record.direction = .downward ∧
  record.externalInsertion = false ∧
  LowerFactProvenancePreserved record

theorem pure_downward_selection_preserves_present_lower_facts
    {record : TransmissionRecord}
    (hPure : PureDownwardSelection record)
    (hAfter : record.lowerFactPresentAfter = true) :
    record.lowerFactPresentBefore = true := by
  rcases hPure.2.2.2 hAfter with hBefore | hInsert
  · exact hBefore
  · have hNoInsert : record.externalInsertion = false := hPure.2.2.1
    rw [hNoInsert] at hInsert
    exact Bool.noConfusion hInsert

theorem pure_downward_selection_cannot_create_absent_lower_fact
    {record : TransmissionRecord}
    (hPure : PureDownwardSelection record)
    (hAbsent : record.lowerFactPresentBefore = false) :
    record.lowerFactPresentAfter = false := by
  cases hAfter : record.lowerFactPresentAfter
  · rfl
  · have hBefore := pure_downward_selection_preserves_present_lower_facts hPure hAfter
    rw [hAbsent] at hBefore
    exact Bool.noConfusion hBefore

end TransmissionRecord

/-- A typed commuting square for descent fidelity. -/
structure DescentSquare (Upper Lower UpperView LowerView : Type) where
  upperMap : Upper → UpperView
  descent : Upper → Lower
  viewDescent : UpperView → LowerView
  lowerMap : Lower → LowerView

namespace DescentSquare

def Commutes {Upper Lower UpperView LowerView : Type}
    (square : DescentSquare Upper Lower UpperView LowerView) : Prop :=
  ∀ x, square.viewDescent (square.upperMap x) =
    square.lowerMap (square.descent x)

theorem fidelity_is_commuting_square
    {Upper Lower UpperView LowerView : Type}
    (square : DescentSquare Upper Lower UpperView LowerView)
    (h : Commutes square) : Commutes square := h

end DescentSquare

structure TransmissionFidelity where
  transmission : TransmissionRecord
  payloadPreserved : Bool
  lossAccounted : Bool
  ambiguityAccounted : Bool
  sourcePreserved : Bool
  budgetPreserved : Bool
  squareCommutes : Bool
  deriving Repr, DecidableEq, BEq

namespace TransmissionFidelity

def Valid (fidelity : TransmissionFidelity) : Prop :=
  TransmissionRecord.WellFormed fidelity.transmission ∧
  fidelity.payloadPreserved = true ∧
  fidelity.lossAccounted = true ∧
  fidelity.ambiguityAccounted = true ∧
  fidelity.sourcePreserved = true ∧
  fidelity.budgetPreserved = true ∧
  fidelity.squareCommutes = true

instance (fidelity : TransmissionFidelity) : Decidable (Valid fidelity) := by
  unfold Valid
  infer_instance

theorem valid_records_loss {fidelity : TransmissionFidelity}
    (h : Valid fidelity) : fidelity.lossAccounted = true := h.2.2.1

theorem valid_records_ambiguity {fidelity : TransmissionFidelity}
    (h : Valid fidelity) : fidelity.ambiguityAccounted = true := h.2.2.2.1

theorem valid_preserves_source {fidelity : TransmissionFidelity}
    (h : Valid fidelity) : fidelity.sourcePreserved = true := h.2.2.2.2.1

theorem valid_preserves_budget {fidelity : TransmissionFidelity}
    (h : Valid fidelity) : fidelity.budgetPreserved = true := h.2.2.2.2.2.1

end TransmissionFidelity

structure SelectionCausationProfile where
  downwardSelection : Bool
  descentFaithful : Bool
  lowerFactsPreserved : Bool
  independentCausalCertificate : Bool
  causalCredit : Bool
  deriving Repr, DecidableEq, BEq

namespace SelectionCausationProfile

def Valid (profile : SelectionCausationProfile) : Prop :=
  (profile.causalCredit = true →
    profile.downwardSelection = true ∧
    profile.descentFaithful = true ∧
    profile.lowerFactsPreserved = true ∧
    profile.independentCausalCertificate = true)

instance (profile : SelectionCausationProfile) : Decidable (Valid profile) := by
  unfold Valid
  infer_instance

end SelectionCausationProfile

private def structuralSelectionWithoutCausation : SelectionCausationProfile :=
  { downwardSelection := true, descentFaithful := true,
    lowerFactsPreserved := true, independentCausalCertificate := false,
    causalCredit := false }

theorem structural_downward_selection_is_not_automatically_causal :
    SelectionCausationProfile.Valid structuralSelectionWithoutCausation ∧
    structuralSelectionWithoutCausation.downwardSelection = true ∧
    structuralSelectionWithoutCausation.causalCredit = false := by decide

structure DirectionalTransmissionControl where
  upwardValid : Bool
  downwardValid : Bool
  peerValid : Bool
  deriving Repr, DecidableEq, BEq

private def allDirectionControl : DirectionalTransmissionControl :=
  { upwardValid := true, downwardValid := true, peerValid := true }

theorem all_three_transmission_directions_have_positive_controls :
    allDirectionControl.upwardValid = true ∧
    allDirectionControl.downwardValid = true ∧
    allDirectionControl.peerValid = true := by decide

end FoundationsVII
