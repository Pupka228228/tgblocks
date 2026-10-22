# The event panel shows the four filters that matter; the two that a `when`
# condition covers are hidden. They still parse, compile and convert, so an old
# bot that uses them keeps working and is not silently changed.

from tgblocks import model
from tgblocks.convert import (
    blocks_xml_to_spec, board_to_text, spec_to_blocks_xml, spec_to_nodes, spec_to_text,
)
from tgblocks.dsl import compile_source
from tgblocks.dsl.parser import parse
from tgblocks.textlang import compile_text, parse_text


def event_params(kind: str, lang: str = "ru"):
    for event in model.schema(lang)["events"]:
        if event["kind"] == kind:
            return {param["name"]: param for param in event["params"]}
    raise AssertionError(kind)


def test_patterns_are_hidden_in_the_message_event():
    assert event_params("text")["patterns"]["hidden"] is True


def test_the_regex_filter_is_hidden_everywhere():
    # Events that carry a text body get the regex filter; those that do not never
    # had one.
    for kind in ("text", "command"):
        assert event_params(kind)["regex"]["hidden"] is True, kind
    schema_filters = {param["name"]: param for param in model.schema()["filters"]}
    assert schema_filters["regex"]["hidden"] is True
    assert schema_filters["chat"]["hidden"] is False
    assert schema_filters["from_user"]["hidden"] is False


def test_the_visible_filters_are_still_offered():
    for kind in ("text", "photo", "command"):
        params = event_params(kind)
        assert params["chat"]["hidden"] is False
        if "from_user" in params:
            assert params["from_user"]["hidden"] is False


def test_blockly_does_not_offer_a_field_for_a_hidden_filter():
    for block in model.blockly_blocks():
        for key, value in block.items():
            if not key.startswith("args"):
                continue
            for arg in value:
                assert arg["name"] not in {"REGEX", "PATTERNS"}, block["type"]


def test_an_old_bot_with_a_regex_filter_still_compiles():
    source = 'bot token "1:x"\n\non message regex="^[0-9]+$":\n    send "цифры"\n'
    code = compile_source(source, "old.tg")
    assert "regexp" in code.lower()
    assert parse(source, "old.tg").handlers[0].regex == "^[0-9]+$"
    # The text syntax keeps its own spelling: on.message(TEXT, regex="...").
    text = 'token("1:x")\n\non.message(TEXT, regex="^[0-9]+$"):\n    send("цифры")\n'
    assert parse_text(text, "old.txt").handlers[0].regex == "^[0-9]+$"
    assert "regexp" in compile_text(text, "old.txt").lower()


def test_exact_texts_still_parse():
    source = 'bot token "1:x"\n\non message "да", "нет":\n    send "ладно"\n'
    assert tuple(parse(source, "old.tg").handlers[0].patterns) == ("да", "нет")


def test_a_hidden_filter_survives_the_node_board():
    source = 'bot token "1:x"\n\non message regex="^[0-9]+$":\n    send "цифры"\n'
    spec = parse(source, "old.tg")
    board = spec_to_nodes(spec)
    event = [node for node in board["nodes"].values() if node["type"] == "event"][0]
    # No field is drawn for it, but the value must not be dropped on the way back.
    assert event["props"]["regex"] == "^[0-9]+$"
    assert board_to_text(board) == spec_to_text(spec)


def test_the_block_editor_round_trips_it_as_well():
    spec = parse('bot token "1:x"\n\non message regex="^[0-9]+$":\n    send "цифры"\n',
                 "old.tg")
    assert blocks_xml_to_spec(spec_to_blocks_xml(spec)).handlers[0].regex == "^[0-9]+$"
