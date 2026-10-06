/-!
# Foundations VII identifiers and finite vocabularies

The aliases and enums in this file are transparent data.  Scientific claim
grade, evidence grade, operational status, and negative-result scope are
separate types; bookkeeping alone cannot identify them.
-/

namespace FoundationsVII

abbrev TheoryId := Nat
abbrev InterfaceId := Nat
abbrev ScopeId := Nat
abbrev EventId := Nat
abbrev TransitionId := Nat
abbrev SourceId := Nat
abbrev ResourceId := Nat
abbrev AuditId := Nat
abbrev ClaimId := Nat
abbrev DetectorId := Nat
abbrev CommitmentId := Nat
abbrev ObstructionId := Nat
abbrev ObserverId := Nat
abbrev RecordId := Nat
abbrev BridgeId := Nat
abbrev CertificateId := Nat
abbrev Timestamp := Nat
abbrev Cost := Nat

inductive SourceKind where
  | native
  | bridged
  | externalProvision
  | endogenous
  | observer
  | environment
  | mixed
  deriving Repr, DecidableEq, BEq, Inhabited

inductive AuditDisposition where
  | accepted
  | failed
  | revoked
  | refunded
  | withdrawn
  deriving Repr, DecidableEq, BEq, Inhabited

inductive BridgeDisposition where
  | proposed
  | accepted
  | failed
  | withdrawn
  deriving Repr, DecidableEq, BEq, Inhabited

/-- Soundness, executability, reachability, firing, and occurrence are not aliases. -/
inductive OperationalStatus where
  | sound
  | executable
  | reachable
  | fired
  | occurrent
  deriving Repr, DecidableEq, BEq, Inhabited

inductive InteractionStatus where
  | potentialContact
  | witnessedContact
  | compositeFormed
  | strictJoin
  | obstructed
  | certifiedNoninteraction
  deriving Repr, DecidableEq, BEq, Inhabited

inductive JoinObstructionKind where
  | source
  | compatibility
  | gluing
  | retention
  | novelty
  | budget
  | time
  | audit
  deriving Repr, DecidableEq, BEq, Inhabited

/-- Scientific statement grade.  Finite evidence has its own type below. -/
inductive ClaimGrade where
  | theorem
  | corollary
  | schema
  | calibration
  | conjecture
  | philosophy
  | nonclaim
  deriving Repr, DecidableEq, BEq, Inhabited

/-- Evidence provenance, separate from the grade of the scientific statement. -/
inductive EvidenceGrade where
  | none
  | executableExample
  | boundedSearch
  | exhaustiveFiniteLean
  | exhaustiveFiniteExternal
  | calibrationData
  | theoremBacked
  deriving Repr, DecidableEq, BEq, Inhabited

inductive ConditionRole where
  | necessary
  | sufficient
  | necessaryAndSufficient
  | neitherCertified
  deriving Repr, DecidableEq, BEq, Inhabited

inductive SpecificationKind where
  | normative
  | illustrativeExample
  | notApplicable
  deriving Repr, DecidableEq, BEq, Inhabited

inductive QuantifierGrade where
  | oneInstance
  | finiteCarrier
  | declaredFamily
  | boundedHorizon
  | universalUnderHypotheses
  deriving Repr, DecidableEq, BEq, Inhabited

inductive NegativeEvidenceGrade where
  | pointNull
  | boundedSearch
  | exhaustiveClosedFinite
  | theoremImpossibility
  deriving Repr, DecidableEq, BEq, Inhabited

inductive NegativeScope where
  | oneInstance
  | boundedFamily
  | closedFiniteFamily
  | unrestrictedUnderHypotheses
  deriving Repr, DecidableEq, BEq, Inhabited

/-! Explicit finite enumerations used by fixtures and structural proofs. -/

def allSourceKinds : List SourceKind :=
  [.native, .bridged, .externalProvision, .endogenous, .observer, .environment, .mixed]

def allAuditDispositions : List AuditDisposition :=
  [.accepted, .failed, .revoked, .refunded, .withdrawn]

def allBridgeDispositions : List BridgeDisposition :=
  [.proposed, .accepted, .failed, .withdrawn]

def allOperationalStatuses : List OperationalStatus :=
  [.sound, .executable, .reachable, .fired, .occurrent]

def allInteractionStatuses : List InteractionStatus :=
  [.potentialContact, .witnessedContact, .compositeFormed, .strictJoin,
   .obstructed, .certifiedNoninteraction]

def allClaimGrades : List ClaimGrade :=
  [.theorem, .corollary, .schema, .calibration, .conjecture, .philosophy, .nonclaim]

def allEvidenceGrades : List EvidenceGrade :=
  [.none, .executableExample, .boundedSearch, .exhaustiveFiniteLean,
   .exhaustiveFiniteExternal, .calibrationData, .theoremBacked]

def allNegativeEvidenceGrades : List NegativeEvidenceGrade :=
  [.pointNull, .boundedSearch, .exhaustiveClosedFinite, .theoremImpossibility]

def allNegativeScopes : List NegativeScope :=
  [.oneInstance, .boundedFamily, .closedFiniteFamily, .unrestrictedUnderHypotheses]

theorem sourceKind_mem_all (value : SourceKind) : value ∈ allSourceKinds := by
  cases value <;> simp [allSourceKinds]

theorem auditDisposition_mem_all (value : AuditDisposition) :
    value ∈ allAuditDispositions := by
  cases value <;> simp [allAuditDispositions]

theorem bridgeDisposition_mem_all (value : BridgeDisposition) :
    value ∈ allBridgeDispositions := by
  cases value <;> simp [allBridgeDispositions]

theorem operationalStatus_mem_all (value : OperationalStatus) :
    value ∈ allOperationalStatuses := by
  cases value <;> simp [allOperationalStatuses]

theorem interactionStatus_mem_all (value : InteractionStatus) :
    value ∈ allInteractionStatuses := by
  cases value <;> simp [allInteractionStatuses]

theorem claimGrade_mem_all (value : ClaimGrade) : value ∈ allClaimGrades := by
  cases value <;> simp [allClaimGrades]

theorem evidenceGrade_mem_all (value : EvidenceGrade) : value ∈ allEvidenceGrades := by
  cases value <;> simp [allEvidenceGrades]

theorem negativeEvidenceGrade_mem_all (value : NegativeEvidenceGrade) :
    value ∈ allNegativeEvidenceGrades := by
  cases value <;> simp [allNegativeEvidenceGrades]

theorem negativeScope_mem_all (value : NegativeScope) : value ∈ allNegativeScopes := by
  cases value <;> simp [allNegativeScopes]

theorem operational_statuses_pairwise_distinct :
    allOperationalStatuses.eraseDups.length = 5 := by decide

theorem sound_ne_executable :
    OperationalStatus.sound ≠ OperationalStatus.executable := by decide

theorem sound_ne_reachable :
    OperationalStatus.sound ≠ OperationalStatus.reachable := by decide

theorem sound_ne_fired :
    OperationalStatus.sound ≠ OperationalStatus.fired := by decide

theorem sound_ne_occurrent :
    OperationalStatus.sound ≠ OperationalStatus.occurrent := by decide

theorem executable_ne_reachable :
    OperationalStatus.executable ≠ OperationalStatus.reachable := by decide

theorem executable_ne_fired :
    OperationalStatus.executable ≠ OperationalStatus.fired := by decide

theorem executable_ne_occurrent :
    OperationalStatus.executable ≠ OperationalStatus.occurrent := by decide

theorem reachable_ne_fired :
    OperationalStatus.reachable ≠ OperationalStatus.fired := by decide

theorem reachable_ne_occurrent :
    OperationalStatus.reachable ≠ OperationalStatus.occurrent := by decide

theorem fired_ne_occurrent :
    OperationalStatus.fired ≠ OperationalStatus.occurrent := by decide

theorem witnessedContact_ne_strictJoin :
    InteractionStatus.witnessedContact ≠ InteractionStatus.strictJoin := by decide

theorem obstructed_ne_certifiedNoninteraction :
    InteractionStatus.obstructed ≠ InteractionStatus.certifiedNoninteraction := by decide

end FoundationsVII
