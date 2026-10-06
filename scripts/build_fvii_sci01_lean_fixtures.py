#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "formalization" / "lean" / "FoundationsVII" / "Models" / "Finite"
SCENARIOS = ROOT / "readiness" / "two_theory_world" / "scenarios.jsonl"
COUNTERMODELS = ROOT / "readiness" / "countermodel_atlas.jsonl"

FLAG_MAP = {
    "anti_product":"antiProduct", "budget_ok":"budgetOk", "closed_family":"closedFamily",
    "common_refinement":"commonRefinement", "compatible":"compatible", "composite":"composite",
    "contact":"contact", "detector_power":"detectorPower", "drive":"drive", "fired":"fired",
    "generator_reachable":"generatorReachable", "holonomy":"holonomy", "join_destroyed":"joinDestroyed",
    "neutral_seed":"neutralSeed", "new_residual":"newResidual", "observer_priced":"observerPriced",
    "observer_used":"observerUsed", "order_residue":"orderResidue", "parent_refined":"parentRefined",
    "partial_domain":"partialDomain", "prospective":"prospective", "reachable":"reachable",
    "relabel_only":"relabelOnly", "resemblance_only":"resemblanceOnly", "retention":"retention",
    "retrospective":"retrospective", "same_source":"sameSource", "scheduling_only":"schedulingOnly",
    "seed":"seed", "sound":"sound", "source_independent":"sourceIndependent",
    "total_lens_only":"totalLensOnly",
}
STATUS_MAP = {
    "BOOTSTRAP_BLOCKED":"bootstrapBlocked", "LAWFUL_FIRST_EXTENSION":"lawfulFirstExtension",
    "PROSPECTIVE_ADMISSION":"prospectiveAdmission",
    "RETROSPECTIVE_SELF_CERTIFICATION_REJECTED":"retrospectiveSelfCertificationRejected",
    "INDEPENDENCE_GATE_FAILED":"independenceGateFailed", "CONTACT_WITHOUT_JOIN":"contactWithoutJoin",
    "COMMON_REFINEMENT_NONSTRICT":"commonRefinementNonstrict", "STRICT_JOIN":"strictJoin",
    "RETENTION_OBSTRUCTION":"retentionObstruction", "BUDGET_OBSTRUCTION":"budgetObstruction",
    "SOURCE_OBSTRUCTION":"sourceObstruction", "NO_EVIDENCED_CONTACT":"noEvidencedContact",
    "CERTIFIED_NONINTERACTION":"certifiedNoninteraction", "FAKE_JOIN_SCHEDULING":"fakeJoinScheduling",
    "FAKE_JOIN_RELABELING":"fakeJoinRelabeling", "ORDER_RESIDUE":"orderResidue",
    "HOLONOMY_ZERO_ARROW":"holonomyZeroArrow", "DRIVEN_ARROW":"drivenArrow",
    "SOUND_UNREACHABLE":"soundUnreachable", "REACHABLE_NONOCCURRENT":"reachableNonoccurrent",
    "OCCURRENT_EVENT":"occurrentEvent", "UNPRICED_OBSERVER":"unpricedObserver",
    "UNLICENSED_TOTALITY_TRANSFER":"unlicensedTotalityTransfer",
    "REFINEMENT_DESTROYS_JOIN":"refinementDestroysJoin",
}
ASSERT_MAP = {
    "bridge_valid":"bridgeValid", "certified_noninteraction":"certifiedNoninteraction",
    "contact":"contact", "directionality":"directionality", "endogenous":"endogenous",
    "first_extension":"firstExtension", "holonomy":"holonomy", "new_residual":"newResidual",
    "occurred":"occurred", "prospective_credit":"prospectiveCredit", "reachable":"reachable",
    "strict_join":"strictJoin",
}


def rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def q(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


def list_str(values: list[str]) -> str:
    return "[" + ", ".join(q(v) for v in values) + "]"


def scenario_name(sid: str) -> str:
    return "scenario" + sid.split("S")[-1]


def cm_name(cid: str) -> str:
    return "countermodel" + cid.split("-")[-1]


def main() -> int:
    scenarios = rows(SCENARIOS)
    lines = [
        "/-! Generated frozen scenario declarations.  Source: readiness/two_theory_world/scenarios.jsonl -/",
        "",
        "import FoundationsVII.Models.Finite.Evaluator",
        "",
        "namespace FoundationsVII.Models.Finite",
        "",
    ]
    for s in scenarios:
        fields = [f"{FLAG_MAP[k]} := {'true' if v else 'false'}" for k,v in sorted(s["flags"].items())]
        assertions = [f"(.{ASSERT_MAP[k]}, {'true' if v else 'false'})" for k,v in sorted(s["assertions"].items())]
        name = scenario_name(s["scenario_id"])
        lines.extend([
            f"def {name} : ScenarioFixture :=",
            f"  {{ fixtureId := {q(s['scenario_id'])}",
            f"    name := {q(s['name'])}",
            "    flags :=",
            "      { " + "\n        ".join(fields) + " }" if fields else "      {}",
            f"    expectedStatus := .{STATUS_MAP[s['expected_status']]}",
            "    assertions := [" + ", ".join(assertions) + "]",
            f"    candidateIds := {list_str(sorted(s['candidate_ids']))} }}",
            "",
            f"theorem {name}_passes : scenarioPass {name} = true := by",
            "  decide",
            "",
        ])
    lines.append("def allScenarios : List ScenarioFixture :=")
    lines.append("  [" + "\n  , ".join(scenario_name(s["scenario_id"]) for s in scenarios) + "]")
    lines.extend([
        "",
        "theorem all_scenarios_pass : allScenarios.all scenarioPass = true := by",
        "  decide",
        "",
        "theorem all_scenario_statuses_are_pairwise_distinct :",
        "    (allScenarios.map ScenarioFixture.expectedStatus).eraseDups.length = 24 := by",
        "  decide",
        "",
        "end FoundationsVII.Models.Finite",
        "",
    ])
    (OUT / "Scenarios.lean").write_text("\n".join(lines), encoding="utf-8")

    scenario_by = {s["scenario_id"]: s for s in scenarios}
    cms = rows(COUNTERMODELS)
    lines = [
        "/-! Generated countermodel declarations.  Source: readiness/countermodel_atlas.jsonl -/",
        "",
        "import FoundationsVII.Models.Finite.Scenarios",
        "",
        "namespace FoundationsVII.Models.Finite",
        "",
        "def countermodelPass (fixture : CountermodelFixture) : Bool :=",
        "  scenarioPass fixture.scenario &&",
        "  (evaluate fixture.scenario.flags).1 == fixture.expectedStatus",
        "",
    ]
    for cm in cms:
        name=cm_name(cm["countermodel_id"]); s=scenario_by[cm["scenario_id"]]
        lines.extend([
            f"def {name} : CountermodelFixture :=",
            f"  {{ fixtureId := {q(cm['countermodel_id'])}",
            f"    name := {q(cm['name'])}",
            f"    scenario := {scenario_name(cm['scenario_id'])}",
            f"    expectedStatus := .{STATUS_MAP[s['expected_status']]}",
            f"    shows := {q(cm['shows'])}",
            f"    candidateIds := {list_str(sorted(cm['candidate_ids']))} }}",
            "",
            f"theorem {name}_passes : countermodelPass {name} = true := by",
            "  decide",
            "",
        ])
    lines.append("def allCountermodels : List CountermodelFixture :=")
    lines.append("  ["+"\n  , ".join(cm_name(cm["countermodel_id"]) for cm in cms)+"]")
    lines.extend([
        "",
        "theorem all_countermodels_pass : allCountermodels.all countermodelPass = true := by",
        "  decide",
        "",
        "end FoundationsVII.Models.Finite",
        "",
    ])
    (OUT / "Countermodels.lean").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"lean_scenarios":len(scenarios),"lean_countermodels":len(cms)},sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
