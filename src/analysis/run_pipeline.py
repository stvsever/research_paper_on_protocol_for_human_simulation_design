"""Minimal analysis pipeline stub for the research paper template."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUTS = ROOT / "src" / "outputs" / "analysis"


def run_pipeline() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    manifest = {
        "project": "[Project Name]",
        "status": "template",
        "next_steps": [
            "Replace placeholder text and assets.",
            "Add project-specific analysis code.",
            "Update workflow stage names if needed.",
        ],
    }
    (OUTPUTS / "results_manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    print(f"[template] analysis scaffold ready: {OUTPUTS}")


if __name__ == "__main__":
    run_pipeline()
