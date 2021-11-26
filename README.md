# Simple Input Output Testing Helper (SIOT)

Build status: ![SIOT Tests Pipeline](https://github.com/pestanko/siot/actions/workflows/tests.yml/badge.svg)

This simple helper provides simple wrappers over file execution, see the [examples](/examples)

## Getting started

In order to "install" this package, all you need to do is to copy a single file [`siot.py`](./siot.py) to your root
folder.

```shell
cd <TO YOUR DIRECTORY>
wget https://raw.github.com/pestanko/siot/siot.py
```

And you can start developing tests.

## Example usage

More examples can be found in [examples](/examples) directory.

### Pytest example

In order to run tests written using the pytest, you need to have installed the [``pytest``](https://docs.pytest.org/)

#### Global setup: conftest.py

File where you can define your fixtures and setup.

```python
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
```

#### Example test

You can define multiple tests in separate files, for example:

```python
from pathlib import Path

from siot import Executable, ExecParams, Content


def test_echo_hello_world(echocat: Executable):
    # Execute the the executable with specified params
    res = echocat.execute(ExecParams(args=["cat"], stdin=Content(text="Hello world!")))

    assert res.exit == 0  # assert that exit code is zero
    assert res.out().text() == 'Hello world!'  # out is stdout
    assert res.out().size() != 0  # Take a look at class siot.Content for more methods
    assert res.err().is_empty()  # err is stderr


def test_echo_single_word(echocat: Executable):
    res = echocat.execute(ExecParams(args=["cat"], stdin=Content(text="Hello!")))

    assert res.exit == 0
    assert res.out().text() == 'Hello!'
    assert res.err().is_empty()


def test_echo_hello_world_from_file(echocat: Executable, data_path: Path):
    res = echocat.execute(ExecParams(args=["cat"], stdin=Content(file=data_path / "hello_world.in")))

    assert res.exit == 0
    assert res.out().text() == 'Hello world!\n'
    assert res.err().is_empty()


def test_echo_hello_world_in_file_out_file(echocat: Executable, data_path: Path):
    hello_content = Content(file=data_path / "hello_world.in")
    res = echocat.execute(ExecParams(args=["cat"], stdin=hello_content))

    assert res.exit == 0
    assert res.out() == hello_content
    res.out().assert_content(hello_content)
    assert res.err().is_empty()
```

This example is from [examples for echocat](examples/pytest_echocat)

In order to run this example you need to copy the ``siot.py``
to the ``examples/pytest_echocat`` (or start the virtualenv and install the package)

```shell
cp siot.py examples/pytest_echocat/
cd examples/pytest_echocat

# Execute the tests
pytest
```

### UnitTest Example

Can be found in: [examples/unittest_echocat](examples/unittest_echocat)

In order to run the example you need to again copy the ``siot.py``
to the example directory

```shell
cp siot.py examples/unittest_echocat/
cd examples/unittest_echocat

# Execute the tests
python -m unittest tests/*.py
```

### Test Scenario with build and [`cut.h`](https://github.com/spito/testing)

This test scenario is using unit testing with [`cut.h`](https://github.com/spito/testing)
and the io testing using the helper - it will also build a solution using ``cmake`` and `make`

The scenario can be found here: [examples/pytest_cut_mixed](examples/pytest_cut_mixed)


```shell
cp siot.py examples/pytest_cut_mixed/
cd examples/pytest_cut_mixed

# Execute the tests
pytest
```
