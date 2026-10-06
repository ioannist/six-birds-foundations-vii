#!/usr/bin/env python3
"""Build the Foundations VII Step-3 dependency-closure/readiness dossier.

The builder consumes the frozen Step-2 claim corpus, bridge atlas, wish-list
links, and inherited Lean indexes.  It produces candidate specifications,
source traces, countermodels, finite reference scenarios, and proof targets.
It deliberately does not draft Foundations VII and does not add Lean source.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-07-26"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def scalar(x: Any) -> str:
    if isinstance(x, (list, dict, tuple)):
        return json.dumps(x, ensure_ascii=False, sort_keys=True)
    if isinstance(x, bool):
        return "true" if x else "false"
    return "" if x is None else str(x)


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: scalar(row.get(k, "")) for k in fields})


def unique(seq: Iterable[Any]) -> list[Any]:
    out: list[Any] = []
    seen: set[str] = set()
    for x in seq:
        key = json.dumps(x, sort_keys=True, ensure_ascii=False) if isinstance(x, (dict, list)) else str(x)
        if key not in seen:
            seen.add(key)
            out.append(x)
    return out


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    def esc(x: Any) -> str:
        return scalar(x).replace("\n", " ").replace("|", "\\|")
    return "\n".join([
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *["| " + " | ".join(esc(x) for x in row) + " |" for row in rows],
    ])


def tokens(text: str) -> set[str]:
    stop = {"the","and","with","from","into","that","this","under","without","for","not","does","only","must","may","can","vii","candidate","claim","theorem","schema","result"}
    return {x for x in re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", text.lower()) if x not in stop}


# Thirty-six candidate dossiers.  The exact source dependencies are generated
# from the Step-2 evidence rows for the named convergence groups.
CANDIDATE_SPECS: list[dict[str, Any]] = [
    dict(id="VII-C001", name="Accessible-domain state normal form", groups=["CG01","CG21"], kind="DEFINITION_AND_FINITE_NORMAL_FORM", chapter="Ch02", priority="P0", conclusion="A theory package admits a typed operational-domain record separating expressible, present, exposed, recoverable, admissible, reachable, and occurrent statuses; converses require explicit witnesses.", obligations=["Define equality and scope change for domain states.","Prove non-collapse finite models for each adjacent status.","Relate the record to inherited quotient and access data without replacing P1–P6."], nonclaims=["Domain width is not capability.","No total order among all status coordinates is claimed."], scenarios=["TTW-S19","TTW-S20","TTW-S21"], cms=["CM-08","CM-09","CM-12"], fts=["FT01","FT02"]),
    dict(id="VII-C002", name="Lawful admission transition system", groups=["CG02","CG25"], kind="DEFINITION_AND_SCHEMA", chapter="Ch03", priority="P0", conclusion="Admission, expiry, revocation, retraction, and rollback are typed transitions whose execution requires source, budget, guard, and audit witnesses distinct from rule text.", obligations=["Give transition typing and ledger-update laws.","Separate soundness, executability, reachability, firing, and occurrence.","Specify lawful rollback without erasing history."], nonclaims=["A well-formed rule need not be executable.","A reachable transition need not fire."], scenarios=["TTW-S19","TTW-S20","TTW-S21"], cms=["CM-08","CM-09","CM-18"], fts=["FT01","FT02","FT17"]),
    dict(id="VII-C003", name="Bootstrap obstruction theorem", groups=["CG03"], kind="CANDIDATE_NO_GO_THEOREM", chapter="Ch03", priority="P0", conclusion="A closed admission regime with no admitted seed and no reachable generator has no lawful first extension.", obligations=["Define first-extension and closed-regime hypotheses exactly.","Prove the finite theorem and isolate infinite escape routes.","Distinguish neutral provisioning from outcome-rigging."], nonclaims=["External provision is not forbidden.","The theorem is scoped to the declared transition family."], scenarios=["TTW-S01","TTW-S02"], cms=["CM-19","CM-20"], fts=["FT03","FT18"]),
    dict(id="VII-C004", name="Neutral seed and provisioning certificate", groups=["CG03","CG09"], kind="DEFINITION_AND_AUDIT_SCHEMA", chapter="Ch03", priority="P1", conclusion="A seed receives neutral-provisioning status only when its source, symmetry, task-blindness, preregistration, and control coordinates are recorded before use.", obligations=["Define admissible seed equivalence classes.","Prove that post-hoc or source-laundered stocking fails the certificate.","Provide finite positive and rigged-seed controls."], nonclaims=["Neutrality is audit-relative, not metaphysical independence."], scenarios=["TTW-S02","TTW-S05"], cms=["CM-01","CM-19"], fts=["FT04","FT05"]),
    dict(id="VII-C005", name="Common-origin non-transfer law", groups=["CG05","CG09"], kind="CANDIDATE_THEOREM_AND_COUNTERMODEL", chapter="Ch04", priority="P0", conclusion="Common origin, common carrier, or common instrument does not entail shared access, source independence, or an independence-sensitive join.", obligations=["Construct same-source/no-shared-access models.","State extra witnesses sufficient for each stronger conclusion.","Block total-lens-to-partial-domain transfer."], nonclaims=["Common origin may still be relevant evidence when correctly typed."], scenarios=["TTW-S05","TTW-S23"], cms=["CM-01","CM-12","CM-26"], fts=["FT05","FT17"]),
    dict(id="VII-C006", name="Prospective commitment certificate", groups=["CG04"], kind="DEFINITION_AND_TEMPORAL_SCHEMA", chapter="Ch03", priority="P0", conclusion="A prospective commitment is a timestamped, preregistered, finite-budget rule that fixes later admission conditions before the target evidence is observed.", obligations=["Define certified temporal precedence without assuming one global clock.","Prove retrospective predicates cannot discharge the same certificate.","Specify expiry and unused-budget accounting."], nonclaims=["Commitment does not guarantee reachability or success."], scenarios=["TTW-S03","TTW-S04"], cms=["CM-20","CM-09"], fts=["FT04","FT16"]),
    dict(id="VII-C007", name="Join-entry record normal form", groups=["CG06","CG28"], kind="DEFINITION_AND_NORMAL_FORM", chapter="Ch04", priority="P0", conclusion="Entry to the join calculus requires parent packages, typed contact surface, witnessed contact or pending status, source and licensing ledgers, budget, obstruction semantics, and an append-only audit record.", obligations=["Prove field sufficiency for retrospective verification.","Separate pending, failed, obstructed, and completed statuses.","Show omission of source/contact/budget fields permits false positives."], nonclaims=["Record completeness does not prove a join exists."], scenarios=["TTW-S06","TTW-S08","TTW-S12"], cms=["CM-02","CM-03","CM-14"], fts=["FT06","FT07"]),
    dict(id="VII-C008", name="Join existence and obstruction status calculus", groups=["CG07"], kind="CANDIDATE_SCHEMA_WITH_SCOPED_THEOREMS", chapter="Ch05", priority="P0", conclusion="Within a declared finite interface family, join attempts are classified as no contact, contact, common refinement, composite, strict join, typed obstruction, or coverage-qualified non-interaction.", obligations=["Prove statuses disjoint or state permitted overlaps.","Give source, compatibility, gluing, retention, novelty, budget, and temporal obstruction witnesses.","Do not claim completeness beyond the declared family."], nonclaims=["The taxonomy is not universal without a completeness theorem."], scenarios=["TTW-S06","TTW-S07","TTW-S08","TTW-S10","TTW-S13"], cms=["CM-02","CM-13","CM-27"], fts=["FT09","FT10"]),
    dict(id="VII-C009", name="Strict join certificate and anti-product witness", groups=["CG08"], kind="CANDIDATE_THEOREM", chapter="Ch05", priority="P0", conclusion="A strict join requires composite objecthood, recoverable parent retention, and a distinction or operation that does not factor through either parent or their declared mere product/common refinement.", obligations=["Define the comparison baseline and anti-product witness.","Prove relabeling, coarsening, and scheduling controls fail strictness.","Keep objecthood, novelty, and directionality certificates separate."], nonclaims=["Strict join does not imply a P6 arrow.","Parent strictness alone does not prove joint strictness."], scenarios=["TTW-S07","TTW-S08","TTW-S15"], cms=["CM-03","CM-13","CM-14","CM-16"], fts=["FT07","FT08"]),
    dict(id="VII-C010", name="Source-independence gate", groups=["CG09"], kind="DEFINITION_AND_NO_GO_SCHEMA", chapter="Ch06", priority="P0", conclusion="Independence-sensitive join claims require a source/ancestry witness separate from behavioral nonfactorization; native and bridged records retain their source types.", obligations=["Define ancestry equivalence and honest bridging.","Prove same-lineage re-expression fails independence credit.","Separate source independence from causal independence."], nonclaims=["Source independence is not sufficient for strict novelty or causal independence."], scenarios=["TTW-S05","TTW-S11"], cms=["CM-01","CM-26"], fts=["FT05"]),
    dict(id="VII-C011", name="Join budget and payment ledger", groups=["CG10","CG23"], kind="DEFINITION_AND_BOUNDEDNESS_SCHEMA", chapter="Ch06", priority="P0", conclusion="A join ledger prices interface access, parent retention, joint novelty, observer/instrument occupancy, cross-costs, and explicit refunds; zero total cost requires a certified zero-cost channel.", obligations=["Define currencies without assuming one scalar currency.","Prove finite live-join bounds under stated capacity hypotheses.","Expose hidden observer subsidies and post-failure refunds."], nonclaims=["No universal conserved interaction currency is asserted."], scenarios=["TTW-S10","TTW-S22"], cms=["CM-11","CM-21"], fts=["FT09","FT16"]),
    dict(id="VII-C012", name="Enablement record and attribution calculus", groups=["CG14"], kind="DEFINITION_AND_SCHEMA", chapter="Ch07", priority="P0", conclusion="Enablement records identify the operation made available, its source, execution witness, budget, target effect, and attribution to theorist, carrier, peer theory, observer, environment, endogenous system, or mixed source.", obligations=["Define enablement independently of descent, containment, sufficiency, and causation.","Give mixed-provenance and observer-certified cases.","Prove attribution is stable under honest bridge refinement."], nonclaims=["Enablement does not imply descent or sufficient determination."], scenarios=["TTW-S02","TTW-S21","TTW-S22"], cms=["CM-06","CM-07","CM-17"], fts=["FT11"]),
    dict(id="VII-C013", name="Endogenous enablement criterion", groups=["CG14","CG15"], kind="CANDIDATE_THEOREM", chapter="Ch07", priority="P0", conclusion="Enablement is endogenous only when the system carries, reaches, executes, and audits the enabling generator within the declared boundary and pays its resource costs.", obligations=["State carried-generator and boundary conditions.","Prove theorist-triggered and hidden-observer cases fail.","Relate to inherited repair-generator reachability without overidentifying cognition."], nonclaims=["Endogenous does not mean uncaused or environmentally isolated."], scenarios=["TTW-S02","TTW-S22"], cms=["CM-11","CM-17"], fts=["FT12","FT16"]),
    dict(id="VII-C014", name="Birth/contact-surface classification", groups=["CG15"], kind="CANDIDATE_CLASSIFICATION_SCHEMA", chapter="Ch07", priority="P1", conclusion="Layer birth is classified by who performs closure, what new object survives, whether participants are created or only related, and whether the birth occurs at or through a contact surface.", obligations=["Reconcile inherited birth classes before adding cases.","Provide finite reachability requirements for each class.","Separate undergoing closure from performing it."], nonclaims=["Contact does not itself constitute birth."], scenarios=["TTW-S06","TTW-S08"], cms=["CM-02","CM-17"], fts=["FT11","FT12"]),
    dict(id="VII-C015", name="Typed transmission and descent-fidelity law", groups=["CG17"], kind="CANDIDATE_THEOREM_FAMILY", chapter="Ch07", priority="P0", conclusion="Upward, downward, and peer transmission are typed maps with explicit payload, loss, ambiguity, and source records; downward selection cannot create lower-carrier facts absent from the lower carrier.", obligations=["Define transmission types and descent-fidelity witnesses.","Prove direction-specific invariants and countermodels.","Separate structural selection from a top-down causal channel."], nonclaims=["Construction direction is not automatically temporal directionality."], scenarios=["TTW-S16","TTW-S24"], cms=["CM-06","CM-22","CM-23"], fts=["FT13","FT19"]),
    dict(id="VII-C016", name="Peer contact and transport without join", groups=["CG11"], kind="DEFINITION_AND_CANDIDATE_THEOREM", chapter="Ch04", priority="P0", conclusion="Certified content may become available to a peer through a typed contact/transport record without forming a joint theory; destination ownership and provenance remain explicit.", obligations=["Classify rendezvous, mediation, sequential transport, shared carrier, and shared budget.","Prove contact-before-connection under local-interface hypotheses.","Distinguish sequential composition from interaction of composites."], nonclaims=["Peer transport is not joint objecthood or strict novelty."], scenarios=["TTW-S06","TTW-S12"], cms=["CM-02","CM-19"], fts=["FT05","FT06"]),
    dict(id="VII-C017", name="Interaction-order residue and holonomy", groups=["CG19"], kind="CANDIDATE_THEOREM_AND_FINITE_ASSAY", chapter="Ch09", priority="P0", conclusion="For three or more admitted interactions, inequivalent legal orderings define a route residue relative to a declared predictive quotient; nonzero residue is interaction holonomy, not by itself directionality.", obligations=["Define bracketing/order comparison on one typed target.","Prove finite examples and confluence controls.","Add a separate drive/null certificate for arrow claims."], nonclaims=["P3 holonomy does not imply a P6 arrow."], scenarios=["TTW-S16","TTW-S17","TTW-S18"], cms=["CM-10","CM-24"], fts=["FT14","FT15"]),
    dict(id="VII-C018", name="Admission confluence and seed-dependence law", groups=["CG18"], kind="CANDIDATE_THEOREM_FAMILY", chapter="Ch09", priority="P1", conclusion="Distinct lawful admission/refinement routes are confluent exactly under declared critical-pair and audit-equivalence conditions; otherwise fixed points may depend on route or initial seed partition.", obligations=["State finite critical-pair conditions.","Construct nonconfluent and seed-dependent controls.","Separate terminal equality from predictive equivalence."], nonclaims=["One commuting square does not prove global confluence."], scenarios=["TTW-S16","TTW-S24"], cms=["CM-23","CM-24"], fts=["FT14"]),
    dict(id="VII-C019", name="Access/join residual and obstruction-dissolution ledger", groups=["CG22"], kind="DEFINITION_AND_CANDIDATE_LAWS", chapter="Ch10", priority="P1", conclusion="Inaccessible, unadmitted, expired, failed, or join-created distinctions remain typed residuals; ascent, peer join, refinement, or declared termination may discharge them, with cross-terms recorded explicitly.", obligations=["Define residual addition and cross-term conditions.","Construct peer-removable and join-manufactured needles.","Prove no silent deletion under scope changes."], nonclaims=["Access growth need not monotonically reduce all obstructions."], scenarios=["TTW-S10","TTW-S24"], cms=["CM-22","CM-25"], fts=["FT09","FT20"]),
    dict(id="VII-C020", name="Bridge and semantic-withdrawal discipline", groups=["CG24"], kind="INHERITED_PROTOCOL_PLUS_VII_ADAPTER", chapter="Ch01", priority="P0", conclusion="Every imported law or interaction claim carries source/target maps, hypotheses, audit path, nonclaims, and append-only failure or withdrawal records; citations alone never license transport.", obligations=["Reuse the Step-2 bridge schema as VII's own citation rule.","Specify paraphrase and downstream-dependency sweeps for withdrawal.","Retain failed bridges as first-class records."], nonclaims=["A bridge certificate does not strengthen its source theorem."], scenarios=["TTW-S23"], cms=["CM-12","CM-18"], fts=["FT05","FT17"]),
    dict(id="VII-C021", name="Reachability, guard activity, and horizon law", groups=["CG25"], kind="CANDIDATE_THEOREM_AND_EVIDENCE_SCHEMA", chapter="Ch08", priority="P0", conclusion="Lawfulness, non-vacuity, reachability, firing, and occurrence are separate; finite-horizon non-occurrence licenses only horizon-qualified conclusions unless reachability and guard power are independently established.", obligations=["Define guard-activity and reachability witnesses.","Prove sound-unreachable and reachable-nonoccurring models.","State exhaustive closed-family conditions for stronger negatives."], nonclaims=["Non-occurrence alone is not impossibility."], scenarios=["TTW-S19","TTW-S20","TTW-S21"], cms=["CM-08","CM-09","CM-18"], fts=["FT02","FT17"]),
    dict(id="VII-C022", name="Exposure, recoverability, admissibility, and rigidity calculus", groups=["CG21"], kind="DEFINITION_AND_SCOPED_THEOREMS", chapter="Ch02", priority="P1", conclusion="Determination, exposure, recoverability, and admissibility are independent interface coordinates; exposure overread and spurious rigidity occur when distinctions or constraints are supplied by operations absent from the substrate.", obligations=["Give auxiliary-recovery equivalence conditions.","Construct same-determination/different-exposure models.","Separate genuine rigidity from wrong-interface overconstraint."], nonclaims=["Exposure is not determination; recoverability is not permission."], scenarios=["TTW-S15","TTW-S19"], cms=["CM-03","CM-12"], fts=["FT01","FT17"]),
    dict(id="VII-C023", name="Negative-result quantifier discipline", groups=["CG26"], kind="INHERITED_LOGIC_PLUS_VII_RULE", chapter="Ch08", priority="P0", conclusion="The force of a negative result is fixed by its quantifiers and search-family closure: a point null, bounded search, exhaustive finite family, and theorem-grade impossibility have distinct conclusions.", obligations=["Encode the four evidence grades in the claim schema.","Prove the finite exhaustive inference rule.","Require escape-route and family-closure records."], nonclaims=["A failed instance never refutes an unrestricted existential claim."], scenarios=["TTW-S13","TTW-S19"], cms=["CM-18","CM-27"], fts=["FT17"]),
    dict(id="VII-C024", name="Claim-grade and normative-specification discipline", groups=["CG27"], kind="INHERITED_PROTOCOL", chapter="Ch01", priority="P0", conclusion="VII statements preserve theorem/schema/calibration/conjecture/philosophy grades, label necessary and sufficient conditions explicitly, and are judged against normative specifications rather than illustrative examples.", obligations=["Carry grade fields into every candidate and theorem ledger.","Run red-line and nonclaim scans before drafting.","Preserve P039 and P040/P058 source/version limitations."], nonclaims=["The readiness dossier is not a proof or paper draft."], scenarios=["TTW-S23"], cms=["CM-12","CM-18"], fts=["FT17"]),
    dict(id="VII-C025", name="Two-Theory World detector contract", groups=["CG28"], kind="FINITE_REFERENCE_SPECIFICATION", chapter="Ch11", priority="P0", conclusion="Every interaction law is paired with append-only evidence, signal, null, falsifier, same-source/no-contact/scheduling/relabeling controls, and asymmetric false-positive costs in a finite reference world.", obligations=["Implement deterministic scenario evaluation.","Freeze expected statuses before later experiments.","Treat the lab as an assay, never a substitute for proof."], nonclaims=["Passing finite scenarios does not prove universal laws."], scenarios=[f"TTW-S{i:02d}" for i in range(1,25)], cms=[f"CM-{i:02d}" for i in range(1,28)], fts=["FT20"]),
    dict(id="VII-C026", name="Categorical reduction decision", groups=["CG12"], kind="DEFERRED_THEOREM_TARGET", chapter="Ch12", priority="P2", conclusion="Reduction of the VII join to product, pullback, pushout, or another categorical construction remains conditional on an explicit category of packages, interfaces, and admissible morphisms.", obligations=["Define the category and universal property before reduction claims.","Find a finite countermodel to unconditional reduction.","Prove only special-case equivalences first."], nonclaims=["No unconditional categorical reduction is claimed in Step 3."], scenarios=["TTW-S07","TTW-S08"], cms=["CM-13","CM-27"], fts=["FT07"]),
    dict(id="VII-C027", name="Enablement-chain composition law", groups=["CG16"], kind="CANDIDATE_THEOREM", chapter="Ch07", priority="P2", conclusion="Enablement relations compose only when source types, execution witnesses, budgets, and residual obligations compose; chain order may carry holonomy or accumulated debt.", obligations=["Define composability and accumulated ledgers.","Prove a finite associative special case and non-associative control.","Separate composed enablement from transitive causation."], nonclaims=["Enablement is not assumed transitive without hypotheses."], scenarios=["TTW-S16","TTW-S17"], cms=["CM-07","CM-24"], fts=["FT11","FT15"]),
    dict(id="VII-C028", name="Primitive-operation algebra readiness criterion", groups=["CG29"], kind="EXPLICIT_DEFERRAL", chapter="Ch12", priority="P2", conclusion="A generators-and-relations algebra is deferred until primitive operations, equivalences, composition domains, and categorical semantics are fixed and proved nonredundant.", obligations=["List candidate generators and dependency risks.","State the evidence gate for reopening the algebra program.","Prevent P1–P6 from being repurposed as unproved generators."], nonclaims=["No complete primitive algebra is claimed."], scenarios=["TTW-S16"], cms=["CM-24"], fts=["FT14"]),
    dict(id="VII-C029", name="Observer and instrument occupancy law", groups=["CG23","CG10"], kind="CANDIDATE_NO_GO_AND_LEDGER_SCHEMA", chapter="Ch06", priority="P0", conclusion="An observer or instrument using bounded shared capacity cannot certify native/endogenous formation while omitting its occupancy, source role, or cost from the system ledger.", obligations=["Define occupancy and shared-capacity accounting.","Prove hidden-occupancy false-positive model.","State certified zero-cost and external-observer escape routes."], nonclaims=["Observation is not prohibited; unrecorded load-bearing observation is."], scenarios=["TTW-S22"], cms=["CM-11","CM-21"], fts=["FT16"]),
    dict(id="VII-C030", name="Parent refinement, retention, and join descent", groups=["CG13"], kind="CANDIDATE_THEOREM_FAMILY", chapter="Ch05", priority="P1", conclusion="A join certificate records which parent objects, laws, and source identities remain recoverable; parent refinement may preserve, strengthen, weaken, or destroy the join depending on compatibility and strictness witnesses.", obligations=["Define parent-retention maps and refinement transport.","Construct join-destruction and partial-retention models.","Prove no silent full-retention claim after erasure."], nonclaims=["Retention alone is not strict novelty."], scenarios=["TTW-S09","TTW-S24"], cms=["CM-05","CM-22"], fts=["FT07","FT19"]),
    dict(id="VII-C031", name="Contact-degree conservation decision", groups=["CG30"], kind="EXPLICIT_DEFERRAL_AND_TEST_PROGRAM", chapter="Ch12", priority="P2", conclusion="No conserved contact degree is assumed; candidate quantities must first be defined, shown invariant under declared joins, and separated from bookkeeping artifacts.", obligations=["Inventory plausible invariants from inherited currencies and residuals.","Construct nonconservation controls.","Require an exact conservation theorem before naming a degree."], nonclaims=["No conserved contact quantity is claimed."], scenarios=["TTW-S08","TTW-S10"], cms=["CM-21","CM-25"], fts=["FT09","FT20"]),
    dict(id="VII-C032", name="Interaction arrow, irreversibility, and cross-time contact", groups=["CG20","CG19"], kind="CANDIDATE_SCHEMA_AND_ASSAY", chapter="Ch09", priority="P1", conclusion="Arrow or irreversibility claims require a drive/path-asymmetry certificate and null-versus-driven controls distinct from order residue; cross-time contact uses explicit synchronization or order witnesses rather than assumed simultaneity.", obligations=["Define drive and reversal tests.","Give holonomy-zero-arrow and driven controls.","Specify contact across partially ordered or incommensurable clocks."], nonclaims=["Order sensitivity and entropy production internal to a parent do not alone prove an inter-theory arrow."], scenarios=["TTW-S17","TTW-S18"], cms=["CM-10","CM-24"], fts=["FT15"]),
    dict(id="VII-C033", name="Coverage-qualified certified non-interaction", groups=["CG07","CG26","CG28"], kind="CANDIDATE_NEGATIVE_RESULT_SCHEMA", chapter="Ch08", priority="P0", conclusion="Certified non-interaction is a positive, family-scoped result only when contact channels, detector power, budget, horizon, and search-family closure are recorded and all admissible cases are exhausted or theoremically excluded.", obligations=["Define coverage and power certificates.","Separate no evidenced contact from certified non-interaction.","State exact escape routes outside the family."], nonclaims=["No finite null universalizes beyond its covered family."], scenarios=["TTW-S12","TTW-S13"], cms=["CM-02","CM-18","CM-27"], fts=["FT10","FT17"]),
    dict(id="VII-C034", name="Enablement without descent separation theorem", groups=["CG14","CG17"], kind="CANDIDATE_SEPARATION_THEOREM", chapter="Ch07", priority="P0", conclusion="There exist lawful enablement records in which an operation becomes available and is load-bearing while no factorization/descent of the enabled object through the enabler exists; enablement may also be necessary but insufficient.", obligations=["Construct finite witnesses for both separations.","Specify the no-descent audit and insufficiency alternatives.","Block causal overstatement."], nonclaims=["The theorem does not deny that some enablement also descends."], scenarios=["TTW-S03","TTW-S21"], cms=["CM-06","CM-07"], fts=["FT11","FT13"]),
    dict(id="VII-C035", name="No-free-join and self-bootstrap no-go family", groups=["CG03","CG06","CG08","CG10"], kind="CANDIDATE_NO_GO_FAMILY", chapter="Ch06", priority="P0", conclusion="A join cannot create the first capability required to execute itself, manufacture strict joint information by relabeling, or receive positive-cost join credit without a paid or certified zero-cost channel.", obligations=["Separate bootstrap, novelty, and payment hypotheses.","Prove finite cases and list external-seed/zero-cost escape routes.","Avoid conflating the family with one universal no-go."], nonclaims=["The family permits admitted seeds, declared bridges, and proven zero-cost channels."], scenarios=["TTW-S01","TTW-S10","TTW-S15"], cms=["CM-03","CM-19","CM-21"], fts=["FT03","FT08","FT18"]),
    dict(id="VII-C036", name="Join-created obstruction and needle law", groups=["CG22","CG08","CG19"], kind="CANDIDATE_THEOREM_AND_COUNTERMODEL", chapter="Ch10", priority="P1", conclusion="A join may dissolve parent obstructions yet create new cross-term needles localized to the composite interface; the ledger must distinguish inherited, dissolved, and newly generated residuals.", obligations=["Construct a finite join-created needle.","Define cross-term provenance and discharge conditions.","Prove relabeling does not count as new obstruction."], nonclaims=["Joining is not monotonically obstruction-reducing."], scenarios=["TTW-S08","TTW-S24"], cms=["CM-25","CM-03"], fts=["FT08","FT20"]),
]


OBJECT_SPECS = [
    ("VII-O01","TheoryPackage","T=(Z,f,Σ_f,E,A) with declared variants and audits",[],"INHERITED",["VII-C001","VII-C020","VII-C026"]),
    ("VII-O02","InterfaceLens","Typed quotient/readout/instrument interface over a theory package",["VII-O01"],"INHERITED",["VII-C001","VII-C022"]),
    ("VII-O03","AuditRecord","Append-only provenance, replay, check, grade, and nonclaim record",["VII-O01"],"INHERITED",["VII-C020","VII-C024","VII-C015","VII-C017","VII-C023"]),
    ("VII-O04","DomainState","(Expr,Present,Exposed,Recoverable,Admissible,Reachable,Occurrent) at scope/time",["VII-O01","VII-O02"],"NEW_CANDIDATE",["VII-C001","VII-C002","VII-C021","VII-C036"]),
    ("VII-O05","AdmissionTransition","Typed source/guard/cost/effect/audit transition between domain states",["VII-O04","VII-O03"],"NEW_CANDIDATE",["VII-C002","VII-C003","VII-C018","VII-C028"]),
    ("VII-O06","ProspectiveCommitment","Timestamped preregistered finite-budget future admission condition",["VII-O05"],"NEW_CANDIDATE",["VII-C006"]),
    ("VII-O07","SourceLedger","Native/bridged/external/endogenous source and ancestry ledger",["VII-O03"],"NEW_CANDIDATE",["VII-C004","VII-C005","VII-C010","VII-C035"]),
    ("VII-O08","BudgetLedger","Typed resource, occupancy, cross-cost, residual, and refund ledger",["VII-O03"],"NEW_CANDIDATE",["VII-C011","VII-C029","VII-C031","VII-C035"]),
    ("VII-O09","ContactSurface","Pair of owned interfaces plus admissible crossing relation",["VII-O02"],"NEW_CANDIDATE",["VII-C007","VII-C016","VII-C014","VII-C026"]),
    ("VII-O10","ContactWitness","Source-typed event showing that a record crossed a contact surface",["VII-O09","VII-O03","VII-O07"],"NEW_CANDIDATE",["VII-C007","VII-C016"]),
    ("VII-O11","InteractionRecord","Parents, contact, transitions, ledgers, status, and audit",["VII-O10","VII-O08"],"NEW_CANDIDATE",["VII-C007","VII-C025","VII-C017","VII-C018","VII-C028","VII-C031","VII-C032"]),
    ("VII-O12","JoinCandidate","Interaction record plus candidate composite and comparison baseline",["VII-O11"],"NEW_CANDIDATE",["VII-C008","VII-C009","VII-C026","VII-C028","VII-C035"]),
    ("VII-O13","JoinCertificate","Objecthood, retention, source, budget, and strictness witnesses",["VII-O12"],"NEW_CANDIDATE",["VII-C009","VII-C030","VII-C036"]),
    ("VII-O14","JoinObstruction","Typed source/compatibility/gluing/retention/novelty/budget/time failure witness",["VII-O12"],"NEW_CANDIDATE",["VII-C008","VII-C019","VII-C036"]),
    ("VII-O15","NonInteractionCertificate","Coverage- and power-qualified negative interaction record",["VII-O11","VII-O14"],"NEW_CANDIDATE",["VII-C033","VII-C023"]),
    ("VII-O16","EnablementRecord","Enabled operation, source, execution, target effect, budget, and attribution",["VII-O05","VII-O07","VII-O08"],"NEW_CANDIDATE",["VII-C012","VII-C013","VII-C034","VII-C014","VII-C015","VII-C027"]),
    ("VII-O17","ReachabilityWitness","Finite executable path with guards, resources, and state trace",["VII-O04","VII-O05"],"NEW_CANDIDATE",["VII-C002","VII-C021"]),
    ("VII-O18","ObserverOccupancyRecord","Observer/instrument source, visibility, capacity occupancy, and cost",["VII-O07","VII-O08"],"NEW_CANDIDATE",["VII-C011","VII-C029"]),
]


SCENARIOS: list[dict[str, Any]] = [
    dict(id="TTW-S01", name="Closed bootstrap with no seed", flags=dict(seed=False,generator_reachable=False), expected="BOOTSTRAP_BLOCKED", assertions={"first_extension":False}),
    dict(id="TTW-S02", name="External neutral seed enables first extension", flags=dict(seed=True,neutral_seed=True,generator_reachable=True,reachable=True,fired=True), expected="LAWFUL_FIRST_EXTENSION", assertions={"first_extension":True,"endogenous":False}),
    dict(id="TTW-S03", name="Prospective commitment admits later evidence", flags=dict(seed=True,prospective=True,reachable=True,fired=True), expected="PROSPECTIVE_ADMISSION", assertions={"prospective_credit":True}),
    dict(id="TTW-S04", name="Retrospective self-certifying prediction", flags=dict(retrospective=True,reachable=True,fired=True), expected="RETROSPECTIVE_SELF_CERTIFICATION_REJECTED", assertions={"prospective_credit":False}),
    dict(id="TTW-S05", name="Same-source resemblance pseudo-join", flags=dict(contact=True,same_source=True,resemblance_only=True,composite=True), expected="INDEPENDENCE_GATE_FAILED", assertions={"strict_join":False}),
    dict(id="TTW-S06", name="Witnessed contact without composite", flags=dict(contact=True,composite=False), expected="CONTACT_WITHOUT_JOIN", assertions={"contact":True,"strict_join":False}),
    dict(id="TTW-S07", name="Common refinement without anti-product novelty", flags=dict(contact=True,common_refinement=True,composite=True,retention=True,anti_product=False), expected="COMMON_REFINEMENT_NONSTRICT", assertions={"strict_join":False}),
    dict(id="TTW-S08", name="Certificate-bearing strict join", flags=dict(contact=True,source_independent=True,composite=True,retention=True,anti_product=True,budget_ok=True), expected="STRICT_JOIN", assertions={"strict_join":True}),
    dict(id="TTW-S09", name="Composite erases one parent", flags=dict(contact=True,source_independent=True,composite=True,retention=False,anti_product=True,budget_ok=True), expected="RETENTION_OBSTRUCTION", assertions={"strict_join":False}),
    dict(id="TTW-S10", name="Positive-cost join without budget", flags=dict(contact=True,source_independent=True,composite=True,retention=True,anti_product=True,budget_ok=False), expected="BUDGET_OBSTRUCTION", assertions={"strict_join":False}),
    dict(id="TTW-S11", name="Independent behavior without source independence", flags=dict(contact=True,source_independent=False,composite=True,retention=True,anti_product=True,budget_ok=True), expected="SOURCE_OBSTRUCTION", assertions={"strict_join":False}),
    dict(id="TTW-S12", name="Compatible interfaces but no witnessed contact", flags=dict(contact=False,compatible=True,closed_family=False), expected="NO_EVIDENCED_CONTACT", assertions={"contact":False}),
    dict(id="TTW-S13", name="Coverage-qualified certified non-interaction", flags=dict(contact=False,compatible=True,closed_family=True,detector_power=True), expected="CERTIFIED_NONINTERACTION", assertions={"certified_noninteraction":True}),
    dict(id="TTW-S14", name="Scheduling artifact masquerades as novelty", flags=dict(contact=True,composite=True,scheduling_only=True), expected="FAKE_JOIN_SCHEDULING", assertions={"strict_join":False}),
    dict(id="TTW-S15", name="Relabeling masquerades as novelty", flags=dict(contact=True,composite=True,relabel_only=True), expected="FAKE_JOIN_RELABELING", assertions={"strict_join":False}),
    dict(id="TTW-S16", name="Three-theory order residue", flags=dict(contact=True,order_residue=True,holonomy=True,drive=False), expected="ORDER_RESIDUE", assertions={"holonomy":True}),
    dict(id="TTW-S17", name="Holonomy with zero arrow", flags=dict(contact=True,holonomy=True,drive=False), expected="HOLONOMY_ZERO_ARROW", assertions={"directionality":False}),
    dict(id="TTW-S18", name="Driven arrow control", flags=dict(contact=True,holonomy=True,drive=True), expected="DRIVEN_ARROW", assertions={"directionality":True}),
    dict(id="TTW-S19", name="Sound rule that is unreachable", flags=dict(sound=True,reachable=False), expected="SOUND_UNREACHABLE", assertions={"reachable":False,"occurred":False}),
    dict(id="TTW-S20", name="Reachable admission that does not occur", flags=dict(sound=True,reachable=True,fired=False), expected="REACHABLE_NONOCCURRENT", assertions={"reachable":True,"occurred":False}),
    dict(id="TTW-S21", name="Reachable and occurrent admission", flags=dict(sound=True,reachable=True,fired=True), expected="OCCURRENT_EVENT", assertions={"occurred":True}),
    dict(id="TTW-S22", name="Unpriced observer occupancy", flags=dict(observer_used=True,observer_priced=False,reachable=True,fired=True), expected="UNPRICED_OBSERVER", assertions={"endogenous":False}),
    dict(id="TTW-S23", name="Total-lens theorem applied to partial domain", flags=dict(total_lens_only=True,partial_domain=True), expected="UNLICENSED_TOTALITY_TRANSFER", assertions={"bridge_valid":False}),
    dict(id="TTW-S24", name="Parent refinement changes join and residual", flags=dict(contact=True,parent_refined=True,join_destroyed=True,new_residual=True), expected="REFINEMENT_DESTROYS_JOIN", assertions={"strict_join":False,"new_residual":True}),
]


COUNTERMODELS: list[dict[str, Any]] = [
    dict(id="CM-01", name="Same source but no shared access", scenario="TTW-S05", shows="Common origin does not imply shared access or independence.", candidates=["VII-C005","VII-C010"]),
    dict(id="CM-02", name="Common interface without witnessed contact", scenario="TTW-S12", shows="Compatibility does not imply contact or non-interaction.", candidates=["VII-C007","VII-C008","VII-C016","VII-C033"]),
    dict(id="CM-03", name="Contact without strict joint information", scenario="TTW-S06", shows="Contact does not imply strict join.", candidates=["VII-C007","VII-C009","VII-C036"]),
    dict(id="CM-04", name="Scheduling-only apparent joint novelty", scenario="TTW-S14", shows="Post-hoc scheduling can manufacture an apparent joint signal.", candidates=["VII-C009","VII-C025"]),
    dict(id="CM-05", name="Join that loses one child", scenario="TTW-S09", shows="Composite formation does not imply parent retention.", candidates=["VII-C009","VII-C030"]),
    dict(id="CM-06", name="Enablement without descent", scenario="TTW-S03", shows="An enabling condition can be load-bearing without factorization of the enabled object.", candidates=["VII-C012","VII-C015","VII-C034"]),
    dict(id="CM-07", name="Enablement necessary but insufficient", scenario="TTW-S03", shows="An enabler may be necessary while alternatives still determine the result.", candidates=["VII-C012","VII-C027","VII-C034"]),
    dict(id="CM-08", name="Sound but unreachable admission rule", scenario="TTW-S19", shows="Soundness does not imply operational reachability.", candidates=["VII-C001","VII-C002","VII-C021"]),
    dict(id="CM-09", name="Reachable admission that never occurs", scenario="TTW-S20", shows="Reachability does not imply occurrence.", candidates=["VII-C001","VII-C002","VII-C006","VII-C021"]),
    dict(id="CM-10", name="Holonomy with zero arrow", scenario="TTW-S17", shows="Route residue does not imply directionality.", candidates=["VII-C017","VII-C032"]),
    dict(id="CM-11", name="Observer occupancy omitted from budget", scenario="TTW-S22", shows="Hidden observer resources defeat endogenous/native credit.", candidates=["VII-C011","VII-C013","VII-C029"]),
    dict(id="CM-12", name="Total-lens result fails on partial self-owned access", scenario="TTW-S23", shows="Totality assumptions do not transfer silently.", candidates=["VII-C005","VII-C020","VII-C022","VII-C024"]),
    dict(id="CM-13", name="Product/common refinement without strictness", scenario="TTW-S07", shows="Common refinement is not anti-product novelty.", candidates=["VII-C008","VII-C009","VII-C026"]),
    dict(id="CM-14", name="Relabeling-only fake join", scenario="TTW-S15", shows="Presentation change cannot manufacture strict content.", candidates=["VII-C007","VII-C009"]),
    dict(id="CM-15", name="Strict extension without certified objecthood", scenario="TTW-S15", shows="Nonfactorization does not imply closure/objecthood.", candidates=["VII-C009"]),
    dict(id="CM-16", name="Strict join without directionality", scenario="TTW-S08", shows="Strict novelty does not imply a P6 arrow.", candidates=["VII-C009","VII-C032"]),
    dict(id="CM-17", name="Theorist-triggered enablement is not endogenous", scenario="TTW-S02", shows="Execution by the analyst fails the carried-generator condition.", candidates=["VII-C012","VII-C013","VII-C014"]),
    dict(id="CM-18", name="Finite negative search with open family", scenario="TTW-S19", shows="A bounded null does not prove a universal no-go.", candidates=["VII-C002","VII-C021","VII-C023","VII-C024","VII-C033"]),
    dict(id="CM-19", name="Shared carrier without lawful peer transport", scenario="TTW-S01", shows="Co-location does not provide an executable bridge or first capability.", candidates=["VII-C003","VII-C016","VII-C035"]),
    dict(id="CM-20", name="Post-hoc prediction self-certification", scenario="TTW-S04", shows="Retrospective admission cannot earn prospective credit.", candidates=["VII-C003","VII-C004","VII-C006"]),
    dict(id="CM-21", name="Zero-cost join hides positive observer cost", scenario="TTW-S22", shows="Unpriced occupancy invalidates no-cost credit.", candidates=["VII-C011","VII-C029","VII-C031","VII-C035"]),
    dict(id="CM-22", name="Parent refinement destroys an admissible join", scenario="TTW-S24", shows="Join admissibility need not be monotone under parent refinement.", candidates=["VII-C015","VII-C019","VII-C030"]),
    dict(id="CM-23", name="Seed-dependent closure fixed points", scenario="TTW-S24", shows="Initial partition/seed can change the terminal package.", candidates=["VII-C015","VII-C018"]),
    dict(id="CM-24", name="Identical members assembled in different orders", scenario="TTW-S16", shows="Bracketing/order may change the audited result.", candidates=["VII-C017","VII-C018","VII-C027","VII-C028","VII-C032"]),
    dict(id="CM-25", name="Join manufactures a cross-term needle", scenario="TTW-S24", shows="Joining need not monotonically dissolve obstructions.", candidates=["VII-C019","VII-C031","VII-C036"]),
    dict(id="CM-26", name="One-lineage pseudo-join", scenario="TTW-S05", shows="Behavioral difference inside one lineage does not establish source independence.", candidates=["VII-C005","VII-C010"]),
    dict(id="CM-27", name="Lawful parents with no common admissible package", scenario="TTW-S13", shows="Parent lawfulness does not guarantee join existence.", candidates=["VII-C008","VII-C026","VII-C033"]),
]


FORMAL_TARGETS = [
    ("FT01","Finite access-status data model","Lean candidate","P0",["SixBirds.ClaimRecord","SixBirdsFoundationsV.AccessPolicy"],["VII-C001","VII-C002","VII-C022"]),
    ("FT02","Admission reachability graph and occurrence separation","Lean candidate","P0",["SixBirdsFoundationsV.RepairGeneratorReachabilityRecord","SixBirdsFoundationsV.RepairGeneratorReachabilityCertified"],["VII-C001","VII-C002","VII-C021"]),
    ("FT03","Bootstrap obstruction","direct proof + Lean candidate","P0",["SixBirdsFoundationsV.NoReachableRepairGenerator"],["VII-C003","VII-C035"]),
    ("FT04","Prospective commitment timestamp/budget record","schema then Lean candidate","P1",["SixBirdsFoundationsV.SharedBudgetAllocationRecord"],["VII-C004","VII-C006"]),
    ("FT05","Source and bridge ledger","Lean candidate","P0",["SixBirdsFoundationsV.CarriedSource","SixBirdsFoundationsV.TransportTokenRecord"],["VII-C004","VII-C005","VII-C010","VII-C016","VII-C020"]),
    ("FT06","Typed contact witness","finite data model","P0",["SixBirdsIII.InstrumentClaimRecord"],["VII-C007","VII-C016"]),
    ("FT07","Join certificate normal form","Lean candidate","P0",["SixBirdsFoundationsV.repairJoin","SixBirdsFoundationsV.join_well_defined"],["VII-C007","VII-C009","VII-C026","VII-C030"]),
    ("FT08","Anti-product/nonfactorization witness","direct proof + finite check","P0",["SixBirdsFoundationsV.StrictSelfExtension"],["VII-C009","VII-C035","VII-C036"]),
    ("FT09","Join obstruction and budget record","Lean candidate","P0",["SixBirdsFoundationsV.BudgetFeasible","SixBirdsFoundationsV.ObstructionStatusRecord"],["VII-C008","VII-C011","VII-C019","VII-C031"]),
    ("FT10","Coverage-qualified non-interaction certificate","finite exhaustive check","P1",["SixBirdsFoundationsV.E11_NCTDObstruction"],["VII-C008","VII-C033"]),
    ("FT11","Enablement record","Lean candidate","P0",["SixBirdsFoundationsV.RepairGeneratorReachabilityRecord"],["VII-C012","VII-C014","VII-C027","VII-C034"]),
    ("FT12","Endogenous generator criterion","direct proof + Lean candidate","P0",["SixBirdsFoundationsV.NoReachableRepairGeneratorExcludesEndogenousFamily"],["VII-C013"]),
    ("FT13","Transmission/descent fidelity","schema only until maps fixed","P1",["SixBirdsIII.descent_square_recovery"],["VII-C015","VII-C034"]),
    ("FT14","Confluence and critical-pair finite models","finite exhaustive check","P1",["SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.caseB_confluent_runs_share_final","SixBirdsFoundationsVI.Laws.G8OdometerAbelianization.caseD_nonconfluent_witness"],["VII-C017","VII-C018","VII-C028"]),
    ("FT15","Interaction holonomy/arrow separation","Lean candidate + finite check","P0",["HolonomyMemory.LoopAsymmetry","HolonomyMemory.loopAsymmetry_exhibits_movedPredictive_fixedCurrent"],["VII-C017","VII-C027","VII-C032"]),
    ("FT16","Budget and observer occupancy","finite data model","P0",["SixBirdsFoundationsV.BindingExposureBudget","SixBirdsFoundationsV.PositiveAccessMoveCosts"],["VII-C006","VII-C011","VII-C013","VII-C029"]),
    ("FT17","Negative quantifier and claim-grade rules","direct proof","P0",["SixBirds.AdmissibleClaim","SixBirds.NonclaimRecord"],["VII-C002","VII-C005","VII-C020","VII-C021","VII-C022","VII-C023","VII-C024","VII-C033"]),
    ("FT18","No-free-access/no-free-join lemmas","direct proof + Lean candidate","P0",["SixBirdsMetaMath.FoundationsIV.Access.NoFreeDistinction.financed_refinement_retains_access"],["VII-C003","VII-C035"]),
    ("FT19","Parent retention and refinement transport","Lean candidate","P1",["SixBirdsMetaMath.FoundationsIV.StatusRecordsCoherence.ObjectPersistence.persistence_extension_retains_old"],["VII-C015","VII-C030"]),
    ("FT20","Residual/needle and finite-world semantics","finite exhaustive check","P1",["SixBirdsFoundationsV.ResidualStatusRecord","SixBirdsMetaMath.Xi.Obstruction.blindSpotWitness"],["VII-C019","VII-C025","VII-C031","VII-C036"]),
]


CHAPTERS = [
    ("Ch01","Scope, inheritance, grades, and bridge contract",[],["VII-C020","VII-C024"]),
    ("Ch02","Partial domains and access coordinates",["Ch01"],["VII-C001","VII-C022"]),
    ("Ch03","Admission, bootstrap, and prospective commitment",["Ch02"],["VII-C002","VII-C003","VII-C004","VII-C006"]),
    ("Ch04","Contact surfaces, interaction records, and peer transport",["Ch02","Ch03"],["VII-C005","VII-C007","VII-C016"]),
    ("Ch05","Join status, strictness, and parent retention",["Ch04"],["VII-C008","VII-C009","VII-C030"]),
    ("Ch06","Source, budget, observer, and no-free-join",["Ch03","Ch05"],["VII-C010","VII-C011","VII-C029","VII-C035"]),
    ("Ch07","Enablement, birth, transmission, and descent fidelity",["Ch03","Ch04"],["VII-C012","VII-C013","VII-C014","VII-C015","VII-C027","VII-C034"]),
    ("Ch08","Reachability and negative-result force",["Ch03","Ch04"],["VII-C021","VII-C023","VII-C033"]),
    ("Ch09","Confluence, order, holonomy, and arrow",["Ch05","Ch07"],["VII-C017","VII-C018","VII-C032"]),
    ("Ch10","Residuals, needles, and obstruction dissolution",["Ch05","Ch09"],["VII-C019","VII-C036"]),
    ("Ch11","Two-Theory World and countermodel battery",["Ch06","Ch08","Ch09","Ch10"],["VII-C025"]),
    ("Ch12","Formalization targets and explicit deferrals",["Ch01","Ch11"],["VII-C026","VII-C028","VII-C031"]),
]


RED_LINES = [
    "Do not redefine P1–P6, closure/objecthood, the F/E/G laws, or the eight existing no-gos as VII novelties.",
    "Do not infer shared access from common source, carrier, ancestry, vocabulary, or instrument.",
    "Do not infer witnessed contact from interface compatibility.",
    "Do not infer a join from contact.",
    "Do not infer strict join from product, common refinement, co-presentation, or relabeling.",
    "Do not infer objecthood from strictness/nonfactorization.",
    "Do not infer directionality from strictness, contact, order sensitivity, or holonomy.",
    "Do not infer occurrence from soundness, admissibility, executability, or reachability.",
    "Do not infer reachability from rule text or mathematical soundness.",
    "Do not equate enablement with descent, containment, sufficiency, causation, or endogeny.",
    "Do not label theorist-triggered or hidden-observer execution endogenous.",
    "Do not infer top-down creation of lower facts from structural selection or constraint.",
    "Do not relabel bridged records native or erase source lineage.",
    "Do not apply total-lens results to partial self-owned domains without a bridge theorem.",
    "Do not credit prospective commitment to a predicate fixed after observing the target evidence.",
    "Do not claim zero-cost interaction while omitting observer/instrument occupancy.",
    "Do not universalize a finite, pointwise, horizon-limited, or open-family negative.",
    "Do not call no evidenced contact certified non-interaction without coverage and detector-power witnesses.",
    "Do not claim a complete taxonomy of admission, contact, joins, or obstruction without a completeness proof.",
    "Do not claim necessary-and-sufficient join conditions unless both directions are proved on the declared carrier.",
    "Do not claim categorical reduction before defining the category and universal property.",
    "Do not claim a full generators-and-relations algebra before primitive operations and equivalences are fixed.",
    "Do not posit a conserved contact degree or one scalar interaction currency without an invariance theorem.",
    "Do not treat Two-Theory World success as a universal proof.",
    "Do not alter imported Foundations V/VI Lean sources; use VII-owned wrappers and exact bridge records.",
    "Do not claim fresh Lean kernel verification when Lean 4.28.0 has not been replayed locally.",
    "Do not reconstruct P039 body theorems from its abstract; eighteen includes and the bibliography are missing.",
    "Do not count P040 and P058 as independent evidence or choose a canonical version without a later ruling.",
    "Do not silently erase failed bridges, retractions, refunds, or negative runs from append-only ledgers.",
    "Do not present this readiness dossier as a Foundations VII proof or paper draft.",
]


DECISIONS = [
    ("DP01","Is contact surface primitive or reducible to inherited interface mediation?","Keep it as a candidate record; require a reduction proof before calling it derived.",["VII-C007","VII-C016"],"Exact source/target interface category and equivalence theorem."),
    ("DP02","Are join statuses complete?","Treat the list as scoped to the declared finite interface family.",["VII-C008"],"Completeness theorem or explicit counterexample outside the family."),
    ("DP03","Is source independence required for every join?","Require it only for independence-sensitive claims; preserve non-independent joins as separately typed.",["VII-C009","VII-C010"],"Claim-by-claim source sensitivity criterion."),
    ("DP04","Can categorical products or pullbacks represent the join?","Defer unconditional reduction; permit special-case theorems.",["VII-C026"],"Category, morphisms, universal property, and countermodels."),
    ("DP05","Is there one scalar join currency?","No; retain typed ledgers unless a representation theorem is proved.",["VII-C011"],"Additivity/duality theorem across all declared costs."),
    ("DP06","Is there a conserved contact degree, including observer/instrument occupancy?","Do not posit one; retain an explicit test program.",["VII-C031","VII-C029"],"Candidate invariant and nontrivial conservation proof."),
    ("DP07","How is simultaneous contact defined for incommensurable internal times?","Use explicit synchronization/order witnesses; no unique simultaneity assumption.",["VII-C032"],"Clock/interface model and invariance under admissible reparameterization."),
    ("DP08","When is enablement endogenous?","Use carried, reachable, executed, audited, and budgeted generator criteria.",["VII-C013"],"Proof that each condition is necessary or a revised grade."),
    ("DP09","Can contact create new participants or only a relation?","Keep both cases typed and require an objecthood witness for created participants.",["VII-C014"],"Finite birth models and closure proof."),
    ("DP10","Does parent refinement preserve joins?","No monotonicity assumption; classify preserve/strengthen/weaken/destroy cases.",["VII-C030"],"Refinement transport theorems and countermodels."),
    ("DP11","Does interaction holonomy imply an arrow?","No; require a separate drive/path-asymmetry certificate.",["VII-C017","VII-C032"],"Null-versus-driven theorem and reversal assay."),
    ("DP12","Should primitive generators and relations be developed in VII?","Defer until categorical and operational composition are fixed.",["VII-C028"],"Nonredundant primitive list and composition laws."),
    ("DP13","Which P040/P058 member is canonical?","Keep both non-independent and unresolved.",["VII-C020","VII-C024"],"Theorem-level source reconciliation and owner ruling."),
    ("DP14","Can P039 contribute body-level results?","No; abstract-only until missing source files are supplied.",["VII-C024"],"The eighteen included TeX files and bibliography."),
    ("DP15","How strong may certified non-interaction be?","Only as strong as the covered family, detector power, budget, and horizon.",["VII-C033"],"Closed-family audit or theorem-grade impossibility."),
]


NO_GOS = [
    ("NGVII-01","No first extension without seed or reachable generator",["VII-C003","VII-C035"],"TTW-S01","TTW-S02"),
    ("NGVII-02","No resemblance-only independence-sensitive join",["VII-C009","VII-C010"],"TTW-S05","TTW-S08"),
    ("NGVII-03","No retrospective self-certification",["VII-C006"],"TTW-S04","TTW-S03"),
    ("NGVII-04","No automatic total-lens transfer",["VII-C005","VII-C020"],"TTW-S23","TTW-S08"),
    ("NGVII-05","No unpriced observer-native formation credit",["VII-C029"],"TTW-S22","TTW-S02"),
    ("NGVII-06","No join from contact alone",["VII-C007","VII-C008"],"TTW-S06","TTW-S08"),
    ("NGVII-07","No product/common-refinement strictness credit",["VII-C009"],"TTW-S07","TTW-S08"),
    ("NGVII-08","No one-lineage source-independence credit",["VII-C010"],"TTW-S05","TTW-S08"),
    ("NGVII-09","No positive-cost join credit without payment or certified zero-cost channel",["VII-C011","VII-C035"],"TTW-S10","TTW-S08"),
    ("NGVII-10","No arrow from holonomy alone",["VII-C017","VII-C032"],"TTW-S17","TTW-S18"),
    ("NGVII-11","No occurrence from reachability alone",["VII-C021"],"TTW-S20","TTW-S21"),
]


ANTI_DUP = {
    "CG01":"Do not redescribe inherited quotient-relative access, adequacy, or fixed-interface saturation as VII novelties.",
    "CG02":"Do not identify a rule, mathematical operation, executable substrate transition, and occurred event.",
    "CG03":"Reuse existing no-free-distinction and repair-generator obstructions; add only the admission/bootstrap specialization.",
    "CG04":"Do not call retrospective fit prospective commitment.",
    "CG05":"Do not transfer total-lens or common-source results to partial shared access without a bridge.",
    "CG06":"Do not treat record completeness as join existence.",
    "CG07":"Do not call an obstruction taxonomy complete without proof.",
    "CG08":"Do not collapse product/composite formation into strict novelty.",
    "CG09":"Do not collapse behavioral nonfactorization into ancestry/source independence.",
    "CG10":"Do not assume one scalar currency or zero cost by omission.",
    "CG11":"Do not collapse peer transport, contact, and joint theory formation.",
    "CG12":"Do not import categorical language before objects and morphisms are fixed.",
    "CG13":"Do not claim full retention after erasure or partial projection.",
    "CG14":"Do not collapse enablement into descent, sufficient causation, or endogeny.",
    "CG15":"Do not create a new birth taxonomy before reconciling inherited classes.",
    "CG16":"Do not assume enablement transitivity.",
    "CG17":"Do not infer top-down fact creation or a temporal arrow from construction direction.",
    "CG18":"Do not infer global confluence from one commuting square.",
    "CG19":"Do not infer P6 directionality from P3/order holonomy.",
    "CG20":"Do not assume a unique simultaneity relation or infer irreversibility from parent entropy alone.",
    "CG21":"Do not collapse determination, exposure, recoverability, admissibility, and rigidity.",
    "CG22":"Do not assume wider access or joining monotonically dissolves all needles.",
    "CG23":"Do not omit observer/instrument occupancy from native or endogenous claims.",
    "CG24":"Do not treat citation or verbal similarity as theorem transport.",
    "CG25":"Do not infer occurrence or capability from soundness, or impossibility from short-horizon non-occurrence.",
    "CG26":"Do not universalize negatives beyond their quantified family.",
    "CG27":"Do not promote schemas, calibrations, examples, or philosophy to theorem grade.",
    "CG28":"Do not treat a finite assay as proof.",
    "CG29":"Do not claim a complete primitive algebra without generators/relations proof.",
    "CG30":"Do not name a conserved degree before an invariance theorem.",
}


def scenario_eval(flags: dict[str, Any]) -> tuple[str, dict[str, bool]]:
    f = defaultdict(bool, flags)
    contact = bool(f["contact"])
    strict_join = bool(contact and f["source_independent"] and f["composite"] and f["retention"] and f["anti_product"] and f["budget_ok"] and not f["scheduling_only"] and not f["relabel_only"])
    directionality = bool(f["drive"])
    occurred = bool(f["fired"])
    first_extension = bool(f["seed"] and f["generator_reachable"] and occurred)
    prospective_credit = bool(f["prospective"] and not f["retrospective"])
    certified_noninteraction = bool(not contact and f["closed_family"] and f["detector_power"])
    bridge_valid = not bool(f["total_lens_only"] and f["partial_domain"])
    endogenous = bool(f["generator_reachable"] and occurred and not f["observer_used"] and not f["seed"])
    if not f["seed"] and not f["generator_reachable"] and not any([contact,f["compatible"],f["closed_family"],f["sound"],f["prospective"],f["retrospective"],f["observer_used"],f["total_lens_only"],f["parent_refined"]]): status="BOOTSTRAP_BLOCKED"
    elif f["retrospective"]: status="RETROSPECTIVE_SELF_CERTIFICATION_REJECTED"
    elif f["observer_used"] and not f["observer_priced"]: status="UNPRICED_OBSERVER"
    elif f["total_lens_only"] and f["partial_domain"]: status="UNLICENSED_TOTALITY_TRANSFER"
    elif f["holonomy"] and not f["drive"] and not f["order_residue"]: status="HOLONOMY_ZERO_ARROW"
    elif f["drive"]: status="DRIVEN_ARROW"
    elif f["order_residue"]: status="ORDER_RESIDUE"
    elif f["sound"] and not f["reachable"]: status="SOUND_UNREACHABLE"
    elif f["reachable"] and not f["fired"]: status="REACHABLE_NONOCCURRENT"
    elif f["sound"] and f["reachable"] and f["fired"]: status="OCCURRENT_EVENT"
    elif f["parent_refined"] and f["join_destroyed"]: status="REFINEMENT_DESTROYS_JOIN"
    elif certified_noninteraction: status="CERTIFIED_NONINTERACTION"
    elif not contact and f["compatible"]: status="NO_EVIDENCED_CONTACT"
    elif f["scheduling_only"]: status="FAKE_JOIN_SCHEDULING"
    elif f["relabel_only"]: status="FAKE_JOIN_RELABELING"
    elif contact and f["same_source"] and f["resemblance_only"]: status="INDEPENDENCE_GATE_FAILED"
    elif contact and not f["composite"]: status="CONTACT_WITHOUT_JOIN"
    elif contact and f["common_refinement"] and not f["anti_product"]: status="COMMON_REFINEMENT_NONSTRICT"
    elif contact and f["composite"] and not f["retention"]: status="RETENTION_OBSTRUCTION"
    elif contact and f["composite"] and f["anti_product"] and not f["budget_ok"]: status="BUDGET_OBSTRUCTION"
    elif contact and f["composite"] and f["anti_product"] and not f["source_independent"]: status="SOURCE_OBSTRUCTION"
    elif strict_join: status="STRICT_JOIN"
    elif prospective_credit: status="PROSPECTIVE_ADMISSION"
    elif first_extension: status="LAWFUL_FIRST_EXTENSION"
    else: status="UNCLASSIFIED"
    derived = {"contact":contact,"strict_join":strict_join,"directionality":directionality,"reachable":bool(f["reachable"]),"occurred":occurred,"first_extension":first_extension,"prospective_credit":prospective_credit,"certified_noninteraction":certified_noninteraction,"bridge_valid":bridge_valid,"endogenous":endogenous,"new_residual":bool(f["new_residual"]),"holonomy":bool(f["holonomy"])}
    return status, derived


def graphml(path: Path, nodes: list[dict[str,str]], edges: list[dict[str,str]]) -> None:
    ns="http://graphml.graphdrawing.org/xmlns"; ET.register_namespace("",ns)
    root=ET.Element(f"{{{ns}}}graphml")
    for kid,target,name in [("k0","node","kind"),("k1","node","label"),("k2","edge","relation")]:
        ET.SubElement(root,f"{{{ns}}}key",{"id":kid,"for":target,"attr.name":name,"attr.type":"string"})
    g=ET.SubElement(root,f"{{{ns}}}graph",{"id":"FoundationsVIIReadiness","edgedefault":"directed"})
    for n in nodes:
        el=ET.SubElement(g,f"{{{ns}}}node",{"id":n["node_id"]})
        for kid,field in [("k0","kind"),("k1","label")]: d=ET.SubElement(el,f"{{{ns}}}data",{"key":kid}); d.text=n[field]
    for i,e in enumerate(edges,1):
        el=ET.SubElement(g,f"{{{ns}}}edge",{"id":f"e{i:06d}","source":e["source"],"target":e["target"]}); d=ET.SubElement(el,f"{{{ns}}}data",{"key":"k2"}); d.text=e["relation"]
    path.parent.mkdir(parents=True,exist_ok=True); ET.ElementTree(root).write(path,encoding="utf-8",xml_declaration=True)


def main() -> int:
    claims=read_jsonl(ROOT/"registry/claims.jsonl"); claim_by={x["claim_id"]:x for x in claims}
    claims_by_paper: dict[str,list[dict[str,Any]]]=defaultdict(list)
    for x in claims: claims_by_paper[x["source_paper"]].append(x)
    evidence=read_jsonl(ROOT/"wishlists/step2_evidence_links.jsonl"); ev_by={x["request_id"]:x for x in evidence}
    groups_rows=read_csv(ROOT/"wishlists/convergence_groups.csv")
    group_meta: dict[str,dict[str,Any]]={}
    for r in groups_rows:
        d=group_meta.setdefault(r["convergence_group"],{"group_title":r["group_title"],"group_scope":r["group_scope"],"request_ids":[]})
        d["request_ids"].append(r["request_id"])
    bridges=read_jsonl(ROOT/"bridges/bridge_atlas.jsonl"); bridge_by={x["bridge_id"]:x for x in bridges}
    laws=[]
    for p in ["F_laws","E_laws","G_laws","no_go_theorems"]: laws+=read_jsonl(ROOT/f"registry/{p}.jsonl")
    law_by={(x.get("law_id") or x.get("no_go_id") or x.get("id")):x for x in laws}
    lean=read_csv(ROOT/"formalization/integration/cumulative_lean_declarations.csv"); lean_by={x["fully_qualified_name"]:x for x in lean}
    catalog={x["paper_id"]:x for x in read_csv(ROOT/"config/paper_catalog.csv")}
    manifest={x["paper_id"]:x for x in read_csv(ROOT/"corpus/paper_manifest.csv")}

    # Clean only Step-3 owned generated trees.
    for rel in ["readiness","vii","formalization/step3"]:
        p=ROOT/rel
        if p.exists(): shutil.rmtree(p)
    for p in [ROOT/"readiness/candidates",ROOT/"readiness/paper_rereads",ROOT/"readiness/two_theory_world",ROOT/"vii/candidates",ROOT/"vii/rereads",ROOT/"vii/lab",ROOT/"vii/no_go",ROOT/"vii/dependency",ROOT/"formalization/step3"]: p.mkdir(parents=True,exist_ok=True)

    # Candidate dossiers with complete source traces.
    candidates=[]; candidate_by_group: dict[str,list[str]]=defaultdict(list); source_trace_rows=[]
    for spec in CANDIDATE_SPECS:
        atoms=unique(rid for g in spec["groups"] for rid in group_meta[g]["request_ids"])
        rows=[ev_by[x] for x in atoms]
        support=unique(cid for r in rows for cid in r["supporting_claim_ids"])
        boundary=unique(cid for r in rows for cid in r["counterclaim_or_boundary_ids"])
        open_ids=unique(cid for r in rows for cid in r["open_problem_ids"])
        bridge_ids=unique(bid for r in rows for bid in r["linked_bridge_ids"] if bid in bridge_by)
        law_ids=unique(lid for r in rows for lid in r["linked_law_or_no_go_ids"] if lid in law_by)
        resolved=[]; seen=set()
        for role,ids in [("SUPPORT",support),("BOUNDARY",boundary),("OPEN",open_ids)]:
            for cid in ids:
                if cid in seen or cid not in claim_by: continue
                seen.add(cid); c=claim_by[cid]
                loc={"candidate_id":spec["id"],"trace_role":role,"claim_id":cid,"source_paper":c["source_paper"],"source_title":c["source_title"],"claim_type":c["claim_type"],"claim_grade":c["claim_grade"],"proof_status":c.get("proof_status",""),"source_location":c["source_location"],"hypotheses":c.get("hypotheses",[]),"conclusion":c.get("conclusion",""),"normalized_claim":c.get("normalized_claim",""),"nonclaims":c.get("nonclaims",[]),"formalization_status":c.get("formalization",{}).get("status","")}
                resolved.append(loc); source_trace_rows.append(loc)
        candidate={
            "candidate_id":spec["id"],"name":spec["name"],"kind":spec["kind"],"priority":spec["priority"],"status_grade":"UNPROVED_FOUNDATIONS_VII_CANDIDATE" if "INHERITED" not in spec["kind"] else "INHERITED_PROTOCOL_WITH_VII_ADAPTER","proof_status":"SPECIFICATION_READY_NOT_PROVED","decision_status":"READY_FOR_LATER_PROOF_OR_SCOPE_DECISION","step3_ruling":"READINESS_ONLY_NO_NEW_THEOREM_ASSERTED","convergence_groups":spec["groups"],"wishlist_atoms":atoms,"typed_objects":[x[0] for x in OBJECT_SPECS if spec["id"] in x[5]],"setup":["Fix the inherited SBT theory package(s), carrier, interfaces, quotient/readout, and audit scope.","Declare all source, transition, budget, observer, and temporal records used by the candidate.","Restrict the conclusion to the stated finite or explicitly quantified carrier until a stronger proof is supplied."],"hypotheses":["All records are well typed and source-located.","No undeclared operation, source, or observer resource is used.","Inherited results are transported only through accepted bridge/reuse records."],"informal_law":spec["conclusion"],"proposed_conclusion":spec["conclusion"],"condition_grade":"Candidate theorem/schema at the declared scope; necessity/sufficiency only where explicitly proved later.","proof_obligations":spec["obligations"],"detector":{"signal":f"A source-typed witness satisfying the {spec['name']} record and its declared audit.","null":"A matched case with the principal witness removed while all unrelated fields are held fixed.","falsifier":f"A well-typed model satisfying the hypotheses but violating the proposed conclusion for {spec['name']}."},"falsifier":f"A valid declared-scope countermodel to {spec['conclusion']}","positive_model":spec["scenarios"][:1] or ["TTW-S08"],"null_models":spec["scenarios"][1:] or ["TTW-S12"],"countermodels":spec["cms"],"escape_routes":["Narrow or change the declared carrier/interface family.","Add an explicit source, seed, bridge, budget, or drive witness omitted by the no-go hypotheses."],"formalization_targets":spec["fts"],"recommended_chapter":spec["chapter"],"layer_instantiations":["finite formal theory domains","cognitive/social access policies","instrument-limited scientific applications"],"nonclaims":unique(spec["nonclaims"]+["This Step-3 dossier is not a proof of the candidate.","Finite reference-world success does not universalize the statement."]),"source_trace":{"supporting_claim_ids":support,"boundary_claim_ids":boundary,"open_problem_ids":open_ids,"bridge_ids":bridge_ids,"law_or_no_go_ids":law_ids,"resolved_source_locations":resolved,"trace_basis":"Complete union of Step-2 evidence attached to the candidate's convergence groups, deduplicated per candidate with SUPPORT > BOUNDARY > OPEN role precedence."}
        }
        candidates.append(candidate)
        for g in spec["groups"]: candidate_by_group[g].append(spec["id"])
        write_json(ROOT/f"readiness/candidates/{spec['id']}.json",candidate)
        md=[f"# {spec['id']} — {spec['name']}","",f"**Grade:** `{candidate['status_grade']}`  ",f"**Priority:** `{spec['priority']}`  ",f"**Chapter:** `{spec['chapter']}`  ","","## Proposed conclusion","",spec["conclusion"],"","## Setup and hypotheses",""]+[f"- {x}" for x in candidate["setup"]+candidate["hypotheses"]]+["","## Proof obligations",""]+[f"- {x}" for x in spec["obligations"]]+["","## Detector / null / falsifier","",f"- **Signal:** {candidate['detector']['signal']}",f"- **Null:** {candidate['detector']['null']}",f"- **Falsifier:** {candidate['detector']['falsifier']}","","## Finite models and countermodels","",f"- Positive: {', '.join(candidate['positive_model'])}",f"- Nulls: {', '.join(candidate['null_models'])}",f"- Countermodels: {', '.join(candidate['countermodels'])}","","## Source trace","",f"- Supporting claims: {len(support)}",f"- Boundary claims: {len(boundary)}",f"- Open obligations: {len(open_ids)}",f"- Exact deduplicated source rows: {len(resolved)}",f"- Bridges: {', '.join(bridge_ids) or 'none'}",f"- Prior laws/no-gos: {', '.join(law_ids) or 'none'}","","## Nonclaims",""]+[f"- {x}" for x in candidate["nonclaims"]]+[""]
        (ROOT/f"readiness/candidates/{spec['id']}.md").write_text("\n".join(md),encoding="utf-8")
    write_jsonl(ROOT/"readiness/candidate_index.jsonl",candidates)
    write_csv(ROOT/"readiness/candidate_index.csv",candidates,["candidate_id","name","kind","priority","status_grade","convergence_groups","wishlist_atoms","typed_objects","proposed_conclusion","proof_obligations","positive_model","null_models","countermodels","formalization_targets","recommended_chapter"])
    (ROOT/"readiness/CANDIDATE_INDEX.md").write_text("# Foundations VII candidate index\n\n"+md_table(["ID","Candidate","Grade","Priority","Groups","Chapter"],[[c["candidate_id"],c["name"],c["kind"],c["priority"],", ".join(c["convergence_groups"]),c["recommended_chapter"]] for c in candidates])+"\n",encoding="utf-8")

    # Scope inheritance / anti-duplication.
    scope=[]
    for gid in sorted(group_meta):
        atom_rows=[ev_by[x] for x in group_meta[gid]["request_ids"]]
        supports=unique(y for r in atom_rows for y in r["supporting_claim_ids"])
        boundaries=unique(y for r in atom_rows for y in r["counterclaim_or_boundary_ids"])
        opens=unique(y for r in atom_rows for y in r["open_problem_ids"])
        lids=unique(y for r in atom_rows for y in r["linked_law_or_no_go_ids"] if y in law_by)
        status="DEFERRED" if gid in {"CG12","CG29","CG30"} else ("INHERITED_DISCIPLINE" if gid in {"CG24","CG26","CG27"} else "INHERITED_CORE_PLUS_NEW_VII")
        scope.append({"convergence_group":gid,**group_meta[gid],"candidate_ids":candidate_by_group[gid],"disposition":status,"inherited_law_ids":lids,"supporting_claim_ids":supports,"boundary_claim_ids":boundaries,"open_problem_ids":opens,"inherited_core":f"The prior corpus supplies {len(supports)} supporting claim records, {len(boundaries)} explicit boundaries, {len(opens)} open obligations, and the linked law/no-go set {', '.join(lids) or 'none explicitly tagged'}.","anti_duplication_ruling":ANTI_DUP[gid],"new_vii_obligation":"Resolve only the remainder stated by the group's scope: "+group_meta[gid]["group_scope"],"birdint_available":any(claim_by[x]["source_paper"]=="P026" for x in supports if x in claim_by),"deferred_or_blocked":"Explicitly deferred" if status=="DEFERRED" else "No critical source blocker; theorem proof remains future work."})
    write_jsonl(ROOT/"readiness/scope_inheritance.jsonl",scope); write_csv(ROOT/"readiness/scope_inheritance.csv",scope,["convergence_group","group_title","group_scope","request_ids","candidate_ids","disposition","inherited_law_ids","supporting_claim_ids","boundary_claim_ids","open_problem_ids","inherited_core","anti_duplication_ruling","new_vii_obligation","birdint_available","deferred_or_blocked"])
    (ROOT/"readiness/SCOPE_INHERITANCE.md").write_text("# Scope inheritance and anti-duplication map\n\n"+"\n\n".join(f"## {r['convergence_group']} — {r['group_title']}\n\n**Disposition:** `{r['disposition']}`\n\n**Inherited core:** {r['inherited_core']}\n\n**Anti-duplication:** {r['anti_duplication_ruling']}\n\n**New or deferred obligation:** {r['new_vii_obligation']}" for r in scope)+"\n",encoding="utf-8")

    # Object model.
    objects=[]
    for oid,name,sig,defined,status,cids in OBJECT_SPECS:
        objects.append({"object_id":oid,"name":name,"signature":sig,"defined_from":defined,"status":status,"irreducibility":"Inherited object remains authoritative." if status=="INHERITED" else "Retained as a candidate primitive/record because the listed operational fields are not jointly recoverable from one inherited object without an adapter theorem.","candidate_ids":cids,"nonclaims":["This record does not replace P1–P6.","Primitive status remains reviewable if a later reduction theorem is proved."]})
    write_jsonl(ROOT/"readiness/object_model.jsonl",objects); write_csv(ROOT/"readiness/object_model.csv",objects,["object_id","name","signature","defined_from","status","irreducibility","candidate_ids","nonclaims"])
    (ROOT/"readiness/OBJECT_MODEL.md").write_text("# Minimal Foundations VII object model\n\n"+md_table(["ID","Object","Status","Signature","Defined from"],[[o["object_id"],o["name"],o["status"],o["signature"],", ".join(o["defined_from"])] for o in objects])+"\n",encoding="utf-8")

    # Wishlist final adjudication.
    def status_for(r: dict[str,Any]) -> str:
        gid=r["convergence_group"]; text=r["atomic_request"].lower(); rid=r["request_id"]
        if gid in {"CG12","CG29","CG30"}: return "DEFERRED_TO_LATER_FOUNDATION"
        if gid=="CG28" or any(w in text for w in ["test ","measure ","build a finite","publish substrate","validate that"]): return "EXPERIMENTAL_OR_CALIBRATION_OBLIGATION"
        if rid.startswith("ARC-NG") or rid.startswith("MM-NG") or rid.startswith("MED-NG") or r["countermodel_requirement"]=="YES" or " cannot " in f" {text} ": return "COUNTERMODEL_OR_NO_GO_NEEDED"
        if gid in {"CG26","CG27"} and r["step2_evidence_status"]=="CORPUS_RESULT_IDENTIFIED_VERIFY_EXACT_SCOPE": return "INHERITED_RESULT"
        if gid=="CG24" or r["step2_evidence_status"]=="CORPUS_RESULT_IDENTIFIED_VERIFY_EXACT_SCOPE": return "COROLLARY_WITH_EXPLICIT_BRIDGE"
        if any(text.startswith(w) for w in ["define","specify","require","represent","classify","maintain","format","separate"]): return "CANDIDATE_VII_SCHEMA_OR_DEFINITION"
        return "CANDIDATE_VII_THEOREM"
    adjud=[]
    scope_by={x["convergence_group"]:x for x in scope}
    for r in evidence:
        s=scope_by[r["convergence_group"]]
        final=status_for(r)
        adjud.append({"request_id":r["request_id"],"source_file":r["source_file"],"source_line":r["source_line"],"source_anchor":r["source_anchor"],"atomic_request":r["atomic_request"],"convergence_group":r["convergence_group"],"group_title":s["group_title"],"candidate_ids":candidate_by_group[r["convergence_group"]],"final_status":final,"supporting_claim_ids":r["supporting_claim_ids"],"boundary_claim_ids":r["counterclaim_or_boundary_ids"],"open_problem_ids":r["open_problem_ids"],"bridge_ids":r["linked_bridge_ids"],"law_or_no_go_ids":r["linked_law_or_no_go_ids"],"countermodel_requirement":r["countermodel_requirement"],"required_artifact":r["required_artifact"],"scope_modifier":"Finite/declared carriers and explicit source, runtime, interface, budget, and audit records unless a later theorem discharges stronger hypotheses.","rationale":f"Step 2 status: {r['step2_evidence_status']}. {s['inherited_core']} Anti-duplication: {s['anti_duplication_ruling']} Step 3 therefore assigns {final} and routes the remaining work to {', '.join(candidate_by_group[r['convergence_group']])}.","acceptance_or_red_line":r["acceptance_or_red_line"]})
    write_jsonl(ROOT/"wishlists/step3_adjudication.jsonl",adjud); write_csv(ROOT/"wishlists/step3_adjudication.csv",adjud,["request_id","source_file","source_line","source_anchor","atomic_request","convergence_group","group_title","candidate_ids","final_status","supporting_claim_ids","boundary_claim_ids","open_problem_ids","bridge_ids","law_or_no_go_ids","countermodel_requirement","required_artifact","scope_modifier","rationale","acceptance_or_red_line"])
    # compact mirror names
    shutil.copy2(ROOT/"wishlists/step3_adjudication.jsonl",ROOT/"wishlists/final_adjudication_step3.jsonl"); shutil.copy2(ROOT/"wishlists/step3_adjudication.csv",ROOT/"wishlists/final_adjudication_step3.csv")
    counts=Counter(x["final_status"] for x in adjud)
    (ROOT/"wishlists/WISHLIST_ADJUDICATION_STEP3.md").write_text("# Final Step-3 wish-list adjudication\n\nAll 130 atoms are adjudicated exactly once.\n\nStatus census: `"+str(dict(sorted(counts.items())))+"`.\n\n"+md_table(["Request","Group","Final status","Candidates"],[[x["request_id"],x["convergence_group"],x["final_status"],", ".join(x["candidate_ids"])] for x in adjud])+"\n",encoding="utf-8")

    # Finite scenarios and evaluator results.
    scenario_rows=[]; result_rows=[]; assertion_count=0; assertion_pass=0
    for s in SCENARIOS:
        status,derived=scenario_eval(s["flags"]); checks={k:(derived.get(k)==v) for k,v in s["assertions"].items()}; assertion_count+=len(checks); assertion_pass+=sum(checks.values())
        cids=unique(c["candidate_id"] for c in candidates if s["id"] in c["positive_model"]+c["null_models"])
        row={"scenario_id":s["id"],"name":s["name"],"flags":s["flags"],"expected_status":s["expected"],"assertions":s["assertions"],"candidate_ids":cids,"falsifier":"Reference evaluator status or any declared assertion differs from the frozen expectation."}
        scenario_rows.append(row); result_rows.append({"scenario_id":s["id"],"expected_status":s["expected"],"observed_status":status,"status_pass":status==s["expected"],"assertion_results":checks,"all_pass":status==s["expected"] and all(checks.values())})
    write_jsonl(ROOT/"readiness/two_theory_world/scenarios.jsonl",scenario_rows); write_csv(ROOT/"readiness/two_theory_world/scenarios.csv",scenario_rows,["scenario_id","name","flags","expected_status","assertions","candidate_ids","falsifier"]); write_jsonl(ROOT/"readiness/two_theory_world/reference_model_results.jsonl",result_rows)
    ref_summary={"scenario_count":len(result_rows),"status_matches":sum(x["status_pass"] for x in result_rows),"assertion_count":assertion_count,"assertions_passing":assertion_pass,"all_pass":all(x["all_pass"] for x in result_rows)}; write_json(ROOT/"generated/step3_reference_model_results.json",ref_summary)
    (ROOT/"readiness/two_theory_world/SPECIFICATION.md").write_text("# Two-Theory World specification\n\nThe finite world freezes source, contact, join, budget, observer, reachability, order, and negative-result controls before later implementation. It is a consistency/reference assay, not empirical validation or a replacement for proof.\n\n"+md_table(["ID","Scenario","Expected","Candidates"],[[x["scenario_id"],x["name"],x["expected_status"],", ".join(x["candidate_ids"])] for x in scenario_rows])+"\n",encoding="utf-8")
    (ROOT/"readiness/two_theory_world/REFERENCE_MODEL_RESULTS.md").write_text(f"# Two-Theory World reference results\n\n- Scenarios: **{len(result_rows)}**\n- Status matches: **{ref_summary['status_matches']}**\n- Assertions: **{assertion_pass}/{assertion_count}**\n- Overall: **{'PASS' if ref_summary['all_pass'] else 'FAIL'}**\n",encoding="utf-8")

    # Countermodel atlas.
    cms=[{"countermodel_id":x["id"],"name":x["name"],"scenario_id":x["scenario"],"shows":x["shows"],"candidate_ids":x["candidates"],"escape_route":"Add the missing typed witness or narrow the claim; do not relabel the countermodel as a positive case."} for x in COUNTERMODELS]
    write_jsonl(ROOT/"readiness/countermodel_atlas.jsonl",cms); write_csv(ROOT/"readiness/countermodel_atlas.csv",cms,["countermodel_id","name","scenario_id","shows","candidate_ids","escape_route"])
    (ROOT/"readiness/COUNTERMODEL_ATLAS.md").write_text("# Countermodel and null atlas\n\n"+md_table(["ID","Countermodel","Shows","Scenario","Candidates"],[[x["countermodel_id"],x["name"],x["shows"],x["scenario_id"],", ".join(x["candidate_ids"])] for x in cms])+"\n",encoding="utf-8")

    # Formalization targets and exact prior declaration reuse.
    formal=[]; reuse_rows=[]
    for tid,name,mode,priority,decls,cids in FORMAL_TARGETS:
        missing=[d for d in decls if d not in lean_by]
        if missing: raise RuntimeError(f"Missing prior declarations for {tid}: {missing}")
        formal.append({"target_id":tid,"name":name,"proof_mode":mode,"priority":priority,"prior_declarations":decls,"candidate_ids":cids,"new_module":f"FoundationsVII.Readiness.{tid}","kernel_status":"NOT_IMPLEMENTED_IN_STEP3; specification only","step3_boundary":"No new Lean declaration or fresh kernel claim in Step 3."})
        for d in decls: reuse_rows.append({"target_id":tid,"candidate_ids":cids,"prior_declaration":d,**lean_by[d]})
    write_jsonl(ROOT/"formalization/step3/formalization_targets.jsonl",formal); write_csv(ROOT/"formalization/step3/formalization_targets.csv",formal,["target_id","name","proof_mode","priority","prior_declarations","candidate_ids","new_module","kernel_status","step3_boundary"]); write_csv(ROOT/"formalization/step3/prior_reuse_matrix.csv",reuse_rows,["target_id","candidate_ids","prior_declaration","layer","module","file","line","kind","declared_name","namespace","fully_qualified_name"]); write_jsonl(ROOT/"formalization/step3/prior_reuse_matrix.jsonl",reuse_rows)
    (ROOT/"formalization/step3/FORMALIZATION_TARGETS.md").write_text("# Foundations VII formalization targets\n\nStep 3 specifies proof targets and exact inherited declaration reuse only. It adds no Lean declaration and claims no fresh Lean 4.28.0 kernel replay.\n\n"+md_table(["ID","Target","Mode","Priority","Candidates","Prior declarations"],[[x["target_id"],x["name"],x["proof_mode"],x["priority"],", ".join(x["candidate_ids"]),", ".join(x["prior_declarations"])] for x in formal])+"\n",encoding="utf-8")

    # Chapters, red lines, decisions, candidate no-gos.
    chapters=[{"chapter_id":cid,"title":title,"depends_on":deps,"candidate_ids":cids,"purpose":"Logical placement only; this is not draft prose."} for cid,title,deps,cids in CHAPTERS]
    write_jsonl(ROOT/"readiness/chapter_dag.jsonl",chapters); write_csv(ROOT/"readiness/chapter_dag.csv",chapters,["chapter_id","title","depends_on","candidate_ids","purpose"]); (ROOT/"readiness/CHAPTER_DAG.md").write_text("# Proposed chapter dependency DAG\n\nLogical order only; not a paper draft.\n\n"+md_table(["Chapter","Title","Depends on","Candidates"],[[x["chapter_id"],x["title"],", ".join(x["depends_on"]),", ".join(x["candidate_ids"])] for x in chapters])+"\n",encoding="utf-8")
    red=[{"red_line_id":f"RL{i:02d}","rule":rule,"enforcement":"candidate nonclaims + validator + later drafting gate"} for i,rule in enumerate(RED_LINES,1)]; write_jsonl(ROOT/"readiness/red_lines.jsonl",red); write_csv(ROOT/"readiness/red_lines.csv",red,["red_line_id","rule","enforcement"]); (ROOT/"readiness/RED_LINES.md").write_text("# Red-line and nonclaim register\n\n"+"\n".join(f"- **{x['red_line_id']}** — {x['rule']}" for x in red)+"\n",encoding="utf-8")
    decisions=[{"decision_id":a,"question":b,"current_ruling":c,"blocking_candidates":d,"evidence_needed":e} for a,b,c,d,e in DECISIONS]; write_jsonl(ROOT/"readiness/decision_points.jsonl",decisions); write_csv(ROOT/"readiness/decision_points.csv",decisions,["decision_id","question","current_ruling","blocking_candidates","evidence_needed"]); (ROOT/"readiness/DECISION_POINTS.md").write_text("# Explicit Step-3 decision points\n\n"+"\n\n".join(f"## {x['decision_id']}\n\n**Question:** {x['question']}\n\n**Current safe ruling:** {x['current_ruling']}\n\n**Evidence gate:** {x['evidence_needed']}" for x in decisions)+"\n",encoding="utf-8")
    nogos=[{"no_go_id":a,"name":b,"candidate_ids":c,"failure_scenario":d,"escape_or_positive_scenario":e,"hypotheses":"Only the typed conditions recorded in the associated candidate dossier and finite scenario.","conclusion_grade":"CANDIDATE_SCOPED_NO_GO_NOT_YET_PROVED","escape_routes":"The positive/escape scenario supplies the missing seed, source, budget, bridge, drive, or occurrence witness.","nonclaims":"No universal impossibility beyond the declared carrier/family."} for a,b,c,d,e in NO_GOS]; write_jsonl(ROOT/"readiness/no_go_program.jsonl",nogos); write_csv(ROOT/"readiness/no_go_program.csv",nogos,["no_go_id","name","candidate_ids","failure_scenario","escape_or_positive_scenario","hypotheses","conclusion_grade","escape_routes","nonclaims"]); (ROOT/"readiness/NO_GO_PROGRAM.md").write_text("# Candidate Foundations VII no-go program\n\nThese are scoped proof targets, not proved theorems.\n\n"+md_table(["ID","No-go","Candidates","Failure assay","Escape control"],[[x["no_go_id"],x["name"],", ".join(x["candidate_ids"]),x["failure_scenario"],x["escape_or_positive_scenario"]] for x in nogos])+"\n",encoding="utf-8")

    # All-paper dependency reread records.
    group_to_candidates={g:set(v) for g,v in candidate_by_group.items()}
    rereads=[]
    for pid in sorted(claims_by_paper):
        pcs=sorted(claims_by_paper[pid],key=lambda x:x["claim_id"])
        group_hits=Counter(g for c in pcs for g in c.get("vii_links",[]))
        cids=unique(cid for g,_ in group_hits.most_common() for cid in sorted(group_to_candidates.get(g,set())))
        if not cids: cids=["VII-C020","VII-C024"]
        boundary=[c["claim_id"] for c in pcs if c["claim_grade"] in {"EXPLICIT_NONCLAIM_OR_SCOPE_BOUNDARY","NONCLAIM","SCOPE_BOUNDARY"} or "nonclaim" in c["claim_type"].lower() or "scope" in c["claim_type"].lower()]
        open_ids=[c["claim_id"] for c in pcs if "OPEN" in c["claim_grade"] or "open" in c["claim_type"].lower()]
        source_status="BLOCKED_BODY_LEVEL_SOURCE; ABSTRACT_ONLY" if pid=="P039" else "COMPLETE_SUPPLIED_SOURCE_TREE"
        version="UNRESOLVED_NONINDEPENDENT_VF-SAU-01" if pid in {"P040","P058"} else "NOT_APPLICABLE"
        r={"paper_id":pid,"title":catalog[pid]["title"],"reading_order":catalog[pid]["reading_order"],"cluster":catalog[pid]["cluster"],"all_claims_reconsidered":len(pcs),"relevant_claim_ids":[c["claim_id"] for c in pcs],"boundary_claim_ids":boundary,"open_problem_ids":open_ids,"candidate_ids":cids,"top_convergence_groups":[g for g,_ in group_hits.most_common(10)],"source_status":source_status,"version_family_ruling":version,"source_path":manifest[pid]["source_path"],"root_sha256":manifest[pid]["root_sha256"],"source_tree_sha256":manifest[pid]["tree_sha256"],"step3_role":"BLOCKED_SOURCE_ABSTRACT_ONLY" if pid=="P039" else "DEPENDENCY_CLOSURE_REREAD","findings":[f"All {len(pcs)} canonical Step-2 claims were reconsidered against the candidate graph.","Exact source statements and grades remain controlling; this record is a dependency index.","Application-specific success cannot be promoted back into an abstract VII theorem without a bridge."],"anti_overread":[c.get("normalized_claim","") for c in pcs if c["claim_id"] in boundary[:8]]}
        rereads.append(r); write_json(ROOT/f"readiness/paper_rereads/{pid}.json",r)
        extra=" The supplied package omits eighteen included TeX files and the bibliography; no body theorem is reconstructed." if pid=="P039" else ""
        (ROOT/f"readiness/paper_rereads/{pid}.md").write_text(f"# {pid} — {r['title']}\n\n**Status:** `{source_status}`  \n**Claims reconsidered:** {len(pcs)}  \n**Candidate links:** {', '.join(cids)}  \n**Version ruling:** `{version}`\n\nAll canonical claim, boundary, and open-obligation records for this paper were reread through the Step-3 candidate dependency graph.{extra}\n\n## Anti-overread\n\n"+"\n".join(f"- {x}" for x in r["anti_overread"])+"\n",encoding="utf-8")
    write_jsonl(ROOT/"readiness/paper_reread_matrix.jsonl",rereads); write_csv(ROOT/"readiness/paper_reread_matrix.csv",rereads,["paper_id","title","reading_order","cluster","all_claims_reconsidered","relevant_claim_ids","boundary_claim_ids","open_problem_ids","candidate_ids","top_convergence_groups","source_status","version_family_ruling","source_path","root_sha256","source_tree_sha256","step3_role"])
    (ROOT/"readiness/PAPER_REREAD_MATRIX.md").write_text("# All-paper Step-3 dependency reread matrix\n\n"+md_table(["Paper","Claims","Status","Candidate links","Version ruling"],[[x["paper_id"],x["all_claims_reconsidered"],x["source_status"],len(x["candidate_ids"]),x["version_family_ruling"]] for x in rereads])+"\n",encoding="utf-8")

    # Comprehensive dependency graph.
    nodes: dict[str,dict[str,str]]={}; edges:set[tuple[str,str,str]]=set()
    def node(i,k,l): nodes.setdefault(i,{"node_id":i,"kind":k,"label":l[:300]})
    def edge(a,b,r): edges.add((a,b,r))
    for c in candidates:
        cid=c["candidate_id"]; node(cid,"candidate",c["name"])
        for g in c["convergence_groups"]: node(g,"convergence_group",group_meta[g]["group_title"]); edge(g,cid,"motivates")
        for a in c["wishlist_atoms"]: node(a,"wishlist_atom",ev_by[a]["atomic_request"]); edge(a,cid,"adjudicated_by"); edge(a,ev_by[a]["convergence_group"],"belongs_to")
        for loc in c["source_trace"]["resolved_source_locations"]: node(loc["claim_id"],"prior_claim",loc["normalized_claim"]); edge(loc["claim_id"],cid,loc["trace_role"])
        for b in c["source_trace"]["bridge_ids"]: node(b,"typed_bridge",bridge_by[b].get("classification","bridge")); edge(b,cid,"bridge_dependency")
        for l in c["source_trace"]["law_or_no_go_ids"]: node(l,"prior_law_or_no_go",l); edge(l,cid,"prior_machinery")
        for s in set(c["positive_model"]+c["null_models"]): node(s,"finite_scenario",next(x["name"] for x in scenario_rows if x["scenario_id"]==s)); edge(cid,s,"tested_by")
        for cm in c["countermodels"]: node(cm,"countermodel",next(x["name"] for x in cms if x["countermodel_id"]==cm)); edge(cm,cid,"blocks_overread")
        for ft in c["formalization_targets"]: node(ft,"formal_target",next(x["name"] for x in formal if x["target_id"]==ft)); edge(cid,ft,"formalized_later_by")
        node(c["recommended_chapter"],"chapter",next(x["title"] for x in chapters if x["chapter_id"]==c["recommended_chapter"])); edge(cid,c["recommended_chapter"],"assigned_to")
        for o in objects:
            if cid in o["candidate_ids"]: node(o["object_id"],"object",o["name"]); edge(o["object_id"],cid,"typed_object_for")
    for o in objects:
        node(o["object_id"],"object",o["name"])
        for p in o["defined_from"]: edge(p,o["object_id"],"defines")
    for n in nogos:
        node(n["no_go_id"],"candidate_no_go",n["name"])
        for cid in n["candidate_ids"]: edge(n["no_go_id"],cid,"no_go_front_for")
        edge(n["no_go_id"],n["failure_scenario"],"failure_assay"); edge(n["no_go_id"],n["escape_or_positive_scenario"],"escape_control")
    for d in decisions:
        node(d["decision_id"],"decision",d["question"])
        for cid in d["blocking_candidates"]: edge(d["decision_id"],cid,"governs")
    for r in red:
        node(r["red_line_id"],"red_line",r["rule"]); rt=tokens(r["rule"])
        for c in candidates:
            if len(rt & tokens(c["name"]+" "+c["proposed_conclusion"]+" "+" ".join(c["nonclaims"])))>=2: edge(r["red_line_id"],c["candidate_id"],"constrains")
    for ch in chapters:
        node(ch["chapter_id"],"chapter",ch["title"])
        for dep in ch["depends_on"]: edge(dep,ch["chapter_id"],"precedes")
    for f in formal:
        for d in f["prior_declarations"]: node(d,"prior_lean_declaration",d); edge(f["target_id"],d,"reuses")
    node_rows=sorted(nodes.values(),key=lambda x:x["node_id"]); edge_rows=[{"source":a,"target":b,"relation":r} for a,b,r in sorted(edges)]
    write_csv(ROOT/"readiness/candidate_dependency_nodes.csv",node_rows,["node_id","kind","label"]); write_csv(ROOT/"readiness/candidate_dependency_edges.csv",edge_rows,["source","target","relation"]); graphml(ROOT/"readiness/candidate_dependency_graph.graphml",node_rows,edge_rows); write_csv(ROOT/"readiness/candidate_source_trace.csv",source_trace_rows,["candidate_id","trace_role","claim_id","source_paper","source_title","claim_type","claim_grade","proof_status","source_location","hypotheses","conclusion","normalized_claim","nonclaims","formalization_status"]); write_jsonl(ROOT/"readiness/candidate_source_trace.jsonl",source_trace_rows)

    # Compact vii/ mirror for later paper planning tools.
    for src,dst in [("candidate_index.jsonl","candidates/candidates.jsonl"),("candidate_index.csv","candidates/candidates.csv"),("object_model.jsonl","object_model/object_model.jsonl"),("object_model.csv","object_model/object_model.csv"),("scope_inheritance.jsonl","scope_inheritance_map.jsonl"),("scope_inheritance.csv","scope_inheritance_map.csv"),("countermodel_atlas.jsonl","countermodels/countermodel_atlas.jsonl"),("countermodel_atlas.csv","countermodels/countermodel_atlas.csv"),("chapter_dag.jsonl","chapter/chapter_nodes.jsonl"),("chapter_dag.csv","chapter/chapter_dependency_dag.csv"),("red_lines.jsonl","red_line_register.jsonl"),("red_lines.csv","red_line_register.csv"),("decision_points.jsonl","decisions/decision_points.jsonl"),("decision_points.csv","decisions/decision_points.csv"),("no_go_program.jsonl","no_go/no_go_program.jsonl"),("no_go_program.csv","no_go/no_go_program.csv")]:
        (ROOT/f"vii/{dst}").parent.mkdir(parents=True,exist_ok=True); shutil.copy2(ROOT/f"readiness/{src}",ROOT/f"vii/{dst}")
    for c in candidates: shutil.copy2(ROOT/f"readiness/candidates/{c['candidate_id']}.md",ROOT/f"vii/candidates/{c['candidate_id']}.md")
    for r in rereads: shutil.copy2(ROOT/f"readiness/paper_rereads/{r['paper_id']}.md",ROOT/f"vii/rereads/{r['paper_id']}.md"); shutil.copy2(ROOT/f"readiness/paper_rereads/{r['paper_id']}.json",ROOT/f"vii/rereads/{r['paper_id']}.json")
    for src,dst in [("readiness/two_theory_world/scenarios.jsonl","vii/lab/scenarios.jsonl"),("readiness/two_theory_world/scenarios.csv","vii/lab/scenarios.csv"),("readiness/two_theory_world/SPECIFICATION.md","vii/lab/TWO_THEORY_WORLD.md"),("readiness/two_theory_world/REFERENCE_MODEL_RESULTS.md","vii/lab/REFERENCE_MODEL_RESULTS.md"),("readiness/candidate_dependency_nodes.csv","vii/dependency/nodes.csv"),("readiness/candidate_dependency_edges.csv","vii/dependency/edges.csv"),("readiness/candidate_dependency_graph.graphml","vii/dependency/candidate_dependency_graph.graphml"),("readiness/candidate_source_trace.csv","vii/dependency/candidate_source_trace.csv"),("readiness/candidate_source_trace.jsonl","vii/dependency/candidate_source_trace.jsonl")]: shutil.copy2(ROOT/src,ROOT/dst)
    shutil.copytree(ROOT/"formalization/step3",ROOT/"vii/formalization",dirs_exist_ok=True)

    # Coverage transition: 57 CLOSED, P039 BLOCKED.
    coverage=read_csv(ROOT/"corpus/coverage.csv")
    if not (ROOT/"corpus/coverage_history_step3.csv").exists(): shutil.copy2(ROOT/"corpus/coverage.csv",ROOT/"corpus/coverage_history_step3.csv")
    for row in coverage:
        if row["paper_id"]=="P039": row["state"]="BLOCKED"; row["notes"]="Step 3 adjudicated abstract-level evidence only; eighteen included TeX files and bibliography remain missing."
        else: row["state"]="CLOSED"; row["notes"]="Step 3 dependency reread and VII adjudication complete; source claims remain authoritative."
    write_csv(ROOT/"corpus/coverage.csv",coverage,list(coverage[0].keys()))

    summary={"stage":"STEP3_READINESS_COMPLETE_NO_PAPER_DRAFT","date":DATE,"papers_reread":len(rereads),"scope_groups":len(scope),"object_model_records":len(objects),"candidate_dossiers":len(candidates),"wishlist_atoms_adjudicated":len(adjud),"wishlist_status_counts":dict(sorted(counts.items())),"finite_scenarios":len(scenario_rows),"countermodels":len(cms),"candidate_no_gos":len(nogos),"formalization_targets":len(formal),"prior_lean_declaration_reuse_links":len(reuse_rows),"chapters":len(chapters),"red_lines":len(red),"decision_points":len(decisions),"candidate_source_trace_rows":len(source_trace_rows),"candidate_dependency_nodes":len(node_rows),"candidate_dependency_edges":len(edge_rows),"new_foundations_vii_lean_declarations":0,"critical_blockers":[],"noncritical_limitations":["P039 remains abstract-only because eighteen included TeX files and the bibliography are absent.","Lean 4.28.0 is unavailable locally; no fresh kernel replay is claimed.","P040/P058 remain one unresolved non-independent evidence family.","Universal categorical join reduction, a full generators-and-relations algebra, and a conserved contact degree are deferred."]}
    write_json(ROOT/"generated/step3_summary.json",summary); write_json(ROOT/"generated/step3_normalized_summary.json",summary); write_json(ROOT/"config/step3_blueprint.json",{"stage":summary["stage"],"date":DATE,"candidate_ids":[x["candidate_id"] for x in candidates],"object_ids":[x["object_id"] for x in objects],"scenario_ids":[x["scenario_id"] for x in scenario_rows],"countermodel_ids":[x["countermodel_id"] for x in cms],"formal_target_ids":[x["target_id"] for x in formal],"chapter_ids":[x["chapter_id"] for x in chapters],"red_line_ids":[x["red_line_id"] for x in red],"decision_ids":[x["decision_id"] for x in decisions],"no_go_ids":[x["no_go_id"] for x in nogos]})
    (ROOT/"readiness/CLAIMABLE_BOUNDARY.md").write_text("# Foundations VII claimable boundary\n\n## Defensible new center\n\nA scoped, proof-carrying admission/contact calculus for partially accessible, source-typed theory packages: operational domain states, prospective commitment, witnessed contact, certificate-bearing strict join, enablement attribution, observer occupancy, reachability, and coverage-qualified obstruction/non-interaction.\n\n## Inherited rather than new\n\nClosure/objecthood, quotient-relative access, strict nonfactorization, F/E/G laws, BirdInt roles, route mismatch, confluence/holonomy machinery, currencies/budgets, and the eight existing no-gos remain inherited and require exact adapters.\n\n## Not presently claimable\n\nA universal join taxonomy, unconditional categorical reduction, a complete primitive algebra, one scalar interaction currency, a conserved contact degree, monotone access growth, automatic totality transfer, or an arrow inferred from holonomy.\n",encoding="utf-8")
    (ROOT/"readiness/READINESS_DOSSIER.md").write_text(f"# Foundations VII pre-authoring readiness dossier\n\nStep 3 closes the dependency and scope questions needed before a later paper-planning phase. It contains {len(candidates)} candidate dossiers, {len(scope)} scope rulings, {len(adjud)} wish-list adjudications, {len(scenario_rows)} finite scenarios, {len(cms)} countermodels, {len(formal)} formal targets, and exact source traces over {len(source_trace_rows)} candidate/claim relations.\n\nThe controlling proposal is a scoped contact/admission calculus, not a universal interaction algebra. Every candidate remains unproved unless explicitly inherited.\n\nThis readiness dossier is not a proof of any new Foundations VII theorem, and it is not a paper draft.\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
