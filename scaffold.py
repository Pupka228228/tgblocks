#!/usr/bin/env python3
"""scaffold.py - generate the "tgblocks" project (DSL + visual block builder for Telegram bots).

Usage:
    python scaffold.py            # create the project in ./tgblocks
    python scaffold.py myfolder   # create the project in ./myfolder

The generated project is a ready-to-install Python package:
    cd tgblocks && pip install -e ".[dev]"
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

# BEGIN GENERATED FILE PAYLOAD (python tools/build_scaffold.py)
FILES: Dict[str, str] = {
    ".gitattributes": r"""# normalize line endings: the repo is text, LF everywhere, CRLF only for .bat/.cmd
* text=auto eol=lf
*.bat text eol=crlf
*.cmd text eol=crlf
*.png binary
*.jpg binary
""",
    ".gitignore": r"""__pycache__/
*.py[cod]
*.egg-info/
build/
dist/
.venv/
venv/
.pytest_cache/
.mypy_cache/
.ruff_cache/
.coverage
# generated bots
bot.py
!examples/*.py
.idea/
.vscode/
.DS_Store
""",
    "LICENSE": r"""MIT License

Copyright (c) 2025 tgblocks contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""",
    "README.md": r"""# tgblocks

**A tiny text DSL and three visual editors for Telegram bots on aiogram 3.**

Five lines of text - or five dragged blocks - and you get ordinary, editable aiogram
code. No account, no cloud, no lock-in: the editor is a local server on
127.0.0.1, and the result is a normal bot.py you can read, commit and deploy.

[![CI](https://github.com/Pupka228228/tgblocks/actions/workflows/ci.yml/badge.svg)](https://github.com/Pupka228228/tgblocks/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

![tgblocks in action](https://raw.githubusercontent.com/Pupka228228/tgblocks/main/docs/demo.gif)

## Install

```bash
pip install "tgblocks[runtime]"     # runtime adds aiogram: ready to run bots
tgblocks                            # opens the editor at http://127.0.0.1:8765/
```

Without the extra: `pip install tgblocks` installs the compiler and the editors only,
which is enough to generate and read code. To follow the newest commit instead of the
release:

```bash
pip install "tgblocks[runtime] @ git+https://github.com/Pupka228228/tgblocks.git"
```

From a clone, for development:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev,runtime]"
```

### Run without installing globally (pipx)

If you don't want to install `tgblocks` into your main Python environment, use `pipx` but first, install the dependencies:
```bash
python -m pip install --user pipx
python -m pipx ensurepath
```
Then restart the command prompt and enter:
```bash
pipx run --spec "tgblocks[runtime]" tgblocks
```

## Three views, one compiler

### `/nodes` - boxes and wires

![nodes](https://raw.githubusercontent.com/Pupka228228/tgblocks/main/docs/editor-nodes.png)

Blocks come from the palette on the left, and they do not connect by themselves: drag
from a dot to the block you want, and `✕` in the middle of a wire removes it. Drag the
background to pan, wheel to zoom, `Ctrl+Z` and `Ctrl+Y` undo and redo.

### `/blocks` - Blockly

![blocks](https://raw.githubusercontent.com/Pupka228228/tgblocks/main/docs/editor-blocks.png)

The same bot with blocks generated from the same catalogue. Blockly ships inside the
package, so this view works without internet.

### `/text` - the code, with help

![text](https://raw.githubusercontent.com/Pupka228228/tgblocks/main/docs/editor-text.png)

Syntax highlighting, auto-indent, and an **Insert…** palette that puts any call the
compiler knows at the cursor.

All three are one document. A change in any view shows up in the other two within a
second, and clearing one clears the bot everywhere. The ⚙ panel in the header switches
the theme and the interface language - English by default, Russian at one click, and the
block names, field captions and hints change with it.

## Why

Paid bot constructors keep your bot inside their panel: you rent the hosting, you cannot
read the code, and leaving means starting again. Writing aiogram 3 by hand is the
opposite - full control, but the first hour is dispatcher, routers, filters, keyboards,
callbacks and an async entrypoint before anything answers.

tgblocks is the middle: a language small enough to fit on a postcard, or an editor where
a bot is boxes with wires. Both produce the same readable aiogram code, and the code is
yours.

## Quick start

`bot.tg`:

```
bot token "123456:ABC"
bot name "Hello bot"

on /start:
    send "Hi! I am your bot."
    buttons:
        "Help" -> /help
        "Site" -> url "https://example.com"

on /help:
    send "Commands: /start, /help"

on message:
    when text contains "hi":
        send "Hello there!"
    else:
        send "Not sure what you mean. Try /help."
```

```bash
tgblocks check bot.tg              # parse, a one-line summary and warnings
tgblocks compile bot.tg -o bot.py  # aiogram 3 code
tgblocks run bot.tg --dry-run      # print the code, start nothing
TG_BOT_TOKEN=123456:ABC python bot.py
```

One command is enough to work: `tgblocks` opens the editor, `tgblocks bot.tg` starts
that bot, and both work from any folder once the package is installed.

The token is **not** written into `bot.py` unless you ask for it (`--embed-token`):
generated code reads `TG_BOT_TOKEN` at startup, so the file is safe to commit.
`tgblocks run` passes the token from the file or from `--token` through the
environment.

## Editor commands

```bash
tgblocks                        # http://127.0.0.1:8765/  -> boxes and wires
tgblocks --view text            # / -> text editor
tgblocks --view blocks          # / -> Blockly
tgblocks --port 9000            # another port (flags work without the subcommand)
```

Every editor has **Run** / **Stop** and a **Logs** tab: the generated bot runs as a
separate process and its output streams into the page. Each editor can download the
`.tg` text and the `.py` code.

Starting `tgblocks` again while the editor is open does not fail on a busy port: if it
is the same version it just opens the editor that runs, and if the port is held by an
old window (or another program) it starts on the next free port and prints that one
address.

### The catalogue is the source of truth

Everything a bot can do is described once, in `src/tgblocks/model.py`: an action, its
parameters, its labels, the aiogram method it lands on. The DSL parser, the text
parser, the converters (text ⇄ node board ⇄ Blockly XML) and the code generator all
read that one table, and `/api/schema` hands it to the three pages, so their palettes
and property fields are generated too. Adding an aiogram method is a catalogue entry
plus one emitter - not five copies that drift apart.

## What a bot can do

```text
Messages     send  edit_text  delete  answer_callback  pin  unpin

Media        send_photo  send_document  send_video  send_animation  send_audio
             send_voice  send_sticker  send_location  send_contact  send_poll
             send_dice

Keyboard     inline buttons: -> /command, -> url "…", -> web_app "…"
             reply keyboards, -> contact, -> location

Logic        when text == / != / contains / startswith / endswith
             several values at once, else

Dialogues    state order, set_state order, clear_state, on state order:

Moderation   ban_user, unban_user, mute_user

Service      typing, delay 2, log "…", pass
```

### Events

```text
Commands     on /start:

Messages     on message:            on message "a", "b":
             on photo:              on sticker:            on voice:
             on video:              on video_note:         on audio:
             on document:           on animation:          on location:
             on contact:            on poll:               on dice:
             on new_members:        on left_member:        on pinned:
             on web_app_data:

Other        on edited:             on any:               on callback:
             on callback "/data":   on inline_query:      on chat_member:
             on my_chat_member:     on poll_answer:       on channel_post:

Filters      on message chat=supergroup:
             on message from_user=123:
             on message regex="^[0-9]+$":
```

Webhook mode is a directive, not a rewrite: `bot webhook "https://example.com/hook"`
makes the generated bot serve the update endpoint instead of polling, and it still
falls back to polling when `TG_WEBHOOK_URL` is empty.

Full step-by-step reference in Russian: **[ИНСТРУКЦИЯ.md](INSTRUCTIONS.md)**.
A bot that uses everything: **[examples/full.tg](examples/full.tg)**.

## Errors with line numbers

```
bot.tg:7:5: error: expected a quoted text
   7 |     send Hello!
     |         ^
  hint: wrap the value in double quotes, for example: "Hello!"
```

Two handlers that claim the same messages are refused at parse time: aiogram calls
only the first one, so the second would silently never run. A button that calls a
command nobody handles is a warning, not an error - the bot still builds.

## Telegram is blocked? Use a proxy

```
bot token "123456:ABC"
bot proxy "socks5://127.0.0.1:1080"
```

`socks5://`, `socks4://`, `http://` and `https://` work; socks needs `aiohttp-socks`
(in the `runtime` extra). The value can also come from `TG_PROXY`. When the connection
fails, the generated bot prints a short explanation instead of a full aiohttp
traceback.

Paste only the URL into the bot's `proxy` field - not the whole record from a proxy
list. To check that a proxy actually reaches Telegram before running a bot:

```bash
tgblocks proxy socks5://host:port
```

It performs the same steps the bot will (SOCKS5/HTTP CONNECT → TLS → `api.telegram.org`)
and prints the ready-to-paste lines for all three editors when the proxy works.

## Security model

The editor is a local tool that can start processes, so the server treats the browser
as a potential attacker:

- it answers only on `127.0.0.1`, and only to a `Host` header that is one of its own
  (a hostile domain pointing at 127.0.0.1 is refused);
- cross-site requests are refused by `Origin` and `Sec-Fetch-Site` checks, and a POST
  body must be `application/json` - the two ways a foreign page could otherwise drive
  it;
- running a preview is a child process by design, so `--host` needs `--allow-remote`
  before that is exposed to the network.

Secrets stay out of artefacts: `compile` writes code without the token unless you pass
`--embed-token`.

## Python API

- `from tgblocks import compile_source, compile_text` - DSL text or editor text to
  aiogram code.
- `from tgblocks import parse, generate` - AST in, code out.
- `from tgblocks import run` - a DSL string inside a normal `.py` file.
- `tgblocks.dsl.parser.DSLParseError` carries `line`, `column`, `message` and `hint`.

## Project layout

```
src/tgblocks/
    model.py             the catalogue: every action and event, once
    dsl/parser.py        DSL text -> AST, with line/column errors
    dsl/codegen.py       AST -> readable aiogram 3 code
    textlang.py          the Python-looking syntax -> the same AST
    convert.py           AST <-> text, <-> node board, <-> Blockly XML
    cli.py               check / compile / run / proxy / visual
    runner.py            compile and execute a bot from DSL text
    visual/server.py     the local editor server (API + same-origin guards)
    visual/static/       nodes.html, blocks.html, text.html, shared project store
                         plus vendor/blockly.js, which ships with the package
tests/                   the suite: golden code, fake Telegram, editors, security
examples/                hello.tg, full.tg, features.txt
tools/                   build_scaffold.py, check_javascript.py, qa_smoke.py
docs/                    screenshots and the demo GIF used by this README
scaffold.py              a single-file generator of this project
```

## Tests

```bash
python -m pytest -q          # 261 tests
```

The suite runs the generated bots on a fake Telegram, so a broken `/start` fails a
test instead of failing in production:

- `tests/test_golden.py` - pins the generated code for a corpus of bots and imports
  every sample into the real aiogram package;
- `tests/test_bots.py`, `tests/test_features.py`, `tests/test_examples.py` - feed real
  updates through a real `Dispatcher` and assert the API calls a user would cause;
- `tests/test_sync.py`, `tests/test_ui.py` - the editors: one document for three
  views, the schema, and both "compile this canvas" paths;
- `tests/test_security.py` - the CSRF, rebinding and wide-bind refusals;
- `tests/test_scaffold.py` - `scaffold.py` cannot drift from the tree again.

Beyond pytest:

```bash
python tools/build_scaffold.py --check   # the single-file generator is fresh
python tools/check_javascript.py         # editor JS parses and defines its helpers
python tools/qa_smoke.py                 # endpoints plus the editor-to-editor hand-off
```

## Limitations (on purpose)

- No payments, no scenes, no arbitrary callback payloads: buttons carry a command.
- One handler per filter: several `on message:` blocks are refused, branch with `when`.
- The editors do not turn hand-written Python back into blocks: the DSL text is the
  source of truth once you leave the browser.
- `scaffold.py` carries a copy of the project; `tools/build_scaffold.py` regenerates it
  and `tests/test_scaffold.py` fails if it went stale.

## License

MIT - see [LICENSE](LICENSE).

## Support the project

If you find `tgblocks` useful, you can buy me a coffee to support further development. This is a voluntary donation, not a payment for software.

[![DonationAlerts](https://img.shields.io/badge/Donate-DonationAlerts-blue?style=flat)](https://www.donationalerts.com/r/Coder_x)

## Русский

`tgblocks` - маленький язык и три редактора для Telegram-ботов на aiogram 3. Написал
пять строк (или собрал блоки мышкой) - получил обычный `bot.py`, который можно читать,
править и выкладывать.

```bash
pip install "tgblocks[runtime]"       # пакет и aiogram, чтобы запускать ботов
tgblocks                              # редактор в браузере, 127.0.0.1:8765
tgblocks check examples/full.tg       # проверить бота
tgblocks run examples/full.tg         # запустить бота из DSL
tgblocks compile examples/hello.tg -o mybot.py
```

Всё работает на твоём компьютере: никаких аккаунтов, облака и подписок. Три вида
(узлы, текст, блоки) - это один и тот же бот, поэтому правка в одном виде сразу видна
в двух других. В шапке есть кнопка настроек: тёмная или светлая тема и русский или
английский интерфейс. Токен в сгенерированный файл не пишется, если не попросить
`--embed-token`.

Пакет уже лежит на PyPI, поэтому ставится одной строкой - файлы никто не скачивает:

```bash
pip install "tgblocks[runtime]"
```

Если нужен самый свежий коммит, а не релиз:

```bash
pip install "tgblocks[runtime] @ git+https://github.com/Pupka228228/tgblocks.git"
```

Подробно по шагам, с разбором ошибок: **[ИНСТРУКЦИЯ.md](ИНСТРУКЦИЯ.md)**.
""",
    "examples/features.txt": r"""token("1:x")

on.command("/start"):
    send("Привет")
    typing()
    delay(1)
    send_photo("https://example.com/cat.jpg", "кот")

on.video_note():
    delete()

on.new_members():
    send("Добро пожаловать")

on.edited():
    send("Ты изменил сообщение")
""",
    "examples/full.tg": r"""# Всё, что умеет tgblocks, в одном боте.
# Запуск:  tgblocks run examples/full.tg --token 123456:ABC
# Проверка: tgblocks check examples/full.tg

bot token "PASTE_YOUR_TOKEN"
bot name "tgblocks full"
# bot proxy "socks5://127.0.0.1:1080"
# bot webhook "https://example.com/hook"
# bot webhook_path "/hook"
# bot webhook_secret "секрет"

# шаги диалога заказа
state order
state phone

# ---------------------------------------------------------------- команды
on /start:
    send "Привет! Выбери, что показать, или сделай заказ."
    buttons:
        "Меню" -> /menu
        "Заказ" -> /order
        "Сайт" -> url "https://example.com"

on /menu:
    send "Вот что я умею:"
    buttons reply:
        "/start"
        "/order"

# ------------------------------------------------------------------ заказ
on /order:
    send "Что заказать?"
    set_state order

on state order:
    send "Записал. Теперь телефон?"
    set_state phone

on state phone:
    send "Готово! Заказ принят."
    clear_state

on /cancel:
    clear_state
    send "Отменил."

# ------------------------------------------------------------------ медиа
on /photo:
    send_photo "https://picsum.photos/600/400" "Случайная картинка"

on /doc:
    send_document "https://example.com/file.pdf" "Инструкция"

on /poll:
    send_poll "Чай или кофе?" "Чай" "Кофе" "Воду"

on /where:
    send_location 55.75 37.61

on /phone:
    send_contact "+10000000000" "Поддержка"

# ------------------------------------------------------- кнопки и ответы
on /confirm:
    send "Уверен?"
    buttons:
        "Да" -> /confirmed
        "Нет" -> /cancelled

on /confirmed:
    edit_text "Готово: подтверждено."
    answer_callback "Записал!"

on /cancelled:
    edit_text "Ок, отменил."

# ----------------------------------------------------------------- фильтры
on message chat=supergroup:
    when text contains "спам":
        delete
        ban_user
    else:
        send "В группе пишем по делу."

on message from_user=0 regex="^[0-9]+$":
    send "Это число: понял."

on callback "/buy":
    send "Покупаем!"
    answer_callback "Перехожу к оплате" alert

# ------------------------------------------------------------- сервисное
on /log:
    log "кто-то нажал /log"
    send "Записал в лог"

on photo:
    send "Хорошее фото."

on sticker:
    send "Стикер принят."

on any:
    when text contains "привет":
        send "И тебе привет!"
    else:
        send "Напиши /menu, /order или /help."
""",
    "examples/hello.tg": r"""# A tiny Telegram bot written in the tgblocks DSL.
# Replace the token (or export TG_BOT_TOKEN) and run:
#     tgblocks run examples/hello.tg

bot token "PASTE_YOUR_TOKEN"
bot name "tgblocks hello"

on /start:
    send "Привет! Я бот на tgblocks."
    buttons:
        "Помощь" -> /help
        "О боте" -> /about

on /help:
    send "Команды: /start, /help, /about"
    buttons reply:
        "/start"

on /about:
    send "Собрано из DSL и блоков. Код — обычный aiogram 3."

on message:
    when text contains "привет":
        send "И тебе привет!"
    else:
        send "Не понял. Напиши /help."

on photo:
    send "Хорошее фото! А теперь напиши /help."

on sticker:
    send "Стикер принят."

on any:
    send "Я понимаю только текст и фото."
""",
    "pyproject.toml": r"""[build-system]
requires = ["hatchling>=1.18"]
build-backend = "hatchling.build"

[project]
name = "tgblocks"
version = "0.2.9"
description = "Visual editor for building Telegram bots on aiogram 3"
readme = "README.md"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "tgblocks contributors" }]
keywords = ["telegram", "bot", "dsl", "blockly", "aiogram", "low-code", "codegen"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Environment :: Console",
    "Operating System :: OS Independent",
    "Framework :: AsyncIO",
    "Topic :: Communications :: Chat",
    "Topic :: Software Development :: Code Generators",
    "Topic :: Software Development :: User Interfaces",
]
dependencies = []

[project.optional-dependencies]
# aiogram is only needed to actually poll Telegram, not to compile a bot.
runtime = ["aiogram>=3.4,<4", "aiohttp-socks>=0.8"]
dev = ["pytest>=7", "build>=1"]

[project.scripts]
tgblocks = "tgblocks.cli:main"

[project.urls]
Homepage = "https://github.com/Pupka228228/tgblocks"
Repository = "https://github.com/Pupka228228/tgblocks"
Issues = "https://github.com/Pupka228228/tgblocks/issues"

[tool.hatch.build.targets.wheel]
packages = ["src/tgblocks"]

[tool.hatch.build.targets.sdist]
include = ["src", "examples", "tests", "README.md", "LICENSE", "pyproject.toml",
           "CHANGELOG.md", "ИНСТРУКЦИЯ.md"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
""",
    "src/tgblocks/__init__.py": r"""# tgblocks: a tiny DSL, a text syntax and a visual editor for Telegram bots.
#
# The package is a compiler: .tg DSL or the editor syntax -> aiogram 3 code.
#
#     from tgblocks import parse, generate
#     code = generate(parse(open("bot.tg").read()))
#
#     from tgblocks.textlang import compile_text
#     code = compile_text(open("bot.txt").read())

from .dsl.codegen import generate
from .dsl.parser import BotSpec, DSLParseError, parse, parse_file
from .textlang import compile_text, parse_text

__version__ = "0.2.0"

__all__ = [
    "__version__",
    "BotSpec",
    "DSLParseError",
    "compile_text",
    "generate",
    "parse",
    "parse_file",
    "parse_text",
]
""",
    "src/tgblocks/__main__.py": r"""# Allows `python -m tgblocks run examples/hello.tg`.

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
""",
    "src/tgblocks/cli.py": r"""# Command line interface: run, compile, check and the visual editor.

from __future__ import annotations

import argparse
import os
import runpy
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

from . import __version__
from .dsl.codegen import generate
from .dsl.parser import DSLParseError, parse_file
from .runner import missing_token_error, usable_token


def _print_warnings(bot, stream) -> None:
    for warning in getattr(bot, "warnings", ()):
        print("warning: {0}".format(warning), file=stream)


def _describe(handler) -> str:
    # One column that actually distinguishes two handlers of the same kind.
    if handler.kind == "command":
        return handler.command or "/"
    if handler.kind == "state":
        return "state[{0}]".format(handler.state)
    if handler.kind == "callback":
        return "callback[{0}]".format(handler.data) if handler.data else "callback"
    extras = []
    if handler.patterns:
        extras.append(", ".join(handler.patterns))
    if handler.chat:
        extras.append("chat=" + handler.chat)
    if handler.from_user:
        extras.append("from_user={0}".format(handler.from_user))
    if handler.regex:
        extras.append("regex=" + handler.regex)
    return "{0}[{1}]".format(handler.kind, "; ".join(extras)) if extras else handler.kind


def cmd_check(args: argparse.Namespace) -> int:
    bot = parse_file(args.file)
    events = [_describe(handler) for handler in bot.handlers]
    print(
        "OK {0}: handlers={1} - {2}".format(
            args.file, len(bot.handlers), ", ".join(events) or "none"
        )
    )
    _print_warnings(bot, sys.stderr)
    return 0


def cmd_compile(args: argparse.Namespace) -> int:
    bot = parse_file(args.file)
    code = generate(bot, embed_token=args.embed_token)
    _print_warnings(bot, sys.stderr)
    if args.output == "-":
        sys.stdout.write(code)
    else:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(code, encoding="utf-8")
        print("wrote {0} ({1} lines)".format(target, code.count("\n")))
    if not args.embed_token:
        print(
            "note: the token is not written into the file. "
            "Start the bot with TG_BOT_TOKEN=... or pass --embed-token.",
            file=sys.stderr,
        )
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    bot = parse_file(args.file)
    _print_warnings(bot, sys.stderr)

    if args.dry_run:
        # Inspection output must be safe to paste into a repository.
        sys.stdout.write(generate(bot, embed_token=False))
        return 0

    token = args.token or os.environ.get("TG_BOT_TOKEN") or usable_token(bot)
    error = missing_token_error(bot, token)
    if error:
        print("error: {0} (file: {1})".format(error, args.file), file=sys.stderr)
        return 2

    code = generate(bot, embed_token=False)

    try:
        import aiogram  # noqa: F401
    except ImportError:
        print(
            'error: aiogram is not installed. Run: pip install "tgblocks[runtime]"',
            file=sys.stderr,
        )
        return 2

    # Write the generated code to a temp file and execute it as __main__.
    with tempfile.TemporaryDirectory(prefix="tgblocks-") as folder:
        target = Path(folder) / "bot.py"
        target.write_text(code, encoding="utf-8")
        print("starting {0} (Ctrl+C to stop)".format(args.file))
        runpy.run_path(str(target), run_name="__main__")
    return 0


def cmd_proxy(args: argparse.Namespace) -> int:
    from .network import ProxyError, check_proxy, parse_proxy, proxy_hint

    proxies = list(args.proxies)
    if not proxies:
        from os import environ

        configured = environ.get("TG_PROXY", "").strip()
        if not configured:
            print(
                "error: no proxy given and TG_PROXY is not set.\n"
                "       Usage: tgblocks proxy socks5://host:port",
                file=sys.stderr,
            )
            return 2
        proxies = [configured]

    failed = 0
    for url in proxies:
        try:
            parse_proxy(url)
        except ProxyError as error:
            print("error: {0}: {1}".format(url, error), file=sys.stderr)
            failed += 1
            continue
        works, message, seconds = check_proxy(url, timeout=args.timeout)
        mark = "OK  " if works else "FAIL"
        print("{0} {1}  ({2:.1f} c)  {3}".format(mark, url, seconds, message))
        if works:
            for line in proxy_hint(url).splitlines():
                print("     {0}".format(line))
        else:
            failed += 1
    return 0 if not failed else 1


def cmd_visual(args: argparse.Namespace) -> int:
    from .visual.server import serve

    serve(
        host=args.host,
        port=args.port,
        open_browser=not args.no_browser,
        view=args.view,
        allow_remote=args.allow_remote,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tgblocks",
        description="A tiny text DSL and three visual editors for Telegram bots. "
        "Run `tgblocks` alone to open the editor, or `tgblocks bot.tg` to start a bot.",
        epilog="examples: tgblocks | tgblocks bot.tg | tgblocks compile bot.tg -o bot.py",
    )
    parser.add_argument(
        "--version", action="version", version="tgblocks {0}".format(__version__)
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    run_parser = subparsers.add_parser("run", help="compile a .tg file and start the bot")
    run_parser.add_argument("file", help="path to a .tg file")
    run_parser.add_argument("--token", help="bot token (overrides the DSL and the env)")
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the generated aiogram code instead of starting the bot",
    )
    run_parser.set_defaults(func=cmd_run)

    compile_parser = subparsers.add_parser(
        "compile", help="translate a .tg file into aiogram 3 Python code"
    )
    compile_parser.add_argument("file", help="path to a .tg file")
    compile_parser.add_argument(
        "-o", "--output", default="-", help="output file, or - for stdout (default)"
    )
    compile_parser.add_argument(
        "--embed-token",
        action="store_true",
        help="write the token from the .tg file into the output (off by default: "
        "generated bots read TG_BOT_TOKEN)",
    )
    compile_parser.set_defaults(func=cmd_compile)

    check_parser = subparsers.add_parser("check", help="validate a .tg file only")
    check_parser.add_argument("file", help="path to a .tg file")
    check_parser.set_defaults(func=cmd_check)

    proxy_parser = subparsers.add_parser(
        "proxy", help="check that a proxy can reach api.telegram.org"
    )
    proxy_parser.add_argument(
        "proxies", nargs="*",
        help="proxy URLs: socks5://host:port, socks4://, http://, https:// "
        "(default: TG_PROXY)",
    )
    proxy_parser.add_argument(
        "--timeout", type=float, default=8.0, help="seconds per proxy (default 8)"
    )
    proxy_parser.set_defaults(func=cmd_proxy)

    visual_parser = subparsers.add_parser(
        "visual", help="open the local visual editor in a browser"
    )
    visual_parser.add_argument("--host", default="127.0.0.1", help="bind address")
    visual_parser.add_argument("--port", type=int, default=8765, help="port (default 8765)")
    visual_parser.add_argument(
        "--view",
        choices=["nodes", "blocks", "text"],
        default="nodes",
        help="editor at / : nodes (boxes), blocks (Blockly) or text",
    )
    visual_parser.add_argument(
        "--no-browser", action="store_true", help="do not open a browser window"
    )
    visual_parser.add_argument(
        "--allow-remote",
        action="store_true",
        help="allow --host other than 127.0.0.1 (the editor can run generated code)",
    )
    visual_parser.set_defaults(func=cmd_visual)

    return parser


COMMANDS = {"run", "compile", "check", "visual"}


def _is_bot_file(argument: str) -> bool:
    # `tgblocks bot.tg` is shorthand for `tgblocks run bot.tg`: the command has to
    # work from any folder, without remembering a subcommand.
    if not argument or argument.startswith("-") or argument in COMMANDS:
        return False
    if argument.lower().endswith((".tg", ".txt", ".py")):
        return True
    return Path(argument).is_file()


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    # A redirected stdout on Windows uses the ANSI codepage; without this, any
    # character outside it (a Cyrillic bot name, for example) would raise
    # UnicodeEncodeError instead of printing.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):  # pragma: no cover - exotic streams
            pass
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments:
        # Bare `tgblocks`: the editor is what people mean, and it is also what
        # the README promises.
        arguments = ["visual"]
    elif _is_bot_file(arguments[0]):
        arguments = ["run"] + arguments
    elif arguments[0].startswith("-") and arguments[0] not in ("-h", "--help", "--version"):
        # `tgblocks --port 9000` is the same as `tgblocks visual --port 9000`:
        # the subcommand is optional, the flags are not second-class citizens.
        arguments = ["visual"] + arguments
    args = parser.parse_args(arguments)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    try:
        return args.func(args) or 0
    except DSLParseError as error:
        print(error.render(getattr(args, "file", "<dsl>")), file=sys.stderr)
        return 1
    except FileNotFoundError as error:
        print("error: {0}".format(error), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nstopped", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
""",
    "src/tgblocks/convert.py": '# Conversions between the three editor representations.\n#\n#   text syntax  <->  AST (BotSpec)  ->  nodes graph JSON\n#                                    ->  Blockly workspace XML\n#\n# The text syntax is the common interchange: the node editor can emit it from\n# its DSL, the Blockly editor can emit it from its generated DSL, and both can\n# be restored from it.\n#\n# Every action and event comes from tgblocks.model, so a new aiogram feature\n# travels through all three editors without touching this file.\n\nfrom __future__ import annotations\n\nimport json\nimport re\nimport xml.etree.ElementTree as ET\nfrom typing import Dict, List, Sequence\n\nfrom .dsl.parser import (\n    Action,\n    BotSpec,\n    Button,\n    Buttons,\n    Condition,\n    Handler,\n    When,\n)\nfrom .model import (\n    ACTIONS_BY_KIND,\n    ActionSpec,\n    EventSpec,\n    EVENTS_BY_KIND,\n    event_for,\n)\n\nINDENT = "    "\n\n# Node types that are older than the catalogue keep their historical names, so\n# projects saved by the previous version still open.\nNODE_ALIAS = {"send_photo": "photo"}\nNODE_ALIAS_BACK = {value: key for key, value in NODE_ALIAS.items()}\n\n# Text-syntax helpers: which node/action kind a Blockly event block carries.\nCONST_KINDS = {\n    "new_members": "NEW_MEMBERS",\n    "left_member": "LEFT_MEMBER",\n    "video_note": "VIDEO_NOTE",\n    "pinned": "PINNED",\n    "web_app_data": "WEB_APP_DATA",\n    "edited": "EDITED",\n    "dice": "DICE",\n}\n\n_STATE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")\n\n\ndef _q(value: str) -> str:\n    return json.dumps(str(value), ensure_ascii=False)\n\n\n# --------------------------------------------------------------------- text\ndef _render_argument(param, value) -> List[str]:\n    # One param -> the argument texts that reproduce it in the text syntax.\n    if param.kind == "values":\n        return [_q(item) for item in (value or ())]\n    if param.kind == "bool":\n        return [param.name + ("=True" if value else "=False")] if value else []\n    if value in (None, ""):\n        return []\n    if param.kind == "number":\n        return [str(value)]\n    if param.kind == "state":\n        return [str(value) if _STATE_RE.match(str(value)) else _q(value)]\n    return [_q(value)]\n\n\ndef _action_args(spec: ActionSpec, params: Dict[str, object]) -> List[str]:\n    args: List[str] = []\n    for param in spec.params:\n        args.extend(_render_argument(param, params.get(param.name, param.default)))\n    return args\n\n\ndef _buttons_text(buttons: Buttons, level: int, lines: List[str]) -> None:\n    pad = INDENT * level\n    lines.append(pad + "buttons(" + _q(buttons.style) + ")")\n    for item in buttons.items:\n        head = pad + "button(" + _q(item.label)\n        if item.kind == "url":\n            lines.append(head + ", url=" + _q(item.target or "") + ")")\n        elif item.kind == "web_app":\n            lines.append(head + ", web_app=" + _q(item.target or "") + ")")\n        elif item.kind == "contact":\n            lines.append(head + ", contact=True)")\n        elif item.kind == "location":\n            lines.append(head + ", location=True)")\n        elif item.kind == "command":\n            lines.append(head + ", " + _q(item.target or "") + ")")\n        else:\n            lines.append(head + ")")\n\n\ndef _actions_text(actions: Sequence[object], level: int, lines: List[str]) -> None:\n    pad = INDENT * level\n    index = 0\n    while index < len(actions):\n        node = actions[index]\n        if isinstance(node, Action) and node.kind == "send":\n            lines.append(pad + "send(" + _q(str(node.params.get("text", ""))) + ")")\n            following = actions[index + 1] if index + 1 < len(actions) else None\n            if isinstance(following, Buttons):\n                _buttons_text(following, level + 1, lines)\n                index += 2\n                continue\n            index += 1\n            continue\n        if isinstance(node, Buttons):\n            _buttons_text(node, level, lines)\n            index += 1\n            continue\n        if isinstance(node, When):\n            if node.condition.source == "dice":\n                lines.append(\n                    pad + \'when("dice", \' + _q(node.condition.op) + ", "\n                    + str(node.condition.value) + "):"\n                )\n            else:\n                extra = "".join("; " + _q(item) for item in (node.condition.values or ()))\n                lines.append(\n                    pad + "when(" + _q(node.condition.op) + ", "\n                    + _q(node.condition.value) + extra + "):"\n                )\n            _actions_text(node.then, level + 1, lines)\n            if node.orelse:\n                lines.append(pad + "otherwise():")\n                _actions_text(node.orelse, level + 1, lines)\n            index += 1\n            continue\n        if isinstance(node, Action):\n            spec = ACTIONS_BY_KIND.get(node.kind)\n            if spec is None:\n                raise ValueError("unknown action: {0!r}".format(node.kind))\n            if node.kind == "nothing":\n                lines.append(pad + "pass")\n            else:\n                lines.append(\n                    pad + node.kind + "(" + ", ".join(_action_args(spec, node.params)) + ")"\n                )\n            index += 1\n            continue\n        raise ValueError("unknown action: {0!r}".format(node))\n    if not actions:\n        lines.append(pad + "pass")\n\n\ndef _event_head(handler: Handler) -> str:\n    spec = EVENTS_BY_KIND.get(handler.kind)\n    if spec is None:\n        raise ValueError("unknown event: {0!r}".format(handler.kind))\n    extra: List[str] = []\n    if handler.chat:\n        extra.append("chat=" + _q(handler.chat))\n    if handler.from_user:\n        extra.append("from_user=" + str(handler.from_user))\n    if handler.regex:\n        extra.append("regex=" + _q(handler.regex))\n\n    if handler.kind == "command":\n        args = [_q(handler.command or "/start")] + extra\n        return "on.command(" + ", ".join(args) + "):"\n    if handler.kind == "text":\n        args = ["TEXT"] + [_q(item) for item in handler.patterns] + extra\n        return "on.message(" + ", ".join(args) + "):"\n    if handler.kind == "callback":\n        args = ([_q(handler.data)] if handler.data else []) + extra\n        return "on.callback(" + ", ".join(args) + "):"\n    if handler.kind == "state":\n        args = [handler.state] + extra\n        return "on.state(" + ", ".join(args) + "):"\n    args = extra\n    return "on." + handler.kind + "(" + ", ".join(args) + "):"\n\n\ndef spec_to_text(spec: BotSpec) -> str:\n    lines: List[str] = []\n    if spec.token:\n        lines.append("token(" + _q(spec.token) + ")")\n    if spec.name and spec.name != "tgblocks bot":\n        lines.append("name(" + _q(spec.name) + ")")\n    if spec.proxy:\n        lines.append("proxy(" + _q(spec.proxy) + ")")\n    if spec.webhook:\n        lines.append("webhook(" + _q(spec.webhook) + ")")\n        if spec.webhook_path and spec.webhook_path != "/webhook":\n            lines.append("webhook_path(" + _q(spec.webhook_path) + ")")\n        if spec.webhook_secret:\n            lines.append("webhook_secret(" + _q(spec.webhook_secret) + ")")\n    if lines:\n        lines.append("")\n    for state in spec.states:\n        lines.append("state(" + state + ")")\n    if spec.states:\n        lines.append("")\n    for handler in spec.handlers:\n        lines.append(_event_head(handler))\n        _actions_text(handler.actions, 1, lines)\n        lines.append("")\n    return "\\n".join(lines).rstrip() + "\\n"\n\n\n# -------------------------------------------------------------------- nodes\ndef _node_type(action_kind: str) -> str:\n    return NODE_ALIAS.get(action_kind, action_kind)\n\n\ndef _action_kind(node_type: str) -> str:\n    return NODE_ALIAS_BACK.get(node_type, node_type)\n\n\ndef spec_to_nodes(spec: BotSpec, layout: Dict[str, dict] = None) -> Dict[str, object]:\n    nodes: Dict[str, dict] = {}\n    counter = [0]\n\n    def new_id(prefix: str) -> str:\n        counter[0] += 1\n        return prefix + str(counter[0])\n\n    def make(kind: str, props: dict, x: float, y: float) -> str:\n        node_id = new_id(kind[:1])\n        nodes[node_id] = {\n            "id": node_id,\n            "type": kind,\n            "props": props,\n            "parent": None,\n            "children": [],\n            "x": x,\n            "y": y,\n        }\n        return node_id\n\n    def link(parent: str, child: str) -> None:\n        nodes[parent]["children"].append(child)\n        if nodes[child]["parent"] is None:\n            nodes[child]["parent"] = parent\n\n    bot_props = {\n        "token": spec.token or "",\n        "proxy": spec.proxy or "",\n        "name": "" if spec.name in ("", "tgblocks bot") else spec.name,\n    }\n    if spec.webhook:\n        bot_props["webhook"] = spec.webhook\n        bot_props["webhook_path"] = spec.webhook_path\n        bot_props["webhook_secret"] = spec.webhook_secret\n    bot_id = make("bot", bot_props, 60, 60)\n    y = 280\n    for handler in spec.handlers:\n        props = _handler_props(handler)\n        event_id = make("event", props, 60, y)\n        link(bot_id, event_id)\n        _actions_nodes(handler.actions, event_id, 60, y + 170, nodes, make, link)\n        y += 400\n\n    board = {"nodes": nodes, "counter": counter[0], "rootId": bot_id, "manual": True}\n    if layout:\n        # Keep the canvas where the user left it: only new blocks get fresh spots.\n        apply_layout(board, layout)\n    return board\n\n\ndef _handler_props(handler: Handler) -> dict:\n    kind = "message" if handler.kind == "text" else handler.kind\n    props: Dict[str, object] = {"kind": kind}\n    if handler.kind == "command":\n        props["command"] = handler.command or "/start"\n    if handler.patterns:\n        # Kept on the event: the editor shows this field only when it is set.\n        props["patterns"] = list(handler.patterns)\n    if handler.kind == "callback" and handler.data:\n        props["data"] = handler.data\n    if handler.kind == "state":\n        props["state"] = handler.state\n    if handler.chat:\n        props["chat"] = handler.chat\n    if handler.from_user:\n        props["from_user"] = handler.from_user\n    if handler.regex:\n        props["regex"] = handler.regex\n    return props\n\n\ndef _actions_nodes(actions, parent_id, x, y, nodes, make, link) -> None:\n    for node in actions:\n        if isinstance(node, Action):\n            node_type = _node_type(node.kind)\n            props = dict(node.params)\n            if node.kind == "nothing":\n                link(parent_id, make("nothing", {}, x, y))\n                y += 110\n                continue\n            action_id = make(node_type, props, x, y)\n            link(parent_id, action_id)\n            y += 150\n        elif isinstance(node, Buttons):\n            buttons_id = make("buttons", {"style": node.style}, x + 300, y - 150)\n            parent = nodes[parent_id]\n            send_children = [\n                child for child in parent["children"] if nodes[child]["type"] == "send"\n            ]\n            if send_children:\n                link(send_children[-1], buttons_id)\n            else:\n                link(parent_id, buttons_id)\n            for item in node.items:\n                button_id = make(\n                    "button",\n                    {"label": item.label, "target": item.target or "",\n                     "kind": item.kind},\n                    x + 600,\n                    y - 150,\n                )\n                link(buttons_id, button_id)\n                y += 110\n        elif isinstance(node, When):\n            when_props = {"op": node.condition.op, "value": node.condition.value}\n            if node.condition.source == "dice":\n                when_props["source"] = "dice"\n            if node.condition.values:\n                when_props["values"] = list(node.condition.values)\n            when_id = make("when", when_props, x + 380, y)\n            link(parent_id, when_id)\n            _actions_nodes(node.then, when_id, x + 380, y + 170, nodes, make, link)\n            if node.orelse:\n                start = y + 170 + 170 * max(1, len(node.then))\n                otherwise_id = make("otherwise", {}, x + 760, start)\n                link(when_id, otherwise_id)\n                _actions_nodes(node.orelse, otherwise_id, x + 760, start + 150, nodes,\n                               make, link)\n\n\n# ------------------------------------------------------------------- blocks\n# Every event kind the block editor can show.\nBLOCKLY_KINDS = {spec.kind for spec in EVENTS_BY_KIND.values()} | {"message"}\n\n\ndef _xml(value) -> str:\n    return (\n        str(value)\n        .replace("&", "&amp;")\n        .replace("<", "&lt;")\n        .replace(">", "&gt;")\n        .replace(\'"\', "&quot;")\n    )\n\n\ndef _field(name: str, value) -> str:\n    return \'<field name="{0}">{1}</field>\'.format(name, _xml(value))\n\n\ndef _chain_xml(blocks: List[List[str]], depth: int) -> List[str]:\n    """Join block renderings the way Blockly chains them: with <next>.\n\n    Blockly keeps one block per statement slot and links the rest through\n    `<next>`. Writing siblings into one <statement> made the editor show only\n    the first of them, which is exactly the bug this function removes.\n    """\n    if not blocks:\n        return []\n    pad = "  " * depth\n    out = list(blocks[0])\n    if len(blocks) > 1:\n        out.append(pad + "  <next>")\n        out.extend(_chain_xml(blocks[1:], depth + 2))\n        out.append(pad + "  </next>")\n    out.append(pad + "</block>")\n    return out\n\n\ndef _block_head(kind: str, depth: int) -> List[str]:\n    return ["  " * depth + \'<block type="tg_{0}">\'.format(kind)]\n\n\ndef _actions_blocks(actions: Sequence[object], depth: int) -> List[List[str]]:\n    inner = "  " * (depth + 1)\n    blocks: List[List[str]] = []\n    index = 0\n    while index < len(actions):\n        node = actions[index]\n        if isinstance(node, Action):\n            kind = node.kind\n            spec = ACTIONS_BY_KIND.get(kind)\n            block = _node_type(kind)\n            if kind == "nothing":\n                blocks.append(_block_head("nothing", depth))\n                index += 1\n                continue\n            if kind == "send":\n                lines = _block_head("send", depth)\n                lines.append(inner + _field("TEXT", str(node.params.get("text", ""))))\n                following = actions[index + 1] if index + 1 < len(actions) else None\n                if isinstance(following, Buttons):\n                    lines.append(inner + \'<statement name="DO">\')\n                    lines.extend(_chain_xml([_buttons_block(following, depth + 2)], depth + 2))\n                    lines.append(inner + "</statement>")\n                    index += 2\n                else:\n                    index += 1\n                blocks.append(lines)\n                continue\n            lines = _block_head(block, depth)\n            if spec is not None:\n                for param in spec.params:\n                    value = node.params.get(param.name, param.default)\n                    if param.kind == "values":\n                        value = "; ".join(str(item) for item in (value or ()))\n                    elif param.kind == "bool":\n                        value = "true" if value else "false"\n                    lines.append(inner + _field(param.name.upper(), value))\n            blocks.append(lines)\n            index += 1\n            continue\n\n        if isinstance(node, Buttons):\n            blocks.append(_buttons_block(node, depth))\n            index += 1\n            continue\n\n        if isinstance(node, When):\n            lines = _block_head("when", depth)\n            lines.append(inner + _field("SOURCE", node.condition.source))\n            lines.append(inner + _field("OP", node.condition.op))\n            lines.append(inner + _field("VALUE", node.condition.value))\n            lines.append(inner + _field("VALUES", "; ".join(node.condition.values)))\n            if node.then:\n                lines.append(inner + \'<statement name="DO">\')\n                lines.extend(_chain_xml(_actions_blocks(node.then, depth + 2), depth + 2))\n                lines.append(inner + "</statement>")\n            if node.orelse:\n                lines.append(inner + \'<statement name="ELSE">\')\n                lines.extend(_chain_xml(_actions_blocks(node.orelse, depth + 2), depth + 2))\n                lines.append(inner + "</statement>")\n            blocks.append(lines)\n            index += 1\n            continue\n        index += 1\n    return blocks\n\n\ndef _buttons_block(buttons: Buttons, depth: int) -> List[str]:\n    pad = "  " * depth\n    inner = "  " * (depth + 1)\n    lines = _block_head("buttons", depth)\n    lines.append(inner + _field("STYLE", buttons.style))\n    if buttons.items:\n        lines.append(inner + \'<statement name="DO">\')\n        rows: List[List[str]] = []\n        for item in buttons.items:\n            row = _block_head("button", depth + 2)\n            row.append("  " * (depth + 3) + _field("LABEL", item.label))\n            row.append("  " * (depth + 3) + _field("TARGET", item.target or ""))\n            row.append("  " * (depth + 3) + _field("KIND", item.kind))\n            rows.append(row)\n        lines.extend(_chain_xml(rows, depth + 2))\n        lines.append(inner + "</statement>")\n    return lines\n\n\ndef _event_block(handler: Handler, depth: int) -> List[str]:\n    pad = "  " * depth\n    inner = "  " * (depth + 1)\n    kind = handler.kind if handler.kind in BLOCKLY_KINDS else "any"\n    lines = _block_head("on", depth)\n    lines.append(inner + _field("KIND", kind))\n    lines.append(inner + _field("COMMAND", handler.command or ""))\n    lines.append(inner + _field("PATTERNS", ", ".join(handler.patterns)))\n    lines.append(inner + _field("DATA", handler.data))\n    lines.append(inner + _field("STATE", handler.state))\n    lines.append(inner + _field("CHAT", handler.chat))\n    lines.append(inner + _field("FROM_USER", handler.from_user or ""))\n    lines.append(inner + _field("REGEX", handler.regex))\n    blocks = _actions_blocks(handler.actions, depth + 2)\n    if blocks:\n        lines.append(inner + \'<statement name="DO">\')\n        lines.extend(_chain_xml(blocks, depth + 2))\n        lines.append(inner + "</statement>")\n    return lines\n\n\ndef spec_to_blocks_xml(spec: BotSpec) -> str:\n    lines: List[str] = [\'<xml xmlns="https://developers.google.com/blockly/xml">\']\n    lines.append(\'  <block type="tg_bot">\')\n    lines.append("    " + _field("TOKEN", spec.token or ""))\n    lines.append("    " + _field("NAME", "" if spec.name in ("", "tgblocks bot") else spec.name))\n    lines.append("    " + _field("PROXY", spec.proxy or ""))\n    lines.append("    " + _field("WEBHOOK", spec.webhook or ""))\n    if spec.handlers:\n        lines.append(\'    <statement name="DO">\')\n        lines.extend(_chain_xml([_event_block(handler, 3) for handler in spec.handlers], 3))\n        lines.append("    </statement>")\n    lines.append("  </block>")\n    lines.append("</xml>")\n    return "\\n".join(lines)\n\n\n# --------------------------------------------------------- board -> text\ndef _props(node: dict) -> dict:\n    value = node.get("props")\n    return value if isinstance(value, dict) else {}\n\n\ndef _children(board: dict, node: dict) -> List[dict]:\n    nodes = board.get("nodes") if isinstance(board.get("nodes"), dict) else board\n    out: List[dict] = []\n    for child_id in node.get("children") or []:\n        child = nodes.get(child_id)\n        if isinstance(child, dict):\n            out.append(child)\n    return out\n\n\ndef _children_of(node: dict, nodes: Dict[str, dict]) -> List[dict]:\n    out: List[dict] = []\n    for child_id in node.get("children") or []:\n        child = nodes.get(str(child_id))\n        if isinstance(child, dict):\n            out.append(child)\n    return out\n\n\ndef _button_from(node: dict) -> Button:\n    props = _props(node)\n    return Button(\n        label=str(props.get("label", "")),\n        kind=str(props.get("kind") or _guess_button_kind(props.get("target"))),\n        target=str(props.get("target", "")),\n    )\n\n\ndef _guess_button_kind(target) -> str:\n    text = str(target or "")\n    if text.startswith(("http://", "https://")):\n        return "url"\n    if text.startswith("/"):\n        return "command"\n    return "none"\n\n\ndef _params_from(spec: ActionSpec, props: dict) -> Dict[str, object]:\n    params: Dict[str, object] = {}\n    for param in spec.params:\n        value = props.get(param.name, param.default)\n        if param.kind == "values":\n            value = _patterns(value)\n        elif param.kind == "bool":\n            value = str(value).lower() in ("1", "true", "yes", "on", "да")\n        elif param.kind == "number":\n            try:\n                number = float(str(value).replace(",", ".") or 0)\n                value = int(number) if number.is_integer() else number\n            except ValueError:\n                value = 0\n        else:\n            value = str(value if value is not None else "")\n        params[param.name] = value\n    return params\n\n\ndef _buttons_from(node: dict, nodes: Dict[str, dict]) -> List[object]:\n    props = _props(node)\n    items = [_button_from(child) for child in _children_of(node, nodes)\n             if child.get("type") == "button"]\n    return [Buttons(style=str(props.get("style", "inline")), items=items)]\n\n\ndef _actions_of(children: List[dict], nodes: Dict[str, dict],\n                warnings: List[str] = None) -> List[object]:\n    """Turn one list of sibling blocks into actions.\n\n    The canvas lets a block sit *beside* another, so two rules are resolved here:\n    a `buttons` block right after a `send` belongs to it, and an `otherwise`\n    right after a `when` (or inside it) becomes that condition\'s else branch.\n    """\n    out: List[object] = []\n    index = 0\n    while index < len(children):\n        child = children[index]\n        node_type = str(child.get("type"))\n\n        if node_type == "otherwise":\n            if warnings is not None:\n                warnings.append("«Иначе» без «Условия» перед ним - блок пропущен")\n            index += 1\n            continue\n\n        if node_type == "buttons":\n            if warnings is not None:\n                warnings.append("«Клавиатура» должна стоять сразу после «Сообщения»")\n            index += 1\n            continue\n\n        if node_type == "when":\n            props = _props(child)\n            inner = _children_of(child, nodes)\n            nested_else = [item for item in inner if item.get("type") == "otherwise"]\n            then_children = [item for item in inner if item.get("type") != "otherwise"]\n            orelse: List[object] = []\n            consumed = 1\n            if nested_else:\n                orelse = _actions_of(_children_of(nested_else[0], nodes), nodes, warnings)\n            elif index + 1 < len(children) and children[index + 1].get("type") == "otherwise":\n                orelse = _actions_of(_children_of(children[index + 1], nodes), nodes, warnings)\n                consumed = 2\n            out.append(When(\n                condition=Condition(op=str(props.get("op", "contains")),\n                                    value=str(props.get("value", "")),\n                                    values=_patterns(props.get("values")),\n                                    source=str(props.get("source") or "text")),\n                then=_actions_of(then_children, nodes, warnings),\n                orelse=orelse,\n            ))\n            index += consumed\n            continue\n\n        if node_type == "send":\n            props = _props(child)\n            actions: List[object] = [\n                Action(kind="send", params={"text": str(props.get("text", ""))})\n            ]\n            consumed = 1\n            nested = [item for item in _children_of(child, nodes)\n                      if item.get("type") == "buttons"]\n            if nested:\n                actions.extend(_buttons_from(nested[0], nodes))\n            elif index + 1 < len(children) and children[index + 1].get("type") == "buttons":\n                actions.extend(_buttons_from(children[index + 1], nodes))\n                consumed = 2\n            out.extend(actions)\n            index += consumed\n            continue\n\n        spec = ACTIONS_BY_KIND.get(_action_kind(node_type))\n        if spec is not None:\n            out.append(Action(kind=spec.kind, params=_params_from(spec, _props(child))))\n        elif warnings is not None:\n            warnings.append("Неизвестный блок «{0}» пропущен".format(node_type))\n        index += 1\n    return out\n\n\ndef _patterns(value) -> tuple:\n    # The board carries patterns as a list; older files may hold one string.\n    if isinstance(value, str):\n        items = [item.strip() for item in value.replace(";", ",").split(",")]\n        return tuple(item for item in items if item)\n    if isinstance(value, (list, tuple)):\n        return tuple(str(item) for item in value if str(item).strip())\n    return ()\n\n\ndef board_to_spec(board: dict) -> BotSpec:\n    section = board.get("nodes") if isinstance(board.get("nodes"), dict) else board\n    nodes: Dict[str, dict] = {\n        str(key): value\n        for key, value in (section or {}).items()\n        if isinstance(value, dict)\n    }\n    root_id = board.get("rootId")\n    root = nodes.get(str(root_id)) if root_id is not None else None\n    if not isinstance(root, dict):\n        for candidate in nodes.values():\n            if candidate.get("type") == "bot":\n                root = candidate\n                break\n    spec = BotSpec()\n    if not isinstance(root, dict):\n        return spec\n    props = _props(root)\n    spec.token = str(props.get("token", "")).strip() or None\n    spec.proxy = str(props.get("proxy", "")).strip()\n    spec.webhook = str(props.get("webhook", "") or "").strip()\n    spec.webhook_path = str(props.get("webhook_path", "") or "/webhook").strip()\n    spec.webhook_secret = str(props.get("webhook_secret", "") or "").strip()\n    name = str(props.get("name", "") or "").strip()\n    if name:\n        spec.name = name\n    warnings: List[str] = []\n    for event in _children_of(root, nodes):\n        if event.get("type") != "event":\n            continue\n        handler, handler_warnings = _handler_from(event, nodes)\n        warnings.extend(handler_warnings)\n        if not handler.actions:\n            warnings.append(\n                "у события «{0}» нет действий".format(handler.kind)\n                if handler.kind != "command"\n                else "у команды {0} нет действий".format(handler.command)\n            )\n        spec.handlers.append(handler)\n    spec.warnings = warnings\n    # States are declared by the actions that use them, in source order.\n    for handler in spec.handlers:\n        for action in _walk(handler.actions):\n            if isinstance(action, Action) and action.kind == "set_state":\n                state = str(action.params.get("state") or "")\n                if state and state not in spec.states:\n                    spec.states.append(state)\n    for handler in spec.handlers:\n        if handler.kind == "state" and handler.state and handler.state not in spec.states:\n            spec.states.append(handler.state)\n    return spec\n\n\ndef _walk(actions):\n    for node in actions:\n        yield node\n        if isinstance(node, When):\n            yield from _walk(node.then)\n            yield from _walk(node.orelse)\n\n\ndef _handler_from(event: dict, nodes: Dict[str, dict]):\n    props = _props(event)\n    kind = str(props.get("kind", "command"))\n    if kind == "message":\n        kind = "text"\n    params: Dict[str, object] = {}\n    if kind == "command":\n        params["command"] = str(props.get("command", "") or "/start")\n    if kind == "callback":\n        params["data"] = str(props.get("data", "") or "")\n    if kind == "state":\n        params["state"] = str(props.get("state", "") or "")\n    if "patterns" in props:\n        params["patterns"] = _patterns(props.get("patterns"))\n    for key in ("chat", "from_user", "regex"):\n        if props.get(key):\n            params[key] = props[key]\n    warnings: List[str] = []\n    actions = _actions_of(_children_of(event, nodes), nodes, warnings)\n    return Handler(kind=kind, actions=actions, params=params), warnings\n\n\ndef board_to_text(board: dict) -> str:\n    return spec_to_text(board_to_spec(board))\n\n\n# --------------------------------------------------------- blocks -> spec\n_XML_NS = "{https://developers.google.com/blockly/xml}"\n\n\ndef _tag(element) -> str:\n    return element.tag.replace(_XML_NS, "") if isinstance(element.tag, str) else ""\n\n\ndef _child(element, tag: str):\n    for child in element:\n        if _tag(child) == tag:\n            return child\n    return None\n\n\ndef _field_value(element, name: str, default: str = "") -> str:\n    for child in element:\n        if _tag(child) == "field" and child.get("name") == name:\n            return (child.text or "").strip()\n    return default\n\n\ndef _statement_blocks(element, name: str) -> List:\n    # <statement name="DO"><block .../></statement> - the first block of a chain.\n    statement = None\n    for child in element:\n        if _tag(child) == "statement" and child.get("name") == name:\n            statement = child\n            break\n    if statement is None:\n        return []\n    for child in statement:\n        if _tag(child) == "block":\n            return [child]\n    return []\n\n\ndef _next_block(element):\n    # Blockly chains blocks with <next><block .../></next>.\n    next_tag = _child(element, "next")\n    if next_tag is None:\n        return None\n    for child in next_tag:\n        if _tag(child) == "block":\n            return child\n    return None\n\n\ndef _chain(element) -> List:\n    out = []\n    current = element\n    while current is not None:\n        out.append(current)\n        current = _next_block(current)\n    return out\n\n\ndef _buttons_from_block(element) -> Buttons:\n    style = _field_value(element, "STYLE", "inline") or "inline"\n    items: List[Button] = []\n    for block in _chain_many(_statement_blocks(element, "DO")):\n        if _tag(block) != "block" or block.get("type") != "tg_button":\n            continue\n        target = _field_value(block, "TARGET")\n        kind = _field_value(block, "KIND") or _guess_button_kind(target)\n        items.append(Button(label=_field_value(block, "LABEL"), kind=kind,\n                            target=target))\n    return Buttons(style=style, items=items)\n\n\ndef _chain_many(blocks: List) -> List:\n    out: List = []\n    for block in blocks:\n        out.extend(_chain(block))\n    return out\n\n\ndef _actions_from_block(element) -> List[object]:\n    out: List[object] = []\n    for block in _chain(element):\n        block_type = str(block.get("type", ""))\n        if block_type == "tg_send":\n            out.append(Action(kind="send", params={"text": _field_value(block, "TEXT")}))\n            buttons = _statement_blocks(block, "DO")\n            if buttons:\n                out.append(_buttons_from_block(buttons[0]))\n            continue\n        if block_type == "tg_buttons":\n            out.append(_buttons_from_block(block))\n            continue\n        if block_type == "tg_when":\n            then_blocks = _statement_blocks(block, "DO")\n            else_blocks = _statement_blocks(block, "ELSE")\n            then: List[object] = []\n            orelse: List[object] = []\n            if then_blocks:\n                then = _actions_from_block(then_blocks[0])\n            if else_blocks:\n                orelse = _actions_from_block(else_blocks[0])\n            out.append(When(\n                condition=Condition(op=_field_value(block, "OP", "contains"),\n                                    value=_field_value(block, "VALUE"),\n                                    values=_patterns(_field_value(block, "VALUES")),\n                                    source=_field_value(block, "SOURCE", "text") or "text"),\n                then=then, orelse=orelse))\n            continue\n        if block_type == "tg_otherwise":\n            blocks = _statement_blocks(block, "DO")\n            if blocks:\n                out.extend(_actions_from_block(blocks[0]))\n            continue\n        if not block_type.startswith("tg_"):\n            continue\n        kind = _action_kind(block_type[3:])\n        spec = ACTIONS_BY_KIND.get(kind)\n        if spec is None:\n            continue\n        params: Dict[str, object] = {}\n        for param in spec.params:\n            raw = _field_value(block, param.name.upper(), "")\n            if param.kind == "values":\n                params[param.name] = _patterns(raw)\n            elif param.kind == "bool":\n                params[param.name] = raw.lower() in ("true", "1", "yes", "on", "да")\n            elif param.kind == "number":\n                try:\n                    number = float(raw.replace(",", ".") or 0)\n                    params[param.name] = int(number) if number.is_integer() else number\n                except ValueError:\n                    params[param.name] = 0\n            else:\n                params[param.name] = raw\n        out.append(Action(kind=kind, params=params))\n    return out\n\n\ndef _handler_from_block(element) -> Handler:\n    kind = _field_value(element, "KIND", "command") or "command"\n    if kind == "message":\n        kind = "text"\n    params: Dict[str, object] = {}\n    if kind == "command":\n        params["command"] = _field_value(element, "COMMAND", "/start") or "/start"\n    if kind == "callback":\n        params["data"] = _field_value(element, "DATA")\n    if kind == "state":\n        params["state"] = _field_value(element, "STATE")\n    patterns = _patterns(_field_value(element, "PATTERNS"))\n    if patterns:\n        params["patterns"] = patterns\n    chat = _field_value(element, "CHAT")\n    if chat:\n        params["chat"] = chat\n    from_user = _field_value(element, "FROM_USER")\n    if from_user:\n        try:\n            params["from_user"] = int(float(from_user))\n        except ValueError:\n            pass\n    regex = _field_value(element, "REGEX")\n    if regex:\n        params["regex"] = regex\n    actions: List[object] = []\n    blocks = _statement_blocks(element, "DO")\n    if blocks:\n        actions = _actions_from_block(blocks[0])\n    return Handler(kind=kind, actions=actions, params=params)\n\n\ndef blocks_xml_to_spec(xml_text: str) -> BotSpec:\n    """Read a Blockly workspace exported by the block editor."""\n    spec = BotSpec()\n    try:\n        root = ET.fromstring(xml_text)\n    except ET.ParseError as error:\n        raise ValueError("cannot read the workspace XML: {0}".format(error)) from None\n    blocks = [child for child in root if _tag(child) == "block"]\n    if not blocks:\n        return spec\n    for block in _chain(blocks[0]):\n        if block.get("type") != "tg_bot":\n            continue\n        spec.token = _field_value(block, "TOKEN") or None\n        name = _field_value(block, "NAME")\n        if name:\n            spec.name = name\n        spec.proxy = _field_value(block, "PROXY")\n        spec.webhook = _field_value(block, "WEBHOOK")\n        events = _statement_blocks(block, "DO")\n        for event_block in _chain_many(events):\n            if event_block.get("type") == "tg_on":\n                spec.handlers.append(_handler_from_block(event_block))\n    for handler in spec.handlers:\n        for action in _walk(handler.actions):\n            if isinstance(action, Action) and action.kind == "set_state":\n                state = str(action.params.get("state") or "")\n                if state and state not in spec.states:\n                    spec.states.append(state)\n    for handler in spec.handlers:\n        if handler.kind == "state" and handler.state and handler.state not in spec.states:\n            spec.states.append(handler.state)\n    return spec\n\n\n# -------------------------------------------------------------------- layout\n# Where the blocks sit on the canvas is editor state, not bot logic: it lives\n# next to the text and is keyed by a structural path, so re-reading the same\n# bot puts every block back where the user left it.\ndef _board_nodes(board: dict) -> dict:\n    if not isinstance(board, dict):\n        return {}\n    section = board.get("nodes")\n    return section if isinstance(section, dict) else board\n\n\ndef _walk_board(board: dict):\n    # Yields (path, node) for the whole tree under the bot block.\n    nodes = _board_nodes(board)\n    root_id = board.get("rootId") if isinstance(board, dict) else None\n    root = nodes.get(root_id) if root_id else None\n    if not isinstance(root, dict):\n        root_id, root = None, None\n        for key, candidate in nodes.items():\n            if isinstance(candidate, dict) and candidate.get("type") == "bot":\n                root_id, root = key, candidate\n                break\n    if root is None:\n        return\n\n    def visit(node_id: str, path: str) -> None:\n        node = nodes.get(node_id)\n        if not isinstance(node, dict):\n            return\n        yield path, node\n        counters: Dict[str, int] = {}\n        for child_id in node.get("children") or []:\n            child = nodes.get(child_id)\n            if not isinstance(child, dict):\n                continue\n            kind = child.get("type")\n            if kind == "event":\n                bucket = "e"\n            elif kind == "otherwise":\n                bucket = "o"\n            elif kind == "buttons":\n                bucket = "k"\n            elif kind == "button":\n                bucket = "c"\n            else:\n                bucket = "a"\n            counters[bucket] = counters.get(bucket, 0) + 1\n            yield from visit(child_id, path + "/" + bucket + str(counters[bucket]))\n\n    yield from visit(root_id, "b")\n\n\ndef board_layout(board: dict) -> Dict[str, dict]:\n    layout: Dict[str, dict] = {}\n    for path, node in _walk_board(board):\n        x, y = node.get("x"), node.get("y")\n        if isinstance(x, (int, float)) and isinstance(y, (int, float)):\n            layout[path] = {"x": x, "y": y}\n    return layout\n\n\ndef apply_layout(board: dict, layout: Dict[str, dict]) -> dict:\n    if not isinstance(layout, dict) or not layout:\n        return board\n    for path, node in _walk_board(board):\n        spot = layout.get(path)\n        if not isinstance(spot, dict):\n            continue\n        x, y = spot.get("x"), spot.get("y")\n        if isinstance(x, (int, float)) and isinstance(y, (int, float)):\n            node["x"], node["y"] = x, y\n    return board\n',
    "src/tgblocks/dsl/__init__.py": r"""# Text DSL front end: parser + aiogram code generator.

from .codegen import CodeGenError, compile_source, generate
from .parser import (
    Action,
    BotSpec,
    Button,
    Buttons,
    Condition,
    DSLParseError,
    Handler,
    When,
    parse,
    parse_file,
    validate,
)

__all__ = [
    "Action",
    "BotSpec",
    "Button",
    "Buttons",
    "CodeGenError",
    "Condition",
    "DSLParseError",
    "Handler",
    "When",
    "compile_source",
    "generate",
    "parse",
    "parse_file",
    "validate",
]
""",
    "src/tgblocks/dsl/codegen.py": '# Compile a parsed tgblocks bot into readable aiogram 3 source code.\n#\n# The generator reads the catalogue in tgblocks.model: every action has an\n# emitter family there, and every event knows its aiogram observer and filter.\n# Generated helpers are emitted only when a bot uses them, so a small bot stays\n# small and a bot with media does not carry unused code.\n\nfrom __future__ import annotations\n\nimport json\nimport keyword\nimport re\nfrom typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple\n\nfrom ..model import ACTIONS_BY_KIND, EVENTS_BY_KIND, EventSpec\nfrom .parser import (\n    Action,\n    BotSpec,\n    Buttons,\n    Condition,\n    DSLParseError,\n    Handler,\n    When,\n)\n\nINDENT = "    "\nLINE_WIDTH = 88\n\n# Names used by the generated helpers: a command called /reply must not shadow them.\nRESERVED = {\n    "reply", "inline", "keyboard", "text_of", "media", "remove", "typing",\n    "delay", "pin", "unpin", "edit_text", "answer_callback", "ban_user",\n    "unban_user", "mute_user", "send_poll", "inline_result", "api",\n    "dp", "bot", "main", "state", "Form", "logging", "asyncio", "os",\n    "Bot", "Dispatcher", "F", "Command", "Message", "CallbackQuery",\n}\n\n\ndef _literal(value: str) -> str:\n    # Double-quoted Python literal, Cyrillic kept as is.\n    return json.dumps(str(value), ensure_ascii=False)\n\n\ndef _tuple_literal(values) -> str:\n    items = [_literal(item) for item in values]\n    if not items:\n        return "()"\n    if len(items) == 1:\n        return "({0},)".format(items[0])\n    return "({0})".format(", ".join(items))\n\n\ndef _number(value) -> str:\n    number = float(value)\n    return str(int(number)) if number.is_integer() else str(number)\n\n\ndef _condition_expression(condition: Condition) -> str:\n    if condition.source == "dice":\n        # What the interactive emoji landed on, as a number.\n        number = condition.value if condition.value.lstrip("-").isdigit() else "0"\n        return "dice_value(event) {0} {1}".format(condition.op, number)\n    text = "text_of(event)"\n    lowered = "text_of(event).lower()"\n    value = condition.value\n    if condition.values:\n        parts = []\n        for item in (value,) + tuple(condition.values):\n            piece = _condition_expression(\n                Condition(op=condition.op, value=item, line=condition.line)\n            )\n            if piece not in parts:\n                parts.append(piece)\n        if condition.op == "!=":\n            return " and ".join(parts)\n        return " or ".join("({0})".format(item) for item in parts)\n    if condition.op == "==":\n        return "{0} == {1}".format(text, _literal(value))\n    if condition.op == "!=":\n        return "{0} != {1}".format(text, _literal(value))\n    if condition.op == "contains":\n        return "{0} in {1}".format(_literal(value.lower()), lowered)\n    if condition.op == "startswith":\n        return "{0}.startswith({1})".format(lowered, _literal(value.lower()))\n    if condition.op == "endswith":\n        return "{0}.endswith({1})".format(lowered, _literal(value.lower()))\n    raise CodeGenError(\n        "unsupported condition operator {0!r}".format(condition.op),\n        line=condition.line,\n    )\n\n\nclass CodeGenError(DSLParseError):\n    # Raised when the DSL is syntactically valid but cannot become Python.\n    pass\n\n\n# ------------------------------------------------------------------- helpers\n# Each helper is emitted only when a handler uses it. The first element is the\n# name used to decide that; the body is plain Python.\nHELPER_BODIES: Dict[str, str] = {\n    "inline": \'\'\'def inline(*buttons) -> InlineKeyboardMarkup:\n    # inline(("Help", "/help", "command"), ("Site", "https://example.com", "url"))\n    rows = []\n    for label, target, kind in buttons:\n        if kind == "web_app":\n            rows.append([InlineKeyboardButton(text=label, web_app=WebAppInfo(url=target))])\n        elif kind == "url" or target.startswith(("http://", "https://")):\n            rows.append([InlineKeyboardButton(text=label, url=target)])\n        else:\n            rows.append([InlineKeyboardButton(text=label, callback_data=target)])\n    return InlineKeyboardMarkup(inline_keyboard=rows)\'\'\',\n    "keyboard": \'\'\'def keyboard(*buttons) -> ReplyKeyboardMarkup:\n    # keyboard(("Help", "text"), ("Phone", "contact")) - a reply keyboard\n    rows = []\n    for label, kind in buttons:\n        if kind == "contact":\n            rows.append([KeyboardButton(text=label, request_contact=True)])\n        elif kind == "location":\n            rows.append([KeyboardButton(text=label, request_location=True)])\n        else:\n            rows.append([KeyboardButton(text=label)])\n    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)\'\'\',\n    "text_of": \'\'\'def text_of(event) -> str:\n    # Message and CallbackQuery both land here, so unwrap the message first.\n    message = event.message if isinstance(event, CallbackQuery) else event\n    return (message.text or "") if message is not None else ""\'\'\',\n    "dice_value": \'\'\'def dice_value(event) -> int:\n    # What the interactive emoji landed on; 0 when the message has none.\n    message = event.message if isinstance(event, CallbackQuery) else event\n    dice = getattr(message, "dice", None)\n    return dice.value if dice is not None else 0\'\'\',\n    "reply": \'\'\'async def reply(event, text, markup=None) -> None:\n    # One call answers a plain message, an inline-button press or a chat event.\n    if isinstance(event, CallbackQuery):\n        if event.message is not None:\n            await event.message.answer(text, reply_markup=markup)\n        await event.answer()\n    elif isinstance(event, Message):\n        await event.answer(text, reply_markup=markup)\n    else:\n        await event.bot.send_message(event.chat.id, text, reply_markup=markup)\'\'\',\n    "media": \'\'\'async def media(event, method, *args, **kwargs) -> None:\n    # media(event, "answer_photo", "https://...", caption="...") - any send method\n    message = event.message if isinstance(event, CallbackQuery) else event\n    await getattr(message, method)(*args, **kwargs)\n    if isinstance(event, CallbackQuery):\n        await event.answer()\'\'\',\n    "send_poll": \'\'\'async def send_poll(event, question, options) -> None:\n    message = event.message if isinstance(event, CallbackQuery) else event\n    await message.answer_poll(\n        question, [InputPollOption(text=item) for item in options]\n    )\n    if isinstance(event, CallbackQuery):\n        await event.answer()\'\'\',\n    "remove": \'\'\'async def remove(event) -> None:\n    # Delete the message the button or command arrived from.\n    message = event.message if isinstance(event, CallbackQuery) else event\n    await message.delete()\n    if isinstance(event, CallbackQuery):\n        await event.answer()\'\'\',\n    "typing": \'\'\'async def typing(event) -> None:\n    # Show "bot is typing..." in the chat.\n    message = event.message if isinstance(event, CallbackQuery) else event\n    await event.bot.send_chat_action(message.chat.id, "typing")\'\'\',\n    "delay": \'\'\'async def delay(seconds) -> None:\n    await asyncio.sleep(seconds)\'\'\',\n    "edit_text": \'\'\'async def edit_text(event, text) -> None:\n    message = event.message if isinstance(event, CallbackQuery) else event\n    await message.edit_text(text)\n    if isinstance(event, CallbackQuery):\n        await event.answer()\'\'\',\n    "answer_callback": \'\'\'async def answer_callback(event, text="", alert=False) -> None:\n    if isinstance(event, CallbackQuery):\n        await event.answer(text or None, show_alert=alert or None)\'\'\',\n    "pin": \'\'\'async def pin(event, silent=False) -> None:\n    message = event.message if isinstance(event, CallbackQuery) else event\n    await event.bot.pin_chat_message(\n        message.chat.id, message.message_id, disable_notification=silent\n    )\'\'\',\n    "unpin": \'\'\'async def unpin(event) -> None:\n    message = event.message if isinstance(event, CallbackQuery) else event\n    await event.bot.unpin_chat_message(message.chat.id, message.message_id)\'\'\',\n    "ban_user": \'\'\'async def ban_user(event, user_id=0) -> None:\n    message = event.message if isinstance(event, CallbackQuery) else event\n    target = user_id or (message.from_user.id if message.from_user else 0)\n    await event.bot.ban_chat_member(message.chat.id, target)\'\'\',\n    "unban_user": \'\'\'async def unban_user(event, user_id=0) -> None:\n    message = event.message if isinstance(event, CallbackQuery) else event\n    target = user_id or (message.from_user.id if message.from_user else 0)\n    await event.bot.unban_chat_member(message.chat.id, target)\'\'\',\n    "mute_user": \'\'\'async def mute_user(event, user_id=0, minutes=10) -> None:\n    message = event.message if isinstance(event, CallbackQuery) else event\n    target = user_id or (message.from_user.id if message.from_user else 0)\n    await event.bot.restrict_chat_member(\n        message.chat.id,\n        target,\n        permissions=ChatPermissions(can_send_messages=False),\n        until_date=timedelta(minutes=minutes),\n    )\'\'\',\n    "inline_result": \'\'\'async def inline_result(event, title, text, description="") -> None:\n    await event.answer(\n        results=[\n            InlineQueryResultArticle(\n                id=str(abs(hash(text)) % 10**8),\n                title=title,\n                description=description or None,\n                input_message_content=InputTextMessageContent(message_text=text),\n            )\n        ]\n    )\'\'\',\n}\n\n# Which import a helper needs (besides the always-present aiogram core).\nHELPER_IMPORTS: Dict[str, Tuple[str, ...]] = {\n    "inline": ("InlineKeyboardButton", "InlineKeyboardMarkup"),\n    "keyboard": ("KeyboardButton", "ReplyKeyboardMarkup"),\n    "media": (),\n    "send_poll": ("InputPollOption",),\n    "edit_text": (),\n    "answer_callback": (),\n    "mute_user": ("ChatPermissions", "timedelta"),\n    "inline_result": ("InlineQueryResultArticle", "InputTextMessageContent"),\n}\n\nRUN_LINE = "# Run:  TG_BOT_TOKEN=123456:ABC python bot.py"\n\n\nclass _Usage:\n    """Which imports and helpers the generated file has to carry."""\n\n    def __init__(self) -> None:\n        self.helpers: Set[str] = set()\n        self.types: Set[str] = set()\n        self.use_command = False\n        self.use_filter = False\n        self.use_state = False\n        self.use_webhook = False\n\n    def want(self, helper: str) -> None:\n        self.helpers.add(helper)\n        for name in HELPER_IMPORTS.get(helper, ()):  # type: ignore[arg-type]\n            self.types.add(name)\n\n\ndef _iter_actions(actions) -> Iterable[object]:\n    for node in actions:\n        yield node\n        if isinstance(node, When):\n            yield from _iter_actions(node.then)\n            yield from _iter_actions(node.orelse)\n\n\ndef _scan(spec: BotSpec, usage: _Usage) -> None:\n    for handler in spec.handlers:\n        spec_event = EVENTS_BY_KIND.get(handler.kind)\n        if handler.kind == "command":\n            usage.use_command = True\n            # Every command also answers its own inline button, and that\n            # decorator is built from F.data.\n            usage.use_filter = True\n        if handler.kind == "callback" and handler.data:\n            # The callback filter itself is F.data == "...".\n            usage.use_filter = True\n        if spec_event is not None and spec_event.filter:\n            usage.use_filter = True\n        if handler.chat or handler.from_user or handler.regex or handler.patterns:\n            usage.use_filter = True\n        if handler.kind == "state":\n            usage.use_state = True\n        for node in _iter_actions(handler.actions):\n            if isinstance(node, Buttons):\n                usage.want("keyboard" if node.style == "reply" else "inline")\n                if node.style == "reply" and any(\n                    button.kind == "contact" or button.kind == "location"\n                    for button in node.items\n                ):\n                    usage.types.add("KeyboardButton")\n                if any(button.kind == "web_app" for button in node.items):\n                    usage.types.add("WebAppInfo")\n                continue\n            if not isinstance(node, Action):\n                continue\n            kind = node.kind\n            if kind == "send":\n                usage.want("reply")\n            elif kind in ("send_photo", "send_document", "send_video", "send_animation",\n                          "send_audio", "send_voice", "send_sticker", "send_location",\n                          "send_contact", "send_dice"):\n                usage.want("media")\n            elif kind == "send_poll":\n                usage.want("send_poll")\n            elif kind == "delete":\n                usage.want("remove")\n            elif kind == "typing":\n                usage.want("typing")\n            elif kind == "delay":\n                usage.want("delay")\n            elif kind == "edit_text":\n                usage.want("edit_text")\n            elif kind == "answer_callback":\n                usage.want("answer_callback")\n            elif kind == "pin":\n                usage.want("pin")\n            elif kind == "unpin":\n                usage.want("unpin")\n            elif kind == "ban_user":\n                usage.want("ban_user")\n            elif kind == "unban_user":\n                usage.want("unban_user")\n            elif kind == "mute_user":\n                usage.want("mute_user")\n            elif kind == "inline_result":\n                usage.want("inline_result")\n            elif kind in ("set_state", "clear_state"):\n                usage.use_state = True\n    # Conditions need one helper each: text comparison or the emoji value.\n    for node in _iter_actions([node for handler in spec.handlers for node in handler.actions]):\n        if isinstance(node, When):\n            usage.want("dice_value" if node.condition.source == "dice" else "text_of")\n    if spec.states:\n        usage.use_state = True\n    if spec.webhook:\n        usage.use_webhook = True\n    if usage.helpers & {"reply", "media", "edit_text", "remove", "typing", "pin",\n                        "unpin", "ban_user", "unban_user", "mute_user", "text_of",\n                        "send_poll"}:\n        usage.types.add("CallbackQuery")\n    if usage.helpers & {"reply", "edit_text", "remove", "typing", "pin", "unpin",\n                        "ban_user", "unban_user", "mute_user", "send_poll", "media",\n                        "inline_result", "answer_callback"}:\n        usage.types.add("Message")\n\n\ndef _needs_text_of(node: When) -> bool:\n    return node.condition.source != "dice"\n\n\n# --------------------------------------------------------------------- emitters\nclass _Emitter:\n    def __init__(self, bot: BotSpec, embed_token: bool = True) -> None:\n        self.bot = bot\n        self.embed_token = embed_token\n        self._lines: List[str] = []\n        self._used: Set[str] = set()\n        self.usage = _Usage()\n        _scan(bot, self.usage)\n\n    # ------------------------------------------------------------------ names\n    def _unique(self, base: str) -> str:\n        candidate = base\n        counter = 0\n        while (\n            candidate in self._used\n            or candidate in RESERVED\n            or keyword.iskeyword(candidate)\n        ):\n            counter += 1\n            candidate = "{0}_{1}".format(base, counter)\n        self._used.add(candidate)\n        return candidate\n\n    def _name_for(self, handler: Handler) -> str:\n        if handler.kind == "command" and handler.command:\n            base = re.sub(r"\\W", "_", handler.command.lstrip("/")) or "command"\n            if base in RESERVED or keyword.iskeyword(base):\n                base = "cmd_" + base\n            return self._unique(base)\n        name = "on_" + handler.kind\n        if handler.kind == "state" and handler.state:\n            name = "on_state_" + re.sub(r"\\W", "_", handler.state)\n        return self._unique(name)\n\n    # ---------------------------------------------------------------- assembly\n    def generate(self) -> str:\n        out: List[str] = []\n        out.extend(self._header())\n        out.append("")\n        out.append("")\n        ordered = sorted(\n            self.bot.handlers,\n            key=lambda item: (\n                self._order(item),\n                _KIND_ORDER.get(item.kind, 25),\n                0 if item.patterns else 1,\n            ),\n        )\n        for handler in ordered:\n            out.extend(self._emit_handler(handler, self._name_for(handler)))\n            out.append("")\n            out.append("")\n        out.extend(self._footer())\n        return "\\n".join(out).rstrip("\\n") + "\\n"\n\n    def _order(self, handler: Handler) -> int:\n        spec = EVENTS_BY_KIND.get(handler.kind)\n        base = _OBSERVER_ORDER.get(spec.observer if spec else "message", 8)\n        return base\n\n    # ------------------------------------------------------------------ header\n    def _header(self) -> List[str]:\n        lines = [\n            "# Telegram bot generated by tgblocks - edit freely.",\n            "# Bot: {0}".format(self.bot.name),\n            RUN_LINE,\n        ]\n        if not self.embed_token:\n            # A generated bot is something people commit and share: the secret\n            # stays in the environment or in the .tg file, never in the artefact.\n            lines.append("# The token is NOT written into this file on purpose: export")\n            lines.append("# TG_BOT_TOKEN=123456:ABC before running it.")\n        lines.append("")\n        lines.append("import asyncio")\n        lines.append("import logging")\n        lines.append("import os")\n        if "timedelta" in self.usage.types:\n            lines.append("from datetime import timedelta")\n        lines.append("")\n        lines.append("from aiogram import Bot, Dispatcher" + (", F" if self.usage.use_filter else ""))\n        lines.append("from aiogram.client.session.aiohttp import AiohttpSession")\n        lines.append("from aiogram.exceptions import TelegramNetworkError")\n        if self.usage.use_command:\n            lines.append("from aiogram.filters import Command")\n        if self.usage.use_state:\n            lines.append("from aiogram.filters import StateFilter")\n            lines.append("from aiogram.fsm.context import FSMContext")\n            lines.append("from aiogram.fsm.state import State, StatesGroup")\n            lines.append("from aiogram.fsm.storage.memory import MemoryStorage")\n        lines.append("")\n        lines.append("try:")\n        lines.append("    from aiohttp_socks import ProxyConnectionError")\n        lines.append("except Exception:  # aiohttp-socks is optional")\n        lines.append("    ProxyConnectionError = ConnectionError")\n\n        types = self._type_names()\n        if types:\n            lines.append("from aiogram.types import (")\n            for name in types:\n                lines.append("    {0},".format(name))\n            lines.append(")")\n        lines.append("")\n        lines.append("BOT_TOKEN = os.environ.get(\\"TG_BOT_TOKEN\\", {0})".format(\n            _literal(self.bot.token or "") if self.embed_token else \'""\'))\n        lines.append("PROXY = os.environ.get(\\"TG_PROXY\\", {0})".format(\n            _literal(self.bot.proxy or "")))\n        if self.usage.use_webhook:\n            lines.append("WEBHOOK_URL = os.environ.get(\\"TG_WEBHOOK_URL\\", {0})".format(\n                _literal(self.bot.webhook)))\n            lines.append("WEBHOOK_PATH = {0}".format(_literal(self.bot.webhook_path)))\n            lines.append("WEBHOOK_SECRET = os.environ.get(\\"TG_WEBHOOK_SECRET\\", {0})".format(\n                _literal(self.bot.webhook_secret)))\n        lines.append("")\n        if self.usage.use_state:\n            lines.append("dp = Dispatcher(storage=MemoryStorage())")\n            lines.append("")\n            lines.append("")\n            lines.append("class Form(StatesGroup):")\n            for state in self.bot.states:\n                lines.append("    {0} = State()".format(state))\n        else:\n            lines.append("dp = Dispatcher()")\n\n        for helper in self._helper_order():\n            lines.append("")\n            lines.append("")\n            lines.extend(HELPER_BODIES[helper].splitlines())\n        return lines\n\n    def _helper_order(self) -> List[str]:\n        order = ["inline", "keyboard", "text_of", "dice_value", "reply", "media",\n                 "send_poll", "remove", "typing", "delay", "edit_text",\n                 "answer_callback", "pin", "unpin", "ban_user", "unban_user",\n                 "mute_user", "inline_result"]\n        return [name for name in order if name in self.usage.helpers]\n\n    def _type_names(self) -> List[str]:\n        core = {"CallbackQuery", "Message"} & self.usage.types\n        names = []\n        for name in ("CallbackQuery", "ChatPermissions", "InlineKeyboardButton",\n                     "InlineKeyboardMarkup", "InlinePollOption", "InlineQuery"\n                     "ResultArticle", "InputPollOption", "InputTextMessageContent",\n                     "KeyboardButton", "Message", "ReplyKeyboardMarkup", "WebAppInfo"):\n            if name in self.usage.types:\n                names.append(name)\n        return names\n\n    # ----------------------------------------------------------------- handlers\n    def _emit_handler(self, handler: Handler, name: str) -> List[str]:\n        self._lines = []\n        self._emit_actions(handler.actions, 1)\n        if not self._lines:\n            self._lines = ["{0}pass".format(INDENT)]\n\n        lines: List[str] = []\n        lines.extend(self._decorators(handler))\n        needs_state = self._uses_state(handler.actions)\n        signature = "(event, state: FSMContext)" if needs_state else "(event)"\n        lines.append("async def {0}{1} -> None:".format(name, signature))\n        lines.extend(self._lines)\n        return lines\n\n    def _uses_state(self, actions) -> bool:\n        for node in _iter_actions(actions):\n            if isinstance(node, Action) and node.kind in ("set_state", "clear_state"):\n                return True\n        return False\n\n    def _decorators(self, handler: Handler) -> List[str]:\n        spec = EVENTS_BY_KIND.get(handler.kind)\n        if spec is None:\n            raise CodeGenError("unknown event {0!r}".format(handler.kind),\n                               line=handler.line)\n        # Filters go as separate arguments, never joined with "&": aiogram checks\n        # them one by one, while `Command(...) & F.chat.type == "x"` raises\n        # "unsupported operand type(s) for &: \'Command\' and \'bool\'" at runtime.\n        filters = self._filters(handler, spec)\n        lines = ["@dp.{0}({1})".format(spec.observer, ", ".join(filters))]\n        if handler.kind == "command":\n            callback_filters = [\'F.data == {0}\'.format(_literal(handler.command or ""))]\n            if handler.from_user:\n                callback_filters.append("F.from_user.id == {0}".format(handler.from_user))\n            lines.append("@dp.callback_query({0})".format(", ".join(callback_filters)))\n        return lines\n\n    def _filters(self, handler: Handler, spec: EventSpec) -> List[str]:\n        filters: List[str] = []\n        if spec.filter:\n            filters.append(spec.filter)\n        if handler.patterns:\n            filters.append("F.text.in_({0})".format(_tuple_literal(handler.patterns)))\n        if handler.kind == "command":\n            filters.append(\'Command("{0}")\'.format((handler.command or "").lstrip("/")))\n        if handler.kind == "callback" and handler.data:\n            filters.append("F.data == {0}".format(_literal(handler.data)))\n        if handler.kind == "state":\n            filters.append("StateFilter(Form.{0})".format(handler.state))\n        if handler.chat:\n            filters.append(\'F.chat.type == {0}\'.format(_literal(handler.chat)))\n        if handler.from_user:\n            filters.append("F.from_user.id == {0}".format(handler.from_user))\n        if handler.regex:\n            filters.append("F.text.regexp({0})".format(_literal(handler.regex)))\n        return filters\n\n    # --------------------------------------------------------------- statements\n    def _emit_actions(self, actions: Sequence[object], depth: int) -> None:\n        pad = INDENT * depth\n        index = 0\n        while index < len(actions):\n            node = actions[index]\n\n            if isinstance(node, Action) and node.kind == "send":\n                markup = None\n                step = 1\n                following = actions[index + 1] if index + 1 < len(actions) else None\n                if isinstance(following, Buttons):\n                    markup = self._keyboard_expression(following)\n                    step = 2\n                self._lines.extend(self._reply_lines(str(node.params.get("text", "")),\n                                                     markup, depth))\n                index += step\n                continue\n\n            if isinstance(node, Buttons):\n                raise CodeGenError(\n                    "buttons must follow a send statement",\n                    line=node.line,\n                    hint=\'put `send "..."` directly before the buttons block\',\n                )\n\n            if isinstance(node, When):\n                self._lines.append(\n                    "{0}if {1}:".format(pad, _condition_expression(node.condition))\n                )\n                self._emit_actions(node.then, depth + 1)\n                if node.orelse:\n                    self._lines.append("{0}else:".format(pad))\n                    self._emit_actions(node.orelse, depth + 1)\n                index += 1\n                continue\n\n            if isinstance(node, Action):\n                self._emit_action(node, depth)\n                index += 1\n                continue\n\n            raise CodeGenError(\n                "cannot compile this statement", line=getattr(node, "line", 1)\n            )\n\n    def _emit_action(self, node: Action, depth: int) -> None:\n        pad = INDENT * depth\n        kind = node.kind\n        params = node.params\n        spec = ACTIONS_BY_KIND.get(kind)\n        if spec is None:\n            raise CodeGenError("unknown action {0!r}".format(kind), line=node.line)\n\n        if kind in _MEDIA_ACTIONS:\n            call_args: List[str] = []\n            method = spec.method\n            if kind == "send_dice":\n                call_args.append("emoji={0}".format(_literal(str(params.get("emoji", "🎲")))))\n            elif kind == "send_location":\n                call_args.append("latitude={0}".format(_number(params.get("latitude", 0))))\n                call_args.append("longitude={0}".format(_number(params.get("longitude", 0))))\n            elif kind == "send_contact":\n                call_args.append(_literal(str(params.get("phone", ""))))\n                call_args.append(_literal(str(params.get("first_name", ""))))\n            else:\n                call_args.append(_literal(str(params.get(spec.payload, ""))))\n                caption = str(params.get("caption", "") or "")\n                if spec.caption and caption:\n                    call_args.append("caption={0}".format(_literal(caption)))\n            self._lines.append("{0}await media(event, {1}, {2})".format(\n                pad, _literal(method), ", ".join(call_args)))\n            return\n\n        if kind == "send_poll":\n            options = [str(item) for item in (params.get("options") or ())]\n            self._lines.append("{0}await send_poll(".format(pad))\n            self._lines.append("{0}event,".format(INDENT * (depth + 1)))\n            self._lines.append("{0}{1},".format(INDENT * (depth + 1),\n                                                _literal(str(params.get("question", "")))))\n            self._lines.append("{0}({1}),".format(INDENT * (depth + 1),\n                                                  ", ".join(_literal(item) for item in options)))\n            self._lines.append("{0})".format(pad))\n            return\n\n        if kind == "delete":\n            self._lines.append("{0}await remove(event)".format(pad))\n            return\n        if kind == "typing":\n            self._lines.append("{0}await typing(event)".format(pad))\n            return\n        if kind == "delay":\n            self._lines.append("{0}await delay({1})".format(\n                pad, _number(params.get("seconds", 1))))\n            return\n        if kind == "nothing":\n            self._lines.append("{0}pass  # ничего".format(pad))\n            return\n        if kind == "edit_text":\n            self._lines.append("{0}await edit_text(event, {1})".format(\n                pad, _literal(str(params.get("text", "")))))\n            return\n        if kind == "answer_callback":\n            text = str(params.get("text", "") or "")\n            alert = bool(params.get("alert"))\n            args = [_literal(text)]\n            if alert:\n                args.append("alert=True")\n            self._lines.append("{0}await answer_callback(event, {1})".format(\n                pad, ", ".join(args)))\n            return\n        if kind == "pin":\n            silent = bool(params.get("silent"))\n            self._lines.append("{0}await pin(event{1})".format(\n                pad, ", silent=True" if silent else ""))\n            return\n        if kind == "unpin":\n            self._lines.append("{0}await unpin(event)".format(pad))\n            return\n        if kind in ("ban_user", "unban_user"):\n            user_id = int(params.get("user_id") or 0)\n            args = ["event"] + ([str(user_id)] if user_id else [])\n            self._lines.append("{0}await {1}({2})".format(pad, kind, ", ".join(args)))\n            return\n        if kind == "mute_user":\n            user_id = int(params.get("user_id") or 0)\n            minutes = params.get("minutes", 10)\n            args = ["event"]\n            if user_id or minutes != 10:\n                args.append(str(user_id))\n            if minutes != 10:\n                args.append(_number(minutes))\n            self._lines.append("{0}await mute_user({1})".format(pad, ", ".join(args)))\n            return\n        if kind == "set_state":\n            self._lines.append("{0}await state.set_state(Form.{1})".format(\n                pad, params.get("state")))\n            return\n        if kind == "clear_state":\n            self._lines.append("{0}await state.clear()".format(pad))\n            return\n        if kind == "log":\n            self._lines.append("{0}logging.info({1})".format(\n                pad, _literal(str(params.get("text", "")))))\n            return\n        if kind == "inline_result":\n            description = str(params.get("description", "") or "")\n            args = [_literal(str(params.get("title", ""))),\n                    _literal(str(params.get("text", "")))]\n            if description:\n                args.append(_literal(description))\n            self._lines.append("{0}await inline_result(event, {1})".format(\n                pad, ", ".join(args)))\n            return\n        raise CodeGenError("cannot compile {0!r}".format(kind), line=node.line)\n\n    # ------------------------------------------------------------ formatting\n    def _reply_lines(self, text: str, markup: Optional[str], depth: int) -> List[str]:\n        pad = INDENT * depth\n        inner = INDENT * (depth + 1)\n        if markup is None:\n            single = "{0}await reply(event, {1})".format(pad, _literal(text))\n            return [single] if len(single) <= LINE_WIDTH else [\n                "{0}await reply(".format(pad),\n                "{0}event,".format(inner),\n                "{0}{1},".format(inner, _literal(text)),\n                "{0})".format(pad),\n            ]\n\n        if len(pad) + len(markup) + 20 <= LINE_WIDTH and "\\n" not in markup:\n            return [\n                "{0}await reply(".format(pad),\n                "{0}event,".format(inner),\n                "{0}{1},".format(inner, _literal(text)),\n                "{0}{1},".format(inner, markup),\n                "{0})".format(pad),\n            ]\n\n        lines = [\n            "{0}await reply(".format(pad),\n            "{0}event,".format(inner),\n            "{0}{1},".format(inner, _literal(text)),\n        ]\n        lines.extend(self._wrapped_markup(markup, depth + 1))\n        lines.append("{0})".format(pad))\n        return lines\n\n    def _wrapped_markup(self, markup: str, depth: int) -> List[str]:\n        pad = INDENT * depth\n        if len(pad) + len(markup) + 1 <= LINE_WIDTH:\n            return ["{0}{1},".format(pad, markup)]\n\n        call, args = markup.split("(", 1)\n        args = args.rsplit(")", 1)[0]\n        pieces = _split_arguments(args)\n        lines = ["{0}{1}(".format(pad, call)]\n        for piece in pieces:\n            lines.append("{0}{1},".format(INDENT * (depth + 1), piece))\n        lines.append("{0}),".format(pad))\n        return lines\n\n    def _keyboard_expression(self, node: Buttons) -> str:\n        if node.style == "reply":\n            pairs = []\n            for button in node.items:\n                kind_name = button.kind if button.kind in ("contact", "location") else "text"\n                pairs.append("({0}, {1})".format(_literal(button.label), _literal(kind_name)))\n            return "keyboard({0})".format(", ".join(pairs))\n        triples = []\n        for button in node.items:\n            if button.kind in ("url", "web_app") and button.target:\n                triples.append("({0}, {1}, {2})".format(\n                    _literal(button.label), _literal(button.target), _literal(button.kind)))\n            elif button.kind == "command" and button.target:\n                triples.append("({0}, {1}, {2})".format(\n                    _literal(button.label), _literal(button.target), \'"command"\'))\n            else:\n                raise CodeGenError(\n                    "inline buttons need a target",\n                    line=button.line,\n                    hint=\'write `"Help" -> /help` or `"Site" -> url "https://example.com"`\',\n                )\n        return "inline({0})".format(", ".join(triples))\n\n    # ------------------------------------------------------------------ footer\n    def _footer(self) -> List[str]:\n        lines: List[str] = []\n        lines.append("async def main() -> None:")\n        lines.append("{0}logging.basicConfig(level=logging.INFO)".format(INDENT))\n        lines.append("{0}if not BOT_TOKEN or BOT_TOKEN == \\"PASTE_YOUR_TOKEN\\":".format(INDENT))\n        lines.append("{0}    raise SystemExit(".format(INDENT))\n        lines.append("{0}        \\"No bot token: put one in the .tg file, pass "\n                     "--token, or set TG_BOT_TOKEN.\\"".format(INDENT))\n        lines.append("{0}    )".format(INDENT))\n        lines.append("")\n        lines.append("{0}session = None".format(INDENT))\n        lines.append("{0}if PROXY:".format(INDENT))\n        lines.append("{0}    try:".format(INDENT))\n        lines.append("{0}        import aiohttp_socks  # noqa: F401".format(INDENT))\n        lines.append("{0}    except ImportError:".format(INDENT))\n        lines.append("{0}        raise SystemExit(".format(INDENT))\n        lines.append("{0}            \\"Proxy needs the aiohttp-socks package: "\n                     "pip install aiohttp-socks\\"".format(INDENT))\n        lines.append("{0}        )".format(INDENT))\n        lines.append("{0}    session = AiohttpSession(proxy=PROXY)".format(INDENT))\n        lines.append("{0}bot = Bot(token=BOT_TOKEN, session=session)".format(INDENT))\n        lines.append("")\n        lines.append("{0}try:".format(INDENT))\n        if self.usage.use_webhook:\n            lines.append("{0}    if WEBHOOK_URL:".format(INDENT))\n            lines.append("{0}        await serve_webhook(bot)".format(INDENT))\n            lines.append("{0}    else:".format(INDENT))\n            lines.append("{0}        await dp.start_polling(bot)".format(INDENT))\n        else:\n            lines.append("{0}    await dp.start_polling(bot)".format(INDENT))\n        lines.append("{0}except (TelegramNetworkError, OSError, "\n                     "ProxyConnectionError) as error:".format(INDENT))\n        lines.append("{0}    raise SystemExit(".format(INDENT))\n        lines.append(r\'{0}        "Нет связи с api.telegram.org ({{0}}).\\n"\'.format(INDENT))\n        lines.append(r\'{0}        "Скорее всего Telegram заблокирован в этой сети. \'\n                     r\'Варианты:\\n"\'.format(INDENT))\n        lines.append(r\'{0}        "  1) включить VPN для всей системы;\\n"\'.format(INDENT))\n        lines.append(r\'{0}        "  2) указать прокси: bot proxy \'\n                     r\'\\"socks5://127.0.0.1:1080\\" или TG_PROXY=...\\n"\'.format(INDENT))\n        lines.append(r\'{0}        "     и поставить пакет: pip install aiohttp-socks"\'\n                     r".format(error)".format(INDENT))\n        lines.append("{0}    )".format(INDENT))\n        lines.append("{0}finally:".format(INDENT))\n        lines.append("{0}    await bot.session.close()".format(INDENT))\n        if self.usage.use_webhook:\n            lines.append("")\n            lines.append("")\n            lines.extend(_webhook_body(self.bot.webhook_path))\n        lines.append("")\n        lines.append("")\n        lines.append(\'if __name__ == "__main__":\')\n        lines.append("{0}asyncio.run(main())".format(INDENT))\n        return lines\n\n\n_MEDIA_ACTIONS = {\n    "send_photo", "send_document", "send_video", "send_animation", "send_audio",\n    "send_voice", "send_sticker", "send_location", "send_contact", "send_dice",\n}\n\n# Handlers are written in a fixed order, so the generated file reads top to\n# bottom: commands, then plain text, then the narrower content types, then the\n# catch-all. aiogram calls the first matching handler, so this order is what\n# makes a specific handler win over `on any:`.\n_OBSERVER_ORDER = {\n    "message": 0,\n    "edited_message": 1,\n    "callback_query": 2,\n    "inline_query": 3,\n    "channel_post": 4,\n    "chat_member": 5,\n    "my_chat_member": 6,\n    "poll_answer": 7,\n}\n\n_KIND_ORDER = {\n    "command": 0,\n    "text": 1,\n    "state": 2,\n    "callback": 3,\n    "edited": 4,\n    "photo": 5,\n    "sticker": 6,\n    "voice": 7,\n    "video": 8,\n    "video_note": 9,\n    "audio": 10,\n    "document": 11,\n    "animation": 12,\n    "location": 13,\n    "contact": 14,\n    "poll": 15,\n    "dice": 16,\n    "new_members": 17,\n    "left_member": 18,\n    "pinned": 19,\n    "web_app_data": 20,\n    "any": 30,\n}\n\n\ndef _join_filters(parts: Sequence[str]) -> str:\n    parts = [part for part in parts if part]\n    if not parts:\n        return ""\n    if len(parts) == 1:\n        return parts[0]\n    return " & ".join("({0})".format(part) for part in parts)\n\n\ndef _webhook_body(path: str) -> List[str]:\n    return \'\'\'async def serve_webhook(bot: Bot) -> None:\n    # Webhook mode: the bot listens on PORT (default 8080) and Telegram pushes.\n    from aiohttp import web\n    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application\n\n    port = int(os.environ.get("PORT", "8080"))\n    await bot.set_webhook(WEBHOOK_URL, secret_token=WEBHOOK_SECRET or None)\n    app = web.Application()\n    handler = SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET or None)\n    handler.register(app, path=WEBHOOK_PATH)\n    setup_application(app, dp, bot=bot)\n    runner = web.AppRunner(app)\n    await runner.setup()\n    await web.TCPSite(runner, "0.0.0.0", port).start()\n    logging.info("webhook %s is listening on port %s", WEBHOOK_PATH, port)\n    await asyncio.Event().wait()\'\'\'.format(path=path).splitlines()\n\n\ndef _split_arguments(text: str) -> List[str]:\n    # Split "(\'a\', \'/a\'), (\'b\', \'/b\')" on top-level commas only.\n    pieces: List[str] = []\n    depth = 0\n    current: List[str] = []\n    quote = ""\n    for char in text:\n        if quote:\n            current.append(char)\n            if char == quote:\n                quote = ""\n            continue\n        if char in "\'\\"":\n            quote = char\n            current.append(char)\n            continue\n        if char in "([{":\n            depth += 1\n        elif char in ")]}":\n            depth -= 1\n        if char == "," and depth == 0:\n            pieces.append("".join(current).strip())\n            current = []\n            continue\n        current.append(char)\n    tail = "".join(current).strip()\n    if tail:\n        pieces.append(tail)\n    return pieces\n\n\ndef generate(bot: BotSpec, embed_token: bool = True) -> str:\n    # Return aiogram 3 source code for a parsed bot.\n    #\n    # embed_token=False keeps the secret out of the generated file: the bot then\n    # reads TG_BOT_TOKEN at startup, which is what the CLI does by default.\n    return _Emitter(bot, embed_token=embed_token).generate()\n\n\ndef compile_source(source: str, filename: str = "<dsl>", embed_token: bool = True) -> str:\n    # Parse DSL text and return generated Python code.\n    from .parser import parse\n\n    return generate(parse(source, filename), embed_token=embed_token)\n',
    "src/tgblocks/dsl/parser.py": '# Parser for the tgblocks indentation-based DSL.\n#\n# The grammar is deliberately boring:\n#\n#     bot token "123456:ABC"\n#     bot name "Hello bot"\n#\n#     on /start:\n#         send "Hello!"\n#         buttons:\n#             "Help" -> /help\n#             "Docs" -> url "https://example.com"\n#\n#     on message:\n#         when text contains "hi":\n#             send "Hi there!"\n#         else:\n#             send "Try /help"\n#\n#     on message "hi", "hello":        # only these exact texts\n#         send "Hi there!"\n#\n# Everything a bot can do is described in tgblocks.model; this module only turns\n# text into that AST. A new action or event therefore costs nothing here.\n#\n# Every structural error becomes a DSLParseError that carries the line number,\n# the offending source line and a short hint - beginners should never see a\n# traceback from this module.\n\nfrom __future__ import annotations\n\nimport ast\nimport re\nfrom dataclasses import dataclass, field\nfrom pathlib import Path\nfrom typing import Any, Dict, List, NoReturn, Optional, Tuple\n\nfrom ..model import (\n    ACTIONS_BY_KIND,\n    BindError,\n    EventSpec,\n    action_for,\n    bind_arguments,\n    coerce,\n    event_for,\n)\n\n__all__ = [\n    "Action",\n    "BotSpec",\n    "Button",\n    "Buttons",\n    "Condition",\n    "DSLParseError",\n    "Handler",\n    "When",\n    "parse",\n    "parse_file",\n    "validate",\n]\n\n# Which action families a handler of this event can run. A command handler also\n# answers its own inline button, so it can do callback things too.\nFAMILY_EXTRA = {"command": ("callback",)}\n\n\nclass DSLParseError(Exception):\n    # A syntax or semantic error inside a .tg file.\n\n    def __init__(\n        self,\n        message: str,\n        line: int = 1,\n        column: int = 1,\n        source_line: str = "",\n        hint: str = "",\n    ) -> None:\n        super().__init__(message)\n        self.message = message\n        self.line = line\n        self.column = column\n        self.source_line = source_line\n        self.hint = hint\n\n    def render(self, filename: str = "<dsl>") -> str:\n        # Compiler-style diagnostic with a caret pointing at the column.\n        head = "{0}:{1}:{2}: error: {3}".format(filename, self.line, self.column, self.message)\n        if not self.source_line:\n            text = head\n        else:\n            gutter = "{0:>4} | ".format(self.line)\n            caret = " " * (len(gutter) + max(self.column - 1, 0)) + "^"\n            text = "\\n".join([head, gutter + self.source_line, caret])\n        if self.hint:\n            text += "\\n  hint: {0}".format(self.hint)\n        return text\n\n    def __str__(self) -> str:\n        return self.render()\n\n\n# --------------------------------------------------------------------- the AST\n@dataclass\nclass Button:\n    label: str\n    kind: str = "none"  # "command" | "url" | "web_app" | "contact" | "location" | "none"\n    target: Optional[str] = None\n    line: int = 0\n\n\n@dataclass\nclass Buttons:\n    style: str  # "inline" | "reply"\n    items: List[Button]\n    line: int = 0\n\n\n@dataclass\nclass Action:\n    # One leaf action: its kind comes from the catalogue, its params are already\n    # coerced (numbers are numbers, flags are bools, lists are tuples).\n    kind: str\n    params: Dict[str, Any] = field(default_factory=dict)\n    line: int = 0\n\n    def get(self, name: str, default: Any = "") -> Any:\n        value = self.params.get(name, default)\n        return default if value is None else value\n\n    @property\n    def text(self) -> str:\n        return str(self.get("text", ""))\n\n\n@dataclass\nclass Condition:\n    op: str  # == | != | contains | startswith | endswith\n    value: str\n    line: int = 0\n    values: Tuple[str, ...] = ()\n    # What is compared: the message text, or the number the interactive emoji\n    # landed on (`when dice == 6`).\n    source: str = "text"\n\n\n@dataclass\nclass When:\n    condition: Condition\n    then: List[object]\n    orelse: List[object]\n    line: int = 0\n\n\n@dataclass\nclass Handler:\n    kind: str  # a catalogue event kind: command | text | photo | ... | callback | state\n    actions: List[object]\n    params: Dict[str, Any] = field(default_factory=dict)\n    line: int = 0\n\n    # Convenience views used by the converters and the tests.\n    @property\n    def command(self) -> Optional[str]:\n        return self.params.get("command") or None\n\n    @property\n    def patterns(self) -> Tuple[str, ...]:\n        return tuple(self.params.get("patterns") or ())\n\n    @property\n    def data(self) -> str:\n        return str(self.params.get("data") or "")\n\n    @property\n    def state(self) -> str:\n        return str(self.params.get("state") or "")\n\n    @property\n    def chat(self) -> str:\n        return str(self.params.get("chat") or "")\n\n    @property\n    def from_user(self) -> int:\n        return int(self.params.get("from_user") or 0)\n\n    @property\n    def regex(self) -> str:\n        return str(self.params.get("regex") or "")\n\n\n@dataclass\nclass BotSpec:\n    token: Optional[str] = None\n    name: str = "tgblocks bot"\n    proxy: str = ""\n    handlers: List[Handler] = field(default_factory=list)\n    token_line: int = 0\n    # FSM: the dialogue steps, in declaration order.\n    states: List[str] = field(default_factory=list)\n    # Webhook mode: when set, the generated bot serves it instead of polling.\n    webhook: str = ""\n    webhook_path: str = "/webhook"\n    webhook_secret: str = ""\n    # Non-fatal findings (a button that leads nowhere): reported by `tgblocks\n    # check` and in the editor, but never blocks a build - the bot still runs.\n    warnings: List[str] = field(default_factory=list)\n\n\n@dataclass\nclass _Token:\n    line: int\n    indent: int\n    text: str\n    raw: str\n\n\n_DIRECTIVE_RE = re.compile(r"^bot\\s+(token|name|proxy|webhook|webhook_path|webhook_secret)\\s+(.+)$")\n_ON_RE = re.compile(r"^on\\s+(.+?)\\s*:\\s*$")\n_SEND_RE = re.compile(r"^send\\s+(.+)$")\n_BUTTONS_RE = re.compile(r"^buttons(?:\\s+(inline|reply))?\\s*:\\s*$")\n_WHEN_RE = re.compile(r"^(?:when|if)\\s+(.+?)\\s*:\\s*$")\n_COND_RE = re.compile(r"^(text|dice)\\s*(==|!=|contains|startswith|endswith)\\s+(.+)$")\n_DICE_OPS = ("==", "!=")\n_BUTTON_RE = re.compile(\n    r"^(\\"(?:[^\\"\\\\]|\\\\.)*\\"|\'(?:[^\'\\\\]|\\\\.)*\')(?:\\s*->\\s*(.+))?$"\n)\n_COMMAND_RE = re.compile(r"^/[A-Za-z0-9_]{1,32}$")\n_STATE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,31}$")\n\n# Every action keyword the DSL understands, including the aliases.\n_ACTION_WORDS = set(ACTIONS_BY_KIND)\nfor _alias in ("pass", "photo", "document", "video", "animation", "audio", "voice",\n               "sticker", "location", "contact", "poll", "dice", "alert", "state"):\n    _ACTION_WORDS.add(_alias)\n\n\ndef _tokenize(source: str) -> List[_Token]:\n    # Turn raw text into (line, indent, stripped text) triples, dropping blanks\n    # and full-line comments. Leading tabs are rejected: they break alignment.\n    tokens: List[_Token] = []\n    for line_number, raw in enumerate(source.splitlines(), start=1):\n        leading = raw[: len(raw) - len(raw.lstrip())]\n        if "\\t" in leading:\n            raise DSLParseError(\n                "tabs are not allowed for indentation",\n                line_number,\n                1,\n                raw,\n                "use spaces instead, 4 per level",\n            )\n        stripped = raw.strip()\n        if not stripped or stripped.startswith("#"):\n            continue\n        indent = len(raw) - len(raw.lstrip(" "))\n        tokens.append(_Token(line_number, indent, stripped, raw))\n    return tokens\n\n\ndef lex_arguments(text: str) -> List[Tuple[str, bool]]:\n    """Split `"a" b=1 "c d" 2` into [(value, is_bare)] pairs.\n\n    Quoted strings are unescaped with ast.literal_eval (so \\\\n works), bare words\n    stay bare. Commas that separate list items are dropped.\n    """\n    items: List[Tuple[str, bool]] = []\n    index = 0\n    length = len(text)\n    while index < length:\n        while index < length and text[index].isspace():\n            index += 1\n        if index >= length:\n            break\n        char = text[index]\n        if char in "\\"\'":\n            quote = char\n            start = index\n            index += 1\n            while index < length:\n                if text[index] == "\\\\":\n                    index += 2\n                    continue\n                if text[index] == quote:\n                    index += 1\n                    break\n                index += 1\n            raw = text[start:index]\n            try:\n                value = ast.literal_eval(raw)\n            except (SyntaxError, ValueError):\n                raise DSLParseError(\n                    "cannot read the text {0}".format(raw[:40]),\n                    hint="check that the closing quote is there and escapes are valid",\n                ) from None\n            if not isinstance(value, str):\n                raise DSLParseError("the value must be text")\n            items.append((value, False))\n            continue\n        start = index\n        while index < length and not text[index].isspace():\n            index += 1\n        word = text[start:index]\n        if word.strip(",") == "":\n            continue\n        items.append((word, True))\n    return items\n\n\ndef _unquote_single(raw: str) -> Optional[str]:\n    # `"text"` or `\'text\'` -> text; None when the value is not quoted.\n    text = raw.strip()\n    if len(text) < 2 or text[0] not in "\\"\'" or text[-1] != text[0]:\n        return None\n    try:\n        value = ast.literal_eval(text)\n    except (SyntaxError, ValueError):\n        return None\n    return value if isinstance(value, str) else None\n\n\nclass _Parser:\n    def __init__(self, source: str, filename: str = "<dsl>") -> None:\n        # Editors on Windows love to add a UTF-8 BOM: it is not part of the DSL.\n        source = source.lstrip("\\ufeff")\n        # DSL embedded in a Python string usually carries the indentation of the\n        # code around it: drop the common margin so both styles parse the same.\n        lines = source.splitlines()\n        margin = None\n        for line in lines:\n            if not line.strip():\n                continue\n            indent = len(line) - len(line.lstrip(" "))\n            margin = indent if margin is None else min(margin, indent)\n        if margin:\n            lines = [line[margin:] for line in lines]\n        source = "\\n".join(lines)\n        self.filename = filename\n        self.source_lines = source.splitlines()\n        self.tokens = _tokenize(source)\n        self.pos = 0\n\n    # ------------------------------------------------------------------ errors\n    def _fail(self, message: str, token: _Token, hint: str = "") -> NoReturn:\n        raw = ""\n        if 0 < token.line <= len(self.source_lines):\n            raw = self.source_lines[token.line - 1]\n        column = len(raw) - len(raw.lstrip(" ")) + 1 if raw else 1\n        raise DSLParseError(message, token.line, column, raw, hint)\n\n    def _fail_line(self, line: int, message: str, hint: str = "") -> NoReturn:\n        raw = self.source_lines[line - 1] if 0 < line <= len(self.source_lines) else ""\n        column = len(raw) - len(raw.lstrip(" ")) + 1 if raw else 1\n        raise DSLParseError(message, line, column, raw, hint)\n\n    def _unquote(self, raw: str, token: _Token, what: str = "text") -> str:\n        text = raw.strip()\n        if len(text) < 2 or text[0] not in "\\"\'" or text[-1] != text[0]:\n            self._fail(\n                "expected a quoted {0}".format(what),\n                token,\n                \'wrap the value in double quotes, for example: "Hello!"\',\n            )\n        value = _unquote_single(text)\n        if value is None:\n            self._fail(\n                "cannot read the {0}".format(what),\n                token,\n                "check that the closing quote is there and escapes such as \\\\n are valid",\n            )\n        return value\n\n    # ------------------------------------------------------------------- entry\n    def parse(self) -> BotSpec:\n        bot = BotSpec()\n        while self.pos < len(self.tokens):\n            token = self.tokens[self.pos]\n            if token.indent != 0:\n                self._fail(\n                    "unexpected indentation",\n                    token,\n                    "this line is indented, but no block is open here",\n                )\n            if token.text.startswith("bot "):\n                self._parse_directive(bot, token)\n            elif token.text.startswith("on "):\n                bot.handlers.append(self._parse_handler(token, bot))\n            elif token.text.startswith("state ") and not token.text.endswith(":"):\n                name = token.text[len("state "):].strip()\n                self._add_state(bot, name, token)\n                self.pos += 1\n            elif token.text.startswith("else"):\n                self._fail(\n                    "\'else\' without \'when\'",\n                    token,\n                    "put \'else:\' directly under a \'when ...:\' line",\n                )\n            else:\n                self._fail(\n                    "unknown statement: {0!r}".format(token.text),\n                    token,\n                    \'expected `bot token "..."`, `bot name "..."` or `on /command:`\',\n                )\n\n        if bot.token is None:\n            self._fail_line(\n                1,\n                "the bot token is missing",\n                \'add `bot token "123456:ABC"` as the first line of the file\',\n            )\n        if not bot.handlers:\n            self._fail_line(\n                1,\n                "the bot has no handlers",\n                "add at least one block such as `on /start:`",\n            )\n        self._check(bot)\n        return bot\n\n    def _check(self, bot: BotSpec) -> None:\n        validate(bot, fail=lambda message, line, hint: self._fail_line(line, message, hint))\n        # A handler for a dialogue step needs that step to exist.\n        for handler in bot.handlers:\n            state = handler.state\n            if handler.kind == "state" and state and state not in bot.states:\n                self._fail_line(\n                    handler.line,\n                    "unknown state {0!r}".format(state),\n                    "declare it first: `state {0}`".format(state),\n                )\n\n    def _add_state(self, bot: BotSpec, name: str, token: _Token) -> None:\n        if not _STATE_RE.match(name or ""):\n            self._fail(\n                "invalid state name {0!r}".format(name),\n                token,\n                "use letters, digits and _ (for example: `state order`)",\n            )\n        if name in bot.states:\n            self._fail(\n                "duplicate state {0!r}".format(name),\n                token,\n                "each dialogue step is declared once",\n            )\n        bot.states.append(name)\n\n    # --------------------------------------------------------------- statements\n    def _parse_directive(self, bot: BotSpec, token: _Token) -> None:\n        match = _DIRECTIVE_RE.match(token.text)\n        if match is None:\n            self._fail(\n                "unsupported bot directive",\n                token,\n                \'only `bot token`, `bot name`, `bot proxy` and `bot webhook` exist\',\n            )\n        key = match.group(1)\n        labels = {"token": "token", "name": "bot name", "proxy": "proxy URL",\n                  "webhook": "webhook URL", "webhook_path": "webhook path",\n                  "webhook_secret": "webhook secret"}\n        value = self._unquote(match.group(2), token, labels[key])\n        # A pasted value often carries a stray space or tab: it is never\n        # meaningful in a token, a URL or a path, and it silently breaks them.\n        if key != "name":\n            value = value.strip()\n        if key == "proxy":\n            if not value.startswith(("socks5://", "socks4://", "http://", "https://")):\n                self._fail(\n                    "proxy must start with socks5://, socks4://, http:// or https://",\n                    token,\n                    \'for example: bot proxy "socks5://127.0.0.1:1080"\',\n                )\n            bot.proxy = value\n        elif key == "webhook":\n            if not value.startswith(("http://", "https://")):\n                self._fail(\n                    "the webhook URL must start with http:// or https://",\n                    token,\n                    \'for example: bot webhook "https://example.com/webhook"\',\n                )\n            bot.webhook = value\n        elif key == "webhook_path":\n            if not value.startswith("/"):\n                self._fail("the webhook path must start with /", token,\n                           \'for example: bot webhook_path "/hook"\')\n            bot.webhook_path = value\n        elif key == "webhook_secret":\n            bot.webhook_secret = value\n        elif key == "token":\n            if bot.token is not None:\n                self._fail(\n                    "duplicate `bot token`", token, "the token can only be declared once"\n                )\n            bot.token = value\n            bot.token_line = token.line\n        else:\n            bot.name = value\n        self.pos += 1\n\n    # ------------------------------------------------------------------- events\n    def _parse_handler(self, token: _Token, bot: Optional[BotSpec] = None) -> Handler:\n        match = _ON_RE.match(token.text)\n        if match is None:\n            self._fail(\n                "invalid event declaration",\n                token,\n                "write `on /command:` or `on message:`",\n            )\n        target = match.group(1).strip()\n        self.pos += 1\n        actions = self._parse_block(token)\n        try:\n            items = lex_arguments(target)\n        except DSLParseError:\n            self._fail("cannot read the event", token, "write `on /command:`")\n        if not items:\n            self._fail("empty event", token, "write `on /command:` or `on message:`")\n\n        first_value, first_bare = items[0]\n        rest = items[1:]\n\n        # on /start: - the command itself is the target.\n        if first_bare and first_value.startswith("/"):\n            if not _COMMAND_RE.match(first_value):\n                self._fail("invalid command {0!r}".format(first_value), token)\n            params = self._bind_event(self._event("command"), rest, token)\n            params["command"] = first_value\n            return Handler(kind="command", actions=actions, params=params, line=token.line)\n\n        spec = event_for(first_value) if first_bare else None\n        if spec is None and first_bare is False:\n            # on "a", "b": with no event word means "exactly these texts".\n            spec = event_for("text")\n            rest = items\n        if spec is None:\n            self._fail(\n                "invalid event {0!r}".format(first_value),\n                token,\n                "use `on /command:`, `on message:`, `on photo:`, `on callback:`, "\n                "`on state <step>:` or `on any:`",\n            )\n        params = self._bind_event(spec, rest, token)\n        if spec.key_param == "command":\n            command = str(params.get("command") or "").strip()\n            if not _COMMAND_RE.match(command):\n                self._fail(\n                    "the command must look like /start",\n                    token,\n                    \'write `on /start:` instead of `on command "start":`\',\n                )\n        if spec.kind == "state":\n            state = str(params.get("state") or "").strip()\n            if not state:\n                self._fail("a state handler needs a step", token,\n                           "write `on state order:` after `state order`")\n        return Handler(kind=spec.kind, actions=actions, params=params, line=token.line)\n\n    def _event(self, kind: str) -> EventSpec:\n        spec = event_for(kind)\n        assert spec is not None, kind\n        return spec\n\n    def _bind_event(self, spec: EventSpec, items, token: _Token) -> Dict[str, Any]:\n        try:\n            return bind_arguments(spec, items)\n        except BindError as error:\n            self._fail(error.message, token, error.hint or "")\n\n    # ------------------------------------------------------------------- blocks\n    def _parse_block(self, header: _Token) -> List[object]:\n        if self.pos >= len(self.tokens) or self.tokens[self.pos].indent <= header.indent:\n            self._fail(\n                "expected an indented block",\n                header,\n                \'indent the block by 4 spaces, for example:     send "Hi"\',\n            )\n        block_indent = self.tokens[self.pos].indent\n        nodes: List[object] = []\n        while self.pos < len(self.tokens):\n            token = self.tokens[self.pos]\n            if token.indent < block_indent:\n                break\n            if token.indent > block_indent:\n                self._fail(\n                    "unexpected indentation",\n                    token,\n                    "this line is deeper than the block it belongs to",\n                )\n            nodes.append(self._parse_statement(token, block_indent))\n        return nodes\n\n    def _parse_statement(self, token: _Token, indent: int) -> object:\n        text = token.text\n\n        if text == "else:" or text.startswith("else "):\n            self._fail(\n                "\'else\' without \'when\'",\n                token,\n                "put `else:` under a `when ...:` line at the same indentation",\n            )\n\n        if text == "send" or text.startswith("send "):\n            return self._parse_send(token)\n\n        if text.startswith("buttons"):\n            return self._parse_buttons_block(token)\n\n        if text.startswith("when ") or text.startswith("if "):\n            return self._parse_when(token, indent)\n\n        word, _, rest = text.partition(" ")\n        word = word.rstrip(":")\n        spec = action_for(word)\n        if spec is None:\n            self._fail(\n                "unknown statement: {0!r}".format(text),\n                token,\n                "inside a block use `send`, `buttons`, `when`, `delete`, "\n                "`send_photo`, `delay`, `set_state` or `pass`",\n            )\n        if spec.kind == "otherwise":\n            self._fail(\n                "\'else\' without \'when\'",\n                token,\n                "put `else:` under a `when ...:` line at the same indentation",\n            )\n        if spec.kind == "when":\n            self._fail("use `when text contains \\"...\\":`", token,\n                       "the short form is `when <condition>:`")\n        try:\n            params = bind_arguments(spec, lex_arguments(rest))\n        except BindError as error:\n            self._fail(error.message, token, error.hint or "")\n        self.pos += 1\n        return Action(kind=spec.kind, params=params, line=token.line)\n\n    def _parse_send(self, token: _Token) -> Action:\n        match = _SEND_RE.match(token.text)\n        if match is None:\n            self._fail("missing text after `send`", token, \'example: send "Hello!"\')\n        value = self._unquote(match.group(1), token)\n        self.pos += 1\n        return Action(kind="send", params={"text": value}, line=token.line)\n\n    def _parse_when(self, token: _Token, indent: int) -> When:\n        match = _WHEN_RE.match(token.text)\n        if match is None:\n            self._fail("invalid condition", token, \'example: `when text == "hi":`\')\n        condition = self._parse_condition(match.group(1), token)\n        self.pos += 1\n        then = self._parse_block(token)\n        orelse: List[object] = []\n        if self.pos < len(self.tokens):\n            following = self.tokens[self.pos]\n            if following.indent == indent and following.text == "else:":\n                self.pos += 1\n                orelse = self._parse_block(following)\n        return When(condition=condition, then=then, orelse=orelse, line=token.line)\n\n    def _parse_buttons_block(self, token: _Token) -> Buttons:\n        match = _BUTTONS_RE.match(token.text)\n        if match is None:\n            self._fail(\n                "invalid buttons block",\n                token,\n                "write `buttons:` for inline buttons or `buttons reply:` for a keyboard",\n            )\n        style = match.group(1) or "inline"\n        self.pos += 1\n        return Buttons(style=style, items=self._parse_buttons(token, style), line=token.line)\n\n    def _parse_buttons(self, header: _Token, style: str) -> List[Button]:\n        if self.pos >= len(self.tokens) or self.tokens[self.pos].indent <= header.indent:\n            self._fail(\n                "the buttons block is empty",\n                header,\n                \'add a row such as `"Help" -> /help`\',\n            )\n        item_indent = self.tokens[self.pos].indent\n        items: List[Button] = []\n        while self.pos < len(self.tokens):\n            token = self.tokens[self.pos]\n            if token.indent < item_indent:\n                break\n            if token.indent > item_indent:\n                self._fail("unexpected indentation", token, "each button sits on its own line")\n            items.append(self._parse_button(token, style))\n            self.pos += 1\n        return items\n\n    def _parse_button(self, token: _Token, style: str) -> Button:\n        match = _BUTTON_RE.match(token.text)\n        if match is None:\n            self._fail(\n                "invalid button",\n                token,\n                \'write `"Label" -> /command`, `"Label" -> url "https://..."` \'\n                \'or plain `"Label"` for reply buttons\',\n            )\n        label = self._unquote(match.group(1), token, "button label")\n        raw_target = (match.group(2) or "").strip()\n        button = Button(label=label, line=token.line)\n        if not raw_target:\n            return button\n        if style == "reply":\n            # Reply buttons can ask for a phone number or a location.\n            if raw_target in ("contact", "location"):\n                button.kind = raw_target\n                return button\n            self._fail(\n                "reply buttons cannot have a target",\n                token,\n                \'the label itself is sent as text, so drop the `-> ...` part \'\n                "(or use `-> contact` / `-> location`)",\n            )\n        if raw_target.startswith("url"):\n            url = self._unquote(raw_target[3:], token, "URL")\n            if not url.startswith(("http://", "https://")):\n                self._fail("URL buttons must start with http:// or https://", token)\n            button.kind = "url"\n            button.target = url\n        elif raw_target.startswith("web_app"):\n            url = self._unquote(raw_target[len("web_app"):], token, "URL")\n            if not url.startswith("https://"):\n                self._fail("web app buttons need an https:// URL", token)\n            button.kind = "web_app"\n            button.target = url\n        elif raw_target.startswith("/"):\n            if not _COMMAND_RE.match(raw_target):\n                self._fail("invalid command {0!r}".format(raw_target), token)\n            button.kind = "command"\n            button.target = raw_target\n        else:\n            self._fail(\n                "invalid button target {0!r}".format(raw_target),\n                token,\n                \'use `-> /command`, `-> url "https://..."` or `-> web_app "https://..."`\',\n            )\n        return button\n\n    def _parse_condition(self, text: str, token: _Token) -> Condition:\n        extra = []\n        if ";" in text:\n            chunks = text.split(";")\n            text = chunks[0]\n            for chunk in chunks[1:]:\n                chunk = chunk.strip()\n                if not (chunk.startswith(\'"\') or chunk.startswith("\'")):\n                    self._fail(\n                        "each extra condition value must be a quoted string",\n                        token,\n                        \'write when text contains "a";"b":\',\n                    )\n                extra.append(self._unquote(chunk, token, "comparison value"))\n        match = _COND_RE.match(text.strip())\n        if match is None:\n            self._fail(\n                "unsupported condition",\n                token,\n                \'use `text == "..."`, `text contains "..."` or `dice == 6`\',\n            )\n        source = match.group(1)\n        op = match.group(2)\n        if source == "dice":\n            if op not in _DICE_OPS:\n                self._fail(\n                    "для интерактивного эмодзи подходят только == и !=",\n                    token,\n                    \'сравни число, которое выпало: `when dice == 6:`\',\n                )\n            raw = match.group(3).strip()\n            if not raw.lstrip("-").isdigit():\n                self._fail(\n                    "для интерактивного эмодзи нужно число",\n                    token,\n                    \'кубик даёт 1-6, дартс - 1-6, слоты - 1-64: `when dice == 6:`\',\n                )\n            return Condition(op=op, value=raw, line=token.line, source="dice")\n        # Several values mean "any of them": when text contains "a", "b":\n        parts = [part for part in _split_items(match.group(3)) if part]\n        if not parts:\n            self._fail(\n                "the condition has no value",\n                token,\n                \'add the text to compare with, for example: when text contains "hi"\',\n            )\n        value = self._unquote(parts[0], token, "comparison value")\n        for part in parts[1:]:\n            extra.append(self._unquote(part, token, "comparison value"))\n        return Condition(op=op, value=value, line=token.line,\n                         values=tuple(extra), source=source)\n\n\ndef _split_items(text: str) -> List[str]:\n    # Split on top-level commas, keeping quoted strings (and their commas) whole.\n    parts: List[str] = []\n    current: List[str] = []\n    quote = ""\n    escaped = False\n    for char in text:\n        if quote:\n            current.append(char)\n            if escaped:\n                escaped = False\n            elif char == "\\\\":\n                escaped = True\n            elif char == quote:\n                quote = ""\n            continue\n        if char in "\'\\"":\n            quote = char\n            current.append(char)\n            continue\n        if char == ",":\n            parts.append("".join(current).strip())\n            current = []\n            continue\n        current.append(char)\n    tail = "".join(current).strip()\n    if tail:\n        parts.append(tail)\n    return parts\n\n\n# ---------------------------------------------------------------- shared checks\ndef _walk_actions(actions):\n    # Every action, including the ones nested inside `when` and inside a send.\n    for node in actions:\n        yield node\n        if isinstance(node, When):\n            for child in _walk_actions(node.then):\n                yield child\n            for child in _walk_actions(node.orelse):\n                yield child\n\n\ndef filter_signature(handler: Handler) -> Tuple[str, str]:\n    # Two handlers with the same signature can never both run: aiogram calls the\n    # first matching handler and returns. Everything that narrows the filter is\n    # part of the signature, so a chat=group variant is a different handler.\n    spec = event_for(handler.kind)\n    observer = spec.observer if spec else "message"\n    parts: List[str] = []\n    if spec and spec.filter:\n        parts.append(spec.filter)\n    if handler.kind == "command":\n        parts = [\'Command("{0}")\'.format((handler.command or "").lstrip("/"))]\n    elif handler.patterns:\n        parts.append("F.text.in_({0})".format(", ".join(handler.patterns)))\n    elif handler.kind == "callback" and handler.data:\n        parts.append(\'F.data == "{0}"\'.format(handler.data))\n    elif handler.kind == "state":\n        parts.append("StateFilter({0})".format(handler.state))\n    if handler.chat:\n        parts.append(\'F.chat.type == "{0}"\'.format(handler.chat))\n    if handler.from_user:\n        parts.append("F.from_user.id == {0}".format(handler.from_user))\n    if handler.regex:\n        parts.append(\'F.text.regexp("{0}")\'.format(handler.regex))\n    return observer, " & ".join(parts)\n\n\ndef validate(bot: BotSpec, fail=None) -> None:\n    # Semantic checks that both front ends share: a command may be handled once,\n    # two handlers may not claim the same filters, and a button must lead to a\n    # handler that exists (otherwise it looks fine in the editor and does nothing\n    # in Telegram).\n    def boom(message: str, line: int, hint: str = "") -> NoReturn:\n        if fail is not None:\n            fail(message, line, hint)\n        raise DSLParseError(message, line, 1, "", hint)\n\n    seen_commands = set()\n    seen_filters = {}\n    for handler in bot.handlers:\n        if handler.kind == "command":\n            if handler.command in seen_commands:\n                boom(\n                    "duplicate handler for {0}".format(handler.command),\n                    handler.line,\n                    "a command can be handled once; branch inside it with `when`",\n                )\n            seen_commands.add(handler.command)\n        key = filter_signature(handler)\n        if key in seen_filters:\n            boom(\n                "this handler would never run: line {0} already handles the same "\n                "messages".format(seen_filters[key]),\n                handler.line,\n                "merge them into one block, or branch inside it with `when`",\n            )\n        seen_filters[key] = handler.line\n\n    bot.warnings = []\n    commands = {\n        handler.command for handler in bot.handlers\n        if handler.kind == "command" and handler.command\n    }\n    for handler in bot.handlers:\n        for node in _walk_actions(handler.actions):\n            if isinstance(node, Buttons):\n                for button in node.items:\n                    if button.kind == "command" and button.target not in commands:\n                        bot.warnings.append(\n                            \'line {0}: button "{1}" calls {2}, but no `on {2}:` block \'\n                            "exists".format(button.line, button.label, button.target)\n                        )\n\n\ndef parse(source: str, filename: str = "<dsl>") -> BotSpec:\n    # Parse DSL text into a BotSpec tree.\n    return _Parser(source, filename).parse()\n\n\ndef parse_file(path: str) -> BotSpec:\n    # Read `path` as UTF-8 (BOM tolerated) and parse it.\n    file_path = Path(path)\n    try:\n        source = file_path.read_text(encoding="utf-8-sig")\n    except FileNotFoundError:\n        raise FileNotFoundError("DSL file not found: {0}".format(file_path)) from None\n    return parse(source, str(file_path))\n',
    "src/tgblocks/model.py": '# The feature catalogue: one description of everything a bot can do.\n#\n# Before this module every feature had to be written five times - in the DSL\n# parser, in the text parser, in two converters and in the code generator - and a\n# sixth time in each editor page. That is exactly why the three fronts drifted\n# apart. Now a feature is one ActionSpec or EventSpec here:\n#\n#   * the parsers accept it and check its arguments (dsl/parser, textlang);\n#   * the converters render it back to text and to the node/Blockly models;\n#   * the code generator has an emitter for its `emit` family;\n#   * /api/schema hands it to the editors, which build their palettes and\n#     property fields from it.\n#\n# Adding an aiogram method is therefore a catalogue entry plus one emitter.\n\nfrom __future__ import annotations\n\nimport ast\nfrom dataclasses import dataclass, field, replace\nfrom typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple\n\n# Action families: which events an action can run under, and which one it needs.\nMESSAGE = "message"      # Message, EditedMessage, ChannelPost: event.answer(...)\nCALLBACK = "callback"    # CallbackQuery: event.message.answer(...) + event.answer()\nCHAT = "chat"            # ChatMemberUpdated: event.bot.send_message(event.chat.id, ...)\nINLINE = "inline"        # InlineQuery: event.answer(results=[...])\nALL_EVENTS = (MESSAGE, CALLBACK, CHAT)\n\n\nclass BindError(ValueError):\n    """An action\'s arguments do not fit its description."""\n\n    def __init__(self, message: str, hint: str = "") -> None:\n        super().__init__(message)\n        self.message = message\n        self.hint = hint\n\n\n@dataclass(frozen=True)\nclass Param:\n    name: str\n    label: str\n    kind: str = "text"       # text | multiline | number | bool | choice | values | state\n    default: Any = ""\n    choices: Tuple[Tuple[str, str], ...] = ()\n    hint: str = ""\n    required: bool = False\n    # Hidden params are parsed, compiled and converted like any other, but the\n    # editors do not offer a field for them: the same job is done better by a\n    # `when` condition, which the user can see on the canvas.\n    hidden: bool = False\n\n\n@dataclass(frozen=True)\nclass ActionSpec:\n    kind: str\n    label: str\n    group: str\n    params: Tuple[Param, ...] = ()\n    # How the generator writes it. "media" means "call Message.<method> with the\n    # payload param and an optional caption"; "custom" is a hand-written emitter.\n    emit: str = "custom"\n    method: str = ""          # aiogram Message method name for emit="media"\n    payload: str = ""         # which param is the first positional argument\n    caption: bool = False\n    observers: Tuple[str, ...] = ALL_EVENTS\n    container: bool = False   # the node editor lets blocks nest inside it\n    hint: str = ""\n\n    def param(self, name: str) -> Optional[Param]:\n        for item in self.params:\n            if item.name == name:\n                return item\n        return None\n\n    def defaults(self) -> Dict[str, Any]:\n        return {item.name: item.default for item in self.params}\n\n\n@dataclass(frozen=True)\nclass EventSpec:\n    kind: str\n    label: str\n    group: str\n    observer: str               # aiogram observer attribute: message, callback_query, ...\n    family: str = MESSAGE       # which action family the handlers belong to\n    filter: str = ""            # aiogram filter expression, "" means "everything"\n    key_param: str = ""         # command / callback data / state name\n    params: Tuple[Param, ...] = ()\n\n    def param(self, name: str) -> Optional[Param]:\n        for item in self.params:\n            if item.name == name:\n                return item\n        return None\n\n    def defaults(self) -> Dict[str, Any]:\n        return {item.name: item.default for item in self.params}\n\n\n# --------------------------------------------------------------------- filters\n# Optional narrowing available on every event. It turns into one more filter\n# argument on the generated handler.\nCHAT_FILTER = Param(\n    "chat",\n    "получено",\n    kind="choice",\n    choices=(("", "в любом чате"), ("private", "в личке"), ("group", "в группе"),\n             ("supergroup", "в супергруппе"), ("channel", "в канале")),\n    hint="где именно получено сообщение",\n)\nFROM_FILTER = Param(\n    "from_user",\n    "только от пользователя с ID",\n    kind="number",\n    hint="0 - от любого; ID можно узнать у @userinfobot",\n)\nREGEX_FILTER = Param(\n    "regex",\n    "текст подходит под шаблон",\n    hint=\'например ^[0-9]+$ - только цифры, ^привет - начинает с «привет»\',\n    hidden=True,\n)\nCOMMON_EVENT_PARAMS: Tuple[Param, ...] = ()\n\nGROUPS = (\n    ("event", "События"),\n    ("message", "Сообщения"),\n    ("media", "Медиа"),\n    ("keyboard", "Клавиатура"),\n    ("logic", "Логика"),\n    ("state", "Состояния"),\n    ("moderation", "Модерация"),\n    ("service", "Сервис"),\n)\n\n\n# --------------------------------------------------------------------- actions\nACTIONS: Tuple[ActionSpec, ...] = (\n    # --- messages ---------------------------------------------------------\n    ActionSpec(\n        "send", "Отправить текст", "message",\n        params=(Param("text", "Текст", kind="multiline", required=True, default="Привет!"),),\n        emit="send", container=True,\n        hint="сообщение от бота; кнопки вкладываются внутрь",\n    ),\n    ActionSpec(\n        "send_photo", "Фото", "media",\n        params=(Param("url", "URL или file_id", required=True, default="https://"),\n                Param("caption", "Подпись")),\n        emit="media", method="answer_photo", payload="url", caption=True,\n    ),\n    ActionSpec(\n        "send_document", "Документ", "media",\n        params=(Param("url", "URL или file_id", required=True, default="https://"),\n                Param("caption", "Подпись")),\n        emit="media", method="answer_document", payload="url", caption=True,\n    ),\n    ActionSpec(\n        "send_video", "Видео", "media",\n        params=(Param("url", "URL или file_id", required=True, default="https://"),\n                Param("caption", "Подпись")),\n        emit="media", method="answer_video", payload="url", caption=True,\n    ),\n    ActionSpec(\n        "send_animation", "GIF", "media",\n        params=(Param("url", "URL или file_id", required=True, default="https://"),\n                Param("caption", "Подпись")),\n        emit="media", method="answer_animation", payload="url", caption=True,\n    ),\n    ActionSpec(\n        "send_audio", "Аудио", "media",\n        params=(Param("url", "URL или file_id", required=True, default="https://"),\n                Param("caption", "Подпись")),\n        emit="media", method="answer_audio", payload="url", caption=True,\n    ),\n    ActionSpec(\n        "send_voice", "Голосовое", "media",\n        params=(Param("url", "URL или file_id", required=True, default="https://"),\n                Param("caption", "Подпись")),\n        emit="media", method="answer_voice", payload="url", caption=True,\n    ),\n    ActionSpec(\n        "send_sticker", "Стикер", "media",\n        params=(Param("url", "URL или file_id", required=True, default="https://"),),\n        emit="media", method="answer_sticker", payload="url",\n    ),\n    ActionSpec(\n        "send_location", "Геолокация", "media",\n        params=(Param("latitude", "Широта", kind="number", default="0", required=True),\n                Param("longitude", "Долгота", kind="number", default="0", required=True)),\n        emit="media", method="answer_location",\n    ),\n    ActionSpec(\n        "send_contact", "Контакт", "media",\n        params=(Param("phone", "Телефон", default="+10000000000", required=True),\n                Param("first_name", "Имя", default="Имя")),\n        emit="media", method="answer_contact",\n    ),\n    ActionSpec(\n        "send_poll", "Опрос", "media",\n        params=(Param("question", "Вопрос", required=True, default="Вопрос?"),\n                Param("options", "Варианты", kind="values", required=True,\n                      hint="через запятую: Да, Нет, Не знаю")),\n        emit="custom",\n    ),\n    ActionSpec(\n        "send_dice", "Интерактивное эмодзи", "media",\n        params=(Param("emoji", "Какое", kind="choice",\n                      choices=(("🎲", "кубик"), ("🎯", "дартс"), ("🏀", "баскетбол"),\n                               ("⚽", "футбол"), ("🎰", "слоты"), ("🎳", "боулинг"),\n                               ("🎉", "хлопушка")),\n                      default="🎲"),),\n        emit="media", method="answer_dice",\n        hint="Telegram бросает эмодзи; что выпало - можно проверить условием",\n    ),\n    # --- editing and answering ------------------------------------------\n    ActionSpec(\n        "edit_text", "Изменить текст", "message",\n        params=(Param("text", "Новый текст", kind="multiline", required=True, default=""),),\n        emit="custom", hint="переписать сообщение, на котором нажали кнопку",\n    ),\n    ActionSpec(\n        "answer_callback", "Всплывающая подсказка", "message",\n        params=(Param("text", "Текст", default=""), Param("alert", "Окно с кнопкой ОК",\n                                                          kind="bool", default=False)),\n        emit="custom", observers=(CALLBACK,),\n        hint="короткое сообщение над кнопкой, которую нажали",\n    ),\n    ActionSpec(\n        "delete", "Удалить сообщение", "message",\n        params=(), emit="delete",\n    ),\n    ActionSpec(\n        "typing", "Печатает…", "service",\n        params=(), emit="typing",\n    ),\n    ActionSpec(\n        "pin", "Закрепить", "message",\n        params=(Param("silent", "Без уведомления", kind="bool", default=False),),\n        emit="custom",\n    ),\n    ActionSpec(\n        "unpin", "Открепить", "message",\n        params=(), emit="custom",\n    ),\n    # --- logic ------------------------------------------------------------\n    ActionSpec(\n        "when", "Условие", "logic",\n        params=(Param("op", "Проверка", kind="choice",\n                      choices=(("contains", "содержит"), ("==", "равно"),\n                               ("!=", "не равно"), ("startswith", "начинается с"),\n                               ("endswith", "заканчивается на")),\n                      default="contains"),\n                Param("value", "Значение", default="привет", required=True),\n                Param("values", "Ещё значения", kind="values")),\n        emit="when", container=True,\n    ),\n    ActionSpec(\n        "otherwise", "Иначе", "logic", params=(), emit="otherwise", container=True,\n    ),\n    ActionSpec("nothing", "Ничего", "logic", params=(), emit="nothing"),\n    # --- states (FSM) -----------------------------------------------------\n    ActionSpec(\n        "set_state", "Запомнить шаг", "state",\n        params=(Param("state", "Шаг", kind="state", required=True),),\n        emit="custom", hint="диалог запомнит, на каком шаге пользователь",\n    ),\n    ActionSpec(\n        "clear_state", "Забыть шаг", "state", params=(), emit="custom",\n    ),\n    # --- moderation -------------------------------------------------------\n    ActionSpec(\n        "ban_user", "Забанить", "moderation",\n        params=(Param("user_id", "ID пользователя", kind="number", default="0"),),\n        emit="custom", hint="пустой ID - забанить автора сообщения",\n    ),\n    ActionSpec(\n        "unban_user", "Разбанить", "moderation",\n        params=(Param("user_id", "ID пользователя", kind="number", default="0"),),\n        emit="custom",\n    ),\n    ActionSpec(\n        "mute_user", "Заглушить", "moderation",\n        params=(Param("user_id", "ID пользователя", kind="number", default="0"),\n                Param("minutes", "Минут", kind="number", default="10")),\n        emit="custom",\n    ),\n    # --- service ----------------------------------------------------------\n    ActionSpec(\n        "delay", "Пауза", "service",\n        params=(Param("seconds", "Секунды", kind="number", default="1", required=True),),\n        emit="delay",\n    ),\n    ActionSpec(\n        "log", "Запись в лог", "service",\n        params=(Param("text", "Текст", default="", required=True),),\n        emit="custom", hint="печатается в консоль и во вкладку «Логи»",\n    ),\n    ActionSpec(\n        "inline_result", "Ответ на inline-запрос", "message",\n        params=(Param("title", "Заголовок в списке", required=True, default="Заголовок"),\n                Param("text", "Текст, который отправится", kind="multiline",\n                      required=True, default="Текст"),\n                Param("description", "Пояснение под заголовком")),\n        emit="custom", observers=(INLINE,),\n        hint="когда человек пишет «@бот запрос» в любом чате; показывается "\n             "одна карточка-ответ",\n    ),\n)\n\nACTIONS_BY_KIND: Dict[str, ActionSpec] = {item.kind: item for item in ACTIONS}\n\n# How the editors word every action. The machine names stay as they are; this is\n# the one place to change a label or the one-line explanation under it.\nACTION_TEXT: Dict[str, Tuple[str, str]] = {\n    "send": ("Отправить текст", "сообщение от бота; кнопки вкладываются внутрь"),\n    "send_photo": ("Фото", "картинка по ссылке или file_id"),\n    "send_document": ("Документ", "файл по ссылке или file_id"),\n    "send_video": ("Видео", "ролик по ссылке или file_id"),\n    "send_animation": ("GIF", "анимация по ссылке или file_id"),\n    "send_audio": ("Аудио", "музыка по ссылке или file_id"),\n    "send_voice": ("Голосовое", "запись по ссылке или file_id"),\n    "send_sticker": ("Стикер", "стикер по ссылке или file_id"),\n    "send_location": ("Геолокация", "точка на карте: широта и долгота"),\n    "send_contact": ("Контакт", "телефон и имя одной карточкой"),\n    "send_poll": ("Опрос", "вопрос и варианты ответа; Telegram считает голоса сам"),\n    "send_dice": ("Интерактивное эмодзи",\n                  "Telegram бросает кубик или дартс; что выпало - проверяется условием"),\n    "edit_text": ("Изменить отправленное",\n                  "переписать сообщение, на котором нажали кнопку"),\n    "answer_callback": ("Подсказка над кнопкой",\n                        "короткий текст или окно с «ОК» после нажатия"),\n    "delete": ("Удалить сообщение", "стереть сообщение, из которого пришла команда"),\n    "typing": ("Показать «печатает…»", "индикатор набора в чате"),\n    "pin": ("Закрепить сообщение", "закрепить сообщение в чате"),\n    "unpin": ("Открепить сообщение", "снять закрепление"),\n    "when": ("Условие", "проверка текста сообщения; внутри - что делать"),\n    "otherwise": ("Иначе", "ветка «иначе» для условия рядом"),\n    "nothing": ("Ничего не делать", "пустое действие, например внутри условия"),\n    "set_state": ("Перейти к шагу", "диалог запомнит, на каком шаге человек"),\n    "clear_state": ("Завершить диалог", "забыть шаг: дальше работают обычные обработчики"),\n    "ban_user": ("Забанить", "без ID - забанить автора сообщения"),\n    "unban_user": ("Разбанить", "вернуть доступ в чат"),\n    "mute_user": ("Заглушить", "запретить писать на N минут"),\n    "delay": ("Пауза", "подождать перед следующим действием"),\n    "log": ("Запись в лог", "печатается в консоль и во вкладку «Логи»"),\n    "inline_result": ("Ответ на inline-запрос",\n                      "когда человек пишет «@бот запрос» в любом чате; "\n                      "показывается одна карточка-ответ"),\n}\n\nACTIONS = tuple(\n    replace(item, label=ACTION_TEXT[item.kind][0], hint=ACTION_TEXT[item.kind][1])\n    if item.kind in ACTION_TEXT else item\n    for item in ACTIONS\n)\nACTIONS_BY_KIND = {item.kind: item for item in ACTIONS}\n\n# Keywords that read better as aliases in the DSL and the text syntax.\nACTION_ALIASES = {\n    "pass": "nothing",\n    "photo": "send_photo",\n    "document": "send_document",\n    "video": "send_video",\n    "animation": "send_animation",\n    "audio": "send_audio",\n    "voice": "send_voice",\n    "sticker": "send_sticker",\n    "location": "send_location",\n    "contact": "send_contact",\n    "poll": "send_poll",\n    "dice": "send_dice",\n    "alert": "answer_callback",\n    "state": "set_state",\n    "log_text": "log",\n}\n\n\n# ---------------------------------------------------------------------- events\nEVENTS: Tuple[EventSpec, ...] = (\n    EventSpec("command", "Команда", "event", "message",\n              key_param="command",\n              params=(Param("command", "Команда", default="/start", required=True),)),\n    EventSpec("text", "Текст", "event", "message", filter="F.text",\n              params=(Param("patterns", "Только эти тексты", kind="values",\n                            hint="точные совпадения, через запятую", hidden=True),)),\n    EventSpec("photo", "Фото", "event", "message", filter="F.photo"),\n    EventSpec("sticker", "Стикер", "event", "message", filter="F.sticker"),\n    EventSpec("voice", "Голосовое", "event", "message", filter="F.voice"),\n    EventSpec("video", "Видео", "event", "message", filter="F.video"),\n    EventSpec("video_note", "Кружок", "event", "message", filter="F.video_note"),\n    EventSpec("audio", "Аудио", "event", "message", filter="F.audio"),\n    EventSpec("document", "Документ", "event", "message", filter="F.document"),\n    EventSpec("animation", "GIF", "event", "message", filter="F.animation"),\n    EventSpec("location", "Геолокация", "event", "message", filter="F.location"),\n    EventSpec("contact", "Контакт", "event", "message", filter="F.contact"),\n    EventSpec("poll", "Опрос", "event", "message", filter="F.poll"),\n    EventSpec("dice", "Кубик", "event", "message", filter="F.dice"),\n    EventSpec("new_members", "Новый участник", "event", "message",\n              filter="F.new_chat_members"),\n    EventSpec("left_member", "Участник вышел", "event", "message",\n              filter="F.left_chat_member"),\n    EventSpec("pinned", "Сообщение закреплено", "event", "message",\n              filter="F.pinned_message"),\n    EventSpec("web_app_data", "Данные из Web App", "event", "message",\n              filter="F.web_app_data"),\n    EventSpec("any", "Любое сообщение", "event", "message"),\n    EventSpec("edited", "Сообщение изменено", "event", "edited_message",\n              filter="F.text"),\n    EventSpec("callback", "Нажата кнопка", "event", "callback_query",\n              family=CALLBACK, key_param="data",\n              params=(Param("data", "Данные кнопки",\n                            hint="пусто - любая кнопка; иначе точное совпадение"),)),\n    EventSpec("state", "Сообщение на шаге диалога", "event", "message",\n              key_param="state",\n              params=(Param("state", "Шаг", kind="state", required=True),)),\n    EventSpec("inline_query", "Inline-запрос", "event", "inline_query",\n              family=INLINE),\n    EventSpec("chat_member", "Участник изменился", "event", "chat_member",\n              family=CHAT),\n    EventSpec("my_chat_member", "Бот добавлен/убран", "event", "my_chat_member",\n              family=CHAT),\n    EventSpec("poll_answer", "Ответ на опрос", "event", "poll_answer",\n              family=CHAT),\n    EventSpec("channel_post", "Пост в канале", "event", "channel_post"),\n)\n\ndef _extra_params(spec: "EventSpec") -> Tuple[Param, ...]:\n    # Every event accepts the same optional narrowings; which ones make sense\n    # depends on what the update carries.\n    extras: List[Param] = []\n    if spec.family in (MESSAGE, CHAT):\n        extras.append(CHAT_FILTER)\n    extras.append(FROM_FILTER)\n    if spec.family == MESSAGE and spec.filter in ("F.text", ""):\n        extras.append(REGEX_FILTER)\n    return tuple(extras)\n\n\nEVENTS = tuple(replace(spec, params=spec.params + _extra_params(spec)) for spec in EVENTS)\n\nEVENTS_BY_KIND: Dict[str, EventSpec] = {item.kind: item for item in EVENTS}\n\nEVENT_ALIASES = {\n    "message": "text",\n    "image": "photo",\n    "left_chat_member": "left_member",\n    "new_chat_members": "new_members",\n    "button": "callback",\n    "inline": "inline_query",\n    "any": "any",\n}\n\n# Keyboard styles the `buttons` block understands.\nKEYBOARD_STYLES = (\n    ("inline", "inline-кнопки под сообщением"),\n    ("reply", "reply-клавиатура вместо поля ввода"),\n)\n\n# Button targets: a command, a URL, or a reply-keyboard request.\nBUTTON_KINDS = (\n    ("command", "команда"),\n    ("url", "ссылка"),\n    ("web_app", "web app"),\n    ("contact", "запросить телефон"),\n    ("location", "запросить геолокацию"),\n)\n\n\n# ------------------------------------------------------------------- argument binding\ndef _strip_quotes(value: Any) -> Any:\n    # `url="https://x"` arrives as the text `"https://x"` with its quotes: the\n    # text syntax writes keyword arguments like Python does.\n    if not isinstance(value, str):\n        return value\n    text = value.strip()\n    if len(text) < 2 or text[0] not in "\\"\'" or text[-1] != text[0]:\n        return value\n    try:\n        parsed = ast.literal_eval(text)\n    except (SyntaxError, ValueError):\n        return value\n    return parsed if isinstance(parsed, str) else value\n\n\ndef _as_bool(value: Any) -> bool:\n    if isinstance(value, bool):\n        return value\n    text = str(value).strip().lower()\n    if text in ("1", "true", "yes", "on", "да"):\n        return True\n    if text in ("0", "false", "no", "off", "нет", ""):\n        return False\n    raise BindError("ожидалось true или false, получено {0!r}".format(value))\n\n\ndef _as_number(value: Any) -> Any:\n    text = str(value).strip().replace(",", ".")\n    if text == "":\n        return 0\n    try:\n        number = float(text)\n    except ValueError:\n        raise BindError("ожидалось число, получено {0!r}".format(value)) from None\n    return int(number) if number.is_integer() else number\n\n\ndef coerce(param: Param, value: Any) -> Any:\n    value = _strip_quotes(value)\n    if param.kind == "bool":\n        return _as_bool(value)\n    if param.kind == "number":\n        return _as_number(value)\n    if param.kind == "values":\n        if isinstance(value, (list, tuple)):\n            return tuple(str(item) for item in value if str(item).strip())\n        return tuple(\n            part.strip() for part in str(value).replace(";", ",").split(",")\n            if part.strip()\n        )\n    if param.kind == "choice":\n        allowed = [item[0] for item in param.choices]\n        text = str(value)\n        if allowed and text not in allowed:\n            raise BindError(\n                "ожидалось одно из {0}, получено {1!r}".format(\n                    ", ".join(allowed), value\n                )\n            )\n        return text\n    return str(value)\n\n\ndef bind_arguments(spec: ActionSpec, items: Sequence[Tuple[str, bool]]) -> Dict[str, Any]:\n    """Map source arguments onto the catalogue entry.\n\n    `items` are (value, is_bare) pairs in source order, where bare means "not a\n    quoted string" - `delay 2`, `alert`, `state=order`. A named `name=value` item\n    sets that param, a bare bool param name turns it on, and everything else\n    fills the declared params in order. A `values` param swallows the tail.\n    """\n    result = spec.defaults()\n    filled = set()\n    pending = list(items)\n    index = 0\n    while pending:\n        raw, is_bare = pending.pop(0)\n        text = str(raw)\n        if is_bare and "=" in text:\n            name, _, value = text.partition("=")\n            param = spec.param(name.strip())\n            if param is None:\n                raise BindError(\n                    "у {0} нет параметра {1!r}".format(spec.kind, name.strip()),\n                    "доступны: " + ", ".join(p.name for p in spec.params),\n                )\n            result[param.name] = coerce(param, value.strip())\n            filled.add(param.name)\n            continue\n        if is_bare:\n            named = spec.param(text)\n            if named is not None and named.kind == "bool":\n                result[named.name] = True\n                filled.add(named.name)\n                continue\n        while index < len(spec.params) and spec.params[index].name in filled:\n            index += 1\n        if index >= len(spec.params):\n            raise BindError(\n                "{0} не принимает столько аргументов".format(spec.kind),\n                "параметры: " + ", ".join(p.name for p in spec.params),\n            )\n        param = spec.params[index]\n        if param.kind == "values":\n            rest = [text] + [str(value) for value, bare in pending if not bare]\n            pending = []\n            result[param.name] = coerce(param, rest)\n            filled.add(param.name)\n            break\n        result[param.name] = coerce(param, text)\n        filled.add(param.name)\n        index += 1\n    _check_required(spec, result)\n    return result\n\n\ndef _check_required(spec: ActionSpec, values: Dict[str, Any]) -> None:\n    for param in spec.params:\n        if not param.required:\n            continue\n        value = values.get(param.name)\n        if value is None or value == "" or value == ():\n            raise BindError(\n                "{0}: нужен параметр {1!r}".format(spec.kind, param.name),\n                param.hint or param.label,\n            )\n\n\ndef action_for(keyword: str) -> Optional[ActionSpec]:\n    kind = ACTION_ALIASES.get(keyword, keyword)\n    return ACTIONS_BY_KIND.get(kind)\n\n\ndef event_for(keyword: str) -> Optional[EventSpec]:\n    kind = EVENT_ALIASES.get(keyword, keyword)\n    return EVENTS_BY_KIND.get(kind)\n\n\n# ------------------------------------------------------------------- languages\n# The catalogue is written in Russian; these are the English labels the editors\n# show when the interface language is switched. Lookup is by the Russian text, so\n# a new action still appears in English as soon as its words are listed here.\nEN_TEXT: Dict[str, str] = {\n    # actions\n    "Отправить текст": "Send text",\n    "Фото": "Photo", "Документ": "Document", "Видео": "Video", "GIF": "GIF",\n    "Аудио": "Audio", "Голосовое": "Voice message", "Стикер": "Sticker",\n    "Геолокация": "Location", "Контакт": "Contact", "Опрос": "Poll",\n    "Интерактивное эмодзи": "Interactive emoji",\n    "Изменить отправленное": "Edit message",\n    "Подсказка над кнопкой": "Toast over the button",\n    "Удалить сообщение": "Delete message",\n    "Показать «печатает…»": "Show “typing…”",\n    "Закрепить сообщение": "Pin message", "Открепить сообщение": "Unpin message",\n    "Условие": "Condition", "Иначе": "Else", "Ничего не делать": "Do nothing",\n    "Перейти к шагу": "Go to step", "Завершить диалог": "End dialogue",\n    "Забанить": "Ban", "Разбанить": "Unban", "Заглушить": "Mute",\n    "Пауза": "Pause", "Запись в лог": "Write to log",\n    "Ответ на inline-запрос": "Inline query answer",\n    # hints\n    "сообщение от бота; кнопки вкладываются внутрь":\n        "a message from the bot; keyboards nest inside",\n    "Telegram бросает кубик или дартс; что выпало - проверяется условием":\n        "Telegram rolls it; check what came up with a condition",\n    "переписать сообщение, на котором нажали кнопку":\n        "rewrite the message the button was pressed on",\n    "короткий текст или окно с «ОК» после нажатия":\n        "a short text or an OK dialog after the press",\n    "диалог запомнит, на каком шаге человек":\n        "the dialogue remembers which step the person is on",\n    "забыть шаг: дальше работают обычные обработчики":\n        "forget the step: ordinary handlers take over",\n    "когда человек пишет «@бот запрос» в любом чате; показывается одна карточка-ответ":\n        "when someone types “@bot query”; one result card is shown",\n    # events\n    "Команда": "Command", "Текст": "Text", "Кружок": "Video note",\n    "Новый участник": "New member", "Участник вышел": "Member left",\n    "Сообщение закреплено": "Message pinned",\n    "Данные из Web App": "Web App data", "Любое сообщение": "Any message",\n    "Сообщение изменено": "Message edited", "Нажата кнопка": "Button pressed",\n    "Сообщение на шаге диалога": "Message at a dialogue step",\n    "Inline-запрос": "Inline query", "Участник изменился": "Member updated",\n    "Бот добавлен/убран": "Bot added/removed", "Ответ на опрос": "Poll answer",\n    "Пост в канале": "Channel post",\n    # params\n    "Текст": "Text", "Подпись": "Caption", "Ссылка или file_id": "URL or file_id",\n    "URL или file_id": "URL or file_id", "Какое": "Which one",\n    "Вопрос": "Question", "Варианты": "Options", "Широта": "Latitude",\n    "Долгота": "Longitude", "Телефон": "Phone", "Имя": "First name",\n    "Новый текст": "New text", "Окно с кнопкой ОК": "OK dialog",\n    "Без уведомления": "Without notification", "ID пользователя": "User ID",\n    "Минут": "Minutes", "Секунды": "Seconds", "Шаг": "Step",\n    "Проверка": "Comparison", "Значение": "Value", "Ещё значения": "More values",\n    "Заголовок в списке": "Title in the list", "Текст, который отправится": "Sent text",\n    "Пояснение под заголовком": "Description under the title",\n    "получено": "received", "только от пользователя с ID": "only from user ID",\n    "текст подходит под шаблон": "text matches a pattern",\n    "Только эти тексты": "Only these texts", "Данные кнопки": "Button data",\n    # choices\n    "в любом чате": "in any chat", "в личке": "in private", "в группе": "in a group",\n    "в супергруппе": "in a supergroup", "в канале": "in a channel",\n    "кубик": "dice", "дартс": "darts", "баскетбол": "basketball", "футбол": "football",\n    "слоты": "slots", "боулинг": "bowling", "хлопушка": "party",\n    "содержит": "contains", "равно": "equals", "не равно": "not equal",\n    "начинается с": "starts with", "заканчивается на": "ends with",\n    "команда": "command", "ссылка": "link", "запросить телефон": "request phone",\n    "запросить геолокацию": "request location",\n    # groups and keyboard\n    "События": "Events", "Сообщения": "Messages", "Медиа": "Media",\n    "Клавиатура": "Keyboard", "Логика": "Logic", "Состояния": "Dialogues",\n    "Модерация": "Moderation", "Сервис": "Service",\n    "inline-кнопки под сообщением": "inline buttons under the message",\n    "reply-клавиатура вместо поля ввода": "reply keyboard instead of the input field",\n    # the remaining hints, so no Russian word survives in the English palette\n    "0 - от любого; ID можно узнать у @userinfobot":\n        "0 - from anyone; find the ID with @userinfobot",\n    "Кубик": "Dice",\n    "анимация по ссылке или file_id": "a GIF by URL or file_id",\n    "без ID - забанить автора сообщения": "no ID - ban the author of the message",\n    "вернуть доступ в чат": "restore access to the chat",\n    "ветка «иначе» для условия рядом": "the else branch of the condition nearby",\n    "вопрос и варианты ответа; Telegram считает голоса сам":\n        "a question and its options; Telegram counts the votes",\n    "где именно получено сообщение": "which kind of chat the message came from",\n    "закрепить сообщение в чате": "pin the message in the chat",\n    "запись по ссылке или file_id": "a voice message by URL or file_id",\n    "запретить писать на N минут": "mute for N minutes",\n    "индикатор набора в чате": "the typing indicator in the chat",\n    "картинка по ссылке или file_id": "a picture by URL or file_id",\n    "музыка по ссылке или file_id": "music by URL or file_id",\n    "например ^[0-9]+$ - только цифры, ^привет - начинает с «привет»":\n        "e.g. ^[0-9]+$ - digits only; ^hi - starts with “hi”",\n    "печатается в консоль и во вкладку «Логи»":\n        "printed to the console and the Logs tab",\n    "подождать перед следующим действием": "wait before the next action",\n    "проверка текста сообщения; внутри - что делать":\n        "a check on the message text; what to do goes inside",\n    "пусто - любая кнопка; иначе точное совпадение":\n        "empty - any button; otherwise an exact match",\n    "пустое действие, например внутри условия": "a no-op, e.g. inside a condition",\n    "ролик по ссылке или file_id": "a video by URL or file_id",\n    "снять закрепление": "unpin the message",\n    "стереть сообщение, из которого пришла команда":\n        "delete the message the command came from",\n    "стикер по ссылке или file_id": "a sticker by URL or file_id",\n    "телефон и имя одной карточкой": "a phone and a name in one card",\n    "точка на карте: широта и долгота": "a point on the map: latitude and longitude",\n    "точные совпадения, через запятую": "exact matches, comma separated",\n    "файл по ссылке или file_id": "a file by URL or file_id",\n    "через запятую: Да, Нет, Не знаю": "comma separated: Yes, No, Not sure",\n}\n\n\ndef english(text: str) -> str:\n    # English label for a Russian one, or the original text when it is missing.\n    return EN_TEXT.get(text, text)\n\n\n# ------------------------------------------------------------------ editor schema\nGROUP_COLOUR = {\n    "message": "#1f7a4d", "media": "#1f7a4d", "keyboard": "#7ee0a8",\n    "logic": "#c98bff", "state": "#d05c9b", "moderation": "#c0392b",\n    "service": "#4a5a7a", "event": "#f0a35e",\n}\n\n# Blocks with statement slots are written by the page: their shape is part of the\n# Blockly XML that convert.py reads back.\nSTRUCTURAL_BLOCKS = frozenset({"send", "when", "otherwise", "buttons", "button"})\n\n\ndef _blockly_field(param: Param, label, lang: str) -> Dict[str, Any]:\n    name = param.name.upper()\n    if param.kind == "choice":\n        return {"type": "field_dropdown", "name": name,\n                "options": [[label(choice_label), str(value)]\n                            for value, choice_label in param.choices]}\n    if param.kind == "bool":\n        return {"type": "field_dropdown", "name": name,\n                "options": [["yes" if lang == "en" else "да", "true"],\n                            ["no" if lang == "en" else "нет", "false"]]}\n    return {\n        "type": "field_input",\n        "name": name,\n        "text": "" if param.kind == "values" else str(param.default or ""),\n    }\n\n\ndef blockly_blocks(lang: str = "ru") -> List[Dict[str, Any]]:\n    """Blockly block definitions for every catalogue action.\n\n    Blockly numbers placeholders **per message**: `message0` refers to `args0`\n    with `%1`, and `message1` starts again at `%1` for `args1`. Numbering them\n    globally ("%2" in message1) makes Blockly refuse the whole definition with\n    "Message index %2 out of range", which is what broke the block editor once.\n    Building the JSON here keeps that rule in one testable place.\n    """\n    def label(text: str) -> str:\n        return english(text) if lang == "en" else text\n\n    blocks: List[Dict[str, Any]] = []\n    for spec in ACTIONS:\n        if spec.kind in STRUCTURAL_BLOCKS:\n            continue\n        definition: Dict[str, Any] = {\n            "type": "tg_" + ("photo" if spec.kind == "send_photo" else spec.kind),\n            "colour": GROUP_COLOUR.get(spec.group, "#4a5a7a"),\n            "tooltip": label(spec.hint) or label(spec.label),\n            "previousStatement": None,\n            "nextStatement": None,\n        }\n        if not spec.params:\n            definition["message0"] = label(spec.label)\n        visible = [param for param in spec.params if not param.hidden]\n        for index, param in enumerate(visible):\n            caption = label(spec.label) if index == 0 else label(param.label)\n            definition["message{0}".format(index)] = caption + " %1"\n            definition["args{0}".format(index)] = [_blockly_field(param, label, lang)]\n        blocks.append(definition)\n    return blocks\n\n\ndef _param_schema(param: Param, label=str) -> Dict[str, Any]:\n    # `label` is the translator for the requested language; label_en stays for\n    # clients that switch language without reloading.\n    return {\n        "name": param.name,\n        "label": label(param.label),\n        "label_en": english(param.label),\n        "kind": param.kind,\n        "default": param.default,\n        "choices": [{"value": value, "label": label(choice), "label_en": english(choice)}\n                    for value, choice in param.choices],\n        "hint": label(param.hint),\n        "hint_en": english(param.hint),\n        "required": param.required,\n        "hidden": param.hidden,\n    }\n\n\ndef schema(lang: str = "ru") -> Dict[str, Any]:\n    """The whole catalogue as JSON for the three editors."""\n    lang = "en" if str(lang).lower().startswith("en") else "ru"\n\n    def label(text: str) -> str:\n        return english(text) if lang == "en" else text\n\n    return {\n        "version": 3,\n        "lang": lang,\n        "groups": [{"kind": kind, "label": label(item), "label_en": english(item)}\n                   for kind, item in GROUPS],\n        "actions": [\n            {\n                "kind": item.kind,\n                "label": label(item.label),\n                "label_en": english(item.label),\n                "group": item.group,\n                "container": item.container,\n                "observers": list(item.observers),\n                "params": [_param_schema(param, label) for param in item.params],\n                "hint": label(item.hint),\n                "hint_en": english(item.hint),\n            }\n            for item in ACTIONS\n        ],\n        "events": [\n            {\n                "kind": item.kind,\n                "label": label(item.label),\n                "label_en": english(item.label),\n                "group": item.group,\n                "observer": item.observer,\n                "family": item.family,\n                "key_param": item.key_param,\n                "params": [_param_schema(param, label) for param in item.params],\n            }\n            for item in EVENTS\n        ],\n        "filters": [_param_schema(param, label) for param in\n                    (CHAT_FILTER, FROM_FILTER, REGEX_FILTER)],\n        "keyboards": [{"value": value, "label": label(item), "label_en": english(item)}\n                      for value, item in KEYBOARD_STYLES],\n        "buttons": [{"value": value, "label": label(item), "label_en": english(item)}\n                    for value, item in BUTTON_KINDS],\n        "condition_ops": [\n            ("==", label("равно")), ("!=", label("не равно")),\n            ("contains", label("содержит")), ("startswith", label("начинается с")),\n            ("endswith", label("заканчивается на")),\n        ],\n        # Ready-to-use Blockly definitions: the page feeds them straight to\n        # Blockly.defineBlocksWithJsonArray, so the per-message numbering rule\n        # lives here and is covered by a test.\n        "blocks": blockly_blocks(lang),\n    }\n',
    "src/tgblocks/network.py": '# Can this proxy reach api.telegram.org?\n#\n# A bot behind a blocked network needs a proxy that actually tunnels HTTPS to\n# Telegram. "The proxy is in the list" is not the same thing: most free SOCKS\n# entries are dead, closed, or do not allow port 443. This module performs the\n# same three steps the bot will: connect, ask for api.telegram.org:443, then do a\n# real TLS handshake - so the answer is about the bot, not about a ping.\n\nfrom __future__ import annotations\n\nimport base64\nimport socket\nimport ssl\nimport time\nfrom typing import Optional, Tuple\nfrom urllib.parse import unquote, urlsplit\n\nTARGET = "api.telegram.org"\nTARGET_PORT = 443\nDEFAULT_PORTS = {"socks5": 1080, "socks4": 1080, "http": 8080, "https": 8080}\nSCHEMES = tuple(DEFAULT_PORTS)\n\n\nclass ProxyError(Exception):\n    """The proxy string itself is wrong (not a network problem)."""\n\n\ndef parse_proxy(url: str) -> Tuple[str, str, int, Optional[str], Optional[str]]:\n    """`socks5://user:pass@host:1080` -> (scheme, host, port, user, password)."""\n    text = (url or "").strip()\n    if not text:\n        raise ProxyError("пустая строка прокси")\n    if "://" not in text:\n        raise ProxyError(\n            "нужна схема: socks5://, socks4://, http:// или https:// - "\n            "например socks5://127.0.0.1:1080, а не {0!r}".format(text[:40])\n        )\n    parts = urlsplit(text)\n    scheme = parts.scheme.lower()\n    if scheme not in SCHEMES:\n        raise ProxyError(\n            "неизвестная схема {0!r}: подходят {1}".format(scheme, ", ".join(SCHEMES))\n        )\n    if not parts.hostname:\n        raise ProxyError("в адресе нет хоста: {0!r}".format(text[:60]))\n    port = parts.port or DEFAULT_PORTS[scheme]\n    user = unquote(parts.username) if parts.username else None\n    password = unquote(parts.password) if parts.password else None\n    return scheme, parts.hostname, port, user, password\n\n\ndef _recv_exactly(sock: socket.socket, size: int) -> bytes:\n    data = b""\n    while len(data) < size:\n        chunk = sock.recv(size - len(data))\n        if not chunk:\n            raise OSError("прокси закрыл соединение")\n        data += chunk\n    return data\n\n\ndef _socks5(sock: socket.socket, user: Optional[str], password: Optional[str]) -> None:\n    methods = b"\\x00\\x02" if user else b"\\x00"\n    sock.sendall(b"\\x05" + bytes([len(methods)]) + methods)\n    version, method = _recv_exactly(sock, 2)\n    if version != 5:\n        raise OSError("это не SOCKS5 (ответ {0!r})".format(bytes([version, method])))\n    if method == 0x02:\n        name = (user or "").encode()\n        secret = (password or "").encode()\n        sock.sendall(b"\\x01" + bytes([len(name)]) + name + bytes([len(secret)]) + secret)\n        if _recv_exactly(sock, 2)[1] != 0:\n            raise OSError("прокси не принял логин/пароль")\n    elif method != 0x00:\n        raise OSError("прокси требует способ входа, которого нет в строке")\n    name = TARGET.encode()\n    sock.sendall(b"\\x05\\x01\\x00\\x03" + bytes([len(name)]) + name\n                 + TARGET_PORT.to_bytes(2, "big"))\n    reply = _recv_exactly(sock, 4)\n    if reply[1] != 0:\n        reasons = {1: "общий сбой", 2: "соединения запрещены", 3: "сеть недоступна",\n                   4: "хост недоступен", 5: "соединение отклонено", 6: "TTL истёк",\n                   7: "команда не поддержана", 8: "тип адреса не поддержан"}\n        raise OSError("прокси не пустил к {0}: {1}".format(\n            TARGET, reasons.get(reply[1], "код {0}".format(reply[1]))))\n\n\ndef _socks4(sock: socket.socket, user: Optional[str]) -> None:\n    import struct\n\n    address = socket.gethostbyname(TARGET)\n    sock.sendall(b"\\x04\\x01" + struct.pack(">H", TARGET_PORT)\n                 + socket.inet_aton(address) + (user or "").encode() + b"\\x00")\n    reply = _recv_exactly(sock, 8)\n    if reply[1] != 0x5A:\n        raise OSError("SOCKS4 не пустил к {0}".format(TARGET))\n\n\ndef _http_connect(sock: socket.socket, scheme: str,\n                  user: Optional[str], password: Optional[str]) -> None:\n    request = "CONNECT {0}:{1} HTTP/1.1\\r\\nHost: {0}:{1}\\r\\n".format(TARGET, TARGET_PORT)\n    if user:\n        token = base64.b64encode("{0}:{1}".format(user, password or "").encode()).decode()\n        request += "Proxy-Authorization: Basic {0}\\r\\n".format(token)\n    request += "\\r\\n"\n    sock.sendall(request.encode())\n    answer = b""\n    while b"\\r\\n\\r\\n" not in answer:\n        chunk = sock.recv(1)\n        if not chunk:\n            raise OSError("прокси закрыл соединение до ответа")\n        answer += chunk\n    status = answer.split(b"\\r\\n")[0].decode(errors="replace")\n    if " 200" not in status:\n        raise OSError("прокси отказал: {0}".format(status))\n\n\ndef check_proxy(url: str, timeout: float = 8.0) -> Tuple[bool, str, float]:\n    """Return (works, message, seconds) for a proxy URL the bot could use."""\n    scheme, host, port, user, password = parse_proxy(url)\n    started = time.time()\n\n    def took() -> float:\n        return time.time() - started\n\n    try:\n        sock = socket.create_connection((host, port), timeout=timeout)\n    except OSError as error:\n        return False, "нет соединения с прокси {0}:{1} ({2})".format(\n            host, port, error or "таймаут"), took()\n\n    try:\n        sock.settimeout(timeout)\n        if scheme == "socks5":\n            _socks5(sock, user, password)\n        elif scheme == "socks4":\n            _socks4(sock, user)\n        else:\n            _http_connect(sock, scheme, user, password)\n\n        context = ssl.create_default_context()\n        tls = context.wrap_socket(sock, server_hostname=TARGET)\n        try:\n            tls.sendall(b"GET / HTTP/1.1\\r\\nHost: " + TARGET.encode()\n                        + b"\\r\\nConnection: close\\r\\nUser-Agent: tgblocks\\r\\n\\r\\n")\n            data = tls.recv(64)\n        finally:\n            tls.close()\n        if not data.startswith(b"HTTP/"):\n            return False, "туннель есть, но Telegram ответил странно: {0!r}".format(\n                data[:40]), took()\n        status = data.split(b"\\r\\n")[0].decode(errors="replace")\n        return True, "работает: {0}".format(status), took()\n    except ssl.SSLError as error:\n        return False, "TLS не поднялся ({0}): прокси вряд ли пускает HTTPS".format(\n            error.reason or error), took()\n    except OSError as error:\n        return False, str(error), took()\n    finally:\n        try:\n            sock.close()\n        except OSError:\n            pass\n\n\ndef proxy_hint(url: str) -> str:\n    # Ready-to-paste lines for all three editors, so a working proxy is easy to\n    # put where it belongs.\n    return "\\n".join([\n        \'бот:    bot proxy "{0}"\'.format(url),\n        \'текст:  proxy("{0}")\'.format(url),\n        "узлы:   поле proxy в блоке «Бот»",\n        "без файла: TG_PROXY={0}".format(url),\n    ])\n',
    "src/tgblocks/runner.py": r"""# Run a bot whose DSL lives inside a normal .py file.
#
#     from tgblocks import run
#
#     run(
#         '''
#     bot token "123456:ABC"
#
#     on /start:
#         send "Hi!"
#     '''
#     )
#
# Why a string and not raw DSL in a .py file? Python parses a script before any
# installed package gets a chance to run, so `bot token "..."` at module level is
# a SyntaxError regardless of what pip installed. Keeping the DSL in a string
# leaves the file valid Python: `python bot.py` and the IDE Run button just work.

from __future__ import annotations

import os
from typing import Optional

from .dsl.codegen import generate
from .dsl.parser import BotSpec, parse

# Tokens that obviously are placeholders: refuse to start a bot with them.
PLACEHOLDER_TOKENS = {"", "PASTE_YOUR_TOKEN", "123456:REPLACE_WITH_YOUR_TOKEN"}


def compile_string(source: str, filename: str = "<embedded>") -> str:
    # DSL text -> aiogram 3 source code, without executing anything.
    return generate(parse(source, filename))


def usable_token(spec: BotSpec) -> Optional[str]:
    # The token declared in the .tg file, unless it is an obvious placeholder.
    if spec.token and spec.token not in PLACEHOLDER_TOKENS:
        return spec.token
    return None


def missing_token_error(spec: BotSpec, token: Optional[str] = None) -> Optional[str]:
    # Store an explicit token and explain the problem when there is none.
    if token:
        os.environ["TG_BOT_TOKEN"] = token
        return None
    if os.environ.get("TG_BOT_TOKEN"):
        return None
    if not spec.token or spec.token in PLACEHOLDER_TOKENS:
        return (
            "no bot token: pass token=..., set TG_BOT_TOKEN, "
            'or replace bot token "PASTE_YOUR_TOKEN"'
        )
    return None


def run_spec(
    spec: BotSpec,
    token: Optional[str] = None,
    filename: str = "<embedded>",
) -> None:
    # Execute an already built BotSpec (used by run() and by the builder API).
    error = missing_token_error(spec, token)
    if error:
        raise SystemExit("tgblocks: {0}".format(error))

    try:
        import aiogram  # noqa: F401
    except ImportError:
        raise SystemExit(
            'tgblocks: aiogram is not installed. Run: pip install "tgblocks[runtime]"'
        )

    code = generate(spec)
    namespace = {"__name__": "__main__", "__file__": filename, "__package__": None}
    exec(compile(code, filename, "exec"), namespace)


def run(
    source: str,
    token: Optional[str] = None,
    filename: str = "<embedded>",
) -> None:
    # Compile DSL text and start polling. Blocks until Ctrl+C.
    run_spec(parse(source, filename), token=token, filename=filename)
""",
    "src/tgblocks/textlang.py": r"""# Parser for the text syntax used by the browser text editor.
#
# The syntax looks like Python, but it is our own language: the browser editor
# parses it here and compiles it with the same generator as the DSL.
#
#     token("123456:ABC")
#     name("my bot")
#
#     on.command("/start"):
#         send("Привет")
#         button("Помощь", "/help")
#         button("Сайт", url="https://example.com")
#
#     on.message(TEXT, "привет", "Привет"):
#         send("И тебе привет!")
#
#     on.message(PHOTO):
#         send("Хорошее фото")
#
# Actions are not enumerated here: tgblocks.model describes them, this module
# only reads the syntax. A new action therefore needs no change in this file.

from __future__ import annotations

import ast
import re
from typing import Any, Dict, List, NoReturn, Optional, Tuple

from .model import (
    BindError,
    EventSpec,
    action_for,
    bind_arguments,
    event_for,
)
from .dsl.parser import (
    Action,
    BotSpec,
    Button,
    Buttons,
    Condition,
    DSLParseError,
    Handler,
    When,
    validate,
)

OPS = ("==", "!=", "contains", "startswith", "endswith")

# Constants used as the first argument of on.message(...).
KINDS = {
    "TEXT": "text",
    "PHOTO": "photo",
    "IMAGE": "photo",
    "STICKER": "sticker",
    "VOICE": "voice",
    "VIDEO": "video",
    "VIDEO_NOTE": "video_note",
    "AUDIO": "audio",
    "DOCUMENT": "document",
    "ANIMATION": "animation",
    "LOCATION": "location",
    "CONTACT": "contact",
    "POLL": "poll",
    "DICE": "dice",
    "NEW_MEMBERS": "new_members",
    "LEFT_MEMBER": "left_member",
    "PINNED": "pinned",
    "WEB_APP_DATA": "web_app_data",
    "EDITED": "edited",
    "ANY": "any",
}

_CALL_RE = re.compile(r"^(?P<name>[A-Za-z_][\w.]*)\((?P<args>.*)\)(?P<colon>:)?$")
_COMMAND_RE = re.compile(r"^/[A-Za-z0-9_]{1,32}$")
_STATE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,31}$")


class _Line:
    def __init__(self, number: int, indent: int, text: str, raw: str) -> None:
        self.number = number
        self.indent = indent
        self.text = text
        self.raw = raw


def _split_arguments(text: str) -> List[str]:
    # Split on top-level commas, keeping quoted strings intact.
    parts: List[str] = []
    current: List[str] = []
    depth = 0
    quote = ""
    escaped = False
    for char in text:
        if quote:
            current.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = ""
            continue
        if char in "'\"":
            quote = char
            current.append(char)
            continue
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        if char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


class _Parser:
    def __init__(self, source: str, filename: str = "<text>") -> None:
        self.filename = filename
        source = source.lstrip("\ufeff")
        self.source_lines = source.splitlines()
        self.lines = self._tokenize(source)
        self.pos = 0

    # ------------------------------------------------------------- tokenizer
    def _tokenize(self, source: str) -> List[_Line]:
        lines: List[_Line] = []
        for number, raw in enumerate(source.splitlines(), start=1):
            leading = raw[: len(raw) - len(raw.lstrip())]
            if "\t" in leading:
                raise DSLParseError(
                    "tabs are not allowed for indentation",
                    number,
                    1,
                    raw,
                    "use 4 spaces per level",
                )
            text = raw.strip()
            if not text or text.startswith("#"):
                continue
            lines.append(_Line(number, len(raw) - len(raw.lstrip(" ")), text, raw))
        return lines

    # ----------------------------------------------------------------- errors
    def _fail(self, message: str, line: _Line, hint: str = "") -> NoReturn:
        column = line.indent + 1
        raise DSLParseError(message, line.number, column, line.raw, hint)

    def _string(self, argument: str, line: _Line, what: str = "text") -> str:
        argument = argument.strip()
        if len(argument) < 2 or argument[0] not in "'\"" or argument[-1] != argument[0]:
            self._fail(
                "expected a quoted {0}".format(what),
                line,
                'write it in quotes, for example: "{0}"'.format(what),
            )
        try:
            value = ast.literal_eval(argument)
        except (SyntaxError, ValueError):
            self._fail("cannot read the {0}".format(what), line, "check the quotes")
        if not isinstance(value, str):
            self._fail("the {0} must be text".format(what), line)
        return value

    def _items(self, arguments: str, line: _Line) -> List[Tuple[str, bool]]:
        # Comma separated arguments -> (value, is_bare) for the catalogue binder.
        items: List[Tuple[str, bool]] = []
        for part in _split_arguments(arguments):
            part = part.strip()
            if not part:
                continue
            if part[0] in "'\"":
                items.append((self._string(part, line), False))
            else:
                items.append((part, True))
        return items

    # ------------------------------------------------------------------ entry
    def parse(self) -> BotSpec:
        bot = BotSpec()
        while self.pos < len(self.lines):
            line = self.lines[self.pos]
            if line.indent != 0:
                self._fail("unexpected indentation", line, "this line has no open block")
            name, arguments, has_colon = self._split_call(line)

            if name == "pass":
                # `pass` at the top level means nothing here, exactly like in Python.
                self.pos += 1
                continue
            handled = self._directive(bot, name, arguments, line)
            if handled:
                self.pos += 1
                continue
            if name == "state":
                self._add_state(bot, arguments, line)
                self.pos += 1
                continue
            if name.startswith("on."):
                bot.handlers.append(self._parse_event(line, name, arguments, has_colon))
                continue
            self._fail(
                "unknown call {0}()".format(name),
                line,
                'expected token("..."), name("..."), on.command("/start"): or '
                "on.message(...):",
            )
        if bot.token is None:
            raise DSLParseError(
                "token(...) is missing",
                1,
                1,
                self.source_lines[0] if self.source_lines else "",
                'add token("123456:ABC") at the top',
            )
        if not bot.handlers:
            raise DSLParseError(
                "the bot has no events",
                1,
                1,
                self.source_lines[0] if self.source_lines else "",
                'add on.command("/start"): with an indented block',
            )
        validate(bot, fail=self._validate_fail)
        return bot

    def _validate_fail(self, message: str, line: int, hint: str = "") -> NoReturn:
        # The shared checks report a line; this parser knows the source line too.
        raw = self.source_lines[line - 1] if 0 < line <= len(self.source_lines) else ""
        raise DSLParseError(message, line, 1, raw, hint)

    def _directive(self, bot: BotSpec, name: str, arguments: str, line: _Line) -> bool:
        if name == "token":
            if bot.token is not None:
                self._fail("duplicate token(...)", line, "declare it once")
            # A pasted token arrives with spaces: they are never part of it.
            bot.token = self._string(arguments, line, "token").strip()
            return True
        if name == "name":
            bot.name = self._string(arguments, line, "name")
            return True
        if name == "proxy":
            proxy = self._string(arguments, line, "proxy URL").strip()
            if not proxy.startswith(("socks5://", "socks4://", "http://", "https://")):
                self._fail(
                    "proxy must start with socks5://, socks4://, http:// or https://",
                    line,
                    'proxy("socks5://127.0.0.1:1080")',
                )
            bot.proxy = proxy
            return True
        if name == "webhook":
            url = self._string(arguments, line, "webhook URL").strip()
            if not url.startswith(("http://", "https://")):
                self._fail("the webhook URL must start with http:// or https://", line)
            bot.webhook = url
            return True
        if name == "webhook_path":
            path = self._string(arguments, line, "webhook path").strip()
            if not path.startswith("/"):
                self._fail("the webhook path must start with /", line)
            bot.webhook_path = path
            return True
        if name == "webhook_secret":
            bot.webhook_secret = self._string(arguments, line, "webhook secret").strip()
            return True
        return False

    def _add_state(self, bot: BotSpec, arguments: str, line: _Line) -> None:
        items = _split_arguments(arguments)
        if not items:
            self._fail("state(...) needs a name", line, 'state("order") or state(order)')
        value = items[0].strip()
        name = value[1:-1] if value[:1] in "'\"" else value
        if not _STATE_RE.match(name):
            self._fail(
                "invalid state name {0!r}".format(name),
                line,
                "use letters, digits and _ (for example: state(order))",
            )
        if name in bot.states:
            self._fail("duplicate state {0!r}".format(name), line, "declare it once")
        bot.states.append(name)

    def _split_call(self, line: _Line):
        if line.text in ("pass", "pass()"):
            return "pass", "", False
        match = _CALL_RE.match(line.text)
        if not match:
            self._fail(
                "cannot read this line",
                line,
                'a statement looks like send("Hi") or on.command("/start"):',
            )
        return match.group("name"), match.group("args"), bool(match.group("colon"))

    # ----------------------------------------------------------------- events
    def _parse_event(self, line: _Line, name: str, arguments: str,
                     has_colon: bool) -> Handler:
        if not has_colon:
            self._fail("expected ':' at the end", line, 'write on.command("/start"):')
        self.pos += 1
        items = self._items(arguments, line)

        if name == "on.command":
            if not items:
                self._fail("on.command(...) needs a command", line, 'on.command("/start"):')
            command = str(items[0][0])
            if not _COMMAND_RE.match(command):
                self._fail(
                    "invalid command {0!r}".format(command),
                    line,
                    "a command starts with / and uses letters, digits, underscores",
                )
            params = self._bind_event(self._event("command"), items[1:], line)
            params["command"] = command
            actions = self._parse_block(line)
            return Handler(kind="command", actions=actions, params=params, line=line.number)

        kind = name[3:]
        rest = items
        if kind == "message":
            kind, rest = self._message_kind(items, line)
        spec = event_for(kind)
        if spec is None:
            self._fail(
                "unknown event {0}".format(name),
                line,
                "use on.message(...), on.photo(), on.sticker(), on.any(), "
                "on.callback(...) or on.state(...)",
            )
        params = self._bind_event(spec, rest, line)
        actions = self._parse_block(line)
        if spec.kind == "state" and not str(params.get("state") or ""):
            self._fail("a state handler needs a step", line, 'on.state("order"):')
        return Handler(kind=spec.kind, actions=actions, params=params, line=line.number)

    def _event(self, kind: str) -> EventSpec:
        spec = event_for(kind)
        assert spec is not None, kind
        return spec

    def _message_kind(self, items, line: _Line):
        # on.message(TEXT, "привет") / on.message(PHOTO) / on.message("привет")
        kind = "text"
        rest = list(items)
        if rest:
            value, bare = rest[0]
            if bare:
                upper = str(value).strip().upper()
                if upper in KINDS:
                    kind = KINDS[upper]
                    rest = rest[1:]
                elif str(value) in ("message", "text", "photo", "sticker", "voice",
                                    "video", "document", "animation", "any", "image"):
                    kind = event_for(str(value)).kind if event_for(str(value)) else "text"
                    rest = rest[1:]
        return kind, rest

    def _bind_event(self, spec: EventSpec, items, line: _Line) -> Dict[str, Any]:
        try:
            return bind_arguments(spec, items)
        except BindError as error:
            self._fail(error.message, line, error.hint or "")

    # ---------------------------------------------------------------- blocks
    def _parse_block(self, header: _Line) -> List[object]:
        if self.pos >= len(self.lines) or self.lines[self.pos].indent <= header.indent:
            self._fail(
                "expected an indented block",
                header,
                "indent the body by 4 spaces",
            )
        indent = self.lines[self.pos].indent
        actions: List[object] = []
        style = "inline"
        while self.pos < len(self.lines):
            line = self.lines[self.pos]
            if line.indent < indent:
                break
            if line.indent > indent:
                self._fail("unexpected indentation", line, "align it with the block")

            name, arguments, has_colon = self._split_call(line)

            if name == "buttons":
                style = self._string(arguments, line, "keyboard style")
                if style not in ("inline", "reply"):
                    self._fail('buttons("...") expects "inline" or "reply"', line)
                self.pos += 1
                continue

            if name == "button":
                actions = self._add_button(actions, line, arguments, style)
                self.pos += 1
                continue

            if name == "send":
                actions.append(Action(kind="send", line=line.number,
                                      params={"text": self._string(arguments, line)}))
                self.pos += 1
                # A deeper indented block belongs to this send: its buttons.
                if self.pos < len(self.lines) and self.lines[self.pos].indent > indent:
                    actions = self._parse_buttons_block(
                        actions, self.lines[self.pos].indent, style
                    )
                continue

            if name == "when":
                if not has_colon:
                    self._fail('expected ":" after when(...)', line)
                condition = self._condition(arguments, line)
                self.pos += 1
                node = When(condition=condition, then=self._parse_block(line),
                            orelse=[], line=line.number)
                actions.append(node)
                continue

            if name == "otherwise":
                if not has_colon:
                    self._fail('expected ":" after otherwise()', line)
                if not actions or not isinstance(actions[-1], When):
                    self._fail(
                        "otherwise() without when()",
                        line,
                        "put it right after an indented when(...) block",
                    )
                self.pos += 1
                actions[-1].orelse = self._parse_block(line)
                continue

            if name in ("pass", "nothing"):
                actions.append(Action(kind="nothing", line=line.number))
                self.pos += 1
                continue

            spec = action_for(name)
            if spec is None:
                self._fail(
                    "unknown statement {0}()".format(name),
                    line,
                    "inside a block use send(), button(), buttons(), when(), "
                    "send_photo(), delete(), delay() or set_state()",
                )
            if spec.kind == "when":
                self._fail("use when(...) with an operator", line,
                           'when("contains", "hi"):')
            try:
                params = bind_arguments(spec, self._items(arguments, line))
            except BindError as error:
                self._fail(error.message, line, error.hint or "")
            actions.append(Action(kind=spec.kind, params=params, line=line.number))
            self.pos += 1
        return actions

    def _parse_buttons_block(self, actions: List[object], indent: int,
                             style: str) -> List[object]:
        # Buttons nested under send(...) keep the indentation obvious:
        #     send("Привет")
        #         button("Помощь", "/help")
        while self.pos < len(self.lines):
            line = self.lines[self.pos]
            if line.indent < indent:
                break
            if line.indent > indent:
                self._fail("unexpected indentation", line, "align the buttons")
            name, arguments, _ = self._split_call(line)
            if name == "buttons":
                style = self._string(arguments, line, "keyboard style")
                if style not in ("inline", "reply"):
                    self._fail('buttons("...") expects "inline" or "reply"', line)
                self.pos += 1
                continue
            if name != "button":
                self._fail(
                    "only button() belongs under send()",
                    line,
                    'write button("Помощь", "/help")',
                )
            actions = self._add_button(actions, line, arguments, style)
            self.pos += 1
        return actions

    def _add_button(self, actions: List[object], line: _Line, arguments: str,
                    style: str) -> List[object]:
        parts = _split_arguments(arguments)
        if not parts:
            self._fail("button() needs a label", line, 'button("Помощь", "/help")')
        label = self._string(parts[0], line, "button label")
        target = None
        url = None
        request = ""
        for extra in parts[1:]:
            extra = extra.strip()
            if extra.startswith("url="):
                url = self._string(extra[4:], line, "URL")
            elif extra.startswith("web_app="):
                url = self._string(extra[8:], line, "URL")
                request = "web_app"
            elif extra.startswith("contact="):
                request = "contact" if _truthy(extra[8:]) else ""
            elif extra.startswith("location="):
                request = "location" if _truthy(extra[8:]) else ""
            else:
                target = self._string(extra, line, "button target")

        button = Button(label=label, line=line.number)
        if request in ("contact", "location"):
            if style != "reply":
                self._fail(
                    'requesting "%s" works only in a reply keyboard' % request,
                    line,
                    'put buttons("reply") before the button',
                )
            button.kind = request
        elif url is not None:
            if not url.startswith(("http://", "https://")):
                self._fail("URL must start with http:// or https://", line)
            button.kind = "web_app" if request == "web_app" else "url"
            button.target = url
        elif target is not None:
            if style == "reply":
                self._fail(
                    "reply buttons send their label as text",
                    line,
                    'drop the second argument, or use buttons("inline")',
                )
            if not _COMMAND_RE.match(target):
                self._fail(
                    "button target must look like /help",
                    line,
                    'for a link use button("Сайт", url="https://...")',
                )
            button.kind = "command"
            button.target = target

        if actions and isinstance(actions[-1], Action) and actions[-1].kind == "send":
            actions.append(Buttons(style=style, items=[button], line=line.number))
        elif actions and isinstance(actions[-1], Buttons):
            actions[-1].items.append(button)
        else:
            self._fail("button() must follow send()", line, "put send(...) right before it")
        return actions

    def _condition(self, arguments: str, line: _Line) -> Condition:
        extra_values: List[str] = []
        if ";" in arguments:
            chunks = _split_semicolons(arguments)
            arguments = chunks[0]
            for chunk in chunks[1:]:
                extra_values.append(self._string(chunk.strip(), line, "value"))
        condition = self._single_condition(arguments, line)
        condition.values = tuple(extra_values)
        return condition

    def _single_condition(self, arguments: str, line: _Line) -> Condition:
        parts = [part.strip() for part in _split_arguments(arguments)]
        source = "text"
        if len(parts) >= 2:
            first = self._bare(parts[0])
            if first in ("dice", "text"):
                # when("dice", "==", 6) / when("dice", 6) / when("text", "contains", "hi")
                source = first
                parts = parts[1:]
        if source == "dice":
            return self._dice_condition(parts, line)
        if len(parts) == 1:
            op, value = "==", self._string(parts[0], line, "value")
        elif len(parts) == 2:
            first = parts[0].strip()
            candidate = self._string(first, line, "operator") if first[:1] in "'\"" else first
            if candidate not in OPS:
                self._fail(
                    "unknown operator {0!r}".format(candidate),
                    line,
                    "operators: {0}".format(", ".join(OPS)),
                )
            op = candidate
            value = self._string(parts[1], line, "value")
        else:
            self._fail(
                "cannot read the condition",
                line,
                'use when("hi"), when("contains", "hi") or when("dice", "==", 6)',
            )
        return Condition(op=op, value=value, line=line.number, source=source)

    def _bare(self, part: str) -> str:
        return part[1:-1] if part[:1] in "'\"" and part[-1:] == part[:1] else part

    def _dice_condition(self, parts, line: _Line) -> Condition:
        # The interactive emoji gives a number: compare it with == or !=.
        if len(parts) == 1:
            op, raw = "==", self._bare(parts[0])
        elif len(parts) == 2:
            op, raw = self._bare(parts[0]), self._bare(parts[1])
        else:
            self._fail("cannot read the condition", line, 'when("dice", "==", 6)')
        if op not in ("==", "!="):
            self._fail(
                "для интерактивного эмодзи подходят только == и !=",
                line,
                'when("dice", "==", 6)',
            )
        if not raw.lstrip("-").isdigit():
            self._fail(
                "для интерактивного эмодзи нужно число",
                line,
                'кубик даёт 1-6: when("dice", "==", 6)',
            )
        return Condition(op=op, value=raw, line=line.number, source="dice")


def _truthy(raw: str) -> bool:
    return raw.strip().strip("'\"").lower() in ("1", "true", "yes", "on", "да")


def _split_semicolons(text: str) -> List[str]:
    # Split on ';' outside of quotes: when("contains", "a";"b")
    parts: List[str] = []
    current: List[str] = []
    quote = ""
    escape = False
    for char in text:
        if escape:
            current.append(char)
            escape = False
            continue
        if char == "\\":
            current.append(char)
            escape = True
            continue
        if quote:
            current.append(char)
            if char == quote:
                quote = ""
            continue
        if char in "\"'":
            quote = char
            current.append(char)
            continue
        if char == ";":
            parts.append("".join(current))
            current = []
            continue
        current.append(char)
    parts.append("".join(current))
    return parts


def parse_text(source: str, filename: str = "<text>") -> BotSpec:
    # Parse the Python-looking text syntax into the shared BotSpec tree.
    return _Parser(source, filename).parse()


def compile_text(source: str, filename: str = "<text>", embed_token: bool = True) -> str:
    # Text syntax -> aiogram 3 source code.
    from .dsl.codegen import generate

    return generate(parse_text(source, filename), embed_token=embed_token)
""",
    "src/tgblocks/visual/__init__.py": r"""# Browser-based visual block editor for the tgblocks DSL.

from .server import serve

__all__ = ["serve"]
""",
    "src/tgblocks/visual/server.py": r"""# Tiny localhost HTTP server that hosts the visual editors.
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
""",
    "src/tgblocks/visual/static/blocks.html": r"""
<!DOCTYPE html>
<html lang="en" translate="no">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title data-i18n="title_blocks">tgblocks - blocks</title>
<style>
  :root { --chip:#1b2033; --chip-hover:#242b48; --field:#11151f; --scroll:#3a4166; --log:#0b0e16; --log-fg:#9aa2c6; --flyout:#1d2136; --tok-key:#c98bff; --tok-fn:#7ee0a8; --tok-str:#f0a35e; --tok-num:#5b8cff; --tok-com:#5d6488; --tok-pun:#8d93b4; --bg:#0f1220; --panel:#171a2b; --line:#282d47; --fg:#e8eaf4; --muted:#8d93b4;
          --accent:#5b8cff; --ok:#7ee0a8; --err:#ff8f8f; }
  * { box-sizing: border-box; }
  html, body { height: 100%; }
  body { margin:0; display:flex; flex-direction:column; background:var(--bg); color:var(--fg);
         font:14px/1.5 "Segoe UI", system-ui, -apple-system, sans-serif; }
  header { display:flex; align-items:center; gap:10px; padding:10px 14px;
           background:var(--panel); border-bottom:1px solid var(--line); }
  h1 { margin:0; font-size:14px; font-weight:600; letter-spacing:.4px; }
  h1 span { color:var(--muted); font-weight:400; }
  .spacer { flex:1; }
  button { font:inherit; color:var(--fg); background:var(--chip-hover); border:1px solid var(--line);
           border-radius:6px; padding:7px 12px; cursor:pointer; }
  button:hover { background:#2c3260; }
  button.primary { background:var(--accent); border-color:var(--accent); color:#fff; font-weight:600; }
  a.nav { color:var(--muted); text-decoration:none; padding:7px 10px; border:1px solid var(--line);
          border-radius:6px; }
  main { flex:1; display:flex; min-height:0; }
  #blockly { flex:1 1 60%; min-width:300px; height:100%; }
  aside { flex:1 1 40%; min-width:280px; display:flex; flex-direction:column;
          border-left:1px solid var(--line); }
  .tabs { display:flex; gap:6px; padding:8px 12px; background:var(--panel);
          border-bottom:1px solid var(--line); }
  .tab { padding:5px 12px; border-radius:6px; color:var(--muted); cursor:pointer; }
  .tab.active { color:var(--fg); background:var(--chip-hover); }
  pre { flex:1; margin:0; padding:14px; overflow:auto; white-space:pre; tab-size:4;
        font:12.5px/1.55 "Cascadia Code", Consolas, "Courier New", monospace; }
  #status { min-height:38px; padding:9px 12px; border-top:1px solid var(--line);
            color:var(--muted); white-space:pre-wrap; font-size:12.5px; }
  #status.ok { color:var(--ok); } #status.error { color:var(--err); }
  #pane-log { color:var(--log-fg); }
  .hidden { display:none !important; }
  .file-name { color:var(--muted); font-size:12px; padding:0 4px; }
  /* no hairline frames around the workspace and toolbox */
  .blocklyMainBackground { stroke: none !important; }
  .blocklyToolboxDiv, .blocklyFlyout, .blocklyFlyoutBackground { border: 0 !important; }
  .blocklyFlyoutBackground { fill: var(--flyout) !important; }
  .blocklyTreeRow { border: 0 !important; }
</style>
</head>
<body>
<header>
  <h1>tgblocks <span data-i18n="page_blocks">blocks</span></h1>
  <span class="spacer"></span>
  <button id="btn-open" data-i18n="open" title="открыть файл бота">Открыть файл…</button>
  <span id="file-name" class="file-name">bot1</span>
  <button id="btn-download-py" data-i18n="download">Download .py</button>
  <button id="btn-compile" class="primary" data-i18n="compile">Compile</button>
  <button id="btn-run" data-i18n="run">▶ Запустить</button>
  <button id="btn-stop" data-i18n="stop">■ Стоп</button>
  <a class="nav" href="/nodes" data-i18n="view_nodes">Вид: узлы</a>
  <a class="nav" href="/text" data-i18n="view_text">Вид: текст</a>
</header>
<main>
  <input id="import" type="file" accept=".py,.txt,.tg" class="hidden" />
  <div id="blockly"></div>
  <aside>
    <div class="tabs">
      <div class="tab active" data-pane="text" data-i18n="tab_text">Текст</div>
      <div class="tab" data-pane="code" data-i18n="tab_python">Python (aiogram 3)</div>
      <div class="tab" data-pane="logs" data-i18n="tab_logs">Логи</div>
    </div>
    <pre id="pane-text"></pre>
    <pre id="pane-code" class="hidden"></pre>
    <pre id="pane-log" class="hidden"></pre>
    <div id="status">Loading Blockly...</div>
  </aside>
</main>
<script src="/tgblocks-project.js"></script>
<script src="/tgblocks-ui.js"></script>
<!-- Blockly ships with the package: the block editor works without internet. -->
<script src="/vendor/blockly.js"></script>
<script>
  // A missing local copy falls back to the CDN; if both fail the page says so
  // instead of hanging on "Loading Blockly…".
  if (!window.Blockly) {
    document.write('<script src="https://unpkg.com/blockly@10.4.3/blockly_compressed.js">'
                   + "\u003c/script>");
  }
</script>
<script>
(function () {
  "use strict";

  // One-line translator for the few words that live in this page, not in the
  // catalogue: L("по-русски", "in english").
  function L(ru, en) {
    return (window.TgUi && TgUi.lang() === "en" && en) ? en : ru;
  }

  var dslPane = document.getElementById("pane-text");
  var codePane = document.getElementById("pane-code");
  var statusEl = document.getElementById("status");
  var fileNameEl = document.getElementById("file-name");
  var importInput = document.getElementById("import");
  var workspace = null;
  var THEMES = {};
  var lastDsl = "", lastCode = "", lastHasToken = false;
  var loading = false;      // true while the board is being rebuilt from text

  function setStatus(text, kind) {
    statusEl.textContent = text;
    statusEl.className = kind || "";
  }

  function literal(value) {
    return JSON.stringify(String(value == null ? "" : value));
  }

  function workspaceXml() {
    // The workspace goes to the server as XML: the same Python converter that
    // draws this canvas from text turns it back, so there is no second DSL
    // writer here to drift away from the real one.
    return Blockly.Xml.domToText(Blockly.Xml.workspaceToDom(workspace));
  }

  async function compileWorkspace() {
    // An empty canvas is "delete everything": tell the shared document, so the
    // other two views do not keep showing the bot that no longer exists here.
    if (workspace && workspace.getTopBlocks(false).length === 0) {
      lastDsl = "";
      lastCode = "";
      dslPane.textContent = "";
      codePane.textContent = "";
      if (!loading) { TgProject.saveText(""); }
      setStatus(L("Пусто. Перетащи блок «токен» из палитры.", "Empty. Drag the token block from the palette."), "ok");
      return;
    }
    var xml;
    try {
      xml = workspaceXml();
    } catch (error) {
      setStatus(String(error && error.message ? error.message : error), "error");
      return;
    }
    try {
      var response = await fetch("/api/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ xml: xml })
      });
      var data = await response.json();
      if (!data.ok) {
        // An unfinished canvas: the last good text stays in the project.
        setStatus(data.detail || data.error || "Compilation failed.", "error");
        return;
      }
      lastDsl = data.text || "";
      lastCode = data.code || "";
      lastHasToken = !!data.has_token;
      dslPane.textContent = lastDsl;
      codePane.textContent = lastCode;
      if (!loading) { TgProject.saveText(lastDsl); }
      var warnings = data.warnings || [];
      var line = TgUi.fmt("status_ok_lines", { lines: lastCode.split("\n").length });
      if (warnings.length) { line += " · " + warnings.join("; "); }
      setStatus(line, "ok");
    } catch (error) {
      setStatus("Cannot reach the tgblocks server: " + error, "error");
    }
  }

  var compileTimer = null;
  function scheduleCompile() {
    clearTimeout(compileTimer);
    compileTimer = setTimeout(compileWorkspace, 400);
  }

  function download(name, text, mime) {
    var blob = new Blob([text], { type: mime || "text/plain;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    link.href = url;
    link.download = name;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  // Rebuild the canvas from the shared text (used on load and on every change
  // that arrives from another view).
  async function renderText(text) {
    dslPane.textContent = text;
    if (!text.trim()) {
      loading = true;
      workspace.clear();
      loading = false;
      setStatus(L("Пустой бот: перетащи блок «bot token» из палитры.", "Empty bot: drag the bot token block from the palette."));
      return;
    }
    var response = await fetch("/api/to_blocks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source: text })
    });
    var data = await response.json();
    if (!data.ok) {
      setStatus(data.detail || data.error || L("не удалось показать текст блоками", "cannot show the text as blocks"), "error");
      return;
    }
    var xml = Blockly.utils.xml.textToDom(data.xml);
    loading = true;
    workspace.clear();
    Blockly.Xml.domToWorkspace(xml, workspace);
    loading = false;
    compileWorkspace();
    setStatus(L("Файл: ", "File: ") + TgProject.currentName() + L(" · собран из общего текста", " · built from the shared text"), "ok");
  }

  async function loadProject(name) {
    try {
      var data = await TgProject.load(name);
      fileNameEl.textContent = data.name;
      await renderText(data.text);
    } catch (error) {
      setStatus(L("Не удалось открыть бота: ", "Could not open the bot: ") + error.message, "error");
    }
  }

  // ---------------------------------------------------------------- catalogue
  var SCHEMA = null;
  var ACTIONMAP = {};
  var EVENTMAP = {};

  var GROUP_COLOUR = {
    message: "#1f7a4d", media: "#1f7a4d", keyboard: "#7ee0a8", logic: "#c98bff",
    state: "#d05c9b", moderation: "#c0392b", service: "#4a5a7a", event: "#f0a35e"
  };

  async function loadSchema() {
    try {
      var response = await fetch("/api/schema?lang=" +
                                 (window.TgUi ? TgUi.lang() : "ru"));
      var data = await response.json();
      if (!data || !data.actions) { return; }
      SCHEMA = data;
      data.actions.forEach(function (item) { ACTIONMAP[item.kind] = item; });
      data.events.forEach(function (item) { EVENTMAP[item.kind] = item; });
    } catch (error) {
      setStatus(L("Не удалось получить схему блоков: ", "Could not load the block catalogue: ") + error, "error");
    }
  }

  function blockTypeOf(kind) {
    return "tg_" + (kind === "send_photo" ? "photo" : kind);
  }

  // Action blocks come ready-made from /api/schema: Blockly numbers placeholders
  // per message (message1 starts again at %1), and that rule lives in Python
  // where a test can check it. The page only re-colours them.

  // The structural blocks are written by hand: they carry statement slots.
  var STRUCTURAL = ["send", "when", "otherwise", "buttons", "button"];

  function defineBlocksFromSchema() {
    var definitions = [];

    definitions.push({
      type: "tg_bot",
      message0: L("токен %1", "token %1"),
      args0: [{ type: "field_input", name: "TOKEN", text: "123456:REPLACE_WITH_YOUR_TOKEN" }],
      message1: L("имя %1", "name %1"),
      args1: [{ type: "field_input", name: "NAME", text: "" }],
      message2: L("прокси %1", "proxy %1"),
      args2: [{ type: "field_input", name: "PROXY", text: "" }],
      message3: "webhook %1",
      args3: [{ type: "field_input", name: "WEBHOOK", text: "" }],
      message4: "%1",
      args4: [{ type: "input_statement", name: "DO" }],
      colour: "#2f4fa8",
      tooltip: L("Токен от @BotFather и события внутри.", "The @BotFather token, with events inside.")
    });

    var kindOptions = (SCHEMA ? SCHEMA.events : []).map(function (item) {
      return [window.TgUi ? TgUi.tr(item) : item.label, item.kind];
    });

    definitions.push({
      type: "tg_on",
      message0: L("событие %1", "event %1"),
      args0: [{ type: "field_dropdown", name: "KIND",
                options: kindOptions.length ? kindOptions : [["команда", "command"]] }],
      message1: L("команда %1", "command %1"),
      args1: [{ type: "field_input", name: "COMMAND", text: "/start" }],
      message2: L("тексты %1", "texts %1"),
      args2: [{ type: "field_input", name: "PATTERNS", text: "" }],
      message3: L("данные кнопки %1", "button data %1"),
      args3: [{ type: "field_input", name: "DATA", text: "" }],
      message4: L("шаг %1", "step %1"),
      args4: [{ type: "field_input", name: "STATE", text: "" }],
      message5: L("чат %1", "chat %1"),
      args5: [{ type: "field_dropdown", name: "CHAT",
                options: [[L("любой", "any"), ""], [L("личка", "private"), "private"], [L("группа", "group"), "group"],
                          [L("супергруппа", "supergroup"), "supergroup"], [L("канал", "channel"), "channel"]] }],
      message6: L("ID автора %1", "author ID %1"),
      args6: [{ type: "field_input", name: "FROM_USER", text: "" }],
      message7: L("регулярка %1", "regex %1"),
      args7: [{ type: "field_input", name: "REGEX", text: "" }],
      message8: "%1",
      args8: [{ type: "input_statement", name: "DO" }],
      previousStatement: null,
      nextStatement: null,
      colour: "#c26a1f",
      tooltip: L("Реакция на команду, сообщение, кнопку или шаг диалога.", "React to a command, a message, a button press or a dialogue step.")
    });

    definitions.push({
      type: "tg_send",
      message0: L("сообщение %1", "message %1"),
      args0: [{ type: "field_input", name: "TEXT", text: "Привет!" }],
      message1: L("кнопки %1", "buttons %1"),
      args1: [{ type: "input_statement", name: "DO" }],
      previousStatement: null,
      nextStatement: null,
      colour: "#1f7a4d",
      tooltip: L("Отправить текст; клавиатура вкладывается внутрь.", "Send text; a keyboard nests inside.")
    });

    definitions.push({
      type: "tg_buttons",
      message0: L("клавиатура %1", "keyboard %1"),
      args0: [{ type: "field_dropdown", name: "STYLE",
                options: [["inline", "inline"], ["reply", "reply"]] }],
      message1: "%1",
      args1: [{ type: "input_statement", name: "DO" }],
      previousStatement: null,
      nextStatement: null,
      colour: "#7ee0a8",
      tooltip: L("Набор кнопок под сообщением.", "A set of buttons under the message.")
    });

    definitions.push({
      type: "tg_button",
      message0: L("кнопка %1 -> %2", "button %1 -> %2"),
      args0: [
        { type: "field_input", name: "LABEL", text: "Кнопка" },
        { type: "field_input", name: "TARGET", text: "/help" }
      ],
      message1: L("вид %1", "kind %1"),
      args1: [{ type: "field_dropdown", name: "KIND",
                options: [[L("команда", "command"), "command"], [L("ссылка", "link"), "url"],
                          ["web app", "web_app"], [L("телефон", "phone"), "contact"],
                          [L("геолокация", "location"), "location"]] }],
      previousStatement: null,
      nextStatement: null,
      colour: "#7ee0a8",
      tooltip: L("Кнопка: команда, ссылка или запрос телефона/геолокации.", "A button: a command, a link, or a phone/location request.")
    });

    definitions.push({
      type: "tg_when",
      message0: L("если %1 %2 %3", "if %1 %2 %3"),
      args0: [
        { type: "field_dropdown", name: "SOURCE",
          options: [[L("текст", "text"), "text"], [L("эмодзи", "emoji"), "dice"]] },
        { type: "field_dropdown", name: "OP",
          options: [[L("содержит", "contains"), "contains"], [L("равно", "equals"), "=="],
                    [L("не равно", "not equal"), "!="], [L("начинается с", "starts with"), "startswith"],
                    [L("кончается на", "ends with"), "endswith"]] },
        { type: "field_input", name: "VALUE", text: "привет" }
      ],
      message1: L("ещё значения %1", "more values %1"),
      args1: [{ type: "field_input", name: "VALUES", text: "" }],
      message2: L("то %1", "then %1"),
      args2: [{ type: "input_statement", name: "DO" }],
      message3: L("иначе %1", "else %1"),
      args3: [{ type: "input_statement", name: "ELSE" }],
      previousStatement: null,
      nextStatement: null,
      colour: "#c98bff",
      tooltip: L("Проверка текста сообщения.", "A check on the message text or the emoji value.")
    });

    definitions.push({
      type: "tg_otherwise",
      message0: L("иначе", "else"),
      message1: "%1",
      args1: [{ type: "input_statement", name: "DO" }],
      previousStatement: null,
      nextStatement: null,
      colour: "#c98bff",
      tooltip: L("Ветка «иначе» для условия рядом.", "The else branch of the condition nearby.")
    });

    (SCHEMA && SCHEMA.blocks ? SCHEMA.blocks : []).forEach(function (block) {
      definitions.push(block);
    });

    Blockly.defineBlocksWithJsonArray(definitions);
  }

  function buildToolbox() {
    var contents = [
      { kind: "category", name: L("Бот", "Bot"), colour: "#5b8cff",
        contents: [{ kind: "block", type: "tg_bot" }] },
      { kind: "category", name: L("События", "Events"), colour: "#f0a35e",
        contents: [{ kind: "block", type: "tg_on" }] }
    ];
    var order = [["message", "Сообщения"], ["media", "Медиа"],
                 ["keyboard", "Клавиатура"], ["logic", "Логика"],
                 ["state", "Диалоги"], ["moderation", "Модерация"],
                 ["service", "Сервис"]];
    var actions = SCHEMA ? SCHEMA.actions : [];
    var groupName = {};
    if (SCHEMA) {
      SCHEMA.groups.forEach(function (group) {
        groupName[group.kind] = window.TgUi ? TgUi.tr(group) : group.label;
      });
    }
    order.forEach(function (pair) {
      var blocks = actions.filter(function (item) { return item.group === pair[0]; })
        .map(function (item) { return { kind: "block", type: blockTypeOf(item.kind) }; });
      if (pair[0] === "keyboard") {
        blocks.push({ kind: "block", type: "tg_buttons" });
        blocks.push({ kind: "block", type: "tg_button" });
      }
      if (!blocks.length) { return; }
      contents.push({ kind: "category", name: groupName[pair[0]] || pair[1],
                      colour: GROUP_COLOUR[pair[0]] || "#7ee0a8", contents: blocks });
    });
    return { kind: "categoryToolbox", contents: contents };
  }

  async function boot() {
    if (typeof Blockly === "undefined") {
      setStatus("Blockly could not be loaded from the CDN. Check your internet connection, " +
                "or use the node editor at /nodes.", "error");
      return;
    }
    await loadSchema();

    defineBlocksFromSchema();

    var darkTheme = Blockly.Theme.defineTheme("tgblocks-dark", {
      base: Blockly.Themes.Classic,
      componentStyles: {
        workspaceBackgroundColour: "#0f1220",
        toolboxBackgroundColour: "#171a2b",
        toolboxForegroundColour: "#e8eaf4",
        flyoutBackgroundColour: "var(--flyout)",
        flyoutForegroundColour: "#c9cee6",
        flyoutOpacity: 0.95,
        scrollbarColour: "var(--scroll)",
        insertionMarkerColour: "#5b8cff",
        insertionMarkerOpacity: 0.4,
        cursorColour: "#5b8cff"
      }
    });

    // The same canvas for the light interface theme.
    var lightTheme = Blockly.Theme.defineTheme("tgblocks-light", {
      base: Blockly.Themes.Classic,
      componentStyles: {
        workspaceBackgroundColour: "#f4f6fb",
        toolboxBackgroundColour: "#ffffff",
        toolboxForegroundColour: "#1a1e2b",
        flyoutBackgroundColour: "#eef1f8",
        flyoutForegroundColour: "#1a1e2b",
        flyoutOpacity: 0.98,
        scrollbarColour: "#c3cada",
        insertionMarkerColour: "#3b6cf0",
        insertionMarkerOpacity: 0.4,
        cursorColour: "#3b6cf0"
      }
    });

    THEMES = { dark: darkTheme, light: lightTheme };
    var activeTheme = (window.TgUi && TgUi.theme() === "light") ? lightTheme : darkTheme;

    var toolbox = buildToolbox();

    workspace = Blockly.inject("blockly", {
      toolbox: toolbox,
      theme: activeTheme,
      grid: { spacing: 26, length: 3, colour: "#222741", snap: true },
      zoom: { controls: true, wheel: true, startScale: 0.85, maxScale: 2, minScale: 0.4 },
      trashcan: true,
      move: { scrollbars: true, drag: true, wheel: true }
    });

    workspace.addChangeListener(function (event) {
      if (event.isUiEvent || loading) { return; }
      scheduleCompile();
    });

    TgProject.configure({
      status: setStatus,
      reload: async function (fresh) {
        fileNameEl.textContent = TgProject.currentName();
        await renderText(fresh.text);
      }
    });

    document.getElementById("btn-open").addEventListener("click", function () {
      importInput.value = "";
      importInput.click();
    });

    importInput.addEventListener("change", function () {
      var file = importInput.files[0];
      if (!file) { return; }
      var reader = new FileReader();
      reader.onload = function () {
        var name = file.name.replace(/\.[^.]+$/, "").replace(/[^A-Za-z0-9_-]/g, "") || "bot1";
        var text = String(reader.result || "").replace(/^\uFEFF/, "");
        var converted = fetch("/api/to_blocks", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ source: text })
        });
        converted.then(function (response) {
          return response.json();
        }).then(function (data) {
          if (!data.ok) {
            setStatus(L("Это не текст бота: ", "That is not bot text: ") + (data.detail || data.error), "error");
            return;
          }
          TgProject.setName(name);
          fileNameEl.textContent = name;
          TgProject.saveText(text);
          TgProject.flush();
          var xml = Blockly.utils.xml.textToDom(data.xml);
          loading = true;
          workspace.clear();
          Blockly.Xml.domToWorkspace(xml, workspace);
          loading = false;
          dslPane.textContent = text;
          compileWorkspace();
          setStatus(L("Открыт файл: ", "Opened file: ") + file.name, "ok");
        });
      };
      reader.readAsText(file);
      importInput.value = "";
    });

    loadProject(TgProject.currentName());

    document.getElementById("btn-compile").addEventListener("click", compileWorkspace);

    var logPane = document.getElementById("pane-log");
    var logSince = 0;
    var logTimer = null;

    async function pollLogs() {
      try {
        var response = await fetch("/api/logs?since=" + logSince);
        var data = await response.json();
        if (data.lines.length) {
          logPane.textContent += data.lines.join("\n") + "\n";
          logPane.scrollTop = logPane.scrollHeight;
        }
        logSince = data.total;
        document.getElementById("btn-stop").disabled = !data.running;
      } catch (error) {
        /* server is gone */
      }
    }

    async function runBot() {
      if (!lastCode) { setStatus("Compile first.", "error"); return; }
      // Ask only when the bot block has no token; otherwise just start it.
      var token = "";
      if (!lastHasToken) {
        var entered = window.prompt(
          "У бота нет токена. Впиши его (Enter - взять из TG_BOT_TOKEN):", "");
        if (entered === null) { return; }
        token = entered;
      }
      var response = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: lastCode, token: token })
      });
      var data = await response.json();
      if (!data.ok) { setStatus(data.error || L("не запустилось", "did not start"), "error"); return; }
      logSince = 0;
      logPane.textContent = "";
      document.querySelector('[data-pane="logs"]').click();
      setStatus(L("Запущен (pid ", "Running (pid ") + data.pid + ").", "ok");
      if (!logTimer) { logTimer = setInterval(pollLogs, 1000); }
      pollLogs();
    }

    document.getElementById("btn-run").addEventListener("click", runBot);
    document.getElementById("btn-stop").addEventListener("click", async function () {
      await fetch("/api/stop", { method: "POST" });
      setStatus(L("Остановлен.", "Stopped."), "ok");
      pollLogs();
    });
    document.getElementById("btn-stop").disabled = true;
    document.getElementById("btn-download-py").addEventListener("click", function () {
      download("bot.py", lastCode, "text/x-python;charset=utf-8");
    });
    document.querySelectorAll(".tab").forEach(function (tab) {
      tab.addEventListener("click", function () {
        document.querySelectorAll(".tab").forEach(function (other) {
          other.classList.toggle("active", other === tab);
        });
        var pane = tab.dataset.pane;
        dslPane.classList.toggle("hidden", pane !== "text");
        codePane.classList.toggle("hidden", pane !== "code");
        document.getElementById("pane-log").classList.toggle("hidden", pane !== "logs");
      });
    });
    document.addEventListener("keydown", function (event) {
      if ((event.ctrlKey || event.metaKey) && event.key === "Enter") { compileWorkspace(); }
    });

    setStatus(L("Перетащи блок «bot token» из палитры - файл подхватится из общего проекта.", "Drag the bot token block from the palette - the file comes from the shared project."));
  }

  boot();

  // Blockly needs its own theme switch, and its block captions are baked into the
  // definitions, so a language change reloads the page. Only a real click in the
  // settings panel does that: reloading on boot (when the language comes from the
  // browser or from ?lang=) would loop forever.
  window.TgUiOnChange = function (state) {
    if (workspace && THEMES[state.theme]) { workspace.setTheme(THEMES[state.theme]); }
  };
  window.TgUiOnLanguage = function () { window.location.reload(); };
})();
</script>
</body>
</html>
""",
    "src/tgblocks/visual/static/nodes.html": r"""
<!DOCTYPE html>
<html lang="ru" translate="no">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title data-i18n="title_nodes">tgblocks - узлы</title>
<style>
  :root { --chip:#1b2033; --chip-hover:#242b48; --field:#11151f; --scroll:#3a4166; --log:#0b0e16; --log-fg:#9aa2c6; --flyout:#1d2136; --tok-key:#c98bff; --tok-fn:#7ee0a8; --tok-str:#f0a35e; --tok-num:#5b8cff; --tok-com:#5d6488; --tok-pun:#8d93b4; --bg:#0e111c; --panel:#161a28; --line:#272c42; --fg:#e8eaf4; --muted:#8d93b4;
          --accent:#5b8cff; --ok:#7ee0a8; --err:#ff8f8f; --node:#1d2233; }
  * { box-sizing: border-box; }
  html, body { height: 100%; }
  body { margin:0; display:flex; flex-direction:column; background:var(--bg); color:var(--fg);
         font:13px/1.45 "Segoe UI", system-ui, -apple-system, sans-serif; overflow:hidden; }
  header { display:flex; flex-wrap:wrap; align-items:center; gap:6px; padding:8px 12px;
           background:var(--panel); border-bottom:1px solid var(--line); }
  header h1 { margin:0 8px 0 0; font-size:13px; font-weight:600; letter-spacing:.3px; }
  header h1 span { color:var(--muted); font-weight:400; }
  .spacer { flex:1; }
  button { font:inherit; color:var(--fg); background:var(--chip-hover); border:1px solid var(--line);
           border-radius:6px; padding:5px 9px; cursor:pointer; white-space:nowrap; }
  button:hover { background:#2c3260; }
  button.primary { background:var(--accent); border-color:var(--accent); color:#fff; font-weight:600; }
  button.tool { padding:5px 8px; min-width:30px; }
  .file-name { color:var(--muted); font-size:12px; padding:0 4px; }
  main { flex:1; display:flex; min-height:0; }
  #canvas { position:relative; flex:1 1 auto; min-width:200px; overflow:hidden;
            background-image:radial-gradient(#20243a 1px, transparent 1px);
            background-size:26px 26px; cursor:grab; }
  #canvas.panning { cursor:grabbing; }
  #viewport { position:absolute; left:0; top:0; transform-origin:0 0; }
  #wires { position:absolute; left:0; top:0; pointer-events:auto; }
  #nodes { position:absolute; left:0; top:0; }
  .node { position:absolute; width:auto; min-width:250px; max-width:520px;
          background:var(--node); border:0;
          border-radius:10px; box-shadow:0 4px 14px rgba(0,0,0,.35); cursor:grab;
          user-select:none; }
  .node:active { cursor:grabbing; }
  .node.selected { box-shadow:0 0 0 2px rgba(91,140,255,.55); }
  .node.ok { border-color:#7ee0a8; box-shadow:0 0 0 2px rgba(126,224,168,.35); }
  .node.bad { opacity:.45; }
  .node-head { display:flex; align-items:center; gap:6px; padding:6px 8px;
               border-bottom:1px solid var(--line); }
  .node-head .kind { font-weight:600; font-size:12px; letter-spacing:.2px; }
  .node-head .badge { margin-left:auto; color:var(--muted); font-size:11px; max-width:110px;
                      overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .node-head .del { padding:0 6px; background:transparent; border:0; color:var(--muted); }
  .node-head .del:hover { color:var(--err); }
  .node-note { color:var(--muted); font-size:12px; padding:2px 0; }
  .node-body { padding:7px 8px 9px; display:flex; flex-direction:column; gap:6px; }
  .node-body input, .node-body select {
      font:inherit; width:100%; min-width:0; padding:4px 6px; color:var(--fg);
      background:var(--field); border:1px solid var(--line); border-radius:5px; cursor:text; }
  .node-body select { cursor:pointer; }
  .node-body input:focus, .node-body select:focus { outline:none; border-color:var(--accent); }
  /* a condition can compare against any number of texts, added one by one */
  .value-row { display:flex; gap:4px; align-items:center; }
  .value-row input { flex:1; }
  .value-del { flex:0 0 auto; width:26px; padding:4px 0; text-align:center;
               background:var(--chip); border:1px solid var(--line); border-radius:5px;
               color:var(--muted); cursor:pointer; }
  .value-del:hover { color:var(--err); border-color:var(--err); }
  .value-add { width:100%; padding:2px 0; font-size:12px; text-align:left;
               background:none; border:0; color:var(--accent); cursor:pointer; }
  .value-add:hover { color:#fff; text-decoration:underline; }
  .port { position:absolute; cursor:crosshair; display:flex; align-items:center;
          justify-content:center; font-size:11px; line-height:1; color:#0e111c;
          font-weight:700; border:2px solid rgba(0,0,0,.35); }
  .port:hover { filter:brightness(1.25); }
  .port.in { left:50%; top:-11px; margin-left:-11px; width:22px; height:22px;
             border-radius:50%; background:#7ee0a8; }
  .port.in.cond { background:#8d93b4; }
  .port.inside { right:-9px; top:8px; bottom:8px; width:18px; border-radius:9px;
                 background:#5b8cff; }
  .port.cond { left:50%; bottom:-11px; margin-left:-11px; width:22px; height:22px;
               border-radius:50%; background:#8d93b4; }
  .port.elseout { left:50%; bottom:-11px; margin-left:-11px; width:22px; height:22px;
                  border-radius:50%; background:#f0a35e; }
  .port.in.else { background:#f0a35e; }
  .port:hover, .port.hot { background:var(--accent); border-color:#fff; }
  #palette { flex:0 0 208px; background:var(--panel); border-right:1px solid var(--line);
             padding:10px 8px 12px 10px; overflow-y:auto; overflow-x:hidden;
             display:flex; flex-direction:column; gap:12px;
             scrollbar-width:thin; scrollbar-color:var(--scroll) transparent;
             scrollbar-gutter:stable; }
  .pal-title { color:var(--muted); font-size:10.5px; text-transform:uppercase;
               letter-spacing:.7px; margin-bottom:6px; }
  .pal-item { display:flex; flex-direction:column; align-items:flex-start; gap:1px;
              width:100%; min-width:0; text-align:left; background:var(--chip);
              border:1px solid var(--line);
              border-radius:8px; padding:7px 9px; margin-bottom:6px; cursor:pointer; }
  .pal-item:hover { border-color:var(--accent); background:var(--chip-hover); }
  .pal-item b { font-size:12.5px; font-weight:600; }
  /* long hints wrap instead of widening the palette */
  .pal-item span { color:var(--muted); font-size:10.5px; line-height:1.25;
                   white-space:normal; overflow-wrap:anywhere; }
  .pal-hint { margin-top:auto; color:var(--muted); font-size:10.5px; line-height:1.4; }
  #splitter { flex:0 0 7px; cursor:col-resize; background:var(--line); position:relative; }
  #splitter:hover, #splitter.active { background:var(--accent); }
  aside { flex:0 0 440px; min-width:240px; display:flex; flex-direction:column; min-height:0; }
  .tabs { display:flex; gap:6px; padding:7px 10px; background:var(--panel);
          border-bottom:1px solid var(--line); }
  .tab { padding:4px 10px; border-radius:6px; color:var(--muted); cursor:pointer; }
  .tab.active { color:var(--fg); background:var(--chip-hover); }
  pre { flex:1; margin:0; padding:12px; overflow:auto; white-space:pre; tab-size:4;
        font:12px/1.5 "Cascadia Code", Consolas, "Courier New", monospace;
        scrollbar-width:thin; scrollbar-color:var(--scroll) transparent; }
  #status { min-height:34px; padding:8px 10px; border-top:1px solid var(--line);
            color:var(--muted); white-space:pre-wrap; font-size:12px; }
  #status.ok { color:var(--ok); } #status.error { color:var(--err); }
  #pane-log { color:var(--log-fg); }
  #wires path.wire { pointer-events:stroke; cursor:pointer; }
  #wires path.wire-hit { pointer-events:stroke; cursor:pointer; }
  /* hovering near the line lights up the whole grab area */
  #wires path.wire-hit:hover { stroke:rgba(255,143,143,.20); }
  #wires path.wire:hover { stroke:#ff8f8f; stroke-width:3; }
  .hidden { display:none !important; }
  /* A field must never spill out of its block: padding and border count into
     the width of the box, not on top of it. */
  .node-body input, .node-body select { box-sizing:border-box; }
  /* a caption above every field: a drop-down alone does not say what it is */
  .node-body .field { display:flex; flex-direction:column; gap:2px; }
  .node-body .field-label { color:var(--muted); font-size:10.5px; line-height:1.2; }
  /* a filter that came from the text view: readable, and removable in one click */
  .node-body .hidden-value { display:flex; align-items:center; gap:6px;
    background:var(--chip); border:1px dashed var(--line); border-radius:5px;
    padding:3px 6px; font-size:11.5px; color:var(--muted); }
  .node-body .hidden-value span { flex:1 1 auto; min-width:0; overflow:hidden;
    text-overflow:ellipsis; white-space:nowrap; }
  .node-body .hidden-clear { flex:0 0 auto; padding:0 5px; border:0; cursor:pointer;
    background:transparent; color:var(--muted); font:inherit; }
  .node-body .hidden-clear:hover { color:var(--err); }
</style>
</head>
<body>
<header>
  <h1>tgblocks <span data-i18n="page_nodes">узлы</span></h1>
  <button id="btn-open" data-i18n="open" title="открыть файл бота">Открыть файл…</button>
  <span id="file-name" class="file-name">bot1</span>
  <button id="btn-clear" data-i18n="clear" title="удалить все блоки">Очистить</button>
  <button id="btn-run" data-i18n="run" title="запустить бота">▶ Запустить</button>
  <button id="btn-stop" data-i18n="stop" title="остановить бота">■ Стоп</button>
  <span class="spacer"></span>
  <button id="btn-py" data-i18n="download">Скачать .py</button>
  <button id="btn-copy" data-i18n="copy">Копировать</button>
  <a href="/text" style="color:var(--muted);text-decoration:none;padding:5px 8px;
     border:1px solid var(--line);border-radius:6px;" data-i18n="view_text">Вид: текст</a>
  <a href="/blocks" style="color:var(--muted);text-decoration:none;padding:5px 8px;
     border:1px solid var(--line);border-radius:6px;" data-i18n="view_blocks">Вид: блоки</a>
</header>
<main>
  <nav id="palette"></nav>
  <input id="import" type="file" accept=".json" class="hidden" />
  <div id="canvas">
    <div id="viewport">
      <svg id="wires" width="2000" height="1600"></svg>
      <div id="handles"></div>
      <div id="nodes"></div>
    </div>
  </div>
  <div id="splitter" title="resize the panel"></div>
  <aside id="aside">
    <div class="tabs">
      <div class="tab active" data-pane="text" data-i18n="tab_text">Текст</div>
      <div class="tab" data-pane="code" data-i18n="tab_python">Python</div>
      <div class="tab" data-pane="logs" data-i18n="tab_logs">Логи</div>
    </div>
    <pre id="pane-text"></pre>
    <pre id="pane-code" class="hidden"></pre>
    <pre id="pane-log" class="hidden"></pre>
    <div id="status">Добавь «Бот» в меню слева. Колесо - масштаб, тяни фон - панорама,
тяни узел - двигать, тяни точку - связать, Delete - удалить.</div>
  </aside>
</main>
<input id="file" type="file" accept=".json" class="hidden" />
<script src="/tgblocks-project.js"></script>
<script src="/tgblocks-ui.js"></script>
<script>
(function () {
  "use strict";

  var LABEL = {
    bot: "Бот", event: "Событие", buttons: "Клавиатура", button: "Кнопка",
    when: "Условие", otherwise: "Иначе"
  };
  var LABEL_EN = {
    bot: "Bot", event: "Event", buttons: "Keyboard", button: "Button",
    when: "Condition", otherwise: "Else"
  };

  function labelOf(type) {
    if (window.TgUi && TgUi.lang() === "en" && LABEL_EN[type]) {
      return LABEL_EN[type];
    }
    return LABEL[type] || type;
  }
  // The palette, the property fields and the legal connections all come from
  // the server-side catalogue (/api/schema): a new aiogram feature shows up here
  // without touching this page.
  var SCHEMA = { actions: [], events: [], groups: [], filters: [], keyboards: [],
                 buttons: [], condition_ops: [] };
  var ACTION = {};   // action kind -> spec
  var EVENT = {};    // event kind -> spec

  function nodeTypeOf(kind) { return kind === "send_photo" ? "photo" : kind; }

  function actionKindOf(type) { return type === "photo" ? "send_photo" : type; }

  function eventKindOf(kind) { return kind === "message" ? "text" : kind; }
  var state = { nodes: {}, counter: 0, rootId: null, selected: null, drag: null,
                manual: false, view: { scale: 1, tx: 24, ty: 16 } };
  var history = [], future = [];

  var nodesEl = document.getElementById("nodes");
  var handlesEl = document.getElementById("handles");
  var wiresEl = document.getElementById("wires");
  var viewportEl = document.getElementById("viewport");
  var canvasEl = document.getElementById("canvas");
  var asideEl = document.getElementById("aside");
  var splitterEl = document.getElementById("splitter");
  var dslPane = document.getElementById("pane-text");
  var codePane = document.getElementById("pane-code");
  var statusEl = document.getElementById("status");
  var lastDsl = "", lastCode = "", lastHasToken = false;
  var restoring = false;   // true while the canvas is being rebuilt from text

  async function loadSchema() {
    try {
      var response = await fetch("/api/schema?lang=" +
                                 (window.TgUi ? TgUi.lang() : "ru"));
      var data = await response.json();
      if (!data || !data.actions) { return; }
      SCHEMA = data;
      SCHEMA.actions.forEach(function (item) {
        ACTION[item.kind] = item;
        LABEL[nodeTypeOf(item.kind)] = TgUi.tr(item);
      });
      SCHEMA.events.forEach(function (item) { EVENT[item.kind] = item; });
      buildPalette();
    } catch (error) {
      log("не удалось получить схему блоков: " + error);
    }
  }

  function buildPalette() {
    var palette = document.getElementById("palette");
    palette.innerHTML = "";

    function section(title) {
      var box = document.createElement("div");
      var head = document.createElement("div");
      head.className = "pal-title";
      head.textContent = title;
      box.appendChild(head);
      palette.appendChild(box);
      return box;
    }

    function entry(box, add, title, hint) {
      var button = document.createElement("button");
      button.className = "pal-item";
      button.dataset.add = add;
      var name = document.createElement("b");
      name.textContent = title;
      button.appendChild(name);
      if (hint) {
        var note = document.createElement("span");
        note.textContent = hint;
        button.appendChild(note);
      }
      box.appendChild(button);
    }

    var base = section(L("Основа", "Basics"));
    entry(base, "bot", L("Бот", "Bot"), L("токен и прокси", "token and proxy"));
    entry(base, "event", L("Событие", "Event"),
          L("команда, сообщение, кнопка", "command, message, button"));

    var groups = SCHEMA.groups.map(function (group) {
      return [group.kind, TgUi.tr(group)];
    });
    groups.forEach(function (pair) {
      var items = SCHEMA.actions.filter(function (item) {
        return item.group === pair[0];
      });
      if (!items.length && pair[0] !== "keyboard") { return; }
      var box = section(pair[1]);
      if (pair[0] === "keyboard") {
        entry(box, "buttons", L("Клавиатура", "Keyboard"),
              L("набор кнопок под сообщением", "a set of buttons under the message"));
        entry(box, "button", L("Кнопка", "Button"), L("внутри клавиатуры", "inside a keyboard"));
      }
      items.forEach(function (item) {
        entry(box, nodeTypeOf(item.kind), TgUi.tr(item), TgUi.hint(item));
      });
    });
  }

  // One-line translator for the few words that live in this page, not in the
  // catalogue: `L("по-русски", "in english")`.
  function L(ru, en) { return TgUi.lang() === "en" ? en : ru; }

  function clamp(value, low, high) { return Math.min(high, Math.max(low, value)); }

  function log(message) {
    // Everything about linking also goes to the browser console (F12).
    if (window.console && console.log) { console.log("[tgblocks] " + message); }
  }

  function setStatus(text, kind) {
    statusEl.textContent = text;
    statusEl.className = kind || "";
  }

  function literal(value) {
    return JSON.stringify(String(value == null ? "" : value));
  }

  function uid(prefix) {
    state.counter += 1;
    return prefix + state.counter;
  }

  function createNode(type, props, parent) {
    var node = { id: uid(type.charAt(0)), type: type, props: props || {},
                 parent: parent || null, children: [] };
    state.nodes[node.id] = node;
    return node;
  }

  function isContainer(type) {
    return type === "bot" || type === "event" || type === "when" ||
           type === "otherwise" || type === "send" || type === "buttons";
  }

  function childAllowed(parentType, childType) {
    if (parentType === "bot") { return childType === "event"; }
    if (parentType === "buttons") { return childType === "button"; }
    if (parentType === "send") { return childType === "buttons"; }
    if (childType === "bot" || childType === "event") { return false; }
    if (childType === "button") { return false; }
    if (parentType === "when" || parentType === "event" || parentType === "otherwise") {
      return true;
    }
    return false;
  }

  function ancestors(node) {
    // parent is a node id, not an object: walk through state.nodes.
    var out = [];
    var current = node && node.parent ? state.nodes[node.parent] : null;
    while (current) {
      out.push(current.id);
      current = current.parent ? state.nodes[current.parent] : null;
    }
    return out;
  }

  function subtreeIds(node) {
    var out = [node.id];
    node.children.forEach(function (id) { out = out.concat(subtreeIds(state.nodes[id])); });
    return out;
  }

  function parentsOf(nodeId) {
    return Object.keys(state.nodes).filter(function (id) {
      return (state.nodes[id].children || []).indexOf(nodeId) >= 0;
    });
  }

  function reaches(startId, targetId) {
    var stack = [startId], seen = {};
    while (stack.length) {
      var id = stack.pop();
      if (seen[id]) { continue; }
      seen[id] = true;
      if (id === targetId) { return true; }
      var node = state.nodes[id];
      if (node) { (node.children || []).forEach(function (child) { stack.push(child); }); }
    }
    return false;
  }

  function detach(node) {
    // A block may have several parents: cut every incoming link.
    Object.keys(state.nodes).forEach(function (id) {
      var parent = state.nodes[id];
      parent.children = (parent.children || []).filter(function (child) {
        return child !== node.id;
      });
    });
    node.parent = null;
  }

  // ------------------------------------------------------------- view (zoom)
  function applyView() {
    var view = state.view;
    viewportEl.style.transform = "translate(" + view.tx + "px," + view.ty + "px) scale(" +
                                 view.scale + ")";
  }

  function toModel(clientX, clientY) {
    var rect = canvasEl.getBoundingClientRect();
    return {
      x: (clientX - rect.left - state.view.tx) / state.view.scale,
      y: (clientY - rect.top - state.view.ty) / state.view.scale
    };
  }

  function zoomAt(clientX, clientY, factor) {
    var rect = canvasEl.getBoundingClientRect();
    var next = clamp(state.view.scale * factor, 0.25, 2.5);
    var px = clientX - rect.left;
    var py = clientY - rect.top;
    state.view.tx = px - (px - state.view.tx) * (next / state.view.scale);
    state.view.ty = py - (py - state.view.ty) * (next / state.view.scale);
    state.view.scale = next;
    applyView();
  }

  function zoomCenter(factor) {
    var rect = canvasEl.getBoundingClientRect();
    zoomAt(rect.left + rect.width / 2, rect.top + rect.height / 2, factor);
  }

  function fitView() {
    var elements = Array.from(nodesEl.children);
    if (!elements.length) {
      state.view = { scale: 1, tx: 24, ty: 16 };
      applyView();
      return;
    }
    var minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    elements.forEach(function (el) {
      var x = parseFloat(el.style.left) || 0;
      var y = parseFloat(el.style.top) || 0;
      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      maxX = Math.max(maxX, x + el.offsetWidth);
      maxY = Math.max(maxY, y + el.offsetHeight);
    });
    var rect = canvasEl.getBoundingClientRect();
    var width = Math.max(1, maxX - minX);
    var height = Math.max(1, maxY - minY);
    var scale = clamp(Math.min((rect.width - 80) / width, (rect.height - 80) / height), 0.25, 1.4);
    state.view.scale = scale;
    state.view.tx = (rect.width - width * scale) / 2 - minX * scale;
    state.view.ty = (rect.height - height * scale) / 2 - minY * scale;
    applyView();
  }

  // --------------------------------------------------------------- history
  function snapshot() {
    history.push(JSON.stringify({ nodes: state.nodes, counter: state.counter,
                                  rootId: state.rootId, manual: state.manual }));
    if (history.length > 60) { history.shift(); }
    future.length = 0;
  }

  function restore(raw) {
    var data = JSON.parse(raw);
    state.nodes = data.nodes;
    state.counter = data.counter;
    state.rootId = data.rootId;
    state.manual = data.manual;
    state.selected = null;
    render();
  }

  function undo() {
    if (!history.length) { setStatus(L("Отменять нечего.", "Nothing to undo.")); return; }
    future.push(JSON.stringify({ nodes: state.nodes, counter: state.counter,
                                 rootId: state.rootId, manual: state.manual }));
    restore(history.pop());
    setStatus(L("Отменено.", "Undone."), "ok");
  }

  function redo() {
    if (!future.length) { setStatus(L("Повторять нечего.", "Nothing to redo.")); return; }
    history.push(JSON.stringify({ nodes: state.nodes, counter: state.counter,
                                  rootId: state.rootId, manual: state.manual }));
    restore(future.pop());
    setStatus(L("Повторено.", "Redone."), "ok");
  }

  // ------------------------------------------------------------------ edit
  function removeNode(node) {
    if (!node) { return; }
    snapshot();
    var doomed = subtreeIds(node);
    doomed.forEach(function (id) { delete state.nodes[id]; });
    detach(node);
    if (doomed.indexOf(state.rootId) >= 0) { state.rootId = null; }
    state.selected = null;
    render();
    scheduleCompile();
    var box = Array.from(nodesEl.children).map(function (el) {
      return { x: parseFloat(el.style.left) || 0, y: parseFloat(el.style.top) || 0 };
    });
    if (box.length) {
      var rect = canvasEl.getBoundingClientRect();
      var visible = box.some(function (point) {
        return point.x * state.view.scale + state.view.tx < rect.width &&
               point.y * state.view.scale + state.view.ty < rect.height &&
               point.x * state.view.scale + state.view.tx > -200 &&
               point.y * state.view.scale + state.view.ty > -200;
      });
      if (!visible) { fitView(); }
    }
  }

  function clearOutput(message) {
    lastDsl = "";
    lastCode = "";
    dslPane.textContent = "";
    codePane.textContent = "";
    if (message) { setStatus(message); }
  }

  function duplicate(node) {
    if (!node || !node.parent) { setStatus(L("Выбери узел внутри бота.", "Pick a block inside the bot."), "error"); return; }
    snapshot();
    function clone(source) {
      var copy = { id: uid(source.type.charAt(0)), type: source.type,
                   props: JSON.parse(JSON.stringify(source.props)), parent: null, children: [] };
      state.nodes[copy.id] = copy;
      source.children.forEach(function (id) {
        var child = clone(state.nodes[id]);
        child.parent = copy.id;
        copy.children.push(child.id);
      });
      return copy;
    }
    var parent = state.nodes[node.parent];
    var index = parent.children.indexOf(node.id);
    var copy = clone(node);
    copy.parent = parent.id;
    parent.children.splice(index + 1, 0, copy.id);
    state.selected = copy.id;
    render();
  }

  function defaultProps(type) {
    // Defaults come from the catalogue, so a new block starts with sensible
    // values without a second table in this file.
    if (type === "bot") { return { token: "PASTE_YOUR_TOKEN", proxy: "" }; }
    if (type === "event") { return { kind: "command", command: "/start" }; }
    if (type === "buttons") { return { style: "inline" }; }
    if (type === "button") { return { label: "Кнопка", target: "", kind: "command" }; }
    if (type === "when") { return { op: "contains", value: "привет" }; }
    if (type === "otherwise") { return {}; }
    var spec = ACTION[actionKindOf(type)];
    var props = {};
    if (!spec) { return props; }
    (spec.params || []).forEach(function (param) {
      if (param.kind === "values") { props[param.name] = []; }
      else if (param.kind === "bool") { props[param.name] = "false"; }
      else { props[param.name] = param.default != null ? param.default : ""; }
    });
    if (type === "send" && !props.text) { props.text = "Привет!"; }
    return props;
  }

  function addNode(type) {
    if (type === "bot" && state.rootId) {
      setStatus(L("Бот уже есть - он один.", "There is only one bot block."), "error");
      return;
    }
    snapshot();
    var node = createNode(type, defaultProps(type), null);
    var rect = canvasEl.getBoundingClientRect();
    var center = toModel(rect.left + rect.width / 2, rect.top + rect.height / 2);
    node.x = Math.round(center.x - 125);
    node.y = Math.round(center.y - 40);
    // find a free spot: do not drop a new block on top of an existing one
    var occupied = Object.keys(state.nodes)
      .map(function (id) { return state.nodes[id]; })
      .filter(function (other) { return other.id !== node.id && other.x != null; });
    var guard = 0;
    while (guard < 80 && occupied.some(function (other) {
      return Math.abs(other.x - node.x) < 270 && Math.abs(other.y - node.y) < 150;
    })) {
      node.y += 160;
      if (guard % 3 === 2) { node.x += 290; node.y -= 320; }
      guard += 1;
    }
    if (type === "bot") { state.rootId = node.id; }
    state.selected = node.id;
    render();
    scheduleCompile();
    if (type !== "bot") {
      setStatus(L("Блок добавлен свободно. Соедини его с «Бот» и другими блоками точками.", "Block added on its own. Connect it to the bot and the others by the dots."));
    }
  }

  // ----------------------------------------------------------------- render
  function buildBody(node) {
    var body = document.createElement("div");
    body.className = "node-body";

    function input(key, placeholder) {
      var el = document.createElement("input");
      el.value = node.props[key] || "";
      el.placeholder = placeholder;
      el.addEventListener("input", function () {
        node.props[key] = el.value;
        drawWires();
        scheduleCompile();
      });
      return el;
    }

    function select(pairs, key, fallback, onChange) {
      var el = document.createElement("select");
      pairs.forEach(function (pair) {
        var option = document.createElement("option");
        option.value = pair[0];
        option.textContent = pair[1];
        if ((node.props[key] || fallback) === pair[0]) { option.selected = true; }
        el.appendChild(option);
      });
      el.addEventListener("change", function () {
        node.props[key] = el.value;
        if (onChange) { onChange(); }
        scheduleCompile();
      });
      return el;
    }

    function listInput(key, placeholder) {
      // A list field (message patterns): shown as "a, b", stored as an array so
      // the text view keeps them and the bot keeps reacting to those texts.
      var el = document.createElement("input");
      var current = node.props[key];
      el.value = Array.isArray(current) ? current.join(", ") : (current || "");
      el.placeholder = placeholder;
      el.addEventListener("input", function () {
        node.props[key] = el.value.split(",")
          .map(function (item) { return item.trim(); })
          .filter(function (item) { return item.length > 0; });
        drawWires();
        scheduleCompile();
      });
      return el;
    }

    function valueRow(list, index) {
      // One extra comparison value of a condition.
      var row = document.createElement("div");
      row.className = "value-row";

      var el = document.createElement("input");
      el.value = list[index] || "";
      el.placeholder = L("ещё значение", "one more value");
      el.addEventListener("input", function () {
        list[index] = el.value;
        drawWires();
        scheduleCompile();
      });

      var remove = document.createElement("button");
      remove.type = "button";
      remove.className = "value-del";
      remove.title = "убрать это значение";
      remove.textContent = "×";
      remove.addEventListener("click", function (event) {
        event.stopPropagation();
        list.splice(index, 1);
        render();
        scheduleCompile();
      });

      row.appendChild(el);
      row.appendChild(remove);
      return row;
    }

    function addValueButton(list, nodeId) {
      var add = document.createElement("button");
      add.type = "button";
      add.className = "value-add";
      add.textContent = L("+ ещё значение", "+ one more value");
      add.title = "добавить ещё одно значение: подойдёт любое из них";
      add.addEventListener("click", function (event) {
        event.stopPropagation();
        list.push("");
        render();
        // put the cursor straight into the fresh row
        var node = nodesEl.querySelector('.node[data-id="' + nodeId + '"]');
        var inputs = node ? node.querySelectorAll(".value-row input") : [];
        if (inputs.length) { inputs[inputs.length - 1].focus(); }
        scheduleCompile();
      });
      return add;
    }

    function note(text) {
      var el = document.createElement("span");
      el.className = "node-note";
      el.textContent = text;
      return el;
    }

    function paramField(param) {
      // A caption plus one widget: without the caption a drop-down says
      // "в любом чате" and nobody knows what it is about.
      var wrap = document.createElement("div");
      wrap.className = "field";
      var caption = document.createElement("span");
      caption.className = "field-label";
      caption.textContent = TgUi.tr(param) + (param.required ? " *" : "");
      wrap.appendChild(caption);
      wrap.appendChild(widgetFor(param));
      return wrap;
    }

    function widgetFor(param) {
      // One widget per catalogue param kind: the schema decides what a block
      // can hold, so a new aiogram feature gets its fields for free.
      var key = param.name;
      if (param.kind === "values") {
        return listInput(key, TgUi.tr(param));
      }
      if (param.kind === "bool") {
        return select([["false", L("нет", "no")], ["true", L("да", "yes")]],
                      key, "false");
      }
      if (param.kind === "choice") {
        return select((param.choices || []).map(function (item) {
          return [String(item.value), TgUi.choiceLabel(item)];
        }), key, param.default);
      }
      // Every text field is one line, like the rest of the block: a taller box
      // made the canvas uneven. Line breaks are written as \n inside the text.
      return input(key, TgUi.tr(param));
    }

    if (node.type === "bot") {
      body.appendChild(input("token", L("токен от @BotFather", "token from @BotFather")));
      body.appendChild(input("proxy", L("прокси (пусто - без прокси)",
                                       "proxy (empty - no proxy)")));
      body.appendChild(input("name", L("название бота (необязательно)",
                                      "bot name (optional)")));
      body.appendChild(input("webhook", L("webhook https://… (необязательно)",
                                         "webhook https://… (optional)")));
      return body;
    }

    if (node.type === "event") {
      var choices = SCHEMA.events.map(function (item) {
        return [item.kind === "text" ? "message" : item.kind, TgUi.tr(item)];
      });
      if (!choices.length) { choices = [["command", L("команда", "command")]]; }
      body.appendChild(select(choices, "kind", "command", render));
      var eventSpec = EVENT[eventKindOf(node.props.kind || "command")];
      if (eventSpec) {
        (eventSpec.params || []).forEach(function (param) {
          // "Only these texts" and "matches a pattern" are hidden: a `when`
          // condition shows the same filter on the canvas, and one place to edit
          // it is better than two.
          if (param.hidden) { return; }
          body.appendChild(paramField(param));
        });
        (eventSpec.params || []).forEach(function (param) {
          if (!param.hidden) { return; }
          if (!hasValue(node.props[param.name])) { return; }
          body.appendChild(hiddenFilter(param, node));
        });
      }
      return body;
    }

    function hasValue(value) {
      if (Array.isArray(value)) {
        return value.some(function (item) { return String(item).trim() !== ""; });
      }
      return value != null && String(value).trim() !== "";
    }

    // A filter that came from the text view (regex, a list of exact texts) keeps
    // working, but the canvas shows it as a read-only chip with a way to drop it:
    // dropping the field silently would change the bot on the next compile.
    function hiddenFilter(param, node) {
      var wrap = document.createElement("div");
      wrap.className = "field hidden-filter";
      var caption = document.createElement("span");
      caption.className = "field-label";
      caption.textContent = TgUi.tr(param);
      wrap.appendChild(caption);

      var row = document.createElement("div");
      row.className = "hidden-value";
      var text = document.createElement("span");
      var value = node.props[param.name];
      text.textContent = Array.isArray(value) ? value.join(", ") : String(value);
      text.title = TgUi.hint(param);
      row.appendChild(text);

      var clear = document.createElement("button");
      clear.type = "button";
      clear.className = "hidden-clear";
      clear.textContent = "✕";
      clear.title = L("убрать фильтр", "remove the filter");
      clear.addEventListener("click", function (event) {
        event.stopPropagation();
        snapshot();
        delete node.props[param.name];
        render();
        scheduleCompile();
      });
      row.appendChild(clear);
      wrap.appendChild(row);
      return wrap;
    }

    if (node.type === "buttons") {
      body.appendChild(select(SCHEMA.keyboards.map(function (item) {
        return [item.value, TgUi.choiceLabel(item)];
      }), "style", "inline"));
      return body;
    }

    if (node.type === "button") {
      body.appendChild(input("label", L("текст на кнопке", "button label")));
      body.appendChild(select(SCHEMA.buttons.map(function (item) {
        return [item.value, TgUi.choiceLabel(item)];
      }), "kind", "command", render));
      var buttonKind = node.props.kind || "command";
      if (buttonKind !== "contact" && buttonKind !== "location") {
        body.appendChild(input("target",
          buttonKind === "command" ? L("/команда", "/command") : "https://…"));
      }
      return body;
    }

    if (node.type === "when") {
      body.appendChild(select(
        [["text", L("текст сообщения", "message text")],
         ["dice", L("интерактивное эмодзи", "interactive emoji")]],
        "source", "text", render));
      var dice = (node.props.source || "text") === "dice";
      body.appendChild(select(
        dice ? [["==", L("равно", "equals")], ["!=", L("не равно", "not equal")]]
             : (SCHEMA.condition_ops || []),
        "op", dice ? "==" : "contains", render));
      body.appendChild(input("value", dice
        ? L("число, которое выпало", "the number rolled")
        : L("текст", "text")));
      if (!dice) {
        var extras = node.props.values || (node.props.values = []);
        extras.forEach(function (item, index) {
          body.appendChild(valueRow(extras, index));
        });
        body.appendChild(addValueButton(extras, node.id));
      }
      return body;
    }

    if (node.type === "otherwise") {
      body.appendChild(note(L("ветка «иначе»: сюда попадут блоки, если условие не сработало",
                              "the else branch: runs when the condition fails")));
      return body;
    }

    var actionSpec = ACTION[actionKindOf(node.type)];
    if (!actionSpec) {
      body.appendChild(note(L("неизвестный блок: ", "unknown block: ") + node.type));
      return body;
    }
    (actionSpec.params || []).forEach(function (param) {
      body.appendChild(paramField(param));
    });
    return body;
  }

  function render() {
    Object.keys(state.nodes).forEach(function (id) {
      var node = state.nodes[id];
      if (!node || typeof node !== "object" || typeof node.type !== "string") {
        delete state.nodes[id];
        return;
      }
      node.children = (node.children || []).filter(function (childId) {
        var child = state.nodes[childId];
        return !!child && typeof child === "object" && typeof child.type === "string";
      });
    });
    var ghost = document.getElementById("ghost");
    if (ghost) { ghost.remove(); }
    nodesEl.innerHTML = "";
    handlesEl.innerHTML = "";
    applyView();

    var ids = Object.keys(state.nodes);
    if (!ids.length) {
      wiresEl.innerHTML = "";
      clearOutput("Пусто. Добавь блоки из меню слева и соедини их точками.");
      return;
    }

    ids.forEach(function (id) {
      var node = state.nodes[id];
      var el = document.createElement("div");
      el.className = "node" + (state.selected === node.id ? " selected" : "");
      el.dataset.id = node.id;

      var head = document.createElement("div");
      head.className = "node-head";
      var kind = document.createElement("span");
      kind.className = "kind";
      kind.textContent = labelOf(node.type);
      head.appendChild(kind);
      var badge = document.createElement("span");
      badge.className = "badge";
      badge.textContent = node.type === "event"
        ? ((node.props.kind || "command") === "command"
            ? (node.props.command || "") : (node.props.kind || ""))
        : "";
      head.appendChild(badge);
      var del = document.createElement("button");
      del.className = "del";
      del.textContent = "✕";
      del.addEventListener("click", function (event) {
        event.stopPropagation();
        removeNode(node);
      });
      head.appendChild(del);
      el.appendChild(head);
      el.appendChild(buildBody(node));

      // Бот - корень, входа у него нет. Остальные принимают связь зелёной точкой.
      if (node.type !== "bot") {
        var entry = document.createElement("div");
        var inputClass = node.type === "when" ? " cond" : (node.type === "otherwise" ? " else" : "");
        entry.className = "port in" + inputClass;
        entry.dataset.port = "in";
        entry.dataset.node = node.id;
        entry.textContent = "\u25BC";
        el.appendChild(entry);
      }

      // Синий выход - полоса справа, есть у каждого блока.
      var nextPort = document.createElement("div");
      nextPort.className = "port inside";
      nextPort.dataset.port = "inside";
      nextPort.dataset.node = node.id;
      nextPort.textContent = "\u25B6";
      el.appendChild(nextPort);

      if (node.type === "when") {
        var elsePort = document.createElement("div");
        elsePort.className = "port elseout";
        elsePort.dataset.port = "elseout";
        elsePort.dataset.node = node.id;
        elsePort.textContent = "\u25BC";
        el.appendChild(elsePort);
      }

      if (node.type === "event") {
        var condPort = document.createElement("div");
        condPort.className = "port cond";
        condPort.dataset.port = "cond";
        condPort.dataset.node = node.id;
        condPort.textContent = "\u25BC";
        el.appendChild(condPort);
      }
      el.addEventListener("mousedown", function (event) {
        state.selected = node.id;
        Array.from(nodesEl.children).forEach(function (other) {
          other.classList.toggle("selected", other.dataset.id === node.id);
        });
        if (isInteractive(event.target)) { return; }
        startDragNode(event, node, el);
      });
      nodesEl.appendChild(el);
    });

    layout();
    drawWires();
    scheduleCompile();
  }

  function isInteractive(target) {
    return !!(target.closest && (target.closest("input") || target.closest("select") ||
                                 target.closest("button") || target.closest(".port")));
  }

  function layout() {
    // Nothing is auto-arranged: every node stays where you dropped it.
    Array.from(nodesEl.children).forEach(function (el, index) {
      var node = state.nodes[el.dataset.id];
      if (!node) { return; }
      if (node.x == null || node.y == null) {
        node.x = 40 + (index % 4) * 300;
        node.y = 40 + Math.floor(index / 4) * 200;
      }
      el.style.left = node.x + "px";
      el.style.top = node.y + "px";
    });
    var width = 800, height = 600;
    Array.from(nodesEl.children).forEach(function (el) {
      var right = (parseFloat(el.style.left) || 0) + el.offsetWidth + 120;
      var bottom = (parseFloat(el.style.top) || 0) + el.offsetHeight + 120;
      if (right > width) { width = right; }
      if (bottom > height) { height = bottom; }
    });
    wiresEl.setAttribute("width", width);
    wiresEl.setAttribute("height", height);
    wiresEl.setAttribute("viewBox", "0 0 " + width + " " + height);
  }

  function portCenter(nodeId, portName) {
    var el = nodesEl.querySelector('.node[data-id="' + nodeId + '"]');
    if (!el) { return null; }
    var left = parseFloat(el.style.left) || 0;
    var top = parseFloat(el.style.top) || 0;
    var width = el.offsetWidth;
    var height = el.offsetHeight;
    if (portName === "in") { return { x: left + width / 2, y: top }; }
    if (portName === "out") { return { x: left + width / 2, y: top + height }; }
    return { x: left + width, y: top + height / 2 };
  }

  function curve(a, b) {
    var mid = (a.y + b.y) / 2;
    return "M " + a.x + " " + a.y + " C " + a.x + " " + mid + ", " + b.x + " " + mid +
           ", " + b.x + " " + b.y;
  }

  function curveDown(a, b) {
    // Condition lines leave straight down and only then turn to the block.
    var drop = Math.max(24, Math.min(120, Math.abs(b.y - a.y) / 2));
    return "M " + a.x + " " + a.y + " C " + a.x + " " + (a.y + drop) + ", " +
           b.x + " " + (b.y - drop) + ", " + b.x + " " + b.y;
  }

  function growWireCanvas() {
    // The wire sheet must cover every block, otherwise lines get cut off.
    var width = 800, height = 600;
    Array.from(nodesEl.children).forEach(function (el) {
      var right = (parseFloat(el.style.left) || 0) + el.offsetWidth + 240;
      var bottom = (parseFloat(el.style.top) || 0) + el.offsetHeight + 240;
      if (right > width) { width = Math.round(right); }
      if (bottom > height) { height = Math.round(bottom); }
    });
    wiresEl.setAttribute("width", width);
    wiresEl.setAttribute("height", height);
    wiresEl.setAttribute("viewBox", "0 0 " + width + " " + height);
  }

  function wireList() {
    // Blue output = next block: events come from Бот, actions chain from the
    // previous action. Grey output = condition, and it only feeds "Условие".
    var out = [];
    Object.keys(state.nodes).forEach(function (id) {
      var node = state.nodes[id];
      var children = (node.children || []).filter(function (childId) {
        return !!state.nodes[childId];
      });
      var lastAction = node.id;
      children.forEach(function (childId) {
        var child = state.nodes[childId];
        if (child.type === "when") {
          // conditions branch from the parent with the grey output
          out.push({ parent: node.id, child: childId, source: node.id, port: "cond" });
          return;
        }
        if (child.type === "otherwise") {
          // "иначе" hangs off the orange output of the condition
          out.push({ parent: node.id, child: childId, source: node.id, port: "elseout" });
          return;
        }
        // events hang off Бот, actions chain through the blue strip
        var source = node.type === "bot" ? node.id : lastAction;
        out.push({ parent: node.id, child: childId, source: source, port: "inside" });
        if (node.type !== "bot") { lastAction = childId; }
      });
    });
    return out;
  }

  function insidePoint(nodeId, index, count) {
    // Fan the children out along the right edge instead of one shared dot.
    var el = nodesEl.querySelector('.node[data-id="' + nodeId + '"]');
    if (!el) { return null; }
    var left = parseFloat(el.style.left) || 0;
    var top = parseFloat(el.style.top) || 0;
    var usable = Math.max(24, el.offsetHeight - 28);
    var step = count > 1 ? usable / count : 0;
    var y = top + 14 + (count > 1 ? (index + 0.5) * step : usable / 2);
    return { x: left + el.offsetWidth, y: y };
  }

  function portDotPoint(nodeId, cls) {
    var nodeEl = nodesEl.querySelector('.node[data-id="' + nodeId + '"]');
    if (!nodeEl) { return null; }
    var dot = nodeEl.querySelector('.port.' + cls);
    if (!dot) { return null; }
    var left = parseFloat(nodeEl.style.left) || 0;
    var top = parseFloat(nodeEl.style.top) || 0;
    return { x: left + dot.offsetLeft + dot.offsetWidth / 2,
             y: top + dot.offsetTop + dot.offsetHeight / 2 };
  }

  function condPoint(nodeId) {
    // Real position of the grey dot: its own offset inside the block.
    return portDotPoint(nodeId, "cond");
  }

  function stripPoint(nodeId, index) {
    var el = nodesEl.querySelector('.node[data-id="' + nodeId + '"]');
    if (!el) { return null; }
    var left = parseFloat(el.style.left) || 0;
    var top = parseFloat(el.style.top) || 0;
    var height = el.offsetHeight;
    var offset = Math.max(-0.35, Math.min(0.35, index * 0.18));
    return { x: left + el.offsetWidth, y: top + height * (0.5 + offset) };
  }

  function drawWires() {
    growWireCanvas();
    var parts = [];
    var seen = {};
    wireList().forEach(function (wire) {
      var index = seen[wire.source] || 0;
      seen[wire.source] = index + 1;
      var from = null;
      if (wire.port === "cond") {
        from = condPoint(wire.source);
      } else if (wire.port === "elseout") {
        from = portDotPoint(wire.source, "elseout");
      } else {
        from = stripPoint(wire.source, index);
        if (!from) { from = portCenter(wire.source, wire.port); }
      }
      var to = portCenter(wire.child, "in");
      if (!from || !to) { return; }
      var childId = wire.child;
      var child = state.nodes[childId];
      var isCond = child && child.type === "when";
      var isElse = child && child.type === "otherwise";
      var path = (isCond || isElse) ? curveDown(from, to) : curve(from, to);
      var wireColor = isCond ? "#8d93b4" : (isElse ? "#f0a35e" : "#5b8cff");
      var markerId = isCond ? "tg-arrow-cond" : (isElse ? "tg-arrow-else" : "tg-arrow");
      parts.push('<path class="wire" data-child="' + childId +
                 '" data-else="' + (isElse ? "1" : "0") +
                 '" d="' + path + '" fill="none" stroke="' + wireColor +
                 '" stroke-width="1.8"' +
                 ' marker-end="url(#' + markerId + ')" />');
      // The line keeps its thin look; this fat transparent copy sits on top so
      // grabbing it (and deleting the link) does not need a pixel-perfect aim.
      parts.push('<path class="wire-hit" data-child="' + childId +
                 '" d="' + path + '" fill="none" stroke="transparent"' +
                 ' stroke-width="26" />');
    });
    wiresEl.innerHTML =
      '<defs>' +
      '<marker id="tg-arrow" viewBox="0 0 10 10" refX="9" refY="5"' +
      ' markerWidth="7" markerHeight="7" orient="auto-start-reverse">' +
      '<path d="M 0 0 L 10 5 L 0 10 z" fill="#5b8cff"/></marker>' +
      '<marker id="tg-arrow-cond" viewBox="0 0 10 10" refX="9" refY="5"' +
      ' markerWidth="7" markerHeight="7" orient="auto-start-reverse">' +
      '<path d="M 0 0 L 10 5 L 0 10 z" fill="#8d93b4"/></marker>' +
      '<marker id="tg-arrow-else" viewBox="0 0 10 10" refX="9" refY="5"' +
      ' markerWidth="7" markerHeight="7" orient="auto-start-reverse">' +
      '<path d="M 0 0 L 10 5 L 0 10 z" fill="#f0a35e"/></marker>' +
      '</defs>' + parts.join("");
  }

  // ------------------------------------------------------------- interactions
  var moving = null;
  var panMoved = false;
  var panning = null;
  var splitting = null;

  function startDragNode(event, node, el) {
    event.preventDefault();
    if (!state.manual) {
      snapshot();
      state.manual = true;
      Array.from(nodesEl.children).forEach(function (child) {
        var current = state.nodes[child.dataset.id];
        if (current && current.x == null) {
          current.x = parseFloat(child.style.left) || 0;
          current.y = parseFloat(child.style.top) || 0;
        }
      });
    }
    moving = { node: node, startX: event.clientX, startY: event.clientY,
               x: node.x || 0, y: node.y || 0 };
    el.style.zIndex = 5;
  }

  canvasEl.addEventListener("mousedown", function (event) {
    if (!pending) { return; }
    if (event.target.closest && (event.target.closest(".node") || event.target.closest(".port"))) {
      return;
    }
    pending = null;
    markTargets(null);
    setStatus(L("Связывание отменено.", "Linking cancelled."));
  });

  canvasEl.addEventListener("click", function (event) {
    if (panMoved) { return; }
    var path = event.target.closest ? event.target.closest("path[data-child]") : null;
    if (!path) { return; }
    event.stopPropagation();
    var child = state.nodes[path.dataset.child];
    log("удаляю связь для " + (child ? child.type + "/" + child.id : path.dataset.child));
    if (!child) { render(); return; }
    snapshot();
    detach(child);
    render();
    scheduleCompile();
    setStatus(L("Связь удалена.", "Wire removed."), "ok");
  });

  canvasEl.addEventListener("mousedown", function (event) {
    if (event.target.closest(".node")) { return; }
    panMoved = false;
    panning = { startX: event.clientX, startY: event.clientY,
                tx: state.view.tx, ty: state.view.ty };
    canvasEl.classList.add("panning");
  });

  var pending = null;
  var dragMoved = false;

  nodesEl.addEventListener("mousedown", function (event) {
    var port = event.target.closest(".port");
    var nodeEl = event.target.closest(".node");

    // Second step of the click mode: the port was already clicked.
    if (pending) {
      event.preventDefault();
      event.stopPropagation();
      var source = pending;
      pending = null;
      markTargets(null);
      if (nodeEl && nodeEl.dataset.id !== source.node) {
        link(source, nodeEl.dataset.id);
      } else {
        setStatus(L("Связывание отменено.", "Linking cancelled."));
      }
      return;
    }

    if (!port) { return; }
    event.preventDefault();
    dragMoved = false;
    state.drag = { node: port.dataset.node, port: port.dataset.port, hot: null,
                   startX: event.clientX, startY: event.clientY };
    var oldGhost = document.getElementById("ghost");
    if (oldGhost) { oldGhost.remove(); }
    var ghost = document.createElementNS("http://www.w3.org/2000/svg", "path");
    ghost.setAttribute("stroke", "#5b8cff");
    ghost.setAttribute("stroke-width", "1.8");
    ghost.setAttribute("fill", "none");
    ghost.setAttribute("stroke-dasharray", "5 4");
    ghost.id = "ghost";
    wiresEl.appendChild(ghost);
    pending = state.drag;
    markTargets(pending);
    setStatus(L("Кликни блок - или тяни линию к нему.", "Click a block - or drag the line to it."));
  });

  splitterEl.addEventListener("mousedown", function (event) {
    event.preventDefault();
    splitting = { startX: event.clientX, width: asideEl.offsetWidth };
    splitterEl.classList.add("active");
  });

  document.addEventListener("mousemove", function (event) {
    if (splitting) {
      var width = clamp(splitting.width - (event.clientX - splitting.startX), 240,
                        window.innerWidth - 320);
      asideEl.style.flex = "0 0 " + width + "px";
      return;
    }
    if (panning) {
      state.view.tx = panning.tx + (event.clientX - panning.startX);
      state.view.ty = panning.ty + (event.clientY - panning.startY);
      if (Math.abs(event.clientX - panning.startX) > 4 ||
          Math.abs(event.clientY - panning.startY) > 4) {
        panMoved = true;
      }
      applyView();
      return;
    }
    if (moving) {
      var dx = (event.clientX - moving.startX) / state.view.scale;
      var dy = (event.clientY - moving.startY) / state.view.scale;
      moving.node.x = Math.max(8, moving.x + dx);
      moving.node.y = Math.max(8, moving.y + dy);
      var el = nodesEl.querySelector('.node[data-id="' + moving.node.id + '"]');
      if (el) {
        el.style.left = moving.node.x + "px";
        el.style.top = moving.node.y + "px";
      }
      drawWires();
      return;
    }
    if (!state.drag) { return; }

    if (Math.abs(event.clientX - state.drag.startX) > 4 ||
        Math.abs(event.clientY - state.drag.startY) > 4) {
      dragMoved = true;
      pending = null;
    }

    var ghost = document.getElementById("ghost");
    var hot = nodesEl.querySelector('.port.hot');
    if (hot) { hot.classList.remove("hot"); }
    var hovered = document.elementFromPoint(event.clientX, event.clientY);
    var nodeEl = hovered && hovered.closest ? hovered.closest(".node") : null;
    if (nodeEl) {
      var entry = nodeEl.querySelector(".port.in");
      if (entry) { entry.classList.add("hot"); }
      state.drag.hot = canLink(state.drag, nodeEl.dataset.id) ? nodeEl.dataset.id : null;
    } else {
      state.drag.hot = null;
    }
    if (!ghost) { return; }
    var source = null;
    if (state.drag.port === "cond") {
      source = condPoint(state.drag.node);
    } else if (state.drag.port === "elseout") {
      source = portDotPoint(state.drag.node, "elseout");
    } else {
      source = portCenter(state.drag.node, state.drag.port);
    }
    if (!source) { return; }
    var targetPoint = toModel(event.clientX, event.clientY);
    var condDrag = state.drag.port === "cond" || state.drag.port === "elseout";
    ghost.setAttribute("d", (condDrag ? curveDown : curve)(source, targetPoint));
  });

  document.addEventListener("mouseup", function () {
    if (splitting) {
      splitting = null;
      splitterEl.classList.remove("active");
      return;
    }
    if (panning) {
      panning = null;
      canvasEl.classList.remove("panning");
      return;
    }
    if (moving) {
      moving = null;
      scheduleCompile();
      return;
    }
    if (!state.drag) { return; }
    var drag = state.drag;
    state.drag = null;
    var ghost = document.getElementById("ghost");
    if (ghost) { ghost.remove(); }
    var hot = nodesEl.querySelector(".port.hot");
    if (hot) { hot.classList.remove("hot"); }

    if (!dragMoved) {
      pending = drag;
      markTargets(pending);
      setStatus(L("Теперь кликни нужный блок.", "Now click the block you need."));
      return;
    }

    markTargets(null);
    if (drag.hot) { link(drag, drag.hot); }
  });

  function cancelPointer() {
    if (state.drag) {
      state.drag = null;
      var ghost = document.getElementById("ghost");
      if (ghost) { ghost.remove(); }
      markTargets(null);
    }
    pending = null;
    moving = null;
    panning = null;
    canvasEl.classList.remove("panning");
  }

  window.addEventListener("error", function (event) {
    setStatus(L("Ошибка в редакторе: ", "Editor error: ") + event.message + L(" - открой F12", " - open F12"), "error");
  });

  window.addEventListener("blur", cancelPointer);
  document.addEventListener("mouseleave", cancelPointer);

  canvasEl.addEventListener("contextmenu", function (event) {
    var path = event.target.closest ? event.target.closest("path[data-child]") : null;
    if (!path) { return; }
    event.preventDefault();
    var child = state.nodes[path.dataset.child];
    if (!child) { return; }
    snapshot();
    detach(child);
    render();
    scheduleCompile();
    setStatus(L("Связь удалена.", "Wire removed."), "ok");
  });

  canvasEl.addEventListener("wheel", function (event) {
    event.preventDefault();
    zoomAt(event.clientX, event.clientY, event.deltaY < 0 ? 1.12 : 1 / 1.12);
  }, { passive: false });

  canvasEl.addEventListener("dblclick", function (event) {
    if (event.target.closest && event.target.closest(".node")) { return; }
    fitView();
  });

  splitterEl.addEventListener("dblclick", function () {
    asideEl.style.flex = "0 0 440px";
  });

  function canLink(drag, targetId) {
    var source = state.nodes[drag.node];
    var target = state.nodes[targetId];
    if (!source || !target || source.id === target.id) { return false; }

    // grey feeds only conditions, orange feeds only "иначе", blue feeds neither
    if (drag.port === "cond" && target.type !== "when") { return false; }
    if (drag.port !== "cond" && target.type === "when") { return false; }
    if (drag.port === "elseout" && target.type !== "otherwise") { return false; }
    if (drag.port !== "elseout" && target.type === "otherwise") { return false; }

    if (isContainer(source.type) && childAllowed(source.type, target.type) &&
        !reaches(target.id, source.id)) {
      return true;
    }
    if (isContainer(target.type) && childAllowed(target.type, source.type) &&
        !reaches(source.id, target.id)) {
      return true;
    }
    var parent = target.parent ? state.nodes[target.parent] : null;
    if (parent && childAllowed(parent.type, source.type) &&
        subtreeIds(source).indexOf(target.id) < 0) {
      return true;
    }
    var home = source.parent ? state.nodes[source.parent] : null;
    if (!parent && home && childAllowed(home.type, target.type) &&
        subtreeIds(target).indexOf(source.id) < 0) {
      return true;
    }
    return false;
  }

  function markTargets(drag) {
    Array.from(nodesEl.children).forEach(function (el) {
      el.classList.remove("ok");
      el.classList.remove("bad");
      if (!drag) { return; }
      if (el.dataset.id === drag.node) { return; }
      el.classList.add(canLink(drag, el.dataset.id) ? "ok" : "bad");
    });
  }

  function attach(parentNode, childNode) {
    if (parentNode.id === childNode.id || reaches(childNode.id, parentNode.id)) {
      setStatus(L("Так получится петля - нельзя.", "That would make a loop."), "error");
      return;
    }
    snapshot();
    parentNode.children = parentNode.children || [];
    if (parentNode.children.indexOf(childNode.id) < 0) {
      parentNode.children.push(childNode.id);
    }
    if (!childNode.parent) { childNode.parent = parentNode.id; }
    render();
    scheduleCompile();
    var count = parentsOf(childNode.id).length;
    setStatus(L("«", "") + labelOf(childNode.type) +
              L("» теперь внутри «", "” is now inside “") + labelOf(parentNode.type) +
              L("»", "”") +
              (count > 1 ? L(" (входов: ", " (inputs: ") + count + ")" : "") + ".", "ok");
  }

  function link(drag, targetId) {
    var source = state.nodes[drag.node];
    var target = state.nodes[targetId];
    log("link: " + (source && source.type) + " " + drag.port + " -> " + (target && target.type));
    if (drag.port === "cond" && target && target.type !== "when") {
      setStatus(L("Серый выход ведёт только к «Условие».", "The grey port leads only to a condition."), "error");
      return;
    }
    if (drag.port !== "cond" && target && target.type === "when") {
      setStatus(L("К «Условию» ведёт только серый выход - тяни от серой точки.", "Only the grey port leads to a condition - drag from the grey dot."), "error");
      return;
    }
    if (drag.port === "elseout" && target && target.type !== "otherwise") {
      setStatus(L("Оранжевый выход ведёт только к «Иначе».", "The orange port leads only to an else block."), "error");
      return;
    }
    if (drag.port !== "elseout" && target && target.type === "otherwise") {
      setStatus(L("К «Иначе» ведёт только оранжевый выход условия.", "Only the orange port of a condition leads to an else block."), "error");
      return;
    }
    if (!source || !target || source.id === target.id) {
      log("link: пустой источник или цель");
      return;
    }

    // 1) container -> child: event, when, buttons or bot takes the target inside
    if (isContainer(source.type) && childAllowed(source.type, target.type) &&
        !reaches(target.id, source.id)) {
      attach(source, target);
      return;
    }

    // 2) the other direction is fine too: dropping an action onto an event nests it
    if (isContainer(target.type) && childAllowed(target.type, source.type) &&
        !reaches(source.id, target.id)) {
      attach(target, source);
      return;
    }

    // 3) same level: put the source right before the target
    var parent = target.parent ? state.nodes[target.parent] : null;
    if (parent && childAllowed(parent.type, source.type) &&
        subtreeIds(source).indexOf(target.id) < 0) {
      snapshot();
      parent.children = parent.children.filter(function (id) { return id !== source.id; });
      var position = parent.children.indexOf(target.id);
      parent.children.splice(position, 0, source.id);
      if (!source.parent) { source.parent = parent.id; }
      render();
      setStatus(L("«", "") + labelOf(source.type) +
                L("» теперь перед «", "” is now before “") + labelOf(target.type) +
                L("».", "”."), "ok");
      return;
    }

    // 4) the target is still free: join it where the source already lives,
    // right after the source, so a chain can be built before attaching it.
    var home = source.parent ? state.nodes[source.parent] : null;
    if (!parent && home && childAllowed(home.type, target.type) &&
        subtreeIds(target).indexOf(source.id) < 0) {
      snapshot();
      home.children = home.children.filter(function (id) { return id !== target.id; });
      var after = home.children.indexOf(source.id);
      home.children.splice(after + 1, 0, target.id);
      if (!target.parent) { target.parent = home.id; }
      render();
      setStatus(L("«", "") + labelOf(target.type) +
                L("» идёт после «", "” comes after “") + labelOf(source.type) +
                L("».", "”."), "ok");
      return;
    }

    log("link: запрещено " + source.type + " -> " + target.type);
    if (!parent && !home) {
      setStatus(L("Сначала прикрепи один из блоков к «Событие», потом соединяй их между собой.", "First attach one of the blocks to an event, then link them to each other."), "error");
      return;
    }
    setStatus(L("«", "") + labelOf(target.type) +
              L("» нельзя вложить в «", "” cannot be nested in “") + labelOf(source.type) +
              L("».", "”."), "error");
  }

  document.addEventListener("keydown", function (event) {
    var typing = /^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement.tagName);
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "z" && !typing) {
      event.preventDefault(); undo(); return;
    }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "y" && !typing) {
      event.preventDefault(); redo(); return;
    }
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "d" && !typing) {
      event.preventDefault(); duplicate(state.nodes[state.selected]); return;
    }
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") { compile(); return; }
    if (event.key === "f" && !typing) { fitView(); return; }
    if (event.key === "Escape" && pending) {
      pending = null;
      markTargets(null);
      setStatus(L("Связывание отменено.", "Linking cancelled."));
      return;
    }
    if ((event.key === "Delete" || event.key === "Backspace") && !typing && state.selected) {
      removeNode(state.nodes[state.selected]);
    }
  });

  async function compile() {
    if (!state.rootId || !state.nodes[state.rootId]) {
      var foundBot = Object.keys(state.nodes).filter(function (id) {
        return state.nodes[id] && state.nodes[id].type === "bot";
      })[0];
      if (foundBot) {
        state.rootId = foundBot;
      } else {
        clearOutput("Пусто. Добавь блок «Бот» в меню слева.");
        return;
      }
    }
    // The board goes to the server as it is: one converter in Python instead of
    // a second DSL writer here that can drift away from it.
    try {
      var response = await fetch("/api/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nodes: currentBoard() })
      });
      var data = await response.json();
      if (!data.ok) {
        lastDsl = "";
        lastCode = "";
        dslPane.textContent = "";
        codePane.textContent = "";
        setStatus(data.detail || data.error || L("Не собралось.", "Compilation failed."), "error");
        return;
      }
      lastDsl = data.text || "";
      lastCode = data.code || "";
      lastHasToken = !!data.has_token;
      dslPane.textContent = lastDsl;
      codePane.textContent = lastCode;
      var unlinked = Object.keys(state.nodes).filter(function (id) {
        return id !== state.rootId && !state.nodes[id].parent;
      }).length;
      var warnings = data.warnings || [];
      var line = TgUi.fmt("status_ok_nodes", {
        blocks: Object.keys(state.nodes).length,
        lines: lastCode.split("\n").length
      });
      if (unlinked) { line += TgUi.fmt("status_unlinked", { count: unlinked }); }
      if (warnings.length) { line += " · " + warnings.join("; "); }
      setStatus(line, "ok");
    } catch (error) {
      setStatus(L("Нет связи с сервером tgblocks: ", "Cannot reach the tgblocks server: ") + error, "error");
    }
  }

  var timer = null;

  function scheduleSave() {
    if (restoring) {
      // Opening the view must not write anything: only real edits are saved.
      return;
    }
    // Debouncing, revision bookkeeping and the flush on page close all live in
    // the shared module, so this view saves exactly like the other two.
    TgProject.saveBoard(currentBoard());
  }

  function currentBoard() {
    return { nodes: state.nodes, counter: state.counter,
             rootId: state.rootId, manual: state.manual };
  }

  function scheduleCompile() {
    clearTimeout(timer);
    timer = setTimeout(compile, 400);
    scheduleSave();
  }

  function download(name, text, mime) {
    var blob = new Blob([text], { type: mime || "text/plain;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    link.href = url;
    link.download = name;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  // ------------------------------------------------------------------ files
  var fileName = document.getElementById("file-name");
  var importInput = document.getElementById("import");

  // The canvas is one picture of the shared text: the text is what all three
  // views agree on, while the board itself is kept as a draft so unconnected
  // blocks and hand-placed positions survive a reload.
  async function renderText(text) {
    if (!text.trim()) {
      applyProject({ nodes: {}, counter: 0, rootId: null });
      clearOutput("Пусто. Добавь блок «Бот» в меню слева.");
      setStatus(L("Пустой бот: добавь блок «Бот» в меню слева.", "Empty bot: add a bot block from the palette on the left."));
      return;
    }
    try {
      var name = TgProject.currentName();
      var response = await fetch("/api/to_nodes?name=" + encodeURIComponent(name), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source: text, name: name })
      });
      var data = await response.json();
      if (!data.ok) {
        setStatus(data.detail || data.error || L("не удалось показать текст блоками", "cannot show the text as blocks"), "error");
        return;
      }
      applyProject(data.nodes);
      dslPane.textContent = text;
      compile();
    } catch (error) {
      setStatus(L("Нет связи с сервером: ", "Cannot reach the server: ") + error, "error");
    }
  }

  async function loadProject(name) {
    try {
      var data = await TgProject.load(name);
      fileName.textContent = data.name;
      var draft = data.draft;
      var draftNodes = draft && draft.board ? Object.keys(draft.board.nodes || {}) : [];
      if (draft && draft.rev === data.rev && draftNodes.length) {
        // Exactly the canvas the user left, unconnected blocks included. An
        // empty draft is ignored: it would hide a perfectly good bot text.
        applyProject(draft.board);
        dslPane.textContent = data.text;
        compile();
      } else {
        await renderText(data.text);
      }
      setStatus(L("Файл: ", "File: ") + data.name);
    } catch (error) {
      setStatus(L("Не удалось открыть бота: ", "Could not open the bot: ") + error.message, "error");
    }
  }

  TgProject.configure({
    status: setStatus,
    reload: async function (fresh) {
      fileName.textContent = TgProject.currentName();
      await renderText(fresh.text);
    }
  });

  function isBlockMap(value) {
    if (!value || typeof value !== "object" || Array.isArray(value)) { return false; }
    var keys = Object.keys(value);
    if (!keys.length) { return true; }
    return keys.every(function (key) {
      var item = value[key];
      return !!item && typeof item === "object" && typeof item.type === "string";
    });
  }

  function readProject(stored) {
    // Accepts every shape met in practice:
    //   {nodes: blocks, counter, rootId}      - section
    //   {nodes: section, text: "..."}         - whole bot file
    //   {nodes: {nodes: section}}             - double wrapped file
    //   {b1: {...}, e2: {...}}                - bare map of blocks
    var section = stored && stored.nodes && typeof stored.nodes === "object"
      ? stored.nodes
      : stored;
    var guard = 0;
    while (guard < 5 && section && section.nodes &&
           typeof section.nodes === "object" && !isBlockMap(section.nodes)) {
      section = section.nodes;
      guard += 1;
    }
    if (section && section.nodes && isBlockMap(section.nodes)) {
      return { blocks: section.nodes, meta: section };
    }
    if (isBlockMap(section)) {
      return { blocks: section, meta: {} };
    }
    return { blocks: {}, meta: {} };
  }

  function applyProject(stored) {
    var project = readProject(stored);
    state.nodes = project.blocks;
    state.counter = project.meta.counter || 0;
    state.rootId = project.meta.rootId || null;
    if (!state.rootId || !state.nodes[state.rootId]) {
      var botId = Object.keys(state.nodes).filter(function (id) {
        return state.nodes[id] && state.nodes[id].type === "bot";
      })[0];
      state.rootId = botId || null;
    }
    if (!state.counter) {
      state.counter = Object.keys(state.nodes).reduce(function (max, id) {
        var number = parseInt(String(id).replace(/^[a-z]+/i, ""), 10);
        return isNaN(number) ? max : Math.max(max, number);
      }, 0);
    }
    state.selected = null;
    state.manual = true;
    restoring = true;
    render();
    restoring = false;
    var visible = state.rootId && state.nodes[state.rootId]
      ? state.nodes[state.rootId]
      : Object.keys(state.nodes).map(function (id) { return state.nodes[id]; })[0];
    if (visible && visible.x != null) {
      state.view.scale = 1;
      state.view.tx = 40 - visible.x;
      state.view.ty = 40 - visible.y;
      applyView();
      drawWires();
    }
  }

  async function openBoard() {
    // A real Explorer dialog: pick a bot file and swap the board to it.
    importInput.value = "";
    importInput.click();
  }

  importInput.addEventListener("change", function () {
    var file = importInput.files[0];
    if (!file) { return; }
    var reader = new FileReader();
    reader.onload = function () {
      var name = file.name.replace(/\.[^.]+$/, "").replace(/[^A-Za-z0-9_-]/g, "") || "bot1";
      var raw = String(reader.result || "").replace(/^\uFEFF/, "");
      var stored = null;
      try {
        var parsed = JSON.parse(raw);
        stored = parsed && parsed.nodes ? parsed.nodes : parsed;
      } catch (error) {
        setStatus(L("Это не файл блоков. Python-код открывается в «Вид: текст».", "That is not a block file. Python code opens in the text view."), "error");
        return;
      }
      TgProject.setName(name);
      fileName.textContent = name;
      applyProject(stored);
      TgProject.saveBoard(currentBoard());
      TgProject.flush();
      setStatus(L("Открыт файл: ", "Opened file: ") + file.name, "ok");
    };
    reader.readAsText(file);
    importInput.value = "";
  });

  // ------------------------------------------------------------------- boot
  document.getElementById("palette").addEventListener("click", function (event) {
    var item = event.target.closest("[data-add]");
    if (item) { addNode(item.dataset.add); }
  });

  var logPane = document.getElementById("pane-log");
  var logSince = 0;
  var logTimer = null;

  async function pollLogs() {
    try {
      var response = await fetch("/api/logs?since=" + logSince);
      var data = await response.json();
      if (data.lines.length) {
        logPane.textContent += data.lines.join("\n") + "\n";
        logPane.scrollTop = logPane.scrollHeight;
      }
      logSince = data.total;
      document.getElementById("btn-stop").disabled = !data.running;
    } catch (error) {
      /* server is gone: stop quietly */
    }
  }

  async function runBot() {
    if (!lastCode) { setStatus(L("Сначала собери код.", "Compile first."), "error"); return; }
    // The token usually sits in the bot block already: asking for it again on
    // every start was the most common complaint about this button.
    var token = "";
    if (!lastHasToken) {
      var entered = window.prompt(
        "У бота нет токена. Впиши его (Enter - взять из TG_BOT_TOKEN):", "");
      if (entered === null) { return; }
      token = entered;
    }
    try {
      var response = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: lastCode, token: token })
      });
      var data = await response.json();
      if (!data.ok) { setStatus(data.error || L("не запустилось", "did not start"), "error"); return; }
      logSince = 0;
      logPane.textContent = "";
      document.querySelector('[data-pane="logs"]').click();
      setStatus(L("Запущен (pid ", "Running (pid ") + data.pid + L("). Логи на вкладке «Логи».", "). See the Logs tab."), "ok");
      if (!logTimer) { logTimer = setInterval(pollLogs, 1000); }
      pollLogs();
    } catch (error) {
      setStatus(L("Нет связи с сервером: ", "Cannot reach the server: ") + error, "error");
    }
  }

  async function stopBot() {
    await fetch("/api/stop", { method: "POST" });
    setStatus(L("Остановлен.", "Stopped."), "ok");
    pollLogs();
  }

  document.getElementById("btn-clear").addEventListener("click", function () {
    if (!Object.keys(state.nodes).length) { return; }
    if (!window.confirm(L("Удалить все блоки?", "Delete every block?"))) { return; }
    snapshot();
    state.nodes = {};
    state.counter = 0;
    state.rootId = null;
    state.selected = null;
    pending = null;
    render();
    // Clearing is an edit of the shared document: save it, so the other two
    // views do not keep showing the bot that was just deleted here.
    scheduleCompile();
    setStatus(L("Всё удалено. Добавь блоки из меню слева.", "Everything deleted. Add blocks from the palette on the left."), "ok");
  });

  document.getElementById("btn-open").addEventListener("click", openBoard);
  (async function bootFiles() {
    await loadSchema();
    await loadProject(TgProject.currentName());
  })();

  document.getElementById("btn-run").addEventListener("click", runBot);
  document.getElementById("btn-stop").addEventListener("click", stopBot);
  document.getElementById("btn-stop").disabled = true;
  document.getElementById("btn-py").addEventListener("click", function () {
    download("bot.py", lastCode, "text/x-python;charset=utf-8");
  });
  document.getElementById("btn-copy").addEventListener("click", function () {
    var text = codePane.classList.contains("hidden") ? dslPane.textContent : lastCode;
    navigator.clipboard.writeText(text).then(function () {
      setStatus(L("Скопировано.", "Copied."), "ok");
    }, function () {
      setStatus(L("Браузер не дал доступ к буферу.", "The browser refused clipboard access."), "error");
    });
  });
  document.querySelectorAll(".tab").forEach(function (tab) {
    tab.addEventListener("click", function () {
      document.querySelectorAll(".tab").forEach(function (other) {
        other.classList.toggle("active", other === tab);
      });
      var pane = tab.dataset.pane;
      dslPane.classList.toggle("hidden", pane !== "text");
      codePane.classList.toggle("hidden", pane !== "code");
      logPane.classList.toggle("hidden", pane !== "logs");
    });
  });
  window.addEventListener("resize", function () {
    if (!state.rootId) { return; }
    layout();
    drawWires();
  });

  applyView();
  render();

  // Switching the interface language re-labels the palette and every block.
  window.TgUiOnChange = function () {
    if (!SCHEMA.actions.length) { return; }
    SCHEMA.actions.forEach(function (item) {
      LABEL[nodeTypeOf(item.kind)] = TgUi.tr(item);
    });
    buildPalette();
    render();
  };
})();
</script>
</body>
</html>
""",
    "src/tgblocks/visual/static/text.html": r"""<!DOCTYPE html>
<html lang="ru" translate="no">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title data-i18n="title_text">tgblocks - текст</title>
<style>
  :root { --chip:#1b2033; --chip-hover:#242b48; --field:#11151f; --scroll:#3a4166; --log:#0b0e16; --log-fg:#9aa2c6; --flyout:#1d2136; --tok-key:#c98bff; --tok-fn:#7ee0a8; --tok-str:#f0a35e; --tok-num:#5b8cff; --tok-com:#5d6488; --tok-pun:#8d93b4; --bg:#0e111c; --panel:#161a28; --line:#272c42; --fg:#e8eaf4; --muted:#8d93b4;
          --accent:#5b8cff; --ok:#7ee0a8; --err:#ff8f8f; }
  * { box-sizing: border-box; }
  html, body { height: 100%; }
  body { margin:0; display:flex; flex-direction:column; background:var(--bg); color:var(--fg);
         font:13px/1.45 "Segoe UI", system-ui, -apple-system, sans-serif; overflow:hidden; }
  header { display:flex; align-items:center; gap:6px; padding:8px 12px; background:var(--panel);
           border-bottom:1px solid var(--line); }
  h1 { margin:0 10px 0 0; font-size:13px; font-weight:600; letter-spacing:.3px; }
  h1 span { color:var(--muted); font-weight:400; }
  .spacer { flex:1; }
  button { font:inherit; color:var(--fg); background:var(--chip-hover); border:1px solid var(--line);
           border-radius:6px; padding:5px 9px; cursor:pointer; white-space:nowrap; }
  button:hover { background:#2c3260; }
  button.primary { background:var(--accent); border-color:var(--accent); color:#fff; font-weight:600; }
  a.nav { color:var(--muted); text-decoration:none; padding:5px 8px; border:1px solid var(--line);
          border-radius:6px; }
  main { flex:1; display:flex; min-height:0; }
  #editor { position:relative; flex:1 1 55%; min-width:280px; border-right:1px solid var(--line);
            overflow:hidden; }
  #highlight, #source {
      position:absolute; inset:0; margin:0; padding:14px 16px; border:0; overflow:auto;
      font:13px/1.6 "Cascadia Code", Consolas, "Courier New", monospace;
      white-space:pre-wrap; word-break:break-word; tab-size:4; }
  #highlight { pointer-events:none; color:var(--fg); }
  #source { background:transparent; color:transparent; caret-color:var(--fg);
            resize:none; outline:none; }
  #source::selection { background:rgba(91,140,255,.30); }
  #status { min-height:34px; padding:8px 12px; border-top:1px solid var(--line);
            color:var(--muted); white-space:pre-wrap; font-size:12px; }
  #status.ok { color:var(--ok); } #status.error { color:var(--err); }
  aside { flex:1 1 45%; min-width:280px; display:flex; flex-direction:column; min-height:0; }
  .tabs { display:flex; gap:6px; padding:7px 10px; background:var(--panel);
          border-bottom:1px solid var(--line); }
  .tabs b { color:var(--muted); font-weight:400; font-size:12px; padding:4px 0 4px 4px; }
  pre { flex:1; margin:0; padding:12px; overflow:auto; white-space:pre; tab-size:4;
        font:12px/1.55 "Cascadia Code", Consolas, "Courier New", monospace;
        scrollbar-width:thin; scrollbar-color:var(--scroll) transparent; }
  .tok-key { color:var(--tok-key); } .tok-fn { color:var(--tok-fn); } .tok-str { color:var(--tok-str); }
  .tok-num { color:var(--tok-num); } .tok-com { color:var(--tok-com); font-style:italic; }
  .tok-pun { color:var(--tok-pun); }
  .file-name { color:var(--muted); font-size:12px; padding:0 4px; }
  .hidden { display:none !important; }
  #pane-log { flex:0 0 32%; border-top:1px solid var(--line); background:var(--log);
              color:var(--log-fg); }
  /* ready-made calls from the catalogue: they insert text, they do not wrap it */
  #snippets { position:fixed; z-index:20; top:52px; right:16px; width:340px;
              max-height:70vh; overflow:auto; padding:10px; border:1px solid var(--line);
              border-radius:10px; background:var(--panel);
              box-shadow:0 18px 40px rgba(0,0,0,.45); }
  #snippets .group { margin:0 0 10px; }
  #snippets .group b { display:block; margin:0 0 5px; color:var(--muted);
                       font-size:11px; text-transform:uppercase; letter-spacing:.04em; }
  #snippets button { display:block; width:100%; margin:0 0 3px; padding:5px 8px;
                     border:1px solid var(--line); border-radius:6px;
                     background:transparent; color:var(--fg); font-size:12px;
                     text-align:left; cursor:pointer; }
  #snippets button:hover { background:var(--chip-hover); }
</style>
</head>
<body>
<header>
  <h1>tgblocks <span data-i18n="page_text">текст</span></h1>
  <button id="btn-open" data-i18n="open" title="открыть файл с диска">Открыть файл…</button>
  <span id="file-name" class="file-name">bot1</span>
  <button id="btn-clear" data-i18n="clear" title="очистить текст">Очистить</button>
  <button id="btn-compile" class="primary" data-i18n="compile">Собрать</button>
  <button id="btn-snippets" data-i18n="snippets" title="вставить готовый вызов">Вставить…</button>
  <button id="btn-run" data-i18n="run">▶ Запустить</button>
  <button id="btn-stop" data-i18n="stop">■ Стоп</button>
  <button id="btn-download" data-i18n="download">Скачать .py</button>
  <button id="btn-copy" data-i18n="copy">Копировать</button>
  <span class="spacer"></span>
  <a class="nav" href="/nodes" data-i18n="view_nodes">Вид: узлы</a>
  <a class="nav" href="/blocks" data-i18n="view_blocks">Вид: блоки</a>
</header>
<main>
  <input id="import" type="file" accept=".py,.txt,.tg" class="hidden" />
  <div id="snippets" class="hidden" aria-label="готовые блоки"></div>
  <div id="editor">
    <pre id="highlight"></pre>
    <textarea id="source" spellcheck="false" autocapitalize="off" autocomplete="off"></textarea>
  </div>
  <aside>
    <div class="tabs"><b data-i18n="tab_python">Python (aiogram 3)</b><span class="spacer"></span><b data-i18n="tab_logs">Логи</b></div>
    <pre id="pane-code"></pre>
    <pre id="pane-log" class="log"></pre>
    <div id="status">Пиши слева, Ctrl+Enter - собрать.</div>
  </aside>
</main>
<script src="/tgblocks-project.js"></script>
<script src="/tgblocks-ui.js"></script>
<script>
(function () {
  "use strict";

  // One-line translator for the few words that live in this page, not in the
  // catalogue: L("по-русски", "in english").
  function L(ru, en) {
    return (window.TgUi && TgUi.lang() === "en" && en) ? en : ru;
  }

  var source = document.getElementById("source");
  var highlight = document.getElementById("highlight");
  var pane = document.getElementById("pane-code");
  var statusEl = document.getElementById("status");
  var lastCode = "", lastHasToken = false;

  var NAMES = {
    token: 1, name: 1, on: 1, command: 1, message: 1, send: 1, button: 1, buttons: 1,
    when: 1, otherwise: 1, url: 1, TEXT: 1, PHOTO: 1, IMAGE: 1, STICKER: 1, VOICE: 1,
    VIDEO: 1, DOCUMENT: 1, ANIMATION: 1, ANY: 1
  };
  var OPS = { contains: 1, startswith: 1, endswith: 1 };

  // Ready-made calls, built from the server-side catalogue: the palette here
  // covers every action the compiler knows, including the ones added later.
  var snippetsEl = document.getElementById("snippets");

  function argumentText(param) {
    if (param.kind === "values") { return '"значение"'; }
    if (param.kind === "number") { return String(param.default || 0); }
    if (param.kind === "state") { return "order"; }
    if (param.kind === "bool") { return null; }
    return JSON.stringify(String(param.default == null ? "" : param.default));
  }

  function callText(spec) {
    var args = [];
    (spec.params || []).forEach(function (param) {
      var text = argumentText(param);
      if (text === null) { return; }
      if (!param.required && (param.default === "" || param.default == null)) { return; }
      args.push(text);
    });
    return spec.kind + "(" + args.join(", ") + ")";
  }

  function eventText(event) {
    if (event.kind === "command") { return 'on.command("/start"):\n    send("Привет")'; }
    if (event.kind === "text") { return 'on.message(TEXT, "привет"):\n    send("Привет")'; }
    if (event.kind === "callback") { return 'on.callback("/menu"):\n    send("Нажали кнопку")'; }
    if (event.kind === "state") { return 'on.state("order"):\n    send("Шаг диалога")'; }
    return "on." + event.kind + "():\n    send(\"Привет\")";
  }

  async function loadSchema() {
    var response;
    try {
      response = await fetch("/api/schema?lang=" +
                             (window.TgUi ? TgUi.lang() : "ru"));
    } catch (error) {
      return;
    }
    var schema = await response.json();
    if (!schema || !schema.actions) { return; }
    schema.actions.forEach(function (action) { NAMES[action.kind] = 1; });
    schema.events.forEach(function (event) { NAMES[event.kind] = 1; });

    snippetsEl.innerHTML = "";
    var groups = [["events", window.TgUi ? TgUi.tr({ label: "События",
                                                     label_en: "Events" }) : "События",
                   schema.events.map(eventText)]];
    schema.groups.forEach(function (group) {
      var items = schema.actions.filter(function (action) {
        return action.group === group.kind;
      }).map(callText);
      if (items.length) {
        groups.push([group.kind, window.TgUi ? TgUi.tr(group) : group.label, items]);
      }
    });
    groups.forEach(function (triple) {
      var box = document.createElement("div");
      box.className = "group";
      var head = document.createElement("b");
      head.textContent = triple[1];
      box.appendChild(head);
      triple[2].forEach(function (code) {
        var button = document.createElement("button");
        button.type = "button";
        button.textContent = code.split("\n")[0];
        button.title = code;
        button.addEventListener("click", function () {
          insertAtCursor(code + "\n");
          snippetsEl.classList.add("hidden");
        });
        box.appendChild(button);
      });
      snippetsEl.appendChild(box);
    });
  }

  function insertAtCursor(text) {
    var start = source.selectionStart;
    var before = source.value.slice(0, start);
    var lineStart = before.lastIndexOf("\n") + 1;
    var indent = (before.slice(lineStart).match(/^[ ]*/) || [""])[0];
    var block = text.split("\n").map(function (line, index) {
      return index === 0 ? line : indent + line;
    }).join("\n");
    source.value = before + block + source.value.slice(source.selectionEnd);
    var caret = start + block.length;
    source.selectionStart = source.selectionEnd = caret;
    source.focus();
    refresh();
    schedule();
  }

  document.getElementById("btn-snippets").addEventListener("click", function () {
    snippetsEl.classList.toggle("hidden");
  });
  document.addEventListener("click", function (event) {
    if (!snippetsEl.classList.contains("hidden") &&
        !snippetsEl.contains(event.target) &&
        event.target.id !== "btn-snippets") {
      snippetsEl.classList.add("hidden");
    }
  });

  function escapeHtml(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

  function classify(word) {
    if (NAMES[word]) { return "tok-fn"; }
    if (OPS[word] || word === "==" || word === "!=") { return "tok-key"; }
    return "";
  }

  function paint(text) {
    var out = "";
    var pattern = /(#[^\n]*)|("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')|([A-Za-z_][\w.]*)|(\d+)|([()\[\]{},:=.]+)/g;
    var index = 0;
    var match;
    while ((match = pattern.exec(text)) !== null) {
      out += escapeHtml(text.slice(index, match.index));
      var token = match[0];
      if (match[1]) { out += '<span class="tok-com">' + escapeHtml(token) + "</span>"; }
      else if (match[2]) { out += '<span class="tok-str">' + escapeHtml(token) + "</span>"; }
      else if (match[3]) {
        var cls = classify(token);
        out += cls ? '<span class="' + cls + '">' + escapeHtml(token) + "</span>"
                   : escapeHtml(token);
      }
      else if (match[4]) { out += '<span class="tok-num">' + escapeHtml(token) + "</span>"; }
      else { out += '<span class="tok-pun">' + escapeHtml(token) + "</span>"; }
      index = match.index + token.length;
    }
    out += escapeHtml(text.slice(index));
    return out;
  }

  function refresh() {
    highlight.innerHTML = paint(source.value) + "\n";
    highlight.scrollTop = source.scrollTop;
    highlight.scrollLeft = source.scrollLeft;
  }

  function setStatus(text, kind) {
    statusEl.textContent = text;
    statusEl.className = kind || "";
  }

  async function compile() {
    var text = source.value;
    if (!text.trim()) {
      lastCode = "";
      pane.textContent = "";
      setStatus(L("Пусто. Напиши ", "Empty. Write ") + 'token("...")' + L(" и ", " and ") + 'on.command("/start"):' + L("", ""));
      return;
    }
    try {
      var response = await fetch("/api/compile_text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source: text })
      });
      var data = await response.json();
      if (!data.ok) {
        lastCode = "";
        pane.textContent = "";
        setStatus(data.detail || data.error || L("Не собралось.", "Compilation failed."), "error");
        return;
      }
      lastCode = data.code;
      lastHasToken = !!data.has_token;
      pane.textContent = data.code;
      setStatus(TgUi.fmt("status_ok_lines",
                         { lines: data.code.split("\n").length }), "ok");
    } catch (error) {
      setStatus(L("Нет связи с сервером tgblocks: ", "Cannot reach the tgblocks server: ") + error, "error");
    }
  }

  var timer = null;
  function schedule() {
    clearTimeout(timer);
    timer = setTimeout(compile, 400);
    scheduleSave();
  }

  source.addEventListener("input", function () {
    refresh();
    schedule();
  });
  source.addEventListener("scroll", refresh);
  function nextIndent(line) {
    // How many extra spaces the next line deserves after this one.
    var trimmed = line.trim();
    if (/(^|[\s(])on\.[\w.]+\(.*\):\s*$/.test(trimmed)) { return 4; }
    if (/^(when|otherwise)\(.*\):\s*$/.test(trimmed)) { return 4; }
    if (/^send\(.*\)\s*$/.test(trimmed)) { return 4; }
    return 0;
  }

  function indentBlock(outdent) {
    var value = source.value;
    var from = value.lastIndexOf("\n", source.selectionStart - 1) + 1;
    var to = value.indexOf("\n", source.selectionEnd);
    if (to === -1) { to = value.length; }
    var chunk = value.slice(from, to);
    var lines = chunk.split("\n").map(function (line) {
      if (outdent) { return line.replace(/^ {1,4}/, ""); }
      return line.trim() ? "    " + line : line;
    });
    var replacement = lines.join("\n");
    source.value = value.slice(0, from) + replacement + value.slice(to);
    source.selectionStart = from;
    source.selectionEnd = from + replacement.length;
    refresh();
    schedule();
  }

  source.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey && !event.ctrlKey && !event.metaKey) {
      event.preventDefault();
      var value = source.value;
      var caret = source.selectionStart;
      var lineStart = value.lastIndexOf("\n", caret - 1) + 1;
      var line = value.slice(lineStart, caret);
      var indent = (line.match(/^ */) || [""])[0];
      var extra = new Array(nextIndent(line) + 1).join(" ");
      var insert = "\n" + indent + extra;
      source.value = value.slice(0, caret) + insert + value.slice(source.selectionEnd);
      var next = caret + insert.length;
      source.selectionStart = source.selectionEnd = next;
      refresh();
      schedule();
      return;
    }
    if (event.key === "Tab") {
      event.preventDefault();
      if (event.shiftKey || source.selectionStart !== source.selectionEnd) {
        indentBlock(event.shiftKey);
        return;
      }
      var caret = source.selectionStart;
      source.value = source.value.slice(0, caret) + "    " + source.value.slice(caret);
      source.selectionStart = source.selectionEnd = caret + 4;
      refresh();
      schedule();
    }
  });

  document.addEventListener("keydown", function (event) {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      event.preventDefault();
      compile();
    }
  });
  document.getElementById("btn-compile").addEventListener("click", compile);
  document.getElementById("btn-copy").addEventListener("click", function () {
    navigator.clipboard.writeText(lastCode || source.value).then(function () {
      setStatus(L("Скопировано.", "Copied."), "ok");
    }, function () {
      setStatus(L("Браузер не дал доступ к буферу.", "The browser refused clipboard access."), "error");
    });
  });
  document.getElementById("btn-download").addEventListener("click", function () {
    var blob = new Blob([lastCode], { type: "text/x-python;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var link = document.createElement("a");
    link.href = url;
    link.download = "bot.py";
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  });

  var fileName = document.getElementById("file-name");
  var importInput = document.getElementById("import");

  // The text is the shared document: every view reads and writes this one.
  function showText(text) {
    if (source.value === text) { return; }
    var caret = source.selectionStart;
    source.value = text;
    source.selectionStart = source.selectionEnd = Math.min(caret, text.length);
    refresh();
    compile();
  }

  TgProject.configure({
    status: setStatus,
    reload: async function (fresh) {
      showText(fresh.text);
      fileName.textContent = TgProject.currentName();
    }
  });

  function scheduleSave() {
    // Saving is debounced inside TgProject, next to the revision bookkeeping.
    TgProject.saveText(source.value);
  }

  async function loadFile(name) {
    try {
      var data = await TgProject.load(name);
      fileName.textContent = data.name;
      showText(data.text);
      setStatus(L("Файл: ", "File: ") + data.name);
    } catch (error) {
      setStatus(L("Не удалось открыть файл: ", "Could not open the file: ") + error.message, "error");
    }
  }

  importInput.addEventListener("change", function () {
    var file = importInput.files[0];
    if (!file) { return; }
    var reader = new FileReader();
    reader.onload = function () {
      var name = file.name.replace(/\.[^.]+$/, "").replace(/[^A-Za-z0-9_-]/g, "") || "bot1";
      showText(String(reader.result || "").replace(/^\uFEFF/, ""));
      TgProject.setName(name);
      fileName.textContent = name;
      TgProject.saveText(source.value);
      TgProject.flush();
      setStatus(L("Открыт файл: ", "Opened file: ") + file.name, "ok");
    };
    reader.readAsText(file);
    importInput.value = "";
  });

  var logEl = document.getElementById("pane-log");
  var logSince = 0;
  var polling = null;

  function appendLog(lines) {
    if (!lines.length) { return; }
    logEl.textContent += lines.join("\n") + "\n";
    logEl.scrollTop = logEl.scrollHeight;
  }

  async function pollLogs() {
    try {
      var response = await fetch("/api/logs?since=" + logSince);
      var data = await response.json();
      appendLog(data.lines);
      logSince = data.total;
      if (data.running) {
        document.getElementById("btn-stop").disabled = false;
      } else {
        document.getElementById("btn-stop").disabled = true;
      }
    } catch (error) {
      /* server gone: stop polling quietly */
    }
  }

  function startPolling() {
    if (polling) { return; }
    polling = setInterval(pollLogs, 1000);
  }

  async function runBot() {
    if (!lastCode) { setStatus(L("Сначала собери код.", "Compile first."), "error"); return; }
    // The token is usually already in token("..."): do not ask for it again.
    var token = "";
    if (!lastHasToken) {
      var entered = window.prompt(
        "У бота нет токена. Впиши его (Enter - взять из TG_BOT_TOKEN):", "");
      if (entered === null) { return; }
      token = entered;
    }
    try {
      var response = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: lastCode, token: token })
      });
      var data = await response.json();
      if (!data.ok) { setStatus(data.error || L("не запустилось", "did not start"), "error"); return; }
      logSince = 0;
      logEl.textContent = "";
      setStatus(L("Запущен (pid ", "Running (pid ") + data.pid + L("). Логи ниже.", "). Logs below."), "ok");
      startPolling();
      pollLogs();
    } catch (error) {
      setStatus(L("Нет связи с сервером: ", "Cannot reach the server: ") + error, "error");
    }
  }

  async function stopBot() {
    await fetch("/api/stop", { method: "POST" });
    setStatus(L("Остановлен.", "Stopped."), "ok");
    pollLogs();
  }

  document.getElementById("btn-run").addEventListener("click", runBot);
  document.getElementById("btn-stop").addEventListener("click", stopBot);
  document.getElementById("btn-stop").disabled = true;

  document.getElementById("btn-open").addEventListener("click", function () {
    importInput.value = "";
    importInput.click();
  });
  document.getElementById("btn-clear").addEventListener("click", function () {
    if (!source.value.trim()) { return; }
    if (!window.confirm(L("Очистить текст?", "Clear the text?"))) { return; }
    source.value = "";
    refresh();
    schedule();
    // Clearing here clears the shared bot for the other two views as well.
    TgProject.saveText("");
    setStatus(L("Пусто.", "Empty."), "ok");
  });
  (async function bootFiles() {
    await loadSchema();
    await loadFile(TgProject.currentName());
  })();

  refresh();
  setStatus(L("Enter - авто-отступ · Tab / Shift+Tab - отступ блока · Ctrl+Enter - собрать.", "Enter - auto-indent · Tab / Shift+Tab - indent a block · Ctrl+Enter - compile."));

  // The snippet palette is rebuilt in the new language without losing the code.
  window.TgUiOnChange = function () {
    loadSchema();
    refresh();
  };
})();
</script>
</body>
</html>
""",
    "src/tgblocks/visual/static/tgblocks-project.js": r"""/* One bot, three pictures of it.
 *
 * Every editor page (nodes.html, blocks.html, text.html) loads this module: it
 * owns the single project document behind all of them, so an edit made in one
 * view shows up in the others instead of being reset on the next switch.
 *
 * The document lives on the server as {rev, text, layout}:
 *   text   - the bot itself, in the text syntax: the only source of truth
 *   layout - where the blocks sit on the canvas (never invalidates a view)
 *   rev    - bumped on every text change; editors poll it to notice each other
 *
 * A save carries the revision it was based on. If another view saved in the
 * meantime the server refuses it (conflict) and this module reloads the fresh
 * text, so two open views can never silently overwrite each other.
 */
(function (global) {
  "use strict";

  var NAME_KEY = "tgblocks.bot";
  var POLL_MS = 1200;
  var SAVE_MS = 700;

  var state = {
    name: "",
    rev: 0,
    text: "",
    layout: {},
    draft: null,      // the node canvas as the user left it (may be unfinished)
    dirty: false,     // local changes waiting to be sent
    busy: false,      // a save is in flight
    editing: false    // the user is mid-gesture: never reload underneath them
  };

  var saveTimer = null;
  var pending = null;
  var pollTimer = null;
  var reloadHook = null;
  var statusHook = null;

  function currentName() {
    return global.localStorage.getItem(NAME_KEY) || "bot1";
  }

  function setName(name) {
    state.name = name;
    global.localStorage.setItem(NAME_KEY, name);
  }

  function status(text, kind) {
    if (statusHook) { statusHook(text, kind); }
  }

  function projectUrl(name) {
    return "/api/project?name=" + encodeURIComponent(name || state.name);
  }

  // ------------------------------------------------------------------ loading
  async function load(name) {
    var target = name || currentName();
    var response = await fetch(projectUrl(target));
    var data = await response.json();
    if (!data.ok) { throw new Error(data.error || "не удалось открыть бота"); }
    setName(data.name || target);
    state.rev = data.rev || 0;
    state.text = data.text || "";
    state.layout = data.layout || {};
    state.draft = data.draft || null;
    state.dirty = false;
    pending = null;
    clearTimeout(saveTimer);
    return {
      name: state.name, rev: state.rev, text: state.text,
      layout: state.layout, draft: state.draft
    };
  }

  // ------------------------------------------------------------------- saving
  function queue(payload) {
    pending = payload;
    state.dirty = true;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(flush, SAVE_MS);
  }

  function saveText(text) {
    if (typeof text !== "string") { return; }
    // An empty string is a legitimate edit ("Очистить"): the server bumps the
    // revision and every other view forgets the bot too.
    queue({ text: text });
  }

  function saveBoard(board) {
    // The server turns the board into the shared text and keeps its positions.
    queue({
      nodes: {
        nodes: board.nodes, counter: board.counter,
        rootId: board.rootId, manual: board.manual
      }
    });
  }

  async function apply(data, note) {
    state.rev = data.rev;
    state.text = data.text;
    state.dirty = false;
    if (reloadHook) {
      await reloadHook({ rev: data.rev, text: data.text, draft: data.draft || null });
    }
    if (note) { status(note, "ok"); }
  }

  async function flush() {
    clearTimeout(saveTimer);
    if (!pending || !state.name) { return; }
    var payload = pending;
    pending = null;
    payload.baseRev = state.rev;
    state.busy = true;
    try {
      var response = await fetch(projectUrl(), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      var data = await response.json();
      if (data.ok) {
        state.rev = data.rev;
        state.text = data.text;
        if (data.incomplete) {
          // A half-built canvas: it is kept as a draft, the bot text is not a
          // bot yet, so stay dirty and say nothing alarming.
          state.dirty = true;
          status("Доска сохранена черновиком: для бота нужен токен и событие.");
          return;
        }
        state.dirty = false;
        return;
      }
      if (data.conflict) {
        await apply(data, "Бот изменён в другом виде - показал свежую версию.");
        return;
      }
      if (data.incomplete) {
        state.dirty = true;
        status(data.error || "доска ещё не собрана в бота");
        return;
      }
      if (data.lossy) {
        // This view cannot express part of the bot: refuse quietly-but-clearly
        // and stop polling from reloading the canvas over the user's work.
        state.dirty = true;
        status(data.error, "error");
        return;
      }
      state.dirty = false;
      status(data.detail || data.error || "не сохранилось", "error");
    } catch (error) {
      // The edit stays in the editor; the next change retries the save.
      state.dirty = true;
      status("Нет связи с сервером: " + error, "error");
    } finally {
      state.busy = false;
    }
  }

  // -------------------------------------------------------------- live reload
  async function poll() {
    if (!state.name || state.busy || state.dirty || state.editing) { return; }
    try {
      var response = await fetch("/api/rev?name=" + encodeURIComponent(state.name));
      var data = await response.json();
      if (!data.ok || data.rev === state.rev) { return; }
      var fresh = await load(state.name);
      await apply(fresh, "Показал версию из другого вида.");
    } catch (error) {
      /* server is gone: stay quiet and keep working locally */
    }
  }

  function startPolling() {
    if (pollTimer) { return; }
    pollTimer = setInterval(poll, POLL_MS);
  }

  // ------------------------------------------------------------- page leaving
  function flushForUnload() {
    // Called from pagehide/beforeunload: the pending edit must reach the server
    // even though this page is about to disappear.
    clearTimeout(saveTimer);
    if (!pending || !state.name) { return; }
    var payload = pending;
    pending = null;
    payload.baseRev = state.rev;
    var body = JSON.stringify(payload);
    var url = projectUrl();
    try {
      if (global.navigator.sendBeacon && global.navigator.sendBeacon(url, body)) { return; }
    } catch (error) { /* fall through to a keepalive fetch */ }
    try {
      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: body,
        keepalive: true
      });
    } catch (error) { /* nothing else can be done while unloading */ }
  }

  // --------------------------------------------------------------------- hooks
  function configure(options) {
    options = options || {};
    reloadHook = options.reload || null;
    statusHook = options.status || null;
    if (!options.manualPolling) { startPolling(); }
  }

  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden") { flushForUnload(); }
  });
  global.addEventListener("pagehide", flushForUnload);

  global.TgProject = {
    configure: configure,
    load: load,
    saveText: saveText,
    saveBoard: saveBoard,
    flush: flush,
    poll: poll,
    setName: setName,
    currentName: currentName,
    setEditing: function (value) { state.editing = !!value; },
    getState: function () {
      return {
        name: state.name, rev: state.rev, text: state.text,
        draft: state.draft, dirty: state.dirty
      };
    }
  };
})(window);
""",
    "src/tgblocks/visual/static/tgblocks-ui.js": r"""/* Settings shared by the three editors: theme and interface language.
 *
 * Every page loads this module before its own script, so a preference is applied
 * before the first paint and the same choice follows the user between /nodes,
 * /text and /blocks. The catalogue labels come from /api/schema already
 * translated; `TgUi.tr()` picks the right one for the current language.
 */
(function (global) {
  "use strict";

  var THEME_KEY = "tgblocks.theme";
  var LANG_KEY = "tgblocks.lang";

  var TEXT = {
    ru: {
      settings: "Настройки",
      theme: "Тема",
      dark: "тёмная",
      light: "светлая",
      language: "Язык",
      russian: "русский",
      english: "english",
      close: "Закрыть",
      note: "Выбор запоминается в этом браузере.",
      open: "Открыть файл…",
      clear: "Очистить",
      compile: "Собрать",
      snippets: "Вставить…",
      run: "▶ Запустить",
      stop: "■ Стоп",
      download: "Скачать .py",
      copy: "Копировать",
      view_nodes: "Вид: узлы",
      view_text: "Вид: текст",
      view_blocks: "Вид: блоки",
      tab_text: "Текст",
      tab_python: "Python (aiogram 3)",
      tab_logs: "Логи",
      page_nodes: "узлы",
      page_text: "текст",
      page_blocks: "блоки",
      title_nodes: "tgblocks - узлы",
      title_text: "tgblocks - текст",
      title_blocks: "tgblocks - блоки",
      status_ok_nodes: "OK · блоков: {blocks} · строк aiogram-кода: {lines}",
      status_ok_lines: "OK · строк aiogram-кода: {lines}",
      status_unlinked: " · не подключено: {count}",
      status_empty_nodes: "Пусто. Добавь блоки из меню слева.",
      status_compiled_empty: "Пусто. Перетащи блок «токен» из палитры."
    },
    en: {
      settings: "Settings",
      theme: "Theme",
      dark: "dark",
      light: "light",
      language: "Language",
      russian: "русский",
      english: "english",
      close: "Close",
      note: "The choice is remembered in this browser.",
      open: "Open file…",
      clear: "Clear",
      compile: "Compile",
      snippets: "Insert…",
      run: "▶ Run",
      stop: "■ Stop",
      download: "Download .py",
      copy: "Copy",
      view_nodes: "View: nodes",
      view_text: "View: text",
      view_blocks: "View: blocks",
      tab_text: "Text",
      tab_python: "Python (aiogram 3)",
      tab_logs: "Logs",
      page_nodes: "nodes",
      page_text: "text",
      page_blocks: "blocks",
      title_nodes: "tgblocks - nodes",
      title_text: "tgblocks - text",
      title_blocks: "tgblocks - blocks",
      status_ok_nodes: "OK · blocks: {blocks} · lines of aiogram code: {lines}",
      status_ok_lines: "OK · lines of aiogram code: {lines}",
      status_unlinked: " · not connected: {count}",
      status_empty_nodes: "Empty. Add blocks from the palette on the left.",
      status_compiled_empty: "Empty. Drag the “token” block from the palette."
    }
  };

  var LIGHT_CSS =
    ':root[data-theme="light"] {' +
    '--bg:#f4f6fb; --panel:#ffffff; --line:#d7dce8; --fg:#1a1e2b;' +
    '--muted:#5c6480; --accent:#3b6cf0; --ok:#1f8a55; --err:#c0392b;' +
    '--node:#ffffff;' +
    '--chip:#eef2fb; --chip-hover:#e2e8f7; --field:#ffffff;' +
    '--scroll:#c3cada; --log:#f7f9ff; --log-fg:#3b4360; --flyout:#eef1f8;' +
    '--tok-key:#7b3fd6; --tok-fn:#1f8a55; --tok-str:#b45309;' +
    '--tok-num:#2b5bd7; --tok-com:#7b839e; --tok-pun:#6b7280; }' +
    ':root[data-theme="light"] body { background:var(--bg); color:var(--fg); }' +
    ':root[data-theme="light"] header,' +
    ' :root[data-theme="light"] #palette,' +
    ' :root[data-theme="light"] aside {' +
    'background:var(--panel); }' +
    ':root[data-theme="light"] .pal-title, :root[data-theme="light"] .pal-hint,' +
    ' :root[data-theme="light"] .pal-item span,' +
    ' :root[data-theme="light"] .field-label {' +
    'color:var(--muted); }' +
    ':root[data-theme="light"] .port { border-color:#9aa4c0; color:#4b5563; }' +
    // Only the visible wire: the wide transparent hit area underneath must stay
    // invisible, otherwise every connection looks like a thick grey pipe.
    ':root[data-theme="light"] #wires path.wire { stroke:#9aa4c0; }' +
    ':root[data-theme="light"] #wires path.wire-hit { stroke:transparent; }' +
    ':root[data-theme="light"] .node,' +
    ' :root[data-theme="light"] .node-head,' +
    ' :root[data-theme="light"] .node-body {' +
    'background:var(--node); color:var(--fg); }' +
    ':root[data-theme="light"] .node { box-shadow:0 2px 10px rgba(20,30,60,.12); }' +
    ':root[data-theme="light"] .node-body input,' +
    ' :root[data-theme="light"] .node-body select {' +
    'background:var(--field); color:var(--fg); border-color:var(--line); }' +
    ':root[data-theme="light"] button:hover { background:var(--chip-hover); }' +
    ':root[data-theme="light"] #canvas { background:var(--bg); }' +
    ':root[data-theme="light"] .tab.active { color:var(--fg); }' +
    /* the settings panel itself */
    '#tg-settings { position:fixed; z-index:60; top:52px; right:14px; width:270px;' +
    'padding:12px; border:1px solid var(--line); border-radius:10px;' +
    'background:var(--panel); color:var(--fg); box-shadow:0 18px 40px rgba(0,0,0,.45);' +
    'font:13px/1.4 system-ui, "Segoe UI", sans-serif; }' +
    '#tg-settings h3 { margin:0 0 8px; font-size:13px; font-weight:600; }' +
    '#tg-settings .row { margin:0 0 10px; }' +
    '#tg-settings .row > span { display:block; margin:0 0 4px; color:var(--muted);' +
    'font-size:11px; text-transform:uppercase; letter-spacing:.04em; }' +
    '#tg-settings .choices { display:flex; gap:6px; flex-wrap:wrap; }' +
    '#tg-settings button { padding:5px 10px; border:1px solid var(--line);' +
    'border-radius:6px; background:transparent; color:var(--fg); cursor:pointer;' +
    'font:inherit; }' +
    '#tg-settings button.active { border-color:var(--accent); color:var(--accent); }' +
    '#tg-settings .note { color:var(--muted); font-size:11px; margin:8px 0 0; }' +
    '#tg-settings-close { float:right; padding:2px 8px; }';

  // English is the default so the tool opens in the language most people read
  // the README in; the choice is remembered per browser.
  var state = { theme: "dark", lang: "en" };

  function read() {
    try {
      var theme = global.localStorage.getItem(THEME_KEY);
      var lang = global.localStorage.getItem(LANG_KEY);
      if (theme === "light" || theme === "dark") { state.theme = theme; }
      if (lang === "en" || lang === "ru") { state.lang = lang; }
      // ?theme=light and ?lang=ru make the choice shareable (and testable) and
      // stick for the following pages.
      var query = new URLSearchParams(global.location.search);
      var forcedTheme = query.get("theme");
      var forcedLang = query.get("lang");
      if (forcedTheme === "light" || forcedTheme === "dark") {
        state.theme = forcedTheme;
        global.localStorage.setItem(THEME_KEY, forcedTheme);
      }
      if (forcedLang === "en" || forcedLang === "ru") {
        state.lang = forcedLang;
        global.localStorage.setItem(LANG_KEY, forcedLang);
      }
    } catch (error) { /* private mode: keep the defaults */ }
  }

  function write() {
    try {
      global.localStorage.setItem(THEME_KEY, state.theme);
      global.localStorage.setItem(LANG_KEY, state.lang);
    } catch (error) { /* private mode: the choice lasts one page */ }
  }

  function t(key) {
    var table = TEXT[state.lang] || TEXT.ru;
    return table[key] || TEXT.ru[key] || key;
  }

  // A translated line with {placeholders} filled in.
  function fmt(key, values) {
    var text = t(key);
    Object.keys(values || {}).forEach(function (name) {
      text = text.split("{" + name + "}").join(String(values[name]));
    });
    return text;
  }

  // Catalogue label / hint for the current language, with a graceful fallback.
  function tr(item) {    if (!item) { return ""; }
    if (state.lang === "en" && item.label_en) { return item.label_en; }
    return item.label || "";
  }

  function hint(item) {
    if (!item) { return ""; }
    if (state.lang === "en" && item.hint_en) { return item.hint_en; }
    return item.hint || "";
  }

  function choiceLabel(choice) {
    if (!choice) { return ""; }
    if (state.lang === "en" && choice.label_en) { return choice.label_en; }
    return choice.label || "";
  }

  function apply() {
    var root = document.documentElement;
    root.setAttribute("data-theme", state.theme);
    root.setAttribute("lang", state.lang);
    var elements = document.querySelectorAll("[data-i18n]");
    for (var i = 0; i < elements.length; i += 1) {
      var key = elements[i].getAttribute("data-i18n");
      var text = (TEXT[state.lang] || TEXT.ru)[key];
      if (text) { elements[i].textContent = text; }
    }
    var toggle = document.getElementById("tg-settings-button");
    if (toggle) { toggle.textContent = "\u2699 " + t("settings"); }
    if (typeof global.TgUiOnChange === "function") { global.TgUiOnChange(state); }
  }

  function panel() {
    var existing = document.getElementById("tg-settings");
    if (existing) { existing.remove(); return; }
    var box = document.createElement("div");
    box.id = "tg-settings";

    var title = document.createElement("h3");
    title.textContent = t("settings");
    var close = document.createElement("button");
    close.id = "tg-settings-close";
    close.textContent = "✕";
    close.title = t("close");
    close.addEventListener("click", function () { box.remove(); });
    title.appendChild(close);
    box.appendChild(title);

    box.appendChild(row(t("theme"), [["dark", t("dark")], ["light", t("light")]],
                        state.theme, function (value) {
      state.theme = value;
      write();
      apply();
      box.remove();
      panel();
    }));
    box.appendChild(row(t("language"), [["ru", t("russian")], ["en", t("english")]],
                        state.lang, function (value) {
      state.lang = value;
      write();
      apply();
      box.remove();
      if (typeof global.TgUiOnLanguage === "function") { global.TgUiOnLanguage(state); }
      panel();
    }));

    var note = document.createElement("p");
    note.className = "note";
    note.textContent = t("note");
    box.appendChild(note);
    document.body.appendChild(box);
  }

  function row(label, choices, current, onPick) {
    var wrap = document.createElement("div");
    wrap.className = "row";
    var caption = document.createElement("span");
    caption.textContent = label;
    wrap.appendChild(caption);
    var list = document.createElement("div");
    list.className = "choices";
    choices.forEach(function (pair) {
      var button = document.createElement("button");
      button.type = "button";
      button.textContent = pair[1];
      if (pair[0] === current) { button.className = "active"; }
      button.addEventListener("click", function () { onPick(pair[0]); });
      list.appendChild(button);
    });
    wrap.appendChild(list);
    return wrap;
  }

  function injectStyle() {
    var style = document.createElement("style");
    style.textContent = LIGHT_CSS;
    document.head.appendChild(style);
  }

  function injectButton() {
    var header = document.querySelector("header");
    if (!header || document.getElementById("tg-settings-button")) { return; }
    var button = document.createElement("button");
    button.id = "tg-settings-button";
    button.type = "button";
    button.textContent = t("settings");
    button.addEventListener("click", function (event) {
      event.stopPropagation();
      panel();
    });
    document.addEventListener("click", function (event) {
      var box = document.getElementById("tg-settings");
      if (box && !box.contains(event.target) && event.target.id !== "tg-settings-button") {
        box.remove();
      }
    });
    var links = header.querySelector("a");
    if (links) { header.insertBefore(button, links); } else { header.appendChild(button); }
  }

  function boot() {
    read();
    injectStyle();
    injectButton();
    apply();
  }

  // The preference is read as soon as this file loads: a page's own script runs
  // before DOMContentLoaded, and it asks TgUi.lang() while building its palette.
  read();
  try {
    document.documentElement.setAttribute("data-theme", state.theme);
    document.documentElement.setAttribute("lang", state.lang);
  } catch (error) { /* no document yet: boot() will do it */ }

  global.TgUi = {
    boot: boot,
    tr: tr,
    hint: hint,
    choiceLabel: choiceLabel,
    t: t,
    fmt: fmt,
    lang: function () { return state.lang; },
    theme: function () { return state.theme; }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})(window);
""",
    "tests/botkit.py": '# A fake Telegram for tests: real aiogram, real dispatcher, no network.\n#\n# The generated bots are the product, so they are executed here exactly the way\n# `python bot.py` would run them - only the transport is replaced. Every API call\n# the bot makes is recorded, which lets a test assert what a user would see:\n# which message was sent, with which keyboard, in which order.\n\nimport asyncio\nimport types\n\nfrom aiogram import Bot\nfrom aiogram.client.session.base import BaseSession\nfrom aiogram.types import Chat, Message\n\nBOT_TOKEN = "42:TEST_TOKEN"\n\n\ndef _model_fields(model) -> set:\n    fields = getattr(model, "model_fields", None)          # pydantic v2\n    if fields is None:\n        fields = getattr(model, "__fields__", {})          # pydantic v1\n    return set(fields)\n\n\ndef _poll_payload() -> dict:\n    """A poll payload for the aiogram that is installed.\n\n    Telegram keeps adding required fields (3.31 brought `persistent_id`,\n    `allows_revoting` and `members_only`), and an old aiogram rejects what it does\n    not know. Asking the model which fields exist keeps the suite green on every\n    supported version.\n    """\n    from aiogram.types import Poll, PollOption\n\n    option = {"text": "a", "voter_count": 0}\n    if "persistent_id" in _model_fields(PollOption):\n        option["persistent_id"] = "0"\n\n    payload = {\n        "id": "1",\n        "question": "q",\n        "options": [option],\n        "total_voter_count": 1,\n        "is_closed": False,\n        "is_anonymous": False,\n        "type": "regular",\n        "allows_multiple_answers": False,\n    }\n    for name, value in (("allows_revoting", False), ("members_only", False)):\n        if name in _model_fields(Poll):\n            payload[name] = value\n    return payload\n\n# The smallest payload Telegram would accept for each kind of message content:\n# aiogram validates the update before the dispatcher sees it, so a made-up\n# "file_id only" object would fail for dice, polls, stickers and locations.\nCONTENT = {\n    # Telegram sends photo size variants as a list, biggest last.\n    "photo": [{"file_id": "f", "file_unique_id": "u", "width": 1, "height": 1}],\n    "sticker": {"file_id": "f", "file_unique_id": "u", "type": "regular", "width": 1,\n                "height": 1, "is_animated": False, "is_video": False},\n    "voice": {"file_id": "f", "file_unique_id": "u", "duration": 1},\n    "video": {"file_id": "f", "file_unique_id": "u", "width": 1, "height": 1,\n              "duration": 1},\n    "video_note": {"file_id": "f", "file_unique_id": "u", "length": 1, "duration": 1},\n    "audio": {"file_id": "f", "file_unique_id": "u", "duration": 1},\n    "document": {"file_id": "f", "file_unique_id": "u"},\n    "animation": {"file_id": "f", "file_unique_id": "u", "width": 1, "height": 1,\n                  "duration": 1},\n    "location": {"latitude": 1.0, "longitude": 1.0},\n    "contact": {"phone_number": "+100", "first_name": "Tester"},\n    # Telegram grows required Poll fields over time (aiogram 3.31 added three).\n    # The payload is built for the aiogram that is installed, so the suite runs on\n    # any supported version instead of only the newest one.\n    "poll": _poll_payload(),\n    "dice": {"emoji": "🎲", "value": 3},\n}\n\n\nclass FakeSession(BaseSession):\n    def __init__(self) -> None:\n        super().__init__()\n        self.methods = []\n        self.me = None\n\n    # ------------------------------------------------------------------ transport\n    def _response(self, method):\n        from aiogram.types import Message as MessageType\n\n        returning = getattr(method, "__returning__", None)\n        if isinstance(returning, type) and issubclass(returning, MessageType):\n            return Message(\n                message_id=999,\n                date=0,\n                chat=Chat(id=42, type="private"),\n            )\n        return True\n\n    async def make_request(self, bot, method, timeout=None):\n        self.methods.append(method)\n        return self._response(method)\n\n    async def stream_content(self, url, headers=None, timeout=30, chunk_size=65536,\n                            raise_for_status=True):\n        yield b""\n\n    async def close(self) -> None:\n        return None\n\n    # -------------------------------------------------------------------- queries\n    def all(self, cls):\n        return [method for method in self.methods if isinstance(method, cls)]\n\n    def first(self, cls):\n        found = self.all(cls)\n        assert found, "no {0} was sent; got {1}".format(\n            cls.__name__, [type(m).__name__ for m in self.methods]\n        )\n        return found[0]\n\n    def texts(self):\n        from aiogram.methods import SendMessage\n\n        return [method.text for method in self.all(SendMessage)]\n\n    def reset(self):\n        self.methods.clear()\n\n\nclass Harness:\n    """A generated bot, mounted on a fake Telegram."""\n\n    def __init__(self, code: str, name: str = "generated_bot") -> None:\n        self.code = code\n        self.session = FakeSession()\n        self.bot = Bot(token=BOT_TOKEN, session=self.session)\n        module = types.ModuleType(name)\n        module.__file__ = "<generated>"\n        exec(compile(code, "<generated>", "exec"), module.__dict__)\n        self.module = module\n        self.dp = module.dp\n        self.session.me = self.bot\n\n    # --------------------------------------------------------------------- updates\n    def ask(self, update: dict):\n        """Feed one raw update (the JSON Telegram would post) and return the reply."""\n        update = dict(update)\n        update.setdefault("update_id", len(self.session.methods) + 1)\n        return asyncio.run(self.dp.feed_raw_update(self.bot, update))\n\n    def command(self, text: str, chat_id: int = 42, user_id: int = 7):\n        return self.ask(message_payload(text, chat_id=chat_id, user_id=user_id))\n\n    def text(self, text: str, chat_id: int = 42, user_id: int = 7, chat_kind: str = ""):\n        return self.ask(message_payload(text, chat_id=chat_id, user_id=user_id,\n                                        chat_kind=chat_kind))\n\n    def content(self, field: str, chat_id: int = 42):\n        return self.ask(message_payload(None, chat_id=chat_id, extra={field: CONTENT[field]}))\n\n    def press(self, data: str, chat_id: int = 42):\n        return self.ask(callback_payload(data, chat_id=chat_id))\n\n\n# ---------------------------------------------------------------------- payloads\ndef _chat(chat_id: int, kind: str = "private") -> dict:\n    return {"id": chat_id, "type": kind}\n\n\ndef _user(user_id: int = 7) -> dict:\n    return {"id": user_id, "is_bot": False, "first_name": "Tester", "username": "tester"}\n\n\ndef message_payload(text, chat_id: int = 42, user_id: int = 7, extra=None,\n                    message_id: int = 1, chat_kind: str = "") -> dict:\n    kind = chat_kind or ("supergroup" if chat_id < 0 else "private")\n    message = {\n        "message_id": message_id,\n        "date": 1700000000,\n        "chat": _chat(chat_id, kind),\n        "from": _user(user_id),\n    }\n    if text is not None:\n        message["text"] = text\n        message["entities"] = (\n            [{"type": "bot_command", "offset": 0, "length": len(text)}]\n            if text.startswith("/")\n            else []\n        )\n    if extra:\n        message.update(extra)\n    return {"update_id": message_id, "message": message}\n\n\ndef callback_payload(data: str, chat_id: int = 42, user_id: int = 7) -> dict:\n    return {\n        "update_id": 5000,\n        "callback_query": {\n            "id": "cb-1",\n            "from": _user(user_id),\n            "chat_instance": "instance",\n            "data": data,\n            "message": {\n                "message_id": 2,\n                "date": 1700000000,\n                "chat": _chat(chat_id),\n                "text": "menu",\n            },\n        },\n    }\n\n\ndef edited_payload(text: str, chat_id: int = 42) -> dict:\n    return {\n        "update_id": 6000,\n        "edited_message": {\n            "message_id": 3,\n            "date": 1700000000,\n            "chat": _chat(chat_id),\n            "from": _user(),\n            "text": text,\n            "edit_date": 1700000001,\n        },\n    }\n\n\nclass FakeSleep:\n    """Replaces asyncio.sleep so `delay 5` does not slow the test suite down."""\n\n    def __init__(self) -> None:\n        self.delays = []\n\n    async def __call__(self, seconds, *args, **kwargs):\n        self.delays.append(seconds)\n        await _real_sleep(0)\n\n\n_real_sleep = asyncio.sleep\n\n\ndef fast_time(monkeypatch) -> FakeSleep:\n    fake = FakeSleep()\n    for target in (asyncio,):\n        monkeypatch.setattr(target, "sleep", fake)\n    return fake\n',
    "tests/corpus.py": '# Test corpus: every language feature the generators must keep working.\n#\n# Each entry is one bot. `syntax` says which front end parses the source, so the\n# same list protects the DSL, the text syntax and (later) the editors that emit\n# them. Adding a feature means adding an entry here: the golden file in\n# tests/golden/ then pins the exact generated code.\n\nfrom dataclasses import dataclass\n\n\n@dataclass(frozen=True)\nclass Case:\n    name: str\n    syntax: str  # "dsl" | "text"\n    source: str\n\n\ndef _case(name: str, syntax: str, source: str) -> Case:\n    return Case(name=name, syntax=syntax, source=source.lstrip("\\n"))\n\n\nCORPUS = [\n    _case(\n        "hello",\n        "dsl",\n        """\nbot token "123456:ABC"\nbot name "Hello bot"\n\non /start:\n    send "Hi! I am your bot."\n    buttons:\n        "Help" -> /help\n        "About" -> /about\n\non /help:\n    send "Commands: /start, /help, /about"\n    buttons reply:\n        "/start"\n        "/help"\n\non message:\n    when text contains "hi":\n        send "Hello there!"\n    else:\n        send "Not sure what you mean. Try /help."\n""",\n    ),\n    _case(\n        "events",\n        "dsl",\n        """\nbot token "1:events"\n\non message:\n    send "text"\non photo:\n    send "photo"\non sticker:\n    send "sticker"\non voice:\n    send "voice"\non video:\n    send "video"\non video_note:\n    send "round"\non audio:\n    send "audio"\non document:\n    send "document"\non animation:\n    send "gif"\non location:\n    send "location"\non contact:\n    send "contact"\non poll:\n    send "poll"\non new_members:\n    send "welcome"\non left_member:\n    send "bye"\non edited:\n    send "edited"\non any:\n    send "fallback"\n""",\n    ),\n    _case(\n        "actions",\n        "dsl",\n        """\nbot token "1:actions"\n\non /start:\n    typing\n    delay 2\n    delay 0.5\n    send "line one\\\\nline two \\\\"quoted\\\\""\n    send_photo "https://example.com/cat.jpg" "Котик"\n    send_photo "https://example.com/dog.jpg"\n    delete\n    pass\n""",\n    ),\n    _case(\n        "conditions",\n        "dsl",\n        """\nbot token "1:cond"\n\non message:\n    when text == "точное":\n        send "eq"\n    when text != "стоп":\n        send "ne"\n    when text contains "цена":\n        send "has"\n    when text startswith "купи":\n        send "starts"\n    when text endswith "?":\n        send "ends"\n    when text contains "a", "b":\n        send "any of them"\n    when text != "x", "y":\n        send "neither"\n""",\n    ),\n    _case(\n        "nested",\n        "dsl",\n        """\nbot token "1:nested"\n\non /start:\n    send "outer"\n    when text contains "a":\n        send "inner a"\n        when text contains "b":\n            send "deeper"\n        else:\n            send "inner not b"\n    else:\n        send "outer else"\n        buttons:\n            "Site" -> url "https://example.com"\n""",\n    ),\n    _case(\n        "patterns",\n        "dsl",\n        """\nbot token "1:patterns"\n\non message "привет", "здравствуй":\n    send "и тебе привет"\n\non text "buy":\n    send "уже покупаю"\n""",\n    ),\n    _case(\n        "proxy",\n        "dsl",\n        """\nbot token "1:proxy"\nbot proxy "socks5://127.0.0.1:1080"\n\non /start:\n    send "via proxy"\n""",\n    ),\n    _case(\n        "long-buttons",\n        "dsl",\n        \'\\n\'.join(\n            [\'bot token "1:long"\', "", "on /start:", \'    send "menu"\', "    buttons:"]\n            + [\n                \'        "Очень длинная подпись кнопки, которая точно не влезет в восемьдесят восемь символов %d" -> /cmd%d\'\n                % (index, index)\n                for index in range(3)\n            ]\n        ),\n    ),\n    _case(\n        "text-basic",\n        "text",\n        """\ntoken("123456:TEST")\nname("Текстовый бот")\n\non.command("/start"):\n    send("Привет")\n    button("Помощь", "/help")\n    button("Сайт", url="https://example.com")\n\non.message(TEXT, "привет", "Привет"):\n    send("И тебе привет")\n\non.message(PHOTO):\n    send("Хорошее фото")\n""",\n    ),\n    _case(\n        "text-actions",\n        "text",\n        """\ntoken("1:text")\nproxy("socks5://127.0.0.1:1080")\n\non.command("/start"):\n    typing()\n    delay(1.5)\n    send_photo("https://example.com/cat.jpg", "котик")\n    delete()\n\non.message(TEXT):\n    when("contains", "как дела";"как ты"):\n        send("Отлично")\n    otherwise():\n        send("Напиши /help")\n""",\n    ),\n    _case(\n        "text-buttons",\n        "text",\n        """\ntoken("1:buttons")\n\non.command("/menu"):\n    send("Меню")\n    buttons("inline")\n    button("Помощь", "/help")\n    button("Сайт", url="https://example.com")\n\non.command("/reply"):\n    buttons("reply")\n    send("Выбери")\n    button("Один")\n    button("Два")\n""",\n    ),\n]\n\n\ndef case_by_name(name: str) -> Case:\n    for case in CORPUS:\n        if case.name == name:\n            return case\n    raise KeyError(name)\n',
    "tests/golden/actions.py": r"""# Telegram bot generated by tgblocks - edit freely.
# Bot: tgblocks bot
# Run:  TG_BOT_TOKEN=123456:ABC python bot.py

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command

try:
    from aiohttp_socks import ProxyConnectionError
except Exception:  # aiohttp-socks is optional
    ProxyConnectionError = ConnectionError
from aiogram.types import (
    CallbackQuery,
    Message,
)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "1:actions")
PROXY = os.environ.get("TG_PROXY", "")

dp = Dispatcher()


async def reply(event, text, markup=None) -> None:
    # One call answers a plain message, an inline-button press or a chat event.
    if isinstance(event, CallbackQuery):
        if event.message is not None:
            await event.message.answer(text, reply_markup=markup)
        await event.answer()
    elif isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    else:
        await event.bot.send_message(event.chat.id, text, reply_markup=markup)


async def media(event, method, *args, **kwargs) -> None:
    # media(event, "answer_photo", "https://...", caption="...") - any send method
    message = event.message if isinstance(event, CallbackQuery) else event
    await getattr(message, method)(*args, **kwargs)
    if isinstance(event, CallbackQuery):
        await event.answer()


async def remove(event) -> None:
    # Delete the message the button or command arrived from.
    message = event.message if isinstance(event, CallbackQuery) else event
    await message.delete()
    if isinstance(event, CallbackQuery):
        await event.answer()


async def typing(event) -> None:
    # Show "bot is typing..." in the chat.
    message = event.message if isinstance(event, CallbackQuery) else event
    await event.bot.send_chat_action(message.chat.id, "typing")


async def delay(seconds) -> None:
    await asyncio.sleep(seconds)


@dp.message(Command("start"))
@dp.callback_query(F.data == "/start")
async def start(event) -> None:
    await typing(event)
    await delay(2)
    await delay(0.5)
    await reply(event, "line one\nline two \"quoted\"")
    await media(event, "answer_photo", "https://example.com/cat.jpg", caption="Котик")
    await media(event, "answer_photo", "https://example.com/dog.jpg")
    await remove(event)
    pass  # ничего


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_TOKEN":
        raise SystemExit(
            "No bot token: put one in the .tg file, pass --token, or set TG_BOT_TOKEN."
        )

    session = None
    if PROXY:
        try:
            import aiohttp_socks  # noqa: F401
        except ImportError:
            raise SystemExit(
                "Proxy needs the aiohttp-socks package: pip install aiohttp-socks"
            )
        session = AiohttpSession(proxy=PROXY)
    bot = Bot(token=BOT_TOKEN, session=session)

    try:
        await dp.start_polling(bot)
    except (TelegramNetworkError, OSError, ProxyConnectionError) as error:
        raise SystemExit(
            "Нет связи с api.telegram.org ({0}).\n"
            "Скорее всего Telegram заблокирован в этой сети. Варианты:\n"
            "  1) включить VPN для всей системы;\n"
            "  2) указать прокси: bot proxy \"socks5://127.0.0.1:1080\" или TG_PROXY=...\n"
            "     и поставить пакет: pip install aiohttp-socks".format(error)
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
""",
    "tests/golden/conditions.py": r"""# Telegram bot generated by tgblocks - edit freely.
# Bot: tgblocks bot
# Run:  TG_BOT_TOKEN=123456:ABC python bot.py

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError

try:
    from aiohttp_socks import ProxyConnectionError
except Exception:  # aiohttp-socks is optional
    ProxyConnectionError = ConnectionError
from aiogram.types import (
    CallbackQuery,
    Message,
)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "1:cond")
PROXY = os.environ.get("TG_PROXY", "")

dp = Dispatcher()


def text_of(event) -> str:
    # Message and CallbackQuery both land here, so unwrap the message first.
    message = event.message if isinstance(event, CallbackQuery) else event
    return (message.text or "") if message is not None else ""


async def reply(event, text, markup=None) -> None:
    # One call answers a plain message, an inline-button press or a chat event.
    if isinstance(event, CallbackQuery):
        if event.message is not None:
            await event.message.answer(text, reply_markup=markup)
        await event.answer()
    elif isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    else:
        await event.bot.send_message(event.chat.id, text, reply_markup=markup)


@dp.message(F.text)
async def on_text(event) -> None:
    if text_of(event) == "точное":
        await reply(event, "eq")
    if text_of(event) != "стоп":
        await reply(event, "ne")
    if "цена" in text_of(event).lower():
        await reply(event, "has")
    if text_of(event).lower().startswith("купи"):
        await reply(event, "starts")
    if text_of(event).lower().endswith("?"):
        await reply(event, "ends")
    if ("a" in text_of(event).lower()) or ("b" in text_of(event).lower()):
        await reply(event, "any of them")
    if text_of(event) != "x" and text_of(event) != "y":
        await reply(event, "neither")


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_TOKEN":
        raise SystemExit(
            "No bot token: put one in the .tg file, pass --token, or set TG_BOT_TOKEN."
        )

    session = None
    if PROXY:
        try:
            import aiohttp_socks  # noqa: F401
        except ImportError:
            raise SystemExit(
                "Proxy needs the aiohttp-socks package: pip install aiohttp-socks"
            )
        session = AiohttpSession(proxy=PROXY)
    bot = Bot(token=BOT_TOKEN, session=session)

    try:
        await dp.start_polling(bot)
    except (TelegramNetworkError, OSError, ProxyConnectionError) as error:
        raise SystemExit(
            "Нет связи с api.telegram.org ({0}).\n"
            "Скорее всего Telegram заблокирован в этой сети. Варианты:\n"
            "  1) включить VPN для всей системы;\n"
            "  2) указать прокси: bot proxy \"socks5://127.0.0.1:1080\" или TG_PROXY=...\n"
            "     и поставить пакет: pip install aiohttp-socks".format(error)
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
""",
    "tests/golden/events.py": r"""# Telegram bot generated by tgblocks - edit freely.
# Bot: tgblocks bot
# Run:  TG_BOT_TOKEN=123456:ABC python bot.py

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError

try:
    from aiohttp_socks import ProxyConnectionError
except Exception:  # aiohttp-socks is optional
    ProxyConnectionError = ConnectionError
from aiogram.types import (
    CallbackQuery,
    Message,
)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "1:events")
PROXY = os.environ.get("TG_PROXY", "")

dp = Dispatcher()


async def reply(event, text, markup=None) -> None:
    # One call answers a plain message, an inline-button press or a chat event.
    if isinstance(event, CallbackQuery):
        if event.message is not None:
            await event.message.answer(text, reply_markup=markup)
        await event.answer()
    elif isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    else:
        await event.bot.send_message(event.chat.id, text, reply_markup=markup)


@dp.message(F.text)
async def on_text(event) -> None:
    await reply(event, "text")


@dp.message(F.photo)
async def on_photo(event) -> None:
    await reply(event, "photo")


@dp.message(F.sticker)
async def on_sticker(event) -> None:
    await reply(event, "sticker")


@dp.message(F.voice)
async def on_voice(event) -> None:
    await reply(event, "voice")


@dp.message(F.video)
async def on_video(event) -> None:
    await reply(event, "video")


@dp.message(F.video_note)
async def on_video_note(event) -> None:
    await reply(event, "round")


@dp.message(F.audio)
async def on_audio(event) -> None:
    await reply(event, "audio")


@dp.message(F.document)
async def on_document(event) -> None:
    await reply(event, "document")


@dp.message(F.animation)
async def on_animation(event) -> None:
    await reply(event, "gif")


@dp.message(F.location)
async def on_location(event) -> None:
    await reply(event, "location")


@dp.message(F.contact)
async def on_contact(event) -> None:
    await reply(event, "contact")


@dp.message(F.poll)
async def on_poll(event) -> None:
    await reply(event, "poll")


@dp.message(F.new_chat_members)
async def on_new_members(event) -> None:
    await reply(event, "welcome")


@dp.message(F.left_chat_member)
async def on_left_member(event) -> None:
    await reply(event, "bye")


@dp.message()
async def on_any(event) -> None:
    await reply(event, "fallback")


@dp.edited_message(F.text)
async def on_edited(event) -> None:
    await reply(event, "edited")


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_TOKEN":
        raise SystemExit(
            "No bot token: put one in the .tg file, pass --token, or set TG_BOT_TOKEN."
        )

    session = None
    if PROXY:
        try:
            import aiohttp_socks  # noqa: F401
        except ImportError:
            raise SystemExit(
                "Proxy needs the aiohttp-socks package: pip install aiohttp-socks"
            )
        session = AiohttpSession(proxy=PROXY)
    bot = Bot(token=BOT_TOKEN, session=session)

    try:
        await dp.start_polling(bot)
    except (TelegramNetworkError, OSError, ProxyConnectionError) as error:
        raise SystemExit(
            "Нет связи с api.telegram.org ({0}).\n"
            "Скорее всего Telegram заблокирован в этой сети. Варианты:\n"
            "  1) включить VPN для всей системы;\n"
            "  2) указать прокси: bot proxy \"socks5://127.0.0.1:1080\" или TG_PROXY=...\n"
            "     и поставить пакет: pip install aiohttp-socks".format(error)
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
""",
    "tests/golden/hello.py": r"""# Telegram bot generated by tgblocks - edit freely.
# Bot: Hello bot
# Run:  TG_BOT_TOKEN=123456:ABC python bot.py

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command

try:
    from aiohttp_socks import ProxyConnectionError
except Exception:  # aiohttp-socks is optional
    ProxyConnectionError = ConnectionError
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "123456:ABC")
PROXY = os.environ.get("TG_PROXY", "")

dp = Dispatcher()


def inline(*buttons) -> InlineKeyboardMarkup:
    # inline(("Help", "/help", "command"), ("Site", "https://example.com", "url"))
    rows = []
    for label, target, kind in buttons:
        if kind == "web_app":
            rows.append([InlineKeyboardButton(text=label, web_app=WebAppInfo(url=target))])
        elif kind == "url" or target.startswith(("http://", "https://")):
            rows.append([InlineKeyboardButton(text=label, url=target)])
        else:
            rows.append([InlineKeyboardButton(text=label, callback_data=target)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def keyboard(*buttons) -> ReplyKeyboardMarkup:
    # keyboard(("Help", "text"), ("Phone", "contact")) - a reply keyboard
    rows = []
    for label, kind in buttons:
        if kind == "contact":
            rows.append([KeyboardButton(text=label, request_contact=True)])
        elif kind == "location":
            rows.append([KeyboardButton(text=label, request_location=True)])
        else:
            rows.append([KeyboardButton(text=label)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def text_of(event) -> str:
    # Message and CallbackQuery both land here, so unwrap the message first.
    message = event.message if isinstance(event, CallbackQuery) else event
    return (message.text or "") if message is not None else ""


async def reply(event, text, markup=None) -> None:
    # One call answers a plain message, an inline-button press or a chat event.
    if isinstance(event, CallbackQuery):
        if event.message is not None:
            await event.message.answer(text, reply_markup=markup)
        await event.answer()
    elif isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    else:
        await event.bot.send_message(event.chat.id, text, reply_markup=markup)


@dp.message(Command("start"))
@dp.callback_query(F.data == "/start")
async def start(event) -> None:
    await reply(
        event,
        "Hi! I am your bot.",
        inline(("Help", "/help", "command"), ("About", "/about", "command")),
    )


@dp.message(Command("help"))
@dp.callback_query(F.data == "/help")
async def help(event) -> None:
    await reply(
        event,
        "Commands: /start, /help, /about",
        keyboard(("/start", "text"), ("/help", "text")),
    )


@dp.message(F.text)
async def on_text(event) -> None:
    if "hi" in text_of(event).lower():
        await reply(event, "Hello there!")
    else:
        await reply(event, "Not sure what you mean. Try /help.")


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_TOKEN":
        raise SystemExit(
            "No bot token: put one in the .tg file, pass --token, or set TG_BOT_TOKEN."
        )

    session = None
    if PROXY:
        try:
            import aiohttp_socks  # noqa: F401
        except ImportError:
            raise SystemExit(
                "Proxy needs the aiohttp-socks package: pip install aiohttp-socks"
            )
        session = AiohttpSession(proxy=PROXY)
    bot = Bot(token=BOT_TOKEN, session=session)

    try:
        await dp.start_polling(bot)
    except (TelegramNetworkError, OSError, ProxyConnectionError) as error:
        raise SystemExit(
            "Нет связи с api.telegram.org ({0}).\n"
            "Скорее всего Telegram заблокирован в этой сети. Варианты:\n"
            "  1) включить VPN для всей системы;\n"
            "  2) указать прокси: bot proxy \"socks5://127.0.0.1:1080\" или TG_PROXY=...\n"
            "     и поставить пакет: pip install aiohttp-socks".format(error)
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
""",
    "tests/golden/long-buttons.py": r"""# Telegram bot generated by tgblocks - edit freely.
# Bot: tgblocks bot
# Run:  TG_BOT_TOKEN=123456:ABC python bot.py

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command

try:
    from aiohttp_socks import ProxyConnectionError
except Exception:  # aiohttp-socks is optional
    ProxyConnectionError = ConnectionError
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "1:long")
PROXY = os.environ.get("TG_PROXY", "")

dp = Dispatcher()


def inline(*buttons) -> InlineKeyboardMarkup:
    # inline(("Help", "/help", "command"), ("Site", "https://example.com", "url"))
    rows = []
    for label, target, kind in buttons:
        if kind == "web_app":
            rows.append([InlineKeyboardButton(text=label, web_app=WebAppInfo(url=target))])
        elif kind == "url" or target.startswith(("http://", "https://")):
            rows.append([InlineKeyboardButton(text=label, url=target)])
        else:
            rows.append([InlineKeyboardButton(text=label, callback_data=target)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def reply(event, text, markup=None) -> None:
    # One call answers a plain message, an inline-button press or a chat event.
    if isinstance(event, CallbackQuery):
        if event.message is not None:
            await event.message.answer(text, reply_markup=markup)
        await event.answer()
    elif isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    else:
        await event.bot.send_message(event.chat.id, text, reply_markup=markup)


@dp.message(Command("start"))
@dp.callback_query(F.data == "/start")
async def start(event) -> None:
    await reply(
        event,
        "menu",
        inline(
            ("Очень длинная подпись кнопки, которая точно не влезет в восемьдесят восемь символов 0", "/cmd0", "command"),
            ("Очень длинная подпись кнопки, которая точно не влезет в восемьдесят восемь символов 1", "/cmd1", "command"),
            ("Очень длинная подпись кнопки, которая точно не влезет в восемьдесят восемь символов 2", "/cmd2", "command"),
        ),
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_TOKEN":
        raise SystemExit(
            "No bot token: put one in the .tg file, pass --token, or set TG_BOT_TOKEN."
        )

    session = None
    if PROXY:
        try:
            import aiohttp_socks  # noqa: F401
        except ImportError:
            raise SystemExit(
                "Proxy needs the aiohttp-socks package: pip install aiohttp-socks"
            )
        session = AiohttpSession(proxy=PROXY)
    bot = Bot(token=BOT_TOKEN, session=session)

    try:
        await dp.start_polling(bot)
    except (TelegramNetworkError, OSError, ProxyConnectionError) as error:
        raise SystemExit(
            "Нет связи с api.telegram.org ({0}).\n"
            "Скорее всего Telegram заблокирован в этой сети. Варианты:\n"
            "  1) включить VPN для всей системы;\n"
            "  2) указать прокси: bot proxy \"socks5://127.0.0.1:1080\" или TG_PROXY=...\n"
            "     и поставить пакет: pip install aiohttp-socks".format(error)
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
""",
    "tests/golden/nested.py": r"""# Telegram bot generated by tgblocks - edit freely.
# Bot: tgblocks bot
# Run:  TG_BOT_TOKEN=123456:ABC python bot.py

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command

try:
    from aiohttp_socks import ProxyConnectionError
except Exception:  # aiohttp-socks is optional
    ProxyConnectionError = ConnectionError
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "1:nested")
PROXY = os.environ.get("TG_PROXY", "")

dp = Dispatcher()


def inline(*buttons) -> InlineKeyboardMarkup:
    # inline(("Help", "/help", "command"), ("Site", "https://example.com", "url"))
    rows = []
    for label, target, kind in buttons:
        if kind == "web_app":
            rows.append([InlineKeyboardButton(text=label, web_app=WebAppInfo(url=target))])
        elif kind == "url" or target.startswith(("http://", "https://")):
            rows.append([InlineKeyboardButton(text=label, url=target)])
        else:
            rows.append([InlineKeyboardButton(text=label, callback_data=target)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def text_of(event) -> str:
    # Message and CallbackQuery both land here, so unwrap the message first.
    message = event.message if isinstance(event, CallbackQuery) else event
    return (message.text or "") if message is not None else ""


async def reply(event, text, markup=None) -> None:
    # One call answers a plain message, an inline-button press or a chat event.
    if isinstance(event, CallbackQuery):
        if event.message is not None:
            await event.message.answer(text, reply_markup=markup)
        await event.answer()
    elif isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    else:
        await event.bot.send_message(event.chat.id, text, reply_markup=markup)


@dp.message(Command("start"))
@dp.callback_query(F.data == "/start")
async def start(event) -> None:
    await reply(event, "outer")
    if "a" in text_of(event).lower():
        await reply(event, "inner a")
        if "b" in text_of(event).lower():
            await reply(event, "deeper")
        else:
            await reply(event, "inner not b")
    else:
        await reply(
            event,
            "outer else",
            inline(("Site", "https://example.com", "url")),
        )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_TOKEN":
        raise SystemExit(
            "No bot token: put one in the .tg file, pass --token, or set TG_BOT_TOKEN."
        )

    session = None
    if PROXY:
        try:
            import aiohttp_socks  # noqa: F401
        except ImportError:
            raise SystemExit(
                "Proxy needs the aiohttp-socks package: pip install aiohttp-socks"
            )
        session = AiohttpSession(proxy=PROXY)
    bot = Bot(token=BOT_TOKEN, session=session)

    try:
        await dp.start_polling(bot)
    except (TelegramNetworkError, OSError, ProxyConnectionError) as error:
        raise SystemExit(
            "Нет связи с api.telegram.org ({0}).\n"
            "Скорее всего Telegram заблокирован в этой сети. Варианты:\n"
            "  1) включить VPN для всей системы;\n"
            "  2) указать прокси: bot proxy \"socks5://127.0.0.1:1080\" или TG_PROXY=...\n"
            "     и поставить пакет: pip install aiohttp-socks".format(error)
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
""",
    "tests/golden/patterns.py": r"""# Telegram bot generated by tgblocks - edit freely.
# Bot: tgblocks bot
# Run:  TG_BOT_TOKEN=123456:ABC python bot.py

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError

try:
    from aiohttp_socks import ProxyConnectionError
except Exception:  # aiohttp-socks is optional
    ProxyConnectionError = ConnectionError
from aiogram.types import (
    CallbackQuery,
    Message,
)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "1:patterns")
PROXY = os.environ.get("TG_PROXY", "")

dp = Dispatcher()


async def reply(event, text, markup=None) -> None:
    # One call answers a plain message, an inline-button press or a chat event.
    if isinstance(event, CallbackQuery):
        if event.message is not None:
            await event.message.answer(text, reply_markup=markup)
        await event.answer()
    elif isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    else:
        await event.bot.send_message(event.chat.id, text, reply_markup=markup)


@dp.message(F.text, F.text.in_(("привет", "здравствуй")))
async def on_text(event) -> None:
    await reply(event, "и тебе привет")


@dp.message(F.text, F.text.in_(("buy",)))
async def on_text_1(event) -> None:
    await reply(event, "уже покупаю")


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_TOKEN":
        raise SystemExit(
            "No bot token: put one in the .tg file, pass --token, or set TG_BOT_TOKEN."
        )

    session = None
    if PROXY:
        try:
            import aiohttp_socks  # noqa: F401
        except ImportError:
            raise SystemExit(
                "Proxy needs the aiohttp-socks package: pip install aiohttp-socks"
            )
        session = AiohttpSession(proxy=PROXY)
    bot = Bot(token=BOT_TOKEN, session=session)

    try:
        await dp.start_polling(bot)
    except (TelegramNetworkError, OSError, ProxyConnectionError) as error:
        raise SystemExit(
            "Нет связи с api.telegram.org ({0}).\n"
            "Скорее всего Telegram заблокирован в этой сети. Варианты:\n"
            "  1) включить VPN для всей системы;\n"
            "  2) указать прокси: bot proxy \"socks5://127.0.0.1:1080\" или TG_PROXY=...\n"
            "     и поставить пакет: pip install aiohttp-socks".format(error)
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
""",
    "tests/golden/proxy.py": r"""# Telegram bot generated by tgblocks - edit freely.
# Bot: tgblocks bot
# Run:  TG_BOT_TOKEN=123456:ABC python bot.py

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command

try:
    from aiohttp_socks import ProxyConnectionError
except Exception:  # aiohttp-socks is optional
    ProxyConnectionError = ConnectionError
from aiogram.types import (
    CallbackQuery,
    Message,
)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "1:proxy")
PROXY = os.environ.get("TG_PROXY", "socks5://127.0.0.1:1080")

dp = Dispatcher()


async def reply(event, text, markup=None) -> None:
    # One call answers a plain message, an inline-button press or a chat event.
    if isinstance(event, CallbackQuery):
        if event.message is not None:
            await event.message.answer(text, reply_markup=markup)
        await event.answer()
    elif isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    else:
        await event.bot.send_message(event.chat.id, text, reply_markup=markup)


@dp.message(Command("start"))
@dp.callback_query(F.data == "/start")
async def start(event) -> None:
    await reply(event, "via proxy")


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_TOKEN":
        raise SystemExit(
            "No bot token: put one in the .tg file, pass --token, or set TG_BOT_TOKEN."
        )

    session = None
    if PROXY:
        try:
            import aiohttp_socks  # noqa: F401
        except ImportError:
            raise SystemExit(
                "Proxy needs the aiohttp-socks package: pip install aiohttp-socks"
            )
        session = AiohttpSession(proxy=PROXY)
    bot = Bot(token=BOT_TOKEN, session=session)

    try:
        await dp.start_polling(bot)
    except (TelegramNetworkError, OSError, ProxyConnectionError) as error:
        raise SystemExit(
            "Нет связи с api.telegram.org ({0}).\n"
            "Скорее всего Telegram заблокирован в этой сети. Варианты:\n"
            "  1) включить VPN для всей системы;\n"
            "  2) указать прокси: bot proxy \"socks5://127.0.0.1:1080\" или TG_PROXY=...\n"
            "     и поставить пакет: pip install aiohttp-socks".format(error)
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
""",
    "tests/golden/text-actions.py": r"""# Telegram bot generated by tgblocks - edit freely.
# Bot: tgblocks bot
# Run:  TG_BOT_TOKEN=123456:ABC python bot.py

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command

try:
    from aiohttp_socks import ProxyConnectionError
except Exception:  # aiohttp-socks is optional
    ProxyConnectionError = ConnectionError
from aiogram.types import (
    CallbackQuery,
    Message,
)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "1:text")
PROXY = os.environ.get("TG_PROXY", "socks5://127.0.0.1:1080")

dp = Dispatcher()


def text_of(event) -> str:
    # Message and CallbackQuery both land here, so unwrap the message first.
    message = event.message if isinstance(event, CallbackQuery) else event
    return (message.text or "") if message is not None else ""


async def reply(event, text, markup=None) -> None:
    # One call answers a plain message, an inline-button press or a chat event.
    if isinstance(event, CallbackQuery):
        if event.message is not None:
            await event.message.answer(text, reply_markup=markup)
        await event.answer()
    elif isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    else:
        await event.bot.send_message(event.chat.id, text, reply_markup=markup)


async def media(event, method, *args, **kwargs) -> None:
    # media(event, "answer_photo", "https://...", caption="...") - any send method
    message = event.message if isinstance(event, CallbackQuery) else event
    await getattr(message, method)(*args, **kwargs)
    if isinstance(event, CallbackQuery):
        await event.answer()


async def remove(event) -> None:
    # Delete the message the button or command arrived from.
    message = event.message if isinstance(event, CallbackQuery) else event
    await message.delete()
    if isinstance(event, CallbackQuery):
        await event.answer()


async def typing(event) -> None:
    # Show "bot is typing..." in the chat.
    message = event.message if isinstance(event, CallbackQuery) else event
    await event.bot.send_chat_action(message.chat.id, "typing")


async def delay(seconds) -> None:
    await asyncio.sleep(seconds)


@dp.message(Command("start"))
@dp.callback_query(F.data == "/start")
async def start(event) -> None:
    await typing(event)
    await delay(1.5)
    await media(event, "answer_photo", "https://example.com/cat.jpg", caption="котик")
    await remove(event)


@dp.message(F.text)
async def on_text(event) -> None:
    if ("как дела" in text_of(event).lower()) or ("как ты" in text_of(event).lower()):
        await reply(event, "Отлично")
    else:
        await reply(event, "Напиши /help")


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_TOKEN":
        raise SystemExit(
            "No bot token: put one in the .tg file, pass --token, or set TG_BOT_TOKEN."
        )

    session = None
    if PROXY:
        try:
            import aiohttp_socks  # noqa: F401
        except ImportError:
            raise SystemExit(
                "Proxy needs the aiohttp-socks package: pip install aiohttp-socks"
            )
        session = AiohttpSession(proxy=PROXY)
    bot = Bot(token=BOT_TOKEN, session=session)

    try:
        await dp.start_polling(bot)
    except (TelegramNetworkError, OSError, ProxyConnectionError) as error:
        raise SystemExit(
            "Нет связи с api.telegram.org ({0}).\n"
            "Скорее всего Telegram заблокирован в этой сети. Варианты:\n"
            "  1) включить VPN для всей системы;\n"
            "  2) указать прокси: bot proxy \"socks5://127.0.0.1:1080\" или TG_PROXY=...\n"
            "     и поставить пакет: pip install aiohttp-socks".format(error)
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
""",
    "tests/golden/text-basic.py": r"""# Telegram bot generated by tgblocks - edit freely.
# Bot: Текстовый бот
# Run:  TG_BOT_TOKEN=123456:ABC python bot.py

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command

try:
    from aiohttp_socks import ProxyConnectionError
except Exception:  # aiohttp-socks is optional
    ProxyConnectionError = ConnectionError
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "123456:TEST")
PROXY = os.environ.get("TG_PROXY", "")

dp = Dispatcher()


def inline(*buttons) -> InlineKeyboardMarkup:
    # inline(("Help", "/help", "command"), ("Site", "https://example.com", "url"))
    rows = []
    for label, target, kind in buttons:
        if kind == "web_app":
            rows.append([InlineKeyboardButton(text=label, web_app=WebAppInfo(url=target))])
        elif kind == "url" or target.startswith(("http://", "https://")):
            rows.append([InlineKeyboardButton(text=label, url=target)])
        else:
            rows.append([InlineKeyboardButton(text=label, callback_data=target)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def reply(event, text, markup=None) -> None:
    # One call answers a plain message, an inline-button press or a chat event.
    if isinstance(event, CallbackQuery):
        if event.message is not None:
            await event.message.answer(text, reply_markup=markup)
        await event.answer()
    elif isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    else:
        await event.bot.send_message(event.chat.id, text, reply_markup=markup)


@dp.message(Command("start"))
@dp.callback_query(F.data == "/start")
async def start(event) -> None:
    await reply(
        event,
        "Привет",
        inline(("Помощь", "/help", "command"), ("Сайт", "https://example.com", "url")),
    )


@dp.message(F.text, F.text.in_(("привет", "Привет")))
async def on_text(event) -> None:
    await reply(event, "И тебе привет")


@dp.message(F.photo)
async def on_photo(event) -> None:
    await reply(event, "Хорошее фото")


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_TOKEN":
        raise SystemExit(
            "No bot token: put one in the .tg file, pass --token, or set TG_BOT_TOKEN."
        )

    session = None
    if PROXY:
        try:
            import aiohttp_socks  # noqa: F401
        except ImportError:
            raise SystemExit(
                "Proxy needs the aiohttp-socks package: pip install aiohttp-socks"
            )
        session = AiohttpSession(proxy=PROXY)
    bot = Bot(token=BOT_TOKEN, session=session)

    try:
        await dp.start_polling(bot)
    except (TelegramNetworkError, OSError, ProxyConnectionError) as error:
        raise SystemExit(
            "Нет связи с api.telegram.org ({0}).\n"
            "Скорее всего Telegram заблокирован в этой сети. Варианты:\n"
            "  1) включить VPN для всей системы;\n"
            "  2) указать прокси: bot proxy \"socks5://127.0.0.1:1080\" или TG_PROXY=...\n"
            "     и поставить пакет: pip install aiohttp-socks".format(error)
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
""",
    "tests/golden/text-buttons.py": r"""# Telegram bot generated by tgblocks - edit freely.
# Bot: tgblocks bot
# Run:  TG_BOT_TOKEN=123456:ABC python bot.py

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command

try:
    from aiohttp_socks import ProxyConnectionError
except Exception:  # aiohttp-socks is optional
    ProxyConnectionError = ConnectionError
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "1:buttons")
PROXY = os.environ.get("TG_PROXY", "")

dp = Dispatcher()


def inline(*buttons) -> InlineKeyboardMarkup:
    # inline(("Help", "/help", "command"), ("Site", "https://example.com", "url"))
    rows = []
    for label, target, kind in buttons:
        if kind == "web_app":
            rows.append([InlineKeyboardButton(text=label, web_app=WebAppInfo(url=target))])
        elif kind == "url" or target.startswith(("http://", "https://")):
            rows.append([InlineKeyboardButton(text=label, url=target)])
        else:
            rows.append([InlineKeyboardButton(text=label, callback_data=target)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def keyboard(*buttons) -> ReplyKeyboardMarkup:
    # keyboard(("Help", "text"), ("Phone", "contact")) - a reply keyboard
    rows = []
    for label, kind in buttons:
        if kind == "contact":
            rows.append([KeyboardButton(text=label, request_contact=True)])
        elif kind == "location":
            rows.append([KeyboardButton(text=label, request_location=True)])
        else:
            rows.append([KeyboardButton(text=label)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


async def reply(event, text, markup=None) -> None:
    # One call answers a plain message, an inline-button press or a chat event.
    if isinstance(event, CallbackQuery):
        if event.message is not None:
            await event.message.answer(text, reply_markup=markup)
        await event.answer()
    elif isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    else:
        await event.bot.send_message(event.chat.id, text, reply_markup=markup)


@dp.message(Command("menu"))
@dp.callback_query(F.data == "/menu")
async def menu(event) -> None:
    await reply(
        event,
        "Меню",
        inline(("Помощь", "/help", "command"), ("Сайт", "https://example.com", "url")),
    )


@dp.message(Command("reply"))
@dp.callback_query(F.data == "/reply")
async def cmd_reply(event) -> None:
    await reply(
        event,
        "Выбери",
        keyboard(("Один", "text"), ("Два", "text")),
    )


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN or BOT_TOKEN == "PASTE_YOUR_TOKEN":
        raise SystemExit(
            "No bot token: put one in the .tg file, pass --token, or set TG_BOT_TOKEN."
        )

    session = None
    if PROXY:
        try:
            import aiohttp_socks  # noqa: F401
        except ImportError:
            raise SystemExit(
                "Proxy needs the aiohttp-socks package: pip install aiohttp-socks"
            )
        session = AiohttpSession(proxy=PROXY)
    bot = Bot(token=BOT_TOKEN, session=session)

    try:
        await dp.start_polling(bot)
    except (TelegramNetworkError, OSError, ProxyConnectionError) as error:
        raise SystemExit(
            "Нет связи с api.telegram.org ({0}).\n"
            "Скорее всего Telegram заблокирован в этой сети. Варианты:\n"
            "  1) включить VPN для всей системы;\n"
            "  2) указать прокси: bot proxy \"socks5://127.0.0.1:1080\" или TG_PROXY=...\n"
            "     и поставить пакет: pip install aiohttp-socks".format(error)
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
""",
    "tests/test_blockly.py": r"""# Blockly definitions are generated on the server.
#
# Blockly requires placeholders to restart at %1 in every message: message0 uses
# args0 with %1, message1 uses args1 with %1 again. A global "%2" in message1
# makes Blockly reject the whole definition with "Message index %2 out of range",
# which silently emptied the block editor's palette.

import re

import pytest

from tgblocks import model
from tgblocks.visual.server import _Handler  # noqa: F401 - import guard


def blocks(lang: str = "ru"):
    return model.blockly_blocks(lang)


def test_every_block_is_well_formed_for_blockly():
    for block in blocks():
        assert block["type"].startswith("tg_")
        assert re.match(r"^#[0-9a-fA-F]{6}$", block["colour"]), block["type"]
        messages = [key for key in block if key.startswith("message")]
        assert messages, block["type"]
        for message in messages:
            index = message[len("message"):]
            args = block.get("args" + index)
            placeholders = re.findall(r"%(\d+)", block[message])
            if not args:
                # A block with no fields is just a caption.
                assert placeholders == [], "{0}.{1}".format(block["type"], message)
                continue
            assert placeholders == ["1"] * len(args), (
                "{0}.{1} = {2!r} with {3} arg(s): placeholders must be %1 per "
                "message".format(block["type"], message, block[message], len(args)))


def test_no_global_placeholder_numbering_sneaks_in():
    for block in blocks():
        for key, value in block.items():
            if key.startswith("message"):
                numbers = [int(item) for item in re.findall(r"%(\d+)", value)]
                assert numbers in ([], [1]), "{0}.{1}: {2!r}".format(
                    block["type"], key, value)


def test_every_action_has_a_block():
    names = {block["type"] for block in blocks()}
    for spec in model.ACTIONS:
        if spec.kind in model.STRUCTURAL_BLOCKS:
            continue
        expected = "tg_" + ("photo" if spec.kind == "send_photo" else spec.kind)
        assert expected in names, expected


def test_blocks_use_the_interface_language():
    russian = {block["type"]: block for block in blocks("ru")}
    english = {block["type"]: block for block in blocks("en")}
    assert russian["tg_send_document"]["message0"].startswith("Документ")
    assert english["tg_send_document"]["message0"].startswith("Document")
    assert english["tg_send_poll"]["message1"].startswith("Options")
    assert russian["tg_send_poll"]["message1"].startswith("Варианты")


def test_field_names_match_what_the_xml_reader_expects():
    # convert.blocks_xml_to_spec reads <field name="PARAM"> in upper case.
    for spec in model.ACTIONS:
        if spec.kind in model.STRUCTURAL_BLOCKS:
            continue
        block = [item for item in blocks()
                 if item["type"] == "tg_" + ("photo" if spec.kind == "send_photo"
                                             else spec.kind)][0]
        expected = {param.name.upper() for param in spec.params}
        found = set()
        for key, value in block.items():
            if key.startswith("args"):
                for arg in value:
                    found.add(arg["name"])
        assert found == expected, spec.kind


def test_the_schema_carries_the_blocks_and_the_language():
    ru = model.schema()
    en = model.schema("en")
    assert ru["lang"] == "ru" and en["lang"] == "en"
    assert len(ru["blocks"]) == len(en["blocks"]) > 20
    assert ru["actions"][0]["label"] != en["actions"][0]["label"]
    # Every label must have an English twin, or the switch would show Russian.
    for action in en["actions"]:
        assert action["label"] == action["label_en"]
    for event in en["events"]:
        assert event["label"] == event["label_en"]
""",
    "tests/test_bots.py": r"""# Behavioural tests: what a user actually sees when the generated bot runs.
#
# These are not string assertions on the emitted code - every test starts the
# generated bot on a fake Telegram, feeds it the JSON of an incoming update and
# checks the API calls that came back. If the generated bot stops answering
# `/start`, or answers with the wrong keyboard, this file fails.

import asyncio

import pytest
from aiogram.methods import (
    AnswerCallbackQuery,
    DeleteMessage,
    SendChatAction,
    SendMessage,
    SendPhoto,
)
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

from botkit import Harness, edited_payload, fast_time, message_payload
from corpus import case_by_name
from tgblocks.dsl import compile_source
from tgblocks.textlang import compile_text


def bot(name: str) -> Harness:
    case = case_by_name(name)
    if case.syntax == "dsl":
        code = compile_source(case.source, name + ".tg")
    else:
        code = compile_text(case.source, name + ".txt")
    return Harness(code, "bot_" + name.replace("-", "_"))


# ------------------------------------------------------------------ the happy path
def test_start_sends_the_text_and_the_inline_keyboard():
    harness = bot("hello")
    harness.command("/start")

    sent = harness.session.first(SendMessage)
    assert sent.text == "Hi! I am your bot."
    assert isinstance(sent.reply_markup, InlineKeyboardMarkup)
    rows = sent.reply_markup.inline_keyboard
    assert [[button.text for button in row] for row in rows] == [["Help"], ["About"]]
    assert [[button.callback_data for button in row] for row in rows] == [["/help"], ["/about"]]


def test_pressing_an_inline_button_runs_the_command_and_closes_the_spinner():
    harness = bot("hello")
    harness.press("/help")

    assert harness.session.texts() == ["Commands: /start, /help, /about"]
    answered = harness.session.first(AnswerCallbackQuery)
    assert answered.callback_query_id == "cb-1"


def test_reply_keyboard_is_a_real_reply_keyboard():
    harness = bot("hello")
    harness.command("/help")

    sent = harness.session.first(SendMessage)
    assert isinstance(sent.reply_markup, ReplyKeyboardMarkup)
    assert [[button.text for button in row] for row in sent.reply_markup.keyboard] == [
        ["/start"],
        ["/help"],
    ]
    assert sent.reply_markup.resize_keyboard is True


def test_text_condition_and_else_branch():
    harness = bot("hello")

    harness.text("hi there")
    assert harness.session.texts() == ["Hello there!"]

    harness.session.reset()
    harness.text("не понял")
    assert harness.session.texts() == ["Not sure what you mean. Try /help."]


# ------------------------------------------------------------------------ events
@pytest.mark.parametrize(
    "kind,expected",
    [
        ("photo", "photo"),
        ("sticker", "sticker"),
        ("voice", "voice"),
        ("video", "video"),
        ("video_note", "round"),
        ("audio", "audio"),
        ("document", "document"),
        ("animation", "gif"),
        ("location", "location"),
        ("contact", "contact"),
        ("poll", "poll"),
    ],
)
def test_every_content_type_reaches_its_handler(kind, expected):
    harness = bot("events")
    harness.content(kind)
    assert harness.session.texts() == [expected]


def test_text_message_wins_over_the_catch_all():
    harness = bot("events")
    harness.text("hello")
    assert harness.session.texts() == ["text"]


def test_unmatched_content_falls_through_to_any():
    # `on any:` is registered last, so a dice message (no handler of its own)
    # must still be answered by the catch-all instead of being ignored.
    harness = bot("events")
    harness.content("dice")
    assert harness.session.texts() == ["fallback"]


def test_new_members_and_left_member_and_edited():
    harness = bot("events")
    harness.ask(
        message_payload(
            None,
            extra={"new_chat_members": [{"id": 11, "is_bot": False, "first_name": "New"}]},
        )
    )
    harness.session.reset()
    harness.ask(
        message_payload(
            None,
            extra={"left_chat_member": {"id": 12, "is_bot": False, "first_name": "Gone"}},
        )
    )
    harness.session.reset()
    harness.ask(edited_payload("changed"))

    assert "edited" in harness.session.texts()


# ----------------------------------------------------------------------- actions
def test_actions_reach_the_right_api_methods(monkeypatch):
    sleeps = fast_time(monkeypatch)
    harness = bot("actions")
    harness.command("/start")

    names = [type(method).__name__ for method in harness.session.methods]
    assert names[0] == "SendChatAction"
    assert harness.session.first(SendChatAction).action == "typing"
    assert sleeps.delays == [2, 0.5]

    messages = harness.session.all(SendMessage)
    assert messages[0].text == 'line one\nline two "quoted"'

    photo = harness.session.first(SendPhoto)
    assert photo.photo == "https://example.com/cat.jpg"
    assert photo.caption == "Котик"
    assert len(harness.session.all(SendPhoto)) == 2

    assert harness.session.all(DeleteMessage)


def test_passing_does_nothing_visible(monkeypatch):
    fast_time(monkeypatch)
    harness = bot("actions")
    harness.command("/start")
    # `pass` must not emit an empty message or crash the handler.
    assert all(isinstance(method, (SendChatAction, SendMessage, SendPhoto, DeleteMessage))
               for method in harness.session.methods)


# -------------------------------------------------------------------- conditions
@pytest.mark.parametrize(
    "text,expected",
    [
        ("точное", "eq"),
        ("стоп", None),
        ("тут цена 100", "has"),
        ("купи хлеб", "starts"),
        ("как дела?", "ends"),
    ],
)
def test_every_condition_operator(text, expected):
    harness = bot("conditions")
    harness.text(text)
    texts = harness.session.texts()
    if expected is None:
        assert texts == [] or expected not in texts
    else:
        assert expected in texts


def test_several_values_mean_any_of_them():
    harness = bot("conditions")
    harness.text("a")
    assert "any of them" in harness.session.texts()
    harness.session.reset()
    harness.text("b")
    assert "any of them" in harness.session.texts()


def test_not_equal_with_several_values_needs_all_of_them():
    harness = bot("conditions")
    harness.text("x")
    assert "neither" not in harness.session.texts()
    harness.text("zzz")
    assert "neither" in harness.session.texts()


def test_nested_conditions():
    harness = bot("nested")
    harness.command("/start")
    # The command itself is `send "outer"` plus a condition on the same message.
    handlers = harness.session.texts()
    assert "outer" in handlers


# --------------------------------------------------------------------- patterns
def test_text_patterns_are_exact_and_case_sensitive():
    harness = bot("patterns")
    harness.text("привет")
    assert harness.session.texts() == ["и тебе привет"]
    harness.session.reset()
    harness.text("Привет")
    # F.text.in_ is exact: a different case must not match.
    assert harness.session.texts() == []
""",
    "tests/test_clear.py": '# Clearing a view clears the bot for all three views.\n#\n# The project store kept the last good text when a canvas was empty ("unfinished\n# canvas"), which is right for a half-built board but wrong for "delete\n# everything": the other views kept showing code the user had removed.\n\nimport json\nimport threading\nimport urllib.request\nfrom http.server import ThreadingHTTPServer\n\nimport pytest\n\nimport tgblocks.visual.server as server\nfrom tgblocks.convert import spec_to_nodes, spec_to_text\nfrom tgblocks.textlang import parse_text\n\nFULL = """token("1:TEST")\n\non.command("/start"):\n    send("Привет!")\n"""\n\n\n@pytest.fixture()\ndef api(tmp_path, monkeypatch):\n    monkeypatch.setattr(server, "STORAGE_DIR", tmp_path / "projects")\n    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server._Handler)\n    httpd.view = "nodes"\n    threading.Thread(target=httpd.serve_forever, daemon=True).start()\n    yield "http://127.0.0.1:{0}".format(httpd.server_address[1])\n    httpd.shutdown()\n    httpd.server_close()\n\n\ndef get(base, path):\n    with urllib.request.urlopen(base + path, timeout=10) as response:\n        return json.loads(response.read().decode("utf-8"))\n\n\ndef post(base, path, payload):\n    body = json.dumps(payload).encode("utf-8")\n    request = urllib.request.Request(base + path, data=body,\n                                     headers={"Content-Type": "application/json"})\n    with urllib.request.urlopen(request, timeout=15) as response:\n        return json.loads(response.read().decode("utf-8"))\n\n\ndef test_an_empty_board_clears_the_bot(api):\n    first = post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})\n    assert first["ok"] and first["rev"] == 1\n\n    # The node editor deletes every block: the board arrives with no nodes.\n    cleared = post(api, "/api/project?name=bot1",\n                   {"baseRev": first["rev"], "nodes": {"nodes": {}, "rootId": None}})\n    assert cleared["ok"] is True\n    assert cleared["text"] == ""\n    assert cleared["rev"] == first["rev"] + 1, "должна появиться новая ревизия"\n\n    # The other views poll the revision and read the empty text.\n    stored = get(api, "/api/project?name=bot1")\n    assert stored["text"] == ""\n    assert stored["rev"] == cleared["rev"]\n\n\ndef test_empty_text_from_the_text_view_also_clears(api):\n    first = post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})\n    cleared = post(api, "/api/project?name=bot1", {"baseRev": first["rev"], "text": ""})\n    assert cleared["ok"] is True and cleared["text"] == ""\n    assert get(api, "/api/project?name=bot1")["text"] == ""\n\n\ndef test_clearing_twice_does_not_bump_the_revision(api):\n    post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})\n    first = post(api, "/api/project?name=bot1", {"baseRev": 1, "text": ""})\n    second = post(api, "/api/project?name=bot1",\n                  {"baseRev": first["rev"], "nodes": {"nodes": {}}})\n    assert second["ok"] is True\n    assert second["rev"] == first["rev"]\n    assert second["text"] == ""\n\n\ndef test_a_half_built_board_still_keeps_the_last_good_text(api):\n    # A canvas with a bot but no events is not "delete everything": the bot text\n    # must survive so the user does not lose it while dragging blocks around.\n    first = post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})\n    draft = {"nodes": {"b1": {"id": "b1", "type": "bot", "props": {"token": ""},\n                              "parent": None, "children": [], "x": 0, "y": 0}},\n             "counter": 1, "rootId": "b1"}\n    reply = post(api, "/api/project?name=bot1", {"baseRev": first["rev"], "nodes": draft})\n    assert reply["ok"] is True and reply.get("incomplete") is True\n    stored = get(api, "/api/project?name=bot1")\n    assert stored["text"] == _canonical(FULL)\n    assert stored["rev"] == first["rev"]\n\n\ndef test_reopening_the_view_after_clearing_starts_from_nothing(api):\n    post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})\n    post(api, "/api/project?name=bot1", {"baseRev": 1, "text": ""})\n    stored = get(api, "/api/project?name=bot1")\n    # The document is empty and no draft survives, so every editor opens blank:\n    # the page draws the empty canvas itself instead of asking for a conversion.\n    assert stored["text"] == ""\n    assert stored["draft"] is None\n    assert stored["layout"] == {} or isinstance(stored["layout"], dict)\n\n\ndef _canonical(text: str) -> str:\n    return spec_to_text(parse_text(text, "t"))\n',
    "tests/test_cli.py": r"""# CLI tests: the command line is the part people script, so it is tested through
# main() rather than by hand. The token handling is a security property now:
# `compile` must not write the secret into the artefact unless asked.

import os

import pytest

from tgblocks.cli import main

BOT = 'bot token "123456:SECRET"\n\non /start:\n    send "hi"\n'


@pytest.fixture(autouse=True)
def no_leaked_token():
    # `run` exports the token into the environment on purpose; keep that from
    # leaking into the next test.
    before = os.environ.pop("TG_BOT_TOKEN", None)
    yield
    os.environ.pop("TG_BOT_TOKEN", None)
    if before is not None:
        os.environ["TG_BOT_TOKEN"] = before


@pytest.fixture()
def bot_file(tmp_path):
    path = tmp_path / "bot.tg"
    path.write_text(BOT, encoding="utf-8")
    return path


def run(argv, capsys):
    code = main(argv)
    out, err = capsys.readouterr()
    return code, out, err


def test_version(capsys):
    with pytest.raises(SystemExit) as info:
        main(["--version"])
    assert info.value.code == 0


def test_flags_without_a_subcommand_mean_the_editor(monkeypatch):
    seen = {}

    def fake_visual(args):
        seen["port"] = args.port
        seen["browser"] = args.no_browser
        return 0

    monkeypatch.setattr("tgblocks.cli.cmd_visual", fake_visual)
    assert main(["--port", "9000", "--no-browser"]) == 0
    assert seen["port"] == 9000
    assert seen["browser"] is True


def test_bare_command_opens_the_editor(monkeypatch):
    # `tgblocks` with no arguments must start the visual editor: that is the
    # command people type, and it has to work from any folder.
    seen = {}

    def fake_visual(args):
        seen["view"] = args.view
        seen["port"] = args.port
        return 0

    monkeypatch.setattr("tgblocks.cli.cmd_visual", fake_visual)
    assert main([]) == 0
    assert seen["view"] == "nodes"
    assert seen["port"] == 8765


def test_help_flag_still_prints_the_usage(capsys):
    with pytest.raises(SystemExit) as info:
        main(["--help"])
    assert info.value.code == 0
    out = capsys.readouterr().out
    assert "tgblocks" in out


def test_a_bot_file_runs_without_a_subcommand(bot_file, monkeypatch):
    seen = {}

    def fake_run(args):
        seen["file"] = args.file
        seen["dry"] = args.dry_run
        return 0

    monkeypatch.setattr("tgblocks.cli.cmd_run", fake_run)
    assert main([str(bot_file), "--dry-run"]) == 0
    assert seen["file"] == str(bot_file)
    assert seen["dry"] is True


def test_an_unknown_word_is_a_normal_argument_error(capsys):
    with pytest.raises(SystemExit) as info:
        main(["frobnicate"])
    assert info.value.code == 2


def test_compile_to_stdout_keeps_the_token_out(bot_file, capsys):
    code, out, err = run(["compile", str(bot_file)], capsys)
    assert code == 0
    assert "SECRET" not in out
    assert 'os.environ.get("TG_BOT_TOKEN", "")' in out
    assert "note: the token is not written" in err


def test_compile_embeds_the_token_on_request(bot_file, capsys):
    code, out, _ = run(["compile", str(bot_file), "--embed-token"], capsys)
    assert code == 0
    assert '"123456:SECRET"' in out


def test_compile_writes_a_file(bot_file, tmp_path, capsys):
    target = tmp_path / "out" / "bot.py"
    code, out, _ = run(["compile", str(bot_file), "-o", str(target)], capsys)
    assert code == 0
    assert target.exists()
    assert "wrote" in out
    assert "SECRET" not in target.read_text(encoding="utf-8")


def test_check_reports_the_handlers(bot_file, capsys):
    code, out, _ = run(["check", str(bot_file)], capsys)
    assert code == 0
    assert out.startswith("OK ")
    assert "/start" in out


def test_check_summary_distinguishes_states_and_filters(tmp_path, capsys):
    path = tmp_path / "mixed.tg"
    path.write_text(
        'bot token "1:x"\n\n'
        "state order\n\n"
        'on /start:\n    set_state order\n'
        'on state order:\n    send "ok"\n'
        'on message chat=supergroup:\n    send "g"\n'
        'on callback "/buy":\n    send "b"\n',
        encoding="utf-8",
    )
    code, out, _ = run(["check", str(path)], capsys)
    assert code == 0
    assert "state[order]" in out
    assert "text[chat=supergroup]" in out
    assert "callback[/buy]" in out


def test_dry_run_prints_code_without_a_token(bot_file, capsys, monkeypatch):
    monkeypatch.delenv("TG_BOT_TOKEN", raising=False)
    code, out, _ = run(["run", str(bot_file), "--dry-run"], capsys)
    assert code == 0
    assert "async def" in out
    assert "SECRET" not in out


def test_run_without_a_token_fails_cleanly(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("TG_BOT_TOKEN", raising=False)
    path = tmp_path / "placeholder.tg"
    path.write_text('bot token "PASTE_YOUR_TOKEN"\n\non /start:\n    send "hi"\n',
                    encoding="utf-8")
    code, _, err = run(["run", str(path)], capsys)
    assert code == 2
    assert "no bot token" in err


def test_syntax_error_is_reported_with_a_position(tmp_path, capsys):
    path = tmp_path / "bad.tg"
    path.write_text('bot token "1:x"\n\non /start:\n    send Hi!\n', encoding="utf-8")
    code, _, err = run(["check", str(path)], capsys)
    assert code == 1
    assert "bad.tg:4:5" in err
    assert "hint:" in err


def test_missing_file_is_an_error(capsys):
    code, _, err = run(["check", "nope.tg"], capsys)
    assert code == 2
    assert "not found" in err


def test_run_uses_the_token_from_the_dsl_file(bot_file, capsys, monkeypatch):
    # The generated code carries no token, so `run` must hand it over in the
    # environment - and it must not leak into the printed code.
    monkeypatch.delenv("TG_BOT_TOKEN", raising=False)
    captured = {}

    def fake_run_path(path, run_name=None):
        captured["path"] = path
        captured["env"] = os.environ.get("TG_BOT_TOKEN")
        raise KeyboardInterrupt

    monkeypatch.setattr("tgblocks.cli.runpy.run_path", fake_run_path)
    monkeypatch.setattr("tgblocks.cli.generate", lambda spec, **kw: 'print("stub")')
    code = main(["run", str(bot_file)])
    assert code == 130  # Ctrl+C is a normal stop, not a failure
    assert captured["env"] == "123456:SECRET"
""",
    "tests/test_dice.py": r"""# Conditions on the interactive emoji: `when dice == 6`.
#
# The value Telegram reports (message.dice.value) is a number, so the comparison
# is numeric and the two syntaxes agree.

import pytest

from botkit import Harness, message_payload
from tgblocks.convert import board_to_text, blocks_xml_to_spec, spec_to_blocks_xml, \
    spec_to_nodes, spec_to_text
from tgblocks.dsl import compile_source
from tgblocks.dsl.parser import DSLParseError, parse
from tgblocks.textlang import parse_text

DSL = (
    'bot token "1:x"\n\n'
    "on dice:\n"
    "    when dice == 6:\n"
    '        send "six"\n'
    "    when dice != 6:\n"
    '        send "not six"\n'
)


def roll(harness, value):
    return harness.ask(message_payload(None, extra={"dice": {"emoji": "🎲", "value": value}}))


def test_dsl_parses_a_dice_condition():
    spec = parse(DSL)
    conditions = [node.condition for node in spec.handlers[0].actions
                  if hasattr(node, "condition")]
    assert [(item.source, item.op, item.value) for item in conditions] == [
        ("dice", "==", "6"), ("dice", "!=", "6")]


def test_the_generated_bot_compares_the_rolled_number():
    harness = Harness(compile_source(DSL), "dice_bot")
    roll(harness, 6)
    assert harness.session.texts() == ["six"]
    harness.session.reset()
    roll(harness, 2)
    assert harness.session.texts() == ["not six"]


def test_text_syntax_takes_the_dice_source():
    spec = parse_text('token("1:x")\n\non.dice():\n    when("dice", "==", 6):\n'
                      '        send("six")\n')
    condition = spec.handlers[0].actions[0].condition
    assert (condition.source, condition.op, condition.value) == ("dice", "==", "6")

    code = compile_source('bot token "1:x"\n\non dice:\n    when dice == 6:\n'
                          '        send "six"\n')
    assert "dice_value(event) == 6" in code
    assert "def dice_value(event) -> int:" in code


def test_only_equality_makes_sense_for_an_emoji():
    with pytest.raises(DSLParseError) as info:
        parse('bot token "1:x"\n\non dice:\n    when dice contains "6":\n        send "x"\n')
    assert "==" in info.value.message or "только" in info.value.message


def test_a_non_number_is_refused():
    with pytest.raises(DSLParseError):
        parse('bot token "1:x"\n\non dice:\n    when dice == "шесть":\n        send "x"\n')


def test_the_condition_survives_every_editor():
    spec = parse(DSL)
    canonical = spec_to_text(spec)
    assert 'when("dice", "==", 6)' in canonical
    assert board_to_text(spec_to_nodes(spec)) == canonical

    xml = spec_to_blocks_xml(spec)
    assert '<field name="SOURCE">dice</field>' in xml
    assert spec_to_text(blocks_xml_to_spec(xml)) == canonical
""",
    "tests/test_dsl.py": r"""# Tests for the DSL parser, the text syntax and the aiogram generator.

import pytest

from tgblocks.dsl import compile_source
from tgblocks.dsl.parser import DSLParseError, parse
from tgblocks.textlang import compile_text, parse_text

DSL = '''
bot token "123456:TEST"
bot name "Test bot"

on /start:
    send "Hi"
    buttons:
        "Help" -> /help
        "Site" -> url "https://example.com"

on photo:
    send "nice"

on message:
    when text contains "ping":
        send "pong"
    else:
        send "?"
'''

TEXT = '''
token("123456:TEST")
name("Test bot")

on.command("/start"):
    send("Hi")
    button("Help", "/help")
    button("Site", url="https://example.com")

on.message(TEXT, "ping", "Ping"):
    send("pong")

on.message(PHOTO):
    send("nice")
'''


def test_dsl_parses_token_and_handlers():
    bot = parse(DSL)
    assert bot.token == "123456:TEST"
    assert bot.name == "Test bot"
    assert [handler.kind for handler in bot.handlers] == ["command", "photo", "text"]


def test_dsl_codegen_is_readable_aiogram():
    code = compile_source(DSL)
    assert '@dp.message(Command("start"))' in code
    assert '@dp.callback_query(F.data == "/start")' in code
    assert 'inline(("Help", "/help", "command"), ("Site", "https://example.com", "url"))' in code
    assert "@dp.message(F.photo)" in code
    assert "await dp.start_polling(bot)" in code
    assert "Bot(token=BOT_TOKEN, session=session)" in code


def test_dsl_missing_token_reports_first_line():
    with pytest.raises(DSLParseError) as info:
        parse('on /start:\n    send "hi"\n')
    assert info.value.line == 1
    assert "token" in info.value.message


def test_dsl_unknown_statement_has_line_number():
    with pytest.raises(DSLParseError) as info:
        parse('bot token "1:x"\n\non /start:\n    dance\n')
    assert info.value.line == 4
    assert "dance" in info.value.message


def test_dsl_buttons_without_send_is_an_error():
    with pytest.raises(DSLParseError) as info:
        compile_source('bot token "1:x"\non /start:\n    buttons:\n        "A" -> /a\n')
    assert "send" in info.value.message


def test_text_parses_events_and_patterns():
    bot = parse_text(TEXT)
    assert bot.token == "123456:TEST"
    assert [(handler.kind, handler.patterns) for handler in bot.handlers] == [
        ("command", ()),
        ("text", ("ping", "Ping")),
        ("photo", ()),
    ]


def test_text_compiles_like_the_dsl():
    code = compile_text(TEXT)
    assert '@dp.message(Command("start"))' in code
    assert 'inline(("Help", "/help", "command"), ("Site", "https://example.com", "url"))' in code
    assert 'F.text.in_(("ping", "Ping"))' in code
    assert "@dp.message(F.photo)" in code


def test_text_requires_colon_after_event():
    with pytest.raises(DSLParseError) as info:
        parse_text('token("1")\non.command("/start")\n    send("a")\n')
    assert ":" in info.value.message
    assert info.value.line == 2


def test_text_button_must_follow_send():
    with pytest.raises(DSLParseError) as info:
        parse_text('token("1")\non.command("/start"):\n    button("a", "/b")\n')
    assert "send" in info.value.message


def test_text_when_and_otherwise():
    code = compile_text(
        'token("1")\non.message(TEXT, ""):\n'
        '    when("contains", "hi"):\n'
        '        send("hello")\n'
        '    otherwise():\n'
        '        send("?")\n'
    )
    assert 'if "hi" in text_of(event).lower():' in code
    assert "else:" in code
""",
    "tests/test_examples.py": r"""# Every example in the repository must compile, import into aiogram and answer
# the messages it advertises. Examples rot faster than code, so they live under
# the same checks as the tests themselves.

import pathlib

import pytest

from botkit import Harness, fast_time
from tgblocks.convert import spec_to_blocks_xml, spec_to_nodes, spec_to_text, board_to_spec
from tgblocks.dsl import compile_source
from tgblocks.dsl.parser import parse_file

EXAMPLES = pathlib.Path(__file__).resolve().parents[1] / "examples"


def examples():
    return sorted(EXAMPLES.glob("*.tg"))


def test_there_are_examples():
    assert examples(), "the examples directory is empty"


@pytest.mark.parametrize("path", examples(), ids=lambda item: item.name)
def test_example_compiles_and_imports(path):
    pytest.importorskip("aiogram")
    source = path.read_text(encoding="utf-8")
    code = compile_source(source, path.name)
    harness = Harness(code, "example_" + path.stem.replace("-", "_"))
    assert harness.dp is not None
    # A bot from the examples must actually answer /start.
    harness.command("/start")
    assert harness.session.methods, "the example bot answered nothing to /start"


@pytest.mark.parametrize("path", examples(), ids=lambda item: item.name)
def test_example_survives_all_three_editors(path):
    spec = parse_file(str(path))
    canonical = spec_to_text(spec)
    board = spec_to_nodes(spec)
    assert spec_to_text(board_to_spec(board)) == canonical
    xml = spec_to_blocks_xml(spec)
    assert 'type="tg_bot"' in xml


def test_the_full_example_uses_the_new_features():
    text = (EXAMPLES / "full.tg").read_text(encoding="utf-8")
    for feature in ("set_state", "clear_state", "send_poll", "send_document",
                    "answer_callback", "edit_text", "ban_user", "chat=supergroup",
                    "regex=", "log "):
        assert feature in text, feature


def test_the_full_example_walks_the_order_dialogue():
    source = (EXAMPLES / "full.tg").read_text(encoding="utf-8")
    harness = Harness(compile_source(source, "full.tg"), "example_full")
    harness.command("/order")
    assert harness.session.texts() == ["Что заказать?"]
    harness.session.reset()
    harness.text("две пиццы")
    assert harness.session.texts() == ["Записал. Теперь телефон?"]
    harness.session.reset()
    harness.text("+100")
    assert harness.session.texts() == ["Готово! Заказ принят."]


def test_the_full_example_answers_its_menu_buttons():
    source = (EXAMPLES / "full.tg").read_text(encoding="utf-8")
    harness = Harness(compile_source(source, "full.tg"), "example_full_buttons")
    harness.press("/buy")
    assert "Покупаем!" in harness.session.texts()


def test_the_full_example_media_commands(monkeypatch):
    fast_time(monkeypatch)
    source = (EXAMPLES / "full.tg").read_text(encoding="utf-8")
    harness = Harness(compile_source(source, "full.tg"), "example_full_media")
    for command in ("/photo", "/doc", "/poll", "/where", "/phone"):
        harness.session.reset()
        harness.command(command)
        assert harness.session.methods, command
""",
    "tests/test_features.py": r"""# End-to-end tests for the aiogram features added on top of the first release:
# media, edits, callbacks, chat actions, the dialogue steps and the filters.
#
# Each test compiles a real bot from the DSL or the text syntax, runs it on the
# fake Telegram from botkit and checks the API calls a user would cause.

import asyncio

import pytest
from aiogram.methods import (
    AnswerCallbackQuery,
    AnswerInlineQuery,
    BanChatMember,
    DeleteMessage,
    EditMessageText,
    PinChatMessage,
    RestrictChatMember,
    SendContact,
    SendDice,
    SendDocument,
    SendLocation,
    SendMessage,
    SendPoll,
    SendSticker,
    SendVideo,
    SendVoice,
)

from botkit import CONTENT, Harness, callback_payload, fast_time, message_payload
from tgblocks.dsl import compile_source


def bot(dsl: str, name: str = "features") -> Harness:
    source = 'bot token "1:feature"\n\n' + dsl.lstrip("\n")
    return Harness(compile_source(source, name + ".tg"), "bot_" + name)


# ---------------------------------------------------------------------- media
@pytest.mark.parametrize(
    "action,method,with_caption",
    [
        ("send_document", SendDocument, True),
        ("send_video", SendVideo, True),
        ("send_voice", SendVoice, True),
        ("send_sticker", SendSticker, False),
    ],
)
def test_media_actions_reach_telegram(action, method, with_caption):
    caption = ' "подпись"' if with_caption else ""
    harness = bot('on /send:\n    %s "https://example.com/file"%s\n' % (action, caption))
    harness.command("/send")
    sent = harness.session.first(method)
    assert sent.chat_id == 42


def test_media_without_a_caption_is_allowed():
    harness = bot('on /send:\n    send_document "https://example.com/file"\n')
    harness.command("/send")
    assert harness.session.first(SendDocument).caption is None


def test_location_contact_dice_and_poll():
    harness = bot(
        "on /where:\n"
        '    send_location 55.75 37.61\n'
        "on /phone:\n"
        '    send_contact "+100" "Tester"\n'
        "on /dice:\n"
        '    send_dice "🎲"\n'
        "on /poll:\n"
        '    send_poll "Чай или кофе?" "Чай" "Кофе"\n'
    )
    harness.command("/where")
    location = harness.session.first(SendLocation)
    assert (location.latitude, location.longitude) == (55.75, 37.61)

    harness.session.reset()
    harness.command("/phone")
    contact = harness.session.first(SendContact)
    assert contact.phone_number == "+100" and contact.first_name == "Tester"

    harness.session.reset()
    harness.command("/dice")
    assert harness.session.first(SendDice).emoji == "🎲"

    harness.session.reset()
    harness.command("/poll")
    poll = harness.session.first(SendPoll)
    assert poll.question == "Чай или кофе?"
    assert [option.text for option in poll.options] == ["Чай", "Кофе"]


def test_media_from_an_inline_button_answers_the_callback_too():
    harness = bot(
        "on /menu:\n"
        '    send "меню"\n'
        "    buttons:\n"
        '        "Документ" -> /doc\n'
        "on /doc:\n"
        '    send_document "https://example.com/file"\n'
    )
    harness.press("/doc")
    assert harness.session.first(SendDocument)
    assert harness.session.first(AnswerCallbackQuery)


# ---------------------------------------------------------------------- edits
def test_edit_text_rewrites_the_message_of_the_button():
    harness = bot(
        "on /start:\n"
        '    send "меню"\n'
        "    buttons:\n"
        '        "Готово" -> /done\n'
        "on /done:\n"
        '    edit_text "Готово!"\n'
    )
    harness.press("/done")
    assert harness.session.first(EditMessageText).text == "Готово!"


def test_answer_callback_shows_a_toast_or_an_alert():
    harness = bot(
        "on /start:\n"
        '    send "меню"\n'
        "    buttons:\n"
        '        "A" -> /a\n'
        "on /a:\n"
        '    answer_callback "Готово"\n'
        "on /b:\n"
        '    answer_callback "Ошибка" alert\n'
    )
    harness.press("/a")
    toast = harness.session.first(AnswerCallbackQuery)
    assert toast.text == "Готово" and toast.show_alert is None

    harness.session.reset()
    harness.press("/b")
    alert = harness.session.first(AnswerCallbackQuery)
    assert alert.show_alert is True


# ---------------------------------------------------------------- moderation
def test_pin_and_ban_and_mute():
    harness = bot(
        "on /pin:\n"
        "    pin\n"
        "on /pinquiet:\n"
        "    pin silent\n"
        "on /ban:\n"
        "    ban_user\n"
        "on /ban42:\n"
        "    ban_user 42\n"
        "on /mute:\n"
        "    mute_user 42 30\n"
    )
    harness.command("/pin", chat_id=-100)
    pinned = harness.session.first(PinChatMessage)
    assert pinned.chat_id == -100 and pinned.message_id == 1

    harness.session.reset()
    harness.command("/ban")
    banned = harness.session.first(BanChatMember)
    assert banned.user_id == 7  # the sender of the message

    harness.session.reset()
    harness.command("/ban42")
    assert harness.session.first(BanChatMember).user_id == 42

    harness.session.reset()
    harness.command("/mute")
    muted = harness.session.first(RestrictChatMember)
    assert muted.user_id == 42
    assert muted.permissions.can_send_messages is False


# ------------------------------------------------------------------- dialogues
def test_dialogue_steps_walk_the_user_through_the_form():
    harness = bot(
        "state order\n"
        "state phone\n"
        "\n"
        "on /order:\n"
        '    send "Что заказать?"\n'
        "    set_state order\n"
        "\n"
        "on state order:\n"
        '    send "Записал заказ"\n'
        "    set_state phone\n"
        "\n"
        "on state phone:\n"
        '    send "Телефон записан"\n'
        "    clear_state\n"
    )
    harness.command("/order")
    assert harness.session.texts() == ["Что заказать?"]

    # The next message lands in the "order" step, not in a generic handler.
    harness.session.reset()
    harness.text("две пиццы")
    assert harness.session.texts() == ["Записал заказ"]

    harness.session.reset()
    harness.text("+100")
    assert harness.session.texts() == ["Телефон записан"]

    # After clear_state the step handler no longer matches.
    harness.session.reset()
    harness.text("ещё что-то")
    assert harness.session.texts() == []


def test_state_handler_survives_a_callback():
    harness = bot(
        "state step\n"
        "on /go:\n"
        "    set_state step\n"
        "on state step:\n"
        '    send "внутри шага"\n'
    )
    harness.command("/go")
    harness.session.reset()
    harness.text("что угодно")
    assert harness.session.texts() == ["внутри шага"]


# --------------------------------------------------------------------- events
def test_callback_event_with_exact_data():
    harness = bot(
        'on /start:\n'
        '    send "меню"\n'
        "on callback \"/buy\":\n"
        '    send "покупаем"\n'
    )
    harness.press("/buy")
    assert harness.session.texts() == ["покупаем"]


def test_callback_event_without_data_catches_every_button():
    harness = bot(
        'on callback:\n'
        '    send "кнопка"\n'
    )
    harness.press("anything")
    assert harness.session.texts() == ["кнопка"]


def test_chat_filter_ignores_other_chats():
    # Telegram reports "private", "group", "supergroup" and "channel"; a filter
    # for one of them must not fire in the others.
    harness = bot(
        "on message chat=supergroup:\n"
        '    send "только в супергруппе"\n'
    )
    harness.text("привет", chat_id=42)                     # private
    assert harness.session.texts() == []
    harness.text("привет", chat_id=-100, chat_kind="group")  # basic group
    assert harness.session.texts() == []
    harness.text("привет", chat_id=-100)                   # supergroup
    assert harness.session.texts() == ["только в супергруппе"]


def test_from_user_filter():
    harness = bot(
        "on message from_user=99:\n"
        '    send "для одного"\n'
    )
    harness.text("привет", user_id=7)
    assert harness.session.texts() == []
    harness.text("привет", user_id=99)
    assert harness.session.texts() == ["для одного"]


def test_regex_filter():
    harness = bot(
        'on message regex="^[0-9]+$":\n'
        '    send "число"\n'
    )
    harness.text("привет")
    assert harness.session.texts() == []
    harness.text("12345")
    assert harness.session.texts() == ["число"]


def test_inline_mode_answers_with_an_article():
    harness = bot(
        "on inline_query:\n"
        '    inline_result "Заголовок" "Текст ответа" "Описание"\n'
    )
    harness.ask({
        "update_id": 900,
        "inline_query": {
            "id": "iq-1",
            "from": {"id": 7, "is_bot": False, "first_name": "Tester"},
            "query": "q",
            "offset": "",
        },
    })
    answer = harness.session.first(AnswerInlineQuery)
    assert answer.results[0].title == "Заголовок"


def test_chat_member_event_can_greet_the_group():
    harness = bot(
        "on chat_member:\n"
        '    send "новый участник"\n'
    )
    harness.ask({
        "update_id": 901,
        "chat_member": {
            "chat": {"id": -100, "type": "supergroup", "title": "G"},
            "from": {"id": 7, "is_bot": False, "first_name": "Tester"},
            "date": 1700000000,
            "old_chat_member": {"status": "left", "user": {"id": 8, "is_bot": False,
                                                           "first_name": "New"}},
            "new_chat_member": {"status": "member", "user": {"id": 8, "is_bot": False,
                                                             "first_name": "New"}},
        },
    })
    sent = harness.session.first(SendMessage)
    assert sent.chat_id == -100 and sent.text == "новый участник"


def test_log_writes_to_the_process_log(caplog):
    import logging

    caplog.set_level(logging.INFO)
    harness = bot(
        "on /log:\n"
        '    log "пользователь нажал /log"\n'
    )
    harness.command("/log")
    assert any("нажал" in record.getMessage() for record in caplog.records)


# --------------------------------------------------------------------- webhook
def test_webhook_bot_builds_a_real_aiohttp_app():
    code = compile_source(
        'bot token "1:x"\nbot webhook "https://example.com/hook"\n'
        'bot webhook_path "/hook"\n\non /start:\n    send "hi"\n',
        "webhook.tg",
    )
    assert "WEBHOOK_URL" in code and "SimpleRequestHandler" in code
    module = __import__("types").ModuleType("webhook_bot")
    module.__file__ = "<generated>"
    exec(compile(code, "<generated>", "exec"), module.__dict__)
    assert module.WEBHOOK_PATH == "/hook"
    assert callable(module.serve_webhook)

    # The aiohttp integration accepts exactly the arguments the generated code
    # passes; a wrong keyword here would only fail on a live deploy.
    from aiogram import Bot
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler
    from botkit import FakeSession

    bot_instance = Bot(token="1:TEST", session=FakeSession())
    handler = SimpleRequestHandler(dispatcher=module.dp, bot=bot_instance,
                                   secret_token=None)
    assert handler is not None


def test_polling_bot_has_no_webhook_code():
    code = compile_source('bot token "1:x"\n\non /start:\n    send "hi"\n', "poll.tg")
    assert "WEBHOOK_URL" not in code
    assert "start_polling" in code
""",
    "tests/test_filters.py": r"""# Filters on generated handlers: aiogram checks each filter separately, and a
# Command filter cannot be joined with a magic filter by "&".
#
# `Command("start") & (F.chat.type == "private")` looks reasonable and fails at
# runtime with "unsupported operand type(s) for &: 'Command' and 'bool'". These
# tests run the generated bot on a fake Telegram for every filter combination.

import pytest

from botkit import Harness, message_payload
from tgblocks.dsl import compile_source
from tgblocks.textlang import compile_text

CASES = {
    "command-chat": ('bot token "1:x"\n\non /start chat=private:\n    send "hi"\n'),
    "command-from-user": ('bot token "1:x"\n\non /start from_user=7:\n    send "hi"\n'),
    "command-regex": ('bot token "1:x"\n\non /start regex="^/":\n    send "hi"\n'),
    "command-chat-from-user": (
        'bot token "1:x"\n\non /start chat=private from_user=7:\n    send "hi"\n'
    ),
    "message-chat": ('bot token "1:x"\n\non message chat=supergroup:\n    send "hi"\n'),
    "message-regex": (
        'bot token "1:x"\n\non message regex="^[0-9]+$":\n    send "hi"\n'
    ),
    "message-patterns-chat": (
        'bot token "1:x"\n\non message "a", "b" chat=private:\n    send "hi"\n'
    ),
    "callback-data": ('bot token "1:x"\n\non callback "/buy":\n    send "hi"\n'),
    "state": (
        'bot token "1:x"\n\nstate s\non /go:\n    set_state s\n'
        'on state s:\n    send "hi"\n'
    ),
    "text-command-chat": (
        'token("1:x")\n\non.command("/start", chat="private"):\n    send("hi")\n'
    ),
}


def build(source: str) -> str:
    if source.startswith('token("'):
        return compile_text(source, "case.txt")
    return compile_source(source, "case.tg")


@pytest.mark.parametrize("name", sorted(CASES), ids=sorted(CASES))
def test_filtered_handlers_run_without_type_errors(name, caplog):
    import logging

    caplog.set_level(logging.ERROR, logger="aiogram.event")
    harness = Harness(build(CASES[name]), "filters_" + name.replace("-", "_"))
    # aiogram logs a filter that raises instead of propagating it, so the check
    # is on the log: no "Cause exception" lines for a normal update.
    harness.command("/start")
    harness.text("a")
    failures = [record.getMessage() for record in caplog.records
                if "Cause exception" in record.getMessage()]
    assert failures == [], failures


def test_each_filter_is_a_separate_argument():
    code = compile_source(CASES["command-chat"])
    assert '@dp.message(Command("start"), F.chat.type == "private")' in code
    assert " & " not in code.split("async def main")[0].split("dp = Dispatcher")[1]


def test_command_filter_still_matches_and_respects_the_chat():
    harness = Harness(build(CASES["command-chat"]), "filters_chat")

    harness.command("/start", chat_id=42)          # private
    assert harness.session.texts() == ["hi"]

    harness.session.reset()
    harness.command("/start", chat_id=-100)        # supergroup
    assert harness.session.texts() == []


def test_from_user_filter_is_enforced():
    harness = Harness(build(CASES["command-from-user"]), "filters_from_user")

    harness.command("/start", user_id=7)
    assert harness.session.texts() == ["hi"]

    harness.session.reset()
    harness.ask(message_payload("/start", user_id=8))
    assert harness.session.texts() == []


def test_callback_event_without_a_command_still_compiles_filters():
    # This used to emit F.data == "..." without importing F.
    code = build(CASES["callback-data"])
    assert "from aiogram import Bot, Dispatcher, F" in code
    harness = Harness(code, "filters_callback")
    harness.press("/buy")
    assert harness.session.texts() == ["hi"]
""",
    "tests/test_golden.py": r"""# Golden tests: the generated code is the product, so it is pinned byte for byte.
#
# On top of comparing with tests/golden/, every case must also survive two harder
# checks: it must be valid Python (ast.parse) and it must import inside the real
# aiogram package - that is what catches a wrong filter name or a missing type,
# not the string assertions scattered in the other test modules.
#
# Regenerate the goldens on purpose (after reviewing the diff!):
#     python -m pytest tests/test_golden.py --update-golden

import ast
import importlib
import os
import sys
import types

import pytest

from corpus import CORPUS
from tgblocks.dsl import compile_source
from tgblocks.textlang import compile_text

GOLDEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden")


def generate(case) -> str:
    if case.syntax == "dsl":
        return compile_source(case.source, case.name + ".tg")
    return compile_text(case.source, case.name + ".txt")


def golden_path(case) -> str:
    return os.path.join(GOLDEN_DIR, case.name + ".py")


def import_generated(code: str, name: str):
    # Execute the generated module the way `python bot.py` would, minus __main__:
    # importing it registers every handler on a real aiogram Dispatcher.
    module = types.ModuleType(name)
    module.__file__ = "<generated:" + name + ">"
    sys.modules[name] = module
    try:
        exec(compile(code, module.__file__, "exec"), module.__dict__)
    finally:
        sys.modules.pop(name, None)
    return module


@pytest.mark.parametrize("case", CORPUS, ids=[case.name for case in CORPUS])
def test_generated_code_is_valid_python(case):
    ast.parse(generate(case), case.name + ".py")


@pytest.mark.parametrize("case", CORPUS, ids=[case.name for case in CORPUS])
def test_generated_code_imports_into_aiogram(case):
    pytest.importorskip("aiogram")
    module = import_generated(generate(case), "tgblocks_golden_" + case.name.replace("-", "_"))
    assert module.BOT_TOKEN
    assert module.dp is not None
    handlers = (
        len(module.dp.message.handlers)
        + len(module.dp.callback_query.handlers)
        + len(module.dp.edited_message.handlers)
    )
    assert handlers >= 1


@pytest.mark.parametrize("case", CORPUS, ids=[case.name for case in CORPUS])
def test_generated_code_matches_golden(case):
    code = generate(case)
    if "--update-golden" in sys.argv or os.environ.get("UPDATE_GOLDEN"):
        os.makedirs(GOLDEN_DIR, exist_ok=True)
        with open(golden_path(case), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(code)
        return
    assert os.path.exists(golden_path(case)), (
        "no golden file for {0}; run with --update-golden".format(case.name)
    )
    with open(golden_path(case), "r", encoding="utf-8", newline="") as handle:
        expected = handle.read().replace("\r\n", "\n")
    assert code == expected, (
        "generated code for {0} changed; review the diff, then rerun with "
        "--update-golden".format(case.name)
    )
""",
    "tests/test_hidden_filters.py": r"""# The event panel shows the four filters that matter; the two that a `when`
# condition covers are hidden. They still parse, compile and convert, so an old
# bot that uses them keeps working and is not silently changed.

from tgblocks import model
from tgblocks.convert import (
    blocks_xml_to_spec, board_to_text, spec_to_blocks_xml, spec_to_nodes, spec_to_text,
)
from tgblocks.dsl import compile_source
from tgblocks.dsl.parser import parse
from tgblocks.textlang import compile_text, parse_text


def event_params(kind: str, lang: str = "ru"):
    for event in model.schema(lang)["events"]:
        if event["kind"] == kind:
            return {param["name"]: param for param in event["params"]}
    raise AssertionError(kind)


def test_patterns_are_hidden_in_the_message_event():
    assert event_params("text")["patterns"]["hidden"] is True


def test_the_regex_filter_is_hidden_everywhere():
    # Events that carry a text body get the regex filter; those that do not never
    # had one.
    for kind in ("text", "command"):
        assert event_params(kind)["regex"]["hidden"] is True, kind
    schema_filters = {param["name"]: param for param in model.schema()["filters"]}
    assert schema_filters["regex"]["hidden"] is True
    assert schema_filters["chat"]["hidden"] is False
    assert schema_filters["from_user"]["hidden"] is False


def test_the_visible_filters_are_still_offered():
    for kind in ("text", "photo", "command"):
        params = event_params(kind)
        assert params["chat"]["hidden"] is False
        if "from_user" in params:
            assert params["from_user"]["hidden"] is False


def test_blockly_does_not_offer_a_field_for_a_hidden_filter():
    for block in model.blockly_blocks():
        for key, value in block.items():
            if not key.startswith("args"):
                continue
            for arg in value:
                assert arg["name"] not in {"REGEX", "PATTERNS"}, block["type"]


def test_an_old_bot_with_a_regex_filter_still_compiles():
    source = 'bot token "1:x"\n\non message regex="^[0-9]+$":\n    send "цифры"\n'
    code = compile_source(source, "old.tg")
    assert "regexp" in code.lower()
    assert parse(source, "old.tg").handlers[0].regex == "^[0-9]+$"
    # The text syntax keeps its own spelling: on.message(TEXT, regex="...").
    text = 'token("1:x")\n\non.message(TEXT, regex="^[0-9]+$"):\n    send("цифры")\n'
    assert parse_text(text, "old.txt").handlers[0].regex == "^[0-9]+$"
    assert "regexp" in compile_text(text, "old.txt").lower()


def test_exact_texts_still_parse():
    source = 'bot token "1:x"\n\non message "да", "нет":\n    send "ладно"\n'
    assert tuple(parse(source, "old.tg").handlers[0].patterns) == ("да", "нет")


def test_a_hidden_filter_survives_the_node_board():
    source = 'bot token "1:x"\n\non message regex="^[0-9]+$":\n    send "цифры"\n'
    spec = parse(source, "old.tg")
    board = spec_to_nodes(spec)
    event = [node for node in board["nodes"].values() if node["type"] == "event"][0]
    # No field is drawn for it, but the value must not be dropped on the way back.
    assert event["props"]["regex"] == "^[0-9]+$"
    assert board_to_text(board) == spec_to_text(spec)


def test_the_block_editor_round_trips_it_as_well():
    spec = parse('bot token "1:x"\n\non message regex="^[0-9]+$":\n    send "цифры"\n',
                 "old.tg")
    assert blocks_xml_to_spec(spec_to_blocks_xml(spec)).handlers[0].regex == "^[0-9]+$"
""",
    "tests/test_i18n.py": r"""# The English interface is complete: every catalogue word has a translation.
#
# A missing entry falls back to Russian, which shows up as a Russian word inside an
# English palette - exactly the kind of half-translated UI this test prevents.

import pytest

from tgblocks import model
from tgblocks.model import ACTIONS, EVENTS, CHAT_FILTER, FROM_FILTER, REGEX_FILTER


def _catalogue_texts():
    for spec in ACTIONS + EVENTS:
        yield spec.label
        hint = getattr(spec, "hint", "")
        if hint:
            yield hint
        for param in spec.params:
            yield param.label
            if param.hint:
                yield param.hint
            for _value, label in param.choices:
                yield label
    for param in (CHAT_FILTER, FROM_FILTER, REGEX_FILTER):
        yield param.label
        for _value, label in param.choices:
            yield label
    for _value, label in model.KEYBOARD_STYLES:
        yield label
    for _value, label in model.BUTTON_KINDS:
        yield label


def test_every_catalogue_word_has_an_english_twin():
    # A few words are the same in both languages and need no dictionary entry.
    neutral = {"GIF", "web app", "URL", "RTMP", "ID"}
    missing = sorted({text for text in _catalogue_texts()
                      if text and text not in neutral
                      and model.english(text) == text})
    assert missing == [], "нет перевода: {0}".format(missing)


def test_the_schema_is_english_when_asked():
    schema = model.schema("en")
    russian = [action["label"] for action in schema["actions"]
               if action["label"] != action["label_en"]]
    assert russian == []
    for action in schema["actions"]:
        assert action["label"] == model.english(action["label"])
        for param in action["params"]:
            assert param["label"] == model.english(param["label"])


def test_the_default_language_is_english():
    # The editors read /api/schema without ?lang for their first paint.
    assert model.schema("EN")["lang"] == "en"
    assert model.schema("ru")["lang"] == "ru"
    assert model.schema("fr")["lang"] == "ru", "неизвестный язык - русский"
""",
    "tests/test_proxy.py": '# `tgblocks proxy` and the proxy checker behind it.\n#\n# The network itself is not touched here: the SOCKS5/HTTP handshakes are checked\n# byte for byte against a scripted socket, so the test says exactly which bytes\n# the bot sends and how each refusal is reported to the user.\n\nimport socket\nimport ssl\nimport struct\nfrom types import SimpleNamespace\n\nimport pytest\n\nfrom tgblocks.cli import main\nfrom tgblocks.network import ProxyError, check_proxy, parse_proxy, proxy_hint\n\n\n# ------------------------------------------------------------------- the string\n@pytest.mark.parametrize(\n    "url,scheme,host,port,user,password",\n    [\n        ("socks5://208.102.51.6:58208", "socks5", "208.102.51.6", 58208, None, None),\n        ("socks5://127.0.0.1", "socks5", "127.0.0.1", 1080, None, None),\n        ("socks4://10.0.0.1:9050", "socks4", "10.0.0.1", 9050, None, None),\n        ("http://proxy.local:3128", "http", "proxy.local", 3128, None, None),\n        ("https://proxy.local:8443", "https", "proxy.local", 8443, None, None),\n        ("socks5://user:p%40ss@host:1080", "socks5", "host", 1080, "user", "p@ss"),\n    ],\n)\ndef test_parse_proxy_accepts_what_the_bot_accepts(url, scheme, host, port, user, password):\n    assert parse_proxy(url) == (scheme, host, port, user, password)\n\n\n@pytest.mark.parametrize(\n    "url,fragment",\n    [\n        ("", "пустая"),\n        ("208.102.51.6:58208", "схема"),\n        ("ftp://host:21", "схема"),\n        ("socks5://", "хост"),\n    ],\n)\ndef test_parse_proxy_explains_a_wrong_string(url, fragment):\n    with pytest.raises(ProxyError) as info:\n        parse_proxy(url)\n    assert fragment in str(info.value)\n\n\ndef test_proxy_hint_shows_the_line_for_each_editor():\n    text = proxy_hint("socks5://1.2.3.4:1080")\n    assert \'bot proxy "socks5://1.2.3.4:1080"\' in text\n    assert \'proxy("socks5://1.2.3.4:1080")\' in text\n    assert "TG_PROXY=socks5://1.2.3.4:1080" in text\n\n\n# ---------------------------------------------------------- the handshakes\nclass FakeSocket:\n    """A stream: replies are concatenated and handed out size by size."""\n\n    def __init__(self, replies):\n        self.buffer = b"".join(replies)\n        self.sent = b""\n        self.closed = False\n\n    def sendall(self, data):\n        self.sent += data\n\n    def recv(self, size):\n        chunk, self.buffer = self.buffer[:size], self.buffer[size:]\n        return chunk\n\n    def settimeout(self, value):\n        self.timeout = value\n\n    def close(self):\n        self.closed = True\n\n\ndef fake_network(monkeypatch, sock, tls_reply=b"HTTP/1.1 400 Bad Request\\r\\n\\r\\n"):\n    def create_connection(address, timeout=None):\n        sock.address = address\n        return sock\n\n    class FakeTLS(FakeSocket):\n        def __init__(self):\n            super().__init__([])\n\n        def recv(self, size):\n            return tls_reply[:size]\n\n    tls = FakeTLS()\n    context = SimpleNamespace(\n        wrap_socket=lambda raw, server_hostname=None: tls\n    )\n    monkeypatch.setattr(socket, "create_connection", create_connection)\n    monkeypatch.setattr(ssl, "create_default_context", lambda: context)\n    return sock, tls\n\n\ndef test_socks5_handshake_is_exactly_what_the_bot_sends(monkeypatch):\n    sock = FakeSocket([\n        b"\\x05\\x00",              # method: no auth\n        b"\\x05\\x00\\x00\\x01",      # connect granted\n    ])\n    fake_network(monkeypatch, sock)\n\n    works, message, _ = check_proxy("socks5://1.2.3.4:1080", timeout=3)\n\n    assert works is True, message\n    assert sock.address == ("1.2.3.4", 1080)\n    expected = (b"\\x05\\x01\\x00"\n                b"\\x05\\x01\\x00\\x03" + bytes([len("api.telegram.org")])\n                + b"api.telegram.org" + (443).to_bytes(2, "big"))\n    assert sock.sent.startswith(expected)\n\n\ndef test_socks5_with_password_sends_the_credentials(monkeypatch):\n    sock = FakeSocket([b"\\x05\\x02", b"\\x01\\x00", b"\\x05\\x00\\x00\\x01"])\n    fake_network(monkeypatch, sock)\n\n    works, message, _ = check_proxy("socks5://user:secret@1.2.3.4:1080")\n\n    assert works is True, message\n    # RFC 1929: version 1, length-prefixed user name, then password.\n    assert sock.sent.startswith(b"\\x05\\x02\\x00")\n    assert b"\\x01\\x04user\\x06secret" in sock.sent\n\n\ndef test_socks5_refusal_is_reported_in_words(monkeypatch):\n    sock = FakeSocket([b"\\x05\\x00", b"\\x05\\x05\\x00\\x01"])  # connection refused\n    fake_network(monkeypatch, sock)\n\n    works, message, _ = check_proxy("socks5://1.2.3.4:1080")\n\n    assert works is False\n    assert "не пустил" in message\n    assert "отклонено" in message\n\n\ndef test_http_proxy_uses_connect_and_reports_a_refusal(monkeypatch):\n    sock = FakeSocket([b"HTTP/1.1 407 Proxy Authentication Required\\r\\n\\r\\n"])\n    fake_network(monkeypatch, sock)\n\n    works, message, _ = check_proxy("http://1.2.3.4:3128")\n\n    assert works is False\n    assert "отказ" in message\n    assert sock.sent.startswith(b"CONNECT api.telegram.org:443 HTTP/1.1")\n\n\ndef test_socks4_handshake(monkeypatch):\n    sock = FakeSocket([b"\\x00\\x5a\\x00\\x00\\x00\\x00\\x00\\x00"])\n    fake_network(monkeypatch, sock)\n    monkeypatch.setattr(socket, "gethostbyname", lambda host: "149.154.167.220")\n\n    works, message, _ = check_proxy("socks4://1.2.3.4:1080")\n\n    assert works is True, message\n    assert sock.sent == (b"\\x04\\x01" + struct.pack(">H", 443)\n                         + socket.inet_aton("149.154.167.220") + b"\\x00")\n\n\ndef test_a_dead_proxy_is_reported_without_raising(monkeypatch):\n    def refuse(address, timeout=None):\n        raise TimeoutError("timed out")\n\n    monkeypatch.setattr(socket, "create_connection", refuse)\n\n    works, message, seconds = check_proxy("socks5://208.102.51.6:58208", timeout=2)\n\n    assert works is False\n    assert "нет соединения" in message\n    assert "208.102.51.6:58208" in message\n\n\n# ------------------------------------------------------------------ the command\ndef test_proxy_command_reports_a_working_proxy(monkeypatch, capsys):\n    monkeypatch.setattr("tgblocks.network.check_proxy",\n                        lambda url, timeout=8.0: (True, "работает: HTTP/1.1 400", 0.4))\n    code = main(["proxy", "socks5://1.2.3.4:1080"])\n    out = capsys.readouterr().out\n    assert code == 0\n    assert "OK" in out\n    assert \'bot proxy "socks5://1.2.3.4:1080"\' in out\n\n\ndef test_proxy_command_fails_on_a_dead_proxy(monkeypatch, capsys):\n    monkeypatch.setattr("tgblocks.network.check_proxy",\n                        lambda url, timeout=8.0: (False, "нет соединения", 2.0))\n    code = main(["proxy", "socks5://1.2.3.4:1080"])\n    assert code == 1\n    assert "FAIL" in capsys.readouterr().out\n\n\ndef test_proxy_command_explains_a_bad_string(capsys):\n    code = main(["proxy", "1.2.3.4:1080"])\n    assert code == 1\n    assert "схема" in capsys.readouterr().err\n\n\ndef test_proxy_command_uses_the_environment(monkeypatch, capsys):\n    monkeypatch.setenv("TG_PROXY", "socks5://9.9.9.9:1080")\n    monkeypatch.setattr("tgblocks.network.check_proxy",\n                        lambda url, timeout=8.0: (True, "работает", 0.1))\n    code = main(["proxy"])\n    assert code == 0\n    assert "9.9.9.9" in capsys.readouterr().out\n\n\ndef test_proxy_command_without_anything_says_how(capsys, monkeypatch):\n    monkeypatch.delenv("TG_PROXY", raising=False)\n    code = main(["proxy"])\n    assert code == 2\n    assert "tgblocks proxy" in capsys.readouterr().err\n',
    "tests/test_scaffold.py": r"""# scaffold.py carries a copy of the whole project, because it must work in an
# empty folder with nothing but itself. That copy used to drift (it was 600 lines
# behind, and the project it generated had a broken editor page), so these tests
# hold the copy and the tree together. Regenerate with:
#
#     python tools/build_scaffold.py

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SCAFFOLD = ROOT / "scaffold.py"
HAS_TOOL = SCAFFOLD.exists() and (TOOLS / "build_scaffold.py").exists()

pytestmark = pytest.mark.skipif(
    not HAS_TOOL,
    reason="scaffold.py and tools/ are not part of this copy of the project",
)

build_scaffold = None
if HAS_TOOL:
    # A generated project carries these tests but not the generator itself, so
    # the import must not run there (a module-level ImportError is not skippable).
    sys.path.insert(0, str(TOOLS))
    import build_scaffold  # noqa: E402

import importlib.util  # noqa: E402


def load_scaffold():
    spec = importlib.util.spec_from_file_location("tgblocks_scaffold", SCAFFOLD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def scaffold():
    return load_scaffold()


def test_payload_is_regenerated_from_the_tree():
    # --check exits 1 and prints an explanation when someone edited a source file
    # without rebuilding the payload.
    assert build_scaffold.main(["--check"]) == 0


def test_every_embedded_file_matches_the_disk(scaffold):
    for relative, content in scaffold.FILES.items():
        on_disk = (ROOT / relative)
        assert on_disk.is_file(), "embedded file is gone: " + relative
        assert on_disk.read_text(encoding="utf-8") == content, (
            "embedded copy of {0} is stale".format(relative)
        )


def test_every_project_file_is_embedded(scaffold):
    missing = sorted(set(build_scaffold.collect_files()) - set(scaffold.FILES))
    assert missing == []


def test_generated_project_is_identical(scaffold, tmp_path):
    target = scaffold.create_project(str(tmp_path / "out"))
    written = sorted(
        item.relative_to(target).as_posix()
        for item in target.rglob("*")
        if item.is_file()
    )
    assert written == sorted(scaffold.FILES)
    for relative in written:
        assert (target / relative).read_text(encoding="utf-8") == scaffold.FILES[relative]


def test_generated_project_is_installable_python_package(scaffold, tmp_path):
    target = scaffold.create_project(str(tmp_path / "out"))
    assert (target / "pyproject.toml").exists()
    assert (target / "src" / "tgblocks" / "__init__.py").exists()
    assert (target / "src" / "tgblocks" / "visual" / "static" / "nodes.html").exists()
    # The page asks for this file over HTTP: a copy without it cannot run.
    assert (target / "src" / "tgblocks" / "visual" / "static" / "tgblocks-project.js").exists()
    assert (target / "tests" / "test_sync.py").exists()
""",
    "tests/test_security.py": '# The editor is a local web server that can start processes, so it is a target:\n# any page the user visits could POST to 127.0.0.1 while the editor is open.\n# These tests replay the attacks that used to work and must keep failing.\n\nimport json\nimport threading\nimport urllib.error\nimport urllib.request\nfrom http.server import ThreadingHTTPServer\n\nimport pytest\n\nimport tgblocks.visual.server as server\n\nGOOD_TEXT = \'token("1:x")\\n\\non.command("/start"):\\n    send("hi")\\n\'\n\n\n@pytest.fixture()\ndef api(tmp_path, monkeypatch):\n    monkeypatch.setattr(server, "STORAGE_DIR", tmp_path / "projects")\n    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server._Handler)\n    httpd.view = "nodes"\n    thread = threading.Thread(target=httpd.serve_forever, daemon=True)\n    thread.start()\n    base = "http://127.0.0.1:{0}".format(httpd.server_address[1])\n    yield base\n    httpd.shutdown()\n    httpd.server_close()\n\n\ndef request(base, path, payload=None, headers=None, method=None):\n    """Return (status, body) and never raise for 4xx/5xx; body is JSON when it is."""\n    data = None if payload is None else json.dumps(payload).encode("utf-8")\n    req = urllib.request.Request(base + path, data=data, headers=headers or {},\n                                 method=method)\n\n    def parse(raw):\n        if not raw:\n            return None\n        try:\n            return json.loads(raw)\n        except json.JSONDecodeError:\n            return raw\n\n    try:\n        with urllib.request.urlopen(req, timeout=10) as response:\n            return response.status, parse(response.read().decode("utf-8"))\n    except urllib.error.HTTPError as error:\n        return error.code, parse(error.read().decode("utf-8"))\n\n\nJSON = {"Content-Type": "application/json"}\n\n\n# --------------------------------------------------------------------- the attacks\ndef test_cross_origin_post_is_refused(api):\n    # Exactly the request a hostile page can send with fetch(..., {mode:"no-cors"}).\n    status, body = request(\n        api,\n        "/api/run",\n        {"code": "print(\'ARBITRARY-CODE-RAN\')"},\n        headers={\n            "Origin": "https://evil.example",\n            "Content-Type": "text/plain;charset=UTF-8",\n        },\n    )\n    assert status in (403, 415)\n    assert body.get("ok") is False\n    assert server.RUNNER.running() is False\n\n\ndef test_cross_origin_write_is_refused_and_stores_nothing(api):\n    status, _ = request(\n        api,\n        "/api/project?name=stolen",\n        {"baseRev": 0, "text": GOOD_TEXT},\n        headers={"Origin": "https://evil.example", "Content-Type": "text/plain"},\n    )\n    assert status in (403, 415)\n    status, body = request(api, "/api/files?kind=bots", headers=JSON)\n    assert status == 200 and body["files"] == []\n\n\ndef test_sec_fetch_site_cross_site_is_refused(api):\n    status, _ = request(\n        api,\n        "/api/project?name=stolen",\n        {"text": GOOD_TEXT},\n        headers={"Sec-Fetch-Site": "cross-site", **JSON},\n    )\n    assert status == 403\n\n\ndef test_dns_rebinding_host_is_refused(api):\n    # A hostile domain pointed at 127.0.0.1 keeps its own name in Host.\n    status, _ = request(api, "/api/files?kind=bots",\n                        headers={"Host": "evil.example:80"})\n    assert status == 403\n\n\ndef test_non_json_body_is_refused(api):\n    # `<form enctype="text/plain">` and no-cors fetches cannot lie about this.\n    status, _ = request(api, "/api/compile", {"dsl": GOOD_TEXT},\n                        headers={"Content-Type": "application/x-www-form-urlencoded"})\n    assert status == 415\n\n\ndef test_preflight_does_not_grant_cors(api):\n    req = urllib.request.Request(api + "/api/run", method="OPTIONS")\n    try:\n        with urllib.request.urlopen(req, timeout=10) as response:\n            headers = dict(response.headers)\n            status = response.status\n    except urllib.error.HTTPError as error:\n        headers = dict(error.headers)\n        status = error.code\n    assert status >= 400\n    assert "Access-Control-Allow-Origin" not in headers\n\n\n# ------------------------------------------------------------- the editor still works\ndef test_same_origin_json_request_still_works(api):\n    status, body = request(\n        api,\n        "/api/compile",\n        {"dsl": \'bot token "1:x"\\n\\non /start:\\n    send "hi"\\n\'},\n        headers={"Origin": api, **JSON},\n    )\n    assert status == 200 and body["ok"] is True\n    assert "async def" in body["code"]\n\n\ndef test_the_page_itself_loads(api):\n    status, _ = request(api, "/nodes")\n    assert status == 200\n\n\ndef test_wide_bind_needs_an_explicit_flag():\n    with pytest.raises(SystemExit) as info:\n        server.serve(host="0.0.0.0", open_browser=False)\n    assert "allow-remote" in str(info.value)\n',
    "tests/test_server_ports.py": '# The local server\'s behaviour around ports: `tgblocks` must always end with a\n# working editor, from any folder, and must never open a stale window after an\n# upgrade without saying so.\n\nimport json\nimport socket\nimport threading\nimport urllib.error\nimport urllib.request\n\nimport pytest\n\nimport tgblocks.visual.server as server\n\n\n@pytest.fixture()\ndef running_editor(tmp_path, monkeypatch):\n    """A real tgblocks server on a free port, as the first instance."""\n    monkeypatch.setattr(server, "STORAGE_DIR", tmp_path / "projects")\n    httpd = server._Server(("127.0.0.1", 0), server._Handler)\n    httpd.view = "nodes"\n    thread = threading.Thread(target=httpd.serve_forever, daemon=True)\n    thread.start()\n    yield httpd.server_address[1]\n    httpd.shutdown()\n    httpd.server_close()\n\n\n@pytest.fixture()\ndef stop_after_banner(monkeypatch):\n    """Make serve() return right after printing the banner."""\n\n    def fake_serve_forever(self):\n        raise KeyboardInterrupt\n\n    monkeypatch.setattr(server, "_Server", _OneShotServer)\n    return None\n\n\nclass _OneShotServer(server._Server):\n    def serve_forever(self):\n        raise KeyboardInterrupt\n\n\ndef test_second_start_opens_the_running_editor(running_editor, capsys, monkeypatch):\n    opened = []\n    monkeypatch.setattr(server.webbrowser, "open", lambda url: opened.append(url))\n\n    # No exception: the second invocation points at the editor that already runs.\n    server.serve(port=running_editor, open_browser=True)\n\n    printed = capsys.readouterr().out\n    assert "http://127.0.0.1:{0}/".format(running_editor) in printed\n    assert opened == ["http://127.0.0.1:{0}/".format(running_editor)]\n    # Exactly one address is offered, not a list of ports to try.\n    assert printed.count("http://") == 1\n\n\ndef test_an_old_window_does_not_stop_the_new_editor(capsys, monkeypatch):\n    # A stale 0.1.0 keeps the port; the new code must still give the user an editor\n    # and say where it went, instead of opening the old pages. The port is taken\n    # for real, so the test does not depend on what happens to run on this machine.\n    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n    blocker.bind(("127.0.0.1", 0))\n    blocker.listen(1)\n    port = blocker.getsockname()[1]\n    monkeypatch.setattr(server, "_existing_editor", lambda host, taken: "0.0.1")\n    monkeypatch.setattr(server.webbrowser, "open", lambda url: None)\n    monkeypatch.setattr(server, "_Server", _OneShotServer)\n    try:\n        server.serve(port=port, open_browser=False)\n    finally:\n        blocker.close()\n\n    printed = capsys.readouterr().out\n    assert "old tgblocks 0.0.1" in printed\n    assert "starting on " in printed\n    assert printed.count("http://") == 1\n    assert "http://127.0.0.1:{0}/".format(port) not in printed\n\n\ndef test_a_taken_port_moves_to_the_next_free_one(capsys, monkeypatch):\n    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n    blocker.bind(("127.0.0.1", 0))\n    blocker.listen(1)\n    port = blocker.getsockname()[1]\n    monkeypatch.setattr(server, "webbrowser", server.webbrowser)\n    monkeypatch.setattr(server.webbrowser, "open", lambda url: None)\n    monkeypatch.setattr(server, "_Server", _OneShotServer)\n    try:\n        server.serve(port=port, open_browser=False)\n    finally:\n        blocker.close()\n\n    printed = capsys.readouterr().out\n    assert "taken by another program" in printed\n    assert "http://127.0.0.1:{0}/".format(port + 1) in printed\n    assert printed.count("http://") == 1\n\n\ndef test_the_banner_names_one_address(capsys, monkeypatch):\n    monkeypatch.setattr(server.webbrowser, "open", lambda url: None)\n    monkeypatch.setattr(server, "_Server", _OneShotServer)\n\n    free = server._find_free_port("127.0.0.1", 8800)\n    server.serve(port=free, open_browser=False)\n\n    printed = capsys.readouterr().out\n    assert printed.count("http://") == 1\n    assert "http://127.0.0.1:{0}/".format(free) in printed\n\n\ndef test_a_request_without_a_source_says_to_reload(tmp_path, monkeypatch):\n    monkeypatch.setattr(server, "STORAGE_DIR", tmp_path / "projects")\n    httpd = server._Server(("127.0.0.1", 0), server._Handler)\n    httpd.view = "nodes"\n    thread = threading.Thread(target=httpd.serve_forever, daemon=True)\n    thread.start()\n    port = httpd.server_address[1]\n    try:\n        body = json.dumps({}).encode("utf-8")\n        request = urllib.request.Request(\n            "http://127.0.0.1:{0}/api/compile".format(port), data=body,\n            headers={"Content-Type": "application/json"},\n        )\n        with pytest.raises(urllib.error.HTTPError) as info:\n            urllib.request.urlopen(request, timeout=5)\n        payload = json.loads(info.value.read().decode("utf-8"))\n        assert info.value.code == 400\n        assert "reload the editor page" in payload["error"]\n        assert "Ctrl+F5" in payload["error"]\n    finally:\n        httpd.shutdown()\n        httpd.server_close()\n\n\ndef test_find_free_port_skips_busy_ones():\n    blocker = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n    blocker.bind(("127.0.0.1", 0))\n    blocker.listen(1)\n    busy = blocker.getsockname()[1]\n    try:\n        found = server._find_free_port("127.0.0.1", busy, tries=5)\n        assert found is not None and found > busy\n    finally:\n        blocker.close()\n',
    "tests/test_sync.py": '# Tests for the shared project store: every visual editor has to see the same\n# bot, and no conversion may quietly drop part of it.\n#\n# The three views are only different pictures of one text document, so these\n# tests pin down that promise: text -> nodes -> text and text -> blocks -> text\n# keep every action, every pattern and the canvas layout.\n\nimport json\nimport threading\nimport urllib.request\nfrom http.server import ThreadingHTTPServer\n\nimport pytest\n\nfrom tgblocks.convert import (\n    board_layout,\n    board_to_text,\n    spec_to_blocks_xml,\n    spec_to_nodes,\n    spec_to_text,\n)\nfrom tgblocks.dsl.parser import parse\nfrom tgblocks.textlang import parse_text\n\nFULL = """token("123456:TEST")\nname("Demo bot")\nproxy("socks5://127.0.0.1:1080")\n\non.command("/start"):\n    send("Привет!")\n    buttons("inline")\n    button("Помощь", "/help")\n    button("Сайт", url="https://example.com")\n\non.message(TEXT, "привет", "здравствуй"):\n    typing()\n    delay(2)\n    send_photo("https://example.com/cat.jpg", "Котик")\n    delete()\n\non.message(PHOTO):\n    when("contains", "кот"):\n        send("Мур")\n    otherwise():\n        send("Не кот")\n    pass\n"""\n\n\ndef _canonical(text: str) -> str:\n    return spec_to_text(parse_text(text, "test.txt"))\n\n\ndef test_text_survives_the_node_board():\n    canonical = _canonical(FULL)\n    assert board_to_text(spec_to_nodes(parse_text(canonical, "t"))) == canonical\n\n\ndef test_text_survives_the_block_editor():\n    # The blocks view cannot show every node, so its XML must carry them all.\n    canonical = _canonical(FULL)\n    xml = spec_to_blocks_xml(parse_text(canonical, "t"))\n    for needed in ("tg_photo", "tg_typing", "tg_delay", "tg_delete", "tg_nothing"):\n        assert \'<block type="{}"\'.format(needed) in xml\n    assert \'<field name="NAME">Demo bot</field>\' in xml\n    assert \'<field name="PROXY">socks5://127.0.0.1:1080</field>\' in xml\n\n\ndef test_event_filter_travels_with_the_bot():\n    # `on.message(TEXT, "a", "b")` is a filter on the event, not a condition:\n    # it must survive both canvases instead of being rewritten or dropped.\n    spec = parse_text(\'token("1:x")\\non.message(TEXT, "привет", "здравствуй"):\\n\'\n                      \'    send("Hi")\\n\', "t")\n\n    xml = spec_to_blocks_xml(spec)\n    assert \'<field name="PATTERNS">привет, здравствуй</field>\' in xml\n\n    board = spec_to_nodes(spec)\n    events = [node for node in board["nodes"].values() if node["type"] == "event"]\n    assert events[0]["props"]["patterns"] == ["привет", "здравствуй"]\n    assert board_to_text(board) == _canonical(\n        \'token("1:x")\\non.message(TEXT, "привет", "здравствуй"):\\n    send("Hi")\\n\'\n    )\n\n\ndef test_condition_with_several_values_survives_every_view():\n    # `when("contains", "Привет";"привет")` is one condition, not two branches.\n    text = (\'token("1:x")\\n\\non.message(TEXT):\\n\'\n            \'    when("contains", "Привет"; "привет"):\\n\'\n            \'        send("Привет!")\\n\'\n            \'    otherwise():\\n\'\n            \'        pass\\n\')\n    canonical = _canonical(text)\n    board = spec_to_nodes(parse_text(canonical, "t"))\n    assert board_to_text(board) == canonical\n\n    xml = spec_to_blocks_xml(parse_text(canonical, "t"))\n    assert \'<field name="VALUE">Привет</field>\' in xml\n    assert \'<field name="VALUES">привет</field>\' in xml\n\n\ndef test_dsl_accepts_several_condition_values():\n    spec = parse(\'bot token "1:x"\\non /start:\\n\'\n                 \'    when text contains "Привет", "привет":\\n\'\n                 \'        send "hi"\\n\')\n    condition = spec.handlers[0].actions[0].condition\n    assert condition.op == "contains"\n    assert (condition.value,) + condition.values == ("Привет", "привет")\n\n\n\ndef test_node_board_keeps_the_bot_name_and_the_text_filter():\n    board = spec_to_nodes(parse_text(FULL, "t"))\n    bot = board["nodes"][board["rootId"]]\n    assert bot["props"]["name"] == "Demo bot"\n\n    events = [node for node in board["nodes"].values() if node["type"] == "event"]\n    filtered = [node for node in events if node["props"].get("patterns")]\n    assert filtered[0]["props"]["patterns"] == ["привет", "здравствуй"]\n\n\ndef test_layout_survives_rebuilding_the_board():\n    spec = parse_text(FULL, "t")\n    board = spec_to_nodes(spec)\n    moved = board["rootId"]\n    board["nodes"][moved]["x"] = 999\n    board["nodes"][moved]["y"] = 777\n\n    layout = board_layout(board)\n    rebuilt = spec_to_nodes(parse_text(FULL, "t"), layout)\n\n    assert rebuilt["nodes"][moved]["x"] == 999\n    assert rebuilt["nodes"][moved]["y"] == 777\n\n\ndef test_dsl_accepts_text_patterns():\n    spec = parse(\'bot token "1:x"\\non message "a", "b":\\n    send "hi"\\n\')\n    assert spec.handlers[0].kind == "text"\n    assert spec.handlers[0].patterns == ("a", "b")\n\n\n# ------------------------------------------------------------- the HTTP store\n@pytest.fixture()\ndef api(tmp_path, monkeypatch):\n    import tgblocks.visual.server as server\n\n    monkeypatch.setattr(server, "STORAGE_DIR", tmp_path / "projects")\n    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server._Handler)\n    httpd.view = "nodes"\n    thread = threading.Thread(target=httpd.serve_forever, daemon=True)\n    thread.start()\n    base = "http://127.0.0.1:{0}".format(httpd.server_address[1])\n    yield base\n    httpd.shutdown()\n    httpd.server_close()\n\n\ndef _get(base: str, path: str):\n    with urllib.request.urlopen(base + path) as response:\n        return json.loads(response.read().decode("utf-8"))\n\n\ndef _post(base: str, path: str, payload: dict):\n    data = json.dumps(payload).encode("utf-8")\n    request = urllib.request.Request(\n        base + path, data=data, headers={"Content-Type": "application/json"}\n    )\n    with urllib.request.urlopen(request) as response:\n        return json.loads(response.read().decode("utf-8"))\n\n\ndef test_store_round_trip_and_revisions(api):\n    empty = _get(api, "/api/project?name=bot1")\n    assert empty["text"] == "" and empty["rev"] == 0\n\n    first = _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})\n    assert first["ok"] and first["rev"] == 1\n    assert first["text"] == _canonical(FULL)\n    assert _get(api, "/api/rev?name=bot1")["rev"] == 1\n\n    second = _post(api, "/api/project?name=bot1",\n                   {"baseRev": 1, "text": first["text"].replace("Привет!", "Здравствуйте!")})\n    assert second["ok"] and second["rev"] == 2\n    assert "Здравствуйте!" in _get(api, "/api/project?name=bot1")["text"]\n\n\ndef test_stale_editor_gets_a_conflict_instead_of_overwriting(api):\n    _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})\n    # A second tab still believes the file is at revision 0.\n    stale = _post(api, "/api/project?name=bot1",\n                  {"baseRev": 0, "text": \'token("1:x")\\non.command("/a"):\\n    send("x")\\n\'})\n    assert stale["ok"] is False and stale["conflict"] is True\n    assert stale["rev"] == 1\n    assert "Привет" in stale["text"]          # the editor reloads this text\n    assert "Привет" in _get(api, "/api/project?name=bot1")["text"]\n\n\ndef test_broken_text_is_rejected_and_not_stored(api):\n    good = _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})\n    bad = _post(api, "/api/project?name=bot1",\n                {"baseRev": good["rev"], "text": \'token("1:x")\\n\'})\n    assert bad["ok"] is False and ("event" in bad["error"] or "handler" in bad["error"])\n    stored = _get(api, "/api/project?name=bot1")\n    assert stored["rev"] == good["rev"]\n    assert stored["text"] == _canonical(FULL)\n\n\ndef test_layout_is_saved_without_a_new_revision(api):\n    _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})\n    payload = {"layout": {"b": {"x": 10, "y": 20}}}\n    _post(api, "/api/project_layout?name=bot1", payload)\n\n    stored = _get(api, "/api/project?name=bot1")\n    assert stored["rev"] == 1                  # dragging blocks is not an edit\n    assert stored["layout"] == {"b": {"x": 10, "y": 20}}\n\n\ndef test_board_comes_back_where_it_was(api):\n    _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})\n    _post(api, "/api/project_layout?name=bot1", {"layout": {"b": {"x": 500, "y": 600}}})\n\n    board = _post(api, "/api/to_nodes?name=bot1", {"source": _canonical(FULL), "name": "bot1"})\n    assert board["ok"]\n    assert board["nodes"]["nodes"][board["nodes"]["rootId"]]["x"] == 500\n\n\ndef test_old_project_files_are_read_as_text(api, tmp_path):\n    folder = tmp_path / "projects" / "bots"\n    folder.mkdir(parents=True)\n    legacy = {\n        "nodes": spec_to_nodes(parse_text(FULL, "t")),\n        "text": FULL,\n        "stamp": {"nodes": 111, "text": 222},\n    }\n    (folder / "old.json").write_text(json.dumps(legacy), encoding="utf-8")\n\n    stored = _get(api, "/api/project?name=old")\n    assert stored["rev"] == 1\n    assert stored["text"] == _canonical(FULL)\n    assert stored["layout"]                   # canvas positions kept\n\n\ndef test_edit_in_one_view_reaches_the_others(api):\n    # 1. The text view writes a bot.\n    first = _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})\n    assert first["ok"]\n\n    # 2. The node view opens it: it gets the same bot as a board.\n    board = _post(api, "/api/to_nodes?name=bot1",\n                  {"source": _get(api, "/api/project?name=bot1")["text"], "name": "bot1"})\n    nodes = board["nodes"]["nodes"]\n\n    # 3. The user edits one send block in the node view and saves the board.\n    send = [node for node in nodes.values() if node["type"] == "send"][0]\n    send["props"]["text"] = "Правка из узлов"\n    saved = _post(api, "/api/project?name=bot1",\n                  {"baseRev": first["rev"], "nodes": board["nodes"]})\n    assert saved["ok"] and saved["changed"] is True\n    assert saved["rev"] == first["rev"] + 1\n\n    # 4. The text view polls the revision and reads the edit.\n    assert _get(api, "/api/rev?name=bot1")["rev"] == saved["rev"]\n    assert "Правка из узлов" in _get(api, "/api/project?name=bot1")["text"]\n\n    # 5. The block view renders it from that same text.\n    xml = _post(api, "/api/to_blocks", {"source": saved["text"]})\n    assert xml["ok"] and "Правка из узлов" in xml["xml"]\n\n\ndef test_dragging_blocks_does_not_rewrite_the_bot(api):\n    plain = \'token("1:x")\\n\\non.command("/start"):\\n    send("Hi")\\n\'\n    first = _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": plain})\n    board = _post(api, "/api/to_nodes?name=bot1", {"source": first["text"], "name": "bot1"})\n    root = board["nodes"]["rootId"]\n    board["nodes"]["nodes"][root]["x"] = 1234\n\n    # Same bot, new position: the text did not change, so no view reloads.\n    moved = _post(api, "/api/project?name=bot1",\n                  {"baseRev": first["rev"], "nodes": board["nodes"]})\n    assert moved["ok"] and moved["changed"] is False\n    assert moved["rev"] == first["rev"]\n\n    stored = _get(api, "/api/project?name=bot1")\n    assert stored["layout"]["b"] == {"x": 1234, "y": board["nodes"]["nodes"][root]["y"]}\n\n\ndef test_unfinished_board_is_kept_as_a_draft(api):\n    first = _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": FULL})\n    # A canvas with only a bot block and no token: not a bot yet.\n    draft = {"nodes": {"b1": {"id": "b1", "type": "bot", "props": {"token": ""},\n                              "parent": None, "children": [], "x": 0, "y": 0}},\n             "counter": 1, "rootId": "b1", "manual": True}\n    reply = _post(api, "/api/project?name=bot1", {"baseRev": first["rev"], "nodes": draft})\n    assert reply["ok"] and reply["incomplete"] is True\n    assert reply["rev"] == first["rev"]          # the good text is untouched\n\n    stored = _get(api, "/api/project?name=bot1")\n    assert stored["draft"]["board"]["rootId"] == "b1"\n    assert "Привет" in stored["text"]\n\n\ndef test_shared_module_is_served(api):\n    with urllib.request.urlopen(api + "/tgblocks-project.js") as response:\n        body = response.read().decode("utf-8")\n    assert "TgProject" in body\n\n\ndef test_block_editor_reads_every_field_it_is_given():\n    # The block editor now round-trips through Blockly XML, so the invariant is\n    # that the XML reader understands every field the writer emits and that the\n    # bot comes back unchanged. A field the reader ignores would be a silent\n    # data loss on the next save.\n    import re\n\n    from tgblocks.convert import blocks_xml_to_spec\n    from tgblocks.model import ACTIONS, EVENTS\n\n    xml = spec_to_blocks_xml(parse_text(FULL, "t"))\n    emitted = set(re.findall(r\'<field name="([A-Za-z_]+)"\', xml))\n\n    allowed = {"TOKEN", "NAME", "PROXY", "WEBHOOK", "KIND", "COMMAND", "PATTERNS",\n               "DATA", "STATE", "CHAT", "FROM_USER", "REGEX", "LABEL", "TARGET",\n               "STYLE", "OP", "VALUE", "VALUES", "SOURCE"}\n    for spec in list(ACTIONS) + list(EVENTS):\n        for param in spec.params:\n            allowed.add(param.name.upper())\n\n    assert emitted - allowed == set()\n    assert spec_to_text(blocks_xml_to_spec(xml)) == _canonical(FULL)\n\n\ndef test_board_save_that_would_drop_an_event_filter_is_refused(api):\n    filtered = \'token("1:x")\\n\\non.message(TEXT, "привет"):\\n    send("Hi")\\n\'\n    first = _post(api, "/api/project?name=bot1", {"baseRev": 0, "text": filtered})\n\n    # A board that cannot carry the filter (the block editor has no field for\n    # it) would silently drop it: the server refuses instead.\n    board = _post(api, "/api/to_nodes?name=bot1", {"source": first["text"], "name": "bot1"})\n    nodes = board["nodes"]["nodes"]\n    event = [node for node in nodes.values() if node["type"] == "event"][0]\n    event["props"].pop("patterns", None)\n    reply = _post(api, "/api/project?name=bot1",\n                  {"baseRev": first["rev"], "nodes": board["nodes"]})\n    assert reply["ok"] is False and reply["lossy"] is True\n    assert "текст" in reply["error"]\n\n    stored = _get(api, "/api/project?name=bot1")\n    assert stored["text"] == first["text"]     # the bot is untouched\n\n\n',
    "tests/test_ui.py": '# The editor HTTP API: the schema the pages are built from, and the two\n# "compile this canvas" paths the node and block editors use.\n#\n# These tests speak to a real server, so a page that would break is caught here\n# rather than by clicking through it.\n\nimport json\nimport sys\nimport pathlib\nimport subprocess\nimport threading\nimport urllib.error\nimport urllib.request\nfrom http.server import ThreadingHTTPServer\n\nimport pytest\n\nimport tgblocks.visual.server as server\nfrom tgblocks.convert import spec_to_blocks_xml, spec_to_nodes, spec_to_text\nfrom tgblocks.dsl import compile_source\nfrom tgblocks.textlang import parse_text\n\nROOT = pathlib.Path(__file__).resolve().parents[1]\nSTATIC = ROOT / "src" / "tgblocks" / "visual" / "static"\n\nFULL = """token("1:TEST")\nname("Demo bot")\n\non.command("/start"):\n    send("РџСЂРёРІРµС‚!")\n    button("РџРѕРјРѕС‰СЊ", "/help")\n\non.message(TEXT, "РїСЂРёРІРµС‚"):\n    send_document("https://example.com/f.pdf", "С„Р°Р№Р»")\n    when("contains", "РєРѕС‚"):\n        send("РњСѓСЂ")\n    otherwise():\n        send("РќРµ РєРѕС‚")\n\non.callback("/buy"):\n    send("РїРѕРєСѓРїР°РµРј")\n"""\n\n\n@pytest.fixture()\ndef api(tmp_path, monkeypatch):\n    monkeypatch.setattr(server, "STORAGE_DIR", tmp_path / "projects")\n    httpd = ThreadingHTTPServer(("127.0.0.1", 0), server._Handler)\n    httpd.view = "nodes"\n    thread = threading.Thread(target=httpd.serve_forever, daemon=True)\n    thread.start()\n    yield "http://127.0.0.1:{0}".format(httpd.server_address[1])\n    httpd.shutdown()\n    httpd.server_close()\n\n\ndef get(base, path):\n    with urllib.request.urlopen(base + path, timeout=10) as response:\n        return json.loads(response.read().decode("utf-8"))\n\n\ndef post(base, path, payload):\n    body = json.dumps(payload).encode("utf-8")\n    request = urllib.request.Request(base + path, data=body,\n                                     headers={"Content-Type": "application/json"})\n    try:\n        with urllib.request.urlopen(request, timeout=30) as response:\n            return json.loads(response.read().decode("utf-8"))\n    except urllib.error.HTTPError as error:\n        return json.loads(error.read().decode("utf-8"))\n\n\n# ------------------------------------------------------------------- the schema\ndef test_schema_describes_every_feature(api):\n    schema = get(api, "/api/schema")\n    assert schema["version"] >= 2\n    assert len(schema["actions"]) >= 25\n    assert len(schema["events"]) >= 20\n    for action in schema["actions"]:\n        assert action["kind"] and action["label"] and action["group"]\n        assert isinstance(action["params"], list)\n        assert action["observers"]\n    for event in schema["events"]:\n        assert event["kind"] and event["label"] and event["observer"]\n    assert {"inline", "reply"} == {item["value"] for item in schema["keyboards"]}\n\n\ndef test_schema_covers_the_aiogram_methods_we_promise(api):\n    kinds = {action["kind"] for action in get(api, "/api/schema")["actions"]}\n    for needed in ("send_document", "send_video", "send_poll", "send_location",\n                   "answer_callback", "edit_text", "set_state", "clear_state",\n                   "ban_user", "mute_user", "inline_result"):\n        assert needed in kinds\n\n\n# --------------------------------------------------------------- node editor API\ndef test_board_compiles_into_text_and_code(api):\n    spec = parse_text(FULL, "t")\n    board = spec_to_nodes(spec)\n    data = post(api, "/api/compile", {"nodes": board})\n    assert data["ok"] is True, data\n    assert data["text"] == spec_to_text(parse_text(spec_to_text(spec), "t2"))\n    assert "async def" in data["code"]\n    assert "answer_document" in data["code"]\n\n\ndef test_board_compiles_into_importable_aiogram_code(api):\n    pytest.importorskip("aiogram")\n    board = spec_to_nodes(parse_text(FULL, "t"))\n    code = post(api, "/api/compile", {"nodes": board})["code"]\n    namespace = {"__name__": "ui_board_bot", "__file__": "<generated>"}\n    exec(compile(code, "<generated>", "exec"), namespace)\n    assert namespace["dp"] is not None\n\n\ndef test_broken_board_is_an_answer_not_a_crash(api):\n    data = post(api, "/api/compile", {"nodes": {"nodes": {"x": "nonsense"}}})\n    assert data["ok"] is False\n    assert data["error"]\n\n\ndef test_empty_board_is_an_answer_not_a_crash(api):\n    data = post(api, "/api/compile", {"nodes": {}})\n    assert data["ok"] is False or data.get("text") is not None\n\n\ndef test_boards_warnings_reach_the_page(api):\n    # A button that calls a command nobody handles is worth showing in the UI.\n    board = spec_to_nodes(parse_text(\n        \'token("1:x")\\n\\non.command("/start"):\\n    send("m")\\n\'\n        \'    button("РќРµС‚", "/missing")\\n\', "t"))\n    data = post(api, "/api/compile", {"nodes": board})\n    assert data["ok"] is True\n    assert any("/missing" in warning for warning in data["warnings"])\n\n\n# -------------------------------------------------------------- block editor API\ndef test_xml_workspace_compiles(api):\n    xml = spec_to_blocks_xml(parse_text(FULL, "t"))\n    data = post(api, "/api/compile", {"xml": xml})\n    assert data["ok"] is True, data\n    assert "answer_document" in data["code"]\n\n\ndef test_invalid_xml_is_an_answer_not_a_crash(api):\n    data = post(api, "/api/compile", {"xml": "<xml><block"})\n    assert data["ok"] is False\n    assert data["error"]\n\n\n# --------------------------------------------------------------------- the pages\n@pytest.mark.parametrize("page", ["nodes.html", "blocks.html", "text.html"])\ndef test_pages_exist_and_load(api, page):\n    assert (STATIC / page).exists()\n    status = urllib.request.urlopen(api + "/" + page.replace(".html", ""), timeout=10).status\n    assert status == 200\n\n\n@pytest.mark.parametrize("page", ["nodes.html", "blocks.html"])\ndef test_editors_use_the_schema_instead_of_hardcoded_tables(page):\n    source = (STATIC / page).read_text(encoding="utf-8")\n    assert "/api/schema" in source\n    # The old hand-written tables are gone: a new feature is a catalogue entry.\n    assert "actionsToDsl" not in source\n    assert "workspaceToDsl" not in source\n\n\ndef test_every_page_javascript_parses():\n    node = shutil_which("node")\n    tool = ROOT / "tools" / "check_javascript.py"\n    if node is None:\n        pytest.skip("node is not installed")\n    if not tool.exists():\n        pytest.skip("tools/ is not part of this copy of the project")\n    result = subprocess.run([sys.executable, str(tool)], capture_output=True, text=True)\n    assert result.returncode == 0, result.stdout + result.stderr\n\n\ndef shutil_which(name):\n    import shutil\n    return shutil.which(name)\n',
    "tests/test_validation.py": r"""# Semantic checks shared by the DSL and the text syntax.
#
# aiogram calls the first handler whose filters match and returns, so two
# handlers with the same filters are not branches - the second is dead code that
# the author cannot see. A button that calls a command nobody handles looks fine
# in the editor and does nothing in Telegram: that is a warning, not an error,
# because the bot still runs.

import pytest

from tgblocks.dsl import compile_source
from tgblocks.dsl.parser import DSLParseError, parse
from tgblocks.textlang import compile_text, parse_text


def dsl(body: str, token: str = 'bot token "1:x"\n\n') -> str:
    return token + body


# ------------------------------------------------------------------- duplicates
@pytest.mark.parametrize(
    "body",
    [
        "on photo:\n    send \"a\"\non photo:\n    send \"b\"\n",
        "on message:\n    send \"a\"\non message:\n    send \"b\"\n",
        "on any:\n    send \"a\"\non any:\n    send \"b\"\n",
        'on message "x":\n    send "a"\non message "x":\n    send "b"\n',
        "on sticker:\n    send \"a\"\non sticker:\n    send \"b\"\n",
    ],
)
def test_two_handlers_with_the_same_filter_are_refused(body):
    with pytest.raises(DSLParseError) as info:
        parse(dsl(body))
    assert "never run" in info.value.message
    assert info.value.hint


@pytest.mark.parametrize(
    "body",
    [
        # Different patterns are different filters: both stay.
        'on message "x":\n    send "a"\non message "y":\n    send "b"\n',
        # A pattern filter narrows the plain text handler, so this is fine.
        'on message "x":\n    send "a"\non message:\n    send "b"\n',
        # Different observers never compete.
        'on message:\n    send "a"\non edited:\n    send "b"\n',
        # A command handler and a text handler are different filters.
        'on /start:\n    send "a"\non message:\n    send "b"\n',
        # The catch-all is a different filter from F.text.
        'on message:\n    send "a"\non any:\n    send "b"\n',
    ],
)
def test_handlers_that_can_all_run_are_allowed(body):
    spec = parse(dsl(body))
    assert len(spec.handlers) == 2


def test_duplicates_are_refused_in_the_text_syntax_too():
    with pytest.raises(DSLParseError) as info:
        parse_text('token("1:x")\n\non.photo():\n    send("a")\n\non.photo():\n'
                   '    send("b")\n')
    assert "never run" in info.value.message


# ------------------------------------------------------------------ dead buttons
def test_button_to_a_missing_command_is_reported_as_a_warning():
    spec = parse(dsl(
        'on /start:\n    send "menu"\n    buttons:\n        "Help" -> /help\n'
    ))
    assert len(spec.warnings) == 1
    assert "/help" in spec.warnings[0]
    # A warning must not stop the build: the bot still compiles.
    assert "async def start" in compile_source(dsl(
        'on /start:\n    send "menu"\n    buttons:\n        "Help" -> /help\n'
    ))


def test_button_to_an_existing_command_is_quiet():
    spec = parse(dsl(
        'on /start:\n    send "menu"\n    buttons:\n        "Help" -> /help\n\n'
        'on /help:\n    send "here"\n'
    ))
    assert spec.warnings == []


def test_warning_points_at_the_button_line():
    spec = parse(dsl(
        'on /start:\n    send "menu"\n    buttons:\n        "Gone" -> /gone\n'
    ))
    assert "line 6" in spec.warnings[0]


def test_dead_button_in_the_text_syntax():
    spec = parse_text('token("1:x")\n\non.command("/start"):\n    send("m")\n'
                      '    button("Help", "/help")\n')
    assert spec.warnings and "/help" in spec.warnings[0]


def test_warning_for_a_button_nested_in_a_condition():
    spec = parse(dsl(
        'on /start:\n    when text contains "a":\n        send "x"\n'
        '        buttons:\n            "Two" -> /two\n'
    ))
    assert spec.warnings and "/two" in spec.warnings[0]


# ------------------------------------------------------------------- regressions
def test_top_level_pass_in_the_text_syntax_is_not_a_crash():
    # This used to raise NameError: name 'actions' is not defined.
    code = compile_text('pass\ntoken("1:x")\n\non.command("/a"):\n    send("x")\n')
    assert "async def a" in code


def test_blank_text_syntax_error_is_reported_not_raised():
    with pytest.raises(DSLParseError) as info:
        parse_text('token("1:x")\n')
    assert "event" in info.value.message or "handler" in info.value.message
""",
    "tests/test_whitespace.py": r"""# Whitespace around service values: a pasted proxy often arrives with a leading
# tab or a trailing space ("\tsocks4://1.2.3.4:1080"), and that silently breaks
# the connection while looking correct in the field.

import pytest

from botkit import Harness
from tgblocks.convert import board_to_spec, spec_to_nodes, spec_to_text
from tgblocks.dsl import compile_source
from tgblocks.dsl.parser import parse
from tgblocks.textlang import parse_text


def test_the_dsl_strips_the_token_and_the_proxy():
    spec = parse('bot token "  1:ABC  "\nbot proxy "  socks5://1.2.3.4:1080  "\n'
                 'bot name "  с пробелами  "\n\non /start:\n    send "hi"\n')
    assert spec.token == "1:ABC"
    assert spec.proxy == "socks5://1.2.3.4:1080"
    # A bot name is a display string: its spaces are the author's business.
    assert spec.name == "  с пробелами  "


def test_the_dsl_strips_a_tab_that_comes_with_a_paste():
    spec = parse('bot token "1:ABC"\nbot proxy "\tsocks4://171.245.71.144:1086"\n\n'
                 'on /start:\n    send "hi"\n')
    assert spec.proxy == "socks4://171.245.71.144:1086"
    # The generated bot must carry the clean value.
    code = compile_source('bot token "1:ABC"\nbot proxy "\tsocks4://171.245.71.144:1086"\n'
                          '\n\non /start:\n    send "hi"\n')
    assert 'os.environ.get("TG_PROXY", "socks4://171.245.71.144:1086")' in code


def test_webhook_values_are_stripped_too():
    spec = parse('bot token "1:x"\nbot webhook " https://e.com/hook "\n'
                 'bot webhook_path " /hook "\n\non /start:\n    send "hi"\n')
    assert spec.webhook == "https://e.com/hook"
    assert spec.webhook_path == "/hook"


def test_a_board_with_a_padded_token_produces_clean_text():
    spec = parse_text('token("  1:ABC  ")\n\non.command("/start"):\n    send("hi")\n')
    board = spec_to_nodes(spec)
    # Simulate the value as it sits in the editor: with a stray tab.
    board["nodes"][board["rootId"]]["props"]["token"] = "\t1:ABC\t"
    board["nodes"][board["rootId"]]["props"]["proxy"] = " socks4://1.2.3.4:1080 "
    rebuilt = board_to_spec(board)
    assert rebuilt.token == "1:ABC"
    assert rebuilt.proxy == "socks4://1.2.3.4:1080"
    assert 'token("1:ABC")' in spec_to_text(rebuilt)
    assert 'proxy("socks4://1.2.3.4:1080")' in spec_to_text(rebuilt)


def test_text_syntax_token_is_stripped(monkeypatch):
    monkeypatch.delenv("TG_BOT_TOKEN", raising=False)
    spec = parse_text('token("  1:ABC  ")\n\non.command("/start"):\n    send("hi")\n')
    assert spec.token == "1:ABC"
""",
}
# END GENERATED FILE PAYLOAD

NEXT_STEPS = r"""Next steps
----------
  cd {name}
  python -m venv .venv
  .venv\Scripts\activate              (Linux/macOS: source .venv/bin/activate)
  pip install -e ".[dev]"
  pytest -q
  tgblocks visual
  tgblocks run examples/hello.tg --dry-run
"""


def create_project(root: str = ".") -> Path:
    # Write every file from FILES under `root` and return the resolved path.
    base = Path(root).expanduser().resolve()
    for relative_path, content in FILES.items():
        target = base / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        # newline="\n" keeps the generated project identical to the repository on
        # every platform, which is what tests/test_scaffold.py compares.
        target.write_text(content, encoding="utf-8", newline="\n")
    return base


def _tree_lines(directory: Path, prefix: str = "") -> List[str]:
    # ASCII tree so it prints on any Windows console codepage.
    entries = sorted(
        directory.iterdir(), key=lambda item: (item.is_file(), item.name.lower())
    )
    lines: List[str] = []
    for index, entry in enumerate(entries):
        last = index == len(entries) - 1
        connector = "`-- " if last else "|-- "
        lines.append(prefix + connector + entry.name + ("/" if entry.is_dir() else ""))
        if entry.is_dir():
            lines.extend(_tree_lines(entry, prefix + ("    " if last else "|   ")))
    return lines


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    project = create_project(target)
    print("")
    print("tgblocks scaffold created in: {0}".format(project))
    print("")
    print(project.name + "/")
    for line in _tree_lines(project):
        print(line)
    print("")
    print(NEXT_STEPS.format(name=project.name))
