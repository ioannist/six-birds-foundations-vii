import FoundationsVII.Prior.Metadata
import SixBirdsMetaMath.FoundationsIV.Access.NoFreeDistinction

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsMetaMath.FoundationsIV.Access.NoFreeDistinction.financed_refinement_retains_access
def adapter_ft18_financed_refinement_retains_access_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-18-01"
    formalizationTarget := "FT18"
    sourceModule := "SixBirdsMetaMath.FoundationsIV.Access.NoFreeDistinction"
    sourceDeclaration := "SixBirdsMetaMath.FoundationsIV.Access.NoFreeDistinction.financed_refinement_retains_access"
    sourceType := "theorem SixBirdsMetaMath.FoundationsIV.Access.NoFreeDistinction.financed_refinement_retains_access"
    targetType := "no-free access/join protocol records"
    preservedHypotheses := ["old access retention and financed refinement map"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for No-free-access/no-free-join lemmas", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
