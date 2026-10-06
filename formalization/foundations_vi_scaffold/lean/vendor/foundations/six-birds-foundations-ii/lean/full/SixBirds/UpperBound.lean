import SixBirds.LowerBounds

namespace SixBirds

def classifyResidual (r : RawRecord) : ResidualClass :=
  match r.kind with
  | RawKind.probability => ResidualClass.composite
  | RawKind.causality => ResidualClass.composite
  | RawKind.agency => ResidualClass.empiricalBridgeAnnotation
  | RawKind.event => ResidualClass.absorbed Role.P6
  | RawKind.provenance => ResidualClass.absorbed Role.P6
  | RawKind.replay => ResidualClass.absorbed Role.P6
  | RawKind.check => ResidualClass.absorbed Role.P6
  | RawKind.transition => ResidualClass.absorbed Role.P4
  | RawKind.refinement => ResidualClass.absorbed Role.P4
  | RawKind.index => ResidualClass.absorbed Role.P4
  | RawKind.order => ResidualClass.absorbed Role.P4
  | RawKind.path => ResidualClass.absorbed Role.P3
  | RawKind.derivation => ResidualClass.absorbed Role.P3
  | RawKind.trace => ResidualClass.coveredBookkeeping
  | RawKind.predicate => ResidualClass.absorbed Role.P2
  | RawKind.relation => ResidualClass.composite
  | RawKind.map => ResidualClass.composite
  | RawKind.partialMap => ResidualClass.composite
  | RawKind.comparison => ResidualClass.coveredBookkeeping
  | RawKind.object => ResidualClass.presentationVariant
  | RawKind.state => ResidualClass.presentationVariant
  | RawKind.objective => ResidualClass.empiricalBridgeAnnotation
  | RawKind.semantic => ResidualClass.outsideDomainStructure

def ClassifiedWithinCoveredScope (_D : FATCD) (r : RawRecord) : Prop :=
  CoveredResidualClass (classifyResidual r)

theorem classifyResidual_covered : ∀ r : RawRecord, CoveredResidualClass (classifyResidual r) := by
  intro r
  cases r with
  | mk ident kind finiteFields refs =>
    cases kind <;> exact True.intro

theorem alignment_rules :
    ∀ (D : FATCD) (role : Role) (p : DerivedRoleProjection D role),
      AlignedProjection role p.attachment.cluster := by
  intro D role p
  exact p.aligned

theorem probability_closure :
    ∀ D : FATCD, ClassifiedWithinCoveredScope D (rawRecord 0 RawKind.probability) := by
  intro D
  exact True.intro

theorem causality_closure :
    ∀ D : FATCD, ClassifiedWithinCoveredScope D (rawRecord 0 RawKind.causality) := by
  intro D
  exact True.intro

theorem agency_closure :
    ∀ D : FATCD, ClassifiedWithinCoveredScope D (rawRecord 0 RawKind.agency) := by
  intro D
  exact True.intro

theorem upper_bound_classification :
    ∀ (D : FATCD) (r : RawRecord), ClassifiedWithinCoveredScope D r := by
  intro D r
  exact classifyResidual_covered r

theorem unresolved_and_genuine_seventh_empty :
    ∀ (_D : FATCD) (r : RawRecord), classifyResidual r ≠ ResidualClass.unresolvedThreat ∧
      classifyResidual r ≠ ResidualClass.genuineSeventhRole := by
  intro _D r
  constructor
  · intro h
    have covered := classifyResidual_covered r
    rw [h] at covered
    exact covered
  · intro h
    have covered := classifyResidual_covered r
    rw [h] at covered
    exact covered

end SixBirds
