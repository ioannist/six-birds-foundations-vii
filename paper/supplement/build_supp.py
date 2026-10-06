#!/usr/bin/env python3
"""Generate the supplement tables of Foundations VII from the release registries
and the Lean sources.  Run from the repository root:

    python3 paper/supplement/build_supp.py

Every row is derived from science/registry/final_*.jsonl or from the Lean files
under formalization/lean; nothing is typed by hand except the map from
main-paper items to their Lean declarations (ITEMS below).
"""
import json, re, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
REG = ROOT / "science" / "registry"
LEAN = ROOT / "formalization" / "lean"
OUT = pathlib.Path(__file__).resolve().parent


def load(name):
    return [json.loads(l) for l in open(REG / f"{name}.jsonl") if l.strip()]


DECLS = {d["fully_qualified_name"]: d for d in load("final_public_declarations")}

# Semantic modules are newer than the registries: locate them in the source.
SEM = {}
for f in sorted((LEAN / "FoundationsVII" / "Semantics").glob("*.lean")):
    rel = f.relative_to(ROOT).as_posix()
    ns_stack = ["FoundationsVII", "Semantics"]
    for i, line in enumerate(f.read_text().splitlines(), 1):
        m = re.match(r"namespace (\S+)", line)
        if m and m.group(1) != "FoundationsVII.Semantics":
            ns_stack.append(m.group(1))
            continue
        m = re.match(r"end (\S+)", line)
        if m and len(ns_stack) > 2 and m.group(1) == ns_stack[-1]:
            ns_stack.pop()
            continue
        m = re.match(r"(?:private |noncomputable |protected )*(theorem|def|structure|inductive|instance|abbrev)\s+([^\s:({\[]+)", line)
        if m and m.group(2) and not line.startswith("private"):
            kind, nm = m.group(1), m.group(2)
            fq = ".".join(ns_stack + [nm])
            SEM[fq] = {"kind": kind, "path": rel, "line": i}


def where(fq):
    if fq in DECLS:
        d = DECLS[fq]
        return d["kind"], d["path"], d["line"]
    if fq in SEM:
        d = SEM[fq]
        return d["kind"], d["path"], d["line"]
    return None


def tex(s):
    s = s.replace("\\", "\\textbackslash{}")
    for a, b in [("&", "\\&"), ("%", "\\%"), ("$", "\\$"), ("#", "\\#"), ("_", "\\_"),
                 ("{", "\\{"), ("}", "\\}"), ("~", "\\textasciitilde{}"), ("^", "\\^{}")]:
        s = s.replace(a, b)
    s = s.replace("\\textbackslash\\{\\}", "\\textbackslash{}")
    return s


def path(s):
    return "\\path{" + s + "}"


S = "FoundationsVII.Semantics."
F = "FoundationsVII."

# Main-paper numbered items -> (catalog identifiers, Lean declarations).
ITEMS = [
    ("def:semantic-join", "new", [S+"TheoryPackage", S+"SemanticJoin", S+"PackageJoin"]),
    ("def:factorization", "new", [S+"Factors", S+"FactorsOnImage", S+"SplitPair", S+"factors_implies_onImage"]),
    ("thm:split-criterion", "new", [S+"factorsOnImage_iff_no_split", S+"FiniteSplitCheck", S+"finiteSplitCheck_correct"]),
    ("def:strict-observable", "new", [S+"StrictObservable"]),
    ("thm:strict-split", "new", [S+"strict_iff_split_pairs"]),
    ("ex:cube", "new", [S+"cubeJoin", S+"cubeObservable", S+"cube_strict", S+"cube_first_not_strict"]),
    ("def:common-refinement", "new", [S+"CommonRefinement"]),
    ("prop:refinement", "new", [S+"factors_through_pair_of_refinement"]),
    ("rem:refinement-limit", "new", [S+"identity_refinement_recovers_cube"]),
    ("def:cheap", "new", [S+"RelabelOnly", S+"SchedulingOnly", S+"CoarseningOnly"]),
    ("prop:strict-not-cheap", "new", [S+"split_composition", S+"strict_not_relabel", S+"strict_not_coarsening"]),
    ("thm:bridge", "VII-C009 (semantic)", [S+"SemanticStrictEvidence", S+"semanticFlag", S+"strictCertificate", S+"strictCertificate_valid", S+"cubeCertificate_valid"]),
    ("def:rewriting", "new", [S+"Star", S+"Joinable", S+"LocallyConfluent", S+"Confluent", S+"Terminates", S+"Normal"]),
    ("thm:newman", "new", [S+"newman"]),
    ("cor:normal-forms", "new", [S+"normal_star_eq", S+"normal_forms_unique", S+"unique_reachable_normal"]),
    ("prop:finite-peaks", "new", [S+"finiteReachCheck_correct", S+"finiteJoinCheck_correct", S+"finitePeakCheckComplete_correct", S+"finitePeakCheckFin_correct"]),
    ("rem:graph-search", "new", []),
    ("ex:four-state", "new", [S+"fourStep", S+"four_local", S+"four_not_confluent"]),
    ("def:admission-system", "new", [S+"AdmissionRules", S+"AdmissionRules.Enabled", S+"AdmissionRules.Step"]),
    ("thm:admission", "VII-C018 (semantic)", [S+"AdmissionRules.terminates", S+"AdmissionRules.commuting_admissions", S+"AdmissionRules.locallyConfluent", S+"AdmissionRules.confluent", S+"AdmissionRules.unique_fixed_point", S+"AdmissionRules.star_preserves_nodup"]),
    ("ex:disabling", "new", [S+"disablingStep", S+"disabling_terminates", S+"disabling_not_local", S+"disabling_two_fixed_points"]),
    ("ex:free-admission", "new", [S+"freeRules", S+"free_example"]),
    ("prop:enablement-model", "VII-C034 (semantic)", [S+"lowerStep", S+"reachableVector", S+"form", S+"upperStep", S+"form_injective", S+"upper_step_iff_lower", S+"three_distinct_upper_states", S+"nontrivial_upper_formation", S+"enabled_not_descended", S+"observable_descends_of_fibre_constant"]),
    ("prop:no-free-join", "VII-C035 (semantic)", [S+"EventSystem", S+"Lawful", S+"sole_producer_join_absent", S+"external_source_allows_join"]),
    ("prop:selection", "VII-C015 (semantic)", [S+"select", S+"SelectionStep", S+"selection_run_preserves", S+"insertion_not_selection"]),
    ("prop:search", "VII-C021, VII-C033 (semantic)", [S+"ReachWithin", S+"detect", S+"detector_sound", S+"detector_coverage", S+"beyond_horizon_null", S+"no_contact_with_one_use", S+"contact_with_two_uses"]),
    ("ex:cube-certificate", "VII-C009 (semantic)", [S+"strictCertificate", S+"strictCertificate_valid", S+"cubeCertificate_valid"]),
    ("def:access", "VII-C001", [F+"DomainState", F+"DomainState.Coherent", F+"DomainState.normalForm_eq"]),
    ("def:contact", "VII-C016", [F+"ContactSurface", F+"ContactWitness", F+"ContactMode", F+"ContactChannelEvidence.rendezvous_licensed"]),
    ("def:join-status", "VII-C008", [F+"JoinStatus", F+"JoinAssessment.classify", F+"Models.Finite.Phase3.status_partition_complete"]),
    ("def:strict-certificate", "VII-C009", [F+"StrictJoinEvidence.Certified", F+"AntiProductWitness.Valid", F+"StrictJoinEvidence.certified_has_anti_product_novelty", F+"AntiProductWitness.valid_is_nonfactorizing"]),
    ("def:enablement", "VII-C012, VII-C013", [F+"EnablementRecord", F+"AttributedEnablement.WellFormed", F+"EndogenousEnablementProfile.Eligible", F+"EndogenousEnablementProfile.eligible_iff_exact_criterion"]),
    ("def:route", "VII-C017", [F+"RouteComparison.Holonomy", F+"constructive_interaction_holonomy", F+"holonomy_with_zero_arrow_witness"]),
    ("def:drive", "VII-C032", [F+"DriveCertificate.Valid", F+"ArrowClaim.Eligible", F+"driven_arrow_requires_independent_drive_certificate", F+"CrossTimeContact.Valid"]),
    ("prop:bootstrap", "VII-C003, NGVII-01", [F+"AdmissionRegime.no_first_extension_without_seed_or_reachable_generator", F+"NoGo.NGVII_01_escape_admitted_seed", F+"NoGo.NGVII_01_escape_reachable_generator", F+"NoGo.NGVII_01_escape_open_external_provision"]),
    ("rem:refinement-refuted", "VII-C030", [F+"RefinementEffect", F+"no_unconditional_join_monotonicity_under_refinement", F+"refinement_effects_have_all_four_controls"]),
    ("rem:degree-refuted", "VII-C031", [F+"ContactQuantityTransformation.Conserved", F+"plausible_contact_quantities_disagree", F+"omitted_observer_occupancy_invalidates_conservation_credit", F+"exact_scoped_contact_conservation_is_available"]),
    ("rem:deferral-categorical", "VII-C026", [F+"UniversalConstructionCertificate.RepresentsStrictJoin", F+"mere_product_is_not_strict_join_credit", F+"special_case_categorical_representation_is_conditional"]),
    ("rem:deferral-algebra", "VII-C028", [F+"AlgebraReadiness.Ready", F+"full_generators_relations_program_deferred_with_formal_reopen_condition", F+"resource_delta_fragment_is_associative"]),
]

missing = []
rows = []
for label, ident, decls in ITEMS:
    cells = []
    for d in decls:
        w = where(d)
        if w is None:
            missing.append(d)
            continue
        kind, p, line = w
        short = d.replace("FoundationsVII.", "")
        cells.append(f"\\path{{{short}}} ({kind}) \\newline {path(p)}:{line}")
    if not decls:
        cells = ["paper-only algorithmic observation; no Lean declaration"]
    rows.append(f"\\Cref{{{label}}} & {tex(ident)} & {' \\newline '.join(cells)} \\\\")
if missing:
    sys.exit("missing declarations: " + ", ".join(missing))
# Completeness: every numbered item of the main paper has exactly one concordance row.
# closed_over: numbered environments in paper/sections and their labels in build/main.aux.
# wrong_if: a numbered item is added, removed or relabelled without updating ITEMS.
NUMBERED = ("theorem", "proposition", "corollary", "lemma", "definition", "example", "remark")
_secs = OUT.parent / "sections"
_moved = [OUT / "supp_certificates.tex"]
_envs = sum(len(re.findall(r"\\begin\{(" + "|".join(NUMBERED) + r")\}", f.read_text()))
            for f in sorted(_secs.glob("*.tex")) + _moved)
_aux = (OUT.parent / "build" / "main.aux").read_text()
_labels = set(re.findall(r"\\newlabel\{((?:thm|prop|cor|lem|def|ex|rem):[^}@]+)\}", _aux))
_labels |= set(re.findall(r"\\label\{((?:thm|prop|cor|lem|def|ex|rem):[^}]+)\}", "".join(f.read_text() for f in _moved)))
_items = [label for label, _, _ in ITEMS]
if len(_items) != len(set(_items)) or set(_items) != _labels or len(_items) != _envs:
    sys.exit(f"concordance mismatch: rows {len(_items)}, numbered environments {_envs}, "
             f"missing {sorted(_labels - set(_items))}, extra {sorted(set(_items) - _labels)}")
(OUT / "concordance_rows.tex").write_text("\n".join(rows) + "\n")

# ---- Register of the 36 catalog entries --------------------------------------
PLACE = {
    "VII-C001": "def:access", "VII-C002": "sec:certificates", "VII-C003": "prop:bootstrap",
    "VII-C004": "sec:sep-definitional", "VII-C005": "sec:sep-separations", "VII-C006": "sec:certificates",
    "VII-C007": "sec:certificates", "VII-C008": "def:join-status", "VII-C009": "def:strict-certificate",
    "VII-C010": "sec:certificates", "VII-C011": "sec:certificates", "VII-C012": "def:enablement",
    "VII-C013": "sec:sep-definitional", "VII-C014": "sec:certificates", "VII-C015": "sec:sep-definitional",
    "VII-C016": "sec:sep-separations", "VII-C017": "def:route", "VII-C018": "sec:sep-definitional",
    "VII-C019": "sec:certificates", "VII-C020": "sec:certificates", "VII-C021": "sec:sep-definitional",
    "VII-C022": "sec:certificates", "VII-C023": "sec:certificates", "VII-C024": "sec:setting-kinds",
    "VII-C025": "sec:ttw", "VII-C026": "rem:deferral-categorical", "VII-C027": "sec:sep-definitional",
    "VII-C028": "rem:deferral-algebra", "VII-C029": "sec:sep-refusals", "VII-C030": "rem:refinement-refuted",
    "VII-C031": "rem:degree-refuted", "VII-C032": "def:drive", "VII-C033": "sec:sep-definitional",
    "VII-C034": "sec:sep-separations", "VII-C035": "sec:sep-refusals", "VII-C036": "sec:sep-definitional",
}
READING = {
    "VII-C003": "consequence of definitions (\\Cref{prop:bootstrap})",
    "VII-C004": "definition; authorization does not use neutrality",
    "VII-C005": "separations and a refusal",
    "VII-C009": "definition; semantic counterpart \\Cref{thm:bridge}",
    "VII-C013": "definition read as an equivalence",
    "VII-C015": "consequence of the definition; semantic counterpart \\Cref{prop:selection}",
    "VII-C016": "separation (existence of transport without a composite)",
    "VII-C017": "definition; separation from the arrow",
    "VII-C018": "reformulation; semantic counterpart \\Cref{thm:admission}",
    "VII-C021": "certificate definition; semantic counterpart \\Cref{prop:search}",
    "VII-C025": "decidable finite statement",
    "VII-C027": "associativity unconditional; credit needs composability",
    "VII-C029": "refusal",
    "VII-C032": "refusal without a drive certificate",
    "VII-C033": "certificate definition; semantic counterpart \\Cref{prop:search}",
    "VII-C034": "separation profiles",
    "VII-C035": "refusals; first clause \\Cref{prop:no-free-join}",
    "VII-C036": "recorded attribution",
    "VII-C030": "refuted; four-way classification",
    "VII-C031": "two scalars disagree",
    "VII-C026": "deferred; checklist only",
    "VII-C028": "deferred; monoid of resource deltas",
}
DISP = {
    "FORMAL_SCHEMA": "formal schema", "CONDITIONAL_THEOREM": "conditional theorem",
    "REFUTED_CANDIDATE": "refuted candidate", "CLOSED_DEFERRAL": "closed deferral",
    "CONSTRUCTIVE_COUNTERMODEL": "constructive countermodel", "LEAN_DECIDABLE_FINITE": "decidable finite",
}
BAN = re.compile(r"step[- ]?3|dossier|landed|phase|frozen|pre-?ship|handoff", re.I)

def clean_list(xs):
    return [x for x in xs if not BAN.search(x)]

ESTABLISHED = {
    "VII-C001": "Defines the seven-coordinate access record and its coherence spine. Each failed converse has a coherent witness in the reference world.",
    "VII-C002": "Defines five typed admission transitions, each requiring source, budget, guard and audit witnesses, with a typed effect on admissibility.",
    "VII-C003": "In a closed regime with no admitted seed and no reachable generator no first extension is authorized; this follows from the definition of authorization. Each of the three escape routes is realized by a regime record.",
    "VII-C004": "Defines the neutral-provisioning certificate and refuses neutral credit to retrospectively stocked or relabelled system-generated seeds. Authorization of a first extension does not use neutrality.",
    "VII-C005": "Exhibits access records with the same origin, carrier and instrument and different access fields, and a record with shared access and a common source; a shared lineage fails the independence gate by definition.",
    "VII-C006": "Defines the prospective-commitment record; a use registered after its evidence cannot discharge the prospective certificate.",
    "VII-C007": "Defines the join-entry record. A well-formed record does not establish that a join exists.",
    "VII-C008": "Defines seven join statuses; over each declared finite interface family the classifier assigns exactly one, checked by enumeration.",
    "VII-C009": "Defines the strict-join certificate; its necessity clauses are projections of recorded fields. Semantic counterpart: main paper, \\Cref{thm:strict-split} and \\Cref{thm:bridge}, which cover the parents and their pairing but not every common refinement (\\Cref{rem:refinement-limit}).",
    "VII-C010": "Defines the source-independence gate; behavioural non-factorization alone does not earn independence-sensitive credit.",
    "VII-C011": "Defines the join ledger; an entry is credited when payments plus refunds cover its amount, or when its amount is zero on a certified zero-cost channel.",
    "VII-C012": "Defines the enablement record with its attribution field; a hidden executor defeats attribution.",
    "VII-C013": "The endogeny criterion is the definition read as an equivalence. The two hidden-executor controls each satisfy every other condition.",
    "VII-C014": "Defines the birth record; a contact record can be marked relation-only.",
    "VII-C015": "Defines transmission records; for a pure downward selection the conclusion that no lower fact is created is contained in the definition.",
    "VII-C016": "Exhibits a well-formed peer-transport record marked as forming no composite.",
    "VII-C017": "Defines route residue for two route results; exhibits a comparison record with residue and no arrow credit.",
    "VII-C018": "Relates two predicates on the same critical-pair records; this is a reformulation and proves no path confluence. Exhibits a seed-partition record whose two terminal-package fields are unequal. Semantic counterpart: main paper, \\Cref{thm:admission}, which gives a unique terminal state from each state when admission only enables, and \\Cref{ex:disabling}.",
    "VII-C019": "Defines the append-only residual ledger with inherited, dissolved and join-created classes; scope changes do not delete residuals silently.",
    "VII-C020": "Defines the bridge contract; a citation alone does not license transport.",
    "VII-C021": "Defines the operational profile and the horizon-qualified negative certificate; reachability alone does not give occurrence.",
    "VII-C022": "Defines interface coordinates for determination, exposure, recoverability and admissibility; equal determination can have different exposure.",
    "VII-C023": "Defines the negative-evidence record; a point null does not license an unrestricted negative.",
    "VII-C024": "Defines the grade record; finite evidence does not upgrade a claim's grade.",
    "VII-C025": "Over the 24 scenarios and 27 named countermodels the detector contract is well formed and complete and every expected status is decided; checked by evaluation.",
    "VII-C026": "Deferred. The categorical certificate is a checklist of flags and supports no categorical statement; a mere product earns no strict-join credit.",
    "VII-C027": "Resource deltas combine associatively with an identity for all inputs; composability governs credit. Exhibits a two-link chain record whose composed values differ with order.",
    "VII-C028": "Deferred; the resource-delta fragment is a monoid.",
    "VII-C029": "Native or endogenous credit is refused while charged occupancy is below actual occupancy; external observer and zero occupancy are escapes.",
    "VII-C030": "Refuted at the level of records: a well-formed refinement record labelled destroys exists, so unconditional preservation is not permitted. All four effect labels occur among the records of the declared carrier; no model of refinement acting on a join is given.",
    "VII-C031": "Two particular scalar degrees disagree on one vector, and an apparent conservation omitting observer occupancy fails the accounting certificate. Nothing universal is proved.",
    "VII-C032": "An arrow claim requires a drive certificate; exhibits a comparison record with residue and no arrow credit. Cross-time contact requires a synchronization or partial-order witness.",
    "VII-C033": "Defines the coverage certificate for non-interaction; a declared exhaustive family excludes contact within that family only.",
    "VII-C034": "Exhibits Boolean separation profiles: load-bearing enablement with no recorded descent, and a necessary but insufficient enabler.",
    "VII-C035": "Payment and relabelling refusals follow from the ledger and anti-product definitions. The first clause, that a join cannot create its own first capability, is \\Cref{prop:no-free-join} of the main paper.",
    "VII-C036": "The ledger can record a transition that discharges one inherited residual and marks one new residual as join-created. The mark is recorded, not derived from a model of a join.",
}
cands = load("final_candidate_closure")
assert set(ESTABLISHED) == {c["candidate_id"] for c in cands}
# Cross-references into the main paper must be labels, never hard-coded numbers.
NUMREF = re.compile(r"(Theorem|Example|Proposition|Definition|Remark|Corollary|Lemma|Section|Table)s?[~ ]+S?[0-9]")
for _d in (READING, ESTABLISHED, PLACE):
    for _k, _v in _d.items():
        assert not NUMREF.search(_v), f"hard-coded number in {_k}: {_v}"

reg = []
for c in cands:
    cid = c["candidate_id"]
    disp = DISP.get(c["terminal_disposition"], c["terminal_disposition"].lower())
    reading = READING.get(cid, "definition")
    ev = []
    if c.get("finite_assay_ids"): ev.append("assays " + ", ".join(c["finite_assay_ids"]))
    if c.get("countermodels"): ev.append("countermodels " + ", ".join(c["countermodels"]))
    ev.append(f"{len(c.get('lean_declarations', []))} Lean declarations")
    reg.append(f"{tex(cid)} \\newline {tex(c['name'])} & {reading} \\newline \\Cref{{{PLACE[cid]}}} & {ESTABLISHED[cid]} & {tex('; '.join(ev))} \\\\")
(OUT / "register_rows.tex").write_text("\n".join(reg) + "\n")
nc = []
for c in cands:
    items = clean_list(c.get("nonclaims", [])) + [e for e in clean_list(c.get("escape_routes", []))]
    ncl = [re.sub(r" in Step ?3", "", n).replace("a P6 arrow", "an arrow").replace("The theorem is scoped", "The statement is scoped") for n in c.get("nonclaims", [])]
    ncl = clean_list(ncl)
    esc = clean_list(c.get("escape_routes", []))
    txt = " ".join(tex(n if n.endswith('.') else n + '.') for n in ncl)
    etxt = " ".join(tex(n if n.endswith('.') else n + '.') for n in esc)
    nc.append(f"{tex(c['candidate_id'])} & {txt} & {etxt} \\\\")
(OUT / "nonclaim_rows.tex").write_text("\n".join(nc) + "\n")

# ---- No-go register -----------------------------------------------------------
ng = load("final_no_go_closure")
# The zero-cost escape credits a join of amount zero, not a positive-cost one (Join/Budget.lean:32).
NOGO_NAME = {"NGVII-09": "No positive-cost join credit without payment; a zero-cost join on a certified zero-cost channel is credited without payment"}
rows = []
for n in ng:
    esc = " \\newline ".join(path(e.replace("FoundationsVII.NoGo.", "")) for e in n["escape_theorems"])
    name = NOGO_NAME.get(n["no_go_id"], n["name"])
    rows.append(f"{tex(n['no_go_id'])} & {tex(name)} & {tex(', '.join(n['candidate_ids']))} & {esc} \\\\")
(OUT / "nogo_rows.tex").write_text("\n".join(rows) + "\n")

# ---- Corollaries -------------------------------------------------------------
co = load("final_corollaries")
rows = []
for c in co:
    short = c["declaration"].split(".")[-1]
    rows.append(f"{tex(c['corollary_id'])} & {path(short)} & {tex(', '.join(x.replace('VII-','') for x in c['candidate_ids']))} & {path(c['path'])}:{c['line']} \\\\")
(OUT / "corollary_rows.tex").write_text("\n".join(rows) + "\n")

# ---- Assays -------------------------------------------------------------------
GROUP = {"2": "Access and admission", "3": "Contact and join", "4": "Enablement and dynamics", "5": "Integration across clusters"}
assays = load("final_finite_assays")
out = []
for g in "2345":
    sub = [a for a in assays if a["family_id"].startswith(f"P{g}-")]
    sub.sort(key=lambda a: a["family_id"])
    out.append(f"\\multicolumn{{5}}{{@{{}}l}}{{\\emph{{{GROUP[g]}}}}}\\\\")
    for a in sub:
        desc = BAN.sub("", a["description"]).strip()
        n = lambda v: f"{v:,}".replace(",", "{,}")
        out.append(f"{tex(a['family_id'])} & {n(a['raw_cardinality'])} & {n(a['canonical_cardinality'])} & {n(a['accepted_cardinality'])} & {tex(desc)} \\\\")
    out.append("\\midrule")
head = r"""{\scriptsize
\begin{longtable}{@{}lrrr>{\raggedright\arraybackslash}p{8.2cm}@{}}
\caption{Finite assays.}\label{tab:assays}\\
\toprule
\textbf{Assay} & \textbf{Raw} & \textbf{Canon.} & \textbf{Acc.} & \textbf{Family} \\
\midrule
\endfirsthead
\toprule
\textbf{Assay} & \textbf{Raw} & \textbf{Canon.} & \textbf{Acc.} & \textbf{Family} \\
\midrule
\endhead
\bottomrule
\endfoot
"""
(OUT / "assay_table.tex").write_text(head + "\n".join(out[:-1]) + "\n\\end{longtable}\n}\n")
tot = {k: sum(a[k] for a in assays) for k in ("raw_cardinality", "canonical_cardinality", "accepted_cardinality", "rejected_cardinality")}
print("assay totals", tot, "count", len(assays))

# ---- Countermodels --------------------------------------------------------------
cms = [c for c in load("final_countermodels") if c["countermodel_kind"] == "NAMED_REFERENCE_COUNTERMODEL"]
cms.sort(key=lambda c: int(c["countermodel_id"].split("-")[1]))
rows = []
for c in cms:
    rows.append(f"{tex(c['countermodel_id'])} & {tex(c['name'])} & {tex(c['shows'])} & {tex(c['scenario_id'])} \\\\")
(OUT / "countermodel_rows.tex").write_text("\n".join(rows) + "\n")
print("countermodels", len(cms))

# ---- Certificate field lists from the Lean structures ------------------------------
STRUCTS = ["DomainState", "AdmissionRegime", "TypedAdmissionStep", "NeutralProvisioningCertificate",
           "ProspectiveCommitment", "BridgeContract", "ContactSurface", "JoinEntryRecord",
           "StrictJoinEvidence", "AntiProductWitness", "SourceIndependenceGate", "JoinCostEntry",
           "JoinPaymentLedger", "ObserverOccupancyRecord", "EnablementRecord", "TransmissionRecord",
           "OperationalProfile", "NegativeEvidenceRecord", "ContactCoverageCertificate",
           "RouteComparison", "DriveCertificate", "ResidualEntry", "ResidualLedger",
           "ContactQuantityTransformation"]
found = {}
for f in sorted((LEAN / "FoundationsVII").rglob("*.lean")):
    if "Semantics" in f.parts:
        continue
    lines = f.read_text().splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"structure (\w+)", line)
        if m and m.group(1) in STRUCTS and m.group(1) not in found:
            fields = []
            for l2 in lines[i+1:]:
                if not l2.startswith("  ") or l2.strip().startswith("deriving"):
                    break
                fm = re.match(r"\s+(\w+)\s*:\s*(.+)", l2)
                if fm:
                    fields.append((fm.group(1), fm.group(2).strip()))
            found[m.group(1)] = (f.relative_to(ROOT).as_posix(), i + 1, fields)
lost = [s for s in STRUCTS if s not in found]
if lost:
    print("structures not found:", lost)
out = []
for s in STRUCTS:
    if s not in found:
        continue
    p, line, fields = found[s]
    fl = "; ".join(f"\\path{{{a}}}" for a, _ in fields)
    out.append(f"\\path{{{s}}} \\newline {path(p)}:{line} & {len(fields)} & {fl} \\\\")
(OUT / "field_rows.tex").write_text("\n".join(out) + "\n")

# ---- Axioms of the semantic modules --------------------------------------------------
rep = (LEAN / "SEMANTICS_REPORT.md").read_text()
block = "\n".join(part.split("```")[0] for part in rep.split("```text")[1:])
block = re.sub(r",\n\s*", ", ", block)
rows = []
for l in block.strip().splitlines():
    m = re.match(r"'(?:_private\._stdin\.0\.)?FoundationsVII\.Semantics\.([^']+)' (.*)", l)
    if not m:
        continue
    nm, rest = m.groups()
    ax = "none" if "does not depend" in rest else re.search(r"\[(.*)\]", rest).group(1)
    rows.append(f"\\path{{{nm}}} & {tex(ax)} \\\\")
(OUT / "semantic_axiom_rows.tex").write_text("\n".join(rows) + "\n")
print("semantic theorems", len(rows), "concordance items", len(ITEMS), "register", len(reg))
