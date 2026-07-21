# Project Lambda

**The market pays for proximity to expensive problems — not for knowing Python or Rust** (tools matter, but as means). Project Lambda structures study around that thesis: it turns an **engineer profile** + a **market intent** into an evidence-driven plan — expensive problems decoded, gaps mapped against what actually transfers, weekly sprints that each end in proof-of-work, and honest positioning.

Lambda assumes nobody's goal. It is not "come become a better software engineer" — that is one possible intent among many. **Nothing is tailored until intake captures a profile and an intent:**

- **targeted** — "I want this job" (one job description)
- **directional** — "I want to be highly employable in domain X" (a market composite)
- **exploratory** — "I want to become more valuable overall" (narrowing intent is part of the work)

## Architecture

**The engine is fixed; the JD is data — and so is the user.** A new JD (or a new person) produces a new *mapping*, never a new workflow. Reasoning is staged, each stage with a small contract — not one giant schema policed by regex:

```
INTAKE (gate)   profile + intent — nothing tailored without both
   ↓
DECODE          the 5–10 expensive problems the posting actually pays for
   ↓               (technologies are EVIDENCE of problems, not a curriculum)
MAP             match onto the domain backlog (data/backlog.md, stable IDs;
   ↓                grows with new IDs, never mutates)
INTERSECT       per problem: what transfers (profile is law), gap severity,
   ↓                credibility risk
RANK            deterministic code: importance × gap, foundations first
   ↓
PLAN            weekly sprints, one evidence artifact each with a "done when"
   ↓                a skeptical senior reviewer would accept + honest positioning
RENDER          plan.json → Obsidian vault + self-contained dashboard (offline)
```

## Project shape

```
app.py                       # CLI: generate (pipeline) / render (offline)
ui.py                        # local Streamlit UI, same pipeline
lambda_core/
  llm.py                     # thin Anthropic client (JSON in/out)
  prompts.py                 # per-stage prompts (iterate quality here)
  pipeline.py                # the staged pipeline + deterministic ranking
  backlog.py                 # domain backlog: parse / prompt-format / grow
  validate.py                # slim: JSON Schema + a few substance floors
  render.py                  # plan.json → vault + dashboard (no LLM)
data/
  backlog.md                 # domain backlog (P1–P61+), grows via runs
  plan_schema.json           # the plan.json contract (CLI ↔ dashboard ↔ skill)
assets/dashboard_template.html
skill/lambda-targeted/       # Claude skill: run the same pipeline conversationally
docs/                        # constitution (framework) + engine spec + instance brief
examples/                    # sample JDs, profiles, and a rendered demo plan
```

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # set ANTHROPIC_API_KEY
```

## Run

```bash
# Full pipeline (needs ANTHROPIC_API_KEY)
python app.py generate -j examples/jobs/ai_infra_systems.md -p examples/profiles/your_real_profile.md

# Directional intent: pass a domain brief or several postings concatenated
python app.py generate -j my_domain_composite.md -p profile.md --intent directional

# Offline: render an existing plan.json (no API key needed)
python app.py render examples/plans/bytedance_ai_compute_demo.json

# UI
streamlit run ui.py
```

Output per run: `plan.json`, a self-contained `dashboard.html`, and an Obsidian-ready `vault/` (plan overview, positioning, weekly sprint files, engineering-page stubs).

## Iterating on quality

Edit `lambda_core/prompts.py` only. If you feel the urge to add output-policing code, resist it — fix the stage prompt instead. `validate.py` is deliberately small; if it grows past ~100 lines, something upstream is broken.

## Anti-overfit test

Run two very different JDs **and** two very different profiles through the identical pipeline. If any stage needs changing, something overfit — fix the output, never the pipeline. The engine contains zero JD-specific and zero user-specific logic.

## Tests

```bash
python -m pytest tests/ -q      # offline: schema, backlog, ranking, rendering
```
