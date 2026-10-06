import FoundationsVII.Prior.Metadata
import SixBirdsFoundationsV.Laws.E5ReclosureCollapse

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsFoundationsV.RepairGeneratorReachabilityRecord
def adapter_ft11_repairgeneratorreachabilityrecord_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-11-01"
    formalizationTarget := "FT11"
    sourceModule := "SixBirdsFoundationsV.Laws.E5ReclosureCollapse"
    sourceDeclaration := "SixBirdsFoundationsV.RepairGeneratorReachabilityRecord"
    sourceType := "structure SixBirdsFoundationsV.RepairGeneratorReachabilityRecord"
    targetType := "FoundationsVII.EnablementRecord"
    preservedHypotheses := ["declared reachability record and scope"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Enablement record", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
