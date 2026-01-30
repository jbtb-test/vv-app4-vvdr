"""
============================================================
tests.test_io_loader
------------------------------------------------------------
Description :
    Tests unitaires du loader YAML (source of truth).

Objectifs :
    - Support list-of-records et wrapper {decisions: [...]}
    - Erreurs propres sur YAML invalide / schema invalide
    - Détection duplicate decision_id (domaine)

Usage :
    pytest -q
============================================================
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vv_app4_vvdr.io_loader import YamlLoaderError, load_decisions_from_yaml


# ============================================================
# 🔧 Fixtures
# ============================================================
@pytest.fixture
def yaml_list_ok(tmp_path: Path) -> Path:
    p = tmp_path / "list_ok.yaml"
    p.write_text(
        "\n".join(
            [
                "- decision_id: VVDR-001",
                "  date: '2026-01-15'",
                "  title: 'Alpha'",
                "  context: 'ctx'",
                "  decision: 'dec'",
                "  rationale: 'rat'",
                "  status: 'ACCEPTED'",
                "  decision_type: 'GOVERNANCE'",
                "  source: 'MANUAL'",
                "- decision_id: VVDR-002",
                "  date: '2026-01-20'",
                "  title: 'Beta'",
                "  context: 'ctx'",
                "  decision: 'dec'",
                "  rationale: 'rat'",
                "  status: 'ACCEPTED'",
                "  decision_type: 'PROCESS'",
                "  source: 'MANUAL'",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def yaml_wrapper_ok(tmp_path: Path) -> Path:
    p = tmp_path / "wrapper_ok.yaml"
    p.write_text(
        "\n".join(
            [
                "decisions:",
                "  - decision_id: VVDR-001",
                "    date: '2026-01-15'",
                "    title: 'Beta'",
                "    context: 'ctx'",
                "    decision: 'dec'",
                "    rationale: 'rat'",
                "    status: 'ACCEPTED'",
                "    decision_type: 'GOVERNANCE'",
                "    source: 'MANUAL'",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def yaml_duplicate_ids(tmp_path: Path) -> Path:
    p = tmp_path / "dup.yaml"
    p.write_text(
        "\n".join(
            [
                "- decision_id: VVDR-001",
                "  date: '2026-01-15'",
                "  title: 'Alpha2'",
                "  context: 'ctx'",
                "  decision: 'dec'",
                "  rationale: 'rat'",
                "  status: 'ACCEPTED'",
                "  decision_type: 'GOVERNANCE'",
                "  source: 'MANUAL'",
                "- decision_id: VVDR-001",
                "  date: '2026-01-16'",
                "  title: 'Alpha2'",
                "  context: 'ctx'",
                "  decision: 'dec'",
                "  rationale: 'rat'",
                "  status: 'ACCEPTED'",
                "  decision_type: 'GOVERNANCE'",
                "  source: 'MANUAL'",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return p


# ============================================================
# 🧪 Tests
# ============================================================
def test_loader_accepts_list_shape(yaml_list_ok: Path):
    recs = load_decisions_from_yaml(yaml_list_ok)
    assert len(recs) == 2
    assert recs[0].decision_id == "VVDR-001"


def test_loader_accepts_wrapper_shape(yaml_wrapper_ok: Path):
    recs = load_decisions_from_yaml(yaml_wrapper_ok)
    assert len(recs) == 1
    assert recs[0].decision_id == "VVDR-001"


def test_loader_missing_file(tmp_path: Path):
    missing = tmp_path / "nope.yaml"
    with pytest.raises(YamlLoaderError):
        load_decisions_from_yaml(missing)


def test_loader_duplicate_ids_raise(yaml_duplicate_ids: Path):
    with pytest.raises(YamlLoaderError, match="Duplicate decision_id"):
        load_decisions_from_yaml(yaml_duplicate_ids)

