from pathlib import Path

import pytest

import siot


@pytest.fixture(scope='session', autouse=True)
def _enable_logging():
    # Enable the execution logging
    siot.load_logger()


@pytest.fixture()
def workspace(tmp_path: Path) -> siot.Workspace:
    # define the test workspace
    # the execution output will be stored in the workspace
    return siot.Workspace(tmp_path)


@pytest.fixture(scope='session')
def data_path() -> Path:
    # Helper - this fixture defines where your data files files are stored
    # Example: `/tests/data`
    # You should store there (in/out) files that will be used in tests
    return Path(__file__).parent / 'data'


@pytest.fixture()
def echocat(workspace) -> siot.Executable:
    # Register your executable that will be used in the tests
    # The argument of the method is a location of the file
    return workspace.executable('build/echocat')
