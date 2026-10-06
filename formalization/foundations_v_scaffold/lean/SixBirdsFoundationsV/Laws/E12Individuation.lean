import SixBirdsFoundationsV.Definitional.ESystem
import SixBirdsFoundationsV.Definitional.ProbeEconomy
import SixBirdsFoundationsV.Laws.E3SelfMaintainingReclosure
import SixBirdsFoundationsV.Laws.E6E9PricedAccess

namespace SixBirdsFoundationsV

/-!
E12 individuation setup.

This setup layer mechanizes the boundary-discovery substrate from the accepted
E12 six-field normal form (`formalization/notes/examples/E12.md`).  It reuses
D3/D4 carried records and repair steps, D6/E6+E9 probe-budget witnesses, and
E3's closure-apparatus maintenance machinery directly.  The six-way status
apparatus and E12 theorems are intentionally left to later mechanization
subsections.
-/

/-- A candidate individual is a predicate on the existing D4 carrier. -/
def Subcarrier
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    (T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData) :
    Type _ :=
  T.Z -> Prop

/--
Certified declared finite family of candidate subcarriers.  The list is the
actual range searched by E12 status predicates; arbitrary predicates outside
this declared family are not silently eligible for maximality or federation.
-/
structure Candidates
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    (T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData) where
  members : List (Subcarrier T)
  declaredCandidateFamily : Prop
  declared : declaredCandidateFamily

/--
Certified attribution of ledger entries to subcarrier-local repair or budget
activity.  E12 uses this as host input, then checks carriedness through D4's
ledger and record policy.
-/
structure GeneratedByActivityIn
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  holds : Subcarrier S.T -> LedgerEntry -> Prop

def EntryClosedOn
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (recordPolicyI : CarriedRecordPolicy S.T LedgerEntry)
    (_I : Subcarrier S.T) (entry : LedgerEntry) : Prop :=
  entry ∈ S.Lambda_S.ledgerEntries ∧
    ∃ n : Nat,
      CarriedRecordAt recordPolicyI entry n
        FineSourceTag.committed_state true true

def RecordClosedOn
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (recordPolicyI : CarriedRecordPolicy S.T LedgerEntry)
    (generatedBy : GeneratedByActivityIn S)
    (I : Subcarrier S.T) : Prop :=
  (∃ entry : LedgerEntry, generatedBy.holds I entry) ∧
    ∀ entry : LedgerEntry,
      generatedBy.holds I entry -> EntryClosedOn S recordPolicyI I entry

structure RepairAttributedTo
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (sourceStatePolicy : CarriedRecordPolicy S.T S.T.Z)
    (I : Subcarrier S.T) where
  defectRecord : DefectRecord
  auditRecord : AuditRecord
  sourceState : S.T.Z
  targetState : S.T.Z
  sourceInI : I sourceState
  isRepairStep :
    ESystem.RepairStep S sourceState targetState defectRecord auditRecord
  sourceOccurrenceN0 : Nat
  sourceOccurrenceTag : FineSourceTag
  sourceOccurrenceGeneratedByS : Bool
  sourceOccurrenceInScope : Bool
  sourceOccurrenceTagAdmissible :
    sourceOccurrenceTag = FineSourceTag.committed_state ∨
      sourceOccurrenceTag = FineSourceTag.audited_cell_records
  sourceOccurrenceGeneratedBySTrue :
    sourceOccurrenceGeneratedByS = true
  sourceOccurrenceInScopeTrue : sourceOccurrenceInScope = true
  sourceOccurrenceCertified :
    CarriedRecordAt sourceStatePolicy sourceState sourceOccurrenceN0
      sourceOccurrenceTag sourceOccurrenceGeneratedByS sourceOccurrenceInScope

def RepairClosedOn
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (sourceStatePolicy : CarriedRecordPolicy S.T S.T.Z)
    (I : Subcarrier S.T) : Prop :=
  (∃ _r : RepairAttributedTo S sourceStatePolicy I, True) ∧
    ∀ r : RepairAttributedTo S sourceStatePolicy I, I r.targetState

def AttributedToI
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    {Probe : Type z} {XiFamily : Type z'}
    (accessPolicyRecord :
      CarriedRecordPolicy S.T (AccessPolicy Probe XiFamily))
    (I : Subcarrier S.T)
    {economy : ProbeEconomy S Probe XiFamily}
    {move : ProbeMove Probe XiFamily}
    (w : ExposureBudgetWitness economy move) : Prop :=
  w.budgetEntry ∈ S.Lambda_S.ledgerEntries ∧
    ∃ policy : AccessPolicy Probe XiFamily,
      ∃ accessMove : AccessMove Probe XiFamily,
        ∃ n0 : Nat, ∃ sourceTag : FineSourceTag,
          ∃ generatedByS : Bool, ∃ inScope : Bool,
            PolicyCarriedAt accessPolicyRecord policy n0 sourceTag
              generatedByS inScope ∧
            (sourceTag = FineSourceTag.committed_state ∨
              sourceTag = FineSourceTag.audited_cell_records) ∧
            generatedByS = true ∧
            inScope = true ∧
            I (S.T.tau n0) ∧
            policy.selects accessMove ∧
            AccessMove.toProbeMove accessMove = move

def BudgetClosedOn
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    {Probe : Type z} {XiFamily : Type z'}
    (recordPolicyI : CarriedRecordPolicy S.T LedgerEntry)
    (accessPolicyRecord :
      CarriedRecordPolicy S.T (AccessPolicy Probe XiFamily))
    (I : Subcarrier S.T) : Prop :=
  (∃ (economy : ProbeEconomy S Probe XiFamily)
      (move : ProbeMove Probe XiFamily)
      (w : ExposureBudgetWitness economy move),
      BudgetFeasible w ∧ AttributedToI S accessPolicyRecord I w) ∧
    ∀ (economy : ProbeEconomy S Probe XiFamily)
      (move : ProbeMove Probe XiFamily)
      (w : ExposureBudgetWitness economy move),
      BudgetFeasible w ->
        AttributedToI S accessPolicyRecord I w ->
          EntryClosedOn S recordPolicyI I w.budgetEntry

structure InterfaceState
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    (I : Subcarrier T) where
  state : T.Z

structure BoundaryQuotient where
  quotientId : Nat
  deriving DecidableEq, Repr

/--
Certified declared family of viability probes.  The Agents-paper viability
kernel and probe construction are not derived locally in E12.
-/
structure DeclaredViabilityProbes
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    (T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData) where
  Probe : Type z
  probes : List Probe
  declaredProbeFamily : Prop
  declared : declaredProbeFamily

structure InstitutionalBoundaryCandidate
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    (I : Subcarrier T) where
  interfaceQuotient : InterfaceState I -> BoundaryQuotient

/--
Certified F7 sufficiency-closure interface for the declared viability probes.
The host supplies which quotients all declared probes descend through.
-/
structure SufficiencyClosureCertified
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    (viabilityProbes : DeclaredViabilityProbes T) where
  holds : {I : Subcarrier T} -> {Q : Type} ->
    (InterfaceState I -> Q) -> Prop

/--
Certified F10 coarsest-quotient interface.  The direction is load-bearing:
`q` must factor through every other sufficient quotient `π`, so `q = f ∘ π`.
-/
structure CoarsestQuotientCertified
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {I : Subcarrier T}
    (viabilityProbes : DeclaredViabilityProbes T)
    (sufficiency : SufficiencyClosureCertified viabilityProbes)
    (q : InterfaceState I -> BoundaryQuotient) where
  holds : Prop
  certified : holds
  factorizes :
    ∀ (Q' : Type) (π : InterfaceState I -> Q'),
      sufficiency.holds π ->
        ∃ f : Q' -> BoundaryQuotient, q = fun x => f (π x)

def ViabilitySufficientBoundary
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData}
    {I : Subcarrier T}
    (viabilityProbes : DeclaredViabilityProbes T)
    (sufficiency : SufficiencyClosureCertified viabilityProbes)
    (B : InstitutionalBoundaryCandidate I)
    (coarsest :
      CoarsestQuotientCertified viabilityProbes sufficiency
        B.interfaceQuotient) : Prop :=
  sufficiency.holds B.interfaceQuotient ∧ coarsest.holds

/--
Certified bridge from an institutional boundary candidate to the E3 closure
apparatus that maintains it.
-/
structure BoundaryApparatusFor
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord) where
  holds :
    {I : Subcarrier S.T} ->
      InstitutionalBoundaryCandidate I -> ClosureApparatus S -> Prop

def SelfMaintainedBoundary
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (boundaryApparatus : BoundaryApparatusFor S)
    (I : Subcarrier S.T) (B : InstitutionalBoundaryCandidate I) : Prop :=
  ∃ (t : Nat) (app_t app_tplus1 : ClosureApparatus S)
    (m : ClosureMaintenanceOperator S)
    (record : MaintenanceReinstatementRecord S),
    boundaryApparatus.holds (I := I) B app_t ∧
      MaintenanceReinstatementFor S H appPolicy maintenancePolicy
        reinstatementPolicy t app_t app_tplus1 m record ∧
      I record.sourceState

def Individuates
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    {Probe : Type z'''''} {XiFamily : Type z''''''}
    (recordPolicyI : CarriedRecordPolicy S.T LedgerEntry)
    (generatedBy : GeneratedByActivityIn S)
    (sourceStatePolicy : CarriedRecordPolicy S.T S.T.Z)
    (accessPolicyRecord :
      CarriedRecordPolicy S.T (AccessPolicy Probe XiFamily))
    (viabilityProbes : DeclaredViabilityProbes S.T)
    (sufficiency : SufficiencyClosureCertified viabilityProbes)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (boundaryApparatus : BoundaryApparatusFor S)
    (I : Subcarrier S.T) : Prop :=
  RepairClosedOn S sourceStatePolicy I ∧
    BudgetClosedOn S recordPolicyI accessPolicyRecord I ∧
    RecordClosedOn S recordPolicyI generatedBy I ∧
    ∃ B : InstitutionalBoundaryCandidate I,
      ∃ coarsest :
        CoarsestQuotientCertified viabilityProbes sufficiency
          B.interfaceQuotient,
        ViabilitySufficientBoundary viabilityProbes sufficiency B coarsest ∧
          SelfMaintainedBoundary S H appPolicy maintenancePolicy
            reinstatementPolicy boundaryApparatus I B

def MaximalIndividuating
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    {InstrumentRecord : Type y} {LedgerEntry : Type y'}
    {DefectRecord : Type y''} {MovePayload : Type y'''}
    {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
    {ChallengeClass : Type z} {SourceQuotient : Type z'}
    {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
    {ObstructionWitness : Type z''''}
    (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
      InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
      AuditRecord)
    (H :
      ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
        TargetReadout ObstructionWitness DefectRecord MoveRecord
        AuditRecord)
    {Probe : Type z'''''} {XiFamily : Type z''''''}
    (recordPolicyI : CarriedRecordPolicy S.T LedgerEntry)
    (generatedBy : GeneratedByActivityIn S)
    (sourceStatePolicy : CarriedRecordPolicy S.T S.T.Z)
    (accessPolicyRecord :
      CarriedRecordPolicy S.T (AccessPolicy Probe XiFamily))
    (viabilityProbes : DeclaredViabilityProbes S.T)
    (sufficiency : SufficiencyClosureCertified viabilityProbes)
    (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
    (maintenancePolicy : CarriedRecordPolicy S.T MaintenanceOperatorRecord)
    (reinstatementPolicy :
      CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
    (boundaryApparatus : BoundaryApparatusFor S)
    (candidates : Candidates S.T)
    (I : Subcarrier S.T) : Prop :=
  I ∈ candidates.members ∧
    Individuates S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus I ∧
    ∀ I' : Subcarrier S.T,
      I' ∈ candidates.members ->
        (∀ z : S.T.Z, I z -> I' z) ->
          Individuates S H recordPolicyI generatedBy sourceStatePolicy
            accessPolicyRecord viabilityProbes sufficiency appPolicy
            maintenancePolicy reinstatementPolicy boundaryApparatus I' ->
            I' = I

section StatusApparatus

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
variable {ChallengeClass : Type z} {SourceQuotient : Type z'}
variable {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
variable {ObstructionWitness : Type z''''}
variable {Probe : Type z'''''} {XiFamily : Type z''''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
  AuditRecord)
variable (H :
  ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
    TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
variable (recordPolicyI : CarriedRecordPolicy S.T LedgerEntry)
variable (generatedBy : GeneratedByActivityIn S)
variable (sourceStatePolicy : CarriedRecordPolicy S.T S.T.Z)
variable (accessPolicyRecord :
  CarriedRecordPolicy S.T (AccessPolicy Probe XiFamily))
variable (viabilityProbes : DeclaredViabilityProbes S.T)
variable (sufficiency : SufficiencyClosureCertified viabilityProbes)
variable (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
variable (maintenancePolicy :
  CarriedRecordPolicy S.T MaintenanceOperatorRecord)
variable (reinstatementPolicy :
  CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
variable (boundaryApparatus : BoundaryApparatusFor S)
variable (candidates : Candidates S.T)

def OverlapsAnotherMaximal (I : Subcarrier S.T) : Prop :=
  ∃ I' : Subcarrier S.T,
    I' ∈ candidates.members ∧
      MaximalIndividuating S H recordPolicyI generatedBy
        sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
        appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
        candidates I' ∧
      I' ≠ I ∧
      (∃ z : S.T.Z, I z ∧ I' z) ∧
      ¬ (∀ z : S.T.Z, I z -> I' z) ∧
      ¬ (∀ z : S.T.Z, I' z -> I z)

def FederatedEvidence (I : Subcarrier S.T) : Prop :=
  (I ∈ candidates.members ∧
      ¬ Individuates S H recordPolicyI generatedBy sourceStatePolicy
        accessPolicyRecord viabilityProbes sufficiency appPolicy
        maintenancePolicy reinstatementPolicy boundaryApparatus I ∧
      ∃ C : Subcarrier S.T,
        C ∈ candidates.members ∧
          (∀ z : S.T.Z, I z -> C z) ∧
          I ≠ C ∧
          MaximalIndividuating S H recordPolicyI generatedBy
            sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
            appPolicy maintenancePolicy reinstatementPolicy
            boundaryApparatus candidates C) ∨
    (MaximalIndividuating S H recordPolicyI generatedBy
        sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
        appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
        candidates I ∧
      OverlapsAnotherMaximal S H recordPolicyI generatedBy
        sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
        appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
        candidates I)

inductive IndividuationStatus where
  | integrated
  | federated
  | subsidiary
  | platform_dependent
  | shadow
  | non_individuated
  deriving DecidableEq, Repr

def IntegratedCase (I : Subcarrier S.T) : Prop :=
  MaximalIndividuating S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I ∧
    ¬ OverlapsAnotherMaximal S H recordPolicyI generatedBy
      sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
      appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
      candidates I

def FederatedCase (I : Subcarrier S.T) : Prop :=
  ¬ IntegratedCase S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I ∧
    FederatedEvidence S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I

def SubsidiaryCase (I : Subcarrier S.T) : Prop :=
  ¬ IntegratedCase S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I ∧
    ¬ FederatedCase S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I ∧
    RepairClosedOn S sourceStatePolicy I ∧
    RecordClosedOn S recordPolicyI generatedBy I ∧
    ¬ BudgetClosedOn S recordPolicyI accessPolicyRecord I ∧
    ∃ B : InstitutionalBoundaryCandidate I,
      ∃ coarsest :
        CoarsestQuotientCertified viabilityProbes sufficiency
          B.interfaceQuotient,
        ViabilitySufficientBoundary viabilityProbes sufficiency B coarsest

def PlatformDependentCase (I : Subcarrier S.T) : Prop :=
  ¬ IntegratedCase S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I ∧
    ¬ FederatedCase S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I ∧
    ¬ SubsidiaryCase S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I ∧
    RepairClosedOn S sourceStatePolicy I ∧
    BudgetClosedOn S recordPolicyI accessPolicyRecord I ∧
    RecordClosedOn S recordPolicyI generatedBy I ∧
    ∃ B : InstitutionalBoundaryCandidate I,
      ∃ coarsest :
        CoarsestQuotientCertified viabilityProbes sufficiency
          B.interfaceQuotient,
        ViabilitySufficientBoundary viabilityProbes sufficiency B coarsest ∧
          ¬ SelfMaintainedBoundary S H appPolicy maintenancePolicy
            reinstatementPolicy boundaryApparatus I B

def ShadowCase (I : Subcarrier S.T) : Prop :=
  ¬ IntegratedCase S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I ∧
    ¬ FederatedCase S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I ∧
    ¬ SubsidiaryCase S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I ∧
    ¬ PlatformDependentCase S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I ∧
    RepairClosedOn S sourceStatePolicy I ∧
    BudgetClosedOn S recordPolicyI accessPolicyRecord I ∧
    ¬ RecordClosedOn S recordPolicyI generatedBy I

def NonIndividuatedCase (I : Subcarrier S.T) : Prop :=
  ¬ IntegratedCase S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I ∧
    ¬ FederatedCase S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I ∧
    ¬ SubsidiaryCase S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I ∧
    ¬ PlatformDependentCase S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I ∧
    ¬ ShadowCase S H recordPolicyI generatedBy sourceStatePolicy
      accessPolicyRecord viabilityProbes sufficiency appPolicy
      maintenancePolicy reinstatementPolicy boundaryApparatus candidates I

structure IndividuationStatusRecord
    {FData : Type u} {RuleFamily : Type v}
    {ResidualFamily : Type w} {AuditAccessData : Type x}
    (T : TheoryPackage FData RuleFamily ResidualFamily AuditAccessData)
    (LedgerEntry : Type y) (AuditRecord : Type y') where
  subcarrier : Subcarrier T
  status : IndividuationStatus
  supportingLedgerEntries : List LedgerEntry
  supportingAuditRecords : List AuditRecord

variable (statusPolicy :
  CarriedRecordPolicy S.T (IndividuationStatusRecord S.T LedgerEntry AuditRecord))

def IndividuationStatusOccurrenceFor
    (I : Subcarrier S.T)
    (record : IndividuationStatusRecord S.T LedgerEntry AuditRecord) :
    Prop :=
  I ∈ candidates.members ∧
    record.subcarrier = I ∧
    (∃ n0 : Nat,
      CarriedRecordAt statusPolicy record n0
        FineSourceTag.committed_state true true) ∧
    (∀ entry : LedgerEntry, entry ∈ record.supportingLedgerEntries ->
      entry ∈ S.Lambda_S.ledgerEntries) ∧
    ∀ auditRecord : AuditRecord, auditRecord ∈ record.supportingAuditRecords ->
      HasCarriedRecordEvidence S.auditRecordPolicy auditRecord

def IntegratedHolds (I : Subcarrier S.T) : Prop :=
  ∃ record : IndividuationStatusRecord S.T LedgerEntry AuditRecord,
    IndividuationStatusOccurrenceFor S candidates statusPolicy I record ∧
      record.status = IndividuationStatus.integrated ∧
      IntegratedCase S H recordPolicyI generatedBy sourceStatePolicy
        accessPolicyRecord viabilityProbes sufficiency appPolicy
        maintenancePolicy reinstatementPolicy boundaryApparatus candidates I

def FederatedHolds (I : Subcarrier S.T) : Prop :=
  ∃ record : IndividuationStatusRecord S.T LedgerEntry AuditRecord,
    IndividuationStatusOccurrenceFor S candidates statusPolicy I record ∧
      record.status = IndividuationStatus.federated ∧
      FederatedCase S H recordPolicyI generatedBy sourceStatePolicy
        accessPolicyRecord viabilityProbes sufficiency appPolicy
        maintenancePolicy reinstatementPolicy boundaryApparatus candidates I

def SubsidiaryHolds (I : Subcarrier S.T) : Prop :=
  ∃ record : IndividuationStatusRecord S.T LedgerEntry AuditRecord,
    IndividuationStatusOccurrenceFor S candidates statusPolicy I record ∧
      record.status = IndividuationStatus.subsidiary ∧
      SubsidiaryCase S H recordPolicyI generatedBy sourceStatePolicy
        accessPolicyRecord viabilityProbes sufficiency appPolicy
        maintenancePolicy reinstatementPolicy boundaryApparatus candidates I

def PlatformDependentHolds (I : Subcarrier S.T) : Prop :=
  ∃ record : IndividuationStatusRecord S.T LedgerEntry AuditRecord,
    IndividuationStatusOccurrenceFor S candidates statusPolicy I record ∧
      record.status = IndividuationStatus.platform_dependent ∧
      PlatformDependentCase S H recordPolicyI generatedBy sourceStatePolicy
        accessPolicyRecord viabilityProbes sufficiency appPolicy
        maintenancePolicy reinstatementPolicy boundaryApparatus candidates I

def ShadowHolds (I : Subcarrier S.T) : Prop :=
  ∃ record : IndividuationStatusRecord S.T LedgerEntry AuditRecord,
    IndividuationStatusOccurrenceFor S candidates statusPolicy I record ∧
      record.status = IndividuationStatus.shadow ∧
      ShadowCase S H recordPolicyI generatedBy sourceStatePolicy
        accessPolicyRecord viabilityProbes sufficiency appPolicy
        maintenancePolicy reinstatementPolicy boundaryApparatus candidates I

def NonIndividuatedHolds (I : Subcarrier S.T) : Prop :=
  ∃ record : IndividuationStatusRecord S.T LedgerEntry AuditRecord,
    IndividuationStatusOccurrenceFor S candidates statusPolicy I record ∧
      record.status = IndividuationStatus.non_individuated ∧
      NonIndividuatedCase S H recordPolicyI generatedBy sourceStatePolicy
        accessPolicyRecord viabilityProbes sufficiency appPolicy
        maintenancePolicy reinstatementPolicy boundaryApparatus candidates I

def CompleteIndividuationStatus (I : Subcarrier S.T) : Prop :=
  (∃ record : IndividuationStatusRecord S.T LedgerEntry AuditRecord,
    IndividuationStatusOccurrenceFor S candidates statusPolicy I record ∧
      ((record.status = IndividuationStatus.integrated ∧
          IntegratedCase S H recordPolicyI generatedBy sourceStatePolicy
            accessPolicyRecord viabilityProbes sufficiency appPolicy
            maintenancePolicy reinstatementPolicy boundaryApparatus
            candidates I) ∨
        (record.status = IndividuationStatus.federated ∧
          FederatedCase S H recordPolicyI generatedBy sourceStatePolicy
            accessPolicyRecord viabilityProbes sufficiency appPolicy
            maintenancePolicy reinstatementPolicy boundaryApparatus
            candidates I) ∨
        (record.status = IndividuationStatus.subsidiary ∧
          SubsidiaryCase S H recordPolicyI generatedBy sourceStatePolicy
            accessPolicyRecord viabilityProbes sufficiency appPolicy
            maintenancePolicy reinstatementPolicy boundaryApparatus
            candidates I) ∨
        (record.status = IndividuationStatus.platform_dependent ∧
          PlatformDependentCase S H recordPolicyI generatedBy
            sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
            appPolicy maintenancePolicy reinstatementPolicy
            boundaryApparatus candidates I) ∨
        (record.status = IndividuationStatus.shadow ∧
          ShadowCase S H recordPolicyI generatedBy sourceStatePolicy
            accessPolicyRecord viabilityProbes sufficiency appPolicy
            maintenancePolicy reinstatementPolicy boundaryApparatus
            candidates I) ∨
        (record.status = IndividuationStatus.non_individuated ∧
          NonIndividuatedCase S H recordPolicyI generatedBy
            sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
            appPolicy maintenancePolicy reinstatementPolicy
            boundaryApparatus candidates I))) ∧
    ∀ record1 record2 :
      IndividuationStatusRecord S.T LedgerEntry AuditRecord,
      IndividuationStatusOccurrenceFor S candidates statusPolicy I record1 ->
      IndividuationStatusOccurrenceFor S candidates statusPolicy I record2 ->
      record1.status = record2.status

end StatusApparatus

section Theorems

variable {FData : Type u} {RuleFamily : Type v}
variable {ResidualFamily : Type w} {AuditAccessData : Type x}
variable {InstrumentRecord : Type y} {LedgerEntry : Type y'}
variable {DefectRecord : Type y''} {MovePayload : Type y'''}
variable {MoveRecord : Type y''''} {AuditRecord : Type y'''''}
variable {ChallengeClass : Type z} {SourceQuotient : Type z'}
variable {DeclaredFamily : Type z''} {TargetReadout : Type z'''}
variable {ObstructionWitness : Type z''''}
variable {Probe : Type z'''''} {XiFamily : Type z''''''}

variable (S : ESystem FData RuleFamily ResidualFamily AuditAccessData
  InstrumentRecord LedgerEntry DefectRecord MovePayload MoveRecord
  AuditRecord)
variable (H :
  ChallengeHistory ChallengeClass SourceQuotient DeclaredFamily
    TargetReadout ObstructionWitness DefectRecord MoveRecord AuditRecord)
variable (recordPolicyI : CarriedRecordPolicy S.T LedgerEntry)
variable (generatedBy : GeneratedByActivityIn S)
variable (sourceStatePolicy : CarriedRecordPolicy S.T S.T.Z)
variable (accessPolicyRecord :
  CarriedRecordPolicy S.T (AccessPolicy Probe XiFamily))
variable (viabilityProbes : DeclaredViabilityProbes S.T)
variable (sufficiency : SufficiencyClosureCertified viabilityProbes)
variable (appPolicy : CarriedRecordPolicy S.T ClosureApparatusRecord)
variable (maintenancePolicy :
  CarriedRecordPolicy S.T MaintenanceOperatorRecord)
variable (reinstatementPolicy :
  CarriedRecordPolicy S.T (MaintenanceReinstatementRecord S))
variable (boundaryApparatus : BoundaryApparatusFor S)
variable (candidates : Candidates S.T)
variable (statusPolicy :
  CarriedRecordPolicy S.T (IndividuationStatusRecord S.T LedgerEntry AuditRecord))

theorem E12_Individuation
    (I : Subcarrier S.T)
    (record : IndividuationStatusRecord S.T LedgerEntry AuditRecord)
    (hOccurrence :
      IndividuationStatusOccurrenceFor S candidates statusPolicy I record)
    (hCase :
      match record.status with
      | IndividuationStatus.integrated =>
          IntegratedCase S H recordPolicyI generatedBy sourceStatePolicy
            accessPolicyRecord viabilityProbes sufficiency appPolicy
            maintenancePolicy reinstatementPolicy boundaryApparatus
            candidates I
      | IndividuationStatus.federated =>
          FederatedCase S H recordPolicyI generatedBy sourceStatePolicy
            accessPolicyRecord viabilityProbes sufficiency appPolicy
            maintenancePolicy reinstatementPolicy boundaryApparatus
            candidates I
      | IndividuationStatus.subsidiary =>
          SubsidiaryCase S H recordPolicyI generatedBy sourceStatePolicy
            accessPolicyRecord viabilityProbes sufficiency appPolicy
            maintenancePolicy reinstatementPolicy boundaryApparatus
            candidates I
      | IndividuationStatus.platform_dependent =>
          PlatformDependentCase S H recordPolicyI generatedBy
            sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
            appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
            candidates I
      | IndividuationStatus.shadow =>
          ShadowCase S H recordPolicyI generatedBy sourceStatePolicy
            accessPolicyRecord viabilityProbes sufficiency appPolicy
            maintenancePolicy reinstatementPolicy boundaryApparatus
            candidates I
      | IndividuationStatus.non_individuated =>
          NonIndividuatedCase S H recordPolicyI generatedBy
            sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
            appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
            candidates I) :
    match record.status with
    | IndividuationStatus.integrated =>
        IntegratedHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I
    | IndividuationStatus.federated =>
        FederatedHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I
    | IndividuationStatus.subsidiary =>
        SubsidiaryHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I
    | IndividuationStatus.platform_dependent =>
        PlatformDependentHolds S H recordPolicyI generatedBy
          sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
          appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
          candidates statusPolicy I
    | IndividuationStatus.shadow =>
        ShadowHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I
    | IndividuationStatus.non_individuated =>
        NonIndividuatedHolds S H recordPolicyI generatedBy
          sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
          appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
          candidates statusPolicy I := by
  cases hStatus : record.status <;> simp [hStatus] at hCase ⊢
  · exact ⟨record, hOccurrence, hStatus, hCase⟩
  · exact ⟨record, hOccurrence, hStatus, hCase⟩
  · exact ⟨record, hOccurrence, hStatus, hCase⟩
  · exact ⟨record, hOccurrence, hStatus, hCase⟩
  · exact ⟨record, hOccurrence, hStatus, hCase⟩
  · exact ⟨record, hOccurrence, hStatus, hCase⟩

theorem E12_StatusPartition
    (I : Subcarrier S.T)
    (hComplete :
      CompleteIndividuationStatus S H recordPolicyI generatedBy
        sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
        appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
        candidates statusPolicy I) :
    (IntegratedHolds S H recordPolicyI generatedBy sourceStatePolicy
        accessPolicyRecord viabilityProbes sufficiency appPolicy
        maintenancePolicy reinstatementPolicy boundaryApparatus candidates
        statusPolicy I ∧
        ¬ FederatedHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ SubsidiaryHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ PlatformDependentHolds S H recordPolicyI generatedBy
          sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
          appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
          candidates statusPolicy I ∧
        ¬ ShadowHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ NonIndividuatedHolds S H recordPolicyI generatedBy
          sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
          appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
          candidates statusPolicy I) ∨
      (FederatedHolds S H recordPolicyI generatedBy sourceStatePolicy
        accessPolicyRecord viabilityProbes sufficiency appPolicy
        maintenancePolicy reinstatementPolicy boundaryApparatus candidates
        statusPolicy I ∧
        ¬ IntegratedHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ SubsidiaryHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ PlatformDependentHolds S H recordPolicyI generatedBy
          sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
          appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
          candidates statusPolicy I ∧
        ¬ ShadowHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ NonIndividuatedHolds S H recordPolicyI generatedBy
          sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
          appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
          candidates statusPolicy I) ∨
      (SubsidiaryHolds S H recordPolicyI generatedBy sourceStatePolicy
        accessPolicyRecord viabilityProbes sufficiency appPolicy
        maintenancePolicy reinstatementPolicy boundaryApparatus candidates
        statusPolicy I ∧
        ¬ IntegratedHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ FederatedHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ PlatformDependentHolds S H recordPolicyI generatedBy
          sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
          appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
          candidates statusPolicy I ∧
        ¬ ShadowHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ NonIndividuatedHolds S H recordPolicyI generatedBy
          sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
          appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
          candidates statusPolicy I) ∨
      (PlatformDependentHolds S H recordPolicyI generatedBy
        sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
        appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
        candidates statusPolicy I ∧
        ¬ IntegratedHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ FederatedHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ SubsidiaryHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ ShadowHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ NonIndividuatedHolds S H recordPolicyI generatedBy
          sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
          appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
          candidates statusPolicy I) ∨
      (ShadowHolds S H recordPolicyI generatedBy sourceStatePolicy
        accessPolicyRecord viabilityProbes sufficiency appPolicy
        maintenancePolicy reinstatementPolicy boundaryApparatus candidates
        statusPolicy I ∧
        ¬ IntegratedHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ FederatedHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ SubsidiaryHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ PlatformDependentHolds S H recordPolicyI generatedBy
          sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
          appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
          candidates statusPolicy I ∧
        ¬ NonIndividuatedHolds S H recordPolicyI generatedBy
          sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
          appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
          candidates statusPolicy I) ∨
      (NonIndividuatedHolds S H recordPolicyI generatedBy
        sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
        appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
        candidates statusPolicy I ∧
        ¬ IntegratedHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ FederatedHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ SubsidiaryHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I ∧
        ¬ PlatformDependentHolds S H recordPolicyI generatedBy
          sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
          appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
          candidates statusPolicy I ∧
        ¬ ShadowHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I) := by
  rcases hComplete.1 with ⟨record, hOccurrence, hBranch⟩
  rcases hBranch with hIntegratedCase | hRest
  · have hIntegrated :
        IntegratedHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I :=
      ⟨record, hOccurrence, hIntegratedCase.1, hIntegratedCase.2⟩
    have hNotFederated :
        ¬ FederatedHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I := by
      intro hOther
      rcases hOther with ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
      exact hOtherCase.1 hIntegratedCase.2
    have hNotSubsidiary :
        ¬ SubsidiaryHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I := by
      intro hOther
      rcases hOther with ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
      exact hOtherCase.1 hIntegratedCase.2
    have hNotPlatform :
        ¬ PlatformDependentHolds S H recordPolicyI generatedBy
          sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
          appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
          candidates statusPolicy I := by
      intro hOther
      rcases hOther with ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
      exact hOtherCase.1 hIntegratedCase.2
    have hNotShadow :
        ¬ ShadowHolds S H recordPolicyI generatedBy sourceStatePolicy
          accessPolicyRecord viabilityProbes sufficiency appPolicy
          maintenancePolicy reinstatementPolicy boundaryApparatus candidates
          statusPolicy I := by
      intro hOther
      rcases hOther with ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
      exact hOtherCase.1 hIntegratedCase.2
    have hNotNon :
        ¬ NonIndividuatedHolds S H recordPolicyI generatedBy
          sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
          appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
          candidates statusPolicy I := by
      intro hOther
      rcases hOther with ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
      exact hOtherCase.1 hIntegratedCase.2
    exact Or.inl
      ⟨hIntegrated, hNotFederated, hNotSubsidiary, hNotPlatform,
        hNotShadow, hNotNon⟩
  · rcases hRest with hFederatedCase | hRest
    · have hFederated :
          FederatedHolds S H recordPolicyI generatedBy sourceStatePolicy
            accessPolicyRecord viabilityProbes sufficiency appPolicy
            maintenancePolicy reinstatementPolicy boundaryApparatus candidates
            statusPolicy I :=
        ⟨record, hOccurrence, hFederatedCase.1, hFederatedCase.2⟩
      have hNotIntegrated :
          ¬ IntegratedHolds S H recordPolicyI generatedBy sourceStatePolicy
            accessPolicyRecord viabilityProbes sufficiency appPolicy
            maintenancePolicy reinstatementPolicy boundaryApparatus candidates
            statusPolicy I := by
        intro hOther
        rcases hOther with
          ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
        exact hFederatedCase.2.1 hOtherCase
      have hNotSubsidiary :
          ¬ SubsidiaryHolds S H recordPolicyI generatedBy sourceStatePolicy
            accessPolicyRecord viabilityProbes sufficiency appPolicy
            maintenancePolicy reinstatementPolicy boundaryApparatus candidates
            statusPolicy I := by
        intro hOther
        rcases hOther with
          ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
        exact hOtherCase.2.1 hFederatedCase.2
      have hNotPlatform :
          ¬ PlatformDependentHolds S H recordPolicyI generatedBy
            sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
            appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
            candidates statusPolicy I := by
        intro hOther
        rcases hOther with
          ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
        exact hOtherCase.2.1 hFederatedCase.2
      have hNotShadow :
          ¬ ShadowHolds S H recordPolicyI generatedBy sourceStatePolicy
            accessPolicyRecord viabilityProbes sufficiency appPolicy
            maintenancePolicy reinstatementPolicy boundaryApparatus candidates
            statusPolicy I := by
        intro hOther
        rcases hOther with
          ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
        exact hOtherCase.2.1 hFederatedCase.2
      have hNotNon :
          ¬ NonIndividuatedHolds S H recordPolicyI generatedBy
            sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
            appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
            candidates statusPolicy I := by
        intro hOther
        rcases hOther with
          ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
        exact hOtherCase.2.1 hFederatedCase.2
      exact Or.inr (Or.inl
        ⟨hFederated, hNotIntegrated, hNotSubsidiary, hNotPlatform,
          hNotShadow, hNotNon⟩)
    · rcases hRest with hSubsidiaryCase | hRest
      · have hSubsidiary :
            SubsidiaryHolds S H recordPolicyI generatedBy sourceStatePolicy
              accessPolicyRecord viabilityProbes sufficiency appPolicy
              maintenancePolicy reinstatementPolicy boundaryApparatus candidates
              statusPolicy I :=
          ⟨record, hOccurrence, hSubsidiaryCase.1, hSubsidiaryCase.2⟩
        have hNotIntegrated :
            ¬ IntegratedHolds S H recordPolicyI generatedBy sourceStatePolicy
              accessPolicyRecord viabilityProbes sufficiency appPolicy
              maintenancePolicy reinstatementPolicy boundaryApparatus candidates
              statusPolicy I := by
          intro hOther
          rcases hOther with
            ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
          exact hSubsidiaryCase.2.1 hOtherCase
        have hNotFederated :
            ¬ FederatedHolds S H recordPolicyI generatedBy sourceStatePolicy
              accessPolicyRecord viabilityProbes sufficiency appPolicy
              maintenancePolicy reinstatementPolicy boundaryApparatus candidates
              statusPolicy I := by
          intro hOther
          rcases hOther with
            ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
          exact hSubsidiaryCase.2.2.1 hOtherCase
        have hNotPlatform :
            ¬ PlatformDependentHolds S H recordPolicyI generatedBy
              sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
              appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
              candidates statusPolicy I := by
          intro hOther
          rcases hOther with
            ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
          exact hOtherCase.2.2.1 hSubsidiaryCase.2
        have hNotShadow :
            ¬ ShadowHolds S H recordPolicyI generatedBy sourceStatePolicy
              accessPolicyRecord viabilityProbes sufficiency appPolicy
              maintenancePolicy reinstatementPolicy boundaryApparatus candidates
              statusPolicy I := by
          intro hOther
          rcases hOther with
            ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
          exact hOtherCase.2.2.1 hSubsidiaryCase.2
        have hNotNon :
            ¬ NonIndividuatedHolds S H recordPolicyI generatedBy
              sourceStatePolicy accessPolicyRecord viabilityProbes sufficiency
              appPolicy maintenancePolicy reinstatementPolicy boundaryApparatus
              candidates statusPolicy I := by
          intro hOther
          rcases hOther with
            ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
          exact hOtherCase.2.2.1 hSubsidiaryCase.2
        exact Or.inr (Or.inr (Or.inl
          ⟨hSubsidiary, hNotIntegrated, hNotFederated, hNotPlatform,
            hNotShadow, hNotNon⟩))
      · rcases hRest with hPlatformCase | hRest
        · have hPlatform :
              PlatformDependentHolds S H recordPolicyI generatedBy
                sourceStatePolicy accessPolicyRecord viabilityProbes
                sufficiency appPolicy maintenancePolicy reinstatementPolicy
                boundaryApparatus candidates statusPolicy I :=
            ⟨record, hOccurrence, hPlatformCase.1, hPlatformCase.2⟩
          have hNotIntegrated :
              ¬ IntegratedHolds S H recordPolicyI generatedBy
                sourceStatePolicy accessPolicyRecord viabilityProbes
                sufficiency appPolicy maintenancePolicy reinstatementPolicy
                boundaryApparatus candidates statusPolicy I := by
            intro hOther
            rcases hOther with
              ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
            exact hPlatformCase.2.1 hOtherCase
          have hNotFederated :
              ¬ FederatedHolds S H recordPolicyI generatedBy sourceStatePolicy
                accessPolicyRecord viabilityProbes sufficiency appPolicy
                maintenancePolicy reinstatementPolicy boundaryApparatus
                candidates statusPolicy I := by
            intro hOther
            rcases hOther with
              ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
            exact hPlatformCase.2.2.1 hOtherCase
          have hNotSubsidiary :
              ¬ SubsidiaryHolds S H recordPolicyI generatedBy
                sourceStatePolicy accessPolicyRecord viabilityProbes
                sufficiency appPolicy maintenancePolicy reinstatementPolicy
                boundaryApparatus candidates statusPolicy I := by
            intro hOther
            rcases hOther with
              ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
            exact hPlatformCase.2.2.2.1 hOtherCase
          have hNotShadow :
              ¬ ShadowHolds S H recordPolicyI generatedBy sourceStatePolicy
                accessPolicyRecord viabilityProbes sufficiency appPolicy
                maintenancePolicy reinstatementPolicy boundaryApparatus
                candidates statusPolicy I := by
            intro hOther
            rcases hOther with
              ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
            exact hOtherCase.2.2.2.1 hPlatformCase.2
          have hNotNon :
              ¬ NonIndividuatedHolds S H recordPolicyI generatedBy
                sourceStatePolicy accessPolicyRecord viabilityProbes
                sufficiency appPolicy maintenancePolicy reinstatementPolicy
                boundaryApparatus candidates statusPolicy I := by
            intro hOther
            rcases hOther with
              ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
            exact hOtherCase.2.2.2.1 hPlatformCase.2
          exact Or.inr (Or.inr (Or.inr (Or.inl
            ⟨hPlatform, hNotIntegrated, hNotFederated, hNotSubsidiary,
              hNotShadow, hNotNon⟩)))
        · rcases hRest with hShadowCase | hNonCase
          · have hShadow :
                ShadowHolds S H recordPolicyI generatedBy sourceStatePolicy
                  accessPolicyRecord viabilityProbes sufficiency appPolicy
                  maintenancePolicy reinstatementPolicy boundaryApparatus
                  candidates statusPolicy I :=
              ⟨record, hOccurrence, hShadowCase.1, hShadowCase.2⟩
            have hNotIntegrated :
                ¬ IntegratedHolds S H recordPolicyI generatedBy
                  sourceStatePolicy accessPolicyRecord viabilityProbes
                  sufficiency appPolicy maintenancePolicy reinstatementPolicy
                  boundaryApparatus candidates statusPolicy I := by
              intro hOther
              rcases hOther with
                ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              exact hShadowCase.2.1 hOtherCase
            have hNotFederated :
                ¬ FederatedHolds S H recordPolicyI generatedBy
                  sourceStatePolicy accessPolicyRecord viabilityProbes
                  sufficiency appPolicy maintenancePolicy reinstatementPolicy
                  boundaryApparatus candidates statusPolicy I := by
              intro hOther
              rcases hOther with
                ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              exact hShadowCase.2.2.1 hOtherCase
            have hNotSubsidiary :
                ¬ SubsidiaryHolds S H recordPolicyI generatedBy
                  sourceStatePolicy accessPolicyRecord viabilityProbes
                  sufficiency appPolicy maintenancePolicy reinstatementPolicy
                  boundaryApparatus candidates statusPolicy I := by
              intro hOther
              rcases hOther with
                ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              exact hShadowCase.2.2.2.1 hOtherCase
            have hNotPlatform :
                ¬ PlatformDependentHolds S H recordPolicyI generatedBy
                  sourceStatePolicy accessPolicyRecord viabilityProbes
                  sufficiency appPolicy maintenancePolicy reinstatementPolicy
                  boundaryApparatus candidates statusPolicy I := by
              intro hOther
              rcases hOther with
                ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              exact hShadowCase.2.2.2.2.1 hOtherCase
            have hNotNon :
                ¬ NonIndividuatedHolds S H recordPolicyI generatedBy
                  sourceStatePolicy accessPolicyRecord viabilityProbes
                  sufficiency appPolicy maintenancePolicy reinstatementPolicy
                  boundaryApparatus candidates statusPolicy I := by
              intro hOther
              rcases hOther with
                ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              exact hOtherCase.2.2.2.2 hShadowCase.2
            exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inl
              ⟨hShadow, hNotIntegrated, hNotFederated, hNotSubsidiary,
                hNotPlatform, hNotNon⟩))))
          · have hNon :
                NonIndividuatedHolds S H recordPolicyI generatedBy
                  sourceStatePolicy accessPolicyRecord viabilityProbes
                  sufficiency appPolicy maintenancePolicy reinstatementPolicy
                  boundaryApparatus candidates statusPolicy I :=
              ⟨record, hOccurrence, hNonCase.1, hNonCase.2⟩
            have hNotIntegrated :
                ¬ IntegratedHolds S H recordPolicyI generatedBy
                  sourceStatePolicy accessPolicyRecord viabilityProbes
                  sufficiency appPolicy maintenancePolicy reinstatementPolicy
                  boundaryApparatus candidates statusPolicy I := by
              intro hOther
              rcases hOther with
                ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              exact hNonCase.2.1 hOtherCase
            have hNotFederated :
                ¬ FederatedHolds S H recordPolicyI generatedBy
                  sourceStatePolicy accessPolicyRecord viabilityProbes
                  sufficiency appPolicy maintenancePolicy reinstatementPolicy
                  boundaryApparatus candidates statusPolicy I := by
              intro hOther
              rcases hOther with
                ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              exact hNonCase.2.2.1 hOtherCase
            have hNotSubsidiary :
                ¬ SubsidiaryHolds S H recordPolicyI generatedBy
                  sourceStatePolicy accessPolicyRecord viabilityProbes
                  sufficiency appPolicy maintenancePolicy reinstatementPolicy
                  boundaryApparatus candidates statusPolicy I := by
              intro hOther
              rcases hOther with
                ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              exact hNonCase.2.2.2.1 hOtherCase
            have hNotPlatform :
                ¬ PlatformDependentHolds S H recordPolicyI generatedBy
                  sourceStatePolicy accessPolicyRecord viabilityProbes
                  sufficiency appPolicy maintenancePolicy reinstatementPolicy
                  boundaryApparatus candidates statusPolicy I := by
              intro hOther
              rcases hOther with
                ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              exact hNonCase.2.2.2.2.1 hOtherCase
            have hNotShadow :
                ¬ ShadowHolds S H recordPolicyI generatedBy sourceStatePolicy
                  accessPolicyRecord viabilityProbes sufficiency appPolicy
                  maintenancePolicy reinstatementPolicy boundaryApparatus
                  candidates statusPolicy I := by
              intro hOther
              rcases hOther with
                ⟨other, _hOtherOccurrence, _hOtherStatus, hOtherCase⟩
              exact hNonCase.2.2.2.2.2 hOtherCase
            exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr
              ⟨hNon, hNotIntegrated, hNotFederated, hNotSubsidiary,
                hNotPlatform, hNotShadow⟩))))

end Theorems

end SixBirdsFoundationsV
