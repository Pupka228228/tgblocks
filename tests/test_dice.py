# Conditions on the interactive emoji: `when dice == 6`.
#
# The value Telegram reports (message.dice.value) is a number, so the comparison
# is numeric and the two syntaxes agree.

import pytest

from botkit import Harness, message_payload
from tgblocks.convert import board_to_text, blocks_xml_to_spec, spec_to_blocks_xml, \
    spec_to_nodes, spec_to_text
from tgblocks.dsl import compile_source
from tgblocks.dsl.parser import DSLParseError, parse
from tgblocks.textlang import parse_text

DSL = (
    'bot token "1:x"\n\n'
    "on dice:\n"
    "    when dice == 6:\n"
    '        send "six"\n'
    "    when dice != 6:\n"
    '        send "not six"\n'
)


def roll(harness, value):
    return harness.ask(message_payload(None, extra={"dice": {"emoji": "🎲", "value": value}}))


def test_dsl_parses_a_dice_condition():
    spec = parse(DSL)
    conditions = [node.condition for node in spec.handlers[0].actions
                  if hasattr(node, "condition")]
    assert [(item.source, item.op, item.value) for item in conditions] == [
        ("dice", "==", "6"), ("dice", "!=", "6")]


def test_the_generated_bot_compares_the_rolled_number():
    harness = Harness(compile_source(DSL), "dice_bot")
    roll(harness, 6)
    assert harness.session.texts() == ["six"]
    harness.session.reset()
    roll(harness, 2)
    assert harness.session.texts() == ["not six"]


def test_text_syntax_takes_the_dice_source():
    spec = parse_text('token("1:x")\n\non.dice():\n    when("dice", "==", 6):\n'
                      '        send("six")\n')
    condition = spec.handlers[0].actions[0].condition
    assert (condition.source, condition.op, condition.value) == ("dice", "==", "6")

    code = compile_source('bot token "1:x"\n\non dice:\n    when dice == 6:\n'
                          '        send "six"\n')
    assert "dice_value(event) == 6" in code
    assert "def dice_value(event) -> int:" in code


def test_only_equality_makes_sense_for_an_emoji():
    with pytest.raises(DSLParseError) as info:
        parse('bot token "1:x"\n\non dice:\n    when dice contains "6":\n        send "x"\n')
    assert "==" in info.value.message or "только" in info.value.message


def test_a_non_number_is_refused():
    with pytest.raises(DSLParseError):
        parse('bot token "1:x"\n\non dice:\n    when dice == "шесть":\n        send "x"\n')


def test_the_condition_survives_every_editor():
    spec = parse(DSL)
    canonical = spec_to_text(spec)
    assert 'when("dice", "==", 6)' in canonical
    assert board_to_text(spec_to_nodes(spec)) == canonical

    xml = spec_to_blocks_xml(spec)
    assert '<field name="SOURCE">dice</field>' in xml
    assert spec_to_text(blocks_xml_to_spec(xml)) == canonical
