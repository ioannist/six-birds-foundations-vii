import FoundationsVII.Join.Categorical

/-!
# Candidate contact quantities and conservation decision

A quantity is called conserved only relative to a declared transformation and
an exact equality certificate.  The record does not select a universal scalar.
-/

namespace FoundationsVII

structure ContactQuantityVector where
  access : Nat
  retention : Nat
  novelty : Nat
  observer : Nat
  residual : Nat
  deriving Repr, DecidableEq, BEq

namespace ContactQuantityVector

def scalarPlain (quantity : ContactQuantityVector) : Nat :=
  quantity.access + quantity.retention + quantity.novelty +
    quantity.observer + quantity.residual

def scalarNoveltyWeighted (quantity : ContactQuantityVector) : Nat :=
  quantity.access + quantity.retention + 2 * quantity.novelty +
    quantity.observer + 3 * quantity.residual

end ContactQuantityVector

structure ContactQuantityTransformation where
  before : ContactQuantityVector
  after : ContactQuantityVector
  declaredScalarName : String
  beforeScalar : Nat
  afterScalar : Nat
  observerIncluded : Bool
  instrumentIncluded : Bool
  residualIncluded : Bool
  exactEqualityChecked : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace ContactQuantityTransformation

def Conserved (record : ContactQuantityTransformation) : Prop :=
  record.declaredScalarName ≠ "" ∧
  record.observerIncluded = true ∧
  record.instrumentIncluded = true ∧
  record.residualIncluded = true ∧
  record.beforeScalar = record.afterScalar ∧
  record.exactEqualityChecked = true ∧
  record.audit.entries ≠ []

instance (record : ContactQuantityTransformation) : Decidable (Conserved record) := by
  unfold Conserved
  infer_instance

theorem exact_certificate_licenses_scoped_conservation
    {record : ContactQuantityTransformation} (h : Conserved record) :
    record.beforeScalar = record.afterScalar := h.2.2.2.2.1

end ContactQuantityTransformation

private def degreeVector : ContactQuantityVector :=
  { access := 1
    retention := 1
    novelty := 1
    observer := 0
    residual := 1 }

private def hiddenObserverBefore : ContactQuantityVector :=
  { access := 1
    retention := 1
    novelty := 0
    observer := 0
    residual := 0 }

private def hiddenObserverAfter : ContactQuantityVector :=
  { access := 1
    retention := 1
    novelty := 0
    observer := 1
    residual := 0 }

private def apparentConservationWithOmittedObserver :
    ContactQuantityTransformation :=
  { before := hiddenObserverBefore
    after := hiddenObserverAfter
    declaredScalarName := "access+retention only"
    beforeScalar := 2
    afterScalar := 2
    observerIncluded := false
    instrumentIncluded := true
    residualIncluded := true
    exactEqualityChecked := true
    audit := phase3Audit }

private def exactScopedConservation : ContactQuantityTransformation :=
  { before := degreeVector
    after := degreeVector
    declaredScalarName := "plain declared finite quantity"
    beforeScalar := ContactQuantityVector.scalarPlain degreeVector
    afterScalar := ContactQuantityVector.scalarPlain degreeVector
    observerIncluded := true
    instrumentIncluded := true
    residualIncluded := true
    exactEqualityChecked := true
    audit := phase3Audit }

theorem plausible_contact_quantities_disagree :
    ContactQuantityVector.scalarPlain degreeVector = 4 ∧
    ContactQuantityVector.scalarNoveltyWeighted degreeVector = 7 ∧
    ContactQuantityVector.scalarPlain degreeVector ≠
      ContactQuantityVector.scalarNoveltyWeighted degreeVector := by
  decide

theorem omitted_observer_occupancy_invalidates_conservation_credit :
    apparentConservationWithOmittedObserver.beforeScalar =
      apparentConservationWithOmittedObserver.afterScalar ∧
    ¬ ContactQuantityTransformation.Conserved apparentConservationWithOmittedObserver := by
  decide

theorem exact_scoped_contact_conservation_is_available :
    ContactQuantityTransformation.Conserved exactScopedConservation := by
  decide

/-- DP06 terminal ruling: no universal contact degree is named.  Exact scoped
invariants remain admissible when every declared coordinate is included and the
equality is proved. -/
theorem no_unqualified_contact_degree_from_bookkeeping_alone :
    ContactQuantityVector.scalarPlain degreeVector ≠
      ContactQuantityVector.scalarNoveltyWeighted degreeVector := by
  decide

end FoundationsVII
