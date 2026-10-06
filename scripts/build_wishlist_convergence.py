#!/usr/bin/env python3
"""Create a provenance-preserving convergence map across the four wish lists."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "wishlists"
ATOMS = list(csv.DictReader((OUT / "atomic_requests.csv").open(newline="", encoding="utf-8")))

GROUPS: dict[str, tuple[str, str, list[str]]] = {
    "CG01": ("Domain founding and status ladder", "Accessible-domain founding, width, and the separation of expressible, present, reachable, and occurrent.", ["ARC-H1","ARC-H8","MM-STATUS"]),
    "CG02": ("Admission kinds and lawful domain transition", "Typed admission mechanisms, retraction/rollback, and the difference between well-formed and substrate-admissible operations.", ["ARC-H2","ARC-H7","CLD-D3"]),
    "CG03": ("Bootstrap, seeding, and no-free access", "First-extension obstruction, minimum seeds, neutral provisioning, capability expressivity, and anti-smuggling of access.", ["ARC-H3","ARC-H4","ARC-NG1","MM-BOOT","MM-SEED","MM-NG1","MED-S4"]),
    "CG04": ("Prospective commitment and temporal admissibility", "Preregistered admission, timing, finite commitment budgets, and prohibition of retrospectively self-certifying predictions.", ["ARC-H6","ARC-H22","ARC-NG3","ARC-H27"]),
    "CG05": ("Partial access and non-transfer from common origin", "Shared origin does not establish shared access, and total-lens results do not transfer automatically to partial self-owned domains.", ["ARC-H5","ARC-NG4"]),
    "CG06": ("Join entry and record normal form", "Minimum typed records, licensing controls, contact surfaces, and pending states required to enter a join calculus.", ["ARC-H9","CLD-O2","MM-JOINNF","MED-D1","MED-I5"]),
    "CG07": ("Join existence, obstruction, and certified non-interaction", "Existence criteria, obstruction taxonomies, join statuses, no-common-package cases, and attribution of failure.", ["ARC-H10","ARC-H21","CLD-A1","CLD-E3","MED-D2","MED-T3","MED-T7"]),
    "CG08": ("Strict joint novelty and anti-manufacture", "Anti-product witnesses, strictness over parents, and no manufacture of joint content by relabeling or undeclared operations.", ["ARC-H11","CLD-A4","CLD-E2","MED-T1","MED-NG1"]),
    "CG09": ("Source independence and native parent evidence", "Ancestry independence, native versus bridged records, and controls against same-lineage or common-source fake joins.", ["ARC-H12","ARC-NG2","MM-INDEP","MM-NG2","MED-NG2","MED-S1"]),
    "CG10": ("Join currency, payment, and resource bounds", "Join cost, cross-costs, confluence prices, zero-cost no-gos, and finite bounds on simultaneously live joins.", ["ARC-H13","CLD-A3","CLD-E1","MM-OP1","MED-NG4","MED-NG5"]),
    "CG11": ("Contact modes, peer transport, and interaction without join", "Rendezvous, local contact, sequential transport, shared carriers/budgets, and middle states short of joint objecthood.", ["ARC-H19","ARC-H20","MM-LOCAL","MM-OP3","MED-D3","MED-T4"]),
    "CG12": ("Categorical reduction of join", "Whether and under what hypotheses the interaction join reduces to a product, pullback, or related categorical construction.", ["CLD-A2"]),
    "CG13": ("Parent refinement, retention, and descent through join", "Whether parent refinement destroys joins and which laws/records survive or are lost after joining.", ["MED-T2","MED-T6"]),
    "CG14": ("Enablement definition, attribution, and endogeny", "Enablement versus descent/causation, who performs closure, endogenous execution, necessary-but-insufficient enabling, and observer certification.", ["ARC-H14","ARC-H15","CLD-O3","CLD-C1","CLD-C2","CLD-C3","MED-B3"]),
    "CG15": ("Birth classes, contact-surface birth, and reachability", "Reconciliation of layer-birth classes, join-created participants, undergoing versus performing closure, and finite expressivity required for birth.", ["ARC-H16","MM-OP4","MED-B1","MED-B2"]),
    "CG16": ("Enablement-chain composition", "Composition, accumulated budget, residual, and holonomy along chains of enabling relations.", ["CLD-C4"]),
    "CG17": ("Upward/downward transmission and descent fidelity", "Typed payload flow, construction direction, descent loss, structural selection, and limits on top-down creation claims.", ["ARC-H17","ARC-H18","CLD-O4","CLD-B2","MED-D4","MED-NG3","MED-UP"]),
    "CG18": ("Confluence, construction routes, and seed dependence", "Whole-construction confluence, critical pairs, and dependence of fixed points on initial partitions or admission routes.", ["ARC-H24","CLD-B1","CLD-B3"]),
    "CG19": ("Join order, associativity, and interaction holonomy", "Order/bracketing sensitivity, route residue, obstruction from A-then-B versus B-then-A, and absence of a global potential.", ["ARC-H23","ARC-H25","CLD-A5","CLD-E4","MM-OP2","MED-H1","MED-H2"]),
    "CG20": ("Interaction arrow, consistency, irreversibility, and simultaneity", "Null-versus-driven controls, irreversible joining, mutually constraining fixed points, and contact across incommensurable internal times.", ["MED-CIRC","MED-H3","MED-H4","MED-H5"]),
    "CG21": ("Exposure, recoverability, admissibility, and rigidity", "Determination versus exposure/recovery, overread, operational admissibility, privilege, and genuine versus spurious rigidity.", ["ARC-S3","CLD-O1","CLD-D1","CLD-D2","CLD-D4"]),
    "CG22": ("Needles, residuals, and obstruction dissolution", "How access and joins dissolve, preserve, or manufacture obstructions and how residual/cross-term accounting behaves.", ["ARC-H26","ARC-H28","MED-N1","MED-N2","MED-N3","MED-N4"]),
    "CG23": ("Observer and instrument occupancy", "Budgeted probes, observer consumption of shared capacity, and detector source/visibility/capacity preconditions.", ["MM-OBSERVER","MM-NG3","MED-I3"]),
    "CG24": ("Bridge, transport, and withdrawal discipline", "Applicability certificates, source-to-target maps, claim dependencies, and append-only correction/withdrawal records.", ["ARC-S1","MM-BRIDGE","MM-WITHDRAW","MED-D5","MED-M1","MED-M2","MED-M3"]),
    "CG25": ("Reachability, non-vacuity, horizon, and guard activity", "A sound mechanism must be executable and reachable; horizon-limited non-occurrence and inactive guards have limited evidentiary force.", ["ARC-S2","ARC-S6","MM-HORIZON","MED-S6"]),
    "CG26": ("Negative-result quantifiers", "What one point, an exhaustive search, or a closed-family negative may falsify.", ["ARC-S4","MM-NG4","MED-S5"]),
    "CG27": ("Claim grades, specification discipline, and non-goals", "Normative-specification fidelity, necessary/sufficient labels, explicit scope, countermodels, and exclusions against redoing or universalizing prior work.", ["ARC-S5","ARC-NONGOALS","CLD-DISC","MM-NONGOAL","MED-S3"]),
    "CG28": ("Detector, null, falsifier, and Two-Theory World", "Detection contracts, append-only join evidence, null batteries, asymmetric false-positive costs, and the finite laboratory.", ["ARC-LAB","MED-I1","MED-I2","MED-I4","MED-S2"]),
    "CG29": ("Primitive generators and relations", "Whether a primitive-operation algebra is ready or should be explicitly deferred.", ["CLD-F"]),
    "CG30": ("Conserved contact degree", "Whether any quantity or degree is conserved across joining, without assuming that one exists.", ["MED-T5"]),
}

atom_by_id = {r["request_id"]: r for r in ATOMS}
assigned: dict[str, str] = {}
for gid, (_title, _scope, ids) in GROUPS.items():
    for rid in ids:
        if rid not in atom_by_id:
            raise SystemExit(f"Unknown request ID in {gid}: {rid}")
        if rid in assigned:
            raise SystemExit(f"Duplicate convergence assignment: {rid} in {assigned[rid]} and {gid}")
        assigned[rid] = gid
missing = sorted(set(atom_by_id) - set(assigned))
extra = sorted(set(assigned) - set(atom_by_id))
if missing or extra:
    raise SystemExit(f"Convergence map incomplete: missing={missing} extra={extra}")

rows: list[dict[str, str]] = []
for atom in ATOMS:
    gid = assigned[atom["request_id"]]
    title, scope, _ids = GROUPS[gid]
    rows.append({
        "convergence_group": gid,
        "group_title": title,
        "group_scope": scope,
        "request_id": atom["request_id"],
        "source_code": atom["source_code"],
        "source_file": atom["source_file"],
        "source_line": atom["source_line"],
        "cluster": atom["cluster"],
        "step1_disposition": atom["step1_disposition"],
        "atomic_request": atom["atomic_request"],
    })
with (OUT / "convergence_groups.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

md = [
    "# Provenance-preserving wish-list convergence map",
    "",
    "The 130 atomic requests are grouped into 30 provisional convergence fronts. Grouping means ‘these requests should be adjudicated together’; it does **not** declare the requests equivalent, true, mutually consistent, or already established. Every atom retains its source file and line.",
    "",
]
for gid in sorted(GROUPS):
    title, scope, ids = GROUPS[gid]
    group_rows = [atom_by_id[rid] for rid in ids]
    sources = Counter(r["source_code"] for r in group_rows)
    dispositions = Counter(r["step1_disposition"] for r in group_rows)
    md += [
        f"## {gid} — {title}",
        "",
        scope,
        "",
        f"- **Atoms:** {len(ids)} — " + ", ".join(f"`{rid}`" for rid in ids) + ".",
        "- **Source coverage:** " + ", ".join(f"{k}={v}" for k, v in sorted(sources.items())) + ".",
        "- **Provisional dispositions:** " + ", ".join(f"{k}={v}" for k, v in sorted(dispositions.items())) + ".",
        "",
    ]
(OUT / "CONVERGENCE_MAP.md").write_text("\n".join(md) + "\n", encoding="utf-8")

# Add an idempotent cross-reference to the main wish-list synthesis.
syn_path = OUT / "WISHLIST_SYNTHESIS_STEP1.md"
syn = syn_path.read_text(encoding="utf-8")
start = "<!-- CONVERGENCE-MAP:BEGIN -->"
end = "<!-- CONVERGENCE-MAP:END -->"
import re
syn = re.sub(r"\n<!-- CONVERGENCE-MAP:BEGIN -->.*?<!-- CONVERGENCE-MAP:END -->\n", "\n", syn, flags=re.S)
block = f"""
<!-- CONVERGENCE-MAP:BEGIN -->
## Provenance-preserving merge

The **130** source-located atoms are additionally organized into **{len(GROUPS)} provisional convergence groups** in `CONVERGENCE_MAP.md` and `convergence_groups.csv`. This merges overlapping work fronts without deleting provenance or pretending that similarly worded requests are equivalent. Singleton groups remain where a question is genuinely distinct or explicitly open.
<!-- CONVERGENCE-MAP:END -->
"""
marker = "\n## Step-2 use"
if marker in syn:
    syn = syn.replace(marker, block + marker, 1)
else:
    syn += block
syn_path.write_text(syn, encoding="utf-8")
print(f"atoms={len(ATOMS)} convergence_groups={len(GROUPS)} assigned={len(assigned)}")
