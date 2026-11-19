---
id: E-local-availability
derives_from: []
---

# Appendix E — Running decision models locally

Retrieved 2026-11-12. `[O]` = the maker's own repo, model card or docs; `[S]` =
secondary source; "n/s" = not stated. All latency figures are the publisher's own
unless marked; nobody publishes a measurement on a plain 4 vCPU / 16 GB machine, so
CPU numbers below are on other hardware and are indicative only. One independent
study (Roussos, Appendix G) found local medians 3–7x slower than model-card claims.

## E.1 Short answer

**A developer can run a decision model on a laptop alongside normal work.**
Encoder-class models (Laya, Phocinae-Largha, jevos, Von, d1-omni) need about 1–5 GB
of RAM and answer in tens to hundreds of milliseconds on CPU or Apple Silicon.
Models of 4B–9B are comfortable on a 24–36 GB Mac or a 16–24 GB GPU. The 27B class
(Clef, Kev-27B, pplx-decider, d3) needs a dedicated 80 GB GPU unless quantized.

**The catch is accuracy, not hardware.** The models that fit comfortably on a
laptop CPU are the weakest: sub-1B encoders collapse before 100 options
(TypedBench), Laya's Banking77 score is 0.425 against Jev's 0.870, and its accuracy
degrades past about 20 options per question. This is precisely the situation in
which a *tree* of small decisions is attractive: keep each node to a handful of
options that a small local model can handle.

## E.2 Model comparison

| Model | Maker | Params | Weights license | Disk | Minimum hardware | Latency (publisher) | Context | `/v1/systemone` server |
|---|---|---|---|---|---|---|---|---|
| Laya (English) | Convai Innovations | 421M | Apache-2.0 | ~0.8 GB | CPU, 5 GB RAM | T4 39.5 ms/1 question; M3 Max (MLX) p50 13.4 ms; 56-core CPU 453 ms/4 questions | 512 | Yes (`laya-serve`, :8000) |
| Laya-multilingual | Convai | 322M | Apache-2.0 | ~0.65 GB | CPU, 4 GB RAM | T4 32.8 ms; MLX p50 7.4 ms; CPU ~0.5 s/5 questions | 1,024 (8,192 opt-in) | Yes |
| Laya-typed-decisions | Convai | 421M | Apache-2.0 | 0.85 GB | CPU, 5 GB RAM | 56-core CPU 441 ms/4 questions | 1,024 | Yes |
| Phocinae-Largha-150M | Phocinae Project | 144M | Apache-2.0 | 289 MB fp16 | 4 GB RAM, no GPU (peak 1.8 GB) | CPU 1 thread p50 1.64 s; 8 threads 8–20 decisions/s; RTX 5090 21 ms | 512 | Yes (:8155) |
| jevos v4/v5 | feder-cr | 0.9B | MIT | GGUF Q4_K_M 619 MB | CPU, ~1–1.4 GB RAM | 28–130 ms on a 16-thread laptop CPU | 8,192 | Yes (:8017) |
| Von 1.2/1.3 | wfzyx (V. H. Panisa) | 395M | Apache-2.0 | 1.5 GB fp32 (README says ~3 GB download) | CPU | 0.096 s raw p50 on 4 vCPU Xeon w/ OpenVINO; 0.34–0.36 s board p50; 0.023 s on A10G | 8,192 | Yes (`von serve`, Docker `ghcr.io/wfzyx/von:cpu`). **Archived 2026-10-19** |
| d1-omni-600M | Liquid AI | 587M | LFM Open License v1.0 (**$10M revenue cap**) | 2.35 GB safetensors; GGUF Q8_0 407 MB | n/s | none published by Liquid; 114 ms/1 question on a shared 8-vCPU Xeon `[S]` | 16,384 | Python `system_one()`; GGUF via llama.cpp |
| d1-3B | Liquid AI | 3.1B | LFM Open License v1.0 | n/s | n/s | M5 Pro 30 ms; RTX 4090 8 ms | 32,768 | not confirmed |
| GLiNER2.5-Decide | Fastino | ~340M | Apache-2.0 | n/s | CPU or GPU | n/s | n/s | No (Python library `gliner2`) |
| Kev-0.8B | Jared Palmer | 0.8B | Apache-2.0 | n/s | 4 GB GPU or any Apple Silicon Mac | M5 149 ms (28 ms cached), 5 questions | 8,192 | Yes (:8009) |
| Kev-4B | Jared Palmer | 4B | Apache-2.0 | GGUF Q4_K_M 3.0 GB, Q8_0 4.5 GB | 32 GB Mac or 16+ GB GPU | M5 721 ms (136 cached); H100 18 ms | 8,192 | Yes |
| Kev-9B / Kev-27B | Jared Palmer | 9B / 27B | Apache-2.0 | 27B: 51 GB bf16 | ~17 GB GPU / 80 GB GPU | 27B: H200 67 ms/6 questions | 8,192 / 65,536 | Yes |
| jev-style 0.8B | Chaoliang Yan | 0.8B | Apache-2.0 | GGUF Q4_K_M 0.53 GB; MLX 8-bit 0.8 GB | n/s | M1 Max (MLX) 0.15–0.2 s | 25,600 | Yes (:8765) |
| Strands Decider 2B | AWS Strands Labs | 1.9B | code Apache-2.0; weights n/s | n/s | 24 GB GPU for training | M3 Pro 153 ms; RTX 3090 115 ms | n/s | Yes (:8000) |
| Tev1 0.8B / 4B | Together AI | 0.8B / 4B | **"being finalized"** | 0.8–1.5 GB / 4.4–4.6 GB | n/s | n/s | ~2,000 effective | via Ollama (:11434) |
| Nimble 9B | Bespoke Labs | 9B | Apache-2.0 per Ollama; repo states none | 9.3–9.5 GB | 24+ GB Mac | M5 Max 91 ms; M5 Pro 444 ms median; H100 106 ms | 8,192 | via Ollama |
| Winnow-E4B / 12B | EldanRing | Gemma 4 E4B / 12B | Apache-2.0 | Q8_0 8.0 GB | 10–12 GB VRAM | 148 decisions/s on RTX 5070 Ti | ~65K tested | Yes (llama.cpp-based) |
| JevAlt Deem-4B | Mert Kaya | 4B | Apache-2.0 (site footer only) | n/s | CPU, ~3 GB RAM at Q4_K_M | n/s | n/s | Yes (`jevalt serve`) |
| Decision 2.0 Kai-0.6B … Vega-27B | vLLM Semantic Router | 0.6B–27B | Apache-2.0 | n/s | n/s | Kai 4.9 ms and Lux-9B 18.4 ms claimed "single GPU"; **measured 17–53 ms and 127–295 ms** on a DGX Spark `[S]` | 8,192 | via vLLM |
| Decision 3.0 d3-edge … d3 | vLLM-SR | 0.59B–26B | Apache-2.0 `[S]` | d3-mini 9.1 GB | d3-mini: 16 GB card | d3-edge 6.7 ms on MI325X `[S]` | 262,144 | Yes (vLLM nightly only) |
| Clef-flash | Cloudflare | 9B | Apache-2.0 | n/s | tested on one H200 | median 38.8 ms | 16,384 | Yes (SGLang image) |
| Clef | Cloudflare | 27B | Apache-2.0 | GGUF Q4_K_M 19.5 GB; BF16 54.1 GB | one H200 (BF16) | median 209.3 ms | 16,384 | Yes |
| pplx-decider-v1.1-27b | Perplexity | 26B | Apache-2.0 | ~49 GiB | CUDA GPU | n/s | 8,192 | No (Python only) |
| StartLux-Decision v1.1 | StartLux Labs | 0.8B–27B, 35B MoE | **CC BY-NC 4.0** | n/s | H200 used for timing | 25–52 ms | up to 256K | Yes |
| OpenJev 27B | independent | 27B | **CC BY-NC 4.0** | n/s | GPU | n/s | n/s | via llama.cpp |

Other open models that exist but were not profiled for hardware: Standard One
(3B/8B, license unclear), Intern-Decision (0.8B/2B/4B), Security-One 27B, Jeeves 9B
(PostHog), OpenThai-SystemOne 0.8B, Saina Helm 2/Omni 0.8B, Lev 4B, NanoJev 0.6B,
decider 2B, RSI-Jev 4B/27B, OneJev 0.8B–27B, WebJev 35B-A3B, Vev 4B/9B
(non-commercial), JEV-27B/9B (distilled from Jev), JevK5 2B/4B/9B, reflex 4B,
imajev 4B, NeoHorse-Jev-4B, WaterSheep, Wald-4B, Valen 0.8B–4B, Dwight 4B. See
Appendix A for one-line descriptions.

## E.3 Runtimes

| Runtime | What it is | Language / license | Maturity signals | Serve command | Notes |
|---|---|---|---|---|---|
| **Ollama >= 0.35** | General local model runner; `/v1/systemone` added 2026-09-28/29 | Go / MIT | Mainstream; latest stable 0.40.16 (2026-11-09) | `ollama pull nimble` then call `http://localhost:11434/v1/systemone` | Models `nimble` (9B), `tev1` (4B), `tev1:0.8b`, Clef builds. **Limits: 1–64 questions, 2–26 options, 2–10 score levels, 64 KiB body.** Not yet in the Ollama CLI or client libraries (HTTP only). TypeSafe SDK works with `TYPESAFE_BASE_URL=http://localhost:11434`, `TYPESAFE_API_KEY=ollama` |
| **llama.cpp** | `llama serve` exposes `POST /v1/systemone` | C++ / MIT | Mainstream | `llama serve -hf ggml-org/Kev-4B-GGUF` (or `:Q8_0`); Docker: `docker model run hf.co/ggml-org/Kev-4B-GGUF:Q4_K_M` | Supports Julia-1 (144M), Laya, Kev-4B, lev, OpenJev, Clef (Clef needs an unmerged PR) per the September launch post. The server README as read on 2026-11-12 instead names these natively served architectures: openjev, granite-switch, laya, clef, pplx-decider, vllm-decision2, vllm-d3, lfm2-d1, lfm2-d1-omni, h2o-lightning — so Clef now appears supported and Kev is not named. Per-model option caps (52 for openjev, 255 for most); 400 on an invalid request, 501 when the model is not a decision model. Published speeds are GPU only. A user reported "input (11982 tokens) is too large" with Clef and Kev |
| **LM Studio** | Desktop app and local server; documents a Jev-compatible `POST /v1/systemone` and an OpenAI-style Decisions endpoint (added to this appendix 2026-11-12, after the first pass missed it) | Proprietary app, free to use | Mainstream | Load a decision model, start the local server (default `http://localhost:1234`) | Requires "a loaded decision model, not a regular chat model"; follows llama.cpp's implementation. Its docs give no response example, limits, model list or minimum version. Optional bearer API tokens (0.4.0+). See `../poc/README.md` for use through an SSH tunnel |
| **Ollaya** | Ollama-style runner dedicated to decision models (29 families, each with its author's calibration) | Apache-2.0 | ~1.5k stars, 339 commits, single maintainer | `curl -fsSL https://ollaya.dev/install.sh \| sh`; `ollaya serve` (:11435) | Docker `ghcr.io/ollaya-dev/ollaya` (CPU), `:cuda`. Also serves `/v1/decisions` and an MCP server. Its own advice: without an NVIDIA GPU, start with `laya`. CPU latency across its catalogue ranges 0.3 s to **62 s** per five-question request |
| **laya-serve** | Laya's own server | Python / Apache-2.0 | Laya repo: 35.5k stars, 2,923 commits, v0.4.31 | `laya-serve` (:8000); Docker Compose files for CPU and CUDA in repo | Server caps Choice at 100 options; quality degrades past ~20 |
| **vLLM Jev** (mode-io) | vLLM-native serving on Linux and Apple Silicon | Apache-2.0 | 954 stars, 158 commits, no releases | `uv pip install '.[cuda]'`; `vllm-jev serve <model>` (:8795) | Mac serves one request at a time; Kev-0.8B can flip labels under concurrent batches |
| **SGLang** | `/v1/decisions` and `/v1/systemone` reading option probabilities from an ordinary chat model | Apache-2.0 | Mainstream | `python -m sglang.launch_server --model-path Qwen/Qwen3.8-27B --port 30000` | Validated only on one H200; probabilities uncalibrated and can shift ~0.07 between cold and cached requests |
| **sys1** | Rust server on candle | Rust / Apache-2.0 | 62 stars, 40 commits, single maintainer | `cargo install sys1 --features cpu`; `sys1 --model-id convaiinnovations/laya` (:3000) | CPU, Metal and CUDA builds; no published image or benchmarks |
| **laya.cpp** | Native C++ Laya on ggml | C++20 / MIT | 130 stars, 252 commits | `laya-cli --server --port 8080 --variant english` | CUDA, Vulkan, Core ML, CPU; automatic request batching; prebuilt binaries |
| **Laya-MLX / Laya-CoreML** | Apple Silicon ports | Apache-2.0 | 7.1k stars | `pip install laya-mlx` | Peak memory under 1 GB; ~5 ms per short decision on M3 Max (Core ML) |
| **Flide** | OmniJev's engine | Apache-2.0 | 472 stars, v0.1.15 | `flide serve --model OmniJev/OneJev1.6-0.8B` | NVIDIA only |
| **Unsloth Desktop** | Desktop app serving Laya and Clef | proprietary app | beta | `POST http://localhost:8888/v1/systemone` | CPU by default; first request 10–20 s, then "well under a second on most CPUs" |
| **Von** | Self-contained server | Python / Apache-2.0 | 922 stars, 220 commits, **archived** | `docker run --rm -p 8000:8000 -v von-hf:/data/huggingface ghcr.io/wfzyx/von:cpu` | Byte-compatible with the TypeSafe wire shape by its own claim; adds truncation headers and `--on-overflow refuse` |

**Training-free option.** Any ordinary open LLM can be turned into a decision
endpoint by reading the next-token probabilities of option labels: AnyJev (Nokia,
Apache-2.0, pre-alpha, exposes `/v1/decide` rather than `/v1/systemone`), SemIf
(MIT, CLI only), simple-jev (Featherless), SGLang's endpoints, and DiffusionGemma
Spaces. Probabilities from this route are uncalibrated. The academic audit
(Appendix B) finds no evidence that purpose-trained typed models beat this readout
on accuracy; the difference claimed is calibration.

## E.4 What fits where

**CPU only (the "4 vCPU / 16 GB" class, and standard CI runners).** RAM fits for
all of these; latency on 4 vCPUs is extrapolated.

- jevos 0.9B — the best-documented CPU option: 28–130 ms on a 16-thread laptop CPU,
  ~1–1.4 GB RAM. Accuracy trails Jev on harder tasks.
- Laya family — 4–5 GB RAM; roughly 0.2–0.6 s per multi-question request on CPUs.
- Phocinae-Largha 150M — 1.64 s single-threaded; estimate 0.2–0.5 s on 4 threads.
- Von — 0.1–0.36 s on 4 vCPU with OpenVINO (archived project).
- Runnable but unmeasured on CPU: d1-omni GGUF Q8_0 (407 MB), jev-style 0.8B
  (0.53 GB), Tev1 0.8B, Kev-0.8B, JevAlt Deem-4B (~3 GB RAM).
- **Not acceptable on CPU: 4B and larger** (seconds to a minute per request).

**Apple Silicon laptop, 16–36 GB.**

- Negligible footprint, fine on 16 GB next to an IDE and browser: Laya-MLX (< 1 GB,
  7–13 ms), Kev-0.8B (149 ms), jev-style 0.8B (0.15–0.2 s), Strands 2B (153 ms).
- Comfortable on 24–36 GB: Tev1 4B and Kev-4B (3–5 GB; 0.1–0.7 s), d1-3B (30 ms on
  M5 Pro), Winnow-E4B (8 GB), Nimble 9B (9.5 GB; 91–444 ms).
- Tight: Nimble on 16 GB; any 27B model at 4-bit on 36 GB (16–20 GB of weights
  leaves little headroom). Kev's own guidance for Kev-27B is a 96–128 GB Mac.

**GPU class.**

| GPU class | Runs |
|---|---|
| 4–8 GB or T4 | Laya (33–40 ms), Kev-0.8B, Phocinae |
| 16–24 GB (T4 16 GB, L4, A10G, RTX 3090/4090) | Kev-4B, d3-mini, Winnow-E4B, Strands 2B, Kev-9B (~17 GB), Nimble 9B; Clef Q4_K_M (19.5 GB) is marginal on 24 GB |
| 32–48 GB (RTX 5090, L40S, A6000) | Clef Q8_0 (28.7 GB) |
| 80 GB (A100-80, H100, H200) | Clef BF16, Kev-27B, pplx-decider, d3 |

**Approximate cloud GPU rental** (`[S]`, price-index summaries, Sep–Nov 2026): L4
$0.43–0.84/h; A10G ~$1.00–1.32/h; RTX 4090 $0.14–0.74/h; A100-80 $1.39–5.03/h; H100
$1.99–4.01/h at specialists and $6.88–12.29/h at hyperscalers; H200 from $3.75/h.
For scale: AIMultiple's benchmark priced a rented A100 at $1.673/h ≈ $40/day, and
$40 buys roughly a million hosted Jev decisions.

**Dedicated box or developer laptop?**

| Situation | Recommendation |
|---|---|
| Prototyping, pre-commit hooks, local dev loops, nodes with <= ~20 options | Sub-1B model on the developer's own machine. 1–5 GB RAM, no GPU. This is a portion of local resources comparable to a language server |
| Team-shared decision service, or 4B–9B models | One 16–24 GB GPU box (or a Mac with 32+ GB), or simply the hosted API |
| 27B-class accuracy on-premises (data cannot leave) | Dedicated 80 GB GPU server; otherwise use a hosted 27B (Clef on Workers AI, Perplexity) |
| Lowest effort, best accuracy per dollar today | Hosted API. At $0.02–0.24 per million input tokens, self-hosting wins only on privacy, offline use, fork-PR CI without secrets, or very high volume |

## E.5 Required software

- Python route: Python 3.11+, `transformers >= 5.15` and `torch` (d1-omni), or a
  project package (`pip install von-sdk`, `pip install laya-mlx`, `pip install
  "jev-style[mlx]"`, `pip install strands-decider`, `pip install "gliner2[local]"`).
  `trust_remote_code=True` is required for d1-omni — pin the revision.
- No-Python route: Ollama >= 0.35 or llama.cpp with a GGUF build; or a Docker image
  (`ghcr.io/wfzyx/von:cpu`, `ghcr.io/ollaya-dev/ollaya`).
- Clients: the official `typesafe-sdk` (Python) and `@typesafe-ai/sdk` (Node 22+)
  work against any compatible server by changing the base URL. Plain HTTP works from
  any language.
- d1-omni precision note: use float32 on CPU and float16 on GPU; bfloat16 changes
  0.8–1.7% of answers.

## E.6 License traps

- **Non-commercial weights:** StartLux-Decision, OpenJev 27B, Vev (CC BY-NC 4.0 or
  equivalent). Do not use at work without a commercial license.
- **Revenue cap:** the Liquid d1 family (LFM Open License v1.0) grants commercial
  rights only to legal entities — including affiliates under common control — with
  under **US$10 million annual revenue**. Qualified non-profits doing research are
  exempt. Larger companies need a commercial agreement with Liquid.
- **Unpublished or unclear licenses:** Tev1 ("being finalized"), Nimble (repo
  states none; Ollama says Apache-2.0), Strands Decider weights, JevAlt (footer
  only), Standard One, pplx-decider (Apache-2.0 but the card refers to a private
  repository).
- **Distillation from Jev:** TypeSafe's Master Customer Agreement (updated
  2026-09-23) §2.3(b) prohibits using its services or output "to perform model
  distillation" or to build a competing product. Models openly distilled from Jev
  outputs — jev-style 2B v4, autotrust JEV-27B/9B (and anything built on them, such
  as Security-One 27B via AutoJev) — carry provenance risk for a cautious legal
  team, even where their own license says Apache-2.0. Kev and Nimble explicitly
  state they used no Jev outputs. `stuntd`, which records Jev answers and trains a
  local head on them, is the same pattern applied to your own traffic and falls
  under the same clause.
- **Base-model licenses:** Qwen3/3.5/3.8 and Gemma 4 bases are reported as
  Apache-2.0 by the projects built on them.
- **Abandonment:** Von was archived three weeks after release; several projects are
  single-maintainer and weeks old. Pin model revisions and container digests.

## E.7 Sources

ollama.com/blog/ollama-now-supports-jev-style-decision-models ·
docs.ollama.com/capabilities/decision.md · ollama.com/library/nimble ·
ollama.com/library/tev1 · huggingface.co/blog/ggml-org/decision-models-in-llamacpp ·
huggingface.co/ggml-org/Kev-4B-GGUF · huggingface.co/ggml-org/Clef-GGUF ·
docs.sglang.io/docs/supported-models/decision_models · github.com/mode-io/vllm-jev ·
github.com/ollaya-dev/ollaya · github.com/alvarobartt/sys1 ·
github.com/lkarlslund/laya.cpp · github.com/mizorewww/laya-mlx ·
github.com/OmniJev/Flide · unsloth.ai/docs/models/decision-laya.md ·
github.com/NandhaKishorM/laya · huggingface.co/convaiinnovations/laya ·
github.com/jaredpalmer/kev · huggingface.co/vllm-sr/Decision-2.0-Kai-0.6B ·
recipes.vllm.ai/vllm-sr/d3-mini · huggingface.co/Cloudflare/clef ·
huggingface.co/Cloudflare/clef-flash · huggingface.co/fastino/GLiNER2.5-Decide ·
github.com/Phocinae/Phocinae-Largha-150M-v1 · github.com/feder-cr/jev ·
github.com/strands-labs/strands-decider · github.com/bespokelabsai/nimble ·
huggingface.co/togethercomputer/Tev1-4B-experimental ·
github.com/lawrence3699/jev-style · huggingface.co/LiquidAI/d1-omni-600M (and
`/blob/main/LICENSE`) · huggingface.co/LiquidAI/d1-3B · github.com/wfzyx/von ·
huggingface.co/wfzyx/von · huggingface.co/perplexity-ai/pplx-decider-v1.1-27b ·
github.com/StartLuxLabs/Startlux-Decision · typesafe.ai/legal/mca ·
pypi.org/project/anyjev

Not found during research: Umpirix (repo 404), Bud Decision Studio, LitJev, a
TurinTech Hugging Face collection (Ollama listings only).
