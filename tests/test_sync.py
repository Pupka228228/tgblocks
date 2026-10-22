# Tests for the shared project store: every visual editor has to see the same
# bot, and no conversion may quietly drop part of it.
#
# The three views are only different pictures of one text document, so these
# tests pin down that promise: text -> nodes -> text and text -> blocks -> text
# keep every action, every pattern and the canvas layout.

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from tgblocks.convert import (
    board_layout,
    board_to_text,
    spec_to_blocks_xml,
    spec_to_nodes,
    spec_to_text,
)
from tgblocks.dsl.parser import parse
from tgblocks.textlang import parse_text

FULL = """token("123456:TEST")
name("Demo bot")
proxy("socks5://127.0.0.1:1080")

on.command("/start"):
    send("Привет!")
    buttons("inline")
    button("Помощь", "/help")
    button("Сайт", url="https://example.com")

on.message(TEXT, "привет", "здравствуй"):
    typing()
    delay(2)
    send_photo("https://example.com/cat.jpg", "Котик")
    delete()

on.message(PHOTO):
    when("contains", "кот"):
        send("Мур")
    otherwise():
        send("Не кот")
    pass
"""


def _canonical(text: str) -> str:
    return spec_to_text(parse_text(text, "test.txt"))


def test_text_survives_the_node_board():
    canonical = _canonical(FULL)
    assert board_to_text(spec_to_nodes(parse_text(canonical, "t"))) == canonical


def test_text_survives_the_block_editor():
    # The blocks view cannot show every node, so its XML must carry them all.
    canonical = _canonical(FULL)
    xml = spec_to_blocks_xml(parse_text(canonical, "t"))
    for needed in ("tg_photo", "tg_typing", "tg_delay", "tg_delete", "tg_nothing"):
        assert '<block type="{}"'.format(needed) in xml
    assert '<field name="NAME">Demo bot</field>' in xml
    assert '<field name="PROXY">socks5://127.0.0.1:1080</field>' in xml


def test_event_filter_travels_with_the_bot():
    # `on.message(TEXT, "a", "b")` is a filter on the event, not a condition:
    # it must survive both canvases instead of being rewritten or dropped.
    spec = parse_text('token("1:x")\non.message(TEXT, "привет", "здравствуй"):\n'
                      '    send("Hi")\n', "t")

    xml = spec_to_blocks_xml(spec)
    assert '<field name="PATTERNS">привет, здравствуй</field>' in xml

    board = spec_to_nodes(spec)
    events = [node for node in board["nodes"].values() if node["type"] == "event"]
    assert events[0]["props"]["patterns"] == ["привет", "здравствуй"]
    assert board_to_text(board) == _canonical(
        'token("1:x")\non.message(TEXT, "привет", "здравствуй"):\n    send("Hi")\n'
    )


def test_condition_with_several_values_survives_every_view():
    # `when("contains", "Привет";"привет")` is one condition, not two branches.
    text = ('token("1:x")\n\non.message(TEXT):\n'
            '    when("contains", "Привет"; "привет"):\n'
            '        send("Привет!")\n'
            '    otherwise():\n'
            '        pass\n')
    canonical = _canonical(text)
    board = spec_to_nodes(parse_text(canonical, "t"))
    assert board_to_text(board) == canonical

    xml = spec_to_blocks_xml(parse_text(canonical, "t"))
    assert '<field name="VALUE">Привет</field>' in xml
    assert '<field name="VALUES">привет</field>' in xml


def test_dsl_accepts_several_condition_values():
    spec = parse('bot token "1:x"\non /start:\n'
                 '    when text contains "Привет", "привет":\n'
                 '        send "hi"\n')
    condition = spec.handlers[0].actions[0].condition
    assert condition.op == "contains"
    assert (condition.value,) + condition.values == ("Привет", "привет")



def test_node_board_keeps_the_bot_name_and_the_text_filter():
    board = spec_to_nodes(parse_text(FULL, "t"))
    bot = board["nodes"][board["rootId"]]
    assert bot["props"]["name"] == "Demo bot"

    events = [node for node in board["nodes"].values() if node["type"] == "event"]
    filtered = [node for node in events if node["props"].get("patterns")]
    assert filtered[0]["props"]["patterns"] == ["привет", "здравствуй"]


def test_layout_survives_rebuilding_the_board():
    spec = parse_text(FULL, "t")
    board = spec_to_nodes(spec)
    moved = board["rootId"]
    board["nodes"][moved]["x"] = 999
    board["nodes"][moved]["y"] = 777

    layout = board_layout(board)
    rebuilt = spec_to_nodes(parse_text(FULL, "t"), layout)

    assert rebuilt["nodes"][moved]["x"] == 999
    assert rebuilt["nodes"][moved]["y"] == 777


def test_dsl_accepts_text_patterns():
    spec = parse('bot token "1:x"\non message "a", "b":\n    send "hi"\n')
    assert spec.handlers[0].kind == "text"
    assert spec.handlers[0].patterns == ("a", "b")


# ------------------------------------------------------------- the HTTP store
@pytest.fixture()
def api(tmp_path, monkeypatch):
    import tgblocks.visual.server as server

    monkeypatch.setattr(server, "STORAGE_DIR", tmp_path / "projects")
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server._Handler)
    httpd.view = "nodes"
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = "http://127.0.0.1:{0}".format(httpd.server_address[1])
    yield base
    httpd.shutdown()
    httpd.server_close()


def _get(base: str, path: str):
    with urllib.request.urlopen(base + path) as response:
        return json.loads(response.read().decode("utf-8"))


def _post(base: str, path: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        base + path, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def test_store_round_trip_and_revisions(api):
    empty = _get(api, "/api/project?name=bot1")
    assert empty["text"] == "" and empty["rev"] == 0

    first = _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})
    assert first["ok"] and first["rev"] == 1
    assert first["text"] == _canonical(FULL)
    assert _get(api, "/api/rev?name=bot1")["rev"] == 1

    second = _post(api, "/api/project?name=bot1",
                   {"baseRev": 1, "text": first["text"].replace("Привет!", "Здравствуйте!")})
    assert second["ok"] and second["rev"] == 2
    assert "Здравствуйте!" in _get(api, "/api/project?name=bot1")["text"]


def test_stale_editor_gets_a_conflict_instead_of_overwriting(api):
    _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})
    # A second tab still believes the file is at revision 0.
    stale = _post(api, "/api/project?name=bot1",
                  {"baseRev": 0, "text": 'token("1:x")\non.command("/a"):\n    send("x")\n'})
    assert stale["ok"] is False and stale["conflict"] is True
    assert stale["rev"] == 1
    assert "Привет" in stale["text"]          # the editor reloads this text
    assert "Привет" in _get(api, "/api/project?name=bot1")["text"]


def test_broken_text_is_rejected_and_not_stored(api):
    good = _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})
    bad = _post(api, "/api/project?name=bot1",
                {"baseRev": good["rev"], "text": 'token("1:x")\n'})
    assert bad["ok"] is False and ("event" in bad["error"] or "handler" in bad["error"])
    stored = _get(api, "/api/project?name=bot1")
    assert stored["rev"] == good["rev"]
    assert stored["text"] == _canonical(FULL)


def test_layout_is_saved_without_a_new_revision(api):
    _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})
    payload = {"layout": {"b": {"x": 10, "y": 20}}}
    _post(api, "/api/project_layout?name=bot1", payload)

    stored = _get(api, "/api/project?name=bot1")
    assert stored["rev"] == 1                  # dragging blocks is not an edit
    assert stored["layout"] == {"b": {"x": 10, "y": 20}}


def test_board_comes_back_where_it_was(api):
    _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})
    _post(api, "/api/project_layout?name=bot1", {"layout": {"b": {"x": 500, "y": 600}}})

    board = _post(api, "/api/to_nodes?name=bot1", {"source": _canonical(FULL), "name": "bot1"})
    assert board["ok"]
    assert board["nodes"]["nodes"][board["nodes"]["rootId"]]["x"] == 500


def test_old_project_files_are_read_as_text(api, tmp_path):
    folder = tmp_path / "projects" / "bots"
    folder.mkdir(parents=True)
    legacy = {
        "nodes": spec_to_nodes(parse_text(FULL, "t")),
        "text": FULL,
        "stamp": {"nodes": 111, "text": 222},
    }
    (folder / "old.json").write_text(json.dumps(legacy), encoding="utf-8")

    stored = _get(api, "/api/project?name=old")
    assert stored["rev"] == 1
    assert stored["text"] == _canonical(FULL)
    assert stored["layout"]                   # canvas positions kept


def test_edit_in_one_view_reaches_the_others(api):
    # 1. The text view writes a bot.
    first = _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})
    assert first["ok"]

    # 2. The node view opens it: it gets the same bot as a board.
    board = _post(api, "/api/to_nodes?name=bot1",
                  {"source": _get(api, "/api/project?name=bot1")["text"], "name": "bot1"})
    nodes = board["nodes"]["nodes"]

    # 3. The user edits one send block in the node view and saves the board.
    send = [node for node in nodes.values() if node["type"] == "send"][0]
    send["props"]["text"] = "Правка из узлов"
    saved = _post(api, "/api/project?name=bot1",
                  {"baseRev": first["rev"], "nodes": board["nodes"]})
    assert saved["ok"] and saved["changed"] is True
    assert saved["rev"] == first["rev"] + 1

    # 4. The text view polls the revision and reads the edit.
    assert _get(api, "/api/rev?name=bot1")["rev"] == saved["rev"]
    assert "Правка из узлов" in _get(api, "/api/project?name=bot1")["text"]

    # 5. The block view renders it from that same text.
    xml = _post(api, "/api/to_blocks", {"source": saved["text"]})
    assert xml["ok"] and "Правка из узлов" in xml["xml"]


def test_dragging_blocks_does_not_rewrite_the_bot(api):
    plain = 'token("1:x")\n\non.command("/start"):\n    send("Hi")\n'
    first = _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": plain})
    board = _post(api, "/api/to_nodes?name=bot1", {"source": first["text"], "name": "bot1"})
    root = board["nodes"]["rootId"]
    board["nodes"]["nodes"][root]["x"] = 1234

    # Same bot, new position: the text did not change, so no view reloads.
    moved = _post(api, "/api/project?name=bot1",
                  {"baseRev": first["rev"], "nodes": board["nodes"]})
    assert moved["ok"] and moved["changed"] is False
    assert moved["rev"] == first["rev"]

    stored = _get(api, "/api/project?name=bot1")
    assert stored["layout"]["b"] == {"x": 1234, "y": board["nodes"]["nodes"][root]["y"]}


def test_unfinished_board_is_kept_as_a_draft(api):
    first = _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})
    # A canvas with only a bot block and no token: not a bot yet.
    draft = {"nodes": {"b1": {"id": "b1", "type": "bot", "props": {"token": ""},
                              "parent": None, "children": [], "x": 0, "y": 0}},
             "counter": 1, "rootId": "b1", "manual": True}
    reply = _post(api, "/api/project?name=bot1", {"baseRev": first["rev"], "nodes": draft})
    assert reply["ok"] and reply["incomplete"] is True
    assert reply["rev"] == first["rev"]          # the good text is untouched

    stored = _get(api, "/api/project?name=bot1")
    assert stored["draft"]["board"]["rootId"] == "b1"
    assert "Привет" in stored["text"]


def test_shared_module_is_served(api):
    with urllib.request.urlopen(api + "/tgblocks-project.js") as response:
        body = response.read().decode("utf-8")
    assert "TgProject" in body


def test_block_editor_reads_every_field_it_is_given():
    # The block editor now round-trips through Blockly XML, so the invariant is
    # that the XML reader understands every field the writer emits and that the
    # bot comes back unchanged. A field the reader ignores would be a silent
    # data loss on the next save.
    import re

    from tgblocks.convert import blocks_xml_to_spec
    from tgblocks.model import ACTIONS, EVENTS

    xml = spec_to_blocks_xml(parse_text(FULL, "t"))
    emitted = set(re.findall(r'<field name="([A-Za-z_]+)"', xml))

    allowed = {"TOKEN", "NAME", "PROXY", "WEBHOOK", "KIND", "COMMAND", "PATTERNS",
               "DATA", "STATE", "CHAT", "FROM_USER", "REGEX", "LABEL", "TARGET",
               "STYLE", "OP", "VALUE", "VALUES", "SOURCE"}
    for spec in list(ACTIONS) + list(EVENTS):
        for param in spec.params:
            allowed.add(param.name.upper())

    assert emitted - allowed == set()
    assert spec_to_text(blocks_xml_to_spec(xml)) == _canonical(FULL)


def test_board_save_that_would_drop_an_event_filter_is_refused(api):
    filtered = 'token("1:x")\n\non.message(TEXT, "привет"):\n    send("Hi")\n'
    first = _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": filtered})

    # A board that cannot carry the filter (the block editor has no field for
    # it) would silently drop it: the server refuses instead.
    board = _post(api, "/api/to_nodes?name=bot1", {"source": first["text"], "name": "bot1"})
    nodes = board["nodes"]["nodes"]
    event = [node for node in nodes.values() if node["type"] == "event"][0]
    event["props"].pop("patterns", None)
    reply = _post(api, "/api/project?name=bot1",
                  {"baseRev": first["rev"], "nodes": board["nodes"]})
    assert reply["ok"] is False and reply["lossy"] is True
    assert "текст" in reply["error"]

    stored = _get(api, "/api/project?name=bot1")
    assert stored["text"] == first["text"]     # the bot is untouched


