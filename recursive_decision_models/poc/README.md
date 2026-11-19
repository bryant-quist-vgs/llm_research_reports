---
id: poc-README
derives_from: [BRIEF]
---

# Proof-of-concept proposals

**Status: proposals. Nothing in this directory has been executed** — no test run, no
model request, no workflow run, not even a syntax check of the Python files. No
environment existed when it was written (2026-11-12). The only mechanical check was
that the JSON tree and the example cases file parse as JSON. The code was desk-checked
by reading, and every expected value in the tests was worked out by hand. Expect to
fix things on first run.

## What is here

| File | What it is |
|---|---|
| `rdm.py` | A recursive decision tree runner. Standard library only. Each node asks one Choice question over the `POST /v1/systemone` wire shape; code owns context, recursion, depth limit, call budget and the confidence gate. Greedy, beam and branch-ratio modes |
| `rdm_contract.md` | What `rdm.py` is allowed to do (inputs, outputs, behaviors, capability surface). Version `v0` |
| `rdm_test.py` | Tests for every load-bearing behavior, with an in-process fake model |
| `depth_eval.py` | The measurement no published benchmark provides: accuracy by depth, coverage versus accuracy across confidence thresholds, tree versus one flat question versus beam versus branch-ratio, cost per 1,000 decisions |
| `depth_eval_contract.md`, `depth_eval_test.py` | Its contract (`v0`) and tests |
| `trees/pr_triage.json` | Example tree: pull-request triage, depth up to 3, at most 4 options per node, an escape option on the ambiguous nodes |
| `cases/pr_triage.example.jsonl` | Six **illustrative** labelled cases showing the file format. Far too few to measure anything |
| `workflows/decide-hosted.yml` | GitHub Actions design A: hosted API, advisory output, neutral on fork PRs |
| `workflows/decide-local.yml` | GitHub Actions design B: small local model on the standard CPU runner, cached weights, works on fork PRs |

## How this relates to the talk's code

`rdm.py` is a deliberately small, **pure-decision subset** of the design in the talk
(reference code: `rawwerks/rdm` in Rust and `dspy.experimental.RDM` in Python; see
`../appendices/H-talk-and-vendor-patterns.md`).

| Talk's design | This PoC |
|---|---|
| Typed questions: Noul, Choice, Score | Choice only |
| Tools: functions that slice state and call the module again | A static table of nodes; an option's `next` names the child node |
| Code slices context per call (rule 1) | `state_keys` per node selects which keys of a JSON state the node sees |
| A decision may call another decision, up to a depth limit (rule 2) | `next`, `--max-depth`, `--max-calls` |
| Works with no generative model (rule 3) | Always: no generative call exists in the module |
| Composes with LLMs and agents (rule 3) | Left to the caller: exit code 3 (abstained) is the hook for escalation |
| Pointer loop, `finish`, map, arbiter, `Fit`, `Near`, `ReAnchor` | Not implemented |
| Taxonomy demo: follow every child at least half as likely as the top, then ask again among the leaves found | `--branch-ratio 0.5` |
| No confidence gate in the demo | `--min-prob` gate on every node and on the resolving question (default 0.70) |

If the pilot shows the pattern is worth adopting, evaluate the reference
implementations or the libraries in `../appendices/G-prior-art-and-critiques.md`
(`discern`, `solvi`, `hunch`, `jev-tree`) before growing this file.

## Tree format

```json
{
  "root": "kind",
  "resolve_instructions": "optional; question used to pick among leaves in branch-ratio mode",
  "nodes": {
    "kind": {
      "instructions": "The question asked at this node.",
      "state_keys": ["title", "files"],
      "allow_none": true,
      "min_prob": 0.8,
      "options": {
        "docs_only": {"description": "Observable criteria for this option.", "value": "docs"},
        "source_change": {"description": "…", "next": "surface"}
      }
    }
  }
}
```

An option with `next` recurses; one without is a leaf whose result is `value` (or
the option name). `allow_none` adds an escape option; choosing it is an abstention.

## Running it, once an environment exists

Requirements: Python 3.11+ and nothing else. A hosted key or a local server.

```bash
cd recursive_decision_models/poc
```

```bash
python3 rdm_test.py
```

```bash
python3 depth_eval_test.py
```

Hosted (TypeSafe Jev; pin the version):

```bash
RDM_MODEL=jev-1.14.0 python3 rdm.py --tree trees/pr_triage.json --state state.json --min-prob 0.8
```

Local (any `/v1/systemone` server; Ollama shown, which caps a question at 26 options).
For LM Studio behind the SSH tunnel, see the next section.

```bash
RDM_BASE_URL=http://localhost:11434 RDM_MODEL=nimble python3 rdm.py --tree trees/pr_triage.json --state state.json --max-options 26
```

Evaluation on your own labelled cases:

```bash
RDM_MODEL=jev-1.14.0 python3 depth_eval.py --tree trees/pr_triage.json --cases cases/your_cases.jsonl --flat-instructions "Which label fits this pull request?" --beam-width 3 --branch-ratio 0.5 --out report.json
```

`TYPESAFE_API_KEY` is read from the environment and sent only to `api.typesafe.ai`;
`RDM_API_KEY` is sent to whatever endpoint is in use; with neither applicable no
`Authorization` header is sent. Exit codes of `rdm.py`: 0 decided; 3 abstained,
depth or budget exceeded (a result is still printed); 2 usage or tree error; 4
backend error.

## Running through the LM Studio SSH tunnel

This is the route for the local-evaluation setup in `inference_tunnel_setup`: LM
Studio on the inference box, reached from the workstation at `localhost:<port>`
through `setup_lmstudio_tunnel_local.sh`. **The tunnel scripts need no change**,
because the server stays LM Studio and their `/api/v1/models` attestation stays
valid. Like the rest of this directory, this route has not been exercised: no tunnel
was up when it was written.

**Why it works.** LM Studio's server documents a Jev-compatible `POST /v1/systemone`
endpoint ("Decisions (System One)") that requires "a loaded decision model, not a
regular chat model" and follows the llama.cpp server's implementation. That
implementation's documented response is the shape `rdm.py` already reads
(`answers.<id>.probabilities`, `usage.input_tokens`), and it returns 400 for an
invalid request and 501 when the named model is not a decision model. LM Studio's
own page gives no response example, limits or minimum version.

**What `rdm.py` and `depth_eval.py` do for a local endpoint:**

| Behavior | Why |
|---|---|
| Base URL defaults to `LOCAL_LLM_SERVER` (after `--base-url` and `RDM_BASE_URL`) | It is the variable the tunnel prints and the benchmark manifests set |
| Model defaults to `EXPECTED_LMSTUDIO_MODEL` (after `--model` and `RDM_MODEL`) when the endpoint is loopback; with none set, exit 2 | The model sent is the model the tunnel attested. `jev-latest` means nothing to LM Studio |
| `TYPESAFE_API_KEY` is sent only to `api.typesafe.ai` | A developer with a hosted key exported must not leak it down the tunnel. Use `RDM_API_KEY` if LM Studio's API tokens are switched on |
| Proxies are disabled for a loopback host | A `localhost` tunnel exists only on this machine; a proxy would fail to reach it and would see the state |
| HTTP 501 is not retried and says the model is not a decision model | The likeliest first-run mistake is naming a chat model's key |

The only network destination is `localhost:<tunnel port>`, which is what the
benchmark sandbox's `pi_policy` already allows. Keep the host spelled `localhost`
in the URL, as the tunnel prints it; the Seatbelt rule matches that literal token.

**Steps.**

1. On the inference box, load a *decision* model in LM Studio. The llama.cpp server
   names the architectures it serves natively: `openjev`, `granite-switch`, `laya`,
   `clef`, `pplx-decider`, `vllm-decision2`, `vllm-d3`, `lfm2-d1`, `lfm2-d1-omni`,
   `h2o-lightning`. For a 128 GB Apple Silicon machine the obvious candidates are
   Clef 27B (Apache-2.0; GGUF 19.5 GB at Q4_K_M, 28.7 GB at Q8_0, 54.1 GB at BF16)
   for accuracy and Laya (421M, Apache-2.0) as a fast smoke test. Mind the licences:
   `lfm2-d1` is revenue-capped and `openjev` is non-commercial
   (`../appendices/E-local-availability.md`). Whether LM Studio's bundled llama.cpp
   runtime is recent enough for a given architecture is unverified; update it first.
2. On the inference box, list the model keys and note the decision model's:

   ```bash
   zsh setup_lmstudio_tunnel_inference.sh --check
   ```

3. On the workstation, start the tunnel with that key so it is attested:

   ```bash
   INFERENCE_SSH_TARGET=user@inference-host EXPECTED_LMSTUDIO_MODEL=<decision-model-key> zsh setup_lmstudio_tunnel_local.sh --background
   ```

4. Export the two variables, attest, and run. `rdm.py` runs no subprocess, so the
   attestation is a separate command in front of it:

   ```bash
   export LOCAL_LLM_SERVER=http://localhost:1234 EXPECTED_LMSTUDIO_MODEL=<decision-model-key>
   ```

   ```bash
   zsh /path/to/inference_tunnel_setup/setup_lmstudio_tunnel_local.sh --attest && python3 rdm.py --tree trees/pr_triage.json --state state.json --timeout 120
   ```

   ```bash
   zsh /path/to/inference_tunnel_setup/setup_lmstudio_tunnel_local.sh --attest && python3 depth_eval.py --tree trees/pr_triage.json --cases cases/your_cases.jsonl --price-per-mtok 0 --timeout 120 --out report.json
   ```

**If it fails** (`rdm.py` exit 4 prints one of these):

| Message | Likely cause |
|---|---|
| `HTTP 501 from endpoint` | The key names a chat model, or no decision model is loaded |
| `HTTP 404 from endpoint` | This LM Studio build has no `/v1/systemone` route; update LM Studio and its llama.cpp runtime |
| `HTTP 401` or `403` | LM Studio's API tokens are on; set `RDM_API_KEY` to the token |
| `HTTP 400 from endpoint` | The request was rejected: too many options for this model, or state too long for its context or batch size. Some models evaluate the whole prompt in one batch |
| `could not reach endpoint` | The tunnel is down (`--status`), or the first request timed out while the model loaded (raise `--timeout`) |
| `answer options differ from those sent` | The server is not returning the System One response shape |

**Serving from something other than LM Studio** (Ollama ≥ 0.35, `llama-server`, vLLM
Jev) needs nothing more from this PoC — same wire shape; set `RDM_MODEL` — but the
tunnel's own backend check would then fail, because it calls LM Studio's
`/api/v1/models` and reads `.models[].key`. That change belongs in
`setup_lmstudio_tunnel_local.sh` and has not been made.

## Reading a `depth_eval.py` report

| Field | Question it answers |
|---|---|
| `greedy.accuracy` vs `flat.accuracy` | Does the tree beat one flat question over all leaves? If not, the tree is only buying token savings |
| `per_depth[*].accuracy` | Which level is the weak one |
| `product_of_depth_accuracies` vs `greedy.accuracy` | Do errors compound as independent per-level errors would predict |
| `thresholds[*].coverage`, `.selective_accuracy` | What a confidence gate buys: how much is automated and how accurate that part is |
| `thresholds[*].wrong_and_decided` | The rate of confident errors — the number that matters for anything acted on automatically |
| `beam`, `ratio` | Whether exploring more than one branch earns its extra requests |
| `*.cost_per_1000_usd`, `*.latency_ms` | Cost and client-side latency per decision path |

Choose a threshold on one split of the cases and report accuracy on another. Add a
trivial baseline (keyword rule, TF-IDF classifier) and, if you can, a single LLM
call on the same cases; several published studies found a cheap baseline already
matched the decision model (`../appendices/G-prior-art-and-critiques.md`).

## Ratifying the contracts

Both trios follow the contract-plus-tests convention and stay at `v0` until:

1. the tests pass against the scripts (fix whichever of script, test or contract is
   wrong);
2. a reviewer that did not write them reviews each trio against its contract;
3. the review's findings are resolved and recorded in the contract's change log;
4. the version line and the script header are bumped to `v1`, once.

## Known gaps

- Workflows pin `actions/checkout` (v7.0.1) and `actions/cache` (v6.1.0) to the
  release commits looked up on 2026-11-12. The steps use only long-standing inputs
  (`ref`, `persist-credentials`, `path`, `key`, the `cache-hit` output), but they
  were not checked against those releases' documentation. The local workflow's image
  digest, model name and weights mount are placeholders (`REPLACE_ME`), and the
  suggested server project is archived.
- `rdm.py` does not count tokens or truncate; an oversize state surfaces as a
  backend error.
- Only the `/v1/systemone` shape is implemented. OpenAI's and Perplexity's
  `/v1/decisions` shape (`../appendices/D-cloud-availability.md`) needs a second
  backend class.
- One question per request. Batching every node into one request (cheaper where the
  vendor bills state once per request) is not implemented.
- Third-party servers' compatibility with the wire shape is their claim; none was
  tested. That includes LM Studio's `/v1/systemone`, whose own documentation shows
  no response example.
- `rdm.py` does not run the tunnel's `--attest` itself (it starts no subprocess);
  nothing stops an operator from skipping that step.
