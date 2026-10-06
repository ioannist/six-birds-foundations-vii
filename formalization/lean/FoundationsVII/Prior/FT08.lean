import FoundationsVII.Prior.Metadata
import SixBirdsFoundationsV.Laws.E1Internalization

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsFoundationsV.StrictSelfExtension
def adapter_ft08_strictselfextension_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-08-01"
    formalizationTarget := "FT08"
    sourceModule := "SixBirdsFoundationsV.Laws.E1Internalization"
    sourceDeclaration := "SixBirdsFoundationsV.StrictSelfExtension"
    sourceType := "structure SixBirdsFoundationsV.StrictSelfExtension"
    targetType := "strictness component of FoundationsVII.JoinCertificate"
    preservedHypotheses := ["strict self-extension/nonfactorization witness"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Anti-product/nonfactorization witness", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
