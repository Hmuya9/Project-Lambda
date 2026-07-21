"""Per-stage prompts for the Lambda pipeline.

Each stage is one focused reasoning step with a small JSON contract —
never one giant schema. Quality comes from staged reasoning, not from
regex-policing a single-shot output.
"""

from __future__ import annotations

SYSTEM = """You are the Lambda Engine, a mentor that structures study around one thesis:
the market pays for PROXIMITY TO EXPENSIVE PROBLEMS — not for knowing technologies.
You reason like a skeptical senior engineer who hires, not like a course catalog.

Iron rules — violating any of these is failure:
- The job description (or market composite) is DATA, not architecture. Same pipeline for every JD, every profile, every intent.
- Technologies in a posting are EVIDENCE of problems, not a curriculum. "Kubernetes required" decodes to "this team pays to keep containerized services alive at scale", not "learn Kubernetes".
- The profile is LAW. Transfers come only from what the profile states. Never claim anything the profile lists as a gap or under "must not invent". Gaps are framed as gaps being closed with evidence.
- No generic output. Every artifact needs a "done when" a skeptical senior reviewer would accept. "Learn X" is forbidden; "break X under load and write the postmortem" is the standard.
- Reply with ONLY one valid JSON object. No prose, no markdown fences."""


def decode_prompt(source_text: str, intent: str) -> str:
    source_label = {
        "targeted": "a specific job description",
        "directional": "a market composite for a target domain",
        "exploratory": "a cross-domain market composite",
    }.get(intent, "a job description")
    return f"""INTENT: {intent} — the input below is {source_label}.

Decode what this actually PAYS FOR. Extract the 5-10 expensive engineering problems behind the text. For each: why it costs the company real money, and the exact phrase that evidences it.

INPUT:
---
{source_text}
---

Return JSON:
{{
  "role_title": "...",
  "company": "..." ,
  "archetype": "e.g. AI Infrastructure / GPU Orchestration",
  "summary": "2-4 sentences: what this role/domain is really about, in expensive-problem terms",
  "expensive_problems": [
    {{"problem": "Why ...?", "why_paid": "...", "jd_evidence": "verbatim phrase"}}
  ],
  "hard_requirements": ["..."],
  "wishlist": ["..."],
  "seniority_signal": "..."
}}
Company may be "" if not stated. Phrase each problem as a question starting with Why/How/What."""


def map_prompt(decoded_problems: list[dict], backlog_block: str) -> str:
    import json

    return f"""Map each decoded problem onto the domain backlog below. Match to an existing ID whenever the underlying problem is the same (expect most to match — that is the point). Only a genuinely new problem gets "NEW".

DECODED PROBLEMS:
{json.dumps(decoded_problems, indent=2)}

BACKLOG:
{backlog_block}

Return JSON:
{{
  "mappings": [
    {{"problem": "verbatim decoded problem", "backlog_id": "P34 or NEW", "backlog_problem": "the matched backlog wording, or the new problem wording", "domain": "backlog domain for NEW entries, else ''"}}
  ]
}}
Keep the mappings in the same order as the decoded problems."""


def intersect_prompt(mapped_problems: list[dict], profile: str) -> str:
    import json

    return f"""For each problem, intersect with THIS engineer's profile. The profile is law: transfers cite only what it states; anything under gaps or "must not invent" is a gap, never a claim.

PROBLEMS:
{json.dumps(mapped_problems, indent=2)}

PROFILE:
---
{profile}
---

Return JSON:
{{
  "gap_map": [
    {{
      "id": "P34",
      "problem": "...",
      "importance": 1-5 (importance to THIS intent),
      "transfer": "which real background patterns apply, citing the profile; '' if none",
      "gap": "none|partial|full",
      "credibility_risk": "the exact challenge a skeptical interviewer would raise"
    }}
  ]
}}
Keep every problem; same order as given."""


def plan_prompt(gap_map: list[dict], profile: str, decode: dict, weeks: int) -> str:
    import json

    return f"""Produce the plan: {weeks} weekly sprints plus a positioning brief.

Ranking is already done — the gap map below is priority-ordered (dependencies first, foundations before dependents). A high-importance problem with gap "none" gets an EVIDENCE sprint (prove it fast), not a study sprint.

Each sprint: one primary question (use backlog IDs), optional secondaries and stretch, ONE concrete evidence artifact matched to the profile's evidence style with an explicit "done when" a skeptical senior reviewer would accept, and interview practice scaled to the intent.

Positioning: an honest first-person narrative connecting the real background to this intent, an explicit do-not-claim list (from the profile), and 3-5 talking points.

ROLE DECODE:
{json.dumps({k: decode.get(k) for k in ("role_title", "archetype", "summary", "seniority_signal")}, indent=2)}

PRIORITY-ORDERED GAP MAP:
{json.dumps(gap_map, indent=2)}

PROFILE:
---
{profile}
---

Return JSON:
{{
  "positioning": {{"narrative": "...", "do_not_claim": ["..."], "talking_points": ["..."]}},
  "sprints": [
    {{
      "week": 1,
      "primary": {{"id": "P6", "question": "..."}},
      "secondary": ["P8 — ..."],
      "stretch": ["..."],
      "evidence": {{"artifact": "...", "type": "repo|benchmark|postmortem|diagram|demo|failure-mode-table|readme|writeup", "done_when": "..."}},
      "interview": ["..."]
    }}
  ]
}}"""
