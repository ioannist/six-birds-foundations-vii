import FoundationsVII.Prior.Metadata
import SixBirdsFoundationsV.Definitional.RepairJoin

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsFoundationsV.repairJoin
def adapter_ft07_repairjoin_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-07-01"
    formalizationTarget := "FT07"
    sourceModule := "SixBirdsFoundationsV.Definitional.RepairJoin"
    sourceDeclaration := "SixBirdsFoundationsV.repairJoin"
    sourceType := "def SixBirdsFoundationsV.repairJoin"
    targetType := "FoundationsVII.JoinCertificate"
    preservedHypotheses := ["declared repair-join inputs", "well-definedness premises"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Join certificate normal form", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

#check SixBirdsFoundationsV.join_well_defined
def adapter_ft07_join_well_defined_02 : AdapterMetadata :=
  { adapterId := "FVII-ADP-07-02"
    formalizationTarget := "FT07"
    sourceModule := "SixBirdsFoundationsV.Definitional.RepairJoin"
    sourceDeclaration := "SixBirdsFoundationsV.join_well_defined"
    sourceType := "theorem SixBirdsFoundationsV.join_well_defined"
    targetType := "FoundationsVII.JoinCertificate"
    preservedHypotheses := ["declared repair-join inputs", "well-definedness premises"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Join certificate normal form", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
