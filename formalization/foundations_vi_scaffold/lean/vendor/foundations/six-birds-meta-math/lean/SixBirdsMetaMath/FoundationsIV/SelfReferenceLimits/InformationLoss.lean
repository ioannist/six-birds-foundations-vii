import SixBirdsMetaMath.FoundationsIV.Transport.DescentRepair

/-!
F34 Information Loss Normal Form.

Information loss is modeled as quotient-relative nonrecoverability: declared
source information is preserved exactly when it descends through the later
accessible quotient after transport.
-/

namespace SixBirdsMetaMath.FoundationsIV.SelfReferenceLimits.InformationLoss

open SixBirdsMetaMath.FoundationsIV.Transport.DescentRepair

/-- The later accessible recovery signature on the source carrier. -/
def laterRecoverySignature {H0 H1 R : Type} (transport : H0 → H1)
    (recoveryQuotient : H1 → R) : H0 → R :=
  recoveryQuotient ∘ transport

/-- Declared source information is recoverable from the later quotient exactly
when it descends through the later recovery signature. -/
def Recoverable {H0 Info H1 R : Type} (sourceInfo : H0 → Info)
    (transport : H0 → H1) (recoveryQuotient : H1 → R) : Prop :=
  Descends (laterRecoverySignature transport recoveryQuotient)
    (fun h : H0 => h) sourceInfo

/-- Information-loss obstruction: same later accessible state, different
declared source information. -/
def InformationLossObstruction {H0 Info H1 R : Type} (sourceInfo : H0 → Info)
    (transport : H0 → H1) (recoveryQuotient : H1 → R) : (H0 × H0) → Prop :=
  splitPairObstruction (laterRecoverySignature transport recoveryQuotient)
    (fun h : H0 => h) sourceInfo

/-- No information-loss obstruction is present. -/
def InformationLossObstructionEmpty {H0 Info H1 R : Type}
    (sourceInfo : H0 → Info) (transport : H0 → H1)
    (recoveryQuotient : H1 → R) : Prop :=
  ObstructionEmpty (InformationLossObstruction sourceInfo transport recoveryQuotient)

/-- Information is lost relative to the declared source information, transport,
and recovery quotient when the loss obstruction has a witness. -/
def InformationLost {H0 Info H1 R : Type} (sourceInfo : H0 → Info)
    (transport : H0 → H1) (recoveryQuotient : H1 → R) : Prop :=
  ∃ pair, InformationLossObstruction sourceInfo transport recoveryQuotient pair

/-- Forward quotient transport from a source quotient to a later quotient. -/
def ForwardTransport {H0 Q0 H1 Q1 : Type} (sourceQuotient : H0 → Q0)
    (transport : H0 → H1) (laterQuotient : H1 → Q1) : Prop :=
  Descends sourceQuotient transport laterQuotient

/-- Forward split obstruction: the same source quotient class can produce
different later quotient classes. -/
def ForwardSplitObstruction {H0 Q0 H1 Q1 : Type} (sourceQuotient : H0 → Q0)
    (transport : H0 → H1) (laterQuotient : H1 → Q1) : (H0 × H0) → Prop :=
  splitPairObstruction sourceQuotient transport laterQuotient

/-- No forward split obstruction is present. -/
def ForwardSplitObstructionEmpty {H0 Q0 H1 Q1 : Type}
    (sourceQuotient : H0 → Q0) (transport : H0 → H1)
    (laterQuotient : H1 → Q1) : Prop :=
  ObstructionEmpty (ForwardSplitObstruction sourceQuotient transport laterQuotient)

/-- Merge obstruction: different source quotient classes merge inside the later
accessible quotient. This is information loss for the source quotient. -/
def MergeObstruction {H0 Q0 H1 Q1 : Type} (sourceQuotient : H0 → Q0)
    (transport : H0 → H1) (laterQuotient : H1 → Q1) : (H0 × H0) → Prop :=
  InformationLossObstruction sourceQuotient transport laterQuotient

/-- No merge obstruction is present. -/
def MergeObstructionEmpty {H0 Q0 H1 Q1 : Type} (sourceQuotient : H0 → Q0)
    (transport : H0 → H1) (laterQuotient : H1 → Q1) : Prop :=
  InformationLossObstructionEmpty sourceQuotient transport laterQuotient

/-- The source quotient is recoverable from the later quotient. -/
def SourceQuotientRecoverable {H0 Q0 H1 Q1 : Type}
    (sourceQuotient : H0 → Q0) (transport : H0 → H1)
    (laterQuotient : H1 → Q1) : Prop :=
  Recoverable sourceQuotient transport laterQuotient

/-- Exact reversible preservation: forward quotient transport and backward
recovery both exist. -/
def ReversibleInformationPreservation {H0 Q0 H1 Q1 : Type}
    (sourceQuotient : H0 → Q0) (transport : H0 → H1)
    (laterQuotient : H1 → Q1) : Prop :=
  ForwardTransport sourceQuotient transport laterQuotient ∧
    SourceQuotientRecoverable sourceQuotient transport laterQuotient

/-- Target-family recovery, represented by a joint source signature. -/
def TargetFamilyRecoverable {H0 Signature H1 R : Type}
    (signature : H0 → Signature) (transport : H0 → H1)
    (recoveryQuotient : H1 → R) : Prop :=
  Recoverable signature transport recoveryQuotient

/-- Target-family loss obstruction. -/
def TargetFamilyLossObstruction {H0 Signature H1 R : Type}
    (signature : H0 → Signature) (transport : H0 → H1)
    (recoveryQuotient : H1 → R) : (H0 × H0) → Prop :=
  InformationLossObstruction signature transport recoveryQuotient

/-- No target-family loss obstruction is present. -/
def TargetFamilyLossObstructionEmpty {H0 Signature H1 R : Type}
    (signature : H0 → Signature) (transport : H0 → H1)
    (recoveryQuotient : H1 → R) : Prop :=
  InformationLossObstructionEmpty signature transport recoveryQuotient

/-- A finer later quotient preserves information hidden from the declared
current recovery quotient. -/
def LaterQuotientRefines {H1 RPlus R : Type} (finer : H1 → RPlus)
    (coarser : H1 → R) : Prop :=
  Descends finer (fun h : H1 => h) coarser

/-- Hidden preservation: unrecoverable from current access, but recoverable from
a finer hidden/memory/upstream quotient that refines the current quotient. -/
def HiddenPreservation {H0 Info H1 R RPlus : Type} (sourceInfo : H0 → Info)
    (transport : H0 → H1) (current : H1 → R) (hidden : H1 → RPlus) : Prop :=
  LaterQuotientRefines hidden current ∧
    Recoverable sourceInfo transport hidden ∧
      ¬ Recoverable sourceInfo transport current

/-- Boundary-encoded preservation is ordinary recovery through a declared
boundary quotient. -/
def BoundaryEncodedPreservation {H0 Info H1 B : Type} (sourceInfo : H0 → Info)
    (transport : H0 → H1) (boundary : H1 → B) : Prop :=
  Recoverable sourceInfo transport boundary

/-- Coarse preservation: a coarsening of the declared source information is
recoverable even though the full source information is not. -/
def CoarseInformationPreservation {H0 Info InfoC H1 R : Type}
    (sourceInfo : H0 → Info) (coarsen : Info → InfoC)
    (transport : H0 → H1) (recoveryQuotient : H1 → R) : Prop :=
  Recoverable (coarsen ∘ sourceInfo) transport recoveryQuotient ∧
    ¬ Recoverable sourceInfo transport recoveryQuotient

/-- Canonical recovery repair that stores the later accessible quotient and the
missing source information. -/
def recoveryRepairQuotient {H0 Info H1 R : Type} (sourceInfo : H0 → Info)
    (transport : H0 → H1) (recoveryQuotient : H1 → R) : H0 → R × Info :=
  sourceRepairQuotient (laterRecoverySignature transport recoveryQuotient)
    (fun h : H0 => h) sourceInfo

/-- Source status vocabulary for information-loss claims. -/
inductive InformationLossStatus where
  | reversibleInformationPreservation
  | informationLoss
  | forwardTransportFailure
  | sourceQuotientInsufficient
  | targetFamilyPreserved
  | partialInformationLoss
  | hiddenPreservation
  | boundaryEncodedPreservation
  | recordPreserved
  | erasedWithRecord
  | probabilisticRetention
  | coarseInformationPreservation
  | targetOverreach
  | presentationArtifactRecovery
  | protocolSupportedRecovery
  | informationLossOverread
deriving DecidableEq

/-- Meaning assignment for the F34 status vocabulary. -/
def InformationLossStatusHolds (reversible loss forwardFailure sourceInsufficient
    familyPreserved partialLoss hidden boundaryEncoded record erased probabilistic coarse
    targetOverreach presentationArtifact protocol overread : Prop) :
    InformationLossStatus → Prop
  | InformationLossStatus.reversibleInformationPreservation => reversible
  | InformationLossStatus.informationLoss => loss
  | InformationLossStatus.forwardTransportFailure => forwardFailure
  | InformationLossStatus.sourceQuotientInsufficient => sourceInsufficient
  | InformationLossStatus.targetFamilyPreserved => familyPreserved
  | InformationLossStatus.partialInformationLoss => partialLoss
  | InformationLossStatus.hiddenPreservation => hidden
  | InformationLossStatus.boundaryEncodedPreservation => boundaryEncoded
  | InformationLossStatus.recordPreserved => record
  | InformationLossStatus.erasedWithRecord => erased
  | InformationLossStatus.probabilisticRetention => probabilistic
  | InformationLossStatus.coarseInformationPreservation => coarse
  | InformationLossStatus.targetOverreach => targetOverreach
  | InformationLossStatus.presentationArtifactRecovery => presentationArtifact
  | InformationLossStatus.protocolSupportedRecovery => protocol
  | InformationLossStatus.informationLossOverread => overread

/-- Recoverability is exactly absence of the information-loss obstruction. -/
theorem recoverable_iff_no_loss_obstruction {H0 Info H1 R : Type}
    (sourceInfo : H0 → Info) (transport : H0 → H1)
    (recoveryQuotient : H1 → R)
    (hlater :
      Function.Surjective (laterRecoverySignature transport recoveryQuotient)) :
    Recoverable sourceInfo transport recoveryQuotient ↔
      InformationLossObstructionEmpty sourceInfo transport recoveryQuotient :=
  descent_repair_normal_form (laterRecoverySignature transport recoveryQuotient)
    (fun h : H0 => h) sourceInfo hlater

/-- Factorization form of recoverability. -/
theorem recoverable_iff_factorization {H0 Info H1 R : Type}
    (sourceInfo : H0 → Info) (transport : H0 → H1)
    (recoveryQuotient : H1 → R) :
    Recoverable sourceInfo transport recoveryQuotient ↔
      ∃ recovery : R → Info,
        recovery ∘ laterRecoverySignature transport recoveryQuotient = sourceInfo := by
  constructor
  · intro hrec
    rcases hrec with ⟨recovery, hrecovery⟩
    exact ⟨recovery, by simpa [Function.comp, laterRecoverySignature] using hrecovery⟩
  · intro hfactor
    rcases hfactor with ⟨recovery, hrecovery⟩
    exact ⟨recovery, by simpa [Function.comp, laterRecoverySignature] using hrecovery⟩

/-- Information loss is exactly non-recoverability, under the declared reachable
later quotient carrier. -/
theorem information_lost_iff_not_recoverable {H0 Info H1 R : Type}
    (sourceInfo : H0 → Info) (transport : H0 → H1)
    (recoveryQuotient : H1 → R)
    (hlater :
      Function.Surjective (laterRecoverySignature transport recoveryQuotient)) :
    InformationLost sourceInfo transport recoveryQuotient ↔
      ¬ Recoverable sourceInfo transport recoveryQuotient := by
  constructor
  · intro hlost hrec
    rcases hlost with ⟨pair, hpair⟩
    have hempty :=
      (recoverable_iff_no_loss_obstruction sourceInfo transport recoveryQuotient
        hlater).1 hrec
    exact hempty pair hpair
  · intro hnotRecoverable
    classical
    exact Classical.byContradiction (fun hnoLoss =>
      hnotRecoverable
        ((recoverable_iff_no_loss_obstruction sourceInfo transport recoveryQuotient
          hlater).2 (fun pair hpair => hnoLoss ⟨pair, hpair⟩)))

/-- Forward quotient transport is exactly absence of the split obstruction. -/
theorem forward_transport_iff_no_split {H0 Q0 H1 Q1 : Type}
    (sourceQuotient : H0 → Q0) (transport : H0 → H1)
    (laterQuotient : H1 → Q1)
    (hsource : Function.Surjective sourceQuotient) :
    ForwardTransport sourceQuotient transport laterQuotient ↔
      ForwardSplitObstructionEmpty sourceQuotient transport laterQuotient :=
  descent_repair_normal_form sourceQuotient transport laterQuotient hsource

/-- Recoverability of a source quotient from a later quotient is exactly absence
of the merge obstruction. -/
theorem source_recoverable_iff_no_merge {H0 Q0 H1 Q1 : Type}
    (sourceQuotient : H0 → Q0) (transport : H0 → H1)
    (laterQuotient : H1 → Q1)
    (hlater :
      Function.Surjective (laterRecoverySignature transport laterQuotient)) :
    SourceQuotientRecoverable sourceQuotient transport laterQuotient ↔
      MergeObstructionEmpty sourceQuotient transport laterQuotient :=
  recoverable_iff_no_loss_obstruction sourceQuotient transport laterQuotient hlater

/-- Reversible preservation is exactly no split and no merge. -/
theorem reversible_preservation_iff_no_split_and_no_merge {H0 Q0 H1 Q1 : Type}
    (sourceQuotient : H0 → Q0) (transport : H0 → H1)
    (laterQuotient : H1 → Q1)
    (hsource : Function.Surjective sourceQuotient)
    (hlater :
      Function.Surjective (laterRecoverySignature transport laterQuotient)) :
    ReversibleInformationPreservation sourceQuotient transport laterQuotient ↔
      ForwardSplitObstructionEmpty sourceQuotient transport laterQuotient ∧
        MergeObstructionEmpty sourceQuotient transport laterQuotient := by
  constructor
  · intro hrev
    exact ⟨(forward_transport_iff_no_split sourceQuotient transport laterQuotient
        hsource).1 hrev.1,
      (source_recoverable_iff_no_merge sourceQuotient transport laterQuotient
        hlater).1 hrev.2⟩
  · intro hclear
    exact ⟨(forward_transport_iff_no_split sourceQuotient transport laterQuotient
        hsource).2 hclear.1,
      (source_recoverable_iff_no_merge sourceQuotient transport laterQuotient
        hlater).2 hclear.2⟩

/-- Target-family recovery is the same normal form for a joint signature. -/
theorem target_family_recoverable_iff_no_loss {H0 Signature H1 R : Type}
    (signature : H0 → Signature) (transport : H0 → H1)
    (recoveryQuotient : H1 → R)
    (hlater :
      Function.Surjective (laterRecoverySignature transport recoveryQuotient)) :
    TargetFamilyRecoverable signature transport recoveryQuotient ↔
      TargetFamilyLossObstructionEmpty signature transport recoveryQuotient :=
  recoverable_iff_no_loss_obstruction signature transport recoveryQuotient hlater

/-- The canonical recovery repair refines the later accessible quotient. -/
theorem recovery_repair_refines_later_signature {H0 Info H1 R : Type}
    (sourceInfo : H0 → Info) (transport : H0 → H1)
    (recoveryQuotient : H1 → R) :
    SourceRefinement (recoveryRepairQuotient sourceInfo transport recoveryQuotient)
      (laterRecoverySignature transport recoveryQuotient) :=
  source_repair_refines (laterRecoverySignature transport recoveryQuotient)
    (fun h : H0 => h) sourceInfo

/-- After canonical recovery repair, the source information descends. -/
theorem recovery_repair_recovers {H0 Info H1 R : Type}
    (sourceInfo : H0 → Info) (transport : H0 → H1)
    (recoveryQuotient : H1 → R) :
    Recoverable sourceInfo (fun h : H0 => h)
      (recoveryRepairQuotient sourceInfo transport recoveryQuotient) := by
  exact source_repair_descends (laterRecoverySignature transport recoveryQuotient)
    (fun h : H0 => h) sourceInfo

/--
Information Loss Normal Form. Declared source information is recoverable
exactly when it factors through the later accessible quotient after transport;
loss is nonempty merge inside that quotient. Forward preservation, backward
recovery, reversible preservation, and target-family recovery are kept as
separate quotient checks.
-/
theorem information_loss_normal_form {H0 Info H1 R Q0 Q1 Signature : Type}
    (sourceInfo : H0 → Info) (transport : H0 → H1)
    (recoveryQuotient : H1 → R) (sourceQuotient : H0 → Q0)
    (laterQuotient : H1 → Q1) (signature : H0 → Signature)
    (hlaterRecovery :
      Function.Surjective (laterRecoverySignature transport recoveryQuotient))
    (hsourceQuotient : Function.Surjective sourceQuotient)
    (hlaterQuotient :
      Function.Surjective (laterRecoverySignature transport laterQuotient)) :
    (Recoverable sourceInfo transport recoveryQuotient ↔
      InformationLossObstructionEmpty sourceInfo transport recoveryQuotient) ∧
      (Recoverable sourceInfo transport recoveryQuotient ↔
        ∃ recovery : R → Info,
          recovery ∘ laterRecoverySignature transport recoveryQuotient = sourceInfo) ∧
        (InformationLost sourceInfo transport recoveryQuotient ↔
          ¬ Recoverable sourceInfo transport recoveryQuotient) ∧
          (ForwardTransport sourceQuotient transport laterQuotient ↔
            ForwardSplitObstructionEmpty sourceQuotient transport laterQuotient) ∧
            (SourceQuotientRecoverable sourceQuotient transport laterQuotient ↔
              MergeObstructionEmpty sourceQuotient transport laterQuotient) ∧
              (ReversibleInformationPreservation sourceQuotient transport
                  laterQuotient ↔
                ForwardSplitObstructionEmpty sourceQuotient transport laterQuotient ∧
                  MergeObstructionEmpty sourceQuotient transport laterQuotient) ∧
                (TargetFamilyRecoverable signature transport recoveryQuotient ↔
                  TargetFamilyLossObstructionEmpty signature transport
                    recoveryQuotient) := by
  exact ⟨recoverable_iff_no_loss_obstruction sourceInfo transport recoveryQuotient
      hlaterRecovery,
    recoverable_iff_factorization sourceInfo transport recoveryQuotient,
    information_lost_iff_not_recoverable sourceInfo transport recoveryQuotient
      hlaterRecovery,
    forward_transport_iff_no_split sourceQuotient transport laterQuotient
      hsourceQuotient,
    source_recoverable_iff_no_merge sourceQuotient transport laterQuotient
      hlaterQuotient,
    reversible_preservation_iff_no_split_and_no_merge sourceQuotient transport
      laterQuotient hsourceQuotient hlaterQuotient,
    target_family_recoverable_iff_no_loss signature transport recoveryQuotient
      hlaterRecovery⟩

end SixBirdsMetaMath.FoundationsIV.SelfReferenceLimits.InformationLoss
