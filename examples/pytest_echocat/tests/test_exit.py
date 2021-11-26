from siot import Executable, ExecParams, Content


def test_echo_hello_world(echocat: Executable):
    res = echocat.execute(ExecParams(args=["exit", '100']))

    assert res.exit == 100
    assert res.out().is_empty()
    assert res.err().is_empty()


def test_echo_single_word(echocat: Executable):
    res = echocat.execute(ExecParams(args=["exit", '0']))

    assert res.exit == 0
    assert res.out().is_empty()
    assert res.err().is_empty()
