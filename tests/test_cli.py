# CLI tests: the command line is the part people script, so it is tested through
# main() rather than by hand. The token handling is a security property now:
# `compile` must not write the secret into the artefact unless asked.

import os

import pytest

from tgblocks.cli import main

BOT = 'bot token "123456:SECRET"\n\non /start:\n    send "hi"\n'


@pytest.fixture(autouse=True)
def no_leaked_token():
    # `run` exports the token into the environment on purpose; keep that from
    # leaking into the next test.
    before = os.environ.pop("TG_BOT_TOKEN", None)
    yield
    os.environ.pop("TG_BOT_TOKEN", None)
    if before is not None:
        os.environ["TG_BOT_TOKEN"] = before


@pytest.fixture()
def bot_file(tmp_path):
    path = tmp_path / "bot.tg"
    path.write_text(BOT, encoding="utf-8")
    return path


def run(argv, capsys):
    code = main(argv)
    out, err = capsys.readouterr()
    return code, out, err


def test_version(capsys):
    with pytest.raises(SystemExit) as info:
        main(["--version"])
    assert info.value.code == 0


def test_flags_without_a_subcommand_mean_the_editor(monkeypatch):
    seen = {}

    def fake_visual(args):
        seen["port"] = args.port
        seen["browser"] = args.no_browser
        return 0

    monkeypatch.setattr("tgblocks.cli.cmd_visual", fake_visual)
    assert main(["--port", "9000", "--no-browser"]) == 0
    assert seen["port"] == 9000
    assert seen["browser"] is True


def test_bare_command_opens_the_editor(monkeypatch):
    # `tgblocks` with no arguments must start the visual editor: that is the
    # command people type, and it has to work from any folder.
    seen = {}

    def fake_visual(args):
        seen["view"] = args.view
        seen["port"] = args.port
        return 0

    monkeypatch.setattr("tgblocks.cli.cmd_visual", fake_visual)
    assert main([]) == 0
    assert seen["view"] == "nodes"
    assert seen["port"] == 8765


def test_help_flag_still_prints_the_usage(capsys):
    with pytest.raises(SystemExit) as info:
        main(["--help"])
    assert info.value.code == 0
    out = capsys.readouterr().out
    assert "tgblocks" in out


def test_a_bot_file_runs_without_a_subcommand(bot_file, monkeypatch):
    seen = {}

    def fake_run(args):
        seen["file"] = args.file
        seen["dry"] = args.dry_run
        return 0

    monkeypatch.setattr("tgblocks.cli.cmd_run", fake_run)
    assert main([str(bot_file), "--dry-run"]) == 0
    assert seen["file"] == str(bot_file)
    assert seen["dry"] is True


def test_an_unknown_word_is_a_normal_argument_error(capsys):
    with pytest.raises(SystemExit) as info:
        main(["frobnicate"])
    assert info.value.code == 2


def test_compile_to_stdout_keeps_the_token_out(bot_file, capsys):
    code, out, err = run(["compile", str(bot_file)], capsys)
    assert code == 0
    assert "SECRET" not in out
    assert 'os.environ.get("TG_BOT_TOKEN", "")' in out
    assert "note: the token is not written" in err


def test_compile_embeds_the_token_on_request(bot_file, capsys):
    code, out, _ = run(["compile", str(bot_file), "--embed-token"], capsys)
    assert code == 0
    assert '"123456:SECRET"' in out


def test_compile_writes_a_file(bot_file, tmp_path, capsys):
    target = tmp_path / "out" / "bot.py"
    code, out, _ = run(["compile", str(bot_file), "-o", str(target)], capsys)
    assert code == 0
    assert target.exists()
    assert "wrote" in out
    assert "SECRET" not in target.read_text(encoding="utf-8")


def test_check_reports_the_handlers(bot_file, capsys):
    code, out, _ = run(["check", str(bot_file)], capsys)
    assert code == 0
    assert out.startswith("OK ")
    assert "/start" in out


def test_check_summary_distinguishes_states_and_filters(tmp_path, capsys):
    path = tmp_path / "mixed.tg"
    path.write_text(
        'bot token "1:x"\n\n'
        "state order\n\n"
        'on /start:\n    set_state order\n'
        'on state order:\n    send "ok"\n'
        'on message chat=supergroup:\n    send "g"\n'
        'on callback "/buy":\n    send "b"\n',
        encoding="utf-8",
    )
    code, out, _ = run(["check", str(path)], capsys)
    assert code == 0
    assert "state[order]" in out
    assert "text[chat=supergroup]" in out
    assert "callback[/buy]" in out


def test_dry_run_prints_code_without_a_token(bot_file, capsys, monkeypatch):
    monkeypatch.delenv("TG_BOT_TOKEN", raising=False)
    code, out, _ = run(["run", str(bot_file), "--dry-run"], capsys)
    assert code == 0
    assert "async def" in out
    assert "SECRET" not in out


def test_run_without_a_token_fails_cleanly(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("TG_BOT_TOKEN", raising=False)
    path = tmp_path / "placeholder.tg"
    path.write_text('bot token "PASTE_YOUR_TOKEN"\n\non /start:\n    send "hi"\n',
                    encoding="utf-8")
    code, _, err = run(["run", str(path)], capsys)
    assert code == 2
    assert "no bot token" in err


def test_syntax_error_is_reported_with_a_position(tmp_path, capsys):
    path = tmp_path / "bad.tg"
    path.write_text('bot token "1:x"\n\non /start:\n    send Hi!\n', encoding="utf-8")
    code, _, err = run(["check", str(path)], capsys)
    assert code == 1
    assert "bad.tg:4:5" in err
    assert "hint:" in err


def test_missing_file_is_an_error(capsys):
    code, _, err = run(["check", "nope.tg"], capsys)
    assert code == 2
    assert "not found" in err


def test_run_uses_the_token_from_the_dsl_file(bot_file, capsys, monkeypatch):
    # The generated code carries no token, so `run` must hand it over in the
    # environment - and it must not leak into the printed code.
    monkeypatch.delenv("TG_BOT_TOKEN", raising=False)
    captured = {}

    def fake_run_path(path, run_name=None):
        captured["path"] = path
        captured["env"] = os.environ.get("TG_BOT_TOKEN")
        raise KeyboardInterrupt

    monkeypatch.setattr("tgblocks.cli.runpy.run_path", fake_run_path)
    monkeypatch.setattr("tgblocks.cli.generate", lambda spec, **kw: 'print("stub")')
    code = main(["run", str(bot_file)])
    assert code == 130  # Ctrl+C is a normal stop, not a failure
    assert captured["env"] == "123456:SECRET"
