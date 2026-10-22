# Parser for the text syntax used by the browser text editor.
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
