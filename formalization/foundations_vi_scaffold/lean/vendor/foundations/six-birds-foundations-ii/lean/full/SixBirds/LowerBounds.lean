import SixBirds.Admissibility

namespace SixBirds

structure CommonWitnessData (role : Role) where
  D : FATCD
  cluster : List RawRecord
  theta : ThresholdAttachment D role
  level : Level
  finiteVerification : FiniteDescription D.desc
  closureVerification : ClosedDescription D.desc
  auditVerification : AuditedDescription D.desc
  nonclaimRecord : Bool
  projection : DerivedRoleProjection D role

def commonWitnessData (role : Role) : CommonWitnessData role :=
  { D := witnessDescription role
    cluster := (witnessDescription role).desc.raw
    theta := thresholdAttachment role
    level := Level.verification
    finiteVerification := (witnessDescription role).finite
    closureVerification := (witnessDescription role).closed
    auditVerification := (witnessDescription role).audited
    nonclaimRecord := true
    projection := roleProjection role }

theorem six_role_lower_bounds :
    ∀ role : Role, ∃ w : CommonWitnessData role,
      Nonempty (DerivedRoleProjection w.D role) := by
  intro role
  refine ⟨commonWitnessData role, ?_⟩
  exact ⟨(commonWitnessData role).projection⟩

theorem p1_witness :
    ∃ D : FATCD, Nonempty (DerivedRoleProjection D Role.P1) := by
  exact ⟨witnessDescription Role.P1, ⟨roleProjection Role.P1⟩⟩

theorem p2_witness :
    ∃ D : FATCD, Nonempty (DerivedRoleProjection D Role.P2) := by
  exact ⟨witnessDescription Role.P2, ⟨roleProjection Role.P2⟩⟩

theorem p3_witness :
    ∃ D : FATCD, Nonempty (DerivedRoleProjection D Role.P3) := by
  exact ⟨witnessDescription Role.P3, ⟨roleProjection Role.P3⟩⟩

theorem p4_witness :
    ∃ D : FATCD, Nonempty (DerivedRoleProjection D Role.P4) := by
  exact ⟨witnessDescription Role.P4, ⟨roleProjection Role.P4⟩⟩

theorem p5_witness :
    ∃ D : FATCD, Nonempty (DerivedRoleProjection D Role.P5) := by
  exact ⟨witnessDescription Role.P5, ⟨roleProjection Role.P5⟩⟩

theorem p6_witness :
    ∃ D : FATCD, Nonempty (DerivedRoleProjection D Role.P6) := by
  exact ⟨witnessDescription Role.P6, ⟨roleProjection Role.P6⟩⟩

end SixBirds
