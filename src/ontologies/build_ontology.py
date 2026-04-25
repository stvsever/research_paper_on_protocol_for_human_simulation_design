"""Build the canonical ontology.json describing the combinatorial state space of
LLM-based synthetic-human-behavior simulation designs.

The Python module IS the source of truth; ontology.json is a regenerable artifact.
Run:  python build_ontology.py            (writes ontology.json next to this file)

Schema (high-level)
-------------------
{
  "schema_version": str,
  "ontology_id":    str,
  "meta":           dict   # vocabularies + sampling semantics
  "dimensions":     dict   # the typed taxonomic tree (groups + leaves)
  "constraints":    list   # cross-tree compatibility rules
  "presets":        dict   # named curated subsets ("conventional", "minimal", ...)
}

Every NON-leaf carries a `_meta` block defining how children combine
(cardinality, stage, default-selection rules). Every LEAF is a self-contained
configuration atom carrying a typed value-space, role tags, stage, and
*local* compatibility hints. *Global* compatibility lives in `constraints`.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Tiny DSL — all metadata as kwargs, children always passed as a list.
# ---------------------------------------------------------------------------

def G(
    label: str,
    children: list,
    *,
    desc: str = "",
    cardinality: str = "exactly_one",
    k: int | None = None,
    stage: str | list[str] = "design",
    role: str | list[str] = "design_variable",
    optional: bool = False,
    tags: list[str] | None = None,
) -> dict:
    """A non-leaf node. cardinality ∈ {exactly_one, at_least_one, at_most_k,
    at_least_k, exactly_k, any_subset, all_of}."""
    return {
        "_kind": "group",
        "_meta": {
            "label": label,
            "desc": desc,
            "cardinality": cardinality,
            "k": k,
            "stage": stage if isinstance(stage, list) else [stage],
            "role": role if isinstance(role, list) else [role],
            "optional": optional,
            "tags": tags or [],
        },
        "children": {c["_meta"]["label"]: c for c in children},
    }


def L(
    label: str,
    *,
    desc: str = "",
    var_type: str = "categorical",
    value_space: Any = None,
    roles: list[str] | None = None,
    stage: str | list[str] = "design",
    requires: list[str] | None = None,
    forbids: list[str] | None = None,
    enables: list[str] | None = None,
    outcome_modes: list[str] | None = None,
    tags: list[str] | None = None,
    conventional: bool = False,
    cost_class: str = "medium",
    notes: str = "",
) -> dict:
    """A terminal configuration atom."""
    return {
        "_kind": "leaf",
        "_meta": {
            "label": label,
            "desc": desc,
            "var_type": var_type,
            "value_space": value_space,
            "roles": roles or ["design_variable"],
            "stage": stage if isinstance(stage, list) else [stage],
            "requires": requires or [],
            "forbids": forbids or [],
            "enables": enables or [],
            "outcome_modes": outcome_modes or [],
            "tags": tags or [],
            "conventional": conventional,
            "cost_class": cost_class,
            "notes": notes,
        },
    }


def C(cid, relation, *, if_=None, then=None, rationale="", severity="hard", stage=None):
    return {
        "id": cid, "relation": relation,
        "if": if_ or [], "then": then or [],
        "rationale": rationale, "severity": severity, "stage": stage,
    }


# ---------------------------------------------------------------------------
# 1. Meta ontology
# ---------------------------------------------------------------------------
META = {
    "schema_doc": (
        "Every group has _meta.cardinality. Every leaf has _meta.var_type and "
        "_meta.value_space. Sampling = traverse groups respecting cardinality, "
        "draw leaves, then apply `constraints` to filter the cross-product."
    ),
    "stages": {
        "design": "Choices made before any data are generated.",
        "calibration": "Choices made on a held-out alignment subset.",
        "generation": "Choices made at LLM-call time.",
        "postprocessing": "Choices applied to raw model outputs.",
        "evaluation": "Choices about how silicon-vs-human comparison is performed.",
        "confirmation": "Choices made on a locked confirmation set.",
        "deployment": "Choices governing how the artifact is released/used.",
    },
    "variable_roles": {
        "design_variable": "Manipulated by the researcher across configurations.",
        "conditioning_variable": "Information injected into the prompt/persona.",
        "outcome_variable": "Quantity used to score silicon vs human.",
        "moderator_variable": "Hypothesised to change the size/sign of effects.",
        "mediator_variable": "On the causal path between design and outcome.",
        "control_variable": "Held fixed (or balanced) to isolate other effects.",
        "grouping_variable": "Defines comparison strata.",
        "temporal_index_variable": "Indexes wave / occasion / sequence position.",
        "evaluation_variable": "Used only inside the evaluation pipeline.",
        "infrastructure_variable": "Platform/runtime choice with no theoretical content.",
        "ethical_variable": "Constrained by IRB / governance, not freely sampled.",
    },
    "variable_types": {
        "binary":          {"levels": 2, "ordered": False, "analysis": ["classification"]},
        "nominal":         {"levels": ">2", "ordered": False, "analysis": ["multiclass"]},
        "ordinal":         {"levels": ">2", "ordered": True,  "analysis": ["regression","ordinal","multiclass"]},
        "categorical":     {"levels": ">=2","ordered": False, "analysis": ["multiclass","binary"]},
        "continuous":      {"levels": "inf","ordered": True,  "analysis": ["regression"]},
        "count":           {"levels": "N",  "ordered": True,  "analysis": ["regression","poisson"]},
        "proportion":      {"levels": "[0,1]","ordered": True,"analysis": ["regression","beta"]},
        "time_to_event":   {"levels": "R+", "ordered": True,  "analysis": ["survival"]},
        "text":             {"levels": "free","ordered": False,"analysis": ["embedding","topic","llm_judge"]},
        "graph":            {"levels": "structural","ordered": False,"analysis": ["graph_recovery"]},
        "sequence":        {"levels": "ordered_set","ordered": True,"analysis": ["sequence_model"]},
        "multilabel":      {"levels": "subset","ordered": False,"analysis": ["multilabel"]},
        "compositional":   {"levels": "simplex","ordered": False,"analysis": ["dirichlet","clr"]},
        "distribution":    {"levels": "pmf/pdf","ordered": False,"analysis": ["distribution_metric"]},
        "embedding":       {"levels": "R^d", "ordered": False,"analysis": ["regression","cosine"]},
        "ranking":         {"levels": "permutation","ordered": True,"analysis": ["rank_metric"]},
        "free":             {"levels": "any", "ordered": False, "analysis": []},
    },
    "outcome_modes": {
        "regression":           "Continuous scalar (e.g., MMLU score, mean rating).",
        "binary":               "Two-class outcome (yes/no, correct/incorrect).",
        "multiclass":           "K>2 unordered classes (model id, party choice).",
        "ordinal":              "Ordered K-level outcome (Likert, severity).",
        "multilabel":           "Subset of K labels.",
        "ranking":              "Permutation outcome.",
        "distribution":         "Outcome is a distribution (PMF over options).",
        "survival":             "Time-to-event with censoring.",
        "graph":                "Network/graph outcome.",
        "latent_regression":    "A latent score (factor / IRT) as outcome.",
        "hierarchical_mixed":   "Mixed regression+classification at multiple levels.",
        "embedding":            "Vector outcome compared via cosine / MMD.",
        "text_judged":          "Free text scored by an external LLM judge.",
        "sequence_model":       "Sequence outcome modelled with seq2seq / HMM.",
    },
    "analysis_unit_levels": {
        "response": "A single emitted response, token span, class label, or scalar value.",
        "item": "One survey item, task trial, vignette, stimulus, or decision problem.",
        "respondent": "A stable human or silicon respondent across one or more items.",
        "session": "A contiguous interaction block or experimental session.",
        "group": "A demographic, cultural, treatment, or latent subgroup.",
        "dataset_task": "A single benchmark task derived from one human dataset.",
        "configuration": "One ontology-valid simulation design leaf set.",
        "model": "The concrete LLM endpoint used to instantiate a configuration.",
        "replicate": "A repeated generation seed or stochastic replicate.",
    },
    "feature_encoding_strategies": {
        "binary_indicator": "Encode selected leaves as 0/1 features.",
        "one_hot": "Encode nominal levels with a reference category or full-rank contrasts.",
        "ordinal_integer": "Encode ordered levels as monotone integers, with categorical sensitivity check.",
        "continuous_z": "Standardize continuous values using training-set mean and SD only.",
        "bounded_continuous_logit": "Logit-transform bounded proportions after epsilon clipping.",
        "count_log1p": "Use log(1+x) for overdispersed counts when used as predictors.",
        "compositional_ilr": "Use isometric log-ratio coordinates for simplex-valued predictors.",
        "distributional_summary": "Represent distributions by preregistered distances or moments.",
        "embedding_projection": "Represent embeddings by frozen projections or distances, not raw high-dimensional leakage features.",
        "hierarchical_keys": "Retain respondent/item/dataset/configuration keys for grouped splits and clustered errors.",
    },
    "mixed_outcome_resolution_policy": {
        "priority": [
            "raw_human_outcome_definition",
            "ontology_leaf_outcome_modes",
            "analysis_model_structure",
            "metric_family",
            "standardized_SHFS"
        ],
        "rule": (
            "A configuration is analytically valid only when the selected metric family "
            "and analysis model structure share at least one legitimate outcome mode "
            "with the benchmark task. Hierarchical mixed outcomes preserve both lower-level "
            "item/trial information and higher-level respondent/group keys."
        ),
        "hierarchical_index": [
            "dataset_family",
            "dataset_task",
            "human_split",
            "configuration_id",
            "model_id",
            "replicate_id",
            "respondent_id",
            "item_id"
        ],
    },
    "cardinality_modes": {
        "exactly_one":  "Pick exactly one child (mutually exclusive).",
        "at_least_one": "Pick one or more.",
        "at_most_k":    "Pick zero..k.",
        "at_least_k":   "Pick k..all.",
        "exactly_k":    "Pick exactly k.",
        "any_subset":   "Any subset (incl. empty).",
        "all_of":       "All children apply jointly (no choice).",
    },
    "relation_types": {
        "requires":           "A presupposes B; selecting A without B is invalid.",
        "forbids":            "A and B cannot co-occur.",
        "enables":            "A makes B legal (where B was otherwise gated).",
        "mutually_exclusive": "Exactly one of {A,B,...} may be selected.",
        "co_recommended":     "If A then B is strongly suggested (soft).",
        "calibrates":         "B's parameters are tuned by A (procedural link).",
        "precedes":           "A must occur in an earlier stage than B.",
        "follows":            "A must occur in a later stage than B.",
        "modulates":          "A changes the legal value-space of B.",
        "overrides":          "A's selection overrides any B-level choice.",
    },
    "constraint_classes": {
        "hard":      "Configurations violating this are filtered out.",
        "soft":      "Configurations get a penalty / warning but remain.",
        "advisory":  "Informational only.",
        "resource":  "Budget / latency / compute feasibility.",
        "validity":  "Statistical or measurement validity.",
        "ethical":   "IRB / governance.",
        "execution": "Provider / endpoint / hardware feasibility.",
    },
    "incompatibility_families": {
        "REASONING_NEEDS_REASONING_MODEL": "High reasoning effort requires a reasoning-class model.",
        "MEMORY_NEEDS_STATEFUL_TOPOLOGY": "Multi-turn memory needs non-stateless topologies.",
        "JOINT_EVAL_NEEDS_JOINT_GENERATION": "Joint-distribution recovery needs joint generation.",
        "INDIVIDUAL_RECOVERY_NEEDS_IDENTITY": "Person-level recovery needs stable persona id.",
        "DISTRIBUTION_CALIBRATION_NEEDS_BENCHMARK": "Distribution-matching needs a human benchmark.",
        "FULL_COMPLETION_VS_STOCHASTIC_MISSINGNESS": "Full-completion gates conflict with stochastic missingness.",
        "CROSS_WAVE_NEEDS_PERSISTENCE": "Cross-wave consistency needs multi-wave persistent personas.",
        "COUNTERFACTUAL_NEEDS_INTERVENTION": "Counterfactual recovery needs intervention encoding.",
        "GROUP_FAIRNESS_NEEDS_LABELS": "Group-fairness eval needs group labels.",
        "STRUCTURED_PARSING_NEEDS_STRUCTURED_OUTPUT": "Strict parsers need structured outputs.",
        "FINETUNE_NEEDS_OPEN_OR_HOSTED_FT_API": "SFT/PO need fine-tuneable model access.",
        "MULTIAGENT_NEEDS_ORCHESTRATION": "Multi-agent regimes need an orchestration layer.",
        "CRITIC_NEEDS_ITERATION_BUDGET": "Actor-critic loops need a non-zero iteration budget.",
        "TOOL_USE_NEEDS_TOOL_CAPABLE_MODEL": "Tool-mediated orchestration needs tool-using model.",
        "CROSS_CULTURAL_NEEDS_LOCALIZATION": "Cross-cultural eval needs localized wording / norms.",
        "ABSOLUTE_TEMP_VS_DETERMINISM": "Fixed-seed determinism vs provider-managed randomness.",
        "MULTIMODAL_STIM_NEEDS_MULTIMODAL_MODEL": "Image/audio/video stimuli need a multimodal model.",
    },
    "search_strategies": [
        "exhaustive_enumeration", "theory_guided_enumeration", "random_sampling",
        "stratified_sampling", "latin_hypercube", "bayesian_optimization",
        "evolutionary_search", "constraint_satisfaction",
        "multiobjective_pareto", "sequential_experimental_design",
    ],
    "objective_structures": [
        "single_objective", "weighted_sum", "pareto_frontier",
        "lexicographic", "satisficing", "robust_minmax",
    ],
    "tradeoff_axes": [
        "fidelity_cost", "fidelity_latency", "fidelity_diversity",
        "fidelity_robustness", "fidelity_fairness", "fidelity_interpretability",
        "fidelity_safety", "fidelity_reproducibility",
    ],
    "id_path_format": "Stable ids = dot-paths of slugified labels; constraints reference these.",
    "presets_doc": "Named curated subsets to keep enumeration tractable.",
}


# ---------------------------------------------------------------------------
# Reusable value-space templates
# ---------------------------------------------------------------------------
LIKERT_5 = {"levels": [1, 2, 3, 4, 5], "ordered": True}
LIKERT_7 = {"levels": [1, 2, 3, 4, 5, 6, 7], "ordered": True}
PROB_01  = {"min": 0.0, "max": 1.0, "ordered": True}
TEMP_RNG = {"min": 0.0, "max": 2.0, "ordered": True, "default": 1.0}
TOPP_RNG = {"min": 0.0, "max": 1.0, "ordered": True, "default": 1.0}
TOPK_RNG = {"min": 0,   "max": 200, "ordered": True}


# ---------------------------------------------------------------------------
# 2.1 Research Problem Formulation
# ---------------------------------------------------------------------------
RESEARCH_PROBLEM = G("research_problem_formulation", [
    G("intended_scientific_function", [
        L("descriptive_individual_pointwise",
          desc="Reproduce a specific person's specific responses.",
          var_type="categorical",
          outcome_modes=["binary","multiclass","ordinal","regression"],
          tags=["individual_level","high_difficulty"], conventional=True,
          requires=["synthetic_population_specification.persona_identity_structure.stable_synthetic_identities"]),
        L("descriptive_individual_ranking",
          desc="Reproduce within-person ordinal rankings.",
          var_type="ranking", outcome_modes=["ranking"],
          tags=["individual_level"], conventional=True),
        L("descriptive_individual_pattern",
          desc="Reproduce within-person response patterns / profiles.",
          var_type="sequence", outcome_modes=["embedding","graph"],
          tags=["individual_level"]),
        L("descriptive_marginal_distribution",
          desc="Match population-level marginals.",
          var_type="distribution", outcome_modes=["distribution"], conventional=True),
        L("descriptive_joint_distribution",
          desc="Match cross-variable joint distributions.",
          var_type="distribution", outcome_modes=["distribution","graph"]),
        L("descriptive_conditional_distribution",
          var_type="distribution", outcome_modes=["distribution","regression"]),
        L("descriptive_temporal_distribution",
          var_type="sequence", outcome_modes=["distribution","survival"]),
        L("predictive_design_piloting", conventional=True),
        L("predictive_hypothesis_prioritization",
          var_type="ranking", outcome_modes=["ranking"]),
        L("predictive_power_screening",
          var_type="continuous", outcome_modes=["regression"]),
        L("predictive_intervention_pretesting"),
        L("measurement_item_screening"),
        L("measurement_scale_prototyping"),
        L("measurement_response_format_stress", var_type="ordinal"),
        L("decision_policy_simulation",     tags=["high_stakes"]),
        L("decision_market_simulation",     tags=["high_stakes"]),
        L("decision_clinical_pathway",      tags=["high_stakes","ethical_sensitive"]),
        L("decision_educational_assessment"),
    ], desc="Primary epistemic purpose.", cardinality="at_least_one"),

    G("target_human_output_type", [
        L("survey_binary",          var_type="binary",  outcome_modes=["binary"], conventional=True),
        L("survey_likert_ordinal",  var_type="ordinal", value_space=LIKERT_5, outcome_modes=["ordinal","regression"], conventional=True),
        L("survey_likert_7",        var_type="ordinal", value_space=LIKERT_7, outcome_modes=["ordinal","regression"]),
        L("survey_continuous",      var_type="continuous", outcome_modes=["regression"]),
        L("survey_forced_choice",   var_type="categorical", outcome_modes=["multiclass","binary"]),
        L("survey_multi_response",  var_type="multilabel", outcome_modes=["multilabel"]),
        L("text_short_justification", var_type="text", outcome_modes=["text_judged","embedding"]),
        L("text_narrative",          var_type="text", outcome_modes=["text_judged","embedding"]),
        L("text_explanation",        var_type="text", outcome_modes=["text_judged"]),
        L("text_conversational_turn",var_type="text", outcome_modes=["text_judged","embedding"]),
        L("behavior_one_shot_choice",  var_type="categorical", outcome_modes=["binary","multiclass"]),
        L("behavior_sequential_choice",var_type="sequence",   outcome_modes=["sequence_model"]),
        L("behavior_strategic_move",   var_type="categorical", outcome_modes=["multiclass"]),
        L("behavior_resource_allocation", var_type="compositional", outcome_modes=["regression","distribution"]),
        L("social_dyadic_negotiation", var_type="text",       outcome_modes=["text_judged"]),
        L("social_group_contribution", var_type="text",       outcome_modes=["text_judged"]),
        L("social_post",               var_type="text",       outcome_modes=["text_judged","embedding"]),
        L("social_reply_behavior",     var_type="categorical",outcome_modes=["binary","multiclass"]),
        L("latent_trait_estimate",     var_type="continuous", outcome_modes=["latent_regression","regression"]),
        L("latent_preference_score",   var_type="continuous", outcome_modes=["latent_regression"]),
        L("latent_ideology_score",     var_type="continuous", outcome_modes=["latent_regression"]),
        L("latent_risk_tolerance",     var_type="continuous", outcome_modes=["latent_regression"]),
    ], cardinality="at_least_one"),

    G("target_inference_unit", [
        L("item_level",        conventional=True),
        L("scale_level",       var_type="continuous", conventional=True),
        L("session_level"),
        L("participant_level", conventional=True),
        L("dyad_level"),
        L("group_level"),
        L("population_level",  var_type="distribution", conventional=True),
        L("cross_cultural_level", var_type="distribution"),
    ], cardinality="at_least_one"),

    G("causal_ambition", [
        L("descriptive_fidelity",       conventional=True),
        L("associational_fidelity",     conventional=True),
        L("intervention_effect_recovery", tags=["high_difficulty"]),
        L("mechanism_approximation",     tags=["high_difficulty"]),
        L("counterfactual_approximation", tags=["high_difficulty"]),
        L("policy_extrapolation",        tags=["high_stakes","high_difficulty"]),
    ], cardinality="exactly_one"),

    G("time_structure", [
        L("static_snapshot",          conventional=True),
        L("repeated_cross_section"),
        L("panel_sequence"),
        L("event_triggered_sequence"),
        L("longitudinal_trajectory"),
        L("multi_wave_intervention"),
    ], cardinality="exactly_one"),

    G("domain_scope", [
        G("psychology", [
            L("social_psychology", conventional=True),
            L("personality_psychology", conventional=True),
            L("clinical_psychology", tags=["ethical_sensitive"]),
            L("cognitive_psychology"),
            L("developmental_psychology"),
            L("health_psychology"),
            L("organizational_psychology"),
        ], cardinality="any_subset"),
        G("economics", [
            L("behavioral_economics", conventional=True),
            L("experimental_economics"),
            L("labor_economics"),
        ], cardinality="any_subset"),
        G("political_science", [
            L("public_opinion", conventional=True),
            L("electoral_behavior"),
            L("political_communication"),
        ], cardinality="any_subset"),
        G("sociology", [
            L("identity_processes"),
            L("norm_compliance"),
            L("network_sociology"),
        ], cardinality="any_subset"),
        G("marketing", [
            L("brand_preference"),
            L("purchase_intention"),
            L("ad_response"),
        ], cardinality="any_subset"),
        G("education", [
            L("assessment_response"),
            L("learning_strategy_choice"),
        ], cardinality="any_subset"),
        G("public_health", [
            L("risk_perception"),
            L("health_behavior"),
            L("vaccination_attitudes"),
        ], cardinality="any_subset"),
        G("hci", [
            L("user_satisfaction"),
            L("interaction_choice"),
        ], cardinality="any_subset"),
    ], cardinality="at_least_one"),
], desc="Why is silicon data being generated and what counts as success?",
   cardinality="all_of")


# ---------------------------------------------------------------------------
# 2.2 Target Human System
# ---------------------------------------------------------------------------
TARGET_SYSTEM = G("target_human_system_specification", [
    G("population_scope", [
        L("general_population", conventional=True),
        L("nationally_representative_sample", conventional=True),
        L("convenience_sample"),
        L("student_sample"),
        L("clinical_sample", tags=["ethical_sensitive"]),
        L("expert_population"),
        L("hard_to_reach_population", tags=["ethical_sensitive"]),
        L("vulnerable_population", tags=["ethical_sensitive","high_stakes"]),
        L("cross_national_population"),
        L("synthetic_only_population", tags=["no_human_anchor"]),
    ], cardinality="exactly_one"),

    G("representation_granularity", [
        L("unconditioned_generic_respondent", conventional=True,
          forbids=["contextual_conditioning.persona_demographic_conditioning"]),
        L("group_level_persona", conventional=True),
        L("individual_level_persona", conventional=True),
        L("household_level_persona"),
        L("organization_level_actor"),
        L("multi_agent_society"),
    ], cardinality="exactly_one"),

    G("human_heterogeneity_model", [
        L("homogeneous_population_assumption", conventional=True),
        L("stratified_heterogeneity", conventional=True),
        L("latent_class_heterogeneity"),
        L("continuous_trait_heterogeneity"),
        L("network_structured_heterogeneity"),
        L("context_dependent_heterogeneity"),
    ], cardinality="exactly_one"),

    G("behavioral_regime", [
        L("attitudinal_responding", conventional=True),
        L("normative_judgment"),
        L("affective_appraisal"),
        L("choice_under_risk"),
        L("strategic_interaction"),
        L("memory_based_recall"),
        L("moral_evaluation"),
        L("social_perception"),
        L("consumer_preference"),
        L("information_seeking"),
        L("self_disclosure"),
    ], cardinality="at_least_one"),

    G("response_process_assumption", [
        L("direct_response_emulation", conventional=True),
        L("deliberative_reasoning_emulation"),
        L("heuristic_based_emulation"),
        L("dual_process_emulation"),
        L("role_conditioned_emulation"),
        L("experience_sampling_emulation"),
        L("constructive_response_emulation"),
    ], cardinality="exactly_one"),
], cardinality="all_of")


# ---------------------------------------------------------------------------
# 2.3 Human Benchmark Data Design
# ---------------------------------------------------------------------------
BENCHMARK = G("human_benchmark_data_design", [
    G("benchmark_source_type", [
        L("experimental_dataset", conventional=True),
        L("survey_dataset", conventional=True),
        L("panel_dataset"),
        L("administrative_dataset"),
        L("observational_behavioral_log"),
        L("controlled_lab_task_dataset"),
        L("field_experiment_dataset"),
        L("published_summary_statistics", tags=["aggregate_only"]),
        L("public_psychometric_repository", tags=["public"]),
        L("none_unsupervised_simulation",
          desc="No human anchor; only internal coherence checks possible.",
          tags=["no_human_anchor"],
          forbids=["evaluation_and_validation_framework.evaluation_target.individual_ranking_recovery",
                   "evaluation_and_validation_framework.evaluation_target.calibration_recovery"]),
    ], cardinality="at_least_one"),

    G("benchmark_access_regime", [
        L("internal_primary_dataset"),
        L("public_dataset", conventional=True),
        L("licensed_dataset"),
        L("synthetic_benchmark_from_human_data"),
    ], cardinality="exactly_one"),

    G("benchmark_quality_criteria", [
        L("adequate_sample_size", var_type="binary"),
        L("measurement_reliability", var_type="continuous", value_space=PROB_01),
        L("construct_validity", var_type="ordinal"),
        L("sampling_coverage", var_type="ordinal"),
        L("temporal_relevance", var_type="ordinal"),
        L("context_match", var_type="ordinal"),
        L("missingness_acceptability", var_type="proportion"),
        L("annotation_quality", var_type="ordinal"),
        L("preregistration_present", var_type="binary"),
    ], cardinality="any_subset"),

    G("benchmark_split_strategy", [
        L("no_split"),
        L("calibration_confirmation_split", conventional=True),
        L("train_validation_test_split"),
        L("k_fold_cross_validation", value_space={"k": [3, 5, 10]}),
        L("nested_cross_validation"),
        L("leave_one_study_out"),
        L("leave_one_population_out"),
        L("leave_one_subject_out"),
        L("temporal_holdout_split"),
        L("group_kfold_by_cluster"),
    ], cardinality="exactly_one"),

    G("benchmark_alignment_unit", [
        L("exact_item_match", conventional=True),
        L("construct_level_match"),
        L("scenario_level_match"),
        L("task_level_match"),
        L("outcome_level_match"),
        L("crosswalk_mapped_match"),
    ], cardinality="exactly_one"),

    G("benchmark_preprocessing", [
        L("raw_responses_retained", conventional=True),
        L("reverse_scoring_applied"),
        L("scale_aggregation_applied"),
        L("missing_data_imputed"),
        L("outliers_winsorized"),
        L("survey_weights_applied"),
        L("category_collapsing_applied"),
        L("text_normalization_applied"),
        L("attention_check_screening"),
        L("careless_responding_screening"),
        L("duplicate_respondent_filtering"),
    ], cardinality="any_subset"),

    # User's MMLU example: same dataset can be score (regression) or class (multiclass)
    G("benchmark_representation_mode", [
        L("raw_response_multiclass",
          var_type="categorical", outcome_modes=["multiclass","binary"], conventional=True),
        L("raw_response_ordinal",
          var_type="ordinal", outcome_modes=["ordinal","regression"], conventional=True),
        L("aggregate_score_regression",
          var_type="continuous", outcome_modes=["regression"], conventional=True,
          notes="E.g., total MMLU accuracy as a continuous outcome."),
        L("latent_factor_score",
          var_type="continuous", outcome_modes=["latent_regression"]),
        L("irt_theta",
          var_type="continuous", outcome_modes=["latent_regression"]),
        L("response_distribution_pmf",
          var_type="distribution", outcome_modes=["distribution"]),
        L("ranking_within_person",
          var_type="ranking", outcome_modes=["ranking"]),
        L("model_or_provider_id_as_class",
          var_type="nominal", outcome_modes=["multiclass"],
          notes="Models/providers as discrete classes (e.g., for ablation factor).",
          tags=["meta_factor"]),
        L("text_response_for_judge",
          var_type="text", outcome_modes=["text_judged","embedding"]),
        L("hierarchical_mixed_representation",
          var_type="sequence", outcome_modes=["hierarchical_mixed"],
          notes="Item-level classification nested in person-level regression."),
    ], desc=("How a benchmark is treated for analysis. Same dataset can be a "
             "score (regression) or a category (multiclass) — different "
             "configurations with different downstream eligibility."),
       cardinality="at_least_one"),
], cardinality="all_of", stage=["design","evaluation"])


# ---------------------------------------------------------------------------
# 2.4 Synthetic Population
# ---------------------------------------------------------------------------
SYNTHETIC_POP = G("synthetic_population_specification", [
    G("population_construction_paradigm", [
        L("direct_persona_enumeration", conventional=True),
        L("stratified_persona_sampling", conventional=True),
        L("distribution_based_persona_sampling"),
        L("archetype_mixture_construction"),
        L("case_based_reconstruction"),
        L("agent_population_initialization"),
        L("digital_twin_reconstruction", tags=["ethical_sensitive"]),
    ], cardinality="exactly_one"),

    G("synthetic_sample_size_strategy", [
        L("human_matched_sample_size", conventional=True),
        L("oversampled_synthetic_population"),
        L("fixed_budget_sample_size"),
        L("precision_targeted_sample_size", var_type="count"),
        L("adaptive_stopping_sample_size"),
        L("power_targeted_sample_size", var_type="count"),
    ], cardinality="exactly_one"),

    G("composition_control", [
        L("naturalistic_composition", conventional=True),
        L("balanced_composition"),
        L("oversampled_minority_composition"),
        L("quota_constrained_composition"),
        L("weighted_composition"),
        L("counterfactual_composition", tags=["intervention"]),
    ], cardinality="exactly_one"),

    G("persona_identity_structure", [
        L("anonymous_respondent_slots", conventional=True),
        L("stable_synthetic_identities"),
        L("reusable_panel_identities"),
        L("session_specific_identities"),
        L("multi_role_identities"),
    ], cardinality="exactly_one"),

    G("persona_attribute_source", [
        L("observed_human_attributes", conventional=True,
          requires=["human_benchmark_data_design.benchmark_source_type"]),
        L("imputed_attributes"),
        L("sampled_from_marginals"),
        L("sampled_from_joint_distribution"),
        L("handcrafted_profiles"),
        L("hybrid_observed_sampled_profiles", conventional=True),
        L("llm_generated_profiles", tags=["self_referential"]),
    ], cardinality="exactly_one"),

    G("persona_persistence", [
        L("one_off_respondent_instantiation", conventional=True),
        L("within_study_stable_respondent"),
        L("cross_study_stable_respondent"),
        L("multi_wave_persistent_respondent"),
    ], cardinality="exactly_one"),

    G("inter_respondent_dependence", [
        L("independent_respondents", conventional=True),
        L("household_clustering"),
        L("peer_network_dependence"),
        L("group_membership_dependence"),
        L("geographic_dependence"),
        L("longitudinal_within_person_dependence"),
    ], cardinality="exactly_one"),
], cardinality="all_of")


# ---------------------------------------------------------------------------
# 2.5 Model System Selection
# ---------------------------------------------------------------------------
MODEL_SYSTEM = G("model_system_selection", [
    G("provider_class", [
        L("proprietary_api_model", conventional=True),
        L("open_weights_model", conventional=True),
        L("local_deployment_model"),
        L("hosted_open_weights_model"),
        L("research_prototype_model"),
    ], cardinality="at_least_one"),

    G("model_family", [
        L("gpt_family", conventional=True),
        L("claude_family", conventional=True),
        L("gemini_family", conventional=True),
        L("llama_family"),
        L("mistral_family"),
        L("deepseek_family"),
        L("qwen_family"),
        L("phi_family"),
        L("yi_family"),
        L("specialized_survey_simulation_model"),
    ], cardinality="at_least_one"),

    G("model_capability_regime", [
        L("general_chat_model", conventional=True),
        L("reasoning_model"),
        L("instruction_tuned_model", conventional=True),
        L("tool_using_model"),
        L("multimodal_model"),
        L("long_context_model"),
        L("code_specialised_model"),
    ], cardinality="any_subset"),

    G("model_scale", [
        L("nano_scale_model"),
        L("mini_scale_model", conventional=True),
        L("mid_scale_model", conventional=True),
        L("frontier_scale_model", conventional=True),
    ], cardinality="exactly_one"),

    G("model_versioning", [
        L("fixed_snapshot_version", conventional=True),
        L("rolling_alias_version"),
        L("date_pinned_version"),
        L("research_checkpoint_version"),
    ], cardinality="exactly_one"),

    G("transparency_regime", [
        L("fully_documented_model"),
        L("partially_documented_model"),
        L("opaque_commercial_model"),
    ], cardinality="exactly_one"),

    G("training_specificity", [
        L("general_purpose_model", conventional=True),
        L("domain_adapted_model"),
        L("task_finetuned_model"),
        L("distribution_aligned_model"),
        L("preference_aligned_model"),
        L("safety_overlaid_model"),
    ], cardinality="exactly_one"),

    G("access_constraints", [
        L("rate_limited_endpoint"),
        L("budget_limited_endpoint"),
        L("region_specific_endpoint"),
        L("institutional_gateway_access"),
        L("offline_batch_access"),
    ], cardinality="any_subset"),

    G("model_as_factor_representation", [
        L("model_not_a_factor", conventional=True),
        L("model_as_nominal_factor",
          var_type="nominal", outcome_modes=["multiclass"], tags=["meta_factor"]),
        L("model_as_ordinal_scale_proxy",
          var_type="ordinal", outcome_modes=["ordinal","regression"]),
        L("model_as_continuous_proxy",
          var_type="continuous", outcome_modes=["regression"],
          notes="E.g., MMLU score as a stand-in for the model identity."),
    ], desc="When the model itself is an experimental factor (for ablation).",
       cardinality="exactly_one"),

    G("latent_performance_benchmark", [
        L("mmlu_not_used_or_unobserved", conventional=True,
          tags=["latent_performance", "mmlu"]),
        L("mmlu_target_49",
          var_type="continuous",
          value_space={"benchmark": "MMLU", "target_accuracy": 0.49, "selection_rule": "nearest_available_model"},
          outcome_modes=["regression"],
          tags=["latent_performance", "mmlu", "pilot_factor"],
          notes="Pilot target: choose the OpenRouter-accessible model closest to 49% MMLU in the frozen benchmark table."),
        L("mmlu_target_63",
          var_type="continuous",
          value_space={"benchmark": "MMLU", "target_accuracy": 0.63, "selection_rule": "nearest_available_model"},
          outcome_modes=["regression"],
          tags=["latent_performance", "mmlu", "pilot_factor"]),
        L("mmlu_target_75",
          var_type="continuous",
          value_space={"benchmark": "MMLU", "target_accuracy": 0.75, "selection_rule": "nearest_available_model"},
          outcome_modes=["regression"],
          tags=["latent_performance", "mmlu", "pilot_factor"]),
        L("mmlu_target_82",
          var_type="continuous",
          value_space={"benchmark": "MMLU", "target_accuracy": 0.82, "selection_rule": "nearest_available_model"},
          outcome_modes=["regression"],
          tags=["latent_performance", "mmlu", "pilot_factor"]),
        L("mmlu_target_93",
          var_type="continuous",
          value_space={"benchmark": "MMLU", "target_accuracy": 0.93, "selection_rule": "nearest_available_model",
                       "candidate_model": "openai/gpt-5", "documented_mmlu": 0.930},
          outcome_modes=["regression"],
          tags=["latent_performance", "mmlu", "pilot_factor"],
          cost_class="high"),
        L("mmlu_target_35",
          var_type="continuous",
          value_space={"benchmark": "MMLU", "target_accuracy": 0.35, "selection_rule": "nearest_available_model",
                       "candidate_model": "liquid/lfm-2.5-1.2b-instruct:free", "mmlu_status": "TBD_confirm_before_pilot"},
          outcome_modes=["regression"],
          tags=["latent_performance", "mmlu", "pilot_factor"],
          cost_class="low",
          notes="Lowest pilot anchor. MMLU TBD from Liquid AI model card; fallback to mmlu_target_49 if no model with MMLU ≤ 0.43 available."),
        L("mmlu_target_73",
          var_type="continuous",
          value_space={"benchmark": "MMLU", "target_accuracy": 0.73, "selection_rule": "nearest_available_model",
                       "candidate_model": "meta-llama/llama-3.1-8b-instruct", "documented_mmlu": 0.730},
          outcome_modes=["regression"],
          tags=["latent_performance", "mmlu", "pilot_factor"],
          cost_class="low"),
        L("mmlu_target_85",
          var_type="continuous",
          value_space={"benchmark": "MMLU", "target_accuracy": 0.85, "selection_rule": "nearest_available_model",
                       "candidate_model": "microsoft/phi-4", "documented_mmlu": 0.848},
          outcome_modes=["regression"],
          tags=["latent_performance", "mmlu", "pilot_factor"],
          cost_class="medium"),
        L("mmlu_target_86",
          var_type="continuous",
          value_space={"benchmark": "MMLU", "target_accuracy": 0.86, "selection_rule": "nearest_available_model",
                       "candidate_model": "meta-llama/llama-3.3-70b-instruct", "documented_mmlu": 0.860},
          outcome_modes=["regression"],
          tags=["latent_performance", "mmlu", "pilot_factor"],
          cost_class="medium"),
        L("mmlu_target_88",
          var_type="continuous",
          value_space={"benchmark": "MMLU", "target_accuracy": 0.88, "selection_rule": "nearest_available_model",
                       "candidate_model": "openai/gpt-4o", "documented_mmlu": 0.887},
          outcome_modes=["regression"],
          tags=["latent_performance", "mmlu", "pilot_factor"],
          cost_class="medium"),
    ], desc="Optional latent performance representation used when model identity is encoded by external benchmark score.",
       cardinality="exactly_one"),
], cardinality="all_of")


# ---------------------------------------------------------------------------
# 2.6 Adaptation / Alignment
# ---------------------------------------------------------------------------
ADAPTATION = G("model_adaptation_and_alignment", [
    G("adaptation_strategy", [
        L("zero_shot_use", conventional=True),
        L("few_shot_conditioning", conventional=True),
        L("in_context_calibration"),
        L("supervised_fine_tuning", tags=["finetune"]),
        L("preference_optimization", tags=["finetune"]),
        L("distribution_matching_fine_tuning", tags=["finetune"]),
        L("retrieval_augmented_conditioning"),
        L("lora_adapter_tuning", tags=["finetune"]),
        L("prefix_tuning", tags=["finetune"]),
        L("reinforcement_from_human_feedback", tags=["finetune","high_cost"]),
    ], cardinality="exactly_one"),

    G("fine_tuning_target", [
        L("response_style_alignment"),
        L("marginal_distribution_alignment"),
        L("joint_distribution_alignment"),
        L("treatment_effect_alignment"),
        L("persona_consistency_alignment"),
        L("calibration_alignment"),
        L("refusal_rate_alignment"),
    ], cardinality="any_subset", optional=True),

    G("alignment_data_scope", [
        L("same_domain_same_population_data", conventional=True),
        L("same_domain_different_population_data"),
        L("cross_domain_social_science_data"),
        L("behavioral_trace_data"),
        L("expert_annotated_exemplars"),
        L("simulated_self_distilled_data", tags=["self_referential"]),
    ], cardinality="exactly_one"),

    G("alignment_granularity", [
        L("global_model_alignment"),
        L("population_specific_alignment"),
        L("task_specific_alignment"),
        L("item_family_alignment"),
        L("context_specific_alignment"),
        L("subgroup_specific_alignment"),
    ], cardinality="exactly_one"),

    G("alignment_objective_family", [
        L("next_token_supervision"),
        L("instruction_following_supervision"),
        L("kl_regularised_distribution_matching"),
        L("ordinal_response_calibration"),
        L("contrastive_preference_alignment"),
        L("constrained_decoding_alignment"),
        L("moment_matching_objective"),
    ], cardinality="exactly_one", optional=True),

    G("alignment_governance", [
        L("preregistered_alignment_pipeline"),
        L("exploratory_alignment_pipeline"),
        L("held_out_confirmation_alignment"),
        L("continual_updating_alignment"),
        L("frozen_alignment_baseline"),
    ], cardinality="exactly_one", optional=True),
], cardinality="all_of", stage=["design","calibration"])


# ---------------------------------------------------------------------------
# 2.7 Measure / Stimulus Representation
# ---------------------------------------------------------------------------
MEASURE_REPR = G("measure_task_and_stimulus_representation", [
    G("instrument_representation", [
        G("measurement_family", [
            L("survey_scale_representation", conventional=True),
            L("vignette_battery_representation"),
            L("choice_task_representation"),
            L("game_theoretic_task_representation"),
            L("interview_question_representation"),
            L("behavioral_log_abstraction"),
            L("implicit_measure_representation"),
            L("reaction_time_task_representation"),
        ], cardinality="at_least_one"),
        G("item_structure", [
            L("single_stem_single_response", conventional=True),
            L("matrix_item"),
            L("branching_item"),
            L("scenario_embedded_item"),
            L("comparative_judgment_item"),
            L("open_construct_elicitation_item"),
        ], cardinality="exactly_one"),
        G("response_scale_design", [
            L("binary_scale", var_type="binary", conventional=True),
            L("ternary_scale", var_type="ordinal"),
            L("five_point_likert", var_type="ordinal", value_space=LIKERT_5, conventional=True),
            L("seven_point_likert", var_type="ordinal", value_space=LIKERT_7, conventional=True),
            L("ten_point_rating", var_type="ordinal"),
            L("visual_analog_scale", var_type="continuous"),
            L("forced_ranking_scale", var_type="ranking"),
            L("probability_estimate_scale", var_type="proportion"),
        ], cardinality="exactly_one"),
    ], cardinality="all_of"),

    G("construct_information_packaging", [
        L("no_construct_information", conventional=True),
        L("construct_label_only"),
        L("construct_definition", conventional=True),
        L("theoretical_background_summary"),
        L("psychometric_norms"),
        L("known_base_rate_information"),
        L("population_reference_distribution"),
        L("anti_priming_information"),
    ], cardinality="exactly_one"),

    G("stimulus_material_encoding", [
        L("text_scenario", conventional=True),
        L("conversation_transcript"),
        L("news_article_summary"),
        L("image_description_proxy",
          requires=["model_system_selection.model_capability_regime.multimodal_model"]),
        L("video_summary_proxy"),
        L("audio_summary_proxy"),
        L("experimental_instruction_sheet"),
        L("policy_brief_stimulus"),
        L("native_image_input",
          requires=["model_system_selection.model_capability_regime.multimodal_model"]),
        L("interactive_simulator_stimulus"),
    ], cardinality="any_subset"),

    G("experimental_design_encoding", [
        L("between_subjects_condition_encoding", conventional=True),
        L("within_subjects_condition_encoding"),
        L("factorial_condition_encoding"),
        L("adaptive_intervention_encoding"),
        L("counterfactual_scenario_encoding", tags=["intervention"]),
        L("randomized_order_encoding"),
    ], cardinality="exactly_one"),

    G("reference_frame", [
        L("current_self_reference_frame", conventional=True),
        L("past_self_reference_frame"),
        L("future_self_reference_frame"),
        L("peer_comparison_reference_frame"),
        L("population_typicality_reference_frame"),
        L("normative_ideal_reference_frame"),
    ], cardinality="exactly_one"),

    G("language_and_localization", [
        L("source_language_exact_wording", conventional=True),
        L("translated_wording"),
        L("back_translated_wording"),
        L("locale_specific_adapted_wording"),
        L("register_simplified_wording"),
        L("literacy_adjusted_wording"),
    ], cardinality="exactly_one"),

    G("routing_and_eligibility_logic", [
        L("no_skip_logic", conventional=True),
        L("eligibility_gate"),
        L("conditional_follow_up"),
        L("disqualifying_branch"),
        L("adaptive_probe_branch"),
        L("exposure_contingent_branch"),
    ], cardinality="exactly_one"),
], cardinality="all_of")


# ---------------------------------------------------------------------------
# 2.8 Contextual Conditioning
# ---------------------------------------------------------------------------
CONTEXT = G("contextual_conditioning", [
    G("persona_demographic_conditioning", [
        G("age_specification", [
            L("exact_age", var_type="count", conventional=True),
            L("age_band", var_type="ordinal"),
            L("life_stage", var_type="categorical"),
            L("birth_cohort", var_type="categorical"),
        ], cardinality="at_most_k", k=1),
        G("sex_and_gender_specification", [
            L("sex_assigned_at_birth", var_type="categorical", conventional=True),
            L("gender_identity", var_type="categorical"),
            L("pronoun_set", var_type="categorical"),
            L("gender_role_orientation", var_type="continuous"),
        ], cardinality="any_subset"),
        G("geography_specification", [
            L("country_of_residence", var_type="categorical", conventional=True),
            L("country_of_origin", var_type="categorical"),
            L("region", var_type="categorical"),
            L("urbanicity", var_type="ordinal"),
            L("migration_status", var_type="categorical"),
        ], cardinality="any_subset"),
        G("socioeconomic_position_specification", [
            L("education_level", var_type="ordinal", conventional=True),
            L("household_income", var_type="ordinal"),
            L("occupational_status", var_type="categorical"),
            L("employment_status", var_type="categorical"),
            L("social_class_identification", var_type="ordinal"),
            L("subjective_ses", var_type="ordinal"),
        ], cardinality="any_subset"),
        G("cultural_and_identity_specification", [
            L("race_or_ethnicity", var_type="categorical", tags=["ethical_sensitive"]),
            L("religion", var_type="categorical", tags=["ethical_sensitive"]),
            L("language_background", var_type="categorical"),
            L("national_identity", var_type="categorical"),
            L("community_identification", var_type="categorical"),
        ], cardinality="any_subset"),
        G("political_specification", [
            L("party_identification", var_type="categorical", conventional=True),
            L("ideological_self_placement", var_type="ordinal"),
            L("political_interest", var_type="ordinal"),
            L("political_engagement", var_type="ordinal"),
            L("authoritarianism_score", var_type="continuous"),
            L("populism_attitude", var_type="continuous"),
        ], cardinality="any_subset"),
        G("household_and_family_specification", [
            L("marital_status", var_type="categorical"),
            L("parental_status", var_type="categorical"),
            L("household_composition", var_type="categorical"),
            L("caregiving_status", var_type="categorical"),
        ], cardinality="any_subset"),
        G("health_and_functioning_specification", [
            L("general_health_status", var_type="ordinal"),
            L("disability_status", var_type="categorical", tags=["ethical_sensitive"]),
            L("mental_health_history", var_type="categorical", tags=["ethical_sensitive"]),
            L("neurodivergence_status", var_type="categorical", tags=["ethical_sensitive"]),
            L("chronic_illness_status", var_type="categorical"),
        ], cardinality="any_subset"),
        G("digital_and_media_environment_specification", [
            L("platform_usage_intensity", var_type="ordinal"),
            L("news_consumption_pattern", var_type="categorical"),
            L("technical_literacy", var_type="ordinal"),
            L("device_access", var_type="categorical"),
            L("social_media_diet", var_type="compositional"),
        ], cardinality="any_subset"),
    ], cardinality="any_subset"),

    G("psychological_conditioning", [
        G("stable_traits", [
            L("big_five_profile", var_type="embedding", value_space={"d": 5}),
            L("hexaco_profile", var_type="embedding", value_space={"d": 6}),
            L("need_for_cognition", var_type="continuous"),
            L("risk_preference", var_type="continuous"),
            L("trust_disposition", var_type="continuous"),
            L("self_efficacy", var_type="continuous"),
            L("locus_of_control", var_type="continuous"),
            L("dark_triad_profile", var_type="embedding", value_space={"d": 3}),
        ], cardinality="any_subset"),
        G("motivational_states", [
            L("goal_orientation", var_type="categorical"),
            L("incentive_salience", var_type="continuous"),
            L("social_desirability_concern", var_type="continuous"),
            L("compliance_motivation", var_type="continuous"),
            L("regulatory_focus", var_type="categorical"),
        ], cardinality="any_subset"),
        G("affective_states", [
            L("mood_state", var_type="categorical"),
            L("stress_level", var_type="ordinal"),
            L("arousal_level", var_type="ordinal"),
            L("fatigue_level", var_type="ordinal"),
            L("affect_valence", var_type="continuous"),
            L("affect_arousal", var_type="continuous"),
        ], cardinality="any_subset"),
        G("cognitive_states", [
            L("attention_level", var_type="ordinal"),
            L("working_memory_load", var_type="ordinal"),
            L("uncertainty_state", var_type="continuous"),
            L("time_pressure_state", var_type="ordinal"),
            L("cognitive_load_manipulation", var_type="categorical"),
        ], cardinality="any_subset"),
    ], cardinality="any_subset"),

    G("behavioral_history_conditioning", [
        L("prior_survey_responses", var_type="sequence"),
        L("prior_task_performance", var_type="sequence"),
        L("purchase_history", var_type="sequence"),
        L("voting_history", var_type="sequence"),
        L("clinical_history", var_type="sequence", tags=["ethical_sensitive"]),
        L("media_exposure_history", var_type="sequence"),
        L("interaction_history", var_type="sequence"),
        L("location_trajectory", var_type="sequence", tags=["ethical_sensitive"]),
    ], cardinality="any_subset"),

    G("social_context_conditioning", [
        L("peer_norm_exposure"),
        L("family_norm_exposure"),
        L("institutional_context"),
        L("group_membership_context"),
        L("intergroup_context"),
        L("audience_presence"),
        L("anonymity_condition"),
    ], cardinality="any_subset"),

    G("situational_context_conditioning", [
        L("time_of_day"),
        L("day_of_week"),
        L("season"),
        L("crisis_context"),
        L("economic_context"),
        L("policy_context"),
        L("experimental_condition", conventional=True),
        L("local_event_context"),
    ], cardinality="any_subset"),

    G("information_reduction_strategy", [
        L("no_conditioning",
          forbids=["contextual_conditioning.persona_demographic_conditioning"],
          tags=["conditioning_depth", "pilot_factor"]),
        L("minimal_conditioning",
          tags=["conditioning_depth", "pilot_factor"]),
        L("demographic_core_conditioning", conventional=True,
          tags=["conditioning_depth", "pilot_factor"]),
        L("psychographic_core_conditioning"),
        L("full_observed_conditioning", conventional=True,
          tags=["conditioning_depth", "pilot_factor"]),
        L("reduced_salient_conditioning"),
        L("theoretically_relevant_conditioning"),
        L("data_driven_feature_selected_conditioning"),
    ], cardinality="exactly_one"),
], cardinality="all_of", role="conditioning_variable")


# ---------------------------------------------------------------------------
# 2.9 Prompt / Instruction Architecture
# ---------------------------------------------------------------------------
PROMPT_ARCH = G("prompt_and_instruction_architecture", [
    G("prompt_framing_strategy", [
        L("direct_questionnaire_framing", conventional=True),
        L("persona_role_framing", conventional=True),
        L("interview_framing"),
        L("narrative_profile_framing"),
        L("bullet_attribute_framing"),
        L("scenario_immersion_framing"),
        L("behavioral_task_framing"),
        L("conversational_framing"),
        L("simulated_interviewer_framing"),
    ], cardinality="exactly_one"),

    G("respondent_role_instruction", [
        L("act_as_specific_individual"),
        L("act_as_representative_group_member"),
        L("act_as_probabilistic_draw_from_population", conventional=True),
        L("act_as_stable_reusable_persona"),
        L("act_as_situation_bound_agent"),
    ], cardinality="exactly_one"),

    G("task_framing_emphasis", [
        L("accuracy_emphasis"),
        L("realism_emphasis"),
        L("typicality_emphasis"),
        L("diversity_emphasis"),
        L("uncertainty_awareness_emphasis"),
        L("calibration_emphasis"),
        L("anti_average_emphasis"),
    ], cardinality="any_subset"),

    G("response_generation_perspective", [
        L("first_person_perspective", conventional=True),
        L("third_person_perspective"),
        L("observer_based_prediction"),
        L("self_reflection_simulation"),
    ], cardinality="exactly_one"),

    G("prompt_content_packaging", [
        L("items_only", conventional=True),
        L("items_plus_construct_labels"),
        L("items_plus_definitions"),
        L("items_plus_normative_statistics"),
        L("items_plus_reference_vignettes"),
        L("items_plus_scale_usage_instructions"),
        L("items_plus_response_constraints"),
    ], cardinality="exactly_one"),

    G("item_presentation_regime", [
        L("all_measures_in_single_prompt", conventional=True),
        L("one_measure_per_prompt"),
        L("one_item_per_prompt"),
        L("one_block_per_prompt"),
        L("adaptive_item_routing"),
    ], cardinality="exactly_one"),

    G("ordering_strategy", [
        L("original_human_order", conventional=True),
        L("randomized_order"),
        L("fixed_theoretical_order"),
        L("difficulty_ordered_sequence"),
        L("construct_grouped_sequence"),
        L("counterbalanced_orders"),
    ], cardinality="exactly_one"),

    G("wording_fidelity", [
        L("exact_human_wording", conventional=True),
        L("lightly_standardised_wording"),
        L("simplified_wording"),
        L("expanded_clarified_wording"),
        L("cross_culturally_adapted_wording"),
    ], cardinality="exactly_one"),

    G("prompt_style_attributes", [
        L("formal_register"),
        L("conversational_register"),
        L("neutral_register", conventional=True),
        L("high_precision_register"),
        L("low_ambiguity_register"),
        L("low_cognitive_load_register"),
    ], cardinality="any_subset"),

    G("formatting_choices", [
        L("plain_paragraph_formatting"),
        L("numbered_item_formatting", conventional=True),
        L("markdown_table_formatting"),
        L("json_schema_formatting"),
        L("xml_like_tag_formatting"),
        L("delimited_record_formatting"),
    ], cardinality="exactly_one"),

    G("instruction_specificity", [
        L("minimal_instruction"),
        L("standardised_instruction", conventional=True),
        L("detailed_instruction"),
        L("stepwise_instruction"),
        L("constraint_explicit_instruction"),
    ], cardinality="exactly_one"),

    G("cognitive_guidance", [
        L("no_reasoning_cue", conventional=True,
          desc="No explicit cognitive instruction; model uses its default response mode."),
        L("brief_reflection_cue",
          desc="Prompt model to briefly consider the question before answering."),
        L("deliberate_carefully_cue",
          desc="Instruct deliberative, slow System-2 style reasoning."),
        L("think_like_target_person_cue",
          desc="Explicitly instruct the model to reason as if it were the target persona."),
        L("answer_instinctively_cue",
          desc="Suppress deliberation; elicit gut-level System-1 style responding."),
        L("use_typical_experience_cue",
          desc="Anchor reasoning to typical lived experiences of the target persona."),
        L("zero_shot_chain_of_thought_cue",
          desc="Append 'Let's think step by step' without exemplars (Wei et al., 2022).",
          tags=["chain_of_thought"]),
        L("few_shot_chain_of_thought_cue",
          desc="Provide worked chain-of-thought exemplars before the target question.",
          tags=["chain_of_thought"]),
        L("plan_then_respond_cue",
          desc="Instruct model to outline a reasoning plan before emitting its final response.",
          tags=["chain_of_thought"]),
        L("self_consistency_cue",
          desc="Generate multiple independent reasoning paths; aggregate final answers by majority vote.",
          tags=["chain_of_thought"]),
        L("metacognitive_reflection_cue",
          desc="Prompt the model to assess its own uncertainty and reasoning quality before finalising response.",
          tags=["metacognition"]),
        L("perspective_taking_cue",
          desc="Explicitly prompt consideration of the item from multiple vantage points before selecting a response."),
    ], cardinality="exactly_one"),

    G("bias_management_prompting", [
        L("social_desirability_suppression_instruction"),
        L("stereotype_avoidance_instruction"),
        L("do_not_moralise_instruction"),
        L("human_variability_preservation_instruction"),
        L("do_not_default_to_average_instruction"),
        L("avoid_refusal_instruction"),
    ], cardinality="any_subset"),

    G("uncertainty_prompting", [
        L("deterministic_single_best_response", conventional=True),
        L("response_with_confidence_rating"),
        L("response_distribution_output"),
        L("multiple_plausible_responses"),
        L("range_constrained_response"),
        L("verbal_uncertainty_response"),
    ], cardinality="exactly_one"),

    G("example_provision", [
        L("no_examples", conventional=True),
        L("format_only_example"),
        L("one_worked_example"),
        L("multiple_heterogeneous_examples"),
        L("in_distribution_examples"),
        L("out_of_distribution_warning_example"),
    ], cardinality="exactly_one"),

    G("system_prompt_design", [
        L("no_system_prompt", conventional=True,
          desc="No system prompt; model uses its default behavior."),
        L("generic_assistant_system_prompt", conventional=True,
          desc="Generic helpful-assistant framing with no simulation-specific context."),
        L("survey_researcher_role_system_prompt",
          desc="Positions the model as a survey research instrument tasked with producing human-like responses."),
        L("simulated_human_participant_system_prompt",
          desc="System prompt explicitly tells the model it will simulate a human study participant."),
        L("persona_constrained_system_prompt",
          desc="System prompt carries persona constraints (demographics, traits) that persist across all turns."),
        L("task_aware_domain_expert_system_prompt",
          desc="System prompt injects domain knowledge relevant to the target task or scale."),
        L("confidentiality_and_honesty_system_prompt",
          desc="System prompt includes explicit honesty and candor instruction alongside data-use framing."),
        L("anti_refusal_guardrail_system_prompt",
          desc="System prompt instructs model to comply with all items and suppress refusal behavior."),
        L("format_contract_system_prompt",
          desc="System prompt specifies output schema, format, and length constraints."),
        L("chain_of_thought_scaffold_system_prompt",
          desc="System prompt pre-activates step-by-step reasoning mode.",
          tags=["chain_of_thought"]),
    ], cardinality="at_most_k", k=3,
       desc="Content, role, and scope of the system-level prompt passed before any user turn."),

    G("prompt_template_management", [
        L("single_monolithic_template", conventional=True,
          desc="One static template used for all respondents and items."),
        L("parameterised_template_with_slot_filling", conventional=True,
          desc="Template contains named slots filled programmatically per respondent."),
        L("dynamic_template_assembly",
          desc="Template components assembled at runtime by orchestration logic."),
        L("template_library_with_selection_policy",
          desc="Multiple validated templates; a selection policy rotates or chooses among them."),
        L("persona_conditional_template_branching",
          desc="Template branch chosen conditionally on persona attributes (e.g., language, cultural background)."),
        L("llm_generated_bespoke_template",
          desc="A meta-LLM call generates the item-specific template before the main generation call."),
        L("template_ablation_registry",
          desc="Templates versioned in a registry; ablation studies draw from multiple registered versions."),
    ], cardinality="exactly_one",
       desc="How prompt templates are authored, stored, selected, and parameterised across respondents."),
], cardinality="all_of", stage="generation")


# ---------------------------------------------------------------------------
# 2.10 Interaction Decomposition / Multi-Agent
# ---------------------------------------------------------------------------
INTERACTION = G("interaction_decomposition_and_orchestration", [
    G("call_topology", [
        L("single_call_per_respondent", conventional=True),
        L("single_call_per_measure"),
        L("single_call_per_item"),
        L("single_call_per_session_block"),
        L("multi_turn_dialogue_per_respondent"),
        L("tree_of_calls_workflow"),
        L("graph_of_calls_workflow"),
    ], cardinality="exactly_one"),

    G("multi_call_aggregation_strategy", [
        L("no_replication", conventional=True),
        L("replicate_same_prompt"),
        L("replicate_with_paraphrases"),
        L("replicate_across_models"),
        L("replicate_across_temperatures"),
        L("replicate_across_seeds"),
        L("replicate_across_personas"),
    ], cardinality="exactly_one"),

    G("cross_item_dependency_handling", [
        L("independent_item_generation", conventional=True),
        L("sequentially_conditioned_item_generation"),
        L("memory_carried_item_generation"),
        L("latent_state_carried_item_generation"),
        L("consistency_constrained_item_generation"),
    ], cardinality="exactly_one"),

    G("within_respondent_memory_policy", [
        L("stateless_calls", conventional=True),
        L("session_memory_retention"),
        L("structured_persona_memory"),
        L("summary_memory_compression"),
        L("full_transcript_carryover"),
        L("vector_memory_retrieval"),
    ], cardinality="exactly_one"),

    G("between_respondent_isolation_policy", [
        L("full_isolation", conventional=True),
        L("shared_population_prior"),
        L("shared_calibration_context"),
        L("shared_batch_context"),
    ], cardinality="exactly_one"),

    G("conversation_manager_strategy", [
        L("manual_prompt_chaining", conventional=True),
        L("programmatic_state_machine"),
        L("tool_mediated_orchestration",
          requires=["model_system_selection.model_capability_regime.tool_using_model"]),
        L("agentic_planner_executor_loop"),
        L("graph_compiled_workflow"),
    ], cardinality="exactly_one"),

    G("conditional_branching_strategy", [
        L("no_branching", conventional=True),
        L("skip_logic_branching"),
        L("adaptive_probe_branching"),
        L("refusal_recovery_branching"),
        L("consistency_repair_branching"),
    ], cardinality="exactly_one"),

    # ---- multi-agent subtree -------------------------------------------
    G("multi_agent_simulation_design", [
        G("agent_topology", [
            L("single_agent", conventional=True,
              tags=["critic_actor_absent", "pilot_factor"]),
            L("actor_critic_pair", tags=["actor_critic", "critic_actor_present", "pilot_factor"]),
            L("actor_multi_critic", tags=["actor_critic"]),
            L("debate_two_agents"),
            L("debate_n_agents"),
            L("hierarchical_planner_executor"),
            L("hierarchical_planner_workers"),
            L("blackboard_society"),
            L("market_of_agents"),
            L("council_with_judge"),
            L("simulated_focus_group"),
            L("interviewer_interviewee_pair"),
            L("teacher_student_pair"),
            L("adversarial_red_team_blue_team"),
            L("network_of_peers", desc="Agents on an arbitrary graph topology."),
        ], cardinality="exactly_one"),
        G("agent_role_assignment", [
            L("homogeneous_roles"),
            L("specialised_roles"),
            L("randomly_drawn_roles"),
            L("data_driven_roles"),
        ], cardinality="exactly_one", optional=True),
        G("agent_communication_protocol", [
            L("free_form_natural_language"),
            L("structured_json_messages"),
            L("typed_function_calls"),
            L("blackboard_writes"),
            L("symbolic_proposition_exchange"),
            L("limited_token_budget_messages"),
        ], cardinality="exactly_one", optional=True),
        G("critic_evaluation_type", [
            L("rubric_score_critic"),
            L("preference_pairwise_critic"),
            L("constraint_violation_critic"),
            L("calibration_critic"),
            L("psychometric_consistency_critic"),
            L("self_consistency_critic"),
            L("retrieval_grounded_critic"),
            L("verifier_with_ground_truth"),
            L("debate_judge_critic"),
            L("majority_vote_critic"),
            L("learned_reward_model_critic"),
            L("human_in_the_loop_critic", tags=["high_cost"]),
        ], cardinality="any_subset", optional=True),
        G("iteration_control", [
            G("max_iterations", [
                L("max_iter_1", var_type="count", value_space={"min":1,"max":1}),
                L("max_iter_3", var_type="count", value_space={"min":3,"max":3}, conventional=True),
                L("max_iter_5", var_type="count", value_space={"min":5,"max":5}),
                L("max_iter_10", var_type="count", value_space={"min":10,"max":10}),
                L("max_iter_unbounded", var_type="count"),
            ], cardinality="exactly_one"),
            G("convergence_criterion", [
                L("fixed_iterations"),
                L("score_threshold"),
                L("score_plateau"),
                L("kl_to_prev_response"),
                L("critic_passes_all"),
                L("budget_exhausted"),
            ], cardinality="exactly_one"),
            G("revision_policy", [
                L("full_rewrite_each_iter"),
                L("targeted_edits_each_iter"),
                L("accept_or_reject_each_iter"),
                L("debate_then_synthesise"),
            ], cardinality="exactly_one"),
        ], cardinality="all_of", optional=True),
        G("agent_aggregation", [
            L("final_speaker_wins"),
            L("majority_vote_aggregation"),
            L("weighted_vote_aggregation"),
            L("judge_decision"),
            L("synthesis_summary"),
            L("argmax_critic_score"),
            L("bayesian_belief_pooling"),
        ], cardinality="exactly_one", optional=True),
        G("agent_memory_scope", [
            L("private_per_agent_only"),
            L("shared_scratchpad"),
            L("episodic_per_session"),
            L("semantic_long_term_memory"),
            L("retrieval_indexed_memory"),
        ], cardinality="exactly_one", optional=True),
        G("agent_diversity_strategy", [
            L("identical_agents"),
            L("different_personas_same_model"),
            L("different_models"),
            L("different_decoding_params"),
            L("different_role_prompts"),
            L("different_value_systems"),
        ], cardinality="any_subset", optional=True),
        G("agent_safety_layer", [
            L("guardrail_filter_pre_post"),
            L("content_policy_check"),
            L("self_correcting_revision"),
            L("external_moderator_agent"),
            L("kill_switch_on_runaway_loops"),
        ], cardinality="any_subset", optional=True),
        G("agent_cost_control", [
            L("hard_iteration_cap"),
            L("token_budget_per_agent"),
            L("token_budget_per_session"),
            L("early_stopping_on_agreement"),
            L("hierarchical_routing_to_cheaper_model"),
        ], cardinality="any_subset", optional=True),
    ], cardinality="all_of", optional=True,
       desc="Optional multi-agent layer."),

    G("ensemble_strategy", [
        L("single_model_workflow", conventional=True),
        L("homogeneous_ensemble"),
        L("heterogeneous_ensemble"),
        L("stacked_two_stage_ensemble"),
        L("mixture_of_experts_routing"),
        L("boosted_correction_ensemble"),
    ], cardinality="exactly_one"),

    G("temporal_execution_design", [
        L("one_pass_batch_generation", conventional=True),
        L("incremental_streaming_generation"),
        L("scheduled_multi_wave_generation"),
        L("human_in_the_loop_review_cycle"),
    ], cardinality="exactly_one"),

    G("parallelization_strategy", [
        L("sequential_execution"),
        L("respondent_level_parallelisation", conventional=True),
        L("item_level_parallelisation"),
        L("model_level_parallelisation"),
        L("cluster_distributed_execution"),
    ], cardinality="exactly_one"),
], cardinality="all_of", stage="generation")


# ---------------------------------------------------------------------------
# 2.11 Sampling / Generation Controls
# ---------------------------------------------------------------------------
SAMPLING = G("sampling_and_generation_controls", [
    G("randomness_regime", [
        L("fully_deterministic_decoding"),
        L("low_stochasticity_decoding", conventional=True),
        L("moderate_stochasticity_decoding", conventional=True),
        L("high_stochasticity_decoding"),
        L("adaptive_stochasticity_decoding"),
    ], cardinality="exactly_one"),

    G("temperature_control", [
        L("temp_zero", var_type="continuous", value_space={"value": 0.0}, conventional=True),
        L("temp_low_0_3", var_type="continuous", value_space={"min": 0.0, "max": 0.4}),
        L("temp_medium_0_7", var_type="continuous", value_space={"min": 0.5, "max": 0.9}, conventional=True),
        L("temp_high_1_0", var_type="continuous", value_space={"min": 1.0, "max": 1.5}),
        L("temp_extreme_2_0", var_type="continuous", value_space={"min": 1.5, "max": 2.0}),
        L("temp_per_task_tuned", var_type="continuous", value_space=TEMP_RNG),
        L("temp_per_stage_tuned", var_type="continuous", value_space=TEMP_RNG),
    ], cardinality="exactly_one"),

    G("nucleus_sampling_control", [
        L("no_top_p", conventional=True),
        L("tight_top_p", var_type="continuous", value_space={"min": 0.5, "max": 0.8}),
        L("moderate_top_p", var_type="continuous", value_space={"min": 0.8, "max": 0.95}),
        L("broad_top_p", var_type="continuous", value_space={"min": 0.95, "max": 1.0}),
        L("dynamic_top_p", var_type="continuous", value_space=TOPP_RNG),
    ], cardinality="exactly_one"),

    G("top_k_control", [
        L("no_top_k", conventional=True),
        L("small_top_k", var_type="count", value_space={"min": 1, "max": 10}),
        L("moderate_top_k", var_type="count", value_space={"min": 10, "max": 50}),
        L("large_top_k", var_type="count", value_space={"min": 50, "max": 200}),
        L("adaptive_top_k", var_type="count", value_space=TOPK_RNG),
    ], cardinality="exactly_one"),

    G("reasoning_budget_control", [
        L("no_explicit_reasoning_budget", conventional=True),
        L("low_reasoning_effort"),
        L("medium_reasoning_effort"),
        L("high_reasoning_effort",
          requires=["model_system_selection.model_capability_regime.reasoning_model"]),
        L("task_adaptive_reasoning_effort"),
    ], cardinality="exactly_one"),

    G("length_control", [
        L("fixed_minimal_output_length"),
        L("fixed_moderate_output_length", conventional=True),
        L("free_length_output"),
        L("token_capped_output", var_type="count", value_space={"min": 1, "max": 8192}),
        L("schema_limited_output"),
    ], cardinality="exactly_one"),

    G("diversity_control", [
        L("diversity_via_sampling_only", conventional=True),
        L("diversity_via_persona_variation"),
        L("diversity_via_prompt_paraphrase_variation"),
        L("diversity_via_model_mixture"),
        L("diversity_via_latent_state_sampling"),
        L("diversity_via_explicit_typicality_penalty"),
    ], cardinality="any_subset"),

    G("reproducibility_control", [
        L("fixed_seed", conventional=True),
        L("seed_sweep"),
        L("provider_managed_randomness"),
        L("local_deterministic_replay"),
        L("no_seed_control", tags=["non_reproducible"]),
    ], cardinality="exactly_one"),

    G("termination_control", [
        L("default_stop_behavior", conventional=True),
        L("explicit_stop_tokens"),
        L("json_schema_closure"),
        L("delimiter_based_closure"),
        L("multi_field_termination"),
    ], cardinality="exactly_one"),

    G("safety_filter_interaction", [
        L("standard_safety_setting", conventional=True),
        L("relaxed_research_setting", tags=["governance_required"]),
        L("high_restriction_setting"),
        L("external_moderation_layer"),
    ], cardinality="exactly_one"),

    G("cost_latency_tradeoff", [
        L("latency_minimised_generation"),
        L("cost_minimised_generation"),
        L("quality_maximised_generation", conventional=True),
        L("balanced_utility_generation", conventional=True),
    ], cardinality="exactly_one"),
], cardinality="all_of", stage="generation")


# ---------------------------------------------------------------------------
# 2.12 Output Representation / Capture
# ---------------------------------------------------------------------------
OUTPUT_REPR = G("output_representation_and_capture", [
    G("output_modality", [
        L("scalar_numeric_output", var_type="continuous", outcome_modes=["regression"]),
        L("ordinal_category_output", var_type="ordinal", outcome_modes=["ordinal"], conventional=True),
        L("nominal_category_output", var_type="nominal", outcome_modes=["multiclass"]),
        L("ranked_list_output", var_type="ranking", outcome_modes=["ranking"]),
        L("free_text_output", var_type="text", outcome_modes=["text_judged","embedding"]),
        L("mixed_structured_output", var_type="sequence", outcome_modes=["hierarchical_mixed"]),
        L("probability_vector_output", var_type="distribution", outcome_modes=["distribution"]),
    ], cardinality="exactly_one"),

    G("structured_schema_design", [
        L("single_field_schema", conventional=True),
        L("flat_multi_field_schema"),
        L("nested_json_schema"),
        L("tabular_record_schema"),
        L("event_log_schema"),
        L("dialogue_transcript_schema"),
    ], cardinality="exactly_one"),

    G("measurement_mapping", [
        L("direct_item_score_output", conventional=True),
        L("latent_trait_then_item_output"),
        L("item_response_with_explanation"),
        L("distribution_over_response_options"),
        L("counterfactual_alternate_response_output"),
    ], cardinality="exactly_one"),

    G("response_constraint_strategy", [
        L("hard_bounded_integer_output", conventional=True),
        L("hard_category_set_output"),
        L("regex_constrained_output"),
        L("json_enum_constrained_output"),
        L("soft_instructional_constraint_only"),
        L("grammar_constrained_decoding"),
    ], cardinality="exactly_one"),

    G("missingness_representation", [
        L("no_missingness_allowed", conventional=True),
        L("explicit_refusal_category"),
        L("explicit_dont_know_category"),
        L("explicit_not_applicable_category"),
        L("stochastic_missingness_output"),
    ], cardinality="exactly_one"),

    G("confidence_representation", [
        L("no_confidence_field", conventional=True),
        L("confidence_score", var_type="continuous", value_space=PROB_01),
        L("probability_vector", var_type="distribution"),
        L("verbal_confidence_category"),
        L("entropy_proxy_output"),
        L("logit_capture", tags=["needs_logit_access"]),
    ], cardinality="exactly_one"),

    G("auxiliary_trace_capture", [
        L("final_answer_only", conventional=True),
        L("hidden_intermediate_state_not_captured"),
        L("explanatory_rationale_captured"),
        L("step_summary_captured"),
        L("calibration_metadata_captured"),
        L("tool_call_trace_captured"),
    ], cardinality="any_subset"),

    G("logging_granularity", [
        L("prompt_response_pair_logging", conventional=True),
        L("token_usage_logging"),
        L("latency_logging"),
        L("model_version_logging"),
        L("retry_history_logging"),
        L("failure_code_logging"),
        L("seed_logging"),
    ], cardinality="any_subset"),

    G("storage_format", [
        L("json_lines_storage", conventional=True),
        L("hierarchical_json_storage"),
        L("tabular_csv_storage"),
        L("database_record_storage"),
        L("graph_structured_storage"),
        L("versioned_artifact_storage"),
        L("parquet_columnar_storage"),
    ], cardinality="exactly_one"),
], cardinality="all_of", stage="generation")


# ---------------------------------------------------------------------------
# 2.13 Postprocessing
# ---------------------------------------------------------------------------
POSTPROCESS = G("postprocessing_and_data_transformation", [
    G("parsing_strategy", [
        L("strict_parser"),
        L("tolerant_parser", conventional=True),
        L("regex_extraction"),
        L("schema_repair_parser"),
        L("llm_based_self_repair_parser"),
    ], cardinality="exactly_one"),

    G("validation_strategy", [
        L("type_validation", conventional=True),
        L("range_validation", conventional=True),
        L("category_membership_validation"),
        L("cross_field_consistency_validation"),
        L("within_respondent_consistency_validation"),
        L("across_wave_consistency_validation"),
        L("attention_check_validation"),
    ], cardinality="any_subset"),

    G("score_transformation", [
        L("native_output_retained", conventional=True),
        L("linear_rescaling"),
        L("ordinal_to_interval_mapping"),
        L("z_score_standardisation"),
        L("norm_based_equating"),
        L("percentile_mapping"),
        L("calibration_curve_adjustment"),
        L("logit_link_transformation"),
    ], cardinality="exactly_one"),

    G("scale_construction", [
        L("item_sum_score", conventional=True),
        L("item_mean_score"),
        L("weighted_composite_score"),
        L("factor_score_estimation"),
        L("irt_based_trait_estimation"),
        L("profile_vector_retention"),
    ], cardinality="exactly_one"),

    G("text_transformation", [
        L("raw_text_retained"),
        L("rule_based_coding"),
        L("embedding_based_representation"),
        L("topic_model_projection"),
        L("sentiment_score_projection"),
        L("human_annotation_pipeline", tags=["high_cost"]),
        L("llm_judge_coding"),
    ], cardinality="any_subset"),

    G("distribution_correction", [
        L("no_correction", conventional=True),
        L("marginal_reweighting"),
        L("joint_distribution_raking"),
        L("post_stratification"),
        L("importance_weighting"),
        L("rejection_sampling_filter"),
        L("conformal_calibration"),
    ], cardinality="exactly_one"),

    G("bias_adjustment", [
        L("social_desirability_correction"),
        L("extreme_response_style_correction"),
        L("acquiescence_correction"),
        L("differential_item_functioning_correction"),
        L("group_bias_correction"),
    ], cardinality="any_subset"),

    G("aggregation_strategy", [
        L("single_draw_usage", conventional=True),
        L("mean_over_replicates"),
        L("median_over_replicates"),
        L("majority_vote_over_replicates"),
        L("bayesian_model_averaging"),
        L("weighted_ensemble_aggregation"),
    ], cardinality="exactly_one"),
], cardinality="all_of", stage="postprocessing")


# ---------------------------------------------------------------------------
# 2.14 Quality Assurance
# ---------------------------------------------------------------------------
QA = G("quality_assurance_and_failure_management", [
    G("failure_type_handling", [
        L("refusal_handling", conventional=True),
        L("safety_block_handling"),
        L("format_violation_handling", conventional=True),
        L("nonsensical_output_handling"),
        L("empty_output_handling"),
        L("timeout_handling"),
        L("truncation_handling"),
        L("hallucinated_metadata_handling"),
    ], cardinality="any_subset"),

    G("retry_policy", [
        L("no_retry"),
        L("same_prompt_retry", conventional=True),
        L("lower_temperature_retry"),
        L("format_repair_retry"),
        L("alternative_model_retry"),
        L("human_review_retry", tags=["high_cost"]),
    ], cardinality="exactly_one"),

    G("exclusion_policy", [
        L("respondent_level_exclusion"),
        L("item_level_exclusion"),
        L("configuration_level_exclusion"),
        L("wave_level_exclusion"),
        L("pairwise_available_case_retention"),
    ], cardinality="any_subset"),

    G("completion_threshold_policy", [
        L("no_completion_threshold"),
        L("min_50_percent_completion"),
        L("min_75_percent_completion", conventional=True),
        L("full_completion_required",
          forbids=["output_representation_and_capture.missingness_representation.stochastic_missingness_output"]),
        L("domain_specific_completion_threshold"),
    ], cardinality="exactly_one"),

    G("plausibility_screening", [
        L("range_plausibility_check", conventional=True),
        L("distribution_plausibility_check"),
        L("invariant_pattern_check"),
        L("unrealistic_homogeneity_check"),
        L("contradiction_check"),
        L("temporal_plausibility_check"),
    ], cardinality="any_subset"),

    G("adversarial_stress_testing", [
        L("prompt_perturbation_test"),
        L("formatting_perturbation_test"),
        L("demographic_swap_test"),
        L("counterfactual_identity_swap_test"),
        L("context_omission_test"),
        L("jailbreak_resistance_test"),
    ], cardinality="any_subset"),

    G("audit_trail_strategy", [
        L("immutable_run_log", conventional=True),
        L("configuration_registry"),
        L("prompt_version_archive"),
        L("data_lineage_capture"),
        L("seed_and_endpoint_archive"),
    ], cardinality="any_subset"),
], cardinality="all_of")


# ---------------------------------------------------------------------------
# 2.15 Evaluation Framework
# ---------------------------------------------------------------------------
EVALUATION = G("evaluation_and_validation_framework", [
    G("evaluation_target", [
        L("individual_ranking_recovery"),
        L("marginal_distribution_recovery", conventional=True),
        L("joint_association_recovery"),
        L("treatment_effect_recovery"),
        L("group_difference_recovery"),
        L("response_diversity_recovery"),
        L("calibration_recovery"),
        L("temporal_dynamics_recovery"),
        L("network_structure_recovery"),
        L("inter_individual_difference_moderation_recovery",
          desc="Recovery of moderating role of individual differences."),
    ], cardinality="at_least_one"),

    G("evaluation_unit", [
        L("item_level_evaluation", conventional=True),
        L("scale_level_evaluation", conventional=True),
        L("pairwise_association_evaluation"),
        L("respondent_level_evaluation"),
        L("population_level_evaluation"),
        L("cross_group_evaluation"),
    ], cardinality="at_least_one"),

    G("metric_family", [
        G("correlation_metrics", [
            L("pearson_correlation", outcome_modes=["regression"]),
            L("spearman_correlation", outcome_modes=["regression","ordinal","ranking"]),
            L("kendall_rank_correlation", outcome_modes=["ranking","ordinal"]),
            L("intraclass_correlation", outcome_modes=["regression"]),
        ], cardinality="at_least_one"),
        G("distribution_metrics", [
            L("wasserstein_distance", outcome_modes=["distribution","regression"]),
            L("kl_divergence", outcome_modes=["distribution"]),
            L("jensen_shannon_divergence", outcome_modes=["distribution"]),
            L("total_variation_distance", outcome_modes=["distribution"]),
            L("kolmogorov_smirnov", outcome_modes=["distribution","regression"]),
            L("earth_mover_by_group", outcome_modes=["distribution"]),
            L("mmd_metric", outcome_modes=["distribution","embedding"]),
        ], cardinality="at_least_one"),
        G("prediction_error_metrics", [
            L("mean_absolute_error", outcome_modes=["regression","ordinal"]),
            L("mean_squared_error", outcome_modes=["regression"]),
            L("absolute_correlation_error", outcome_modes=["regression"]),
            L("brier_score", outcome_modes=["binary","multiclass"]),
            L("log_loss", outcome_modes=["binary","multiclass","distribution"]),
        ], cardinality="at_least_one"),
        G("classification_metrics", [
            L("accuracy", outcome_modes=["binary","multiclass"]),
            L("balanced_accuracy", outcome_modes=["binary","multiclass"]),
            L("f1_score", outcome_modes=["binary","multiclass","multilabel"]),
            L("auroc", outcome_modes=["binary"]),
            L("auprc", outcome_modes=["binary"]),
            L("matthews_correlation", outcome_modes=["binary"]),
        ], cardinality="at_least_one"),
        G("calibration_metrics", [
            L("calibration_intercept", outcome_modes=["binary","regression"]),
            L("calibration_slope", outcome_modes=["binary","regression"]),
            L("expected_calibration_error", outcome_modes=["binary","multiclass"]),
        ], cardinality="at_least_one"),
        G("reliability_metrics", [
            L("internal_consistency_alpha", outcome_modes=["regression"]),
            L("test_retest_stability", outcome_modes=["regression"]),
            L("between_replicate_stability", outcome_modes=["regression","distribution"]),
        ], cardinality="at_least_one"),
        G("structural_metrics", [
            L("factor_loading_recovery", outcome_modes=["latent_regression"]),
            L("network_structure_recovery", outcome_modes=["graph"]),
            L("cluster_structure_recovery", outcome_modes=["multiclass"]),
            L("cramers_v_matrix_recovery", outcome_modes=["multiclass","binary"]),
        ], cardinality="at_least_one"),
        G("ranking_metrics", [
            L("ndcg", outcome_modes=["ranking"]),
            L("mean_reciprocal_rank", outcome_modes=["ranking"]),
            L("kendall_tau_rank", outcome_modes=["ranking"]),
        ], cardinality="at_least_one"),
        G("survival_metrics", [
            L("concordance_index", outcome_modes=["survival"]),
            L("integrated_brier_survival", outcome_modes=["survival"]),
        ], cardinality="at_least_one"),
        G("text_metrics", [
            L("bleu", outcome_modes=["text_judged"]),
            L("rouge", outcome_modes=["text_judged"]),
            L("bertscore", outcome_modes=["text_judged","embedding"]),
            L("llm_judge_score", outcome_modes=["text_judged"]),
            L("embedding_cosine", outcome_modes=["embedding","text_judged"]),
        ], cardinality="at_least_one"),
    ], cardinality="at_least_one"),

    G("comparator_design", [
        L("human_human_split_benchmark", conventional=True),
        L("human_silicon_direct_comparison", conventional=True),
        L("silicon_silicon_stability_comparison"),
        L("baseline_heuristic_comparison"),
        L("alternative_non_llm_method_comparison"),
        L("classical_simulation_comparison"),
    ], cardinality="at_least_one"),

    G("generalization_test", [
        L("same_dataset_same_domain", conventional=True),
        L("new_dataset_same_domain"),
        L("new_population_same_domain"),
        L("new_domain_same_method"),
        L("new_time_period_same_population"),
        L("cross_provider_generalisation"),
    ], cardinality="at_least_one"),

    G("uncertainty_quantification", [
        L("bootstrap_confidence_intervals", conventional=True),
        L("bayesian_posterior_uncertainty"),
        L("split_half_stability"),
        L("across_seed_variability"),
        L("across_configuration_variability"),
        L("conformal_prediction_intervals"),
    ], cardinality="any_subset"),

    G("subgroup_evaluation", [
        L("demographic_subgroup_fidelity"),
        L("political_subgroup_fidelity"),
        L("clinical_subgroup_fidelity"),
        L("cross_cultural_fidelity"),
        L("vulnerable_population_fidelity"),
        L("intersectional_subgroup_fidelity"),
    ], cardinality="any_subset"),

    G("fairness_evaluation", [
        L("differential_accuracy_by_group"),
        L("differential_calibration_by_group"),
        L("stereotype_amplification_assessment"),
        L("representation_flattening_assessment"),
        L("minority_distribution_recovery"),
        L("counterfactual_fairness_test"),
    ], cardinality="any_subset"),

    G("analysis_model_structure", [
        L("regression_outcome_structure", outcome_modes=["regression","latent_regression"], conventional=True),
        L("binary_classification_outcome_structure", outcome_modes=["binary"]),
        L("multiclass_outcome_structure", outcome_modes=["multiclass"]),
        L("ordinal_regression_outcome_structure", outcome_modes=["ordinal","regression"]),
        L("multilabel_outcome_structure", outcome_modes=["multilabel"]),
        L("ranking_outcome_structure", outcome_modes=["ranking"]),
        L("distribution_matching_outcome_structure", outcome_modes=["distribution"]),
        L("hierarchical_mixed_outcome_structure",
          outcome_modes=["hierarchical_mixed"],
          desc="Item-level classification nested in person-level regression."),
        L("network_recovery_outcome_structure", outcome_modes=["graph"]),
        L("latent_variable_outcome_structure", outcome_modes=["latent_regression"]),
        L("time_series_outcome_structure", outcome_modes=["sequence_model","regression"]),
        L("survival_outcome_structure", outcome_modes=["survival"]),
    ], cardinality="at_least_one"),
], cardinality="all_of", stage="evaluation", role="evaluation_variable")


# ---------------------------------------------------------------------------
# 2.16 Robustness / Multiverse
# ---------------------------------------------------------------------------
ROBUSTNESS = G("robustness_generalization_and_multiverse", [
    G("specification_space_mapping", [
        L("manual_specification_grid"),
        L("factorial_grid", conventional=True),
        L("fractional_factorial_grid"),
        L("random_multiverse_sample", conventional=True),
        L("latin_hypercube_sample"),
        L("bayesian_optimization"),
        L("evolutionary_search"),
        L("constraint_satisfaction_search"),
    ], cardinality="exactly_one"),

    G("perturbation_families", [
        L("prompt_wording_perturbation", conventional=True),
        L("format_perturbation"),
        L("order_perturbation"),
        L("context_inclusion_perturbation"),
        L("model_perturbation", conventional=True),
        L("hyperparameter_perturbation"),
        L("postprocessing_perturbation"),
        L("seed_perturbation"),
    ], cardinality="any_subset"),

    G("robustness_summary", [
        L("specification_curve", conventional=True),
        L("multiverse_distribution_plot"),
        L("sensitivity_index"),
        L("variance_decomposition"),
        L("sobol_style_importance_analysis"),
        L("leave_one_decision_out_analysis"),
        L("shapley_decision_importance"),
    ], cardinality="any_subset"),

    G("overfitting_control", [
        L("preregistered_search_space", conventional=True),
        L("locked_confirmation_set"),
        L("nested_validation"),
        L("early_stopping_on_calibration_search"),
        L("complexity_penalty_on_configuration_selection"),
    ], cardinality="any_subset"),

    G("domain_transfer_design", [
        L("within_construct_transfer"),
        L("cross_construct_transfer"),
        L("cross_study_transfer"),
        L("cross_cultural_transfer"),
        L("cross_provider_transfer"),
        L("cross_time_transfer"),
    ], cardinality="any_subset"),

    G("replicability_design", [
        L("exact_reproduction_run", conventional=True),
        L("provider_drift_monitoring"),
        L("endpoint_migration_check"),
        L("prompt_archive_replay"),
        L("containerised_local_replay"),
    ], cardinality="any_subset"),

    G("alternative_method_benchmarking", [
        L("embedding_based_baseline"),
        L("classical_statistical_simulation_baseline"),
        L("agent_based_rule_baseline"),
        L("human_forecasting_baseline"),
        L("simple_mean_or_mode_baseline", conventional=True),
    ], cardinality="any_subset"),
], cardinality="all_of")


# ---------------------------------------------------------------------------
# 2.17 Execution Environment
# ---------------------------------------------------------------------------
EXECUTION_ENV = G("execution_environment_and_infrastructure", [
    G("invocation_layer", [
        L("chat_completion_endpoint", conventional=True),
        L("response_oriented_endpoint"),
        L("batch_inference_endpoint"),
        L("local_inference_server"),
        L("queue_based_orchestration_service"),
    ], cardinality="exactly_one"),

    G("hardware_regime", [
        L("cpu_inference"),
        L("single_gpu_inference"),
        L("multi_gpu_inference"),
        L("cluster_inference"),
        L("provider_managed_hardware_abstraction", conventional=True),
    ], cardinality="exactly_one"),

    G("caching_policy", [
        L("no_cache"),
        L("prompt_hash_cache", conventional=True),
        L("response_cache"),
        L("embedding_cache"),
        L("configuration_artifact_cache"),
    ], cardinality="any_subset"),

    G("budget_management", [
        L("fixed_token_budget", conventional=True),
        L("fixed_monetary_budget"),
        L("runtime_ceiling"),
        L("per_configuration_budget_cap"),
        L("adaptive_budget_allocation"),
    ], cardinality="any_subset"),

    G("monitoring_stack", [
        L("latency_dashboard"),
        L("cost_dashboard"),
        L("error_dashboard"),
        L("distribution_drift_dashboard"),
        L("configuration_coverage_dashboard"),
    ], cardinality="any_subset"),

    G("security_and_access_control", [
        L("local_only_processing"),
        L("encrypted_artifact_store"),
        L("access_controlled_prompt_registry"),
        L("restricted_output_export"),
        L("secure_compute_environment"),
    ], cardinality="any_subset"),

    G("version_control_discipline", [
        L("prompt_version_pinning", conventional=True),
        L("model_version_pinning", conventional=True),
        L("code_commit_pinning", conventional=True),
        L("container_snapshot_pinning"),
        L("dataset_version_pinning"),
    ], cardinality="any_subset"),
], cardinality="all_of", role="infrastructure_variable")


# ---------------------------------------------------------------------------
# 2.18 Governance / Ethics
# ---------------------------------------------------------------------------
GOVERNANCE = G("governance_ethics_and_deployment_constraints", [
    G("ethical_risk_scope", [
        L("misrepresentation_risk"),
        L("identity_flattening_risk"),
        L("stereotype_reproduction_risk"),
        L("exclusion_of_vulnerable_voices_risk"),
        L("false_confidence_risk"),
        L("decision_automation_risk"),
        L("dual_use_risk"),
    ], cardinality="any_subset"),

    G("population_protection_design", [
        L("sensitive_attribute_minimisation"),
        L("vulnerable_group_safeguards"),
        L("differential_harm_review"),
        L("stakeholder_consultation"),
        L("human_oversight_requirement"),
    ], cardinality="any_subset"),

    G("disclosure_policy", [
        L("full_synthetic_provenance_disclosure", conventional=True),
        L("partial_research_disclosure"),
        L("internal_use_only_disclosure"),
        L("publication_transparency_standard"),
    ], cardinality="exactly_one"),

    G("reproducibility_governance", [
        L("full_prompt_release", conventional=True),
        L("configuration_release"),
        L("code_release", conventional=True),
        L("model_version_release"),
        L("restricted_due_to_license"),
    ], cardinality="any_subset"),

    G("legal_and_policy_constraints", [
        L("data_use_license_compliance"),
        L("api_terms_compliance"),
        L("jurisdictional_privacy_compliance"),
        L("institutional_review_compliance"),
        L("dual_use_assessment"),
    ], cardinality="any_subset"),

    G("deployment_boundary", [
        L("exploratory_research_only", conventional=True),
        L("decision_support_with_human_review"),
        L("educational_demonstration_use"),
        L("commercial_insight_use"),
        L("high_stakes_use_prohibited"),
    ], cardinality="exactly_one"),
], cardinality="all_of", role="ethical_variable")


# ---------------------------------------------------------------------------
# 3. Cross-tree constraints
# ---------------------------------------------------------------------------
CONSTRAINTS = [
    C("C001", "requires",
      if_=["sampling_and_generation_controls.reasoning_budget_control.high_reasoning_effort"],
      then=["model_system_selection.model_capability_regime.reasoning_model"],
      rationale="High reasoning effort requires a reasoning-class model."),
    C("C002", "forbids",
      if_=["interaction_decomposition_and_orchestration.within_respondent_memory_policy.session_memory_retention"],
      then=["interaction_decomposition_and_orchestration.call_topology.single_call_per_respondent"],
      rationale="Session memory retention is incompatible with one-shot per-respondent calls."),
    C("C003", "requires",
      if_=["evaluation_and_validation_framework.evaluation_target.joint_association_recovery"],
      then=["interaction_decomposition_and_orchestration.cross_item_dependency_handling.sequentially_conditioned_item_generation",
            "interaction_decomposition_and_orchestration.cross_item_dependency_handling.memory_carried_item_generation",
            "interaction_decomposition_and_orchestration.cross_item_dependency_handling.latent_state_carried_item_generation"],
      rationale="Joint-association recovery needs non-independent item generation."),
    C("C004", "requires",
      if_=["evaluation_and_validation_framework.evaluation_target.individual_ranking_recovery"],
      then=["synthetic_population_specification.persona_identity_structure.stable_synthetic_identities",
            "synthetic_population_specification.persona_identity_structure.reusable_panel_identities",
            "synthetic_population_specification.persona_identity_structure.multi_role_identities"],
      rationale="Person-level recovery needs identity stability."),
    C("C005", "requires",
      if_=["model_adaptation_and_alignment.adaptation_strategy.distribution_matching_fine_tuning"],
      then=["human_benchmark_data_design.benchmark_source_type.experimental_dataset",
            "human_benchmark_data_design.benchmark_source_type.survey_dataset",
            "human_benchmark_data_design.benchmark_source_type.panel_dataset",
            "human_benchmark_data_design.benchmark_source_type.administrative_dataset",
            "human_benchmark_data_design.benchmark_source_type.observational_behavioral_log",
            "human_benchmark_data_design.benchmark_source_type.controlled_lab_task_dataset",
            "human_benchmark_data_design.benchmark_source_type.field_experiment_dataset",
            "human_benchmark_data_design.benchmark_source_type.published_summary_statistics",
            "human_benchmark_data_design.benchmark_source_type.public_psychometric_repository"],
      rationale="Distribution matching needs a non-empty human benchmark."),
    C("C006", "forbids",
      if_=["quality_assurance_and_failure_management.completion_threshold_policy.full_completion_required"],
      then=["output_representation_and_capture.missingness_representation.stochastic_missingness_output"],
      rationale="Full-completion gates contradict stochastic missingness."),
    C("C007", "requires",
      if_=["evaluation_and_validation_framework.evaluation_target.temporal_dynamics_recovery"],
      then=["synthetic_population_specification.persona_persistence.multi_wave_persistent_respondent",
            "synthetic_population_specification.persona_persistence.cross_study_stable_respondent"],
      rationale="Cross-wave dynamics require persistent personas."),
    C("C008", "requires",
      if_=["evaluation_and_validation_framework.evaluation_target.treatment_effect_recovery"],
      then=["measure_task_and_stimulus_representation.experimental_design_encoding.between_subjects_condition_encoding",
            "measure_task_and_stimulus_representation.experimental_design_encoding.within_subjects_condition_encoding",
            "measure_task_and_stimulus_representation.experimental_design_encoding.factorial_condition_encoding",
            "measure_task_and_stimulus_representation.experimental_design_encoding.adaptive_intervention_encoding",
            "measure_task_and_stimulus_representation.experimental_design_encoding.counterfactual_scenario_encoding"],
      rationale="Treatment-effect recovery needs an intervention-encoding scheme."),
    C("C009", "requires",
      if_=["evaluation_and_validation_framework.fairness_evaluation"],
      then=["contextual_conditioning.persona_demographic_conditioning"],
      rationale="Fairness evaluation requires group labels in the conditioning."),
    C("C010", "requires",
      if_=["postprocessing_and_data_transformation.parsing_strategy.strict_parser"],
      then=["output_representation_and_capture.response_constraint_strategy.hard_bounded_integer_output",
            "output_representation_and_capture.response_constraint_strategy.hard_category_set_output",
            "output_representation_and_capture.response_constraint_strategy.regex_constrained_output",
            "output_representation_and_capture.response_constraint_strategy.json_enum_constrained_output",
            "output_representation_and_capture.response_constraint_strategy.grammar_constrained_decoding"],
      rationale="Strict parsers need a structured output contract."),
    C("C011", "requires",
      if_=["model_adaptation_and_alignment.adaptation_strategy.supervised_fine_tuning",
           "model_adaptation_and_alignment.adaptation_strategy.preference_optimization",
           "model_adaptation_and_alignment.adaptation_strategy.distribution_matching_fine_tuning",
           "model_adaptation_and_alignment.adaptation_strategy.lora_adapter_tuning",
           "model_adaptation_and_alignment.adaptation_strategy.prefix_tuning"],
      then=["model_system_selection.provider_class.open_weights_model",
            "model_system_selection.provider_class.local_deployment_model",
            "model_system_selection.provider_class.hosted_open_weights_model"],
      rationale="Fine-tuning requires open / fine-tuneable provider class."),
    C("C012", "requires",
      if_=["interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_topology.actor_critic_pair",
           "interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_topology.actor_multi_critic",
           "interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_topology.debate_two_agents",
           "interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_topology.debate_n_agents",
           "interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_topology.hierarchical_planner_executor",
           "interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_topology.hierarchical_planner_workers",
           "interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_topology.blackboard_society",
           "interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_topology.market_of_agents",
           "interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_topology.council_with_judge",
           "interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_topology.simulated_focus_group",
           "interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_topology.adversarial_red_team_blue_team",
           "interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_topology.network_of_peers"],
      then=["interaction_decomposition_and_orchestration.conversation_manager_strategy.programmatic_state_machine",
            "interaction_decomposition_and_orchestration.conversation_manager_strategy.tool_mediated_orchestration",
            "interaction_decomposition_and_orchestration.conversation_manager_strategy.agentic_planner_executor_loop",
            "interaction_decomposition_and_orchestration.conversation_manager_strategy.graph_compiled_workflow"],
      rationale="Non-trivial agent topologies need an orchestration manager."),
    C("C013", "requires",
      if_=["interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_topology.actor_critic_pair",
           "interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_topology.actor_multi_critic"],
      then=["interaction_decomposition_and_orchestration.multi_agent_simulation_design.iteration_control"],
      rationale="Actor-critic loops must declare an iteration control block."),
    C("C014", "forbids",
      if_=["interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_topology.single_agent"],
      then=["interaction_decomposition_and_orchestration.multi_agent_simulation_design.critic_evaluation_type"],
      rationale="Single-agent runs cannot have a separate critic agent."),
    C("C015", "requires",
      if_=["interaction_decomposition_and_orchestration.conversation_manager_strategy.tool_mediated_orchestration"],
      then=["model_system_selection.model_capability_regime.tool_using_model"],
      rationale="Tool-mediated orchestration requires a tool-capable model."),
    C("C016", "mutually_exclusive",
      if_=["sampling_and_generation_controls.reproducibility_control.fixed_seed",
           "sampling_and_generation_controls.reproducibility_control.provider_managed_randomness"],
      then=[],
      rationale="Already mutually exclusive by group cardinality; documented for clarity.",
      severity="advisory"),
    C("C017", "requires",
      if_=["measure_task_and_stimulus_representation.language_and_localization.locale_specific_adapted_wording",
           "evaluation_and_validation_framework.subgroup_evaluation.cross_cultural_fidelity",
           "evaluation_and_validation_framework.generalization_test.new_population_same_domain"],
      then=["contextual_conditioning.persona_demographic_conditioning.geography_specification"],
      rationale="Cross-cultural / new-population tests need geography conditioning."),
    C("C018", "requires",
      if_=["research_problem_formulation.causal_ambition.counterfactual_approximation",
           "evaluation_and_validation_framework.evaluation_target.treatment_effect_recovery"],
      then=["measure_task_and_stimulus_representation.experimental_design_encoding.counterfactual_scenario_encoding",
            "measure_task_and_stimulus_representation.experimental_design_encoding.between_subjects_condition_encoding",
            "measure_task_and_stimulus_representation.experimental_design_encoding.factorial_condition_encoding",
            "measure_task_and_stimulus_representation.experimental_design_encoding.adaptive_intervention_encoding"],
      rationale="Counterfactual / treatment effect ambition requires intervention encoding."),
    C("C019", "requires",
      if_=["measure_task_and_stimulus_representation.stimulus_material_encoding.image_description_proxy",
           "measure_task_and_stimulus_representation.stimulus_material_encoding.native_image_input"],
      then=["model_system_selection.model_capability_regime.multimodal_model"],
      rationale="Image / video / audio stimuli need a multimodal model."),
    C("C020", "forbids",
      if_=["target_human_system_specification.representation_granularity.unconditioned_generic_respondent"],
      then=["contextual_conditioning.persona_demographic_conditioning",
            "contextual_conditioning.psychological_conditioning"],
      rationale="An unconditioned generic respondent cannot carry persona conditioning."),
    C("C021", "co_recommended",
      if_=["evaluation_and_validation_framework.metric_family.distribution_metrics"],
      then=["evaluation_and_validation_framework.evaluation_target.marginal_distribution_recovery",
            "evaluation_and_validation_framework.evaluation_target.joint_association_recovery"],
      rationale="Distribution metrics co-recommend distribution-recovery targets.",
      severity="soft"),
    C("C022", "requires",
      if_=["evaluation_and_validation_framework.metric_family.classification_metrics"],
      then=["evaluation_and_validation_framework.analysis_model_structure.binary_classification_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.multiclass_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.multilabel_outcome_structure"],
      rationale="Classification metrics need a classification analysis structure."),
    C("C023", "requires",
      if_=["evaluation_and_validation_framework.metric_family.survival_metrics"],
      then=["evaluation_and_validation_framework.analysis_model_structure.survival_outcome_structure"],
      rationale="Survival metrics need a survival outcome."),
    C("C024", "requires",
      if_=["evaluation_and_validation_framework.metric_family.ranking_metrics"],
      then=["evaluation_and_validation_framework.analysis_model_structure.ranking_outcome_structure"],
      rationale="Ranking metrics need a ranking outcome."),
    C("C025", "requires",
      if_=["evaluation_and_validation_framework.metric_family.text_metrics"],
      then=["output_representation_and_capture.output_modality.free_text_output"],
      rationale="Text metrics need free-text outputs."),
    C("C026", "requires",
      if_=["output_representation_and_capture.confidence_representation.logit_capture"],
      then=["model_system_selection.provider_class.open_weights_model",
            "model_system_selection.provider_class.local_deployment_model"],
      rationale="Logit capture is generally only feasible on open / local deployments."),
    C("C027", "requires",
      if_=["interaction_decomposition_and_orchestration.multi_agent_simulation_design.critic_evaluation_type.human_in_the_loop_critic"],
      then=["governance_ethics_and_deployment_constraints.population_protection_design.human_oversight_requirement"],
      rationale="Human-in-the-loop critics imply human oversight governance."),
    C("C028", "modulates",
      if_=["interaction_decomposition_and_orchestration.multi_agent_simulation_design.iteration_control.max_iterations.max_iter_unbounded"],
      then=["interaction_decomposition_and_orchestration.multi_agent_simulation_design.agent_cost_control"],
      rationale="Unbounded iterations require explicit cost control."),
    C("C029", "requires",
      if_=["evaluation_and_validation_framework.evaluation_target.network_structure_recovery"],
      then=["evaluation_and_validation_framework.analysis_model_structure.network_recovery_outcome_structure"],
      rationale="Network recovery target needs network outcome structure."),
    C("C030", "advisory",
      if_=["sampling_and_generation_controls.temperature_control.temp_zero"],
      then=["sampling_and_generation_controls.diversity_control.diversity_via_persona_variation",
            "sampling_and_generation_controls.diversity_control.diversity_via_prompt_paraphrase_variation",
            "sampling_and_generation_controls.diversity_control.diversity_via_model_mixture"],
      rationale="At temperature zero, diversity must come from non-sampling sources.",
      severity="soft"),
    C("C031", "forbids",
      if_=["human_benchmark_data_design.benchmark_source_type.none_unsupervised_simulation"],
      then=["evaluation_and_validation_framework.comparator_design.human_silicon_direct_comparison",
            "evaluation_and_validation_framework.evaluation_target.calibration_recovery"],
      rationale="No-benchmark designs cannot do direct human-silicon comparison."),
    C("C032", "requires",
      if_=["evaluation_and_validation_framework.metric_family.correlation_metrics"],
      then=["evaluation_and_validation_framework.analysis_model_structure.regression_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.ordinal_regression_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.ranking_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.latent_variable_outcome_structure"],
      rationale="Correlation metrics require ordered, continuous, ranking, or latent outcomes."),
    C("C033", "requires",
      if_=["evaluation_and_validation_framework.metric_family.distribution_metrics"],
      then=["evaluation_and_validation_framework.analysis_model_structure.distribution_matching_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.regression_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.latent_variable_outcome_structure"],
      rationale="Distribution metrics require distributional or ordered scalar outcome structure."),
    C("C034", "requires",
      if_=["evaluation_and_validation_framework.metric_family.prediction_error_metrics"],
      then=["evaluation_and_validation_framework.analysis_model_structure.regression_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.ordinal_regression_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.binary_classification_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.multiclass_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.distribution_matching_outcome_structure"],
      rationale="Prediction-error metrics require scalar, ordinal, classification, or distribution outcome structure."),
    C("C035", "requires",
      if_=["evaluation_and_validation_framework.metric_family.calibration_metrics"],
      then=["evaluation_and_validation_framework.analysis_model_structure.regression_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.binary_classification_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.multiclass_outcome_structure"],
      rationale="Calibration metrics require a predicted scalar or class probability structure."),
    C("C036", "requires",
      if_=["evaluation_and_validation_framework.metric_family.reliability_metrics"],
      then=["evaluation_and_validation_framework.analysis_model_structure.regression_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.distribution_matching_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.latent_variable_outcome_structure"],
      rationale="Reliability metrics require repeated scalar, latent, or distributional measurement."),
    C("C037", "requires",
      if_=["evaluation_and_validation_framework.metric_family.structural_metrics"],
      then=["evaluation_and_validation_framework.analysis_model_structure.latent_variable_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.network_recovery_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.multiclass_outcome_structure",
            "evaluation_and_validation_framework.analysis_model_structure.binary_classification_outcome_structure"],
      rationale="Structural metrics require latent, network, cluster, or association outcome structure."),
    C("C038", "requires",
      if_=["evaluation_and_validation_framework.analysis_model_structure.hierarchical_mixed_outcome_structure"],
      then=["evaluation_and_validation_framework.evaluation_unit.item_level_evaluation"],
      rationale="Hierarchical mixed outcomes must preserve lower-level item or trial information."),
    C("C039", "requires",
      if_=["evaluation_and_validation_framework.analysis_model_structure.hierarchical_mixed_outcome_structure"],
      then=["evaluation_and_validation_framework.evaluation_unit.respondent_level_evaluation",
            "evaluation_and_validation_framework.evaluation_unit.cross_group_evaluation",
            "evaluation_and_validation_framework.evaluation_unit.population_level_evaluation"],
      rationale="Hierarchical mixed outcomes must preserve a higher-level respondent, group, or population unit."),
    C("C040", "modulates",
      if_=["model_system_selection.latent_performance_benchmark.mmlu_target_88",
           "model_system_selection.latent_performance_benchmark.mmlu_target_93"],
      then=["execution_environment_and_infrastructure.budget_management.per_configuration_budget_cap",
            "execution_environment_and_infrastructure.budget_management.fixed_monetary_budget"],
      rationale="Frontier-tier models (MMLU ≥ 0.88) carry materially higher inference costs; a budget cap is strongly recommended.",
      severity="soft"),
    C("C041", "modulates",
      if_=["model_system_selection.latent_performance_benchmark.mmlu_target_85",
           "model_system_selection.latent_performance_benchmark.mmlu_target_86"],
      then=["execution_environment_and_infrastructure.budget_management.per_configuration_budget_cap"],
      rationale="High-capability models (MMLU 0.85–0.86) impose elevated per-token costs; budget monitoring is recommended.",
      severity="soft"),
    C("C042", "requires",
      if_=["sampling_and_generation_controls.reasoning_budget_control.high_reasoning_effort"],
      then=["execution_environment_and_infrastructure.budget_management"],
      rationale="High reasoning effort multiplies token usage substantially; at least one budget management leaf must be active."),
    C("C043", "co_recommended",
      if_=["prompt_and_instruction_architecture.cognitive_guidance.zero_shot_chain_of_thought_cue",
           "prompt_and_instruction_architecture.cognitive_guidance.few_shot_chain_of_thought_cue",
           "prompt_and_instruction_architecture.cognitive_guidance.plan_then_respond_cue",
           "prompt_and_instruction_architecture.system_prompt_design.chain_of_thought_scaffold_system_prompt"],
      then=["output_representation_and_capture.auxiliary_trace_capture.explanatory_rationale_captured",
            "output_representation_and_capture.auxiliary_trace_capture.step_summary_captured"],
      rationale="Chain-of-thought elicitation should be paired with trace capture to enable post-hoc reasoning-quality validation.",
      severity="soft"),
    C("C044", "co_recommended",
      if_=["prompt_and_instruction_architecture.system_prompt_design.persona_constrained_system_prompt"],
      then=["contextual_conditioning.persona_demographic_conditioning",
            "contextual_conditioning.psychological_conditioning"],
      rationale="A persona-constrained system prompt should be aligned with conditioning variables applied at the user-turn level.",
      severity="soft"),
]


# ---------------------------------------------------------------------------
# 4. Presets
# ---------------------------------------------------------------------------
PRESETS = {
    "minimal_smoke": {
        "desc": "Tiny subset for testing the sampler end-to-end.",
        "include_subtrees": [
            "research_problem_formulation.intended_scientific_function",
            "research_problem_formulation.target_human_output_type",
            "model_system_selection.model_family",
            "sampling_and_generation_controls.temperature_control",
        ],
        "conventional_only": True,
    },
    "conventional_core": {
        "desc": "All conventional=True leaves across the whole tree.",
        "include_subtrees": ["*"],
        "conventional_only": True,
    },
    "multi_agent_focus": {
        "desc": "Subtrees relevant to multi-agent / critic-actor design.",
        "include_subtrees": [
            "interaction_decomposition_and_orchestration",
            "model_system_selection.model_capability_regime",
            "sampling_and_generation_controls",
            "evaluation_and_validation_framework.evaluation_target",
        ],
        "conventional_only": False,
    },
    "evaluation_focus": {
        "desc": "Evaluation / metric choices plus dependency subtrees needed for valid compatibility checks.",
        "include_subtrees": [
            "evaluation_and_validation_framework",
            "human_benchmark_data_design.benchmark_representation_mode",
            "output_representation_and_capture.output_modality",
            "contextual_conditioning",
            "interaction_decomposition_and_orchestration",
            "synthetic_population_specification",
            "measure_task_and_stimulus_representation",
            "model_system_selection",
            "governance_ethics_and_deployment_constraints",
        ],
        "conventional_only": False,
    },
    "prompting_only": {
        "desc": "Just prompt-construction levers.",
        "include_subtrees": [
            "prompt_and_instruction_architecture",
            "measure_task_and_stimulus_representation",
        ],
        "conventional_only": False,
    },
}


# ---------------------------------------------------------------------------
# 5. Assemble + write
# ---------------------------------------------------------------------------
def assemble() -> dict:
    return {
        "schema_version": "2.0",
        "ontology_id": "llm_synthetic_human_design_v2",
        "title": "Combinatorial State Space of LLM-Based Synthetic Human-Behavior Generation Designs",
        "summary": (
            "A typed, machine-readable taxonomy of design choices researchers and "
            "practitioners face when generating silicon human-behavior data with "
            "LLMs. The `meta` block defines the algebra (variable types, roles, "
            "stages, cardinalities, relations, outcome modes); `dimensions` holds "
            "the typed tree; `constraints` encodes cross-tree compatibility; "
            "`presets` defines named curated subsets for tractable enumeration."
        ),
        "meta": META,
        "dimensions": {
            "research_problem_formulation": RESEARCH_PROBLEM,
            "target_human_system_specification": TARGET_SYSTEM,
            "human_benchmark_data_design": BENCHMARK,
            "synthetic_population_specification": SYNTHETIC_POP,
            "model_system_selection": MODEL_SYSTEM,
            "model_adaptation_and_alignment": ADAPTATION,
            "measure_task_and_stimulus_representation": MEASURE_REPR,
            "contextual_conditioning": CONTEXT,
            "prompt_and_instruction_architecture": PROMPT_ARCH,
            "interaction_decomposition_and_orchestration": INTERACTION,
            "sampling_and_generation_controls": SAMPLING,
            "output_representation_and_capture": OUTPUT_REPR,
            "postprocessing_and_data_transformation": POSTPROCESS,
            "quality_assurance_and_failure_management": QA,
            "evaluation_and_validation_framework": EVALUATION,
            "robustness_generalization_and_multiverse": ROBUSTNESS,
            "execution_environment_and_infrastructure": EXECUTION_ENV,
            "governance_ethics_and_deployment_constraints": GOVERNANCE,
        },
        "constraints": CONSTRAINTS,
        "presets": PRESETS,
    }


def main() -> None:
    out = assemble()
    here = Path(__file__).parent
    target = here / "ontology.json"
    target.write_text(json.dumps(out, indent=2, ensure_ascii=False))

    n_groups = 0
    n_leaves = 0

    def walk(node):
        nonlocal n_groups, n_leaves
        if node.get("_kind") == "leaf":
            n_leaves += 1
            return
        n_groups += 1
        for c in node.get("children", {}).values():
            walk(c)

    for d in out["dimensions"].values():
        walk(d)
    print(f"Wrote {target} ({target.stat().st_size:,} bytes)")
    print(f"  groups: {n_groups}")
    print(f"  leaves: {n_leaves}")
    print(f"  constraints: {len(out['constraints'])}")
    print(f"  presets: {list(out['presets'].keys())}")


if __name__ == "__main__":
    main()
