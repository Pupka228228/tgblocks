# Compile a parsed tgblocks bot into readable aiogram 3 source code.
#
# The generator reads the catalogue in tgblocks.model: every action has an
# emitter family there, and every event knows its aiogram observer and filter.
# Generated helpers are emitted only when a bot uses them, so a small bot stays
# small and a bot with media does not carry unused code.

from __future__ import annotations

import json
import keyword
import re
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from ..model import ACTIONS_BY_KIND, EVENTS_BY_KIND, EventSpec
from .parser import (
    Action,
    BotSpec,
    Buttons,
    Condition,
    DSLParseError,
    Handler,
    When,
)

INDENT = "    "
LINE_WIDTH = 88

# Names used by the generated helpers: a command called /reply must not shadow them.
RESERVED = {
    "reply", "inline", "keyboard", "text_of", "media", "remove", "typing",
    "delay", "pin", "unpin", "edit_text", "answer_callback", "ban_user",
    "unban_user", "mute_user", "send_poll", "inline_result", "api",
    "dp", "bot", "main", "state", "Form", "logging", "asyncio", "os",
    "Bot", "Dispatcher", "F", "Command", "Message", "CallbackQuery",
}


def _literal(value: str) -> str:
    # Double-quoted Python literal, Cyrillic kept as is.
    return json.dumps(str(value), ensure_ascii=False)


def _tuple_literal(values) -> str:
    items = [_literal(item) for item in values]
    if not items:
        return "()"
    if len(items) == 1:
        return "({0},)".format(items[0])
    return "({0})".format(", ".join(items))


def _number(value) -> str:
    number = float(value)
    return str(int(number)) if number.is_integer() else str(number)


def _condition_expression(condition: Condition) -> str:
    if condition.source == "dice":
        # What the interactive emoji landed on, as a number.
        number = condition.value if condition.value.lstrip("-").isdigit() else "0"
        return "dice_value(event) {0} {1}".format(condition.op, number)
    text = "text_of(event)"
    lowered = "text_of(event).lower()"
    value = condition.value
    if condition.values:
        parts = []
        for item in (value,) + tuple(condition.values):
            piece = _condition_expression(
                Condition(op=condition.op, value=item, line=condition.line)
            )
            if piece not in parts:
                parts.append(piece)
        if condition.op == "!=":
            return " and ".join(parts)
        return " or ".join("({0})".format(item) for item in parts)
    if condition.op == "==":
        return "{0} == {1}".format(text, _literal(value))
    if condition.op == "!=":
        return "{0} != {1}".format(text, _literal(value))
    if condition.op == "contains":
        return "{0} in {1}".format(_literal(value.lower()), lowered)
    if condition.op == "startswith":
        return "{0}.startswith({1})".format(lowered, _literal(value.lower()))
    if condition.op == "endswith":
        return "{0}.endswith({1})".format(lowered, _literal(value.lower()))
    raise CodeGenError(
        "unsupported condition operator {0!r}".format(condition.op),
        line=condition.line,
    )


class CodeGenError(DSLParseError):
    # Raised when the DSL is syntactically valid but cannot become Python.
    pass


# ------------------------------------------------------------------- helpers
# Each helper is emitted only when a handler uses it. The first element is the
# name used to decide that; the body is plain Python.
HELPER_BODIES: Dict[str, str] = {
    "inline": '''def inline(*buttons) -> InlineKeyboardMarkup:
    # inline(("Help", "/help", "command"), ("Site", "https://example.com", "url"))
    rows = []
    for label, target, kind in buttons:
        if kind == "web_app":
            rows.append([InlineKeyboardButton(text=label, web_app=WebAppInfo(url=target))])
        elif kind == "url" or target.startswith(("http://", "https://")):
            rows.append([InlineKeyboardButton(text=label, url=target)])
        else:
            rows.append([InlineKeyboardButton(text=label, callback_data=target)])
    return InlineKeyboardMarkup(inline_keyboard=rows)''',
    "keyboard": '''def keyboard(*buttons) -> ReplyKeyboardMarkup:
    # keyboard(("Help", "text"), ("Phone", "contact")) - a reply keyboard
    rows = []
    for label, kind in buttons:
        if kind == "contact":
            rows.append([KeyboardButton(text=label, request_contact=True)])
        elif kind == "location":
            rows.append([KeyboardButton(text=label, request_location=True)])
        else:
            rows.append([KeyboardButton(text=label)])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)''',
    "text_of": '''def text_of(event) -> str:
    # Message and CallbackQuery both land here, so unwrap the message first.
    message = event.message if isinstance(event, CallbackQuery) else event
    return (message.text or "") if message is not None else ""''',
    "dice_value": '''def dice_value(event) -> int:
    # What the interactive emoji landed on; 0 when the message has none.
    message = event.message if isinstance(event, CallbackQuery) else event
    dice = getattr(message, "dice", None)
    return dice.value if dice is not None else 0''',
    "reply": '''async def reply(event, text, markup=None) -> None:
    # One call answers a plain message, an inline-button press or a chat event.
    if isinstance(event, CallbackQuery):
        if event.message is not None:
            await event.message.answer(text, reply_markup=markup)
        await event.answer()
    elif isinstance(event, Message):
        await event.answer(text, reply_markup=markup)
    else:
        await event.bot.send_message(event.chat.id, text, reply_markup=markup)''',
    "media": '''async def media(event, method, *args, **kwargs) -> None:
    # media(event, "answer_photo", "https://...", caption="...") - any send method
    message = event.message if isinstance(event, CallbackQuery) else event
    await getattr(message, method)(*args, **kwargs)
    if isinstance(event, CallbackQuery):
        await event.answer()''',
    "send_poll": '''async def send_poll(event, question, options) -> None:
    message = event.message if isinstance(event, CallbackQuery) else event
    await message.answer_poll(
        question, [InputPollOption(text=item) for item in options]
    )
    if isinstance(event, CallbackQuery):
        await event.answer()''',
    "remove": '''async def remove(event) -> None:
    # Delete the message the button or command arrived from.
    message = event.message if isinstance(event, CallbackQuery) else event
    await message.delete()
    if isinstance(event, CallbackQuery):
        await event.answer()''',
    "typing": '''async def typing(event) -> None:
    # Show "bot is typing..." in the chat.
    message = event.message if isinstance(event, CallbackQuery) else event
    await event.bot.send_chat_action(message.chat.id, "typing")''',
    "delay": '''async def delay(seconds) -> None:
    await asyncio.sleep(seconds)''',
    "edit_text": '''async def edit_text(event, text) -> None:
    message = event.message if isinstance(event, CallbackQuery) else event
    await message.edit_text(text)
    if isinstance(event, CallbackQuery):
        await event.answer()''',
    "answer_callback": '''async def answer_callback(event, text="", alert=False) -> None:
    if isinstance(event, CallbackQuery):
        await event.answer(text or None, show_alert=alert or None)''',
    "pin": '''async def pin(event, silent=False) -> None:
    message = event.message if isinstance(event, CallbackQuery) else event
    await event.bot.pin_chat_message(
        message.chat.id, message.message_id, disable_notification=silent
    )''',
    "unpin": '''async def unpin(event) -> None:
    message = event.message if isinstance(event, CallbackQuery) else event
    await event.bot.unpin_chat_message(message.chat.id, message.message_id)''',
    "ban_user": '''async def ban_user(event, user_id=0) -> None:
    message = event.message if isinstance(event, CallbackQuery) else event
    target = user_id or (message.from_user.id if message.from_user else 0)
    await event.bot.ban_chat_member(message.chat.id, target)''',
    "unban_user": '''async def unban_user(event, user_id=0) -> None:
    message = event.message if isinstance(event, CallbackQuery) else event
    target = user_id or (message.from_user.id if message.from_user else 0)
    await event.bot.unban_chat_member(message.chat.id, target)''',
    "mute_user": '''async def mute_user(event, user_id=0, minutes=10) -> None:
    message = event.message if isinstance(event, CallbackQuery) else event
    target = user_id or (message.from_user.id if message.from_user else 0)
    await event.bot.restrict_chat_member(
        message.chat.id,
        target,
        permissions=ChatPermissions(can_send_messages=False),
        until_date=timedelta(minutes=minutes),
    )''',
    "inline_result": '''async def inline_result(event, title, text, description="") -> None:
    await event.answer(
        results=[
            InlineQueryResultArticle(
                id=str(abs(hash(text)) % 10**8),
                title=title,
                description=description or None,
                input_message_content=InputTextMessageContent(message_text=text),
            )
        ]
    )''',
}

# Which import a helper needs (besides the always-present aiogram core).
HELPER_IMPORTS: Dict[str, Tuple[str, ...]] = {
    "inline": ("InlineKeyboardButton", "InlineKeyboardMarkup"),
    "keyboard": ("KeyboardButton", "ReplyKeyboardMarkup"),
    "media": (),
    "send_poll": ("InputPollOption",),
    "edit_text": (),
    "answer_callback": (),
    "mute_user": ("ChatPermissions", "timedelta"),
    "inline_result": ("InlineQueryResultArticle", "InputTextMessageContent"),
}

RUN_LINE = "# Run:  TG_BOT_TOKEN=123456:ABC python bot.py"


class _Usage:
    """Which imports and helpers the generated file has to carry."""

    def __init__(self) -> None:
        self.helpers: Set[str] = set()
        self.types: Set[str] = set()
        self.use_command = False
        self.use_filter = False
        self.use_state = False
        self.use_webhook = False

    def want(self, helper: str) -> None:
        self.helpers.add(helper)
        for name in HELPER_IMPORTS.get(helper, ()):  # type: ignore[arg-type]
            self.types.add(name)


def _iter_actions(actions) -> Iterable[object]:
    for node in actions:
        yield node
        if isinstance(node, When):
            yield from _iter_actions(node.then)
            yield from _iter_actions(node.orelse)


def _scan(spec: BotSpec, usage: _Usage) -> None:
    for handler in spec.handlers:
        spec_event = EVENTS_BY_KIND.get(handler.kind)
        if handler.kind == "command":
            usage.use_command = True
            # Every command also answers its own inline button, and that
            # decorator is built from F.data.
            usage.use_filter = True
        if handler.kind == "callback" and handler.data:
            # The callback filter itself is F.data == "...".
            usage.use_filter = True
        if spec_event is not None and spec_event.filter:
            usage.use_filter = True
        if handler.chat or handler.from_user or handler.regex or handler.patterns:
            usage.use_filter = True
        if handler.kind == "state":
            usage.use_state = True
        for node in _iter_actions(handler.actions):
            if isinstance(node, Buttons):
                usage.want("keyboard" if node.style == "reply" else "inline")
                if node.style == "reply" and any(
                    button.kind == "contact" or button.kind == "location"
                    for button in node.items
                ):
                    usage.types.add("KeyboardButton")
                if any(button.kind == "web_app" for button in node.items):
                    usage.types.add("WebAppInfo")
                continue
            if not isinstance(node, Action):
                continue
            kind = node.kind
            if kind == "send":
                usage.want("reply")
            elif kind in ("send_photo", "send_document", "send_video", "send_animation",
                          "send_audio", "send_voice", "send_sticker", "send_location",
                          "send_contact", "send_dice"):
                usage.want("media")
            elif kind == "send_poll":
                usage.want("send_poll")
            elif kind == "delete":
                usage.want("remove")
            elif kind == "typing":
                usage.want("typing")
            elif kind == "delay":
                usage.want("delay")
            elif kind == "edit_text":
                usage.want("edit_text")
            elif kind == "answer_callback":
                usage.want("answer_callback")
            elif kind == "pin":
                usage.want("pin")
            elif kind == "unpin":
                usage.want("unpin")
            elif kind == "ban_user":
                usage.want("ban_user")
            elif kind == "unban_user":
                usage.want("unban_user")
            elif kind == "mute_user":
                usage.want("mute_user")
            elif kind == "inline_result":
                usage.want("inline_result")
            elif kind in ("set_state", "clear_state"):
                usage.use_state = True
    # Conditions need one helper each: text comparison or the emoji value.
    for node in _iter_actions([node for handler in spec.handlers for node in handler.actions]):
        if isinstance(node, When):
            usage.want("dice_value" if node.condition.source == "dice" else "text_of")
    if spec.states:
        usage.use_state = True
    if spec.webhook:
        usage.use_webhook = True
    if usage.helpers & {"reply", "media", "edit_text", "remove", "typing", "pin",
                        "unpin", "ban_user", "unban_user", "mute_user", "text_of",
                        "send_poll"}:
        usage.types.add("CallbackQuery")
    if usage.helpers & {"reply", "edit_text", "remove", "typing", "pin", "unpin",
                        "ban_user", "unban_user", "mute_user", "send_poll", "media",
                        "inline_result", "answer_callback"}:
        usage.types.add("Message")


def _needs_text_of(node: When) -> bool:
    return node.condition.source != "dice"


# --------------------------------------------------------------------- emitters
class _Emitter:
    def __init__(self, bot: BotSpec, embed_token: bool = True) -> None:
        self.bot = bot
        self.embed_token = embed_token
        self._lines: List[str] = []
        self._used: Set[str] = set()
        self.usage = _Usage()
        _scan(bot, self.usage)

    # ------------------------------------------------------------------ names
    def _unique(self, base: str) -> str:
        candidate = base
        counter = 0
        while (
            candidate in self._used
            or candidate in RESERVED
            or keyword.iskeyword(candidate)
        ):
            counter += 1
            candidate = "{0}_{1}".format(base, counter)
        self._used.add(candidate)
        return candidate

    def _name_for(self, handler: Handler) -> str:
        if handler.kind == "command" and handler.command:
            base = re.sub(r"\W", "_", handler.command.lstrip("/")) or "command"
            if base in RESERVED or keyword.iskeyword(base):
                base = "cmd_" + base
            return self._unique(base)
        name = "on_" + handler.kind
        if handler.kind == "state" and handler.state:
            name = "on_state_" + re.sub(r"\W", "_", handler.state)
        return self._unique(name)

    # ---------------------------------------------------------------- assembly
    def generate(self) -> str:
        out: List[str] = []
        out.extend(self._header())
        out.append("")
        out.append("")
        ordered = sorted(
            self.bot.handlers,
            key=lambda item: (
                self._order(item),
                _KIND_ORDER.get(item.kind, 25),
                0 if item.patterns else 1,
            ),
        )
        for handler in ordered:
            out.extend(self._emit_handler(handler, self._name_for(handler)))
            out.append("")
            out.append("")
        out.extend(self._footer())
        return "\n".join(out).rstrip("\n") + "\n"

    def _order(self, handler: Handler) -> int:
        spec = EVENTS_BY_KIND.get(handler.kind)
        base = _OBSERVER_ORDER.get(spec.observer if spec else "message", 8)
        return base

    # ------------------------------------------------------------------ header
    def _header(self) -> List[str]:
        lines = [
            "# Telegram bot generated by tgblocks - edit freely.",
            "# Bot: {0}".format(self.bot.name),
            RUN_LINE,
        ]
        if not self.embed_token:
            # A generated bot is something people commit and share: the secret
            # stays in the environment or in the .tg file, never in the artefact.
            lines.append("# The token is NOT written into this file on purpose: export")
            lines.append("# TG_BOT_TOKEN=123456:ABC before running it.")
        lines.append("")
        lines.append("import asyncio")
        lines.append("import logging")
        lines.append("import os")
        if "timedelta" in self.usage.types:
            lines.append("from datetime import timedelta")
        lines.append("")
        lines.append("from aiogram import Bot, Dispatcher" + (", F" if self.usage.use_filter else ""))
        lines.append("from aiogram.client.session.aiohttp import AiohttpSession")
        lines.append("from aiogram.exceptions import TelegramNetworkError")
        if self.usage.use_command:
            lines.append("from aiogram.filters import Command")
        if self.usage.use_state:
            lines.append("from aiogram.filters import StateFilter")
            lines.append("from aiogram.fsm.context import FSMContext")
            lines.append("from aiogram.fsm.state import State, StatesGroup")
            lines.append("from aiogram.fsm.storage.memory import MemoryStorage")
        lines.append("")
        lines.append("try:")
        lines.append("    from aiohttp_socks import ProxyConnectionError")
        lines.append("except Exception:  # aiohttp-socks is optional")
        lines.append("    ProxyConnectionError = ConnectionError")

        types = self._type_names()
        if types:
            lines.append("from aiogram.types import (")
            for name in types:
                lines.append("    {0},".format(name))
            lines.append(")")
        lines.append("")
        lines.append("BOT_TOKEN = os.environ.get(\"TG_BOT_TOKEN\", {0})".format(
            _literal(self.bot.token or "") if self.embed_token else '""'))
        lines.append("PROXY = os.environ.get(\"TG_PROXY\", {0})".format(
            _literal(self.bot.proxy or "")))
        if self.usage.use_webhook:
            lines.append("WEBHOOK_URL = os.environ.get(\"TG_WEBHOOK_URL\", {0})".format(
                _literal(self.bot.webhook)))
            lines.append("WEBHOOK_PATH = {0}".format(_literal(self.bot.webhook_path)))
            lines.append("WEBHOOK_SECRET = os.environ.get(\"TG_WEBHOOK_SECRET\", {0})".format(
                _literal(self.bot.webhook_secret)))
        lines.append("")
        if self.usage.use_state:
            lines.append("dp = Dispatcher(storage=MemoryStorage())")
            lines.append("")
            lines.append("")
            lines.append("class Form(StatesGroup):")
            for state in self.bot.states:
                lines.append("    {0} = State()".format(state))
        else:
            lines.append("dp = Dispatcher()")

        for helper in self._helper_order():
            lines.append("")
            lines.append("")
            lines.extend(HELPER_BODIES[helper].splitlines())
        return lines

    def _helper_order(self) -> List[str]:
        order = ["inline", "keyboard", "text_of", "dice_value", "reply", "media",
                 "send_poll", "remove", "typing", "delay", "edit_text",
                 "answer_callback", "pin", "unpin", "ban_user", "unban_user",
                 "mute_user", "inline_result"]
        return [name for name in order if name in self.usage.helpers]

    def _type_names(self) -> List[str]:
        core = {"CallbackQuery", "Message"} & self.usage.types
        names = []
        for name in ("CallbackQuery", "ChatPermissions", "InlineKeyboardButton",
                     "InlineKeyboardMarkup", "InlinePollOption", "InlineQuery"
                     "ResultArticle", "InputPollOption", "InputTextMessageContent",
                     "KeyboardButton", "Message", "ReplyKeyboardMarkup", "WebAppInfo"):
            if name in self.usage.types:
                names.append(name)
        return names

    # ----------------------------------------------------------------- handlers
    def _emit_handler(self, handler: Handler, name: str) -> List[str]:
        self._lines = []
        self._emit_actions(handler.actions, 1)
        if not self._lines:
            self._lines = ["{0}pass".format(INDENT)]

        lines: List[str] = []
        lines.extend(self._decorators(handler))
        needs_state = self._uses_state(handler.actions)
        signature = "(event, state: FSMContext)" if needs_state else "(event)"
        lines.append("async def {0}{1} -> None:".format(name, signature))
        lines.extend(self._lines)
        return lines

    def _uses_state(self, actions) -> bool:
        for node in _iter_actions(actions):
            if isinstance(node, Action) and node.kind in ("set_state", "clear_state"):
                return True
        return False

    def _decorators(self, handler: Handler) -> List[str]:
        spec = EVENTS_BY_KIND.get(handler.kind)
        if spec is None:
            raise CodeGenError("unknown event {0!r}".format(handler.kind),
                               line=handler.line)
        # Filters go as separate arguments, never joined with "&": aiogram checks
        # them one by one, while `Command(...) & F.chat.type == "x"` raises
        # "unsupported operand type(s) for &: 'Command' and 'bool'" at runtime.
        filters = self._filters(handler, spec)
        lines = ["@dp.{0}({1})".format(spec.observer, ", ".join(filters))]
        if handler.kind == "command":
            callback_filters = ['F.data == {0}'.format(_literal(handler.command or ""))]
            if handler.from_user:
                callback_filters.append("F.from_user.id == {0}".format(handler.from_user))
            lines.append("@dp.callback_query({0})".format(", ".join(callback_filters)))
        return lines

    def _filters(self, handler: Handler, spec: EventSpec) -> List[str]:
        filters: List[str] = []
        if spec.filter:
            filters.append(spec.filter)
        if handler.patterns:
            filters.append("F.text.in_({0})".format(_tuple_literal(handler.patterns)))
        if handler.kind == "command":
            filters.append('Command("{0}")'.format((handler.command or "").lstrip("/")))
        if handler.kind == "callback" and handler.data:
            filters.append("F.data == {0}".format(_literal(handler.data)))
        if handler.kind == "state":
            filters.append("StateFilter(Form.{0})".format(handler.state))
        if handler.chat:
            filters.append('F.chat.type == {0}'.format(_literal(handler.chat)))
        if handler.from_user:
            filters.append("F.from_user.id == {0}".format(handler.from_user))
        if handler.regex:
            filters.append("F.text.regexp({0})".format(_literal(handler.regex)))
        return filters

    # --------------------------------------------------------------- statements
    def _emit_actions(self, actions: Sequence[object], depth: int) -> None:
        pad = INDENT * depth
        index = 0
        while index < len(actions):
            node = actions[index]

            if isinstance(node, Action) and node.kind == "send":
                markup = None
                step = 1
                following = actions[index + 1] if index + 1 < len(actions) else None
                if isinstance(following, Buttons):
                    markup = self._keyboard_expression(following)
                    step = 2
                self._lines.extend(self._reply_lines(str(node.params.get("text", "")),
                                                     markup, depth))
                index += step
                continue

            if isinstance(node, Buttons):
                raise CodeGenError(
                    "buttons must follow a send statement",
                    line=node.line,
                    hint='put `send "..."` directly before the buttons block',
                )

            if isinstance(node, When):
                self._lines.append(
                    "{0}if {1}:".format(pad, _condition_expression(node.condition))
                )
                self._emit_actions(node.then, depth + 1)
                if node.orelse:
                    self._lines.append("{0}else:".format(pad))
                    self._emit_actions(node.orelse, depth + 1)
                index += 1
                continue

            if isinstance(node, Action):
                self._emit_action(node, depth)
                index += 1
                continue

            raise CodeGenError(
                "cannot compile this statement", line=getattr(node, "line", 1)
            )

    def _emit_action(self, node: Action, depth: int) -> None:
        pad = INDENT * depth
        kind = node.kind
        params = node.params
        spec = ACTIONS_BY_KIND.get(kind)
        if spec is None:
            raise CodeGenError("unknown action {0!r}".format(kind), line=node.line)

        if kind in _MEDIA_ACTIONS:
            call_args: List[str] = []
            method = spec.method
            if kind == "send_dice":
                call_args.append("emoji={0}".format(_literal(str(params.get("emoji", "🎲")))))
            elif kind == "send_location":
                call_args.append("latitude={0}".format(_number(params.get("latitude", 0))))
                call_args.append("longitude={0}".format(_number(params.get("longitude", 0))))
            elif kind == "send_contact":
                call_args.append(_literal(str(params.get("phone", ""))))
                call_args.append(_literal(str(params.get("first_name", ""))))
            else:
                call_args.append(_literal(str(params.get(spec.payload, ""))))
                caption = str(params.get("caption", "") or "")
                if spec.caption and caption:
                    call_args.append("caption={0}".format(_literal(caption)))
            self._lines.append("{0}await media(event, {1}, {2})".format(
                pad, _literal(method), ", ".join(call_args)))
            return

        if kind == "send_poll":
            options = [str(item) for item in (params.get("options") or ())]
            self._lines.append("{0}await send_poll(".format(pad))
            self._lines.append("{0}event,".format(INDENT * (depth + 1)))
            self._lines.append("{0}{1},".format(INDENT * (depth + 1),
                                                _literal(str(params.get("question", "")))))
            self._lines.append("{0}({1}),".format(INDENT * (depth + 1),
                                                  ", ".join(_literal(item) for item in options)))
            self._lines.append("{0})".format(pad))
            return

        if kind == "delete":
            self._lines.append("{0}await remove(event)".format(pad))
            return
        if kind == "typing":
            self._lines.append("{0}await typing(event)".format(pad))
            return
        if kind == "delay":
            self._lines.append("{0}await delay({1})".format(
                pad, _number(params.get("seconds", 1))))
            return
        if kind == "nothing":
            self._lines.append("{0}pass  # ничего".format(pad))
            return
        if kind == "edit_text":
            self._lines.append("{0}await edit_text(event, {1})".format(
                pad, _literal(str(params.get("text", "")))))
            return
        if kind == "answer_callback":
            text = str(params.get("text", "") or "")
            alert = bool(params.get("alert"))
            args = [_literal(text)]
            if alert:
                args.append("alert=True")
            self._lines.append("{0}await answer_callback(event, {1})".format(
                pad, ", ".join(args)))
            return
        if kind == "pin":
            silent = bool(params.get("silent"))
            self._lines.append("{0}await pin(event{1})".format(
                pad, ", silent=True" if silent else ""))
            return
        if kind == "unpin":
            self._lines.append("{0}await unpin(event)".format(pad))
            return
        if kind in ("ban_user", "unban_user"):
            user_id = int(params.get("user_id") or 0)
            args = ["event"] + ([str(user_id)] if user_id else [])
            self._lines.append("{0}await {1}({2})".format(pad, kind, ", ".join(args)))
            return
        if kind == "mute_user":
            user_id = int(params.get("user_id") or 0)
            minutes = params.get("minutes", 10)
            args = ["event"]
            if user_id or minutes != 10:
                args.append(str(user_id))
            if minutes != 10:
                args.append(_number(minutes))
            self._lines.append("{0}await mute_user({1})".format(pad, ", ".join(args)))
            return
        if kind == "set_state":
            self._lines.append("{0}await state.set_state(Form.{1})".format(
                pad, params.get("state")))
            return
        if kind == "clear_state":
            self._lines.append("{0}await state.clear()".format(pad))
            return
        if kind == "log":
            self._lines.append("{0}logging.info({1})".format(
                pad, _literal(str(params.get("text", "")))))
            return
        if kind == "inline_result":
            description = str(params.get("description", "") or "")
            args = [_literal(str(params.get("title", ""))),
                    _literal(str(params.get("text", "")))]
            if description:
                args.append(_literal(description))
            self._lines.append("{0}await inline_result(event, {1})".format(
                pad, ", ".join(args)))
            return
        raise CodeGenError("cannot compile {0!r}".format(kind), line=node.line)

    # ------------------------------------------------------------ formatting
    def _reply_lines(self, text: str, markup: Optional[str], depth: int) -> List[str]:
        pad = INDENT * depth
        inner = INDENT * (depth + 1)
        if markup is None:
            single = "{0}await reply(event, {1})".format(pad, _literal(text))
            return [single] if len(single) <= LINE_WIDTH else [
                "{0}await reply(".format(pad),
                "{0}event,".format(inner),
                "{0}{1},".format(inner, _literal(text)),
                "{0})".format(pad),
            ]

        if len(pad) + len(markup) + 20 <= LINE_WIDTH and "\n" not in markup:
            return [
                "{0}await reply(".format(pad),
                "{0}event,".format(inner),
                "{0}{1},".format(inner, _literal(text)),
                "{0}{1},".format(inner, markup),
                "{0})".format(pad),
            ]

        lines = [
            "{0}await reply(".format(pad),
            "{0}event,".format(inner),
            "{0}{1},".format(inner, _literal(text)),
        ]
        lines.extend(self._wrapped_markup(markup, depth + 1))
        lines.append("{0})".format(pad))
        return lines

    def _wrapped_markup(self, markup: str, depth: int) -> List[str]:
        pad = INDENT * depth
        if len(pad) + len(markup) + 1 <= LINE_WIDTH:
            return ["{0}{1},".format(pad, markup)]

        call, args = markup.split("(", 1)
        args = args.rsplit(")", 1)[0]
        pieces = _split_arguments(args)
        lines = ["{0}{1}(".format(pad, call)]
        for piece in pieces:
            lines.append("{0}{1},".format(INDENT * (depth + 1), piece))
        lines.append("{0}),".format(pad))
        return lines

    def _keyboard_expression(self, node: Buttons) -> str:
        if node.style == "reply":
            pairs = []
            for button in node.items:
                kind_name = button.kind if button.kind in ("contact", "location") else "text"
                pairs.append("({0}, {1})".format(_literal(button.label), _literal(kind_name)))
            return "keyboard({0})".format(", ".join(pairs))
        triples = []
        for button in node.items:
            if button.kind in ("url", "web_app") and button.target:
                triples.append("({0}, {1}, {2})".format(
                    _literal(button.label), _literal(button.target), _literal(button.kind)))
            elif button.kind == "command" and button.target:
                triples.append("({0}, {1}, {2})".format(
                    _literal(button.label), _literal(button.target), '"command"'))
            else:
                raise CodeGenError(
                    "inline buttons need a target",
                    line=button.line,
                    hint='write `"Help" -> /help` or `"Site" -> url "https://example.com"`',
                )
        return "inline({0})".format(", ".join(triples))

    # ------------------------------------------------------------------ footer
    def _footer(self) -> List[str]:
        lines: List[str] = []
        lines.append("async def main() -> None:")
        lines.append("{0}logging.basicConfig(level=logging.INFO)".format(INDENT))
        lines.append("{0}if not BOT_TOKEN or BOT_TOKEN == \"PASTE_YOUR_TOKEN\":".format(INDENT))
        lines.append("{0}    raise SystemExit(".format(INDENT))
        lines.append("{0}        \"No bot token: put one in the .tg file, pass "
                     "--token, or set TG_BOT_TOKEN.\"".format(INDENT))
        lines.append("{0}    )".format(INDENT))
        lines.append("")
        lines.append("{0}session = None".format(INDENT))
        lines.append("{0}if PROXY:".format(INDENT))
        lines.append("{0}    try:".format(INDENT))
        lines.append("{0}        import aiohttp_socks  # noqa: F401".format(INDENT))
        lines.append("{0}    except ImportError:".format(INDENT))
        lines.append("{0}        raise SystemExit(".format(INDENT))
        lines.append("{0}            \"Proxy needs the aiohttp-socks package: "
                     "pip install aiohttp-socks\"".format(INDENT))
        lines.append("{0}        )".format(INDENT))
        lines.append("{0}    session = AiohttpSession(proxy=PROXY)".format(INDENT))
        lines.append("{0}bot = Bot(token=BOT_TOKEN, session=session)".format(INDENT))
        lines.append("")
        lines.append("{0}try:".format(INDENT))
        if self.usage.use_webhook:
            lines.append("{0}    if WEBHOOK_URL:".format(INDENT))
            lines.append("{0}        await serve_webhook(bot)".format(INDENT))
            lines.append("{0}    else:".format(INDENT))
            lines.append("{0}        await dp.start_polling(bot)".format(INDENT))
        else:
            lines.append("{0}    await dp.start_polling(bot)".format(INDENT))
        lines.append("{0}except (TelegramNetworkError, OSError, "
                     "ProxyConnectionError) as error:".format(INDENT))
        lines.append("{0}    raise SystemExit(".format(INDENT))
        lines.append(r'{0}        "Нет связи с api.telegram.org ({{0}}).\n"'.format(INDENT))
        lines.append(r'{0}        "Скорее всего Telegram заблокирован в этой сети. '
                     r'Варианты:\n"'.format(INDENT))
        lines.append(r'{0}        "  1) включить VPN для всей системы;\n"'.format(INDENT))
        lines.append(r'{0}        "  2) указать прокси: bot proxy '
                     r'\"socks5://127.0.0.1:1080\" или TG_PROXY=...\n"'.format(INDENT))
        lines.append(r'{0}        "     и поставить пакет: pip install aiohttp-socks"'
                     r".format(error)".format(INDENT))
        lines.append("{0}    )".format(INDENT))
        lines.append("{0}finally:".format(INDENT))
        lines.append("{0}    await bot.session.close()".format(INDENT))
        if self.usage.use_webhook:
            lines.append("")
            lines.append("")
            lines.extend(_webhook_body(self.bot.webhook_path))
        lines.append("")
        lines.append("")
        lines.append('if __name__ == "__main__":')
        lines.append("{0}asyncio.run(main())".format(INDENT))
        return lines


_MEDIA_ACTIONS = {
    "send_photo", "send_document", "send_video", "send_animation", "send_audio",
    "send_voice", "send_sticker", "send_location", "send_contact", "send_dice",
}

# Handlers are written in a fixed order, so the generated file reads top to
# bottom: commands, then plain text, then the narrower content types, then the
# catch-all. aiogram calls the first matching handler, so this order is what
# makes a specific handler win over `on any:`.
_OBSERVER_ORDER = {
    "message": 0,
    "edited_message": 1,
    "callback_query": 2,
    "inline_query": 3,
    "channel_post": 4,
    "chat_member": 5,
    "my_chat_member": 6,
    "poll_answer": 7,
}

_KIND_ORDER = {
    "command": 0,
    "text": 1,
    "state": 2,
    "callback": 3,
    "edited": 4,
    "photo": 5,
    "sticker": 6,
    "voice": 7,
    "video": 8,
    "video_note": 9,
    "audio": 10,
    "document": 11,
    "animation": 12,
    "location": 13,
    "contact": 14,
    "poll": 15,
    "dice": 16,
    "new_members": 17,
    "left_member": 18,
    "pinned": 19,
    "web_app_data": 20,
    "any": 30,
}


def _join_filters(parts: Sequence[str]) -> str:
    parts = [part for part in parts if part]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return " & ".join("({0})".format(part) for part in parts)


def _webhook_body(path: str) -> List[str]:
    return '''async def serve_webhook(bot: Bot) -> None:
    # Webhook mode: the bot listens on PORT (default 8080) and Telegram pushes.
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    port = int(os.environ.get("PORT", "8080"))
    await bot.set_webhook(WEBHOOK_URL, secret_token=WEBHOOK_SECRET or None)
    app = web.Application()
    handler = SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET or None)
    handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", port).start()
    logging.info("webhook %s is listening on port %s", WEBHOOK_PATH, port)
    await asyncio.Event().wait()'''.format(path=path).splitlines()


def _split_arguments(text: str) -> List[str]:
    # Split "('a', '/a'), ('b', '/b')" on top-level commas only.
    pieces: List[str] = []
    depth = 0
    current: List[str] = []
    quote = ""
    for char in text:
        if quote:
            current.append(char)
            if char == quote:
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
            pieces.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        pieces.append(tail)
    return pieces


def generate(bot: BotSpec, embed_token: bool = True) -> str:
    # Return aiogram 3 source code for a parsed bot.
    #
    # embed_token=False keeps the secret out of the generated file: the bot then
    # reads TG_BOT_TOKEN at startup, which is what the CLI does by default.
    return _Emitter(bot, embed_token=embed_token).generate()


def compile_source(source: str, filename: str = "<dsl>", embed_token: bool = True) -> str:
    # Parse DSL text and return generated Python code.
    from .parser import parse

    return generate(parse(source, filename), embed_token=embed_token)
