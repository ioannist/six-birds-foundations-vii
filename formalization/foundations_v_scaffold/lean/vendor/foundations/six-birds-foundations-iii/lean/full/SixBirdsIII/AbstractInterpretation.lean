namespace SixBirdsIII

structure AIHost where
  C : Type
  A : Type
  leC : C -> C -> Prop
  leA : A -> A -> Prop
  alpha : C -> A
  gamma : A -> C
  rho : C -> C
  F : C -> C
  Fsharp : A -> A
  finiteC : Bool
  finiteA : Bool
  auditPresent : Bool
  rho_eq : forall c : C, rho c = gamma (alpha c)
  leC_trans : forall x y z : C, leC x y -> leC y z -> leC x z
  leC_antisymm : forall x y : C, leC x y -> leC y x -> x = y
  leA_trans : forall x y z : A, leA x y -> leA y z -> leA x z
  alpha_mono : forall x y : C, leC x y -> leA (alpha x) (alpha y)
  gamma_mono : forall x y : A, leA x y -> leC (gamma x) (gamma y)
  unit : forall c : C, leC c (gamma (alpha c))
  counit : forall a : A, leA (alpha (gamma a)) a
  F_mono : forall x y : C, leC x y -> leC (F x) (F y)
  Fsharp_mono : forall x y : A, leA x y -> leA (Fsharp x) (Fsharp y)
  adjunction : forall c : C, forall a : A, leA (alpha c) a <-> leC c (gamma a)
  gamma_fixed : forall a : A, rho (gamma a) = gamma a

def ClosureOperatorOn (H : AIHost) (rho : H.C -> H.C) : Prop :=
  (forall c : H.C, H.leC c (rho c)) /\
    (forall c c' : H.C, H.leC c c' -> H.leC (rho c) (rho c')) /\
    (forall c : H.C, rho (rho c) = rho c)

def AbstractSoundness (H : AIHost) : Prop :=
  forall c : H.C, H.leA (H.alpha (H.F c)) (H.Fsharp (H.alpha c))

def ConcreteSoundness (H : AIHost) : Prop :=
  forall a : H.A, H.leC (H.F (H.gamma a)) (H.gamma (H.Fsharp a))

def Representable (H : AIHost) (p : H.C) : Prop :=
  exists a : H.A, H.gamma a = p

def FixedByRho (H : AIHost) (p : H.C) : Prop :=
  H.rho p = p

theorem ai_closure_as_packaging
    (H : AIHost)
    (_hfiniteC : H.finiteC = true)
    (_hfiniteA : H.finiteA = true)
    (_haudit : H.auditPresent = true) :
    ClosureOperatorOn H H.rho := by
  constructor
  · intro c
    rw [H.rho_eq c]
    exact H.unit c
  constructor
  · intro c c' hc
    rw [H.rho_eq c, H.rho_eq c']
    exact H.gamma_mono (H.alpha c) (H.alpha c') (H.alpha_mono c c' hc)
  · intro c
    have hdown : H.leC (H.rho (H.rho c)) (H.rho c) := by
      rw [H.rho_eq (H.rho c), H.rho_eq c]
      exact H.gamma_mono (H.alpha (H.gamma (H.alpha c))) (H.alpha c)
        (H.counit (H.alpha c))
    have hup : H.leC (H.rho c) (H.rho (H.rho c)) := by
      have hunit := H.unit (H.rho c)
      rw [← H.rho_eq (H.rho c)] at hunit
      exact hunit
    exact H.leC_antisymm (H.rho (H.rho c)) (H.rho c) hdown hup

theorem ai_descent_as_sound_transformer (H : AIHost) :
    AbstractSoundness H <-> ConcreteSoundness H := by
  constructor
  · intro habs a
    apply (H.adjunction (H.F (H.gamma a)) (H.Fsharp a)).mp
    exact H.leA_trans (H.alpha (H.F (H.gamma a)))
      (H.Fsharp (H.alpha (H.gamma a)))
      (H.Fsharp a)
      (habs (H.gamma a))
      (H.Fsharp_mono (H.alpha (H.gamma a)) a (H.counit a))
  · intro hconc c
    apply (H.adjunction (H.F c) (H.Fsharp (H.alpha c))).mpr
    exact H.leC_trans (H.F c)
      (H.F (H.gamma (H.alpha c)))
      (H.gamma (H.Fsharp (H.alpha c)))
      (H.F_mono c (H.gamma (H.alpha c)) (H.unit c))
      (hconc (H.alpha c))

theorem ai_representability_as_fixedness (H : AIHost) :
    forall p : H.C, Representable H p <-> FixedByRho H p := by
  intro p
  constructor
  · rintro ⟨a, rfl⟩
    exact H.gamma_fixed a
  · intro hfixed
    refine ⟨H.alpha p, ?_⟩
    exact (H.rho_eq p).symm.trans hfixed

structure AIModelFamily where
  HostId : Type
  host : HostId -> AIHost
  finiteFamily : Bool
  allHostsAdmissible : Bool
  packagingRole : forall k : HostId, ClosureOperatorOn (host k) (host k).rho
  descentRole : forall k : HostId,
    AbstractSoundness (host k) <-> ConcreteSoundness (host k)
  representabilityRole : forall k : HostId, forall p : (host k).C,
    Representable (host k) p <-> FixedByRho (host k) p
  auditPresent : Bool
  nonclaimsRecorded : Bool

def RealizesAIFragment (fam : AIModelFamily) : Prop :=
  fam.finiteFamily = true /\
    fam.allHostsAdmissible = true /\
    (forall k : fam.HostId, ClosureOperatorOn (fam.host k) (fam.host k).rho) /\
    (forall k : fam.HostId,
      AbstractSoundness (fam.host k) <-> ConcreteSoundness (fam.host k)) /\
    (forall k : fam.HostId, forall p : (fam.host k).C,
      Representable (fam.host k) p <-> FixedByRho (fam.host k) p) /\
    fam.auditPresent = true /\
    fam.nonclaimsRecorded = true

theorem ai_model_family
    (fam : AIModelFamily)
    (hfinite : fam.finiteFamily = true)
    (hadm : fam.allHostsAdmissible = true)
    (haudit : fam.auditPresent = true)
    (hnonclaims : fam.nonclaimsRecorded = true) :
    RealizesAIFragment fam := by
  exact ⟨hfinite, hadm, fam.packagingRole, fam.descentRole,
    fam.representabilityRole, haudit, hnonclaims⟩

end SixBirdsIII
