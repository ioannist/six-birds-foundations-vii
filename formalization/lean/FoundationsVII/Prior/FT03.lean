import FoundationsVII.Prior.Metadata
import SixBirdsFoundationsV.Laws.E1Internalization

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsFoundationsV.NoReachableRepairGenerator
def adapter_ft03_noreachablerepairgenerator_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-03-01"
    formalizationTarget := "FT03"
    sourceModule := "SixBirdsFoundationsV.Laws.E1Internalization"
    sourceDeclaration := "SixBirdsFoundationsV.NoReachableRepairGenerator"
    sourceType := "def SixBirdsFoundationsV.NoReachableRepairGenerator"
    targetType := "bootstrap obstruction over FoundationsVII.AdmissionTransition"
    preservedHypotheses := ["declared carrier and horizon", "absence of reachable repair generator"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Bootstrap obstruction", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
