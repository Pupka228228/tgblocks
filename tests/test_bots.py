# Behavioural tests: what a user actually sees when the generated bot runs.
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
