import FoundationsVII.Join.Strictness

/-!
# Source ancestry, honest bridging, and independence-sensitive credit

Behavioral nonfactorization and source independence are separate axes.  Native
and bridged records retain their declared source kinds.
-/

namespace FoundationsVII

structure SourceAncestry where
  sourceId : SourceId
  rootId : SourceId
  declaredParents : List SourceId
  kind : SourceKind
  deriving Repr, DecidableEq, BEq

namespace SourceAncestry

def SameLineage (left right : SourceAncestry) : Prop :=
  left.rootId = right.rootId

def Independent (left right : SourceAncestry) : Prop :=
  left.rootId ≠ right.rootId

theorem same_lineage_excludes_independence {left right : SourceAncestry}
    (hSame : SameLineage left right) : ¬ Independent left right := by
  intro hIndependent
  exact hIndependent hSame

theorem independence_excludes_same_lineage {left right : SourceAncestry}
    (hIndependent : Independent left right) : ¬ SameLineage left right := by
  intro hSame
  exact hIndependent hSame

end SourceAncestry

structure HonestBridgeRecord where
  bridgeId : BridgeId
  origin : SourceAncestry
  transported : SourceAncestry
  disposition : BridgeDisposition
  declaredOrigin : SourceId
  preservesSourceKind : Bool
  audit : AuditRecord
  deriving Repr, DecidableEq, BEq

namespace HonestBridgeRecord

def Certified (bridge : HonestBridgeRecord) : Prop :=
  bridge.disposition = BridgeDisposition.accepted ∧
  bridge.declaredOrigin = bridge.origin.sourceId ∧
  bridge.origin.sourceId ∈ bridge.transported.declaredParents ∧
  bridge.transported.kind = SourceKind.bridged ∧
  bridge.preservesSourceKind = true ∧
  bridge.audit.entries ≠ []

instance (bridge : HonestBridgeRecord) : Decidable (Certified bridge) := by
  unfold Certified
  infer_instance

theorem certified_records_bridged_kind {bridge : HonestBridgeRecord}
    (h : Certified bridge) : bridge.transported.kind = SourceKind.bridged :=
  h.2.2.2.1

theorem certified_records_declared_origin {bridge : HonestBridgeRecord}
    (h : Certified bridge) :
    bridge.origin.sourceId ∈ bridge.transported.declaredParents :=
  h.2.2.1

theorem certified_preserves_kind_metadata {bridge : HonestBridgeRecord}
    (h : Certified bridge) : bridge.preservesSourceKind = true :=
  h.2.2.2.2.1

end HonestBridgeRecord

structure SourceIndependenceGate where
  left : SourceAncestry
  right : SourceAncestry
  behavioralNonfactorization : Bool
  ancestryWitnessed : Bool
  bridgeHonest : Bool
  deriving Repr, DecidableEq, BEq

namespace SourceIndependenceGate

def Certified (gate : SourceIndependenceGate) : Prop :=
  SourceAncestry.Independent gate.left gate.right ∧
  gate.ancestryWitnessed = true ∧
  gate.bridgeHonest = true

def IndependenceSensitiveCredit (gate : SourceIndependenceGate) : Prop :=
  Certified gate ∧ gate.behavioralNonfactorization = true

theorem same_lineage_fails_independence_sensitive_credit
    {gate : SourceIndependenceGate}
    (hSame : SourceAncestry.SameLineage gate.left gate.right) :
    ¬ IndependenceSensitiveCredit gate := by
  intro hCredit
  exact SourceAncestry.same_lineage_excludes_independence hSame hCredit.1.1

theorem behavioral_nonfactorization_alone_is_insufficient
    {gate : SourceIndependenceGate}
    (hBehavior : gate.behavioralNonfactorization = true)
    (hNotIndependent : ¬ SourceAncestry.Independent gate.left gate.right) :
    ¬ IndependenceSensitiveCredit gate := by
  intro hCredit
  exact hNotIndependent hCredit.1.1

theorem certified_gate_separates_source_and_behavior
    {gate : SourceIndependenceGate}
    (h : IndependenceSensitiveCredit gate) :
    SourceAncestry.Independent gate.left gate.right ∧
    gate.behavioralNonfactorization = true :=
  ⟨h.1.1, h.2⟩

end SourceIndependenceGate

end FoundationsVII
