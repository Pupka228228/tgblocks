# Test corpus: every language feature the generators must keep working.
#
# Each entry is one bot. `syntax` says which front end parses the source, so the
# same list protects the DSL, the text syntax and (later) the editors that emit
# them. Adding a feature means adding an entry here: the golden file in
# tests/golden/ then pins the exact generated code.

from dataclasses import dataclass


@dataclass(frozen=True)
class Case:
    name: str
    syntax: str  # "dsl" | "text"
    source: str


def _case(name: str, syntax: str, source: str) -> Case:
    return Case(name=name, syntax=syntax, source=source.lstrip("\n"))


CORPUS = [
    _case(
        "hello",
        "dsl",
        """
bot token "123456:ABC"
bot name "Hello bot"

on /start:
    send "Hi! I am your bot."
    buttons:
        "Help" -> /help
        "About" -> /about

on /help:
    send "Commands: /start, /help, /about"
    buttons reply:
        "/start"
        "/help"

on message:
    when text contains "hi":
        send "Hello there!"
    else:
        send "Not sure what you mean. Try /help."
""",
    ),
    _case(
        "events",
        "dsl",
        """
bot token "1:events"

on message:
    send "text"
on photo:
    send "photo"
on sticker:
    send "sticker"
on voice:
    send "voice"
on video:
    send "video"
on video_note:
    send "round"
on audio:
    send "audio"
on document:
    send "document"
on animation:
    send "gif"
on location:
    send "location"
on contact:
    send "contact"
on poll:
    send "poll"
on new_members:
    send "welcome"
on left_member:
    send "bye"
on edited:
    send "edited"
on any:
    send "fallback"
""",
    ),
    _case(
        "actions",
        "dsl",
        """
bot token "1:actions"

on /start:
    typing
    delay 2
    delay 0.5
    send "line one\\nline two \\"quoted\\""
    send_photo "https://example.com/cat.jpg" "Котик"
    send_photo "https://example.com/dog.jpg"
    delete
    pass
""",
    ),
    _case(
        "conditions",
        "dsl",
        """
bot token "1:cond"

on message:
    when text == "точное":
        send "eq"
    when text != "стоп":
        send "ne"
    when text contains "цена":
        send "has"
    when text startswith "купи":
        send "starts"
    when text endswith "?":
        send "ends"
    when text contains "a", "b":
        send "any of them"
    when text != "x", "y":
        send "neither"
""",
    ),
    _case(
        "nested",
        "dsl",
        """
bot token "1:nested"

on /start:
    send "outer"
    when text contains "a":
        send "inner a"
        when text contains "b":
            send "deeper"
        else:
            send "inner not b"
    else:
        send "outer else"
        buttons:
            "Site" -> url "https://example.com"
""",
    ),
    _case(
        "patterns",
        "dsl",
        """
bot token "1:patterns"

on message "привет", "здравствуй":
    send "и тебе привет"

on text "buy":
    send "уже покупаю"
""",
    ),
    _case(
        "proxy",
        "dsl",
        """
bot token "1:proxy"
bot proxy "socks5://127.0.0.1:1080"

on /start:
    send "via proxy"
""",
    ),
    _case(
        "long-buttons",
        "dsl",
        '\n'.join(
            ['bot token "1:long"', "", "on /start:", '    send "menu"', "    buttons:"]
            + [
                '        "Очень длинная подпись кнопки, которая точно не влезет в восемьдесят восемь символов %d" -> /cmd%d'
                % (index, index)
                for index in range(3)
            ]
        ),
    ),
    _case(
        "text-basic",
        "text",
        """
token("123456:TEST")
name("Текстовый бот")

on.command("/start"):
    send("Привет")
    button("Помощь", "/help")
    button("Сайт", url="https://example.com")

on.message(TEXT, "привет", "Привет"):
    send("И тебе привет")

on.message(PHOTO):
    send("Хорошее фото")
""",
    ),
    _case(
        "text-actions",
        "text",
        """
token("1:text")
proxy("socks5://127.0.0.1:1080")

on.command("/start"):
    typing()
    delay(1.5)
    send_photo("https://example.com/cat.jpg", "котик")
    delete()

on.message(TEXT):
    when("contains", "как дела";"как ты"):
        send("Отлично")
    otherwise():
        send("Напиши /help")
""",
    ),
    _case(
        "text-buttons",
        "text",
        """
token("1:buttons")

on.command("/menu"):
    send("Меню")
    buttons("inline")
    button("Помощь", "/help")
    button("Сайт", url="https://example.com")

on.command("/reply"):
    buttons("reply")
    send("Выбери")
    button("Один")
    button("Два")
""",
    ),
]


def case_by_name(name: str) -> Case:
    for case in CORPUS:
        if case.name == name:
            return case
    raise KeyError(name)
