import SixBirdsMetaMath.FoundationsIV.Transport.DescentRepair

/-!
F49 Common-Source / Nonlocal Correlation Normal Form.

A correlation is structurally explained only when its joint residual is carried
by a declared common source, a lawful directed route, or a declared shared
interface. If none of those role-specific factorization records is supplied,
the dependency remains a statused residual, and nonlocality is always relative
to a declared locality package.
-/

namespace SixBirdsMetaMath.FoundationsIV.SelfReferenceLimits.CommonSourceNonlocal

open SixBirdsMetaMath.FoundationsIV.Transport.DescentRepair

/-- The joint readout `(a, b)` of two local probes. -/
def jointReadout {H A B : Type} (readoutA : H → A) (readoutB : H → B) :
    H → A × B :=
  fun h => (readoutA h, readoutB h)

/-- The quotient carrying a declared common source together with the two local
access packages. -/
def commonSourceCorrelationQuotient {H S LA LB : Type} (source : H → S)
    (leftAccess : H → LA) (rightAccess : H → LB) : H → (S × LA) × LB :=
  fun h => ((source h, leftAccess h), rightAccess h)

/-- The quotient carrying a shared interface together with the two local access
packages. -/
def interfaceCorrelationQuotient {H I LA LB : Type} (sharedInterface : H → I)
    (leftAccess : H → LA) (rightAccess : H → LB) : H → (I × LA) × LB :=
  fun h => ((sharedInterface h, leftAccess h), rightAccess h)

/-- Common-source explanation at the joint-residual layer: the joint readout
descends through `(source, leftAccess, rightAccess)`. -/
def CommonSourceFactorization {H S LA LB A B : Type} (source : H → S)
    (leftAccess : H → LA) (rightAccess : H → LB)
    (readoutA : H → A) (readoutB : H → B) : Prop :=
  Descends (commonSourceCorrelationQuotient source leftAccess rightAccess)
    (fun h : H => h) (jointReadout readoutA readoutB)

/-- Common-source obstruction: same source and local data, different joint
readout. -/
def CommonSourceObstruction {H S LA LB A B : Type} (source : H → S)
    (leftAccess : H → LA) (rightAccess : H → LB)
    (readoutA : H → A) (readoutB : H → B) : (H × H) → Prop :=
  splitPairObstruction
    (commonSourceCorrelationQuotient source leftAccess rightAccess)
    (fun h : H => h) (jointReadout readoutA readoutB)

/-- No common-source obstruction is present. -/
def CommonSourceObstructionEmpty {H S LA LB A B : Type} (source : H → S)
    (leftAccess : H → LA) (rightAccess : H → LB)
    (readoutA : H → A) (readoutB : H → B) : Prop :=
  ObstructionEmpty
    (CommonSourceObstruction source leftAccess rightAccess readoutA readoutB)

/-- Deterministic local response maps for a common source. This is stronger
than bare joint descent and records the source's role as a shared cause rather
than an untyped joint interface. -/
def CommonSourceResponseStructure {H S LA LB A B : Type} (source : H → S)
    (leftAccess : H → LA) (rightAccess : H → LB)
    (readoutA : H → A) (readoutB : H → B) : Prop :=
  ∃ responseA : S × LA → A, ∃ responseB : S × LB → B,
    responseA ∘ (fun h : H => (source h, leftAccess h)) = readoutA ∧
      responseB ∘ (fun h : H => (source h, rightAccess h)) = readoutB

/-- A role-declared common-source explanation supplies both joint descent and
the local response structure. -/
def CommonSourceExplanation {H S LA LB A B : Type} (source : H → S)
    (leftAccess : H → LA) (rightAccess : H → LB)
    (readoutA : H → A) (readoutB : H → B) : Prop :=
  CommonSourceFactorization source leftAccess rightAccess readoutA readoutB ∧
    CommonSourceResponseStructure source leftAccess rightAccess readoutA readoutB

/-- Interface-mediated explanation: the joint readout descends through the
shared interface and local packages. -/
def InterfaceMediatedFactorization {H I LA LB A B : Type}
    (sharedInterface : H → I) (leftAccess : H → LA) (rightAccess : H → LB)
    (readoutA : H → A) (readoutB : H → B) : Prop :=
  Descends (interfaceCorrelationQuotient sharedInterface leftAccess rightAccess)
    (fun h : H => h) (jointReadout readoutA readoutB)

/-- Interface obstruction: same interface and local data, different joint
readout. -/
def InterfaceMediatedObstruction {H I LA LB A B : Type}
    (sharedInterface : H → I) (leftAccess : H → LA) (rightAccess : H → LB)
    (readoutA : H → A) (readoutB : H → B) : (H × H) → Prop :=
  splitPairObstruction
    (interfaceCorrelationQuotient sharedInterface leftAccess rightAccess)
    (fun h : H => h) (jointReadout readoutA readoutB)

/-- No interface-mediated obstruction is present. -/
def InterfaceMediatedObstructionEmpty {H I LA LB A B : Type}
    (sharedInterface : H → I) (leftAccess : H → LA) (rightAccess : H → LB)
    (readoutA : H → A) (readoutB : H → B) : Prop :=
  ObstructionEmpty
    (InterfaceMediatedObstruction sharedInterface leftAccess rightAccess readoutA readoutB)

/-- Route transport descent for a declared directed route/intervention package.
The route is not mere order: admissibility and stability are separate records. -/
def DirectRouteFactorization {RouteContext RouteQuotient RouteTarget Residue : Type}
    (routeQuotient : RouteContext → RouteQuotient)
    (routeTransport : RouteContext → RouteTarget)
    (targetResidue : RouteTarget → Residue) : Prop :=
  Descends routeQuotient routeTransport targetResidue

/-- Direct-route obstruction: same route quotient, different target residue. -/
def DirectRouteObstruction {RouteContext RouteQuotient RouteTarget Residue : Type}
    (routeQuotient : RouteContext → RouteQuotient)
    (routeTransport : RouteContext → RouteTarget)
    (targetResidue : RouteTarget → Residue) : (RouteContext × RouteContext) → Prop :=
  splitPairObstruction routeQuotient routeTransport targetResidue

/-- No direct-route obstruction is present. -/
def DirectRouteObstructionEmpty {RouteContext RouteQuotient RouteTarget Residue : Type}
    (routeQuotient : RouteContext → RouteQuotient)
    (routeTransport : RouteContext → RouteTarget)
    (targetResidue : RouteTarget → Residue) : Prop :=
  ObstructionEmpty (DirectRouteObstruction routeQuotient routeTransport targetResidue)

/-- A role-declared direct-route explanation records admissibility, stability,
and route descent. -/
def DirectRouteExplanation {RouteContext RouteQuotient RouteTarget Residue : Type}
    (routeAdmissible routeStable : Prop)
    (routeQuotient : RouteContext → RouteQuotient)
    (routeTransport : RouteContext → RouteTarget)
    (targetResidue : RouteTarget → Residue) : Prop :=
  routeAdmissible ∧ routeStable ∧
    DirectRouteFactorization routeQuotient routeTransport targetResidue

/-- A source is hidden from current observation when it does not descend through
the current access quotient. -/
def HiddenCommonSource {H Current S : Type} (currentAccess : H → Current)
    (source : H → S) : Prop :=
  ¬ Descends currentAccess (fun h : H => h) source

/-- Product independence is the null-correlation baseline: the declared
correlation residual vanishes. -/
def ProductIndependence (residualVanishes : Prop) : Prop :=
  residualVanishes

/-- Accepted correlation explanation is a role-declared source, route, or
interface record. -/
def AcceptedCorrelationExplanation (commonSource directRoute sharedInterface : Prop) :
    Prop :=
  commonSource ∨ directRoute ∨ sharedInterface

/-- If no explanatory role is supplied, a present dependency is a statused
correlation residual, not an explained relation. -/
def CorrelationResidual (correlationPresent commonSource directRoute sharedInterface :
    Prop) : Prop :=
  correlationPresent ∧ ¬ commonSource ∧ ¬ directRoute ∧ ¬ sharedInterface

/-- Nonlocal residual status is locality-relative: it is a residual dependency
plus failure of the declared locality package. -/
def NonlocalCorrelationResidual (correlationPresent localityPackage commonSource
    directRoute sharedInterface : Prop) : Prop :=
  CorrelationResidual correlationPresent commonSource directRoute sharedInterface ∧
    ¬ localityPackage

/-- Source status vocabulary for common-source and nonlocal-correlation claims. -/
inductive CorrelationStatus where
  | productIndependence
  | commonSource
  | hiddenCommonSource
  | probabilisticCommonSource
  | directRoute
  | bidirectionalRoute
  | feedbackCorrelation
  | interfaceMediated
  | boundaryMediated
  | horizonMediated
  | bridgeMediatedCorrelation
  | localityResidual
  | nonlocalCorrelationResidual
  | correlationResidual
  | commonSourceFailure
  | routeFailure
  | interfaceLeakage
  | contextCoupledSource
  | selectionConditionedCorrelation
  | postselectedCorrelation
  | presentationCorrelationArtifact
  | protocolCorrelationArtifact
  | topologicalCorrelation
  | anomalyMediatedCorrelation
  | correlationDualityMismatch
  | correlationOverread
deriving DecidableEq

/-- Meaning assignment for the F49 correlation status vocabulary. -/
def CorrelationStatusHolds (product commonSource hiddenSource probabilisticSource
    directRoute bidirectional feedback interface boundary horizon bridge localityResidual
    nonlocalResidual residual sourceFailure routeFailure interfaceLeakage
    contextCoupled selectionConditioned postselected presentationArtifact protocolArtifact
    topological anomalyMediated dualityMismatch overread : Prop) :
    CorrelationStatus → Prop
  | CorrelationStatus.productIndependence => product
  | CorrelationStatus.commonSource => commonSource
  | CorrelationStatus.hiddenCommonSource => hiddenSource
  | CorrelationStatus.probabilisticCommonSource => probabilisticSource
  | CorrelationStatus.directRoute => directRoute
  | CorrelationStatus.bidirectionalRoute => bidirectional
  | CorrelationStatus.feedbackCorrelation => feedback
  | CorrelationStatus.interfaceMediated => interface
  | CorrelationStatus.boundaryMediated => boundary
  | CorrelationStatus.horizonMediated => horizon
  | CorrelationStatus.bridgeMediatedCorrelation => bridge
  | CorrelationStatus.localityResidual => localityResidual
  | CorrelationStatus.nonlocalCorrelationResidual => nonlocalResidual
  | CorrelationStatus.correlationResidual => residual
  | CorrelationStatus.commonSourceFailure => sourceFailure
  | CorrelationStatus.routeFailure => routeFailure
  | CorrelationStatus.interfaceLeakage => interfaceLeakage
  | CorrelationStatus.contextCoupledSource => contextCoupled
  | CorrelationStatus.selectionConditionedCorrelation => selectionConditioned
  | CorrelationStatus.postselectedCorrelation => postselected
  | CorrelationStatus.presentationCorrelationArtifact => presentationArtifact
  | CorrelationStatus.protocolCorrelationArtifact => protocolArtifact
  | CorrelationStatus.topologicalCorrelation => topological
  | CorrelationStatus.anomalyMediatedCorrelation => anomalyMediated
  | CorrelationStatus.correlationDualityMismatch => dualityMismatch
  | CorrelationStatus.correlationOverread => overread

/-- A common-source quotient has the expected split-pair normal form. -/
theorem common_source_factorization_iff_no_obstruction {H S LA LB A B : Type}
    (source : H → S) (leftAccess : H → LA) (rightAccess : H → LB)
    (readoutA : H → A) (readoutB : H → B)
    (hsource :
      Function.Surjective
        (commonSourceCorrelationQuotient source leftAccess rightAccess)) :
    CommonSourceFactorization source leftAccess rightAccess readoutA readoutB ↔
      CommonSourceObstructionEmpty source leftAccess rightAccess readoutA readoutB :=
  descent_repair_normal_form
    (commonSourceCorrelationQuotient source leftAccess rightAccess)
    (fun h : H => h) (jointReadout readoutA readoutB) hsource

/-- Separate local response maps induce joint common-source factorization. -/
theorem separate_common_source_responses_factor {H S LA LB A B : Type}
    (source : H → S) (leftAccess : H → LA) (rightAccess : H → LB)
    (readoutA : H → A) (readoutB : H → B)
    (hresponses :
      CommonSourceResponseStructure source leftAccess rightAccess readoutA readoutB) :
    CommonSourceFactorization source leftAccess rightAccess readoutA readoutB := by
  rcases hresponses with ⟨responseA, responseB, hA, hB⟩
  refine ⟨fun data => (responseA data.1, responseB (data.1.1, data.2)), ?_⟩
  funext h
  exact Prod.ext (congrFun hA h) (congrFun hB h)

/-- A role-declared common-source explanation is obstruction-free plus the
separate local response record. -/
theorem common_source_explanation_iff {H S LA LB A B : Type} (source : H → S)
    (leftAccess : H → LA) (rightAccess : H → LB)
    (readoutA : H → A) (readoutB : H → B)
    (hsource :
      Function.Surjective
        (commonSourceCorrelationQuotient source leftAccess rightAccess)) :
    CommonSourceExplanation source leftAccess rightAccess readoutA readoutB ↔
      CommonSourceObstructionEmpty source leftAccess rightAccess readoutA readoutB ∧
        CommonSourceResponseStructure source leftAccess rightAccess readoutA readoutB := by
  constructor
  · intro h
    exact ⟨(common_source_factorization_iff_no_obstruction source leftAccess
      rightAccess readoutA readoutB hsource).1 h.1, h.2⟩
  · intro h
    exact ⟨(common_source_factorization_iff_no_obstruction source leftAccess
      rightAccess readoutA readoutB hsource).2 h.1, h.2⟩

/-- Interface-mediated correlation has the same descent/obstruction normal form
with a role-declared interface quotient. -/
theorem interface_mediated_iff_no_obstruction {H I LA LB A B : Type}
    (sharedInterface : H → I) (leftAccess : H → LA) (rightAccess : H → LB)
    (readoutA : H → A) (readoutB : H → B)
    (hinterface :
      Function.Surjective
        (interfaceCorrelationQuotient sharedInterface leftAccess rightAccess)) :
    InterfaceMediatedFactorization sharedInterface leftAccess rightAccess readoutA readoutB ↔
      InterfaceMediatedObstructionEmpty sharedInterface leftAccess rightAccess
        readoutA readoutB :=
  descent_repair_normal_form
    (interfaceCorrelationQuotient sharedInterface leftAccess rightAccess)
    (fun h : H => h) (jointReadout readoutA readoutB) hinterface

/-- Direct-route explanation is route admissibility and stability plus absence
of route-descent obstruction. -/
theorem direct_route_explanation_iff_no_obstruction
    {RouteContext RouteQuotient RouteTarget Residue : Type}
    (routeAdmissible routeStable : Prop)
    (routeQuotient : RouteContext → RouteQuotient)
    (routeTransport : RouteContext → RouteTarget)
    (targetResidue : RouteTarget → Residue)
    (hroute : Function.Surjective routeQuotient) :
    DirectRouteExplanation routeAdmissible routeStable routeQuotient routeTransport
        targetResidue ↔
      routeAdmissible ∧ routeStable ∧
        DirectRouteObstructionEmpty routeQuotient routeTransport targetResidue := by
  constructor
  · intro h
    exact ⟨h.1, h.2.1,
      (descent_repair_normal_form routeQuotient routeTransport targetResidue hroute).1
        h.2.2⟩
  · intro h
    exact ⟨h.1, h.2.1,
      (descent_repair_normal_form routeQuotient routeTransport targetResidue hroute).2
        h.2.2⟩

/-- Accepted explanations are exactly the declared source, route, or interface
records. -/
theorem accepted_correlation_explanation_iff (commonSource directRoute
    sharedInterface : Prop) :
    AcceptedCorrelationExplanation commonSource directRoute sharedInterface ↔
      commonSource ∨ directRoute ∨ sharedInterface := by
  constructor
  · intro h
    exact h
  · intro h
    exact h

/-- Residual classification is the complement of supplied explanatory roles
for a present dependency. -/
theorem correlation_residual_iff (correlationPresent commonSource directRoute
    sharedInterface : Prop) :
    CorrelationResidual correlationPresent commonSource directRoute sharedInterface ↔
      correlationPresent ∧ ¬ commonSource ∧ ¬ directRoute ∧ ¬ sharedInterface := by
  constructor
  · intro h
    exact h
  · intro h
    exact h

/-- Nonlocal residual classification is residual status plus failure of the
declared locality package. -/
theorem nonlocal_correlation_residual_iff (correlationPresent localityPackage
    commonSource directRoute sharedInterface : Prop) :
    NonlocalCorrelationResidual correlationPresent localityPackage commonSource
        directRoute sharedInterface ↔
      correlationPresent ∧ ¬ commonSource ∧ ¬ directRoute ∧ ¬ sharedInterface ∧
        ¬ localityPackage := by
  constructor
  · intro h
    rcases h with ⟨hresidual, hlocality⟩
    exact ⟨hresidual.1, hresidual.2.1, hresidual.2.2.1, hresidual.2.2.2,
      hlocality⟩
  · intro h
    exact ⟨⟨h.1, h.2.1, h.2.2.1, h.2.2.2.1⟩, h.2.2.2.2⟩

/--
Common-Source / Nonlocal Correlation Normal Form. Common-source,
direct-route, and interface-mediated explanations are role-declared quotient
descent records with corresponding split-pair obstructions; if none is
supplied, a present dependency is only a residual, and it becomes nonlocal only
relative to a failed locality package.
-/
theorem common_source_nonlocal_correlation
    {H S I LA LB A B RouteContext RouteQuotient RouteTarget Residue : Type}
    (source : H → S) (sharedInterface : H → I)
    (leftAccess : H → LA) (rightAccess : H → LB)
    (readoutA : H → A) (readoutB : H → B)
    (routeAdmissible routeStable correlationPresent localityPackage : Prop)
    (routeQuotient : RouteContext → RouteQuotient)
    (routeTransport : RouteContext → RouteTarget)
    (targetResidue : RouteTarget → Residue)
    (hsource :
      Function.Surjective
        (commonSourceCorrelationQuotient source leftAccess rightAccess))
    (hinterface :
      Function.Surjective
        (interfaceCorrelationQuotient sharedInterface leftAccess rightAccess))
    (hroute : Function.Surjective routeQuotient) :
    (CommonSourceFactorization source leftAccess rightAccess readoutA readoutB ↔
      CommonSourceObstructionEmpty source leftAccess rightAccess readoutA readoutB) ∧
      (CommonSourceExplanation source leftAccess rightAccess readoutA readoutB ↔
        CommonSourceObstructionEmpty source leftAccess rightAccess readoutA readoutB ∧
          CommonSourceResponseStructure source leftAccess rightAccess readoutA readoutB) ∧
        (InterfaceMediatedFactorization sharedInterface leftAccess rightAccess
            readoutA readoutB ↔
          InterfaceMediatedObstructionEmpty sharedInterface leftAccess rightAccess
            readoutA readoutB) ∧
          (DirectRouteExplanation routeAdmissible routeStable routeQuotient
              routeTransport targetResidue ↔
            routeAdmissible ∧ routeStable ∧
              DirectRouteObstructionEmpty routeQuotient routeTransport targetResidue) ∧
            (AcceptedCorrelationExplanation
                (CommonSourceExplanation source leftAccess rightAccess readoutA readoutB)
                (DirectRouteExplanation routeAdmissible routeStable routeQuotient
                  routeTransport targetResidue)
                (InterfaceMediatedFactorization sharedInterface leftAccess rightAccess
                  readoutA readoutB) ↔
              CommonSourceExplanation source leftAccess rightAccess readoutA readoutB ∨
                DirectRouteExplanation routeAdmissible routeStable routeQuotient
                  routeTransport targetResidue ∨
                  InterfaceMediatedFactorization sharedInterface leftAccess rightAccess
                    readoutA readoutB) ∧
              (CorrelationResidual correlationPresent
                  (CommonSourceExplanation source leftAccess rightAccess readoutA readoutB)
                  (DirectRouteExplanation routeAdmissible routeStable routeQuotient
                    routeTransport targetResidue)
                  (InterfaceMediatedFactorization sharedInterface leftAccess rightAccess
                    readoutA readoutB) ↔
                correlationPresent ∧
                  ¬ CommonSourceExplanation source leftAccess rightAccess readoutA readoutB ∧
                    ¬ DirectRouteExplanation routeAdmissible routeStable routeQuotient
                      routeTransport targetResidue ∧
                      ¬ InterfaceMediatedFactorization sharedInterface leftAccess
                        rightAccess readoutA readoutB) ∧
                (NonlocalCorrelationResidual correlationPresent localityPackage
                    (CommonSourceExplanation source leftAccess rightAccess readoutA readoutB)
                    (DirectRouteExplanation routeAdmissible routeStable routeQuotient
                      routeTransport targetResidue)
                    (InterfaceMediatedFactorization sharedInterface leftAccess rightAccess
                      readoutA readoutB) ↔
                  correlationPresent ∧
                    ¬ CommonSourceExplanation source leftAccess rightAccess readoutA
                      readoutB ∧
                      ¬ DirectRouteExplanation routeAdmissible routeStable routeQuotient
                        routeTransport targetResidue ∧
                        ¬ InterfaceMediatedFactorization sharedInterface leftAccess
                          rightAccess readoutA readoutB ∧
                          ¬ localityPackage) := by
  refine ⟨common_source_factorization_iff_no_obstruction source leftAccess
    rightAccess readoutA readoutB hsource, ?_⟩
  refine ⟨common_source_explanation_iff source leftAccess rightAccess readoutA readoutB
    hsource, ?_⟩
  refine ⟨interface_mediated_iff_no_obstruction sharedInterface leftAccess rightAccess
    readoutA readoutB hinterface, ?_⟩
  refine ⟨direct_route_explanation_iff_no_obstruction routeAdmissible routeStable
    routeQuotient routeTransport targetResidue hroute, ?_⟩
  refine ⟨accepted_correlation_explanation_iff _ _ _, ?_⟩
  refine ⟨correlation_residual_iff _ _ _ _, ?_⟩
  exact nonlocal_correlation_residual_iff _ _ _ _ _

end SixBirdsMetaMath.FoundationsIV.SelfReferenceLimits.CommonSourceNonlocal
