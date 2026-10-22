# Tiny localhost HTTP server that hosts the visual editors.
#
# Routes:
#   GET  /              the editor chosen with --view (nodes by default)
#   GET  /nodes         box-and-wire editor
#   GET  /blocks        Blockly editor (needs the CDN on first load)
#   GET  /api/health    {"ok": true, "version": "...", "view": "..."}
#   POST /api/compile   {"dsl": "..."} -> {"ok": true, "dsl": "...", "code": "..."}
#                                        {"ok": false, "error": "...", "detail": "..."}
#
# The browser never compiles anything itself: both editors turn their model into
# DSL text and POST it here, so the parser and the code generator stay in Python.

from __future__ import annotations

import collections
import json
import mimetypes
import re
import os
import socket
import subprocess
import sys
import tempfile
import threading
import webbrowser
from urllib.parse import unquote
from urllib.request import urlopen
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .. import __version__
from ..convert import (
    blocks_xml_to_spec,
    board_layout,
    board_to_spec,
    board_to_text,
    spec_to_blocks_xml,
    spec_to_nodes,
    spec_to_text,
)
from ..dsl.codegen import generate
from ..dsl.parser import DSLParseError, parse, validate
from ..model import schema as feature_schema
from ..textlang import parse_text

STATIC_DIR = Path(__file__).resolve().parent / "static"
STORAGE_DIR = Path.home() / ".tgblocks" / "projects"
FILE_KINDS = ("bots",)
FILE_NAME_RE = re.compile(r"^[A-Za-z0-9_\-]{1,32}$")

# The editor is a local tool that can start processes, so the browser must not be
# able to drive it from any other page. Everything below is a guard against the
# three ways that happens in practice:
#
#   * CSRF - a page on another site POSTs to 127.0.0.1 (no-cors requests carry a
#     simple Content-Type and no custom headers, so requiring JSON is enough);
#   * DNS rebinding - evil.example resolves to 127.0.0.1, so the Host header has
#     to be one of ours, not the attacker's domain;
#   * a deliberate wide bind (`--host 0.0.0.0`) that puts an unprotected code
#     runner on the network, which now needs an explicit --allow-remote.
LOOPBACK_NAMES = {"127.0.0.1", "localhost", "::1"}
JSON_TYPE = "application/json"



def _query(path: str, key: str, default: str = "") -> str:
    query = path.split("?", 1)[1] if "?" in path else ""
    for chunk in query.split("&"):
        if chunk.startswith(key + "="):
            return unquote(chunk[len(key) + 1:])
    return default


def _project_path(kind: str, name: str) -> Path:
    if kind not in FILE_KINDS:
        raise ValueError("unknown file kind")
    if not FILE_NAME_RE.match(name or ""):
        raise ValueError("bad file name: use letters, digits, _ and -")
    return STORAGE_DIR / kind / (name + ".json")


# ---------------------------------------------------------------- project store
# One file per bot holds one canonical document:
#
#   {"rev": 7, "text": "<canonical text syntax>", "layout": {"b/a1": {"x":..}}}
#
# `text` is the bot itself; `layout` is only where the blocks sit on the canvas,
# so it never invalidates another view. Every editor reads and writes this same
# document, which is what keeps the three views in step.
PROJECT_LOCK = threading.Lock()


def _empty_project() -> dict:
    return {"rev": 0, "text": "", "layout": {}, "draft": None}


def _normalise_project(raw) -> dict:
    project = _empty_project()
    if not isinstance(raw, dict):
        return project
    text = raw.get("text")
    if isinstance(text, str):
        project["text"] = text
    layout = raw.get("layout")
    if isinstance(layout, dict):
        project["layout"] = layout
    draft = raw.get("draft")
    if isinstance(draft, dict) and isinstance(draft.get("board"), dict):
        project["draft"] = draft
    rev = raw.get("rev")
    if isinstance(rev, int) and not isinstance(rev, bool) and rev >= 0:
        project["rev"] = rev
    elif raw:
        # A file written by an older version: it has no revision yet.
        project["rev"] = 1
    # Older files kept the board as well: take the canvas positions from it and
    # rebuild the text when the file has none.
    board = raw.get("nodes")
    if isinstance(board, dict):
        if not project["text"]:
            try:
                project["text"] = board_to_text(board)
            except Exception:  # a damaged board must not make the file unreadable
                project["text"] = ""
        if not project["layout"]:
            try:
                project["layout"] = board_layout(board)
            except Exception:
                project["layout"] = {}
    # All three views must receive the very same text, so canonicalise what is
    # stored: a file written by an older version or by hand may be formatted
    # differently while meaning the same bot.
    if project["text"]:
        try:
            project["text"] = spec_to_text(parse_text(project["text"], "project.txt"))
        except Exception:  # keep the raw text: the editor will show the error
            pass
    return project


def _read_project(name: str) -> dict:
    path = _project_path("bots", name)
    if not path.exists():
        return _empty_project()
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return _empty_project()
    return _normalise_project(raw)


def _write_project(name: str, project: dict) -> None:
    path = _project_path("bots", name)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(
        {
            "rev": project["rev"],
            "text": project["text"],
            "layout": project["layout"],
            "draft": project.get("draft"),
        },
        ensure_ascii=False,
    )
    # write-then-rename: a crash mid-save must not truncate the bot
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    os.replace(temporary, path)


def _board_is_empty(board) -> bool:
    nodes = board.get("nodes") if isinstance(board, dict) else None
    return not isinstance(nodes, dict) or not nodes


def _pattern_count(text: str) -> int:
    if not text:
        return 0
    try:
        spec = parse_text(text, "project.txt")
    except Exception:
        return 0
    return sum(len(handler.patterns) for handler in spec.handlers)


def _has_real_token(spec) -> bool:
    # A placeholder is not a token: the editor should still ask for a real one.
    from ..runner import PLACEHOLDER_TOKENS

    return bool(spec.token and spec.token not in PLACEHOLDER_TOKENS)


def _clear_project(name: str, project: dict, layout) -> dict:
    # Emptying a view empties the shared document: a new revision makes the other
    # editors reload instead of keeping the code the user just deleted.
    changed = bool(project["text"])
    project["text"] = ""
    project["draft"] = None
    if isinstance(layout, dict):
        project["layout"] = layout
    if changed:
        project["rev"] += 1
    _write_project(name, project)
    return {"ok": True, "rev": project["rev"], "text": "", "changed": changed}


def _save_project(name: str, incoming: dict) -> dict:
    # Applies one edit, from whichever view made it.
    #
    # `board` (the node canvas) also carries unconnected blocks and positions,
    # which the text cannot express: it is kept as a draft tied to the revision
    # it belongs to, so the canvas survives a reload while the text stays the
    # contract every view shares.
    #
    # `base_rev` is the revision the editor last saw: if the file moved on, the
    # edit is refused instead of silently overwriting the other view's work.
    board = incoming.get("nodes")
    text = incoming.get("text")
    layout = incoming.get("layout")
    with PROJECT_LOCK:
        project = _read_project(name)
        base_rev = incoming.get("baseRev")
        if isinstance(base_rev, int) and base_rev != project["rev"]:
            return {
                "ok": False,
                "conflict": True,
                "rev": project["rev"],
                "text": project["text"],
                "error": "файл изменён в другом виде",
            }

        if isinstance(board, dict) and _board_is_empty(board):
            # "Delete everything" is a real edit, not an unfinished canvas:
            # every other view has to forget the bot too, otherwise the old code
            # keeps showing up where the user already removed it.
            return _clear_project(name, project, layout)

        if isinstance(board, dict):
            try:
                text = board_to_text(board)
                layout = board_layout(board)
            except Exception:
                text = ""
            if not isinstance(text, str) or not text.strip():
                # An unfinished canvas: keep it as a draft, touch nothing else.
                project["draft"] = (
                    None if _board_is_empty(board)
                    else {"board": board, "rev": project["rev"]}
                )
                _write_project(name, project)
                return {"ok": True, "rev": project["rev"], "text": project["text"],
                        "incomplete": True}

        if isinstance(text, str) and not text.strip():
            # The text view was cleared on purpose.
            return _clear_project(name, project, layout)

        try:
            spec = parse_text(text, name + ".txt")
        except DSLParseError as error:
            reply = {
                "ok": False,
                "error": error.message,
                "line": error.line,
                "column": error.column,
                "detail": error.render(name + ".txt"),
            }
            if isinstance(board, dict):
                # Half-built boards are normal while editing: store the draft so
                # the canvas is not lost, and keep the last good text.
                project["draft"] = (
                    None if _board_is_empty(board)
                    else {"board": board, "rev": project["rev"]}
                )
                _write_project(name, project)
                reply["incomplete"] = True
            return reply

        canonical = spec_to_text(spec)
        if isinstance(board, dict) and _pattern_count(project["text"]) and not _pattern_count(
            canonical
        ):
            # The block editor has no field for an exact-text filter on an event.
            # Refuse instead of silently dropping it from the bot.
            return {
                "ok": False,
                "lossy": True,
                "rev": project["rev"],
                "text": project["text"],
                "error": "в боте есть фильтр текста у события - он сохраняется "
                         "только из «Вид: текст»",
            }
        changed = canonical != project["text"]
        project["text"] = canonical
        if isinstance(layout, dict):
            project["layout"] = layout
        if changed:
            project["rev"] += 1
        if isinstance(board, dict):
            project["draft"] = {"board": board, "rev": project["rev"]}
        _write_project(name, project)

    return {"ok": True, "rev": project["rev"], "text": project["text"],
            "changed": changed}


def migrate_legacy_files() -> None:
    # Move old per-view projects (nodes/, text/) into the shared bots/ files.
    bots = STORAGE_DIR / "bots"
    bots.mkdir(parents=True, exist_ok=True)
    for kind, key in (("nodes", "nodes"), ("text", "text")):
        folder = STORAGE_DIR / kind
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.json")):
            try:
                payload = json.loads(path.read_text(encoding="utf-8-sig"))
            except (OSError, json.JSONDecodeError):
                continue
            target = bots / path.name
            merged = {}
            if target.exists():
                try:
                    merged = json.loads(target.read_text(encoding="utf-8-sig"))
                except (OSError, json.JSONDecodeError):
                    merged = {}
            if not isinstance(merged, dict):
                merged = {}
            if key in merged:
                continue
            if kind == "nodes" and isinstance(payload, dict) and "nodes" in payload:
                merged[key] = payload
            elif isinstance(payload, dict) and key in payload:
                merged[key] = payload[key]
            else:
                merged[key] = payload
            target.write_text(json.dumps(merged, ensure_ascii=False), encoding="utf-8")


def _list_projects(kind: str):
    folder = STORAGE_DIR / kind
    if not folder.exists():
        return []
    return sorted(item.stem for item in folder.glob("*.json"))
LOG_LIMIT = 400


class _Runner:
    # Keeps one bot process alive and remembers its output for the log pane.

    def __init__(self) -> None:
        self.process = None
        self.lines = collections.deque(maxlen=LOG_LIMIT)
        self.lock = threading.Lock()

    def running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def start(self, code: str, token: str = "") -> int:
        self.stop()
        folder = tempfile.mkdtemp(prefix="tgblocks-run-")
        target = Path(folder) / "bot.py"
        target.write_text(code, encoding="utf-8")
        env = dict(os.environ)
        if token:
            env["TG_BOT_TOKEN"] = token
        with self.lock:
            self.lines.clear()
        self.process = subprocess.Popen(
            [sys.executable, "-u", str(target)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        threading.Thread(target=self._read, args=(self.process,), daemon=True).start()
        return self.process.pid

    def _read(self, process) -> None:
        if process.stdout is None:
            return
        for line in process.stdout:
            with self.lock:
                self.lines.append(line.rstrip())
        with self.lock:
            self.lines.append("--- процесс завершился ---")

    def snapshot(self, since: int):
        with self.lock:
            lines = list(self.lines)
        return {"running": self.running(), "lines": lines[since:], "total": len(lines)}

    def stop(self) -> None:
        process = self.process
        self.process = None
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


RUNNER = _Runner()
VIEWS = {"nodes": "nodes.html", "blocks": "blocks.html", "text": "text.html"}
MAX_BODY = 2 * 1024 * 1024


def _split_host(value: str):
    # Host: "127.0.0.1:8765", "localhost", "[::1]:8765" -> (name, port or None)
    value = (value or "").strip()
    if value.startswith("["):
        end = value.find("]")
        if end < 0:
            return value, None
        name = value[1:end]
        rest = value[end + 1:]
        return name, rest[1:] if rest.startswith(":") else None
    if ":" in value:
        name, _, port = value.rpartition(":")
        return name, port
    return value, None


def _host_is_ours(value: str, port: int) -> bool:
    name, given_port = _split_host(value)
    if name.lower() not in LOOPBACK_NAMES and name != "127.0.0.1":
        return False
    if given_port in (None, ""):
        return True
    return given_port == str(port)


def _origin_is_ours(value: str, port: int) -> bool:
    # Origin: "http://127.0.0.1:8765" (the scheme is not part of the decision).
    for scheme in ("http://", "https://"):
        if value.startswith(scheme):
            return _host_is_ours(value[len(scheme):], port)
    if value in ("null", ""):
        return False
    return _host_is_ours(value, port)


class _Handler(BaseHTTPRequestHandler):
    server_version = "tgblocks"

    def log_message(self, fmt, *args):  # keep the terminal quiet
        return

    # -------------------------------------------------------------- same-origin
    def _discard_body(self) -> None:
        # Answer a refusal only after the client finished writing its body,
        # otherwise the socket closes mid-request and the browser sees a reset
        # instead of the reason. A body that was already read is not read twice.
        if getattr(self, "_body_read", False):
            return
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if 0 < length <= MAX_BODY:
            try:
                self.rfile.read(length)
            except OSError:
                pass
        self._body_read = True

    def _reject(self, status: int, error: str) -> None:
        self._discard_body()
        self._json(status, {"ok": False, "error": error})

    def _guard(self) -> bool:
        # False means the request was already answered and must not be handled.
        port = self.server.server_address[1]
        if not _host_is_ours(self.headers.get("Host", ""), port):
            self._reject(403, "wrong Host header: the editor only answers on 127.0.0.1")
            return False
        site = (self.headers.get("Sec-Fetch-Site") or "").strip().lower()
        if site and site not in ("same-origin", "none"):
            self._reject(403, "cross-site request refused")
            return False
        origin = self.headers.get("Origin")
        if origin and not _origin_is_ours(origin, port):
            self._reject(403, "cross-origin request refused")
            return False
        return True

    def _same_origin_only(self) -> None:
        # Answer a CORS preflight with "no": the request is then never sent.
        self.send_response(405)
        self.send_header("Allow", "GET, POST")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_OPTIONS(self) -> None:  # noqa: N802 - required by http.server
        self._same_origin_only()

    # ------------------------------------------------------------------ helpers
    def _send(self, status: int, body, content_type: str = "application/json; charset=utf-8") -> None:
        payload = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        # no caching: otherwise the browser keeps the old editor JS after updates
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(payload)

    def _json(self, status: int, data) -> None:
        self._send(status, json.dumps(data, ensure_ascii=False))

    def _page(self, name: str) -> None:
        path = STATIC_DIR / name
        if not path.exists():
            self._json(500, {"ok": False, "error": "editor assets are missing: " + name})
            return
        self._send(200, path.read_bytes(), "text/html; charset=utf-8")

    # --------------------------------------------------------------------- HTTP
    def do_GET(self) -> None:  # noqa: N802 - required by http.server
        if not self._guard():
            return
        path = self.path.split("?", 1)[0]
        view = getattr(self.server, "view", "nodes")

        if path in ("/", "/index.html"):
            self._page(VIEWS.get(view, VIEWS["nodes"]))
            return
        if path == "/nodes":
            self._page(VIEWS["nodes"])
            return
        if path == "/blocks":
            self._page(VIEWS["blocks"])
            return
        if path == "/text":
            self._page(VIEWS["text"])
            return
        if path == "/api/files":
            kind = _query(self.path, "kind", "bots")
            try:
                self._json(200, {"ok": True, "files": _list_projects(kind)})
            except ValueError as error:
                self._json(400, {"ok": False, "error": str(error)})
            return
        if path in ("/api/project", "/api/file"):
            name = _query(self.path, "name", "")
            try:
                project = _read_project(name)
            except ValueError as error:
                self._json(400, {"ok": False, "error": str(error)})
                return
            self._json(200, {"ok": True, "name": name, "data": project,
                             "rev": project["rev"], "text": project["text"],
                             "layout": project["layout"], "draft": project.get("draft")})
            return
        if path == "/api/rev":
            name = _query(self.path, "name", "")
            try:
                self._json(200, {"ok": True, "rev": _read_project(name)["rev"]})
            except ValueError as error:
                self._json(400, {"ok": False, "error": str(error)})
            return
        if path == "/api/logs":
            query = self.path.split("?", 1)[1] if "?" in self.path else ""
            since = 0
            for chunk in query.split("&"):
                if chunk.startswith("since="):
                    try:
                        since = int(chunk[6:])
                    except ValueError:
                        since = 0
            self._json(200, RUNNER.snapshot(since))
            return
        if path == "/api/health":
            self._json(200, {"ok": True, "version": __version__, "view": view})
            return
        if path == "/api/schema":
            # The catalogue of everything a bot can do: the editors build their
            # palettes and property fields from this, so a new aiogram feature
            # appears in all three without touching their code. `?lang=en` gives
            # the same catalogue with English labels.
            self._json(200, feature_schema(_query(self.path, "lang", "ru")))
            return

        candidate = (STATIC_DIR / path.lstrip("/")).resolve()
        if candidate.is_file() and STATIC_DIR in candidate.parents:
            guess = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
            self._send(200, candidate.read_bytes(), guess)
            return

        self._json(404, {"ok": False, "error": "not found"})

    def do_POST(self) -> None:  # noqa: N802 - required by http.server
        if not self._guard():
            return
        path = self.path.split("?", 1)[0]
        if path not in ("/api/compile", "/api/compile_text", "/api/run", "/api/stop",
                        "/api/file", "/api/project", "/api/project_layout",
                        "/api/to_text", "/api/to_nodes", "/api/to_blocks",
                        "/api/nodes_to_text"):
            self._json(404, {"ok": False, "error": "not found"})
            return

        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            self._json(413, {"ok": False, "error": "request body is too large"})
            return
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        self._body_read = True
        # A cross-site <form> or no-cors fetch cannot set this header, so a
        # request with a body must be JSON or it is not from our own page.
        # The body is read first: closing the socket on a client that is still
        # writing its payload produces a connection reset instead of an answer.
        if length and not (self.headers.get("Content-Type") or "").strip().lower().startswith(
            JSON_TYPE
        ):
            self._reject(415, "POST bodies must be application/json")
            return
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self._json(400, {"ok": False, "error": "invalid JSON body"})
            return

        if path in ("/api/project", "/api/file"):
            name = _query(self.path, "name", "")
            incoming = data if isinstance(data, dict) else {}
            if not isinstance(incoming.get("text"), str) and not isinstance(
                incoming.get("nodes"), dict
            ):
                self._json(400, {"ok": False, "error": "nothing to save"})
                return
            try:
                result = _save_project(name, incoming)
            except ValueError as error:
                self._json(400, {"ok": False, "error": str(error)})
                return
            if not result.get("ok"):
                # a conflict or a syntax error: the editor shows it and reloads
                self._json(200, result)
                return
            self._json(200, {"ok": True, "name": name, "rev": result["rev"],
                             "text": result["text"],
                             "changed": result.get("changed", True),
                             "incomplete": result.get("incomplete", False)})
            return
        if path == "/api/project_layout":
            # Canvas positions only: saved without touching the revision, so the
            # other views are not reloaded just because a block was dragged.
            name = _query(self.path, "name", "")
            layout = data.get("layout") if isinstance(data, dict) else None
            if not isinstance(layout, dict):
                self._json(400, {"ok": False, "error": "bad layout"})
                return
            try:
                with PROJECT_LOCK:
                    project = _read_project(name)
                    project["layout"] = layout
                    _write_project(name, project)
            except ValueError as error:
                self._json(400, {"ok": False, "error": str(error)})
                return
            self._json(200, {"ok": True, "rev": project["rev"]})
            return

        if path == "/api/run":
            code = data.get("code", "")
            if not isinstance(code, str) or not code.strip():
                self._json(400, {"ok": False, "error": "no generated code yet"})
                return
            token = data.get("token", "")
            pid = RUNNER.start(code, str(token) if token else "")
            self._json(200, {"ok": True, "pid": pid})
            return
        if path == "/api/stop":
            RUNNER.stop()
            self._json(200, {"ok": True})
            return

        if path in ("/api/to_text", "/api/to_nodes", "/api/to_blocks", "/api/nodes_to_text"):
            self._convert(path, data)
            return

        if path == "/api/compile_text":
            self._compile_text(data)
            return

        dsl = data.get("dsl", "")
        board = data.get("nodes")
        blocks = data.get("xml")
        if isinstance(board, dict):
            # The node editor sends its canvas: one converter in Python produces
            # the shared text and the code together, so the two cannot disagree.
            self._compile_board(board)
            return
        if isinstance(blocks, str) and blocks.strip():
            # The block editor sends the Blockly workspace in the same format
            # Blockly itself uses for saving.
            self._compile_blocks(blocks)
            return
        if not isinstance(dsl, str) or not dsl.strip():
            # A page that asks for code without naming any source is a page from
            # an older tgblocks: say what to do instead of an internal message.
            self._json(400, {
                "ok": False,
                "error": "the request brought no source: reload the editor page "
                         "(Ctrl+F5) - it is probably a page from an older tgblocks",
            })
            return

        try:
            spec = parse(dsl, "editor.tg")
            code = generate(spec)
        except DSLParseError as error:
            self._json(
                200,
                {
                    "ok": False,
                    "error": error.message,
                    "line": error.line,
                    "column": error.column,
                    "detail": error.render("editor.tg"),
                    "dsl": dsl,
                },
            )
            return

        self._json(200, {"ok": True, "dsl": dsl, "code": code,
                         "warnings": list(spec.warnings),
                         "has_token": _has_real_token(spec)})

    def _compile_board(self, board: dict) -> None:
        # Board -> text -> code, in one answer for the node editor.
        try:
            spec = board_to_spec(board)
            if not spec.handlers:
                self._json(200, {
                    "ok": False,
                    "error": "в доске нет ни одного события",
                    "detail": "Добавь блок «Событие» и соедини его с «Бот».",
                })
                return
            validate(spec)
            text = spec_to_text(spec)
            code = generate(spec)
        except DSLParseError as error:
            self._json(200, {"ok": False, "error": error.message,
                             "detail": error.render("editor.tg"),
                             "line": error.line, "column": error.column})
            return
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            # The canvas can hold anything the browser produced: answer with a
            # message instead of dropping the connection.
            print("tgblocks: cannot compile the board: {0!r}".format(error))
            self._json(200, {"ok": False, "error": "не удалось собрать блоки",
                             "detail": str(error)})
            return
        self._json(200, {"ok": True, "text": text, "dsl": text, "code": code,
                         "warnings": list(spec.warnings),
                         "has_token": _has_real_token(spec)})

    def _compile_blocks(self, xml: str) -> None:
        # Blockly workspace -> text -> code, for the block editor.
        try:
            spec = blocks_xml_to_spec(xml)
            if not spec.handlers:
                self._json(200, {
                    "ok": False,
                    "error": "в блоке «бот» нет ни одного события",
                    "detail": "Перетащи блок «событие» внутрь блока «токен».",
                })
                return
            validate(spec)
            text = spec_to_text(spec)
            code = generate(spec)
        except DSLParseError as error:
            self._json(200, {"ok": False, "error": error.message,
                             "detail": error.render("editor.tg")})
            return
        except (ValueError, KeyError, TypeError, AttributeError) as error:
            self._json(200, {"ok": False, "error": "не удалось прочитать блоки",
                             "detail": str(error)})
            return
        self._json(200, {"ok": True, "text": text, "dsl": text, "code": code,
                         "warnings": list(spec.warnings),
                         "has_token": _has_real_token(spec)})

    def _convert(self, path: str, data) -> None:
        # Move work between the three editors through the shared text syntax.
        try:
            if path == "/api/nodes_to_text":
                board = data.get("nodes", {})
                if not isinstance(board, dict):
                    self._json(400, {"ok": False, "error": "bad board"})
                    return
                self._json(200, {"ok": True, "text": board_to_text(board)})
                return

            if path == "/api/to_text":
                dsl = data.get("dsl", "")
                if not isinstance(dsl, str) or not dsl.strip():
                    self._json(400, {"ok": False, "error": "the DSL source is empty"})
                    return
                self._json(200, {"ok": True, "text": spec_to_text(parse(dsl, "editor.tg"))})
                return

            source = data.get("source", "")
            if not isinstance(source, str) or not source.strip():
                self._json(400, {"ok": False, "error": "the source is empty"})
                return
            spec = parse_text(source, "editor.txt")
            if path == "/api/to_nodes":
                # Reuse the saved canvas positions so opening the board does not
                # scatter the blocks the user placed by hand.
                layout = {}
                name = data.get("name")
                if isinstance(name, str) and name:
                    try:
                        layout = _read_project(name)["layout"]
                    except ValueError:
                        layout = {}
                self._json(200, {"ok": True, "nodes": spec_to_nodes(spec, layout)})
                return
            self._json(200, {"ok": True, "xml": spec_to_blocks_xml(spec)})
        except DSLParseError as error:
            self._json(
                200,
                {
                    "ok": False,
                    "error": error.message,
                    "line": error.line,
                    "column": error.column,
                    "detail": error.render("editor.txt"),
                },
            )
        except ValueError as error:
            self._json(200, {"ok": False, "error": str(error)})

    def _compile_text(self, data) -> None:
        # The text editor sends the Python-looking syntax, not the DSL.
        source = data.get("source", "")
        if not isinstance(source, str) or not source.strip():
            self._json(400, {"ok": False, "error": "the source is empty"})
            return

        try:
            spec = parse_text(source, "editor.txt")
            code = generate(spec)
        except DSLParseError as error:
            self._json(
                200,
                {
                    "ok": False,
                    "error": error.message,
                    "line": error.line,
                    "column": error.column,
                    "detail": error.render("editor.txt"),
                },
            )
            return
        self._json(200, {"ok": True, "code": code, "warnings": list(spec.warnings),
                         "has_token": _has_real_token(spec)})


class _Server(ThreadingHTTPServer):
    # On Windows the default (SO_REUSEADDR) lets a second server bind the same
    # port, so an old instance keeps answering and new code silently never runs.
    allow_reuse_address = False


def _address(host: str, port: int) -> str:
    # The one address a person should type. A wildcard bind is still reached at
    # 127.0.0.1 from the same machine.
    name = "127.0.0.1" if host in ("", "0.0.0.0", "::", "[::]") else host
    if ":" in name and not name.startswith("["):
        name = "[" + name + "]"
    return "http://{0}:{1}/".format(name, port)


def _existing_editor(host: str, port: int):
    # The version of the tgblocks already answering on that port, or None when
    # the port is free or held by an unrelated program.
    url = _address(host, port) + "api/health"
    try:
        with urlopen(url, timeout=1.5) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict) or data.get("ok") is not True:
        return None
    version = data.get("version")
    return version if isinstance(version, str) else "?"


def _find_free_port(host: str, start: int, tries: int = 20):
    # The next port that can be bound, so `tgblocks` always ends with an editor.
    for candidate in range(start, start + tries):
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            probe.bind((host if host not in ("", "0.0.0.0") else "127.0.0.1", candidate))
        except OSError:
            continue
        finally:
            probe.close()
        return candidate
    return None


def serve(
    host: str = "127.0.0.1",
    port: int = 8765,
    open_browser: bool = True,
    view: str = "nodes",
    allow_remote: bool = False,
) -> None:
    # Run the editor until Ctrl+C.
    if view not in VIEWS:
        raise SystemExit(
            "error: unknown view {0!r}; use nodes, blocks or text".format(view)
        )
    if host not in LOOPBACK_NAMES and not allow_remote:
        raise SystemExit(
            "error: --host {0} would expose the editor (it can run generated code) "
            "to the network.\n"
            "       Keep the default 127.0.0.1, or add --allow-remote if you really "
            "mean it.".format(host)
        )
    for name in VIEWS.values():
        if not (STATIC_DIR / name).exists():
            raise SystemExit("error: editor assets are missing: {0}".format(name))

    try:
        migrate_legacy_files()
    except OSError as error:
        print("warning: could not migrate old projects: {0}".format(error))

    try:
        httpd = _Server((host, port), _Handler)
    except OSError as error:
        # The usual reason is not a broken port: it is a second `tgblocks` while
        # the first one is still open.
        address = _address(host, port)
        running = _existing_editor(host, port)
        if running == __version__:
            # Same build: there is nothing to start, the editor is already there.
            print("tgblocks is already running: {0}".format(address), flush=True)
            print(
                "  open it in the browser"
                if not open_browser
                else "  opening it - same editor, same document.",
                flush=True,
            )
            print("  Ctrl+C in that window stops it.", flush=True)
            if open_browser:
                webbrowser.open(address)
            return
        if running:
            note = ("port {0} is used by an old tgblocks {1} - press Ctrl+C in that "
                    "window to get the default port back").format(port, running)
        else:
            note = "port {0} is taken by another program ({1})".format(
                port, error.strerror or error)
        spare = _find_free_port(host, port + 1)
        if spare is None:
            raise SystemExit(
                "error: {0}, and no free port above it.\n"
                "       Stop what holds the port, then run tgblocks again.\n"
                "       Or pick one yourself: tgblocks --port <number>".format(note)
            )
        print("note: {0}.".format(note), flush=True)
        print("      starting on {0} instead.".format(spare), flush=True)
        port = spare
        httpd = _Server((host, port), _Handler)
    httpd.view = view

    address = _address(host, port)
    print("tgblocks: {0}".format(address), flush=True)
    print("  views: /nodes | /text | /blocks    (Ctrl+C to stop)", flush=True)

    if open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(address)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped", flush=True)
    finally:
        httpd.server_close()
