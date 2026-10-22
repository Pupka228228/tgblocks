# The feature catalogue: one description of everything a bot can do.
#
# Before this module every feature had to be written five times - in the DSL
# parser, in the text parser, in two converters and in the code generator - and a
# sixth time in each editor page. That is exactly why the three fronts drifted
# apart. Now a feature is one ActionSpec or EventSpec here:
#
#   * the parsers accept it and check its arguments (dsl/parser, textlang);
#   * the converters render it back to text and to the node/Blockly models;
#   * the code generator has an emitter for its `emit` family;
#   * /api/schema hands it to the editors, which build their palettes and
#     property fields from it.
#
# Adding an aiogram method is therefore a catalogue entry plus one emitter.

from __future__ import annotations

import ast
from dataclasses import dataclass, field, replace
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

# Action families: which events an action can run under, and which one it needs.
MESSAGE = "message"      # Message, EditedMessage, ChannelPost: event.answer(...)
CALLBACK = "callback"    # CallbackQuery: event.message.answer(...) + event.answer()
CHAT = "chat"            # ChatMemberUpdated: event.bot.send_message(event.chat.id, ...)
INLINE = "inline"        # InlineQuery: event.answer(results=[...])
ALL_EVENTS = (MESSAGE, CALLBACK, CHAT)


class BindError(ValueError):
    """An action's arguments do not fit its description."""

    def __init__(self, message: str, hint: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint


@dataclass(frozen=True)
class Param:
    name: str
    label: str
    kind: str = "text"       # text | multiline | number | bool | choice | values | state
    default: Any = ""
    choices: Tuple[Tuple[str, str], ...] = ()
    hint: str = ""
    required: bool = False
    # Hidden params are parsed, compiled and converted like any other, but the
    # editors do not offer a field for them: the same job is done better by a
    # `when` condition, which the user can see on the canvas.
    hidden: bool = False


@dataclass(frozen=True)
class ActionSpec:
    kind: str
    label: str
    group: str
    params: Tuple[Param, ...] = ()
    # How the generator writes it. "media" means "call Message.<method> with the
    # payload param and an optional caption"; "custom" is a hand-written emitter.
    emit: str = "custom"
    method: str = ""          # aiogram Message method name for emit="media"
    payload: str = ""         # which param is the first positional argument
    caption: bool = False
    observers: Tuple[str, ...] = ALL_EVENTS
    container: bool = False   # the node editor lets blocks nest inside it
    hint: str = ""

    def param(self, name: str) -> Optional[Param]:
        for item in self.params:
            if item.name == name:
                return item
        return None

    def defaults(self) -> Dict[str, Any]:
        return {item.name: item.default for item in self.params}


@dataclass(frozen=True)
class EventSpec:
    kind: str
    label: str
    group: str
    observer: str               # aiogram observer attribute: message, callback_query, ...
    family: str = MESSAGE       # which action family the handlers belong to
    filter: str = ""            # aiogram filter expression, "" means "everything"
    key_param: str = ""         # command / callback data / state name
    params: Tuple[Param, ...] = ()

    def param(self, name: str) -> Optional[Param]:
        for item in self.params:
            if item.name == name:
                return item
        return None

    def defaults(self) -> Dict[str, Any]:
        return {item.name: item.default for item in self.params}


# --------------------------------------------------------------------- filters
# Optional narrowing available on every event. It turns into one more filter
# argument on the generated handler.
CHAT_FILTER = Param(
    "chat",
    "получено",
    kind="choice",
    choices=(("", "в любом чате"), ("private", "в личке"), ("group", "в группе"),
             ("supergroup", "в супергруппе"), ("channel", "в канале")),
    hint="где именно получено сообщение",
)
FROM_FILTER = Param(
    "from_user",
    "только от пользователя с ID",
    kind="number",
    hint="0 - от любого; ID можно узнать у @userinfobot",
)
REGEX_FILTER = Param(
    "regex",
    "текст подходит под шаблон",
    hint='например ^[0-9]+$ - только цифры, ^привет - начинает с «привет»',
    hidden=True,
)
COMMON_EVENT_PARAMS: Tuple[Param, ...] = ()

GROUPS = (
    ("event", "События"),
    ("message", "Сообщения"),
    ("media", "Медиа"),
    ("keyboard", "Клавиатура"),
    ("logic", "Логика"),
    ("state", "Состояния"),
    ("moderation", "Модерация"),
    ("service", "Сервис"),
)


# --------------------------------------------------------------------- actions
ACTIONS: Tuple[ActionSpec, ...] = (
    # --- messages ---------------------------------------------------------
    ActionSpec(
        "send", "Отправить текст", "message",
        params=(Param("text", "Текст", kind="multiline", required=True, default="Привет!"),),
        emit="send", container=True,
        hint="сообщение от бота; кнопки вкладываются внутрь",
    ),
    ActionSpec(
        "send_photo", "Фото", "media",
        params=(Param("url", "URL или file_id", required=True, default="https://"),
                Param("caption", "Подпись")),
        emit="media", method="answer_photo", payload="url", caption=True,
    ),
    ActionSpec(
        "send_document", "Документ", "media",
        params=(Param("url", "URL или file_id", required=True, default="https://"),
                Param("caption", "Подпись")),
        emit="media", method="answer_document", payload="url", caption=True,
    ),
    ActionSpec(
        "send_video", "Видео", "media",
        params=(Param("url", "URL или file_id", required=True, default="https://"),
                Param("caption", "Подпись")),
        emit="media", method="answer_video", payload="url", caption=True,
    ),
    ActionSpec(
        "send_animation", "GIF", "media",
        params=(Param("url", "URL или file_id", required=True, default="https://"),
                Param("caption", "Подпись")),
        emit="media", method="answer_animation", payload="url", caption=True,
    ),
    ActionSpec(
        "send_audio", "Аудио", "media",
        params=(Param("url", "URL или file_id", required=True, default="https://"),
                Param("caption", "Подпись")),
        emit="media", method="answer_audio", payload="url", caption=True,
    ),
    ActionSpec(
        "send_voice", "Голосовое", "media",
        params=(Param("url", "URL или file_id", required=True, default="https://"),
                Param("caption", "Подпись")),
        emit="media", method="answer_voice", payload="url", caption=True,
    ),
    ActionSpec(
        "send_sticker", "Стикер", "media",
        params=(Param("url", "URL или file_id", required=True, default="https://"),),
        emit="media", method="answer_sticker", payload="url",
    ),
    ActionSpec(
        "send_location", "Геолокация", "media",
        params=(Param("latitude", "Широта", kind="number", default="0", required=True),
                Param("longitude", "Долгота", kind="number", default="0", required=True)),
        emit="media", method="answer_location",
    ),
    ActionSpec(
        "send_contact", "Контакт", "media",
        params=(Param("phone", "Телефон", default="+10000000000", required=True),
                Param("first_name", "Имя", default="Имя")),
        emit="media", method="answer_contact",
    ),
    ActionSpec(
        "send_poll", "Опрос", "media",
        params=(Param("question", "Вопрос", required=True, default="Вопрос?"),
                Param("options", "Варианты", kind="values", required=True,
                      hint="через запятую: Да, Нет, Не знаю")),
        emit="custom",
    ),
    ActionSpec(
        "send_dice", "Интерактивное эмодзи", "media",
        params=(Param("emoji", "Какое", kind="choice",
                      choices=(("🎲", "кубик"), ("🎯", "дартс"), ("🏀", "баскетбол"),
                               ("⚽", "футбол"), ("🎰", "слоты"), ("🎳", "боулинг"),
                               ("🎉", "хлопушка")),
                      default="🎲"),),
        emit="media", method="answer_dice",
        hint="Telegram бросает эмодзи; что выпало - можно проверить условием",
    ),
    # --- editing and answering ------------------------------------------
    ActionSpec(
        "edit_text", "Изменить текст", "message",
        params=(Param("text", "Новый текст", kind="multiline", required=True, default=""),),
        emit="custom", hint="переписать сообщение, на котором нажали кнопку",
    ),
    ActionSpec(
        "answer_callback", "Всплывающая подсказка", "message",
        params=(Param("text", "Текст", default=""), Param("alert", "Окно с кнопкой ОК",
                                                          kind="bool", default=False)),
        emit="custom", observers=(CALLBACK,),
        hint="короткое сообщение над кнопкой, которую нажали",
    ),
    ActionSpec(
        "delete", "Удалить сообщение", "message",
        params=(), emit="delete",
    ),
    ActionSpec(
        "typing", "Печатает…", "service",
        params=(), emit="typing",
    ),
    ActionSpec(
        "pin", "Закрепить", "message",
        params=(Param("silent", "Без уведомления", kind="bool", default=False),),
        emit="custom",
    ),
    ActionSpec(
        "unpin", "Открепить", "message",
        params=(), emit="custom",
    ),
    # --- logic ------------------------------------------------------------
    ActionSpec(
        "when", "Условие", "logic",
        params=(Param("op", "Проверка", kind="choice",
                      choices=(("contains", "содержит"), ("==", "равно"),
                               ("!=", "не равно"), ("startswith", "начинается с"),
                               ("endswith", "заканчивается на")),
                      default="contains"),
                Param("value", "Значение", default="привет", required=True),
                Param("values", "Ещё значения", kind="values")),
        emit="when", container=True,
    ),
    ActionSpec(
        "otherwise", "Иначе", "logic", params=(), emit="otherwise", container=True,
    ),
    ActionSpec("nothing", "Ничего", "logic", params=(), emit="nothing"),
    # --- states (FSM) -----------------------------------------------------
    ActionSpec(
        "set_state", "Запомнить шаг", "state",
        params=(Param("state", "Шаг", kind="state", required=True),),
        emit="custom", hint="диалог запомнит, на каком шаге пользователь",
    ),
    ActionSpec(
        "clear_state", "Забыть шаг", "state", params=(), emit="custom",
    ),
    # --- moderation -------------------------------------------------------
    ActionSpec(
        "ban_user", "Забанить", "moderation",
        params=(Param("user_id", "ID пользователя", kind="number", default="0"),),
        emit="custom", hint="пустой ID - забанить автора сообщения",
    ),
    ActionSpec(
        "unban_user", "Разбанить", "moderation",
        params=(Param("user_id", "ID пользователя", kind="number", default="0"),),
        emit="custom",
    ),
    ActionSpec(
        "mute_user", "Заглушить", "moderation",
        params=(Param("user_id", "ID пользователя", kind="number", default="0"),
                Param("minutes", "Минут", kind="number", default="10")),
        emit="custom",
    ),
    # --- service ----------------------------------------------------------
    ActionSpec(
        "delay", "Пауза", "service",
        params=(Param("seconds", "Секунды", kind="number", default="1", required=True),),
        emit="delay",
    ),
    ActionSpec(
        "log", "Запись в лог", "service",
        params=(Param("text", "Текст", default="", required=True),),
        emit="custom", hint="печатается в консоль и во вкладку «Логи»",
    ),
    ActionSpec(
        "inline_result", "Ответ на inline-запрос", "message",
        params=(Param("title", "Заголовок в списке", required=True, default="Заголовок"),
                Param("text", "Текст, который отправится", kind="multiline",
                      required=True, default="Текст"),
                Param("description", "Пояснение под заголовком")),
        emit="custom", observers=(INLINE,),
        hint="когда человек пишет «@бот запрос» в любом чате; показывается "
             "одна карточка-ответ",
    ),
)

ACTIONS_BY_KIND: Dict[str, ActionSpec] = {item.kind: item for item in ACTIONS}

# How the editors word every action. The machine names stay as they are; this is
# the one place to change a label or the one-line explanation under it.
ACTION_TEXT: Dict[str, Tuple[str, str]] = {
    "send": ("Отправить текст", "сообщение от бота; кнопки вкладываются внутрь"),
    "send_photo": ("Фото", "картинка по ссылке или file_id"),
    "send_document": ("Документ", "файл по ссылке или file_id"),
    "send_video": ("Видео", "ролик по ссылке или file_id"),
    "send_animation": ("GIF", "анимация по ссылке или file_id"),
    "send_audio": ("Аудио", "музыка по ссылке или file_id"),
    "send_voice": ("Голосовое", "запись по ссылке или file_id"),
    "send_sticker": ("Стикер", "стикер по ссылке или file_id"),
    "send_location": ("Геолокация", "точка на карте: широта и долгота"),
    "send_contact": ("Контакт", "телефон и имя одной карточкой"),
    "send_poll": ("Опрос", "вопрос и варианты ответа; Telegram считает голоса сам"),
    "send_dice": ("Интерактивное эмодзи",
                  "Telegram бросает кубик или дартс; что выпало - проверяется условием"),
    "edit_text": ("Изменить отправленное",
                  "переписать сообщение, на котором нажали кнопку"),
    "answer_callback": ("Подсказка над кнопкой",
                        "короткий текст или окно с «ОК» после нажатия"),
    "delete": ("Удалить сообщение", "стереть сообщение, из которого пришла команда"),
    "typing": ("Показать «печатает…»", "индикатор набора в чате"),
    "pin": ("Закрепить сообщение", "закрепить сообщение в чате"),
    "unpin": ("Открепить сообщение", "снять закрепление"),
    "when": ("Условие", "проверка текста сообщения; внутри - что делать"),
    "otherwise": ("Иначе", "ветка «иначе» для условия рядом"),
    "nothing": ("Ничего не делать", "пустое действие, например внутри условия"),
    "set_state": ("Перейти к шагу", "диалог запомнит, на каком шаге человек"),
    "clear_state": ("Завершить диалог", "забыть шаг: дальше работают обычные обработчики"),
    "ban_user": ("Забанить", "без ID - забанить автора сообщения"),
    "unban_user": ("Разбанить", "вернуть доступ в чат"),
    "mute_user": ("Заглушить", "запретить писать на N минут"),
    "delay": ("Пауза", "подождать перед следующим действием"),
    "log": ("Запись в лог", "печатается в консоль и во вкладку «Логи»"),
    "inline_result": ("Ответ на inline-запрос",
                      "когда человек пишет «@бот запрос» в любом чате; "
                      "показывается одна карточка-ответ"),
}

ACTIONS = tuple(
    replace(item, label=ACTION_TEXT[item.kind][0], hint=ACTION_TEXT[item.kind][1])
    if item.kind in ACTION_TEXT else item
    for item in ACTIONS
)
ACTIONS_BY_KIND = {item.kind: item for item in ACTIONS}

# Keywords that read better as aliases in the DSL and the text syntax.
ACTION_ALIASES = {
    "pass": "nothing",
    "photo": "send_photo",
    "document": "send_document",
    "video": "send_video",
    "animation": "send_animation",
    "audio": "send_audio",
    "voice": "send_voice",
    "sticker": "send_sticker",
    "location": "send_location",
    "contact": "send_contact",
    "poll": "send_poll",
    "dice": "send_dice",
    "alert": "answer_callback",
    "state": "set_state",
    "log_text": "log",
}


# ---------------------------------------------------------------------- events
EVENTS: Tuple[EventSpec, ...] = (
    EventSpec("command", "Команда", "event", "message",
              key_param="command",
              params=(Param("command", "Команда", default="/start", required=True),)),
    EventSpec("text", "Текст", "event", "message", filter="F.text",
              params=(Param("patterns", "Только эти тексты", kind="values",
                            hint="точные совпадения, через запятую", hidden=True),)),
    EventSpec("photo", "Фото", "event", "message", filter="F.photo"),
    EventSpec("sticker", "Стикер", "event", "message", filter="F.sticker"),
    EventSpec("voice", "Голосовое", "event", "message", filter="F.voice"),
    EventSpec("video", "Видео", "event", "message", filter="F.video"),
    EventSpec("video_note", "Кружок", "event", "message", filter="F.video_note"),
    EventSpec("audio", "Аудио", "event", "message", filter="F.audio"),
    EventSpec("document", "Документ", "event", "message", filter="F.document"),
    EventSpec("animation", "GIF", "event", "message", filter="F.animation"),
    EventSpec("location", "Геолокация", "event", "message", filter="F.location"),
    EventSpec("contact", "Контакт", "event", "message", filter="F.contact"),
    EventSpec("poll", "Опрос", "event", "message", filter="F.poll"),
    EventSpec("dice", "Кубик", "event", "message", filter="F.dice"),
    EventSpec("new_members", "Новый участник", "event", "message",
              filter="F.new_chat_members"),
    EventSpec("left_member", "Участник вышел", "event", "message",
              filter="F.left_chat_member"),
    EventSpec("pinned", "Сообщение закреплено", "event", "message",
              filter="F.pinned_message"),
    EventSpec("web_app_data", "Данные из Web App", "event", "message",
              filter="F.web_app_data"),
    EventSpec("any", "Любое сообщение", "event", "message"),
    EventSpec("edited", "Сообщение изменено", "event", "edited_message",
              filter="F.text"),
    EventSpec("callback", "Нажата кнопка", "event", "callback_query",
              family=CALLBACK, key_param="data",
              params=(Param("data", "Данные кнопки",
                            hint="пусто - любая кнопка; иначе точное совпадение"),)),
    EventSpec("state", "Сообщение на шаге диалога", "event", "message",
              key_param="state",
              params=(Param("state", "Шаг", kind="state", required=True),)),
    EventSpec("inline_query", "Inline-запрос", "event", "inline_query",
              family=INLINE),
    EventSpec("chat_member", "Участник изменился", "event", "chat_member",
              family=CHAT),
    EventSpec("my_chat_member", "Бот добавлен/убран", "event", "my_chat_member",
              family=CHAT),
    EventSpec("poll_answer", "Ответ на опрос", "event", "poll_answer",
              family=CHAT),
    EventSpec("channel_post", "Пост в канале", "event", "channel_post"),
)

def _extra_params(spec: "EventSpec") -> Tuple[Param, ...]:
    # Every event accepts the same optional narrowings; which ones make sense
    # depends on what the update carries.
    extras: List[Param] = []
    if spec.family in (MESSAGE, CHAT):
        extras.append(CHAT_FILTER)
    extras.append(FROM_FILTER)
    if spec.family == MESSAGE and spec.filter in ("F.text", ""):
        extras.append(REGEX_FILTER)
    return tuple(extras)


EVENTS = tuple(replace(spec, params=spec.params + _extra_params(spec)) for spec in EVENTS)

EVENTS_BY_KIND: Dict[str, EventSpec] = {item.kind: item for item in EVENTS}

EVENT_ALIASES = {
    "message": "text",
    "image": "photo",
    "left_chat_member": "left_member",
    "new_chat_members": "new_members",
    "button": "callback",
    "inline": "inline_query",
    "any": "any",
}

# Keyboard styles the `buttons` block understands.
KEYBOARD_STYLES = (
    ("inline", "inline-кнопки под сообщением"),
    ("reply", "reply-клавиатура вместо поля ввода"),
)

# Button targets: a command, a URL, or a reply-keyboard request.
BUTTON_KINDS = (
    ("command", "команда"),
    ("url", "ссылка"),
    ("web_app", "web app"),
    ("contact", "запросить телефон"),
    ("location", "запросить геолокацию"),
)


# ------------------------------------------------------------------- argument binding
def _strip_quotes(value: Any) -> Any:
    # `url="https://x"` arrives as the text `"https://x"` with its quotes: the
    # text syntax writes keyword arguments like Python does.
    if not isinstance(value, str):
        return value
    text = value.strip()
    if len(text) < 2 or text[0] not in "\"'" or text[-1] != text[0]:
        return value
    try:
        parsed = ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return value
    return parsed if isinstance(parsed, str) else value


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in ("1", "true", "yes", "on", "да"):
        return True
    if text in ("0", "false", "no", "off", "нет", ""):
        return False
    raise BindError("ожидалось true или false, получено {0!r}".format(value))


def _as_number(value: Any) -> Any:
    text = str(value).strip().replace(",", ".")
    if text == "":
        return 0
    try:
        number = float(text)
    except ValueError:
        raise BindError("ожидалось число, получено {0!r}".format(value)) from None
    return int(number) if number.is_integer() else number


def coerce(param: Param, value: Any) -> Any:
    value = _strip_quotes(value)
    if param.kind == "bool":
        return _as_bool(value)
    if param.kind == "number":
        return _as_number(value)
    if param.kind == "values":
        if isinstance(value, (list, tuple)):
            return tuple(str(item) for item in value if str(item).strip())
        return tuple(
            part.strip() for part in str(value).replace(";", ",").split(",")
            if part.strip()
        )
    if param.kind == "choice":
        allowed = [item[0] for item in param.choices]
        text = str(value)
        if allowed and text not in allowed:
            raise BindError(
                "ожидалось одно из {0}, получено {1!r}".format(
                    ", ".join(allowed), value
                )
            )
        return text
    return str(value)


def bind_arguments(spec: ActionSpec, items: Sequence[Tuple[str, bool]]) -> Dict[str, Any]:
    """Map source arguments onto the catalogue entry.

    `items` are (value, is_bare) pairs in source order, where bare means "not a
    quoted string" - `delay 2`, `alert`, `state=order`. A named `name=value` item
    sets that param, a bare bool param name turns it on, and everything else
    fills the declared params in order. A `values` param swallows the tail.
    """
    result = spec.defaults()
    filled = set()
    pending = list(items)
    index = 0
    while pending:
        raw, is_bare = pending.pop(0)
        text = str(raw)
        if is_bare and "=" in text:
            name, _, value = text.partition("=")
            param = spec.param(name.strip())
            if param is None:
                raise BindError(
                    "у {0} нет параметра {1!r}".format(spec.kind, name.strip()),
                    "доступны: " + ", ".join(p.name for p in spec.params),
                )
            result[param.name] = coerce(param, value.strip())
            filled.add(param.name)
            continue
        if is_bare:
            named = spec.param(text)
            if named is not None and named.kind == "bool":
                result[named.name] = True
                filled.add(named.name)
                continue
        while index < len(spec.params) and spec.params[index].name in filled:
            index += 1
        if index >= len(spec.params):
            raise BindError(
                "{0} не принимает столько аргументов".format(spec.kind),
                "параметры: " + ", ".join(p.name for p in spec.params),
            )
        param = spec.params[index]
        if param.kind == "values":
            rest = [text] + [str(value) for value, bare in pending if not bare]
            pending = []
            result[param.name] = coerce(param, rest)
            filled.add(param.name)
            break
        result[param.name] = coerce(param, text)
        filled.add(param.name)
        index += 1
    _check_required(spec, result)
    return result


def _check_required(spec: ActionSpec, values: Dict[str, Any]) -> None:
    for param in spec.params:
        if not param.required:
            continue
        value = values.get(param.name)
        if value is None or value == "" or value == ():
            raise BindError(
                "{0}: нужен параметр {1!r}".format(spec.kind, param.name),
                param.hint or param.label,
            )


def action_for(keyword: str) -> Optional[ActionSpec]:
    kind = ACTION_ALIASES.get(keyword, keyword)
    return ACTIONS_BY_KIND.get(kind)


def event_for(keyword: str) -> Optional[EventSpec]:
    kind = EVENT_ALIASES.get(keyword, keyword)
    return EVENTS_BY_KIND.get(kind)


# ------------------------------------------------------------------- languages
# The catalogue is written in Russian; these are the English labels the editors
# show when the interface language is switched. Lookup is by the Russian text, so
# a new action still appears in English as soon as its words are listed here.
EN_TEXT: Dict[str, str] = {
    # actions
    "Отправить текст": "Send text",
    "Фото": "Photo", "Документ": "Document", "Видео": "Video", "GIF": "GIF",
    "Аудио": "Audio", "Голосовое": "Voice message", "Стикер": "Sticker",
    "Геолокация": "Location", "Контакт": "Contact", "Опрос": "Poll",
    "Интерактивное эмодзи": "Interactive emoji",
    "Изменить отправленное": "Edit message",
    "Подсказка над кнопкой": "Toast over the button",
    "Удалить сообщение": "Delete message",
    "Показать «печатает…»": "Show “typing…”",
    "Закрепить сообщение": "Pin message", "Открепить сообщение": "Unpin message",
    "Условие": "Condition", "Иначе": "Else", "Ничего не делать": "Do nothing",
    "Перейти к шагу": "Go to step", "Завершить диалог": "End dialogue",
    "Забанить": "Ban", "Разбанить": "Unban", "Заглушить": "Mute",
    "Пауза": "Pause", "Запись в лог": "Write to log",
    "Ответ на inline-запрос": "Inline query answer",
    # hints
    "сообщение от бота; кнопки вкладываются внутрь":
        "a message from the bot; keyboards nest inside",
    "Telegram бросает кубик или дартс; что выпало - проверяется условием":
        "Telegram rolls it; check what came up with a condition",
    "переписать сообщение, на котором нажали кнопку":
        "rewrite the message the button was pressed on",
    "короткий текст или окно с «ОК» после нажатия":
        "a short text or an OK dialog after the press",
    "диалог запомнит, на каком шаге человек":
        "the dialogue remembers which step the person is on",
    "забыть шаг: дальше работают обычные обработчики":
        "forget the step: ordinary handlers take over",
    "когда человек пишет «@бот запрос» в любом чате; показывается одна карточка-ответ":
        "when someone types “@bot query”; one result card is shown",
    # events
    "Команда": "Command", "Текст": "Text", "Кружок": "Video note",
    "Новый участник": "New member", "Участник вышел": "Member left",
    "Сообщение закреплено": "Message pinned",
    "Данные из Web App": "Web App data", "Любое сообщение": "Any message",
    "Сообщение изменено": "Message edited", "Нажата кнопка": "Button pressed",
    "Сообщение на шаге диалога": "Message at a dialogue step",
    "Inline-запрос": "Inline query", "Участник изменился": "Member updated",
    "Бот добавлен/убран": "Bot added/removed", "Ответ на опрос": "Poll answer",
    "Пост в канале": "Channel post",
    # params
    "Текст": "Text", "Подпись": "Caption", "Ссылка или file_id": "URL or file_id",
    "URL или file_id": "URL or file_id", "Какое": "Which one",
    "Вопрос": "Question", "Варианты": "Options", "Широта": "Latitude",
    "Долгота": "Longitude", "Телефон": "Phone", "Имя": "First name",
    "Новый текст": "New text", "Окно с кнопкой ОК": "OK dialog",
    "Без уведомления": "Without notification", "ID пользователя": "User ID",
    "Минут": "Minutes", "Секунды": "Seconds", "Шаг": "Step",
    "Проверка": "Comparison", "Значение": "Value", "Ещё значения": "More values",
    "Заголовок в списке": "Title in the list", "Текст, который отправится": "Sent text",
    "Пояснение под заголовком": "Description under the title",
    "получено": "received", "только от пользователя с ID": "only from user ID",
    "текст подходит под шаблон": "text matches a pattern",
    "Только эти тексты": "Only these texts", "Данные кнопки": "Button data",
    # choices
    "в любом чате": "in any chat", "в личке": "in private", "в группе": "in a group",
    "в супергруппе": "in a supergroup", "в канале": "in a channel",
    "кубик": "dice", "дартс": "darts", "баскетбол": "basketball", "футбол": "football",
    "слоты": "slots", "боулинг": "bowling", "хлопушка": "party",
    "содержит": "contains", "равно": "equals", "не равно": "not equal",
    "начинается с": "starts with", "заканчивается на": "ends with",
    "команда": "command", "ссылка": "link", "запросить телефон": "request phone",
    "запросить геолокацию": "request location",
    # groups and keyboard
    "События": "Events", "Сообщения": "Messages", "Медиа": "Media",
    "Клавиатура": "Keyboard", "Логика": "Logic", "Состояния": "Dialogues",
    "Модерация": "Moderation", "Сервис": "Service",
    "inline-кнопки под сообщением": "inline buttons under the message",
    "reply-клавиатура вместо поля ввода": "reply keyboard instead of the input field",
    # the remaining hints, so no Russian word survives in the English palette
    "0 - от любого; ID можно узнать у @userinfobot":
        "0 - from anyone; find the ID with @userinfobot",
    "Кубик": "Dice",
    "анимация по ссылке или file_id": "a GIF by URL or file_id",
    "без ID - забанить автора сообщения": "no ID - ban the author of the message",
    "вернуть доступ в чат": "restore access to the chat",
    "ветка «иначе» для условия рядом": "the else branch of the condition nearby",
    "вопрос и варианты ответа; Telegram считает голоса сам":
        "a question and its options; Telegram counts the votes",
    "где именно получено сообщение": "which kind of chat the message came from",
    "закрепить сообщение в чате": "pin the message in the chat",
    "запись по ссылке или file_id": "a voice message by URL or file_id",
    "запретить писать на N минут": "mute for N minutes",
    "индикатор набора в чате": "the typing indicator in the chat",
    "картинка по ссылке или file_id": "a picture by URL or file_id",
    "музыка по ссылке или file_id": "music by URL or file_id",
    "например ^[0-9]+$ - только цифры, ^привет - начинает с «привет»":
        "e.g. ^[0-9]+$ - digits only; ^hi - starts with “hi”",
    "печатается в консоль и во вкладку «Логи»":
        "printed to the console and the Logs tab",
    "подождать перед следующим действием": "wait before the next action",
    "проверка текста сообщения; внутри - что делать":
        "a check on the message text; what to do goes inside",
    "пусто - любая кнопка; иначе точное совпадение":
        "empty - any button; otherwise an exact match",
    "пустое действие, например внутри условия": "a no-op, e.g. inside a condition",
    "ролик по ссылке или file_id": "a video by URL or file_id",
    "снять закрепление": "unpin the message",
    "стереть сообщение, из которого пришла команда":
        "delete the message the command came from",
    "стикер по ссылке или file_id": "a sticker by URL or file_id",
    "телефон и имя одной карточкой": "a phone and a name in one card",
    "точка на карте: широта и долгота": "a point on the map: latitude and longitude",
    "точные совпадения, через запятую": "exact matches, comma separated",
    "файл по ссылке или file_id": "a file by URL or file_id",
    "через запятую: Да, Нет, Не знаю": "comma separated: Yes, No, Not sure",
}


def english(text: str) -> str:
    # English label for a Russian one, or the original text when it is missing.
    return EN_TEXT.get(text, text)


# ------------------------------------------------------------------ editor schema
GROUP_COLOUR = {
    "message": "#1f7a4d", "media": "#1f7a4d", "keyboard": "#7ee0a8",
    "logic": "#c98bff", "state": "#d05c9b", "moderation": "#c0392b",
    "service": "#4a5a7a", "event": "#f0a35e",
}

# Blocks with statement slots are written by the page: their shape is part of the
# Blockly XML that convert.py reads back.
STRUCTURAL_BLOCKS = frozenset({"send", "when", "otherwise", "buttons", "button"})


def _blockly_field(param: Param, label, lang: str) -> Dict[str, Any]:
    name = param.name.upper()
    if param.kind == "choice":
        return {"type": "field_dropdown", "name": name,
                "options": [[label(choice_label), str(value)]
                            for value, choice_label in param.choices]}
    if param.kind == "bool":
        return {"type": "field_dropdown", "name": name,
                "options": [["yes" if lang == "en" else "да", "true"],
                            ["no" if lang == "en" else "нет", "false"]]}
    return {
        "type": "field_input",
        "name": name,
        "text": "" if param.kind == "values" else str(param.default or ""),
    }


def blockly_blocks(lang: str = "ru") -> List[Dict[str, Any]]:
    """Blockly block definitions for every catalogue action.

    Blockly numbers placeholders **per message**: `message0` refers to `args0`
    with `%1`, and `message1` starts again at `%1` for `args1`. Numbering them
    globally ("%2" in message1) makes Blockly refuse the whole definition with
    "Message index %2 out of range", which is what broke the block editor once.
    Building the JSON here keeps that rule in one testable place.
    """
    def label(text: str) -> str:
        return english(text) if lang == "en" else text

    blocks: List[Dict[str, Any]] = []
    for spec in ACTIONS:
        if spec.kind in STRUCTURAL_BLOCKS:
            continue
        definition: Dict[str, Any] = {
            "type": "tg_" + ("photo" if spec.kind == "send_photo" else spec.kind),
            "colour": GROUP_COLOUR.get(spec.group, "#4a5a7a"),
            "tooltip": label(spec.hint) or label(spec.label),
            "previousStatement": None,
            "nextStatement": None,
        }
        if not spec.params:
            definition["message0"] = label(spec.label)
        visible = [param for param in spec.params if not param.hidden]
        for index, param in enumerate(visible):
            caption = label(spec.label) if index == 0 else label(param.label)
            definition["message{0}".format(index)] = caption + " %1"
            definition["args{0}".format(index)] = [_blockly_field(param, label, lang)]
        blocks.append(definition)
    return blocks


def _param_schema(param: Param, label=str) -> Dict[str, Any]:
    # `label` is the translator for the requested language; label_en stays for
    # clients that switch language without reloading.
    return {
        "name": param.name,
        "label": label(param.label),
        "label_en": english(param.label),
        "kind": param.kind,
        "default": param.default,
        "choices": [{"value": value, "label": label(choice), "label_en": english(choice)}
                    for value, choice in param.choices],
        "hint": label(param.hint),
        "hint_en": english(param.hint),
        "required": param.required,
        "hidden": param.hidden,
    }


def schema(lang: str = "ru") -> Dict[str, Any]:
    """The whole catalogue as JSON for the three editors."""
    lang = "en" if str(lang).lower().startswith("en") else "ru"

    def label(text: str) -> str:
        return english(text) if lang == "en" else text

    return {
        "version": 3,
        "lang": lang,
        "groups": [{"kind": kind, "label": label(item), "label_en": english(item)}
                   for kind, item in GROUPS],
        "actions": [
            {
                "kind": item.kind,
                "label": label(item.label),
                "label_en": english(item.label),
                "group": item.group,
                "container": item.container,
                "observers": list(item.observers),
                "params": [_param_schema(param, label) for param in item.params],
                "hint": label(item.hint),
                "hint_en": english(item.hint),
            }
            for item in ACTIONS
        ],
        "events": [
            {
                "kind": item.kind,
                "label": label(item.label),
                "label_en": english(item.label),
                "group": item.group,
                "observer": item.observer,
                "family": item.family,
                "key_param": item.key_param,
                "params": [_param_schema(param, label) for param in item.params],
            }
            for item in EVENTS
        ],
        "filters": [_param_schema(param, label) for param in
                    (CHAT_FILTER, FROM_FILTER, REGEX_FILTER)],
        "keyboards": [{"value": value, "label": label(item), "label_en": english(item)}
                      for value, item in KEYBOARD_STYLES],
        "buttons": [{"value": value, "label": label(item), "label_en": english(item)}
                    for value, item in BUTTON_KINDS],
        "condition_ops": [
            ("==", label("равно")), ("!=", label("не равно")),
            ("contains", label("содержит")), ("startswith", label("начинается с")),
            ("endswith", label("заканчивается на")),
        ],
        # Ready-to-use Blockly definitions: the page feeds them straight to
        # Blockly.defineBlocksWithJsonArray, so the per-message numbering rule
        # lives here and is covered by a test.
        "blocks": blockly_blocks(lang),
    }
