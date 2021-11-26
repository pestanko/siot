from pathlib import Path

from siot import Executable, ExecParams, Content


def test_cat_hello_world(echocat: Executable):
    res = echocat.execute(ExecParams(args=["cat"], stdin=Content(text="Hello world!")))

    assert res.exit == 0
    assert res.out().text() == 'Hello world!'
    assert res.err().is_empty()


def test_cat_hello_world_simplified(echocat: Executable):
    res = echocat.execute(args=["cat"], text="Hello world!")

    assert res.exit == 0
    assert res.out().text() == 'Hello world!'
    assert res.err().is_empty()


def test_cat_single_word(echocat: Executable):
    res = echocat.execute(ExecParams(args=["cat"], stdin=Content(text="Hello!")))

    assert res.exit == 0
    assert res.out().text() == 'Hello!'
    assert res.err().is_empty()


def test_cat_hello_world_from_file(echocat: Executable, data_path: Path):
    res = echocat.execute(ExecParams(args=["cat"], stdin=Content(file=data_path / "hello_world.in")))

    assert res.exit == 0
    assert res.out().text() == 'Hello world!\n'
    assert res.err().is_empty()


def test_cat_hello_world_in_file_out_file(echocat: Executable, data_path: Path):
    hello_content = Content(file=data_path / "hello_world.in")
    res = echocat.execute(ExecParams(args=["cat"], stdin=hello_content))

    assert res.exit == 0
    assert res.out() == hello_content
    res.out().assert_content(hello_content)
    assert res.err().is_empty()
