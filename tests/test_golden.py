# Golden tests: the generated code is the product, so it is pinned byte for byte.
#
# On top of comparing with tests/golden/, every case must also survive two harder
# checks: it must be valid Python (ast.parse) and it must import inside the real
# aiogram package - that is what catches a wrong filter name or a missing type,
# not the string assertions scattered in the other test modules.
#
# Regenerate the goldens on purpose (after reviewing the diff!):
#     python -m pytest tests/test_golden.py --update-golden

import ast
import importlib
import os
import sys
import types

import pytest

from corpus import CORPUS
from tgblocks.dsl import compile_source
from tgblocks.textlang import compile_text

GOLDEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "golden")


def generate(case) -> str:
    if case.syntax == "dsl":
        return compile_source(case.source, case.name + ".tg")
    return compile_text(case.source, case.name + ".txt")


def golden_path(case) -> str:
    return os.path.join(GOLDEN_DIR, case.name + ".py")


def import_generated(code: str, name: str):
    # Execute the generated module the way `python bot.py` would, minus __main__:
    # importing it registers every handler on a real aiogram Dispatcher.
    module = types.ModuleType(name)
    module.__file__ = "<generated:" + name + ">"
    sys.modules[name] = module
    try:
        exec(compile(code, module.__file__, "exec"), module.__dict__)
    finally:
        sys.modules.pop(name, None)
    return module


@pytest.mark.parametrize("case", CORPUS, ids=[case.name for case in CORPUS])
def test_generated_code_is_valid_python(case):
    ast.parse(generate(case), case.name + ".py")


@pytest.mark.parametrize("case", CORPUS, ids=[case.name for case in CORPUS])
def test_generated_code_imports_into_aiogram(case):
    pytest.importorskip("aiogram")
    module = import_generated(generate(case), "tgblocks_golden_" + case.name.replace("-", "_"))
    assert module.BOT_TOKEN
    assert module.dp is not None
    handlers = (
        len(module.dp.message.handlers)
        + len(module.dp.callback_query.handlers)
        + len(module.dp.edited_message.handlers)
    )
    assert handlers >= 1


@pytest.mark.parametrize("case", CORPUS, ids=[case.name for case in CORPUS])
def test_generated_code_matches_golden(case):
    code = generate(case)
    if "--update-golden" in sys.argv or os.environ.get("UPDATE_GOLDEN"):
        os.makedirs(GOLDEN_DIR, exist_ok=True)
        with open(golden_path(case), "w", encoding="utf-8", newline="\n") as handle:
            handle.write(code)
        return
    assert os.path.exists(golden_path(case)), (
        "no golden file for {0}; run with --update-golden".format(case.name)
    )
    with open(golden_path(case), "r", encoding="utf-8", newline="") as handle:
        expected = handle.read().replace("\r\n", "\n")
    assert code == expected, (
        "generated code for {0} changed; review the diff, then rerun with "
        "--update-golden".format(case.name)
    )
