import SixBirdsIII.Domain

namespace SixBirdsFoundationsV

/-!
D3 carried record and carried instrument.

The fine source split is Foundations-V local because the vendored FIII Lean
`SourceTag.real` intentionally coarsens the paper's source-of-truth family.
The own-kernel trace predicate keeps the final D3 draft's contiguous interval
shape: every index from `nStart` up to `n0` must be in scope and witnessed by
the system transition support.
-/

inductive FineSourceTag where
  | committed_state
  | audited_cell_records
  | independent_pair_witness
  | simulation_trace
  | ablation_record
  | fallback
  | unknown
  | contradictory
  deriving DecidableEq, Repr

def CarriedSource (tag : FineSourceTag) (generatedByS inScope : Bool) : Prop :=
  (tag = FineSourceTag.committed_state ∨
    tag = FineSourceTag.audited_cell_records) ∧
  generatedByS = true ∧
  inScope = true

def IsCarrierCoordinate {Z : Type u} {R : Type v}
    (coordinateDeclared : (Z -> R) -> Prop) (rhoOf : Z -> R) : Prop :=
  coordinateDeclared rhoOf

def OwnKernelTraceTo {Z : Type u}
    (LegitimateStart : (Nat -> Z) -> Nat -> Prop)
    (suppK : Z -> Z -> Prop)
    (tau : Nat -> Z) (StepInScope : Nat -> Prop)
    (nStart n0 : Nat) : Prop :=
  nStart <= n0 ∧
  LegitimateStart tau nStart ∧
  ∀ n : Nat, nStart <= n -> n < n0 ->
    StepInScope n ∧ suppK (tau n) (tau (n + 1))

def ExistsDeclaredTrajectory {Z : Type u} {R : Type v}
    (LegitimateStart : (Nat -> Z) -> Nat -> Prop)
    (suppK : Z -> Z -> Prop)
    (tau : Nat -> Z) (StepInScope : Nat -> Prop)
    (nStart n0 : Nat) (rhoOf : Z -> R) (rho : R) : Prop :=
  OwnKernelTraceTo LegitimateStart suppK tau StepInScope nStart n0 ∧
  rho = rhoOf (tau n0)

def CarriedRecord {Z : Type u} {R : Type v}
    (coordinateDeclared : (Z -> R) -> Prop)
    (rhoOf : Z -> R) (rho : R)
    (LegitimateStart : (Nat -> Z) -> Nat -> Prop)
    (suppK : Z -> Z -> Prop)
    (tau : Nat -> Z) (StepInScope : Nat -> Prop)
    (nStart n0 : Nat)
    (sourceTag : FineSourceTag) (generatedByS inScope : Bool) : Prop :=
  IsCarrierCoordinate coordinateDeclared rhoOf ∧
  ExistsDeclaredTrajectory LegitimateStart suppK tau StepInScope
    nStart n0 rhoOf rho ∧
  CarriedSource sourceTag generatedByS inScope

structure CheckRuleRecord (Record : Type u) where
  record : Record
  audit : SixBirdsIII.AuditTag
  deriving Repr

def AllRecords {Record : Type u} (recordCarried : Record -> Prop) :
    List Record -> Prop
  | [] => True
  | record :: records => recordCarried record ∧ AllRecords recordCarried records

/-!
There is no dedicated FIII `CheckRuleTag` in the vendored substrate. Following
D3's six-field draft, check-rule records are anchored on FIII `AuditTag` and
the `Instrument.auditRequired` surface, while carriedness is still checked on
the underlying records listed here.

Future concrete E-law instantiations should pass a named completeness predicate,
for example `CompleteInstrumentInventory instrument visibilityRecords
thresholdRecords checkRuleRecords`, rather than an opaque bare proposition.
D3 only requires the certified input; it does not define the concrete inventory
predicate before a concrete instrument host exists.
-/
def CarriedInstrument {Record : Type u}
    (recordCarried : Record -> Prop)
    (_instrument : SixBirdsIII.Instrument)
    (recordsAreCompleteInventory : Prop)
    (visibilityRecords thresholdRecords : List Record)
    (checkRuleRecords : List (CheckRuleRecord Record)) : Prop :=
  recordsAreCompleteInventory ∧
  AllRecords recordCarried visibilityRecords ∧
  AllRecords recordCarried thresholdRecords ∧
  AllRecords (fun checkRule => recordCarried checkRule.record) checkRuleRecords

theorem carriedSource_committed_state :
    CarriedSource FineSourceTag.committed_state true true := by
  exact ⟨Or.inl rfl, rfl, rfl⟩

theorem carriedSource_audited_cell_records :
    CarriedSource FineSourceTag.audited_cell_records true true := by
  exact ⟨Or.inr rfl, rfl, rfl⟩

theorem carriedSource_allowed_tag {tag : FineSourceTag}
    {generatedByS inScope : Bool}
    (h : CarriedSource tag generatedByS inScope) :
    tag = FineSourceTag.committed_state ∨
      tag = FineSourceTag.audited_cell_records := by
  exact h.1

theorem not_carriedSource_fallback (generatedByS inScope : Bool) :
    ¬ CarriedSource FineSourceTag.fallback generatedByS inScope := by
  intro h
  cases h.1 with
  | inl htag => cases htag
  | inr htag => cases htag

theorem not_carriedSource_independent_pair_witness
    (generatedByS inScope : Bool) :
    ¬ CarriedSource FineSourceTag.independent_pair_witness
      generatedByS inScope := by
  intro h
  cases h.1 with
  | inl htag => cases htag
  | inr htag => cases htag

theorem not_carriedSource_simulation_trace
    (generatedByS inScope : Bool) :
    ¬ CarriedSource FineSourceTag.simulation_trace generatedByS inScope := by
  intro h
  cases h.1 with
  | inl htag => cases htag
  | inr htag => cases htag

theorem not_carriedSource_ablation_record
    (generatedByS inScope : Bool) :
    ¬ CarriedSource FineSourceTag.ablation_record generatedByS inScope := by
  intro h
  cases h.1 with
  | inl htag => cases htag
  | inr htag => cases htag

theorem not_carriedSource_unknown (generatedByS inScope : Bool) :
    ¬ CarriedSource FineSourceTag.unknown generatedByS inScope := by
  intro h
  cases h.1 with
  | inl htag => cases htag
  | inr htag => cases htag

theorem not_carriedSource_contradictory (generatedByS inScope : Bool) :
    ¬ CarriedSource FineSourceTag.contradictory generatedByS inScope := by
  intro h
  cases h.1 with
  | inl htag => cases htag
  | inr htag => cases htag

def carriedSource_decidable (tag : FineSourceTag)
    (generatedByS inScope : Bool) :
    Decidable (CarriedSource tag generatedByS inScope) := by
  unfold CarriedSource
  infer_instance

theorem ownKernelTraceTo_step_in_scope {Z : Type u}
    {LegitimateStart : (Nat -> Z) -> Nat -> Prop}
    {suppK : Z -> Z -> Prop}
    {tau : Nat -> Z} {StepInScope : Nat -> Prop}
    {nStart n0 n : Nat}
    (h : OwnKernelTraceTo LegitimateStart suppK tau StepInScope nStart n0)
    (hlo : nStart <= n) (hhi : n < n0) :
    StepInScope n := by
  exact (h.2.2 n hlo hhi).1

theorem ownKernelTraceTo_suppK {Z : Type u}
    {LegitimateStart : (Nat -> Z) -> Nat -> Prop}
    {suppK : Z -> Z -> Prop}
    {tau : Nat -> Z} {StepInScope : Nat -> Prop}
    {nStart n0 n : Nat}
    (h : OwnKernelTraceTo LegitimateStart suppK tau StepInScope nStart n0)
    (hlo : nStart <= n) (hhi : n < n0) :
    suppK (tau n) (tau (n + 1)) := by
  exact (h.2.2 n hlo hhi).2

theorem not_ownKernelTraceTo_of_step_not_in_scope {Z : Type u}
    {LegitimateStart : (Nat -> Z) -> Nat -> Prop}
    {suppK : Z -> Z -> Prop}
    {tau : Nat -> Z} {StepInScope : Nat -> Prop}
    {nStart n0 n : Nat}
    (hlo : nStart <= n) (hhi : n < n0)
    (hskip : ¬ StepInScope n) :
    ¬ OwnKernelTraceTo LegitimateStart suppK tau StepInScope nStart n0 := by
  intro h
  exact hskip (ownKernelTraceTo_step_in_scope h hlo hhi)

theorem not_carriedRecord_of_step_not_in_scope {Z : Type u} {R : Type v}
    {coordinateDeclared : (Z -> R) -> Prop}
    {rhoOf : Z -> R} {rho : R}
    {LegitimateStart : (Nat -> Z) -> Nat -> Prop}
    {suppK : Z -> Z -> Prop}
    {tau : Nat -> Z} {StepInScope : Nat -> Prop}
    {nStart n0 n : Nat}
    {sourceTag : FineSourceTag} {generatedByS inScope : Bool}
    (hlo : nStart <= n) (hhi : n < n0)
    (hskip : ¬ StepInScope n) :
    ¬ CarriedRecord coordinateDeclared rhoOf rho LegitimateStart suppK tau
      StepInScope nStart n0 sourceTag generatedByS inScope := by
  intro h
  exact hskip
    (ownKernelTraceTo_step_in_scope h.2.1.1 hlo hhi)

def ownKernelTraceTo_decidable_of_inputs {Z : Type u}
    (LegitimateStart : (Nat -> Z) -> Nat -> Prop)
    (suppK : Z -> Z -> Prop)
    (tau : Nat -> Z) (StepInScope : Nat -> Prop)
    (nStart n0 : Nat)
    [Decidable (LegitimateStart tau nStart)]
    [Decidable
      (∀ n : Nat, nStart <= n -> n < n0 ->
        StepInScope n ∧ suppK (tau n) (tau (n + 1)))] :
    Decidable (OwnKernelTraceTo LegitimateStart suppK tau StepInScope
      nStart n0) := by
  unfold OwnKernelTraceTo
  infer_instance

def carriedRecord_decidable_of_inputs {Z : Type u} {R : Type v}
    (coordinateDeclared : (Z -> R) -> Prop)
    (rhoOf : Z -> R) (rho : R)
    (LegitimateStart : (Nat -> Z) -> Nat -> Prop)
    (suppK : Z -> Z -> Prop)
    (tau : Nat -> Z) (StepInScope : Nat -> Prop)
    (nStart n0 : Nat)
    (sourceTag : FineSourceTag) (generatedByS inScope : Bool)
    [Decidable (IsCarrierCoordinate coordinateDeclared rhoOf)]
    [Decidable
      (ExistsDeclaredTrajectory LegitimateStart suppK tau StepInScope
        nStart n0 rhoOf rho)]
    [Decidable (CarriedSource sourceTag generatedByS inScope)] :
    Decidable
      (CarriedRecord coordinateDeclared rhoOf rho LegitimateStart suppK tau
        StepInScope nStart n0 sourceTag generatedByS inScope) := by
  unfold CarriedRecord
  infer_instance

def carriedInstrument_decidable_of_inputs {Record : Type u}
    (recordCarried : Record -> Prop)
    (instrument : SixBirdsIII.Instrument)
    (recordsAreCompleteInventory : Prop)
    (visibilityRecords thresholdRecords : List Record)
    (checkRuleRecords : List (CheckRuleRecord Record))
    [Decidable recordsAreCompleteInventory]
    [Decidable (AllRecords recordCarried visibilityRecords)]
    [Decidable (AllRecords recordCarried thresholdRecords)]
    [Decidable
      (AllRecords
        (fun checkRule => recordCarried checkRule.record) checkRuleRecords)] :
    Decidable
      (CarriedInstrument recordCarried instrument recordsAreCompleteInventory visibilityRecords
        thresholdRecords checkRuleRecords) := by
  unfold CarriedInstrument
  infer_instance

theorem not_carriedInstrument_of_incomplete_inventory {Record : Type u}
    (recordCarried : Record -> Prop)
    (instrument : SixBirdsIII.Instrument)
    {recordsAreCompleteInventory : Prop}
    (visibilityRecords thresholdRecords : List Record)
    (checkRuleRecords : List (CheckRuleRecord Record))
    (hincomplete : ¬ recordsAreCompleteInventory) :
    ¬ CarriedInstrument recordCarried instrument recordsAreCompleteInventory
      visibilityRecords thresholdRecords checkRuleRecords := by
  intro h
  exact hincomplete h.1

theorem not_carriedInstrument_empty_without_complete_inventory
    {Record : Type u}
    (recordCarried : Record -> Prop)
    (instrument : SixBirdsIII.Instrument) :
    ¬ CarriedInstrument recordCarried instrument False
      ([] : List Record) ([] : List Record) ([] : List (CheckRuleRecord Record)) := by
  intro h
  exact False.elim h.1

end SixBirdsFoundationsV
