"""Per-stage prompts for the Lambda pipeline.

Each stage is one focused reasoning step with a small JSON contract —
never one giant schema. Quality comes from staged reasoning, not from
regex-policing a single-shot output.
"""

from __future__ import annotations

SYSTEM = """You are the Lambda Engine — part senior engineer who hires, part tutor who makes hard things feel doable. You structure study around one thesis:
the market pays for PROXIMITY TO EXPENSIVE PROBLEMS — not for knowing technologies.

Voice — this matters as much as correctness:
- Say everything TWICE: first HUMAN (a simple analogy a curious 15-year-old could picture — zero jargon), then ENGINEER (precise, honest). Never skip the human version.
- The user is a visual learner. Prefer explanations someone can PICTURE: machines, water, traffic, factories, control loops. Prefer resources someone can WATCH.
- Excite the inner-child engineer: "wouldn't it be cool if you could SEE...?" — but never lie about difficulty. The message is always: this is challenging AND doable, here is the first small win.
- You are on the user's side. Warm, direct, no corporate filler.

Iron rules — violating any of these is failure:
- The job description (or market composite) is DATA, not architecture. Same pipeline for every JD, every profile, every intent.
- Technologies in a posting are EVIDENCE of problems, not a curriculum. "Kubernetes required" decodes to "this team pays to keep containerized services alive at scale", not "learn Kubernetes".
- The profile is LAW. Transfers come only from what the profile states. Never claim anything the profile lists as a gap or under "must not invent". Gaps are framed as gaps being closed with evidence.
- No generic output. Every artifact needs a "done when" a skeptical senior reviewer would accept. "Learn X" is forbidden; "break X under load and write the postmortem" is the standard.
- RESOURCES: never invent URLs. Recommend resources as SEARCH QUERIES (YouTube / MIT OpenCourseWare search terms) plus creators known for visual explanations (e.g. 3Blue1Brown, Computerphile, Fireship, ByteByteGo, Branch Education, Asianometry, MIT OCW). The app turns queries into search links — a query cannot be a dead link.
- Reply with ONLY one valid JSON object. No prose, no markdown fences."""


def decode_prompt(source_text: str, intent: str) -> str:
    source_label = {
        "targeted": "a specific job description",
        "directional": "a market composite for a target domain",
        "exploratory": "a cross-domain market composite",
    }.get(intent, "a job description")
    return f"""INTENT: {intent} — the input below is {source_label}.

Decode what this actually PAYS FOR. Extract the 5-10 expensive engineering problems behind the text. For each: why it costs the company real money, and the exact phrase that evidences it.

Then write the HUMAN HOOK — the part that makes an engineer lean in instead of feeling behind:
- what_this_really_is: 2-3 sentences, "This role is about ..." in plain language, then ONE vivid analogy from the physical world that makes the whole role picturable.
- why_exciting: 2-3 sentences that light up the inner-child engineer — what they would get to SEE and touch.
- why_doable: 2-3 sentences that make it feel reachable — what kind of person thrives here and why the path is walkable one project at a time.

INPUT:
---
{source_text}
---

Return JSON:
{{
  "role_title": "...",
  "company": "...",
  "archetype": "e.g. AI Infrastructure / GPU Orchestration",
  "summary": "2-4 sentences: what this role/domain is really about, in expensive-problem terms",
  "human_hook": {{
    "what_this_really_is": "...",
    "why_exciting": "...",
    "why_doable": "..."
  }},
  "expensive_problems": [
    {{"problem": "Why ...?", "why_paid": "...", "human": "one plain-language sentence + tiny analogy for THIS problem", "jd_evidence": "verbatim phrase"}}
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


def pitch_prompt(gap_map: list[dict], profile: str, decode: dict) -> str:
    import json

    return f"""Now the fun part. We need to sit this engineer as CLOSE to the top expensive problems as possible — by building something. Pitch 3 candidate PROJECTS they can pick from.

Each project must:
- sit close to as many of the TOP-priority problems as possible (cite the P-ids),
- be a conceptually-equivalent MINIATURE of the industrial-scale problem — same physics, smaller machine (a 3-node home lab teaches the same lesson as a 10,000-node fleet),
- have a VISUAL payoff: something the engineer can literally watch happen (a dashboard lighting up, pods dying and healing, a latency curve bending),
- be pitched to the inner-child engineer: the hook starts from "Wouldn't it be cool if you could SEE/BUILD/BREAK ...",
- fit the profile's evidence style and honestly state its difficulty,
- include a FIRST WIN reachable in one sitting — momentum beats ambition.

PRIORITY-ORDERED GAP MAP:
{json.dumps(gap_map, indent=2)}

ROLE DECODE (for context):
{json.dumps({k: decode.get(k) for k in ("role_title", "archetype", "summary")}, indent=2)}

PROFILE:
---
{profile}
---

Return JSON:
{{
  "project_options": [
    {{
      "title": "short, concrete, exciting",
      "hook": "Wouldn't it be cool if you could ... (2-3 sentences, visual, inner-child)",
      "what_you_will_see": "the visual payoff, concretely",
      "analogy": "one physical-world analogy that makes the project picturable",
      "problems_touched": ["P34", "P30"],
      "what_you_will_learn": "2-3 sentences, plain language",
      "difficulty": 1-5,
      "weeks_estimate": 6-10,
      "first_win": "what works by the end of the FIRST sitting"
    }}
  ],
  "recommended": 0
}}
Order the options with your recommended one first. "recommended" is its index (0)."""


def plan_prompt(
    gap_map: list[dict], profile: str, decode: dict, weeks: int, project: dict | None = None
) -> str:
    import json

    project_block = (
        f"""THE ENGINEER PICKED THIS PROJECT — every sprint builds one piece of it:
{json.dumps(project, indent=2)}
"""
        if project
        else "No project was picked; design the sprints around the smallest builds that prove each problem."
    )
    return f"""Produce the plan: {weeks} weekly sprints plus a positioning brief. You are the tutor now — every sprint must make the engineer feel "I can picture this, and I can do this week's piece."

{project_block}

Ranking is already done — the gap map below is priority-ordered (dependencies first, foundations before dependents). A high-importance problem with gap "none" gets an EVIDENCE sprint (prove it fast), not a study sprint.

Each sprint needs:
- primary question (use backlog IDs) — the week's engineering question,
- simple_intro: 2-3 sentences explaining this week's problem with ZERO jargon and one analogy — say it human first,
- why_this_matters: 1-2 sentences tying it to the expensive problem and the goal,
- watch: 2-3 WATCH-FIRST resources, ordered gentle→deeper. Each is a SEARCH QUERY (never a URL): item 1 = short, visual, non-technical introduction (name a visual creator if apt); item 2 = deeper technical explanation; item 3 (optional) = lecture-depth (MIT OCW / conference talk search). Include "why" for each (one line: what they'll be able to picture afterward).
- optional secondaries and stretch,
- ONE concrete evidence artifact (matched to the profile's evidence style) building this week's piece of the project, with an explicit "done when" a skeptical senior reviewer would accept,
- interview practice scaled to the intent.

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
      "simple_intro": "...",
      "why_this_matters": "...",
      "watch": [
        {{"title": "what this video is", "query": "youtube search query", "source": "youtube|mit-ocw", "why": "what you'll be able to picture afterward"}}
      ],
      "secondary": ["P8 — ..."],
      "stretch": ["..."],
      "evidence": {{"artifact": "...", "type": "repo|benchmark|postmortem|diagram|demo|failure-mode-table|verification-log|readme|writeup", "done_when": "..."}},
      "interview": ["..."]
    }}
  ]
}}"""
