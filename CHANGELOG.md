# Changelog

## 0.2.7

The screenshots and the demo GIF in the README were taken again against the current
editor, so they show what the reader will actually see. Nothing in the package changed.

## 0.2.6

Wording only: the documentation and the editor hints were read once more and tightened.
Nothing in the compiler or in the generated code changed.

## 0.2.5

The header and the browser tab title follow the interface language.

### Fixed

- "tgblocks nodes" in English and "tgblocks узлы" in Russian. Before this, `/nodes` and
  `/text` kept a Russian word in the corner even with English selected.

## 0.2.4

Small text edits in the documentation and the editor hints.

## 0.2.3

Documentation only. The package is installed from PyPI with one command, and the README
no longer suggests otherwise: the repository install is now described as "the newest
commit instead of the release".

## 0.2.2

Metadata only: the PyPI summary and the GitHub description became the same sentence,
"Visual editor for building Telegram bots on aiogram 3". The code is unchanged.

## 0.2.1

Metadata, tests and documentation. The generated aiogram code is unchanged.

### Changed

- **Minimum Python is now 3.10.** `aiogram` itself requires 3.10, so on 3.9 the
  `runtime` extra could only pull an old version that the suite could not cover. The
  CI matrix is 3.10, 3.11 and 3.13 on Windows and Linux.
- The PyPI summary is the same sentence as the README: three visual editors, not one.

### Fixed

- The test poll payload is built from the installed aiogram, so a new release that adds
  required `Poll` fields (3.31 added three) no longer turns the whole matrix red.
- `tools/qa_smoke.py` no longer hardcodes a Windows path: it works from any clone and on
  Linux.
- `tools/check_markdown.py` and `tools/qa_smoke.py` write UTF-8, so the Windows runner
  reports a failure instead of crashing on Russian output.

### Documentation

- README rewritten for a first-time visitor: a demo GIF, one install command, the three
  views as sections with screenshots, and actions and events as aligned code blocks.

## 0.2.0

The release that made the three editors agree with each other.

### Added

- **A single feature catalogue** (`src/tgblocks/model.py`): every action and event is
  described once, and the DSL parser, the text parser, the converters, the code
  generator and all three editors read it. `/api/schema` serves it to the pages, so a
  new block appears in `/nodes`, `/blocks` and `/text` without touching their code.
- **Media**: `send_document`, `send_video`, `send_animation`, `send_audio`,
  `send_voice`, `send_sticker`, `send_location`, `send_contact`, `send_poll`,
  `send_dice`.
- **Editing and answering**: `edit_text`, `answer_callback [alert]`.
- **Chat actions**: `pin [silent]`, `unpin`.
- **Moderation**: `ban_user`, `unban_user`, `mute_user` - without an ID they act on the
  sender of the message.
- **Dialogues (FSM)**: `state order`, `set_state`, `clear_state`, `on state order:`.
  The generated bot gets `StatesGroup` and a `MemoryStorage` dispatcher.
- **Events**: `on callback:`, `on callback "/data":`, `on inline_query:` with
  `inline_result`, `on chat_member:`, `on my_chat_member:`, `on poll_answer:`,
  `on channel_post:`, `on dice:`, `on pinned:`, `on web_app_data:`.
- **Filters** on any event: `chat=`, `from_user=`, `regex=`.
- **Webhook mode**: `bot webhook`, `bot webhook_path`, `bot webhook_secret`.
- **Keyboard buttons**: Web App buttons, and reply buttons that request a contact or a
  location.
- `tgblocks check` reports warnings, and the editors show them.
- `tools/check_javascript.py`, and tests that parse every page.

### Changed

- `tgblocks compile` writes code **without** the token; `--embed-token` restores the old
  behaviour. `tgblocks run` passes the token through the environment.
- Generated helpers are emitted only when a bot uses them, so a small bot stays small.
- The node editor no longer has its own JavaScript DSL writer: the board goes to the
  server, and one converter produces the shared text and the code.
- The block editor sends its Blockly workspace as XML; the server converts it back.
  Blocks are now chained with `<next>`, which fixes only the first handler being shown.
- `scaffold.py` is generated from the tree by `tools/build_scaffold.py` and checked by
  `tests/test_scaffold.py`.

### Fixed

- **Security**: the local server refused nothing from other origins. It now checks
  `Host`, `Origin` and `Sec-Fetch-Site`, requires `application/json` bodies, and needs
  `--allow-remote` before `--host` exposes it. Requests from a foreign page could start
  arbitrary code through `/api/run`.
- Two handlers with the same filters are refused instead of silently leaving the second
  one dead.
- A button that calls a command nobody handles produces a warning.
- `pass` at the top level of the text syntax no longer raises `NameError`.
- The server no longer reloads the DSL modules on every request (that replaced the
  exception classes under a running `except`).
- On Windows, a second `tgblocks visual` can no longer bind the same port and leave the
  old code answering.
- `Tuple` is imported where it is annotated; the long-line wrapper, the entity escaping
  and the `_1`-suffixed handler names are consistent.
- **Filters and magic filters**: `Command("start") & F.chat.type == "private"` crashed
  with `TypeError: unsupported operand type(s) for &: 'Command' and 'bool'`. Filters are
  now separate decorator arguments, and every combination is run against aiogram in
  `tests/test_filters.py`.
- **The three views stay in sync when a document is emptied**: clearing a canvas or the
  text sets a new revision with empty text, instead of leaving the old bot in the other
  views. A half-built canvas still keeps the last good text.
- **Editor pages no longer hang**: a missing page-local helper (`L`) threw at boot and
  left `/blocks` and `/text` on "Loading Blockly…"; `tools/check_javascript.py` now fails
  on a helper that is called but never defined.
- **The light theme was broken**: colours were hardcoded per rule, so only `--bg`/`--panel`
  changed. Every surface is a variable now (`--chip`, `--field`, `--log`, `--tok-*`), and
  the Blockly canvas follows the theme too.
- `/blocks?lang=ru` reloaded itself in a loop, because the page compared the language
  before the preference was read.
- Stray spaces or tabs around a pasted token, proxy or webhook URL are stripped instead of
  silently breaking the connection.

### Editor

- **Settings in every view**: ⚙ in the header switches the theme (dark/light) and the
  interface language (English by default, Russian optional). The choice is remembered and
  can be shared as `?theme=light&lang=ru`; the whole catalogue - block names, field
  captions, hints, drop-down values, status lines - is translated.
- **Typing is one-line everywhere again**, and every field has a caption, so a drop-down
  says what it is.
- **Two event filters are hidden** from the panel: "only these texts" and "matches a
  pattern". A `when` condition does the same job visibly. Values that come from the text
  view are kept and shown as a removable chip, so nothing is dropped silently.
- **Blockly ships with the package** (`static/vendor/blockly.js`), so the block editor
  works without internet; the CDN is only a fallback.
- The palette scrollbar is thin and vertical; a drag handle sets the panel width.
- The scrollbar, the fields and the node headers are correct in both themes.

## 0.1.0

First public shape: DSL, one code generator, three editors, no tests worth the name.
