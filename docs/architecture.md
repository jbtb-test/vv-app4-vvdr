# APP4 — VVDR Architecture

## Objectif

APP4 (VVDR — V&V Decision Register) est une application de **gouvernance** destinée à
tracer, structurer et exporter des **décisions humaines** liées à la qualité,
aux risques et aux règles du portfolio V&V.

Elle **ne pilote aucune autre application** (APP1 / APP2 / APP3) et n’introduit
aucune automatisation décisionnelle.

---

## Positionnement dans le portfolio

APP4 répond à la question :

> **“Pourquoi ces règles, ces choix, cette gouvernance ?”**

| App | Question couverte |
|----|-------------------|
| APP1 | Qualité des exigences |
| APP2 | Traçabilité & couverture |
| APP3 | Accélération IA (suggestions) |
| **APP4** | **WHY — décisions & gouvernance** |

---

## Pipeline fonctionnel

```text
YAML (source of truth)
|
v
Validation déterministe
(schema + règles + unicité)
|
v
Exports figés
(MD / CSV / JSON)
```

---

### 1. Entrée — Source of truth

- Fichier YAML versionné :
  `data/inputs/demo_decisions.yaml`
- Formats supportés :
  - liste simple
  - wrapper `{ decisions: [...] }`

---

### 2. Validation déterministe

Chaque décision est validée sur :

- champs obligatoires
- enums contrôlés
- format de date
- unicité des `decision_id`
- liens explicites aux risques (R1…R6)

Toute erreur bloque la génération.

---

### 3. Exports

Sorties générées **sans dépendance externe** :

- `decision_register.md` — lecture humaine / audit
- `decision_register.csv` — analyse tableur
- `decision_register.json` — intégration outillage

Ordre stable, contenu reproductible.

---

## Principes clés

- décisions **humaines uniquement**
- aucun impact automatique sur APP1/2/3
- déterminisme total
- audit-ready
- gouvernance explicite et traçable

---

## Conclusion

APP4 est une brique de **maturité V&V** :
elle rend visibles et démontrables les décisions
qui structurent le reste du portfolio.
