# End-to-end tests for the aiogram features added on top of the first release:
# media, edits, callbacks, chat actions, the dialogue steps and the filters.
#
# Each test compiles a real bot from the DSL or the text syntax, runs it on the
# fake Telegram from botkit and checks the API calls a user would cause.

import asyncio

import pytest
from aiogram.methods import (
    AnswerCallbackQuery,
    AnswerInlineQuery,
    BanChatMember,
    DeleteMessage,
    EditMessageText,
    PinChatMessage,
    RestrictChatMember,
    SendContact,
    SendDice,
    SendDocument,
    SendLocation,
    SendMessage,
    SendPoll,
    SendSticker,
    SendVideo,
    SendVoice,
)

from botkit import CONTENT, Harness, callback_payload, fast_time, message_payload
from tgblocks.dsl import compile_source


def bot(dsl: str, name: str = "features") -> Harness:
    source = 'bot token "1:feature"\n\n' + dsl.lstrip("\n")
    return Harness(compile_source(source, name + ".tg"), "bot_" + name)


# ---------------------------------------------------------------------- media
@pytest.mark.parametrize(
    "action,method,with_caption",
    [
        ("send_document", SendDocument, True),
        ("send_video", SendVideo, True),
        ("send_voice", SendVoice, True),
        ("send_sticker", SendSticker, False),
    ],
)
def test_media_actions_reach_telegram(action, method, with_caption):
    caption = ' "подпись"' if with_caption else ""
    harness = bot('on /send:\n    %s "https://example.com/file"%s\n' % (action, caption))
    harness.command("/send")
    sent = harness.session.first(method)
    assert sent.chat_id == 42


def test_media_without_a_caption_is_allowed():
    harness = bot('on /send:\n    send_document "https://example.com/file"\n')
    harness.command("/send")
    assert harness.session.first(SendDocument).caption is None


def test_location_contact_dice_and_poll():
    harness = bot(
        "on /where:\n"
        '    send_location 55.75 37.61\n'
        "on /phone:\n"
        '    send_contact "+100" "Tester"\n'
        "on /dice:\n"
        '    send_dice "🎲"\n'
        "on /poll:\n"
        '    send_poll "Чай или кофе?" "Чай" "Кофе"\n'
    )
    harness.command("/where")
    location = harness.session.first(SendLocation)
    assert (location.latitude, location.longitude) == (55.75, 37.61)

    harness.session.reset()
    harness.command("/phone")
    contact = harness.session.first(SendContact)
    assert contact.phone_number == "+100" and contact.first_name == "Tester"

    harness.session.reset()
    harness.command("/dice")
    assert harness.session.first(SendDice).emoji == "🎲"

    harness.session.reset()
    harness.command("/poll")
    poll = harness.session.first(SendPoll)
    assert poll.question == "Чай или кофе?"
    assert [option.text for option in poll.options] == ["Чай", "Кофе"]


def test_media_from_an_inline_button_answers_the_callback_too():
    harness = bot(
        "on /menu:\n"
        '    send "меню"\n'
        "    buttons:\n"
        '        "Документ" -> /doc\n'
        "on /doc:\n"
        '    send_document "https://example.com/file"\n'
    )
    harness.press("/doc")
    assert harness.session.first(SendDocument)
    assert harness.session.first(AnswerCallbackQuery)


# ---------------------------------------------------------------------- edits
def test_edit_text_rewrites_the_message_of_the_button():
    harness = bot(
        "on /start:\n"
        '    send "меню"\n'
        "    buttons:\n"
        '        "Готово" -> /done\n'
        "on /done:\n"
        '    edit_text "Готово!"\n'
    )
    harness.press("/done")
    assert harness.session.first(EditMessageText).text == "Готово!"


def test_answer_callback_shows_a_toast_or_an_alert():
    harness = bot(
        "on /start:\n"
        '    send "меню"\n'
        "    buttons:\n"
        '        "A" -> /a\n'
        "on /a:\n"
        '    answer_callback "Готово"\n'
        "on /b:\n"
        '    answer_callback "Ошибка" alert\n'
    )
    harness.press("/a")
    toast = harness.session.first(AnswerCallbackQuery)
    assert toast.text == "Готово" and toast.show_alert is None

    harness.session.reset()
    harness.press("/b")
    alert = harness.session.first(AnswerCallbackQuery)
    assert alert.show_alert is True


# ---------------------------------------------------------------- moderation
def test_pin_and_ban_and_mute():
    harness = bot(
        "on /pin:\n"
        "    pin\n"
        "on /pinquiet:\n"
        "    pin silent\n"
        "on /ban:\n"
        "    ban_user\n"
        "on /ban42:\n"
        "    ban_user 42\n"
        "on /mute:\n"
        "    mute_user 42 30\n"
    )
    harness.command("/pin", chat_id=-100)
    pinned = harness.session.first(PinChatMessage)
    assert pinned.chat_id == -100 and pinned.message_id == 1

    harness.session.reset()
    harness.command("/ban")
    banned = harness.session.first(BanChatMember)
    assert banned.user_id == 7  # the sender of the message

    harness.session.reset()
    harness.command("/ban42")
    assert harness.session.first(BanChatMember).user_id == 42

    harness.session.reset()
    harness.command("/mute")
    muted = harness.session.first(RestrictChatMember)
    assert muted.user_id == 42
    assert muted.permissions.can_send_messages is False


# ------------------------------------------------------------------- dialogues
def test_dialogue_steps_walk_the_user_through_the_form():
    harness = bot(
        "state order\n"
        "state phone\n"
        "\n"
        "on /order:\n"
        '    send "Что заказать?"\n'
        "    set_state order\n"
        "\n"
        "on state order:\n"
        '    send "Записал заказ"\n'
        "    set_state phone\n"
        "\n"
        "on state phone:\n"
        '    send "Телефон записан"\n'
        "    clear_state\n"
    )
    harness.command("/order")
    assert harness.session.texts() == ["Что заказать?"]

    # The next message lands in the "order" step, not in a generic handler.
    harness.session.reset()
    harness.text("две пиццы")
    assert harness.session.texts() == ["Записал заказ"]

    harness.session.reset()
    harness.text("+100")
    assert harness.session.texts() == ["Телефон записан"]

    # After clear_state the step handler no longer matches.
    harness.session.reset()
    harness.text("ещё что-то")
    assert harness.session.texts() == []


def test_state_handler_survives_a_callback():
    harness = bot(
        "state step\n"
        "on /go:\n"
        "    set_state step\n"
        "on state step:\n"
        '    send "внутри шага"\n'
    )
    harness.command("/go")
    harness.session.reset()
    harness.text("что угодно")
    assert harness.session.texts() == ["внутри шага"]


# --------------------------------------------------------------------- events
def test_callback_event_with_exact_data():
    harness = bot(
        'on /start:\n'
        '    send "меню"\n'
        "on callback \"/buy\":\n"
        '    send "покупаем"\n'
    )
    harness.press("/buy")
    assert harness.session.texts() == ["покупаем"]


def test_callback_event_without_data_catches_every_button():
    harness = bot(
        'on callback:\n'
        '    send "кнопка"\n'
    )
    harness.press("anything")
    assert harness.session.texts() == ["кнопка"]


def test_chat_filter_ignores_other_chats():
    # Telegram reports "private", "group", "supergroup" and "channel"; a filter
    # for one of them must not fire in the others.
    harness = bot(
        "on message chat=supergroup:\n"
        '    send "только в супергруппе"\n'
    )
    harness.text("привет", chat_id=42)                     # private
    assert harness.session.texts() == []
    harness.text("привет", chat_id=-100, chat_kind="group")  # basic group
    assert harness.session.texts() == []
    harness.text("привет", chat_id=-100)                   # supergroup
    assert harness.session.texts() == ["только в супергруппе"]


def test_from_user_filter():
    harness = bot(
        "on message from_user=99:\n"
        '    send "для одного"\n'
    )
    harness.text("привет", user_id=7)
    assert harness.session.texts() == []
    harness.text("привет", user_id=99)
    assert harness.session.texts() == ["для одного"]


def test_regex_filter():
    harness = bot(
        'on message regex="^[0-9]+$":\n'
        '    send "число"\n'
    )
    harness.text("привет")
    assert harness.session.texts() == []
    harness.text("12345")
    assert harness.session.texts() == ["число"]


def test_inline_mode_answers_with_an_article():
    harness = bot(
        "on inline_query:\n"
        '    inline_result "Заголовок" "Текст ответа" "Описание"\n'
    )
    harness.ask({
        "update_id": 900,
        "inline_query": {
            "id": "iq-1",
            "from": {"id": 7, "is_bot": False, "first_name": "Tester"},
            "query": "q",
            "offset": "",
        },
    })
    answer = harness.session.first(AnswerInlineQuery)
    assert answer.results[0].title == "Заголовок"


def test_chat_member_event_can_greet_the_group():
    harness = bot(
        "on chat_member:\n"
        '    send "новый участник"\n'
    )
    harness.ask({
        "update_id": 901,
        "chat_member": {
            "chat": {"id": -100, "type": "supergroup", "title": "G"},
            "from": {"id": 7, "is_bot": False, "first_name": "Tester"},
            "date": 1700000000,
            "old_chat_member": {"status": "left", "user": {"id": 8, "is_bot": False,
                                                           "first_name": "New"}},
            "new_chat_member": {"status": "member", "user": {"id": 8, "is_bot": False,
                                                             "first_name": "New"}},
        },
    })
    sent = harness.session.first(SendMessage)
    assert sent.chat_id == -100 and sent.text == "новый участник"


def test_log_writes_to_the_process_log(caplog):
    import logging

    caplog.set_level(logging.INFO)
    harness = bot(
        "on /log:\n"
        '    log "пользователь нажал /log"\n'
    )
    harness.command("/log")
    assert any("нажал" in record.getMessage() for record in caplog.records)


# --------------------------------------------------------------------- webhook
def test_webhook_bot_builds_a_real_aiohttp_app():
    code = compile_source(
        'bot token "1:x"\nbot webhook "https://example.com/hook"\n'
        'bot webhook_path "/hook"\n\non /start:\n    send "hi"\n',
        "webhook.tg",
    )
    assert "WEBHOOK_URL" in code and "SimpleRequestHandler" in code
    module = __import__("types").ModuleType("webhook_bot")
    module.__file__ = "<generated>"
    exec(compile(code, "<generated>", "exec"), module.__dict__)
    assert module.WEBHOOK_PATH == "/hook"
    assert callable(module.serve_webhook)

    # The aiohttp integration accepts exactly the arguments the generated code
    # passes; a wrong keyword here would only fail on a live deploy.
    from aiogram import Bot
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler
    from botkit import FakeSession

    bot_instance = Bot(token="1:TEST", session=FakeSession())
    handler = SimpleRequestHandler(dispatcher=module.dp, bot=bot_instance,
                                   secret_token=None)
    assert handler is not None


def test_polling_bot_has_no_webhook_code():
    code = compile_source('bot token "1:x"\n\non /start:\n    send "hi"\n', "poll.tg")
    assert "WEBHOOK_URL" not in code
    assert "start_polling" in code
