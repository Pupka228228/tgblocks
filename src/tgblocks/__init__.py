# tgblocks: a tiny DSL, a text syntax and a visual editor for Telegram bots.
#
# The package is a compiler: .tg DSL or the editor syntax -> aiogram 3 code.
#
#     from tgblocks import parse, generate
#     code = generate(parse(open("bot.tg").read()))
#
#     from tgblocks.textlang import compile_text
#     code = compile_text(open("bot.txt").read())

from .dsl.codegen import generate
from .dsl.parser import BotSpec, DSLParseError, parse, parse_file
from .textlang import compile_text, parse_text

__version__ = "0.2.0"

__all__ = [
    "__version__",
    "BotSpec",
    "DSLParseError",
    "compile_text",
    "generate",
    "parse",
    "parse_file",
    "parse_text",
]
