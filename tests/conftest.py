from pathlib import Path

import pytest

import siot

ROOT_DIR = Path(__file__).parent.parent


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
def examples() -> Path:
    return ROOT_DIR / 'examples'
