"""Placeholder helper for future paper asset export logic."""

from __future__ import annotations

from pathlib import Path


def export_assets(root: Path) -> None:
    figures = root / "paper" / "assets" / "figures"
    tables = root / "paper" / "assets" / "tables"
    print(f"[template] figures dir: {figures}")
    print(f"[template] tables dir: {tables}")
