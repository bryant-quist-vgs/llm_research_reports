#!/usr/bin/env python3
"""depth_eval_test.py — Tests for depth_eval.py, built against contract v0.
PROPOSAL: never executed.

Coverage (numbers are contract behaviors):
  - Happy path: one report with greedy summary, threshold sweep, per-depth accuracy,
    flat, beam and branch-ratio runs, on four hand-computed cases.
  - B1 load-bearing: invalid thresholds, settings, trees and flat preconditions raise
    before any backend call.
  - B2: per-node min_prob is ignored by the greedy run; the operator's tree object is
    not modified.
  - B3 load-bearing: the sweep makes no requests beyond the greedy run.
  - B4: per-depth accuracy conditions on a correct prefix; the product is reported.
  - B5: flat baseline option names, descriptions and values; cyclic and oversize
    trees are usage errors.
  - B6 / B9: beam and branch-ratio runs are summarized when requested, else null.
  - B7: a backend error is per-case and counted wrong; all-error returns None (exit 4).
  - Trust boundary: malformed case lines are usage errors naming the line number and
    never its content; the report never contains a case's state.
  - CLI exit codes 0 / 2 / 4 and --out; the CLI resolves its endpoint through
    rdm.resolve_endpoint, so the inference tunnel's variables select it.

The stand-in model reads its answers from each case's state, so every expected number
below can be checked by hand. All fixtures are in-process: no sockets, no network, no
files outside a temp dir.

Run with:
    python -m pytest depth_eval_test.py
or:
    python depth_eval_test.py
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest import mock

import depth_eval
import rdm

AREA, HW, SW, LEAF, FLAT = (
    "Which area?", "Which hardware part?", "Which software part?", "Which leaf?", "Flat?",
)

TREE = {
    "root": "area",
    "resolve_instructions": LEAF,
    "nodes": {
        "area": {"instructions": AREA, "min_prob": 0.99, "options": {
            "hw": {"description": "Hardware", "next": "hw"},
            "sw": {"description": "Software", "next": "sw"}}},
        "hw": {"instructions": HW, "options": {
            "disk": {"description": "Disk"},
            "fan": {"description": "Fan", "value": "FAN"}}},
        "sw": {"instructions": SW, "options": {
            "os": {"description": "Operating system"},
            "app": {"description": "Application"}}},
    },
}


def flat_answer(winner):
    names = ["hw/disk", "hw/fan", "sw/os", "sw/app"]
    return {name: (0.7 if name == winner else 0.1) for name in names}


def case(expected, expected_path, **answers):
    return {"state": {"answers": answers}, "expected": expected, "expected_path": expected_path}


# Greedy: c1 right, c2 right, c3 wrong at depth 2, c4 wrong at depth 1.
CASES = [
    case("disk", ["hw", "disk"], **{
        AREA: {"hw": 0.9, "sw": 0.1}, HW: {"disk": 0.8, "fan": 0.2},
        FLAT: flat_answer("hw/disk")}),
    case("FAN", ["hw", "fan"], **{
        AREA: {"hw": 0.6, "sw": 0.4}, HW: {"disk": 0.1, "fan": 0.9},
        SW: {"os": 0.5, "app": 0.5},
        LEAF: {"hw > fan": 0.8, "sw > os": 0.1, "sw > app": 0.1},
        FLAT: flat_answer("hw/fan")}),
    case("app", ["sw", "app"], **{
        AREA: {"hw": 0.05, "sw": 0.95}, SW: {"os": 0.55, "app": 0.45},
        LEAF: {"sw > os": 0.3, "sw > app": 0.7},
        FLAT: flat_answer("sw/app")}),
    case("os", ["sw", "os"], **{
        AREA: {"hw": 0.55, "sw": 0.45}, HW: {"disk": 0.5, "fan": 0.5},
        SW: {"os": 0.95, "app": 0.05},
        LEAF: {"sw > os": 0.6, "hw > disk": 0.2, "hw > fan": 0.2},
        FLAT: flat_answer("hw/disk")}),
]


class StateBackend:
    """A stand-in model: each case's state carries the answer to give per question."""

    def __init__(self):
        self.calls = []

    def __call__(self, state, instructions, criteria):
        self.calls.append((instructions, dict(criteria)))
        if state.get("fail"):
            raise rdm.BackendError("HTTP 500 from endpoint")
        return dict(state["answers"][instructions]), 1000


def evaluate(cases=CASES, tree=TREE, backend=None, **kwargs):
    backend = backend or StateBackend()
    kwargs.setdefault("thresholds", [0.5, 0.75, 0.95])
    return depth_eval.evaluate(tree, cases, backend, **kwargs), backend


class EvaluateTests(unittest.TestCase):
    def test_happy_path_report(self):
        report, _ = evaluate(flat_instructions=FLAT, beam_width=2, branch_ratio=0.5)
        self.assertEqual((report["cases"], report["errors"]), (4, 0))

        greedy = report["greedy"]
        self.assertEqual(greedy["reached_leaf"], 4)
        self.assertAlmostEqual(greedy["accuracy"], 0.5)
        self.assertAlmostEqual(greedy["mean_calls"], 2.0)
        self.assertAlmostEqual(greedy["mean_input_tokens"], 2000.0)
        self.assertAlmostEqual(greedy["cost_per_1000_usd"], 0.084)
        self.assertIsNotNone(greedy["latency_ms"]["p50"])
        self.assertIsNotNone(greedy["latency_ms"]["p95"])

        self.assertAlmostEqual(report["flat"]["accuracy"], 0.75)
        self.assertAlmostEqual(report["flat"]["mean_calls"], 1.0)
        self.assertAlmostEqual(report["beam"]["accuracy"], 0.75)
        self.assertAlmostEqual(report["ratio"]["accuracy"], 1.0)
        self.assertAlmostEqual(report["ratio"]["mean_calls"], 3.25)

    # Load-bearing: fit-assessment sessions read these fields (see ../BRIEF.md).
    def test_threshold_sweep_values(self):
        report, _ = evaluate()
        rows = {row["min_prob"]: row for row in report["thresholds"]}
        self.assertAlmostEqual(rows[0.5]["coverage"], 1.0)
        self.assertAlmostEqual(rows[0.5]["selective_accuracy"], 0.5)
        self.assertAlmostEqual(rows[0.5]["wrong_and_decided"], 0.5)
        self.assertAlmostEqual(rows[0.75]["coverage"], 0.25)
        self.assertAlmostEqual(rows[0.75]["selective_accuracy"], 1.0)
        self.assertAlmostEqual(rows[0.75]["accuracy"], 0.25)
        self.assertAlmostEqual(rows[0.75]["wrong_and_decided"], 0.0)
        self.assertAlmostEqual(rows[0.95]["coverage"], 0.0)
        self.assertIsNone(rows[0.95]["selective_accuracy"])

    # Load-bearing B3: a sweep costs one greedy run, not one run per threshold.
    def test_sweep_makes_no_extra_requests(self):
        _, one = evaluate(thresholds=[0.5])
        _, many = evaluate(thresholds=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95])
        self.assertEqual(len(one.calls), 8)
        self.assertEqual(len(many.calls), 8)

    def test_per_depth_conditions_on_a_correct_prefix(self):
        report, _ = evaluate()
        self.assertEqual(report["per_depth"], [
            {"depth": 1, "reached": 4, "correct": 3, "accuracy": 0.75},
            {"depth": 2, "reached": 3, "correct": 2, "accuracy": 2 / 3},
        ])
        self.assertAlmostEqual(report["product_of_depth_accuracies"], 0.5)

    def test_per_depth_is_empty_without_expected_paths(self):
        cases = [{"state": c["state"], "expected": c["expected"]} for c in CASES]
        report, _ = evaluate(cases=cases)
        self.assertEqual(report["per_depth"], [])
        self.assertIsNone(report["product_of_depth_accuracies"])

    def test_optional_runs_are_null_unless_requested(self):
        report, _ = evaluate()
        self.assertEqual((report["flat"], report["beam"], report["ratio"]), (None, None, None))

    # B2: the root's min_prob of 0.99 would abstain every case if it were honored.
    def test_per_node_thresholds_are_ignored_and_tree_is_not_modified(self):
        before = json.dumps(TREE, sort_keys=True)
        report, _ = evaluate()
        self.assertEqual(report["greedy"]["reached_leaf"], 4)
        self.assertEqual(json.dumps(TREE, sort_keys=True), before)

    def test_flat_baseline_shape(self):
        flat = depth_eval.flatten(TREE, FLAT, 255)
        options = flat["nodes"][flat["root"]]["options"]
        self.assertEqual(list(options), ["hw/disk", "hw/fan", "sw/os", "sw/app"])
        self.assertEqual(options["hw/fan"], {"description": "Hardware > Fan", "value": "FAN"})
        self.assertEqual(options["sw/os"], {"description": "Software > Operating system", "value": "os"})
        self.assertEqual(flat["nodes"][flat["root"]]["instructions"], FLAT)

    # Load-bearing B1: nothing is sent when any input is invalid.
    def test_invalid_inputs_make_no_backend_call(self):
        cyclic = {"root": "a", "nodes": {"a": {"instructions": "again?", "options": {
            "yes": {"description": "again", "next": "a"}, "no": {"description": "stop"}}}}}
        bad = [
            ({"thresholds": []}, TREE, depth_eval.UsageError),
            ({"thresholds": [0]}, TREE, depth_eval.UsageError),
            ({"thresholds": [1.5]}, TREE, depth_eval.UsageError),
            ({"beam_width": 0}, TREE, depth_eval.UsageError),
            ({"beam_width": 2, "beam_min_prob": 0}, TREE, depth_eval.UsageError),
            ({"branch_ratio": 2}, TREE, depth_eval.UsageError),
            ({"flat_instructions": FLAT}, cyclic, depth_eval.UsageError),
            ({"flat_instructions": FLAT, "max_options": 3}, TREE, depth_eval.UsageError),
            ({}, {"root": "missing", "nodes": {}}, rdm.TreeError),
        ]
        for kwargs, tree, error in bad:
            backend = StateBackend()
            with self.assertRaises(error):
                evaluate(tree=tree, backend=backend, **kwargs)
            self.assertEqual(backend.calls, [])

    # B7: one failing case is counted wrong and evaluation continues.
    def test_backend_errors_are_per_case(self):
        failing = {"state": {"fail": True}, "expected": "disk", "expected_path": ["hw", "disk"]}
        report, _ = evaluate(cases=CASES + [failing])
        self.assertEqual((report["cases"], report["errors"]), (5, 1))
        self.assertAlmostEqual(report["greedy"]["accuracy"], 2 / 5)
        self.assertAlmostEqual(report["greedy"]["mean_calls"], 2.0)
        self.assertEqual(report["per_depth"][0]["reached"], 4)

    def test_all_cases_failing_returns_none(self):
        failing = {"state": {"fail": True}, "expected": "disk"}
        report, _ = evaluate(cases=[failing, failing])
        self.assertIsNone(report)

    # Trust boundary: case content never appears in the report.
    def test_report_never_contains_state(self):
        cases = json.loads(json.dumps(CASES))
        for item in cases:
            item["state"]["body"] = "SECRET-STATE-MARKER"
        report, _ = evaluate(cases=cases, flat_instructions=FLAT, beam_width=2, branch_ratio=0.5)
        self.assertNotIn("SECRET-STATE-MARKER", json.dumps(report))


class LoadCasesTests(unittest.TestCase):
    def load(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "cases.jsonl")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(text)
            return depth_eval.load_cases(path)

    def test_blank_lines_are_skipped(self):
        cases = self.load('{"state": "a", "expected": 1}\n\n{"state": "b", "expected": 2}\n')
        self.assertEqual([c["expected"] for c in cases], [1, 2])

    # Trust boundary: errors name the line number, never the line's content.
    def test_malformed_lines_are_usage_errors_without_content(self):
        for text in (
            '{"state": "a", "expected": 1}\nSECRET-STATE-MARKER not json\n',
            '{"state": "a", "expected": 1}\n{"state": "SECRET-STATE-MARKER"}\n',
            '{"state": "a", "expected": 1}\n'
            '{"state": "SECRET-STATE-MARKER", "expected": 1, "expected_path": "hw"}\n',
            '{"state": "a", "expected": 1}\n["SECRET-STATE-MARKER"]\n',
        ):
            with self.assertRaises(depth_eval.UsageError) as caught:
                self.load(text)
            self.assertIn("line 2", str(caught.exception))
            self.assertNotIn("SECRET-STATE-MARKER", str(caught.exception))

    def test_empty_file_is_a_usage_error(self):
        with self.assertRaises(depth_eval.UsageError):
            self.load("\n\n")


class CliTests(unittest.TestCase):
    def run_cli(self, cases_text, backend, extra=(), tree=TREE, env=None):
        """Runs main() with a fake backend and ONLY the given environment variables."""
        self.built = []  # positional arguments each HttpBackend was constructed with

        def factory(*args, **kwargs):
            self.built.append(args)
            return backend

        with tempfile.TemporaryDirectory() as tmp:
            tree_path = os.path.join(tmp, "tree.json")
            cases_path = os.path.join(tmp, "cases.jsonl")
            out_path = os.path.join(tmp, "report.json")
            with open(tree_path, "w", encoding="utf-8") as handle:
                json.dump(tree, handle)
            with open(cases_path, "w", encoding="utf-8") as handle:
                handle.write(cases_text)
            argv = ["--tree", tree_path, "--cases", cases_path, *extra]
            if "--out" in extra:
                argv[argv.index("--out") + 1] = out_path
            out, err = io.StringIO(), io.StringIO()
            with mock.patch.object(depth_eval.rdm, "HttpBackend", factory), \
                    mock.patch.dict(os.environ, env or {}, clear=True), \
                    contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = depth_eval.main(argv)
            written = None
            if os.path.exists(out_path):
                with open(out_path, encoding="utf-8") as handle:
                    written = handle.read()
            return code, out.getvalue(), err.getvalue(), written

    CASES_TEXT = "".join(json.dumps(c) + "\n" for c in CASES)

    def test_exit_0_prints_one_report_and_writes_out(self):
        code, out, _, written = self.run_cli(
            self.CASES_TEXT, StateBackend(),
            extra=["--flat-instructions", FLAT, "--branch-ratio", "0.5", "--out", "PLACEHOLDER"],
        )
        self.assertEqual(code, 0)
        report = json.loads(out)
        self.assertAlmostEqual(report["greedy"]["accuracy"], 0.5)
        self.assertAlmostEqual(report["ratio"]["accuracy"], 1.0)
        self.assertEqual(json.loads(written), report)

    # The evaluation follows the inference tunnel's variables (rdm contract B13).
    def test_tunnel_environment_selects_endpoint_and_model_without_vendor_key(self):
        env = {"LOCAL_LLM_SERVER": "http://localhost:1234",
               "EXPECTED_LMSTUDIO_MODEL": "clef-q8", "TYPESAFE_API_KEY": "sk-hosted"}
        code, _, _, _ = self.run_cli(self.CASES_TEXT, StateBackend(), env=env)
        self.assertEqual(code, 0)
        self.assertEqual(self.built, [("http://localhost:1234", None, "clef-q8")])

    def test_exit_2_when_a_local_endpoint_has_no_model(self):
        backend = StateBackend()
        code, out, _, _ = self.run_cli(
            self.CASES_TEXT, backend, env={"LOCAL_LLM_SERVER": "http://localhost:1234"}
        )
        self.assertEqual((code, out), (2, ""))
        self.assertEqual(backend.calls, [])

    def test_exit_2_on_bad_cases_file(self):
        code, out, err, _ = self.run_cli("not json\n", StateBackend())
        self.assertEqual((code, out), (2, ""))
        self.assertIn("depth_eval:", err)

    def test_exit_2_on_invalid_tree(self):
        code, out, _, _ = self.run_cli(
            self.CASES_TEXT, StateBackend(), tree={"root": "x", "nodes": {}}
        )
        self.assertEqual((code, out), (2, ""))

    def test_exit_4_when_every_case_fails(self):
        text = json.dumps({"state": {"fail": True, "body": "SECRET-STATE-MARKER"}, "expected": 1}) + "\n"
        code, out, err, _ = self.run_cli(text, StateBackend())
        self.assertEqual((code, out), (4, ""))
        self.assertNotIn("SECRET-STATE-MARKER", err)


if __name__ == "__main__":
    unittest.main()
