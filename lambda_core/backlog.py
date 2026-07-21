"""Domain backlog: parse, format for prompts, and append new entries.

The backlog is data (data/backlog.md). It grows with new IDs; it never mutates.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BACKLOG = ROOT / "data" / "backlog.md"

_ENTRY = re.compile(r"^(\d+)\.\s+(.+?)\s*$")
_HEADER = re.compile(r"^##\s+(.+?)\s*$")


@dataclass
class Problem:
    id: str  # "P11"
    problem: str
    domain: str


def load_backlog(path: Path | str = DEFAULT_BACKLOG) -> list[Problem]:
    problems: list[Problem] = []
    domain = "Uncategorized"
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        header = _HEADER.match(line)
        if header:
            domain = header.group(1)
            continue
        entry = _ENTRY.match(line)
        if entry:
            problems.append(
                Problem(id=f"P{entry.group(1)}", problem=entry.group(2), domain=domain)
            )
    if not problems:
        raise ValueError(f"No backlog entries parsed from {path}")
    return problems


def next_id(problems: list[Problem]) -> int:
    return max(int(p.id[1:]) for p in problems) + 1


def as_prompt_block(problems: list[Problem]) -> str:
    """Compact backlog listing for inclusion in prompts."""
    lines: list[str] = []
    domain = None
    for p in problems:
        if p.domain != domain:
            domain = p.domain
            lines.append(f"[{domain}]")
        lines.append(f"{p.id}: {p.problem}")
    return "\n".join(lines)


def append_entries(
    new_entries: list[dict], path: Path | str = DEFAULT_BACKLOG
) -> list[str]:
    """Append genuinely new problems under '## Added from targeted runs'.

    Returns the IDs appended. Existing IDs are never touched.
    """
    if not new_entries:
        return []
    path = Path(path)
    problems = load_backlog(path)
    existing = {p.problem.strip().lower() for p in problems}
    text = path.read_text(encoding="utf-8")
    if "## Added from targeted runs" not in text:
        text = text.rstrip() + "\n\n## Added from targeted runs\n"
    appended: list[str] = []
    counter = next_id(problems)
    for entry in new_entries:
        problem = str(entry.get("problem", "")).strip()
        if not problem or problem.lower() in existing:
            continue
        text = text.rstrip() + f"\n{counter}. {problem}\n"
        appended.append(f"P{counter}")
        existing.add(problem.lower())
        counter += 1
    path.write_text(text, encoding="utf-8")
    return appended
