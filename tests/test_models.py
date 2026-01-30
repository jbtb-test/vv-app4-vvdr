"""
============================================================
tests.test_models
------------------------------------------------------------
Description :
    Tests unitaires des modèles domaine (DecisionRecord, enums).

Objectifs :
    - Vérifier parsing nominal via from_dict()
    - Vérifier erreurs sur champs obligatoires / enums invalides
    - Vérifier parsing date (format attendu)

Usage :
    pytest -q
============================================================
"""

from __future__ import annotations

import pytest

from vv_app4_vvdr.models import DecisionRecord


# ============================================================
# 🔧 Fixtures
# ============================================================
@pytest.fixture
def record_dict_nominal():
    return {
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


# ============================================================
# 🧪 Tests
# ============================================================
def test_decision_record_from_dict_nominal(record_dict_nominal):
    r = DecisionRecord.from_dict(record_dict_nominal)
    assert r.decision_id == "VVDR-001"
    assert r.date.isoformat() == "2026-01-15"
    assert r.status.value == "ACCEPTED"
    assert r.decision_type.value == "GOVERNANCE"
    assert r.source.value == "MANUAL"


def test_decision_record_missing_required_fields(record_dict_nominal):
    bad = dict(record_dict_nominal)
    bad.pop("decision_id")
    with pytest.raises(ValueError):
        DecisionRecord.from_dict(bad)


def test_decision_record_invalid_enum_value(record_dict_nominal):
    bad = dict(record_dict_nominal)
    bad["status"] = "NOPE"
    with pytest.raises(ValueError):
        DecisionRecord.from_dict(bad)


def test_decision_record_invalid_date_format(record_dict_nominal):
    bad = dict(record_dict_nominal)
    bad["date"] = "15/01/2026"
    with pytest.raises(ValueError):
        DecisionRecord.from_dict(bad)
