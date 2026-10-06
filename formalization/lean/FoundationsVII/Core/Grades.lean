import FoundationsVII.Core.Identifiers

/-!
# Scientific grades, evidence envelopes, and normative specifications

The constructors make theorem-grade claims, finite assays, and normative
specifications definitionally distinct.  A later bridge may connect them only
through an explicit proof and audit record.
-/

namespace FoundationsVII

structure GradedClaim where
  claimId : ClaimId
  statement : String
  grade : ClaimGrade
  conditionRole : ConditionRole
  specificationKind : SpecificationKind
  sourceLocations : List String
  nonclaims : List String
  deriving Repr, DecidableEq, BEq

structure FiniteEvidenceEnvelope where
  grade : EvidenceGrade
  quantifier : QuantifierGrade
  carrierDescription : String
  rawCardinality : Nat
  canonicalCardinality : Nat
  horizon : Nat
  detectorDescription : String
  evidenceHash : String
  nonclaims : List String
  deriving Repr, DecidableEq, BEq

structure NormativeSpecification where
  specificationId : String
  obligation : String
  acceptanceGate : String
  nonclaims : List String
  deriving Repr, DecidableEq, BEq

namespace GradedClaim

def WellFormed (claim : GradedClaim) : Prop :=
  claim.statement ≠ "" ∧
  claim.sourceLocations ≠ [] ∧
  claim.nonclaims ≠ []

instance (claim : GradedClaim) : Decidable (WellFormed claim) := by
  unfold WellFormed
  infer_instance

end GradedClaim

namespace FiniteEvidenceEnvelope

def WellFormed (evidence : FiniteEvidenceEnvelope) : Prop :=
  evidence.carrierDescription ≠ "" ∧
  evidence.canonicalCardinality ≤ evidence.rawCardinality ∧
  evidence.detectorDescription ≠ "" ∧
  evidence.evidenceHash ≠ "" ∧
  evidence.nonclaims ≠ []

instance (evidence : FiniteEvidenceEnvelope) : Decidable (WellFormed evidence) := by
  unfold WellFormed
  infer_instance

theorem constructed_wellFormed (evidence : FiniteEvidenceEnvelope)
    (hCarrier : evidence.carrierDescription ≠ "")
    (hCardinality : evidence.canonicalCardinality ≤ evidence.rawCardinality)
    (hDetector : evidence.detectorDescription ≠ "")
    (hHash : evidence.evidenceHash ≠ "")
    (hNonclaims : evidence.nonclaims ≠ []) : WellFormed evidence := by
  exact ⟨hCarrier, hCardinality, hDetector, hHash, hNonclaims⟩

end FiniteEvidenceEnvelope

namespace NormativeSpecification

def WellFormed (specification : NormativeSpecification) : Prop :=
  specification.specificationId ≠ "" ∧
  specification.obligation ≠ "" ∧
  specification.acceptanceGate ≠ "" ∧
  specification.nonclaims ≠ []

instance (specification : NormativeSpecification) : Decidable (WellFormed specification) := by
  unfold WellFormed
  infer_instance

end NormativeSpecification

theorem theorem_ne_schema : ClaimGrade.theorem ≠ ClaimGrade.schema := by decide

theorem theorem_ne_calibration : ClaimGrade.theorem ≠ ClaimGrade.calibration := by decide

theorem theorem_ne_conjecture : ClaimGrade.theorem ≠ ClaimGrade.conjecture := by decide

theorem theorem_ne_philosophy : ClaimGrade.theorem ≠ ClaimGrade.philosophy := by decide

theorem theorem_ne_nonclaim : ClaimGrade.theorem ≠ ClaimGrade.nonclaim := by decide

theorem theoremBacked_ne_exhaustiveFiniteExternal :
    EvidenceGrade.theoremBacked ≠ EvidenceGrade.exhaustiveFiniteExternal := by decide

theorem theoremBacked_ne_exhaustiveFiniteLean :
    EvidenceGrade.theoremBacked ≠ EvidenceGrade.exhaustiveFiniteLean := by decide

theorem necessary_ne_sufficient :
    ConditionRole.necessary ≠ ConditionRole.sufficient := by decide

theorem normative_ne_illustrative :
    SpecificationKind.normative ≠ SpecificationKind.illustrativeExample := by decide

theorem finite_carrier_ne_universal :
    QuantifierGrade.finiteCarrier ≠ QuantifierGrade.universalUnderHypotheses := by decide

theorem bounded_horizon_ne_universal :
    QuantifierGrade.boundedHorizon ≠ QuantifierGrade.universalUnderHypotheses := by decide

end FoundationsVII
