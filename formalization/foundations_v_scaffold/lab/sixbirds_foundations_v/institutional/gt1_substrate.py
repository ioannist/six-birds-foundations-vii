#!/usr/bin/env python3
# Copied from six-birds-game-theory/emergence_lab/steps/gt1_substrate_quotients_artifacts/substrate.py.
"""Exact finite repeated-game substrate and quotient enumeration for gt1."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


ARTIFACT_DIR = Path(__file__).resolve().parent
SPEC_PATH = ARTIFACT_DIR / "substrate_spec.json"

ACTIONS = ("C", "D")
PROFILES = ("CC", "CD", "DC", "DD")
LENSES = ("Pi_0", "Pi_1", "Pi_2")
GAME_IDS = ("pd", "stag_hunt")
PRIMARY_LENS = "Pi_2"

FIXED_REQUIRED_FILES = {
    "substrate_spec.json",
    "substrate.py",
    "run_gt1_validate.py",
}

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


@dataclass(frozen=True)
class Automaton:
    id: str
    initial_action: str
    responses: Tuple[str, str, str, str]
    aliases: Tuple[str, ...]

    def response(self, local_profile: str) -> str:
        return self.responses[PROFILES.index(local_profile)]

    def response_map(self) -> Dict[str, str]:
        return {profile: self.responses[i] for i, profile in enumerate(PROFILES)}


def load_spec() -> Dict[str, Any]:
    with SPEC_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def frac_to_str(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def json_dumps(data: Any) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def named_signatures(spec: Mapping[str, Any]) -> Dict[Tuple[str, str, str, str, str], List[str]]:
    out: Dict[Tuple[str, str, str, str, str], List[str]] = defaultdict(list)
    for alias, data in spec["automaton_catalog"]["named_classics"].items():
        responses = data["responses"]
        sig = (
            data["initial_action"],
            responses["CC"],
            responses["CD"],
            responses["DC"],
            responses["DD"],
        )
        out[sig].append(alias)
    return out


def make_catalog(spec: Mapping[str, Any]) -> List[Automaton]:
    names = named_signatures(spec)
    catalog: List[Automaton] = []
    for initial in ACTIONS:
        for responses in itertools.product(ACTIONS, repeat=4):
            sig = (initial,) + tuple(responses)
            aliases = tuple(sorted(names.get(sig, [])))
            response_code = "".join(responses)
            if aliases:
                auto_id = aliases[0]
            else:
                auto_id = f"R_{initial}_{response_code}"
            catalog.append(
                Automaton(
                    id=auto_id,
                    initial_action=initial,
                    responses=tuple(responses),
                    aliases=aliases,
                )
            )
    catalog.sort(key=lambda a: (a.initial_action, "".join(a.responses), a.id))
    if len(catalog) != spec["automaton_catalog"]["catalog_size"]:
        raise ValueError("catalog size does not match frozen spec")
    return catalog


def local_profile(global_profile: str, player: int) -> str:
    if player == 1:
        return global_profile
    if player == 2:
        return global_profile[1] + global_profile[0]
    raise ValueError(f"bad player index {player}")


def next_profile(auto1: Automaton, auto2: Automaton, prefix: Tuple[str, ...]) -> str:
    if not prefix:
        return auto1.initial_action + auto2.initial_action
    last = prefix[-1]
    a1 = auto1.response(local_profile(last, 1))
    a2 = auto2.response(local_profile(last, 2))
    return a1 + a2


def generate_prefix(auto1: Automaton, auto2: Automaton, length: int) -> Tuple[str, ...]:
    prefix: Tuple[str, ...] = ()
    for _ in range(length):
        prefix = prefix + (next_profile(auto1, auto2, prefix),)
    return prefix


def payoff_table(spec: Mapping[str, Any], game: str) -> Dict[str, Tuple[Fraction, Fraction]]:
    table = {}
    for profile, pair in spec["stage_games"][game]["payoffs"].items():
        table[profile] = (parse_fraction(pair[0]), parse_fraction(pair[1]))
    return table


def profile_counts(prefix: Tuple[str, ...]) -> Tuple[int, int, int, int]:
    counter = Counter(prefix)
    return tuple(counter[profile] for profile in PROFILES)


def cumulative_payoff(spec: Mapping[str, Any], game: str, prefix: Tuple[str, ...]) -> Tuple[Fraction, Fraction]:
    payoffs = payoff_table(spec, game)
    total1 = Fraction(0)
    total2 = Fraction(0)
    for profile in prefix:
        p1, p2 = payoffs[profile]
        total1 += p1
        total2 += p2
    return (total1, total2)


def readout_tuple(spec: Mapping[str, Any], game: str, lens: str, prefix: Tuple[str, ...]) -> Tuple[Any, ...]:
    if not prefix:
        raise ValueError("gt1 interfaces start at t=1")
    last = prefix[-1]
    counts = profile_counts(prefix)
    if lens == "Pi_0":
        return ("Pi_0", last)
    if lens == "Pi_1":
        return ("Pi_1", last, counts)
    if lens == "Pi_2":
        payoff = tuple(frac_to_str(v) for v in cumulative_payoff(spec, game, prefix))
        return ("Pi_2", last, counts, payoff)
    raise ValueError(f"unknown lens {lens}")


def readout_to_jsonable(readout: Tuple[Any, ...]) -> Dict[str, Any]:
    lens = readout[0]
    if lens == "Pi_0":
        return {"lens": lens, "last_profile": readout[1]}
    if lens == "Pi_1":
        return {
            "lens": lens,
            "last_profile": readout[1],
            "empirical_counts": {profile: readout[2][i] for i, profile in enumerate(PROFILES)},
        }
    if lens == "Pi_2":
        return {
            "lens": lens,
            "last_profile": readout[1],
            "empirical_counts": {profile: readout[2][i] for i, profile in enumerate(PROFILES)},
            "cumulative_payoff_pair": list(readout[3]),
        }
    raise ValueError(f"unknown readout tuple {readout}")


def prefix_to_jsonable(prefix: Tuple[str, ...]) -> List[str]:
    return list(prefix)


def sequence_to_jsonable(sequence: Tuple[Tuple[Any, ...], ...]) -> List[Dict[str, Any]]:
    return [readout_to_jsonable(readout) for readout in sequence]


def distribution_to_jsonable(distribution: Tuple[Tuple[Tuple[Tuple[Any, ...], ...], Fraction], ...]) -> List[Dict[str, Any]]:
    rows = []
    for outcome, prob in distribution:
        rows.append(
            {
                "outcome": sequence_to_jsonable(outcome),
                "probability": frac_to_str(prob),
            }
        )
    return rows


def distribution_key(distribution: Tuple[Tuple[Tuple[Tuple[Any, ...], ...], Fraction], ...]) -> Tuple[Any, ...]:
    return tuple((outcome, prob) for outcome, prob in distribution)


@dataclass
class CarrierComputation:
    spec: Dict[str, Any]
    catalog: List[Automaton]
    pair_ids: List[str]
    pair_automata: Dict[str, Tuple[Automaton, Automaton]]
    pair_prefixes: Dict[str, Dict[int, Tuple[str, ...]]]
    prefix_to_pairs: Dict[int, Dict[Tuple[str, ...], List[str]]]
    max_history_len: int


def build_carrier(spec: Mapping[str, Any], catalog_ids: Sequence[str] | None = None) -> CarrierComputation:
    catalog = make_catalog(spec)
    if catalog_ids is not None:
        selected = set(catalog_ids)
        catalog = [auto for auto in catalog if auto.id in selected]
        missing = selected - {auto.id for auto in catalog}
        if missing:
            raise ValueError(f"unknown control catalog ids: {sorted(missing)}")

    horizon = max(spec["history_interfaces"]["prefix_lengths"])
    max_tau = max(item["tau"] for item in spec["admissible_continuations"])
    max_history_len = horizon + max_tau

    pair_ids: List[str] = []
    pair_automata: Dict[str, Tuple[Automaton, Automaton]] = {}
    pair_prefixes: Dict[str, Dict[int, Tuple[str, ...]]] = {}
    for auto1 in catalog:
        for auto2 in catalog:
            pair_id = f"{auto1.id}|{auto2.id}"
            pair_ids.append(pair_id)
            pair_automata[pair_id] = (auto1, auto2)
            full = generate_prefix(auto1, auto2, max_history_len)
            pair_prefixes[pair_id] = {n: full[:n] for n in range(max_history_len + 1)}

    prefix_to_pairs: Dict[int, Dict[Tuple[str, ...], List[str]]] = {}
    for t in spec["history_interfaces"]["prefix_lengths"]:
        buckets: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
        for pair_id in pair_ids:
            buckets[pair_prefixes[pair_id][t]].append(pair_id)
        prefix_to_pairs[t] = {prefix: sorted(ids) for prefix, ids in buckets.items()}

    return CarrierComputation(
        spec=dict(spec),
        catalog=catalog,
        pair_ids=pair_ids,
        pair_automata=pair_automata,
        pair_prefixes=pair_prefixes,
        prefix_to_pairs=prefix_to_pairs,
        max_history_len=max_history_len,
    )


def future_distribution(
    carrier: CarrierComputation,
    game: str,
    lens: str,
    t: int,
    prefix: Tuple[str, ...],
    tau: int,
) -> Tuple[Tuple[Tuple[Tuple[Any, ...], ...], Fraction], ...]:
    pair_ids = carrier.prefix_to_pairs[t][prefix]
    denom = len(pair_ids)
    if denom == 0:
        raise ValueError("history has no posterior support")
    outcomes: Counter[Tuple[Tuple[Any, ...], ...]] = Counter()
    for pair_id in pair_ids:
        full_prefix = carrier.pair_prefixes[pair_id][t + tau]
        sequence = tuple(
            readout_tuple(carrier.spec, game, lens, full_prefix[: t + step])
            for step in range(1, tau + 1)
        )
        outcomes[sequence] += 1
    return tuple(
        sorted(
            ((outcome, Fraction(count, denom)) for outcome, count in outcomes.items()),
            key=lambda item: canonical_json(sequence_to_jsonable(item[0])),
        )
    )


def predictive_signature(
    carrier: CarrierComputation,
    game: str,
    lens: str,
    t: int,
    prefix: Tuple[str, ...],
) -> Tuple[Any, ...]:
    current = readout_tuple(carrier.spec, game, lens, prefix)
    future = []
    for cont in carrier.spec["admissible_continuations"]:
        tau = cont["tau"]
        future.append((tau, distribution_key(future_distribution(carrier, game, lens, t, prefix, tau))))
    return (("current", current), ("future", tuple(future)))


def separator_for_pair(
    carrier: CarrierComputation,
    game: str,
    lens: str,
    t: int,
    prefix_a: Tuple[str, ...],
    prefix_b: Tuple[str, ...],
) -> Dict[str, Any]:
    for cont in carrier.spec["admissible_continuations"]:
        tau = cont["tau"]
        dist_a = future_distribution(carrier, game, lens, t, prefix_a, tau)
        dist_b = future_distribution(carrier, game, lens, t, prefix_b, tau)
        if dist_a != dist_b:
            probs_a = {canonical_json(sequence_to_jsonable(outcome)): prob for outcome, prob in dist_a}
            probs_b = {canonical_json(sequence_to_jsonable(outcome)): prob for outcome, prob in dist_b}
            all_keys = sorted(set(probs_a) | set(probs_b))
            for key in all_keys:
                if probs_a.get(key, Fraction(0)) != probs_b.get(key, Fraction(0)):
                    outcome = json.loads(key)
                    return {
                        "continuation": {"type": "play_on", "tau": tau},
                        "later_observable": f"{lens}_readout_sequence_t_plus_1_to_t_plus_{tau}",
                        "separating_outcome": outcome,
                        "probability_a": frac_to_str(probs_a.get(key, Fraction(0))),
                        "probability_b": frac_to_str(probs_b.get(key, Fraction(0))),
                        "distribution_a": distribution_to_jsonable(dist_a),
                        "distribution_b": distribution_to_jsonable(dist_b),
                    }
    raise ValueError("pair is not predictively separated")


def quotient_metrics(
    carrier: CarrierComputation,
    game: str,
    lens: str,
    t: int,
) -> Dict[str, Any]:
    histories = sorted(carrier.prefix_to_pairs[t].keys())
    current_by_prefix: Dict[Tuple[str, ...], Tuple[Any, ...]] = {}
    predictive_by_prefix: Dict[Tuple[str, ...], Tuple[Any, ...]] = {}
    current_groups: Dict[Tuple[Any, ...], List[Tuple[str, ...]]] = defaultdict(list)
    pred_groups: Dict[Tuple[Any, ...], List[Tuple[str, ...]]] = defaultdict(list)
    for prefix in histories:
        current = readout_tuple(carrier.spec, game, lens, prefix)
        pred = predictive_signature(carrier, game, lens, t, prefix)
        current_by_prefix[prefix] = current
        predictive_by_prefix[prefix] = pred
        current_groups[current].append(prefix)
        pred_groups[pred].append(prefix)

    witness_count = 0
    max_fiber = 0
    for current, prefixes in current_groups.items():
        pred_counter = Counter(predictive_by_prefix[prefix] for prefix in prefixes)
        max_fiber = max(max_fiber, len(pred_counter))
        n = len(prefixes)
        same_current_pairs = n * (n - 1) // 2
        same_predictive_pairs = sum(count * (count - 1) // 2 for count in pred_counter.values())
        witness_count += same_current_pairs - same_predictive_pairs

    return {
        "game": game,
        "lens": lens,
        "t": t,
        "history_count": len(histories),
        "current_quotient_size": len(current_groups),
        "predictive_quotient_size": len(pred_groups),
        "max_fiber_size": max_fiber,
        "strict_refinement": witness_count > 0,
        "witness_count": witness_count,
        "current_by_prefix": current_by_prefix,
        "predictive_by_prefix": predictive_by_prefix,
        "current_groups": current_groups,
    }


def first_witness(
    carrier: CarrierComputation,
    game: str,
    lens: str,
    t: int,
) -> Dict[str, Any] | None:
    metrics = quotient_metrics(carrier, game, lens, t)
    pred = metrics["predictive_by_prefix"]
    for current in sorted(metrics["current_groups"], key=lambda item: canonical_json(readout_to_jsonable(item))):
        prefixes = sorted(metrics["current_groups"][current])
        for idx, prefix_a in enumerate(prefixes):
            for prefix_b in prefixes[idx + 1 :]:
                if pred[prefix_a] != pred[prefix_b]:
                    separator = separator_for_pair(carrier, game, lens, t, prefix_a, prefix_b)
                    return {
                        "game": game,
                        "lens": lens,
                        "interface_t": t,
                        "witness_ordinal": 1,
                        "history_a": prefix_a,
                        "history_b": prefix_b,
                        "current_readout": current,
                        "separator": separator,
                        "posterior_support_count_a": len(carrier.prefix_to_pairs[t][prefix_a]),
                        "posterior_support_count_b": len(carrier.prefix_to_pairs[t][prefix_b]),
                        "locus_witness_count": metrics["witness_count"],
                    }
    return None


def witnesses_for_locus(
    carrier: CarrierComputation,
    game: str,
    lens: str,
    t: int,
) -> List[Dict[str, Any]]:
    metrics = quotient_metrics(carrier, game, lens, t)
    pred = metrics["predictive_by_prefix"]
    witnesses: List[Dict[str, Any]] = []
    ordinal = 1
    for current in sorted(metrics["current_groups"], key=lambda item: canonical_json(readout_to_jsonable(item))):
        prefixes = sorted(metrics["current_groups"][current])
        for idx, prefix_a in enumerate(prefixes):
            for prefix_b in prefixes[idx + 1 :]:
                if pred[prefix_a] != pred[prefix_b]:
                    separator = separator_for_pair(carrier, game, lens, t, prefix_a, prefix_b)
                    witnesses.append(
                        {
                            "game": game,
                            "lens": lens,
                            "interface_t": t,
                            "witness_ordinal": ordinal,
                            "history_a": prefix_a,
                            "history_b": prefix_b,
                            "current_readout": current,
                            "separator": separator,
                            "posterior_support_count_a": len(carrier.prefix_to_pairs[t][prefix_a]),
                            "posterior_support_count_b": len(carrier.prefix_to_pairs[t][prefix_b]),
                            "locus_witness_count": metrics["witness_count"],
                        }
                    )
                    ordinal += 1
    if len(witnesses) != metrics["witness_count"]:
        raise ValueError("witness enumeration count mismatch")
    return witnesses


def all_metrics(carrier: CarrierComputation) -> List[Dict[str, Any]]:
    rows = []
    for game in GAME_IDS:
        for lens in LENSES:
            for t in carrier.spec["history_interfaces"]["prefix_lengths"]:
                rows.append(quotient_metrics(carrier, game, lens, t))
    return rows


def control_metrics(spec: Mapping[str, Any]) -> List[Dict[str, Any]]:
    control = build_carrier(spec, catalog_ids=("AllC", "AllD"))
    rows = []
    for t in spec["null_control"]["interfaces"]:
        metrics = quotient_metrics(control, GAME_IDS[0], spec["null_control"]["lens"], t)
        rows.append(
            {
                "control_carrier_id": spec["null_control"]["carrier_id"],
                "game": GAME_IDS[0],
                "lens": spec["null_control"]["lens"],
                "t": t,
                "history_count": metrics["history_count"],
                "current_quotient_size": metrics["current_quotient_size"],
                "predictive_quotient_size": metrics["predictive_quotient_size"],
                "max_fiber_size": metrics["max_fiber_size"],
                "witness_count": metrics["witness_count"],
                "closed": metrics["current_quotient_size"] == metrics["predictive_quotient_size"]
                and metrics["witness_count"] == 0,
            }
        )
    return rows


def choose_primary_witnesses(carrier: CarrierComputation, metrics_rows: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    witnesses = []
    for game in GAME_IDS:
        candidates = [
            row for row in metrics_rows
            if row["game"] == game and row["lens"] == PRIMARY_LENS and row["witness_count"] > 0
        ]
        if not candidates:
            continue
        chosen = sorted(candidates, key=lambda row: (row["t"], -row["witness_count"]))[0]
        locus_witnesses = witnesses_for_locus(carrier, game, PRIMARY_LENS, chosen["t"])
        if not locus_witnesses:
            raise ValueError("metrics reported a witness but none was found")
        witnesses.extend(locus_witnesses)
    return witnesses


def compact_metric_row(row: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "game": row["game"],
        "lens": row["lens"],
        "t": row["t"],
        "history_count": row["history_count"],
        "current_quotient_size": row["current_quotient_size"],
        "predictive_quotient_size": row["predictive_quotient_size"],
        "max_fiber_size": row["max_fiber_size"],
        "strict_refinement": row["strict_refinement"],
        "witness_count": row["witness_count"],
    }


def witness_file_name(witness: Mapping[str, Any]) -> str:
    ordinal = int(witness.get("witness_ordinal", 1))
    return f"witnesses/gt1_witness_{witness['game']}_{witness['lens']}_t{witness['interface_t']}_{ordinal:03d}.json"


def witness_to_jsonable(carrier: CarrierComputation, witness: Mapping[str, Any]) -> Dict[str, Any]:
    prefix_a = witness["history_a"]
    prefix_b = witness["history_b"]
    t = witness["interface_t"]
    game = witness["game"]
    lens = witness["lens"]
    current_a = readout_tuple(carrier.spec, game, lens, prefix_a)
    current_b = readout_tuple(carrier.spec, game, lens, prefix_b)
    if current_a != current_b:
        raise ValueError("stored witness histories are not current-equivalent")
    sep = witness["separator"]
    transcript = {
        "verification_rule": "Recompute current readouts and exact future distributions from substrate_spec.json and the generated automaton catalog.",
        "history_a_posterior_support_count": witness["posterior_support_count_a"],
        "history_b_posterior_support_count": witness["posterior_support_count_b"],
        "current_readout_equal": True,
        "separating_probabilities_differ": sep["probability_a"] != sep["probability_b"],
        "locus_witness_count": witness["locus_witness_count"],
    }
    return {
        "witness_id": f"gt1_{game}_{lens}_t{t}_{int(witness.get('witness_ordinal', 1)):03d}",
        "carrier_id": carrier.spec["carrier_id"],
        "game": game,
        "lens": lens,
        "interface_t": t,
        "history_a": prefix_to_jsonable(prefix_a),
        "history_b": prefix_to_jsonable(prefix_b),
        "current_readout": readout_to_jsonable(current_a),
        "separating_continuation": sep["continuation"],
        "later_observable": sep["later_observable"],
        "separating_outcome": sep["separating_outcome"],
        "probability_a": sep["probability_a"],
        "probability_b": sep["probability_b"],
        "distribution_a": sep["distribution_a"],
        "distribution_b": sep["distribution_b"],
        "verification_transcript": transcript,
    }


def csv_text(fieldnames: Sequence[str], rows: Sequence[Mapping[str, Any]]) -> str:
    from io import StringIO

    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fieldnames})
    return buf.getvalue()


def automata_catalog_json(catalog: Sequence[Automaton]) -> str:
    data = {
        "catalog_size": len(catalog),
        "local_profile_order": list(PROFILES),
        "automata": [
            {
                "id": auto.id,
                "initial_action": auto.initial_action,
                "responses": auto.response_map(),
                "aliases": list(auto.aliases),
            }
            for auto in catalog
        ],
    }
    return json_dumps(data)


def build_results() -> Dict[str, Any]:
    spec = load_spec()
    carrier = build_carrier(spec)
    metrics_rows = all_metrics(carrier)
    compact_rows = [compact_metric_row(row) for row in metrics_rows]
    control_rows = control_metrics(spec)
    primary_witnesses = choose_primary_witnesses(carrier, metrics_rows)
    witness_payloads = {
        witness_file_name(witness): witness_to_jsonable(carrier, witness)
        for witness in primary_witnesses
    }
    primary_loci = [
        row for row in compact_rows if row["lens"] == PRIMARY_LENS and row["witness_count"] > 0
    ]
    earliest_primary = {}
    for game in GAME_IDS:
        game_rows = [row for row in primary_loci if row["game"] == game]
        earliest_primary[game] = sorted(game_rows, key=lambda row: row["t"])[0] if game_rows else None
    return {
        "spec": spec,
        "carrier": carrier,
        "metrics_rows": compact_rows,
        "control_rows": control_rows,
        "primary_witnesses": primary_witnesses,
        "witness_payloads": witness_payloads,
        "earliest_primary": earliest_primary,
    }


def quotient_table_text(rows: Sequence[Mapping[str, Any]]) -> str:
    table_rows = []
    for row in rows:
        table_rows.append(
            {
                "game": row["game"],
                "lens": row["lens"],
                "t": row["t"],
                "history_count": row["history_count"],
                "Q_size": row["current_quotient_size"],
                "M_size": row["predictive_quotient_size"],
                "max_fiber_size": row["max_fiber_size"],
                "strict_refinement": "yes" if row["strict_refinement"] else "no",
                "witness_count": row["witness_count"],
            }
        )
    return csv_text(
        ("game", "lens", "t", "history_count", "Q_size", "M_size", "max_fiber_size", "strict_refinement", "witness_count"),
        table_rows,
    )


def witness_counts_text(rows: Sequence[Mapping[str, Any]]) -> str:
    table_rows = [
        {
            "game": row["game"],
            "lens": row["lens"],
            "t": row["t"],
            "witness_count": row["witness_count"],
            "scope": "declared carrier, declared lens, declared interface, declared play-on continuation catalog",
        }
        for row in rows
    ]
    return csv_text(("game", "lens", "t", "witness_count", "scope"), table_rows)


def control_table_text(rows: Sequence[Mapping[str, Any]]) -> str:
    table_rows = [
        {
            "control_carrier_id": row["control_carrier_id"],
            "game": row["game"],
            "lens": row["lens"],
            "t": row["t"],
            "history_count": row["history_count"],
            "Q_size": row["current_quotient_size"],
            "M_size": row["predictive_quotient_size"],
            "max_fiber_size": row["max_fiber_size"],
            "witness_count": row["witness_count"],
            "closed": "yes" if row["closed"] else "no",
            "scope": "memory-0 constant-strategy restriction with declared Pi_0 lens and play-on continuation catalog",
        }
        for row in rows
    ]
    return csv_text(
        ("control_carrier_id", "game", "lens", "t", "history_count", "Q_size", "M_size", "max_fiber_size", "witness_count", "closed", "scope"),
        table_rows,
    )


def schema_payload(results: Mapping[str, Any]) -> Dict[str, Any]:
    rows = results["metrics_rows"]
    control_rows = results["control_rows"]
    primary = results["earliest_primary"]
    total_witnesses = sum(row["witness_count"] for row in rows)
    target_witnesses = sum((row["witness_count"] if row else 0) for row in primary.values())
    verdict = (
        "Strict refinement instantiated at Pi_2 for both declared payoff families; "
        "the memory-0 constant-strategy control is closed on Pi_0."
        if target_witnesses > 0 and all(row["closed"] for row in control_rows)
        else "Obstruction recorded on the declared gt1 grid."
    )
    return {
        "step": "gt1_substrate_quotients",
        "orientation": "ADEQUACY",
        "active_residual": "R0.1",
        "main_object": "Frozen exact finite repeated-game carrier with current and predictive quotients.",
        "final_verdict": verdict,
        "verdict_grade": {
            "quotient_enumeration": "theorem-grade-on-the-carrier",
            "strict_refinement_at_target_loci": "theorem-grade-on-the-carrier",
            "witness_density_interpretation": "finite-carrier diagnostic",
            "null_control_closure": "theorem-grade-on-the-carrier",
        },
        "witness_count": total_witnesses,
        "carrier_id": results["spec"]["carrier_id"],
        "stage_games": list(GAME_IDS),
        "lens_hierarchy": list(LENSES),
        "history_interfaces": results["spec"]["history_interfaces"]["prefix_lengths"],
        "continuation_taus": [item["tau"] for item in results["spec"]["admissible_continuations"]],
        "automaton_catalog_size": len(results["carrier"].catalog),
        "prior": results["spec"]["prior"],
        "target_lens": PRIMARY_LENS,
        "target_loci": primary,
        "target_witness_count": target_witnesses,
        "stored_witness_files": sorted(results["witness_payloads"].keys()),
        "null_control": {
            "carrier_id": results["spec"]["null_control"]["carrier_id"],
            "closed_all_declared_interfaces": all(row["closed"] for row in control_rows),
            "rows": control_rows,
        },
        "pi2_redundancy": "At fixed game and t, Pi_2 payoff pair is determined by Pi_1 counts and the payoff table.",
        "artifact_scope": "declared finite carrier, declared lenses, declared interfaces, declared prior, declared continuation catalog",
    }


def summary_text(results: Mapping[str, Any]) -> str:
    schema = schema_payload(results)
    primary = schema["target_loci"]
    pd = primary.get("pd")
    sh = primary.get("stag_hunt")
    pd_line = "none" if pd is None else f"t={pd['t']}, |Q|={pd['current_quotient_size']}, |M|={pd['predictive_quotient_size']}, witnesses={pd['witness_count']}"
    sh_line = "none" if sh is None else f"t={sh['t']}, |Q|={sh['current_quotient_size']}, |M|={sh['predictive_quotient_size']}, witnesses={sh['witness_count']}"
    witness_file_count = len(results["witness_payloads"])
    witness_files = f"{witness_file_count} files under `witnesses/`; see `primary_witness_index.json`."
    return f"""# gt1 Results Summary

## Orientation

Orientation: ADEQUACY. Active residual: R0.1. The manager specified the repeated-game family; this step freezes the remaining carrier choices, computes the Holonomy-style current/predictive quotients, and performs the first split-pair search on that declared grid.

## Main Object

Carrier `gt1_full_memory1_reactive_v1` contains the two declared payoff families, a complete 32-rule deterministic memory-1 reactive automaton catalog over local last joint action, a uniform exact prior over 1024 ordered automaton pairs, prefix interfaces `t=1..6`, and play-on continuations for `tau=1,2,3`. Histories are generated joint-action prefixes; predictive laws are exact conditional distributions under the frozen prior restricted to automaton pairs consistent with the prefix.

The richest recorded lens is `Pi_2`, but it is not treated as strictly richer than `Pi_1`: at fixed game and interface `t`, cumulative payoff is determined by `Pi_1`'s joint-action counts and the declared payoff table.

## Move

The runner enumerated every generated prefix, formed `Q` by exact current readout equality, formed `M` by exact equality of the current readout plus all declared play-on future readout distributions, and counted every unordered split pair in each current fiber.

## Verdicts

Strict refinement instantiated on the declared carrier at the richest recorded lens:

- `pd`, `Pi_2`: {pd_line}.
- `stag_hunt`, `Pi_2`: {sh_line}.

Grade: theorem-grade-on-the-carrier for the quotient enumeration and split-pair existence at the declared loci. The density pattern across the grid is a finite-carrier diagnostic.

Stored target witness files: {witness_files}

Null control: the memory-0 constant-strategy restriction with `Pi_0` is closed at every declared interface (`M=Q`, zero witnesses). Grade: theorem-grade-on-the-carrier for that restricted control.

## Deflationary Reading

The split-pair behavior is expected recovery-grade non-vacuity: reactive and grim-trigger-style histories can share the same stage signature while carrying different posterior evidence about the automaton pair. The new gt1 content is the frozen carrier, exact quotient machinery, enumeration-complete witness counts, and closed null control.

## Outputs

- `substrate_spec.json`: frozen carrier declaration.
- `automata_catalog.json`: final deduplicated 32-rule catalog with named aliases.
- `quotient_table_gt1.csv`: `|Q|`, `|M|`, max fiber size, and witness counts per `(game,lens,t)`.
- `witness_counts_gt1.csv`: density table for every declared grid point.
- `null_control_table_gt1.csv`: closed-control table.
- `witnesses/*.json`: primary verified witness files.
- `gt1_statement_substrate_quotients.tex`: formal carrier statement and enumeration propositions.
- `run_gt1_validate.py`: single entry point that recomputes the construction and validates artifacts.

## Active Residual

R0.1 is reduced to the next layer of obligations: the carrier now exists, but closure-deficit tables, intervention loops, and promotion-gate audits have not been run on it.

## Current Frontier

1. Compute exact `CD_tau(Pi_k)` tables from the frozen prior/posterior process on this carrier.
2. Construct play-on or simple impose-remove loop candidates for a later hysteresis step, keeping intervention catalogs separate from gt1.
3. Build the first promotion-gate audit around the accepted `Pi_2` split-pair loci, including no-smuggling and visibility checks.
"""


def nonclaim_text(results: Mapping[str, Any]) -> str:
    schema = schema_payload(results)
    return f"""# gt1 Nonclaim Boundary

The gt1 strict-refinement claim is scoped to carrier `{schema['carrier_id']}`, the declared payoff tables, the 32-rule memory-1 reactive catalog, the uniform ordered-pair prior, interfaces `t=1..6`, lenses `Pi_0..Pi_2`, and play-on continuations `tau=1,2,3`.

The witness claim does not extend beyond this finite carrier. It does not classify other strategy catalogs, other priors, other horizons, other continuation catalogs, or other payoff families.

The primary split pairs are recovery-grade non-vacuity. They show that the machinery detects expected hidden posterior distinctions in repeated play; they are not presented as a new behavioral discovery.

`Pi_2` is not claimed to be a strict lens refinement of `Pi_1` here. At fixed game and interface `t`, cumulative payoff is derivable from the `Pi_1` joint-action counts and the declared payoff table.

The null control proves only that the same quotient machinery returns closure on the memory-0 constant-strategy restriction with `Pi_0`. It is not a classification of every possible control.

No closure-deficit table, hysteresis loop, promotion-gate verdict, welfare statement, empirical bridge, or selection claim is discharged in gt1.
"""


def statement_text(results: Mapping[str, Any]) -> str:
    schema = schema_payload(results)
    pd = schema["target_loci"]["pd"]
    sh = schema["target_loci"]["stag_hunt"]
    control_ok = schema["null_control"]["closed_all_declared_interfaces"]
    template = r"""\documentclass[11pt]{article}
\usepackage{amsmath,amssymb,amsthm}
\usepackage[margin=1in]{geometry}

\newtheorem{definition}{Definition}
\newtheorem{proposition}{Proposition}

\begin{document}

\title{gt1 Statement: Frozen Substrate, Quotients, and Split-Pair Enumeration}
\date{}
\maketitle

\section{Declared Carrier}

The carrier is the finite repeated-game substrate recorded in \texttt{substrate\_spec.json} under identifier \texttt{__CARRIER_ID__}. The action set is \(\{C,D\}\), the joint-profile set is \(\Omega=\{CC,CD,DC,DD\}\), and the payoff families are the two declared \(2\times2\) tables in the frozen specification. The automaton catalog contains every deterministic memory-one reactive rule of the form
\[
(\alpha,r_{CC},r_{CD},r_{DC},r_{DD})\in \{C,D\}^5,
\]
where \(\alpha\) is the initial action and \(r_{\omega}\) is the response to the local previous profile \(\omega=(\text{own last action},\text{opponent last action})\). The named strategies AllC, AllD, TFT, Grim, and WSLS are aliases of entries in this catalog after deduplication.

The prior is uniform on ordered automaton pairs. A history at interface \(t\in\{1,\ldots,6\}\) is a generated joint-action prefix \(h=(\omega_1,\ldots,\omega_t)\) with nonempty posterior support. The admissible gt1 continuations are play-on maps for \(\tau\in\{1,2,3\}\).

\section{Lens Hierarchy}

\begin{definition}[Stage lenses]
At interface \(t\), the three current readouts are:
\[
\Pi_0(h)=\omega_t,
\]
\[
\Pi_1(h)=\left(\omega_t,\,(n_{CC}(h),n_{CD}(h),n_{DC}(h),n_{DD}(h))\right),
\]
and
\[
\Pi_2(h)=\left(\Pi_1(h),\,\sum_{s=1}^t u(\omega_s)\right),
\]
where \(u(\omega)\) is the declared payoff pair for the active game.
\end{definition}

\begin{proposition}[Pi\(_2\) reduction on the declared carrier]
For a fixed game and fixed interface \(t\), \(\Pi_2\) factors through \(\Pi_1\).
\end{proposition}

\begin{proof}
The payoff table assigns a fixed payoff pair \(u(\omega)\) to each joint profile \(\omega\). The cumulative payoff pair is
\[
\sum_{\omega\in\Omega} n_{\omega}(h)u(\omega).
\]
The counts \(n_{\omega}(h)\) are part of \(\Pi_1(h)\), so the payoff component of \(\Pi_2(h)\) is determined by \(\Pi_1(h)\) and the declared payoff table.
\end{proof}

\section{Current and Predictive Quotients}

\begin{definition}[Current quotient]
For a lens \(\Pi_k\), histories \(h,h'\) at the same interface are current-equivalent when \(\Pi_k(h)=\Pi_k(h')\). The quotient is denoted \(Q_{g,k,t}\).
\end{definition}

\begin{definition}[Predictive quotient]
For a lens \(\Pi_k\), a game \(g\), and an interface \(t\), the predictive signature of \(h\) is the pair consisting of its current readout \(\Pi_k(h)\) and, for each declared play-on continuation \(\tau\), the exact conditional distribution of the sequence
\[
\left(\Pi_k(h_{t+1}),\ldots,\Pi_k(h_{t+\tau})\right)
\]
under the uniform prior restricted to automaton pairs consistent with \(h\). Two histories are predictively equivalent when these signatures are equal. The quotient is denoted \(M_{g,k,t}\).
\end{definition}

This is the Holonomy-with-Memory quotient definition specialized to a finite repeated-game support: histories are play prefixes, interfaces are prefix lengths, continuations are declared play-on maps, and events are the declared lens readouts. The current readout is included in the predictive signature, implementing the identity/current component that makes \(M_{g,k,t}\) refine \(Q_{g,k,t}\).

\section{Enumeration Propositions}

\begin{proposition}[Strict refinement at the richest recorded lens]
On the declared carrier, \(M\) strictly refines \(Q\) at the following recorded loci:
\[
\text{PD},\Pi_2,t=__PD_T__:\quad |Q|=__PD_Q__,\ |M|=__PD_M__,\ \text{witnesses}=__PD_WIT__,
\]
\[
\text{StagHunt},\Pi_2,t=__SH_T__:\quad |Q|=__SH_Q__,\ |M|=__SH_M__,\ \text{witnesses}=__SH_WIT__.
\]
\end{proposition}

\begin{proof}
The script \texttt{run\_gt1\_validate.py} recomputes the automaton-pair posterior supports, current readouts, future conditional distributions, quotient partitions, and split-pair counts from \texttt{substrate\_spec.json}. The table \texttt{quotient\_table\_gt1.csv} is the enumeration transcript. A split pair is counted exactly when two histories share a \(Q\)-class and have different predictive signatures.
\end{proof}

\begin{proposition}[Closed null control]
On the memory-zero constant-strategy restriction \(\{\text{AllC},\text{AllD}\}\), using \(\Pi_0\), the gt1 quotient computation has \(M=Q\) and zero split pairs at each declared interface.
\end{proposition}

\begin{proof}
The validation script recomputes the restricted carrier. The transcript is \texttt{null\_control\_table\_gt1.csv}. The recorded closed flag is \texttt{__CONTROL_OK__} for every declared control row.
\end{proof}

\end{document}
"""
    replacements = {
        "__CARRIER_ID__": schema["carrier_id"],
        "__PD_T__": str(pd["t"]),
        "__PD_Q__": str(pd["current_quotient_size"]),
        "__PD_M__": str(pd["predictive_quotient_size"]),
        "__PD_WIT__": str(pd["witness_count"]),
        "__SH_T__": str(sh["t"]),
        "__SH_Q__": str(sh["current_quotient_size"]),
        "__SH_M__": str(sh["predictive_quotient_size"]),
        "__SH_WIT__": str(sh["witness_count"]),
        "__CONTROL_OK__": str(control_ok).lower(),
    }
    for old, new in replacements.items():
        template = template.replace(old, new)
    return template


def witness_index_payload(results: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "carrier_id": results["spec"]["carrier_id"],
        "primary_lens": PRIMARY_LENS,
        "witness_files": [
            {
                "path": path,
                "game": payload["game"],
                "lens": payload["lens"],
                "interface_t": payload["interface_t"],
                "locus_witness_count": payload["verification_transcript"]["locus_witness_count"],
            }
            for path, payload in sorted(results["witness_payloads"].items())
        ],
        "scope": "declared finite carrier and declared play-on continuation catalog",
    }


def transcript_payload(results: Mapping[str, Any], artifact_hashes: Mapping[str, str]) -> Dict[str, Any]:
    return {
        "step": "gt1_substrate_quotients",
        "carrier_id": results["spec"]["carrier_id"],
        "recomputed": True,
        "metric_rows": len(results["metrics_rows"]),
        "control_rows": len(results["control_rows"]),
        "stored_witness_files": sorted(results["witness_payloads"].keys()),
        "artifact_hashes": dict(sorted(artifact_hashes.items())),
    }


def classification_text(results: Mapping[str, Any], paths: Iterable[str]) -> str:
    rows = []
    predictive = {
        "substrate_spec.json",
        "automata_catalog.json",
        "quotient_table_gt1.csv",
        "witness_counts_gt1.csv",
        "null_control_table_gt1.csv",
        "primary_witness_index.json",
    }
    analytical = {"gt1_statement_substrate_quotients.tex"}
    audit = {
        "gt1_results_summary.md",
        "gt1_schema.json",
        "content_classification_gt1.csv",
        "nonclaim_boundary_gt1.md",
        "run_gt1_validate.py",
        "substrate.py",
        "verification_transcript_gt1.json",
    }
    for path in sorted(paths):
        if path.startswith("witnesses/"):
            classification = "predictive structural"
            grade = "theorem-grade-on-the-carrier"
        elif path in predictive:
            classification = "predictive structural"
            grade = "theorem-grade-on-the-carrier" if path.endswith(".csv") or path.endswith(".json") else "finite-carrier diagnostic"
        elif path in analytical:
            classification = "analytical structural"
            grade = "theorem-grade-on-the-carrier"
        elif path in audit:
            classification = "organizational/audit"
            grade = "organizational/audit"
        else:
            classification = "remaining external content"
            grade = "not applicable"
        rows.append(
            {
                "artifact": path,
                "classification": classification,
                "grade": grade,
                "scope": "gt1 declared finite carrier and declared continuation catalog",
            }
        )
    return csv_text(("artifact", "classification", "grade", "scope"), rows)


def build_payloads(results: Mapping[str, Any]) -> Dict[str, str]:
    payloads: Dict[str, str] = {}
    payloads["automata_catalog.json"] = automata_catalog_json(results["carrier"].catalog)
    payloads["quotient_table_gt1.csv"] = quotient_table_text(results["metrics_rows"])
    payloads["witness_counts_gt1.csv"] = witness_counts_text(results["metrics_rows"])
    payloads["null_control_table_gt1.csv"] = control_table_text(results["control_rows"])
    payloads["gt1_results_summary.md"] = summary_text(results)
    payloads["gt1_schema.json"] = json_dumps(schema_payload(results))
    payloads["nonclaim_boundary_gt1.md"] = nonclaim_text(results)
    payloads["gt1_statement_substrate_quotients.tex"] = statement_text(results)
    payloads["primary_witness_index.json"] = json_dumps(witness_index_payload(results))
    for path, witness in results["witness_payloads"].items():
        payloads[path] = json_dumps(witness)

    all_paths_for_classification = set(payloads) | FIXED_REQUIRED_FILES | {"content_classification_gt1.csv", "verification_transcript_gt1.json"}
    payloads["content_classification_gt1.csv"] = classification_text(results, all_paths_for_classification)

    artifact_hashes = {
        path: sha256_text(text)
        for path, text in payloads.items()
        if path != "verification_transcript_gt1.json"
    }
    payloads["verification_transcript_gt1.json"] = json_dumps(transcript_payload(results, artifact_hashes))
    return payloads


def write_artifacts() -> Dict[str, Any]:
    results = build_results()
    payloads = build_payloads(results)
    witness_dir = ARTIFACT_DIR / "witnesses"
    witness_dir.mkdir(parents=True, exist_ok=True)
    for old_witness in witness_dir.glob("*.json"):
        old_witness.unlink()
    for rel_path, text in payloads.items():
        path = ARTIFACT_DIR / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return results


def check_forbidden_phrases() -> List[str]:
    violations = []
    for path in ARTIFACT_DIR.rglob("*"):
        if path.suffix.lower() not in {".md", ".tex", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in text:
                violations.append(f"{path.relative_to(ARTIFACT_DIR)} contains forbidden phrase: {phrase}")
    return violations


def validate_witness_file(carrier: CarrierComputation, rel_path: str) -> None:
    path = ARTIFACT_DIR / rel_path
    data = json.loads(path.read_text(encoding="utf-8"))
    prefix_a = tuple(data["history_a"])
    prefix_b = tuple(data["history_b"])
    game = data["game"]
    lens = data["lens"]
    t = data["interface_t"]
    if prefix_a not in carrier.prefix_to_pairs[t]:
        raise AssertionError(f"{rel_path}: history_a not generated")
    if prefix_b not in carrier.prefix_to_pairs[t]:
        raise AssertionError(f"{rel_path}: history_b not generated")
    current_a = readout_tuple(carrier.spec, game, lens, prefix_a)
    current_b = readout_tuple(carrier.spec, game, lens, prefix_b)
    if current_a != current_b:
        raise AssertionError(f"{rel_path}: histories are not current-equivalent")
    pred_a = predictive_signature(carrier, game, lens, t, prefix_a)
    pred_b = predictive_signature(carrier, game, lens, t, prefix_b)
    if pred_a == pred_b:
        raise AssertionError(f"{rel_path}: histories are not predictively separated")
    sep = separator_for_pair(carrier, game, lens, t, prefix_a, prefix_b)
    if sep["continuation"] != data["separating_continuation"]:
        raise AssertionError(f"{rel_path}: separating continuation mismatch")
    if sep["probability_a"] != data["probability_a"] or sep["probability_b"] != data["probability_b"]:
        raise AssertionError(f"{rel_path}: separating probabilities mismatch")


def validate_schema_fields() -> None:
    path = ARTIFACT_DIR / "gt1_schema.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    required = [
        "step",
        "orientation",
        "active_residual",
        "main_object",
        "final_verdict",
        "verdict_grade",
        "witness_count",
        "carrier_id",
    ]
    missing = [field for field in required if field not in data or data[field] in ("", None)]
    if missing:
        raise AssertionError(f"schema missing required fields: {missing}")


def validate_artifacts() -> None:
    results = build_results()
    payloads = build_payloads(results)
    errors: List[str] = []

    for rel_path in sorted(set(payloads) | FIXED_REQUIRED_FILES):
        path = ARTIFACT_DIR / rel_path
        if not path.exists():
            errors.append(f"missing artifact: {rel_path}")
            continue
        if rel_path in payloads:
            actual = path.read_text(encoding="utf-8")
            if actual != payloads[rel_path]:
                errors.append(f"artifact is not reproducible from substrate.py: {rel_path}")

    try:
        validate_schema_fields()
    except Exception as exc:  # pragma: no cover
        errors.append(str(exc))

    for rel_path in sorted(results["witness_payloads"]):
        try:
            validate_witness_file(results["carrier"], rel_path)
        except Exception as exc:  # pragma: no cover
            errors.append(str(exc))

    errors.extend(check_forbidden_phrases())

    if errors:
        for err in errors:
            print(f"VALIDATION ERROR: {err}", file=sys.stderr)
        raise SystemExit(1)
    print("gt1 validation passed")


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if args == ["--validate"]:
        validate_artifacts()
        return 0
    if args:
        print("usage: substrate.py [--validate]", file=sys.stderr)
        return 2
    write_artifacts()
    print("gt1 artifacts written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
