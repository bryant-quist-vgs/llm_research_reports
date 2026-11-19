---
id: D-cloud-availability
derives_from: []
---

# Appendix D — Cloud / hosted availability

Retrieved 2026-11-12. `[O]` = the vendor's own page; `[R]` = router or marketplace
listing (OpenRouter, Vercel); `[S]` = secondary source. Prices are US dollars per
million **input** tokens; **output is free at every vendor listed** because a
decision model emits no text. Prices and limits in this market are changing weekly;
re-check before committing.

## D.1 Short answer

Decision models are widely available as hosted APIs: at least 18 vendors, most
reachable through one key at OpenRouter. Prices cluster at **$0.01–$0.24 per
million input tokens** — one to three orders of magnitude below LLMs. Two API
shapes exist: TypeSafe's `POST /v1/systemone` (the de facto standard, implemented
by most vendors and all local runtimes) and OpenAI's `POST /v1/decisions`
(different field names; also used by Perplexity).

## D.2 Vendor comparison

| Host / model | Model ids and size | Weights | $ per M input | Context and limits | API shape | Status |
|---|---|---|---|---|---|---|
| **TypeSafe Jev** (direct) | `jev-1.14.0` (= `jev-latest`), `jev-1.13.0`; size undisclosed | Closed | 0.042 `[O]` | 64k/request, 32k/question; 262k with a long-context header (slower, less accurate); Choice 1–255 options; Score 1–10 levels; text, JSON, PNG/JPEG | `POST https://api.typesafe.ai/v1/systemone` | Self-serve keys; site says "early access" |
| **Cloudflare Clef** | `@cf/cloudflare/clef`, 27B | Open, Apache-2.0 | 0.24 `[O]` | 65,536 documented (but see conflicts); 1–64 questions; 4 images | Jev-compatible body on Workers AI | GA |
| **Cloudflare Clef-flash** | `@cf/cloudflare/clef-flash`, 9B | Open, Apache-2.0 | 0.038 `[O]` | ~25K `[R]` | same | GA |
| **Cloudflare Clef-omni** | 30B MoE (3B active) | Open | 0.15 `[O]` | 66K `[R]`; adds audio/video | same | Released 2026-10-09 |
| **OpenAI Decisions API** | `gpt-6-luna` | Closed | 0.10 uncached `[O]` | 1–400 questions; Score 2–10 levels; ~1M context `[R]` | **Own shape:** `POST /v1/decisions` | GA per guide |
| **Microsoft Foundry** | `Microsoft-Decision-1` (9B post-train) | Closed | 0.042 `[R]` | 32,768; text/JSON only | `<endpoint>/providers/microsoft/v1/systemone` | Preview |
| **Perplexity** | `pplx-decider-v1.2` (27B), `pplx-decider-flash-v1.2` (4B) | v1.1 open (Apache-2.0); v1.2 closed | 0.02 / 0.01 `[O]` | < 256K; Choice 1–255; 8 images/question | `POST /v1/decisions` with `state`/`questions` | — |
| **Liquid AI** | `d1.1`, `d1-ultra` hosted | Hosted closed; d1-3B and d1-omni-600M open | 0.02 / 0.042 `[O]` | 33K–66K `[R]` | `/v1/systemone` | `liquid/d1` retires 2026-11-20 |
| **Upstage** | `solar-decide`, `solar-decide-flash` | Closed | 0.10 direct `[O]`; 0.05 on OpenRouter | 512K; text only | `/v1/systemone` | Beta |
| **Inception** | `mercury-decide` (+ `:free` route) | Closed | 0.02; free route `[R]` | 66K | `/v1/systemone` | — |
| **Nace AI Drex** | `drex-v1.5` (9B), `drex-v2.0` (35B MoE), `drex-max` | Closed on API | 0.04 / 0.06 / 0.06 `[R]` | 131K–262K | System One compatible | — |
| **Subquadratic** | SubQ Snap 1.2 | Closed | 0.04; 100M free tokens for new users `[O]` | 384K; multimodal | n/s | Limited preview |
| **Respan** | `span-02`, `span-01`, `span-01-lite` | span-02 open | 0.01; lite free `[R]` | 131K | `/api/v1/decisions`, System One body | — |
| **Fastino** | `GLiDE`, `GLiDE-2B`, `GLiDE-0.8B` | n/s | 0.04 / 0.02 / 0.01 `[O]` | n/s | `POST api.fastino.ai/v1/systemone` | — |
| **Fireworks** | `rune` (26B-A4B) | n/s | 0.042; cached 0.0084 `[O]` | 262K; 256 questions; text only | System One and Decisions routes | Serverless since 2026-10-27 |
| **Baseten** | Elephant 1 (9B), Mammoth 1 (27B); Decision 2.0 Kai dedicated | Kai Apache-2.0 | 0.035 / 0.10 `[R]` | 16K; Kai 8,192 | System One | — |
| **MachineFi** | `trio-spark` v1.4 | Closed | 0.042; 100 free decisions `[O]` | **1,024 tokens**; 2–8 choices | Own shape | Live |
| **Together AI** | `tev1-4b-experimental` | License pending | 0.042 `[R]` | 33K; 2–24 options | Chat completions returning a letter | Experimental |
| **Google** | `gemini-decision-1` | Closed | 0.10 `[R]` | 262K; 255 options | "Decisions API" | Listed 2026-11-11; no Google page found |
| **Databricks** | `ai_decide` SQL function | Apache-2.0 models | n/s | — | SQL | Beta |

**Gateways that resell several of the above:**

- **OpenRouter** — `POST https://openrouter.ai/api/v1/systemone` (TypeSafe shape;
  the TypeSafe SDK works with base URL `https://openrouter.ai/api`) and an alpha
  `POST /api/alpha/decisions`. "22 decision models from 13 makers as of October
  16"; a third party counts 31. Usage for the week of 2026-11-02: Jev 1.13 897M
  requests, Jev 1.14 561M, Perplexity Decider v1.2 274M; **TypeSafe holds 71.1% of
  decision requests.** An agent skill exists (openrouter.ai/skills/openrouter-decisions).
- **Vercel AI Gateway** — `typesafe-ai/jev` at $0.042, 32,000 context; per-request
  zero data retention; also lists `microsoft/microsoft-decision-1`.
- **Cloudflare** — also lists `typesafe/jev` as a third-party model at $0.042,
  32,000 context, zero data retention.
- **LiteLLM** and **TrueFoundry** — gateway support for `/v1/decisions` and
  `/v1/systemone` `[S]`.

**Not available (as far as could be determined):** AWS Bedrock (Amazon's own
Strands Decider 2B is open weights to run yourself); Hugging Face Inference
Providers (Clef "isn't deployed by any Inference Provider"); Groq, Cerebras,
Replicate, Modal (none found — absence of evidence only); Google Vertex AI
(unconfirmed). **GitHub Models was retired on 2026-07-30** and is not an option.

## D.3 Wire shapes

**TypeSafe `/v1/systemone`** (the shape the PoC in `../poc/` targets). Auth:
`Authorization: Bearer $TYPESAFE_API_KEY`. Image input requires the header
`TypeSafe-Danger-Zone-Images: true`; long context requires
`TypeSafe-Danger-Zone-Long-Context: true`. Errors: `400` `{"detail": ...}`, `422`
validation, `429` rate limit.

```json
{
  "model": "jev-latest",
  "state": "I was charged twice for my subscription this month. Please refund the extra charge.",
  "questions": {
    "billing": {"type": "noul", "instructions": "Is this message about billing?"},
    "tone": {"type": "choice", "instructions": "What is the tone?",
             "criteria": {"angry": "…", "calm": "…", "excited": "…"}},
    "urgency": {"type": "score", "instructions": "How urgent is this?",
                "criteria": ["Can wait", "Needs attention this week", "Needs attention today"]}
  }
}
```

```json
{
  "model": "jev-1.14.0",
  "answers": {
    "billing": {"type": "noul", "noul": 0.98},
    "tone": {"type": "choice", "choice": "calm", "confidence": 0.7,
             "probabilities": {"angry": 0.15, "calm": 0.8, "excited": 0.05}},
    "urgency": {"type": "score", "score": 1.7, "confidence": 0.55,
                "legend": {"0": "Can wait", "1": "Needs attention this week", "2": "Needs attention today"},
                "probabilities": {"0": 0.1, "1": 0.1, "2": 0.8}}
  },
  "usage": {"input_tokens": 120, "output_tokens": 12}
}
```

Field rules: `questions` is an object keyed by names you choose; each has `type`
(`noul` | `choice` | `score` | `box`) and `instructions`. Choice `criteria` maps
option name → description (1–255 entries; a missing description means the option is
judged by its name). Score `criteria` is an ordered array (position = level,
starting at 0). Noul `criteria` is optional `{"true": …, "false": …}`. `box`
(image localization) needs Jev 1.14. The response `model` names the versioned model
that actually answered. `GET /v1/models` lists aliases.

**Official SDKs.** Python: `pip install typesafe-sdk`; `TypeSafeClient` /
`AsyncTypeSafeClient`; `client.system_one(state=..., questions={"billing":
Noul(instructions="…")})`; results at `response.nouls["billing"].noul`,
`response.choices["tone"].choice`, `response.scores["urgency"].score`.
JavaScript/TypeScript: `npm install @typesafe-ai/sdk` (Node 22+);
`client.systemOne({...})`; helpers `choice()`, `noul()`, `score()`, `box()`,
`image()`. Both retry 429s by default. Any other language can call the HTTP API
directly. Community SDKs exist for Go, Rust, Ruby, PHP, Elixir, Swift, Kotlin,
.NET, Scala and C++ (Appendix A).

**OpenAI `/v1/decisions`** (different names: `input` not `state`; `questions` is an
array; `predicate` not `noul`; `choices` with `value`/`description`):

```json
{
  "model": "gpt-6-luna",
  "input": "I was charged twice for my order.",
  "questions": [{
    "type": "choice",
    "name": "department",
    "instructions": "Which department should handle this complaint?",
    "choices": [
      {"value": "billing", "description": "Payments, invoices, and refunds."},
      {"value": "technical", "description": "Problems using the product."},
      {"value": "other", "description": "Requests outside these categories."}
    ]
  }]
}
```

**Vercel AI SDK** (`pnpm add ai @ai-sdk/typesafe-ai`; note the function is named
`experimental_decide` on the provider page and `experimental_evaluate` in an
earlier changelog, and uses type `boolean` rather than `noul`):

```ts
import { experimental_decide } from 'ai';

const result = await experimental_decide({
  model: "typesafe-ai/jev",
  state: 'I was charged twice. Please refund the duplicate.',
  questions: {
    requestsRefund: { type: 'boolean', instructions: 'Is the customer requesting money back?' },
  },
});
console.log(result.answers.requestsRefund.probability);
```

## D.4 Integrations

| Integration | Status |
|---|---|
| Pydantic AI | First-party. `pydantic_ai.models.system_one.SystemOneModel` talks to any `/v1/systemone` server (incl. Ollama >= 0.35); `TypeSafeModel`; `decision_route_threshold` raises a hand-off that `ModelFallback` can pass to an LLM — built-in confidence-gated escalation |
| LangChain | First-party, alpha: `langchain-typesafe` (`TypeSafeClassifier`), experimental router and auto-mode middleware |
| Vercel AI SDK | First-party provider `@ai-sdk/typesafe-ai` |
| LlamaIndex | Community only (`llama-index-jev`: reranker and router) |
| DSPy | No merged support found; the talk's author maintains an experimental `dspy.experimental.RDM` on a fork branch |
| Claude Code / coding agents | Official TypeSafe skill: `claude plugin marketplace add typesafe-ai/skills` then `claude plugin install typesafe@typesafe-ai`; or `npx skills add typesafe-ai/skills --skill typesafe-ai` |
| MCP | No official TypeSafe MCP server; community servers exist (jkudish/jev-mcp, System One Connector) |
| Databases | Community: sqlite3-jev, pg-jev, jevql (SQL functions over rows) |
| GitHub Actions | No official action; ~32 community actions on the Marketplace (Appendix F) |
| Comparison shim | Official `system-one-adapter` (`pip install system-one-adapter`): a drop-in client backed by LLM APIs, for running the same questions against chat models |

## D.5 Data handling and compliance (TypeSafe)

- Hosted in the United States; EU SCCs and UK addendum cover transfers.
- "Jev is not trained on customer requests or responses"; no per-customer
  fine-tuning ("the same weights serve every account"). No fine-tuning is offered.
- Retention period is not stated ("as long as reasonably necessary"). Zero data
  retention is available to enterprise customers on request; per-request ZDR is
  available through Vercel AI Gateway and Cloudflare.
- Certifications: the enterprise page points to a Trust Center "to request access
  to the SOC 2 Type II report"; the privacy policy and DPA name no certifications;
  ISO and HIPAA are not mentioned. Treat SOC 2 as claimed-but-unverified.
- Sub-processors are listed at trust.typesafe.ai/subprocessors (not readable
  during research).
- Rate limits are per organization, in tokens/second and requests/second, shown in
  the console; third-party reports cite 250,000 tokens/s and 1,200 requests/min as
  standard.
- **Contract terms to know:** the Master Customer Agreement prohibits using output
  to distill or train an imitating model or to build a competing product, and
  restricts publishing performance benchmarks of the service.

Other vendors: Cloudflare states zero data retention for Clef and no training on
requests outside its fine-tuning product. OpenAI offers ZDR and HIPAA for eligible
customers and regional processing in the US and Europe. Microsoft-Decision-1
deploys as `GlobalStandard` or `DataZoneStandard` under Azure's terms.

**Fine-tuning as a service:** Cloudflare (hands-on service now; self-serve planned;
method "RLCD"; no price). Liquid's open models are fine-tunable. TypeSafe: none.

## D.6 Cost model

Cost per 1,000 decisions = tokens per decision x price per million / 1,000. One
question per request, list prices, no caching.

| Option ($/M) | ~500 tokens | ~3,000 tokens | ~30,000 tokens |
|---|---|---|---|
| Jev — direct, OpenRouter, Vercel, Cloudflare (0.042) | $0.021 | $0.126 | $1.26 |
| Microsoft-Decision-1 (0.042) | $0.021 | $0.126 | $1.26 |
| Clef 27B (0.24) | $0.12 | $0.72 | $7.20 |
| Clef-flash 9B (0.038) | $0.019 | $0.114 | $1.14 |
| OpenAI gpt-6-luna decisions (0.10) | $0.05 | $0.30 | $3.00 |
| Perplexity Decider v1.2 (0.02) | $0.01 | $0.06 | $0.60 |
| Perplexity Decider Flash (0.01) | $0.005 | $0.03 | $0.30 |
| Respan Span-02 (0.01) | $0.005 | $0.03 | $0.30 |

For scale, at the LLM input prices AIMultiple recorded in September 2026 the same
3,000-token decision costs about $2.25 per 1,000 through Gemini 3.8 Flash ($0.75/M)
and about $30 per 1,000 through GPT-6 Astra ($10/M), before output tokens. Measured
head-to-heads put decision models at 22x–49x cheaper than a frontier LLM on
classification (OpenRouter, AY Automate; Appendices C and G).

**A recursive tree re-sends state at every level.** Cost per 1,000 root-to-leaf
traversals ≈ depth x the single-decision figure:

| Option | 3,000-token state, depth 3 / 4 | 30,000-token state, depth 3 / 4 |
|---|---|---|
| Jev | $0.38 / $0.50 | $3.78 / $5.04 |
| Clef 27B | $2.16 / $2.88 | $21.60 / $28.80 |
| OpenAI (uncached) | $0.90 / $1.20 | $9.00 / $12.00 |
| Perplexity Decider v1.2 | $0.18 / $0.24 | $1.80 / $2.40 |

Three things change this arithmetic:

1. **Option descriptions are tokens too.** A flat 255-option question carries all
   255 descriptions; a tree node carries a handful. In jev-tree's benchmark a
   three-call tree used ~7x *fewer* tokens than one 255-option request (Appendix
   H). When state is small and the option list is large, a tree is cheaper; when
   state is large and options are few, a tree is depth-times more expensive.
2. **Code can slice state per node** (rule 1 of the talk). A node that only needs
   the title should only be sent the title.
3. **Speculative batching.** Putting every node's question into one request reads
   state once. A branching-3 tree has 13 internal nodes at depth 3 and 40 at depth
   4, which fits Clef (64 questions), OpenAI (400) and Fireworks Rune (256).
   Perplexity v1.2 explicitly bills state once per request; Liquid and Perplexity
   Flash bill state once per question, so batching saves nothing there. TypeSafe's
   own fan-out cookbook claims 13 batched questions are 12.2x cheaper than 13
   requests. Batching trades the tree's sequential dependence for cost: every
   node is asked whether or not its parent selected it.

Latency: hosted single decisions are ~0.1–0.5 s end to end (TypeSafe "about 100
ms" for most calls; independent medians 116–386 ms; p99 ~0.85 s; under 100
concurrent calls a few per thousand took 10–35 s). A depth-d sequential tree is
therefore roughly d x 0.2–0.4 s; a frontier LLM call is 1–3 s without reasoning
and far more with it.

## D.7 Conflicts between sources (unresolved)

1. **Clef-flash price:** $0.038 (Cloudflare pricing page) vs $0.019 promo
   (OpenRouter) vs $0.09 (a secondary article).
2. **Clef context:** 65,536 (Cloudflare docs) vs "Workers AI currently truncates
   long text state to roughly the first 2K tokens" (OpenRouter's listing; AIMultiple
   also observed a 2,048-token cut) vs 16,384 (Hugging Face card default). **Test
   before trusting Clef with long state.**
3. **Jev context:** 32,000 (Vercel, Cloudflare) vs 64k/32k (TypeSafe) vs 262,144
   (OpenRouter, long-context mode).
4. **Jev version behind `jev-latest`:** the official models page says 1.14.0
   (available from 2026-10-14); a source dated 2026-10-09 said 1.13.0. Pin an
   explicit version.
5. **TypeSafe access and compliance:** "early access" vs "public" with self-serve
   keys; SOC 2 Type II referenced on the enterprise page but nowhere else.
6. **OpenAI Decisions status:** GA with 400 questions (OpenAI guide) vs 200
   (OpenRouter) vs "limited preview" (early-October press).
7. **Liquid license:** docs say "LFM Open License" (revenue-capped) while a blog
   says "without restrictions". The LICENSE file controls; see Appendix E.
8. **Solar Decide:** $0.10 direct vs $0.05 on OpenRouter.

## D.8 Sources

docs.typesafe.ai/concepts/system-one · /models · /api · /sdk · /confidence.md ·
/legal · typesafe.ai · typesafe.ai/enterprise · typesafe.ai/legal/mca ·
blog.cloudflare.com/clef-decision-models · developers.cloudflare.com/workers-ai/models/clef/ ·
developers.cloudflare.com/workers-ai/platform/pricing/ ·
developers.cloudflare.com/ai/models/typesafe/jev/ ·
developers.openai.com/api/docs/guides/decisions ·
learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-microsoft-decision ·
docs.perplexity.ai/docs/decisions/quickstart · docs.liquid.ai/lfm/models/decision-models ·
liquid.ai/pricing · liquid.ai/blog/open-d1 · console.upstage.ai/docs/models/solar-decide ·
inceptionlabs.ai/models · subq.ai/pricing · docs.fastino.ai/pricing ·
docs.fireworks.ai/serverless/pricing · huggingface.co/MachineFi/Trio-Spark ·
openrouter.ai/docs/guides/community/jev.md · openrouter.ai/rankings/decisions ·
vercel.com/ai-gateway/models/jev · ai-sdk.dev/providers/ai-sdk-providers/typesafe-ai ·
pydantic.dev/docs/ai/models/system-one/
