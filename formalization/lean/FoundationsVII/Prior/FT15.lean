import FoundationsVII.Prior.Metadata
import HolonomyMemory.Asymmetry

/-! Generated exact inherited-adapter anchors. Metadata is not semantic equivalence. -/

namespace FoundationsVII.Prior

#check HolonomyMemory.LoopAsymmetry
def adapter_ft15_loopasymmetry_01 : AdapterMetadata :=
  { adapterId := "FVII-ADP-15-01"
    formalizationTarget := "FT15"
    sourceModule := "HolonomyMemory.Asymmetry"
    sourceDeclaration := "HolonomyMemory.LoopAsymmetry"
    sourceType := "def HolonomyMemory.LoopAsymmetry"
    targetType := "holonomy/arrow-separated FoundationsVII.InteractionRecord"
    preservedHypotheses := ["loop, quotient, and current/predictive interfaces"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Interaction holonomy/arrow separation", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

#check HolonomyMemory.loopAsymmetry_exhibits_movedPredictive_fixedCurrent
def adapter_ft15_loopasymmetry_exhibits_movedpredictive_fixedcurrent_02 : AdapterMetadata :=
  { adapterId := "FVII-ADP-15-02"
    formalizationTarget := "FT15"
    sourceModule := "HolonomyMemory.Asymmetry"
    sourceDeclaration := "HolonomyMemory.loopAsymmetry_exhibits_movedPredictive_fixedCurrent"
    sourceType := "theorem HolonomyMemory.loopAsymmetry_exhibits_movedPredictive_fixedCurrent"
    targetType := "holonomy/arrow-separated FoundationsVII.InteractionRecord"
    preservedHypotheses := ["loop, quotient, and current/predictive interfaces"]
    addedHypotheses := ["VII-owned source, audit, and disposition fields for Interaction holonomy/arrow separation", "explicit accepted bridge before semantic reuse"]
    lostHypotheses := ["none silently; unmatched inherited fields remain outside the adapter conclusion"]
    trustDependencies := ["exact imported declaration; theorem-level axioms are separately audited"] }

end FoundationsVII.Prior
