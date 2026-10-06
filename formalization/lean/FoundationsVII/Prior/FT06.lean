import FoundationsVII.Prior.Metadata
import SixBirdsIII.InstrumentClaims

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsIII.InstrumentClaimRecord
def adapter_ft06_instrumentclaimrecord_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-06-01"
    formalizationTarget := "FT06"
    sourceModule := "SixBirdsIII.InstrumentClaims"
    sourceDeclaration := "SixBirdsIII.InstrumentClaimRecord"
    sourceType := "structure SixBirdsIII.InstrumentClaimRecord"
    targetType := "FoundationsVII.ContactWitness"
    preservedHypotheses := ["typed instrument claim and subject/interface ownership"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Typed contact witness", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
