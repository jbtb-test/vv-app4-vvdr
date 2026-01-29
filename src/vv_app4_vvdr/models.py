#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
vv_app4_vvdr.models
------------------------------------------------------------
Description :
    Modèles de domaine — APP4 VVDR (V&V Decision Record).

Rôle :
    - Définir une structure stable et auditable pour les décisions V&V humaines
    - Valider les champs critiques (IDs, dates, enums, textes)
    - Garantir un tri déterministe (exports stables)

Notes :
    - Pas de dépendance externe
    - Pas de logique IO ici (YAML/CSV/MD/JSON -> autres modules)
============================================================
"""

from __future__ import annotations

# ============================================================
# 📦 Imports
# ============================================================
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple


# ============================================================
# ⚠️ Exceptions
# ============================================================
class ModelError(ValueError):
    """Erreur de validation des modèles VVDR."""


# ============================================================
# 🧾 Enums (stables)
# ============================================================
class DecisionStatus(str, Enum):
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class DecisionType(str, Enum):
    PROCESS = "PROCESS"
    TECHNICAL = "TECHNICAL"
    QUALITY = "QUALITY"
    RISK = "RISK"
    GOVERNANCE = "GOVERNANCE"


class DecisionSource(str, Enum):
    MANUAL = "MANUAL"
    APP1_QRA = "APP1_QRA"
    APP2_TCTC = "APP2_TCTC"
    APP3_AITA = "APP3_AITA"


# ============================================================
# 🔎 Helpers validation
# ============================================================
def _require_str(name: str, value: Any, *, min_len: int = 1) -> str:
    if not isinstance(value, str):
        raise ModelError(f"Invalid '{name}': expected str.")
    v = value.strip()
    if len(v) < min_len:
        raise ModelError(f"Invalid '{name}': empty/too short.")
    return v


def _optional_str(name: str, value: Any) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ModelError(f"Invalid '{name}': expected str or null.")
    v = value.strip()
    return v or None


def _as_str_list(name: str, value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        # tolérance : un seul string -> liste 1 élément
        v = value.strip()
        return [v] if v else []
    if not isinstance(value, list):
        raise ModelError(f"Invalid '{name}': expected list[str].")
    out: List[str] = []
    for i, item in enumerate(value):
        if not isinstance(item, str):
            raise ModelError(f"Invalid '{name}[{i}]': expected str.")
        s = item.strip()
        if s:
            out.append(s)
    return out


def parse_date_yyyy_mm_dd(value: Any, *, field_name: str = "date") -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if not isinstance(value, str):
        raise ModelError(f"Invalid '{field_name}': expected YYYY-MM-DD string.")
    v = value.strip()
    try:
        return datetime.strptime(v, "%Y-%m-%d").date()
    except ValueError as e:
        raise ModelError(f"Invalid '{field_name}': expected YYYY-MM-DD, got '{v}'.") from e


def _parse_enum(enum_cls: Any, name: str, value: Any) -> Any:
    if isinstance(value, enum_cls):
        return value
    if not isinstance(value, str):
        raise ModelError(f"Invalid '{name}': expected {enum_cls.__name__} as string.")
    v = value.strip().upper()
    try:
        return enum_cls(v)
    except Exception as e:
        allowed = ", ".join([m.value for m in enum_cls])  # type: ignore[arg-type]
        raise ModelError(f"Invalid '{name}': '{v}' not in [{allowed}].") from e


# ============================================================
# 🧩 Domain model
# ============================================================
@dataclass(frozen=True, slots=True)
class DecisionRecord:
    """
    Décision V&V humaine (audit-ready).

    Tri déterministe recommandé :
        (date, decision_id)
    """
    decision_id: str
    date: date
    title: str
    context: str
    decision: str
    rationale: str

    status: DecisionStatus = DecisionStatus.ACCEPTED
    decision_type: DecisionType = DecisionType.PROCESS
    source: DecisionSource = DecisionSource.MANUAL

    references: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    risk_refs: List[str] = field(default_factory=list)

    supersedes: Optional[str] = None
    owner: Optional[str] = None

    def sort_key(self) -> Tuple[date, str]:
        return (self.date, self.decision_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "date": self.date.strftime("%Y-%m-%d"),
            "title": self.title,
            "context": self.context,
            "decision": self.decision,
            "rationale": self.rationale,
            "status": self.status.value,
            "decision_type": self.decision_type.value,
            "source": self.source.value,
            "references": list(self.references),
            "tags": list(self.tags),
            "risk_refs": list(self.risk_refs),
            "supersedes": self.supersedes,
            "owner": self.owner,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DecisionRecord":
        if not isinstance(data, dict):
            raise ModelError("Invalid record: expected dict.")

        decision_id = _require_str("decision_id", data.get("decision_id"))
        d = parse_date_yyyy_mm_dd(data.get("date"), field_name="date")
        title = _require_str("title", data.get("title"), min_len=3)

        context = _require_str("context", data.get("context"), min_len=3)
        decision = _require_str("decision", data.get("decision"), min_len=3)
        rationale = _require_str("rationale", data.get("rationale"), min_len=3)

        status = _parse_enum(DecisionStatus, "status", data.get("status", DecisionStatus.ACCEPTED.value))
        decision_type = _parse_enum(DecisionType, "decision_type", data.get("decision_type", DecisionType.PROCESS.value))
        source = _parse_enum(DecisionSource, "source", data.get("source", DecisionSource.MANUAL.value))

        references = _as_str_list("references", data.get("references"))
        tags = _as_str_list("tags", data.get("tags"))
        risk_refs = _as_str_list("risk_refs", data.get("risk_refs"))

        supersedes = _optional_str("supersedes", data.get("supersedes"))
        owner = _optional_str("owner", data.get("owner"))

        return DecisionRecord(
            decision_id=decision_id,
            date=d,
            title=title,
            context=context,
            decision=decision,
            rationale=rationale,
            status=status,
            decision_type=decision_type,
            source=source,
            references=references,
            tags=tags,
            risk_refs=risk_refs,
            supersedes=supersedes,
            owner=owner,
        )


# ============================================================
# ✅ Batch validation helpers
# ============================================================
def ensure_unique_ids(records: Iterable[DecisionRecord]) -> None:
    seen: set[str] = set()
    for r in records:
        if r.decision_id in seen:
            raise ModelError(f"Duplicate decision_id: '{r.decision_id}'.")
        seen.add(r.decision_id)


def sort_records(records: List[DecisionRecord]) -> List[DecisionRecord]:
    return sorted(records, key=lambda r: r.sort_key())
