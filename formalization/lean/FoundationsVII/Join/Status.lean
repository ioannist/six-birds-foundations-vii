import FoundationsVII.Join.Entry

/-!
# Declared-family join status calculus

The classifier is complete only for its declared finite Boolean interface.
Underlying axes may overlap even though the reported terminal status is a
single constructor.
-/

namespace FoundationsVII

inductive JoinStatus where
  | noEvidencedContact
  | evidencedContact
  | commonRefinement
  | lawfulComposite
  | strictJoin
  | obstructed
  | certifiedNoninteraction
  deriving Repr, DecidableEq, BEq, Inhabited

structure JoinAssessment where
  evidencedContact : Bool
  commonRefinement : Bool
  composite : Bool
  objecthood : Bool
  retention : Bool
  antiProduct : Bool
  sourceIndependent : Bool
  budgetPaid : Bool
  obstructionPresent : Bool
  noninteractionCertified : Bool
  deriving Repr, DecidableEq, BEq

namespace JoinAssessment

def StrictEligible (assessment : JoinAssessment) : Prop :=
  assessment.evidencedContact = true ∧
  assessment.composite = true ∧
  assessment.objecthood = true ∧
  assessment.retention = true ∧
  assessment.antiProduct = true ∧
  assessment.sourceIndependent = true ∧
  assessment.budgetPaid = true

instance (assessment : JoinAssessment) : Decidable (StrictEligible assessment) := by
  unfold StrictEligible
  infer_instance

def strictEligibleB (assessment : JoinAssessment) : Bool :=
  assessment.evidencedContact && assessment.composite &&
  assessment.objecthood && assessment.retention && assessment.antiProduct &&
  assessment.sourceIndependent && assessment.budgetPaid

def classify (assessment : JoinAssessment) : JoinStatus :=
  if assessment.noninteractionCertified then .certifiedNoninteraction
  else if assessment.obstructionPresent then .obstructed
  else if strictEligibleB assessment then .strictJoin
  else if assessment.composite then .lawfulComposite
  else if assessment.commonRefinement then .commonRefinement
  else if assessment.evidencedContact then .evidencedContact
  else .noEvidencedContact

theorem strictEligibleB_eq_true_iff (assessment : JoinAssessment) :
    strictEligibleB assessment = true ↔ StrictEligible assessment := by
  simp [strictEligibleB, StrictEligible, and_assoc]

theorem strict_status_constructor {assessment : JoinAssessment}
    (hNoninteraction : assessment.noninteractionCertified = false)
    (hObstruction : assessment.obstructionPresent = false)
    (hStrict : StrictEligible assessment) :
    classify assessment = JoinStatus.strictJoin := by
  simp [classify, hNoninteraction, hObstruction,
    (strictEligibleB_eq_true_iff assessment).2 hStrict]

theorem noninteraction_status_constructor {assessment : JoinAssessment}
    (h : assessment.noninteractionCertified = true) :
    classify assessment = JoinStatus.certifiedNoninteraction := by
  simp [classify, h]

theorem obstruction_status_constructor {assessment : JoinAssessment}
    (hNoNI : assessment.noninteractionCertified = false)
    (hObs : assessment.obstructionPresent = true) :
    classify assessment = JoinStatus.obstructed := by
  simp [classify, hNoNI, hObs]

def overlappingAxesExample : JoinAssessment :=
  { evidencedContact := true
    commonRefinement := true
    composite := true
    objecthood := true
    retention := true
    antiProduct := false
    sourceIndependent := false
    budgetPaid := false
    obstructionPresent := false
    noninteractionCertified := false }

theorem contact_refinement_and_composite_axes_may_overlap :
    overlappingAxesExample.evidencedContact = true ∧
    overlappingAxesExample.commonRefinement = true ∧
    overlappingAxesExample.composite = true := by decide

theorem overlapping_axes_classify_as_lawful_composite :
    classify overlappingAxesExample = JoinStatus.lawfulComposite := by decide

theorem noContact_ne_contact :
    JoinStatus.noEvidencedContact ≠ JoinStatus.evidencedContact := by decide

theorem contact_ne_strictJoin :
    JoinStatus.evidencedContact ≠ JoinStatus.strictJoin := by decide

theorem commonRefinement_ne_strictJoin :
    JoinStatus.commonRefinement ≠ JoinStatus.strictJoin := by decide

theorem obstructed_ne_certifiedNoninteraction :
    JoinStatus.obstructed ≠ JoinStatus.certifiedNoninteraction := by decide

end JoinAssessment

end FoundationsVII
