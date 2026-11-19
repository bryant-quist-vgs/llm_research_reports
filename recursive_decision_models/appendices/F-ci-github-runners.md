---
id: F-ci-github-runners
derives_from: []
---

# Appendix F — Running a decision model in a GitHub Actions runner

Retrieved 2026-11-12. `[O]` = official GitHub docs or changelog; `[S]` = secondary
(README, blog, vendor); `[E]` = estimate made during this research. Verify the
`[O]` figures against docs.github.com before budgeting; GitHub changes them often.

## F.1 Short answer

**Yes, in three ways.**

| Design | How | Works on fork PRs? | Added time | Cost per run (private repo) |
|---|---|---|---|---|
| **A. Hosted API** from a standard runner | A step calls `/v1/systemone` with a secret key | No — forks get no secrets | ~5–30 s `[E]` | ~$0.006 runner minute + ~$0.0013 API for a 30k-token diff |
| **B. Small local model** (<= ~0.4B encoder, 1–3 GB) on the standard CPU runner | Cache weights, start a server container, call `localhost` | **Yes** — no secret needed, data stays on the runner | ~20–120 s cold start with cache hit `[E]`; 0.1–2.6 s per decision | $0.006–0.018 `[E]` |
| **C. 4B–27B model** on a GPU larger runner or self-hosted | T4 GPU runner (16 GB VRAM) or your own hardware via ARC | Self-hosted: never on public repos | 1–5 min cold start hosted `[E]` | $0.16–0.31 `[E]` on the T4 runner |

Calling a hosted API from CI is already common: a Marketplace search for "jev"
returns 32 actions. At least one published action runs a model on the runner CPU
with no key. **GitHub's own model service is not an option — GitHub Models was
retired on 2026-07-30** `[O]`.

## F.2 Runner facts

**Standard GitHub-hosted runners** `[O]`:

| Runner | Public repos | Private repos |
|---|---|---|
| Linux x64 (`ubuntu-latest`) | 4 vCPU / 16 GB RAM / 14 GB SSD | 2 vCPU / 8 GB / 14 GB |
| Linux arm64 | 4 / 16 GB / 14 GB | 2 / 8 GB / 14 GB |
| Windows | 4 / 16 GB / 14 GB | 2 / 8 GB / 14 GB |
| macOS arm64 (M1) | 3 / 7 GB / 14 GB | same |
| `ubuntu-slim` | 1 vCPU / 5 GB, 15-minute limit, no Docker-in-Docker | same |

- Price per minute `[O]`: Linux 2-core x64 $0.006; arm64 $0.005; Windows $0.010;
  macOS $0.062. Each job rounds up to a whole minute. Standard runners are free
  and unlimited on public repos.
- Included usage is now expressed in dollars per month `[O]`: Free $12, Pro $18,
  Team $18, Enterprise Cloud $300.
- Limits `[O]`: 6 hours per job on hosted runners.
- Eligible Linux jobs may land on AWS or Azure ("multi-cloud") `[O]`, so CPU models
  differ between runs — allow a tolerance on probabilities.

**Larger and GPU runners** `[O]`: Linux x64 4-core $0.012/min up to 96-core
$0.252/min. **GPU runner: one size — 4 vCPU, one Tesla T4 with 16 GB VRAM, 28 GB
RAM, 176 GB SSD; $0.052/min on Linux.** Available only to organizations on Team or
Enterprise Cloud; billed per minute even on public repos.

**Caching weights** `[O]`: `actions/cache` gives 10 GB per repository on all plans
(expandable at $0.07 per GB-month). Entries unused for 7 days are evicted. Pull
requests, including fork PRs, can read base-branch caches. Restore speed is not
documented; vendor benchmarks suggest ~10–34 s per GB `[S]`. GHCR container storage
and `GITHUB_TOKEN` pulls from Actions are currently free `[O]`, but hosted runners
keep no Docker layer cache between jobs, so an image is pulled every run. Custom
pre-baked images are larger-runner only.

**Service containers** `[O]`: Linux runners only. When the job runs directly on the
runner, steps reach the service at `localhost:<mapped port>`. Health checks are
passed as Docker options:

```yaml
services:
  decide:
    image: ghcr.io/wfzyx/von:cpu        # pin with @sha256:<digest>
    ports: ["8000:8000"]
    options: >-
      --health-cmd "<probe>" --health-interval 10s
      --health-timeout 5s --health-retries 30
```

Two practical caveats: neither Von nor Laya documents a health endpoint; and
services start *before* any step, so a cache restored by a step cannot be mounted
into a service container. Either bake the weights into the image, or start the
server with `docker run -d -v …` in a step after the cache restore and wait for it
with a retry loop.

**Self-hosted runners and ARC** `[O]`: needed for models above T4 capacity, weights
too large for the cache, air-gapped data, or a persistently warm server. No GitHub
charge. Actions Runner Controller is a Kubernetes operator that creates ephemeral
runner pods. **"Self-hosted runners should almost never be used for public
repositories"** — untrusted workflow code can persistently compromise them.

## F.3 Security: the part that decides the design

- **Fork PRs get no secrets** `[O]`. On `pull_request` from a fork, secrets are not
  passed and `GITHUB_TOKEN` is read-only (Dependabot PRs are treated the same). So
  `TYPESAFE_API_KEY` is unavailable exactly where the input is least trusted.
- **`pull_request_target` runs with secrets in the base-repo context** `[O]`.
  GitHub's guidance is to avoid it if you build or run PR code.
- **Script injection** `[O]`: pass PR titles and bodies through intermediate
  environment variables, never inline `${{ }}` in `run:`. Pin actions to full
  commit SHAs.
- **The model's input is attacker-controlled.** A diff, a PR description or a
  commit message is state, and state is the attack surface: JevAdvBench reports
  attacks flip 46.3% of correct decisions, direct task-override text flips 92.0%,
  and at a 0.8 confidence threshold 23.5% of still-executed decisions are wrong
  (Appendix B). Datadog showed a "counterfeit policy" placed in untrusted content
  cut injection-detection recall from 82.9% to 3.9% (Appendix G).

**Consequences for any CI design:**

1. A decision model in CI is **advisory** — a label, a comment, a routing hint, a
   request for human review — or one signal among several. It is never the sole
   authorizer of a merge, a deploy, or a privileged step.
2. Read the questions, options and thresholds from the **base ref**, not from the
   PR.
3. Decide the failure policy explicitly: fail open (report neutral) on API errors,
   timeouts and missing keys for advisory checks; fail closed only where a missed
   decision is worse than a blocked PR, and then pair it with a deterministic rule.
4. Asymmetric gating helps: a model may *add* scrutiny on its own say-so, but may
   *remove* scrutiny only together with a deterministic check.

## F.4 Prior art

| Project | Language / license / stars | What it does in CI |
|---|---|---|
| **Open Jev Typed Decisions** (`intikhab49/open-jev-typed-decision-engine@v1`) | Apache-2.0 / 50 | **Runs the model on the runner CPU, no key.** ModernBERT-base ~150M on onnxruntime; ~1.2 GB of ONNX weights downloaded from a GitHub release on first run, verified against `SHA256SUMS`, then cached. ~2.6 s per call on `ubuntu-latest`. Self-reported in-distribution accuracy 0.697 |
| pr-sieve (Thestral12) | MIT | `pull_request` only ("Never `pull_request_target`"); reads policy from the base ref; fork PRs without a key report `neutral`; 429/5xx/timeouts report `neutral` (fail-open) |
| getsentry/pr-risk-action | n/s | `pull_request_target` with read-only permissions; **never checks out PR code**; reads revisions into an isolated bare repo and verifies `expected-head-sha`; 10-minute timeout; "unclassified" fails an advisory job |
| Jev PR Judge (juanegido) | — | `pull_request`, no checkout, `fail-on: none` by default |
| kyu1204/jgrep + jgrep-action | TypeScript (Bun) / MIT / 62 | English lint rules over `git diff`; exit 0 match, 1 none, 2 error; the action fails closed on exit 2 |
| abhixhek/jevcal | Python / MIT / 12 | `jevcal check --lock decisions.lock.json` exits 1 on accuracy or coverage drift; `--strict` fails on a model-version change. README warns probabilities are rounded to two decimals and identical requests occasionally differ |
| Eliot5566/s1kit | Python / MIT | Action with `fail-under`; tests one suite against Jev, Laya, llama.cpp, Ollama |
| allebee/pytest-jev | Python / MIT / 8 | `jev` fixture; skips without a key; `--jev-require` makes a missing key fail CI; unsure band 0.2–0.8 |
| doeixd/jev-pref | Node 20+ / MIT / 14 | AGENTS.md preferences become checks; action with `fail-on: gates` |
| Eliot5566/JEV-Paper-Radar | Python / MIT / 41 | Daily arXiv triage on a cron workflow; ~$0.06/day |
| valentynkit/jev-commit | Python stdlib / MIT / 17 | `commit-msg` hook; pinned to `jev-1.13.0`; fails open on API errors; blocks only on a detected credential |
| Eve2512/Strayguard | Python / MIT | pre-commit hook flagging stray new files |
| ckorhonen/jev-lint | TypeScript / MIT / 19 | Edit-time hook for coding agents (not CI). Its README says local Kev/Laya are "not yet accurate or fast enough" |
| `ai-action/setup-ollama@v2` | MIT / 17 | Installs Ollama on a runner; README shows caching `~/.ollama` |

There is no official TypeSafe action.

Representative workflows from the READMEs:

```yaml
# s1kit: gate a labelled suite on pull requests
on: pull_request
jobs:
  s1kit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Eliot5566/s1kit@v0.2.0
        with: { suite: s1kit.yaml, fail-under: "0.9" }
        env: { TYPESAFE_API_KEY: "${{ secrets.TYPESAFE_API_KEY }}" }
```

```yaml
# jev-commit as a pre-commit hook; install with --hook-type commit-msg
repos:
  - repo: https://github.com/valentynkit/jev-commit
    rev: v0.1.0
    hooks: [{ id: jev-commit }]
```

## F.5 Measurements on runners

No published tokens-per-second or download timings exist for llama.cpp or Ollama
decision models on GitHub-hosted runners. The closest data, all `[S]`:

- Open Jev action: 2.6 s per call on `ubuntu-latest`.
- A community list reports, on "CPU-only CI runners": hosted Jev 164 ms; Laya via
  `laya-serve` 0.59–2.2 s with 81–95% accuracy.
- Von: 0.096 s raw p50 on a 4-vCPU Xeon with OpenVINO (not a runner).
- Hosted Jev: ~0.16–0.5 s per decision.

Private repos get 2 vCPU / 8 GB, so expect local models to be slower there than
on public-repo runners.

## F.6 Reference designs

**A. Hosted API from a standard runner.** No model cold start. Add the call as a
step in an existing job to avoid paying a separate rounded-up minute. Pin
`jev-1.13.0` or `jev-1.14.0`, never `jev-latest`; log the `model` the response
reports. Expect residual nondeterminism (0.17% re-run flips; two-decimal rounding
via some gateways) — use a dead band around thresholds and a lock file as jevcal
does. Fork PRs: skip as neutral, or use the no-checkout `pull_request_target`
pattern. See `../poc/workflows/decide-hosted.yml`.

**B. Small local model on a standard CPU runner.** Works on fork PRs under plain
`pull_request`. Restore 1–3 GB of weights with `actions/cache` (fits the 10 GB
allowance) and start a digest-pinned server image after the restore. Keep the cache
warm with a scheduled job on the default branch at least every 7 days. Pin the
Hugging Face revision SHA or release tag plus SHA256, and the image `@sha256`;
avoid unpinned `trust_remote_code`. Accuracy will be lower than hosted (~0.70 for
the Open Jev action's model; 81–95% for Laya on easy tasks) and open models are as
attackable as Jev. Keep each question to a few options. See
`../poc/workflows/decide-local.yml`.

**C. 4B–27B model on a GPU runner or self-hosted.** The T4 runner plausibly fits a
4B model and a quantized 9B; a 27B model does not fit comfortably in 16 GB `[E]`.
Weights of 5–17 GB crowd or exceed the 10 GB cache — use paid cache expansion, a
custom image, or a persistent volume on self-hosted. No published latency exists
for 4B–27B decision models on a T4. For this size class a hosted 27B model (Clef,
Perplexity Decider, Mammoth) is usually simpler than a GPU runner unless the data
cannot leave.

## F.7 Sources

docs.github.com/en/actions/reference/runners/github-hosted-runners ·
/actions/reference/runners/larger-runners · /actions/reference/limits ·
/billing/reference/actions-runner-pricing · /billing/concepts/product-billing/github-actions ·
/actions/reference/workflows-and-actions/dependency-caching ·
/actions/tutorials/use-containerized-services/use-docker-service-containers ·
/actions/reference/runners/self-hosted-runners ·
/actions/concepts/runners/actions-runner-controller ·
/actions/reference/security/secure-use ·
/actions/reference/workflows-and-actions/events-that-trigger-workflows ·
github.blog/changelog/2026-07-30-github-models-is-now-retired/ ·
github.com/marketplace?type=actions&query=jev · github.com/ai-action/setup-ollama ·
github.com/ollama/ollama/releases · and the repositories named in F.4.
