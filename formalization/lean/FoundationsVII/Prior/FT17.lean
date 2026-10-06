import FoundationsVII.Prior.Metadata
import SixBirds.Admissibility

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirds.AdmissibleClaim
def adapter_ft17_admissibleclaim_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-17-01"
    formalizationTarget := "FT17"
    sourceModule := "SixBirds.Admissibility"
    sourceDeclaration := "SixBirds.AdmissibleClaim"
    sourceType := "def SixBirds.AdmissibleClaim"
    targetType := "FoundationsVII.AuditRecord / GradedClaim / NegativeEvidenceRecord"
    preservedHypotheses := ["claim bookkeeping, grade, and explicit nonclaims"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Negative quantifier and claim-grade rules", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

#check SixBirds.NonclaimRecord
def adapter_ft17_nonclaimrecord_02 : AdapterMetadata :=
  { adapterId := "FVII-ADP-17-02"
    formalizationTarget := "FT17"
    sourceModule := "SixBirds.Admissibility"
    sourceDeclaration := "SixBirds.NonclaimRecord"
    sourceType := "structure SixBirds.NonclaimRecord"
    targetType := "FoundationsVII.AuditRecord / GradedClaim / NegativeEvidenceRecord"
    preservedHypotheses := ["claim bookkeeping, grade, and explicit nonclaims"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Negative quantifier and claim-grade rules", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
