/-!
G12 Finite Witness Radiation: finite obstruction restriction and orbit
radiation.

This file formalizes the elementary theorem surface from `THEOREMS.md` for
G12. It does not construct a group action, Euclidean geometry, unit-distance
coordinates, SAT certificates, or the de Bruijn-Erdos compactness theorem.
The compactness bridge is represented as a named hypothesis.
-/

universe u

namespace SixBirdsFoundationsVI.Laws.G12FiniteWitnessRadiation

/--
A total proper `k`-coloring of the whole carrier.

The color function takes values in `Nat`; the first conjunct bounds every color
by `< k`, and the second conjunct says adjacent vertices receive distinct
colors.
-/
def ProperKColoring {X : Type u}
    (E : X -> X -> Prop) (k : Nat) (c : X -> Nat) : Prop :=
  (forall x : X, c x < k) /\
    forall x y : X, E x y -> c x ≠ c y

/--
A finite induced-subgraph obstruction.

`FiniteWitnessObstruction E k W` says that the finite list of vertices `W`
cannot be properly colored with colors `< k`, using only the `E`-edges whose
endpoints both lie in `W`.
-/
def FiniteWitnessObstruction {X : Type u}
    (E : X -> X -> Prop) (k : Nat) (W : List X) : Prop :=
  ¬ (exists c : X -> Nat,
    (forall x : X, x ∈ W -> c x < k) /\
      forall x y : X, x ∈ W -> y ∈ W -> E x y -> c x ≠ c y)

/--
The core G12 restriction theorem: a finite non-`k`-colorable induced witness
forbids a global proper `k`-coloring.
-/
theorem no_global_k_coloring {X : Type u}
    (E : X -> X -> Prop) (k : Nat) (W : List X)
    (hwitness : FiniteWitnessObstruction E k W) :
    ¬ (exists c : X -> Nat, ProperKColoring E k c) := by
  intro hglobal
  rcases hglobal with ⟨c, hproper⟩
  rcases hproper with ⟨hbound, hedge⟩
  apply hwitness
  refine ⟨c, ?_, ?_⟩
  · intro x _hx
    exact hbound x
  · intro x y _hx _hy hxy
    exact hedge x y hxy

/--
Faithful abstraction of an automorphism of the graph relation.

The orbit-radiation theorem below only uses the forward implication, but the
full biconditional matches the setup language that `gamma` preserves `E`.
-/
def StructurePreserving {X : Type u}
    (E : X -> X -> Prop) (gamma : X -> X) : Prop :=
  forall x y : X, E x y <-> E (gamma x) (gamma y)

/--
Local replacement for the standard `List.mem_map` helper.
-/
private theorem image_mem_map {X : Type u}
    (gamma : X -> X) (W : List X) {x : X}
    (hx : x ∈ W) : gamma x ∈ W.map gamma := by
  induction W with
  | nil =>
      cases hx
  | cons _ tail ih =>
      cases hx with
      | head =>
          exact List.Mem.head _
      | tail _ htail =>
          exact List.Mem.tail _ (ih htail)

/--
Orbit radiation: a structure-preserving map sends a finite witness to another
finite witness.

No injectivity hypothesis is needed. A coloring of `W.map gamma` pulls back
along `gamma` to a coloring of `W`; the forward direction of preservation sends
each original edge to an edge between the images.
-/
theorem orbit_radiation {X : Type u}
    (E : X -> X -> Prop) (k : Nat) (W : List X)
    (gamma : X -> X) (hpres : StructurePreserving E gamma)
    (hwitness : FiniteWitnessObstruction E k W) :
    FiniteWitnessObstruction E k (W.map gamma) := by
  intro himage
  rcases himage with ⟨cimage, hbound_image, hproper_image⟩
  apply hwitness
  refine ⟨fun x => cimage (gamma x), ?_, ?_⟩
  · intro x hx
    have hmem : gamma x ∈ W.map gamma := image_mem_map gamma W hx
    exact hbound_image (gamma x) hmem
  · intro x y hx hy hxy
    have hx_image : gamma x ∈ W.map gamma := image_mem_map gamma W hx
    have hy_image : gamma y ∈ W.map gamma := image_mem_map gamma W hy
    have hxy_image : E (gamma x) (gamma y) := (hpres x y).mp hxy
    exact hproper_image (gamma x) (gamma y) hx_image hy_image hxy_image

/--
Named imported compactness bridge.

This is the de Bruijn-Erdos graph-coloring compactness commitment as used by
G12: if no global proper `k`-coloring exists, then some finite induced witness
already obstructs `k`-colorability. The bridge is assumed, not proved here.
-/
def CompactnessBridge {X : Type u}
    (E : X -> X -> Prop) (k : Nat) : Prop :=
  (¬ (exists c : X -> Nat, ProperKColoring E k c)) ->
    exists W : List X, FiniteWitnessObstruction E k W

/--
With the compactness bridge named as a hypothesis, finite witnesses are
equivalent to nonexistence of a global proper `k`-coloring.
-/
theorem finite_witness_iff_no_global_coloring {X : Type u}
    (E : X -> X -> Prop) (k : Nat)
    (hbridge : CompactnessBridge E k) :
    (¬ (exists c : X -> Nat, ProperKColoring E k c)) <->
      exists W : List X, FiniteWitnessObstruction E k W := by
  constructor
  · intro hnoglobal
    exact hbridge hnoglobal
  · intro hwitness
    rcases hwitness with ⟨W, hW⟩
    exact no_global_k_coloring E k W hW

end SixBirdsFoundationsVI.Laws.G12FiniteWitnessRadiation
