import FoundationsVII.Core.Grades

/-!
# Narrow inherited-adapter contract

An adapter is explicit metadata plus a compile-time import of the named source
surface.  It never strengthens the source theorem and never hides added or lost
hypotheses.
-/

namespace FoundationsVII.Prior

inductive AdapterFidelity where
  | exactAlias
  | exactReusableCore
  | conditionalReuse
  | metadataOnly
  deriving Repr, DecidableEq, Inhabited

structure AdapterContract where
  adapterId : String
  formalizationTargetIds : List String
  sourceModule : String
  sourceDeclarations : List String
  sourceTypes : List String
  targetTypes : List String
  preservedHypotheses : List String
  addedHypotheses : List String
  lostHypotheses : List String
  trustDependencies : List String
  nonclaims : List String
  fidelity : AdapterFidelity
  deriving Repr, DecidableEq

namespace AdapterContract

def complete (contract : AdapterContract) : Prop :=
  contract.adapterId ≠ "" ∧
  contract.formalizationTargetIds ≠ [] ∧
  contract.sourceModule ≠ "" ∧
  contract.sourceDeclarations ≠ [] ∧
  contract.sourceTypes ≠ [] ∧
  contract.targetTypes ≠ [] ∧
  contract.nonclaims ≠ []

instance (contract : AdapterContract) : Decidable (complete contract) := by
  unfold complete
  infer_instance

end AdapterContract

end FoundationsVII.Prior
