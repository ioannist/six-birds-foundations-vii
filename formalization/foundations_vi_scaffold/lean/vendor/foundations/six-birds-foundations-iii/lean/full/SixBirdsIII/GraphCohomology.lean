namespace SixBirdsIII

structure GraphCohomologySupport where
  Cycle : Type
  Cochain0 : Type
  Cochain1 : Type
  Scalar : Type
  zero : Scalar
  exact : Cochain1 -> Prop
  classZero : Cochain1 -> Prop
  integral : Cochain1 -> Cycle -> Scalar
  betaOneZero : Prop
  noCycles : Prop
  finiteGraphHost : Bool
  graphInstrument : Bool

def ExactFormsHaveZeroIntegrals (G : GraphCohomologySupport) : Prop :=
  forall a : G.Cochain1, G.exact a -> forall gamma : G.Cycle,
    G.integral a gamma = G.zero

def PairingNondegenerate (G : GraphCohomologySupport) : Prop :=
  forall a : G.Cochain1,
    (¬ G.classZero a) <->
      exists gamma : G.Cycle, G.integral a gamma ≠ G.zero

def ForestSupport (G : GraphCohomologySupport) : Prop :=
  G.finiteGraphHost = true /\
    G.graphInstrument = true /\
    G.betaOneZero /\
    G.noCycles

def FirstCohomologyZero (G : GraphCohomologySupport) : Prop :=
  forall a : G.Cochain1, G.classZero a

def ForestNoCohomologySupport (G : GraphCohomologySupport) : Prop :=
  ForestSupport G /\ FirstCohomologyZero G

def HasCycleSupportedDrive (G : GraphCohomologySupport) (a : G.Cochain1) : Prop :=
  exists gamma : G.Cycle, G.integral a gamma ≠ G.zero

def CohomologicalDriveClass (G : GraphCohomologySupport) (a : G.Cochain1) : Prop :=
  ¬ G.classZero a

def NoCycleSupportedDrive (G : GraphCohomologySupport) : Prop :=
  forall a : G.Cochain1, ¬ HasCycleSupportedDrive G a

inductive DriveCertificateStatus where
  | present
  | absentWithRecord
deriving DecidableEq, Repr

theorem nonzero_affinity_equivalence
    (G : GraphCohomologySupport)
    (hpair : PairingNondegenerate G)
    (a : G.Cochain1) :
    CohomologicalDriveClass G a <->
      HasCycleSupportedDrive G a := by
  exact hpair a

theorem exact_form_null_drive
    (G : GraphCohomologySupport)
    (hexact : ExactFormsHaveZeroIntegrals G)
    (a : G.Cochain1)
    (ha : G.exact a) :
    forall gamma : G.Cycle, G.integral a gamma = G.zero := by
  exact hexact a ha

theorem forest_no_drive
    (G : GraphCohomologySupport)
    (hforest : ForestNoCohomologySupport G)
    (hpair : PairingNondegenerate G) :
    NoCycleSupportedDrive G := by
  intro a hdrive
  have hnonzero : CohomologicalDriveClass G a :=
    (nonzero_affinity_equivalence G hpair a).mpr hdrive
  exact hnonzero (hforest.right a)

structure GraphGate where
  source : GraphCohomologySupport
  target : GraphCohomologySupport
  admissible : Bool
  forestProducing : Prop
  cycleRankLossRecorded : Bool

theorem gating_affinity_suppression
    (gate : GraphGate)
    (_hadm : gate.admissible = true)
    (_hloss : gate.cycleRankLossRecorded = true)
    (hforest : ForestNoCohomologySupport gate.target)
    (hpair : PairingNondegenerate gate.target) :
    NoCycleSupportedDrive gate.target := by
  exact forest_no_drive gate.target hforest hpair

theorem gating_drive_certificate_absent_with_record
    (gate : GraphGate)
    (hadm : gate.admissible = true)
    (hloss : gate.cycleRankLossRecorded = true)
    (hforest : ForestNoCohomologySupport gate.target)
    (hpair : PairingNondegenerate gate.target) :
    NoCycleSupportedDrive gate.target /\
      DriveCertificateStatus.absentWithRecord =
        DriveCertificateStatus.absentWithRecord := by
  exact ⟨gating_affinity_suppression gate hadm hloss hforest hpair, rfl⟩

end SixBirdsIII
