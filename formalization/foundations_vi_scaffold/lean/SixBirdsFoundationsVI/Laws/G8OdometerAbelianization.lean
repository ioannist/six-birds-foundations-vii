/-!
G8 Odometer Abelianization: setup layer, Theorem Parts A/B, and witnesses.

This file formalizes the data and boxed hypotheses from the Setup subsection of
`THEOREMS.md` for G8, plus Theorem Part A (order-independent stabilization and
odometer invariance), Part B (least action), and the concrete case-enumeration
witnesses for confluent route-dependent counters and terminating non-confluence.
-/

namespace SixBirdsFoundationsVI.Laws.G8OdometerAbelianization

/--
Apply a finite list of fired sites to a starting configuration.

The prose law quantifies over unbounded runs, but the Lean setup starts with the
finite prefixes needed for termination and sufficiency statements. `ApplyRun m x
sites` is the configuration obtained by firing the sites in order, ignoring
legality; legality is tracked separately by `LegalRun`.
-/
def ApplyRun {C V : Type} (m : V → C → C) (x : C) : List V → C
  | [] => x
  | v :: rest => ApplyRun m (m v x) rest

/--
A finite legal run from a starting configuration to a final configuration.

The encoding choice is inductive rather than a raw fold predicate: each cons
step records that the next fired site is legal at the current configuration,
then continues from the moved configuration. This keeps the final configuration
explicit for later odometer and stabilization statements while leaving `C` and
`V` as arbitrary types.
-/
inductive LegalRun {C V : Type} (m : V → C → C) (L : V → C → Prop) :
    C → List V → C → Prop where
  | nil (x : C) : LegalRun m L x [] x
  | cons {x y : C} {v : V} {rest : List V} :
      L v x → LegalRun m L (m v x) rest y → LegalRun m L x (v :: rest) y

/--
The finite counter vector of a fired-site list.

This is the Lean version of `u_run(v) = #{ i : v_i = v }`. It needs
`DecidableEq V` only to compare a fired site with the queried site; no finiteness
or `Fintype V` assumption is imposed.
-/
def RunCounter {V : Type} [DecidableEq V] : List V → V → Nat
  | [], _ => 0
  | fired :: rest, v => (if fired = v then 1 else 0) + RunCounter rest v

/--
A fired-site list has exactly the declared counter vector.

This is the multiset/order bridge used by sufficiency: the list supplies one
admissible ordering, while this predicate says its multiplicities are the
declared script `n : V → Nat`.
-/
def HasCounter {V : Type} [DecidableEq V] (sites : List V) (n : V → Nat) :
    Prop :=
  ∀ v : V, RunCounter sites v = n v

/--
A configuration is stable when no site is legal.
-/
def Stable {C V : Type} (L : V → C → Prop) (c : C) : Prop :=
  ∀ v : V, ¬ L v c

/--
A declared script is sufficient from `x` when some ordering of exactly that
script is a legal run from `x` to a stable final configuration.

This predicate requires a genuine `LegalRun`: it compares only scripts that are
realized by an admissible legal firing order. Consequently `least_action` below
proves minimality only against other legally-realizable sufficient scripts, not
against the fully general Fey-Levine-Peres comparison class of force-fired
scripts with illegal intermediate steps. The definition is finite-prefix/
termination oriented; non-terminating behavior is handled by later theorem and
case-enumeration layers, not by this setup predicate.
-/
def Sufficient {C V : Type} [DecidableEq V] (m : V → C → C)
    (L : V → C → Prop) (x : C) (n : V → Nat) : Prop :=
  ∃ sites : List V, ∃ final : C,
    HasCounter sites n ∧ LegalRun m L x sites final ∧ Stable L final

/--
A site is necessary at `x` when every sufficient stabilizing script from `x`
fires it at least once.

This is derived from `Sufficient`, not supplied as an unconstrained parameter.
That matters for `[H-G8-mono]`: necessity is tied to the declared stabilizing
scripts rather than to a free predicate that could make the monotonicity package
vacuous.
-/
def Necessary {C V : Type} [DecidableEq V] (m : V → C → C)
    (L : V → C → Prop) (x : C) (v : V) : Prop :=
  ∀ n : V → Nat, Sufficient m L x n → 0 < n v

/--
Pointwise comparison of counter vectors.

This is separated out because `[H-G8-mono]` says stabilizing scripts are
compared pointwise, rather than by an arbitrary order.
-/
def PointwiseLE {V : Type} (n k : V → Nat) : Prop :=
  ∀ v : V, n v ≤ k v

/--
A legal prefix has not exceeded the declared script `n`.

This is the prefix-side version of pointwise script comparison used by the
least-action exchange argument: before the first alleged over-fire, every site
count is still bounded by the comparison script.
-/
def PrefixBoundedBy {V : Type} [DecidableEq V] (firedPrefix : List V)
    (n : V → Nat) : Prop :=
  ∀ v : V, RunCounter firedPrefix v ≤ n v

/--
`[H-G8]`: abelian compatibility for distinct simultaneously legal sites.

The hypothesis is explicitly restricted to `v ≠ w`; the `v = w` case is outside
its scope. Moves are represented as total functions guarded by legality. Thus
"both composites are defined" is formalized by preserving the cross-legality
guards `L w (m v c)` and `L v (m w c)` and then requiring the two composites to
agree directly.
-/
def AbelianCompatible {C V : Type} (m : V → C → C) (L : V → C → Prop) :
    Prop :=
  ∀ (c : C) (v w : V), v ≠ w → L v c → L w c →
    L w (m v c) ∧
      L v (m w c) ∧
        m w (m v c) = m v (m w c)

/--
`[H-G8-mono]`: the separate monotonicity package needed for least action.

The previous version of this definition was vacuous: after assuming pointwise
script comparison, positivity preservation was just arithmetic. The corrected
shape is an exchange/domination property on legal prefixes. If `n` is already a
sufficient script from `x`, then no legal prefix whose fired-site counts are
still pointwise bounded by `n` can sit at a configuration where a site `v` is
legal after that prefix has already spent all of `n v`.

This is the abstract content needed by the least-action proof spine: at the
first alleged over-fire relative to a sufficient script, the prefix is bounded
everywhere, exactly exhausted at the over-fired site, and still legally fires
that site. `[H-G8-mono]` rules out that situation. The condition is not a pure
arithmetic fact about `RunCounter`; it constrains the interaction of
`LegalRun`, `Sufficient`, the move family `m`, and legality `L`.
-/
def LeastActionMonotonicity {C V : Type} [DecidableEq V] (m : V → C → C)
    (L : V → C → Prop) : Prop :=
  ∀ (x : C) (firedPrefix : List V) (c : C) (n : V → Nat) (v : V),
    LegalRun m L x firedPrefix c →
      Sufficient m L x n →
        PrefixBoundedBy firedPrefix n →
          RunCounter firedPrefix v = n v →
            L v c → False

/--
One legal firing step, used to express termination independently of any chosen
finite run list.
-/
def Steps {C V : Type} (m : V → C → C) (L : V → C → Prop)
    (c c' : C) : Prop :=
  ∃ v : V, L v c ∧ c' = m v c

/--
No infinite legal firing sequence starts at `x`.

Lean core's `Acc` is the Mathlib-free well-foundedness/accessibility predicate.
`TerminatesFrom m L x` says the one-step relation generated by legal moves is
accessible at `x`, which is the formal counterpart of "every maximal legal run
from `x` terminates." The finite Part-A proof below only needs the two displayed
terminating runs, but the theorem signatures retain this hypothesis to match
the prose statement.
-/
def TerminatesFrom {C V : Type} (m : V → C → C) (L : V → C → Prop)
    (x : C) : Prop :=
  Acc (fun c' c => Steps m L c c') x

/--
A legal run starting at an already stable configuration must be the empty run.

This is the base case for comparing two stable terminating runs.
-/
theorem stable_legal_run_empty {C V : Type} [DecidableEq V]
    {m : V → C → C} {L : V → C → Prop} {x final : C} {sites : List V}
    (hstable : Stable L x) (hrun : LegalRun m L x sites final) :
    final = x ∧ ∀ v : V, RunCounter sites v = 0 := by
  cases hrun with
  | nil x =>
      exact ⟨rfl, by intro v; rfl⟩
  | cons hleg _htail =>
      exact False.elim ((hstable _) hleg)

/--
Adding the same first fired site to two lists preserves counter equality.
-/
theorem runCounter_cons_congr {V : Type} [DecidableEq V] (v : V)
    {left right : List V}
    (h : ∀ q : V, RunCounter left q = RunCounter right q) :
    ∀ q : V, RunCounter (v :: left) q = RunCounter (v :: right) q := by
  intro q
  simp [RunCounter, h q]

/--
If a site is legal at the start of a legal run ending stably, then that site can
be commuted to the front of the run without changing the final configuration or
the counter vector.

This is the labelled diamond step lifted along a finite stable run. It is the
main auxiliary lemma for Part A.
-/
theorem extract_first_move {C V : Type} [DecidableEq V]
    {m : V → C → C} {L : V → C → Prop}
    (habelian : AbelianCompatible m L)
    {x final : C} {sites : List V} {v : V}
    (hlegal : L v x)
    (hrun : LegalRun m L x sites final)
    (hstable : Stable L final) :
    ∃ tail : List V,
      LegalRun m L (m v x) tail final ∧
        ∀ q : V, RunCounter (v :: tail) q = RunCounter sites q := by
  induction hrun generalizing v with
  | nil x =>
      exact False.elim ((hstable _) hlegal)
  | cons hfirst htail ih =>
      rename_i x y fired rest
      by_cases hsame : fired = v
      · subst hsame
        refine ⟨rest, htail, ?_⟩
        intro q
        rfl
      · have hswap := habelian x v fired (by intro hv; exact hsame hv.symm) hlegal hfirst
        rcases hswap with ⟨hFiredAfterV, hVAfterFired, hcomm⟩
        rcases ih hVAfterFired hstable with ⟨tail, htailFromV, hcountTail⟩
        refine ⟨fired :: tail, ?_, ?_⟩
        · exact LegalRun.cons hFiredAfterV (hcomm ▸ htailFromV)
        · intro q
          have htailCount := hcountTail q
          dsimp [RunCounter] at htailCount ⊢
          omega

/--
G8 Part A, combined form: stable legal terminating runs from the same starting
configuration have the same final configuration and the same counter vector.
-/
theorem partA_order_independent_and_odometer {C V : Type} [DecidableEq V]
    {m : V → C → C} {L : V → C → Prop} {x final₁ final₂ : C}
    {sites₁ sites₂ : List V}
    (habelian : AbelianCompatible m L)
    (_hterminates : TerminatesFrom m L x)
    (hrun₁ : LegalRun m L x sites₁ final₁)
    (hstable₁ : Stable L final₁)
    (hrun₂ : LegalRun m L x sites₂ final₂)
    (hstable₂ : Stable L final₂) :
    final₁ = final₂ ∧ ∀ v : V, RunCounter sites₁ v = RunCounter sites₂ v := by
  induction hrun₁ generalizing sites₂ final₂ with
  | nil x =>
      have hempty := stable_legal_run_empty hstable₁ hrun₂
      exact ⟨hempty.1.symm, by intro v; rw [hempty.2 v]; rfl⟩
  | cons hfirst htail ih =>
      rename_i x y fired rest
      rcases extract_first_move habelian hfirst hrun₂ hstable₂ with
        ⟨tail₂, htail₂, hcountExtract⟩
      have hterminatesTail : TerminatesFrom m L (m fired x) := by
        exact Acc.inv _hterminates ⟨fired, hfirst, rfl⟩
      have hrec := ih hterminatesTail hstable₁ htail₂ hstable₂
      exact ⟨hrec.1, by
        intro q
        calc
          RunCounter (fired :: rest) q = RunCounter (fired :: tail₂) q :=
            runCounter_cons_congr fired hrec.2 q
          _ = RunCounter sites₂ q := hcountExtract q⟩

/--
G8 Part A, order-independent stabilization projection.
-/
theorem order_independent_stabilization {C V : Type} [DecidableEq V]
    {m : V → C → C} {L : V → C → Prop} {x final₁ final₂ : C}
    {sites₁ sites₂ : List V}
    (habelian : AbelianCompatible m L)
    (hterminates : TerminatesFrom m L x)
    (hrun₁ : LegalRun m L x sites₁ final₁)
    (hstable₁ : Stable L final₁)
    (hrun₂ : LegalRun m L x sites₂ final₂)
    (hstable₂ : Stable L final₂) :
    final₁ = final₂ :=
  (partA_order_independent_and_odometer habelian hterminates hrun₁ hstable₁
    hrun₂ hstable₂).1

/--
G8 Part A, odometer-invariance projection.
-/
theorem odometer_invariance {C V : Type} [DecidableEq V]
    {m : V → C → C} {L : V → C → Prop} {x final₁ final₂ : C}
    {sites₁ sites₂ : List V}
    (habelian : AbelianCompatible m L)
    (hterminates : TerminatesFrom m L x)
    (hrun₁ : LegalRun m L x sites₁ final₁)
    (hstable₁ : Stable L final₁)
    (hrun₂ : LegalRun m L x sites₂ final₂)
    (hstable₂ : Stable L final₂) :
    ∀ v : V, RunCounter sites₁ v = RunCounter sites₂ v :=
  (partA_order_independent_and_odometer habelian hterminates hrun₁ hstable₁
    hrun₂ hstable₂).2

/--
Appending one legal firing to the end of a legal run gives another legal run.

Part B uses this to grow the "already-fired prefix" while preserving the fact
that it is a legal prefix from the original start state.
-/
theorem legalRun_snoc {C V : Type} {m : V → C → C} {L : V → C → Prop}
    {x c : C} {firedPrefix : List V} {v : V}
    (hrun : LegalRun m L x firedPrefix c) (hlegal : L v c) :
    LegalRun m L x (firedPrefix ++ [v]) (m v c) := by
  induction hrun with
  | nil x =>
      exact LegalRun.cons hlegal (LegalRun.nil (m v x))
  | cons hfirst _htail ih =>
      exact LegalRun.cons hfirst (ih hlegal)

/--
Counter update for appending a single fired site.

This is the arithmetic step behind the first-violation argument.
-/
theorem runCounter_append_single {V : Type} [DecidableEq V]
    (firedPrefix : List V) (fired q : V) :
    RunCounter (firedPrefix ++ [fired]) q =
      RunCounter firedPrefix q + (if fired = q then 1 else 0) := by
  induction firedPrefix with
  | nil =>
      simp [RunCounter]
  | cons head tail ih =>
      dsimp [RunCounter]
      rw [ih]
      omega

/--
If a prefix is bounded by `n` and the next fired site is still strictly below
its `n`-budget, then appending that firing keeps the prefix bounded.
-/
theorem prefixBounded_snoc {V : Type} [DecidableEq V]
    {firedPrefix : List V} {n : V → Nat} {fired : V}
    (hbounded : PrefixBoundedBy firedPrefix n)
    (hroom : RunCounter firedPrefix fired < n fired) :
    PrefixBoundedBy (firedPrefix ++ [fired]) n := by
  intro q
  rw [runCounter_append_single firedPrefix fired q]
  by_cases hq : fired = q
  · subst hq
    simp
    omega
  · simp [hq]
    exact hbounded q

/--
Least-action prefix lemma.

Starting from a legal prefix whose counters are bounded by a sufficient script
`n`, every legal continuation remains bounded by `n`. If the next move would be
the first violation, then the previous prefix is bounded, exhausted at that
site, and the site is legal; this is exactly the contradiction supplied by
`LeastActionMonotonicity`.
-/
theorem legalRun_counts_bounded_from_prefix {C V : Type} [DecidableEq V]
    {m : V → C → C} {L : V → C → Prop} {x c final : C}
    {firedPrefix tail : List V} {n : V → Nat}
    (hmono : LeastActionMonotonicity m L)
    (hsufficient : Sufficient m L x n)
    (hprefixRun : LegalRun m L x firedPrefix c)
    (hprefixBound : PrefixBoundedBy firedPrefix n)
    (htail : LegalRun m L c tail final) :
    ∀ v : V, RunCounter (firedPrefix ++ tail) v ≤ n v := by
  induction htail generalizing firedPrefix with
  | nil c =>
      intro v
      simpa using hprefixBound v
  | cons hlegal _htail ih =>
      rename_i c' y fired rest
      by_cases hroom : RunCounter firedPrefix fired < n fired
      · have hprefixRun' : LegalRun m L x (firedPrefix ++ [fired]) (m fired c') :=
          legalRun_snoc hprefixRun hlegal
        have hprefixBound' : PrefixBoundedBy (firedPrefix ++ [fired]) n :=
          prefixBounded_snoc hprefixBound hroom
        intro v
        have hrec := ih hprefixRun' hprefixBound' v
        simpa [List.append_assoc] using hrec
      · have hexhausted : RunCounter firedPrefix fired = n fired := by
          have hle := hprefixBound fired
          have hnle : n fired ≤ RunCounter firedPrefix fired := Nat.le_of_not_gt hroom
          exact Nat.le_antisymm hle hnle
        exact False.elim
          (hmono x firedPrefix c' n fired hprefixRun hsufficient hprefixBound
            hexhausted hlegal)

/--
G8 Part B: least action.

For any legal stabilization from `x`, its counter vector is pointwise minimal
among all legally sufficient scripts from `x`. This is the legal-vs-legal
comparison proved by the present Lean hypotheses. It does not prove the fully
general Fey-Levine-Peres principle comparing the legal odometer with arbitrary
nonnegative stabilizing scripts that may require illegal/out-of-turn
intermediate topplings. Part A makes the chosen legal stabilization's counter
vector independent of the legal order; this theorem is the pointwise minimality
statement for any representative legal stabilization.
`AbelianCompatible` is included as the standing system hypothesis from the prose
theorem header, though this proof uses the exchange content already packaged in
`LeastActionMonotonicity`.
-/
theorem least_action {C V : Type} [DecidableEq V]
    {m : V → C → C} {L : V → C → Prop} {x final : C}
    {sites : List V} {n : V → Nat}
    (_habelian : AbelianCompatible m L)
    (hmono : LeastActionMonotonicity m L)
    (hrun : LegalRun m L x sites final)
    (_hstable : Stable L final)
    (hsufficient : Sufficient m L x n) :
    ∀ v : V, RunCounter sites v ≤ n v := by
  have hprefixRun : LegalRun m L x ([] : List V) x := LegalRun.nil x
  have hprefixBound : PrefixBoundedBy ([] : List V) n := by
    intro v
    exact Nat.zero_le _
  have hbounded :=
    legalRun_counts_bounded_from_prefix hmono hsufficient hprefixRun
      hprefixBound hrun
  intro v
  simpa using hbounded v

/-
Case-enumeration witnesses.

The prose case table for G8 is not a decision procedure for all systems. The
two concrete witnesses below mechanize the separating examples: confluence does
not imply canonical counters, and termination does not imply confluence.
-/

/--
States for case (b): `S` branches to `A` or `B`, and all maximal branches
terminate at the shared normal state `N`.
-/
inductive CaseBState where
  | S
  | A
  | B
  | N
  deriving DecidableEq

/--
Moves for case (b): `r,s` choose branches from `S`; `p,t` close the `A` branch;
`q` closes the `B` branch.
-/
inductive CaseBMove where
  | r
  | s
  | p
  | q
  | t
  deriving DecidableEq

/--
Total move function for case (b), guarded by `caseBLegal` for actual runs.
Illegal applications are fixed as identity values only so the move family has
the total-function shape used by the G8 setup.
-/
def caseBMove : CaseBMove → CaseBState → CaseBState
  | CaseBMove.r, CaseBState.S => CaseBState.A
  | CaseBMove.s, CaseBState.S => CaseBState.B
  | CaseBMove.p, CaseBState.A => CaseBState.N
  | CaseBMove.q, CaseBState.B => CaseBState.N
  | CaseBMove.t, CaseBState.A => CaseBState.N
  | _, c => c

/--
Legality predicate for case (b): exactly `r,s` at `S`, `p,t` at `A`, and `q`
at `B`; no move is legal at `N`.
-/
def caseBLegal : CaseBMove → CaseBState → Prop
  | CaseBMove.r, CaseBState.S => True
  | CaseBMove.s, CaseBState.S => True
  | CaseBMove.p, CaseBState.A => True
  | CaseBMove.t, CaseBState.A => True
  | CaseBMove.q, CaseBState.B => True
  | _, _ => False

/--
Case (b) fails `[H-G8]`: after `r` and `s` compete at `S`, firing `r` destroys
the legality of `s`, so the distinct legal moves do not commute.
-/
theorem caseB_not_abelian : ¬ AbelianCompatible caseBMove caseBLegal := by
  intro h
  have hcomp :=
    h CaseBState.S CaseBMove.r CaseBMove.s (by decide) trivial trivial
  exact hcomp.1

/--
The normal state `N` in case (b) is stable.
-/
theorem caseB_stable_N : Stable caseBLegal CaseBState.N := by
  intro v h
  cases v <;> cases h

/--
No case (b) move is legal at `N`.
-/
theorem caseB_no_legal_N (v : CaseBMove) : ¬ caseBLegal v CaseBState.N := by
  intro h
  cases v <;> cases h

/--
Any stable legal run beginning at `N` must end at `N`, since no case (b) move
is legal at `N`.
-/
theorem caseB_stable_run_from_N {sites : List CaseBMove} {final : CaseBState}
    (hrun : LegalRun caseBMove caseBLegal CaseBState.N sites final)
    (_hstable : Stable caseBLegal final) :
    final = CaseBState.N := by
  cases hrun with
  | nil x =>
      rfl
  | cons hlegal _hrest =>
      exact False.elim (caseB_no_legal_N _ hlegal)

/--
After any legal move from `A`, the remaining case (b) run starts at `N`.
-/
theorem caseB_after_A_move_ends_N {fired : CaseBMove} {sites : List CaseBMove}
    {final : CaseBState}
    (hlegal : caseBLegal fired CaseBState.A)
    (hrest : LegalRun caseBMove caseBLegal
      (caseBMove fired CaseBState.A) sites final)
    (hstable : Stable caseBLegal final) :
    final = CaseBState.N := by
  cases fired
  · cases hlegal
  · cases hlegal
  · exact caseB_stable_run_from_N hrest hstable
  · cases hlegal
  · exact caseB_stable_run_from_N hrest hstable

/--
Any stable legal run beginning at `A` must continue through either `p` or `t`
and therefore end at `N`; stopping at `A` is impossible because `p` and `t` are
legal there.
-/
theorem caseB_stable_run_from_A {sites : List CaseBMove} {final : CaseBState}
    (hrun : LegalRun caseBMove caseBLegal CaseBState.A sites final)
    (hstable : Stable caseBLegal final) :
    final = CaseBState.N := by
  cases hrun with
  | nil x =>
      exact False.elim ((hstable CaseBMove.p) trivial)
  | cons hlegal hrest =>
      exact caseB_after_A_move_ends_N hlegal hrest hstable

/--
After any legal move from `B`, the remaining case (b) run starts at `N`.
-/
theorem caseB_after_B_move_ends_N {fired : CaseBMove} {sites : List CaseBMove}
    {final : CaseBState}
    (hlegal : caseBLegal fired CaseBState.B)
    (hrest : LegalRun caseBMove caseBLegal
      (caseBMove fired CaseBState.B) sites final)
    (hstable : Stable caseBLegal final) :
    final = CaseBState.N := by
  cases fired
  · cases hlegal
  · cases hlegal
  · cases hlegal
  · exact caseB_stable_run_from_N hrest hstable
  · cases hlegal

/--
Any stable legal run beginning at `B` must continue through `q` and therefore
end at `N`; stopping at `B` is impossible because `q` is legal there.
-/
theorem caseB_stable_run_from_B {sites : List CaseBMove} {final : CaseBState}
    (hrun : LegalRun caseBMove caseBLegal CaseBState.B sites final)
    (hstable : Stable caseBLegal final) :
    final = CaseBState.N := by
  cases hrun with
  | nil x =>
      exact False.elim ((hstable CaseBMove.q) trivial)
  | cons hlegal hrest =>
      exact caseB_after_B_move_ends_N hlegal hrest hstable

/--
After any legal move from `S`, the remaining case (b) run starts at `A` or `B`,
and therefore any stable completion ends at `N`.
-/
theorem caseB_after_S_move_ends_N {fired : CaseBMove} {sites : List CaseBMove}
    {final : CaseBState}
    (hlegal : caseBLegal fired CaseBState.S)
    (hrest : LegalRun caseBMove caseBLegal
      (caseBMove fired CaseBState.S) sites final)
    (hstable : Stable caseBLegal final) :
    final = CaseBState.N := by
  cases fired
  · exact caseB_stable_run_from_A hrest hstable
  · exact caseB_stable_run_from_B hrest hstable
  · cases hlegal
  · cases hlegal
  · cases hlegal

/--
General case (b) confluence: every stable legal run from `S`, not just the three
displayed routes, ends at the unique normal form `N`.
-/
theorem caseB_stable_run_from_S_ends_N {sites : List CaseBMove}
    {final : CaseBState}
    (hrun : LegalRun caseBMove caseBLegal CaseBState.S sites final)
    (hstable : Stable caseBLegal final) :
    final = CaseBState.N := by
  cases hrun with
  | nil x =>
      exact False.elim ((hstable CaseBMove.r) trivial)
  | cons hlegal hrest =>
      exact caseB_after_S_move_ends_N hlegal hrest hstable

/--
`N` is accessible for the case (b) step relation because no legal step leaves
`N`.
-/
theorem caseB_terminates_from_N :
    TerminatesFrom caseBMove caseBLegal CaseBState.N := by
  apply Acc.intro
  intro y hstep
  cases hstep with
  | intro v hv =>
      cases hv with
      | intro hlegal _hy =>
          cases v <;> cases hlegal

/--
`A` is accessible in case (b): every legal step from `A` goes to `N`.
-/
theorem caseB_terminates_from_A :
    TerminatesFrom caseBMove caseBLegal CaseBState.A := by
  apply Acc.intro
  intro y hstep
  cases hstep with
  | intro v hv =>
      cases hv with
      | intro hlegal hy =>
          cases v
          · cases hlegal
          · cases hlegal
          · subst y
            exact caseB_terminates_from_N
          · cases hlegal
          · subst y
            exact caseB_terminates_from_N

/--
`B` is accessible in case (b): its only legal step goes to `N`.
-/
theorem caseB_terminates_from_B :
    TerminatesFrom caseBMove caseBLegal CaseBState.B := by
  apply Acc.intro
  intro y hstep
  cases hstep with
  | intro v hv =>
      cases hv with
      | intro hlegal hy =>
          cases v
          · cases hlegal
          · cases hlegal
          · cases hlegal
          · subst y
            exact caseB_terminates_from_N
          · cases hlegal

/--
Case (b) terminates from `S`: the two legal first moves go to `A` and `B`, both
already accessible.
-/
theorem caseB_terminates_from_S :
    TerminatesFrom caseBMove caseBLegal CaseBState.S := by
  apply Acc.intro
  intro y hstep
  cases hstep with
  | intro v hv =>
      cases hv with
      | intro hlegal hy =>
          cases v
          · subst y
            exact caseB_terminates_from_A
          · subst y
            exact caseB_terminates_from_B
          · cases hlegal
          · cases hlegal
          · cases hlegal

/--
The first case (b) maximal route, `S --r--> A --p--> N`, is legal.
-/
theorem caseB_run_rp :
    LegalRun caseBMove caseBLegal CaseBState.S
      [CaseBMove.r, CaseBMove.p] CaseBState.N := by
  apply LegalRun.cons
  · trivial
  · apply LegalRun.cons
    · trivial
    · exact LegalRun.nil CaseBState.N

/--
The second case (b) maximal route, `S --r--> A --t--> N`, is legal.
-/
theorem caseB_run_rt :
    LegalRun caseBMove caseBLegal CaseBState.S
      [CaseBMove.r, CaseBMove.t] CaseBState.N := by
  apply LegalRun.cons
  · trivial
  · apply LegalRun.cons
    · trivial
    · exact LegalRun.nil CaseBState.N

/--
The third case (b) maximal route, `S --s--> B --q--> N`, is legal.
-/
theorem caseB_run_sq :
    LegalRun caseBMove caseBLegal CaseBState.S
      [CaseBMove.s, CaseBMove.q] CaseBState.N := by
  apply LegalRun.cons
  · trivial
  · apply LegalRun.cons
    · trivial
    · exact LegalRun.nil CaseBState.N

/--
The three displayed case (b) routes are confluent in the concrete sense needed
for the witness: they share the same stable final state `N`.
-/
theorem caseB_confluent_runs_share_final :
    ∃ final : CaseBState,
      LegalRun caseBMove caseBLegal CaseBState.S
        [CaseBMove.r, CaseBMove.p] final ∧
      LegalRun caseBMove caseBLegal CaseBState.S
        [CaseBMove.r, CaseBMove.t] final ∧
      LegalRun caseBMove caseBLegal CaseBState.S
        [CaseBMove.s, CaseBMove.q] final ∧
      Stable caseBLegal final := by
  exact ⟨CaseBState.N, caseB_run_rp, caseB_run_rt, caseB_run_sq,
    caseB_stable_N⟩

/--
The `r,p` route fires `s` zero times.
-/
theorem caseB_counter_rp_s_zero :
    RunCounter [CaseBMove.r, CaseBMove.p] CaseBMove.s = 0 := by
  rfl

/--
The `s,q` route fires `s` once.
-/
theorem caseB_counter_sq_s_one :
    RunCounter [CaseBMove.s, CaseBMove.q] CaseBMove.s = 1 := by
  rfl

/--
Case (b) has route-dependent counters even though the displayed maximal routes
share the same stable normal form.
-/
theorem caseB_route_dependent_counter :
    RunCounter [CaseBMove.r, CaseBMove.p] CaseBMove.s ≠
      RunCounter [CaseBMove.s, CaseBMove.q] CaseBMove.s := by
  intro h
  have h0 : RunCounter [CaseBMove.r, CaseBMove.p] CaseBMove.s = 0 :=
    caseB_counter_rp_s_zero
  have h1 : RunCounter [CaseBMove.s, CaseBMove.q] CaseBMove.s = 1 :=
    caseB_counter_sq_s_one
  rw [h0, h1] at h
  cases h

/--
States for case (d): `S` has two one-step legal exits to distinct normal states.
-/
inductive CaseDState where
  | S
  | A
  | B
  deriving DecidableEq

/--
Moves for case (d): two competing exits from `S`.
-/
inductive CaseDMove where
  | r
  | s
  deriving DecidableEq

/--
Total move function for case (d), guarded by `caseDLegal` for actual runs.
-/
def caseDMove : CaseDMove → CaseDState → CaseDState
  | CaseDMove.r, CaseDState.S => CaseDState.A
  | CaseDMove.s, CaseDState.S => CaseDState.B
  | _, c => c

/--
Legality predicate for case (d): both exits are legal only at `S`; `A` and `B`
are normal.
-/
def caseDLegal : CaseDMove → CaseDState → Prop
  | CaseDMove.r, CaseDState.S => True
  | CaseDMove.s, CaseDState.S => True
  | _, _ => False

/--
The `A` final state in case (d) is stable.
-/
theorem caseD_stable_A : Stable caseDLegal CaseDState.A := by
  intro v h
  cases v <;> cases h

/--
The `B` final state in case (d) is stable.
-/
theorem caseD_stable_B : Stable caseDLegal CaseDState.B := by
  intro v h
  cases v <;> cases h

/--
Case (d) terminates from `S`: both legal first moves reach already stable
states.
-/
theorem caseD_terminates_from_S :
    TerminatesFrom caseDMove caseDLegal CaseDState.S := by
  apply Acc.intro
  intro y hstep
  cases hstep with
  | intro v hv =>
      cases hv with
      | intro hlegal hy =>
          cases v
          · subst y
            apply Acc.intro
            intro z hstepA
            cases hstepA with
            | intro w hw =>
                cases hw with
                | intro hlegalA _hz =>
                    cases w <;> cases hlegalA
          · subst y
            apply Acc.intro
            intro z hstepB
            cases hstepB with
            | intro w hw =>
                cases hw with
                | intro hlegalB _hz =>
                    cases w <;> cases hlegalB

/--
The first case (d) route, `S --r--> A`, is legal and reaches a stable state.
-/
theorem caseD_run_r :
    LegalRun caseDMove caseDLegal CaseDState.S [CaseDMove.r] CaseDState.A := by
  apply LegalRun.cons
  · trivial
  · exact LegalRun.nil CaseDState.A

/--
The second case (d) route, `S --s--> B`, is legal and reaches a stable state.
-/
theorem caseD_run_s :
    LegalRun caseDMove caseDLegal CaseDState.S [CaseDMove.s] CaseDState.B := by
  apply LegalRun.cons
  · trivial
  · exact LegalRun.nil CaseDState.B

/--
The two stable final states in case (d) are distinct.
-/
theorem caseD_final_states_distinct : CaseDState.A ≠ CaseDState.B := by
  decide

/--
Case (d) is terminating but non-confluent in the displayed concrete sense: two
legal one-step routes from the same start reach distinct stable final states.
-/
theorem caseD_nonconfluent_witness :
    LegalRun caseDMove caseDLegal CaseDState.S [CaseDMove.r] CaseDState.A ∧
      Stable caseDLegal CaseDState.A ∧
      LegalRun caseDMove caseDLegal CaseDState.S [CaseDMove.s] CaseDState.B ∧
      Stable caseDLegal CaseDState.B ∧
      CaseDState.A ≠ CaseDState.B := by
  exact ⟨caseD_run_r, caseD_stable_A, caseD_run_s, caseD_stable_B,
    caseD_final_states_distinct⟩

end SixBirdsFoundationsVI.Laws.G8OdometerAbelianization
