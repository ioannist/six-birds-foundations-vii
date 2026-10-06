namespace SixBirdsIII

def Iterate {X : Type} (E : X -> X) : Nat -> X -> X
  | 0 => fun x => x
  | n + 1 => fun x => E (Iterate E n x)

theorem idempotent_saturation {X : Type}
    (E : X -> X)
    (idem : ∀ x : X, E (E x) = E x) :
    ∀ n x, 1 ≤ n -> Iterate E n x = E x := by
  intro n
  cases n with
  | zero =>
      intro x h
      cases h
  | succ n =>
      induction n with
      | zero =>
          intro x _h
          rfl
      | succ n ih =>
          intro x _h
          change E (Iterate E (n + 1) x) = E x
          rw [ih x (Nat.succ_pos n)]
          exact idem x

end SixBirdsIII
