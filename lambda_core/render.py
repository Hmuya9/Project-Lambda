"""Deterministic rendering: plan dict → Obsidian-ready vault + dashboard HTML.

No reasoning, no LLM, no network. The JD is data; nothing here changes per JD.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "assets" / "dashboard_template.html"


def _slug(text: str, maxlen: int = 60) -> str:
    s = re.sub(r"[^\w\s-]", "", text).strip()
    return s[:maxlen].strip() or "untitled"


def _cell(value: Any) -> str:
    """Make arbitrary model text safe inside a Markdown table cell."""
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def watch_url(item: dict[str, Any]) -> str:
    """Turn a watch-item search query into a search URL (never a dead link)."""
    from urllib.parse import quote_plus

    q = quote_plus(str(item.get("query", "")))
    if item.get("source") == "mit-ocw":
        return f"https://ocw.mit.edu/search/?q={q}"
    return f"https://www.youtube.com/results?search_query={q}"


def render_dashboard(plan: dict[str, Any], out: Path) -> Path:
    html = TEMPLATE.read_text(encoding="utf-8")
    injected = html.replace(
        "/*__PLAN_JSON__*/null", json.dumps(plan, ensure_ascii=False)
    )
    path = out / "dashboard.html"
    path.write_text(injected, encoding="utf-8")
    return path


def _render_overview(plan: dict[str, Any], vault: Path) -> None:
    m, rd = plan["meta"], plan["role_decode"]
    lines = [
        f"# Plan Overview — {m.get('role_title', '')}"
        + (f" @ {m['company']}" if m.get("company") else ""),
        "",
        f"**Archetype:** {m.get('archetype', '')}  ",
        f"**Generated:** {m.get('generated', '')}  ",
        f"**Mode:** {m.get('mode', '')}",
        "",
        "> **The goal this week is not to study more. The goal is to become more valuable.**",
        "",
    ]
    hook = rd.get("human_hook") or {}
    if hook.get("what_this_really_is"):
        lines += [
            "## What this role really is",
            "",
            hook.get("what_this_really_is", ""),
            "",
            f"**Why it's exciting:** {hook.get('why_exciting', '')}",
            "",
            f"**Why it's doable:** {hook.get('why_doable', '')}",
            "",
        ]
    project = plan.get("project") or {}
    if project.get("title"):
        lines += [
            f"## Your Project — {project.get('title', '')}",
            "",
            project.get("hook", ""),
            "",
            f"**What you'll see:** {project.get('what_you_will_see', '')}  ",
            f"**Think of it as:** {project.get('analogy', '')}  ",
            f"**First win:** {project.get('first_win', '')}  ",
            f"**Difficulty:** {project.get('difficulty', '?')}/5 · ~{project.get('weeks_estimate', '?')} weeks · touches "
            + ", ".join(project.get("problems_touched", [])),
            "",
        ]
    lines += [
        "## Role Decode",
        "",
        rd.get("summary", ""),
        "",
        "| ID | Expensive problem | Why they pay | JD evidence |",
        "|----|-------------------|--------------|-------------|",
    ]
    for p in rd.get("expensive_problems", []):
        lines.append(
            f"| {_cell(p.get('id'))} | {_cell(p.get('problem'))} | {_cell(p.get('why_paid'))} "
            f"| {_cell(p.get('jd_evidence'))} |"
        )
    lines += [
        "",
        "## Gap Map",
        "",
        "| Pri | ID | Problem | Importance | Gap | Transfers | Credibility risk |",
        "|-----|----|---------|-----------:|-----|-----------|------------------|",
    ]
    for g in sorted(plan["gap_map"], key=lambda x: x.get("priority", 99)):
        lines.append(
            f"| {_cell(g.get('priority'))} | {_cell(g.get('id'))} | {_cell(g.get('problem'))} "
            f"| {_cell(g.get('importance'))}/5 | {_cell(g.get('gap'))} "
            f"| {_cell(g.get('transfer'))} | {_cell(g.get('credibility_risk'))} |"
        )
    (vault / "00 - Plan Overview.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _render_positioning(plan: dict[str, Any], vault: Path) -> None:
    pos = plan["positioning"]
    lines = ["# Positioning", "", pos.get("narrative", ""), "", "## Talking points", ""]
    lines += [f"- {t}" for t in pos.get("talking_points", [])]
    lines += ["", "## Do NOT claim", ""]
    lines += [f"- ❌ {t}" for t in pos.get("do_not_claim", [])]
    (vault / "01 - Positioning.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _render_sprints(plan: dict[str, Any], vault: Path) -> None:
    d = vault / "02 - Weekly Sprints"
    d.mkdir(parents=True, exist_ok=True)
    for s in plan["sprints"]:
        ev = s["evidence"]
        lines = [
            f"# Week {s['week']}",
            "",
            "**The goal this week is not to study more. The goal is to become more valuable.**",
            "",
            "## Primary Objective",
            "",
            f"{s['primary'].get('id','')} — {s['primary'].get('question','')}",
            "",
        ]
        if s.get("simple_intro"):
            lines += ["## Say It Human First", "", s["simple_intro"], ""]
            if s.get("why_this_matters"):
                lines += [f"**Why this matters:** {s['why_this_matters']}", ""]
        watch = [w for w in (s.get("watch") or []) if isinstance(w, dict)]
        if watch:
            lines += ["## Watch First (gentle → deeper)", ""]
            for w in watch:
                why = f" — {w['why']}" if w.get("why") else ""
                lines.append(f"- [{w.get('title', 'video')}]({watch_url(w)}){why}")
            lines.append("")
        lines += [
            "## Secondary Objectives",
            "",
        ]
        lines += [f"- [ ] {x}" for x in s.get("secondary", [])] or ["- (none)"]
        lines += ["", "## Stretch", ""]
        lines += [f"- [ ] {x}" for x in s.get("stretch", [])] or ["- (none)"]
        lines += [
            "",
            "## Evidence",
            "",
            f"- **Artifact ({ev.get('type','')}):** {ev.get('artifact','')}",
            f"- **Done when:** {ev.get('done_when','')}",
            "",
            "## Interview",
            "",
        ]
        lines += [f"- [ ] {x}" for x in s.get("interview", [])] or ["- (none)"]
        lines += ["", "## Reflection", "", "Completed:", "", "Difficulties:", "", "Next week:", ""]
        (d / f"Week {s['week']}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _render_engineering_pages(plan: dict[str, Any], vault: Path) -> None:
    d = vault / "03 - Engineering Notebook"
    d.mkdir(parents=True, exist_ok=True)
    seen: dict[str, str] = {}
    for g in plan["gap_map"]:
        seen[g["id"]] = g["problem"]
    for s in plan["sprints"]:
        pid = s["primary"].get("id")
        if pid and pid not in seen:
            seen[pid] = s["primary"].get("question", pid)
    for pid, problem in seen.items():
        page = "\n".join(
            [
                f"# {pid} — {problem}",
                "",
                "## Engineering Question", "", problem, "",
                "## Problem", "", "_What problem existed?_", "",
                "## Solution", "", "_Why was this solution created, and how does it solve the problem?_", "",
                "## Tradeoffs", "", "_What tradeoffs does it introduce?_", "",
                "## Real-world Use", "", "_Where have I personally applied or observed it?_", "",
                "## Two-minute explanation", "", "- [ ] I can explain this in under two minutes", "",
                "## Evidence", "", "Project:", "",
            ]
        )
        (d / f"{pid} - {_slug(problem)}.md").write_text(page, encoding="utf-8")


def render_all(plan: dict[str, Any], out_dir: Path | str) -> dict[str, Any]:
    """Render dashboard + vault. Returns a summary dict."""
    out = Path(out_dir)
    vault = out / "vault"
    vault.mkdir(parents=True, exist_ok=True)

    render_dashboard(plan, out)
    _render_overview(plan, vault)
    _render_positioning(plan, vault)
    _render_sprints(plan, vault)
    _render_engineering_pages(plan, vault)

    return {
        "out": str(out.resolve()),
        "sprints": len(plan["sprints"]),
        "pages": len(list((vault / "03 - Engineering Notebook").glob("*.md"))),
    }
