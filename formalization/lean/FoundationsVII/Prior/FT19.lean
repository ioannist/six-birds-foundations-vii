import FoundationsVII.Prior.Metadata
import SixBirdsMetaMath.FoundationsIV.StatusRecordsCoherence.ObjectPersistence

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsMetaMath.FoundationsIV.StatusRecordsCoherence.ObjectPersistence.persistence_extension_retains_old
def adapter_ft19_persistence_extension_retains_old_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-19-01"
    formalizationTarget := "FT19"
    sourceModule := "SixBirdsMetaMath.FoundationsIV.StatusRecordsCoherence.ObjectPersistence"
    sourceDeclaration := "SixBirdsMetaMath.FoundationsIV.StatusRecordsCoherence.ObjectPersistence.persistence_extension_retains_old"
    sourceType := "theorem SixBirdsMetaMath.FoundationsIV.StatusRecordsCoherence.ObjectPersistence.persistence_extension_retains_old"
    targetType := "retention component of FoundationsVII.JoinCertificate"
    preservedHypotheses := ["old identity and persistence-extension map"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Parent retention and refinement transport", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
