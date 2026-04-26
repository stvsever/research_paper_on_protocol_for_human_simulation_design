# Synthetic-Human-Behavior Design Ontology

A typed, machine-readable ontology of design choices that researchers and practitioners face when generating LLM-simulated human-behavior data, together with executable tooling that enumerates or randomly samples **eligible** configurations from the combinatorial state space. The artifact underpins a data-driven, multi-dataset empirical study of which design choices explain the most variance in silicon-human fidelity.

---

## Ontology Overview

![Circular radial diagram of the 18-dimension LLM simulation design ontology](figures/ontology_overview_v2.png)

The simulation design space is formalized as 1,149 leaf design choices organized across 18 top-level dimensions and 212 hierarchical groups. Each dimension covers a distinct stage of the simulation pipeline — from research problem formulation and model selection through prompt architecture, contextual conditioning, generation controls, and governance. The inner ring shows the 18 dimensions; the outer ring shows their direct sub-groups. Hard constraints (44 total) encode cross-tree incompatibilities, cardinality rules govern how many choices may be selected per group, and a constraint-aware sampler draws eligible configurations for empirical evaluation. The unconstrained state space exceeds 10³⁰ possible combinations; constraint filtering and cardinality rules reduce this to a tractable eligible set for stratified sampling.

---

## Folder layout

```
src/ontologies/
├── README.md                   # this file
├── ontology.json               # canonical artifact (regenerable)
├── build_ontology.py           # source of truth: a declarative Python builder
├── sample_configurations.py    # CLI to enumerate / sample eligible configs
├── samples/
│   └── eligible_samples.txt    # example output (one config per non-comment row)
└── constructs/
    └── study_constructs.txt    # downstream-study construct list (separate)
```

`build_ontology.py` is the source of truth. Re-run it to regenerate
`ontology.json`:

```bash
python build_ontology.py
```

---

## What the ontology represents

`ontology.json` is structured as four top-level blocks:

| block          | role                                                                      |
| -------------- | ------------------------------------------------------------------------- |
| `meta`         | The vocabularies that make the JSON self-describing (see below).          |
| `dimensions`   | The typed taxonomic tree of design choices (groups + leaves).             |
| `constraints`  | Cross-tree compatibility rules referenced by stable dot-path leaf ids.    |
| `presets`      | Named curated subsets to keep enumeration tractable for testing.          |

### The `meta` block — the algebra of sampling

`meta` defines *how* the tree is meant to be sampled, not just labels:

* **`stages`** — design / calibration / generation / postprocessing /
  evaluation / confirmation / deployment.
* **`variable_roles`** — design / conditioning / outcome / moderator /
  mediator / control / grouping / temporal-index / evaluation /
  infrastructure / ethical.
* **`variable_types`** — binary, nominal, ordinal, categorical, continuous,
  count, proportion, time-to-event, text, graph, sequence, multilabel,
  compositional, distribution, embedding, ranking, free.  Each type carries a
  `levels`, `ordered`, and a list of `analysis` modes it natively supports
  (e.g., `ordinal → [regression, ordinal, multiclass]`).
* **`outcome_modes`** — the legitimate downstream analysis structures a leaf
  can play if used as an *outcome*: `regression`, `binary`, `multiclass`,
  `ordinal`, `multilabel`, `ranking`, `distribution`, `survival`, `graph`,
  `latent_regression`, `hierarchical_mixed`, `embedding`, `text_judged`,
  `sequence_model`.
  * **This is what encodes the user's MMLU example:** the same benchmark
    leaf can appear as `aggregate_score_regression` (a continuous score),
    `raw_response_multiclass` (per-item classification), `latent_factor_score`
    (latent regression), or `hierarchical_mixed_representation` (item-level
    classification nested in person-level regression). The *same dataset*
    therefore generates *different* downstream eligibility constraints
    depending on which representation is selected.
* **`cardinality_modes`** — how children of a group combine:
  `exactly_one`, `at_least_one`, `at_most_k`, `at_least_k`, `exactly_k`,
  `any_subset`, `all_of`. Every group declares one.
* **`relation_types`** — `requires`, `forbids`, `enables`, `mutually_exclusive`,
  `co_recommended`, `calibrates`, `precedes`, `follows`, `modulates`,
  `overrides` — the algebra over leaf/group ids.
* **`constraint_classes`** — `hard`, `soft`, `advisory`, `resource`,
  `validity`, `ethical`, `execution`. Hard constraints filter configurations;
  soft/advisory ones are kept on the side for downstream weighting.
* **`incompatibility_families`** — pre-named recurring conflict patterns
  (e.g., `MULTIAGENT_NEEDS_ORCHESTRATION`,
  `STRUCTURED_PARSING_NEEDS_STRUCTURED_OUTPUT`,
  `MULTIMODAL_STIM_NEEDS_MULTIMODAL_MODEL`, ...) that the cross-tree
  constraints cite.
* **`search_strategies`**, **`objective_structures`**, **`tradeoff_axes`** —
  vocabularies for the downstream optimisation paper (multi-verse / Sobol /
  Pareto / etc.).

Because all of this lives at the top of `ontology.json`, every leaf below
inherits a fully self-describing semantics.

### Dimensions (top-level groups)

```
research_problem_formulation              # why generate silicon data
target_human_system_specification         # who/what is being simulated
human_benchmark_data_design               # the human-data anchor
synthetic_population_specification        # how silicon respondents are built
model_system_selection                    # the LLM(s)
model_adaptation_and_alignment            # zero-shot / SFT / DPO / DM-FT / ...
measure_task_and_stimulus_representation  # instruments + stimuli
contextual_conditioning                   # persona / psych / situational info
prompt_and_instruction_architecture       # how prompts are built
interaction_decomposition_and_orchestration   # call topology + multi-agent
sampling_and_generation_controls          # decoding-time controls
output_representation_and_capture         # output schema / logging
postprocessing_and_data_transformation    # parsing / reweighting / scoring
quality_assurance_and_failure_management  # retries / exclusions / audits
evaluation_and_validation_framework       # metrics / comparators / fairness
robustness_generalization_and_multiverse  # specification curves / Sobol
execution_environment_and_infrastructure  # endpoints / hardware / caching
governance_ethics_and_deployment_constraints   # IRB / disclosure / dual use
```

For manuscript reporting and preregistration summaries, these 18 operational
dimensions can be collapsed without changing the machine-readable ontology into
seven higher-level design families:

| reporting family | ontology dimensions |
| --- | --- |
| Study target and human benchmark | `research_problem_formulation`, `target_human_system_specification`, `human_benchmark_data_design` |
| Synthetic respondent representation | `synthetic_population_specification`, `contextual_conditioning` |
| Model and adaptation choices | `model_system_selection`, `model_adaptation_and_alignment` |
| Task, prompt, and interaction design | `measure_task_and_stimulus_representation`, `prompt_and_instruction_architecture`, `interaction_decomposition_and_orchestration` |
| Generation, capture, and postprocessing | `sampling_and_generation_controls`, `output_representation_and_capture`, `postprocessing_and_data_transformation` |
| Quality assurance and validation | `quality_assurance_and_failure_management`, `evaluation_and_validation_framework`, `robustness_generalization_and_multiverse` |
| Infrastructure and governance | `execution_environment_and_infrastructure`, `governance_ethics_and_deployment_constraints` |

Every group recursively carries a `_meta.cardinality`. Every leaf carries:

| field            | purpose                                                                |
| ---------------- | ----------------------------------------------------------------------- |
| `var_type`       | from `meta.variable_types`                                               |
| `value_space`    | type-specific (continuous range / categorical levels / vector dim / …)   |
| `roles`          | from `meta.variable_roles`                                               |
| `stage`          | from `meta.stages`                                                       |
| `outcome_modes`  | which analysis structures this leaf is legitimate as an outcome under    |
| `requires`       | local "at least one leaf under id X must also be selected"               |
| `forbids`        | local "no leaf under id X may co-occur"                                  |
| `enables`        | softly suggests a co-selection                                           |
| `tags`           | free-form labels (`high_stakes`, `ethical_sensitive`, `meta_factor`, …)   |
| `conventional`   | `True` ⇔ part of the "conventional core" preset                          |
| `cost_class`     | `low` / `medium` / `high` (cost / latency)                                |
| `notes`          | a short prose annotation                                                  |

### The multi-agent subtree

The `interaction_decomposition_and_orchestration` dimension contains a full
`multi_agent_simulation_design` subtree with its own internal cross-product:

* `agent_topology` (single, actor-critic, debate, hierarchical, blackboard,
  market, council, focus-group, interviewer, teacher-student, red-team,
  network-of-peers, …)
* `agent_role_assignment`, `agent_communication_protocol`
* `critic_evaluation_type` (rubric, pairwise, calibration, psychometric,
  self-consistency, retrieval-grounded, debate-judge, learned-reward-model,
  human-in-the-loop, …)
* `iteration_control`:
  * `max_iterations` ∈ {1, 3, 5, 10, unbounded}
  * `convergence_criterion` ∈ {fixed, score-threshold, plateau, KL,
    critic-passes-all, budget-exhausted}
  * `revision_policy` ∈ {full-rewrite, targeted-edits, accept-or-reject,
    debate-then-synthesise}
* `agent_aggregation`, `agent_memory_scope`, `agent_diversity_strategy`,
  `agent_safety_layer`, `agent_cost_control`

Cross-tree constraints (`C012`, `C013`, `C014`, `C027`, `C028`, …) gate the
multi-agent subtree against the rest of the ontology — e.g., non-trivial
topologies require an orchestration manager; actor-critic loops require an
iteration-control block; human-in-the-loop critics require human oversight
governance; unbounded iterations require explicit cost control.

### Constraints

Each constraint has the shape:

```json
{
  "id":        "C012",
  "relation":  "requires",
  "if":        ["...leaf or group dot-id..."],
  "then":      ["...one or more dot-ids..."],
  "rationale": "Non-trivial agent topologies need an orchestration manager.",
  "severity":  "hard",
  "stage":     null
}
```

Triggering semantics:

* `requires`: if any leaf under any `if[i]` is in the config, then at least
  one leaf under some `then[j]` must also be in the config.
* `forbids`: if any leaf under any `if[i]` *and* any leaf under any `then[j]`
  is in the config, the config is invalid.
* `mutually_exclusive`: at most one of the `if` references may have any leaf
  selected.
* `modulates`, `co_recommended`, `advisory`: not enforced by the sampler;
  carried for downstream analysis.

Only `severity: "hard"` constraints filter eligibility. Soft / advisory
constraints survive into the output (`violations` field) for later weighting.

---

## Sampling logic

The CLI walks the tree recursively. At each group it picks children in line
with the group's `cardinality`. Then it expands those choices recursively.
Finally, the resulting set of leaves is checked against `requires` / `forbids`
/ global constraints; invalid configurations are dropped (or kept with a
`violations` annotation if `--include-invalid` is set).

Two sampling modes:

| mode         | behaviour                                                                |
| ------------ | ------------------------------------------------------------------------ |
| `enumerate`  | Lazy ordered cross-product, truncated at each group by `--max-branch`.   |
| `sample`     | True random recursive draw — one configuration per call (default).      |

`enumerate` is useful for small subtrees (e.g., `prompting_only` preset).
`sample` is the practical mode for the full tree.

### Presets

Defined in `ontology.json.presets`:

* `minimal_smoke`     — tiny subset, just for end-to-end testing (≈ 11 leaves)
* `conventional_core` — every leaf marked `conventional=True` across the tree
* `multi_agent_focus` — multi-agent / orchestration / sampling / eval-target
* `evaluation_focus`  — eval framework + benchmark representation + output,
  with required outcome/metric/analysis dependencies included
* `prompting_only`    — prompt + measure/stimulus subtrees

A preset bundles `include_subtrees` + `conventional_only`. CLI flags can
extend or override.

---

## Quickstart

### 1. Build the ontology

```bash
cd src/ontologies
python build_ontology.py
# → ontology.json (~ 975 KB, 1123 leaves, 209 groups, 39 constraints)
```

### 2. Run the smoke test (used to generate `samples/eligible_samples.txt`)

```bash
python sample_configurations.py \
    --preset conventional_core \
    --mode sample \
    --max-samples 100 \
    --scan-limit 20000 \
    --seed 7 \
    --output samples/eligible_samples.txt
```

This is the canonical command. The output file has:

* a `#`-prefixed metadata header (preset, seed, scan/valid counts,
  top-violated constraints)
* one row per eligible configuration, JSON-encoded:
  `{"valid": true, "violations": [...], "n_leaves": N, "leaves": [...]}`

### 3. Other useful invocations

```bash
# Just list every group dot-id (use these as --include-subtree values)
python sample_configurations.py --list-subtrees

# Just list leaves currently in scope under a chosen subtree
python sample_configurations.py \
    --include-subtree interaction_decomposition_and_orchestration.multi_agent_simulation_design \
    --list-leaves

# Multi-agent only, random draws
python sample_configurations.py \
    --preset multi_agent_focus \
    --max-samples 200 --seed 1 \
    --output samples/multi_agent.txt

# Enumeration mode for a small subtree (deterministic, ordered)
python sample_configurations.py \
    --include-subtree sampling_and_generation_controls.temperature_control \
    --include-subtree model_system_selection.model_capability_regime \
    --mode enumerate --max-samples 100

# Constraint coverage report only (no rows written)
python sample_configurations.py \
    --preset conventional_core --max-samples 500 \
    --scan-limit 10000 --report-only

# Exclude an entire subtree
python sample_configurations.py --preset conventional_core \
    --exclude-subtree governance_ethics_and_deployment_constraints \
    --max-samples 50 --output samples/no_governance.txt
```

### 4. Interpreting the report

The summary that the CLI prints (and that lives in the file header)
includes:

* `candidates_scanned` — total draws considered
* `valid_candidates`   — passed all hard constraints
* `valid_rate`         — `valid / scanned`
* `top_violated_constraints` — highest-frequency constraint ids that filtered
  draws. These tell you where the configuration space is densely correlated
  (e.g., `C020` and the `unconditioned_generic_respondent → demo_conditioning`
  forbid co-fire often, because both leaves are conventional).

A *low* valid rate is usually informative — it means the conventional preset
is internally constrained, and a serious empirical run should bias toward
constraint-aware sampling (e.g., constraint-satisfaction search from
`meta.search_strategies`).

---

## CLI reference

```
--ontology PATH              ontology.json path (default: ./ontology.json)
--mode {enumerate,sample}    sample = random draws (default); enumerate = ordered
--seed INT                   RNG seed for sample mode (default: 42)
--max-samples N              stop after N valid configurations (default: 100)
--scan-limit N               hard cap on total candidates scanned (default: 200000)
--max-branch N               per-group branching cap in enumerate mode (default: 8)

--preset NAME                use a named preset from ontology.json.presets
--include-subtree DOT_ID     restrict to leaves under this group/leaf (repeatable)
--exclude-subtree DOT_ID     drop leaves under this group/leaf (repeatable)
--conventional-only          keep only leaves with conventional=True
--tag-filter TAG             keep only leaves with this tag (repeatable)

--output PATH                write rows to this file
--include-invalid            also write configs that violated constraints
--report-only                don't write rows; only print summary
--list-subtrees              print all group dot-ids and exit
--list-leaves                print leaves in current scope and exit
```

---

## Extending the ontology

Edit `build_ontology.py`:

* Add a leaf:
  ```python
  L("my_new_leaf",
    desc="...",
    var_type="ordinal",
    value_space={"levels": [1,2,3], "ordered": True},
    outcome_modes=["ordinal","regression"],
    tags=["my_tag"], conventional=False)
  ```
* Add a group:
  ```python
  G("my_group", [L(...), L(...)],
    desc="...", cardinality="at_least_one", optional=False)
  ```
* Add a cross-tree constraint:
  ```python
  C("C032", "requires",
    if_=["...dot.id..."], then=["...dot.id..."],
    rationale="...", severity="hard")
  ```

Then `python build_ontology.py` → `ontology.json` is regenerated. The sampler
picks up all changes the next time it is run.

---

## Versioning

`ontology_id` and `schema_version` live at the top of `ontology.json`. Bump
`schema_version` if you change the leaf metadata schema or constraint shape;
bump `ontology_id` if you re-baseline the dimension structure.
