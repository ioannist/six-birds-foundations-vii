/-!
F3 Holonomy-Memory Repair Normal Form.

Route residue has no unallocated status: if two route outcomes are invisible
to the current quotient `Q` but distinguished by future probes on the
predictive quotient `M`, then the route forces memory. The canonical repair is
the promotion from the current quotient to the predictive quotient.
-/

namespace SixBirdsMetaMath.FoundationsIV.Transport.HolonomyMemoryRepair

/-- Two route handles are indistinguishable by every current-quotient probe. -/
def CurrentQInvisible {Route Q : Type} (currentVisible : Route → Q → Prop)
    (r₁ r₂ : Route) : Prop :=
  ∀ q : Q, currentVisible r₁ q ↔ currentVisible r₂ q

/-- Two route handles are distinguished by at least one predictive-quotient
future probe. -/
def FutureMVisible {Route M : Type} (futureVisible : Route → M → Prop)
    (r₁ r₂ : Route) : Prop :=
  ∃ m : M, futureVisible r₁ m ≠ futureVisible r₂ m

/-- Hidden route residue: current-invisible, future-visible route difference. -/
def HiddenRouteResidue {Route Q M : Type}
    (currentVisible : Route → Q → Prop) (futureVisible : Route → M → Prop)
    (r₁ r₂ : Route) : Prop :=
  CurrentQInvisible currentVisible r₁ r₂ ∧ FutureMVisible futureVisible r₁ r₂

/-- A memory witness is a route with some hidden route-residue mate. -/
def MemoryWitness {Route Q M : Type}
    (currentVisible : Route → Q → Prop) (futureVisible : Route → M → Prop)
    (route : Route) : Prop :=
  ∃ other : Route, HiddenRouteResidue currentVisible futureVisible route other

/--
The predictive repair witness records the same hidden route residue at the
`M`-level, together with the fact that the predictive witness has a current
shadow through `π : M -> Q`.
-/
def PredictiveRepairWitness {Route Q M : Type} (π : M → Q)
    (currentVisible : Route → Q → Prop) (futureVisible : Route → M → Prop)
    (r₁ r₂ : Route) : Prop :=
  CurrentQInvisible currentVisible r₁ r₂ ∧
    ∃ m : M,
      futureVisible r₁ m ≠ futureVisible r₂ m ∧
        (currentVisible r₁ (π m) ↔ currentVisible r₂ (π m))

/-- Hidden route residue always supplies the predictive repair witness. -/
theorem hidden_residue_gives_predictive_repair {Route Q M : Type} (π : M → Q)
    (currentVisible : Route → Q → Prop) (futureVisible : Route → M → Prop)
    {r₁ r₂ : Route} :
    HiddenRouteResidue currentVisible futureVisible r₁ r₂ →
      PredictiveRepairWitness π currentVisible futureVisible r₁ r₂ := by
  intro h
  rcases h with ⟨hcurrent, ⟨m, hfuture⟩⟩
  exact ⟨hcurrent, ⟨m, hfuture, hcurrent (π m)⟩⟩

/-- A predictive repair witness forgets back to hidden route residue. -/
theorem predictive_repair_gives_hidden_residue {Route Q M : Type} (π : M → Q)
    (currentVisible : Route → Q → Prop) (futureVisible : Route → M → Prop)
    {r₁ r₂ : Route} :
    PredictiveRepairWitness π currentVisible futureVisible r₁ r₂ →
      HiddenRouteResidue currentVisible futureVisible r₁ r₂ := by
  intro h
  rcases h with ⟨hcurrent, ⟨m, hfuture, _hshadow⟩⟩
  exact ⟨hcurrent, ⟨m, hfuture⟩⟩

/--
Holonomy-Memory Repair Normal Form: a route forces memory exactly when it has
a current-invisible mate that is visible to the predictive quotient. The
comparison map `π : M -> Q` records that the M-level repair still has a
current quotient shadow.
-/
theorem holonomy_memory_repair_normal_form {Route Q M : Type} (π : M → Q)
    (currentVisible : Route → Q → Prop) (futureVisible : Route → M → Prop)
    (route : Route) :
    MemoryWitness currentVisible futureVisible route ↔
      ∃ r₁ r₂ : Route,
        r₁ = route ∧
          PredictiveRepairWitness π currentVisible futureVisible r₁ r₂ := by
  constructor
  · intro hmemory
    rcases hmemory with ⟨other, hhidden⟩
    exact ⟨route, other, rfl,
      hidden_residue_gives_predictive_repair π currentVisible futureVisible hhidden⟩
  · intro hrepair
    rcases hrepair with ⟨r₁, r₂, hroute, hpredictive⟩
    subst hroute
    exact ⟨r₂,
      predictive_repair_gives_hidden_residue π currentVisible futureVisible hpredictive⟩

end SixBirdsMetaMath.FoundationsIV.Transport.HolonomyMemoryRepair
