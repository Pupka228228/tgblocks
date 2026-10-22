# Filters on generated handlers: aiogram checks each filter separately, and a
# Command filter cannot be joined with a magic filter by "&".
#
# `Command("start") & (F.chat.type == "private")` looks reasonable and fails at
# runtime with "unsupported operand type(s) for &: 'Command' and 'bool'". These
# tests run the generated bot on a fake Telegram for every filter combination.

import pytest

from botkit import Harness, message_payload
from tgblocks.dsl import compile_source
from tgblocks.textlang import compile_text

CASES = {
    "command-chat": ('bot token "1:x"\n\non /start chat=private:\n    send "hi"\n'),
    "command-from-user": ('bot token "1:x"\n\non /start from_user=7:\n    send "hi"\n'),
    "command-regex": ('bot token "1:x"\n\non /start regex="^/":\n    send "hi"\n'),
    "command-chat-from-user": (
        'bot token "1:x"\n\non /start chat=private from_user=7:\n    send "hi"\n'
    ),
    "message-chat": ('bot token "1:x"\n\non message chat=supergroup:\n    send "hi"\n'),
    "message-regex": (
        'bot token "1:x"\n\non message regex="^[0-9]+$":\n    send "hi"\n'
    ),
    "message-patterns-chat": (
        'bot token "1:x"\n\non message "a", "b" chat=private:\n    send "hi"\n'
    ),
    "callback-data": ('bot token "1:x"\n\non callback "/buy":\n    send "hi"\n'),
    "state": (
        'bot token "1:x"\n\nstate s\non /go:\n    set_state s\n'
        'on state s:\n    send "hi"\n'
    ),
    "text-command-chat": (
        'token("1:x")\n\non.command("/start", chat="private"):\n    send("hi")\n'
    ),
}


def build(source: str) -> str:
    if source.startswith('token("'):
        return compile_text(source, "case.txt")
    return compile_source(source, "case.tg")


@pytest.mark.parametrize("name", sorted(CASES), ids=sorted(CASES))
def test_filtered_handlers_run_without_type_errors(name, caplog):
    import logging

    caplog.set_level(logging.ERROR, logger="aiogram.event")
    harness = Harness(build(CASES[name]), "filters_" + name.replace("-", "_"))
    # aiogram logs a filter that raises instead of propagating it, so the check
    # is on the log: no "Cause exception" lines for a normal update.
    harness.command("/start")
    harness.text("a")
    failures = [record.getMessage() for record in caplog.records
                if "Cause exception" in record.getMessage()]
    assert failures == [], failures


def test_each_filter_is_a_separate_argument():
    code = compile_source(CASES["command-chat"])
    assert '@dp.message(Command("start"), F.chat.type == "private")' in code
    assert " & " not in code.split("async def main")[0].split("dp = Dispatcher")[1]


def test_command_filter_still_matches_and_respects_the_chat():
    harness = Harness(build(CASES["command-chat"]), "filters_chat")

    harness.command("/start", chat_id=42)          # private
    assert harness.session.texts() == ["hi"]

    harness.session.reset()
    harness.command("/start", chat_id=-100)        # supergroup
    assert harness.session.texts() == []


def test_from_user_filter_is_enforced():
    harness = Harness(build(CASES["command-from-user"]), "filters_from_user")

    harness.command("/start", user_id=7)
    assert harness.session.texts() == ["hi"]

    harness.session.reset()
    harness.ask(message_payload("/start", user_id=8))
    assert harness.session.texts() == []


def test_callback_event_without_a_command_still_compiles_filters():
    # This used to emit F.data == "..." without importing F.
    code = build(CASES["callback-data"])
    assert "from aiogram import Bot, Dispatcher, F" in code
    harness = Harness(code, "filters_callback")
    harness.press("/buy")
    assert harness.session.texts() == ["hi"]
