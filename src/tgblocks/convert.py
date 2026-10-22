# Conversions between the three editor representations.
#
#   text syntax  <->  AST (BotSpec)  ->  nodes graph JSON
#                                    ->  Blockly workspace XML
#
# The text syntax is the common interchange: the node editor can emit it from
# its DSL, the Blockly editor can emit it from its generated DSL, and both can
# be restored from it.
#
# Every action and event comes from tgblocks.model, so a new aiogram feature
# travels through all three editors without touching this file.

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Sequence

from .dsl.parser import (
    Action,
    BotSpec,
    Button,
    Buttons,
    Condition,
    Handler,
    When,
)
from .model import (
    ACTIONS_BY_KIND,
    ActionSpec,
    EventSpec,
    EVENTS_BY_KIND,
    event_for,
)

INDENT = "    "

# Node types that are older than the catalogue keep their historical names, so
# projects saved by the previous version still open.
NODE_ALIAS = {"send_photo": "photo"}
NODE_ALIAS_BACK = {value: key for key, value in NODE_ALIAS.items()}

# Text-syntax helpers: which node/action kind a Blockly event block carries.
CONST_KINDS = {
    "new_members": "NEW_MEMBERS",
    "left_member": "LEFT_MEMBER",
    "video_note": "VIDEO_NOTE",
    "pinned": "PINNED",
    "web_app_data": "WEB_APP_DATA",
    "edited": "EDITED",
    "dice": "DICE",
}

_STATE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _q(value: str) -> str:
    return json.dumps(str(value), ensure_ascii=False)


# --------------------------------------------------------------------- text
def _render_argument(param, value) -> List[str]:
    # One param -> the argument texts that reproduce it in the text syntax.
    if param.kind == "values":
        return [_q(item) for item in (value or ())]
    if param.kind == "bool":
        return [param.name + ("=True" if value else "=False")] if value else []
    if value in (None, ""):
        return []
    if param.kind == "number":
        return [str(value)]
    if param.kind == "state":
        return [str(value) if _STATE_RE.match(str(value)) else _q(value)]
    return [_q(value)]


def _action_args(spec: ActionSpec, params: Dict[str, object]) -> List[str]:
    args: List[str] = []
    for param in spec.params:
        args.extend(_render_argument(param, params.get(param.name, param.default)))
    return args


def _buttons_text(buttons: Buttons, level: int, lines: List[str]) -> None:
    pad = INDENT * level
    lines.append(pad + "buttons(" + _q(buttons.style) + ")")
    for item in buttons.items:
        head = pad + "button(" + _q(item.label)
        if item.kind == "url":
            lines.append(head + ", url=" + _q(item.target or "") + ")")
        elif item.kind == "web_app":
            lines.append(head + ", web_app=" + _q(item.target or "") + ")")
        elif item.kind == "contact":
            lines.append(head + ", contact=True)")
        elif item.kind == "location":
            lines.append(head + ", location=True)")
        elif item.kind == "command":
            lines.append(head + ", " + _q(item.target or "") + ")")
        else:
            lines.append(head + ")")


def _actions_text(actions: Sequence[object], level: int, lines: List[str]) -> None:
    pad = INDENT * level
    index = 0
    while index < len(actions):
        node = actions[index]
        if isinstance(node, Action) and node.kind == "send":
            lines.append(pad + "send(" + _q(str(node.params.get("text", ""))) + ")")
            following = actions[index + 1] if index + 1 < len(actions) else None
            if isinstance(following, Buttons):
                _buttons_text(following, level + 1, lines)
                index += 2
                continue
            index += 1
            continue
        if isinstance(node, Buttons):
            _buttons_text(node, level, lines)
            index += 1
            continue
        if isinstance(node, When):
            if node.condition.source == "dice":
                lines.append(
                    pad + 'when("dice", ' + _q(node.condition.op) + ", "
                    + str(node.condition.value) + "):"
                )
            else:
                extra = "".join("; " + _q(item) for item in (node.condition.values or ()))
                lines.append(
                    pad + "when(" + _q(node.condition.op) + ", "
                    + _q(node.condition.value) + extra + "):"
                )
            _actions_text(node.then, level + 1, lines)
            if node.orelse:
                lines.append(pad + "otherwise():")
                _actions_text(node.orelse, level + 1, lines)
            index += 1
            continue
        if isinstance(node, Action):
            spec = ACTIONS_BY_KIND.get(node.kind)
            if spec is None:
                raise ValueError("unknown action: {0!r}".format(node.kind))
            if node.kind == "nothing":
                lines.append(pad + "pass")
            else:
                lines.append(
                    pad + node.kind + "(" + ", ".join(_action_args(spec, node.params)) + ")"
                )
            index += 1
            continue
        raise ValueError("unknown action: {0!r}".format(node))
    if not actions:
        lines.append(pad + "pass")


def _event_head(handler: Handler) -> str:
    spec = EVENTS_BY_KIND.get(handler.kind)
    if spec is None:
        raise ValueError("unknown event: {0!r}".format(handler.kind))
    extra: List[str] = []
    if handler.chat:
        extra.append("chat=" + _q(handler.chat))
    if handler.from_user:
        extra.append("from_user=" + str(handler.from_user))
    if handler.regex:
        extra.append("regex=" + _q(handler.regex))

    if handler.kind == "command":
        args = [_q(handler.command or "/start")] + extra
        return "on.command(" + ", ".join(args) + "):"
    if handler.kind == "text":
        args = ["TEXT"] + [_q(item) for item in handler.patterns] + extra
        return "on.message(" + ", ".join(args) + "):"
    if handler.kind == "callback":
        args = ([_q(handler.data)] if handler.data else []) + extra
        return "on.callback(" + ", ".join(args) + "):"
    if handler.kind == "state":
        args = [handler.state] + extra
        return "on.state(" + ", ".join(args) + "):"
    args = extra
    return "on." + handler.kind + "(" + ", ".join(args) + "):"


def spec_to_text(spec: BotSpec) -> str:
    lines: List[str] = []
    if spec.token:
        lines.append("token(" + _q(spec.token) + ")")
    if spec.name and spec.name != "tgblocks bot":
        lines.append("name(" + _q(spec.name) + ")")
    if spec.proxy:
        lines.append("proxy(" + _q(spec.proxy) + ")")
    if spec.webhook:
        lines.append("webhook(" + _q(spec.webhook) + ")")
        if spec.webhook_path and spec.webhook_path != "/webhook":
            lines.append("webhook_path(" + _q(spec.webhook_path) + ")")
        if spec.webhook_secret:
            lines.append("webhook_secret(" + _q(spec.webhook_secret) + ")")
    if lines:
        lines.append("")
    for state in spec.states:
        lines.append("state(" + state + ")")
    if spec.states:
        lines.append("")
    for handler in spec.handlers:
        lines.append(_event_head(handler))
        _actions_text(handler.actions, 1, lines)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


# -------------------------------------------------------------------- nodes
def _node_type(action_kind: str) -> str:
    return NODE_ALIAS.get(action_kind, action_kind)


def _action_kind(node_type: str) -> str:
    return NODE_ALIAS_BACK.get(node_type, node_type)


def spec_to_nodes(spec: BotSpec, layout: Dict[str, dict] = None) -> Dict[str, object]:
    nodes: Dict[str, dict] = {}
    counter = [0]

    def new_id(prefix: str) -> str:
        counter[0] += 1
        return prefix + str(counter[0])

    def make(kind: str, props: dict, x: float, y: float) -> str:
        node_id = new_id(kind[:1])
        nodes[node_id] = {
            "id": node_id,
            "type": kind,
            "props": props,
            "parent": None,
            "children": [],
            "x": x,
            "y": y,
        }
        return node_id

    def link(parent: str, child: str) -> None:
        nodes[parent]["children"].append(child)
        if nodes[child]["parent"] is None:
            nodes[child]["parent"] = parent

    bot_props = {
        "token": spec.token or "",
        "proxy": spec.proxy or "",
        "name": "" if spec.name in ("", "tgblocks bot") else spec.name,
    }
    if spec.webhook:
        bot_props["webhook"] = spec.webhook
        bot_props["webhook_path"] = spec.webhook_path
        bot_props["webhook_secret"] = spec.webhook_secret
    bot_id = make("bot", bot_props, 60, 60)
    y = 280
    for handler in spec.handlers:
        props = _handler_props(handler)
        event_id = make("event", props, 60, y)
        link(bot_id, event_id)
        _actions_nodes(handler.actions, event_id, 60, y + 170, nodes, make, link)
        y += 400

    board = {"nodes": nodes, "counter": counter[0], "rootId": bot_id, "manual": True}
    if layout:
        # Keep the canvas where the user left it: only new blocks get fresh spots.
        apply_layout(board, layout)
    return board


def _handler_props(handler: Handler) -> dict:
    kind = "message" if handler.kind == "text" else handler.kind
    props: Dict[str, object] = {"kind": kind}
    if handler.kind == "command":
        props["command"] = handler.command or "/start"
    if handler.patterns:
        # Kept on the event: the editor shows this field only when it is set.
        props["patterns"] = list(handler.patterns)
    if handler.kind == "callback" and handler.data:
        props["data"] = handler.data
    if handler.kind == "state":
        props["state"] = handler.state
    if handler.chat:
        props["chat"] = handler.chat
    if handler.from_user:
        props["from_user"] = handler.from_user
    if handler.regex:
        props["regex"] = handler.regex
    return props


def _actions_nodes(actions, parent_id, x, y, nodes, make, link) -> None:
    for node in actions:
        if isinstance(node, Action):
            node_type = _node_type(node.kind)
            props = dict(node.params)
            if node.kind == "nothing":
                link(parent_id, make("nothing", {}, x, y))
                y += 110
                continue
            action_id = make(node_type, props, x, y)
            link(parent_id, action_id)
            y += 150
        elif isinstance(node, Buttons):
            buttons_id = make("buttons", {"style": node.style}, x + 300, y - 150)
            parent = nodes[parent_id]
            send_children = [
                child for child in parent["children"] if nodes[child]["type"] == "send"
            ]
            if send_children:
                link(send_children[-1], buttons_id)
            else:
                link(parent_id, buttons_id)
            for item in node.items:
                button_id = make(
                    "button",
                    {"label": item.label, "target": item.target or "",
                     "kind": item.kind},
                    x + 600,
                    y - 150,
                )
                link(buttons_id, button_id)
                y += 110
        elif isinstance(node, When):
            when_props = {"op": node.condition.op, "value": node.condition.value}
            if node.condition.source == "dice":
                when_props["source"] = "dice"
            if node.condition.values:
                when_props["values"] = list(node.condition.values)
            when_id = make("when", when_props, x + 380, y)
            link(parent_id, when_id)
            _actions_nodes(node.then, when_id, x + 380, y + 170, nodes, make, link)
            if node.orelse:
                start = y + 170 + 170 * max(1, len(node.then))
                otherwise_id = make("otherwise", {}, x + 760, start)
                link(when_id, otherwise_id)
                _actions_nodes(node.orelse, otherwise_id, x + 760, start + 150, nodes,
                               make, link)


# ------------------------------------------------------------------- blocks
# Every event kind the block editor can show.
BLOCKLY_KINDS = {spec.kind for spec in EVENTS_BY_KIND.values()} | {"message"}


def _xml(value) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _field(name: str, value) -> str:
    return '<field name="{0}">{1}</field>'.format(name, _xml(value))


def _chain_xml(blocks: List[List[str]], depth: int) -> List[str]:
    """Join block renderings the way Blockly chains them: with <next>.

    Blockly keeps one block per statement slot and links the rest through
    `<next>`. Writing siblings into one <statement> made the editor show only
    the first of them, which is exactly the bug this function removes.
    """
    if not blocks:
        return []
    pad = "  " * depth
    out = list(blocks[0])
    if len(blocks) > 1:
        out.append(pad + "  <next>")
        out.extend(_chain_xml(blocks[1:], depth + 2))
        out.append(pad + "  </next>")
    out.append(pad + "</block>")
    return out


def _block_head(kind: str, depth: int) -> List[str]:
    return ["  " * depth + '<block type="tg_{0}">'.format(kind)]


def _actions_blocks(actions: Sequence[object], depth: int) -> List[List[str]]:
    inner = "  " * (depth + 1)
    blocks: List[List[str]] = []
    index = 0
    while index < len(actions):
        node = actions[index]
        if isinstance(node, Action):
            kind = node.kind
            spec = ACTIONS_BY_KIND.get(kind)
            block = _node_type(kind)
            if kind == "nothing":
                blocks.append(_block_head("nothing", depth))
                index += 1
                continue
            if kind == "send":
                lines = _block_head("send", depth)
                lines.append(inner + _field("TEXT", str(node.params.get("text", ""))))
                following = actions[index + 1] if index + 1 < len(actions) else None
                if isinstance(following, Buttons):
                    lines.append(inner + '<statement name="DO">')
                    lines.extend(_chain_xml([_buttons_block(following, depth + 2)], depth + 2))
                    lines.append(inner + "</statement>")
                    index += 2
                else:
                    index += 1
                blocks.append(lines)
                continue
            lines = _block_head(block, depth)
            if spec is not None:
                for param in spec.params:
                    value = node.params.get(param.name, param.default)
                    if param.kind == "values":
                        value = "; ".join(str(item) for item in (value or ()))
                    elif param.kind == "bool":
                        value = "true" if value else "false"
                    lines.append(inner + _field(param.name.upper(), value))
            blocks.append(lines)
            index += 1
            continue

        if isinstance(node, Buttons):
            blocks.append(_buttons_block(node, depth))
            index += 1
            continue

        if isinstance(node, When):
            lines = _block_head("when", depth)
            lines.append(inner + _field("SOURCE", node.condition.source))
            lines.append(inner + _field("OP", node.condition.op))
            lines.append(inner + _field("VALUE", node.condition.value))
            lines.append(inner + _field("VALUES", "; ".join(node.condition.values)))
            if node.then:
                lines.append(inner + '<statement name="DO">')
                lines.extend(_chain_xml(_actions_blocks(node.then, depth + 2), depth + 2))
                lines.append(inner + "</statement>")
            if node.orelse:
                lines.append(inner + '<statement name="ELSE">')
                lines.extend(_chain_xml(_actions_blocks(node.orelse, depth + 2), depth + 2))
                lines.append(inner + "</statement>")
            blocks.append(lines)
            index += 1
            continue
        index += 1
    return blocks


def _buttons_block(buttons: Buttons, depth: int) -> List[str]:
    pad = "  " * depth
    inner = "  " * (depth + 1)
    lines = _block_head("buttons", depth)
    lines.append(inner + _field("STYLE", buttons.style))
    if buttons.items:
        lines.append(inner + '<statement name="DO">')
        rows: List[List[str]] = []
        for item in buttons.items:
            row = _block_head("button", depth + 2)
            row.append("  " * (depth + 3) + _field("LABEL", item.label))
            row.append("  " * (depth + 3) + _field("TARGET", item.target or ""))
            row.append("  " * (depth + 3) + _field("KIND", item.kind))
            rows.append(row)
        lines.extend(_chain_xml(rows, depth + 2))
        lines.append(inner + "</statement>")
    return lines


def _event_block(handler: Handler, depth: int) -> List[str]:
    pad = "  " * depth
    inner = "  " * (depth + 1)
    kind = handler.kind if handler.kind in BLOCKLY_KINDS else "any"
    lines = _block_head("on", depth)
    lines.append(inner + _field("KIND", kind))
    lines.append(inner + _field("COMMAND", handler.command or ""))
    lines.append(inner + _field("PATTERNS", ", ".join(handler.patterns)))
    lines.append(inner + _field("DATA", handler.data))
    lines.append(inner + _field("STATE", handler.state))
    lines.append(inner + _field("CHAT", handler.chat))
    lines.append(inner + _field("FROM_USER", handler.from_user or ""))
    lines.append(inner + _field("REGEX", handler.regex))
    blocks = _actions_blocks(handler.actions, depth + 2)
    if blocks:
        lines.append(inner + '<statement name="DO">')
        lines.extend(_chain_xml(blocks, depth + 2))
        lines.append(inner + "</statement>")
    return lines


def spec_to_blocks_xml(spec: BotSpec) -> str:
    lines: List[str] = ['<xml xmlns="https://developers.google.com/blockly/xml">']
    lines.append('  <block type="tg_bot">')
    lines.append("    " + _field("TOKEN", spec.token or ""))
    lines.append("    " + _field("NAME", "" if spec.name in ("", "tgblocks bot") else spec.name))
    lines.append("    " + _field("PROXY", spec.proxy or ""))
    lines.append("    " + _field("WEBHOOK", spec.webhook or ""))
    if spec.handlers:
        lines.append('    <statement name="DO">')
        lines.extend(_chain_xml([_event_block(handler, 3) for handler in spec.handlers], 3))
        lines.append("    </statement>")
    lines.append("  </block>")
    lines.append("</xml>")
    return "\n".join(lines)


# --------------------------------------------------------- board -> text
def _props(node: dict) -> dict:
    value = node.get("props")
    return value if isinstance(value, dict) else {}


def _children(board: dict, node: dict) -> List[dict]:
    nodes = board.get("nodes") if isinstance(board.get("nodes"), dict) else board
    out: List[dict] = []
    for child_id in node.get("children") or []:
        child = nodes.get(child_id)
        if isinstance(child, dict):
            out.append(child)
    return out


def _children_of(node: dict, nodes: Dict[str, dict]) -> List[dict]:
    out: List[dict] = []
    for child_id in node.get("children") or []:
        child = nodes.get(str(child_id))
        if isinstance(child, dict):
            out.append(child)
    return out


def _button_from(node: dict) -> Button:
    props = _props(node)
    return Button(
        label=str(props.get("label", "")),
        kind=str(props.get("kind") or _guess_button_kind(props.get("target"))),
        target=str(props.get("target", "")),
    )


def _guess_button_kind(target) -> str:
    text = str(target or "")
    if text.startswith(("http://", "https://")):
        return "url"
    if text.startswith("/"):
        return "command"
    return "none"


def _params_from(spec: ActionSpec, props: dict) -> Dict[str, object]:
    params: Dict[str, object] = {}
    for param in spec.params:
        value = props.get(param.name, param.default)
        if param.kind == "values":
            value = _patterns(value)
        elif param.kind == "bool":
            value = str(value).lower() in ("1", "true", "yes", "on", "да")
        elif param.kind == "number":
            try:
                number = float(str(value).replace(",", ".") or 0)
                value = int(number) if number.is_integer() else number
            except ValueError:
                value = 0
        else:
            value = str(value if value is not None else "")
        params[param.name] = value
    return params


def _buttons_from(node: dict, nodes: Dict[str, dict]) -> List[object]:
    props = _props(node)
    items = [_button_from(child) for child in _children_of(node, nodes)
             if child.get("type") == "button"]
    return [Buttons(style=str(props.get("style", "inline")), items=items)]


def _actions_of(children: List[dict], nodes: Dict[str, dict],
                warnings: List[str] = None) -> List[object]:
    """Turn one list of sibling blocks into actions.

    The canvas lets a block sit *beside* another, so two rules are resolved here:
    a `buttons` block right after a `send` belongs to it, and an `otherwise`
    right after a `when` (or inside it) becomes that condition's else branch.
    """
    out: List[object] = []
    index = 0
    while index < len(children):
        child = children[index]
        node_type = str(child.get("type"))

        if node_type == "otherwise":
            if warnings is not None:
                warnings.append("«Иначе» без «Условия» перед ним - блок пропущен")
            index += 1
            continue

        if node_type == "buttons":
            if warnings is not None:
                warnings.append("«Клавиатура» должна стоять сразу после «Сообщения»")
            index += 1
            continue

        if node_type == "when":
            props = _props(child)
            inner = _children_of(child, nodes)
            nested_else = [item for item in inner if item.get("type") == "otherwise"]
            then_children = [item for item in inner if item.get("type") != "otherwise"]
            orelse: List[object] = []
            consumed = 1
            if nested_else:
                orelse = _actions_of(_children_of(nested_else[0], nodes), nodes, warnings)
            elif index + 1 < len(children) and children[index + 1].get("type") == "otherwise":
                orelse = _actions_of(_children_of(children[index + 1], nodes), nodes, warnings)
                consumed = 2
            out.append(When(
                condition=Condition(op=str(props.get("op", "contains")),
                                    value=str(props.get("value", "")),
                                    values=_patterns(props.get("values")),
                                    source=str(props.get("source") or "text")),
                then=_actions_of(then_children, nodes, warnings),
                orelse=orelse,
            ))
            index += consumed
            continue

        if node_type == "send":
            props = _props(child)
            actions: List[object] = [
                Action(kind="send", params={"text": str(props.get("text", ""))})
            ]
            consumed = 1
            nested = [item for item in _children_of(child, nodes)
                      if item.get("type") == "buttons"]
            if nested:
                actions.extend(_buttons_from(nested[0], nodes))
            elif index + 1 < len(children) and children[index + 1].get("type") == "buttons":
                actions.extend(_buttons_from(children[index + 1], nodes))
                consumed = 2
            out.extend(actions)
            index += consumed
            continue

        spec = ACTIONS_BY_KIND.get(_action_kind(node_type))
        if spec is not None:
            out.append(Action(kind=spec.kind, params=_params_from(spec, _props(child))))
        elif warnings is not None:
            warnings.append("Неизвестный блок «{0}» пропущен".format(node_type))
        index += 1
    return out


def _patterns(value) -> tuple:
    # The board carries patterns as a list; older files may hold one string.
    if isinstance(value, str):
        items = [item.strip() for item in value.replace(";", ",").split(",")]
        return tuple(item for item in items if item)
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value if str(item).strip())
    return ()


def board_to_spec(board: dict) -> BotSpec:
    section = board.get("nodes") if isinstance(board.get("nodes"), dict) else board
    nodes: Dict[str, dict] = {
        str(key): value
        for key, value in (section or {}).items()
        if isinstance(value, dict)
    }
    root_id = board.get("rootId")
    root = nodes.get(str(root_id)) if root_id is not None else None
    if not isinstance(root, dict):
        for candidate in nodes.values():
            if candidate.get("type") == "bot":
                root = candidate
                break
    spec = BotSpec()
    if not isinstance(root, dict):
        return spec
    props = _props(root)
    spec.token = str(props.get("token", "")).strip() or None
    spec.proxy = str(props.get("proxy", "")).strip()
    spec.webhook = str(props.get("webhook", "") or "").strip()
    spec.webhook_path = str(props.get("webhook_path", "") or "/webhook").strip()
    spec.webhook_secret = str(props.get("webhook_secret", "") or "").strip()
    name = str(props.get("name", "") or "").strip()
    if name:
        spec.name = name
    warnings: List[str] = []
    for event in _children_of(root, nodes):
        if event.get("type") != "event":
            continue
        handler, handler_warnings = _handler_from(event, nodes)
        warnings.extend(handler_warnings)
        if not handler.actions:
            warnings.append(
                "у события «{0}» нет действий".format(handler.kind)
                if handler.kind != "command"
                else "у команды {0} нет действий".format(handler.command)
            )
        spec.handlers.append(handler)
    spec.warnings = warnings
    # States are declared by the actions that use them, in source order.
    for handler in spec.handlers:
        for action in _walk(handler.actions):
            if isinstance(action, Action) and action.kind == "set_state":
                state = str(action.params.get("state") or "")
                if state and state not in spec.states:
                    spec.states.append(state)
    for handler in spec.handlers:
        if handler.kind == "state" and handler.state and handler.state not in spec.states:
            spec.states.append(handler.state)
    return spec


def _walk(actions):
    for node in actions:
        yield node
        if isinstance(node, When):
            yield from _walk(node.then)
            yield from _walk(node.orelse)


def _handler_from(event: dict, nodes: Dict[str, dict]):
    props = _props(event)
    kind = str(props.get("kind", "command"))
    if kind == "message":
        kind = "text"
    params: Dict[str, object] = {}
    if kind == "command":
        params["command"] = str(props.get("command", "") or "/start")
    if kind == "callback":
        params["data"] = str(props.get("data", "") or "")
    if kind == "state":
        params["state"] = str(props.get("state", "") or "")
    if "patterns" in props:
        params["patterns"] = _patterns(props.get("patterns"))
    for key in ("chat", "from_user", "regex"):
        if props.get(key):
            params[key] = props[key]
    warnings: List[str] = []
    actions = _actions_of(_children_of(event, nodes), nodes, warnings)
    return Handler(kind=kind, actions=actions, params=params), warnings


def board_to_text(board: dict) -> str:
    return spec_to_text(board_to_spec(board))


# --------------------------------------------------------- blocks -> spec
_XML_NS = "{https://developers.google.com/blockly/xml}"


def _tag(element) -> str:
    return element.tag.replace(_XML_NS, "") if isinstance(element.tag, str) else ""


def _child(element, tag: str):
    for child in element:
        if _tag(child) == tag:
            return child
    return None


def _field_value(element, name: str, default: str = "") -> str:
    for child in element:
        if _tag(child) == "field" and child.get("name") == name:
            return (child.text or "").strip()
    return default


def _statement_blocks(element, name: str) -> List:
    # <statement name="DO"><block .../></statement> - the first block of a chain.
    statement = None
    for child in element:
        if _tag(child) == "statement" and child.get("name") == name:
            statement = child
            break
    if statement is None:
        return []
    for child in statement:
        if _tag(child) == "block":
            return [child]
    return []


def _next_block(element):
    # Blockly chains blocks with <next><block .../></next>.
    next_tag = _child(element, "next")
    if next_tag is None:
        return None
    for child in next_tag:
        if _tag(child) == "block":
            return child
    return None


def _chain(element) -> List:
    out = []
    current = element
    while current is not None:
        out.append(current)
        current = _next_block(current)
    return out


def _buttons_from_block(element) -> Buttons:
    style = _field_value(element, "STYLE", "inline") or "inline"
    items: List[Button] = []
    for block in _chain_many(_statement_blocks(element, "DO")):
        if _tag(block) != "block" or block.get("type") != "tg_button":
            continue
        target = _field_value(block, "TARGET")
        kind = _field_value(block, "KIND") or _guess_button_kind(target)
        items.append(Button(label=_field_value(block, "LABEL"), kind=kind,
                            target=target))
    return Buttons(style=style, items=items)


def _chain_many(blocks: List) -> List:
    out: List = []
    for block in blocks:
        out.extend(_chain(block))
    return out


def _actions_from_block(element) -> List[object]:
    out: List[object] = []
    for block in _chain(element):
        block_type = str(block.get("type", ""))
        if block_type == "tg_send":
            out.append(Action(kind="send", params={"text": _field_value(block, "TEXT")}))
            buttons = _statement_blocks(block, "DO")
            if buttons:
                out.append(_buttons_from_block(buttons[0]))
            continue
        if block_type == "tg_buttons":
            out.append(_buttons_from_block(block))
            continue
        if block_type == "tg_when":
            then_blocks = _statement_blocks(block, "DO")
            else_blocks = _statement_blocks(block, "ELSE")
            then: List[object] = []
            orelse: List[object] = []
            if then_blocks:
                then = _actions_from_block(then_blocks[0])
            if else_blocks:
                orelse = _actions_from_block(else_blocks[0])
            out.append(When(
                condition=Condition(op=_field_value(block, "OP", "contains"),
                                    value=_field_value(block, "VALUE"),
                                    values=_patterns(_field_value(block, "VALUES")),
                                    source=_field_value(block, "SOURCE", "text") or "text"),
                then=then, orelse=orelse))
            continue
        if block_type == "tg_otherwise":
            blocks = _statement_blocks(block, "DO")
            if blocks:
                out.extend(_actions_from_block(blocks[0]))
            continue
        if not block_type.startswith("tg_"):
            continue
        kind = _action_kind(block_type[3:])
        spec = ACTIONS_BY_KIND.get(kind)
        if spec is None:
            continue
        params: Dict[str, object] = {}
        for param in spec.params:
            raw = _field_value(block, param.name.upper(), "")
            if param.kind == "values":
                params[param.name] = _patterns(raw)
            elif param.kind == "bool":
                params[param.name] = raw.lower() in ("true", "1", "yes", "on", "да")
            elif param.kind == "number":
                try:
                    number = float(raw.replace(",", ".") or 0)
                    params[param.name] = int(number) if number.is_integer() else number
                except ValueError:
                    params[param.name] = 0
            else:
                params[param.name] = raw
        out.append(Action(kind=kind, params=params))
    return out


def _handler_from_block(element) -> Handler:
    kind = _field_value(element, "KIND", "command") or "command"
    if kind == "message":
        kind = "text"
    params: Dict[str, object] = {}
    if kind == "command":
        params["command"] = _field_value(element, "COMMAND", "/start") or "/start"
    if kind == "callback":
        params["data"] = _field_value(element, "DATA")
    if kind == "state":
        params["state"] = _field_value(element, "STATE")
    patterns = _patterns(_field_value(element, "PATTERNS"))
    if patterns:
        params["patterns"] = patterns
    chat = _field_value(element, "CHAT")
    if chat:
        params["chat"] = chat
    from_user = _field_value(element, "FROM_USER")
    if from_user:
        try:
            params["from_user"] = int(float(from_user))
        except ValueError:
            pass
    regex = _field_value(element, "REGEX")
    if regex:
        params["regex"] = regex
    actions: List[object] = []
    blocks = _statement_blocks(element, "DO")
    if blocks:
        actions = _actions_from_block(blocks[0])
    return Handler(kind=kind, actions=actions, params=params)


def blocks_xml_to_spec(xml_text: str) -> BotSpec:
    """Read a Blockly workspace exported by the block editor."""
    spec = BotSpec()
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as error:
        raise ValueError("cannot read the workspace XML: {0}".format(error)) from None
    blocks = [child for child in root if _tag(child) == "block"]
    if not blocks:
        return spec
    for block in _chain(blocks[0]):
        if block.get("type") != "tg_bot":
            continue
        spec.token = _field_value(block, "TOKEN") or None
        name = _field_value(block, "NAME")
        if name:
            spec.name = name
        spec.proxy = _field_value(block, "PROXY")
        spec.webhook = _field_value(block, "WEBHOOK")
        events = _statement_blocks(block, "DO")
        for event_block in _chain_many(events):
            if event_block.get("type") == "tg_on":
                spec.handlers.append(_handler_from_block(event_block))
    for handler in spec.handlers:
        for action in _walk(handler.actions):
            if isinstance(action, Action) and action.kind == "set_state":
                state = str(action.params.get("state") or "")
                if state and state not in spec.states:
                    spec.states.append(state)
    for handler in spec.handlers:
        if handler.kind == "state" and handler.state and handler.state not in spec.states:
            spec.states.append(handler.state)
    return spec


# -------------------------------------------------------------------- layout
# Where the blocks sit on the canvas is editor state, not bot logic: it lives
# next to the text and is keyed by a structural path, so re-reading the same
# bot puts every block back where the user left it.
def _board_nodes(board: dict) -> dict:
    if not isinstance(board, dict):
        return {}
    section = board.get("nodes")
    return section if isinstance(section, dict) else board


def _walk_board(board: dict):
    # Yields (path, node) for the whole tree under the bot block.
    nodes = _board_nodes(board)
    root_id = board.get("rootId") if isinstance(board, dict) else None
    root = nodes.get(root_id) if root_id else None
    if not isinstance(root, dict):
        root_id, root = None, None
        for key, candidate in nodes.items():
            if isinstance(candidate, dict) and candidate.get("type") == "bot":
                root_id, root = key, candidate
                break
    if root is None:
        return

    def visit(node_id: str, path: str) -> None:
        node = nodes.get(node_id)
        if not isinstance(node, dict):
            return
        yield path, node
        counters: Dict[str, int] = {}
        for child_id in node.get("children") or []:
            child = nodes.get(child_id)
            if not isinstance(child, dict):
                continue
            kind = child.get("type")
            if kind == "event":
                bucket = "e"
            elif kind == "otherwise":
                bucket = "o"
            elif kind == "buttons":
                bucket = "k"
            elif kind == "button":
                bucket = "c"
            else:
                bucket = "a"
            counters[bucket] = counters.get(bucket, 0) + 1
            yield from visit(child_id, path + "/" + bucket + str(counters[bucket]))

    yield from visit(root_id, "b")


def board_layout(board: dict) -> Dict[str, dict]:
    layout: Dict[str, dict] = {}
    for path, node in _walk_board(board):
        x, y = node.get("x"), node.get("y")
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            layout[path] = {"x": x, "y": y}
    return layout


def apply_layout(board: dict, layout: Dict[str, dict]) -> dict:
    if not isinstance(layout, dict) or not layout:
        return board
    for path, node in _walk_board(board):
        spot = layout.get(path)
        if not isinstance(spot, dict):
            continue
        x, y = spot.get("x"), spot.get("y")
        if isinstance(x, (int, float)) and isinstance(y, (int, float)):
            node["x"], node["y"] = x, y
    return board
