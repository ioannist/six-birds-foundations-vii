
/-!
Vendor note: the meta-math original imports `SixBirdsMetaMath.Terminology`.
That import is intentionally dropped here rather than rewritten because
`Terminology.lean` pulls in the unvendored `ImportedFoundations` and
`FoundationsICompat` dependency chain, which is outside this vendoring unit.
The import is unused in this file: there is no `Terminology`-qualified
reference in the body, and `Terminology.lean` declares no notation or instances
that could apply implicitly.
-/

namespace SixBirdsMetaMath.Xi.StandingHypotheses

/-!
Ξ companion paper §2 "Standing hypotheses: the legal energy quotient".

This section contains only a `remark` environment (null-mode warning);
no `mechanize_now` items. The module is kept as a stub so the Xi axis
umbrella has one module per labeled section.
-/

end SixBirdsMetaMath.Xi.StandingHypotheses
