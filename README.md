# APP4 — VVDR (V&V Decision Register)

## Démo en 1 phrase
Registre décisionnel **auditable et versionné** (type “decision log” V&V) qui centralise des **décisions humaines** liées aux risques,
les valide (schéma + règles), et génère des exports **déterministes** (**MD / CSV / JSON**) à partir d’une **source YAML**.

**But :** rendre traçables et démontrables les décisions structurantes du portfolio (APP1/APP2/APP3) **sans couplage technique** :
- **source-of-truth** = YAML versionné
- **validation** déterministe des enregistrements
- **exports** stables (ordre, formats) pour audit / revue / recrutement
- **zéro automatisation décisionnelle** (APP4 ne “pilote” pas les autres apps)

---

## Problème métier
Dans beaucoup de projets, les décisions V&V (gouvernance, risques, règles de démonstration, stratégie de tests, hygiène repo) sont :
- dispersées (emails, réunions, tickets, notes)
- non versionnées ou difficiles à retrouver
- non auditables (pas de “WHY” clair, pas d’historique)
- peu démontrables en entretien (pas de trace simple et lisible)

---

## Valeur apportée
- **Audit-ready** : décisions structurées, datées, typées, liées aux risques (R1..R6)
- **Traçabilité du WHY** : “qui a décidé quoi, quand, pourquoi”
- **Déterminisme** : mêmes entrées → mêmes exports (ordre stable)
- **Découplage** : APP4 documente la gouvernance **sans dépendre** d’APP1/2/3

---

## Fonctionnement (pipeline résumé)

1) **Entrée (source of truth)**  
   `data/inputs/demo_decisions.yaml`  
   Formats supportés :
   - liste de records
   - wrapper `{ decisions: [...] }`

2) **Validation déterministe**  
   Parsing + contrôle des champs + enums + date + unicité des IDs

3) **Sorties**
   - `decision_register.md` (lecture “humaine”)
   - `decision_register.csv` (exploitation tableur)
   - `decision_register.json` (intégration/outillage)

> APP4 ne fait aucune “décision automatique”.  
> Il trace et exporte des décisions **humaines**.

---

## Installation (local)

```powershell
python -m venv venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -e ".[dev]"
# Tests (CI-friendly)
pytest -q
```

---

## Quickstart

### Option A — Lecture rapide (sans exécution)

Ouvrir directement la source-of-truth :
- data/inputs/demo_decisions.yaml

Tu y verras notamment :
- gouvernance IA “suggestion-only” (R1)
- standardisation multi-apps (R2)
- lisibilité recruteur < 2 minutes (R3)
- stratégie de tests (R4)
- hygiène outputs/démo (R5)
- standard env/outillage (R6)

###  Option B — Reproduire localement (recommandé)

```powershell
python -m vv_app4_vvdr.main --verbose
```

Génère automatiquement :
- data/outputs/decision_register.md
- data/outputs/decision_register.csv
- data/outputs/decision_register.json

Ouvrir le .md / .csv / .json pour vérifier :
- ordre stable
- contenu cohérent
- aucune dépendance externe

---

## Structure du projet

```text
vv-app4-vvdr/
├─ src/
│  └─ vv_app4_vvdr/
│     ├─ models.py
│     ├─ io_loader.py
│     ├─ export.py
│     └─ main.py
├─ tests/
├─ data/
│  └─ inputs/
├─ docs/
└─ README.md
```

---

## ⚖️ Usage & licence

Ce dépôt est fourni à des fins de démonstration et d’évaluation professionnelle uniquement.

Il ne constitue pas un produit certifié ni un outil industriel prêt à l’emploi.
Les décisions et impacts doivent être analysés et validés par un humain.

© 2026 JBTB. Tous droits réservés.
Voir le fichier LICENSE
 pour les conditions complètes d’utilisation.