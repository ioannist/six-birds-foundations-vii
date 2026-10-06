import FoundationsVII.Core.Grades
import FoundationsVII.Core.Join
import FoundationsVII.Core.Enablement
import FoundationsVII.Core.Reachability
import FoundationsVII.Core.Observer

/-!
# Phase-1 protocol assets

This module supplies terminal structural assets for VII-C020, VII-C023, and
VII-C024, plus the detector contract type used by VII-C025.  They are protocol
and bookkeeping results, not later admission, join, enablement, or dynamics
laws.
-/

namespace FoundationsVII

/-! ## VII-C020 — bridge and semantic-withdrawal discipline -/

structure CitationRecord where
  citationKey : String
  sourceLocation : String
  paraphrase : String
  deriving Repr, DecidableEq, BEq

structure BridgeContract where
  bridgeId : BridgeId
  sourceDeclaration : String
  targetDeclaration : String
  sourceType : String
  targetType : String
  sourceMap : String
  targetMap : String
  preservedHypotheses : List String
  addedHypotheses : List String
  lostHypotheses : List String
  trustDependencies : List String
  nonclaims : List String
  disposition : BridgeDisposition
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace BridgeContract

/--
A bridge record is structurally complete when its endpoints and maps are named,
its limitations are nonempty, and it has an audit.  The four hypothesis/trust
lists are allowed to be empty: in a typed record, `[]` is the explicit claim
that the corresponding class is empty, not an omitted field.
-/
def WellFormed (bridge : BridgeContract) : Prop :=
  bridge.sourceDeclaration ≠ "" ∧
  bridge.targetDeclaration ≠ "" ∧
  bridge.sourceType ≠ "" ∧
  bridge.targetType ≠ "" ∧
  bridge.sourceMap ≠ "" ∧
  bridge.targetMap ≠ "" ∧
  bridge.nonclaims ≠ [] ∧
  bridge.audit.entries ≠ []

instance (bridge : BridgeContract) : Decidable (WellFormed bridge) := by
  unfold WellFormed
  infer_instance


theorem constructed_wellFormed (bridge : BridgeContract)
    (hSourceDeclaration : bridge.sourceDeclaration ≠ "")
    (hTargetDeclaration : bridge.targetDeclaration ≠ "")
    (hSourceType : bridge.sourceType ≠ "")
    (hTargetType : bridge.targetType ≠ "")
    (hSourceMap : bridge.sourceMap ≠ "")
    (hTargetMap : bridge.targetMap ≠ "")
    (hNonclaims : bridge.nonclaims ≠ [])
    (hAudit : bridge.audit.entries ≠ []) : WellFormed bridge := by
  exact ⟨hSourceDeclaration, hTargetDeclaration, hSourceType, hTargetType,
    hSourceMap, hTargetMap, hNonclaims, hAudit⟩

end BridgeContract

inductive TransportAuthorization where
  | citationOnly (citation : CitationRecord)
  | certifiedBridge (bridge : BridgeContract)
  deriving Repr, DecidableEq, BEq

namespace TransportAuthorization

def bridgeWellFormed (bridge : BridgeContract) : Bool :=
  decide (BridgeContract.WellFormed bridge)

def licensed : TransportAuthorization → Bool
  | .citationOnly _ => false
  | .certifiedBridge bridge =>
      (bridge.disposition == BridgeDisposition.accepted) &&
        decide (BridgeContract.WellFormed bridge)

theorem citation_only_is_not_licensed (citation : CitationRecord) :
    licensed (.citationOnly citation) = false := rfl

theorem accepted_wellFormed_bridge_is_licensed (bridge : BridgeContract)
    (hDisposition : bridge.disposition = BridgeDisposition.accepted)
    (hWellFormed : BridgeContract.WellFormed bridge) :
    licensed (.certifiedBridge bridge) = true := by
  have hBeq : (bridge.disposition == BridgeDisposition.accepted) = true := by
    rw [hDisposition]
    decide
  simp [licensed, hBeq, hWellFormed]

/-- Compatibility alias: “complete” means exactly `BridgeContract.WellFormed`. -/
theorem accepted_complete_bridge_is_licensed (bridge : BridgeContract)
    (hDisposition : bridge.disposition = BridgeDisposition.accepted)
    (hComplete : BridgeContract.WellFormed bridge) :
    licensed (.certifiedBridge bridge) = true :=
  accepted_wellFormed_bridge_is_licensed bridge hDisposition hComplete

/-- Compatibility alias retained for downstream Phase-1 registries. -/
theorem accepted_bridge_is_licensed (bridge : BridgeContract)
    (hDisposition : bridge.disposition = BridgeDisposition.accepted)
    (hComplete : BridgeContract.WellFormed bridge) :
    licensed (.certifiedBridge bridge) = true :=
  accepted_wellFormed_bridge_is_licensed bridge hDisposition hComplete

theorem incomplete_bridge_is_not_licensed (bridge : BridgeContract)
    (hIncomplete : ¬ BridgeContract.WellFormed bridge) :
    licensed (.certifiedBridge bridge) = false := by
  simp [licensed, hIncomplete]

theorem failed_bridge_is_not_licensed (bridge : BridgeContract)
    (h : bridge.disposition = BridgeDisposition.failed) :
    licensed (.certifiedBridge bridge) = false := by
  have hBeq : (bridge.disposition == BridgeDisposition.accepted) = false := by
    rw [h]
    decide
  simp [licensed, hBeq]

theorem withdrawn_bridge_is_not_licensed (bridge : BridgeContract)
    (h : bridge.disposition = BridgeDisposition.withdrawn) :
    licensed (.certifiedBridge bridge) = false := by
  have hBeq : (bridge.disposition == BridgeDisposition.accepted) = false := by
    rw [h]
    decide
  simp [licensed, hBeq]

end TransportAuthorization

structure BridgeLedgerEntry where
  bridge : BridgeContract
  downstreamClaimIds : List ClaimId
  paraphraseSweepComplete : Bool
  dependencySweepComplete : Bool
  deriving Repr, DecidableEq, BEq

namespace BridgeLedgerEntry

def WellFormed (entry : BridgeLedgerEntry) : Prop :=
  BridgeContract.WellFormed entry.bridge ∧
  (entry.bridge.disposition = BridgeDisposition.withdrawn →
    entry.paraphraseSweepComplete = true ∧
    entry.dependencySweepComplete = true)

instance (entry : BridgeLedgerEntry) : Decidable (WellFormed entry) := by
  unfold WellFormed
  infer_instance

end BridgeLedgerEntry

structure BridgeLedger where
  entries : List BridgeLedgerEntry
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace BridgeLedger

def append (ledger : BridgeLedger) (entry : BridgeLedgerEntry)
    (auditEntry : AuditEntry) : BridgeLedger :=
  { entries := ledger.entries ++ [entry]
    audit := ledger.audit.append auditEntry }

def EntryExtends (old newer : BridgeLedger) : Prop :=
  ∃ suffix : List BridgeLedgerEntry, newer.entries = old.entries ++ suffix

def Extends (old newer : BridgeLedger) : Prop :=
  EntryExtends old newer ∧ AuditRecord.Extends old.audit newer.audit

theorem append_extends (ledger : BridgeLedger) (entry : BridgeLedgerEntry)
    (auditEntry : AuditEntry) : Extends ledger (append ledger entry auditEntry) := by
  exact ⟨⟨[entry], rfl⟩, AuditRecord.append_extends ledger.audit auditEntry⟩

theorem mem_of_extends {old newer : BridgeLedger}
    (h : Extends old newer) {entry : BridgeLedgerEntry}
    (hmem : entry ∈ old.entries) : entry ∈ newer.entries := by
  rcases h.1 with ⟨suffix, hsuffix⟩
  rw [hsuffix]
  simp only [List.mem_append]
  exact Or.inl hmem

theorem audit_mem_of_extends {old newer : BridgeLedger}
    (h : Extends old newer) {entry : AuditEntry}
    (hmem : entry ∈ old.audit.entries) : entry ∈ newer.audit.entries :=
  AuditRecord.mem_of_extends h.2 hmem

theorem failed_bridge_not_silently_deleted {old newer : BridgeLedger}
    (h : Extends old newer) {entry : BridgeLedgerEntry}
    (hmem : entry ∈ old.entries)
    (_ : entry.bridge.disposition = BridgeDisposition.failed) :
    entry ∈ newer.entries := mem_of_extends h hmem

theorem withdrawn_bridge_not_silently_deleted {old newer : BridgeLedger}
    (h : Extends old newer) {entry : BridgeLedgerEntry}
    (hmem : entry ∈ old.entries)
    (_ : entry.bridge.disposition = BridgeDisposition.withdrawn) :
    entry ∈ newer.entries := mem_of_extends h hmem

theorem withdrawn_entry_requires_sweeps {entry : BridgeLedgerEntry}
    (hWellFormed : BridgeLedgerEntry.WellFormed entry)
    (hWithdrawn : entry.bridge.disposition = BridgeDisposition.withdrawn) :
    entry.paraphraseSweepComplete = true ∧
      entry.dependencySweepComplete = true :=
  hWellFormed.2 hWithdrawn

end BridgeLedger

/-! ## VII-C023 — negative-result quantifier discipline -/

structure NegativeEvidenceRecord where
  recordId : RecordId
  grade : NegativeEvidenceGrade
  scope : NegativeScope
  carrierDescription : String
  familyDescription : String
  familyClosed : Bool
  searchBound : Option Nat
  detectorPowerDescription : String
  escapeRoutes : List String
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace NegativeEvidenceRecord

def scopeAllows (declared requested : NegativeScope) : Bool :=
  match declared, requested with
  | .oneInstance, .oneInstance => true
  | .boundedFamily, .oneInstance => true
  | .boundedFamily, .boundedFamily => true
  | .closedFiniteFamily, .oneInstance => true
  | .closedFiniteFamily, .boundedFamily => true
  | .closedFiniteFamily, .closedFiniteFamily => true
  | .unrestrictedUnderHypotheses, _ => true
  | _, _ => false

def gradeAllows (record : NegativeEvidenceRecord)
    (requested : NegativeScope) : Bool :=
  match record.grade, requested with
  | .pointNull, .oneInstance => true
  | .boundedSearch, .oneInstance => true
  | .boundedSearch, .boundedFamily => true
  | .exhaustiveClosedFinite, .oneInstance => record.familyClosed
  | .exhaustiveClosedFinite, .boundedFamily => record.familyClosed
  | .exhaustiveClosedFinite, .closedFiniteFamily => record.familyClosed
  | .theoremImpossibility, _ => true
  | _, _ => false

def licenses (record : NegativeEvidenceRecord)
    (requestedScope : NegativeScope) : Bool :=
  scopeAllows record.scope requestedScope && gradeAllows record requestedScope

def WellFormed (record : NegativeEvidenceRecord) : Prop :=
  record.carrierDescription ≠ "" ∧
  record.familyDescription ≠ "" ∧
  record.detectorPowerDescription ≠ "" ∧
  record.escapeRoutes ≠ [] ∧
  (record.grade = NegativeEvidenceGrade.exhaustiveClosedFinite →
    record.familyClosed = true) ∧
  record.audit.entries ≠ []

instance (record : NegativeEvidenceRecord) : Decidable (WellFormed record) := by
  unfold WellFormed
  infer_instance

theorem point_null_does_not_license_unrestricted
    (record : NegativeEvidenceRecord)
    (h : record.grade = NegativeEvidenceGrade.pointNull) :
    record.licenses NegativeScope.unrestrictedUnderHypotheses = false := by
  cases hScope : record.scope <;> simp [licenses, scopeAllows, gradeAllows, h, hScope]

theorem bounded_search_does_not_license_unrestricted
    (record : NegativeEvidenceRecord)
    (h : record.grade = NegativeEvidenceGrade.boundedSearch) :
    record.licenses NegativeScope.unrestrictedUnderHypotheses = false := by
  cases hScope : record.scope <;> simp [licenses, scopeAllows, gradeAllows, h, hScope]

theorem exhaustive_closed_finite_licenses_its_closed_family
    (record : NegativeEvidenceRecord)
    (hGrade : record.grade = NegativeEvidenceGrade.exhaustiveClosedFinite)
    (hScope : record.scope = NegativeScope.closedFiniteFamily)
    (hClosed : record.familyClosed = true) :
    record.licenses NegativeScope.closedFiniteFamily = true := by
  simp [licenses, scopeAllows, gradeAllows, hGrade, hScope, hClosed]

theorem exhaustive_finite_does_not_license_unrestricted
    (record : NegativeEvidenceRecord)
    (h : record.grade = NegativeEvidenceGrade.exhaustiveClosedFinite) :
    record.licenses NegativeScope.unrestrictedUnderHypotheses = false := by
  cases hScope : record.scope <;> simp [licenses, scopeAllows, gradeAllows, h, hScope]

theorem theorem_impossibility_licenses_under_unrestricted_declared_scope
    (record : NegativeEvidenceRecord)
    (hGrade : record.grade = NegativeEvidenceGrade.theoremImpossibility)
    (hScope : record.scope = NegativeScope.unrestrictedUnderHypotheses)
    (requested : NegativeScope) :
    record.licenses requested = true := by
  cases requested <;> simp [licenses, scopeAllows, gradeAllows, hGrade, hScope]

end NegativeEvidenceRecord

/-! ## VII-C024 — claim-grade and normative-specification discipline -/

structure ScienceAssetRecord where
  assetId : String
  claim : GradedClaim
  evidence : Option FiniteEvidenceEnvelope
  formalDeclaration : Option String
  specification : Option NormativeSpecification
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace ScienceAssetRecord

def GradeFaithful (asset : ScienceAssetRecord) : Prop :=
  ((asset.claim.grade = ClaimGrade.theorem ∨
      asset.claim.grade = ClaimGrade.corollary) →
    asset.formalDeclaration.isSome = true) ∧
  (∀ envelope, asset.evidence = some envelope →
    envelope.grade = EvidenceGrade.exhaustiveFiniteExternal →
    asset.claim.grade ≠ ClaimGrade.theorem ∧
      asset.claim.grade ≠ ClaimGrade.corollary) ∧
  (∀ envelope, asset.evidence = some envelope →
    envelope.grade = EvidenceGrade.exhaustiveFiniteLean →
    asset.claim.grade ≠ ClaimGrade.theorem ∧
      asset.claim.grade ≠ ClaimGrade.corollary) ∧
  (asset.claim.specificationKind = SpecificationKind.normative →
    asset.specification.isSome = true) ∧
  asset.audit.entries ≠ []

theorem constructed_gradeFaithful (asset : ScienceAssetRecord)
    (hTheorem : (asset.claim.grade = ClaimGrade.theorem ∨
      asset.claim.grade = ClaimGrade.corollary) →
      asset.formalDeclaration.isSome = true)
    (hExternal : ∀ envelope, asset.evidence = some envelope →
      envelope.grade = EvidenceGrade.exhaustiveFiniteExternal →
      asset.claim.grade ≠ ClaimGrade.theorem ∧
        asset.claim.grade ≠ ClaimGrade.corollary)
    (hLeanFinite : ∀ envelope, asset.evidence = some envelope →
      envelope.grade = EvidenceGrade.exhaustiveFiniteLean →
      asset.claim.grade ≠ ClaimGrade.theorem ∧
        asset.claim.grade ≠ ClaimGrade.corollary)
    (hNormative : asset.claim.specificationKind = SpecificationKind.normative →
      asset.specification.isSome = true)
    (hAudit : asset.audit.entries ≠ []) : GradeFaithful asset := by
  exact ⟨hTheorem, hExternal, hLeanFinite, hNormative, hAudit⟩

theorem theorem_grade_requires_formal_declaration {asset : ScienceAssetRecord}
    (hFaithful : GradeFaithful asset)
    (hGrade : asset.claim.grade = ClaimGrade.theorem) :
    asset.formalDeclaration.isSome = true :=
  hFaithful.1 (Or.inl hGrade)

theorem corollary_grade_requires_formal_declaration {asset : ScienceAssetRecord}
    (hFaithful : GradeFaithful asset)
    (hGrade : asset.claim.grade = ClaimGrade.corollary) :
    asset.formalDeclaration.isSome = true :=
  hFaithful.1 (Or.inr hGrade)

theorem external_finite_evidence_does_not_upgrade_to_theorem
    {asset : ScienceAssetRecord} {envelope : FiniteEvidenceEnvelope}
    (hFaithful : GradeFaithful asset)
    (hEnvelope : asset.evidence = some envelope)
    (hExternal : envelope.grade = EvidenceGrade.exhaustiveFiniteExternal) :
    asset.claim.grade ≠ ClaimGrade.theorem :=
  (hFaithful.2.1 envelope hEnvelope hExternal).1

theorem external_finite_evidence_does_not_upgrade_to_corollary
    {asset : ScienceAssetRecord} {envelope : FiniteEvidenceEnvelope}
    (hFaithful : GradeFaithful asset)
    (hEnvelope : asset.evidence = some envelope)
    (hExternal : envelope.grade = EvidenceGrade.exhaustiveFiniteExternal) :
    asset.claim.grade ≠ ClaimGrade.corollary :=
  (hFaithful.2.1 envelope hEnvelope hExternal).2

theorem lean_finite_evidence_does_not_upgrade_to_theorem
    {asset : ScienceAssetRecord} {envelope : FiniteEvidenceEnvelope}
    (hFaithful : GradeFaithful asset)
    (hEnvelope : asset.evidence = some envelope)
    (hFinite : envelope.grade = EvidenceGrade.exhaustiveFiniteLean) :
    asset.claim.grade ≠ ClaimGrade.theorem :=
  (hFaithful.2.2.1 envelope hEnvelope hFinite).1

theorem lean_finite_evidence_does_not_upgrade_to_corollary
    {asset : ScienceAssetRecord} {envelope : FiniteEvidenceEnvelope}
    (hFaithful : GradeFaithful asset)
    (hEnvelope : asset.evidence = some envelope)
    (hFinite : envelope.grade = EvidenceGrade.exhaustiveFiniteLean) :
    asset.claim.grade ≠ ClaimGrade.corollary :=
  (hFaithful.2.2.1 envelope hEnvelope hFinite).2

theorem normative_specification_requires_payload {asset : ScienceAssetRecord}
    (hFaithful : GradeFaithful asset)
    (hNormative : asset.claim.specificationKind = SpecificationKind.normative) :
    asset.specification.isSome = true :=
  hFaithful.2.2.2.1 hNormative

end ScienceAssetRecord

/-! ## VII-C025 — Two-Theory World detector contract -/

structure DetectorContract where
  detectorId : DetectorId
  signalDescription : String
  nullDescription : String
  falsifierDescription : String
  signalCaseIds : List String
  nullCaseIds : List String
  falsifierCaseIds : List String
  sameSourceControls : List String
  noContactControls : List String
  schedulingControls : List String
  relabelingControls : List String
  falsePositiveCost : Cost
  falseNegativeCost : Cost
  frozenScenarioIds : List String
  frozenCountermodelIds : List String
  evidenceAudit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace DetectorContract

def frozenCaseIds (contract : DetectorContract) : List String :=
  contract.frozenScenarioIds ++ contract.frozenCountermodelIds

def listedInFrozen (contract : DetectorContract) (caseIds : List String) : Bool :=
  caseIds.all (fun caseId => (frozenCaseIds contract).contains caseId)

def WellFormed (contract : DetectorContract) : Prop :=
  contract.signalDescription ≠ "" ∧
  contract.nullDescription ≠ "" ∧
  contract.falsifierDescription ≠ "" ∧
  contract.signalCaseIds ≠ [] ∧
  contract.nullCaseIds ≠ [] ∧
  contract.falsifierCaseIds ≠ [] ∧
  contract.sameSourceControls ≠ [] ∧
  contract.noContactControls ≠ [] ∧
  contract.schedulingControls ≠ [] ∧
  contract.relabelingControls ≠ [] ∧
  contract.frozenScenarioIds ≠ [] ∧
  contract.frozenCountermodelIds ≠ [] ∧
  contract.falseNegativeCost < contract.falsePositiveCost ∧
  listedInFrozen contract contract.signalCaseIds = true ∧
  listedInFrozen contract contract.nullCaseIds = true ∧
  listedInFrozen contract contract.falsifierCaseIds = true ∧
  listedInFrozen contract contract.sameSourceControls = true ∧
  listedInFrozen contract contract.noContactControls = true ∧
  listedInFrozen contract contract.schedulingControls = true ∧
  listedInFrozen contract contract.relabelingControls = true ∧
  contract.evidenceAudit.entries ≠ []

instance (contract : DetectorContract) : Decidable (WellFormed contract) := by
  unfold WellFormed
  infer_instance

def FrozenComplete (contract : DetectorContract)
    (scenarioCount countermodelCount : Nat) : Prop :=
  contract.frozenScenarioIds.length = scenarioCount ∧
  contract.frozenCountermodelIds.length = countermodelCount ∧
  contract.frozenScenarioIds.eraseDups.length = scenarioCount ∧
  contract.frozenCountermodelIds.eraseDups.length = countermodelCount

instance (contract : DetectorContract) (scenarioCount countermodelCount : Nat) :
    Decidable (FrozenComplete contract scenarioCount countermodelCount) := by
  unfold FrozenComplete
  infer_instance

end DetectorContract

end FoundationsVII
