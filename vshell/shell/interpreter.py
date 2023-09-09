import pathlib
import re
import sys
import typing
from contextlib import suppress
from dataclasses import dataclass
from typing import Protocol, TextIO, Callable


class ParseError(Exception):
    pass


class FileSystem(Protocol):
    pass


class ShellError(Exception):
    pass


class ShellContext(Protocol):
    cwd: str
    stdin: TextIO
    stdout: TextIO


CommandFunc = Callable[[list[str], ShellContext], bool]


class ShellInterpreter:

    def __init__(
            self,
            fs: FileSystem,
            stdin: TextIO = sys.stdin,
            stdout: TextIO = sys.stdout,
            stderr: TextIO = sys.stderr,
    ) -> None:
        self.fs = fs
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self._commands: dict[str, CommandFunc] = {}
        self.current_dir = "/"
        self._exited = False

    @property
    def cwd(self) -> str:
        return self.current_dir

    @cwd.setter
    def cwd(self, cwd: str) -> None:
        cwd = self.make_absolute(cwd)
        if not self.fs.exists(cwd):
            raise FileNotFoundError("directory does not exist")

        self.current_dir = cwd

    def process_prompt(self, prompt: str) -> None:
        args = self.parse_prompt(prompt)
        if not args:
            return

        command = self._commands.get(args[0])
        if not command:
            raise ShellError(f"command {args[0]} not found")

        command(args, self)

    def parse_prompt(self, prompt: str) -> list[str]:
        args = re.split(r"\s+", prompt)
        return [arg for arg in args if arg]

    def unpack_template(self, ) -> list[str]:
        pass

    def run(self) -> None:
        while not self._exited:
            try:
                self.stdout.write(f'\n{self.current_dir}$ ')
                sys.stdout.flush()
                line = self.stdin.readline()
                self.process_prompt(line)
            except (EOFError, KeyboardInterrupt):
                self.exit()
            except (ShellError, ParseError) as e:
                sys.stderr.write(f"vshell: {e.args[0]} \n")
                sys.stderr.flush()

    def exit(self) -> None:
        self._exited = True

    def command(self, aliases: list[str]) -> Callable[[CommandFunc], CommandFunc]:
        def decorator(func: CommandFunc) -> CommandFunc:
            for alias in aliases:
                self._commands[alias] = func
            return func

        return decorator

    def open(self, path: str) -> typing.IO[bytes]:
        return self.fs.open(self.make_absolute(path))

    def make_absolute(self, path: str) -> str:
        if path.startswith('/'):
            return path
        return str(pathlib.PurePosixPath(self.current_dir) / path)
