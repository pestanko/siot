#! /usr/bin/env python3
import datetime
import enum
import filecmp
import inspect
import logging
import logging.config
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

PYTHON_REQUIRED = "3.8"
VERSION = '0.0.1-alpha'
__version__ = VERSION
NAME = "siot"

# Logging specific stuff
LOG = logging.getLogger(NAME)

TRACE = 5
logging.addLevelName(TRACE, 'TRACE')


def log_trace(self, msg, *args, **kwargs):
    self.log(TRACE, msg, *args, **kwargs)


logging.Logger.trace = log_trace


# Base classes

class Content:
    """Wrapper over three kinds of content
    In order to simplify comparison and definition of the stdin/out/err

    it can be either:
    - File - File representation of the file
    - Text - text (printable/utf-8) representation of the file/content
    - Binary - binary data

    If all of them are None, the content is empty
    """

    def __init__(self, text: str = None, binary: bytes = None, file: Path = None):
        self._text: str = text
        self._binary: bytes = binary
        self._file = Path(file) if file else None

    @property
    def file(self) -> Optional[Path]:
        """Returns the file location
        :return: None if not set or if the file does not exists
        """
        return self._file if self._file and self._file.exists() else None

    def text(self, encoding='utf-8') -> Optional[str]:
        """Gets a text representation (printable) of the content
        If the content is file - it loads a whole file content \
        If the content is text - it returns the text as it is
        If the content is binary the encoding is applied and
        tries to convert binary data to text
        :param encoding: default is utf-8
        :return:
        """
        if self._text is not None:
            return self._text
        if self._binary is not None:
            return self._binary.decode(encoding)
        if self.file:
            return self.file.read_text(encoding)
        return None

    def binary(self, encoding='utf-8') -> Optional[bytes]:
        """Gets a binary representation of the content
        If the content is file - it loads a whole file content \
        If the content is binary - it returns bytes as they are
        If the content is text the encoding is applied and
        tries to convert string data to bytes
        :param encoding: default is utf-8
        :return:
        """
        if self._binary is not None:
            return self._binary
        if self._text is not None:
            return self._text.encode(encoding)
        if self.file:
            return self.file.read_bytes()
        return None

    def size(self) -> int:
        """Returns a content size
        :return: if the content is empty, the 0 is returned
        """
        if self.file:
            return self.file.stat().st_size
        if self._text:
            return len(self._text)
        if self._binary:
            return len(self._binary)
        return 0

    def assert_content(self, other: 'Content' = None, **kw) -> None:
        """Asserts that contents are the same
        This method works only with PyTest
        :param other: Other Content representation
        :param kw:
        """
        other = other if other else Content(**kw)
        if other.file and self.file:
            assert filecmp.cmp(str(other.file), str(self.file))
        if other._text is not None or self._text is not None:
            assert self.text() == other.text()
        if other._binary is not None or self._binary is not None:
            assert self.binary() == other.binary()

    def is_empty(self) -> bool:
        """Returns whether the content is empty
        Resolution:
        - if all the parameters are empty (text, binary, file)
        - if the size is empty (this method calls self.size)
        :return: true if the content is empty
        """
        return (not self.file and not self._text and not self._binary) or self.size() == 0

    def __eq__(self, other: 'Content') -> bool:
        if other.file is not None and self.file is not None:
            return filecmp.cmp(other.file, self.file)
        return self.binary() == other.binary()

    def __str__(self):
        if self.is_empty():
            return "Content::EMPTY"
        if self.file:
            return f'Content::FILE("{self.file}")'
        if self._text:
            return f'Content::TEXT("{self._text}")'
        if self._binary:
            return f'Content::BIN("{self._binary}")'
        return "Content::EMPTY"

    def __repr__(self) -> str:
        return str(self)


class ExecParams:
    def __init__(self, args: List[str] = None, stdin: 'Content' = None, env: Dict[str, str] = None, **kwargs):
        """Creates an instance of the Exec parameters
        :param args: List of executable arguments
        :param stdin: Standard input content representation
        :param env: Dictionary of env variables
        :param kwargs: Other optional arguments
        """
        self.args = [str(arg) for arg in args] if args else []
        self.env: Dict[str, str] = {k: str(v) for k, v in env.items()} if env else {}
        self.stdin: Optional[Content] = stdin if stdin else self.resolve_content(kwargs)
        self.other = kwargs if kwargs else {}

    @classmethod
    def resolve_content(cls, kwargs) -> Optional[Content]:
        def _resolve(name: str):
            return Content(**{name: kwargs[name]}) if name in kwargs else None

        for prop in ('text', 'binary', 'file'):
            val = _resolve(prop)
            if val is not None:
                del kwargs[prop]
                return val
        return None


class Workspace:
    def __init__(self, workspace: Path = None):
        """Creates an instance of the workspace
        workspace defines where the executable output will be stored
        :param workspace: Location where the executable (stdout, stderr) will be stored
        """
        self.ws_path = workspace
        self.execs: List['Executable'] = []

    def executable(self, path: Union[Path, str]) -> 'Executable':
        """Register a new executable
        :param path: Location of the executable
        :return:
        """
        exe = Executable(path, workspace=self)
        self.execs.append(exe)
        return exe

    def execute(self, exec_path: Path, params: 'ExecParams' = None, **kw) -> 'CommandResult':
        """Execute the command/executable and store its outputs to the workspace
        :param exec_path: Location of the executable
        :param params: Additional parameters (args, env, stdin)
        :param kw: optional arguments that will be passed to the params
        :return: Execution result
        """
        params = params if params else ExecParams(**kw)
        LOG.info("[EXEC] Executing \"%s\" with workspace path \"%s\"", exec_path, self.ws_path)
        params = params if params is not None else ExecParams()
        res = execute_cmd(
            str(exec_path),
            args=params.args,
            stdin=params.stdin,
            ws=self.ws_path,
            **params.other,
        )
        return res


class Executable:
    def __init__(self, executable: Path, workspace: 'Workspace' = None):
        self.exe: Path = Path(executable)
        self.workspace: Workspace = workspace

    def execute(self, params: 'ExecParams' = None, args: List[str] = None,
                stdin: Content = None, **kwargs) -> 'CommandResult':
        if not self.exe.exists():
            raise FileNotFoundError(str(self.exe))
        if params is None:
            params = ExecParams(args=args, stdin=stdin, **kwargs)
        return self.workspace.execute(self.exe, params)


class CommandResult:
    def __init__(self, exit_code: int, stdout: Path, stderr: Path, elapsed: int):
        self.exit: int = exit_code
        self.stdout: Path = stdout
        self.stderr: Path = stderr
        self.elapsed: int = elapsed

    def out(self) -> Content:
        return Content(file=self.stdout)

    def err(self) -> Content:
        return Content(file=self.stderr)

    def __str__(self) -> str:
        return str({
            'exit': self.exit,
            'stdout': str(self.stdout),
            'stderr': str(self.stderr),
            'elapsed': self.elapsed,
        })

    def __repr__(self) -> str:
        return str(self)


def build_using_cmake(path: Path):
    ws = Workspace(path)
    res = ws.execute('cmake', args=['-Bbuild'])
    if res.exit != 0:
        LOG.error("Unable to build using cmake")
        raise RuntimeError("Command failed: cmake")
    res = ws.execute('make', args=['-Cbuild'])
    if res.exit != 0:
        LOG.error("Unable to build using make")
        raise RuntimeError("Command failed: make")


# Utils


def execute_cmd(cmd: str, args: List[str], ws: Path, stdin: Content = None,
                stdout: Path = None, stderr: Path = None, nm: str = None,
                log: logging.Logger = None, timeout: int = 60, cmd_prefix: List[str] = None,
                env: Dict[str, Any] = None, cwd: Union[str, Path] = None,
                **kwargs) -> 'CommandResult':
    # pylint: disable=R0914,R0913
    log = log or LOG
    log.info("[CMD] Exec: '%s' with args %s", cmd, str(args))
    log.debug(" -> [CMD] Exec STDIN: '%s'", stdin if stdin else "EMPTY")
    log.trace(" -> [CMD] Exec with timeout %d, cwd: '%s'", timeout, cwd)
    if not nm:
        nm = cmd.split('/')[-1] + "_" + datetime.datetime.now().isoformat("_").replace(':', '-')
    stdout = stdout or ws / f'{nm}.stdout'
    stderr = stderr or ws / f'{nm}.stderr'

    full_env = {**os.environ, **(env or {})}

    with stdout.open('w') as fd_out, stderr.open('w') as fd_err:
        fd_in = Path(stdin.file).open('r') if stdin and stdin.file else None
        _input = stdin.binary() if fd_in is None and stdin else None
        start_time = time.perf_counter_ns()
        try:
            cmd_prefix = cmd_prefix if cmd_prefix else []
            exec_result = subprocess.run(
                [*cmd_prefix, cmd, *args],
                stdout=fd_out,
                stderr=fd_err,
                stdin=fd_in,
                input=_input,
                timeout=timeout,
                env=full_env,
                check=False,
                cwd=str(cwd) if cwd else None,
                **kwargs
            )
        except Exception as ex:
            log.error("[CMD] Execution '%s' failed: %s", cmd, ex)
            raise ex
        finally:
            end_time = time.perf_counter_ns()
            if fd_in:
                fd_in.close()

    log.debug("[CMD] Result[exit=%d]: %s", exec_result.returncode, str(exec_result))
    log.trace(" -> Command stdout '%s'", stdout)
    log.trace("STDOUT: %s", stdout.read_bytes())
    log.trace(" -> Command stderr '%s'", stderr)
    log.trace("STDERR: %s", stderr.read_bytes())

    return CommandResult(
        exit_code=exec_result.returncode,
        elapsed=end_time - start_time,
        stdout=stdout,
        stderr=stderr,
    )


def obj_get_props_dict(obj: object) -> Dict[str, Any]:
    cls = obj.__class__
    props = inspect.getmembers(cls, lambda o: isinstance(o, property))
    res = {}
    for name, prop in props:
        res[name] = prop.fget(obj)
    return res


def dict_serialize(obj, as_dict_skip: bool = False) -> Any:
    if obj is None or isinstance(obj, (str, int)):
        return obj
    if isinstance(obj, list):
        return [dict_serialize(i) for i in obj]

    if isinstance(obj, set):
        return {dict_serialize(i) for i in obj}

    if isinstance(obj, dict):
        return {k: dict_serialize(v) for k, v in obj.items()}

    if isinstance(obj, enum.Enum):
        return obj.value

    if hasattr(obj, '__dict__'):
        return {k: dict_serialize(v) for k, v in obj.__dict__.items()}

    return str(obj)


def load_logger(level: str = None, log_file: Optional[Path] = None, file_level: str = None):
    level = level if level else os.getenv("LOG_LEVEL", "info")
    level = level.upper()
    file_level = file_level.upper() if file_level else level
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
            },
            'single': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'handlers': {
            'console': {
                'level': 'TRACE',
                'class': 'logging.StreamHandler',
                'formatter': 'single'
            },
        },
        'loggers': {
            NAME: {
                'handlers': ['console'],
                'level': level,
            }
        }
    }
    if log_file and log_file.parent.exists():
        log_config['handlers']['file'] = {
            'level': file_level,
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': str(log_file)
        }
        log_config['loggers'][NAME]['handlers'].append('file')
    logging.config.dictConfig(log_config)
