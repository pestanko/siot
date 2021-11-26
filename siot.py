#! /usr/bin/env python3


import enum
import inspect
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union

PYTHON_REQUIRED = "3.7"
VERSION = '0.0.1-alpha'
__version__ = VERSION
NAME = "siot"
LOG = logging.getLogger(NAME)


class AsDict:
    """Helper class for the "nicer" serialization - converting objects to the dictionaries
    """

    def as_dict(self, params: Dict = None) -> Dict:
        data = obj_get_props_dict(self)
        if params:
            data.update(params)
        return data

    def d_serialize(self) -> Dict:
        return dict_serialize(self.as_dict())

    def __str__(self) -> str:
        return str(self.d_serialize())

    def __repr__(self):
        return self.__str__()


class Content:
    def __init__(self, text: str = None, binary: bytes = None, file: Path = None):
        self._text: str = text
        self._binary: bytes = binary
        self.file = Path(file) if file else None

    def text(self, encoding='utf-8') -> Optional[str]:
        if self._text is not None:
            return self._text
        if self._binary is not None:
            return self._binary.decode(encoding)
        if self.file and self.file.exists():
            return self.file.read_text(encoding)
        return None

    def binary(self, encoding='utf-8') -> Optional[bytes]:
        if self._binary is not None:
            return self._binary
        if self._text is not None:
            return self._text.encode(encoding)
        if self.file and self.file.exists():
            return self.file.read_bytes()
        return None

    def is_empty(self) -> bool:
        return (not self.file and not self._text and not self._binary) or not self.binary()

    def is_blank(self) -> bool:
        return self.is_empty() or not self.text().strip()


class ExecParams:
    def __init__(self, args: List[str] = None, stdin: 'Content' = None, env: Dict[str, str] = None, **kwargs):
        self.args = args if args else []
        self.stdin: Optional[Content] = stdin
        self.env: Dict[str, str] = {k: str(v) for k, v in env.items()} if env else {}
        self.other = kwargs if kwargs else {}


class Workspace:
    def __init__(self, workspace: Path = None):
        self.ws_path = workspace
        self.execs: List['Executable'] = []

    def executable(self, path: Union[Path, str]) -> 'Executable':
        exe = Executable(path, workspace=self)
        self.execs.append(exe)
        return exe

    def execute(self, exec_path: Path, params: 'ExecParams' = None) -> 'CommandResult':
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

    def execute(self, params: 'ExecParams' = None) -> 'CommandResult':
        if not self.exe.exists():
            raise FileNotFoundError(str(self.exe))
        return self.workspace.execute(self.exe, params)


class CommandResult(AsDict):
    def __init__(self, exit_code: int, stdout: Path, stderr: Path, elapsed: int):
        self.exit: int = exit_code
        self.stdout: Path = stdout
        self.stderr: Path = stderr
        self.elapsed: int = elapsed

    def out(self) -> Content:
        return Content(file=self.stdout)

    def err(self) -> Content:
        return Content(file=self.stderr)

    def as_dict(self, params: Dict = None) -> Dict:
        return {
            'exit': self.exit,
            'stdout': str(self.stdout),
            'stderr': str(self.stderr),
            'elapsed': self.elapsed,
        }


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
    nm = nm or cmd
    stdout = stdout or ws / f'{nm}.stdout'
    stderr = stderr or ws / f'{nm}.stderr'

    full_env = {**os.environ, **(env or {})}

    with stdout.open('w') as fd_out, stderr.open('w') as fd_err:
        fd_in = Path(stdin).open('r') if stdin and stdin.file else None
        _input = stdin.binary() if stdin else None
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

    if not as_dict_skip and isinstance(obj, AsDict):
        return obj.as_dict()

    if hasattr(obj, '__dict__'):
        return {k: dict_serialize(v) for k, v in obj.__dict__.items()}

    return str(obj)
