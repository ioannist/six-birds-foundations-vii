"""Fast tests for the G12 Heule finite-witness lab."""

from foundations_vi_lab.g12_finite_witness.coloring_sat import (
    build_coloring_cnf,
    color_var,
)
from foundations_vi_lab.g12_finite_witness.parsing import (
    load_heule_826,
    parse_vertex_line,
)
from foundations_vi_lab.g12_finite_witness.unit_distance import (
    squared_distance,
    verify_edge_unit_distances,
)


def test_vertex_parser_handles_sqrt_fraction() -> None:
    """The Mathematica-style parser handles fractional radicands."""

    x, y = parse_vertex_line("{1/2, Sqrt[11/3]/2}")
    assert str(x) == "1/2"
    assert "sqrt(33)" in str(y)


def test_heule_data_structural_sanity() -> None:
    """The vendored graph has the declared size and clean undirected edges."""

    vertices, edge_data = load_heule_826()
    assert len(vertices) == 826
    assert edge_data.vertex_count == 826
    assert edge_data.declared_edge_count == 4273
    assert len(edge_data.edges) == 4273
    assert edge_data.touched_vertices == tuple(range(1, 827))
    assert all(i != j for i, j in edge_data.edges)
    assert len(set(edge_data.edges)) == len(edge_data.edges)


def test_declared_edges_are_exact_unit_distance() -> None:
    """Every declared edge has exact squared distance one."""

    vertices, edge_data = load_heule_826()
    symbolic_failures, numeric_failures = verify_edge_unit_distances(
        vertices, edge_data.edges
    )
    assert symbolic_failures == ()
    assert numeric_failures == ()
    assert squared_distance(vertices, edge_data.edges[0]) == 1


def test_four_coloring_cnf_dimensions() -> None:
    """The standard 4-coloring encoding has the expected size."""

    _, edge_data = load_heule_826()
    cnf = build_coloring_cnf(edge_data.vertex_count, edge_data.edges)
    assert cnf.variables == 3304
    assert len(cnf.clauses) == 22874
    assert color_var(1, 0) == 1
    assert color_var(826, 3) == 3304
