"""Parsers for the G12 Heule 826 vertex and edge data."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Final

import sympy as sp


DATA_DIR: Final[Path] = Path(__file__).with_name("data")
VERTEX_FILE: Final[Path] = DATA_DIR / "heule_826.vtx"
EDGE_FILE: Final[Path] = DATA_DIR / "heule_826.edge"

SQRT_PATTERN: Final[re.Pattern[str]] = re.compile(r"Sqrt\[([^\]]*)\]")

Vertex = tuple[sp.Expr, sp.Expr]
Edge = tuple[int, int]


@dataclass(frozen=True)
class EdgeData:
    """Parsed DIMACS-style edge data and structural sanity facts."""

    vertex_count: int
    declared_edge_count: int
    edges: tuple[Edge, ...]
    touched_vertices: tuple[int, ...]


def _mathematica_to_sympy(expr: str) -> str:
    """Convert the small Mathematica expression subset used by `.vtx`."""

    return SQRT_PATTERN.sub(r"sqrt(\1)", expr)


def parse_vertex_line(line: str) -> Vertex:
    """Parse one `{x, y}` coordinate line into exact SymPy expressions."""

    stripped = line.strip()
    if not stripped.startswith("{") or not stripped.endswith("}"):
        raise ValueError(f"invalid vertex line: {line!r}")
    body = stripped[1:-1]
    parts = body.split(",", 1)
    if len(parts) != 2:
        raise ValueError(f"invalid vertex coordinate pair: {line!r}")
    x_text, y_text = (_mathematica_to_sympy(part.strip()) for part in parts)
    return (sp.sympify(x_text), sp.sympify(y_text))


def parse_vertices(path: Path = VERTEX_FILE) -> tuple[Vertex, ...]:
    """Parse all vertex coordinates."""

    return tuple(
        parse_vertex_line(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )


def parse_edges(path: Path = EDGE_FILE) -> EdgeData:
    """Parse and validate the DIMACS-style edge file."""

    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        raise ValueError("empty edge file")
    header = lines[0].split()
    if len(header) != 4 or header[:2] != ["p", "edge"]:
        raise ValueError(f"invalid edge header: {lines[0]!r}")
    vertex_count = int(header[2])
    declared_edge_count = int(header[3])

    seen: set[Edge] = set()
    touched: set[int] = set()
    parsed: list[Edge] = []
    for line in lines[1:]:
        parts = line.split()
        if len(parts) != 3 or parts[0] != "e":
            raise ValueError(f"invalid edge line: {line!r}")
        i = int(parts[1])
        j = int(parts[2])
        if i == j:
            raise ValueError(f"self-loop: {line!r}")
        if not (1 <= i <= vertex_count and 1 <= j <= vertex_count):
            raise ValueError(f"edge endpoint out of range: {line!r}")
        edge = (i, j) if i < j else (j, i)
        if edge in seen:
            raise ValueError(f"duplicate undirected edge: {line!r}")
        seen.add(edge)
        touched.update(edge)
        parsed.append(edge)

    if len(parsed) != declared_edge_count:
        raise ValueError(
            f"declared {declared_edge_count} edges, parsed {len(parsed)}"
        )
    return EdgeData(
        vertex_count=vertex_count,
        declared_edge_count=declared_edge_count,
        edges=tuple(parsed),
        touched_vertices=tuple(sorted(touched)),
    )


def load_heule_826() -> tuple[tuple[Vertex, ...], EdgeData]:
    """Load the vendored Heule 826 graph data."""

    vertices = parse_vertices()
    edges = parse_edges()
    if len(vertices) != edges.vertex_count:
        raise ValueError(
            f"vertex file has {len(vertices)} rows, edge header declares {edges.vertex_count}"
        )
    return vertices, edges
