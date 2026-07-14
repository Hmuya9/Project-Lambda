"""Load job description and engineer profile from files or interactive paste."""

from __future__ import annotations

from pathlib import Path


def load_text(path: str | Path) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {p}")
    text = p.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(f"File is empty: {p}")
    return text


def read_multiline(prompt: str) -> str:
    print(prompt)
    print("(Finish with a line containing only END)")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "END":
            break
        lines.append(line)
    text = "\n".join(lines).strip()
    if not text:
        raise ValueError("No text provided.")
    return text


def resolve_input(
    *,
    file_path: str | None,
    interactive_label: str,
    allow_interactive: bool,
) -> str:
    if file_path:
        return load_text(file_path)
    if not allow_interactive:
        raise ValueError(f"Missing {interactive_label}: pass a file path or use --interactive.")
    return read_multiline(f"Paste {interactive_label}, then type END:")
