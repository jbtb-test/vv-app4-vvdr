#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
vv_app4_vvdr.io_loader
------------------------------------------------------------
Description:
    YAML loader (source of truth) for APP4 VVDR.

    Reads a YAML file containing decision record(s), normalizes
    the structure, converts items into DecisionRecord objects,
    validates them (domain rules), and returns a deterministically
    sorted list.

Goals:
    - Robust YAML parsing with clear, actionable error messages
    - Deterministic ordering (stable outputs for V&V / demos)
    - No side-effects (pure loader)

Supported YAML shapes:
    1) List of records:
        - {id: ..., title: ..., date: ..., status: ..., ...}
        - {id: ..., ...}

    2) Dict wrapper:
        decisions:
          - {id: ..., ...}
          - {id: ..., ...}

Usage (example):
    from pathlib import Path
    from vv_app4_vvdr.io_loader import load_decisions_from_yaml

    records = load_decisions_from_yaml(Path("data/inputs/demo_decisions.yaml"))

CLI integration:
    This module is called by vv_app4_vvdr.main (4.1.5).
============================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Mapping, Sequence

import yaml

from vv_app4_vvdr.models import (
    DecisionRecord,
    ModelError,
    ensure_unique_ids,
    sort_records,
)


# ============================================================
# Errors (clean messages)
# ============================================================
@dataclass
class YamlLoaderError(RuntimeError):
    """Raised when the YAML loader fails with a user-friendly message."""

    message: str
    path: Path | None = None

    def __str__(self) -> str:  # pragma: no cover
        if self.path:
            return f"{self.message} (file: {self.path.as_posix()})"
        return self.message


# ============================================================
# Public API
# ============================================================
def load_decisions_from_yaml(path: Path) -> list[DecisionRecord]:
    """
    Load decision records from a YAML file.

    Args:
        path: Path to YAML file.

    Returns:
        A deterministically sorted list of DecisionRecord.

    Raises:
        YamlLoaderError: on I/O, YAML syntax, schema issues, or validation errors.
    """
    path = Path(path)

    if not path.exists():
        raise YamlLoaderError("YAML file not found", path=path)
    if not path.is_file():
        raise YamlLoaderError("YAML path is not a file", path=path)

    raw = _read_yaml(path)
    items = _extract_items(raw, path)

    records: list[DecisionRecord] = []
    for idx, item in enumerate(items):
        try:
            record_dict = _ensure_mapping(item, path=path, idx=idx)
            record = DecisionRecord.from_dict(record_dict)  # <-- if your models differ, adapt here
            # If your model requires explicit validation:
            if hasattr(record, "validate") and callable(getattr(record, "validate")):
                record.validate()
            records.append(record)
        except YamlLoaderError:
            raise
        except Exception as exc:
            raise YamlLoaderError(
                message=f"Invalid decision record at index {idx}: {exc}",
                path=path,
            ) from exc

    try:
        ensure_unique_ids(records)
        return sort_records(records)
    except ModelError as exc:
        # Encapsulation cohérente avec le contrat du loader
        raise YamlLoaderError(message=str(exc), path=path) from exc



# ============================================================
# Internals
# ============================================================
def _read_yaml(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise YamlLoaderError(f"Unable to read YAML file: {exc}", path=path) from exc

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise YamlLoaderError(f"YAML syntax error: {exc}", path=path) from exc

    if data is None:
        # empty YAML file -> treat as empty list (stable behavior)
        return []
    return data


def _extract_items(raw: Any, path: Path) -> Sequence[Any]:
    """
    Normalize YAML shapes to a list of item mappings.
    """
    if isinstance(raw, list):
        return raw

    if isinstance(raw, dict):
        # allow wrapper key
        if "decisions" in raw:
            decisions = raw["decisions"]
            if decisions is None:
                return []
            if not isinstance(decisions, list):
                raise YamlLoaderError(
                    "Invalid YAML: 'decisions' must be a list",
                    path=path,
                )
            return decisions

        # If a dict is provided directly as a single record
        # (rare but convenient), accept it.
        return [raw]

    raise YamlLoaderError(
        "Invalid YAML: expected a list of records or a dict wrapper with key 'decisions'",
        path=path,
    )


def _ensure_mapping(item: Any, path: Path, idx: int) -> Mapping[str, Any]:
    if not isinstance(item, dict):
        raise YamlLoaderError(
            message=f"Invalid record at index {idx}: expected a mapping/dict",
            path=path,
        )

    # Normalize keys to strings (YAML can sometimes parse non-str keys)
    normalized: dict[str, Any] = {}
    for k, v in item.items():
        normalized[str(k)] = v
    return normalized


def _sorted_deterministic(records: Iterable[DecisionRecord]) -> List[DecisionRecord]:
    """
    Deterministic sort using the domain sort_key() if available,
    else fallback to stable string repr.
    """
    records_list = list(records)
    if not records_list:
        return []

    first = records_list[0]
    if hasattr(first, "sort_key") and callable(getattr(first, "sort_key")):
        return sorted(records_list, key=lambda r: r.sort_key())

    # Fallback (should not happen if models.py follows your plan)
    return sorted(records_list, key=lambda r: str(r))
