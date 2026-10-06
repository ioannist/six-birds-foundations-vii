from __future__ import annotations

from sixbirds_foundations_v.institutional import gt1_substrate, gt9_resettable_forcing


def test_gt1_repeated_game_carrier_builds_on_frozen_spec_subset() -> None:
    spec = gt1_substrate.load_spec()
    carrier = gt1_substrate.build_carrier(spec, catalog_ids=["AllC", "AllD"])

    assert carrier.max_history_len >= 1
    assert carrier.pair_ids == ["AllC|AllC", "AllC|AllD", "AllD|AllC", "AllD|AllD"]
    assert carrier.prefix_to_pairs[1]


def test_gt9_resettable_public_label_is_live() -> None:
    assert gt9_resettable_forcing.public_label(()) == "0"
    assert gt9_resettable_forcing.public_label(("CC", "CC")) == "0"
    assert gt9_resettable_forcing.public_label(("CC", "DD")) == "1"
    assert gt9_resettable_forcing.public_label(("DD", "CC", "CC")) == "0"


def test_gt9_resettable_carrier_builds_against_vendored_gt1_subset() -> None:
    spec = gt1_substrate.load_spec()
    full_catalog = gt9_resettable_forcing.make_extended_catalog(gt1_substrate, spec)
    subset = [
        strategy
        for strategy in full_catalog
        if strategy.base_id in {"AllC", "AllD"} and strategy.template_id in {"blind", "reactC"}
    ]
    carrier = gt9_resettable_forcing.build_carrier(
        gt1_substrate,
        spec,
        subset,
        horizon=4,
        carrier_id="test_resettable_subset",
    )

    assert len(subset) == 4
    assert len(carrier.pair_ids) == 16
    reactive_pair = "reactC:AllD|reactC:AllD"
    assert carrier.pair_prefixes[reactive_pair][4] == ("DD", "CC", "CC", "DD")
