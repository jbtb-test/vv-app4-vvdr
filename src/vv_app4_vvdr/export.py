#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
vv_app4_vvdr.export
------------------------------------------------------------
Description:
    Deterministic exports for APP4 VVDR.

    Export a list of DecisionRecord into 3 stable artifacts:
      - decision_register.md
      - decision_register.csv
      - decision_register.json

Goals:
    - Deterministic ordering (stable exports for audit/demo)
    - Fallback-safe: even if input list is empty, generate files
    - Clear errors on I/O failure

Usage:
    from pathlib import Path
    from vv_app4_vvdr.export import export_decision_register

    export_decision_register(records, out_dir=Path("data/outputs"))

Notes:
    Sorting is enforced using the domain sort_key() (or model helper
    sort_records()) to guarantee stable ordering.
============================================================
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence

from vv_app4_vvdr.models import DecisionRecord, sort_records


# ============================================================
# Errors
# ============================================================
@dataclass(frozen=True)
class ExportError(RuntimeError):
    """Raised when exporting fails with a user-friendly message."""

    message: str
    path: Path | None = None

    def __str__(self) -> str:  # pragma: no cover
        if self.path:
            return f"{self.message} (path: {self.path.as_posix()})"
        return self.message


# ============================================================
# Public API
# ============================================================
def export_decision_register(
    records: Sequence[DecisionRecord] | Iterable[DecisionRecord],
    out_dir: Path,
) -> dict[str, Path]:
    """
    Export decision register in MD/CSV/JSON.

    Args:
        records: DecisionRecord collection.
        out_dir: Output directory.

    Returns:
        Dict of artifact name -> file path.

    Raises:
        ExportError: on I/O failure or invalid out_dir.
    """
    out_dir = Path(out_dir)

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise ExportError(f"Unable to create output directory: {exc}", path=out_dir) from exc

    # Enforce deterministic ordering
    records_list = list(records)
    records_sorted: List[DecisionRecord] = sort_records(records_list) if records_list else []

    md_path = out_dir / "decision_register.md"
    csv_path = out_dir / "decision_register.csv"
    json_path = out_dir / "decision_register.json"

    _write_md(records_sorted, md_path)
    _write_csv(records_sorted, csv_path)
    _write_json(records_sorted, json_path)

    return {
        "md": md_path,
        "csv": csv_path,
        "json": json_path,
    }


# ============================================================
# Internals: writers
# ============================================================
def _write_md(records: List[DecisionRecord], path: Path) -> None:
    """
    Markdown export optimized for recruiter readability.
    """
    lines: list[str] = []
    lines.append("# Decision Register (APP4 — VVDR)")
    lines.append("")
    lines.append(f"- Total decisions: **{len(records)}**")
    lines.append("")
    lines.append("## Index")
    lines.append("")
    if not records:
        lines.append("_No decisions found._")
        lines.append("")
    else:
        for r in records:
            lines.append(f"- **{r.decision_id}** — {r.title} ({r.status.value})")
        lines.append("")

    lines.append("## Details")
    lines.append("")
    if not records:
        lines.append("_No decision records to display._")
        lines.append("")
    else:
        for r in records:
            lines.extend(_md_block_for_record(r))
            lines.append("")

    _safe_write_text(path, "\n".join(lines).rstrip() + "\n")


def _md_block_for_record(r: DecisionRecord) -> list[str]:
    def _fmt_list(items: list[str]) -> str:
        return ", ".join(items) if items else "-"

    return [
        f"### {r.decision_id} — {r.title}",
        "",
        f"- **Date**: {r.date.isoformat()}",
        f"- **Status**: {r.status.value}",
        f"- **Type**: {r.decision_type.value}",
        f"- **Source**: {r.source.value}",
        f"- **Owner**: {r.owner or '-'}",
        f"- **Supersedes**: {r.supersedes or '-'}",
        f"- **Risk refs**: {_fmt_list(r.risk_refs)}",
        f"- **Tags**: {_fmt_list(r.tags)}",
        f"- **References**: {_fmt_list(r.references)}",
        "",
        "**Context**",
        "",
        _escape_md_multiline(r.context),
        "",
        "**Decision**",
        "",
        _escape_md_multiline(r.decision),
        "",
        "**Rationale**",
        "",
        _escape_md_multiline(r.rationale),
    ]


def _escape_md_multiline(text: str) -> str:
    # Keep it simple: we just preserve newlines and avoid accidental list formatting issues.
    # If you later want fenced blocks, we can switch to ```text blocks.
    return text.strip() if text.strip() else "-"


def _write_csv(records: List[DecisionRecord], path: Path) -> None:
    """
    CSV export for audit / spreadsheet usage.
    """
    fieldnames = [
        "decision_id",
        "date",
        "title",
        "status",
        "decision_type",
        "source",
        "owner",
        "supersedes",
        "risk_refs",
        "tags",
        "references",
        "context",
        "decision",
        "rationale",
    ]

    try:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for r in records:
                writer.writerow(
                    {
                        "decision_id": r.decision_id,
                        "date": r.date.isoformat(),
                        "title": r.title,
                        "status": r.status.value,
                        "decision_type": r.decision_type.value,
                        "source": r.source.value,
                        "owner": r.owner or "",
                        "supersedes": r.supersedes or "",
                        "risk_refs": ";".join(r.risk_refs),
                        "tags": ";".join(r.tags),
                        "references": ";".join(r.references),
                        "context": r.context,
                        "decision": r.decision,
                        "rationale": r.rationale,
                    }
                )
    except OSError as exc:
        raise ExportError(f"Unable to write CSV: {exc}", path=path) from exc


def _write_json(records: List[DecisionRecord], path: Path) -> None:
    """
    JSON export stable + human-readable (2-space indent).
    """
    payload = {
        "schema": "vvdr.decision_register.v1",
        "count": len(records),
        "decisions": [r.to_dict() for r in records],
    }

    try:
        text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
        _safe_write_text(path, text.rstrip() + "\n")
    except OSError as exc:
        raise ExportError(f"Unable to write JSON: {exc}", path=path) from exc


def _safe_write_text(path: Path, content: str) -> None:
    try:
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        raise ExportError(f"Unable to write file: {exc}", path=path) from exc
