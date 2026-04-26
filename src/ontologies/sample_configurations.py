#!/usr/bin/env python3
"""Enumerate or randomly sample eligible design configurations from ontology.json.

Each *configuration* is a set of selected leaf-ids. Eligibility is determined by:
  1. Group cardinality   (exactly_one, at_least_one, any_subset, all_of, ...)
  2. Leaf local rules    (_meta.requires / _meta.forbids)
  3. Global constraints  (top-level `constraints` array)

Usage examples
--------------
# All conventional leaves only, sample 100 configs
python sample_configurations.py --preset conventional_core --mode sample \\
    --max-samples 100 --output samples/eligible_samples.txt

# Just multi-agent + sampling subtrees, full enumeration capped at 50
python sample_configurations.py \\
    --include-subtree interaction_decomposition_and_orchestration.multi_agent_simulation_design \\
    --include-subtree sampling_and_generation_controls.temperature_control \\
    --mode enumerate --max-samples 50

# Validate constraint coverage on conventional preset
python sample_configurations.py --preset conventional_core --mode sample \\
    --max-samples 200 --report-only
"""
from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
DEFAULT_ONTOLOGY = HERE / "ontology.json"


# ---------------------------------------------------------------------------
# Tree indexing
# ---------------------------------------------------------------------------

def index_tree(dimensions: dict) -> tuple[dict, dict, dict, dict]:
    """Walk the dimensions tree.

    Returns:
        groups   : dict id -> group meta
        leaves   : dict id -> leaf meta
        children : dict id -> [child ids]   (group ids only; values are child ids)
        parent   : dict id -> parent id
    """
    groups, leaves, children, parent = {}, {}, {}, {}

    def walk(node, path):
        kind = node["_kind"]
        meta = node["_meta"]
        nid = ".".join(path) if path else None
        if kind == "leaf":
            leaves[nid] = meta
            return
        # group
        if nid is not None:
            groups[nid] = meta
        kids = []
        for label, child in node.get("children", {}).items():
            cpath = path + [label]
            cid = ".".join(cpath)
            parent[cid] = nid
            kids.append(cid)
            walk(child, cpath)
        if nid is None:
            # synthetic root
            groups["__root__"] = {"label": "__root__", "cardinality": "all_of"}
            for k in kids:
                parent[k] = "__root__"
            children["__root__"] = kids
        else:
            children[nid] = kids

    # Insert a synthetic root over the dimensions dict
    root = {
        "_kind": "group",
        "_meta": {"label": "__root__", "cardinality": "all_of",
                  "stage": ["design"], "role": ["design_variable"],
                  "optional": False, "tags": [], "desc": "", "k": None},
        "children": dimensions,
    }
    walk(root, [])
    return groups, leaves, children, parent


# ---------------------------------------------------------------------------
# Eligibility filtering by subtree / preset
# ---------------------------------------------------------------------------

def collect_descendants(node_id: str, children: dict) -> set:
    out = {node_id}
    stack = [node_id]
    while stack:
        n = stack.pop()
        for c in children.get(n, []):
            if c not in out:
                out.add(c); stack.append(c)
    return out


def restrict_to_subtrees(include, exclude, leaves, children) -> set:
    """Return set of leaf-ids that are inside any include and outside all exclude."""
    if not include or include == ["*"]:
        allowed = set(leaves.keys())
    else:
        allowed = set()
        for inc in include:
            desc = collect_descendants(inc, children)
            allowed |= (desc & set(leaves.keys()))
    for exc in exclude or []:
        desc = collect_descendants(exc, children)
        allowed -= (desc & set(leaves.keys()))
    return allowed


# ---------------------------------------------------------------------------
# Local choice generator per group
# ---------------------------------------------------------------------------

def legal_child_choices(group_id: str, group_meta: dict, kid_ids: list[str],
                        allowed_leaves: set, leaves: dict, children: dict,
                        rng: random.Random | None, mode: str,
                        max_branch: int | None) -> list[list[str]]:
    """Yield concrete subsets of kid_ids legal under this group's cardinality.

    Each kid may be a leaf OR a sub-group (which we include as a "presence" token
    here; downstream we resolve it).
    """
    # Filter kids: a leaf-kid must be in allowed_leaves; a group-kid must
    # contain at least one allowed leaf in its descendants (else it's empty).
    keepable = []
    for k in kid_ids:
        if k in leaves:
            if k in allowed_leaves: keepable.append(k)
        else:
            descendants_leaves = collect_descendants(k, children) & set(leaves.keys())
            if descendants_leaves & allowed_leaves: keepable.append(k)

    card = group_meta.get("cardinality", "exactly_one")
    k_param = group_meta.get("k")
    optional = group_meta.get("optional", False)

    if not keepable:
        return [[]] if (optional or card in ("any_subset","at_most_k","all_of")) else []

    n = len(keepable)
    if card == "exactly_one":
        return [[c] for c in keepable]
    if card == "all_of":
        return [list(keepable)]
    if card == "at_least_one":
        subs = []
        for r in range(1, n + 1):
            for combo in itertools.combinations(keepable, r):
                subs.append(list(combo))
        return _trim(subs, mode, rng, max_branch)
    if card == "any_subset":
        subs = [[]]
        for r in range(1, n + 1):
            for combo in itertools.combinations(keepable, r):
                subs.append(list(combo))
        return _trim(subs, mode, rng, max_branch)
    if card == "at_most_k":
        kk = k_param or n
        subs = [[]]
        for r in range(1, min(kk, n) + 1):
            for combo in itertools.combinations(keepable, r):
                subs.append(list(combo))
        return _trim(subs, mode, rng, max_branch)
    if card == "at_least_k":
        kk = k_param or 1
        subs = []
        for r in range(min(kk, n), n + 1):
            for combo in itertools.combinations(keepable, r):
                subs.append(list(combo))
        return _trim(subs, mode, rng, max_branch)
    if card == "exactly_k":
        kk = k_param or 1
        return _trim([list(c) for c in itertools.combinations(keepable, min(kk, n))],
                     mode, rng, max_branch)
    # default
    return [[c] for c in keepable]


def _trim(subs, mode, rng, max_branch):
    if max_branch and len(subs) > max_branch:
        if mode == "sample" and rng is not None:
            return rng.sample(subs, max_branch)
        return subs[:max_branch]
    return subs


# ---------------------------------------------------------------------------
# Configuration enumeration / sampling
# ---------------------------------------------------------------------------

def expand_node(node_id: str, groups: dict, leaves: dict, children: dict,
                allowed_leaves: set, rng, mode: str, max_branch: int | None):
    """Generator of frozensets-of-leaf-ids representing one realisation of node.

    Used for mode='enumerate' (ordered cross-product, truncated by max_branch).
    """
    if node_id in leaves:
        yield frozenset({node_id})
        return
    gmeta = groups[node_id]
    kids = children.get(node_id, [])
    choices = legal_child_choices(node_id, gmeta, kids, allowed_leaves,
                                  leaves, children, rng, mode, max_branch)
    if not choices:
        yield frozenset()
        return
    for choice in choices:
        if not choice:
            yield frozenset()
            continue
        sub_iters = []
        for k in choice:
            kid_options = list(expand_node(k, groups, leaves, children,
                                           allowed_leaves, rng, mode, max_branch))
            if max_branch and len(kid_options) > max_branch:
                kid_options = (rng.sample(kid_options, max_branch)
                               if (mode == "sample" and rng) else kid_options[:max_branch])
            sub_iters.append(kid_options or [frozenset()])
        for combo in itertools.product(*sub_iters):
            yield frozenset().union(*combo)


def sample_one(node_id: str, groups: dict, leaves: dict, children: dict,
               allowed_leaves: set, rng: random.Random,
               subset_prob: float = 0.0) -> frozenset:
    """Draw ONE configuration uniformly-at-random from the legal space at node.

    subset_prob controls Bernoulli probability for any_subset groups.
    When 0.0 (default) the sampler uses an adaptive rule:
        p = min(0.5, max(0.15, TARGET_SUBSET_SIZE / n))
    where TARGET_SUBSET_SIZE = 3, targeting ~3 selections per any_subset group
    regardless of how many children it has.  This prevents the leaf explosion
    that caused 0% valid rates when large any_subset groups (44 leaves) each
    contributed ~22 leaves via the naive Bernoulli-0.5 rule.

    Pass subset_prob > 0.0 to override (e.g. 0.3 for denser sampling).
    """
    _TARGET = 3  # desired mean selections per any_subset group

    if node_id in leaves:
        return frozenset({node_id})
    gmeta = groups[node_id]
    kids = children.get(node_id, [])
    # Filter kids to those reachable to allowed leaves
    keepable = []
    for k in kids:
        if k in leaves:
            if k in allowed_leaves: keepable.append(k)
        else:
            descendants_leaves = collect_descendants(k, children) & set(leaves.keys())
            if descendants_leaves & allowed_leaves: keepable.append(k)
    card = gmeta.get("cardinality", "exactly_one")
    k_param = gmeta.get("k")
    optional = gmeta.get("optional", False)
    n = len(keepable)
    if n == 0:
        return frozenset()

    if card == "exactly_one":
        chosen = [rng.choice(keepable)]
    elif card == "all_of":
        chosen = list(keepable)
    elif card == "at_least_one":
        # Draw a count in [1, min(n, TARGET+2)] to avoid over-selection in large groups
        upper = min(n, max(1, _TARGET + 2))
        r = rng.randint(1, upper)
        chosen = rng.sample(keepable, r)
    elif card == "any_subset":
        # Adaptive Bernoulli: target ~_TARGET selections regardless of group size.
        # If caller supplies explicit subset_prob, honour it.
        p = subset_prob if subset_prob > 0.0 else min(0.5, max(0.15, _TARGET / n))
        chosen = [k for k in keepable if rng.random() < p]
        if not chosen and not optional and n > 0:
            chosen = [rng.choice(keepable)]
    elif card == "at_most_k":
        kk = min(k_param or n, n)
        # For at_most_k, draw uniformly in [0, kk] (empty is always legal here)
        r = rng.randint(0, kk)
        chosen = rng.sample(keepable, r) if r else []
    elif card == "at_least_k":
        kk = min(k_param or 1, n)
        upper = min(n, max(kk, _TARGET + 1))
        r = rng.randint(kk, upper)
        chosen = rng.sample(keepable, r)
    elif card == "exactly_k":
        kk = min(k_param or 1, n)
        chosen = rng.sample(keepable, kk)
    else:
        chosen = [rng.choice(keepable)]

    out = frozenset()
    for c in chosen:
        out = out | sample_one(c, groups, leaves, children, allowed_leaves, rng,
                               subset_prob=subset_prob)
    return out


# ---------------------------------------------------------------------------
# Constraint repair
# ---------------------------------------------------------------------------

def is_under(child_id: str, ancestor_id: str) -> bool:
    return child_id == ancestor_id or child_id.startswith(ancestor_id + ".")


def repair_config(cfg: frozenset, constraints: list, leaves: dict,
                  allowed_leaves: set) -> frozenset:
    """Best-effort constraint repair on a sampled configuration.

    Two passes:

    1. REQUIRES repair — for each violated hard `requires` constraint (global or
       leaf-local), add the *first* matching allowed leaf from the `then` set.
       Handles: geography conditioning for cross-cultural/locale targets (C017),
       multimodal model for image stimuli (C019), orchestration manager for
       complex agent topologies (C012), stable identity for individual-level
       targets (C004, C047), and all leaf-local `requires` rules.

    2. FORBIDS repair — for each violated hard `forbids` constraint (global or
       leaf-local), remove leaves that are the *if* (triggering) side, provided
       the removal leaves the config structurally intact (non-empty required
       groups are not checked here; that is caught by the constraint checker).
       Handles: none_unsupervised_simulation co-existing with real sources (C045),
       unconditioned_generic_respondent co-existing with persona conditioning (C020),
       and leaf-local forbids rules.

    Repair is heuristic — it does not guarantee full validity, but it
    dramatically increases the valid rate without a complete constraint-
    propagation solver.  The constraint checker (constraints_pass) remains the
    authoritative gatekeeper.
    """
    cfg_set = set(cfg)

    # ── Pass 1: REQUIRES ─────────────────────────────────────────────────────
    for _round in range(3):   # up to 3 cascaded repair rounds
        changed = False

        # Leaf-local requires
        for lid in sorted(cfg_set):
            if lid not in leaves:
                continue
            for req in leaves[lid].get("requires", []):
                if not any(is_under(x, req) for x in cfg_set):
                    for candidate in sorted(allowed_leaves):
                        if is_under(candidate, req) and candidate not in cfg_set:
                            cfg_set.add(candidate)
                            changed = True
                            break

        # Global hard requires
        for c in constraints:
            if c.get("severity", "hard") != "hard":
                continue
            if c["relation"] != "requires":
                continue
            if_triggered = any(any(is_under(x, ref) for x in cfg_set)
                               for ref in c.get("if", []))
            if not if_triggered:
                continue
            then_refs = c.get("then", [])
            if not then_refs:
                continue
            then_ok = any(any(is_under(x, ref) for x in cfg_set)
                          for ref in then_refs)
            if then_ok:
                continue
            # Add one leaf from the first satisfying then_ref
            for ref in then_refs:
                added = False
                for candidate in sorted(allowed_leaves):
                    if is_under(candidate, ref) and candidate not in cfg_set:
                        cfg_set.add(candidate)
                        changed = True
                        added = True
                        break
                if added:
                    break

        if not changed:
            break

    # ── Pass 2: FORBIDS ──────────────────────────────────────────────────────
    # Leaf-local forbids: remove the leaf that fires the rule
    for lid in sorted(list(cfg_set)):
        if lid not in leaves or lid not in cfg_set:
            continue
        for forb in leaves[lid].get("forbids", []):
            if any(is_under(x, forb) for x in cfg_set):
                cfg_set.discard(lid)
                break

    # Global hard forbids: remove the *if* side (the special-case leaf)
    for c in constraints:
        if c.get("severity", "hard") != "hard":
            continue
        if c["relation"] != "forbids":
            continue
        if_leaves_present = [x for x in cfg_set
                              if any(is_under(x, ref) for ref in c.get("if", []))]
        then_leaves_present = [x for x in cfg_set
                                if any(is_under(x, ref) for ref in c.get("then", []))]
        if if_leaves_present and then_leaves_present:
            for leaf in if_leaves_present:
                cfg_set.discard(leaf)

    # ── Pass 3: MUTUALLY_EXCLUSIVE ───────────────────────────────────────────
    # If more than one of the if_set refs is covered, keep only the first and
    # remove all subsequent.  This handles C046 (ranking/survival/text metrics).
    for c in constraints:
        if c.get("severity", "hard") != "hard":
            continue
        if c["relation"] != "mutually_exclusive":
            continue
        # Collect which if_set refs are currently covered
        covered_refs = [ref for ref in c.get("if", [])
                        if any(is_under(x, ref) for x in cfg_set)]
        if len(covered_refs) > 1:
            # Drop leaves belonging to all but the first covered ref
            for ref in covered_refs[1:]:
                for leaf in sorted(list(cfg_set)):
                    if is_under(leaf, ref):
                        cfg_set.discard(leaf)

    # ── Pass 4: MODULATES (hard) — treat as requires ─────────────────────────
    for c in constraints:
        if c.get("severity", "hard") != "hard":
            continue
        if c["relation"] != "modulates":
            continue
        if_triggered = any(any(is_under(x, ref) for x in cfg_set)
                           for ref in c.get("if", []))
        if not if_triggered:
            continue
        then_refs = c.get("then", [])
        then_ok = any(any(is_under(x, ref) for x in cfg_set) for ref in then_refs)
        if then_ok:
            continue
        for ref in then_refs:
            for candidate in sorted(allowed_leaves):
                if is_under(candidate, ref) and candidate not in cfg_set:
                    cfg_set.add(candidate)
                    break

    # ── Pass 5: REQUIRES cleanup (re-run after forbids/mutually_exclusive) ───
    # Passes 2–4 may have removed leaves, invalidating requires that were OK
    # before.  One final requires sweep catches these secondary violations.
    for lid in sorted(cfg_set):
        if lid not in leaves:
            continue
        for req in leaves[lid].get("requires", []):
            if not any(is_under(x, req) for x in cfg_set):
                for candidate in sorted(allowed_leaves):
                    if is_under(candidate, req) and candidate not in cfg_set:
                        cfg_set.add(candidate)
                        break
    for c in constraints:
        if c.get("severity", "hard") != "hard":
            continue
        if c["relation"] not in ("requires", "modulates"):
            continue
        if_triggered = any(any(is_under(x, ref) for x in cfg_set)
                           for ref in c.get("if", []))
        if not if_triggered:
            continue
        then_refs = c.get("then", [])
        if not then_refs:
            continue
        if any(any(is_under(x, ref) for x in cfg_set) for ref in then_refs):
            continue
        for ref in then_refs:
            for candidate in sorted(allowed_leaves):
                if is_under(candidate, ref) and candidate not in cfg_set:
                    cfg_set.add(candidate)
                    break

    return frozenset(cfg_set)


def config_touches(config: frozenset, ref: str) -> bool:
    """True if any leaf in config falls under `ref` (leaf or group id)."""
    for l in config:
        if is_under(l, ref):
            return True
    return False


def constraints_pass(config: frozenset, constraints: list, leaves: dict) -> tuple[bool, list]:
    """Return (ok, list_of_violated_constraint_ids) for hard constraints only.

    Also enforces leaf-local requires/forbids.
    """
    violated = []

    # --- leaf-local rules ---
    for lid in config:
        meta = leaves[lid]
        for r in meta.get("requires", []):
            # `r` may be a leaf or group. Require at least one leaf from config under r.
            if not any(config_touches(config, r) for _ in (0,)):
                # Need at least one leaf in config that is under r.
                if not any(is_under(x, r) for x in config):
                    violated.append(f"local_requires:{lid}->{r}")
        for f in meta.get("forbids", []):
            if any(is_under(x, f) for x in config):
                violated.append(f"local_forbids:{lid}->{f}")

    # --- global constraints ---
    for c in constraints:
        sev = c.get("severity", "hard")
        if sev != "hard":
            continue  # soft/advisory don't filter
        rel = c["relation"]
        if_set = c.get("if", [])
        then_set = c.get("then", [])
        if rel == "requires":
            triggered = any(any(is_under(x, ref) for x in config) for ref in if_set)
            if triggered and then_set:
                # at least one of then_set must be touched
                if not any(any(is_under(x, ref) for x in config) for ref in then_set):
                    violated.append(c["id"])
        elif rel == "forbids":
            if_present = any(any(is_under(x, ref) for x in config) for ref in if_set)
            then_present = any(any(is_under(x, ref) for x in config) for ref in then_set)
            if if_present and then_present:
                violated.append(c["id"])
        elif rel == "mutually_exclusive":
            present = sum(1 for ref in if_set if any(is_under(x, ref) for x in config))
            if present > 1:
                violated.append(c["id"])
        elif rel == "modulates":
            triggered = any(any(is_under(x, ref) for x in config) for ref in if_set)
            if triggered and then_set:
                if not any(any(is_under(x, ref) for x in config) for ref in then_set):
                    violated.append(c["id"])
        # other relations are non-filtering
    return (len(violated) == 0, violated)


# ---------------------------------------------------------------------------
# Main sampling orchestration
# ---------------------------------------------------------------------------

def run(args):
    onto = json.loads(Path(args.ontology).read_text())
    groups, leaves, children, parent = index_tree(onto["dimensions"])
    constraints = onto.get("constraints", [])
    presets = onto.get("presets", {})

    # Resolve include/exclude
    include = list(args.include_subtree or [])
    exclude = list(args.exclude_subtree or [])
    conventional_only = args.conventional_only

    if args.preset:
        if args.preset not in presets:
            sys.exit(f"unknown preset {args.preset!r}; have {list(presets)}")
        ps = presets[args.preset]
        include = include + ps.get("include_subtrees", [])
        if ps.get("conventional_only"):
            conventional_only = True

    if args.list_presets:
        for name in sorted(presets):
            ps = presets[name]
            desc = ps.get("desc", ps.get("description", ""))
            print(f"{name}\t{desc}")
        return

    if not include:
        include = ["*"]

    allowed = restrict_to_subtrees(include, exclude, leaves, children)
    if conventional_only:
        allowed = {l for l in allowed if leaves[l].get("conventional")}
    if args.tag_filter:
        wanted = set(args.tag_filter)
        allowed = {l for l in allowed if wanted & set(leaves[l].get("tags", []))}
    if not allowed:
        sys.exit("no leaves remain after subtree/conventional/tag filtering")

    if args.list_subtrees:
        for gid in sorted(groups):
            if gid == "__root__": continue
            print(gid)
        return

    if args.list_leaves:
        for lid in sorted(allowed):
            print(lid)
        return

    rng = random.Random(args.seed)
    mode = args.mode
    subset_prob: float = args.subset_prob  # 0.0 = adaptive (recommended)

    # Build constraint rationale map for human-readable violation reporting
    constraint_rationale = {c["id"]: c.get("rationale", "") for c in constraints}

    do_repair: bool = not args.no_repair

    # Generator over the synthetic root.
    if mode == "enumerate":
        gen = expand_node("__root__", groups, leaves, children, allowed, rng,
                          mode, args.max_branch)
    else:
        def _sampler():
            while True:
                cfg = sample_one("__root__", groups, leaves, children, allowed, rng,
                                 subset_prob=subset_prob)
                if do_repair:
                    cfg = repair_config(cfg, constraints, leaves, allowed)
                yield cfg
        gen = _sampler()

    n_total = 0
    n_valid = 0
    violation_counts: dict = defaultdict(int)
    leaf_selection_counts: dict = defaultdict(int)   # marginal coverage tracker
    leaf_size_sum = 0
    out_lines = []

    for cfg in gen:
        n_total += 1
        ok, viols = constraints_pass(cfg, constraints, leaves)
        if ok:
            n_valid += 1
            leaf_size_sum += len(cfg)
            for lid in cfg:
                leaf_selection_counts[lid] += 1
        for v in viols:
            violation_counts[v] += 1
        if not args.include_invalid and not ok:
            if n_total >= args.scan_limit:
                break
            continue

        if not args.report_only:
            row = {
                "valid": ok,
                "violations": viols,
                "n_leaves": len(cfg),
                "leaves": sorted(cfg),
            }
            out_lines.append(json.dumps(row, ensure_ascii=False))

        if n_valid >= args.max_samples:
            break
        if n_total >= args.scan_limit:
            break

    # ── Marginal coverage: leaves never selected across valid configs ──────────
    never_selected = sorted(
        lid for lid in allowed if leaf_selection_counts[lid] == 0
    ) if n_valid > 0 else sorted(allowed)

    # ── Human-readable top violations ─────────────────────────────────────────
    top_viols_annotated = []
    for vid, cnt in sorted(violation_counts.items(), key=lambda x: -x[1])[:10]:
        rationale = constraint_rationale.get(vid, "")
        top_viols_annotated.append({
            "constraint": vid,
            "count": cnt,
            "rate": round(cnt / n_total, 3) if n_total else None,
            "rationale": rationale,
        })

    # Build summary
    summary = {
        "ontology": str(args.ontology),
        "schema_version": onto.get("schema_version"),
        "ontology_id": onto.get("ontology_id"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "preset": args.preset,
        "include_subtrees": include,
        "exclude_subtrees": exclude,
        "conventional_only": conventional_only,
        "tag_filter": args.tag_filter,
        "mode": mode,
        "seed": args.seed,
        "subset_prob": subset_prob if subset_prob > 0.0 else "adaptive",
        "max_samples": args.max_samples,
        "max_branch": args.max_branch,
        "scan_limit": args.scan_limit,
        "candidates_scanned": n_total,
        "valid_candidates": n_valid,
        "valid_rate": round(n_valid / n_total, 4) if n_total else None,
        "mean_leaves_per_valid_config": round(leaf_size_sum / n_valid, 1) if n_valid else None,
        "n_leaves_in_scope": len(allowed),
        "constraints_evaluated": sum(1 for c in constraints if c.get("severity", "hard") == "hard"),
        "top_violated_constraints": top_viols_annotated,
        "marginal_coverage": {
            "n_leaves_never_selected": len(never_selected),
            "coverage_rate": round(1 - len(never_selected) / len(allowed), 4) if allowed else None,
            "uncovered_leaves": never_selected[:30],  # cap at 30 for readability
        },
    }

    # Output
    if args.output:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        text = ["# eligible_samples.txt"]
        text.append("# " + "-" * 60)
        text.append("# Each non-comment row is a JSON-encoded configuration with")
        text.append("# fields: valid, violations, n_leaves, leaves[].")
        text.append("# Header below summarises the run; rows follow.")
        text.append("# " + "-" * 60)
        for k, v in summary.items():
            text.append(f"# {k}: {json.dumps(v, ensure_ascii=False)}")
        text.append("# " + "-" * 60)
        text.extend(out_lines)
        target.write_text("\n".join(text) + "\n")
        print(f"wrote {target} ({len(out_lines)} configs)")

    # Always print summary to stdout
    print(json.dumps(summary, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Enumerate / sample eligible design configurations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--ontology", default=str(DEFAULT_ONTOLOGY),
                   help="Path to ontology.json (default: ./ontology.json)")
    p.add_argument("--mode", choices=["enumerate", "sample"], default="sample",
                   help="enumerate = ordered cross-product (truncated by --max-branch); "
                        "sample = random draws (use --seed for reproducibility)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--max-samples", type=int, default=100,
                   help="Stop after this many VALID configurations.")
    p.add_argument("--scan-limit", type=int, default=200_000,
                   help="Hard cap on total candidates considered (valid+invalid).")
    p.add_argument("--max-branch", type=int, default=8,
                   help="Per-group branching cap (truncates large any_subset / "
                        "at_least_one expansions).")

    p.add_argument("--preset", default=None,
                   help="Use a named preset from ontology.json.presets")
    p.add_argument("--include-subtree", action="append", default=[],
                   help="Restrict to leaves under this dot-id (repeatable). "
                        "Default = whole tree.")
    p.add_argument("--exclude-subtree", action="append", default=[],
                   help="Drop leaves under this dot-id (repeatable).")
    p.add_argument("--conventional-only", action="store_true",
                   help="Keep only leaves marked conventional=True.")
    p.add_argument("--tag-filter", action="append", default=[],
                   help="Keep only leaves carrying ANY of these tags (repeatable).")
    p.add_argument("--subset-prob", type=float, default=0.0,
                   help="Bernoulli probability for any_subset groups (0.0 = adaptive, "
                        "recommended). Adaptive rule targets ~3 selections per group "
                        "regardless of group size, preventing leaf explosion in large "
                        "any_subset groups. Set > 0 to override (e.g. 0.3 for denser "
                        "conditioning sampling).")
    p.add_argument("--no-repair", action="store_true",
                   help="Disable the post-sample constraint-repair pass (requires and "
                        "forbids heuristic repair). Useful for diagnosing the raw "
                        "violation distribution before repair.")

    p.add_argument("--output", default=None,
                   help="Path to write eligible_samples.txt-style file.")
    p.add_argument("--include-invalid", action="store_true",
                   help="Also write rows that violated constraints (with their id).")
    p.add_argument("--report-only", action="store_true",
                   help="Don't write rows; just print the summary.")
    p.add_argument("--list-subtrees", action="store_true",
                   help="List all group dot-ids and exit (handy for --include-subtree).")
    p.add_argument("--list-leaves", action="store_true",
                   help="List leaves in the current scope and exit.")
    p.add_argument("--list-presets", action="store_true",
                   help="List named presets from ontology.json and exit.")
    return p.parse_args(argv)


if __name__ == "__main__":
    run(parse_args())
