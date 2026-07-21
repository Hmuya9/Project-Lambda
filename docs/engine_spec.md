# Lambda Engine — Design Spec v1.1

## Why this design exists

The previous implementation failed four ways: output too generic, system overcomplicated, profile ignored, and — fatally — the workflow was built *around* one specific job description, so it broke the moment a new JD was pasted. The failure was visible in the code: a 20-section one-shot output contract, a 2,100-line regex validator counting "causal words", an aligner that injected hardcoded role-specific investigations, and prompts pleading "do NOT default to GPU fleet repair".

Two architectural rules fix this:

1. **The engine is fixed; a job description is data.** Nothing in the engine may reference a specific job, company, or stack. A new JD produces a new *mapping*, never a new workflow.
2. **The engine is also user-agnostic.** Lambda does not assume anyone's goal. **Nothing is tailored until intake has captured a Profile and a Market Intent.** The invariant thesis: the market pays for proximity to expensive problems, not for knowing technologies.

## One engine, three surfaces

- **CLI / Streamlit UI (this repo)** — staged reasoning via the Anthropic API: intake → decode → map → intersect → rank → plan → `plan.json`, then deterministic rendering.
- **Claude skill (`skill/lambda-targeted/`)** — the same pipeline run conversationally in a Claude session.
- **Dashboard (HTML)** — renders any `plan.json`: role decode, gap map, sprint board, positioning. Data-driven, offline.

## The stable core (never changes per JD or per user)

1. **Constitution** (`docs/constitution.md`) — the framework itself.
2. **Profile schema** — background, strengths, transferable patterns, gaps, evidence style, learning style, constraints, "must not invent" list.
3. **Intent taxonomy** — targeted / directional / exploratory.
4. **Backlog mechanics** (`data/backlog.md`) — domain-scoped expensive problems with stable IDs; grows (new IDs), never mutates. Other domains get their own backlogs built the same way.
5. **Evidence taxonomy** — repo, demo, diagram, failure-mode table, benchmark, postmortem, readme, writeup.
6. **Sprint Operating System** — weekly cadence, primary/secondary/stretch, completion criteria, one engineering page per question.
7. **plan.json contract** (`data/plan_schema.json`) — shared by pipeline, renderer, dashboard, and skill.

## Design principles (from the postmortem)

1. **Staged reasoning, small contracts.** Four focused model calls beat one giant schema. Depth per stage, not breadth per call.
2. **Rank in code, not in the model.** priority = importance × gap severity, foundations first — deterministic and testable.
3. **Validate structure, not substance.** JSON Schema plus a few cheap substance floors (non-empty "done when", no consumption-as-artifact, non-empty do-not-claim). If validation grows past ~100 lines, fix the pipeline instead.
4. **No overfit:** zero JD-specific and zero user-specific logic anywhere in the engine. Test: two very different JDs AND two very different profiles through the identical pipeline.
5. **No tailoring without intake:** missing profile or intent is a hard error, never a guess.
6. **No generic output:** every sprint names a concrete artifact with a "done when" a skeptical senior reviewer would accept.
7. **Profile is law:** transfers cite the profile; the "must not invent" list is enforced in positioning.
8. **Simple survives:** one JSON contract, one pipeline, one renderer, one template. If the system itself becomes work, it has failed.
