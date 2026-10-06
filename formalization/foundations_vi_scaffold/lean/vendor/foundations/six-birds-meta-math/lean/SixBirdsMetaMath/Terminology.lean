import SixBirdsMetaMath.ImportedFoundations
import SixBirdsMetaMath.FoundationsICompat

/-!
Needles paper-facing terminology.

Primary source: `paper/notation_and_terminology.md`.

This module aliases Foundations II and III declarations into a stable
`SixBirdsMetaMath.*` surface. Per the governance doc, no needles-local
status families are declared yet; if mechanization requires one,
declare it here and in the governance doc simultaneously.
-/

namespace SixBirdsMetaMath

-- Foundations II surface
abbrev F2Role := SixBirds.Role
abbrev F2FATCD := SixBirds.FATCD
abbrev F2ChannelStatus := SixBirds.ChannelStatus
abbrev F2ScopedExactSix := SixBirds.scoped_exact_six
theorem F2TypedNonCollapse {r s : SixBirds.Role} :
    r ≠ s → SixBirds.ForbiddenCollapse r s :=
  SixBirds.typed_non_collapse

-- Foundations III surface
abbrev F3BirdIntDomain := SixBirdsIII.BirdIntDomain
abbrev F3Primitive := SixBirdsIII.Primitive
abbrev F3Level := SixBirdsIII.Level
abbrev F3Host := SixBirdsIII.Host
abbrev F3PromotionStatus := SixBirdsIII.PromotionStatus
abbrev F3ClaimStatus := SixBirdsIII.ClaimStatus
abbrev F3GateStatus := SixBirdsIII.GateStatus
abbrev F3StrictGateStatus := SixBirdsIII.StrictGateStatus
abbrev F3SqStatus := SixBirdsIII.SqStatus
abbrev F3PromotionBridgeRecord := SixBirdsIII.PromotionBridgeRecord
abbrev F3ClaimRecord := SixBirdsIII.ClaimRecord
abbrev F3DefectRecord := SixBirdsIII.DefectRecord
abbrev F3DirectedCellRecord := SixBirdsIII.DirectedCellRecord
abbrev F3TopDownChannelRecord := SixBirdsIII.TopDownChannelRecord
abbrev F3ThresholdTag := SixBirdsIII.ThresholdTag
abbrev F3VisibilityTag := SixBirdsIII.VisibilityTag

end SixBirdsMetaMath
