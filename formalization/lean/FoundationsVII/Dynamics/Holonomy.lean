import FoundationsVII.Dynamics.Confluence
import FoundationsVII.Prior.FT15

/-!
# Interaction-order residue, holonomy, and arrow separation

Two legal routes on one typed target may leave a route residue. Predictive
route residue is interaction holonomy. An arrow requires an independent drive,
path-asymmetry, reversal, budget, and audit certificate.
-/

namespace FoundationsVII

structure RouteResult where
  routeId : Nat
  targetTheory : TheoryId
  memberIds : List TheoryId
  orderCode : Nat
  bracketingCode : Nat
  predictiveValue : Nat
  auditValue : Nat
  legal : Bool
  deriving Repr, DecidableEq, BEq

structure RouteComparison where
  left : RouteResult
  right : RouteResult
  deriving Repr, DecidableEq, BEq

namespace RouteComparison

def SameTypedTarget (comparison : RouteComparison) : Prop :=
  comparison.left.targetTheory = comparison.right.targetTheory ∧
  comparison.left.memberIds = comparison.right.memberIds

instance (comparison : RouteComparison) : Decidable (SameTypedTarget comparison) := by
  unfold SameTypedTarget
  infer_instance

def ChangedRoute (comparison : RouteComparison) : Prop :=
  comparison.left.orderCode ≠ comparison.right.orderCode ∨
  comparison.left.bracketingCode ≠ comparison.right.bracketingCode

instance (comparison : RouteComparison) : Decidable (ChangedRoute comparison) := by
  unfold ChangedRoute
  infer_instance

def RouteResidue (comparison : RouteComparison) : Prop :=
  comparison.left.legal = true ∧
  comparison.right.legal = true ∧
  SameTypedTarget comparison ∧
  ChangedRoute comparison ∧
  (comparison.left.predictiveValue ≠ comparison.right.predictiveValue ∨
    comparison.left.auditValue ≠ comparison.right.auditValue)

instance (comparison : RouteComparison) : Decidable (RouteResidue comparison) := by
  unfold RouteResidue
  infer_instance

def Holonomy (comparison : RouteComparison) : Prop :=
  RouteResidue comparison ∧
  comparison.left.predictiveValue ≠ comparison.right.predictiveValue

instance (comparison : RouteComparison) : Decidable (Holonomy comparison) := by
  unfold Holonomy
  infer_instance

end RouteComparison

structure DriveCertificate where
  drivePresent : Bool
  pathAsymmetry : Bool
  reversalFails : Bool
  budgeted : Bool
  audited : Bool
  deriving Repr, DecidableEq, BEq

namespace DriveCertificate

def Valid (certificate : DriveCertificate) : Prop :=
  certificate.drivePresent = true ∧
  certificate.pathAsymmetry = true ∧
  certificate.reversalFails = true ∧
  certificate.budgeted = true ∧
  certificate.audited = true

instance (certificate : DriveCertificate) : Decidable (Valid certificate) := by
  unfold Valid
  infer_instance

end DriveCertificate

structure ArrowClaim where
  comparison : RouteComparison
  drive : DriveCertificate
  arrowCredit : Bool
  deriving Repr, DecidableEq, BEq

namespace ArrowClaim

def Eligible (claim : ArrowClaim) : Prop :=
  claim.arrowCredit = true ∧
  DriveCertificate.Valid claim.drive

instance (claim : ArrowClaim) : Decidable (Eligible claim) := by
  unfold Eligible
  infer_instance

end ArrowClaim

private def routeA : RouteResult :=
  { routeId := 1, targetTheory := 3, memberIds := [1, 2, 3],
    orderCode := 12, bracketingCode := 1, predictiveValue := 7,
    auditValue := 100, legal := true }

private def routeB : RouteResult :=
  { routeId := 2, targetTheory := 3, memberIds := [1, 2, 3],
    orderCode := 21, bracketingCode := 2, predictiveValue := 9,
    auditValue := 101, legal := true }

private def holonomyComparison : RouteComparison :=
  { left := routeA, right := routeB }

private def zeroDrive : DriveCertificate :=
  { drivePresent := false, pathAsymmetry := false, reversalFails := false,
    budgeted := true, audited := true }

private def drivenCertificate : DriveCertificate :=
  { drivePresent := true, pathAsymmetry := true, reversalFails := true,
    budgeted := true, audited := true }

private def holonomyZeroArrowClaim : ArrowClaim :=
  { comparison := holonomyComparison, drive := zeroDrive, arrowCredit := false }

private def drivenArrowClaim : ArrowClaim :=
  { comparison := holonomyComparison, drive := drivenCertificate,
    arrowCredit := true }

theorem constructive_interaction_holonomy :
    RouteComparison.Holonomy holonomyComparison := by decide

theorem holonomy_with_zero_arrow_witness :
    RouteComparison.Holonomy holonomyZeroArrowClaim.comparison ∧
    holonomyZeroArrowClaim.arrowCredit = false := by decide

theorem driven_arrow_positive_control :
    RouteComparison.Holonomy drivenArrowClaim.comparison ∧
    ArrowClaim.Eligible drivenArrowClaim := by decide

theorem driven_arrow_requires_independent_drive_certificate
    {claim : ArrowClaim} (h : ArrowClaim.Eligible claim) :
    DriveCertificate.Valid claim.drive := h.2

structure ReversalControl where
  forwardValue : Nat
  reverseValue : Nat
  drivePresent : Bool
  reversalFails : Bool
  deriving Repr, DecidableEq, BEq

private def reversibleNull : ReversalControl :=
  { forwardValue := 5, reverseValue := 5,
    drivePresent := false, reversalFails := false }

private def drivenIrreversible : ReversalControl :=
  { forwardValue := 5, reverseValue := 3,
    drivePresent := true, reversalFails := true }

theorem reversal_null_and_driven_controls_are_distinct :
    reversibleNull.forwardValue = reversibleNull.reverseValue ∧
    drivenIrreversible.forwardValue ≠ drivenIrreversible.reverseValue ∧
    reversibleNull.drivePresent = false ∧
    drivenIrreversible.drivePresent = true := by decide

end FoundationsVII
