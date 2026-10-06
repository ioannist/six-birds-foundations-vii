from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from sixbirds_foundations_v._holonomy_support.schemas.common import (
    ensure_finite_nonnegative_number,
    ensure_nonempty_string,
    ensure_repo_relative_path,
    ensure_unique_strings,
)


class SixBirdsRecombinationModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def ensure_optional_nonempty_string(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    return ensure_nonempty_string(value, field_name)


def ensure_optional_repo_relative_path(
    value: str | None,
    field_name: str,
) -> str | None:
    if value is None:
        return None
    return ensure_repo_relative_path(value, field_name)


__all__ = [
    "SixBirdsRecombinationModel",
    "ensure_finite_nonnegative_number",
    "ensure_nonempty_string",
    "ensure_optional_nonempty_string",
    "ensure_optional_repo_relative_path",
    "ensure_repo_relative_path",
    "ensure_unique_strings",
]
