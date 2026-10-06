namespace SixBirds

inductive Role where
  | P1
  | P2
  | P3
  | P4
  | P5
  | P6
  deriving DecidableEq, Repr

def primitiveRoles : List Role :=
  [Role.P1, Role.P2, Role.P3, Role.P4, Role.P5, Role.P6]

theorem primitiveRoles_length : primitiveRoles.length = 6 := rfl

def RoleMeaning : Role -> String
  | Role.P1 => "update-vs-quotient compatibility / descent obstruction"
  | Role.P2 => "macro-specification representability"
  | Role.P3 => "enriched route/coherence mismatch"
  | Role.P4 => "stage/order/transition/refinement structure"
  | Role.P5 => "quotient packaging / quotienting"
  | Role.P6 => "audit/bookkeeping/provenance/replay/checkability"

inductive Level where
  | behavioral
  | verification
  | structuralCategorical
  deriving DecidableEq, Repr

def levelTrichotomy : List Level :=
  [Level.behavioral, Level.verification, Level.structuralCategorical]

structure LevelProfile where
  role : Role
  behavioral : String
  verification : String
  structuralCategorical : String

structure SelectedLift where
  role : Role
  source : Level
  target : Level
  selected : Bool
  nonUnique : Bool
  addedData : String

structure SelectedLiftAtlas where
  lift : Role -> SelectedLift
  selected : ∀ r, (lift r).selected = true
  nonUnique : ∀ r, (lift r).nonUnique = true

def selectedLift (r : Role) : SelectedLift :=
  { role := r
    source := Level.behavioral
    target := Level.structuralCategorical
    selected := true
    nonUnique := true
    addedData := RoleMeaning r }

def selectedLiftAtlas : SelectedLiftAtlas :=
  { lift := selectedLift
    selected := by
      intro r
      cases r <;> rfl
    nonUnique := by
      intro r
      cases r <;> rfl }

def ForbiddenCollapse (r s : Role) : Prop :=
  r ≠ s

theorem boundary_distinctions :
    ∀ {r s : Role}, r ≠ s -> ForbiddenCollapse r s := by
  intro r s h
  exact h

end SixBirds
