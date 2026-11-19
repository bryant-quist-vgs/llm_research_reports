---
id: G-prior-art-and-critiques
derives_from: []
---

# Appendix G — Prior art for composition, and independent critiques

Retrieved 2026-11-12. "AR" = author- or vendor-reported; "IND" = independent
third-party measurement. Star and commit counts are as displayed that day; no
release dates could be confirmed. Almost every project here is under ten weeks old.
The full ecosystem inventory (hosted APIs, ~43 open models, runtimes, 34 SDKs, 67
applications, 41 agent tools) is in Appendix A; the speaker's own RDM code and
`jev-tree` are detailed in Appendix H.

## G.1 Libraries that implement composition, gating, escalation or audit

| Project | What it does | Language / license | Stars / commits | Install | Recursion · gate · trace |
|---|---|---|---|---|---|
| **rawwerks/rdm** | The talk's reference: a decision model in a loop whose answers run tools, call the module again, or finish | Rust / MIT | 4 / new (2026-11-08) | git dependency | **Recursive** (`max_depth`), per-question thresholds, `RDM_TRACE=1` call tree. See Appendix H |
| **rawwerks/dspy** `feat/rdm-v0` | `dspy.experimental.RDM`, Python reference | Python / MIT | fork branch | — | Recursive; `trajectory` on the root |
| **reachjalil/jev-tree** | One Choice per taxonomy level; auto-partitions lists over `maxFanout` | TypeScript / MIT | 10 / 4 | `npm install jev-tree` | **Recursive** (`maxDepth` 16, `maxCalls` 64). No gate, beam or backtracking. No trace |
| **steven-shoemaker/hunch** | Jev judgments as pandas/Python verbs; `hunch.Tree` walks a taxonomy keeping the best few paths | Python / MIT | 9 / 28 | `pip install hunch-jev` | **Beam over a taxonomy.** Answer "shape" sure / split / unsure: split re-asks the top two, unsure can go to an LLM. Cache, `dry_run` |
| **doeixd/discern** | Uncertainty-aware control flow; "maybe" is an explicit branch | TypeScript / MIT | 17 / 26 | `npm install @doeixd/discern effect@rc` | **Nested registries** capped by `withMaxDepth` (default 8). `onUncertain`, `minProbability`, `minMargin`; near-ties raise. `runWithTrace`, model-free `replay`, execution tree |
| **BillionsBobby/JevRouter** | Routes the next step across models, subagents, skills, MCP tools as one candidate set | TypeScript / MIT | 469 / 81 | `npm install github:BillionsBobby/JevRouter` | `group_by` hierarchical routing: coarse top-K then final choice; `decompose` into sub-goals. Below threshold → `no_decision`. Append-only receipts with provenance hashes |
| **jexp/neo4jev** | Walks a Neo4j graph hop by hop, offering outgoing relationships as choices | Python / MIT | 185 / 39 | `uv sync` | Iterative multi-hop with **beam** and max depth; per-hop probability view |
| **solvi-ai/solvi** | Runtime where a model proposes and code decides: typed questions, hard checks, rules, quote verification | Python / Apache-2.0 | 13 / 1,444 (v1.2.0) | `pip install solvi` | Tiered (System One → slow path → person). Calibrated guards (`act_guard`, `max_risk`); hard checks override confidence. **Hash-chained replayable traces**, `audit()` |
| **zjunlp/JevLoop** | Agent runtime that sends each fork in the loop (act? which tool? risk? done?) to a decision model; the LLM only writes | TypeScript / Apache-2.0 | 25 / 284 | `npm install github:zjunlp/JevLoop` | Seven decision nodes. Gates on top probability; irreversible actions go to `ask_human`. **Strong audit set:** `replay`, `trace --verify`, `metrics`, `claim-audit`. Falls back to local Laya, then rules, with no key |
| **gopaljigaur/decide** (pydecide) | Client that tries an ordered chain of backends (Jev → OpenRouter → OpenAI Decisions → local Laya → cross-encoder → JSON-prompted LLM) | Python / MIT | 1 / 120 | `pip install pydecide` | Below-threshold answers pass to the next backend; route recorded per response; `decide fit` fits thresholds from logged outcomes |
| **AntonioCoppe/jev-harness** | Policy layer: confidence gate, shadow mode, recipes, offline eval CLI | TypeScript / MIT | 15 / 57 | `npm install jev-harness` | `minConfidence` + `onLowConfidence` (review / escalate / suppress). Fixture replay, shadow no-op |
| **AbdelStark/s1-rs** | Typed Rust layer: enums and structs become questions | Rust / MIT or Apache-2.0 | 1 / 4 | git dependency | `Policy::act(0.85).review(0.6)` → `Verdict::Act / Review / Escalate` — the cleanest three-way type |
| **bladedevoff/stuntd** | Local proxy that records typed decisions made through hosted APIs, then trains small heads on a frozen Laya encoder to answer locally | Python / Apache-2.0 | 76 / 14 | `pip install "stuntd[train,jev]"` | Answers locally only above a calibrated threshold plus a novelty check; 2% audit sample; auto-reverts to shadow. **Note the TypeSafe anti-distillation clause** (Appendix E) |
| **browser-use/jev-ultrafast** | Browser agent: one request picks an operation and a DOM element; a small LLM writes text only for typing | Python / MIT | 24.5k / 5 | clone + `uv sync` | Flat loop, no gate. Inspector with probabilities and saved traces |
| **RiskAverseTech/toolgate** | Tool-call firewall (allow / ask / deny) as a hook, plugin or MCP proxy | TypeScript / MIT | 28 / 89 | `npm install -g @riskaverse/toolgate` | Static rules, then model. Max risk >= 0.85 deny, >= 0.55 ask. `audit.jsonl` |
| **eugeniughelbur/jev-engineering** | PR review router, shell-command gate, model routing | Python / MIT | 16 / 41 | `pip install jev-engineering` | Fixed pipeline: hard rules → read-only fast path → Jev → thresholds (deny 0.90, allow 0.10). Config layers can tighten but not loosen |
| **AshutoshVJTI/progressgate** | Detects semantic stagnation in agent loops | TypeScript / MIT | 1 / 7 | `npm install progressgate` | Returns CONTINUE / WARN / REPLAN / HALT |
| **suraj-phanindra/wellposed** | Offline linter for decision requests (45 structural checks) | JavaScript / MIT | 2 / 44 | `npm i -g wellposed` | Catches missing escape options and broken state paths before sending |
| **typesafe-ai/system-one-adapter-python** | Official shim that sends System One requests to OpenAI / Anthropic / Gemini for comparison | Python / MIT | 411 / 6 | `pip install 'system-one-adapter[openai]'` | Every provider attempt logged, replayable |
| **christianmat/jev-pokemon** | Jev plays Pokémon Red; the harness reads RAM and lists legal options | TypeScript / GPL-2.0 | 134 / 247 | clone | Two layers, no LLM. Finished the game in 37 h 40 m over 16,150 decisions for ~$1.65 (AR); needed loop-breakers and had 16 team wipes |

**Languages at a glance.** TypeScript dominates tooling; Python dominates models,
evaluation and data work; Rust has the talk's reference implementation plus several
SDKs; C++ appears in runtimes (llama.cpp, laya.cpp, jevos). Licenses are almost
uniformly MIT or Apache-2.0 for code.

**Maturity at a glance.** Nothing here is mature. The most-starred items are either
vendor-adjacent (jev-ultrafast, typesafe-ai/skills) or weeks old. No project that
does recursion publishes per-level accuracy or a compounding analysis. The most
complete gate-plus-trace designs are solvi, JevLoop and discern. Frameworks with
first-party support: Pydantic AI (built-in confidence-gated hand-off to an LLM),
LangChain (alpha), Vercel AI SDK. OpenProse, the speaker's employer, has released
nothing for recursive decisions.

## G.2 Reusable question patterns and anti-patterns

From vicfei/awesome-jev-prompts (CC0, 51 patterns; thresholds are starting points
to re-fit from a few hundred logged cases).

**Anti-patterns:**

1. Asking the model to compute (arithmetic, counting, dates).
2. Unbounded Choice lists.
3. No escape option (`other` / `none_of_the_above` / `review`).
4. A Score with an unordered rubric.
5. Reading Noul 0.5 as "medium" rather than "uncertain". Suggested bands: >= 0.8
   act, <= 0.4 pass, explicit uncertain branch between.
6. One global threshold for every action.
7. Floating `jev-latest` on threshold-sensitive paths; pin a version and log the
   returned one.
8. Ignoring a near-tie (0.45 vs 0.42 is a coin flip).
9. Letting one question own composition or side effects.
10. Using the model as authorization or a substitute for review.
11. Relying on label words; write observable criteria per label and run a
    label-flip self-check.

**Templates:** ticket triage = Choice of owning team (with `unrouted`) then Score
severity on four ordered levels. Email triage = Choice kind + Score urgency + Noul
needs-reply, composed in code. RAG filter = keep if relevance >= 2.5, or >= 2 with
entity match >= 0.8. Confidence gates: 0.6 default, 0.8 for security, 0.4 for a
pre-filter. Division of labour: "the model proposes, Jev supplies evidence, code
decides."

## G.3 Independent critiques and negative results

### Roussos, "Decision Models at the Game Table" (Oct 2026, IND, single practitioner)
Six decision models (hosted `jev-1.13.0`; Cloudflare Clef 27B/9B; vLLM-SR Decision
2.0 at 0.6B/4B/9B) against a local generative model, on one tabletop-RPG campaign's
tooling. Labels are one game master's past rulings, frozen and hashed.

| Model | Measured median latency | Model-card claim |
|---|---|---|
| Clef 27B (local, DGX Spark) | 420–960 ms | — |
| Clef-flash 9B | 125–270 ms | — |
| Decision-2.0 Lux-9B | 127–295 ms | 18.4 ms |
| Decision-2.0 Nox-4B | 79–206 ms | — |
| Decision-2.0 Kai-0.6B | 17–53 ms | 4.9 ms |
| Jev (hosted, end to end) | 116–121 ms (p99 232 ms) | — |
| Generative model, fast setting | 2.0–4.9 s | — |

Local medians were **3–7x the model-card figures**. The whole Jev run (6,292
requests, 4.2M tokens) cost about $0.18.

- **Triage — the win.** AUC 0.93; Jev and Clef 27B forwarded about half a pile of
  unknown tokens with 0 of 84 real names lost, on held-out data.
- **Verdict prediction — an artifact.** AUC 0.80–0.81 looked strong, but a
  one-feature baseline scored 0.897; without the upstream model's prose the
  classifiers fell below chance. They were reading the drafting model's hedges.
- **Spelling choice — a loss.** Jev 69.0%, Clef 66.4%, generative 76.1%; open
  models below 27B 15–31%. Candidate recall capped everyone at 79%. Jev abstained
  rather than guessing: 28 confident wrong names against Clef's 109.
- **Entity typing — structural failure.** Judging facts one at a time created about
  as many split entities as it repaired. A model-free chain (conventions → prior
  rulings → registry → 60% majority vote → human queue) matched the game master 32
  of 33 times.
- **Fine-tuning** recalibrated (AUC 0.900 → 0.963) but did not teach house
  conventions.

Design rules: use decision models as **filters and flags, not deciders**; count
abstentions and confident-wrong answers separately; a ruling should be made once
and read back (that did more for consistency than any classifier); add a trivial
baseline and a control set to any evaluation; re-measure latency on your own
hardware. On composition: each call feeds the next and errors compound silently
without a checkpoint; judging items independently cannot impose a cross-item
consistency property.

### "Jev Does Not Play Dice" (Hayashi, 2026-09-20, IND)
Asked to call a hidden fair die, Jev chose "1" in all 400 trials at a mean reported
probability of 82.9%; accuracy 19.0% (truth 16.7%). Coin 92.0%, spinner 90.2%, all
at chance accuracy. Choice also rewrote probabilities stated in documents (a stated
30% became 5.3%). Lesson: picking an option and estimating its probability are
different jobs; a high probability when the information is simply absent is
meaningless.

### One call or twelve dimension scores? (agentjournal.dev, 2026-09-17, IND)
Decomposing a judgment into 12–14 scored dimensions helps only when the single call
is already weak (74.0% vs 64.7%). A character-bigram naive Bayes matched the
dimensions for free. On a ledger task a 12-option Choice scored 40.0% against 94.9%
for word-bigram naive Bayes. **On guardrails decomposition was harmful:**
false-positive rate 37.2% versus 1.5% for the direct call. Twelve dimensions cost
1.6–2.3x the tokens of one question.

### "Classifier or filter?" (Aman Kumar, 2026-09-18, IND, ~16,000 calls)
Public sets: Enron 98.7%, SST-2 95.7%, AG News 91.3%, Banking77 76.0%. 82% of
answers were >= 0.9 confident and 96% of those were correct; below 0.9, accuracy
was 55–72%. On a private pipeline a 135-option task managed 68.6%, with the
probability swinging by 0.5 between runs on the same page. At 100 concurrent calls
a few per thousand took 10–35 s. Verdict: **a filter in front of a classifier, not
a replacement.**

### 791 labelled decisions against four LLMs (AY Automate, 2026-09-20, IND)
Jev 83.8% (8-way), 78.8% (77-way), 87.0% (injection) versus GPT-5.6 Terra 89.4 /
84.0 / 86.8. Latency p50 0.33 s vs 1.17 s; cost 40–49x lower. The vendor's 193.6x
and 444.6x claims did not replicate.

| Jev gated at 0.80, rest escalated to Terra | 8-way | 77-way |
|---|---|---|
| Share Jev answered | 80.6% | 77.1% |
| Accuracy on what Jev answered | 93.8% | 88.2% |
| Cascade accuracy | 90.0% | 84.8% |
| Terra alone | 89.4% | 84.3% |
| Cascade cost vs Terra alone | 25.7% | 27.9% |

Thresholds were evaluated on the same items, so this is optimistic.

### Other independent findings

| Source | Finding |
|---|---|
| ASSAY-001 (Forseti, pre-registered) | Calibration held on CLINC150 (ECE 0.020) and failed on Banking77 (ECE 0.094; the 0.8–0.9 bin was 66.7% accurate). Zero type errors in 8,576 responses. Latency median ~385 ms, p99 ~850 ms |
| Red Hat (2026-10-02) | Jev 86.35% on prompt injection, behind a Qwen judge (89.31%) and a ~200M DeBERTa classifier (89.01% at 54 ms vs 348 ms). Policy wording did not transfer between decision models. "Did not find decision models faster, cheaper or better than LLM judges" |
| Datadog Security Labs (2026-10-15) | A "counterfeit policy" prepended to untrusted content cut Noul injection recall from **82.90% to 3.88%** (12,295 samples). A counterfeit definition in an editable profile field moved a tool-risk gate from 0.893 to 0.290, below its block line |
| Rao & Callison-Burch (arXiv 2609.29769, abstract) | Over 85% of flash-tier LLM verdicts repeat a decision model's most confident errors. Oracle-threshold cascades gain at most 2.7 points over the best single judge |
| "What Can't Jev Decide?" (arXiv 2610.24929, abstract) | Error-free lookup up to 20k tokens and 64 options, but 53–80% at sixteen chained updates. It follows a stale state summary, and its confidence does not flag errors inherited from stale input |
| wellposed (AR) | On 31 real Choice questions with no escape option, Jev was wrong on every non-fitting input, 36% of them at >= 0.9 confidence. Adding `other` fixed 90% and changed 0 of 62 fitting answers. Co-batched questions moved answers by up to 0.51 |
| Jev search rerank eval (IND) | Jev rerank alone does not beat embeddings once judge circularity is removed; fusing Jev with embeddings wins (0.864 nDCG@10) |
| Jev Phishing Bench (IND, 2,000 emails) | Jev 62.6% vs Claude Haiku 4.5 81.3%; a domain-list rule with no AI scored 91.6% |
| Amplitude (2026-09-28) | Per-node calibration does not carry to workflows, because correlated mistakes survive composition |
| Arize | Zero-shot Jev 98.3% vs a trained TF-IDF logistic regression 98.4% on spam. No explanations means little signal for debugging |
| shimo4228/jev-skill-router (AR, self-critical) | One-week shadow log: 1,242 decisions, 539 suggestions, 28 followed (~5%). Removed: in a self-steering agent one injected line changes every later step, so the effect cannot be attributed, and the host model already sees every option |
| hermes-jev-skills (AR) | Handoffs written from Jev's keep/summarize/drop digest recalled 37.5% vs 58.7% from the plain transcript |

### The skeptics' case (Hacker News, 168 points)
*Against:* it is an ordinary LLM without the generation loop; the confidence is a
softmax over tokens under a nicer API and any GGUF model's log-probabilities can do
the same; usable calibration is hard (the fair-die result); no published paper;
estimates are unstable under modest shift; speed claims depend on batching.
*For:* a trained classifier needs labels you cannot get for an open-ended planner;
trained calibration is a stronger signal than raw log-probabilities; a low-latency
calibrated classifier is valuable in itself; it is a quick way to find out whether a
classification is feasible at all.

## G.4 Known failure modes, consolidated

1. **Depth compounds, and gating trades accuracy for coverage.** With 83.8%
   per-step accuracy (AY Automate, 8-way) and independent errors, three levels give
   ~59% end to end. Gating each step at 0.80 lifts per-step accuracy to 93.8% (~83%
   over three levels) but only ~52% of items clear all three gates (0.806^3). These
   are illustrative calculations, not measurements; errors in practice are
   correlated, which can make it better or worse. Greedy walks have no recovery
   path.
2. **Confidence does not see upstream errors.** A child fed a wrong parent result
   answers confidently.
3. **Escalation has a low ceiling when the fallback shares the errors.** Cascades
   gain at most a few points; several only matched the frontier model, at a quarter
   of its cost.
4. **Calibration is dataset-dependent.** Fine on CLINC150 and spam, overconfident
   on Banking77 and phishing, meaningless when the information is absent.
   Thresholds must be fitted per question and per pinned model version.
5. **Option enumeration is the hard part.** Missing escape options produce
   confident wrong answers; many-option questions degrade (12-option 40%, 77-option
   ~76–81%, 135-option 68.6%); candidate recall caps accuracy; overlapping labels
   create confident errors.
6. **State is an attack surface.** Attacker-written text inside state can redefine
   the question. Never use a decision model as authorization or as a sole security
   control.
7. **Ordering and framing.** Aggregate accuracy is stable under shuffling but which
   items fail changes; wording does not transfer across models; a yes/no swap flips
   half of answers; co-batched questions can interfere.
8. **Cross-item consistency and house conventions** cannot be enforced by judging
   items one at a time.
9. **Computation, multi-update reasoning, whole-document reading, string-level
   judgments** — use code or a reasoning model.
10. **A cheaper baseline may already win.** N-gram naive Bayes, a regex rule, a
    fine-tuned DeBERTa or an embedding ranker matched or beat Jev in at least four
    separate studies.
11. **Self-steering agent loops** are confounded and hard to evaluate; prefer
    fixed-step pipelines and shadow mode first.
12. **No explanations.** Poor for debugging.
