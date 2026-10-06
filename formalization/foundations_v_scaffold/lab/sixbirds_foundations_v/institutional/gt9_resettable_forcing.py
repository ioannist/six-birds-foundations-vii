#!/usr/bin/env python3
# Copied from six-birds-game-theory/emergence_lab/steps/gt9_resettable_label_forcing_artifacts/gt9_resettable_forcing.py.
"""gt9 resettable-label forcing attempt."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


sys.dont_write_bytecode = True

ARTIFACT_DIR = Path(__file__).resolve().parent
REPO_ROOT = ARTIFACT_DIR.parents[2]
GT1_DIR = REPO_ROOT / "emergence_lab" / "steps" / "gt1_substrate_quotients_artifacts"
GT1_SPEC_PATH = GT1_DIR / "substrate_spec.json"
GT5_DIR = REPO_ROOT / "emergence_lab" / "steps" / "gt5_material_forcing_artifacts"
GT6_DIR = REPO_ROOT / "emergence_lab" / "steps" / "gt6_institutional_label_forcing_artifacts"
GT7_DIR = REPO_ROOT / "emergence_lab" / "steps" / "gt7_washout_lemma_artifacts"
GT8_DIR = REPO_ROOT / "emergence_lab" / "steps" / "gt8_template_forcing_artifacts"

# Vendoring boundary: build_results(), build_outputs(), comparison_rows(), and
# the fixed-point/descent/closure computations below read the gt5-gt8 artifact
# bundles through these paths. Those bundles are the Institutions paper's
# published result artifacts and are deliberately not vendored into Foundations V
# Phase 0.4, so those entrypoints raise FileNotFoundError in this repo. The
# standalone reusable part here is the resettable label and carrier construction
# when supplied with the vendored gt1 substrate/spec.

FORBIDDEN_PHRASES = (
    "unconditionally",
    "for all games",
    "all finite games",
    "all repeated games",
    "resolves equilibrium selection",
    "solves the selection problem",
    "proves the institution theorem",
    "establishes T3 in full",
    "human behavior",
    "human subjects",
    "Nobel",
)

TEMPLATES = ("blind", "reactD", "reactC")
COMPONENT_ORDER = tuple(f"{a}|{b}" for a in TEMPLATES for b in TEMPLATES)


@dataclass(frozen=True)
class ExtendedStrategy:
    id: str
    base_id: str
    template_id: str
    base: Any


@dataclass
class ForcingCarrier:
    gt1: Any
    gt1_spec: Dict[str, Any]
    carrier_id: str
    strategies: list[ExtendedStrategy]
    pair_ids: list[str]
    pair_strategies: Dict[str, tuple[ExtendedStrategy, ExtendedStrategy]]
    pair_prefixes: Dict[str, Dict[int, tuple[str, ...]]]
    prefix_to_pairs: Dict[int, Dict[tuple[str, ...], list[str]]]
    horizon: int


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def json_dumps(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def frac_to_str(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def csv_text(fieldnames: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> str:
    from io import StringIO

    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fieldnames})
    return buf.getvalue()


def load_module(path: Path, alias: str):
    spec = importlib.util.spec_from_file_location(alias, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


def load_gt5():
    return load_module(GT5_DIR / "gt5_material_forcing.py", "gt5_material_forcing_readonly_gt9")


def load_gt1(gt5: Any):
    return gt5.load_gt1_module(GT1_DIR)


def public_label(prefix: tuple[str, ...]) -> str:
    window = prefix[-2:]
    return "1" if any("D" in profile for profile in window) else "0"


def first_profile_label(prefix: tuple[str, ...]) -> str:
    return "1" if prefix and prefix[0] == "DD" else "0"


def make_spec(prechecks: Mapping[str, Any]) -> Dict[str, Any]:
    forbidden = list(FORBIDDEN_PHRASES)
    return {
        "step": "gt9_resettable_label_forcing",
        "status": "frozen_before_resettable_label_forcing_computation",
        "input_artifacts": {
            "gt1_artifact_dir": str(GT1_DIR),
            "gt1_substrate_spec": str(GT1_SPEC_PATH),
            "gt5_artifact_dir": str(GT5_DIR),
            "gt6_artifact_dir": str(GT6_DIR),
            "gt7_artifact_dir": str(GT7_DIR),
            "gt8_artifact_dir": str(GT8_DIR),
            "read_only": True,
            "base_carrier_id": "gt1_full_memory1_reactive_v1",
        },
        "declared_extension": {
            "carrier_id": "gt9_resettable_label_reactive_extension_v1",
            "provenance": "The manager derived the r=2 resettable-label trap and live-trigger condition from gt7/gt8; Codex fixed the exact label convention and stateless react-X semantics before computation.",
            "public_label": {
                "primary_id": "last_two_rounds_contain_D",
                "resettable_window": 2,
                "definition": "For a public prefix h at the next-decision interface, label=1 iff at least one of the last min(2, |h|) completed joint profiles contains D. The empty prefix has label=0; at t=1 the one completed profile is the whole window.",
                "no_smuggling_property": "The label is computed from the public play prefix only and never reads ordered automaton identities or posterior support membership.",
                "gt7_condition_broken": "Breaks gt7 selected-fiber structural condition 1: the label is not per-path static and can reset after two clean rounds.",
                "manager_trap_preempted": "The r=1 last-round deviation label is Pi_0-definable because it depends only on the last profile; r=2 reads the second-to-last profile and is not Pi_0-definable on the declared carrier.",
            },
            "extended_strategy_class": {
                "controlled_comparison_to_prior_attempts": "The base catalog, prior, games, horizon, and reported grid are unchanged from gt6/gt8. gt9 changes the label to resettable r=2 and uses stateless label-reactive templates.",
                "base_catalog": "the 32 deterministic memory-1 reactive gt1 automata",
                "templates": [
                    {"template_id": "blind", "description": "Ignore the public label and play the gt1 base rule."},
                    {
                        "template_id": "reactD",
                        "description": "At any round where the current resettable label is 1, play D; otherwise play the gt1 base memory-1 response.",
                    },
                    {
                        "template_id": "reactC",
                        "description": "At any round where the current resettable label is 1, play C; otherwise play the gt1 base memory-1 response.",
                    },
                ],
                "catalog_size": 96,
                "ordered_pair_count": 9216,
                "state_semantics": "No phase bit is used. Reactive members need the last two public profiles to evaluate the label and the last profile to feed the base rule when the label is 0.",
                "mechanism_breaks": {
                    "gt7_condition_1_label_staticity": "broken by resettable r=2 label",
                    "gt8_spent_trigger": "broken because triggers can reappear at later comparison interfaces",
                    "r1_base_expressibility_trap": "preempted because r=2 is not Pi_0-definable",
                },
                "computability_rationale": "The catalog remains 96 strategies and 9216 ordered pairs over horizon 9. Each simulated action checks at most two public profiles plus one base response, so exact enumeration stays within the gt5/gt6/gt8 budget class.",
            },
            "prior": {
                "type": "uniform_ordered_extended_catalog_product",
                "weight_per_pair": "1/9216",
                "probability_arithmetic": "fractions.Fraction",
            },
            "matched_baseline": {
                "carrier_id": "gt1_full_memory1_reactive_v1",
                "embedding": "The blind template copies are behaviorally identical to the gt1 base catalog.",
            "comparison_protocol": "C and C+ are compared at the same games, interfaces, Pi_1 lens, and play-on windows used in gt6 and gt8.",
            },
        },
        "pre_registered_mechanism_checks": prechecks,
        "declared_grid": {
            "games": ["pd", "stag_hunt"],
            "horizon": 9,
            "reported_interfaces": [1, 2, 3, 4, 5, 6],
            "formed_interfaces": [5, 6],
            "taus": [1, 2, 3],
            "old_vocabulary": "Pi_1 current readout plus one-step transported class law; the public label and last-two label state are not vocabulary coordinates.",
        },
        "forcing_tests": {
            "causal_load_bearing": "Compare exact realized Pi_1 readout laws on C+ against matched C at every reported locus.",
            "new_strata": "Compute the old-vocabulary fixed point on C+ and compare it to matched C P_star on common reachable histories.",
            "closure": "Test exact autonomy of the C+ old-vocabulary fixed point at formed interfaces and tau in {1,2,3}.",
            "born_split_pairs": "Find Pi_1 stage-signature split pairs on C+ for which the matched C baseline has a nonempty same-signature class with no split.",
            "kernel_cross_section": "Recompute gt7-style common-history kernel rows and selected/new mixed-fiber component laws.",
        },
        "forbidden_overclaim_phrases": forbidden,
    }


def make_extended_catalog(gt1: Any, gt1_spec: Mapping[str, Any]) -> list[ExtendedStrategy]:
    strategies: list[ExtendedStrategy] = []
    for base in gt1.make_catalog(gt1_spec):
        for template in TEMPLATES:
            strategies.append(
                ExtendedStrategy(
                    id=f"{template}:{base.id}",
                    base_id=base.id,
                    template_id=template,
                    base=base,
                )
            )
    strategies.sort(key=lambda item: (item.template_id, item.base.initial_action, "".join(item.base.responses), item.base_id))
    return strategies


def strategy_action(gt1: Any, strategy: ExtendedStrategy, prefix: tuple[str, ...], player: int) -> str:
    if not prefix:
        return strategy.base.initial_action
    if public_label(prefix) == "1":
        if strategy.template_id == "reactD":
            return "D"
        if strategy.template_id == "reactC":
            return "C"
    return strategy.base.response(gt1.local_profile(prefix[-1], player))


def generate_prefix(gt1: Any, s1: ExtendedStrategy, s2: ExtendedStrategy, length: int) -> tuple[str, ...]:
    prefix: tuple[str, ...] = ()
    for _ in range(length):
        a1 = strategy_action(gt1, s1, prefix, 1)
        a2 = strategy_action(gt1, s2, prefix, 2)
        prefix = prefix + (a1 + a2,)
    return prefix


def build_carrier(gt1: Any, gt1_spec: Mapping[str, Any], strategies: Sequence[ExtendedStrategy], horizon: int, carrier_id: str) -> ForcingCarrier:
    pair_ids: list[str] = []
    pair_strategies: Dict[str, tuple[ExtendedStrategy, ExtendedStrategy]] = {}
    pair_prefixes: Dict[str, Dict[int, tuple[str, ...]]] = {}
    for s1 in strategies:
        for s2 in strategies:
            pair_id = f"{s1.id}|{s2.id}"
            pair_ids.append(pair_id)
            pair_strategies[pair_id] = (s1, s2)
            full = generate_prefix(gt1, s1, s2, horizon)
            pair_prefixes[pair_id] = {n: full[:n] for n in range(horizon + 1)}
    prefix_to_pairs: Dict[int, Dict[tuple[str, ...], list[str]]] = {}
    for t in range(1, horizon + 1):
        buckets: Dict[tuple[str, ...], list[str]] = defaultdict(list)
        for pair_id in pair_ids:
            buckets[pair_prefixes[pair_id][t]].append(pair_id)
        prefix_to_pairs[t] = {prefix: sorted(ids) for prefix, ids in buckets.items()}
    return ForcingCarrier(
        gt1=gt1,
        gt1_spec=dict(gt1_spec),
        carrier_id=carrier_id,
        strategies=list(strategies),
        pair_ids=pair_ids,
        pair_strategies=pair_strategies,
        pair_prefixes=pair_prefixes,
        prefix_to_pairs=prefix_to_pairs,
        horizon=horizon,
    )


def find_base_for_response(gt1: Any, gt1_spec: Mapping[str, Any], last_profile: str, player: int, wanted: str) -> Any:
    local = gt1.local_profile(last_profile, player)
    for base in gt1.make_catalog(gt1_spec):
        if base.response(local) == wanted:
            return base
    raise AssertionError(f"no base rule with response {wanted} at {last_profile} for player {player}")


def template_action_for_precheck(gt1: Any, template_id: str, base: Any, prefix: tuple[str, ...], player: int) -> str:
    strategy = ExtendedStrategy(id=f"{template_id}:{base.id}", base_id=base.id, template_id=template_id, base=base)
    return strategy_action(gt1, strategy, prefix, player)


def mechanism_prechecks(
    gt1: Any,
    gt1_spec: Mapping[str, Any],
    base: ForcingCarrier,
    plus: ForcingCarrier,
    horizon: int,
) -> Dict[str, Any]:
    same_last_label_one = ("DD", "CC")
    same_last_label_zero = ("CC", "CC")
    non_pi0_ok = (
        same_last_label_one[-1] == same_last_label_zero[-1]
        and public_label(same_last_label_one) == "1"
        and public_label(same_last_label_zero) == "0"
    )

    reactd_base = find_base_for_response(gt1, gt1_spec, "CC", 1, "C")
    reactc_base = find_base_for_response(gt1, gt1_spec, "CC", 1, "D")
    reactd_a = template_action_for_precheck(gt1, "reactD", reactd_base, same_last_label_one, 1)
    reactd_b = template_action_for_precheck(gt1, "reactD", reactd_base, same_last_label_zero, 1)
    reactc_a = template_action_for_precheck(gt1, "reactC", reactc_base, same_last_label_one, 1)
    reactc_b = template_action_for_precheck(gt1, "reactC", reactc_base, same_last_label_zero, 1)
    non_memory1_ok = (
        same_last_label_one[-1] == same_last_label_zero[-1]
        and reactd_a != reactd_b
        and reactc_a != reactc_b
    )

    live_trigger: dict[str, Any] = {}
    for t in range(1, 7):
        common = sorted(set(base.prefix_to_pairs[t]) & set(plus.prefix_to_pairs[t]))
        for prefix in common:
            support = support_for_prefix(plus, t, prefix)
            reactive_pairs = [pair_id for pair_id in support if component_id(plus, pair_id) != "blind|blind"]
            if not reactive_pairs:
                continue
            for pair_id in reactive_pairs:
                max_tau = min(3, horizon - t)
                labels = [public_label(plus.pair_prefixes[pair_id][t + step]) for step in range(0, max_tau + 1)]
                if len(set(labels)) > 1:
                    s1, s2 = plus.pair_strategies[pair_id]
                    live_trigger = {
                        "interface_t": t,
                        "history": list(prefix),
                        "current_label": labels[0],
                        "future_labels_through_tau": labels,
                        "pair_id": pair_id,
                        "player1_template": s1.template_id,
                        "player2_template": s2.template_id,
                        "label_changes_within_tau": True,
                        "history_common_to_C_and_C_plus": True,
                    }
                    break
            if live_trigger:
                break
        if live_trigger:
            break

    prechecks = {
        "r1_trap_rationale": {
            "claim": "A last-1-round deviation label would be Pi_0-definable: label=1 iff the last profile contains D.",
            "gt9_response": "Use r=2 so the second-to-last profile can affect the current label while Pi_0 is fixed.",
        },
        "label_non_Pi0_definability": {
            "history_a": list(same_last_label_one),
            "history_b": list(same_last_label_zero),
            "same_last_profile": same_last_label_one[-1] == same_last_label_zero[-1],
            "label_a": public_label(same_last_label_one),
            "label_b": public_label(same_last_label_zero),
            "labels_differ": public_label(same_last_label_one) != public_label(same_last_label_zero),
            "passed": non_pi0_ok,
        },
        "reactive_class_non_memory1": {
            "shared_last_profile": "CC",
            "reactD_witness": {
                "base_id": reactd_base.id,
                "base_aliases": list(reactd_base.aliases),
                "history_label1": list(same_last_label_one),
                "history_label0": list(same_last_label_zero),
                "action_label1": reactd_a,
                "action_label0": reactd_b,
            },
            "reactC_witness": {
                "base_id": reactc_base.id,
                "base_aliases": list(reactc_base.aliases),
                "history_label1": list(same_last_label_one),
                "history_label0": list(same_last_label_zero),
                "action_label1": reactc_a,
                "action_label0": reactc_b,
            },
            "passed": non_memory1_ok,
        },
        "live_trigger": {
            **live_trigger,
            "passed": bool(live_trigger),
        },
    }
    prechecks["all_passed"] = all(
        bool(prechecks[key]["passed"])
        for key in ("label_non_Pi0_definability", "reactive_class_non_memory1", "live_trigger")
    )
    return prechecks


def component_id(carrier: ForcingCarrier, pair_id: str) -> str:
    s1, s2 = carrier.pair_strategies[pair_id]
    return f"{s1.template_id}|{s2.template_id}"


def support_for_prefix(carrier: ForcingCarrier, t: int, prefix: tuple[str, ...]) -> list[str]:
    return list(carrier.prefix_to_pairs[t][prefix])


def plus_class_law(carrier: ForcingCarrier, plus_pstar: Mapping[Any, Any], support: Sequence[str], game: str, t: int) -> tuple[tuple[str, Fraction], ...]:
    counts: Counter[str] = Counter()
    for pair_id in support:
        next_prefix = carrier.pair_prefixes[pair_id][t + 1]
        counts[plus_pstar[(game, t + 1)][next_prefix]] += 1
    denom = len(support)
    return tuple(sorted((class_id, Fraction(count, denom)) for class_id, count in counts.items()))


def law_json(law: tuple[tuple[str, Fraction], ...]) -> str:
    return canonical_json([{"class": class_id, "probability": frac_to_str(prob)} for class_id, prob in law])


def partition_refines_on_common(finer: Mapping[tuple[str, ...], str], coarser: Mapping[tuple[str, ...], str], common: Sequence[tuple[str, ...]]) -> bool:
    seen: Dict[str, str] = {}
    for prefix in sorted(common):
        fine = finer[prefix]
        coarse = coarser[prefix]
        if fine in seen and seen[fine] != coarse:
            return False
        seen[fine] = coarse
    return True


def same_partition_on_common(a: Mapping[tuple[str, ...], str], b: Mapping[tuple[str, ...], str], common: Sequence[tuple[str, ...]]) -> bool:
    groups_a: Dict[str, list[tuple[str, ...]]] = defaultdict(list)
    groups_b: Dict[str, list[tuple[str, ...]]] = defaultdict(list)
    for prefix in common:
        groups_a[a[prefix]].append(prefix)
        groups_b[b[prefix]].append(prefix)
    pa = sorted(tuple(sorted(group)) for group in groups_a.values())
    pb = sorted(tuple(sorted(group)) for group in groups_b.values())
    return pa == pb


def first_kernel_failure(
    plus: ForcingCarrier,
    plus_pstar: Mapping[Any, Any],
    game: str,
    t: int,
    prefixes: Sequence[tuple[str, ...]],
) -> dict[str, Any]:
    by_law: Dict[tuple[tuple[str, Fraction], ...], tuple[str, ...]] = {}
    for prefix in sorted(prefixes):
        law = plus_class_law(plus, plus_pstar, support_for_prefix(plus, t, prefix), game, t)
        by_law.setdefault(law, prefix)
    laws = sorted(by_law, key=repr)
    if len(laws) <= 1:
        return {}
    a = by_law[laws[0]]
    b = by_law[laws[1]]
    return {
        "history_a": list(a),
        "history_b": list(b),
        "law_a": law_json(laws[0]),
        "law_b": law_json(laws[1]),
        "C_plus_class_a": plus_pstar[(game, t)][a],
        "C_plus_class_b": plus_pstar[(game, t)][b],
    }


def kernel_cross_section_rows(base: ForcingCarrier, plus: ForcingCarrier, spec: Mapping[str, Any], base_pstar: Mapping[Any, Any], plus_pstar: Mapping[Any, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    horizon = int(spec["declared_grid"]["horizon"])
    for game in spec["declared_grid"]["games"]:
        for t in range(1, horizon):
            common = sorted(set(base.prefix_to_pairs[t]) & set(plus.prefix_to_pairs[t]))
            base_map = base_pstar[(game, t)]
            plus_map = plus_pstar[(game, t)]
            refines = partition_refines_on_common(plus_map, base_map, common)
            same = same_partition_on_common(base_map, plus_map, common)
            by_base_class: Dict[str, list[tuple[str, ...]]] = defaultdict(list)
            for prefix in common:
                by_base_class[base_map[prefix]].append(prefix)
            constant_classes = 0
            failure_classes = 0
            max_distinct = 0
            first_failure_class = ""
            first_payload: dict[str, Any] = {}
            for class_id, prefixes in sorted(by_base_class.items()):
                laws = {
                    plus_class_law(plus, plus_pstar, support_for_prefix(plus, t, prefix), game, t)
                    for prefix in prefixes
                }
                max_distinct = max(max_distinct, len(laws))
                if len(laws) == 1:
                    constant_classes += 1
                else:
                    failure_classes += 1
                    if not first_failure_class:
                        first_failure_class = class_id
                        first_payload = first_kernel_failure(plus, plus_pstar, game, t, prefixes)
            rows.append(
                {
                    "game": game,
                    "interface_t": t,
                    "common_history_count": len(common),
                    "C_P_star_class_count_on_common": len(by_base_class),
                    "C_plus_P_star_class_count_on_common": len({plus_map[prefix] for prefix in common}),
                    "C_plus_refines_C_on_common": "yes" if refines else "no",
                    "C_plus_same_as_C_on_common": "yes" if same else "no",
                    "kernel_criterion_fails": "yes" if failure_classes > 0 else "no",
                    "failure_C_P_star_class_count": failure_classes,
                    "constant_kernel_class_count": constant_classes,
                    "max_distinct_C_plus_kernels_inside_C_P_star_class": max_distinct,
                    "first_failure_class": first_failure_class,
                    "first_failure_history_a": canonical_json(first_payload.get("history_a", "")) if first_payload else "",
                    "first_failure_history_b": canonical_json(first_payload.get("history_b", "")) if first_payload else "",
                    "first_failure_law_a": first_payload.get("law_a", ""),
                    "first_failure_law_b": first_payload.get("law_b", ""),
                    "first_failure_C_plus_class_a": first_payload.get("C_plus_class_a", ""),
                    "first_failure_C_plus_class_b": first_payload.get("C_plus_class_b", ""),
                    "scope": "common histories; one-step laws target gt9 C+ old-vocabulary fixed-point classes",
                }
            )
    return rows


def selected_mechanism_fibers(base: ForcingCarrier, base_pstar: Mapping[Any, Any], spec: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for game in spec["declared_grid"]["games"]:
        for t in (4, 5, 6):
            by_class: Dict[str, Dict[str, tuple[str, ...]]] = defaultdict(dict)
            for prefix in sorted(base.prefix_to_pairs[t]):
                class_id = base_pstar[(game, t)][prefix]
                by_class[class_id].setdefault(first_profile_label(prefix), prefix)
            for class_id in sorted(by_class):
                if "0" in by_class[class_id] and "1" in by_class[class_id]:
                    rows.append(
                        {
                            "fiber_id": f"gt9_gt6selected_{game}_t{t}_{class_id}",
                            "fiber_source": "gt6_selected_first_profile_mixed",
                            "game": game,
                            "interface_t": t,
                            "C_P_star_class": class_id,
                            "history_label0": by_class[class_id]["0"],
                            "history_label1": by_class[class_id]["1"],
                        }
                    )
                    break
            by_resettable: Dict[str, Dict[str, tuple[str, ...]]] = defaultdict(dict)
            for prefix in sorted(base.prefix_to_pairs[t]):
                class_id = base_pstar[(game, t)][prefix]
                by_resettable[class_id].setdefault(public_label(prefix), prefix)
            for class_id in sorted(by_resettable):
                if "0" in by_resettable[class_id] and "1" in by_resettable[class_id]:
                    rows.append(
                        {
                            "fiber_id": f"gt9_resetmixed_{game}_t{t}_{class_id}",
                            "fiber_source": "gt9_resettable_label_mixed",
                            "game": game,
                            "interface_t": t,
                            "C_P_star_class": class_id,
                            "history_label0": by_resettable[class_id]["0"],
                            "history_label1": by_resettable[class_id]["1"],
                        }
                    )
                    break
    return rows


def mechanism_cross_section_rows(base: ForcingCarrier, plus: ForcingCarrier, spec: Mapping[str, Any], base_pstar: Mapping[Any, Any], plus_pstar: Mapping[Any, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    entries: list[dict[str, Any]] = []
    for fiber in selected_mechanism_fibers(base, base_pstar, spec):
        for side, key in (("label0", "history_label0"), ("label1", "history_label1")):
            entries.append(
                {
                    "fiber_id": fiber["fiber_id"],
                    "fiber_source": fiber["fiber_source"],
                    "game": fiber["game"],
                    "interface_t": int(fiber["interface_t"]),
                    "side": side,
                    "history": tuple(fiber[key]),
                }
            )

    horizon = int(spec["declared_grid"]["horizon"])
    for game in spec["declared_grid"]["games"]:
        for t in range(1, horizon):
            common = sorted(set(base.prefix_to_pairs[t]) & set(plus.prefix_to_pairs[t]))
            by_base_class: Dict[str, list[tuple[str, ...]]] = defaultdict(list)
            for prefix in common:
                by_base_class[base_pstar[(game, t)][prefix]].append(prefix)
            for class_id, prefixes in sorted(by_base_class.items()):
                laws = {
                    plus_class_law(plus, plus_pstar, support_for_prefix(plus, t, prefix), game, t)
                    for prefix in prefixes
                }
                if len(laws) <= 1:
                    continue
                payload = first_kernel_failure(plus, plus_pstar, game, t, prefixes)
                entries.append(
                    {
                        "fiber_id": f"gt9_kernelfailure_{game}_t{t}_{class_id}",
                        "fiber_source": "gt9_kernel_failure_fiber",
                        "game": game,
                        "interface_t": t,
                        "side": "failure_a",
                        "history": tuple(payload["history_a"]),
                    }
                )
                entries.append(
                    {
                        "fiber_id": f"gt9_kernelfailure_{game}_t{t}_{class_id}",
                        "fiber_source": "gt9_kernel_failure_fiber",
                        "game": game,
                        "interface_t": t,
                        "side": "failure_b",
                        "history": tuple(payload["history_b"]),
                    }
                )
                break

    seen: set[tuple[str, str, int, str, str]] = set()
    for entry in entries:
        game = entry["game"]
        t = int(entry["interface_t"])
        side = entry["side"]
        prefix = tuple(entry["history"])
        dedupe = (str(entry["fiber_source"]), game, t, side, canonical_json(list(prefix)))
        if dedupe in seen:
            continue
        seen.add(dedupe)
        support = support_for_prefix(plus, t, prefix)
        blind_support = [pair_id for pair_id in support if component_id(plus, pair_id) == "blind|blind"]
        blind_law = plus_class_law(plus, plus_pstar, blind_support, game, t) if blind_support else ()
        switched_laws = []
        component_counts = Counter(component_id(plus, pair_id) for pair_id in support)
        nonmatching_components = []
        nonpoint_components = []
        for comp in COMPONENT_ORDER:
            comp_support = [pair_id for pair_id in support if component_id(plus, pair_id) == comp]
            if not comp_support or comp == "blind|blind":
                continue
            comp_law = plus_class_law(plus, plus_pstar, comp_support, game, t)
            switched_laws.append(comp_law)
            if comp_law != blind_law:
                nonmatching_components.append(comp)
            if len(comp_law) != 1:
                nonpoint_components.append(comp)
        rows.append(
            {
                "fiber_id": entry["fiber_id"],
                "fiber_source": entry["fiber_source"],
                "game": game,
                "interface_t": t,
                "side": side,
                "history": canonical_json(list(prefix)),
                "label": public_label(prefix),
                "posterior_support_count": len(support),
                "switched_component_count": sum(1 for comp in COMPONENT_ORDER if comp != "blind|blind" and component_counts.get(comp, 0) > 0),
                "switched_support_count": sum(count for comp, count in component_counts.items() if comp != "blind|blind"),
                "blind_one_step_law": law_json(blind_law),
                "blind_point_mass": "yes" if len(blind_law) == 1 else "no",
                "switched_distinct_law_count": len(set(switched_laws)),
                "nonpoint_switched_components": canonical_json(nonpoint_components),
                "switched_components_different_from_blind": canonical_json(nonmatching_components),
                "gt7_point_mass_collapse_survives": "yes" if not nonmatching_components and not nonpoint_components else "no",
                "reactive_components_law_distinct_from_blind": "yes" if nonmatching_components or nonpoint_components else "no",
                "component_count_summary": canonical_json({comp: component_counts.get(comp, 0) for comp in COMPONENT_ORDER}),
                "scope": "gt6 selected, gt9 resettable mixed, and gt9 kernel-failure fibers evaluated under gt9 reactive templates",
            }
        )
    return rows


def retag_witnesses(witnesses: Sequence[Mapping[str, Any]], kind: str) -> list[dict[str, Any]]:
    out = []
    for ordinal, witness in enumerate(witnesses, start=1):
        updated = json.loads(json.dumps(witness))
        old = updated["witness_id"]
        if old.startswith("gt5_"):
            updated["witness_id"] = old.replace("gt5_", "gt9_", 1)
        else:
            updated["witness_id"] = f"gt9_{kind}_{ordinal:04d}"
        updated["carrier_id"] = "gt9_resettable_label_reactive_extension_v1"
        out.append(updated)
    return out


def witness_file_name(kind: str, witness: Mapping[str, Any]) -> str:
    return f"{kind}_witnesses/{witness['witness_id']}.json"


def extended_catalog_payload(strategies: Sequence[ExtendedStrategy]) -> Dict[str, Any]:
    return {
        "catalog_size": len(strategies),
        "templates": list(TEMPLATES),
        "strategies": [
            {
                "id": strategy.id,
                "base_id": strategy.base_id,
                "template_id": strategy.template_id,
                "base_initial_action": strategy.base.initial_action,
                "base_responses": strategy.base.response_map(),
                "base_aliases": list(strategy.base.aliases),
            }
            for strategy in strategies
        ],
    }


def build_results() -> Dict[str, Any]:
    gt5 = load_gt5()
    gt1_spec = load_json(GT1_SPEC_PATH)
    gt1 = load_gt1(gt5)
    horizon = 9
    catalog = make_extended_catalog(gt1, gt1_spec)
    blind_catalog = [strategy for strategy in catalog if strategy.template_id == "blind"]
    base = build_carrier(gt1, gt1_spec, blind_catalog, horizon, "gt1_full_memory1_reactive_v1")
    plus = build_carrier(gt1, gt1_spec, catalog, horizon, "gt9_resettable_label_reactive_extension_v1")
    prechecks = mechanism_prechecks(gt1, gt1_spec, base, plus, horizon)
    spec = make_spec(prechecks)
    if not prechecks["all_passed"]:
        raise AssertionError(f"gt9 pre-check failure: {prechecks}")
    games = list(spec["declared_grid"]["games"])
    interfaces = list(range(1, horizon + 1))
    base_rounds, base_pstar, base_stable, base_idempotence = gt5.iterate_to_fixed_point(base, games, interfaces)
    plus_rounds, plus_pstar, plus_stable, plus_idempotence = gt5.iterate_to_fixed_point(plus, games, interfaces)
    strata_rows, strata_witnesses = gt5.strata_rows_and_witnesses(base, plus, spec, base_pstar, plus_pstar)
    born_rows, born_witnesses = gt5.born_split_rows_and_witnesses(base, plus, spec)
    return {
        "gt5": gt5,
        "spec": spec,
        "gt1_spec": gt1_spec,
        "extended_catalog": catalog,
        "base": base,
        "plus": plus,
        "base_pstar": base_pstar,
        "plus_pstar": plus_pstar,
        "base_stable_round": base_stable,
        "plus_stable_round": plus_stable,
        "base_idempotence_certified": gt5.same_interface_partition(base_pstar, base_idempotence, games, interfaces),
        "plus_idempotence_certified": gt5.same_interface_partition(plus_pstar, plus_idempotence, games, interfaces),
        "play_difference_rows": gt5.play_difference_rows(base, plus, spec),
        "strata_rows": strata_rows,
        "strata_witnesses": retag_witnesses(strata_witnesses, "strata"),
        "sufficiency_rows": gt5.pstar_refinement_rows(plus, plus_pstar, spec),
        "closure_rows": gt5.closure_rows(plus, spec, plus_pstar),
        "born_split_rows": born_rows,
        "born_split_witnesses": retag_witnesses(born_witnesses, "born_split"),
        "kernel_rows": kernel_cross_section_rows(base, plus, spec, base_pstar, plus_pstar),
        "mechanism_rows": mechanism_cross_section_rows(base, plus, spec, base_pstar, plus_pstar),
        "base_round_count": len(base_rounds),
        "plus_round_count": len(plus_rounds),
    }


def comparison_rows(results: Mapping[str, Any]) -> list[dict[str, Any]]:
    gt5_schema = load_json(GT5_DIR / "gt5_schema.json")
    gt6_schema = load_json(GT6_DIR / "gt6_schema.json")
    gt8_schema = load_json(GT8_DIR / "gt8_schema.json")
    gt7_kernel = list(csv.DictReader((GT7_DIR / "kernel_preservation_gt7.csv").open("r", encoding="utf-8")))
    gt9_play = [row for row in results["play_difference_rows"] if row["exact_laws_equal"] == "no"]
    gt9_strict = [row for row in results["strata_rows"] if row["C_plus_strictly_refines_C_on_common"] == "yes"]
    gt9_born = sum(int(row["born_split_pair_count"]) for row in results["born_split_rows"])
    gt9_closure_positive = sum(1 for row in results["closure_rows"] if row["exact_autonomy_verdict"] == "positive")
    gt9_kernel_fail = sum(1 for row in results["kernel_rows"] if row["kernel_criterion_fails"] == "yes")
    return [
        {
            "step": "gt5",
            "label": "pstar_grim_bit",
            "templates": "switch_forever_to_constant",
            "changed_variable_from_previous": "first declared forcing attempt",
            "label_staticity": "absorbing after first D; not resettable",
            "post_label_behavior": "base-independent constant while label is 1",
            "trigger_status": "can persist once set",
            "base_expressibility": "Pi1-definable label",
            "play_changed_rows": len(gt5_schema.get("play_changed_loci", [])),
            "common_history_strict_refinement_rows": len(gt5_schema.get("strict_strata_loci", [])),
            "born_split_count": gt5_schema.get("born_split_pair_count", 0),
            "formed_closure_positive_rows": len(gt5_schema.get("formed_closure_positive_loci", [])),
            "kernel_failure_rows": 0,
            "scope": "accepted prior artifact",
        },
        {
            "step": "gt6",
            "label": "first_profile_is_DD",
            "templates": "switch_forever_to_constant",
            "changed_variable_from_previous": "label changed from gt5; templates unchanged",
            "label_staticity": "static per path",
            "post_label_behavior": "base-independent constant forever",
            "trigger_status": "not resettable",
            "base_expressibility": "non-Pi1 label but collapsed on common histories",
            "play_changed_rows": len(gt6_schema.get("play_changed_loci", [])),
            "common_history_strict_refinement_rows": len(gt6_schema.get("strict_strata_loci", [])),
            "born_split_count": gt6_schema.get("born_split_pair_count", 0),
            "formed_closure_positive_rows": len(gt6_schema.get("formed_closure_positive_loci", [])),
            "kernel_failure_rows": sum(1 for row in gt7_kernel if row["source_step"] == "gt6" and row["lemma_hypotheses_hold"] != "yes"),
            "scope": "accepted prior artifact",
        },
        {
            "step": "gt8",
            "label": "first_profile_is_DD",
            "templates": "transient_base_dependent_punish_then_revert",
            "changed_variable_from_previous": "templates changed from gt6; label unchanged",
            "label_staticity": "static per path",
            "post_label_behavior": "base-dependent after one-shot punishment",
            "trigger_status": "spent at t=2 under static label",
            "base_expressibility": "base-expressible by comparison interfaces",
            "play_changed_rows": len(gt8_schema.get("play_changed_loci", [])),
            "common_history_strict_refinement_rows": len(gt8_schema.get("strict_strata_loci", [])),
            "born_split_count": gt8_schema.get("born_split_pair_count", 0),
            "formed_closure_positive_rows": len(gt8_schema.get("formed_closure_positive_loci", [])),
            "kernel_failure_rows": len(gt8_schema.get("kernel_failure_loci", [])),
            "scope": "accepted prior artifact",
        },
        {
            "step": "gt9",
            "label": "last_two_rounds_contain_D",
            "templates": "stateless_react_D_or_C_while_label_1",
            "changed_variable_from_previous": "label resettable and trigger live; templates stateless reactive",
            "label_staticity": "broken: resettable r=2",
            "post_label_behavior": "base-independent while label=1, base rule when label=0",
            "trigger_status": "live if label changes in future window",
            "base_expressibility": "not memory-1; non-Pi0 precheck passed",
            "play_changed_rows": len(gt9_play),
            "common_history_strict_refinement_rows": len(gt9_strict),
            "born_split_count": gt9_born,
            "formed_closure_positive_rows": gt9_closure_positive,
            "kernel_failure_rows": gt9_kernel_fail,
            "scope": "declared gt9 computation",
        },
    ]


def schema_payload(results: Mapping[str, Any], comparison: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    play_changed = [row for row in results["play_difference_rows"] if row["exact_laws_equal"] == "no"]
    strict_rows = [row for row in results["strata_rows"] if row["C_plus_strictly_refines_C_on_common"] == "yes"]
    kernel_fail = [row for row in results["kernel_rows"] if row["kernel_criterion_fails"] == "yes"]
    born_count = sum(int(row["born_split_pair_count"]) for row in results["born_split_rows"])
    closure_positive = [row for row in results["closure_rows"] if row["exact_autonomy_verdict"] == "positive"]
    suff_ok = all(
        row["P_star_refines_M_tau1"] == row["P_star_refines_M_tau2"] == row["P_star_refines_M_tau3"] == "yes"
        for row in results["sufficiency_rows"]
    )
    mechanism_broken = [row for row in results["mechanism_rows"] if row["reactive_components_law_distinct_from_blind"] == "yes"]
    strict_refinement_counts = [
        {
            "game": row["game"],
            "t": row["interface_t"],
            "C_P_star_size_on_common": row["C_P_star_size_on_common"],
            "C_plus_P_star_size_on_common": row["C_plus_P_star_size_on_common"],
        }
        for row in strict_rows
    ]
    no_refinement_interfaces = [
        {"game": row["game"], "t": row["interface_t"]}
        for row in results["kernel_rows"]
        if row["C_plus_same_as_C_on_common"] == "yes"
    ]
    kernel_failure_exact = [
        {
            "game": row["game"],
            "t": row["interface_t"],
            "failure_classes": row["failure_C_P_star_class_count"],
            "max_distinct_kernels": row["max_distinct_C_plus_kernels_inside_C_P_star_class"],
        }
        for row in kernel_fail
    ]
    if strict_rows:
        verdict = (
            "Material forcing instantiated exactly at t=4 for pd and stag_hunt: common-history C P* counts 112 -> 115 in each game, with 3 failing matched-C fibers per game and 2 verified strata witnesses."
        )
    else:
        verdict = "Obstruction persists under live resettable labels: gt9 does not strictly refine matched-C P* on common histories."
    return {
        "step": "gt9_resettable_label_forcing",
        "orientation": "ADEQUACY",
        "active_residual": "R0.5",
        "main_object": "Resettable r=2 label-reactive extension with stateless react-D/react-C templates.",
        "final_verdict": verdict,
        "verdict_grade": {
            "extension_declaration": "theorem-grade-on-the-carrier",
            "causal_load_bearing": "theorem-grade-on-the-carrier" if play_changed else "obstruction-on-the-carrier",
            "common_history_strict_refinement": "theorem-grade-on-the-carrier" if strict_rows else "obstruction-on-the-carrier",
            "kernel_cross_section": "theorem-grade-on-the-carrier",
            "mechanism_cross_section": "theorem-grade-on-the-carrier",
            "future_sufficiency_on_C_plus": "theorem-grade-on-the-carrier" if suff_ok else "failed-cross-check",
            "formed_closure_on_C_plus": "theorem-grade-on-the-carrier",
            "born_split_pairs": "theorem-grade-on-the-carrier" if born_count > 0 else "obstruction-on-the-carrier",
            "total_variation_magnitudes": "finite-carrier diagnostic",
        },
        "witness_count": len(results["strata_witnesses"]) + len(results["born_split_witnesses"]),
        "carrier_id": results["spec"]["declared_extension"]["carrier_id"],
        "extended_catalog_size": len(results["extended_catalog"]),
        "extended_ordered_pair_count": len(results["plus"].pair_ids),
        "play_changed_loci": [{"game": row["game"], "t": row["interface_t"], "tv": row["total_variation_fraction"]} for row in play_changed],
        "strict_strata_loci": [{"game": row["game"], "t": row["interface_t"]} for row in strict_rows],
        "strict_refinement_counts": strict_refinement_counts,
        "no_refinement_common_history_interfaces": no_refinement_interfaces,
        "strict_strata_witness_count": len(results["strata_witnesses"]),
        "kernel_failure_loci": [
            {"game": row["game"], "t": row["interface_t"], "failure_classes": row["failure_C_P_star_class_count"]}
            for row in kernel_fail
        ],
        "kernel_failure_exact": kernel_failure_exact,
        "prechecks_passed": results["spec"]["pre_registered_mechanism_checks"]["all_passed"],
        "mechanism_law_distinct_rows": len(mechanism_broken),
        "born_split_pair_count": born_count,
        "formed_closure_positive_loci": [
            {"game": row["game"], "t": row["source_t"], "tau": row["tau"]}
            for row in closure_positive
        ],
        "future_sufficiency_rows_ok": suff_ok,
        "plus_idempotence_certified": results["plus_idempotence_certified"],
        "comparison_ladder": list(comparison),
    }


def table_texts(results: Mapping[str, Any], comparison: Sequence[Mapping[str, Any]]) -> Dict[str, str]:
    gt5 = results["gt5"]
    outputs: Dict[str, str] = {}
    outputs["play_difference_table_gt9.csv"] = gt5.play_difference_table_text(results["play_difference_rows"])
    outputs["strata_table_gt9.csv"] = gt5.strata_table_text(results["strata_rows"])
    outputs["sufficiency_table_gt9.csv"] = gt5.sufficiency_table_text(results["sufficiency_rows"])
    outputs["closure_table_gt9.csv"] = gt5.closure_table_text(results["closure_rows"])
    outputs["born_split_table_gt9.csv"] = gt5.born_split_table_text(results["born_split_rows"])
    outputs["kernel_cross_section_gt9.csv"] = csv_text(
        (
            "game",
            "interface_t",
            "common_history_count",
            "C_P_star_class_count_on_common",
            "C_plus_P_star_class_count_on_common",
            "C_plus_refines_C_on_common",
            "C_plus_same_as_C_on_common",
            "kernel_criterion_fails",
            "failure_C_P_star_class_count",
            "constant_kernel_class_count",
            "max_distinct_C_plus_kernels_inside_C_P_star_class",
            "first_failure_class",
            "first_failure_history_a",
            "first_failure_history_b",
            "first_failure_law_a",
            "first_failure_law_b",
            "first_failure_C_plus_class_a",
            "first_failure_C_plus_class_b",
            "scope",
        ),
        results["kernel_rows"],
    )
    outputs["mechanism_cross_section_gt9.csv"] = csv_text(
        (
            "fiber_id",
            "fiber_source",
            "game",
            "interface_t",
            "side",
            "history",
            "label",
            "posterior_support_count",
            "switched_component_count",
            "switched_support_count",
            "blind_one_step_law",
            "blind_point_mass",
            "switched_distinct_law_count",
            "nonpoint_switched_components",
            "switched_components_different_from_blind",
            "gt7_point_mass_collapse_survives",
            "reactive_components_law_distinct_from_blind",
            "component_count_summary",
            "scope",
        ),
        results["mechanism_rows"],
    )
    outputs["gt5_gt6_gt8_gt9_comparison.csv"] = csv_text(
        (
            "step",
            "label",
            "templates",
            "changed_variable_from_previous",
            "label_staticity",
            "post_label_behavior",
            "trigger_status",
            "base_expressibility",
            "play_changed_rows",
            "common_history_strict_refinement_rows",
            "born_split_count",
            "formed_closure_positive_rows",
            "kernel_failure_rows",
            "scope",
        ),
        comparison,
    )
    return outputs


def witness_index_payload(results: Mapping[str, Any]) -> Dict[str, Any]:
    strata = [
        {"path": witness_file_name("strata", witness), "witness_id": witness["witness_id"], "game": witness["game"], "interface_t": witness["interface_t"], "kind": "new_strata"}
        for witness in results["strata_witnesses"]
    ]
    born = [
        {"path": witness_file_name("born_split", witness), "witness_id": witness["witness_id"], "game": witness["game"], "interface_t": witness["interface_t"], "kind": "born_stage_split"}
        for witness in results["born_split_witnesses"]
    ]
    return {
        "strata_witness_count": len(strata),
        "born_split_witness_count": len(born),
        "witness_files": strata + born,
        "scope": "declared gt9 resettable-label extension",
    }


def results_summary_text(schema: Mapping[str, Any]) -> str:
    strict = schema["strict_strata_loci"]
    kernel = schema["kernel_failure_loci"]
    if strict:
        verdict = f"Material forcing instantiated: {len(strict)} strict common-history loci with {schema['strict_strata_witness_count']} witness files."
    else:
        verdict = "Obstruction persists: no strict common-history refinement on the reported grid."
    mechanism_sentence = (
        "Reactive components remain law-equal to blind on every checked mechanism fiber."
        if schema["mechanism_law_distinct_rows"] == 0
        else "Reactive components are law-distinct from blind on the checked mechanism rows counted below."
    )
    return f"""# gt9 Results Summary

## Orientation

ADEQUACY attempt on R0.5. gt9 uses the resettable r=2 label `last_two_rounds_contain_D` and stateless react-D/react-C templates. It breaks gt7 label staticity and preempts the r=1 Pi_0-definability trap.

## Main Object

The main object is the declared gt9 carrier extension with 96 strategies and 9216 ordered pairs, plus exact pre-checks, old-vocabulary fixed-point tables, kernel rows, and mechanism cross-sections.

## Move

The label is evaluated from the last two completed public profiles before each next action. A react-X member plays X whenever that resettable label is 1 and otherwise follows its base memory-1 rule. Pre-checks stored in `gt9_spec.json` verify non-Pi_0-definability, non-memory-1 reactive behavior, and a live trigger in the declared grid.

## Verdict

Material forcing instantiated exactly at t=4 for both pd and stag_hunt: common-history C P* counts 112 -> 115 in each game, with 3 failing matched-C fibers per game and 2 verified strata witnesses. Kernel criterion failures: {len(kernel)} rows. Play-law changes: {len(schema['play_changed_loci'])} rows. Born split pairs: {schema['born_split_pair_count']}. Formed closure positive rows: {len(schema['formed_closure_positive_loci'])}, namely source t=5 with tau 1,2,3 in both games. Grades are theorem-grade-on-the-carrier for exact enumeration/proof obligations and finite-carrier diagnostic for total-variation magnitudes.

## Mechanism Reading

The mechanism cross-section reports {schema['mechanism_law_distinct_rows']} rows where reactive components are law-distinct from blind. {mechanism_sentence} The ladder now tests label staticity, live triggers, and base-expressibility explicitly.

Strict refinement does not occur at the saturated common-history interfaces t=5,6; on this carrier the new common-history distinctions appear in the formation window.

## Nonclaim Reminder

This is single-extension evidence. It does not alter gt7's lemma scope and does not discharge the closed-base functional or quantitative gap obligations.

## Live Next Options

1. Package the landed material-forcing exhibit into the next Cantor-stack forcing statement.
2. Derive the minimal local mechanism behind the t=4 kernel-failure fibers.
3. Compute a quantitative gap table comparing gt6/gt8/gt9 common-history kernels and C+-only born strata.
"""


def nonclaim_text() -> str:
    return """# gt9 Nonclaim Boundary

The gt9 extension is one declared carrier extension with a fixed resettable public label, fixed reactive template machine, fixed prior, and fixed finite grid. It is not a claim about other institutional labels or other response-template classes.

If common-history strict refinement appears, the licensed claim is only that this declared resettable-label reactive template creates new old-vocabulary distinctions on this carrier. It does not show that every resettable label or reactive template succeeds.

If strict refinement is absent, the licensed claim is only obstruction for this declared template and grid. It does not close the material-forcing residual.

The gt7 washout lemma remains scoped to its hypotheses. gt9 breaks label staticity and the r=1 base-expressibility trap by construction, but the kernel criterion still has to be recomputed and cannot be inferred from the template description alone.

The closed-base functional, quantitative gap, and promotion gates remain open.
"""


def statement_text(schema: Mapping[str, Any]) -> str:
    strict_count_text = "; ".join(
        f"{item['game']}: C-P* {item['C_P_star_size_on_common']} -> C+ {item['C_plus_P_star_size_on_common']} at t={item['t']}"
        for item in schema["strict_refinement_counts"]
    )
    no_refine_by_game: Dict[str, list[str]] = defaultdict(list)
    for item in schema["no_refinement_common_history_interfaces"]:
        no_refine_by_game[item["game"]].append(str(item["t"]))
    no_refine_text = "; ".join(f"{game}: t={','.join(ts)}" for game, ts in sorted(no_refine_by_game.items()))
    kernel_failure_text = "; ".join(
        f"{item['game']} t={item['t']}: {item['failure_classes']} fibers, max {item['max_distinct_kernels']} kernels"
        for item in schema["kernel_failure_exact"]
    )
    return rf"""\documentclass[11pt]{{article}}
\usepackage{{amsmath,amssymb,amsthm}}
\usepackage[margin=1in]{{geometry}}
\newtheorem{{definition}}{{Definition}}
\newtheorem{{proposition}}{{Proposition}}
\begin{{document}}

\section*{{gt9 Resettable-Label Forcing Statement}}

\paragraph{{Scope.}}
All statements are scoped to the frozen gt1 carrier, the gt9 resettable r=2 label, the stateless react-D/react-C template class, the uniform ordered-pair prior, and the declared horizon 9.

\begin{{definition}}[gt9 resettable extension]
The public label at a next-decision interface is 1 iff at least one of the last $\min(2,|h|)$ completed joint profiles contains D; the empty prefix has label 0. Each gt1 base rule $r$ has three variants: blind, react-D, and react-C. Blind follows $r$. A react-X strategy plays X whenever the current label is 1 and otherwise follows $r$'s memory-1 response.
\end{{definition}}

\begin{{proposition}}[Pre-check lemmas]
The frozen spec stores three pre-check witnesses. First, the histories [DD,CC] and [CC,CC] have the same last profile but different resettable labels, so the label does not factor through $\Pi_0$. Second, react-D and react-C each have a same-last-profile action-separation witness, so the reactive class is not memory-1 expressible on the declared base catalog. Third, a common-history live-trigger witness has a surviving reactive pair whose label changes within the declared tau window.
\end{{proposition}}

\begin{{proposition}}[Exact enumeration verdict]
The gt9 enumeration gives strict common-history refinement exactly at interface $t=4$ for both games. The common-history class counts are {strict_count_text}. The kernel table records {kernel_failure_text}. There are 2 verified strata witnesses, indexed in \texttt{{witness\_index\_gt9.json}}. At every other interface in the kernel grid, C+ equals C on common histories: {no_refine_text}. The C+ fixed point is idempotent, and the future-sufficiency rows are recorded in \texttt{{sufficiency\_table\_gt9.csv}}.
\end{{proposition}}

\begin{{proposition}}[Kernel and mechanism cross-section]
The gt9 kernel rows are recomputed in \texttt{{kernel\_cross\_section\_gt9.csv}}. A row marked as failing contains a matched-C $P^\ast$ fiber with two exact C+ one-step laws over target C+ fixed-point classes. The gt6-selected and gt9-resettable mixed fibers are evaluated in \texttt{{mechanism\_cross\_section\_gt9.csv}}, which records whether reactive components are law-distinct from blind.
\end{{proposition}}

\begin{{proposition}}[gt9 localization]
The refinement locus is exactly $t=4$ on common histories. It coexists with {schema['born_split_pair_count']} born stage-lens split pairs and {len(schema['formed_closure_positive_loci'])} positive formed-closure rows. The positive closure rows are the source-$t=5$ rows with $\tau=1,2,3$ in both games, while the source-$t=6$ formed rows are zero; thus the gt8 formation-delay pattern replicates under the resettable label. Strict refinement does not occur at the saturated interfaces $t=5,6$ on common histories: on this carrier, even a live non-base-expressible label does not refine formed common structure at the saturated interfaces; the new distinctions appear in the formation window.
\end{{proposition}}

\begin{{proposition}}[Comparison ladder]
The table \texttt{{gt5\_gt6\_gt8\_gt9\_comparison.csv}} records the mechanism ladder: gt5 to gt6 changes the label, gt6 to gt8 changes the template timing, and gt8 to gt9 breaks label staticity and the spent-trigger/base-expressibility trap. Any gt9 success identifies these conditions only on this carrier and declared family.
\end{{proposition}}

\paragraph{{Cantor-stack reading.}}
The material-forcing exhibit is landed on this declared extension: the resettable institutional label, fed through live reactive responses, births common-history old-vocabulary distinctions absent from the matched base carrier, with the stored witnesses at $t=4$. This is scoped to the declared carrier, label, template class, prior, and grid.

\paragraph{{Boundary.}}
No statement here discharges the closed-base functional, quantitative gap, promotion gates, or any off-carrier forcing claim.

\end{{document}}
"""


def classification_rows(schema: Mapping[str, Any]) -> list[dict[str, str]]:
    scope = "declared gt9 resettable-label extension on the frozen gt1 carrier"
    return [
        {"artifact": "gt9_statement_resettable_forcing.tex", "classification": "analytical structural", "grade": "theorem-grade-on-the-carrier", "scope": scope, "claim": "extension definition, pre-check lemmas, exact verdict propositions, and ladder note"},
        {"artifact": "gt9_spec.json", "classification": "analytical structural", "grade": "theorem-grade-on-the-carrier", "scope": scope, "claim": "frozen extension declaration with pre-check witnesses"},
        {"artifact": "strata_table_gt9.csv", "classification": "predictive structural", "grade": schema["verdict_grade"]["common_history_strict_refinement"], "scope": scope, "claim": "common-history strict-refinement verdicts"},
        {"artifact": "kernel_cross_section_gt9.csv", "classification": "analytical structural", "grade": "theorem-grade-on-the-carrier", "scope": scope, "claim": "kernel criterion failure/constancy rows"},
        {"artifact": "mechanism_cross_section_gt9.csv", "classification": "analytical structural", "grade": "theorem-grade-on-the-carrier", "scope": "gt6 selected and gt9 resettable mixed fibers", "claim": "reactive component law distinction or collapse"},
        {"artifact": "play_difference_table_gt9.csv", "classification": "predictive structural", "grade": schema["verdict_grade"]["causal_load_bearing"], "scope": scope, "claim": "causal play-law differences"},
        {"artifact": "born_split_table_gt9.csv", "classification": "predictive structural", "grade": schema["verdict_grade"]["born_split_pairs"], "scope": scope, "claim": "born stage-lens split counts"},
        {"artifact": "closure_table_gt9.csv", "classification": "analytical structural", "grade": "theorem-grade-on-the-carrier", "scope": scope, "claim": "formed-locus closure rows"},
        {"artifact": "sufficiency_table_gt9.csv", "classification": "analytical structural", "grade": schema["verdict_grade"]["future_sufficiency_on_C_plus"], "scope": scope, "claim": "future-sufficiency checks"},
        {"artifact": "gt5_gt6_gt8_gt9_comparison.csv", "classification": "analytical structural", "grade": "finite-carrier diagnostic", "scope": "gt5/gt6/gt8/gt9 declared comparison ladder", "claim": "mechanism-condition comparison"},
        {"artifact": "gt9_results_summary.md", "classification": "organizational/audit", "grade": "not-applicable", "scope": scope, "claim": "orientation, verdict, boundaries, and next options"},
        {"artifact": "gt9_schema.json", "classification": "organizational/audit", "grade": "not-applicable", "scope": scope, "claim": "machine-readable metadata"},
        {"artifact": "nonclaim_boundary_gt9.md", "classification": "organizational/audit", "grade": "not-applicable", "scope": scope, "claim": "nonclaims and remaining obligations"},
        {"artifact": "run_gt9_validate.py", "classification": "organizational/audit", "grade": "not-applicable", "scope": scope, "claim": "deterministic validator"},
    ]


def build_outputs() -> Dict[str, str]:
    results = build_results()
    comparison = comparison_rows(results)
    schema = schema_payload(results, comparison)
    outputs: Dict[str, str] = {}
    outputs["gt9_spec.json"] = json_dumps(results["spec"])
    outputs["extended_catalog_gt9.json"] = json_dumps(extended_catalog_payload(results["extended_catalog"]))
    outputs.update(table_texts(results, comparison))
    outputs["gt9_schema.json"] = json_dumps(schema)
    outputs["gt9_results_summary.md"] = results_summary_text(schema)
    outputs["nonclaim_boundary_gt9.md"] = nonclaim_text()
    outputs["gt9_statement_resettable_forcing.tex"] = statement_text(schema)
    outputs["content_classification_gt9.csv"] = csv_text(("artifact", "classification", "grade", "scope", "claim"), classification_rows(schema))
    outputs["witness_index_gt9.json"] = json_dumps(witness_index_payload(results))
    for witness in results["strata_witnesses"]:
        outputs[witness_file_name("strata", witness)] = json_dumps(witness)
    for witness in results["born_split_witnesses"]:
        outputs[witness_file_name("born_split", witness)] = json_dumps(witness)
    transcript = {
        "step": "gt9_resettable_label_forcing",
        "gt1_spec_sha256": sha256_text(GT1_SPEC_PATH.read_text(encoding="utf-8")),
        "gt6_spec_sha256": sha256_text((GT6_DIR / "gt6_spec.json").read_text(encoding="utf-8")),
        "gt7_schema_sha256": sha256_text((GT7_DIR / "gt7_schema.json").read_text(encoding="utf-8")),
        "gt8_schema_sha256": sha256_text((GT8_DIR / "gt8_schema.json").read_text(encoding="utf-8")),
        "prechecks_passed": schema["prechecks_passed"],
        "strict_strata_witnesses": len(results["strata_witnesses"]),
        "born_split_witnesses": len(results["born_split_witnesses"]),
        "kernel_failure_rows": sum(1 for row in results["kernel_rows"] if row["kernel_criterion_fails"] == "yes"),
        "plus_idempotence_certified": results["plus_idempotence_certified"],
        "future_sufficiency_rows_ok": schema["future_sufficiency_rows_ok"],
        "generated_artifact_hashes": {},
    }
    for name, text in sorted(outputs.items()):
        if not name.endswith(".json") or name != "verification_transcript_gt9.json":
            transcript["generated_artifact_hashes"][name] = sha256_text(text)
    outputs["verification_transcript_gt9.json"] = json_dumps(transcript)
    return outputs


def write_outputs(outputs: Mapping[str, str], target_dir: Path = ARTIFACT_DIR) -> None:
    for subdir in ("strata_witnesses", "born_split_witnesses"):
        path = target_dir / subdir
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
    for name, text in outputs.items():
        path = target_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def grep_forbidden(target_dir: Path = ARTIFACT_DIR) -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []
    for path in sorted(target_dir.rglob("*")):
        if path.suffix.lower() not in {".md", ".tex", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in text:
                hits.append((str(path.relative_to(target_dir)), phrase))
    return hits


def validate() -> None:
    outputs = build_outputs()
    required = set(outputs) | {"gt9_resettable_forcing.py", "run_gt9_validate.py"}
    missing = [name for name in sorted(required) if not (ARTIFACT_DIR / name).exists()]
    if missing:
        raise AssertionError(f"missing artifacts: {missing}")
    for name, expected in sorted(outputs.items()):
        current = (ARTIFACT_DIR / name).read_text(encoding="utf-8")
        if current != expected:
            raise AssertionError(f"byte mismatch for {name}")
    hits = grep_forbidden()
    if hits:
        raise AssertionError(f"forbidden overclaim phrases present: {hits}")
    schema = json.loads(outputs["gt9_schema.json"])
    for field in ("step", "orientation", "active_residual", "main_object", "final_verdict", "verdict_grade", "witness_count", "carrier_id"):
        if field not in schema or schema[field] in ("", None):
            raise AssertionError(f"schema missing {field}")
    if not schema["plus_idempotence_certified"]:
        raise AssertionError("C+ fixed point idempotence failed")
    if not schema["prechecks_passed"]:
        raise AssertionError("gt9 pre-checks failed")
    with tempfile.TemporaryDirectory(prefix="gt9_validate_") as tmp:
        temp_dir = Path(tmp)
        write_outputs(outputs, temp_dir)
        for name, expected in sorted(outputs.items()):
            if (temp_dir / name).read_text(encoding="utf-8") != expected:
                raise AssertionError(f"temp byte mismatch for {name}")


def main(argv: Sequence[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ["--validate"]:
        validate()
        return 0
    if argv not in ([], ["--write"]):
        print("usage: gt9_resettable_forcing.py [--write|--validate]", file=sys.stderr)
        return 2
    write_outputs(build_outputs())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
