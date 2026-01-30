#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
vv_app4_vvdr
------------------------------------------------------------
Description :
    APP4 — VVDR (Verification & Validation Decision Register)

Rôle :
    - Fournir un registre décisionnel humain, auditable et déterministe
    - Consolider les décisions issues des constats APP1 / APP2 / APP3
    - Aucun couplage technique avec les autres apps
    - Aucune automatisation décisionnelle (pas d’IA au MVP)

API publique (stable) :
    - __version__ : version applicative
    - Domain models / loaders / exports exposés explicitement
============================================================
"""

from __future__ import annotations

# ============================================================
# Version (source of truth = pyproject.toml)
# ============================================================
__version__: str = "0.1.0"

# ============================================================
# API publique (sera enrichie progressivement)
# ============================================================
__all__: list[str] = [
    "__version__",
]
