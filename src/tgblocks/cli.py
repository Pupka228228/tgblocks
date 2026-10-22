# Command line interface: run, compile, check and the visual editor.

from __future__ import annotations

import argparse
import os
import runpy
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

from . import __version__
from .dsl.codegen import generate
from .dsl.parser import DSLParseError, parse_file
from .runner import missing_token_error, usable_token


def _print_warnings(bot, stream) -> None:
    for warning in getattr(bot, "warnings", ()):
        print("warning: {0}".format(warning), file=stream)


def _describe(handler) -> str:
    # One column that actually distinguishes two handlers of the same kind.
    if handler.kind == "command":
        return handler.command or "/"
    if handler.kind == "state":
        return "state[{0}]".format(handler.state)
    if handler.kind == "callback":
        return "callback[{0}]".format(handler.data) if handler.data else "callback"
    extras = []
    if handler.patterns:
        extras.append(", ".join(handler.patterns))
    if handler.chat:
        extras.append("chat=" + handler.chat)
    if handler.from_user:
        extras.append("from_user={0}".format(handler.from_user))
    if handler.regex:
        extras.append("regex=" + handler.regex)
    return "{0}[{1}]".format(handler.kind, "; ".join(extras)) if extras else handler.kind


def cmd_check(args: argparse.Namespace) -> int:
    bot = parse_file(args.file)
    events = [_describe(handler) for handler in bot.handlers]
    print(
        "OK {0}: handlers={1} - {2}".format(
            args.file, len(bot.handlers), ", ".join(events) or "none"
        )
    )
    _print_warnings(bot, sys.stderr)
    return 0


def cmd_compile(args: argparse.Namespace) -> int:
    bot = parse_file(args.file)
    code = generate(bot, embed_token=args.embed_token)
    _print_warnings(bot, sys.stderr)
    if args.output == "-":
        sys.stdout.write(code)
    else:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(code, encoding="utf-8")
        print("wrote {0} ({1} lines)".format(target, code.count("\n")))
    if not args.embed_token:
        print(
            "note: the token is not written into the file. "
            "Start the bot with TG_BOT_TOKEN=... or pass --embed-token.",
            file=sys.stderr,
        )
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    bot = parse_file(args.file)
    _print_warnings(bot, sys.stderr)

    if args.dry_run:
        # Inspection output must be safe to paste into a repository.
        sys.stdout.write(generate(bot, embed_token=False))
        return 0

    token = args.token or os.environ.get("TG_BOT_TOKEN") or usable_token(bot)
    error = missing_token_error(bot, token)
    if error:
        print("error: {0} (file: {1})".format(error, args.file), file=sys.stderr)
        return 2

    code = generate(bot, embed_token=False)

    try:
        import aiogram  # noqa: F401
    except ImportError:
        print(
            'error: aiogram is not installed. Run: pip install "tgblocks[runtime]"',
            file=sys.stderr,
        )
        return 2

    # Write the generated code to a temp file and execute it as __main__.
    with tempfile.TemporaryDirectory(prefix="tgblocks-") as folder:
        target = Path(folder) / "bot.py"
        target.write_text(code, encoding="utf-8")
        print("starting {0} (Ctrl+C to stop)".format(args.file))
        runpy.run_path(str(target), run_name="__main__")
    return 0


def cmd_proxy(args: argparse.Namespace) -> int:
    from .network import ProxyError, check_proxy, parse_proxy, proxy_hint

    proxies = list(args.proxies)
    if not proxies:
        from os import environ

        configured = environ.get("TG_PROXY", "").strip()
        if not configured:
            print(
                "error: no proxy given and TG_PROXY is not set.\n"
                "       Usage: tgblocks proxy socks5://host:port",
                file=sys.stderr,
            )
            return 2
        proxies = [configured]

    failed = 0
    for url in proxies:
        try:
            parse_proxy(url)
        except ProxyError as error:
            print("error: {0}: {1}".format(url, error), file=sys.stderr)
            failed += 1
            continue
        works, message, seconds = check_proxy(url, timeout=args.timeout)
        mark = "OK  " if works else "FAIL"
        print("{0} {1}  ({2:.1f} c)  {3}".format(mark, url, seconds, message))
        if works:
            for line in proxy_hint(url).splitlines():
                print("     {0}".format(line))
        else:
            failed += 1
    return 0 if not failed else 1


def cmd_visual(args: argparse.Namespace) -> int:
    from .visual.server import serve

    serve(
        host=args.host,
        port=args.port,
        open_browser=not args.no_browser,
        view=args.view,
        allow_remote=args.allow_remote,
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tgblocks",
        description="A tiny text DSL and three visual editors for Telegram bots. "
        "Run `tgblocks` alone to open the editor, or `tgblocks bot.tg` to start a bot.",
        epilog="examples: tgblocks | tgblocks bot.tg | tgblocks compile bot.tg -o bot.py",
    )
    parser.add_argument(
        "--version", action="version", version="tgblocks {0}".format(__version__)
    )
    subparsers = parser.add_subparsers(dest="command", metavar="command")

    run_parser = subparsers.add_parser("run", help="compile a .tg file and start the bot")
    run_parser.add_argument("file", help="path to a .tg file")
    run_parser.add_argument("--token", help="bot token (overrides the DSL and the env)")
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the generated aiogram code instead of starting the bot",
    )
    run_parser.set_defaults(func=cmd_run)

    compile_parser = subparsers.add_parser(
        "compile", help="translate a .tg file into aiogram 3 Python code"
    )
    compile_parser.add_argument("file", help="path to a .tg file")
    compile_parser.add_argument(
        "-o", "--output", default="-", help="output file, or - for stdout (default)"
    )
    compile_parser.add_argument(
        "--embed-token",
        action="store_true",
        help="write the token from the .tg file into the output (off by default: "
        "generated bots read TG_BOT_TOKEN)",
    )
    compile_parser.set_defaults(func=cmd_compile)

    check_parser = subparsers.add_parser("check", help="validate a .tg file only")
    check_parser.add_argument("file", help="path to a .tg file")
    check_parser.set_defaults(func=cmd_check)

    proxy_parser = subparsers.add_parser(
        "proxy", help="check that a proxy can reach api.telegram.org"
    )
    proxy_parser.add_argument(
        "proxies", nargs="*",
        help="proxy URLs: socks5://host:port, socks4://, http://, https:// "
        "(default: TG_PROXY)",
    )
    proxy_parser.add_argument(
        "--timeout", type=float, default=8.0, help="seconds per proxy (default 8)"
    )
    proxy_parser.set_defaults(func=cmd_proxy)

    visual_parser = subparsers.add_parser(
        "visual", help="open the local visual editor in a browser"
    )
    visual_parser.add_argument("--host", default="127.0.0.1", help="bind address")
    visual_parser.add_argument("--port", type=int, default=8765, help="port (default 8765)")
    visual_parser.add_argument(
        "--view",
        choices=["nodes", "blocks", "text"],
        default="nodes",
        help="editor at / : nodes (boxes), blocks (Blockly) or text",
    )
    visual_parser.add_argument(
        "--no-browser", action="store_true", help="do not open a browser window"
    )
    visual_parser.add_argument(
        "--allow-remote",
        action="store_true",
        help="allow --host other than 127.0.0.1 (the editor can run generated code)",
    )
    visual_parser.set_defaults(func=cmd_visual)

    return parser


COMMANDS = {"run", "compile", "check", "visual"}


def _is_bot_file(argument: str) -> bool:
    # `tgblocks bot.tg` is shorthand for `tgblocks run bot.tg`: the command has to
    # work from any folder, without remembering a subcommand.
    if not argument or argument.startswith("-") or argument in COMMANDS:
        return False
    if argument.lower().endswith((".tg", ".txt", ".py")):
        return True
    return Path(argument).is_file()


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    # A redirected stdout on Windows uses the ANSI codepage; without this, any
    # character outside it (a Cyrillic bot name, for example) would raise
    # UnicodeEncodeError instead of printing.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):  # pragma: no cover - exotic streams
            pass
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments:
        # Bare `tgblocks`: the editor is what people mean, and it is also what
        # the README promises.
        arguments = ["visual"]
    elif _is_bot_file(arguments[0]):
        arguments = ["run"] + arguments
    elif arguments[0].startswith("-") and arguments[0] not in ("-h", "--help", "--version"):
        # `tgblocks --port 9000` is the same as `tgblocks visual --port 9000`:
        # the subcommand is optional, the flags are not second-class citizens.
        arguments = ["visual"] + arguments
    args = parser.parse_args(arguments)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    try:
        return args.func(args) or 0
    except DSLParseError as error:
        print(error.render(getattr(args, "file", "<dsl>")), file=sys.stderr)
        return 1
    except FileNotFoundError as error:
        print("error: {0}".format(error), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\nstopped", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
