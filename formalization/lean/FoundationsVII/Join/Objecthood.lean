import FoundationsVII.Join.Entry

/-!
# Proof-carrying composite objecthood

A lawful composite is not obtained from contact or novelty by declaration.  It
is represented by a carrier, a declared closure operation, a fixed-point proof,
and explicit parent embeddings.  This generic witness is independent of the
finite Boolean assay.
-/

namespace FoundationsVII

universe u

structure CompositeClosureWitness (α : Type u) where
  leftParent : List α
  rightParent : List α
  composite : List α
  closure : List α → List α
  leftEmbeds : ∀ x, x ∈ leftParent → x ∈ composite
  rightEmbeds : ∀ x, x ∈ rightParent → x ∈ composite
  fixedPoint : closure composite = composite
  audit : AuditRecord

namespace CompositeClosureWitness

def Objecthood (witness : CompositeClosureWitness α) : Prop :=
  witness.closure witness.composite = witness.composite

def RetainsLeft (witness : CompositeClosureWitness α) : Prop :=
  ∀ x, x ∈ witness.leftParent → x ∈ witness.composite

def RetainsRight (witness : CompositeClosureWitness α) : Prop :=
  ∀ x, x ∈ witness.rightParent → x ∈ witness.composite

def Certified (witness : CompositeClosureWitness α) : Prop :=
  Objecthood witness ∧ RetainsLeft witness ∧ RetainsRight witness ∧
    witness.audit.entries ≠ []

theorem objecthood_from_fixed_point (witness : CompositeClosureWitness α) :
    Objecthood witness := witness.fixedPoint

theorem left_retention_from_embedding (witness : CompositeClosureWitness α) :
    RetainsLeft witness := witness.leftEmbeds

theorem right_retention_from_embedding (witness : CompositeClosureWitness α) :
    RetainsRight witness := witness.rightEmbeds

theorem certified_of_proof_carrying_witness
    (witness : CompositeClosureWitness α)
    (hAudit : witness.audit.entries ≠ []) : Certified witness := by
  exact ⟨witness.fixedPoint, witness.leftEmbeds, witness.rightEmbeds, hAudit⟩

theorem certified_has_objecthood {witness : CompositeClosureWitness α}
    (h : Certified witness) : Objecthood witness := h.1

theorem certified_retains_both_parents {witness : CompositeClosureWitness α}
    (h : Certified witness) : RetainsLeft witness ∧ RetainsRight witness :=
  ⟨h.2.1, h.2.2.1⟩

end CompositeClosureWitness

private def finiteClosure (xs : List Nat) : List Nat := xs

private def finiteCompositeWitness : CompositeClosureWitness Nat :=
  { leftParent := [1]
    rightParent := [2]
    composite := [1, 2]
    closure := finiteClosure
    leftEmbeds := by
      intro x hx
      simp only [List.mem_singleton] at hx
      subst x
      simp
    rightEmbeds := by
      intro x hx
      simp only [List.mem_singleton] at hx
      subst x
      simp
    fixedPoint := rfl
    audit := phase3Audit }

theorem finite_composite_objecthood_control :
    CompositeClosureWitness.Certified finiteCompositeWitness := by
  exact CompositeClosureWitness.certified_of_proof_carrying_witness
    finiteCompositeWitness (by decide)

end FoundationsVII
