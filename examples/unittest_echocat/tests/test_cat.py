import shared
from siot import Content


class TestEchoScenario(shared.SharedTestCase):
    def test_echo_hello_world(self):
        res = self.echocat.execute(args=["cat"], text="Hello world!")

        self.assertEqual(res.exit, 0)
        self.assertEqual(res.out().text(), 'Hello world!')
        self.assertTrue(res.err().is_empty())

    def test_echo_hello_world_file(self):
        hello_file = self.data_path / 'hello_world.in'
        res = self.echocat.execute(args=["cat"], file=hello_file)

        self.assertEqual(res.exit, 0)
        self.assertEqual(res.out().text(), 'Hello world!\n')
        self.assertEqual(res.out(), Content(file=hello_file))
        res.out().assert_content(Content(file=hello_file))
        self.assertTrue(res.err().is_empty())
