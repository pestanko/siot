from pathlib import Path

from siot import Executable, ExecParams, Content


def test_0(mixed: Executable):
    res = mixed.execute(ExecParams(args=["0"]))

    assert res.exit == 0
    assert res.out().text() == "Square: 0\nCube: 0\n"
    assert res.err().is_empty()


def test_1(mixed: Executable):
    res = mixed.execute(args=["1"])

    assert res.exit == 0
    assert res.out().text() == "Square: 1\nCube: 1\n"
    assert res.err().is_empty()


def test_exit_fail(mixed: Executable):
    res = mixed.execute(args=["1", "2"])

    assert res.exit != 0
    assert res.out().is_empty()
    assert not res.err().is_empty()
