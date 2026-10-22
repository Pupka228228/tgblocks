# Parser for the tgblocks indentation-based DSL.
#
# The grammar is deliberately boring:
#
#     bot token "123456:ABC"
#     bot name "Hello bot"
#
#     on /start:
#         send "Hello!"
#         buttons:
#             "Help" -> /help
#             "Docs" -> url "https://example.com"
#
#     on message:
#         when text contains "hi":
#             send "Hi there!"
#         else:
#             send "Try /help"
#
#     on message "hi", "hello":        # only these exact texts
#         send "Hi there!"
#
# Everything a bot can do is described in tgblocks.model; this module only turns
# text into that AST. A new action or event therefore costs nothing here.
#
# Every structural error becomes a DSLParseError that carries the line number,
# the offending source line and a short hint - beginners should never see a
# traceback from this module.

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Optional, Tuple

from ..model import (
    ACTIONS_BY_KIND,
    BindError,
    EventSpec,
    action_for,
    bind_arguments,
    coerce,
    event_for,
)

__all__ = [
    "Action",
    "BotSpec",
    "Button",
    "Buttons",
    "Condition",
    "DSLParseError",
    "Handler",
    "When",
    "parse",
    "parse_file",
    "validate",
]

# Which action families a handler of this event can run. A command handler also
# answers its own inline button, so it can do callback things too.
FAMILY_EXTRA = {"command": ("callback",)}


class DSLParseError(Exception):
    # A syntax or semantic error inside a .tg file.

    def __init__(
        self,
        message: str,
        line: int = 1,
        column: int = 1,
        source_line: str = "",
        hint: str = "",
    ) -> None:
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.source_line = source_line
        self.hint = hint

    def render(self, filename: str = "<dsl>") -> str:
        # Compiler-style diagnostic with a caret pointing at the column.
        head = "{0}:{1}:{2}: error: {3}".format(filename, self.line, self.column, self.message)
        if not self.source_line:
            text = head
        else:
            gutter = "{0:>4} | ".format(self.line)
            caret = " " * (len(gutter) + max(self.column - 1, 0)) + "^"
            text = "\n".join([head, gutter + self.source_line, caret])
        if self.hint:
            text += "\n  hint: {0}".format(self.hint)
        return text

    def __str__(self) -> str:
        return self.render()


# --------------------------------------------------------------------- the AST
@dataclass
class Button:
    label: str
    kind: str = "none"  # "command" | "url" | "web_app" | "contact" | "location" | "none"
    target: Optional[str] = None
    line: int = 0


@dataclass
class Buttons:
    style: str  # "inline" | "reply"
    items: List[Button]
    line: int = 0


@dataclass
class Action:
    # One leaf action: its kind comes from the catalogue, its params are already
    # coerced (numbers are numbers, flags are bools, lists are tuples).
    kind: str
    params: Dict[str, Any] = field(default_factory=dict)
    line: int = 0

    def get(self, name: str, default: Any = "") -> Any:
        value = self.params.get(name, default)
        return default if value is None else value

    @property
    def text(self) -> str:
        return str(self.get("text", ""))


@dataclass
class Condition:
    op: str  # == | != | contains | startswith | endswith
    value: str
    line: int = 0
    values: Tuple[str, ...] = ()
    # What is compared: the message text, or the number the interactive emoji
    # landed on (`when dice == 6`).
    source: str = "text"


@dataclass
class When:
    condition: Condition
    then: List[object]
    orelse: List[object]
    line: int = 0


@dataclass
class Handler:
    kind: str  # a catalogue event kind: command | text | photo | ... | callback | state
    actions: List[object]
    params: Dict[str, Any] = field(default_factory=dict)
    line: int = 0

    # Convenience views used by the converters and the tests.
    @property
    def command(self) -> Optional[str]:
        return self.params.get("command") or None

    @property
    def patterns(self) -> Tuple[str, ...]:
        return tuple(self.params.get("patterns") or ())

    @property
    def data(self) -> str:
        return str(self.params.get("data") or "")

    @property
    def state(self) -> str:
        return str(self.params.get("state") or "")

    @property
    def chat(self) -> str:
        return str(self.params.get("chat") or "")

    @property
    def from_user(self) -> int:
        return int(self.params.get("from_user") or 0)

    @property
    def regex(self) -> str:
        return str(self.params.get("regex") or "")


@dataclass
class BotSpec:
    token: Optional[str] = None
    name: str = "tgblocks bot"
    proxy: str = ""
    handlers: List[Handler] = field(default_factory=list)
    token_line: int = 0
    # FSM: the dialogue steps, in declaration order.
    states: List[str] = field(default_factory=list)
    # Webhook mode: when set, the generated bot serves it instead of polling.
    webhook: str = ""
    webhook_path: str = "/webhook"
    webhook_secret: str = ""
    # Non-fatal findings (a button that leads nowhere): reported by `tgblocks
    # check` and in the editor, but never blocks a build - the bot still runs.
    warnings: List[str] = field(default_factory=list)


@dataclass
class _Token:
    line: int
    indent: int
    text: str
    raw: str


_DIRECTIVE_RE = re.compile(r"^bot\s+(token|name|proxy|webhook|webhook_path|webhook_secret)\s+(.+)$")
_ON_RE = re.compile(r"^on\s+(.+?)\s*:\s*$")
_SEND_RE = re.compile(r"^send\s+(.+)$")
_BUTTONS_RE = re.compile(r"^buttons(?:\s+(inline|reply))?\s*:\s*$")
_WHEN_RE = re.compile(r"^(?:when|if)\s+(.+?)\s*:\s*$")
_COND_RE = re.compile(r"^(text|dice)\s*(==|!=|contains|startswith|endswith)\s+(.+)$")
_DICE_OPS = ("==", "!=")
_BUTTON_RE = re.compile(
    r"^(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*')(?:\s*->\s*(.+))?$"
)
_COMMAND_RE = re.compile(r"^/[A-Za-z0-9_]{1,32}$")
_STATE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,31}$")

# Every action keyword the DSL understands, including the aliases.
_ACTION_WORDS = set(ACTIONS_BY_KIND)
for _alias in ("pass", "photo", "document", "video", "animation", "audio", "voice",
               "sticker", "location", "contact", "poll", "dice", "alert", "state"):
    _ACTION_WORDS.add(_alias)


def _tokenize(source: str) -> List[_Token]:
    # Turn raw text into (line, indent, stripped text) triples, dropping blanks
    # and full-line comments. Leading tabs are rejected: they break alignment.
    tokens: List[_Token] = []
    for line_number, raw in enumerate(source.splitlines(), start=1):
        leading = raw[: len(raw) - len(raw.lstrip())]
        if "\t" in leading:
            raise DSLParseError(
                "tabs are not allowed for indentation",
                line_number,
                1,
                raw,
                "use spaces instead, 4 per level",
            )
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        tokens.append(_Token(line_number, indent, stripped, raw))
    return tokens


def lex_arguments(text: str) -> List[Tuple[str, bool]]:
    """Split `"a" b=1 "c d" 2` into [(value, is_bare)] pairs.

    Quoted strings are unescaped with ast.literal_eval (so \\n works), bare words
    stay bare. Commas that separate list items are dropped.
    """
    items: List[Tuple[str, bool]] = []
    index = 0
    length = len(text)
    while index < length:
        while index < length and text[index].isspace():
            index += 1
        if index >= length:
            break
        char = text[index]
        if char in "\"'":
            quote = char
            start = index
            index += 1
            while index < length:
                if text[index] == "\\":
                    index += 2
                    continue
                if text[index] == quote:
                    index += 1
                    break
                index += 1
            raw = text[start:index]
            try:
                value = ast.literal_eval(raw)
            except (SyntaxError, ValueError):
                raise DSLParseError(
                    "cannot read the text {0}".format(raw[:40]),
                    hint="check that the closing quote is there and escapes are valid",
                ) from None
            if not isinstance(value, str):
                raise DSLParseError("the value must be text")
            items.append((value, False))
            continue
        start = index
        while index < length and not text[index].isspace():
            index += 1
        word = text[start:index]
        if word.strip(",") == "":
            continue
        items.append((word, True))
    return items


def _unquote_single(raw: str) -> Optional[str]:
    # `"text"` or `'text'` -> text; None when the value is not quoted.
    text = raw.strip()
    if len(text) < 2 or text[0] not in "\"'" or text[-1] != text[0]:
        return None
    try:
        value = ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return None
    return value if isinstance(value, str) else None


class _Parser:
    def __init__(self, source: str, filename: str = "<dsl>") -> None:
        # Editors on Windows love to add a UTF-8 BOM: it is not part of the DSL.
        source = source.lstrip("\ufeff")
        # DSL embedded in a Python string usually carries the indentation of the
        # code around it: drop the common margin so both styles parse the same.
        lines = source.splitlines()
        margin = None
        for line in lines:
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip(" "))
            margin = indent if margin is None else min(margin, indent)
        if margin:
            lines = [line[margin:] for line in lines]
        source = "\n".join(lines)
        self.filename = filename
        self.source_lines = source.splitlines()
        self.tokens = _tokenize(source)
        self.pos = 0

    # ------------------------------------------------------------------ errors
    def _fail(self, message: str, token: _Token, hint: str = "") -> NoReturn:
        raw = ""
        if 0 < token.line <= len(self.source_lines):
            raw = self.source_lines[token.line - 1]
        column = len(raw) - len(raw.lstrip(" ")) + 1 if raw else 1
        raise DSLParseError(message, token.line, column, raw, hint)

    def _fail_line(self, line: int, message: str, hint: str = "") -> NoReturn:
        raw = self.source_lines[line - 1] if 0 < line <= len(self.source_lines) else ""
        column = len(raw) - len(raw.lstrip(" ")) + 1 if raw else 1
        raise DSLParseError(message, line, column, raw, hint)

    def _unquote(self, raw: str, token: _Token, what: str = "text") -> str:
        text = raw.strip()
        if len(text) < 2 or text[0] not in "\"'" or text[-1] != text[0]:
            self._fail(
                "expected a quoted {0}".format(what),
                token,
                'wrap the value in double quotes, for example: "Hello!"',
            )
        value = _unquote_single(text)
        if value is None:
            self._fail(
                "cannot read the {0}".format(what),
                token,
                "check that the closing quote is there and escapes such as \\n are valid",
            )
        return value

    # ------------------------------------------------------------------- entry
    def parse(self) -> BotSpec:
        bot = BotSpec()
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if token.indent != 0:
                self._fail(
                    "unexpected indentation",
                    token,
                    "this line is indented, but no block is open here",
                )
            if token.text.startswith("bot "):
                self._parse_directive(bot, token)
            elif token.text.startswith("on "):
                bot.handlers.append(self._parse_handler(token, bot))
            elif token.text.startswith("state ") and not token.text.endswith(":"):
                name = token.text[len("state "):].strip()
                self._add_state(bot, name, token)
                self.pos += 1
            elif token.text.startswith("else"):
                self._fail(
                    "'else' without 'when'",
                    token,
                    "put 'else:' directly under a 'when ...:' line",
                )
            else:
                self._fail(
                    "unknown statement: {0!r}".format(token.text),
                    token,
                    'expected `bot token "..."`, `bot name "..."` or `on /command:`',
                )

        if bot.token is None:
            self._fail_line(
                1,
                "the bot token is missing",
                'add `bot token "123456:ABC"` as the first line of the file',
            )
        if not bot.handlers:
            self._fail_line(
                1,
                "the bot has no handlers",
                "add at least one block such as `on /start:`",
            )
        self._check(bot)
        return bot

    def _check(self, bot: BotSpec) -> None:
        validate(bot, fail=lambda message, line, hint: self._fail_line(line, message, hint))
        # A handler for a dialogue step needs that step to exist.
        for handler in bot.handlers:
            state = handler.state
            if handler.kind == "state" and state and state not in bot.states:
                self._fail_line(
                    handler.line,
                    "unknown state {0!r}".format(state),
                    "declare it first: `state {0}`".format(state),
                )

    def _add_state(self, bot: BotSpec, name: str, token: _Token) -> None:
        if not _STATE_RE.match(name or ""):
            self._fail(
                "invalid state name {0!r}".format(name),
                token,
                "use letters, digits and _ (for example: `state order`)",
            )
        if name in bot.states:
            self._fail(
                "duplicate state {0!r}".format(name),
                token,
                "each dialogue step is declared once",
            )
        bot.states.append(name)

    # --------------------------------------------------------------- statements
    def _parse_directive(self, bot: BotSpec, token: _Token) -> None:
        match = _DIRECTIVE_RE.match(token.text)
        if match is None:
            self._fail(
                "unsupported bot directive",
                token,
                'only `bot token`, `bot name`, `bot proxy` and `bot webhook` exist',
            )
        key = match.group(1)
        labels = {"token": "token", "name": "bot name", "proxy": "proxy URL",
                  "webhook": "webhook URL", "webhook_path": "webhook path",
                  "webhook_secret": "webhook secret"}
        value = self._unquote(match.group(2), token, labels[key])
        # A pasted value often carries a stray space or tab: it is never
        # meaningful in a token, a URL or a path, and it silently breaks them.
        if key != "name":
            value = value.strip()
        if key == "proxy":
            if not value.startswith(("socks5://", "socks4://", "http://", "https://")):
                self._fail(
                    "proxy must start with socks5://, socks4://, http:// or https://",
                    token,
                    'for example: bot proxy "socks5://127.0.0.1:1080"',
                )
            bot.proxy = value
        elif key == "webhook":
            if not value.startswith(("http://", "https://")):
                self._fail(
                    "the webhook URL must start with http:// or https://",
                    token,
                    'for example: bot webhook "https://example.com/webhook"',
                )
            bot.webhook = value
        elif key == "webhook_path":
            if not value.startswith("/"):
                self._fail("the webhook path must start with /", token,
                           'for example: bot webhook_path "/hook"')
            bot.webhook_path = value
        elif key == "webhook_secret":
            bot.webhook_secret = value
        elif key == "token":
            if bot.token is not None:
                self._fail(
                    "duplicate `bot token`", token, "the token can only be declared once"
                )
            bot.token = value
            bot.token_line = token.line
        else:
            bot.name = value
        self.pos += 1

    # ------------------------------------------------------------------- events
    def _parse_handler(self, token: _Token, bot: Optional[BotSpec] = None) -> Handler:
        match = _ON_RE.match(token.text)
        if match is None:
            self._fail(
                "invalid event declaration",
                token,
                "write `on /command:` or `on message:`",
            )
        target = match.group(1).strip()
        self.pos += 1
        actions = self._parse_block(token)
        try:
            items = lex_arguments(target)
        except DSLParseError:
            self._fail("cannot read the event", token, "write `on /command:`")
        if not items:
            self._fail("empty event", token, "write `on /command:` or `on message:`")

        first_value, first_bare = items[0]
        rest = items[1:]

        # on /start: - the command itself is the target.
        if first_bare and first_value.startswith("/"):
            if not _COMMAND_RE.match(first_value):
                self._fail("invalid command {0!r}".format(first_value), token)
            params = self._bind_event(self._event("command"), rest, token)
            params["command"] = first_value
            return Handler(kind="command", actions=actions, params=params, line=token.line)

        spec = event_for(first_value) if first_bare else None
        if spec is None and first_bare is False:
            # on "a", "b": with no event word means "exactly these texts".
            spec = event_for("text")
            rest = items
        if spec is None:
            self._fail(
                "invalid event {0!r}".format(first_value),
                token,
                "use `on /command:`, `on message:`, `on photo:`, `on callback:`, "
                "`on state <step>:` or `on any:`",
            )
        params = self._bind_event(spec, rest, token)
        if spec.key_param == "command":
            command = str(params.get("command") or "").strip()
            if not _COMMAND_RE.match(command):
                self._fail(
                    "the command must look like /start",
                    token,
                    'write `on /start:` instead of `on command "start":`',
                )
        if spec.kind == "state":
            state = str(params.get("state") or "").strip()
            if not state:
                self._fail("a state handler needs a step", token,
                           "write `on state order:` after `state order`")
        return Handler(kind=spec.kind, actions=actions, params=params, line=token.line)

    def _event(self, kind: str) -> EventSpec:
        spec = event_for(kind)
        assert spec is not None, kind
        return spec

    def _bind_event(self, spec: EventSpec, items, token: _Token) -> Dict[str, Any]:
        try:
            return bind_arguments(spec, items)
        except BindError as error:
            self._fail(error.message, token, error.hint or "")

    # ------------------------------------------------------------------- blocks
    def _parse_block(self, header: _Token) -> List[object]:
        if self.pos >= len(self.tokens) or self.tokens[self.pos].indent <= header.indent:
            self._fail(
                "expected an indented block",
                header,
                'indent the block by 4 spaces, for example:     send "Hi"',
            )
        block_indent = self.tokens[self.pos].indent
        nodes: List[object] = []
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if token.indent < block_indent:
                break
            if token.indent > block_indent:
                self._fail(
                    "unexpected indentation",
                    token,
                    "this line is deeper than the block it belongs to",
                )
            nodes.append(self._parse_statement(token, block_indent))
        return nodes

    def _parse_statement(self, token: _Token, indent: int) -> object:
        text = token.text

        if text == "else:" or text.startswith("else "):
            self._fail(
                "'else' without 'when'",
                token,
                "put `else:` under a `when ...:` line at the same indentation",
            )

        if text == "send" or text.startswith("send "):
            return self._parse_send(token)

        if text.startswith("buttons"):
            return self._parse_buttons_block(token)

        if text.startswith("when ") or text.startswith("if "):
            return self._parse_when(token, indent)

        word, _, rest = text.partition(" ")
        word = word.rstrip(":")
        spec = action_for(word)
        if spec is None:
            self._fail(
                "unknown statement: {0!r}".format(text),
                token,
                "inside a block use `send`, `buttons`, `when`, `delete`, "
                "`send_photo`, `delay`, `set_state` or `pass`",
            )
        if spec.kind == "otherwise":
            self._fail(
                "'else' without 'when'",
                token,
                "put `else:` under a `when ...:` line at the same indentation",
            )
        if spec.kind == "when":
            self._fail("use `when text contains \"...\":`", token,
                       "the short form is `when <condition>:`")
        try:
            params = bind_arguments(spec, lex_arguments(rest))
        except BindError as error:
            self._fail(error.message, token, error.hint or "")
        self.pos += 1
        return Action(kind=spec.kind, params=params, line=token.line)

    def _parse_send(self, token: _Token) -> Action:
        match = _SEND_RE.match(token.text)
        if match is None:
            self._fail("missing text after `send`", token, 'example: send "Hello!"')
        value = self._unquote(match.group(1), token)
        self.pos += 1
        return Action(kind="send", params={"text": value}, line=token.line)

    def _parse_when(self, token: _Token, indent: int) -> When:
        match = _WHEN_RE.match(token.text)
        if match is None:
            self._fail("invalid condition", token, 'example: `when text == "hi":`')
        condition = self._parse_condition(match.group(1), token)
        self.pos += 1
        then = self._parse_block(token)
        orelse: List[object] = []
        if self.pos < len(self.tokens):
            following = self.tokens[self.pos]
            if following.indent == indent and following.text == "else:":
                self.pos += 1
                orelse = self._parse_block(following)
        return When(condition=condition, then=then, orelse=orelse, line=token.line)

    def _parse_buttons_block(self, token: _Token) -> Buttons:
        match = _BUTTONS_RE.match(token.text)
        if match is None:
            self._fail(
                "invalid buttons block",
                token,
                "write `buttons:` for inline buttons or `buttons reply:` for a keyboard",
            )
        style = match.group(1) or "inline"
        self.pos += 1
        return Buttons(style=style, items=self._parse_buttons(token, style), line=token.line)

    def _parse_buttons(self, header: _Token, style: str) -> List[Button]:
        if self.pos >= len(self.tokens) or self.tokens[self.pos].indent <= header.indent:
            self._fail(
                "the buttons block is empty",
                header,
                'add a row such as `"Help" -> /help`',
            )
        item_indent = self.tokens[self.pos].indent
        items: List[Button] = []
        while self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            if token.indent < item_indent:
                break
            if token.indent > item_indent:
                self._fail("unexpected indentation", token, "each button sits on its own line")
            items.append(self._parse_button(token, style))
            self.pos += 1
        return items

    def _parse_button(self, token: _Token, style: str) -> Button:
        match = _BUTTON_RE.match(token.text)
        if match is None:
            self._fail(
                "invalid button",
                token,
                'write `"Label" -> /command`, `"Label" -> url "https://..."` '
                'or plain `"Label"` for reply buttons',
            )
        label = self._unquote(match.group(1), token, "button label")
        raw_target = (match.group(2) or "").strip()
        button = Button(label=label, line=token.line)
        if not raw_target:
            return button
        if style == "reply":
            # Reply buttons can ask for a phone number or a location.
            if raw_target in ("contact", "location"):
                button.kind = raw_target
                return button
            self._fail(
                "reply buttons cannot have a target",
                token,
                'the label itself is sent as text, so drop the `-> ...` part '
                "(or use `-> contact` / `-> location`)",
            )
        if raw_target.startswith("url"):
            url = self._unquote(raw_target[3:], token, "URL")
            if not url.startswith(("http://", "https://")):
                self._fail("URL buttons must start with http:// or https://", token)
            button.kind = "url"
            button.target = url
        elif raw_target.startswith("web_app"):
            url = self._unquote(raw_target[len("web_app"):], token, "URL")
            if not url.startswith("https://"):
                self._fail("web app buttons need an https:// URL", token)
            button.kind = "web_app"
            button.target = url
        elif raw_target.startswith("/"):
            if not _COMMAND_RE.match(raw_target):
                self._fail("invalid command {0!r}".format(raw_target), token)
            button.kind = "command"
            button.target = raw_target
        else:
            self._fail(
                "invalid button target {0!r}".format(raw_target),
                token,
                'use `-> /command`, `-> url "https://..."` or `-> web_app "https://..."`',
            )
        return button

    def _parse_condition(self, text: str, token: _Token) -> Condition:
        extra = []
        if ";" in text:
            chunks = text.split(";")
            text = chunks[0]
            for chunk in chunks[1:]:
                chunk = chunk.strip()
                if not (chunk.startswith('"') or chunk.startswith("'")):
                    self._fail(
                        "each extra condition value must be a quoted string",
                        token,
                        'write when text contains "a";"b":',
                    )
                extra.append(self._unquote(chunk, token, "comparison value"))
        match = _COND_RE.match(text.strip())
        if match is None:
            self._fail(
                "unsupported condition",
                token,
                'use `text == "..."`, `text contains "..."` or `dice == 6`',
            )
        source = match.group(1)
        op = match.group(2)
        if source == "dice":
            if op not in _DICE_OPS:
                self._fail(
                    "для интерактивного эмодзи подходят только == и !=",
                    token,
                    'сравни число, которое выпало: `when dice == 6:`',
                )
            raw = match.group(3).strip()
            if not raw.lstrip("-").isdigit():
                self._fail(
                    "для интерактивного эмодзи нужно число",
                    token,
                    'кубик даёт 1-6, дартс - 1-6, слоты - 1-64: `when dice == 6:`',
                )
            return Condition(op=op, value=raw, line=token.line, source="dice")
        # Several values mean "any of them": when text contains "a", "b":
        parts = [part for part in _split_items(match.group(3)) if part]
        if not parts:
            self._fail(
                "the condition has no value",
                token,
                'add the text to compare with, for example: when text contains "hi"',
            )
        value = self._unquote(parts[0], token, "comparison value")
        for part in parts[1:]:
            extra.append(self._unquote(part, token, "comparison value"))
        return Condition(op=op, value=value, line=token.line,
                         values=tuple(extra), source=source)


def _split_items(text: str) -> List[str]:
    # Split on top-level commas, keeping quoted strings (and their commas) whole.
    parts: List[str] = []
    current: List[str] = []
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
        if char == ",":
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        parts.append(tail)
    return parts


# ---------------------------------------------------------------- shared checks
def _walk_actions(actions):
    # Every action, including the ones nested inside `when` and inside a send.
    for node in actions:
        yield node
        if isinstance(node, When):
            for child in _walk_actions(node.then):
                yield child
            for child in _walk_actions(node.orelse):
                yield child


def filter_signature(handler: Handler) -> Tuple[str, str]:
    # Two handlers with the same signature can never both run: aiogram calls the
    # first matching handler and returns. Everything that narrows the filter is
    # part of the signature, so a chat=group variant is a different handler.
    spec = event_for(handler.kind)
    observer = spec.observer if spec else "message"
    parts: List[str] = []
    if spec and spec.filter:
        parts.append(spec.filter)
    if handler.kind == "command":
        parts = ['Command("{0}")'.format((handler.command or "").lstrip("/"))]
    elif handler.patterns:
        parts.append("F.text.in_({0})".format(", ".join(handler.patterns)))
    elif handler.kind == "callback" and handler.data:
        parts.append('F.data == "{0}"'.format(handler.data))
    elif handler.kind == "state":
        parts.append("StateFilter({0})".format(handler.state))
    if handler.chat:
        parts.append('F.chat.type == "{0}"'.format(handler.chat))
    if handler.from_user:
        parts.append("F.from_user.id == {0}".format(handler.from_user))
    if handler.regex:
        parts.append('F.text.regexp("{0}")'.format(handler.regex))
    return observer, " & ".join(parts)


def validate(bot: BotSpec, fail=None) -> None:
    # Semantic checks that both front ends share: a command may be handled once,
    # two handlers may not claim the same filters, and a button must lead to a
    # handler that exists (otherwise it looks fine in the editor and does nothing
    # in Telegram).
    def boom(message: str, line: int, hint: str = "") -> NoReturn:
        if fail is not None:
            fail(message, line, hint)
        raise DSLParseError(message, line, 1, "", hint)

    seen_commands = set()
    seen_filters = {}
    for handler in bot.handlers:
        if handler.kind == "command":
            if handler.command in seen_commands:
                boom(
                    "duplicate handler for {0}".format(handler.command),
                    handler.line,
                    "a command can be handled once; branch inside it with `when`",
                )
            seen_commands.add(handler.command)
        key = filter_signature(handler)
        if key in seen_filters:
            boom(
                "this handler would never run: line {0} already handles the same "
                "messages".format(seen_filters[key]),
                handler.line,
                "merge them into one block, or branch inside it with `when`",
            )
        seen_filters[key] = handler.line

    bot.warnings = []
    commands = {
        handler.command for handler in bot.handlers
        if handler.kind == "command" and handler.command
    }
    for handler in bot.handlers:
        for node in _walk_actions(handler.actions):
            if isinstance(node, Buttons):
                for button in node.items:
                    if button.kind == "command" and button.target not in commands:
                        bot.warnings.append(
                            'line {0}: button "{1}" calls {2}, but no `on {2}:` block '
                            "exists".format(button.line, button.label, button.target)
                        )


def parse(source: str, filename: str = "<dsl>") -> BotSpec:
    # Parse DSL text into a BotSpec tree.
    return _Parser(source, filename).parse()


def parse_file(path: str) -> BotSpec:
    # Read `path` as UTF-8 (BOM tolerated) and parse it.
    file_path = Path(path)
    try:
        source = file_path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise FileNotFoundError("DSL file not found: {0}".format(file_path)) from None
    return parse(source, str(file_path))
