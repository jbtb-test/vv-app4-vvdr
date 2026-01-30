# APP4 — Setup & Dependencies

## Principes

- pyproject.toml = source de vérité
- runtime minimal
- aucune IA
- aucun secret requis
- layout src/

---

## Installation locale

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -U pip
pip install -e ".[dev]"
pytest -q
```

---

## Exécution

```powershell
python -m vv_app4_vvdr.main --verbose
```

---

## Dépendances

- Python ≥ 3.11
- PyYAML
- pytest (dev)
- Aucune dépendance réseau ou clé externe.