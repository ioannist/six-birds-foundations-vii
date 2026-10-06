import FoundationsVII.Prior.Metadata
import SixBirdsFoundationsV.Definitional.CarriedRecord
import SixBirdsFoundationsV.Laws.E13RepairTransport

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsFoundationsV.CarriedSource
def adapter_ft05_carriedsource_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-05-01"
    formalizationTarget := "FT05"
    sourceModule := "SixBirdsFoundationsV.Definitional.CarriedRecord"
    sourceDeclaration := "SixBirdsFoundationsV.CarriedSource"
    sourceType := "def SixBirdsFoundationsV.CarriedSource"
    targetType := "FoundationsVII.SourceLedger / FoundationsVII.BridgeContract / FoundationsVII.BridgeLedger"
    preservedHypotheses := ["fine source tag", "source/target carrier identity", "declared transport token"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Source and bridge ledger", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

#check SixBirdsFoundationsV.TransportTokenRecord
def adapter_ft05_transporttokenrecord_02 : AdapterMetadata :=
  { adapterId := "FVII-ADP-05-02"
    formalizationTarget := "FT05"
    sourceModule := "SixBirdsFoundationsV.Laws.E13RepairTransport"
    sourceDeclaration := "SixBirdsFoundationsV.TransportTokenRecord"
    sourceType := "structure SixBirdsFoundationsV.TransportTokenRecord"
    targetType := "FoundationsVII.SourceLedger / FoundationsVII.BridgeContract / FoundationsVII.BridgeLedger"
    preservedHypotheses := ["fine source tag", "source/target carrier identity", "declared transport token"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Source and bridge ledger", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
