import SixBirdsMetaMath.FoundationsIV.Stability.SufficiencyClosure

/-!
F10 Quotientality / Layer-Sameness.

Layer access is quotient access. A lawful instrument induces a current
signature map `qI`; two carrier states are the same layer object exactly when
`qI` identifies them. Current-visible expressions are precisely those that
factor through this access quotient.
-/

namespace SixBirdsMetaMath.FoundationsIV.Access.Quotientality

open SixBirdsMetaMath.FoundationsIV.Stability.SufficiencyClosure

/-- A lawful observation signature: a declared family of observables, packaged
as a single current signature map on the closure carrier. -/
structure ObservationSignature (H : Type) where
  Sig : Type
  sigmaI : H → Sig

/-- The kernel relation induced by the observation signature. -/
def accessKernel {H : Type} (S : ObservationSignature H) (h h' : H) : Prop :=
  S.sigmaI h = S.sigmaI h'

/-- The canonical access quotient induced by an observation signature. -/
def AccessQuotient {H : Type} (S : ObservationSignature H) : Type :=
  Quot (accessKernel S)

/-- The canonical quotient map from carrier states to access classes. -/
def qI {H : Type} (S : ObservationSignature H) : H → AccessQuotient S :=
  Quot.mk (accessKernel S)

/-- The signature descends back out of the canonical access quotient. -/
def accessSignature {H : Type} (S : ObservationSignature H) :
    AccessQuotient S → S.Sig :=
  Quot.lift S.sigmaI (fun _ _ h => h)

/-- The canonical quotient is exactly the kernel of the observation signature. -/
theorem qI_eq_iff_accessKernel {H : Type} (S : ObservationSignature H)
    (x y : H) :
    qI S x = qI S y ↔ accessKernel S x y := by
  constructor
  · intro h
    exact congrArg (accessSignature S) h
  · intro h
    exact Quot.sound h

/-- The canonical access quotient is reachable by construction. -/
theorem qI_surjective {H : Type} (S : ObservationSignature H) :
    Function.Surjective (qI S) := by
  intro z
  refine Quot.inductionOn z ?_
  intro h
  exact ⟨h, rfl⟩

/-- An observable is lawful for the signature when it is constant on signature
fibers. -/
def LawfulObservable {H R : Type} (S : ObservationSignature H) (o : H → R) :
    Prop :=
  ∀ h h' : H, accessKernel S h h' → o h = o h'

/-- Factoring uniquely through the canonical access quotient. -/
def ObservableFactorsUniquely {H R : Type} (S : ObservationSignature H)
    (o : H → R) : Prop :=
  ∃ obar : AccessQuotient S → R,
    obar ∘ qI S = o ∧
      ∀ obar' : AccessQuotient S → R, obar' ∘ qI S = o → obar' = obar

/-- A declared quotient carries the observation signature when the signature
factors through it. -/
def CarriesObservationSignature {H Q : Type} (S : ObservationSignature H)
    (π : H → Q) : Prop :=
  ∃ sigBar : Q → S.Sig, sigBar ∘ π = S.sigmaI

/-- Layer-sameness induced by the canonical access quotient. -/
def LayerSame {H QI : Type} (qI : H → QI) (x y : H) : Prop :=
  qI x = qI y

/-- A current-visible expression is constant on access-quotient fibers. -/
def CurrentVisible {H QI W : Type} (qI : H → QI) (expr : H → W) : Prop :=
  PackageClosed qI expr

/-- A current-visible expression factors through the access quotient. -/
def FactorsThroughAccess {H QI W : Type} (qI : H → QI) (expr : H → W) : Prop :=
  FactorsThroughQ qI expr

/-- The declared quotient loses a distinction visible to the access quotient. -/
def VisibleLossPair {H Q QI : Type} (q : H → Q) (qI : H → QI) :
    (H × H) → Prop :=
  fun pair => q pair.1 = q pair.2 ∧ qI pair.1 ≠ qI pair.2

/-- The declared quotient carries a distinction invisible to the instrument. -/
def GhostDistinctionPair {H Q QI : Type} (q : H → Q) (qI : H → QI) :
    (H × H) → Prop :=
  fun pair => qI pair.1 = qI pair.2 ∧ q pair.1 ≠ q pair.2

/-- No access-visible distinction is lost by the declared quotient. -/
def NoVisibleLoss {H Q QI : Type} (q : H → Q) (qI : H → QI) : Prop :=
  ∀ x y : H, q x = q y → qI x = qI y

/-- No current-invisible ghost distinction is carried by the declared quotient. -/
def NoGhostDistinction {H Q QI : Type} (q : H → Q) (qI : H → QI) : Prop :=
  ∀ x y : H, qI x = qI y → q x = q y

/-- Common refinement repair preserving the declared quotient and the actual
access quotient. -/
def commonAccessRefinement {H Q QI : Type} (q : H → Q) (qI : H → QI) :
    H → Q × QI :=
  fun h => (q h, qI h)

/-- Every lawful observable factors uniquely through the canonical access
quotient. -/
theorem observable_factorization {H R : Type} (S : ObservationSignature H)
    (o : H → R) (hlawful : LawfulObservable S o) :
    ObservableFactorsUniquely S o := by
  let obar : AccessQuotient S → R :=
    Quot.lift o (fun a b h => hlawful a b h)
  refine ⟨obar, ?_, ?_⟩
  · funext h
    rfl
  · intro obar' hobar'
    funext z
    refine Quot.inductionOn z ?_
    intro h
    have hval : obar' (qI S h) = o h := congrFun hobar' h
    change obar' (qI S h) = obar (qI S h)
    exact hval

/-- Coarsest-quotient property: any reachable quotient carrying the declared
observation signature refines the canonical access quotient. -/
theorem qI_is_coarsest {H Q : Type} (S : ObservationSignature H) (π : H → Q)
    (hπ : Function.Surjective π) (hcarries : CarriesObservationSignature S π) :
    ∃ collapse : Q → AccessQuotient S, collapse ∘ π = qI S := by
  classical
  rcases hcarries with ⟨sigBar, hsigBar⟩
  let collapse : Q → AccessQuotient S :=
    fun z => qI S (Classical.choose (hπ z))
  refine ⟨collapse, ?_⟩
  funext h
  unfold collapse Function.comp
  let h0 : H := Classical.choose (hπ (π h))
  have hh0 : π h0 = π h := Classical.choose_spec (hπ (π h))
  have hsig : accessKernel S h0 h := by
    calc
      S.sigmaI h0 = sigBar (π h0) := (congrFun hsigBar h0).symm
      _ = sigBar (π h) := by rw [hh0]
      _ = S.sigmaI h := congrFun hsigBar h
  exact Quot.sound hsig

/-- Exact comparison form: if a quotient carries the signature and has no ghost
distinctions beyond access, then the two quotient maps factor through each
other. -/
theorem qI_exact_comparison {H Q : Type} (S : ObservationSignature H)
    (π : H → Q) (hπ : Function.Surjective π)
    (hcarries : CarriesObservationSignature S π)
    (hnoGhost : NoGhostDistinction π (qI S)) :
    (∃ collapse : Q → AccessQuotient S, collapse ∘ π = qI S) ∧
      ∃ refine : AccessQuotient S → Q, refine ∘ qI S = π := by
  constructor
  · exact qI_is_coarsest S π hπ hcarries
  · let refine : AccessQuotient S → Q :=
      Quot.lift π (fun a b h => hnoGhost a b (Quot.sound h))
    refine ⟨refine, ?_⟩
    funext h
    rfl

/-- Four statuses for a declared quotient relative to the access quotient. -/
inductive AccessQuotientStatus where
  | exactAccess
  | accessCoarsening
  | ghostRefinement
  | incomparableAccess
deriving DecidableEq

/-- Meaning of each access quotient comparison status. -/
def AccessStatusHolds {H Q QI : Type} (q : H → Q) (qI : H → QI) :
    AccessQuotientStatus → Prop
  | AccessQuotientStatus.exactAccess =>
      NoVisibleLoss q qI ∧ NoGhostDistinction q qI
  | AccessQuotientStatus.accessCoarsening =>
      ¬ NoVisibleLoss q qI ∧ NoGhostDistinction q qI
  | AccessQuotientStatus.ghostRefinement =>
      NoVisibleLoss q qI ∧ ¬ NoGhostDistinction q qI
  | AccessQuotientStatus.incomparableAccess =>
      ¬ NoVisibleLoss q qI ∧ ¬ NoGhostDistinction q qI

/-- Exactly one access quotient status applies. -/
def ExactlyOneAccessStatus {H Q QI : Type} (q : H → Q) (qI : H → QI) : Prop :=
  ∃ status : AccessQuotientStatus,
    AccessStatusHolds q qI status ∧
      ∀ other : AccessQuotientStatus,
        AccessStatusHolds q qI other → other = status

/-- Visible-loss pairs are absent exactly when `NoVisibleLoss` holds. -/
theorem no_visible_loss_iff_no_visible_loss_pair {H Q QI : Type}
    (q : H → Q) (qI : H → QI) :
    NoVisibleLoss q qI ↔ ∀ pair : H × H, ¬ VisibleLossPair q qI pair := by
  constructor
  · intro h pair hp
    rcases pair with ⟨x, y⟩
    exact hp.2 (h x y hp.1)
  · intro h x y hq
    exact Classical.byContradiction (fun hneq =>
      False.elim (h (x, y) ⟨hq, hneq⟩))

/-- Ghost-distinction pairs are absent exactly when `NoGhostDistinction` holds. -/
theorem no_ghost_iff_no_ghost_pair {H Q QI : Type} (q : H → Q) (qI : H → QI) :
    NoGhostDistinction q qI ↔
      ∀ pair : H × H, ¬ GhostDistinctionPair q qI pair := by
  constructor
  · intro h pair hp
    rcases pair with ⟨x, y⟩
    exact hp.2 (h x y hp.1)
  · intro h x y hqI
    exact Classical.byContradiction (fun hneq =>
      False.elim (h (x, y) ⟨hqI, hneq⟩))

/-- The common refinement carries every access-visible distinction. -/
theorem common_access_refinement_no_visible_loss {H Q QI : Type}
    (q : H → Q) (qI : H → QI) :
    NoVisibleLoss (commonAccessRefinement q qI) qI := by
  intro x y h
  exact congrArg Prod.snd h

/-- The two obstruction bits classify the declared quotient relative to access. -/
theorem access_status_partition {H Q QI : Type} (q : H → Q) (qI : H → QI) :
    ExactlyOneAccessStatus q qI := by
  classical
  by_cases hloss : NoVisibleLoss q qI
  · by_cases hghost : NoGhostDistinction q qI
    · refine ⟨AccessQuotientStatus.exactAccess, ⟨hloss, hghost⟩, ?_⟩
      intro other hother
      cases other with
      | exactAccess => rfl
      | accessCoarsening =>
          exact False.elim (hother.1 hloss)
      | ghostRefinement =>
          exact False.elim (hother.2 hghost)
      | incomparableAccess =>
          exact False.elim (hother.1 hloss)
    · refine ⟨AccessQuotientStatus.ghostRefinement, ⟨hloss, hghost⟩, ?_⟩
      intro other hother
      cases other with
      | exactAccess =>
          exact False.elim (hghost hother.2)
      | accessCoarsening =>
          exact False.elim (hother.1 hloss)
      | ghostRefinement => rfl
      | incomparableAccess =>
          exact False.elim (hother.1 hloss)
  · by_cases hghost : NoGhostDistinction q qI
    · refine ⟨AccessQuotientStatus.accessCoarsening, ⟨hloss, hghost⟩, ?_⟩
      intro other hother
      cases other with
      | exactAccess =>
          exact False.elim (hloss hother.1)
      | accessCoarsening => rfl
      | ghostRefinement =>
          exact False.elim (hother.2 hghost)
      | incomparableAccess =>
          exact False.elim (hother.2 hghost)
    · refine ⟨AccessQuotientStatus.incomparableAccess, ⟨hloss, hghost⟩, ?_⟩
      intro other hother
      cases other with
      | exactAccess =>
          exact False.elim (hloss hother.1)
      | accessCoarsening =>
          exact False.elim (hghost hother.2)
      | ghostRefinement =>
          exact False.elim (hloss hother.1)
      | incomparableAccess => rfl

/--
Quotientality Normal Form. A lawful observation signature constructs its
canonical access quotient. Layer-sameness is exactly equality of observation
signatures; lawful observables factor uniquely through the constructed quotient;
current visibility is factorization through that quotient; and any declared
quotient has exactly one of the four access-comparison statuses relative to it.
-/
theorem quotientality {H Q W : Type} (S : ObservationSignature H) (q : H → Q)
    (expr : H → W) (hlawful : LawfulObservable S expr) :
    (∀ x y : H, LayerSame (qI S) x y ↔ accessKernel S x y) ∧
      ObservableFactorsUniquely S expr ∧
        (Function.Surjective q →
          CarriesObservationSignature S q →
            ∃ collapse : Q → AccessQuotient S, collapse ∘ q = qI S) ∧
          (CurrentVisible (qI S) expr ↔ FactorsThroughAccess (qI S) expr) ∧
            ExactlyOneAccessStatus q (qI S) := by
  constructor
  · intro x y
    exact qI_eq_iff_accessKernel S x y
  · constructor
    · exact observable_factorization S expr hlawful
    · constructor
      · intro hq hcarries
        exact qI_is_coarsest S q hq hcarries
      · constructor
        · exact (sufficiency_closure (qI S) expr (qI_surjective S)).1
        · exact access_status_partition q (qI S)

end SixBirdsMetaMath.FoundationsIV.Access.Quotientality
