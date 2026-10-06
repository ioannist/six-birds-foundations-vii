"""SAT encoding for 4-colorability of the G12 finite witness graph."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from foundations_vi_lab.g12_finite_witness.parsing import Edge


@dataclass(frozen=True)
class CNFInstance:
    """In-memory CNF instance."""

    variables: int
    clauses: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class SolveSummary:
    """Summary of one SAT solver invocation."""

    solver_name: str
    status: str
    elapsed_seconds: float
    variables: int
    clauses: int


def color_var(vertex: int, color: int, colors: int = 4) -> int:
    """Map a 1-indexed vertex and 0-indexed color to a DIMACS variable."""

    if vertex <= 0:
        raise ValueError("vertices are 1-indexed")
    if not (0 <= color < colors):
        raise ValueError(f"color out of range: {color}")
    return (vertex - 1) * colors + color + 1


def build_coloring_cnf(vertex_count: int, edges: tuple[Edge, ...], colors: int = 4) -> CNFInstance:
    """Build the standard graph `colors`-colorability CNF."""

    clauses: list[tuple[int, ...]] = []
    for vertex in range(1, vertex_count + 1):
        clauses.append(tuple(color_var(vertex, color, colors) for color in range(colors)))
        for c1 in range(colors):
            for c2 in range(c1 + 1, colors):
                clauses.append(
                    (-color_var(vertex, c1, colors), -color_var(vertex, c2, colors))
                )
    for i, j in edges:
        for color in range(colors):
            clauses.append((-color_var(i, color, colors), -color_var(j, color, colors)))
    return CNFInstance(variables=vertex_count * colors, clauses=tuple(clauses))


def write_dimacs(path: Path, cnf: CNFInstance) -> None:
    """Write a CNF instance in DIMACS format."""

    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"p cnf {cnf.variables} {len(cnf.clauses)}"]
    lines.extend(" ".join(str(lit) for lit in clause) + " 0" for clause in cnf.clauses)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def solve_cnf(cnf: CNFInstance, solver_name: str = "g3") -> SolveSummary:
    """Solve a CNF instance with PySAT."""

    from pysat.solvers import Solver

    start = time.perf_counter()
    with Solver(name=solver_name, bootstrap_with=[list(clause) for clause in cnf.clauses]) as solver:
        result = solver.solve()
    elapsed = time.perf_counter() - start
    status = "SAT" if result is True else "UNSAT" if result is False else "UNKNOWN"
    return SolveSummary(
        solver_name=solver_name,
        status=status,
        elapsed_seconds=elapsed,
        variables=cnf.variables,
        clauses=len(cnf.clauses),
    )
