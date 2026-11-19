Contract version: v0

# rdm.py — Recursive decision tree runner over a System One endpoint: Contract

`rdm.py` is a single-file reference implementation of a *recursive decision model*: a
table of decision nodes, each of which asks one typed Choice question of a
non-generative decision model through the `POST /v1/systemone` wire shape, and whose
chosen option may name another node to decide next. Code owns the control flow, the
context, the depth limit and the stopping rule; the model only returns a probability
per declared option. It is usable as an importable module (`decide(...)`) and as a CLI
that prints one JSON result. It never calls a generative model.

Status: **proposal, never executed.** The contract stays at `v0` until an environment
exists, the tests have been run, and a review has closed (see Change log).

## Inputs

- **`--tree PATH`** (CLI) / `tree: dict` (module) — required. JSON object
  `{"root": "<node id>", "nodes": {"<node id>": NODE, ...}}`. **Trust:**
  operator-provided (trusted), but structurally validated before any network call.
  `NODE` is:
  - `instructions` (string, required) — the question asked at this node.
  - `options` (object, required, 2..`max_options` entries) — option name →
    `{"description": string, "next": "<node id>" (optional), "value": any JSON (optional)}`.
    An option with `next` recurses into that node; an option without `next` is a leaf
    whose result is `value` if present, otherwise the option name.
  - `min_prob` (number in (0, 1], optional) — per-node override of the acceptance
    threshold.
  - `state_keys` (array of strings, optional) — when the state is a JSON object, send
    only these keys to the model at this node. This is how code, not the model,
    decides what context a node sees.
  - `allow_none` (boolean, optional, default false) — add a reserved option
    `__none__` ("None of the listed options fits."). Choosing it is an abstention.
  `next` may reference any node, including an ancestor or the node itself; cycles are
  legal and are bounded only by `max_depth` and `max_calls`.
  The tree object may also carry `resolve_instructions` (non-empty string, optional):
  the question text used for the final "which of these leaves" question in
  branch-ratio mode (behavior 12). Default: the root node's `instructions`.
- **`--state PATH`** (CLI, `-` for stdin) / `state: Any` (module) — required. The
  content being decided about. A file whose text parses as JSON is sent as that JSON
  value; any other text is sent as a string. **Trust:** external content
  (untrusted). It is never executed, never interpolated into instructions, never
  written to the trace, and it only reaches the model in the `state` field.
- **`--base-url URL`** — optional. Default: env `RDM_BASE_URL`, else env
  `LOCAL_LLM_SERVER` (the variable the inference-tunnel scripts export, for example
  `http://localhost:1234`), else `https://api.typesafe.ai`. Must be `http://` or
  `https://`. **Trust:** operator.
- **`--model NAME`** — optional. Default: env `RDM_MODEL`; else, when the base URL's
  host is loopback, env `EXPECTED_LMSTUDIO_MODEL` (the model key the tunnel attests);
  else, for a non-loopback host, `jev-latest`. A loopback base URL with no model from
  any of these is a usage error. **Trust:** operator.
- **`--min-prob FLOAT`** — optional, default `0.70`. A node's top option is accepted
  only if its probability is at least this value. **Trust:** operator.
- **`--max-depth INT`** — optional, default `8`. Maximum number of nodes on one
  root-to-leaf path. **Trust:** operator.
- **`--max-calls INT`** — optional, default `64`. Maximum model requests for one
  `decide` call, across all beams. **Trust:** operator.
- **`--beam-width INT`** — optional, default `1` (greedy). When greater than 1, up to
  this many partial paths are kept per level, ranked by joint probability. Only
  useful together with a lower `--min-prob` (for example 0.15), because at most one
  option can reach a threshold above 0.5. **Trust:** operator.
- **`--branch-ratio FLOAT`** — optional, default `0` (off), range [0, 1]. When greater
  than 0, selects branch-ratio mode (behavior 12), the rule used in the talk's
  taxonomy demo with ratio 0.5. Cannot be combined with `--beam-width` above 1. Only
  branches when `--min-prob` is low enough for a near-tie to pass the gate: with
  ratio 0.5 a second option can qualify only when the top probability is at most
  2/3. **Trust:** operator.
- **`--max-options INT`** — optional, default `255` (the TypeSafe Choice cap; Ollama's
  is 26). Trees with a node above the cap are rejected. **Trust:** operator.
- **`--timeout FLOAT`** — optional, default `30` seconds per request. **Trust:** operator.
- **`--retries INT`** — optional, default `2`. Retries on HTTP 429, 500, 502, 503
  and 504 and on connection errors only. **Trust:** operator.
- **`--trace-out PATH`** — optional. Where to also write the result JSON. **Trust:**
  operator.
- **Environment `RDM_API_KEY`** — optional bearer token, sent to whatever base URL is
  in use (a hosted vendor, a gateway, or a local server with API tokens switched on).
  **Trust:** operator secret.
- **Environment `TYPESAFE_API_KEY`** — optional bearer token, used only when
  `RDM_API_KEY` is unset **and** the base URL's host is exactly `api.typesafe.ai`. It
  is never sent to any other host. When no key applies, no `Authorization` header is
  sent. **Trust:** operator secret.
- **The model's HTTP response** — **Trust:** external content (untrusted). Validated:
  must be JSON with `answers.q.probabilities` mapping exactly the option names that
  were sent to finite numbers in [0, 1]. Anything else is a backend error.

## Outputs

- **stdout** — exactly one JSON object (the *result*), then a newline:
  - `status`: `"decided"` | `"abstained"` | `"depth_exceeded"` | `"budget_exceeded"`.
  - `value`: the leaf's `value` or option name when `decided`, else `null`.
  - `path`: array of `{"node", "option", "probability"}` for the accepted steps of
    the best path (partial when not `decided`).
  - `joint_probability`: product of the path's step probabilities (1.0 for an empty
    path).
  - `resolve_probability`: the probability the resolving question gave the chosen
    leaf in branch-ratio mode; `null` whenever no resolving question was asked.
  - `calls`: number of model requests made. `input_tokens`: sum of
    `usage.input_tokens` reported by the backend (0 when absent).
  - `trace`: array, one entry per model request, of `{"node", "depth",
    "probabilities", "top", "top_probability", "accepted", "input_tokens"}`. The
    resolving question appears as node `__resolve__` at depth 0. The trace never
    contains the state or the API key.
  `Load-bearing: depth_eval.py reads status, value, path[*].option,
  path[*].probability, calls and input_tokens; CI workflows read status and value
  with jq.`
- **`--trace-out PATH`** — optional file containing the same JSON object.
- **stderr** — one-line human-readable error messages. Never the state, never the key.
- **Exit code** — `0` decided; `3` abstained, depth exceeded or budget exceeded (a
  result was still printed); `2` usage or tree-validation error, unreadable input
  file, or unwritable `--trace-out`; `4` backend error (HTTP failure after retries,
  or a malformed response).
  `Load-bearing: CI workflows branch on 0 vs 3 vs 4 to implement fail-open / fail-closed.`

## Behaviors

1. **Validate the tree and arguments before any request.** Root exists; every `next`
   names an existing node; every node has 2..`max_options` options (counting
   `__none__` when `allow_none`); `min_prob` in (0, 1]; no option is literally named
   `__none__`; `resolve_instructions`, if present, is a non-empty string;
   `branch_ratio` is in [0, 1] and is not combined with `beam_width` above 1.
   Failure raises `TreeError` (CLI exit 2) with zero network calls.
   `Load-bearing: rdm_test.py asserts no backend call happens on an invalid tree.`
2. **One Choice question per node visit** (plus at most one resolving question per
   run in branch-ratio mode, in the same shape). The request body is
   `{"model", "state", "questions": {"q": {"type": "choice", "instructions",
   "criteria": {option: description}}}}`. The state sent is the full state, or the
   `state_keys` subset when the state is an object and the node declares
   `state_keys`.
   `Load-bearing: this is the /v1/systemone wire shape shared by TypeSafe Jev, Von,
   Ollama >= 0.35, llama.cpp and other compatible servers.`
3. **Code decides, from probabilities.** The chosen option is the arg-max of the
   returned `probabilities` (ties broken by the order options were declared). The
   backend's own `choice` and `confidence` fields are ignored.
4. **Threshold gate (abstention).** If the top probability is below the node's
   threshold, or the top option is `__none__`, that path stops and is marked
   abstained; nothing below it is asked.
   `Load-bearing: the "do not act on low confidence" guarantee that callers rely on
   to escalate to a human or an LLM.`
5. **Recursion with a depth limit.** An accepted option with `next` makes the next
   node the current node at depth + 1. A path that would visit more than
   `max_depth` nodes stops with `depth_exceeded`.
   `Load-bearing: termination guarantee for cyclic trees.`
6. **Call budget.** Before each request, if `calls == max_calls` the run stops with
   `budget_exceeded`, returning the best partial path.
   `Load-bearing: cost ceiling per decision.`
7. **Beam search (optional).** With `beam_width` k > 1, at each level every live
   path's node is asked, each path is extended by every option whose probability
   meets the node threshold (excluding `__none__`), and the k extensions with the
   highest joint probability survive. A finished leaf competes on joint probability
   with live paths; the run ends when the best candidate is a finished leaf or no
   live path remains. With k = 1 this is exactly the greedy descent of behaviors 3–5.
8. **Result selection.** Preference order: best `decided` path by joint probability
   (or, in branch-ratio mode, the leaf picked by the resolving question of behavior
   12); otherwise the longest partial path, with status `budget_exceeded` if the
   budget stopped the run, else `depth_exceeded` if any path hit the depth limit,
   else `abstained`.
9. **Retries.** HTTP 429, 500, 502, 503, 504 and connection errors are retried up to
   `retries` times with exponential backoff starting at 0.5 s, honoring a numeric
   `Retry-After` header up to 10 s. Other HTTP errors fail immediately; in
   particular 501, which llama.cpp-based servers (LM Studio included) return when the
   named model is not a decision model, is not retried and its message says so.
   Exhaustion raises `BackendError` (CLI exit 4).
10. **Response validation.** A response that is not JSON, lacks
    `answers.q.probabilities`, has option names different from those sent, or has a
    non-finite or out-of-range probability raises `BackendError`.
    `Load-bearing: a hostile or broken server cannot steer the tree to an undeclared
    option.`
11. **No generation, no side effects.** The module never calls a chat/completions
    endpoint, never executes anything named by a leaf `value`, and performs no action
    on the decision. It returns data; the caller acts.
12. **Branch-ratio mode (optional).** With `branch_ratio` r > 0, the gate of behavior
    4 still applies to each node's top option, but an accepted node is extended by
    *every* option (excluding `__none__`) whose probability is at least r times the
    top probability, and no path is pruned: every followed branch is explored until
    it reaches a leaf, abstains, or hits the depth limit or call budget. If more
    than one leaf is reached, one further Choice question is asked — the tree's
    `resolve_instructions` (default: the root's `instructions`) over the root's view
    of the state, with one option per leaf named by its option path joined with
    ` > ` and described by the leaf option's description — and its arg-max is the
    result. That answer is gated by the run's `min_prob`: below it the status is
    `abstained` and `value` is `null`. If the resolving question cannot be asked
    (call budget spent, more leaves than `max_options`, or two leaves with the same
    joined name), the leaf with the highest joint probability is returned and
    `resolve_probability` is `null`. With one leaf, no resolving question is asked.
13. **Endpoint resolution** (`resolve_endpoint`, used by this CLI and by
    `depth_eval.py`). Base URL, model and key are chosen as described under Inputs,
    before any request; a loopback endpoint with no model is a usage error (CLI exit
    2). "Loopback" means the host is `localhost`, ends in `.localhost`, or is a
    loopback IP address.
    `Load-bearing: lets the runner follow the inference tunnel's own variables
    (LOCAL_LLM_SERVER, EXPECTED_LMSTUDIO_MODEL) with no extra configuration, and
    keeps a hosted vendor's key from being sent down the tunnel.`
14. **Loopback endpoints are reached directly, never through a proxy.** When the
    base URL's host is loopback, proxy environment variables and system proxy
    settings are ignored for the request.
    `Load-bearing: a localhost SSH tunnel is only reachable from this machine; routing
    it through a proxy would both fail and hand the state to the proxy. The sandbox
    that runs benchmark workers allows only localhost:<tunnel port>.`

Any behavior the script performs that is not listed here is **undeclared** and
constitutes drift.

## Declared capability surface

- **Filesystem reads:** the `--tree` path and the `--state` path (or stdin). No other
  reads.
- **Filesystem writes:** the `--trace-out` path only, when given. No other writes.
- **Network access:** HTTP(S) `POST {base_url}/v1/systemone` only. `base_url` scheme
  restricted to `http`/`https`. Redirects are refused (a 3xx is a backend error), so
  the request and its bearer token never reach another host. A loopback host is
  contacted directly with proxies disabled; for any other host the Python standard
  library's default proxy handling applies (proxy environment variables and system
  settings). No other hosts, paths or methods.
- **Subprocess invocation:** No subprocess invocation. In particular the script does
  not run the tunnel's `--attest` check; the operator runs it first.
- **Environment variables read:** `RDM_BASE_URL`, `LOCAL_LLM_SERVER`, `RDM_MODEL`,
  `EXPECTED_LMSTUDIO_MODEL`, `RDM_API_KEY`, `TYPESAFE_API_KEY`; and, for non-loopback
  hosts only, the proxy variables the standard library reads (`http_proxy`,
  `https_proxy`, `no_proxy` and their upper-case forms).
- **Secrets handled:** one bearer API key — `RDM_API_KEY` for any base URL, or
  `TYPESAFE_API_KEY` for `api.typesafe.ai` only — sent only in the `Authorization`
  header to `base_url`; never logged, never written to stdout, stderr or the trace.
- **Privilege escalation:** No privilege escalation.

## Assumptions for operation

- Python >= 3.11, standard library only.
- UTF-8 for all file and network I/O.
- The endpoint implements the System One wire shape: a `choice` question returns
  `answers.<name>.probabilities` over the caller's option names (TypeSafe docs,
  `docs.typesafe.ai/api`). Compatibility of third-party servers is their claim, not
  verified here.
- When used through the inference tunnel (`inference_tunnel_setup`): the operator has
  started the tunnel and run its `--attest` check; LM Studio on the inference box
  serves `POST /v1/systemone` (its documentation says it does, for "a loaded decision
  model, not a regular chat model", following the llama.cpp server's implementation);
  and the model named is such a decision model. None of this has been exercised
  against a live server.
- `state` plus one question fits the endpoint's context limit; the script does not
  count tokens or truncate. Oversize requests surface as a backend error.
- This is a deliberately small, pure-decision subset of the talk's design
  (`rawwerks/rdm`, `dspy.experimental.RDM`): a static table of Choice nodes. It has
  no tools, no pointer loop, no Noul or Score questions, no map, no arbiter and no
  language-model fallback.
- The caller treats the result as advisory data. The state is attacker-controllable
  in most deployments, and published adversarial results show single-sentence edits
  flip a material share of decisions, so the caller must not grant privileges on the
  strength of a decision alone.

## Anti-patterns this script must not do

- Do **not** interpolate state into `instructions` or option descriptions. State is
  data; mixing it into the question lets the content rewrite the question.
- Do **not** fall back to a generative model inside this module. Escalation is the
  caller's decision, made on the returned status.
- Do **not** silently chunk or truncate a node with too many options. Reject it; the
  operator restructures the tree.
- Do **not** log the state or the request body.

## Revision rules

- Removing a behavior, an input, an output, or an assumption requires a high threshold
  and a deliberate version bump.
- Added assumptions never relax previous assumptions.
- Added capabilities to the declared capability surface require operator review.
- A version is ratified only after review; one change is one bump.
- The script's file header references the contract version it was built against.

## Change log

- **v1** — (pending): initial version. Drafted 2026-11-12 in three passes, all still
  unratified: the greedy and beam runner; branch-ratio mode (behavior 12); and
  inference-tunnel support (behaviors 13 and 14, the `LOCAL_LLM_SERVER` and
  `EXPECTED_LMSTUDIO_MODEL` defaults, the narrower `TYPESAFE_API_KEY` rule, and 501
  no longer retried).
  Review: not yet run. The script and tests were written without being executed, at
  the operator's request (no environment existed on 2026-11-12). To ratify: run
  `python rdm_test.py`, fix what it raises, have a fresh reviewer run the
  auditable-script review prompt over the trio, record the result here, then bump the
  version line and the script header to v1.
