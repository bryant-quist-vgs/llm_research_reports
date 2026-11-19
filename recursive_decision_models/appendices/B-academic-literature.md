---
id: B-academic-literature
derives_from: []
---

# Appendix B — Academic literature

Retrieved 2026-11-12. Every paper here is an arXiv preprint with no venue unless
marked otherwise; the field is eight weeks old (Jev was released 2026-09-15) and
almost all evidence is on one closed model version, `jev-1.13.0`. Numbers are as
reported by the papers' authors. Papers marked *(abstract only)* were not read in
full. "TDM" = typed decision model. "ECE" = expected calibration error (lower is
better).

## B.1 The one-paragraph answer

No preprint or peer-reviewed paper measures accuracy as a function of depth for
recursive or tree-composed decision models. What exists is: one hierarchical-routing
experiment on synthetic org charts (greedy descent 37.6% correct final unit, beam
search no better), one serial-construction experiment showing severe composition
loss (33.0% and 2.1% retention), two systems that embed bounded decision loops
inside an LLM pipeline (Jev-Mem, JevGPT), and one benchmark of step-by-step control
in text games where ~90%-optimal single decisions still produce poor episodes
because the model does not track state. The best-supported advantages of decision
models are cost and latency, not accuracy. The best-supported risks are adversarial
fragility that confidence thresholds do not fix, and probabilities that are not
coherent across question forms.

## B.2 Papers about decision models

### Typed Decision Models: An Early Evidence Audit and Evaluation Checklist — arXiv 2609.32160
Lijuan Tang, Yuemeng Zheng (Northeastern University). 2026-09-26. 25 pages.

Audits 28 arXiv papers posted 19–24 Sep 2026: 22 evaluate hosted Jev, 5 build open
TDMs, 1 is an ecosystem study.

- 21 of 27 model-evaluating papers include **no label-probability baseline**. Where
  one exists the typed readout shows no independent accuracy gain (AUROC .974 typed
  three-seed ensemble vs .950 label-token readout, not significant; macro accuracy
  .761 for both in another study).
- Jev trails stronger LLMs: median 11.6 macro-F1 points on social-science
  annotation; 5.8 on ContractNLI (77.4% vs 83.2% Gemini 3.1 Pro); 14.6 on
  JudgeBench; 19.8 on hard RM-Bench. It is never significantly behind flash-tier
  judges on binary rubric criteria.
- Speed and cost are the clear gains: median latency ~0.15–0.45 s; rubric judging
  30–220x faster and 29–325x cheaper than flash-tier judges. One frozen judge
  cascade reaches 92.5 vs GPT-6's 93.1 at 57% of the fee.
- On composition: per-step accuracy is "a weak proxy for end-to-end success because
  errors compound"; no study in the corpus tests the vendor's two-stage
  high-cardinality choice; decomposition into atomic questions has unmeasured error
  propagation. Trees and recursion are not analyzed.

**The 14-item evaluation checklist** (use this when judging any claim, including
your own pilot):

| # | Item |
|---|---|
| B1 | Include a label-log-probability baseline from an ordinary or same-backbone LM |
| B2 | Where a threshold escalates to another model, include a cheap generative cascade baseline |
| B3 | Where labels suffice, compare with a task-specific model (encoder, probe) |
| T1 | Report spread across models; no parity claims on near-ceiling tests |
| T2 | Report per-decision consistency across repeated, reordered and reworded requests |
| T3 | Test option-name invariance (swap names; neutral vs semantic names) |
| T4 | State data provenance (synthetic/real, gold-label source, whether the benchmark predates the model) |
| R1 | Give exact model version and run date |
| R2 | Give confidence intervals or significance tests for headline results |
| R3 | Disclose prompts, baselines and thresholds chosen after seeing test data |
| C1 | Measure calibration (ECE, Brier, reliability) if probabilities are used |
| C2 | Report accuracy among the highest-confidence examples, per task |
| C3 | Fit escalation thresholds on separate data, or fix them in advance |
| C4 | Report latency with and without caching |

Compliance in the audited corpus: T3 1/27, C4 3/20, B1 5/26, R2 15/27.

### Jev in the Wild — arXiv 2609.30216
Guoming Ling, Muen Xue (Sun Yat-sen University), Zijian Ye (CUHK). 2026-09-24.

2,170 verified public GitHub projects in Jev's first week (1,865 new, 305 existing
repos that integrated it; 43,750 stars on the new ones).

| Category | Subcategory | Projects | Share |
|---|---|---|---|
| Interface agents | Web interaction | 125 | 5.8% |
| | Desktop & mobile | 50 | 2.3% |
| Software engineering | Code quality | 90 | 4.1% |
| | Dev workflows | 218 | 10.0% |
| Search & memory | Context & memory | 77 | 3.5% |
| | Search & data | 120 | 5.5% |
| | Classification | 184 | 8.5% |
| Safety & governance | Review & approval | 82 | 3.8% |
| | Security & compliance | 93 | 4.3% |
| Routing & automation | Model & tool routing | 132 | 6.1% |
| | Workflow automation | 118 | 5.4% |
| Simulation & control | Games & simulation | 227 | 10.5% |
| | Robotics & control | 25 | 1.2% |
| Content & expert tasks | Professional tasks | 176 | 8.1% |
| | Content & dialogue | 211 | 9.7% |
| Infrastructure & other | SDKs & tools | 175 | 8.1% |
| | Research & resources | 56 | 2.6% |
| | Other | 11 | 0.5% |

Decision-use patterns: attribute judgment 77%, scoring/ranking 52%, action
selection 31%; 69.7% of projects combine two or more. Interfaces used: Choice
81.0%, Noul 72.2%, Score 45.4%, all three 36.8%. Multi-step patterns are described
but not quantified: per-step agent loops (jev-ultrafast), closed-loop control
(typesafe-mario), staged Noul → Choice → Score review (jev-review), and a two-stage
hierarchical classifier whose confidence is the **minimum along the path**
(tax-doc-classifier).

### Evaluating and Benchmarking the System One Model Jev — arXiv 2609.37647
Deußer, Ramamurthy, Sparrenberg, Sifa (Univ. Bonn, Lamarr Institute, Accura AI
Labs, Fraunhofer IAIS). v2 2026-10-29. Code:
github.com/AppliedMachineLearning-Lab/jev-benchmarking.

Zero-shot `jev-1.13.0` on 37 datasets (346,009 requests, US$9.40 total) against
option-probability readouts from Qwen3.8-27B and Gemma-4-E4B.

- Jev beats Qwen on 27, loses 9, ties 1; beats Gemma on all 37.
- ECE: pooled Choice 0.028 (Jev) / 0.063 (Qwen) / 0.208 (Gemma); single Noul 0.052
  / 0.113 / 0.123; **multi-label Noul is worse for Jev** (0.168 vs 0.119).
- Mean latency 0.36 s (rate-limit bound).
- **Sequential control, one Choice per step, arg-max executed** (the closest thing
  to a published "decision model as agent loop" benchmark):

| Task | Jev | Qwen3.8-27B | Gemma-4-E4B | Reference |
|---|---|---|---|---|
| ALFWorld | 35.1% | 54.5% | 6.7% | expert 90.3% |
| TextWorld | 42.2% | 51.1% | 12.2% | solver 100% |
| BabyAI-Text | 20.8% | 16.8% | 4.8% | expert 100% |
| FrozenLake | 13.4% | 9.4% | 4.2% | optimal 74.8%, random 6.6% |
| Blackjack | 42.6% | 41.2% | 41.1% | optimal 44.0% |

  Jev picks the optimal Blackjack action in 90.0% of decisions, yet repeats
  ineffective actions on 44.7% of ALFWorld and 40.6% of TextWorld steps and is
  overconfident there (ECE 0.247). The authors' recommendation: **leave episode
  tracking to the harness** — i.e. code must own state and history.

### Beyond Calibration: probability axioms — arXiv 2609.33209
Keyi Li, Yihao He, Quanyi Li (Northeastern University, Shenyang). 2026-09-27. Code:
github.com/bro789/typed-decision-coherence.

160 three-label items, ten question forms each. Jev's P(X) + P(not X) misses 1 by
0.064 on average (repeat-call noise 0.013) vs 0.293 for Qwen first-token readout.
Jev's three single-label Noul probabilities sum to 1.14 on average. Monotonicity
violations > 0.05 in 8.4% of checks. Guidance: do not mix probabilities from
different question forms in one rule; do not treat per-option Noul values as a
distribution; do not port thresholds across formats. **Choice is coherent by
construction.** Not tested: multiplying probabilities across calls (which is what a
tree's joint path probability does).

### Evaluating System One Models for Agent Security Decisions — arXiv 2609.33401
Yixuan Liu (TraceStone; NTU). v3 2026-10-03. Code:
github.com/yxsec/system-one-security-eval.

Jev, Laya, Decider, Nimble vs specialist guards and LLM judges on WAInjectBench,
R-Judge, AgentHarm. Macro-F1: WAInjectBench Nimble 0.778, Jev 0.756, GPT-4.1 0.707;
R-Judge Jev 0.825, GPT-4.1 0.807, a reasoning model 0.966. **Good aggregate numbers
hide a group failure:** Jev misses all 130 unsafe injection inputs that carry no
explicit instruction; of 1,446 inputs it scores below 0.1 unsafe, 9.2% are unsafe.
Temperature scaling helped in only 6 of 12 model/task cases. At a 1% miss limit,
symmetric thresholds automate 7.63% of R-Judge; separate allow/block thresholds
automate 47.03%, almost all blocks. An LLM review cascade fixes 10 of Jev's 167
misses on WAInjectBench but adds 33 new errors.

### JevAdvBench — arXiv 2609.31142
Hu et al. (IIE-CAS, HUST, Griffith and others). v2 2026-10-26. Data:
JevAdvBench.github.io/JevAdvBench/.

862 audited questions, 71 scenarios, twelve black-box attacks; only correct
decisions are attacked. **Attacks flip 46.3% of Jev's correct decisions** (identical
re-runs flip 0.17%); accuracy falls from 92.9% to 53.8%.

| Family | Method | Flip rate |
|---|---|---|
| Hijacking (76.6% pooled) | Task override | 92.0% |
| | Authority notice | 86.1% |
| | Self-promotion inside options | 21.1% |
| Contextual (67.5%) | Flawed reasoning, no command | 77.2% |
| | Irrelevant background | 67.4% |
| | Third-party opinion | 57.5% |
| Structural (7.4%) | Evidence order | 72.0% |
| | Near-miss options | 8.3% |
| | Option order | 2.4% |
| Linguistic (13.4%) | Character edits | 24.1% |
| | Word substitution | 9.1% |
| | Paraphrase | 8.0% |

The same variants flip 34.0–51.7% on eight open TDMs. **Confidence gating does not
rescue it:** at a 0.8 threshold 23.5% of still-executed decisions are wrong; at
0.99, 7.9% are wrong and automation falls to 37.7%. No defenses were evaluated.
(A widely repeated "one appended opinion flips 12.1%" figure describes v1 of this
paper; v2's figures above supersede it.)

### Narrow Decision Models — arXiv 2610.25553
Carlos André Antunes and nine co-authors (Softplan). 2026-10-18. 27 pages. **The
closest paper to tree composition.**

An organization-specific encoder (~110M mmBERT-base + 6.4M new parameters) that
serializes state → questions → options as a prefix tree with a block attention
mask, giving option-order invariance and question isolation by construction.

- **Hierarchical routing:** each org-chart node is a Choice over its children plus
  "none of these". Pre-registered procedure: greedy top-down descent; follow the
  arg-max; stop if abstention wins or the top probability is below a threshold; no
  backtracking. Path confidence may be product, geometric mean or minimum.
- **Result:** on four unseen fictitious charts (165 items) greedy descent reaches
  the correct final unit 37.6% [29.7, 44.8] of the time, vs BM25 15.2%. **Beam
  search and an exhaustive sweep both reach 35.2% — no better than greedy.**
- "Accuracy per decision compounds along a path" is listed as a limitation; no
  accuracy-by-depth numbers are given.
- Flat accuracy falls with label count: Banking77 0.953 with 4 labels vs 0.701 with
  77 — the motivation for trees.
- Calibration: Choice ECE 0.188 → 0.033 after calibration; abstention AUROC 0.79.
- On 9,092 real legal documents (28 types): 91.2% agreement with a production LLM's
  labels vs 90.2% for TF-IDF + logistic regression (macro-F1 0.80 vs 0.61).

### TypedBench — arXiv 2610.11392
Sharma, Duncan, Marceau Caron, Vollmer (DFKI, RPTU, Imperial, Mila). v2 2026-10-09.

Templated generators, nine suites; Jev 1.13.0, Laya 0.3.4 (421M encoder), Kev
0.8B/4B/9B.

- Ticket-priority accuracy: Jev median 0.874, **range 0.708–0.946 across
  paraphrases of the same question** (a 24-point spread); Kev 9B 0.565; Laya
  0.343–0.383 (majority prior 0.338).
- Selective prediction: coverage at 5% risk is 0.80 for Jev, 0.08–0.20 for
  decoders, 0.00 for encoders.
- **Option scaling:** Jev holds accuracy to 255 options at ~233 ms; encoders
  collapse before 100 options; decoders take seconds. (This is why small local
  models need trees and Jev may not.)
- Co-asked questions change at most 3% of answers. A paraphrased negation drops
  Jev's phishing accuracy from 0.99 to 0.76.
- With asymmetric costs, acting on Jev's probabilities was worse than taking its
  arg-max (2,300 vs 1,080 cost per 10^4 decisions).
- Encoder-to-Jev escalation at threshold 0.7 closes half the gap.

### ProbabilityBench — arXiv 2610.17016
Dai, Tang, Futami, Ishida (Florida State, Tokyo, Osaka, RIKEN). 2026-10-12. Code:
github.com/ishida-lab/ProbabilityBench.

Three simulated worlds with exactly known class probabilities; quality is KL
divergence to truth. Eight decision models and eight generative models. Decision
models hold 10 of 14 cost-quality Pareto points (Perplexity Decider cheapest at
$0.02/M input tokens), but **the best absolute quality is generative** (GPT-5.6
Terra, Claude Sonnet 5.5).

### Shorter entries

- **PixelJev — 2609.29283** (Nanjing Univ., MSRA). Visual choice by reading
  letter-token logits from Qwen3.5-2B/4B VLMs. 64-shot LoRA lifts Pets accuracy
  60.13% → 92.40%; specialists (DINOv2 probes) still win on source tasks;
  calibration does not follow accuracy.
- **Chinese-Jev — 2609.36965** (Fudan, NUS, UCAS). ~322M encoder initialized from
  Laya Multilingual. General accuracy 69.20% vs Jev 68.35%; legal 60.10% vs 68.35%;
  financial 64.72% vs 78.39%. 14–15 ms local vs 256–284 ms for Jev including the
  network round trip.
- **Decision models in pentest harnesses — 2609.28940** (independent). Design paper
  with a single-run case study. Useful design rule: the decision layer is
  *additive* — it may lower confidence or prune, but cannot override a
  deterministic validator. Cites Laya at 32.8–39.5 ms on a T4 with raw ECE 0.466 →
  0.081 after temperature scaling.
- **Jev-Mem — 2609.23986** (UT Dallas). Jev controls memory construction and an
  iterative route → retrieve → assess → expand loop with hard limits in code (depth
  8, 60 nodes, 16 Jev attempts, 15 s); one small-LLM call writes the answer. LoCoMo
  judge score 0.777 vs 0.700 for the best prior system; build time 158 s vs 1,044 s.
  No ablations.
- **JevGPT — 2610.18272** (KAUST). GPT-5.5 plans; Jev judges relevance and
  localizes evidence in parallel. BrowseComp-Plus 90.48% at ~$0.67 per question
  (Jev's share $0.06) vs ReAct 77.11% at $3.08.
- **Choice2Seq — 2610.16191** *(abstract only)*. Jev selects the right whole answer
  on 97.1% (arithmetic) and 99.5% (lexical retrieval) of items but retains only
  **33.0% and 2.1%** of those when the answer must be rebuilt from sequential local
  decisions. Dialogue-state construction is largely preserved. The strongest
  quantitative evidence of composition loss found.
- **System1-Arena — 2610.21244** (UT Austin). 92,125 static questions plus 138
  closed-loop environments in which the top choice is executed each step. Static:
  Jev 72.6% vs GPT-6 Luna 71.2%. **Three models with identical 67.8% single-step
  accuracy reach 26.5%, 17.4% (Jev) and 5.7% closed-loop success**; the best loop
  result of any model is 32.9%. Together with Choice2Seq this is the main evidence
  that single-decision accuracy does not predict composed performance. Details and
  the other composition benchmarks are in Appendix C.5.
- **Selection bias — 2610.35826** (Tencent). Across eight option orderings Jev's
  accuracy moves under 2 points but it keeps only 72–73% of initial successes;
  36.7–37.9% of unanimous answers are wrong. Takeaway: reliable isolated decisions
  need not remain reliable under composition.
- **Decision gates — 2610.00346** *(abstract only)*. Fine-tuned DeBERTa-v3-large
  wins on all labelled benchmarks but one. **Swapping "yes" and "no" flips 50.5
  answers per hundred for Jev.** At a guaranteed 5% risk Jev keeps 0.528 of intent
  decisions; an in-scope threshold still accepts 31.0% of out-of-scope requests. A
  trained first stage escalating to Gemma-4-31B matches Gemma's accuracy at about
  Jev's price.
- **Can confidence be trusted? — 2611.12521** *(abstract only)*. The provider's
  `confidence` field is a closed-form dispersion measure, not an accuracy estimate.
  Bundling questions flips 11.7–22.4% of binary decisions on a 0.8B model vs
  0.1–0.2% at 4B.
- **ViZDoom precedent — 2604.07385** (pre-Jev, April 2026). A 1.3M-parameter
  ModernBERT action classifier scored 178 frags in 10 episodes vs 13 for all tested
  LLMs combined, at 31 ms per decision. Small classifiers playing Doom predates the
  decision-model category.

## B.3 Recursion background

### Recursive Language Models — arXiv 2512.24601
Alex L. Zhang, Tim Kraska, Omar Khattab (MIT CSAIL). v3 2026-05-11. Code:
github.com/alexzhang13/rlm. This is the idea the talk transplants.

The prompt is stored as a variable in a persistent Python REPL. The root LLM sees
only metadata, writes code to inspect and split the prompt, and calls `llm_query`
(a sub-LM, or a sub-RLM at depth > 1) inside loops; only truncated stdout returns
to the root. Default depth 1; depths 0–3 tested.

| Task (GPT-5) | Base | Compaction agent | RLM depth 1 | RLM depth 3 |
|---|---|---|---|---|
| CodeQA | 24.0 | 58.0 | 62.0 | 58.0 |
| BrowseComp+ (6–11M tokens) | 0.0 | 70.5 | 91.3 | 92.0 |
| OOLONG | 44.0 | 46.0 | 56.0 | 58.0 |
| OOLONG-Pairs | 0.1 | 0.1 | 58.0 | 76.0 |

Depth is **not monotonic** (depth 0 beat depth 1 on CodeQA for one model).
Limitations: blocking sequential sub-calls, heavy-tailed cost, sub-call explosion,
errors propagated by deeper recursion. The crucial difference from recursive
decision models: in an RLM the *model* writes the decomposition; in an RDM *code*
does, and the model only scores options.

### Recursive Models for Long-Horizon Reasoning — arXiv 2603.02112 (ICML 2026)
Chenxiao Yang, Nathan Srebro, Zhiyuan Li (TTIC). The only peer-reviewed item here.

One model with `call` and `return` tools; a call opens a fresh child context and a
return passes back only the answer. Theory: with local context S(n),
unbounded-depth recursion solves TIME(2^O(S(n))); **constant-depth recursion
reaches only SPACE(S(n)), no better than summarization.** Error accumulation is
discussed only qualitatively. The theory concerns generative models and does not
transfer directly to non-generative decision calls.

## B.4 Older literature this builds on

Citations in this section other than FrugalGPT and Mozannar & Sontag were not
re-verified during this research and should be checked before being quoted.

- **Hierarchical classification and error propagation.** Koller & Sahami (ICML
  1997): top-down local classifiers per taxonomy node. Silla & Freitas (Data Mining
  and Knowledge Discovery, 2011): the standard survey; its central caveat is that a
  wrong decision at an upper node cannot be recovered below. Viola & Jones (CVPR
  2001): early-exit cascades.
- **Selective classification and deferral.** Chow (IEEE Trans. Inf. Theory, 1970):
  the optimal reject rule. El-Yaniv & Wiener (JMLR 2010) and Geifman & El-Yaniv
  (NeurIPS 2017): the risk-coverage trade-off. Madras et al. (NeurIPS 2018) and
  Mozannar & Sontag (ICML 2020, arXiv 2006.01862): learning to defer.
- **Calibration.** Guo, Pleiss, Sun & Weinberger (ICML 2017, arXiv 1706.04599):
  modern networks are overconfident; temperature scaling is a strong post-hoc fix.
  Brier (1950); Gneiting & Raftery (JASA 2007): proper scoring rules.
- **Zero-shot classification by scoring text pairs.** Yin, Hay & Roth (EMNLP 2019):
  labels as NLI hypotheses. Nogueira & Cho (arXiv 1901.04085): BERT cross-encoder
  reranking. These are the direct ancestors of state-plus-option scoring.
- **Label-token readouts.** Zhao et al. (ICML 2021, "Calibrate Before Use");
  Holtzman et al. (EMNLP 2021, surface-form competition); Willard & Louf (2023,
  constrained generation). These are the baselines the audit says are usually
  missing.
- **LLM cascades.** FrugalGPT (Chen, Zaharia & Zou, arXiv 2305.05176): a learned
  cascade with up to 98% cost savings at matched performance.
- **System 1 / System 2.** Kahneman, *Thinking, Fast and Slow* (2011); terminology
  from Stanovich & West (2000). Used as an architectural analogy only.

## B.5 What the literature does and does not establish

| Question | Status |
|---|---|
| Are decision models cheaper and faster than LLM judges? | Yes, consistently: ~0.15–0.45 s and $0.042/M input tokens; 30–220x faster, 29–325x cheaper than flash-tier judges |
| Are they as accurate as frontier LLMs? | No on hard tasks (6–20 points behind); comparable to small/mid LLMs; behind fine-tuned encoders when labels exist |
| Is the typed interface itself better than reading label logits from an ordinary LM? | Not shown; the audit finds no independent accuracy gain |
| Are the probabilities calibrated? | Mixed: good pooled Choice ECE in one study, underconfident in another, incoherent across question forms, 50.5% yes/no-swap flips |
| Do confidence thresholds make automation safe? | Not against adversarial input: 23.5% of executed decisions wrong at 0.8 |
| Does an LLM fallback fix low-confidence cases? | Only when errors are complementary; reviewers often repeat confident misses and add false positives |
| Does accuracy hold up when decisions are composed in depth? | **Unmeasured.** One synthetic routing result (37.6%), one severe serial-construction loss, text-game loops that fail on state tracking |
| Does beam search help over greedy descent? | One data point says no (35.2% vs 37.6%) |
| Do recursive decision trees beat a single flat choice or a single LLM call? | **No published comparison of accuracy, cost or latency** |
