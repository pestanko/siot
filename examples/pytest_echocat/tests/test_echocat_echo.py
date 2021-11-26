from siot import Executable, ExecParams


def test_echo_hello_world(echocat: Executable):
    res = echocat.execute(ExecParams(args=["echo", "Hello", "world"]))

    assert res.exit == 0
    assert res.out().text() == 'Hello world\n'
    assert res.err().is_empty()


def test_echo_single_word(echocat: Executable):
    res = echocat.execute(ExecParams(args=["echo", "Hello"]))

    assert res.exit == 0
    assert res.out().text() == 'Hello\n'
    assert res.err().is_empty()
