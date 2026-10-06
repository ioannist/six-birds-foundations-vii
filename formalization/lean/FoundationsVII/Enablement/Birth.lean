import FoundationsVII.Enablement.Endogenous
import FoundationsVII.Contact.Transport

/-!
# Birth and participant-creation classification

Closure performed by a system and closure undergone by a system are distinct.
Contact may remain relation-only. Any credited new participant must survive the
declared closure and satisfy objecthood.
-/

namespace FoundationsVII

inductive ClosureAgency where
  | systemPerforms
  | systemUndergoes
  | peer
  | environment
  | mixed
  deriving Repr, DecidableEq, BEq, Inhabited

inductive BirthOutcome where
  | relationOnly
  | newLayer
  | newParticipant
  | refinementOnly
  deriving Repr, DecidableEq, BEq, Inhabited

/-- The four inherited activation classes are retained as an orthogonal
signature axis: packaging is present in all four; drive and staging anomaly
supply the two class bits.  This taxonomy does not itself assert participant
creation. -/
inductive InheritedBirthClass where
  | classI
  | classII
  | classIII
  | classIV
  deriving Repr, DecidableEq, BEq, Inhabited

structure PrimitiveBirthSignature where
  packaging : Bool
  drive : Bool
  stagingAnomaly : Bool
  deriving Repr, DecidableEq, BEq

def signatureOfInheritedClass : InheritedBirthClass → PrimitiveBirthSignature
  | .classI => { packaging := true, drive := false, stagingAnomaly := false }
  | .classII => { packaging := true, drive := true, stagingAnomaly := false }
  | .classIII => { packaging := true, drive := false, stagingAnomaly := true }
  | .classIV => { packaging := true, drive := true, stagingAnomaly := true }

def allInheritedBirthClasses : List InheritedBirthClass :=
  [.classI, .classII, .classIII, .classIV]

theorem inheritedBirthClass_mem_all (birthClass : InheritedBirthClass) :
    birthClass ∈ allInheritedBirthClasses := by
  cases birthClass <;> simp [allInheritedBirthClasses]

theorem inherited_birth_class_signatures_are_injective
    {left right : InheritedBirthClass}
    (h : signatureOfInheritedClass left = signatureOfInheritedClass right) :
    left = right := by
  cases left <;> cases right <;> simp [signatureOfInheritedClass] at h ⊢

theorem every_inherited_birth_class_activates_packaging
    (birthClass : InheritedBirthClass) :
    (signatureOfInheritedClass birthClass).packaging = true := by
  cases birthClass <;> rfl

structure ReachableBirthEvidence where
  birthClass : InheritedBirthClass
  generatorCarried : Bool
  generatorReachable : Bool
  generatorExecuted : Bool
  audited : Bool
  deriving Repr, DecidableEq, BEq

namespace ReachableBirthEvidence

def Valid (evidence : ReachableBirthEvidence) : Prop :=
  evidence.generatorCarried = true ∧
  evidence.generatorReachable = true ∧
  evidence.generatorExecuted = true ∧
  evidence.audited = true

instance (evidence : ReachableBirthEvidence) : Decidable (Valid evidence) := by
  unfold Valid
  infer_instance

theorem valid_requires_reachable_generator {evidence : ReachableBirthEvidence}
    (h : Valid evidence) : evidence.generatorReachable = true := h.2.1

end ReachableBirthEvidence

structure BirthRecord where
  agency : ClosureAgency
  outcome : BirthOutcome
  contactPresent : Bool
  survivesClosure : Bool
  objecthoodCertified : Bool
  performedBySystem : Bool
  participantCredit : Bool
  birthCredit : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace BirthRecord

def WellFormed (record : BirthRecord) : Prop :=
  record.audit.entries ≠ [] ∧
  (record.performedBySystem = true ↔ record.agency = .systemPerforms) ∧
  (record.participantCredit = true ↔
    record.outcome = .newParticipant ∧ record.contactPresent = true ∧
    record.survivesClosure = true ∧ record.objecthoodCertified = true) ∧
  (record.birthCredit = true ↔
    (record.outcome = .newLayer ∨ record.outcome = .newParticipant) ∧
    record.survivesClosure = true ∧ record.objecthoodCertified = true) ∧
  (record.outcome = .relationOnly → record.participantCredit = false)

instance (record : BirthRecord) : Decidable (WellFormed record) := by
  unfold WellFormed
  infer_instance

theorem participant_credit_requires_objecthood {record : BirthRecord}
    (h : WellFormed record) (hCredit : record.participantCredit = true) :
    record.objecthoodCertified = true := (h.2.2.1.mp hCredit).2.2.2

theorem participant_credit_requires_closure_survival {record : BirthRecord}
    (h : WellFormed record) (hCredit : record.participantCredit = true) :
    record.survivesClosure = true := (h.2.2.1.mp hCredit).2.2.1

theorem relation_only_has_no_participant_credit {record : BirthRecord}
    (h : WellFormed record) (hRelation : record.outcome = .relationOnly) :
    record.participantCredit = false := h.2.2.2.2 hRelation

end BirthRecord

structure BirthClassificationProfile where
  agency : ClosureAgency
  outcome : BirthOutcome
  objecthood : Bool
  survivesClosure : Bool
  contact : Bool
  deriving Repr, DecidableEq, BEq

private def relationOnlyContact : BirthClassificationProfile :=
  { agency := .peer, outcome := .relationOnly, objecthood := false,
    survivesClosure := false, contact := true }

private def systemPerformedBirth : BirthClassificationProfile :=
  { agency := .systemPerforms, outcome := .newLayer, objecthood := true,
    survivesClosure := true, contact := false }

private def systemUnderwentBirth : BirthClassificationProfile :=
  { agency := .systemUndergoes, outcome := .newLayer, objecthood := true,
    survivesClosure := true, contact := true }

theorem contact_can_remain_relation_only :
    ∃ profile : BirthClassificationProfile,
      profile.contact = true ∧ profile.outcome = .relationOnly ∧
      profile.objecthood = false :=
  ⟨relationOnlyContact, rfl, rfl, rfl⟩

theorem closure_performed_and_closure_undergone_are_distinct :
    systemPerformedBirth.agency ≠ systemUnderwentBirth.agency := by decide

theorem system_performed_birth_control :
    systemPerformedBirth.agency = .systemPerforms ∧
    systemPerformedBirth.outcome = .newLayer ∧
    systemPerformedBirth.objecthood = true ∧
    systemPerformedBirth.survivesClosure = true := by decide

theorem system_underwent_birth_control :
    systemUnderwentBirth.agency = .systemUndergoes ∧
    systemUnderwentBirth.outcome = .newLayer ∧
    systemUnderwentBirth.objecthood = true ∧
    systemUnderwentBirth.survivesClosure = true := by decide

theorem inherited_activation_class_does_not_by_itself_create_participant :
    ∃ birthClass : InheritedBirthClass,
      (signatureOfInheritedClass birthClass).packaging = true ∧
      relationOnlyContact.outcome = .relationOnly ∧
      relationOnlyContact.objecthood = false := by
  exact ⟨.classI, rfl, rfl, rfl⟩

/-- DP09: contact may create a relation; participant credit needs objecthood. -/
theorem participant_creation_is_conditional_not_automatic :
    (∃ profile : BirthClassificationProfile,
      profile.contact = true ∧ profile.outcome = .relationOnly) ∧
    (∃ profile : BirthClassificationProfile,
      profile.outcome = .newLayer ∧ profile.objecthood = true ∧
      profile.survivesClosure = true) := by
  exact ⟨⟨relationOnlyContact, rfl, rfl⟩,
    ⟨systemPerformedBirth, rfl, rfl, rfl⟩⟩

end FoundationsVII
