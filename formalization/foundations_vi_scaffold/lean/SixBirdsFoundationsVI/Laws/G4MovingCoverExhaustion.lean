/-!
G4 Moving-Cover Exhaustion: abstract cover/certificate schemas.

This file formalizes the layer-agnostic setup from `THEOREMS.md` for G4. It
does not construct Fibonacci-Sylvester Egyptian-fraction covers,
Erdos-Straus instances, or concrete numerator-descent budgets; those are
calibration and lab content.
-/

namespace SixBirdsFoundationsVI.Laws.G4MovingCoverExhaustion

/--
`[H-G4-sound]`: every declared patch proves the target on every index in its
region.

`R alpha t` means target index `t` lies in the region covered by patch
`alpha`. The certificate data itself is abstracted away; its only used
consequence is `P t`.
-/
def Sound {T Alpha : Type} (P : T → Prop)
    (R : Alpha → T → Prop) : Prop :=
  ∀ (alpha : Alpha) (t : T), R alpha t → P t

/--
`[H-G4-exhaust]`, reduced to the consequence used by the positive schema:
every target index is covered by some patch.

The prose allows global staged audits and pointwise residual audits. Concrete
staging/residual bookkeeping is instance data; the abstract theorem only needs
this coverage surface.
-/
def Exhausted {T Alpha : Type} (R : Alpha → T → Prop) : Prop :=
  ∀ t : T, ∃ alpha : Alpha, R alpha t

/--
G4 positive schema: sound patches plus an exhaustion audit close every target.

For each `t`, the exhaustion audit supplies a covering patch `alpha`; soundness
then turns `R alpha t` into `P t`.
-/
theorem positive_schema {T Alpha : Type} {P : T → Prop}
    {R : Alpha → T → Prop}
    (hsound : Sound P R) (hexhaust : Exhausted R) :
    ∀ t : T, P t := by
  intro t
  rcases hexhaust t with ⟨alpha, hregion⟩
  exact hsound alpha t hregion

/--
`[H-G4-language-complete]`: if the target family is actually closed, then the
declared certificate language can express that closure as an exhaustion audit.

This is a separate meta-hypothesis about the chosen patch language. It is not
inferred from patch soundness.
-/
def LanguageComplete {T Alpha : Type} (R : Alpha → T → Prop)
    (P : T → Prop) : Prop :=
  (∀ t : T, P t) → Exhausted R

/--
G4 conditional biconditional: relative to soundness and language completeness,
target closure is equivalent to existence of an exhaustion certificate in the
declared language.

The forward direction is exactly language completeness; the reverse direction
is the positive schema.
-/
theorem conditional_biconditional {T Alpha : Type} {P : T → Prop}
    {R : Alpha → T → Prop}
    (hsound : Sound P R) (hlanguage : LanguageComplete R P) :
    (∀ t : T, P t) ↔ Exhausted R := by
  constructor
  · intro hclosed
    exact hlanguage hclosed
  · intro hexhaust
    exact positive_schema hsound hexhaust

/--
`[H-G4-fixed-leak]`: every finite package drawn from the restricted patch
class `C` misses some target.

Finite subfamilies are represented by core Lean `List Alpha` membership,
keeping this file Mathlib-free.
-/
def FixedLeak {T Alpha : Type} (C : Alpha → Prop)
    (R : Alpha → T → Prop) : Prop :=
  ∀ l : List Alpha, (∀ alpha : Alpha, alpha ∈ l → C alpha) →
    ∃ t : T, ∀ alpha : Alpha, alpha ∈ l → ¬ R alpha t

/--
G4 fixed-package no-go schema: under a fixed-package leak hypothesis, no finite
list of patches from the restricted class `C` covers all targets.

The no-go is scoped to the declared restricted class. It does not rule out
moving covers or richer certificate languages outside `C`.
-/
theorem fixed_package_no_go {T Alpha : Type} {C : Alpha → Prop}
    {R : Alpha → T → Prop}
    (hleak : FixedLeak C R) (l : List Alpha)
    (hl : ∀ alpha : Alpha, alpha ∈ l → C alpha) :
    ¬ (∀ t : T, ∃ alpha : Alpha, alpha ∈ l ∧ R alpha t) := by
  intro hcover
  rcases hleak l hl with ⟨t, hmiss⟩
  rcases hcover t with ⟨alpha, halpha, hregion⟩
  exact hmiss alpha halpha hregion

end SixBirdsFoundationsVI.Laws.G4MovingCoverExhaustion
