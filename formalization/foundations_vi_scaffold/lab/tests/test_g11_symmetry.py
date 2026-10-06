from foundations_vi_lab.g11_symmetry.wang_sat import (
    CONTROL_TILES,
    JEANDEL_RAO_TILES,
    TorusInstance,
    encode_torus,
    solve_torus,
    validate_assignment,
    variable_id,
)


def test_variable_numbering_for_tiny_instance() -> None:
    assert variable_id(1, 1, 2, 0, 0, 0) == 1
    assert variable_id(1, 1, 2, 0, 0, 1) == 2


def test_control_1x1_clause_shape_and_assignment(tmp_path) -> None:
    instance = TorusInstance(CONTROL_TILES, 1, 1)
    cnf = encode_torus(instance)

    assert cnf.nv == 2
    assert [1, 2] in cnf.clauses
    assert [-1, -2] in cnf.clauses
    assert cnf.clauses.count([-1, -2]) == 3
    assert cnf.clauses.count([-2, -1]) == 2
    assert len(cnf.clauses) == 6
    assert validate_assignment(instance, [[0]]) is True

    result = solve_torus("control_1x1", instance, dimacs_path=tmp_path / "control.cnf")
    assert result.status == "SAT"
    assert result.assignment == [[0]]


def test_jeandel_rao_1x1_unsat(tmp_path) -> None:
    result = solve_torus(
        "jeandel_rao_1x1",
        TorusInstance(JEANDEL_RAO_TILES, 1, 1),
        dimacs_path=tmp_path / "jr_1x1.cnf",
    )

    assert result.status == "UNSAT"
