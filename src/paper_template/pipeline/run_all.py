"""Print the stage order for the template workflow."""

from __future__ import annotations

STAGES = [
    "01_protocol",
    "02_search_development",
    "03_source_collection",
    "04_record_management",
    "05_screening",
    "06_full_text_eligibility",
    "07_construct_extraction",
    "08_synthesis",
    "09_domain_tagging",
    "10_framework_construction",
    "11_instrument_finalization",
    "12_measurement_calibration",
    "13_prompt_calibration",
    "14_model_scoring",
    "15_robustness_sensitivity_network",
    "16_output_freeze",
    "17_manuscript_preparation",
]


def run_all() -> None:
    for stage in STAGES:
        print(f"[template] ready: {stage}")
