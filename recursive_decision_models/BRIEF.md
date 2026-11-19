---
id: BRIEF
derives_from:
  - A-ecosystem-inventory
  - B-academic-literature
  - C-benchmarks
  - D-cloud-availability
  - E-local-availability
  - F-ci-github-runners
  - G-prior-art-and-critiques
  - H-talk-and-vendor-patterns
---

# Recursive decision models — research brief

Research date: **2026-11-12**. This brief is written to be handed to a session that
has to answer one question: *does this technique fit a particular application?* It
is self-contained. You should not need to search the web to use it; the appendices
in `appendices/` hold the detail behind every claim here, and `poc/` holds unrun
proof-of-concept code.

**How to use it.** Read sections 1–5 to understand the technique and the state of
the evidence. Use sections 6–11 as reference for availability, cost and prior art.
Then apply section 12, which is the fit-assessment procedure and the answer format.
Do not re-research the field. If a fact you need is missing, say so in your answer
rather than guessing.

**How much to trust it.** The whole category is eight weeks old. Almost every number
comes from a preprint, a vendor, or a single practitioner, and prices and model
versions change weekly. Figures are marked where they are vendor- or
author-reported. Treat any figure as "true on 2026-11-12, re-check before
committing money or a design".

---

## 1. Bottom line

1. **"Recursive decision models" (RDM) is a design pattern from one talk, not an
   established technique.** It was proposed by Raymond Weitekamp (OpenProse) in a
   talk published 2026-11-10 and a blog post dated 2026-10-01. The reference code
   was four days old with four GitHub stars on the research date. No paper uses the
   term.
2. **The pattern:** replace an LLM's reasoning step with a tree (or loop) of small
   questions put to a *decision model* — a fast, cheap, non-generative model that
   returns a probability for each option you list. Code holds the context, lists the
   options, and decides what to ask next; a decision may lead to another decision,
   up to a depth limit; no generative model is required.
3. **The ingredient is real and widely available.** Decision models are sold by at
   least 18 hosted vendors at $0.01–$0.24 per million input tokens with free output,
   answer in roughly 0.1–0.5 s, and exist as open weights that run on a laptop.
   Against a frontier LLM they are measured at roughly 20–50x cheaper and 3–13x
   faster on classification, and several points less accurate on anything hard.
4. **The recursion is unproven.** Nobody — not the speaker, not a vendor, not a
   paper, not a benchmark — has published accuracy as a function of tree depth, or a
   comparison of a recursive tree against one flat decision or one LLM call. The
   speaker says the benchmarks "will come only after" a v1.
5. **The adjacent evidence on composing decisions is discouraging.** Errors compound
   with depth; three models with identical 67.8% single-step accuracy scored 26.5%,
   17.4% and 5.7% when their choices were executed in a loop; the one routing-tree
   experiment reached 37.6% and beam search did not help; confidence does not flag a
   mistake inherited from a parent step.
6. **Where it plausibly fits:** high-volume, latency- or cost-sensitive decisions
   over a *closed* set of outcomes that decomposes into a shallow hierarchy (2–3
   levels, a handful of options per level), where a low-confidence answer can be
   handed to a person or an LLM, the result is advisory or cheaply reversible, and
   you have labelled examples to measure it.
7. **Where it does not:** anything needing generated text or an explanation;
   arithmetic, dates, counting or multi-step state tracking; decisions whose input
   an attacker can write and whose outcome grants something; problems a single
   decision call, a trained classifier or a rule already solves.
8. **Practical recommendation for any application:** first ask whether a *single*
   decision call (or one request with several questions) does the job — that is
   well supported. Add depth only when one flat question cannot hold the options or
   a small local model needs few options per question, and then only behind a
   confidence gate, measured on your own data with `poc/depth_eval.py` or
   equivalent before anything depends on it.

---

## 2. What a decision model is

A **decision model** (also "System One model", "typed decision model", "Jev-like
model") reads a `state` — text, JSON, sometimes images — plus one or more
**questions whose possible answers the caller declares in advance**. It returns a
probability for each declared answer. It generates no text. The category was started
by **TypeSafe AI's Jev**, released 2026-09-15.

| Question type | You declare | You get back |
|---|---|---|
| **Noul** | A statement | Probability it is true |
| **Choice** | 1–255 named options, each with a description | The chosen option and a probability for every option |
| **Score** | An ordered rubric of up to 10 levels | A level and a probability for every level |
| **Box** (Jev 1.14+) | An image and a target | A location in the image |

The de facto wire shape is TypeSafe's `POST /v1/systemone`; most hosted vendors and
every local runtime accept it:

```json
{
  "model": "jev-1.14.0",
  "state": "I was charged twice for my subscription this month. Please refund the extra charge.",
  "questions": {
    "billing": {"type": "noul", "instructions": "Is this message about billing?"},
    "tone": {"type": "choice", "instructions": "What is the tone?",
             "criteria": {"angry": "…", "calm": "…", "excited": "…"}}
  }
}
```

```json
{
  "model": "jev-1.14.0",
  "answers": {
    "billing": {"type": "noul", "noul": 0.98},
    "tone": {"type": "choice", "choice": "calm", "confidence": 0.7,
             "probabilities": {"angry": 0.15, "calm": 0.8, "excited": 0.05}}
  },
  "usage": {"input_tokens": 120, "output_tokens": 12}
}
```

OpenAI and Perplexity use a different shape, `POST /v1/decisions` (`input` instead
of `state`, `questions` as an array, `predicate` instead of `noul`). Full field
rules and SDK calls are in Appendix D.3.

Properties that matter for design:

- **Several questions can ride in one request** and are answered independently; one
  answer does not influence another. State is read once, so batching is cheap.
- **A Choice always picks something.** If none of your options fits, it still
  returns one, often confidently. You must add an escape option or a companion
  yes/no question ("does any option fit?").
- **The `confidence` field is arithmetic on the probabilities**, not an independent
  estimate of being right. Gate on the probability of the option you will act on.
- **No explanation is returned.** You get numbers, not reasons.
- **Thresholds belong to a model version.** Pin an explicit version (`jev-1.14.0`,
  not `jev-latest`) and re-fit thresholds when it changes.
- **The model cannot invent an option.** Something else — code, a taxonomy, an
  application, an LLM — has to enumerate the choices.

The vendor's own guidance (TypeSafe): code owns control flow; the model makes
judgments and "your code makes the decision"; decompose into atomic questions; ask
many per request; route on uncertainty; and do **not** build agent `while` loops
around the model. Note that the last point is in tension with the talk.

---

## 3. What "recursive decision models" means

### 3.1 Source

- Talk: "Your Agent Doesn't Need an LLM for Every Decision — Raymond Weitekamp,
  OpenProse", AI Engineer YouTube channel, published 2026-11-10, 51:48. Its original
  title was "recursive decision models".
- Blog post: raw.works/recursive-decision-models/, 2026-10-01.
- Code: `github.com/rawwerks/rdm` (Rust, MIT, created 2026-11-08, 4 stars), a Python
  `dspy.experimental.RDM` on an unmerged fork branch, and in-browser demos at
  recursivedecisionmodels.com.

The name is easy to confuse with three unrelated things: Recursive Language Models
(the idea it borrows from, section 3.4), "tiny recursive models" in ML research, and
recursive decision problems in economics.

### 3.2 Definition

From the reference README: "A Recursive Decision Model (RDM) puts a decision model
in a loop. Its answers pick what happens next: a function runs, a language model
writes, or the same question is asked again about a smaller piece of the state. That
last one is the recursion." The talk's one-line version: "a decision that can decide
to make another decision."

The three rules the speaker calls non-negotiable:

1. **Externalize context.** The full context lives in code; code slices it and shows
   each question only the piece it needs.
2. **A decision may call another decision**, up to a maximum depth.
3. **It must work with no generative model at all**, and also compose with LLMs and
   agents when they are present.

The speaker contrasts two layouts. *Decision as a tool*: an agent calls a decision
model for a gate, a router or a judge — he calls this obvious, and it is what most
of the ecosystem builds. *Decision model as root*: the decision loop is in charge,
and an LLM is merely one of the options it may select. RDM is the second.

### 3.3 Mechanics

- **A node is one request**: a state slice plus typed questions, answered once.
- **Children are enumerated by code, never by the model.** A "tool" is a plain
  function that slices state and calls the module again one level down.
- **An answer selects what runs next**: a yes on a Noul, or the chosen option of a
  Choice, runs the function of the same name. Arguments are never written by the
  model: "an argument the model should choose is one more question."
- **Stopping**: no answer selects anything; an explicit `finish`; the depth limit; a
  repeated identical request; or a budget (reference defaults: depth 3, 20 loop
  turns, 256 model requests per run).
- **Thresholds are per question** (examples use 0.7 and 0.3).
- **An LLM is "a tool like any other"**: it runs only when a decision selects it and
  its output is checked by code.
- Two further concepts the speaker says are unsettled: the **map** (the set of
  named things a decision can point at, each with a description for the model and an
  object for the code) and the **arbiter** (a gate deciding which of many
  speculative parallel decisions may write to shared state; Rust only).

The clearest example is hierarchical classification over a 12,378-category product
taxonomy. Note the branching rule — follow every child at least half as likely as
the likeliest, then ask again among whatever leaves came back ("no beam width and
no path score"). This is the speaker's code with one debug `print` line removed:

```python
def classify(listing, category="All products"):
    under = taxonomy[category]
    if not under:
        return category  # a leaf
    odds = choose(listing, under)
    likely = [each for each in under if odds[each] >= max(odds.values()) / 2]
    found = [classify(listing, each) for each in likely]  # the same function, one level down
    odds = choose(listing, found)  # more than one came back: ask again, among those
    return max(found, key=odds.get)
```

It reached the expected leaf in 8 requests on **one** example. The speaker: "I am
not claiming that this is 'better' in any way."

### 3.4 Where the idea comes from

**Recursive Language Models** (Zhang, Kraska, Khattab, MIT; arXiv 2512.24601): a
long prompt is stored as a variable in a code sandbox; a root LLM writes code to
inspect and split it and calls sub-models on the pieces. It works well for very long
inputs (for example 91.3 vs 70.5 for a compaction agent on a 6–11M-token browsing
benchmark), but deeper recursion is not reliably better and the authors list error
propagation and cost blow-up as limitations.

The crucial difference: **in an RLM the model writes the decomposition; in an RDM
code does, and the model only scores options.** RDM is therefore more predictable
and cheaper per step, and strictly less capable: it can only walk paths someone
enumerated in advance.

### 3.5 What the talk showed, and what it did not

| Demo | What was shown | Evidence value |
|---|---|---|
| Handbook search by halving, and an outline walk | 15 requests each; no LLM | Illustration. Speaker: "a terrible way to actually solve this problem" |
| Product taxonomy | Expected leaf reached in 8 requests | One example |
| Factorio repair | Tree narrows failing group → line → machine, then replaces it | Speaker: "a little bit of a toy example" |
| Smart home | A map with memory got 87% of requests right vs 66% without, over a few simulated days | **The only accuracy-like number in the talk, post or code.** Toy simulation |
| Doom | Replay of TypeSafe's launch clip (~10 queries/s, ~$7/hour) | Not the speaker's work; TypeSafe says a non-AI bot could play better |
| Browser use | Claim that pre-enumerated actions "might be enough" | Based on his own slides website |

**Not shown anywhere:** latency, cost or accuracy of a tree against a single LLM
call or a single decision; any benchmark; any production use. Limitations the
speaker states himself: every option must be pre-enumerated ("there is no easy way
to generate new decisions to make"); paths are predefined; the map interface is
unsettled; runs can die retrying one command; option order biases choices; thresholds
are version-specific; and, asked what it is good for: "I don't know."

A widely shared summary of the talk (startuphub.ai) contains errors — it credits the
Doom demo to the speaker and treats his slide-site remark as a general statistic.
Details: Appendix H.

---

## 4. What the evidence supports

| Claim | Status | Basis |
|---|---|---|
| Decision models are much cheaper and faster than LLMs for picking among options | **Established** | Independent: 22–49x cheaper, ~3–13x faster than a frontier LLM on classification; median 0.12–0.39 s. An academic audit finds 30–220x faster and 29–325x cheaper than flash-tier LLM judges. The vendor's 193.6x / 444.6x claims did not replicate |
| They match frontier LLMs on accuracy | **False on hard tasks** | 6–20 points behind on contracts, judging and reasoning benchmarks; 81.0% vs 84.4% on a 77-way intent task; comparable to small and mid LLMs |
| They beat simple baselines | **Often not** | In at least four independent studies an n-gram classifier, a regex or domain rule, a fine-tuned DeBERTa, or an embedding ranker matched or beat the decision model |
| The typed interface beats reading option probabilities from an ordinary LLM | **Not shown** | The audit of 28 papers found no independent accuracy gain; the claimed benefit is calibration |
| Probabilities are calibrated enough to gate on | **Depends on the dataset** | Good on some sets (ECE 0.02), poor on others (ECE 0.09; a 0.8–0.9 bin that was 66.7% accurate). High confidence when the information is simply absent. Swapping "yes" and "no" flipped 50.5% of answers in one study |
| A confidence gate plus LLM fallback recovers frontier accuracy at lower cost | **Partly** | Independent cascades matched the frontier model at ~26–28% of its cost, with thresholds tuned on the test data. Gains are capped when the fallback shares the errors: one study found over 85% of a flash-tier LLM's verdicts repeat the decision model's most confident mistakes |
| Decisions are robust to hostile text in the state | **False** | Attacks flip 46.3% of correct decisions; an injected "task override" flips 92.0%; at a 0.8 confidence threshold 23.5% of executed decisions are still wrong. A counterfeit policy in untrusted content cut injection-detection recall from 82.9% to 3.9% |
| A tree of small decisions handles more options, more cheaply, than one flat question | **Plausible, thinly evidenced** | A synthetic test found a 3-level tree used ~7x fewer tokens than one 255-option question and scored 180/180 — but a keyword baseline also scored 180/180. Small models collapse before ~100 options, so they need trees; Jev holds accuracy to 255 options |
| Accuracy holds up as decisions are chained in depth | **Unmeasured for trees; poor in loops** | See section 5 |
| Recursive decision trees beat one LLM call | **No published comparison** | — |

Where decision models stand against each other (Appendix C): on current independent
leaderboards Jev is mid-pack (rank 67–76 of ~301 on one; 15th–18th of hosted systems
on another), and several hosted and open 27–31B models score higher. Models under 1B
parameters score near chance on hard or unfamiliar tasks and look far better on
public test sets than on private ones.

---

## 5. Composition: the central risk

This is the part a fit assessment must take most seriously, because it is exactly
what "recursive" adds and exactly what nobody has measured.

**Depth compounds error.** If each step is right with probability *p* and errors are
independent, a path of *d* steps is right with probability *p^d*:

| Per-step accuracy | 2 steps | 3 steps | 4 steps | 5 steps |
|---|---|---|---|---|
| 95% | 90% | 86% | 81% | 77% |
| 90% | 81% | 73% | 66% | 59% |
| 85% | 72% | 61% | 52% | 44% |
| 80% | 64% | 51% | 41% | 33% |

This is arithmetic, not measurement. The one published check agrees with it: a model
that is 97% right per question passed all 15 questions about a document 63% of the
time, and 0.97^15 ≈ 0.63. Real errors are correlated, which can make a tree better
or worse than the table.

**Gating trades coverage for accuracy.** Illustration from one independent
measurement (8-way classification): ungated, 83.8% per step gives about 59% over
three levels. Gate each step at 0.80 and per-step accuracy on answered items rises
to 93.8% — about 83% over three levels — but only about 52% of items clear all three
gates. The rest must go somewhere: a person, an LLM, or a safe default.

**What has actually been measured about composition:**

| Evidence | Result |
|---|---|
| System1-Arena (UT Austin, 138 closed-loop environments) | Three models with **identical 67.8% single-step accuracy** reached 26.5%, 17.4% (Jev) and 5.7% closed-loop success. Best of any model: 32.9% |
| Narrow Decision Models (arXiv 2610.25553) — the only routing-tree experiment | Greedy descent through unseen org charts: correct final unit 37.6%. **Beam search and an exhaustive sweep: 35.2%, no better** |
| Choice2Seq (arXiv 2610.16191, abstract) | A model that picks the right whole answer 97–99% of the time kept only **33.0% and 2.1%** of those when the answer had to be built from sequential local decisions |
| Sequential control in text games (arXiv 2609.37647) | Jev picks the optimal Blackjack action 90% of the time, yet solves 35% of ALFWorld tasks and repeats ineffective actions on 40–45% of steps. Authors: leave state tracking to the harness |
| Browser tasks (AIMultiple, 50 tasks) | Jev 17/50; the best decision model 43/50; a frontier LLM 47/50. Jev declared the task "blocked" in 25 of its 33 failures |
| "What Can't Jev Decide?" (arXiv 2610.24929, abstract) | 53–80% after sixteen chained updates; follows a stale summary; **confidence does not flag inherited errors** |
| TypeSafe's hierarchical cookbook | Beam matched 3 of 3 examples, greedy 2 of 3. Three examples |
| A practitioner's study (Roussos) | Errors compound silently without a checkpoint; judging items one at a time cannot enforce consistency across items |

**Reading:** static, shallow trees over a real taxonomy are the best case and are
still unmeasured. Open-ended loops (the "decision model as agent" picture) are the
worst case and are measured to be poor. Whether exploring several branches helps is
contested: one paper says no, one three-example cookbook says yes.

**Design rules that follow:**

1. Keep trees shallow (2–3 levels) and each node small (a handful of options).
2. Put a confidence gate on every node, with an explicit escape option or companion
   Noul, and decide in advance where abstentions go.
3. Do not multiply or compare probabilities from different question forms; a Choice
   is internally coherent, a set of separate Nouls is not.
4. Keep state, history and loop control in code. Never ask the model to track what
   it already tried.
5. Send each node only the state it needs. This is cheaper and also more accurate
   (long, irrelevant state degrades answers).
6. Measure end-to-end accuracy by depth on your own labelled data before relying on
   the tree; per-node accuracy is a weak proxy.

---

## 6. Availability: hosted

Decision models are easy to buy. Prices are US dollars per million **input** tokens;
**output is free at every vendor**. Full table (about 20 hosts), conflicts between
sources, and wire-shape details: Appendix D.

| Host / model | $ per M input | Limits worth knowing | API shape | Notes |
|---|---|---|---|---|
| TypeSafe **Jev** `jev-1.14.0`, `jev-1.13.0` | 0.042 | 64k tokens/request; 255 options; 10 score levels; text, JSON, images | `/v1/systemone` | The original; 71% of decision traffic on OpenRouter; closed weights; mid-pack on current leaderboards |
| Cloudflare **Clef** (27B) / **Clef-flash** (9B) | 0.24 / 0.038 | 64 questions/request; sources conflict on usable context (possibly truncated near 2K tokens) | Jev-compatible on Workers AI | Open weights (Apache-2.0); zero data retention |
| OpenAI Decisions API `gpt-6-luna` | 0.10 | Up to 400 questions | `/v1/decisions` (own shape) | ZDR and regional processing for eligible customers |
| Microsoft Foundry `Microsoft-Decision-1` | 0.042 | 32,768 tokens; text/JSON only | `/v1/systemone` under an Azure endpoint | Preview; Azure data-zone deployment |
| Perplexity `pplx-decider-v1.2` / flash | 0.02 / 0.01 | 255 options | `/v1/decisions` | Cheapest of the well-ranked models; bills state once per request |
| Liquid `d1.1` / `d1-ultra` | 0.02 / 0.042 | 33K–66K | `/v1/systemone` | d1-ultra tops an independent guardrail board |
| Nace **Drex** v1.5 / v2.0 / max | 0.04 / 0.06 / 0.06 | 131K–262K | Compatible | Drex Max leads several boards |
| Fastino **GLiDE** family | 0.01–0.04 | — | `/v1/systemone` | Near the top of independent boards |
| Fireworks `rune` | 0.042 | 256 questions; text only | Both shapes | Serverless |
| Others | 0.01–0.10 | — | Mostly compatible | Upstage, Inception, Subquadratic, Respan, Baseten, Together, MachineFi, Google (listing only), Databricks SQL function |

**Gateways.** OpenRouter exposes 22+ decision models behind one key at
`https://openrouter.ai/api/v1/systemone` (the TypeSafe SDK works with that base URL).
Vercel AI Gateway and Cloudflare also resell Jev with per-request zero data
retention. LiteLLM and TrueFoundry support both shapes.

**Not available:** AWS Bedrock, Hugging Face Inference Providers, Groq, Cerebras,
Replicate, Modal (none found); Google Vertex AI unconfirmed. **GitHub Models was
retired on 2026-07-30.**

**Integrations.** Official SDKs: Python `typesafe-sdk`, JavaScript
`@typesafe-ai/sdk` (Node 22+). First-party support in Pydantic AI (including a
built-in "below this confidence, hand off to an LLM" route), LangChain (alpha) and
the Vercel AI SDK. Community only for LlamaIndex, MCP, SQL databases. No merged DSPy
support. No official GitHub Action (about 32 community ones). Any language can call
the HTTP API directly.

**Data handling (TypeSafe).** US-hosted; states it does not train on customer
requests; no fine-tuning offered; retention period not stated; zero data retention
on request for enterprise, or per request through Vercel or Cloudflare. A SOC 2
Type II report is referenced on the enterprise page only — treat as claimed, not
verified. **Contract terms to check before use:** the customer agreement prohibits
using outputs to distill or train an imitating model and restricts publishing
performance benchmarks of the service.

**Latency.** Roughly 0.1–0.5 s per request end to end; p99 around 0.85 s; under 100
concurrent calls one study saw a few per thousand take 10–35 s.

---

## 7. Availability: local

Full model table (about 25 profiled models), runtimes and sources: Appendix E.

**Can a developer run one on their own machine? Yes.** The smallest class needs
1–5 GB of RAM and no GPU — comparable to a language server. The question is not
hardware but accuracy: the models that fit comfortably on a laptop CPU are the
weakest, near chance on hard or unfamiliar tasks and degrading beyond about 20
options per question. That weakness is the practical argument *for* a tree: keep
every node to a few options a small model can handle.

| Situation | What to run | Where |
|---|---|---|
| Prototyping, pre-commit hooks, local dev loops; nodes with ≤ ~20 options | A sub-1B model: Laya (421M, Apache-2.0), jevos (0.9B, MIT), Kev-0.8B (Apache-2.0) | **The developer's own laptop.** 1–5 GB RAM, CPU or any Apple Silicon Mac; tens to hundreds of ms |
| Better accuracy, still personal hardware | 4B–9B: Kev-4B, Nimble 9B | A 24–36 GB Apple Silicon Mac or a 16–24 GB GPU; 0.1–0.7 s. **Not usable on CPU** (seconds to a minute) |
| Team-shared service | 4B–9B on one box, or simply a hosted API | One 16–24 GB GPU machine |
| 27B-class accuracy with data kept on-premises | Clef, Kev-27B, pplx-decider-v1.1 | **Dedicated 80 GB GPU server** (A100-80/H100/H200), or a 96–128 GB Mac. Quantized Clef (19.5 GB) is marginal on a 24 GB card |
| Lowest effort and best accuracy per dollar | Hosted API | — |

Self-hosting wins only on privacy, offline use, CI without secrets, or very high
volume: a rented A100 costs about $40 per day, which buys roughly a million hosted
Jev decisions.

**Software.** Either route works with the standard wire shape:

- **Ollama ≥ 0.35** — `ollama pull nimble`, then `POST
  http://localhost:11434/v1/systemone`. Limits: 64 questions, **2–26 options per
  question**, 64 KiB body.
- **llama.cpp** — `llama serve -hf ggml-org/Kev-4B-GGUF`.
- **LM Studio** — its local server documents the same `POST /v1/systemone` for a
  loaded decision model (not a regular chat model), at `http://localhost:1234`.
- Dedicated servers: `laya-serve` (port 8000), Ollaya (port 11435), vLLM Jev,
  SGLang, `sys1` (Rust), `laya.cpp`, Laya-MLX for Apple Silicon.
- The official SDKs work against any of them by changing the base URL. Python 3.11+
  is needed only for the Python-library routes.

**Independent caution on speed:** one practitioner measured local medians 3–7x
slower than model-card claims. Re-measure on your own hardware.

**License traps.**

- **Non-commercial weights** (CC BY-NC): StartLux-Decision, OpenJev 27B, Vev.
- **Revenue cap:** Liquid's open d1 models grant commercial use only to
  organizations (including affiliates) under US$10 million annual revenue.
- **Unpublished or unclear licenses:** Together's Tev1, Nimble (repository states
  none), Strands Decider weights.
- **Distillation provenance:** models openly distilled from Jev outputs (jev-style
  2B v4, autotrust JEV-27B/9B and derivatives) may conflict with TypeSafe's
  anti-distillation clause even where their own license says Apache-2.0. Kev and
  Nimble state they used no Jev outputs. Tools that record your Jev answers to train
  a local replacement (`stuntd`) fall under the same clause.
- **Abandonment:** Von, a well-regarded CPU server, was archived three weeks after
  release. Pin model revisions and container digests.

---

## 8. Availability: GitHub Actions runners

**Yes, a decision model can run as part of a GitHub runner, in three ways.** Detail,
runner specifications, prior-art actions and security guidance: Appendix F.
Proposed workflows: `poc/workflows/`.

| Design | How | Fork PRs? | Added time | Cost per run (private repo) |
|---|---|---|---|---|
| **A. Hosted API** from a standard runner | A step calls the API with a secret key | No — forks get no secrets | ~5–30 s | ~$0.006 runner minute + ~$0.0013 for a 30k-token diff |
| **B. Small local model** (≤ ~0.4B, 1–3 GB) on the standard CPU runner | Cache weights, start a server container, call `localhost` | **Yes** — no secret, data stays on the runner | ~20–120 s cold start with a cache hit; 0.1–2.6 s per decision | ~$0.006–0.018 |
| **C. 4B–27B model** on a GPU runner or self-hosted | GitHub's T4 runner (16 GB VRAM, $0.052/min, Team/Enterprise only) or your own hardware | Never self-hosted on public repos | 1–5 min cold start | ~$0.16–0.31 on the T4 runner |

Time and cost figures in rows B and C are estimates made during this research; no
published measurement of a decision model on a GitHub-hosted runner exists beyond
one action reporting 2.6 s per call.

Facts that shape the design:

- Standard runners: 4 vCPU / 16 GB on public repositories, **2 vCPU / 8 GB on
  private** ones. Enough for a sub-1B model; too slow for 4B and up.
- `actions/cache` allows 10 GB per repository and evicts entries unused for 7 days;
  a 1–3 GB model fits, a 27B model does not.
- Service containers start before any step, so they cannot see a cache restored by a
  step; start the server with `docker run` after the restore.
- GitHub Models no longer exists, so there is no built-in model service.
- At least one published action already runs a ~150M model on the runner CPU with no
  key (~1.2 GB of weights, self-reported accuracy 0.70).

**Security rules for any CI use** (these decide the design more than cost does):

1. A pull request's title, body, commits and diff are attacker-controlled state.
   Given the adversarial results in section 4, a decision model in CI is
   **advisory** — a label, a comment, a routing hint — or one signal among several.
   It is never the sole authorizer of a merge, a deploy or a privileged step.
2. Use `pull_request`, not `pull_request_target`; never check out or run PR code in
   a job that holds a secret.
3. Read questions, options and thresholds from the **base** commit.
4. Fail open (neutral) on missing keys, API errors and timeouts for advisory
   checks; let the model *add* scrutiny on its own but *remove* scrutiny only
   together with a deterministic check.
5. Pin the model version and expect small run-to-run differences; keep a dead band
   around thresholds.

---

## 9. Prior art: projects, libraries and tooling

The ecosystem is large and very young: an academic survey counted 2,170 public
projects in Jev's first week. A paraphrased inventory of the main community
catalogue (11 hosted APIs, 43 open models, 18 runtimes, 34 SDKs, 67 applications, 41
agent tools, 26 benchmarks) is Appendix A. The table below covers what is relevant
to *composing* decisions. Stars and commit counts are as displayed on 2026-11-12;
all are free and open source unless noted; **none is mature** — almost everything is
under ten weeks old and single-maintainer.

| Project | Language | License | Stars | What it gives you |
|---|---|---|---|---|
| `rawwerks/rdm` | Rust | MIT | 4 | The talk's reference implementation: recursion, tools, depth limit, call-tree trace. Four days old |
| `rawwerks/dspy` branch `feat/rdm-v0` | Python | MIT | fork | `dspy.experimental.RDM`; not merged upstream |
| `reachjalil/jev-tree` | TypeScript | MIT | 10 | One Choice per taxonomy level, auto-partitions long lists, depth and call caps. Greedy only, no gate |
| `steven-shoemaker/hunch` | Python | MIT | 9 | Beam search over a taxonomy; classifies each answer as sure / split / unsure |
| `doeixd/discern` | TypeScript | MIT | 17 | Nested decision registries with a depth cap, explicit "uncertain" branch, near-tie detection, replayable traces |
| `solvi-ai/solvi` | Python | Apache-2.0 | 13 (1,444 commits, v1.2.0) | Tiered decide → slow path → person; hard checks override confidence; hash-chained replayable traces |
| `zjunlp/JevLoop` | TypeScript | Apache-2.0 | 25 (284 commits) | Agent loop with seven decision points; irreversible actions go to a human; replay and audit commands; falls back to a local model |
| `BillionsBobby/JevRouter` | TypeScript | MIT | 469 | Hierarchical routing across models, tools and sub-agents; abstains below threshold; signed receipts |
| `jexp/neo4jev` | Python | MIT | 185 | Beam search over graph hops |
| `gopaljigaur/decide` (pydecide) | Python | MIT | 1 | Ordered chain of backends with confidence fall-through; fits thresholds from logged outcomes |
| `AntonioCoppe/jev-harness` | TypeScript | MIT | 15 | Confidence gate, shadow mode, fixture replay |
| `AbdelStark/s1-rs` | Rust | MIT / Apache-2.0 | 1 | Typed three-way verdict: act / review / escalate |
| `typesafe-ai/system-one-adapter-python` | Python | MIT | 411 | Official shim to run the same questions against chat LLMs for comparison |
| `suraj-phanindra/wellposed` | JavaScript | MIT | 2 | Offline linter for decision requests (missing escape options and the like) |
| `abhixhek/jevcal`, `Eliot5566/s1kit` | Python | MIT | 12 / — | Threshold fitting, drift checks and CI gates on your own labelled data |
| Pydantic AI, LangChain, Vercel AI SDK | Python / TS | open source | mainstream | First-party decision-model support (LangChain's is alpha) |

Languages: TypeScript dominates tooling, Python dominates models and evaluation,
Rust has the reference implementation, C++ appears in runtimes. Cost: the libraries
are free; you pay for model calls or hardware. More libraries, CI actions, question
templates and eleven documented anti-patterns: Appendices F and G.

**No library that does recursion publishes per-level accuracy or a compounding
analysis.** The most complete gate-plus-audit designs are `solvi`, `JevLoop` and
`discern`.

---

## 10. What the academic research says

Everything is an arXiv preprint except where noted; almost all of it evaluates one
closed model version, `jev-1.13.0`. Paper-by-paper summaries: Appendix B.

- **An audit of the first 28 papers** (arXiv 2609.32160) finds most lack the obvious
  baseline (reading option probabilities from an ordinary LLM); where it exists the
  typed interface shows no accuracy gain. Jev trails stronger LLMs by 6–20 points on
  hard tasks and is never significantly behind flash-tier judges on binary rubric
  checks. Speed and cost are the clear wins. It supplies a 14-item checklist for
  evaluating any decision-model claim (reproduced in Appendix B) and notes that
  per-step accuracy is "a weak proxy for end-to-end success because errors compound".
- **A 37-dataset benchmark** (arXiv 2609.37647): Jev beats a 27B open LLM's
  probability readout on 27 datasets and is better calibrated on single questions,
  worse on multi-label yes/no. In step-by-step text games it does poorly because it
  does not track state.
- **Probability coherence** (arXiv 2609.33209): Choice probabilities are coherent by
  construction; separate yes/no probabilities for the same labels sum to 1.14 on
  average. Do not combine probabilities across question forms. Multiplying
  probabilities across calls — what a tree's path score does — was not tested.
- **Adversarial robustness** (JevAdvBench, arXiv 2609.31142 v2): figures in section
  4. The same attacks flip 34–52% of decisions on eight open models. No defense was
  evaluated. An older and widely repeated "12.1%" figure is from version 1.
- **Security decisions** (arXiv 2609.33401): good aggregate scores hide a group
  failure — Jev missed all 130 unsafe inputs that carried no explicit instruction.
  Separate allow and block thresholds automate far more than one symmetric
  threshold.
- **Narrow Decision Models** (arXiv 2610.25553): the closest paper to tree
  composition; results in section 5. Also shows flat accuracy falling with label
  count (0.953 with 4 labels, 0.701 with 77) — the motivation for trees.
- **TypedBench** (arXiv 2610.11392): the same question paraphrased moved Jev's
  accuracy between 0.708 and 0.946. Small encoders collapse before 100 options; Jev
  holds to 255.
- **ProbabilityBench** (arXiv 2610.17016): decision models dominate the
  cost-quality frontier, but the best absolute probability quality is generative.
- **Systems that embed bounded decision loops inside an LLM pipeline** report gains:
  Jev-Mem (memory retrieval; limits of depth 8, 16 attempts, 15 s held in code) and
  JevGPT (an LLM plans, Jev judges relevance: 90.48% at ~$0.67 per question vs
  77.11% at $3.08 for a ReAct agent). Both are author-reported and keep the LLM in
  charge.
- **Theory** (ICML 2026, the only peer-reviewed item): constant-depth recursion
  gives a generative model no more power than summarization; the benefit of
  recursion comes from unbounded depth. It concerns generative models and does not
  transfer directly.
- **Older literature** predicts the main findings: hierarchical classification
  suffers unrecoverable upper-level errors; selective classification formalizes the
  accuracy-coverage trade; cascades can cut cost sharply at matched accuracy when
  the stages' errors differ.

---

## 11. Benchmarks

**Benchmarks exist — more than a dozen — but none measures recursive or tree
composition.** Standings, methods and how to run them: Appendix C.

| Benchmark | Independent? | Private test set? | What it tells you |
|---|---|---|---|
| JevBench v1.8 | Yes (one maintainer) | 1,200 of 1,500 items sealed | Accuracy, calibration, speed and cost of hosted APIs; the only CPU-timed rows for small models |
| Jev Decision Index 0.4.1 | Yes | Headline score fully private | ~301 models; exposes small models that look good only on public data |
| Artificial Analysis Decision Index v2.1 | Yes | ~45% | Decision models against LLMs; includes the one 15-question conjunction test |
| Decision Models as Guardrails (raxIT) | Yes | Partly | 33 systems on guardrail checks; best decision models ~90–92 balanced accuracy |
| System 1 Decision Benchmark v5 | Yes | Sealed key | Hard reasoning-flavoured choices: best decision model 70.3%, Jev 1.14 54.0%, a no-reasoning LLM 81.6% |
| System1-Arena | Yes (UT Austin) | — | Closed-loop composition loss (section 5) |
| AIM-Decision (AIMultiple) | Publisher | Mostly withheld | Browser tasks and 1,655 classification items across 62 models |
| TypedBench, ProbabilityBench, JevAdvBench | Yes (academic) | — | Wording sensitivity, probability quality, adversarial robustness |
| OpenRouter Banking77 | Router | No | Jev 81.0% at 175 ms and $0.11 per 1,000 vs Claude Opus 5 84.4% at 2,266 ms and $2.42 |

Tools for measuring on your own data: `jevcal` (per-question thresholds and drift
checks), `s1kit` (one suite against several servers, with a CI action),
`pytest-jev`, `wellposed` (request linter), and the unrun `poc/depth_eval.py` in
this directory, which targets the gap: accuracy by depth, coverage against
confidence, and tree versus flat versus beam.

Still unmeasured anywhere: accuracy by tree depth; whether a path probability is
calibrated; cost and latency of chained calls; CPU latency on standard hardware;
adversarial robustness inside a composed pipeline.

---

## 12. Fit assessment: how to judge a use case

You have been given a use case. Work through this section and answer in the format
of 12.6. Keep three questions separate, because they have different answers:

- **(a) Does a decision model fit at all** — as opposed to an LLM, a trained
  classifier, or rules?
- **(b) If so, does it need composition**, or does one call (possibly with several
  questions) do the job?
- **(c) If it needs composition, which shape** — a static tree, a cascade with
  escalation, or a loop?

### 12.1 Preconditions for (a): a decision model at all

All must hold. If one fails, a decision model is the wrong tool for that part.

| # | Precondition | Fails when |
|---|---|---|
| P1 | The output is a pick, a yes/no or an ordinal score over answers **known before asking** | The output is text, code, a plan, an extraction of unknown values, or an explanation |
| P2 | The judgment can be made from the supplied state by reading, not computing | It needs arithmetic, counting, date comparison, multi-hop inference, or tracking changes over many steps |
| P3 | A wrong answer is tolerable, catchable or cheaply reversible, and a "not sure" path exists | The decision is final and unreviewed, or there is nowhere to send abstentions |
| P4 | The decision is not the sole security or authorization control, **or** nobody hostile can write into the state | Untrusted text (user input, PR content, web pages, emails, tool output) reaches the state and the outcome grants access, money, a merge or a deploy |
| P5 | Labelled examples exist or can be produced (a few hundred) | Correctness cannot be checked, so thresholds cannot be fitted and regressions cannot be seen |

### 12.2 Is a decision model better than the alternatives?

| Alternative | Prefer it when |
|---|---|
| **Rules / code** | The criterion can be written exactly. Always use code for what code can decide |
| **Trained classifier** (TF-IDF + logistic regression, fine-tuned encoder) | The label set is stable and you have thousands of labelled examples. Repeatedly matches or beats zero-shot decision models, and is cheaper still |
| **Single LLM call** | Volume is low enough that cost and latency do not matter, the task is hard, or you need reasons |
| **Decision model** | Labels are scarce or the option set changes often (zero-shot matters); volume is high or latency must be sub-second; you want probabilities to route on; you are currently paying an LLM only to pick among options |

A decision model's advantage over an LLM is cost and speed, not accuracy. If the
application has neither a cost problem nor a latency problem, the case is weak.

### 12.3 Does it need composition? (b)

Use **one request** when a single question, or several independent questions
answered together and combined in code, covers the decision. This is the
well-supported use and should be the default. Vendor-documented single-request
patterns: screen with a yes/no before an expensive stage; a companion yes/no asking
whether any option fits; per-action thresholds; weighted combination of several
scores in code.

Consider **composition** only when at least one of these is true:

- The options do not fit one question: more than the model's cap (255 hosted; 26 on
  Ollama; about 20 before small local models degrade), or so many that flat accuracy
  drops (measured: 4 labels 0.953 → 77 labels 0.701 on one model).
- The option list is large and the state is small, so a tree sends far fewer
  option descriptions per request.
- Later questions genuinely depend on earlier answers (the options at step 2 are
  defined by the choice at step 1) and cannot be asked speculatively in one batch.
- Different steps need different slices of a large state.

If none holds, the answer to (b) is "no recursion needed", and that is a useful
finding, not a failure.

### 12.4 Which shape? (c)

| Shape | Evidence | Use when |
|---|---|---|
| **Static tree** over an existing hierarchy (taxonomy, org chart, decision table), 2–3 levels | Unmeasured but the best case; cost and token arithmetic is favourable | The hierarchy already exists and its levels are meaningful to a reader |
| **Cascade**: decision model first, escalate low-confidence items to an LLM or person | Best-supported composition: independent studies match frontier accuracy at ~26–28% of the cost | You already use an LLM and want to cut its cost, and can tolerate matching rather than beating it |
| **Speculative batch**: ask every node's question in one request, walk the answers in code | Vendor-documented; state is billed once at vendors that bill per request | The tree is small (tens of nodes) and the vendor's question limit allows it |
| **Loop / agent** with the decision model in charge | Measured to be poor (section 5); vendor advises against | Only for experiments, with code-enforced budgets, loop-breakers and a human or LLM checkpoint |

### 12.5 Signals to weigh

**For:**

- Tens of thousands of decisions a day or more, or a hard latency budget under ~1 s.
- An LLM is currently used only to route, classify, gate or rank.
- The domain has a natural shallow hierarchy with few options per level.
- Abstention has an obvious destination (human queue, LLM, safe default).
- A probability trail per decision would help audit or tuning.
- Must run without secrets, offline, or with data kept local (points to a small
  local model, which in turn points to small nodes).

**Against:**

- A flat choice among fewer than ~20 options already works — use one call.
- More than 3 levels deep with no abstention path.
- The same large state must be re-read at every level (cost multiplies by depth and
  accuracy drops with irrelevant context).
- Consistency *across* items matters (naming conventions, deduplication, "treat
  these the same as last time").
- Option definitions overlap, or cannot be stated as observable criteria.
- The people consuming the decision need a reason, not a probability.
- Cost and latency of the current solution are already acceptable.

### 12.6 Required answer format

Answer every use-case assessment in this shape, so that assessments can be compared:

```markdown
## <Use case name>

**Verdict:** one of
  - Fit — pilot it
  - Possible fit — pilot with a named risk
  - Decision model yes, recursion no
  - Poor fit
  - Not enough information

**The decision being made:** <one sentence: from what state, to which outcomes>

**Preconditions (12.1):** P1 … P5, each pass / fail / unknown with one line of why.

**Why a decision model rather than rules, a classifier or an LLM (12.2):** <2–4 lines,
or "it is not better because …">

**Composition (12.3–12.4):** needed / not needed, and which shape. If a tree:
proposed levels, options per level, where abstentions go.

**Expected economics:** decisions per day, tokens of state per node, depth →
estimated cost per 1,000 and latency (section 13), against the current solution.

**Main risks:** the 2–4 failure modes from section 14 that apply, each with its
mitigation.

**Deployment:** hosted / local / CI, suggested model class, license or data-handling
issue if any.

**What would have to be measured in a pilot, and the pass bar:** <metrics from 12.7>

**Unknowns:** facts about the use case that would change this verdict.
```

Be willing to answer "Decision model yes, recursion no" and "Poor fit". Given the
evidence, those will be the right answers for many use cases.

### 12.7 Pilot protocol

When the verdict is a pilot, this is the minimum that makes the result trustworthy.
`poc/depth_eval.py` (unrun) implements steps 4–6 for a static tree.

1. **Collect at least a few hundred labelled cases** from real traffic, including
   cases that fit no option. Record the correct leaf and, for a tree, the correct
   option at each level. Split into a tuning set and a held-out set.
2. **Write options as observable criteria**, not label words. Add an escape option
   or companion yes/no at every node where "none of these" is possible. Lint for
   missing escapes.
3. **Pin the model version.** Send each node only the state it needs.
4. **Measure, on the held-out set:** end-to-end accuracy; accuracy at each depth
   given a correct prefix; and the product of the per-depth accuracies beside the
   end-to-end figure.
5. **Sweep the confidence threshold** and record, at each value: coverage (share
   decided), accuracy on the decided share, and the share that is *decided and
   wrong*. Choose thresholds on the tuning set only.
6. **Run the baselines on the same cases:** one flat question over all leaves; a
   trivial model (keyword rule or TF-IDF classifier); the current solution or one
   LLM call; optionally beam search and the talk's branch-ratio rule.
7. **Record cost per 1,000 and p50/p95 latency** for each.
8. **If input can be hostile,** add cases with instructions, fake policies and
   irrelevant opinions embedded in the state, and report how many decisions flip.
9. **Run in shadow mode first** — log decisions without acting on them — before
   anything depends on the output.

A pilot passes when, at the chosen threshold, the decided-and-wrong rate is within
what the application tolerates, coverage is high enough to be worth the plumbing,
the tree beats or matches the flat question and the trivial baseline, and total cost
including escalations is below the current solution. The owner of the application
must set those numbers; this brief cannot.

---

## 13. Cost and latency model

**Single decision.** Cost per 1,000 decisions = tokens per request × price per
million ÷ 1,000. Output is free. At Jev's $0.042: about $0.02 for 500 tokens, $0.13
for 3,000 tokens, $1.26 for 30,000 tokens. For scale, the same 3,000-token input
costs about $2.25 per 1,000 through a flash-tier LLM at $0.75 per million and about
$30 through a frontier LLM at $10 per million, before output tokens.

**A tree re-sends state at every level.** Cost per 1,000 root-to-leaf paths ≈ depth
× the single-request figure, plus escalations:

| Model | 3,000-token state, depth 3 / 4 | 30,000-token state, depth 3 / 4 |
|---|---|---|
| Jev ($0.042) | $0.38 / $0.50 | $3.78 / $5.04 |
| Perplexity Decider v1.2 ($0.02) | $0.18 / $0.24 | $1.80 / $2.40 |
| OpenAI Decisions ($0.10) | $0.90 / $1.20 | $9.00 / $12.00 |
| Clef 27B ($0.24) | $2.16 / $2.88 | $21.60 / $28.80 |

Three things change the arithmetic:

1. **Option descriptions are tokens.** When the option list is long and the state
   is short, a tree is *cheaper* than one flat question (one synthetic test: ~7x
   fewer tokens). When the state is long and options are few, a tree is depth-times
   more expensive.
2. **Per-node state slicing** removes most of the multiplier if each node needs only
   part of the state.
3. **Batching all nodes into one request** reads state once at vendors that bill per
   request, at the price of asking every node whether or not its parent chose it. A
   branching-3 tree has 13 internal nodes at depth 3 and 40 at depth 4.

**With a gate and escalation,** total cost per 1,000 ≈ tree cost + (1 − coverage) ×
1,000 × cost of one escalation. With 50% coverage and a $0.03 LLM call, escalations
($15 per 1,000) dwarf the tree; the saving is whatever share of LLM calls the tree
avoided.

**Latency.** A hosted request is roughly 0.1–0.5 s, so a sequential path of depth
*d* is roughly *d* × 0.2–0.4 s, with a long tail under high concurrency. Sibling
branches can run in parallel. A frontier LLM call is 1–3 s without reasoning and far
longer with it. A depth-4 sequential tree therefore has roughly the latency of one
fast LLM call — the speed advantage shrinks as depth grows. Local sub-1B models
answer in tens to hundreds of milliseconds without a network hop.

---

## 14. Failure modes

Consolidated from the independent critiques and papers (Appendices B and G).

| # | Failure mode | Mitigation |
|---|---|---|
| 1 | **Depth compounds error; gating trades coverage for accuracy** | Shallow trees; gate every node; measure end to end |
| 2 | **Confidence does not see upstream errors**: a child given a wrong parent result answers confidently | Checkpoints; do not treat a confident leaf as validating its path |
| 3 | **Escalation has a low ceiling** when the fallback model shares the errors | Escalate to something different in kind (a stronger model with reasoning, a rule, a person) |
| 4 | **Calibration is dataset-dependent**; confidence is meaningless when the information is absent | Fit thresholds per question on your data; pin the model version |
| 5 | **No escape option**: forced, confident wrong picks on inputs that fit nothing (36% at ≥ 0.9 confidence in one test) | Escape option or companion yes/no on every node |
| 6 | **Too many or overlapping options**: 77-way ~76–81%, 135-way 68.6%, a 12-way task at 40% | Fewer options per node; observable criteria; this is the legitimate reason for a tree |
| 7 | **State is an attack surface** | Advisory use only on untrusted input; never the sole authorization; pair with deterministic checks |
| 8 | **Wording and order sensitivity**: paraphrase moved accuracy 0.708–0.946; a yes/no swap flipped half of answers; the model leans to the first option | Test paraphrases and reorderings; freeze wording with the threshold |
| 9 | **No cross-item consistency or house conventions** | Make rulings once in code or a lookup and read them back |
| 10 | **Computation, dates, counting, multi-step state** | Do it in code; extract parts with a Choice and compare in code |
| 11 | **A cheaper baseline already wins** | Always run a trivial baseline in the pilot |
| 12 | **Self-steering loops are unevaluable**: one injected line changes every later step | Fixed-step pipelines; shadow mode; one team removed its decision-model router after a week because only ~5% of suggestions were followed and the effect could not be attributed |
| 13 | **No explanations** | Log the per-node probabilities as the audit trail; keep an LLM or a person for cases needing reasons |
| 14 | **Ecosystem churn**: weekly price and version changes, archived projects, unclear licenses | Pin versions and digests; prefer the HTTP wire shape over any one library; check licenses (section 7) |

---

## 15. What would change this assessment

- A published measurement of accuracy against depth for a recursive tree, or a
  head-to-head of tree versus flat versus LLM — from the speaker (who has promised
  benchmarks after a v1), a vendor or a paper.
- A defense against in-state adversarial text that holds up independently.
- A decision model that closes the accuracy gap to frontier LLMs on hard tasks while
  keeping the price.
- Your own pilot: on a specific application, measured numbers outrank everything in
  this brief.

---

## 16. Glossary

| Term | Meaning |
|---|---|
| Decision model, System One model, typed decision model (TDM) | A non-generative model returning probabilities over caller-declared answers |
| Jev | TypeSafe AI's decision model; the first and most used |
| State | The content a decision is about (text, JSON, images) |
| Noul / Choice / Score / Box | Question types: yes-no probability / pick one option / ordinal level / image location |
| Criteria | The descriptions attached to options or score levels |
| `/v1/systemone` | TypeSafe's wire shape, the de facto standard; `/v1/decisions` is OpenAI's variant |
| RDM | Recursive decision model: the talk's pattern of decisions that lead to further decisions |
| RLM | Recursive Language Model: the earlier idea in which an LLM writes code to split its own context and call sub-models |
| Map | In the talk, the set of named things a decision can point at |
| Arbiter | In the talk, a gate over which parallel decisions may write to shared state |
| Greedy descent | Follow the most probable option at each node |
| Beam search | Keep the best *k* partial paths by joint probability |
| Branch ratio | The talk's rule: follow every option at least half as likely as the top one, then ask again among the leaves found |
| Confidence gate | Act only when the chosen option's probability exceeds a threshold; otherwise abstain |
| Escape option / companion Noul | An explicit "none of these", or a separate yes/no asking whether any option fits |
| Cascade | Cheap model first; escalate uncertain items to a stronger model or a person |
| Coverage | Share of items the system decides rather than abstains on |
| Selective accuracy | Accuracy on the items it did decide |
| ECE | Expected calibration error: how far stated probabilities are from observed accuracy (lower is better) |
| Shadow mode | Running the system and logging its decisions without acting on them |

---

## 17. Where the detail is

| Appendix | Contents |
|---|---|
| `appendices/A-ecosystem-inventory.md` | Paraphrased inventory of the community catalogue: every hosted API, open model, runtime, SDK, application and tool |
| `appendices/B-academic-literature.md` | Paper-by-paper summaries, the 14-item evaluation checklist, what is and is not established |
| `appendices/C-benchmarks.md` | Each benchmark's design, standings and how to run it; tooling for your own data |
| `appendices/D-cloud-availability.md` | Full vendor table, wire shapes with examples, SDKs, integrations, data handling, cost tables, unresolved conflicts between sources |
| `appendices/E-local-availability.md` | Model-by-model hardware, runtimes and commands, what fits where, license traps |
| `appendices/F-ci-github-runners.md` | Runner specifications and prices, caching, security guidance, prior-art actions, reference designs |
| `appendices/G-prior-art-and-critiques.md` | Composition libraries, question templates and anti-patterns, independent critiques, consolidated failure modes |
| `appendices/H-talk-and-vendor-patterns.md` | The talk in detail, the speaker's code, TypeSafe's official patterns and stated failure modes, `jev-tree` |
| `poc/` | Unrun proposals: a tree runner, an accuracy-by-depth evaluation harness, an example tree, two CI workflows |
