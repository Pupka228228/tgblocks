# Clearing a view clears the bot for all three views.
#
# The project store kept the last good text when a canvas was empty ("unfinished
# canvas"), which is right for a half-built board but wrong for "delete
# everything": the other views kept showing code the user had removed.

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

import tgblocks.visual.server as server
from tgblocks.convert import spec_to_nodes, spec_to_text
from tgblocks.textlang import parse_text

FULL = """token("1:TEST")

on.command("/start"):
    send("Привет!")
"""


@pytest.fixture()
def api(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "STORAGE_DIR", tmp_path / "projects")
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server._Handler)
    httpd.view = "nodes"
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
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
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def test_an_empty_board_clears_the_bot(api):
    first = post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})
    assert first["ok"] and first["rev"] == 1

    # The node editor deletes every block: the board arrives with no nodes.
    cleared = post(api, "/api/project?name=bot1",
                   {"baseRev": first["rev"], "nodes": {"nodes": {}, "rootId": None}})
    assert cleared["ok"] is True
    assert cleared["text"] == ""
    assert cleared["rev"] == first["rev"] + 1, "должна появиться новая ревизия"

    # The other views poll the revision and read the empty text.
    stored = get(api, "/api/project?name=bot1")
    assert stored["text"] == ""
    assert stored["rev"] == cleared["rev"]


def test_empty_text_from_the_text_view_also_clears(api):
    first = post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})
    cleared = post(api, "/api/project?name=bot1", {"baseRev": first["rev"], "text": ""})
    assert cleared["ok"] is True and cleared["text"] == ""
    assert get(api, "/api/project?name=bot1")["text"] == ""


def test_clearing_twice_does_not_bump_the_revision(api):
    post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})
    first = post(api, "/api/project?name=bot1", {"baseRev": 1, "text": ""})
    second = post(api, "/api/project?name=bot1",
                  {"baseRev": first["rev"], "nodes": {"nodes": {}}})
    assert second["ok"] is True
    assert second["rev"] == first["rev"]
    assert second["text"] == ""


def test_a_half_built_board_still_keeps_the_last_good_text(api):
    # A canvas with a bot but no events is not "delete everything": the bot text
    # must survive so the user does not lose it while dragging blocks around.
    first = post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})
    draft = {"nodes": {"b1": {"id": "b1", "type": "bot", "props": {"token": ""},
                              "parent": None, "children": [], "x": 0, "y": 0}},
             "counter": 1, "rootId": "b1"}
    reply = post(api, "/api/project?name=bot1", {"baseRev": first["rev"], "nodes": draft})
    assert reply["ok"] is True and reply.get("incomplete") is True
    stored = get(api, "/api/project?name=bot1")
    assert stored["text"] == _canonical(FULL)
    assert stored["rev"] == first["rev"]


def test_reopening_the_view_after_clearing_starts_from_nothing(api):
    post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})
    post(api, "/api/project?name=bot1", {"baseRev": 1, "text": ""})
    stored = get(api, "/api/project?name=bot1")
    # The document is empty and no draft survives, so every editor opens blank:
    # the page draws the empty canvas itself instead of asking for a conversion.
    assert stored["text"] == ""
    assert stored["draft"] is None
    assert stored["layout"] == {} or isinstance(stored["layout"], dict)


def _canonical(text: str) -> str:
    return spec_to_text(parse_text(text, "t"))
