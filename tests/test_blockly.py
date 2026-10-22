# Blockly definitions are generated on the server.
#
# Blockly requires placeholders to restart at %1 in every message: message0 uses
# args0 with %1, message1 uses args1 with %1 again. A global "%2" in message1
# makes Blockly reject the whole definition with "Message index %2 out of range",
# which silently emptied the block editor's palette.

import re

import pytest

from tgblocks import model
from tgblocks.visual.server import _Handler  # noqa: F401 - import guard


def blocks(lang: str = "ru"):
    return model.blockly_blocks(lang)


def test_every_block_is_well_formed_for_blockly():
    for block in blocks():
        assert block["type"].startswith("tg_")
        assert re.match(r"^#[0-9a-fA-F]{6}$", block["colour"]), block["type"]
        messages = [key for key in block if key.startswith("message")]
        assert messages, block["type"]
        for message in messages:
            index = message[len("message"):]
            args = block.get("args" + index)
            placeholders = re.findall(r"%(\d+)", block[message])
            if not args:
                # A block with no fields is just a caption.
                assert placeholders == [], "{0}.{1}".format(block["type"], message)
                continue
            assert placeholders == ["1"] * len(args), (
                "{0}.{1} = {2!r} with {3} arg(s): placeholders must be %1 per "
                "message".format(block["type"], message, block[message], len(args)))


def test_no_global_placeholder_numbering_sneaks_in():
    for block in blocks():
        for key, value in block.items():
            if key.startswith("message"):
                numbers = [int(item) for item in re.findall(r"%(\d+)", value)]
                assert numbers in ([], [1]), "{0}.{1}: {2!r}".format(
                    block["type"], key, value)


def test_every_action_has_a_block():
    names = {block["type"] for block in blocks()}
    for spec in model.ACTIONS:
        if spec.kind in model.STRUCTURAL_BLOCKS:
            continue
        expected = "tg_" + ("photo" if spec.kind == "send_photo" else spec.kind)
        assert expected in names, expected


def test_blocks_use_the_interface_language():
    russian = {block["type"]: block for block in blocks("ru")}
    english = {block["type"]: block for block in blocks("en")}
    assert russian["tg_send_document"]["message0"].startswith("Документ")
    assert english["tg_send_document"]["message0"].startswith("Document")
    assert english["tg_send_poll"]["message1"].startswith("Options")
    assert russian["tg_send_poll"]["message1"].startswith("Варианты")


def test_field_names_match_what_the_xml_reader_expects():
    # convert.blocks_xml_to_spec reads <field name="PARAM"> in upper case.
    for spec in model.ACTIONS:
        if spec.kind in model.STRUCTURAL_BLOCKS:
            continue
        block = [item for item in blocks()
                 if item["type"] == "tg_" + ("photo" if spec.kind == "send_photo"
                                             else spec.kind)][0]
        expected = {param.name.upper() for param in spec.params}
        found = set()
        for key, value in block.items():
            if key.startswith("args"):
                for arg in value:
                    found.add(arg["name"])
        assert found == expected, spec.kind


def test_the_schema_carries_the_blocks_and_the_language():
    ru = model.schema()
    en = model.schema("en")
    assert ru["lang"] == "ru" and en["lang"] == "en"
    assert len(ru["blocks"]) == len(en["blocks"]) > 20
    assert ru["actions"][0]["label"] != en["actions"][0]["label"]
    # Every label must have an English twin, or the switch would show Russian.
    for action in en["actions"]:
        assert action["label"] == action["label_en"]
    for event in en["events"]:
        assert event["label"] == event["label_en"]
