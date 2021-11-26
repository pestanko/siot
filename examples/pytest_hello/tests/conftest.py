from pathlib import Path

import pytest

import siot


@pytest.fixture()
def workspace(tmp_path: Path) -> siot.Workspace:
    return siot.Workspace(tmp_path)


@pytest.fixture()
def hello(workspace) -> siot.Executable:
    return workspace.executable('build/hello')
