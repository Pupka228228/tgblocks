# The local server's behaviour around ports: `tgblocks` must always end with a
# working editor, from any folder, and must never open a stale window after an
# upgrade without saying so.

import json
import socket
import threading
import urllib.error
import urllib.request

import pytest

import tgblocks.visual.server as server


@pytest.fixture()
def running_editor(tmp_path, monkeypatch):
    """A real tgblocks server on a free port, as the first instance."""
    monkeypatch.setattr(server, "STORAGE_DIR", tmp_path / "projects")
    httpd = server._Server(("127.0.0.1", 0), server._Handler)
    httpd.view = "nodes"
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield httpd.server_address[1]
    httpd.shutdown()
    httpd.server_close()


@pytest.fixture()
def stop_after_banner(monkeypatch):
    """Make serve() return right after printing the banner."""

    def fake_serve_forever(self):
        raise KeyboardInterrupt

    monkeypatch.setattr(server, "_Server", _OneShotServer)
    return None


class _OneShotServer(server._Server):
    def serve_forever(self):
        raise KeyboardInterrupt


def test_second_start_opens_the_running_editor(running_editor, capsys, monkeypatch):
    opened = []
    monkeypatch.setattr(server.webbrowser, "open", lambda url: opened.append(url))

    # No exception: the second invocation points at the editor that already runs.
    server.serve(port=running_editor, open_browser=True)

    printed = capsys.readouterr().out
    assert "http://127.0.0.1:{0}/".format(running_editor) in printed
    assert opened == ["http://127.0.0.1:{0}/".format(running_editor)]
    # Exactly one address is offered, not a list of ports to try.
    assert printed.count("http://") == 1


def test_an_old_window_does_not_stop_the_new_editor(capsys, monkeypatch):
    # A stale 0.1.0 keeps the port; the new code must still give the user an editor
    # and say where it went, instead of opening the old pages. The port is taken
    # for real, so the test does not depend on what happens to run on this machine.
    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker.bind(("127.0.0.1", 0))
    blocker.listen(1)
    port = blocker.getsockname()[1]
    monkeypatch.setattr(server, "_existing_editor", lambda host, taken: "0.0.1")
    monkeypatch.setattr(server.webbrowser, "open", lambda url: None)
    monkeypatch.setattr(server, "_Server", _OneShotServer)
    try:
        server.serve(port=port, open_browser=False)
    finally:
        blocker.close()

    printed = capsys.readouterr().out
    assert "old tgblocks 0.0.1" in printed
    assert "starting on " in printed
    assert printed.count("http://") == 1
    assert "http://127.0.0.1:{0}/".format(port) not in printed


def test_a_taken_port_moves_to_the_next_free_one(capsys, monkeypatch):
    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker.bind(("127.0.0.1", 0))
    blocker.listen(1)
    port = blocker.getsockname()[1]
    monkeypatch.setattr(server, "webbrowser", server.webbrowser)
    monkeypatch.setattr(server.webbrowser, "open", lambda url: None)
    monkeypatch.setattr(server, "_Server", _OneShotServer)
    try:
        server.serve(port=port, open_browser=False)
    finally:
        blocker.close()

    printed = capsys.readouterr().out
    assert "taken by another program" in printed
    assert "http://127.0.0.1:{0}/".format(port + 1) in printed
    assert printed.count("http://") == 1


def test_the_banner_names_one_address(capsys, monkeypatch):
    monkeypatch.setattr(server.webbrowser, "open", lambda url: None)
    monkeypatch.setattr(server, "_Server", _OneShotServer)

    free = server._find_free_port("127.0.0.1", 8800)
    server.serve(port=free, open_browser=False)

    printed = capsys.readouterr().out
    assert printed.count("http://") == 1
    assert "http://127.0.0.1:{0}/".format(free) in printed


def test_a_request_without_a_source_says_to_reload(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "STORAGE_DIR", tmp_path / "projects")
    httpd = server._Server(("127.0.0.1", 0), server._Handler)
    httpd.view = "nodes"
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    port = httpd.server_address[1]
    try:
        body = json.dumps({}).encode("utf-8")
        request = urllib.request.Request(
            "http://127.0.0.1:{0}/api/compile".format(port), data=body,
            headers={"Content-Type": "application/json"},
        )
        with pytest.raises(urllib.error.HTTPError) as info:
            urllib.request.urlopen(request, timeout=5)
        payload = json.loads(info.value.read().decode("utf-8"))
        assert info.value.code == 400
        assert "reload the editor page" in payload["error"]
        assert "Ctrl+F5" in payload["error"]
    finally:
        httpd.shutdown()
        httpd.server_close()


def test_find_free_port_skips_busy_ones():
    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    blocker.bind(("127.0.0.1", 0))
    blocker.listen(1)
    busy = blocker.getsockname()[1]
    try:
        found = server._find_free_port("127.0.0.1", busy, tries=5)
        assert found is not None and found > busy
    finally:
        blocker.close()
