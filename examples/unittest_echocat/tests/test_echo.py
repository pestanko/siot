from siot import ExecParams
import shared


class TestEchoScenario(shared.SharedTestCase):
    def test_echo_hello_world(self):
        res = self.echocat.execute(ExecParams(args=["echo", "Hello", "world"]))

        self.assertEqual(res.exit, 0)
        self.assertEqual(res.out().text(), 'Hello world\n')
        self.assertTrue(res.err().is_empty())

    def test_echo_single_word(self):
        res = self.echocat.execute(ExecParams(args=["echo", "Hello"]))

        self.assertEqual(res.exit, 0)
        self.assertEqual(res.out().text(), 'Hello\n')
        self.assertTrue(res.err().is_empty())
