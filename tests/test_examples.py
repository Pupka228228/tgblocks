# Every example in the repository must compile, import into aiogram and answer
# the messages it advertises. Examples rot faster than code, so they live under
# the same checks as the tests themselves.

import pathlib

import pytest

from botkit import Harness, fast_time
from tgblocks.convert import spec_to_blocks_xml, spec_to_nodes, spec_to_text, board_to_spec
from tgblocks.dsl import compile_source
from tgblocks.dsl.parser import parse_file

EXAMPLES = pathlib.Path(__file__).resolve().parents[1] / "examples"


def examples():
    return sorted(EXAMPLES.glob("*.tg"))


def test_there_are_examples():
    assert examples(), "the examples directory is empty"


@pytest.mark.parametrize("path", examples(), ids=lambda item: item.name)
def test_example_compiles_and_imports(path):
    pytest.importorskip("aiogram")
    source = path.read_text(encoding="utf-8")
    code = compile_source(source, path.name)
    harness = Harness(code, "example_" + path.stem.replace("-", "_"))
    assert harness.dp is not None
    # A bot from the examples must actually answer /start.
    harness.command("/start")
    assert harness.session.methods, "the example bot answered nothing to /start"


@pytest.mark.parametrize("path", examples(), ids=lambda item: item.name)
def test_example_survives_all_three_editors(path):
    spec = parse_file(str(path))
    canonical = spec_to_text(spec)
    board = spec_to_nodes(spec)
    assert spec_to_text(board_to_spec(board)) == canonical
    xml = spec_to_blocks_xml(spec)
    assert 'type="tg_bot"' in xml


def test_the_full_example_uses_the_new_features():
    text = (EXAMPLES / "full.tg").read_text(encoding="utf-8")
    for feature in ("set_state", "clear_state", "send_poll", "send_document",
                    "answer_callback", "edit_text", "ban_user", "chat=supergroup",
                    "regex=", "log "):
        assert feature in text, feature


def test_the_full_example_walks_the_order_dialogue():
    source = (EXAMPLES / "full.tg").read_text(encoding="utf-8")
    harness = Harness(compile_source(source, "full.tg"), "example_full")
    harness.command("/order")
    assert harness.session.texts() == ["Что заказать?"]
    harness.session.reset()
    harness.text("две пиццы")
    assert harness.session.texts() == ["Записал. Теперь телефон?"]
    harness.session.reset()
    harness.text("+100")
    assert harness.session.texts() == ["Готово! Заказ принят."]


def test_the_full_example_answers_its_menu_buttons():
    source = (EXAMPLES / "full.tg").read_text(encoding="utf-8")
    harness = Harness(compile_source(source, "full.tg"), "example_full_buttons")
    harness.press("/buy")
    assert "Покупаем!" in harness.session.texts()


def test_the_full_example_media_commands(monkeypatch):
    fast_time(monkeypatch)
    source = (EXAMPLES / "full.tg").read_text(encoding="utf-8")
    harness = Harness(compile_source(source, "full.tg"), "example_full_media")
    for command in ("/photo", "/doc", "/poll", "/where", "/phone"):
        harness.session.reset()
        harness.command(command)
        assert harness.session.methods, command
