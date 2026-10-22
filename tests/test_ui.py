# The editor HTTP API: the schema the pages are built from, and the two
# "compile this canvas" paths the node and block editors use.
#
# These tests speak to a real server, so a page that would break is caught here
# rather than by clicking through it.

import json
import sys
import pathlib
import subprocess
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

import tgblocks.visual.server as server
from tgblocks.convert import spec_to_blocks_xml, spec_to_nodes, spec_to_text
from tgblocks.dsl import compile_source
from tgblocks.textlang import parse_text

ROOT = pathlib.Path(__file__).resolve().parents[1]
STATIC = ROOT / "src" / "tgblocks" / "visual" / "static"

FULL = """token("1:TEST")
name("Demo bot")

on.command("/start"):
    send("РџСЂРёРІРµС‚!")
    button("РџРѕРјРѕС‰СЊ", "/help")

on.message(TEXT, "РїСЂРёРІРµС‚"):
    send_document("https://example.com/f.pdf", "С„Р°Р№Р»")
    when("contains", "РєРѕС‚"):
        send("РњСѓСЂ")
    otherwise():
        send("РќРµ РєРѕС‚")

on.callback("/buy"):
    send("РїРѕРєСѓРїР°РµРј")
"""


@pytest.fixture()
def api(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "STORAGE_DIR", tmp_path / "projects")
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server._Handler)
    httpd.view = "nodes"
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield "http://127.0.0.1:{0}".format(httpd.server_address[1])
    httpd.shutdown()
    httpd.server_close()


def get(base, path):
    with urllib.request.urlopen(base + path, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def post(base, path, payload):
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(base + path, data=body,
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return json.loads(error.read().decode("utf-8"))


# ------------------------------------------------------------------- the schema
def test_schema_describes_every_feature(api):
    schema = get(api, "/api/schema")
    assert schema["version"] >= 2
    assert len(schema["actions"]) >= 25
    assert len(schema["events"]) >= 20
    for action in schema["actions"]:
        assert action["kind"] and action["label"] and action["group"]
        assert isinstance(action["params"], list)
        assert action["observers"]
    for event in schema["events"]:
        assert event["kind"] and event["label"] and event["observer"]
    assert {"inline", "reply"} == {item["value"] for item in schema["keyboards"]}


def test_schema_covers_the_aiogram_methods_we_promise(api):
    kinds = {action["kind"] for action in get(api, "/api/schema")["actions"]}
    for needed in ("send_document", "send_video", "send_poll", "send_location",
                   "answer_callback", "edit_text", "set_state", "clear_state",
                   "ban_user", "mute_user", "inline_result"):
        assert needed in kinds


# --------------------------------------------------------------- node editor API
def test_board_compiles_into_text_and_code(api):
    spec = parse_text(FULL, "t")
    board = spec_to_nodes(spec)
    data = post(api, "/api/compile", {"nodes": board})
    assert data["ok"] is True, data
    assert data["text"] == spec_to_text(parse_text(spec_to_text(spec), "t2"))
    assert "async def" in data["code"]
    assert "answer_document" in data["code"]


def test_board_compiles_into_importable_aiogram_code(api):
    pytest.importorskip("aiogram")
    board = spec_to_nodes(parse_text(FULL, "t"))
    code = post(api, "/api/compile", {"nodes": board})["code"]
    namespace = {"__name__": "ui_board_bot", "__file__": "<generated>"}
    exec(compile(code, "<generated>", "exec"), namespace)
    assert namespace["dp"] is not None


def test_broken_board_is_an_answer_not_a_crash(api):
    data = post(api, "/api/compile", {"nodes": {"nodes": {"x": "nonsense"}}})
    assert data["ok"] is False
    assert data["error"]


def test_empty_board_is_an_answer_not_a_crash(api):
    data = post(api, "/api/compile", {"nodes": {}})
    assert data["ok"] is False or data.get("text") is not None


def test_boards_warnings_reach_the_page(api):
    # A button that calls a command nobody handles is worth showing in the UI.
    board = spec_to_nodes(parse_text(
        'token("1:x")\n\non.command("/start"):\n    send("m")\n'
        '    button("РќРµС‚", "/missing")\n', "t"))
    data = post(api, "/api/compile", {"nodes": board})
    assert data["ok"] is True
    assert any("/missing" in warning for warning in data["warnings"])


# -------------------------------------------------------------- block editor API
def test_xml_workspace_compiles(api):
    xml = spec_to_blocks_xml(parse_text(FULL, "t"))
    data = post(api, "/api/compile", {"xml": xml})
    assert data["ok"] is True, data
    assert "answer_document" in data["code"]


def test_invalid_xml_is_an_answer_not_a_crash(api):
    data = post(api, "/api/compile", {"xml": "<xml><block"})
    assert data["ok"] is False
    assert data["error"]


# --------------------------------------------------------------------- the pages
@pytest.mark.parametrize("page", ["nodes.html", "blocks.html", "text.html"])
def test_pages_exist_and_load(api, page):
    assert (STATIC / page).exists()
    status = urllib.request.urlopen(api + "/" + page.replace(".html", ""), timeout=10).status
    assert status == 200


@pytest.mark.parametrize("page", ["nodes.html", "blocks.html"])
def test_editors_use_the_schema_instead_of_hardcoded_tables(page):
    source = (STATIC / page).read_text(encoding="utf-8")
    assert "/api/schema" in source
    # The old hand-written tables are gone: a new feature is a catalogue entry.
    assert "actionsToDsl" not in source
    assert "workspaceToDsl" not in source


def test_every_page_javascript_parses():
    node = shutil_which("node")
    tool = ROOT / "tools" / "check_javascript.py"
    if node is None:
        pytest.skip("node is not installed")
    if not tool.exists():
        pytest.skip("tools/ is not part of this copy of the project")
    result = subprocess.run([sys.executable, str(tool)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def shutil_which(name):
    import shutil
    return shutil.which(name)
