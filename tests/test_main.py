"""
============================================================
tests.test_main
------------------------------------------------------------
Description :
    Smoke test E2E (CLI) pour APP4 VVDR.

Objectifs :
    - Exécuter vv_app4_vvdr.main.run() en mode tmp_path
    - Vérifier génération des 3 fichiers (md/csv/json)
    - Vérifier contenu minimal (schema JSON, header MD, CSV header)

Usage :
    pytest -q
============================================================
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vv_app4_vvdr.main import run


# ============================================================
# 🔧 Fixtures
# ============================================================
@pytest.fixture
def sample_yaml(tmp_path: Path) -> Path:
    p = tmp_path / "demo_decisions.yaml"
    p.write_text(
        "\n".join(
            [
                "- decision_id: VVDR-001",
                "  date: '2026-01-15'",
                "  title: 'Decision A'",
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


@pytest.fixture
def out_dir(tmp_path: Path) -> Path:
    return tmp_path / "out"


# ============================================================
# 🧪 Tests
# ============================================================
def test_cli_smoke_generates_3_files(sample_yaml: Path, out_dir: Path):
    rc = run(["--input", str(sample_yaml), "--out-dir", str(out_dir)])
    assert rc == 0

    md_path = out_dir / "decision_register.md"
    csv_path = out_dir / "decision_register.csv"
    json_path = out_dir / "decision_register.json"

    assert md_path.exists()
    assert csv_path.exists()
    assert json_path.exists()

    md = md_path.read_text(encoding="utf-8")
    assert md.startswith("# Decision Register")

    csv_txt = csv_path.read_text(encoding="utf-8")
    assert "decision_id,date,title,status" in csv_txt.splitlines()[0]

    json_txt = json_path.read_text(encoding="utf-8")
    assert '"schema"' in json_txt
    assert "vvdr.decision_register.v1" in json_txt
