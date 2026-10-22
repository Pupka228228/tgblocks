# Whitespace around service values: a pasted proxy often arrives with a leading
# tab or a trailing space ("\tsocks4://1.2.3.4:1080"), and that silently breaks
# the connection while looking correct in the field.

import pytest

from botkit import Harness
from tgblocks.convert import board_to_spec, spec_to_nodes, spec_to_text
from tgblocks.dsl import compile_source
from tgblocks.dsl.parser import parse
from tgblocks.textlang import parse_text


def test_the_dsl_strips_the_token_and_the_proxy():
    spec = parse('bot token "  1:ABC  "\nbot proxy "  socks5://1.2.3.4:1080  "\n'
                 'bot name "  с пробелами  "\n\non /start:\n    send "hi"\n')
    assert spec.token == "1:ABC"
    assert spec.proxy == "socks5://1.2.3.4:1080"
    # A bot name is a display string: its spaces are the author's business.
    assert spec.name == "  с пробелами  "


def test_the_dsl_strips_a_tab_that_comes_with_a_paste():
    spec = parse('bot token "1:ABC"\nbot proxy "\tsocks4://171.245.71.144:1086"\n\n'
                 'on /start:\n    send "hi"\n')
    assert spec.proxy == "socks4://171.245.71.144:1086"
    # The generated bot must carry the clean value.
    code = compile_source('bot token "1:ABC"\nbot proxy "\tsocks4://171.245.71.144:1086"\n'
                          '\n\non /start:\n    send "hi"\n')
    assert 'os.environ.get("TG_PROXY", "socks4://171.245.71.144:1086")' in code


def test_webhook_values_are_stripped_too():
    spec = parse('bot token "1:x"\nbot webhook " https://e.com/hook "\n'
                 'bot webhook_path " /hook "\n\non /start:\n    send "hi"\n')
    assert spec.webhook == "https://e.com/hook"
    assert spec.webhook_path == "/hook"


def test_a_board_with_a_padded_token_produces_clean_text():
    spec = parse_text('token("  1:ABC  ")\n\non.command("/start"):\n    send("hi")\n')
    board = spec_to_nodes(spec)
    # Simulate the value as it sits in the editor: with a stray tab.
    board["nodes"][board["rootId"]]["props"]["token"] = "\t1:ABC\t"
    board["nodes"][board["rootId"]]["props"]["proxy"] = " socks4://1.2.3.4:1080 "
    rebuilt = board_to_spec(board)
    assert rebuilt.token == "1:ABC"
    assert rebuilt.proxy == "socks4://1.2.3.4:1080"
    assert 'token("1:ABC")' in spec_to_text(rebuilt)
    assert 'proxy("socks4://1.2.3.4:1080")' in spec_to_text(rebuilt)


def test_text_syntax_token_is_stripped(monkeypatch):
    monkeypatch.delenv("TG_BOT_TOKEN", raising=False)
    spec = parse_text('token("  1:ABC  ")\n\non.command("/start"):\n    send("hi")\n')
    assert spec.token == "1:ABC"
