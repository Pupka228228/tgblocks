# Semantic checks shared by the DSL and the text syntax.
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
