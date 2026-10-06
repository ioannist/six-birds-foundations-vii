import FoundationsVII.Dynamics.CrossTime
import FoundationsVII.Enablement.Composition

/-!
# Primitive-operation algebra readiness

The full generators-and-relations program is reopened only after generators,
equivalence, composition domains, nonredundancy, semantics, and laws are all
fixed. A small resource-delta algebraic fragment is proved independently.
-/

namespace FoundationsVII

structure AlgebraReadiness where
  generatorsDeclared : Bool
  equivalenceDeclared : Bool
  compositionDomainsDeclared : Bool
  nonredundancyProved : Bool
  semanticsDeclared : Bool
  lawsProved : Bool
  deriving Repr, DecidableEq, BEq

namespace AlgebraReadiness

def Ready (readiness : AlgebraReadiness) : Prop :=
  readiness.generatorsDeclared = true ∧
  readiness.equivalenceDeclared = true ∧
  readiness.compositionDomainsDeclared = true ∧
  readiness.nonredundancyProved = true ∧
  readiness.semanticsDeclared = true ∧
  readiness.lawsProved = true

instance (readiness : AlgebraReadiness) : Decidable (Ready readiness) := by
  unfold Ready
  infer_instance

end AlgebraReadiness

private def currentAlgebraReadiness : AlgebraReadiness :=
  { generatorsDeclared := true, equivalenceDeclared := false,
    compositionDomainsDeclared := true, nonredundancyProved := false,
    semanticsDeclared := false, lawsProved := false }

private def reopenAlgebraReadiness : AlgebraReadiness :=
  { generatorsDeclared := true, equivalenceDeclared := true,
    compositionDomainsDeclared := true, nonredundancyProved := true,
    semanticsDeclared := true, lawsProved := true }

theorem current_full_primitive_algebra_is_not_ready :
    ¬ AlgebraReadiness.Ready currentAlgebraReadiness := by decide

theorem full_algebra_reopen_condition_is_exact :
    AlgebraReadiness.Ready reopenAlgebraReadiness := by decide

theorem resource_delta_fragment_is_associative
    (a b c : ResourceDelta) :
    ResourceDelta.combine (ResourceDelta.combine a b) c =
      ResourceDelta.combine a (ResourceDelta.combine b c) :=
  ResourceDelta.combine_assoc a b c

theorem resource_delta_fragment_has_left_identity (a : ResourceDelta) :
    ResourceDelta.combine ResourceDelta.zero a = a :=
  ResourceDelta.zero_left a

theorem resource_delta_fragment_has_right_identity (a : ResourceDelta) :
    ResourceDelta.combine a ResourceDelta.zero = a :=
  ResourceDelta.zero_right a

/-- DP12 terminal ruling. -/
theorem full_generators_relations_program_deferred_with_formal_reopen_condition :
    (¬ AlgebraReadiness.Ready currentAlgebraReadiness) ∧
    AlgebraReadiness.Ready reopenAlgebraReadiness := by decide

end FoundationsVII
