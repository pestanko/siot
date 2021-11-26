from pathlib import Path

import pytest

import siot


@pytest.fixture(scope='session', autouse=True)
def _enable_logging():
    siot.load_logger(level='TRACE')


@pytest.fixture()
def workspace(tmp_path: Path) -> siot.Workspace:
    return siot.Workspace(tmp_path)


@pytest.fixture(scope='session')
def data_path() -> Path:
    return Path(__file__).parent / 'data'


@pytest.fixture()
def echocat(workspace) -> siot.Executable:
    return workspace.executable('build/echocat')
