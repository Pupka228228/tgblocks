"""Check every editor page's inline JavaScript parses (node --check)."""
import json
import pathlib
import re
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent
STATIC = ROOT / "src" / "tgblocks" / "visual" / "static"
failures = []

for page in sorted(STATIC.glob("*.html")):
    html = page.read_text(encoding="utf-8")
    blocks = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S)
    for index, body in enumerate(blocks):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False,
                                         encoding="utf-8") as handle:
            handle.write(body)
            name = handle.name
        result = subprocess.run(["node", "--check", name], capture_output=True, text=True)
        if result.returncode != 0:
            failures.append((page.name, index, result.stderr.strip().splitlines()[:6]))
            print("SYNTAX ERROR", page.name, "script", index)
            for line in result.stderr.strip().splitlines()[:8]:
                print("   ", line)

for js in sorted(STATIC.glob("*.js")):
    result = subprocess.run(["node", "--check", str(js)], capture_output=True, text=True)
    if result.returncode != 0:
        failures.append((js.name, 0, result.stderr.splitlines()[:6]))
        print("SYNTAX ERROR", js.name)
        for line in result.stderr.splitlines()[:8]:
            print("   ", line)

# Parsing is not enough: `L("текст", "text")` in a page without `function L`
# throws at boot and the page hangs on its first status line. A page that calls a
# helper must define it - this catches the class of bug that a syntax check misses.
HELPERS = {"L": r"function L\(", "TgUi": r"tgblocks-ui\.js"}
for page in sorted(STATIC.glob("*.html")):
    html = page.read_text(encoding="utf-8")
    blocks = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S)
    script_text = "\n".join(blocks)
    for helper, definition in HELPERS.items():
        used = re.search(r"(?<![\w.$])" + helper + r"[\.(]", script_text)
        defined = re.search(definition, html)
        if used and not defined:
            failures.append((page.name, 0, ["calls {0} but never defines it".format(helper)]))
            print("UNDEFINED HELPER", page.name, helper)

print(json.dumps({"checked": True, "failures": len(failures)}))
sys.exit(1 if failures else 0)
