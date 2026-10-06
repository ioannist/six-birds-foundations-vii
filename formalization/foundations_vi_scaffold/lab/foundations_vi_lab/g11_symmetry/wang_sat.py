"""SAT encoding for small periodic Wang-tile checks used by G11-L1."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pysat.formula import CNF
from pysat.solvers import Glucose3


Tile = tuple[int, int, int, int]
Assignment = list[list[int]]


CONTROL_TILES: tuple[Tile, ...] = (
    (0, 0, 0, 0),
    (1, 1, 1, 1),
)


JEANDEL_RAO_TILES: tuple[Tile, ...] = (
    (3, 3, 3, 1),
    (1, 1, 0, 2),
    (0, 0, 1, 0),
    (2, 2, 1, 0),
    (2, 2, 0, 2),
    (3, 1, 1, 1),
    (3, 1, 2, 2),
    (1, 3, 2, 3),
    (3, 0, 1, 1),
    (0, 3, 2, 1),
    (1, 0, 2, 2),
)


@dataclass(frozen=True)
class TorusInstance:
    """A concrete periodic Wang-tile SAT instance."""

    tiles: tuple[Tile, ...]
    rows: int
    cols: int


@dataclass(frozen=True)
class SolveResult:
    """SAT/UNSAT result for one torus instance."""

    name: str
    rows: int
    cols: int
    variables: int
    clauses: int
    status: str
    assignment: Assignment | None
    dimacs_path: str


def variable_id(rows: int, cols: int, tile_count: int, row: int, col: int, tile: int) -> int:
    """Return the DIMACS variable id for `(row,col,tile)`."""

    if not (0 <= row < rows and 0 <= col < cols and 0 <= tile < tile_count):
        raise ValueError("cell or tile index out of range")
    return 1 + ((row * cols + col) * tile_count + tile)


def _forbid_pair(cnf: CNF, first: int, second: int) -> None:
    cnf.append([-first, -second])


def encode_torus(instance: TorusInstance) -> CNF:
    """Build the CNF for a periodic `rows x cols` Wang-tile torus."""

    if instance.rows <= 0 or instance.cols <= 0:
        raise ValueError("torus dimensions must be positive")
    if not instance.tiles:
        raise ValueError("tile set must be nonempty")

    cnf = CNF()
    tile_count = len(instance.tiles)
    for row in range(instance.rows):
        for col in range(instance.cols):
            cell_vars = [
                variable_id(instance.rows, instance.cols, tile_count, row, col, tile)
                for tile in range(tile_count)
            ]
            cnf.append(cell_vars)
            for i in range(tile_count):
                for j in range(i + 1, tile_count):
                    _forbid_pair(cnf, cell_vars[i], cell_vars[j])

    for row in range(instance.rows):
        for col in range(instance.cols):
            east_col = (col + 1) % instance.cols
            north_row = (row + 1) % instance.rows
            for left_index, left_tile in enumerate(instance.tiles):
                for right_index, right_tile in enumerate(instance.tiles):
                    if left_tile[1] != right_tile[0]:
                        _forbid_pair(
                            cnf,
                            variable_id(instance.rows, instance.cols, tile_count, row, col, left_index),
                            variable_id(
                                instance.rows,
                                instance.cols,
                                tile_count,
                                row,
                                east_col,
                                right_index,
                            ),
                        )
                    if left_tile[3] != right_tile[2]:
                        _forbid_pair(
                            cnf,
                            variable_id(instance.rows, instance.cols, tile_count, row, col, left_index),
                            variable_id(
                                instance.rows,
                                instance.cols,
                                tile_count,
                                north_row,
                                col,
                                right_index,
                            ),
                        )
    return cnf


def decode_assignment(instance: TorusInstance, model: list[int]) -> Assignment:
    """Decode a SAT model into a grid of tile indices."""

    true_vars = {literal for literal in model if literal > 0}
    tile_count = len(instance.tiles)
    assignment: Assignment = []
    for row in range(instance.rows):
        decoded_row = []
        for col in range(instance.cols):
            chosen = [
                tile
                for tile in range(tile_count)
                if variable_id(instance.rows, instance.cols, tile_count, row, col, tile) in true_vars
            ]
            if len(chosen) != 1:
                raise ValueError(f"model does not choose exactly one tile at {(row, col)}")
            decoded_row.append(chosen[0])
        assignment.append(decoded_row)
    return assignment


def validate_assignment(instance: TorusInstance, assignment: Assignment) -> bool:
    """Check a decoded torus assignment directly against Wang matching rules."""

    if len(assignment) != instance.rows:
        return False
    for row in assignment:
        if len(row) != instance.cols:
            return False
        if any(tile < 0 or tile >= len(instance.tiles) for tile in row):
            return False
    for row in range(instance.rows):
        for col in range(instance.cols):
            tile = instance.tiles[assignment[row][col]]
            east_tile = instance.tiles[assignment[row][(col + 1) % instance.cols]]
            north_tile = instance.tiles[assignment[(row + 1) % instance.rows][col]]
            if tile[1] != east_tile[0]:
                return False
            if tile[3] != north_tile[2]:
                return False
    return True


def solve_torus(
    name: str,
    instance: TorusInstance,
    *,
    dimacs_path: Path,
) -> SolveResult:
    """Encode, save, and solve one periodic Wang-tile torus instance."""

    cnf = encode_torus(instance)
    dimacs_path.parent.mkdir(parents=True, exist_ok=True)
    cnf.to_file(str(dimacs_path))
    with Glucose3(bootstrap_with=cnf.clauses) as solver:
        sat = solver.solve()
        model = solver.get_model() if sat else None
    assignment = decode_assignment(instance, model) if model is not None else None
    if assignment is not None and not validate_assignment(instance, assignment):
        raise AssertionError(f"solver assignment failed direct validation for {name}")
    return SolveResult(
        name=name,
        rows=instance.rows,
        cols=instance.cols,
        variables=instance.rows * instance.cols * len(instance.tiles),
        clauses=len(cnf.clauses),
        status="SAT" if sat else "UNSAT",
        assignment=assignment,
        dimacs_path=str(dimacs_path),
    )
