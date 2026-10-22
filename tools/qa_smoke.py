"""Full QA sweep: every endpoint, every editor hand-off, every example.

Run against a throwaway server so nothing in the user's project store is touched.
Prints only failures, then a summary.
"""
import ast
import json
import pathlib
import sys
import threading
import urllib.error
import urllib.request

# The Windows runner's console is not UTF-8, so Russian output would crash here.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from http.server import ThreadingHTTPServer            # noqa: E402

import tgblocks.visual.server as server                # noqa: E402
from tgblocks.convert import (                         # noqa: E402
    blocks_xml_to_spec, board_to_spec, board_to_text, spec_to_blocks_xml,
    spec_to_nodes, spec_to_text,
)
from tgblocks.dsl import compile_source                # noqa: E402
from tgblocks.dsl.parser import parse_file             # noqa: E402
from tgblocks.textlang import compile_text, parse_text  # noqa: E402

failures = []


def fail(where, message):
    failures.append("{0}: {1}".format(where, message))
    print("FAIL {0}: {1}".format(where, message))


# --------------------------------------------------------------- round trips
def check_round_trip(name, spec):
    canonical = spec_to_text(spec)
    try:
        again = spec_to_text(parse_text(canonical, name))
    except Exception as error:  # noqa: BLE001
        fail(name, "С‚РµРєСЃС‚ РЅРµ СЂР°Р·Р±РёСЂР°РµС‚СЃСЏ РѕР±СЂР°С‚РЅРѕ: {0}: {1}".format(
            type(error).__name__, error))
        return
    if again != canonical:
        fail(name, "С‚РµРєСЃС‚ РјРµРЅСЏРµС‚СЃСЏ РїСЂРё РїРѕРІС‚РѕСЂРЅРѕРј СЂР°Р·Р±РѕСЂРµ")
        print("   Р±С‹Р»Рѕ:  {0!r}".format(canonical[:120]))
        print("   СЃС‚Р°Р»Рѕ: {0!r}".format(again[:120]))

    try:
        board_text = board_to_text(spec_to_nodes(spec))
    except Exception as error:  # noqa: BLE001
        fail(name, "РґРѕСЃРєР° СѓР·Р»РѕРІ РїР°РґР°РµС‚: {0}: {1}".format(type(error).__name__, error))
        return
    if board_text != canonical:
        fail(name, "С‚РµРєСЃС‚ РјРµРЅСЏРµС‚СЃСЏ С‡РµСЂРµР· РґРѕСЃРєСѓ СѓР·Р»РѕРІ")
        print("   Р±С‹Р»Рѕ:  {0!r}".format(canonical[:120]))
        print("   СЃС‚Р°Р»Рѕ: {0!r}".format(board_text[:120]))

    try:
        xml = spec_to_blocks_xml(spec)
        xml_text = spec_to_text(blocks_xml_to_spec(xml))
    except Exception as error:  # noqa: BLE001
        fail(name, "Blockly XML РїР°РґР°РµС‚: {0}: {1}".format(type(error).__name__, error))
        return
    if xml_text != canonical:
        fail(name, "С‚РµРєСЃС‚ РјРµРЅСЏРµС‚СЃСЏ С‡РµСЂРµР· Blockly XML")
        print("   Р±С‹Р»Рѕ:  {0!r}".format(canonical[:120]))
        print("   СЃС‚Р°Р»Рѕ: {0!r}".format(xml_text[:120]))

    try:
        # The canonical form is the text syntax, so it compiles with compile_text.
        code = compile_text(canonical, name)
        ast.parse(code, name)
    except Exception as error:  # noqa: BLE001
        fail(name, "РєРѕРґ РЅРµ РєРѕРјРїРёР»РёСЂСѓРµС‚СЃСЏ: {0}: {1}".format(type(error).__name__, error))


print("=== 1. РїСЂРёРјРµСЂС‹ Рё РєРѕСЂРїСѓСЃ: DSL -> С‚РµРєСЃС‚ -> СѓР·Р»С‹ -> Blockly -> РєРѕРґ ===")
from corpus import CORPUS                              # noqa: E402

for case in CORPUS:
    if case.syntax == "dsl":
        try:
            from tgblocks.dsl.parser import parse as parse_dsl
            spec = parse_dsl(case.source, case.name)
        except Exception as error:  # noqa: BLE001
            fail(case.name, "DSL РЅРµ СЂР°Р·Р±РёСЂР°РµС‚СЃСЏ: {0}".format(error))
            continue
    else:
        try:
            spec = parse_text(case.source, case.name)
        except Exception as error:  # noqa: BLE001
            fail(case.name, "С‚РµРєСЃС‚ РЅРµ СЂР°Р·Р±РёСЂР°РµС‚СЃСЏ: {0}".format(error))
            continue
    check_round_trip(case.name, spec)

for path in sorted((ROOT / "examples").glob("*.tg")):
    try:
        spec = parse_file(str(path))
    except Exception as error:  # noqa: BLE001
        fail(path.name, "РЅРµ СЂР°Р·Р±РёСЂР°РµС‚СЃСЏ: {0}".format(error))
        continue
    check_round_trip(path.name, spec)

# ------------------------------------------------------------- the live API
print()
print("=== 2. HTTP API ===")
import tempfile                                            # noqa: E402

server.STORAGE_DIR = pathlib.Path(tempfile.mkdtemp(prefix="tgblocks-qa-"))
httpd = ThreadingHTTPServer(("127.0.0.1", 0), server._Handler)
httpd.view = "nodes"
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = "http://127.0.0.1:{0}".format(httpd.server_address[1])


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=15) as response:
        raw = response.read().decode("utf-8")
        return json.loads(raw) if raw.lstrip().startswith(("{", "[")) else raw


def post(path, payload):
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(BASE + path, data=body,
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"ok": False, "error": raw}


SOURCE = (ROOT / "examples" / "full.tg").read_text(encoding="utf-8")
TEXT = spec_to_text(parse_file(str(ROOT / "examples" / "full.tg")))

for lang in ("ru", "en"):
    schema = get("/api/schema?lang=" + lang)
    if schema.get("version", 0) < 3 or not schema.get("blocks"):
        fail("schema", "РЅРµС‚ Р±Р»РѕРєРѕРІ РёР»Рё РІРµСЂСЃРёРё РґР»СЏ lang=" + lang)
    if schema.get("lang") != lang:
        fail("schema", "РЅРµ РІРµСЂРЅСѓР» lang=" + lang)

for path in ("/nodes", "/text", "/blocks", "/api/health", "/api/files?kind=bots"):
    try:
        get(path)
    except Exception as error:  # noqa: BLE001
        fail("GET " + path, error)

compile_cases = {
    "dsl": {"dsl": SOURCE},
    "text": {"nodes": spec_to_nodes(parse_file(str(ROOT / "examples" / "full.tg")))},
    "xml": {"xml": spec_to_blocks_xml(parse_file(str(ROOT / "examples" / "full.tg")))},
}
for name, payload in compile_cases.items():
    data = post("/api/compile", payload)
    if not data.get("ok"):
        fail("compile " + name, data.get("error") or data.get("detail"))
        continue
    if not data.get("code"):
        fail("compile " + name, "РїСѓСЃС‚РѕР№ РєРѕРґ")
    if "has_token" not in data:
        fail("compile " + name, "РЅРµС‚ has_token")

text_compile = post("/api/compile_text", {"source": TEXT})
if not text_compile.get("ok"):
    fail("compile_text", text_compile.get("error"))

# editor -> editor hand-off through the shared document
first = post("/api/project?name=qa", {"baseRev": 0, "text": TEXT})
if not first.get("ok"):
    fail("project save", first.get("error"))
else:
    stored = get("/api/project?name=qa")
    if stored["text"] != first["text"]:
        fail("project load", "С‚РµРєСЃС‚ РЅРµ СЃРѕРІРїР°РґР°РµС‚ СЃ СЃРѕС…СЂР°РЅС‘РЅРЅС‹Рј")
    to_nodes = post("/api/to_nodes?name=qa", {"source": stored["text"], "name": "qa"})
    if not to_nodes.get("ok"):
        fail("to_nodes", to_nodes.get("error"))
    else:
        back = post("/api/compile", {"nodes": to_nodes["nodes"]})
        if not back.get("ok"):
            fail("nodes->compile", back.get("error") or back.get("detail"))
        elif back.get("text") != stored["text"]:
            fail("nodes hand-off", "С‚РµРєСЃС‚ РёР·РјРµРЅРёР»СЃСЏ РїСЂРё РїРµСЂРµС…РѕРґРµ РІ СѓР·Р»С‹ Рё РѕР±СЂР°С‚РЅРѕ")
    to_blocks = post("/api/to_blocks", {"source": stored["text"]})
    if not to_blocks.get("ok"):
        fail("to_blocks", to_blocks.get("error"))
    else:
        from_xml = post("/api/compile", {"xml": to_blocks["xml"]})
        if not from_xml.get("ok"):
            fail("blocks->compile", from_xml.get("error") or from_xml.get("detail"))
        elif from_xml.get("text") != stored["text"]:
            fail("blocks hand-off", "С‚РµРєСЃС‚ РёР·РјРµРЅРёР»СЃСЏ РїСЂРё РїРµСЂРµС…РѕРґРµ РІ Р±Р»РѕРєРё Рё РѕР±СЂР°С‚РЅРѕ")
    stale = post("/api/project?name=qa", {"baseRev": 0, "text": TEXT})
    if not stale.get("conflict"):
        fail("project conflict", "СѓСЃС‚Р°СЂРµРІС€Р°СЏ СЂРµРІРёР·РёСЏ РЅРµ РѕС‚РєР»РѕРЅРµРЅР°")

print()
print("=== РёС‚РѕРі ===")
if failures:
    print("{0} РїСЂРѕР±Р»РµРјС‹(С‹):".format(len(failures)))
    for item in failures:
        print("  -", item)
else:
    print("РІСЃРµ РїСЂРѕРІРµСЂРєРё РїСЂРѕС€Р»Рё")

httpd.shutdown()
sys.exit(1 if failures else 0)

