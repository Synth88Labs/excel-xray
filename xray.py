"""
xray.py — Excel X-Ray: audit any workbook for hidden risks.

Reads an .xlsx file, analyzes it for formula errors, inconsistent formulas,
external links, volatile functions, and hidden sheets, then writes a branded
HTML report and prints a Health Score summary.

Usage:
    python xray.py <workbook.xlsx> [-o report.html]

Example:
    python xray.py budget.xlsx -o budget_xray.html

Author: Synth88Labs
License: MIT
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from analyze import analyze
from report import render_html


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Audit an Excel workbook for hidden risks.")
    p.add_argument("input", type=Path, help="Input .xlsx / .xlsm file.")
    p.add_argument("-o", "--output", type=Path, default=None,
                   help="Output HTML report path. Default: '<name>_xray.html'.")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.input.is_file():
        print(f"Error: '{args.input}' is not a file.", file=sys.stderr)
        return 1
    if args.input.suffix.lower() not in (".xlsx", ".xlsm", ".xltx", ".xltm"):
        print(f"Error: X-Ray needs an Excel workbook (.xlsx/.xlsm), not '{args.input.suffix}'.",
              file=sys.stderr)
        return 1

    try:
        result = analyze(args.input)
    except Exception as exc:  # noqa: BLE001
        print(f"Error analyzing '{args.input}': {exc}", file=sys.stderr)
        return 1

    out_path = args.output or args.input.with_name(f"{args.input.stem}_xray.html")
    out_path.write_text(render_html(result), encoding="utf-8")

    print(f"Excel X-Ray — {args.input.name}")
    print(f"  Health Score: {result.health}/100  (Grade {result.grade} — {result.risk_label})")
    print(f"  Sheets: {result.n_sheets}   Formula cells: {result.n_formulas}   "
          f"Findings: {len(result.findings)}")
    if result.counts:
        for cat, n in sorted(result.counts.items(), key=lambda kv: -kv[1]):
            print(f"    - {cat}: {n}")
    print(f"\nReport saved: {out_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
