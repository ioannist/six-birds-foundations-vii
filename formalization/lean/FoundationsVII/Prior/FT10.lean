import FoundationsVII.Prior.Metadata
import SixBirdsFoundationsV.Laws.E11InstitutionalRewrite

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check SixBirdsFoundationsV.E11_NCTDObstruction
def adapter_ft10_e11_nctdobstruction_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-10-01"
    formalizationTarget := "FT10"
    sourceModule := "SixBirdsFoundationsV.Laws.E11InstitutionalRewrite"
    sourceDeclaration := "SixBirdsFoundationsV.E11_NCTDObstruction"
    sourceType := "theorem SixBirdsFoundationsV.E11_NCTDObstruction"
    targetType := "FoundationsVII.NonInteractionCertificate"
    preservedHypotheses := ["the original institutional rewrite hypotheses and covered carrier"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Coverage-qualified non-interaction certificate", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
