# Preregistration: A Data-Driven Protocol for LLM-Based Simulation of Human Behavior

Preregistration version: 1.4 draft for OSF registration  
Date: 2026-04-25  
Author: Stijn Van Severen  
Contact: stijn.vanseveren@ugent.be  
Repository scope: `/Users/stijnvanseveren/PythonProjects/research_paper_on_synthetic_generation_design`  
Canonical ontology: `src/ontologies/ontology.json`  
Canonical deviations log: `src/preregistration/deviations.md`

## 1. Study Title

A Data-Driven Protocol for LLM-Based Simulation of Human Behavior: An Ontology-Grounded, Multi-Dataset Study of Silicon-Human Fidelity.

## 2. Short Summary

This study will evaluate how design choices in large language model (LLM)-based human-data simulation affect fidelity to empirical human datasets. The design space is represented by a machine-readable ontology of eligible simulation configurations (`src/ontologies/ontology.json`). The study will first run a narrow pilot over a deliberately simple subset of the sampling space, then execute a larger preregistered sampling loop over eligible configurations. For each configuration and dataset, LLM-generated "silicon" responses will be compared against held-out human responses using standardized performance metrics that can be aggregated across outcome types. Two preregistered machine-learning approaches will then be used to estimate which design features explain the largest variance in simulation performance: a transparent linear OLS/WLS explanatory model with explicit collinearity handling and an XGBoost gradient-boosted tree model with SHAP explanations. The final output will be a data-driven protocol for selecting, validating, and reporting LLM-based simulators of human data.

## 3. Research Questions

RQ1. Across diverse open-access human datasets, how much does silicon-human fidelity vary as a function of LLM simulation design configuration?

RQ2. Which ontology-coded design features explain the largest variance in simulation performance across datasets and outcome types?

RQ3. Do a transparent linear model and a nonlinear ensemble model converge on the same high-importance design features, and where do they diverge?

RQ4. Can feature-importance estimates, robustness analyses, and held-out validation be converted into a generalizable protocol for designing LLM-based simulators of human behavioral data?

## 4. Confirmatory Hypotheses

H1. Simulation fidelity will vary substantially across design configurations after controlling for dataset and outcome type.

H2. Model capability, response-format design, contextual/persona conditioning, and evaluation/auditing loops will explain a non-trivial share of performance variance.

H3. Critic-actor realism auditing will improve average fidelity relative to single-pass generation, but its benefit will be heterogeneous and may be larger for socially contextual, morally evaluative, or high-ambiguity tasks than for highly structured factual or forced-choice tasks.

H4. A protocol built from stable design-feature importance will outperform a conventional baseline protocol and random eligible configurations on locked test configurations and held-out datasets.

## 5. Study Type

This is a computational, secondary-data, preregistered methodological study. No new human participants will be recruited. Human benchmark datasets will be open-access, open-source, public-use, or accessible under non-commercial research terms compatible with the planned analyses. The main empirical units are configuration-dataset cells, where each cell consists of one eligible LLM simulation design applied to one human benchmark dataset or dataset task.

## 6. Core Design Artifacts

The simulation design space is defined by:

1. `src/ontologies/build_ontology.py`: source-of-truth builder for the ontology.
2. `src/ontologies/ontology.json`: canonical machine-readable ontology.
3. `src/ontologies/sample_configurations.py`: CLI sampler that returns eligible configurations after applying cardinality rules and hard constraints.
4. `src/ontologies/samples/eligible_samples.txt`: example output format.
5. `src/preregistration/deviations.md`: public log for pilot-driven and full-study deviations.
6. `src/data/README.md` and `src/data/sources_manifest.json`: raw-source staging notes, source URLs, dataset-domain descriptions, DOI status where available, and manual retrieval instructions.

The ontology encodes design features as leaf nodes with metadata including variable type, stage, role, outcome modes, local requires/forbids, tags, cost class, and compatibility notes. Hard constraints are applied before a sampled configuration is considered eligible. Soft and advisory constraints are retained for analysis but do not invalidate configurations.

## 7. Human Benchmark Dataset Pool

The study will prioritize datasets that are open-access or open-source, cover different prediction contexts, and contain individual-level human responses with enough metadata to define held-out prediction tasks.

Primary candidate datasets:

| Dataset | Domain family | Prediction context | Planned role | Data-staging status |
| --- | --- | --- | --- | --- |
| AIID: Attitudes, Identities, and Individual Differences | Individual differences, identity, explicit/implicit social attitudes, psychometrics | Person-level explicit attitudes, implicit attitudes, identities, demographics, and individual-difference measures collected via Project Implicit | Mandatory primary dataset for inter-individual heterogeneity | Confirmatory subset downloaded to `src/data/raw/aiid/` |
| Project Implicit Demo Website Datasets: Race IAT staged first | Implicit cognition, reaction-time social cognition, explicit attitudes, intergroup bias | IAT scores, explicit race attitudes, demographics, and task metadata; other Project Implicit domains may be added as separate dataset-family strata | Primary social-cognition dataset family | Race IAT 2025 archive and codebooks downloaded to `src/data/raw/project_implicit_demo/race_iat/` |
| ANES Time Series Cumulative File | Political behavior, elections, ideology, issue positions, public opinion | Vote choice, party identification, ideology, policy preferences, demographics, and election-year context | Primary political-behavior dataset | Current codebook downloaded; raw data file requires manual ANES retrieval |
| General Social Survey | US social attitudes, demographics, behavior, religion, morality, social norms | Survey responses across attitudes, institutions, social behavior, demographics, and social change | Primary broad social-survey dataset | Current codebook downloaded; raw extract requires GSS Data Explorer or official GSS retrieval |
| European Social Survey | Cross-national European attitudes, politics, trust, well-being, social behavior | Country/round/respondent-level predictors and survey outcomes across European countries | Cross-national validation dataset | Zenodo metadata downloaded; direct raw-data curl returned 403, manual browser download required |
| World Values Survey | Global values, culture, religion, trust, political attitudes, morality, norms | Cross-national value and belief responses across countries and waves | Global cross-cultural values dataset | Manual WVS retrieval required after accepting terms |
| Moral Machine | Moral judgment, autonomous-vehicle dilemmas, cross-cultural ethics | Forced-choice moral dilemmas with scenario attributes and country-level context | Moral-judgment and distributional-choice dataset | Documentation and small auxiliary files downloaded; large response archives deferred |
| Psych-101 / Centaur dataset | Cognitive science, trial-by-trial decision-making, psychological experiments | Trial-level choices across many natural-language psychological experiments | Cognitive-behavior external validation dataset, subject to license and compute feasibility | Hugging Face dataset card downloaded; large data files deferred |

The dataset pool deliberately spans at least seven prediction-context families: individual differences and identity, implicit social cognition, political behavior, broad social surveys, cross-cultural values, moral dilemma choice, and trial-by-trial cognition. This diversity is necessary because a protocol that only performs well on one survey family would not justify broad claims about LLM-based simulation of human data.

Dataset inclusion criteria:

1. The dataset is public-use, open-access, open-source, or otherwise available for non-commercial academic analysis.
2. The dataset includes human response variables that can be predicted or simulated from non-identifying context.
3. The dataset includes enough metadata to define at least one benchmark task with train/calibration/test splits.
4. The dataset license permits automated analysis and use of non-identifying records in prompts or prompt-derived summaries.
5. The dataset can be represented as one or more outcome modes in the ontology: regression, binary, multiclass, ordinal, ranking, distribution, sequence, graph, text-judged, latent-regression, or hierarchical-mixed.

Dataset exclusion criteria:

1. Data-use terms forbid the planned computational use or uploading of non-identifying records to third-party APIs.
2. The data contain direct identifiers that cannot be removed or transformed before LLM use.
3. The task requires private sensitive information that cannot be safely coarsened or summarized.
4. The dataset cannot support a held-out human benchmark after preprocessing.
5. The dataset cannot be documented sufficiently for reproducible scoring.

If a planned dataset is unavailable or incompatible, it will be replaced by another open dataset from the same prediction-context stratum where possible. Replacements will be logged in `src/preregistration/deviations.md` before full confirmatory analysis.

## 8. Human Data Preprocessing

For each dataset, the following preprocessing plan will be applied before any confirmatory LLM generation:

1. Remove direct identifiers and variables prohibited by the dataset license.
2. Coarsen or suppress rare demographic combinations that could increase re-identification risk.
3. Define task-specific outcome variables and predictor/context variables.
4. Harmonize outcome coding into explicit ontology outcome modes.
5. Create deterministic dataset splits using fixed seeds:
   - 60 percent training/reference split.
   - 20 percent calibration/validation split.
   - 20 percent locked human test split.
6. Preserve survey weights where provided; use unweighted analysis only if weights are unavailable or incompatible with a given metric.
7. Document all recodes, exclusions, missingness rules, and task definitions in dataset-specific preprocessing manifests.

The training/reference split may be used to construct prompt templates, response-option descriptions, item metadata, population summaries, or persona conditioning summaries. The calibration split may be used during the pilot for debugging, prompt sanity checks, metric validation, and budget estimation. The locked human test split will not be used to optimize prompts, select configurations, choose hyperparameters, or decide exclusions.

## 9. Synthetic Data Generation Overview

For each eligible configuration-dataset cell, the system will generate silicon responses to match the structure of the human benchmark task. Depending on the task, simulation units may be individual respondents, respondent-item pairs, sessions, item blocks, trajectories, or group-level distributions.

All LLM calls will be routed through OpenRouter for logistical consistency using a single OpenRouter API key. The `.env` file at the repository root was checked on 2026-04-25 and contains `OPENROUTER_API_KEY`. The OpenRouter `/api/v1/key` endpoint returned HTTP 200 using that key on 2026-04-25. This validation establishes that the key is present and accepted; the key itself, key label, and any sensitive account metadata will not be written into preregistration text, logs, prompts, or generated artifacts.

The study will log model identifier, canonical slug when available, provider metadata returned by OpenRouter, temperature, top-p, seed support, prompt version, output schema, retry count, timestamp, token usage, and cost where available. API routing will not be used to silently substitute a different model unless the substitution rule has been preregistered or logged as a deviation.

Generated data will be stored separately from raw human benchmark data. Prompts will be versioned and rendered from templates. Any prompt that includes human-derived context will use non-identifying, license-compatible, task-relevant information only.

## 10. Pilot Study

The pilot is intended to validate execution, metrics, logging, prompt rendering, parsing, cost estimates, and basic signal detectability. Pilot results will not be treated as confirmatory evidence for the final protocol. Pilot-driven changes to the full-study plan will be logged in `src/preregistration/deviations.md` before the full sampling loop begins.

### 10.1 Pilot Factors

The pilot will vary exactly three simple design factors:

1. Latent model performance target via MMLU: ten target values spanning the full practical range from the weakest commercially available instruction-tuned text model on OpenRouter to the current frontier, selected to provide dense coverage of the capability dimension and to minimize range restriction.
2. Critic-actor realism auditing: absent versus present.
3. Conditioning depth: minimal demographic/task conditioning versus full observed non-identifying conditioning.

This yields 10 × 2 × 2 = 40 pilot design cells per dataset task before replication.

### 10.2 Pilot MMLU Target Values and Model Mapping

The pilot uses target MMLU values, not bins. For each target, the selected model is the OpenRouter-accessible model with the closest documented MMLU score in the frozen benchmark table used at preregistration time. The OpenRouter `/api/v1/models` endpoint was queried on 2026-04-25 and all ten candidate model IDs were confirmed available. For small Llama 3.2 models, MMLU values are taken from the published Meta model card. For other models, values are taken from the LM Market Cap benchmark table or the model's official published benchmarks. The selection rule will be rerun only if a selected model is unavailable at execution time, and any replacement will be logged in `src/preregistration/deviations.md`.

| Target MMLU | Selected pilot model | OpenRouter model id | Documented MMLU | Abs. diff | Primary source |
| ---: | --- | --- | ---: | ---: | --- |
| 0.35 | Liquid LFM 2.5 1.2B Instruct | `liquid/lfm-2.5-1.2b-instruct:free` | TBD | TBD | Liquid AI model card — **confirm before pilot execution**; see fallback rule below |
| 0.49 | Meta Llama 3.2 1B Instruct | `meta-llama/llama-3.2-1b-instruct` | 0.493 | 0.003 | Meta Llama 3.2 model card |
| 0.63 | Meta Llama 3.2 3B Instruct | `meta-llama/llama-3.2-3b-instruct` | 0.634 | 0.004 | Meta Llama 3.2 model card |
| 0.73 | Meta Llama 3.1 8B Instruct | `meta-llama/llama-3.1-8b-instruct` | 0.730 | 0.000 | Meta Llama 3.1 published benchmarks |
| 0.75 | Google Gemma 2 27B | `google/gemma-2-27b-it` | 0.752 | 0.002 | LM Market Cap benchmark table |
| 0.82 | OpenAI GPT-4o mini | `openai/gpt-4o-mini` | 0.820 | 0.000 | LM Market Cap benchmark table |
| 0.85 | Microsoft Phi-4 | `microsoft/phi-4` | 0.848 | 0.002 | Microsoft Phi-4 published benchmarks |
| 0.86 | Meta Llama 3.3 70B Instruct | `meta-llama/llama-3.3-70b-instruct` | 0.860 | 0.000 | Meta Llama 3.3 published benchmarks |
| 0.88 | OpenAI GPT-4o | `openai/gpt-4o` | 0.887 | 0.007 | LM Market Cap benchmark table |
| 0.93 | OpenAI GPT-5 | `openai/gpt-5` | 0.930 | 0.000 | LM Market Cap benchmark table |

The ten-level MMLU range (0.35–0.93, span ≈ 0.58) is designed to provide dense capability coverage and to avoid range restriction. The bottom anchor targets the practical lower bound of commercially accessible instruction-tuned text models on OpenRouter. Notes on specific tiers:

- Targets 0.73 and 0.75 are deliberately kept as separate tiers because they represent qualitatively different model architectures and scale classes (8 B dense Llama versus 27 B dense Gemma); the realized MMLU gap of 0.022 is smaller than the inter-target gap in the rest of the range but is retained to avoid silently excluding this scale class.
- Targets 0.85 and 0.86 represent different model families (dense 14 B Microsoft Phi versus dense 70 B Llama); realized MMLU similarity reflects frontier clustering and is noted as a limitation of the pilot design.
- The LFM 2.5 1.2B MMLU must be confirmed from the Liquid AI published model card before pilot execution. If no model with documented MMLU ≤ 0.43 is available at execution time, the 0.35 anchor will be replaced by `meta-llama/llama-3.2-1b-instruct` (0.493) and logged as a deviation; a range-restriction sensitivity analysis is then preregistered (see Section 19, item 18).
- If the LFM 2.5 1.2B documented MMLU differs from the 0.35 estimate by more than 0.05, it will be retained as the lowest-available anchor and the realized value used as the continuous model-capability variable in analysis.

Tie-breaking rule: if two available models are equally close to a target MMLU value, select the lower-cost model if token pricing differs by at least 20 percent; otherwise select the model from the provider family less represented in the current tier set. The realized MMLU score will be used as the continuous model-capability variable in all analyses.

### 10.3 Pilot Critic-Actor Levels

Absent: one actor model response is generated and parsed without an explicit realism-auditing critic loop.

Present: an actor generates a response, a critic evaluates whether the response is plausible, format-valid, and consistent with the target human context, and the actor may revise once. The critic prompt will not reveal held-out human outcomes. The preregistered pilot loop uses `max_iter = 1` revision after initial generation, rubric-based realism auditing, and accept/revise output control.

### 10.4 Pilot Conditioning-Depth Levels

Minimal conditioning: provide only the task/instrument wording, response options, and a minimal respondent descriptor needed for task legality.

Full observed non-identifying conditioning: provide all license-compatible non-identifying predictor variables selected for the task, including demographics, relevant prior responses, and task context where available. Direct identifiers and rare identifying combinations remain excluded.

### 10.5 Pilot Success Criteria

The full study may proceed if:

1. At least 95 percent of pilot calls return parseable outputs after allowed retries.
2. At least 90 percent of generated rows pass schema validation.
3. The primary standardized fidelity metric can be computed for all included pilot datasets.
4. Logging captures all fields needed to reconstruct configuration, prompt, model, response, and cost.
5. Total projected full-study cost can be estimated within a factor of two from pilot usage.

If any criterion fails, the failure and corrective changes will be recorded as deviations before full generation begins.

## 11. Full Sampling Plan

The full study will sample eligible configurations from `src/ontologies/ontology.json` using `src/ontologies/sample_configurations.py`. The target is a stratified random sample of eligible configurations that covers the major ontology branches while remaining feasible under API and data-use constraints.

Canonical sampler command for conventional-core smoke testing:

```bash
python src/ontologies/sample_configurations.py \
  --preset conventional_core \
  --mode sample \
  --max-samples 100 \
  --scan-limit 20000 \
  --seed 7 \
  --output src/ontologies/samples/eligible_samples.txt
```

Full-study configuration sampling will use fixed seeds and record all candidate and accepted configurations. The planned primary sampling procedure is:

1. Generate an initial pool of eligible configurations from the full ontology using `--mode sample`.
2. Stratify configurations by top-level ontology branches and key design tags, including model capability representation, contextual conditioning, prompt architecture, orchestration/multi-agent design, sampling controls, output representation, postprocessing, quality assurance, and evaluation framework.
3. Deduplicate exact leaf sets.
4. Remove configurations that require unavailable models, unavailable modalities, prohibited data use, or unfeasible cost after pilot-based budget estimation.
5. Freeze the sampled configuration list before full locked-test evaluation.

Coverage rules for the full sample:

1. Continuous and ordinal design variables will be sampled to cover the full feasible value range, not only frontier/high-performance regions. Where the ontology defines a bounded continuous value space, the primary design will use maximin or Latin-hypercube-style coverage over the legal interval.
2. Multiclass and nominal variables will use stratified coverage so that rare but legal design levels are not silently excluded.
3. Hierarchical and mixed outcome configurations will be retained only when respondent/item/group keys needed for valid scoring are preserved.
4. If a high-cardinality categorical feature is too sparse for the ML design matrix, it will be collapsed using ontology parent branches before modeling, not by outcome-driven post hoc grouping.
5. Feasibility filtering for cost, license, model access, or modality access will be performed before locked-test scoring and will be logged separately from performance-based exclusions.

The planned target is at least 500 eligible full-study configurations and at least 3,000 valid configuration-dataset-task cells. If fewer cells are feasible, the study will proceed only if at least 200 eligible configurations and 1,000 valid cells remain; otherwise the full confirmatory analysis will be relabeled exploratory.

### 11.1 Combinatorial State Space and Tractability

The full ontology encodes 1,149 leaf-level design choices across 18 dimensions with mixed cardinality modes (exactly_one, at_least_one, any_subset, etc.) and 44 hard cross-tree constraints. Even under the most conservative estimate—treating each `exactly_one` dimension independently—the eligible state space exceeds 10^30 distinct configurations. Exhaustive enumeration is therefore infeasible; coverage must be achieved through principled stratification rather than completeness.

The primary strategy is three-stage: (a) a **stratified core draw** using the `conventional_core` preset, ensuring coverage of well-validated design families; (b) a **broad random draw** from the full eligible space after constraint filtering, to sample non-conventional combinations; and (c) a **targeted supplementary draw** for ontology branches underrepresented after (a)–(b), specifically subtrees such as multi-agent orchestration, fine-tuning strategies, and multimodal stimuli. Each stage uses a distinct fixed seed and records all candidates scanned.

Coverage is monitored post-hoc by:

1. **Marginal coverage:** for each `exactly_one` group, every legal level must appear in at least one sampled configuration.
2. **Pairwise coverage:** for every pair of top-level ontology dimensions, at least 10 training rows must contain a distinct combination of dimension-level selections.
3. **Scan efficiency:** if the `conventional_core` draw yields fewer than 200 eligible configurations within a scan limit of 50,000 candidates, the scan limit is raised to 200,000 before relaxing the conventional-only filter. If 500 configurations still cannot be reached, the study proceeds with the available pool and the effective coverage is reported explicitly alongside any resulting range-restriction caveats.

This staged design is preferable to purely random sampling because it prevents implicit range restriction—accidentally sampling only configurations that satisfy constraints easily (typically the conventional or minimal-setting cluster)—while remaining computationally feasible without requiring a formal space-filling design over the non-Euclidean, constraint-dense configuration space.

## 12. Outcome Metrics

The primary target for the ML analysis is a standardized silicon-human fidelity score (SHFS) computed for each configuration-dataset-task cell.

For a score-like metric where higher is better:

```text
SHFS = clip((S_config - S_null) / (S_ceiling - S_null), 0, 1)
```

For a loss-like metric where lower is better, the metric will first be converted to a higher-is-better score by subtracting from the null loss:

```text
S_config = L_null - L_config
S_ceiling = L_null - L_human_ceiling
SHFS = clip(S_config / S_ceiling, 0, 1)
```

Definitions:

1. `S_config` or `L_config`: performance of the silicon simulator.
2. `S_null` or `L_null`: task-appropriate null baseline, such as marginal human response distribution, majority class, mean response, or survey-weighted population average.
3. `S_ceiling` or `L_human_ceiling`: estimated human split-half, bootstrap, or train-test reliability ceiling where available.
4. `clip`: values below 0 are set to 0 and values above 1 are set to 1 for the primary aggregate; unclipped scores will be retained for sensitivity analyses.

**Edge-case handling for degenerate baselines.** If S_ceiling ≤ S_null for a given task (i.e., the human split-half or test reliability is at or below the null baseline—indicating a floor-reliability task), the SHFS formula is undefined or degenerate. Such tasks will be: (1) excluded from the primary SHFS aggregate for that cell; (2) reported in a separate "floor-reliability stratum" to document that the benchmark task lacks the reliability required for meaningful silicon-human comparison; and (3) included in the failure-mode analysis (§18). If S_ceiling is unavailable (no split-half or test–retest estimate exists for a dataset-task), a conservative ceiling of 1.0 is substituted, with a note that this may understate fidelity relative to the true human ceiling. Sensitivity of primary conclusions to ceiling imputation is tested in supplementary analysis (§19, item 20).

Metric families by outcome type:

| Outcome mode | Primary metric candidates | Secondary metric candidates |
| --- | --- | --- |
| Binary or multiclass | log loss, Brier score, balanced accuracy | macro-F1, AUROC where defined, ECE calibration |
| Ordinal or Likert | ordinal MAE, polyserial/Spearman correlation | weighted kappa, threshold calibration |
| Continuous | RMSE/MAE, Pearson/Spearman correlation | calibration slope, distributional error |
| Distributional | Jensen-Shannon divergence, Wasserstein distance | KL divergence where safe, total variation |
| Ranking | Kendall tau, Spearman rho | top-k agreement |
| Sequence or trial-by-trial | negative log likelihood, sequence accuracy | transition-matrix recovery |
| Text judged | rubric score by frozen evaluator, embedding similarity | human-audit subset where feasible |
| Graph or network | edge F1, graph edit distance | degree-distribution recovery |
| Hierarchical mixed | level-specific SHFS plus variance-component recovery | item-within-respondent calibration, random-effect correlation |

The primary SHFS will be the mean of standardized task metrics within each cell, with one metric per outcome family selected before locked-test scoring. Secondary outcomes include cost-adjusted SHFS, parse failure rate, refusal rate, token cost, latency, subgroup-fidelity dispersion, calibration error, and distributional similarity.

Mixed-outcome handling:

1. Each task will first be assigned a raw human outcome definition, then an ontology outcome mode, then an analysis model structure, then a metric family.
2. A metric is valid only if its metric family and analysis structure share a legitimate outcome mode with the benchmark task.
3. For hierarchical mixed outcomes, scoring will preserve item/trial-level observations and respondent/group-level keys. The primary hierarchical score will average standardized lower-level prediction fidelity and higher-level variance/correlation recovery.
4. Aggregation to SHFS will occur only after outcome-appropriate metrics have been computed. Raw binary, multiclass, ordinal, continuous, distributional, text, sequence, graph, and hierarchical scores will not be directly pooled without normalization against the null and ceiling baselines.
5. When multiple valid metrics exist for a task, the primary metric will be selected before locked-test scoring; alternative valid metrics will be used only in sensitivity analyses.

## 13. ML Feature Matrix

Each configuration-dataset-task cell will be encoded as a feature vector containing:

1. One-hot ontology leaf indicators.
2. Ontology branch-level aggregates, such as number of selected leaves per top-level dimension.
3. Model-capability variables, including realized MMLU score when used.
4. Dataset descriptors: domain, outcome mode, sample size, number of response options, country/culture coverage, individual-difference richness, task ambiguity, and whether the task is survey-like, moral-choice, political, cognitive, or implicit-attitude based.
5. Execution descriptors: token usage, cost, retry count, parse failure count, and provider metadata.

Feature engineering rules:

1. Exact duplicate features will be removed.
2. Features with zero variance in the training set will be removed.
3. Perfectly collinear one-hot features will be removed using QR/SVD rank checks fit on the training set only.
4. Near-collinear feature clusters will be diagnosed using pairwise association, condition indices, and variance inflation factors. When needed, features will be collapsed upward to the nearest ontology parent branch using deterministic rules that do not inspect outcome values.
5. Binary ontology leaves will be encoded as indicators. Nominal variables will use one-hot or full-rank contrasts. Ordinal variables will use monotone integer coding with categorical sensitivity checks. Continuous variables will be standardized on the training set only. Bounded proportions will use epsilon-clipped logit sensitivity checks. Count variables will use raw and log1p sensitivity checks when overdispersed.
6. Hierarchical keys will be retained for grouped splitting, clustered errors, and mixed-outcome scoring, but direct respondent IDs will not be used as predictive features.
7. Feature transformations will be fit on training data only and applied unchanged to validation/test data.
8. Dataset/task identifiers may be included as fixed effects in the linear model but will not be used to claim generalizable design recommendations unless effects survive held-out dataset validation.
9. Sparse high-cardinality features will be represented by ontology branch aggregates if fewer than 20 training rows support a leaf-level contrast.

### 13.1 Handling the Mixed Hierarchical Nominal/Continuous Input Structure

The ML feature matrix is structurally heterogeneous. Ontology design dimensions vary across at least four variable classes — nominal unordered (e.g., `prompt_framing_strategy`), binary indicator (conventional leaf presence/absence), ordinal (e.g., `instruction_specificity`), and continuous (e.g., realized MMLU score, token count). Within each dimension, leaves are mutually exclusive under `exactly_one` cardinality but unconstrained when multiple cardinalities apply. This structure requires explicit handling in both models.

**Within-branch encoding.** For each ontology group with `exactly_one` cardinality, leaves are one-hot encoded with one reference category. For `any_subset` or `at_least_one` cardinality, leaves are encoded as binary indicators. Branch-level aggregates (e.g., number of leaves selected per top-level dimension, fraction of subset leaves activated) are retained as additional continuous predictors to capture coarse dimensionality effects when leaf-level support is sparse.

**Hierarchical nesting in the linear model.** The 18 top-level dimension groups define a two-level hierarchy: dimensions at the first level, leaves at the second. The branch-first estimation strategy (§15.1) explicitly respects this structure: the first-stage model includes only branch-level aggregates, and leaf contrasts are added incrementally only when (a) they add non-zero independent information after QR/SVD rank checks, and (b) they are supported by at least 20 training rows. Variance decomposition is reported at the branch level to avoid over-attributing importance to individual leaves from high-cardinality branches. When interaction terms involve nominal leaves from different branches, these are encoded as cross-product indicators and subjected to the same Holm-Bonferroni familywise correction as the five preregistered interaction families.

**Hierarchical nesting in XGBoost.** XGBoost does not require explicit hierarchical decomposition, but grouped SHAP aggregation will be applied at the ontology branch level so that correlated one-hot siblings are attributed jointly rather than independently. Specifically, for each ontology group with ≥ 3 leaves, SHAP values of sibling leaves will be summed to form a branch-level SHAP contribution before ranking. This prevents spuriously high individual-leaf importance when the branch effect is strong but any particular leaf has low marginal contrast.

**Continuous design features.** Realized MMLU score and other continuous design variables (e.g., temperature, k in `at_most_k` cardinality groups, token budget) are treated as numeric predictors and entered as standardized continuous effects in the linear model. In XGBoost, SHAP dependence plots for these features will be inspected for threshold or non-monotone effects. If MMLU shows non-monotone SHAP dependence after kernel-smoothed visualization, a piecewise-linear representation (breakpoint at the median capability tier) will be included in the OLS model as a supplementary sensitivity check.

**Cross-level interactions.** Interactions between continuous MMLU capability and nominal prompt/conditioning design leaves are the most methodologically important cross-level interactions in this study. These are the preregistered interaction families 1 and 5 (§15.1). They will be represented as products of standardized MMLU × leaf indicator, entered after the branch-level main effects, and subjected to Holm-Bonferroni correction. This avoids capitalization on chance from the high number of potential leaf × MMLU interactions while keeping the analysis responsive to the scientifically motivated question of whether prompt design effects are moderated by model capability.

## 14. Train, Validation, and Test Splits for ML Analyses

The meta-analytic ML dataset consists of rows representing configuration-dataset-task cells.

Primary split:

1. Training set: 60 percent of configuration IDs.
2. Validation set: 20 percent of configuration IDs.
3. Independent test set: 20 percent of configuration IDs.

Splitting is grouped by configuration ID so that the exact same design configuration does not appear in more than one split. Within each configuration split, dataset-task cells are retained where available. A second split index will group by dataset family for external validation. The primary test set therefore evaluates interpolation to unseen configurations; the external split evaluates generalization to unseen dataset families.

External generalization split:

1. At least one dataset family will be held out from protocol derivation when enough dataset families are available.
2. Psych-101/Centaur and Moral Machine are preferred external validation candidates because they differ from standard survey prediction tasks.
3. If licensing or feasibility prevents those holdouts, the final held-out datasets will be selected before protocol derivation and logged.

Cross-validation:

1. Hyperparameter tuning will use grouped cross-validation within the training set, with groups defined by configuration ID and, in sensitivity checks, by dataset family.
2. Validation performance will guide feature-collapse thresholds, model selection, and early stopping for XGBoost.
3. The independent test set will be evaluated once after all preprocessing, hyperparameters, feature grouping, and protocol-derivation rules are frozen.
4. Leave-one-dataset-family-out cross-validation will be reported as a robustness analysis.
5. Bootstrap uncertainty intervals will resample configuration IDs, not individual rows, to avoid overstating precision from repeated dataset-task cells.

## 15. Primary ML Models

Exactly two primary ML approaches will be used for the main feature-importance conclusions.

### 15.1 Transparent Linear Explanatory Model

The first primary model will be a transparent linear explanatory model estimated as OLS or reliability-weighted least squares after deterministic preprocessing. It is retained because the study needs a directly inspectable estimate of direction, effect size, and variance explained, not only a black-box predictive ranking. The dependent variable is SHFS. If cell-level SHFS has known or estimable uncertainty, the primary linear model will use inverse-variance or reliability weights; otherwise it will use unweighted OLS with the same formula.

Planned fixed-effect formula:

```text
SHFS ~ ontology_branch_features
     + supported_leaf_level_contrasts
     + realized_model_capability
     + dataset_descriptors
     + outcome_mode
     + dataset_family_fixed_effects
     + preregistered_low_order_interactions
```

The linear model will be estimated in a branch-first hierarchy:

1. Fit a branch-level model using ontology parent-branch features and dataset/task descriptors.
2. Add leaf-level contrasts only when the leaf has adequate support and does not make the training design matrix rank deficient.
3. Preserve dataset-family and outcome-mode fixed effects so that design-feature estimates are not confounded with one unusually easy or difficult dataset family.
4. Report leaf-level coefficients as conditional on the retained ontology branch, not as independent causal effects.

Low-order interactions are preregistered for:

1. Realized MMLU capability by outcome mode.
2. Critic-actor auditing by outcome mode.
3. Conditioning depth by dataset domain.
4. Output representation by parser/metric family.
5. Model capability by critic-actor auditing, to test whether auditing compensates for lower base capability or mainly amplifies high-capability models.

Collinearity and rank handling:

1. Exact linear dependencies will be removed using QR/SVD rank checks fit on the training set only. The condition number of the full design matrix (largest / smallest eigenvalue of X'X) will be computed and reported.
2. Variance inflation factors greater than 10, condition indices greater than 30, or pairwise feature correlations above 0.90 will trigger deterministic feature collapsing to ontology parent branches using rules defined on the training set only.
3. For mutually exclusive levels, one reference category or a sum-to-zero contrast will be used; full redundant dummy encodings will not enter the final OLS design.
4. Univariate marginal regressions will be reported as descriptive screening and triangulation only. They will not determine confirmatory feature selection because marginal associations are expected to be confounded by ontology compatibility constraints.
5. Ridge-regularized linear estimates will be reported as a stability sensitivity analysis, but ridge will not replace the preregistered OLS/WLS estimand for primary transparent inference. A LASSO path analysis will additionally be reported to show which features remain non-zero across regularization levels (stability selection); LASSO is used for sensitivity only, not for primary coefficient reporting.

Influential observations:

1. Cook's D and DFFITS will be computed for all training rows in the linear model. Rows with Cook's D > 4/n or DFFITS above 2√(p/n) will be flagged.
2. Flagged rows will be inspected for systematic patterns, such as near-universal parse failures, a single extreme dataset task, or an unusually small within-configuration sample size.
3. The primary result will be from the full training set; sensitivity results excluding high-influence rows will be reported in the supplementary analyses.

Multiple testing correction for interactions:

1. The five preregistered interaction families are tested as a group within the linear model.
2. The familywise error rate across these five interaction tests will be controlled using the Holm-Bonferroni step-down procedure.
3. An interaction will be reported as confirmatory evidence only if it survives Holm-Bonferroni correction and its direction is consistent across at least two grouped cross-validation folds.

Inference and importance:

1. Report standardized coefficients and raw-scale coefficients.
2. Report heteroskedasticity-robust and, where feasible, two-way clustered standard errors by dataset family and configuration family (Cameron and Miller, 2015 multiway clustering).
3. Report partial R-squared and leave-one-feature-group-out cross-validated delta R-squared by ontology branch.
4. Report commonality or dominance-style variance decomposition at the ontology-branch level where collinearity makes individual coefficients misleading.
5. Report coefficient sign stability across grouped cross-validation folds and bootstrap resamples.
6. Do not use stepwise selection for confirmatory conclusions.

If the final linear design remains unstable after the above rules, leaf-level OLS coefficients will be marked descriptive and only branch-level linear variance decomposition will be used for protocol derivation. This does not invalidate the preregistered nonlinear model; it clarifies that the linear model's role is transparent explanation under collinearity rather than maximum predictive accuracy.

### 15.2 XGBoost Model With SHAP Explanation

The second primary model will be an XGBoost gradient-boosted decision-tree regressor predicting SHFS. It is retained because design effects are likely nonlinear, thresholded, and interaction-heavy. XGBoost is the preregistered nonlinear learner; other ensembles may be used only as supplementary robustness checks.

Training plan:

1. Use the same training/validation/test split and deterministic feature preprocessing as the linear model.
2. Tune learning rate, maximum depth, subsample, column subsample, number of estimators, minimum child weight, L1/L2 regularization, and tree-splitting loss by grouped cross-validation inside the training set using Bayesian hyperparameter optimization (Optuna or equivalent) with a grouped k-fold scheme (groups = configuration IDs).
3. Use early stopping on grouped-CV validation loss.
4. Optimize validation RMSE as the primary tuning criterion and report MAE and rank correlation (Spearman) as secondary criteria.
5. Evaluate final model performance once on the independent test set after all tuning is frozen.
6. Report calibration of predicted SHFS values: plot predicted versus actual SHFS on test rows and report calibration slope and intercept. A well-calibrated model should yield slope ≈ 1 and intercept ≈ 0.
7. Fit a sensitivity model with a monotonic constraint on realized MMLU capability only if diagnostics show implausible non-monotonic extrapolation; the unconstrained model remains primary unless the constrained model materially improves held-out performance.

SHAP explanation plan:

1. Compute TreeSHAP values on validation and independent test rows using a training-set background distribution.
2. Report mean absolute SHAP value by feature and by ontology branch.
3. Report signed SHAP dependence plots for the top feature groups, especially MMLU capability, critic-actor auditing, conditioning depth, output representation, and metric/analysis structure.
4. Report SHAP interaction values for the preregistered interaction families where computationally feasible.
5. Bootstrap configuration IDs to estimate stability intervals for SHAP rankings.
6. Use grouped SHAP aggregation for collinear leaf sets so correlated ontology features are not overinterpreted as independent causal drivers.
7. Treat SHAP as model explanation, not causal identification.

A feature or branch will be labeled "high-confidence important" only if all of the following hold:

1. It is among the top-ranked XGBoost feature groups by held-out mean absolute SHAP.
2. Its rank is stable across grouped bootstrap resamples.
3. It has convergent evidence from the transparent linear model, either through partial R-squared, leave-one-group-out delta R-squared, or stable standardized coefficient direction.
4. It does not derive its importance only from failure/cost artifacts unless the protocol rule is explicitly about feasibility rather than fidelity.

## 16. Protocol Derivation Procedure

The final protocol will be derived after all ML models are fit and before any confirmatory manuscript interpretation. It is not a narrative summary: it is a multi-layer, empirically grounded decision guide generated from the evidence table and cross-validated against held-out data.

### 16.1 Evidence Synthesis Table

Before constructing any protocol artifact, assemble a structured evidence table with one row per ontology branch and each of the following columns:

| Column | Content |
|---|---|
| Branch | Ontology dot-path identifier |
| OLS partial R² | Cross-validated contribution to SHFS variance |
| OLS coefficient direction | Stable sign across CV folds (+/−/mixed) |
| SHAP mean absolute | XGBoost mean absolute SHAP on held-out rows |
| Convergence flag | OLS and XGBoost agree on top-5 ranking (Y/N) |
| Conditional flag | Effect size varies > 0.05 across outcome modes or dataset families |
| Cost penalty | Estimated token-cost multiplier relative to conventional baseline |
| Failure rate | Mean parse-failure, refusal, or out-of-range response rate |
| Subgroup fidelity delta | Signed SHFS difference between majority and smallest demographic group |
| Evidence tier | A (convergent strong), B (one model only), C (unstable), D (insufficient support) |

### 16.2 Classification of Design Features

Each branch and leaf is assigned one of four protocol statuses, determined by the evidence table and decision rules defined before analysis:

- **Default recommend:** Evidence tier A or B (positive effect), failure rate < 15%, no evidence of subgroup-fidelity degradation, cost multiplier < 3×. Include in the core protocol.
- **Conditional recommend:** Evidence tier A or B but effect sign or magnitude depends significantly on outcome mode, dataset domain, or model capability range. Include with a condition clause.
- **Avoid unless justified:** Evidence tier A or B with negative or negligible median effect, or failure rate ≥ 25%, or systematic subgroup-fidelity degradation. Accompanied by a brief rationale.
- **Researcher-discretion zone:** Evidence tier C or D (unstable or low-power). Listed in the supplementary protocol inventory without a firm recommendation.

A branch's status will be determined using training-set evidence only; held-out data are reserved for protocol validation (§16.5).

### 16.3 Protocol Layers

The protocol will be presented in four consecutive layers, so researchers with different constraints can extract actionable guidance at their appropriate depth.

**Layer 1 — Universal core (domain-independent):** The 5–10 design choices with the strongest, most stable positive effect on SHFS across all dataset families and outcome types. These are unconditional defaults: any silicon simulation study should adopt them regardless of task. Presented as a short numbered checklist.

**Layer 2 — Domain-conditional rules:** A lookup matrix with rows = outcome type (regression / ordinal / binary classification / distribution recovery / text judgement / ranking) and columns = dataset domain (individual differences, implicit cognition, political behavior, social attitudes, cross-cultural values, moral dilemma, trial-by-trial cognition). Each cell specifies the 2–4 most impactful conditional choices specific to that combination. Missing cells where evidence is insufficient are marked "no data."

**Layer 3 — Resource-adjusted protocol:** A cost-tiered summary showing the best achievable SHFS at three budget levels (low / medium / high token cost per respondent), based on the estimated cost_class of recommended leaves. Researchers with constrained budgets can select from this tier rather than the unconditional Layer 1 defaults.

**Layer 4 — Decision tree:** A branching flowchart with ≤ 12 binary or ternary decision nodes, traversed in order: (1) outcome type, (2) dataset domain, (3) available model capability tier, (4) human conditioning data availability, (5) multi-agent auditing feasibility, (6) output format, (7) postprocessing and validation. Each terminal node specifies the recommended configuration family and an expected SHFS range derived from test data.

### 16.4 Implementation Checklist

Alongside the decision tree, a reporting checklist (modeled on CONSORT style) will be produced specifying which protocol elements must be described in any paper using LLM-based behavioral simulation. Checklist items will be categorized as mandatory (Level 1 protocol), recommended (Level 2–3), or domain-specific optional.

### 16.5 Protocol Validation

The protocol will be evaluated against two held-out sets:

1. **Held-out configurations:** The 20% of eligible configurations withheld from model training (see §14). Configurations selected according to the protocol's Layer 1 defaults should outperform both the conventional-core baseline and a random eligible-configuration baseline.
2. **Held-out dataset families:** At least one dataset family will be withheld from ML training and used only at this validation stage to test cross-domain generalizability of Layer 2 recommendations.

Quantitative validation criteria (preregistered):

- Protocol-selected configurations must achieve mean test SHFS ≥ 0.05 above the conventional-core baseline.
- Protocol-selected configurations must achieve mean test SHFS ≥ 0.03 above a cost-matched random baseline.
- No Layer 1 recommendation may produce a mean demographic-subgroup SHFS gap > 0.10 relative to the majority subgroup.
- Cost-adjusted SHFS (SHFS / cost_multiplier) must not decrease by more than 0.02 relative to the conventional baseline.

If Layer 1 recommendations fail the ≥ 0.05 threshold, the protocol will be downgraded to "empirically suggestive" and the primary conclusion will state that no universal protocol with validated superiority was identified, while reporting conditional effects from Layer 2.

## 17. Baselines

Primary baselines:

1. Human marginal-distribution null baseline.
2. Conventional-core design baseline from the ontology.
3. Single-call, no-critic, minimal-conditioning baseline.
4. Random eligible configuration baseline.

Secondary baselines:

1. Dataset-specific simple statistical model where appropriate.
2. Model-family baseline: same prompt/configuration across pilot models.
3. Cost-matched baseline: best configuration under equal or lower token budget.

## 18. Missing Data, Failures, and Exclusions

Human missing data:

1. Item nonresponse will be handled using task-appropriate complete-case analysis, missingness indicators, or multiple imputation only if required by the dataset and documented before scoring.
2. The primary analysis will not impute held-out outcome variables for scoring.
3. Survey weights and missingness codes will be respected where documented.

LLM failures:

1. Each failed call may be retried up to the preregistered retry limit for that configuration.
2. Parse failures after retries will be recorded as failures and included in secondary failure-rate outcomes.
3. A configuration-dataset cell will be excluded from primary SHFS only if fewer than 80 percent of required simulated rows are valid after retries.
4. Excluded cells will remain in the failure analysis.

Outliers:

1. Token-cost and latency outliers will be retained for cost analysis.
2. SHFS values will be clipped only for the primary normalized aggregate; unclipped values will be analyzed in sensitivity checks.
3. No configuration will be removed for poor performance alone.

## 19. Supplementary and Robustness Analyses

Planned supplementary analyses:

1. Variance decomposition by dataset family, ontology branch, model capability, and outcome mode.
2. Leave-one-dataset-family-out generalization.
3. Leave-one-model-family-out sensitivity.
4. SHFS aggregation sensitivity using alternative metric weights.
5. Exclusion of MMLU/model-capability features to test whether non-model design choices retain importance.
6. Cost-latency Pareto frontier analysis.
7. Subgroup-fidelity analysis by available demographic or identity variables.
8. Robustness to excluding Project Implicit/AIID sensitive-attitude tasks.
9. Critic-actor ablation: actor-only versus actor-critic at matched model and conditioning depth.
10. Prompt-format ablation where response schema permits.
11. Failure-mode taxonomy for refusals, malformed outputs, implausible responses, and over-regularized distributions.
12. Rank stability of OLS and SHAP feature importance under bootstrapping.
13. Comparison of task-level versus dataset-level aggregation.
14. Analysis of whether configurations recover individual-level heterogeneity or only aggregate marginal distributions.
15. Negative-control tasks where no individual-level prediction should be possible beyond marginal distributions.
16. Mixed-effects / multilevel model as supplementary transparency check: fit a two-level random-intercept model with configuration-level predictors at level 1 and dataset-family random intercepts at level 2, using the same feature set as the primary OLS model. This respects the nested structure of cells within dataset families without removing dataset-family variance from the primary OLS estimand. Compare fixed-effect estimates between OLS-with-clustering and the mixed-effects model; systematic divergence will be reported and interpreted.
17. Influential-observation sensitivity: refit primary linear model excluding cells flagged by Cook's D or DFFITS diagnostics; compare coefficient direction and magnitude against the full-data estimates.
18. Range-restriction analysis for pilot MMLU anchor: if the lowest pilot MMLU target (0.35) cannot be filled with a model whose documented MMLU is ≤ 0.43 at execution time, report the effective MMLU range used, estimate the expected attenuation in capability–SHFS slope given the reduced range, and flag any MMLU-related conclusions as potentially conservative.
19. LASSO stability-selection path: report which ontology branch aggregates and leaf indicators remain non-zero as the LASSO penalty increases from near-zero to sparse, using the same training set and preprocessing as the primary OLS model. This provides a data-driven feature-importance ranking that is orthogonal to SHAP.
20. XGBoost calibration check: compare predicted versus actual SHFS on the held-out test set using a calibration plot and report the calibration slope and intercept; over- or under-confidence in SHFS predictions will be reported as a limitation of the SHAP rankings.
21. Semantic embedding cluster analysis: each benchmark item or item group will be represented as a concatenated text string (item wording + response options + dataset context descriptor) and embedded using a single frozen, non-fine-tuned text-embedding model applied uniformly across all datasets (e.g., OpenAI `text-embedding-3-large` or an equivalent open model). In the resulting high-dimensional embedding space, items are clustered using k-means (k selected via gap statistic, minimum k = 3, maximum k = 20) and hierarchical agglomerative clustering (Ward linkage; dendrogram truncated at 10 levels). SHFS values are then regressed on cluster membership as a categorical predictor, controlling for dataset-family and outcome mode fixed effects, to test whether semantically coherent item groups show systematically different fidelity profiles beyond what dataset-family labels capture. This analysis identifies cross-dataset fidelity zones—e.g., whether LLMs consistently underperform on morally ambiguous items or items with rare demographic conditioning—independent of the nominal dataset grouping. Results reported as: (a) 2D UMAP projections of item embeddings colored by SHFS; (b) cluster-level SHFS box plots; (c) partial R² of embedding-cluster membership in the primary OLS model; and (d) qualitative description of the three highest- and three lowest-SHFS semantic clusters.
22. Training-data contamination protocol: see §19.1 for the full preregistered detection pipeline, item-level risk scoring, corrected sampling, and reporting plan.
23. Floor-reliability stratum analysis: all configuration-dataset-task cells excluded from primary SHFS due to degenerate baselines (§12) will be analyzed as a separate stratum. Descriptive statistics of their raw performance scores, parse failure rates, and outcome modes will be reported to document which task families are structurally resistant to silicon-human comparison under current reliability conditions.

### 19.1 Training-Data Contamination Protocol

Contamination risk is assigned as a (dataset, model) pair, not per dataset alone, because a dataset released after a model's training cutoff cannot be contaminated in that model's weights. Documented cutoffs: GPT-4o mini Oct 2023; Llama 3.2 1B/3B/3.1 8B/3.3 70B Dec 2023; Gemma 2 27B ~Apr 2024; GPT-4o Apr 2024; Phi-4 Jun 2024; LFM 2.5 1.2B and GPT-5 TBD (confirmed before pilot). Against these cutoffs, seven of eight benchmark datasets (AIID 2018, Race IAT instrument ~2002, ANES ongoing, GSS ongoing, ESS rounds 1–11 from 2003, WVS Wave 7 2022, Moral Machine 2018) are Tier 3 — high-risk for all models — because their item text was publicly indexed well before every model's cutoff. Psych-101/Centaur (April 2025) is the single naturally clean dataset (Tier 0) for nine of ten models, requiring no probe-based filtering. Tier assignments are locked in `src/data/sources_manifest.json` before generation; GPT-5 and LFM cutoff confirmations are logged as deviations if they reclassify Psych-101.

**Item-level scoring.** For each (item, model) pair in Tier 2–3 cells, two probes are run per model using token log-probabilities (open-weights models directly; closed-source models via a matched open-weights proxy): (a) Min-K% probability probe (K = 20%; Shi et al., 2024) — anomalously high probability on the least-likely tokens flags memorization; (b) shuffled-response perplexity ratio — a ratio > 1.5 (original vs. shuffled token ordering) is a positive indicator. Each pair receives a contamination score (0–1); scores ≥ 0.5 are flagged. Items flagged for ≥ 5 of 10 models are classified as broadly contaminated and excluded from all clean-only analyses.

**Design-variable interaction test.** Five design variables most likely to modulate memorization are tested for a contamination × design-variable interaction in a supplementary OLS model controlling for dataset-family and outcome-mode fixed effects: (1) conditioning depth, (2) prompt framing, (3) few-shot exemplar inclusion, (4) model capability tier (MMLU ≥ 0.82 vs. < 0.82), and (5) output constraint strategy. A significant positive interaction indicates that a feature's SHFS benefit is inflated in high-contamination conditions; those features are flagged in the main text. Familywise error rate controlled with Holm-Bonferroni across the five tests.

**Corrected analyses.** Four supplementary re-runs are reported: (a) *Psych-101 natural holdout* — primary ML analysis restricted to Psych-101/Centaur cells, which are probe-free Tier 0 for nine models and serve as the highest-confidence clean validation; (b) *probe-based clean-only re-run* — all datasets, restricted to non-flagged (item, model) pairs; (c) *inverse-contamination-probability WLS* — (1 − contamination score) as case weight, preserving power while downweighting flagged pairs; (d) *early- vs. late-cutoff model comparison* — models grouped by cutoff (Oct–Dec 2023 vs. Apr–Jun 2024) to test whether capability–fidelity relationships conflate genuine capability with training-data recency on Tier 3 datasets. If the top-5 feature rankings from analysis (a) diverge from full-data rankings by > 2 positions for any feature, that feature's main-text conclusion is flagged with an explicit contamination caveat. Full results reported in Supplementary Tables C1–C4 and Figures C1–C2.

## 20. Ethics, Privacy, and Governance

This study uses existing public or public-use human datasets. No new human participants will be recruited. The main ethical risks are re-identification, inappropriate use of sensitive attributes, misleading claims about human validity, and downstream misuse of synthetic simulators.

Safeguards:

1. Direct identifiers will not be included in prompts or generated datasets.
2. Rare or high-risk attribute combinations will be coarsened or omitted.
3. Sensitive variables will be used only when permitted by dataset terms and scientifically necessary.
4. Project Implicit data-use restrictions, including non-commercial research use and no re-identification, will be followed.
5. The study will not release row-level synthetic data that could be mistaken for real individuals without clear labeling and documentation.
6. The final protocol will explicitly state that high fidelity on benchmark datasets does not imply ethical permissibility for manipulative, deceptive, or high-stakes deployment.
7. The study will distinguish methodological validation from authorization to replace human evidence in policy, clinical, legal, or electoral settings.
8. **Training-data contamination disclosure.** Several benchmark datasets are publicly available and may have appeared in LLM pre-training corpora. This does not invalidate the study's design-choice comparisons (contamination affects all configurations for a given model equally), but it means that absolute SHFS values may overstate generalizable simulation fidelity. All published results will clearly note this risk and report the contamination-sensitivity analysis (§19, item 22).
9. **MMLU as capability proxy.** MMLU is used as a continuous model-capability covariate because it is consistently documented across providers. However, models with identical MMLU scores may differ substantially on social-science-relevant tasks (e.g., theory-of-mind, cultural knowledge, value alignment). MMLU-related findings will be described as estimates of the capability–fidelity relationship along the MMLU dimension specifically, with a limitation note that other capability dimensions (instruction-following, calibration, cultural competence) are not independently captured.

## 21. Reproducibility Plan

The study will preserve:

1. Ontology version and generated configuration files.
2. Dataset preprocessing manifests.
3. Prompt templates and rendered prompt hashes.
4. OpenRouter model IDs, canonical slugs where available, and response metadata.
5. Random seeds for human-data splitting, configuration sampling, and model fitting.
6. Raw LLM outputs when license-compatible.
7. Parsed silicon responses.
8. Metric computation scripts.
9. ML training and validation splits.
10. Final protocol-generation evidence tables.

Any change after preregistration that affects sampling, datasets, metrics, model selection, exclusion rules, or primary analyses will be logged in `src/preregistration/deviations.md` with date, stage, rationale, and expected impact.

## 22. Stopping Rules

The pilot stops after all 40 pilot design cells per included pilot dataset task are completed or after unrecoverable API/data-use failure.

The full generation loop stops when one of the following occurs:

1. The target number of valid configuration-dataset-task cells is reached.
2. The preregistered budget ceiling is reached.
3. API or license conditions prevent further valid generation.
4. A critical validity defect is discovered and logged before continuing.

Stopping for cost or API failure will not be based on observed SHFS performance.

## 23. Reporting Plan

The final manuscript will report:

1. The ontology and sampling logic.
2. Dataset inclusion/exclusion decisions.
3. Pilot outcomes and any preregistered deviations.
4. Full configuration sampling summary.
5. Primary SHFS results by dataset and configuration family.
6. OLS coefficients and partial R-squared.
7. XGBoost predictive performance and SHAP feature importance.
8. Agreement and disagreement between linear and nonlinear explanations.
9. Protocol derivation table and final protocol.
10. Held-out validation results.
11. Ethics, limits, and misuse constraints.

The protocol will be presented as both prose and a structured checklist/decision tree so that researchers and companies can apply it to future LLM-based simulation studies.

## 24. References and Source Verification

Dataset, model-source, and DOI checks were performed on 2026-04-25. Raw-source staging notes are stored in `src/data/README.md`, and machine-readable source status is stored in `src/data/sources_manifest.json`. Final dataset inclusion will additionally depend on license review, exact file availability, and task-level preprocessing feasibility at execution time.

### 24.1 Dataset and Model Sources

| Source | Verification status on 2026-04-25 | DOI or persistent reference |
| --- | --- | --- |
| AIID OSF project | OSF wiki and data component checked; confirmatory subset downloaded | OSF project: https://osf.io/pcjwf/; no dataset DOI identified in source metadata |
| Project Implicit Demo Website Datasets | OSF wiki checked; Race IAT 2025 archive and codebooks downloaded | Race IAT data paper DOI: `10.5334/jopd.ac`; broader PI demo preprint DOI: `10.31234/osf.io/pdu9a` |
| ANES Time Series Cumulative File | Official data page checked; current cumulative codebook downloaded; raw data requires manual retrieval | Official source: https://electionstudies.org/data-center/anes-time-series-cumulative-data-file/; no DOI identified |
| General Social Survey | Official GSS/NORC access page checked; 2024 codebook downloaded; raw extract requires manual retrieval | Official source: https://gss.norc.org/content/norc/us/en/gss/get-the-data.html; no current dataset DOI identified |
| European Social Survey merged Round 1-11 data | Zenodo metadata downloaded; raw `.dta` direct curl returned HTTP 403 and requires browser download | DOI: `10.5281/zenodo.12799641` |
| World Values Survey | Official documentation page checked; raw data requires WVSA-mediated/manual retrieval | WVS Wave 7 dataset DOI listed by WVS: `10.14281/18241.17` |
| Moral Machine | Nature article and OSF data files checked; documentation and small auxiliary files downloaded; large response archives deferred | DOI: `10.1038/s41586-018-0637-6` |
| Psych-101 / Centaur | Nature article and Hugging Face dataset card checked; dataset card downloaded; large files deferred | DOI: `10.1038/s41586-025-09215-4` |
| LM Market Cap benchmark table | Used for higher-capability pilot MMLU anchors; values frozen in `src/data/raw/model_benchmarks/mmlu_pilot_model_mapping.csv` | Source: https://lmmarketcap.com/benchmarks; no DOI |
| Meta Llama 3.2 model card | Used for MMLU anchors at targets 0.49 and 0.63 | Source: https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct; no DOI |
| Liquid AI LFM 2.5 model documentation | Used for lowest MMLU pilot anchor (target 0.35); MMLU TBD — must be confirmed from published Liquid AI benchmarks before pilot execution | Source: https://www.liquid.ai/liquid-foundation-models; no DOI |
| OpenRouter API and rankings | API availability checked for all ten pilot model IDs via `/api/v1/models` endpoint on 2026-04-25; all ten IDs confirmed present in the model list | Sources: https://openrouter.ai/rankings and https://openrouter.ai/docs/api-reference/list-endpoints-for-a-model; no DOI |

### 24.2 Reference List for Cited Datasets and Articles

1. Hussey, I., Hughes, S., & Nosek, B. A. (2018). The implicit and explicit Attitudes, Identities, and Individual Differences (AIID) Dataset. Open Science Framework. https://osf.io/pcjwf/
2. Xu, K., Nosek, B. A., & Greenwald, A. G. (2014). Psychology data from the Race Implicit Association Test on the Project Implicit Demo website. Journal of Open Psychology Data, 2(1), e3. https://doi.org/10.5334/jopd.ac
3. Xu, K., Nosek, B. A., Greenwald, A. G., et al. (2016). Project Implicit Demo Website Datasets. PsyArXiv. https://doi.org/10.31234/osf.io/pdu9a
4. American National Election Studies. (2026). ANES Time Series Cumulative Data File, current release February 5, 2026. https://electionstudies.org/data-center/anes-time-series-cumulative-data-file/
5. NORC at the University of Chicago. (2026). General Social Survey data and documentation. https://gss.norc.org/content/norc/us/en/gss/get-the-data.html
6. Mentesoglu Tardivo. (2024). European Social Survey Data Round 1-11 merged. Zenodo. https://doi.org/10.5281/zenodo.12799641
7. World Values Survey Association. (2022). World Values Survey Wave 7 (2017-2022) Cross-National Data-Set, version 3.0.0. https://doi.org/10.14281/18241.17
8. Awad, E., Dsouza, S., Kim, R., Schulz, J., Henrich, J., Shariff, A., Bonnefon, J.-F., & Rahwan, I. (2018). The Moral Machine experiment. Nature, 563, 59-64. https://doi.org/10.1038/s41586-018-0637-6
9. Binz, M., Akata, E., Bethge, M., et al. (2025). A foundation model to predict and capture human cognition. Nature, 644, 1002-1009. https://doi.org/10.1038/s41586-025-09215-4
10. LM Market Cap. (2026). AI benchmark explorer and model benchmark tables. https://lmmarketcap.com/benchmarks
11. OpenRouter. (2026). Rankings and API documentation. https://openrouter.ai/rankings and https://openrouter.ai/docs/api-reference/list-endpoints-for-a-model
12. Meta. (2024). Llama 3.2 1B Instruct model card. https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct
13. Liquid AI. (2025). LFM 2.5 model family documentation. https://www.liquid.ai/liquid-foundation-models (MMLU benchmark values to be confirmed from published model card before pilot execution.)
14. Cameron, A. C., & Miller, D. L. (2015). A practitioner's guide to cluster-robust inference. *Journal of Human Resources*, *50*(2), 317–372. https://doi.org/10.3368/jhr.50.2.317

**Methodological works cited:**

15. Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 785–794. https://doi.org/10.1145/2939672.2939785
16. Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*, *30*, 4765–4774. https://proceedings.neurips.cc/paper_files/paper/2017/hash/8a20a8621978632d76c43dfd28b67767-Abstract.html
17. Lundberg, S. M., Erion, G., Chen, H., DeGrave, A., Prutkin, J. M., Nair, B., Katz, R., Himmelfarb, J., Bansal, N., & Lee, S.-I. (2020). From local explanations to global understanding with explainable AI for trees. *Nature Machine Intelligence*, *2*, 56–67. https://doi.org/10.1038/s42256-019-0138-9
18. Hendrycks, D., Burns, C., Basart, S., Zou, A., Mazeika, M., Song, D., & Steinhardt, J. (2021). Measuring massive multitask language understanding. *International Conference on Learning Representations*. https://arxiv.org/abs/2009.03300
19. Argyle, L. P., Busby, E. C., Fulda, N., Gubler, J. R., Rytting, C., & Wingate, D. (2023). Out of one, many: Using language models to simulate human samples. *Political Analysis*, *31*(3), 337–351. https://doi.org/10.1017/pan.2023.2
20. Bisbee, J., Clinton, J. D., Dorff, C., Kenkel, B., & Larson, J. M. (2024). Synthetic replacements for human survey data? The perils of large language models. *Political Analysis*, *32*(4), 401–416. https://doi.org/10.1017/pan.2024.5
21. Santurkar, S., Durmus, E., Ladhak, F., Lee, C., Liang, P., & Hashimoto, T. (2023). Whose opinions do language models reflect? *Proceedings of the 40th International Conference on Machine Learning*, 29971–30004. https://proceedings.mlr.press/v202/santurkar23a.html
22. Bail, C. A. (2024). Can generative AI improve social science? *Proceedings of the National Academy of Sciences*, *121*(21), e2314021121. https://doi.org/10.1073/pnas.2314021121
23. Tjuatja, L., Chen, V., Wu, T., Talwalkwar, A., & Neubig, G. (2024). Do LLMs exhibit human-like response biases? A case study in survey research. *Transactions of the Association for Computational Linguistics*, *12*, 1011–1026. https://doi.org/10.1162/tacl_a_00685
24. Optuna Development Team. (2019). Optuna: A next-generation hyperparameter optimization framework. *Proceedings of the 25th ACM SIGKDD*, 2623–2631. https://doi.org/10.1145/3292500.3330701
25. Shi, W., Ajith, A., Xia, M., Huang, Y., Liu, D., Blevins, T., Chen, D., & Zettlemoyer, L. (2024). Detecting pretraining data from the ground up. *International Conference on Learning Representations (ICLR 2024)*. https://arxiv.org/abs/2310.16789
26. Cummins, J. (2025). The threat of analytic flexibility in using large language models to simulate human data. *arXiv preprint* arXiv:2509.13397. https://doi.org/10.48550/arXiv.2509.13397

### 24.3 OpenRouter Key and Model Availability Check

The repository `.env` file was checked locally on 2026-04-25 and contains `OPENROUTER_API_KEY`. The OpenRouter `/api/v1/auth/key` endpoint returned HTTP 200 using that key on 2026-04-25. The OpenRouter `/api/v1/models` endpoint was queried on 2026-04-25 and all ten preregistered pilot model IDs were confirmed present in the model list: `liquid/lfm-2.5-1.2b-instruct:free`, `meta-llama/llama-3.2-1b-instruct`, `meta-llama/llama-3.2-3b-instruct`, `meta-llama/llama-3.1-8b-instruct`, `google/gemma-2-27b-it`, `openai/gpt-4o-mini`, `microsoft/phi-4`, `meta-llama/llama-3.3-70b-instruct`, `openai/gpt-4o`, and `openai/gpt-5`. No key value, key label, account balance, or sensitive account metadata is stored in this preregistration, logs, or data files.
