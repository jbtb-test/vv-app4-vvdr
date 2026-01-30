# INTERNAL — Governance & Decision Policy (APP4 VVDR)

## Rôle d’APP4

APP4 est un **registre décisionnel** destiné à tracer des décisions humaines
structurantes liées à la qualité, aux risques et aux règles V&V.

Il n’exécute aucune logique métier.

---

## Types de décisions

- GOVERNANCE
- PROCESS
- QUALITY

Chaque décision :
- est datée
- justifiée
- liée à un ou plusieurs risques (R1…R6)
- versionnée via Git

---

## Règles de gouvernance

- une décision = un sujet structurant
- pas de micro-décisions
- toute évolution → nouvelle décision avec `supersedes`
- aucune décision implicite

---

## Relation avec les risques

Chaque décision doit :
- couvrir au moins un risque identifié
- apporter une mitigation claire
- être vérifiable via preuve (Rx-V)

---

## Non-objectifs

APP4 ne :
- calcule rien
- décide rien automatiquement
- remplace pas l’humain
- dépend pas des autres apps

---

## Conclusion

APP4 formalise la gouvernance V&V du portfolio
et constitue une preuve de maturité méthodologique.
