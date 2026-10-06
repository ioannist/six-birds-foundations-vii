# Minimal Foundations VII object model

| ID | Object | Status | Signature | Defined from |
| --- | --- | --- | --- | --- |
| VII-O01 | TheoryPackage | INHERITED | T=(Z,f,Σ_f,E,A) with declared variants and audits |  |
| VII-O02 | InterfaceLens | INHERITED | Typed quotient/readout/instrument interface over a theory package | VII-O01 |
| VII-O03 | AuditRecord | INHERITED | Append-only provenance, replay, check, grade, and nonclaim record | VII-O01 |
| VII-O04 | DomainState | NEW_CANDIDATE | (Expr,Present,Exposed,Recoverable,Admissible,Reachable,Occurrent) at scope/time | VII-O01, VII-O02 |
| VII-O05 | AdmissionTransition | NEW_CANDIDATE | Typed source/guard/cost/effect/audit transition between domain states | VII-O04, VII-O03 |
| VII-O06 | ProspectiveCommitment | NEW_CANDIDATE | Timestamped preregistered finite-budget future admission condition | VII-O05 |
| VII-O07 | SourceLedger | NEW_CANDIDATE | Native/bridged/external/endogenous source and ancestry ledger | VII-O03 |
| VII-O08 | BudgetLedger | NEW_CANDIDATE | Typed resource, occupancy, cross-cost, residual, and refund ledger | VII-O03 |
| VII-O09 | ContactSurface | NEW_CANDIDATE | Pair of owned interfaces plus admissible crossing relation | VII-O02 |
| VII-O10 | ContactWitness | NEW_CANDIDATE | Source-typed event showing that a record crossed a contact surface | VII-O09, VII-O03, VII-O07 |
| VII-O11 | InteractionRecord | NEW_CANDIDATE | Parents, contact, transitions, ledgers, status, and audit | VII-O10, VII-O08 |
| VII-O12 | JoinCandidate | NEW_CANDIDATE | Interaction record plus candidate composite and comparison baseline | VII-O11 |
| VII-O13 | JoinCertificate | NEW_CANDIDATE | Objecthood, retention, source, budget, and strictness witnesses | VII-O12 |
| VII-O14 | JoinObstruction | NEW_CANDIDATE | Typed source/compatibility/gluing/retention/novelty/budget/time failure witness | VII-O12 |
| VII-O15 | NonInteractionCertificate | NEW_CANDIDATE | Coverage- and power-qualified negative interaction record | VII-O11, VII-O14 |
| VII-O16 | EnablementRecord | NEW_CANDIDATE | Enabled operation, source, execution, target effect, budget, and attribution | VII-O05, VII-O07, VII-O08 |
| VII-O17 | ReachabilityWitness | NEW_CANDIDATE | Finite executable path with guards, resources, and state trace | VII-O04, VII-O05 |
| VII-O18 | ObserverOccupancyRecord | NEW_CANDIDATE | Observer/instrument source, visibility, capacity occupancy, and cost | VII-O07, VII-O08 |
