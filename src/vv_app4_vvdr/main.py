#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
vv_app4_vvdr.main
------------------------------------------------------------
Description:
    CLI entry point for APP4 VVDR (Verification & Validation
    Decision Register).

    Orchestrates:
      1) YAML loading (source of truth)
      2) Domain validation + deterministic ordering
      3) Exports (MD / CSV / JSON)

Usage:
    python -m vv_app4_vvdr.main
    python -m vv_app4_vvdr.main --input data/inputs/demo_decisions.yaml
    python -m vv_app4_vvdr.main --out-dir data/outputs --verbose

Options:
    --input     Path to YAML decision register
    --out-dir   Output directory for exports
    --verbose   Enable verbose logging

Exit codes:
    0  Success
    1  User / domain / I/O error
============================================================
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import NoReturn

from vv_app4_vvdr.io_loader import YamlLoaderError, load_decisions_from_yaml
from vv_app4_vvdr.export import ExportError, export_decision_register
from vv_app4_vvdr import __version__


# ============================================================
# CLI
# ============================================================
def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vv-app4-vvdr",
        description=(
            "APP4 VVDR — Decision Register\n\n"
            "Load a YAML decision register (source of truth) and generate\n"
            "deterministic exports (MD / CSV / JSON)."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/inputs/demo_decisions.yaml"),
        help="Path to input YAML decision register (default: data/inputs/demo_decisions.yaml)",
    )

    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/outputs"),
        help="Output directory for generated artifacts (default: data/outputs)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


# ============================================================
# Orchestration
# ============================================================
def run(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    if args.verbose:
        print("[VVDR] Starting decision register generation")
        print(f"[VVDR] Input YAML : {args.input}")
        print(f"[VVDR] Output dir : {args.out_dir}")

    try:
        records = load_decisions_from_yaml(args.input)

        if args.verbose:
            print(f"[VVDR] Loaded {len(records)} decision record(s)")

        outputs = export_decision_register(records, args.out_dir)

        if args.verbose:
            print("[VVDR] Generated artifacts:")
            for name, path in outputs.items():
                print(f"  - {name.upper():4s}: {path}")

        return 0

    except (YamlLoaderError, ExportError) as exc:
        print(f"[VVDR][ERROR] {exc}", file=sys.stderr)
        return 1

    except Exception as exc:  # last-resort guard
        print(f"[VVDR][FATAL] Unexpected error: {exc}", file=sys.stderr)
        return 1


def main() -> NoReturn:
    sys.exit(run())


if __name__ == "__main__":
    main()
