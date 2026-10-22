# Tests for the DSL parser, the text syntax and the aiogram generator.

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
