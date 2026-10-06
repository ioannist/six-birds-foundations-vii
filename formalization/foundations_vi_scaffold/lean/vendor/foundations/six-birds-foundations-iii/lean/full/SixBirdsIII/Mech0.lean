import SixBirdsIII.Records

namespace SixBirdsIII

def CellPair (cell : DirectedCellRecord) : Primitive × Primitive :=
  (cell.actor, cell.informant)

def CellStatusMap (cell : DirectedCellRecord) : CellStatus :=
  cell.status

def FactorsThrough {A B C : Type} (f : A -> C) (g : A -> B) : Prop :=
  ∃ h : B -> C, ∀ a, f a = h (g a)

structure StatusFactorization where
  code : Primitive -> Primitive -> Primitive
  decode : Primitive -> CellStatus

theorem no_total_algebra
    {Cell : Type}
    (pair : Cell -> Primitive × Primitive)
    (status : Cell -> CellStatus)
    (c1 c2 : Cell)
    (same_pair : pair c1 = pair c2)
    (different_status : status c1 ≠ status c2) :
    ¬ FactorsThrough status pair := by
  intro hfac
  rcases hfac with ⟨h, hh⟩
  apply different_status
  calc
    status c1 = h (pair c1) := hh c1
    _ = h (pair c2) := by rw [same_pair]
    _ = status c2 := (hh c2).symm

theorem no_total_decoder
    {Cell : Type}
    (pair : Cell -> Primitive × Primitive)
    (status : Cell -> CellStatus)
    (c1 c2 : Cell)
    (same_pair : pair c1 = pair c2)
    (different_status : status c1 ≠ status c2) :
    ¬ ∃ (op : Primitive -> Primitive -> Primitive)
        (decode : Primitive -> CellStatus),
      ∀ c, status c = decode (op (pair c).1 (pair c).2) := by
  intro h
  rcases h with ⟨op, decode, hdecode⟩
  exact no_total_algebra pair status c1 c2 same_pair different_status
    ⟨fun p => decode (op p.1 p.2), hdecode⟩

end SixBirdsIII
