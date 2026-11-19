---
id: A-ecosystem-inventory
derives_from: []
---

# Appendix A — Ecosystem inventory

Retrieved 2026-11-12. This is a complete paraphrased inventory of the community list
`AnotiaWang/awesome-decision-models` (CC0-1.0; 713 stars, 146 forks, 149 commits; homepage
anotiawang.github.io/awesome-decision-models/), the most complete catalogue of the category.
Descriptions are paraphrased with facts kept; linked projects were not individually visited
for this appendix, and **scores, latencies and costs are author-reported claims** on
benchmarks each project chose, so they are not comparable across entries. Where another
appendix verified an entry directly (B papers, C benchmarks, D hosted APIs, E local models,
G composition libraries, H the talk), prefer that appendix. Two entries could not be found
when checked: Umpirix (repository 404) and Bud Decision Studio.

Naming note: "Jev" is TypeSafe AI's model; the community uses "Jev-like", "System One model",
"typed decision model" and "decision model" interchangeably for the category.

**Definition of "decision model" (per the README):** A decision model reads a state (text, JSON, and for some models images) plus questions whose answers are declared in advance. It returns a probability for every answer instead of generated text. Question types: Noul (probability that a statement is true), Choice (one of the caller's options), and Score (a level on an ordered rubric). The README says TypeSafe AI introduced the category in September 2026 with Jev and its `/v1/systemone` API, and that many models and runtimes accept the same request shape. The list is community-maintained and not affiliated with any model provider.

**Taxonomy (README's own sections, in order):** Hosted APIs; Open Models (subsections "From companies and labs" and "Community models"); Inference Techniques; Runtimes & Platforms; SDKs & Clients; Applications; Demos & Games; Agent Tools; Benchmarks & Evaluations (subsections Leaderboards, Studies, Tooling); Papers; Articles (with a "Community cookbooks" subheading); Related; Contribute; License.

Approximate counts: Hosted APIs 11; Open Models 43 (18 from labs, 25 community); Inference Techniques 10; Runtimes 18; SDKs 34; Applications 67; Demos & Games 32; Agent Tools 41; Benchmarks 26 (7 leaderboards, 13 studies, 6 tooling); Papers 9; Articles 10; Related 6.

---

## 1. Hosted APIs
API-only models, oldest first. Open-weight models their publishers also host (Clef, pplx-decider) are under Open Models.

1. **Jev**, https://docs.typesafe.ai/introduction. TypeSafe AI's first System One model and origin of the `/v1/systemone` API: Noul, Choice, Score over a text state in one request. Keys from the TypeSafe console. Also served via Vercel AI Gateway, Cloudflare Workers AI, and OpenRouter. Sub-links: playground (console.typesafe.ai/playground), console (console.typesafe.ai), GitHub (github.com/typesafe-ai), workflow evals (evals.typesafe.ai), cookbooks (docs.typesafe.ai/llms.txt), patterns (docs.typesafe.ai/patterns), "Jev 1.13 jaggedness" known failure modes (docs.typesafe.ai/model-jaggedness/jev-1.13), Discord (discord.gg/typesafe), X @typesafeai.
2. **meraGPT Decider 1**, https://meragpt.com/docs. Hosted model `state-decider-1` (alias `sd-1`) answering Noul, Choice, Score via `/v1/systemone`, compatible with the TypeSafe SDK. Limits: 4,096 tokens per request; Choice up to ten labels.
3. **Trio-Spark**, https://github.com/machinefi/trio-spark. MachineFi's hosted model for text, images, and sampled video frames. Choice, Score, Noul via `/v1/systemone`, with a probability per option in one pass. Reports v1.3 at 90.9% across 13 public-dataset tasks, and ECE 0.019 on the 10 tasks where calibration is measured (release post: machinefi.com/blog/trio-spark-v13-decisions). Weights closed.
4. **Solar Decide**, https://openrouter.ai/upstage/solar-decide. Upstage's beta model on Solar Mini 4, 512K context, same request format as Jev. Solar Decide Flash (openrouter.ai/upstage/solar-decide-flash) is the lower-latency variant.
5. **Span-01**, https://www.respan.ai/blog/introducing-span-1. Respan's classifier for AI traces. For each plain-language behavior (prompt injection, hallucination, agent loops) returns present, absent, or not observable. Span-01 and a Lite tier on OpenRouter (openrouter.ai/respan/span-01).
6. **d1**, https://docs.liquid.ai/lfm/models/decision-models. Liquid AI's first decision model, text and images. Served at a `/v1/systemone` endpoint the TypeSafe SDKs can call. On OpenRouter (openrouter.ai/liquid/d1), text only for now. Launch blog: liquid.ai/blog/d1-decision-model. Model size not disclosed.
7. **OpenAI Decisions API**, https://openai.com/index/devday-2026-recap. Announced at DevDay 2026; public beta since October 2026. GPT-6 Luna answers Noul, Choice, Score over text, JSON, or image state, with a probability per option and no generated text. Also on OpenRouter as GPT-6 Luna Decisions (openrouter.ai/openai/gpt-6-luna-decisions).
8. **Mercury Decide**, https://openrouter.ai/inception/mercury-decide. Inception's model, with a free route on OpenRouter. Inception cites up to 14 decisions per second.
9. **Tazo**, https://tazolabs.com/. Tazo Labs' audio-native model for live voice agents. Reads call audio with no transcript step; returns a probability per option (e.g., respond, wait, yield, backchannel, escalate). API access by request. Write-up: tazolabs.com/blog/tazo-vs-jev-audio-decision-model.
10. **Microsoft-Decision-1**, https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-microsoft-decision. Microsoft Foundry model for text and JSON. Noul, Choice, Score via `/providers/microsoft/v1/systemone` on a Foundry deployment. Auth: Microsoft Entra ID or API key. Docs cover deployment and a support-ticket classifier.
11. **djev**, https://djev.dev. Maisa's hosted decision API for text and images (yes/no, choice, score), with a live playground. API host api.djev.dev. Access by invite or recovery key. Open-source implementation: github.com/Davipar/djev-dev.

## 2. Open Models
Open-weight models you can download and run. Scores are as reported by each project on the benchmark it chose, so they are not comparable across entries.

### 2a. From companies and labs
1. **Clef**, https://huggingface.co/Cloudflare/clef. Cloudflare's Apache-2.0 models post-trained from Qwen3.8-27B. Reads text, JSON, images, or video; scores every option of every question jointly. Clef-flash is the smaller, faster variant. Both hosted on Workers AI with a Jev-compatible API. Launch blog with Jev Decision Index results: blog.cloudflare.com/clef-decision-models.
2. **pplx-decider-v1.1-27b**, https://huggingface.co/perplexity-ai/pplx-decider-v1.1-27b. Perplexity's Apache-2.0 multimodal model, fine-tuned from Qwen3.8-27B. v1.1 lifts the causal mask and adds training data. Card reports 61.56 on the Jev Decision Index vs 57.9 for Jev. Also on the Perplexity Decisions API (docs.perplexity.ai/docs/decisions/quickstart) and OpenRouter (openrouter.ai/perplexity/pplx-decider-v1.1-27b).
3. **Strands Decider 2B**, https://github.com/strands-labs/strands-decider. AWS Strands Labs. Qwen3.5-2B with the LM head replaced by a pointer head of about one million parameters that scores each option, plus a rank-16 LoRA. Weights, training data, and scripts public. Launch post (strandsagents.com/blog/introducing-strands-decider) uses it to check a Strands agent's tool calls before they run.
4. **Nimble**, https://github.com/bespokelabsai/nimble. Bespoke Labs' 9B LoRA fine-tune of Qwen3.5-9B on contrastively curated synthetic data. Public 13-dataset benchmark suite. In Ollama as `nimble`.
5. **Tev1**, https://huggingface.co/togethercomputer/Tev1-4B-experimental. Together AI's experimental 4B and 0.8B supervised fine-tunes of Qwen3.5. Walkthrough: "training your own decision model for $17" (together.ai/blog/how-to-train-your-own-jev). In Ollama as `tev1`.
6. **Laya**, https://github.com/NandhaKishorM/laya. Convai Innovations' multilingual non-autoregressive model. Choice, Score, Noul in one forward pass. Published weights, PyPI package, and a router that picks a checkpoint per request.
7. **GLiNER2.5-Decide**, https://huggingface.co/fastino/GLiNER2.5-Decide. Fastino's Apache-2.0 DeBERTa-v3-large classifier. Caller-defined tasks and labels get probabilities in one forward pass via `gliner2` on CPU or GPU. For operational classification, routing, ordinal scoring.
8. **Standard One**, https://huggingface.co/StandardThinking/StandardOne-8B. Standard Thinking's Apache-2.0 3B and 8B models on Ministral 3, with a retained Pixtral vision tower. Text or images in, option probabilities out via `/v1/systemone`. Merged weights, adapters, GGUF builds, server code.
9. **OpenJev**, https://huggingface.co/openjev/openjev. Independent open-weight model scoring caller-defined options in one forward pass, with calibration and serving code. Weights CC BY-NC 4.0 (noncommercial); helper and server code Apache-2.0. Separate from SemIf (formerly OpenJev).
10. **StartLux-Decision**, https://github.com/StartLuxLabs/StartLux-Decision. Five dense sizes (0.8B to 27B) and a 35B-A3B mixture of experts. Reads text, JSON, or images up to 256K tokens via `/v1/systemone`. Authors report 63.88 vs 57.91 for Jev on Decision Index 0.2.1. Code Apache-2.0; weights CC BY-NC 4.0.
11. **Decision 2.0**, https://huggingface.co/collections/vllm-sr/decision-20-6ab7cf7bdfb506bf8269cb00. vLLM Semantic Router's Apache-2.0 models, 0.6B to 27B. Up to 64 Choice, Noul, Score questions about one input in one forward pass. Loadable with Transformers.
12. **Intern-Decision**, https://github.com/InternLM/Intern-Decision. InternLM's multimodal models (0.8B, 2B, 4B), fine-tuned from Qwen3.5 with the vision tower frozen. Ships training code, two inference backends, temperature calibration, and a 96-case distribution-calibration benchmark. Weights: huggingface.co/collections/internlm/intern-decision.
13. **Security-One 27B**, https://huggingface.co/superagent-ai/security-one-27b. Superagent's Apache-2.0 security-triage model, fine-tuned from AutoJev-27B on Qwen3.8-27B. Scores supplied options for prompt injection, tool calls, code changes, alert severity in one pass. Launch blog: superagent.sh/blog/introducing-security-one.
14. **Jeeves**, https://github.com/PostHog/jeeves. PostHog's 9B Jev-like model (Qwen3.5-9B with LoRA and pointer head), trained with CISPO to reason before deciding; diffusion drafter for speed. Reports 0.935 vs 0.866 for Jev on JevBench's 231 public items. Training code and data public.
15. **Phocinae-Largha-150M-v1**, https://github.com/Phocinae/Phocinae-Largha-150M-v1. Bilingual (English/Chinese) model built on mmBERT-small (144.3M params, Apache-2.0). One forward pass gives calibrated Choice, Score, Noul probabilities; trained for option-order invariance; confidence gate. typed-decisions 0.906 (en, fitted on this dataset's train split) and 0.848 (zh, machine-translated). Latency: p50 21.0 ms on RTX 5090 (fp16), about 1.64 s per case on CPU. At τ=0.6, 55.0% of decisions resolve locally with 0 output tokens.
16. **VideoJev**, https://github.com/MCG-NJU/VideoJev. Open 4B and 35B-A3B models scoring temporal candidates and answer options for video grounding and multiple-choice QA. Multiple queries over one shared video prefix, no text generation.
17. **OpenThai-SystemOne**, https://huggingface.co/iapp/OpenThai-SystemOne. iApp / OpenThai's Apache-2.0 Thai and English 0.8B model. Choice, Score, Noul in one pass, mirroring `POST /v1/systemone`. Pip package; Ollama build `iapp/openthai-systemone`. Independent; not affiliated with TypeSafe.
18. **Saina Helm 2 and Omni**, https://github.com/run-saina/saina. Open-weight 0.8B models scoring caller-defined answers in one shared forward pass. Helm 2 reads text; Omni adds images and short audio. Server supports Jev-compatible `/v1/systemone` requests.

### 2b. Community models
19. **Kev**, https://github.com/jaredpalmer/kev. Qwen3.5 models (0.8B, 4B, 9B) you can train and serve. Choice, Score, Noul in one pass. Published weights, frozen eval suites, local `/v1/systemone` server.
20. **Lev**, https://github.com/InterfazeAI/lev. Interfaze's open model: Qwen3.5-4B with a LoRA, zero output tokens, `/v1/systemone`-compatible server. Authors report 74.3 macro on 13 S1Bench subsets vs 76.1 for Jev, in their harness. Weights: interfaze-ai/lev. Independent.
21. **Von**, https://github.com/wfzyx/von. Local non-autoregressive model with a `/v1/systemone`-compatible server and a Doom demo where each move is one forward pass.
22. **NanoJev**, https://github.com/TianyuCodings/NanoJev. 0.6B parallel model: outputs a full distribution, no decoded text. Published weights and checkpoints for ViZDoom, Maze, Snake. Author's ViZDoom Basic split: 128/128 vs 56/128 for Jev.
23. **jevlike**, https://github.com/vinnylarouge/jevlike. Trains a small one-pass scorer mapping context plus N text options to a probability per option. Doom and chess vision demos; Wikispeedia next-click example. Explicitly not a reproduction of TypeSafe's architecture or RLCD.
24. **decider**, https://github.com/Mapika/decider. Qwen3.5-2B fine-tune emitting typed decisions with calibrated probabilities in one pass.
25. **RSI-Jev**, https://github.com/Shanghua-Gao/RSI-Jev. Jev-like models trained by a recursively self-improving AI research system that publishes every experiment, failures included. 4B and 27B (v6.1-VL). Probability per Choice, Score, Noul option in one pass over text or images. Effort setting (low, medium, high, auto). Open weights; `/v1/systemone`-compatible server.
26. **jev-style**, https://github.com/lawrence3699/jev-style. 0.8B Qwen3.5 model. Install with `pip install "jev-style[torch]"` or `[mlx]` on Apple silicon. Runs locally via PyTorch, MLX, or llama.cpp (scorer built separately), behind a `/v1/systemone`-compatible server. Includes an MCP server and a Claude Code guard hook.
27. **PlayJev**, https://github.com/OmniJev/PlayJev. Qwen3.5-0.8B-Base fine-tuned to play ten browser games from 448 px frames. One forward pass per move; probabilities read from option letters; no generated text. Open weights; browser demo.
28. **OneJev**, https://github.com/OmniJev/OneJev. OmniJev team's open multimodal model in four sizes (0.8B to 27B). Choice, Score, Noul over a screenshot, photo, video, or text, with calibrated probabilities. Weights on Hugging Face.
29. **jevos**, https://github.com/feder-cr/jev. 1B model for CPU-only laptops: MiniCPM5 cut to 17 layers with a one-logit head. GGUF q4_k_m at 619 MB, runs on llama.cpp, about 54 ms per short request. Noul (yes/no) only; Choice and Score return HTTP 422.
30. **WebJev**, https://github.com/lexmount/WebJev. Model for browser agents: Qwen3.5-35B-A3B fine-tune picking the next operation and target element. On 125 real-website tasks, completes 38.5% vs 16.7% for Jev 1.13 in the same agent. Apache-2.0 weights, training data and recipe, demo app.
31. **Vev**, https://github.com/Xiaooolong/vev. Open-source Jev implementation with vision input, fine-tuned from Qwen3.5 4B/9B. Screenshots and photos go directly into the state. Reads label-token probabilities, no generated text. Open code and weights; weights for non-commercial use only.
32. **JEV-27B**, https://huggingface.co/autotrust/JEV-27B. AutoTrust's Apache-2.0 model distilled from Jev 1.13 onto Qwen3.8-27B. One vLLM engine serves both decisions and the untouched Qwen model. Authors report 84.07 vs 83.85 for Jev over six public benchmarks (own runs). Smaller sibling: JEV-9B (huggingface.co/autotrust/JEV-9B).
33. **Winnow**, https://huggingface.co/EldanRing/Winnow-12B. Apache-2.0 Gemma 4 fine-tunes (12B and E4B) for typed decisions. Served from a llama.cpp-based server answering both `/v1/systemone` and `/v1/chat/completions`.
34. **JevK5**, https://github.com/allebee/jevk5. Apache-2.0 models on Qwen3.5 (2B, 4B, 9B) behind a `/v1/systemone` server, with GGUF builds for llama.cpp on CPU and GPU.
35. **JevAlt**, https://mertkayacs.github.io/jevalt/. Mert Kaya's open 4B models: Deem-4B (English), Karar-4B (Turkish), Wähler-4B (German), with GGUF builds. `jevalt serve` exposes `/v1/systemone`. Q4_K_M uses about 3 GB RAM on a laptop CPU. Independent.
36. **TurinTech compressed decision models**, https://huggingface.co/collections/turintech/compressed-decision-models-6accea74eb7016a886f25fdb. GGUF conversions of Clef, Perplexity Decider, Kev, d3 for local llama.cpp inference; model cards describe quality trade-offs.
37. **reflex**, https://github.com/kshetrajna12/reflex. Small model on frozen Qwen3.5-4B. One `/v1/systemone` endpoint, one forward pass, about 200 ms. Compared with Jev on JevBench's public items.
38. **imajev**, https://huggingface.co/mohit67890/imajev-4b. Apache-2.0 4B LoRA on Qwen3.5-4B for photo decisions: checks a photo against your record or compares two photos. Trained `unknown` probability so apps can abstain. Jev request shape plus `images`. Runs on MLX or PyTorch.
39. **NeoHorse-Jev-4B**, https://huggingface.co/TokenRhythm/NeoHorse-Jev-4B. Apache-2.0 4B model on NeoHorse-1-4B. Text or one image plus text. Prefill-only inference; served at `/v1/systemone`.
40. **WaterSheep**, https://github.com/SamratDuttaOfficial/WaterSheep. Apache-2.0 text model. Noul, Choice, Score, multi-label questions get calibrated probabilities. Local `/v1/systemone` server that TypeSafe's Python SDK works with unchanged.
41. **Wald-4B**, https://huggingface.co/org2ai/Wald-4B. Apache-2.0 4B decoder trained in full from Qwen3.5-4B-Base. Optional thinking; calibrated option probabilities; self-hosted `/v1/systemone` server for CUDA GPUs. GitHub: github.com/org2AI/wald-4b.
42. **Valen**, https://github.com/Valen-Team/Valen. Apache-2.0 multimodal models (0.8B, 2B, 4B). Text, images, video in; probabilities over supplied candidates out. Training code and data included. Free demo and API: valen-team.github.io.
43. **Dwight 4B**, https://huggingface.co/zime-ai/dwight-4b. Zime AI's Apache-2.0 model for sales call transcripts, fine-tuned from Qwen3-4B-Instruct-2507. Yes/no, choice, or 0-10 score question gets a single option token with probabilities. Separate mode writes JSON insights with verbatim quotes. Self-hosted with vLLM; community GGUF builds. English B2B calls only.

## 3. Inference Techniques
Ways to get decision-model behavior from existing models, usually by reading option probabilities in one forward pass, with little or no training.

1. **SemIf**, https://github.com/TheoLeeCJ/SemIf-OpenJev. Formerly OpenJev. Typed decisions from open models on a home RTX 3090 and in the browser; reads option logits instead of generating text.
2. **LitJev**, https://github.com/zhengxuyu/litjev. Reproduction of Jev that turns any Qwen model into a fast decision model, same `/v1/systemone` schema (Choice, Score, Noul). No training; no generated answer text.
3. **TetraJev**, https://github.com/FeiLiuEM/tetrajev. Local decision layer. Two frozen open-weight readers give four readings per item (letter and per-candidate yes/no), fused without fitting and routed by agreement with calibrated release gates. Evaluated on eight decision suites, a RAG reranking pass, and DecisionBench's 35 task categories. No training.
4. **jevmlx**, https://github.com/bnsd55/jevmlx. Parallel constrained decisions for any MLX model on Apple Silicon: schema-valid JSON in one forward pass.
5. **JEVfire**, https://github.com/kikoncuo/jevfire. Parallel decisions for CUDA LLMs via vLLM, with a browser Mario demo (~71 ms/action locally).
6. **PocketJev**, https://github.com/NullPo-jp/PocketJev. On-device iPhone visual decisions with MLX and Qwen3-VL option logits. Camera plus 3 choices; no text generation; ~1 s; no photo saved.
7. **jev-visual**, https://github.com/hr98w/jev-visual. Educational visual inference on Apple Silicon: shared multimodal context, candidate scoring; sorting-factory, Breakout, and gesture demos.
8. **DiffusionGemma decision endpoint**, https://huggingface.co/spaces/victor/DiffusionGemma-free-endpoint. Free Hugging Face Space reading probabilities per answer from DiffusionGemma, no fine-tuning, behind the `/v1/systemone` format.
9. **AnyJev**, https://github.com/nokia-applied-research/AnyJev. Nokia's training-free method turning any LLM into a Jev-style model whose answers hold when option order changes. Also self-distilled Tacit models (1.7B to 9B) that send a capped share of low-confidence decisions to the model's own reasoning. `pip install anyjev`.
10. **simple-jev**, https://github.com/featherless-ai/simple-jev. Featherless AI server turning compatible open Hugging Face models into a `/v1/systemone` endpoint without training a classifier head. Laya backend; reproducible prompt-format search.

## 4. Runtimes & Platforms
Servers, gateways, and native runtimes for running decision models.

1. **Ollama**, https://ollama.com/blog/ollama-now-supports-jev-style-decision-models. Serves `/v1/systemone` locally since 0.35. First decision models in its library: `nimble` and `tev1`.
2. **llama.cpp**, https://huggingface.co/blog/ggml-org/decision-models-in-llamacpp. `llama-server` serves Laya, Kev-4B, OpenJev, Clef at `/v1/systemone`. Image state; router mode loads several models on demand.
3. **SGLang**, https://docs.sglang.io/docs/supported-models/decision_models. Native `/v1/decisions` and `/v1/systemone` endpoints reading option probabilities from a validated chat model's next-token scores; no special checkpoint.
4. **vLLM Jev**, https://github.com/mode-io/vllm-jev. Native vLLM serving on Linux and Apple Silicon, including image and video questions for Valen.
5. **Flide**, https://github.com/OmniJev/Flide. OmniJev inference engine. Forks one state into all its questions in one pass, so each answer matches the question asked alone. Serves OneJev, Qwen3.5, Gemma 4 via `/v1/systemone`. `pip install flide`.
6. **openjev**, https://github.com/razorback16/openjev. Jev-compatible server on DiffusionGemma 26B-A4B and other backends. `/v1/systemone` plus OpenAI Decisions API shape; Docker/vLLM or MLX; free hosted route via Codiv. Separate from the HF weights named OpenJev. Independent.
7. **Unsloth**, https://unsloth.ai/docs/models/decision-laya. Unsloth desktop app serves Laya and Clef locally via a TypeSafe-compatible `/v1/systemone` API on macOS, Windows, Linux.
8. **Ollaya**, https://github.com/ollaya-dev/ollaya. Ollama-style runtime: pulls and serves open encoders and decoders (Laya, Von, Kev, Decider, Nimble, Winnow, more) with each author's calibration, behind `/v1/systemone`. Official TypeSafe Python SDK works unchanged. Site: ollaya.dev.
9. **Laya-MLX**, https://github.com/mizorewww/laya-mlx. Independent native MLX port of Laya for Apple Silicon. Choice, Score, Noul without text generation or cloud API; keeps upstream formatting and calibration; port-fidelity checks and performance data.
10. **Laya-CoreML**, https://github.com/mizorewww/laya-coreml. Core ML and Neural Engine port of Laya from the Laya-MLX author. Reproducible speed and energy benchmarks. About 5 ms per short decision on an M3 Max.
11. **laya.cpp**, https://github.com/lkarlslund/laya.cpp. Native C++ inference for Laya on ggml with CUDA, Vulkan, Core ML backends; Jev-compatible HTTP server with automatic request batching; prebuilt binaries.
12. **sys1**, https://github.com/alvarobartt/sys1. Rust server on candle for self-hosted models like Laya. System One-compatible API; dynamic token-based batching; CPU, Metal, CUDA builds.
13. **OpenRouter decision models**, https://openrouter.ai/models?output_modalities=decisions. Models from several publishers behind OpenRouter's alpha Decisions API, which chat-completions SDKs cannot call. Usage guide as an agent skill: openrouter.ai/skills/openrouter-decisions.
14. **Vercel AI Gateway**, https://vercel.com/ai-gateway/models/jev. Hosts Jev as `typesafe-ai/jev`.
15. **Jev Agent**, https://jev-agent.com/api-access. Unofficial hosted gateway for Jev and 12 other decision models. `/api/v1/systemone` (TypeSafe shape), `/api/v1/decisions` (OpenAI Decisions shape), `/api/v1/classify` (eight published Jev rulesets). Also an MCP server and a no-key playground; 5 free credits a month. Not affiliated with TypeSafe AI.
16. **Umpirix**, https://github.com/caelum0x/umpirix. Self-hostable Apache-2.0 typed-decision server with its own in-process engine (CPU int8 ONNX embedding classifier, lexical fallback; no API key or database). Wire-compatible with TypeSafe's API: official SDKs work via `TYPESAFE_BASE_URL`. Ships an MCP server and CLI classifier. Formerly named OpenJev. Independent.
17. **stuntd**, https://github.com/bladedevoff/stuntd. Local proxy on open Laya that speaks the Jev API. Records answers from a Jev upstream, trains a per-question head, and serves it with a calibrated threshold and upstream fallback.
18. **Bud Decision Studio**, https://github.com/BudEcosystem/Bud-Decision-Studio. Open-source cross-platform desktop runtime and playground from Bud Ecosystem for running, evaluating, managing, and training Jev-like models locally, with a `/v1/systemone` API. Supports 10+ decision models.

## 5. SDKs & Clients
Clients for the `/v1/systemone` API, official first. Most were written for TypeSafe's hosted Jev. Official TypeSafe SDKs also work with compatible servers such as Ollaya and Liquid d1. Community packages are unaffiliated unless noted.

1. **Python SDK**, https://github.com/typesafe-ai/typesafe-sdk-python. Official. `pip install typesafe-sdk`. Docs: docs.typesafe.ai/sdk/python. The community `typesafe-ai` PyPI package is a redirect shim; install `typesafe-sdk`.
2. **JavaScript / TypeScript SDK**, https://github.com/typesafe-ai/typesafe-sdk-js. Official. `npm install @typesafe-ai/sdk`. Docs: docs.typesafe.ai/sdk/javascript.
3. **System One adapter (Python)**, https://github.com/typesafe-ai/system-one-adapter-python. Official drop-in `TypeSafeClient` replacement backed by LLM APIs, for comparing Jev with chat models on the same questions. `pip install system-one-adapter`.
4. **Vercel AI SDK provider**, https://ai-sdk.dev/providers/ai-sdk-providers/typesafe-ai. Package `@ai-sdk/typesafe-ai` plus `experimental_evaluate`. Model `jev-latest` or Gateway ID `typesafe-ai/jev`.
5. **Pydantic AI**, https://pydantic.dev/docs/ai/api/models/system_one. `pydantic_ai.models.system_one` sends typed questions to any `/v1/systemone` endpoint; provider docs for TypeSafe Jev and other models.
6. **Milvus Model**, https://github.com/milvus-io/milvus-model. Python reranker adapter sending candidate documents as Jev Noul questions in one request; sorts scores and keeps original indices.
7. **Elixir SDK**, https://github.com/nshkrdotcom/typesafe_sdk. Community Hex package `typesafe_sdk` for `system_one` and model listing (hexdocs.pm/typesafe_sdk).
8. **Jev (Elixir OTP)**, https://github.com/dannote/jev. Hex package `jev`. Jev as a peer GenServer; answers arrive as messages to pattern-match; network-free tests.
9. **Ruby SDK**, https://github.com/joshmn/typesafe-sdk. Community Ruby 3.1+ client: Noul/Choice/Score, retries, model listing, thread-safe pooled HTTP. No async client.
10. **RubyLLM TypeSafe**, https://github.com/kieranklaassen/ruby_llm-typesafe. TypeSafe provider for RubyLLM 2 with offline model metadata and typed responses.
11. **typesafe-ai-rails**, https://github.com/GenieRobot/typesafe-ai-rails. Unofficial Rails integration on the community Ruby gem: configuration, usage and cost telemetry, opt-in confidence policies.
12. **Rust SDK (typesafe-ai-rs)**, https://github.com/gilljon/typesafe-ai-rs. Independent async and blocking client.
13. **TypeSafe AI for Rust**, https://github.com/Twister915/typesafe-ai. Rust client: async and blocking transports, typed responses, observable retries.
14. **typesafe-rs**, https://github.com/AbdelStark/typesafe-rs. Latency-focused Rust transport SDK targeting behavioral parity with official clients.
15. **s1-rs**, https://github.com/AbdelStark/s1-rs. Rust derive layer for Choice/Score/Noul; typed question sets; confidence gates; network-free tests.
16. **Advocaat**, https://github.com/pithings/advocaat. Small TypeScript client with tagged helpers for chances, choices, scores.
17. **Scala / ZIO SDK**, https://github.com/jamesward/zio-typesafe-ai. Community ZIO client with a small DSL for noul, choice, score.
18. **.NET SDK**, https://github.com/saibimajdi/typesafeai-dotnet-sdk. Community client for typed questions and confidence-scored answers.
19. **PHP SDK**, https://github.com/Butochnikov/typesafe-sdk-php. Unofficial PHP client: typed DTOs, promises, exceptions. Used by the Laravel package.
20. **Laravel TypeSafe Jev**, https://github.com/Butochnikov/laravel-typesafe-jev. Unofficial Laravel 12/13 integration: config, facade, scoped DI, recording fake on the PHP SDK.
21. **jev-go**, https://github.com/Gaurav-Gosain/jev-go. Unofficial Go client for typed judgments and calibrated probabilities. `go get github.com/Gaurav-Gosain/jev-go`.
22. **Stumble/jev-go**, https://github.com/Stumble/jev-go. Unofficial dependency-free Go SDK for TypeSafe direct and Vercel AI Gateway: typed questions, retries, interactive CLI, installable agent skill.
23. **jevclient**, https://github.com/AboveColin/jevclient. Unofficial async Python client (`pip install jevclient`) with typed Noul/Choice/Score helpers; separate from the official SDK.
24. **LlamaIndex Jev**, https://github.com/WiktorB2004/llama-index-jev. Unofficial LlamaIndex reranker (`JevRerank`) and router (`JevSingleSelector`/`JevMultiSelector`) on the official Python SDK.
25. **Swift SDK**, https://github.com/ainame/swift-typesafe. Unofficial Swift 6.4 client aligned with Python SDK 0.6.0 API, including Linux.
26. **TypeSafe AI Swift SDK**, https://github.com/alterhq/typesafe-sdk-swift. Unofficial dependency-free Swift 6 client: strict concurrency, configurable auth and retries, network-free tests.
27. **System One Foundation Models**, https://github.com/peterfriese/system-one-foundation-models. Unofficial Swift 6 bridge mapping Apple's `@Generable` types to Noul, Choice, Score. Backends: hosted Jev, HTTP Laya, on-device Core ML Laya. Confidence routing.
28. **discern**, https://github.com/doeixd/discern. Unofficial Effect library: Choice/Noul/Score answers become typed patterns with an explicit `Uncertain` branch. Recording, replay, caching, call budgets as middleware. Provider-neutral; reaches Jev via `@effect/ai-typesafe`.
29. **kojev (Kotlin Multiplatform)**, https://github.com/ItisNoMatter/kojev. Community client for JVM, Android, iOS. Choice and Score answers map to your own enums. Maven Central: `io.github.itisnomatter:kojev:0.1.0`.
30. **jev4k**, https://github.com/pambrose/jev4k. Unofficial JVM Kotlin client: Choice, Score, Noul as a DSL with typed values including enums. Maven Central: `com.pambrose:jev4k`.
31. **hunch**, https://github.com/steven-shoemaker/hunch. Unofficial Python library (with TypeScript port) turning Choice/Score/Noul into functions over lists and DataFrames (classify, score, check, where, extract, pick, rank, verify). Deduplication, caching, optional LLM escalation for unsure rows.
32. **pydecide**, https://github.com/gopaljigaur/decide. Unofficial Python client (`pip install pydecide`) sending one question set to hosted Jev, OpenRouter, OpenAI Decisions API, Laya, Laya MLX, or a sentence-transformers reranker. Falls through an ordered chain on errors or low confidence; records which backend answered. Ships a `/v1/systemone` server.
33. **JevT++**, https://github.com/wiatrM/jevtpp. Unofficial C++20 library: compile-time enum schemas, typed decisions with abstention, local Laya backends, optional TypeSafe HTTP client. Tests use mocks and loopback HTTP, not live-provider validation.
34. **solvi**, https://github.com/solvi-ai/solvi. Unofficial Python runtime with a System One adapter. Jev, another decision model, an LLM, or a local checkpoint proposes typed answers; hard checks and calibrated thresholds decide, abstain, or escalate to a person. Hash-chained replayable traces.

## 6. Applications
Open-source products and demos that put a decision model in a real loop. Most use Jev.

1. **MemSearch**, https://github.com/zilliztech/memsearch. Markdown memory for coding agents, with optional Jev Noul reranker and a published English/Chinese retrieval evaluation. Community integration, not an official SDK.
2. **Jev-Mem**, https://github.com/libingzheren/Jev-Mem. Unofficial agent memory system: Jev or local Laya controls memory organization, query routing, retrieval budgets, candidate scoring, stopping; an LLM writes answers. Paper: arxiv.org/abs/2609.23986 (LoCoMo results).
3. **Jev RAG**, https://github.com/aifabrice/jev-rag. Unofficial local-first knowledge search. SQLite BM25 or agent-planned lexical retrieval; Jev Noul for evidence reranking; reproducible NFCorpus evaluation. No vector DB by default.
4. **JevGPT**, https://github.com/sunyasheng/JevGPT. Unofficial research agent from paper arxiv.org/abs/2610.18272. GPT-5.5 plans research; Jev uses Choice to locate answer lines and Noul to check document relevance, in parallel. Includes BrowseComp-Plus and NeuCLIRBench reproduction code. Successor of Jev Deep Research.
5. **Jev Ultrafast**, https://github.com/browser-use/jev-ultrafast. Browser agent from Browser Use. Jev picks an operation and DOM element in one request; a small LLM writes text only for `TYPE_TEXT`. Zürich to London on Google Flights in ~7 s. Library, inspector, measurements.
6. **Jev Social**, https://github.com/socai-io/jev-social. Browser-grounded social research. Jev selects bounded Instagram, TikTok, LinkedIn search/read operations; socai executes in the user's Chrome. Unofficial.
7. **Jev Web Analyzer**, https://github.com/replynodes/jev-web-analyzer. Analyzes a public SaaS landing page as Markdown and asks Jev ten bounded Choice questions about first-visit understanding, including the first change to make.
8. **Jev Account Filter**, https://github.com/caiweihan/jev-account-filter. Unofficial video-platform account screening with OpenRouter Jev 1.14. Noul ranks first-page titles; Choice classifies Top-N thumbnails plus metadata. For dataset curation and research.
9. **jev-align (Sutro)**, https://github.com/sutro-sh/jev-align. Unofficial active-learning CLI. Evaluates CSV, Parquet, JSONL rows with Jev; asks humans to label uncertain and audit samples; uses GEPA to propose better definitions.
10. **JevSpan**, https://github.com/lzq-0529/jev-span. Unofficial zero-shot NER for Chinese and English. Code enumerates candidate spans; Jev Choice nominates, verifies, fixes boundaries. Each entity keeps a probability and decision trace.
11. **Jev for Chrome**, https://github.com/chy4pro/jev-for-chrome. Unofficial Chrome extension (Manifest V3) port of Jev Ultrafast. Runs via OpenRouter, TypeSafe, or Cloudflare. Includes a 17-task headless Chromium suite with recorded traces.
12. **jev-ego**, https://github.com/romaluev/jev-ego. Browser agent on ego lite (lite.ego.app). One TypeSafe request picks operation and indexed element. Observe/act/suggest/step CLI.
13. **jev-browser**, https://github.com/Ying-Kai-Liao/jev-browser. Unofficial browser automation: LLM plans the outcome; Jev decides each click/type on a Playwright snapshot (~300 ms/call). Library, CLI, MCP server (`npx -y -p jev-browser jev-browser-mcp`).
14. **Sedum**, https://github.com/sedum-dev/sedum. Unofficial AI testing tool for Playwright. Jev picks each action in goal mode; Choice finds elements for plain-English steps; verifies claims as two Nouls (holds, contradicted). Clicks, waits, exit codes deterministic.
15. **typesafe-computer-use**, https://github.com/awlevin/typesafe-computer-use. macOS computer-use loop: OCR the screen, Jev classifies the next action, then click. About $0.0002 per step.
16. **Yappy**, https://yappy.biz/jev/. macOS voice agent (closed source; public write-up with measurements). Jev picks operation and target from the accessibility table each step; chat model writes text only for typing; full agent takes over when confidence drops. Author-reported: 275–690 ms per decision; $0.003 for five.
17. **Mobile Jev**, https://github.com/droidrun/mobile-jev. Android agent on Mobilerun; Jev decides each tap. Example: Uber SFO to Golden Gate payment screen in ~21 s over 9 actions. Live studio, CLI, traces. No ADB.
18. **Unclutter**, https://github.com/kitze/unclutter. Chrome/Firefox extension: Jev classifies nonessential page elements; local template rules hide them on later visits.
19. **jevMail**, https://github.com/ilyamk/jev-gmail-ai-spam-filter-and-labeling. Unofficial Gmail spam filter, auto-labeler, inbox organizer: Jev reads intent to apply custom labels; optionally archives high-confidence unwanted mail.
20. **HA-Jev**, https://github.com/AboveColin/HA-Jev. Unofficial Home Assistant integration: typed questions about entity state become sensors and automation actions; target picker; usage, cost, daily-budget entities.
21. **Every**, https://github.com/sufianetaouil/every. Semantic code-search CLI: yes/no question against every function, ranked by Noul probability.
22. **JevPDF**, https://github.com/kylemclaren/jevpdf. Unofficial "Ctrl+F by meaning" for PDFs: pdf.js extracts lines in-browser; Jev answers one Noul per line; matches highlighted and ranked.
23. **DocJev**, https://github.com/jerryjliu/docjev. Document classification and splitting: LiteParse extracts page text locally; Jev predicts category or boundaries in a packet. Visual report over 40 real government documents.
24. **tax-doc-classifier**, https://github.com/kyotofin/tax-doc-classifier. Tax-page classifier from a production pipeline: one Jev request per page chooses among 261 IRS forms and 7 page kinds using a JSON file of descriptions. About $0.001 per page.
25. **blink**, https://github.com/ellipsis-dev/blink. Codebase search: an ensemble of walkers asks Jev which file answers a natural-language query.
26. **Jev Search**, https://github.com/superagents-lab/jev-search. Unofficial web search app: Jev Choice and Noul select sources, time ranges, query candidates; results retrieved via Search1API.
27. **Jev Reranker (Rust CLI)**, https://github.com/shinpr/jev-reranker. Unofficial JSON-in/JSON-out CLI using Jev Noul to rerank results, filter documents without usable evidence, or extract passages.
28. **jevsearch**, https://github.com/kylemclaren/jevsearch. Unofficial shadcn/ui site-search block: keyword hits first; one Jev request re-ranks top 20 with a Noul per page, a Choice for best answer, and a Noul for whether any page answers.
29. **jev-research-pipeline**, https://github.com/shimo4228/jev-research-pipeline. Unofficial experimental research monitor: Jev screens papers against open research questions (Noul gates, Score dimensions); code applies thresholds; Qwen writes notes into an Obsidian vault.
30. **neo4jev**, https://github.com/jexp/neo4jev. Neo4j graph navigation: at each node Jev chooses which relationship to follow; beam search over log-probabilities.
31. **hono-jev-router**, https://github.com/yusukebe/hono-jev-router. Experimental Hono router: Jev matches requests to plain-language route descriptions.
32. **sqlite3-jev**, https://github.com/mattn/sqlite3-jev. SQLite C extension: `jev_noul`, `jev_choice`, `jev_score` as SQL functions via libcurl.
33. **jevql**, https://github.com/kylemclaren/jevql. Unofficial psql-style CLI and Go/TypeScript/Python SDKs for vanilla Postgres: `jev()`, `jev_prob`, `jev_choice`, `jev_score` in plain SQL, no extension. SQL runs on server; Jev judges surviving rows in batches.
34. **pg-jev**, https://github.com/realZachi/pg-jev. PostgreSQL extension: `jev()`, `jev_prob`, `jev_choice`, `jev_score` filter, rank, classify rows with plain-language conditions. No embeddings or vector column.
35. **jev-resilience**, https://github.com/Vicente-MD/jev-resilience. Unofficial Spring WebFlux starter: semantic circuit breaker using Jev to catch silent HTTP 200 failures.
36. **tripwire**, https://github.com/noelzappy/tripwire. Unofficial AI SDK middleware and OpenAI-compatible proxy: seven Jev checks per LLM response in ~100 ms, confidence-gated.
37. **ProgressGate**, https://github.com/AshutoshVJTI/progressgate. Detects semantic stagnation in agent loops. Jev judges trajectory; code returns CONTINUE, WARN, REPLAN, or HALT.
38. **jev-harness**, https://github.com/AntonioCoppe/jev-harness. Unofficial production layer around Jev: policy, confidence gate, shadow mode, recipes, eval CLI.
39. **jev-tree**, https://github.com/reachjalil/jev-tree. Recursive Choice over a taxonomy so catalogs larger than Jev's 255-option cap still fit.
40. **jev-shell-history**, https://github.com/mrnugget/jev-shell-history. Fish-style zsh autosuggestions: Jev ranks recent history as you type.
41. **Supercov**, https://github.com/supercorp-ai/supercov. Code quality and test coverage for coding agents: Jev scores each source file so the agent knows what to fix first.
42. **jev-lint**, https://github.com/ckorhonen/jev-lint. Unofficial fuzzy linter for Claude Code and Codex: Jev flags team-rule violations at edit time; configurable rule packs; repo-specific rules.
43. **Jev Review**, https://github.com/devagrawal09/jev-review. Staged code-review workflow and local dashboard driven by focused Jev calls.
44. **Foreman**, https://github.com/thruwire/foreman. Software-factory loop: Codex implements; Jev independently judges completeness, tests, and whether a human is needed.
45. **Jev Drone**, https://github.com/RomanSlack/jev-drone. MuJoCo quadrotor: control and safety in code; Jev handles slower tactical judgments.
46. **Jev Plays StarCraft**, https://github.com/phyous/tsai-sc. Structured-state harness for the original StarCraft shareware campaign, with verified run and probability traces.
47. **Jev × Civilization II**, https://github.com/phyous/tsai-civ2. Original Civ II in a browser; Jev chooses empire, city, research, unit actions. Experimental; no verified win yet.
48. **Jev Trade**, https://github.com/aowang-ai/jev-trade. Live Hyperliquid desk: each tick Jev answers Choice questions (long/short, open/close/hold, leverage); code places or pulls quotes. Dry-run by default; a live key sends real orders. Demo: jev-trade.com.
49. **Jev Trader**, https://github.com/jarrodwatts/jev-trader. One buy/sell decision per Monad block on Kuru's MON-USDC book. Demo: jev-trader.vercel.app.
50. **Human Compiler**, https://github.com/asfarsadewa/human-compiler. Paste corporate prose; Jev scores passive-aggression, urgency, information density; code emits rustc-style diagnostics. Live: human-compiler.asfarlab.fun.
51. **Jev Wrapped**, https://github.com/gaborishka/jev-wrapped. Telegram channel X-ray: Jev judges up to 1,500 public posts from the last year with one Choice over ten post kinds and three Noul checks (paid ad, clickbait, emotional pressure). Shareable card. Live: wrapped.ivanhabor.com.
52. **JEVMETER**, https://github.com/ChetasLua/jevmeter. Live Jev meter on any video: every sentence scored, rendered as a 16:9 edit. Demo link is an X post.
53. **jev-audio-beeper**, https://github.com/santos-sanz/jev-audio-beeper. Low-latency audio insult detector: Jev decides; ffmpeg beeps in ~466 ms without rewriting the track.
54. **jev-askable-arm**, https://github.com/TarunTomar122/jev-askable-arm. Zero-shot English goals on a simulated Franka arm; Jev chains hardcoded primitives.
55. **Codex Jev Router**, https://github.com/suenot/codex-jev-router. Codex subagent routing: Jev chooses model and reasoning effort from Choice and Noul answers; code applies confidence gates and falls back to Sol.
56. **Jev Auto Router**, https://github.com/miniLV/Jev-Auto-Router. Unofficial model-routing prototype: Jev picks model and reasoning effort per call, via local Responses proxy, with independent task verification.
57. **jev-router**, https://github.com/gargpratyush/jev-router. Per-turn routing for Claude Code and Codex: simple work to fast tier, hard work to strong tier. `npm i -g jev-router`.
58. **jev-secret-detection**, https://github.com/teyhouse/jev-secret-detection. Secret-in-diff detector with repeatable Jev verdicts.
59. **commit-miner**, https://github.com/devanshbatham/commit-miner. Rust CLI classifying commit diffs with Jev: bug fixes, security/CWEs, change types. HTML and CSV reports.
60. **jev-eval-agent**, https://github.com/vinilana/jev-eval-agent. Public eval harness for early Jev tests.
61. **Jev Logs**, https://github.com/reachjalil/jevlogs. OpenTelemetry log triage: Jev scores diagnostic value and priority before an expensive LLM reads the archive.
62. **Smart home assistant demo**, https://docs.typesafe.ai/demos/smart-home. Official interactive demo of speculative fan-out (docs.typesafe.ai/patterns/fan-out).
63. **jev.nvim**, https://github.com/valentynkit/jev.nvim. Neovim plugin: splits buffer into functions with Treesitter, scores each against a plain-language question with Jev, ranks answers in the quickfix window.
64. **jev-skip**, https://github.com/valentynkit/jev-skip. Browser extension reading YouTube captions; paints per-segment sponsor probability on the seek bar before the intro ends; no crowd database. Reports catching 77% of SponsorBlock's sponsor seconds across 23 videos, at $0.0008 per video.
65. **JevBystander**, https://github.com/Nisaka520/JevBystander. Android accessibility app reading the visible WeChat chat and sending one batched Jev request (10-way intent Choice, 9-way emotion distribution, 0–3 urgency Score, 11-way reply-posture Choice) to show three toasts. No generated reply, no input injection, no screenshot or OCR.
66. **Jev Chat Assistant**, https://github.com/jev-chat/jev-chat-jarvis. Unofficial Android chat copilot: accessibility service reads QQ, X, or Feishu/Lark chats (Feishu via on-device OCR); one batched Jev request asks intent, needs, next-action Choice, danger Score, three Noul checks; a chat model drafts three replies; code fills the picked reply into the input box without sending.
67. **Paper Radar**, https://github.com/Eliot5566/JEV-Paper-Radar. Unofficial daily arXiv and bioRxiv radar: Jev answers one Noul per plain-English interest per paper; code applies thresholds; publishes a page and RSS feed from GitHub Actions. Live demo (eliot5566.github.io/JEV-Paper-Radar/public/) needs no key.

## 7. Demos & Games
Toys, live sites, and realtime agents.

1. **Yes / No**, https://yesno.coderai.dev. Free no-signup Noul demo: yes/no/maybe answers, with web search when needed.
2. **TypeSafe AdBlock**, https://github.com/realZachi/typesafe-adblock. Chrome extension demo: Jev judges DOM elements and removes likely ads. BYOK, no backend. Each page consumes API tokens; author documents missed ads and mistaken removals.
3. **Jev Tetris**, https://jev-omega.vercel.app. Jev picks rotation and column from holes, stack height, bumpiness.
4. **Jev Pac-Man**, https://jev-pacman.ephraimduncan.com. Maze as JSON; Jev picks the turn at each junction in real time.
5. **Jev Chess**, https://jevchess.com. Shared board, internet vs Jev. Each legal move is one Choice; probabilities shade pieces; live calibration panel scores every move.
6. **Chess with Jev**, https://chriswijnia.com/lab/chess. Chess and Chess960 in the browser: code lists each legal move's facts; Jev picks one per turn as a Choice, candidates drawn as arrows. Source: github.com/cwdx/chess-with-jev.
7. **typesafe-mario**, https://github.com/fhshaik/typesafe-mario. Super Mario Bros. from structured emulator state.
8. **jev-doom-agent**, https://github.com/lukaske/jev-doom-agent. Browser-native Doom (Chocolate Doom WASM) with spatial state and live decision telemetry.
9. **jev-gomoku**, https://github.com/mizchi/jev-gomoku. MoonBit client plus Jev-vs-Jev gomoku. Write-up (Japanese): zenn.dev/mizchi/articles/jev-plays-gomoku.
10. **jev-t-rex-runner**, https://github.com/joshlarsen/jev-t-rex-runner. Chrome dinosaur game played by Jev.
11. **snake-jev**, https://github.com/siroccomask/snake-jev. Snake: hundreds of typed direction decisions per run.
12. **Jev Guard**, https://guard-jev.vercel.app. Comment-moderation playground.
13. **jev-fit**, https://jev-fit.com. Paste a software idea; Jev answers a fixed typed rubric in one call; page says plain code, Jev, or a reasoning LLM, with probabilities. Unofficial, closed source; free page and API.
14. **Hollow Creek**, https://hollow-creek-sigma.vercel.app. Village NPCs judge the player each tick (actions, feelings) instead of chatting.
15. **Jev mood demo**, https://jev-demo.vercel.app. Talk nicely or nastily over time; structured state tracks mood.
16. **Jev Room**, https://jev-room.moe136231.chatgpt.site. One sentence becomes six room settings; Jev chooses, the app renders.
17. **1 Million Emojis**, https://chriswijnia.com/lab/emoji. Shared 1000×1000 emoji canvas; after each stroke Jev picks an adjacent square and its emoji as one Choice. Source: github.com/cwdx/1-million-emojis.
18. **Jevvie**, https://chriswijnia.com/lab/jevvie. Page companion: the page offers its actions as WebMCP tools; one Choice picks the action the visitor means, with a Choice per argument; asks back when the top two are close. Source: github.com/cwdx/jevvie.
19. **TypeSafe Typewriter**, https://typesafe-demo.val.run/. Live Val Town demo: 16 typed judgments update as you type. Launch post by Steve Krouse (x.com link).
20. **jev-got**, https://github.com/phureewat29/jev-got. Game of Thrones roleplay as Jon Snow: a story model writes scenes; Jev answers location, danger, and music.
21. **Little Airways**, https://github.com/lbotinelly/jev-little-airways. Toy archipelago ATC: Jev judges divert, emergency, and landing order from each plane's local state, ~150 ms.
22. **jev-plays-pokemon-red**, https://github.com/valentynkit/jev-plays-pokemon-red. Pokémon Red on PyBoy: deterministic code owns route and arithmetic; Jev picks only at branches; each battle turn's faint prediction scored by Brier against emulator RAM.
23. **Jev Plays Pokémon Red**, https://github.com/christianmat/jev-pokemon. Harness reads Game Boy RAM and lists legal options; Jev picked every move and beat the game in 37h 40m over 16,150 decisions, about $1.65.
24. **jev-canvas**, https://github.com/gaborishka/jev-canvas. Draw on a tldraw canvas with voice and a webcam-tracked finger; Jev decides action, target, place on each partial transcript. English and Ukrainian commands.
25. **Jevtown**, https://github.com/gaborishka/jevtown. Town of 10,000 computed personas reads your post. Jev scores audience to pick the first 600 readers; one Choice per persona gives a reaction; code advances waves only while glad readers outnumber annoyed ones by at least a tenth. Live: jevtown.ivanhabor.com.
26. **sudoku-vs-jev**, https://github.com/zebedelu/sudoku-vs-jev. Terminal Sudoku: Python enforces rules; Jev picks one move per turn; steady on forced moves, shaky when guessing.
27. **chess-vs-jev**, https://github.com/zebedelu/chess-vs-jev. Pygame chess: python-chess enforces rules; Jev picks one legal move per turn. Modes: Human vs Human, Human vs Jev, Jev vs Jev.
28. **JevsBistro**, https://github.com/andrewsilber/JevsBistro. Deterministic 3D restaurant simulation replaying one dinner service to compare rule-based, camera-assisted, and Jev-planned waiters; logs state, options, confidence, latency.
29. **jev-asks-until-sure**, https://github.com/mintannn/jev-asks-until-sure. Twenty Questions where confidence sets the stopping rule: Jev commits, hedges, or refuses. Live: jev.mintan.org.
30. **Jev × 2048**, https://jev-2048-ultra.vercel.app. Web lab where Jev is the 2048 decision engine, showing each move's probability distribution, confidence, latency, and token cost.
31. **Book Aurora**, https://github.com/dani1005/book-aurora. Jev reads a novel: each passage gets nine emotion scores plus intensity in one call. Frankenstein: 601 passages, 6,010 typed decisions, about 25 s and 3 cents; exports a poster.
32. **FlightBench**, https://github.com/AlperKartkaya/FlightBench. Fixed-wing landing simulator and benchmark: four Jev Choice decisions map to aircraft controls; compares against human-pilot, baseline, and LLM controllers.

## 8. Agent Tools
Tools that expose decision models to coding agents and MCP clients.

1. **TypeSafe agent skill**, https://github.com/typesafe-ai/skills. Official skill: primitives, patterns, structuring evaluations. Claude Code: `claude plugin marketplace add typesafe-ai/skills`, then `claude plugin install typesafe@typesafe-ai`. Other agents: `npx skills add typesafe-ai/skills --skill typesafe-ai`.
2. **fast-jev-compaction**, https://github.com/tamaratran/fast-jev-compaction. Claude Code plugin and npm library: Jev scores tool calls and drops stale ones instead of summarizing context.
3. **SkillRanker**, https://github.com/Dicklesworthstone/skillranker. Rust CLI: Jev ranks which agent skill fits the next step from live session context; Claude Code hooks.
4. **langchain-skill-router**, https://github.com/deyna256/langchain-skill-router. LangChain deepagents middleware for per-turn skill routing from catalogs of hundreds of SKILL.md files; pluggable judge; falls back to full catalog on failure. `pip install "langchain-skill-router[jev]"`.
5. **jev-skill-router**, https://github.com/shimo4228/jev-skill-router. Unofficial Claude Code hook asking Jev which installed skill fits each prompt; logs (shadow mode) or adds a hint (inject mode). Includes author's one-week shadow log and why the router was removed.
6. **JevRouter**, https://github.com/BillionsBobby/JevRouter. Unofficial router putting models, subagents, skills, MCP tools, CLIs in one candidate set: one Choice; code enforces availability, permissions, risk, confirmation. On 10 Toolathlon tasks, position-wise hits 38–44% for Jev vs 24% for DeepSeek V4.1 Flash.
7. **JevLoop**, https://github.com/zjunlp/JevLoop. Unofficial agent loop: sends each fork (tool, risk, done) to Jev 1.13.0; LLM still writes. With no key falls back to local Laya, then rules. `npm run demo` runs offline.
8. **Jevbridge**, https://github.com/tacticocc/Jevbridge. Unofficial ACP/MCP adapter: typed Jev decisions and computer use beside Codex, Claude, Grok, OpenCode.
9. **eve**, https://github.com/vercel/eve. Vercel's agent framework. Experimental `autoModel` defaults to Gateway `typesafe-ai/jev` to pick a model from an allowlist.
10. **jev-mcp (Node)**, https://github.com/jkudish/jev-mcp. Node MCP wrapping three cookbook patterns: `jev_verify` (citation check), `jev_screen` (prompt injection/guardrails), `jev_find` (semantic ranking without embeddings). `npx -y github:jkudish/jev-mcp`.
11. **Jev MCP (Python)**, https://github.com/blakestone-x/jev-mcp. Python MCP server: classify, score, check, match, screen tools.
12. **Jev Review MCP**, https://github.com/NiazMorshed2007/jev-review. Local-first MCP: Claude Code, Codex, Cursor, OpenCode get structured quality review from Jev while they write. Not the same project as the Applications entry "Jev Review".
13. **System One Connector**, https://github.com/itsmostafa/system-one-connector. Go CLI and single-binary MCP server (formerly typesafe-mcp): gives Claude Code, Claude Desktop, Codex, Hermes, pi typed decisions from Jev, d1, CLM, or Laya.
14. **pi-typesafe**, https://github.com/DevMortimer/pi-typesafe. Pi extension: one consented, key-managed TypeSafe client; batched `typesafe_evaluate`; offline-testable transport.
15. **pi-jev**, https://github.com/y0usaf/pi-jev. Pi extension with a shadow-mode tool-call gate, output judge, typed `jev_ask`.
16. **pi-warden**, https://github.com/DevMortimer/pi-warden. Pi guardrails on pi-typesafe: held tool results instead of a dialog; write checks against a project rules file.
17. **pi-jev-auto-mode**, https://github.com/jomatsu/pi-jev-auto-mode. Pi auto mode: Jev semantically approves `bash`, `write`, `edit`; fails closed when undecided.
18. **Bicameral**, https://github.com/AbdelStark/bicameral. Pi coding harness: LLM writes; Jev supplies typed reflexes for policy, loop detection, review. Explicitly not a sandbox.
19. **jev-pref**, https://github.com/doeixd/jev-pref. Turns AGENTS.md preferences into a Jev-powered linter: project-specific semantic rules in `jev-pref.json`, checked against hunks, staged files, or PRs. `npx jev-pref setup`.
20. **hermes-jev-skills**, https://github.com/kerpopule/hermes-jev-skills. Hermes pack, also for Claude Code and Codex: Jev handles model routing, skill choice, search, memory, compaction. About 0.4 s per routing turn; about 2.8 s to pick among 377 skills. Measured: a handoff digest recalled less than the plain transcript, so handoffs keep the dialogue.
21. **jev-system-architect**, https://github.com/samtay32/jev-system-architect. Skill finding brittle semantic logic and turning it into Choice/Score/Noul boundaries.
22. **augustus**, https://github.com/24601/Augustus. Unofficial augustus and augustus-train agent skills for application-specific decision models: primitive, base-model, and method selection; data assembly; fitting; export/reload; bounded improvement; independent evaluation. TypeSafe Jev is the default hosted exemplar.
23. **jev-axi**, https://github.com/shiftynick/jev-axi. CLI plus Claude Code and Codex hooks: Jev scores each shell command for hazards before it runs; screens fetched text for prompt injection; routine commands decided locally, nothing sent.
24. **jev-engineering**, https://github.com/eugeniughelbur/jev-engineering. Decision layer for coding agents: deterministic rules first, then one Jev request; delivered as a Claude Code hook, MCP server, loopback service, or shared team policy. Ships a 300-call injection test.
25. **toolgate**, https://github.com/RiskAverseTech/toolgate. Unofficial tool-call firewall for Claude Code hooks and MCP servers: Jev answers seven risk questions per call; code maps to allow/ask/deny; fails closed; tracks write-then-execute across a session.
26. **OnlyRead**, https://github.com/onlyreadai/onlyread. Unofficial Chrome extension keeping AI agents read-only on chosen sites: asks Jev whether each request would change data and blocks those; uncertain cases go to a second model.
27. **Jevonian**, https://github.com/xinyao27/jevonian. Local OpenAI/Anthropic/Responses-compatible proxy: one Jev call picks model route and thinking level for `jevonian/auto` from session state; code filters candidates and owns thresholds; pinned models skip Jev; each decision logged with model, reason, token usage, and cost estimate.
28. **jev-opus**, https://github.com/WXK-AI/jev-opus. Unofficial CLI and Claude Code gateway: runs Claude Code on Opus 5.5; asks Jev typed Choice/Score/Noul questions per prompt and after each tool batch to set reasoning effort; code enforces floors and ceilings and keeps the prompt cache.
29. **jev-belay**, https://github.com/valentynkit/jev-belay. Claude Code Stop hook: checks transcript evidence before trusting "done"; spends one four-question Jev call only when files changed with no passing check since; fails open on errors.
30. **jev-commit**, https://github.com/valentynkit/jev-commit. Pre-commit hook: one Jev call checks whether the commit message matches the staged diff, flags debug leftovers and unmentioned work, blocks only on a detected credential.
31. **strayguard**, https://github.com/Eve2512/Strayguard. Pre-commit hook: one Choice per new file flags scratch scripts, output dumps, build output, and local-only files.
32. **jev-use**, https://github.com/shitianfang/jev-use. Claude Code, Codex, pi plugin: Jev answers batched typed questions in an agent loop; a typed escalation contract hands writing and low-confidence steps back to the LLM.
33. **dsh-jev-tools**, https://github.com/HorusJiang/dsh-jev-tools. DeepSeek Harness plugin: Jev prunes oversized tool output, screens pages for injected instructions, picks skills; provides `jev_ask` and `jev_gate` tools.
34. **slop-grader**, https://github.com/lukstei/slop-grader. Rule-based CLI and agent skill grading text for AI slop, grammar, technical-doc quality against custom rulesets; guides an agent to auto-fix violations. Not a Jev tool.
35. **pytest-jev**, https://github.com/allebee/pytest-jev. pytest plugin for semantic assertions on LLM output: each plain-English claim becomes a Jev Noul in one request; passes at p ≥ 0.8; failures print every claim's probability; `choice` and `score` cover routing and rubric checks.
36. **jgrep (kyu1204)**, https://github.com/kyu1204/jgrep. Semantic grep for code, git diffs, CSV rows: one Noul per 5–60 line chunk, 16 chunks per Jev request; grep-style file:line output and exit codes for CI lint rules written in English.
37. **jevgrep (allebee)**, https://github.com/allebee/jevgrep. Streaming grep-by-meaning for logs: one Noul per line against a plain-English question; prints lines at or above a threshold, including from `tail -f`.
38. **jevgrep (dzhng)**, https://github.com/dzhng/jevgrep. Code-search CLI and agent skill: Jev judges relevance across folders, files, declarations; `jg` returns files, leads, verbatim excerpts. In the author's ten-task SWE-bench comparison it solved the same 8 tasks as baseline at about 30% lower cost.
39. **wellposed**, https://github.com/suraj-phanindra/wellposed. Offline linter and agent skill for Jev requests: 40 structural checks with no model call (e.g., missing none-of-the-above options, broken state paths, wrong criteria shapes); Jev-on-Jev checks for what structure cannot decide; labelled corpora score both layers.
40. **jev-auto-approve**, https://github.com/BasmaAbouzied0/jev-auto-approve. Claude Code PreToolUse hook: one Noul per Bash command on whether it is strictly read-only; auto-approves at p ≥ 0.95; otherwise falls back to the normal prompt; never denies. Local hard-no list and injection filter. Published calibration: 0 of 8 state-changing commands approved.
41. **jev-secret-guard**, https://github.com/BasmaAbouzied0/jev-secret-guard. Claude Code PreToolUse hook stopping agents writing or sending secrets: known key formats blocked locally; unknown high-entropy strings sent to Jev as a Noul in masked form. p ≥ 0.80 blocks; 0.30–0.80 or any Jev error asks the human. Published calibration: 6 of 6 secrets blocked, 0 of 6 benign strings blocked.

## 9. Benchmarks & Evaluations
Leaderboards first, then single-task studies and tooling. Most studies measure Jev.

### 9a. Leaderboards
1. **Jev Decision Index**, https://huggingface.co/spaces/multimodalart/jev-decision-index. Hugging Face Space comparing Jev with open decision models on a versioned suite, with calibration metrics and documented methods. Open-model inference timings and Jev's hosted HTTPS latency are not directly comparable.
2. **JevBench**, https://github.com/fstandhartinger/jevbench. MIT-licensed harness and leaderboard of 534 English decisions with public and sealed tiers. Reports accuracy, latency, and price together. Discussion: news.ycombinator.com/item?id=49800574.
3. **Jevals.com**, https://jevals.com/. Independent benchmark of hosted Jev and six LLMs on the same Noul, Choice, Score questions, graded against human labels (PubMedQA, Banking77, HelpSteer2). Per-decision logs published as open data.
4. **LangWatch Jev benchmark**, https://langwatch.ai/compare/jev-benchmark. Jev vs seven open models under 1B parameters on 15 decision tasks, with 95% intervals, latency, and contamination checks.
5. **Decision Models as Guardrails**, https://dm-as-guardrails.raxitlabs.com. raxIT Labs benchmark of 29 decision models (including Liquid d1-ultra and d1.1, Jev, Kev, Laya, Clef, Strands Deciders, Microsoft-Decision-1, Drex, Mercury Decide, Solar Decide, Span-02, Perplexity and OpenAI Decisions APIs) plus Amazon Bedrock Guardrails. Same 9,975 labelled guardrail checks; one fixed 0.5 block threshold. Reports balanced accuracy with 95% intervals, cost per 1,000 checks, per-row results.
6. **System 1 Decision Benchmark**, https://github.com/etsabary/system-1-decision-benchmark. Independent comparison of hosted and local decision models plus no-reasoning LLM references on 1,342 text questions; per-category accuracy, response times, cost, route details.
7. **Visual Decision Benchmark**, https://github.com/etsabary/visual-decision-benchmark. Independent comparison on 200 image-grounded questions across 20 categories: accuracy, latency, cost, image provenance.

### 9b. Studies
1. **typesafe-ai-benchmark**, https://github.com/iammrduncan/inference-benchmarks. Side-by-side of Jev vs Qwen 3.8 27B on Cerebras for the same System One questions. Video post on X.
2. **Jev Rerank Bench**, https://github.com/anessbelbati/jev-rerank-bench. Reranking comparison with raw provider responses, scoring code, uncertainty intervals, documented limits.
3. **Jev Spam Eval**, https://github.com/bitnovus/jev-spam-eval. Exploratory zero-shot spam study vs trained TF-IDF baselines, with post-hoc tuning caveats.
4. **Jev × NASA Kepler**, https://gist.github.com/ipaulsmith/e5c3ae3a492a455435d5bfc161404312. Independent retrospective test of Jev 1.13 on 8,054 historical Kepler Objects of Interest, with NASA Exoplanet Archive dispositions hidden during prediction. 72.5% archive-disposition match vs 64.4% for a fixed 3-rule baseline. Exact requests, metrics, baseline, caveats included.
5. **Jev Phishing Bench**, https://github.com/anisselbd/jev-phishing-bench. 2,000 emails: Jev vs Claude Haiku 4.5 on click-or-not, with calibration, latency, cost. Haiku wins on accuracy.
6. **jev-agent-failure-benchmark**, https://github.com/TokenTrim/jev-agent-failure-benchmark. Who&When Pro (injected agent failures): Jev vs a strong LLM on who, which step, and error category.
7. **jev-sec-bench**, https://github.com/Gaurav-Gosain/jev-sec-bench. Blind prompt-injection and vulnerable-code detection benchmarks on public corpora, built on jev-go.
8. **ASSAY-001**, https://github.com/jourdanlabs/assay-001. Independent pre-registered check of Jev calibration and type safety on Banking77 and CLINC150. Split verdict; full logs. Write-up: donttrustme.ai/assay-001.html.
9. **Jev search rerank eval**, https://github.com/zhuyansen/jev-search-rerank-eval. 9,831 labelled pairs: Jev rerank vs BM25 and bge-m3, with judge circularity measured. Fusion wins; Jev alone does not beat embeddings.
10. **Smoking-history extraction benchmark**, https://github.com/vclic/smoking-extraction-benchmark. 1,000 synthetic notes: Jev vs OpenAI structured outputs on accuracy, cost, latency.
11. **jev-fanout-bench**, https://github.com/blowxian/jev-fanout-bench. Batched vs separate Jev calls across 2,976 requests via OpenRouter; about 261 fixed input tokens per request; charges match published rate; answer differences comparable to repeat-request noise.
12. **minimind-jev**, https://github.com/vicfei/minimind-jev. Train-your-own tiny Jev for Chinese reranking: frozen bge-small-zh plus a from-scratch 660K decision head; 3 minutes on a laptop GPU; $0 API. Evaluated via jev-rag-zh-benchmark (github.com/vicfei/jev-rag-zh-benchmark) on T2Reranking hard negatives (n=100, 95% paired CIs): nDCG@5 0.488, not separable from hosted Jev-1.13 at this n, significantly above BM25. Documents a distillation negative result (teacher soft labels lost to gold binary labels). Releases teacher-judgments dataset (huggingface.co/datasets/cnfeichen/t2reranking-4level-judgments) and checkpoint (huggingface.co/cnfeichen/minimind-jev-v0.1).
13. **ProbabilityBench**, https://github.com/ishida-lab/ProbabilityBench. Evaluates Jev, Perplexity Decider, others against exact instance-level class probabilities in three simulated text domains (peer review, covert information transfer, credit risk); KL divergence. Paper: arxiv.org/abs/2610.17016.

### 9c. Tooling
1. **JevalKit**, https://github.com/Valen-Team/JevalKit. Open evaluation toolkit for Jev-like models: unified model interfaces; prepared text, image, video benchmarks. Leaderboard distinguishes full evaluations from smoke tests and imported predictions (huggingface.co/spaces/Valen-Team/JevalKit-Leaderboard).
2. **System One Playground**, https://github.com/goodboybeau/system-one-playground. Local Apple Silicon workbench comparing Laya, Decider, Kev, Jev, and others side by side; public-dataset accuracy and calibration; input-truncation diagnostics; latency, memory, load tests.
3. **Jev DSPy Lab**, https://github.com/jmanhype/jev-dspy-lab. Unofficial DSPy companion: records and replays TypeSafe calls while measuring calibration, selective risk, confidence-gated abstention, latency, tokens, modeled cost.
4. **jevcal**, https://github.com/abhixhek/jevcal. Unofficial CLI: fits a per-question confidence threshold to a target accuracy on your labeled data; verifies on held-out split; shows LLM-fallback traffic; fails CI when a Jev update breaks locked thresholds.
5. **jevals**, https://github.com/openlayer-ai/jevals. Openlayer's agent evals and guardrails as decision questions (tool choice, grounding, relevancy, injection). Runs on Jev, or locally on Kev, Laya, or Eikos. `pip install jevals`.
6. **s1kit**, https://github.com/Eliot5566/s1kit. Unofficial Python CLI: runs one YAML suite of labelled cases against any `/v1/systemone` server (Jev, Laya, Kev, llama.cpp, Ollama) side by side; picks a per-question confidence cutoff for a target precision; routes cheapest-first with escalation.

## 10. Papers
The README lists 9 papers. It gives arXiv IDs (in the URLs) but no author lists or venues.

1. **Typed Decision Models: An Early Evidence Audit and Evaluation Checklist**, arXiv 2609.32160, https://arxiv.org/abs/2609.32160. Reviews 28 papers from the first days after Jev's release. The typed readout shows no independent accuracy advantage over comparable label-probability readouts; clearest gains are latency and cost. Derives a 14-item evaluation checklist.
2. **Jev in the Wild: A Data-Driven Analysis of the Jev Model's Functionality, Applications and Ecosystem**, arXiv 2609.30216, https://arxiv.org/abs/2609.30216. First data-driven survey of Jev's application ecosystem across 2,170 public GitHub projects: early growth, application domains, decision-use patterns.
3. **Evaluating and Benchmarking the System One Model Jev**, arXiv 2609.37647, https://arxiv.org/abs/2609.37647. Zero-shot Jev 1.13 on 37 datasets (346,009 requests, under $10) vs Qwen3.8-27B and Gemma-4-E4B option probabilities. Jev beats Qwen on 27 of 37 and Gemma on all 37. Choice probabilities well calibrated; binary thresholds poorly placed. Code and raw responses released.
4. **Beyond Calibration: Do a Typed-Decision Model's Probabilities Obey the Probability Axioms?**, arXiv 2609.33209, https://arxiv.org/abs/2609.33209. Label-free coherence checks: Jev's "X" and "not X" probabilities miss summing to one by 0.064 on average, vs 0.293 for Qwen3.8-27B's first-token readout; single-label probabilities over-sum to 1.14.
5. **Evaluating System One Models for Agent Security Decisions**, arXiv 2609.33401, https://arxiv.org/abs/2609.33401. Jev, Laya, Decider, Nimble vs specialized classifiers and LLM judges on prompt injection and risk screening. Good aggregate calibration can hide confident failures concentrated in particular attack groups.
6. **JevAdvBench**, arXiv 2609.31142, https://arxiv.org/abs/2609.31142. First adversarial benchmark for decision models: 812 typed questions and 9,744 single-edit attacks. On Jev 1.13, one unverified opinion appended to the state flips 12.1% of decisions (this describes version 1 of the paper; version 2 reports 46.3% for the strongest attack, see Appendix B); the authors argue state should be treated as untrusted input.
7. **From Text Decisions to Pixels**, arXiv 2609.29283, https://arxiv.org/abs/2609.29283. PixelJev, a native-image decision interface on small open multimodal models. 64-shot adaptation lifts Pets accuracy from 60.13% to 92.40%; calibration does not follow accuracy gains.
8. **Chinese-Jev**, arXiv 2609.36965, https://arxiv.org/abs/2609.36965. Encoder-only System One model for Chinese, pretrained on 10 million examples, fine-tuned for medicine, law, finance; CJ-Bench benchmark. Authors report higher general-domain accuracy than Jev at a 20x speedup.
9. **Calibrated Decision Models for Autonomous Penetration-Testing Harnesses**, arXiv 2609.28940, https://arxiv.org/abs/2609.28940. Where Jev and Laya fit in LLM pentest agents: finding adjudication, severity recalibration, agent pruning, confirmation loops. Exploratory case study.

## 11. Articles
Independent measurements and experiments. A subheading "Community cookbooks" follows entry 9.

1. **Jev in Search: Three Practical Evaluations**, https://zc277584121.github.io/rag/2026/09/22/jev-search-deep-evaluation.html. Experiments on search stopping, memory reranking, multi-hop relation selection; limitations include private data, unequal sample counts, simulated speed illustration.
2. **Mini-Vibe Check: TypeSafe's Jev Judged Everything I've Written in 0.7 Seconds**, https://every.to/vibe-check/mini-vibe-check-typesafe-s-jev-judged-everything-i-ve-written-in-0-7-seconds. Every's Mike Taylor runs Jev over a writing corpus.
3. **TypeSafeのJevを正しく驚く、それってLLMでできませんか？** (Japanese), https://zenn.dev/nwn/articles/824026c76116e0. Reproduces the JSON-vs-logit shortcut on Gemma; compares Jev with LLMs on the public Mario harness.
4. **Jev: one judge call, or twelve dimension scores?**, https://agentjournal.dev/blog/llm-judge-vs-feature-extraction/. Measured on three classification tasks: one direct Jev question per row vs 12–14 Jev-scored dimensions with locally fitted weights; token costs, confidence intervals, false-positive rates.
5. **Testing Jev on public and private data: classifier or filter?**, https://amankumar.ai/blogs/jev-measured. 16,000 calls vs gpt-5.4-mini and gpt-5.6-luna; where it wins, where it breaks, threshold procedure.
6. **Is Jev as Accurate as Frontier Models at Classification?**, https://openrouter.ai/blog/insights/jev-vs-claude-opus-5-classification/. OpenRouter ran all 3,080 Banking77 test utterances through Jev 1.13 and Claude Opus 5: 81.0% vs 84.4% accuracy; 175 ms vs 2,266 ms median; about $0.11 vs $2.42 per 1,000.
7. **We Tested Jev on 791 Labeled Decisions Against Four LLMs**, https://www.ayautomate.com/blog/jev-vs-llm-benchmark. Independent OpenRouter run on 8-way and 77-way Banking77 routing plus prompt-injection detection. Jev matches small models and trails GPT-5.6 Terra by about 5 points on 77-way routing. A 0.80 confidence gate escalating the rest to Terra matches Terra's accuracy at about a quarter of the cost.
8. **Jev × LexGLUE**, https://github.com/chepyle/jev-test. Reproducible zero-shot run of Jev 1.13 (`typesafe/jev-1.13-20260917`) on all seven LexGLUE tasks, 23,607 test examples. Mean micro-F1 69.9 at $4.02, vs 71.3 at $16.45 for GPT-5.6 Luna via chat JSON.
9. **Jev Does Not Play Dice: 83% probability, 19% accuracy on a hidden fair die roll**, https://kantahayashiai.github.io/posts/jev-does-not-play-dice/. Calibration check on fair dice, coins, spinners (true probability known exactly) and synthetic forecast documents. Jev selects face 1 on all 400 die rolls, with 82.9% mean reported probability vs 19.0% accuracy. Code: github.com/KantaHayashiAI/jev-does-not-play-dice.

Community cookbooks:
10. **Milvus Search with Jev**, https://github.com/milvus-io/bootcamp/tree/master/bootcamp/RAG/search_with_jev. Nine runnable Python notebooks combining Gemini embeddings, Milvus retrieval, and Jev decisions for reranking, filtering, search stopping, routing, cache reuse, curation, guardrails, evaluation.

## 12. Related
1. **awesome-jev-prompts**, https://github.com/vicfei/awesome-jev-prompts. 51 field-tested Jev question patterns in 9 categories (including embodied/multimodal and anti-patterns), with templates, thresholds, failure modes; every entry sourced under a four-level verification policy. CC0; bilingual EN/中文.
2. **awesome-ai-quant**, https://github.com/vicfei/awesome-ai-quant. Reading map for AI engineers entering quantitative finance: trading agents, LLM factor mining, decision models in markets, tabular foundation models. Bilingual EN/中文.
3. **MrJev/awesome-jev**, https://github.com/MrJev/awesome-jev. Selective list behind a 10-star bar; hands-on reviews at mrjev.com/best-jev-tools/.
4. **Awesome TypeSafe Jev**, https://github.com/AbdelStark/awesome-typesafe-jev. Unofficial source-backed Jev field guide with a typed-decision walkthrough, community project cards, independent evaluation links, first-contribution path.
5. **laya.tools**, https://laya.tools. Unofficial directory of about 950 projects built on open Laya (GitHub, npm, Hugging Face, X), with a Laya vs Jev comparison. Not affiliated with TypeSafe or ConvAI.
6. **AgentPlugins JEV directory**, https://agentplugins-2v1.pages.dev/jev-plugins/. Cross-ecosystem plugin and tool directory ranked by GitHub stars (includes browser-use/jev-ultrafast, Laya, Kev, fast-jev-compaction). Also a tutorial (agentplugins-2v1.pages.dev/typesafe/) and a Laya vs Jev vs Kev comparison (agentplugins-2v1.pages.dev/laya-vs-jev/). Not affiliated with TypeSafe.

## 13. Contribute
Points to CONTRIBUTING.md. Summary: open a pull request adding a project with a link and a one-line description. Projects should be useful and built on or around a decision model.

## 14. License
CC0 1.0, public domain dedication (LICENSE file).

---

