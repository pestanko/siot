import unittest
import tempfile
from pathlib import Path

import siot
from siot import Executable, Workspace


class SharedTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        siot.load_logger()
        cls.root_dir = Path(__file__).parent.parent
        cls.data_path = Path(__file__).parent / 'data'
        cls.tmp_path_factory = Path(tempfile.mkdtemp(prefix="echocat_"))

    def setUp(self) -> None:
        self.ws_path = self.tmp_path_factory / self.__class__.__name__
        if not self.ws_path.exists():
            self.ws_path.mkdir()

        self.workspace = Workspace(self.ws_path)
        self.echocat: Executable = self.workspace.executable("build/echocat")
