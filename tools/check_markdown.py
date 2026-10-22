"""Check the Markdown that GitHub and PyPI render as a landing page.

Catches the mistakes that actually broke the page: unclosed fences, an image that
points at a file that is not in the repository, a wrong branch in the raw URL, and
wide tables (they fall apart in narrow preview windows).
"""
import pathlib
import re
import sys

# A Windows console is not UTF-8 by default, and GitHub's Windows runner has no
# Cyrillic code page at all: printing Russian would crash the check, not report it.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
# ИНСТРУКЦИЯ.md is a long reference with small two-column tables; these files are
# the ones a visitor sees first.
FILES = ("README.md", "GITHUB.md", "CHANGELOG.md")

problems = []

for name in FILES:
    path = ROOT / name
    if not path.exists():
        problems.append("{0}: файла нет".format(name))
        continue
    text = path.read_text(encoding="utf-8")

    fences = len(re.findall(r"^```", text, re.M))
    if fences % 2:
        problems.append("{0}: непарные ``` ({1})".format(name, fences))

    for _alt, url in re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", text):
        if not url.startswith("http"):
            if not (ROOT / url).exists():
                problems.append("{0}: локального файла {1} нет".format(name, url))
            continue
        match = re.match(
            r"https://raw\.githubusercontent\.com/[^/]+/[^/]+/([^/]+)/(.+)", url)
        if not match:
            continue                      # a badge or an outside picture
        branch, rel = match.groups()
        if branch != "main":
            problems.append("{0}: ветка {1} вместо main в {2}".format(name, branch, rel))
        if not (ROOT / rel).exists():
            problems.append("{0}: файла {1} нет в репозитории".format(name, rel))

    if re.search(r"^\|.*\|", text, re.M):
        problems.append("{0}: markdown-таблица (разъезжается в узком окне)".format(name))

    for number, line in enumerate(text.splitlines(), 1):
        if line.rstrip() != line:
            problems.append("{0}:{1}: пробел в конце строки".format(name, number))
        if "\t" in line:
            problems.append("{0}:{1}: табулятор".format(name, number))

print("файлов проверено: {0}, проблем: {1}".format(len(FILES), len(problems)))
for item in problems[:20]:
    print("  -", item)
sys.exit(1 if problems else 0)
