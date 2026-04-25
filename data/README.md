# Data Staging Area

This directory stages raw source files and source-retrieval notes for the preregistered study:

`Which design choices make LLM-generated human behavioral data more valid?`

The goal at this stage is not to preprocess the data, but to make source status explicit before the pilot and full sampling loops begin. Raw source files are kept under `data/raw/`; cleaned task-specific files should later be written to `data/interim/` and locked analysis-ready files to `data/processed/`.

## Current Structure

| Path | Purpose |
| --- | --- |
| `data/raw/aiid/` | AIID OSF confirmatory subset and source notes. |
| `data/raw/project_implicit_demo/race_iat/` | Project Implicit Race IAT 2025 raw archive and codebooks. |
| `data/raw/anes_cdf/` | ANES cumulative-file documentation; data file requires manual retrieval. |
| `data/raw/gss/` | GSS documentation; data file requires manual retrieval or extraction. |
| `data/raw/ess/` | ESS source metadata; raw Zenodo file currently requires browser/manual retrieval because direct curl returned 403. |
| `data/raw/wvs/` | WVS retrieval notes; raw data requires site-mediated download/registration. |
| `data/raw/moral_machine/` | Moral Machine documentation and small country-level archives; full response files are too large for automatic download here. |
| `data/raw/psych101_centaur/` | Psych-101/Centaur Hugging Face dataset card; full prompt/response file is large and should be pulled intentionally. |
| `data/raw/model_benchmarks/` | Frozen pilot MMLU target-to-model mapping and OpenRouter validation notes. |
| `data/sources_manifest.json` | Machine-readable source manifest with domain, DOI where available, and retrieval status. |

## Files Downloaded Automatically

The following files were downloaded on 2026-04-25:

| Source | Downloaded files |
| --- | --- |
| AIID | `AIID_subset_confirmatory.csv.zip`, `README.md` |
| Project Implicit Race IAT | `Race_IAT.public.2025.csv.zip`, `Race_IAT.public.2025.codebook.csv`, `Race_IAT_public_2002-2025_codebook.xlsx`, `readme.2025.txt` |
| ANES | `anes_timeseries_cdf_codebook_var_20260205.pdf` |
| GSS | `GSS_2024_Codebook_R2.pdf` |
| ESS | `zenodo_12799641_metadata.json` |
| Moral Machine | `MMdata_ReadMe.txt`, `country_cluster_map.csv.zip`, `moral_distance.csv.zip`, `CountriesChangePr.csv.tar.gz` |
| Psych-101/Centaur | `README.md` |
| Model benchmarks | `mmlu_pilot_model_mapping.csv`, `openrouter_validation_2026-04-25.md` |

## Manual or Intentional Retrieval Still Needed

These sources need either authenticated/manual download, explicit acceptance of terms, or a deliberate large-file pull:

1. ANES cumulative raw data file: download from the ANES data center and place the raw file in `data/raw/anes_cdf/`.
2. GSS cumulative raw data: retrieve from GSS Data Explorer or the official GSS/NORC download interface and place it in `data/raw/gss/`.
3. ESS merged data: the Zenodo metadata is present, but direct command-line download returned HTTP 403. Use the Zenodo browser download for DOI `10.5281/zenodo.12799641` and place the `.dta` file in `data/raw/ess/`.
4. WVS raw data: retrieve the WVS Wave 7 or time-series dataset after accepting WVSA terms and place it in `data/raw/wvs/`.
5. Moral Machine full response data: the large individual-level response files should be downloaded only if needed for confirmatory analysis, because they are hundreds of MB to multiple GB.
6. Psych-101 full data: pull the Hugging Face dataset intentionally using `datasets` or `huggingface_hub` because the primary prompt file is large.
7. Additional Project Implicit domains: only Race IAT 2025 was staged automatically. Other Project Implicit domains should be added as separate subdirectories if included.

## Preprocessing Policy

Before any LLM call or confirmatory scoring:

1. Review each source license and data-use terms.
2. Remove direct identifiers and suppress rare identifying combinations.
3. Create deterministic task manifests documenting outcome variables, predictors, split seeds, weights, recodes, missingness rules, and excluded variables.
4. Store raw data unchanged under `data/raw/`; write derived files only under `data/interim/` or `data/processed/`.
5. Do not place API keys, credentials, private notes, or account metadata in this directory.

