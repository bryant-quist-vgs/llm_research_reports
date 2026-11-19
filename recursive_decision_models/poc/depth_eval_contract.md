Contract version: v0

# depth_eval.py — Accuracy-versus-depth evaluation of a recursive decision tree: Contract

`depth_eval.py` runs an `rdm.py` decision tree over a file of labelled cases and
prints one JSON report answering the questions no published benchmark answers for
recursive trees: how accuracy falls with depth, what a confidence threshold buys in
accuracy for what loss of coverage, how the tree compares with one flat Choice over
all leaves and with beam search, and what it costs per thousand decisions. It makes
model requests only through `rdm.decide` and performs no action on any decision.

Status: **proposal, never executed.** The contract stays at `v0` until an environment
exists, the tests have been run, and a review has closed (see Change log).

## Inputs

- **`--tree PATH`** — required. An `rdm.py` tree (see `rdm_contract.md`). **Trust:**
  operator-provided (trusted); validated by `rdm.validate_tree`.
- **`--cases PATH`** — required. JSON Lines; each non-blank line is an object with
  `state` (any JSON; the content to decide about), `expected` (any JSON; the correct
  leaf value) and optionally `expected_path` (array of option names from the root).
  **Trust:** `state` is external content (untrusted) and is only ever passed to
  `rdm.decide` as state; `expected` and `expected_path` are operator labels
  (trusted). A line that is not such an object is a usage error naming the line
  number, never its content.
- **`--thresholds FLOAT [FLOAT ...]`** — optional, default
  `0.5 0.6 0.7 0.8 0.9 0.95`. Each in (0, 1]. **Trust:** operator.
- **`--flat-instructions TEXT`** — optional. When given, also evaluate a flat
  baseline: one Choice over every leaf of the tree, asked with this text. Requires an
  acyclic tree whose leaf count is within `--max-options`. **Trust:** operator.
- **`--beam-width INT`** and **`--beam-min-prob FLOAT`** — optional (default: no beam
  run; `--beam-min-prob` default `0.15`). When `--beam-width` is greater than 1, also
  evaluate beam search with these settings. **Trust:** operator.
- **`--branch-ratio FLOAT`** — optional, default `0` (no ratio run), range [0, 1].
  When greater than 0, also evaluate `rdm.py`'s branch-ratio mode with this ratio
  (the talk's taxonomy demo uses 0.5). **Trust:** operator.
- **`--price-per-mtok FLOAT`** — optional, default `0.042` (TypeSafe Jev list price
  in USD per million input tokens, November 2026). Pass `0` for a self-hosted model.
  **Trust:** operator.
- **`--base-url`, `--model`, `--timeout`, `--retries`, `--max-depth`, `--max-calls`,
  `--max-options`** — optional; same meaning and defaults as `rdm.py`, including the
  `LOCAL_LLM_SERVER` and `EXPECTED_LMSTUDIO_MODEL` defaults used with the inference
  tunnel. **Trust:** operator.
- **`--out PATH`** — optional. Where to also write the report. **Trust:** operator.
- **Environment** — `RDM_BASE_URL`, `LOCAL_LLM_SERVER`, `RDM_MODEL`,
  `EXPECTED_LMSTUDIO_MODEL`, `RDM_API_KEY`, `TYPESAFE_API_KEY`, resolved by
  `rdm.resolve_endpoint` exactly as `rdm_contract.md` describes (behavior 13 there).
  **Trust:** operator; the two keys are operator secrets.

## Outputs

- **stdout** — exactly one JSON object (the *report*), then a newline:
  - `cases`, `errors` — number of cases, and of cases whose greedy run raised a
    backend error.
  - `greedy` — a *run summary* (below) for greedy descent with thresholds disabled.
  - `thresholds` — array, one entry per requested threshold `t`:
    `{"min_prob", "coverage", "selective_accuracy", "accuracy", "wrong_and_decided"}`
    where a case counts as *decided at t* when greedy descent reached a leaf and every
    step probability on its path is at least `t`; `coverage` = decided / cases;
    `selective_accuracy` = correct / decided (`null` when nothing is decided);
    `accuracy` = correct-and-decided / cases; `wrong_and_decided` =
    wrong-and-decided / cases (the rate of confident errors).
  - `per_depth` — array `{"depth", "reached", "correct", "accuracy"}` over cases that
    carry `expected_path`: at depth d, `reached` counts cases whose greedy path
    agrees with the expected path on all earlier levels and made a choice at d;
    `correct` counts those that also chose the expected option at d.
  - `product_of_depth_accuracies` — product of the `per_depth` accuracies (`null` if
    no case has `expected_path`): the end-to-end accuracy that independent per-level
    errors would predict, for comparison with `greedy.accuracy`.
  - `flat`, `beam`, `ratio` — a run summary each, or `null` when not requested.
  - A *run summary* is `{"reached_leaf", "accuracy", "mean_calls",
    "mean_input_tokens", "cost_per_1000_usd", "latency_ms": {"p50", "p95"}}`.
    `accuracy` = cases whose returned value equals `expected` / all cases (backend
    errors count as wrong). Means and latency are over cases without a backend error
    (`null` when there are none). Latency is client wall-clock per case and includes
    retries.
  The report never contains any case's state or the API key.
  `Load-bearing: the fit-assessment sessions described in ../BRIEF.md read coverage,
  selective_accuracy, wrong_and_decided, per_depth and cost_per_1000_usd to decide
  whether a tree is good enough for a use case.`
- **`--out PATH`** — optional file containing the same JSON object.
- **stderr** — one-line error messages; never a state, never the key.
- **Exit code** — `0` report produced; `2` usage error, invalid tree or cases file,
  flat baseline impossible, unreadable or unwritable file; `4` every case failed
  with a backend error (no report is printed).

## Behaviors

1. **Validate everything before the first request.** Tree, cases file, thresholds,
   beam and ratio settings and (when requested) the flat baseline's preconditions are
   checked first; any
   failure exits 2 with zero model requests.
   `Load-bearing: depth_eval_test.py asserts no backend call on invalid input.`
2. **Greedy run with thresholds disabled.** A deep copy of the tree with every
   per-node `min_prob` removed is run once per case with `min_prob = 1e-9`,
   `beam_width = 1`. `allow_none` still applies. The operator's tree file is not
   modified.
3. **Offline threshold sweep.** All `thresholds` entries are computed from the
   recorded step probabilities of the greedy run, without further requests.
   `Load-bearing: makes a threshold sweep cost one run instead of one run per
   threshold.`
4. **Per-depth accuracy.** Computed as defined under Outputs, from the greedy run.
5. **Flat baseline (optional).** The tree's leaves are enumerated depth-first; each
   becomes one option named by its option path joined with `/`, described by the
   descriptions on that path joined with ` > `, valued as the leaf's value. A cycle,
   or a leaf count outside 2..`max_options`, is a usage error. The one-node tree is
   run per case through `rdm.decide`.
6. **Beam run (optional).** The threshold-stripped tree is run per case with the
   given `beam_width` and `beam_min_prob`.
7. **Backend errors are per-case.** A case whose run raises `rdm.BackendError` is
   recorded as an error and counted as wrong; evaluation continues. If every case of
   the greedy run errored, exit 4.
8. **No action.** The script only measures. It never acts on a decision and never
   calls a generative model.
9. **Branch-ratio run (optional).** The threshold-stripped tree is run per case with
   the given `branch_ratio` and `min_prob = 1e-9`, so neither the nodes nor the
   resolving question is gated — the rule as the talk states it.

Any behavior the script performs that is not listed here is **undeclared** and
constitutes drift.

## Declared capability surface

- **Filesystem reads:** the `--tree` path and the `--cases` path. No other reads.
- **Filesystem writes:** the `--out` path only, when given. No other writes.
- **Network access:** only what `rdm.HttpBackend` performs: `POST
  {base_url}/v1/systemone`, redirects refused, proxies disabled for a loopback host.
- **Subprocess invocation:** No subprocess invocation.
- **Environment variables read:** through `rdm.resolve_endpoint` only:
  `RDM_BASE_URL`, `LOCAL_LLM_SERVER`, `RDM_MODEL`, `EXPECTED_LMSTUDIO_MODEL`,
  `RDM_API_KEY`, `TYPESAFE_API_KEY`.
- **Secrets handled:** the bearer API key chosen by `rdm.resolve_endpoint`, passed to
  `rdm.HttpBackend` and nowhere else; never logged or written.
- **Privilege escalation:** No privilege escalation.

## Assumptions for operation

- Python >= 3.11, standard library only, plus the sibling module `rdm.py`
  (contract `rdm_contract.md`) importable from the same directory.
- UTF-8 for all file I/O.
- Labels are correct and the cases are representative of production input; the
  report says nothing about inputs unlike the cases.
- Request volume is roughly cases x mean depth for the greedy run, plus cases for the
  flat run, plus up to cases x depth x beam width for the beam run, plus up to cases
  x `max_calls` for the branch-ratio run (it does not prune). The operator sizes the
  case file to the budget.
- Latency figures include network time and are not comparable across machines.

## Anti-patterns this script must not do

- Do **not** tune thresholds and report accuracy on the same cases as if it were a
  held-out estimate; the report is descriptive. Hold out a split when choosing a
  threshold.
- Do **not** echo case content in errors or the report.

## Revision rules

- Removing a behavior, an input, an output, or an assumption requires a high threshold
  and a deliberate version bump.
- Added assumptions never relax previous assumptions.
- Added capabilities to the declared capability surface require operator review.
- A version is ratified only after review; one change is one bump.
- The script's file header references the contract version it was built against.

## Change log

- **v1** — (pending): initial version. Drafted 2026-11-12, still unratified,
  including the branch-ratio run (behavior 9) and endpoint resolution through
  `rdm.resolve_endpoint` for use with the inference tunnel.
  Review: not yet run. The script and tests were written without being executed, at
  the operator's request (no environment existed on 2026-11-12). To ratify: run
  `python depth_eval_test.py`, fix what it raises, have a fresh reviewer run the
  auditable-script review prompt over the trio (with `rdm.py` as a sibling module),
  record the result here, then bump the version line and the script header to v1.
