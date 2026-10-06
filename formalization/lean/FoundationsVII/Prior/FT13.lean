import FoundationsVII.Prior.Metadata
import SixBirdsIII.HighStructure

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsIII.descent_square_recovery
def adapter_ft13_descent_square_recovery_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-13-01"
    formalizationTarget := "FT13"
    sourceModule := "SixBirdsIII.HighStructure"
    sourceDeclaration := "SixBirdsIII.descent_square_recovery"
    sourceType := "theorem SixBirdsIII.descent_square_recovery"
    targetType := "transmission/descent fidelity over FoundationsVII.EnablementRecord"
    preservedHypotheses := ["descent-square maps and recovery premise"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Transmission/descent fidelity", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
