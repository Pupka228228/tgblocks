# A fake Telegram for tests: real aiogram, real dispatcher, no network.
#
# The generated bots are the product, so they are executed here exactly the way
# `python bot.py` would run them - only the transport is replaced. Every API call
# the bot makes is recorded, which lets a test assert what a user would see:
# which message was sent, with which keyboard, in which order.

import asyncio
import types

from aiogram import Bot
from aiogram.client.session.base import BaseSession
from aiogram.types import Chat, Message

BOT_TOKEN = "42:TEST_TOKEN"


def _model_fields(model) -> set:
    fields = getattr(model, "model_fields", None)          # pydantic v2
    if fields is None:
        fields = getattr(model, "__fields__", {})          # pydantic v1
    return set(fields)


def _poll_payload() -> dict:
    """A poll payload for the aiogram that is installed.

    Telegram keeps adding required fields (3.31 brought `persistent_id`,
    `allows_revoting` and `members_only`), and an old aiogram rejects what it does
    not know. Asking the model which fields exist keeps the suite green on every
    supported version.
    """
    from aiogram.types import Poll, PollOption

    option = {"text": "a", "voter_count": 0}
    if "persistent_id" in _model_fields(PollOption):
        option["persistent_id"] = "0"

    payload = {
        "id": "1",
        "question": "q",
        "options": [option],
        "total_voter_count": 1,
        "is_closed": False,
        "is_anonymous": False,
        "type": "regular",
        "allows_multiple_answers": False,
    }
    for name, value in (("allows_revoting", False), ("members_only", False)):
        if name in _model_fields(Poll):
            payload[name] = value
    return payload

# The smallest payload Telegram would accept for each kind of message content:
# aiogram validates the update before the dispatcher sees it, so a made-up
# "file_id only" object would fail for dice, polls, stickers and locations.
CONTENT = {
    # Telegram sends photo size variants as a list, biggest last.
    "photo": [{"file_id": "f", "file_unique_id": "u", "width": 1, "height": 1}],
    "sticker": {"file_id": "f", "file_unique_id": "u", "type": "regular", "width": 1,
                "height": 1, "is_animated": False, "is_video": False},
    "voice": {"file_id": "f", "file_unique_id": "u", "duration": 1},
    "video": {"file_id": "f", "file_unique_id": "u", "width": 1, "height": 1,
              "duration": 1},
    "video_note": {"file_id": "f", "file_unique_id": "u", "length": 1, "duration": 1},
    "audio": {"file_id": "f", "file_unique_id": "u", "duration": 1},
    "document": {"file_id": "f", "file_unique_id": "u"},
    "animation": {"file_id": "f", "file_unique_id": "u", "width": 1, "height": 1,
                  "duration": 1},
    "location": {"latitude": 1.0, "longitude": 1.0},
    "contact": {"phone_number": "+100", "first_name": "Tester"},
    # Telegram grows required Poll fields over time (aiogram 3.31 added three).
    # The payload is built for the aiogram that is installed, so the suite runs on
    # any supported version instead of only the newest one.
    "poll": _poll_payload(),
    "dice": {"emoji": "🎲", "value": 3},
}


class FakeSession(BaseSession):
    def __init__(self) -> None:
        super().__init__()
        self.methods = []
        self.me = None

    # ------------------------------------------------------------------ transport
    def _response(self, method):
        from aiogram.types import Message as MessageType

        returning = getattr(method, "__returning__", None)
        if isinstance(returning, type) and issubclass(returning, MessageType):
            return Message(
                message_id=999,
                date=0,
                chat=Chat(id=42, type="private"),
            )
        return True

    async def make_request(self, bot, method, timeout=None):
        self.methods.append(method)
        return self._response(method)

    async def stream_content(self, url, headers=None, timeout=30, chunk_size=65536,
                            raise_for_status=True):
        yield b""

    async def close(self) -> None:
        return None

    # -------------------------------------------------------------------- queries
    def all(self, cls):
        return [method for method in self.methods if isinstance(method, cls)]

    def first(self, cls):
        found = self.all(cls)
        assert found, "no {0} was sent; got {1}".format(
            cls.__name__, [type(m).__name__ for m in self.methods]
        )
        return found[0]

    def texts(self):
        from aiogram.methods import SendMessage

        return [method.text for method in self.all(SendMessage)]

    def reset(self):
        self.methods.clear()


class Harness:
    """A generated bot, mounted on a fake Telegram."""

    def __init__(self, code: str, name: str = "generated_bot") -> None:
        self.code = code
        self.session = FakeSession()
        self.bot = Bot(token=BOT_TOKEN, session=self.session)
        module = types.ModuleType(name)
        module.__file__ = "<generated>"
        exec(compile(code, "<generated>", "exec"), module.__dict__)
        self.module = module
        self.dp = module.dp
        self.session.me = self.bot

    # --------------------------------------------------------------------- updates
    def ask(self, update: dict):
        """Feed one raw update (the JSON Telegram would post) and return the reply."""
        update = dict(update)
        update.setdefault("update_id", len(self.session.methods) + 1)
        return asyncio.run(self.dp.feed_raw_update(self.bot, update))

    def command(self, text: str, chat_id: int = 42, user_id: int = 7):
        return self.ask(message_payload(text, chat_id=chat_id, user_id=user_id))

    def text(self, text: str, chat_id: int = 42, user_id: int = 7, chat_kind: str = ""):
        return self.ask(message_payload(text, chat_id=chat_id, user_id=user_id,
                                        chat_kind=chat_kind))

    def content(self, field: str, chat_id: int = 42):
        return self.ask(message_payload(None, chat_id=chat_id, extra={field: CONTENT[field]}))

    def press(self, data: str, chat_id: int = 42):
        return self.ask(callback_payload(data, chat_id=chat_id))


# ---------------------------------------------------------------------- payloads
def _chat(chat_id: int, kind: str = "private") -> dict:
    return {"id": chat_id, "type": kind}


def _user(user_id: int = 7) -> dict:
    return {"id": user_id, "is_bot": False, "first_name": "Tester", "username": "tester"}


def message_payload(text, chat_id: int = 42, user_id: int = 7, extra=None,
                    message_id: int = 1, chat_kind: str = "") -> dict:
    kind = chat_kind or ("supergroup" if chat_id < 0 else "private")
    message = {
        "message_id": message_id,
        "date": 1700000000,
        "chat": _chat(chat_id, kind),
        "from": _user(user_id),
    }
    if text is not None:
        message["text"] = text
        message["entities"] = (
            [{"type": "bot_command", "offset": 0, "length": len(text)}]
            if text.startswith("/")
            else []
        )
    if extra:
        message.update(extra)
    return {"update_id": message_id, "message": message}


def callback_payload(data: str, chat_id: int = 42, user_id: int = 7) -> dict:
    return {
        "update_id": 5000,
        "callback_query": {
            "id": "cb-1",
            "from": _user(user_id),
            "chat_instance": "instance",
            "data": data,
            "message": {
                "message_id": 2,
                "date": 1700000000,
                "chat": _chat(chat_id),
                "text": "menu",
            },
        },
    }


def edited_payload(text: str, chat_id: int = 42) -> dict:
    return {
        "update_id": 6000,
        "edited_message": {
            "message_id": 3,
            "date": 1700000000,
            "chat": _chat(chat_id),
            "from": _user(),
            "text": text,
            "edit_date": 1700000001,
        },
    }


class FakeSleep:
    """Replaces asyncio.sleep so `delay 5` does not slow the test suite down."""

    def __init__(self) -> None:
        self.delays = []

    async def __call__(self, seconds, *args, **kwargs):
        self.delays.append(seconds)
        await _real_sleep(0)


_real_sleep = asyncio.sleep


def fast_time(monkeypatch) -> FakeSleep:
    fake = FakeSleep()
    for target in (asyncio,):
        monkeypatch.setattr(target, "sleep", fake)
    return fake
