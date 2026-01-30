"""
============================================================
tests.test_export
------------------------------------------------------------
Description :
    Tests unitaires des exports (MD/CSV/JSON).

Objectifs :
    - Générer les 3 fichiers sur un out_dir tmp
    - Vérifier présence + contenu minimal
    - Vérifier fallback safe quand records=[]

Usage :
    pytest -q
============================================================
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vv_app4_vvdr.export import export_decision_register
from vv_app4_vvdr.models import DecisionRecord


# ============================================================
# 🔧 Fixtures
# ============================================================
@pytest.fixture
def one_record() -> DecisionRecord:
    return DecisionRecord.from_dict(
        {
            "decision_id": "VVDR-001",
            "date": "2026-01-15",
            "title": "Decision A",
            "context": "ctx",
            "decision": "dec",
            "rationale": "rat",
            "status": "ACCEPTED",
            "decision_type": "GOVERNANCE",
            "source": "MANUAL",
        }
    )


# ============================================================
# 🧪 Tests
# ============================================================
def test_export_generates_files(one_record: DecisionRecord, tmp_path: Path):
    out = export_decision_register([one_record], out_dir=tmp_path)

    md_path = out["md"]
    csv_path = out["csv"]
    json_path = out["json"]

    assert md_path.exists()
    assert csv_path.exists()
    assert json_path.exists()

    assert "Decision Register" in md_path.read_text(encoding="utf-8")
    assert "decision_id,date,title,status" in csv_path.read_text(encoding="utf-8").splitlines()[0]

    js = json_path.read_text(encoding="utf-8")
    assert "vvdr.decision_register.v1" in js
    assert '"count"' in js


def test_export_empty_fallback(tmp_path: Path):
    out = export_decision_register([], out_dir=tmp_path)

    assert out["md"].exists()
    assert out["csv"].exists()
    assert out["json"].exists()

    md = out["md"].read_text(encoding="utf-8")
    assert "Total decisions" in md  # should be 0 but we keep it minimal

    csv_lines = out["csv"].read_text(encoding="utf-8").splitlines()
    assert len(csv_lines) == 1  # header only

    js = out["json"].read_text(encoding="utf-8")
    assert "vvdr.decision_register.v1" in js
