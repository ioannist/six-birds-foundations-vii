from __future__ import annotations

from collections.abc import Callable

from sixbirds_foundations_v.repair_join import Refines, fiber_equiv, repair_join


DOMAIN = ("a", "b", "c", "d")


def _map(mapping: dict[str, object]) -> Callable[[str], object]:
    return lambda x: mapping[x]


q = _map({"a": 0, "b": 0, "c": 1, "d": 1})
r = _map({"a": "left", "b": "right", "c": "left", "d": "right"})
s_discrete = _map({"a": "a", "b": "b", "c": "c", "d": "d"})
t = _map({"a": "top", "b": "middle", "c": "middle", "d": "top"})


def test_join_refines_left() -> None:
    assert repair_join(q, r)("a") == (q("a"), r("a"))
    assert Refines(repair_join(q, r), q, DOMAIN)


def test_join_refines_right() -> None:
    assert Refines(repair_join(q, r), r, DOMAIN)


def test_vee_greatest_lower_bound() -> None:
    assert Refines(s_discrete, q, DOMAIN)
    assert Refines(s_discrete, r, DOMAIN)
    assert Refines(s_discrete, repair_join(q, r), DOMAIN)


def test_join_well_defined_under_fiber_equivalence() -> None:
    q_prime = _map({"a": "Q0", "b": "Q0", "c": "Q1", "d": "Q1"})
    r_prime = _map({"a": 10, "b": 20, "c": 10, "d": 20})

    assert fiber_equiv(q, q_prime, DOMAIN)
    assert fiber_equiv(r, r_prime, DOMAIN)
    assert fiber_equiv(repair_join(q, r), repair_join(q_prime, r_prime), DOMAIN)


def test_join_idem() -> None:
    assert fiber_equiv(repair_join(q, q), q, DOMAIN)


def test_join_comm() -> None:
    assert fiber_equiv(repair_join(q, r), repair_join(r, q), DOMAIN)


def test_join_assoc() -> None:
    assert fiber_equiv(
        repair_join(repair_join(q, r), t),
        repair_join(q, repair_join(r, t)),
        DOMAIN,
    )


def test_refines_rejects_incomparable_fiber_structures() -> None:
    assert not Refines(q, r, DOMAIN)
    assert not Refines(r, q, DOMAIN)
