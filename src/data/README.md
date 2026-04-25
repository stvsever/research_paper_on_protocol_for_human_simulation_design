# Data

All files under `data/raw/` are **excluded from this repository** — they are either too large for version control, governed by source-specific data-use terms that prohibit redistribution, or both. This README documents what is needed, where to get it, and where to place it.

Preprocessed files will live under `data/interim/` (task-specific, generated). Locked analysis-ready files will live under `data/processed/` (generated). Neither is versioned.

---

## Required Datasets

| Dataset | Domain | Where to retrieve | Target path |
|---|---|---|---|
| AIID confirmatory subset | Individual differences, explicit/implicit attitudes | [OSF project osf.io/pcjwf](https://osf.io/pcjwf/) — download `AIID_subset_confirmatory.csv.zip` | `data/raw/aiid/` |
| Project Implicit Race IAT 2025 | Implicit cognition, intergroup bias | [OSF osf.io/52qxl](https://osf.io/52qxl/) — download archive and codebooks | `data/raw/project_implicit_demo/race_iat/` |
| ANES Time Series Cumulative File | Political behavior, elections | [electionstudies.org](https://electionstudies.org/data-center/anes-time-series-cumulative-data-file/) — requires free registration | `data/raw/anes_cdf/` |
| General Social Survey | US social attitudes | [gss.norc.org](https://gss.norc.org/content/norc/us/en/gss/get-the-data.html) — requires free registration | `data/raw/gss/` |
| European Social Survey rounds 1–11 | Cross-national European attitudes | Zenodo DOI [10.5281/zenodo.12799641](https://doi.org/10.5281/zenodo.12799641) — browser download required (direct curl returns 403) | `data/raw/ess/` |
| World Values Survey Wave 7 | Global values and culture | [worldvaluessurvey.org](https://www.worldvaluessurvey.org/WVSDocumentationWV7.jsp) — requires WVSA terms acceptance | `data/raw/wvs/` |
| Moral Machine | Moral dilemmas, cross-cultural ethics | [osf.io/3hvt2](https://osf.io/3hvt2/) — large files; download only if needed for confirmatory analysis | `data/raw/moral_machine/` |
| Psych-101 / Centaur | Trial-by-trial cognition | Hugging Face `marcelbinz/psych-101` — pull intentionally via `datasets` or `huggingface_hub`; primary file is large | `data/raw/psych101_centaur/` |

---

## Model Benchmark Reference

The frozen pilot model-to-MMLU mapping is stored in the repository at:

```
data/raw/model_benchmarks/mmlu_pilot_model_mapping.csv
```

> **Note:** This file is not in the repository either — retrieve it from the `src/ontologies/` context or reconstruct from the preregistration (Section 24.1).

---

## Size and License Notes

| Dataset | Approx. size | License / terms |
|---|---|---|
| AIID subset | ~39 MB (zip) | CC-BY 4.0 |
| Race IAT 2025 | ~71 MB (zip) | Project Implicit data-use agreement |
| ANES | ~50–200 MB | Free for non-commercial research |
| GSS | ~50–300 MB | Free for non-commercial research |
| ESS | ~100–500 MB | CC-BY 4.0 |
| WVS Wave 7 | ~50–100 MB | WVSA non-commercial research terms |
| Moral Machine (full) | Several GB | See Nature article and OSF notes |
| Psych-101 (full) | Several GB | See Hugging Face dataset card |

---

## Preprocessing Policy

Before any LLM call or confirmatory scoring:

1. Review each source license and data-use terms.
2. Remove direct identifiers and suppress rare identifying combinations.
3. Create deterministic task manifests (outcome variables, predictors, split seeds, weights, recodes, missingness rules).
4. Store raw data unchanged under `data/raw/`; write derived files only to `data/interim/` or `data/processed/`.
5. Do not place API keys, credentials, or private notes in this directory.
