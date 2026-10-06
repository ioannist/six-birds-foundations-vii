/-!
G11 Local-Rule Global-Anti-Symmetry: abstract period and hierarchy setup.

This file formalizes the abstract theorem surface from `THEOREMS.md` for G11.
It deliberately does not build Wang tiles, subshifts of finite type, finite
regions, or the concrete per-period certificates. Those are calibration/lab
content for a later packet.
-/

namespace SixBirdsFoundationsVI.Laws.G11GlobalAntiSymmetry

/--
A configuration assigns a symbol in `A` to each position in `V`.

In the flagship tiling/SFT instances, `V` stands for a lattice such as `Z^d`
and `A` for a finite alphabet. The abstract theorem does not need to construct
either object.
-/
abbrev Config (V A : Type) := V → A

/--
The declared zero period acts as the identity translation.

This records the setup clause that `P0` is the identity period. The main
aperiodicity proof does not use the identity law directly, but it is kept as
standing typed data for statement fidelity to the prose setup.
-/
def ZeroPeriod {V P : Type} (translate : V → P → V) (P0 : P) : Prop :=
  ∀ v : V, translate v P0 = v

/--
`HasPeriod translate x p` says that `p` is a period of configuration `x`.
-/
def HasPeriod {V P A : Type} (translate : V → P → V)
    (x : Config V A) (p : P) : Prop :=
  ∀ v : V, x (translate v p) = x v

/--
A configuration is aperiodic when every declared period is the zero period.
-/
def Aperiodic {V P A : Type} (translate : V → P → V) (P0 : P)
    (x : Config V A) : Prop :=
  ∀ p : P, HasPeriod translate x p → p = P0

/--
`NonemptyAdmissible` is `[H-G11-nonempty]`: at least one configuration satisfies
the declared local rules.

The predicate `Admissible` stands in for "satisfies all local rules of `C`";
this abstract packet does not construct those local rules from forbidden
patterns.
-/
def NonemptyAdmissible {V A : Type} (Admissible : Config V A → Prop) : Prop :=
  ∃ x : Config V A, Admissible x

/--
`[H-G11-hierarchy]`, in abstract constructive form.

For every admissible configuration and every candidate period, the forced
hierarchy either identifies the candidate as the zero period or supplies some
scale whose forced block/marker structure breaks that period. This is the
option-(b) encoding from the packet: `Scale` and `BreaksAt` preserve the prose's
"some scale k" hierarchy shape, while the disjunction avoids adding a global
decidable equality assumption for arbitrary period types.
-/
def Hierarchy {V P A Scale : Type} (P0 : P)
    (Admissible : Config V A → Prop)
    (BreaksAt : Config V A → Scale → P → Prop) : Prop :=
  ∀ x : Config V A, Admissible x →
    ∀ p : P, p = P0 ∨ ∃ k : Scale, BreaksAt x k p

/--
Forced scale breaks rule out period invariance.

This is the abstract version of "the hierarchy is locally forced by the rules of
`C`": if an admissible configuration has a forced scale-level break for `p`,
then `p` cannot be an actual period of that configuration.
-/
def ForcedBreaksPeriod {V P A Scale : Type} (translate : V → P → V)
    (Admissible : Config V A → Prop)
    (BreaksAt : Config V A → Scale → P → Prop) : Prop :=
  ∀ (x : Config V A) (k : Scale) (p : P),
    Admissible x → BreaksAt x k p → ¬ HasPeriod translate x p

/--
Part (a) of the G11 theorem: admissible configurations exist by
`[H-G11-nonempty]`.
-/
theorem admissible_configurations_exist {V A : Type}
    {Admissible : Config V A → Prop}
    (hnonempty : NonemptyAdmissible Admissible) :
    ∃ x : Config V A, Admissible x :=
  hnonempty

/--
Part (b) of the G11 theorem: hierarchy plus forced-break soundness makes every
admissible configuration aperiodic.

The zero-period identity hypothesis is part of G11's setup and is therefore
carried in the signature, although this packaging proof only needs the hierarchy
and forced-break clauses.
-/
theorem hierarchy_forces_aperiodic {V P A Scale : Type}
    {translate : V → P → V} {P0 : P}
    {Admissible : Config V A → Prop}
    {BreaksAt : Config V A → Scale → P → Prop}
    (_hzero : ZeroPeriod translate P0)
    (hhierarchy : Hierarchy P0 Admissible BreaksAt)
    (hforced : ForcedBreaksPeriod translate Admissible BreaksAt) :
    ∀ x : Config V A, Admissible x → Aperiodic translate P0 x := by
  intro x hx p hperiod
  rcases hhierarchy x hx p with hzero | hbreak
  · exact hzero
  · rcases hbreak with ⟨k, hk⟩
    exact False.elim (hforced x k p hx hk hperiod)

/--
Combined G11 theorem surface: `[H-G11-nonempty]` gives existence, and
`[H-G11-hierarchy]` plus forced-break soundness gives universal aperiodicity.
-/
theorem g11_global_anti_symmetry {V P A Scale : Type}
    {translate : V → P → V} {P0 : P}
    {Admissible : Config V A → Prop}
    {BreaksAt : Config V A → Scale → P → Prop}
    (hzero : ZeroPeriod translate P0)
    (hhierarchy : Hierarchy P0 Admissible BreaksAt)
    (hforced : ForcedBreaksPeriod translate Admissible BreaksAt)
    (hnonempty : NonemptyAdmissible Admissible) :
    (∃ x : Config V A, Admissible x) ∧
      (∀ x : Config V A, Admissible x → Aperiodic translate P0 x) :=
  ⟨admissible_configurations_exist hnonempty,
    hierarchy_forces_aperiodic hzero hhierarchy hforced⟩

end SixBirdsFoundationsVI.Laws.G11GlobalAntiSymmetry
