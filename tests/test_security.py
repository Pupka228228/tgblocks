# The editor is a local web server that can start processes, so it is a target:
# any page the user visits could POST to 127.0.0.1 while the editor is open.
# These tests replay the attacks that used to work and must keep failing.

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

import tgblocks.visual.server as server

GOOD_TEXT = 'token("1:x")\n\non.command("/start"):\n    send("hi")\n'


@pytest.fixture()
def api(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "STORAGE_DIR", tmp_path / "projects")
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server._Handler)
    httpd.view = "nodes"
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = "http://127.0.0.1:{0}".format(httpd.server_address[1])
    yield base
    httpd.shutdown()
    httpd.server_close()


def request(base, path, payload=None, headers=None, method=None):
    """Return (status, body) and never raise for 4xx/5xx; body is JSON when it is."""
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(base + path, data=data, headers=headers or {},
                                 method=method)

    def parse(raw):
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, parse(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        return error.code, parse(error.read().decode("utf-8"))


JSON = {"Content-Type": "application/json"}


# --------------------------------------------------------------------- the attacks
def test_cross_origin_post_is_refused(api):
    # Exactly the request a hostile page can send with fetch(..., {mode:"no-cors"}).
    status, body = request(
        api,
        "/api/run",
        {"code": "print('ARBITRARY-CODE-RAN')"},
        headers={
            "Origin": "https://evil.example",
            "Content-Type": "text/plain;charset=UTF-8",
        },
    )
    assert status in (403, 415)
    assert body.get("ok") is False
    assert server.RUNNER.running() is False


def test_cross_origin_write_is_refused_and_stores_nothing(api):
    status, _ = request(
        api,
        "/api/project?name=stolen",
        {"baseRev": 0, "text": GOOD_TEXT},
        headers={"Origin": "https://evil.example", "Content-Type": "text/plain"},
    )
    assert status in (403, 415)
    status, body = request(api, "/api/files?kind=bots", headers=JSON)
    assert status == 200 and body["files"] == []


def test_sec_fetch_site_cross_site_is_refused(api):
    status, _ = request(
        api,
        "/api/project?name=stolen",
        {"text": GOOD_TEXT},
        headers={"Sec-Fetch-Site": "cross-site", **JSON},
    )
    assert status == 403


def test_dns_rebinding_host_is_refused(api):
    # A hostile domain pointed at 127.0.0.1 keeps its own name in Host.
    status, _ = request(api, "/api/files?kind=bots",
                        headers={"Host": "evil.example:80"})
    assert status == 403


def test_non_json_body_is_refused(api):
    # `<form enctype="text/plain">` and no-cors fetches cannot lie about this.
    status, _ = request(api, "/api/compile", {"dsl": GOOD_TEXT},
                        headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert status == 415


def test_preflight_does_not_grant_cors(api):
    req = urllib.request.Request(api + "/api/run", method="OPTIONS")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            headers = dict(response.headers)
            status = response.status
    except urllib.error.HTTPError as error:
        headers = dict(error.headers)
        status = error.code
    assert status >= 400
    assert "Access-Control-Allow-Origin" not in headers


# ------------------------------------------------------------- the editor still works
def test_same_origin_json_request_still_works(api):
    status, body = request(
        api,
        "/api/compile",
        {"dsl": 'bot token "1:x"\n\non /start:\n    send "hi"\n'},
        headers={"Origin": api, **JSON},
    )
    assert status == 200 and body["ok"] is True
    assert "async def" in body["code"]


def test_the_page_itself_loads(api):
    status, _ = request(api, "/nodes")
    assert status == 200


def test_wide_bind_needs_an_explicit_flag():
    with pytest.raises(SystemExit) as info:
        server.serve(host="0.0.0.0", open_browser=False)
    assert "allow-remote" in str(info.value)
