import FoundationsVII.Semantics.Join
import FoundationsVII.Semantics.Rewriting

namespace FoundationsVII.Semantics

/-- A real formation event exists, but its Boolean observable does not descend
through a map that forgets the formed state. -/
def formationStep (x y : Bool) : Prop := x = false ∧ y = true

theorem formation_enabled : Star formationStep false true :=
  Star.single ⟨rfl, rfl⟩

theorem enabled_observable_not_descended :
    ¬ FactorsOnImage (fun _ : Bool => ()) (fun x => x) := by
  intro h
  have noSplit := (factorsOnImage_iff_no_split _ _).1 h
  exact noSplit ⟨false, true, rfl, by decide⟩

/-- Both maps retain the parental coordinates, but only the finer map retains
information in the cube's third coordinate. -/
theorem coarse_refinement_loses_cube :
    CommonRefinement cubeJoin.pA cubeJoin.pB
      (fun j => (cubeJoin.pA j, cubeJoin.pB j)) ∧
    ¬ FactorsOnImage (fun j => (cubeJoin.pA j, cubeJoin.pB j)) cubeObservable := by
  constructor
  · exact ⟨id, fun _ => rfl⟩
  · exact cube_strict.2.2

theorem fine_refinement_retains_cube :
    CommonRefinement cubeJoin.pA cubeJoin.pB (fun j => j) ∧
    FactorsOnImage (fun j : Bool × Bool × Bool => j) cubeObservable :=
  identity_refinement_recovers_cube

end FoundationsVII.Semantics
