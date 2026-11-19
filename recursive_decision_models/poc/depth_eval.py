#!/usr/bin/env python3
# depth_eval.py — accuracy-versus-depth evaluation of an rdm.py decision tree.
# Built against contract v0 (depth_eval_contract.md). PROPOSAL: never executed.
"""Evaluate a recursive decision tree on labelled cases.

    python depth_eval.py --tree trees/taxonomy.json --cases cases.jsonl \
        --flat-instructions "Which category fits this product?" --beam-width 3

Prints one JSON report: threshold sweep (coverage vs. accuracy), per-depth accuracy,
optional flat, beam and branch-ratio runs, cost per 1,000 decisions.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import sys
import time
from typing import Any

import rdm

DISABLED = 1e-9  # a min_prob that accepts every answer except __none__


class UsageError(ValueError):
    """Invalid arguments, cases file, or flat-baseline precondition."""


# -------------------------------------------------------------------------- input


def load_cases(path: str) -> list[dict[str, Any]]:
    cases = []
    with open(path, encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                case = json.loads(line)
            except json.JSONDecodeError:
                raise UsageError(f"cases line {number}: not JSON") from None
            if not isinstance(case, dict) or "state" not in case or "expected" not in case:
                raise UsageError(f'cases line {number}: needs "state" and "expected"')
            path_ = case.get("expected_path")
            if path_ is not None and not (
                isinstance(path_, list) and all(isinstance(p, str) for p in path_)
            ):
                raise UsageError(f"cases line {number}: expected_path must be strings")
            cases.append(case)
    if not cases:
        raise UsageError("cases file is empty")
    return cases


def strip_thresholds(tree: dict[str, Any]) -> dict[str, Any]:
    """Behavior 2: a copy of the tree with every per-node min_prob removed."""
    stripped = copy.deepcopy(tree)
    for node in stripped["nodes"].values():
        node.pop("min_prob", None)
    return stripped


def flatten(tree: dict[str, Any], instructions: str, max_options: int) -> dict[str, Any]:
    """Behavior 5: a one-node tree with one option per leaf of `tree`."""
    nodes = tree["nodes"]
    leaves: dict[str, dict[str, Any]] = {}

    def walk(node_id: str, names: list[str], descriptions: list[str], stack: set[str]) -> None:
        if node_id in stack:
            raise UsageError("flat baseline needs an acyclic tree")
        for name, option in nodes[node_id]["options"].items():
            here_names = names + [name]
            here_descriptions = descriptions + [option["description"]]
            if "next" in option:
                walk(option["next"], here_names, here_descriptions, stack | {node_id})
            else:
                leaves["/".join(here_names)] = {
                    "description": " > ".join(here_descriptions),
                    "value": option.get("value", name),
                }

    walk(tree["root"], [], [], set())
    if not 2 <= len(leaves) <= max_options:
        raise UsageError(f"flat baseline needs 2..{max_options} leaves, tree has {len(leaves)}")
    return {"root": "flat", "nodes": {"flat": {"instructions": instructions, "options": leaves}}}


# ---------------------------------------------------------------------------- run


def run(tree: dict[str, Any], cases: list[dict[str, Any]], backend: rdm.Backend, **limits: Any):
    """One rdm.decide per case. Returns [{"result": dict | None, "seconds": float}]."""
    records = []
    for case in cases:
        started = time.perf_counter()
        try:
            result = rdm.decide(tree, case["state"], backend, **limits)
        except rdm.BackendError:  # behavior 7: per-case, counted as wrong
            result = None
        records.append({"result": result, "seconds": time.perf_counter() - started})
    return records


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, math.ceil(q * len(ordered)) - 1)]


def summarize(records: list[dict], cases: list[dict], price_per_mtok: float) -> dict[str, Any]:
    ok = [r for r in records if r["result"] is not None]
    decided = [
        (r["result"], c) for r, c in zip(records, cases)
        if r["result"] is not None and r["result"]["status"] == "decided"
    ]
    tokens = _mean([r["result"]["input_tokens"] for r in ok])
    return {
        "reached_leaf": len(decided),
        "accuracy": sum(res["value"] == c["expected"] for res, c in decided) / len(cases),
        "mean_calls": _mean([r["result"]["calls"] for r in ok]),
        "mean_input_tokens": tokens,
        "cost_per_1000_usd": None if tokens is None else tokens * price_per_mtok / 1e6 * 1000,
        "latency_ms": {
            "p50": _ms(_percentile([r["seconds"] for r in ok], 0.50)),
            "p95": _ms(_percentile([r["seconds"] for r in ok], 0.95)),
        },
    }


def _ms(seconds: float | None) -> float | None:
    return None if seconds is None else round(seconds * 1000, 1)


def sweep(records: list[dict], cases: list[dict], thresholds: list[float]) -> list[dict]:
    """Behavior 3: offline, from the greedy run's step probabilities."""
    rows = []
    for threshold in thresholds:
        decided = correct = 0
        for record, case in zip(records, cases):
            result = record["result"]
            if result is None or result["status"] != "decided":
                continue
            if all(step["probability"] >= threshold for step in result["path"]):
                decided += 1
                correct += result["value"] == case["expected"]
        rows.append(
            {
                "min_prob": threshold,
                "coverage": decided / len(cases),
                "selective_accuracy": correct / decided if decided else None,
                "accuracy": correct / len(cases),
                "wrong_and_decided": (decided - correct) / len(cases),
            }
        )
    return rows


def per_depth(records: list[dict], cases: list[dict]) -> list[dict]:
    """Behavior 4: accuracy at depth d given a correct prefix."""
    reached: dict[int, int] = {}
    correct: dict[int, int] = {}
    for record, case in zip(records, cases):
        expected = case.get("expected_path")
        if expected is None or record["result"] is None:
            continue
        chosen = [step["option"] for step in record["result"]["path"]]
        for index, want in enumerate(expected):
            if index >= len(chosen) or chosen[:index] != expected[:index]:
                break
            reached[index] = reached.get(index, 0) + 1
            correct[index] = correct.get(index, 0) + (chosen[index] == want)
    return [
        {
            "depth": index + 1,
            "reached": reached[index],
            "correct": correct[index],
            "accuracy": correct[index] / reached[index],
        }
        for index in sorted(reached)
    ]


def evaluate(
    tree: dict[str, Any],
    cases: list[dict[str, Any]],
    backend: rdm.Backend,
    *,
    thresholds: list[float],
    flat_instructions: str | None = None,
    beam_width: int = 1,
    beam_min_prob: float = 0.15,
    branch_ratio: float = 0.0,
    price_per_mtok: float = 0.042,
    max_depth: int = 8,
    max_calls: int = 64,
    max_options: int = 255,
) -> dict[str, Any] | None:
    """Build the report. Returns None when every greedy case hit a backend error."""
    # Behavior 1: everything is validated before the first request.
    rdm.validate_tree(tree, max_options)
    if not thresholds or not all(rdm._is_probability(t, allow_zero=False) for t in thresholds):
        raise UsageError("thresholds must be in (0, 1]")
    if not rdm._is_probability(beam_min_prob, allow_zero=False) or beam_width < 1:
        raise UsageError("beam settings out of range")
    if not rdm._is_probability(branch_ratio):
        raise UsageError("branch ratio must be in [0, 1]")
    free = strip_thresholds(tree)
    flat_tree = flatten(tree, flat_instructions, max_options) if flat_instructions else None
    limits = {"max_depth": max_depth, "max_calls": max_calls, "max_options": max_options}

    greedy = run(free, cases, backend, min_prob=DISABLED, beam_width=1, **limits)
    errors = sum(r["result"] is None for r in greedy)
    if errors == len(cases):
        return None
    depths = per_depth(greedy, cases)
    report = {
        "cases": len(cases),
        "errors": errors,
        "greedy": summarize(greedy, cases, price_per_mtok),
        "thresholds": sweep(greedy, cases, thresholds),
        "per_depth": depths,
        "product_of_depth_accuracies": math.prod(d["accuracy"] for d in depths) if depths else None,
        "flat": None,
        "beam": None,
        "ratio": None,
    }
    if flat_tree is not None:
        flat = run(flat_tree, cases, backend, min_prob=DISABLED, beam_width=1, **limits)
        report["flat"] = summarize(flat, cases, price_per_mtok)
    if beam_width > 1:
        beam = run(free, cases, backend, min_prob=beam_min_prob, beam_width=beam_width, **limits)
        report["beam"] = summarize(beam, cases, price_per_mtok)
    if branch_ratio > 0:  # behavior 9: the talk's rule, with no confidence gate
        ratio = run(
            free, cases, backend, min_prob=DISABLED, branch_ratio=branch_ratio, **limits
        )
        report["ratio"] = summarize(ratio, cases, price_per_mtok)
    return report


# ---------------------------------------------------------------------------- cli


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tree", required=True)
    parser.add_argument("--cases", required=True)
    parser.add_argument(
        "--thresholds", type=float, nargs="+", default=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95]
    )
    parser.add_argument("--flat-instructions")
    parser.add_argument("--beam-width", type=int, default=1)
    parser.add_argument("--beam-min-prob", type=float, default=0.15)
    parser.add_argument("--branch-ratio", type=float, default=0.0)
    parser.add_argument("--price-per-mtok", type=float, default=0.042)
    parser.add_argument("--base-url", help="default: RDM_BASE_URL, LOCAL_LLM_SERVER, TypeSafe")
    parser.add_argument("--model", help="default: RDM_MODEL, EXPECTED_LMSTUDIO_MODEL (local)")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--max-depth", type=int, default=8)
    parser.add_argument("--max-calls", type=int, default=64)
    parser.add_argument("--max-options", type=int, default=255)
    parser.add_argument("--out")
    args = parser.parse_args(argv)

    try:
        base_url, model, api_key = rdm.resolve_endpoint(args.base_url, args.model)
        with open(args.tree, encoding="utf-8") as handle:
            tree = json.load(handle)
        cases = load_cases(args.cases)
        backend = rdm.HttpBackend(
            base_url, api_key, model, timeout=args.timeout, retries=args.retries
        )
        report = evaluate(
            tree,
            cases,
            backend,
            thresholds=args.thresholds,
            flat_instructions=args.flat_instructions,
            beam_width=args.beam_width,
            beam_min_prob=args.beam_min_prob,
            branch_ratio=args.branch_ratio,
            price_per_mtok=args.price_per_mtok,
            max_depth=args.max_depth,
            max_calls=args.max_calls,
            max_options=args.max_options,
        )
    except (UsageError, rdm.TreeError, OSError, json.JSONDecodeError) as err:
        print(f"depth_eval: {err}", file=sys.stderr)
        return 2
    if report is None:
        print("depth_eval: every case failed with a backend error", file=sys.stderr)
        return 4

    text = json.dumps(report, indent=2)
    print(text)
    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8") as handle:
                handle.write(text + "\n")
        except OSError as err:
            print(f"depth_eval: could not write report: {err}", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
