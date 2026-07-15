# Project Lambda

Local-first Python MVP: a **Role-to-Roadmap Engine** that turns a **technical job description** + an **engineer background** into an engineering-growth plan — expensive problems, mental models, skill dependencies, progressive investigations, a proof-of-work ladder, evidence, and interview readiness.

It is **not** a one-shot project generator, career coach, resume scorer, or interview tutor.

## Project Philosophy

Project Lambda is built from a problem-first engineering apprenticeship system. See docs/mission_brief_v2.md for the operating philosophy, learning model, evidence standard, and engineering rules.

## What it produces

1. **Role interpretation** + expensive problem map
2. **Surface keywords → deep skills**, candidate transfer strengths / real gaps
3. **General value threshold** + skill dependency graph
4. **Investigation roadmap** (5–8 progressive Why-investigations)
5. **Proof-of-work ladder** (small → final; final only after prerequisites)
6. **First investigation prompt** (paste-ready)
7. **Evidence plan** (Obsidian / GitHub) + **interview readiness map**
8. Markdown (and optional JSON) under `outputs/`

## Project shape

```
app.py                 # CLI entrypoint
ui.py                  # local Streamlit UI (wraps the same generator)
lambda_core/
  prompts.py           # system prompt + JSON schema (iterate here)
  inputs.py            # load / paste JD + profile
  outputs.py           # Markdown render + file write
  generator.py         # single LLM call
examples/
  jobs/                # sample job descriptions
  profiles/            # sample engineer backgrounds
outputs/               # generated roadmaps
```

## Setup

```bash
cd "c:\Project Lambda"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY` (and optionally `OPENAI_MODEL`).

For a local OpenAI-compatible server (e.g. Ollama):

```env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.1
```

## Run (CLI)

```bash
python app.py --job examples/jobs/fluidstack_production_engineering.md --profile examples/profiles/your_real_profile.md
```

Options:

| Flag | Meaning |
|------|---------|
| `--job` / `-j` | Job description file |
| `--profile` / `-p` | Engineer profile file |
| `--interactive` / `-i` | Paste missing text (end with `END`) |
| `--out` / `-o` | Custom Markdown path |
| `--json` | Also write a `.json` sidecar |
| `--stdout` | Print Markdown to stdout |

Example with JSON sidecar:

```bash
python app.py -j examples/jobs/fluidstack_production_engineering.md -p examples/profiles/your_real_profile.md --json
```

## Run (UI)

Local Streamlit UI wrapping the same generator (no redeploy / no cloud):

```bash
pip install -r requirements.txt
streamlit run ui.py
```

Paste a raw job description and engineer profile, click **Generate**, preview the Role-to-Roadmap Markdown, then save or download Markdown/JSON under `outputs/`. Example files can be loaded from `examples/jobs` and `examples/profiles`.

The CLI (`app.py`) continues to work as before.

## Iteration

Improve output quality by editing `lambda_core/prompts.py` only — schema + system prompt. Keep I/O and CLI stable unless you need new product surface.
