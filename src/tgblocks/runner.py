# Run a bot whose DSL lives inside a normal .py file.
#
#     from tgblocks import run
#
#     run(
#         '''
#     bot token "123456:ABC"
#
#     on /start:
#         send "Hi!"
#     '''
#     )
#
# Why a string and not raw DSL in a .py file? Python parses a script before any
# installed package gets a chance to run, so `bot token "..."` at module level is
# a SyntaxError regardless of what pip installed. Keeping the DSL in a string
# leaves the file valid Python: `python bot.py` and the IDE Run button just work.

from __future__ import annotations

import os
from typing import Optional

from .dsl.codegen import generate
from .dsl.parser import BotSpec, parse

# Tokens that obviously are placeholders: refuse to start a bot with them.
PLACEHOLDER_TOKENS = {"", "PASTE_YOUR_TOKEN", "123456:REPLACE_WITH_YOUR_TOKEN"}


def compile_string(source: str, filename: str = "<embedded>") -> str:
    # DSL text -> aiogram 3 source code, without executing anything.
    return generate(parse(source, filename))


def usable_token(spec: BotSpec) -> Optional[str]:
    # The token declared in the .tg file, unless it is an obvious placeholder.
    if spec.token and spec.token not in PLACEHOLDER_TOKENS:
        return spec.token
    return None


def missing_token_error(spec: BotSpec, token: Optional[str] = None) -> Optional[str]:
    # Store an explicit token and explain the problem when there is none.
    if token:
        os.environ["TG_BOT_TOKEN"] = token
        return None
    if os.environ.get("TG_BOT_TOKEN"):
        return None
    if not spec.token or spec.token in PLACEHOLDER_TOKENS:
        return (
            "no bot token: pass token=..., set TG_BOT_TOKEN, "
            'or replace bot token "PASTE_YOUR_TOKEN"'
        )
    return None


def run_spec(
    spec: BotSpec,
    token: Optional[str] = None,
    filename: str = "<embedded>",
) -> None:
    # Execute an already built BotSpec (used by run() and by the builder API).
    error = missing_token_error(spec, token)
    if error:
        raise SystemExit("tgblocks: {0}".format(error))

    try:
        import aiogram  # noqa: F401
    except ImportError:
        raise SystemExit(
            'tgblocks: aiogram is not installed. Run: pip install "tgblocks[runtime]"'
        )

    code = generate(spec)
    namespace = {"__name__": "__main__", "__file__": filename, "__package__": None}
    exec(compile(code, filename, "exec"), namespace)


def run(
    source: str,
    token: Optional[str] = None,
    filename: str = "<embedded>",
) -> None:
    # Compile DSL text and start polling. Blocks until Ctrl+C.
    run_spec(parse(source, filename), token=token, filename=filename)
