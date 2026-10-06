import FoundationsVII.Residuals.All

/-!
# Conditional categorical representations of join

Products, pullbacks, pushouts, and other universal constructions receive join
credit only after a finite package category, its admissible morphisms, and the
relevant universal-property check are declared.  A universal construction
never supplies anti-product novelty by itself.
-/

namespace FoundationsVII

inductive CategoricalConstructionKind where
  | product
  | pullback
  | pushout
  | declaredOther
  deriving Repr, DecidableEq, BEq, Inhabited

structure PackageMorphism where
  source : TheoryId
  target : TheoryId
  mapDescription : String
  admissible : Bool
  sourcePreserving : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace PackageMorphism

def WellFormed (morphism : PackageMorphism) : Prop :=
  morphism.mapDescription ≠ "" ∧
  morphism.admissible = true ∧
  morphism.sourcePreserving = true ∧
  morphism.audit.entries ≠ []

instance (morphism : PackageMorphism) : Decidable (WellFormed morphism) := by
  unfold WellFormed
  infer_instance

end PackageMorphism

/-- A finite declared category record.  The laws are proof obligations carried
as checked fields; this is deliberately not a universal claim about all SBT
packages or a global `Category` instance. -/
structure FinitePackageCategory where
  objects : List TheoryId
  morphisms : List PackageMorphism
  identitiesChecked : Bool
  compositionClosed : Bool
  associativityChecked : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace FinitePackageCategory

def WellFormed (category : FinitePackageCategory) : Prop :=
  category.objects ≠ [] ∧
  category.objects.Nodup ∧
  (∀ morphism, morphism ∈ category.morphisms →
    PackageMorphism.WellFormed morphism ∧
    morphism.source ∈ category.objects ∧
    morphism.target ∈ category.objects) ∧
  category.identitiesChecked = true ∧
  category.compositionClosed = true ∧
  category.associativityChecked = true ∧
  category.audit.entries ≠ []

instance (category : FinitePackageCategory) : Decidable (WellFormed category) := by
  unfold WellFormed
  infer_instance

theorem wellFormed_has_checked_category_laws
    {category : FinitePackageCategory} (h : WellFormed category) :
    category.identitiesChecked = true ∧
    category.compositionClosed = true ∧
    category.associativityChecked = true := by
  rcases h with ⟨_, _, _, hId, hComp, hAssoc, _⟩
  exact ⟨hId, hComp, hAssoc⟩

end FinitePackageCategory

structure UniversalConstructionCertificate where
  category : FinitePackageCategory
  construction : CategoricalConstructionKind
  apex : TheoryId
  leftProjection : PackageMorphism
  rightProjection : PackageMorphism
  universalProperty : String
  universalPropertyChecked : Bool
  preservesParents : Bool
  antiProductNoveltySeparatelyCertified : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace UniversalConstructionCertificate

def Valid (certificate : UniversalConstructionCertificate) : Prop :=
  FinitePackageCategory.WellFormed certificate.category ∧
  certificate.apex ∈ certificate.category.objects ∧
  PackageMorphism.WellFormed certificate.leftProjection ∧
  PackageMorphism.WellFormed certificate.rightProjection ∧
  certificate.leftProjection.source = certificate.apex ∧
  certificate.rightProjection.source = certificate.apex ∧
  certificate.universalProperty ≠ "" ∧
  certificate.universalPropertyChecked = true ∧
  certificate.preservesParents = true ∧
  certificate.audit.entries ≠ []

instance (certificate : UniversalConstructionCertificate) : Decidable (Valid certificate) := by
  unfold Valid
  infer_instance
/-- The categorical representation is licensed as a strict-join
representation only with independent anti-product novelty evidence. -/
def RepresentsStrictJoin (certificate : UniversalConstructionCertificate) : Prop :=
  Valid certificate ∧ certificate.antiProductNoveltySeparatelyCertified = true

theorem represents_strict_join_iff_valid_and_independently_novel
    (certificate : UniversalConstructionCertificate) :
    RepresentsStrictJoin certificate ↔
      Valid certificate ∧
      certificate.antiProductNoveltySeparatelyCertified = true := Iff.rfl

theorem representation_requires_explicit_universal_property
    {certificate : UniversalConstructionCertificate}
    (h : RepresentsStrictJoin certificate) :
    certificate.universalPropertyChecked = true := by
  rcases h.1 with ⟨_, _, _, _, _, _, _, hChecked, _, _⟩
  exact hChecked

theorem representation_preserves_declared_parents
    {certificate : UniversalConstructionCertificate}
    (h : RepresentsStrictJoin certificate) :
    certificate.preservesParents = true := by
  rcases h.1 with ⟨_, _, _, _, _, _, _, _, hParents, _⟩
  exact hParents

end UniversalConstructionCertificate

private def leftProjectionWitness : PackageMorphism :=
  { source := 3
    target := 1
    mapDescription := "left parent recovery projection"
    admissible := true
    sourcePreserving := true
    audit := phase3Audit }

private def rightProjectionWitness : PackageMorphism :=
  { source := 3
    target := 2
    mapDescription := "right parent recovery projection"
    admissible := true
    sourcePreserving := true
    audit := phase3Audit }

private def finitePackageCategoryWitness : FinitePackageCategory :=
  { objects := [1, 2, 3]
    morphisms := [leftProjectionWitness, rightProjectionWitness]
    identitiesChecked := true
    compositionClosed := true
    associativityChecked := true
    audit := phase3Audit }

private def productWithoutNovelty : UniversalConstructionCertificate :=
  { category := finitePackageCategoryWitness
    construction := .product
    apex := 3
    leftProjection := leftProjectionWitness
    rightProjection := rightProjectionWitness
    universalProperty := "unique pairing in the declared finite package category"
    universalPropertyChecked := true
    preservesParents := true
    antiProductNoveltySeparatelyCertified := false
    audit := phase3Audit }

private def specialCaseStrictRepresentation : UniversalConstructionCertificate :=
  { productWithoutNovelty with
    construction := .pullback
    antiProductNoveltySeparatelyCertified := true }

theorem finite_package_category_control_is_well_formed :
    FinitePackageCategory.WellFormed finitePackageCategoryWitness := by
  simp [FinitePackageCategory.WellFormed, finitePackageCategoryWitness,
    PackageMorphism.WellFormed, leftProjectionWitness,
    rightProjectionWitness, phase3Audit, phase3AuditEntry]

theorem mere_product_is_not_strict_join_credit :
    UniversalConstructionCertificate.Valid productWithoutNovelty ∧
    ¬ UniversalConstructionCertificate.RepresentsStrictJoin
      productWithoutNovelty := by
  simp [UniversalConstructionCertificate.Valid,
    UniversalConstructionCertificate.RepresentsStrictJoin,
    productWithoutNovelty, finitePackageCategoryWitness,
    FinitePackageCategory.WellFormed, PackageMorphism.WellFormed,
    leftProjectionWitness, rightProjectionWitness, phase3Audit,
    phase3AuditEntry]

theorem special_case_categorical_representation_is_conditional :
    UniversalConstructionCertificate.RepresentsStrictJoin
      specialCaseStrictRepresentation := by
  simp [UniversalConstructionCertificate.RepresentsStrictJoin,
    UniversalConstructionCertificate.Valid, specialCaseStrictRepresentation,
    productWithoutNovelty, finitePackageCategoryWitness,
    FinitePackageCategory.WellFormed, PackageMorphism.WellFormed,
    leftProjectionWitness, rightProjectionWitness, phase3Audit,
    phase3AuditEntry]

/-- DP04 terminal ruling: no unconditional categorical reduction.  The finite
countermodel is a valid checked product that preserves both parents but lacks
independent anti-product novelty. -/
theorem unconditional_categorical_reduction_countermodel :
    UniversalConstructionCertificate.Valid productWithoutNovelty ∧
    productWithoutNovelty.construction = CategoricalConstructionKind.product ∧
    productWithoutNovelty.antiProductNoveltySeparatelyCertified = false := by
  simp [UniversalConstructionCertificate.Valid, productWithoutNovelty,
    finitePackageCategoryWitness, FinitePackageCategory.WellFormed,
    PackageMorphism.WellFormed, leftProjectionWitness,
    rightProjectionWitness, phase3Audit, phase3AuditEntry]

end FoundationsVII
