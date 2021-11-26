from pathlib import Path

import pytest

import siot


@pytest.fixture(scope='session', autouse=True)
def _enable_logging():
    siot.load_logger()


@pytest.fixture()
def workspace(tmp_path: Path) -> siot.Workspace:
    return siot.Workspace(tmp_path)


@pytest.fixture()
def hello(workspace) -> siot.Executable:
    return workspace.executable('build/hello')
