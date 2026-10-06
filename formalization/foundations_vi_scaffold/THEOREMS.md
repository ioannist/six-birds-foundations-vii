# Foundations VI Target-State Theorem Catalog

This file is the target-state catalog for *Six Birds Foundations VI: Closure in Motion*. The build-ready source of truth remains the `design/` folder while Phase 1 is underway; once this file is populated and accepted, it supersedes `design/02_LAW_CATALOG.md` as the canonical law text and leaves that file as background and audit history.

## Legend

**Six-part normal form.** Setup declares the abstract data, including the temporal or growing quantifier and the nearest Foundations IV cousin. Theorem states the layer-agnostic claim with named hypotheses when needed. Proof spine records the structural proof route and citation trail. Case enumeration gives mutually exclusive statuses and witness data. Interaction status explains the BirdInt primitive roles and gates. Nonclaims records what the law does not assert.

**Status tags.** `theorem` means the abstract claim is proved in-paper, usually by adapting a complete classical proof. `schema` means the claim is an implication with named obligations whose general discharge is not yet proved. `calibration-anchored schema` means a schema whose mechanism is fully verified on at least one solved instance.

**Instance tags.** `calibration` means the instance is solved mathematics or a completely certified model for the mechanism. `conjectural` means the intended instance contains an open or unverified hypothesis and carries no closure claim. `structural` means the instance is a cited analogy or typed target whose full G-law hypotheses still need checking.

## Index

#### Cluster A - Temporal currencies: solvency, escrow, and credit

- **G1 - Hidden Amortized Solvency** (`theorem`/`schema` split; flagship: Collatz). A promoted solvency ledger makes eventual descent equivalent to escaping every finite bad-tail membrane, while the ghost-discharge half stays conditional.
- **G2 - Transfinite Escrow** (`theorem`; flagship: Goodstein sequences). Stage-indexed presentation changes are audited by strict descent in a well-founded, often ordinal, escrow carrier.
- **G3 - Amortized Potential Currency** (`theorem`; flagships: binary counters and dynamic arrays). A nonnegative potential turns unbounded local step costs into bounded finite-run cost ledgers by telescoping.

#### Cluster B - Moving and self-generated obstructions

- **G4 - Moving-Cover Exhaustion** (`schema`; flagships: Fibonacci-Sylvester and Erdos-Straus). Infinite target families close only through explicit moving covers and exhaustion budgets, not through local admissibility alone.
- **G5 - Carry-Horizon Confinement** (`calibration-anchored schema`; flagships: base-2 reverse-and-add and Lychrel candidates). Digit dynamics can require a growing predictive carry horizon, with certified escape supplied by closed pattern families.
- **G6 - Endogenous Needle Generation** (`schema`; flagship: Recaman's sequence). The orbit manufactures its own obstruction set, so coverage depends on the audited race between obstruction growth and return pressure.
- **G7 - Adversarial Mobility Confinement** (`calibration-anchored schema`; flagship: the angel problem). Escape or confinement is certified by visible strategies in an unbounded mobility-versus-deletion game.

#### Cluster C - Defect integration and emergent transport

- **G8 - Odometer Abelianization** (`theorem`; flagship: abelian sandpiles). Abelian local moves integrate route dependence into a unique odometer and, with monotonicity, a least-action ledger.
- **G9 - Defect-Evacuation-to-Transport** (`calibration-anchored schema`; flagships: rule 184 and Langton's ant). Defect censuses certify when persistent local disorder resolves into recurrence-with-displacement transport.
- **G10 - Lossful Boundary Persistence** (`theorem`; flagships: Ducci games and Gilbreath). A declared boundary readout persists under repeated lossy operations only when a protecting interior invariant regenerates.

#### Cluster D - Productive obstructions and sparse saturation

- **G11 - Local-Rule Global-Anti-Symmetry** (`theorem`; flagship: aperiodic tilings). Local rules can force hierarchy while producing finite defects against every candidate period.
- **G12 - Finite Witness Radiation** (`theorem`; flagship: Hadwiger-Nelson). A finite obstruction in a homogeneous carrier gives a global impossibility through orbit invariance and compactness.
- **G13 - Thin-Orbit Saturation** (`schema`; flagship: Apollonian circle packings). A technically thin orbit can saturate a positive-density admissible target through expansion, while reciprocity obstructions remain separate residuals.

## Laws

### Cluster A - Temporal currencies: solvency, escrow, and credit

Verified gap: the corpus has currency and descent tools, but not the temporal solvency, ordinal escrow, and finite-run credit ledgers needed for liveness and amortized dynamics. Cluster A records those temporal currency laws.

### G1 - Hidden Amortized Solvency

**Status:** Part (a) is an unconditional `theorem`. Part (b) is `schema`, not yet `calibration-anchored`: binary counters and size-change termination calibrate the solvency-currency mechanism, but no existing instantiation of the real Collatz ghost/completion mechanism yet fully calibrates the ghost-convergence plus native/ghost-separation discharge mechanism. `design/04_LABS.md` G1-L3 now supplies a completed finite-toy exhibit of the discharge mechanism itself (an exhaustive finite residue model with corrected nonterminal set `Gamma_16={14563,21845}`), not a calibration of real Collatz; the real-Collatz calibration route remains open.

#### 1. Setup

Let `X` be a native discrete carrier with update `T: X -> X` and optional accepted terminal set `A subset X`, fixed by `T`. A run from `x` is

```text
x_0=x, x_{j+1}=T(x_j),  j=0,1,2,...
```

The promoted ledger records per-step visible debt `d_j`, hidden payment `p_j`, and any finite-prefix tax term `tax_k(x)`. The solvency currency is

```text
V_k(x) = sum_{j<k}(p_j - d_j) - tax_k(x).
```

A descent certificate is valid only when the boundary inequality is exact:

```text
V_k(x) > 0  <=>  T^k(x) < x
```

for the declared native order. The unbounded quantifier is the law's content: G1 asks whether every nonterminal native `x` eventually has some finite `k` with `V_k(x)>0`; terminal points in `A` are already discharged, and the bad-tail membrane below is imposed only on `X \ A`.

For the Collatz flagship, `X` is all odd positive integers and `A={1}`. The accelerated map is closed on this `X`:

```text
T(n) = (3n+1) / 2^{a(n)},  a(n)=nu_2(3n+1).
```

In particular, `T(1)=1` because `3*1+1=4`, `nu_2(4)=2`, and `4/4=1`, so the known trivial cycle is a genuine fixed point of the accelerated map; also `T(5)=1`, and `1` remains inside `X`.

For the orbit `n_j=T^j(n)`, set

```text
a_j = nu_2(3n_j+1),
A_k = sum_{j<k} a_j,
B_0 = 0,
B_{j+1} = 3 B_j + 2^{A_j}.
```

The exact affine ledger is

```text
n_k = (3^k n + B_k) / 2^{A_k}.
```

This identity is verified by induction. It is true at `k=0` because `A_0=0` and `B_0=0`. If it holds at `k`, then

```text
n_{k+1}
= (3 n_k + 1) / 2^{a_k}
= (3(3^k n + B_k)/2^{A_k} + 1) / 2^{a_k}
= (3^{k+1} n + 3B_k + 2^{A_k}) / 2^{A_k+a_k}
= (3^{k+1} n + B_{k+1}) / 2^{A_{k+1}}.
```

Define the Collatz solvency currency

```text
V_k(n) = A_k log 2 - k log 3 - log(1 + B_k/(3^k n)).
```

Then

```text
n_k/n
= (3^k n + B_k)/(2^{A_k} n)
= (3^k/2^{A_k}) * (1 + B_k/(3^k n)),
```

so

```text
log(n_k/n)
= k log 3 - A_k log 2 + log(1 + B_k/(3^k n))
= -V_k(n).
```

Since `log` is increasing and `n>0`,

```text
V_k(n)>0  <=>  log(n_k/n)<0  <=>  n_k/n<1  <=>  n_k<n.
```

This is the descending boundary certificate. It is an exact integer inequality in the lab; the logarithmic form is presentation.

Let `X_hat` be a completion containing limits of infinite insolvent threads; for Collatz the relevant completion is the `2`-adic integers. Let `Gamma` be the ghost locus: non-descending fixed or periodic points in `X_hat \ X`. In `Z_2`, the point `-1 = ...1111_2` is a ghost because

```text
3(-1)+1 = -2 = 2*(-1),
nu_2(-2)=1,
T(-1)=(-2)/2=-1.
```

For each `k`, define the bad-tail membrane

```text
N_k = { x in X \ A : V_j(x) <= 0 for every 1 <= j <= k }.
```

Thus `x in intersection_k N_k` means that a nonterminal native point never becomes solvent at any finite stage.

**Closest Foundations IV cousin.** F13a, Hiddenness Normal Form, fixes one hiddenness interface: a carrier, one current quotient, one predictive quotient refining it, and predicates saying whether a current fiber contains multiple predictive classes. It is a single-instant exposure/surplus normal form. G1 is a liveness law over an unbounded run: the hidden data are the future valuation ledger, the membranes `N_k` are indexed by time, and the claim asks whether the hidden debt is eventually discharged by a native descent certificate. No F-IV row has this unbounded eventual-solvency quantifier.

For Collatz, the F13a-style split is concrete: computing `T(n) mod 2^m` when `a=nu_2(3n+1)` requires knowing `3n+1 mod 2^{m+a}`, hence `n mod 2^{m+a}`. The valuation `a` is unbounded because the congruence `3n+1 == 0 mod 2^a` has odd solutions for every `a`. Therefore no fixed residue quotient `n mod 2^m` is future-sufficient for all Collatz descent probes.

#### 2. Theorem

**Part (a): Reduction, unconditional.** Pointwise liveness is equivalent to emptiness of the infinite bad-tail intersection:

```text
(for every x in X \ A, exists k>=1 with V_k(x)>0)
<=> intersection_{k>=1} N_k = empty.
```

Equivalently, no nonterminal native point starts an infinite thread that remains in the bad-tail membrane forever. Points in `A` are already terminally discharged.

**Part (b): Discharge schema, conditional.** Add two boxed hypotheses.

**[H-G1-ghost-convergence: ghost convergence, boxed.]** Fix a computable neighborhood system `U_h(Gamma)` in `X_hat` with `intersection_h U_h(Gamma)=Gamma`. Every infinite bad thread based at a nonterminal native point has a limit in `X_hat`, every such limit lies in `Gamma`, and therefore for every `h` the thread is eventually in `U_h(Gamma)`.

**[H-G1-separation: native/ghost separation, boxed.]** For every nonterminal native point `x`, there are computable values `h(x)` and `K(x)` proving that `T^t(x) notin U_{h(x)}(Gamma)` for every `t>=K(x)`, using only native certificates. Equivalently, no nonterminal native orbit can remain compatible with convergence to `Gamma` beyond its certified horizon.

If `[H-G1-ghost-convergence]` and `[H-G1-separation]` both hold, then `intersection_k N_k` is empty. Consequently the bad-tail residual for each nonterminal native point carries AOR status `eventual_zero` pointwise: for each fixed `x`, the predicate `x in N_k` is eventually false. Terminal points in `A` are already discharged. This uses the AOR asymptotic status vocabulary as an object-level run statement; it is not a density or almost-all claim.

For Collatz, both `[H-G1-ghost-convergence]` and `[H-G1-separation]` are unproved. They are named obligations, not evidence that the Collatz conjecture has been proved.

#### 3. Proof Spine

Part (a) is direct. If pointwise liveness holds and a nonterminal `x` were in every `N_k`, then every finite prefix would satisfy `V_j(x)<=0`, contradicting the finite `k` with `V_k(x)>0`. Conversely, if the intersection is empty, then each nonterminal `x` fails membership in some `N_k`; by definition, some `1<=j<=k` has `V_j(x)>0`, giving pointwise liveness. Terminal points in `A` were discharged before the membrane test.

For Part (b), suppose toward contradiction that some nonterminal native `x` lies in every `N_k`. Its orbit is an infinite bad thread. By `[H-G1-ghost-convergence]`, this thread is eventually in `U_{h(x)}(Gamma)`. By `[H-G1-separation]`, the same native orbit is outside `U_{h(x)}(Gamma)` for every `t>=K(x)`. Contradiction. Hence no such `x` exists, so Part (a) gives liveness and the residual is pointwise `eventual_zero`.

The Collatz ghost-shadowing family is unconditional and points in the opposite direction from any fixed-depth proof. Let

```text
n_L = 2^L - 1.
```

For the first step,

```text
3n_L+1 = 3(2^L-1)+1 = 3*2^L - 2 = 2(3*2^{L-1}-1),
```

and `3*2^{L-1}-1` is odd when `L>=2`, so `a_0=1` and `n_1=3*2^{L-1}-1`. For the next step,

```text
3n_1+1 = 3(3*2^{L-1}-1)+1 = 9*2^{L-1}-2 = 2(9*2^{L-2}-1),
```

and `9*2^{L-2}-1` is odd when `L>=3`, so `a_1=1`. In general, for `0<=i<L`,

```text
n_i = 3^i 2^{L-i} - 1.
```

Then for `0<=i<L-1`,

```text
3n_i+1 = 3^{i+1}2^{L-i} - 2
        = 2(3^{i+1}2^{L-i-1} - 1),
```

with the parenthesized factor odd, so `a_i=1`. Thus `2^L-1` shadows the `2`-adic ghost branch for `L-1` accelerated odd steps. This proves arbitrarily long insolvent prefixes exist; it does not prove or disprove Collatz.

The cycle globalization condition also follows from the affine ledger. For a valuation word `(a_0,...,a_{k-1})`, the corresponding affine data give

```text
n_k = (3^k n + B_k)/2^{A_k}.
```

A cycle with this word must satisfy `n_k=n`, hence

```text
2^{A_k} n = 3^k n + B_k,
(2^{A_k}-3^k)n = B_k,
n = B_k / (2^{A_k}-3^k).
```

Therefore the word globalizes to a positive integer cycle only if `2^{A_k}>3^k` and `B_k/(2^{A_k}-3^k)` is a positive integer. This is a local-global residual, not a liveness proof.

#### 4. Case Enumeration

| Case | Status | Witness type |
|---|---|---|
| (a) Terminal or immediate solvent | Either `x in A`, or `x notin A` and `V_1(x)>0`, hence `T(x)<x`. | Terminal membership, or one-step ledger certificate. |
| (b) Finite bad prefix before discharge | There is a least discharge time `k>1`: `x in N_{k-1}` and `V_k(x)>0`. | Bounded membrane audit plus later exact ledger `(A_k,B_k)`; Collatz witnesses include `2^L-1` showing `k-1` can be arbitrarily large. |
| (c) Infinite bad thread | `x in intersection_k N_k`; under Part (b)'s hypotheses this must be ghost-bound and then excluded. | Infinite membrane record; in Collatz this is exactly the unproved obstruction. |

These three rows partition native-point orbit fates by first discharge time: terminal or one-step discharge, later certified discharge after a finite bad prefix, or no finite discharge. They are mutually exclusive after the least discharge time is fixed, and exhaustive for the declared deterministic run.

**Separate local-global cycle question.** A locally admissible valuation word `(a_0,...,a_{k-1})` globalizes to a native cycle exactly when the integrality certificate `n=B_k/(2^{A_k}-3^k)` is a positive integer. Divisibility failure means the local valuation word does not correspond to a native cycle. This is a valuation-word question, not a fourth orbit-fate case.

#### 5. Interaction Status

G1 is the SAU pattern in temporal form. The ledger and completion are promoted support: they need not descend to the native integer layer. The only native assertion is the boundary certificate `V_k(x)>0`, equivalently `T^k(x)<x`. The ghost `-1`, the `2`-adic completion, and the valuation ledger are not literal native objects; using them is legal only through the descended certificate and the named hypotheses. This is NC-18 discipline.

#### 6. Nonclaims

1. G1 does not prove Collatz. Part (a) is an unconditional reduction; Part (b) requires `[H-G1-ghost-convergence]` and `[H-G1-separation]`, which are unproved for Collatz.
2. The `2^L-1` ghost-shadowing family is a real, verified, unconditional fact showing arbitrarily long insolvent prefixes. It is evidence against fixed finite-depth proof strategies, not evidence for or against the Collatz conjecture.
3. Density and drift results are not upgraded to pointwise liveness. Tao's almost-all result for Collatz has `probabilistic` status relative to G1's pointwise target and does not discharge `[H-G1-ghost-convergence]` or `[H-G1-separation]`.
4. Part (b) is not yet `calibration-anchored`: the existing solved examples calibrate amortized solvency, not the real Collatz ghost-convergence/separation discharge mechanism. G1-L3's finite ghost toy is a completed finite-model exhibit of the discharge mechanism, not a calibration of real Collatz; the real-Collatz calibration route remains open.
5. No novelty is claimed for the classical number-theoretic content. G1's contribution is the layer-agnostic solvency/liveness normal form and its explicit split between unconditional reduction and conditional discharge.
6. The ghost, completion, and ledger are promoted objects. Only `V_k(x)>0` / `T^k(x)<x` is asserted at the native integer layer.

#### Layer Instantiations

1. **Collatz accelerated odd map - conjectural flagship.** The exact ledger and solvency certificate are the formulas above. The `2`-adic ghost `-1`, the `2^L-1` finite shadowing family, and the cycle integrality condition are verified algebraic facts. The liveness claim remains open because `[H-G1-ghost-convergence]` and `[H-G1-separation]` are unproved. Citations: Lagarias, "The 3x+1 problem and its generalizations," *American Mathematical Monthly* 92, 3-23, 1985; Lagarias, ed., *The Ultimate Challenge: The 3x+1 Problem*, AMS, 2010; Tao, "Almost all orbits of the Collatz map attain almost bounded values," arXiv:1909.03562.
2. **Binary-counter increment - calibration for solvency currency.** Incrementing a binary counter with `r` trailing ones flips `r+1` bits, so the visible step cost is unbounded. With potential `Phi = number of 1-bits`, the potential change is `1-r`; actual cost plus potential change is `(r+1)+(1-r)=2`. Thus hidden potential pays visible debt exactly on every step. This calibrates the currency mechanism, not the ghost/completion mechanism. Citation: Tarjan, "Amortized Computational Complexity," *SIAM Journal on Algebraic and Discrete Methods* 6(2), 306-318, 1985; Cormen, Leiserson, Rivest, and Stein, *Introduction to Algorithms*, amortized-analysis chapter.
3. **Program termination by size-change/ranking functions - calibration.** Size-change and lexicographic ranking methods introduce richer well-founded state so that local non-descent is discharged by a hidden ranking certificate. This is a solved termination-analysis mechanism and an exact analogue of "promoted ledger gives native liveness," without a Collatz-style ghost. Citation: Lee, Jones, and Ben-Amram, "The Size-Change Principle for Program Termination," *POPL 2001* / *ACM SIGPLAN Notices* 36(3), 81-92, 2001.
4. **Aliquot dynamics - conjectural folded instance.** Let `s(n)=sigma(n)-n` be the sum of proper divisors. The Catalan-Dickson boundedness/termination picture for aliquot sequences is open; Guy and Selfridge argued that some aliquot sequences may be unbounded. The relevant currency is not scalar valuation but the whole factorization/divisor-supply ledger, so this instance demonstrates that G1 ledgers need not be one-dimensional. Citation: Guy and Selfridge, "What drives an aliquot sequence?," *Mathematics of Computation* 29, 101-107, 1975; Guy, *Unsolved Problems in Number Theory*.
5. **Switched and probabilistic termination/stability certificates - structural.** Average-dwell-time switched systems and ranking-supermartingale proofs both separate average or hidden certificates from pointwise native progress. They are structural G1 analogues unless a specific model supplies an exact `V_k>0` boundary certificate and an `eventual_zero` residual. Citations: Liberzon, *Switching in Systems and Control*, Birkhauser, 2003; Agrawal, Chatterjee, and Novotny, "Lexicographic Ranking Supermartingales: An Efficient Approach to Termination of Probabilistic Programs," arXiv:1709.04037.

### G2 - Transfinite Escrow

**Status:** `theorem`. Justification: the abstract termination implication is a direct well-founded-descent theorem, and the Goodstein calibration fully discharges the stage-indexed escrow audit by the classical ordinal assignment below `epsilon_0`. The proof-theoretic price side is imported by citation, not reproved.

#### 1. Setup

Let `X` be a native state carrier with a stage-indexed run

```text
x_0, x_1, x_2, ...
x_{k+1} = T_k(x_k)
```

where a fixed transition `T` is the special case `T_k=T`. Let `A subset X` be the accepted terminal set. For each stage `k`, declare a presentation

```text
pi_k: X -> P_k
```

and an escrow map

```text
e_k: P_k -> W
```

into a well-founded carrier `(W,<)`.

**[H-G2-stage-coherence: composed stage-coherence audit, boxed.]** For every nonterminal step of the run,

```text
e_{k+1}(pi_{k+1}(T_k(x_k))) < e_k(pi_k(x_k)).
```

The inequality is deliberately on the composed object "presentation change plus native step." It is not enough to say that the escrow decreases before or after rebasing separately: a changing presentation can hide the descent by moving value between encodings. The audit requires the re-presentation and the step to be recorded as one checked transition, so any descent used by the proof appears in the escrow ledger.

The temporal quantifier is unbounded: G2 asks whether every infinite nonterminal run would force an infinite strictly decreasing chain in `W`.

**Closest Foundations IV cousin.** F2, Descent-Repair Normal Form, fixes one quotient `q:X->Q`, one map `F:X->Y`, and one target readout `r:Y->R`; its theorem says `r o F` descends through `q` exactly when a single split-pair obstruction is empty, with source-refinement or target-coarsening repairs when it is not. G2 changes the logical type: the quotient/presentation is stage-indexed (`pi_k`), the readout is an escrow into a well-founded carrier, and the descent condition must hold for every step of an unbounded run after composing the presentation change with the native transition.

#### 2. Theorem

**Part (a): Termination, unconditional.** If `[H-G2-stage-coherence]` holds for every nonterminal step and `(W,<)` is well-founded, then no infinite nonterminal run exists. Therefore every run reaches `A` in finitely many steps. When `W` is equipped with an effective height/rank extractor for the initial escrow value, that extractor gives a finite step-count certificate or bound; otherwise the descended certificate is the finite terminating trace itself.

**Part (b): Imported price/lower bound.** For declared problem families, the existence of a sound uniform escrow may require a named minimum order strength. For Goodstein sequences, the required strength is `epsilon_0`: the standard proof uses ordinal descent below `epsilon_0`, and Kirby-Paris showed that Goodstein's theorem is not provable in Peano Arithmetic. Equivalently for this normal form, no PA-internal escrow whose well-foundedness is provable below the `epsilon_0` strength can certify termination of all Goodstein sequences. This is an imported proof-theoretic lower-bound claim, not a new proof in G2.

#### 3. Proof Spine

For Part (a), assume an infinite nonterminal run. By `[H-G2-stage-coherence]`, the escrow values

```text
e_0(pi_0(x_0)) > e_1(pi_1(x_1)) > e_2(pi_2(x_2)) > ...
```

form an infinite strictly descending chain in `W`, contradicting well-foundedness. Thus a run satisfying the audit must terminate. No local monotonicity of the native values is needed; only the audited escrow values descend.

For the Goodstein calibration, take `X=N`, terminal set `A={0}`, and stage base `k>=2`. The presentation `pi_k(n)` is the hereditary base-`k` representation of `n`: write `n` in base `k`, then recursively write every exponent in base `k`. The Goodstein transition is

```text
G_k(n) = rebase_{k->k+1}(n) - 1,
```

where `rebase_{k->k+1}` means replacing every occurrence of base `k` in the hereditary expression by `k+1`. The escrow map is the ordinal assignment

```text
O_k(n) = hereditary base-k expression for n, with every base k replaced by omega.
```

The key identity is ordinal invariance under rebasing:

```text
O_{k+1}(rebase_{k->k+1}(n)) = O_k(n).
```

This holds because hereditary syntax is preserved by the rebase operation: coefficients and exponents remain in the same finite tree positions, and `O_k`/`O_{k+1}` both replace the current base symbol at every such position by the same ordinal `omega`.

Worked example at base `2`, starting from `n=4`:

```text
4 = 2^2 = 2^(2^1)          hereditary base 2
O_2(4) = omega^(omega^1) = omega^omega

rebase_{2->3}(4) = 3^(3^1) = 27
O_3(27) = omega^(omega^1) = omega^omega
```

Thus rebasing alone preserves the ordinal escrow even though the native integer jumps from `4` to `27`. The Goodstein step subtracts one:

```text
G_2(4) = 27 - 1 = 26
26 = 2*3^2 + 2*3 + 2       hereditary base 3 exponents are finite
O_3(26) = omega^2*2 + omega*2 + 2
```

and ordinal comparison gives

```text
omega^2*2 + omega*2 + 2 < omega^omega = O_2(4).
```

In general, `rebase` preserves `O_k`, and subtracting `1` from a positive natural hereditary expression strictly decreases the associated ordinal:

```text
O_{k+1}(G_k(n))
< O_{k+1}(rebase_{k->k+1}(n))
= O_k(n).
```

The Goodstein escrow values are ordinals below `epsilon_0`, and ordinals below `epsilon_0` are well-founded in the usual set-theoretic proof. Therefore every Goodstein sequence terminates at `0`. Kirby and Paris, "Accessible Independence Results for Peano Arithmetic," *Bulletin of the London Mathematical Society* 14(4), 285-293, 1982, is the cited source for the Goodstein/hydra independence result and the PA-unprovability price.

#### 4. Case Enumeration

For a declared escrow audit, classify by the least order-strength class that actually carries the sound stage-coherent escrow, or by failure at the declared strength.

| Case | Order-strength status | Witness type |
|---|---|---|
| (a) Natively monotone | `W` embeds in `N`; ordinary natural-number descent suffices. | Scalar ranking function with `e_{k+1}<e_k`. |
| (b) Promoted scalar/lexicographic | `W` embeds in a finite lexicographic product such as `N^m`, and no one-dimensional natural rank has been supplied. | Lexicographic or multicomponent ranking certificate. |
| (c) Transfinite escrow | A genuine ordinal notation system is used, for example order type at least `omega^omega`; Goodstein uses ordinals cofinal below `epsilon_0`. | Stage-coherent ordinal assignment such as `O_k`. |
| (d) No escrow at declared strength | The chosen strength `alpha` cannot soundly certify the whole declared family. | Lower-bound or independence witness; Kirby-Paris gives this for PA-strength escrows for all Goodstein sequences. |

The rows are mutually exclusive for a fixed declared audit: either a sound escrow exists and is recorded in its least supplied strength class (a)-(c), or the declared strength fails (d). They are exhaustive for the normal-form audit because every proposed `W` either supplies a well-founded stage-coherent descent certificate at some declared order strength or does not.

#### 5. Interaction Status

G2 is a P4 staging/refinement construction coupled to P1 descent. The escrow is P6 ledger content, but its values live in a well-founded order rather than in a real-valued budget. The descended boundary certificate is finite termination of the native run; the promoted ordinal escrow need not be native data.

#### 6. Nonclaims

1. G2 does not claim that physical or biological systems carry transfinite escrows unless a precise native carrier, presentation family, and well-founded escrow map are supplied.
2. No novelty is claimed for Goodstein's theorem, hydra termination, ordinal analysis, or the Kirby-Paris independence result. The contribution is the layer-agnostic stage-coherent-escrow normal form.
3. The price/lower-bound part is imported proof theory. G2 records the order-strength commitment; it does not reprove the PA-independence theorem.
4. Stage-coherence is load-bearing. A proof that decreases only after an unrecorded re-presentation has not discharged `[H-G2-stage-coherence]`.

#### Layer Instantiations

1. **Goodstein sequences and hydra games - calibration.** Hereditary-base presentation, ordinal assignment `O_k`, and strict descent below `epsilon_0` give the full positive mechanism; Kirby-Paris gives the PA-unprovability price. Citation: Kirby and Paris, "Accessible Independence Results for Peano Arithmetic," *Bulletin of the London Mathematical Society* 14(4), 285-293, 1982.
2. **Program termination by ranking functions - calibration.** Floyd-style termination arguments assign a well-founded rank to program states; ordinal-indexed variants are G2 instances when the rank is transfinite and stage-coherent across control-state presentations. Citation: Floyd, "Assigning Meanings to Programs," *Proceedings of Symposia in Applied Mathematics* 19, 19-32, 1967.
3. **Term-rewrite termination by recursive path orderings - calibration.** Recursive/path orderings supply well-founded term measures that can have transfinite order types; a rewrite step is legal when the left-hand side strictly dominates the right-hand side in the chosen ordering. Citation: Dershowitz, "Orderings for Term-Rewriting Systems," *Theoretical Computer Science* 17(3), 279-301, 1982.
4. **Proof-theoretic ordinal analysis - structural.** Gentzen's analysis of Peano Arithmetic uses transfinite induction up to `epsilon_0`; this is the proof-theoretic background for the Goodstein price. Citation: Gentzen, "Die Widerspruchsfreiheit der reinen Zahlentheorie," *Mathematische Annalen* 112, 493-565, 1936.
5. **AOR cascade termination and multiset descent - calibration/reflexive corpus tie.** The AOR paper's cascade-termination theorem uses the Dershowitz-Manna multiset extension of a well-founded status order to prove finite discharge cascades. This verifies that the corpus already uses well-founded multiset descent internally, while G2 promotes such descent to a first-class escrow currency. Citations: Dershowitz and Manna, "Proving Termination with Multiset Orderings," *Communications of the ACM* 22(8), 465-476, 1979; `six-birds-papers/Tsiokos_2026_Audited_Operational_Realisability_A_Closure_Completion_Reflection_for_Carriers_with_Audit_Data.tex`, `thm:aor:cascade-termination`.

### G3 - Amortized Potential Currency

**Status:** `theorem`. Justification: the abstract claim is the classical potential-method telescoping identity over finite runs, with binary counters and dynamic-array resizing fully discharging the arithmetic calibration.

#### 1. Setup

Let `(S, ->)` be a transition system. A run prefix is a finite chain

```text
s_0 -> s_1 -> ... -> s_n.
```

Each transition `s_{i-1}->s_i` has a declared actual cost

```text
a_i = a(s_{i-1}->s_i) in Q_{>=0}.
```

Declare a potential function

```text
Phi: S -> Q_{>=0}.
```

The amortized cost of step `i` is

```text
a_hat_i = a_i + Phi(s_i) - Phi(s_{i-1}).
```

G3 is a finite-prefix safety law: it bounds total cost on every checked finite run prefix. It is not G1's liveness law. G1 asks whether an unbounded run eventually earns a positive descent certificate and may use ghosts/completions to organize insolvent tails; G3 assumes a supplied potential and proves only the finite-prefix cost bound that follows from its telescoping identity. G3 never uses a ghost locus, completion, or eventual-success assertion.

**Closest Foundations IV cousin.** F27, Conservation as Orbit Descent, says a declared quantity `C:X->V` is conserved for a declared route or symmetry exactly when it descends through the orbit quotient, i.e. it is constant on orbit classes. G3 differs on the conservation axis: `Phi` is not required to be orbit-constant and usually is not. Its lawful content is that potential differences telescope against visible step costs over finite prefixes, yielding a bounded-cost ledger rather than a conserved readout.

#### 2. Theorem

For every finite run prefix `s_0 -> ... -> s_n`,

```text
sum_{i=1..n} a_i
= sum_{i=1..n} a_hat_i + Phi(s_0) - Phi(s_n)
<= sum_{i=1..n} a_hat_i + Phi(s_0),
```

because `Phi(s_n)>=0`. Therefore, if a declared class of runs has `a_hat_i <= B` for every step, then every length-`n` prefix has

```text
sum_{i=1..n} a_i <= n*B + Phi(s_0).
```

**Currency-legality clause.** A potential `Phi` is a G3 currency only when all of the following are part of the declared audit: `Phi` is nonnegative on the state class, the amortized costs are computed by the exact telescoping formula above, and the resulting bound controls a declared run-level feasibility claim such as total-cost or per-operation amortized cost. A non-telescoping score, or a post-hoc statistic that correlates with cost but does not prove a declared bound, is a proxy rather than a currency in the corpus C-role sense.

#### 3. Proof Spine

Expand the amortized costs:

```text
sum_{i=1..n} a_hat_i
= (a_1 + Phi(s_1)-Phi(s_0))
 + (a_2 + Phi(s_2)-Phi(s_1))
 + ...
 + (a_n + Phi(s_n)-Phi(s_{n-1}))
= sum_{i=1..n} a_i + Phi(s_n) - Phi(s_0).
```

Rearranging gives

```text
sum_{i=1..n} a_i
= sum_{i=1..n} a_hat_i + Phi(s_0) - Phi(s_n).
```

Since `Phi(s_n)>=0`, dropping `-Phi(s_n)` gives the upper bound. This is the whole theorem; every calibration instance is an audit that the chosen `Phi` is nonnegative and that `a_hat_i` is uniformly bounded.

**Binary-counter check.** Let `Phi` be the number of `1` bits. If an increment sees `r` trailing ones, it flips those `r` bits to `0` and flips the next `0` to `1`, so actual cost is `a_i=r+1`. The potential change is `1-r`, hence

```text
a_hat_i = (r+1) + (1-r) = 2.
```

Example:

```text
0111 -> 1000
r=3
actual flips = 4
Phi before = 3
Phi after = 1
a_hat = 4 + 1 - 3 = 2.
```

For a non-carry example:

```text
0100 -> 0101
r=0
actual flips = 1
Phi before = 1
Phi after = 2
a_hat = 1 + 2 - 1 = 2.
```

**Dynamic-array doubling check.** Use the nonnegative insertion-only potential

```text
Phi = max(0, 2*size - capacity).
```

On states after the usual doubling policy has restored `size >= capacity/2` for nonempty arrays, this is the standard `2*size-capacity` potential. A non-resizing insertion in that range costs `1`, increases `size` by `1`, and changes `Phi` by at most `2`, so `a_hat<=3`. The empty initial edge case has `Phi=0` and is checked directly.

At a full array with `size=capacity=m`, a resizing insertion copies `m` items and inserts one new item, so `a_i=m+1`. Before the operation,

```text
Phi_before = 2m - m = m.
```

After doubling to capacity `2m` and size `m+1`,

```text
Phi_after = 2(m+1) - 2m = 2.
```

Thus

```text
a_hat = (m+1) + 2 - m = 3.
```

Concrete resize:

```text
size=4, capacity=4, Phi=4
insert with resize: cost=5
size=5, capacity=8, Phi=2
a_hat = 5 + 2 - 4 = 3.
```

#### 4. Case Enumeration

For a declared run family together with one chosen, audited potential `Phi`, exactly one of the following applies. If multiple legal potentials exist, this table classifies the audit record `(run family, Phi)`, not the run family in isolation.

| Case | Status | Witness type |
|---|---|---|
| (a) Prepaid | The audited `Phi` is legal and `Phi(s_i)<=Phi(s_{i-1})` for every checked step; the potential only pays down. | Nonincreasing-potential audit plus telescoping bound. |
| (b) Borrow-and-repay | The audited `Phi` is legal, some step has `Phi(s_i)>Phi(s_{i-1})`, and `a_hat_i` remains uniformly bounded over the run family. | Credit ledger with bounded amortized costs; binary counters and dynamic arrays are examples. |
| (c) Insolvent in the declared class | No legal `Phi` in the declared candidate class controls the stated run-level claim, so no audit record can be chosen. | Lower-bound witness, e.g. a family of length-`n` runs with superlinear total cost under every candidate whose initial potential and amortized bound would imply only linear cost. |

The partition is by one object type: a declared audit record `(run family, Phi)`, with (c) reserved for failure to produce any legal record from the declared class. For any chosen legal `Phi`, either it is nonincreasing on all steps (a) or it increases on at least one step (b). If no legal `Phi` exists, the case is (c).

#### 5. Interaction Status

G3 is P6 ledger content gated by P2 currency legality. The potential is the ledger balance, actual costs are visible debits, and amortized costs are audited charges. The P2 gate rejects proxies: the potential must telescope and must control a declared finite-run feasibility claim.

#### 6. Nonclaims

1. G3 does not assert that a useful potential exists for an arbitrary system. Finding such a potential, especially for an arithmetic or dynamical liveness problem, is G1's territory.
2. G3 is safety-grade, not liveness-grade. It bounds finite-run cost prefixes; it does not prove eventual termination, eventual descent, or eventual success.
3. G3 never uses ghosts, completions, or bad-tail membranes.
4. No novelty is claimed for the classical amortized-analysis technique. The contribution is the layer-agnostic currency normal form and the proxy-exclusion discipline.

#### Layer Instantiations

1. **Binary-counter increment - calibration.** `Phi=#1 bits` gives exact amortized cost `2` per increment, as verified above. Citations: Tarjan, "Amortized Computational Complexity," *SIAM Journal on Algebraic and Discrete Methods* 6(2), 306-318, 1985; Cormen, Leiserson, Rivest, and Stein, *Introduction to Algorithms*, amortized-analysis chapter.
2. **Dynamic-array doubling - calibration.** With `Phi=max(0,2*size-capacity)`, equivalently `2*size-capacity` on the standard nonempty post-resize load range, insertions have amortized cost at most `3` under unit insert/copy costs. Citation: Cormen, Leiserson, Rivest, and Stein, *Introduction to Algorithms*, dynamic tables/amortized-analysis treatment.
3. **Splay trees - calibration.** Sleator and Tarjan's access lemma uses a rank potential of the form `Phi=sum_x log(size(subtree_x))`, up to logarithm-base convention; the exact constant changes with the base, not the telescoping role. Citation: Sleator and Tarjan, "Self-Adjusting Binary Search Trees," *Journal of the ACM* 32(3), 652-686, 1985.
4. **Passivity/storage functions in control - structural.** Dissipativity/passivity uses a nonnegative storage function whose change is bounded by supplied work; Foundations I already contains the bridge-slot `D-TK-BRG-02` for passivity with storage. G3 generalizes that bridge-slot pattern into a full finite-run potential-currency law. Citations: Willems, "Dissipative Dynamical Systems, Part I: General Theory," *Archive for Rational Mechanics and Analysis* 45, 321-351, 1972; `six-birds-papers/Tsiokos_2026_Six_Birds_Foundations_of_Emergence_Calculus.tex`, `D-TK-BRG-02`.
5. **Energy-harvesting battery budgets - structural.** In energy-harvesting communication and embedded-sensor models, battery state is an explicit storage potential: consumption over any finite prefix is constrained by initial charge plus harvested energy, subject to battery-capacity and energy-causality constraints. This is a G3-style finite-prefix ledger when the battery update is declared exactly; it remains structural here because this entry does not instantiate one fixed hardware model and cost convention. Citations: Ozel, Tutuncuoglu, Yang, Ulukus, and Yener, "Transmission with Energy Harvesting Nodes in Fading Wireless Channels: Optimal Policies," arXiv:1106.1595; Yang and Ulukus, "Optimal Packet Scheduling in an Energy Harvesting Communication System," arXiv:1010.1295.

### Cluster B - Moving and self-generated obstructions

Verified gap: every obstruction in the corpus is declared up front and static. Cluster B covers obstructions that move with the run, are manufactured by the run, or respond adversarially to it.

### G4 - Moving-Cover Exhaustion

**Status:** `schema`. Justification: the Fibonacci-Sylvester instance is a complete theorem-grade calibration, but the layer-agnostic local-to-global claim is conditional on a declared exhaustion certificate and a declared patch class. The general form is therefore a schema, not a free theorem that local coverage implies global closure.

#### 1. Setup

Let `T` be an infinite index set and let `{P(t) : t in T}` be a target family. A certificate patch is data

```text
c_alpha validates P(t) for every t in R_alpha subset T.
```

The regions `R_alpha` are part of the audit; local admissibility of a patch does not by itself globalize the target family.

A cover is **moving** relative to a declared patch class when no finite subfamily of patches covers all of `T`, and the patch parameters required for targets in `T` are unbounded. In the Egyptian-fraction calibration, the patch parameters are the unit-fraction denominators generated by the greedy expansion; as the target rational varies, those denominators are unbounded.

There are two equivalent audit shapes, depending on the instance.

```text
Global cover audit:
U_n = T \ union_{alpha<=n} R_alpha,
with U_n descending to empty under a declared exhaustion order.

Pointwise target audit:
for each t, residuals rho_0(t), rho_1(t), ...
with a budget b_j(t) in a well-founded order W_t,
b_{j+1}(t) < b_j(t), until rho_N(t) is empty.
```

The Fibonacci-Sylvester calibration uses the pointwise form on proper rationals `p/q` in `(0,1)`: each target gets its own finite certificate sequence, and the budget is the numerator of the remaining rational.

**Closest Foundations IV cousin.** F4, Local-Global Obstruction Normal Form, starts with a declared finite patch system: a finite index set `I`, local object sets `(Q_i)_{i in I}`, overlap compatibility, and a restriction map from global objects. It classifies compatible local families by whether they globalize. G4 changes the axis from finite gluing to unbounded exhaustion: the patch family may grow with the target, the certificate is stage-indexed, and closure is legal only when an explicit exhaustion ledger is supplied. This is exactly the NC-14 discipline: local admissibility does not imply global admissibility without the extra exhaustion data.

#### 2. Theorem

**[H-G4-sound: patch soundness.]** For every patch index `alpha` and every `t in R_alpha`, the certificate `c_alpha` proves `P(t)` in the declared local certificate system.

**[H-G4-exhaust: exhaustion audit.]** One of the declared audit forms proves total coverage:

```text
Global form: for every t in T, some n has t notin U_n.
Pointwise form: for every t in T, the residual rho_N(t) is empty for some finite N.
```

**[H-G4-language-complete: certificate-language completeness.]** If `P(t)` holds for all `t in T`, then the declared certificate language contains a global or pointwise exhaustion certificate witnessing that closure. This is a separate meta-hypothesis about the chosen language; it is not inferred from local compatibility.

**[H-G4-fixed-leak: fixed-package leak.]** For a declared restricted class `C` of admissible patch regions, such as finite unions of residue classes modulo a fixed modulus or finite sets of allowed unit denominators, every finite subfamily from `C` misses at least one target `t in T`. When the escaping target can be exhibited, this is a constructive no-go witness.

**Positive schema.** If `[H-G4-sound]` and `[H-G4-exhaust]` hold, then `P(t)` holds for every `t in T`: choose the finite patch or terminal residual certificate supplied by `[H-G4-exhaust]`, then apply `[H-G4-sound]`.

**Conditional biconditional.** Relative to `[H-G4-sound]` and `[H-G4-language-complete]`, closure of `{P(t)}` is equivalent to the existence of an exhaustion certificate in the declared language. The forward direction uses `[H-G4-language-complete]`; the reverse direction is the positive schema. Completeness of the certificate language is an extra hypothesis, not a consequence of local patch admissibility.

**Fixed-package no-go schema.** If `[H-G4-fixed-leak]` holds for a restricted finite-package class `C`, then no finite package from `C` closes the claim. This no-go is about that restricted finite class only; it does not block a richer unbounded moving-cover family from satisfying `[H-G4-exhaust]`.

For Egyptian fractions this no-go is elementary: a fixed finite set `D` of allowed denominators gives only finitely many subset sums `sum_{d in E} 1/d`, while there are infinitely many rational targets in `(0,1)`. Therefore no fixed finite denominator package covers all proper rational targets in `(0,1)`. The greedy moving cover succeeds by allowing denominators to depend on the target.

#### 3. Proof Spine

For the Fibonacci-Sylvester greedy algorithm, take a proper positive rational `p/q` in lowest terms, `0<p<q`. The greedy step chooses

```text
m = ceil(q/p),
1/m <= p/q,
rho' = p/q - 1/m = (pm-q)/(qm).
```

From the definition of the ceiling,

```text
m-1 < q/p <= m.
```

Multiplying by `p>0` gives

```text
p(m-1) < q <= pm.
```

The right inequality gives `pm-q >= 0`, so the greedy subtraction does not overshoot. The left inequality gives

```text
pm - q < p.
```

If `pm=q`, the remainder is zero and the expansion terminates. If `pm>q`, the unreduced remainder has numerator `pm-q`, and its reduced numerator is at most `pm-q`, hence strictly smaller than `p`. Thus the numerator budget strictly decreases through positive integers at every nonterminal greedy step. No infinite descent is possible, so the algorithm terminates after finitely many steps.

This calibration claim is deliberately scoped to proper fractions in `(0,1)`, where the standard greedy construction produces a finite distinct-denominator Egyptian-fraction expansion. I do not use the improper-rational shortcut "repeat `1/1`": repetition would violate the distinct-denominator convention used in the fixed-package no-go. The moving-cover content is already visible on `(0,1)`: a fixed finite denominator set has only finitely many distinct subset sums, while the target family contains infinitely many proper rational values, so no single finite denominator package can cover the family.

For the Erdos-Straus conjecture,

```text
4/n = 1/x + 1/y + 1/z,  n>=2,
```

the same normal form is only conjectural. It is enough to check prime `n`: if `4/p` has a three-unit expansion, then `4/(mp)` has one by multiplying all denominators by `m`; therefore a composite counterexample would have a prime-factor counterexample. Mordell-style modular identities are reported to cover all `n` except the residue classes

```text
1, 121, 169, 289, 361, 529 mod 840.
```

This mod-840 uncovered-class list is now well triangulated (independently cross-checked 2026-07-08 against Wikipedia's Erdos-Straus article and Elsholtz-Tao's own related-work framing, both agreeing on the same six classes); the specific polynomial identities themselves are still secondary-sourced only, not independently retrieved from Mordell's original pp. 287-290 text (*Diophantine Equations*, Academic Press, 1969, Ch. 30), so a primary-source flag remains for the identities' exact form when this appears in the paper. The quadratic-residue obstruction to polynomial congruence identities is attributed to Mordell alone (not Schinzel — a 2026-07-08 verification pass found no source crediting this specific no-go argument to Schinzel; Schinzel's genuine, distinct ties to Erdos-Straus are the generalized `a/n` conjecture via Sierpinski, studied by Vaughan, and an unrelated 1956 odd-denominator paper): an identity for `n == r mod p` can exist only when `r` is a non-quadratic-residue modulo `p`, since `1` is a quadratic residue mod every `p>1` and is therefore never coverable by any finite identity family. This supports a fixed-package no-go for that identity class; it does not prove or disprove Erdos-Straus.

Density and average-solution results, including work of Webb and Elsholtz-Tao, remain `probabilistic` relative to the pointwise conjecture.

#### 4. Case Enumeration

The table classifies one declared G4 audit record: a target family, a patch class, and the evidence submitted for that class. Apply the first matching row.

| Case | Status | Witness type |
|---|---|---|
| (a) Finitely-coverable | A finite patch subfamily covers all of `T`. | Finite list of patches plus proof that their regions cover `T`. |
| (b) Moving-cover-exhaustible | No finite package is supplied, but a global or pointwise exhaustion budget proves every target is eventually covered. | Well-founded residual descent; Fibonacci-Sylvester numerator descent is the calibration. |
| (c) Fixed-package no-go | A no-go witness shows every finite package from a declared restricted finite class misses some target; this is distinct from a successful moving cover using an unbounded, target-dependent family. | `[H-G4-fixed-leak]`; finite denominator sets for proper rationals in `(0,1)` give a concrete example. |
| (d) Probabilistically-covered-only | Evidence covers density one, almost all targets, or bounded computational ranges, but no pointwise exhaustion certificate is supplied. | Density/exceptional-set estimate or finite search record, status `probabilistic`. |
| (e) Uncertified | None of the above evidence has been supplied. | Open obligation, not a G4 closure claim. |

Rows are mutually exclusive by priority for the declared audit record. In particular, a no-go for one restricted finite patch class can coexist with a moving-cover proof in a richer class; those are different audit records, not a contradiction.

#### 5. Interaction Status

G4 is P2 feasibility/gating over an unbounded target family plus P6 exhaustion ledger content. The patch validates local feasibility on its region; the exhaustion budget is the audit object that licenses global closure. Without that budget, NC-14 blocks the inference from local admissibility to global admissibility.

#### 6. Nonclaims

1. G4 does not prove the Erdos-Straus conjecture.
2. Mordell-style residue coverage and quadratic-residue obstruction results are sub-results about specific identity families. They are not progress from local admissibility to global closure unless an exhaustion certificate is supplied.
3. Density-one, average, or bounded-search evidence stays `probabilistic`; it is not upgraded to pointwise closure.
4. No novelty is claimed for the Fibonacci-Sylvester algorithm, covering systems, or cited Erdos-Straus partial results. G4's contribution is the moving-cover/exhaustion normal form and NC-14-compliant audit discipline.

#### Layer Instantiations

1. **Fibonacci-Sylvester Egyptian fractions - calibration.** On proper fractions in `(0,1)`, the greedy algorithm gives a finite target-dependent distinct-denominator certificate, with strict numerator descent as the exhaustion budget. Citation: Fibonacci, *Liber Abaci*; Eppstein, "Ten Algorithms for Egyptian Fractions," *Mathematica in Education and Research* 4(2), 1995.
2. **Erdos-Straus - conjectural flagship.** The conjecture remains open. Prime reduction is verified; the mod-840 residue list and quadratic-residue obstruction are included as secondary-source-verified, primary-source-flagged sub-results. Citations: Mordell, *Diophantine Equations*, Academic Press, 1969; Elsholtz and Tao, "Counting the number of solutions to the Erdos-Straus equation on unit fractions," *Journal of the Australian Mathematical Society* 94(1), 50-105, 2013.
3. **Erdos covering systems - calibration.** Finite congruence covering systems are the pure combinatorial fixed-cover analogue; Hough solved Erdos's minimum-modulus problem by proving an absolute bound on the least modulus in distinct covering systems. Citation: Hough, "Solution of the minimum modulus problem for covering systems," *Annals of Mathematics* 181(1), 361-382, 2015.
4. **Symbolic integration by pattern families - structural.** Risch-style symbolic integration and rule-based integration systems use growing, expression-dependent case families rather than a single finite pattern table for all inputs. This is structural here unless a specific integrator trace supplies the patch regions and exhaustion budget. Citations: Risch, "The Problem of Integration in Finite Terms," *Transactions of the American Mathematical Society* 139, 167-189, 1969; Bronstein, *Symbolic Integration I*, Springer, 2005.
5. **CEGAR/proof automation - structural.** Counterexample-guided abstraction refinement and related proof automation grow their case split or abstraction precision with the input; a successful proof is a target-dependent exhaustion of spurious counterexamples. This is structural unless a concrete verifier supplies the well-founded refinement budget. Citation: Clarke, Grumberg, Jha, Lu, and Veith, "Counterexample-guided abstraction refinement for symbolic model checking," *Journal of the ACM* 50(5), 752-794, 2003.

### G5 - Carry-Horizon Confinement

**Status:** `calibration-anchored schema`. Justification: the no-go and confinement claims are conditional on named horizon and pattern hypotheses, but the confinement mechanism is fully discharged by the solved base-2 reverse-and-add instance `10110_2 = 22`.

#### 1. Setup

Fix a base `b>=2`. For a positive integer `n` with canonical base-`b` digit string `digits_b(n)`, define

```text
rev_b(n) = the integer represented by reverse(digits_b(n)),
R_b(n) = n + rev_b(n).
```

The target predicate is usually `Pal_b(n)`, meaning `digits_b(n)` is a palindrome. The depth-`m` current quotient is

```text
q_m(n) = n mod b^m,
```

equivalently the last `m` base-`b` digits. For a future probe `F_j` such as `q_m(R_b^j(n))` or the palindrome verdict within the first `j` steps, define the carry horizon `h_j(x)` to be the least depth `M` such that all `y` with `q_M(y)=q_M(x)` give the same declared probe value as `x`; set `h_j(x)=infinity` when no finite suffix depth suffices. The law quantifies over an unbounded run: the question is whether a fixed current quotient depth can remain predictive as `j -> infinity`.

A pattern certificate is a regular or automatic language `Pcal` over base-`b` digit strings, interpreted as a set of integers. Its audit data must state the phase convention, the transition closure, and the target exclusion.

**[H-G5-unbounded-horizon: moving carry horizon.]** For every fixed suffix depth `m`, there are a step `j` and states `y,z` in the declared carrier with `q_m(y)=q_m(z)` but different future probe values. Equivalently, some step-indexed split-pair obstruction

```text
Delta(q_m, R_b^j, r_j) != empty
```

is nonempty, where `r_j` is the declared target readout for that step.

**[H-G5-closed-pattern: target-free closed language.]** A declared regular or automatic language `Pcal` satisfies `R_b(Pcal) subset Pcal`, and no member of `Pcal` satisfies the target predicate. If the certificate is phase-indexed, this means `R_b(P_i) subset P_{i+1}` cyclically, with the union `Pcal = union_i P_i` target-free.

**Closest Foundations IV cousins.** F13a, Hiddenness Normal Form, fixes one hiddenness interface: one current quotient, one predictive quotient, and one single-instant exposure/collapse test. F3, Holonomy-Memory Repair Normal Form, compares exactly two declared routes once and repairs the residue by recording memory. G5 is the step-indexed strengthening of both: it asks for a sequence of quotient/prediction failures as the carry horizon grows along an unbounded orbit, and it accepts a regular-language confinement certificate only when that certificate is propagated through the whole run.

#### 2. Theorem

**No-go schema.** Under `[H-G5-unbounded-horizon]`, no fixed-depth quotient `q_m` is future-sufficient for the declared unbounded run. For every `m`, the named hypothesis supplies a step `j` and a nonempty split-pair obstruction `Delta(q_m, R_b^j, r_j)`, so the future probe cannot factor through `q_m`.

**Confinement schema.** Under `[H-G5-closed-pattern]`, if some iterate `R_b^N(x)` lies in `Pcal`, then no later iterate satisfies the target predicate. Closure gives `R_b^{N+t}(x) in Pcal` for every `t>=0`, and target-freeness gives `not Pal_b(R_b^{N+t}(x))` for every `t>=0`.

These are conditional schemas. The no-go half does not by itself prove escape from the target, and the confinement half applies only after a concrete target-free closed language has been verified.

#### 3. Proof Spine

For the no-go half, the proof is the split-pair definition applied at each depth. In reverse-and-add, the low `m` digits after one step depend on the low digits of `n` and on the high digits brought down by `rev_b(n)`; over an unbounded orbit, longer digit strings can expose carries from positions outside any fixed suffix window. `[H-G5-unbounded-horizon]` packages that moving-carry fact as an auditable split-pair family rather than treating it as a heuristic.

For the base-2 confinement calibration, let `R=R_2`. The verified seed is

```text
22 = 10110_2.
```

Directly,

```text
10110 -> 100011 -> 1010100 -> 1101001 -> 10110100.
```

For `r>=2`, define four phase languages:

```text
P0(r) = 10 1^r 01 0^r
P1(r) = 11 0^(r-2) 1 000 1^(r-2) 01
P2(r) = 10 1^r 01 0^(r+1)
P3(r) = 11 0^r 10 1^(r-1) 01
```

Binary addition with carries verifies the phase cycle

```text
R(P0(r)) = P1(r)
R(P1(r)) = P2(r)
R(P2(r)) = P3(r)
R(P3(r)) = P0(r+1).
```

The first cycle is concrete:

```text
P0(2) = 10110100
R(P0(2)) = 10110100 + 00101101 = 11100001 = P1(2),
R(P1(2)) = 101101000 = P2(2),
R(P2(2)) = 110010101 = P3(2),
R(P3(2)) = 1011101000 = P0(3).
```

No string in these phase languages is a palindrome: `P0` and `P2` start with `1` and end with `0`; `P1` and `P3` start with `11` and end with `01`, so their second digit and penultimate digit differ. The four finite pre-entry strings displayed above are also non-palindromic. Therefore the orbit of `22` is certified never to reach a binary palindrome. This confirms the design-doc seed `10110_2 = 22`, but the closed invariant used here is the full four-phase regular family, not merely the every-fourth-iterate pattern. Sources checked: OEIS A060382 records `a(2)=22` as the proved base-2 palindrome-free seed and links Kevin Brown's MathPages note (`mathpages.com/home/kmath004`, "Digit Reversal Sums Leading to Palindromes" — this Kevin Brown is not the Cornell topologist Kenneth S. Brown, a distinct person some secondary discussions conflate him with; no peer-reviewed publication of this result was located, so the attribution remains informally sourced); the Lychrel-number survey page records the same `4n` subsequence pattern. An independent 2026-07-08 verification pass also confirms the closed-form pattern directly: `22` in base 2 is `10110`, and after `4n` steps the orbit equals `10` + `(n+1)` ones + `01` + `(n+1)` zeros, i.e. the regex `10 1^k 01 0^k` for `k>=2` — closure under `R^4` (four applications per pattern-step), not literal single-step `R`-closure, matching the four-phase family `P0..P3` used above.

For base 10, `196` has no analogous target-free closed-language certificate. Large finite searches remain bounded evidence only.

#### 4. Case Enumeration

The table classifies one declared G5 audit record: a base, a target predicate, an orbit, and the submitted horizon/pattern evidence. Apply the first matching row.

| Case | Status | Witness type |
|---|---|---|
| (a) Confined-to-target-basin | The orbit reaches the target, or enters a certified basin whose closure forces eventual target hit. | Explicit hitting time or basin certificate. |
| (b) Certified escape | The orbit enters a target-free closed pattern family, discharging `[H-G5-closed-pattern]`. | Regular/automatic invariant; the base-2 `22` four-phase certificate is the calibration. |
| (c) Horizon-budgeted-undetermined | Only finite-depth or finite-iteration evidence is supplied, or `[H-G5-unbounded-horizon]` is measured without a target-free closed pattern. | Bounded carry-horizon audit, iteration log, or split-pair samples; base-10 `196` belongs here. |

Rows are mutually exclusive by priority for the declared audit record. They are exhaustive for the evidence statuses G5 accepts: target-certified, escape-certified, or not yet pointwise certified.

#### 5. Interaction Status

G5 combines P1 descent obstruction with P5 packaging. The split-pair family records that fixed current quotients fail as predictive carriers when the carry horizon moves; the regular language packages an infinite target-free residue into a finite certificate. This is not a P6-drive or arrow claim: carry-horizon growth is hidden predictive content, not entropy production.

#### 6. Nonclaims

1. G5 does not prove or disprove any base-10 Lychrel candidate. In particular, `196` remains open.
2. Large base-10 computations, however deep, stay bounded-verification or `probabilistic` evidence unless they produce a genuine closed target-free certificate.
3. `[H-G5-unbounded-horizon]` alone is only a no-go for fixed-depth prediction; it is not an escape certificate.
4. No novelty is claimed for the classical base-2 reverse-and-add result. G5's contribution is the layer-agnostic carry-horizon normal form and the separation between moving-quotient no-go evidence and closed-pattern confinement evidence.

#### Layer Instantiations

1. **Base-2 reverse-and-add - calibration.** The seed `10110_2 = 22` is certified never to reach a palindrome by the four-phase regular invariant above. Citations: OEIS A060382; Kevin Brown, "Digit Reversal Sums Leading to Palindromes," MathPages (informally sourced; no peer-reviewed publication located).
2. **Base-10 Lychrel candidates - conjectural.** The `196` reverse-and-add orbit has extensive finite computation but no proof of non-palindromicity; it remains open. Citations: John Walker, "Three Years of Computing," Fourmilab; Lychrel-number survey references to Wade VanLandingham and later computation records.
3. **Carry-propagation side channels in arithmetic circuits - structural.** Variable carry propagation can expose digit-position information through timing or power behavior; this is a G5-style moving-horizon risk only when the hardware model declares the readout and leakage predicate. Citation: Kocher, "Timing Attacks on Implementations of Diffie-Hellman, RSA, DSS, and Other Systems," CRYPTO 1996.
4. **Finite-precision error fronts in numerical computing - structural.** Rounding and cancellation can move the depth at which hidden low-order information affects later results; this is structural here unless a particular algorithm supplies the quotient chain and horizon audit. Citation: Higham, *Accuracy and Stability of Numerical Algorithms*, 2nd ed., SIAM, 2002.
5. **Automatic sequences and regular invariants - calibration/structural.** Regular languages and finite automata supply the certificate class used by the base-2 proof; other digit systems become G5 instances only when the transition closure and target exclusion are checked. Citation: Allouche and Shallit, *Automatic Sequences: Theory, Applications, Generalizations*, Cambridge University Press, 2003.

### G6 - Endogenous Needle Generation

**Status:** `schema`. Justification: G6 has named hypotheses and an open flagship instance. `design/04_LABS.md` G6-L2 now supplies solved calibration instances for both abstract schemas, but only through deliberately designed tunable variants (jump-`2n` parity trapping for `hole_forming_schema`; constant-jump-`1` full coverage for `covering_schema`), not through the ordinary Recaman recurrence itself, and not through a single instance discharging both schemas at once. Whether that custom-toy calibration should upgrade this law to `calibration-anchored schema` — matching how G7 and G9 anchor on genuinely recognized classical instances (the angel problem, Rule 184) rather than purpose-built toys — remains a deliberate, separately-considered decision, not made here.

#### 1. Setup

Let `X` be a countable carrier and let a run be

```text
x_0, x_1, x_2, ...
x_{n+1} = T(x_n, S_n),
S_n = G(x_0, ..., x_n) subset X.
```

Here `S_n` is the endogenous obstruction set: it is not fixed before the run, but computed from the orbit's own past by the declared history functional `G`. In the Recaman instance, `S_n={a_0,...,a_n}` is the visited set.

For a finite audit window `W subset X`, write `V_n={x_0,...,x_n}` and `H_n(W)=W \ V_n` for the unvisited holes inside `W`. Fix a counting measure or other declared finite measure `mu` on audit windows. The Phase-1 proposed rate quantities are:

```text
gamma_n(W) = mu((S_{n+1} \ S_n) cap W)
rho_n(W)   = declared measure of legal first-visit pressure from (x_n,S_n)
             toward H_n(W).
```

The exact definition of `rho_n` is instance data: in a deterministic system it may be a `0/1` legal-return indicator; in a stochastic or branching system it may be a probability, capacity, or number of legal channels. What is not optional is the audit: `rho_n` must be computed before using the future visit as evidence.

**[H-G6-dominant-pressure: proposed Phase-1 pressure domination.]** There is a finite exception set `E subset X`, a cofinal exhaustion by finite windows

```text
W_1 subset W_2 subset ... subset X \ E,
union_M W_M = X \ E,
```

and, for each `M`, a finite block decomposition of times after some `N_M` such that whenever `H_n(W_M)` is nonempty at the start of a block `I`, the audited inequality

```text
sum_{i in I} rho_i(W_M) >= 1 + sum_{i in I} gamma_i(W_M)
```

holds, and the audit charges the positive excess to at least one distinct first visit in `H_n(W_M)` during that block. This is a deliberately strong proposed formalization: pressure must not merely be large in prose; it must buy a new visit in the window faster than the history-generated obstruction can seal the remaining holes.

**[H-G6-dominant-obstruction: proposed Phase-1 obstruction domination.]** There are a target `y in X`, a time `N`, and a declared sequence of separating cuts `C_n(y)` such that `y notin V_N` and, for every `n>=N`, every legal path from `(x_n,S_n)` to `y` crosses `S_n` or a certified blocked cut. Quantitatively, on every later audit block `I`,

```text
sum_{i in I} gamma_i(C_i(y)) > sum_{i in I} rho_i(C_i(y)).
```

The strict excess must be tied to the displayed cut, not inferred from density alone.

**Closest Foundations IV cousin.** F6, No-Needles Stability, starts with a formed stability package that declares the currency block, layer-bridge block, dissolving-direction block, currency and residual budgets, and transport selector up front. It proves that no unpriced layer-dissolving needle survives that declared package. G6 changes the provenance axis: the needle is manufactured by the run's own history `S_n=G(x_0,...,x_n)`, and the theorist audits the race between return pressure and the growing obstruction after the fact. F6 is declared-upfront needle killing; G6 is orbit-manufactured needle generation.

#### 2. Theorem

**Covering schema.** If `[H-G6-dominant-pressure]` holds, then every point in `X \ E` is eventually visited. Equivalently, the orbit is cofinite-covering relative to the declared exception set `E`.

**Hole-forming schema.** If `[H-G6-dominant-obstruction]` holds, then the displayed target `y` is a permanent hole: `y notin V_n` for all `n>=N`.

Both directions are schemas. G6 does not assert that any concrete system satisfies either hypothesis until the relevant rate ledger and witness cuts have been supplied.

#### 3. Proof Spine

For the covering direction, fix an audit window `W_M`. It is finite. Each block satisfying `[H-G6-dominant-pressure]` and starting with a nonempty hole set must produce at least one new first visit in that hole set. Therefore `|H_n(W_M)|` decreases after each such charged block and cannot decrease forever. Hence `W_M` is covered after finitely many charged blocks. Since the exhaustion is cofinal outside the finite exception set `E`, every point of `X \ E` is eventually visited.

For the hole-forming direction, `[H-G6-dominant-obstruction]` supplies a target `y` and a persistent separating cut. Every legal route to `y` after time `N` crosses an obstruction whose growth dominates the available return pressure on every audit block. Thus no certified legal visit to `y` can occur after `N`; because `y notin V_N`, it remains a permanent hole.

For Recaman's sequence, the recurrence is:

```text
a_0 = 0,
a_n = a_{n-1} - n    if a_{n-1}-n is positive and unused,
a_n = a_{n-1} + n    otherwise.
```

OEIS A005132 states the equivalent nonnegative condition; since `0` is already used at the start, the positive/unused and nonnegative/unused versions agree on the actual run. Whether every positive integer eventually appears remains open. OEIS A005132 records that `852655` is the smallest missing number after computations as large as `10^612` terms, citing Benjamin Chaffin's computations. That is a bounded computational fact, not a permanent-hole proof. The hit-time sequence is OEIS A057167; the Recaman sequence itself is OEIS A005132.

No provable toy variant is included in this Phase-1 entry. The law remains schema-grade until G6-L2 supplies at least one fully proved covering variant and one fully proved permanent-hole variant.

#### 4. Case Enumeration

G6 has two classification axes. The first is system-level: what has been proved about the run relative to a declared target domain and exception set.

| System case | Status | Witness type |
|---|---|---|
| (S-a) Cofinite-covering relative to `E` | `[H-G6-dominant-pressure]` is discharged on a cofinal exhaustion of `X \ E`. | Finite exception set `E` plus pressure ledger with charged first visits in every finite audit window outside `E`. |
| (S-b) Uncontrolled obstruction growth | The rate audit shows obstruction growth escaping the proposed pressure ledger on cofinal windows, but no valid cofinite-covering certificate is supplied. | Divergent or unbounded `gamma/rho` audit, possibly without a per-target permanent-hole cut. |
| (S-c) System-uncertified | Neither a cofinite pressure certificate nor an uncontrolled-growth certificate has been supplied. | Census, finite search, or rate plots without a system-level proof; Recaman is currently here. |

The second axis is per-target: what has been proved about one declared point `y`.

| Target case | Status | Witness type |
|---|---|---|
| (T-a) Covered target | `y` is visited at a displayed time, or a system-level cofinite-covering certificate has `y notin E`. | Hitting time, or `[H-G6-dominant-pressure]` with `y in X \ E`. |
| (T-b) Certified permanent hole | `[H-G6-dominant-obstruction]` is discharged for this `y`. | Persistent separating cut with strict obstruction-over-pressure inequality. |
| (T-c) Target-uncertified | No hitting time, no applicable cofinite certificate, and no permanent-hole cut has been supplied. | Finite search or unresolved target obligation. |

These tables are mutually exclusive on their own axes. A system-level cofinite-covering claim relative to `E` is compatible with a per-target permanent-hole certificate exactly when the target lies in `E` or is added to `E`. The genuine contradiction is narrower: the same audit cannot both claim `y notin E` is covered by `[H-G6-dominant-pressure]` and certify `y` as a permanent hole by `[H-G6-dominant-obstruction]`. If that happens, the audit record is inconsistent rather than a new G6 case.

#### 5. Interaction Status

G6 is P5 packaging of the history-generated obstruction set plus P2 feasibility gating through the legal-move predicate, with a P6 rate ledger for `gamma_n` and `rho_n`. The analysis is theorist-side and external: the orbit may generate `S_n`, but it does not certify its own coverage, completeness, or hole formation. This is the NC-16/NC-17 boundary; no same-level self-certification is being credited.

#### 6. Nonclaims

1. G6 does not resolve whether Recaman's sequence covers every positive integer.
2. `[H-G6-dominant-pressure]` and `[H-G6-dominant-obstruction]` are Phase-1 proposed formalizations, not settled final definitions. Later labs may refine the exact `rho_n` and `gamma_n` inequality form.
3. The term "endogenous needle" means a history-generated obstruction described by an external theorist. It is distinct from Foundations V's "Endogenous Closure," which concerns a system-side closure apparatus in the sibling cognition project.
4. NC-16/NC-17 are load-bearing: this law never lets the system certify itself from the same layer. All G6 certificates are external audits of the generated obstruction landscape.
5. No novelty is claimed for Recaman's sequence or for the cited computational fact that `852655` remains the smallest missing value after large finite computations.

#### Layer Instantiations

1. **Recaman's sequence - conjectural flagship.** The visited set is the orbit-generated obstruction set; the universal-coverage question is open, and `852655` is only a long-missing value in finite computations. Citations: OEIS A005132; OEIS A057167; Chaffin computation notes linked from OEIS A005132.
2. **Self-avoiding walks and excluded volume - structural.** The walk's own past forbids future lattice sites, producing an endogenous obstruction landscape. This is structural here because G6's coverage/hole dichotomy requires a specific rate ledger beyond the standard model. Citations: Madras and Slade, *The Self-Avoiding Walk*, Birkhauser, 1993; Flory, *Principles of Polymer Chemistry*, Cornell University Press, 1953.
3. **Novelty search and curiosity-driven RL - structural.** Visited-state penalties and pseudo-count bonuses make the agent's history alter the future exploration landscape. The seam with Foundations V E9 Curiosity is explicit: V prices the agent's own probe-acquisition economy, while G6 analyzes the orbit's history-generated obstruction set from the theorist's external side. Citations: Bellemare et al., "Unifying Count-Based Exploration and Intrinsic Motivation," NeurIPS 2016; Six Birds Foundations V (*Endogenous Closure*), E9 Curiosity Law.
4. **Online algorithms with irrevocable commitments - structural.** Accepted/rejected commitments alter the feasible set for later requests, creating a history-generated obstruction landscape. This is structural unless a concrete scheduler supplies `gamma_n`, `rho_n`, and a covering or hole witness. Citations: Borodin and El-Yaniv, *Online Computation and Competitive Analysis*, Cambridge University Press, 1998; Boyar et al., "Relaxing the Irrevocability Requirement for Online Graph Algorithms," arXiv:1704.08835.
5. **Greedy sequences in combinatorial number theory - structural.** Mian-Chowla/Sidon and Stanley-type sequences choose new terms by avoiding constraints manufactured by previously chosen terms. They instantiate endogenous obstruction generation, but not G6's coverage/hole theorem without a separate rate audit. Citations: Mian and Chowla, "On the B_2 sequences of Sidon," *Proceedings of the National Academy of Sciences, India* A, 1944; Rolnick, "On the classification of Stanley sequences," arXiv:1408.1940.

### G7 - Adversarial Mobility Confinement

**Status:** `calibration-anchored schema`. Justification: the abstract law is a certificate-typing schema with named strategy obligations, while the classical angel problem fully calibrates both sides: the standard power-1 angel is confined, and every standard power `p>=2` angel escapes.

#### 1. Setup

Let `B` be a homogeneous board, usually the lattice graph `Z^2` with Chebyshev metric

```text
d_infty((x,y),(x',y')) = max(|x-x'|, |y-y'|).
```

Fix an agent mobility parameter `p>=1` and a devil deletion budget `b>=1`. In the standard angel game, `B=Z^2`, `b=1`, and a power-`p` angel may move each turn to a different undeleted square with `d_infty <= p`, jumping over deleted squares if necessary. Let `D_n subset B` be the deleted set after `n` devil moves and `a_n` the angel position. A visible finite history is

```text
H_n = (a_0,D_0,a_1,D_1,...,a_n,D_n).
```

At each unbounded turn, the angel chooses a legal next position from the `p`-ball around `a_n` outside `D_n`; then the devil deletes at most `b` visible squares not occupied by the angel. The angel wins if it has a strategy to move forever. The devil wins if it has a strategy that forces a finite time at which the angel has no legal move. The adversary's strategy space is part of the declared game data.

**[H-G7-escape-strategy: visible agent escape certificate.]** There is a declared angel strategy `sigma_A` mapping each finite visible history to a legal move, together with an invariant `I_n(H_n)` and a proof that for every legal devil strategy, following `sigma_A` keeps `I_n` true and leaves at least one legal undeleted move available at every finite turn.

**[H-G7-confinement-strategy: visible adversary confinement certificate.]** There is a declared devil strategy `sigma_D` mapping each finite visible history to at most `b` legal deletions, together with a wall, cut, ranking, or amortization proof that for every legal angel strategy, following `sigma_D` forces a finite turn `N` at which the angel has no legal move.

**Closest Foundations IV cousin.** F6, No-Needles Stability, declares the formed package's currency block, bridge block, residual budgets, and transport selector up front; it has no turn index and no adversary reacting to the run. G7 adds the missing game-valued axis: obstruction is selected adaptively by a visible adversary under a per-turn budget, and certification is a strategy proof over an unbounded play.

#### 2. Theorem

For a fixed board, mobility rule, and devil budget, exactly the following certificate statuses are admissible:

1. If `[H-G7-escape-strategy]` is discharged, the angel wins: every play consistent with the strategy is infinite.
2. If `[H-G7-confinement-strategy]` is discharged, the devil wins: every play against the strategy is trapped after finitely many turns.
3. If neither strategy certificate has been supplied, the parameter lies in the open band for that declared ruleset.

For the classical angel problem on `Z^2` with one deletion per turn, the threshold is fully known:

```text
p = 1      devil wins;
p >= 2    angel wins.
```

The loss of the power-1 angel is the early Conway/Berlekamp result recorded in *Winning Ways* and discussed in Kutz's angel-problem work. The power-2 angel wins by independent 2007 proofs of Mathe and Kloster. Bowditch independently proved that a power-4 angel wins; Gacs gave another independent high-power proof by a hierarchical method. Thus there is no remaining open `p` band for the standard two-dimensional one-devil game.

#### 3. Proof Spine

G7 does not reproduce the classical proofs. It extracts their certificate types.

For confinement, the devil certificate is a visible wall-building or cut-growth schedule. In the power-1 case the angel is too slow to cross a suitably amortized enclosing construction: the devil spends one deletion per turn but can arrange deleted squares so that every possible king move is eventually fenced. The proof obligation is not "the devil feels adversarial"; it is a finite strategy plus an invariant showing that every angel response remains inside a shrinking or closable legal region.

For escape, the angel certificate is a visible route-maintenance invariant whose progress outpaces the devil's unit deletion budget. Kloster's proof gives a constructive path-management strategy for the 2-angel: maintain a north-going path with left/right regions, update it when the devil blocks squares, and charge path-length increases to newly blocked squares. Mathe's proof reduces the real devil to a "nice devil" and uses a wall-following maze invariant to show a 2-angel cannot be trapped. Bowditch's proof shows a 4-angel wins by passing through auxiliary game variants and a circuitous-path/phantom-angel argument. Gacs's high-power proof uses a hierarchical escape construction. These proofs discharge `[H-G7-escape-strategy]` for the stated powers; by monotonicity, a higher-power angel can simulate any lower-power winning strategy.

#### 4. Case Enumeration

The table classifies one declared game record: board, move metric, angel power `p`, devil budget `b`, and visible strategy space.

| Case | Status | Witness type |
|---|---|---|
| (a) Confined | `[H-G7-confinement-strategy]` is discharged. | Devil strategy plus finite trap invariant; standard `p=1,b=1` angel belongs here. |
| (b) Escaping | `[H-G7-escape-strategy]` is discharged. | Angel strategy plus infinite-survival invariant; standard `p>=2,b=1` angels belong here. |
| (c) Open band | Neither certificate has been supplied for the declared ruleset. | Parameter record and unresolved obligation; none remains for standard `Z^2`, `b=1`, but variants may have open bands. |

The rows are mutually exclusive for a fixed declared game. If both an angel-winning and devil-winning strategy were valid, play the two strategies against each other; the resulting single play would have to be both infinite and finitely trapped, a contradiction. The rows are exhaustive as certificate statuses: a declared game has an escape certificate, a confinement certificate, or neither has been accepted.

#### 5. Interaction Status

G7 is P2 feasibility/mobility under a dynamic legal-move predicate plus P6 budget accounting for the devil's deletion rate. The angel strategy proves feasible continuation; the devil strategy proves a budgeted obstruction schedule. The adversarial structure is visible and typed in the audit, not an unspoken hidden oracle.

#### 6. Nonclaims

1. G7 does not claim a general threshold for arbitrary graphs, lattices, move metrics, or devil budgets. Thresholds are board- and rule-relative.
2. NC-18 is load-bearing: the adversary's strategy space must be fully declared and visible. No hidden-oracle devil is ever implicitly assumed.
3. The classical angel-problem mathematics is not new here. G7's contribution is the layer-agnostic certificate typing for mobility versus adversarial obstruction budget.
4. Finite-board searches, including G7-L1, are exhibits and mechanized sanity checks; they do not replace the infinite-board strategy proofs.

#### Layer Instantiations

1. **Angel problem - calibration.** On `Z^2` with one deleted square per turn, `p=1` is confined and `p>=2` escapes. Citations: Berlekamp, Conway, and Guy, *Winning Ways for your Mathematical Plays*, Vol. 2, Academic Press, 1982; Conway, "The Angel Problem," in *Games of No Chance*, MSRI Publications 29, 3-12, 1996; Bowditch, "The angel game in the plane," *Combinatorics, Probability and Computing* 16(3), 345-362, 2007; Mathe, "The angel of power 2 wins," *Combinatorics, Probability and Computing* 16(3), 363-374, 2007; Kloster, "A solution to the angel problem," *Theoretical Computer Science* 389(1-2), 152-161, 2007; Gacs, "The angel wins," arXiv:0706.2817.
2. **Pursuit-evasion and graph cop-number - structural/calibration.** Cops-and-robbers games similarly classify mobility versus capture strategies on declared graphs, but thresholds depend on graph class and capture rules. Citations: Nowakowski and Winkler, "Vertex-to-vertex pursuit in a graph," *Discrete Mathematics* 43, 235-239, 1983; Aigner and Fromme, "A game of cops and robbers," *Discrete Applied Mathematics* 8, 1-12, 1984.
3. **Routing under adversarial link failure - structural.** Dynamic network routing under adversarial queues or failures asks whether packet mobility and rerouting can outpace adversarial blockage rates. This is structural unless a concrete network model supplies both strategies. Citation: Borodin, Kleinberg, Raghavan, Sudan, and Williamson, "Adversarial Queuing Theory," *Journal of the ACM* 48(1), 13-38, 2001.
4. **Percolation navigation above criticality - structural.** Supercritical percolation provides infinite open clusters through random obstruction fields; it is a probabilistic analogue rather than an adaptive devil unless the adversary model is declared. Citations: Grimmett, *Percolation*, 2nd ed., Springer, 1999; Kesten, *Percolation Theory for Mathematicians*, Birkhauser, 1982.
5. **Robust motion planning with dynamic obstacles - structural.** Robotics uses explicit dynamic-obstacle models and safety/viability certificates to decide whether motion can continue without collision. This is G7-like when the obstacle budget and planner strategy are declared. Citations: LaValle, *Planning Algorithms*, Cambridge University Press, 2006; Fraichard and Asama, "Inevitable Collision States: A Step Towards Safer Robots?", *Advanced Robotics* 18(10), 1001-1024, 2004.

### Cluster C - Defect integration and emergent transport

Verified gaps: route defects in the corpus are binary and never integrate into potentials; nothing derives motion or transport from substrate dynamics; only the destructive direction of information loss is covered. Cluster C supplies odometers, defect-to-transport accounting, and lossful persistence.

### G8 - Odometer Abelianization

**Status:** `theorem`. Justification: the abstract theorem is the carrier-agnostic form of the classical abelian sandpile abelian property and least-action theorem, with the proof imported and adapted from Dhar (1990) and Fey-Levine-Peres (2010).

#### 1. Setup

Let `C` be a configuration space and let `V` be a finite or locally finite index set of sites. For each `v in V`, let `m_v: C -> C` be a partial local move, with legality predicate `L_v(c)` saying that `m_v` may be applied at configuration `c`. A run from `x in C` is an unbounded legal sequence

```text
x = c_0 --v_0--> c_1 --v_1--> c_2 --v_2--> ...
```

continued until no legal move remains, if such a time exists. Its counter vector is

```text
u_run(v) = #{ i : v_i = v } in N^V,
```

with `u_run(v)` finite when the run terminates and possibly infinite in the non-terminating case. A configuration is stable when no `L_v` holds. A vector `n in N^V` is sufficient for `x` when applying the multiset of moves prescribed by `n`, in some legal admissible stabilizing order, reaches a stable configuration.

**[H-G8: Abelian compatibility hypothesis, boxed and load-bearing.]** For all configurations `c` and all distinct sites `v != w`, if `L_v(c)` and `L_w(c)` both hold, then `m_v` preserves legality of `w`, `m_w` preserves legality of `v`, and

```text
m_w(m_v(c)) = m_v(m_w(c))
```

whenever both composites are defined; counters add by the standard basis vectors `e_v` and `e_w`, so the two two-step routes have the same counter vector `e_v + e_w`. The case `v = w` is outside the scope of this hypothesis entirely: `[H-G8]` does not require a move to preserve its own legality after firing. This hypothesis is discharged in the flagship instance by Dhar's abelian property for sandpiles; outside that setting it is an explicit proof obligation, not a metaphor.

**[H-G8-mono: least-action monotonicity hypothesis, boxed and separate.]** For least-action claims, the move system also carries a declared comparison structure supporting the sandpile/abelian-network monotonicity argument: stabilizing scripts are compared pointwise, legal move maps are compatible with the comparison, and adding extra available resource or delaying commuting legal moves cannot make a genuinely necessary firing disappear from every stabilizing script. This is not derived from `[H-G8]`. In the flagship sandpile instance it is discharged by the standard monotonicity/comparison lemma used in the least-action principle of Fey-Levine-Peres; for general carrier-agnostic systems it remains a separate proof obligation.

The temporal quantifier is the point of the law: G8 quantifies over every legal firing order in an unbounded run until termination, and over the whole accumulated counter vector, rather than over one fixed comparison square.

**Closest Foundations IV cousins.** F3, Holonomy-Memory Repair Normal Form, compares exactly two fixed routes once; when their outputs agree at the current quotient but differ at the predictive quotient, its output is "record the residue," not "produce one global scalar" or one canonical counter ledger. G8 is stronger and different: under `[H-G8]` and termination, all legal routes through an unbounded run integrate into one global odometer potential. F27, Conservation as Orbit Descent, presumes a quantity `C` already exists and characterizes conservation as orbit-constancy; it never constructs a potential. G8 constructs the conserved ledger from legal move counters and proves its route independence.

#### 2. Theorem

For a system `(C, V, {m_v}, L)` satisfying `[H-G8]`, fix an initial configuration `x`.

**Part A: abelian odometer.** If every maximal legal run from `x` terminates, then:

1. **Order-independent stabilization.** All legal terminating runs from `x` end at the same stable configuration `x^o`.
2. **Odometer invariance.** All legal terminating runs from `x` have the same counter vector `u_x in N^V`.

**Part B: least action.** If `[H-G8-mono]` is also supplied, then among all legally sufficient vectors `n in N^V` whose prescribed multiset of moves can be realized by some legal admissible stabilizing order from `x`, the odometer is pointwise minimal: `u_x(v) <= n(v)` for every `v in V`. Equivalently, the legal stabilization fires no site more than necessary relative to other legal stabilizations and no site fewer than legality plus the monotone comparison structure forces. This is a legal-vs-legal least-action theorem; it does not compare against arbitrary nonnegative scripts realized only by illegal or out-of-turn topplings.

Part A is the layer-agnostic form of Dhar's abelian property for sandpile automata. Part B is inspired by the FLP-style least-action proof for sandpiles and abelian-network-like carriers with the extra monotonicity data named in `[H-G8-mono]`, but this mechanization proves the narrower legal-vs-legal comparison, not the fully general Fey-Levine-Peres principle over arbitrary stabilizing scripts. In the finite graph sandpile with sink, `m_v` is toppling at `v`, legality is instability at `v`, and `u_x(v)` is the usual number of firings at `v` (Dhar, "Self-organized critical state of sandpile automaton models," *Physical Review Letters* 64, 1613-1616, 1990; Fey, Levine, and Peres, "Growth rates and explosions in sandpiles," *Journal of Statistical Physics* 138, 143-159, 2010, arXiv:0901.3805).

#### 3. Proof Spine

The proof is the standard abelian sandpile proof abstracted away from graphs.

First, `[H-G8]` gives a diamond-lemma-style local commutation rule for distinct legal moves with matched counters: whenever two different legal moves are available, either order reaches the same configuration and records the same two counter increments. By repeatedly swapping adjacent independent legal moves, any two legal terminating orders can be compared without changing the multiset of moves already accounted for. The terminating assumption prevents an infinite postponement defect, so local commutation propagates to order-independent final state and firing counts.

Second, least action uses `[H-G8-mono]`, not `[H-G8]` alone. Compare a legal stabilization with any other legally sufficient stabilizing vector `n`. If the legal run tried to fire some site more often than `n`, take the first time this pointwise domination fails. At that prefix, abelian compatibility plus the declared monotone comparison structure let the already-fired legal multiset be commuted against the declared sufficient multiset, contradicting the claim that `n` had already supplied enough moves to stabilize. The fully general Fey-Levine-Peres comparison class of arbitrary nonnegative stabilizing scripts, including force-firing scripts with illegal intermediate topplings, is not covered by this proof; this proof relies on `[H-G8]`'s legal-guarded commutativity and `[H-G8-mono]`'s legal-run exchange surface. This is the abstract pointer to the least-action proof in Fey-Levine-Peres; outside sandpile/abelian-network carriers it is a named obligation, not an automatic consequence of commutation.

#### 4. Case Enumeration

| Case | Status | Witness type |
|---|---|---|
| (a) Abelian with odometer | `[H-G8]` holds and every maximal legal run from `x` terminates; if `[H-G8-mono]` also holds, least action is included. | Proof of abelian compatibility, termination certificate, stable final state `x^o`, odometer `u_x`, and, when claimed, monotonicity/comparison proof. |
| (b) Confluent without canonical counters | The system terminates and has a unique normal form, but counter vectors depend on the route. This is the separating witness from mere confluence and from F3-style route-residue repair. | Concrete terminating rewrite system below. |
| (c) Non-terminating | Some legal run from `x` is infinite, so `u_run` may be infinite and least action has no finite odometer to certify. | Infinite legal run or failed termination budget; this belongs to G3's amortized-potential territory if a separate finite currency can bound the run. |
| (d) Terminating, non-confluent | All runs terminate, but legal routes can reach different stable final configurations, so neither a normal form nor an odometer is well-defined. | Concrete route-dependent-final-state witness below. |

This table enumerates the positive G8 case and the failure modes needed to separate G8 from confluence and termination. It is not a decision procedure for every terminating non-abelian system; terminating systems with accidentally route-independent counters but no `[H-G8]` proof are outside the positive theorem until the named hypotheses are supplied.

**Case (b) separating witness.** Let the states be `S, A, B, N`, with `N` normal. Let the legal moves be

```text
r: S -> A
s: S -> B
p: A -> N
q: B -> N
t: A -> N
```

There are no other moves. The system terminates because every move strictly decreases the rank `S > A,B > N`. It is confluent from `S`: every maximal route reaches the unique normal form `N`. But the move counters are route-dependent:

```text
S --r--> A --p--> N     has counter (r=1, p=1, s=0, q=0, t=0)
S --s--> B --q--> N     has counter (r=0, p=0, s=1, q=1, t=0)
S --r--> A --t--> N     has counter (r=1, t=1, s=0, p=0, q=0)
```

Thus unique normal form does not produce a canonical move-count ledger. The missing property is exactly `[H-G8]`: after `r` and `s` compete at `S`, the other branch is not preserved as a legal commuting move. Confluence records that route defects can be joined; G8 requires the stronger abelian compatibility that integrates route data into one odometer.

**Case (d) terminating non-confluent witness.** Let the states be `S, A, B`, with `A` and `B` both normal and distinct. Let the only legal moves be

```text
r: S -> A
s: S -> B
```

The rank `S > A,B` proves termination. The two maximal legal routes from `S` reach different stable final configurations, so confluence fails before any counter-canonical question can arise.

#### 5. Interaction Status

G8 turns P3 route/holonomy data into P6 audit/ledger content through a P2 conservation/abelian gate. The legal move order is P3 route data; the counter vector `u_x` is P6 bookkeeping content; `[H-G8]` is the P2 gate that makes the bookkeeping conserved across all legal routes. This is conditional on the abelian hypothesis and termination: it is not an unconditional claim that holonomy, route mismatch, or confluence implies a canonical potential, and it is not a `P6_drive` claim.

#### 6. Nonclaims

1. The odometer is a ledger/potential, never a drive, arrow, or entropy-production concept. The term `P6_drive` is reserved for genuine thermodynamic or EPR-style drive content, not for sandpile firing counts or route-integrated audit ledgers.
2. G8 sharpens but does not resolve Foundations II's open recognition-completeness question or Foundations III's missing holonomy-to-drive bridge. Foundations II, Remark `rem:recognition-open`, explicitly leaves finite conservation/balance laws and emergent assembled holonomy as possible recognition gaps; Foundations III records NC-12 and the missing `B_{3->6}^{drive}` bridge. G8 shows that this content is law-governed in the abelian/conservative case and takes no position on whether it is a genuine seventh primitive role.
3. `[H-G8]` is load-bearing and named. Non-abelian systems are outside this law's positive theorem; case (b) demonstrates that terminating confluence alone does not determine a canonical counter vector.
4. No novelty is claimed for the classical sandpile mathematics itself. Dhar's abelian property, Fey-Levine-Peres least action, and the rotor-routing/chip-firing literature supply the classical proof stack; the Foundations VI contribution is the layer-agnostic normal form and the separating witness that distinguishes odometer invariance from mere confluence.
5. Part B's least-action theorem compares the legal odometer only against other legally sufficient scripts, realized by some legal admissible order, not against the fully general class of arbitrary nonnegative integer scripts - including ones realized only via illegal or out-of-turn topplings - used in the classical Fey-Levine-Peres least-action principle. Extending to that fully general comparison class would require an unconditional, not merely legal-guarded, commutativity hypothesis on the move family, which is not assumed here.

#### Layer Instantiations

1. **Abelian sandpiles and rotor-routing - calibration.** Finite graph sandpiles with sink discharge `[H-G8]` by Dhar's abelian property and discharge least action by Fey-Levine-Peres. Rotor-routing is the deterministic sibling in the same abelian-network family; see Holroyd, Levine, Meszaros, Peres, Propp, and Wilson, "Chip-Firing and Rotor-Routing on Directed Graphs," *In and Out of Equilibrium 2*, Progress in Probability 60, 331-364, 2008, arXiv:0801.3306.
2. **Quantitative confluence certificates in rewriting - structural.** The corpus rewriting paper proves elementary flatness iff local confluence and confluence plus normalization gives a unique normal form, but its claim-support matrix leaves the full finite terminating left-linear TRS confluence-as-flatness theorem as "deferred" theorem packaging. G8 supplies part of the missing quantitative layer only for abelian sub-cases where route counters commute; it is not a general solution to that rewriting paper's deferred theorem package. Source checked: `six-birds-papers/Tsiokos_2026_To_Flatten_a_Stone_with_Six_Birds_Critical_Pairs_Holonomy_and_Confluence_in_Rewriting_Systems.tex`, Section `sec:proved-supported-deferred`.
3. **Distributed load balancing and gossip averaging - structural.** Diffusive load balancing and randomized gossip algorithms have conserved total mass/average and order-sensitive local exchanges; G8 applies only to subfamilies where local exchange counters commute and termination or convergence has a finite stabilization surrogate. References: Cybenko, "Dynamic load balancing for distributed memory multiprocessors," *Journal of Parallel and Distributed Computing* 7(2), 279-301, 1989; Boyd, Ghosh, Prabhakar, and Shah, "Randomized gossip algorithms," *IEEE Transactions on Information Theory* 52(6), 2508-2530, 2006.
4. **Neural avalanche models - structural, unverified for G8.** Neural avalanche work supplies a real avalanche/cascade literature, but biological avalanche dynamics are not automatically abelian and their event counters need not be route-independent. The citable anchor is Beggs and Plenz, "Neuronal avalanches in neocortical circuits," *Journal of Neuroscience* 23(35), 11167-11177, 2003. To upgrade this beyond structural, one would need a precise model with commuting local relaxations and a certified finite odometer.
5. **Settlement netting and clearing vectors - structural, unverified for G8.** Clearing systems have ledger-like conservation and least/clearing fixed-point constructions, but ordinary financial settlement is not automatically an abelian local-move system. The citable anchor is Eisenberg and Noe, "Systemic Risk in Financial Systems," *Management Science* 47(2), 236-249, 2001. To instantiate G8 strictly, one must exhibit local settlement moves whose counters commute and whose clearing vector is the resulting odometer-like least action object.

### G9 - Defect-Evacuation-to-Transport

**Status:** `calibration-anchored schema`. Justification: the mechanism is completely discharged in the rule-184 traffic cellular automaton, but the abstract implication still depends on named census and absorption hypotheses rather than on a carrier-agnostic proof covering all extended systems.

#### 1. Setup

Let `X` be a spatial lattice or graph with translation action `shift_d`, let `S` be a finite local state set, and let `T: S^X -> S^X` be a synchronous cellular automaton or declared local update on configurations. A run is the unbounded sequence

```text
c_0, c_1 = T(c_0), c_2 = T(c_1), ...
```

indexed by `n in N`. Fix a regular reference background family `B_n` such that `B_{n+1}=T(B_n)` or such that the mismatch between `T(B_n)` and `B_{n+1}` is explicitly recorded. A defect at time `n` is a finite, typed witness that `c_n` differs from `B_n` on a declared local patch. The defect census is a typed ledger

```text
delta_n = (D_n, create_n, annihilate_n, bind_n, absorb_n),
```

where `D_n` is the finite set, multiset, or measured set of active defects and each event family is a per-step accounting record from `D_n` to `D_{n+1}`: creation, annihilation, binding into a finite composite, or absorption into a transporter. The scalar count `|delta_n|` may be used only when the event ledger states which measure of defects it counts.

A transporter is a finite pattern record

```text
R = (P, W, tau, d, t0, certificate)
```

with finite support window `W`, period `tau > 0`, and displacement vector `d`. Its certificate is checkable: for every `k >= 0` in the certified regime and every site `x in W + k d`,

```text
c_{t0 + (k+1) tau}(x + d) = c_{t0 + k tau}(x),
```

with the same equality recorded after translating the whole finite support of `P`. When a global transport regime is claimed, the witness must give either one common `(tau,d)` for the active region or a finite list of component transporter records with explicitly disjoint supports and velocities.

**[H-G9-census: typed defect-accounting hypothesis, boxed.]** The run carries an exact defect ledger: every active defect at time `n` is either continued, annihilated, bound, absorbed, or explicitly marked unresolved at time `n+1`, and every new defect at `n+1` is charged to a creation event. There is a finite `N` such that for all `n >= N`, the unresolved defect measure is non-increasing after accounting for bound and absorbed defects:

```text
|unresolved_{n+1}| <= |unresolved_n|.
```

**[H-G9-absorb: transporter-absorption hypothesis, boxed.]** There are finite constants `N,T` and a finite family of transporter records `{R_j}` such that every defect still unresolved for `T` steps after time `N` is either annihilated, bound into a finite non-moving composite, or assigned by the ledger to exactly one transporter record. The positive transport conclusion uses the transporter-assigned branch; the bound-composite branch is the defect-bound case below, not a transport claim.

The temporal quantifier is essential: G9 quantifies over the whole tail of the run, asking whether the defect census eventually evacuates into recurrence-with-displacement records. It does not classify one fixed pattern at one fixed time.

**Closest Foundations IV cousin.** F19, Object Persistence, starts with carriers `H_i,H_j`, access quotients, and a declared transport `gamma: H_i -> H_j`; its theorem checks whether an already-posited object identity persists through that already-posited transport. G9 has the opposite logical type. The transporter is not declared at the start as the object whose persistence is to be checked; it emerges over unbounded time from many local defects, and the law requires a census showing that the residual defects have been evacuated into a newly certified recurrence-with-displacement record.

**Separating witness from F19.** Consider a one-dimensional local lattice rule over background `.` with one defect state `X` and transporter states `A,B`: an isolated `X` becomes `AB` in one step, and thereafter `AB` shifts one site to the right at every step. Starting from one `X`, no transporter object or declared transport exists at time `0`; after time `1`, the record `(P=AB, tau=1, d=+1)` is checkable forever. F19 can verify persistence only after that transport has been declared. G9 is the law that audits the evacuation event `X -> AB` and promotes the emergent recurrence record to the transport certificate.

#### 2. Theorem

For a run of an extended local system with Setup data as above:

**Positive schema.** If `[H-G9-census]` holds, `[H-G9-absorb]` holds, and the persistent-defect set assigned to transporter records is nonempty, with at least one assigned transporter having nonzero displacement `d != 0`, then the run enters a certified transport regime. Concretely, there is a finite time `t0` and a finite nonempty family of transporter records `{R_j=(P_j,W_j,tau_j,d_j,t0_j)}` such that every transporter-assigned persistent defect after `t0` is covered by one of the `R_j`, and each `R_j` satisfies its recurrence-with-displacement equality on its declared support. Persistent defects not assigned to a transporter may still be bound into finite stationary residue; those mixed outcomes remain transport-certified because the moving transporter subset is nonempty. In the single-transporter or common-velocity case, this is eventual spatio-temporal periodicity modulo translation:

```text
c_{t + tau}|_{W + d} = shift_d(c_t|_W)   for all certified t >= t0.
```

**Negative schema.** If the ledger has unbounded unresolved creation, meaning `sup_n |unresolved_n| = infinity` or infinitely many creation events remain unmatched by annihilation, binding, or absorption, then the positive transport claim is blocked. The witness is the defect-proliferation ledger itself; no recurrence-with-displacement record may be inferred from finite local motion or from holonomy language alone.

If all defects are eventually annihilated or otherwise resolved with no persistent transporter-assigned defect, the run is cleared/quiescent, not transport-certified.

The rule-184 traffic automaton discharges this schema as a calibration instance: under the usual particle interpretation, density below `1/2` yields eventual free-flow of particles, density above `1/2` yields the dual free-flow of holes/jam motion, and density exactly `1/2` yields the alternating critical pattern on finite periodic systems. This is the solved traffic-rule mechanism described in the rule-184 and particle-hopping literature, including Fuks (1997), Nagel (1996), and Chowdhury, Santen, and Schadschneider (2000).

#### 3. Proof Spine

This is a schema, so the proof spine is the required discharge pattern rather than a complete abstract proof.

First, the event ledger must prove that defect creation is eventually controlled: after some `N`, every created defect is paired with a later annihilation, binding, or absorption event, and the unresolved defect measure never increases along the certified tail. Second, the persistent-defect branch must be exhausted by transporter absorption records, not merely by visual pattern recognition. Third, each transporter record must carry a finite recurrence-with-displacement certificate; without that equality, motion has not been certified.

In rule 184 this proof spine is discharged combinatorially. The update swaps every adjacent `10` to `01`, conserves particle number, and evolves finite periodic configurations toward the known low-density free-flow, high-density jam/hole-flow, or critical alternating regimes. The defect ledger is the count and arrangement of blocked cars or holes, and the transport record is the eventual periodic shift. The literature anchors used here are Fuks, "Solution of the Density Classification Problem with Two Cellular Automata Rules," *Physical Review E* 55, R2081-R2084, 1997, arXiv:comp-gas/9703001; Nagel, "Particle hopping models and traffic flow theory," *Physical Review E* 53, 4655-4672, 1996, arXiv:cond-mat/9509075; and Chowdhury, Santen, and Schadschneider, "Statistical physics of vehicular traffic and some related systems," *Physics Reports* 329, 199-329, 2000, arXiv:cond-mat/0007053.

#### 4. Case Enumeration

| Case | Status | Witness type |
|---|---|---|
| (a) Cleared / quiescent | All defects are eventually annihilated or resolved, and no persistent transporter or bound residue remains. This is not a transport claim. | Tail time `N` with empty persistent-defect set and ledger records closing every prior defect by annihilation or resolution. |
| (b) Transport-certified | At least one persistent defect is assigned to a transporter record with nonzero displacement. Other persistent defects may also be bound into stationary residue. | Nonempty transporter-assigned defect subset, recurrence-with-displacement record `(P,W,tau,d,t0)` with `d != 0`, and ledger assignments for any bound residual defects. |
| (c) Defect-bound only | Persistent defects exist, none is assigned to a nonzero-displacement transporter, and all are bound into finite stationary composites, oscillators, or stable residues. | Bounded census tail plus certificate that every persistent component has `d=0` or no transporter record. |
| (d) Defect-proliferating | Defect creation is unbounded or remains unmatched forever, regardless of any partial transport records. | Ledger witness with `sup_n |unresolved_n| = infinity` or an infinite unmatched creation family. |
| (e) Undetermined with census budget | The run has only a finite-depth census or an unresolved tail obligation. | Audit horizon `K`, current defect budget, unresolved event list, and an explicit statement that no eventual transport claim is made beyond `K`. |

These cases partition certified statuses for a declared run by priority: finite-depth or unresolved audits are (e); otherwise unbounded unmatched creation is (d); otherwise an empty persistent-defect set is (a); otherwise a nonempty nonzero-displacement transporter subset is (b); otherwise the remaining bounded persistent defects are (c). This is not a decidability theorem for arbitrary cellular automata.

#### 5. Interaction Status

G9 uses P5 packaging/pattern-recognition to identify defect composites and transporter records, and P6 ledger content to account for creation, annihilation, binding, and absorption events. The transport certificate is the finite recurrence-with-displacement equality, not an entropy-production or arrow-of-time certificate. Route or holonomy data alone never licenses the conclusion; the law requires its own explicit structural transport record and census ledger.

#### 6. Nonclaims

1. Emergent transport in G9 is never called drive or `P6_drive`. That term remains reserved for genuine entropy-production or EPR-style drive content. The Protocol Trap discipline applies: route dependence, holonomy, or visually directional motion is not an arrow of time without the proper drive certificate.
2. The Langton's-ant highway conjecture is open. G9 does not claim that every finite initial configuration reaches the 104-step highway, and finite simulations do not upgrade the conjectural instance to a theorem.
3. No novelty is claimed for the classical cellular-automaton or traffic-rule mathematics. Rule 184, particle-hopping traffic models, and known CA glider examples supply the calibration and instance material; G9 supplies the layer-agnostic census-and-transport normal form.
4. A certified recurrence-with-displacement record is finite and checkable at the depth it names. It is not a proof of eventual or asymptotic behavior beyond that depth unless the instance supplies a solved theorem, as rule 184 does.

#### Layer Instantiations

1. **Rule 184 / traffic cellular automata - calibration.** Rule 184 has an exact particle-hopping interpretation and solved density regimes: free particle flow below density `1/2`, dual hole/jam flow above density `1/2`, and the alternating critical case at density `1/2` on finite periodic systems. Citations: Fuks, "Solution of the Density Classification Problem with Two Cellular Automata Rules," *Physical Review E* 55, R2081-R2084, 1997, arXiv:comp-gas/9703001; Nagel (1996); and Chowdhury, Santen, and Schadschneider (2000). This is the calibration instance discharging the G9 census-to-transport mechanism.
2. **Langton's ant - conjectural.** The highway claim remains open for arbitrary finite initial configurations, and this remains open through the most recent literature checked (2024-2025). The standard ant was introduced by Langton, "Studying artificial life with cellular automata," *Physica D* 22, 120-149, 1986. Trajectory unboundedness is a separate, proved result: Bunimovich and Troubetzkoy, "Recurrence properties of Lorentz lattice gas cellular automata," *Journal of Statistical Physics* 67(1-2), 289-302, 1992 (independently verified 2026-07-08 against three sources, including two specialist surveys that confirm this 1992 paper's general Lorentz-lattice-gas result explicitly covers the standard two-color ant). A popular but incorrect rival attribution, the "Cohen-Kong theorem" (traced to Stewart's 1994 *Scientific American* account), is explicitly flagged as incorrect by secondary literature and should not be used; the specialist literature cites Bunimovich-Troubetzkoy exclusively. This unboundedness fragment remains a Nonclaim-scoped citation, not a G9 discharge: G9's own theorem and lab are fully carried by Rule 184, not Langton's ant.
3. **Excitable-media cellular automata and soliton-like pulses - structural, unverified for G9.** Greenberg-Hastings-style cellular automata provide discrete excitable-media waves and spiral cores, but G9 requires an explicit defect census and transporter recurrence record for a specific model. Citations: Greenberg, "Spatial patterns for discrete models of diffusion in excitable media," *SIAM Journal on Applied Mathematics* 34, 515-523, 1978; Durrett and Griffeath, "Asymptotic behavior of excitable cellular automata," arXiv:patt-sol/9303002.
4. **Cellular-automata glider ecology / ALife - structural.** Conway Life gliders and related CA particles are direct recurrence-with-displacement objects. They instantiate the transporter witness when the period/displacement equality is checked, but arbitrary debris-to-glider emergence remains model-specific. Citations: Gardner, "Mathematical Games: The fantastic combinations of John Conway's new solitaire game Life," *Scientific American*, October 1970; Pivato, "Defect particle kinematics in one-dimensional cellular automata," arXiv:math/0506417.
5. **Queue-clearing and traffic shock waves in OR - structural, unverified for G9.** Kinematic traffic waves and cell-transmission models supply moving jam/clearing-front analogues, but a G9 instance requires a discrete event ledger matching creation, annihilation, and absorption of queue defects. Citations: Lighthill and Whitham, "On kinematic waves. II. A theory of traffic flow on long crowded roads," *Proceedings of the Royal Society A* 229, 317-345, 1955; Richards, "Shock waves on the highway," *Operations Research* 4, 42-51, 1956; Daganzo, "The cell transmission model: A dynamic representation of highway traffic consistent with the hydrodynamic theory," *Transportation Research Part B* 28, 269-287, 1994.

### G10 - Lossful Boundary Persistence

**Status:** `theorem`. Justification: once the protection and regeneration hypotheses are stated, the positive law is a direct induction. The Ducci calibration supplies the collapse-side witness, not a positive persistence discharge.

#### 1. Setup

Let `X` be a state space and let `D: X -> X` be a declared destructive operator. Destructive means lossful in the explicit sense that `D` is not injective: there exist `x != y` with `D(x)=D(y)`. Let `b: X -> B` be a declared boundary readout and let `rho: B -> B` be the declared boundary-update function. Let `I: X -> Prop` be an interior invariant predicate.

For an initial state `x_0`, write the unbounded iterated run as

```text
x_{n+1} = D(x_n),  n = 0,1,2,...
```

G10 asks whether the boundary relationship survives every iteration of the lossy map, not merely one application.

**[H-G10-protect: protection hypothesis, boxed.]** For every state `x`, if `I(x)` holds, then the next boundary value is exactly determined by the current boundary value:

```text
I(x) => b(D(x)) = rho(b(x)).
```

This is the exact functional relationship; no unstated "target value" is allowed.

**[H-G10-regen: regeneration hypothesis, boxed.]** For every state `x`,

```text
I(x) => I(D(x)).
```

The invariant must survive the destructive step. Empirical persistence of the boundary without this regeneration proof is not a G10 theorem instance.

**Closest Foundations IV cousin.** F34, Information Loss Normal Form, starts with source and later carriers `H_0,H_1` and one declared transport `tau: H_0 -> H_1`; it characterizes when a single lossy step is legitimate because every later identification is invisible to the declared source information. G10 has the opposite direction and a temporal quantifier: it studies unbounded iteration of one lossy operator and proves that one declared boundary relationship can persist forever, but only because a separately declared interior invariant regenerates the protection at every step. This is the constructive persistence counterpart to the corpus's destructive direction, not a reversal of information loss.

#### 2. Theorem

Assume `[H-G10-protect]`, `[H-G10-regen]`, and `I(x_0)`. Then for every `n >= 0`:

1. `I(x_n)` holds.
2. The boundary obeys the iterated protection law

```text
b(x_n) = rho^n(b(x_0)).
```

Equivalently, at every step `n`,

```text
b(x_{n+1}) = rho(b(x_n)).
```

The theorem is unconditional given the named hypotheses. It does not require `D` to be invertible and does not reconstruct lost interior information.

#### 3. Proof Spine

The proof is induction on `n`.

Base case: `I(x_0)` is an explicit assumption, and `b(x_0)=rho^0(b(x_0))` by definition of zero-fold iteration.

Inductive step: assume `I(x_n)` and `b(x_n)=rho^n(b(x_0))`. By `[H-G10-regen]`, `I(D(x_n))`, so `I(x_{n+1})`. By `[H-G10-protect]`,

```text
b(x_{n+1}) = b(D(x_n)) = rho(b(x_n)) = rho(rho^n(b(x_0))) = rho^{n+1}(b(x_0)).
```

Thus both the invariant and the boundary law hold for all `n`.

The Ducci game verifies the destructive/collapse side literally, not the positive protection side. For `k=2^m`, let `S` be the cyclic shift on `k` coordinates. Modulo `2`, the Ducci map is the linear operator `L=I+S`, since `|a-b| = a+b mod 2`. In characteristic `2`, the freshman-dream identity gives

```text
L^{2^m} = (I+S)^{2^m} = I + S^{2^m}.
```

Because `S^k=I` and `k=2^m`, this equals `I+I=0` over `F_2`. Hence after each block of `k` Ducci steps the tuple becomes divisible by one more power of `2`. Integer Ducci iterates are bounded after the first step by the initial range, so divisibility by arbitrarily high powers of `2` forces the tuple to become all zero. Therefore any nonzero boundary persistence claim for all initial `2^m`-tuples collapses unless it has a different invariant than the nilpotently destroyed parity structure.

#### 4. Case Enumeration

| Case | Status | Witness type |
|---|---|---|
| (a) Certified-persistent | `[H-G10-protect]`, `[H-G10-regen]`, and `I(x_0)` are proved for the declared `D,b,rho,I`. | The two boxed hypothesis proofs plus the induction theorem. |
| (b) Collapsing | A finite collapse certificate shows the proposed protecting structure is destroyed or the state reaches a nilpotent terminal class. | Nilpotency/ranking certificate; for Ducci with `k=2^m`, the mod-2 proof above plus boundedness. |
| (c) Persistent empirically at bounded depth | Boundary persistence has been checked only through a finite depth `K`. | Exact computation record through `K`, with no claim for `n>K`. |
| (d) Unclassified / no invariant supplied | No regeneration proof, collapse proof, or bounded-depth certificate has been supplied. | Missing invariant or unresolved obligation record. |

These cases partition the certified status of a declared G10 boundary-persistence claim by priority: a full protection/regeneration proof is (a); failing that, a collapse proof is (b); failing that, finite evidence is (c); otherwise the claim is unclassified (d). This is not a decision procedure for arbitrary lossy operators.

#### 5. Interaction Status

G10 concerns which content survives repeated P5-style compression/packaging and how P6 audit records certify that survival. The boundary readout is declared content, the interior invariant is the protection record, and the induction is the audit trail across the run. This is not a `P6_drive` or arrow-of-time claim; no entropy-production direction is inferred.

#### 6. Nonclaims

1. G10 does not contradict the corpus's data-processing or granularity-collapse results. Those results say that information lost by a declared lossy map is not generically recoverable and that a single compression is legitimate only when lost distinctions are declared invisible. G10 says only that one declared boundary relationship can survive repeated loss when `[H-G10-protect]` and `[H-G10-regen]` are independently proved. It is not a generic reversibility claim.
2. Gilbreath's conjecture is open. The claim that every iterated absolute-difference row of the primes begins with `1` remains conjectural; any computational verification stays at bounded-verification or probabilistic status, never a proof.
3. No novelty is claimed for the classical Ducci-game linear-algebra result. Ducci supplies the collapse-side calibration for this normal form.
4. The gap-structure reframing of Gilbreath is heuristic. Odlyzko's computation and later random-analogue work support studying gap-smallness/randomness as the interior-invariant candidate, but this is not a theorem proving Gilbreath.

#### Layer Instantiations

1. **Ducci games - calibration, collapsing case.** `D(x_1,...,x_k)=(|x_1-x_2|,...,|x_k-x_1|)` is destructive: all constant tuples map to zero, so distinct inputs collide. For `k=2^m`, the mod-2 operator `I+S` is nilpotent as shown above, and boundedness of integer Ducci iterates forces all-zero collapse. For non-powers of two, sequences are eventually periodic and may enter nonzero cycles. Citations: Chamberland and Thomas, "The N-Number Ducci Game," *Journal of Difference Equations and Applications* 10(3), 339-342, 2004; Breuer, "Ducci sequences in higher dimensions," *Integers* 7, 2007; Breuer et al., "Ducci-sequences and cyclotomic polynomials," *Finite Fields and Their Applications* 13, 293-304, 2007.
2. **Gilbreath / Proth-Gilbreath conjecture - conjectural.** Let `D` be iterated absolute difference on prime rows and `b` be the first entry. The target relationship is `rho(2)=1` and `rho(1)=1`, with conjectural interior invariant `I` a suitable small-gap/randomness condition on the row. The conjecture is open. Citation for computation: Odlyzko, "Iterated absolute values of differences of consecutive primes," *Mathematics of Computation*, 1993. The small-gap/randomness reframing is treated as heuristic here; a precise random analogue is Chase, "A random analogue of Gilbreath's conjecture," arXiv:2005.00530.
3. **Finite-difference schemes and boundary-condition stability - structural.** Repeated finite-difference updates are lossy at unresolved scales, while boundary conditions or summation-by-parts/simultaneous-approximation-term structures can preserve declared boundary constraints. This is structural unless a specific scheme supplies `[H-G10-protect]` and `[H-G10-regen]`. Citations: Strikwerda, *Finite Difference Schemes and Partial Differential Equations*, SIAM; Gustafsson, Kreiss, and Oliger, *Time Dependent Problems and Difference Methods*, Wiley; Coulombel and Faye, "Sharp stability for finite difference approximations of hyperbolic equations with boundary conditions," arXiv:2102.03066.
4. **Edge detection under repeated smoothing/differencing - structural, unverified for G10.** Scale-space smoothing destroys high-frequency detail, while selected edge or zero-crossing structures may persist under declared conditions. This remains structural until the edge invariant and regeneration condition are proved for a concrete operator. Citations: Canny, "A Computational Approach to Edge Detection," *IEEE Transactions on Pattern Analysis and Machine Intelligence* 8, 679-698, 1986; Witkin, "Scale-space filtering," IJCAI, 1983.
5. **Checksum cascades and error propagation - calibration, worked positive toy; structural for production systems.** Let `X={0,1}^2 x {0,1}` with states `x=((a,b),c)`. Let the boundary readout be `bdy(x)=c`, let `rho(c)=c`, and let the interior invariant be `I(x): c = a xor b`. Define the destructive map

```text
D(((a,b),c)) = ((c,0),c).
```

This map is not injective: `((0,0),0)` and `((1,1),0)` both map to `((0,0),0)`. If `I(x)` holds, then `bdy(D(x))=c=rho(bdy(x))`, so `[H-G10-protect]` holds. Also `D(x)=((c,0),c)` satisfies `c = c xor 0`, so `[H-G10-regen]` holds. Therefore the checksum boundary value persists for all iterates by the G10 induction theorem, while the original two-bit data block is genuinely lost. Real checksum cascades require their own algebraic invariants and remain structural beyond this toy. Citations: Fletcher, "An Arithmetic Checksum for Serial Transmissions," *IEEE Transactions on Communications*, 1982; Stone, Greenwald, Partridge, and Hughes, "Performance of Checksums and CRCs over Real Data," *IEEE/ACM Transactions on Networking* 6, 529-543, 1998.

### Cluster D - Productive obstructions and sparse saturation

Verified gap: corpus obstructions are negative, to be priced, dissolved, or confined. Cluster D covers obstructions that produce global structure, certify global facts by surviving, and sparse generators that saturate thick targets.

### G11 - Local-Rule Global-Anti-Symmetry

**Status:** `theorem`. Justification: given the named hierarchy and nonemptiness hypotheses, the abstract implication is a direct proof: local rules force a hierarchy at unbounded scales, and every nonzero period is contradicted at a sufficiently large scale. Classical aperiodic tilings supply solved calibration instances; Berger's undecidability result limits recognition, not the theorem once certificates are supplied.

#### 1. Setup

Let `C` be a finite local constraint system over configurations `x: Z^d -> A`, with finite alphabet `A`; equivalently, let `C` be a subshift of finite type specified by finitely many forbidden patterns. The flagship case has `d=2` and `C` is a Wang-tile or geometric-tile matching rule. A nonzero vector `p in Z^d` is a candidate period when

```text
x(v+p) = x(v) for every v in Z^d.
```

A **per-period defect certificate** for `p` is a finite region `R_p subset Z^d` plus a proof that the local rules of `C`, restricted to `R_p`, are inconsistent with the equalities `x(v+p)=x(v)` wherever both sides are represented in the finite audit. This is the NC-14 gate: local rules do not imply global anti-symmetry unless the per-period obstruction is actually supplied.

A **hierarchy certificate** is a forced composition structure: scales `L_k -> infinity`, finite block types `B_k`, and locally readable block-origin/marker data such that every admissible configuration has a unique decomposition into `k`-blocks for every `k`, with `(k+1)`-blocks composed from `k`-blocks.

**[H-G11-hierarchy: forced unique composition.]** Every globally admissible `C`-configuration carries the declared hierarchy uniquely at every scale `k`; the hierarchy is locally forced by the rules of `C`; and for every nonzero period vector `p`, some scale `k` has forced marker/block structure that cannot be invariant under translation by `p`.

**[H-G11-nonempty: admissible configuration.]** There exists at least one global configuration satisfying all local rules of `C`.

**Closest Foundations IV cousins.** F4, Local-Global Obstruction Normal Form, starts with one declared finite patch system and classifies one local family by whether it globalizes. G11 is not that finite gluing question: it is a `forall p` generative forcing statement, where every candidate period vector in an infinite family must receive its own finite defect certificate. F40, Anomaly / Symmetry Obstruction, diagnoses whether one declared symmetry action descends through one quotient/readout package. G11 forces all nonzero translational symmetries to fail simultaneously by a hierarchy whose scales grow without bound.

#### 2. Theorem

Assume `[H-G11-hierarchy]` and `[H-G11-nonempty]`.

1. Admissible configurations exist by `[H-G11-nonempty]`.
2. For every nonzero period vector `p`, `[H-G11-hierarchy]` supplies a scale `k` whose forced block/marker structure cannot be invariant under `p`.
3. Because the hierarchy is locally forced, this contradiction can be witnessed in a finite region `R_p`, giving a per-period defect certificate.
4. Therefore no admissible configuration has any nonzero period; every admissible configuration is aperiodic.

**Undecidability face.** For an arbitrary finite Wang tile set, deciding whether `[H-G11-nonempty]` holds is the domino problem, and Berger proved it undecidable. Thus the case table below is a real logical classification of outcomes, but there is no general algorithm that decides which case an arbitrary declared tile set belongs to. G11 does not get around Berger's theorem.

#### 3. Proof Spine

The Robinson-style proof shape is hierarchical forcing. Local matching rules force small recognizable blocks; those blocks compose into larger blocks; the larger blocks compose again; and the process continues at unbounded scales. If a tiling had period `p`, then at a scale much larger than `|p|`, the forced block-origin or marker grid would have to be invariant under translation by `p`. The unique-composition certificate says this cannot happen. Since the rules forcing that scale are local, the contradiction is witnessed on a finite patch, which becomes the per-period defect certificate.

Classical calibrations instantiate this shape in different ways. Berger proved the domino problem undecidable in 1966 and, as part of that work, obtained the first aperiodic Wang tile set; the published set is commonly reported as `20,426` tiles, with later reductions in unpublished or follow-up work. Robinson's 1971 construction gives a six-prototile aperiodic set and a clear forced square-hierarchy proof. Penrose introduced aperiodic planar tile sets in the 1970s, including two-tile kite/dart and rhomb versions with matching rules and inflation/deflation hierarchy. Smith, Myers, Kaplan, and Goodman-Strauss announced the hat monotile in 2023: the hat is a single polykite shape, but its tilings require use of reflected copies, so the proof treats it as an aperiodic monotile with reflections allowed. The same team then announced the spectre in 2023: a related chiral aperiodic monotile that tiles aperiodically using rotations and translations only, with no reflected copies required; their papers appeared in *Combinatorial Theory* in 2024.

#### 4. Case Enumeration

The table classifies one declared constraint system `C`.

| Case | Logical status | Witness type |
|---|---|---|
| (a) Periodic-admissible | `C` has at least one admissible periodic configuration. | Period vector `p != 0` plus a finite fundamental-domain certificate satisfying all local rules. |
| (b) Aperiodicity-forced | `C` has admissible configurations, but every admissible configuration is aperiodic. | `[H-G11-nonempty]` plus per-period defect certificates; `[H-G11-hierarchy]` is the flagship certificate generator. |
| (c) Empty | No admissible global configuration exists. | Emptiness proof, finite contradiction where available, or external unsatisfiability certificate. |

The three rows are mutually exclusive and exhaustive as a logical classification: a constraint system either has no global configuration, has a global configuration with some nonzero period, or has global configurations but none periodic. The classification is not an effective decision procedure for arbitrary finite tile sets; Berger's domino-problem undecidability is exactly the obstruction to such an algorithm.

#### 5. Interaction Status

G11 is P2 constraint/gating by local rules, P4 hierarchy/staging across forced scales, and P1 descent obstruction for every candidate period vector. The productive obstruction is local-rule incompatibility with periodic descent: each `p` fails through a finite defect certificate, while the hierarchy supplies the unbounded family of such defects.

#### 6. Nonclaims

1. G11 does not provide an algorithm for classifying arbitrary finite tile sets as periodic-admissible, aperiodicity-forced, or empty. Berger's undecidability theorem remains in force.
2. No novelty is claimed for the classical aperiodic tiling constructions of Berger, Robinson, Penrose, or Smith-Myers-Kaplan-Goodman-Strauss.
3. The hierarchy-certificate hypothesis is specific to the proof pattern used here. Other aperiodicity proofs are G11 instances only if they supply an analogous per-period defect generator.
4. Physical quasicrystals are not claimed to literally satisfy `[H-G11-hierarchy]` unless a specific model supplies the local rules, nonemptiness proof, and period-defect certificates.
5. G11-L1 is a finite-period mechanization lab for small Wang sets; it is an exhibit of the per-period certificate schema, not a decision procedure for the general domino problem.

#### Layer Instantiations

1. **Aperiodic tilings and Wang tile sets - calibration.** Berger, Robinson, Penrose, and the hat/spectre monotiles provide solved aperiodicity constructions; the hierarchy/per-period-defect mechanism is the flagship calibration. Citations: Berger, *The Undecidability of the Domino Problem*, Memoirs of the AMS 66, 1966; Robinson, "Undecidability and Nonperiodicity for Tilings of the Plane," *Inventiones Mathematicae* 12, 177-209, 1971; Penrose, "The role of aesthetics in pure and applied mathematical research," *Bulletin of the Institute of Mathematics and its Applications* 10, 266-271, 1974; Smith, Myers, Kaplan, and Goodman-Strauss, "An aperiodic monotile," arXiv:2303.10798 / *Combinatorial Theory*, 2024; Smith, Myers, Kaplan, and Goodman-Strauss, "A chiral aperiodic monotile," arXiv:2305.17743 / *Combinatorial Theory*, 2024.
2. **Quasicrystals - structural/empirical bridge.** Quasicrystals exhibit long-range order without translational periodicity, but a physical material is a G11 instance only after a precise local-rule or model hierarchy is supplied. Citations: Shechtman, Blech, Gratias, and Cahn, "Metallic Phase with Long-Range Orientational Order and No Translational Symmetry," *Physical Review Letters* 53, 1951-1953, 1984; Senechal, *Quasicrystals and Geometry*, Cambridge University Press, 1995.
3. **Symbolic dynamics and subshifts of finite type - calibration/structural.** Multidimensional SFTs are the formal home of local constraints whose global configurations may be periodic, aperiodic, or empty; aperiodic SFT constructions are direct G11 calibrations when a hierarchy proof is supplied. Citations: Lind and Marcus, *An Introduction to Symbolic Dynamics and Coding*, Cambridge University Press, 1995; Durand, Romashchenko, and Shen, "Fixed Point and Aperiodic Tilings," arXiv:0802.2432.
4. **Constraint satisfaction with forced non-repetition - structural.** CSP encodings can force global asymmetry or non-repetition through local clauses, but they are G11 instances only when they provide nonempty global models and per-period or symmetry-defect certificates. Citation: Dechter, *Constraint Processing*, Morgan Kaufmann, 2003.
5. **Synchronization and coding patterns - structural.** Synchronization strings and related coding constructions use local labels to prevent ambiguous repeated alignments; this is structurally G11-like when the forbidden-period ambiguity has a finite certificate. Citation: Haeupler and Shahrasbi, "Synchronization Strings: Codes for Insertions and Deletions Approaching the Singleton Bound," STOC 2017.

### G12 - Finite Witness Radiation

**Status:** `theorem`. Justification: after narrowing "radiation" to the two admitted ingredients--group orbit and compactness bridge--the core claim is a direct finite-witness theorem. The Hadwiger-Nelson lower bound supplies a fully precise recognition source: `cert(W)` is a finite unit-distance graph plus a finite non-4-colorability certificate.

#### 1. Setup

Let `X` be a carrier with a graph relation `E subset X x X` and let `Gamma` be a group acting transitively on `X` by automorphisms of `E`. In the flagship, `X=R^2`, `E(x,y)` means `||x-y||_2=1`, and `Gamma` is the Euclidean isometry group generated by translations, rotations, and reflections.

For `k>=1`, a proper `k`-coloring is a function

```text
c: X -> {1,...,k}
```

such that `E(x,y)` implies `c(x) != c(y)`. For a finite `W subset X`, let `G[W]` be the finite induced unit-distance graph whose vertices are the points of `W` and whose edges are the pairs at distance exactly `1`.

The finite certificate is:

```text
cert_k(W) =
  coordinates for the vertices of W,
  an edge list E_W verified against the declared distance relation,
  a proof that G[W] is not k-colorable.
```

For the flagship, the last component may be a checkable SAT UNSAT certificate for the `k`-coloring formula, or a direct finite combinatorial proof. The coordinate/edge part is part of the certificate: a graph that is non-`k`-colorable but not actually realized as a unit-distance subgraph of the plane is not a Hadwiger-Nelson witness.

Radiation means exactly two things.

1. **Orbit radiation.** If `gamma in Gamma`, then `gamma W` has the same finite graph and the same non-`k`-colorability certificate, because `Gamma` preserves `E`.
2. **Compactness bridge.** In a background theory with the de Bruijn-Erdos graph-coloring compactness principle--available in ZFC, and commonly proved using an ultrafilter/Boolean-prime-ideal form of choice--the chromatic number of an infinite graph is the supremum of the chromatic numbers of its finite subgraphs.

**[H-G12-homogeneity: orbit invariance.]** `Gamma` acts transitively on `X` and preserves the relation `E`.

**[H-G12-finite-witness: checkable finite obstruction.]** There exists a finite `W subset X` with `cert_k(W)` proving `chi(G[W])>k`.

**[H-G12-compactness: purchased compactness bridge.]** The working metatheory includes the de Bruijn-Erdos compactness principle for graph coloring. This is needed for finite witnesses to exhaust global finite chromatic bounds; it is not needed merely to infer a lower bound from a displayed finite subgraph.

**Closest Foundations IV cousin.** F6, No-Needles Stability, proves that no unpriced layer-dissolving needle survives once the declared currency, residual, and transport budgets are satisfied. G12 reverses the polarity: the finite obstruction is not dissolved, priced, or confined. Its permanent survival as a finite subgraph of the carrier is exactly the global lower-bound certificate.

#### 2. Theorem

Assume `[H-G12-finite-witness]`. Then `X` has no proper `k`-coloring.

Proof: if `c:X->{1,...,k}` were a proper coloring of the whole carrier, its restriction `c|_W` would be a proper `k`-coloring of `G[W]`, contradicting `cert_k(W)`. Therefore `chi(X,E)>k`.

Assume also `[H-G12-homogeneity]`. Then every translate/rotate/reflect `gamma W` is an equally valid finite witness with the same certificate transported by `gamma`. This is orbit radiation; it adds location-invariance of the witness, not a stronger lower bound.

Assume also `[H-G12-compactness]`. Then, for finite chromatic bounds, the global chromatic number of `(X,E)` is the supremum of the chromatic numbers of its finite induced subgraphs. This is the de Bruijn-Erdos bridge. It says finite witnesses are not merely sufficient for lower bounds; in the chosen metatheory, they are complete for finite chromatic lower-bound detection.

#### 3. Proof Spine

The finite-witness lower bound is a restriction argument, not a metaphor. A global coloring restricts to every finite subgraph. A finite non-`k`-colorable subgraph therefore forbids a global `k`-coloring.

The compactness bridge has the usual de Bruijn-Erdos proof shape: if every finite subgraph has a `k`-coloring, compactness or an ultrafilter-style choice argument selects compatible finite colorings and yields a global `k`-coloring. This bridge is available in ZFC; without the relevant choice principle, it should be recorded as a purchased set-theoretic commitment rather than silently assumed.

For Hadwiger-Nelson, the graph `(R^2,E)` has an edge between points at Euclidean distance `1`. The current ZFC bracket is

```text
5 <= chi(R^2) <= 7.
```

The lower bound `5` is finite-witness radiation. De Grey's 2018 construction gives a finite unit-distance graph with `1581` vertices that is not 4-colorable, raising the lower bound from `4` to `5`. The Polymath16 search and verification effort then organized reductions of the witness size; Heule produced `553`-vertex non-4-colorable unit-distance graphs by clausal proof minimization, and Parts reported a `509`-vertex, `2442`-edge 5-chromatic unit-distance graph. Accessible current summaries still report `509` as the smallest known size in this line. The upper bound `7` is the classical hexagonal-tiling construction: tile the plane by small regular hexagons of diameter less than `1` and color the hexagons in a repeating seven-color pattern so any two same-colored cells are separated by more than unit distance. The exact value remains open: it is one of `5,6,7`.

The choice-sensitivity warning must be stated carefully. Shelah and Soifer show that chromatic-number questions for the plane and related distance graphs can be sensitive to set-theoretic axioms; the Hadwiger-Nelson exact value is therefore not to be treated as a purely finite certificate unless a finite witness or a specified metatheory supplies the relevant bridge. The de Grey lower bound itself is finite and does not depend on this subtlety once the finite graph and non-4-colorability certificate are accepted.

#### 4. Case Enumeration

The table classifies one submitted G12 claim: carrier, relation, group action, target bound `k`, and witness data.

| Case | Status | Witness type |
|---|---|---|
| (a) Radiating witness | A valid `cert_k(W)` exists; with `[H-G12-homogeneity]`, all `Gamma`-copies are equivalent witnesses; with `[H-G12-compactness]`, finite witnesses exhaust finite global bounds. | Verified coordinates/edge list plus non-`k`-colorability proof; de Grey/Heule/Parts graphs instantiate this for `k=4`. |
| (b) Locally neutralizable | The proposed witness is not actually a witness: its edge list is invalid, its coordinates do not realize the claimed relation, or it admits a `k`-coloring. | A proper local recoloring, coordinate failure, or SAT model for the coloring formula. |
| (c) Choice-sensitive bridge | The claim relies on global compactness, definability, measurability, or exact chromatic-value assertions whose truth depends on the set-theoretic background. | Explicit axiom ledger: ZFC, ZF plus extra principles, measurable coloring restriction, or a Shelah-Soifer-style warning record. |
| (d) Uncertified | No finite witness certificate or valid axiom ledger has been supplied. | Missing coordinates, missing unit-distance verification, missing UNSAT proof, or unresolved metatheory. |

Rows are mutually exclusive by audit priority. First fix the metatheory; if the claim is metatheory-dependent, record (c). In a fixed metatheory, a proposed finite witness either verifies (a), fails locally (b), or remains uncertified (d).

#### 5. Interaction Status

G12 is mainly P1 obstruction content plus P2 constraint/gating. The finite graph is a P1 obstruction to descent of a `k`-coloring from the carrier to all finite unit-distance constraints. The property class of legal colorings is the P2 gate. The P6 role is limited: `cert(W)` is an audit record, not a debt ledger or drive. This mapping is narrower than in G1-G10; forcing more BirdInt roles here would be artificial.

#### 6. Nonclaims

1. G12 does not determine the exact chromatic number of the plane. The current known bracket is `5 <= chi(R^2) <= 7`, and the exact value remains open.
2. The de Bruijn-Erdos compactness bridge is a set-theoretic commitment. Choice-dependence and definability restrictions are real and must be recorded when they affect the claim.
3. Shelah-Soifer-style results are a warning about set-theoretic sensitivity for plane/distance-graph coloring questions; they are not a finite proof of any exact Hadwiger-Nelson value.
4. No novelty is claimed for de Grey's construction, Polymath16/Heule/Parts reductions, the de Bruijn-Erdos theorem, or the hexagonal seven-coloring.
5. The F6 polarity is genuinely inverted: G12 does not dissolve or price the finite obstruction. It uses the obstruction's survival as a positive certificate.

#### Layer Instantiations

1. **Hadwiger-Nelson / chromatic number of the plane - calibration.** Finite unit-distance graphs with chromatic number `5` certify `chi(R^2)>4`; the current bracket is `5,6,7`. Citations: de Grey, "The Chromatic Number of the Plane Is at least 5," *Geombinatorics* 28, 5-18, 2018, arXiv:1804.02385; Heule, "Computing Small Unit-Distance Graphs with Chromatic Number 5," arXiv:1805.12181; Parts, "Graph minimization, focusing on the example of 5-chromatic unit-distance graphs in the plane," arXiv:2010.12665; Polymath16 project materials and Mixon's 2021 closing summary for the reduction/verification stream; de Bruijn and Erdos, "A colour problem for infinite graphs and a problem in the theory of relations," 1951.
2. **Finite CSP hardness gadgets - structural.** A finite gadget can certify a lower bound or hardness transfer for an entire problem family when embedded by a declared reduction; this is structurally analogous to witness radiation, but it needs an explicit reduction map in place of `Gamma`. Citation: Garey, Johnson, and Stockmeyer, "Some simplified NP-complete graph problems," *Theoretical Computer Science* 1, 237-267, 1976.
3. **Rigidity gadgets in discrete geometry - structural.** Finite frameworks can certify rigidity or non-flexibility properties under declared embedding rules; this is a finite-witness pattern only when the framework certificate and ambient action are explicit. Citations: Laman, "On graphs and rigidity of plane skeletal structures," *Journal of Engineering Mathematics* 4, 331-340, 1970; Asimow and Roth, "The rigidity of graphs," *Transactions of the American Mathematical Society* 245, 279-289, 1978.
4. **Finite forbidden-minor witnesses - structural.** In minor-closed graph classes, a finite excluded minor certifies global nonmembership of any graph containing it. This is a finite obstruction-as-certificate pattern, but the carrier is graph containment rather than a homogeneous Euclidean motion group. Citation: Robertson and Seymour, "Graph Minors. XX. Wagner's conjecture," *Journal of Combinatorial Theory, Series B* 92, 325-357, 2004.
5. **Mechanism-design impossibility gadgets - structural.** Finite preference-profile configurations can witness impossibility theorems for whole mechanism classes when the reduction/closure over agent sets is declared. This remains structural here because G12's `Gamma`-orbit and compactness bridge are replaced by social-choice closure assumptions. Citations: Gibbard, "Manipulation of voting schemes," *Econometrica* 41, 587-601, 1973; Satterthwaite, "Strategy-proofness and Arrow's conditions," *Journal of Economic Theory* 10, 187-217, 1975.

### G13 - Thin-Orbit Saturation

**Status:** `schema`. Justification: the abstract implication is not proved here from first principles; the deep saturation inputs are imported instance theorems. The law's Phase-1 content is the typed audit: thin orbit, thick admissible target, expansion certificate, density-one saturation record, and the separate reciprocity-obstruction row.

#### 1. Setup

Let `G` be an algebraic group over `Q`, let `G_Z` be a declared arithmetic lattice such as `G(Z)`, and let `Lambda < G_Z` act on a discrete carrier `Y`. Fix a base point `x_0 in Y` and define the orbit

```text
O = Lambda . x_0.
```

The observable is a projection

```text
pi: O -> Z
```

and the target is a set `A subset Z_{\ge 0}`. For this law, "thick" means a positive-density target in the ordinary counting sense:

```text
d(A) = lim_{N->infinity} #(A cap [1,N]) / N > 0
```

when the limit exists, or else a declared positive lower density. For congruence targets, `A` is a finite union of residue classes modulo some `Q_0`, so `d(A)=|R|/Q_0`.

The orbit is "thin" only in the technical arithmetic sense:

```text
Lambda is thin in G_Z iff Lambda is Zariski dense in its
Zariski closure arithmetic lattice and [G_Z : Lambda] = infinity.
```

Equivalently, in the Apollonian instance used below, the orientation-preserving Apollonian group is Zariski dense in the real orthogonal group of the Descartes form but has infinite index in the corresponding integral arithmetic group.

An expansion certificate is a uniform spectral gap for congruence quotients. Concretely, fix a finite symmetric generating set `S` for `Lambda` and congruence kernels `Lambda(q)`. The certificate is a number `epsilon>0` such that the normalized adjacency operators of the Cayley or Schreier graphs

```text
Cay(Lambda/Lambda(q), S_q)
```

have second eigenvalue at most `1-epsilon` for every admissible modulus `q`; equivalently, the graph Laplacians have first nonzero eigenvalue at least `epsilon`. This is the expansion data that supports effective equidistribution in congruence quotients.

**[H-G13-thin: technical thinness.]** `Lambda` is Zariski dense in the relevant algebraic group and has infinite index in the declared arithmetic lattice.

**[H-G13-expansion: spectral gap.]** The congruence quotient family for `Lambda` has a uniform spectral gap with respect to the declared generators.

**[H-G13-congruence-audit: local admissibility.]** `A` is the finite union of residue classes modulo a declared modulus `Q_0` that pass all declared local congruence obstructions. This is explicitly only a local audit.

**[H-G13-imported-saturation: instance theorem.]** For the declared orbit and observable, an imported theorem proves an exceptional-set bound of the form

```text
#((A \ pi(O)) cap [1,N]) = O(N^{1-eta})
```

for some `eta>0`, or else a stronger finite-exception/full-saturation bound.

**[H-G13-reciprocity-record: noncongruence obstruction.]** A declared infinite family `R_rec subset A` is proved to be missed by `pi(O)` by a reciprocity argument not expressible as exclusion from the finite congruence audit `A`.

**Closest Foundations IV cousin.** F4, Local-Global Obstruction Normal Form, fixes one declared restriction map and one local-family datum, then asks whether that datum lies in the image. G13 is not a one-object local-global test: it is an asymptotic orbit-coverage claim over an unbounded target family. Its sibling relationship to G4 is real but different in mechanism: G4 covers by target-dependent certificates; G13 covers by orbit growth plus expansion. F49 is weaker as a cousin: it tests a fixed common-source/interface/direct-route factorization of readouts, not asymptotic density in a projected orbit.

#### 2. Theorem

This is a schema with imported mathematical payload.

Assume `[H-G13-thin]`, `[H-G13-expansion]`, `[H-G13-congruence-audit]`, and `[H-G13-imported-saturation]`. Then the projected orbit saturates the thick admissible target up to the declared exceptional-set bound:

```text
#((A \ pi(O)) cap [1,N]) = O(N^{1-eta})
```

for the `eta>0` supplied by the imported theorem. In particular, the relative density of missed admissible targets is zero:

```text
#((A \ pi(O)) cap [1,N]) / #(A cap [1,N]) -> 0.
```

If the imported theorem supplies a finite-exception bound, the instance is fully saturated beyond a finite threshold. If it supplies only positive density, density one is not licensed.

If `[H-G13-reciprocity-record]` is also discharged with an infinite `R_rec`, then the original finite-congruence local-global claim is false for that instance: `R_rec subset A` passes the congruence audit but is missed by the thin orbit for a reciprocity reason. This does not contradict density-one saturation when `R_rec` has density zero; it refines the residual taxonomy.

For Apollonian circle packings, the density-one input is Bourgain-Kontorovich: for a fixed primitive integral Apollonian gasket, almost every admissible integer is a curvature, with exceptions up to `N` bounded by `O(N^{1-eta})` for effectively computable `eta>0`. The 2024 Annals paper of Haag, Kertzer, Rickards, and Stange supplies the reciprocity record for many packings: certain quadratic and quartic families are missed even though they pass the mod-24 local audit.

#### 3. Proof Spine

The schema proof is not reproduced. Its shape is: expansion gives effective equidistribution of the thin orbit on congruence quotients; the congruence audit identifies a positive-density target `A`; a sieve/circle-method argument converts equidistribution and counting into an exceptional-set bound for missed admissible targets.

The Apollonian flagship uses Descartes' circle theorem. For a Descartes quadruple of oriented curvatures `(k1,k2,k3,k4)`,

```text
k1^2 + k2^2 + k3^2 + k4^2 = (1/2)(k1+k2+k3+k4)^2.
```

Equivalently, `2 sum_i k_i^2 - (sum_i k_i)^2 = 0`, the Descartes quadratic form of signature `(3,1)`. Replacing one curvature by the other root of this quadratic gives the four Apollonian reflections; these generate the Apollonian group orbit of an integral root quadruple.

For the standard primitive packing with root quadruple `(-1,2,2,3)`, applying the four Descartes reflections modulo `24` gives the admissible curvature classes

```text
2, 3, 6, 11, 14, 15, 18, 23  (mod 24).
```

Thus the local target has density `8/24 = 1/3`. In other primitive integral packings the admissible set consists of six or eight classes modulo `24`, determined by the root quadruple and the congruence image.

Bourgain-Fuchs proved positive density for the set of curvatures in integer Apollonian packings. Bourgain-Kontorovich strengthened the local-global direction to density one: almost every admissible integer is hit, with `O(N^{1-eta})` missed admissible integers up to `N`. Their proof uses the Apollonian group as a thin group and uses spectral-gap input over congruence towers, including Varju's appendix in the Bourgain-Kontorovich paper.

Haag, Kertzer, Rickards, and Stange later showed that the full local-global conjecture is false for many primitive integral Apollonian packings. The missed families are quadratic and quartic, arise from quadratic and quartic reciprocity, and are obstructions of the thin Apollonian group rather than of its Zariski closure. That is the G13 distinction: congruence admissibility is a local audit; reciprocity is a separate residual type, not a disguised congruence failure.

#### 4. Case Enumeration

The audit has two levels. The system-level table classifies the whole projected orbit against its declared thick target.

| Case | Status | Witness type |
|---|---|---|
| (a) Saturated | `A \ pi(O)` is finite, or empty beyond a declared threshold. | A finite-exception/full-saturation theorem for the instance. |
| (b) Density-one with exceptional set | `#((A \ pi(O)) cap [1,N]) = O(N^{1-eta})`, but a finite-exception theorem is not available or is false. | Bourgain-Kontorovich for Apollonian gaskets; compatible with infinite zero-density residual families. |
| (c) Positive-density only | The orbit is known to hit a positive-density subset of the target, but density-one saturation is not certified. | Bourgain-Fuchs style positive-density result without the stronger local-global theorem. |
| (d) Undetermined | The thinness, expansion, congruence audit, or imported saturation theorem is missing. | Open obligation; no G13 saturation claim. |

The target-level obstruction table classifies a specific integer or declared infinite target family after the local audit is fixed.

| Case | Status | Witness type |
|---|---|---|
| (i) Congruence-obstructed | The target is not in `A`; it fails the finite residue-class audit. | A residue modulo `Q_0` outside the admissible class list. |
| (ii) Hit | The target lies in `pi(O)`. | An explicit orbit element mapping to the target. |
| (iii) Reciprocity-obstructed | The target or family lies in `A` but is proved missed by quadratic/quartic reciprocity. | Haag-Kertzer-Rickards-Stange type family. |
| (iv) Other exceptional / uncertified | The target lies in `A`, is not certified hit, and has no assigned reciprocity obstruction. | Finite computation gap, density-one exceptional set without pointwise classification, or open target. |

These tables avoid the earlier axis-mixing failure. Congruence-obstructed and reciprocity-obstructed are disjoint by definition: a reciprocity obstruction is recorded only after the target has passed the congruence audit. A density-one system-level theorem can coexist with infinitely many reciprocity-obstructed targets if that exceptional family has zero density.

#### 5. Interaction Status

G13 is primarily P2 gating plus P6 audit content. The congruence classes define the P2 admissibility gate; the expansion and exceptional-set bounds are P6 ledger data measuring how much admissible target mass remains uncovered. P1 enters only through explicit obstruction records, especially reciprocity-obstructed families. The BirdInt fit should remain this narrow: treating spectral gap as a "drive" or as a generic closure force would overread the mathematics.

#### 6. Nonclaims

1. G13 does not prove the Bourgain-Fuchs, Bourgain-Kontorovich, or Haag-Kertzer-Rickards-Stange theorems. They are imported recognition sources.
2. The status ceiling is `schema`. Deep solved instances calibrate the shape, but the general thin-orbit-saturation implication is not proved in this catalog entry.
3. "Thin" never means vaguely sparse; it means infinite index in the relevant arithmetic lattice while remaining Zariski dense in the algebraic group.
4. "Thick" never means visually large; it means positive counting density, usually a finite union of congruence classes.
5. Congruence admissibility is local and incomplete. The 2024 reciprocity obstruction shows that passing all mod-24 tests need not imply eventual representation.
6. No novelty is claimed for Apollonian packings, Zaremba-type results, expansion/spectral-gap theory, or the reciprocity obstruction theorem.

#### Layer Instantiations

1. **Apollonian circle packings / thin groups - calibration, imported.** Primitive integral Apollonian curvature sets instantiate the full G13 audit: thin Apollonian group, mod-24 admissibility, spectral-gap input, Bourgain-Kontorovich density-one saturation, and Haag-Kertzer-Rickards-Stange reciprocity residuals. Citations: Bourgain and Fuchs, "A proof of the positive density conjecture for integer Apollonian circle packings," arXiv:1001.3894; Bourgain and Kontorovich, "On the Local-Global Conjecture for integral Apollonian gaskets," *Inventiones Mathematicae* 196, 589-650, 2014; Haag, Kertzer, Rickards, and Stange, "The local-global conjecture for Apollonian circle packings is false," *Annals of Mathematics* 200(2), 749-770, 2024.
2. **Zaremba's conjecture / continued-fraction orbits - calibration, imported.** Bourgain-Kontorovich technology gives density-one results for denominators represented by bounded partial quotients, a parallel thin-orbit saturation pattern. Citation: Bourgain and Kontorovich, "On Zaremba's conjecture," *Annals of Mathematics* 180, 137-196, 2014.
3. **Affine sieve in thin orbits - structural/calibration.** Almost-prime Pythagorean triples in thin orbits use the same expansion-and-sieve architecture, but the target is almost-primality rather than density-one coverage of all admissible integers. Citation: Kontorovich and Oh, "Almost prime Pythagorean triples in thin orbits," *Journal fur die reine und angewandte Mathematik* 667, 89-131, 2012.
4. **Expander-based derandomized coverage - structural.** Sparse generator walks can cover test spaces with guarantees supplied by spectral gap; this matches the expansion-certificate part of G13 but not the arithmetic reciprocity audit. Citation: Hoory, Linial, and Wigderson, "Expander graphs and their applications," *Bulletin of the American Mathematical Society* 43, 439-561, 2006.
5. **Quasicrystal/model-set diffraction supports - structural, unverified for G13.** Model sets can be sparse, highly structured generators with dense or rich observable spectra, but no thin arithmetic group or G13-style congruence/reciprocity audit is asserted here. Citation for the structural background: Baake and Grimm, *Aperiodic Order. Volume 1: A Mathematical Invitation*, Cambridge University Press, 2013.
