import FoundationsVII.Prior.Metadata
import SixBirds.Admissibility
import SixBirdsFoundationsV.Laws.E6E9PricedAccess

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirds.ClaimRecord
def adapter_ft01_claimrecord_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-01-01"
    formalizationTarget := "FT01"
    sourceModule := "SixBirds.Admissibility"
    sourceDeclaration := "SixBirds.ClaimRecord"
    sourceType := "structure SixBirds.ClaimRecord"
    targetType := "FoundationsVII.DomainState / graded access status"
    preservedHypotheses := ["typed claim/access coordinates", "declared audit scope"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Finite access-status data model", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

#check SixBirdsFoundationsV.AccessPolicy
def adapter_ft01_accesspolicy_02 : AdapterMetadata :=
  { adapterId := "FVII-ADP-01-02"
    formalizationTarget := "FT01"
    sourceModule := "SixBirdsFoundationsV.Laws.E6E9PricedAccess"
    sourceDeclaration := "SixBirdsFoundationsV.AccessPolicy"
    sourceType := "structure SixBirdsFoundationsV.AccessPolicy"
    targetType := "FoundationsVII.DomainState / graded access status"
    preservedHypotheses := ["typed claim/access coordinates", "declared audit scope"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Finite access-status data model", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
