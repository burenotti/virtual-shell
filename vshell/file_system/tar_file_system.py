import re
import tarfile
import typing
import abc
from dataclasses import dataclass

from .errors import FileNotFound, FileTypeError

__all__ = ['TarFileSystem']


class TarFileSystem:

    def __init__(self, archive: tarfile.TarFile) -> None:
        self._archive = archive
        path: tarfile.TarInfo
        self._files = {trim_path(info.path): info for info in archive.getmembers()}
        self._files['/'] = tarfile.TarInfo('/')

    def _get(self, path: str) -> tarfile.TarInfo | None:
        path = trim_path(path)
        return self._files.get(path)

    def exists(self, path: str) -> bool:
        return self._get(path) is not None

    def is_dir(self, path: str) -> bool:
        info = self._get(path)
        if info is None:
            raise FileNotFound(f"File {path} does not exist", path)

        return info.isdir()

    def is_file(self, path: str) -> bool:
        info = self._get(path)
        if info is None:
            raise FileNotFound(f"File {path} does not exist", path)

        return info.isfile()

    def open(self, path: str) -> typing.IO[bytes] | None:
        if not self.is_file(path):
            raise FileTypeError("Only files can be opened, not directories", path)

        info = self._get(path)
        return self._archive.extractfile(info)

    def list_dir(self, path: str) -> list[str]:
        if not self.is_dir(path):
            raise FileTypeError("Only dir can be listed", path)

        self._get(path)


def trim_path(path: str) -> str:
    return f"/{path.strip('/')}"
