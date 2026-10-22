#!/usr/bin/env python3
"""Regenerate the embedded file payload of scaffold.py from the real project.

`scaffold.py` has to be a single self-contained file (it is the thing people copy
into an empty folder), so it cannot read the project tree at runtime - it carries
a copy of it. That copy used to be maintained by hand and silently drifted 600
lines behind the real sources, so it is generated now:

    python tools/build_scaffold.py           # rewrite the payload in scaffold.py
    python tools/build_scaffold.py --check   # exit 1 when the payload is stale

The tests run --check, so forgetting to rebuild cannot reach a release.

Everything except tools/ itself, caches and the git database is embedded, so the
generated project is complete: sources, pages, tests and examples.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
SCAFFOLD = ROOT / "scaffold.py"

BEGIN = "# BEGIN GENERATED FILE PAYLOAD (python tools/build_scaffold.py)"
END = "# END GENERATED FILE PAYLOAD"

# What the generated project contains. Ordered so the payload reads like a tree.
INCLUDE_DIRS = ("src", "tests", "examples")
INCLUDE_FILES = (
    "pyproject.toml",
    "README.md",
    "LICENSE",
    ".gitignore",
    ".gitattributes",
)
SKIP_PARTS = {"__pycache__", ".pytest_cache", ".git", ".mypy_cache", ".ruff_cache",
              ".venv", "node_modules", "dist", "build", "vendor"}
# A vendored library (Blockly) is served by the installed package; a scaffolded
# bot project has no editor, so embedding it would only bloat the payload.
SKIP_SUFFIXES = {".pyc", ".pyo", ".jpg", ".jpeg", ".png", ".gif", ".ico", ".zip"}


def _wanted(path: Path) -> bool:
    if any(part in SKIP_PARTS for part in path.parts):
        return False
    if path.suffix.lower() in SKIP_SUFFIXES:
        return False
    return path.is_file()


def collect_files() -> Dict[str, str]:
    """Map of posix relative path -> file text, exactly as it is on disk."""
    paths: List[Path] = []
    for name in INCLUDE_FILES:
        candidate = ROOT / name
        if candidate.is_file():
            paths.append(candidate)
    for folder in INCLUDE_DIRS:
        base = ROOT / folder
        if base.is_dir():
            paths.extend(sorted(item for item in base.rglob("*") if _wanted(item)))
    files: Dict[str, str] = {}
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        files[relative] = path.read_text(encoding="utf-8")
    return dict(sorted(files.items()))


def _literal(text: str) -> str:
    """A Python source literal that is readable and always valid."""
    if text.endswith("\n") and '"""' not in text and not text.endswith('\\\n'):
        # Every text file ends with a newline, so the raw literal never ends on a
        # backslash or a quote and cannot be closed early.
        return 'r"""' + text + '"""'
    # Rare files (no trailing newline, or an embedded triple quote).
    return repr(text)


def render_payload(files: Dict[str, str]) -> str:
    lines = [BEGIN, "FILES: Dict[str, str] = {"]
    for name, content in files.items():
        lines.append('    "{0}": {1},'.format(name, _literal(content)))
    lines.append("}")
    lines.append(END)
    return "\n".join(lines)


def current_payload(scaffold_text: str) -> str:
    if BEGIN in scaffold_text and END in scaffold_text:
        start = scaffold_text.index(BEGIN)
        stop = scaffold_text.index(END) + len(END)
        return scaffold_text[start:stop]
    return ""


def build(scaffold_text: str, files: Dict[str, str]) -> str:
    payload = render_payload(files)
    if BEGIN in scaffold_text and END in scaffold_text:
        start = scaffold_text.index(BEGIN)
        stop = scaffold_text.index(END) + len(END)
        return scaffold_text[:start] + payload + scaffold_text[stop:]
    # First run on a file that still carries the hand-maintained dict.
    start = scaffold_text.index("FILES: Dict[str, str] = {")
    stop = scaffold_text.index("\nNEXT_STEPS")
    return scaffold_text[:start] + payload + "\n\n" + scaffold_text[stop:].lstrip("\n")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="only report whether scaffold.py is up to date")
    args = parser.parse_args(argv)

    files = collect_files()
    text = SCAFFOLD.read_text(encoding="utf-8")
    wanted = render_payload(files)
    if BEGIN in text and END in text and current_payload(text) == wanted:
        print("scaffold.py is up to date ({0} files)".format(len(files)))
        return 0
    if args.check:
        print("scaffold.py is STALE: run python tools/build_scaffold.py", file=sys.stderr)
        return 1
    SCAFFOLD.write_text(build(text, files), encoding="utf-8", newline="\n")
    print("wrote scaffold.py with {0} files".format(len(files)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
