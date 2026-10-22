# scaffold.py carries a copy of the whole project, because it must work in an
# empty folder with nothing but itself. That copy used to drift (it was 600 lines
# behind, and the project it generated had a broken editor page), so these tests
# hold the copy and the tree together. Regenerate with:
#
#     python tools/build_scaffold.py

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SCAFFOLD = ROOT / "scaffold.py"
HAS_TOOL = SCAFFOLD.exists() and (TOOLS / "build_scaffold.py").exists()

pytestmark = pytest.mark.skipif(
    not HAS_TOOL,
    reason="scaffold.py and tools/ are not part of this copy of the project",
)

build_scaffold = None
if HAS_TOOL:
    # A generated project carries these tests but not the generator itself, so
    # the import must not run there (a module-level ImportError is not skippable).
    sys.path.insert(0, str(TOOLS))
    import build_scaffold  # noqa: E402

import importlib.util  # noqa: E402


def load_scaffold():
    spec = importlib.util.spec_from_file_location("tgblocks_scaffold", SCAFFOLD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def scaffold():
    return load_scaffold()


def test_payload_is_regenerated_from_the_tree():
    # --check exits 1 and prints an explanation when someone edited a source file
    # without rebuilding the payload.
    assert build_scaffold.main(["--check"]) == 0


def test_every_embedded_file_matches_the_disk(scaffold):
    for relative, content in scaffold.FILES.items():
        on_disk = (ROOT / relative)
        assert on_disk.is_file(), "embedded file is gone: " + relative
        assert on_disk.read_text(encoding="utf-8") == content, (
            "embedded copy of {0} is stale".format(relative)
        )


def test_every_project_file_is_embedded(scaffold):
    missing = sorted(set(build_scaffold.collect_files()) - set(scaffold.FILES))
    assert missing == []


def test_generated_project_is_identical(scaffold, tmp_path):
    target = scaffold.create_project(str(tmp_path / "out"))
    written = sorted(
        item.relative_to(target).as_posix()
        for item in target.rglob("*")
        if item.is_file()
    )
    assert written == sorted(scaffold.FILES)
    for relative in written:
        assert (target / relative).read_text(encoding="utf-8") == scaffold.FILES[relative]


def test_generated_project_is_installable_python_package(scaffold, tmp_path):
    target = scaffold.create_project(str(tmp_path / "out"))
    assert (target / "pyproject.toml").exists()
    assert (target / "src" / "tgblocks" / "__init__.py").exists()
    assert (target / "src" / "tgblocks" / "visual" / "static" / "nodes.html").exists()
    # The page asks for this file over HTTP: a copy without it cannot run.
    assert (target / "src" / "tgblocks" / "visual" / "static" / "tgblocks-project.js").exists()
    assert (target / "tests" / "test_sync.py").exists()
