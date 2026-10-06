import FoundationsVII.Prior.Metadata
import SixBirdsFoundationsV.Laws.E1Internalization

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsFoundationsV.NoReachableRepairGeneratorExcludesEndogenousFamily
def adapter_ft12_noreachablerepairgeneratorexcludesendogenousfamily_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-12-01"
    formalizationTarget := "FT12"
    sourceModule := "SixBirdsFoundationsV.Laws.E1Internalization"
    sourceDeclaration := "SixBirdsFoundationsV.NoReachableRepairGeneratorExcludesEndogenousFamily"
    sourceType := "def SixBirdsFoundationsV.NoReachableRepairGeneratorExcludesEndogenousFamily"
    targetType := "endogenous-source criterion over FoundationsVII.EnablementRecord"
    preservedHypotheses := ["absence of reachable generator under the inherited criterion"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Endogenous generator criterion", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
