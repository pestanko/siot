from siot import Workspace, Executable


def test_hello_world(hello: Executable):
    res = hello.execute()
    assert res.exit == 0
    assert res.out().text() == 'Hello World\n'
    assert res.err().is_empty()
