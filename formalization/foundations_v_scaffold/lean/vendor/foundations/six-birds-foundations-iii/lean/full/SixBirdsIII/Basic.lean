namespace SixBirdsIII

inductive Primitive where
  | P1
  | P2
  | P3
  | P4
  | P5
  | P6
  deriving DecidableEq, Repr

def primitiveLabels : List Primitive :=
  [Primitive.P1, Primitive.P2, Primitive.P3, Primitive.P4, Primitive.P5, Primitive.P6]

theorem primitiveLabels_length : primitiveLabels.length = 6 := rfl

inductive Level where
  | behavioral
  | verification
  | structural
  deriving DecidableEq, Repr

def levels : List Level :=
  [Level.behavioral, Level.verification, Level.structural]

theorem levels_length : levels.length = 3 := rfl

inductive Host where
  | fin
  | prob
  | graph
  | ai
  | pica
  | cantorShell
  | decoratedCategory
  | instrument
  deriving DecidableEq, Repr

def hosts : List Host :=
  [Host.fin, Host.prob, Host.graph, Host.ai, Host.pica,
   Host.cantorShell, Host.decoratedCategory, Host.instrument]

theorem hosts_length : hosts.length = 8 := rfl

end SixBirdsIII
