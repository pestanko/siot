import shutil
from pathlib import Path

import siot
from siot import Workspace


def test_pytest_cut_mixed(workspace: Workspace, examples: Path):
    name = 'pytest_cut_mixed'
    ws = _prepare_ws(workspace, examples, name, build=False)
    res = workspace.execute('python', args=['-m', 'pytest'], cwd=ws)
    assert res.exit == 0


def test_pytest_echocat(workspace: Workspace, examples: Path):
    name = 'pytest_echocat'
    ws = _prepare_ws(workspace, examples, name)
    res = workspace.execute('python', args=['-m', 'pytest'], cwd=ws)
    assert res.exit == 0


def test_pytest_hello(workspace: Workspace, examples: Path):
    name = 'pytest_hello'
    ws = _prepare_ws(workspace, examples, name)
    res = workspace.execute('python', args=['-m', 'pytest'], cwd=ws)
    assert res.exit == 0


def test_unittest_echocat(workspace: Workspace, examples: Path):
    name = 'unittest_echocat'
    ws = _prepare_ws(workspace, examples, name)
    res = workspace.execute(
        'python',
        args=['-m', 'unittest', 'discover', '-s', 'tests'],
        cwd=ws
    )
    assert res.exit == 0


def _prepare_ws(ws: Workspace, examples: Path, name: str,
                build: bool = True, clean: bool = True) -> Path:
    sources = examples / name
    assert sources.exists()
    if clean:
        _clean_build(sources)
    if build:
        siot.build_using_cmake(ws.ws_path, sources)
    # shutil.copy2(examples.parent / 'siot.py', sources)
    return sources


def _clean_build(ws: Path):
    bld = ws / 'build'
    if bld.exists():
        shutil.rmtree(bld, ignore_errors=True)
