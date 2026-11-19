---
id: C-benchmarks
derives_from: []
---

# Appendix C — Benchmarks

Retrieved 2026-11-12. `[IND]` = operator does not sell an evaluated model; `[VEN]`
= operator has a commercial stake; `[AUTH]` = a model or tool author's own claim.
Scores are not comparable across benchmarks, nor across method versions of the same
benchmark. Nothing here was re-run.

## C.1 Short answer

**Yes, benchmarks exist — more than a dozen, eight weeks after the category
appeared.** They cover single decisions well (accuracy, calibration, latency, price;
several with sealed test sets). **None measures recursive or tree composition**:
no per-level accuracy, no error propagation from a wrong parent, no check that a
path probability (a product of node probabilities) stays calibrated. The closest
proxies are closed-loop control benchmarks and one flat 15-way conjunction test,
and both show large composition losses.

| Benchmark | Operator | Independent? | Sealed / private set? | Measures | Best for |
|---|---|---|---|---|---|
| JevBench v1.8 | F. Standhartinger ("Benchmark Heaven") | Yes | 1,200 of 1,500 items sealed, rotating | Accuracy, calibration, speed, cost | Choosing a hosted API; CPU-timed open rows |
| Jev Decision Index 0.4.1 | Apolinário (HF Space) | Yes | Headline score 100% private | Chance-corrected accuracy on 37 public benchmarks + private tasks | Choosing an open model; exposes small-model overfitting |
| Artificial Analysis Decision Index v2.1 | Artificial Analysis | Yes | ~45% private | Probability-aware score, vs LLMs, cost per task | Decision models vs LLMs |
| Jevals.com 0.1.0 | Unnamed independent | Yes | No | Brier-style skill on 3 public tasks | Small sanity check |
| LangWatch Jev benchmark | LangWatch | **No** (sells Jev-based evals) | No | Jev vs sub-1B open models, 15 tasks | Sub-1B open models |
| Decision Models as Guardrails v1.0.0 | raxIT Labs | Yes | 2,269 held-back rows | Guardrail balanced accuracy, 33 systems | Guardrail use |
| System 1 Decision Benchmark v5 | etsabary | Yes | Sealed key | Hard reasoning-flavoured decisions | Stress test |
| Visual Decision Benchmark | etsabary | Yes | Sealed key | Image-grounded choices | Vision |
| AIM-Decision | AIMultiple | Publisher | 40 of 50 tasks withheld | 50 browser tasks + 1,655 classification items | Multi-step browser use |
| System1-Arena (arXiv 2610.21244) | UT Austin | Yes | — | 92,125 static questions + 138 closed-loop environments | **Composition loss** |
| TypedBench (arXiv 2610.11392) | DFKI et al. | Yes | — | Calibration, framing sensitivity, cost | Wording sensitivity |
| ProbabilityBench (arXiv 2610.17016) | Univ. Tokyo et al. | Yes | — | KL to exact ground-truth probabilities | Probability quality |
| JevAdvBench (arXiv 2609.31142) | IIE-CAS et al. | Yes | — | Adversarial flips | Robustness |
| OpenRouter Banking77 | OpenRouter | Router | No | One 77-way dataset vs Claude Opus 5 | Cost/latency vs frontier LLM |

## C.2 JevBench (Benchmark Heaven) `[IND]`

github.com/fstandhartinger/jevbench — Python 3.10+, stdlib-only adapters, MIT (harness
and public items); 341 stars; a self-described one-person hobby project.

**Design (v1.8).** 1,500 typed decisions per system: 300 public, 1,200 sealed (600
Choice, 300 Noul, 300 Score), rotated and retired after exposure. English only.
Task families: routing, answer-adequacy judging, policy yes/no, intent
classification, ordinal severity, enum extraction. Four axes, each 0–100:
Intelligence (chance-corrected accuracy), Calibration, Speed, Cost. *Capability* =
mean of Intelligence and Calibration (leads the open-weights board); *Composite* =
harmonic mean of all four (leads the hosted board). Any decision over 10 s counts
as wrong. Self-hosted latency is an assumption: 2 x measured + 150 ms.

**Run the public split locally:**

```bash
python -m jevbench.cli run --tasks datasets/public/original.jsonl \
  --adapter typesafe --model jev-latest --key-env TYPESAFE_API_KEY \
  --price-in-per-m 0.042 --price-out-per-m 0 \
  --results RUN/results.jsonl --raw-dir RUN/raw \
  --ledger RUN/ledger.jsonl --cap-usd 15 --manifest RUN/manifest.json
python -m jevbench.cli summarize --tasks datasets/public/original.jsonl \
  --results RUN/results.jsonl --public-export RUN/summary.json
```

**Hosted-API board, v1.8, updated 2026-11-10:**

| # | System | Composite | Intelligence | Calibration | p50 | $ per 1k decisions |
|---|---|---|---|---|---|---|
| 1 | Super Decider | 78.5 | 79 | 91 | 0.25 s | 0.016 |
| 2 | Myles-G 12B | 78.2 | 57 | 84 | 0.48 s | ~0.0011 |
| 3 | kettei-fat | 77.7 | 80 | 93 | 0.20 s | ~0.026 |
| 4 | Fastino GLiDE | 76.4 | 76 | 93 | 0.36 s | 0.023 |
| 5 | Liquid d1-ultra | 76.0 | 70 | 91 | 0.23 s | ~0.018 |
| 6 | SubQ Snap 1.1 | 75.7 | 76 | 88 | 0.47 s | ~0.020 |
| 7 | Drex Max | 75.4 | 79 | 90 | 0.25 s | 0.031 |
| 8 | Bespoke Nimble-v4-max | 74.8 | 68 | 91 | 0.26 s | ~0.020 |
| 15 | **Jev 1.13.0** | 71.4 | 64 | 91 | 0.24 s | 0.032 |
| 18 | **Jev 1.14.0** | 70.2 | 60 | 90 | 0.23 s | ~0.032 |

GPT-6 Luna (medium reasoning) has Capability 98.4 but Composite 39.1 because it
falls outside the cost and latency caps — a concrete illustration that an LLM is
more accurate and a decision model is cheaper and faster.

**Sub-1B and CPU-timed rows (v1.6.1):**

| System | Size | Capability | Intelligence | Calibration | Measured p50 |
|---|---|---|---|---|---|
| lev-350m | 350M | 43.3 | 4.8 | 81.9 | 0.022 s GPU |
| watt-flash-0.1 | 140M | 41.6 | 3.8 | 79.4 | 0.432 s CPU |
| Decision Fast | 0.6B | 40.6 | 6.1 | 75.1 | 0.058 s GPU |
| openJev Verdict 1.4 | 151M | 40.4 | 5.0 | 75.7 | 0.293 s CPU |
| verdict-small | 118M | 37.6 | 2.3 | 72.9 | 0.049 s CPU |
| kev 0.6B | 0.6B | 36.9 | 7.6 | 66.3 | 0.057 s GPU |

**Every sub-1B row has chance-corrected Intelligence of 7.6 or lower** — near
chance on this suite's accuracy; their scores are carried by calibration. Top open
models (27–31B) reach Capability 76–85, above Jev 1.13's 77.1.

**Criticisms:** items look simple and miss the agent/game uses the category is
marketed for; a zero-shot BART baseline was missing; results did not match the
Decision Index; sealed items are sent to hosted vendors, so outsiders cannot
reproduce official scores; single maintainer with heavy version churn. Five
unrelated projects share the name "JevBench".

## C.3 Jev Decision Index `[IND]`

github.com/apolinario/decision-index (96 stars, MIT code) and the Hugging Face Space
multimodalart/jev-decision-index (910 likes). Python.

**Design.** Chance-corrected scores (0 = random, 100 = perfect); unanswered = wrong.
**Full score (v0.4, 2026-10-19) = 0.60 x private same-skill tests + 0.40 x private
new-domain tasks**, equated onto the public scale. Models slower than 1,000 ms per
request on one RTX PRO 6000 are excluded. ~301 models listed.

**The 37 public benchmarks, by area:**

- *Knowledge & reasoning (25.8%):* GPQA Diamond, GSM8K (rebuilt), ChessBench, MuSR,
  SATA-Bench, CRUXEval, CLadder, HLE, MMLU-Pro, BBH, WinoGrande.
- *Language understanding (25.8%):* ContractNLI, ANLI, HellaSwag, ACOS, FinEntity,
  iSarcasmEval, VAST, NLI4CT, RAGTruth.
- *Retrieval & classification (20%):* BANKING77, CLINC150+OOS, BRIGHT (subset),
  Amazon ESCI, PhishNChips, HoVer.
- *Tools & automation (18.3%):* BFCL, ToolRet (subset), API-Bank, Home appliances,
  When2Call.
- *Arts & human taste (10%):* BPoMP, Humicroedit, POP909, cfcolor, Habermas Machine,
  New Yorker.

**Run it** (needs ~17 GB disk; engines `http` for any `/v1/systemone` server, or
`transformers`):

```bash
pip install -e ".[transformers,rebuild]"
python -m decision_index suite rebuild --work work
python -m decision_index pipeline --engine transformers --model Qwen/Qwen2.5-7B-Instruct --out runs/qwen-7b
```

**Standings, v0.4.1:**

| Rank | Model | Full | Public | New-domain | Params | Median ms |
|---|---|---|---|---|---|---|
| 1 | karpo-decision-31B | 73.86 | 75.05 | 61.50 | 31.3B | 94 |
| 2 | GLiDE 27B | 73.37 | 72.49 | 61.57 | 26.1B | 122 |
| 3 | REAX 1.3 | 72.64 | 73.71 | 61.05 | 57.4B | 246 |
| 5 | Copernicus-31B | 72.11 | 70.37 | 62.09 | 31.3B | 155 |
| 10 | OneJev1.6g-31B | 70.86 | 69.82 | 61.47 | 31.3B | 95 |
| 22 | baselabs mammoth-1 | 68.44 | 75.34 | 56.27 | 27.4B | 220 |
| 67 | **Jev 1.14** | 60.24 | 60.70 | 48.26 | undisclosed | 196 (HTTP) |
| 76 | **Jev 1.13** | 59.22 | 57.96 | 47.72 | undisclosed | 524 (HTTP) |
| 185 | GLiDE 0.8B (best sub-1B) | 36.36 | 54.32 | 11.14 | 0.75B | 37 |
| 201 | GLiDE 0.4B | 33.84 | 51.10 | 10.00 | 0.40B | 18 |
| 217 | OneJev1.6-0.8B | 29.58 | 48.76 | 9.28 | 0.85B | 13 |
| 252 | Crivo-68M | 19.51 | 32.82 | 7.59 | 0.068B | 12 |

Two things to take from this table. First, **Jev is mid-pack (rank 67–76 of ~301)**;
many open 27–31B models now beat it. Second, **sub-1B models score 45–59 on public
tasks but 5–11 on private new-domain tasks**: they transfer poorly, or are tuned to
the public sets. Public-only numbers (vendor cards, LangWatch, Jevals) overstate
small models. Earlier model cards cite v0.2.1 scores on a different scale (for
example d1-omni-600M 15.95, Von 13.74, d1-3B 48.57, Jev 57.9).

## C.4 Artificial Analysis Decision Index `[IND]`

**v1.0 (2026-10-13)** — four evaluations at 25% each (AA-Omniscience-Decision,
HLE-MultiChoice, When2Call, WildGuardTest):

| Model | Index | $ per 1M tasks | Median |
|---|---|---|---|
| Claude Haiku 5.5 (low), an LLM | 61 | 184 | 1.4 s |
| **Jev 1.13** | 58 | 42 | 0.13 s |
| GPT-6 Luna (low), an LLM | 55 | 131 | 1.5 s |
| GLiDE | 54 | 119 | — |
| Microsoft-Decision-1 | 54 | 31 | — |

Finding: decision models are overconfident on knowledge and reasoning questions and
better calibrated on tool-calling and safety.

**v2.0 / v2.1 (November 2026, live).** Weights: AA-Paperclip 30% (private),
EvalSafe-O*NET-AA 15%, AA-Omniscience-Decision 15% (private), HLE-MultiChoice 15%,
AA-Symmetry 15% (120 questions asked in 460 reordered, reworded or negated forms),
When2Call 10%. Decision Score = 50 x (1 + accuracy − Brier), so probabilities are
scored, not just picks.

**AA-Paperclip is the one published composition test:** 1,500 documents with 15
answers each; a document passes only if all 15 are right.

| Model | Index v2 | Paperclip all-15-pass | $ per 1M tasks | Time per task |
|---|---|---|---|---|
| Claude Haiku 5.5 (max), LLM | 77 | 92% | 6,240 | 32.65 s |
| GPT-6 Luna (max), LLM | 76 | 86% | 1,530 | 11.34 s |
| Drex Max v1.1 | 73 | 63% | 102 | 275 ms |
| GLiDE v1.2 | 73 | 62% | 780 | — |
| Decider v1.2 | — | 55% | 68 | — |
| Clef | — | 36% | 859 | — |
| Celeris-1.1 Decision | — | 24% | 14 | 56 ms |

Drex Max is 97% right per question, and 0.97^15 ≈ 0.63 matches its observed 63%
all-pass rate — exactly what independent per-decision errors would produce. That
is one model on one flat conjunction, but it is the only published check of the
`p^d` intuition, and it holds. Jev 1.14's v2 score was not retrievable.

## C.5 Composition and multi-step benchmarks

| Benchmark | What it measures | Headline |
|---|---|---|
| **System1-Arena** (arXiv 2610.21244, UT Austin) `[IND]` | 92,125 static questions plus 138 closed-loop environments (18 families) in which the top choice is executed each step | Static: Jev 72.6% vs GPT-6 Luna 71.2%. **Three models with identical 67.8% single-step accuracy reach 26.5% (Decision-2.0-Vega-27B), 17.4% (Jev) and 5.7% (Qwen3.5-9B) closed-loop success.** Best loop result 32.9% (Gemma-4-31B). Four small System One models reach at most 3.1% |
| **AIM-Decision** (AIMultiple) `[VEN]` | 50 live-site browser tasks (limits 900 s, 60 actions, 120 decision calls); a text LLM types form values | Jev 1.13 17/50; Kev-9B 20–21/50 (32/50 after fine-tuning on 606 decisions); Kev-27B 40; Drex Max 43; Gemini 3.8 Flash 43; GPT-6 Astra 47. Jev declared the task "blocked" in 25 of its 33 failures, 16 before taking any action. Drex Max cost $0.001 per completed task vs $0.224 for Astra |
| **WindTunnel** (nekuda) `[VEN]` | 49 browser tasks, 8 sites, comparing agent interfaces | "Jev + Mercury 2.5" 25/49 (best DOM configuration); Claude Haiku 5.5 over WebMCP 49/49 |
| **Sequential control** (arXiv 2609.37647) `[IND]` | One Choice per step in ALFWorld, TextWorld, BabyAI-Text, FrozenLake, Blackjack | Jev 35.1% / 42.2% / 20.8% / 13.4% / 42.6%; repeats ineffective actions on 40–45% of steps (Appendix B) |
| **AA-Paperclip** | 15-answer conjunction | See C.4 |
| **jevbench.dev** | Live StarCraft II, one legal move per step | 24 wins in 105 published runs |
| **ViZDoom community test** | Five decisions per second | Kills per episode: fine-tuned Qwen3.5-4B 3.63; Laya 1.25; Jev 1.13 |

Not found: any benchmark for hierarchical taxonomy classification or tree
composition with a decision model. Mario, Pokémon and Minecraft exist only as demos.

## C.6 Other single-decision benchmarks

**Decision Models as Guardrails (raxIT Labs, v1.0.0, 2026-11-12) `[IND]`.** 9,875
labelled guardrail checks (2,269 held back) across eight use cases, fixed 0.5
threshold, balanced accuracy. Apache-2.0 code and per-row results.

| # | System | Score | Catch | False block | $ per 1k |
|---|---|---|---|---|---|
| 1 | Liquid d1-ultra | 91.6 | 92.5% | 9.4% | 0.027 |
| 2 | pplx-decider-v1.2 | 90.7 | 90.6% | 9.3% | 0.013 |
| 3 | GPT-6 Luna (Decisions) | 90.0 | 92.4% | 12.3% | 0.110 |
| 6 | Clef | 89.5 | 91.5% | 12.5% | 0.202 |
| 7 | Microsoft-Decision-1 | 89.4 | 89.9% | 11.2% | 0.026 |
| 9 | Jev 1.14 | 88.7 | 90.0% | 12.7% | 0.039 |

Self-hosted: Strands Decider 12B 86.4, d1-2B 83.8, Kev-4B 81.4. Amazon Bedrock
Guardrails 79.0 at $0.113. Jailbreaks typed into chat are hard for everyone (best
75.2).

**System 1 Decision Benchmark v5 (etsabary) `[IND]`.** 1,456 hard questions (logic,
scheduling, state tracking, planning), adversarially filtered. GPT-6.1 Terra (no
reasoning) 81.6% at 1,160 ms; best decision model D3 Ultra 70.3% at 172 ms; **Jev
1.14 54.0%** at 173 ms; local 4B–9B quantized models 46.6–48.4%.

**Jevals.com `[IND]`.** Skill scores (0 = no better than base rates): Jev 69.0 /
67.8 / 9.2 on noul / choice / score; Gemini 3.8 Flash 73.0 / 74.1 / 4.6. On the
Score task "no model clearly beats guessing yet."

**LangWatch `[VEN]`.** Jev vs the best uncontaminated sub-1B open model: prompt
injection 94.6 vs 56.2; PII 90.8 vs 22.8; 77-intent routing 79.6 vs 42.4;
20-intent routing 89.1 vs 77.0. Its own caveat: **a no-model baseline such as
TF-IDF beats every open model on 9 of 11 tasks.**

**OpenRouter Banking77 `[IND]`.** 3,080 utterances, 77 options.

| | Jev 1.13 | Claude Opus 5 (no reasoning) |
|---|---|---|
| Accuracy | 81.0% | 84.4% |
| p50 / p95 latency | 175 / 270 ms | 2,266 / 3,004 ms |
| Cost per 1,000 | $0.11 | $2.42 cached (~$19 uncached) |

A cascade at confidence 0.90 lets Jev handle 75.9% of traffic for 84.0% accuracy at
$0.69 per 1,000 (thresholds chosen on the test set, so an upper bound). Jev's
confidence ranks well but is not calibrated: 96.3% accurate at >= 0.99, 29.6%
accurate below 0.5.

**AIM-Decision classification half `[VEN]`.** 62 decision models on 1,655 questions.
Cost per 1,000 decisions: Jev 1.13 $0.039; decider-12b $0.06; Clef $0.17; local
models on a rented A100 $0.007–0.57. On paper-topic classification (20 options) a
keyword classifier trained on 28,595 papers scored 70.4 and no decision model was
significantly higher. Checking an agent's "done" signal on the final page: 44 of 62
models above 90; five at 99.5.

## C.7 Tooling for your own data

| Tool | Language / license | Install | What it does | CI-oriented |
|---|---|---|---|---|
| abhixhek/jevcal | Python / MIT | `pip install "git+https://github.com/abhixhek/jevcal"` | Fits a per-question threshold to a target accuracy, verifies on held-out data, `jevcal check --lock decisions.lock.json --data data.jsonl` exits 1 on drift | Yes |
| Eliot5566/s1kit | Python / MIT (alpha) | `pip install s1kit` | One YAML suite against any `/v1/systemone` server side by side; `s1kit calibrate`; cheapest-first router | Yes (GitHub Action with `fail-under`) |
| openlayer-ai/jevals | Python / MIT (alpha) | `pip install jevals` | Agent evals as decision questions (tool choice, grounding); runs on Jev or local Kev/Laya | Partly |
| Valen-Team/JevalKit | Python / Apache-2.0 | clone + `pip install -e '.[hf,data]'` | Wraps eight suites incl. JevBench and the Decision Index | Smoke runs |
| allebee/pytest-jev | Python / MIT | `pip install pytest-jev` | `jev.expect(reply, holds=[...], lacks=[...])`; passes at p >= 0.8 | Yes |
| suraj-phanindra/wellposed | JS / MIT | `npm i -g wellposed` | Offline linter for decision requests (missing escape options, wrong criteria shapes) | Yes |
| `poc/depth_eval.py` in this directory | Python stdlib | — | Accuracy vs depth, threshold sweep, flat and beam baselines for a tree (unrun proposal) | — |

Note: TypeSafe's customer agreement restricts publishing Jev performance numbers;
jevcal and LangWatch withhold figures for that reason. Check the agreement before
publishing your own results.

## C.8 Reading the benchmarks together

- **Agreement is moderate at the top and weak in the middle.** Drex Max, GLiDE,
  d1-ultra and mammoth-1 lead on most boards they appear on. Jev is consistently
  mid-pack on current boards. Sharp disagreements exist (Super Decider is #1 on
  JevBench's API board and last of 30 on System 1 Decision).
- **Calibration findings conflict by task:** overconfident per Artificial Analysis
  and OpenRouter, underconfident per TypedBench.
- **To choose a model to self-host on CPU:** Decision Index (sub-1B rows with
  private new-domain scores) plus JevBench's open-weights board (the only CPU-timed
  rows). Both say sub-1B models are near chance on hard or unfamiliar tasks — budget
  for in-domain evaluation.
- **To choose an API:** JevBench's hosted board plus Artificial Analysis v2.1; add
  raxIT for guardrails.
- **Still unmeasured anywhere:** accuracy by tree depth; path-probability
  calibration; option-count scaling beyond 77; cost and latency of chained calls;
  CPU latency on standard hardware; adversarial robustness inside composed
  pipelines.
