---
id: README
derives_from: [BRIEF]
---

# Recursive decision models — research package

Researched 2026-11-12. The subject is the pattern presented in Raymond Weitekamp's
talk "Your Agent Doesn't Need an LLM for Every Decision" (AI Engineer, published
2026-11-10; original title "recursive decision models"): replacing LLM reasoning
steps with trees or loops of small questions put to fast, non-generative *decision
models*.

## Start here

**[BRIEF.md](BRIEF.md)** is the document to hand to a session. It is self-contained:
what the technique is, what the evidence does and does not support, availability
(hosted, local, GitHub runners), prior art, academic research, benchmarks, cost
model, failure modes, and a fit-assessment procedure with a fixed answer format
(section 12).

The one-paragraph answer: decision models are real, cheap, fast and widely
available, and using one for a single routing, gating or classification decision is
well supported. The *recursive* part is one speaker's design pattern with four-day-old
reference code and no published measurement; the adjacent evidence on chaining
decisions is discouraging. Expect many use cases to come out as "decision model yes,
recursion no".

## Handing it to a session

Give the session `BRIEF.md` (and access to this directory for the appendices) with a
prompt along these lines:

```text
Read recursive_decision_models/BRIEF.md in full. Do not research the topic further;
the brief and its appendices are the source of truth, and where they are silent, say
so instead of guessing.

Use case: <describe the application: what is decided, from what input, among which
outcomes, how often, what happens when it is wrong, who or what can write the input,
what the current solution is and what it costs, what labelled data exists>.

Assess whether recursive decision models fit this use case by following section 12
of the brief, and answer in the format of section 12.6.
```

The more of the bracketed facts you supply, the fewer "unknown" entries come back.
Sections 12.1 and 12.5 list exactly which facts the assessment turns on.

## Contents

| Path | What it is |
|---|---|
| [BRIEF.md](BRIEF.md) | The research brief and fit-assessment guide |
| [appendices/A-ecosystem-inventory.md](appendices/A-ecosystem-inventory.md) | Inventory of the community catalogue of models, runtimes, SDKs, applications and tools |
| [appendices/B-academic-literature.md](appendices/B-academic-literature.md) | Paper-by-paper summaries; a 14-item checklist for judging any decision-model claim |
| [appendices/C-benchmarks.md](appendices/C-benchmarks.md) | Benchmarks, standings, how to run them, tooling for your own data |
| [appendices/D-cloud-availability.md](appendices/D-cloud-availability.md) | Hosted vendors, prices, limits, wire shapes, SDKs, integrations, data handling |
| [appendices/E-local-availability.md](appendices/E-local-availability.md) | Open models, hardware needs, runtimes, required software, license traps |
| [appendices/F-ci-github-runners.md](appendices/F-ci-github-runners.md) | Running a decision model in GitHub Actions: three designs, limits, security |
| [appendices/G-prior-art-and-critiques.md](appendices/G-prior-art-and-critiques.md) | Composition libraries (language, license, maturity), patterns, independent critiques, failure modes |
| [appendices/H-talk-and-vendor-patterns.md](appendices/H-talk-and-vendor-patterns.md) | The talk in detail, the speaker's code, the vendor's official patterns |
| [poc/](poc/README.md) | **Unrun** proposals: tree runner, accuracy-by-depth evaluation harness, example tree, two CI workflows |

## Status and caveats

- **The proof-of-concept code has never been executed**, not even for a syntax
  check. No environment existed. Contracts are at `v0`; see
  [poc/README.md](poc/README.md) for how to ratify them.
- **The field is eight weeks old.** Most figures come from preprints, vendors or
  single practitioners, and many are author-reported. Prices, limits, model versions
  and leaderboard positions were changing weekly. Re-check anything you will spend
  money or design effort on.
- **Sources conflict in places** (context limits, one vendor's price, compliance
  claims). Known conflicts are listed in Appendix D.7 rather than silently resolved.
- **Some papers were read as abstracts only**; they are marked in Appendix B.
- **Appendix A is a paraphrase of a community list**; its entries were not
  individually verified unless another appendix covers them.
- **Not legal advice.** License and contract observations (non-commercial weights, a
  revenue-capped license, an anti-distillation clause, restrictions on publishing
  benchmarks) are flagged for review, not interpreted.
- Markdown files carry `id` and `derives_from` frontmatter. None is marked as a
  source of truth and no dependency index was built; decide whether `BRIEF.md`
  should be one.
