import FoundationsVII.Core.Protocols

/-!
# Structural constructor non-collapse

These are finite constructor facts only.  They are not implication laws between
soundness, executability, reachability, firing, occurrence, contact, or join.
-/

namespace FoundationsVII

theorem interaction_statuses_pairwise_distinct :
    allInteractionStatuses.eraseDups.length = 6 := by decide

theorem claim_grades_pairwise_distinct :
    allClaimGrades.eraseDups.length = 7 := by decide

theorem evidence_grades_pairwise_distinct :
    allEvidenceGrades.eraseDups.length = 7 := by decide

theorem negative_evidence_grades_pairwise_distinct :
    allNegativeEvidenceGrades.eraseDups.length = 4 := by decide

theorem negative_scopes_pairwise_distinct :
    allNegativeScopes.eraseDups.length = 4 := by decide

theorem witnessed_contact_ne_strict_join :
    InteractionStatus.witnessedContact ≠ InteractionStatus.strictJoin := by decide

theorem composite_formed_ne_strict_join :
    InteractionStatus.compositeFormed ≠ InteractionStatus.strictJoin := by decide

theorem finite_external_ne_theorem_backed :
    EvidenceGrade.exhaustiveFiniteExternal ≠ EvidenceGrade.theoremBacked := by decide

theorem finite_lean_ne_theorem_backed :
    EvidenceGrade.exhaustiveFiniteLean ≠ EvidenceGrade.theoremBacked := by decide

end FoundationsVII
