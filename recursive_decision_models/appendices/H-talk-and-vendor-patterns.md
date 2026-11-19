---
id: H-talk-and-vendor-patterns
derives_from: []
---

# Appendix H — The talk, the speaker's code, and TypeSafe's official patterns

Retrieved 2026-11-12. `[TALK]` = the talk's transcript (YouTube auto-captions);
`[SPEAKER]` = Raymond Weitekamp's own blog post, repos and site; `[TYPESAFE]` =
official TypeSafe docs or blog; `[3P]` = third party. Code blocks marked verbatim
were relayed through a summarizing fetch tool and should be re-checked against the
source before being relied on character-for-character.

## H.1 The talk

- **Title:** "Your Agent Doesn't Need an LLM for Every Decision — Raymond Weitekamp,
  OpenProse". AI Engineer YouTube channel, published 2026-11-10, 51:48, video id
  `hFNbPmzzcEs`. Pre-recorded virtual talk. Its original title, per the opening
  line, was "recursive decision models"; he says it is "really" about "operating
  system one".
- **Links in the description:** recursivedecisionmodels.com, github.com/rawwerks/rdm,
  openprose.ai, oSo.computer, x.com/raw_works.
- **Chapters:** defining system one models; introduction to recursive models;
  architecting decision recursion; composition of AI primitives; rules and visual
  examples; visual search and recursion; games without reasoning; the role of
  generation; smart home application; shared interface and arbiter; implementation
  and tools; human-computer interaction; radical HCI and music; Earshot demo;
  Operating System One.
- **Blog post:** raw.works/recursive-decision-models/, dated 2026-10-01.
- **No latency, cost or accuracy comparison** of trees against single reasoning
  calls is given anywhere in the talk or the post. From the post: "the benchmarks
  will come only after I nail down a v1 of the RDM module."

## H.2 Definition and the three rules

**Definition `[SPEAKER, rdm README]`:** "A Recursive Decision Model (RDM) puts a
decision model in a loop. Its answers pick what happens next: a function runs, a
language model writes, or the same question is asked again about a smaller piece of
the state. That last one is the recursion. It is the idea of a Recursive Language
Model (RLM), for a model that decides instead of writing."

**Tagline `[TALK]`:** "a decision that can decide to make another decision." He
calls RDM "the marriage" of RLMs and Jev.

**The three "non-negotiables" `[SPEAKER, blog]`:**

1. "The RDM system must externalize context and be able to programmatically
   decompose slices of that context."
2. "The decision model must have the choice to call another decision model, up to
   some maximum depth of recursion."
3. "The RDM system must be able to work with and without the presence of any
   generative model or function. In other words, it must stand alone as 'pure
   decision models' and also compose with LLMs and agents."

Rules 1 and 2 are, in his words, "copied straight from the RLM idea." Rule 3 exists
because using a decision model as a tool for an agent is "obvious", and the
no-generation case "proves that the RDM architecture is actually correct."

**Mapping to RLMs `[TALK]`:** in an RLM the root calls sub-RLMs, depth is capped,
and at maximum depth the leaf is a plain LLM call. In an RDM the root can call a
sub-RDM, and at maximum depth it makes "a single system one call." He contrasts two
layouts:

- *Decision as a tool* — an agent calls a decision model. Within about 24 hours of
  Jev's release people had built compaction judges, tool-call gates and model
  routers this way.
- *Decision model as root* — his focus. An LLM or agent is only one of the options
  the root can choose.

**Framing:** generation diverges, decisions converge. Recurring question: "what if
reasoning was actually many small decisions?" TypeSafe's own position, which he
accepts, is that Jev makes judgments and "your code makes the decision."

## H.3 Mechanics

**Loop `[SPEAKER, rdm README, verbatim]`:**

```text
call(request):                         a request is a state and typed questions
    answers <- predict(request)        asked once, and never again
    for each tool the answers select:  the tools run at once
        observation <- tool(...)       inside a tool, calling the module is a sub-call, one level down
        if an output pointed at it:    the same question again, about the state as it is now
    return answers, observations
```

**Minimal Python version `[SPEAKER, blog, verbatim]`:**

```python
import dspy
class RDM(dspy.Module):
    def __init__(self, signature, tools, max_depth=3):
        super().__init__()
        self.predict = dspy.Predict(signature)
        self.tools = {tool.__name__: tool for tool in tools}
        self.max_depth, self.depth = max_depth, 0
    def forward(self, **inputs):
        answers = self.predict(**inputs)  # one request to the decision model
        observations = {}
        if self.depth < self.max_depth:
            self.depth += 1  # anything a tool calls is one level deeper
            for name, tool in self.tools.items():
                if answers[name].value:  # a yes runs the tool of the same name
                    observations[name] = tool(**inputs)
            self.depth -= 1
        return dspy.Prediction(observations=observations, **answers)
```

**How the pieces work `[SPEAKER, dspy.experimental.RDM reference and rdm README]`:**

| Piece | Behaviour |
|---|---|
| Node | One request: a signature whose outputs are typed decisions (Noul, Choice / `Literal`, Score), answered once, with probabilities |
| Children | Enumerated by **code**, not the model. A tool (plain function) slices state and calls the module again (`call.rdm` in Python; `call.sub` / `call.batch` in Rust) |
| Selecting a tool | An output named after a tool runs it on a yes or on a chosen option. An output typed `dspy.Tool` is a "pointer" at any tool or at `finish`; after a pointed-at tool runs, the same question is asked again on the updated state |
| Tool arguments | Never written by the model. Filled by name from the request's other answers, then its inputs: "an argument the model should choose is one more question" |
| Defaults (DSPy) | `max_depth=3` (depth at which tools are not run; first call is depth 0), `max_iters=20` (turns of one pointer loop), `max_predictor_calls=256` per run including sub-calls, `max_tokens=None`, `finish=True`. Blog examples use `max_depth=10`; the Rust example `.max_depth(6)` |
| Stopping | No answer selects a tool; `finish`; `max_depth`; a repeated identical request; or a limit. `termination_reason` ∈ `final`, `repeat`, `max_depth`, `max_iters`, `max_predictor_calls`, `max_tokens` |
| Robustness | A one-option choice is answered without asking. A failing tool becomes an observation, not a crash |
| Return value | The call's answers and probabilities, `observations`, `termination_reason`, and on the root a `trajectory` (every request with depth, parent, tool name, inputs shown, outputs with probabilities, model, tokens) |
| State | Held in code. `rdm(..., state=...)` is readable by tools and shown to no request; Rust has `Shared<T>` |
| Thresholds | Per question (examples use 0.7 and 0.3), stored on predictors, re-fittable by `ReAnchor` (changes only numbers; no prompts, no model calls) |
| Helpers | `RDM.Fit` cuts a long input or over-long option list to what one request holds, deciding with the same model. `RDM.Near` is a map with readable dimensions that offers only the nearest names. `RDM.Filter` sorts what the model rated. `RDM.Repl` is a sandbox where an LLM writes functions that land on the map |
| LLM fallback | A language model is "a tool like any other". "The language model chooses nothing that happens": it runs only when a decision selects it, and its output is a candidate checked by caller code |

**The map `[TALK; SPEAKER]`.** "A decision model can only point, so something has
to say what it is pointing at." A map is a set of names, each with a description
for the model and a thing for the code. Maps can change at runtime and nest. He
says this interface is the part he is "still wrestling with."

**The arbiter `[TALK; SPEAKER, Rust only]`.** Because decision calls are cheap,
many are run speculatively in parallel; the arbiter gates which results may write
to state, to avoid colliding writers (his analogy: many readers, locked writes). In
Rust, `Arbitrate` makes each ruling one decision request: yes/no per tool, plus a
choice of finish / wait / start one more / say what is not known. No Python
counterpart exists.

## H.4 The demos, with what was actually shown

| Demo | Whose | What happens | Numbers | Speaker's own caveat |
|---|---|---|---|---|
| Handbook halving search | Speaker | One Noul ("is the answer in this text?") over a 71-line handbook, halving on yes | 15 requests | "a terrible way to actually solve this problem" |
| Outline walk ("the shape of RLM") | Speaker | Handbook stays in Python as an outline; each request shows one entry plus the headings under it. No LLM configured | 15 requests; largest shows 272 of 2,555 characters | — |
| Shopify taxonomy, "hierarchical search, without the beam" | Speaker | Recursive classify over 12,378 categories (see code below) | Reaches the cookbook's expected leaf in 8 requests; ~20 lines vs ~150 in TypeSafe's cookbook | "I am not claiming that this is 'better' in any way." One example |
| Galton board | Speaker | Visualization of pins that decide | — | Concedes it could be one classifier call |
| Visual recursive search | Others | Zooming into image hits; recursively halving an image | — | Concedes a good vision model might do it in one shot |
| Doom | **TypeSafe's launch clip**, replayed | Two coupled compositions: first-person (hold, carry on, walk, dodge) and map-aware exploration | TypeSafe: ~10 queries/s, ~$7/hour, text-structured state not images | Called underdeveloped; TypeSafe itself says a non-AI bot could play better |
| Factorio | Speaker | Tree picks the failing group of lines, then the line, then the inserter, then replaces it. No LLM | none | "a little bit of a toy example" (identical lines); the agent "ran the long way around" for lack of path-finding |
| Browser / computer use | Speaker | Claim that pre-enumerated actions "might be enough" | The "three actionable elements" figure is **his own slides website only** | Not a general statistic |
| Smart home | Speaker, adapted from TypeSafe | Simulated house that pushes back (thermostat refuses while a window is open → close window → set thermostat) | A map with memory got **87%** of requests right vs **66%** for a map with none, over "a few simulated days" in a toy house, no LLM | One run retried the same command at every level until the request limit |
| Earshot / oSo | Speaker | Voice-first computer-use agent; an RDM decides when to trust a tiny supervised audio model | Reaction time "essentially 45 millisecond" | oSo is unreleased (waitlist only) |

The 87% vs 66% smart-home figure is the only accuracy-like number in the talk, post
or repos.

**The Shopify classifier `[SPEAKER, verbatim]`** — note the branching rule: follow
every child at least half as likely as the likeliest, then ask again among whatever
leaves came back. "There is no beam width and no path score."

```python
def classify(listing, category="All products"):
    under = taxonomy[category]
    if not under:
        return category  # a leaf
    odds = choose(listing, under)
    likely = [each for each in under if odds[each] >= max(odds.values()) / 2]
    print(category.rpartition(" > ")[2], "->", [each.rpartition(" > ")[2] for each in likely])
    found = [classify(listing, each) for each in likely]  # the same function, one level down
    odds = choose(listing, found)  # more than one came back: ask again, among those
    return max(found, key=odds.get)
```

## H.5 Released code

| Artifact | Language / license | Maturity | Notes |
|---|---|---|---|
| **github.com/rawwerks/rdm** | Rust (1.96+) / MIT | Created 2026-11-08; 4 stars, 2 forks; not on crates.io | Crates: `systemone` (wire protocol, `DecisionModel` trait), `one-system` (client/gateway for hosted Jev, OpenRouter, llama.cpp), `rdm` (the loop: `Signature`, `Tool`, `Rdm`, `Call`, `Filter`, `Fit`, `Near`, `Repl`, `lm`, `Rlm`, `reanchor`), `rdm-wasm`. 18 examples that run offline on deterministic stand-ins: `cargo run -p rdm --example handbook`. `RDM_TRACE=1` prints the call tree. Backends: hosted Jev (`TYPESAFE_API_KEY`), OpenRouter, an LLM acting as decider (`RDM_DECISION_MODEL=lm`), or local Laya via `llama-server -hf ggml-org/Laya-GGUF`. Depend with `rdm = { git = "https://github.com/rawwerks/rdm" }` |
| **github.com/rawwerks/dspy**, branch `feat/rdm-v0` | Python / MIT (DSPy) | Experimental fork branch, not merged upstream | `dspy.experimental.RDM`, the Python reference |
| **github.com/rawwerks/one-system** | TypeScript / MIT | Created 2026-09-21; 9 stars | "LiteLLM for Jev" gateway |
| **recursivedecisionmodels.com** | SvelteKit site | — | In-browser demos: /hierarchy, /smart-home, /notebook, /rdm, /models, /pinboard |
| OpenProse (`openprose/prose`) | — | 1.9k stars, MIT | Nothing released for recursive decisions |

**Bottom line on maturity:** the reference implementation was four days old, with
four stars, when this was written. Treat RDM as a design pattern with example code,
not as a library to depend on.

## H.6 Limitations the speaker states

- Pure-decision trees need every option pre-enumerated by code, another agent or
  the application: "there is no easy way to generate new decisions to make."
- Paths in pure trees are predefined and regular: "the shape of the data."
- The map interface is unsettled. A decision model asked what to keep "kept
  everything and never chose to forget." LLM-written map lines "have not beaten
  plain pointing in any project we have tried."
- With an LLM in the loop, runs can die by retrying one command until the request
  limit.
- "What is it good for?" — "I don't know."
- Option-order bias carries into pointers (tools are offered in list order,
  `finish` last).
- Thresholds are model-version-specific.

**Corrections to the widely shared secondary write-up (startuphub.ai, 2026-11-11):**
Doom was TypeSafe's demo, not the speaker's; "browser pages expose about three
actionable elements" refers to his own slides site; and the write-up omits the map,
the arbiter, the 87% vs 66% result and the request counts.

## H.7 TypeSafe's official composition patterns

From docs.typesafe.ai/patterns. TypeSafe's general position
(`concepts/how-to-build-with-system-one`): code owns control flow; use code when
you can; decompose state and questions into atomic ones; ask many questions per
request; combine answers in code or a classical ML model; route on uncertainty; do
**not** build agent `while` loops around the model. Questions in one request "are
evaluated independently and in parallel. One primitive's result does not become
hidden context that changes another primitive's result."

| Pattern | What it is | Thresholds given |
|---|---|---|
| Speculative fan-out | Put every question the code might need into one request (state is read once) and ignore the irrelevant answers. 13 batched questions are claimed 12.2x cheaper and 11.8x faster than 13 requests | e.g. `bug_severity.score > 1.5 and bug_repro.noul > 0.6` |
| Screen with a Noul first | A cheap yes/no gate before a stage that needs bigger state, an LLM or a person | `YES_ABOVE = 0.7`, `NO_BELOW = 0.3`; the middle band gets its own outcome |
| Companion Noul | A Choice always picks something, so add a same-request Noul asking whether *any* option fits. Preferred over an `other` option, which competes for probability | Example: a desk-lamp message gets Choice 0.96 but companion Noul 0.02 → general inbox |
| Routing by confidence (Score) | Low Score confidence → triage; otherwise route on score bands | `confidence < 0.5` → triage |
| Routing by probability | Per-action thresholds on the chosen option's probability | below 0.7 → human; `approve_transfer` needs > 0.9 |
| Composite scoring | Several Scores normalized and weighted in code | e.g. `0.40*py + 0.10*lead + 0.40*arch + 0.10*general` |

**Hierarchical classification cookbook** (numbers from `jev-1.14.0`, 2026-11-03).
One Choice per node over its direct children; greedy versus parallel beam with
`BEAM_WIDTH, MAX_DEPTH, EPSILON = 3, 12, 1e-9`. Path score is the geometric mean of
edge probabilities: `product(edge_probabilities) ** (1 / decisions)`. On three
single examples (CPC patents, Shopify, MeSH) **beam matched 3 of 3 and greedy 2 of
3** — greedy returned "Pet Chairs" for the Shopify example the talk uses. Three
examples are not a benchmark, and the Narrow Decision Models paper (Appendix B)
found beam no better than greedy on its routing task.

**SDE cascade cookbook** (1,000 scheduling tasks; cheap model → Jev rule checks at
`FIRE_T = 0.7` → escalation to a strong model):

| Configuration | Accuracy | Cost per 1,000 tasks |
|---|---|---|
| Cheap model alone | 92.6% | $0.16 |
| Cascade, 3% escalated | 94.9% | $0.26 |
| Cascade, 13% escalated | 96.5% | $0.49 |
| Cascade, 54% escalated | 98.1% | $1.31 |
| Strong model alone | 98.1% | $1.89 |

The Jev checks themselves cost $0.04 per 1,000 tasks. Vendor-run.

**Confidence fields.** `confidence` is derived from the probabilities, not an
independent accuracy estimate. Choice: `(p_max - 1/n) / (1 - 1/n)`. Score:
`max(0, 1 - Σ p_i·|i − m| / MAD_unif)` with `m` the most likely level. Noul has no
confidence field; use `|2p − 1|` if needed. For a Choice with a fixed option count,
confidence adds nothing beyond the top probability — threshold on the probability
of the option you will act on.

**Jaggedness (known failure modes), with TypeSafe's remedies:**

1. Literal reading → write exact conditions.
2. Math and numbers (counting, hex/RGB, interpolating) → do it in code.
3. Date/time comparison → extract parts via Choice, compare in code.
4. Indirection and double negatives → reduce hops, name the state.
5. Large state with irrelevant detail ("Jev suffers from context rot") → filter
   first.
6. Adversarial content in state can move answers → precise criteria, test edge
   cases.
7. Contradiction between instructions and criteria → align them.
8. Choice option order ("Jev leans toward the option that comes first") → reorder
   and check consistency.
9. Generation → use a generative model.

Modes 4, 5 and 8 bear directly on recursive trees: deeper trees mean more hops,
trees exist to keep per-node state small, and every node has an option order.

**Launch claims `[TYPESAFE blog, 2026-09-15]`.** Training method "Reinforcement
Learning for Calibrated Decisions" (RLCD); new architecture plus a parallel
sampler; parameter count undisclosed. Latency 70–500 ms end to end versus 3–329 s
for LLMs; homepage claim of 193.6x faster and 444.6x cheaper across four workflow
evals built by TypeSafe's own team. Independent replications found 40–49x cheaper
and ~3.5x faster against a frontier model (Appendix G). Above 255 options TypeSafe
uses a two-stage score-then-choose.

## H.8 jev-tree: the nearest prior implementation of taxonomy recursion `[3P]`

github.com/reachjalil/jev-tree — TypeScript, MIT, 10 stars, npm `jev-tree` 0.1.0,
Node 22+, created 2026-09-18. Walks root to leaf with one Choice per level. If a
node has more children than `maxFanout` (default 32, range 2–255), siblings are
partitioned into contiguous labelled buckets and the walk recurses into the picked
bucket. Defaults `maxDepth` 16, `maxCalls` 64, `timeoutMs` 8000. Greedy top-1 only:
no beam, no companion Noul, no confidence gate. On timeout, failure or budget
exhaustion it returns `reason: 'unavailable'` and never invents a leaf.

```ts
import { createJevTree } from 'jev-tree';
const tree = createJevTree({ maxFanout: 32 });
const result = await tree.select({
  state: 'Replica lag 47m on primary still accepting writes',
  question: 'Which incident type is this?',
  shape: { id: 'incidents', label: 'incidents', children: [ /* … */ ] },
});
result.ids;     // ['incidents', 'data', 'replica_lag']
result.reason;  // 'model' | 'unavailable'
```

Author's benchmark (synthetic: 320 leaves, 180 tickets):

| Method | Correct | Tail items (index >= 255) | Mean calls | Input tokens | Est. cost |
|---|---|---|---|---|---|
| Authored tree (8 → 8 → 5) | 180/180 | 90/90 | 3.0 | 357,583 | ~$0.015 |
| Flat list, auto-partitioned | 179/180 | 89/90 | 2.0 | 565,000 | ~$0.024 |
| Truncate to 255 options | 90/180 | 0/90 | 1.0 | 2,454,465 | ~$0.103 |

The useful observation: **the tree used three calls but about 7x fewer tokens**
than one 255-option request, because each node shows only a handful of option
descriptions. The caveat: a keyword baseline also scored 180/180, because the
signal was planted in the synthetic tickets.

Convergent idea `[3P]`: Sean Goedecke (2026-09-18) describes "tiered goals" for
Doom (nested loops at roughly 10 s / 5 s / 1 s / 100 ms) and "tournament sampling"
for more than 255 options.
