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


_ADDED_HEADER = "## Added from targeted runs"


def append_entries(
    new_entries: list[dict], path: Path | str = DEFAULT_BACKLOG
) -> list[str]:
    """Append genuinely new problems under '## Added from targeted runs'.

    Entries are inserted INTO that section (created at the end if absent), not
    blindly at the end of the file — so the backlog stays correct even if other
    sections are later added below it. Existing IDs are never touched.
    """
    if not new_entries:
        return []
    path = Path(path)
    problems = load_backlog(path)
    existing = {p.problem.strip().lower() for p in problems}
    text = path.read_text(encoding="utf-8")
    if _ADDED_HEADER not in text:
        text = text.rstrip() + f"\n\n{_ADDED_HEADER}\n"

    appended: list[str] = []
    lines_to_add: list[str] = []
    counter = next_id(problems)
    for entry in new_entries:
        problem = str(entry.get("problem", "")).strip()
        if not problem or problem.lower() in existing:
            continue
        lines_to_add.append(f"{counter}. {problem}")
        appended.append(f"P{counter}")
        existing.add(problem.lower())
        counter += 1
    if not lines_to_add:
        return []

    # Insert at the end of the Added section (= before the next '## ' header,
    # or at end of file if the section is last).
    section_start = text.index(_ADDED_HEADER)
    next_header = text.find("\n## ", section_start + len(_ADDED_HEADER))
    insert_at = len(text.rstrip()) if next_header == -1 else next_header
    block = "\n" + "\n".join(lines_to_add)
    text = text[:insert_at].rstrip() + block + "\n" + text[insert_at:].lstrip("\n")
    path.write_text(text.rstrip() + "\n", encoding="utf-8")
    return appended
