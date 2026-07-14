# Project Lambda

Local-first Python MVP that turns a **technical job description** + an **engineer background** into a **problem-first engineering execution plan** — not career advice, resume scoring, or interview coaching.

## Project Philosophy

Project Lambda is built from a problem-first engineering apprenticeship system. See docs/mission_brief_v2.md for the operating philosophy, learning model, evidence standard, and engineering rules.

## What it produces

1. Structured **Problem-Solution Contract** (JSON → Markdown)
2. One high-signal **proof-of-work project** spec
3. A **verification / benchmark checklist**
4. Markdown (and optional JSON) under `outputs/`

## Project shape

```
app.py                 # CLI entrypoint
lambda_core/
  prompts.py           # system prompt + JSON schema (iterate here)
  inputs.py            # load / paste JD + profile
  outputs.py           # Markdown render + file write
  generator.py         # single LLM call
examples/
  jobs/                # sample job descriptions
  profiles/            # sample engineer backgrounds
outputs/               # generated contracts
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

## Run

```bash
python app.py --job examples/jobs/ai_infra_systems.md --profile examples/profiles/engineer_background.md
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
python app.py -j examples/jobs/ai_infra_systems.md -p examples/profiles/engineer_background.md --json
```

## Iteration

Improve output quality by editing `lambda_core/prompts.py` only — schema + system prompt. Keep I/O and CLI stable unless you need new product surface.
