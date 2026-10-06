import ClosureLadder

/-!
Foundations I import surface for needles.

The vendored Foundations I Lean track is locally adapted to Lean
v4.28.0 with mathlib stripped (see
`vendor/foundations/foundations-i-adaptation.md`). This module exposes
a stable needles-facing alias surface over the canonical `ClosureLadder`
declarations. F2 and F3 are imported directly via `Terminology`; only
F1 needs a Compat layer.
-/

namespace SixBirdsMetaMath

abbrev F1ClosureOp := ClosureOp
abbrev F1ClosureLadder := ClosureLadder
abbrev F1IdempotentEndo := ClosureLadder.IdempotentEndo

def F1PackagingPack {α β} (f : α → β) :=
  ClosureLadder.MetaPackaging.pack f

end SixBirdsMetaMath
