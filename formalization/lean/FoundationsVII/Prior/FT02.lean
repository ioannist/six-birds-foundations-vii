import FoundationsVII.Prior.Metadata
import SixBirdsFoundationsV.Laws.E5ReclosureCollapse

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsFoundationsV.RepairGeneratorReachabilityRecord
def adapter_ft02_repairgeneratorreachabilityrecord_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-02-01"
    formalizationTarget := "FT02"
    sourceModule := "SixBirdsFoundationsV.Laws.E5ReclosureCollapse"
    sourceDeclaration := "SixBirdsFoundationsV.RepairGeneratorReachabilityRecord"
    sourceType := "structure SixBirdsFoundationsV.RepairGeneratorReachabilityRecord"
    targetType := "FoundationsVII.AdmissionTransition / FoundationsVII.ReachabilityWitness"
    preservedHypotheses := ["explicit reachability record", "exclusive reachability status"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Admission reachability graph and occurrence separation", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

#check SixBirdsFoundationsV.RepairGeneratorReachabilityCertified
def adapter_ft02_repairgeneratorreachabilitycertified_02 : AdapterMetadata :=
  { adapterId := "FVII-ADP-02-02"
    formalizationTarget := "FT02"
    sourceModule := "SixBirdsFoundationsV.Laws.E5ReclosureCollapse"
    sourceDeclaration := "SixBirdsFoundationsV.RepairGeneratorReachabilityCertified"
    sourceType := "structure SixBirdsFoundationsV.RepairGeneratorReachabilityCertified"
    targetType := "FoundationsVII.AdmissionTransition / FoundationsVII.ReachabilityWitness"
    preservedHypotheses := ["explicit reachability record", "exclusive reachability status"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Admission reachability graph and occurrence separation", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
