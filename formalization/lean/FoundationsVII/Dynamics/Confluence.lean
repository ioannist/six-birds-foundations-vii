import FoundationsVII.Dynamics.Transmission
import FoundationsVII.Prior.FT14

/-!
# Confluence, critical pairs, and seed dependence

The finite criterion is stated only for the declared closed finite system.
Joinability and audit equivalence are both required. Terminal equality,
predictive equivalence, and presentation equality remain distinct.
-/

namespace FoundationsVII

structure CriticalPair where
  pairId : Nat
  bothLegal : Bool
  joinable : Bool
  auditEquivalent : Bool
  terminalEqual : Bool
  predictiveEquivalent : Bool
  deriving Repr, DecidableEq, BEq

namespace CriticalPair

def Resolved (pair : CriticalPair) : Prop :=
  pair.bothLegal = false ∨
    (pair.joinable = true ∧ pair.auditEquivalent = true)

theorem resolved_of_joinable_audit_equivalent {pair : CriticalPair}
    (hLegal : pair.bothLegal = true)
    (hJoinable : pair.joinable = true)
    (hAudit : pair.auditEquivalent = true) : Resolved pair := by
  exact Or.inr ⟨hJoinable, hAudit⟩

end CriticalPair

structure FiniteAdmissionSystem where
  criticalPairs : List CriticalPair
  closedFamily : Bool
  allTransitionsEnumerated : Bool
  deriving Repr, DecidableEq, BEq

namespace FiniteAdmissionSystem

def CriticalPairCriterion (system : FiniteAdmissionSystem) : Prop :=
  system.closedFamily = true ∧
  system.allTransitionsEnumerated = true ∧
  ∀ pair, pair ∈ system.criticalPairs → CriticalPair.Resolved pair

def ConfluentAtDeclaredScope (system : FiniteAdmissionSystem) : Prop :=
  system.closedFamily = true ∧
  system.allTransitionsEnumerated = true ∧
  ∀ pair, pair ∈ system.criticalPairs → pair.bothLegal = true →
    pair.joinable = true ∧ pair.auditEquivalent = true

theorem finite_critical_pair_criterion_iff_confluent
    (system : FiniteAdmissionSystem) :
    CriticalPairCriterion system ↔ ConfluentAtDeclaredScope system := by
  constructor
  · intro h
    refine ⟨h.1, h.2.1, ?_⟩
    intro pair hMem hLegal
    rcases h.2.2 pair hMem with hNotLegal | hResolved
    · rw [hLegal] at hNotLegal
      exact Bool.noConfusion hNotLegal
    · exact hResolved
  · intro h
    refine ⟨h.1, h.2.1, ?_⟩
    intro pair hMem
    cases hLegal : pair.bothLegal
    · exact Or.inl hLegal
    · exact Or.inr (h.2.2 pair hMem hLegal)

end FiniteAdmissionSystem

private def confluentPair : CriticalPair :=
  { pairId := 1, bothLegal := true, joinable := true,
    auditEquivalent := true, terminalEqual := true,
    predictiveEquivalent := true }

private def nonconfluentPair : CriticalPair :=
  { pairId := 2, bothLegal := true, joinable := false,
    auditEquivalent := false, terminalEqual := false,
    predictiveEquivalent := false }

private def confluentSystem : FiniteAdmissionSystem :=
  { criticalPairs := [confluentPair], closedFamily := true,
    allTransitionsEnumerated := true }

private def nonconfluentSystem : FiniteAdmissionSystem :=
  { criticalPairs := [nonconfluentPair], closedFamily := true,
    allTransitionsEnumerated := true }

theorem finite_confluent_positive_model :
    FiniteAdmissionSystem.ConfluentAtDeclaredScope confluentSystem := by
  simp [FiniteAdmissionSystem.ConfluentAtDeclaredScope,
    FiniteAdmissionSystem.CriticalPairCriterion, confluentSystem,
    CriticalPair.Resolved, confluentPair]

theorem finite_nonconfluent_countermodel :
    ¬ FiniteAdmissionSystem.ConfluentAtDeclaredScope nonconfluentSystem := by
  simp [FiniteAdmissionSystem.ConfluentAtDeclaredScope,
    FiniteAdmissionSystem.CriticalPairCriterion, nonconfluentSystem,
    CriticalPair.Resolved, nonconfluentPair]

structure SeedPartitionResult where
  sameRules : Bool
  sameSeedPartition : Bool
  terminalPackageA : Nat
  terminalPackageB : Nat
  predictiveEquivalent : Bool
  presentationOnly : Bool
  deriving Repr, DecidableEq, BEq

namespace SeedPartitionResult

def SeedDependent (result : SeedPartitionResult) : Prop :=
  result.sameRules = true ∧
  result.sameSeedPartition = false ∧
  result.terminalPackageA ≠ result.terminalPackageB

instance (result : SeedPartitionResult) : Decidable (SeedDependent result) := by
  unfold SeedDependent
  infer_instance

def PresentationDifferenceOnly (result : SeedPartitionResult) : Prop :=
  result.presentationOnly = true ∧
  result.predictiveEquivalent = true

instance (result : SeedPartitionResult) : Decidable (PresentationDifferenceOnly result) := by
  unfold PresentationDifferenceOnly
  infer_instance

end SeedPartitionResult

private def seedDependentControl : SeedPartitionResult :=
  { sameRules := true, sameSeedPartition := false,
    terminalPackageA := 1, terminalPackageB := 2,
    predictiveEquivalent := false, presentationOnly := false }

private def presentationOnlyControl : SeedPartitionResult :=
  { sameRules := true, sameSeedPartition := true,
    terminalPackageA := 1, terminalPackageB := 1,
    predictiveEquivalent := true, presentationOnly := true }

theorem seed_partition_can_change_terminal_package :
    SeedPartitionResult.SeedDependent seedDependentControl := by decide

theorem presentation_difference_is_not_seed_dependence :
    SeedPartitionResult.PresentationDifferenceOnly presentationOnlyControl ∧
    ¬ SeedPartitionResult.SeedDependent presentationOnlyControl := by decide

/-- One resolved square is not a global confluence proof. -/
structure LocalGlobalConfluenceBoundary where
  onePairResolved : Bool
  familyClosed : Bool
  allPairsChecked : Bool
  globalConfluenceCredit : Bool
  deriving Repr, DecidableEq, BEq

private def oneSquareOnly : LocalGlobalConfluenceBoundary :=
  { onePairResolved := true, familyClosed := false,
    allPairsChecked := false, globalConfluenceCredit := false }

theorem one_commuting_square_does_not_establish_global_confluence :
    oneSquareOnly.onePairResolved = true ∧
    oneSquareOnly.globalConfluenceCredit = false := by decide

end FoundationsVII
