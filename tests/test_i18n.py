# The English interface is complete: every catalogue word has a translation.
#
# A missing entry falls back to Russian, which shows up as a Russian word inside an
# English palette - exactly the kind of half-translated UI this test prevents.

import pytest

from tgblocks import model
from tgblocks.model import ACTIONS, EVENTS, CHAT_FILTER, FROM_FILTER, REGEX_FILTER


def _catalogue_texts():
    for spec in ACTIONS + EVENTS:
        yield spec.label
        hint = getattr(spec, "hint", "")
        if hint:
            yield hint
        for param in spec.params:
            yield param.label
            if param.hint:
                yield param.hint
            for _value, label in param.choices:
                yield label
    for param in (CHAT_FILTER, FROM_FILTER, REGEX_FILTER):
        yield param.label
        for _value, label in param.choices:
            yield label
    for _value, label in model.KEYBOARD_STYLES:
        yield label
    for _value, label in model.BUTTON_KINDS:
        yield label


def test_every_catalogue_word_has_an_english_twin():
    # A few words are the same in both languages and need no dictionary entry.
    neutral = {"GIF", "web app", "URL", "RTMP", "ID"}
    missing = sorted({text for text in _catalogue_texts()
                      if text and text not in neutral
                      and model.english(text) == text})
    assert missing == [], "нет перевода: {0}".format(missing)


def test_the_schema_is_english_when_asked():
    schema = model.schema("en")
    russian = [action["label"] for action in schema["actions"]
               if action["label"] != action["label_en"]]
    assert russian == []
    for action in schema["actions"]:
        assert action["label"] == model.english(action["label"])
        for param in action["params"]:
            assert param["label"] == model.english(param["label"])


def test_the_default_language_is_english():
    # The editors read /api/schema without ?lang for their first paint.
    assert model.schema("EN")["lang"] == "en"
    assert model.schema("ru")["lang"] == "ru"
    assert model.schema("fr")["lang"] == "ru", "неизвестный язык - русский"
