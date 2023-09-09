import argparse
import sys
import tarfile
from typing import Sequence
from vshell.file_system import TarFileSystem
from vshell.shell.interpreter import ShellInterpreter, ShellContext


def run(args: Sequence[str]) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", help="path to archive (tar or zip)")
    namespace = parser.parse_args(args)
    path: str = namespace.file_path

    if tarfile.is_tarfile(path):
        archive = tarfile.open(path, 'r')
        fs = TarFileSystem(archive)
    else:
        raise Exception("Provided file is not a tar archive")

    shell = ShellInterpreter(fs, sys.stdin, sys.stdout, sys.stderr)

    @shell.command(['pwd'])
    def pwd(args: list[str], ctx: ShellContext) -> bool:
        ctx.stdout.write(ctx.cwd)
        return True

    @shell.command(['cd'])
    def cd(args: list[str], ctx: ShellContext) -> bool:
        if len(args) == 1:
            sys.stderr.write("provide dir\n")
            return False
        if len(args) > 2:
            sys.stderr.write("too many arguments\n")
            return False
        try:
            ctx.cwd = args[1]
            return True
        except Exception as e:
            sys.stderr.write(f"{e.args[0]}\n")
            return False

    @shell.command(['ls'])
    def ls(args: list[str], ctx: ShellContext) -> bool:
        if len(args) == 1:
            sys.stderr.write("provide dir\n")
            return False
        if len(args) > 2:
            sys.stderr.write("too many arguments\n")
            return False
        try:
            for res in ctx.fs.find_template(args[1]):
                sys.stdout.write(res)
                sys.stdout.write('\n')
            return True
        except Exception as e:
            sys.stderr.write(f"{e.args[0]}\n")
            return False

    @shell.command(['cat'])
    def cat(args: list[str], ctx: ShellContext) -> bool:
        if len(args) == 1:
            sys.stderr.write("provide file path\n")
            return False
        elif len(args) > 2:
            sys.stderr.write("too many arguments\n")
            return False
        try:
            with ctx.open(args[1]) as file:
                sys.stdout.writelines([line.decode('utf-8') for line in file.readlines()])

            return True
        except Exception as e:
            sys.stderr.write(f"{e.args[0]}\n")
            return False

    shell.run()
