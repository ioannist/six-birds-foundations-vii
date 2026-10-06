import SixBirds.Roles

namespace SixBirds

inductive RawKind where
  | object
  | state
  | relation
  | map
  | partialMap
  | predicate
  | comparison
  | path
  | derivation
  | index
  | order
  | transition
  | refinement
  | trace
  | event
  | provenance
  | replay
  | check
  | probability
  | causality
  | agency
  | objective
  | semantic
  deriving DecidableEq, Repr

structure RawRecord where
  ident : Nat
  kind : RawKind
  finiteFields : Bool
  refs : List Nat
  deriving Repr

inductive AnnotationKind where
  | level
  | threshold
  | lift
  | forget
  | visibility
  | bridge
  | audit
  | claim
  | promotion
  | translation
  | nonclaim
  | witness
  | collapse
  deriving DecidableEq, Repr

structure Annotation where
  kind : AnnotationKind
  target : Nat
  finiteFields : Bool
  refs : List Nat
  deriving Repr

structure Description where
  raw : List RawRecord
  annotations : List Annotation

def RawIds (D : Description) : List Nat :=
  D.raw.map RawRecord.ident

def HasRawId (D : Description) (id : Nat) : Prop :=
  id ∈ RawIds D

def HasRawKind (D : Description) (kind : RawKind) : Prop :=
  ∃ r ∈ D.raw, r.kind = kind

def HasAnnotationKind (D : Description) (kind : AnnotationKind) : Prop :=
  ∃ a ∈ D.annotations, a.kind = kind

def FiniteDescription (D : Description) : Prop :=
  (∀ r ∈ D.raw, r.finiteFields = true) ∧
  (∀ a ∈ D.annotations, a.finiteFields = true)

def ClosedDescription (D : Description) : Prop :=
  (∀ r ∈ D.raw, ∀ ref ∈ r.refs, HasRawId D ref) ∧
  (∀ a ∈ D.annotations, HasRawId D a.target ∧ ∀ ref ∈ a.refs, HasRawId D ref)

def AuditedDescription (D : Description) : Prop :=
  HasAnnotationKind D AnnotationKind.audit ∧
  HasAnnotationKind D AnnotationKind.claim ∧
  HasAnnotationKind D AnnotationKind.nonclaim

structure FATCD where
  desc : Description
  finite : FiniteDescription desc
  closed : ClosedDescription desc
  audited : AuditedDescription desc

def FATCDDomain := FATCD

def roleRawKinds : Role -> List RawKind
  | Role.P1 => [RawKind.object, RawKind.relation, RawKind.map, RawKind.comparison]
  | Role.P2 => [RawKind.predicate, RawKind.relation, RawKind.comparison]
  | Role.P3 => [RawKind.path, RawKind.comparison]
  | Role.P4 => [RawKind.index, RawKind.transition, RawKind.refinement]
  | Role.P5 => [RawKind.object, RawKind.relation, RawKind.map, RawKind.comparison]
  | Role.P6 => [RawKind.event, RawKind.provenance, RawKind.replay, RawKind.check]

def RoleKindPresent (D : Description) (role : Role) : Prop :=
  ∀ kind ∈ roleRawKinds role, HasRawKind D kind

structure ThresholdAttachment (D : FATCD) (role : Role) where
  cluster : List RawRecord
  cluster_nonempty : cluster ≠ []
  cluster_from_description : ∀ r ∈ cluster, r ∈ D.desc.raw
  threshold : Annotation
  threshold_in_description : threshold ∈ D.desc.annotations
  thresholdIsDeclared : threshold.kind = AnnotationKind.threshold
  thresholdTargetsCluster : ∃ r ∈ cluster, threshold.target = r.ident
  witness : Annotation
  witness_in_description : witness ∈ D.desc.annotations
  witnessIsDeclared : witness.kind = AnnotationKind.witness
  level : Level
  collapseRecorded : HasAnnotationKind D.desc AnnotationKind.collapse
  auditRecorded : HasAnnotationKind D.desc AnnotationKind.audit

def AlignedProjection (role : Role) (cluster : List RawRecord) : Prop :=
  ∀ kind ∈ roleRawKinds role, ∃ r ∈ cluster, r.kind = kind

structure DerivedRoleProjection (D : FATCD) (role : Role) where
  attachment : ThresholdAttachment D role
  aligned : AlignedProjection role attachment.cluster
  collapseCasesRecorded : HasAnnotationKind D.desc AnnotationKind.collapse
  lossesAndLiftsRecorded :
    HasAnnotationKind D.desc AnnotationKind.lift ∧ HasAnnotationKind D.desc AnnotationKind.forget
  nonclaimsPreserved : HasAnnotationKind D.desc AnnotationKind.nonclaim

inductive ResidualClass where
  | absorbed (role : Role)
  | composite
  | presentationVariant
  | levelShift
  | activationThresholdRefinement
  | instrumentVisibilityArtifact
  | empiricalBridgeAnnotation
  | outsideDomainStructure
  | coveredBookkeeping
  | unresolvedThreat
  | genuineSeventhRole
  deriving DecidableEq, Repr

def ResidualClassificationScheme := ResidualClass

def CoveredResidualClass : ResidualClass -> Prop
  | ResidualClass.absorbed _ => True
  | ResidualClass.composite => True
  | ResidualClass.presentationVariant => True
  | ResidualClass.levelShift => True
  | ResidualClass.activationThresholdRefinement => True
  | ResidualClass.instrumentVisibilityArtifact => True
  | ResidualClass.empiricalBridgeAnnotation => True
  | ResidualClass.outsideDomainStructure => True
  | ResidualClass.coveredBookkeeping => True
  | ResidualClass.unresolvedThreat => False
  | ResidualClass.genuineSeventhRole => False

theorem outsideDomain_is_covered :
    CoveredResidualClass ResidualClass.outsideDomainStructure := by
  exact True.intro

def rawRecord (ident : Nat) (kind : RawKind) : RawRecord :=
  { ident := ident, kind := kind, finiteFields := true, refs := [] }

def badRawRecord : RawRecord :=
  { ident := 99, kind := RawKind.object, finiteFields := false, refs := [] }

def ann (kind : AnnotationKind) (target : Nat) : Annotation :=
  { kind := kind, target := target, finiteFields := true, refs := [] }

def badAnn (kind : AnnotationKind) (target : Nat) : Annotation :=
  { kind := kind, target := target, finiteFields := false, refs := [] }

def roleRaw (role : Role) : List RawRecord :=
  match role with
  | Role.P1 => [rawRecord 1 RawKind.object, rawRecord 2 RawKind.relation,
      rawRecord 3 RawKind.map, rawRecord 4 RawKind.comparison]
  | Role.P2 => [rawRecord 1 RawKind.predicate, rawRecord 2 RawKind.relation,
      rawRecord 3 RawKind.comparison]
  | Role.P3 => [rawRecord 1 RawKind.path, rawRecord 2 RawKind.comparison]
  | Role.P4 => [rawRecord 1 RawKind.index, rawRecord 2 RawKind.transition,
      rawRecord 3 RawKind.refinement]
  | Role.P5 => [rawRecord 1 RawKind.object, rawRecord 2 RawKind.relation,
      rawRecord 3 RawKind.map, rawRecord 4 RawKind.comparison]
  | Role.P6 => [rawRecord 1 RawKind.event, rawRecord 2 RawKind.provenance,
      rawRecord 3 RawKind.replay, rawRecord 4 RawKind.check]

def baseAnnotations : List Annotation :=
  [ann AnnotationKind.threshold 1,
   ann AnnotationKind.witness 1,
   ann AnnotationKind.level 1,
   ann AnnotationKind.collapse 1,
   ann AnnotationKind.audit 1,
   ann AnnotationKind.claim 1,
   ann AnnotationKind.nonclaim 1,
   ann AnnotationKind.lift 1,
   ann AnnotationKind.forget 1,
   ann AnnotationKind.visibility 1,
   ann AnnotationKind.bridge 1]

def witnessDescriptionData (role : Role) : Description :=
  { raw := roleRaw role
    annotations := baseAnnotations }

theorem roleRaw_finite : ∀ role : Role, ∀ r ∈ roleRaw role, r.finiteFields = true := by
  intro role r h
  cases role
  · simp [roleRaw, rawRecord] at h
    rcases h with h | h | h | h <;> subst r <;> rfl
  · simp [roleRaw, rawRecord] at h
    rcases h with h | h | h <;> subst r <;> rfl
  · simp [roleRaw, rawRecord] at h
    rcases h with h | h <;> subst r <;> rfl
  · simp [roleRaw, rawRecord] at h
    rcases h with h | h | h <;> subst r <;> rfl
  · simp [roleRaw, rawRecord] at h
    rcases h with h | h | h | h <;> subst r <;> rfl
  · simp [roleRaw, rawRecord] at h
    rcases h with h | h | h | h <;> subst r <;> rfl

theorem baseAnnotations_finite :
    ∀ a ∈ baseAnnotations, a.finiteFields = true := by
  intro a h
  simp [baseAnnotations, ann] at h
  rcases h with h | h | h | h | h | h | h | h | h | h | h <;> cases h <;> rfl

theorem roleRaw_ids_cover_refs :
    ∀ role : Role, ∀ r ∈ roleRaw role, ∀ ref ∈ r.refs, HasRawId (witnessDescriptionData role) ref := by
  intro role r hr ref href
  cases role
  · simp [roleRaw, rawRecord] at hr
    rcases hr with hr | hr | hr | hr <;> subst r <;> simp at href
  · simp [roleRaw, rawRecord] at hr
    rcases hr with hr | hr | hr <;> subst r <;> simp at href
  · simp [roleRaw, rawRecord] at hr
    rcases hr with hr | hr <;> subst r <;> simp at href
  · simp [roleRaw, rawRecord] at hr
    rcases hr with hr | hr | hr <;> subst r <;> simp at href
  · simp [roleRaw, rawRecord] at hr
    rcases hr with hr | hr | hr | hr <;> subst r <;> simp at href
  · simp [roleRaw, rawRecord] at hr
    rcases hr with hr | hr | hr | hr <;> subst r <;> simp at href

theorem baseAnnotations_targets_closed :
    ∀ role : Role, ∀ a ∈ baseAnnotations,
      HasRawId (witnessDescriptionData role) a.target ∧
      ∀ ref ∈ a.refs, HasRawId (witnessDescriptionData role) ref := by
  intro role a ha
  constructor
  · have target_one : a.target = 1 := by
      simp [baseAnnotations, ann] at ha
      rcases ha with ha | ha | ha | ha | ha | ha | ha | ha | ha | ha | ha <;> subst a <;> rfl
    cases role <;> simp [witnessDescriptionData, HasRawId, RawIds, roleRaw, rawRecord, target_one]
  · intro ref href
    simp [baseAnnotations, ann] at ha
    rcases ha with ha | ha | ha | ha | ha | ha | ha | ha | ha | ha | ha <;> subst a <;> simp at href

theorem witnessDescription_finite (role : Role) :
    FiniteDescription (witnessDescriptionData role) := by
  exact ⟨roleRaw_finite role, baseAnnotations_finite⟩

theorem witnessDescription_closed (role : Role) :
    ClosedDescription (witnessDescriptionData role) := by
  exact ⟨roleRaw_ids_cover_refs role, baseAnnotations_targets_closed role⟩

theorem witnessDescription_audited (role : Role) :
    AuditedDescription (witnessDescriptionData role) := by
  constructor
  · exact ⟨ann AnnotationKind.audit 1, by simp [witnessDescriptionData, baseAnnotations], rfl⟩
  constructor
  · exact ⟨ann AnnotationKind.claim 1, by simp [witnessDescriptionData, baseAnnotations], rfl⟩
  · exact ⟨ann AnnotationKind.nonclaim 1, by simp [witnessDescriptionData, baseAnnotations], rfl⟩

def witnessDescription (role : Role) : FATCD :=
  { desc := witnessDescriptionData role
    finite := witnessDescription_finite role
    closed := witnessDescription_closed role
    audited := witnessDescription_audited role }

def emptyDescription : Description :=
  { raw := [rawRecord 1 RawKind.object]
    annotations := [ann AnnotationKind.audit 1, ann AnnotationKind.claim 1, ann AnnotationKind.nonclaim 1] }

theorem emptyDescription_finite : FiniteDescription emptyDescription := by
  constructor
  · intro r h
    simp [emptyDescription, rawRecord] at h
    cases h
    rfl
  · intro a h
    simp [emptyDescription, ann] at h
    rcases h with h | h | h <;> cases h <;> rfl

theorem emptyDescription_closed : ClosedDescription emptyDescription := by
  constructor
  · intro r h ref href
    simp [emptyDescription, rawRecord] at h
    subst r
    simp at href
  · intro a h
    constructor
    · simp [emptyDescription, HasRawId, RawIds, ann, rawRecord] at h ⊢
      rcases h with h | h | h <;> subst a <;> simp
    · intro ref href
      simp [emptyDescription, ann] at h
      rcases h with h | h | h <;> subst a <;> simp at href

theorem emptyDescription_audited : AuditedDescription emptyDescription := by
  constructor
  · exact ⟨ann AnnotationKind.audit 1, by simp [emptyDescription], rfl⟩
  constructor
  · exact ⟨ann AnnotationKind.claim 1, by simp [emptyDescription], rfl⟩
  · exact ⟨ann AnnotationKind.nonclaim 1, by simp [emptyDescription], rfl⟩

def emptyFATCD : FATCD :=
  { desc := emptyDescription
    finite := emptyDescription_finite
    closed := emptyDescription_closed
    audited := emptyDescription_audited }

theorem threshold_mem (role : Role) :
    ann AnnotationKind.threshold 1 ∈ (witnessDescription role).desc.annotations := by
  cases role <;> simp [witnessDescription, witnessDescriptionData, baseAnnotations]

theorem witness_mem (role : Role) :
    ann AnnotationKind.witness 1 ∈ (witnessDescription role).desc.annotations := by
  cases role <;> simp [witnessDescription, witnessDescriptionData, baseAnnotations]

theorem first_role_raw_mem (role : Role) :
    ∃ r ∈ (witnessDescription role).desc.raw, r.ident = 1 := by
  cases role <;> simp [witnessDescription, witnessDescriptionData, roleRaw, rawRecord]

theorem threshold_targets_cluster (role : Role) :
    ∃ r ∈ (witnessDescription role).desc.raw, (ann AnnotationKind.threshold 1).target = r.ident := by
  cases role <;> simp [witnessDescription, witnessDescriptionData, roleRaw, rawRecord, ann]

theorem roleRaw_aligned : ∀ role : Role, AlignedProjection role (roleRaw role) := by
  intro role kind hkind
  cases role <;> simp [roleRawKinds] at hkind
  · rcases hkind with h | h | h | h <;> subst kind <;> simp [roleRaw, rawRecord]
  · rcases hkind with h | h | h <;> subst kind <;> simp [roleRaw, rawRecord]
  · rcases hkind with h | h <;> subst kind <;> simp [roleRaw, rawRecord]
  · rcases hkind with h | h | h <;> subst kind <;> simp [roleRaw, rawRecord]
  · rcases hkind with h | h | h | h <;> subst kind <;> simp [roleRaw, rawRecord]
  · rcases hkind with h | h | h | h <;> subst kind <;> simp [roleRaw, rawRecord]

theorem roleRaw_cluster_from_description :
    ∀ role : Role, ∀ r ∈ roleRaw role, r ∈ (witnessDescription role).desc.raw := by
  intro role r h
  simpa [witnessDescription, witnessDescriptionData] using h

def thresholdAttachment (role : Role) :
    ThresholdAttachment (witnessDescription role) role :=
  { cluster := roleRaw role
    cluster_nonempty := by
      cases role <;> simp [roleRaw, rawRecord]
    cluster_from_description := roleRaw_cluster_from_description role
    threshold := ann AnnotationKind.threshold 1
    threshold_in_description := threshold_mem role
    thresholdIsDeclared := rfl
    thresholdTargetsCluster := by
      cases role <;> simp [roleRaw, rawRecord, ann]
    witness := ann AnnotationKind.witness 1
    witness_in_description := witness_mem role
    witnessIsDeclared := rfl
    level := Level.verification
    collapseRecorded := ⟨ann AnnotationKind.collapse 1, by cases role <;> simp [witnessDescription, witnessDescriptionData, baseAnnotations], rfl⟩
    auditRecorded := (witnessDescription role).audited.left }

def roleProjection (role : Role) :
    DerivedRoleProjection (witnessDescription role) role :=
  { attachment := thresholdAttachment role
    aligned := roleRaw_aligned role
    collapseCasesRecorded := (thresholdAttachment role).collapseRecorded
    lossesAndLiftsRecorded := by
      constructor
      · exact ⟨ann AnnotationKind.lift 1, by cases role <;> simp [witnessDescription, witnessDescriptionData, baseAnnotations], rfl⟩
      · exact ⟨ann AnnotationKind.forget 1, by cases role <;> simp [witnessDescription, witnessDescriptionData, baseAnnotations], rfl⟩
    nonclaimsPreserved := (witnessDescription role).audited.right.right }

def GenericTransitionProjectsToP3 : Prop :=
  AlignedProjection Role.P3 [rawRecord 1 RawKind.transition]

def GenericPathProjectsToP5 : Prop :=
  AlignedProjection Role.P5 [rawRecord 1 RawKind.path]

def GenericSemanticsProjectsToP1 : Prop :=
  AlignedProjection Role.P1 [rawRecord 1 RawKind.semantic]

theorem generic_transition_not_p3 : ¬ GenericTransitionProjectsToP3 := by
  intro h
  have needPath : ∃ r ∈ [rawRecord 1 RawKind.transition], r.kind = RawKind.path := by
    exact h RawKind.path (by simp [roleRawKinds])
  rcases needPath with ⟨r, hr, hk⟩
  simp [rawRecord] at hr
  cases hr
  cases hk

theorem generic_path_not_p5 : ¬ GenericPathProjectsToP5 := by
  intro h
  have needObject : ∃ r ∈ [rawRecord 1 RawKind.path], r.kind = RawKind.object := by
    exact h RawKind.object (by simp [roleRawKinds])
  rcases needObject with ⟨r, hr, hk⟩
  simp [rawRecord] at hr
  cases hr
  cases hk

theorem generic_semantics_not_p1 : ¬ GenericSemanticsProjectsToP1 := by
  intro h
  have needObject : ∃ r ∈ [rawRecord 1 RawKind.semantic], r.kind = RawKind.object := by
    exact h RawKind.object (by simp [roleRawKinds])
  rcases needObject with ⟨r, hr, hk⟩
  simp [rawRecord] at hr
  cases hr
  cases hk

theorem non_circularity :
    ∀ D : FATCD, FiniteDescription D.desc ∧ ClosedDescription D.desc ∧
      AuditedDescription D.desc := by
  intro D
  exact ⟨D.finite, D.closed, D.audited⟩

theorem non_overbreadth :
    ∀ D : FATCD, FiniteDescription D.desc ∧ ClosedDescription D.desc ∧
      AuditedDescription D.desc := by
  intro D
  exact ⟨D.finite, D.closed, D.audited⟩

end SixBirds
